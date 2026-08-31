from __future__ import annotations

import inspect
from pathlib import Path
from tempfile import TemporaryDirectory

import backend.server.routes.files as files_route
import backend.server.stores.upload_document_extractor as extractor


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U5.9 - PHYSICAL ALIAS PRESERVATION ===")


router = extractor.detect_upload_source_type
router_source = inspect.getsource(router).lower()

app_source = Path(
    "frontend/public/assets/js/app.js"
).read_text(
    encoding="utf-8",
    errors="replace",
).lower()

api_source = Path(
    "frontend/public/assets/js/app/api.js"
).read_text(
    encoding="utf-8",
    errors="replace",
).lower()


# ------------------------------------------------------------
# A. Physical extension identity
# ------------------------------------------------------------

print()
print("=== A. PHYSICAL EXTENSION IDENTITY ===")

check(
    "MD_REMAINS_PHYSICAL_MD",
    files_route._guess_ext("document.md") == ".md",
)

check(
    "MARKDOWN_REMAINS_PHYSICAL_MARKDOWN",
    files_route._guess_ext("document.markdown") == ".markdown",
)

check(
    "HTML_REMAINS_PHYSICAL_HTML",
    files_route._guess_ext("document.html") == ".html",
)

check(
    "HTM_REMAINS_PHYSICAL_HTM",
    files_route._guess_ext("document.htm") == ".htm",
)


# ------------------------------------------------------------
# B. Alias collapse only at logical-family output
# ------------------------------------------------------------

print()
print("=== B. LOGICAL FAMILY COLLAPSE ===")

check(
    "MD_ROUTES_MARKDOWN",
    router("document.md") == "markdown",
)

check(
    "MARKDOWN_ROUTES_MARKDOWN",
    router("document.markdown") == "markdown",
)

check(
    "HTML_ROUTES_HTML",
    router("document.html") == "html",
)

check(
    "HTM_ROUTES_HTML",
    router("document.htm") == "html",
)

check(
    "ROUTER_DOES_NOT_REWRITE_PHYSICAL_EXTENSION",
    ".replace(" not in router_source
    and "rename" not in router_source,
)


# ------------------------------------------------------------
# C. Extraction metadata preserves physical extension
# ------------------------------------------------------------

print()
print("=== C. EXTRACTION METADATA PHYSICAL IDENTITY ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    md_path = root / "sample.md"
    md_path.write_text(
        "# Heading\n\nParagraph.",
        encoding="utf-8",
    )
    md_result = extractor.extract_markdown_upload_v1(md_path)

    markdown_path = root / "sample.markdown"
    markdown_path.write_text(
        "# Heading\n\nParagraph.",
        encoding="utf-8",
    )
    markdown_result = extractor.extract_markdown_upload_v1(
        markdown_path
    )

    html_path = root / "sample.html"
    html_path.write_text(
        "<html><body><p>Paragraph.</p></body></html>",
        encoding="utf-8",
    )
    html_result = extractor.extract_html_upload_v1(html_path)

    htm_path = root / "sample.htm"
    htm_path.write_text(
        "<html><body><p>Paragraph.</p></body></html>",
        encoding="utf-8",
    )
    htm_result = extractor.extract_html_upload_v1(htm_path)

    check(
        "MD_METADATA_PRESERVES_DOT_MD",
        md_result.metadata.get("extension") == ".md",
    )

    check(
        "MARKDOWN_METADATA_PRESERVES_DOT_MARKDOWN",
        markdown_result.metadata.get("extension") == ".markdown",
    )

    check(
        "HTML_METADATA_PRESERVES_DOT_HTML",
        html_result.metadata.get("extension") == ".html",
    )

    check(
        "HTM_METADATA_PRESERVES_DOT_HTM",
        htm_result.metadata.get("extension") == ".htm",
    )


# ------------------------------------------------------------
# D. Frontend normalization remains session-only
# ------------------------------------------------------------

print()
print("=== D. FRONTEND SESSION NORMALIZATION ONLY ===")

check(
    "FRONTEND_MARKDOWN_SESSION_ALIAS_PRESENT",
    'if (value === ".markdown") return ".md";'
    in app_source,
)

check(
    "FRONTEND_HTM_SESSION_ALIAS_PRESENT",
    'if (value === ".htm") return ".html";'
    in app_source,
)

check(
    "FRONTEND_SENDS_ORIGINAL_FILE_OBJECT",
    'fd.append("file", file);'
    in api_source,
)

check(
    "BACKEND_ROUTER_INDEPENDENT_OF_SESSION_ALIAS",
    "canonicalsessionformat" not in router_source,
)


# ------------------------------------------------------------
# E. Final-suffix rules remain authoritative
# ------------------------------------------------------------

print()
print("=== E. FINAL-SUFFIX AUTHORITY ===")

check(
    "MARKDOWN_EXE_IS_UNSUPPORTED",
    router("document.markdown.exe") == "unsupported",
)

check(
    "HTM_ZIP_IS_UNSUPPORTED",
    router("document.htm.zip") == "unsupported",
)

check(
    "MD_PDF_IS_UNSUPPORTED",
    router("document.md.pdf") == "unsupported",
)

check(
    "HTML_EXE_IS_UNSUPPORTED",
    router("document.html.exe") == "unsupported",
)


# ------------------------------------------------------------
# F. Canonical alias mapping remains singular
# ------------------------------------------------------------

print()
print("=== F. ALIAS MAP SINGULARITY ===")

expected_map = {
    ".txt": "txt",
    ".md": "markdown",
    ".markdown": "markdown",
    ".html": "html",
    ".htm": "html",
    ".docx": "docx",
}

check(
    "CANONICAL_ALIAS_MAP_EXACT",
    extractor.SUPPORTED_UPLOAD_EXTENSIONS == expected_map,
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
        "U5.9_PHYSICAL_ALIAS_PRESERVATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.9 physical alias preservation verification failed."
    )

print(
    "U5.9_PHYSICAL_ALIAS_PRESERVATION: CERTIFIED"
)

print(
    "U5.9_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U5.10_ROUTER_ORDERING_TRANSITION: AUTHORIZED"
)

print(
    "U5.9_FINAL_ALIAS_PRESERVATION_VERIFICATION: PASS"
)