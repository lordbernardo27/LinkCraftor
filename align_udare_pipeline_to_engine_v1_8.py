from __future__ import annotations

import ast
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ID = "ws_whattoexpect_com"

OLD_ENGINE = (
    "universal_dom_article_reconstruction_engine_v1_7"
)

NEW_ENGINE = (
    "universal_dom_article_reconstruction_engine_v1_8"
)

TARGET_FILES = [
    Path(
        "backend/server/workers/"
        "udare_reconstruction_worker.py"
    ),
    Path(
        "backend/server/runtime/"
        "udare_runtime_contract.py"
    ),
    Path(
        "backend/server/stores/"
        "udare_store.py"
    ),
    Path(
        "backend/server/stores/"
        "udare_article_document_builder.py"
    ),
]

QUEUE_PATH = Path(
    "backend/server/data/jobs/"
    "universal_knowledge/"
    f"{WORKSPACE_ID}/queue.jsonl"
)

QUEUE_BACKUP = Path(
    "backend/server/data/runtime/"
    "udare_phase_4_3_controlled_execution/"
    "queue_before_first_5.jsonl"
)

REPORT_PATH = Path(
    "backend/server/data/runtime/"
    "udare_engine_v1_8_alignment/"
    "udare_engine_v1_8_alignment_report.json"
)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def read_jsonl(
    path: Path,
) -> list[dict]:
    rows = []

    for line in path.read_text(
        encoding="utf-8",
        errors="replace",
    ).splitlines():
        if line.strip():
            value = json.loads(
                line
            )

            if not isinstance(
                value,
                dict,
            ):
                raise RuntimeError(
                    f"Non-object queue row in {path}."
                )

            rows.append(
                value
            )

    return rows


def write_jsonl(
    path: Path,
    rows: list[dict],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        "".join(
            json.dumps(
                row,
                ensure_ascii=False,
            )
            + "\n"

            for row in rows
        ),
        encoding="utf-8",
    )


timestamp = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

source_changes = {}


# ---------------------------------------------------------------------
# 1. Align only the targeted UDARE modules
# ---------------------------------------------------------------------

for path in TARGET_FILES:
    if not path.is_file():
        raise RuntimeError(
            f"Missing required UDARE module: {path}"
        )

    original = path.read_text(
        encoding="utf-8-sig"
    )

    occurrence_count = original.count(
        OLD_ENGINE
    )

    if occurrence_count == 0:
        source_changes[
            str(
                path
            )
        ] = {
            "old_engine_occurrences":
                0,

            "new_engine_already_present":
                NEW_ENGINE
                in original,

            "changed":
                False,
        }

        continue

    backup_path = path.with_name(
        path.name
        + f".before_udare_v1_8_alignment_{timestamp}"
    )

    shutil.copy2(
        path,
        backup_path,
    )

    updated = original.replace(
        OLD_ENGINE,
        NEW_ENGINE,
    )

    ast.parse(
        updated,
        filename=str(
            path
        ),
    )

    path.write_text(
        updated,
        encoding="utf-8",
    )

    source_changes[
        str(
            path
        )
    ] = {
        "old_engine_occurrences":
            occurrence_count,

        "backup_path":
            str(
                backup_path
            ),

        "changed":
            True,
    }


# ---------------------------------------------------------------------
# 2. Restore the queue to its exact pre-first-five state
# ---------------------------------------------------------------------

if not QUEUE_BACKUP.is_file():
    raise RuntimeError(
        "Missing Phase 4.3A queue backup: "
        f"{QUEUE_BACKUP}"
    )

queue_rows = read_jsonl(
    QUEUE_BACKUP
)

udare_rows = [
    row

    for row
    in queue_rows

    if str(
        row.get(
            "job_type"
        )
        or row.get(
            "stage"
        )
        or ""
    ).strip()
    == "udare_reconstruction"
]

if len(
    udare_rows
) != 2225:
    raise RuntimeError(
        "Expected 2,225 UDARE jobs in the queue backup, "
        f"found {len(udare_rows)}."
    )


# ---------------------------------------------------------------------
# 3. Align every queued UDARE job payload to v1.8
# ---------------------------------------------------------------------

updated_queue_jobs = 0

