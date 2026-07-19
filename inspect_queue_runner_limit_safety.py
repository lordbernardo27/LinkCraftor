from __future__ import annotations

import ast
from pathlib import Path


TARGET = Path(
    "backend/server/workers/"
    "universal_knowledge_queue_runner.py"
)

FUNCTION_NAME = "run_universal_knowledge_queue_v1"


source = TARGET.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

lines = source.splitlines()
tree = ast.parse(source, filename=str(TARGET))

target = None

for node in ast.walk(tree):
    if (
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == FUNCTION_NAME
    ):
        target = node
        break

if target is None:
    raise RuntimeError(
        f"{FUNCTION_NAME} was not found in {TARGET}"
    )


print()
print("=" * 112)
print("QUEUE RUNNER READ/REWRITE SAFETY INSPECTION")
print("=" * 112)
print("File:", TARGET)
print(
    "Function lines:",
    f"{target.lineno}-{target.end_lineno}",
)
print("-" * 112)

for line_number in range(
    target.lineno,
    target.end_lineno + 1,
):
    print(
        f"{line_number:5}: "
        f"{lines[line_number - 1]}"
    )


print()
print("=" * 112)
print("READ_QUEUE CALLS")
print("=" * 112)

calls_found = 0

for node in ast.walk(target):
    if not isinstance(node, ast.Call):
        continue

    function_name = None

    if isinstance(node.func, ast.Name):
        function_name = node.func.id
    elif isinstance(node.func, ast.Attribute):
        function_name = node.func.attr

    if function_name != "read_queue":
        continue

    calls_found += 1

    print()
    print("Call line:", node.lineno)

    try:
        print(
            "Call source:",
            ast.unparse(node),
        )
    except Exception:
        print(
            "Call source:",
            lines[node.lineno - 1].strip(),
        )

    print(
        "Positional arguments:",
        len(node.args),
    )

    print(
        "Keyword arguments:",
        {
            keyword.arg: ast.unparse(keyword.value)
            for keyword in node.keywords
            if keyword.arg
        },
    )


print()
print("=" * 112)
print("QUEUE REWRITE CALLS")
print("=" * 112)

for node in ast.walk(target):
    if not isinstance(node, ast.Call):
        continue

    function_name = None

    if isinstance(node.func, ast.Name):
        function_name = node.func.id
    elif isinstance(node.func, ast.Attribute):
        function_name = node.func.attr

    if function_name != "_write_remaining_queue_v1":
        continue

    print()
    print("Call line:", node.lineno)

    try:
        print(
            "Call source:",
            ast.unparse(node),
        )
    except Exception:
        print(
            "Call source:",
            lines[node.lineno - 1].strip(),
        )


print()
print("=" * 112)
print("RESULT")
print("=" * 112)
print("read_queue calls found:", calls_found)

if calls_found == 0:
    print(
        "FAIL: The queue-reading call was not found."
    )
else:
    print(
        "PASS: Queue-reading and rewrite behavior "
        "was printed for inspection."
    )

print("No backend or runtime file was modified.")
