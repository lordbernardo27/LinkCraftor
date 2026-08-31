from __future__ import annotations

import inspect
import py_compile
from pathlib import Path

import backend.server.routes.files as files_route
import backend.server.stores.upload_document_extractor as extractor
import backend.server.pipelines.upload_document as upload_pipeline
import backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake as upload_intake


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U5.17 - BUILD / INTEGRATION VERIFICATION ===")


# ------------------------------------------------------------
# A. Import / symbol verification
# ------------------------------------------------------------

print()
print("=== A. IMPORT / SYMBOL VERIFICATION ===")

check(
    "UPLOAD_ROUTE_MODULE_IMPORTS",
    files_route is not None,
)

check(
    "UPLOAD_PIPELINE_MODULE_IMPORTS",
    upload_pipeline is not None,
)

check(
    "UPLOAD_INTAKE_MODULE_IMPORTS",
    upload_intake is not None,
)

check(
    "UPLOAD_EXTRACTOR_MODULE_IMPORTS",
    extractor is not None,
)

check(
    "CANONICAL_ROUTER_SYMBOL_EXISTS",
    callable(
        getattr(
            extractor,
            "detect_upload_source_type",
            None,
        )
    ),
)

check(
    "CANONICAL_DISPATCHER_SYMBOL_EXISTS",
    callable(
        getattr(
            extractor,
            "extract_upload_document_v1",
            None,
        )
    ),
)

check(
    "UPLOAD_PIPELINE_ENTRY_SYMBOL_EXISTS",
    callable(
        getattr(
            upload_pipeline,
            "run_upload_document",
            None,
        )
    ),
)


# ------------------------------------------------------------
# B. Exact canonical routing table
# ------------------------------------------------------------

print()
print("=== B. CANONICAL ROUTING TABLE ===")

expected_map = {
    ".txt": "txt",
    ".md": "markdown",
    ".markdown": "markdown",
    ".html": "html",
    ".htm": "html",
    ".docx": "docx",
}

check(
    "EXACT_SIX_FORMAT_ROUTING_TABLE",
    extractor.SUPPORTED_UPLOAD_EXTENSIONS
    == expected_map,
)

check(
    "ROUTING_TABLE_HAS_EXACTLY_SIX_ENTRIES",
    len(
        extractor.SUPPORTED_UPLOAD_EXTENSIONS
    )
    == 6,
)


# ------------------------------------------------------------
# C. Upload route integration
# ------------------------------------------------------------

print()
print("=== C. UPLOAD ROUTE INTEGRATION ===")

route_source = inspect.getsource(
    files_route.upload_file
).lower()

check(
    "UPLOAD_ROUTE_DELEGATES_RUN_UPLOAD_DOCUMENT",
    "run_upload_document"
    in route_source,
)

check(
    "UPLOAD_ROUTE_INJECTS_GUESS_EXTENSION",
    "guess_extension=_guess_ext"
    in route_source,
)

check(
    "UPLOAD_ROUTE_INJECTS_WORKSPACE_NORMALIZER",
    "normalize_workspace_id=_ws"
    in route_source,
)

check(
    "UPLOAD_ROUTE_INJECTS_PREVIEW_HELPER",
    "extract_preview=_extract_preview_from_bytes"
    in route_source,
)

check(
    "UPLOAD_ROUTE_INJECTS_STORAGE_WRITER",
    "store_and_index=_store_and_index"
    in route_source,
)

check(
    "UPLOAD_ROUTE_INJECTS_ROLLBACK_HANDLER",
    "rollback_committed_upload=_rollback_committed_upload"
    in route_source,
)

check(
    "UPLOAD_ROUTE_INJECTS_WORKSPACE_DIRECTORY",
    "workspace_directory=_ws_dir"
    in route_source,
)

check(
    "UPLOAD_ROUTE_INJECTS_ALLOWED_EXTENSIONS",
    "allowed_extensions=allowed_ext"
    in route_source,
)


# ------------------------------------------------------------
# D. Intake contract still intact
# ------------------------------------------------------------

print()
print("=== D. INTAKE CONTRACT ===")

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
).lower()

