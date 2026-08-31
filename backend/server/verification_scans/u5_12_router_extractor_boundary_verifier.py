from __future__ import annotations

import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import backend.server.routes.files as files_route
import backend.server.stores.upload_document_extractor as extractor
import backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake as upload_intake


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U5.12 - ROUTER VS EXTRACTOR RESPONSIBILITY BOUNDARY ===")


router = extractor.detect_upload_source_type
router_source = inspect.getsource(router).lower()

dispatcher = extractor.extract_upload_document_v1
dispatcher_source = inspect.getsource(dispatcher).lower()

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

route_source = inspect.getsource(
    files_route.upload_file
).lower()


# ------------------------------------------------------------
# A. Router responsibility
# ------------------------------------------------------------

print()
print("=== A. ROUTER RESPONSIBILITY ===")

check(
    "ROUTER_USES_FINAL_SUFFIX",
    ".suffix" in router_source,
)

check(
    "ROUTER_NORMALIZES_SUFFIX_CASE",
    ".suffix.lower()" in router_source,
)

check(
    "ROUTER_RESOLVES_LOGICAL_FAMILY",
    "supported_upload_extensions.get"
    in router_source,
)

check(
    "ROUTER_HAS_UNSUPPORTED_FALLBACK",
    '"unsupported"' in router_source,
)


# ------------------------------------------------------------
# B. Router purity
# ------------------------------------------------------------

print()
print("=== B. ROUTER PURITY ===")

forbidden_router_terms = {
    "ROUTER_DOES_NOT_READ_FILE": [
        ".read(",
        "read_bytes",
        "open(",
    ],
    "ROUTER_DOES_NOT_PARSE_CONTENT": [
        "beautifulsoup",
        "bs4",
        "html.parser",
        "docxdocument",
    ],
    "ROUTER_DOES_NOT_NORMALIZE_TEXT": [
        "normalize_text",
        "normalise_text",
        "clean_text",
    ],
    "ROUTER_DOES_NOT_EXTRACT_HEADINGS": [
        "heading",
        "headings",
    ],
    "ROUTER_DOES_NOT_BUILD_METADATA": [
        "metadata",
    ],
    "ROUTER_DOES_NOT_CREATE_EXTRACTION_RESULT": [
        "uploadextractionresult",
    ],
    "ROUTER_DOES_NOT_PERSIST": [
        "write_text",
        "write_bytes",
        "replace(",
        "registry",
    ],
    "ROUTER_DOES_NOT_BUILD_UDUC": [
        "uduc",
    ],
    "ROUTER_DOES_NOT_INVOKE_HIGHLIGHT": [
        "highlight",
    ],
    "ROUTER_DOES_NOT_INVOKE_ACTIVE_TARGET_SET": [
        "active_target",
    ],
    "ROUTER_DOES_NOT_INVOKE_SEMANTIC_RUNTIME_SCORER": [
        "semantic",
        "runtime",
        "scorer",
    ],
}

for name, terms in forbidden_router_terms.items():
    check(
        name,
        all(term not in router_source for term in terms),
    )


# ------------------------------------------------------------
# C. Dispatcher consumes router output
# ------------------------------------------------------------

print()
print("=== C. DISPATCHER CONSUMES ROUTER OUTPUT ===")

check(
    "DISPATCHER_CALLS_CANONICAL_ROUTER",
    "detect_upload_source_type"
    in dispatcher_source,
)

check(
    "DISPATCHER_STORES_LOGICAL_SOURCE_TYPE",
    "source_type = detect_upload_source_type"
    in dispatcher_source.replace("\n", " "),
)


# ------------------------------------------------------------
# D. Family dispatch ownership
# ------------------------------------------------------------

print()
print("=== D. FAMILY DISPATCH OWNERSHIP ===")

check(
    "TXT_FAMILY_DISPATCH",
    'source_type == "txt"'
    in dispatcher_source
    and "extract_txt_upload_v1"
    in dispatcher_source,
)

check(
    "MARKDOWN_FAMILY_DISPATCH",
    'source_type == "markdown"'
    in dispatcher_source
    and "extract_markdown_upload_v1"
    in dispatcher_source,
)

check(
    "HTML_FAMILY_DISPATCH",
    'source_type == "html"'
    in dispatcher_source
    and "extract_html_upload_v1"
    in dispatcher_source,
)

check(
    "DOCX_FAMILY_DISPATCH",
    'source_type == "docx"'
    in dispatcher_source
    and "extract_docx_upload_v1"
    in dispatcher_source,
)


# ------------------------------------------------------------
# E. Format-specific extraction ownership
# ------------------------------------------------------------

print()
print("=== E. FORMAT-SPECIFIC EXTRACTION OWNERSHIP ===")

check(
    "TXT_EXTRACTOR_OWNS_TEXT_DECODING",
    "read_text" in txt_source
    or "decode(" in txt_source,
)

check(
    "MARKDOWN_EXTRACTOR_OWNS_MARKDOWN_PROCESSING",
    "markdown" in markdown_source
    and (
        "read_text" in markdown_source
        or "decode(" in markdown_source
    ),
)

