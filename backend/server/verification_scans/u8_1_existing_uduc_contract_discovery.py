from pathlib import Path
import ast


root = Path("backend/server")

uduc_path = (
    root
    / "stores"
    / "uploaded_document_unified_content.py"
)

normalizer_path = (
    root
    / "stores"
    / "upload_document_normalizer.py"
)

excluded_parts = {
    "backups",
    "verification_scans",
    "__pycache__",
}


def production_files():
    files = []

    for path in root.rglob("*.py"):
        if set(path.parts).intersection(
            excluded_parts
        ):
            continue

        files.append(path)

    return sorted(files)


files = production_files()


print(
    "=== U8.1 EXISTING UDUC CONTRACT DISCOVERY ==="
)

print(
    "UDUC_FILE_PRESENT=",
    uduc_path.exists(),
)

print(
    "UDUC_FILE=",
    uduc_path,
)


source = uduc_path.read_text(
    encoding="utf-8-sig",
)

tree = ast.parse(source)


# ------------------------------------------------------------
# A. Imports
# ------------------------------------------------------------

print()
print("=== A. IMPORTS ===")

for node in tree.body:
    if isinstance(
        node,
        (
            ast.Import,
            ast.ImportFrom,
        ),
    ):
        print(
            ast.get_source_segment(
                source,
                node,
            )
        )


# ------------------------------------------------------------
# B. Module-level constants
# ------------------------------------------------------------

print()
print("=== B. MODULE CONSTANTS ===")

for node in tree.body:
    if not isinstance(
        node,
        ast.Assign,
    ):
        continue

    names = [
        target.id
        for target in node.targets
        if isinstance(
            target,
            ast.Name,
        )
    ]

    if any(
        (
            "UDUC" in name
            or "VERSION" in name
            or "SCHEMA" in name
        )
        for name in names
    ):
        print(
            ast.get_source_segment(
                source,
                node,
            )
        )


# ------------------------------------------------------------
# C. UploadedDocumentUnifiedContent dataclass
# ------------------------------------------------------------

print()
print("=== C. UDUC DATACLASS ===")

uduc_class = next(
    (
        node
        for node in tree.body
        if isinstance(
            node,
            ast.ClassDef,
        )
        and node.name
        == "UploadedDocumentUnifiedContent"
    ),
    None,
)

if uduc_class is None:
    print(
        "UploadedDocumentUnifiedContent: NOT FOUND"
    )
else:
    print(
        ast.get_source_segment(
            source,
            uduc_class,
        )
    )


# ------------------------------------------------------------
# D. All top-level functions
# ------------------------------------------------------------

print()
print("=== D. TOP-LEVEL FUNCTIONS ===")

functions = []

for node in tree.body:
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    ):
        functions.append(
            node.name
        )
        print(node.name)

print(
    "FUNCTION_COUNT=",
    len(functions),
)


# ------------------------------------------------------------
# E. Key helpers / public APIs
# ------------------------------------------------------------

print()
print("=== E. KEY FUNCTION DEFINITIONS ===")

wanted = {
    "_now_iso",
    "_safe_workspace_id",
    "_safe_document_id",
    "_as_list",
    "_as_float",
    "_paragraphs_from_content_body",
    "_build_heading_map",
    "_build_uduc_structure",
    "build_uduc_from_upload_extraction_result",
    "serialize_uduc",
    "uduc_output_path",
    "write_uduc",
    "read_uduc",
    "build_and_write_uduc_from_extraction_result",
    "explain_uploaded_document_unified_content_v1",
}

for node in tree.body:
    if (
        isinstance(
            node,
            ast.FunctionDef,
        )
        and node.name
        in wanted
    ):
        print()
        print(
            f"--- {node.name} ---"
        )

        print(
            ast.get_source_segment(
                source,
                node,
            )
        )


# ------------------------------------------------------------
# F. Current U7 integration state
# ------------------------------------------------------------

print()
print("=== F. CURRENT U7 INTEGRATION STATE ===")

lowered = source.lower()

print(
    "REFERENCES_NORMALIZED_UPLOADED_DOCUMENT_CONTENT=",
    "YES"
    if "normalizeduploadeddocumentcontent"
    in lowered
    else "NO",
)

print(
    "REFERENCES_NORMALIZE_UPLOADED_DOCUMENT_V1=",
    "YES"
    if "normalize_uploaded_document_v1"
    in lowered
    else "NO",
)

print(
    "REFERENCES_UPLOAD_EXTRACTION_RESULT=",
    "YES"
    if "uploadextractionresult"
    in lowered
    else "NO",
)

print(
    "BUILDER_NAME_DIRECT_EXTRACTION_RESULT=",
    "YES"
    if "build_uduc_from_upload_extraction_result"
    in lowered
    else "NO",
)


# ------------------------------------------------------------
# G. Current content handling terms
# ------------------------------------------------------------

print()
print("=== G. CONTENT HANDLING TERM COUNTS ===")

content_terms = [
    ".strip(",
    ".replace(",
    ".lower(",
    "content_body",
    "title",
    "headings",
    "h1",
    "source_type",
    "source_format",
    "extension",
]

for term in content_terms:
    print(
        f"{term}: "
        f"{lowered.count(term.lower())}"
    )


# ------------------------------------------------------------
# H. Structural contract terms
# ------------------------------------------------------------

print()
print("=== H. STRUCTURAL CONTRACT TERM COUNTS ===")

structural_terms = [
    "paragraphs",
    "start_char",
    "end_char",
    "char_count",
    "word_count",
    "heading_map",
    "char_position",
    "document_order",
    "section_count",
    "paragraph_count",
    "estimated_word_count",
    "estimated_character_count",
    "structure_version",
]

