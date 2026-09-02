from copy import deepcopy

import backend.server.stores.uploaded_document_unified_content as uduc_module

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)


print("=== U9.8 STRUCTURAL CONVERGENCE CONTRACT INSPECTION ===")


# ------------------------------------------------------------
# A. Build canonical UDUC fixture
# ------------------------------------------------------------

print()
print("=== A. CANONICAL UDUC STRUCTURE FIXTURE ===")

body = (
    "Heading A\n\n"
    "Paragraph one.\n\n"
    "Heading A\n\n"
    "Paragraph two."
)

normalized = NormalizedUploadedDocumentContent(
    source_path="C:/immutable/u9_8.txt",
    source_type="txt",
    title="U9.8 Structural Contract",
    text=body,
    headings=[
        "Heading A",
        "Heading A",
        "Unmatched Heading",
    ],
    metadata={
        "filename": "u9_8.txt",
        "extension": ".txt",
        "file_size": len(
            body.encode("utf-8")
        ),
        "extraction_method": "txt_upload_v1",
    },
    extraction_status="success",
    extraction_confidence=1.0,
    extraction_created_at="2026-09-01T17:35:00+00:00",
    normalization_status="success",
    normalization_version="uploaded_document_normalization_v1",
    normalized_at="2026-09-01T17:35:01+00:00",
)

uduc = uduc_module.build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u9_8",
    document_id="upload_doc_u9_8",
    original_filename="u9_8.txt",
    stored_filename="stored_u9_8.txt",
    stored_path="C:/persisted/ws_u9_8/stored_u9_8.txt",
    source_metadata={},
)

serialized = uduc_module.serialize_uduc(
    uduc
)

structure = serialized[
    "structure"
]

print(
    "STRUCTURE_VERSION="
    + repr(
        structure.get(
            "structure_version"
        )
    )
)

print(
    "STRUCTURE_KEYS="
    + repr(
        list(
            structure.keys()
        )
    )
)


# ------------------------------------------------------------
# B. Required structural fields
# ------------------------------------------------------------

print()
print("=== B. REQUIRED STRUCTURAL FIELD PRESENCE ===")

required_fields = [
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
]

for field in required_fields:
    print(
        f"STRUCTURE_FIELD_{field.upper()}="
        f"{field in structure}"
    )


# ------------------------------------------------------------
# C. Paragraph contract
# ------------------------------------------------------------

print()
print("=== C. PARAGRAPH CONTRACT ===")

paragraphs = structure.get(
    "paragraphs",
    [],
)

print(
    "PARAGRAPH_COUNT="
    + str(
        len(paragraphs)
    )
)

for paragraph in paragraphs:
    print(
        "PARAGRAPH="
        + repr(
            paragraph
        )
    )

paragraph_required_fields = {
    "index",
    "text",
    "start_char",
    "end_char",
    "char_count",
    "word_count",
}

print(
    "ALL_PARAGRAPHS_HAVE_REQUIRED_FIELDS="
    + str(
        all(
            paragraph_required_fields.issubset(
                paragraph
            )
            for paragraph in paragraphs
        )
    )
)


# ------------------------------------------------------------
# D. Heading map contract
# ------------------------------------------------------------

print()
print("=== D. HEADING MAP CONTRACT ===")

heading_map = structure.get(
    "heading_map",
    [],
)

print(
    "HEADING_MAP_COUNT="
    + str(
        len(heading_map)
    )
)

for heading in heading_map:
    print(
        "HEADING_MAP_ENTRY="
        + repr(
            heading
        )
    )

print(
    "DUPLICATE_HEADINGS_PRESERVED="
    + str(
        sum(
            1
            for item in heading_map
            if item.get(
                "heading"
            )
            == "Heading A"
        )
        == 2
    )
)

print(
    "UNMATCHED_HEADING_PRESENT="
    + str(
        any(
            item.get(
                "heading"
            )
            == "Unmatched Heading"
            for item in heading_map
        )
    )
)

print(
    "UNMATCHED_HEADING_POSITION_IS_NULL="
    + str(
        any(
            item.get(
                "heading"
            )
            == "Unmatched Heading"
            and item.get(
                "char_position"
            )
            is None
            for item in heading_map
        )
    )
)


# ------------------------------------------------------------
# E. Document-order contract
# ------------------------------------------------------------

print()
print("=== E. DOCUMENT ORDER CONTRACT ===")

document_order = structure.get(
    "document_order",
    [],
)

for item in document_order:
    print(
        "DOCUMENT_ORDER_ENTRY="
        + repr(
            item
        )
    )

positioned_values = []

for item in document_order:
    if item.get(
        "type"
    ) == "heading":
        position = item.get(
            "char_position"
        )
    else:
        position = item.get(
            "start_char"
        )

    if isinstance(
        position,
        int,
    ):
        positioned_values.append(
            position
        )

print(
    "POSITIONED_DOCUMENT_ORDER_MONOTONIC="
    + str(
        positioned_values
        == sorted(
            positioned_values
        )
    )
)

unmatched_indexes = [
    index
    for index, item in enumerate(
        document_order
    )
    if (
        item.get(
            "type"
        )
        == "heading"
        and item.get(
            "char_position"
        )
        is None
    )
]

last_positioned_index = max(
    (
        index
        for index, item in enumerate(
            document_order
        )
        if (
            item.get(
                "char_position"
            )
            if item.get(
                "type"
            )
            == "heading"
            else item.get(
                "start_char"
            )
        )
        is not None
    ),
    default=-1,
)

