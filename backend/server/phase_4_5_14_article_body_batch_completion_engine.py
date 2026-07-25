from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
ROOT = Path(__file__).resolve().parents[2]
ARTICLE_BODY_DIR = ROOT / 'backend' / 'server' / 'data' / 'universal_article_body_store'
ARTICLE_BODY_INDEX = ARTICLE_BODY_DIR / 'universal_article_body_index.json'
ARTICLE_BODY_LEDGER = ARTICLE_BODY_DIR / 'universal_article_body_ledger.json'

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding='utf-8'))

def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')

def _safe_id(value: str) -> str:
    cleaned = ''.join((ch if ch.isalnum() or ch in ('-', '_') else '_' for ch in value))
    return cleaned.strip('_')[:160] or 'article_body'

def _extract_validated_body(record: Dict[str, Any]) -> Optional[str]:
    """
    IMPORTANT ARCHITECTURAL RULE:
    This engine must never parse HTML, extract content, clean content, or validate content.

    It only reads already-cleaned and validated article body text produced by the
    official website ingestion pipeline / Website Unified Content Store.
    """
    candidates = [record.get('article_body'), record.get('primary_content'), record.get('cleaned_article_body'), record.get('validated_article_body')]
    for value in candidates:
        if isinstance(value, str) and value.strip():
            return value.strip()
    content = record.get('content')
    if isinstance(content, dict):
        for key in ('article_body', 'primary_content', 'cleaned_article_body', 'validated_article_body'):
            value = content.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None

def _is_validated(record: Dict[str, Any]) -> bool:
    validation = record.get('validation') or record.get('article_validation') or {}
    if isinstance(validation, dict):
        status = str(validation.get('status', '')).lower()
        is_valid = validation.get('is_valid')
        passed = validation.get('passed')
        if is_valid is True or passed is True:
            return True
        if status in {'valid', 'passed', 'approved', 'success'}:
            return True
    status = str(record.get('status', '')).lower()
    if status in {'valid', 'validated', 'approved', 'success'}:
        return True
    return bool(_extract_validated_body(record))

def _iter_website_ucd_records() -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    if not WEBSITE_UCD_DIR.exists():
        return records
    for path in WEBSITE_UCD_DIR.rglob('*.json'):
        payload = _read_json(path)
        if isinstance(payload, dict):
            if isinstance(payload.get('records'), list):
                records.extend((x for x in payload['records'] if isinstance(x, dict)))
            elif isinstance(payload.get('documents'), list):
                records.extend((x for x in payload['documents'] if isinstance(x, dict)))
            elif isinstance(payload.get('items'), list):
                records.extend((x for x in payload['items'] if isinstance(x, dict)))
            else:
                records.append(payload)
        elif isinstance(payload, list):
            records.extend((x for x in payload if isinstance(x, dict)))
    return records

def complete_article_body_store_from_validated_website_content_v1() -> Dict[str, Any]:
    ARTICLE_BODY_DIR.mkdir(parents=True, exist_ok=True)
    index: Dict[str, Any] = _read_json(ARTICLE_BODY_INDEX) or {'version': '1.0', 'store': 'universal_article_body_store', 'items': {}}
    ledger: Dict[str, Any] = _read_json(ARTICLE_BODY_LEDGER) or {'version': '1.0', 'events': []}
    records = _iter_website_ucd_records()
    completed = 0
    skipped = 0
    failed = 0
    for record in records:
        try:
            source_url = record.get('source_url') or record.get('url') or record.get('canonical_url') or record.get('page_url') or ''
            doc_id = record.get('document_id') or record.get('ucd_id') or record.get('source_id') or record.get('id') or source_url
            if not doc_id:
                skipped += 1
                ledger['events'].append({'event': 'skipped', 'reason': 'missing_document_id', 'timestamp': _utc_now()})
                continue
            if not _is_validated(record):
                skipped += 1
                ledger['events'].append({'event': 'skipped', 'document_id': doc_id, 'source_url': source_url, 'reason': 'not_validated_by_website_pipeline', 'timestamp': _utc_now()})
                continue
            body = _extract_validated_body(record)
            if not body:
                skipped += 1
                ledger['events'].append({'event': 'skipped', 'document_id': doc_id, 'source_url': source_url, 'reason': 'missing_validated_article_body', 'timestamp': _utc_now()})
                continue
            body_id = _safe_id(str(doc_id))
            body_path = ARTICLE_BODY_DIR / f'{body_id}.txt'
            body_path.write_text(body, encoding='utf-8')
            index['items'][body_id] = {'document_id': doc_id, 'source_url': source_url, 'body_path': str(body_path.as_posix()), 'character_count': len(body), 'word_count': len(body.split()), 'hydration_method': 'validated_pipeline_copy_only', 'updated_at': _utc_now()}
            ledger['events'].append({'event': 'completed', 'document_id': doc_id, 'body_id': body_id, 'source_url': source_url, 'character_count': len(body), 'word_count': len(body.split()), 'timestamp': _utc_now()})
            completed += 1
        except Exception as exc:
            failed += 1
            ledger['events'].append({'event': 'failed', 'reason': str(exc), 'timestamp': _utc_now()})
    index['updated_at'] = _utc_now()
    index['record_count'] = len(index.get('items', {}))
    _write_json(ARTICLE_BODY_INDEX, index)
    _write_json(ARTICLE_BODY_LEDGER, ledger)
    return {'status': 'completed', 'records_seen': len(records), 'completed': completed, 'skipped': skipped, 'failed': failed, 'article_body_index': str(ARTICLE_BODY_INDEX), 'article_body_ledger': str(ARTICLE_BODY_LEDGER), 'architectural_rule': 'No HTML parsing, extraction, cleaning, or validation occurs in this engine.'}
if __name__ == '__main__':
    result = complete_article_body_store_from_validated_website_content_v1()
    print(json.dumps(result, indent=2, ensure_ascii=False))
