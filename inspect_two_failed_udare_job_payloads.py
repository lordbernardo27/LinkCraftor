from __future__ import annotations

import json
from pathlib import Path

from backend.server.workers.udare_reconstruction_worker import (
    _default_raw_record_loader_v1,
)


WORKSPACE_ID = "ws_whattoexpect_com"

FAILED_JOB_IDS = {
    "ukj_aa7beedfd7a4665e9dcf8eff",
    "ukj_0f13e5bde02545581e4a470e",
}

LEDGER_PATH = Path(
    "backend/server/data/jobs/"
    "universal_knowledge/"
    f"{WORKSPACE_ID}/"
    f"job_ledger_{WORKSPACE_ID}.jsonl"
)


def read_jsonl(
    path: Path,
) -> list[dict]:
    rows = []

    for line in path.read_text(
        encoding="utf-8",
        errors="replace",
    ).splitlines():
        if not line.strip():
            continue

        try:
            value = json.loads(
                line
            )

            if isinstance(
                value,
                dict,
            ):
                rows.append(
                    value
                )

        except Exception:
            pass

    return rows


if not LEDGER_PATH.is_file():
    raise RuntimeError(
        f"Missing job ledger: {LEDGER_PATH}"
    )


ledger_rows = read_jsonl(
    LEDGER_PATH
)

jobs = {}

for row in ledger_rows:
    job_id = str(
        row.get(
            "job_id"
        )
        or ""
    ).strip()

    if job_id not in FAILED_JOB_IDS:
        continue

    candidate = row.get(
        "job"
    )

    if isinstance(
        candidate,
        dict,
    ):
        job = candidate
    else:
        job = row

    payload = job.get(
        "payload"
    )

    if isinstance(
        payload,
        dict,
    ):
        jobs[
            job_id
        ] = job


print()
print("=" * 112)
print("FAILED UDARE JOB PAYLOAD AND LOADER TEST")
print("=" * 112)

for job_id in sorted(
    FAILED_JOB_IDS
):
    job = jobs.get(
        job_id
    )

    print()
    print("-" * 112)
    print("JOB ID:", job_id)

    if not job:
        print("Job not found in ledger.")
        continue

    payload = job.get(
        "payload"
    ) or {}

    html_id = str(
        payload.get(
            "html_id"
        )
        or ""
    )

    source_record_id = str(
        payload.get(
            "source_record_id"
        )
        or ""
    )

    source_url = str(
        payload.get(
            "source_url"
        )
        or payload.get(
            "url"
        )
        or ""
    )

    print()
    print("FULL PAYLOAD")
    print(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
    )

    print()
    print("EXTRACTED VALUES")
    print("  html_id:", repr(html_id))
    print("  source_record_id:", repr(source_record_id))
    print("  source_url:", repr(source_url))
    print("  html_id length:", len(html_id))
    print(
        "  source_record_id length:",
        len(source_record_id),
    )

    direct_html_id_result = (
        _default_raw_record_loader_v1(
            workspace_id=
                WORKSPACE_ID,

            html_id=
                html_id,
        )
        if html_id
        else None
    )

    direct_source_id_result = (
        _default_raw_record_loader_v1(
            workspace_id=
                WORKSPACE_ID,

            html_id=
                source_record_id,
        )
        if source_record_id
        else None
    )

    print()
    print("DIRECT LOADER RESULTS")
    print(
        "  using html_id:",
        "FOUND"
        if isinstance(
            direct_html_id_result,
            dict,
        )
        else "NOT FOUND",
    )

    print(
        "  using source_record_id:",
        "FOUND"
        if isinstance(
            direct_source_id_result,
            dict,
        )
        else "NOT FOUND",
    )

    if isinstance(
        direct_html_id_result,
        dict,
    ):
        print(
            "  returned URL:",
            direct_html_id_result.get(
                "source_url"
            )
            or direct_html_id_result.get(
                "url"
            ),
        )

print()
print("=" * 112)
print("INSPECTION COMPLETE")
print("=" * 112)
print("No queue, worker, job, or store file was modified.")
