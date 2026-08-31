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


print("=== U5.5 - TXT ROUTING CONTRACT ===")


router = extractor.detect_upload_source_type
dispatcher_source = inspect.getsource(
    extractor.extract_upload_document_v1
)
txt_source = inspect.getsource(
    extractor.extract_txt_upload_v1
).lower()
module_source = inspect.getsource(extractor).lower()


# ------------------------------------------------------------
# A. Physical extension -> logical family
# ------------------------------------------------------------

print()
print("=== A. TXT ROUTING MAP ===")

check(
    "TXT_IS_CANONICAL_SUPPORTED_EXTENSION",
    extractor.SUPPORTED_UPLOAD_EXTENSIONS.get(".txt") == "txt",
)

check(
    "LOWERCASE_TXT_ROUTES_TO_TXT",
    router("document.txt") == "txt",
)

check(
    "UPPERCASE_TXT_ROUTES_TO_TXT",
    router("document.TXT") == "txt",
)

check(
    "TXT_DOES_NOT_ROUTE_MARKDOWN",
    router("document.txt") != "markdown",
)

check(
    "TXT_DOES_NOT_ROUTE_HTML",
    router("document.txt") != "html",
)

check(
    "TXT_DOES_NOT_ROUTE_DOCX",
    router("document.txt") != "docx",
)


# ------------------------------------------------------------
# B. Determinism
# ------------------------------------------------------------

print()
print("=== B. TXT ROUTING DETERMINISM ===")

first = router("document.txt")

check(
    "TXT_ROUTING_DETERMINISTIC",
    all(
        router("document.txt") == first
        for _ in range(20)
    ),
)


# ------------------------------------------------------------
# C. Dispatcher contract
# ------------------------------------------------------------

print()
print("=== C. TXT DISPATCHER CONTRACT ===")

check(
    "TXT_FAMILY_DISPATCHES_TO_TXT_EXTRACTOR",
    'source_type == "txt"' in dispatcher_source
    and "extract_txt_upload_v1" in dispatcher_source,
)

txt_branch_start = dispatcher_source.find(
    'if source_type == "txt":'
)

markdown_branch_start = dispatcher_source.find(
    'if source_type == "markdown":'
)

txt_branch = dispatcher_source[
    txt_branch_start:markdown_branch_start
]

check(
    "TXT_BRANCH_DOES_NOT_CALL_MARKDOWN_EXTRACTOR",
    "extract_markdown_upload_v1" not in txt_branch,
)

check(
    "TXT_BRANCH_DOES_NOT_CALL_HTML_EXTRACTOR",
    "extract_html_upload_v1" not in txt_branch,
)

check(
    "TXT_BRANCH_DOES_NOT_CALL_DOCX_EXTRACTOR",
    "extract_docx_upload_v1" not in txt_branch,
)


# ------------------------------------------------------------
# D. TXT extractor defensive extension guard
# ------------------------------------------------------------

print()
print("=== D. TXT EXTRACTOR DEFENSIVE GUARD ===")

check(
    "TXT_EXTRACTOR_REQUIRES_DOT_TXT",
    'p.suffix.lower() != ".txt"' in txt_source,
)

check(
    "TXT_EXTRACTOR_HAS_UNSUPPORTED_EXTENSION_RESULT",
    "unsupported_extension" in txt_source,
)


# ------------------------------------------------------------
# E. Direct extractor behavior
# ------------------------------------------------------------

print()
print("=== E. DIRECT TXT EXTRACTOR BEHAVIOR ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    txt_path = root / "sample.txt"
    txt_path.write_text(
        "First paragraph.\n\nSecond paragraph.",
        encoding="utf-8",
    )

    txt_result = extractor.extract_txt_upload_v1(
        txt_path
    )

    check(
        "TXT_EXTRACTOR_ACCEPTS_TXT",
        txt_result.source_type == "txt"
        and txt_result.extraction_status != "unsupported_extension",
    )

    wrong_path = root / "sample.md"
    wrong_path.write_text(
        "Plain text content",
        encoding="utf-8",
    )

    wrong_result = extractor.extract_txt_upload_v1(
        wrong_path
    )

    check(
        "TXT_EXTRACTOR_REJECTS_NON_TXT",
        wrong_result.extraction_status == "unsupported_extension",
    )


# ------------------------------------------------------------
# F. Routing authority isolation
# ------------------------------------------------------------

print()
print("=== F. TXT ROUTING AUTHORITY ISOLATION ===")

router_source = inspect.getsource(
    extractor.detect_upload_source_type
).lower()

check(
    "TXT_ROUTING_DOES_NOT_USE_MIME",
    "mime" not in router_source,
)

check(
    "TXT_ROUTING_DOES_NOT_USE_CONTENT_TYPE",
    "content_type" not in router_source,
)

check(
    "TXT_ROUTING_DOES_NOT_READ_FILE_BYTES",
    ".read(" not in router_source
    and "read_bytes" not in router_source,
)

check(
    "TXT_ROUTING_DOES_NOT_USE_MAGIC",
    "magic" not in router_source,
)

check(
    "TXT_ROUTING_DOES_NOT_USE_SIGNATURE_AUTHORITY",
    "file_signature" not in router_source
    and "content_signature" not in router_source
    and "signature_bytes" not in router_source
    and "detect_signature" not in router_source,
)


# ------------------------------------------------------------
# G. Unrelated-system isolation
# ------------------------------------------------------------

print()
print("=== G. TXT ROUTING SYSTEM ISOLATION ===")

check(
    "NO_WEBSITE_ROUTING_IN_TXT_CONTRACT",
    "article_body_cleaning_engine" not in module_source
    and "article_cleaning_pipeline" not in module_source,
)

check(
    "NO_URL_IMPORT_ROUTING_IN_TXT_CONTRACT",
    "/api/urls/import" not in module_source,
)

check(
    "NO_DRAFT_IMPORT_ROUTING_IN_TXT_CONTRACT",
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
        "U5.5_TXT_ROUTING_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.5 TXT routing contract verification failed."
    )

print(
    "U5.5_TXT_ROUTING_CONTRACT: CERTIFIED"
)

print(
    "U5.5_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U5.6_MARKDOWN_ROUTING_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U5.5_FINAL_TXT_ROUTING_VERIFICATION: PASS"
)