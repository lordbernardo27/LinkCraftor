from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path("backend/server")
TARGET_FUNCTION = "load_raw_website_html_store_v1"


def find_function():
    results = []

    for path in ROOT.rglob("*.py"):
        try:
            source = path.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
            tree = ast.parse(
                source,
                filename=str(path),
            )
        except Exception:
            continue

        for node in ast.walk(tree):
            if (
                isinstance(
                    node,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                )
                and node.name == TARGET_FUNCTION
            ):
                results.append(
                    (
                        path,
                        source.splitlines(),
                        node.lineno,
                        getattr(
                            node,
                            "end_lineno",
                            node.lineno,
                        ),
                    )
                )

    return results


results = find_function()

print()
print("=" * 112)
print("RAW HTML STORE LOADER INSPECTION")
print("=" * 112)

if not results:
    raise RuntimeError(
        f"{TARGET_FUNCTION} was not found."
    )

for path, lines, function_start, function_end in results:
    start = max(
        1,
        function_start - 25,
    )
    end = min(
        len(lines),
        function_end + 25,
    )

    print()
    print("FILE:", path)
    print(
        f"FUNCTION LINES: "
        f"{function_start}-{function_end}"
    )
    print("-" * 112)

    for current in range(
        start,
        end + 1,
    ):
        marker = (
            ">>>"
            if function_start
            <= current
            <= function_end
            else "   "
        )

        print(
            f"{marker} {current:5}: "
            f"{lines[current - 1]}"
        )

print()
print("=" * 112)
print("SUMMARY")
print("=" * 112)
print(
    "Function definitions found:",
    len(results),
)
print()
print(
    "No store, worker, queue, job, "
    "or backend file was modified."
)
