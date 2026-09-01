from pathlib import Path
import py_compile

from backend.server.stores.uploaded_document_unified_content import (
    _build_uduc_structure,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U8.9 DOCUMENT ORDER REGRESSION VERIFICATION ===")


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
# B. Heading at body start
# ------------------------------------------------------------

print()
print("=== B. HEADING AT BODY START ===")

body = "Heading\n\nParagraph body"
headings = ["Heading"]

order = _build_uduc_structure(
    body,
    headings,
)["document_order"]

check(
    "START_ORDER_COUNT",
    len(order) == 3,
)

check(
    "START_HEADING_FIRST",
    order[0]["type"] == "heading"
    and order[0]["char_position"] == 0,
)

check(
    "START_PARAGRAPH_AT_ZERO_SECOND",
    order[1]["type"] == "paragraph"
    and order[1]["start_char"] == 0,
)


# ------------------------------------------------------------
# C. Later heading
# ------------------------------------------------------------

print()
print("=== C. LATER HEADING ===")

body = (
    "Intro paragraph\n\n"
    "Heading Two\n"
    "Body continues"
)

headings = ["Heading Two"]

order = _build_uduc_structure(
    body,
    headings,
)["document_order"]

check(
    "LATER_INTRO_PARAGRAPH_FIRST",
    order[0]["type"] == "paragraph"
    and order[0]["index"] == 1,
)

check(
    "LATER_HEADING_BEFORE_CONTAINING_PARAGRAPH",
    order[1]["type"] == "heading"
    and order[2]["type"] == "paragraph"
    and order[1]["char_position"]
    == order[2]["start_char"],
)


# ------------------------------------------------------------
# D. Multiple headings / paragraphs
# ------------------------------------------------------------

print()
print("=== D. MULTIPLE HEADING/PARAGRAPH INTERLEAVING ===")

body = (
    "Intro\n\n"
    "Heading A\n\n"
    "Middle\n\n"
    "Heading B\n\n"
    "End"
)

headings = [
    "Heading A",
    "Heading B",
]

order = _build_uduc_structure(
    body,
    headings,
)["document_order"]

positioned_positions = []

for item in order:
    if item["type"] == "heading":
        if isinstance(
            item["char_position"],
            int,
        ):
            positioned_positions.append(
                item["char_position"]
            )
    else:
        positioned_positions.append(
            item["start_char"]
        )

check(
    "POSITIONED_CONTENT_SORTED",
    positioned_positions
    == sorted(positioned_positions),
)

check(
    "PARAGRAPH_ORDER_PRESERVED",
    [
        item["index"]
        for item in order
        if item["type"] == "paragraph"
    ]
    == [1, 2, 3, 4, 5],
)


# ------------------------------------------------------------
# E. Repeated headings
# ------------------------------------------------------------

print()
print("=== E. REPEATED HEADINGS ===")

body = (
    "Repeat\n\n"
    "Alpha\n\n"
    "Repeat\n\n"
    "Omega"
)

headings = [
    "Repeat",
    "Repeat",
]

order = _build_uduc_structure(
    body,
    headings,
)["document_order"]

heading_entries = [
    item
    for item in order
    if item["type"] == "heading"
]

check(
    "REPEATED_HEADING_COUNT_TWO",
    len(heading_entries) == 2,
)

check(
    "REPEATED_HEADING_POSITIONS_ASCENDING",
    heading_entries[0]["char_position"]
    < heading_entries[1]["char_position"],
)


# ------------------------------------------------------------
# F. Equal-position stability
# ------------------------------------------------------------

print()
print("=== F. EQUAL POSITION STABILITY ===")

body = "Heading\nText"
headings = ["Heading"]

order = _build_uduc_structure(
    body,
    headings,
)["document_order"]

check(
    "HEADING_PRECEDES_PARAGRAPH_AT_EQUAL_POSITION",
    len(order) >= 2
    and order[0]["type"] == "heading"
    and order[1]["type"] == "paragraph"
    and order[0]["char_position"]
    == order[1]["start_char"],
)


# ------------------------------------------------------------
# G. Unmatched heading regression
# ------------------------------------------------------------

print()
print("=== G. UNMATCHED HEADING REGRESSION ===")

body = "Alpha\n\nBeta"

headings = [
    "Missing Heading",
]

order = _build_uduc_structure(
    body,
    headings,
)["document_order"]

check(
    "UNMATCHED_HEADING_RETAINED",
    sum(
        1
        for item in order
        if item["type"] == "heading"
    )
    == 1,
)

unmatched = next(
    item
    for item in order
    if item["type"] == "heading"
)

check(
    "UNMATCHED_HEADING_CHAR_POSITION_NONE",
    unmatched["char_position"] is None,
)

check(
    "UNMATCHED_HEADING_SORTS_AFTER_POSITIONED_CONTENT",
    order[-1]["type"] == "heading"
    and order[-1]["char_position"] is None,
)

check(
    "POSITIONED_PARAGRAPHS_REMAIN_BEFORE_UNMATCHED_HEADING",
    [
        item["type"]
        for item in order
    ]
    == [
        "paragraph",
        "paragraph",
        "heading",
    ],
)


# ------------------------------------------------------------
# H. Multiple unmatched headings
# ------------------------------------------------------------

print()
print("=== H. MULTIPLE UNMATCHED HEADINGS ===")

body = "Alpha\n\nBeta"

headings = [
    "Missing One",
    "Missing Two",
]

order = _build_uduc_structure(
    body,
    headings,
)["document_order"]

unmatched_entries = [
    item
    for item in order
    if item["type"] == "heading"
]

check(
    "MULTIPLE_UNMATCHED_COUNT_TWO",
    len(unmatched_entries) == 2,
)

check(
    "MULTIPLE_UNMATCHED_LIST_ORDER_PRESERVED",
    [
        item["text"]
        for item in unmatched_entries
    ]
    == headings,
)

check(
    "MULTIPLE_UNMATCHED_ALL_AT_END",
    [
        item["type"]
        for item in order[-2:]
    ]
    == [
        "heading",
        "heading",
    ],
)

check(
    "MULTIPLE_UNMATCHED_ALL_NONE_POSITION",
    all(
        item["char_position"] is None
        for item in unmatched_entries
    ),
)


# ------------------------------------------------------------
# I. Mixed matched + unmatched headings
# ------------------------------------------------------------

print()
print("=== I. MIXED MATCHED / UNMATCHED ===")

body = (
    "Intro\n\n"
    "Matched Heading\n\n"
    "Body"
)

headings = [
    "Matched Heading",
    "Missing Heading",
]

order = _build_uduc_structure(
    body,
    headings,
)["document_order"]

matched = next(
    item
    for item in order
    if (
        item["type"] == "heading"
        and item["text"] == "Matched Heading"
    )
)

missing = next(
    item
    for item in order
    if (
        item["type"] == "heading"
        and item["text"] == "Missing Heading"
    )
)

check(
    "MATCHED_HEADING_HAS_REAL_POSITION",
    isinstance(
        matched["char_position"],
        int,
    ),
)

check(
    "UNMATCHED_HEADING_REMAINS_NONE",
    missing["char_position"] is None,
)

check(
    "UNMATCHED_HEADING_AFTER_MATCHED_AND_PARAGRAPHS",
    order[-1]["text"]
    == "Missing Heading",
)


# ------------------------------------------------------------
# J. Empty inputs
# ------------------------------------------------------------

print()
print("=== J. EMPTY INPUTS ===")

check(
    "EMPTY_BODY_AND_HEADINGS_ORDER_EMPTY",
    _build_uduc_structure(
        "",
        [],
    )["document_order"]
    == [],
)

order = _build_uduc_structure(
    "Alpha\n\nBeta",
    [],
)["document_order"]

check(
    "EMPTY_HEADINGS_ONLY_PARAGRAPHS",
    [
        item["type"]
        for item in order
    ]
    == [
        "paragraph",
        "paragraph",
    ],
)


# ------------------------------------------------------------
# K. Determinism
# ------------------------------------------------------------

print()
print("=== K. DETERMINISM ===")

body = (
    "Heading A\n\n"
    "Text\n\n"
    "Heading B"
)

headings = [
    "Heading A",
    "Missing Heading",
    "Heading B",
]

first = _build_uduc_structure(
    body,
    headings,
)["document_order"]

second = _build_uduc_structure(
    body,
    headings,
)["document_order"]

check(
    "DOCUMENT_ORDER_DETERMINISTIC",
    first == second,
)


# ------------------------------------------------------------
# L. Legacy sentinel absent
# ------------------------------------------------------------

print()
print("=== L. LEGACY SENTINEL ABSENCE ===")

source = path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

check(
    "NEGATIVE_ONE_SENTINEL_ABSENT",
    "pos if isinstance(pos, int) else -1"
    not in source,
)

check(
    "THREE_PART_ORDER_TUPLE_PRESENT",
    "for _, _, item in ordered"
    in source,
)


# ------------------------------------------------------------
# M. Final certification
# ------------------------------------------------------------

print()
print("=== M. U8.9 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.9_DOCUMENT_ORDER_CONSTRUCTION: FAIL"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    raise RuntimeError(
        "U8.9 regression verification failed."
    )

print(
    "U8.9_DOCUMENT_ORDER_CONSTRUCTION: CERTIFIED"
)

print(
    "U8.9_ORDER_AUTHORITY: REAL_CHARACTER_POSITION"
)

print(
    "U8.9_POSITIONED_HEADINGS_PARAGRAPHS_INTERLEAVED: YES"
)

print(
    "U8.9_EQUAL_POSITION_RULE: HEADING_BEFORE_PARAGRAPH"
)

print(
    "U8.9_REPEATED_HEADING_ORDER: PRESERVED"
)

print(
    "U8.9_UNMATCHED_HEADING_CHAR_POSITION: NONE"
)

print(
    "U8.9_UNMATCHED_HEADING_ORDER: AFTER_POSITIONED_CONTENT"
)

print(
    "U8.9_MULTIPLE_UNMATCHED_LIST_ORDER: PRESERVED"
)

print(
    "U8.9_NEGATIVE_ONE_SENTINEL: REMOVED"
)

print(
    "U8.9_DETERMINISTIC: YES"
)

print(
    "U8.9_PRODUCTION_PATCH_OUTSTANDING: NO"
)

print(
    "U8.10_STRUCTURAL_SUMMARY_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U8.9_FINAL_DOCUMENT_ORDER_REGRESSION_VERIFICATION: PASS"
)