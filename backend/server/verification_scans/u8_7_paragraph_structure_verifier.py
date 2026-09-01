from backend.server.stores.uploaded_document_unified_content import (
    _paragraphs_from_content_body,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def verify_offsets(body: str, paragraphs: list[dict]) -> tuple[bool, bool, bool]:
    exact = True
    monotonic = True
    non_overlap = True

    previous_start = -1
    previous_end = -1

    for paragraph in paragraphs:
        start = paragraph.get("start_char")
        end = paragraph.get("end_char")
        text = paragraph.get("text")

        if not (
            isinstance(start, int)
            and isinstance(end, int)
            and 0 <= start <= end <= len(body)
        ):
            exact = False
            monotonic = False
            non_overlap = False
            continue

        if body[start:end] != text:
            exact = False

        if start < previous_start:
            monotonic = False

        if previous_end > start:
            non_overlap = False

        previous_start = start
        previous_end = end

    return exact, monotonic, non_overlap


print("=== U8.7 PARAGRAPH STRUCTURE VERIFICATION ===")


# ------------------------------------------------------------
# A. One paragraph
# ------------------------------------------------------------

print()
print("=== A. ONE PARAGRAPH ===")

body = "Alpha beta gamma"
paragraphs = _paragraphs_from_content_body(body)

check(
    "ONE_PARAGRAPH_COUNT",
    len(paragraphs) == 1,
)

check(
    "ONE_PARAGRAPH_INDEX_ONE",
    paragraphs[0]["index"] == 1,
)

check(
    "ONE_PARAGRAPH_TEXT_EXACT",
    paragraphs[0]["text"] == body,
)

check(
    "ONE_PARAGRAPH_START_ZERO",
    paragraphs[0]["start_char"] == 0,
)

check(
    "ONE_PARAGRAPH_END_EXCLUSIVE",
    paragraphs[0]["end_char"] == len(body),
)

check(
    "ONE_PARAGRAPH_CHAR_COUNT",
    paragraphs[0]["char_count"] == len(body),
)


# ------------------------------------------------------------
# B. Multiple paragraphs
# ------------------------------------------------------------

print()
print("=== B. MULTIPLE PARAGRAPHS ===")

body = "Alpha\n\nBeta\n\nGamma"
paragraphs = _paragraphs_from_content_body(body)

check(
    "MULTI_PARAGRAPH_COUNT_THREE",
    len(paragraphs) == 3,
)

check(
    "MULTI_INDEXES_CONTIGUOUS",
    [p["index"] for p in paragraphs]
    == [1, 2, 3],
)

check(
    "MULTI_TEXT_EXACT",
    [p["text"] for p in paragraphs]
    == ["Alpha", "Beta", "Gamma"],
)

exact, monotonic, non_overlap = verify_offsets(
    body,
    paragraphs,
)

check(
    "MULTI_OFFSETS_EXACT",
    exact,
)

check(
    "MULTI_OFFSETS_MONOTONIC",
    monotonic,
)

check(
    "MULTI_OFFSETS_NON_OVERLAPPING",
    non_overlap,
)


# ------------------------------------------------------------
# C. Multiline paragraph
# ------------------------------------------------------------

print()
print("=== C. MULTILINE PARAGRAPH ===")

body = "Line one\nLine two\n\nNext"
paragraphs = _paragraphs_from_content_body(body)

check(
    "MULTILINE_PARAGRAPH_COUNT_TWO",
    len(paragraphs) == 2,
)

check(
    "MULTILINE_FIRST_TEXT_PRESERVED",
    paragraphs[0]["text"]
    == "Line one\nLine two",
)

exact, monotonic, non_overlap = verify_offsets(
    body,
    paragraphs,
)

check(
    "MULTILINE_OFFSETS_EXACT",
    exact,
)

check(
    "MULTILINE_OFFSETS_MONOTONIC",
    monotonic,
)

check(
    "MULTILINE_OFFSETS_NON_OVERLAPPING",
    non_overlap,
)


# ------------------------------------------------------------
# D. Empty content
# ------------------------------------------------------------

print()
print("=== D. EMPTY CONTENT ===")

body = ""
paragraphs = _paragraphs_from_content_body(body)

check(
    "EMPTY_CONTENT_RETURNS_EMPTY_LIST",
    paragraphs == [],
)


# ------------------------------------------------------------
# E. Repeated text
# ------------------------------------------------------------

print()
print("=== E. REPEATED TEXT ===")

body = "Repeat\n\nRepeat\n\nRepeat"
paragraphs = _paragraphs_from_content_body(body)

check(
    "REPEATED_TEXT_COUNT_THREE",
    len(paragraphs) == 3,
)

check(
    "REPEATED_TEXT_VALUES_PRESERVED",
    [p["text"] for p in paragraphs]
    == ["Repeat", "Repeat", "Repeat"],
)

exact, monotonic, non_overlap = verify_offsets(
    body,
    paragraphs,
)

check(
    "REPEATED_TEXT_OFFSETS_EXACT",
    exact,
)

check(
    "REPEATED_TEXT_OFFSETS_MONOTONIC",
    monotonic,
)

check(
    "REPEATED_TEXT_OFFSETS_NON_OVERLAPPING",
    non_overlap,
)


# ------------------------------------------------------------
# F. Unicode
# ------------------------------------------------------------

print()
print("=== F. UNICODE CONTENT ===")

body = "Café 東京\n\nRésumé Ω"
paragraphs = _paragraphs_from_content_body(body)

check(
    "UNICODE_PARAGRAPH_COUNT_TWO",
    len(paragraphs) == 2,
)

check(
    "UNICODE_TEXT_PRESERVED",
    [p["text"] for p in paragraphs]
    == ["Café 東京", "Résumé Ω"],
)

exact, monotonic, non_overlap = verify_offsets(
    body,
    paragraphs,
)

check(
    "UNICODE_OFFSETS_EXACT",
    exact,
)

check(
    "UNICODE_OFFSETS_MONOTONIC",
    monotonic,
)

check(
    "UNICODE_OFFSETS_NON_OVERLAPPING",
    non_overlap,
)


# ------------------------------------------------------------
# G. Word counts
# ------------------------------------------------------------

print()
print("=== G. WORD COUNTS ===")

body = "Alpha beta\nGamma\n\nDelta  epsilon"
paragraphs = _paragraphs_from_content_body(body)

check(
    "WORD_COUNT_FIRST_PARAGRAPH",
    paragraphs[0]["word_count"] == 3,
)

check(
    "WORD_COUNT_SECOND_PARAGRAPH",
    paragraphs[1]["word_count"] == 2,
)


# ------------------------------------------------------------
# H. Structural immutability
# ------------------------------------------------------------

print()
print("=== H. STRUCTURAL IMMUTABILITY ===")

body = "  Alpha\nBeta  \n\nGamma"
original = body

paragraphs = _paragraphs_from_content_body(body)

check(
    "SOURCE_STRING_UNCHANGED",
    body == original,
)

exact, monotonic, non_overlap = verify_offsets(
    body,
    paragraphs,
)

check(
    "STRUCTURAL_TEXT_REMAINS_EXACT_SOURCE_SLICE",
    exact,
)


# ------------------------------------------------------------
# I. Final decision
# ------------------------------------------------------------

print()
print("=== I. U8.7 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.7_PARAGRAPH_STRUCTURE_CONSTRUCTION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(
            f" - {failure}"
        )

    raise RuntimeError(
        "U8.7 paragraph structure verification failed."
    )

print(
    "U8.7_PARAGRAPH_STRUCTURE_CONSTRUCTION: CERTIFIED"
)

print(
    "U8.7_PARAGRAPH_SOURCE: EXACT_CONTENT_BODY"
)

print(
    "U8.7_PARAGRAPH_BOUNDARY_RULE: BLANK_LINE_SEPARATION"
)

print(
    "U8.7_INDEXING: ONE_BASED_CONTIGUOUS"
)

print(
    "U8.7_OFFSET_CONTRACT: START_INCLUSIVE_END_EXCLUSIVE"
)

print(
    "U8.7_PARAGRAPH_TEXT: EXACT_SOURCE_SLICE"
)

print(
    "U8.7_OFFSET_MONOTONICITY: PASS"
)

print(
    "U8.7_OFFSET_NON_OVERLAP: PASS"
)

print(
    "U8.7_UNICODE_PRESERVATION: PASS"
)

print(
    "U8.7_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U8.8_HEADING_MAP_CONSTRUCTION_TRANSITION: AUTHORIZED"
)

print(
    "U8.7_FINAL_PARAGRAPH_STRUCTURE_VERIFICATION: PASS"
)