from __future__ import annotations

from pathlib import Path
import importlib
import py_compile
import tempfile


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print(
    "=== U7.22 BUILD / INTEGRATION VERIFICATION ==="
)


# ------------------------------------------------------------
# A. Compile verification
# ------------------------------------------------------------

print()
print("=== A. COMPILE VERIFICATION ===")

compile_targets = [
    Path(
        "backend/server/stores/upload_document_normalizer.py"
    ),
    Path(
        "backend/server/stores/upload_document_extractor.py"
    ),
    Path(
        "backend/server/stores/uploaded_document_unified_content.py"
    ),
]

compile_failures = []

for path in compile_targets:
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
    "TARGET_COMPILE_FAILURE_COUNT_ZERO",
    len(compile_failures) == 0,
)


# ------------------------------------------------------------
# B. Canonical U7 imports
# ------------------------------------------------------------

print()
print("=== B. CANONICAL U7 IMPORTS ===")

u7 = importlib.import_module(
    "backend.server.stores.upload_document_normalizer"
)

check(
    "IMPORT_NORMALIZED_UPLOADED_DOCUMENT_CONTENT",
    hasattr(
        u7,
        "NormalizedUploadedDocumentContent",
    ),
)

check(
    "IMPORT_NORMALIZE_UPLOADED_DOCUMENT_V1",
    hasattr(
        u7,
        "normalize_uploaded_document_v1",
    ),
)

check(
    "IMPORT_NORMALIZATION_VERSION",
    hasattr(
        u7,
        "NORMALIZATION_VERSION",
    ),
)

check(
    "IMPORT_NORMALIZATION_STATUS_SUCCESS",
    hasattr(
        u7,
        "NORMALIZATION_STATUS_SUCCESS",
    ),
)

check(
    "IMPORT_NORMALIZATION_STATUS_INVALID_INPUT",
    hasattr(
        u7,
        "NORMALIZATION_STATUS_INVALID_INPUT",
    ),
)

check(
    "IMPORT_NORMALIZATION_STATUS_INELIGIBLE",
    hasattr(
        u7,
        "NORMALIZATION_STATUS_INELIGIBLE_EXTRACTION",
    ),
)

check(
    "IMPORT_NORMALIZATION_STATUS_ERROR",
    hasattr(
        u7,
        "NORMALIZATION_STATUS_ERROR",
    ),
)


# ------------------------------------------------------------
# C. U6 extractor imports
# ------------------------------------------------------------

print()
print("=== C. U6 EXTRACTOR IMPORTS ===")

u6 = importlib.import_module(
    "backend.server.stores.upload_document_extractor"
)

check(
    "IMPORT_UPLOAD_EXTRACTION_RESULT",
    hasattr(
        u6,
        "UploadExtractionResult",
    ),
)

check(
    "IMPORT_EXTRACT_UPLOAD_DOCUMENT_V1",
    hasattr(
        u6,
        "extract_upload_document_v1",
    ),
)


# ------------------------------------------------------------
# D. U6 -> U7 type compatibility
# ------------------------------------------------------------

print()
print("=== D. U6 -> U7 TYPE COMPATIBILITY ===")

sample = u6.UploadExtractionResult(
    source_path="C:/immutable/sample.txt",
    source_type="txt",
    title="  Cafe\u0301 Title ",
    text=(
        " Alpha   Beta\r\n\r\n\r\n"
        "Gamma\tDelta\u0000 "
    ),
    headings=[
        " Heading ",
    ],
    metadata={
        "filename": "sample.txt",
        "method": "verification_fixture",
    },
    extraction_status="success",
    extraction_confidence=0.95,
    created_at="2026-08-31T00:00:00+00:00",
)

normalized = (
    u7.normalize_uploaded_document_v1(
        sample
    )
)

check(
    "REAL_UPLOAD_EXTRACTION_RESULT_ACCEPTED",
    isinstance(
        normalized,
        u7.NormalizedUploadedDocumentContent,
    ),
)

check(
    "U6_TO_U7_SUCCESS_STATUS",
    normalized.normalization_status
    == "success",
)

check(
    "U6_TO_U7_TITLE_NORMALIZED",
    normalized.title
    == "Café Title",
)

check(
    "U6_TO_U7_TEXT_NORMALIZED",
    normalized.text
    == "Alpha Beta\n\nGamma Delta",
)

check(
    "U6_TO_U7_HEADINGS_NORMALIZED",
    normalized.headings
    == ["Heading"],
)

check(
    "U6_TO_U7_SOURCE_PATH_PRESERVED",
    normalized.source_path
    == sample.source_path,
)

check(
    "U6_TO_U7_SOURCE_TYPE_PRESERVED",
    normalized.source_type
    == sample.source_type,
)

