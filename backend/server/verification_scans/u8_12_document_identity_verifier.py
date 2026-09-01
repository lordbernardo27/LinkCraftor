from pathlib import Path
import ast
import uuid

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)

from backend.server.stores.uploaded_document_unified_content import (
    _safe_document_id,
    build_uduc_from_normalized_content,
    serialize_uduc,
    uduc_output_path,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def make_normalized() -> NormalizedUploadedDocumentContent:
    return NormalizedUploadedDocumentContent(
        source_path="C:/immutable/document-test.txt",
        source_type="txt",
        title="Document Test",
        text="Alpha beta",
        headings=[],
        metadata={
            "document_id": "metadata_document_should_not_win",
            "source_metadata": {
                "document_id": "source_metadata_should_not_win",
            },
            "filename": "document-test.txt",
            "extension": ".txt",
        },
        extraction_status="success",
        extraction_confidence=0.95,
        extraction_created_at="2026-09-01T00:00:00+00:00",
        normalization_status="success",
        normalization_version="uploaded_document_normalization_v1",
        normalized_at="2026-09-01T00:00:01+00:00",
    )


print("=== U8.12 DOCUMENT IDENTITY VERIFICATION ===")


# ------------------------------------------------------------
# A. Inspect helper behavior
# ------------------------------------------------------------

print()
print("=== A. SAFE DOCUMENT ID BEHAVIOR ===")

cases = [
    ("valid", "doc_alpha"),
    ("uuid", str(uuid.uuid4())),
    ("surrounding_whitespace", "  doc_alpha  "),
    ("path_sensitive", "../doc:alpha/beta"),
    ("empty", ""),
    ("whitespace_only", "   "),
    ("none", None),
]

for label, value in cases:
    try:
        result = _safe_document_id(
            value,
            fallback=None,
        )
        print(
            f"{label}: INPUT={value!r} OUTPUT={result!r}"
        )
    except Exception as exc:
        print(
            f"{label}: INPUT={value!r} "
            f"ERROR={type(exc).__name__}: {exc}"
        )


# ------------------------------------------------------------
# B. Valid explicit document identity
# ------------------------------------------------------------

print()
print("=== B. VALID EXPLICIT DOCUMENT ID ===")

uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="ws_u8_12",
    document_id="doc_alpha",
    original_filename="document-test.txt",
)

check(
    "VALID_DOCUMENT_ID_PRESERVED",
    uduc.document_id == "doc_alpha",
)

serialized = serialize_uduc(
    uduc
)

check(
    "SERIALIZED_DOCUMENT_ID_MATCHES_UDUC",
    serialized["document_id"]
    == uduc.document_id,
)


# ------------------------------------------------------------
# C. UUID identity preservation
# ------------------------------------------------------------

print()
print("=== C. UUID DOCUMENT ID ===")

canonical_uuid = str(
    uuid.uuid4()
)

uuid_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="ws_u8_12",
    document_id=canonical_uuid,
    original_filename="document-test.txt",
)

check(
    "UUID_DOCUMENT_ID_PRESERVED",
    uuid_uduc.document_id
    == canonical_uuid,
)


# ------------------------------------------------------------
# D. Metadata must not override explicit identity
# ------------------------------------------------------------

print()
print("=== D. EXPLICIT AUTHORITY OVER METADATA ===")

check(
    "METADATA_DOCUMENT_DOES_NOT_OVERRIDE_EXPLICIT",
    uduc.document_id
    != make_normalized().metadata.get(
        "document_id"
    ),
)

check(
    "SOURCE_METADATA_DOCUMENT_DOES_NOT_OVERRIDE_EXPLICIT",
    uduc.document_id
    != make_normalized().metadata[
        "source_metadata"
    ].get(
        "document_id"
    ),
)

check(
    "EXPLICIT_DOCUMENT_REMAINS_AUTHORITY",
    uduc.document_id
    == "doc_alpha",
)


# ------------------------------------------------------------
# E. Surrounding whitespace
# ------------------------------------------------------------

print()
print("=== E. SURROUNDING WHITESPACE ===")

whitespace_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="ws_u8_12",
    document_id="  doc_alpha  ",
    original_filename="document-test.txt",
)

print(
    "SURROUNDING_WHITESPACE_RESULT="
    f"{whitespace_uduc.document_id!r}"
)

