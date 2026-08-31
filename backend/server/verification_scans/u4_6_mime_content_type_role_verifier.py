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


print("=== U4.6 - MIME / CONTENT-TYPE ROLE ===")


# ------------------------------------------------------------
# A. Canonical detector remains extension-based
# ------------------------------------------------------------

print()
print("=== A. CANONICAL DETECTION AUTHORITY ===")

guess_source = inspect.getsource(
    files_route._guess_ext
)

check(
    "DETECTOR_USES_FILENAME_SUFFIX",
    ".suffix" in guess_source,
)

check(
    "DETECTOR_IGNORES_CONTENT_TYPE",
    "content_type" not in guess_source.lower(),
)

check(
    "DETECTOR_IGNORES_MIMETYPE",
    "mimetype" not in guess_source.lower(),
)

check(
    "DETECTOR_IGNORES_MIME",
    "mime" not in guess_source.lower(),
)


# ------------------------------------------------------------
# B. Intake acceptance remains extension-only
# ------------------------------------------------------------

print()
print("=== B. INTAKE ACCEPTANCE AUTHORITY ===")

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
)

check(
    "INTAKE_USES_GUESS_EXTENSION",
    "guess_extension(" in intake_source,
)

check(
    "INTAKE_USES_ALLOWED_EXTENSIONS",
    "allowed_extensions" in intake_source,
)

check(
    "INTAKE_REJECTS_UNSUPPORTED_EXTENSION",
    "extension not in allowed_extensions"
    in intake_source,
)

check(
    "INTAKE_HAS_NO_CONTENT_TYPE_AUTHORITY",
    "content_type" not in intake_source.lower(),
)

check(
    "INTAKE_HAS_NO_MIMETYPE_AUTHORITY",
    "mimetype" not in intake_source.lower(),
)

check(
    "INTAKE_HAS_NO_MIME_AUTHORITY",
    "mime" not in intake_source.lower(),
)


# ------------------------------------------------------------
# C. Extractor selection is not MIME-driven
# ------------------------------------------------------------

print()
print("=== C. EXTRACTOR SELECTION ===")

extractor_source = Path(
    extractor.__file__
).read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "EXTRACTOR_USES_EXTENSION_MAP",
    "SUPPORTED_UPLOAD_EXTENSIONS"
    in extractor_source,
)

check(
    "EXTRACTOR_USES_PATH_SUFFIX",
    "p.suffix.lower()"
    in extractor_source,
)

check(
    "EXTRACTOR_HAS_NO_CONTENT_TYPE_ROUTING",
    "content_type"
    not in extractor_source.lower(),
)

check(
    "EXTRACTOR_HAS_NO_MIMETYPE_ROUTING",
    "mimetype"
    not in extractor_source.lower(),
)

check(
    "EXTRACTOR_HAS_NO_MIME_ROUTING",
    "mime"
    not in extractor_source.lower(),
)


# ------------------------------------------------------------
# D. Route content_type role
# ------------------------------------------------------------

print()
print("=== D. ROUTE CONTENT-TYPE ROLE ===")

route_source = Path(
    files_route.__file__
).read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "UPLOADFILE_CONTENT_TYPE_CAPTURED",
    "file.content_type"
    in route_source,
)

check(
    "CONTENT_TYPE_METADATA_FIELD_PRESENT",
    '"content_type"'
    in route_source,
)

check(
    "CONTENT_TYPE_DOES_NOT_MODIFY_ALLOWED_EXT",
    "content_type" not in inspect.getsource(
        files_route._guess_ext
    ).lower(),
)


# ------------------------------------------------------------
# E. Unsupported extension cannot be rescued by MIME
# ------------------------------------------------------------

print()
print("=== E. MIME CANNOT BYPASS EXTENSION CONTRACT ===")

unsupported_samples = [
    "report.pdf",
    "report.exe",
    "report.csv",
    "report.xml",
    "report.zip",
]

