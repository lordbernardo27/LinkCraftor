from __future__ import annotations

import inspect
from pathlib import Path

import backend.server.stores.upload_document_extractor as extractor


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U5.3 - ROUTER INPUT CONTRACT ===")


router = extractor.detect_upload_source_type
router_source = inspect.getsource(router).lower()
signature = inspect.signature(router)


# ------------------------------------------------------------
# A. Function input surface
# ------------------------------------------------------------

print()
print("=== A. INPUT SURFACE ===")

params = list(signature.parameters.values())

check(
    "ROUTER_HAS_ONE_INPUT_PARAMETER",
    len(params) == 1,
)

check(
    "ROUTER_ACCEPTS_PATH_CONTEXT",
    len(params) == 1
    and params[0].name == "path",
)

check(
    "ROUTER_HAS_NO_UPLOADFILE_PARAMETER",
    "uploadfile" not in str(signature).lower(),
)

check(
    "ROUTER_HAS_NO_WORKSPACE_PARAMETER",
    "workspace" not in str(signature).lower(),
)

check(
    "ROUTER_HAS_NO_REQUEST_PARAMETER",
    "request" not in str(signature).lower(),
)


# ------------------------------------------------------------
# B. str / Path compatibility
# ------------------------------------------------------------

print()
print("=== B. STR / PATH COMPATIBILITY ===")

check(
    "STRING_PATH_SUPPORTED",
    router("document.txt") == "txt",
)

check(
    "PATH_OBJECT_SUPPORTED",
    router(Path("document.docx")) == "docx",
)


# ------------------------------------------------------------
# C. Physical suffix authority
# ------------------------------------------------------------

print()
print("=== C. PHYSICAL SUFFIX AUTHORITY ===")

check(
    "ROUTER_USES_PATH_SUFFIX",
    ".suffix.lower()" in router_source,
)

check(
    "ROUTER_LOWERCASES_SUFFIX",
    "suffix.lower()" in router_source,
)

check(
    "UPPERCASE_EXTENSION_NORMALIZED",
    router("ARTICLE.DOCX") == "docx",
)

check(
    "FINAL_SUFFIX_CONTROLS_ROUTING",
    router("article.md.exe") == "unsupported",
)

check(
    "DOCX_ZIP_FINAL_SUFFIX_UNSUPPORTED",
    router("article.docx.zip") == "unsupported",
)


# ------------------------------------------------------------
# D. Alias preservation at physical-input level
# ------------------------------------------------------------

print()
print("=== D. PHYSICAL ALIAS INPUT CONTRACT ===")

check(
    "MD_INPUT_ROUTES_MARKDOWN",
    router("document.md") == "markdown",
)

check(
    "MARKDOWN_INPUT_ROUTES_MARKDOWN",
    router("document.markdown") == "markdown",
)

check(
    "HTML_INPUT_ROUTES_HTML",
    router("document.html") == "html",
)

check(
    "HTM_INPUT_ROUTES_HTML",
    router("document.htm") == "html",
)

check(
    "TXT_INPUT_ROUTES_TXT",
    router("document.txt") == "txt",
)

check(
    "DOCX_INPUT_ROUTES_DOCX",
    router("document.docx") == "docx",
)


# ------------------------------------------------------------
# E. Unsupported contract
# ------------------------------------------------------------

print()
print("=== E. UNSUPPORTED INPUT CONTRACT ===")

check(
    "UNSUPPORTED_SUFFIX_RETURNS_EXPLICIT_UNSUPPORTED",
    router("document.pdf") == "unsupported",
)

check(
    "NO_EXTENSION_RETURNS_UNSUPPORTED",
    router("document") == "unsupported",
)

check(
    "TRAILING_DOT_RETURNS_UNSUPPORTED",
    router("document.") == "unsupported",
)


# ------------------------------------------------------------
# F. No non-path routing authority
# ------------------------------------------------------------

print()
print("=== F. NON-PATH AUTHORITY IS ABSENT ===")

check(
    "ROUTER_DOES_NOT_USE_MIME",
    "mime" not in router_source,
)

check(
    "ROUTER_DOES_NOT_USE_CONTENT_TYPE",
    "content_type" not in router_source,
)

check(
    "ROUTER_DOES_NOT_READ_FILE_BYTES",
    ".read(" not in router_source
    and "read_bytes" not in router_source,
)

check(
    "ROUTER_DOES_NOT_USE_MAGIC",
    "magic" not in router_source,
)

check(
    "ROUTER_DOES_NOT_USE_SIGNATURE_DETECTION",
    "file_signature" not in router_source
    and "content_signature" not in router_source
    and "signature_bytes" not in router_source
    and "detect_signature" not in router_source,
)

check(
    "ROUTER_DOES_NOT_SANITIZE_FILENAME",
    "_safe_upload_filename" not in router_source
    and "sanitize" not in router_source,
)


# ------------------------------------------------------------
# G. No downstream-system dependencies
# ------------------------------------------------------------

print()
print("=== G. DOWNSTREAM INDEPENDENCE ===")

check(
    "ROUTER_DOES_NOT_PERSIST",
    "store" not in router_source
    and "write" not in router_source
    and "persist" not in router_source,
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
    "ROUTER_DOES_NOT_USE_ACTIVE_TARGET_SET",
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
        "U5.3_ROUTER_INPUT_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.3 router input contract verification failed."
    )

print(
    "U5.3_ROUTER_INPUT_CONTRACT: CERTIFIED"
)

print(
    "U5.3_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U5.4_ROUTER_OUTPUT_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U5.3_FINAL_INPUT_CONTRACT_VERIFICATION: PASS"
)