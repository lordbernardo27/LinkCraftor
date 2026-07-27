"""Remove the final active dependencies on retired UUCD workers."""

from __future__ import annotations

import ast
import hashlib
import json
import shutil
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

BACKUP_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor\backend\server\backups\final_legacy_uucd_dependency_cleanup_20260727_000029"
).resolve()

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "final_legacy_uucd_dependency_cleanup_v1.json"
)

ORCHESTRATION_ROUTES = (
    SERVER_ROOT
    / "orchestration"
    / "routes.py"
)

SITE_READER = (
    SERVER_ROOT
    / "routes"
    / "site_reader.py"
)

CANONICAL_REBUILD_MANAGER = (
    SERVER_ROOT
    / "runtime"
    / "canonical_environment_rebuild_manager.py"
)

TARGETS = {
    "orchestration_routes":
        ORCHESTRATION_ROUTES,

    "site_reader":
        SITE_READER,

    "canonical_environment_rebuild_manager":
        CANONICAL_REBUILD_MANAGER,
}

PROTECTED_PATHS = {
    "wuc_package": (
        SERVER_ROOT
        / "website_unified_content"
    ),

    "uploaded_document_unified_content": (
        SERVER_ROOT
        / "stores"
        / "uploaded_document_unified_content.py"
    ),

    "universal_article_body_store_code": (
        SERVER_ROOT
        / "stores"
        / "universal_article_body_store.py"
    ),

    "uucd_body_store_certification_code": (
        SERVER_ROOT
        / "stores"
        / "uucd_body_store_certification.py"
    ),

    "source_lifecycle_control": (
        SERVER_ROOT
        / "stores"
        / "source_lifecycle_control.py"
    ),

    "universal_knowledge_orchestrator": (
        SERVER_ROOT
        / "jobs"
        / "universal_knowledge_orchestrator.py"
    ),

    "udare_store": (
        DATA_ROOT
        / "udare_store"
        / WORKSPACE_ID
    ),

    "article_validation_evidence": (
        DATA_ROOT
        / "article_validation_evidence"
        / WORKSPACE_ID
    ),

    "wuc_evidence": (
        DATA_ROOT
        / "website_unified_content_evidence"
        / WORKSPACE_ID
    ),

    "runtime_registry": (
        DATA_ROOT
        / "runtime"
        / "universal_runtime_registration"
        / "runtime_registration_registry.json"
    ),
}

RETIRED_REFERENCE_TERMS = {
    "from .worker import",
    "run_one_job",
    "worker_health",
    "live_route_orchestration_hooks",
    "enqueue_and_run_website_ingestion_job_v1",
    "registry_driven_canonical_rebuild_manager",
    "universal_knowledge_worker",
    "universal_knowledge_queue_runner",
    "universal_unified_content_document_convergence",
    "build_and_write_uucd_from_uduc_v1",
    "automatic_canonical_rebuild_runner",
}

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "backups",
    "runtime_backups",
    "node_modules",
}


def ensure_inside_project(
    path: Path,
) -> None:
    try:
        path.resolve().relative_to(
            PROJECT_ROOT
        )

    except ValueError as exc:
        raise RuntimeError(
            "Refusing to operate outside LinkCraftor: "
            + str(
                path
            )
        ) from exc


def relative(
    path: Path,
) -> str:
    try:
        return (
            path.resolve()
            .relative_to(
                PROJECT_ROOT
            )
            .as_posix()
        )

    except ValueError:
        return str(
            path.resolve()
        )


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:
        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                block
            )

    return digest.hexdigest()


def fingerprint(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    if not path.exists():
        digest.update(
            b"ABSENT"
        )

        return digest.hexdigest()

    if path.is_file():
        return sha256_file(
            path
        )

    for file_path in sorted(
        (
            candidate
            for candidate in path.rglob(
                "*"
            )
            if candidate.is_file()
        ),
        key=lambda candidate: (
            candidate.relative_to(
                path
            ).as_posix()
        ),
    ):
        digest.update(
            file_path.relative_to(
                path
            ).as_posix().encode(
                "utf-8"
            )
        )

        digest.update(
            b"\x00"
        )

        digest.update(
            sha256_file(
                file_path
            ).encode(
                "ascii"
            )
        )

        digest.update(
            b"\n"
        )

    return digest.hexdigest()


def backup_file(
    source: Path,
) -> Path:
    ensure_inside_project(
        source
    )

    destination = (
        BACKUP_ROOT
        / source.resolve().relative_to(
            PROJECT_ROOT
        )
    )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        source,
        destination,
    )

    if sha256_file(
        source
    ) != sha256_file(
        destination
    ):
        raise RuntimeError(
            "Backup verification failed: "
            + str(
                source
            )
        )

    return destination


