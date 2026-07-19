from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

from backend.server.orchestration.universal_knowledge_orchestrator import (
    create_universal_knowledge_job,
    read_queue,
)

from backend.server.workers.universal_knowledge_queue_runner import (
    run_universal_knowledge_queue_v1,
)

from backend.server.stores.udare_store import (
    refresh_udare_store_manifest_v1,
    verify_udare_store_v1,
)

from backend.server.stores.udare_store_index_builder import (
    build_udare_store_index_v1,
)


WORKSPACE_ID = "ws_whattoexpect_com"
JOB_TYPE = "udare_reconstruction"
EXPECTED_FINAL_COUNT = 2225

REPORT_PATH = Path(
    "backend/server/data/runtime/"
    "udare_phase_4_3b_full_population/"
    "missing_udare_records.json"
)

STORE_ROOT = (
    Path("backend/server/data/udare_store")
    / WORKSPACE_ID
)

ARTICLES_DIR = STORE_ROOT / "articles"
REVIEWS_DIR = STORE_ROOT / "reviews"
METADATA_DIR = STORE_ROOT / "metadata"


def count_files(
    directory: Path,
    pattern: str,
) -> int:
    if not directory.is_dir():
        return 0

    return sum(
        1
        for path in directory.glob(pattern)
        if path.is_file()
    )


def normalize(value: Any) -> str:
    return str(value or "").strip()


if not REPORT_PATH.is_file():
    raise FileNotFoundError(
        f"Missing-record report not found: {REPORT_PATH}"
    )

report = json.loads(
    REPORT_PATH.read_text(
        encoding="utf-8",
    )
)

missing_records = report.get(
    "missing_records"
)

if not isinstance(missing_records, list):
    raise RuntimeError(
        "missing_records is not a list."
    )

if len(missing_records) != 3:
    raise RuntimeError(
        "Expected exactly three missing records, "
        f"found {len(missing_records)}."
    )


before_articles = count_files(
    ARTICLES_DIR,
    "*.html",
)

before_reviews = count_files(
    REVIEWS_DIR,
    "*.html",
)

before_metadata = count_files(
    METADATA_DIR,
    "*.json",
)


print("=" * 112)
print("UDARE THREE-MISSING-RECORD REPAIR")
print("=" * 112)

print("Articles before:", before_articles)
print("Reviews before:", before_reviews)
print("Metadata before:", before_metadata)
print()


existing_queue = read_queue(
    WORKSPACE_ID,
    limit=100000,
)


def queued_source_ids() -> set[str]:
    values: set[str] = set()

    for job in existing_queue:
        job_type = normalize(
            job.get("job_type")
            or job.get("stage")
        )

        if job_type != JOB_TYPE:
            continue

        payload = job.get("payload")

        if not isinstance(payload, dict):
            continue

        for field in (
            "raw_html_id",
            "html_id",
            "source_record_id",
        ):
            value = normalize(
                payload.get(field)
            )

            if value:
                values.add(value)

    return values


already_queued = queued_source_ids()

signature = inspect.signature(
    create_universal_knowledge_job
)

parameters = signature.parameters


def create_job_for_record(
    record: dict[str, Any],
) -> Any:
    html_id = normalize(
        record.get("html_id")
    )

    url = normalize(
        record.get("url")
    )

    if not html_id:
        raise RuntimeError(
            f"Missing html_id in record: {record}"
        )

    payload = {
        "raw_html_id": html_id,
        "html_id": html_id,
        "source_record_id": html_id,
        "source_url": url,
        "url": url,
        "workspace_id": WORKSPACE_ID,
    }

    candidate_values = {
        "workspace_id": WORKSPACE_ID,
        "job_type": JOB_TYPE,
        "pipeline": JOB_TYPE,
        "stage": JOB_TYPE,
        "payload": payload,
        "priority": 50,
        "user_id": "system",
        "product_id": "linkcraftor",
    }

    kwargs: dict[str, Any] = {}

    for name, parameter in parameters.items():
        if name in candidate_values:
            kwargs[name] = candidate_values[name]
            continue

        if parameter.default is inspect.Parameter.empty:
            raise RuntimeError(
                "Cannot safely call "
                "create_universal_knowledge_job(). "
                f"Unsupported required parameter: {name}. "
                f"Signature: {signature}"
            )

    return create_universal_knowledge_job(
        **kwargs
    )


