from __future__ import annotations

import inspect
from pathlib import Path

import backend.server.routes.files as files_route


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U4.12 - FRONTEND / BACKEND ALIGNMENT ===")

expected = {
    ".txt",
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".docx",
}

app_path = Path(
    "frontend/public/assets/js/app.js"
)

api_path = Path(
    "frontend/public/assets/js/app/api.js"
)

app_source = app_path.read_text(
    encoding="utf-8",
    errors="replace",
)

api_source = api_path.read_text(
    encoding="utf-8",
    errors="replace",
)

route_source = inspect.getsource(
    files_route.upload_file
)


# ------------------------------------------------------------
# A. Exact six-format alignment
# ------------------------------------------------------------

print()
print("=== A. SIX-FORMAT ALIGNMENT ===")

check(
    "BACKEND_EXACTLY_SIX_FORMATS",
    set(files_route.ALLOWED_EXT) == expected,
)

check(
    "FRONTEND_PICKER_EXPOSES_ALL_SIX",
    '".docx,.md,.markdown,.html,.htm,.txt"'
    in app_source,
)

for ext in expected:
    check(
        "FRONTEND_HAS_"
        + ext.replace(".", "").upper(),
        ext in app_source,
    )


# ------------------------------------------------------------
# B. Frontend session alias contract
# ------------------------------------------------------------

print()
print("=== B. SESSION ALIAS CONTRACT ===")

check(
    "FRONTEND_MARKDOWN_TO_MD_SESSION_ALIAS",
    'if (value === ".markdown") return ".md";'
    in app_source,
)

check(
    "FRONTEND_HTM_TO_HTML_SESSION_ALIAS",
    'if (value === ".htm") return ".html";'
    in app_source,
)

check(
    "BACKEND_PRESERVES_MARKDOWN_PHYSICAL_ALIAS",
    files_route._guess_ext(
        "article.markdown"
    )
    == ".markdown",
)

check(
    "BACKEND_PRESERVES_HTM_PHYSICAL_ALIAS",
    files_route._guess_ext(
        "article.htm"
    )
    == ".htm",
)


# ------------------------------------------------------------
# C. Canonical Uploaded Document API path
# ------------------------------------------------------------

print()
print("=== C. CANONICAL UPLOAD API PATH ===")

check(
    "API_JS_USES_FORMDATA",
    "new FormData()"
    in api_source,
)

check(
    "API_JS_APPENDS_ORIGINAL_FILE_OBJECT",
    'fd.append("file", file);'
    in api_source,
)

check(
    "API_JS_USES_CANONICAL_FILES_UPLOAD_ENDPOINT",
    "/api/files/upload?workspace_id="
    in api_source,
)

check(
    "API_JS_USES_POST_METHOD",
    'method: "POST"'
    in api_source,
)


# ------------------------------------------------------------
# D. No physical filename alias rewrite before upload
# ------------------------------------------------------------

print()
print("=== D. ORIGINAL PHYSICAL FILENAME PRESERVATION ===")

check(
    "UPLOAD_API_DOES_NOT_RENAME_MARKDOWN_TO_MD",
    'file.name.replace(".markdown", ".md")'
    not in api_source,
)

check(
    "UPLOAD_API_DOES_NOT_RENAME_HTM_TO_HTML",
    'file.name.replace(".htm", ".html")'
    not in api_source,
)

check(
    "UPLOAD_API_DOES_NOT_CREATE_RENAMED_FILE",
    "new File("
    not in api_source,
)

check(
    "UPLOAD_API_SENDS_FILE_DIRECTLY",
    'fd.append("file", file);'
    in api_source,
)


# ------------------------------------------------------------
# E. Backend remains authoritative
# ------------------------------------------------------------

print()
print("=== E. BACKEND AUTHORITY ===")

check(
    "ROUTE_INJECTS_CANONICAL_DETECTOR",
    "guess_extension=_guess_ext"
    in route_source,
)

