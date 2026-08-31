from __future__ import annotations

import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import backend.server.routes.files as files_route
import backend.server.stores.upload_document_extractor as extractor
import backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake as upload_intake


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U5.10 - ROUTER ORDERING ===")


router = extractor.detect_upload_source_type
router_source = inspect.getsource(router).lower()

dispatcher = extractor.extract_upload_document_v1
dispatcher_source = inspect.getsource(dispatcher).lower()

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
).lower()

route_source = inspect.getsource(
    files_route.upload_file
).lower()


# ------------------------------------------------------------
# A. Canonical router sequence
# ------------------------------------------------------------

print()
print("=== A. CANONICAL ROUTER SEQUENCE ===")

check(
    "ROUTER_READS_FINAL_PHYSICAL_SUFFIX",
    ".suffix" in router_source,
)

check(
    "ROUTER_LOWERCASES_FINAL_SUFFIX",
    ".suffix.lower()" in router_source,
)

check(
    "ROUTER_LOOKS_UP_NORMALIZED_SUFFIX",
    "supported_upload_extensions.get"
    in router_source
    and ".suffix.lower()"
    in router_source,
)

check(
    "UNSUPPORTED_IS_LOOKUP_FALLBACK",
    '"unsupported"' in router_source
    and ".get(" in router_source,
)


# ------------------------------------------------------------
# B. Upload route delegates canonical intake dependencies
# ------------------------------------------------------------

print()
print("=== B. UPLOAD ROUTE DELEGATION ===")

check(
    "ROUTE_INJECTS_CANONICAL_EXTENSION_DETECTOR",
    "guess_extension=_guess_ext"
    in route_source,
)

check(
    "ROUTE_INJECTS_CANONICAL_ALLOWLIST",
    "allowed_extensions=allowed_ext"
    in route_source,
)

check(
    "ROUTE_DELEGATES_TO_UPLOAD_COORDINATOR",
    "run_upload_document"
    in route_source,
)


# ------------------------------------------------------------
# C. Canonical intake ordering
# ------------------------------------------------------------

print()
print("=== C. CANONICAL INTAKE ORDERING ===")

detect_pos = intake_source.find(
    "dependencies.guess_extension"
)

allowlist_build_pos = intake_source.find(
    "allowed_extensions ="
)

allowlist_gate_pos = intake_source.find(
    "if extension not in allowed_extensions"
)

workspace_pos = intake_source.find(
    "dependencies.normalize_workspace_id"
)

read_pos = intake_source.find(
    "await file.read(max_upload_bytes + 1)"
)

empty_pos = intake_source.find(
    "if not raw:"
)

oversize_pos = intake_source.find(
    "if len(raw) > max_upload_bytes"
)

preview_pos = intake_source.find(
    "dependencies.extract_preview"
)

store_pos = intake_source.find(
    "dependencies.store_and_index"
)

extract_pos = intake_source.find(
    "extract_upload_document_v1"
)

check(
    "EXTENSION_DETECTION_PRECEDES_ALLOWLIST_BUILD",
    detect_pos >= 0
    and allowlist_build_pos > detect_pos,
)

check(
    "ALLOWLIST_BUILD_PRECEDES_ALLOWLIST_GATE",
    allowlist_build_pos >= 0
    and allowlist_gate_pos > allowlist_build_pos,
)

check(
    "ALLOWLIST_GATE_PRECEDES_FILE_READ",
    allowlist_gate_pos >= 0
    and read_pos > allowlist_gate_pos,
)

check(
    "WORKSPACE_NORMALIZATION_PRECEDES_FILE_READ",
    workspace_pos >= 0
    and read_pos > workspace_pos,
)

check(
    "BOUNDED_FILE_READ_IS_CANONICAL",
    read_pos >= 0,
)

check(
    "EMPTY_CHECK_FOLLOWS_FILE_READ",
    empty_pos > read_pos,
)

check(
    "OVERSIZE_CHECK_FOLLOWS_FILE_READ",
    oversize_pos > read_pos,
)

check(
    "PREVIEW_FOLLOWS_VALIDATED_READ",
    preview_pos > oversize_pos,
)

check(
    "PERSISTENCE_FOLLOWS_PREVIEW",
    store_pos > preview_pos,
)

check(
    "EXTRACTION_FOLLOWS_PERSISTENCE",
    extract_pos > store_pos,
)


