from __future__ import annotations

import inspect
from pathlib import Path

import backend.server.routes.files as files_route
import backend.server.stores.upload_document_extractor as extractor
import backend.server.stores.uploaded_document_unified_content as uduc_store


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U4.5 - ALIAS DETECTION CONTRACT ===")


# ------------------------------------------------------------
# A. Canonical physical aliases
# ------------------------------------------------------------

print()
print("=== A. CANONICAL PHYSICAL ALIASES ===")

expected = {
    ".txt",
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".docx",
}

check(
    "CANONICAL_SIX_FORMAT_SET_PRESENT",
    set(files_route.ALLOWED_EXT) == expected,
)

check(
    "MARKDOWN_MD_PRESENT",
    ".md" in files_route.ALLOWED_EXT,
)

check(
    "MARKDOWN_MARKDOWN_PRESENT",
    ".markdown" in files_route.ALLOWED_EXT,
)

check(
    "HTML_HTML_PRESENT",
    ".html" in files_route.ALLOWED_EXT,
)

check(
    "HTML_HTM_PRESENT",
    ".htm" in files_route.ALLOWED_EXT,
)

check(
    "TXT_NON_ALIAS_PRESENT",
    ".txt" in files_route.ALLOWED_EXT,
)

check(
    "DOCX_NON_ALIAS_PRESENT",
    ".docx" in files_route.ALLOWED_EXT,
)


# ------------------------------------------------------------
# B. Physical alias preservation
# ------------------------------------------------------------

print()
print("=== B. PHYSICAL ALIAS PRESERVATION ===")

check(
    "DETECT_MD_AS_MD",
    files_route._guess_ext("article.md") == ".md",
)

check(
    "DETECT_MARKDOWN_AS_MARKDOWN",
    files_route._guess_ext("article.markdown") == ".markdown",
)

check(
    "DETECT_HTML_AS_HTML",
    files_route._guess_ext("article.html") == ".html",
)

check(
    "DETECT_HTM_AS_HTM",
    files_route._guess_ext("article.htm") == ".htm",
)

check(
    "DETECTOR_DOES_NOT_COLLAPSE_MARKDOWN_ALIAS",
    files_route._guess_ext("article.markdown") != ".md",
)

check(
    "DETECTOR_DOES_NOT_COLLAPSE_HTM_ALIAS",
    files_route._guess_ext("article.htm") != ".html",
)


# ------------------------------------------------------------
# C. Extractor alias contract
# ------------------------------------------------------------

print()
print("=== C. EXTRACTOR ALIAS CONTRACT ===")

extractor_map = dict(
    extractor.SUPPORTED_UPLOAD_EXTENSIONS
)

check(
    "EXTRACTOR_SET_MATCHES_ROUTE_SET",
    set(extractor_map.keys()) == expected,
)

check(
    "MD_AND_MARKDOWN_SHARE_EXTRACTION_FAMILY",
    extractor_map[".md"] == extractor_map[".markdown"],
)

check(
    "HTML_AND_HTM_SHARE_EXTRACTION_FAMILY",
    extractor_map[".html"] == extractor_map[".htm"],
)

check(
    "TXT_NOT_MARKDOWN_ALIAS_FAMILY",
    extractor_map[".txt"] != extractor_map[".md"],
)

check(
    "TXT_NOT_HTML_ALIAS_FAMILY",
    extractor_map[".txt"] != extractor_map[".html"],
)

check(
    "DOCX_NOT_MARKDOWN_ALIAS_FAMILY",
    extractor_map[".docx"] != extractor_map[".md"],
)

check(
    "DOCX_NOT_HTML_ALIAS_FAMILY",
    extractor_map[".docx"] != extractor_map[".html"],
)


# ------------------------------------------------------------
# D. Alias handling remains detection-only at route boundary
# ------------------------------------------------------------

print()
print("=== D. DETECTION-ONLY RESPONSIBILITY ===")

guess_source = inspect.getsource(
    files_route._guess_ext
)

for forbidden in [
    "extract",
    "normalize",
    "format_router",
    "route_format",
    "dispatch",
    "write_bytes",
    "write_text",
    "build_uduc",
]:
    check(
        "DETECTOR_NO_"
        + forbidden.replace("_", "").upper(),
        forbidden.lower() not in guess_source.lower(),
    )


# ------------------------------------------------------------
# E. Frontend session-family collapse
# ------------------------------------------------------------

print()
print("=== E. FRONTEND SESSION ALIAS CONTRACT ===")

frontend_source = Path(
    "frontend/public/assets/js/app.js"
).read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "FRONTEND_ACCEPTS_ALL_SIX_PHYSICAL_FORMATS",
    '".docx,.md,.markdown,.html,.htm,.txt"'
    in frontend_source,
)

check(
    "FRONTEND_MARKDOWN_TO_MD_SESSION_ALIAS",
    'if (value === ".markdown") return ".md";'
    in frontend_source,
)

check(
    "FRONTEND_HTM_TO_HTML_SESSION_ALIAS",
    'if (value === ".htm") return ".html";'
    in frontend_source,
)

route_source = Path(
    files_route.__file__
).read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "BACKEND_DETECTOR_HAS_NO_FRONTEND_SESSION_COLLAPSE",
    "canonicalSessionFormat" not in route_source,
)


# ------------------------------------------------------------
# F. Backend metadata preservation
# ------------------------------------------------------------

print()
print("=== F. BACKEND METADATA PRESERVATION ===")

extractor_source = Path(
    extractor.__file__
).read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "EXTRACTOR_METADATA_RECORDS_PHYSICAL_EXTENSION",
    '"extension": p.suffix.lower()'
    in extractor_source,
)

uduc_source = Path(
    uduc_store.__file__
).read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "UDUC_EXTENSION_METADATA_FALLBACK_PRESENT",
    "Path(original_name).suffix.lower()"
    in uduc_source,
)


# ------------------------------------------------------------
# G. Alias behavior does not expand contract
# ------------------------------------------------------------

print()
print("=== G. NO FORMAT CONTRACT EXPANSION ===")

check(
    "ROUTE_STILL_EXACTLY_SIX_FORMATS",
    len(files_route.ALLOWED_EXT) == 6
    and set(files_route.ALLOWED_EXT) == expected,
)

check(
    "EXTRACTOR_STILL_EXACTLY_SIX_FORMATS",
    len(extractor_map) == 6
    and set(extractor_map.keys()) == expected,
)


# ------------------------------------------------------------
# H. Case behavior on aliases
# ------------------------------------------------------------

print()
print("=== H. ALIAS CASE NORMALIZATION ===")

alias_case_samples = {
    "ARTICLE.MD": ".md",
    "ARTICLE.MARKDOWN": ".markdown",
    "ARTICLE.HTML": ".html",
    "ARTICLE.HTM": ".htm",
    "article.MarkDown": ".markdown",
    "article.HtM": ".htm",
}

for filename, expected_ext in alias_case_samples.items():
    label = (
        filename
        .replace(".", "_")
        .upper()
    )

    check(
        f"ALIAS_CASE_{label}",
        files_route._guess_ext(filename)
        == expected_ext,
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
        "U4.5_ALIAS_DETECTION_CONTRACT_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U4.5 alias detection contract verification failed."
    )

print(
    "U4.5_ALIAS_DETECTION_CONTRACT_VERIFICATION: PASS"
)