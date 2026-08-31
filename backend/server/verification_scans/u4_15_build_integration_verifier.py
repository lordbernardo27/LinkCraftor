from __future__ import annotations

import inspect
from pathlib import Path

import backend.server.routes.files as files_route
import backend.server.stores.upload_document_extractor as extractor

from backend.server.pipelines.upload_document.coordinator import (
    run_upload_document,
)

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake import (
    UploadIntakeDependencies,
    run_upload_intake,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U4.15 - BUILD / INTEGRATION VERIFICATION ===")


# ------------------------------------------------------------
# A. Backend imports and symbols
# ------------------------------------------------------------

print()
print("=== A. BACKEND IMPORT / SYMBOL INTEGRITY ===")

check(
    "FILES_ROUTE_IMPORTABLE",
    files_route is not None,
)

check(
    "UPLOAD_EXTRACTOR_IMPORTABLE",
    extractor is not None,
)

check(
    "UPLOAD_INTAKE_IMPORTABLE",
    callable(run_upload_intake),
)

check(
    "UPLOAD_COORDINATOR_IMPORTABLE",
    callable(run_upload_document),
)

check(
    "UPLOAD_INTAKE_DEPENDENCIES_IMPORTABLE",
    UploadIntakeDependencies is not None,
)


# ------------------------------------------------------------
# B. Canonical six-format contract
# ------------------------------------------------------------

print()
print("=== B. CANONICAL FORMAT CONTRACT ===")

expected = {
    ".docx",
    ".txt",
    ".md",
    ".markdown",
    ".html",
    ".htm",
}

check(
    "BACKEND_ALLOWED_EXT_EXACTLY_SIX",
    set(files_route.ALLOWED_EXT) == expected,
)

check(
    "EXTRACTOR_SUPPORTED_EXTENSIONS_EXACTLY_SIX",
    set(extractor.SUPPORTED_UPLOAD_EXTENSIONS.keys()) == expected,
)

check(
    "GUESS_EXT_CALLABLE",
    callable(files_route._guess_ext),
)

check(
    "GUESS_EXT_CASE_NORMALIZATION_WORKS",
    files_route._guess_ext("ARTICLE.DOCX") == ".docx",
)


# ------------------------------------------------------------
# C. Canonical route registration
# ------------------------------------------------------------

print()
print("=== C. ROUTE REGISTRATION ===")

canonical_route_found = False

for route in files_route.router.routes:
    path = getattr(route, "path", "")
    methods = set(getattr(route, "methods", set()) or set())

    if (
        path == "/api/files/upload"
        and "POST" in methods
    ):
        canonical_route_found = True
        break

check(
    "POST_API_FILES_UPLOAD_REGISTERED",
    canonical_route_found,
)


# ------------------------------------------------------------
# D. Frontend integrity
# ------------------------------------------------------------

print()
print("=== D. FRONTEND INTEGRITY ===")

app_path = Path(
    "frontend/public/assets/js/app.js"
)

api_path = Path(
    "frontend/public/assets/js/app/api.js"
)

legacy_path = Path(
    "frontend/public/assets/js/features/upload.js"
)

app_source = app_path.read_text(
    encoding="utf-8",
    errors="replace",
)

api_source = api_path.read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "APP_JS_EXISTS",
    app_path.exists(),
)

check(
    "API_JS_EXISTS",
    api_path.exists(),
)

check(
    "FRONTEND_PICKER_CANONICAL_SIX_FORMATS",
    '".docx,.md,.markdown,.html,.htm,.txt"'
    in app_source,
)

check(
    "FRONTEND_CANONICAL_UPLOAD_ENDPOINT",
    "/api/files/upload?workspace_id="
    in api_source,
)

check(
    "FRONTEND_SENDS_ORIGINAL_FILE",
    'fd.append("file", file);'
    in api_source,
)

check(
    "LEGACY_FEATURE_UPLOAD_REMOVED",
    not legacy_path.exists(),
)


# ------------------------------------------------------------
# E. No live references to removed module
# ------------------------------------------------------------

print()
print("=== E. REMOVED MODULE REFERENCE INTEGRITY ===")

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
    "NO_LIVE_REMOVED_MODULE_REFERENCES",
    not reference_hits,
)


# ------------------------------------------------------------
# F. U4 dependency isolation
# ------------------------------------------------------------

print()
print("=== F. U4 DEPENDENCY ISOLATION ===")

production_surface = "\n".join(
    [
        inspect.getsource(files_route),
        inspect.getsource(run_upload_intake),
        inspect.getsource(extractor),
    ]
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
    "uucd_engine_v1",
    "uucd_persistence_v1",
    "universal_unified_content_document_v2",
]

for term in forbidden_terms:
    check(
        "NO_FORBIDDEN_"
        + term
        .replace(".", "_")
        .replace("/", "_")
        .replace(" ", "_")
        .upper(),
        term.lower() not in production_surface,
    )


# ------------------------------------------------------------
# G. Unrelated systems remain separate
# ------------------------------------------------------------

print()
print("=== G. UNRELATED SYSTEM ISOLATION ===")

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
        "U4.15_BUILD_INTEGRATION_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U4.15 build/integration verification failed."
    )

print(
    "U4.15_BUILD_INTEGRATION_VERIFICATION: PASS"
)