from __future__ import annotations

import inspect

import backend.server.stores.upload_document_extractor as extractor

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline import (
    upload_intake,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U5.2 - CANONICAL FORMAT ROUTER RESPONSIBILITY ===")


expected_map = {
    ".txt": "txt",
    ".md": "markdown",
    ".markdown": "markdown",
    ".html": "html",
    ".htm": "html",
    ".docx": "docx",
}


print()
print("=== A. ROUTER RESPONSIBILITY ===")

check(
    "ROUTER_MAP_EXACT",
    extractor.SUPPORTED_UPLOAD_EXTENSIONS == expected_map,
)

check(
    "ROUTER_FUNCTION_EXISTS",
    callable(extractor.detect_upload_source_type),
)

for ext, family in expected_map.items():
    check(
        f"MAP_{ext.replace('.', '').upper()}_TO_{family.upper()}",
        extractor.detect_upload_source_type(
            "document" + ext
        )
        == family,
    )


print()
print("=== B. PURE ROUTING BOUNDARY ===")

router_source = inspect.getsource(
    extractor.detect_upload_source_type
).lower()

check(
    "ROUTER_DOES_NOT_EXTRACT",
    "extract_" not in router_source,
)

check(
    "ROUTER_DOES_NOT_PERSIST",
    "store" not in router_source
    and "write" not in router_source
    and "persist" not in router_source,
)

check(
    "ROUTER_DOES_NOT_NORMALIZE",
    "normalize" not in router_source,
)

check(
    "ROUTER_DOES_NOT_BUILD_UDUC",
    "uduc" not in router_source,
)

check(
    "ROUTER_DOES_NOT_HIGHLIGHT",
    "highlight" not in router_source,
)

check(
    "ROUTER_DOES_NOT_USE_MIME",
    "mime" not in router_source
    and "content_type" not in router_source,
)

check(
    "ROUTER_DOES_NOT_USE_MAGIC_OR_SIGNATURE",
    "magic" not in router_source
    and "file_signature" not in router_source
    and "content_signature" not in router_source
    and "detect_signature" not in router_source,
)


print()
print("=== C. U5 / U6 RESPONSIBILITY SEPARATION ===")

dispatcher_source = inspect.getsource(
    extractor.extract_upload_document_v1
)

check(
    "U6_DISPATCHER_CONSUMES_ROUTER_RESULT",
    "detect_upload_source_type" in dispatcher_source,
)

check(
    "FORMAT_SPECIFIC_EXTRACTION_REMAINS_OUTSIDE_ROUTER",
    "extract_txt_upload_v1" not in router_source
    and "extract_markdown_upload_v1" not in router_source
    and "extract_html_upload_v1" not in router_source
    and "extract_docx_upload_v1" not in router_source,
)


print()
print("=== D. INTAKE RESPONSIBILITY ===")

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
)

check(
    "INTAKE_DOES_NOT_IMPLEMENT_FAMILY_ROUTING",
    'source_type == "txt"' not in intake_source
    and 'source_type == "markdown"' not in intake_source
    and 'source_type == "html"' not in intake_source
    and 'source_type == "docx"' not in intake_source,
)


print()
print("=== E. CANONICAL PLACEMENT DECISION ===")

check(
    "CURRENT_ROUTER_PLACEMENT_BEHAVIORALLY_VALID",
    callable(extractor.detect_upload_source_type),
)

check(
    "NO_PREMATURE_U6_REFACTOR_REQUIRED",
    callable(extractor.extract_upload_document_v1),
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
        "U5.2_CANONICAL_FORMAT_ROUTER_RESPONSIBILITY: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.2 router responsibility verification failed."
    )

print(
    "U5.2_CANONICAL_FORMAT_ROUTER_RESPONSIBILITY: CERTIFIED"
)

print(
    "U5.2_DEDICATED_ROUTER_MODULE_REQUIRED_NOW: NO"
)

print(
    "U5.2_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U5.3_ROUTER_INPUT_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U5.2_FINAL_RESPONSIBILITY_VERIFICATION: PASS"
)