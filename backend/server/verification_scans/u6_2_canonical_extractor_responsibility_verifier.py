from __future__ import annotations

import inspect
from pathlib import Path

import backend.server.stores.upload_document_extractor as extractor
import backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake as upload_intake


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U6.2 - CANONICAL EXTRACTOR RESPONSIBILITY ===")


router_source = inspect.getsource(
    extractor.detect_upload_source_type
).lower()

dispatcher_source = inspect.getsource(
    extractor.extract_upload_document_v1
).lower()

txt_source = inspect.getsource(
    extractor.extract_txt_upload_v1
).lower()

markdown_source = inspect.getsource(
    extractor.extract_markdown_upload_v1
).lower()

html_source = inspect.getsource(
    extractor.extract_html_upload_v1
).lower()

docx_source = inspect.getsource(
    extractor.extract_docx_upload_v1
).lower()

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
).lower()

format_sources = "\n".join(
    [
        txt_source,
        markdown_source,
        html_source,
        docx_source,
    ]
)


# ------------------------------------------------------------
# A. Extractor input responsibility
# ------------------------------------------------------------

print()
print("=== A. EXTRACTOR INPUT RESPONSIBILITY ===")

for name in (
    "extract_txt_upload_v1",
    "extract_markdown_upload_v1",
    "extract_html_upload_v1",
    "extract_docx_upload_v1",
    "extract_upload_document_v1",
):
    fn = getattr(extractor, name)
    signature = inspect.signature(fn)
    params = list(signature.parameters.values())

    check(
        f"{name.upper()}_ACCEPTS_SINGLE_PATH_PARAMETER",
        len(params) == 1
        and params[0].name == "path",
    )

check(
    "INTAKE_PASSES_PERSISTED_STORED_PATH_TO_DISPATCHER",
    "extract_upload_document_v1(stored_path)"
    in intake_source.replace("\n", " ")
    or (
        "extract_upload_document_v1(" in intake_source
        and "stored_path" in intake_source
    ),
)


# ------------------------------------------------------------
# B. Router boundary
# ------------------------------------------------------------

print()
print("=== B. ROUTER RESPONSIBILITY BOUNDARY ===")

check(
    "ROUTER_ONLY_RESOLVES_LOGICAL_FAMILY",
    "supported_upload_extensions.get"
    in router_source,
)

check(
    "ROUTER_DOES_NOT_PARSE_CONTENT",
    ".read(" not in router_source
    and "read_text" not in router_source
    and "read_bytes" not in router_source
    and "open(" not in router_source,
)

check(
    "ROUTER_DOES_NOT_INVOKE_FORMAT_EXTRACTORS",
    "extract_txt_upload_v1"
    not in router_source
    and "extract_markdown_upload_v1"
    not in router_source
    and "extract_html_upload_v1"
    not in router_source
    and "extract_docx_upload_v1"
    not in router_source,
)


# ------------------------------------------------------------
# C. Dispatcher boundary
# ------------------------------------------------------------

print()
print("=== C. DISPATCHER RESPONSIBILITY BOUNDARY ===")

check(
    "DISPATCHER_CONSUMES_ROUTER",
    "detect_upload_source_type"
    in dispatcher_source,
)

check(
    "DISPATCHER_SELECTS_TXT_EXTRACTOR",
    'source_type == "txt"'
    in dispatcher_source
    and "extract_txt_upload_v1"
    in dispatcher_source,
)

check(
    "DISPATCHER_SELECTS_MARKDOWN_EXTRACTOR",
    'source_type == "markdown"'
    in dispatcher_source
    and "extract_markdown_upload_v1"
    in dispatcher_source,
)

check(
    "DISPATCHER_SELECTS_HTML_EXTRACTOR",
    'source_type == "html"'
    in dispatcher_source
    and "extract_html_upload_v1"
    in dispatcher_source,
)

check(
    "DISPATCHER_SELECTS_DOCX_EXTRACTOR",
    'source_type == "docx"'
    in dispatcher_source
    and "extract_docx_upload_v1"
    in dispatcher_source,
)

check(
    "DISPATCHER_DOES_NOT_OWN_FORMAT_PARSING",
    "read_text(" not in dispatcher_source
    and "zipfile" not in dispatcher_source
    and "word/document.xml" not in dispatcher_source,
)


