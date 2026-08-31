from __future__ import annotations

import inspect

import backend.server.stores.upload_document_extractor as extractor

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline import (
    upload_intake,
)


print("=== U5.2 STEP 1 - ROUTER RESPONSIBILITY INSPECTION ===")
print()

print("=== CURRENT ROUTING TABLE ===")
print(extractor.SUPPORTED_UPLOAD_EXTENSIONS)

print()
print("=== detect_upload_source_type ===")
print(inspect.getsource(extractor.detect_upload_source_type))

print()
print("=== extract_upload_document_v1 ===")
print(inspect.getsource(extractor.extract_upload_document_v1))

print()
print("=== FORMAT-SPECIFIC EXTRACTOR ENTRY POINTS ===")

for name in [
    "extract_txt_upload_v1",
    "extract_markdown_upload_v1",
    "extract_html_upload_v1",
    "extract_docx_upload_v1",
]:
    obj = getattr(extractor, name)
    print(f"{name}{inspect.signature(obj)}")

print()
print("=== INTAKE CALL SITE ===")

source = inspect.getsource(
    upload_intake.run_upload_intake
)

for i, line in enumerate(source.splitlines(), 1):
    if (
        "extract_upload_document_v1" in line
        or "extension =" in line
        or "allowed_extensions" in line
    ):
        print(f"{i}: {line}")

print()
print("=== RESPONSIBILITY SIGNALS ===")

router_source = (
    inspect.getsource(extractor.detect_upload_source_type)
    + "\n"
    + inspect.getsource(extractor.extract_upload_document_v1)
).lower()

signals = {
    "ROUTER_MAPS_EXTENSION_TO_FAMILY":
        "supported_upload_extensions" in router_source,

    "ROUTER_DISPATCHES_TO_EXTRACTORS":
        "extract_txt_upload_v1" in router_source
        and "extract_markdown_upload_v1" in router_source
        and "extract_html_upload_v1" in router_source
        and "extract_docx_upload_v1" in router_source,

    "ROUTER_DOES_NOT_PERSIST":
        "write_" not in router_source
        and "store_" not in router_source
        and "persist" not in router_source,

    "ROUTER_DOES_NOT_BUILD_UDUC":
        "uduc" not in router_source,

    "ROUTER_DOES_NOT_USE_MIME":
        "mime" not in router_source
        and "content_type" not in router_source,

    "ROUTER_DOES_NOT_USE_MAGIC":
        "magic" not in router_source,

    "ROUTER_DOES_NOT_USE_SIGNATURE_AUTHORITY":
        "file_signature" not in router_source
        and "content_signature" not in router_source
        and "signature_bytes" not in router_source
        and "detect_signature" not in router_source,

    "ROUTER_DOES_NOT_NORMALIZE_CONTENT":
        "normalize" not in router_source,

    "ROUTER_DOES_NOT_INVOKE_HIGHLIGHT":
        "highlight" not in router_source,

    "ROUTER_DOES_NOT_INVOKE_ACTIVE_TARGET_SET":
        "active_target" not in router_source,

    "ROUTER_DOES_NOT_INVOKE_SCORER":
        "scorer" not in router_source,

    "ROUTER_DOES_NOT_INVOKE_SEMANTIC_RUNTIME":
        "semantic_runtime" not in router_source
        and "runtime_reader" not in router_source,
}

failures = []

for name, condition in signals.items():
    status = "PASS" if condition else "FAIL"
    print(f"{name}: {status}")

    if not condition:
        failures.append(name)

print()
print("========================================")

if failures:
    print("U5.2_STEP1_ROUTER_RESPONSIBILITY_INSPECTION: FAIL")
    print("FAILED_SIGNALS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.2 router responsibility inspection failed."
    )

print(
    "U5.2_STEP1_ROUTER_RESPONSIBILITY_INSPECTION: PASS"
)