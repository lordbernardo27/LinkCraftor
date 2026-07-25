"""Read-only scan of all active legacy WUC Store dependencies."""

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

OUTPUT_REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "wuc_legacy_store_dependency_contract_scan.json"
)

TARGET_PATHS = [
    (
        SERVER_ROOT
        / "stores"
        / "website_unified_content_store.py"
    ),

    (
        SERVER_ROOT
        / "stores"
        / "website_unified_content_builder_v2.py"
    ),

    (
        SERVER_ROOT
        / "stores"
        / "website_unified_content_certifier_v2.py"
    ),

    (
        SERVER_ROOT
        / "stores"
        / "website_unified_content_verifier_v2.py"
    ),

    (
        SERVER_ROOT
        / "stores"
        / "crawled_article_viewer.py"
    ),

    (
        SERVER_ROOT
        / "stores"
        / "website_article_integrity_checker.py"
    ),

    (
        SERVER_ROOT
        / "stores"
        / "website_source_pipeline_orchestrator.py"
    ),

    (
        SERVER_ROOT
        / "stores"
        / "website_uucd_rebuild_engine.py"
    ),

    (
        SERVER_ROOT
        / "workers"
        / "website_unified_content_batch_worker.py"
    ),

    (
        SERVER_ROOT
        / "workers"
        / "website_unified_content_batch_worker_v2.py"
    ),

    (
        SERVER_ROOT
        / "stores"
        / "universal_unified_content_document_convergence.py"
    ),
]


