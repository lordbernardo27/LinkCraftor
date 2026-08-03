from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

BODY_STORE_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
)

SERVER_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
)

TARGET_FILES = [
    BODY_STORE_ROOT
    / "body_store_lifecycle_state_manager_v1.py",

    BODY_STORE_ROOT
    / "body_store_state_transition_engine_v1.py",

    BODY_STORE_ROOT
    / "body_store_manager_v1.py",

    BODY_STORE_ROOT
    / "body_store_repository_v1.py",

    BODY_STORE_ROOT
    / "body_store_runtime_v1.py",

    SERVER_ROOT
    / "stores"
    / "source_lifecycle_control.py",

    SERVER_ROOT
    / "tms"
    / "attachment_lifecycle.py",

    SERVER_ROOT
    / "tms"
    / "attachment_orchestration.py",
]

RETENTION_FIELD_TERMS = {
    "retention_policy",
    "retention_policy_id",
    "retention_class",
    "retention_days",
    "retention_period_days",
    "retention_started_at",
    "retention_expires_at",
    "retain_until",
    "minimum_retention_until",
    "retention_status",
    "retention_reason",
}

HOLD_FIELD_TERMS = {
    "hold",
    "hold_type",
    "hold_reason",
    "hold_started_at",
    "hold_expires_at",
    "legal_hold",
    "operational_hold",
    "deletion_hold",
    "is_on_hold",
}

ELIGIBILITY_FIELD_TERMS = {
    "deletion_eligible",
    "eligible_for_deletion",
    "retention_satisfied",
    "retention_expired",
    "can_delete",
    "cleanup_eligible",
}

TIMESTAMP_FIELD_TERMS = {
    "created_at",
    "updated_at",
    "transitioned_at",
    "archived_at",
    "deleted_at",
    "restored_at",
    "expires_at",
    "retain_until",
}

RETENTION_FUNCTION_TERMS = {
    "retention",
    "retain",
    "hold",
    "deletion_eligible",
    "can_delete",
    "eligible_for_deletion",
}

POLICY_TERMS = {
    "policy",
    "retention",
    "hold",
    "minimum_days",
    "default_days",
}

EXPECTED_STATES = {
    "ACTIVE",
    "SUPERSEDED",
    "RETAINED",
    "ARCHIVED",
    "QUARANTINED",
    "PENDING_DELETION",
    "DELETED",
    "RESTORED",
}

REPORT_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_scans"
    / "body_store_retention_policy_contract_v1.json"
)


def relative(
    path: Path,
) -> str:
    return path.relative_to(
        PROJECT_ROOT
    ).as_posix()


