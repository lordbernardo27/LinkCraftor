from __future__ import annotations

from backend.server.jobs.universal_knowledge_orchestrator import create_universal_knowledge_job
from backend.server.runtime.universal_runtime_infrastructure import (
    certify_runtime_infrastructure,
    create_batch,
    inspect_batch,
    inspect_queue,
    inspect_workers,
    move_to_dead_letter,
    retry_job,
    runtime_job_summary,
    runtime_metrics,
    runtime_progress_summary,
    worker_heartbeat,
)
from backend.server.workers.universal_knowledge_worker import execute_universal_knowledge_job_v1


def fail(msg: str):
    raise AssertionError(msg)


def main():
    workspace_id = "ws_phase_45b_runtime_test"

    worker_heartbeat(workspace_id, "worker_1", state="idle")
    worker_heartbeat(workspace_id, "worker_2", state="busy", current_job_id="test_job")

    job1 = create_universal_knowledge_job(
        workspace_id=workspace_id,
        job_type="build_body_store",
        payload={"verification": True},
    )
    job2 = create_universal_knowledge_job(
        workspace_id=workspace_id,
        job_type="certify_uucd_body_store",
        payload={"verification": True},
    )

    result1 = execute_universal_knowledge_job_v1(job1)
    result2 = execute_universal_knowledge_job_v1(job2)

    if not result1.get("ok") or not result2.get("ok"):
        fail("Worker execution failed")

    summary = runtime_job_summary(workspace_id)
    if summary.get("total_jobs", 0) < 2:
        fail("Job summary did not find jobs")

    progress = runtime_progress_summary(workspace_id, job1["job_id"])
    if progress.get("percent") != 100:
        fail("Progress summary not complete")

    queue = inspect_queue(workspace_id)
    if queue.get("queue_size", 0) < 2:
        fail("Queue inspector failed")

    workers = inspect_workers(workspace_id)
    if workers.get("worker_count", 0) < 2:
        fail("Worker manager failed")

    batch = create_batch(workspace_id, "batch_runtime_test", [job1, job2])
    batch_view = inspect_batch(workspace_id, "batch_runtime_test")
    if batch_view.get("job_count") != 2:
        fail("Batch scheduler failed")

    retry = retry_job(workspace_id, job1)
    if not retry.get("ok"):
        fail("Retry manager failed")

    dead = move_to_dead_letter(workspace_id, job2, "verification dead letter")
    if not dead.get("reason"):
        fail("Dead letter queue failed")

    metrics = runtime_metrics(workspace_id)
    if "success_rate_percent" not in metrics:
        fail("Runtime metrics failed")

    cert = certify_runtime_infrastructure(workspace_id)
    if not cert.get("certified"):
        fail(f"Runtime certification failed: {cert}")

    print("PHASE 4.5B RUNTIME INFRASTRUCTURE PASSED")
    print("Workspace:", workspace_id)
    print("Jobs:", summary.get("total_jobs"))
    print("Queue size:", queue.get("queue_size"))
    print("Workers:", workers.get("worker_count"))
    print("Batch jobs:", batch.get("job_count"))
    print("Runtime ready:", cert.get("runtime_ready"))
    print("Next stage:", cert.get("next_stage"))


if __name__ == "__main__":
    main()
