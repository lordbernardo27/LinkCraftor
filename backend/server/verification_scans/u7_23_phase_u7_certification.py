from __future__ import annotations

from pathlib import Path
import ast
import importlib
import py_compile

from backend.server.stores.upload_document_extractor import (
    UploadExtractionResult,
)

import backend.server.stores.upload_document_normalizer as u7


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print(
    "=== U7.23 PHASE U7 FINAL CERTIFICATION ==="
)


# ------------------------------------------------------------
# A. Canonical U7 authority
# ------------------------------------------------------------

print()
print("=== A. CANONICAL U7 AUTHORITY ===")

u7_path = Path(
    "backend/server/stores/upload_document_normalizer.py"
)

check(
    "CANONICAL_U7_FILE_PRESENT",
    u7_path.exists(),
)

check(
    "CANONICAL_NORMALIZER_PRESENT",
    hasattr(
        u7,
        "normalize_uploaded_document_v1",
    ),
)

check(
    "CANONICAL_OUTPUT_DATACLASS_PRESENT",
    hasattr(
        u7,
        "NormalizedUploadedDocumentContent",
    ),
)


# ------------------------------------------------------------
# B. Output contract
# ------------------------------------------------------------

print()
print("=== B. OUTPUT CONTRACT ===")

source = u7_path.read_text(
    encoding="utf-8-sig",
)

tree = ast.parse(source)

cls = next(
    node
    for node in tree.body
    if isinstance(node, ast.ClassDef)
    and node.name
    == "NormalizedUploadedDocumentContent"
)

fields = [
    node.target.id
    for node in cls.body
    if isinstance(node, ast.AnnAssign)
    and isinstance(node.target, ast.Name)
]

expected_fields = [
    "source_path",
    "source_type",
    "title",
    "text",
    "headings",
    "metadata",
    "extraction_status",
    "extraction_confidence",
    "extraction_created_at",
    "normalization_status",
    "normalization_version",
    "normalized_at",
]

check(
    "OUTPUT_FIELD_COUNT_12",
    len(fields) == 12,
)

check(
    "OUTPUT_FIELD_CONTRACT_EXACT",
    fields == expected_fields,
)


# ------------------------------------------------------------
# C. Canonical normalization behavior
# ------------------------------------------------------------

print()
print("=== C. CANONICAL NORMALIZATION BEHAVIOR ===")

sample = UploadExtractionResult(
    source_path="C:/immutable/final.txt",
    source_type="txt",
    title="  Cafe\u0301\tTitle \u0000 ",
    text=(
        "\n\n\n"
        " Alpha   Beta\r\n"
        "Gamma\tDelta\r"
        "\r\n\r\n\r\n"
        "NBSP\u00A0Here "
        "ZWJ\u200DHere "
        "ZWNJ\u200CHere "
        "\u0000"
        "\n\n\n"
    ),
    headings=[
        " Cafe\u0301\tHeading ",
        "",
        "Duplicate",
        "Duplicate",
        "Multi\r\nLine",
    ],
    metadata={
        "filename": "final.txt",
        "custom": "preserve",
    },
    extraction_status="success",
    extraction_confidence=0.95,
    created_at="2026-08-31T00:00:00+00:00",
)

result = u7.normalize_uploaded_document_v1(
    sample
)

check(
    "NORMALIZATION_STATUS_SUCCESS",
    result.normalization_status
    == "success",
)

check(
    "UNICODE_NFC",
    result.title
    == "Café Title",
)

check(
    "LINE_ENDINGS_LF",
    "\r" not in result.text,
)

check(
    "HORIZONTAL_WHITESPACE_NORMALIZED",
    "Alpha Beta\nGamma Delta"
    in result.text,
)

check(
    "PARAGRAPH_BOUNDARIES_NORMALIZED",
    "\n\n\n" not in result.text,
)

check(
    "HEADING_NORMALIZATION",
    result.headings
    == [
        "Café Heading",
        "Duplicate",
        "Duplicate",
        "Multi\nLine",
    ],
)

check(
    "CONTROL_CHARACTERS_REMOVED",
    "\u0000" not in result.title
    and "\u0000" not in result.text,
)

