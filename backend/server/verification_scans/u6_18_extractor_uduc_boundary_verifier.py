from __future__ import annotations

import inspect
from pathlib import Path
from tempfile import TemporaryDirectory

import backend.server.stores.upload_document_extractor as extractor
import backend.server.stores.uploaded_document_unified_content as uduc_store


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U6.18 - EXTRACTOR VS UDUC RESPONSIBILITY BOUNDARY ===")


# ------------------------------------------------------------
# A. U6 canonical handoff contract
# ------------------------------------------------------------

print()
print("=== A. U6 CANONICAL HANDOFF CONTRACT ===")

check(
    "UPLOAD_EXTRACTION_RESULT_EXISTS",
    hasattr(
        extractor,
        "UploadExtractionResult",
    ),
)

fields = getattr(
    extractor.UploadExtractionResult,
    "__dataclass_fields__",
    {},
)

expected_fields = {
    "source_path",
    "source_type",
    "title",
    "text",
    "headings",
    "metadata",
    "extraction_status",
    "extraction_confidence",
    "created_at",
}

check(
    "UPLOAD_EXTRACTION_RESULT_HAS_EXACT_CANONICAL_FIELDS",
    set(fields.keys()) == expected_fields,
)


with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "sample.txt"

    path.write_text(
        "Sample body.",
        encoding="utf-8",
    )

    result = extractor.extract_upload_document_v1(
        path
    )

    check(
        "CANONICAL_DISPATCHER_RETURNS_UPLOAD_EXTRACTION_RESULT",
        isinstance(
            result,
            extractor.UploadExtractionResult,
        ),
    )

    check(
        "SUCCESSFUL_EXTRACTION_IS_INDEPENDENT_OF_UDUC",
        result.extraction_status == "success"
        and result.text == "Sample body.",
    )


# ------------------------------------------------------------
# B. Extractor does not own UDUC construction/persistence
# ------------------------------------------------------------

print()
print("=== B. EXTRACTOR DOES NOT OWN UDUC ===")

extractor_source = inspect.getsource(
    extractor
).lower()

for forbidden in (
    "uploadeddocumentunifiedcontent",
    "build_uduc_from_upload_extraction_result",
    "serialize_uduc",
    "uduc_output_path",
    "write_uduc",
    "read_uduc",
    "build_and_write_uduc_from_extraction_result",
):
    check(
        f"EXTRACTOR_DOES_NOT_CALL_{forbidden.upper()}",
        forbidden not in extractor_source,
    )


# ------------------------------------------------------------
# C. Extractor does not own UDUC identity/schema/persistence
# ------------------------------------------------------------

print()
print("=== C. UDUC IDENTITY / SCHEMA / PERSISTENCE ISOLATION ===")

for forbidden in (
    "uduc_id",
    "uduc_version",
    "uduc_schema",
    "uploaded_document_unified_content",
    "registry",
    "active_target",
    "highlight",
    "uucd",
):
    check(
        f"EXTRACTOR_DOES_NOT_OWN_{forbidden.upper()}",
        forbidden not in extractor_source,
    )


# ------------------------------------------------------------
# D. UDUC builder consumes UploadExtractionResult
# ------------------------------------------------------------

print()
print("=== D. UDUC BUILDER INPUT CONTRACT ===")

builder = (
    uduc_store.build_uduc_from_upload_extraction_result
)

builder_source = inspect.getsource(
    builder
).lower()

check(
    "UDUC_BUILDER_EXISTS",
    callable(builder),
)

check(
    "UDUC_BUILDER_REFERENCES_UPLOAD_EXTRACTION_RESULT",
    "uploadextractionresult"
    in builder_source
    or "extraction_result"
    in builder_source,
)

check(
    "UDUC_BUILDER_CONSUMES_RESULT_TITLE",
    ".title"
    in builder_source
    or 'get("title")'
    in builder_source,
)

check(
    "UDUC_BUILDER_CONSUMES_RESULT_TEXT",
    ".text"
    in builder_source
    or 'get("text")'
    in builder_source,
)

check(
    "UDUC_BUILDER_CONSUMES_RESULT_HEADINGS",
    ".headings"
    in builder_source
    or 'get("headings")'
    in builder_source,
)


# ------------------------------------------------------------
# E. UDUC builder does not reread source files
# ------------------------------------------------------------

print()
print("=== E. UDUC BUILDER DOES NOT RE-EXTRACT SOURCE ===")

for forbidden in (
    ".read_text(",
    ".read_bytes(",
    "open(",
    "zipfile(",
    "extract_txt_upload_v1",
    "extract_markdown_upload_v1",
    "extract_html_upload_v1",
    "extract_docx_upload_v1",
    "extract_upload_document_v1",
):
    check(
        f"UDUC_BUILDER_DOES_NOT_USE_{forbidden.upper().replace('.', '_').replace('(', '').replace(')', '')}",
        forbidden not in builder_source,
    )


# ------------------------------------------------------------
# F. UDUC builder preserves extractor-owned content
# ------------------------------------------------------------