for filename in unsupported_samples:
    detected = files_route._guess_ext(
        filename
    )

    label = (
        filename
        .replace(".", "_")
        .upper()
    )

    check(
        f"UNSUPPORTED_{label}_REMAINS_REJECTABLE",
        detected not in files_route.ALLOWED_EXT,
    )


# ------------------------------------------------------------
# F. Supported extension remains authoritative despite MIME
# ------------------------------------------------------------

print()
print("=== F. SUPPORTED EXTENSION AUTHORITY ===")

supported_samples = {
    "article.txt": ".txt",
    "article.md": ".md",
    "article.markdown": ".markdown",
    "article.html": ".html",
    "article.htm": ".htm",
    "article.docx": ".docx",
}

for filename, expected in supported_samples.items():
    label = (
        filename
        .replace(".", "_")
        .upper()
    )

    check(
        f"SUPPORTED_{label}_DETECTED_BY_EXTENSION",
        files_route._guess_ext(
            filename
        )
        == expected,
    )


# ------------------------------------------------------------
# G. No MIME-based alias normalization
# ------------------------------------------------------------

print()
print("=== G. MIME DOES NOT NORMALIZE ALIASES ===")

check(
    "MARKDOWN_PHYSICAL_ALIAS_STILL_PRESERVED",
    files_route._guess_ext(
        "article.markdown"
    )
    == ".markdown",
)

check(
    "HTM_PHYSICAL_ALIAS_STILL_PRESERVED",
    files_route._guess_ext(
        "article.htm"
    )
    == ".htm",
)


# ------------------------------------------------------------
# H. Response/download content type is separate
# ------------------------------------------------------------

print()
print("=== H. RESPONSE / DOWNLOAD SEPARATION ===")

check(
    "ROUTE_HAS_MEDIA_TYPE_USAGE",
    "media_type="
    in route_source,
)

check(
    "MEDIA_TYPE_USAGE_NOT_IN_GUESS_EXT",
    "media_type"
    not in guess_source.lower(),
)


# ------------------------------------------------------------
# I. Legacy MIME / magic detector residue
# ------------------------------------------------------------

print()
print("=== I. LEGACY MIME / MAGIC RESIDUE ===")

relevant_files = [
    Path("backend/server/routes/files.py"),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_uduc_pipeline/upload_intake.py"
    ),
    Path("backend/server/stores/upload_document_extractor.py"),
    Path("backend/server/stores/uploaded_document_unified_content.py"),
]

combined = "\n".join(
    path.read_text(
        encoding="utf-8",
        errors="replace",
    )
    for path in relevant_files
)

check(
    "NO_LC_UPLOAD_FILE_SIGNATURES",
    "LC_UPLOAD_FILE_SIGNATURES"
    not in combined,
)

check(
    "NO_MAGIC_BASED_UPLOAD_DETECTOR",
    "magic.from_"
    not in combined.lower()
    and "magic_buffer"
    not in combined.lower(),
)

check(
    "NO_MIMETYPES_GUESS_TYPE_UPLOAD_DETECTOR",
    "mimetypes.guess_type"
    not in combined.lower(),
)


# ------------------------------------------------------------
# J. Website MIME logic is not imported into upload branch
# ------------------------------------------------------------

print()
print("=== J. WEBSITE MIME ISOLATION ===")

website_mime_modules = [
    "enterprise_raw_html_acquisition_engine",
    "raw_website_html_fetch_runner",
    "raw_website_html_store",
]

upload_branch_text = "\n".join(
    [
        inspect.getsource(files_route._guess_ext),
        intake_source,
        extractor_source,
    ]
)

for module_name in website_mime_modules:
    check(
        "UPLOAD_BRANCH_NO_IMPORT_"
        + module_name.upper(),
        module_name
        not in upload_branch_text,
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
        "U4.6_MIME_CONTENT_TYPE_ROLE_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U4.6 MIME/content-type role verification failed."
    )

print(
    "U4.6_MIME_CONTENT_TYPE_ROLE_VERIFICATION: PASS"
)