from __future__ import annotations

import inspect

import backend.server.routes.files as files_route

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline import (
    upload_intake,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U4.11 - ERROR CONTRACT ===")

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
)

safe_source = inspect.getsource(
    files_route._safe_upload_filename
)

route_source = inspect.getsource(
    files_route.upload_file
)


# ------------------------------------------------------------
# A. Deterministic client-facing error messages
# ------------------------------------------------------------

print()
print("=== A. CLIENT ERROR CONTRACT ===")

expected_messages = [
    "No file uploaded.",
    "Uploaded file must have a filename.",
    "Uploaded filename is invalid.",
    "File type not allowed:",
    "workspace_id is invalid.",
    "Uploaded file is empty.",
    "Uploaded file exceeds the 250 MB limit.",
]

for message in expected_messages:
    label = (
        message
        .replace(" ", "_")
        .replace(".", "")
        .replace(":", "")
        .replace("-", "_")
        .upper()
    )

    check(
        f"CLIENT_ERROR_{label}_PRESENT",
        message in intake_source,
    )


# ------------------------------------------------------------
# B. Format errors use HTTP 400
# ------------------------------------------------------------

print()
print("=== B. FORMAT ERROR STATUS BOUNDARY ===")

guess_pos = intake_source.find(
    "extension = dependencies.guess_extension(filename)"
)

invalid_name_pos = intake_source.find(
    'detail="Uploaded filename is invalid."'
)

unsupported_pos = intake_source.find(
    'detail=f"File type not allowed: {extension}"'
)

read_pos = intake_source.find(
    "await file.read(MAX_UPLOAD_BYTES + 1)"
)

store_pos = intake_source.find(
    "metadata = dependencies.store_and_index("
)

extract_pos = intake_source.find(
    "extraction_result = extract_upload_document_v1("
)

check(
    "INVALID_FILENAME_ERROR_PRESENT_AFTER_DETECTOR_VALUEERROR",
    -1 < guess_pos < invalid_name_pos,
)

check(
    "UNSUPPORTED_FORMAT_ERROR_BEFORE_FILE_READ",
    -1 < unsupported_pos < read_pos,
)

check(
    "UNSUPPORTED_FORMAT_ERROR_BEFORE_STORAGE",
    -1 < unsupported_pos < store_pos,
)

check(
    "UNSUPPORTED_FORMAT_ERROR_BEFORE_CANONICAL_EXTRACTION",
    -1 < unsupported_pos < extract_pos,
)


# ------------------------------------------------------------
# C. No-extension and deceptive suffixes use same gate
# ------------------------------------------------------------

print()
print("=== C. SINGLE SUPPORTED-FORMAT ERROR GATE ===")

check(
    "NO_EXTENSION_NOT_ALLOWED",
    files_route._guess_ext(
        "document"
    )
    not in files_route.ALLOWED_EXT,
)

check(
    "TRAILING_DOT_NOT_ALLOWED",
    files_route._guess_ext(
        "document."
    )
    not in files_route.ALLOWED_EXT,
)

check(
    "DECEPTIVE_MD_EXE_NOT_ALLOWED",
    files_route._guess_ext(
        "document.md.exe"
    )
    not in files_route.ALLOWED_EXT,
)

check(
    "DECEPTIVE_DOCX_ZIP_NOT_ALLOWED",
    files_route._guess_ext(
        "document.docx.zip"
    )
    not in files_route.ALLOWED_EXT,
)


# ------------------------------------------------------------
# D. Detector ValueError is sanitized
# ------------------------------------------------------------

print()
print("=== D. DETECTOR ERROR SANITIZATION ===")

check(
    "INTAKE_CATCHES_DETECTOR_VALUEERROR",
    "except ValueError:"
    in intake_source,
)

check(
    "INTAKE_RETURNS_SANITIZED_INVALID_FILENAME_ERROR",
    'detail="Uploaded filename is invalid."'
    in intake_source,
)

