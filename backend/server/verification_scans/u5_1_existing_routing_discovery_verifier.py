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


print("=== U5.1 - EXISTING ROUTING DISCOVERY VERIFICATION ===")


expected_map = {
    ".txt": "txt",
    ".md": "markdown",
    ".markdown": "markdown",
    ".html": "html",
    ".htm": "html",
    ".docx": "docx",
}


# ------------------------------------------------------------
# A. Canonical routing table
# ------------------------------------------------------------

print()
print("=== A. CANONICAL ROUTING TABLE ===")

check(
    "SUPPORTED_UPLOAD_EXTENSIONS_EXACT_MAP",
    extractor.SUPPORTED_UPLOAD_EXTENSIONS == expected_map,
)

check(
    "DETECT_UPLOAD_SOURCE_TYPE_EXISTS",
    callable(extractor.detect_upload_source_type),
)

for ext, expected_family in expected_map.items():
    check(
        "ROUTE_"
        + ext.replace(".", "").upper()
        + "_TO_"
        + expected_family.upper(),
        extractor.detect_upload_source_type(
            "document" + ext
        )
        == expected_family,
    )


# ------------------------------------------------------------
# B. Canonical dispatcher
# ------------------------------------------------------------

print()
print("=== B. CANONICAL DISPATCHER ===")

check(
    "EXTRACT_UPLOAD_DOCUMENT_V1_EXISTS",
    callable(extractor.extract_upload_document_v1),
)

dispatcher_source = inspect.getsource(
    extractor.extract_upload_document_v1
)

check(
    "DISPATCHES_TXT",
    'source_type == "txt"' in dispatcher_source
    and "extract_txt_upload_v1" in dispatcher_source,
)

check(
    "DISPATCHES_MARKDOWN",
    'source_type == "markdown"' in dispatcher_source
    and "extract_markdown_upload_v1" in dispatcher_source,
)

check(
    "DISPATCHES_HTML",
    'source_type == "html"' in dispatcher_source
    and "extract_html_upload_v1" in dispatcher_source,
)

check(
    "DISPATCHES_DOCX",
    'source_type == "docx"' in dispatcher_source
    and "extract_docx_upload_v1" in dispatcher_source,
)

check(
    "UNSUPPORTED_SOURCE_TYPE_GUARD_EXISTS",
    "unsupported_source_type" in dispatcher_source,
)


# ------------------------------------------------------------
# C. Intake / route responsibilities
# ------------------------------------------------------------

print()
print("=== C. RESPONSIBILITY BOUNDARIES ===")

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
)

route_source = inspect.getsource(
    files_route.upload_file
)

check(
    "INTAKE_CALLS_CANONICAL_EXTRACTOR",
    "extract_upload_document_v1" in intake_source,
)

check(
    "INTAKE_DOES_NOT_DISPATCH_FORMAT_FAMILIES",
    'source_type == "txt"' not in intake_source
    and 'source_type == "markdown"' not in intake_source
    and 'source_type == "html"' not in intake_source
    and 'source_type == "docx"' not in intake_source,
)

check(
    "FILES_ROUTE_DOES_NOT_DISPATCH_FORMAT_FAMILIES",
    'source_type == "txt"' not in route_source
    and 'source_type == "markdown"' not in route_source
    and 'source_type == "html"' not in route_source
    and 'source_type == "docx"' not in route_source,
)


# ------------------------------------------------------------
# D. Routing authority isolation
# ------------------------------------------------------------

print()
print("=== D. ROUTING AUTHORITY ISOLATION ===")

extractor_source = inspect.getsource(
    extractor
).lower()

check(
    "NO_MIME_ROUTING_AUTHORITY",
    "mime" not in extractor_source,
)

check(
    "NO_CONTENT_TYPE_ROUTING_AUTHORITY",
    "content_type" not in extractor_source,
)

check(
    "NO_MAGIC_ROUTING_AUTHORITY",
    "magic" not in extractor_source,
)

check(
    "NO_SIGNATURE_ROUTING_AUTHORITY",
    "file_signature" not in extractor_source
    and "content_signature" not in extractor_source
    and "signature_bytes" not in extractor_source
    and "detect_signature" not in extractor_source,
)


# ------------------------------------------------------------
# E. Frontend normalization is not routing authority
# ------------------------------------------------------------

print()
print("=== E. FRONTEND SEPARATION ===")

app_source = Path(
    "frontend/public/assets/js/app.js"
).read_text(
    encoding="utf-8",
    errors="replace",
).lower()

check(
    "FRONTEND_MARKDOWN_ALIAS_PRESENT",
    'if (value === ".markdown") return ".md";'
    in app_source,
)

check(
    "FRONTEND_HTM_ALIAS_PRESENT",
    'if (value === ".htm") return ".html";'
    in app_source,
)

check(
    "BACKEND_ROUTER_INDEPENDENT_OF_CANONIC_SESSION_FORMAT",
    "canonicalsessionformat"
    not in extractor_source,
)


# ------------------------------------------------------------
# F. No duplicate live router in scoped production paths
# ------------------------------------------------------------

print()
print("=== F. DUPLICATE ROUTER CHECK ===")

roots = [
    Path("backend/server/routes"),
    Path("backend/server/pipelines/upload_document"),
    Path("backend/server/stores"),
]

router_like_terms = [
    "def route_upload_format",
    "def route_format",
    "def dispatch_format",
    "def detect_upload_source_type",
]

hits = []

for root in roots:
    for path in root.rglob("*.py"):
        if "backups" in path.parts:
            continue

        if "verification_scans" in path.parts:
            continue

        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        for term in router_like_terms:
            if term in text:
                hits.append(
                    (
                        str(path).replace("\\", "/"),
                        term,
                    )
                )

expected_hit = (
    "backend/server/stores/upload_document_extractor.py",
    "def detect_upload_source_type",
)

check(
    "ONLY_CANONICAL_ROUTER_LIKE_DEFINITION_FOUND",
    hits == [expected_hit],
)


# ------------------------------------------------------------
# G. Unrelated routing systems isolated
# ------------------------------------------------------------

print()
print("=== G. UNRELATED SYSTEM ISOLATION ===")

check(
    "NO_WEBSITE_CLEANER_ROUTING",
    "article_body_cleaning_engine"
    not in extractor_source
    and "article_cleaning_pipeline"
    not in extractor_source,
)

check(
    "NO_URL_IMPORT_ROUTING",
    "/api/urls/import"
    not in extractor_source,
)

check(
    "NO_DRAFT_IMPORT_ROUTING",
    "/api/draft/import"
    not in extractor_source,
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
        "U5.1_EXISTING_ROUTING_DISCOVERY: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.1 existing routing discovery failed."
    )

print(
    "U5.1_EXISTING_ROUTING_DISCOVERY: CERTIFIED"
)

print(
    "U5.1_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U5.2_CANONICAL_FORMAT_ROUTER_RESPONSIBILITY_TRANSITION: AUTHORIZED"
)

print(
    "U5.1_FINAL_DISCOVERY_VERIFICATION: PASS"
)