from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

from backend.server.jobs.universal_knowledge_orchestrator import (
    queue_path,
    read_queue,
)


WORKSPACE_ID = "ws_whattoexpect_com"
JOB_TYPE = "udare_reconstruction"

EXPECTED_FINAL_TOTAL = 2225
EXPECTED_STORE_RECORDS = 15
EXPECTED_QUEUE_BEFORE = 2220
EXPECTED_DUPLICATES = 10
EXPECTED_QUEUE_AFTER = 2210

STORE_ROOT = Path(
    "backend/server/data/udare_store"
) / WORKSPACE_ID

METADATA_DIR = (
    STORE_ROOT
    / "metadata"
)

REPORT_PATH = Path(
    "backend/server/data/runtime/"
    "udare_phase_4_3b_queue_reconciliation/"
    "udare_queue_reconciliation_report.json"
)


def read_jsonl(
    path: Path,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    if not path.is_file():
        raise RuntimeError(
            f"Queue file does not exist: {path}"
        )

    for line_number, line in enumerate(
        path.read_text(
            encoding="utf-8",
            errors="strict",
        ).splitlines(),
        start=1,
    ):
        if not line.strip():
            continue

        value = json.loads(
            line
        )

        if not isinstance(
            value,
            dict,
        ):
            raise RuntimeError(
                f"Queue row {line_number} is not a JSON object."
            )

        rows.append(
            value
        )

    return rows


def write_jsonl_atomic(
    path: Path,
    rows: List[Dict[str, Any]],
) -> None:
    temporary = path.with_name(
        path.name
        + ".reconcile.tmp"
    )

    temporary.write_text(
        "".join(
            json.dumps(
                row,
                ensure_ascii=False,
            )
            + "\n"

            for row
            in rows
        ),
        encoding="utf-8",
    )

    temporary.replace(
        path
    )


def write_json_atomic(
    path: Path,
    value: Dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = path.with_name(
        path.name
        + ".tmp"
    )

    temporary.write_text(
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary.replace(
        path
    )


def is_udare_job(
    row: Dict[str, Any],
) -> bool:
    return str(
        row.get(
            "job_type"
        )
        or row.get(
            "stage"
        )
        or ""
    ).strip() == JOB_TYPE


def queue_html_id(
    row: Dict[str, Any],
) -> str:
    payload = (
        row.get(
            "payload"
        )
        or {}
    )

    if not isinstance(
        payload,
        dict,
    ):
        return ""

    return str(
        payload.get(
            "html_id"
        )
        or payload.get(
            "source_record_id"
        )
        or ""
    ).strip()


def queue_document_id(
    row: Dict[str, Any],
) -> str:
    payload = (
        row.get(
            "payload"
        )
        or {}
    )

    if not isinstance(
        payload,
        dict,
    ):
        return ""

    return str(
        payload.get(
            "document_id"
        )
        or payload.get(
            "source_record_id"
        )
        or payload.get(
            "html_id"
        )
        or ""
    ).strip()


active_queue_path = queue_path(
    WORKSPACE_ID
)

queue_rows_before = read_jsonl(
    active_queue_path
)

udare_rows_before = [
    row
    for row in queue_rows_before
    if is_udare_job(row)
]

if len(
    udare_rows_before
) != EXPECTED_QUEUE_BEFORE:
    raise RuntimeError(
        "Expected 2,220 UDARE jobs before reconciliation, "
        f"found {len(udare_rows_before)}."
    )


metadata_files = sorted(
    METADATA_DIR.glob(
        "*.json"
    )
)

if len(
    metadata_files
) != EXPECTED_STORE_RECORDS:
    raise RuntimeError(
        "Expected 15 UDARE metadata records, "
        f"found {len(metadata_files)}."
    )


completed_html_ids: Set[str] = set()
completed_document_ids: Set[str] = set()
completed_records: List[Dict[str, str]] = []


for metadata_path in metadata_files:
    record = json.loads(
        metadata_path.read_text(
            encoding="utf-8",
            errors="strict",
        )
    )

    if not isinstance(
        record,
        dict,
    ):
        raise RuntimeError(
            f"Metadata root is not an object: {metadata_path}"
        )

    html_id = str(
        record.get(
            "html_id"
        )
        or ""
    ).strip()

    document_id = str(
        record.get(
            "document_id"
        )
        or ""
    ).strip()

    if not html_id:
        raise RuntimeError(
            f"Metadata has no html_id: {metadata_path}"
        )

    if not document_id:
        raise RuntimeError(
            f"Metadata has no document_id: {metadata_path}"
        )

    completed_html_ids.add(
        html_id
    )

    completed_document_ids.add(
        document_id
    )

    completed_records.append({
        "html_id":
            html_id,

        "document_id":
            document_id,

        "metadata_path":
            str(
                metadata_path
            ),
    })


duplicate_rows: List[Dict[str, Any]] = []
remaining_rows: List[Dict[str, Any]] = []


for row in queue_rows_before:
    if not is_udare_job(
        row
    ):
        remaining_rows.append(
            row
        )
        continue

    html_id = queue_html_id(
        row
    )

    document_id = queue_document_id(
        row
    )

    already_completed = (
        (
            bool(
                html_id
            )
            and html_id
            in completed_html_ids
        )
        or (
            bool(
                document_id
            )
            and document_id
            in completed_document_ids
        )
    )

    if already_completed:
        duplicate_rows.append(
            row
        )
    else:
        remaining_rows.append(
            row
        )


if len(
    duplicate_rows
) != EXPECTED_DUPLICATES:
    raise RuntimeError(
        "Expected exactly 10 already-completed UDARE jobs "
        f"in the queue, found {len(duplicate_rows)}."
    )


duplicate_job_ids = {
    str(
        row.get(
            "job_id"
        )
        or ""
    ).strip()

    for row
    in duplicate_rows
}

if len(
    duplicate_job_ids
) != EXPECTED_DUPLICATES:
    raise RuntimeError(
        "The ten duplicate queue rows do not have "
        "ten unique job IDs."
    )


timestamp = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

backup_path = active_queue_path.with_name(
    active_queue_path.name
    + f".before_completed_job_reconciliation_{timestamp}"
)

shutil.copy2(
    active_queue_path,
    backup_path,
)


write_jsonl_atomic(
    active_queue_path,
    remaining_rows,
)


verified_rows = read_queue(
    WORKSPACE_ID,
    limit=100000,
)

verified_udare = [
    row
    for row in verified_rows
    if is_udare_job(row)
]

verified_html_ids = {
    queue_html_id(
        row
    )
    for row in verified_udare
}

verified_document_ids = {
    queue_document_id(
        row
    )
    for row in verified_udare
}

remaining_overlap_html = (
    completed_html_ids
    & verified_html_ids
)

remaining_overlap_document = (
    completed_document_ids
    & verified_document_ids
)


checks = {
    "store_metadata_records_15":
        len(
            metadata_files
        )
        == EXPECTED_STORE_RECORDS,

    "queue_before_2220":
        len(
            udare_rows_before
        )
        == EXPECTED_QUEUE_BEFORE,

    "completed_queue_duplicates_10":
        len(
            duplicate_rows
        )
        == EXPECTED_DUPLICATES,

    "unique_duplicate_job_ids_10":
        len(
            duplicate_job_ids
        )
        == EXPECTED_DUPLICATES,

    "queue_after_2210":
        len(
            verified_udare
        )
        == EXPECTED_QUEUE_AFTER,

    "completed_plus_queued_2225":
        (
            len(
                metadata_files
            )
            + len(
                verified_udare
            )
        )
        == EXPECTED_FINAL_TOTAL,

    "no_completed_html_ids_remain_queued":
        len(
            remaining_overlap_html
        )
        == 0,

    "no_completed_document_ids_remain_queued":
        len(
            remaining_overlap_document
        )
        == 0,
}


failed = [
    name
    for name, passed in checks.items()
    if not passed
]


report = {
    "schema_version":
        "udare_queue_reconciliation_report_v1",

    "generated_at_utc":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "workspace_id":
        WORKSPACE_ID,

    "active_queue_path":
        str(
            active_queue_path
        ),

    "queue_backup_path":
        str(
            backup_path
        ),

    "metadata_record_count":
        len(
            metadata_files
        ),

    "udare_queue_before":
        len(
            udare_rows_before
        ),

    "removed_completed_job_count":
        len(
            duplicate_rows
        ),

    "removed_completed_job_ids":
        sorted(
            duplicate_job_ids
        ),

    "removed_completed_jobs": [
        {
            "job_id":
                str(
                    row.get(
                        "job_id"
                    )
                    or ""
                ),

            "html_id":
                queue_html_id(
                    row
                ),

            "document_id":
                queue_document_id(
                    row
                ),
        }

        for row
        in duplicate_rows
    ],

    "udare_queue_after":
        len(
            verified_udare
        ),

    "completed_plus_queued":
        (
            len(
                metadata_files
            )
            + len(
                verified_udare
            )
        ),

    "checks":
        checks,

    "failed_checks":
        failed,

    "worker_invoked":
        False,

    "reconstruction_invoked":
        False,

    "store_modified":
        False,

    "queue_modified":
        True,

    "decision":
        (
            "READY_TO_RESUME_OPTIMIZED_PHASE_4_3B"
            if not failed
            else "BLOCKED"
        ),
}


write_json_atomic(
    REPORT_PATH,
    report,
)


print()
print("=" * 112)
print(
    "UDARE QUEUE / STORE RECONCILIATION"
)
print("=" * 112)

print(
    "Completed UDARE article sets:",
    len(
        metadata_files
    ),
)

print(
    "UDARE jobs before:",
    len(
        udare_rows_before
    ),
)

print(
    "Already-completed jobs removed:",
    len(
        duplicate_rows
    ),
)

print(
    "UDARE jobs after:",
    len(
        verified_udare
    ),
)

print(
    "Completed + queued:",
    (
        len(
            metadata_files
        )
        + len(
            verified_udare
        )
    ),
)

print()
print("REMOVED JOB IDS")

for job_id in sorted(
    duplicate_job_ids
):
    print(
        "  -",
        job_id,
    )

print()
print("CHECKS")

for name, passed in checks.items():
    print(
        f"  {name}:",
        "PASS"
        if passed
        else "FAIL",
    )

print()
print(
    "Report:",
    REPORT_PATH,
)

print()
print("=" * 112)
print(
    "DECISION:",
    report[
        "decision"
    ],
)
print("=" * 112)

print(
    "No worker or reconstruction was invoked."
)

print(
    "No UDARE Store artifact was changed."
)

raise SystemExit(
    0
    if not failed
    else 1
)
