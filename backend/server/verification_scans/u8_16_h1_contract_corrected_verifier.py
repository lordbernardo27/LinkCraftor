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
            else [
                "First Heading",
                "Second Heading",
            ]
        ),
        metadata=base_metadata,
        extraction_status="success",
        extraction_confidence=0.95,
        extraction_created_at="2026-09-01T00:00:00+00:00",
        normalization_status="success",
        normalization_version="uploaded_document_normalization_v1",
        normalized_at="2026-09-01T00:00:01+00:00",
    )


print("=== U8.16 CORRECTED H1 CONTRACT VERIFICATION ===")


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
# B. Baseline H1 authority
# ------------------------------------------------------------

print()
print("=== B. BASELINE H1 AUTHORITY ===")

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
print("=== C. TITLE FALLBACK ===")

title_fallback_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(
        headings=[],
        title="Canonical Title",
    ),
    workspace_id="ws_u8_16",
    document_id="doc_title_fallback",
)

check(
    "H1_FALLS_BACK_TO_NORMALIZED_TITLE",
    title_fallback_uduc.h1
    == "Canonical Title",
)


# ------------------------------------------------------------
# D. Empty fallback
# ------------------------------------------------------------

print()
print("=== D. EMPTY FALLBACK ===")

empty_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(
        headings=[],
        title="",
    ),
    workspace_id="ws_u8_16",
    document_id="doc_empty",
)

check(
    "H1_EMPTY_WHEN_TITLE_AND_HEADINGS_EMPTY",
    empty_uduc.h1
    == "",
)


# ------------------------------------------------------------
# E. Legacy metadata cannot override
# ------------------------------------------------------------

print()
print("=== E. METADATA H1 AUTHORITY REMOVED ===")

metadata_h1_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(
        metadata={
            "h1": "Metadata H1 Must Not Win",
        }
    ),
    workspace_id="ws_u8_16",
    document_id="doc_metadata_h1",
)

check(
    "METADATA_H1_CANNOT_OVERRIDE_CANONICAL_H1",
    metadata_h1_uduc.h1
    == "First Heading",
)


# ------------------------------------------------------------
# F. Source metadata cannot override
# ------------------------------------------------------------

print()
print("=== F. SOURCE METADATA H1 AUTHORITY REMOVED ===")

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


# ------------------------------------------------------------
# G. Repeated headings
# ------------------------------------------------------------

print()
print("=== G. REPEATED HEADINGS ===")

repeated_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(
        headings=[
            "Repeated Heading",
            "Repeated Heading",
        ],
    ),
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
# H. No H1 cleanup
# ------------------------------------------------------------

print()
print("=== H. NO H1 CLEANUP ===")

whitespace_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(
        headings=[
            "  Already U7 Value  ",
        ],
    ),
    workspace_id="ws_u8_16",
    document_id="doc_whitespace",
)

check(
    "H1_EXACTLY_COPIES_U7_HEADING",
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
# J. Immutability / determinism
# ------------------------------------------------------------

print()
print("=== J. IMMUTABILITY / DETERMINISM ===")

check(
    "NORMALIZED_INPUT_UNCHANGED",
    normalized
    == normalized_before,
)

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
# K. Canonical builder AST
# ------------------------------------------------------------

print()
print("=== K. CANONICAL BUILDER AST ===")

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
# L. H1 assignment AST contract
# ------------------------------------------------------------

print()
print("=== L. H1 ASSIGNMENT AST CONTRACT ===")

h1_assignment = None

for node in builder.body:
    if isinstance(
        node,
        ast.Assign,
    ):
        if any(
            isinstance(
                target,
                ast.Name,
            )
            and target.id
            == "h1"
            for target in node.targets
        ):
            h1_assignment = node
            break


check(
    "H1_ASSIGNMENT_FOUND",
    h1_assignment is not None,
)


h1_uses_first_heading_else_title = False
h1_contains_strip = False

if h1_assignment is not None:
    value = h1_assignment.value

    h1_uses_first_heading_else_title = (
        isinstance(
            value,
            ast.IfExp,
        )
        and isinstance(
            value.test,
            ast.Name,
        )
        and value.test.id
        == "headings"
        and isinstance(
            value.body,
            ast.Subscript,
        )
        and isinstance(
            value.body.value,
            ast.Name,
        )
        and value.body.value.id
        == "headings"
        and isinstance(
            value.orelse,
            ast.Name,
        )
        and value.orelse.id
        == "title"
    )

    h1_source = (
        ast.get_source_segment(
            source,
            h1_assignment,
        )
        or ""
    )

    h1_contains_strip = (
        ".strip("
        in h1_source
        or ".strip()"
        in h1_source
    )


check(
    "H1_AST_PRIMARY_FIRST_HEADING_FALLBACK_TITLE",
    h1_uses_first_heading_else_title,
)

check(
    "H1_ASSIGNMENT_HAS_NO_STRIP",
    not h1_contains_strip,
)


# ------------------------------------------------------------
# M. Legacy H1 authority absent
# ------------------------------------------------------------

print()
print("=== M. LEGACY H1 AUTHORITY ABSENT ===")

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
# N. No reread / rerun
# ------------------------------------------------------------

print()
print("=== N. H1 BOUNDARY ===")

for marker in [
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
        "U8.16 corrected H1 contract verification failed."
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