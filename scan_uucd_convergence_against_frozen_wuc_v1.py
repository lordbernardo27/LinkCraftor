"""Read-only contract scan of UUCD convergence against frozen WUC v1."""

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

WUC_ENGINE_PATH = (
    SERVER_ROOT
    / "website_unified_content"
    / "website_unified_content_engine_v1.py"
)

UUCD_CONVERGENCE_PATH = (
    SERVER_ROOT
    / "stores"
    / "universal_unified_content_document_convergence.py"
)

BODY_STORE_PATH = (
    SERVER_ROOT
    / "stores"
    / "universal_article_body_store.py"
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "uucd_convergence_against_frozen_wuc_v1.json"
)

FROZEN_WUC_FIELDS = {
    "schema_version",
    "engine_version",
    "content_id",
    "document_id",
    "workspace_id",
    "source_type",
    "source_format",
    "source_identity",
    "title",
    "h1",
    "headings",
    "canonical_url",
    "content_body",
    "content_hash",
    "body_length",
    "body_word_count",
    "structure",
    "metadata",
    "handoff",
}

REQUIRED_UUCD_FIELDS = {
    "document_id",
    "schema_version",
    "workspace_id",
    "source_id",
    "source_type",
    "source_name",
    "source_format",
    "source_identity",
    "title",
    "h1",
    "headings",
    "canonical_url",
    "content_body",
    "structure",
    "content_hash",
    "content_ref",
    "body_status",
    "metadata",
}

FORBIDDEN_TERMS = {
    "website_unified_content_store",
    "legacy_wuc_store",
    "article_body",
    "truncate",
    "truncation",
    "summarize",
    "summary_only",
    "max_words",
    "word_limit",
    "slice_body",
}

BODY_STORE_WRITE_FUNCTIONS = {
    "build_universal_article_body_store_from_uucd_file_v2",
    "build_universal_article_body_store_from_uucd_payload_v2",
    "write_body",
    "save_body",
    "persist_body",
}

EXPECTED_FUNCTIONS = {
    "build_uucd_from_website_unified_content_v1",
    "build_and_write_uucd_from_wuc_v1",
}


def load_source(
    path: Path,
) -> str:
    return path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )


def parse_source(
    path: Path,
) -> ast.AST:
    return ast.parse(
        load_source(
            path
        ),
        filename=str(
            path
        ),
    )


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


def function_nodes(
    tree: ast.AST,
) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    result: dict[
        str,
        ast.FunctionDef | ast.AsyncFunctionDef
    ] = {}

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
                node.name
            ] = node

    return result


def dictionary_keys(
    node: ast.AST,
) -> set[str]:
    keys: set[str] = set()

    for child in ast.walk(
        node
    ):
        if not isinstance(
            child,
            ast.Dict,
        ):
            continue

        for key in child.keys:
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


def get_field_reads(
    node: ast.AST,
) -> set[str]:
    fields: set[str] = set()

    for child in ast.walk(
        node
    ):
        if not isinstance(
            child,
            ast.Call,
        ):
            continue

        if not isinstance(
            child.func,
            ast.Attribute,
        ):
            continue

        if child.func.attr != "get":
            continue

        if not child.args:
            continue

        first = child.args[
            0
        ]

        if (
            isinstance(
                first,
                ast.Constant,
            )
            and isinstance(
                first.value,
                str,
            )
        ):
            fields.add(
                first.value
            )

    return fields


def imported_modules(
    tree: ast.AST,
) -> list[str]:
    modules: list[str] = []

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            modules.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            module = str(
                node.module or ""
            )

            modules.extend(
                (
                    module
                    + "."
                    + alias.name
                ).strip(".")
                for alias in node.names
            )

    return modules


def source_lines_with_terms(
    source: str,
    terms: set[str],
) -> list[dict[str, Any]]:
    matches: list[
        dict[str, Any]
    ] = []

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):
        lowered = line.casefold()

        matched = sorted(
            term
            for term in terms
            if term in lowered
        )

        if matched:
            matches.append(
                {
                    "line_number":
                        line_number,

                    "matched_terms":
                        matched,

                    "line":
                        line.strip()[:1000],
                }
            )

    return matches


