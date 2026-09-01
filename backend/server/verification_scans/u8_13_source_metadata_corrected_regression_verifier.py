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


def make_normalized(metadata=None):
    base_metadata = {
        "filename": "normalized.txt",
        "extension": ".txt",
        "file_size": 321,
        "extraction_method": "txt_upload_v1",
        "custom_normalized_key": "normalized_value",
    }

    if metadata:
        base_metadata.update(
            metadata
        )

    return NormalizedUploadedDocumentContent(
        source_path="C:/immutable/u8_13.txt",
        source_type="txt",
        title="Canonical Title",
        text="Canonical body.",
        headings=[
            "Canonical Heading",
        ],
        metadata=base_metadata,
        extraction_status="success",
        extraction_confidence=0.95,
        extraction_created_at="2026-09-01T00:00:00+00:00",
        normalization_status="success",
        normalization_version="uploaded_document_normalization_v1",
        normalized_at="2026-09-01T00:00:01+00:00",
    )


print("=== U8.13 CORRECTED SOURCE METADATA REGRESSION VERIFICATION ===")


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

normalized = make_normalized(
    {
        "workspace_id": "metadata_workspace_must_not_win",
        "document_id": "metadata_document_must_not_win",
        "title": "metadata_title_must_not_win",
        "content_body": "metadata_body_must_not_win",
        "headings": [
            "metadata_heading_must_not_win",
        ],
    }
)

source_metadata = {
    "workspace_id": "source_workspace_must_not_win",
    "document_id": "source_document_must_not_win",
    "title": "source_title_must_not_win",
    "content_body": "source_body_must_not_win",
    "headings": [
        "source_heading_must_not_win",
    ],
    "stored_path": "C:/source/provenance.txt",
    "file_size": 999,
    "extraction_method": "source_meta_method",
    "custom_source_key": "source_value",
}

normalized_before = copy.deepcopy(
    normalized
)

source_before = copy.deepcopy(
    source_metadata
)

uduc = build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u8_13",
    document_id="doc_u8_13",
    original_filename="original-explicit.txt",
    stored_filename="stored-explicit.txt",
    stored_path="C:/persisted/ws_u8_13/stored-explicit.txt",
    source_metadata=source_metadata,
)

metadata = uduc.metadata


# ------------------------------------------------------------
# C. Canonical authority
# ------------------------------------------------------------

print()
print("=== C. CANONICAL AUTHORITY ===")

check(
    "WORKSPACE_EXTERNAL_AUTHORITY",
    uduc.workspace_id
    == "ws_u8_13",
)

check(
    "DOCUMENT_EXTERNAL_AUTHORITY",
    uduc.document_id
    == "doc_u8_13",
)

check(
    "TITLE_FROM_NORMALIZED_CONTENT",
    uduc.title
    == "Canonical Title",
)

check(
    "HEADINGS_FROM_NORMALIZED_CONTENT",
    uduc.headings
    == ["Canonical Heading"],
)

check(
    "BODY_FROM_NORMALIZED_CONTENT",
    uduc.content_body
    == "Canonical body.",
)


# ------------------------------------------------------------
# D. Transport fields
# ------------------------------------------------------------

print()
print("=== D. TRANSPORT FIELDS ===")

check(
    "ORIGINAL_FILENAME_EXPLICIT",
    uduc.original_filename
    == "original-explicit.txt",
)

check(
    "STORED_FILENAME_EXPLICIT",
    uduc.stored_filename
    == "stored-explicit.txt",
)

check(
    "STORED_PATH_EXPLICIT",
    uduc.stored_path
    == "C:/persisted/ws_u8_13/stored-explicit.txt",
)


# ------------------------------------------------------------
# E. Metadata envelope
# ------------------------------------------------------------

print()
print("=== E. METADATA ENVELOPE ===")

for key in [
    "extension",
    "file_size",
    "extraction_method",
    "extraction_timestamp",
    "paragraph_count",
    "heading_count",
    "line_count",
    "source_metadata",
    "normalization",
    "boundary",
]:
    check(
        "METADATA_KEY_PRESENT_"
        + key.upper(),
        key in metadata,
    )


# ------------------------------------------------------------
# F. Extraction method precedence
# ------------------------------------------------------------

print()
print("=== F. EXTRACTION METHOD PRECEDENCE ===")

check(
    "CANONICAL_EXTRACTION_METHOD_WINS",
    metadata.get(
        "extraction_method"
    )
    == "txt_upload_v1",
)


legacy_method_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(
        {
            "extraction_method": "",
            "method": "legacy_method_value",
        }
    ),
    workspace_id="ws_u8_13",
    document_id="doc_legacy_method",
)

check(
    "LEGACY_METHOD_FALLBACK_WORKS",
    legacy_method_uduc.metadata.get(
        "extraction_method"
    )
    == "legacy_method_value",
)


legacy_extractor_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(
        {
            "extraction_method": "",
            "extractor": "legacy_extractor_value",
        }
    ),
    workspace_id="ws_u8_13",
    document_id="doc_legacy_extractor",
)

check(
    "LEGACY_EXTRACTOR_FALLBACK_WORKS",
    legacy_extractor_uduc.metadata.get(
        "extraction_method"
    )
    == "legacy_extractor_value",
)


