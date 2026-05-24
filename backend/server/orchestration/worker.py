from __future__ import annotations

from typing import Any, Dict, Optional
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
    update_orchestration_progress(
        job_id,
        5.0,
        {"step": "upload_received"},
        current_step="upload_received",
        progress_message="Upload received by orchestration worker.",
        total_steps=10,
        processed_count=0,
    )

    html = str(payload.get("html") or "")
    text = str(payload.get("text") or "")

    update_orchestration_progress(
        job_id,
        10.0,
        {"step": "file_saved"},
        current_step="file_saved",
        progress_message="Uploaded file saved successfully.",
        total_steps=10,
        processed_count=1,
    )

    update_orchestration_progress(
        job_id,
        15.0,
        {"step": "extracting_text"},
        current_step="extracting_text",
        progress_message="Extracting text and HTML content.",
        total_steps=10,
        processed_count=2,
    )

    if not workspace_id:
        raise ValueError("Missing workspace_id for document_upload_job.")
    if not doc_id:
        raise ValueError("Missing doc_id for document_upload_job.")
    if not stored_path:
        raise ValueError("Missing stored_path for document_upload_job.")

    update_orchestration_progress(
        job_id,
        15.0,
        {"step": "upload_worker_started", "worker_id": worker_id},
        current_step="upload_worker_started",
        progress_message="Worker started processing uploaded document.",
        total_steps=5,
        processed_count=1,
    )

    from backend.server.stores.upload_intel_store_v2 import build_upload_intelligence
    from backend.server.stores.upload_phrase_pool_builder import build_upload_phrase_pool
    from backend.server.stores.active_phrase_pool_builder import build_active_phrase_pool
    from backend.server.stores.highlight_selection_engine import select_highlight_candidates
    from backend.server.stores.highlight_density_engine import apply_highlight_density

    update_orchestration_progress(
        job_id,
        25.0,
        {"step": "running_smart_extractor"},
        current_step="running_smart_extractor",
        progress_message="Running Smart Extractor.",
        total_steps=10,
        processed_count=3,
    )

    update_orchestration_progress(
        job_id,
        30.0,
        {"step": "running_candidate_window_guard"},
        current_step="running_candidate_window_guard",
        progress_message="Running Candidate Window Guard.",
        total_steps=10,
        processed_count=4,
    )

    update_orchestration_progress(
        job_id,
        35.0,
        {"step": "running_phrase_strength_scorer"},
        current_step="running_phrase_strength_scorer",
        progress_message="Running Phrase Strength Scorer.",
        total_steps=5,
        processed_count=2,
    )

    intel_result = build_upload_intelligence(
        workspace_id=workspace_id,
        doc_id=doc_id,
        stored_path=stored_path,
        original_name=original_name,
        html=html,
        text=text,
    )

    update_orchestration_progress(
        job_id,
        65.0,
        {
            "step": "upload_intelligence_completed",
            "doc_id": doc_id,
        },
        current_step="upload_intelligence_completed",
        progress_message="Upload intelligence completed.",
        total_steps=5,
        processed_count=3,
    )

    upload_pool_result = build_upload_phrase_pool(workspace_id)

    update_orchestration_progress(
        job_id,
        82.0,
        {
            "step": "upload_phrase_pool_rebuilt",
            "doc_id": doc_id,
        },
        current_step="upload_phrase_pool_rebuilt",
        progress_message="Upload phrase pool rebuilt.",
        total_steps=5,
        processed_count=4,
    )

    update_orchestration_progress(
        job_id,
        88.0,
        {"step": "running_highlight_selection", "doc_id": doc_id},
        current_step="running_highlight_selection",
        progress_message="Running Highlight Selection.",
        total_steps=10,
        processed_count=8,
    )

    update_orchestration_progress(
        job_id,
        92.0,
        {"step": "running_highlight_density", "doc_id": doc_id},
        current_step="running_highlight_density",
        progress_message="Running Highlight Density.",
        total_steps=10,
        processed_count=9,
    )

    active_pool_result = {}
    highlight_selection_result = {}
    highlight_density_result = {}

    if not defer_active_rebuild and not defer_highlight_pipeline:
        active_pool_result = build_active_phrase_pool(workspace_id)

        highlight_selection_result = select_highlight_candidates(
            workspace_id=workspace_id,
            doc_id=doc_id,
            article_text=text,
            active_phrase_pool=active_pool_result,
        )

        selected_candidates = []
        if isinstance(highlight_selection_result, dict):
            selected_candidates = highlight_selection_result.get("selected") or []

        highlight_density_result = apply_highlight_density(
            article_text=text,
            selected_candidates=selected_candidates,
        )

    update_orchestration_progress(
        job_id,
        95.0,
        {
            "step": "active_phrase_pool_rebuilt",
            "doc_id": doc_id,
        },
        current_step="active_phrase_pool_rebuilt",
        progress_message="Active phrase pool rebuilt.",
        total_steps=5,
        processed_count=5,
    )

    completion_metadata = {
        "step": "document_upload_job_completed",
        "worker_id": worker_id,
        "workspace_id": workspace_id,
        "doc_id": doc_id,
        "intel_result": intel_result,
        "upload_pool_phrase_count": upload_pool_result.get("phrase_count") if isinstance(upload_pool_result, dict) else None,
        "active_pool_phrase_count": active_pool_result.get("phrase_count") if isinstance(active_pool_result, dict) else None,
        "highlight_selection_stats": highlight_selection_result.get("stats") if isinstance(highlight_selection_result, dict) else None,
        "highlight_density_stats": highlight_density_result.get("stats") if isinstance(highlight_density_result, dict) else None,
        "final_highlight_count": (
            len(highlight_density_result.get("final_highlights") or [])
            if isinstance(highlight_density_result, dict)
            else 0
        ),
    }

    if mark_completed:
        completed = mark_job_completed(job_id, completion_metadata)
    else:
        update_orchestration_progress(
            job_id,
            100.0,
            {
                **completion_metadata,
                "step": "batch_child_document_completed",
            },
            current_step="batch_child_document_completed",
            progress_message=f"Batch child document completed: {original_name or doc_id}",
        )
        completed = type("CompletedProxy", (), {
            "job_id": job_id,
            "status": "running",
            "progress_percent": 100.0,
        })()

    return {
        "ok": True,
        "job_id": completed.job_id,
        "status": completed.status,
        "progress_percent": completed.progress_percent,
        "workspace_id": workspace_id,
        "doc_id": doc_id,
    }


