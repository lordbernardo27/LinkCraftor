from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


from backend.server.jobs.universal_knowledge_orchestrator import (
    queue_path,
    read_queue,
)

from backend.server.stores.udare_store import (
    refresh_udare_store_manifest_v1,
    verify_udare_store_v1,
)

from backend.server.workers.universal_knowledge_queue_runner import (
    run_universal_knowledge_queue_v1,
)


WORKSPACE_ID = "ws_whattoexpect_com"
JOB_TYPE = "udare_reconstruction"

EXPECTED_EXECUTED = 5
EXPECTED_REMAINING = 2220

STORE_ROOT = Path(
    "backend/server/data/udare_store"
) / WORKSPACE_ID

ARTICLES_DIR = (
    STORE_ROOT
    / "articles"
)

METADATA_DIR = (
    STORE_ROOT
    / "metadata"
)

INDEX_PATH = (
    STORE_ROOT
    / "index.html"
)

REPORT_DIR = Path(
    "backend/server/data/runtime/"
    "udare_phase_4_3_controlled_execution"
)

REPORT_PATH = (
    REPORT_DIR
    / "phase_4_3a_first_5_report.json"
)

QUEUE_BACKUP_PATH = (
    REPORT_DIR
    / "queue_before_first_5.jsonl"
)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def udare_jobs(
    queue: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    return [
        job

        for job
        in queue

        if str(
            job.get(
                "job_type"
            )
            or job.get(
                "stage"
            )
            or ""
        ).strip()
        == JOB_TYPE
    ]


REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

queue_file = queue_path(
    WORKSPACE_ID
)

if not queue_file.is_file():
    raise RuntimeError(
        f"UDARE queue file does not exist: {queue_file}"
    )


shutil.copy2(
    queue_file,
    QUEUE_BACKUP_PATH,
)


queue_before = read_queue(
    WORKSPACE_ID,
    limit=100000,
)

udare_before = udare_jobs(
    queue_before
)

if len(
    udare_before
) != 2225:
    raise RuntimeError(
        "Expected exactly 2,225 UDARE jobs before execution, "
        f"found {len(udare_before)}."
    )


refresh_udare_store_manifest_v1(
    WORKSPACE_ID
)

store_before = verify_udare_store_v1(
    WORKSPACE_ID
)

counts_before = (
    store_before.get(
        "counts"
    )
    or {}
)

metadata_before = int(
    counts_before.get(
        "metadata_records"
    )
    or 0
)

articles_before = int(
    counts_before.get(
        "article_documents"
    )
    or 0
)

if metadata_before != 0 or articles_before != 0:
    raise RuntimeError(
        "Expected empty UDARE Store before the first real batch: "
        f"metadata={metadata_before}, articles={articles_before}."
    )


print()
print("RUNNING FIRST 5 UDARE JOBS")
print("--------------------------")

runner_result = (
    run_universal_knowledge_queue_v1(
        workspace_id=
            WORKSPACE_ID,

        max_jobs=
            EXPECTED_EXECUTED,

        job_type=
            JOB_TYPE,

        order_by_priority=
            True,
    )
)


results = (
    runner_result.get(
        "results"
    )
    or []
)

successful_results = [
    result

    for result
    in results

    if result.get(
        "ok"
    )
    is True
]

failed_results = [
    result

    for result
    in results

    if result.get(
        "ok"
    )
    is not True
]


queue_after = read_queue(
    WORKSPACE_ID,
    limit=100000,
)

udare_after = udare_jobs(
    queue_after
)


refresh_udare_store_manifest_v1(
    WORKSPACE_ID
)

store_after = verify_udare_store_v1(
    WORKSPACE_ID
)

counts_after = (
    store_after.get(
        "counts"
    )
    or {}
)

metadata_after = int(
    counts_after.get(
        "metadata_records"
    )
    or 0
)

articles_after = int(
    counts_after.get(
        "article_documents"
    )
    or 0
)


article_files = (
    sorted(
        ARTICLES_DIR.glob(
            "*.html"
        )
    )
    if ARTICLES_DIR.is_dir()
    else []
)

metadata_files = (
    sorted(
        METADATA_DIR.glob(
            "*.json"
        )
    )
    if METADATA_DIR.is_dir()
    else []
)


checks = {
    "runner_ok":
        runner_result.get(
            "ok"
        )
        is True,

    "executed_count_5":
        runner_result.get(
            "executed_count"
        )
        == EXPECTED_EXECUTED,

    "successful_count_5":
        len(
            successful_results
        )
        == EXPECTED_EXECUTED,

    "failed_count_zero":
        len(
            failed_results
        )
        == 0,

    "remaining_udare_jobs_2220":
        len(
            udare_after
        )
        == EXPECTED_REMAINING,

    "store_metadata_records_5":
        metadata_after
        == EXPECTED_EXECUTED,

    "store_article_documents_5":
        articles_after
        == EXPECTED_EXECUTED,

    "physical_html_files_5":
        len(
            article_files
        )
        == EXPECTED_EXECUTED,

    "physical_metadata_files_5":
        len(
            metadata_files
        )
        == EXPECTED_EXECUTED,

    "all_html_files_nonempty":
        len(
            article_files
        )
        == EXPECTED_EXECUTED
        and all(
            file.stat().st_size > 0

            for file
            in article_files
        ),

    "all_html_files_reader_documents":
        len(
            article_files
        )
        == EXPECTED_EXECUTED
        and all(
            file.read_text(
                encoding="utf-8",
                errors="replace",
            ).lstrip().casefold().startswith(
                "<!doctype html>"
            )

            for file
            in article_files
        ),
}


failed_checks = [
    name

    for name, passed
    in checks.items()

    if not passed
]


report = {
    "schema_version":
        "udare_phase_4_3a_first_5_report_v1",

    "generated_at_utc":
        utc_now(),

    "workspace_id":
        WORKSPACE_ID,

    "udare_store_root":
        str(
            STORE_ROOT
        ),

    "articles_directory":
        str(
            ARTICLES_DIR
        ),

    "metadata_directory":
        str(
            METADATA_DIR
        ),

    "index_path":
        str(
            INDEX_PATH
        ),

    "index_exists":
        INDEX_PATH.is_file(),

    "queue_backup_path":
        str(
            QUEUE_BACKUP_PATH
        ),

    "queue_udare_count_before":
        len(
            udare_before
        ),

    "queue_udare_count_after":
        len(
            udare_after
        ),

    "runner_result":
        runner_result,

    "successful_count":
        len(
            successful_results
        ),

    "failed_count":
        len(
            failed_results
        ),

    "failed_results":
        failed_results,

    "store_before": {
        "metadata_records":
            metadata_before,

        "article_documents":
            articles_before,
    },

    "store_after": {
        "metadata_records":
            metadata_after,

        "article_documents":
            articles_after,
    },

    "physical_files": {
        "html":
            len(
                article_files
            ),

        "metadata":
            len(
                metadata_files
            ),
    },

    "article_files": [
        str(
            file
        )

        for file
        in article_files
    ],

    "checks":
        checks,

    "failed_checks":
        failed_checks,

    "decision":
        (
            "FIRST_5_UDARE_JOBS_CERTIFIED"
            if not failed_checks
            else "BLOCKED"
        ),
}


REPORT_PATH.write_text(
    json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 112)
print(
    "PHASE 4.3A — FIRST 5 UDARE JOBS"
)
print("=" * 112)

print(
    "UDARE Store root:",
    STORE_ROOT,
)

print(
    "Articles directory:",
    ARTICLES_DIR,
)

print(
    "Metadata directory:",
    METADATA_DIR,
)

print(
    "Clickable index:",
    INDEX_PATH,
)

print(
    "Index currently exists:",
    INDEX_PATH.is_file(),
)

print()
print(
    "UDARE jobs before:",
    len(
        udare_before
    ),
)

print(
    "Jobs executed:",
    runner_result.get(
        "executed_count"
    ),
)

print(
    "Successful:",
    len(
        successful_results
    ),
)

print(
    "Failed:",
    len(
        failed_results
    ),
)

print(
    "UDARE jobs remaining:",
    len(
        udare_after
    ),
)

print(
    "Store metadata records:",
    metadata_after,
)

print(
    "Store HTML documents:",
    articles_after,
)

print()
print("HTML ARTICLES CREATED")

for file in article_files:
    print(
        "  -",
        file,
    )

print()
print("CHECKS")

for name, passed in checks.items():
    print(
        f"  {name}:",
        (
            "PASS"
            if passed
            else "FAIL"
        ),
    )

print()
print(
    "Report:",
    REPORT_PATH,
)

print()
print("=" * 112)
print(
    "PHASE 4.3A DECISION:",
    report[
        "decision"
    ],
)
print("=" * 112)

raise SystemExit(
    0
    if not failed_checks
    else 1
)
