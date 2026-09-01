from __future__ import annotations

import unicodedata

from backend.server.stores.upload_document_extractor import (
    UploadExtractionResult,
)

from backend.server.stores.upload_document_normalizer import (
    NORMALIZATION_VERSION,
    NormalizedUploadedDocumentContent,
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
    status: str = "success",
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
        extraction_status=status,
        extraction_confidence=0.95,
        created_at="2026-08-31T00:00:00+00:00",
    )


print("=== U7.5 - UNICODE NORMALIZATION VERIFICATION ===")


# ------------------------------------------------------------
# A. Canonical NFC behavior
# ------------------------------------------------------------

print()
print("=== A. CANONICAL NFC BEHAVIOR ===")

decomposed = "Cafe\u0301"
composed = "Café"

input_result = make_result(
    title=decomposed,
    text=f"{decomposed} body",
    headings=[decomposed],
)

normalized = normalize_uploaded_document_v1(
    input_result
)

check(
    "RESULT_IS_NORMALIZED_UPLOADED_DOCUMENT_CONTENT",
    isinstance(
        normalized,
        NormalizedUploadedDocumentContent,
    ),
)

check(
    "TITLE_NORMALIZED_TO_NFC",
    normalized.title == composed,
)

check(
    "TEXT_NORMALIZED_TO_NFC",
    normalized.text == f"{composed} body",
)

check(
    "HEADINGS_NORMALIZED_TO_NFC",
    normalized.headings == [composed],
)

check(
    "TITLE_IS_NFC",
    unicodedata.is_normalized(
        "NFC",
        normalized.title,
    ),
)

check(
    "TEXT_IS_NFC",
    unicodedata.is_normalized(
        "NFC",
        normalized.text,
    ),
)


# ------------------------------------------------------------
# B. Non-English script preservation
# ------------------------------------------------------------

print()
print("=== B. NON-ENGLISH SCRIPT PRESERVATION ===")

samples = {
    "GREEK": "Καλημέρα κόσμε",
    "CYRILLIC": "Привет мир",
    "ARABIC": "مرحبا بالعالم",
    "HEBREW": "שלום עולם",
    "CJK": "你好世界",
    "ACCENTED_LATIN": "São Tomé déjà vu",
}

for name, value in samples.items():
    result = normalize_uploaded_document_v1(
        make_result(
            title=value,
            text=value,
            headings=[value],
        )
    )

    check(
        f"{name}_TITLE_PRESERVED",
        result.title
        == unicodedata.normalize(
            "NFC",
            value,
        ),
    )

    check(
        f"{name}_TEXT_PRESERVED",
        result.text
        == unicodedata.normalize(
            "NFC",
            value,
        ),
    )


# ------------------------------------------------------------
# C. Meaningful punctuation and symbols
# ------------------------------------------------------------

print()
print("=== C. PUNCTUATION / SYMBOL PRESERVATION ===")

symbols = (
    "“quoted” ‘text’ — en–dash "
    "€ £ ¥ $ ± × ÷ ∑ ∞ © ™"
)

symbol_result = normalize_uploaded_document_v1(
    make_result(
        title=symbols,
        text=symbols,
        headings=[symbols],
    )
)

check(
    "PUNCTUATION_AND_SYMBOLS_PRESERVED",
    symbol_result.text == symbols,
)


# ------------------------------------------------------------
# D. No compatibility folding
# ------------------------------------------------------------

print()
print("=== D. NO NFKC COMPATIBILITY FOLDING ===")

compatibility_samples = (
    "①",
    "Ⅳ",
    "Å",
    "Ｆｕｌｌｗｉｄｔｈ",
)

for value in compatibility_samples:
    result = normalize_uploaded_document_v1(
        make_result(
            title=value,
            text=value,
            headings=[value],
        )
    )

    expected = unicodedata.normalize(
        "NFC",
        value,
    )

    check(
        "NFC_PRESERVES_COMPATIBILITY_FORM_"
        + str(ord(value[0])),
        result.text == expected,
    )


# ------------------------------------------------------------
# E. No transliteration / accent stripping
# ------------------------------------------------------------

print()
print("=== E. NO TRANSLITERATION ===")

value = "Crème brûlée — Αθήνα — 東京"

result = normalize_uploaded_document_v1(
    make_result(
        title=value,
        text=value,
        headings=[value],
    )
)

check(
    "NO_ASCII_TRANSLITERATION",
    result.text
    == unicodedata.normalize(
        "NFC",
        value,
    ),
)

check(
    "ACCENTS_PRESERVED",
    "è" in result.text
    and "û" in result.text,
)

check(
    "NON_LATIN_SCRIPTS_PRESERVED",
    "Αθήνα" in result.text
    and "東京" in result.text,
)


# ------------------------------------------------------------
# F. Zero-width / format character non-destruction
# ------------------------------------------------------------

print()
print("=== F. ZERO-WIDTH / FORMAT CHARACTER POLICY ===")

zero_width = "A\u200DB"