check(
    "SURROUNDING_WHITESPACE_NOT_UNKNOWN_DOCUMENT",
    whitespace_uduc.document_id
    != "unknown_document",
)


# ------------------------------------------------------------
# F. Path-sensitive document ID
# ------------------------------------------------------------

print()
print("=== F. PATH-SENSITIVE DOCUMENT ID ===")

unsafe_input = "../doc:alpha/beta"

unsafe_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="ws_u8_12",
    document_id=unsafe_input,
    original_filename="document-test.txt",
)

print(
    "PATH_SENSITIVE_INPUT="
    f"{unsafe_input!r}"
)

print(
    "PATH_SENSITIVE_OUTPUT="
    f"{unsafe_uduc.document_id!r}"
)

check(
    "PATH_SENSITIVE_OUTPUT_NONEMPTY",
    bool(
        unsafe_uduc.document_id
    ),
)

check(
    "PATH_SENSITIVE_OUTPUT_HAS_NO_PARENT_TRAVERSAL",
    ".." not in unsafe_uduc.document_id,
)

check(
    "PATH_SENSITIVE_OUTPUT_HAS_NO_SLASH",
    "/" not in unsafe_uduc.document_id,
)

check(
    "PATH_SENSITIVE_OUTPUT_HAS_NO_BACKSLASH",
    "\\" not in unsafe_uduc.document_id,
)


# ------------------------------------------------------------
# G. Persistence path isolation
# ------------------------------------------------------------

print()
print("=== G. PERSISTENCE PATH ISOLATION ===")

output_path = Path(
    uduc_output_path(
        unsafe_uduc.workspace_id,
        unsafe_uduc.document_id,
    )
)

print(
    f"UDUC_OUTPUT_PATH={output_path}"
)

check(
    "OUTPUT_PATH_CONTAINS_WORKSPACE_COMPONENT",
    unsafe_uduc.workspace_id
    in output_path.parts,
)

check(
    "OUTPUT_FILENAME_USES_DOCUMENT_ID",
    output_path.name
    == f"{unsafe_uduc.document_id}.json",
)

check(
    "OUTPUT_PATH_HAS_NO_PARENT_COMPONENT",
    ".." not in output_path.parts,
)


# ------------------------------------------------------------
# H. Missing document ID behavior
# ------------------------------------------------------------

print()
print("=== H. MISSING DOCUMENT ID BEHAVIOR ===")

missing_results = {}

for label, value in [
    ("empty", ""),
    ("whitespace_only", "   "),
    ("none", None),
]:
    try:
        candidate = build_uduc_from_normalized_content(
            normalized_content=make_normalized(),
            workspace_id="ws_u8_12",
            document_id=value,
            original_filename="document-test.txt",
        )

        missing_results[label] = (
            "returned",
            candidate.document_id,
        )

        print(
            f"{label}: RETURNED "
            f"{candidate.document_id!r}"
        )

    except Exception as exc:
        missing_results[label] = (
            "raised",
            type(exc).__name__,
        )

        print(
            f"{label}: RAISED "
            f"{type(exc).__name__}: {exc}"
        )


unknown_cases = [
    label
    for label, outcome in missing_results.items()
    if (
        outcome[0] == "returned"
        and outcome[1] == "unknown_document"
    )
]

fallback_cases = [
    label
    for label, outcome in missing_results.items()
    if (
        outcome[0] == "returned"
        and outcome[1]
        not in (
            "",
            None,
        )
    )
]

check(
    "MISSING_DOCUMENT_SILENT_UNKNOWN_ABSENT",
    len(unknown_cases) == 0,
)


# ------------------------------------------------------------
# I. Determinism
# ------------------------------------------------------------

print()
print("=== I. DETERMINISM ===")

first = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="ws_u8_12",
    document_id="doc_deterministic",
    original_filename="document-test.txt",
)

second = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="ws_u8_12",
    document_id="doc_deterministic",
    original_filename="document-test.txt",
)

check(
    "DOCUMENT_ID_DETERMINISTIC",
    first.document_id
    == second.document_id
    == "doc_deterministic",
)


# ------------------------------------------------------------
# J. Static authority/fallback inspection
# ------------------------------------------------------------

print()
print("=== J. STATIC DOCUMENT AUTHORITY INSPECTION ===")