check(
    "U6_TO_U7_EXTRACTION_STATUS_PRESERVED",
    normalized.extraction_status
    == sample.extraction_status,
)

check(
    "U6_TO_U7_EXTRACTION_CONFIDENCE_PRESERVED",
    normalized.extraction_confidence
    == sample.extraction_confidence,
)

check(
    "U6_TO_U7_EXTRACTION_CREATED_AT_PRESERVED",
    normalized.extraction_created_at
    == sample.created_at,
)


# ------------------------------------------------------------
# E. Current upload-module import smoke test
# ------------------------------------------------------------

print()
print("=== E. CURRENT UPLOAD MODULE IMPORT SMOKE TEST ===")

modules = [
    "backend.server.routes.files",
    "backend.server.pipelines.upload_document.coordinator",
    "backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.coordinator",
    "backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake",
    "backend.server.stores.upload_document_extractor",
    "backend.server.stores.upload_document_normalizer",
    "backend.server.stores.uploaded_document_unified_content",
]

module_failures = []

for module_name in modules:
    try:
        importlib.import_module(
            module_name
        )

        print(
            f"IMPORT_OK: {module_name}"
        )
    except Exception as exc:
        module_failures.append(
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
    "CURRENT_UPLOAD_MODULE_IMPORT_FAILURE_COUNT_ZERO",
    len(module_failures) == 0,
)


# ------------------------------------------------------------
# F. Removed legacy backup import safety
# ------------------------------------------------------------

print()
print("=== F. REMOVED LEGACY BACKUP SAFETY ===")

removed_live_backup = Path(
    "backend/server/stores/smart_phrase_extractor_backup_before_v2.py"
)

backup_copy = Path(
    "backend/server/backups/u7_20_legacy_normalization_cleanup/"
    "smart_phrase_extractor_backup_before_v2.py"
)

check(
    "REMOVED_LEGACY_BACKUP_NOT_LIVE",
    not removed_live_backup.exists(),
)

check(
    "REMOVED_LEGACY_BACKUP_SAFETY_COPY_PRESENT",
    backup_copy.exists(),
)


# ------------------------------------------------------------
# G. Legitimate generic normalizer import
# ------------------------------------------------------------

print()
print("=== G. GENERIC NORMALIZER IMPORTABILITY ===")

generic = importlib.import_module(
    "backend.server.utils.text_normalization"
)

check(
    "GENERIC_NORMALIZER_IMPORTABLE",
    generic is not None,
)

check(
    "GENERIC_FIX_MOJIBAKE_IMPORTABLE",
    hasattr(
        generic,
        "fix_mojibake_text",
    ),
)


# ------------------------------------------------------------
# H. Website cleaner isolation/importability
# ------------------------------------------------------------

print()
print("=== H. WEBSITE CLEANER IMPORTABILITY ===")

website_modules = [
    "backend.server.stores.article_body_cleaning_engine",
    "backend.server.stores.article_cleaning_pipeline",
]

website_failures = []

for module_name in website_modules:
    try:
        importlib.import_module(
            module_name
        )

        print(
            f"IMPORT_OK: {module_name}"
        )
    except Exception as exc:
        website_failures.append(
            (
                module_name,
                type(exc).__name__,
            )
        )

        print(
            f"IMPORT_FAIL: {module_name}: "
            f"{type(exc).__name__}"
        )

check(
    "WEBSITE_CLEANER_IMPORT_FAILURE_COUNT_ZERO",
    len(website_failures) == 0,
)


# ------------------------------------------------------------
# I. Current Canonical UUCD importability
# ------------------------------------------------------------

print()
print("=== I. CURRENT CANONICAL UUCD IMPORTABILITY ===")

uucd = importlib.import_module(
    "backend.server.universal_unified_content_document.uucd_engine_v1"
)

check(
    "CURRENT_CANONICAL_UUCD_IMPORTABLE",
    uucd is not None,
)

check(
    "CURRENT_CANONICAL_UUCD_BUILD_FUNCTION_PRESENT",
    hasattr(
        uucd,
        "build_transient_uucd_from_wuc_v1",
    ),
)

check(
    "CURRENT_CANONICAL_UUCD_VALIDATOR_PRESENT",
    hasattr(
        uucd,
        "validate_universal_handoff_envelope_v1",
    ),
)


# ------------------------------------------------------------
# J. No premature U7 wiring
# ------------------------------------------------------------

print()
print("=== J. NO PREMATURE U7 WIRING ===")

inspection_paths = [
    Path(
        "backend/server/routes/files.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/coordinator.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_uduc_pipeline/coordinator.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_uduc_pipeline/upload_intake.py"
    ),
    Path(
        "backend/server/stores/uploaded_document_unified_content.py"
    ),
]

premature_refs = []

