from pathlib import Path
import py_compile

from backend.server.stores.upload_document_extractor import (
    UploadExtractionResult,
)

from backend.server.stores.upload_document_normalizer import (
    normalize_uploaded_document_v1,
)

from backend.server.stores.uploaded_document_unified_content import (
    build_uduc_from_normalized_content,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U8.6 STRUCTURAL PARITY / OFFSET VERIFICATION ===")


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
# B. Build canonical normalized fixture
# ------------------------------------------------------------

print()
print("=== B. CANONICAL CONTENT PARITY ===")

extraction = UploadExtractionResult(
    source_path="C:/immutable/u8_6.txt",
    source_type="txt",
    title="  Title\tHere  ",
    text=(
        "  First   paragraph  \r\n"
        "continues here  \r\n\r\n\r\n"
        "  Second\tparagraph  "
    ),
    headings=[
        "  First Heading  ",
        "Second Heading",
    ],
    metadata={
        "filename": "u8_6.txt",
        "extension": ".txt",
        "method": "u8_6_verifier",
    },
    extraction_status="success",
    extraction_confidence=0.95,
    created_at="2026-08-31T00:00:00+00:00",
)

normalized = normalize_uploaded_document_v1(
    extraction
)

uduc = build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u8_6",
    document_id="doc_u8_6",
    original_filename="u8_6.txt",
)

check(
    "TITLE_EXACTLY_PRESERVED",
    uduc.title == normalized.title,
)

check(
    "BODY_EXACTLY_PRESERVED",
    uduc.content_body == normalized.text,
)

check(
    "HEADINGS_EXACTLY_PRESERVED",
    uduc.headings == normalized.headings,
)


# ------------------------------------------------------------
# C. Paragraph structural parity
# ------------------------------------------------------------

print()
print("=== C. PARAGRAPH STRUCTURAL PARITY ===")

paragraphs = uduc.structure.get(
    "paragraphs",
    []
)

check(
    "PARAGRAPHS_NONEMPTY",
    isinstance(paragraphs, list)
    and len(paragraphs) > 0,
)

paragraph_offsets_valid = True
paragraph_text_exact = True
char_counts_valid = True

for paragraph in paragraphs:
    start = paragraph.get("start_char")
    end = paragraph.get("end_char")
    text = paragraph.get("text")

    if not (
        isinstance(start, int)
        and isinstance(end, int)
        and 0 <= start <= end <= len(
            uduc.content_body
        )
    ):
        paragraph_offsets_valid = False
        continue

    source_slice = uduc.content_body[
        start:end
    ]

    if text != source_slice:
        paragraph_text_exact = False

    if paragraph.get("char_count") != len(text):
        char_counts_valid = False

check(
    "PARAGRAPH_OFFSETS_VALID",
    paragraph_offsets_valid,
)

check(
    "PARAGRAPH_TEXT_EQUALS_EXACT_SOURCE_SLICE",
    paragraph_text_exact,
)

check(
    "PARAGRAPH_CHAR_COUNTS_MATCH_TEXT",
    char_counts_valid,
)


# ------------------------------------------------------------
# D. Heading-map identity
# ------------------------------------------------------------

print()
print("=== D. HEADING MAP IDENTITY ===")

heading_map = uduc.structure.get(
    "heading_map",
    []
)

check(
    "HEADING_MAP_IS_LIST",
    isinstance(
        heading_map,
        list,
    ),
)

mapped_headings = [
    item.get("heading")
    for item in heading_map
]

check(
    "HEADING_MAP_PRESERVES_U7_HEADINGS",
    mapped_headings
    == normalized.headings,
)


# ------------------------------------------------------------
# E. Repeated-heading position behavior
# ------------------------------------------------------------

print()
print("=== E. REPEATED HEADING BEHAVIOR ===")

repeat_extraction = UploadExtractionResult(
    source_path="C:/immutable/repeat.txt",
    source_type="txt",
    title="Repeat",
    text=(
        "Repeat\n\n"
        "Alpha\n\n"
        "Repeat\n\n"
        "Omega"
    ),
    headings=[
        "Repeat",
        "Repeat",
    ],
    metadata={
        "filename": "repeat.txt",
        "extension": ".txt",
    },
    extraction_status="success",
    extraction_confidence=0.95,
    created_at="2026-08-31T00:00:00+00:00",
)

repeat_normalized = normalize_uploaded_document_v1(
    repeat_extraction
)

repeat_uduc = build_uduc_from_normalized_content(
    normalized_content=repeat_normalized,
    workspace_id="ws_u8_6",
    document_id="doc_repeat",
    original_filename="repeat.txt",
)

repeat_map = repeat_uduc.structure.get(
    "heading_map",
    []
)

positions = [
    item.get("char_position")
    for item in repeat_map
]

check(
    "REPEATED_HEADING_COUNT_TWO",
    len(repeat_map) == 2,
)

check(
    "REPEATED_HEADINGS_MAP_TO_DISTINCT_POSITIONS",
    len(positions) == 2
    and all(
        isinstance(value, int)
        for value in positions
    )
    and positions[0] < positions[1],
)


# ------------------------------------------------------------
# F. Transitional cleanup absence
# ------------------------------------------------------------

print()
print("=== F. TRANSITIONAL CLEANUP ABSENCE ===")

source = path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

check(
    "OBSOLETE_AS_LIST_ABSENT",
    "def _as_list(" not in source,
)

check(
    "PARAGRAPH_MATCH_STRIP_ABSENT",
    "block = m.group(0).strip()"
    not in source,
)

check(
    "PARAGRAPH_FALLBACK_STRIP_ABSENT",
    "block = raw.strip()"
    not in source,
)

check(
    "HEADING_MAP_STRIP_ABSENT",
    'h = str(heading or "").strip()'
    not in source,
)

check(
    "H1_COMPATIBILITY_STILL_PRESENT",
    "h1 = str(" in source,
)


# ------------------------------------------------------------
# G. Final certification
# ------------------------------------------------------------

print()
print("=== G. U8.6 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.6_REMOVE_TRANSITIONAL_CONTENT_CLEANUP: FAIL"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    raise RuntimeError(
        "U8.6 verification failed."
    )

print(
    "U8.6_REMOVE_TRANSITIONAL_CONTENT_CLEANUP: CERTIFIED"
)

print(
    "U8.6_CANONICAL_CONTENT_PARITY: PASS"
)

print(
    "U8.6_PARAGRAPH_OFFSET_INTEGRITY: PASS"
)

print(
    "U8.6_HEADING_IDENTITY_PRESERVATION: PASS"
)

print(
    "U8.6_REPEATED_HEADING_FORWARD_SEARCH: PASS"
)

print(
    "U8.6_OBSOLETE_AS_LIST_REMOVAL: COMPLETE"
)

print(
    "U8.6_H1_COMPATIBILITY: DEFERRED_TO_U8.16"
)

print(
    "U8.6_PRODUCTION_PATCH_OUTSTANDING: NO"
)

print(
    "U8.7_PARAGRAPH_STRUCTURE_CONSTRUCTION_TRANSITION: AUTHORIZED"
)

print(
    "U8.6_FINAL_TRANSITIONAL_CONTENT_CLEANUP_VERIFICATION: PASS"
)