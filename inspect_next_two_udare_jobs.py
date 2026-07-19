from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


WORKSPACE_ID = "ws_whattoexpect_com"
DATA_ROOT = Path("backend/server/data")

candidate_files = []

for path in DATA_ROOT.rglob("*"):
    if not path.is_file():
        continue

    name = path.name.lower()

    if (
        WORKSPACE_ID.lower() in str(path).lower()
        and "queue" in name
        and path.suffix.lower() in {".json", ".jsonl"}
    ):
        candidate_files.append(path)


print()
print("=" * 112)
print("UDARE QUEUE AND JOB-TYPE INSPECTION")
print("=" * 112)
print("Workspace:", WORKSPACE_ID)
print("Candidate queue files:", len(candidate_files))


all_records = []

for path in sorted(candidate_files):
    try:
        text = path.read_text(
            encoding="utf-8-sig",
            errors="strict",
        )
    except Exception as exc:
        print()
        print("READ ERROR:", path)
        print(type(exc).__name__, str(exc))
        continue

    records = []

    try:
        if path.suffix.lower() == ".jsonl":
            for line_number, line in enumerate(
                text.splitlines(),
                start=1,
            ):
                if not line.strip():
                    continue

                item = json.loads(line)

                if isinstance(item, dict):
                    records.append(item)
        else:
            parsed = json.loads(text)

            if isinstance(parsed, list):
                records.extend(
                    item
                    for item in parsed
                    if isinstance(item, dict)
                )

            elif isinstance(parsed, dict):
                for key in (
                    "jobs",
                    "queue",
                    "records",
                    "items",
                ):
                    value = parsed.get(key)

                    if isinstance(value, list):
                        records.extend(
                            item
                            for item in value
                            if isinstance(item, dict)
                        )
                        break

                else:
                    if (
                        "job_id" in parsed
                        or "job_type" in parsed
                    ):
                        records.append(parsed)

    except Exception as exc:
        print()
        print("PARSE ERROR:", path)
        print(type(exc).__name__, str(exc))
        continue

    matching = []

    for record in records:
        workspace_id = str(
            record.get("workspace_id")
            or record.get("tenant_id")
            or ""
        )

        if workspace_id != WORKSPACE_ID:
            continue

        matching.append(record)

        all_records.append(
            {
                "_source_path": str(path),
                **record,
            }
        )

    if matching:
        print()
        print("-" * 112)
        print("FILE:", path)
        print("Workspace records:", len(matching))

        status_counts = Counter(
            str(record.get("status") or "unknown")
            for record in matching
        )

        type_counts = Counter(
            str(
                record.get("job_type")
                or record.get("type")
                or "unknown"
            )
            for record in matching
        )

        print("Status counts:", dict(status_counts))
        print("Job-type counts:", dict(type_counts))


queued = [
    record
    for record in all_records
    if str(record.get("status") or "").lower() == "queued"
]

udare_queued = [
    record
    for record in queued
    if (
        "udare" in str(
            record.get("job_type")
            or record.get("type")
            or ""
        ).lower()
        or "udare" in str(
            record.get("pipeline")
            or ""
        ).lower()
        or "udare" in str(
            record.get("stage")
            or ""
        ).lower()
        or "udare" in json.dumps(
            record.get("payload") or {},
            ensure_ascii=False,
        ).lower()
    )
]


print()
print("=" * 112)
print("QUEUED UDARE SUMMARY")
print("=" * 112)
print("All queued workspace records:", len(queued))
print("Queued UDARE records:", len(udare_queued))

job_types = Counter(
    str(
        record.get("job_type")
        or record.get("type")
        or "unknown"
    )
    for record in udare_queued
)

print("UDARE job types:", dict(job_types))


print()
print("=" * 112)
print("NEXT TWO QUEUED UDARE JOBS")
print("=" * 112)

for index, record in enumerate(
    udare_queued[:2],
    start=1,
):
    payload = record.get("payload")

    if not isinstance(payload, dict):
        payload = {}

    print()
    print(f"JOB {index}")
    print("Source queue:    ", record.get("_source_path"))
    print("job_id:         ", record.get("job_id"))
    print(
        "job_type:       ",
        record.get("job_type")
        or record.get("type"),
    )
    print("status:          ", record.get("status"))
    print("priority:        ", record.get("priority"))
    print(
        "source_record_id:",
        payload.get("source_record_id")
        or record.get("source_record_id"),
    )
    print(
        "html_id:         ",
        payload.get("html_id")
        or record.get("html_id"),
    )
    print(
        "source_url:      ",
        payload.get("source_url")
        or record.get("source_url"),
    )


print()
print("=" * 112)
print("RESULT")
print("=" * 112)

if not udare_queued:
    print("FAIL: No queued UDARE jobs were discovered.")
else:
    print("PASS: Queued UDARE jobs were discovered.")
    print(
        "No queue, job, worker, store, or backend "
        "file was modified."
    )
