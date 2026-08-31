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


print("=== U5.7 - HTML ROUTING CONTRACT ===")


router = extractor.detect_upload_source_type

dispatcher_source = inspect.getsource(
    extractor.extract_upload_document_v1
)

html_source = inspect.getsource(
    extractor.extract_html_upload_v1
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
print("=== A. HTML ROUTING MAP ===")

check(
    "HTML_IS_CANONICAL_SUPPORTED_EXTENSION",
    extractor.SUPPORTED_UPLOAD_EXTENSIONS.get(".html")
    == "html",
)

check(
    "HTM_IS_CANONICAL_SUPPORTED_EXTENSION",
    extractor.SUPPORTED_UPLOAD_EXTENSIONS.get(".htm")
    == "html",
)

check(
    "LOWERCASE_HTML_ROUTES_HTML",
    router("document.html") == "html",
)

check(
    "LOWERCASE_HTM_ROUTES_HTML",
    router("document.htm") == "html",
)

check(
    "UPPERCASE_HTML_ROUTES_HTML",
    router("DOCUMENT.HTML") == "html",
)

check(
    "UPPERCASE_HTM_ROUTES_HTML",
    router("DOCUMENT.HTM") == "html",
)

check(
    "MIXED_CASE_HTML_ROUTES_HTML",
    router("document.HtMl") == "html",
)


# ------------------------------------------------------------
# B. Alias convergence and isolation
# ------------------------------------------------------------

print()
print("=== B. HTML ALIAS CONVERGENCE ===")

check(
    "HTML_AND_HTM_CONVERGE",
    router("document.html")
    == router("document.htm")
    == "html",
)

check(
    "HTML_DOES_NOT_ROUTE_TXT",
    router("document.html") != "txt",
)

check(
    "HTML_DOES_NOT_ROUTE_MARKDOWN",
    router("document.html") != "markdown",
)

check(
    "HTML_DOES_NOT_ROUTE_DOCX",
    router("document.html") != "docx",
)


# ------------------------------------------------------------
# C. Determinism
# ------------------------------------------------------------

print()
print("=== C. HTML ROUTING DETERMINISM ===")

html_first = router("document.html")
htm_first = router("document.htm")

check(
    "HTML_ROUTING_DETERMINISTIC",
    all(
        router("document.html") == html_first
        for _ in range(20)
    ),
)

check(
    "HTM_ROUTING_DETERMINISTIC",
    all(
        router("document.htm") == htm_first
        for _ in range(20)
    ),
)


# ------------------------------------------------------------
# D. Dispatcher contract
# ------------------------------------------------------------

print()
print("=== D. HTML DISPATCHER CONTRACT ===")

check(
    "HTML_FAMILY_DISPATCHES_TO_HTML_EXTRACTOR",
    'source_type == "html"' in dispatcher_source
    and "extract_html_upload_v1" in dispatcher_source,
)

html_branch_start = dispatcher_source.find(
    'if source_type == "html":'
)

docx_branch_start = dispatcher_source.find(
    'if source_type == "docx":'
)

html_branch = dispatcher_source[
    html_branch_start:docx_branch_start
]

check(
    "HTML_BRANCH_DOES_NOT_CALL_TXT_EXTRACTOR",
    "extract_txt_upload_v1" not in html_branch,
)

check(
    "HTML_BRANCH_DOES_NOT_CALL_MARKDOWN_EXTRACTOR",
    "extract_markdown_upload_v1" not in html_branch,
)

check(
    "HTML_BRANCH_DOES_NOT_CALL_DOCX_EXTRACTOR",
    "extract_docx_upload_v1" not in html_branch,
)


# ------------------------------------------------------------
# E. HTML extractor defensive extension guard
# ------------------------------------------------------------

print()
print("=== E. HTML EXTRACTOR DEFENSIVE GUARD ===")

check(
    "HTML_EXTRACTOR_ACCEPTS_HTML_AND_HTM",
    'not in {".html", ".htm"}' in html_source,
)

check(
    "HTML_EXTRACTOR_HAS_UNSUPPORTED_EXTENSION_RESULT",
    "unsupported_extension" in html_source,
)


# ------------------------------------------------------------
# F. Direct extractor behavior
# ------------------------------------------------------------

print()
print("=== F. DIRECT HTML EXTRACTOR BEHAVIOR ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    html_path = root / "sample.html"
    html_path.write_text(
        "<html><head><title>Sample</title></head>"
        "<body><h1>Heading</h1><p>Paragraph.</p></body></html>",
        encoding="utf-8",
    )

    html_result = extractor.extract_html_upload_v1(
        html_path
    )

    check(
        "HTML_EXTRACTOR_ACCEPTS_HTML",
        html_result.source_type == "html"
        and html_result.extraction_status != "unsupported_extension",
    )

    htm_path = root / "sample.htm"
    htm_path.write_text(
        "<html><body><h1>Heading</h1><p>Paragraph.</p></body></html>",
        encoding="utf-8",
    )

    htm_result = extractor.extract_html_upload_v1(
        htm_path
    )

    check(
        "HTML_EXTRACTOR_ACCEPTS_HTM",
        htm_result.source_type == "html"
        and htm_result.extraction_status != "unsupported_extension",
    )

    wrong_path = root / "sample.md"
    wrong_path.write_text(
        "# Heading",
        encoding="utf-8",
    )

    wrong_result = extractor.extract_html_upload_v1(
        wrong_path
    )

    check(
        "HTML_EXTRACTOR_REJECTS_NON_HTML",
        wrong_result.extraction_status
        == "unsupported_extension",
    )


# ------------------------------------------------------------
# G. Routing authority isolation
# ------------------------------------------------------------

print()
print("=== G. HTML ROUTING AUTHORITY ISOLATION ===")

check(
    "HTML_ROUTING_DOES_NOT_USE_MIME",
    "mime" not in router_source,
)

check(
    "HTML_ROUTING_DOES_NOT_USE_CONTENT_TYPE",
    "content_type" not in router_source,
)

check(
    "HTML_ROUTING_DOES_NOT_READ_FILE_BYTES",
    ".read(" not in router_source
    and "read_bytes" not in router_source,
)

check(
    "HTML_ROUTING_DOES_NOT_USE_MAGIC",
    "magic" not in router_source,
)

check(
    "HTML_ROUTING_DOES_NOT_USE_SIGNATURE_AUTHORITY",
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
    "FRONTEND_HTM_SESSION_ALIAS_PRESENT",
    'if (value === ".htm") return ".html";'
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
print("=== I. HTML ROUTING SYSTEM ISOLATION ===")

check(
    "NO_WEBSITE_HTML_ROUTING_IN_UPLOAD_CONTRACT",
    "article_body_cleaning_engine" not in module_source
    and "article_cleaning_pipeline" not in module_source
    and "enterprise_raw_html_acquisition_engine" not in module_source
    and "raw_website_html_fetch_runner" not in module_source,
)

check(
    "NO_URL_IMPORT_ROUTING_IN_HTML_CONTRACT",
    "/api/urls/import" not in module_source,
)

check(
    "NO_DRAFT_IMPORT_ROUTING_IN_HTML_CONTRACT",
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
        "U5.7_HTML_ROUTING_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.7 HTML routing contract verification failed."
    )

print(
    "U5.7_HTML_ROUTING_CONTRACT: CERTIFIED"
)

print(
    "U5.7_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U5.8_DOCX_ROUTING_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U5.7_FINAL_HTML_ROUTING_VERIFICATION: PASS"
)