def excluded(
    path: Path,
) -> bool:
    return any(
        part in EXCLUDED_PARTS
        for part in path.parts
    )


def indentation_of(
    line: str,
) -> str:
    return line[
        :len(
            line
        )
        - len(
            line.lstrip()
        )
    ]


def apply_line_edits(
    source: str,
    edits: list[
        tuple[
            int,
            int,
            list[str],
        ]
    ],
) -> str:
    lines = source.splitlines(
        keepends=False
    )

    for start_line, end_line, replacement in sorted(
        edits,
        key=lambda item: (
            item[
                0
            ]
        ),
        reverse=True,
    ):
        lines[
            start_line - 1:
            end_line
        ] = replacement

    return "\n".join(
        lines
    ).rstrip() + "\n"


def node_contains_names(
    node: ast.AST,
    names: set[str],
) -> bool:
    return any(
        isinstance(
            child,
            ast.Name,
        )
        and child.id
        in names
        for child in ast.walk(
            node
        )
    )


def write_json(
    path: Path,
    payload: dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


print()
print("=" * 112)
print(
    "FINAL LEGACY UUCD DEPENDENCY CLEANUP"
)
print("=" * 112)
print()

failures: list[str] = []
changes: list[
    dict[str, Any]
] = []

BACKUP_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

for name, path in {
    **TARGETS,
    **PROTECTED_PATHS,
}.items():
    if not path.exists():
        failures.append(
            "Required path is missing before cleanup: "
            + name
            + " -> "
            + str(
                path
            )
        )

if failures:
    for failure in failures:
        print(
            "FAIL: "
            + failure
        )

    raise SystemExit(1)


protected_before = {
    name: fingerprint(
        path
    )
    for name, path
    in PROTECTED_PATHS.items()
}


for name, path in TARGETS.items():
    backup = backup_file(
        path
    )

    changes.append(
        {
            "action":
                "BACKUP",

            "target":
                name,

            "path":
                relative(
                    path
                ),

            "backup":
                str(
                    backup
                ),
        }
    )


# ==================================================================
# 1. orchestration/routes.py
# Remove the retired worker import and the route functions that call
# run_one_job() or worker_health().
# ==================================================================

source = ORCHESTRATION_ROUTES.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

tree = ast.parse(
    source,
    filename=str(
        ORCHESTRATION_ROUTES
    ),
)

edits: list[
    tuple[
        int,
        int,
        list[str],
    ]
] = []

for node in tree.body:
    if isinstance(
        node,
        ast.ImportFrom,
    ):
        module = str(
            node.module or ""
        )

        imported_names = {
            alias.name
            for alias in node.names
        }

        if (
            module == "worker"
            and imported_names
            & {
                "run_one_job",
                "worker_health",
            }
        ):
            edits.append(
                (
                    node.lineno,
                    node.end_lineno
                    or node.lineno,
                    [],
                )
            )

    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    ):
        if node_contains_names(
            node,
            {
                "run_one_job",
                "worker_health",
            },
        ):
            start_line = (
                min(
                    (
                        decorator.lineno
                        for decorator
                        in node.decorator_list
                    ),
                    default=node.lineno,
                )
            )

            edits.append(
                (
                    start_line,
                    node.end_lineno
                    or node.lineno,
                    [],
                )
            )

if not edits:
    failures.append(
        "No retired worker import or route functions were found "
        "in orchestration/routes.py."
    )

