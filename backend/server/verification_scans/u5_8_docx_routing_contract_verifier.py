from __future__ import annotations

import inspect
from pathlib import Path
from tempfile import TemporaryDirectory

import backend.server.stores.upload_document_extractor as extractor


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U5.8 - DOCX ROUTING CONTRACT ===")


router = extractor.detect_upload_source_type

dispatcher_source = inspect.getsource(
    extractor.extract_upload_document_v1
)

docx_source = inspect.getsource(
    extractor.extract_docx_upload_v1
).lower()

router_source = inspect.getsource(
    extractor.detect_upload_source_type
).lower()

module_source = inspect.getsource(
    extractor
).lower()


# ------------------------------------------------------------
# A. Physical extension -> logical family
# ------------------------------------------------------------

print()
print("=== A. DOCX ROUTING MAP ===")

check(
    "DOCX_IS_CANONICAL_SUPPORTED_EXTENSION",
    extractor.SUPPORTED_UPLOAD_EXTENSIONS.get(".docx")
    == "docx",
)

check(
    "LOWERCASE_DOCX_ROUTES_DOCX",
    router("document.docx") == "docx",
)

check(
    "UPPERCASE_DOCX_ROUTES_DOCX",
    router("DOCUMENT.DOCX") == "docx",
)

check(
    "MIXED_CASE_DOCX_ROUTES_DOCX",
    router("document.DoCx") == "docx",
)

check(
    "DOCX_DOES_NOT_ROUTE_TXT",
    router("document.docx") != "txt",
)

check(
    "DOCX_DOES_NOT_ROUTE_MARKDOWN",
    router("document.docx") != "markdown",
)

check(
    "DOCX_DOES_NOT_ROUTE_HTML",
    router("document.docx") != "html",
)


# ------------------------------------------------------------
# B. Determinism
# ------------------------------------------------------------

print()
print("=== B. DOCX ROUTING DETERMINISM ===")

first = router("document.docx")

check(
    "DOCX_ROUTING_DETERMINISTIC",
    all(
        router("document.docx") == first
        for _ in range(20)
    ),
)


# ------------------------------------------------------------
# C. Final-suffix authority
# ------------------------------------------------------------

print()
print("=== C. DOCX FINAL-SUFFIX AUTHORITY ===")

check(
    "DOCX_ZIP_IS_UNSUPPORTED",
    router("document.docx.zip") == "unsupported",
)

check(
    "DOCX_EXE_IS_UNSUPPORTED",
    router("document.docx.exe") == "unsupported",
)

check(
    "PDF_DOCX_FINAL_SUFFIX_ROUTES_DOCX",
    router("document.pdf.docx") == "docx",
)


# ------------------------------------------------------------
# D. Dispatcher contract
# ------------------------------------------------------------

print()
print("=== D. DOCX DISPATCHER CONTRACT ===")

check(
    "DOCX_FAMILY_DISPATCHES_TO_DOCX_EXTRACTOR",
    'source_type == "docx"' in dispatcher_source
    and "extract_docx_upload_v1" in dispatcher_source,
)

docx_branch_start = dispatcher_source.find(
    'if source_type == "docx":'
)

unsupported_start = dispatcher_source.find(
    "result = build_empty_upload_result",
    docx_branch_start,
)

docx_branch = dispatcher_source[
    docx_branch_start:unsupported_start
]

check(
    "DOCX_BRANCH_DOES_NOT_CALL_TXT_EXTRACTOR",
    "extract_txt_upload_v1" not in docx_branch,
)

check(
    "DOCX_BRANCH_DOES_NOT_CALL_MARKDOWN_EXTRACTOR",
    "extract_markdown_upload_v1" not in docx_branch,
)

check(
    "DOCX_BRANCH_DOES_NOT_CALL_HTML_EXTRACTOR",
    "extract_html_upload_v1" not in docx_branch,
)


# ------------------------------------------------------------
# E. DOCX extractor defensive extension guard
# ------------------------------------------------------------

