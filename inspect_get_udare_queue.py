from __future__ import annotations

import ast
import json
from pathlib import Path

TARGET = Path("run_udare_phase_4_3b_full_population.py")

if not TARGET.is_file():
    raise FileNotFoundError(f"Missing file: {TARGET}")

text = TARGET.read_text(
    encoding="utf-8",
    errors="strict",
)

tree = ast.parse(
    text,
    filename=str(TARGET),
)

lines = text.splitlines()

definition_found = False

for node in tree.body:
    if (
        isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
        and node.name == "get_udare_queue"
    ):
        definition_found = True

        start = node.lineno
        end = node.end_lineno or node.lineno

        print("=" * 112)
        print("GET_UDARE_QUEUE DEFINITION")
        print("=" * 112)

        for number in range(start, end + 1):
            print(
                f"{number:5d}: "
                f"{lines[number - 1]}"
            )

        print()

if not definition_found:
    raise RuntimeError(
        "get_udare_queue() definition was not found."
    )

namespace: dict = {
    "__name__": "__udare_gate_inspection__",
}

prefix_lines: list[str] = []

for node in tree.body:
    if isinstance(
        node,
        (
            ast.Import,
            ast.ImportFrom,
            ast.Assign,
            ast.AnnAssign,
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    ):
        if (
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name != "get_udare_queue"
        ):
            continue

        start = node.lineno - 1
        end = node.end_lineno or node.lineno

        prefix_lines.extend(
            lines[start:end]
        )
        prefix_lines.append("")

inspection_source = "\n".join(
    prefix_lines
)

exec(
    compile(
        inspection_source,
        str(TARGET),
        "exec",
    ),
    namespace,
)

get_udare_queue = namespace.get(
    "get_udare_queue"
)

if not callable(get_udare_queue):
    raise RuntimeError(
        "get_udare_queue() could not be loaded."
    )

jobs = get_udare_queue()

print("=" * 112)
print("LIVE GET_UDARE_QUEUE RESULT")
print("=" * 112)

print("Returned type:", type(jobs).__name__)
print("Returned count:", len(jobs))

job_type_counts: dict[str, int] = {}
status_counts: dict[str, int] = {}

for job in jobs:
    job_type = str(
        job.get("job_type") or ""
    )
    status = str(
        job.get("status") or ""
    )

    job_type_counts[job_type] = (
        job_type_counts.get(job_type, 0) + 1
    )

    status_counts[status] = (
        status_counts.get(status, 0) + 1
    )

print(
    "Job type counts:",
    json.dumps(
        job_type_counts,
        indent=2,
    ),
)

print(
    "Status counts:",
    json.dumps(
        status_counts,
        indent=2,
    ),
)

print()
print("First five returned jobs:")

print(
    json.dumps(
        [
            {
                "job_id": job.get("job_id"),
                "job_type": job.get("job_type"),
                "status": job.get("status"),
                "html_id": (
                    (job.get("payload") or {}).get(
                        "html_id"
                    )
                    or
                    (job.get("payload") or {}).get(
                        "source_record_id"
                    )
                ),
            }
            for job in jobs[:5]
        ],
        indent=2,
        ensure_ascii=False,
    )
)
