from __future__ import annotations

import importlib
import py_compile
from pathlib import Path


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


root = Path(".").resolve()


print("=== U3.14 FINAL CERTIFICATION ===")


# ------------------------------------------------------------
# 1. Required U3.14 verification logs.
# ------------------------------------------------------------

print()
print("=== A. U3.14 VERIFICATION LOGS ===")

required_logs = {
    "IMPORT_BUILD": (
        Path(
            "backend/server/verification_scans/"
            "u3_14_import_build_surface_verification.txt"
        ),
        "U3.14_IMPORT_BUILD_SURFACE_VERIFICATION: PASS",
    ),
    "ROUTE_WIRING": (
        Path(
            "backend/server/verification_scans/"
            "u3_14_route_wiring_verification.txt"
        ),
        "U3.14_ROUTE_WIRING_VERIFICATION: PASS",
    ),
    "PREMATURE_INTEGRATION": (
        Path(
            "backend/server/verification_scans/"
            "u3_14_premature_integration_boundary_verification.txt"
        ),
        "U3.14_PREMATURE_INTEGRATION_BOUNDARY_VERIFICATION: PASS",
    ),
    "FULL_INTEGRATION_SMOKE": (
        Path(
            "backend/server/verification_scans/"
            "u3_14_full_integration_smoke_verification.txt"
        ),
        "U3.14_FULL_INTEGRATION_SMOKE_VERIFICATION: PASS",
    ),
}


for label, (path, marker) in required_logs.items():
    check(
        f"{label}_LOG_EXISTS",
        path.is_file(),
    )

    text = ""

    if path.is_file():
        for encoding in (
            "utf-8-sig",
            "utf-16",
            "utf-8",
        ):
            try:
                text = path.read_text(
                    encoding=encoding
                )
                break
            except UnicodeError:
                continue

    check(
        f"{label}_PASS_MARKER",
        marker in text,
    )


# ------------------------------------------------------------
# 2. Canonical Upload Document route.
# ------------------------------------------------------------

print()
print("=== B. CANONICAL DOCUMENT UPLOAD ROUTE ===")

import backend.server.routes.files as files_route

document_upload_routes = [
    route
    for route in files_route.router.routes
    if getattr(route, "path", "")
    == "/api/files/upload"
    and "POST"
    in set(
        getattr(route, "methods", set())
        or set()
    )
]

check(
    "EXACTLY_ONE_CANONICAL_DOCUMENT_UPLOAD_ROUTE",
    len(document_upload_routes) == 1,
)


# ------------------------------------------------------------
# 3. Imported-target URL upload remains a separate route.
# ------------------------------------------------------------

print()
print("=== C. IMPORTED-TARGET UPLOAD SEPARATION ===")

compat_path = Path(
    "backend/server/routes/"
    "imported_targets_urls_compat.py"
)

check(
    "IMPORTED_TARGET_COMPAT_FILE_EXISTS",
    compat_path.is_file(),
)

compat_text = ""

if compat_path.is_file():
    compat_text = compat_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

check(
    "IMPORTED_TARGET_UPLOAD_ROUTE_REMAINS_PRESENT",
    '@router.post("/upload")'
    in compat_text,
)

check(
    "IMPORTED_TARGET_ROUTE_IS_NOT_DOCUMENT_UPLOAD_ROUTE",
    "/api/files/upload"
    not in compat_text,
)


# ------------------------------------------------------------
# 4. Exact format contract and ceiling.
# ------------------------------------------------------------

print()
print("=== D. FORMAT / SIZE CONTRACT ===")

expected_extensions = {
    ".txt",
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".docx",
}

check(
    "SIX_FORMAT_ROUTE_ALLOWLIST_EXACT",
    set(files_route.ALLOWED_EXT)
    == expected_extensions,
)

from backend.server.stores.upload_document_extractor import (
    SUPPORTED_UPLOAD_EXTENSIONS,
)

check(
    "SIX_FORMAT_EXTRACTOR_ALLOWLIST_EXACT",
    set(SUPPORTED_UPLOAD_EXTENSIONS.keys())
    == expected_extensions,
)

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline import (
    upload_intake,
)

check(
    "UPLOAD_CEILING_250_MIB",
    upload_intake.MAX_UPLOAD_BYTES
    == 250 * 1024 * 1024,
)


# ------------------------------------------------------------
# 5. Frontend canonical integration.
# ------------------------------------------------------------

print()
print("=== E. FRONTEND CONTRACT ===")

api_path = Path(
    "frontend/public/assets/js/app/api.js"
)

app_path = Path(
    "frontend/public/assets/js/app.js"
)

api_text = api_path.read_text(
    encoding="utf-8",
    errors="replace",
)

app_text = app_path.read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "FRONTEND_CANONICAL_UPLOAD_ENDPOINT_PRESENT",
    "/api/files/upload?workspace_id="
    in api_text,
)