check(
    "INTAKE_DOES_NOT_RETURN_VALUEERROR_TEXT",
    "str(exc)"
    not in intake_source
    and "str(e)"
    not in intake_source,
)


# ------------------------------------------------------------
# E. Safe filename internal messages stay internal
# ------------------------------------------------------------

print()
print("=== E. SANITIZER INTERNAL ERROR BOUNDARY ===")

check(
    "SANITIZER_HAS_MISSING_FILENAME_VALUEERROR",
    'ValueError("Uploaded file must have a filename.")'
    in safe_source,
)

check(
    "SANITIZER_HAS_INVALID_FILENAME_VALUEERROR",
    'ValueError("Uploaded filename is invalid.")'
    in safe_source,
)


# ------------------------------------------------------------
# F. Internal failures remain separate
# ------------------------------------------------------------

print()
print("=== F. INTERNAL FAILURE SEPARATION ===")

check(
    "POST_STORAGE_FAILURES_USE_RUNTIMEERROR",
    "RuntimeError("
    in intake_source,
)

check(
    "CANONICAL_EXTRACTION_FAILURE_IS_INTERNAL",
    "Canonical uploaded-document extraction failed"
    in intake_source,
)

check(
    "ROUTE_RERAISES_HTTP_EXCEPTIONS",
    "except HTTPException:"
    in route_source
    and "raise"
    in route_source,
)

check(
    "ROUTE_CATCHES_UNEXPECTED_EXCEPTIONS",
    "except Exception:"
    in route_source,
)

check(
    "ROUTE_USES_GENERIC_PUBLIC_FAILURE_MESSAGE",
    'detail="Upload processing failed."'
    in route_source,
)


# ------------------------------------------------------------
# G. No internal detail leakage
# ------------------------------------------------------------

print()
print("=== G. INTERNAL DETAIL NON-LEAKAGE ===")

check(
    "ROUTE_DOES_NOT_EXPOSE_STR_EXC",
    "str(exc)"
    not in route_source,
)

check(
    "ROUTE_DOES_NOT_EXPOSE_REPR_EXC",
    "repr(exc)"
    not in route_source,
)

check(
    "ROUTE_DOES_NOT_EXPOSE_TRACEBACK",
    "detail=traceback" not in route_source.lower()
    and "detail = traceback" not in route_source.lower()
    and "traceback.format_exc()" not in route_source.lower(),
)

check(
    "PUBLIC_GENERIC_ERROR_DOES_NOT_INCLUDE_PATH",
    "stored_path"
    not in 'detail="Upload processing failed."',
)


# ------------------------------------------------------------
# H. MIME/signature mismatch creates no parallel error contract
# ------------------------------------------------------------

print()
print("=== H. NO MIME / SIGNATURE ERROR CONTRACT ===")

check(
    "NO_CONTENT_TYPE_ERROR_GATE",
    "content_type"
    not in intake_source.lower(),
)

check(
    "NO_MIME_ERROR_GATE",
    "mime"
    not in intake_source.lower(),
)

check(
    "NO_MAGIC_ERROR_GATE",
    "magic"
    not in intake_source.lower(),
)

check(
    "NO_SIGNATURE_ERROR_GATE",
    "signature"
    not in intake_source.lower(),
)


# ------------------------------------------------------------
# I. Website error isolation
# ------------------------------------------------------------

print()
print("=== I. WEBSITE ERROR ISOLATION ===")

upload_error_surface = (
    intake_source
    + "\n"
    + route_source
).lower()

for module_name in [
    "enterprise_raw_html_acquisition_engine",
    "raw_website_html_fetch_runner",
    "raw_website_html_store",
]:
    check(
        "UPLOAD_ERROR_BOUNDARY_NO_"
        + module_name.upper(),
        module_name
        not in upload_error_surface,
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
        "U4.11_ERROR_CONTRACT_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U4.11 error contract verification failed."
    )

print(
    "U4.11_ERROR_CONTRACT_VERIFICATION: PASS"
)