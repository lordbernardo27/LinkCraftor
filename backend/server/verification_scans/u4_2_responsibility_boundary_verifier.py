from __future__ import annotations

import inspect
from pathlib import Path

import backend.server.routes.files as files_route

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline import (
    upload_intake,
)

import backend.server.stores.upload_document_extractor as extractor
import backend.server.stores.uploaded_document_unified_content as uduc_store


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print(
    "=== U4.2 STEP 1 — CANONICAL RESPONSIBILITY BOUNDARY ==="
)


# ------------------------------------------------------------
# A. Canonical physical detector
# ------------------------------------------------------------

print()
print("=== A. PHYSICAL FORMAT DETECTOR ===")

guess_source = inspect.getsource(
    files_route._guess_ext
)

check(
    "GUESS_EXT_EXISTS",
    callable(files_route._guess_ext),
)

check(
    "GUESS_EXT_USES_SAFE_FILENAME",
    "_safe_upload_filename"
    in guess_source,
)

check(
    "GUESS_EXT_USES_FILENAME_SUFFIX",
    ".suffix"
    in guess_source,
)

check(
    "GUESS_EXT_NORMALIZES_CASE",
    ".lower()"
    in guess_source,
)

for forbidden in [
    "content_type",
    "mimetype",
    "magic",
    "extract_",
    "write_",
    "UDUC",
    "highlight",
    "semantic",
    "scorer",
]:
    check(
        "GUESS_EXT_NO_"
        + forbidden.replace("_", "").upper(),
        forbidden.lower()
        not in guess_source.lower(),
    )


# ------------------------------------------------------------
# B. Supported-format acceptance gate
# ------------------------------------------------------------

print()
print("=== B. ACCEPTANCE GATE ===")

expected_extensions = {
    ".txt",
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".docx",
}

check(
    "ROUTE_ALLOWED_EXT_EXACT",
    set(files_route.ALLOWED_EXT)
    == expected_extensions,
)

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
)

check(
    "INTAKE_CALLS_GUESS_EXTENSION",
    "guess_extension("
    in intake_source,
)

check(
    "INTAKE_CHECKS_ALLOWED_EXTENSIONS",
    "allowed_extensions"
    in intake_source,
)

check(
    "INTAKE_REJECTS_UNSUPPORTED_EXTENSION",
    "extension not in allowed_extensions"
    in intake_source,
)


# ------------------------------------------------------------
# C. Format routing remains separate
# ------------------------------------------------------------

print()
print("=== C. FORMAT ROUTER SEPARATION ===")

combined_detection_surface = (
    guess_source
    + "\n"
    + intake_source
)

router_terms = [
    "format_router",
    "route_format",
    "dispatch_format",
    "extract_docx",
    "extract_markdown",
    "extract_html",
    "extract_txt",
]

check(
    "NO_FORMAT_ROUTER_IMPLEMENTED_IN_DETECTOR",
    all(
        term.lower()
        not in combined_detection_surface.lower()
        for term in router_terms
    ),
)


# ------------------------------------------------------------
# D. Extractor responsibility
# ------------------------------------------------------------

print()
print("=== D. EXTRACTOR RESPONSIBILITY ===")

extractor_source = Path(
    extractor.__file__
).read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "EXTRACTOR_SUPPORTED_EXTENSION_MAP_PRESENT",
    "SUPPORTED_UPLOAD_EXTENSIONS"
    in extractor_source,
)

check(
    "EXTRACTOR_USES_PERSISTED_PATH_SUFFIX",
    "p.suffix.lower()"
    in extractor_source,
)

check(
    "EXTRACTOR_EXTENSION_MAP_EXACT",
    set(
        extractor.SUPPORTED_UPLOAD_EXTENSIONS.keys()
    )
    == expected_extensions,
)

check(
    "EXTRACTOR_DOES_NOT_DEFINE_UPLOAD_ACCEPTANCE_ROUTE",
    "/api/files/upload"
    not in extractor_source,
)