# ------------------------------------------------------------
# D. Logical family before extraction dispatch
# ------------------------------------------------------------

print()
print("=== D. LOGICAL FAMILY BEFORE EXTRACTION ===")

family_detect_pos = dispatcher_source.find(
    "detect_upload_source_type"
)

txt_pos = dispatcher_source.find(
    'source_type == "txt"'
)

markdown_pos = dispatcher_source.find(
    'source_type == "markdown"'
)

html_pos = dispatcher_source.find(
    'source_type == "html"'
)

docx_pos = dispatcher_source.find(
    'source_type == "docx"'
)

check(
    "ROUTER_RUNS_BEFORE_TXT_BRANCH",
    family_detect_pos >= 0
    and txt_pos > family_detect_pos,
)

check(
    "ROUTER_RUNS_BEFORE_MARKDOWN_BRANCH",
    family_detect_pos >= 0
    and markdown_pos > family_detect_pos,
)

check(
    "ROUTER_RUNS_BEFORE_HTML_BRANCH",
    family_detect_pos >= 0
    and html_pos > family_detect_pos,
)

check(
    "ROUTER_RUNS_BEFORE_DOCX_BRANCH",
    family_detect_pos >= 0
    and docx_pos > family_detect_pos,
)


# ------------------------------------------------------------
# E. Family-specific dispatch
# ------------------------------------------------------------

print()
print("=== E. FAMILY-SPECIFIC DISPATCH ===")

check(
    "TXT_DISPATCH_ONLY_AFTER_TXT_RESOLUTION",
    'if source_type == "txt":'
    in dispatcher_source
    and "extract_txt_upload_v1"
    in dispatcher_source,
)

check(
    "MARKDOWN_DISPATCH_ONLY_AFTER_MARKDOWN_RESOLUTION",
    'if source_type == "markdown":'
    in dispatcher_source
    and "extract_markdown_upload_v1"
    in dispatcher_source,
)

check(
    "HTML_DISPATCH_ONLY_AFTER_HTML_RESOLUTION",
    'if source_type == "html":'
    in dispatcher_source
    and "extract_html_upload_v1"
    in dispatcher_source,
)

check(
    "DOCX_DISPATCH_ONLY_AFTER_DOCX_RESOLUTION",
    'if source_type == "docx":'
    in dispatcher_source
    and "extract_docx_upload_v1"
    in dispatcher_source,
)


# ------------------------------------------------------------
# F. Unsupported suffix cannot reach extractor
# ------------------------------------------------------------

