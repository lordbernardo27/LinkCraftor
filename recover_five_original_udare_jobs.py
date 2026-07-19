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

ENGINE = (
    "universal_dom_article_reconstruction_engine_v1_8"
)

EXPECTED_MISSING_JOB_IDS = {
    "ukj_0fa2f6119280180cb6f871cb",
    "ukj_1adcff52dcef2f9fd352b569",
    "ukj_57d0ac0947ab2a4b74d6e2f3",
    "ukj_a1c932024646db9fd631f297",
    "ukj_c589a4cb4fa74f2dae5a9c85",
}

RECOVERY_SOURCE = Path(
    "backend/server/data/jobs/"
    "universal_knowledge/"
    f"{WORKSPACE_ID}/queue.jsonl"
)

REPORT_PATH = Path(
    "backend/server/data/runtime/"
    "udare_five_job_recovery/"
    "udare_five_job_recovery_report.json"
)


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []

    if not path.is_file():
        raise RuntimeError(
            f"Missing JSONL file: {path}"
        )

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
                f"Row {line_number} in {path} is not an object."
            )

        rows.append(value)

    return rows


def write_jsonl_atomic(
    path: Path,
    rows: list[dict],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = path.with_name(
        path.name + ".five_job_recovery.tmp"
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


active_queue = queue_path(
    WORKSPACE_ID
)

active_rows_before = read_queue(
    WORKSPACE_ID,
    limit=100000,
)

active_udare_before = [
    row
    for row in active_rows_before
    if str(
        row.get("job_type")
        or row.get("stage")
        or ""
    ).strip()
    == JOB_TYPE
]

if len(active_udare_before) != 2220:
    raise RuntimeError(
        "Expected 2,220 UDARE jobs before recovery, "
        f"found {len(active_udare_before)}."
    )


active_job_ids_before = {
    str(
        row.get("job_id")
        or ""
    )
    for row in active_rows_before
}

already_present = (
    EXPECTED_MISSING_JOB_IDS
    & active_job_ids_before
)

if already_present:
    raise RuntimeError(
        "One or more recovery jobs are already in the active queue: "
        + ", ".join(
            sorted(already_present)
        )
    )


source_rows = read_jsonl(
    RECOVERY_SOURCE
)

recovery_rows = [
    row
    for row in source_rows
    if str(
        row.get("job_id")
        or ""
    )
    in EXPECTED_MISSING_JOB_IDS
]


recovered_ids = {
    str(
        row.get("job_id")
        or ""
    )
    for row in recovery_rows
}

if recovered_ids != EXPECTED_MISSING_JOB_IDS:
    missing = (
        EXPECTED_MISSING_JOB_IDS
        - recovered_ids
    )

    unexpected = (
        recovered_ids
        - EXPECTED_MISSING_JOB_IDS
    )

    raise RuntimeError(
        "Recovery source mismatch. "
        f"Missing={sorted(missing)}, "
        f"unexpected={sorted(unexpected)}."
    )

if len(recovery_rows) != 5:
    raise RuntimeError(
        "Expected exactly five recovery job objects, "
        f"found {len(recovery_rows)}."
    )


for row in recovery_rows:
    row["status"] = "queued"
    row["lease_owner"] = None
    row["started_at"] = None
    row["completed_at"] = None
    row["error"] = None
    row["error_info"] = None

    payload = row.get("payload")

    if not isinstance(payload, dict):
        raise RuntimeError(
            "Recovered job has no payload object: "
            f"{row.get('job_id')}"
        )

    payload["udare_engine"] = ENGINE

    metadata = payload.get("metadata")

    if isinstance(metadata, dict):
        metadata["udare_engine"] = ENGINE


timestamp = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

active_backup = active_queue.with_name(
    active_queue.name
    + f".before_five_job_recovery_{timestamp}"
)

if active_queue.is_file():
    shutil.copy2(
        active_queue,
        active_backup,
    )


combined_rows = (
    active_rows_before
    + recovery_rows
)

write_jsonl_atomic(
    active_queue,
    combined_rows,
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

verified_queued_udare = [
    row
    for row in verified_udare
    if str(
        row.get("status")
        or ""
    ).strip()
    == "queued"
]

verified_job_ids = {
    str(
        row.get("job_id")
        or ""
    )
    for row in verified_udare
}

verified_html_ids = {
    str(
        (
            row.get("payload")
            or {}
        ).get("html_id")
        or ""
    )
    for row in verified_udare
}

recovered_verified = (
    EXPECTED_MISSING_JOB_IDS
    & verified_job_ids
)

recovered_engine_values = {
    str(
        (
            row.get("payload")
            or {}
        ).get("udare_engine")
        or ""
    )
    for row in verified_udare
    if str(
        row.get("job_id")
        or ""
    )
    in EXPECTED_MISSING_JOB_IDS
}


checks = {
    "active_udare_before_2220":
        len(active_udare_before)
        == 2220,

    "recovered_exactly_five_jobs":
        len(recovery_rows)
        == 5,

    "recovered_ids_exact_match":
        recovered_ids
        == EXPECTED_MISSING_JOB_IDS,

    "active_udare_after_2225":
        len(verified_udare)
        == 2225,

    "all_2225_udare_jobs_queued":
        len(verified_queued_udare)
        == 2225,

    "all_five_recovered_ids_present":
        recovered_verified
        == EXPECTED_MISSING_JOB_IDS,

    "unique_udare_job_ids_2225":
        len(verified_job_ids)
        == 2225
        and ""
        not in verified_job_ids,

    "unique_udare_html_ids_2225":
        len(verified_html_ids)
        == 2225
        and ""
        not in verified_html_ids,

    "recovered_jobs_use_v1_8":
        recovered_engine_values
        == {ENGINE},
}


failed = [
    name
    for name, passed in checks.items()
    if not passed
]


report = {
    "schema_version":
        "udare_five_job_recovery_report_v1",

    "generated_at_utc":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "workspace_id":
        WORKSPACE_ID,

    "active_queue":
        str(active_queue),

    "active_queue_backup":
        str(active_backup),

    "recovery_source":
        str(RECOVERY_SOURCE),

    "udare_count_before":
        len(active_udare_before),

    "recovered_job_count":
        len(recovery_rows),

    "recovered_job_ids":
        sorted(recovered_ids),

    "udare_count_after":
        len(verified_udare),

    "queued_udare_count_after":
        len(verified_queued_udare),

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
print("UDARE FIVE-JOB RECOVERY")
print("=" * 108)

print(
    "Active queue:",
    active_queue,
)

print(
    "UDARE jobs before:",
    len(active_udare_before),
)

print(
    "Original jobs recovered:",
    len(recovery_rows),
)

print(
    "UDARE jobs after:",
    len(verified_udare),
)

print(
    "Queued UDARE jobs after:",
    len(verified_queued_udare),
)

print()
print("RECOVERED JOB IDS")

for job_id in sorted(recovered_ids):
    print(
        "  -",
        job_id,
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
    print("UDARE FIVE-JOB RECOVERY: FAIL")
    print(
        "Failed checks:",
        ", ".join(failed),
    )
else:
    print("UDARE FIVE-JOB RECOVERY: PASS")

print("=" * 108)

print("No queue runner was invoked.")
print("No worker was invoked.")
print("No article was reconstructed.")
print("No UDARE Store write was performed.")

raise SystemExit(
    0 if not failed else 1
)
