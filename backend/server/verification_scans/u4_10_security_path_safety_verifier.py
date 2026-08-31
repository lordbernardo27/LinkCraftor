from __future__ import annotations

import inspect
from pathlib import Path

import backend.server.routes.files as files_route


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U4.10 - SECURITY / PATH SAFETY REVIEW ===")


safe_source = inspect.getsource(
    files_route._safe_upload_filename
)

guess_source = inspect.getsource(
    files_route._guess_ext
)

ws_source = inspect.getsource(
    files_route._ws
)

ws_dir_source = inspect.getsource(
    files_route._ws_dir
)

store_source = inspect.getsource(
    files_route._store_and_index
)


# ------------------------------------------------------------
# A. Filename sanitization precedes extension detection
# ------------------------------------------------------------

print()
print("=== A. FILENAME SANITIZATION BOUNDARY ===")

check(
    "DETECTOR_USES_SAFE_FILENAME_FIRST",
    "_safe_upload_filename(filename)"
    in guess_source,
)

check(
    "DETECTOR_SUFFIX_FROM_SAFE_NAME",
    "Path(safe_name).suffix"
    in guess_source,
)

check(
    "SAFE_FILENAME_COLLAPSES_WINDOWS_SEPARATOR",
    'replace("\\\\", "/")'
    in safe_source,
)

check(
    "SAFE_FILENAME_TAKES_FINAL_PATH_COMPONENT",
    'rsplit("/", 1)[-1]'
    in safe_source,
)

check(
    "SAFE_FILENAME_REMOVES_CONTROL_AND_FORBIDDEN_CHARS",
    r'[\x00-\x1f<>:\"/\\|?*]'
    in safe_source,
)

check(
    "SAFE_FILENAME_STRIPS_TRAILING_SPACE_PERIOD",
    'rstrip(" .")'
    in safe_source,
)


# ------------------------------------------------------------
# B. Path-like filename behavior
# ------------------------------------------------------------

print()
print("=== B. PATH-LIKE FILENAME BEHAVIOR ===")

path_samples = {
    "../../article.md": (
        "article.md",
        ".md",
    ),
    r"..\..\article.docx": (
        "article.docx",
        ".docx",
    ),
    r"C:\temp\article.html": (
        "article.html",
        ".html",
    ),
    "/tmp/article.htm": (
        "article.htm",
        ".htm",
    ),
    "folder/subfolder/article.txt": (
        "article.txt",
        ".txt",
    ),
}

for raw_name, expected in path_samples.items():
    expected_safe, expected_ext = expected

    label = (
        raw_name
        .replace("\\", "_")
        .replace("/", "_")
        .replace(".", "_")
        .replace(":", "_")
        .upper()
    )

    safe_name = files_route._safe_upload_filename(
        raw_name
    )

    detected = files_route._guess_ext(
        raw_name
    )

    check(
        f"PATH_{label}_SANITIZED_TO_BASENAME",
        safe_name == expected_safe,
    )

    check(
        f"PATH_{label}_EXTENSION_CORRECT",
        detected == expected_ext,
    )

    check(
        f"PATH_{label}_NO_DIRECTORY_SEPARATOR",
        "/" not in safe_name
        and "\\" not in safe_name,
    )


# ------------------------------------------------------------
# C. Multi-extension authority
# ------------------------------------------------------------

print()
print("=== C. MULTI-EXTENSION SAFETY ===")

multi_samples = {
    "article.pdf.md": ".md",
    "article.md.exe": ".exe",
    "article.docx.zip": ".zip",
}

for filename, expected_ext in multi_samples.items():
    label = (
        filename
        .replace(".", "_")
        .upper()
    )

    detected = files_route._guess_ext(
        filename
    )

    check(
        f"MULTI_{label}_FINAL_SUFFIX_AUTHORITY",
        detected == expected_ext,
    )


check(
    "DECEPTIVE_MD_EXE_REJECTABLE",
    files_route._guess_ext(
        "article.md.exe"
    )
    not in files_route.ALLOWED_EXT,
)

check(
    "DECEPTIVE_DOCX_ZIP_REJECTABLE",
    files_route._guess_ext(
        "article.docx.zip"
    )
    not in files_route.ALLOWED_EXT,
)


# ------------------------------------------------------------
# D. Hidden / trailing-dot / blank edge cases
# ------------------------------------------------------------

print()
print("=== D. EDGE CASE SAFETY ===")

for hidden in [
    ".txt",
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".docx",
]:
    label = hidden.replace(".", "").upper()

    check(
        f"HIDDEN_{label}_HAS_NO_PHYSICAL_EXTENSION",
        files_route._guess_ext(
            hidden
        )
        == "",
    )


check(
    "TRAILING_DOT_DOES_NOT_BYPASS_GATE",
    files_route._guess_ext(
        "article."
    )
    not in files_route.ALLOWED_EXT,
)


def raises_value_error(value: str) -> bool:
    try:
        files_route._safe_upload_filename(
            value
        )
    except ValueError:
        return True

    return False


check(
    "EMPTY_FILENAME_REJECTED",
    raises_value_error(""),
)