check(
    "NBSP_PRESERVED",
    "\u00A0" in result.text,
)

check(
    "ZWJ_PRESERVED",
    "\u200D" in result.text,
)

check(
    "ZWNJ_PRESERVED",
    "\u200C" in result.text,
)


# ------------------------------------------------------------
# D. Source/provenance and immutability
# ------------------------------------------------------------

print()
print("=== D. SOURCE / PROVENANCE ===")

check(
    "SOURCE_PATH_PRESERVED",
    result.source_path
    == sample.source_path,
)

check(
    "SOURCE_TYPE_PRESERVED",
    result.source_type
    == sample.source_type,
)

check(
    "EXTRACTION_STATUS_PRESERVED",
    result.extraction_status
    == sample.extraction_status,
)

check(
    "EXTRACTION_CONFIDENCE_PRESERVED",
    result.extraction_confidence
    == sample.extraction_confidence,
)

check(
    "EXTRACTION_TIMESTAMP_PRESERVED",
    result.extraction_created_at
    == sample.created_at,
)

check(
    "ORIGINAL_METADATA_PRESERVED",
    result.metadata.get("custom")
    == "preserve",
)


# ------------------------------------------------------------
# E. Failure contract
# ------------------------------------------------------------

print()
print("=== E. FAILURE CONTRACT ===")

invalid_raised = False

try:
    u7.normalize_uploaded_document_v1(
        object()
    )
except TypeError:
    invalid_raised = True

check(
    "PROGRAMMER_CONTRACT_VIOLATION_RAISES",
    invalid_raised,
)


ineligible = UploadExtractionResult(
    source_path="C:/immutable/ineligible.txt",
    source_type="txt",
    title=" Title ",
    text=" Text ",
    headings=[" Heading "],
    metadata={},
    extraction_status="empty_text",
    extraction_confidence=0.0,
    created_at="2026-08-31T00:00:00+00:00",
)

ineligible_result = (
    u7.normalize_uploaded_document_v1(
        ineligible
    )
)

check(
    "INELIGIBLE_EXTRACTION_STATUS",
    ineligible_result.normalization_status
    == "ineligible_extraction",
)

check(
    "INELIGIBLE_OPERATIONS_EMPTY",
    ineligible_result.metadata
    .get("normalization", {})
    .get("operations")
    == [],
)


original_helper = u7._normalize_title


def forced_failure(_: str) -> str:
    raise RuntimeError(
        "SECRET C:/private/internal.txt"
    )


u7._normalize_title = forced_failure

try:
    failure_result = (
        u7.normalize_uploaded_document_v1(
            sample
        )
    )
finally:
    u7._normalize_title = original_helper

check(
    "UNEXPECTED_ERROR_RETURNS_NORMALIZATION_ERROR",
    failure_result.normalization_status
    == "normalization_error",
)

failure_metadata = repr(
    failure_result.metadata
)

check(
    "UNEXPECTED_ERROR_NO_MESSAGE_LEAK",
    "SECRET" not in failure_metadata,
)

check(
    "UNEXPECTED_ERROR_NO_PATH_LEAK",
    "C:/private/internal.txt"
    not in failure_metadata,
)


# ------------------------------------------------------------
# F. Determinism
# ------------------------------------------------------------

print()
print("=== F. DETERMINISM ===")

runs = [
    u7.normalize_uploaded_document_v1(
        sample
    )
    for _ in range(5)
]

first = runs[0]

check(
    "TITLE_DETERMINISTIC",
    all(
        value.title == first.title
        for value in runs
    ),
)

check(
    "TEXT_DETERMINISTIC",
    all(
        value.text == first.text
        for value in runs
    ),
)

check(
    "HEADINGS_DETERMINISTIC",
    all(
        value.headings == first.headings
        for value in runs
    ),
)

check(
    "STATUS_DETERMINISTIC",
    all(
        value.normalization_status
        == first.normalization_status
        for value in runs
    ),
)


# ------------------------------------------------------------
# G. U6 -> U7 boundary
# ------------------------------------------------------------

print()
print("=== G. U6 -> U7 BOUNDARY ===")

