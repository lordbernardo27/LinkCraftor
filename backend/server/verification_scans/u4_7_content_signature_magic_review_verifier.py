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


print("=== U4.7 - CONTENT SIGNATURE / MAGIC DETECTION REVIEW ===")


# ------------------------------------------------------------
# A. Current upload detector surface
# ------------------------------------------------------------

print()
print("=== A. CURRENT UPLOAD DETECTOR SURFACE ===")

guess_source = inspect.getsource(
    files_route._guess_ext
)

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
)

extractor_source = Path(
    extractor.__file__
).read_text(
    encoding="utf-8",
    errors="replace",
)

route_source = Path(
    files_route.__file__
).read_text(
    encoding="utf-8",
    errors="replace",
)

upload_surface = "\n".join(
    [
        guess_source,
        intake_source,
        extractor_source,
    ]
)

check(
    "DETECTOR_REMAINS_SUFFIX_BASED",
    ".suffix" in guess_source,
)

check(
    "NO_LC_UPLOAD_FILE_SIGNATURES",
    "LC_UPLOAD_FILE_SIGNATURES"
    not in upload_surface,
)

check(
    "NO_PYTHON_MAGIC_IMPORT",
    "import magic"
    not in upload_surface.lower()
    and "from magic"
    not in upload_surface.lower(),
)

check(
    "NO_MAGIC_FROM_FILE",
    "magic.from_file"
    not in upload_surface.lower(),
)

check(
    "NO_MAGIC_FROM_BUFFER",
    "magic.from_buffer"
    not in upload_surface.lower(),
)

check(
    "NO_FILETYPE_SIGNATURE_LIBRARY",
    "import filetype"
    not in upload_surface.lower()
    and "filetype.guess"
    not in upload_surface.lower(),
)


# ------------------------------------------------------------
# B. No byte-level acceptance authority
# ------------------------------------------------------------

print()
print("=== B. NO BYTE-LEVEL ACCEPTANCE AUTHORITY ===")

check(
    "GUESS_EXT_DOES_NOT_ACCEPT_FILE_BYTES",
    "bytes"
    not in inspect.signature(
        files_route._guess_ext
    ).parameters,
)

check(
    "GUESS_EXT_HAS_FILENAME_PARAMETER",
    "filename"
    in inspect.signature(
        files_route._guess_ext
    ).parameters,
)

check(
    "INTAKE_ACCEPTANCE_USES_EXTENSION",
    "extension not in allowed_extensions"
    in intake_source,
)

check(
    "INTAKE_HAS_NO_MAGIC_ACCEPTANCE",
    "magic"
    not in intake_source.lower(),
)

check(
    "INTAKE_HAS_NO_SIGNATURE_ACCEPTANCE",
    "signature"
    not in intake_source.lower(),
)


# ------------------------------------------------------------
# C. DOCX ZIP-container detection review
# ------------------------------------------------------------

print()
print("=== C. DOCX ZIP-CONTAINER DETECTION REVIEW ===")

check(
    "NO_ZIPFILE_BASED_UPLOAD_ACCEPTANCE_IN_ROUTE",
    "zipfile"
    not in guess_source.lower(),
)

check(
    "NO_ZIPFILE_BASED_UPLOAD_ACCEPTANCE_IN_INTAKE",
    "zipfile"
    not in intake_source.lower(),
)

check(
    "DOCX_EXTENSION_REMAINS_PHYSICAL_SIGNAL",
    files_route._guess_ext(
        "document.docx"
    )
    == ".docx",
)


# ------------------------------------------------------------
# D. No content sniffing for detection
# ------------------------------------------------------------

print()
print("=== D. NO CONTENT-SNIFFING DETECTOR ===")

detector_only_surface = "\n".join(
    [
        guess_source,
        intake_source,
    ]
).lower()

sniff_terms = [
    "<html",
    "<body",
    "<!doctype",

    "markdown",
    "plain text",
    "is_text",
    "decode(",
    "startswith(b",
    "read_bytes",
]

for term in sniff_terms:
    check(
        "DETECTOR_NO_SNIFF_"
        + (
            term
            .replace("<", "")
            .replace(">", "")
            .replace("!", "")
            .replace("#", "HASH")
            .replace(" ", "_")
            .replace("(", "")
            .replace(".", "_")
            .upper()
        ),
        term not in detector_only_surface,
    )


# ------------------------------------------------------------
# E. Bytes cannot override extension contract
# ------------------------------------------------------------