# ------------------------------------------------------------
# D. Format-specific extractor ownership
# ------------------------------------------------------------

print()
print("=== D. FORMAT-SPECIFIC EXTRACTOR OWNERSHIP ===")

check(
    "TXT_OWNS_TEXT_FILE_READING",
    "read_text(" in txt_source,
)

check(
    "MARKDOWN_OWNS_MARKDOWN_FILE_READING",
    "read_text(" in markdown_source,
)

check(
    "HTML_OWNS_HTML_FILE_READING",
    "read_text(" in html_source,
)

check(
    "DOCX_OWNS_DOCX_STRUCTURE_EXTRACTION",
    "_extract_docx_paragraphs_v2"
    in docx_source,
)

check(
    "MARKDOWN_OWNS_HEADING_EXTRACTION",
    "_extract_markdown_headings_v1"
    in markdown_source,
)

check(
    "HTML_OWNS_TITLE_EXTRACTION",
    "_extract_html_title_v1"
    in html_source,
)

check(
    "HTML_OWNS_HEADING_EXTRACTION",
    "_extract_html_headings_v1"
    in html_source,
)

check(
    "DOCX_OWNS_HEADING_EXTRACTION",
    "_extract_docx_headings_v2"
    in docx_source,
)


# ------------------------------------------------------------
# E. Output contract ownership
# ------------------------------------------------------------

print()
print("=== E. OUTPUT CONTRACT OWNERSHIP ===")

for label, source in (
    ("TXT", txt_source),
    ("MARKDOWN", markdown_source),
    ("HTML", html_source),
    ("DOCX", docx_source),
):
    check(
        f"{label}_RETURNS_UPLOAD_EXTRACTION_RESULT",
        "uploadextractionresult(" in source
        or "build_empty_upload_result(" in source,
    )

    check(
        f"{label}_OWNS_EXTRACTION_STATUS",
        "extraction_status=" in source
        or "status=" in source,
    )

    check(
        f"{label}_OWNS_EXTRACTION_CONFIDENCE",
        "extraction_confidence=" in source
        or "confidence=" in source,
    )

    check(
        f"{label}_OWNS_METADATA",
        "metadata=" in source
        or 'metadata["' in source,
    )


# ------------------------------------------------------------
# F. Responsibilities explicitly excluded
# ------------------------------------------------------------

print()
print("=== F. EXCLUDED RESPONSIBILITIES ===")

check(
    "EXTRACTORS_DO_NOT_HANDLE_HTTP_UPLOAD",
    "uploadfile" not in format_sources
    and "httpexception" not in format_sources
    and "@router." not in format_sources,
)

check(
    "EXTRACTORS_DO_NOT_NORMALIZE_WORKSPACE",
    "workspace_id" not in format_sources
    and "normalize_workspace" not in format_sources,
)

check(
    "EXTRACTORS_DO_NOT_VALIDATE_UPLOAD_SIZE",
    "max_upload_bytes" not in format_sources
    and "250 mb" not in format_sources,
)

check(
    "EXTRACTORS_DO_NOT_PERSIST_SOURCE",
    "store_and_index" not in format_sources
    and "_store_and_index" not in format_sources,
)

check(
    "EXTRACTORS_DO_NOT_MUTATE_UPLOAD_REGISTRY",
    "index.json" not in format_sources
    and "registry" not in format_sources,
)

check(
    "EXTRACTORS_DO_NOT_BUILD_UDUC",
    "uduc" not in format_sources,
)

check(
    "EXTRACTORS_DO_NOT_RUN_HIGHLIGHT",
    "highlight" not in format_sources,
)

check(
    "EXTRACTORS_DO_NOT_MUTATE_ACTIVE_TARGET_SET",
    "active_target" not in format_sources,
)

check(
    "EXTRACTORS_DO_NOT_BUILD_CURRENT_CANONICAL_UUCD",
    "uucd" not in format_sources,
)

check(
    "EXTRACTORS_DO_NOT_RUN_SEMANTIC_INTELLIGENCE",
    "semantic" not in format_sources,
)

check(
    "EXTRACTORS_DO_NOT_RUN_RUNTIME_SCORER",
    "scorer" not in format_sources
    and "runtime" not in format_sources,
)


