from pathlib import Path
import importlib
import py_compile

from backend.server.stores.upload_document_extractor import (
    UploadExtractionResult,
)

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
    normalize_uploaded_document_v1,
)

from backend.server.stores.uploaded_document_unified_content import (
    UploadedDocumentUnifiedContent,
    build_uduc_from_normalized_content,
    build_uduc_from_upload_extraction_result,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print(
    "=== U8.5 COMPILE / HANDOFF VERIFICATION ==="
)


# ------------------------------------------------------------
# A. Compile modified production files
# ------------------------------------------------------------

print()
print("=== A. COMPILE VERIFICATION ===")

targets = [
    Path(
        "backend/server/stores/"
        "uploaded_document_unified_content.py"
    ),
    Path(
        "backend/server/pipelines/"
        "upload_document/coordinator.py"
    ),
]

compile_failures = []

for path in targets:
    try:
        py_compile.compile(
            str(path),
            doraise=True,
        )

        print(
            f"COMPILE_OK: {path}"
        )

    except Exception as exc:
        compile_failures.append(
            (
                path,
                type(exc).__name__,
            )
        )

        print(
            f"COMPILE_FAIL: {path}: "
            f"{type(exc).__name__}"
        )

check(
    "MODIFIED_FILE_COMPILE_FAILURE_COUNT_ZERO",
    len(compile_failures) == 0,
)


# ------------------------------------------------------------
# B. Import smoke test
# ------------------------------------------------------------

print()
print("=== B. IMPORT SMOKE TEST ===")

modules = [
    "backend.server.stores.upload_document_extractor",
    "backend.server.stores.upload_document_normalizer",
    "backend.server.stores.uploaded_document_unified_content",
    "backend.server.pipelines.upload_document.coordinator",
]

import_failures = []

for module_name in modules:
    try:
        importlib.import_module(
            module_name
        )

        print(
            f"IMPORT_OK: {module_name}"
        )

    except Exception as exc:
        import_failures.append(
            (
                module_name,
                type(exc).__name__,
                str(exc),
            )
        )

        print(
            f"IMPORT_FAIL: {module_name}: "
            f"{type(exc).__name__}"
        )

check(
    "IMPORT_FAILURE_COUNT_ZERO",
    len(import_failures) == 0,
)


# ------------------------------------------------------------
# C. Canonical U7 -> U8 handoff
# ------------------------------------------------------------

print()
print("=== C. CANONICAL U7 -> U8 HANDOFF ===")

extraction = UploadExtractionResult(
    source_path="C:/immutable/sample.txt",
    source_type="txt",
    title="  Cafe\u0301\tTitle ",
    text=(
        " Alpha   Beta\r\n\r\n\r\n"
        "Gamma\tDelta\u0000 "
    ),
    headings=[
        " Heading ",
        "Duplicate",
        "Duplicate",
    ],
    metadata={
        "filename": "sample.txt",
        "extension": ".txt",
        "method": "verification_fixture",
        "normalization_test_marker": "keep",
    },
    extraction_status="success",
    extraction_confidence=0.95,
    created_at="2026-08-31T00:00:00+00:00",
)

normalized = (
    normalize_uploaded_document_v1(
        extraction
    )
)

check(
    "U7_OUTPUT_TYPE",
    isinstance(
        normalized,
        NormalizedUploadedDocumentContent,
    ),
)

check(
    "U7_OUTPUT_STATUS_SUCCESS",
    normalized.normalization_status
    == "success",
)

uduc = build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_test",
    document_id="doc_test",
    original_filename="sample.txt",
    stored_filename="doc_test__sample.txt",
    stored_path=(
        "backend/server/data/docs/"
        "ws_test/doc_test__sample.txt"
    ),
    source_metadata={
        "doc_id": "doc_test",
        "filename": "sample.txt",
        "stored_name": "doc_test__sample.txt",
        "file_size": 123,
    },
)

check(
    "U8_OUTPUT_TYPE",
    isinstance(
        uduc,
        UploadedDocumentUnifiedContent,
    ),
)

check(
    "UDUC_SCHEMA_V2",
    uduc.schema_version
    == "uploaded_document_unified_content_v2",
)