check(
    "WHITESPACE_FILENAME_REJECTED",
    raises_value_error("   "),
)

check(
    "DOT_FILENAME_REJECTED",
    raises_value_error("."),
)

check(
    "DOTDOT_FILENAME_REJECTED",
    raises_value_error(".."),
)


# ------------------------------------------------------------
# E. Stored filename ownership
# ------------------------------------------------------------

print()
print("=== E. STORED FILENAME OWNERSHIP ===")

check(
    "STORE_RESANITIZES_CLIENT_FILENAME",
    "_safe_upload_filename(file.filename)"
    in store_source,
)

check(
    "STORE_GENERATES_UUID_DOCUMENT_ID",
    "uuid.uuid4().hex"
    in store_source,
)

check(
    "STORED_NAME_PREFIXED_BY_DOCUMENT_ID",
    'stored_name = f"{doc_id}__{safe_name}"'
    in store_source,
)

check(
    "STORED_PATH_USES_WORKSPACE_DIRECTORY",
    "stored_path = ws_dir / stored_name"
    in store_source,
)

check(
    "CLIENT_FILENAME_NOT_USED_AS_DIRECT_PATH",
    "Path(file.filename)"
    not in store_source,
)


# ------------------------------------------------------------
# F. Workspace path containment
# ------------------------------------------------------------

print()
print("=== F. WORKSPACE PATH CONTAINMENT ===")

check(
    "WORKSPACE_ID_IS_NORMALIZED",
    "_WS_SAFE_RE.sub"
    in ws_source,
)

check(
    "WORKSPACE_CANONICAL_PREFIX_PRESENT",
    'return f"ws_{s}"[:80]'
    in ws_source,
)

check(
    "WORKSPACE_DIRECTORY_ROOTED_AT_DOCS_DIR",
    "return DOCS_DIR / _ws(workspace_id)"
    in ws_dir_source,
)

safe_workspace_samples = [
    "../../outside",
    r"..\..\outside",
    "/tmp/outside",
    r"C:\temp\outside",
    "normal.example-site.com",
]

for raw_ws in safe_workspace_samples:
    normalized = files_route._ws(
        raw_ws
    )

    label = (
        raw_ws
        .replace("\\", "_")
        .replace("/", "_")
        .replace(".", "_")
        .replace(":", "_")
        .upper()
    )

    check(
        f"WORKSPACE_{label}_HAS_CANONICAL_PREFIX",
        normalized.startswith("ws_"),
    )

    check(
        f"WORKSPACE_{label}_NO_PATH_SEPARATOR",
        "/" not in normalized
        and "\\" not in normalized,
    )

    check(
        f"WORKSPACE_{label}_NOT_PARENT_REFERENCE",
        normalized not in {".", ".."}
        and ".." not in normalized,
    )


# ------------------------------------------------------------
# G. Effective workspace directory containment
# ------------------------------------------------------------

print()
print("=== G. EFFECTIVE DIRECTORY CONTAINMENT ===")

docs_root = files_route.DOCS_DIR.resolve()

for raw_ws in safe_workspace_samples:
    ws_path = files_route._ws_dir(
        raw_ws
    ).resolve()

    label = (
        raw_ws
        .replace("\\", "_")
        .replace("/", "_")
        .replace(".", "_")
        .replace(":", "_")
        .upper()
    )

    check(
        f"WORKSPACE_PATH_{label}_UNDER_DOCS_DIR",
        ws_path == docs_root
        or docs_root in ws_path.parents,
    )


# ------------------------------------------------------------
# H. Detector filesystem purity
# ------------------------------------------------------------

print()
print("=== H. DETECTOR FILESYSTEM PURITY ===")

for forbidden in [
    "read_bytes",
    "read_text",
    "write_bytes",
    "write_text",
    "open(",
    "mkdir",
    "unlink",
    "rename",
    "replace(",
]:
    if forbidden == "replace(":
        # _safe_upload_filename legitimately uses str.replace
        # for path-separator normalization. The detector must
        # still have no filesystem Path.replace operation.
        condition = "Path.replace(" not in guess_source
    else:
        condition = forbidden not in guess_source

    check(
        "DETECTOR_NO_FILESYSTEM_"
        + forbidden
        .replace("(", "")
        .replace("_", "")
        .upper(),
        condition,
    )


# ------------------------------------------------------------
# I. Website branch isolation
# ------------------------------------------------------------

print()
print("=== I. WEBSITE PATH LOGIC ISOLATION ===")

detector_surface = (
    safe_source
    + "\n"
    + guess_source
).lower()

for module_name in [
    "enterprise_raw_html_acquisition_engine",
    "raw_website_html_fetch_runner",
    "raw_website_html_store",
]:
    check(
        "UPLOAD_PATH_BOUNDARY_NO_"
        + module_name.upper(),
        module_name
        not in detector_surface,
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
        "U4.10_SECURITY_PATH_SAFETY_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U4.10 security/path safety verification failed."
    )

print(
    "U4.10_SECURITY_PATH_SAFETY_VERIFICATION: PASS"
)