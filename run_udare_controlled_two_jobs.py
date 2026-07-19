from __future__ import annotations

import json
import traceback
from collections import Counter
from pathlib import Path

from backend.server.jobs.universal_knowledge_orchestrator import (
    queue_path,
    read_queue,
)
from backend.server.workers.universal_knowledge_queue_runner import (
    run_universal_knowledge_queue_v1,
)


WORKSPACE_ID = "ws_whattoexpect_com"
JOB_TYPE = "udare_reconstruction"
MAX_JOBS = 2

UDARE_ROOT = (
    Path("backend/server/data/udare_store")
    / WORKSPACE_ID
)

ARTICLE_DIR = UDARE_ROOT / "articles"
REVIEW_DIR = UDARE_ROOT / "review"
METADATA_DIR = UDARE_ROOT / "metadata"


def count_files(path: Path, suffix: str | None = None) -> int:
    if not path.exists():
        return 0

    return sum(
        1
        for item in path.rglob("*")
        if item.is_file()
        and (
            suffix is None
            or item.suffix.lower() == suffix.lower()
        )
    )


def queue_snapshot() -> dict:
    rows = read_queue(
        WORKSPACE_ID,
        limit=10000,
    )

    status_counts = Counter(
        str(row.get("status") or "unknown")
        for row in rows
    )

    type_counts = Counter(
        str(row.get("job_type") or "unknown")
        for row in rows
    )

    udare_rows = [
        row
        for row in rows
        if str(row.get("job_type") or "") == JOB_TYPE
    ]

    return {
        "total": len(rows),
        "status_counts": dict(status_counts),
        "type_counts": dict(type_counts),
        "udare_count": len(udare_rows),
        "first_two_udare": [
            {
                "job_id": row.get("job_id"),
                "status": row.get("status"),
                "priority": row.get("priority"),
                "html_id": (
                    (row.get("payload") or {}).get("html_id")
                    if isinstance(row.get("payload"), dict)
                    else None
                ),
                "source_record_id": (
                    (row.get("payload") or {}).get(
                        "source_record_id"
                    )
                    if isinstance(row.get("payload"), dict)
                    else None
                ),
                "source_url": (
                    (row.get("payload") or {}).get("source_url")
                    if isinstance(row.get("payload"), dict)
                    else None
                ),
            }
            for row in udare_rows[:2]
        ],
    }


def store_snapshot() -> dict:
    return {
        "article_html": count_files(
            ARTICLE_DIR,
            ".html",
        ),
        "review_files": count_files(REVIEW_DIR),
        "metadata_files": count_files(METADATA_DIR),
        "all_store_files": count_files(UDARE_ROOT),
    }


print()
print("=" * 112)
print("UDARE CONTROLLED TWO-JOB EXECUTION")
print("=" * 112)
print("Workspace:", WORKSPACE_ID)
print("Job type:", JOB_TYPE)
print("Maximum jobs:", MAX_JOBS)
print("Active queue:", queue_path(WORKSPACE_ID))


before_queue = queue_snapshot()
before_store = store_snapshot()

print()
print("=" * 112)
print("BEFORE EXECUTION — QUEUE")
print("=" * 112)
print(
    json.dumps(
        before_queue,
        indent=2,
        ensure_ascii=False,
    )
)

print()
print("=" * 112)
print("BEFORE EXECUTION — UDARE STORE")
print("=" * 112)
print(
    json.dumps(
        before_store,
        indent=2,
        ensure_ascii=False,
    )
)


print()
print("=" * 112)
print("EXECUTING EXACTLY TWO UDARE JOBS")
print("=" * 112)

try:
    result = run_universal_knowledge_queue_v1(
        workspace_id=WORKSPACE_ID,
        max_jobs=MAX_JOBS,
        job_type=JOB_TYPE,
        order_by_priority=True,
    )
except Exception as exc:
    print()
    print("RUNNER RAISED AN EXCEPTION")
    print("Exception type:", type(exc).__name__)
    print("Exception:", str(exc))
    print()
    traceback.print_exc()
    raise


print()
print("=" * 112)
print("RUNNER RESULT")
print("=" * 112)
print(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False,
        default=str,
    )
)


after_queue = queue_snapshot()
after_store = store_snapshot()

print()
print("=" * 112)
print("AFTER EXECUTION — QUEUE")
print("=" * 112)
print(
    json.dumps(
        after_queue,
        indent=2,
        ensure_ascii=False,
    )
)

print()
print("=" * 112)
print("AFTER EXECUTION — UDARE STORE")
print("=" * 112)
print(
    json.dumps(
        after_store,
        indent=2,
        ensure_ascii=False,
    )
)


print()
print("=" * 112)
print("CONTROLLED-RUN DELTAS")
print("=" * 112)

print(
    "Total queue delta:",
    after_queue["total"] - before_queue["total"],
)

print(
    "UDARE queue delta:",
    after_queue["udare_count"]
    - before_queue["udare_count"],
)

print(
    "Article HTML delta:",
    after_store["article_html"]
    - before_store["article_html"],
)

print(
    "Review-file delta:",
    after_store["review_files"]
    - before_store["review_files"],
)

print(
    "Metadata-file delta:",
    after_store["metadata_files"]
    - before_store["metadata_files"],
)


print()
print("=" * 112)
print("PASS / FAIL ASSESSMENT")
print("=" * 112)

executed_count = int(
    result.get("executed_count") or 0
)

executed_ok = int(
    result.get("executed_ok") or 0
)

executed_failed = int(
    result.get("executed_failed") or 0
)

expected_queue_delta = -executed_count
actual_queue_delta = (
    after_queue["udare_count"]
    - before_queue["udare_count"]
)

checks = {
    "exactly_two_jobs_selected": executed_count == 2,
    "two_jobs_succeeded": executed_ok == 2,
    "no_jobs_failed": executed_failed == 0,
    "udare_queue_reduced_correctly": (
        actual_queue_delta == expected_queue_delta
    ),
    "unrelated_queue_jobs_preserved": (
        (
            after_queue["total"]
            - after_queue["udare_count"]
        )
        ==
        (
            before_queue["total"]
            - before_queue["udare_count"]
        )
    ),
}

for name, passed in checks.items():
    print(
        f"{'PASS' if passed else 'FAIL'}: {name}"
    )

print()

if all(checks.values()):
    print(
        "FINAL RESULT: PASS — the repaired Raw HTML "
        "loader successfully supported the controlled "
        "UDARE execution."
    )
else:
    print(
        "FINAL RESULT: FAIL — do not resume the remaining "
        "UDARE queue. Review the runner result and exception "
        "details above."
    )
