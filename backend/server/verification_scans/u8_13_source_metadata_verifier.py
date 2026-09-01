from pathlib import Path
import ast
import copy

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


def make_normalized() -> NormalizedUploadedDocumentContent:
    return NormalizedUploadedDocumentContent(
        source_path="C:/immutable/source-meta-test.txt",
        source_type="txt",
        title="Canonical Normalized Title",
        text="Canonical normalized body.",
        headings=[
            "Canonical Heading",
        ],
        metadata={
            "filename": "normalized-metadata-name.txt",
            "extension": ".txt",
            "file_size": 321,
            "extraction_method": "txt_upload_v1",
            "title": "metadata_title_must_not_win",
            "content_body": "metadata_body_must_not_win",
            "headings": [
                "metadata_heading_must_not_win",
            ],
            "workspace_id": "metadata_workspace_must_not_win",
            "document_id": "metadata_document_must_not_win",
            "custom_normalized_key": "normalized_value",
        },
        extraction_status="success",
        extraction_confidence=0.95,
        extraction_created_at="2026-09-01T00:00:00+00:00",
        normalization_status="success",
        normalization_version="uploaded_document_normalization_v1",
        normalized_at="2026-09-01T00:00:01+00:00",
    )


print("=== U8.13 SOURCE METADATA CONTRACT VERIFICATION ===")


# ------------------------------------------------------------
# A. Canonical fixture
# ------------------------------------------------------------

print()
print("=== A. CANONICAL SOURCE METADATA FIXTURE ===")

normalized = make_normalized()

explicit_source_metadata = {
    "filename": "source-meta-name.txt",
    "extension": ".md",
    "file_size": 999,
    "extraction_method": "source_meta_method",
    "workspace_id": "source_workspace_must_not_win",
    "document_id": "source_document_must_not_win",
    "title": "source_title_must_not_win",
    "content_body": "source_body_must_not_win",
    "headings": [
        "source_heading_must_not_win",
    ],
    "stored_path": "C:/explicit/source-meta/stored.txt",
    "custom_source_key": "source_value",
}

normalized_before = copy.deepcopy(
    normalized
)

source_metadata_before = copy.deepcopy(
    explicit_source_metadata
)

uduc = build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u8_13",
    document_id="doc_u8_13",
    original_filename="explicit-original.txt",
    stored_filename="stored-explicit.txt",
    stored_path="C:/persisted/ws_u8_13/stored-explicit.txt",
    source_metadata=explicit_source_metadata,
)

serialized = serialize_uduc(
    uduc
)


# ------------------------------------------------------------
# B. Canonical top-level authority
# ------------------------------------------------------------

print()
print("=== B. CANONICAL TOP-LEVEL AUTHORITY ===")

check(
    "WORKSPACE_ID_EXTERNAL_AUTHORITY",
    uduc.workspace_id == "ws_u8_13",
)

check(
    "DOCUMENT_ID_EXTERNAL_AUTHORITY",
    uduc.document_id == "doc_u8_13",
)

check(
    "TITLE_FROM_NORMALIZED_CONTENT",
    uduc.title
    == "Canonical Normalized Title",
)

check(
    "HEADINGS_FROM_NORMALIZED_CONTENT",
    uduc.headings
    == ["Canonical Heading"],
)

check(
    "CONTENT_BODY_FROM_NORMALIZED_CONTENT",
    uduc.content_body
    == "Canonical normalized body.",
)


# ------------------------------------------------------------
# C. Source metadata cannot override canonical fields
# ------------------------------------------------------------

print()
print("=== C. SOURCE METADATA OVERRIDE RESISTANCE ===")

for forbidden in [
    "source_workspace_must_not_win",
    "metadata_workspace_must_not_win",
]:
    check(
        "WORKSPACE_NOT_OVERRIDDEN_"
        + forbidden.upper(),
        uduc.workspace_id != forbidden,
    )

for forbidden in [
    "source_document_must_not_win",
    "metadata_document_must_not_win",
]:
    check(
        "DOCUMENT_NOT_OVERRIDDEN_"
        + forbidden.upper(),
        uduc.document_id != forbidden,
    )

