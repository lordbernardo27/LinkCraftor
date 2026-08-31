from __future__ import annotations

import inspect
from pathlib import Path

import backend.server.routes.files as files_route
import backend.server.stores.upload_document_extractor as extractor

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline import (
    upload_intake,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U4.14 - FORMAT DETECTION BEHAVIORAL VERIFICATION ===")

expected = {
    ".txt",
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".docx",
}

app_path = Path(
    "frontend/public/assets/js/app.js"
)

api_path = Path(
    "frontend/public/assets/js/app/api.js"
)

legacy_path = Path(
    "frontend/public/assets/js/features/upload.js"
)

app_source = app_path.read_text(
    encoding="utf-8",
    errors="replace",
)

api_source = api_path.read_text(
    encoding="utf-8",
    errors="replace",
)

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
)


print()
print("=== A. CANONICAL SIX-FORMAT CONTRACT ===")

check(
    "BACKEND_ALLOWLIST_EXACTLY_SIX",
    set(files_route.ALLOWED_EXT) == expected,
)

check(
    "EXTRACTOR_SUPPORT_EXACTLY_SIX",
    set(
        extractor.SUPPORTED_UPLOAD_EXTENSIONS.keys()
    )
    == expected,
)


print()
print("=== B. PHYSICAL ALIAS PRESERVATION ===")

check(
    "MARKDOWN_PHYSICAL_ALIAS_PRESERVED",
    files_route._guess_ext(
        "article.markdown"
    )
    == ".markdown",
)

check(
    "HTM_PHYSICAL_ALIAS_PRESERVED",
    files_route._guess_ext(
        "article.htm"
    )
    == ".htm",
)


print()
print("=== C. FINAL-SUFFIX SECURITY ===")

cases = {
    "article.md.exe": ".exe",
    "article.docx.zip": ".zip",
    "article.html.pdf": ".pdf",
}

for filename, expected_ext in cases.items():
    ext = files_route._guess_ext(filename)

    check(
        "FINAL_SUFFIX_"
        + expected_ext.replace(".", "").upper()
        + "_DETECTED",
        ext == expected_ext
        and ext not in files_route.ALLOWED_EXT,
    )


print()
print("=== D. NO-EXTENSION / HIDDEN BEHAVIOR ===")

check(
    "NO_EXTENSION_REJECTABLE",
    files_route._guess_ext(
        "article"
    )
    == "",
)

check(
    "TRAILING_DOT_REJECTABLE",
    files_route._guess_ext(
        "article."
    )
    == "",
)

for filename in [
    ".txt",
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".docx",
]:
    check(
        "HIDDEN_"
        + filename.replace(".", "").upper()
        + "_NOT_ACCEPTED",
        files_route._guess_ext(filename)
        not in files_route.ALLOWED_EXT,
    )


print()
print("=== E. PATH-LIKE INPUT SAFETY ===")

check(
    "WINDOWS_PATH_COLLAPSES_TO_DOCX",
    files_route._guess_ext(
        r"C:\Users\HP\Desktop\article.docx"
    )
    == ".docx",
)

check(
    "POSIX_PATH_COLLAPSES_TO_HTML",
    files_route._guess_ext(
        "/tmp/uploads/article.html"
    )
    == ".html",
)

check(
    "TRAVERSAL_PATH_COLLAPSES_TO_MD",
    files_route._guess_ext(
        r"..\..\article.md"
    )
    == ".md",
)


print()
print("=== F. DETECTION ORDERING ===")

detect_pos = intake_source.find(
    "extension = dependencies.guess_extension(filename)"
)

gate_pos = intake_source.find(
    "if extension not in allowed_extensions:"
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
    "DETECTION_BEFORE_ACCEPTANCE_GATE",
    -1 < detect_pos < gate_pos,
)

check(
    "ACCEPTANCE_GATE_BEFORE_FILE_READ",
    -1 < gate_pos < read_pos,
)

check(
    "ACCEPTANCE_GATE_BEFORE_STORAGE",
    -1 < gate_pos < store_pos,
)

check(
    "ACCEPTANCE_GATE_BEFORE_CANONICAL_EXTRACTION",
    -1 < gate_pos < extract_pos,
)


print()
print("=== G. MIME / MAGIC NON-AUTHORITY ===")

intake_lower = intake_source.lower()

check(
    "NO_MIME_ACCEPTANCE_GATE",
    "mime" not in intake_lower,
)

check(
    "NO_MAGIC_ACCEPTANCE_GATE",
    "magic" not in intake_lower,
)

check(
    "NO_SIGNATURE_ACCEPTANCE_GATE",
    "signature" not in intake_lower,
)


print()
print("=== H. FRONTEND ALIGNMENT ===")

check(
    "FRONTEND_PICKER_HAS_CANONICAL_SIX",
    '".docx,.md,.markdown,.html,.htm,.txt"'
    in app_source,
)

check(
    "FRONTEND_MARKDOWN_SESSION_ALIAS",
    'if (value === ".markdown") return ".md";'
    in app_source,
)

check(
    "FRONTEND_HTM_SESSION_ALIAS",
    'if (value === ".htm") return ".html";'
    in app_source,
)

check(
    "FRONTEND_SENDS_ORIGINAL_FILE",
    'fd.append("file", file);'
    in api_source,
)

check(
    "FRONTEND_USES_CANONICAL_ENDPOINT",
    "/api/files/upload?workspace_id="
    in api_source,
)


print()
print("=== I. LEGACY MODULE REMAINS ABSENT ===")

check(
    "LEGACY_FEATURE_UPLOAD_STILL_REMOVED",
    not legacy_path.exists(),
)


print()
print("=== J. UNRELATED SYSTEM ISOLATION ===")

check(
    "URL_IMPORT_REMAINS_SEPARATE",
    "/api/urls/import?workspace_id="
    in app_source,
)

check(
    "DRAFT_IMPORT_REMAINS_SEPARATE",
    "/api/draft/import?workspace_id="
    in app_source,
)


failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U4.14_FORMAT_DETECTION_BEHAVIORAL_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U4.14 format detection behavioral verification failed."
    )

print(
    "U4.14_FORMAT_DETECTION_BEHAVIORAL_VERIFICATION: PASS"
)