from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from backend.server.orchestration.universal_knowledge_orchestrator import (
    read_queue,
)

WORKSPACE_ID = "ws_whattoexpect_com"
JOB_TYPE = "udare_reconstruction"

STORE_ROOT = (
    Path("backend/server/data/udare_store")
    / WORKSPACE_ID
)

ARTICLES_DIR = STORE_ROOT / "articles"
REVIEWS_DIR = STORE_ROOT / "reviews"
METADATA_DIR = STORE_ROOT / "metadata"


def count_files(directory: Path, pattern: str) -> int:
    if not directory.is_dir():
        return 0

    return sum(
        1
        for path in directory.glob(pattern)
        if path.is_file()
    )


all_queue_jobs = read_queue(
    WORKSPACE_ID,
    limit=100000,
)

udare_jobs = [
    job
    for job in all_queue_jobs
    if str(
        job.get("job_type")
        or job.get("stage")
        or ""
    ).strip() == JOB_TYPE
]

queued_udare_jobs = [
    job
    for job in udare_jobs
    if str(
        job.get("status")
        or "queued"
    ).strip().lower() == "queued"
]

articles = count_files(
    ARTICLES_DIR,
    "*.html",
)

reviews = count_files(
    REVIEWS_DIR,
    "*.html",
)

metadata = count_files(
    METADATA_DIR,
    "*.json",
)

status_counts = Counter(
    str(
        job.get("status")
        or "<missing>"
    ).strip().lower()
    for job in udare_jobs
)

job_type_counts = Counter(
    str(
        job.get("job_type")
        or "<missing>"
    ).strip()
    for job in all_queue_jobs
)

stage_counts = Counter(
    str(
        job.get("stage")
        or "<missing>"
    ).strip()
    for job in all_queue_jobs
)

print("=" * 112)
print("PHASE 4.3B LIVE GATE INSPECTION")
print("=" * 112)

print("All queue jobs:", len(all_queue_jobs))
print("All UDARE-matching jobs:", len(udare_jobs))
print("Queued-status UDARE jobs:", len(queued_udare_jobs))
print()

print("Reader articles:", articles)
print("Visual reviews:", reviews)
print("Metadata records:", metadata)
print()

print(
    "Current gate calculation "
    "(articles + all UDARE-matching jobs):",
    articles + len(udare_jobs),
)

print(
    "Queued-only calculation "
    "(articles + queued-status UDARE jobs):",
    articles + len(queued_udare_jobs),
)

print("Expected final count:", 2225)
print()

print(
    "UDARE status counts:",
    json.dumps(
        dict(status_counts),
        indent=2,
        ensure_ascii=False,
    ),
)

print(
    "All queue job_type counts:",
    json.dumps(
        dict(job_type_counts),
        indent=2,
        ensure_ascii=False,
    ),
)

print(
    "All queue stage counts:",
    json.dumps(
        dict(stage_counts),
        indent=2,
        ensure_ascii=False,
    ),
)

print()
print("First five UDARE-matching jobs:")

print(
    json.dumps(
        [
            {
                "job_id": job.get("job_id"),
                "job_type": job.get("job_type"),
                "stage": job.get("stage"),
                "status": job.get("status"),
                "attempts": job.get("attempts"),
                "html_id": (
                    (job.get("payload") or {}).get("html_id")
                    or
                    (job.get("payload") or {}).get(
                        "source_record_id"
                    )
                ),
            }
            for job in udare_jobs[:5]
        ],
        indent=2,
        ensure_ascii=False,
    )
)
