from __future__ import annotations

import inspect

import backend.server.routes.files as files_route
import backend.server.stores.upload_document_extractor as extractor

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake import (
    UploadIntakeDependencies,
    run_upload_intake,
)

from backend.server.pipelines.upload_document.coordinator import (
    run_upload_document,
)


print("=== U4.15 STEP 1 - IMPORT / INTEGRATION SURFACE ===")
print()

print("FILES_ROUTE_IMPORT: PASS")
print("UPLOAD_EXTRACTOR_IMPORT: PASS")
print("UPLOAD_INTAKE_IMPORT: PASS")
print("UPLOAD_COORDINATOR_IMPORT: PASS")

print()
print("=== CANONICAL SYMBOLS ===")

print(
    "ALLOWED_EXT:",
    sorted(files_route.ALLOWED_EXT),
)

print(
    "SUPPORTED_UPLOAD_EXTENSIONS:",
    sorted(extractor.SUPPORTED_UPLOAD_EXTENSIONS.keys()),
)

print(
    "_guess_ext('ARTICLE.DOCX'):",
    files_route._guess_ext("ARTICLE.DOCX"),
)

print(
    "UploadIntakeDependencies:",
    inspect.signature(UploadIntakeDependencies),
)

print(
    "run_upload_intake:",
    inspect.signature(run_upload_intake),
)

print(
    "run_upload_document:",
    inspect.signature(run_upload_document),
)

print()
print("=== ROUTE REGISTRATION ===")

route_hits = []

for route in files_route.router.routes:
    path = getattr(route, "path", "")
    methods = sorted(getattr(route, "methods", set()) or set())

    if path == "/api/files/upload":
        route_hits.append((path, methods))
        print(
            f"FOUND_ROUTE: path={path!r} methods={methods}"
        )

assert route_hits, "Canonical /upload route not registered."

assert any(
    "POST" in methods
    for _, methods in route_hits
), "Canonical /upload route is not POST."

print()
print("U4.15_STEP1_IMPORT_INTEGRATION: PASS")