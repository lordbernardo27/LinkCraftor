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

OLD_ENGINE = (
    "universal_dom_article_reconstruction_engine_v1_7"
)

NEW_ENGINE = (
    "universal_dom_article_reconstruction_engine_v1_8"
)

MISSING_JOB_IDS = {
    "ukj_8581233ede4fe657d1e36678",
    "ukj_e487bcd8f2100edc0e6fea47",
    "ukj_34ad2c74392e9cc153e1508d",
    "ukj_4fd993ba110bc1028ef61cfc",
    "ukj_b6a53797bc608fd3f9a6f930",
}

LEDGER_PATH = Path(
    "backend/server/data/jobs/"
    "universal_knowledge/"
    f"{WORKSPACE_ID}/"
    f"job_ledger_{WORKSPACE_ID}.jsonl"
)

REPORT_PATH = Path(
    "backend/server/data/runtime/"
    "udare_active_queue_v1_8_repair/"
    "udare_active_queue_v1_8_repair_report.json"
)


def read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        raise RuntimeError(
            f"Missing JSONL file: {path}"
        )

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
                f"Row {line_number} in {path} is not a JSON object."
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
        path.name + ".v1_8_repair.tmp"
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

    temporary.replace(
        path
    )


def is_udare_job(
    row: dict,
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


def align_job_to_v1_8(
    row: dict,
) -> None:
    row["status"] = "queued"
    row["lease_owner"] = None
    row["started_at"] = None
    row["completed_at"] = None
    row["error"] = None
    row["error_info"] = None

    payload = row.get(
        "payload"
    )

    if not isinstance(
        payload,
        dict,
    ):
        raise RuntimeError(
            "UDARE job has no payload object: "
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


active_queue_path = queue_path(
    WORKSPACE_ID
)

active_rows = read_queue(
    WORKSPACE_ID,
    limit=100000,
)

active_udare_before = [
    row

    for row
    in active_rows

    if is_udare_job(
        row
    )
]

if len(
    active_udare_before
) != 2220:
    raise RuntimeError(
        "Expected 2,220 active UDARE jobs before repair, "
        f"found {len(active_udare_before)}."
    )


active_ids_before = {
    str(
        row.get(
            "job_id"
        )
        or ""
    )

    for row
    in active_rows
}

already_present = (
    MISSING_JOB_IDS
    & active_ids_before
)

if already_present:
    raise RuntimeError(
        "One or more missing jobs are already present: "
        + ", ".join(
            sorted(
                already_present
            )
        )
    )


# ------------------------------------------------------------------
# Align every existing active UDARE job to v1.8.
# ------------------------------------------------------------------

aligned_existing_count = 0

for row in active_rows:
    if not is_udare_job(
        row
    ):
        continue

    align_job_to_v1_8(
        row
    )

    aligned_existing_count += 1


if aligned_existing_count != 2220:
    raise RuntimeError(
        "Expected to align 2,220 active jobs, "
        f"aligned {aligned_existing_count}."
    )


# ------------------------------------------------------------------
# Recover the latest five removed jobs from the canonical ledger.
# The ledger may contain multiple lifecycle entries per job, so retain
# the most recent complete record for each requested job ID.
# ------------------------------------------------------------------

ledger_rows = read_jsonl(
    LEDGER_PATH
)

latest_by_job_id: dict[str, dict] = {}

for row in ledger_rows:
    job_id = str(
        row.get(
            "job_id"
        )
        or ""
    ).strip()

    if job_id not in MISSING_JOB_IDS:
        continue

    candidate = row.get(
        "job"
    )

    if isinstance(
        candidate,
        dict,
    ):
        job_record = dict(
            candidate
        )

    else:
        job_record = dict(
            row
        )

    if not isinstance(
        job_record.get(
            "payload"
        ),
        dict,
    ):
        continue

    latest_by_job_id[
        job_id
    ] = job_record


recovered_ids = set(
    latest_by_job_id
)

if recovered_ids != MISSING_JOB_IDS:
    raise RuntimeError(
        "Could not recover every missing job from the ledger. "
        f"Missing: {sorted(MISSING_JOB_IDS - recovered_ids)}"
    )


recovery_rows = [
    latest_by_job_id[
        job_id
    ]

    for job_id
    in sorted(
        MISSING_JOB_IDS
    )
]


for row in recovery_rows:
    align_job_to_v1_8(
        row
    )


# ------------------------------------------------------------------
# Back up and write the corrected active queue.
# ------------------------------------------------------------------

timestamp = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

active_backup = active_queue_path.with_name(
    active_queue_path.name
    + f".before_full_v1_8_repair_{timestamp}"
)

if active_queue_path.is_file():
    shutil.copy2(
        active_queue_path,
        active_backup,
    )


combined_rows = (
    active_rows
    + recovery_rows
)

write_jsonl_atomic(
    active_queue_path,
    combined_rows,
)


# ------------------------------------------------------------------
# Verify through the canonical queue interfaces.
# ------------------------------------------------------------------

verified_rows = read_queue(
    WORKSPACE_ID,
    limit=100000,
)

verified_udare = [
    row

    for row
    in verified_rows

    if is_udare_job(
        row
    )
]

verified_queued_udare = [
    row

    for row
    in verified_udare

    if str(
        row.get(
            "status"
        )
        or ""
    ).strip()
    == "queued"
]

verified_job_ids = {
    str(
        row.get(
            "job_id"
        )
        or ""
    )

    for row
    in verified_udare
}

verified_html_ids = {
    str(
        (
            row.get(
                "payload"
            )
            or {}
        ).get(
            "html_id"
        )
        or ""
    )

    for row
    in verified_udare
}

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
    in verified_udare
}

old_engine_count_after = sum(
    1

    for row
    in verified_udare

    if str(
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
    == OLD_ENGINE
)


checks = {
    "active_udare_before_2220":
        len(
            active_udare_before
        )
        == 2220,

    "aligned_existing_jobs_2220":
        aligned_existing_count
        == 2220,

    "recovered_latest_five_jobs":
        len(
            recovery_rows
        )
        == 5,

    "recovered_ids_exact_match":
        recovered_ids
        == MISSING_JOB_IDS,

    "active_udare_after_2225":
        len(
            verified_udare
        )
        == 2225,

    "all_2225_jobs_queued":
        len(
            verified_queued_udare
        )
        == 2225,

    "unique_job_ids_2225":
        len(
            verified_job_ids
        )
        == 2225
        and ""
        not in verified_job_ids,

    "unique_html_ids_2225":
        len(
            verified_html_ids
        )
        == 2225
        and ""
        not in verified_html_ids,

    "all_jobs_use_only_v1_8":
        engine_values
        == {
            NEW_ENGINE
        },

    "no_v1_7_jobs_remain":
        old_engine_count_after
        == 0,

    "all_five_missing_jobs_restored":
        MISSING_JOB_IDS.issubset(
            verified_job_ids
        ),
}


failed = [
    name

    for name, passed
    in checks.items()

    if not passed
]


report = {
    "schema_version":
        "udare_active_queue_v1_8_repair_report_v1",

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

    "active_queue_backup":
        str(
            active_backup
        ),

    "ledger_path":
        str(
            LEDGER_PATH
        ),

    "old_engine":
        OLD_ENGINE,

    "new_engine":
        NEW_ENGINE,

    "active_udare_before":
        len(
            active_udare_before
        ),

    "aligned_existing_count":
        aligned_existing_count,

    "recovered_job_ids":
        sorted(
            recovered_ids
        ),

    "active_udare_after":
        len(
            verified_udare
        ),

    "queued_udare_after":
        len(
            verified_queued_udare
        ),

    "engine_values_after":
        sorted(
            engine_values
        ),

    "old_engine_count_after":
        old_engine_count_after,

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
print("=" * 112)
print(
    "ACTIVE UDARE QUEUE V1.8 REPAIR"
)
print("=" * 112)

print(
    "Active queue:",
    active_queue_path,
)

print(
    "UDARE jobs before:",
    len(
        active_udare_before
    ),
)

print(
    "Existing jobs aligned:",
    aligned_existing_count,
)

print(
    "Missing jobs recovered:",
    len(
        recovery_rows
    ),
)

print(
    "UDARE jobs after:",
    len(
        verified_udare
    ),
)

print(
    "Queued UDARE jobs after:",
    len(
        verified_queued_udare
    ),
)

print(
    "Engine values after:",
    sorted(
        engine_values
    ),
)

print(
    "Remaining v1.7 jobs:",
    old_engine_count_after,
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

if failed:
    print(
        "ACTIVE UDARE QUEUE V1.8 REPAIR: FAIL"
    )

    print(
        "Failed checks:",
        ", ".join(
            failed
        ),
    )

else:
    print(
        "ACTIVE UDARE QUEUE V1.8 REPAIR: PASS"
    )

print("=" * 112)

print(
    "No queue runner or worker was invoked."
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