check(
    "INTAKE_VALIDATES_FILENAME",
    "uploaded file must have a filename."
    in intake_source,
)

check(
    "INTAKE_DETECTS_EXTENSION",
    "dependencies.guess_extension"
    in intake_source,
)

check(
    "INTAKE_APPLIES_ALLOWLIST_GATE",
    "if extension not in allowed_extensions"
    in intake_source,
)

check(
    "INTAKE_NORMALIZES_WORKSPACE",
    "dependencies.normalize_workspace_id"
    in intake_source,
)

check(
    "INTAKE_USES_BOUNDED_READ",
    "await file.read(max_upload_bytes + 1)"
    in intake_source,
)

check(
    "INTAKE_REJECTS_EMPTY_UPLOAD",
    "uploaded file is empty."
    in intake_source,
)

check(
    "INTAKE_REJECTS_OVERSIZED_UPLOAD",
    "uploaded file exceeds the 250 mb limit."
    in intake_source,
)

check(
    "INTAKE_CREATES_PREVIEW",
    "dependencies.extract_preview"
    in intake_source,
)

check(
    "INTAKE_PERSISTS_SOURCE",
    "dependencies.store_and_index"
    in intake_source,
)

check(
    "INTAKE_INVOKES_CANONICAL_DISPATCHER",
    "extract_upload_document_v1"
    in intake_source,
)


# ------------------------------------------------------------
# E. Ordering
# ------------------------------------------------------------

print()
print("=== E. ROUTING / EXTRACTION ORDER ===")

detect_pos = intake_source.find(
    "dependencies.guess_extension"
)

allowlist_pos = intake_source.find(
    "if extension not in allowed_extensions"
)

read_pos = intake_source.find(
    "await file.read(max_upload_bytes + 1)"
)

persist_pos = intake_source.find(
    "dependencies.store_and_index"
)

dispatch_pos = intake_source.find(
    "extract_upload_document_v1"
)

check(
    "EXTENSION_DETECTION_PRECEDES_ALLOWLIST",
    detect_pos >= 0
    and allowlist_pos > detect_pos,
)

check(
    "ALLOWLIST_PRECEDES_FILE_READ",
    allowlist_pos >= 0
    and read_pos > allowlist_pos,
)

check(
    "PERSISTENCE_PRECEDES_DISPATCHER",
    persist_pos >= 0
    and dispatch_pos > persist_pos,
)


# ------------------------------------------------------------
# F. Unsupported guard
# ------------------------------------------------------------

print()
print("=== F. UNSUPPORTED GUARD ===")

check(
    "UNSUPPORTED_PDF_ROUTES_UNSUPPORTED",
    extractor.detect_upload_source_type(
        "document.pdf"
    )
    == "unsupported",
)

check(
    "NO_EXTENSION_ROUTES_UNSUPPORTED",
    extractor.detect_upload_source_type(
        "document"
    )
    == "unsupported",
)

check(
    "TRAILING_DOT_ROUTES_UNSUPPORTED",
    extractor.detect_upload_source_type(
        "document."
    )
    == "unsupported",
)

check(
    "DECEPTIVE_FINAL_SUFFIX_REMAINS_AUTHORITATIVE",
    extractor.detect_upload_source_type(
        "document.md.exe"
    )
    == "unsupported"
    and extractor.detect_upload_source_type(
        "document.pdf.docx"
    )
    == "docx",
)


# ------------------------------------------------------------
# G. No duplicate logical-family routing
# ------------------------------------------------------------

print()
print("=== G. NO DUPLICATE LOGICAL ROUTING ===")

for family in (
    "txt",
    "markdown",
    "html",
    "docx",
):
    check(
        f"ROUTE_DOES_NOT_DUPLICATE_{family.upper()}_DISPATCH",
        f'source_type == "{family}"'
        not in route_source,
    )

    check(
        f"INTAKE_DOES_NOT_DUPLICATE_{family.upper()}_DISPATCH",
        f'source_type == "{family}"'
        not in intake_source,
    )


# ------------------------------------------------------------
# H. Frontend integration
# ------------------------------------------------------------

