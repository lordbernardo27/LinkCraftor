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


print(
    "=== U4.3 — CANONICAL SUPPORTED PHYSICAL FORMATS ==="
)


expected = {
    ".txt",
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".docx",
}


# ------------------------------------------------------------
# A. Exact backend physical allowlist
# ------------------------------------------------------------

print()
print("=== A. BACKEND PHYSICAL ALLOWLIST ===")

route_set = set(
    files_route.ALLOWED_EXT
)

check(
    "ROUTE_FORMAT_COUNT_IS_SIX",
    len(route_set) == 6,
)

check(
    "ROUTE_ALLOWLIST_EXACT",
    route_set == expected,
)

for ext in sorted(expected):
    check(
        "ROUTE_SUPPORTS_"
        + ext.replace(".", "").upper(),
        ext in route_set,
    )


# ------------------------------------------------------------
# B. Extractor format contract
# ------------------------------------------------------------

print()
print("=== B. EXTRACTOR FORMAT CONTRACT ===")

extractor_set = set(
    extractor.SUPPORTED_UPLOAD_EXTENSIONS.keys()
)

check(
    "EXTRACTOR_FORMAT_COUNT_IS_SIX",
    len(extractor_set) == 6,
)

check(
    "EXTRACTOR_ALLOWLIST_EXACT",
    extractor_set == expected,
)

check(
    "ROUTE_AND_EXTRACTOR_FORMAT_SETS_MATCH",
    route_set == extractor_set,
)


# ------------------------------------------------------------
# C. Alias preservation
# ------------------------------------------------------------

print()
print("=== C. PHYSICAL ALIAS PRESERVATION ===")

check(
    "MARKDOWN_ALIAS_REMAINS_PHYSICAL_MARKDOWN",
    files_route._guess_ext(
        "article.markdown"
    )
    == ".markdown",
)

check(
    "HTM_ALIAS_REMAINS_PHYSICAL_HTM",
    files_route._guess_ext(
        "article.htm"
    )
    == ".htm",
)

check(
    "MARKDOWN_AND_MD_REMAIN_DISTINCT",
    files_route._guess_ext(
        "article.markdown"
    )
    != files_route._guess_ext(
        "article.md"
    ),
)

check(
    "HTM_AND_HTML_REMAIN_DISTINCT",
    files_route._guess_ext(
        "article.htm"
    )
    != files_route._guess_ext(
        "article.html"
    ),
)


# ------------------------------------------------------------
# D. Case normalization
# ------------------------------------------------------------

print()
print("=== D. CASE NORMALIZATION ===")

case_samples = {
    "FILE.TXT": ".txt",
    "FILE.MD": ".md",
    "FILE.MARKDOWN": ".markdown",
    "FILE.HTML": ".html",
    "FILE.HTM": ".htm",
    "FILE.DOCX": ".docx",

    "file.TxT": ".txt",
    "file.Md": ".md",
    "file.MarkDown": ".markdown",
    "file.HtMl": ".html",
    "file.HtM": ".htm",
    "file.DoCx": ".docx",
}

for filename, expected_ext in case_samples.items():
    label = (
        filename
        .replace(".", "_")
        .replace("-", "_")
        .upper()
    )

    check(
        f"CASE_NORMALIZATION_{label}",
        files_route._guess_ext(
            filename
        )
        == expected_ext,
    )


# ------------------------------------------------------------
# E. Unsupported / missing extension
# ------------------------------------------------------------

print()
print("=== E. UNSUPPORTED FORMAT BOUNDARY ===")

unsupported = {
    ".pdf",
    ".csv",
    ".xml",
    ".zip",
    ".rar",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".rtf",
    ".odt",
    ".xlsx",
    ".pptx",
}

for ext in sorted(unsupported):
    check(
        "UNSUPPORTED_"
        + ext.replace(".", "").upper()
        + "_NOT_ALLOWED",
        ext not in route_set,
    )

check(
    "NO_SEVENTH_ROUTE_FORMAT",
    route_set == expected,
)

check(
    "NO_SEVENTH_EXTRACTOR_FORMAT",
    extractor_set == expected,
)


# ------------------------------------------------------------
# F. Filename detection behavior
# ------------------------------------------------------------

print()
print("=== F. FILENAME FORMAT BEHAVIOR ===")

check(
    "NO_EXTENSION_RETURNS_EMPTY",
    files_route._guess_ext(
        "document"
    )
    == "",
)

check(
    "MULTIPLE_DOTS_USE_FINAL_SUFFIX",
    files_route._guess_ext(
        "report.final.review.DOCX"
    )
    == ".docx",
)

check(
    "SUPPORTED_FINAL_SUFFIX_WINS",
    files_route._guess_ext(
        "report.pdf.md"
    )
    == ".md",
)

check(
    "UNSUPPORTED_FINAL_SUFFIX_DETECTED",
    files_route._guess_ext(
        "report.md.exe"
    )
    == ".exe",
)


# ------------------------------------------------------------
# G. Intake rejection contract
# ------------------------------------------------------------

print()
print("=== G. INTAKE ACCEPTANCE CONTRACT ===")

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
)

check(
    "INTAKE_USES_ALLOWED_EXTENSION_SET",
    "allowed_extensions"
    in intake_source,
)

check(
    "INTAKE_REJECTS_EXTENSION_OUTSIDE_SET",
    "extension not in allowed_extensions"
    in intake_source,
)

check(
    "INTAKE_DETECTS_BEFORE_STORE_CALL",
    (
        intake_source.find(
            "guess_extension("
        )
        >= 0
    )
    and (
        intake_source.find(
            "store_and_index("
        )
        >= 0
    )
    and (
        intake_source.find(
            "guess_extension("
        )
        <
        intake_source.find(
            "store_and_index("
        )
    ),
)


# ------------------------------------------------------------
# H. Frontend physical format alignment
# ------------------------------------------------------------

print()
print("=== H. FRONTEND PHYSICAL FORMAT ALIGNMENT ===")

frontend_path = Path(
    "frontend/public/assets/js/app.js"
)

frontend_source = frontend_path.read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "FRONTEND_CANONICAL_PHYSICAL_ACCEPT_LIST_PRESENT",
    '".docx,.md,.markdown,.html,.htm,.txt"'
    in frontend_source,
)

check(
    "FRONTEND_MARKDOWN_ALIAS_PRESENT",
    'if (value === ".markdown") return ".md";'
    in frontend_source,
)

check(
    "FRONTEND_HTM_ALIAS_PRESENT",
    'if (value === ".htm") return ".html";'
    in frontend_source,
)


# ------------------------------------------------------------
# I. Uploaded Document route is not expanded by archive/media
# ------------------------------------------------------------

print()
print("=== I. NO CONTRACT EXPANSION ===")

for ext in [
    ".zip",
    ".rar",
    ".pdf",
    ".csv",
    ".xml",
    ".jpg",
    ".png",
]:
    check(
        "BACKEND_UPLOAD_CONTRACT_EXCLUDES_"
        + ext.replace(".", "").upper(),
        ext not in route_set,
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
        "U4.3_SUPPORTED_PHYSICAL_FORMATS_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U4.3 supported physical formats verification failed."
    )

print(
    "U4.3_SUPPORTED_PHYSICAL_FORMATS_VERIFICATION: PASS"
)