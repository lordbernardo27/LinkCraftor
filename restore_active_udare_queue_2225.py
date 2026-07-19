from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from backend.server.jobs.universal_knowledge_orchestrator import (
    queue_path,
    read_queue,
)


WORKSPACE_ID = "ws_whattoexpect_com"
JOB_TYPE = "udare_reconstruction"

ENGINE_V1_8 = (
    "universal_dom_article_reconstruction_engine_v1_8"
)

BACKUP_PATH = Path(
    "backend/server/data/runtime/"
    "udare_phase_4_3_controlled_execution/"
    "queue_before_first_5.jsonl"
)

REPORT_PATH = Path(
    "backend/server/data/runtime/"
    "udare_active_queue_restore/"
    "udare_active_queue_restore_report.json"
)


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []

    for line_number, line in enumerate(
        path.read_text(
            encoding="utf-8",
            errors="replace",
        ).splitlines(),
        start=1,
    ):
        if not line.strip():
            continue

        value = json.loads(line)

        if not isinstance(value, dict):
            raise RuntimeError(
                f"Queue row {line_number} is not a JSON object."
            )

        rows.append(value)

    return rows


def write_jsonl(
    path: Path,
    rows: list[dict],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = path.with_name(
        path.name + ".restore.tmp"
    )

    temporary.write_text(
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

    temporary.replace(path)


if not BACKUP_PATH.is_file():
    raise RuntimeError(
        f"Missing pre-first-five queue backup: {BACKUP_PATH}"
    )


active_queue_path = queue_path(
    WORKSPACE_ID
)

timestamp = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

active_queue_backup = active_queue_path.with_name(
    active_queue_path.name
    + f".before_correct_restore_{timestamp}"
)

if active_queue_path.is_file():
    shutil.copy2(
        active_queue_path,
        active_queue_backup,
    )


backup_rows = read_jsonl(
    BACKUP_PATH
)

backup_udare_jobs = [
    row
    for row in backup_rows
    if str(
        row.get("job_type")
        or row.get("stage")
        or ""
    ).strip()
    == JOB_TYPE
]

if len(backup_udare_jobs) != 2225:
    raise RuntimeError(
        "The pre-first-five backup does not contain exactly "
        f"2,225 UDARE jobs. Found {len(backup_udare_jobs)}."
    )


updated_jobs = 0

for row in backup_rows:
    job_type = str(
        row.get("job_type")
        or row.get("stage")
        or ""
    ).strip()

    if job_type != JOB_TYPE:
        continue

    row["status"] = "queued"
    row["lease_owner"] = None
    row["started_at"] = None
    row["completed_at"] = None
    row["error"] = None
    row["error_info"] = None

    payload = row.get("payload")

    if not isinstance(payload, dict):
        raise RuntimeError(
            f"UDARE job has no payload object: {row.get('job_id')}"
        )

    payload["udare_engine"] = ENGINE_V1_8

    metadata = payload.get("metadata")

    if isinstance(metadata, dict):
        metadata["udare_engine"] = ENGINE_V1_8

    updated_jobs += 1


if updated_jobs != 2225:
    raise RuntimeError(
        f"Expected to update 2,225 jobs, updated {updated_jobs}."
    )


write_jsonl(
    active_queue_path,
    backup_rows,
)


verified_rows = read_queue(
    WORKSPACE_ID,
    limit=100000,
)

verified_udare = [
    row
    for row in verified_rows
    if str(
        row.get("job_type")
        or row.get("stage")
        or ""
    ).strip()
    == JOB_TYPE
]

verified_queued = [
    row
    for row in verified_udare
    if str(
        row.get("status")
        or ""
    ).strip()
    == "queued"
]

engine_values = {
    str(
        (
            row.get("payload")
            or {}
        ).get("udare_engine")
        or ""
    )
    for row in verified_queued
}

unique_job_ids = {
    str(
        row.get("job_id")
        or ""
    )
    for row in verified_queued
}

unique_html_ids = {
    str(
        (
            row.get("payload")
            or {}
        ).get("html_id")
        or ""
    )
    for row in verified_queued
}


checks = {
    "active_queue_is_queue_path":
        active_queue_path
        == queue_path(WORKSPACE_ID),

    "restored_udare_jobs_2225":
        len(verified_udare)
        == 2225,

    "queued_udare_jobs_2225":
        len(verified_queued)
        == 2225,

    "unique_job_ids_2225":
        len(unique_job_ids)
        == 2225
        and ""
        not in unique_job_ids,

    "unique_html_ids_2225":
        len(unique_html_ids)
        == 2225
        and ""
        not in unique_html_ids,

    "all_jobs_use_v1_8":
        engine_values
        == {ENGINE_V1_8},
}


failed = [
    name
    for name, passed in checks.items()
    if not passed
]


report = {
    "schema_version":
        "udare_active_queue_restore_report_v1",

    "workspace_id":
        WORKSPACE_ID,

    "active_queue_path":
        str(active_queue_path),

    "source_backup_path":
        str(BACKUP_PATH),

    "active_queue_backup_path":
        str(active_queue_backup),

    "total_queue_rows":
        len(verified_rows),

    "udare_job_count":
        len(verified_udare),

    "queued_udare_job_count":
        len(verified_queued),

    "engine_values":
        sorted(engine_values),

    "checks":
        checks,

    "failed_checks":
        failed,

    "queue_runner_invoked":
        False,

    "worker_invoked":
        False,

    "article_reconstructed":
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
print("ACTIVE UDARE QUEUE RESTORE")
print("=" * 108)

print(
    "Active queue:",
    active_queue_path,
)

print(
    "Total queue rows:",
    len(verified_rows),
)

print(
    "UDARE jobs:",
    len(verified_udare),
)

print(
    "Queued UDARE jobs:",
    len(verified_queued),
)

print(
    "Engine values:",
    sorted(engine_values),
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
    "Report:",
    REPORT_PATH,
)

print()
print("=" * 108)

if failed:
    print("ACTIVE UDARE QUEUE RESTORE: FAIL")
    print(
        "Failed checks:",
        ", ".join(failed),
    )
else:
    print("ACTIVE UDARE QUEUE RESTORE: PASS")

print("=" * 108)

print("No queue runner was invoked.")
print("No worker was invoked.")
print("No article was reconstructed.")
print("No UDARE Store write was performed.")

raise SystemExit(
    0 if not failed else 1
)
