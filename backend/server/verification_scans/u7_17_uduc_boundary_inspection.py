from pathlib import Path
import ast


normalizer_path = Path(
    "backend/server/stores/upload_document_normalizer.py"
)

uduc_path = Path(
    "backend/server/stores/uploaded_document_unified_content.py"
)


normalizer_source = normalizer_path.read_text(
    encoding="utf-8-sig"
)

uduc_source = uduc_path.read_text(
    encoding="utf-8-sig"
)

normalizer_tree = ast.parse(
    normalizer_source
)

uduc_tree = ast.parse(
    uduc_source
)


print(
    "=== U7.17 - U7 VS UDUC RESPONSIBILITY BOUNDARY INSPECTION ==="
)


# ------------------------------------------------------------
# A. U7 normalizer imports
# ------------------------------------------------------------

print()
print("=== A. U7 NORMALIZER IMPORTS ===")

for node in normalizer_tree.body:
    if isinstance(
        node,
        (
            ast.Import,
            ast.ImportFrom,
        ),
    ):
        print(
            ast.get_source_segment(
                normalizer_source,
                node,
            )
        )


# ------------------------------------------------------------
# B. U7 structure / UDUC term scan
# ------------------------------------------------------------

print()
print("=== B. U7 STRUCTURE / UDUC TERM SCAN ===")

u7_terms = [
    "uploaded_document_unified_content",
    "build_uduc",
    "write_uduc",
    "read_uduc",
    "schema_version",
    "workspace_id",
    "document_id",
    "paragraphs",
    "paragraph_map",
    "heading_map",
    "document_order",
    "offset",
    "word_count",
    "structure",
]

u7_lower = normalizer_source.lower()

for term in u7_terms:
    print(
        f"{term}: "
        f"{u7_lower.count(term.lower())}"
    )


# ------------------------------------------------------------
# C. U7 output dataclass fields
# ------------------------------------------------------------

print()
print("=== C. U7 OUTPUT DATACLASS FIELDS ===")

normalized_class = next(
    node
    for node in normalizer_tree.body
    if isinstance(
        node,
        ast.ClassDef,
    )
    and node.name
    == "NormalizedUploadedDocumentContent"
)

normalized_fields = []

for node in normalized_class.body:
    if isinstance(
        node,
        ast.AnnAssign,
    ) and isinstance(
        node.target,
        ast.Name,
    ):
        normalized_fields.append(
            node.target.id
        )

for field in normalized_fields:
    print(field)

print(
    "U7_OUTPUT_FIELD_COUNT=",
    len(normalized_fields),
)


forbidden_u7_fields = {
    "workspace_id",
    "document_id",
    "schema_version",
    "structure",
    "paragraphs",
    "paragraph_map",
    "heading_map",
    "document_order",
    "offsets",
}

present_forbidden_u7_fields = sorted(
    forbidden_u7_fields.intersection(
        normalized_fields
    )
)

print(
    "U7_FORBIDDEN_STRUCTURAL_FIELD_COUNT=",
    len(
        present_forbidden_u7_fields
    ),
)

for field in present_forbidden_u7_fields:
    print(
        "FORBIDDEN_U7_FIELD=",
        field,
    )


# ------------------------------------------------------------
# D. UDUC imports and public functions
# ------------------------------------------------------------

print()
print("=== D. UDUC IMPORTS ===")

for node in uduc_tree.body:
    if isinstance(
        node,
        (
            ast.Import,
            ast.ImportFrom,
        ),
    ):
        print(
            ast.get_source_segment(
                uduc_source,
                node,
            )
        )


print()
print("=== E. UDUC FUNCTIONS ===")

for node in uduc_tree.body:
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    ):
        print(
            node.name
        )


# ------------------------------------------------------------
# F. Key UDUC functions
# ------------------------------------------------------------

print()
print("=== F. KEY UDUC STRUCTURAL FUNCTIONS ===")

wanted_functions = {
    "_as_list",
    "_paragraphs_from_content_body",
    "_build_heading_map",
    "_build_uduc_structure",
    "build_uduc_from_upload_extraction_result",
}

for node in uduc_tree.body:
    if (
        isinstance(
            node,
            ast.FunctionDef,
        )
        and node.name
        in wanted_functions
    ):
        print()
        print(
            f"--- {node.name} ---"
        )

        print(
            ast.get_source_segment(
                uduc_source,
                node,
            )
        )


# ------------------------------------------------------------
# G. UDUC normalization-like operations
# ------------------------------------------------------------

print()
print("=== G. UDUC NORMALIZATION-LIKE TERM SCAN ===")

uduc_terms = [
    ".strip(",
    ".lower(",
    ".upper(",
    "unicodedata",
    "normalize(",
    "re.sub",
    "replace(",
    "split(",
    "join(",
]

uduc_lower = uduc_source.lower()

for term in uduc_terms:
    print(
        f"{term}: "
        f"{uduc_lower.count(term.lower())}"
    )


# ------------------------------------------------------------
# H. UDUC persistence / structural terms
# ------------------------------------------------------------

print()
print("=== H. UDUC STRUCTURAL TERM SCAN ===")

structural_terms = [
    "paragraph",
    "heading_map",
    "document_order",
    "offset",
    "word_count",
    "schema_version",
    "workspace_id",
    "document_id",
    "write_uduc",
    "read_uduc",
]

for term in structural_terms:
    print(
        f"{term}: "
        f"{uduc_lower.count(term.lower())}"
    )


# ------------------------------------------------------------
# I. Boundary decision evidence
# ------------------------------------------------------------

print()
print("=== I. U7.17 BOUNDARY EVIDENCE ===")

print(
    "U7_OUTPUT_HAS_UDUC_STRUCTURAL_FIELDS:",
    "YES"
    if present_forbidden_u7_fields
    else "NO",
)

print(
    "U7_IMPORTS_UDUC_MODULE:",
    "YES"
    if "uploaded_document_unified_content"
    in u7_lower
    else "NO",
)

print(
    "U7_CREATES_UDUC_SCHEMA:",
    "YES"
    if (
        "schema_version" in u7_lower
        or "build_uduc" in u7_lower
    )
    else "NO",
)

print(
    "U7_TO_U8_HANDOFF_CLASS:",
    "NormalizedUploadedDocumentContent",
)

print(
    "UDUC_STRUCTURAL_RESPONSIBILITY_PRESENT:",
    "YES"
    if (
        "paragraph" in uduc_lower
        and "heading_map" in uduc_lower
        and "document_order" in uduc_lower
    )
    else "NO",
)

print(
    "UDUC_DEFENSIVE_STRIP_PRESENT:",
    "YES"
    if ".strip(" in uduc_lower
    else "NO",
)

print(
    "U7.17_EXPECTED_REALIGNMENT_LOCATION:",
    "U8",
)