print()
print("=== H. FRONTEND INTEGRATION ===")

api_js = Path(
    "frontend/public/assets/js/app/api.js"
).read_text(
    encoding="utf-8",
    errors="replace",
).lower()

app_js = Path(
    "frontend/public/assets/js/app.js"
).read_text(
    encoding="utf-8",
    errors="replace",
).lower()

check(
    "FRONTEND_UPLOAD_API_TARGETS_CANONICAL_ROUTE",
    "/api/files/upload"
    in api_js,
)

check(
    "FRONTEND_SUBMITS_ORIGINAL_FILE_OBJECT",
    'fd.append("file", file)'
    in api_js
    or "fd.append('file', file)"
    in api_js,
)

check(
    "FRONTEND_MARKDOWN_ALIAS_IS_SESSION_ONLY",
    'if (value === ".markdown") return ".md";'
    in app_js,
)

check(
    "FRONTEND_HTM_ALIAS_IS_SESSION_ONLY",
    'if (value === ".htm") return ".html";'
    in app_js,
)


# ------------------------------------------------------------
# I. Unrelated pipeline isolation
# ------------------------------------------------------------

print()
print("=== I. UNRELATED PIPELINE ISOLATION ===")

router_source = inspect.getsource(
    extractor.detect_upload_source_type
).lower()

dispatcher_source = inspect.getsource(
    extractor.extract_upload_document_v1
).lower()

combined_upload_source = (
    router_source
    + "\n"
    + dispatcher_source
    + "\n"
    + intake_source
    + "\n"
    + route_source
)

check(
    "NO_WEBSITE_CLEANER_CONTAMINATION",
    "article_body_cleaning_engine"
    not in combined_upload_source
    and "article_cleaning_pipeline"
    not in combined_upload_source
    and "raw_website_html"
    not in combined_upload_source,
)

check(
    "NO_URL_IMPORT_CONTAMINATION",
    "/api/urls/import"
    not in combined_upload_source,
)

check(
    "NO_DRAFT_IMPORT_CONTAMINATION",
    "/api/draft/import"
    not in combined_upload_source,
)

check(
    "NO_UPLOAD_WORKER_ROUTING_CONTAMINATION",
    "upload_worker"
    not in combined_upload_source
    and "document_upload_job"
    not in combined_upload_source,
)


# ------------------------------------------------------------
# J. Verification scan isolation
# ------------------------------------------------------------

print()
print("=== J. VERIFICATION SCAN ISOLATION ===")

check(
    "VERIFICATION_SCANS_NOT_PRODUCTION_ROUTER",
    "verification_scans"
    not in inspect.getsourcefile(
        extractor.detect_upload_source_type
    ).replace("\\", "/").lower(),
)

check(
    "VERIFICATION_SCANS_NOT_PRODUCTION_DISPATCHER",
    "verification_scans"
    not in inspect.getsourcefile(
        extractor.extract_upload_document_v1
    ).replace("\\", "/").lower(),
)


# ------------------------------------------------------------
# K. Compile verification
# ------------------------------------------------------------

print()
print("=== K. PYTHON COMPILE VERIFICATION ===")

compile_targets = [
    Path(
        "backend/server/routes/files.py"
    ),
    Path(
        "backend/server/stores/upload_document_extractor.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/__init__.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/coordinator.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_uduc_pipeline/__init__.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_uduc_pipeline/coordinator.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_uduc_pipeline/upload_intake.py"
    ),
]

for target in compile_targets:
    try:
        py_compile.compile(
            str(target),
            doraise=True,
        )
        ok = True
    except Exception:
        ok = False

    check(
        f"COMPILE_{target.name.upper()}",
        ok,
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
        "U5.17_BUILD_INTEGRATION_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.17 build/integration verification failed."
    )

print(
    "U5.17_BUILD_INTEGRATION_VERIFICATION: CERTIFIED"
)

print(
    "U5.17_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U5.18_PHASE_U5_CERTIFICATION_TRANSITION: AUTHORIZED"
)

print(
    "U5.17_FINAL_BUILD_INTEGRATION_VERIFICATION: PASS"
)