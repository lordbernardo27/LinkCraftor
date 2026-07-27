from __future__ import annotations
import os
from backend.server.stores.uploaded_document_unified_content import build_and_write_uduc_from_extraction_result
from backend.server.stores.universal_unified_content_document_convergence import build_and_write_uucd_from_uduc_v1
from backend.server.stores.enterprise_raw_html_acquisition_engine import acquire_raw_html_for_workspace_v1
from typing import Any, Dict
from backend.server.jobs.universal_knowledge_orchestrator import create_universal_knowledge_job, record_job_failure, update_job_progress, update_job_status

def _execute_universal_knowledge_job_without_udare_v1(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Local worker execution contract.

    This is the first local worker foundation. In production, this same job
    contract can be executed by Celery/RQ/SQS/Lambda/App Runner workers.
    """
    workspace_id = job.get('workspace_id') or 'default'
    job_id = job.get('job_id') or ''
    job_type = job.get('job_type') or ''
    payload = job.get('payload') or {}
    try:
        update_job_status(workspace_id=workspace_id, job_id=job_id, status='running', message=f'Running {job_type}.')
        update_job_progress(workspace_id=workspace_id, job_id=job_id, percent=10, message='Worker accepted job.', step='worker_accepted')
        stage_groups = {'upload_arm': {'upload_document_batch', 'upload_file_route_validation', 'format_detection', 'format_router', 'upload_document_extraction', 'build_uduc', 'build_uucd_from_uduc'}, 'website_arm': {'website_connection_batch', 'website_crawl_batch', 'site_page_discovery', 'raw_html_acquisition', 'html_cleaning', 'article_extraction', 'content_normalization', 'build_website_unified_content', 'build_uucd_from_website'}, 'canonical': {'build_uucd', 'source_authorization', 'source_lifecycle', 'source_asset_versioning', 'build_body_store', 'verify_body_store', 'certify_uucd_body_store'}, 'semantic': {'semantic_article_reader', 'semantic_context_builder', 'entity_concept_extraction', 'phrase_neighborhood_intelligence', 'topic_intent_intelligence', 'section_evidence_builder', 'semantic_relationship_graph', 'semantic_learning_export', 'semantic_end_to_end_certification'}}
        group = ''
        for group_name, job_types in stage_groups.items():
            if job_type in job_types:
                group = group_name
                break
        if not group:
            raise ValueError(f'Unsupported worker job_type: {job_type}')
        if group == 'semantic' and payload.get('semantic_ready') is not True:
            raise ValueError('Semantic job blocked because semantic_ready is not true.')
        result = {'handled': True, 'job_type': job_type, 'stage_group': group, 'workspace_id': workspace_id, 'stage_index': payload.get('stage_index'), 'stage_count': payload.get('stage_count'), 'note': 'Stage accepted by full pipeline worker contract.'}
        if job_type == 'upload_document_batch':
            result['document_count'] = len(payload.get('documents') or [])
            result['uduc_write_results'] = _write_uduc_for_upload_batch_job(job)
        if job_type in {'website_connection_batch', 'website_crawl_batch', 'raw_html_acquisition'}:
            result['website_acquisition'] = _run_website_raw_html_acquisition_job(job)
        if job_type == 'build_website_unified_content':
            result['website_unified_content'] = run_website_unified_content_batch_v1(workspace_id=workspace_id, assigned_html_ids=payload.get('assigned_html_ids') or [], batch_id=payload.get('batch_id') or job.get('batch_id') or '', batch_index=payload.get('batch_index'), batch_count=payload.get('batch_count'))
        update_job_progress(workspace_id=workspace_id, job_id=job_id, percent=100, message='Job completed.', step='job_completed')
        update_job_status(workspace_id=workspace_id, job_id=job_id, status='completed', message='Job completed.', result=result)
        return {'ok': True, 'job_id': job_id, 'workspace_id': workspace_id, 'job_type': job_type, 'result': result}
    except Exception as e:
        failure = record_job_failure(workspace_id=workspace_id, job_id=job_id, job_type=job_type, error=str(e), payload=payload)
        return {'ok': False, 'job_id': job_id, 'workspace_id': workspace_id, 'job_type': job_type, 'failure': failure}

def execute_universal_knowledge_job_v1(job: Dict[str, Any]) -> Dict[str, Any]:
    from backend.server.runtime.universal_runtime_registration import ensure_persisted_runtime_registrations_loaded, execute_registered_runtime_job_v1, has_runtime_handler
    ensure_persisted_runtime_registrations_loaded()
    registered_job_type = str(job.get('job_type') or job.get('stage') or '').strip()
    if has_runtime_handler(registered_job_type):
        return execute_registered_runtime_job_v1(job)
    _udare_job = job
    if isinstance(_udare_job, dict) and str(_udare_job.get('job_type') or _udare_job.get('stage') or '').strip() == 'udare_reconstruction':
        from backend.server.workers.udare_reconstruction_worker import run_udare_reconstruction_job_v1
        return run_udare_reconstruction_job_v1(job=_udare_job)
    return _execute_universal_knowledge_job_without_udare_v1(job)

def create_and_execute_local_job_v1(*, workspace_id: str, job_type: str, payload: Dict[str, Any] | None=None) -> Dict[str, Any]:
    job = create_universal_knowledge_job(workspace_id=workspace_id, job_type=job_type, payload=payload or {})
    return execute_universal_knowledge_job_v1(job)

def _write_uduc_for_upload_batch_job(job):
    from pathlib import Path
    import zipfile
    import xml.etree.ElementTree as ET
    payload = job.get('payload') or {}
    workspace_id = job.get('workspace_id') or payload.get('workspace_id') or 'default'
    docs = payload.get('documents') or []
    if not docs and payload.get('document_id'):
        docs = [payload]
    results = []
    for doc in docs:
        document_id = doc.get('document_id') or doc.get('doc_id')
        filename = doc.get('filename') or doc.get('original_name') or doc.get('stored_name') or document_id
        stored_path = doc.get('stored_path')
        if not document_id:
            results.append({'ok': False, 'reason': 'missing_document_id'})
            continue
        if not stored_path:
            docs_dir = Path('backend/server/data/docs') / workspace_id
            matches = list(docs_dir.glob(f'{document_id}__*'))
            if matches:
                stored_path = str(matches[0])
        if not stored_path or not Path(stored_path).exists():
            results.append({'ok': False, 'document_id': document_id, 'reason': 'missing_stored_path'})
            continue
        fp = Path(stored_path)
        raw_text = ''
        try:
            raw_text = fp.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            raw_text = ''
        if not raw_text.strip() and fp.suffix.lower() == '.docx':
            try:
                with zipfile.ZipFile(fp) as z:
                    xml = z.read('word/document.xml')
                root = ET.fromstring(xml)
                ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                raw_text = ' '.join((t.text for t in root.findall('.//w:t', ns) if t.text)).strip()
            except Exception:
                raw_text = ''
        if not raw_text.strip():
            results.append({'ok': False, 'document_id': document_id, 'reason': 'empty_extracted_text'})
            continue
        extraction_result = {'workspace_id': workspace_id, 'document_id': document_id, 'title': Path(str(filename)).stem, 'original_name': filename, 'filename': filename, 'content_body': raw_text, 'text': raw_text, 'headings': [], 'metadata': {'source_type': 'uploaded_document', 'stored_path': stored_path, 'source_pipeline': 'live_upload_orchestration'}}
        written = build_and_write_uduc_from_extraction_result(workspace_id=workspace_id, document_id=document_id, extraction_result=extraction_result)
        uduc_payload = written.get('uduc') or written.get('document') or extraction_result
        uucd_written = build_and_write_uucd_from_uduc_v1(uduc_payload)
        results.append({'ok': True, 'document_id': document_id, 'filename': filename, 'uduc_path': written.get('path') or written.get('output_path'), 'uucd_path': uucd_written.get('uucd_path'), 'uucd_written': bool(uucd_written.get('ok'))})
    return results

def _run_website_raw_html_acquisition_job(job):
    payload = job.get('payload') or {}
    workspace_id = job.get('workspace_id') or payload.get('workspace_id') or 'default'
    batch_size = int(payload.get('batch_size') or 100)
    checkpoint_every = int(payload.get('checkpoint_every') or 25)
    sleep_seconds = float(payload.get('sleep_seconds') or 0.15)
    assigned_urls = payload.get('assigned_urls') or []
    if assigned_urls:
        from pathlib import Path
        import json
        site_pages_path = Path('backend/server/data') / f'site_pages_{workspace_id}.json'
        site_pages_path.parent.mkdir(parents=True, exist_ok=True)
        temp_workspace_id = f"{workspace_id}__assigned_{job.get('job_id')}"
        temp_site_pages_path = Path('backend/server/data') / f'site_pages_{temp_workspace_id}.json'
        temp_site_pages_path.write_text(json.dumps({'workspace_id': temp_workspace_id, 'source_workspace_id': workspace_id, 'pages': [{'url': url} for url in assigned_urls]}, indent=2, ensure_ascii=False), encoding='utf-8')
        result = acquire_raw_html_for_workspace_v1(workspace_id=temp_workspace_id, resume=True, force=False, batch_size=batch_size, checkpoint_every=checkpoint_every, sleep_seconds=sleep_seconds)
        real_path = Path('backend/server/data/raw_website_html') / f'raw_website_html_{workspace_id}.json'
        temp_path = Path('backend/server/data/raw_website_html') / f'raw_website_html_{temp_workspace_id}.json'
        real_path.parent.mkdir(parents=True, exist_ok=True)
        if real_path.exists():
            real_store = json.loads(real_path.read_text(encoding='utf-8'))
        else:
            real_store = {'version': 'raw_website_html_store_v1', 'workspace_id': workspace_id, 'pages': {}}
        temp_store = json.loads(temp_path.read_text(encoding='utf-8')) if temp_path.exists() else {'pages': {}}
        real_store.setdefault('pages', {})
        for html_id, record in (temp_store.get('pages') or {}).items():
            record['workspace_id'] = workspace_id
            real_store['pages'][html_id] = record
        merge_temp_path = real_path.with_name(real_path.name + f'.merge_{os.getpid()}.tmp')
        with merge_temp_path.open('w', encoding='utf-8', newline='\\n') as merge_handle:
            json.dump(real_store, merge_handle, indent=2, ensure_ascii=False)
            merge_handle.flush()
            os.fsync(merge_handle.fileno())
        os.replace(merge_temp_path, real_path)
        raw_html_count = len(real_store.get('pages') or {})
        return {'ok': True, 'stage': 'raw_html_acquisition', 'mode': 'assigned_urls', 'assigned_count': len(assigned_urls), 'processing': result.get('processing'), 'stores': {'raw_html_store_count': raw_html_count, 'raw_html_store_path': str(real_path)}, 'certification': {**(result.get('certification') or {}), 'raw_html_store_count': raw_html_count, 'worker_batch_complete': True}, 'report_path': result.get('report_path'), 'raw_html_complete': False, 'next_job_created': False, 'next_job_id': None}
    result = acquire_raw_html_for_workspace_v1(workspace_id=workspace_id, resume=True, force=False, batch_size=batch_size, checkpoint_every=checkpoint_every, sleep_seconds=sleep_seconds)
    certification = result.get('certification') or {}
    raw_html_complete = bool(certification.get('raw_html_complete_for_site_pages'))
    return {'ok': True, 'stage': 'raw_html_acquisition', 'mode': 'resume_batch', 'processing': result.get('processing'), 'stores': result.get('stores'), 'certification': certification, 'report_path': result.get('report_path'), 'raw_html_complete': raw_html_complete, 'next_job_created': False, 'next_job_id': None}
