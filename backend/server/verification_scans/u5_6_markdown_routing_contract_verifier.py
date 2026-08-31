from __future__ import annotations

import inspect
from pathlib import Path
from tempfile import TemporaryDirectory

import backend.server.stores.upload_document_extractor as extractor


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U5.6 - MARKDOWN ROUTING CONTRACT ===")


router = extractor.detect_upload_source_type

dispatcher_source = inspect.getsource(
    extractor.extract_upload_document_v1
)

markdown_source = inspect.getsource(
    extractor.extract_markdown_upload_v1
).lower()

router_source = inspect.getsource(
    extractor.detect_upload_source_type
).lower()

module_source = inspect.getsource(
    extractor
).lower()


# ------------------------------------------------------------
# A. Physical extension -> logical family
# ------------------------------------------------------------

print()
print("=== A. MARKDOWN ROUTING MAP ===")

check(
    "MD_IS_CANONICAL_SUPPORTED_EXTENSION",
    extractor.SUPPORTED_UPLOAD_EXTENSIONS.get(".md")
    == "markdown",
)

check(
    "MARKDOWN_IS_CANONICAL_SUPPORTED_EXTENSION",
    extractor.SUPPORTED_UPLOAD_EXTENSIONS.get(".markdown")
    == "markdown",
)

check(
    "LOWERCASE_MD_ROUTES_MARKDOWN",
    router("document.md") == "markdown",
)

check(
    "LOWERCASE_MARKDOWN_ROUTES_MARKDOWN",
    router("document.markdown") == "markdown",
)

check(
    "UPPERCASE_MD_ROUTES_MARKDOWN",
    router("DOCUMENT.MD") == "markdown",
)

check(
    "UPPERCASE_MARKDOWN_ROUTES_MARKDOWN",
    router("DOCUMENT.MARKDOWN") == "markdown",
)

check(
    "MIXED_CASE_MARKDOWN_ROUTES_MARKDOWN",
    router("document.MarkDown") == "markdown",
)


# ------------------------------------------------------------
# B. Alias convergence and isolation
# ------------------------------------------------------------

print()
print("=== B. MARKDOWN ALIAS CONVERGENCE ===")

check(
    "MD_AND_MARKDOWN_CONVERGE",
    router("document.md")
    == router("document.markdown")
    == "markdown",
)

check(
    "MARKDOWN_DOES_NOT_ROUTE_TXT",
    router("document.md") != "txt",
)

check(
    "MARKDOWN_DOES_NOT_ROUTE_HTML",
    router("document.md") != "html",
)

check(
    "MARKDOWN_DOES_NOT_ROUTE_DOCX",
    router("document.md") != "docx",
)


# ------------------------------------------------------------
# C. Determinism
# ------------------------------------------------------------

print()
print("=== C. MARKDOWN ROUTING DETERMINISM ===")

md_first = router("document.md")
markdown_first = router("document.markdown")

check(
    "MD_ROUTING_DETERMINISTIC",
    all(
        router("document.md") == md_first
        for _ in range(20)
    ),
)

check(
    "MARKDOWN_ROUTING_DETERMINISTIC",
    all(
        router("document.markdown") == markdown_first
        for _ in range(20)
    ),
)


# ------------------------------------------------------------
# D. Dispatcher contract
# ------------------------------------------------------------

print()
print("=== D. MARKDOWN DISPATCHER CONTRACT ===")

check(
    "MARKDOWN_FAMILY_DISPATCHES_TO_MARKDOWN_EXTRACTOR",
    'source_type == "markdown"' in dispatcher_source
    and "extract_markdown_upload_v1" in dispatcher_source,
)

markdown_branch_start = dispatcher_source.find(
    'if source_type == "markdown":'
)

html_branch_start = dispatcher_source.find(
    'if source_type == "html":'
)

markdown_branch = dispatcher_source[
    markdown_branch_start:html_branch_start
]

check(
    "MARKDOWN_BRANCH_DOES_NOT_CALL_TXT_EXTRACTOR",
    "extract_txt_upload_v1" not in markdown_branch,
)

check(
    "MARKDOWN_BRANCH_DOES_NOT_CALL_HTML_EXTRACTOR",
    "extract_html_upload_v1" not in markdown_branch,
)

check(
    "MARKDOWN_BRANCH_DOES_NOT_CALL_DOCX_EXTRACTOR",
    "extract_docx_upload_v1" not in markdown_branch,
)


# ------------------------------------------------------------
# E. Markdown extractor defensive extension guard
# ------------------------------------------------------------

print()
print("=== E. MARKDOWN EXTRACTOR DEFENSIVE GUARD ===")

check(
    "MARKDOWN_EXTRACTOR_ACCEPTS_MD_AND_MARKDOWN",
    'not in {".md", ".markdown"}' in markdown_source,
)

