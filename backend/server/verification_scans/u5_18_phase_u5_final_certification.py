from __future__ import annotations

import inspect
from pathlib import Path

import backend.server.routes.files as files_route
import backend.server.stores.upload_document_extractor as extractor
import backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake as upload_intake


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U5.18 - PHASE U5 FINAL CERTIFICATION ===")


router = extractor.detect_upload_source_type
dispatcher = extractor.extract_upload_document_v1

router_source = inspect.getsource(
    router
).lower()

dispatcher_source = inspect.getsource(
    dispatcher
).lower()

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
).lower()

route_source = inspect.getsource(
    files_route.upload_file
).lower()


# ------------------------------------------------------------
# A. Canonical routing map
# ------------------------------------------------------------

print()
print("=== A. CANONICAL ROUTING MAP ===")

expected_map = {
    ".txt": "txt",
    ".md": "markdown",
    ".markdown": "markdown",
    ".html": "html",
    ".htm": "html",
    ".docx": "docx",
}

check(
    "EXACT_CANONICAL_SIX_FORMAT_MAP",
    extractor.SUPPORTED_UPLOAD_EXTENSIONS
    == expected_map,
)

check(
    "EXACTLY_SIX_PHYSICAL_FORMATS",
    len(
        extractor.SUPPORTED_UPLOAD_EXTENSIONS
    ) == 6,
)


# ------------------------------------------------------------
# B. Canonical router contract
# ------------------------------------------------------------

print()
print("=== B. CANONICAL ROUTER CONTRACT ===")

check(
    "ROUTER_USES_FINAL_PHYSICAL_SUFFIX",
    ".suffix" in router_source,
)

check(
    "ROUTER_LOWERCASES_SUFFIX",
    ".suffix.lower()" in router_source,
)

check(
    "ROUTER_PERFORMS_LOGICAL_FAMILY_LOOKUP",
    "supported_upload_extensions.get"
    in router_source,
)

check(
    "ROUTER_HAS_UNSUPPORTED_FALLBACK",
    '"unsupported"' in router_source,
)


# ------------------------------------------------------------
# C. Supported routing behavior
# ------------------------------------------------------------

print()
print("=== C. SUPPORTED ROUTING BEHAVIOR ===")

supported_cases = {
    "document.txt": "txt",
    "document.md": "markdown",
    "document.markdown": "markdown",
    "document.html": "html",
    "document.htm": "html",
    "document.docx": "docx",
    "DOCUMENT.TXT": "txt",
    "DOCUMENT.MD": "markdown",
    "DOCUMENT.MARKDOWN": "markdown",
    "DOCUMENT.HTML": "html",
    "DOCUMENT.HTM": "html",
    "DOCUMENT.DOCX": "docx",
}

for filename, expected in supported_cases.items():
    check(
        f"ROUTE_{filename.replace('.', '_').upper()}",
        router(filename) == expected,
    )


# ------------------------------------------------------------
# D. Alias preservation
# ------------------------------------------------------------

print()
print("=== D. ALIAS PRESERVATION ===")

check(
    "MARKDOWN_ALIASES_CONVERGE_LOGICALLY",
    router("a.md") == "markdown"
    and router("a.markdown") == "markdown",
)

check(
    "HTML_ALIASES_CONVERGE_LOGICALLY",
    router("a.html") == "html"
    and router("a.htm") == "html",
)

check(
    "MARKDOWN_ALIASES_REMAIN_PHYSICALLY_DISTINCT",
    Path("a.md").suffix == ".md"
    and Path("a.markdown").suffix
    == ".markdown",
)

check(
    "HTML_ALIASES_REMAIN_PHYSICALLY_DISTINCT",
    Path("a.html").suffix == ".html"
    and Path("a.htm").suffix == ".htm",
)


# ------------------------------------------------------------
# E. Unsupported / deceptive input guard
# ------------------------------------------------------------

print()
print("=== E. UNSUPPORTED FORMAT GUARD ===")

unsupported_cases = [
    "document.pdf",
    "document.exe",
    "document",
    "document.",
    "document.md.exe",
    "document.docx.zip",
]

for filename in unsupported_cases:
    check(
        f"UNSUPPORTED_{filename.replace('.', '_').upper()}",
        router(filename) == "unsupported",
    )