else:
    updated = apply_line_edits(
        source,
        edits,
    )

    ORCHESTRATION_ROUTES.write_text(
        updated,
        encoding="utf-8",
    )

    changes.append(
        {
            "action":
                "REMOVE_RETIRED_ORCHESTRATION_WORKER_ROUTES",

            "path":
                relative(
                    ORCHESTRATION_ROUTES
                ),

            "edit_count":
                len(
                    edits
                ),
        }
    )


# ==================================================================
# 2. routes/site_reader.py
# Remove the retired hook import. Replace only the statement calling
# enqueue_and_run_website_ingestion_job_v1 with a non-executing status.
# ==================================================================

source = SITE_READER.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

tree = ast.parse(
    source,
    filename=str(
        SITE_READER
    ),
)

edits = []

for node in ast.walk(
    tree
):
    if isinstance(
        node,
        ast.ImportFrom,
    ):
        module = str(
            node.module or ""
        )

        if (
            module
            == "backend.server.runtime.live_route_orchestration_hooks"
        ):
            edits.append(
                (
                    node.lineno,
                    node.end_lineno
                    or node.lineno,
                    [],
                )
            )

for node in ast.walk(
    tree
):
    if not isinstance(
        node,
        (
            ast.Assign,
            ast.AnnAssign,
            ast.Expr,
        ),
    ):
        continue

    matching_call = None

    for child in ast.walk(
        node
    ):
        if not isinstance(
            child,
            ast.Call,
        ):
            continue

        function_name = ""

        if isinstance(
            child.func,
            ast.Name,
        ):
            function_name = (
                child.func.id
            )

        elif isinstance(
            child.func,
            ast.Attribute,
        ):
            function_name = (
                child.func.attr
            )

        if (
            function_name
            == "enqueue_and_run_website_ingestion_job_v1"
        ):
            matching_call = child

            break

    if matching_call is None:
        continue

    source_lines = source.splitlines()

    indent = indentation_of(
        source_lines[
            node.lineno - 1
        ]
    )

    if isinstance(
        node,
        ast.Assign,
    ) and any(
        isinstance(
            target,
            ast.Name,
        )
        and target.id
        == "orchestration_result"
        for target in node.targets
    ):
        replacement = [
            (
                indent
                + "orchestration_result = {"
            ),
            (
                indent
                + '    "status": '
                + '"QUEUED_AWAITING_FRESH_RUNTIME",'
            ),
            (
                indent
                + '    "executed": False,'
            ),
            (
                indent
                + '    "reason": '
                + '"Legacy live-route execution retired.",'
            ),
            (
                indent
                + "}"
            ),
        ]

    else:
        replacement = [
            (
                indent
                + "# Legacy live-route execution retired."
            )
        ]

    edits.append(
        (
            node.lineno,
            node.end_lineno
            or node.lineno,
            replacement,
        )
    )

if len(
    edits
) < 2:
    failures.append(
        "Expected both the retired site-reader import and execution "
        "statement to be found."
    )

else:
    updated = apply_line_edits(
        source,
        edits,
    )

    SITE_READER.write_text(
        updated,
        encoding="utf-8",
    )

    changes.append(
        {
            "action":
                "REMOVE_RETIRED_SITE_READER_EXECUTION",

            "path":
                relative(
                    SITE_READER
                ),

            "edit_count":
                len(
                    edits
                ),
        }
    )


# ==================================================================
# 3. canonical_environment_rebuild_manager.py
# Remove the retired manager import. Any functions depending on names
# from that import remain present, but their bodies are disabled with
# an explicit pending-fresh-runtime error.
# ==================================================================

source = CANONICAL_REBUILD_MANAGER.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

tree = ast.parse(
    source,
    filename=str(
        CANONICAL_REBUILD_MANAGER
    ),
)

edits = []
retired_imported_names: set[
    str
] = set()

for node in tree.body:
    if not isinstance(
        node,
        ast.ImportFrom,
    ):
        continue

    module = str(
        node.module or ""
    )

    if (
        module
        == (
            "backend.server.runtime."
            "registry_driven_canonical_rebuild_manager"
        )
    ):
        retired_imported_names.update(
            alias.asname
            or alias.name
            for alias in node.names
        )

        edits.append(
            (
                node.lineno,
                node.end_lineno
                or node.lineno,
                [],
            )
        )

