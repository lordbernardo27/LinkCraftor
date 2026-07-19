from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path("backend/server/data")

FAILED_JOB_IDS = {
    "ukj_aa7beedfd7a4665e9dcf8eff",
    "ukj_0f13e5bde02545581e4a470e",
}

ALLOWED_SUFFIXES = {
    ".json",
    ".jsonl",
    ".txt",
    ".log",
}


def contains_job_id(
    value: Any,
    job_id: str,
) -> bool:
    if isinstance(value, dict):
        return any(
            contains_job_id(key, job_id)
            or contains_job_id(item, job_id)
            for key, item in value.items()
        )

    if isinstance(value, list):
        return any(
            contains_job_id(item, job_id)
            for item in value
        )

    return job_id in str(value)


def print_json_matches(
    *,
    path: Path,
    value: Any,
    job_id: str,
) -> int:
    count = 0

    if isinstance(value, dict):
        if contains_job_id(value, job_id):
            print()
            print("-" * 112)
            print("FILE:", path)
            print("JOB ID:", job_id)
            print("MATCHING JSON OBJECT")
            print("-" * 112)
            print(
                json.dumps(
                    value,
                    indent=2,
                    ensure_ascii=False,
                )
            )
            count += 1

    elif isinstance(value, list):
        for index, item in enumerate(value):
            if contains_job_id(item, job_id):
                print()
                print("-" * 112)
                print("FILE:", path)
                print("JOB ID:", job_id)
                print("LIST INDEX:", index)
                print("MATCHING JSON ITEM")
                print("-" * 112)
                print(
                    json.dumps(
                        item,
                        indent=2,
                        ensure_ascii=False,
                    )
                )
                count += 1

    return count


if not ROOT.is_dir():
    raise RuntimeError(
        f"Data directory is missing: {ROOT}"
    )


print()
print("=" * 112)
print("UDARE FAILED-JOB RECORD INSPECTION")
print("=" * 112)

total_matches = 0
files_scanned = 0

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue

    if path.suffix.casefold() not in ALLOWED_SUFFIXES:
        continue

    try:
        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except Exception:
        continue

    if not any(
        job_id in text
        for job_id in FAILED_JOB_IDS
    ):
        continue

    files_scanned += 1

    if path.suffix.casefold() == ".jsonl":
        for line_number, line in enumerate(
            text.splitlines(),
            start=1,
        ):
            if not any(
                job_id in line
                for job_id in FAILED_JOB_IDS
            ):
                continue

            try:
                value = json.loads(line)
            except Exception:
                print()
                print("-" * 112)
                print("FILE:", path)
                print("LINE:", line_number)
                print("RAW MATCH")
                print("-" * 112)
                print(line)
                total_matches += 1
                continue

            for job_id in FAILED_JOB_IDS:
                if contains_job_id(value, job_id):
                    print()
                    print("-" * 112)
                    print("FILE:", path)
                    print("LINE:", line_number)
                    print("JOB ID:", job_id)
                    print("MATCHING JSONL RECORD")
                    print("-" * 112)
                    print(
                        json.dumps(
                            value,
                            indent=2,
                            ensure_ascii=False,
                        )
                    )
                    total_matches += 1

        continue

    if path.suffix.casefold() == ".json":
        try:
            value = json.loads(text)
        except Exception:
            value = None

        if value is not None:
            for job_id in FAILED_JOB_IDS:
                total_matches += print_json_matches(
                    path=path,
                    value=value,
                    job_id=job_id,
                )
            continue

    lines = text.splitlines()

    for job_id in FAILED_JOB_IDS:
        matching_lines = [
            index
            for index, line in enumerate(
                lines,
                start=1,
            )
            if job_id in line
        ]

        for line_number in matching_lines:
            start = max(
                1,
                line_number - 8,
            )
            end = min(
                len(lines),
                line_number + 8,
            )

            print()
            print("-" * 112)
            print("FILE:", path)
            print("JOB ID:", job_id)
            print(
                "LINES:",
                f"{start}-{end}",
            )
            print("-" * 112)

            for current in range(
                start,
                end + 1,
            ):
                marker = (
                    ">>>"
                    if current == line_number
                    else "   "
                )

                print(
                    f"{marker} {current:6}: "
                    f"{lines[current - 1]}"
                )

            total_matches += 1


print()
print("=" * 112)
print("INSPECTION SUMMARY")
print("=" * 112)
print("Matching files scanned:", files_scanned)
print("Matching records printed:", total_matches)

if total_matches == 0:
    print(
        "No persisted failure records were found "
        "for the two job IDs."
    )

print()
print("No queue, job, worker, or store file was modified.")
