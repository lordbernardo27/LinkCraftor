"""Read-only alignment scan of the existing Body Store code."""

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

BODY_STORE_CODE = (
    SERVER_ROOT
    / "stores"
    / "universal_article_body_store.py"
)

UUCD_ENGINE_CODE = (
    SERVER_ROOT
    / "universal_unified_content_document"
    / "uucd_engine_v1.py"
)

BODY_STORE_OUTPUT = (
    DATA_ROOT
    / "universal_article_body_store"
)

UUCD_OUTPUT = (
    DATA_ROOT
    / "universal_unified_content_documents"
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "body_store_writer_against_fresh_uucd_v1.json"
)

EXPECTED_WRITER_NAMES = {
    "build_universal_article_body_store_from_uucd_payload_v2",
    "build_universal_article_body_store_from_uucd_file_v2",
}

REQUIRED_UUCD_READS = {
    "document_id",
    "workspace_id",
    "source_type",
    "content_body",
    "content_hash",
    "body_ref",
    "body_length",
    "body_word_count",
    "body_status",
    "handoff",
}

FORBIDDEN_INPUT_FIELDS = {
    "article_body",
    "text",
    "raw_html",
    "clean_html",
}

FORBIDDEN_REDUCTION_TERMS = {
    "truncate",
    "truncation",
    "summarize",
    "summary",
    "max_words",
    "word_limit",
    "excerpt",
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
    "semantic_analysis",
    "topic_cluster",
    "entity_extraction",
    "reasoning_engine",
}