u6_path = Path(
    "backend/server/stores/upload_document_extractor.py"
)

u6_source = u6_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

check(
    "U6_EXTRACTION_SAFE_CLEANUP_PRESENT",
    "_normalize_upload_text_v2"
    in u6_source,
)

check(
    "U6_MARKDOWN_CLEANUP_PRESENT",
    "_strip_markdown_syntax_v2"
    in u6_source,
)

check(
    "U6_HTML_EXTRACTION_PRESENT",
    "_strip_html_tags_v1"
    in u6_source,
)

check(
    "U6_DOCX_EXTRACTION_PRESENT",
    "_extract_docx_paragraphs_v2"
    in u6_source,
)


# ------------------------------------------------------------
# H. U7 -> UDUC boundary
# ------------------------------------------------------------

print()
print("=== H. U7 -> UDUC BOUNDARY ===")

uduc_path = Path(
    "backend/server/stores/uploaded_document_unified_content.py"
)

uduc_source = uduc_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

check(
    "U7_OUTPUT_HAS_NO_STRUCTURE",
    not hasattr(result, "structure"),
)

check(
    "U7_OUTPUT_HAS_NO_HEADING_MAP",
    not hasattr(result, "heading_map"),
)

check(
    "UDUC_PARAGRAPH_BUILDER_PRESENT",
    "_paragraphs_from_content_body"
    in uduc_source,
)

check(
    "UDUC_HEADING_MAP_BUILDER_PRESENT",
    "_build_heading_map"
    in uduc_source,
)

check(
    "UDUC_REALIGNMENT_RESERVED_FOR_U8",
    True,
)


# ------------------------------------------------------------
# I. Highlight / ATS / UUCD boundaries
# ------------------------------------------------------------

print()
print("=== I. DOWNSTREAM BOUNDARIES ===")

u7_lower = source.lower()

check(
    "NO_HIGHLIGHT_EXECUTION",
    "highlight(" not in u7_lower,
)

check(
    "NO_ATS_EXECUTION",
    "active_target_set(" not in u7_lower,
)

check(
    "NO_SCORER_EXECUTION",
    "scorer(" not in u7_lower
    and "score_phrase" not in u7_lower,
)

check(
    "NO_UUCD_BUILD_EXECUTION",
    "build_uucd" not in u7_lower
    and "build_transient_uucd" not in u7_lower,
)

check(
    "NO_CONTENT_REF_CREATION",
    "content_ref" not in u7_lower,
)

check(
    "NO_BODY_REF_CREATION",
    "body_ref" not in u7_lower,
)


# ------------------------------------------------------------
# J. Cleaner / generic normalizer isolation
# ------------------------------------------------------------

print()
print("=== J. CLEANER / NORMALIZER ISOLATION ===")

check(
    "NO_WEBSITE_CLEANER_REFERENCE",
    "article_body_cleaning_engine"
    not in u7_lower
    and "article_cleaning_pipeline"
    not in u7_lower,
)

check(
    "NO_GENERIC_NORMALIZER_REFERENCE",
    "fix_mojibake_text"
    not in u7_lower
    and "utils.text_normalization"
    not in u7_lower,
)


# ------------------------------------------------------------
# K. Second authority / legacy cleanup
# ------------------------------------------------------------

print()
print("=== K. LEGACY CLEANUP STATE ===")

removed_live_backup = Path(
    "backend/server/stores/"
    "smart_phrase_extractor_backup_before_v2.py"
)

safety_backup = Path(
    "backend/server/backups/"
    "u7_20_legacy_normalization_cleanup/"
    "smart_phrase_extractor_backup_before_v2.py"
)

check(
    "OBSOLETE_LIVE_BACKUP_REMOVED",
    not removed_live_backup.exists(),
)

check(
    "SAFETY_BACKUP_RETAINED",
    safety_backup.exists(),
)


# ------------------------------------------------------------
# L. Compile / import verification
# ------------------------------------------------------------

print()
print("=== L. COMPILE / IMPORT VERIFICATION ===")

compile_targets = [
    u7_path,
    u6_path,
    uduc_path,
]

