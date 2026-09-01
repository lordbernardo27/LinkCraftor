from pathlib import Path
import ast
import copy
import json
import py_compile
import tempfile

import backend.server.stores.uploaded_document_unified_content as uduc_module

from backend.server.stores.upload_document_extractor import (
    UploadExtractionResult,
)

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
    normalize_uploaded_document_v1,
)

from backend.server.stores.uploaded_document_unified_content import (
    build_and_write_uduc_from_normalized_content,
    build_uduc_from_normalized_content,
    serialize_uduc,
    read_uduc,
)


results = []


def check(name, condition):
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U8.24 BUILD / INTEGRATION VERIFICATION ===")


# ------------------------------------------------------------
# A. Production compile
# ------------------------------------------------------------

print()
print("=== A. PRODUCTION COMPILE ===")

paths = {
    "NORMALIZER": Path(
        "backend/server/stores/"
        "upload_document_normalizer.py"
    ),
    "UDUC": Path(
        "backend/server/stores/"
        "uploaded_document_unified_content.py"
    ),
    "UPLOAD_COORDINATOR": Path(
        "backend/server/pipelines/upload_document/"
        "coordinator.py"
    ),
}

for label, path in paths.items():
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
# B. Live coordinator inspection
# ------------------------------------------------------------

print()
print("=== B. LIVE COORDINATOR INTEGRATION ===")

coordinator_source = paths[
    "UPLOAD_COORDINATOR"
].read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

coordinator_lower = coordinator_source.lower()

check(
    "COORDINATOR_IMPORTS_CANONICAL_UDUC_WRITER",
    "build_and_write_uduc_from_normalized_content"
    in coordinator_source,
)

check(
    "COORDINATOR_CALLS_U7_NORMALIZER",
    "normalize_uploaded_document_v1"
    in coordinator_source,
)

u7_pos = coordinator_source.find(
    "normalize_uploaded_document_v1"
)

u8_pos = coordinator_source.find(
    "build_and_write_uduc_from_normalized_content"
)

check(
    "U7_PRECEDES_U8_IN_LIVE_COORDINATOR",
    u7_pos != -1
    and u8_pos != -1
    and u7_pos < u8_pos,
)

check(
    "COORDINATOR_USES_NORMALIZED_CONTENT_ARGUMENT",
    "normalized_content="
    in coordinator_source,
)

check(
    "UDUC_SUCCESS_GATE_PRESENT",
    'uduc_result.get("ok") is not True'
    in coordinator_source,
)


# ------------------------------------------------------------
# C. Separate downstream branches
# ------------------------------------------------------------

print()
print("=== C. DOWNSTREAM BRANCH SEPARATION ===")

check(
    "HIGHLIGHT_BRANCH_PRESENT",
    "run_uploaded_document_to_highlight_pipeline"
    in coordinator_source,
)

check(
    "REGISTRY_ATS_BRANCH_PRESENT",
    "run_uploaded_document_registry_to_active_target_set_pipeline"
    in coordinator_source,
)

check(
    "ATS_RECEIVES_CANONICAL_UDUC",
    "unified_content=uduc"
    in coordinator_source,
)

highlight_marker = coordinator_source.find(
    "run_uploaded_document_to_highlight_pipeline"
)

ats_marker = coordinator_source.find(
    "run_uploaded_document_registry_to_active_target_set_pipeline"
)

check(
    "DOWNSTREAM_BRANCHES_AFTER_UDUC",
    u8_pos != -1
    and highlight_marker > u8_pos
    and ats_marker > u8_pos,
)

check(
    "HIGHLIGHT_INPUT_REMAINS_EXTRACTION_DERIVED",
    "highlight_extraction_result"
    in coordinator_source
    and '"text": extraction_text'
    in coordinator_source,
)


# ------------------------------------------------------------
# D. Canonical UDUC module authority
# ------------------------------------------------------------

print()
print("=== D. CANONICAL UDUC AUTHORITY ===")

uduc_source = paths[
    "UDUC"
].read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

uduc_tree = ast.parse(
    uduc_source
)

function_names = {
    node.name
    for node in uduc_tree.body
    if isinstance(
        node,
        ast.FunctionDef,
    )
}

for name in [
    "build_uduc_from_normalized_content",
    "build_and_write_uduc_from_normalized_content",
    "serialize_uduc",
    "write_uduc",
    "read_uduc",
]:
    check(
        "CANONICAL_FUNCTION_PRESENT_"
        + name.upper(),
        name in function_names,
    )

