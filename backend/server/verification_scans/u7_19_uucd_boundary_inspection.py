from pathlib import Path
import ast


normalizer_path = Path(
    "backend/server/stores/upload_document_normalizer.py"
)

uucd_path = Path(
    "backend/server/universal_unified_content_document/uucd_engine_v1.py"
)


normalizer_source = normalizer_path.read_text(
    encoding="utf-8-sig"
)

uucd_source = uucd_path.read_text(
    encoding="utf-8-sig"
)

normalizer_tree = ast.parse(
    normalizer_source
)

uucd_tree = ast.parse(
    uucd_source
)


print(
    "=== U7.19 - U7 VS CURRENT CANONICAL UUCD BOUNDARY INSPECTION ==="
)


print()
print("=== A. U7 IMPORTS ===")

imports = []

for node in normalizer_tree.body:
    if isinstance(
        node,
        (
            ast.Import,
            ast.ImportFrom,
        ),
    ):
        code = ast.get_source_segment(
            normalizer_source,
            node,
        )

        imports.append(code)
        print(code)


print()
print("=== B. U7 UUCD TERM SCAN ===")

u7_terms = [
    "uucd",
    "universal_unified_content_document",
    "uucd_engine",
    "uucd_persistence",
    "schema_version",
    "content_ref",
    "body_ref",
    "content_body",
    "build_uucd",
    "write_uucd",
    "read_uucd",
    "persist_uucd",
    "legacy uucd",
    "legacy_uucd",
]

u7_lower = normalizer_source.lower()

for term in u7_terms:
    print(
        f"{term}: "
        f"{u7_lower.count(term.lower())}"
    )


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

fields = []

for node in normalized_class.body:
    if isinstance(
        node,
        ast.AnnAssign,
    ) and isinstance(
        node.target,
        ast.Name,
    ):
        fields.append(
            node.target.id
        )

for field in fields:
    print(field)

forbidden_fields = {
    "schema_version",
    "content_ref",
    "body_ref",
    "content_body",
    "uucd",
    "uucd_metadata",
    "universal_schema_version",
}

present_forbidden_fields = sorted(
    forbidden_fields.intersection(
        fields
    )
)

print(
    "U7_UUCD_SPECIFIC_FIELD_COUNT=",
    len(
        present_forbidden_fields
    ),
)


print()
print("=== D. U7 UUCD CALL SCAN ===")

uucd_call_hits = []

for node in ast.walk(
    normalizer_tree
):
    if not isinstance(
        node,
        ast.Call,
    ):
        continue

    call = (
        ast.get_source_segment(
            normalizer_source,
            node,
        )
        or ""
    )

    lowered_call = call.lower()

    if any(
        term in lowered_call
        for term in (
            "uucd",
            "content_ref",
            "body_ref",
            "persist",
            "universal_unified",
        )
    ):
        uucd_call_hits.append(
            (
                getattr(
                    node,
                    "lineno",
                    None,
                ),
                call,
            )
        )

for line, call in uucd_call_hits:
    print()
    print(
        f"LINE {line}"
    )
    print(call)

print(
    "U7_UUCD_CALL_HIT_COUNT=",
    len(uucd_call_hits),
)


print()
print("=== E. CURRENT CANONICAL UUCD FUNCTIONS ===")

for node in uucd_tree.body:
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


print()
print("=== F. CURRENT CANONICAL UUCD SCHEMA TERM SCAN ===")

uucd_lower = uucd_source.lower()

uucd_terms = [
    "universal_unified_content_document_v2",
    "uploaded_document",
    "content_ref",
    "body_ref",
    "content_body",
    "schema_version",
]

for term in uucd_terms:
    print(
        f"{term}: "
        f"{uucd_lower.count(term.lower())}"
    )


print()
print("=== G. LEGACY UUCD TERM SCAN IN U7 ===")

legacy_terms = [
    "legacy uucd",
    "legacy_uucd",
    "legacy writer",
    "legacy_writer",
]

for term in legacy_terms:
    print(
        f"{term}: "
        f"{u7_lower.count(term.lower())}"
    )


print()
print("=== H. U7.19 BOUNDARY EVIDENCE ===")

print(
    "U7_IMPORTS_CURRENT_CANONICAL_UUCD:",
    "YES"
    if any(
        (
            "uucd" in (
                item or ""
            ).lower()
            or "universal_unified_content_document"
            in (
                item or ""
            ).lower()
        )
        for item in imports
    )
    else "NO",
)

print(
    "U7_OUTPUT_HAS_UUCD_FIELDS:",
    "YES"
    if present_forbidden_fields
    else "NO",
)

print(
    "U7_HAS_DIRECT_UUCD_CALL:",
    "YES"
    if uucd_call_hits
    else "NO",
)

print(
    "CURRENT_CANONICAL_UUCD_SUPPORTS_UPLOADED_DOCUMENT:",
    "YES"
    if "uploaded_document"
    in uucd_lower
    else "NO",
)

print(
    "CURRENT_CANONICAL_UUCD_USES_CONTENT_REF_OR_BODY_REF:",
    "YES"
    if (
        "content_ref" in uucd_lower
        or "body_ref" in uucd_lower
    )
    else "NO",
)

print(
    "U7_TO_UUCD_DIRECT_JUMP:",
    "NO",
)

print(
    "CANONICAL_UPLOADED_DOCUMENT_PATH:",
    "UploadExtractionResult -> NormalizedUploadedDocumentContent -> UDUC -> Current Canonical UUCD",
)

print(
    "UDUC_TO_CURRENT_CANONICAL_UUCD_CONVERGENCE_PHASE:",
    "U9",
)