check(
    "MARKDOWN_EXTRACTOR_HAS_UNSUPPORTED_EXTENSION_RESULT",
    "unsupported_extension" in markdown_source,
)


# ------------------------------------------------------------
# F. Direct extractor behavior
# ------------------------------------------------------------

print()
print("=== F. DIRECT MARKDOWN EXTRACTOR BEHAVIOR ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    md_path = root / "sample.md"
    md_path.write_text(
        "# Heading\n\nParagraph.",
        encoding="utf-8",
    )

    md_result = extractor.extract_markdown_upload_v1(
        md_path
    )

    check(
        "MARKDOWN_EXTRACTOR_ACCEPTS_MD",
        md_result.source_type == "markdown"
        and md_result.extraction_status != "unsupported_extension",
    )

    markdown_path = root / "sample.markdown"
    markdown_path.write_text(
        "# Heading\n\nParagraph.",
        encoding="utf-8",
    )

    markdown_result = extractor.extract_markdown_upload_v1(
        markdown_path
    )

    check(
        "MARKDOWN_EXTRACTOR_ACCEPTS_MARKDOWN",
        markdown_result.source_type == "markdown"
        and markdown_result.extraction_status != "unsupported_extension",
    )

    wrong_path = root / "sample.txt"
    wrong_path.write_text(
        "Plain text",
        encoding="utf-8",
    )

    wrong_result = extractor.extract_markdown_upload_v1(
        wrong_path
    )

    check(
        "MARKDOWN_EXTRACTOR_REJECTS_NON_MARKDOWN",
        wrong_result.extraction_status
        == "unsupported_extension",
    )


# ------------------------------------------------------------
# G. Routing authority isolation
# ------------------------------------------------------------

print()
print("=== G. MARKDOWN ROUTING AUTHORITY ISOLATION ===")

check(
    "MARKDOWN_ROUTING_DOES_NOT_USE_MIME",
    "mime" not in router_source,
)

check(
    "MARKDOWN_ROUTING_DOES_NOT_USE_CONTENT_TYPE",
    "content_type" not in router_source,
)

check(
    "MARKDOWN_ROUTING_DOES_NOT_READ_FILE_BYTES",
    ".read(" not in router_source
    and "read_bytes" not in router_source,
)

check(
    "MARKDOWN_ROUTING_DOES_NOT_USE_MAGIC",
    "magic" not in router_source,
)

check(
    "MARKDOWN_ROUTING_DOES_NOT_USE_SIGNATURE_AUTHORITY",
    "file_signature" not in router_source
    and "content_signature" not in router_source
    and "signature_bytes" not in router_source
    and "detect_signature" not in router_source,
)


# ------------------------------------------------------------
# H. Frontend normalization is not backend authority
# ------------------------------------------------------------

print()
print("=== H. FRONTEND / BACKEND SEPARATION ===")

app_source = Path(
    "frontend/public/assets/js/app.js"
).read_text(
    encoding="utf-8",
    errors="replace",
).lower()

check(
    "FRONTEND_MARKDOWN_SESSION_ALIAS_PRESENT",
    'if (value === ".markdown") return ".md";'
    in app_source,
)

check(
    "BACKEND_ROUTER_INDEPENDENT_OF_SESSION_NORMALIZATION",
    "canonicalsessionformat" not in router_source,
)


# ------------------------------------------------------------
# I. Unrelated-system isolation
# ------------------------------------------------------------

print()
print("=== I. MARKDOWN ROUTING SYSTEM ISOLATION ===")

check(
    "NO_WEBSITE_ROUTING_IN_MARKDOWN_CONTRACT",
    "article_body_cleaning_engine" not in module_source
    and "article_cleaning_pipeline" not in module_source,
)

check(
    "NO_URL_IMPORT_ROUTING_IN_MARKDOWN_CONTRACT",
    "/api/urls/import" not in module_source,
)

check(
    "NO_DRAFT_IMPORT_ROUTING_IN_MARKDOWN_CONTRACT",
    "/api/draft/import" not in module_source,
)

check(
    "NO_UDUC_IN_ROUTER_FUNCTION",
    "uduc" not in router_source,
)

check(
    "NO_HIGHLIGHT_IN_ROUTER_FUNCTION",
    "highlight" not in router_source,
)

check(
    "NO_ACTIVE_TARGET_SET_IN_ROUTER_FUNCTION",
    "active_target" not in router_source,
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
        "U5.6_MARKDOWN_ROUTING_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.6 Markdown routing contract verification failed."
    )

print(
    "U5.6_MARKDOWN_ROUTING_CONTRACT: CERTIFIED"
)

print(
    "U5.6_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U5.7_HTML_ROUTING_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U5.6_FINAL_MARKDOWN_ROUTING_VERIFICATION: PASS"
)