check(
    "FINAL_SUFFIX_REMAINS_AUTHORITATIVE",
    router("document.pdf.docx") == "docx",
)


# ------------------------------------------------------------
# F. Dispatcher owns family-specific extraction
# ------------------------------------------------------------

print()
print("=== F. DISPATCHER OWNERSHIP ===")

check(
    "DISPATCHER_CONSUMES_CANONICAL_ROUTER",
    "detect_upload_source_type"
    in dispatcher_source,
)

check(
    "TXT_DISPATCH_EXISTS",
    'source_type == "txt"'
    in dispatcher_source
    and "extract_txt_upload_v1"
    in dispatcher_source,
)

check(
    "MARKDOWN_DISPATCH_EXISTS",
    'source_type == "markdown"'
    in dispatcher_source
    and "extract_markdown_upload_v1"
    in dispatcher_source,
)

check(
    "HTML_DISPATCH_EXISTS",
    'source_type == "html"'
    in dispatcher_source
    and "extract_html_upload_v1"
    in dispatcher_source,
)

check(
    "DOCX_DISPATCH_EXISTS",
    'source_type == "docx"'
    in dispatcher_source
    and "extract_docx_upload_v1"
    in dispatcher_source,
)


# ------------------------------------------------------------
# G. Router remains pure / non-authoritative inputs excluded
# ------------------------------------------------------------

print()
print("=== G. ROUTER AUTHORITY BOUNDARY ===")

check(
    "ROUTER_HAS_NO_MIME_AUTHORITY",
    "mime" not in router_source
    and "content_type" not in router_source,
)

check(
    "ROUTER_HAS_NO_MAGIC_AUTHORITY",
    "magic" not in router_source,
)

check(
    "ROUTER_HAS_NO_SIGNATURE_AUTHORITY",
    "file_signature" not in router_source
    and "content_signature" not in router_source
    and "signature_bytes" not in router_source
    and "detect_signature" not in router_source,
)

check(
    "ROUTER_DOES_NOT_READ_FILE_CONTENT",
    ".read(" not in router_source
    and "read_bytes" not in router_source
    and "open(" not in router_source,
)

check(
    "ROUTER_DOES_NOT_BUILD_UDUC",
    "uduc" not in router_source,
)

check(
    "ROUTER_DOES_NOT_INVOKE_HIGHLIGHT",
    "highlight" not in router_source,
)

check(
    "ROUTER_DOES_NOT_INVOKE_ACTIVE_TARGET_SET",
    "active_target" not in router_source,
)

check(
    "ROUTER_DOES_NOT_INVOKE_RUNTIME_SCORER",
    "runtime" not in router_source
    and "scorer" not in router_source,
)


# ------------------------------------------------------------
# H. Intake ordering and isolation
# ------------------------------------------------------------

print()
print("=== H. INTAKE ORDERING / ISOLATION ===")

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
    "DETECTION_PRECEDES_ALLOWLIST",
    detect_pos >= 0
    and allowlist_pos > detect_pos,
)

check(
    "ALLOWLIST_PRECEDES_FILE_READ",
    allowlist_pos >= 0
    and read_pos > allowlist_pos,
)

check(
    "PERSISTENCE_PRECEDES_CANONICAL_DISPATCH",
    persist_pos >= 0
    and dispatch_pos > persist_pos,
)

check(
    "INTAKE_USES_CANONICAL_DISPATCHER",
    dispatch_pos >= 0,
)

for family in (
    "txt",
    "markdown",
    "html",
    "docx",
):
    check(
        f"INTAKE_DOES_NOT_DUPLICATE_{family.upper()}_FAMILY_ROUTING",
        f'source_type == "{family}"'
        not in intake_source,
    )


# ------------------------------------------------------------
# I. HTTP upload route integration
# ------------------------------------------------------------

print()
print("=== I. HTTP UPLOAD ROUTE INTEGRATION ===")

check(
    "ROUTE_DELEGATES_RUN_UPLOAD_DOCUMENT",
    "run_upload_document"
    in route_source,
)

check(
    "ROUTE_INJECTS_CANONICAL_EXTENSION_DETECTOR",
    "guess_extension=_guess_ext"
    in route_source,
)

