from __future__ import annotations

from backend.server.stores.upload_document_extractor import (
    UploadExtractionResult,
)

from backend.server.stores.upload_document_normalizer import (
    normalize_uploaded_document_v1,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def make_result(
    *,
    title: str,
    text: str,
    headings: list[str],
) -> UploadExtractionResult:
    return UploadExtractionResult(
        source_path="C:/immutable/source.txt",
        source_type="txt",
        title=title,
        text=text,
        headings=headings,
        metadata={
            "filename": "source.txt",
            "custom": "preserve-me",
        },
        extraction_status="success",
        extraction_confidence=0.95,
        created_at="2026-08-31T00:00:00+00:00",
    )


print("=== U7.11 - CONTROL CHARACTER HANDLING VERIFICATION ===")


# ------------------------------------------------------------
# A. C0 controls removed
# ------------------------------------------------------------

print()
print("=== A. C0 CONTROL REMOVAL ===")

c0_samples = [
    "\u0000",
    "\u0001",
    "\u0002",
    "\u0003",
    "\u0004",
    "\u0005",
    "\u0006",
    "\u0007",
    "\u0008",
    "\u000B",
    "\u000C",
    "\u000E",
    "\u000F",
    "\u0010",
    "\u0011",
    "\u0012",
    "\u0013",
    "\u0014",
    "\u0015",
    "\u0016",
    "\u0017",
    "\u0018",
    "\u0019",
    "\u001A",
    "\u001B",
    "\u001C",
    "\u001D",
    "\u001E",
    "\u001F",
]

source = "A" + "".join(c0_samples) + "B"

result = normalize_uploaded_document_v1(
    make_result(
        title=source,
        text=source,
        headings=[source],
    )
)

check(
    "C0_REMOVED_FROM_TITLE",
    result.title == "AB",
)

check(
    "C0_REMOVED_FROM_TEXT",
    result.text == "AB",
)

check(
    "C0_REMOVED_FROM_HEADINGS",
    result.headings == ["AB"],
)


# ------------------------------------------------------------
# B. LF preserved
# ------------------------------------------------------------

print()
print("=== B. LF PRESERVATION ===")

source = "A\nB\n\nC"

result = normalize_uploaded_document_v1(
    make_result(
        title=source,
        text=source,
        headings=[source],
    )
)

check(
    "LF_PRESERVED_IN_TITLE",
    result.title == source,
)

check(
    "LF_PRESERVED_IN_TEXT",
    result.text == source,
)

check(
    "LF_PRESERVED_IN_HEADING",
    result.headings == [source],
)


# ------------------------------------------------------------
# C. DEL removed
# ------------------------------------------------------------

print()
print("=== C. DEL REMOVAL ===")

source = "A\u007FB"

result = normalize_uploaded_document_v1(
    make_result(
        title=source,
        text=source,
        headings=[source],
    )
)

check(
    "DEL_REMOVED",
    result.title == "AB"
    and result.text == "AB"
    and result.headings == ["AB"],
)


# ------------------------------------------------------------
# D. C1 controls removed
# ------------------------------------------------------------

print()
print("=== D. C1 CONTROL REMOVAL ===")

c1 = "".join(
    chr(codepoint)
    for codepoint in range(0x0080, 0x00A0)
)

source = "A" + c1 + "B"

result = normalize_uploaded_document_v1(
    make_result(
        title=source,
        text=source,
        headings=[source],
    )
)

check(
    "C1_REMOVED_FROM_TITLE",
    result.title == "AB",
)

check(
    "C1_REMOVED_FROM_TEXT",
    result.text == "AB",
)

check(
    "C1_REMOVED_FROM_HEADINGS",
    result.headings == ["AB"],
)


# ------------------------------------------------------------
# E. FEFF removed
# ------------------------------------------------------------

print()
print("=== E. FEFF ARTIFACT REMOVAL ===")

source = "A\uFEFFB"

result = normalize_uploaded_document_v1(
    make_result(
        title=source,
        text=source,
        headings=[source],
    )
)

check(
    "FEFF_REMOVED_FROM_TITLE",
    result.title == "AB",
)

check(
    "FEFF_REMOVED_FROM_TEXT",
    result.text == "AB",
)

check(
    "FEFF_REMOVED_FROM_HEADINGS",
    result.headings == ["AB"],
)


# ------------------------------------------------------------
# F. NBSP preserved
# ------------------------------------------------------------

print()
print("=== F. NBSP PRESERVATION ===")

nbsp = "\u00A0"
source = f"A{nbsp}B"

result = normalize_uploaded_document_v1(
    make_result(
        title=source,
        text=source,
        headings=[source],
    )
)

check(
    "NBSP_PRESERVED",
    result.title == source
    and result.text == source
    and result.headings == [source],
)


# ------------------------------------------------------------
# G. ZWJ / ZWNJ preserved
# ------------------------------------------------------------

print()
print("=== G. ZERO-WIDTH SCRIPT CHARACTER PRESERVATION ===")

zwj = "\u200D"
zwnj = "\u200C"

source = f"A{zwj}B{zwnj}C"

result = normalize_uploaded_document_v1(
    make_result(
        title=source,
        text=source,
        headings=[source],
    )
)

check(
    "ZWJ_PRESERVED",
    zwj in result.title
    and zwj in result.text
    and zwj in result.headings[0],
)

check(
    "ZWNJ_PRESERVED",
    zwnj in result.title
    and zwnj in result.text
    and zwnj in result.headings[0],
)


# ------------------------------------------------------------
# H. Directional formatting preserved
# ------------------------------------------------------------

print()
print("=== H. DIRECTIONAL FORMAT PRESERVATION ===")

lrm = "\u200E"
rlm = "\u200F"

source = f"A{lrm}B{rlm}C"

result = normalize_uploaded_document_v1(
    make_result(
        title=source,
        text=source,
        headings=[source],
    )
)

check(
    "LRM_PRESERVED",
    lrm in result.text,
)

check(
    "RLM_PRESERVED",
    rlm in result.text,
)


# ------------------------------------------------------------
# I. Heading emptied by control removal
# ------------------------------------------------------------

print()
print("=== I. EMPTY HEADING AFTER CONTROL REMOVAL ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="Body",
        headings=[
            "\u0000\u0001",
            "Valid",
        ],
    )
)