print(
    "UNMATCHED_HEADINGS_AFTER_POSITIONED_CONTENT="
    + str(
        all(
            index > last_positioned_index
            for index in unmatched_indexes
        )
    )
)


# ------------------------------------------------------------
# F. Deep-copy convergence simulation
# ------------------------------------------------------------

print()
print("=== F. DEEP-COPY CONVERGENCE SIMULATION ===")

input_structure_before = deepcopy(
    structure
)

uucd_structure = deepcopy(
    structure
)

print(
    "UUCD_STRUCTURE_VALUE_EQUAL_UDUC_STRUCTURE="
    + str(
        uucd_structure
        == structure
    )
)

print(
    "UUCD_STRUCTURE_SAME_OBJECT_AS_UDUC_STRUCTURE="
    + str(
        uucd_structure
        is structure
    )
)

print(
    "UUCD_PARAGRAPHS_SAME_OBJECT="
    + str(
        uucd_structure.get(
            "paragraphs"
        )
        is structure.get(
            "paragraphs"
        )
    )
)

print(
    "UUCD_HEADING_MAP_SAME_OBJECT="
    + str(
        uucd_structure.get(
            "heading_map"
        )
        is structure.get(
            "heading_map"
        )
    )
)

print(
    "UUCD_DOCUMENT_ORDER_SAME_OBJECT="
    + str(
        uucd_structure.get(
            "document_order"
        )
        is structure.get(
            "document_order"
        )
    )
)


# ------------------------------------------------------------
# G. Mutation isolation
# ------------------------------------------------------------

print()
print("=== G. MUTATION ISOLATION ===")

uucd_structure[
    "section_count"
] = 999

if uucd_structure.get(
    "paragraphs"
):
    uucd_structure[
        "paragraphs"
    ][0][
        "text"
    ] = "MUTATED"

print(
    "INPUT_STRUCTURE_UNCHANGED_AFTER_UUCD_MUTATION="
    + str(
        structure
        == input_structure_before
    )
)


# ------------------------------------------------------------
# H. No structural recomputation
# ------------------------------------------------------------

print()
print("=== H. STRUCTURAL RECOMPUTATION EXCLUSIONS ===")

prohibited_actions = [
    "reparagraph",
    "redetect headings",
    "rebuild sections",
    "clean structure",
    "recompute structure",
]

for action in prohibited_actions:
    print(
        f"PROHIBITED_ACTION={action}"
    )

print(
    "U9_STRUCTURE_OPERATION="
    "DEEPCOPY_ONLY"
)


# ------------------------------------------------------------
# I. Structure/body separation
# ------------------------------------------------------------

print()
print("=== I. STRUCTURE / BODY SEPARATION ===")

print(
    "CONTENT_BODY_IN_STRUCTURE="
    + str(
        "content_body"
        in structure
    )
)

print(
    "STRUCTURE_IS_SEPARATE_FROM_BODY="
    + str(
        serialized.get(
            "content_body"
        )
        is not structure
    )
)


# ------------------------------------------------------------
# J. Boundary preservation
# ------------------------------------------------------------

print()
print("=== J. STRUCTURE BOUNDARY PRESERVATION ===")

boundary = structure.get(
    "boundary",
    {},
)

for key, value in boundary.items():
    print(
        f"BOUNDARY_{key.upper()}="
        + repr(value)
    )

print(
    "BOUNDARY_PRESERVES_CONTENT_BODY="
    + str(
        boundary.get(
            "preserves_content_body"
        )
        is True
    )
)

print(
    "BOUNDARY_MODIFIES_CONTENT_BODY_FALSE="
    + str(
        boundary.get(
            "modifies_content_body"
        )
        is False
    )
)

print(
    "BOUNDARY_PERFORMS_CLEANING_FALSE="
    + str(
        boundary.get(
            "performs_cleaning"
        )
        is False
    )
)

print(
    "BOUNDARY_PERFORMS_SEMANTIC_ANALYSIS_FALSE="
    + str(
        boundary.get(
            "performs_semantic_analysis"
        )
        is False
    )
)


# ------------------------------------------------------------
# K. Final U9.8 decision
# ------------------------------------------------------------

print()
print("=== K. U9.8 STRUCTURAL CONVERGENCE DECISION ===")

print(
    "U9.8_STRUCTURE_AUTHORITY="
    "UDUC_STRUCTURE"
)

print(
    "U9.8_CONVERGENCE_OPERATION="
    "DEEPCOPY"
)

print(
    "U9.8_STRUCTURE_RECOMPUTATION_ALLOWED=False"
)

print(
    "U9.8_REPARAGRAPHING_ALLOWED=False"
)

print(
    "U9.8_HEADING_REDETECTION_ALLOWED=False"
)

print(
    "U9.8_SECTION_RECONSTRUCTION_ALLOWED=False"
)

print(
    "U9.8_STRUCTURAL_CLEANUP_ALLOWED=False"
)

print(
    "U9.8_STRUCTURE_VERSION_EXPECTED="
    "uduc_structure_v1_2"
)

print(
    "U9.8_PATCH_DECISION: NONE_INSPECTION_ONLY"
)

print(
    "U9.8_NEXT_STEP: FREEZE_STRUCTURAL_CONVERGENCE_CONTRACT"
)