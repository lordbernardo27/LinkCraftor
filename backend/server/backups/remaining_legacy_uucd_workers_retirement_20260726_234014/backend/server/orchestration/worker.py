# backend/server/orchestration/worker.py
from __future__ import annotations

from typing import Any, Dict, List, Optional
from time import perf_counter
from uuid import uuid4

from .models import JOB_STATUS_RUNNING
from .queue import dequeue_job, queue_snapshot
from .service import (
    mark_job_completed,
    mark_job_failed,
    mark_job_running,
    update_orchestration_progress,
)


def run_test_job(job_id: str, worker_id: str) -> Dict[str, Any]:
    update_orchestration_progress(job_id, 25.0, {"step": "test_job_started"})
    update_orchestration_progress(job_id, 60.0, {"step": "test_job_processing"})
    update_orchestration_progress(job_id, 90.0, {"step": "test_job_finishing"})

    completed = mark_job_completed(
        job_id,
        {"step": "test_job_completed", "worker_id": worker_id},
    )

    return {
        "ok": True,
        "job_id": completed.job_id,
        "status": completed.status,
        "progress_percent": completed.progress_percent,
    }


def _run_highlight_pipeline(
    *,
    workspace_id: str,
    doc_id: str,
    article_text: str,
    active_phrase_pool: Dict[str, Any],
) -> Dict[str, Any]:
    """Run highlight selection + density for one document and return a
    normalized summary. Shared by the single-document job and the
    post-batch pass."""
    from backend.server.stores.highlight_selection_engine import select_highlight_candidates
    from backend.server.stores.highlight_density_engine import apply_highlight_density

    selection_result = select_highlight_candidates(
        workspace_id=workspace_id,
        doc_id=doc_id,
        article_text=article_text,
        active_phrase_pool=active_phrase_pool,
    )

    selected_candidates = []
    if isinstance(selection_result, dict):
        selected_candidates = selection_result.get("selected") or []

    density_result = apply_highlight_density(
        article_text=article_text,
        selected_candidates=selected_candidates,
    )

    final_highlights = (
        density_result.get("final_highlights") or []
        if isinstance(density_result, dict)
        else []
    )

    return {
        "selection_result": selection_result if isinstance(selection_result, dict) else {},
        "density_result": density_result if isinstance(density_result, dict) else {},
        "selection_stats": selection_result.get("stats") if isinstance(selection_result, dict) else None,
        "density_stats": density_result.get("stats") if isinstance(density_result, dict) else None,
        "final_highlight_count": len(final_highlights),
    }


