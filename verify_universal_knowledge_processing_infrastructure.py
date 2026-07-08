from __future__ import annotations

from backend.server.jobs.universal_knowledge_orchestrator import (
    explain_universal_knowledge_orchestrator_v1,
    read_job_progress,
    read_job_status,
    read_queue,
)
from backend.server.workers.universal_knowledge_worker import (
    create_and_execute_local_job_v1,
)


def fail(msg: str):
    raise AssertionError(msg)


def main():
    workspace_id = "ws_phase_45a_orchestration_test"

    upload = create_and_execute_local_job_v1(
        workspace_id=workspace_id,
        job_type="upload_document_batch",
        payload={
            "documents": [
                {"document_id": "DOC_A", "filename": "a.docx"},
                {"document_id": "DOC_B", "filename": "b.md"},
            ],
        },
    )

    if not upload.get("ok"):
        fail("Upload batch job failed")

    website = create_and_execute_local_job_v1(
        workspace_id=workspace_id,
        job_type="website_crawl_batch",
        payload={
            "urls": [
                "https://example.com/a",
                "https://example.com/b",
            ],
        },
    )

    if not website.get("ok"):
        fail("Website crawl batch job failed")

    cert = create_and_execute_local_job_v1(
        workspace_id=workspace_id,
        job_type="certify_uucd_body_store",
        payload={
            "reason": "verification",
        },
    )

    if not cert.get("ok"):
        fail("Certification job failed")

    queue = read_queue(workspace_id)
    if len(queue) < 3:
        fail("Expected at least 3 queued jobs")

    for result in [upload, website, cert]:
        job_id = result["job_id"]
        status = read_job_status(workspace_id, job_id)
        progress = read_job_progress(workspace_id, job_id)

        if status.get("status") != "completed":
            fail(f"Job did not complete: {job_id}")

        if progress.get("percent") != 100:
            fail(f"Progress not 100 for job: {job_id}")

    explanation = explain_universal_knowledge_orchestrator_v1()

    print("PHASE 4.5A UNIVERSAL KNOWLEDGE PROCESSING INFRASTRUCTURE PASSED")
    print("Component:", explanation.get("component"))
    print("Workspace:", workspace_id)
    print("Queued jobs:", len(queue))
    print("Supported job types:", len(explanation.get("supported_job_types") or []))
    print("Scaling rule:", explanation.get("scaling_rule"))
    print("Next stage:", explanation.get("next_stage"))


if __name__ == "__main__":
    main()
