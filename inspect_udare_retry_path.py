from __future__ import annotations

from pathlib import Path


ROOT = Path("backend/server")

TERMS = (
    "retry_job",
    "retry_failed",
    "requeue",
    "failure_registry",
    "dead_letter",
    "run_universal_knowledge_queue_v1",
)

print()
print("=" * 112)
print("UDARE FAILED-JOB RETRY PATH INSPECTION")
print("=" * 112)

matches = 0

for path in ROOT.rglob("*.py"):
    try:
        lines = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        ).splitlines()
    except Exception:
        continue

    matching = [
        number
        for number, line in enumerate(lines, start=1)
        if any(term in line for term in TERMS)
    ]

    if not matching:
        continue

    if not any(
        "udare" in line.lower()
        or "universal_knowledge" in line.lower()
        or "failure" in line.lower()
        or "retry" in line.lower()
        for line in lines
    ):
        continue

    matches += 1

    print()
    print("-" * 112)
    print("FILE:", path)
    print("-" * 112)

    shown = []

    for line_number in matching:
        start = max(1, line_number - 8)
        end = min(len(lines), line_number + 14)

        if any(
            start >= old_start and end <= old_end
            for old_start, old_end in shown
        ):
            continue

        shown.append((start, end))

        for current in range(start, end + 1):
            marker = ">>>" if current in matching else "   "
            print(
                f"{marker} {current:5}: "
                f"{lines[current - 1]}"
            )

        print()

print("=" * 112)
print("SUMMARY")
print("=" * 112)
print("Relevant files found:", matches)
print()
print("No runtime, queue, job, or store file was modified.")