def run_document_upload_job(
    job_id: str,
    worker_id: str,
    payload: Dict[str, Any],
    mark_completed: bool = True,
    defer_active_rebuild: bool = False,
    defer_highlight_pipeline: bool = False,
) -> Dict[str, Any]:
    workspace_id = str(payload.get("workspace_id") or "").strip()
    doc_id = str(payload.get("doc_id") or "").strip()
    stored_path = str(payload.get("stored_path") or "").strip()
    original_name = str(payload.get("original_name") or "").strip()
    html = str(payload.get("html") or "")
    text = str(payload.get("text") or "")

    # FIX: validate BEFORE emitting any progress, so a malformed payload
    # fails immediately instead of after several progress events.
    if not workspace_id:
        raise ValueError("Missing workspace_id for document_upload_job.")
    if not doc_id:
        raise ValueError("Missing doc_id for document_upload_job.")
    if not stored_path:
        raise ValueError("Missing stored_path for document_upload_job.")

    # FIX: cluster_result is initialized up front instead of relying on
    # `'cluster_result' in locals()` (which silently produced None whenever
    # the guarded block didn't run, and NameError-by-accident elsewhere).
    cluster_result: Optional[Dict[str, Any]] = None

    update_orchestration_progress(
        job_id,
        5.0,
        {"step": "upload_worker_started", "worker_id": worker_id},
        current_step="upload_worker_started",
        progress_message="Worker started processing uploaded document.",
        total_steps=10,
        processed_count=0,
    )

    from backend.server.stores.upload_intel_store_v2 import build_upload_intelligence
    from backend.server.stores.upload_phrase_pool_builder import build_upload_phrase_pool
    from backend.server.stores.active_phrase_pool_builder import build_active_phrase_pool
    from backend.server.engine.workspace_topic_cluster_builder import build_workspace_topic_clusters

    from backend.server.stores.upload_document_extractor import extract_upload_document_v1
    from backend.server.stores.uploaded_document_unified_content import build_and_write_uduc_from_extraction_result
    from backend.server.stores.universal_unified_content_document_convergence import build_and_write_uucd_from_uduc_v1
    from backend.server.stores.universal_article_body_store import build_universal_article_body_store_from_uucd_file_v2
    from backend.server.stores.uucd_body_store_certification import certify_uucd_body_store_v1

    update_orchestration_progress(
        job_id,
        10.0,
        {"step": "running_upload_document_extractor"},
        current_step="running_upload_document_extractor",
        progress_message="Running uploaded document extractor.",
        total_steps=10,
        processed_count=1,
    )

    extraction_result = extract_upload_document_v1(stored_path)

    # FIX (content canonicalization): the extractor's normalized text is the
    # canonical body for EVERYTHING downstream in this job — intelligence,
    # phrase pools, and highlights — instead of mixing the mammoth/markdown2
    # preview text (payload["text"]) with the extractor's differently
    # normalized text. Two normalizations of the same document previously
    # flowed through one job, so highlight offsets computed against one
    # could not align with content stored from the other.
    canonical_text = str(getattr(extraction_result, "text", "") or "") or text

    uduc_result = build_and_write_uduc_from_extraction_result(
        extraction_result=extraction_result,
        workspace_id=workspace_id,
        document_id=doc_id,
        original_filename=original_name,
        stored_filename=str(payload.get("stored_name") or ""),
        stored_path=stored_path,
        source_metadata={
            "doc_id": doc_id,
            "filename": original_name,
            "stored_path": stored_path,
            "source_route": str(payload.get("source_route") or ""),
            "document_count": payload.get("document_count"),
        },
    )

    update_orchestration_progress(
        job_id,
        20.0,
        {
            "step": "uploaded_document_unified_content_created",
            "doc_id": doc_id,
            "uduc_path": uduc_result.get("uduc_path"),
        },
        current_step="uploaded_document_unified_content_created",
        progress_message="Uploaded Document Unified Content created.",
        total_steps=10,
        processed_count=2,
    )

    uucd_result = build_and_write_uucd_from_uduc_v1(uduc_result.get("uduc") or {})

    update_orchestration_progress(
        job_id,
        30.0,
        {
            "step": "universal_unified_content_document_created",
            "doc_id": doc_id,
            "uucd_path": uucd_result.get("uucd_path"),
        },
        current_step="universal_unified_content_document_created",
        progress_message="Universal Unified Content Document created.",
        total_steps=10,
        processed_count=3,
    )

    body_store_result = build_universal_article_body_store_from_uucd_file_v2(
        workspace_id=workspace_id,
        uucd_path=uucd_result.get("uucd_path"),
        write_back_uucd=True,
    )

    update_orchestration_progress(
        job_id,
        40.0,
        {
            "step": "universal_article_body_store_created",
            "doc_id": doc_id,
            "body_index_path": body_store_result.get("body_index_path"),
        },
        current_step="universal_article_body_store_created",
        progress_message="Universal Article Body Store updated.",
        total_steps=10,
        processed_count=4,
    )

    body_index_for_current_doc = dict(body_store_result.get("index") or {})
    body_index_for_current_doc["bodies"] = [
        body
        for body in (body_index_for_current_doc.get("bodies") or [])
        if isinstance(body, dict) and str(body.get("document_id") or "") == doc_id
    ]

    certification_result = certify_uucd_body_store_v1(
        workspace_id=workspace_id,
        uucd_payload=body_store_result.get("uucd_payload") or {},
        body_index=body_index_for_current_doc,
        lifecycle_registry={"sources": {}, "events": []},
        asset_version_registry={"assets": []},
        authorization_payload={"unauthorized_documents_quarantined": 0},
    )

    update_orchestration_progress(
        job_id,
        50.0,
        {
            "step": "uucd_body_store_certification_completed",
            "doc_id": doc_id,
            "certification_path": certification_result.get("certification_path"),
            "semantic_ready": (certification_result.get("certification") or {}).get("semantic_ready"),
        },
        current_step="uucd_body_store_certification_completed",
        progress_message="UUCD / Body Store Certification completed.",
        total_steps=10,
        processed_count=5,
    )

    update_orchestration_progress(
        job_id,
        55.0,
        {"step": "building_upload_intelligence", "doc_id": doc_id},
        current_step="building_upload_intelligence",
        progress_message="Building upload intelligence.",
        total_steps=10,
        processed_count=5,
    )

    intel_result = build_upload_intelligence(
        workspace_id=workspace_id,
        doc_id=doc_id,
        stored_path=stored_path,
        original_name=original_name,
        html=html,
        text=canonical_text,
    )

    update_orchestration_progress(
        job_id,
        65.0,
        {"step": "upload_intelligence_completed", "doc_id": doc_id},
        current_step="upload_intelligence_completed",
        progress_message="Upload intelligence completed.",
        total_steps=10,
        processed_count=6,
    )

    upload_pool_result = build_upload_phrase_pool(workspace_id)

    update_orchestration_progress(
        job_id,
        75.0,
        {"step": "upload_phrase_pool_rebuilt", "doc_id": doc_id},
        current_step="upload_phrase_pool_rebuilt",
        progress_message="Upload phrase pool rebuilt.",
        total_steps=10,
        processed_count=7,
    )

    # ------------------------------------------------------------------
    # FIX: the two defer flags are now INDEPENDENT. Previously
    # `if not defer_active_rebuild and not defer_highlight_pipeline:`
    # coupled them — setting only ONE flag disabled BOTH pipelines.
    # ------------------------------------------------------------------
    active_pool_result: Dict[str, Any] = {}
    highlight_summary: Dict[str, Any] = {}

    if not defer_active_rebuild:
        active_pool_result = build_active_phrase_pool(workspace_id)

        # Rebuild topic clusters after active phrase pool changes so
        # cluster intelligence stays aligned with the current phrase set.
        try:
            cluster_result = build_workspace_topic_clusters(workspace_id)
        except Exception as cluster_err:
            cluster_result = {
                "ok": False,
                "error": "topic_cluster_rebuild_failed_after_active_phrase_pool",
                "detail": str(cluster_err)[:300],
            }

        update_orchestration_progress(
            job_id,
            85.0,
            {"step": "active_phrase_pool_rebuilt", "doc_id": doc_id},
            current_step="active_phrase_pool_rebuilt",
            progress_message="Active phrase pool rebuilt.",
            total_steps=10,
            processed_count=8,
        )

    if not defer_highlight_pipeline:
        update_orchestration_progress(
            job_id,
            90.0,
            {"step": "running_highlight_pipeline", "doc_id": doc_id},
            current_step="running_highlight_pipeline",
            progress_message="Running highlight selection and density.",
            total_steps=10,
            processed_count=9,
        )

        highlight_summary = _run_highlight_pipeline(
            workspace_id=workspace_id,
            doc_id=doc_id,
            article_text=canonical_text,
            active_phrase_pool=active_pool_result,
        )

    final_highlight_count = int(highlight_summary.get("final_highlight_count") or 0)

    completion_metadata = {
        "step": "document_upload_job_completed",
        "worker_id": worker_id,
        "workspace_id": workspace_id,
        "doc_id": doc_id,
        "canonical_text_source": "upload_document_extractor" if getattr(extraction_result, "text", "") else "payload_preview",
        "uduc_result": {
            "ok": uduc_result.get("ok") if isinstance(uduc_result, dict) else False,
            "uduc_path": uduc_result.get("uduc_path") if isinstance(uduc_result, dict) else None,
            "document_id": uduc_result.get("document_id") if isinstance(uduc_result, dict) else doc_id,
        },
        "uucd_result": {
            "ok": uucd_result.get("ok") if isinstance(uucd_result, dict) else False,
            "uucd_path": uucd_result.get("uucd_path") if isinstance(uucd_result, dict) else None,
            "document_id": (
                (uucd_result.get("uucd") or {}).get("document_id")
                if isinstance(uucd_result, dict) and isinstance(uucd_result.get("uucd"), dict)
                else doc_id
            ),
        },
        "body_store_result": {
            "ok": body_store_result.get("ok") if isinstance(body_store_result, dict) else False,
            "body_index_path": body_store_result.get("body_index_path") if isinstance(body_store_result, dict) else None,
            "bodies_written": body_store_result.get("bodies_written") if isinstance(body_store_result, dict) else None,
            "missing_bodies": body_store_result.get("missing_bodies") if isinstance(body_store_result, dict) else None,
        },
        "certification_result": {
            "ok": certification_result.get("ok") if isinstance(certification_result, dict) else False,
            "certification_path": certification_result.get("certification_path") if isinstance(certification_result, dict) else None,
            "semantic_ready": (
                (certification_result.get("certification") or {}).get("semantic_ready")
                if isinstance(certification_result, dict)
                else False
            ),
            "certification_level": (
                (certification_result.get("certification") or {}).get("certification_level")
                if isinstance(certification_result, dict)
                else "unknown"
            ),
        },
        "intel_result": intel_result,
        "upload_pool_phrase_count": upload_pool_result.get("phrase_count") if isinstance(upload_pool_result, dict) else None,
        "active_pool_phrase_count": active_pool_result.get("phrase_count") if isinstance(active_pool_result, dict) else None,
        "topic_cluster_rebuild": cluster_result,
        "highlight_selection_stats": highlight_summary.get("selection_stats"),
        "highlight_density_stats": highlight_summary.get("density_stats"),
        "final_highlight_count": final_highlight_count,
        "deferred": {
            "active_rebuild": bool(defer_active_rebuild),
            "highlight_pipeline": bool(defer_highlight_pipeline),
        },
    }

    if mark_completed:
        completed = mark_job_completed(job_id, completion_metadata)
        status = completed.status
        progress = completed.progress_percent
    else:
        update_orchestration_progress(
            job_id,
            99.0,
            {
                **completion_metadata,
                "step": "batch_child_document_completed",
            },
            current_step="batch_child_document_completed",
            progress_message=f"Batch child document completed: {original_name or doc_id}",
        )
        status = "running"
        progress = 99.0

    return {
        "ok": True,
        "job_id": job_id,
        "status": status,
        "progress_percent": progress,
        "workspace_id": workspace_id,
        "doc_id": doc_id,
        # FIX: these were never returned before, so the batch job's
        # highlight totals were permanently zero.
        "final_highlight_count": final_highlight_count,
        "highlight_selection_stats": highlight_summary.get("selection_stats"),
        "highlight_density_stats": highlight_summary.get("density_stats"),
        # Canonical text handed back so the batch job can run the deferred
        # highlight pass without re-extracting the document.
        "canonical_text": canonical_text,
    }