print()
print("=== E. DOCX EXTRACTOR DEFENSIVE GUARD ===")

check(
    "DOCX_EXTRACTOR_REQUIRES_DOT_DOCX",
    'p.suffix.lower() != ".docx"' in docx_source,
)

check(
    "DOCX_EXTRACTOR_HAS_UNSUPPORTED_EXTENSION_RESULT",
    "unsupported_extension" in docx_source,
)


# ------------------------------------------------------------
# F. Direct extractor behavior
# ------------------------------------------------------------

print()
print("=== F. DIRECT DOCX EXTRACTOR BEHAVIOR ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    wrong_path = root / "sample.txt"
    wrong_path.write_text(
        "Not a DOCX file",
        encoding="utf-8",
    )

    wrong_result = extractor.extract_docx_upload_v1(
        wrong_path
    )

    check(
        "DOCX_EXTRACTOR_REJECTS_NON_DOCX",
        wrong_result.extraction_status
        == "unsupported_extension",
    )


# ------------------------------------------------------------
# G. Routing authority isolation
# ------------------------------------------------------------

print()
print("=== G. DOCX ROUTING AUTHORITY ISOLATION ===")

check(
    "DOCX_ROUTING_DOES_NOT_USE_MIME",
    "mime" not in router_source,
)

check(
    "DOCX_ROUTING_DOES_NOT_USE_CONTENT_TYPE",
    "content_type" not in router_source,
)

check(
    "DOCX_ROUTING_DOES_NOT_READ_FILE_BYTES",
    ".read(" not in router_source
    and "read_bytes" not in router_source,
)

check(
    "DOCX_ROUTING_DOES_NOT_USE_MAGIC",
    "magic" not in router_source,
)

check(
    "DOCX_ROUTING_DOES_NOT_USE_SIGNATURE_AUTHORITY",
    "file_signature" not in router_source
    and "content_signature" not in router_source
    and "signature_bytes" not in router_source
    and "detect_signature" not in router_source,
)

check(
    "DOCX_ZIP_CONTAINER_SIGNATURE_NOT_ROUTING_AUTHORITY",
    "zipfile" not in router_source
    and "pk\x03\x04" not in router_source,
)


# ------------------------------------------------------------
# H. Frontend independence
# ------------------------------------------------------------

print()
print("=== H. FRONTEND / BACKEND SEPARATION ===")

check(
    "BACKEND_DOCX_ROUTER_HAS_NO_FRONTEND_STATE",
    "canonicalsessionformat" not in router_source
    and "frontend" not in router_source,
)


# ------------------------------------------------------------
# I. Unrelated-system isolation
# ------------------------------------------------------------

print()
print("=== I. DOCX ROUTING SYSTEM ISOLATION ===")

check(
    "NO_WEBSITE_ROUTING_IN_DOCX_CONTRACT",
    "article_body_cleaning_engine" not in module_source
    and "article_cleaning_pipeline" not in module_source,
)

check(
    "NO_URL_IMPORT_ROUTING_IN_DOCX_CONTRACT",
    "/api/urls/import" not in module_source,
)

check(
    "NO_DRAFT_IMPORT_ROUTING_IN_DOCX_CONTRACT",
    "/api/draft/import" not in module_source,
)

check(
    "NO_UDUC_IN_ROUTER_FUNCTION",
    "uduc" not in router_source,
)

check(
    "NO_HIGHLIGHT_IN_ROUTER_FUNCTION",
    "highlight" not in router_source,
)

check(
    "NO_ACTIVE_TARGET_SET_IN_ROUTER_FUNCTION",
    "active_target" not in router_source,
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
        "U5.8_DOCX_ROUTING_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.8 DOCX routing contract verification failed."
    )

print(
    "U5.8_DOCX_ROUTING_CONTRACT: CERTIFIED"
)

print(
    "U5.8_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U5.9_PHYSICAL_ALIAS_PRESERVATION_TRANSITION: AUTHORIZED"
)

print(
    "U5.8_FINAL_DOCX_ROUTING_VERIFICATION: PASS"
)