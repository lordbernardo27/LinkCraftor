from __future__ import annotations

import json
from pathlib import Path


WORKSPACE_ID = "ws_whattoexpect_com"

FAILED_JOB_IDS = {
    "ukj_aa7beedfd7a4665e9dcf8eff",
    "ukj_0f13e5bde02545581e4a470e",
}

FAILED_RAW_IDS = {
    "raw_html_5ccb5ad2ba98ba7c",
    "raw_html_917b10c1b8a37d89",
}

RAW_STORE = Path(
    "backend/server/data/raw_website_html/"
    "raw_website_html_ws_whattoexpect_com.json"
)

LEDGER = Path(
    "backend/server/data/jobs/universal_knowledge/"
    f"{WORKSPACE_ID}/"
    f"job_ledger_{WORKSPACE_ID}.jsonl"
)


def read_jsonl(path: Path) -> list[dict]:
    rows = []

    if not path.is_file():
        return rows

    for line in path.read_text(
        encoding="utf-8",
        errors="replace",
    ).splitlines():
        if not line.strip():
            continue

        try:
            value = json.loads(line)

            if isinstance(value, dict):
                rows.append(value)

        except Exception:
            pass

    return rows


if not RAW_STORE.is_file():
    raise RuntimeError(
        f"Raw HTML Store missing: {RAW_STORE}"
    )

raw_root = json.loads(
    RAW_STORE.read_text(
        encoding="utf-8",
        errors="replace",
    )
)

pages = raw_root.get("pages") or {}

if not isinstance(pages, dict):
    raise RuntimeError(
        "Raw HTML Store pages container is invalid."
    )


ledger_rows = read_jsonl(
    LEDGER
)

jobs_by_id = {}

for row in ledger_rows:
    job_id = str(
        row.get("job_id")
        or ""
    )

    if job_id not in FAILED_JOB_IDS:
        continue

    candidate = row.get("job")

    if isinstance(candidate, dict):
        jobs_by_id[job_id] = candidate
    else:
        jobs_by_id[job_id] = row


print()
print("=" * 110)
print("FAILED UDARE RAW-RECORD INSPECTION")
print("=" * 110)

print()
print("RAW STORE")
print("  Total pages:", len(pages))

for job_id in sorted(FAILED_JOB_IDS):
    job = jobs_by_id.get(job_id) or {}
    payload = job.get("payload") or {}

    requested_id = str(
        payload.get("source_record_id")
        or payload.get("html_id")
        or ""
    )

    requested_url = str(
        payload.get("source_url")
        or payload.get("url")
        or ""
    )

    exact_record = pages.get(requested_id)

    url_matches = []

    for stored_id, record in pages.items():
        if not isinstance(record, dict):
            continue

        record_url = str(
            record.get("source_url")
            or record.get("url")
            or record.get("canonical_url")
            or record.get("final_url")
            or ""
        )

        if (
            requested_url
            and record_url.rstrip("/")
            == requested_url.rstrip("/")
        ):
            url_matches.append(
                (
                    stored_id,
                    record_url,
                )
            )

    print()
    print("-" * 110)
    print("Job ID:", job_id)
    print("Requested raw ID:", requested_id)
    print("Requested URL:", requested_url)
    print("Exact ID found:", isinstance(exact_record, dict))
    print("URL match count:", len(url_matches))

    for stored_id, record_url in url_matches:
        print("  Matching stored ID:", stored_id)
        print("  Matching URL:", record_url)

print()
print("-" * 110)
print("FAILED RAW IDS DIRECT CHECK")

for raw_id in sorted(FAILED_RAW_IDS):
    print(
        f"  {raw_id}:",
        "FOUND" if raw_id in pages else "MISSING",
    )

print()
print("=" * 110)
print("INSPECTION COMPLETE")
print("=" * 110)
print("No queue or store file was modified.")