for row in queue_rows:
    job_type = str(
        row.get(
            "job_type"
        )
        or row.get(
            "stage"
        )
        or ""
    ).strip()

    if job_type != "udare_reconstruction":
        continue

    payload = row.get(
        "payload"
    )

    if not isinstance(
        payload,
        dict,
    ):
        raise RuntimeError(
            "UDARE queued job has no payload object: "
            f"{row.get('job_id')}"
        )

    payload[
        "udare_engine"
    ] = NEW_ENGINE

    metadata = payload.get(
        "metadata"
    )

    if isinstance(
        metadata,
        dict,
    ):
        metadata[
            "udare_engine"
        ] = NEW_ENGINE

    updated_queue_jobs += 1


if updated_queue_jobs != 2225:
    raise RuntimeError(
        "Expected to update 2,225 UDARE queue jobs, "
        f"updated {updated_queue_jobs}."
    )


current_queue_backup = QUEUE_PATH.with_name(
    QUEUE_PATH.name
    + f".before_udare_v1_8_alignment_{timestamp}"
)

if QUEUE_PATH.is_file():
    current_queue_backup.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        QUEUE_PATH,
        current_queue_backup,
    )


write_jsonl(
    QUEUE_PATH,
    queue_rows,
)


# ---------------------------------------------------------------------
# 4. Verify restored queue
# ---------------------------------------------------------------------

verified_rows = read_jsonl(
    QUEUE_PATH
)

verified_udare = [
    row

    for row
    in verified_rows

    if str(
        row.get(
            "job_type"
        )
        or row.get(
            "stage"
        )
        or ""
    ).strip()
    == "udare_reconstruction"
]

queued_udare = [
    row

    for row
    in verified_udare

    if row.get(
        "status"
    )
    == "queued"
]

engine_values = {
    str(
        (
            row.get(
                "payload"
            )
            or {}
        ).get(
            "udare_engine"
        )
        or ""
    )

    for row
    in queued_udare
}


checks = {
    "source_modules_syntax_valid":
        True,

    "queue_restored_to_2225_udare_jobs":
        len(
            verified_udare
        )
        == 2225,

    "all_2225_jobs_queued":
        len(
            queued_udare
        )
        == 2225,

    "all_queue_jobs_use_v1_8":
        engine_values
        == {
            NEW_ENGINE
        },

    "five_failed_jobs_restored":
        len(
            queued_udare
        )
        == 2225,
}


failed = [
    name

    for name, passed
    in checks.items()

    if not passed
]


report = {
    "schema_version":
        "udare_engine_v1_8_alignment_report_v1",

    "generated_at_utc":
        utc_now(),

    "workspace_id":
        WORKSPACE_ID,

    "old_engine":
        OLD_ENGINE,

    "new_engine":
        NEW_ENGINE,

    "source_changes":
        source_changes,

    "queue_backup_source":
        str(
            QUEUE_BACKUP
        ),

    "current_queue_backup":
        (
            str(
                current_queue_backup
            )
            if current_queue_backup.is_file()
            else ""
        ),

    "queue_path":
        str(
            QUEUE_PATH
        ),

    "udare_job_count":
        len(
            verified_udare
        ),

    "queued_udare_job_count":
        len(
            queued_udare
        ),

    "queue_engine_values":
        sorted(
            engine_values
        ),

    "checks":
        checks,

    "failed_checks":
        failed,

    "worker_invoked":
        False,

    "reconstruction_invoked":
        False,

    "udare_store_write":
        False,
}


REPORT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

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
print("=" * 108)
print(
    "UDARE ENGINE V1.8 ALIGNMENT"
)
print("=" * 108)

print(
    "Old engine:",
    OLD_ENGINE,
)

print(
    "New engine:",
    NEW_ENGINE,
)

print(
    "Restored UDARE jobs:",
    len(
        verified_udare
    ),
)

print(
    "Queued UDARE jobs:",
    len(
        queued_udare
    ),
)

print(
    "Queue engine values:",
    sorted(
        engine_values
    ),
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
print("=" * 108)

if failed:
    print(
        "UDARE ENGINE V1.8 ALIGNMENT: FAIL"
    )

    print(
        "Failed checks:",
        ", ".join(
            failed
        ),
    )

else:
    print(
        "UDARE ENGINE V1.8 ALIGNMENT: PASS"
    )

print("=" * 108)

print(
    "No worker or queue runner was invoked."
)

print(
    "No article was reconstructed."
)

print(
    "No UDARE Store write was performed."
)

raise SystemExit(
    0
    if not failed
    else 1
)
