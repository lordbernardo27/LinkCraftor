from __future__ import annotations

import ast
from pathlib import Path

JOB_ID = "ukj_d2040c85de8e904e32f0cf41"
BACKEND = Path("backend/server")

TARGETS = {
    "update_job_progress",
    "write_json",
    "safe_write_json",
    "atomic_write_json",
}

print()
print("=" * 112)
print("TRACEBACK SOURCE INSPECTION")
print("=" * 112)

found = 0

for py in sorted(BACKEND.rglob("*.py")):

    try:
        source = py.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )
    except Exception:
        continue

    try:
        tree = ast.parse(source, filename=str(py))
    except Exception:
        continue

    lines = source.splitlines()

    for node in ast.walk(tree):

        if not isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            continue

        if node.name not in TARGETS:
            continue

        found += 1

        print()
        print("-" * 112)
        print("FILE:", py)
        print("FUNCTION:", node.name)
        print(
            "LINES:",
            f"{node.lineno}-{node.end_lineno}",
        )
        print("-" * 112)

        start = max(1, node.lineno - 10)
        end = min(len(lines), node.end_lineno + 10)

        for ln in range(start, end + 1):

            marker = (
                ">>>"
                if node.lineno <= ln <= node.end_lineno
                else "   "
            )

            print(
                f"{marker} {ln:5}: {lines[ln-1]}"
            )


print()
print("=" * 112)
print("FAILED JOB STATUS FILES")
print("=" * 112)

for root in [
    Path("backend/server/data/job_status/universal_knowledge"),
    Path("backend/server/data/progress/universal_knowledge"),
    Path("backend/server/data/failures/universal_knowledge"),
]:

    if not root.exists():
        continue

    matches = list(root.rglob(f"*{JOB_ID}*"))

    if not matches:
        continue

    print()
    print("DIRECTORY:", root)

    for p in matches:
        print()
        print("PATH:", p)
        print("SIZE:", p.stat().st_size)

        try:
            print("-" * 80)
            print(
                p.read_text(
                    encoding="utf-8",
                    errors="replace",
                )
            )
            print("-" * 80)
        except Exception as exc:
            print(
                "READ ERROR:",
                type(exc).__name__,
                str(exc),
            )


print()
print("=" * 112)
print("SEARCHING FOR TRACEBACKS")
print("=" * 112)

keywords = (
    JOB_ID,
    "WinError 5",
    "Access is denied",
)

for path in sorted(BACKEND.rglob("*")):

    if not path.is_file():
        continue

    if path.suffix.lower() not in {
        ".log",
        ".txt",
        ".json",
        ".jsonl",
    }:
        continue

    try:
        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except Exception:
        continue

    if not any(k in text for k in keywords):
        continue

    print()
    print("MATCH:", path)
    print("-" * 112)

    for line in text.splitlines():

        if any(k in line for k in keywords):
            print(line)

print()
print("=" * 112)
print("SUMMARY")
print("=" * 112)
print("Functions located:", found)
print("No files were modified.")