def render_signature(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> str:
    arguments = []

    positional = [
        *node.args.posonlyargs,
        *node.args.args,
    ]

    default_offset = (
        len(
            positional
        )
        - len(
            node.args.defaults
        )
    )

    for index, argument in enumerate(
        positional
    ):
        item = argument.arg

        if index >= default_offset:
            default = node.args.defaults[
                index
                - default_offset
            ]

            try:
                item += (
                    "="
                    + ast.unparse(
                        default
                    )
                )

            except Exception:
                item += "=<default>"

        arguments.append(
            item
        )

    if node.args.vararg:
        arguments.append(
            "*"
            + node.args.vararg.arg
        )

    elif node.args.kwonlyargs:
        arguments.append(
            "*"
        )

    for index, argument in enumerate(
        node.args.kwonlyargs
    ):
        item = argument.arg

        default = node.args.kw_defaults[
            index
        ]

        if default is not None:
            try:
                item += (
                    "="
                    + ast.unparse(
                        default
                    )
                )

            except Exception:
                item += "=<default>"

        arguments.append(
            item
        )

    if node.args.kwarg:
        arguments.append(
            "**"
            + node.args.kwarg.arg
        )

    return (
        node.name
        + "("
        + ", ".join(
            arguments
        )
        + ")"
    )


def collect_dictionary_keys(
    tree: ast.AST,
) -> set[str]:
    keys = set()

    for node in ast.walk(
        tree
    ):
        if not isinstance(
            node,
            ast.Dict,
        ):
            continue

        for key in node.keys:
            if (
                isinstance(
                    key,
                    ast.Constant,
                )
                and isinstance(
                    key.value,
                    str,
                )
            ):
                keys.add(
                    key.value
                )

    return keys


def collect_string_constants(
    tree: ast.AST,
) -> set[str]:
    values = set()

    for node in ast.walk(
        tree
    ):
        if (
            isinstance(
                node,
                ast.Constant,
            )
            and isinstance(
                node.value,
                str,
            )
        ):
            values.add(
                node.value
            )

    return values


file_reports = []
syntax_failures = []

retention_fields = set()
hold_fields = set()
eligibility_fields = set()
timestamp_fields = set()
retention_functions = []
possible_policy_definitions = []
body_store_retention_functions = []
external_retention_functions = []
canonical_states_found = set()


for path in TARGET_FILES:
    report: dict[str, Any] = {
        "path":
            relative(
                path
            ),

        "exists":
            path.is_file(),
    }

    if not path.is_file():
        file_reports.append(
            report
        )

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
            relative(
                path
            )
            + ": "
            + str(
                exc
            )
        )

        continue

    keys = collect_dictionary_keys(
        tree
    )

    strings = collect_string_constants(
        tree
    )

    discovered_retention_fields = (
        keys
        & RETENTION_FIELD_TERMS
    )

    discovered_hold_fields = (
        keys
        & HOLD_FIELD_TERMS
    )

    discovered_eligibility_fields = (
        keys
        & ELIGIBILITY_FIELD_TERMS
    )

    discovered_timestamp_fields = (
        keys
        & TIMESTAMP_FIELD_TERMS
    )

    discovered_states = (
        strings
        & EXPECTED_STATES
    )

    retention_fields.update(
        discovered_retention_fields
    )

    hold_fields.update(
        discovered_hold_fields
    )

    eligibility_fields.update(
        discovered_eligibility_fields
    )

    timestamp_fields.update(
        discovered_timestamp_fields
    )

    canonical_states_found.update(
        discovered_states
    )

    local_functions = []
    local_policies = []

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
            lowered_name = (
                node.name.casefold()
            )

            signature = render_signature(
                node
            )

            local_functions.append(
                {
                    "name":
                        node.name,

                    "line":
                        node.lineno,

                    "signature":
                        signature,
                }
            )

            if any(
                term in lowered_name
                for term in RETENTION_FUNCTION_TERMS
            ):
                item = {
                    "path":
                        relative(
                            path
                        ),

                    "line":
                        node.lineno,

                    "name":
                        node.name,

                    "signature":
                        signature,
                }

                retention_functions.append(
                    item
                )

                if (
                    "universal_article_body_store"
                    in path.parts
                ):
                    body_store_retention_functions.append(
                        item
                    )

                else:
                    external_retention_functions.append(
                        item
                    )

        elif isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            try:
                rendered = ast.unparse(
                    node
                )

            except Exception:
                rendered = ""

            lowered_rendered = (
                rendered.casefold()
            )

            if any(
                term in lowered_rendered
                for term in POLICY_TERMS
            ):
                item = {
                    "path":
                        relative(
                            path
                        ),

                    "line":
                        node.lineno,

                    "code":
                        rendered[
                            :1200
                        ],
                }

                possible_policy_definitions.append(
                    item
                )

                local_policies.append(
                    item
                )

    report.update(
        {
            "retention_fields":
                sorted(
                    discovered_retention_fields
                ),

            "hold_fields":
                sorted(
                    discovered_hold_fields
                ),

            "eligibility_fields":
                sorted(
                    discovered_eligibility_fields
                ),

            "timestamp_fields":
                sorted(
                    discovered_timestamp_fields
                ),

            "canonical_states":
                sorted(
                    discovered_states
                ),

            "functions":
                local_functions,

            "possible_policy_definitions":
                local_policies,
        }
    )

    file_reports.append(
        report
    )


dedicated_manager_path = (
    BODY_STORE_ROOT
    / "body_store_retention_policy_manager_v1.py"
)

dedicated_manager_exists = (
    dedicated_manager_path.is_file()
)


if dedicated_manager_exists:
    classification = (
        "BODY_STORE_RETENTION_POLICY_MANAGER_EXISTS"
    )

elif (
    body_store_retention_functions
    or retention_fields
    or hold_fields
):
    classification = (
        "PARTIAL_BODY_STORE_RETENTION_REFERENCES_FOUND"
    )

