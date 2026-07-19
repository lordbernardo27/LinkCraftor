from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


from backend.server.jobs.universal_knowledge_orchestrator import (
    create_universal_knowledge_job,
    job_status_path,
    progress_path,
    queue_path,
    read_queue,
    safe_id,
)

from backend.server.stores.udare_store import (
    refresh_udare_store_manifest_v1,
    verify_udare_store_v1,
)


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_JOB_COUNT = 2225

PIPELINE = "website_reconstruction"
STAGE = "udare_reconstruction"
JOB_TYPE = "udare_reconstruction"

SOURCE_STORE_VERSION = "raw_website_html_store_v1"
UDARE_ENGINE = "universal_dom_article_reconstruction_engine_v1_7"
TARGET_STORE = "udare_store_v1"
ARTICLE_DOCUMENT_FORMAT = "udare_article_reader_document_v1"

MANIFEST_PATH = Path(
    "backend/server/data/runtime/"
    "udare_population_readiness/"
    "population_manifest.json"
)

REPORT_DIR = Path(
    "backend/server/data/runtime/"
    "udare_phase_4_2_job_creation"
)

REPORT_PATH = (
    REPORT_DIR
    / "phase_4_2_job_creation_report.json"
)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def load_manifest() -> List[Dict[str, Any]]:
    if not MANIFEST_PATH.is_file():
        raise RuntimeError(
            f"Missing certified population manifest: {MANIFEST_PATH}"
        )

    value = json.loads(
        MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(
        value,
        list,
    ):
        raise RuntimeError(
            "Population manifest must be a JSON list."
        )

    return value


workspace_id = safe_id(
    WORKSPACE_ID
)

manifest = load_manifest()

if len(
    manifest
) != EXPECTED_JOB_COUNT:
    raise RuntimeError(
        "Population manifest count mismatch: "
        f"expected {EXPECTED_JOB_COUNT}, found {len(manifest)}."
    )


# ---------------------------------------------------------------------
# Preflight: validate manifest identities
# ---------------------------------------------------------------------

manifest_html_ids: List[str] = []
manifest_urls: List[str] = []

missing_html_id: List[int] = []
missing_source_url: List[str] = []
duplicate_html_ids: List[str] = []

seen_html_ids: set[str] = set()


for index, entry in enumerate(
    manifest
):
    if not isinstance(
        entry,
        dict,
    ):
        raise RuntimeError(
            f"Manifest entry {index} is not an object."
        )

    html_id = str(
        entry.get(
            "html_id"
        )
        or ""
    ).strip()

    source_url = str(
        entry.get(
            "source_url"
        )
        or ""
    ).strip()

    if not html_id:
        missing_html_id.append(
            index
        )

    elif html_id in seen_html_ids:
        duplicate_html_ids.append(
            html_id
        )

    seen_html_ids.add(
        html_id
    )

    if not source_url:
        missing_source_url.append(
            html_id
            or f"manifest_index_{index}"
        )

    manifest_html_ids.append(
        html_id
    )

    manifest_urls.append(
        source_url
    )


if missing_html_id:
    raise RuntimeError(
        f"Manifest has {len(missing_html_id)} missing html_id values."
    )

if duplicate_html_ids:
    raise RuntimeError(
        f"Manifest has {len(duplicate_html_ids)} duplicate html_id values."
    )

if missing_source_url:
    raise RuntimeError(
        f"Manifest has {len(missing_source_url)} missing source URLs."
    )


# ---------------------------------------------------------------------
# Preflight: real UDARE Store must still be empty
# ---------------------------------------------------------------------

refresh_udare_store_manifest_v1(
    workspace_id
)

store_before = verify_udare_store_v1(
    workspace_id
)

store_counts_before = (
    store_before.get(
        "counts"
    )
    or {}
)

metadata_before = int(
    store_counts_before.get(
        "metadata_records"
    )
    or 0
)

articles_before = int(
    store_counts_before.get(
        "article_documents"
    )
    or 0
)

if (
    metadata_before != 0
    or articles_before != 0
):
    raise RuntimeError(
        "UDARE Store is not empty before Phase 4.2: "
        f"metadata={metadata_before}, articles={articles_before}."
    )


# ---------------------------------------------------------------------
# Preflight: refuse to duplicate existing UDARE queue jobs
# ---------------------------------------------------------------------

queue_file = queue_path(
    workspace_id
)

existing_queue = read_queue(
    workspace_id,
    limit=100000,
)

existing_udare_jobs = [
    job

    for job
    in existing_queue

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

if existing_udare_jobs:
    raise RuntimeError(
        "Phase 4.2 refused to create duplicate UDARE jobs. "
        f"Existing UDARE queue jobs: {len(existing_udare_jobs)}."
    )


queue_existed_before = (
    queue_file.is_file()
)

queue_backup_path = (
    REPORT_DIR
    / "queue_before_phase_4_2.jsonl"
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

if queue_existed_before:
    shutil.copy2(
        queue_file,
        queue_backup_path,
    )

else:
    queue_backup_path.write_text(
        "",
        encoding="utf-8",
    )


batch_timestamp = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

batch_id = (
    f"udare_population_{workspace_id}_{batch_timestamp}"
)

created_jobs: List[Dict[str, Any]] = []
created_job_ids: List[str] = []


try:
    for index, entry in enumerate(
        manifest,
        start=1,
    ):
        html_id = str(
            entry[
                "html_id"
            ]
        ).strip()

        source_url = str(
            entry[
                "source_url"
            ]
        ).strip()

        identifier = str(
            entry.get(
                "identifier"
            )
            or html_id
        ).strip()

        payload = {
            "schema_version":
                "udare_population_job_payload_v1",

            "workspace_id":
                workspace_id,

            "pipeline":
                PIPELINE,

            "stage":
                STAGE,

            "source_store_version":
                SOURCE_STORE_VERSION,

            # Raw HTML Store is keyed by html_id.
            "source_record_id":
                html_id,

            "html_id":
                html_id,

            "source_url":
                source_url,

            "udare_engine":
                UDARE_ENGINE,

            "target_store":
                TARGET_STORE,

            "article_document_format":
                ARTICLE_DOCUMENT_FORMAT,

            "payload_ref":
                html_id,

            "correlation_id":
                batch_id,

            "max_attempts":
                3,

            "metadata": {
                "population_batch_id":
                    batch_id,

                "population_index":
                    index,

                "population_count":
                    EXPECTED_JOB_COUNT,

                "manifest_identifier":
                    identifier,

                "raw_html_sha256":
                    str(
                        entry.get(
                            "raw_html_sha256"
                        )
                        or ""
                    ),

                "raw_html_bytes":
                    int(
                        entry.get(
                            "raw_html_bytes"
                        )
                        or 0
                    ),

                "article_index_enabled":
                    True,

                "article_output_format":
                    ARTICLE_DOCUMENT_FORMAT,
            },

            "execution_controls": {
                "execute_now":
                    True,

                "queue_handler_required":
                    True,

                "worker_handler_required":
                    True,

                "store_population_allowed":
                    True,

                "isolated_verification":
                    False,

                "workspace_max_running":
                    5,

                "phase":
                    "phase_4_udare_store_population",
            },
        }

        job = create_universal_knowledge_job(
            workspace_id=
                workspace_id,

            user_id=
                "system",

            product_id=
                "linkcraftor",

            pipeline=
                PIPELINE,

            stage=
                STAGE,

            job_type=
                JOB_TYPE,

            payload=
                payload,

            payload_ref=
                html_id,

            priority=
                5,

            parent_job_id=
                "",

            batch_id=
                batch_id,

            enqueue=
                True,
        )

        created_jobs.append(
            job
        )

        created_job_ids.append(
            str(
                job.get(
                    "job_id"
                )
                or ""
            )
        )


except Exception:
    # Restore the queue exactly to its pre-Phase-4.2 state.
    if queue_existed_before:
        shutil.copy2(
            queue_backup_path,
            queue_file,
        )

    elif queue_file.exists():
        queue_file.unlink()

    # Remove status/progress artifacts created by this incomplete batch.
    for job_id in created_job_ids:
        if not job_id:
            continue

        status_file = job_status_path(
            workspace_id,
            job_id,
        )

        progress_file = progress_path(
            workspace_id,
            job_id,
        )

        if status_file.exists():
            status_file.unlink()

        if progress_file.exists():
            progress_file.unlink()

    raise


# ---------------------------------------------------------------------
# Verify the queue after creation
# ---------------------------------------------------------------------

queue_after = read_queue(
    workspace_id,
    limit=100000,
)

udare_jobs_after = [
    job

    for job
    in queue_after

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

queued_udare_jobs = [
    job

    for job
    in udare_jobs_after

    if str(
        job.get(
            "status"
        )
        or ""
    )
    == "queued"
]

queued_html_ids = [
    str(
        (
            job.get(
                "payload"
            )
            or {}
        ).get(
            "html_id"
        )
        or ""
    ).strip()

    for job
    in queued_udare_jobs
]

unique_job_ids = {
    str(
        job.get(
            "job_id"
        )
        or ""
    )

    for job
    in queued_udare_jobs
}

unique_queued_html_ids = set(
    queued_html_ids
)


# ---------------------------------------------------------------------
# Confirm no worker/store activity occurred
# ---------------------------------------------------------------------

refresh_udare_store_manifest_v1(
    workspace_id
)

store_after = verify_udare_store_v1(
    workspace_id
)

store_counts_after = (
    store_after.get(
        "counts"
    )
    or {}
)

metadata_after = int(
    store_counts_after.get(
        "metadata_records"
    )
    or 0
)

articles_after = int(
    store_counts_after.get(
        "article_documents"
    )
    or 0
)


checks = {
    "manifest_count_2225":
        len(
            manifest
        )
        == EXPECTED_JOB_COUNT,

    "created_job_count_2225":
        len(
            created_jobs
        )
        == EXPECTED_JOB_COUNT,

    "udare_queue_count_2225":
        len(
            udare_jobs_after
        )
        == EXPECTED_JOB_COUNT,

    "queued_udare_count_2225":
        len(
            queued_udare_jobs
        )
        == EXPECTED_JOB_COUNT,

    "unique_job_ids_2225":
        len(
            unique_job_ids
        )
        == EXPECTED_JOB_COUNT
        and ""
        not in unique_job_ids,

    "unique_html_ids_2225":
        len(
            unique_queued_html_ids
        )
        == EXPECTED_JOB_COUNT
        and ""
        not in unique_queued_html_ids,

    "queue_matches_manifest":
        unique_queued_html_ids
        == set(
            manifest_html_ids
        ),

    "all_jobs_correct_pipeline":
        all(
            job.get(
                "pipeline"
            )
            == PIPELINE

            for job
            in queued_udare_jobs
        ),

    "all_jobs_correct_stage":
        all(
            job.get(
                "stage"
            )
            == STAGE

            for job
            in queued_udare_jobs
        ),

    "all_jobs_correct_engine":
        all(
            (
                job.get(
                    "payload"
                )
                or {}
            ).get(
                "udare_engine"
            )
            == UDARE_ENGINE

            for job
            in queued_udare_jobs
        ),

    "all_jobs_store_authorized":
        all(
            (
                (
                    job.get(
                        "payload"
                    )
                    or {}
                ).get(
                    "execution_controls"
                )
                or {}
            ).get(
                "store_population_allowed"
            )
            is True

            for job
            in queued_udare_jobs
        ),

    "all_jobs_same_batch":
        all(
            job.get(
                "batch_id"
            )
            == batch_id

            for job
            in queued_udare_jobs
        ),

    "udare_store_metadata_still_zero":
        metadata_after
        == 0,

    "udare_store_articles_still_zero":
        articles_after
        == 0,
}


failed_checks = [
    name

    for name, passed
    in checks.items()

    if not passed
]


report = {
    "schema_version":
        "udare_phase_4_2_job_creation_report_v1",

    "generated_at_utc":
        utc_now(),

    "workspace_id":
        workspace_id,

    "batch_id":
        batch_id,

    "manifest_path":
        str(
            MANIFEST_PATH
        ),

    "manifest_count":
        len(
            manifest
        ),

    "queue_path":
        str(
            queue_file
        ),

    "queue_count_before":
        len(
            existing_queue
        ),

    "queue_count_after":
        len(
            queue_after
        ),

    "created_job_count":
        len(
            created_jobs
        ),

    "udare_queue_count":
        len(
            udare_jobs_after
        ),

    "queued_udare_count":
        len(
            queued_udare_jobs
        ),

    "unique_job_id_count":
        len(
            unique_job_ids
        ),

    "unique_html_id_count":
        len(
            unique_queued_html_ids
        ),

    "udare_store_before": {
        "metadata_records":
            metadata_before,

        "article_documents":
            articles_before,
    },

    "udare_store_after": {
        "metadata_records":
            metadata_after,

        "article_documents":
            articles_after,
    },

    "checks":
        checks,

    "failed_checks":
        failed_checks,

    "sample_jobs":
        queued_udare_jobs[:3],

    "worker_executed":
        False,

    "queue_runner_invoked":
        False,

    "article_reconstructed":
        False,

    "udare_store_population_performed":
        False,

    "decision":
        (
            "READY_FOR_PHASE_4_3_CONTROLLED_EXECUTION"
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
    "PHASE 4.2 — UDARE JOB CREATION VERIFICATION"
)
print("=" * 112)

print(
    "Workspace:",
    workspace_id,
)

print(
    "Batch ID:",
    batch_id,
)

print(
    "Manifest records:",
    len(
        manifest
    ),
)

print(
    "Jobs created:",
    len(
        created_jobs
    ),
)

print(
    "Queued UDARE jobs:",
    len(
        queued_udare_jobs
    ),
)

print(
    "Unique job IDs:",
    len(
        unique_job_ids
    ),
)

print(
    "Unique HTML IDs:",
    len(
        unique_queued_html_ids
    ),
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
    "UDARE Store metadata records:",
    metadata_after,
)

print(
    "UDARE Store article documents:",
    articles_after,
)

print(
    "Report:",
    REPORT_PATH,
)

print()
print("=" * 112)
print(
    "PHASE 4.2 DECISION:",
    report[
        "decision"
    ],
)
print("=" * 112)

print(
    "No queue runner was invoked."
)

print(
    "No worker was executed."
)

print(
    "No article was reconstructed."
)

print(
    "No UDARE Store population was performed."
)

raise SystemExit(
    0
    if not failed_checks
    else 1
)