# ------------------------------------------------------------
# E. Alias preservation
# ------------------------------------------------------------

print()
print("=== E. PHYSICAL ALIAS PRESERVATION ===")

check(
    "MARKDOWN_PHYSICAL_ALIAS_PRESERVED",
    files_route._guess_ext(
        "example.markdown"
    )
    == ".markdown",
)

check(
    "HTM_PHYSICAL_ALIAS_PRESERVED",
    files_route._guess_ext(
        "example.htm"
    )
    == ".htm",
)

check(
    "MARKDOWN_NOT_COLLAPSED_TO_MD_BY_DETECTOR",
    files_route._guess_ext(
        "example.markdown"
    )
    != ".md",
)

check(
    "HTM_NOT_COLLAPSED_TO_HTML_BY_DETECTOR",
    files_route._guess_ext(
        "example.htm"
    )
    != ".html",
)


# ------------------------------------------------------------
# F. MIME responsibility
# ------------------------------------------------------------

print()
print("=== F. MIME / CONTENT-TYPE ROLE ===")

route_source = Path(
    files_route.__file__
).read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "CONTENT_TYPE_IS_RECORDED",
    '"content_type"'
    in route_source,
)

check(
    "GUESS_EXT_IGNORES_CONTENT_TYPE",
    "content_type"
    not in guess_source.lower(),
)

check(
    "INTAKE_DETECTOR_HAS_NO_MIME_AUTHORITY",
    "content_type"
    not in intake_source.lower()
    and "mimetype"
    not in intake_source.lower()
    and "mime"
    not in intake_source.lower(),
)


# ------------------------------------------------------------
# G. UDUC fallback responsibility
# ------------------------------------------------------------

print()
print("=== G. UDUC EXTENSION FALLBACK ===")

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

check(
    "UDUC_DOES_NOT_DEFINE_UPLOAD_ALLOWED_EXT",
    "ALLOWED_EXT"
    not in uduc_source,
)

check(
    "UDUC_DOES_NOT_DEFINE_UPLOAD_GUESS_EXT",
    "def _guess_ext("
    not in uduc_source,
)


# ------------------------------------------------------------
# H. Frontend is non-authoritative
# ------------------------------------------------------------

print()
print("=== H. FRONTEND RESPONSIBILITY ===")

frontend_path = Path(
    "frontend/public/assets/js/app.js"
)

frontend_source = frontend_path.read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "FRONTEND_PHYSICAL_ACCEPT_LIST_PRESENT",
    '".docx,.md,.markdown,.html,.htm,.txt"'
    in frontend_source,
)

check(
    "FRONTEND_MARKDOWN_SESSION_ALIAS_PRESENT",
    'if (value === ".markdown") return ".md";'
    in frontend_source,
)

check(
    "FRONTEND_HTM_SESSION_ALIAS_PRESENT",
    'if (value === ".htm") return ".html";'
    in frontend_source,
)

check(
    "BACKEND_DETECTOR_REMAINS_INDEPENDENT_OF_FRONTEND",
    "canonicalSessionFormat"
    not in route_source,
)


# ------------------------------------------------------------
# I. Detection side-effect boundary
# ------------------------------------------------------------

print()
print("=== I. DETECTION SIDE-EFFECT BOUNDARY ===")

for forbidden in [
    "write_text",
    "write_bytes",
    "mkdir",
    "replace(",
    "build_uduc",
    "highlight",
    "active_target_set",
    "semantic_runtime",
    "scorer",
]:
    check(
        "DETECTOR_NO_SIDE_EFFECT_"
        + forbidden.replace("_", "").replace("(", "").upper(),
        forbidden.lower()
        not in guess_source.lower(),
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
        "U4.2_RESPONSIBILITY_BOUNDARY_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U4.2 responsibility boundary verification failed."
    )

print(
    "U4.2_RESPONSIBILITY_BOUNDARY_VERIFICATION: PASS"
)