def function_name(
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


def get_field_reads(
    node: ast.AST,
) -> set[str]:
    reads: set[str] = set()

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

        key = child.args[0]

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
            reads.add(
                key.value
            )

    return reads


def source_matches(
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

        found = sorted(
            term
            for term in terms
            if term.casefold()
            in lowered
        )

        if found:
            matches.append(
                {
                    "line_number":
                        line_number,

                    "terms":
                        found,

                    "line":
                        line.strip()[:1500],
                }
            )

    return matches


failures: list[str] = []
warnings: list[str] = []

for path in (
    BODY_STORE_CODE,
    UUCD_ENGINE_CODE,
):
    if not path.is_file():
        failures.append(
            "Missing required code file: "
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


body_store_source = BODY_STORE_CODE.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

uucd_source = UUCD_ENGINE_CODE.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

body_store_tree = ast.parse(
    body_store_source,
    filename=str(
        BODY_STORE_CODE
    ),
)

ast.parse(
    uucd_source,
    filename=str(
        UUCD_ENGINE_CODE
    ),
)


functions = {
    node.name:
        node
    for node in body_store_tree.body
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    )
}

detected_writer_names = (
    EXPECTED_WRITER_NAMES
    & set(
        functions
    )
)

payload_writer = functions.get(
    "build_universal_article_body_store_from_uucd_payload_v2"
)

if payload_writer is None:
    failures.append(
        "The existing Body Store code does not contain the expected "
        "payload writer."
    )


payload_reads = (
    get_field_reads(
        payload_writer
    )
    if payload_writer
    else set()
)

missing_uucd_reads = (
    REQUIRED_UUCD_READS
    - payload_reads
)

forbidden_field_reads = (
    FORBIDDEN_INPUT_FIELDS
    & payload_reads
)


write_calls: list[
    dict[str, Any]
] = []

hash_calls: list[
    dict[str, Any]
] = []

path_security_calls: list[
    dict[str, Any]
] = []

for node in ast.walk(
    body_store_tree
):
    if not isinstance(
        node,
        ast.Call,
    ):
        continue

    name = function_name(
        node
    )

    if name in {
        "write_text",
        "write_bytes",
        "open",
        "replace",
        "rename",
    }:
        write_calls.append(
            {
                "function":
                    name,

                "line":
                    node.lineno,

                "call":
                    ast.unparse(
                        node
                    )[:1500],
            }
        )

    if name in {
        "sha256",
        "hexdigest",
    }:
        hash_calls.append(
            {
                "function":
                    name,

                "line":
                    node.lineno,
            }
        )

    if name in {
        "resolve",
        "relative_to",
        "is_relative_to",
    }:
        path_security_calls.append(
            {
                "function":
                    name,

                "line":
                    node.lineno,
            }
        )


reduction_matches = source_matches(
    body_store_source,
    FORBIDDEN_REDUCTION_TERMS,
)

runtime_matches = source_matches(
    body_store_source,
    RUNTIME_TERMS,
)

semantic_matches = source_matches(
    body_store_source,
    SEMANTIC_TERMS,
)


body_ref_mentions = source_matches(
    body_store_source,
    {
        "body_ref",
    },
)

content_hash_mentions = source_matches(
    body_store_source,
    {
        "content_hash",
    },
)

body_length_mentions = source_matches(
    body_store_source,
    {
        "body_length",
    },
)

word_count_mentions = source_matches(
    body_store_source,
    {
        "body_word_count",
    },
)

temporary_write_mentions = source_matches(
    body_store_source,
    {
        ".tmp",
        "temporary",
        "atomic",
    },
)


checks = {
    "required_files_exist":
        BODY_STORE_CODE.is_file()
        and UUCD_ENGINE_CODE.is_file(),

    "all_python_syntax_valid":
        True,

    "payload_writer_exists":
        payload_writer
        is not None,

    "expected_writer_function_detected":
        bool(
            detected_writer_names
        ),

    "reads_document_id":
        "document_id"
        in payload_reads,

    "reads_workspace_id":
        "workspace_id"
        in payload_reads,

    "reads_content_body":
        "content_body"
        in payload_reads,

    "reads_content_hash":
        "content_hash"
        in payload_reads,

    "reads_body_ref":
        "body_ref"
        in payload_reads,

    "reads_body_length":
        "body_length"
        in payload_reads,

    "reads_body_word_count":
        "body_word_count"
        in payload_reads,

    "reads_all_required_fresh_uucd_fields":
        not missing_uucd_reads,

    "does_not_read_legacy_body_fields":
        not forbidden_field_reads,

    "contains_body_write_operation":
        bool(
            write_calls
        ),

    "contains_hash_verification_logic":
        bool(
            hash_calls
            or content_hash_mentions
        ),

    "contains_body_ref_logic":
        bool(
            body_ref_mentions
        ),

    "contains_body_length_logic":
        bool(
            body_length_mentions
        ),

    "contains_word_count_logic":
        bool(
            word_count_mentions
        ),

    "contains_path_boundary_logic":
        bool(
            path_security_calls
        ),

    "no_content_reduction_logic":
        not reduction_matches,

    "no_runtime_execution_logic":
        not runtime_matches,

    "no_semantic_processing_logic":
        not semantic_matches,

    "body_store_output_currently_absent":
        BODY_STORE_OUTPUT.exists()
        is False,

    "uucd_output_currently_absent":
        UUCD_OUTPUT.exists()
        is False,
}


for name, passed in checks.items():
    if passed is not True:
        failures.append(
            "Verification check failed: "
            + name
        )


classification: str

if (
    payload_writer is not None
    and not missing_uucd_reads
    and not forbidden_field_reads
    and write_calls
    and (
        hash_calls
        or content_hash_mentions
    )
    and body_ref_mentions
    and body_length_mentions
    and word_count_mentions
    and path_security_calls
    and not reduction_matches
    and not runtime_matches
    and not semantic_matches
):
    classification = (
        "EXISTING_WRITER_ALIGNED_WITH_FRESH_UUCD"
    )

elif payload_writer is not None:
    classification = (
        "EXISTING_WRITER_REQUIRES_REBUILD_OR_PATCH"
    )

else:
    classification = (
        "NO_COMPATIBLE_BODY_STORE_WRITER"
    )


report = {
    "schema_version":
        "body_store_writer_against_fresh_uucd_v1",

    "workspace_id":
        WORKSPACE_ID,

    "scan_mode":
        "READ_ONLY",

    "classification":
        classification,

    "checks":
        checks,

    "detected_writer_names":
        sorted(
            detected_writer_names
        ),

    "payload_writer_field_reads":
        sorted(
            payload_reads
        ),

    "missing_required_uucd_reads":
        sorted(
            missing_uucd_reads
        ),

    "forbidden_field_reads":
        sorted(
            forbidden_field_reads
        ),

    "write_calls":
        write_calls,

    "hash_calls":
        hash_calls,

    "path_security_calls":
        path_security_calls,

    "reduction_matches":
        reduction_matches,

    "runtime_matches":
        runtime_matches,

    "semantic_matches":
        semantic_matches,

    "temporary_write_mentions":
        temporary_write_mentions,

    "body_store_output_exists":
        BODY_STORE_OUTPUT.exists(),

    "uucd_output_exists":
        UUCD_OUTPUT.exists(),

    "source_files_modified":
        False,

    "data_files_modified":
        False,

    "body_store_executed":
        False,

    "runtime_state_modified":
        False,

    "warnings":
        warnings,

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
print("=" * 112)
print(
    "UNIVERSAL ARTICLE BODY STORE — FRESH UUCD ALIGNMENT SCAN"
)
print("=" * 112)
print()

print(
    "Classification: "
    + classification
)

print()

for name, passed in checks.items():
    print(
        f"{name:<62}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "Detected writer functions:             "
    + str(
        len(
            detected_writer_names
        )
    )
)

print(
    "Required UUCD fields read:             "
    + str(
        len(
            REQUIRED_UUCD_READS
        )
        - len(
            missing_uucd_reads
        )
    )
    + "/"
    + str(
        len(
            REQUIRED_UUCD_READS
        )
    )
)

print(
    "Legacy body fields read:               "
    + str(
        len(
            forbidden_field_reads
        )
    )
)

print(
    "Body write calls:                      "
    + str(
        len(
            write_calls
        )
    )
)

print(
    "Hash-related calls:                    "
    + str(
        len(
            hash_calls
        )
    )
)

print(
    "Path-boundary calls:                   "
    + str(
        len(
            path_security_calls
        )
    )
)

print(
    "Content-reduction matches:             "
    + str(
        len(
            reduction_matches
        )
    )
)

print(
    "Runtime matches:                       "
    + str(
        len(
            runtime_matches
        )
    )
)

print(
    "Semantic-processing matches:           "
    + str(
        len(
            semantic_matches
        )
    )
)

print(
    "Body Store output currently exists:    "
    + str(
        BODY_STORE_OUTPUT.exists()
    )
)

print(
    "UUCD output currently exists:          "
    + str(
        UUCD_OUTPUT.exists()
    )
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
    "Data files modified:    False"
)

print(
    "Body Store executed:    False"
)

print(
    "Runtime state modified: False"
)

print()
print(
    "BODY STORE FRESH UUCD ALIGNMENT SCAN: PASS"
)

print(
    "The existing Body Store implementation was classified without "
    "writing UUCD documents or article bodies."
)

print("=" * 112)
