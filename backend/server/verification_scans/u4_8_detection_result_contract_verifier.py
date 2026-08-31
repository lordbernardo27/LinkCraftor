from __future__ import annotations

import inspect
from pathlib import Path

import backend.server.routes.files as files_route

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline import (
    upload_intake,
)

import backend.server.stores.upload_document_extractor as extractor


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U4.8 - DETECTION RESULT CONTRACT ===")


# ------------------------------------------------------------
# A. Canonical result type
# ------------------------------------------------------------

print()
print("=== A. RESULT TYPE ===")

guess_signature = inspect.signature(
    files_route._guess_ext
)

guess_source = inspect.getsource(
    files_route._guess_ext
)

return_annotation = guess_signature.return_annotation

check(
    "DETECTOR_RETURN_ANNOTATION_IS_STR",
    return_annotation is str
    or return_annotation == "str",
)

sample_result = files_route._guess_ext(
    "article.DOCX"
)

check(
    "DETECTION_RESULT_RUNTIME_TYPE_IS_STR",
    isinstance(sample_result, str),
)

check(
    "DETECTION_RESULT_IS_NOT_STRUCTURED_OBJECT",
    not isinstance(sample_result, (dict, list, tuple, set)),
)


# ------------------------------------------------------------
# B. Canonical lowercase physical extension output
# ------------------------------------------------------------

print()
print("=== B. CANONICAL PHYSICAL EXTENSION OUTPUT ===")

supported_samples = {
    "article.txt": ".txt",
    "article.md": ".md",
    "article.markdown": ".markdown",
    "article.html": ".html",
    "article.htm": ".htm",
    "article.docx": ".docx",
    "ARTICLE.TXT": ".txt",
    "ARTICLE.MD": ".md",
    "ARTICLE.MARKDOWN": ".markdown",
    "ARTICLE.HTML": ".html",
    "ARTICLE.HTM": ".htm",
    "ARTICLE.DOCX": ".docx",
}

for filename, expected in supported_samples.items():
    label = (
        filename
        .replace(".", "_")
        .upper()
    )

    detected = files_route._guess_ext(
        filename
    )

    check(
        f"RESULT_{label}_MATCHES_PHYSICAL_EXTENSION",
        detected == expected,
    )

    check(
        f"RESULT_{label}_HAS_LEADING_DOT",
        detected.startswith("."),
    )

    check(
        f"RESULT_{label}_IS_LOWERCASE",
        detected == detected.lower(),
    )


# ------------------------------------------------------------
# C. Physical alias preservation
# ------------------------------------------------------------

print()
print("=== C. PHYSICAL ALIAS RESULT PRESERVATION ===")

check(
    "RESULT_MARKDOWN_REMAINS_MARKDOWN",
    files_route._guess_ext(
        "article.markdown"
    )
    == ".markdown",
)

check(
    "RESULT_HTM_REMAINS_HTM",
    files_route._guess_ext(
        "article.htm"
    )
    == ".htm",
)

check(
    "RESULT_MARKDOWN_NOT_SESSION_MD",
    files_route._guess_ext(
        "article.markdown"
    )
    != ".md",
)

check(
    "RESULT_HTM_NOT_SESSION_HTML",
    files_route._guess_ext(
        "article.htm"
    )
    != ".html",
)


# ------------------------------------------------------------
# D. Unsupported physical suffix is still detected
# ------------------------------------------------------------

print()
print("=== D. UNSUPPORTED PHYSICAL SUFFIX RESULTS ===")

unsupported_samples = {
    "report.pdf": ".pdf",
    "report.exe": ".exe",
    "report.zip": ".zip",
    "report.csv": ".csv",
    "report.xml": ".xml",
}

for filename, expected in unsupported_samples.items():
    label = (
        filename
        .replace(".", "_")
        .upper()
    )

    detected = files_route._guess_ext(
        filename
    )

    check(
        f"UNSUPPORTED_RESULT_{label}_STILL_DETECTED",
        detected == expected,
    )

    check(
        f"UNSUPPORTED_RESULT_{label}_NOT_ALLOWED",
        detected not in files_route.ALLOWED_EXT,
    )


# ------------------------------------------------------------
# E. No-extension / blank filename behavior
# ------------------------------------------------------------

print()
print("=== E. NO-EXTENSION / BLANK CONTRACT ===")

check(
    "NO_EXTENSION_RESULT_IS_EMPTY_STRING",
    files_route._guess_ext(
        "document"
    )
    == "",
)


def raises_value_error(filename: str) -> bool:
    try:
        files_route._guess_ext(filename)
    except ValueError:
        return True
    return False


check(
    "BLANK_FILENAME_PRODUCES_NO_RESULT",
    raises_value_error(""),
)

check(
    "WHITESPACE_FILENAME_PRODUCES_NO_RESULT",
    raises_value_error("   "),
)


# ------------------------------------------------------------
# F. Determinism
# ------------------------------------------------------------