check(
    "UDUC_PIPELINE_V2",
    uduc.pipeline_version
    == "uploaded_document_uduc_pipeline_v2",
)

check(
    "UDUC_NORMALIZED_TITLE_EXACT",
    uduc.title
    == normalized.title,
)

check(
    "UDUC_NORMALIZED_BODY_EXACT",
    uduc.content_body
    == normalized.text,
)

check(
    "UDUC_NORMALIZED_HEADINGS_EXACT",
    uduc.headings
    == normalized.headings,
)

check(
    "UDUC_EXTRACTION_STATUS_PRESERVED",
    uduc.extraction_status
    == normalized.extraction_status,
)

check(
    "UDUC_EXTRACTION_CONFIDENCE_PRESERVED",
    uduc.extraction_confidence
    == normalized.extraction_confidence,
)

check(
    "UDUC_EXTRACTION_CREATED_AT_PRESERVED",
    uduc.extraction_created_at
    == normalized.extraction_created_at,
)

check(
    "UDUC_NORMALIZATION_STATUS_PRESERVED",
    uduc.normalization_status
    == normalized.normalization_status,
)

check(
    "UDUC_NORMALIZATION_VERSION_PRESERVED",
    uduc.normalization_version
    == normalized.normalization_version,
)

check(
    "UDUC_NORMALIZED_AT_PRESERVED",
    uduc.normalized_at
    == normalized.normalized_at,
)

check(
    "UDUC_NORMALIZATION_METADATA_PRESERVED",
    uduc.metadata.get("normalization")
    == normalized.metadata.get(
        "normalization"
    ),
)


# ------------------------------------------------------------
# D. Structural construction remains active
# ------------------------------------------------------------

print()
print("=== D. STRUCTURAL CONSTRUCTION ===")

structure = uduc.structure

check(
    "STRUCTURE_IS_DICT",
    isinstance(
        structure,
        dict,
    ),
)

check(
    "PARAGRAPHS_PRESENT",
    isinstance(
        structure.get("paragraphs"),
        list,
    ),
)

check(
    "HEADING_MAP_PRESENT",
    isinstance(
        structure.get("heading_map"),
        list,
    ),
)

check(
    "DOCUMENT_ORDER_PRESENT",
    isinstance(
        structure.get("document_order"),
        list,
    ),
)

check(
    "STRUCTURE_DOES_NOT_REWRITE_CONTENT_BODY",
    uduc.content_body
    == normalized.text,
)


# ------------------------------------------------------------
# E. Legacy compatibility wrapper passes through U7
# ------------------------------------------------------------

print()
print("=== E. LEGACY COMPATIBILITY WRAPPER ===")

legacy_uduc = (
    build_uduc_from_upload_extraction_result(
        extraction_result=extraction,
        workspace_id="ws_test",
        document_id="doc_legacy",
        original_filename="sample.txt",
    )
)

check(
    "LEGACY_WRAPPER_RETURNS_UDUC",
    isinstance(
        legacy_uduc,
        UploadedDocumentUnifiedContent,
    ),
)

check(
    "LEGACY_WRAPPER_SCHEMA_V2",
    legacy_uduc.schema_version
    == "uploaded_document_unified_content_v2",
)

check(
    "LEGACY_WRAPPER_CONTENT_NORMALIZED",
    legacy_uduc.title
    == normalized.title
    and legacy_uduc.content_body
    == normalized.text
    and legacy_uduc.headings
    == normalized.headings,
)

check(
    "LEGACY_WRAPPER_HAS_U7_PROVENANCE",
    legacy_uduc.normalization_status
    == "success"
    and bool(
        legacy_uduc.normalization_version
    )
    and bool(
        legacy_uduc.normalized_at
    ),
)


# ------------------------------------------------------------
# F. Canonical builder rejects non-U7 inputs
# ------------------------------------------------------------

print()
print("=== F. CANONICAL INPUT ENFORCEMENT ===")

raw_rejected = False

try:
    build_uduc_from_normalized_content(
        normalized_content=extraction,
        workspace_id="ws_test",
        document_id="doc_bad",
    )
except TypeError:
    raw_rejected = True

check(
    "RAW_UPLOAD_EXTRACTION_RESULT_REJECTED",
    raw_rejected,
)


dict_rejected = False

