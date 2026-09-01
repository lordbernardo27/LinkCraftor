from pathlib import Path
import ast
import py_compile

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)

from backend.server.stores.uploaded_document_unified_content import (
    build_uduc_from_normalized_content,
    build_and_write_uduc_from_normalized_content,
    serialize_uduc,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U8.22 FINAL LEGACY UDUC CLEANUP VERIFICATION ===")


# ------------------------------------------------------------
# A. Production compile
# ------------------------------------------------------------

print()
print("=== A. COMPILE ===")

uduc_path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

coordinator_path = Path(
    "backend/server/pipelines/upload_document/"
    "coordinator.py"
)

for label, path in [
    ("UDUC_MODULE", uduc_path),
    ("LIVE_UPLOAD_COORDINATOR", coordinator_path),
]:
    ok = True

    try:
        py_compile.compile(
            str(path),
            doraise=True,
        )
    except Exception as exc:
        ok = False
        print(
            f"{label}_COMPILE_ERROR="
            f"{type(exc).__name__}: {exc}"
        )

    check(
        f"{label}_COMPILES",
        ok,
    )


# ------------------------------------------------------------
# B. Parse canonical module
# ------------------------------------------------------------

print()
print("=== B. CANONICAL MODULE INVENTORY ===")

source = uduc_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

tree = ast.parse(source)

function_names = {
    node.name
    for node in tree.body
    if isinstance(
        node,
        ast.FunctionDef,
    )
}

legacy_functions = {
    "_coerce_upload_extraction_result",
    "build_uduc_from_upload_extraction_result",
    "build_and_write_uduc_from_extraction_result",
    "explain_uploaded_document_unified_content_v1",
}

for name in sorted(
    legacy_functions
):
    check(
        "LEGACY_FUNCTION_REMOVED_"
        + name.upper(),
        name not in function_names,
    )


# ------------------------------------------------------------
# C. Stale imports removed
# ------------------------------------------------------------

print()
print("=== C. STALE IMPORT CLEANUP ===")

check(
    "UPLOAD_EXTRACTION_RESULT_IMPORT_REMOVED",
    "UploadExtractionResult"
    not in source,
)

check(
    "LEGACY_NORMALIZER_CALL_IMPORT_REMOVED",
    "normalize_uploaded_document_v1"
    not in source,
)


# ------------------------------------------------------------
# D. Canonical U8 functions remain
# ------------------------------------------------------------

print()
print("=== D. CANONICAL U8 FUNCTIONS REMAIN ===")

canonical_functions = {
    "build_uduc_from_normalized_content",
    "serialize_uduc",
    "uduc_output_path",
    "write_uduc",
    "read_uduc",
    "build_and_write_uduc_from_normalized_content",
}

for name in sorted(
    canonical_functions
):
    check(
        "CANONICAL_FUNCTION_PRESENT_"
        + name.upper(),
        name in function_names,
    )


# ------------------------------------------------------------
# E. Exact current versions
# ------------------------------------------------------------

print()
print("=== E. VERSION AUTHORITY ===")

check(
    "CANONICAL_SCHEMA_V2_PRESENT",
    'UDUC_SCHEMA_VERSION = "uploaded_document_unified_content_v2"'
    in source,
)

check(
    "CANONICAL_PIPELINE_V2_PRESENT",
    'UDUC_PIPELINE_VERSION = "uploaded_document_uduc_pipeline_v2"'
    in source,
)

check(
    "LEGACY_SCHEMA_V1_NOT_PRESENT",
    '"uploaded_document_unified_content_v1"'
    not in source,
)

check(
    "LEGACY_PIPELINE_V1_NOT_PRESENT",
    '"uploaded_document_uduc_pipeline_v1"'
    not in source,
)


# ------------------------------------------------------------
# F. Behavioral canonical build
# ------------------------------------------------------------

print()
print("=== F. CANONICAL BUILD BEHAVIOR ===")

normalized = NormalizedUploadedDocumentContent(
    source_path="C:/immutable/u8_22.txt",
    source_type="txt",
    title="U8.22 Canonical Title",
    text=(
        "Paragraph one.\n\n"
        "Heading One\n\n"
        "Paragraph two."
    ),
    headings=[
        "Heading One",
    ],
    metadata={
        "filename": "u8_22.txt",
        "extension": ".txt",
        "file_size": 522,
        "extraction_method": "txt_upload_v1",
    },
    extraction_status="success",
    extraction_confidence=0.95,
    extraction_created_at="2026-09-01T01:10:00+00:00",
    normalization_status="success",
    normalization_version="uploaded_document_normalization_v1",
    normalized_at="2026-09-01T01:10:01+00:00",
)

uduc = build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u8_22",
    document_id="doc_u8_22",
    original_filename="u8_22.txt",
    stored_filename="stored_u8_22.txt",
    stored_path="C:/persisted/ws_u8_22/stored_u8_22.txt",
)

serialized = serialize_uduc(
    uduc
)

check(
    "CANONICAL_BUILD_RETURNS_22_FIELDS",
    len(serialized) == 22,
)

check(
    "CANONICAL_TITLE_PRESERVED",
    serialized.get("title")
    == "U8.22 Canonical Title",
)

check(
    "CANONICAL_CONTENT_BODY_PRESERVED",
    serialized.get("content_body")
    == (
        "Paragraph one.\n\n"
        "Heading One\n\n"
        "Paragraph two."
    ),
)

check(
    "CANONICAL_HEADINGS_PRESERVED",
    serialized.get("headings")
    == ["Heading One"],
)

