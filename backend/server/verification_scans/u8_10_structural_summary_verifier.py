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


print("=== U8.10 STRUCTURAL SUMMARY CONTRACT VERIFICATION ===")


# ------------------------------------------------------------
# A. Inventory current structure fields
# ------------------------------------------------------------

print()
print("=== A. STRUCTURE FIELD INVENTORY ===")

body = "Heading A\n\nAlpha beta\n\nHeading B\n\nGamma"
headings = [
    "Heading A",
    "Heading B",
]

structure = _build_uduc_structure(
    body,
    headings,
)

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
        set(structure.keys())
    ),
)


# ------------------------------------------------------------
# B. Section count
# ------------------------------------------------------------

print()
print("=== B. SECTION COUNT ===")

check(
    "SECTION_COUNT_EQUALS_HEADING_MAP_LENGTH",
    structure["section_count"]
    == len(structure["heading_map"]),
)

duplicate_structure = _build_uduc_structure(
    "Repeat\n\nBody\n\nRepeat",
    ["Repeat", "Repeat"],
)

check(
    "DUPLICATE_HEADINGS_COUNT_AS_SEPARATE_SECTIONS",
    duplicate_structure["section_count"] == 2,
)

unmatched_structure = _build_uduc_structure(
    "Alpha\n\nBeta",
    ["Missing Heading"],
)

check(
    "UNMATCHED_HEADING_STILL_COUNTS_AS_SECTION",
    unmatched_structure["section_count"] == 1,
)


# ------------------------------------------------------------
# C. Paragraph count
# ------------------------------------------------------------

print()
print("=== C. PARAGRAPH COUNT ===")

check(
    "PARAGRAPH_COUNT_EQUALS_PARAGRAPH_LIST_LENGTH",
    structure["paragraph_count"]
    == len(structure["paragraphs"]),
)

multi_paragraph_structure = _build_uduc_structure(
    "Alpha\n\nBeta\n\nGamma",
    [],
)

check(
    "THREE_PARAGRAPHS_COUNT_THREE",
    multi_paragraph_structure["paragraph_count"]
    == 3,
)


# ------------------------------------------------------------
# D. First / last heading
# ------------------------------------------------------------

print()
print("=== D. FIRST / LAST HEADING ===")

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

no_heading_structure = _build_uduc_structure(
    "Alpha\n\nBeta",
    [],
)

check(
    "NO_HEADING_FIRST_EMPTY",
    no_heading_structure["first_heading"]
    == "",
)

check(
    "NO_HEADING_LAST_EMPTY",
    no_heading_structure["last_heading"]
    == "",
)


# ------------------------------------------------------------
# E. First / last paragraph
# ------------------------------------------------------------

print()
print("=== E. FIRST / LAST PARAGRAPH ===")

paragraphs = structure["paragraphs"]

check(
    "FIRST_PARAGRAPH_EXACT",
    structure["first_paragraph"]
    == paragraphs[0]["text"],
)

check(
    "LAST_PARAGRAPH_EXACT",
    structure["last_paragraph"]
    == paragraphs[-1]["text"],
)

empty_structure = _build_uduc_structure(
    "",
    [],
)

check(
    "EMPTY_DOCUMENT_FIRST_PARAGRAPH_EMPTY",
    empty_structure["first_paragraph"]
    == "",
)

check(
    "EMPTY_DOCUMENT_LAST_PARAGRAPH_EMPTY",
    empty_structure["last_paragraph"]
    == "",
)


# ------------------------------------------------------------
# F. Estimated word count
# ------------------------------------------------------------

print()
print("=== F. ESTIMATED WORD COUNT ===")

body = "Alpha beta\nGamma\n\nDelta epsilon"
structure = _build_uduc_structure(
    body,
    [],
)

