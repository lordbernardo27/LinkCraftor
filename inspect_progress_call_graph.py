from __future__ import annotations

from pathlib import Path

BACKEND = Path("backend/server")
TARGET = "update_job_progress("

print()
print("=" * 112)
print("UPDATE_JOB_PROGRESS CALL GRAPH")
print("=" * 112)

matches = []

for py in sorted(BACKEND.rglob("*.py")):

    try:
        lines = py.read_text(
            encoding="utf-8-sig",
            errors="replace",
        ).splitlines()
    except Exception:
        continue

    for i, line in enumerate(lines, start=1):

        if TARGET not in line:
            continue

        # Ignore the function definition itself
        if line.lstrip().startswith("def update_job_progress"):
            continue

        matches.append((py, i, lines))

print("Call sites found:", len(matches))

for path, line_no, lines in matches:

    print()
    print("=" * 112)
    print("FILE:", path)
    print("LINE:", line_no)
    print("=" * 112)

    start = max(1, line_no - 12)
    end = min(len(lines), line_no + 20)

    for n in range(start, end + 1):

        marker = ">>> " if n == line_no else "    "

        print(
            f"{marker}{n:5}: {lines[n-1]}"
        )

print()
print("=" * 112)
print("UDARE WORKER PROGRESS CALLS")
print("=" * 112)

keywords = (
    "runner_dequeued",
    "load_raw_html",
    "reconstruct_article",
    "build_article_document",
    "runner_finished",
)

for py in sorted(BACKEND.rglob("*.py")):

    try:
        lines = py.read_text(
            encoding="utf-8-sig",
            errors="replace",
        ).splitlines()
    except Exception:
        continue

    hits = []

    for i, line in enumerate(lines, start=1):

        if any(k in line for k in keywords):
            hits.append(i)

    if not hits:
        continue

    print()
    print("=" * 112)
    print("FILE:", py)
    print("=" * 112)

    for hit in hits:

        start = max(1, hit - 8)
        end = min(len(lines), hit + 12)

        for n in range(start, end + 1):

            marker = ">>> " if n == hit else "    "

            print(
                f"{marker}{n:5}: {lines[n-1]}"
            )

print()
print("=" * 112)
print("SEARCH FOR JOB STATUS UPDATES")
print("=" * 112)

TARGET2 = "update_job_status("

for py in sorted(BACKEND.rglob("*.py")):

    try:
        lines = py.read_text(
            encoding="utf-8-sig",
            errors="replace",
        ).splitlines()
    except Exception:
        continue

    for i, line in enumerate(lines, start=1):

        if TARGET2 not in line:
            continue

        if line.lstrip().startswith("def update_job_status"):
            continue

        print()
        print("=" * 112)
        print("FILE:", py)
        print("LINE:", i)
        print("=" * 112)

        start = max(1, i - 10)
        end = min(len(lines), i + 18)

        for n in range(start, end + 1):

            marker = ">>> " if n == i else "    "

            print(
                f"{marker}{n:5}: {lines[n-1]}"
            )

print()
print("=" * 112)
print("SUMMARY")
print("=" * 112)
print("Inspection complete.")
print("No files were modified.")