else:
    classification = (
        "NO_BODY_STORE_RETENTION_POLICY_MANAGER_FOUND"
    )


report = {
    "schema_version":
        "body_store_retention_policy_contract_scan_v1",

    "classification":
        classification,

    "dedicated_retention_policy_manager_exists":
        dedicated_manager_exists,

    "retention_fields":
        sorted(
            retention_fields
        ),

    "hold_fields":
        sorted(
            hold_fields
        ),

    "eligibility_fields":
        sorted(
            eligibility_fields
        ),

    "timestamp_fields":
        sorted(
            timestamp_fields
        ),

    "canonical_states_found":
        sorted(
            canonical_states_found
        ),

    "body_store_retention_functions":
        body_store_retention_functions,

    "external_retention_functions":
        external_retention_functions,

    "possible_policy_definitions":
        possible_policy_definitions,

    "files":
        file_reports,

    "syntax_failures":
        syntax_failures,

    "read_only":
        True,

    "production_files_modified":
        False,

    "lifecycle_records_modified":
        False,

    "body_store_modified":
        False,

    "queue_modified":
        False,

    "runtime_registrations_modified":
        False,
}


REPORT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT_PATH.write_text(
    json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 120)
print(
    "BODY STORE RETENTION POLICY MANAGER — CONTRACT DISCOVERY"
)
print("=" * 120)
print()

print(
    "Classification: "
    + classification
)

print()
print(
    "Dedicated Retention Policy Manager exists: "
    + str(
        dedicated_manager_exists
    )
)

print()
print(
    "Existing retention fields:"
)

if retention_fields:
    for item in sorted(
        retention_fields
    ):
        print(
            "  "
            + item
        )

else:
    print(
        "  None"
    )

print()
print(
    "Existing hold fields:"
)

if hold_fields:
    for item in sorted(
        hold_fields
    ):
        print(
            "  "
            + item
        )

else:
    print(
        "  None"
    )

print()
print(
    "Existing deletion-eligibility fields:"
)

if eligibility_fields:
    for item in sorted(
        eligibility_fields
    ):
        print(
            "  "
            + item
        )

else:
    print(
        "  None"
    )

print()
print(
    "Existing lifecycle timestamps:"
)

if timestamp_fields:
    for item in sorted(
        timestamp_fields
    ):
        print(
            "  "
            + item
        )

else:
    print(
        "  None"
    )

print()
print(
    "Body Store retention functions: "
    + str(
        len(
            body_store_retention_functions
        )
    )
)

for item in body_store_retention_functions:
    print(
        "  "
        + item[
            "path"
        ]
        + ":"
        + str(
            item[
                "line"
            ]
        )
        + ":"
        + item[
            "signature"
        ]
    )

print()
print(
    "External retention functions: "
    + str(
        len(
            external_retention_functions
        )
    )
)

for item in external_retention_functions:
    print(
        "  "
        + item[
            "path"
        ]
        + ":"
        + str(
            item[
                "line"
            ]
        )
        + ":"
        + item[
            "signature"
        ]
    )

print()
print(
    "Possible existing policy definitions: "
    + str(
        len(
            possible_policy_definitions
        )
    )
)

for item in possible_policy_definitions:
    print(
        "  "
        + item[
            "path"
        ]
        + ":"
        + str(
            item[
                "line"
            ]
        )
    )

    print(
        "    "
        + item[
            "code"
        ].replace(
            "\n",
            " "
        )
    )

print()
print(
    "Canonical lifecycle states found: "
    + str(
        len(
            canonical_states_found
        )
    )
)

for state in sorted(
    canonical_states_found
):
    print(
        "  "
        + state
    )

print()
print(
    "Report:"
)

print(
    "  "
    + str(
        REPORT_PATH
    )
)

print()
print(
    "Production files modified:       False"
)

print(
    "Lifecycle records modified:      False"
)

print(
    "Body Store modified:             False"
)

print(
    "Body Store Queue modified:       False"
)

print(
    "Runtime registrations modified:  0"
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
        "BODY STORE RETENTION POLICY CONTRACT SCAN: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE RETENTION POLICY CONTRACT SCAN: PASS"
)

print("=" * 120)
