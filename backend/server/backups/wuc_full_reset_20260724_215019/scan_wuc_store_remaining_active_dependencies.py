"""Scan all active Python code for remaining legacy WUC Store dependencies."""

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

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "wuc_store_remaining_active_dependencies.json"
)

LEGACY_MODULE = (
    "backend.server.stores."
    "website_unified_content_store"
)

LEGACY_FUNCTIONS = {
    "load_website_unified_content_store_v1",
    "save_website_unified_content_store_v1",
    "upsert_website_unified_content_document_v1",
    "get_website_unified_content_document_v1",
}

EXPECTED_CLEAN_FILE = (
    SERVER_ROOT
    / "workers"
    / "website_unified_content_batch_worker_v2.py"
)

STORE_MODULE_PATH = (
    SERVER_ROOT
    / "stores"
    / "website_unified_content_store.py"
)

STORE_DATA_ROOT = (
    DATA_ROOT
    / "website_unified_content"
)

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "backups",
    "runtime_backups",
    "node_modules",
}

EXPECTED_EXTERNAL_DEPENDENCIES = {
    (
        "backend/server/stores/"
        "crawled_article_viewer.py"
    ),

    (
        "backend/server/stores/"
        "website_article_integrity_checker.py"
    ),

    (
        "backend/server/stores/"
        "website_source_pipeline_orchestrator.py"
    ),

    (
        "backend/server/stores/"
        "website_uucd_rebuild_engine.py"
    ),

    (
        "backend/server/workers/"
        "website_unified_content_batch_worker.py"
    ),
}


def excluded(
    path: Path,
) -> bool:
    return any(
        part in EXCLUDED_PARTS
        for part in path.parts
    )


def relative(
    path: Path,
) -> str:
    return (
        path.resolve()
        .relative_to(
            PROJECT_ROOT
        )
        .as_posix()
    )


