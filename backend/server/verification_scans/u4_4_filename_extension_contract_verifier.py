from __future__ import annotations

import inspect
from pathlib import Path

import backend.server.routes.files as files_route

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline import (
    upload_intake,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print(
    "=== U4.4 - FILENAME / EXTENSION DETECTION CONTRACT ==="
)


# ------------------------------------------------------------
# A. Core detector implementation
# ------------------------------------------------------------

print()
print("=== A. CORE DETECTOR IMPLEMENTATION ===")

guess_source = inspect.getsource(
    files_route._guess_ext
)

safe_source = inspect.getsource(
    files_route._safe_upload_filename
)

check(
    "DETECTOR_SANITIZES_BEFORE_SUFFIX",
    "_safe_upload_filename"
    in guess_source
    and guess_source.find(
        "_safe_upload_filename"
    )
    <
    guess_source.find(
        ".suffix"
    ),
)

check(
    "DETECTOR_USES_FINAL_SUFFIX",
    ".suffix"
    in guess_source,
)

check(
    "DETECTOR_LOWERCASES_EXTENSION",
    ".lower()"
    in guess_source,
)

check(
    "DETECTOR_REQUIRES_NO_FILESYSTEM_READ",
    all(
        term not in guess_source
        for term in [
            "read_text",
            "read_bytes",
            "open(",
            ".exists(",
            ".is_file(",
        ]
    ),
)


# ------------------------------------------------------------
# B. Deterministic normal filenames
# ------------------------------------------------------------

print()
print("=== B. NORMAL FILENAME BEHAVIOR ===")

samples = {
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

    "article.TxT": ".txt",
    "article.Md": ".md",
    "article.MarkDown": ".markdown",
    "article.HtMl": ".html",
    "article.HtM": ".htm",
    "article.DoCx": ".docx",
}

for filename, expected in samples.items():
    label = (
        filename
        .replace(".", "_")
        .replace("-", "_")
        .upper()
    )

    check(
        f"DETECT_{label}",
        files_route._guess_ext(
            filename
        )
        == expected,
    )


# ------------------------------------------------------------
# C. Multiple dots / final suffix
# ------------------------------------------------------------

print()
print("=== C. MULTIPLE DOTS / DOUBLE EXTENSIONS ===")

check(
    "MULTI_DOT_DOCX_FINAL_SUFFIX",
    files_route._guess_ext(
        "annual.report.final.DOCX"
    )
    == ".docx",
)

check(
    "DOUBLE_EXTENSION_SUPPORTED_FINAL_SUFFIX",
    files_route._guess_ext(
        "report.pdf.md"
    )
    == ".md",
)

check(
    "DOUBLE_EXTENSION_UNSUPPORTED_FINAL_SUFFIX",
    files_route._guess_ext(
        "report.md.exe"
    )
    == ".exe",
)

check(
    "DECEPTIVE_DOCX_EXE_DETECTED_AS_EXE",
    files_route._guess_ext(
        "financial.docx.exe"
    )
    == ".exe",
)

check(
    "DECEPTIVE_PDF_DOCX_DETECTED_AS_DOCX",
    files_route._guess_ext(
        "financial.pdf.docx"
    )
    == ".docx",
)


# ------------------------------------------------------------
# D. Missing / malformed suffix
# ------------------------------------------------------------

print()
print("=== D. MISSING / MALFORMED SUFFIX ===")

check(
    "NO_EXTENSION_RETURNS_EMPTY",
    files_route._guess_ext(
        "document"
    )
    == "",
)

check(
    "TRAILING_DOT_NOT_SUPPORTED",
    files_route._guess_ext(
        "document."
    )
    not in files_route.ALLOWED_EXT,
)

def raises_value_error(filename: str) -> bool:
    try:
        files_route._guess_ext(filename)
    except ValueError:
        return True
    return False


check(
    "EMPTY_FILENAME_REJECTED_DETERMINISTICALLY",
    raises_value_error(""),
)

check(
    "WHITESPACE_FILENAME_REJECTED_DETERMINISTICALLY",
    raises_value_error("   "),
)


# ------------------------------------------------------------
# E. Hidden-file behavior
# ------------------------------------------------------------

print()
print("=== E. HIDDEN-FILE BEHAVIOR ===")

hidden_cases = {
    ".txt": "",
    ".md": "",
    ".html": "",
    ".docx": "",
    ".markdown": "",
    ".htm": "",
    ".hidden": "",
}

for filename, expected in hidden_cases.items():
    label = (
        filename
        .replace(".", "")
        .upper()
        or "EMPTY"
    )

    check(
        f"HIDDEN_{label}_NO_EXTENSION",
        files_route._guess_ext(
            filename
        )
        == expected,
    )


# ------------------------------------------------------------
# F. Path separator / traversal-like names
# ------------------------------------------------------------

print()
print("=== F. PATH SAFETY / SEPARATOR HANDLING ===")

path_cases = {
    "../article.md": ".md",
    "..\\article.md": ".md",
    "../../folder/report.HTML": ".html",
    "..\\..\\folder\\report.DOCX": ".docx",
    "/tmp/article.txt": ".txt",
    "C:\\temp\\article.markdown": ".markdown",
}

for filename, expected in path_cases.items():
    label = (
        filename
        .replace("\\", "_")
        .replace("/", "_")
        .replace(".", "_")
        .replace(":", "_")
        .upper()
    )

    check(
        f"PATH_CASE_{label}",
        files_route._guess_ext(
            filename
        )
        == expected,
    )


# ------------------------------------------------------------
# G. Safe filename preservation of valid suffix
# ------------------------------------------------------------

print()
print("=== G. SAFE FILENAME NORMALIZATION ===")

safe_cases = {
    "my report.md": ".md",
    "my<>report.html": ".html",
    "my:report.docx": ".docx",
    " report final .TXT ": ".txt",
}

for filename, expected in safe_cases.items():
    safe_name = files_route._safe_upload_filename(
        filename
    )

    check(
        "SAFE_FILENAME_NONBLANK_"
        + expected.replace(".", "").upper(),
        bool(
            str(safe_name).strip()
        ),
    )

    check(
        "SAFE_FILENAME_PRESERVES_"
        + expected.replace(".", "").upper(),
        files_route._guess_ext(
            filename
        )
        == expected,
    )


# ------------------------------------------------------------
# H. Intake ordering / rejection
# ------------------------------------------------------------

print()
print("=== H. INTAKE ORDERING / REJECTION ===")

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
)

