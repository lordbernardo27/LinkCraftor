from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")
BASE = ROOT / "backend" / "server"

results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U6.22 - PHASE U6 FINAL CERTIFICATION ===")


# ------------------------------------------------------------
# A. Canonical extractor import
# ------------------------------------------------------------

print()
print("=== A. CANONICAL U6 AUTHORITY ===")

extractor = importlib.import_module(
    "backend.server.stores.upload_document_extractor"
)

check(
    "CANONICAL_EXTRACTOR_IMPORTS",
    extractor is not None,
)

check(
    "CANONICAL_DISPATCHER_EXISTS",
    callable(
        getattr(
            extractor,
            "extract_upload_document_v1",
            None,
        )
    ),
)

check(
    "UPLOAD_EXTRACTION_RESULT_EXISTS",
    hasattr(
        extractor,
        "UploadExtractionResult",
    ),
)


# ------------------------------------------------------------
# B. Exact UploadExtractionResult contract
# ------------------------------------------------------------

print()
print("=== B. UPLOAD EXTRACTION RESULT CONTRACT ===")

actual_fields = list(
    extractor.UploadExtractionResult
    .__dataclass_fields__
    .keys()
)

expected_fields = [
    "source_path",
    "source_type",
    "title",
    "text",
    "headings",
    "metadata",
    "extraction_status",
    "extraction_confidence",
    "created_at",
]

check(
    "UPLOAD_EXTRACTION_RESULT_FIELDS_EXACT",
    actual_fields == expected_fields,
)


# ------------------------------------------------------------
# C. Supported extension contract
# ------------------------------------------------------------

print()
print("=== C. SUPPORTED FORMAT CONTRACT ===")

expected_extensions = {
    ".txt": "txt",
    ".md": "markdown",
    ".markdown": "markdown",
    ".html": "html",
    ".htm": "html",
    ".docx": "docx",
}

check(
    "SUPPORTED_UPLOAD_EXTENSIONS_EXACT",
    extractor.SUPPORTED_UPLOAD_EXTENSIONS
    == expected_extensions,
)

for extension, source_type in expected_extensions.items():
    check(
        "FORMAT_MAPPING_"
        + extension.replace(".", "").upper(),
        extractor.SUPPORTED_UPLOAD_EXTENSIONS.get(
            extension
        )
        == source_type,
    )


# ------------------------------------------------------------
# D. Format-specific extractors
# ------------------------------------------------------------

print()
print("=== D. FORMAT EXTRACTOR CONTRACT ===")

for symbol in (
    "extract_txt_upload_v1",
    "extract_markdown_upload_v1",
    "extract_html_upload_v1",
    "extract_docx_upload_v1",
):
    check(
        symbol.upper() + "_AVAILABLE",
        callable(
            getattr(
                extractor,
                symbol,
                None,
            )
        ),
    )


# ------------------------------------------------------------
# E. Behavioral smoke certification
# ------------------------------------------------------------

print()
print("=== E. FINAL BEHAVIORAL SMOKE ===")


def write_docx(path: Path) -> None:
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>'
        '<w:p>'
        '<w:pPr><w:pStyle w:val="Heading1"/></w:pPr>'
        '<w:r><w:t>DOCX Heading</w:t></w:r>'
        '</w:p>'
        '<w:p>'
        '<w:r><w:t>DOCX body.</w:t></w:r>'
        '</w:p>'
        '</w:body>'
        '</w:document>'
    )

    with ZipFile(
        path,
        "w",
        compression=ZIP_DEFLATED,
    ) as archive:
        archive.writestr(
            "word/document.xml",
            xml,
        )


with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    txt = root / "final.txt"
    txt.write_text(
        "TXT body.",
        encoding="utf-8",
    )

    md = root / "final.md"
    md.write_text(
        "# Markdown Heading\n\nMarkdown body.",
        encoding="utf-8",
    )

    html = root / "final.html"
    html.write_text(
        "<h1>HTML Heading</h1><p>HTML body.</p>",
        encoding="utf-8",
    )

    docx = root / "final.docx"
    write_docx(docx)

    cases = {
        "TXT": txt,
        "MARKDOWN": md,
        "HTML": html,
        "DOCX": docx,
    }

    for name, path in cases.items():
        before = path.read_bytes()

        result = extractor.extract_upload_document_v1(
            path
        )

        after = path.read_bytes()

        check(
            f"{name}_FINAL_SMOKE_SUCCESS",
            result.extraction_status
            == "success",
        )

        check(
            f"{name}_FINAL_SMOKE_CANONICAL_RESULT",
            isinstance(
                result,
                extractor.UploadExtractionResult,
            ),
        )

        check(
            f"{name}_FINAL_SMOKE_HAS_TEXT",
            bool(
                result.text.strip()
            ),
        )

        check(
            f"{name}_FINAL_SMOKE_SOURCE_IMMUTABLE",
            before == after,
        )


