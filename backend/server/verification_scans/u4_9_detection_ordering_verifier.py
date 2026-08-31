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


def pos(source: str, fragment: str) -> int:
    return source.find(fragment)


print("=== U4.9 - DETECTION ORDERING ===")

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
)

guess_source = inspect.getsource(
    files_route._guess_ext
)

route_source = inspect.getsource(
    files_route.upload_file
)


# ------------------------------------------------------------
# A. Filename validation precedes detection
# ------------------------------------------------------------

print()
print("=== A. FILENAME BEFORE DETECTION ===")

filename_pos = pos(
    intake_source,
    'filename = str(file.filename or "").strip()',
)

blank_check_pos = pos(
    intake_source,
    "if not filename:",
)

guess_pos = pos(
    intake_source,
    "extension = dependencies.guess_extension(filename)",
)

check(
    "FILENAME_CAPTURE_BEFORE_FORMAT_DETECTION",
    -1 < filename_pos < guess_pos,
)

check(
    "BLANK_FILENAME_CHECK_BEFORE_FORMAT_DETECTION",
    -1 < blank_check_pos < guess_pos,
)

check(
    "SAFE_FILENAME_NORMALIZATION_INSIDE_DETECTOR",
    "_safe_upload_filename(filename)"
    in guess_source,
)

check(
    "SUFFIX_EXTRACTION_AFTER_SAFE_FILENAME",
    pos(
        guess_source,
        "_safe_upload_filename(filename)",
    )
    < pos(
        guess_source,
        ".suffix",
    ),
)


# ------------------------------------------------------------
# B. Detection precedes acceptance
# ------------------------------------------------------------

print()
print("=== B. DETECTION BEFORE ACCEPTANCE ===")

allowed_set_pos = pos(
    intake_source,
    "allowed_extensions = {",
)

acceptance_pos = pos(
    intake_source,
    "if extension not in allowed_extensions:",
)

check(
    "DETECTION_BEFORE_ALLOWED_SET_CONSTRUCTION",
    -1 < guess_pos < allowed_set_pos,
)

check(
    "DETECTION_BEFORE_ACCEPTANCE_GATE",
    -1 < guess_pos < acceptance_pos,
)

check(
    "ACCEPTANCE_GATE_PRESENT",
    acceptance_pos != -1,
)


# ------------------------------------------------------------
# C. Acceptance precedes file-body read
# ------------------------------------------------------------

print()
print("=== C. ACCEPTANCE BEFORE FILE READ ===")

read_pos = pos(
    intake_source,
    "await file.read(MAX_UPLOAD_BYTES + 1)",
)

check(
    "ACCEPTANCE_BEFORE_BOUNDED_FILE_READ",
    -1 < acceptance_pos < read_pos,
)

check(
    "FORMAT_DETECTION_BEFORE_BOUNDED_FILE_READ",
    -1 < guess_pos < read_pos,
)


# ------------------------------------------------------------
# D. Acceptance precedes preview and persistence
# ------------------------------------------------------------

print()
print("=== D. ACCEPTANCE BEFORE PREVIEW / STORAGE ===")

preview_pos = pos(
    intake_source,
    "preview = dependencies.extract_preview(",
)

store_pos = pos(
    intake_source,
    "metadata = dependencies.store_and_index(",
)

check(
    "ACCEPTANCE_BEFORE_PREVIEW",
    -1 < acceptance_pos < preview_pos,
)

check(
    "ACCEPTANCE_BEFORE_SOURCE_PERSISTENCE",
    -1 < acceptance_pos < store_pos,
)

check(
    "FORMAT_DETECTION_BEFORE_SOURCE_PERSISTENCE",
    -1 < guess_pos < store_pos,
)

check(
    "PREVIEW_BEFORE_SOURCE_PERSISTENCE",
    -1 < preview_pos < store_pos,
)


# ------------------------------------------------------------
# E. Document identity follows persistence
# ------------------------------------------------------------

print()
print("=== E. DOCUMENT IDENTITY ORDER ===")

document_id_pos = pos(
    intake_source,
    'document_id = str(metadata.get("doc_id") or "").strip()',
)

stored_name_pos = pos(
    intake_source,
    'stored_name = str(metadata.get("stored_name") or "").strip()',
)

check(
    "DOCUMENT_ID_OBTAINED_AFTER_STORE_AND_INDEX",
    -1 < store_pos < document_id_pos,
)