guess_pos = intake_source.find(
    "guess_extension("
)

store_pos = intake_source.find(
    "store_and_index("
)

check(
    "FORMAT_DETECTION_BEFORE_STORAGE",
    guess_pos >= 0
    and store_pos >= 0
    and guess_pos < store_pos,
)

check(
    "UNSUPPORTED_EXTENSION_REJECTED",
    "extension not in allowed_extensions"
    in intake_source,
)

check(
    "BLANK_FILENAME_REJECTED_BY_CANONICAL_DETECTOR",
    raises_value_error(""),
)

check(
    "WHITESPACE_FILENAME_REJECTED_BY_CANONICAL_DETECTOR",
    raises_value_error("   "),
)


# ------------------------------------------------------------
# I. Original filename vs stored filename
# ------------------------------------------------------------

print()
print("=== I. ORIGINAL / STORED FILENAME SEPARATION ===")

route_source = Path(
    files_route.__file__
).read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "ORIGINAL_FILENAME_FIELD_PRESENT",
    '"filename"'
    in route_source,
)

check(
    "STORED_NAME_FIELD_PRESENT",
    '"stored_name"'
    in route_source,
)

check(
    "DOCUMENT_ID_PARTICIPATES_IN_STORED_NAME",
    "doc_id"
    in inspect.getsource(
        files_route._store_and_index
    ),
)


# ------------------------------------------------------------
# J. Malformed filenames cannot bypass allowlist
# ------------------------------------------------------------

print()
print("=== J. ALLOWLIST BYPASS RESISTANCE ===")

malformed = [
    "file.exe",
    "file.md.exe",
    "file.docx.exe",
    "file.html.php",
    "file.txt.bat",
    "file.pdf",
    "file",
    "file.",
]

for filename in malformed:
    detected = files_route._guess_ext(
        filename
    )

    check(
        "MALFORMED_REJECTABLE_"
        + filename
        .replace(".", "_")
        .replace("-", "_")
        .upper(),
        detected not in files_route.ALLOWED_EXT,
    )


# ------------------------------------------------------------
# K. Determinism
# ------------------------------------------------------------

print()
print("=== K. DETERMINISM ===")

determinism_samples = [
    "article.md",
    "article.HTML",
    "../unsafe/report.docx",
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

    check(
        "DETERMINISTIC_"
        + filename
        .replace("\\", "_")
        .replace("/", "_")
        .replace(".", "_")
        .upper(),
        first == second,
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
        "U4.4_FILENAME_EXTENSION_CONTRACT_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U4.4 filename/extension contract verification failed."
    )

print(
    "U4.4_FILENAME_EXTENSION_CONTRACT_VERIFICATION: PASS"
)