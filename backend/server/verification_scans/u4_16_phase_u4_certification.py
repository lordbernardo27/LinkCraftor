from __future__ import annotations

import inspect
from pathlib import Path

import backend.server.routes.files as files_route
import backend.server.stores.upload_document_extractor as extractor

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline import (
    upload_intake,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U4.16 - PHASE U4 CERTIFICATION ===")


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

legacy_path = Path(
    "frontend/public/assets/js/features/upload.js"
)

legacy_backup_path = Path(
    "frontend/public/backups/"
    "u4_13_legacy_format_detection_cleanup/upload.js"
)

app_source = app_path.read_text(
    encoding="utf-8",
    errors="replace",
)

api_source = api_path.read_text(
    encoding="utf-8",
    errors="replace",
)

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
)

route_source = inspect.getsource(
    files_route
)

extractor_source = inspect.getsource(
    extractor
)


# ------------------------------------------------------------
# A. Canonical detector contract
# ------------------------------------------------------------

print()
print("=== A. CANONICAL DETECTOR CONTRACT ===")

check(
    "SAFE_FILENAME_FUNCTION_EXISTS",
    callable(files_route._safe_upload_filename),
)

check(
    "GUESS_EXT_FUNCTION_EXISTS",
    callable(files_route._guess_ext),
)

check(
    "LOWERCASE_FINAL_SUFFIX_RESULT",
    files_route._guess_ext(
        "Article.MarkDown"
    )
    == ".markdown",
)

check(
    "FINAL_SUFFIX_AUTHORITY",
    files_route._guess_ext(
        "article.docx.zip"
    )
    == ".zip",
)


# ------------------------------------------------------------
# B. Exact six physical formats
# ------------------------------------------------------------

print()
print("=== B. CANONICAL SIX PHYSICAL FORMATS ===")

check(
    "BACKEND_ALLOWLIST_EXACTLY_SIX",
    set(files_route.ALLOWED_EXT) == expected,
)

check(
    "EXTRACTOR_SUPPORT_EXACTLY_SIX",
    set(
        extractor.SUPPORTED_UPLOAD_EXTENSIONS.keys()
    )
    == expected,
)

for ext in sorted(expected):
    check(
        "SUPPORTED_"
        + ext.replace(".", "").upper(),
        ext in files_route.ALLOWED_EXT,
    )


# ------------------------------------------------------------
# C. Alias contract
# ------------------------------------------------------------

print()
print("=== C. PHYSICAL ALIAS CONTRACT ===")

check(
    "MARKDOWN_REMAINS_PHYSICAL_MARKDOWN",
    files_route._guess_ext(
        "article.markdown"
    )
    == ".markdown",
)

check(
    "HTM_REMAINS_PHYSICAL_HTM",
    files_route._guess_ext(
        "article.htm"
    )
    == ".htm",
)

check(
    "FRONTEND_MARKDOWN_SESSION_ALIAS_ONLY",
    'if (value === ".markdown") return ".md";'
    in app_source,
)

check(
    "FRONTEND_HTM_SESSION_ALIAS_ONLY",
    'if (value === ".htm") return ".html";'
    in app_source,
)


# ------------------------------------------------------------
# D. Detection ordering
# ------------------------------------------------------------

print()
print("=== D. DETECTION ORDERING ===")

detect_pos = intake_source.find(
    "extension = dependencies.guess_extension(filename)"
)

gate_pos = intake_source.find(
    "if extension not in allowed_extensions:"
)

read_pos = intake_source.find(
    "await file.read(MAX_UPLOAD_BYTES + 1)"
)

store_pos = intake_source.find(
    "metadata = dependencies.store_and_index("
)

extract_pos = intake_source.find(
    "extraction_result = extract_upload_document_v1("
)

check(
    "DETECTION_BEFORE_GATE",
    -1 < detect_pos < gate_pos,
)

check(
    "GATE_BEFORE_FILE_READ",
    -1 < gate_pos < read_pos,
)

check(
    "GATE_BEFORE_PERSISTENCE",
    -1 < gate_pos < store_pos,
)

check(
    "GATE_BEFORE_CANONICAL_EXTRACTION",
    -1 < gate_pos < extract_pos,
)


# ------------------------------------------------------------
# E. Unsupported behavior and path safety
# ------------------------------------------------------------

print()
print("=== E. REJECTION / PATH SAFETY ===")

check(
    "NO_EXTENSION_REJECTABLE",
    files_route._guess_ext(
        "article"
    )
    not in files_route.ALLOWED_EXT,
)

check(
    "TRAILING_DOT_REJECTABLE",
    files_route._guess_ext(
        "article."
    )
    not in files_route.ALLOWED_EXT,
)

check(
    "DECEPTIVE_MD_EXE_REJECTABLE",
    files_route._guess_ext(
        "article.md.exe"
    )
    == ".exe"
    and ".exe"
    not in files_route.ALLOWED_EXT,
)

check(
    "DECEPTIVE_DOCX_ZIP_REJECTABLE",
    files_route._guess_ext(
        "article.docx.zip"
    )
    == ".zip"
    and ".zip"
    not in files_route.ALLOWED_EXT,
)

check(
    "WINDOWS_PATH_SAFE",
    files_route._guess_ext(
        r"C:\Users\HP\Desktop\article.docx"
    )
    == ".docx",
)

