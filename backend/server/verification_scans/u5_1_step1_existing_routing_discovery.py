from __future__ import annotations

import inspect

import backend.server.stores.upload_document_extractor as extractor
import backend.server.routes.files as files_route

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline import (
    upload_intake,
)


print("=== U5.1 STEP 1 - EXISTING ROUTING DISCOVERY ===")
print()

print("=== SUPPORTED_UPLOAD_EXTENSIONS ===")
print(extractor.SUPPORTED_UPLOAD_EXTENSIONS)

print()
print("=== DETECTOR / ROUTER-LIKE FUNCTIONS ===")

for name in [
    "_detect_upload_type",
    "detect_upload_type",
    "route_upload_format",
    "route_format",
    "dispatch_format",
    "extract_upload_document_v1",
]:
    obj = getattr(extractor, name, None)

    if obj is not None:
        print(f"FOUND: {name}")
        try:
            print(inspect.getsource(obj))
        except Exception:
            print(repr(obj))
        print()

print("=== UPLOAD EXTRACTOR ROUTING-RELATED LINES ===")

source = inspect.getsource(extractor)

terms = [
    "SUPPORTED_UPLOAD_EXTENSIONS",
    "suffix.lower",
    "source_type",
    "extract_txt",
    "extract_markdown",
    "extract_html",
    "extract_docx",
    "unsupported",
    "if ",
    "elif ",
]

for i, line in enumerate(source.splitlines(), 1):
    lower = line.lower()

    if any(term.lower() in lower for term in terms):
        if any(
            key in lower
            for key in [
                "supported_upload_extensions",
                "suffix.lower",
                "extract_",
                "unsupported",
                "source_type",
            ]
        ):
            print(f"{i}: {line}")

print()
print("=== UPLOAD INTAKE ROUTING-RELATED LINES ===")

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
)

for i, line in enumerate(intake_source.splitlines(), 1):
    if any(
        term in line
        for term in [
            "guess_extension",
            "allowed_extensions",
            "extract_upload_document_v1",
            "extension",
        ]
    ):
        print(f"{i}: {line}")

print()
print("=== FILES ROUTE ROUTING-RELATED LINES ===")

route_source = inspect.getsource(files_route.upload_file)

for i, line in enumerate(route_source.splitlines(), 1):
    if any(
        term in line
        for term in [
            "guess_extension",
            "allowed_extensions",
            "run_upload_document",
        ]
    ):
        print(f"{i}: {line}")

print()
print("U5.1_STEP1_EXISTING_ROUTING_DISCOVERY: PASS")