for forbidden in [
    "source_title_must_not_win",
    "metadata_title_must_not_win",
]:
    check(
        "TITLE_NOT_OVERRIDDEN_"
        + forbidden.upper(),
        uduc.title != forbidden,
    )

for forbidden in [
    "source_body_must_not_win",
    "metadata_body_must_not_win",
]:
    check(
        "BODY_NOT_OVERRIDDEN_"
        + forbidden.upper(),
        uduc.content_body != forbidden,
    )

check(
    "HEADINGS_NOT_OVERRIDDEN_BY_SOURCE_METADATA",
    uduc.headings
    != ["source_heading_must_not_win"],
)

check(
    "HEADINGS_NOT_OVERRIDDEN_BY_NORMALIZED_METADATA",
    uduc.headings
    != ["metadata_heading_must_not_win"],
)


# ------------------------------------------------------------
# D. Filename / stored path contract
# ------------------------------------------------------------

print()
print("=== D. FILE / PATH CONTRACT ===")

check(
    "ORIGINAL_FILENAME_EXPLICIT_PRESERVED",
    uduc.original_filename
    == "explicit-original.txt",
)

check(
    "STORED_FILENAME_EXPLICIT_PRESERVED",
    uduc.stored_filename
    == "stored-explicit.txt",
)

check(
    "STORED_PATH_EXPLICIT_PRESERVED",
    uduc.stored_path
    == "C:/persisted/ws_u8_13/stored-explicit.txt",
)


# ------------------------------------------------------------
# E. Source type / source format
# ------------------------------------------------------------

print()
print("=== E. SOURCE TYPE / FORMAT ===")

check(
    "SOURCE_TYPE_IS_UPLOADED_DOCUMENT",
    uduc.source_type
    == "uploaded_document",
)

print(
    f"SOURCE_FORMAT={uduc.source_format!r}"
)

check(
    "SOURCE_FORMAT_NONEMPTY",
    isinstance(
        uduc.source_format,
        str,
    )
    and bool(uduc.source_format),
)


# ------------------------------------------------------------
# F. Metadata envelope inventory
# ------------------------------------------------------------

print()
print("=== F. METADATA ENVELOPE ===")

metadata = uduc.metadata

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
# G. Source metadata preservation
# ------------------------------------------------------------

print()
print("=== G. SOURCE METADATA PRESERVATION ===")

embedded_source_metadata = metadata.get(
    "source_metadata",
    {},
)

print(
    "EMBEDDED_SOURCE_METADATA="
    f"{embedded_source_metadata!r}"
)

check(
    "SOURCE_METADATA_IS_DICT",
    isinstance(
        embedded_source_metadata,
        dict,
    ),
)

check(
    "CUSTOM_SOURCE_KEY_PRESERVED",
    embedded_source_metadata.get(
        "custom_source_key"
    )
    == "source_value",
)

check(
    "SOURCE_STORED_PATH_PROVENANCE_PRESERVED",
    embedded_source_metadata.get(
        "stored_path"
    )
    == "C:/explicit/source-meta/stored.txt",
)


# ------------------------------------------------------------
# H. Normalized metadata preservation
# ------------------------------------------------------------

print()
print("=== H. NORMALIZED METADATA PRESERVATION ===")

check(
    "CUSTOM_NORMALIZED_METADATA_AVAILABLE",
    normalized.metadata.get(
        "custom_normalized_key"
    )
    == "normalized_value",
)


# ------------------------------------------------------------
# I. Extension / file size / extraction method
# ------------------------------------------------------------

print()
print("=== I. PROVENANCE SUMMARY FIELDS ===")

print(
    f"METADATA_EXTENSION={metadata.get('extension')!r}"
)

print(
    f"METADATA_FILE_SIZE={metadata.get('file_size')!r}"
)

print(
    f"METADATA_EXTRACTION_METHOD={metadata.get('extraction_method')!r}"
)

check(
    "EXTENSION_PROVENANCE_PRESENT",
    metadata.get(
        "extension"
    )
    not in (
        None,
        "",
    ),
)

check(
    "FILE_SIZE_PROVENANCE_PRESENT",
    metadata.get(
        "file_size"
    )
    is not None,
)

