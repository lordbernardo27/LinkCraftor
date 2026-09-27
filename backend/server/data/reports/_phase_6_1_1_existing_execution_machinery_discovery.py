from __future__ import annotations

import ast
import re

from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

BACKEND = (
    ROOT
    / "backend"
    / "server"
)

REPORT = (
    BACKEND
    / "data"
    / "reports"
    / "phase_6_1_1_existing_execution_machinery_discovery.txt"
)


SEARCH_ROOTS = (
    BACKEND / "runtime",
    BACKEND / "jobs",
    BACKEND / "services",
    BACKEND / "orchestration",
)


EXECUTION_TERMS = (
    "execute",
    "execution",
    "executor",
    "dispatch",
    "handler",
    "invoke",
    "claim",
    "enqueue",
    "dequeue",
    "requeue",
    "lease",
    "worker",
    "checkpoint",
    "resume",
    "suspend",
    "cancel",
    "terminate",
    "retry",
    "attempt",
    "backoff",
    "idempot",
    "fence",
    "result",
)


python_files = []


for root in SEARCH_ROOTS:

    if not root.exists():
        continue

    for path in root.rglob("*.py"):

        if "__pycache__" in path.parts:
            continue

        if path.name.startswith("_phase_"):
            continue

        if "_before_" in path.name:
            continue

        python_files.append(path)


python_files = tuple(
    sorted(
        set(
            python_files
        )
    )
)


definitions = []
calls = []
imports = []
source_hits = []
parse_errors = []


for path in python_files:

    relative = str(
        path.relative_to(ROOT)
    )

    try:

        source = path.read_text(
            encoding="utf-8-sig"
        )

        tree = ast.parse(source)

    except Exception as exc:

        parse_errors.append(
            (
                relative,
                repr(exc),
            )
        )

        continue


    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):

            lower_name = node.name.lower()

            if any(
                term in lower_name
                for term in EXECUTION_TERMS
            ):

                definitions.append(
                    (
                        relative,
                        getattr(node, "lineno", 0),
                        type(node).__name__,
                        node.name,
                    )
                )


        elif isinstance(node, ast.ImportFrom):

            module = node.module or ""

            if any(
                term in module.lower()
                for term in EXECUTION_TERMS
            ):

                imports.append(
                    (
                        relative,
                        getattr(node, "lineno", 0),
                        module,
                    )
                )


        elif isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):

                call_name = node.func.id

            elif isinstance(node.func, ast.Attribute):

                call_name = node.func.attr

            else:

                continue


            if any(
                term in call_name.lower()
                for term in EXECUTION_TERMS
            ):

                calls.append(
                    (
                        relative,
                        getattr(node, "lineno", 0),
                        call_name,
                    )
                )


    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):

        lower = line.lower()

        matched = tuple(
            term
            for term in EXECUTION_TERMS
            if term in lower
        )

        if not matched:
            continue

        if (
            line.strip().startswith("#")
            and
            not any(
                token in lower
                for token in (
                    "execute",
                    "dispatch",
                    "handler",
                    "claim",
                    "checkpoint",
                    "retry",
                    "cancel",
                )
            )
        ):
            continue

        source_hits.append(
            (
                relative,
                line_number,
                matched,
                line.strip()[:500],
            )
        )


lines = [
    "PHASE 6.1.1 — EXISTING EXECUTION MACHINERY DISCOVERY",
    "=" * 118,
    "",
    "MODE: READ ONLY",
    "PRODUCTION CODE MODIFIED: NO",
    "",
    "SECTION 1 — FILES SCANNED",
    "-" * 118,
    "",
]


for path in python_files:

    lines.append(
        str(
            path.relative_to(ROOT)
        )
    )


lines.extend(
    [
        "",
        "SECTION 2 — EXECUTION-RELATED DEFINITIONS",
        "-" * 118,
        "",
    ]
)


if definitions:

    for (
        path,
        line_number,
        node_type,
        name,
    ) in definitions:

        lines.append(
            f"{path}:{line_number} | {node_type} | {name}"
        )

else:

    lines.append("NONE")


lines.extend(
    [
        "",
        "SECTION 3 — EXECUTION-RELATED IMPORTS",
        "-" * 118,
        "",
    ]
)


if imports:

    for (
        path,
        line_number,
        module,
    ) in imports:

        lines.append(
            f"{path}:{line_number} | {module}"
        )

else:

    lines.append("NONE")


lines.extend(
    [
        "",
        "SECTION 4 — EXECUTION-RELATED CALL SITES",
        "-" * 118,
        "",
    ]
)


if calls:

    for (
        path,
        line_number,
        call_name,
    ) in calls:

        lines.append(
            f"{path}:{line_number} | {call_name}"
        )

else:

    lines.append("NONE")


lines.extend(
    [
        "",
        "SECTION 5 — SOURCE HITS",
        "-" * 118,
        "",
    ]
)


if source_hits:

    for (
        path,
        line_number,
        matched,
        source_line,
    ) in source_hits:

        lines.append(
            f"{path}:{line_number}"
        )

        lines.append(
            "  TOKENS: "
            + ", ".join(matched)
        )

        lines.append(
            "  SOURCE: "
            + source_line
        )

        lines.append("")

else:

    lines.append("NONE")


lines.extend(
    [
        "",
        "SECTION 6 — PARSE ERRORS",
        "-" * 118,
        "",
    ]
)


if parse_errors:

    for path, error in parse_errors:

        lines.append(
            f"{path} | {error}"
        )

else:

    lines.append("NONE")


lines.extend(
    [
        "",
        "SECTION 7 — DISCOVERY QUESTIONS FOR 6.1.2",
        "-" * 118,
        "",

        "1. Which component currently invokes registered runtime handlers?",
        "2. Which component currently moves a claimed job into RUNNING?",
        "3. Which component currently applies terminal job status?",
        "4. Which component currently captures handler return values?",
        "5. Which component currently captures handler exceptions?",
        "6. Which component currently owns retries/requeue?",
        "7. Which component currently owns attempt accounting?",
        "8. Which component currently validates leases before execution?",
        "9. Which component currently prevents duplicate execution?",
        "10. Which component currently handles cancellation of active work?",
        "11. Which component currently handles checkpoint save/restore?",
        "12. Which component currently writes execution results/state?",
        "13. Does a central execution controller already exist?",
        "14. Does the worker execute jobs directly today?",
        "15. Does Runtime Registration resolve only, or resolve and execute?",
        "",
        "NEXT:",
        "Classify discovered machinery as ALREADY OWNED / WRAP-IN-PHASE-6 / MISSING.",
    ]
)


REPORT.write_text(
    "\n".join(lines),
    encoding="utf-8",
)


print("=" * 100)
print(
    "PHASE 6.1.1 EXISTING EXECUTION MACHINERY DISCOVERY COMPLETE"
)
print("=" * 100)

print(
    "Python files scanned:",
    len(python_files),
)

print(
    "Execution-related definitions:",
    len(definitions),
)

print(
    "Execution-related imports:",
    len(imports),
)

print(
    "Execution-related call sites:",
    len(calls),
)

print(
    "Source hits:",
    len(source_hits),
)

print(
    "Parse errors:",
    len(parse_errors),
)

print()
print(
    "PRODUCTION CODE MODIFIED: NO"
)

print(
    "REPORT:",
    REPORT,
)

print()
print(
    "STATUS: 6.1.1 DISCOVERY COMPLETE — OWNERSHIP CLASSIFICATION REQUIRED"
)
