from __future__ import annotations

import json
from pathlib import Path


REPORT = Path(
    "backend/server/data/runtime/"
    "udare_phase_4_3_controlled_execution/"
    "phase_4_3a_first_5_report.json"
)

if not REPORT.is_file():
    raise RuntimeError(
        f"Missing Phase 4.3A report: {REPORT}"
    )

data = json.loads(
    REPORT.read_text(
        encoding="utf-8",
        errors="replace",
    )
)

runner = data.get("runner_result") or {}
results = runner.get("results") or []

failed = [
    row
    for row in results
    if isinstance(row, dict)
    and row.get("ok") is not True
]

print()
print("=" * 110)
print("LATEST PHASE 4.3A FAILURE DETAILS")
print("=" * 110)

print("Executed:", runner.get("executed_count"))
print("Successful:", data.get("successful_count"))
print("Failed:", data.get("failed_count"))
print("Queue before:", data.get("queue_udare_count_before"))
print("Queue after:", data.get("queue_udare_count_after"))

print()
print("FAILED JOBS")

for index, row in enumerate(failed, start=1):
    failure = row.get("failure")

    error = (
        row.get("error")
        or (
            failure.get("error")
            if isinstance(failure, dict)
            else ""
        )
        or (
            failure.get("message")
            if isinstance(failure, dict)
            else ""
        )
        or ""
    )

    print()
    print(f"{index}. Job ID: {row.get('job_id')}")
    print("   Error:", error or "(none)")
    print("   Result keys:", sorted(row.keys()))

    if isinstance(failure, dict):
        print(
            "   Failure record:",
            json.dumps(
                failure,
                indent=2,
                ensure_ascii=False,
            ),
        )

print()
print("FAILED CHECKS")
for name in data.get("failed_checks") or []:
    print("  -", name)

print()
print("=" * 110)
print("INSPECTION COMPLETE")
print("=" * 110)

print("No queue was modified.")
print("No worker was invoked.")
print("No UDARE Store write was performed.")