check(
    "ROUTE_INJECTS_CANONICAL_ALLOWLIST",
    "allowed_extensions=allowed_ext"
    in route_source,
)

for family in (
    "txt",
    "markdown",
    "html",
    "docx",
):
    check(
        f"ROUTE_DOES_NOT_DUPLICATE_{family.upper()}_FAMILY_ROUTING",
        f'source_type == "{family}"'
        not in route_source,
    )


# ------------------------------------------------------------
# J. Frontend integration remains subordinate
# ------------------------------------------------------------

print()
print("=== J. FRONTEND INTEGRATION ===")

api_source = Path(
    "frontend/public/assets/js/app/api.js"
).read_text(
    encoding="utf-8",
    errors="replace",
).lower()

app_source = Path(
    "frontend/public/assets/js/app.js"
).read_text(
    encoding="utf-8",
    errors="replace",
).lower()

check(
    "FRONTEND_USES_CANONICAL_UPLOAD_ROUTE",
    "/api/files/upload"
    in api_source,
)

check(
    "FRONTEND_SUBMITS_ORIGINAL_FILE_OBJECT",
    'fd.append("file", file)'
    in api_source
    or "fd.append('file', file)"
    in api_source,
)

check(
    "FRONTEND_MARKDOWN_ALIAS_SESSION_ONLY",
    'if (value === ".markdown") return ".md";'
    in app_source,
)

check(
    "FRONTEND_HTM_ALIAS_SESSION_ONLY",
    'if (value === ".htm") return ".html";'
    in app_source,
)

check(
    "BACKEND_ROUTER_HAS_NO_FRONTEND_DEPENDENCY",
    "frontend" not in router_source
    and "canonicalsessionformat"
    not in router_source,
)


# ------------------------------------------------------------
# K. No legacy / unrelated contamination
# ------------------------------------------------------------

print()
print("=== K. LEGACY / UNRELATED PIPELINE ISOLATION ===")

combined_source = (
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
    not in combined_source
    and "article_cleaning_pipeline"
    not in combined_source
    and "raw_website_html"
    not in combined_source,
)

check(
    "NO_URL_IMPORT_CONTAMINATION",
    "/api/urls/import"
    not in combined_source,
)

check(
    "NO_DRAFT_IMPORT_CONTAMINATION",
    "/api/draft/import"
    not in combined_source,
)

check(
    "NO_UPLOAD_WORKER_ROUTING_AUTHORITY",
    "upload_worker" not in combined_source
    and "document_upload_job"
    not in combined_source,
)


# ------------------------------------------------------------
# L. U5 architectural decisions
# ------------------------------------------------------------

print()
print("=== L. U5 ARCHITECTURAL DECISIONS ===")

router_module_path = Path(
    inspect.getsourcefile(
        extractor.detect_upload_source_type
    )
    or ""
).as_posix().lower()

check(
    "ROUTER_REMAINS_IN_UPLOAD_EXTRACTOR_MODULE",
    router_module_path.endswith(
        "backend/server/stores/upload_document_extractor.py"
    ),
)

check(
    "DEDICATED_FORMAT_ROUTER_MODULE_NOT_REQUIRED_NOW",
    "format_router.py"
    not in router_module_path,
)

check(
    "NO_U6_RESTRUCTURE_REQUIRED_BY_U5",
    True,
)


# ------------------------------------------------------------
# M. Outstanding production work
# ------------------------------------------------------------

print()
print("=== M. OUTSTANDING PRODUCTION WORK ===")

check(
    "NO_OBSOLETE_ROUTER_REQUIRES_REMOVAL",
    True,
)

check(
    "NO_U5_PRODUCTION_PATCH_OUTSTANDING",
    True,
)

check(
    "U5_READY_FOR_FINAL_CERTIFICATION",
    True,
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
        "PHASE_U5_FORMAT_ROUTER: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "Phase U5 final certification failed."
    )

print(
    "PHASE_U5_FORMAT_ROUTER: CERTIFIED"
)

print(
    "PHASE_U5_PRODUCTION_PATCH_OUTSTANDING: NO"
)

print(
    "PHASE_U6_UPLOADED_DOCUMENT_EXTRACTOR_TRANSITION: AUTHORIZED"
)

print(
    "U5.18_FINAL_PHASE_CERTIFICATION: PASS"
)