check(
    "STORED_NAME_OBTAINED_AFTER_STORE_AND_INDEX",
    -1 < store_pos < stored_name_pos,
)

check(
    "FORMAT_DETECTION_BEFORE_DOCUMENT_IDENTITY",
    -1 < guess_pos < document_id_pos,
)


# ------------------------------------------------------------
# F. Canonical extraction follows persistence
# ------------------------------------------------------------

print()
print("=== F. PERSISTENCE BEFORE CANONICAL EXTRACTION ===")

stored_path_check_pos = pos(
    intake_source,
    "if not stored_path.is_file():",
)

canonical_extract_pos = pos(
    intake_source,
    "extraction_result = extract_upload_document_v1(",
)

check(
    "STORE_BEFORE_CANONICAL_EXTRACTOR",
    -1 < store_pos < canonical_extract_pos,
)

check(
    "DOCUMENT_ID_BEFORE_CANONICAL_EXTRACTOR",
    -1 < document_id_pos < canonical_extract_pos,
)

check(
    "STORED_PATH_EXISTENCE_CHECK_BEFORE_EXTRACTOR",
    -1 < stored_path_check_pos < canonical_extract_pos,
)

check(
    "FORMAT_ACCEPTANCE_BEFORE_CANONICAL_EXTRACTOR",
    -1 < acceptance_pos < canonical_extract_pos,
)


# ------------------------------------------------------------
# G. Unsupported format fails before downstream work
# ------------------------------------------------------------

print()
print("=== G. UNSUPPORTED FORMAT EARLY FAILURE ===")

check(
    "UNSUPPORTED_REJECTION_BEFORE_PREVIEW",
    -1 < acceptance_pos < preview_pos,
)

check(
    "UNSUPPORTED_REJECTION_BEFORE_STORAGE",
    -1 < acceptance_pos < store_pos,
)

check(
    "UNSUPPORTED_REJECTION_BEFORE_CANONICAL_EXTRACTION",
    -1 < acceptance_pos < canonical_extract_pos,
)


# ------------------------------------------------------------
# H. Route dependency wiring
# ------------------------------------------------------------

print()
print("=== H. ROUTE DEPENDENCY WIRING ===")

check(
    "ROUTE_INJECTS_CANONICAL_GUESS_EXTENSION",
    "guess_extension=_guess_ext"
    in route_source,
)

check(
    "ROUTE_INJECTS_ALLOWED_EXTENSIONS",
    "allowed_extensions=ALLOWED_EXT"
    in route_source,
)

check(
    "ROUTE_INJECTS_STORE_AND_INDEX",
    "store_and_index=_store_and_index"
    in route_source,
)

check(
    "ROUTE_INJECTS_COMPATIBILITY_PREVIEW",
    "extract_preview=_extract_preview_from_bytes"
    in route_source,
)


# ------------------------------------------------------------
# I. MIME cannot reorder authority
# ------------------------------------------------------------

print()
print("=== I. MIME NON-AUTHORITY ===")

check(
    "DETECTOR_HAS_NO_CONTENT_TYPE_INPUT",
    "content_type"
    not in inspect.signature(
        files_route._guess_ext
    ).parameters,
)

check(
    "INTAKE_FORMAT_GATE_NOT_CONTENT_TYPE_BASED",
    "content_type"
    not in intake_source.lower(),
)


# ------------------------------------------------------------
# J. No premature Format Router
# ------------------------------------------------------------

print()
print("=== J. NO PREMATURE FORMAT ROUTER ===")

detector_boundary = (
    guess_source
    + "\n"
    + intake_source
).lower()

for term in [
    "format_router",
    "route_format",
    "dispatch_format",
    "detect_and_route",
]:
    check(
        "NO_PREMATURE_"
        + term.replace("_", "").upper(),
        term not in detector_boundary,
    )


# ------------------------------------------------------------
# K. No premature runtime / semantic / scorer work
# ------------------------------------------------------------

print()
print("=== K. NO PREMATURE INTELLIGENCE EXECUTION ===")

for term in [
    "scorer",
    "semantic_runtime",
    "semantic_reader",
    "uucd_engine",
    "recommendation",
]:
    check(
        "NO_PREMATURE_"
        + term.replace("_", "").upper(),
        term not in detector_boundary,
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
        "U4.9_DETECTION_ORDERING_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U4.9 detection ordering verification failed."
    )

print(
    "U4.9_DETECTION_ORDERING_VERIFICATION: PASS"
)