check(
    "ROUTE_INJECTS_BACKEND_ALLOWLIST",
    "allowed_extensions=ALLOWED_EXT"
    in route_source,
)

check(
    "FRONTEND_CANNOT_EXPAND_BACKEND_ALLOWLIST",
    set(files_route.ALLOWED_EXT) == expected,
)

check(
    "BACKEND_NORMALIZES_UPPERCASE_SUFFIX",
    files_route._guess_ext(
        "ARTICLE.DOCX"
    )
    == ".docx",
)

check(
    "BACKEND_NORMALIZES_MIXED_CASE_SUFFIX",
    files_route._guess_ext(
        "article.MarkDown"
    )
    == ".markdown",
)


# ------------------------------------------------------------
# F. MIME / magic / router non-authority in frontend upload API
# ------------------------------------------------------------

print()
print("=== F. NO FRONTEND FORMAT AUTHORITY ===")

api_lower = api_source.lower()

check(
    "UPLOAD_API_NO_CONTENT_TYPE_AUTHORITY",
    "content_type"
    not in api_lower,
)

check(
    "UPLOAD_API_NO_MIME_AUTHORITY",
    "mimetype"
    not in api_lower
    and "mime_type"
    not in api_lower,
)

check(
    "UPLOAD_API_NO_MAGIC_DETECTION",
    "magic"
    not in api_lower,
)

check(
    "UPLOAD_API_NO_FORMAT_ROUTER",
    "format_router"
    not in api_lower
    and "route_format"
    not in api_lower
    and "dispatch_format"
    not in api_lower,
)


# ------------------------------------------------------------
# G. Separate unrelated upload workflows
# ------------------------------------------------------------

print()
print("=== G. UNRELATED UPLOAD WORKFLOW ISOLATION ===")

check(
    "APP_JS_URL_IMPORT_USES_URLS_ENDPOINT",
    "/api/urls/import?workspace_id="
    in app_source,
)

check(
    "APP_JS_DRAFT_IMPORT_USES_DRAFT_ENDPOINT",
    "/api/draft/import?workspace_id="
    in app_source,
)

check(
    "UPLOADED_DOCUMENT_API_NOT_URL_IMPORT",
    "/api/urls/import"
    not in api_source,
)

check(
    "UPLOADED_DOCUMENT_API_NOT_DRAFT_IMPORT",
    "/api/draft/import"
    not in api_source,
)


# ------------------------------------------------------------
# H. Response compatibility
# ------------------------------------------------------------

print()
print("=== H. RESPONSE COMPATIBILITY ===")

for field in [
    "filename",
    "ext",
    "text",
    "html",
    "doc_id",
    "workspace_id",
]:
    check(
        "API_JS_HANDLES_RESPONSE_FIELD_"
        + field.upper(),
        field in api_source,
    )


# ------------------------------------------------------------
# I. No obsolete document upload endpoint
# ------------------------------------------------------------

print()
print("=== I. NO OBSOLETE DOCUMENT UPLOAD ENDPOINT ===")

obsolete_candidates = [
    "/api/upload",
    "/api/document/upload",
    "/api/documents/upload",
]

for candidate in obsolete_candidates:
    check(
        "API_JS_NO_OBSOLETE_"
        + candidate
        .replace("/", "_")
        .replace("-", "_")
        .upper(),
        candidate not in api_source,
    )

check(
    "API_JS_NO_OBSOLETE_BARE_FILES_UPLOAD",
    'fetch(`${API_BASE}/files/upload'
    not in api_source
    and 'fetch("/files/upload'
    not in api_source
    and "fetch('/files/upload"
    not in api_source,
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
        "U4.12_FRONTEND_BACKEND_ALIGNMENT_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U4.12 frontend/backend alignment verification failed."
    )

print(
    "U4.12_FRONTEND_BACKEND_ALIGNMENT_VERIFICATION: PASS"
)