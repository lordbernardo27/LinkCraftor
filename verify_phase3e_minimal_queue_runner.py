from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from backend.server.workers import (
    universal_knowledge_queue_runner
    as runner
)


workspace_id = "ws_phase3e_isolated"

jobs = [
    {
        "job_id": "job_low",
        "workspace_id": workspace_id,
        "job_type": "udare_reconstruction",
        "status": "queued",
        "priority": 8,
        "payload": {},
    },
    {
        "job_id": "job_high",
        "workspace_id": workspace_id,
        "job_type": "udare_reconstruction",
        "status": "queued",
        "priority": 1,
        "payload": {},
    },
    {
        "job_id": "job_medium",
        "workspace_id": workspace_id,
        "job_type": "udare_reconstruction",
        "status": "queued",
        "priority": 5,
        "payload": {},
    },
    {
        "job_id": "job_other_type",
        "workspace_id": workspace_id,
        "job_type": "build_uucd",
        "status": "queued",
        "priority": 0,
        "payload": {},
    },
    {
        "job_id": "job_completed",
        "workspace_id": workspace_id,
        "job_type": "udare_reconstruction",
        "status": "completed",
        "priority": 0,
        "payload": {},
    },
]


executed_order = []
progress_events = []


def fake_execute(job):
    executed_order.append(
        job["job_id"]
    )

    return {
        "ok": job["job_id"] != "job_medium",
        "job_id": job["job_id"],
        "workspace_id": job["workspace_id"],
        "job_type": job["job_type"],
    }


def fake_progress(**values):
    progress_events.append(
        dict(values)
    )

    return {
        "ok": True,
        **values,
    }


with tempfile.TemporaryDirectory() as temp_dir:
    queue_file = (
        Path(temp_dir)
        / "queue.jsonl"
    )

    def fake_queue_path(_workspace_id):
        return queue_file

    def fake_read_queue(_workspace_id, limit=10000):
        return [
            dict(job)
            for job in jobs
        ][:limit]

    with (
        patch.object(
            runner,
            "queue_path",
            fake_queue_path,
        ),
        patch.object(
            runner,
            "read_queue",
            fake_read_queue,
        ),
        patch.object(
            runner,
            "execute_universal_knowledge_job_v1",
            fake_execute,
        ),
        patch.object(
            runner,
            "update_job_progress",
            fake_progress,
        ),
    ):
        result = (
            runner.run_universal_knowledge_queue_v1(
                workspace_id=workspace_id,
                max_jobs=2,
                job_type="udare_reconstruction",
                order_by_priority=True,
            )
        )

    remaining = []

    if queue_file.exists():
        for line in queue_file.read_text(
            encoding="utf-8"
        ).splitlines():
            if line.strip():
                remaining.append(
                    json.loads(line)
                )


remaining_ids = [
    job["job_id"]
    for job in remaining
]

result_by_id = {
    item["job_id"]: item
    for item in result["results"]
}


checks = {
    "priority_order":
        executed_order
        == [
            "job_high",
            "job_medium",
        ],

    "max_jobs_limit":
        len(executed_order)
        == 2,

    "job_type_filter":
        "job_other_type"
        not in executed_order,

    "nonqueued_not_executed":
        "job_completed"
        not in executed_order,

    "overflow_preserved":
        "job_low"
        in remaining_ids,

    "other_type_preserved":
        "job_other_type"
        in remaining_ids,

    "completed_job_preserved":
        "job_completed"
        in remaining_ids,

    "executed_removed_from_queue":
        "job_high"
        not in remaining_ids
        and "job_medium"
        not in remaining_ids,

    "success_count":
        result["executed_ok"]
        == 1,

    "failure_count":
        result["executed_failed"]
        == 1,

    "executed_count":
        result["executed_count"]
        == 2,

    "remaining_count":
        result["remaining_count"]
        == 3,

    "lease_owner_recorded":
        all(
            item.get("lease_owner")
            == result["runner_id"]
            for item in result["results"]
        ),

    "lease_started_recorded":
        all(
            item.get("lease_started_at")
            for item in result["results"]
        ),

    "lease_finished_recorded":
        all(
            item.get("lease_finished_at")
            for item in result["results"]
        ),

    "runner_dequeued_progress":
        sum(
            1
            for event in progress_events
            if event.get("step")
            == "runner_dequeued"
        )
        == 2,

    "runner_finished_progress":
        sum(
            1
            for event in progress_events
            if event.get("step")
            == "runner_finished"
        )
        == 2,

    "failed_result_retained":
        result_by_id[
            "job_medium"
        ][
            "ok"
        ]
        is False,
}


failed = [
    name
    for name, passed
    in checks.items()
    if not passed
]


print()
print("=" * 100)
print("PHASE 3E — MINIMAL QUEUE RUNNER VERIFICATION")
print("=" * 100)

print()
print("EXECUTED ORDER")
for job_id in executed_order:
    print("  -", job_id)

print()
print("REMAINING QUEUE")
for job_id in remaining_ids:
    print("  -", job_id)

print()
print("CHECKS")
for name, passed in checks.items():
    print(
        f"  {name}:",
        "PASS" if passed else "FAIL",
    )

print()
print("=" * 100)

if failed:
    print("PHASE 3E MINIMAL QUEUE RUNNER: FAIL")
    print(
        "Failed checks:",
        ", ".join(failed),
    )
else:
    print("PHASE 3E MINIMAL QUEUE RUNNER: PASS")

print("=" * 100)

print("No real queue was modified.")
print("No real worker was invoked.")
print("No article was reconstructed or stored.")

raise SystemExit(
    0 if not failed else 1
)
