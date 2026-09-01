from pathlib import Path
import ast

from backend.server.stores.uploaded_document_unified_content import (
    _build_uduc_structure,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U8.10 CORRECTED STRUCTURAL SUMMARY VERIFICATION ===")


# ------------------------------------------------------------
# A. Canonical structure fixture
# ------------------------------------------------------------

body = (
    "Heading A\n\n"
    "Alpha beta\n\n"
    "Heading B\n\n"
    "Gamma"
)

headings = [
    "Heading A",
    "Heading B",
]

structure = _build_uduc_structure(
    body,
    headings,
)


# ------------------------------------------------------------
# B. Field inventory
# ------------------------------------------------------------

print()
print("=== A. FIELD INVENTORY ===")

expected_fields = {
    "paragraphs",
    "heading_map",
    "section_count",
    "paragraph_count",
    "document_order",
    "first_heading",
    "last_heading",
    "first_paragraph",
    "last_paragraph",
    "estimated_word_count",
    "estimated_character_count",
    "structure_version",
    "boundary",
}

check(
    "STRUCTURE_EXPECTED_FIELDS_PRESENT",
    expected_fields.issubset(
        structure.keys()
    ),
)


# ------------------------------------------------------------
# C. Counts
# ------------------------------------------------------------

print()
print("=== B. STRUCTURAL COUNTS ===")

check(
    "SECTION_COUNT_EQUALS_HEADING_MAP_LENGTH",
    structure["section_count"]
    == len(structure["heading_map"]),
)

check(
    "PARAGRAPH_COUNT_EQUALS_PARAGRAPH_LIST_LENGTH",
    structure["paragraph_count"]
    == len(structure["paragraphs"]),
)

duplicate_structure = _build_uduc_structure(
    "Repeat\n\nBody\n\nRepeat",
    ["Repeat", "Repeat"],
)

check(
    "DUPLICATE_HEADINGS_COUNT_SEPARATELY",
    duplicate_structure["section_count"]
    == 2,
)

unmatched_structure = _build_uduc_structure(
    "Alpha\n\nBeta",
    ["Missing Heading"],
)

check(
    "UNMATCHED_HEADING_COUNTS_AS_SECTION",
    unmatched_structure["section_count"]
    == 1,
)


# ------------------------------------------------------------
# D. First / last identities
# ------------------------------------------------------------

print()
print("=== C. FIRST / LAST IDENTITIES ===")

check(
    "FIRST_HEADING_EXACT",
    structure["first_heading"]
    == headings[0],
)

check(
    "LAST_HEADING_EXACT",
    structure["last_heading"]
    == headings[-1],
)

check(
    "FIRST_PARAGRAPH_EXACT",
    structure["first_paragraph"]
    == structure["paragraphs"][0]["text"],
)

check(
    "LAST_PARAGRAPH_EXACT",
    structure["last_paragraph"]
    == structure["paragraphs"][-1]["text"],
)

empty_structure = _build_uduc_structure(
    "",
    [],
)

check(
    "EMPTY_FIRST_HEADING_EMPTY",
    empty_structure["first_heading"]
    == "",
)

check(
    "EMPTY_LAST_HEADING_EMPTY",
    empty_structure["last_heading"]
    == "",
)

check(
    "EMPTY_FIRST_PARAGRAPH_EMPTY",
    empty_structure["first_paragraph"]
    == "",
)

check(
    "EMPTY_LAST_PARAGRAPH_EMPTY",
    empty_structure["last_paragraph"]
    == "",
)


# ------------------------------------------------------------
# E. Word / character counts
# ------------------------------------------------------------

print()
print("=== D. WORD / CHARACTER COUNTS ===")

count_body = (
    "Alpha beta\n"
    "Gamma\n\n"
    "Delta epsilon"
)

count_structure = _build_uduc_structure(
    count_body,
    [],
)

check(
    "WORD_COUNT_EXPECTED_FIVE",
    count_structure["estimated_word_count"]
    == 5,
)

unicode_body = "Café 東京\n\nRésumé Ω"

unicode_structure = _build_uduc_structure(
    unicode_body,
    [],
)

check(
    "UNICODE_WORD_COUNT_EXPECTED_FOUR",
    unicode_structure["estimated_word_count"]
    == 4,
)

check(
    "CHARACTER_COUNT_EQUALS_LEN_CONTENT_BODY",
    unicode_structure[
        "estimated_character_count"
    ]
    == len(unicode_body),
)


# ------------------------------------------------------------
# F. Boundary contract
# ------------------------------------------------------------

print()
print("=== E. BOUNDARY CONTRACT ===")

boundary = structure["boundary"]

check(
    "PRESERVES_CONTENT_BODY_TRUE",
    boundary.get(
        "preserves_content_body"
    )
    is True,
)

check(
    "MODIFIES_CONTENT_BODY_FALSE",
    boundary.get(
        "modifies_content_body"
    )
    is False,
)

check(
    "PERFORMS_CLEANING_FALSE",
    boundary.get(
        "performs_cleaning"
    )
    is False,
)

check(
    "PERFORMS_SEMANTIC_ANALYSIS_FALSE",
    boundary.get(
        "performs_semantic_analysis"
    )
    is False,
)


# ------------------------------------------------------------
# G. Version contract
# ------------------------------------------------------------

print()
print("=== F. STRUCTURE VERSION ===")

version = structure.get(
    "structure_version"
)

print(
    f"CURRENT_STRUCTURE_VERSION={version}"
)

check(
    "STRUCTURE_VERSION_V1_2",
    version
    == "uduc_structure_v1_2",
)


# ------------------------------------------------------------
# H. Input immutability
# ------------------------------------------------------------

print()
print("=== G. INPUT IMMUTABILITY ===")

test_body = "Heading\n\nAlpha beta"
test_headings = ["Heading"]

original_body = test_body
original_headings = list(test_headings)

_build_uduc_structure(
    test_body,
    test_headings,
)

check(
    "BODY_INPUT_UNCHANGED",
    test_body == original_body,
)

check(
    "HEADINGS_INPUT_UNCHANGED",
    test_headings == original_headings,
)


# ------------------------------------------------------------
# I. Corrected downstream boundary inspection
# ------------------------------------------------------------

print()
print("=== H. DOWNSTREAM BOUNDARY INSPECTION ===")

path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

source = path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

tree = ast.parse(source)

function_node = next(
    node
    for node in tree.body
    if isinstance(
        node,
        ast.FunctionDef,
    )
    and node.name
    == "_build_uduc_structure"
)

function_source = (
    ast.get_source_segment(
        source,
        function_node,
    )
    or ""
)

forbidden_execution_markers = [
    "run_highlight",
    "build_highlight",
    "active_target_set",
    "run_active_target",
    "scorer.",
    "score_document",
    "semantic_runtime",
    "semantic_reader",
    "run_semantic",
    "build_uucd",
    "write_uucd",
    "current_canonical_uucd",
    "content_ref",
    "body_ref",
]

for marker in forbidden_execution_markers:
    check(
        "NO_EXECUTION_MARKER_"
        + marker.upper().replace(
            ".",
            "_",
        ),
        marker.lower()
        not in function_source.lower(),
    )


# The literal word "semantic" is valid only in the explicit
# boundary declaration performs_semantic_analysis=False.
check(
    "SEMANTIC_BOUNDARY_FLAG_PRESENT_AND_FALSE",
    '"performs_semantic_analysis": False'
    in function_source,
)


# ------------------------------------------------------------
# J. Final certification
# ------------------------------------------------------------

print()
print("=== I. U8.10 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.10_STRUCTURAL_SUMMARY_CONTRACT: FAIL"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    raise RuntimeError(
        "U8.10 corrected verification failed."
    )

print(
    "U8.10_STRUCTURAL_SUMMARY_CONTRACT: CERTIFIED"
)

print(
    "U8.10_SECTION_COUNT: HEADING_MAP_LENGTH"
)

print(
    "U8.10_PARAGRAPH_COUNT: PARAGRAPH_LIST_LENGTH"
)

print(
    "U8.10_FIRST_LAST_HEADINGS: EXACT_CANONICAL_IDENTITIES"
)

print(
    "U8.10_FIRST_LAST_PARAGRAPHS: EXACT_PARAGRAPH_IDENTITIES"
)

print(
    "U8.10_WORD_COUNT: WHITESPACE_TOKEN_ESTIMATE"
)

print(
    "U8.10_CHARACTER_COUNT: LEN_CONTENT_BODY"
)

print(
    "U8.10_STRUCTURE_VERSION: uduc_structure_v1_2"
)

print(
    "U8.10_BOUNDARY_CONTRACT: PASS"
)

print(
    "U8.10_SEMANTIC_EXECUTION: NO"
)

print(
    "U8.10_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U8.11_WORKSPACE_IDENTITY_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U8.10_FINAL_STRUCTURAL_SUMMARY_VERIFICATION: PASS"
)