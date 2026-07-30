"""Read-only scan for an existing Universal Article Body Store management layer."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

WORKSPACE_ID = "ws_whattoexpect_com"

SERVER_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
)

DATA_ROOT = (
    SERVER_ROOT
    / "data"
)

BODY_STORE_PACKAGE = (
    SERVER_ROOT
    / "universal_article_body_store"
)

BODY_STORE_OUTPUT = (
    DATA_ROOT
    / "universal_article_body_store"
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "universal_article_body_store_management_layer_scan_v1.json"
)

CANDIDATE_FILENAMES = {
    "body_store_manager.py",
    "body_store_manager_v1.py",
    "body_store_repository.py",
    "body_store_repository_v1.py",
    "body_store_reader.py",
    "body_store_reader_v1.py",
    "body_store_verifier.py",
    "body_store_verifier_v1.py",
    "universal_article_body_store_manager.py",
    "universal_article_body_store_repository.py",
}

MANAGEMENT_FUNCTION_NAMES = {
    "get_body",
    "read_body",
    "load_body",
    "find_body",
    "locate_body",
    "body_exists",
    "verify_body",
    "verify_stored_body",
    "list_bodies",
    "list_workspace_bodies",
    "delete_body",
    "purge_body",
    "remove_body",
    "get_body_metadata",
}

REQUIRED_CAPABILITIES = {
    "read_body",
    "verify_integrity",
    "check_exists",
    "workspace_isolation",
    "path_boundary_validation",
    "list_workspace_bodies",
    "missing_body_detection",
    "corruption_detection",
}

FORBIDDEN_ACTIVE_CAPABILITIES = {
    "automatic_delete",
    "semantic_processing",
    "runtime_registration",
    "queue_execution",
    "uucd_persistence",
    "body_rewrite",
}

READ_CALLS = {
    "read_text",
    "read_bytes",
    "open",
}

DELETE_CALLS = {
    "unlink",
    "remove",
    "rmtree",
}

WRITE_CALLS = {
    "write_text",
    "write_bytes",
    "replace",
    "rename",
}

PATH_SECURITY_CALLS = {
    "resolve",
    "relative_to",
    "is_relative_to",
}

HASH_CALLS = {
    "sha256",
    "hexdigest",
}

LIST_CALLS = {
    "glob",
    "rglob",
    "iterdir",
}

RUNTIME_TERMS = {
    "runtime_registration",
    "register_runtime",
    "enqueue",
    "dispatch",
    "create_job",
    "submit_job",
}

SEMANTIC_TERMS = {
    "embedding",
    "semantic",
    "reasoning",
    "topic_cluster",
    "entity_extraction",
}

UUCD_PERSISTENCE_TERMS = {
    "persist_uucd",
    "write_uucd",
    "save_uucd",
    "uucd_persistence",
}


def relative(
    path: Path,
) -> str:
    return path.resolve().relative_to(
        PROJECT_ROOT
    ).as_posix()


def call_name(
    node: ast.Call,
) -> str:
    if isinstance(
        node.func,
        ast.Name,
    ):
        return node.func.id

    if isinstance(
        node.func,
        ast.Attribute,
    ):
        return node.func.attr

    return ""


def source_matches(
    source: str,
    terms: set[str],
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):
        lowered = line.casefold()

        matched = sorted(
            term
            for term in terms
            if term.casefold() in lowered
        )

        if matched:
            matches.append(
                {
                    "line_number":
                        line_number,

                    "matched_terms":
                        matched,

                    "line":
                        line.strip()[:1500],
                }
            )

    return matches


candidate_files: list[Path] = []

if BODY_STORE_PACKAGE.exists():
    for path in BODY_STORE_PACKAGE.rglob(
        "*.py"
    ):
        if path.name in CANDIDATE_FILENAMES:
            candidate_files.append(
                path
            )

for path in SERVER_ROOT.rglob(
    "*.py"
):
    if any(
        part in {
            ".git",
            ".venv",
            "__pycache__",
            "backups",
            "runtime_backups",
            "node_modules",
        }
        for part in path.parts
    ):
        continue

    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    if (
        "universal_article_body_store"
        in source.casefold()
        and any(
            name.casefold()
            in source.casefold()
            for name in MANAGEMENT_FUNCTION_NAMES
        )
    ):
        candidate_files.append(
            path
        )


candidate_files = sorted(
    set(
        candidate_files
    ),
    key=lambda path: relative(
        path
    ),
)


results: list[dict[str, Any]] = []
failures: list[str] = []

aggregate = {
    "read_calls":
        0,

    "delete_calls":
        0,

    "write_calls":
        0,

    "path_security_calls":
        0,

    "hash_calls":
        0,

    "list_calls":
        0,

    "management_functions":
        set(),

    "runtime_matches":
        0,

    "semantic_matches":
        0,

    "uucd_persistence_matches":
        0,
}


for path in candidate_files:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="strict",
    )

    try:
        tree = ast.parse(
            source,
            filename=str(
                path
            ),
        )

    except SyntaxError as exc:
        failures.append(
            relative(
                path
            )
            + ": syntax error at line "
            + str(
                exc.lineno
            )
            + ": "
            + str(
                exc.msg
            )
        )

        continue

    functions = []
    calls = []

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
            functions.append(
                {
                    "name":
                        node.name,

                    "line":
                        node.lineno,
                }
            )

            if node.name in MANAGEMENT_FUNCTION_NAMES:
                aggregate[
                    "management_functions"
                ].add(
                    node.name
                )

        elif isinstance(
            node,
            ast.Call,
        ):
            name = call_name(
                node
            )

            if name:
                calls.append(
                    {
                        "name":
                            name,

                        "line":
                            node.lineno,
                    }
                )

                if name in READ_CALLS:
                    aggregate[
                        "read_calls"
                    ] += 1

                if name in DELETE_CALLS:
                    aggregate[
                        "delete_calls"
                    ] += 1

                if name in WRITE_CALLS:
                    aggregate[
                        "write_calls"
                    ] += 1

                if name in PATH_SECURITY_CALLS:
                    aggregate[
                        "path_security_calls"
                    ] += 1

                if name in HASH_CALLS:
                    aggregate[
                        "hash_calls"
                    ] += 1

                if name in LIST_CALLS:
                    aggregate[
                        "list_calls"
                    ] += 1

    runtime_matches = source_matches(
        source,
        RUNTIME_TERMS,
    )

    semantic_matches = source_matches(
        source,
        SEMANTIC_TERMS,
    )

    uucd_persistence_matches = source_matches(
        source,
        UUCD_PERSISTENCE_TERMS,
    )

    aggregate[
        "runtime_matches"
    ] += len(
        runtime_matches
    )

    aggregate[
        "semantic_matches"
    ] += len(
        semantic_matches
    )

    aggregate[
        "uucd_persistence_matches"
    ] += len(
        uucd_persistence_matches
    )

    results.append(
        {
            "path":
                relative(
                    path
                ),

            "functions":
                functions,

            "management_functions":
                sorted(
                    function[
                        "name"
                    ]
                    for function in functions
                    if function[
                        "name"
                    ]
                    in MANAGEMENT_FUNCTION_NAMES
                ),

            "read_calls":
                [
                    call
                    for call in calls
                    if call[
                        "name"
                    ]
                    in READ_CALLS
                ],

            "delete_calls":
                [
                    call
                    for call in calls
                    if call[
                        "name"
                    ]
                    in DELETE_CALLS
                ],

            "write_calls":
                [
                    call
                    for call in calls
                    if call[
                        "name"
                    ]
                    in WRITE_CALLS
                ],

            "path_security_calls":
                [
                    call
                    for call in calls
                    if call[
                        "name"
                    ]
                    in PATH_SECURITY_CALLS
                ],

            "hash_calls":
                [
                    call
                    for call in calls
                    if call[
                        "name"
                    ]
                    in HASH_CALLS
                ],

            "list_calls":
                [
                    call
                    for call in calls
                    if call[
                        "name"
                    ]
                    in LIST_CALLS
                ],

            "runtime_matches":
                runtime_matches,

            "semantic_matches":
                semantic_matches,

            "uucd_persistence_matches":
                uucd_persistence_matches,
        }
    )


detected_capabilities = {
    "read_body":
        aggregate[
            "read_calls"
        ] > 0,

    "verify_integrity":
        aggregate[
            "hash_calls"
        ] > 0,

    "check_exists":
        (
            "body_exists"
            in aggregate[
                "management_functions"
            ]
            or "find_body"
            in aggregate[
                "management_functions"
            ]
        ),

    "workspace_isolation":
        aggregate[
            "path_security_calls"
        ] > 0,

    "path_boundary_validation":
        aggregate[
            "path_security_calls"
        ] > 0,

    "list_workspace_bodies":
        (
            aggregate[
                "list_calls"
            ] > 0
            or "list_workspace_bodies"
            in aggregate[
                "management_functions"
            ]
        ),

    "missing_body_detection":
        (
            "body_exists"
            in aggregate[
                "management_functions"
            ]
            or "find_body"
            in aggregate[
                "management_functions"
            ]
        ),

    "corruption_detection":
        aggregate[
            "hash_calls"
        ] > 0,
}


forbidden_capabilities = {
    "automatic_delete":
        aggregate[
            "delete_calls"
        ] > 0,

    "semantic_processing":
        aggregate[
            "semantic_matches"
        ] > 0,

    "runtime_registration":
        aggregate[
            "runtime_matches"
        ] > 0,

    "queue_execution":
        aggregate[
            "runtime_matches"
        ] > 0,

    "uucd_persistence":
        aggregate[
            "uucd_persistence_matches"
        ] > 0,

    "body_rewrite":
        aggregate[
            "write_calls"
        ] > 0,
}


missing_required = sorted(
    capability
    for capability in REQUIRED_CAPABILITIES
    if detected_capabilities.get(
        capability
    ) is not True
)

active_forbidden = sorted(
    capability
    for capability in FORBIDDEN_ACTIVE_CAPABILITIES
    if forbidden_capabilities.get(
        capability
    ) is True
)


if (
    candidate_files
    and not missing_required
    and not active_forbidden
):
    classification = (
        "EXISTING_MANAGEMENT_LAYER_COMPLETE"
    )

elif candidate_files:
    classification = (
        "EXISTING_MANAGEMENT_CODE_INCOMPLETE_OR_MIXED"
    )

else:
    classification = (
        "NO_MANAGEMENT_LAYER_FOUND"
    )


report = {
    "schema_version":
        "universal_article_body_store_management_layer_scan_v1",

    "workspace_id":
        WORKSPACE_ID,

    "scan_mode":
        "READ_ONLY",

    "classification":
        classification,

    "candidate_file_count":
        len(
            candidate_files
        ),

    "candidate_files":
        results,

    "detected_capabilities":
        detected_capabilities,

    "missing_required_capabilities":
        missing_required,

    "forbidden_capabilities":
        forbidden_capabilities,

    "active_forbidden_capabilities":
        active_forbidden,

    "aggregate": {
        **aggregate,

        "management_functions":
            sorted(
                aggregate[
                    "management_functions"
                ]
            ),
    },

    "production_body_store_exists":
        BODY_STORE_OUTPUT.exists(),

    "source_files_modified":
        False,

    "data_files_modified":
        False,

    "body_store_modified":
        False,

    "runtime_state_modified":
        False,

    "failures":
        failures,
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
print("=" * 116)
print(
    "UNIVERSAL ARTICLE BODY STORE MANAGEMENT LAYER — READ-ONLY SCAN"
)
print("=" * 116)
print()

print(
    "Classification: "
    + classification
)

print()

print(
    "Candidate files found:                "
    + str(
        len(
            candidate_files
        )
    )
)

print(
    "Management functions found:           "
    + str(
        len(
            aggregate[
                "management_functions"
            ]
        )
    )
)

print()

print(
    "REQUIRED CAPABILITIES"
)

for name, detected in detected_capabilities.items():
    print(
        f"  {name:<42}"
        + (
            "FOUND"
            if detected
            else "MISSING"
        )
    )

print()
print(
    "FORBIDDEN ACTIVE CAPABILITIES"
)

for name, detected in forbidden_capabilities.items():
    print(
        f"  {name:<42}"
        + (
            "FOUND"
            if detected
            else "ABSENT"
        )
    )

print()
print(
    "CANDIDATE FILES"
)

if results:
    for result in results:
        print()
        print(
            "  "
            + result[
                "path"
            ]
        )

        print(
            "    Management functions: "
            + str(
                result[
                    "management_functions"
                ]
            )
        )

else:
    print(
        "  None"
    )

print()
print(
    "Production Body Store exists:         "
    + str(
        BODY_STORE_OUTPUT.exists()
    )
)

print(
    "Source files modified:                False"
)

print(
    "Data files modified:                  False"
)

print(
    "Body Store modified:                  False"
)

print(
    "Runtime state modified:               False"
)

print()
print(
    "FAILURES"
)

if failures:
    for failure in failures:
        print(
            "  - "
            + failure
        )

else:
    print(
        "  None"
    )

print()
print(
    "Scan report: "
    + str(
        REPORT_PATH
    )
)

print()

if failures:
    print(
        "BODY STORE MANAGEMENT LAYER SCAN: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE MANAGEMENT LAYER SCAN: PASS"
)

print(
    "The existing codebase was classified without creating, "
    "reading, modifying, or deleting any production Body Store body."
)

print("=" * 116)