def run_batch_upload_job(job_id: str, worker_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
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
    document_results = []
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

    for index, document in enumerate(documents, start=1):
        doc_id = str(document.get("doc_id") or "").strip()
        original_name = str(document.get("original_name") or document.get("filename") or "").strip()
        stored_path = str(document.get("stored_path") or "").strip()
        html = str(document.get("html") or "")
        text = str(document.get("text") or "")

        document_started_at = perf_counter()
        progress_base = ((index - 1) / max(total_documents, 1)) * 100.0

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

            result_final_highlights = 0
            try:
                result_final_highlights = int(single_result.get("final_highlight_count") or 0)
            except Exception:
                result_final_highlights = 0

            total_final_highlights += result_final_highlights
            if result_final_highlights > 0:
                documents_with_highlights += 1
            else:
                documents_without_highlights += 1

            document_duration_seconds = round(perf_counter() - document_started_at, 4)

            document_results.append({
                "doc_id": doc_id,
                "filename": original_name,
                "status": "completed",
                "final_highlight_count": result_final_highlights,
                "duration_seconds": document_duration_seconds,
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
        document_duration_seconds = round(perf_counter() - document_started_at, 4)
        progress_now = (index / max(total_documents, 1)) * 100.0

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

    from backend.server.stores.active_phrase_pool_builder import build_active_phrase_pool

    update_orchestration_progress(
        job_id,
        98.0,
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

    batch_duration_seconds = round(perf_counter() - batch_started_at, 4)

    batch_success_rate = round(
        (processed_documents / max(total_documents, 1)) * 100,
        2,
    )

    batch_failure_rate = round(
        (failed_documents / max(total_documents, 1)) * 100,
        2,
    )

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
    from backend.server.stores.highlight_selection_engine import select_highlight_candidates
    from backend.server.stores.highlight_density_engine import apply_highlight_density

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

    completed = mark_job_completed(
        job_id,
        {
            "step": "rebuild_active_phrase_pool_completed",
            "worker_id": worker_id,
            "workspace_id": workspace_id,
            "phrase_count": result.get("phrase_count") if isinstance(result, dict) else None,
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


















