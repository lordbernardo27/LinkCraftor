from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

ENGINE_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
    / "body_store_retention_policy_engine_v1.py"
)

if not ENGINE_PATH.is_file():
    raise SystemExit(
        "Retention Policy Engine not found."
    )

source = ENGINE_PATH.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

tree = ast.parse(
    source,
    filename=str(
        ENGINE_PATH
    ),
)

evaluation_function_found = False

required_fields = {
    "deletion_eligible",
    "retention_expired",
    "retention_satisfied",
    "eligibility_reason",
}

found_fields = set()

for node in ast.walk(tree):

    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    ):
        if (
            node.name
            == "evaluate_body_store_deletion_eligibility_v1"
        ):
            evaluation_function_found = True

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
            in required_fields
        ):
            found_fields.add(
                node.value
            )

print()
print("=" * 100)
print(
    "BODY STORE DELETION ELIGIBILITY DISCOVERY"
)
print("=" * 100)
print()

print(
    "Deletion eligibility function:",
    evaluation_function_found,
)

print()

print(
    "Fields discovered:",
    len(found_fields),
)

for item in sorted(found_fields):
    print(
        "  "
        + item
    )

print()
print(
    "Production modified: False"
)
print()

if not evaluation_function_found:
    print(
        "BODY STORE DELETION ELIGIBILITY SCAN: FAIL"
    )
    raise SystemExit(1)

print(
    "BODY STORE DELETION ELIGIBILITY SCAN: PASS"
)

print("=" * 100)
