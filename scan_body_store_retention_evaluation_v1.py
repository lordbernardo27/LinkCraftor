from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

PACKAGE_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
)

TARGET_FILES = [
    PACKAGE_ROOT
    / "body_store_retention_policy_contract_v1.py",

    PACKAGE_ROOT
    / "body_store_retention_policy_engine_v1.py",

    PACKAGE_ROOT
    / "body_store_lifecycle_state_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_state_transition_engine_v1.py",
]

EXPECTED_EVALUATION_FUNCTIONS = {
    "evaluate_body_store_retention_policy_v1",
    "calculate_body_store_retention_result_v1",
    "evaluate_body_store_hold_status_v1",
    "evaluate_body_store_deletion_eligibility_v1",
}

EVALUATION_TERMS = {
    "retention_evaluation",
    "evaluation_id",
    "evaluated_at",
    "retention_expired",
    "retention_satisfied",
    "deletion_eligible",
    "hold_active",
}

FORBIDDEN_WRITE_CALLS = {
    "write_text",
    "write_bytes",
    "mkdir",
    "unlink",
    "rename",
}

function_matches = []
evaluation_references = []
filesystem_write_calls = []
syntax_failures = []


for path in TARGET_FILES:
    if not path.is_file():
        continue

    try:
        source = path.read_text(
            encoding="utf-8-sig",
            errors="strict",
        )

        tree = ast.parse(
            source,
            filename=str(path),
        )

    except Exception as exc:
        syntax_failures.append(
            f"{path.relative_to(PROJECT_ROOT)} : {exc}"
        )

        continue

    lowered = source.casefold()

    if any(
        term in lowered
        for term in EVALUATION_TERMS
    ):
        evaluation_references.append(
            path.relative_to(
                PROJECT_ROOT
            ).as_posix()
        )

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            if node.name in EXPECTED_EVALUATION_FUNCTIONS:
                function_matches.append(
                    {
                        "path":
                            path.relative_to(
                                PROJECT_ROOT
                            ).as_posix(),

                        "line":
                            node.lineno,

                        "name":
                            node.name,
                    }
                )

        elif isinstance(
            node,
            ast.Call,
        ):
            call_name = ""

            if isinstance(
                node.func,
                ast.Name,
            ):
                call_name = node.func.id

            elif isinstance(
                node.func,
                ast.Attribute,
            ):
                call_name = node.func.attr

            if call_name in FORBIDDEN_WRITE_CALLS:
                filesystem_write_calls.append(
                    {
                        "path":
                            path.relative_to(
                                PROJECT_ROOT
                            ).as_posix(),

                        "line":
                            node.lineno,

                        "call":
                            call_name,
                    }
                )


dedicated_evaluation_path = (
    PACKAGE_ROOT
    / "body_store_retention_evaluation_v1.py"
)

dedicated_evaluation_exists = (
    dedicated_evaluation_path.is_file()
)


if dedicated_evaluation_exists:
    classification = (
        "BODY_STORE_RETENTION_EVALUATION_EXISTS"
    )

elif function_matches:
    classification = (
        "RETENTION_ENGINE_EVALUATION_FUNCTIONS_EXIST"
    )

else:
    classification = (
        "NO_BODY_STORE_RETENTION_EVALUATION_FOUND"
    )


print()
print("=" * 116)
print(
    "BODY STORE RETENTION EVALUATION — READ-ONLY DISCOVERY"
)
print("=" * 116)
print()

print(
    "Classification:",
    classification,
)

print()

print(
    "Dedicated evaluation component exists:",
    dedicated_evaluation_exists,
)

print()

print(
    "Evaluation functions found:",
    len(
        function_matches
    ),
)

for item in function_matches:
    print(
        f"  {item['path']}:{item['line']}:{item['name']}"
    )

print()

print(
    "Evaluation-reference files:",
    len(
        set(
            evaluation_references
        )
    ),
)

for item in sorted(
    set(
        evaluation_references
    )
):
    print(
        "  "
        + item
    )

print()

print(
    "Filesystem write calls found:",
    len(
        filesystem_write_calls
    ),
)

for item in filesystem_write_calls:
    print(
        f"  {item['path']}:{item['line']}:{item['call']}"
    )

print()

print(
    "Production files modified:      False"
)

print(
    "Lifecycle records modified:     False"
)

print(
    "Body Store modified:            False"
)

print(
    "Queue modified:                 False"
)

print(
    "Runtime registrations modified: 0"
)

print()

print(
    "SYNTAX FAILURES"
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
        "BODY STORE RETENTION EVALUATION SCAN: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE RETENTION EVALUATION SCAN: PASS"
)

print("=" * 116)
