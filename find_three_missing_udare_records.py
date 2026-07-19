from __future__ import annotations

import json
from pathlib import Path
from typing import Any


WORKSPACE_ID = "ws_whattoexpect_com"

RAW_STORE_PATH = Path(
    "backend/server/data/raw_website_html"
) / f"raw_website_html_{WORKSPACE_ID}.json"

METADATA_DIR = (
    Path("backend/server/data/udare_store")
    / WORKSPACE_ID
    / "metadata"
)


def normalize(value: Any) -> str:
    return str(value or "").strip()


def candidate_ids(record: dict[str, Any]) -> set[str]:
    values: set[str] = set()

    fields = (
        "html_id",
        "raw_html_id",
        "source_record_id",
        "record_id",
        "page_id",
        "content_id",
        "id",
        "url",
        "canonical_url",
        "source_url",
    )

    for field in fields:
        value = normalize(record.get(field))

        if value:
            values.add(value)

    source = record.get("source")

    if isinstance(source, dict):
        for field in fields:
            value = normalize(source.get(field))

            if value:
                values.add(value)

    payload = record.get("payload")

    if isinstance(payload, dict):
        for field in fields:
            value = normalize(payload.get(field))

            if value:
                values.add(value)

    return values


if not RAW_STORE_PATH.is_file():
    raise FileNotFoundError(
        f"Raw HTML store missing: {RAW_STORE_PATH}"
    )

raw_root = json.loads(
    RAW_STORE_PATH.read_text(
        encoding="utf-8",
    )
)

pages = raw_root.get("pages")

if isinstance(pages, dict):
    raw_records = []

    for key, value in pages.items():
        if not isinstance(value, dict):
            continue

        record = dict(value)
        record.setdefault("html_id", key)
        raw_records.append(record)

elif isinstance(pages, list):
    raw_records = [
        record
        for record in pages
        if isinstance(record, dict)
    ]

else:
    raise RuntimeError(
        "Raw HTML store does not contain pages as a dict or list."
    )


completed_identifiers: set[str] = set()
metadata_files = sorted(
    METADATA_DIR.glob("*.json")
)

for path in metadata_files:
    try:
        metadata = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )
    except Exception as exc:
        raise RuntimeError(
            f"Could not read metadata file {path}: {exc}"
        ) from exc

    if isinstance(metadata, dict):
        completed_identifiers.update(
            candidate_ids(metadata)
        )


missing: list[dict[str, Any]] = []

for record in raw_records:
    identifiers = candidate_ids(record)

    if identifiers and not (
        identifiers & completed_identifiers
    ):
        missing.append(
            {
                "html_id": normalize(
                    record.get("html_id")
                    or record.get("raw_html_id")
                    or record.get("source_record_id")
                    or record.get("record_id")
                    or record.get("id")
                ),
                "url": normalize(
                    record.get("url")
                    or record.get("canonical_url")
                    or record.get("source_url")
                ),
                "title": normalize(
                    record.get("title")
                ),
                "all_identifiers": sorted(
                    identifiers
                ),
            }
        )


print("=" * 112)
print("UDARE MISSING RAW HTML RECORDS")
print("=" * 112)

print("Raw HTML records:", len(raw_records))
print("UDARE metadata records:", len(metadata_files))
print("Missing records:", len(missing))
print()

for number, record in enumerate(
    missing,
    start=1,
):
    print("-" * 112)
    print("Missing number:", number)
    print("HTML ID:", record["html_id"])
    print("URL:", record["url"])
    print("Title:", record["title"])
    print(
        "Identifiers:",
        json.dumps(
            record["all_identifiers"],
            ensure_ascii=False,
        ),
    )

report_path = Path(
    "backend/server/data/runtime/"
    "udare_phase_4_3b_full_population/"
    "missing_udare_records.json"
)

report_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)

report_path.write_text(
    json.dumps(
        {
            "workspace_id": WORKSPACE_ID,
            "raw_html_count": len(raw_records),
            "udare_metadata_count": len(metadata_files),
            "missing_count": len(missing),
            "missing_records": missing,
        },
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
    encoding="utf-8",
)

print()
print("Report:", report_path)

if len(missing) == 3:
    print(
        "DECISION: PASS — exactly three missing "
        "Raw HTML records identified."
    )
else:
    print(
        "DECISION: REVIEW — expected exactly three "
        f"missing records, found {len(missing)}."
    )