try:
    build_uduc_from_normalized_content(
        normalized_content={
            "title": "bad"
        },
        workspace_id="ws_test",
        document_id="doc_bad",
    )
except TypeError:
    dict_rejected = True

check(
    "DICT_INPUT_REJECTED",
    dict_rejected,
)


# ------------------------------------------------------------
# G. Coordinator wiring
# ------------------------------------------------------------

print()
print("=== G. COORDINATOR WIRING ===")

coordinator_path = Path(
    "backend/server/pipelines/"
    "upload_document/coordinator.py"
)

coordinator_source = (
    coordinator_path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )
)

check(
    "COORDINATOR_IMPORTS_U7",
    "normalize_uploaded_document_v1"
    in coordinator_source,
)

check(
    "COORDINATOR_RECONSTRUCTS_EXTRACTION_RESULT",
    "canonical_extraction_result = UploadExtractionResult("
    in coordinator_source,
)

check(
    "COORDINATOR_CALLS_CANONICAL_UDUC_WRITER",
    "build_and_write_uduc_from_normalized_content("
    in coordinator_source,
)

check(
    "COORDINATOR_NO_LONGER_CALLS_LEGACY_WRITER",
    "build_and_write_uduc_from_extraction_result("
    not in coordinator_source,
)


# ------------------------------------------------------------
# H. Downstream boundary remains clean
# ------------------------------------------------------------

print()
print("=== H. DOWNSTREAM BOUNDARY ===")

uduc_path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

uduc_source = (
    uduc_path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    ).lower()
)

check(
    "NO_CURRENT_CANONICAL_UUCD_BUILD",
    "build_transient_uucd"
    not in uduc_source
    and "build_uucd"
    not in uduc_source,
)

check(
    "NO_CONTENT_REF_GENERATION",
    "content_ref"
    not in uduc_source,
)

check(
    "NO_BODY_REF_GENERATION",
    "body_ref"
    not in uduc_source,
)

check(
    "NO_HIGHLIGHT_EXECUTION",
    "highlight("
    not in uduc_source,
)

check(
    "NO_ATS_EXECUTION",
    "active_target_set("
    not in uduc_source,
)

check(
    "NO_SCORER_EXECUTION",
    "scorer("
    not in uduc_source
    and "score_phrase"
    not in uduc_source,
)


# ------------------------------------------------------------
# I. Final decision
# ------------------------------------------------------------

print()
print("=== I. U8.5 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U8.5_U7_TO_UDUC_HANDOFF_REALIGNMENT: FAIL"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    if import_failures:
        print(
            "IMPORT_FAILURE_DETAILS:"
        )

        for failure in import_failures:
            print(
                f" - {failure}"
            )

    raise RuntimeError(
        "U8.5 handoff verification failed."
    )

print(
    "U8.5_U7_TO_UDUC_HANDOFF_REALIGNMENT: CERTIFIED"
)

print(
    "U8.5_CANONICAL_HANDOFF: UploadExtractionResult -> NormalizedUploadedDocumentContent -> UploadedDocumentUnifiedContent"
)

print(
    "U8.5_UDUC_SCHEMA_VERSION: uploaded_document_unified_content_v2"
)

print(
    "U8.5_UDUC_PIPELINE_VERSION: uploaded_document_uduc_pipeline_v2"
)

print(
    "U8.5_CANONICAL_CONTENT_PARITY: PASS"
)

print(
    "U8.5_EXTRACTION_PROVENANCE: PRESERVED"
)

print(
    "U8.5_NORMALIZATION_PROVENANCE: PRESERVED"
)

print(
    "U8.5_LEGACY_EXTRACTION_WRAPPER_PASSES_THROUGH_U7: YES"
)

print(
    "U8.5_COORDINATOR_CANONICAL_U7_WIRING: YES"
)

print(
    "U8.5_CURRENT_CANONICAL_UUCD_EXECUTION: NO"
)

print(
    "U8.5_PRODUCTION_PATCH_REQUIRED: COMPLETE"
)

print(
    "U8.6_TRANSITIONAL_CONTENT_CLEANUP_TRANSITION: AUTHORIZED"
)

print(
    "U8.5_FINAL_U7_TO_UDUC_HANDOFF_VERIFICATION: PASS"
)