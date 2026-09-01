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


def make_normalized(
    *,
    extraction_status="success",
    extraction_confidence=0.9375,
    extraction_created_at="2026-09-01T00:00:00.123456+00:00",
    source_type="txt",
    metadata=None,
):
    base_metadata = {
        "filename": "u8_14.txt",
        "extension": ".txt",
        "file_size": 4321,
        "extraction_method": "txt_upload_v1",
        "extractor_detail": "detail_value",
        "custom_extraction_key": "custom_value",
    }

    if metadata:
        base_metadata.update(
            metadata
        )

    return NormalizedUploadedDocumentContent(
        source_path="C:/immutable/u8_14.txt",
        source_type=source_type,
        title="Canonical Title",
        text="Canonical body.",
        headings=[
            "Canonical Heading",
        ],
        metadata=base_metadata,
        extraction_status=extraction_status,
        extraction_confidence=extraction_confidence,
        extraction_created_at=extraction_created_at,
        normalization_status="success",
        normalization_version="uploaded_document_normalization_v1",
        normalized_at="2026-09-01T00:00:01+00:00",
    )


print("=== U8.14 EXTRACTION PROVENANCE REGRESSION VERIFICATION ===")


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
    workspace_id="ws_u8_14",
    document_id="doc_u8_14",
    original_filename="u8_14.txt",
    stored_filename="stored_u8_14.txt",
    stored_path="C:/persisted/ws_u8_14/stored_u8_14.txt",
)

metadata = uduc.metadata
serialized = serialize_uduc(
    uduc
)


# ------------------------------------------------------------
# C. Top-level extraction provenance
# ------------------------------------------------------------

print()
print("=== C. TOP-LEVEL EXTRACTION PROVENANCE ===")

check(
    "EXTRACTION_STATUS_PRESERVED",
    uduc.extraction_status
    == normalized.extraction_status,
)

check(
    "EXTRACTION_CONFIDENCE_PRESERVED",
    uduc.extraction_confidence
    == normalized.extraction_confidence,
)

check(
    "EXTRACTION_CREATED_AT_PRESERVED",
    uduc.extraction_created_at
    == normalized.extraction_created_at,
)

check(
    "SERIALIZED_EXTRACTION_STATUS_PRESERVED",
    serialized["extraction_status"]
    == normalized.extraction_status,
)

check(
    "SERIALIZED_EXTRACTION_CONFIDENCE_PRESERVED",
    serialized["extraction_confidence"]
    == normalized.extraction_confidence,
)

check(
    "SERIALIZED_EXTRACTION_CREATED_AT_PRESERVED",
    serialized["extraction_created_at"]
    == normalized.extraction_created_at,
)


# ------------------------------------------------------------
# D. Confidence exactness
# ------------------------------------------------------------

print()
print("=== D. CONFIDENCE EXACTNESS ===")

for label, value in [
    ("ZERO", 0.0),
    ("FRACTION", 0.3333333333333333),
    ("ONE", 1.0),
]:
    candidate = build_uduc_from_normalized_content(
        normalized_content=make_normalized(
            extraction_confidence=value,
        ),
        workspace_id="ws_u8_14",
        document_id=f"doc_conf_{label.lower()}",
    )

    check(
        f"CONFIDENCE_{label}_EXACT",
        candidate.extraction_confidence
        == value,
    )


# ------------------------------------------------------------
# E. Timestamp parity
# ------------------------------------------------------------

print()
print("=== E. TIMESTAMP PARITY ===")

check(
    "EXTRACTION_TIMESTAMP_MATCHES_TOP_LEVEL",
    metadata.get(
        "extraction_timestamp"
    )
    == uduc.extraction_created_at,
)

check(
    "EXTRACTION_TIMESTAMP_MATCHES_U7",
    metadata.get(
        "extraction_timestamp"
    )
    == normalized.extraction_created_at,
)


# ------------------------------------------------------------
# F. Extraction method
# ------------------------------------------------------------

print()
print("=== F. EXTRACTION METHOD ===")

check(
    "CANONICAL_EXTRACTION_METHOD_PRESERVED",
    metadata.get(
        "extraction_method"
    )
    == "txt_upload_v1",
)