module_path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

source = module_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

tree = ast.parse(source)

builder = next(
    node
    for node in tree.body
    if isinstance(
        node,
        ast.FunctionDef,
    )
    and node.name
    == "build_uduc_from_normalized_content"
)

builder_source = (
    ast.get_source_segment(
        source,
        builder,
    )
    or ""
)

safe_fn = next(
    node
    for node in tree.body
    if isinstance(
        node,
        ast.FunctionDef,
    )
    and node.name
    == "_safe_document_id"
)

safe_source = (
    ast.get_source_segment(
        source,
        safe_fn,
    )
    or ""
)

print()
print("--- _safe_document_id ---")
print(safe_source)

print()
print("--- DOCUMENT REFERENCES IN CANONICAL BUILDER ---")

for line in builder_source.splitlines():
    if "document" in line.lower():
        print(line)


check(
    "SAFE_DOCUMENT_FUNCTION_PRESENT",
    bool(safe_source),
)

check(
    "UNKNOWN_DOCUMENT_LITERAL_PRESENT",
    "unknown_document"
    in source,
)

check(
    "BUILDER_DOCUMENT_ID_PARAMETER_PRESENT",
    "document_id"
    in builder_source,
)

check(
    "NO_UUID_GENERATION_IN_CANONICAL_BUILDER",
    "uuid.uuid4"
    not in builder_source
    and "uuid4("
    not in builder_source,
)


# ------------------------------------------------------------
# K. Downstream boundary
# ------------------------------------------------------------

print()
print("=== K. DOWNSTREAM BOUNDARY ===")

forbidden = [
    "run_highlight",
    "active_target_set",
    "run_semantic",
    "semantic_runtime",
    "build_uucd",
    "write_uucd",
    "current_canonical_uucd",
]

for marker in forbidden:
    check(
        "BUILDER_NO_"
        + marker.upper(),
        marker.lower()
        not in builder_source.lower(),
    )


# ------------------------------------------------------------
# L. Final decision
# ------------------------------------------------------------

print()
print("=== L. U8.12 FINAL DECISION ===")

hard_failures = [
    name
    for name, status in results
    if (
        status != "PASS"
        and name
        != "MISSING_DOCUMENT_SILENT_UNKNOWN_ABSENT"
    )
]

if hard_failures:
    print(
        "U8.12_DOCUMENT_IDENTITY_CONTRACT: FAIL"
    )

    print(
        "HARD_FAILED_CHECKS:"
    )

    for failure in hard_failures:
        print(
            f" - {failure}"
        )

elif unknown_cases or fallback_cases:
    print(
        "U8.12_DOCUMENT_IDENTITY_CONTRACT: REVIEW_REQUIRED"
    )

    if unknown_cases:
        print(
            "U8.12_UNKNOWN_DOCUMENT_CASES:"
            + ",".join(unknown_cases)
        )

    if fallback_cases:
        print(
            "U8.12_OTHER_FALLBACK_CASES:"
            + ",".join(fallback_cases)
        )

    print(
        "U8.12_PRIMARY_DECISION:"
        " REQUIRE_EXTERNALLY_SUPPLIED_DOCUMENT_ID"
    )

    print(
        "U8.12_PATCH_DECISION_REQUIRED: YES"
    )

else:
    print(
        "U8.12_DOCUMENT_IDENTITY_CONTRACT: CERTIFIED"
    )

    print(
        "U8.12_DOCUMENT_AUTHORITY: EXTERNAL_PIPELINE_INPUT"
    )

    print(
        "U8.12_METADATA_OVERRIDE: NO"
    )

    print(
        "U8.12_SILENT_UNKNOWN_DOCUMENT: NO"
    )

    print(
        "U8.12_PATH_SAFETY: PASS"
    )

    print(
        "U8.12_UUID_GENERATION_INSIDE_UDUC: NO"
    )

    print(
        "U8.12_DETERMINISTIC: YES"
    )

    print(
        "U8.12_PRODUCTION_PATCH_REQUIRED: NO"
    )

    print(
        "U8.13_SOURCE_METADATA_CONTRACT_TRANSITION: AUTHORIZED"
    )

    print(
        "U8.12_FINAL_DOCUMENT_IDENTITY_VERIFICATION: PASS"
    )