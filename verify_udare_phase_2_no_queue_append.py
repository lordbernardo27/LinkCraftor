from __future__ import annotations

import json
from pathlib import Path

from backend.server.jobs.universal_knowledge_orchestrator import (
    queue_path,
)


report_path = Path(
    "backend/server/data/runtime/"
    "udare_runtime_phase_2_verification/"
    "udare_runtime_phase_2_verification.json"
)

if not report_path.is_file():
    raise RuntimeError(
        "Phase 2 verification report is missing."
    )

report = json.loads(
    report_path.read_text(
        encoding="utf-8-sig"
    )
)

if report.get(
    "status"
) != "PASS":
    raise RuntimeError(
        "Phase 2 report does not contain PASS."
    )

test_job = (
    report.get(
        "test_job"
    )
    or {}
)

workspace_id = str(
    test_job.get(
        "workspace_id"
    )
    or ""
)

correlation_token = str(
    test_job.get(
        "correlation_token"
    )
    or ""
)

job_id = str(
    test_job.get(
        "job_id"
    )
    or ""
)

if not all(
    (
        workspace_id,
        correlation_token,
        job_id,
    )
):
    raise RuntimeError(
        "Phase 2 report has incomplete test-job identity."
    )

path = queue_path(
    workspace_id
)

queue_contains_token = False
queue_contains_job_id = False

if path.is_file():
    queue_text = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    queue_contains_token = (
        correlation_token
        in queue_text
    )

    queue_contains_job_id = (
        job_id
        in queue_text
    )

if queue_contains_token:
    raise RuntimeError(
        "Phase 2 correlation token was appended "
        "to the execution queue."
    )

if queue_contains_job_id:
    raise RuntimeError(
        "Phase 2 test job ID was appended "
        "to the execution queue."
    )

print(
    "Phase 2 test job queue append: NOT FOUND"
)

print(
    "Queue dispatch suppression: PASS"
)

print(
    "Queue path:",
    path,
)