failures: list[str] = []
warnings: list[str] = []

required_files = {
    "WUC engine":
        WUC_ENGINE_PATH,

    "UUCD convergence":
        UUCD_CONVERGENCE_PATH,

    "Body Store":
        BODY_STORE_PATH,
}

for label, path in required_files.items():
    if not path.is_file():
        failures.append(
            label
            + " file is missing: "
            + str(
                path
            )
        )


trees: dict[str, ast.AST] = {}
sources: dict[str, str] = {}

if not failures:
    for label, path in required_files.items():
        source = load_source(
            path
        )

        sources[
            label
        ] = source

        try:
            trees[
                label
            ] = ast.parse(
                source,
                filename=str(
                    path
                ),
            )

        except SyntaxError as exc:
            failures.append(
                f"{label} syntax failure at line "
                f"{exc.lineno}: {exc.msg}"
            )


uucd_tree = trees.get(
    "UUCD convergence"
)

uucd_source = sources.get(
    "UUCD convergence",
    "",
)

functions = (
    function_nodes(
        uucd_tree
    )
    if uucd_tree
    else {}
)

missing_functions = (
    EXPECTED_FUNCTIONS
    - set(
        functions
    )
)

if missing_functions:
    failures.append(
        "Missing required UUCD convergence functions: "
        + ", ".join(
            sorted(
                missing_functions
            )
        )
    )


builder = functions.get(
    "build_uucd_from_website_unified_content_v1"
)

writer = functions.get(
    "build_and_write_uucd_from_wuc_v1"
)


builder_reads = (
    get_field_reads(
        builder
    )
    if builder
    else set()
)

builder_output_fields = (
    dictionary_keys(
        builder
    )
    if builder
    else set()
)


required_wuc_reads = {
    "workspace_id",
    "source_type",
    "source_format",
    "source_identity",
    "title",
    "h1",
    "headings",
    "canonical_url",
    "content_body",
    "content_hash",
    "structure",
    "metadata",
}

missing_wuc_reads = (
    required_wuc_reads
    - builder_reads
)

if missing_wuc_reads:
    failures.append(
        "UUCD builder does not explicitly consume required WUC fields: "
        + ", ".join(
            sorted(
                missing_wuc_reads
            )
        )
    )


missing_uucd_output_fields = (
    REQUIRED_UUCD_FIELDS
    - builder_output_fields
)

if missing_uucd_output_fields:
    failures.append(
        "UUCD builder output is missing required fields: "
        + ", ".join(
            sorted(
                missing_uucd_output_fields
            )
        )
    )


content_body_reads = (
    "content_body"
    in builder_reads
)

content_hash_reads = (
    "content_hash"
    in builder_reads
)

structure_reads = (
    "structure"
    in builder_reads
)

source_identity_reads = (
    "source_identity"
    in builder_reads
)


article_body_reads: list[
    dict[str, Any]
] = []

body_slicing_operations: list[
    dict[str, Any]
] = []

for node in ast.walk(
    builder
    if builder
    else ast.Module(
        body=[],
        type_ignores=[],
    )
):
    if isinstance(
        node,
        ast.Call,
    ):
        if (
            isinstance(
                node.func,
                ast.Attribute,
            )
            and node.func.attr
            == "get"
            and node.args
            and isinstance(
                node.args[
                    0
                ],
                ast.Constant,
            )
            and node.args[
                0
            ].value
            == "article_body"
        ):
            article_body_reads.append(
                {
                    "line":
                        node.lineno,

                    "call":
                        ast.unparse(
                            node
                        ),
                }
            )

    if isinstance(
        node,
        ast.Subscript,
    ):
        try:
            rendered = ast.unparse(
                node
            )

        except Exception:
            rendered = ""

        if (
            "content_body"
            in rendered
            and ":"
            in rendered
        ):
            body_slicing_operations.append(
                {
                    "line":
                        node.lineno,

                    "expression":
                        rendered,
                }
            )


