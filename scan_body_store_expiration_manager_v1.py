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

EXPIRATION_FUNCTION_TERMS = {
    "expiration",
    "expire",
    "expired",
    "is_expired",
    "evaluate_expiration",
    "calculate_expiration",
}

EXPIRATION_FIELDS = {
    "expires_at",
    "expired_at",
    "retain_until",
    "retention_expired",
    "expiration_status",
    "expiration_reason",
    "evaluated_at",
}

EXPECTED_EXISTING_FUNCTIONS = {
    "calculate_body_store_retention_result_v1",
    "evaluate_body_store_retention_policy_v1",
}

function_matches = []
field_matches = set()
existing_retention_functions = []
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
            filename=str(
                path
            ),
        )

    except Exception as exc:
        syntax_failures.append(
            f"{path.relative_to(PROJECT_ROOT)} : {exc}"
        )

        continue

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
            lowered_name = node.name.casefold()

            if any(
                term in lowered_name
                for term in EXPIRATION_FUNCTION_TERMS
            ):
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

            if node.name in EXPECTED_EXISTING_FUNCTIONS:
                existing_retention_functions.append(
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
            ast.Constant,
        ):
            if (
                isinstance(
                    node.value,
                    str,
                )
                and node.value
                in EXPIRATION_FIELDS
            ):
                field_matches.add(
                    node.value
                )


dedicated_manager_path = (
    PACKAGE_ROOT
    / "body_store_expiration_manager_v1.py"
)

dedicated_manager_exists = (
    dedicated_manager_path.is_file()
)


if dedicated_manager_exists:
    classification = (
        "BODY_STORE_EXPIRATION_MANAGER_EXISTS"
    )

elif function_matches:
    classification = (
        "PARTIAL_EXPIRATION_LOGIC_FOUND"
    )

elif existing_retention_functions:
    classification = (
        "RETENTION_EXPIRATION_SIGNALS_EXIST"
    )

else:
    classification = (
        "NO_BODY_STORE_EXPIRATION_MANAGER_FOUND"
    )


print()
print("=" * 112)
print(
    "BODY STORE EXPIRATION MANAGER — READ-ONLY DISCOVERY"
)
print("=" * 112)
print()

print(
    "Classification:",
    classification,
)

print()

print(
    "Dedicated Expiration Manager exists:",
    dedicated_manager_exists,
)

print()

print(
    "Expiration functions found:",
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
    "Existing retention evaluation functions:",
    len(
        existing_retention_functions
    ),
)

for item in existing_retention_functions:
    print(
        f"  {item['path']}:{item['line']}:{item['name']}"
    )

print()

print(
    "Expiration fields found:",
    len(
        field_matches
    ),
)

for item in sorted(
    field_matches
):
    print(
        "  "
        + item
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
    for failure in syntax_failures:
        print(
            "  "
            + failure
        )

else:
    print(
        "  None"
    )

print()

if syntax_failures:
    print(
        "BODY STORE EXPIRATION MANAGER SCAN: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE EXPIRATION MANAGER SCAN: PASS"
)

print("=" * 112)
