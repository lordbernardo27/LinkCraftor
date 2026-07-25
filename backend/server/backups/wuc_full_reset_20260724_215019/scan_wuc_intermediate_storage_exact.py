"""Identify exact WUC storage directories and active write destinations."""

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

HANDOFF_REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "website_unified_content_handoff_scan.json"
)

OUTPUT_REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "website_unified_content_storage_exact_scan.json"
)

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "backups",
    "runtime_backups",
    "node_modules",
}

BODY_FIELD_NAMES = {
    "article_body",
    "body",
    "body_html",
    "content_body",
    "content_html",
    "html",
    "raw_html",
    "clean_html",
    "article_html",
    "full_text",
}

WRITE_METHODS = {
    "write_text",
    "write_bytes",
    "open",
    "copy",
    "copy2",
    "copyfile",
    "copytree",
    "move",
    "replace",
    "rename",
    "mkdir",
}


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


def excluded(
    path: Path,
) -> bool:
    return any(
        part in EXCLUDED_PARTS
        for part in path.parts
    )


def load_json(
    path: Path,
) -> dict[str, Any]:
    value = json.loads(
        path.read_text(
            encoding="utf-8-sig",
        )
    )

    if not isinstance(
        value,
        dict,
    ):
        raise RuntimeError(
            f"Expected JSON object: {path}"
        )

    return value


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


def detect_body_fields(
    value: Any,
    *,
    prefix: str = "",
) -> list[str]:
    findings: list[str] = []

    if isinstance(
        value,
        dict,
    ):
        for key, child in value.items():
            key_name = str(
                key
            )

            child_prefix = (
                f"{prefix}.{key_name}"
                if prefix
                else key_name
            )

            if (
                key_name.casefold()
                in BODY_FIELD_NAMES
            ):
                findings.append(
                    child_prefix
                )

            findings.extend(
                detect_body_fields(
                    child,
                    prefix=child_prefix,
                )
            )

    elif isinstance(
        value,
        list,
    ):
        for index, child in enumerate(
            value
        ):
            findings.extend(
                detect_body_fields(
                    child,
                    prefix=(
                        f"{prefix}[{index}]"
                    ),
                )
            )

    return findings


def inspect_data_file(
    path: Path,
) -> dict[str, Any]:
    suffix = path.suffix.casefold()

    result: dict[str, Any] = {
        "path":
            relative(
                path
            ),

        "suffix":
            suffix,

        "size_bytes":
            path.stat().st_size,

        "body_fields":
            [],

        "json_valid":
            None,

        "appears_article_body":
            False,

        "contains_html_markup":
            False,
    }

    if suffix in {
        ".html",
        ".htm",
    }:
        result[
            "appears_article_body"
        ] = True

        result[
            "contains_html_markup"
        ] = True

        return result

    if suffix not in {
        ".json",
        ".jsonl",
        ".txt",
        ".md",
    }:
        return result

    text = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    lowered = text.casefold()

    result[
        "contains_html_markup"
    ] = any(
        marker in lowered
        for marker in (
            "<article",
            "<p>",
            "<p ",
            "<h1",
            "<h2",
            "<html",
            "<body",
        )
    )

    if suffix == ".json":
        try:
            payload = json.loads(
                text
            )

            result[
                "json_valid"
            ] = True

            result[
                "body_fields"
            ] = detect_body_fields(
                payload
            )

        except Exception:
            result[
                "json_valid"
            ] = False

    elif suffix == ".jsonl":
        body_fields: list[str] = []
        valid = True

        for line_number, line in enumerate(
            text.splitlines(),
            start=1,
        ):
            stripped = line.strip()

            if not stripped:
                continue

            try:
                payload = json.loads(
                    stripped
                )

            except Exception:
                valid = False
                continue

            body_fields.extend(
                f"line[{line_number}].{field}"
                for field in detect_body_fields(
                    payload
                )
            )

        result[
            "json_valid"
        ] = valid

        result[
            "body_fields"
        ] = body_fields

    result[
        "appears_article_body"
    ] = bool(
        result[
            "body_fields"
        ]
        or result[
            "contains_html_markup"
        ]
    )

    return result