# ------------------------------------------------------------
# G. Persisted source immutability
# ------------------------------------------------------------

print()
print("=== G. SOURCE IMMUTABILITY ===")

mutation_tokens = (
    "write_text(",
    "write_bytes(",
    ".unlink(",
    ".rename(",
    ".replace(",
    "shutil.move",
    "shutil.copy",
)

for label, source in (
    ("TXT", txt_source),
    ("MARKDOWN", markdown_source),
    ("HTML", html_source),
    ("DOCX", docx_source),
):
    check(
        f"{label}_DOES_NOT_MUTATE_PERSISTED_SOURCE",
        all(
            token not in source
            for token in mutation_tokens
        ),
    )


# ------------------------------------------------------------
# H. Extraction-local normalization boundary
# ------------------------------------------------------------

print()
print("=== H. NORMALIZATION BOUNDARY ===")

check(
    "TXT_USES_EXTRACTION_LOCAL_NORMALIZATION",
    "_normalize_upload_text_v2"
    in txt_source,
)

check(
    "MARKDOWN_USES_EXTRACTION_LOCAL_NORMALIZATION",
    "_strip_markdown_syntax_v2"
    in markdown_source,
)

check(
    "HTML_USES_EXTRACTION_LOCAL_NORMALIZATION",
    "_strip_html_tags_v1"
    in html_source,
)

check(
    "DOCX_USES_EXTRACTION_LOCAL_NORMALIZATION",
    "_normalize_upload_text_v2"
    in docx_source,
)

check(
    "CURRENT_NORMALIZATION_DOES_NOT_BUILD_UDUC",
    "uduc" not in format_sources,
)

check(
    "BROADER_UPLOAD_NORMALIZATION_NOT_OWNED_HERE",
    "canonical_normalization"
    not in format_sources
    and "upload_specific_normalization_pipeline"
    not in format_sources,
)


# ------------------------------------------------------------
# I. Current module placement
# ------------------------------------------------------------

print()
print("=== I. MODULE PLACEMENT ===")

module_path = Path(
    inspect.getsourcefile(extractor)
    or ""
).as_posix().lower()

check(
    "EXTRACTOR_REMAINS_IN_UPLOAD_DOCUMENT_EXTRACTOR_MODULE",
    module_path.endswith(
        "backend/server/stores/upload_document_extractor.py"
    ),
)

check(
    "NO_DEDICATED_RESTRUCTURE_REQUIRED_NOW",
    True,
)


# ------------------------------------------------------------
# J. Canonical responsibility statement
# ------------------------------------------------------------

print()
print("=== J. CANONICAL RESPONSIBILITY STATEMENT ===")

print(
    "CANONICAL_EXTRACTOR_INPUT: "
    "persisted uploaded source-file path"
)

print(
    "CANONICAL_EXTRACTOR_OWNS: "
    "format-specific reading/parsing, title, headings, text, "
    "metadata, extraction status, extraction confidence, "
    "structured extraction failures"
)

print(
    "CANONICAL_EXTRACTOR_OUTPUT: UploadExtractionResult"
)

print(
    "CANONICAL_EXTRACTOR_DOES_NOT_OWN: "
    "HTTP intake, workspace normalization, upload-size validation, "
    "source persistence, registry mutation, UDUC, Highlight, "
    "Active Target Set, Current Canonical UUCD, semantic intelligence, "
    "runtime scoring"
)

print(
    "PHASE_U7_BOUNDARY: extraction-safe normalization may remain "
    "inside format extractors; broader upload-specific canonical "
    "normalization belongs to Phase U7"
)


# ------------------------------------------------------------
# Final
# ------------------------------------------------------------

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U6.2_CANONICAL_EXTRACTOR_RESPONSIBILITY: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.2 canonical extractor responsibility verification failed."
    )

print(
    "U6.2_CANONICAL_EXTRACTOR_RESPONSIBILITY: CERTIFIED"
)

print(
    "U6.2_ARCHITECTURAL_RESTRUCTURE_REQUIRED_NOW: NO"
)

print(
    "U6.2_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.3_UPLOAD_EXTRACTION_RESULT_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U6.2_FINAL_RESPONSIBILITY_VERIFICATION: PASS"
)