print()
print("=== F. EXTRACTOR CONTENT OWNERSHIP PRESERVED ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "article.txt"

    path.write_text(
        "Original extracted text.",
        encoding="utf-8",
    )

    extraction_result = (
        extractor.extract_txt_upload_v1(
            path
        )
    )

    uduc = builder(
        extraction_result=extraction_result,
        workspace_id="u6_18_verification_workspace",
        document_id="u6_18_verification_document",
    )

    check(
        "UDUC_BUILD_ACCEPTS_CANONICAL_EXTRACTION_RESULT",
        uduc is not None,
    )

    serialized_uduc = (
        uduc_store.serialize_uduc(
            uduc
        )
    )

    serialized_repr = repr(
        serialized_uduc
    )

    check(
        "UDUC_BUILD_DOES_NOT_REQUIRE_SOURCE_REREAD",
        "Original extracted text."
        in serialized_repr,
    )


# ------------------------------------------------------------
# G. Live intake invokes extractor before UDUC downstream work
# ------------------------------------------------------------

print()
print("=== G. LIVE INTAKE ORDERING BOUNDARY ===")

intake_module = __import__(
    "backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake",
    fromlist=["run_upload_intake"],
)

intake_source = inspect.getsource(
    intake_module.run_upload_intake
).lower()

check(
    "INTAKE_CALLS_CANONICAL_EXTRACTOR",
    "extract_upload_document_v1("
    in intake_source,
)

check(
    "INTAKE_SERIALIZES_EXTRACTION_RESULT",
    "serialize_upload_extraction_result("
    in intake_source,
)

extractor_pos = intake_source.find(
    "extract_upload_document_v1("
)

serialize_pos = intake_source.find(
    "serialize_upload_extraction_result("
)

check(
    "INTAKE_EXTRACTS_BEFORE_SERIALIZATION",
    extractor_pos != -1
    and serialize_pos != -1
    and extractor_pos < serialize_pos,
)


# ------------------------------------------------------------
# H. Failure stops before downstream UDUC construction
# ------------------------------------------------------------

print()
print("=== H. EXTRACTION FAILURE BOUNDARY ===")

check(
    "INTAKE_REJECTS_NON_SUCCESS_EXTRACTION",
    'if extraction_status != "success":'
    in intake_source,
)

check(
    "INTAKE_FAILURE_CHECK_OCCURS_BEFORE_SERIALIZATION",
    intake_source.find(
        'if extraction_status != "success":'
    )
    < serialize_pos,
)


# ------------------------------------------------------------
# I. Extraction serialization is independent of UDUC
# ------------------------------------------------------------

print()
print("=== I. EXTRACTION SERIALIZATION INDEPENDENCE ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "independent.md"

    path.write_text(
        "# Heading\n\nBody.",
        encoding="utf-8",
    )

    result = (
        extractor.extract_markdown_upload_v1(
            path
        )
    )

    serialized = (
        extractor.serialize_upload_extraction_result(
            result
        )
    )

    check(
        "EXTRACTION_SERIALIZES_WITHOUT_UDUC_BUILD",
        isinstance(serialized, dict)
        and serialized.get(
            "extraction_status"
        ) == "success",
    )

    check(
        "EXTRACTION_SERIALIZATION_PRESERVES_TEXT",
        serialized.get("text")
        == result.text,
    )


# ------------------------------------------------------------
# J. U6 testability independent of UDUC persistence
# ------------------------------------------------------------

print()
print("=== J. U6 INDEPENDENT TESTABILITY ===")

check(
    "EXTRACTOR_MODULE_DOES_NOT_IMPORT_UDUC_STORE",
    "uploaded_document_unified_content"
    not in extractor_source,
)

check(
    "EXTRACTOR_MODULE_DOES_NOT_IMPORT_UDUC_WRITERS",
    "write_uduc"
    not in extractor_source
    and "build_and_write_uduc"
    not in extractor_source,
)


# ------------------------------------------------------------
# K. Live-path shortcut / legacy extraction scan
# ------------------------------------------------------------

print()
print("=== K. LIVE-PATH SHORTCUT / LEGACY CHECK ===")

pipeline_module = __import__(
    "backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.coordinator",
    fromlist=["run_uploaded_document_to_uduc_pipeline"],
)

pipeline_source = inspect.getsource(
    pipeline_module
).lower()

check(
    "PIPELINE_DOES_NOT_DIRECTLY_CALL_FORMAT_EXTRACTORS",
    all(
        name not in pipeline_source
        for name in (
            "extract_txt_upload_v1",
            "extract_markdown_upload_v1",
            "extract_html_upload_v1",
            "extract_docx_upload_v1",
        )
    ),
)

check(
    "PIPELINE_DOES_NOT_REREAD_SOURCE_FOR_UDUC",
    ".read_text("
    not in pipeline_source
    and ".read_bytes("
    not in pipeline_source,
)


# ------------------------------------------------------------
# L. Responsibility boundary summary
# ------------------------------------------------------------

print()
print("=== L. RESPONSIBILITY BOUNDARY SUMMARY ===")

check(
    "U6_ENDS_AT_UPLOAD_EXTRACTION_RESULT",
    "uploadextractionresult"
    in extractor_source,
)

check(
    "UDUC_RESPONSIBILITY_EXISTS_OUTSIDE_EXTRACTOR",
    hasattr(
        uduc_store,
        "build_uduc_from_upload_extraction_result",
    )
    and hasattr(
        uduc_store,
        "serialize_uduc",
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
        "U6.18_EXTRACTOR_UDUC_BOUNDARY: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.18 extractor / UDUC boundary verification failed."
    )

print(
    "U6.18_EXTRACTOR_UDUC_BOUNDARY: CERTIFIED"
)

print(
    "U6.18_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.19_LEGACY_EXTRACTOR_CLEANUP_TRANSITION: AUTHORIZED"
)

print(
    "U6.18_FINAL_EXTRACTOR_UDUC_BOUNDARY_VERIFICATION: PASS"
)