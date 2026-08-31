from __future__ import annotations

import inspect
from pathlib import Path

import backend.server.stores.upload_document_extractor as extractor

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline import (
    upload_intake,
)


print("=== U5.1 STEP 3 - ROUTING BOUNDARY DISCOVERY ===")
print()

extractor_source = inspect.getsource(extractor).lower()
intake_source = inspect.getsource(upload_intake).lower()

app_source = Path(
    "frontend/public/assets/js/app.js"
).read_text(
    encoding="utf-8",
    errors="replace",
).lower()


checks = {
    "EXTRACTOR_NO_MIME_ROUTING":
        "mime" not in extractor_source,

    "EXTRACTOR_NO_CONTENT_TYPE_ROUTING":
        "content_type" not in extractor_source,

    "EXTRACTOR_NO_MAGIC_ROUTING":
        "magic" not in extractor_source,

    "EXTRACTOR_NO_SIGNATURE_ROUTING":
        "file_signature" not in extractor_source
        and "content_signature" not in extractor_source
        and "signature_bytes" not in extractor_source
        and "detect_signature" not in extractor_source,

    "INTAKE_NO_FORMAT_FAMILY_DISPATCH":
        'source_type == "txt"' not in intake_source
        and 'source_type == "markdown"' not in intake_source
        and 'source_type == "html"' not in intake_source
        and 'source_type == "docx"' not in intake_source,

    "FRONTEND_SESSION_ALIAS_PRESENT":
        'if (value === ".markdown") return ".md";'
        in app_source
        and 'if (value === ".htm") return ".html";'
        in app_source,

    "EXTRACTOR_NO_FRONTEND_SESSION_AUTHORITY":
        "canonicalsessionformat" not in extractor_source,

    "EXTRACTOR_NO_WEBSITE_CLEANER_ROUTING":
        "article_body_cleaning_engine" not in extractor_source
        and "article_cleaning_pipeline" not in extractor_source,

    "EXTRACTOR_NO_URL_IMPORT_ROUTING":
        "/api/urls/import" not in extractor_source,

    "EXTRACTOR_NO_DRAFT_IMPORT_ROUTING":
        "/api/draft/import" not in extractor_source,
}

failures = []

for name, condition in checks.items():
    status = "PASS" if condition else "FAIL"
    print(f"{name}: {status}")

    if not condition:
        failures.append(name)

print()
print("=== CURRENT ROUTING MAP ===")

for ext, family in sorted(
    extractor.SUPPORTED_UPLOAD_EXTENSIONS.items()
):
    print(f"{ext} -> {family}")

print()
print("========================================")

if failures:
    print("U5.1_STEP3_ROUTING_BOUNDARY_DISCOVERY: FAIL")
    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.1 routing boundary discovery failed."
    )

print(
    "U5.1_STEP3_ROUTING_BOUNDARY_DISCOVERY: PASS"
)