# ------------------------------------------------------------
# G. Source format
# ------------------------------------------------------------

print()
print("=== G. SOURCE FORMAT AUTHORITY ===")

check(
    "SOURCE_FORMAT_PRESERVES_NORMALIZED_SOURCE_TYPE",
    uduc.source_format
    == normalized.source_type,
)


# ------------------------------------------------------------
# H. File size precedence
# ------------------------------------------------------------

print()
print("=== H. FILE SIZE PRECEDENCE ===")

check(
    "CANONICAL_FILE_SIZE_PRESERVED",
    metadata.get(
        "file_size"
    )
    == 4321,
)


source_file_size_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(
        metadata={
            "file_size": None,
        }
    ),
    workspace_id="ws_u8_14",
    document_id="doc_source_file_size",
    source_metadata={
        "file_size": 9876,
    },
)

check(
    "SOURCE_METADATA_FILE_SIZE_FALLBACK_WORKS",
    source_file_size_uduc.metadata.get(
        "file_size"
    )
    == 9876,
)


legacy_bytes_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(
        metadata={
            "file_size": None,
        }
    ),
    workspace_id="ws_u8_14",
    document_id="doc_legacy_bytes",
    source_metadata={
        "file_size": None,
        "bytes": 2468,
    },
)

check(
    "LEGACY_BYTES_FALLBACK_WORKS",
    legacy_bytes_uduc.metadata.get(
        "file_size"
    )
    == 2468,
)


zero_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(
        metadata={
            "file_size": 0,
        }
    ),
    workspace_id="ws_u8_14",
    document_id="doc_zero_size",
    source_metadata={
        "file_size": 999,
        "bytes": 888,
    },
)

check(
    "ZERO_BYTE_CANONICAL_FILE_SIZE_PRESERVED",
    zero_uduc.metadata.get(
        "file_size"
    )
    == 0,
)


none_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(
        metadata={
            "file_size": None,
        }
    ),
    workspace_id="ws_u8_14",
    document_id="doc_none_size",
    source_metadata={
        "file_size": None,
        "bytes": None,
    },
)

check(
    "NO_FILE_SIZE_PROVENANCE_RETURNS_NONE",
    none_uduc.metadata.get(
        "file_size"
    )
    is None,
)


# ------------------------------------------------------------
# I. Extension provenance
# ------------------------------------------------------------

print()
print("=== I. EXTENSION PROVENANCE ===")

check(
    "EXTENSION_PRESERVED",
    metadata.get(
        "extension"
    )
    == ".txt",
)


# ------------------------------------------------------------
# J. Extractor-specific provenance
# ------------------------------------------------------------

print()
print("=== J. EXTRACTOR-SPECIFIC PROVENANCE ===")

embedded = metadata.get(
    "source_metadata",
    {},
)

check(
    "EXTRACTOR_DETAIL_PRESERVED",
    embedded.get(
        "extractor_detail"
    )
    == "detail_value",
)

check(
    "CUSTOM_EXTRACTION_KEY_PRESERVED",
    embedded.get(
        "custom_extraction_key"
    )
    == "custom_value",
)


# ------------------------------------------------------------
# K. Canonical authority isolation
# ------------------------------------------------------------

print()
print("=== K. AUTHORITY ISOLATION ===")

authority = build_uduc_from_normalized_content(
    normalized_content=make_normalized(
        metadata={
            "workspace_id": "bad_workspace",
            "document_id": "bad_document",
            "title": "bad_title",
            "content_body": "bad_body",
            "headings": [
                "bad_heading",
            ],
        }
    ),
    workspace_id="ws_authoritative",
    document_id="doc_authoritative",
    source_metadata={
        "workspace_id": "source_bad_workspace",
        "document_id": "source_bad_document",
        "title": "source_bad_title",
        "content_body": "source_bad_body",
        "headings": [
            "source_bad_heading",
        ],
    },
)

check(
    "WORKSPACE_AUTHORITY_PRESERVED",
    authority.workspace_id
    == "ws_authoritative",
)

check(
    "DOCUMENT_AUTHORITY_PRESERVED",
    authority.document_id
    == "doc_authoritative",
)

check(
    "TITLE_AUTHORITY_PRESERVED",
    authority.title
    == "Canonical Title",
)