check(
    "POSIX_PATH_SAFE",
    files_route._guess_ext(
        "/tmp/uploads/article.html"
    )
    == ".html",
)

check(
    "TRAVERSAL_PATH_SAFE",
    files_route._guess_ext(
        r"..\..\article.md"
    )
    == ".md",
)


# ------------------------------------------------------------
# F. MIME / magic non-authority
# ------------------------------------------------------------

print()
print("=== F. MIME / MAGIC NON-AUTHORITY ===")

intake_lower = intake_source.lower()

check(
    "MIME_NOT_ACCEPTANCE_AUTHORITY",
    "mime" not in intake_lower,
)

check(
    "MAGIC_NOT_ACCEPTANCE_AUTHORITY",
    "magic" not in intake_lower,
)

check(
    "SIGNATURE_NOT_ACCEPTANCE_AUTHORITY",
    "signature" not in intake_lower,
)


# ------------------------------------------------------------
# G. Frontend / backend alignment
# ------------------------------------------------------------

print()
print("=== G. FRONTEND / BACKEND ALIGNMENT ===")

check(
    "FRONTEND_PICKER_EXACT_SIX_PRESENT",
    '".docx,.md,.markdown,.html,.htm,.txt"'
    in app_source,
)

check(
    "FRONTEND_SENDS_ORIGINAL_FILE_OBJECT",
    'fd.append("file", file);'
    in api_source,
)

check(
    "FRONTEND_CANONICAL_ENDPOINT",
    "/api/files/upload?workspace_id="
    in api_source,
)

canonical_route = False

for route in files_route.router.routes:
    path = getattr(route, "path", "")
    methods = set(
        getattr(route, "methods", set()) or set()
    )

    if (
        path == "/api/files/upload"
        and "POST" in methods
    ):
        canonical_route = True
        break

check(
    "BACKEND_CANONICAL_POST_ROUTE_REGISTERED",
    canonical_route,
)


# ------------------------------------------------------------
# H. Legacy cleanup
# ------------------------------------------------------------

print()
print("=== H. LEGACY CLEANUP ===")

check(
    "LEGACY_FEATURE_UPLOAD_REMOVED",
    not legacy_path.exists(),
)

check(
    "LEGACY_FEATURE_UPLOAD_BACKUP_EXISTS",
    legacy_backup_path.exists(),
)

reference_hits = []

for path in Path("frontend/public").rglob("*"):
    if not path.is_file():
        continue

    if path.suffix.lower() not in {
        ".js",
        ".html",
    }:
        continue

    if "backups" in path.parts:
        continue

    text = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    if (
        "features/upload.js" in text
        or "wireUpload" in text
    ):
        reference_hits.append(str(path))

check(
    "NO_LIVE_LEGACY_UPLOAD_REFERENCES",
    not reference_hits,
)


# ------------------------------------------------------------
# I. Deferred / forbidden dependencies
# ------------------------------------------------------------

print()
print("=== I. U4 BOUNDARY ISOLATION ===")

production_surface = (
    route_source
    + "\n"
    + intake_source
    + "\n"
    + extractor_source
).lower()

forbidden_terms = [
    "article_body_cleaning_engine",
    "article_cleaning_pipeline",
    "enterprise_raw_html_acquisition_engine",
    "raw_website_html_fetch_runner",
    "format_router",
    "route_format",
    "dispatch_format",
    "from backend.server.stores.scorer",
    "semantic_runtime",
    "runtime_reader",
    "recommendation",
    "uucd_engine_v1",
    "uucd_persistence_v1",
    "universal_unified_content_document_v2",
]

for term in forbidden_terms:
    check(
        "NO_"
        + term
        .replace(".", "_")
        .replace("/", "_")
        .replace(" ", "_")
        .upper(),
        term.lower()
        not in production_surface,
    )


# ------------------------------------------------------------
# J. Unrelated systems remain isolated
# ------------------------------------------------------------

print()
print("=== J. UNRELATED SYSTEM ISOLATION ===")

check(
    "URL_IMPORT_REMAINS_SEPARATE",
    "/api/urls/import?workspace_id="
    in app_source,
)

check(
    "DRAFT_IMPORT_REMAINS_SEPARATE",
    "/api/draft/import?workspace_id="
    in app_source,
)


# ------------------------------------------------------------
# K. Phase certification
# ------------------------------------------------------------

print()
print("=== K. PHASE U4 CERTIFICATION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

check(
    "ALL_U4_FINAL_CHECKS_PASS",
    not failures,
)

print()
print("========================================")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "PHASE_U4_FORMAT_DETECTION: NOT_CERTIFIED"
    )

    print(
        "PHASE_U4_PRODUCTION_PATCH_OUTSTANDING: YES"
    )

    print(
        "PHASE_U5_FORMAT_ROUTER_TRANSITION: NOT_AUTHORIZED"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "Phase U4 certification failed."
    )

print(
    "PHASE_U4_FORMAT_DETECTION: CERTIFIED"
)

print(
    "PHASE_U4_PRODUCTION_PATCH_OUTSTANDING: NO"
)

print(
    "PHASE_U5_FORMAT_ROUTER_TRANSITION: AUTHORIZED"
)

print(
    "U4.16_FINAL_PHASE_CERTIFICATION: PASS"
)