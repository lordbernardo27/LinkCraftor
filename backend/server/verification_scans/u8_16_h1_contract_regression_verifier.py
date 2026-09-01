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
    title="Canonical Title",
    headings=None,
    text="Canonical body.",
    metadata=None,
):
    base_metadata = {
        "filename": "u8_16.txt",
        "extension": ".txt",
        "file_size": 111,
        "extraction_method": "txt_upload_v1",
        "normalization": {
            "status": "success",
            "version": "uploaded_document_normalization_v1",
            "unicode_form": "NFC",
        },
    }

    if metadata:
        base_metadata.update(
            metadata
        )

    return NormalizedUploadedDocumentContent(
        source_path="C:/immutable/u8_16.txt",
        source_type="txt",
        title=title,
        text=text,
        headings=(
            list(headings)
            if headings is not None
            else ["First Heading", "Second Heading"]
        ),
        metadata=base_metadata,
        extraction_status="success",
        extraction_confidence=0.95,
        extraction_created_at="2026-09-01T00:00:00+00:00",
        normalization_status="success",
        normalization_version="uploaded_document_normalization_v1",
        normalized_at="2026-09-01T00:00:01+00:00",
    )


print("=== U8.16 H1 CONTRACT REGRESSION VERIFICATION ===")


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
# B. First normalized heading authority
# ------------------------------------------------------------

print()
print("=== B. FIRST NORMALIZED HEADING AUTHORITY ===")

normalized = make_normalized()

normalized_before = copy.deepcopy(
    normalized
)

uduc = build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u8_16",
    document_id="doc_u8_16",
)

check(
    "H1_FROM_FIRST_NORMALIZED_HEADING",
    uduc.h1
    == "First Heading",
)

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
# C. Title fallback
# ------------------------------------------------------------

print()
print("=== C. NORMALIZED TITLE FALLBACK ===")

title_fallback = make_normalized(
    headings=[],
    title="Canonical Title",
)

title_fallback_uduc = build_uduc_from_normalized_content(
    normalized_content=title_fallback,
    workspace_id="ws_u8_16",
    document_id="doc_title_fallback",
)

check(
    "H1_FALLS_BACK_TO_NORMALIZED_TITLE",
    title_fallback_uduc.h1
    == "Canonical Title",
)

check(
    "EMPTY_HEADINGS_REMAIN_EMPTY",
    title_fallback_uduc.headings
    == [],
)


# ------------------------------------------------------------
# D. Empty fallback
# ------------------------------------------------------------

print()
print("=== D. EMPTY FALLBACK ===")

empty = make_normalized(
    title="",
    headings=[],
)

empty_uduc = build_uduc_from_normalized_content(
    normalized_content=empty,
    workspace_id="ws_u8_16",
    document_id="doc_empty",
)

check(
    "H1_EMPTY_WHEN_TITLE_AND_HEADINGS_EMPTY",
    empty_uduc.h1
    == "",
)


# ------------------------------------------------------------
# E. Legacy metadata H1 cannot override
# ------------------------------------------------------------

print()
print("=== E. LEGACY METADATA H1 IS PROVENANCE ONLY ===")

metadata_h1 = make_normalized(
    metadata={
        "h1": "Metadata H1 Must Not Win",
    },
)

metadata_h1_uduc = build_uduc_from_normalized_content(
    normalized_content=metadata_h1,
    workspace_id="ws_u8_16",
    document_id="doc_metadata_h1",
)

check(
    "METADATA_H1_CANNOT_OVERRIDE_CANONICAL_H1",
    metadata_h1_uduc.h1
    == "First Heading",
)

check(
    "METADATA_H1_DOES_NOT_MUTATE_TITLE",
    metadata_h1_uduc.title
    == "Canonical Title",
)

check(
    "METADATA_H1_DOES_NOT_MUTATE_HEADINGS",
    metadata_h1_uduc.headings
    == ["First Heading", "Second Heading"],
)


# ------------------------------------------------------------
# F. Source metadata H1 cannot override
# ------------------------------------------------------------

print()
print("=== F. SOURCE METADATA H1 IS PROVENANCE ONLY ===")

source_h1_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="ws_u8_16",
    document_id="doc_source_h1",
    source_metadata={
        "h1": "Source Metadata H1 Must Not Win",
    },
)

check(
    "SOURCE_METADATA_H1_CANNOT_OVERRIDE_CANONICAL_H1",
    source_h1_uduc.h1
    == "First Heading",
)

check(
    "SOURCE_METADATA_H1_DOES_NOT_MUTATE_TITLE",
    source_h1_uduc.title
    == "Canonical Title",
)

check(
    "SOURCE_METADATA_H1_DOES_NOT_MUTATE_HEADINGS",
    source_h1_uduc.headings
    == ["First Heading", "Second Heading"],
)


# ------------------------------------------------------------
# G. Repeated headings
# ------------------------------------------------------------

print()
print("=== G. REPEATED HEADINGS ===")