forbidden_term_matches = source_lines_with_terms(
    uucd_source,
    FORBIDDEN_TERMS,
)

active_forbidden_matches = []

for match in forbidden_term_matches:
    line = match[
        "line"
    ]

    lowered = line.casefold()

    # Ignore explicit negative safety declarations.
    if any(
        phrase in lowered
        for phrase in (
            "not truncate",
            "truncation_performed\": false",
            "summarization_performed\": false",
            "article_body\" not in",
            "no article_body",
        )
    ):
        continue

    active_forbidden_matches.append(
        match
    )


body_store_calls = []

for node in ast.walk(
    uucd_tree
    if uucd_tree
    else ast.Module(
        body=[],
        type_ignores=[],
    )
):
    if not isinstance(
        node,
        ast.Call,
    ):
        continue

    name = call_name(
        node
    )

    if name in BODY_STORE_WRITE_FUNCTIONS:
        body_store_calls.append(
            {
                "function":
                    name,

                "line":
                    node.lineno,
            }
        )


imports = (
    imported_modules(
        uucd_tree
    )
    if uucd_tree
    else []
)

legacy_wuc_store_imports = [
    module
    for module in imports
    if (
        "website_unified_content_store"
        in module.casefold()
    )
]

body_store_imports = [
    module
    for module in imports
    if (
        "universal_article_body_store"
        in module.casefold()
    )
]


writer_calls = []

if writer:
    for node in ast.walk(
        writer
    ):
        if isinstance(
            node,
            ast.Call,
        ):
            writer_calls.append(
                {
                    "function":
                        call_name(
                            node
                        ),

                    "line":
                        node.lineno,

                    "call":
                        ast.unparse(
                            node
                        )[:1500],
                }
            )


writer_write_text_calls = [
    item
    for item in writer_calls
    if item[
        "function"
    ]
    in {
        "write_text",
        "dump",
        "dumps",
        "write",
    }
]


output_path_mentions = source_lines_with_terms(
    uucd_source,
    {
        "universal_unified_content_documents",
        "universal_unified_content_document",
    },
)


deleted_output_state = {
    "legacy_uucd_directory_exists": (
        DATA_ROOT
        / "universal_unified_content_documents"
    ).exists(),

    "legacy_body_store_directory_exists": (
        DATA_ROOT
        / "universal_article_body_store"
    ).exists(),
}


checks = {
    "required_files_exist":
        all(
            path.is_file()
            for path in required_files.values()
        ),

    "all_python_syntax_valid":
        len(
            trees
        )
        == len(
            required_files
        ),

    "required_uucd_functions_exist":
        not missing_functions,

    "builder_reads_content_body":
        content_body_reads,

    "builder_reads_content_hash":
        content_hash_reads,

    "builder_reads_structure":
        structure_reads,

    "builder_reads_source_identity":
        source_identity_reads,

    "builder_reads_all_required_wuc_fields":
        not missing_wuc_reads,

    "builder_outputs_all_required_uucd_fields":
        not missing_uucd_output_fields,

    "builder_does_not_read_legacy_article_body":
        not article_body_reads,

    "builder_does_not_slice_content_body":
        not body_slicing_operations,

    "no_legacy_wuc_store_import":
        not legacy_wuc_store_imports,

    "no_active_forbidden_content_reduction_logic":
        not active_forbidden_matches,

    "uucd_writer_function_writes_output":
        bool(
            writer_write_text_calls
        ),

    "uucd_output_path_is_defined":
        bool(
            output_path_mentions
        ),

    "body_store_is_not_written_inside_uucd_convergence":
        not body_store_calls,

    "legacy_uucd_output_is_currently_absent":
        deleted_output_state[
            "legacy_uucd_directory_exists"
        ]
        is False,

    "legacy_body_store_output_is_currently_absent":
        deleted_output_state[
            "legacy_body_store_directory_exists"
        ]
        is False,
}


for name, passed in checks.items():
    if passed is not True:
        failures.append(
            "Verification check failed: "
            + name
        )


if body_store_imports:
    warnings.append(
        "UUCD convergence imports Body Store code. "
        "This is acceptable only if it does not execute Body Store writes."
    )