def render(
    node: ast.AST,
) -> str:
    try:
        return ast.unparse(
            node
        )

    except Exception:
        return (
            node.__class__.__name__
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


def inspect_file(
    path: Path,
) -> dict[str, Any]:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    result: dict[str, Any] = {
        "path":
            relative(
                path
            ),

        "syntax_valid":
            True,

        "syntax_error":
            None,

        "legacy_imports":
            [],

        "legacy_function_calls":
            [],

        "legacy_name_references":
            [],

        "direct_uucd_calls":
            [],

        "pass_manifest_references":
            [],

        "udare_references":
            [],
    }

    try:
        tree = ast.parse(
            source,
            filename=str(
                path
            ),
        )

    except SyntaxError as exc:
        result[
            "syntax_valid"
        ] = False

        result[
            "syntax_error"
        ] = {
            "line_number":
                exc.lineno,

            "offset":
                exc.offset,

            "message":
                exc.msg,

            "text":
                str(
                    exc.text or ""
                ).strip(),
        }

        return result

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                if (
                    alias.name
                    == LEGACY_MODULE
                    or alias.name.startswith(
                        LEGACY_MODULE
                        + "."
                    )
                ):
                    result[
                        "legacy_imports"
                    ].append(
                        {
                            "line_number":
                                node.lineno,

                            "module":
                                alias.name,

                            "name":
                                alias.asname,
                        }
                    )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            module = str(
                node.module or ""
            )

            if module == LEGACY_MODULE:
                for alias in node.names:
                    result[
                        "legacy_imports"
                    ].append(
                        {
                            "line_number":
                                node.lineno,

                            "module":
                                module,

                            "name":
                                alias.name,

                            "alias":
                                alias.asname,
                        }
                    )

        elif isinstance(
            node,
            ast.Call,
        ):
            called_name = ""

            if isinstance(
                node.func,
                ast.Name,
            ):
                called_name = (
                    node.func.id
                )

            elif isinstance(
                node.func,
                ast.Attribute,
            ):
                called_name = (
                    node.func.attr
                )

            if (
                called_name
                in LEGACY_FUNCTIONS
            ):
                result[
                    "legacy_function_calls"
                ].append(
                    {
                        "line_number":
                            node.lineno,

                        "function":
                            called_name,

                        "call":
                            render(
                                node
                            )[:4000],
                    }
                )

            rendered_call = render(
                node
            )

            lowered_call = (
                rendered_call.casefold()
            )

            if (
                "build_and_write_uucd_from_wuc_v1"
                in rendered_call
            ):
                result[
                    "direct_uucd_calls"
                ].append(
                    {
                        "line_number":
                            node.lineno,

                        "call":
                            rendered_call[:4000],
                    }
                )

            if (
                "article_validation_pass"
                in lowered_call
                or "pass_manifest"
                in lowered_call
            ):
                result[
                    "pass_manifest_references"
                ].append(
                    {
                        "line_number":
                            node.lineno,

                        "call":
                            rendered_call[:4000],
                    }
                )

            if "udare" in lowered_call:
                result[
                    "udare_references"
                ].append(
                    {
                        "line_number":
                            node.lineno,

                        "call":
                            rendered_call[:4000],
                    }
                )

        elif isinstance(
            node,
            ast.Name,
        ):
            if (
                node.id
                in LEGACY_FUNCTIONS
            ):
                result[
                    "legacy_name_references"
                ].append(
                    {
                        "line_number":
                            node.lineno,

                        "name":
                            node.id,
                    }
                )

    for key in (
        "legacy_imports",
        "legacy_function_calls",
        "legacy_name_references",
        "direct_uucd_calls",
        "pass_manifest_references",
        "udare_references",
    ):
        result[
            key
        ].sort(
            key=lambda item: (
                int(
                    item.get(
                        "line_number"
                    )
                    or 0
                ),
                str(
                    item
                ),
            )
        )

    return result


python_files = sorted(
    (
        path
        for path in SERVER_ROOT.rglob(
            "*.py"
        )
        if (
            path.is_file()
            and not excluded(
                path
            )
        )
    ),
    key=lambda path: (
        path.as_posix()
    ),
)

inspections = [
    inspect_file(
        path
    )
    for path in python_files
]

external_dependencies: list[
    dict[str, Any]
] = []

store_module_inspection = None

for inspection in inspections:
    path = inspection[
        "path"
    ]

    has_dependency = bool(
        inspection[
            "legacy_imports"
        ]
        or inspection[
            "legacy_function_calls"
        ]
        or inspection[
            "legacy_name_references"
        ]
    )

    if not has_dependency:
        continue

    if (
        path
        == relative(
            STORE_MODULE_PATH
        )
    ):
        store_module_inspection = (
            inspection
        )

        continue

    external_dependencies.append(
        inspection
    )


external_dependency_paths = {
    inspection[
        "path"
    ]
    for inspection in external_dependencies
}

unexpected_dependency_paths = sorted(
    external_dependency_paths
    - EXPECTED_EXTERNAL_DEPENDENCIES
)

expected_but_missing_paths = sorted(
    EXPECTED_EXTERNAL_DEPENDENCIES
    - external_dependency_paths
)


clean_worker_inspection = next(
    (
        inspection
        for inspection in inspections
        if (
            inspection[
                "path"
            ]
            == relative(
                EXPECTED_CLEAN_FILE
            )
        )
    ),
    None,
)

clean_worker_has_legacy_dependency = bool(
    clean_worker_inspection
    and (
        clean_worker_inspection[
            "legacy_imports"
        ]
        or clean_worker_inspection[
            "legacy_function_calls"
        ]
        or clean_worker_inspection[
            "legacy_name_references"
        ]
    )
)

clean_worker_direct_uucd = bool(
    clean_worker_inspection
    and clean_worker_inspection[
        "direct_uucd_calls"
    ]
)

clean_worker_pass_manifest = bool(
    clean_worker_inspection
    and clean_worker_inspection[
        "pass_manifest_references"
    ]
)

store_data_file_count = (
    sum(
        1
        for path in STORE_DATA_ROOT.rglob(
            "*"
        )
        if path.is_file()
    )
    if STORE_DATA_ROOT.is_dir()
    else 0
)


failures: list[str] = []

if clean_worker_has_legacy_dependency:
    failures.append(
        "Canonical v2 worker still references "
        "the legacy WUC Store."
    )

if not clean_worker_direct_uucd:
    failures.append(
        "Canonical v2 worker does not call "
        "direct UUCD convergence."
    )

if not clean_worker_pass_manifest:
    failures.append(
        "Canonical v2 worker does not reference "
        "the Article Validation PASS contract."
    )

if unexpected_dependency_paths:
    failures.append(
        "Unexpected active legacy Store dependencies were found."
    )

if expected_but_missing_paths:
    failures.append(
        "The active dependency set changed from the expected five files."
    )


report = {
    "schema_version":
        "wuc_store_remaining_active_dependencies_v1",

    "workspace_id":
        WORKSPACE_ID,

    "scan_mode":
        "READ_ONLY",

    "python_files_scanned":
        len(
            python_files
        ),

    "legacy_store_module_exists":
        STORE_MODULE_PATH.is_file(),

    "legacy_store_data_root_exists":
        STORE_DATA_ROOT.is_dir(),

    "legacy_store_data_file_count":
        store_data_file_count,

    "external_dependency_count":
        len(
            external_dependencies
        ),

    "external_dependencies":
        external_dependencies,

    "external_dependency_paths":
        sorted(
            external_dependency_paths
        ),

    "expected_external_dependency_paths":
        sorted(
            EXPECTED_EXTERNAL_DEPENDENCIES
        ),

    "unexpected_dependency_paths":
        unexpected_dependency_paths,

    "expected_but_missing_paths":
        expected_but_missing_paths,

    "store_module_inspection":
        store_module_inspection,

    "canonical_v2_worker": {
        "path":
            relative(
                EXPECTED_CLEAN_FILE
            ),

        "exists":
            EXPECTED_CLEAN_FILE.is_file(),

        "legacy_store_dependency":
            clean_worker_has_legacy_dependency,

        "direct_uucd_convergence":
            clean_worker_direct_uucd,

        "article_validation_pass_contract":
            clean_worker_pass_manifest,
    },

    "source_files_modified":
        False,

    "data_files_modified":
        False,

    "runtime_state_modified":
        False,

    "jobs_enqueued":
        False,

    "workers_started":
        False,

    "wuc_executed":
        False,

    "failures":
        failures,

    "scan_status":
        (
            "PASS"
            if not failures
            else "FAIL"
        ),
}

write_json(
    REPORT_PATH,
    report,
)


print()
print("=" * 108)
print(
    "WUC LEGACY STORE — REMAINING ACTIVE DEPENDENCY SCAN"
)
print("=" * 108)
print()

print(
    "Python files scanned:                   "
    + str(
        report[
            "python_files_scanned"
        ]
    )
)

print(
    "Legacy Store module exists:             "
    + str(
        report[
            "legacy_store_module_exists"
        ]
    )
)

print(
    "Legacy Store data root exists:          "
    + str(
        report[
            "legacy_store_data_root_exists"
        ]
    )
)

print(
    "Legacy Store data files:                "
    + str(
        report[
            "legacy_store_data_file_count"
        ]
    )
)

print(
    "Remaining external dependencies:        "
    + str(
        report[
            "external_dependency_count"
        ]
    )
)

print(
    "Unexpected active dependencies:         "
    + str(
        len(
            unexpected_dependency_paths
        )
    )
)

print(
    "Expected dependencies not detected:     "
    + str(
        len(
            expected_but_missing_paths
        )
    )
)

print()
print(
    "CANONICAL V2 WORKER"
)

print(
    "  Legacy Store dependency:             "
    + str(
        clean_worker_has_legacy_dependency
    )
)

print(
    "  Article Validation PASS input:       "
    + str(
        clean_worker_pass_manifest
    )
)

print(
    "  Direct UUCD convergence:             "
    + str(
        clean_worker_direct_uucd
    )
)

print()
print(
    "REMAINING EXTERNAL DEPENDENCIES"
)

if external_dependencies:
    for inspection in external_dependencies:
        print()
        print(
            "  "
            + inspection[
                "path"
            ]
        )

        for item in inspection[
            "legacy_imports"
        ]:
            print(
                "    IMPORT line "
                + str(
                    item[
                        "line_number"
                    ]
                )
                + ": "
                + item[
                    "module"
                ]
                + "."
                + str(
                    item.get(
                        "name"
                    )
                    or ""
                )
            )

        for item in inspection[
            "legacy_function_calls"
        ]:
            print(
                "    CALL line "
                + str(
                    item[
                        "line_number"
                    ]
                )
                + ": "
                + item[
                    "function"
                ]
            )

else:
    print(
        "  None"
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
    "Source files modified:  False"
)

print(
    "Data files modified:    False"
)

print(
    "Runtime state modified: False"
)

print(
    "WUC executed:           False"
)

print()
print(
    "Dependency report: "
    + str(
        REPORT_PATH
    )
)

print()

if failures:
    print(
        "WUC REMAINING DEPENDENCY SCAN: FAIL"
    )

    print("=" * 108)

    raise SystemExit(1)

print(
    "WUC REMAINING DEPENDENCY SCAN: PASS"
)

print(
    "The canonical v2 worker is clean and the remaining "
    "legacy Store dependencies are fully identified."
)

print("=" * 108)