source_fallback_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(
        {
            "extraction_method": "",
            "method": "",
            "extractor": "",
        }
    ),
    workspace_id="ws_u8_13",
    document_id="doc_source_fallback",
    source_metadata={
        "extraction_method": "source_fallback_value",
    },
)

check(
    "SOURCE_METADATA_EXTRACTION_METHOD_FALLBACK_WORKS",
    source_fallback_uduc.metadata.get(
        "extraction_method"
    )
    == "source_fallback_value",
)


empty_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(
        {
            "extraction_method": "",
            "method": "",
            "extractor": "",
        }
    ),
    workspace_id="ws_u8_13",
    document_id="doc_empty_method",
    source_metadata={},
)

check(
    "NO_METHOD_PROVENANCE_FALLS_BACK_EMPTY",
    empty_uduc.metadata.get(
        "extraction_method"
    )
    == "",
)


# ------------------------------------------------------------
# G. Source metadata preservation
# ------------------------------------------------------------

print()
print("=== G. SOURCE METADATA PRESERVATION ===")

embedded = metadata.get(
    "source_metadata",
    {},
)

check(
    "SOURCE_METADATA_DICT_PRESERVED",
    isinstance(
        embedded,
        dict,
    ),
)

check(
    "CUSTOM_SOURCE_KEY_PRESERVED",
    embedded.get(
        "custom_source_key"
    )
    == "source_value",
)

check(
    "SOURCE_STORED_PATH_PRESERVED",
    embedded.get(
        "stored_path"
    )
    == "C:/source/provenance.txt",
)


# ------------------------------------------------------------
# H. Input immutability
# ------------------------------------------------------------

print()
print("=== H. INPUT IMMUTABILITY ===")

check(
    "NORMALIZED_INPUT_UNCHANGED",
    normalized
    == normalized_before,
)

check(
    "SOURCE_METADATA_INPUT_UNCHANGED",
    source_metadata
    == source_before,
)


# ------------------------------------------------------------
# I. Determinism
# ------------------------------------------------------------

print()
print("=== I. DETERMINISM ===")

second = build_uduc_from_normalized_content(
    normalized_content=copy.deepcopy(
        normalized_before
    ),
    workspace_id="ws_u8_13",
    document_id="doc_u8_13",
    original_filename="original-explicit.txt",
    stored_filename="stored-explicit.txt",
    stored_path="C:/persisted/ws_u8_13/stored-explicit.txt",
    source_metadata=copy.deepcopy(
        source_before
    ),
)

check(
    "SOURCE_METADATA_DETERMINISTIC_EXCEPT_CREATED_AT",
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
# J. Static builder extraction
# ------------------------------------------------------------

print()
print("=== J. CANONICAL BUILDER STATIC SCOPE ===")

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
# K. Static patch presence
# ------------------------------------------------------------

print()
print("=== K. PATCH PRESENCE ===")

expected_order = '''        "extraction_method": (
            meta.get("extraction_method")
            or meta.get("method")
            or meta.get("extractor")
            or src_meta.get("extraction_method")
            or ""
        ),
'''

check(
    "EXTRACTION_METHOD_PRECEDENCE_BLOCK_PRESENT",
    expected_order
    in builder_source,
)


# ------------------------------------------------------------
# L. Correctly scoped U8 boundary
# ------------------------------------------------------------

print()
print("=== L. CANONICAL BUILDER BOUNDARY ===")

for marker in [
    "read_text(",
    "read_bytes(",
    "open(",
    "zipfile",
    "detect_upload_source_type",
    "extract_upload_document",
    "mimetypes",
    "content_type",
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
        + marker.upper()
        .replace("(", "")
        .replace(".", "_"),
        marker.lower()
        not in builder_source.lower(),
    )


# ------------------------------------------------------------
# M. Final certification
# ------------------------------------------------------------

print()
print("=== M. U8.13 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.13_SOURCE_METADATA_CONTRACT: FAIL"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    raise RuntimeError(
        "U8.13 corrected source metadata regression verification failed."
    )

print(
    "U8.13_SOURCE_METADATA_CONTRACT: CERTIFIED"
)

print(
    "U8.13_CANONICAL_CONTENT_AUTHORITY: U7_NORMALIZED_CONTENT"
)

print(
    "U8.13_IDENTITY_AUTHORITY: EXTERNAL_PIPELINE_INPUT"
)

print(
    "U8.13_SOURCE_METADATA_ROLE: PROVENANCE_ONLY"
)

print(
    "U8.13_EXTRACTION_METHOD_PRECEDENCE: CANONICAL_THEN_LEGACY_THEN_SOURCE_METADATA"
)

print(
    "U8.13_SOURCE_REREAD: NO"
)

print(
    "U8.13_FORMAT_REDETECTION: NO"
)

print(
    "U8.13_DOWNSTREAM_EXECUTION: NO"
)

print(
    "U8.13_PRODUCTION_PATCH_OUTSTANDING: NO"
)

print(
    "U8.14_EXTRACTION_PROVENANCE_PRESERVATION_TRANSITION: AUTHORIZED"
)

print(
    "U8.13_FINAL_SOURCE_METADATA_REGRESSION_VERIFICATION: PASS"
)