def inspect_python_writes(
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

        "assignments":
            [],

        "write_calls":
            [],

        "imports":
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
                        "output",
                        "manifest",
                        "body",
                        "content",
                        "article",
                    )
                ):
                    try:
                        rendered = ast.unparse(
                            node.value
                        )

                    except Exception:
                        rendered = "..."

                    result[
                        "assignments"
                    ].append(
                        {
                            "name":
                                name,

                            "line_number":
                                node.lineno,

                            "value":
                                rendered[:2000],
                        }
                    )

        elif isinstance(
            node,
            ast.Call,
        ):
            function_name = ""

            if isinstance(
                node.func,
                ast.Name,
            ):
                function_name = (
                    node.func.id
                )

            elif isinstance(
                node.func,
                ast.Attribute,
            ):
                function_name = (
                    node.func.attr
                )

            if function_name in WRITE_METHODS:
                try:
                    rendered = ast.unparse(
                        node
                    )

                except Exception:
                    rendered = function_name

                result[
                    "write_calls"
                ].append(
                    {
                        "function":
                            function_name,

                        "line_number":
                            node.lineno,

                        "call":
                            rendered[:3000],
                    }
                )

        elif isinstance(
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

    return result


if not HANDOFF_REPORT_PATH.is_file():
    raise FileNotFoundError(
        "WUC handoff scan report is missing: "
        + str(
            HANDOFF_REPORT_PATH
        )
    )

handoff_report = load_json(
    HANDOFF_REPORT_PATH
)

potential_directories = (
    handoff_report.get(
        "potential_intermediate_wuc_directories"
    )
    or []
)

if not isinstance(
    potential_directories,
    list,
):
    raise RuntimeError(
        "Potential WUC directories field is invalid."
    )


directory_inspections: list[
    dict[str, Any]
] = []

for directory_record in (
    potential_directories
):
    if not isinstance(
        directory_record,
        dict,
    ):
        continue

    directory_value = str(
        directory_record.get(
            "path"
        )
        or ""
    ).strip()

    if not directory_value:
        continue

    directory_path = (
        PROJECT_ROOT
        / directory_value
    ).resolve()

    files: list[
        dict[str, Any]
    ] = []

    if directory_path.is_dir():
        for file_path in sorted(
            (
                path
                for path in directory_path.rglob(
                    "*"
                )
                if path.is_file()
            ),
            key=lambda path: (
                path.as_posix()
            ),
        ):
            files.append(
                inspect_data_file(
                    file_path
                )
            )

    body_like_files = [
        record
        for record in files
        if record[
            "appears_article_body"
        ]
    ]

    directory_inspections.append(
        {
            "path":
                relative(
                    directory_path
                ),

            "exists":
                directory_path.is_dir(),

            "file_count":
                len(
                    files
                ),

            "body_like_file_count":
                len(
                    body_like_files
                ),

            "files":
                files,

            "body_like_files":
                body_like_files,

            "classification":
                (
                    "PROHIBITED_INTERMEDIATE_CONTENT_STORE"
                    if body_like_files
                    else "METADATA_OR_EVIDENCE_ONLY_DIRECTORY"
                ),
        }
    )


active_wuc_files = (
    handoff_report.get(
        "active_wuc_files"
    )
    or []
)

source_paths: set[
    Path
] = set()

for record in active_wuc_files:
    if not isinstance(
        record,
        dict,
    ):
        continue

    value = str(
        record.get(
            "path"
        )
        or ""
    ).strip()

    if value:
        path = (
            PROJECT_ROOT
            / value
        ).resolve()

        if (
            path.is_file()
            and not excluded(
                path
            )
        ):
            source_paths.add(
                path
            )


priority_paths = {
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
        / "workers"
        / "website_unified_content_orchestrator.py"
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
}

for path in priority_paths:
    if path.is_file():
        source_paths.add(
            path.resolve()
        )


python_inspections = [
    inspect_python_writes(
        path
    )
    for path in sorted(
        source_paths,
        key=lambda path: (
            path.as_posix()
        ),
    )
]


files_importing_wuc_store: list[
    dict[str, Any]
] = []

for inspection in python_inspections:
    matches = [
        item
        for item in inspection[
            "imports"
        ]
        if (
            "website_unified_content_store"
            in item[
                "module"
            ].casefold()
        )
    ]

    if matches:
        files_importing_wuc_store.append(
            {
                "path":
                    inspection[
                        "path"
                    ],

                "imports":
                    matches,
            }
        )


prohibited_directories = [
    record
    for record in directory_inspections
    if (
        record[
            "classification"
        ]
        == "PROHIBITED_INTERMEDIATE_CONTENT_STORE"
    )
]

wuc_store_module = (
    SERVER_ROOT
    / "stores"
    / "website_unified_content_store.py"
)

report = {
    "schema_version":
        "website_unified_content_storage_exact_scan_v1",

    "workspace_id":
        WORKSPACE_ID,

    "scan_mode":
        "READ_ONLY",

    "potential_directory_count":
        len(
            directory_inspections
        ),

    "directory_inspections":
        directory_inspections,

    "prohibited_intermediate_directory_count":
        len(
            prohibited_directories
        ),

    "prohibited_intermediate_directories":
        prohibited_directories,

    "active_wuc_python_inspections":
        python_inspections,

    "wuc_store_module_exists":
        wuc_store_module.is_file(),

    "wuc_store_module_path":
        relative(
            wuc_store_module
        ),

    "files_importing_wuc_store":
        files_importing_wuc_store,

    "source_files_modified":
        False,

    "data_files_modified":
        False,

    "runtime_state_modified":
        False,

    "jobs_enqueued":
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
    "WUC — EXACT INTERMEDIATE STORAGE AND WRITE-PATH SCAN"
)
print("=" * 108)
print()

print(
    "Potential directories inspected:          "
    + str(
        report[
            "potential_directory_count"
        ]
    )
)

print(
    "Prohibited content directories:           "
    + str(
        report[
            "prohibited_intermediate_directory_count"
        ]
    )
)

print(
    "Legacy WUC Store module exists:           "
    + str(
        report[
            "wuc_store_module_exists"
        ]
    )
)

print(
    "Files importing legacy WUC Store module:  "
    + str(
        len(
            files_importing_wuc_store
        )
    )
)

print()
print(
    "DIRECTORY CLASSIFICATION"
)

if directory_inspections:
    for record in directory_inspections:
        print(
            "  Path: "
            + record[
                "path"
            ]
        )

        print(
            "    Exists: "
            + str(
                record[
                    "exists"
                ]
            )
        )

        print(
            "    Files: "
            + str(
                record[
                    "file_count"
                ]
            )
        )

        print(
            "    Body-like files: "
            + str(
                record[
                    "body_like_file_count"
                ]
            )
        )

        print(
            "    Classification: "
            + record[
                "classification"
            ]
        )

        for body_file in record[
            "body_like_files"
        ][
            :20
        ]:
            print(
                "      BODY-LIKE: "
                + body_file[
                    "path"
                ]
            )

            print(
                "        Body fields: "
                + json.dumps(
                    body_file[
                        "body_fields"
                    ],
                    ensure_ascii=False,
                )
            )

            print(
                "        HTML markup: "
                + str(
                    body_file[
                        "contains_html_markup"
                    ]
                )
            )

else:
    print(
        "  No candidate directories were supplied."
    )

print()
print(
    "FILES IMPORTING LEGACY WUC STORE"
)

if files_importing_wuc_store:
    for record in files_importing_wuc_store:
        print(
            "  "
            + record[
                "path"
            ]
        )

        for item in record[
            "imports"
        ]:
            print(
                "    line "
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

else:
    print(
        "  None"
    )

print()
print(
    "ACTIVE WRITE DESTINATIONS"
)

for inspection in python_inspections:
    if not inspection[
        "write_calls"
    ]:
        continue

    print(
        "  "
        + inspection[
            "path"
        ]
    )

    for item in inspection[
        "write_calls"
    ]:
        print(
            "    line "
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
    "Source files modified:       False"
)

print(
    "Data files modified:         False"
)

print(
    "Runtime state modified:      False"
)

print(
    "WUC executed:                False"
)

print()
print(
    "Exact scan report: "
    + str(
        OUTPUT_REPORT_PATH
    )
)

print()
print(
    "WUC EXACT STORAGE SCAN: PASS"
)

print(
    "The suspected directory and active write paths "
    "were classified without modification."
)

print("=" * 108)
