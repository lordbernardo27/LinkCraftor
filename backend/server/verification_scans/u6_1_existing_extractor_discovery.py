from __future__ import annotations

import inspect
from pathlib import Path

import backend.server.stores.upload_document_extractor as extractor
import backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake as upload_intake


print("=== U6.1 - EXISTING EXTRACTOR DISCOVERY ===")
print()

print("=== A. MODULE LOCATION ===")
print(
    "EXTRACTOR_MODULE:",
    Path(inspect.getsourcefile(extractor) or "").as_posix(),
)

print()
print("=== B. PUBLIC EXTRACTION SYMBOLS ===")

symbols = [
    "UploadExtractionResult",
    "SUPPORTED_UPLOAD_EXTENSIONS",
    "detect_upload_source_type",
    "build_empty_upload_result",
    "extract_txt_upload_v1",
    "extract_markdown_upload_v1",
    "extract_html_upload_v1",
    "extract_docx_upload_v1",
    "extract_upload_document_v1",
]

for name in symbols:
    value = getattr(extractor, name, None)
    print(
        f"{name}:",
        "PRESENT" if value is not None else "MISSING",
    )


print()
print("=== C. UPLOAD EXTRACTION RESULT CONTRACT ===")

result_type = getattr(
    extractor,
    "UploadExtractionResult",
    None,
)

if result_type is not None:
    try:
        print(
            inspect.getsource(result_type)
        )
    except Exception as exc:
        print(
            "SOURCE_UNAVAILABLE:",
            type(exc).__name__,
        )


print()
print("=== D. ROUTER / DISPATCHER ===")

print(
    inspect.getsource(
        extractor.detect_upload_source_type
    )
)

print(
    inspect.getsource(
        extractor.extract_upload_document_v1
    )
)


print()
print("=== E. TXT EXTRACTOR ===")

print(
    inspect.getsource(
        extractor.extract_txt_upload_v1
    )
)


print()
print("=== F. MARKDOWN EXTRACTOR ===")

print(
    inspect.getsource(
        extractor.extract_markdown_upload_v1
    )
)


print()
print("=== G. HTML EXTRACTOR ===")

print(
    inspect.getsource(
        extractor.extract_html_upload_v1
    )
)


print()
print("=== H. DOCX EXTRACTOR ===")

print(
    inspect.getsource(
        extractor.extract_docx_upload_v1
    )
)


print()
print("=== I. EMPTY / FAILURE RESULT BUILDER ===")

print(
    inspect.getsource(
        extractor.build_empty_upload_result
    )
)


print()
print("=== J. FORMAT-SPECIFIC HELPERS ===")

helper_names = [
    "_normalize_upload_text_v2",
    "_extract_markdown_title_v1",
    "_extract_markdown_headings_v1",
    "_strip_markdown_v1",
    "_extract_html_title_v1",
    "_extract_html_headings_v1",
    "_strip_html_tags_v1",
    "_extract_docx_paragraphs_v2",
    "_extract_docx_headings_v2",
]

for name in helper_names:
    value = getattr(extractor, name, None)

    print()
    print(f"--- {name} ---")

    if value is None:
        print("MISSING")
        continue

    try:
        print(inspect.getsource(value))
    except Exception as exc:
        print(
            "SOURCE_UNAVAILABLE:",
            type(exc).__name__,
        )


print()
print("=== K. INTAKE HANDOFF ===")

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
)

for line_no, line in enumerate(
    intake_source.splitlines(),
    start=1,
):
    lower = line.lower()

    if (
        "extract_upload_document_v1" in lower
        or "extraction_result" in lower
        or "extraction_status" in lower
        or "serialize_upload_extraction_result" in lower
    ):
        print(
            f"{line_no}: {line.rstrip()}"
        )


print()
print("=== L. MODULE-LEVEL EXTRACTION-RELATED DEFINITIONS ===")

module_source = inspect.getsource(extractor)

for line_no, line in enumerate(
    module_source.splitlines(),
    start=1,
):
    stripped = line.strip()

    if (
        stripped.startswith("def extract_")
        or stripped.startswith("def _extract_")
        or stripped.startswith("class UploadExtractionResult")
        or stripped.startswith("def build_empty_upload_result")
        or stripped.startswith("def serialize_upload_extraction_result")
    ):
        print(
            f"{line_no}: {stripped}"
        )


print()
print("========================================")
print("U6.1_EXISTING_EXTRACTOR_DISCOVERY: COMPLETE")
print("U6.1_PRODUCTION_FILES_MODIFIED: NO")
print("U6.1_DISCOVERY_ONLY: YES")