for legacy_name in [
    "_coerce_upload_extraction_result",
    "build_uduc_from_upload_extraction_result",
    "build_and_write_uduc_from_extraction_result",
]:
    check(
        "LEGACY_FUNCTION_ABSENT_"
        + legacy_name.upper(),
        legacy_name
        not in function_names,
    )

check(
    "SCHEMA_V2_AUTHORITY",
    'UDUC_SCHEMA_VERSION = "uploaded_document_unified_content_v2"'
    in uduc_source,
)

check(
    "PIPELINE_V2_AUTHORITY",
    'UDUC_PIPELINE_VERSION = "uploaded_document_uduc_pipeline_v2"'
    in uduc_source,
)

check(
    "NO_SCHEMA_V1_AUTHORITY",
    '"uploaded_document_unified_content_v1"'
    not in uduc_source,
)

check(
    "NO_PIPELINE_V1_AUTHORITY",
    '"uploaded_document_uduc_pipeline_v1"'
    not in uduc_source,
)


# ------------------------------------------------------------
# E. Duplicate implementation scan
# ------------------------------------------------------------

print()
print("=== E. DUPLICATE IMPLEMENTATION SCAN ===")

excluded_parts = {
    "backups",
    "runtime_backups",
    "verification_scans",
    "__pycache__",
}

duplicate_hits = []

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

    if path == paths["UDUC"]:
        continue

    text = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    tree = ast.parse(
        text
    )

    for node in tree.body:
        if isinstance(
            node,
            ast.FunctionDef,
        ) and node.name in {
            "build_uduc_from_normalized_content",
            "build_and_write_uduc_from_normalized_content",
            "write_uduc",
            "read_uduc",
        }:
            duplicate_hits.append(
                (
                    str(path),
                    node.name,
                )
            )

print(
    "DUPLICATE_CANONICAL_IMPLEMENTATION_COUNT="
    + str(len(duplicate_hits))
)

for path, name in duplicate_hits:
    print(
        f"DUPLICATE_IMPLEMENTATION: "
        f"{path}: {name}"
    )

check(
    "NO_DUPLICATE_CANONICAL_UDUC_IMPLEMENTATION",
    len(duplicate_hits) == 0,
)


# ------------------------------------------------------------
# F. End-to-end U7 -> U8 fixture
# ------------------------------------------------------------

print()
print("=== F. U7 -> U8 END-TO-END FIXTURE ===")

extraction = UploadExtractionResult(
    source_path="C:/immutable/u8_24.txt",
    source_type="txt",
    title="U8.24 Integration Title",
    text=(
        "Heading A\n\n"
        "Integration paragraph one.\n\n"
        "Integration paragraph two."
    ),
    headings=[
        "Heading A",
    ],
    metadata={
        "filename": "u8_24.txt",
        "extension": ".txt",
        "file_size": 624,
        "extraction_method": "txt_upload_v1",
    },
    extraction_status="success",
    extraction_confidence=0.95,
    created_at="2026-09-01T01:25:00+00:00",
)

extraction_before = copy.deepcopy(
    extraction
)

normalized = normalize_uploaded_document_v1(
    extraction
)

check(
    "U7_RETURNS_NORMALIZED_CONTENT",
    isinstance(
        normalized,
        NormalizedUploadedDocumentContent,
    ),
)

check(
    "U7_NORMALIZATION_SUCCESS",
    normalized.normalization_status
    == "success",
)

normalized_before = copy.deepcopy(
    normalized
)

uduc = build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u8_24",
    document_id="doc_u8_24",
    original_filename="u8_24.txt",
    stored_filename="stored_u8_24.txt",
    stored_path="C:/persisted/ws_u8_24/stored_u8_24.txt",
)

serialized = serialize_uduc(
    uduc
)

check(
    "U8_SERIALIZATION_RETURNS_22_FIELDS",
    len(serialized) == 22,
)

check(
    "U7_TITLE_REACHES_U8",
    serialized.get("title")
    == normalized.title,
)

check(
    "U7_TEXT_REACHES_U8_EXACTLY",
    serialized.get("content_body")
    == normalized.text,
)

check(
    "U7_HEADINGS_REACH_U8_EXACTLY",
    serialized.get("headings")
    == normalized.headings,
)

check(
    "EXTRACTION_PROVENANCE_REACHES_U8",
    serialized.get(
        "extraction_created_at"
    )
    == extraction.created_at,
)

check(
    "NORMALIZATION_PROVENANCE_REACHES_U8",
    serialized.get(
        "normalized_at"
    )
    == normalized.normalized_at,
)

check(
    "EXTRACTION_INPUT_UNCHANGED",
    extraction
    == extraction_before,
)

check(
    "NORMALIZED_INPUT_UNCHANGED",
    normalized
    == normalized_before,
)