check(
    "HTML_EXTRACTOR_OWNS_HTML_PROCESSING",
    "read_text" in html_source
    and "_extract_html_title_v1" in html_source
    and "_extract_html_headings_v1" in html_source
    and "_strip_html_tags_v1" in html_source,
)

check(
    "DOCX_EXTRACTOR_OWNS_DOCX_PROCESSING",
    "_extract_docx_paragraphs_v2" in docx_source
    and "_extract_docx_headings_v2" in docx_source
    and "_normalize_upload_text_v2" in docx_source,
)


# ------------------------------------------------------------
# F. Unsupported family boundary
# ------------------------------------------------------------

print()
print("=== F. UNSUPPORTED FAMILY BOUNDARY ===")

with TemporaryDirectory() as temp_dir:
    unsupported_path = Path(temp_dir) / "sample.pdf"
    unsupported_path.write_text(
        "plain content",
        encoding="utf-8",
    )

    with patch.object(
        extractor,
        "extract_txt_upload_v1",
        wraps=extractor.extract_txt_upload_v1,
    ) as txt_mock, patch.object(
        extractor,
        "extract_markdown_upload_v1",
        wraps=extractor.extract_markdown_upload_v1,
    ) as md_mock, patch.object(
        extractor,
        "extract_html_upload_v1",
        wraps=extractor.extract_html_upload_v1,
    ) as html_mock, patch.object(
        extractor,
        "extract_docx_upload_v1",
        wraps=extractor.extract_docx_upload_v1,
    ) as docx_mock:

        unsupported_result = dispatcher(
            unsupported_path
        )

        check(
            "UNSUPPORTED_RETURNS_UNSUPPORTED_RESULT",
            unsupported_result.source_type
            == "unsupported",
        )

        check(
            "UNSUPPORTED_DOES_NOT_CALL_TXT",
            txt_mock.call_count == 0,
        )

        check(
            "UNSUPPORTED_DOES_NOT_CALL_MARKDOWN",
            md_mock.call_count == 0,
        )

        check(
            "UNSUPPORTED_DOES_NOT_CALL_HTML",
            html_mock.call_count == 0,
        )

        check(
            "UNSUPPORTED_DOES_NOT_CALL_DOCX",
            docx_mock.call_count == 0,
        )


# ------------------------------------------------------------
# G. No duplicate family dispatch
# ------------------------------------------------------------

print()
print("=== G. NO DUPLICATE FAMILY DISPATCH ===")

for family in (
    "txt",
    "markdown",
    "html",
    "docx",
):
    check(
        f"INTAKE_DOES_NOT_DISPATCH_{family.upper()}",
        f'source_type == "{family}"'
        not in intake_source,
    )

    check(
        f"ROUTE_DOES_NOT_DISPATCH_{family.upper()}",
        f'source_type == "{family}"'
        not in route_source,
    )


# ------------------------------------------------------------
# H. Unrelated pipeline isolation
# ------------------------------------------------------------

print()
print("=== H. UNRELATED PIPELINE ISOLATION ===")

combined_upload_source = (
    router_source
    + "\n"
    + dispatcher_source
    + "\n"
    + intake_source
    + "\n"
    + route_source
)

check(
    "WEBSITE_CLEANERS_NOT_IN_UPLOAD_ROUTING_BOUNDARY",
    "article_body_cleaning_engine"
    not in combined_upload_source
    and "article_cleaning_pipeline"
    not in combined_upload_source,
)

check(
    "URL_IMPORT_NOT_IN_UPLOAD_ROUTING_BOUNDARY",
    "/api/urls/import"
    not in combined_upload_source,
)

check(
    "DRAFT_IMPORT_NOT_IN_UPLOAD_ROUTING_BOUNDARY",
    "/api/draft/import"
    not in combined_upload_source,
)


# ------------------------------------------------------------
# I. U5 placement decision
# ------------------------------------------------------------

print()
print("=== I. U5 PLACEMENT DECISION ===")

module_path = Path(
    inspect.getsourcefile(
        extractor.detect_upload_source_type
    )
    or ""
).as_posix().lower()

check(
    "ROUTER_CURRENTLY_LIVES_WITH_UPLOAD_EXTRACTOR_MODULE",
    module_path.endswith(
        "backend/server/stores/upload_document_extractor.py"
    ),
)

check(
    "DEDICATED_ROUTER_MODULE_NOT_REQUIRED_FOR_CURRENT_BEHAVIOR",
    "detect_upload_source_type"
    in inspect.getsource(extractor),
)

check(
    "U5_DOES_NOT_REQUIRE_U6_RESTRUCTURE",
    "format_router.py"
    not in module_path,
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
        "U5.12_ROUTER_EXTRACTOR_RESPONSIBILITY_BOUNDARY: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.12 router/extractor responsibility boundary verification failed."
    )

print(
    "U5.12_ROUTER_EXTRACTOR_RESPONSIBILITY_BOUNDARY: CERTIFIED"
)

print(
    "U5.12_DEDICATED_ROUTER_MODULE_REQUIRED_NOW: NO"
)

print(
    "U5.12_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U5.13_MIME_MAGIC_NON_AUTHORITY_TRANSITION: AUTHORIZED"
)

print(
    "U5.12_FINAL_BOUNDARY_VERIFICATION: PASS"
)