from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


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
    / "body_store_writer_v1.py",

    PACKAGE_ROOT
    / "body_store_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_repository_v1.py",

    PACKAGE_ROOT
    / "body_store_runtime_v1.py",

    PACKAGE_ROOT
    / "body_store_worker_v1.py",

    PACKAGE_ROOT
    / "body_store_queue_v1.py",

    PACKAGE_ROOT
    / "body_store_runtime_registration_v1.py",
]

STATE_FIELD_TERMS = {
    "status",
    "state",
    "lifecycle_state",
    "body_state",
    "record_state",
}

VERSION_FIELD_TERMS = {
    "version",
    "body_version",
    "content_version",
    "revision",
    "supersedes",
    "superseded_by",
    "previous_version",
}

INTEGRITY_FIELD_TERMS = {
    "verified",
    "verification_status",
    "integrity_status",
    "content_hash",
    "corrupted",
    "quarantined",
    "quarantine",
}

IDENTITY_FIELD_TERMS = {
    "workspace_id",
    "document_id",
    "article_id",
    "body_id",
    "body_ref",
    "canonical_url",
    "content_hash",
}

TIMESTAMP_FIELD_TERMS = {
    "created_at",
    "updated_at",
    "stored_at",
    "verified_at",
    "archived_at",
    "deleted_at",
    "restored_at",
}

PERSISTENCE_CALLS = {
    "write_text",
    "write_bytes",
    "replace",
    "rename",
    "unlink",
    "mkdir",
    "rmdir",
}

REPOSITORY_OPERATION_TERMS = {
    "store",
    "read",
    "verify",
    "metadata",
    "list",
    "delete",
    "archive",
    "restore",
}

REPORT_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_scans"
    / "body_store_lifecycle_state_contract_v1.json"
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


