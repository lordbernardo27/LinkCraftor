from __future__ import annotations

import json
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
MAX_JOBS = 50

UDARE_ROOT = (
    Path("backend/server/data/udare_store")
    / WORKSPACE_ID
)

ARTICLES_DIR = UDARE_ROOT / "articles"
METADATA_DIR = UDARE_ROOT / "metadata"
REVIEWS_DIR = UDARE_ROOT / "reviews"


def count_files(directory: Path, pattern: str) -> int:
    if not directory.exists():
        return 0

    return sum(
        1
        for path in directory.glob(pattern)
        if path.is_file()
    )


def queue_snapshot() -> dict:
    jobs = read_queue(
        WORKSPACE_ID,
        limit=10000,
    )

    type_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}

    for job in jobs:
        job_type = str(
            job.get("job_type") or ""
        )
        status = str(
            job.get("status") or ""
        )

        type_counts[job_type] = (
            type_counts.get(job_type, 0) + 1
        )
        status_counts[status] = (
            status_counts.get(status, 0) + 1
        )

    udare_jobs = [
        job
        for job in jobs
        if job.get("job_type") == JOB_TYPE
        and job.get("status") == "queued"
    ]

    return {
        "total": len(jobs),
        "status_counts": status_counts,
        "type_counts": type_counts,
        "udare_count": len(udare_jobs),
        "first_five_udare": [
            {
                "job_id": job.get("job_id"),
                "priority": job.get("priority"),
                "html_id": (
                    (job.get("payload") or {}).get(
                        "html_id"
                    )
                    or
                    (job.get("payload") or {}).get(
                        "source_record_id"
                    )
                ),
                "source_url": (
                    (job.get("payload") or {}).get(
                        "source_url"
                    )
                ),
            }
            for job in udare_jobs[:5]
        ],
    }


def store_snapshot() -> dict:
    return {
        "article_html": count_files(
            ARTICLES_DIR,
            "*.html",
        ),
        "metadata_files": count_files(
            METADATA_DIR,
            "*.json",
        ),
        "review_files": count_files(
            REVIEWS_DIR,
            "*.html",
        ),
    }


def heading(title: str) -> None:
    print()
    print("=" * 112)
    print(title)
    print("=" * 112)


heading("UDARE CONTROLLED FIFTY-JOB EXECUTION")

print("Workspace:", WORKSPACE_ID)
print("Job type:", JOB_TYPE)
print("Maximum jobs:", MAX_JOBS)
print("Active queue:", queue_path(WORKSPACE_ID))

before_queue = queue_snapshot()
before_store = store_snapshot()

heading("BEFORE EXECUTION — QUEUE")
print(
    json.dumps(
        before_queue,
        indent=2,
        ensure_ascii=False,
    )
)

heading("BEFORE EXECUTION — UDARE STORE")
print(
    json.dumps(
        before_store,
        indent=2,
        ensure_ascii=False,
    )
)

if before_queue["udare_count"] < MAX_JOBS:
    raise RuntimeError(
        "Not enough queued UDARE jobs for the "
        f"requested batch. Available: "
        f"{before_queue['udare_count']}"
    )

heading("EXECUTING EXACTLY FIFTY UDARE JOBS")

result = run_universal_knowledge_queue_v1(
    workspace_id=WORKSPACE_ID,
    max_jobs=MAX_JOBS,
    job_type=JOB_TYPE,
    order_by_priority=True,
)

heading("RUNNER RESULT")
print(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False,
    )
)

after_queue = queue_snapshot()
after_store = store_snapshot()

heading("AFTER EXECUTION — QUEUE")
print(
    json.dumps(
        after_queue,
        indent=2,
        ensure_ascii=False,
    )
)

heading("AFTER EXECUTION — UDARE STORE")
print(
    json.dumps(
        after_store,
        indent=2,
        ensure_ascii=False,
    )
)

queue_delta = (
    after_queue["total"]
    - before_queue["total"]
)

udare_delta = (
    after_queue["udare_count"]
    - before_queue["udare_count"]
)

article_delta = (
    after_store["article_html"]
    - before_store["article_html"]
)

metadata_delta = (
    after_store["metadata_files"]
    - before_store["metadata_files"]
)

review_delta = (
    after_store["review_files"]
    - before_store["review_files"]
)

executed_count = int(
    result.get("executed_count") or 0
)

executed_ok = int(
    result.get("executed_ok") or 0
)

executed_failed = int(
    result.get("executed_failed") or 0
)

heading("CONTROLLED-RUN DELTAS")

print("Total queue delta:", queue_delta)
print("UDARE queue delta:", udare_delta)
print("Article HTML delta:", article_delta)
print("Metadata-file delta:", metadata_delta)
print("Review-file delta:", review_delta)
print("Executed count:", executed_count)
print("Executed OK:", executed_ok)
print("Executed failed:", executed_failed)

checks = {
    "exactly_fifty_jobs_selected":
        executed_count == 50,

    "fifty_jobs_succeeded":
        executed_ok == 50,

    "no_jobs_failed":
        executed_failed == 0,

    "total_queue_reduced_correctly":
        queue_delta == -50,

    "udare_queue_reduced_correctly":
        udare_delta == -50,

    "article_count_increased_correctly":
        article_delta == 50,

    "metadata_count_increased_correctly":
        metadata_delta == 50,

    "review_count_increased_correctly":
        review_delta == 50,
}

heading("PASS / FAIL ASSESSMENT")

for name, passed in checks.items():
    print(
        f"{'PASS' if passed else 'FAIL'}: {name}"
    )

failed_results = [
    item
    for item in (result.get("results") or [])
    if not item.get("ok")
]

if failed_results:
    heading("FAILED JOB DETAILS")

    print(
        json.dumps(
            failed_results,
            indent=2,
            ensure_ascii=False,
        )
    )

overall = all(checks.values())

print()

if overall:
    print(
        "FINAL RESULT: PASS — all fifty controlled "
        "UDARE jobs completed and persisted correctly."
    )
else:
    print(
        "FINAL RESULT: FAIL — stop further population "
        "and inspect the failed jobs or count mismatch."
    )

raise SystemExit(
    0 if overall else 1
)