# ------------------------------------------------------------
# G. Persistence integration
# ------------------------------------------------------------

print()
print("=== G. PERSISTENCE INTEGRATION ===")

original_output_dir = getattr(
    uduc_module,
    "UDUC_OUTPUT_DIR",
    None,
)

with tempfile.TemporaryDirectory(
    prefix="u8_24_uduc_"
) as temp_dir:

    uduc_module.UDUC_OUTPUT_DIR = Path(
        temp_dir
    )

    result = (
        build_and_write_uduc_from_normalized_content(
            normalized_content=normalized,
            workspace_id="ws_u8_24",
            document_id="doc_u8_24",
            original_filename="u8_24.txt",
            stored_filename="stored_u8_24.txt",
            stored_path="C:/persisted/ws_u8_24/stored_u8_24.txt",
        )
    )

    check(
        "BUILD_WRITE_RESULT_OK",
        result.get("ok") is True,
    )

    persisted_path = Path(
        result.get(
            "uduc_path",
            "",
        )
    )

    check(
        "PERSISTED_PATH_EXISTS",
        persisted_path.exists(),
    )

    persisted = json.loads(
        persisted_path.read_text(
            encoding="utf-8"
        )
    )

    check(
        "PERSISTED_UDUC_HAS_22_FIELDS",
        len(persisted) == 22,
    )

    check(
        "PERSISTED_EQUALS_RETURNED_UDUC",
        persisted
        == result.get("uduc"),
    )

    round_trip = read_uduc(
        "ws_u8_24",
        "doc_u8_24",
    )

    check(
        "READ_ROUND_TRIP_EQUALS_PERSISTED",
        round_trip
        == persisted,
    )

    check(
        "PERSISTENCE_PATH_WORKSPACE_DOCUMENT_SCOPED",
        "ws_u8_24"
        in persisted_path.parts
        and persisted_path.name
        == "doc_u8_24.json",
    )

    uduc_module.UDUC_OUTPUT_DIR = (
        original_output_dir
    )


# ------------------------------------------------------------
# H. U8 boundary regression
# ------------------------------------------------------------

print()
print("=== H. U8 BOUNDARY REGRESSION ===")

uduc_lower = uduc_source.lower()

for marker in [
    "extract_upload_document",
    "detect_upload_source_type",
    "normalize_uploaded_document_v1",
    "run_uploaded_document_to_highlight_pipeline",
    "active_target_set",
    "build_uucd",
    "write_uucd",
    "universal_article_body_store",
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
# I. Final decision
# ------------------------------------------------------------

print()
print("=== I. U8.24 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.24_BUILD_INTEGRATION_VERIFICATION: REVIEW_REQUIRED"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    print(
        "U8.24_PATCH_DECISION_REQUIRED: REVIEW_EVIDENCE"
    )

else:
    print(
        "U8.24_BUILD_INTEGRATION_VERIFICATION: CERTIFIED"
    )
    print(
        "U8.24_PRODUCTION_COMPILE: PASS"
    )
    print(
        "U8.24_LIVE_COORDINATOR_INTEGRATION: PASS"
    )
    print(
        "U8.24_U7_TO_U8_HANDOFF: PASS"
    )
    print(
        "U8.24_CANONICAL_22_FIELD_SERIALIZATION: PASS"
    )
    print(
        "U8.24_UDUC_PERSISTENCE_INTEGRATION: PASS"
    )
    print(
        "U8.24_HIGHLIGHT_BRANCH_SEPARATION: PASS"
    )
    print(
        "U8.24_ATS_BRANCH_SEPARATION: PASS"
    )
    print(
        "U8.24_LEGACY_UDUC_PATHS: ABSENT"
    )
    print(
        "U8.24_DUPLICATE_CANONICAL_IMPLEMENTATION: NO"
    )
    print(
        "U8.24_SOURCE_REREAD: NO"
    )
    print(
        "U8.24_EXTRACTION_RERUN: NO"
    )
    print(
        "U8.24_NORMALIZATION_RERUN_INSIDE_U8: NO"
    )
    print(
        "U8.24_CURRENT_CANONICAL_UUCD_EXECUTION: NO"
    )
    print(
        "U8.24_BODY_STORE_RUNTIME_EXECUTION: NO"
    )
    print(
        "U8.24_SEMANTIC_SCORER_EXECUTION: NO"
    )
    print(
        "U8.24_PRODUCTION_PATCH_REQUIRED: NO"
    )
    print(
        "U8.25_PHASE_U8_CERTIFICATION_TRANSITION: AUTHORIZED"
    )
    print(
        "U8.24_FINAL_BUILD_INTEGRATION_VERIFICATION: PASS"
    )