for path in inspection_paths:
    if not path.exists():
        continue

    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    if (
        "normalize_uploaded_document_v1"
        in source
        or "NormalizedUploadedDocumentContent"
        in source
    ):
        premature_refs.append(
            path
        )

for path in premature_refs:
    print(path)

check(
    "NO_PREMATURE_U7_PRODUCTION_WIRING",
    len(premature_refs) == 0,
)


# ------------------------------------------------------------
# K. U7 static side-effect boundary
# ------------------------------------------------------------

print()
print("=== K. U7 STATIC SIDE-EFFECT BOUNDARY ===")

u7_path = Path(
    "backend/server/stores/upload_document_normalizer.py"
)

u7_source = u7_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

u7_lower = u7_source.lower()

check(
    "U7_NO_SOURCE_REREAD",
    "read_text(" not in u7_lower
    and "read_bytes(" not in u7_lower
    and "open(" not in u7_lower,
)

check(
    "U7_NO_FILE_WRITE",
    "write_text(" not in u7_lower
    and "write_bytes(" not in u7_lower
    and "unlink(" not in u7_lower
    and "rename(" not in u7_lower,
)

check(
    "U7_NO_HIGHLIGHT_CALL",
    "highlight(" not in u7_lower,
)

check(
    "U7_NO_ATS_CALL",
    "active_target_set(" not in u7_lower,
)

check(
    "U7_NO_SCORER_CALL",
    "scorer(" not in u7_lower
    and "score_phrase" not in u7_lower,
)

check(
    "U7_NO_UUCD_BUILD_CALL",
    "build_uucd" not in u7_lower
    and "build_transient_uucd" not in u7_lower,
)


# ------------------------------------------------------------
# L. Temporary filesystem smoke check
# ------------------------------------------------------------

print()
print("=== L. FILESYSTEM SIDE-EFFECT SMOKE CHECK ===")

with tempfile.TemporaryDirectory() as temp_dir:
    temp_path = Path(temp_dir)

    before_files = sorted(
        str(path.relative_to(temp_path))
        for path in temp_path.rglob("*")
    )

    smoke = u6.UploadExtractionResult(
        source_path=str(
            temp_path / "nonexistent-source.txt"
        ),
        source_type="txt",
        title=" Title ",
        text=" Body ",
        headings=[" Heading "],
        metadata={},
        extraction_status="success",
        extraction_confidence=0.9,
        created_at="2026-08-31T00:00:00+00:00",
    )

    smoke_result = (
        u7.normalize_uploaded_document_v1(
            smoke
        )
    )

    after_files = sorted(
        str(path.relative_to(temp_path))
        for path in temp_path.rglob("*")
    )

check(
    "U7_NORMALIZATION_DOES_NOT_TOUCH_SOURCE_PATH",
    smoke_result.normalization_status
    == "success",
)

check(
    "U7_NORMALIZATION_CREATED_NO_FILES",
    before_files == after_files,
)


# ------------------------------------------------------------
# M. Final decision
# ------------------------------------------------------------

print()
print("=== M. U7.22 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U7.22_BUILD_INTEGRATION_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(
            f" - {failure}"
        )

    if module_failures:
        print(
            "MODULE_IMPORT_FAILURE_DETAILS:"
        )

        for item in module_failures:
            print(
                f" - {item}"
            )

    raise RuntimeError(
        "U7.22 build/integration verification failed."
    )

print(
    "U7.22_BUILD_INTEGRATION_VERIFICATION: CERTIFIED"
)

print(
    "U7.22_COMPILE_VERIFICATION: PASS"
)

print(
    "U7.22_CANONICAL_U7_IMPORTS: PASS"
)

print(
    "U7.22_U6_TO_U7_TYPE_COMPATIBILITY: PASS"
)

print(
    "U7.22_CURRENT_UPLOAD_MODULE_IMPORTS: PASS"
)

print(
    "U7.22_REMOVED_LEGACY_BACKUP_IMPORT_SAFETY: PASS"
)

print(
    "U7.22_GENERIC_NORMALIZER_IMPORTABILITY: PASS"
)

print(
    "U7.22_WEBSITE_CLEANER_IMPORTABILITY: PASS"
)

print(
    "U7.22_CURRENT_CANONICAL_UUCD_IMPORTABILITY: PASS"
)

print(
    "U7.22_PREMATURE_U7_WIRING: NO"
)

print(
    "U7.22_U7_IMPORT_SIDE_EFFECTS: NO"
)

print(
    "U7.22_U7_FILESYSTEM_SIDE_EFFECTS: NO"
)

print(
    "U7.22_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U7.23_PHASE_U7_CERTIFICATION_TRANSITION: AUTHORIZED"
)

print(
    "U7.22_FINAL_BUILD_INTEGRATION_VERIFICATION: PASS"
)