if not retired_imported_names:
    failures.append(
        "The retired registry-driven rebuild-manager import "
        "was not found."
    )

else:
    source_lines = source.splitlines()

    for node in tree.body:
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        if not node_contains_names(
            node,
            retired_imported_names,
        ):
            continue

        if not node.body:
            continue

        body_start = node.body[
            0
        ].lineno

        body_end = (
            node.end_lineno
            or body_start
        )

        definition_line = source_lines[
            node.lineno - 1
        ]

        function_indent = indentation_of(
            definition_line
        )

        body_indent = (
            function_indent
            + "    "
        )

        replacement = [
            (
                body_indent
                + "raise RuntimeError("
            ),
            (
                body_indent
                + '    "Canonical environment rebuild execution '
                + 'is retired pending the fresh runtime implementation."'
            ),
            (
                body_indent
                + ")"
            ),
        ]

        edits.append(
            (
                body_start,
                body_end,
                replacement,
            )
        )

    updated = apply_line_edits(
        source,
        edits,
    )

    CANONICAL_REBUILD_MANAGER.write_text(
        updated,
        encoding="utf-8",
    )

    changes.append(
        {
            "action":
                "DISABLE_RETIRED_CANONICAL_REBUILD_EXECUTION",

            "path":
                relative(
                    CANONICAL_REBUILD_MANAGER
                ),

            "retired_imported_names":
                sorted(
                    retired_imported_names
                ),

            "edit_count":
                len(
                    edits
                ),
        }
    )


# ==================================================================
# Syntax verification.
# ==================================================================

syntax_results: dict[
    str,
    dict[str, Any]
] = {}

for name, path in TARGETS.items():
    try:
        updated_source = path.read_text(
            encoding="utf-8-sig",
            errors="strict",
        )

        ast.parse(
            updated_source,
            filename=str(
                path
            ),
        )

        syntax_results[
            name
        ] = {
            "path":
                relative(
                    path
                ),

            "syntax_valid":
                True,

            "error":
                None,
        }

    except Exception as exc:
        syntax_results[
            name
        ] = {
            "path":
                relative(
                    path
                ),

            "syntax_valid":
                False,

            "error":
                str(
                    exc
                ),
        }

        failures.append(
            "Syntax verification failed for "
            + relative(
                path
            )
            + ": "
            + str(
                exc
            )
        )


# ==================================================================
# Protected architecture verification.
# ==================================================================

protected_after = {
    name: fingerprint(
        path
    )
    for name, path
    in PROTECTED_PATHS.items()
}

protected_unchanged = {
    name: (
        protected_before[
            name
        ]
        == protected_after[
            name
        ]
    )
    for name
    in PROTECTED_PATHS
}

for name, unchanged in protected_unchanged.items():
    if not unchanged:
        failures.append(
            "Protected component changed: "
            + name
        )


# ==================================================================
# Zero-reference verification across active server Python files.
# ==================================================================

remaining_references: list[
    dict[str, Any]
] = []

for path in SERVER_ROOT.rglob(
    "*.py"
):
    if (
        not path.is_file()
        or excluded(
            path
        )
    ):
        continue

    text = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    matches = []

    for line_number, line in enumerate(
        text.splitlines(),
        start=1,
    ):
        lowered = line.casefold()

        matched_terms = sorted(
            term
            for term in RETIRED_REFERENCE_TERMS
            if term.casefold()
            in lowered
        )

        if not matched_terms:
            continue

        matches.append(
            {
                "line_number":
                    line_number,

                "matched_terms":
                    matched_terms,

                "line":
                    line.strip()[:1500],
            }
        )

    if matches:
        remaining_references.append(
            {
                "path":
                    relative(
                        path
                    ),

                "matches":
                    matches,
            }
        )

if remaining_references:
    failures.append(
        "Active references to retired UUCD worker/runtime symbols remain."
    )


