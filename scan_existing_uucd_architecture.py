"""Read-only discovery scan for the existing UUCD architecture."""

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
    / "existing_uucd_architecture_scan.json"
)

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "backups",
    "runtime_backups",
    "node_modules",
}

UUCD_TERMS = (
    "uucd",
    "universal_unified_content_document",
    "universal unified content document",
)

BODY_STORE_TERMS = (
    "universal_article_body_store",
    "article_body_store",
    "body_ref",
    "content_ref",
)

WUC_TERMS = (
    "website_unified_content",
    "wuc",
)

UPLOAD_TERMS = (
    "uploaded_document_unified_content",
    "uduc",
    "upload_extraction_result",
)

RUNTIME_TERMS = (
    "runtime_registration",
    "register_runtime",
    "job_type",
    "queue",
    "worker",
    "dispatch",
)

WRITE_FUNCTION_NAMES = {
    "write_text",
    "write_bytes",
    "dump",
    "dumps",
    "open",
    "save",
    "upsert",
    "insert",
    "write",
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


def render(
    node: ast.AST | None,
) -> str:
    if node is None:
        return ""

    try:
        return ast.unparse(
            node
        )

    except Exception:
        return node.__class__.__name__


def inspect_python_file(
    path: Path,
) -> dict[str, Any]:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    lowered = source.casefold()

    result: dict[str, Any] = {
        "path":
            relative(
                path
            ),

        "syntax_valid":
            True,

        "syntax_error":
            None,

        "functions":
            [],

        "classes":
            [],

        "imports":
            [],

        "assignments":
            [],

        "write_calls":
            [],

        "uucd_references":
            [],

        "body_store_references":
            [],

        "wuc_references":
            [],

        "upload_references":
            [],

        "runtime_references":
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

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):
        line_lowered = line.casefold()

        for field, terms in (
            (
                "uucd_references",
                UUCD_TERMS,
            ),
            (
                "body_store_references",
                BODY_STORE_TERMS,
            ),
            (
                "wuc_references",
                WUC_TERMS,
            ),
            (
                "upload_references",
                UPLOAD_TERMS,
            ),
            (
                "runtime_references",
                RUNTIME_TERMS,
            ),
        ):
            matched = sorted(
                term
                for term in terms
                if term in line_lowered
            )

            if matched:
                result[
                    field
                ].append(
                    {
                        "line_number":
                            line_number,

                        "matched_terms":
                            matched,

                        "line":
                            line.strip()[:1000],
                    }
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
            result[
                "functions"
            ].append(
                {
                    "name":
                        node.name,

                    "line_number":
                        node.lineno,

                    "arguments":
                        [
                            argument.arg
                            for argument
                            in node.args.args
                        ],

                    "return_annotation":
                        render(
                            node.returns
                        ),
                }
            )

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            result[
                "classes"
            ].append(
                {
                    "name":
                        node.name,

                    "line_number":
                        node.lineno,
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
                        "module":
                            alias.name,

                        "line_number":
                            node.lineno,
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
                        "module":
                            (
                                module
                                + "."
                                + alias.name
                            ).strip("."),

                        "line_number":
                            node.lineno,
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
                        "uucd",
                        "path",
                        "root",
                        "store",
                        "body",
                        "content",
                        "document",
                        "manifest",
                    )
                ):
                    result[
                        "assignments"
                    ].append(
                        {
                            "name":
                                name,

                            "line_number":
                                node.lineno,

                            "value":
                                render(
                                    node.value
                                )[:2000],
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

            if (
                function_name
                in WRITE_FUNCTION_NAMES
            ):
                result[
                    "write_calls"
                ].append(
                    {
                        "function":
                            function_name,

                        "line_number":
                            node.lineno,

                        "call":
                            render(
                                node
                            )[:3000],
                    }
                )

    for key in (
        "functions",
        "classes",
        "imports",
        "assignments",
        "write_calls",
        "uucd_references",
        "body_store_references",
        "wuc_references",
        "upload_references",
        "runtime_references",
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


def inspect_data_directory(
    path: Path,
) -> dict[str, Any]:
    if not path.exists():
        return {
            "path":
                relative(
                    path
                ),

            "exists":
                False,

            "file_count":
                0,

            "directory_count":
                0,

            "json_count":
                0,

            "jsonl_count":
                0,

            "html_count":
                0,

            "txt_count":
                0,

            "other_count":
                0,

            "total_bytes":
                0,

            "sample_files":
                [],
        }

    files = [
        candidate
        for candidate in path.rglob(
            "*"
        )
        if candidate.is_file()
    ]

    directories = [
        candidate
        for candidate in path.rglob(
            "*"
        )
        if candidate.is_dir()
    ]

    suffix_counts = {
        ".json":
            0,

        ".jsonl":
            0,

        ".html":
            0,

        ".txt":
            0,
    }

    other_count = 0
    total_bytes = 0

    for file_path in files:
        suffix = file_path.suffix.casefold()

        total_bytes += (
            file_path.stat().st_size
        )

        if suffix in suffix_counts:
            suffix_counts[
                suffix
            ] += 1

        else:
            other_count += 1

    return {
        "path":
            relative(
                path
            ),

        "exists":
            True,

        "file_count":
            len(
                files
            ),

        "directory_count":
            len(
                directories
            ),

        "json_count":
            suffix_counts[
                ".json"
            ],

        "jsonl_count":
            suffix_counts[
                ".jsonl"
            ],

        "html_count":
            suffix_counts[
                ".html"
            ],

        "txt_count":
            suffix_counts[
                ".txt"
            ],

        "other_count":
            other_count,

        "total_bytes":
            total_bytes,

        "sample_files":
            [
                relative(
                    file_path
                )
                for file_path in sorted(
                    files,
                    key=lambda value: (
                        value.as_posix()
                    ),
                )[
                    :20
                ]
            ],
    }


python_candidates: list[
    Path
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

    relative_path = relative(
        path
    ).casefold()

    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    ).casefold()

    if (
        any(
            term
            in relative_path
            for term in (
                "uucd",
                "universal_unified_content",
            )
        )
        or any(
            term
            in source
            for term in UUCD_TERMS
        )
    ):
        python_candidates.append(
            path
        )


python_inspections = [
    inspect_python_file(
        path
    )
    for path in sorted(
        set(
            python_candidates
        ),
        key=lambda value: (
            value.as_posix()
        ),
    )
]


data_candidates = [
    (
        DATA_ROOT
        / "universal_unified_content_document"
    ),

    (
        DATA_ROOT
        / "universal_unified_content_documents"
    ),

    (
        DATA_ROOT
        / "uucd"
    ),

    (
        DATA_ROOT
        / "uucd_store"
    ),

    (
        DATA_ROOT
        / "universal_article_body_store"
    ),

    (
        DATA_ROOT
        / "article_body_store"
    ),

    (
        DATA_ROOT
        / "runtime"
        / "uucd"
    ),

    (
        DATA_ROOT
        / "runtime"
        / "universal_unified_content_document"
    ),
]

data_inspections = [
    inspect_data_directory(
        path
    )
    for path in data_candidates
]


existing_data_directories = [
    inspection
    for inspection in data_inspections
    if inspection[
        "exists"
    ]
]


syntax_failures = [
    inspection[
        "path"
    ]
    for inspection in python_inspections
    if inspection[
        "syntax_valid"
    ]
    is not True
]


function_names = sorted(
    {
        function[
            "name"
        ]
        for inspection in python_inspections
        for function in inspection[
            "functions"
        ]
    }
)


builder_functions = sorted(
    name
    for name in function_names
    if any(
        term in name.casefold()
        for term in (
            "build",
            "create",
            "convert",
            "converge",
            "normalize",
        )
    )
)


writer_functions = sorted(
    name
    for name in function_names
    if any(
        term in name.casefold()
        for term in (
            "write",
            "save",
            "upsert",
            "persist",
            "store",
        )
    )
)


verifier_functions = sorted(
    name
    for name in function_names
    if any(
        term in name.casefold()
        for term in (
            "verify",
            "validate",
            "certify",
            "check",
        )
    )
)


files_with_wuc_support = [
    inspection[
        "path"
    ]
    for inspection in python_inspections
    if inspection[
        "wuc_references"
    ]
]


files_with_upload_support = [
    inspection[
        "path"
    ]
    for inspection in python_inspections
    if inspection[
        "upload_references"
    ]
]


files_with_body_store_support = [
    inspection[
        "path"
    ]
    for inspection in python_inspections
    if inspection[
        "body_store_references"
    ]
]


files_with_runtime_support = [
    inspection[
        "path"
    ]
    for inspection in python_inspections
    if inspection[
        "runtime_references"
    ]
]


files_with_write_calls = [
    inspection[
        "path"
    ]
    for inspection in python_inspections
    if inspection[
        "write_calls"
    ]
]


if not python_inspections:
    architecture_status = (
        "ABSENT"
    )

elif (
    builder_functions
    and writer_functions
    and existing_data_directories
):
    architecture_status = (
        "EXISTING_IMPLEMENTATION_WITH_PERSISTENCE"
    )

elif (
    builder_functions
    and writer_functions
):
    architecture_status = (
        "IMPLEMENTATION_EXISTS_DATA_NOT_CONFIRMED"
    )

elif builder_functions:
    architecture_status = (
        "PARTIAL_BUILDER_ONLY"
    )

else:
    architecture_status = (
        "REFERENCES_OR_LEGACY_ARTIFACTS_ONLY"
    )


report = {
    "schema_version":
        "existing_uucd_architecture_scan_v1",

    "workspace_id":
        WORKSPACE_ID,

    "scan_mode":
        "READ_ONLY",

    "architecture_status":
        architecture_status,

    "python_file_count":
        len(
            python_inspections
        ),

    "python_files":
        python_inspections,

    "syntax_failure_count":
        len(
            syntax_failures
        ),

    "syntax_failure_files":
        syntax_failures,

    "function_count":
        len(
            function_names
        ),

    "function_names":
        function_names,

    "builder_functions":
        builder_functions,

    "writer_functions":
        writer_functions,

    "verifier_functions":
        verifier_functions,

    "files_with_wuc_support":
        files_with_wuc_support,

    "files_with_uploaded_document_support":
        files_with_upload_support,

    "files_with_body_store_support":
        files_with_body_store_support,

    "files_with_runtime_support":
        files_with_runtime_support,

    "files_with_write_calls":
        files_with_write_calls,

    "data_directories":
        data_inspections,

    "existing_data_directory_count":
        len(
            existing_data_directories
        ),

    "existing_data_directories":
        existing_data_directories,

    "source_files_modified":
        False,

    "data_files_modified":
        False,

    "runtime_state_modified":
        False,

    "uucd_executed":
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
print("=" * 108)
print(
    "UUCD — EXISTING ARCHITECTURE DISCOVERY SCAN"
)
print("=" * 108)
print()

print(
    "Architecture status:                  "
    + architecture_status
)

print(
    "UUCD-related Python files:            "
    + str(
        len(
            python_inspections
        )
    )
)

print(
    "Syntax failures:                      "
    + str(
        len(
            syntax_failures
        )
    )
)

print(
    "Detected functions:                   "
    + str(
        len(
            function_names
        )
    )
)

print(
    "Builder/convergence functions:        "
    + str(
        len(
            builder_functions
        )
    )
)

print(
    "Writer/persistence functions:         "
    + str(
        len(
            writer_functions
        )
    )
)

print(
    "Verifier/certification functions:     "
    + str(
        len(
            verifier_functions
        )
    )
)

print(
    "Files supporting WUC input:           "
    + str(
        len(
            files_with_wuc_support
        )
    )
)

print(
    "Files supporting uploaded documents:  "
    + str(
        len(
            files_with_upload_support
        )
    )
)

print(
    "Files linked to Body Store:           "
    + str(
        len(
            files_with_body_store_support
        )
    )
)

print(
    "Files containing runtime references:  "
    + str(
        len(
            files_with_runtime_support
        )
    )
)

print(
    "Existing UUCD/body data directories:  "
    + str(
        len(
            existing_data_directories
        )
    )
)

print()
print(
    "UUCD-RELATED PYTHON FILES"
)

if python_inspections:
    for inspection in python_inspections:
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

        print(
            "    Functions: "
            + str(
                len(
                    inspection[
                        "functions"
                    ]
                )
            )
        )

        print(
            "    WUC references: "
            + str(
                len(
                    inspection[
                        "wuc_references"
                    ]
                )
            )
        )

        print(
            "    Upload references: "
            + str(
                len(
                    inspection[
                        "upload_references"
                    ]
                )
            )
        )

        print(
            "    Body Store references: "
            + str(
                len(
                    inspection[
                        "body_store_references"
                    ]
                )
            )
        )

        print(
            "    Runtime references: "
            + str(
                len(
                    inspection[
                        "runtime_references"
                    ]
                )
            )
        )

        print(
            "    Write calls: "
            + str(
                len(
                    inspection[
                        "write_calls"
                    ]
                )
            )
        )

else:
    print(
        "  None"
    )

print()
print(
    "DETECTED BUILDER / CONVERGENCE FUNCTIONS"
)

if builder_functions:
    for name in builder_functions:
        print(
            "  "
            + name
        )

else:
    print(
        "  None"
    )

print()
print(
    "DETECTED WRITER / PERSISTENCE FUNCTIONS"
)

if writer_functions:
    for name in writer_functions:
        print(
            "  "
            + name
        )

else:
    print(
        "  None"
    )

print()
print(
    "EXISTING DATA DIRECTORIES"
)

if existing_data_directories:
    for inspection in existing_data_directories:
        print()
        print(
            "  "
            + inspection[
                "path"
            ]
        )

        print(
            "    Files: "
            + str(
                inspection[
                    "file_count"
                ]
            )
        )

        print(
            "    JSON: "
            + str(
                inspection[
                    "json_count"
                ]
            )
        )

        print(
            "    JSONL: "
            + str(
                inspection[
                    "jsonl_count"
                ]
            )
        )

        print(
            "    HTML: "
            + str(
                inspection[
                    "html_count"
                ]
            )
        )

        print(
            "    TXT: "
            + str(
                inspection[
                    "txt_count"
                ]
            )
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
    "UUCD executed:          False"
)

print()
print(
    "Discovery report: "
    + str(
        REPORT_PATH
    )
)

print()
print(
    "UUCD EXISTING ARCHITECTURE SCAN: PASS"
)

print(
    "The current UUCD code, persistence, Body Store links "
    "and runtime references were discovered without modification."
)

print("=" * 108)