created = 0
skipped = 0

for record in missing_records:
    if not isinstance(record, dict):
        raise RuntimeError(
            f"Invalid missing record: {record}"
        )

    html_id = normalize(
        record.get("html_id")
    )

    url = normalize(
        record.get("url")
    )

    if html_id in already_queued:
        print(
            "SKIP — already queued:",
            html_id,
            url,
        )
        skipped += 1
        continue

    result = create_job_for_record(
        record
    )

    print(
        "QUEUED:",
        html_id,
        url,
    )

    if isinstance(result, dict):
        print(
            "  Job ID:",
            result.get("job_id"),
        )

    created += 1


queue_after_creation = read_queue(
    WORKSPACE_ID,
    limit=100000,
)

udare_queue_after_creation = [
    job
    for job in queue_after_creation
    if normalize(
        job.get("job_type")
        or job.get("stage")
    )
    == JOB_TYPE
]

print()
print("Jobs created:", created)
print("Jobs skipped:", skipped)
print(
    "UDARE jobs ready:",
    len(udare_queue_after_creation),
)

if len(udare_queue_after_creation) != 3:
    raise RuntimeError(
        "Expected exactly three UDARE jobs before "
        "execution, found "
        f"{len(udare_queue_after_creation)}."
    )


print()
print("=" * 112)
print("EXECUTING THREE UDARE JOBS")
print("=" * 112)

execution = run_universal_knowledge_queue_v1(
    workspace_id=WORKSPACE_ID,
    max_jobs=3,
    job_type=JOB_TYPE,
)

print(
    json.dumps(
        execution,
        indent=2,
        ensure_ascii=False,
        default=str,
    )
)


queue_after_execution = read_queue(
    WORKSPACE_ID,
    limit=100000,
)

remaining_udare = [
    job
    for job in queue_after_execution
    if normalize(
        job.get("job_type")
        or job.get("stage")
    )
    == JOB_TYPE
]


build_udare_store_index_v1(
    WORKSPACE_ID
)

refresh_udare_store_manifest_v1(
    WORKSPACE_ID
)

store_verification = verify_udare_store_v1(
    WORKSPACE_ID
)


final_articles = count_files(
    ARTICLES_DIR,
    "*.html",
)

final_reviews = count_files(
    REVIEWS_DIR,
    "*.html",
)

final_metadata = count_files(
    METADATA_DIR,
    "*.json",
)


checks = {
    "three_jobs_created_or_already_queued":
        created + skipped == 3,

    "queue_remaining_zero":
        len(remaining_udare) == 0,

    "articles_2225":
        final_articles == EXPECTED_FINAL_COUNT,

    "reviews_2225":
        final_reviews == EXPECTED_FINAL_COUNT,

    "metadata_2225":
        final_metadata == EXPECTED_FINAL_COUNT,
}


print()
print("=" * 112)
print("FINAL THREE-RECORD REPAIR VERIFICATION")
print("=" * 112)

print(
    "Remaining UDARE jobs:",
    len(remaining_udare),
)

print(
    "Reader articles:",
    final_articles,
)

print(
    "Visual reviews:",
    final_reviews,
)

print(
    "Metadata records:",
    final_metadata,
)

print()
print("CHECKS")

for name, passed in checks.items():
    print(
        f"  {name}:",
        "PASS" if passed else "FAIL",
    )

print()
print(
    "Store verification:",
    json.dumps(
        store_verification,
        indent=2,
        ensure_ascii=False,
        default=str,
    ),
)

failed_checks = [
    name
    for name, passed in checks.items()
    if not passed
]

if failed_checks:
    print()
    print(
        "DECISION: BLOCKED —",
        ", ".join(failed_checks),
    )

    raise SystemExit(1)

print()
print(
    "DECISION: PASS — all 2,225 Raw HTML records "
    "are now populated in the UDARE Store."
)