# ------------------------------------------------------------
# F. DOCX final contract
# ------------------------------------------------------------

print()
print("=== F. DOCX FINAL CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    styled = root / "styled.docx"
    write_docx(styled)

    styled_result = (
        extractor.extract_docx_upload_v1(
            styled
        )
    )

    check(
        "DOCX_STYLED_HEADING_METHOD_CERTIFIED",
        styled_result.metadata.get(
            "heading_method"
        )
        == "style_based",
    )

    heuristic = root / "heuristic.docx"

    heuristic_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>'
        '<w:p><w:r><w:t>HEURISTIC HEADING</w:t></w:r></w:p>'
        '<w:p><w:r><w:t>Normal body paragraph.</w:t></w:r></w:p>'
        '</w:body>'
        '</w:document>'
    )

    with ZipFile(
        heuristic,
        "w",
        compression=ZIP_DEFLATED,
    ) as archive:
        archive.writestr(
            "word/document.xml",
            heuristic_xml,
        )

    heuristic_result = (
        extractor.extract_docx_upload_v1(
            heuristic
        )
    )

    check(
        "DOCX_HEURISTIC_FALLBACK_CERTIFIED",
        heuristic_result.metadata.get(
            "heading_method"
        )
        == "heuristic_fallback",
    )

    check(
        "DOCX_HEURISTIC_CONFIDENCE_CERTIFIED",
        heuristic_result.extraction_confidence
        == 0.88,
    )


# ------------------------------------------------------------
# G. U6 responsibility boundary
# ------------------------------------------------------------

print()
print("=== G. U6 RESPONSIBILITY BOUNDARY ===")

source = inspect.getsource(
    extractor
).lower()

for forbidden in (
    "article_body_cleaning_engine",
    "article_cleaning_pipeline",
    "build_uduc_from_upload_extraction_result",
    "write_uduc",
    "active_target_set",
    "uucd_engine_v1",
    "uucd_persistence_v1",
    "semantic_runtime",
    "semantic_score",
    "relevance_score",
    "scorer.py",
):
    check(
        "U6_ISOLATED_FROM_"
        + forbidden.upper(),
        forbidden not in source,
    )


# ------------------------------------------------------------
# H. Live dispatcher integration
# ------------------------------------------------------------

print()
print("=== H. LIVE DISPATCHER INTEGRATION ===")

intake_path = (
    BASE
    / "pipelines"
    / "upload_document"
    / "uploaded_document_to_uduc_pipeline"
    / "upload_intake.py"
)

intake_source = intake_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

check(
    "UPLOAD_INTAKE_USES_CANONICAL_DISPATCHER",
    "extract_upload_document_v1"
    in intake_source,
)

for direct_symbol in (
    "extract_txt_upload_v1",
    "extract_markdown_upload_v1",
    "extract_html_upload_v1",
    "extract_docx_upload_v1",
):
    check(
        "UPLOAD_INTAKE_DOES_NOT_BYPASS_WITH_"
        + direct_symbol.upper(),
        direct_symbol
        not in intake_source,
    )


# ------------------------------------------------------------
# I. U7 boundary
# ------------------------------------------------------------

print()
print("=== I. U7 TRANSITION BOUNDARY ===")

check(
    "U6_STRUCTURAL_NORMALIZATION_PRESENT",
    "_normalize_upload_text_v2"
    in source,
)

check(
    "U6_DOES_NOT_CLAIM_BROADER_U7_PIPELINE",
    "upload_specific_normalization_pipeline"
    not in source,
)


# ------------------------------------------------------------
# J. Final phase certification
# ------------------------------------------------------------

print()
print("=== J. PHASE U6 CERTIFICATION DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print("PHASE_U6_UPLOADED_DOCUMENT_EXTRACTOR: FAIL")
    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "Phase U6 final certification failed."
    )

print(
    "PHASE_U6_UPLOADED_DOCUMENT_EXTRACTOR: CERTIFIED"
)

print(
    "PHASE_U6_PRODUCTION_PATCH_OUTSTANDING: NO"
)

print(
    "PHASE_U6_CANONICAL_BOUNDARY: "
    "PERSISTED_SOURCE -> CANONICAL_DISPATCHER -> "
    "FORMAT_EXTRACTOR -> UPLOAD_EXTRACTION_RESULT -> STOP"
)

print(
    "PHASE_U7_UPLOAD_SPECIFIC_NORMALIZATION_TRANSITION: AUTHORIZED"
)

print(
    "U6.22_FINAL_PHASE_CERTIFICATION: PASS"
)