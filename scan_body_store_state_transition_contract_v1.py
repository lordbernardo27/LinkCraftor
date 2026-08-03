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

RUNTIME_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
)

TARGET_FILES = [
    BODY_STORE_ROOT
    / "body_store_lifecycle_state_manager_v1.py",

    BODY_STORE_ROOT
    / "body_store_manager_v1.py",

    BODY_STORE_ROOT
    / "body_store_repository_v1.py",

    BODY_STORE_ROOT
    / "body_store_runtime_v1.py",

    RUNTIME_ROOT
    / "runtime_lifecycle_manager.py",

    RUNTIME_ROOT
    / "runtime_schema"
    / "registry.py",

    RUNTIME_ROOT
    / "runtime_schema"
    / "ports.py",
]

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

TRANSITION_FUNCTION_TERMS = {
    "transition",
    "change_state",
    "set_state",
    "update_state",
    "move_state",
    "apply_transition",
}

TRANSITION_FIELD_TERMS = {
    "previous_state",
    "from_state",
    "current_state",
    "next_state",
    "to_state",
    "transitioned_at",
    "transition_reason",
    "transition_count",
    "transition_history",
    "lifecycle_events",
}

AUDIT_FIELD_TERMS = {
    "actor_type",
    "actor_id",
    "source",
    "state_reason",
    "created_at",
    "updated_at",
    "event_id",
}

ATOMIC_WRITE_CALLS = {
    "replace",
    "rename",
    "write_text",
    "write_bytes",
}

REPORT_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_scans"
    / "body_store_state_transition_contract_v1.json"
)


def relative(
    path: Path,
) -> str:
    return path.relative_to(
        PROJECT_ROOT
    ).as_posix()


def dotted_name(
    node: ast.AST,
) -> str:
    if isinstance(
        node,
        ast.Name,
    ):
        return node.id

    if isinstance(
        node,
        ast.Attribute,
    ):
        parent = dotted_name(
            node.value
        )

        return (
            parent
            + "."
            + node.attr
            if parent
            else node.attr
        )

    return ""


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


file_reports = []
syntax_failures = []

body_store_transition_functions = []
runtime_transition_functions = []
transition_maps = []
transition_fields = set()
audit_fields = set()
atomic_write_calls = []
state_constants = set()
lifecycle_manager_functions = []


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

    strings = collect_string_constants(
        tree
    )

    keys = collect_dictionary_keys(
        tree
    )

    discovered_states = {
        value
        for value in strings
        if value in EXPECTED_STATES
    }

    state_constants.update(
        discovered_states
    )

    discovered_transition_fields = (
        keys
        & TRANSITION_FIELD_TERMS
    )

    discovered_audit_fields = (
        keys
        & AUDIT_FIELD_TERMS
    )

    transition_fields.update(
        discovered_transition_fields
    )

    audit_fields.update(
        discovered_audit_fields
    )

    local_functions = []
    local_maps = []
    local_atomic_calls = []

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

            local_functions.append(
                {
                    "name":
                        node.name,

                    "line":
                        node.lineno,
                }
            )

            if any(
                term in lowered_name
                for term
                in TRANSITION_FUNCTION_TERMS
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
                }

                if (
                    "universal_article_body_store"
                    in path.parts
                ):
                    body_store_transition_functions.append(
                        item
                    )

                else:
                    runtime_transition_functions.append(
                        item
                    )

            if (
                path.name
                == "body_store_lifecycle_state_manager_v1.py"
            ):
                lifecycle_manager_functions.append(
                    {
                        "line":
                            node.lineno,

                        "name":
                            node.name,
                    }
                )

        elif isinstance(
            node,
            ast.Assign,
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

            if (
                "transition"
                in lowered_rendered
                or (
                    any(
                        state
                        in rendered
                        for state
                        in EXPECTED_STATES
                    )
                    and "{" in rendered
                )
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
                            :1000
                        ],
                }

                transition_maps.append(
                    item
                )

                local_maps.append(
                    item
                )

        elif isinstance(
            node,
            ast.Call,
        ):
            call_name = dotted_name(
                node.func
            )

            final_name = (
                call_name.rsplit(
                    ".",
                    1,
                )[
                    -1
                ]
                if call_name
                else ""
            )

            if final_name in ATOMIC_WRITE_CALLS:
                item = {
                    "path":
                        relative(
                            path
                        ),

                    "line":
                        node.lineno,

                    "call":
                        call_name,
                }

                atomic_write_calls.append(
                    item
                )

                local_atomic_calls.append(
                    item
                )

    report.update(
        {
            "states":
                sorted(
                    discovered_states
                ),

            "transition_fields":
                sorted(
                    discovered_transition_fields
                ),

            "audit_fields":
                sorted(
                    discovered_audit_fields
                ),

            "functions":
                local_functions,

            "possible_transition_maps":
                local_maps,

            "atomic_write_calls":
                local_atomic_calls,
        }
    )

    file_reports.append(
        report
    )


