from __future__ import annotations

import inspect

import backend.server.routes.files as files_route

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline import (
    upload_intake,
)

from backend.server.stores import upload_document_extractor


print("=== U4.15 STEP 3 - DEPENDENCY ISOLATION ===")

surfaces = {
    "files_route": inspect.getsource(files_route),
    "upload_intake": inspect.getsource(upload_intake),
    "upload_document_extractor": inspect.getsource(
        upload_document_extractor
    ),
}

forbidden_terms = [
    # Website-only cleaning / acquisition
    "article_body_cleaning_engine",
    "article_cleaning_pipeline",
    "enterprise_raw_html_acquisition_engine",
    "raw_website_html_fetch_runner",

    # Deferred U5 Format Router
    "format_router",
    "route_format",
    "dispatch_format",

    # Linking / semantic / runtime systems
    "scorer.py",
    "from backend.server.stores.scorer",
    "semantic_runtime",
    "runtime_reader",
    "recommendation",

    # UUCD must not be wired into U4 detection
    "uucd_engine_v1",
    "uucd_persistence_v1",
    "universal_unified_content_document_v2",
]

failures = []

for surface_name, source in surfaces.items():
    lower = source.lower()

    for term in forbidden_terms:
        present = term.lower() in lower
        status = "FAIL" if present else "PASS"

        label = (
            surface_name.upper()
            + "_NO_"
            + term
            .replace(".", "_")
            .replace("/", "_")
            .replace(" ", "_")
            .upper()
        )

        print(f"{label}: {status}")

        if present:
            failures.append(
                f"{surface_name}: {term}"
            )

print()
print("========================================")

if failures:
    print(
        "U4.15_STEP3_DEPENDENCY_ISOLATION: FAIL"
    )

    print("FAILED_DEPENDENCIES:")
    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U4.15 dependency isolation failed."
    )

print(
    "U4.15_STEP3_DEPENDENCY_ISOLATION: PASS"
)