from pathlib import Path
import ast
import copy
import py_compile

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)

from backend.server.stores.uploaded_document_unified_content import (
    build_uduc_from_normalized_content,
    serialize_uduc,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def make_normalized():
    return NormalizedUploadedDocumentContent(
        source_path="C:/immutable/u8_15.txt",
        source_type="txt",
        title="Canonical Title",
        text="Canonical body.\n\nSecond paragraph.",
        headings=[
            "Canonical Heading",
        ],
        metadata={
            "filename": "u8_15.txt",
            "extension": ".txt",
            "file_size": 1234,
            "extraction_method": "txt_upload_v1",
            "normalization": {
                "status": "success",
                "version": "uploaded_document_normalization_v1",
                "unicode_form": "NFC",
                "operations": [
                    "line_endings_lf",
                    "horizontal_whitespace",
                    "paragraph_boundaries",
                    "unsafe_control_character_removal",
                ],
                "custom_normalization_key": "custom_normalization_value",
            },
        },
        extraction_status="success",
        extraction_confidence=0.95,
        extraction_created_at="2026-09-01T00:00:00+00:00",
        normalization_status="success",
        normalization_version="uploaded_document_normalization_v1",
        normalized_at="2026-09-01T00:00:01.654321+00:00",
    )


print("=== U8.15 CORRECTED NORMALIZATION PROVENANCE VERIFICATION ===")


# ------------------------------------------------------------
# A. Compile
# ------------------------------------------------------------

print()
print("=== A. COMPILE ===")

path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

compile_ok = True

try:
    py_compile.compile(
        str(path),
        doraise=True,
    )
except Exception as exc:
    compile_ok = False
    print(
        f"COMPILE_ERROR: {type(exc).__name__}: {exc}"
    )

check(
    "UDUC_MODULE_COMPILES",
    compile_ok,
)


# ------------------------------------------------------------
# B. Canonical fixture
# ------------------------------------------------------------

print()
print("=== B. CANONICAL FIXTURE ===")

normalized = make_normalized()
normalized_before = copy.deepcopy(
    normalized
)

uduc = build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u8_15",
    document_id="doc_u8_15",
    original_filename="u8_15.txt",
    stored_filename="stored_u8_15.txt",
    stored_path="C:/persisted/ws_u8_15/stored_u8_15.txt",
)

serialized = serialize_uduc(
    uduc
)

normalization_metadata = uduc.metadata.get(
    "normalization",
    {},
)


# ------------------------------------------------------------
# C. Top-level provenance
# ------------------------------------------------------------

print()
print("=== C. TOP-LEVEL NORMALIZATION PROVENANCE ===")

check(
    "NORMALIZATION_STATUS_PRESERVED",
    uduc.normalization_status
    == normalized.normalization_status,
)

check(
    "NORMALIZATION_VERSION_PRESERVED",
    uduc.normalization_version
    == normalized.normalization_version,
)

check(
    "NORMALIZED_AT_PRESERVED",
    uduc.normalized_at
    == normalized.normalized_at,
)

check(
    "SERIALIZED_NORMALIZATION_STATUS_PRESERVED",
    serialized["normalization_status"]
    == normalized.normalization_status,
)

check(
    "SERIALIZED_NORMALIZATION_VERSION_PRESERVED",
    serialized["normalization_version"]
    == normalized.normalization_version,
)

check(
    "SERIALIZED_NORMALIZED_AT_PRESERVED",
    serialized["normalized_at"]
    == normalized.normalized_at,
)


# ------------------------------------------------------------
# D. Metadata normalization provenance
# ------------------------------------------------------------

print()
print("=== D. METADATA NORMALIZATION PROVENANCE ===")

check(
    "NORMALIZATION_METADATA_IS_DICT",
    isinstance(
        normalization_metadata,
        dict,
    ),
)

check(
    "NORMALIZATION_METADATA_STATUS_PRESERVED",
    normalization_metadata.get("status")
    == "success",
)

check(
    "NORMALIZATION_METADATA_VERSION_PRESERVED",
    normalization_metadata.get("version")
    == "uploaded_document_normalization_v1",
)

check(
    "NORMALIZATION_METADATA_UNICODE_FORM_PRESERVED",
    normalization_metadata.get("unicode_form")
    == "NFC",
)

check(
    "NORMALIZATION_METADATA_OPERATIONS_PRESERVED",
    normalization_metadata.get("operations")
    == [
        "line_endings_lf",
        "horizontal_whitespace",
        "paragraph_boundaries",
        "unsafe_control_character_removal",
    ],
)

check(
    "CUSTOM_NORMALIZATION_METADATA_PRESERVED",
    normalization_metadata.get(
        "custom_normalization_key"
    )
    == "custom_normalization_value",
)


# ------------------------------------------------------------
# E. Content identity
# ------------------------------------------------------------

print()
print("=== E. CONTENT IDENTITY ===")

check(
    "TITLE_PRESERVED_EXACTLY",
    uduc.title
    == normalized.title,
)

check(
    "HEADINGS_PRESERVED_EXACTLY",
    uduc.headings
    == normalized.headings,
)

check(
    "CONTENT_BODY_PRESERVED_EXACTLY",
    uduc.content_body
    == normalized.text,
)


# ------------------------------------------------------------
# F. Input immutability
# ------------------------------------------------------------

print()
print("=== F. INPUT IMMUTABILITY ===")

check(
    "NORMALIZED_INPUT_UNCHANGED",
    normalized
    == normalized_before,
)


# ------------------------------------------------------------
# G. Determinism
# ------------------------------------------------------------

