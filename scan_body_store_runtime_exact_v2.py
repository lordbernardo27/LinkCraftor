from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

SERVER_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
)

EXCLUDED_PARTS = {
    "__pycache__",
    "backups",
    "runtime_backups",
    ".venv",
    ".git",
    "node_modules",
}

EXACT_MODULE_TERMS = {
    "body_store_runtime",
    "universal_article_body_store_runtime",
}

EXACT_JOB_TYPES = {
    "universal_article_body_store.write",
    "universal_article_body_store.read",
    "universal_article_body_store.verify",
    "universal_article_body_store.list",
    "universal_article_body_store.metadata",
    "body_store_write",
    "body_store_read",
    "body_store_verify",
}

EXACT_HANDLER_NAMES = {
    "handle_body_store_write",
    "handle_body_store_read",
    "handle_body_store_verify",
    "execute_body_store_runtime",
    "execute_universal_article_body_store_runtime",
}

EXACT_COORDINATOR_NAMES = {
    "coordinate_body_store_runtime",
    "run_body_store_runtime",
    "body_store_runtime_coordinator",
}

files_with_exact_terms = []
exact_job_references = []
exact_handlers = []
exact_coordinators = []
exact_registration_calls = []
syntax_failures = []


def relative(
    path: Path,
) -> str:
    return path.relative_to(
        PROJECT_ROOT
    ).as_posix()


for path in SERVER_ROOT.rglob(
    "*.py"
):
    if any(
        part in EXCLUDED_PARTS
        for part in path.parts
    ):
        continue

    try:
        source = path.read_text(
            encoding="utf-8-sig",
            errors="strict",
        )

        tree = ast.parse(
            source,
            filename=str(
                path
            ),
        )

    except SyntaxError as exc:
        syntax_failures.append(
            relative(
                path
            )
            + ": "
            + str(
                exc
            )
        )

        continue

    lowered = source.casefold()

    matched_exact_term = any(
        term in lowered
        for term in EXACT_MODULE_TERMS
    )

    if matched_exact_term:
        files_with_exact_terms.append(
            relative(
                path
            )
        )

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            name = node.name.casefold()

            if name in EXACT_HANDLER_NAMES:
                exact_handlers.append(
                    relative(
                        path
                    )
                    + ":"
                    + str(
                        node.lineno
                    )
                    + ":"
                    + node.name
                )

            if name in EXACT_COORDINATOR_NAMES:
                exact_coordinators.append(
                    relative(
                        path
                    )
                    + ":"
                    + str(
                        node.lineno
                    )
                    + ":"
                    + node.name
                )

        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        function_name = ""

        if isinstance(
            node.func,
            ast.Name,
        ):
            function_name = node.func.id

        elif isinstance(
            node.func,
            ast.Attribute,
        ):
            function_name = node.func.attr

        for argument in [
            *node.args,
            *[
                keyword.value
                for keyword in node.keywords
            ],
        ]:
            if not isinstance(
                argument,
                ast.Constant,
            ):
                continue

            if not isinstance(
                argument.value,
                str,
            ):
                continue

            value = argument.value.casefold()

            if value in EXACT_JOB_TYPES:
                exact_job_references.append(
                    relative(
                        path
                    )
                    + ":"
                    + str(
                        node.lineno
                    )
                    + ":"
                    + argument.value
                )

                if (
                    "register"
                    in function_name.casefold()
                ):
                    exact_registration_calls.append(
                        relative(
                            path
                        )
                        + ":"
                        + str(
                            node.lineno
                        )
                        + ":"
                        + function_name
                    )


files_with_exact_terms = sorted(
    set(
        files_with_exact_terms
    )
)

exact_job_references = sorted(
    set(
        exact_job_references
    )
)

exact_handlers = sorted(
    set(
        exact_handlers
    )
)

exact_coordinators = sorted(
    set(
        exact_coordinators
    )
)

exact_registration_calls = sorted(
    set(
        exact_registration_calls
    )
)


runtime_exists = any(
    (
        files_with_exact_terms,
        exact_job_references,
        exact_handlers,
        exact_coordinators,
        exact_registration_calls,
    )
)

classification = (
    "EXACT_BODY_STORE_RUNTIME_FOUND"
    if runtime_exists
    else "NO_EXACT_BODY_STORE_RUNTIME_FOUND"
)


print()
print("=" * 112)
print(
    "UNIVERSAL ARTICLE BODY STORE RUNTIME — EXACT READ-ONLY SCAN"
)
print("=" * 112)
print()

print(
    "Classification: "
    + classification
)

print()
print(
    "Exact runtime-term files:       "
    + str(
        len(
            files_with_exact_terms
        )
    )
)

for item in files_with_exact_terms:
    print(
        "  "
        + item
    )

print()
print(
    "Exact job-type references:      "
    + str(
        len(
            exact_job_references
        )
    )
)

for item in exact_job_references:
    print(
        "  "
        + item
    )

print()
print(
    "Exact runtime handlers:         "
    + str(
        len(
            exact_handlers
        )
    )
)

for item in exact_handlers:
    print(
        "  "
        + item
    )

print()
print(
    "Exact runtime coordinators:     "
    + str(
        len(
            exact_coordinators
        )
    )
)

for item in exact_coordinators:
    print(
        "  "
        + item
    )

print()
print(
    "Exact registration calls:       "
    + str(
        len(
            exact_registration_calls
        )
    )
)

for item in exact_registration_calls:
    print(
        "  "
        + item
    )

print()
print(
    "Source files modified:          False"
)

print(
    "Production Body Store modified: False"
)

print(
    "Runtime jobs created:           0"
)

print(
    "Persistent outputs written:     0"
)

print()
print(
    "Syntax failures"
)

if syntax_failures:
    for item in syntax_failures:
        print(
            "  "
            + item
        )

else:
    print(
        "  None"
    )

print()

if syntax_failures:
    print(
        "BODY STORE RUNTIME EXACT SCAN: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE RUNTIME EXACT SCAN: PASS"
)

print("=" * 112)
