from pathlib import Path

p = Path("backend/server/runtime/universal_runtime_infrastructure.py")
code = p.read_text(encoding="utf-8")

insert = r'''


def upload_batch_completion_gate(
    *,
    workspace_id: str,
    upload_batch_id: str,
    document_jobs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Upload-batch completion gate.

    A document upload batch is complete only after all uploaded document jobs
    have reached terminal states.
    """

    ws = safe_id(workspace_id)
    batch = safe_id(upload_batch_id, "upload_batch")

    document_count = len(document_jobs)
    status_counts = Counter()

    failed_documents: List[Dict[str, Any]] = []
    pending_documents: List[Dict[str, Any]] = []
    completed_documents: List[Dict[str, Any]] = []

    terminal_statuses = {"completed", "failed", "dead_letter"}

    for job in document_jobs:
        job_id = job.get("job_id", "")
        status = read_job_status(ws, job_id)
        state = status.get("status") or job.get("status") or "unknown"

        status_counts[state] += 1

        row = {
            "job_id": job_id,
            "job_type": job.get("job_type"),
            "status": state,
            "document_id": (job.get("payload") or {}).get("document_id") or "",
            "filename": (job.get("payload") or {}).get("filename") or "",
        }

        if state == "completed":
            completed_documents.append(row)
        elif state in {"failed", "dead_letter"}:
            failed_documents.append(row)
        else:
            pending_documents.append(row)

    all_terminal = all(
        (read_job_status(ws, j.get("job_id", "")).get("status") or j.get("status")) in terminal_statuses
        for j in document_jobs
    ) if document_jobs else False

    all_completed = document_count > 0 and len(completed_documents) == document_count
    has_failures = len(failed_documents) > 0
    has_pending = len(pending_documents) > 0

    if all_completed:
        decision = "complete"
        upload_ready_for_certification = True
    elif all_terminal and has_failures:
        decision = "partial_complete_with_failures"
        upload_ready_for_certification = len(completed_documents) > 0
    elif has_pending:
        decision = "in_progress"
        upload_ready_for_certification = False
    else:
        decision = "blocked"
        upload_ready_for_certification = False

    gate = {
        "schema_version": "upload_batch_completion_gate_v1",
        "workspace_id": ws,
        "upload_batch_id": batch,
        "document_count": document_count,
        "completed_count": len(completed_documents),
        "failed_count": len(failed_documents),
        "pending_count": len(pending_documents),
        "status_counts": dict(status_counts),
        "completed_documents": completed_documents,
        "failed_documents": failed_documents,
        "pending_documents": pending_documents,
        "all_terminal": all_terminal,
        "all_completed": all_completed,
        "decision": decision,
        "upload_ready_for_certification": upload_ready_for_certification,
        "created_at": now_iso(),
    }

    path = RUNTIME_ROOT / "upload_batch_completion_gates" / ws / f"upload_batch_completion_gate_{batch}.json"
    write_json(path, gate)
    gate["gate_path"] = str(path)

    return gate
'''

if "def upload_batch_completion_gate(" not in code:
    code = code + insert

p.write_text(code, encoding="utf-8")
print("Added upload_batch_completion_gate.")