def collect_string_keys(
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

all_state_fields = set()
all_version_fields = set()
all_integrity_fields = set()
all_identity_fields = set()
all_timestamp_fields = set()

repository_functions = []
manager_functions = []
runtime_functions = []
filesystem_calls = []
lifecycle_references = []


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

    keys = collect_string_keys(
        tree
    )

    state_fields = sorted(
        keys
        & STATE_FIELD_TERMS
    )

    version_fields = sorted(
        keys
        & VERSION_FIELD_TERMS
    )

    integrity_fields = sorted(
        keys
        & INTEGRITY_FIELD_TERMS
    )

    identity_fields = sorted(
        keys
        & IDENTITY_FIELD_TERMS
    )

    timestamp_fields = sorted(
        keys
        & TIMESTAMP_FIELD_TERMS
    )

    all_state_fields.update(
        state_fields
    )

    all_version_fields.update(
        version_fields
    )

    all_integrity_fields.update(
        integrity_fields
    )

    all_identity_fields.update(
        identity_fields
    )

    all_timestamp_fields.update(
        timestamp_fields
    )

    functions = []
    local_filesystem_calls = []

    lowered_source = source.casefold()

    if any(
        term in lowered_source
        for term in (
            "lifecycle",
            "superseded",
            "archived",
            "quarantined",
            "pending_deletion",
            "restored",
        )
    ):
        lifecycle_references.append(
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
            signature = render_signature(
                node
            )

            functions.append(
                {
                    "name":
                        node.name,

                    "line":
                        node.lineno,

                    "signature":
                        signature,
                }
            )

            lowered_name = (
                node.name.casefold()
            )

            if (
                "repository"
                in path.name.casefold()
                and any(
                    term in lowered_name
                    for term
                    in REPOSITORY_OPERATION_TERMS
                )
            ):
                repository_functions.append(
                    {
                        "path":
                            relative(
                                path
                            ),

                        "line":
                            node.lineno,

                        "signature":
                            signature,
                    }
                )

            if (
                "manager"
                in path.name.casefold()
                and any(
                    term in lowered_name
                    for term
                    in REPOSITORY_OPERATION_TERMS
                )
            ):
                manager_functions.append(
                    {
                        "path":
                            relative(
                                path
                            ),

                        "line":
                            node.lineno,

                        "signature":
                            signature,
                    }
                )

            if (
                "runtime"
                in path.name.casefold()
                and any(
                    term in lowered_name
                    for term
                    in REPOSITORY_OPERATION_TERMS
                )
            ):
                runtime_functions.append(
                    {
                        "path":
                            relative(
                                path
                            ),

                        "line":
                            node.lineno,

                        "signature":
                            signature,
                    }
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

            if final_name in PERSISTENCE_CALLS:
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

                filesystem_calls.append(
                    item
                )

                local_filesystem_calls.append(
                    item
                )

    report.update(
        {
            "dictionary_keys":
                sorted(
                    keys
                ),

            "state_fields":
                state_fields,

            "version_fields":
                version_fields,

            "integrity_fields":
                integrity_fields,

            "identity_fields":
                identity_fields,

            "timestamp_fields":
                timestamp_fields,

            "functions":
                functions,

            "filesystem_calls":
                local_filesystem_calls,
        }
    )

    file_reports.append(
        report
    )


dedicated_state_manager_exists = any(
    path.is_file()
    for path in (
        PACKAGE_ROOT
        / "body_store_lifecycle_state_manager_v1.py",

        PACKAGE_ROOT
        / "body_store_lifecycle_manager_v1.py",
    )
)


if dedicated_state_manager_exists:
    classification = (
        "BODY_STORE_LIFECYCLE_STATE_MANAGER_EXISTS"
    )

elif all_state_fields or lifecycle_references:
    classification = (
        "PARTIAL_BODY_STORE_STATE_REFERENCES_FOUND"
    )

else:
    classification = (
        "NO_BODY_STORE_LIFECYCLE_STATE_MANAGER_FOUND"
    )


report = {
    "schema_version":
        "body_store_lifecycle_state_contract_scan_v1",

    "classification":
        classification,

    "dedicated_state_manager_exists":
        dedicated_state_manager_exists,

    "state_fields":
        sorted(
            all_state_fields
        ),

    "version_fields":
        sorted(
            all_version_fields
        ),

    "integrity_fields":
        sorted(
            all_integrity_fields
        ),

    "identity_fields":
        sorted(
            all_identity_fields
        ),

    "timestamp_fields":
        sorted(
            all_timestamp_fields
        ),

    "repository_functions":
        repository_functions,

    "manager_functions":
        manager_functions,

    "runtime_functions":
        runtime_functions,

    "lifecycle_reference_files":
        sorted(
            set(
                lifecycle_references
            )
        ),

    "filesystem_calls":
        filesystem_calls,

    "files":
        file_reports,

    "syntax_failures":
        syntax_failures,

    "read_only":
        True,

    "production_files_modified":
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
    "BODY STORE LIFECYCLE STATE MANAGER — CONTRACT DISCOVERY"
)
print("=" * 120)
print()

print(
    "Classification: "
    + classification
)

print()
print(
    "Existing state fields:"
)

if all_state_fields:
    for item in sorted(
        all_state_fields
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
    "Existing version/supersession fields:"
)

if all_version_fields:
    for item in sorted(
        all_version_fields
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
    "Existing integrity/quarantine fields:"
)

if all_integrity_fields:
    for item in sorted(
        all_integrity_fields
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
    "Existing identity fields:"
)

if all_identity_fields:
    for item in sorted(
        all_identity_fields
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
    "Existing timestamp fields:"
)

if all_timestamp_fields:
    for item in sorted(
        all_timestamp_fields
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
    "Repository operation functions: "
    + str(
        len(
            repository_functions
        )
    )
)

for item in repository_functions:
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
    "Manager operation functions: "
    + str(
        len(
            manager_functions
        )
    )
)

for item in manager_functions:
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
    "Runtime operation functions: "
    + str(
        len(
            runtime_functions
        )
    )
)

for item in runtime_functions:
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
    "Lifecycle-reference files: "
    + str(
        len(
            set(
                lifecycle_references
            )
        )
    )
)

for item in sorted(
    set(
        lifecycle_references
    )
):
    print(
        "  "
        + item
    )

print()
print(
    "Direct filesystem calls found: "
    + str(
        len(
            filesystem_calls
        )
    )
)

for item in filesystem_calls:
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
        "BODY STORE LIFECYCLE STATE CONTRACT SCAN: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE LIFECYCLE STATE CONTRACT SCAN: PASS"
)

print("=" * 120)