print()
print("=== E. EXTENSION AUTHORITY ===")

supported = {
    "fake.pdf.md": ".md",
    "fake.exe.docx": ".docx",
    "fake.txt.html": ".html",
}

for filename, expected in supported.items():
    label = (
        filename
        .replace(".", "_")
        .upper()
    )

    check(
        f"FINAL_SUFFIX_AUTHORITY_{label}",
        files_route._guess_ext(
            filename
        )
        == expected,
    )

unsupported = [
    "fake.md.exe",
    "fake.docx.pdf",
    "fake.html.zip",
]

for filename in unsupported:
    label = (
        filename
        .replace(".", "_")
        .upper()
    )

    detected = files_route._guess_ext(
        filename
    )

    check(
        f"UNSUPPORTED_FINAL_SUFFIX_REJECTABLE_{label}",
        detected not in files_route.ALLOWED_EXT,
    )


# ------------------------------------------------------------
# F. No MIME/sniffing dependency
# ------------------------------------------------------------

print()
print("=== F. NO MIME / SNIFFING DEPENDENCY ===")

combined_upload_files = "\n".join(
    [
        route_source,
        intake_source,
        extractor_source,
    ]
).lower()

check(
    "NO_MIMETYPES_GUESS_TYPE",
    "mimetypes.guess_type"
    not in combined_upload_files,
)

check(
    "NO_LIBMAGIC_DEPENDENCY",
    "libmagic"
    not in combined_upload_files,
)

check(
    "NO_CONTENT_SNIFFING_PACKAGE",
    "content_sniff"
    not in combined_upload_files
    and "sniffio"
    not in combined_upload_files,
)


# ------------------------------------------------------------
# G. Website sniffing remains isolated
# ------------------------------------------------------------

print()
print("=== G. WEBSITE SNIFFING ISOLATION ===")

website_files = [
    Path(
        "backend/server/stores/"
        "enterprise_raw_html_acquisition_engine.py"
    ),
    Path(
        "backend/server/stores/"
        "raw_website_html_fetch_runner.py"
    ),
    Path(
        "backend/server/stores/"
        "raw_website_html_store.py"
    ),
]

website_existing = [
    path
    for path in website_files
    if path.exists()
]

website_text = "\n".join(
    path.read_text(
        encoding="utf-8",
        errors="replace",
    )
    for path in website_existing
).lower()

check(
    "WEBSITE_SURFACE_EXISTS",
    bool(website_existing),
)

check(
    "UPLOAD_DETECTOR_DOES_NOT_IMPORT_WEBSITE_FETCH_RUNNER",
    "raw_website_html_fetch_runner"
    not in detector_only_surface,
)

check(
    "UPLOAD_DETECTOR_DOES_NOT_IMPORT_ENTERPRISE_HTML_ACQUISITION",
    "enterprise_raw_html_acquisition_engine"
    not in detector_only_surface,
)

check(
    "UPLOAD_DETECTOR_DOES_NOT_IMPORT_RAW_WEBSITE_HTML_STORE",
    "raw_website_html_store"
    not in detector_only_surface,
)


# ------------------------------------------------------------
# H. No premature Format Router implementation
# ------------------------------------------------------------

print()
print("=== H. NO PREMATURE FORMAT ROUTER ===")

router_terms = [
    "format_router",
    "route_format",
    "dispatch_format",
    "detect_and_route",
]

check(
    "NO_FORMAT_ROUTER_IN_DETECTOR_SURFACE",
    all(
        term not in detector_only_surface
        for term in router_terms
    ),
)


# ------------------------------------------------------------
# I. Extractor validation is downstream, not acceptance detection
# ------------------------------------------------------------

print()
print("=== I. EXTRACTOR VALIDATION BOUNDARY ===")

check(
    "EXTRACTOR_HAS_SUPPORTED_EXTENSION_MAP",
    "SUPPORTED_UPLOAD_EXTENSIONS"
    in extractor_source,
)

check(
    "EXTRACTOR_USES_PERSISTED_PATH_SUFFIX",
    "p.suffix.lower()"
    in extractor_source,
)

check(
    "EXTRACTOR_DOES_NOT_DEFINE_UPLOAD_ROUTE",
    "/api/files/upload"
    not in extractor_source,
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
        "U4.7_CONTENT_SIGNATURE_MAGIC_REVIEW_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U4.7 content signature/magic review verification failed."
    )

print(
    "U4.7_CONTENT_SIGNATURE_MAGIC_REVIEW_VERIFICATION: PASS"
)