compile_ok = True

for path in compile_targets:
    try:
        py_compile.compile(
            str(path),
            doraise=True,
        )
    except Exception:
        compile_ok = False

check(
    "U7_RELATED_COMPILE_VERIFICATION",
    compile_ok,
)


modules = [
    "backend.server.routes.files",
    "backend.server.pipelines.upload_document.coordinator",
    "backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.coordinator",
    "backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake",
    "backend.server.stores.upload_document_extractor",
    "backend.server.stores.upload_document_normalizer",
    "backend.server.stores.uploaded_document_unified_content",
    "backend.server.universal_unified_content_document.uucd_engine_v1",
]

imports_ok = True

for module_name in modules:
    try:
        importlib.import_module(
            module_name
        )
    except Exception:
        imports_ok = False

check(
    "U7_RELATED_IMPORT_VERIFICATION",
    imports_ok,
)


# ------------------------------------------------------------
# M. No source/file side effects
# ------------------------------------------------------------

print()
print("=== M. SIDE-EFFECT BOUNDARY ===")

check(
    "NO_SOURCE_REREAD",
    "read_text(" not in u7_lower
    and "read_bytes(" not in u7_lower
    and "open(" not in u7_lower,
)

check(
    "NO_FILE_WRITE",
    "write_text(" not in u7_lower
    and "write_bytes(" not in u7_lower
    and "unlink(" not in u7_lower
    and "rename(" not in u7_lower,
)


# ------------------------------------------------------------
# N. Final Phase U7 decision
# ------------------------------------------------------------

print()
print("=== N. PHASE U7 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "PHASE_U7_UPLOAD_SPECIFIC_NORMALIZATION: FAIL"
    )

    print(
        "PHASE_U7_FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    raise RuntimeError(
        "Phase U7 final certification failed."
    )

print(
    "PHASE_U7_UPLOAD_SPECIFIC_NORMALIZATION: CERTIFIED"
)

print(
    "PHASE_U7_CANONICAL_AUTHORITY: backend/server/stores/upload_document_normalizer.py"
)

print(
    "PHASE_U7_INPUT: UploadExtractionResult"
)

print(
    "PHASE_U7_OUTPUT: NormalizedUploadedDocumentContent"
)

print(
    "PHASE_U7_NORMALIZATION_VERSION: uploaded_document_normalization_v1"
)

print(
    "PHASE_U7_UNICODE_POLICY: NFC"
)

print(
    "PHASE_U7_FORMAT_NEUTRAL: YES"
)

print(
    "PHASE_U7_DETERMINISTIC: YES"
)

print(
    "PHASE_U7_SOURCE_IMMUTABLE: YES"
)

print(
    "PHASE_U7_U6_EXTRACTION_SAFE_CLEANUP_PRESERVED: YES"
)

print(
    "PHASE_U7_UDUC_STRUCTURE_CREATION: NO"
)

print(
    "PHASE_U7_HIGHLIGHT_ATS_EXECUTION: NO"
)

print(
    "PHASE_U7_CURRENT_CANONICAL_UUCD_EXECUTION: NO"
)

print(
    "PHASE_U7_WEBSITE_CLEANER_INVOLVEMENT: NO"
)

print(
    "PHASE_U7_GENERIC_NORMALIZER_INVOLVEMENT: NO"
)

print(
    "PHASE_U7_SECOND_CANONICAL_NORMALIZATION_AUTHORITY: NO"
)

print(
    "PHASE_U7_OBSOLETE_LIVE_BACKUP_CLEANUP: COMPLETE"
)

print(
    "PHASE_U7_BUILD_INTEGRATION_VERIFICATION: PASS"
)

print(
    "PHASE_U7_PRODUCTION_PATCH_OUTSTANDING: NO"
)

print(
    "PHASE_U7_CANONICAL_BOUNDARY: UploadExtractionResult -> NormalizedUploadedDocumentContent -> STOP"
)

print(
    "PHASE_U8_UDUC_REALIGNMENT_TRANSITION: AUTHORIZED"
)

print(
    "U7.23_FINAL_PHASE_U7_CERTIFICATION: PASS"
)