check(
    "FRONTEND_MARKDOWN_ALIAS_PRESENT",
    'if (value === ".markdown") return ".md";'
    in app_text,
)

check(
    "FRONTEND_HTM_ALIAS_PRESENT",
    'if (value === ".htm") return ".html";'
    in app_text,
)

obsolete_frontend_routes = [
    "/upload-document",
    "/upload_document",
    "/document/upload",
]

check(
    "NO_OBSOLETE_FRONTEND_UPLOAD_ENDPOINT",
    all(
        route not in api_text
        and route not in app_text
        for route in obsolete_frontend_routes
    ),
)


# ------------------------------------------------------------
# 6. Markdown corrective contract.
# ------------------------------------------------------------

print()
print("=== F. MARKDOWN CORRECTIVE CONTRACT ===")

extractor_path = Path(
    "backend/server/stores/"
    "upload_document_extractor.py"
)

extractor_text = extractor_path.read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "MARKDOWN_STAR_CODE_REGEX_PRESENT",
    "_MD_STAR_OR_CODE_RE"
    in extractor_text,
)

check(
    "MARKDOWN_BOUNDARY_UNDERSCORE_REGEX_PRESENT",
    "_MD_UNDERSCORE_EMPHASIS_RE"
    in extractor_text,
)

check(
    "OLD_COMBINED_MARKDOWN_REGEX_ABSENT",
    '_MD_EMPHASIS_RE = re.compile'
    not in extractor_text,
)

py_compile.compile(
    str(extractor_path),
    doraise=True,
)

check(
    "MARKDOWN_CORRECTIVE_PATCH_COMPILES",
    True,
)


# ------------------------------------------------------------
# 7. No premature integration.
# ------------------------------------------------------------

print()
print("=== G. PREMATURE INTEGRATION BOUNDARY ===")

production_targets = [
    Path("backend/server/routes/files.py"),
    Path(
        "backend/server/stores/"
        "upload_document_extractor.py"
    ),
    Path(
        "backend/server/stores/"
        "uploaded_document_unified_content.py"
    ),
    Path(
        "backend/server/pipelines/"
        "upload_document/coordinator.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_uduc_pipeline/"
        "coordinator.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_uduc_pipeline/"
        "upload_intake.py"
    ),
]

combined = "\n".join(
    path.read_text(
        encoding="utf-8",
        errors="replace",
    )
    for path in production_targets
)

forbidden = [
    "BackgroundTasks",
    "create_task",
    "run_in_executor",
    "upload_worker",
    "upload worker",
    "upload_job",
    "upload job",
    "uucd_engine",
    "uucd_persistence",
    "universal_unified_content_document",
    "semantic_runtime",
    "run_scorer",
    "register_runtime",
]

check(
    "NO_PREMATURE_WORKER_RUNTIME_UUCD_INTEGRATION",
    all(
        term.lower()
        not in combined.lower()
        for term in forbidden
    ),
)


# ------------------------------------------------------------
# 8. Website cleaner isolation.
# ------------------------------------------------------------

print()
print("=== H. WEBSITE BRANCH ISOLATION ===")

website_cleaners = [
    Path(
        "backend/server/stores/"
        "article_body_cleaning_engine.py"
    ),
    Path(
        "backend/server/stores/"
        "article_cleaning_pipeline.py"
    ),
]

check(
    "WEBSITE_CLEANERS_EXIST",
    all(
        path.is_file()
        for path in website_cleaners
    ),
)

check(
    "UPLOAD_BRANCH_DOES_NOT_REFERENCE_WEBSITE_CLEANERS",
    "article_body_cleaning_engine"
    not in combined
    and "article_cleaning_pipeline"
    not in combined,
)


# ------------------------------------------------------------
# 9. No persistent U3.14 synthetic workspace.
# ------------------------------------------------------------

print()
print("=== I. LIVE SYNTHETIC ARTIFACT SWEEP ===")

live_roots = [
    Path("backend/server/data/docs"),
    Path(
        "backend/server/data/"
        "uploaded_document_unified_content"
    ),
    Path(
        "backend/server/data/dis/"
        "rejection_patterns"
    ),
]

live_hits = []

for live_root in live_roots:
    if not live_root.exists():
        continue

    for path in live_root.rglob("*"):
        if (
            "u3_14_smoke_"
            in path.name.lower()
        ):
            live_hits.append(path)


for path in live_hits:
    print(
        "LIVE_SYNTHETIC_HIT:",
        path,
    )

check(
    "LIVE_U3_14_SYNTHETIC_ARTIFACT_COUNT_ZERO",
    len(live_hits) == 0,
)


# ------------------------------------------------------------
# 10. Final result.
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
        "U3.14_FINAL_CERTIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U3.14 final certification failed."
    )

print(
    "U3.14_FINAL_CERTIFICATION: PASS"
)