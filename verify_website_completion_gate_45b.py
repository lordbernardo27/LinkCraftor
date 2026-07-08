from __future__ import annotations

from backend.server.jobs.universal_knowledge_orchestrator import create_universal_knowledge_job
from backend.server.runtime.universal_runtime_infrastructure import website_completion_gate
from backend.server.workers.universal_knowledge_worker import execute_universal_knowledge_job_v1


def fail(msg: str):
    raise AssertionError(msg)


def main():
    workspace_id = "ws_phase_45b_website_gate"
    website_id = "example_com"

    page_jobs = []

    for url in [
        "https://example.com/page-1",
        "https://example.com/page-2",
        "https://example.com/page-3",
    ]:
        job = create_universal_knowledge_job(
            workspace_id=workspace_id,
            job_type="raw_html_acquisition",
            payload={
                "website_id": website_id,
                "url": url,
            },
        )
        page_jobs.append(job)

    gate_before = website_completion_gate(
        workspace_id=workspace_id,
        website_id=website_id,
        page_jobs=page_jobs,
    )

    if gate_before.get("decision") != "in_progress":
        fail("Gate should be in_progress before page jobs complete")

    for job in page_jobs:
        result = execute_universal_knowledge_job_v1(job)
        if not result.get("ok"):
            fail("Page job failed during verification")

    gate_after = website_completion_gate(
        workspace_id=workspace_id,
        website_id=website_id,
        page_jobs=page_jobs,
    )

    if gate_after.get("decision") != "complete":
        fail(f"Gate should be complete after all pages complete: {gate_after}")

    if gate_after.get("website_ready_for_certification") is not True:
        fail("Website should be ready for certification after all pages complete")

    print("WEBSITE COMPLETION GATE PASSED")
    print("Workspace:", workspace_id)
    print("Website:", website_id)
    print("Page count:", gate_after.get("page_count"))
    print("Completed:", gate_after.get("completed_count"))
    print("Failed:", gate_after.get("failed_count"))
    print("Pending:", gate_after.get("pending_count"))
    print("Decision:", gate_after.get("decision"))
    print("Ready for certification:", gate_after.get("website_ready_for_certification"))
    print("Gate path:", gate_after.get("gate_path"))


if __name__ == "__main__":
    main()
