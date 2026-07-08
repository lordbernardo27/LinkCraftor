from __future__ import annotations

from backend.server.jobs.universal_knowledge_orchestrator import create_universal_knowledge_job
from backend.server.runtime.universal_runtime_infrastructure import upload_batch_completion_gate
from backend.server.workers.universal_knowledge_worker import execute_universal_knowledge_job_v1


def fail(msg: str):
    raise AssertionError(msg)


def main():
    workspace_id = "ws_phase_45b_upload_gate"
    upload_batch_id = "upload_batch_8_docs"

    document_jobs = []

    for i in range(1, 9):
        job = create_universal_knowledge_job(
            workspace_id=workspace_id,
            job_type="upload_document_extraction",
            payload={
                "upload_batch_id": upload_batch_id,
                "document_id": f"DOC_UPLOAD_{i}",
                "filename": f"document_{i}.docx",
            },
        )
        document_jobs.append(job)

    gate_before = upload_batch_completion_gate(
        workspace_id=workspace_id,
        upload_batch_id=upload_batch_id,
        document_jobs=document_jobs,
    )

    if gate_before.get("document_count") != 8:
        fail("Gate should track 8 uploaded documents")

    if gate_before.get("decision") != "in_progress":
        fail("Gate should be in_progress before document jobs complete")

    for job in document_jobs:
        result = execute_universal_knowledge_job_v1(job)
        if not result.get("ok"):
            fail("Document job failed during verification")

    gate_after = upload_batch_completion_gate(
        workspace_id=workspace_id,
        upload_batch_id=upload_batch_id,
        document_jobs=document_jobs,
    )

    if gate_after.get("decision") != "complete":
        fail(f"Gate should be complete after all documents complete: {gate_after}")

    if gate_after.get("upload_ready_for_certification") is not True:
        fail("Upload batch should be ready for certification after all documents complete")

    print("UPLOAD BATCH COMPLETION GATE PASSED")
    print("Workspace:", workspace_id)
    print("Upload batch:", upload_batch_id)
    print("Document count:", gate_after.get("document_count"))
    print("Completed:", gate_after.get("completed_count"))
    print("Failed:", gate_after.get("failed_count"))
    print("Pending:", gate_after.get("pending_count"))
    print("Decision:", gate_after.get("decision"))
    print("Ready for certification:", gate_after.get("upload_ready_for_certification"))
    print("Gate path:", gate_after.get("gate_path"))


if __name__ == "__main__":
    main()
