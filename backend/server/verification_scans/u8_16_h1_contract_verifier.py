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


print("=== U8.16 H1 CONTRACT VERIFICATION ===")


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
# B. Baseline canonical fixture
# ------------------------------------------------------------

print()
print("=== B. BASELINE FIXTURE ===")

normalized = make_normalized()
normalized_before = copy.deepcopy(
    normalized
)

uduc = build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u8_16",
    document_id="doc_u8_16",
)

serialized = serialize_uduc(
    uduc
)


# ------------------------------------------------------------
# C. Current H1 behavior with headings
# ------------------------------------------------------------

print()
print("=== C. H1 WITH NORMALIZED HEADINGS ===")

check(
    "H1_NONEMPTY",
    isinstance(
        uduc.h1,
        str,
    )
    and bool(
        uduc.h1
    ),
)

print(
    f"H1_WITH_HEADINGS={uduc.h1!r}"
)

check(
    "TITLE_PRESERVED",
    uduc.title
    == normalized.title,
)

check(
    "HEADINGS_PRESERVED",
    uduc.headings
    == normalized.headings,
)

check(
    "BODY_PRESERVED",
    uduc.content_body
    == normalized.text,
)


# ------------------------------------------------------------
# D. H1 when headings are empty
# ------------------------------------------------------------

print()
print("=== D. H1 WITH EMPTY HEADINGS ===")

empty_headings = make_normalized(
    headings=[],
)

empty_heading_uduc = build_uduc_from_normalized_content(
    normalized_content=empty_headings,
    workspace_id="ws_u8_16",
    document_id="doc_empty_headings",
)

print(
    f"H1_WITH_EMPTY_HEADINGS={empty_heading_uduc.h1!r}"
)

check(
    "EMPTY_HEADINGS_TITLE_UNCHANGED",
    empty_heading_uduc.title
    == "Canonical Title",
)

check(
    "EMPTY_HEADINGS_LIST_UNCHANGED",
    empty_heading_uduc.headings
    == [],
)


# ------------------------------------------------------------
# E. Empty title and headings
# ------------------------------------------------------------

print()
print("=== E. EMPTY TITLE AND HEADINGS ===")

empty_all = make_normalized(
    title="",
    headings=[],
)

empty_all_uduc = build_uduc_from_normalized_content(
    normalized_content=empty_all,
    workspace_id="ws_u8_16",
    document_id="doc_empty_all",
)

print(
    f"H1_WITH_EMPTY_TITLE_AND_HEADINGS={empty_all_uduc.h1!r}"
)

check(
    "EMPTY_TITLE_REMAINS_EMPTY",
    empty_all_uduc.title
    == "",
)

check(
    "EMPTY_HEADINGS_REMAIN_EMPTY",
    empty_all_uduc.headings
    == [],
)


# ------------------------------------------------------------
# F. Repeated headings
# ------------------------------------------------------------

print()
print("=== F. REPEATED HEADINGS ===")

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

print(
    f"H1_WITH_REPEATED_HEADINGS={repeated_uduc.h1!r}"
)


# ------------------------------------------------------------
# G. metadata h1 authority probe
# ------------------------------------------------------------

print()
print("=== G. NORMALIZED METADATA H1 PROBE ===")

metadata_h1 = make_normalized(
    metadata={
        "h1": "Metadata H1",
    },
)

metadata_h1_uduc = build_uduc_from_normalized_content(
    normalized_content=metadata_h1,
    workspace_id="ws_u8_16",
    document_id="doc_metadata_h1",
)

print(
    f"H1_FROM_METADATA_PROBE={metadata_h1_uduc.h1!r}"
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

check(
    "METADATA_H1_DOES_NOT_MUTATE_BODY",
    metadata_h1_uduc.content_body
    == "Canonical body.",
)


# ------------------------------------------------------------
# H. explicit source_metadata h1 authority probe
# ------------------------------------------------------------

print()
print("=== H. SOURCE METADATA H1 PROBE ===")

source_h1_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="ws_u8_16",
    document_id="doc_source_h1",
    source_metadata={
        "h1": "Source Metadata H1",
    },
)

print(
    f"H1_FROM_SOURCE_METADATA_PROBE={source_h1_uduc.h1!r}"
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

check(
    "SOURCE_METADATA_H1_DOES_NOT_MUTATE_BODY",
    source_h1_uduc.content_body
    == "Canonical body.",
)


# ------------------------------------------------------------
# I. Input immutability
# ------------------------------------------------------------

print()
print("=== I. INPUT IMMUTABILITY ===")

check(
    "NORMALIZED_INPUT_UNCHANGED",
    normalized
    == normalized_before,
)


# ------------------------------------------------------------
# J. Serialization
# ------------------------------------------------------------

print()
print("=== J. SERIALIZATION ===")

check(
    "SERIALIZED_H1_MATCHES_OBJECT",
    serialized["h1"]
    == uduc.h1,
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
# L. Canonical builder static scope
# ------------------------------------------------------------

print()
print("=== L. CANONICAL BUILDER STATIC SCOPE ===")

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
# M. Exact H1 block discovery
# ------------------------------------------------------------

print()
print("=== M. EXACT H1 BLOCK DISCOVERY ===")

lines = builder_source.splitlines()

h1_hits = [
    i
    for i, line in enumerate(lines)
    if "h1 =" in line
]

check(
    "H1_ASSIGNMENT_FOUND",
    bool(
        h1_hits
    ),
)

if h1_hits:
    start = max(
        0,
        h1_hits[0] - 3,
    )

    end = min(
        len(lines),
        h1_hits[0] + 12,
    )

    print(
        "--- CURRENT H1 BLOCK ---"
    )

    print(
        "\n".join(
            lines[start:end]
        )
    )

    print(
        "--- END H1 BLOCK ---"
    )


# ------------------------------------------------------------
# N. No content reconstruction / rerun
# ------------------------------------------------------------

print()
print("=== N. H1 BOUNDARY ===")

for marker in [
    "read_text(",
    "read_bytes(",
    "open(",
    "extract_upload_document",
    "detect_upload_source_type",
    "normalize_uploaded_document_v1",
    "_normalize_title",
    "_normalize_headings",
    "_normalize_horizontal_whitespace",
    "unicodedata.normalize",
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
# P. Contract classification
# ------------------------------------------------------------

print()
print("=== P. U8.16 CONTRACT CLASSIFICATION ===")

print(
    f"CURRENT_H1_BASELINE={uduc.h1!r}"
)

print(
    f"CURRENT_H1_METADATA_OVERRIDE={metadata_h1_uduc.h1!r}"
)

print(
    f"CURRENT_H1_SOURCE_METADATA_OVERRIDE={source_h1_uduc.h1!r}"
)

print(
    f"CURRENT_H1_EMPTY_HEADINGS={empty_heading_uduc.h1!r}"
)

print(
    f"CURRENT_H1_EMPTY_ALL={empty_all_uduc.h1!r}"
)


# ------------------------------------------------------------
# Q. Final decision
# ------------------------------------------------------------

print()
print("=== Q. U8.16 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.16_H1_CONTRACT: REVIEW_REQUIRED"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    print(
        "U8.16_PATCH_DECISION_REQUIRED: REVIEW_EVIDENCE"
    )

else:
    print(
        "U8.16_H1_BEHAVIORAL_BASELINE: VERIFIED"
    )

    print(
        "U8.16_H1_CONTRACT: REVIEW_PRECEDENCE"
    )

    print(
        "U8.16_PATCH_DECISION_REQUIRED: REVIEW_CURRENT_H1_BLOCK"
    )