print()
print("=== F. DETERMINISM ===")

determinism_samples = [
    "article.md",
    "article.markdown",
    "article.HTML",
    "article.htm",
    "article.DOCX",
    "report.pdf",
    "report.md.exe",
    "document",
]

for filename in determinism_samples:
    first = files_route._guess_ext(
        filename
    )

    second = files_route._guess_ext(
        filename
    )

    label = (
        filename
        .replace(".", "_")
        .upper()
    )

    check(
        f"DETERMINISTIC_RESULT_{label}",
        first == second,
    )


# ------------------------------------------------------------
# G. Independent of MIME / bytes / extractor
# ------------------------------------------------------------

print()
print("=== G. RESULT INDEPENDENCE ===")

check(
    "RESULT_CONTRACT_HAS_NO_CONTENT_TYPE_INPUT",
    "content_type"
    not in guess_signature.parameters,
)

check(
    "RESULT_CONTRACT_HAS_NO_MIME_INPUT",
    "mime"
    not in guess_signature.parameters
    and "mimetype"
    not in guess_signature.parameters,
)

check(
    "RESULT_CONTRACT_HAS_NO_BYTES_INPUT",
    "bytes"
    not in guess_signature.parameters,
)

check(
    "RESULT_DETECTOR_SOURCE_HAS_NO_EXTRACTOR_CALL",
    "extract"
    not in guess_source.lower(),
)


# ------------------------------------------------------------
# H. Result is not another abstraction
# ------------------------------------------------------------

print()
print("=== H. RESULT SEMANTIC BOUNDARY ===")

for forbidden in [
    "text/plain",
    "text/html",
    "application/",
    "markdown_family",
    "html_family",
    "docx_family",
    "session_format",
    "format_router",
    "route_format",
    "dispatch",
    "uduc",
    "stored_name",
    "document_id",
]:
    check(
        "RESULT_NOT_"
        + (
            forbidden
            .replace("/", "_")
            .replace("_", "")
            .upper()
        ),
        forbidden.lower()
        not in sample_result.lower(),
    )


# ------------------------------------------------------------
# I. Direct compatibility with ALLOWED_EXT
# ------------------------------------------------------------

print()
print("=== I. ACCEPTANCE COMPATIBILITY ===")

for ext in [
    ".txt",
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".docx",
]:
    filename = "sample" + ext

    detected = files_route._guess_ext(
        filename
    )

    check(
        "RESULT_DIRECTLY_CHECKABLE_"
        + ext.replace(".", "").upper(),
        detected in files_route.ALLOWED_EXT,
    )


# ------------------------------------------------------------
# J. Downstream preservation evidence
# ------------------------------------------------------------

print()
print("=== J. DOWNSTREAM PHYSICAL EXTENSION EVIDENCE ===")

extractor_source = Path(
    extractor.__file__
).read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "EXTRACTOR_METADATA_PRESERVES_PHYSICAL_EXTENSION",
    '"extension": p.suffix.lower()'
    in extractor_source,
)


# ------------------------------------------------------------
# K. Duplicate structured detector review
# ------------------------------------------------------------

print()
print("=== K. STRUCTURED DETECTOR REVIEW ===")

relevant_paths = [
    Path("backend/server/routes/files.py"),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_uduc_pipeline/upload_intake.py"
    ),
    Path("backend/server/stores/upload_document_extractor.py"),
]

combined = "\n".join(
    path.read_text(
        encoding="utf-8",
        errors="replace",
    )
    for path in relevant_paths
)

structured_terms = [
    "FormatDetectionResult",
    "UploadFormatDetectionResult",
    "DetectedFormat",
    "FormatDetectorResult",
]

for term in structured_terms:
    check(
        "NO_DUPLICATE_STRUCTURED_RESULT_"
        + term.upper(),
        term not in combined,
    )


# ------------------------------------------------------------
# L. Simple string contract is sufficient
# ------------------------------------------------------------

print()
print("=== L. SIMPLE STRING CONTRACT SUFFICIENCY ===")

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
)

check(
    "INTAKE_CONSUMES_DETECTED_EXTENSION_DIRECTLY",
    "extension = dependencies.guess_extension("
    in intake_source,
)

check(
    "INTAKE_DIRECTLY_CHECKS_DETECTED_EXTENSION",
    "extension not in allowed_extensions"
    in intake_source,
)

check(
    "NO_PROVEN_NEED_FOR_STRUCTURED_DETECTION_OBJECT",
    (
        "extension = dependencies.guess_extension("
        in intake_source
        and "extension not in allowed_extensions"
        in intake_source
        and (
            guess_signature.return_annotation is str
            or guess_signature.return_annotation == "str"
        )
    ),
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
        "U4.8_DETECTION_RESULT_CONTRACT_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U4.8 detection result contract verification failed."
    )

print(
    "U4.8_DETECTION_RESULT_CONTRACT_VERIFICATION: PASS"
)