check(
    "CONTROL_ONLY_HEADING_REMOVED",
    result.headings == ["Valid"],
)


# ------------------------------------------------------------
# J. U7.5 Unicode regression
# ------------------------------------------------------------

print()
print("=== J. U7.5 REGRESSION ===")

decomposed = "Cafe\u0301"

result = normalize_uploaded_document_v1(
    make_result(
        title=decomposed,
        text=decomposed,
        headings=[decomposed],
    )
)

check(
    "UNICODE_NFC_STILL_ACTIVE",
    result.title == "Café"
    and result.text == "Café"
    and result.headings == ["Café"],
)


# ------------------------------------------------------------
# K. U7.6 line-ending regression
# ------------------------------------------------------------

print()
print("=== K. U7.6 REGRESSION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="A\r\nB\rC",
        text="A\r\nB\rC",
        headings=["H\r\n1"],
    )
)

check(
    "LINE_ENDINGS_STILL_NORMALIZED",
    result.title == "A\nB\nC"
    and result.text == "A\nB\nC"
    and result.headings == ["H\n1"],
)


# ------------------------------------------------------------
# L. U7.7 whitespace regression
# ------------------------------------------------------------

print()
print("=== L. U7.7 REGRESSION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="  A\t  B  ",
        text="  A\t  B  ",
        headings=["  H\t  1  "],
    )
)

check(
    "WHITESPACE_NORMALIZATION_STILL_ACTIVE",
    result.title == "A B"
    and result.text == "A B"
    and result.headings == ["H 1"],
)


# ------------------------------------------------------------
# M. U7.8 paragraph regression
# ------------------------------------------------------------

print()
print("=== M. U7.8 REGRESSION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="\n\nA\n\n\n\nB\n\n",
        headings=[],
    )
)

check(
    "PARAGRAPH_NORMALIZATION_STILL_ACTIVE",
    result.text == "A\n\nB",
)


# ------------------------------------------------------------
# N. U7.9 heading regression
# ------------------------------------------------------------

print()
print("=== N. U7.9 REGRESSION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="Body",
        headings=[
            "",
            "  First  ",
            "  First  ",
        ],
    )
)

check(
    "HEADING_NORMALIZATION_STILL_ACTIVE",
    result.headings
    == [
        "First",
        "First",
    ],
)


# ------------------------------------------------------------
# O. U7.10 title regression
# ------------------------------------------------------------

print()
print("=== O. U7.10 REGRESSION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="",
        text="Body",
        headings=["Heading"],
    )
)

check(
    "EMPTY_TITLE_STILL_PRESERVED",
    result.title == "",
)


# ------------------------------------------------------------
# P. Metadata operation order
# ------------------------------------------------------------