for term in structural_terms:
    print(
        f"{term}: "
        f"{lowered.count(term.lower())}"
    )


# ------------------------------------------------------------
# I. Extraction provenance
# ------------------------------------------------------------

print()
print("=== I. EXTRACTION PROVENANCE TERM COUNTS ===")

provenance_terms = [
    "extraction_status",
    "extraction_confidence",
    "extraction_timestamp",
    "created_at",
    "extraction_method",
    "source_metadata",
    "line_count",
    "paragraph_count",
    "heading_count",
]

for term in provenance_terms:
    print(
        f"{term}: "
        f"{lowered.count(term.lower())}"
    )


# ------------------------------------------------------------
# J. Normalization provenance
# ------------------------------------------------------------

print()
print("=== J. NORMALIZATION PROVENANCE TERM COUNTS ===")

normalization_terms = [
    "normalization_status",
    "normalization_version",
    "normalized_at",
    '"normalization"',
    "unicode_form",
    "operations",
]

for term in normalization_terms:
    print(
        f"{term}: "
        f"{lowered.count(term.lower())}"
    )


# ------------------------------------------------------------
# K. Persistence contract
# ------------------------------------------------------------

print()
print("=== K. PERSISTENCE TERM COUNTS ===")

persistence_terms = [
    "json.dumps",
    "json.loads",
    "write_text",
    "read_text",
    "replace(",
    "tmp",
    "mkdir",
    "uduc_output_path",
    "write_uduc",
    "read_uduc",
]

for term in persistence_terms:
    print(
        f"{term}: "
        f"{lowered.count(term.lower())}"
    )


# ------------------------------------------------------------
# L. Production references to UDUC module
# ------------------------------------------------------------

print()
print("=== L. PRODUCTION REFERENCES TO UDUC MODULE ===")

module_refs = []

for path in files:
    if path == uduc_path:
        continue

    file_source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    if (
        "uploaded_document_unified_content"
        in file_source
    ):
        module_refs.append(
            path
        )

print(
    "UDUC_MODULE_REFERENCE_COUNT=",
    len(module_refs),
)

for path in module_refs:
    print(path)


# ------------------------------------------------------------
# M. Specific function references
# ------------------------------------------------------------

print()
print("=== M. PUBLIC FUNCTION REFERENCE COUNTS ===")

public_names = [
    "build_uduc_from_upload_extraction_result",
    "serialize_uduc",
    "uduc_output_path",
    "write_uduc",
    "read_uduc",
    "build_and_write_uduc_from_extraction_result",
]

for name in public_names:
    refs = []

    for path in files:
        if path == uduc_path:
            continue

        file_source = path.read_text(
            encoding="utf-8-sig",
            errors="ignore",
        )

        if name in file_source:
            refs.append(
                path
            )

    print()
    print(
        f"{name}_REFERENCE_COUNT="
        f"{len(refs)}"
    )

    for path in refs:
        print(path)


# ------------------------------------------------------------
# N. Downstream boundary scan
# ------------------------------------------------------------

print()
print("=== N. DOWNSTREAM BOUNDARY SCAN ===")

downstream_terms = [
    "highlight",
    "active_target_set",
    "target_score",
    "scorer",
    "score_phrase",
    "semantic_runtime",
    "ranking",
    "build_uucd",
    "build_transient_uucd",
    "content_ref",
    "body_ref",
]

for term in downstream_terms:
    print(
        f"{term}: "
        f"{lowered.count(term.lower())}"
    )


# ------------------------------------------------------------
# O. Candidate legacy / transitional patterns
# ------------------------------------------------------------

print()
print("=== O. TRANSITIONAL PATTERN EVIDENCE ===")

print(
    "DIRECT_UPLOAD_EXTRACTION_RESULT_BUILDER_PRESENT:",
    "YES"
    if "build_uduc_from_upload_extraction_result"
    in lowered
    else "NO",
)

print(
    "NORMALIZED_CONTENT_CANONICAL_INPUT_PRESENT:",
    "YES"
    if "normalizeduploadeddocumentcontent"
    in lowered
    else "NO",
)

print(
    "DEFENSIVE_STRIP_PRESENT:",
    "YES"
    if ".strip(" in lowered
    else "NO",
)

print(
    "CONTENT_BODY_FALLBACK_FROM_TEXT_PRESENT:",
    "YES"
    if (
        'er.get("content_body")'
        in source
        and 'er.get("text")'
        in source
    )
    else "NO",
)

print(
    "NORMALIZATION_PROVENANCE_SUPPORT_PRESENT:",
    "YES"
    if (
        "normalization_status"
        in lowered
        or "normalization_version"
        in lowered
        or "normalized_at"
        in lowered
    )
    else "NO",
)


# ------------------------------------------------------------
# P. Canonical discovery boundary
# ------------------------------------------------------------

print()
print("=== P. U8.1 DISCOVERY BOUNDARY ===")

print(
    "CURRENT_UDUC_INPUT:",
    "UploadExtractionResult-compatible object/dict",
)

print(
    "CURRENT_UDUC_OUTPUT:",
    "UploadedDocumentUnifiedContent",
)

print(
    "CURRENT_UDUC_STRUCTURAL_ROLE:",
    "paragraphs + heading_map + document_order + schema/persistence",
)

print(
    "CURRENT_U7_HANDOFF_WIRED:",
    "NO",
)

print(
    "U8_REALIGNMENT_REQUIRED:",
    "YES",
)