print()
print("=== G. DETERMINISM ===")

second = build_uduc_from_normalized_content(
    normalized_content=copy.deepcopy(
        normalized_before
    ),
    workspace_id="ws_u8_15",
    document_id="doc_u8_15",
    original_filename="u8_15.txt",
    stored_filename="stored_u8_15.txt",
    stored_path="C:/persisted/ws_u8_15/stored_u8_15.txt",
)

check(
    "NORMALIZATION_PROVENANCE_DETERMINISTIC_EXCEPT_CREATED_AT",
    {
        k: v
        for k, v in serialize_uduc(uduc).items()
        if k != "created_at"
    }
    ==
    {
        k: v
        for k, v in serialize_uduc(second).items()
        if k != "created_at"
    },
)


# ------------------------------------------------------------
# H. Canonical builder static scope
# ------------------------------------------------------------

print()
print("=== H. CANONICAL BUILDER STATIC SCOPE ===")

source = path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

tree = ast.parse(
    source
)

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

check(
    "CANONICAL_BUILDER_SOURCE_EXTRACTED",
    bool(
        builder_source
    ),
)


# ------------------------------------------------------------
# I. AST normalized_at authority
# ------------------------------------------------------------

print()
print("=== I. NORMALIZED_AT AST AUTHORITY ===")

normalized_at_from_u7 = False
created_at_from_now = False

for node in ast.walk(
    builder
):
    if isinstance(
        node,
        ast.Call,
    ):
        for keyword in node.keywords:
            if keyword.arg == "normalized_at":
                value = keyword.value

                normalized_at_from_u7 = (
                    isinstance(
                        value,
                        ast.Attribute,
                    )
                    and value.attr
                    == "normalized_at"
                    and isinstance(
                        value.value,
                        ast.Name,
                    )
                    and value.value.id
                    == "normalized_content"
                )

            if keyword.arg == "created_at":
                value = keyword.value

                created_at_from_now = (
                    isinstance(
                        value,
                        ast.Call,
                    )
                    and isinstance(
                        value.func,
                        ast.Name,
                    )
                    and value.func.id
                    == "_now_iso"
                )


check(
    "NORMALIZED_AT_FROM_U7_NORMALIZED_CONTENT",
    normalized_at_from_u7,
)

check(
    "UDUC_CREATED_AT_FROM_NOW_IS_SEPARATE",
    created_at_from_now,
)


# ------------------------------------------------------------
# J. No normalization rerun
# ------------------------------------------------------------

print()
print("=== J. NO NORMALIZATION RERUN ===")

for marker in [
    "normalize_uploaded_document_v1",
    "unicodedata.normalize",
    "_normalize_unicode_nfc",
    "_normalize_line_endings_lf",
    "_normalize_horizontal_whitespace",
    "_normalize_paragraph_boundaries",
    "_normalize_title",
    "_normalize_headings",
    "_remove_unsafe_control_characters",
]:
    check(
        "CANONICAL_BUILDER_NO_"
        + marker.upper()
        .replace("(", "")
        .replace(".", "_"),
        marker.lower()
        not in builder_source.lower(),
    )


# ------------------------------------------------------------
# K. No source/extraction rerun
# ------------------------------------------------------------

print()
print("=== K. SOURCE / EXTRACTION BOUNDARY ===")

for marker in [
    "extract_upload_document",
    "detect_upload_source_type",
    "read_text(",
    "read_bytes(",
    "open(",
    "zipfile",
]:
    check(
        "CANONICAL_BUILDER_NO_"
        + marker.upper()
        .replace("(", "")
        .replace(".", "_"),
        marker.lower()
        not in builder_source.lower(),
    )


# ------------------------------------------------------------
# L. No downstream execution
# ------------------------------------------------------------

print()
print("=== L. DOWNSTREAM BOUNDARY ===")

for marker in [
    "run_highlight",
    "active_target_set",
    "run_semantic",
    "semantic_runtime",
    "scorer",
    "build_uucd",
    "write_uucd",
    "current_canonical_uucd",
]:
    check(
        "CANONICAL_BUILDER_NO_"
        + marker.upper(),
        marker.lower()
        not in builder_source.lower(),
    )


# ------------------------------------------------------------
# M. Final certification
# ------------------------------------------------------------

print()
print("=== M. U8.15 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.15_NORMALIZATION_PROVENANCE_PRESERVATION: FAIL"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    raise RuntimeError(
        "U8.15 corrected normalization provenance verification failed."
    )

print(
    "U8.15_NORMALIZATION_PROVENANCE_PRESERVATION: CERTIFIED"
)

print(
    "U8.15_NORMALIZATION_STATUS: PRESERVED"
)

print(
    "U8.15_NORMALIZATION_VERSION: PRESERVED"
)

print(
    "U8.15_NORMALIZED_AT: PRESERVED_EXACTLY"
)

print(
    "U8.15_UDUC_CREATED_AT: SEPARATE_U8_TIMESTAMP"
)

print(
    "U8.15_NORMALIZATION_METADATA: PRESERVED"
)

print(
    "U8.15_CONTENT_RENORMALIZATION: NO"
)

print(
    "U8.15_SOURCE_REREAD: NO"
)

print(
    "U8.15_EXTRACTION_RERUN: NO"
)

print(
    "U8.15_DOWNSTREAM_EXECUTION: NO"
)

print(
    "U8.15_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U8.16_H1_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U8.15_FINAL_NORMALIZATION_PROVENANCE_VERIFICATION: PASS"
)