check(
    "EXTRACTION_PROVENANCE_PRESERVED",
    serialized.get("extraction_created_at")
    == "2026-09-01T01:10:00+00:00",
)

check(
    "NORMALIZATION_PROVENANCE_PRESERVED",
    serialized.get("normalized_at")
    == "2026-09-01T01:10:01+00:00",
)


# ------------------------------------------------------------
# G. Live coordinator still uses canonical path
# ------------------------------------------------------------

print()
print("=== G. LIVE COORDINATOR AUTHORITY ===")

coordinator_source = coordinator_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

coordinator_lower = coordinator_source.lower()

check(
    "LIVE_COORDINATOR_USES_CANONICAL_NORMALIZED_BUILD_WRITE",
    "build_and_write_uduc_from_normalized_content"
    in coordinator_lower,
)

for legacy_name in [
    "_coerce_upload_extraction_result",
    "build_uduc_from_upload_extraction_result",
    "build_and_write_uduc_from_extraction_result",
]:
    check(
        "LIVE_COORDINATOR_NO_"
        + legacy_name.upper(),
        legacy_name.lower()
        not in coordinator_lower,
    )


# ------------------------------------------------------------
# H. No production callers for removed legacy symbols
# ------------------------------------------------------------

print()
print("=== H. PRODUCTION DEPENDENCY REGRESSION ===")

excluded_parts = {
    "backups",
    "runtime_backups",
    "verification_scans",
    "__pycache__",
}

legacy_hits = []

for path in Path(
    "backend/server"
).rglob(
    "*.py"
):
    if any(
        part in excluded_parts
        for part in path.parts
    ):
        continue

    text = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    for name in legacy_functions:
        if name in text:
            legacy_hits.append(
                (
                    str(path),
                    name,
                )
            )


print(
    "LEGACY_PRODUCTION_REFERENCE_COUNT="
    + str(len(legacy_hits))
)

for path, name in legacy_hits:
    print(
        f"LEGACY_PRODUCTION_REFERENCE: "
        f"{path}: {name}"
    )

check(
    "NO_LEGACY_PRODUCTION_REFERENCES",
    len(legacy_hits) == 0,
)


# ------------------------------------------------------------
# I. No preview-derived pseudo-UDUC execution
# ------------------------------------------------------------

print()
print("=== I. PSEUDO-UDUC AUTHORITY CHECK ===")

check(
    "NO_PREVIEW_DERIVED_UDUC_BUILD_CALL",
    "preview_derived_uduc"
    not in coordinator_lower
    and "pseudo_uduc"
    not in coordinator_lower,
)

check(
    "CANONICAL_UDUC_HANDOFF_TO_ATS_REMAINS",
    "unified_content=uduc"
    in coordinator_lower,
)


# ------------------------------------------------------------
# J. Boundary regression
# ------------------------------------------------------------

print()
print("=== J. U8 BOUNDARY REGRESSION ===")

uduc_lower = source.lower()

for marker in [
    "run_uploaded_document_to_highlight_pipeline",
    "active_target_set",
    "build_uucd",
    "write_uucd",
    "semantic_runtime",
    "run_semantic",
    "scorer",
]:
    check(
        "UDUC_CORE_NO_"
        + marker.upper(),
        marker.lower()
        not in uduc_lower,
    )


# ------------------------------------------------------------
# K. No reprocessing reintroduced
# ------------------------------------------------------------

print()
print("=== K. REPROCESSING REGRESSION ===")

for marker in [
    "extract_upload_document",
    "detect_upload_source_type",
    "normalize_uploaded_document_v1",
    "_normalize_title",
    "_normalize_headings",
    "unicodedata.normalize",
]:
    check(
        "UDUC_CORE_NO_"
        + marker.upper()
        .replace(".", "_"),
        marker.lower()
        not in uduc_lower,
    )


# ------------------------------------------------------------
# L. Final decision
# ------------------------------------------------------------

print()
print("=== L. U8.22 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.22_LEGACY_UDUC_CLEANUP: REVIEW_REQUIRED"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

else:
    print(
        "U8.22_LEGACY_UDUC_CLEANUP: CERTIFIED"
    )

    print(
        "U8.22_LEGACY_EXTRACTION_COMPATIBILITY_LAYER: REMOVED"
    )

    print(
        "U8.22_LEGACY_EXPLAIN_V1_HELPER: REMOVED"
    )

    print(
        "U8.22_STALE_IMPORTS: REMOVED"
    )

    print(
        "U8.22_CANONICAL_UDUC_AUTHORITY: NORMALIZED_CONTENT_PATH_ONLY"
    )

    print(
        "U8.22_SCHEMA_AUTHORITY: V2"
    )

    print(
        "U8.22_PIPELINE_AUTHORITY: V2"
    )

    print(
        "U8.22_SOURCE_REREAD: NO"
    )

    print(
        "U8.22_EXTRACTION_RERUN: NO"
    )

    print(
        "U8.22_NORMALIZATION_RERUN: NO"
    )

    print(
        "U8.22_HIGHLIGHT_ATS_BOUNDARY_REGRESSION: NO"
    )

    print(
        "U8.22_CURRENT_CANONICAL_UUCD_BOUNDARY_REGRESSION: NO"
    )

    print(
        "U8.22_PRODUCTION_PATCH_COMPLETE: YES"
    )

    print(
        "U8.23_BEHAVIORAL_UDUC_VERIFICATION_TRANSITION: AUTHORIZED"
    )

    print(
        "U8.22_FINAL_LEGACY_CLEANUP_VERIFICATION: PASS"
    )