print()
print("=== P. NORMALIZATION METADATA ===")

operations = (
    result.metadata
    .get("normalization", {})
    .get("operations")
)

check(
    "NORMALIZATION_OPERATIONS_ORDER",
    operations
    == [
        "unicode_nfc",
        "line_endings_lf",
        "horizontal_whitespace",
        "paragraph_boundaries",
        "heading_normalization",
        "title_normalization",
        "control_character_handling",
    ],
)


# ------------------------------------------------------------
# Q. Provenance preservation
# ------------------------------------------------------------

print()
print("=== Q. PROVENANCE PRESERVATION ===")

check(
    "SOURCE_PATH_PRESERVED",
    result.source_path
    == "C:/immutable/source.txt",
)

check(
    "SOURCE_TYPE_PRESERVED",
    result.source_type == "txt",
)

check(
    "EXTRACTION_STATUS_PRESERVED",
    result.extraction_status == "success",
)

check(
    "EXTRACTION_CONFIDENCE_PRESERVED",
    result.extraction_confidence == 0.95,
)

check(
    "EXTRACTION_TIMESTAMP_PRESERVED",
    result.extraction_created_at
    == "2026-08-31T00:00:00+00:00",
)

check(
    "CUSTOM_METADATA_PRESERVED",
    result.metadata.get("custom")
    == "preserve-me",
)


# ------------------------------------------------------------
# R. Determinism
# ------------------------------------------------------------

print()
print("=== R. DETERMINISM ===")

source = make_result(
    title=" A\u0000 B ",
    text=" A\u0001 B\n\n\nC\uFEFFD ",
    headings=[
        " H\u0002 1 ",
        " H\u0002 1 ",
    ],
)

first = normalize_uploaded_document_v1(
    source
)

second = normalize_uploaded_document_v1(
    source
)

check(
    "DETERMINISTIC_TITLE",
    first.title == second.title,
)

check(
    "DETERMINISTIC_TEXT",
    first.text == second.text,
)

check(
    "DETERMINISTIC_HEADINGS",
    first.headings == second.headings,
)


# ------------------------------------------------------------
# S. Input immutability
# ------------------------------------------------------------

print()
print("=== S. INPUT IMMUTABILITY ===")

original = make_result(
    title=" A\u0000 B ",
    text=" C\u0001 D ",
    headings=[" H\u0002 1 "],
)

before = (
    original.title,
    original.text,
    list(original.headings),
    dict(original.metadata),
)

normalize_uploaded_document_v1(
    original
)

after = (
    original.title,
    original.text,
    list(original.headings),
    dict(original.metadata),
)

check(
    "UPLOAD_EXTRACTION_RESULT_NOT_MUTATED",
    before == after,
)


# ------------------------------------------------------------
# T. Downstream boundary
# ------------------------------------------------------------

print()
print("=== T. DOWNSTREAM BOUNDARY ===")

check(
    "RESULT_HAS_NO_STRUCTURE",
    not hasattr(result, "structure"),
)

check(
    "RESULT_HAS_NO_HEADING_MAP",
    not hasattr(result, "heading_map"),
)

check(
    "RESULT_HAS_NO_UUCD",
    not hasattr(result, "uucd"),
)

check(
    "RESULT_HAS_NO_SEMANTIC_SCORE",
    not hasattr(result, "semantic_score"),
)


# ------------------------------------------------------------
# U. Final decision
# ------------------------------------------------------------

print()
print("=== U. U7.11 DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U7.11_CONTROL_CHARACTER_HANDLING: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U7.11 control-character verification failed."
    )

print(
    "U7.11_CONTROL_CHARACTER_HANDLING: CERTIFIED"
)

print(
    "U7.11_C0_CONTROL_POLICY: REMOVE_EXCEPT_LF"
)

print(
    "U7.11_DEL_POLICY: REMOVE"
)

print(
    "U7.11_C1_CONTROL_POLICY: REMOVE"
)

print(
    "U7.11_FEFF_POLICY: REMOVE"
)

print(
    "U7.11_NBSP_POLICY: PRESERVE"
)

print(
    "U7.11_ZWJ_ZWNJ_POLICY: PRESERVE"
)

print(
    "U7.11_BROAD_CF_PURGE: NO"
)

print(
    "U7.11_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U7.12_BOILERPLATE_ARTIFACT_BOUNDARY_TRANSITION: AUTHORIZED"
)

print(
    "U7.11_FINAL_CONTROL_CHARACTER_HANDLING_VERIFICATION: PASS"
)