check(
    "WORD_COUNT_EXPECTED_FIVE",
    structure["estimated_word_count"]
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


# ------------------------------------------------------------
# G. Estimated character count
# ------------------------------------------------------------

print()
print("=== G. ESTIMATED CHARACTER COUNT ===")

check(
    "CHARACTER_COUNT_EQUALS_LEN_BODY",
    unicode_structure[
        "estimated_character_count"
    ]
    == len(unicode_body),
)


# ------------------------------------------------------------
# H. Structure version
# ------------------------------------------------------------

print()
print("=== H. STRUCTURE VERSION ===")

structure_version = structure.get(
    "structure_version"
)

print(
    f"CURRENT_STRUCTURE_VERSION={structure_version}"
)

check(
    "STRUCTURE_VERSION_PRESENT",
    isinstance(
        structure_version,
        str,
    )
    and bool(structure_version),
)


# ------------------------------------------------------------
# I. Boundary contract
# ------------------------------------------------------------

print()
print("=== I. BOUNDARY CONTRACT ===")

boundary = structure.get(
    "boundary",
    {},
)

check(
    "BOUNDARY_PRESERVES_CONTENT_BODY_TRUE",
    boundary.get(
        "preserves_content_body"
    )
    is True,
)

check(
    "BOUNDARY_MODIFIES_CONTENT_BODY_FALSE",
    boundary.get(
        "modifies_content_body"
    )
    is False,
)

check(
    "BOUNDARY_PERFORMS_CLEANING_FALSE",
    boundary.get(
        "performs_cleaning"
    )
    is False,
)

check(
    "BOUNDARY_PERFORMS_SEMANTIC_ANALYSIS_FALSE",
    boundary.get(
        "performs_semantic_analysis"
    )
    is False,
)


# ------------------------------------------------------------
# J. Exact identity / immutability
# ------------------------------------------------------------

print()
print("=== J. EXACT IDENTITY / IMMUTABILITY ===")

body = "Heading\n\nAlpha beta"
headings = ["Heading"]

original_body = body
original_headings = list(headings)

structure = _build_uduc_structure(
    body,
    headings,
)

check(
    "STRUCTURE_BODY_INPUT_UNCHANGED",
    body == original_body,
)

check(
    "STRUCTURE_HEADINGS_INPUT_UNCHANGED",
    headings == original_headings,
)

check(
    "STRUCTURE_FIRST_HEADING_IDENTITY_EXACT",
    structure["first_heading"]
    == headings[0],
)

check(
    "STRUCTURE_LAST_HEADING_IDENTITY_EXACT",
    structure["last_heading"]
    == headings[-1],
)

check(
    "STRUCTURE_FIRST_PARAGRAPH_IDENTITY_EXACT",
    structure["first_paragraph"]
    == structure["paragraphs"][0]["text"],
)

check(
    "STRUCTURE_LAST_PARAGRAPH_IDENTITY_EXACT",
    structure["last_paragraph"]
    == structure["paragraphs"][-1]["text"],
)


# ------------------------------------------------------------
# K. Static downstream-boundary inspection
# ------------------------------------------------------------

print()
print("=== K. DOWNSTREAM BOUNDARY INSPECTION ===")

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

forbidden = [
    "highlight",
    "active_target",
    "scorer",
    "semantic",
    "uucd",
    "content_ref",
    "body_ref",
]

for marker in forbidden:
    check(
        f"STRUCTURE_NO_{marker.upper()}_WORK",
        marker.lower()
        not in function_source.lower(),
    )


# ------------------------------------------------------------
# L. Version-change inspection
# ------------------------------------------------------------

print()
print("=== L. VERSION CHANGE INSPECTION ===")

print(
    "U8.10_VERSION_REVIEW_NOTE:"
    " U8.6 changed structural text-preservation behavior;"
    " U8.9 changed unmatched-heading document ordering."
)

check(
    "STRUCTURE_VERSION_IS_CURRENT_V1_2",
    structure_version
    == "uduc_structure_v1_2",
)


# ------------------------------------------------------------
# M. Final decision
# ------------------------------------------------------------

print()
print("=== M. U8.10 FINAL DECISION ===")

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

    print(
        "U8.10_PATCH_DECISION_REQUIRED: YES"
    )

else:
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
        "U8.10_BOUNDARY_CONTRACT: PASS"
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