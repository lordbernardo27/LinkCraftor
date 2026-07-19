from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path("backend/server")
RUNNER = Path(
    "backend/server/workers/"
    "universal_knowledge_queue_runner.py"
)

TARGET_FUNCTIONS = {
    "run_universal_knowledge_queue_v1",
    "read_queue",
    "read_universal_knowledge_queue",
    "load_queue",
}


def read_source(path: Path) -> tuple[str, list[str], ast.AST]:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    return source, source.splitlines(), tree


def function_nodes(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            yield node


def called_names(node: ast.AST) -> set[str]:
    names = set()

    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue

        func = child.func

        if isinstance(func, ast.Name):
            names.add(func.id)

        elif isinstance(func, ast.Attribute):
            names.add(func.attr)

    return names


print()
print("=" * 112)
print("UNIVERSAL KNOWLEDGE QUEUE PATH INSPECTION")
print("=" * 112)

if not RUNNER.is_file():
    raise RuntimeError(
        f"Queue runner was not found: {RUNNER}"
    )

runner_source, runner_lines, runner_tree = read_source(
    RUNNER
)

runner_function = None

for node in function_nodes(runner_tree):
    if node.name == "run_universal_knowledge_queue_v1":
        runner_function = node
        break

if runner_function is None:
    raise RuntimeError(
        "run_universal_knowledge_queue_v1 was not found."
    )

start = runner_function.lineno
end = getattr(
    runner_function,
    "end_lineno",
    runner_function.lineno,
)

print()
print("QUEUE RUNNER FILE:", RUNNER)
print(f"FUNCTION LINES: {start}-{end}")
print("-" * 112)

for line_number in range(start, end + 1):
    print(
        f"{line_number:5}: "
        f"{runner_lines[line_number - 1]}"
    )

calls = called_names(runner_function)

print()
print("=" * 112)
print("FUNCTIONS CALLED BY QUEUE RUNNER")
print("=" * 112)

for name in sorted(calls):
    print(name)


interesting_calls = {
    name
    for name in calls
    if (
        "queue" in name.lower()
        or "job" in name.lower()
        or "status" in name.lower()
    )
}

definitions = []

for path in ROOT.rglob("*.py"):
    try:
        source, lines, tree = read_source(path)
    except Exception:
        continue

    for node in function_nodes(tree):
        if (
            node.name in interesting_calls
            or node.name in TARGET_FUNCTIONS
        ):
            definitions.append(
                (
                    path,
                    lines,
                    node.name,
                    node.lineno,
                    getattr(
                        node,
                        "end_lineno",
                        node.lineno,
                    ),
                )
            )


print()
print("=" * 112)
print("RELATED FUNCTION DEFINITIONS")
print("=" * 112)

for path, lines, name, function_start, function_end in definitions:
    print()
    print("-" * 112)
    print("FILE:", path)
    print("FUNCTION:", name)
    print(
        "LINES:",
        f"{function_start}-{function_end}",
    )
    print("-" * 112)

    context_start = max(
        1,
        function_start - 20,
    )

    context_end = min(
        len(lines),
        function_end + 20,
    )

    for line_number in range(
        context_start,
        context_end + 1,
    ):
        marker = (
            ">>>"
            if function_start
            <= line_number
            <= function_end
            else "   "
        )

        print(
            f"{marker} {line_number:5}: "
            f"{lines[line_number - 1]}"
        )


print()
print("=" * 112)
print("QUEUE PATH REFERENCES")
print("=" * 112)

path_terms = (
    "queue.jsonl",
    "queue_ws_",
    "jobs/universal_knowledge",
    "queues/universal_knowledge",
    "JOBS_ROOT",
    "QUEUE_ROOT",
    "QUEUE_DIR",
    "QUEUE_PATH",
)

references = 0

for path in ROOT.rglob("*.py"):
    try:
        lines = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        ).splitlines()
    except Exception:
        continue

    matches = [
        line_number
        for line_number, line in enumerate(
            lines,
            start=1,
        )
        if any(
            term.lower() in line.lower()
            for term in path_terms
        )
    ]

    if not matches:
        continue

    references += 1

    print()
    print("-" * 112)
    print("FILE:", path)
    print("-" * 112)

    shown_ranges = []

    for match in matches:
        range_start = max(1, match - 8)
        range_end = min(len(lines), match + 12)

        if any(
            range_start >= old_start
            and range_end <= old_end
            for old_start, old_end in shown_ranges
        ):
            continue

        shown_ranges.append(
            (
                range_start,
                range_end,
            )
        )

        for line_number in range(
            range_start,
            range_end + 1,
        ):
            marker = (
                ">>>"
                if line_number in matches
                else "   "
            )

            print(
                f"{marker} {line_number:5}: "
                f"{lines[line_number - 1]}"
            )

        print()


print()
print("=" * 112)
print("SUMMARY")
print("=" * 112)
print(
    "Related function definitions:",
    len(definitions),
)
print(
    "Files containing queue-path references:",
    references,
)
print()
print(
    "No queue, job, worker, store, "
    "or backend file was modified."
)