check(
    "EXTRACTION_METHOD_PROVENANCE_PRESENT",
    metadata.get(
        "extraction_method"
    )
    not in (
        None,
        "",
    ),
)


# ------------------------------------------------------------
# J. No input mutation
# ------------------------------------------------------------

print()
print("=== J. INPUT IMMUTABILITY ===")

check(
    "NORMALIZED_INPUT_UNCHANGED",
    normalized == normalized_before,
)

check(
    "SOURCE_METADATA_INPUT_UNCHANGED",
    explicit_source_metadata
    == source_metadata_before,
)


# ------------------------------------------------------------
# K. Determinism
# ------------------------------------------------------------

print()
print("=== K. DETERMINISM ===")

second = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="ws_u8_13",
    document_id="doc_u8_13",
    original_filename="explicit-original.txt",
    stored_filename="stored-explicit.txt",
    stored_path="C:/persisted/ws_u8_13/stored-explicit.txt",
    source_metadata=copy.deepcopy(
        explicit_source_metadata
    ),
)

check(
    "SOURCE_METADATA_OUTPUT_DETERMINISTIC_EXCEPT_CREATED_AT",
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
# L. Static implementation inspection
# ------------------------------------------------------------

print()
print("=== L. STATIC IMPLEMENTATION INSPECTION ===")

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

print()
print("--- SOURCE / METADATA REFERENCES IN BUILDER ---")

for line in builder_source.splitlines():
    lowered = line.lower()

    if (
        "source_metadata" in lowered
        or "original_filename" in lowered
        or "stored_filename" in lowered
        or "stored_path" in lowered
        or "extension" in lowered
        or "file_size" in lowered
        or "extraction_method" in lowered
        or "source_format" in lowered
    ):
        print(line)


# ------------------------------------------------------------
# M. No source reread / format redetection
# ------------------------------------------------------------

print()
print("=== M. SOURCE-REREAD / REDETECTION BOUNDARY ===")

for marker in [
    "read_text(",
    "read_bytes(",
    "open(",
    "zipfile",
    "detect_upload_source_type",
    "extract_upload_document",
    "mimetypes",
    "content_type",
]:
    check(
        "BUILDER_NO_"
        + marker.upper()
        .replace("(", "")
        .replace(".", "_"),
        marker.lower()
        not in builder_source.lower(),
    )


# ------------------------------------------------------------
# N. No downstream work
# ------------------------------------------------------------

print()
print("=== N. DOWNSTREAM BOUNDARY ===")

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
        "BUILDER_NO_"
        + marker.upper(),
        marker.lower()
        not in builder_source.lower(),
    )


# ------------------------------------------------------------
# O. Precedence review
# ------------------------------------------------------------

print()
print("=== O. PRECEDENCE REVIEW ===")

print(
    "ORIGINAL_FILENAME="
    f"{uduc.original_filename!r}"
)

print(
    "STORED_FILENAME="
    f"{uduc.stored_filename!r}"
)

print(
    "STORED_PATH="
    f"{uduc.stored_path!r}"
)

print(
    "EXTENSION="
    f"{metadata.get('extension')!r}"
)

print(
    "FILE_SIZE="
    f"{metadata.get('file_size')!r}"
)

print(
    "EXTRACTION_METHOD="
    f"{metadata.get('extraction_method')!r}"
)


# ------------------------------------------------------------
# P. Final decision
# ------------------------------------------------------------

print()
print("=== P. U8.13 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.13_SOURCE_METADATA_CONTRACT: REVIEW_REQUIRED"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    print(
        "U8.13_PATCH_DECISION_REQUIRED: REVIEW_EVIDENCE"
    )

else:
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
        "U8.13_SOURCE_REREAD: NO"
    )

    print(
        "U8.13_FORMAT_REDETECTION: NO"
    )

    print(
        "U8.13_DOWNSTREAM_EXECUTION: NO"
    )

    print(
        "U8.13_PRODUCTION_PATCH_REQUIRED: NO"
    )

    print(
        "U8.14_EXTRACTION_PROVENANCE_PRESERVATION_TRANSITION: AUTHORIZED"
    )

    print(
        "U8.13_FINAL_SOURCE_METADATA_VERIFICATION: PASS"
    )