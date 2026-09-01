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


print("=== U8.14 EXTRACTION PROVENANCE VERIFICATION ===")


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

serialized = serialize_uduc(
    uduc
)

metadata = uduc.metadata


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
# D. Confidence edge cases
# ------------------------------------------------------------

print()
print("=== D. EXTRACTION CONFIDENCE EDGE CASES ===")

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
# E. Extraction timestamp parity
# ------------------------------------------------------------

print()
print("=== E. EXTRACTION TIMESTAMP PARITY ===")

check(
    "METADATA_EXTRACTION_TIMESTAMP_PRESENT",
    "extraction_timestamp"
    in metadata,
)

check(
    "METADATA_EXTRACTION_TIMESTAMP_MATCHES_TOP_LEVEL",
    metadata.get(
        "extraction_timestamp"
    )
    == uduc.extraction_created_at,
)

check(
    "METADATA_EXTRACTION_TIMESTAMP_MATCHES_U7",
    metadata.get(
        "extraction_timestamp"
    )
    == normalized.extraction_created_at,
)


# ------------------------------------------------------------
# F. Extraction method provenance
# ------------------------------------------------------------

print()
print("=== F. EXTRACTION METHOD PROVENANCE ===")

check(
    "CANONICAL_EXTRACTION_METHOD_PRESERVED",
    metadata.get(
        "extraction_method"
    )
    == "txt_upload_v1",
)


legacy_method_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(
        metadata={
            "extraction_method": "",
            "method": "legacy_method_value",
        }
    ),
    workspace_id="ws_u8_14",
    document_id="doc_legacy_method",
)

check(
    "LEGACY_METHOD_FALLBACK_PRESERVED",
    legacy_method_uduc.metadata.get(
        "extraction_method"
    )
    == "legacy_method_value",
)


legacy_extractor_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(
        metadata={
            "extraction_method": "",
            "extractor": "legacy_extractor_value",
        }
    ),
    workspace_id="ws_u8_14",
    document_id="doc_legacy_extractor",
)

check(
    "LEGACY_EXTRACTOR_FALLBACK_PRESERVED",
    legacy_extractor_uduc.metadata.get(
        "extraction_method"
    )
    == "legacy_extractor_value",
)


source_fallback_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(
        metadata={
            "extraction_method": "",
            "method": "",
            "extractor": "",
        }
    ),
    workspace_id="ws_u8_14",
    document_id="doc_source_method",
    source_metadata={
        "extraction_method": "source_method_value",
    },
)

check(
    "SOURCE_METADATA_METHOD_FALLBACK_PRESERVED",
    source_fallback_uduc.metadata.get(
        "extraction_method"
    )
    == "source_method_value",
)


# ------------------------------------------------------------
# G. Source type / source format provenance
# ------------------------------------------------------------

print()
print("=== G. SOURCE TYPE / FORMAT PROVENANCE ===")

check(
    "UDUC_SOURCE_TYPE_IS_UPLOADED_DOCUMENT",
    uduc.source_type
    == "uploaded_document",
)

check(
    "SOURCE_FORMAT_PRESERVES_NORMALIZED_SOURCE_TYPE",
    uduc.source_format
    == normalized.source_type,
)


for source_type in [
    "txt",
    "markdown",
    "html",
    "docx",
]:
    candidate = build_uduc_from_normalized_content(
        normalized_content=make_normalized(
            source_type=source_type,
            metadata={
                "extension": ".wrong",
            },
        ),
        workspace_id="ws_u8_14",
        document_id=f"doc_source_{source_type}",
    )

    check(
        "SOURCE_FORMAT_FROM_NORMALIZED_SOURCE_TYPE_"
        + source_type.upper(),
        candidate.source_format
        == source_type,
    )


# ------------------------------------------------------------
# H. Extension / file size provenance
# ------------------------------------------------------------

print()
print("=== H. EXTENSION / FILE SIZE PROVENANCE ===")

check(
    "EXTENSION_PRESERVED",
    metadata.get(
        "extension"
    )
    == ".txt",
)

check(
    "FILE_SIZE_PRESERVED",
    metadata.get(
        "file_size"
    )
    == 4321,
)