dedicated_engine_path = (
    BODY_STORE_ROOT
    / "body_store_state_transition_engine_v1.py"
)

dedicated_engine_exists = (
    dedicated_engine_path.is_file()
)


if dedicated_engine_exists:
    classification = (
        "BODY_STORE_STATE_TRANSITION_ENGINE_EXISTS"
    )

elif (
    body_store_transition_functions
    or transition_maps
):
    classification = (
        "PARTIAL_BODY_STORE_TRANSITION_LOGIC_FOUND"
    )

else:
    classification = (
        "NO_BODY_STORE_STATE_TRANSITION_ENGINE_FOUND"
    )


report = {
    "schema_version":
        "body_store_state_transition_contract_scan_v1",

    "classification":
        classification,

    "dedicated_transition_engine_exists":
        dedicated_engine_exists,

    "canonical_states_found":
        sorted(
            state_constants
            & EXPECTED_STATES
        ),

    "all_canonical_states_found":
        EXPECTED_STATES
        <= state_constants,

    "body_store_transition_functions":
        body_store_transition_functions,

    "runtime_transition_functions":
        runtime_transition_functions,

    "possible_transition_maps":
        transition_maps,

    "transition_fields":
        sorted(
            transition_fields
        ),

    "audit_fields":
        sorted(
            audit_fields
        ),

    "atomic_write_calls":
        atomic_write_calls,

    "lifecycle_state_manager_functions":
        lifecycle_manager_functions,

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
    "BODY STORE STATE TRANSITION ENGINE — CONTRACT DISCOVERY"
)
print("=" * 120)
print()

print(
    "Classification: "
    + classification
)

print()
print(
    "Dedicated transition engine exists: "
    + str(
        dedicated_engine_exists
    )
)

print()
print(
    "Canonical states found: "
    + str(
        len(
            state_constants
            & EXPECTED_STATES
        )
    )
)

for state in sorted(
    state_constants
    & EXPECTED_STATES
):
    print(
        "  "
        + state
    )

print()
print(
    "All eight canonical states found: "
    + str(
        EXPECTED_STATES
        <= state_constants
    )
)

print()
print(
    "Body Store transition functions: "
    + str(
        len(
            body_store_transition_functions
        )
    )
)

for item in body_store_transition_functions:
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
            "name"
        ]
    )

print()
print(
    "General Runtime transition functions: "
    + str(
        len(
            runtime_transition_functions
        )
    )
)

for item in runtime_transition_functions:
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
            "name"
        ]
    )

print()
print(
    "Possible transition maps: "
    + str(
        len(
            transition_maps
        )
    )
)

for item in transition_maps:
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
    "Existing transition fields:"
)

if transition_fields:
    for field in sorted(
        transition_fields
    ):
        print(
            "  "
            + field
        )

else:
    print(
        "  None"
    )

print()
print(
    "Existing audit fields:"
)

if audit_fields:
    for field in sorted(
        audit_fields
    ):
        print(
            "  "
            + field
        )

else:
    print(
        "  None"
    )

print()
print(
    "Atomic write calls: "
    + str(
        len(
            atomic_write_calls
        )
    )
)

for item in atomic_write_calls:
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
            "call"
        ]
    )

print()
print(
    "Lifecycle State Manager functions:"
)

for item in lifecycle_manager_functions:
    print(
        "  "
        + str(
            item[
                "line"
            ]
        )
        + ":"
        + item[
            "name"
        ]
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
        "BODY STORE STATE TRANSITION CONTRACT SCAN: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE STATE TRANSITION CONTRACT SCAN: PASS"
)

print("=" * 120)
