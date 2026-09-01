from backend.server.stores.uploaded_document_unified_content import (
    _build_uduc_structure,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def order_types(structure):
    return [
        item.get("type")
        for item in structure.get(
            "document_order",
            [],
        )
    ]


print("=== U8.9 DOCUMENT ORDER VERIFICATION ===")


# ------------------------------------------------------------
# A. Heading at body start
# ------------------------------------------------------------

print()
print("=== A. HEADING AT BODY START ===")

body = "Heading\n\nParagraph body"
headings = ["Heading"]

structure = _build_uduc_structure(
    body,
    headings,
)

order = structure["document_order"]

check(
    "START_ORDER_COUNT",
    len(order) == 3,
)

check(
    "START_HEADING_FIRST",
    order[0]["type"] == "heading"
    and order[0]["text"] == "Heading",
)

check(
    "START_FIRST_PARAGRAPH_SECOND",
    order[1]["type"] == "paragraph"
    and order[1]["start_char"] == 0,
)

check(
    "START_SECOND_PARAGRAPH_THIRD",
    order[2]["type"] == "paragraph",
)


# ------------------------------------------------------------
# B. Heading in later paragraph
# ------------------------------------------------------------

print()
print("=== B. HEADING IN LATER PARAGRAPH ===")

body = (
    "Intro paragraph\n\n"
    "Heading Two\n"
    "Body continues"
)

headings = ["Heading Two"]

structure = _build_uduc_structure(
    body,
    headings,
)

order = structure["document_order"]

check(
    "LATER_FIRST_IS_INTRO_PARAGRAPH",
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
# C. Multiple headings and paragraphs
# ------------------------------------------------------------

print()
print("=== C. MULTIPLE HEADINGS / PARAGRAPHS ===")

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

structure = _build_uduc_structure(
    body,
    headings,
)

order = structure["document_order"]

positions = []

for item in order:
    if item["type"] == "heading":
        positions.append(
            item["char_position"]
        )
    else:
        positions.append(
            item["start_char"]
        )

check(
    "MULTI_DOCUMENT_ORDER_POSITION_SORTED",
    positions == sorted(positions),
)

check(
    "MULTI_HEADINGS_PRESENT",
    [
        item["text"]
        for item in order
        if item["type"] == "heading"
    ]
    == headings,
)

check(
    "MULTI_PARAGRAPHS_SOURCE_ORDER",
    [
        item["index"]
        for item in order
        if item["type"] == "paragraph"
    ]
    == [1, 2, 3, 4, 5],
)


# ------------------------------------------------------------
# D. Repeated headings
# ------------------------------------------------------------

print()
print("=== D. REPEATED HEADINGS ===")

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

structure = _build_uduc_structure(
    body,
    headings,
)

heading_entries = [
    item
    for item in structure[
        "document_order"
    ]
    if item["type"] == "heading"
]

check(
    "REPEATED_HEADING_ORDER_COUNT_TWO",
    len(heading_entries) == 2,
)

check(
    "REPEATED_HEADING_POSITIONS_ASCENDING",
    heading_entries[0]["char_position"]
    < heading_entries[1]["char_position"],
)


# ------------------------------------------------------------
# E. Equal position rule
# ------------------------------------------------------------

print()
print("=== E. EQUAL POSITION RULE ===")

body = "Heading\nText"
headings = ["Heading"]

structure = _build_uduc_structure(
    body,
    headings,
)

order = structure["document_order"]

check(
    "EQUAL_POSITION_HEADING_FIRST",
    len(order) >= 2
    and order[0]["type"] == "heading"
    and order[1]["type"] == "paragraph"
    and order[0]["char_position"]
    == order[1]["start_char"],
)


# ------------------------------------------------------------
# F. Empty headings
# ------------------------------------------------------------

print()
print("=== F. EMPTY HEADINGS ===")

body = "Alpha\n\nBeta"
headings = []

structure = _build_uduc_structure(
    body,
    headings,
)

order = structure["document_order"]

check(
    "EMPTY_HEADINGS_ONLY_PARAGRAPHS",
    order_types(structure)
    == ["paragraph", "paragraph"],
)

check(
    "EMPTY_HEADINGS_PARAGRAPH_ORDER",
    [
        item["index"]
        for item in order
    ]
    == [1, 2],
)


# ------------------------------------------------------------
# G. Empty content
# ------------------------------------------------------------

print()
print("=== G. EMPTY CONTENT ===")

body = ""
headings = []

structure = _build_uduc_structure(
    body,
    headings,
)

check(
    "EMPTY_CONTENT_DOCUMENT_ORDER_EMPTY",
    structure["document_order"] == [],
)


# ------------------------------------------------------------
# H. Unmatched heading
# ------------------------------------------------------------

print()
print("=== H. UNMATCHED HEADING ===")

body = "Alpha\n\nBeta"
headings = [
    "Missing Heading",
]

structure = _build_uduc_structure(
    body,
    headings,
)

order = structure["document_order"]

unmatched = [
    item
    for item in order
    if item["type"] == "heading"
]

check(
    "UNMATCHED_HEADING_RETAINED",
    len(unmatched) == 1,
)

check(
    "UNMATCHED_HEADING_POSITION_NONE",
    unmatched[0]["char_position"]
    is None,
)

# Current implementation converts None to -1 for ordering,
# which places unmatched headings before all real content.
check(
    "UNMATCHED_HEADING_NOT_BEFORE_POSITIONED_CONTENT",
    not (
        order
        and order[0]["type"] == "heading"
        and order[0]["char_position"] is None
    ),
)


# ------------------------------------------------------------
# I. Determinism
# ------------------------------------------------------------

print()
print("=== I. DETERMINISM ===")

body = (
    "Heading A\n\n"
    "Text\n\n"
    "Heading B"
)

headings = [
    "Heading A",
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
# J. Input immutability
# ------------------------------------------------------------

print()
print("=== J. INPUT IMMUTABILITY ===")

body = "Heading\n\nText"
headings = ["Heading"]

original_body = body
original_headings = list(headings)

_build_uduc_structure(
    body,
    headings,
)

check(
    "DOCUMENT_ORDER_BODY_UNCHANGED",
    body == original_body,
)

check(
    "DOCUMENT_ORDER_HEADINGS_UNCHANGED",
    headings == original_headings,
)


# ------------------------------------------------------------
# K. Final decision
# ------------------------------------------------------------

print()
print("=== K. U8.9 FINAL DECISION ===")

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

    print(
        "U8.9_PATCH_DECISION_REQUIRED: YES"
    )

    print(
        "U8.9_PRIMARY_SUSPECT: UNMATCHED_HEADING_SENTINEL_ORDER"
    )

else:
    print(
        "U8.9_DOCUMENT_ORDER_CONSTRUCTION: CERTIFIED"
    )

    print(
        "U8.9_ORDER_AUTHORITY: CHARACTER_POSITION"
    )

    print(
        "U8.9_HEADINGS_PARAGRAPHS_INTERLEAVED: YES"
    )

    print(
        "U8.9_EQUAL_POSITION_RULE: HEADING_BEFORE_PARAGRAPH"
    )

    print(
        "U8.9_UNMATCHED_HEADING_BEHAVIOR: ACCEPTED"
    )

    print(
        "U8.9_DETERMINISTIC: YES"
    )

    print(
        "U8.9_INPUT_MUTATION: NO"
    )

    print(
        "U8.9_PRODUCTION_PATCH_REQUIRED: NO"
    )

    print(
        "U8.10_STRUCTURAL_SUMMARY_CONTRACT_TRANSITION: AUTHORIZED"
    )

    print(
        "U8.9_FINAL_DOCUMENT_ORDER_VERIFICATION: PASS"
    )