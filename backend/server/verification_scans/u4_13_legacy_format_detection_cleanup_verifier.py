from __future__ import annotations

from pathlib import Path
import inspect

import backend.server.routes.files as files_route
import backend.server.stores.upload_document_extractor as extractor


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U4.13 - LEGACY FORMAT DETECTION CLEANUP ===")

root = Path(".")
app_path = Path("frontend/public/assets/js/app.js")
api_path = Path("frontend/public/assets/js/app/api.js")
legacy_path = Path("frontend/public/assets/js/features/upload.js")
backup_path = Path(
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

route_source = inspect.getsource(files_route)
extractor_source = inspect.getsource(extractor)


print()
print("=== A. LEGACY FILE CLEANUP ===")

check(
    "LEGACY_FEATURE_UPLOAD_REMOVED_FROM_LIVE_TREE",
    not legacy_path.exists(),
)

check(
    "LEGACY_FEATURE_UPLOAD_BACKUP_EXISTS",
    backup_path.exists(),
)


print()
print("=== B. CURRENT PICKER REMAINS LIVE ===")

check(
    "CURRENT_PICKER_HAS_CANONICAL_SIX_FORMATS",
    '".docx,.md,.markdown,.html,.htm,.txt"'
    in app_source,
)

check(
    "CURRENT_SESSION_FORMAT_FUNCTION_EXISTS",
    "function canonicalSessionFormat"
    in app_source,
)

check(
    "CURRENT_MARKDOWN_SESSION_ALIAS_EXISTS",
    'if (value === ".markdown") return ".md";'
    in app_source,
)

check(
    "CURRENT_HTM_SESSION_ALIAS_EXISTS",
    'if (value === ".htm") return ".html";'
    in app_source,
)


print()
print("=== C. CANONICAL UPLOAD API REMAINS LIVE ===")

check(
    "API_SENDS_ORIGINAL_FILE_OBJECT",
    'fd.append("file", file);'
    in api_source,
)

check(
    "API_USES_CANONICAL_FILES_UPLOAD_ENDPOINT",
    "/api/files/upload?workspace_id="
    in api_source,
)


print()
print("=== D. BACKEND CANONICAL FORMAT AUTHORITIES ===")

expected = {
    ".docx",
    ".txt",
    ".md",
    ".markdown",
    ".html",
    ".htm",
}

check(
    "BACKEND_ALLOWED_EXT_EXACTLY_CANONICAL_SIX",
    set(files_route.ALLOWED_EXT) == expected,
)

check(
    "EXTRACTOR_SUPPORTED_EXTENSIONS_EXACTLY_CANONICAL_SIX",
    set(extractor.SUPPORTED_UPLOAD_EXTENSIONS.keys()) == expected,
)

check(
    "ROUTE_WIRES_CANONICAL_ALLOWLIST",
    "allowed_extensions=ALLOWED_EXT"
    in inspect.getsource(files_route.upload_file),
)

check(
    "ROUTE_WIRES_CANONICAL_DETECTOR",
    "guess_extension=_guess_ext"
    in inspect.getsource(files_route.upload_file),
)


print()
print("=== E. NO LEGACY DETECTOR REMNANTS ===")

production_surface = (
    route_source
    + "\n"
    + extractor_source
    + "\n"
    + api_source
)

legacy_terms = [
    "mimetypes.guess_type",
    "python-magic",
    "libmagic",
    "LC_UPLOAD_FILE_SIGNATURES",
    "format_router",
    "route_format",
    "dispatch_format",
]

for term in legacy_terms:
    check(
        "NO_LEGACY_"
        + term
        .replace(".", "_")
        .replace("-", "_")
        .upper(),
        term.lower()
        not in production_surface.lower(),
    )


print()
print("=== F. NO LIVE REFERENCES TO REMOVED MODULE ===")

live_frontend_files = [
    p
    for p in Path("frontend/public").rglob("*")
    if p.is_file()
    and p.suffix.lower() in {".js", ".html"}
    and "backups" not in p.parts
]

legacy_reference_hits = []

for path in live_frontend_files:
    text = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    if (
        "features/upload.js" in text
        or "wireUpload" in text
    ):
        legacy_reference_hits.append(str(path))

check(
    "NO_LIVE_FEATURE_UPLOAD_REFERENCES",
    not legacy_reference_hits,
)


print()
print("=== G. UNRELATED FORMAT SYSTEMS UNTOUCHED ===")

check(
    "URL_IMPORT_ENDPOINT_REMAINS_SEPARATE",
    "/api/urls/import?workspace_id="
    in app_source,
)

check(
    "DRAFT_IMPORT_ENDPOINT_REMAINS_SEPARATE",
    "/api/draft/import?workspace_id="
    in app_source,
)


failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U4.13_LEGACY_FORMAT_DETECTION_CLEANUP_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U4.13 legacy format detection cleanup verification failed."
    )

print(
    "U4.13_LEGACY_FORMAT_DETECTION_CLEANUP_VERIFICATION: PASS"
)