report = {
    "schema_version":
        "uucd_convergence_against_frozen_wuc_v1",

    "workspace_id":
        WORKSPACE_ID,

    "scan_mode":
        "READ_ONLY",

    "scan_status":
        (
            "PASS"
            if not failures
            else "FAIL"
        ),

    "checks":
        checks,

    "frozen_wuc_fields":
        sorted(
            FROZEN_WUC_FIELDS
        ),

    "required_wuc_reads":
        sorted(
            required_wuc_reads
        ),

    "detected_wuc_reads":
        sorted(
            builder_reads
        ),

    "missing_wuc_reads":
        sorted(
            missing_wuc_reads
        ),

    "required_uucd_fields":
        sorted(
            REQUIRED_UUCD_FIELDS
        ),

    "detected_uucd_output_fields":
        sorted(
            builder_output_fields
        ),

    "missing_uucd_output_fields":
        sorted(
            missing_uucd_output_fields
        ),

    "article_body_reads":
        article_body_reads,

    "body_slicing_operations":
        body_slicing_operations,

    "legacy_wuc_store_imports":
        legacy_wuc_store_imports,

    "body_store_imports":
        body_store_imports,

    "body_store_write_calls":
        body_store_calls,

    "active_forbidden_matches":
        active_forbidden_matches,

    "writer_write_calls":
        writer_write_text_calls,

    "output_path_mentions":
        output_path_mentions,

    "deleted_output_state":
        deleted_output_state,

    "warnings":
        warnings,

    "failures":
        failures,

    "source_files_modified":
        False,

    "data_outputs_modified":
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
print("=" * 112)
print(
    "UUCD CONVERGENCE — FROZEN WUC CONTRACT ALIGNMENT"
)
print("=" * 112)
print()

for name, passed in checks.items():
    print(
        f"{name:<64}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "Required WUC fields read:              "
    + str(
        len(
            required_wuc_reads
        )
        - len(
            missing_wuc_reads
        )
    )
    + "/"
    + str(
        len(
            required_wuc_reads
        )
    )
)

print(
    "Required UUCD fields produced:         "
    + str(
        len(
            REQUIRED_UUCD_FIELDS
        )
        - len(
            missing_uucd_output_fields
        )
    )
    + "/"
    + str(
        len(
            REQUIRED_UUCD_FIELDS
        )
    )
)

print(
    "Legacy article_body reads:             "
    + str(
        len(
            article_body_reads
        )
    )
)

print(
    "content_body slicing operations:       "
    + str(
        len(
            body_slicing_operations
        )
    )
)

print(
    "Legacy WUC Store imports:              "
    + str(
        len(
            legacy_wuc_store_imports
        )
    )
)

print(
    "Body Store writes inside convergence:  "
    + str(
        len(
            body_store_calls
        )
    )
)

print(
    "Legacy UUCD output currently exists:   "
    + str(
        deleted_output_state[
            "legacy_uucd_directory_exists"
        ]
    )
)

print(
    "Legacy Body Store currently exists:    "
    + str(
        deleted_output_state[
            "legacy_body_store_directory_exists"
        ]
    )
)

print()
print(
    "WARNINGS"
)

if warnings:
    for warning in warnings:
        print(
            "  - "
            + warning
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
    "Alignment report: "
    + str(
        REPORT_PATH
    )
)

print()
print(
    "Source files modified:  False"
)

print(
    "Data outputs modified:  False"
)

print(
    "Runtime state modified: False"
)

print(
    "UUCD executed:          False"
)

print()

if failures:
    print(
        "UUCD CONVERGENCE ALIGNMENT: FAIL"
    )

    print(
        "Do not execute the fresh UUCD rebuild until the contract failures are resolved."
    )

    print("=" * 112)

    raise SystemExit(1)

print(
    "UUCD CONVERGENCE ALIGNMENT: PASS"
)

print(
    "The existing UUCD convergence layer accepts the frozen WUC full-body contract "
    "without legacy Store dependencies, body truncation or Body Store side effects."
)

print("=" * 112)
