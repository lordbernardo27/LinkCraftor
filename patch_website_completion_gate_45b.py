from pathlib import Path

p = Path("backend/server/runtime/universal_runtime_infrastructure.py")
code = p.read_text(encoding="utf-8")

insert = r'''


def website_completion_gate(
    *,
    workspace_id: str,
    website_id: str,
    page_jobs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Website-level completion gate.

    A website is complete only after all discovered page jobs have reached
    terminal states and no required page remains pending/running.
    """

    ws = safe_id(workspace_id)
    site = safe_id(website_id, "website")

    page_count = len(page_jobs)
    status_counts = Counter()

    failed_pages: List[Dict[str, Any]] = []
    pending_pages: List[Dict[str, Any]] = []
    completed_pages: List[Dict[str, Any]] = []

    terminal_statuses = {"completed", "failed", "dead_letter"}

    for job in page_jobs:
        job_id = job.get("job_id", "")
        status = read_job_status(ws, job_id)
        state = status.get("status") or job.get("status") or "unknown"

        status_counts[state] += 1

        row = {
            "job_id": job_id,
            "job_type": job.get("job_type"),
            "status": state,
            "url": (job.get("payload") or {}).get("url") or (job.get("payload") or {}).get("canonical_url") or "",
        }

        if state == "completed":
            completed_pages.append(row)
        elif state in {"failed", "dead_letter"}:
            failed_pages.append(row)
        else:
            pending_pages.append(row)

    all_terminal = all(
        (read_job_status(ws, j.get("job_id", "")).get("status") or j.get("status")) in terminal_statuses
        for j in page_jobs
    ) if page_jobs else False

    all_completed = page_count > 0 and len(completed_pages) == page_count
    has_failures = len(failed_pages) > 0
    has_pending = len(pending_pages) > 0

    if all_completed:
        decision = "complete"
        website_ready_for_certification = True
    elif all_terminal and has_failures:
        decision = "partial_complete_with_failures"
        website_ready_for_certification = len(completed_pages) > 0
    elif has_pending:
        decision = "in_progress"
        website_ready_for_certification = False
    else:
        decision = "blocked"
        website_ready_for_certification = False

    gate = {
        "schema_version": "website_completion_gate_v1",
        "workspace_id": ws,
        "website_id": site,
        "page_count": page_count,
        "completed_count": len(completed_pages),
        "failed_count": len(failed_pages),
        "pending_count": len(pending_pages),
        "status_counts": dict(status_counts),
        "completed_pages": completed_pages,
        "failed_pages": failed_pages,
        "pending_pages": pending_pages,
        "all_terminal": all_terminal,
        "all_completed": all_completed,
        "decision": decision,
        "website_ready_for_certification": website_ready_for_certification,
        "created_at": now_iso(),
    }

    path = RUNTIME_ROOT / "website_completion_gates" / ws / f"website_completion_gate_{site}.json"
    write_json(path, gate)
    gate["gate_path"] = str(path)

    return gate
'''

if "def website_completion_gate(" not in code:
    code = code + insert

p.write_text(code, encoding="utf-8")
print("Added website_completion_gate.")
