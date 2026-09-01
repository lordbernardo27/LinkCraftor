from backend.server.stores.uploaded_document_unified_content import (
    _build_heading_map,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U8.8 HEADING MAP VERIFICATION ===")


# ------------------------------------------------------------
# A. Single heading
# ------------------------------------------------------------

print()
print("=== A. SINGLE HEADING ===")

body = "Intro\n\nHeading One\n\nBody"
headings = ["Heading One"]

original_body = body
original_headings = list(headings)

heading_map = _build_heading_map(
    headings,
    body,
)

check(
    "SINGLE_HEADING_COUNT_ONE",
    len(heading_map) == 1,
)

check(
    "SINGLE_HEADING_INDEX_ONE",
    heading_map[0]["index"] == 1,
)

check(
    "SINGLE_HEADING_TEXT_EXACT",
    heading_map[0]["heading"]
    == headings[0],
)

check(
    "SINGLE_HEADING_POSITION_EXACT",
    heading_map[0]["char_position"]
    == body.find("Heading One"),
)

check(
    "SINGLE_HEADING_LEVEL_NONE",
    heading_map[0]["level"] is None,
)

check(
    "SINGLE_BODY_UNCHANGED",
    body == original_body,
)

check(
    "SINGLE_HEADINGS_UNCHANGED",
    headings == original_headings,
)


# ------------------------------------------------------------
# B. Multiple headings
# ------------------------------------------------------------

print()
print("=== B. MULTIPLE HEADINGS ===")

body = (
    "Intro\n\n"
    "Heading A\n\n"
    "Text\n\n"
    "Heading B\n\n"
    "End"
)

headings = [
    "Heading A",
    "Heading B",
]

heading_map = _build_heading_map(
    headings,
    body,
)

check(
    "MULTI_HEADING_COUNT_TWO",
    len(heading_map) == 2,
)

check(
    "MULTI_INDEXES_ONE_BASED",
    [item["index"] for item in heading_map]
    == [1, 2],
)

check(
    "MULTI_HEADING_IDENTITY_EXACT",
    [
        item["heading"]
        for item in heading_map
    ]
    == headings,
)

check(
    "MULTI_POSITION_A_EXACT",
    heading_map[0]["char_position"]
    == body.find("Heading A"),
)

check(
    "MULTI_POSITION_B_EXACT",
    heading_map[1]["char_position"]
    == body.find("Heading B"),
)


# ------------------------------------------------------------
# C. Repeated headings
# ------------------------------------------------------------

print()
print("=== C. REPEATED HEADINGS ===")

body = (
    "Repeat\n\n"
    "Alpha\n\n"
    "Repeat\n\n"
    "Beta\n\n"
    "Repeat"
)

headings = [
    "Repeat",
    "Repeat",
    "Repeat",
]

heading_map = _build_heading_map(
    headings,
    body,
)

positions = [
    item["char_position"]
    for item in heading_map
]

expected_positions = []

search_from = 0

for _ in headings:
    pos = body.find(
        "Repeat",
        search_from,
    )

    expected_positions.append(
        pos
    )

    search_from = (
        pos + len("Repeat")
    )

check(
    "REPEATED_COUNT_THREE",
    len(heading_map) == 3,
)

check(
    "REPEATED_HEADINGS_PRESERVED",
    [
        item["heading"]
        for item in heading_map
    ]
    == headings,
)

check(
    "REPEATED_POSITIONS_SUCCESSIVE",
    positions == expected_positions,
)

check(
    "REPEATED_POSITIONS_DISTINCT",
    len(set(positions)) == 3,
)


# ------------------------------------------------------------
# D. Unmatched heading
# ------------------------------------------------------------

print()
print("=== D. UNMATCHED HEADING ===")

body = "Alpha\n\nBeta"
headings = [
    "Missing Heading",
]

heading_map = _build_heading_map(
    headings,
    body,
)

check(
    "UNMATCHED_HEADING_RETAINED",
    len(heading_map) == 1
    and heading_map[0]["heading"]
    == "Missing Heading",
)

check(
    "UNMATCHED_POSITION_NONE",
    heading_map[0]["char_position"]
    is None,
)


# ------------------------------------------------------------
# E. Heading-list order differs from body order
# ------------------------------------------------------------

print()
print("=== E. OUT-OF-BODY-ORDER HEADINGS ===")

body = (
    "Heading A\n\n"
    "Body\n\n"
    "Heading B"
)

headings = [
    "Heading B",
    "Heading A",
]

heading_map = _build_heading_map(
    headings,
    body,
)

check(
    "OUT_OF_ORDER_LIST_ORDER_PRESERVED",
    [
        item["heading"]
        for item in heading_map
    ]
    == headings,
)

check(
    "OUT_OF_ORDER_FIRST_POSITION_B",
    heading_map[0]["char_position"]
    == body.find("Heading B"),
)

check(
    "OUT_OF_ORDER_SECOND_FALLBACK_POSITION_A",
    heading_map[1]["char_position"]
    == body.find("Heading A"),
)


# ------------------------------------------------------------
# F. Unicode heading
# ------------------------------------------------------------

print()
print("=== F. UNICODE HEADING ===")

body = (
    "Intro\n\n"
    "Café 東京 Ω\n\n"
    "End"
)

headings = [
    "Café 東京 Ω",
]

heading_map = _build_heading_map(
    headings,
    body,
)

check(
    "UNICODE_HEADING_IDENTITY_EXACT",
    heading_map[0]["heading"]
    == headings[0],
)

check(
    "UNICODE_HEADING_POSITION_EXACT",
    heading_map[0]["char_position"]
    == body.find(
        headings[0]
    ),
)


# ------------------------------------------------------------
# G. Empty heading list
# ------------------------------------------------------------

print()
print("=== G. EMPTY HEADING LIST ===")

body = "Alpha beta"
headings = []

heading_map = _build_heading_map(
    headings,
    body,
)

check(
    "EMPTY_HEADING_LIST_RETURNS_EMPTY_MAP",
    heading_map == [],
)


# ------------------------------------------------------------
# H. Duplicate identity / no deduplication
# ------------------------------------------------------------

print()
print("=== H. DUPLICATE PRESERVATION ===")

body = (
    "Same\n\n"
    "Text\n\n"
    "Same"
)

headings = [
    "Same",
    "Same",
]

heading_map = _build_heading_map(
    headings,
    body,
)

check(
    "DUPLICATE_HEADING_COUNT_PRESERVED",
    len(heading_map) == 2,
)

check(
    "DUPLICATE_HEADING_IDENTITY_PRESERVED",
    [
        item["heading"]
        for item in heading_map
    ]
    == headings,
)


# ------------------------------------------------------------
# I. No mutation
# ------------------------------------------------------------

print()
print("=== I. INPUT IMMUTABILITY ===")

body = "Alpha\n\nHeading\n\nOmega"
headings = ["Heading"]

original_body = body
original_headings = list(headings)

_build_heading_map(
    headings,
    body,
)

check(
    "BODY_NOT_MUTATED",
    body == original_body,
)

check(
    "HEADINGS_NOT_MUTATED",
    headings == original_headings,
)


# ------------------------------------------------------------
# J. Exact heading identity contract
# ------------------------------------------------------------

print()
print("=== J. EXACT IDENTITY CONTRACT ===")

body = (
    "Heading One\n\n"
    "Heading Two"
)

headings = [
    "Heading One",
    "Heading Two",
]

heading_map = _build_heading_map(
    headings,
    body,
)

check(
    "HEADING_MAP_EXACTLY_MATCHES_CANONICAL_LIST",
    [
        item["heading"]
        for item in heading_map
    ]
    == headings,
)

check(
    "ALL_LEVELS_REMAIN_NONE",
    all(
        item["level"] is None
        for item in heading_map
    ),
)


# ------------------------------------------------------------
# K. Final decision
# ------------------------------------------------------------

print()
print("=== K. U8.8 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.8_HEADING_MAP_CONSTRUCTION: FAIL"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    raise RuntimeError(
        "U8.8 heading map verification failed."
    )

print(
    "U8.8_HEADING_MAP_CONSTRUCTION: CERTIFIED"
)

print(
    "U8.8_HEADING_SOURCE: EXACT_U7_NORMALIZED_HEADINGS"
)

print(
    "U8.8_INDEXING: ONE_BASED_LIST_ORDER"
)

print(
    "U8.8_DUPLICATES: PRESERVED"
)

print(
    "U8.8_HEADING_IDENTITY: EXACT"
)

print(
    "U8.8_POSITION_SEARCH: FORWARD_WITH_BEGINNING_FALLBACK"
)

print(
    "U8.8_UNMATCHED_HEADING_POSITION: NONE"
)

print(
    "U8.8_LEVEL_INFERENCE: NONE"
)

print(
    "U8.8_INPUT_MUTATION: NO"
)

print(
    "U8.8_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U8.9_DOCUMENT_ORDER_CONSTRUCTION_TRANSITION: AUTHORIZED"
)

print(
    "U8.8_FINAL_HEADING_MAP_VERIFICATION: PASS"
)