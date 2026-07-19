from __future__ import annotations

import ast
import os
import stat
from pathlib import Path


WORKSPACE_ID = "ws_whattoexpect_com"
FAILED_JOB_ID = "ukj_d2040c85de8e904e32f0cf41"

ORCHESTRATOR = Path(
    "backend/server/jobs/"
    "universal_knowledge_orchestrator.py"
)

BACKEND_ROOT = Path("backend/server")

PROGRESS_DIR = (
    Path("backend/server/data/progress/universal_knowledge")
    / WORKSPACE_ID
)

FINAL_PATH = PROGRESS_DIR / f"{FAILED_JOB_ID}.json"
TMP_PATH = PROGRESS_DIR / f"{FAILED_JOB_ID}.json.tmp"

TARGET_FUNCTIONS = {
    "update_job_progress",
    "write_json",
    "atomic_write_json",
    "safe_write_json",
    "progress_path",
}


def read_python(path: Path):
    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    return source, source.splitlines(), tree


def functions(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            yield node


def print_function(
    path: Path,
    lines: list[str],
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> None:
    print()
    print("-" * 112)
    print("FILE:", path)
    print("FUNCTION:", node.name)
    print(
        "LINES:",
        f"{node.lineno}-{node.end_lineno}",
    )
    print("-" * 112)

    start = max(1, node.lineno - 15)
    end = min(len(lines), node.end_lineno + 15)

    for line_number in range(start, end + 1):
        marker = (
            ">>>"
            if node.lineno <= line_number <= node.end_lineno
            else "   "
        )

        print(
            f"{marker} {line_number:5}: "
            f"{lines[line_number - 1]}"
        )


def describe_path(path: Path) -> None:
    print()
    print("Path:", path)
    print("Exists:", path.exists())
    print("Is file:", path.is_file())
    print("Is directory:", path.is_dir())

    if not path.exists():
        return

    try:
        info = path.stat()

        print("Size:", info.st_size)
        print("Mode:", oct(info.st_mode))
        print(
            "Read-only mode bit:",
            not bool(info.st_mode & stat.S_IWUSR),
        )
        print(
            "OS writable:",
            os.access(path, os.W_OK),
        )
    except Exception as exc:
        print(
            "STAT ERROR:",
            type(exc).__name__,
            str(exc),
        )


print()
print("=" * 112)
print("PROGRESS PERSISTENCE FAILURE INSPECTION")
print("=" * 112)
print("Workspace:", WORKSPACE_ID)
print("Failed job:", FAILED_JOB_ID)


if not ORCHESTRATOR.is_file():
    raise RuntimeError(
        f"Orchestrator not found: {ORCHESTRATOR}"
    )


source, lines, tree = read_python(ORCHESTRATOR)

found_names = set()

for node in functions(tree):
    if node.name in TARGET_FUNCTIONS:
        found_names.add(node.name)
        print_function(
            ORCHESTRATOR,
            lines,
            node,
        )


print()
print("=" * 112)
print("FUNCTIONS FOUND")
print("=" * 112)

for name in sorted(found_names):
    print(name)


print()
print("=" * 112)
print("FAILED JOB PROGRESS PATHS")
print("=" * 112)

describe_path(PROGRESS_DIR)
describe_path(FINAL_PATH)
describe_path(TMP_PATH)


print()
print("=" * 112)
print("PROGRESS DIRECTORY CONTENTS FOR FAILED JOB")
print("=" * 112)

if PROGRESS_DIR.exists():
    matches = sorted(
        path
        for path in PROGRESS_DIR.iterdir()
        if FAILED_JOB_ID in path.name
    )

    if not matches:
        print("No matching files found.")

    for path in matches:
        describe_path(path)


print()
print("=" * 112)
print("TEMPORARY-FILE IMPLEMENTATIONS")
print("=" * 112)

search_terms = (
    ".tmp",
    "with_suffix",
    "replace(",
    "os.replace",
    "update_job_progress(",
)

matched_files = 0

for path in BACKEND_ROOT.rglob("*.py"):
    try:
        file_lines = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        ).splitlines()
    except Exception:
        continue

    matching_lines = [
        number
        for number, line in enumerate(
            file_lines,
            start=1,
        )
        if any(
            term in line
            for term in search_terms
        )
        and (
            "progress" in line.lower()
            or "write_json" in line.lower()
            or ".tmp" in line.lower()
            or "replace(" in line.lower()
        )
    ]

    if not matching_lines:
        continue

    matched_files += 1

    print()
    print("-" * 112)
    print("FILE:", path)
    print("-" * 112)

    shown = set()

    for match in matching_lines:
        start = max(1, match - 5)
        end = min(len(file_lines), match + 8)

        for line_number in range(start, end + 1):
            if line_number in shown:
                continue

            shown.add(line_number)

            marker = (
                ">>>"
                if line_number in matching_lines
                else "   "
            )

            print(
                f"{marker} {line_number:5}: "
                f"{file_lines[line_number - 1]}"
            )


print()
print("=" * 112)
print("CALLERS OF update_job_progress")
print("=" * 112)

caller_count = 0

for path in BACKEND_ROOT.rglob("*.py"):
    try:
        file_lines = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        ).splitlines()
    except Exception:
        continue

    calls = [
        number
        for number, line in enumerate(
            file_lines,
            start=1,
        )
        if "update_job_progress(" in line
    ]

    if not calls:
        continue

    caller_count += 1

    print()
    print("FILE:", path)

    for line_number in calls:
        start = max(1, line_number - 3)
        end = min(
            len(file_lines),
            line_number + 6,
        )

        for number in range(start, end + 1):
            marker = (
                ">>>"
                if number == line_number
                else "   "
            )

            print(
                f"{marker} {number:5}: "
                f"{file_lines[number - 1]}"
            )


print()
print("=" * 112)
print("SUMMARY")
print("=" * 112)
print(
    "Target functions found:",
    sorted(found_names),
)
print(
    "Files with relevant temporary-write logic:",
    matched_files,
)
print(
    "Files calling update_job_progress:",
    caller_count,
)
print()
print(
    "No queue, progress, job, worker, store, "
    "or backend file was modified."
)
