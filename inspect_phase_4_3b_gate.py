from pathlib import Path
import re

FILES = [
    Path("run_udare_phase_4_3b_full_population.py"),
    Path("backend/server/jobs/udare_phase_4_3b.py"),
    Path("backend/server/jobs/udare_phase_4_3b_runner.py"),
    Path("backend/server/jobs/udare_phase_4_3b_full_population.py"),
]

PATTERNS = [
    "completed_plus_queued_equals_2225",
    "2225",
    "completed",
    "queued",
    "gate",
]

found = False

for file in FILES:
    if not file.exists():
        continue

    text = file.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    for i, line in enumerate(lines):
        if any(p in line for p in PATTERNS):
            found = True
            print("=" * 120)
            print(file)
            print(f"Line {i+1}")
            print("=" * 120)

            start = max(0, i - 20)
            end = min(len(lines), i + 21)

            for n in range(start, end):
                print(f"{n+1:5d}: {lines[n]}")

            print()

if not found:
    print("NO GATE LOGIC FOUND.")