check(
    "BODY_AUTHORITY_PRESERVED",
    authority.content_body
    == "Canonical body.",
)

check(
    "HEADINGS_AUTHORITY_PRESERVED",
    authority.headings
    == ["Canonical Heading"],
)


# ------------------------------------------------------------
# L. Input immutability
# ------------------------------------------------------------

print()
print("=== L. INPUT IMMUTABILITY ===")

check(
    "NORMALIZED_INPUT_UNCHANGED",
    normalized
    == normalized_before,
)


# ------------------------------------------------------------
# M. Determinism
# ------------------------------------------------------------

print()
print("=== M. DETERMINISM ===")

second = build_uduc_from_normalized_content(
    normalized_content=copy.deepcopy(
        normalized_before
    ),
    workspace_id="ws_u8_14",
    document_id="doc_u8_14",
    original_filename="u8_14.txt",
    stored_filename="stored_u8_14.txt",
    stored_path="C:/persisted/ws_u8_14/stored_u8_14.txt",
)

check(
    "EXTRACTION_PROVENANCE_DETERMINISTIC_EXCEPT_CREATED_AT",
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
# N. Static builder scope
# ------------------------------------------------------------

print()
print("=== N. CANONICAL BUILDER STATIC SCOPE ===")

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
# O. File-size patch presence
# ------------------------------------------------------------

print()
print("=== O. FILE SIZE PATCH PRESENCE ===")

expected_file_size_block = '''    if meta.get("file_size") is not None:
        file_size = meta.get("file_size")
    elif src_meta.get("file_size") is not None:
        file_size = src_meta.get("file_size")
    elif src_meta.get("bytes") is not None:
        file_size = src_meta.get("bytes")
    else:
        file_size = None
'''

check(
    "FILE_SIZE_PRECEDENCE_BLOCK_PRESENT",
    expected_file_size_block
    in builder_source,
)


# ------------------------------------------------------------
# P. No recomputation / source reread
# ------------------------------------------------------------

print()
print("=== P. EXTRACTION BOUNDARY ===")

for marker in [
    "extract_upload_document",
    "detect_upload_source_type",
    "read_text(",
    "read_bytes(",
    "open(",
    "zipfile",
    "mimetypes",
    "content_type",
    ".stat(",
    "getsize(",
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
# Q. No downstream execution
# ------------------------------------------------------------

print()
print("=== Q. DOWNSTREAM BOUNDARY ===")

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
# R. Final certification
# ------------------------------------------------------------

print()
print("=== R. U8.14 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.14_EXTRACTION_PROVENANCE_PRESERVATION: FAIL"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    raise RuntimeError(
        "U8.14 extraction provenance regression verification failed."
    )

print(
    "U8.14_EXTRACTION_PROVENANCE_PRESERVATION: CERTIFIED"
)

print(
    "U8.14_EXTRACTION_STATUS: PRESERVED"
)

print(
    "U8.14_EXTRACTION_CONFIDENCE: PRESERVED_EXACTLY"
)

print(
    "U8.14_EXTRACTION_CREATED_AT: PRESERVED_EXACTLY"
)

print(
    "U8.14_EXTRACTION_METHOD: PRESERVED"
)

print(
    "U8.14_FILE_SIZE_PRECEDENCE: CANONICAL_THEN_SOURCE_METADATA_THEN_LEGACY_BYTES"
)

print(
    "U8.14_ZERO_BYTE_FILE_SIZE: PRESERVED"
)

print(
    "U8.14_SOURCE_FORMAT_AUTHORITY: U7_NORMALIZED_SOURCE_TYPE"
)

print(
    "U8.14_EXTRACTION_RERUN: NO"
)

print(
    "U8.14_SOURCE_REREAD: NO"
)

print(
    "U8.14_DOWNSTREAM_EXECUTION: NO"
)

print(
    "U8.14_PRODUCTION_PATCH_OUTSTANDING: NO"
)

print(
    "U8.15_NORMALIZATION_PROVENANCE_PRESERVATION_TRANSITION: AUTHORIZED"
)

print(
    "U8.14_FINAL_EXTRACTION_PROVENANCE_REGRESSION_VERIFICATION: PASS"
)