result = normalize_uploaded_document_v1(
    make_result(
        title=zero_width,
        text=zero_width,
        headings=[zero_width],
    )
)

check(
    "ZERO_WIDTH_JOINER_NOT_BLANKET_REMOVED",
    "\u200D" in result.text,
)


# ------------------------------------------------------------
# G. Provenance and source identity
# ------------------------------------------------------------

print()
print("=== G. PROVENANCE PRESERVATION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title=decomposed,
        text=decomposed,
        headings=[decomposed],
    )
)

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
    result.extraction_status
    == "success",
)

check(
    "EXTRACTION_CONFIDENCE_PRESERVED",
    result.extraction_confidence
    == 0.95,
)

check(
    "EXTRACTION_TIMESTAMP_PRESERVED",
    result.extraction_created_at
    == "2026-08-31T00:00:00+00:00",
)

check(
    "EXTRACTION_METADATA_PRESERVED",
    result.metadata.get(
        "custom"
    )
    == "preserve-me",
)


# ------------------------------------------------------------
# H. Normalization metadata
# ------------------------------------------------------------

print()
print("=== H. NORMALIZATION METADATA ===")

normalization_meta = result.metadata.get(
    "normalization",
    {},
)

check(
    "NORMALIZATION_STATUS_SUCCESS",
    result.normalization_status
    == "success",
)

check(
    "NORMALIZATION_VERSION_CORRECT",
    result.normalization_version
    == NORMALIZATION_VERSION
    == "uploaded_document_normalization_v1",
)

check(
    "NORMALIZATION_METADATA_UNICODE_FORM_NFC",
    normalization_meta.get(
        "unicode_form"
    )
    == "NFC",
)

check(
    "NORMALIZATION_METADATA_OPERATION_RECORDED",
    normalization_meta.get(
        "operations"
    )
    == ["unicode_nfc"],
)


# ------------------------------------------------------------
# I. Ineligible extraction behavior
# ------------------------------------------------------------

print()
print("=== I. INELIGIBLE EXTRACTION ===")

ineligible = make_result(
    title=decomposed,
    text=decomposed,
    headings=[decomposed],
    status="empty_text",
)

ineligible_result = (
    normalize_uploaded_document_v1(
        ineligible
    )
)

check(
    "INELIGIBLE_EXTRACTION_STATUS",
    ineligible_result.normalization_status
    == "ineligible_extraction",
)

check(
    "INELIGIBLE_CONTENT_NOT_TRANSFORMED",
    ineligible_result.text
    == decomposed,
)

check(
    "INELIGIBLE_OPERATIONS_EMPTY",
    ineligible_result.metadata.get(
        "normalization",
        {},
    ).get(
        "operations"
    )
    == [],
)


# ------------------------------------------------------------
# J. Determinism
# ------------------------------------------------------------

print()
print("=== J. CONTENT DETERMINISM ===")

source = make_result(
    title=decomposed,
    text=f"{decomposed}\nκόσμε",
    headings=[decomposed],
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
    first.headings
    == second.headings,
)

check(
    "NORMALIZED_AT_DOES_NOT_AFFECT_CONTENT",
    (
        first.title,
        first.text,
        first.headings,
    )
    == (
        second.title,
        second.text,
        second.headings,
    ),
)


# ------------------------------------------------------------
# K. Input object immutability
# ------------------------------------------------------------

print()
print("=== K. INPUT IMMUTABILITY ===")

original = make_result(
    title=decomposed,
    text=decomposed,
    headings=[decomposed],
)

before = (
    original.source_path,
    original.source_type,
    original.title,
    original.text,
    list(original.headings),
    dict(original.metadata),
    original.extraction_status,
    original.extraction_confidence,
    original.created_at,
)

normalize_uploaded_document_v1(
    original
)

after = (
    original.source_path,
    original.source_type,
    original.title,
    original.text,
    list(original.headings),
    dict(original.metadata),
    original.extraction_status,
    original.extraction_confidence,
    original.created_at,
)

check(
    "UPLOAD_EXTRACTION_RESULT_NOT_MUTATED",
    before == after,
)


# ------------------------------------------------------------
# L. Final decision
# ------------------------------------------------------------

print()
print("=== L. U7.5 DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U7.5_UNICODE_NORMALIZATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U7.5 Unicode normalization verification failed."
    )

print(
    "U7.5_UNICODE_NORMALIZATION: CERTIFIED"
)

print(
    "U7.5_CANONICAL_UNICODE_FORM: NFC"
)

print(
    "U7.5_TRANSLITERATION_ALLOWED: NO"
)

print(
    "U7.5_MOJIBAKE_REPAIR_INCLUDED: NO"
)

print(
    "U7.5_ZERO_WIDTH_BLANKET_REMOVAL: NO"
)

print(
    "U7.5_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U7.6_LINE_ENDING_NORMALIZATION_TRANSITION: AUTHORIZED"
)

print(
    "U7.5_FINAL_UNICODE_NORMALIZATION_VERIFICATION: PASS"
)