checks = {
    "orchestration_worker_import_removed":
        (
            "from .worker import"
            not in ORCHESTRATION_ROUTES.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        ),

    "orchestration_worker_routes_removed":
        (
            "run_one_job"
            not in ORCHESTRATION_ROUTES.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
            and "worker_health"
            not in ORCHESTRATION_ROUTES.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        ),

    "site_reader_legacy_import_removed":
        (
            "live_route_orchestration_hooks"
            not in SITE_READER.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        ),

    "site_reader_legacy_execution_removed":
        (
            "enqueue_and_run_website_ingestion_job_v1"
            not in SITE_READER.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        ),

    "site_reader_pending_status_present":
        (
            "QUEUED_AWAITING_FRESH_RUNTIME"
            in SITE_READER.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        ),

    "canonical_rebuild_legacy_import_removed":
        (
            "registry_driven_canonical_rebuild_manager"
            not in CANONICAL_REBUILD_MANAGER.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        ),

    "canonical_rebuild_execution_disabled":
        (
            "retired pending the fresh runtime implementation"
            in CANONICAL_REBUILD_MANAGER.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        ),

    "all_target_files_syntax_valid":
        all(
            result[
                "syntax_valid"
            ]
            for result in syntax_results.values()
        ),

    "zero_remaining_active_references":
        not remaining_references,

    "protected_components_unchanged":
        all(
            protected_unchanged.values()
        ),
}

for name, passed in checks.items():
    if passed is not True:
        failures.append(
            "Final verification failed: "
            + name
        )


report = {
    "schema_version":
        "final_legacy_uucd_dependency_cleanup_v1",

    "workspace_id":
        WORKSPACE_ID,

    "cleanup_status":
        (
            "PASS"
            if not failures
            else "FAIL"
        ),

    "backup_root":
        str(
            BACKUP_ROOT
        ),

    "checks":
        checks,

    "changes":
        changes,

    "syntax_results":
        syntax_results,

    "protected_components_unchanged":
        protected_unchanged,

    "remaining_reference_file_count":
        len(
            remaining_references
        ),

    "remaining_references":
        remaining_references,

    "fresh_uucd_created":
        False,

    "fresh_worker_created":
        False,

    "uucd_data_written":
        False,

    "body_store_data_written":
        False,

    "runtime_registration_created":
        False,

    "failures":
        failures,
}

write_json(
    REPORT_PATH,
    report,
)


print(
    "Files surgically cleaned:             "
    + str(
        len(
            TARGETS
        )
    )
)

print(
    "Remaining active reference files:      "
    + str(
        len(
            remaining_references
        )
    )
)

print()
print(
    "FINAL CHECKS"
)

for name, passed in checks.items():
    print(
        "  "
        + f"{name:<54}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "PROTECTED COMPONENTS"
)

for name, unchanged in protected_unchanged.items():
    print(
        "  "
        + name
        + ": "
        + (
            "UNCHANGED"
            if unchanged
            else "CHANGED"
        )
    )

print()
print(
    "REMAINING REFERENCES"
)

if remaining_references:
    for result in remaining_references:
        print()
        print(
            "  FILE: "
            + result[
                "path"
            ]
        )

        for match in result[
            "matches"
        ]:
            print(
                "    Line "
                + str(
                    match[
                        "line_number"
                    ]
                )
                + ": "
                + match[
                    "line"
                ]
            )

else:
    print(
        "  None"
    )

print()
print(
    "Fresh UUCD created:             False"
)

print(
    "Fresh worker created:           False"
)

print(
    "UUCD data written:              False"
)

print(
    "Body Store data written:        False"
)

print(
    "Runtime Registration created:   False"
)

print()
print(
    "Backup location: "
    + str(
        BACKUP_ROOT
    )
)

print(
    "Cleanup report: "
    + str(
        REPORT_PATH
    )
)

print()

if failures:
    print(
        "FINAL LEGACY UUCD DEPENDENCY CLEANUP: FAIL"
    )

    for failure in failures:
        print(
            "  - "
            + failure
        )

    print("=" * 112)

    raise SystemExit(1)

print(
    "FINAL LEGACY UUCD DEPENDENCY CLEANUP: PASS"
)

print(
    "All remaining imports, routes and execution statements tied to "
    "the retired UUCD workers and runtime managers were removed."
)

print(
    "Unrelated orchestration, site-reader and environment-management "
    "functionality remains present and syntactically valid."
)

print("=" * 112)