def run_batch_upload_job(job_id: str, worker_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    # FIX: these were referenced at the end of the batch but only imported
    # inside run_document_upload_job's scope — build_workspace_topic_clusters
    # raised NameError, silently swallowed, so the post-batch cluster rebuild
    # NEVER ran.
    from backend.server.stores.active_phrase_pool_builder import build_active_phrase_pool
    from backend.server.engine.workspace_topic_cluster_builder import build_workspace_topic_clusters

    workspace_id = str(payload.get("workspace_id") or "").strip()
    documents = payload.get("documents") or []

    if not workspace_id:
        raise ValueError("Missing workspace_id for batch_upload_job.")

    if not isinstance(documents, list):
        raise ValueError("batch_upload_job payload.documents must be a list.")

    total_documents = len(documents)
    processed_documents = 0
    failed_documents = 0
    skipped_documents = 0
    attempted_documents = 0
    document_results: List[Dict[str, Any]] = []
    successful_docs: List[Dict[str, Any]] = []  # for the deferred highlight pass
    batch_started_at = perf_counter()
    total_final_highlights = 0
    documents_with_highlights = 0
    documents_without_highlights = 0

    update_orchestration_progress(
        job_id,
        0.0,
        {"step": "batch_started", "worker_id": worker_id, "document_count": total_documents},
        current_step="batch_started",
        progress_message=f"Batch processing started for {total_documents} documents.",
        total_steps=max(total_documents, 1),
        total_documents=total_documents,
        processed_documents=0,
        failed_documents=0,
        skipped_documents=0,
    )

    if total_documents == 0:
        completed = mark_job_completed(
            job_id,
            {
                "step": "batch_upload_job_completed_empty",
                "worker_id": worker_id,
                "workspace_id": workspace_id,
                "document_count": 0,
                "document_results": [],
            },
        )

        return {
            "ok": True,
            "job_id": completed.job_id,
            "status": completed.status,
            "job_type": "batch_upload_job",
            "document_count": 0,
            "processed_documents": 0,
            "failed_documents": 0,
            "skipped_documents": 0,
        }

    # Per-document work happens in a 0-90% progress band; the tail (90-100%)
    # is reserved for the once-per-batch pool rebuild + highlight pass.
    per_doc_band = 90.0

    for index, document in enumerate(documents, start=1):
        doc_id = str(document.get("doc_id") or "").strip()
        original_name = str(document.get("original_name") or document.get("filename") or "").strip()
        stored_path = str(document.get("stored_path") or "").strip()
        html = str(document.get("html") or "")
        text = str(document.get("text") or "")

        document_started_at = perf_counter()
        progress_base = ((index - 1) / total_documents) * per_doc_band

        update_orchestration_progress(
            job_id,
            progress_base,
            {
                "step": "batch_document_started",
                "worker_id": worker_id,
                "doc_id": doc_id,
                "document_index": index,
                "document_count": total_documents,
            },
            current_step="batch_document_started",
            progress_message=f"Processing document {index} of {total_documents}: {original_name or doc_id}",
            total_steps=total_documents,
            processed_count=processed_documents,
            failed_count=failed_documents,
            total_documents=total_documents,
            processed_documents=processed_documents,
            failed_documents=failed_documents,
            skipped_documents=skipped_documents,
            current_document_id=doc_id,
            current_document_name=original_name,
        )

        try:
            if not doc_id:
                raise ValueError("Missing doc_id.")
            if not stored_path:
                raise ValueError("Missing stored_path.")

            single_result = run_document_upload_job(
                job_id=job_id,
                worker_id=worker_id,
                mark_completed=False,
                defer_active_rebuild=True,
                defer_highlight_pipeline=True,
                payload={
                    "workspace_id": workspace_id,
                    "doc_id": doc_id,
                    "stored_path": stored_path,
                    "stored_name": str(document.get("stored_name") or ""),
                    "original_name": original_name,
                    "html": html,
                    "text": text,
                    "source_route": "batch_upload_job",
                    "document_count": total_documents,
                },
            )

            if not bool(single_result.get("ok", False)):
                raise RuntimeError(str(single_result.get("error") or "Document processing returned ok=false."))

            processed_documents += 1

            successful_docs.append({
                "doc_id": doc_id,
                "original_name": original_name,
                "canonical_text": str(single_result.get("canonical_text") or text),
                "document_index": index,
            })

            document_results.append({
                "doc_id": doc_id,
                "filename": original_name,
                "status": "completed",
                # Filled in by the post-batch highlight pass below.
                "final_highlight_count": 0,
                "duration_seconds": round(perf_counter() - document_started_at, 4),
                "worker_id": worker_id,
                "document_index": index,
                "execution_mode": "sequential_local",
                "parallel_ready": True,
                "result": {
                    "ok": bool(single_result.get("ok", False)),
                    "job_id": single_result.get("job_id"),
                    "status": single_result.get("status"),
                    "workspace_id": single_result.get("workspace_id"),
                    "doc_id": single_result.get("doc_id"),
                    "progress_percent": single_result.get("progress_percent"),
                },
            })

        except Exception as exc:
            failed_documents += 1

            document_results.append({
                "doc_id": doc_id,
                "filename": original_name,
                "status": "failed",
                "error": str(exc),
                "duration_seconds": round(perf_counter() - document_started_at, 4),
                "worker_id": worker_id,
                "document_index": index,
                "execution_mode": "sequential_local",
                "parallel_ready": True,
            })

        attempted_documents = processed_documents + failed_documents + skipped_documents
        progress_now = (index / total_documents) * per_doc_band

        update_orchestration_progress(
            job_id,
            progress_now,
            {
                "step": "batch_document_finished",
                "worker_id": worker_id,
                "doc_id": doc_id,
                "document_index": index,
                "document_count": total_documents,
            },
            current_step="batch_document_finished",
            progress_message=f"Finished document {index} of {total_documents}.",
            total_steps=total_documents,
            processed_count=processed_documents,
            failed_count=failed_documents,
            total_documents=total_documents,
            processed_documents=processed_documents,
            failed_documents=failed_documents,
            skipped_documents=skipped_documents,
            current_document_id=doc_id,
            current_document_name=original_name,
        )

    update_orchestration_progress(
        job_id,
        92.0,
        {
            "step": "batch_rebuilding_active_phrase_pool",
            "worker_id": worker_id,
            "workspace_id": workspace_id,
            "document_count": total_documents,
        },
        current_step="batch_rebuilding_active_phrase_pool",
        progress_message="Rebuilding active phrase pool once after full batch.",
        total_steps=total_documents,
        processed_count=processed_documents,
        failed_count=failed_documents,
        total_documents=total_documents,
        processed_documents=processed_documents,
        failed_documents=failed_documents,
        skipped_documents=skipped_documents,
    )

    final_active_pool_result = build_active_phrase_pool(workspace_id)

    try:
        final_cluster_result: Dict[str, Any] = build_workspace_topic_clusters(workspace_id)
    except Exception as cluster_err:
        final_cluster_result = {
            "ok": False,
            "error": "topic_cluster_rebuild_failed_after_batch_active_phrase_pool",
            "detail": str(cluster_err)[:300],
        }

    # ------------------------------------------------------------------
    # FIX: deferred highlight pass. Child documents ran with
    # defer_highlight_pipeline=True, but previously NOTHING ever ran the
    # highlight pipeline afterwards — batch uploads simply never got
    # highlights. Now, with the final active pool built, run selection +
    # density once per successful document.
    # ------------------------------------------------------------------
    update_orchestration_progress(
        job_id,
        96.0,
        {
            "step": "batch_running_highlight_pipeline",
            "worker_id": worker_id,
            "document_count": len(successful_docs),
        },
        current_step="batch_running_highlight_pipeline",
        progress_message=f"Running highlight pipeline for {len(successful_docs)} documents.",
        total_steps=total_documents,
        processed_count=processed_documents,
        failed_count=failed_documents,
    )

    results_by_doc = {r["doc_id"]: r for r in document_results if r.get("status") == "completed"}

    for sdoc in successful_docs:
        try:
            summary = _run_highlight_pipeline(
                workspace_id=workspace_id,
                doc_id=sdoc["doc_id"],
                article_text=sdoc["canonical_text"],
                active_phrase_pool=final_active_pool_result if isinstance(final_active_pool_result, dict) else {},
            )
            count = int(summary.get("final_highlight_count") or 0)
        except Exception as hl_err:
            summary = {"error": str(hl_err)[:300]}
            count = 0

        total_final_highlights += count
        if count > 0:
            documents_with_highlights += 1
        else:
            documents_without_highlights += 1

        rec = results_by_doc.get(sdoc["doc_id"])
        if rec is not None:
            rec["final_highlight_count"] = count
            rec["highlight_selection_stats"] = summary.get("selection_stats")
            rec["highlight_density_stats"] = summary.get("density_stats")

    batch_duration_seconds = round(perf_counter() - batch_started_at, 4)

    batch_success_rate = round((processed_documents / total_documents) * 100, 2)
    batch_failure_rate = round((failed_documents / total_documents) * 100, 2)

    batch_summary = {
        "total_documents": total_documents,
        "processed_documents": processed_documents,
        "failed_documents": failed_documents,
        "skipped_documents": skipped_documents,
        "attempted_documents": attempted_documents,
        "successful_documents": processed_documents,
        "success_rate": batch_success_rate,
        "failure_rate": batch_failure_rate,
        "batch_duration_seconds": batch_duration_seconds,
        "total_final_highlights": total_final_highlights,
        "documents_with_highlights": documents_with_highlights,
        "documents_without_highlights": documents_without_highlights,
        "execution_mode": "sequential_local",
        "parallel_ready": True,
        "final_active_pool_phrase_count": (
            final_active_pool_result.get("phrase_count")
            if isinstance(final_active_pool_result, dict)
            else None
        ),
        "final_topic_cluster_rebuild": final_cluster_result,
    }

    completed = mark_job_completed(
        job_id,
        {
            "step": "batch_upload_job_completed",
            "worker_id": worker_id,
            "workspace_id": workspace_id,
            "document_count": total_documents,
            "processed_documents": processed_documents,
            "failed_documents": failed_documents,
            "skipped_documents": skipped_documents,
            "attempted_documents": attempted_documents,
            "successful_documents": processed_documents,
            "batch_duration_seconds": batch_duration_seconds,
            "total_final_highlights": total_final_highlights,
            "documents_with_highlights": documents_with_highlights,
            "documents_without_highlights": documents_without_highlights,
            "batch_summary": batch_summary,
            "document_results": document_results,
            "execution_mode": "sequential_local",
            "parallel_ready": True,
            "final_active_pool_phrase_count": (
                final_active_pool_result.get("phrase_count")
                if isinstance(final_active_pool_result, dict)
                else None
            ),
        },
    )

    return {
        "ok": failed_documents == 0,
        "job_id": completed.job_id,
        "status": completed.status,
        "job_type": "batch_upload_job",
        "document_count": total_documents,
        "processed_documents": processed_documents,
        "failed_documents": failed_documents,
        "skipped_documents": skipped_documents,
        "total_final_highlights": total_final_highlights,
    }


def run_rebuild_upload_phrase_pool_job(job_id: str, worker_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    workspace_id = str(payload.get("workspace_id") or "").strip()
    if not workspace_id:
        raise ValueError("Missing workspace_id for rebuild_upload_phrase_pool_job.")

    from backend.server.stores.upload_phrase_pool_builder import build_upload_phrase_pool

    update_orchestration_progress(
        job_id,
        50.0,
        {"step": "rebuilding_upload_phrase_pool", "worker_id": worker_id},
        current_step="rebuilding_upload_phrase_pool",
        progress_message="Rebuilding upload phrase pool.",
        total_steps=2,
        processed_count=1,
    )

    result = build_upload_phrase_pool(workspace_id)

    # FIX: removed the phantom `cluster_result if 'cluster_result' in locals()`
    # — nothing in this job ever built clusters, so it was always None and
    # implied work that never happened.
    completed = mark_job_completed(
        job_id,
        {
            "step": "rebuild_upload_phrase_pool_completed",
            "worker_id": worker_id,
            "workspace_id": workspace_id,
            "phrase_count": result.get("phrase_count") if isinstance(result, dict) else None,
        },
    )

    return {
        "ok": True,
        "job_id": completed.job_id,
        "status": completed.status,
        "job_type": "rebuild_upload_phrase_pool_job",
        "workspace_id": workspace_id,
    }


def run_rebuild_active_phrase_pool_job(job_id: str, worker_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    workspace_id = str(payload.get("workspace_id") or "").strip()
    if not workspace_id:
        raise ValueError("Missing workspace_id for rebuild_active_phrase_pool_job.")

    from backend.server.stores.active_phrase_pool_builder import build_active_phrase_pool
    from backend.server.engine.workspace_topic_cluster_builder import build_workspace_topic_clusters

    update_orchestration_progress(
        job_id,
        50.0,
        {"step": "rebuilding_active_phrase_pool", "worker_id": worker_id},
        current_step="rebuilding_active_phrase_pool",
        progress_message="Rebuilding active phrase pool.",
        total_steps=2,
        processed_count=1,
    )

    result = build_active_phrase_pool(workspace_id)

    try:
        cluster_result: Dict[str, Any] = build_workspace_topic_clusters(workspace_id)
    except Exception as cluster_err:
        cluster_result = {
            "ok": False,
            "error": "topic_cluster_rebuild_failed_after_standalone_active_phrase_pool",
            "detail": str(cluster_err)[:300],
        }

    completed = mark_job_completed(
        job_id,
        {
            "step": "rebuild_active_phrase_pool_completed",
            "worker_id": worker_id,
            "workspace_id": workspace_id,
            "phrase_count": result.get("phrase_count") if isinstance(result, dict) else None,
            # FIX: the cluster rebuild result was computed here but never
            # recorded in the completion metadata.
            "topic_cluster_rebuild": cluster_result,
        },
    )

    return {
        "ok": True,
        "job_id": completed.job_id,
        "status": completed.status,
        "job_type": "rebuild_active_phrase_pool_job",
        "workspace_id": workspace_id,
    }


def execute_job(job_id: str, job_type: str, worker_id: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if job_type == "test_job":
        return run_test_job(job_id, worker_id)

    if job_type == "document_upload_job":
        return run_document_upload_job(job_id, worker_id, payload or {})

    if job_type == "batch_upload_job":
        return run_batch_upload_job(job_id, worker_id, payload or {})

    if job_type == "rebuild_upload_phrase_pool_job":
        return run_rebuild_upload_phrase_pool_job(job_id, worker_id, payload or {})

    if job_type == "rebuild_active_phrase_pool_job":
        return run_rebuild_active_phrase_pool_job(job_id, worker_id, payload or {})

    raise ValueError(f"No worker handler registered for job_type: {job_type}")


def run_one_job(worker_id: Optional[str] = None) -> Dict[str, Any]:
    actual_worker_id = worker_id or f"worker_{uuid4().hex[:10]}"

    job = dequeue_job(actual_worker_id)

    if job is None:
        return {
            "ok": True,
            "worker_id": actual_worker_id,
            "message": "No queued job available.",
            "queue": queue_snapshot(),
        }

    try:
        # With the corrected queue, dequeue_job has already claimed the job
        # (status RUNNING); mark_job_running is idempotent and simply
        # confirms/records the worker identity.
        running_job = mark_job_running(job.job_id, worker_id=actual_worker_id)

        if running_job.status != JOB_STATUS_RUNNING:
            raise RuntimeError(f"Unable to mark job running: {job.job_id}")

        result = execute_job(
            job_id=job.job_id,
            job_type=job.job_type,
            worker_id=actual_worker_id,
            payload=job.payload,
        )

        return {
            "ok": True,
            "worker_id": actual_worker_id,
            "job": result,
            "queue": queue_snapshot(),
        }

    except Exception as exc:
        failed = mark_job_failed(
            job.job_id,
            error_message=str(exc),
            metadata={
                "worker_id": actual_worker_id,
                "job_type": job.job_type,
            },
        )

        return {
            "ok": False,
            "worker_id": actual_worker_id,
            "job_id": failed.job_id,
            "status": failed.status,
            "error": str(exc),
        }


def worker_health() -> Dict[str, Any]:
    return {
        "ok": True,
        "worker_mode": "local_manual",
        "queue": queue_snapshot(),
    }