# ------------------------------------------------------------
# I. Extractor-specific metadata survival
# ------------------------------------------------------------

print()
print("=== I. EXTRACTOR-SPECIFIC METADATA ===")

embedded_source_metadata = metadata.get(
    "source_metadata",
    {},
)

check(
    "SOURCE_METADATA_IS_DICT",
    isinstance(
        embedded_source_metadata,
        dict,
    ),
)

check(
    "EXTRACTOR_DETAIL_PRESERVED",
    embedded_source_metadata.get(
        "extractor_detail"
    )
    == "detail_value",
)

check(
    "CUSTOM_EXTRACTION_KEY_PRESERVED",
    embedded_source_metadata.get(
        "custom_extraction_key"
    )
    == "custom_value",
)


# ------------------------------------------------------------
# J. Provenance cannot override canonical authority
# ------------------------------------------------------------

print()
print("=== J. PROVENANCE AUTHORITY ISOLATION ===")

authority_test = make_normalized(
    metadata={
        "workspace_id": "bad_workspace",
        "document_id": "bad_document",
        "title": "bad_title",
        "content_body": "bad_body",
        "headings": [
            "bad_heading",
        ],
    }
)

authority_uduc = build_uduc_from_normalized_content(
    normalized_content=authority_test,
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
    "WORKSPACE_NOT_OVERRIDDEN_BY_PROVENANCE",
    authority_uduc.workspace_id
    == "ws_authoritative",
)

check(
    "DOCUMENT_NOT_OVERRIDDEN_BY_PROVENANCE",
    authority_uduc.document_id
    == "doc_authoritative",
)

check(
    "TITLE_NOT_OVERRIDDEN_BY_PROVENANCE",
    authority_uduc.title
    == "Canonical Title",
)

check(
    "BODY_NOT_OVERRIDDEN_BY_PROVENANCE",
    authority_uduc.content_body
    == "Canonical body.",
)

check(
    "HEADINGS_NOT_OVERRIDDEN_BY_PROVENANCE",
    authority_uduc.headings
    == ["Canonical Heading"],
)


# ------------------------------------------------------------
# K. Input immutability
# ------------------------------------------------------------

print()
print("=== K. INPUT IMMUTABILITY ===")

check(
    "NORMALIZED_INPUT_UNCHANGED",
    normalized
    == normalized_before,
)


# ------------------------------------------------------------
# L. Determinism
# ------------------------------------------------------------

print()
print("=== L. DETERMINISM ===")

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
# M. Canonical builder static scope
# ------------------------------------------------------------

print()
print("=== M. CANONICAL BUILDER STATIC SCOPE ===")

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
# N. No extraction recomputation / current-time fallback
# ------------------------------------------------------------

print()
print("=== N. NO EXTRACTION RECOMPUTATION ===")

for marker in [
    "extract_upload_document",
    "detect_upload_source_type",
    "read_text(",
    "read_bytes(",
    "open(",
    "zipfile",
    "mimetypes",
    "content_type",
]:
    check(
        "CANONICAL_BUILDER_NO_"
        + marker.upper()
        .replace("(", "")
        .replace(".", "_"),
        marker.lower()
        not in builder_source.lower(),
    )


check(
    "EXTRACTION_TIMESTAMP_NOT_REPLACED_WITH_NOW",
    '"extraction_timestamp": (\n            normalized_content.extraction_created_at\n        )'
    in builder_source,
)


# ------------------------------------------------------------
# O. No downstream work
# ------------------------------------------------------------

print()
print("=== O. DOWNSTREAM BOUNDARY ===")

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
# P. Final decision
# ------------------------------------------------------------

print()
print("=== P. U8.14 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.14_EXTRACTION_PROVENANCE_PRESERVATION: REVIEW_REQUIRED"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    print(
        "U8.14_PATCH_DECISION_REQUIRED: REVIEW_EVIDENCE"
    )

else:
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
        "U8.14_PRODUCTION_PATCH_REQUIRED: NO"
    )

    print(
        "U8.15_NORMALIZATION_PROVENANCE_PRESERVATION_TRANSITION: AUTHORIZED"
    )

    print(
        "U8.14_FINAL_EXTRACTION_PROVENANCE_VERIFICATION: PASS"
    )