def relative(
    path: Path,
) -> str:
    try:
        return str(
            path.resolve().relative_to(
                PROJECT_ROOT
            )
        )

    except ValueError:
        return str(
            path.resolve()
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


def rendered(
    node: ast.AST,
) -> str:
    try:
        return ast.unparse(
            node
        )

    except Exception:
        return node.__class__.__name__


def inspect_file(
    path: Path,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path":
            relative(
                path
            ),

        "exists":
            path.is_file(),

        "syntax_valid":
            None,

        "syntax_error":
            None,

        "imports":
            [],

        "functions":
            [],

        "store_calls":
            [],

        "uucd_calls":
            [],

        "udare_references":
            [],

        "article_validation_references":
            [],

        "return_statements":
            [],

        "path_assignments":
            [],
    }

    if not path.is_file():
        return result

    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

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

            "message":
                exc.msg,

            "text":
                str(
                    exc.text or ""
                ).strip(),
        }

        return result

    result[
        "syntax_valid"
    ] = True

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                result[
                    "imports"
                ].append(
                    {
                        "line_number":
                            node.lineno,

                        "module":
                            alias.name,
                    }
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            module = str(
                node.module or ""
            )

            for alias in node.names:
                result[
                    "imports"
                ].append(
                    {
                        "line_number":
                            node.lineno,

                        "module":
                            (
                                module
                                + "."
                                + alias.name
                            ).strip("."),
                    }
                )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            result[
                "functions"
            ].append(
                {
                    "line_number":
                        node.lineno,

                    "name":
                        node.name,

                    "arguments":
                        [
                            argument.arg
                            for argument
                            in node.args.args
                        ],

                    "returns":
                        rendered(
                            node.returns
                        )
                        if node.returns
                        else None,
                }
            )

        elif isinstance(
            node,
            ast.Call,
        ):
            call_text = rendered(
                node
            )

            lowered = call_text.casefold()

            if (
                "website_unified_content_store"
                in lowered
                or "upsert_website_unified_content"
                in lowered
                or "load_website_unified_content_store"
                in lowered
                or "get_website_unified_content_document"
                in lowered
            ):
                result[
                    "store_calls"
                ].append(
                    {
                        "line_number":
                            node.lineno,

                        "call":
                            call_text[:3000],
                    }
                )

            if (
                "uucd"
                in lowered
                or "universal_unified_content"
                in lowered
            ):
                result[
                    "uucd_calls"
                ].append(
                    {
                        "line_number":
                            node.lineno,

                        "call":
                            call_text[:3000],
                    }
                )

            if (
                "udare"
                in lowered
            ):
                result[
                    "udare_references"
                ].append(
                    {
                        "line_number":
                            node.lineno,

                        "call":
                            call_text[:3000],
                    }
                )

            if (
                "article_validation"
                in lowered
                or "pass_manifest"
                in lowered
            ):
                result[
                    "article_validation_references"
                ].append(
                    {
                        "line_number":
                            node.lineno,

                        "call":
                            call_text[:3000],
                    }
                )

        elif isinstance(
            node,
            ast.Return,
        ):
            result[
                "return_statements"
            ].append(
                {
                    "line_number":
                        node.lineno,

                    "value":
                        rendered(
                            node.value
                        )
                        if node.value
                        else None,
                }
            )

        elif isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            targets = (
                node.targets
                if isinstance(
                    node,
                    ast.Assign,
                )
                else [
                    node.target
                ]
            )

            for target in targets:
                if not isinstance(
                    target,
                    ast.Name,
                ):
                    continue

                name = target.id

                if any(
                    term in name.casefold()
                    for term in (
                        "path",
                        "store",
                        "root",
                        "uucd",
                        "udare",
                        "manifest",
                        "article",
                        "content",
                    )
                ):
                    result[
                        "path_assignments"
                    ].append(
                        {
                            "line_number":
                                node.lineno,

                            "name":
                                name,

                            "value":
                                rendered(
                                    node.value
                                )[:3000],
                        }
                    )

    for key in (
        "imports",
        "functions",
        "store_calls",
        "uucd_calls",
        "udare_references",
        "article_validation_references",
        "return_statements",
        "path_assignments",
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


inspections = [
    inspect_file(
        path
    )
    for path in TARGET_PATHS
]

active_store_dependents = [
    {
        "path":
            inspection[
                "path"
            ],

        "imports":
            [
                item
                for item
                in inspection[
                    "imports"
                ]
                if (
                    "website_unified_content_store"
                    in item[
                        "module"
                    ].casefold()
                )
            ],

        "store_calls":
            inspection[
                "store_calls"
            ],
    }
    for inspection in inspections
    if (
        any(
            "website_unified_content_store"
            in item[
                "module"
            ].casefold()
            for item
            in inspection[
                "imports"
            ]
        )
        or inspection[
            "store_calls"
        ]
    )
]


report = {
    "schema_version":
        "wuc_legacy_store_dependency_contract_scan_v1",

    "workspace_id":
        WORKSPACE_ID,

    "scan_mode":
        "READ_ONLY",

    "inspections":
        inspections,

    "active_store_dependent_count":
        len(
            active_store_dependents
        ),

    "active_store_dependents":
        active_store_dependents,

    "source_files_modified":
        False,

    "data_files_modified":
        False,

    "runtime_state_modified":
        False,

    "wuc_executed":
        False,
}

write_json(
    OUTPUT_REPORT_PATH,
    report,
)


print()
print("=" * 108)
print(
    "WUC — LEGACY STORE DEPENDENCY AND MIGRATION-CONTRACT SCAN"
)
print("=" * 108)
print()

print(
    "Files inspected:                 "
    + str(
        len(
            inspections
        )
    )
)

print(
    "Active legacy Store dependents:  "
    + str(
        len(
            active_store_dependents
        )
    )
)

print()
print(
    "ACTIVE STORE DEPENDENCIES"
)

for dependent in active_store_dependents:
    print()
    print(
        "  "
        + dependent[
            "path"
        ]
    )

    for item in dependent[
        "imports"
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
        )

    for item in dependent[
        "store_calls"
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
                "call"
            ]
        )

print()
print(
    "FUNCTION CONTRACTS"
)

for inspection in inspections:
    print()
    print(
        "  "
        + inspection[
            "path"
        ]
    )

    print(
        "    Syntax valid: "
        + str(
            inspection[
                "syntax_valid"
            ]
        )
    )

    for function in inspection[
        "functions"
    ]:
        print(
            "    "
            + function[
                "name"
            ]
            + "("
            + ", ".join(
                function[
                    "arguments"
                ]
            )
            + ")"
            + " @ line "
            + str(
                function[
                    "line_number"
                ]
            )
        )

    print(
        "    Store calls: "
        + str(
            len(
                inspection[
                    "store_calls"
                ]
            )
        )
    )

    print(
        "    UUCD calls: "
        + str(
            len(
                inspection[
                    "uucd_calls"
                ]
            )
        )
    )

    print(
        "    UDARE references: "
        + str(
            len(
                inspection[
                    "udare_references"
                ]
            )
        )
    )

    print(
        "    Article Validation references: "
        + str(
            len(
                inspection[
                    "article_validation_references"
                ]
            )
        )
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
        OUTPUT_REPORT_PATH
    )
)

print()
print(
    "WUC LEGACY STORE DEPENDENCY SCAN: PASS"
)

print(
    "All active Store dependencies and function contracts "
    "were inspected without modification."
)

print("=" * 108)
