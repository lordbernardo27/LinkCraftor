from __future__ import annotations

import inspect
from pathlib import Path

import backend.server.stores.upload_document_extractor as extractor


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U5.4 - ROUTER OUTPUT CONTRACT ===")


router = extractor.detect_upload_source_type
router_source = inspect.getsource(router).lower()


# ------------------------------------------------------------
# A. Canonical output type
# ------------------------------------------------------------

print()
print("=== A. OUTPUT TYPE ===")

samples = [
    "document.txt",
    "document.md",
    "document.markdown",
    "document.html",
    "document.htm",
    "document.docx",
    "document.pdf",
    "document",
]

outputs = [
    router(sample)
    for sample in samples
]

check(
    "ALL_ROUTER_OUTPUTS_ARE_STRINGS",
    all(isinstance(value, str) for value in outputs),
)


# ------------------------------------------------------------
# B. Supported logical families
# ------------------------------------------------------------

print()
print("=== B. SUPPORTED LOGICAL OUTPUTS ===")

expected_supported = {
    "txt",
    "markdown",
    "html",
    "docx",
}

supported_outputs = {
    router("document.txt"),
    router("document.md"),
    router("document.markdown"),
    router("document.html"),
    router("document.htm"),
    router("document.docx"),
}

check(
    "SUPPORTED_OUTPUT_SET_EXACT",
    supported_outputs == expected_supported,
)

check(
    "TXT_OUTPUT_CANONICAL",
    router("document.txt") == "txt",
)

check(
    "MARKDOWN_OUTPUT_CANONICAL",
    router("document.md") == "markdown"
    and router("document.markdown") == "markdown",
)

check(
    "HTML_OUTPUT_CANONICAL",
    router("document.html") == "html"
    and router("document.htm") == "html",
)

check(
    "DOCX_OUTPUT_CANONICAL",
    router("document.docx") == "docx",
)


# ------------------------------------------------------------
# C. Unsupported output contract
# ------------------------------------------------------------

print()
print("=== C. UNSUPPORTED OUTPUT ===")

unsupported_cases = [
    "document.pdf",
    "document.csv",
    "document.xml",
    "document.zip",
    "document.exe",
    "document",
    "document.",
    "document.md.exe",
    "document.docx.zip",
]

check(
    "ALL_UNSUPPORTED_CASES_RETURN_UNSUPPORTED",
    all(
        router(case) == "unsupported"
        for case in unsupported_cases
    ),
)

check(
    "UNSUPPORTED_OUTPUT_IS_STRING",
    isinstance(
        router("document.pdf"),
        str,
    ),
)


# ------------------------------------------------------------
# D. Output semantic purity
# ------------------------------------------------------------

print()
print("=== D. OUTPUT SEMANTIC PURITY ===")

canonical_outputs = [
    router("document.txt"),
    router("document.md"),
    router("document.markdown"),
    router("document.html"),
    router("document.htm"),
    router("document.docx"),
    router("document.pdf"),
]

check(
    "ROUTER_NEVER_RETURNS_PHYSICAL_EXTENSION",
    all(
        not value.startswith(".")
        for value in canonical_outputs
    ),
)

check(
    "ROUTER_NEVER_RETURNS_MIME_VALUE",
    all(
        "/" not in value
        for value in canonical_outputs
    ),
)

check(
    "ROUTER_NEVER_RETURNS_CALLABLE",
    all(
        not callable(value)
        for value in canonical_outputs
    ),
)

check(
    "ROUTER_NEVER_RETURNS_UPLOAD_EXTRACTION_RESULT",
    all(
        not isinstance(
            value,
            extractor.UploadExtractionResult,
        )
        for value in canonical_outputs
    ),
)


# ------------------------------------------------------------
# E. Alias-collapse contract
# ------------------------------------------------------------

print()
print("=== E. ALIAS COLLAPSE ===")

check(
    "MD_AND_MARKDOWN_COLLAPSE_TO_ONE_FAMILY",
    router("document.md")
    == router("document.markdown")
    == "markdown",
)

check(
    "HTML_AND_HTM_COLLAPSE_TO_ONE_FAMILY",
    router("document.html")
    == router("document.htm")
    == "html",
)


# ------------------------------------------------------------
# F. Determinism
# ------------------------------------------------------------

print()
print("=== F. OUTPUT DETERMINISM ===")

determinism_cases = [
    "document.txt",
    "document.md",
    "document.markdown",
    "document.html",
    "document.htm",
    "document.docx",
    "document.pdf",
]

deterministic = True

for case in determinism_cases:
    first = router(case)

    for _ in range(10):
        if router(case) != first:
            deterministic = False
            break

check(
    "OUTPUT_DETERMINISTIC_FOR_SAME_INPUT",
    deterministic,
)


# ------------------------------------------------------------
# G. Case normalization
# ------------------------------------------------------------

print()
print("=== G. CASE NORMALIZATION ===")

check(
    "UPPERCASE_TXT_RETURNS_TXT",
    router("DOCUMENT.TXT") == "txt",
)

check(
    "UPPERCASE_MARKDOWN_RETURNS_MARKDOWN",
    router("DOCUMENT.MARKDOWN") == "markdown",
)

check(
    "UPPERCASE_HTML_RETURNS_HTML",
    router("DOCUMENT.HTML") == "html",
)

check(
    "UPPERCASE_DOCX_RETURNS_DOCX",
    router("DOCUMENT.DOCX") == "docx",
)


# ------------------------------------------------------------
# H. No downstream-object output
# ------------------------------------------------------------

print()
print("=== H. DOWNSTREAM OBJECT EXCLUSION ===")

check(
    "ROUTER_SOURCE_DOES_NOT_BUILD_UDUC",
    "uduc" not in router_source,
)

check(
    "ROUTER_SOURCE_DOES_NOT_BUILD_METADATA_OBJECT",
    "metadata" not in router_source,
)

check(
    "ROUTER_SOURCE_DOES_NOT_INVOKE_EXTRACTOR_FUNCTION",
    "extract_" not in router_source,
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
        "U5.4_ROUTER_OUTPUT_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.4 router output contract verification failed."
    )

print(
    "U5.4_ROUTER_OUTPUT_CONTRACT: CERTIFIED"
)

print(
    "U5.4_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U5.5_TXT_ROUTING_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U5.4_FINAL_OUTPUT_CONTRACT_VERIFICATION: PASS"
)