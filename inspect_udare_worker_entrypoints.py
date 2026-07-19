from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path("backend/server")

WORKER_PATH = Path(
    "backend/server/workers/"
    "udare_reconstruction_worker.py"
)

MODULE_TERMS = {
    "udare_reconstruction_worker",
    "UDARE reconstruction worker",
}

if not WORKER_PATH.is_file():
    raise RuntimeError(
        f"Worker file not found: {WORKER_PATH}"
    )


worker_source = WORKER_PATH.read_text(
    encoding="utf-8-sig",
    errors="replace",
)

worker_tree = ast.parse(
    worker_source,
    filename=str(WORKER_PATH),
)


public_functions = []
all_exports = []
aliases = []


for node in worker_tree.body:

    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    ):
        public_functions.append(
            {
                "name": node.name,
                "line": node.lineno,
                "end_line": getattr(
                    node,
                    "end_lineno",
                    node.lineno,
                ),
            }
        )

    elif isinstance(node, ast.Assign):

        for target in node.targets:

            if (
                isinstance(target, ast.Name)
                and target.id == "__all__"
            ):
                try:
                    value = ast.literal_eval(
                        node.value
                    )

                    if isinstance(
                        value,
                        (
                            list,
                            tuple,
                        ),
                    ):
                        all_exports.extend(
                            str(item)
                            for item in value
                        )

                except Exception:
                    pass

            if isinstance(target, ast.Name):

                if isinstance(
                    node.value,
                    ast.Name,
                ):
                    aliases.append(
                        (
                            target.id,
                            node.value.id,
                            node.lineno,
                        )
                    )

                elif isinstance(
                    node.value,
                    ast.Attribute,
                ):
                    aliases.append(
                        (
                            target.id,
                            ast.unparse(
                                node.value
                            ),
                            node.lineno,
                        )
                    )


print()
print("=" * 112)
print("UDARE WORKER ENTRY-POINT INSPECTION")
print("=" * 112)

print()
print("WORKER FILE:")
print(WORKER_PATH)

print()
print("FUNCTION DEFINITIONS")
print("-" * 112)

for item in public_functions:
    print(
        f"{item['line']:5}-"
        f"{item['end_line']:5}  "
        f"{item['name']}"
    )

print()
print("__all__ EXPORTS")
print("-" * 112)

if all_exports:
    for name in all_exports:
        print(name)
else:
    print("No __all__ declaration found.")

print()
print("DIRECT FUNCTION ALIASES")
print("-" * 112)

if aliases:
    for target, value, line in aliases:
        print(
            f"Line {line}: "
            f"{target} = {value}"
        )
else:
    print("No direct aliases found.")


candidate_names = {
    item["name"]
    for item in public_functions
    if (
        "udare" in item["name"].casefold()
        or "reconstruct" in item["name"].casefold()
        or "worker" in item["name"].casefold()
        or "execute" in item["name"].casefold()
    )
}

candidate_names.update(
    name
    for name in all_exports
)

print()
print("CANDIDATE ENTRY-POINT NAMES")
print("-" * 112)

for name in sorted(candidate_names):
    print(name)


print()
print("=" * 112)
print("SEARCHING BACKEND FOR IMPORTS, REFERENCES, AND REGISTRATIONS")
print("=" * 112)

matches = 0

for path in ROOT.rglob("*.py"):

    if path == WORKER_PATH:
        continue

    try:
        source = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )
    except Exception:
        continue

    lines = source.splitlines()

    terms = set(MODULE_TERMS)
    terms.update(candidate_names)

    matching_line_numbers = []

    for line_number, line in enumerate(
        lines,
        start=1,
    ):
        if any(
            term in line
            for term in terms
        ):
            matching_line_numbers.append(
                line_number
            )

    if not matching_line_numbers:
        continue

    matches += 1

    print()
    print("-" * 112)
    print("FILE:", path)
    print("-" * 112)

    printed_ranges = []

    for line_number in matching_line_numbers:

        start = max(
            1,
            line_number - 6,
        )

        end = min(
            len(lines),
            line_number + 10,
        )

        if any(
            start >= old_start
            and end <= old_end
            for old_start, old_end
            in printed_ranges
        ):
            continue

        printed_ranges.append(
            (
                start,
                end,
            )
        )

        print()
        print(
            f"LINES {start}-{end}"
        )

        for current in range(
            start,
            end + 1,
        ):
            marker = (
                ">>>"
                if current
                in matching_line_numbers
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
    "Candidate entry-point names:",
    len(candidate_names),
)
print(
    "Backend files containing references:",
    matches,
)

if matches == 0:
    print(
        "No static references were found. "
        "The worker may be loaded dynamically "
        "through importlib or a string-based registry."
    )

print()
print(
    "No backend, queue, job, worker, "
    "or store file was modified."
)