repeated = make_normalized(
    headings=[
        "Repeated Heading",
        "Repeated Heading",
    ],
)

repeated_uduc = build_uduc_from_normalized_content(
    normalized_content=repeated,
    workspace_id="ws_u8_16",
    document_id="doc_repeated",
)

check(
    "REPEATED_HEADINGS_PRESERVED",
    repeated_uduc.headings
    == [
        "Repeated Heading",
        "Repeated Heading",
    ],
)

check(
    "H1_USES_FIRST_REPEATED_HEADING",
    repeated_uduc.h1
    == "Repeated Heading",
)


# ------------------------------------------------------------
# H. No U8 whitespace cleanup
# ------------------------------------------------------------

print()
print("=== H. NO U8 H1 CLEANUP ===")

whitespace_heading = make_normalized(
    headings=[
        "  Already U7 Value  ",
    ],
)

whitespace_uduc = build_uduc_from_normalized_content(
    normalized_content=whitespace_heading,
    workspace_id="ws_u8_16",
    document_id="doc_whitespace",
)

check(
    "H1_EXACTLY_COPIES_FIRST_HEADING",
    whitespace_uduc.h1
    == "  Already U7 Value  ",
)


# ------------------------------------------------------------
# I. Serialization
# ------------------------------------------------------------

print()
print("=== I. SERIALIZATION ===")

serialized = serialize_uduc(
    uduc
)

check(
    "SERIALIZED_H1_MATCHES_OBJECT",
    serialized["h1"]
    == uduc.h1,
)


# ------------------------------------------------------------
# J. Input immutability
# ------------------------------------------------------------

print()
print("=== J. INPUT IMMUTABILITY ===")

check(
    "NORMALIZED_INPUT_UNCHANGED",
    normalized
    == normalized_before,
)


# ------------------------------------------------------------
# K. Determinism
# ------------------------------------------------------------

print()
print("=== K. DETERMINISM ===")

second = build_uduc_from_normalized_content(
    normalized_content=copy.deepcopy(
        normalized_before
    ),
    workspace_id="ws_u8_16",
    document_id="doc_u8_16",
)

check(
    "H1_DETERMINISTIC",
    second.h1
    == uduc.h1,
)


# ------------------------------------------------------------
# L. Static canonical builder inspection
# ------------------------------------------------------------

print()
print("=== L. CANONICAL BUILDER STATIC INSPECTION ===")

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
# M. Canonical H1 block present
# ------------------------------------------------------------

print()
print("=== M. CANONICAL H1 BLOCK ===")

expected_h1_block = '''    # Canonical H1 is a structural compatibility field derived
    # only from U7-normalized content.
    h1 = (
        headings[0]
        if headings
        else title
    )
'''

check(
    "CANONICAL_H1_BLOCK_PRESENT",
    expected_h1_block
    in builder_source,
)

check(
    "METADATA_H1_AUTHORITY_ABSENT",
    'meta.get("h1")'
    not in builder_source,
)

check(
    "SOURCE_METADATA_H1_AUTHORITY_ABSENT",
    'src_meta.get("h1")'
    not in builder_source,
)


# ------------------------------------------------------------
# N. No H1 cleanup / rerun
# ------------------------------------------------------------

print()
print("=== N. H1 BOUNDARY ===")

for marker in [
    ".strip()",
    "normalize_uploaded_document_v1",
    "_normalize_title",
    "_normalize_headings",
    "_normalize_horizontal_whitespace",
    "unicodedata.normalize",
    "read_text(",
    "read_bytes(",
    "open(",
    "extract_upload_document",
    "detect_upload_source_type",
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
# O. No downstream execution
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
# P. Final certification
# ------------------------------------------------------------

print()
print("=== P. U8.16 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.16_H1_CONTRACT: FAIL"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    raise RuntimeError(
        "U8.16 H1 contract regression verification failed."
    )

print(
    "U8.16_H1_CONTRACT: CERTIFIED"
)

print(
    "U8.16_H1_PRIMARY_AUTHORITY: FIRST_U7_NORMALIZED_HEADING"
)

print(
    "U8.16_H1_FALLBACK_AUTHORITY: U7_NORMALIZED_TITLE"
)

print(
    "U8.16_METADATA_H1_AUTHORITY: REMOVED"
)

print(
    "U8.16_SOURCE_METADATA_H1_AUTHORITY: REMOVED"
)

print(
    "U8.16_H1_EXTRA_CLEANUP: NO"
)

print(
    "U8.16_H1_SOURCE_REREAD: NO"
)

print(
    "U8.16_H1_EXTRACTION_RERUN: NO"
)

print(
    "U8.16_H1_NORMALIZATION_RERUN: NO"
)

print(
    "U8.16_DOWNSTREAM_EXECUTION: NO"
)

print(
    "U8.16_PRODUCTION_PATCH_OUTSTANDING: NO"
)

print(
    "U8.17_UDUC_PERSISTENCE_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U8.16_FINAL_H1_CONTRACT_REGRESSION_VERIFICATION: PASS"
)