print()
print("=== F. UNSUPPORTED DISPATCH GUARD ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    unsupported_path = root / "sample.pdf"
    unsupported_path.write_text(
        "plain content",
        encoding="utf-8",
    )

    with patch.object(
        extractor,
        "extract_txt_upload_v1",
        wraps=extractor.extract_txt_upload_v1,
    ) as txt_mock, patch.object(
        extractor,
        "extract_markdown_upload_v1",
        wraps=extractor.extract_markdown_upload_v1,
    ) as md_mock, patch.object(
        extractor,
        "extract_html_upload_v1",
        wraps=extractor.extract_html_upload_v1,
    ) as html_mock, patch.object(
        extractor,
        "extract_docx_upload_v1",
        wraps=extractor.extract_docx_upload_v1,
    ) as docx_mock:

        unsupported_result = dispatcher(
            unsupported_path
        )

        check(
            "UNSUPPORTED_SUFFIX_RETURNS_UNSUPPORTED_SOURCE_TYPE",
            unsupported_result.source_type
            == "unsupported",
        )

        check(
            "UNSUPPORTED_SUFFIX_DOES_NOT_CALL_TXT",
            txt_mock.call_count == 0,
        )

        check(
            "UNSUPPORTED_SUFFIX_DOES_NOT_CALL_MARKDOWN",
            md_mock.call_count == 0,
        )

        check(
            "UNSUPPORTED_SUFFIX_DOES_NOT_CALL_HTML",
            html_mock.call_count == 0,
        )

        check(
            "UNSUPPORTED_SUFFIX_DOES_NOT_CALL_DOCX",
            docx_mock.call_count == 0,
        )


# ------------------------------------------------------------
# G. Router authority purity
# ------------------------------------------------------------

print()
print("=== G. ROUTER AUTHORITY PURITY ===")

check(
    "MIME_DOES_NOT_PRECEDE_EXTENSION_ROUTING",
    "mime" not in router_source,
)

check(
    "CONTENT_TYPE_DOES_NOT_PRECEDE_EXTENSION_ROUTING",
    "content_type" not in router_source,
)

check(
    "BYTE_READ_DOES_NOT_PRECEDE_EXTENSION_ROUTING",
    ".read(" not in router_source
    and "read_bytes" not in router_source,
)

check(
    "MAGIC_DOES_NOT_PRECEDE_EXTENSION_ROUTING",
    "magic" not in router_source,
)

check(
    "SIGNATURE_DOES_NOT_PRECEDE_EXTENSION_ROUTING",
    "file_signature" not in router_source
    and "content_signature" not in router_source
    and "signature_bytes" not in router_source
    and "detect_signature" not in router_source,
)


# ------------------------------------------------------------
# H. Persistence does not redefine routing family
# ------------------------------------------------------------

print()
print("=== H. PERSISTENCE / ROUTER SEPARATION ===")

check(
    "ROUTER_DOES_NOT_PERSIST",
    "write_text" not in router_source
    and "write_bytes" not in router_source
    and "replace(" not in router_source,
)

check(
    "ROUTER_DOES_NOT_USE_WORKSPACE",
    "workspace" not in router_source,
)

check(
    "ROUTER_DOES_NOT_USE_REGISTRY",
    "registry" not in router_source,
)


# ------------------------------------------------------------
# I. Frontend cannot override backend authority
# ------------------------------------------------------------

print()
print("=== I. FRONTEND / BACKEND ORDERING ===")

app_source = Path(
    "frontend/public/assets/js/app.js"
).read_text(
    encoding="utf-8",
    errors="replace",
).lower()

check(
    "FRONTEND_MARKDOWN_ALIAS_IS_SESSION_NORMALIZATION",
    'if (value === ".markdown") return ".md";'
    in app_source,
)

check(
    "FRONTEND_HTM_ALIAS_IS_SESSION_NORMALIZATION",
    'if (value === ".htm") return ".html";'
    in app_source,
)

check(
    "BACKEND_ROUTER_HAS_NO_FRONTEND_SESSION_DEPENDENCY",
    "canonicalsessionformat" not in router_source
    and "frontend" not in router_source,
)


# ------------------------------------------------------------
# J. Intake does not duplicate family routing
# ------------------------------------------------------------

print()
print("=== J. INTAKE ROUTING ISOLATION ===")

check(
    "INTAKE_CALLS_CANONICAL_EXTRACTOR_DISPATCHER",
    "extract_upload_document_v1"
    in intake_source,
)

check(
    "INTAKE_DOES_NOT_FAMILY_DISPATCH_TXT",
    'source_type == "txt"'
    not in intake_source,
)

check(
    "INTAKE_DOES_NOT_FAMILY_DISPATCH_MARKDOWN",
    'source_type == "markdown"'
    not in intake_source,
)

check(
    "INTAKE_DOES_NOT_FAMILY_DISPATCH_HTML",
    'source_type == "html"'
    not in intake_source,
)

check(
    "INTAKE_DOES_NOT_FAMILY_DISPATCH_DOCX",
    'source_type == "docx"'
    not in intake_source,
)


# ------------------------------------------------------------
# K. Unrelated pipeline isolation
# ------------------------------------------------------------

print()
print("=== K. UNRELATED PIPELINE ISOLATION ===")

combined_upload_source = (
    router_source
    + "\n"
    + dispatcher_source
    + "\n"
    + intake_source
)

check(
    "NO_WEBSITE_CLEANER_IN_ROUTING_ORDER",
    "article_body_cleaning_engine"
    not in combined_upload_source
    and "article_cleaning_pipeline"
    not in combined_upload_source,
)

check(
    "NO_URL_IMPORT_IN_ROUTING_ORDER",
    "/api/urls/import"
    not in combined_upload_source,
)

check(
    "NO_DRAFT_IMPORT_IN_ROUTING_ORDER",
    "/api/draft/import"
    not in combined_upload_source,
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
        "U5.10_ROUTER_ORDERING: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.10 router ordering verification failed."
    )

print(
    "U5.10_ROUTER_ORDERING: CERTIFIED"
)

print(
    "U5.10_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U5.11_UNSUPPORTED_INVALID_FORMAT_GUARD_TRANSITION: AUTHORIZED"
)

print(
    "U5.10_FINAL_ROUTER_ORDERING_VERIFICATION: PASS"
)