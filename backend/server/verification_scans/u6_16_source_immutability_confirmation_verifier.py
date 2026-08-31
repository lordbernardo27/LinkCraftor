from __future__ import annotations

import inspect
import os
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_DEFLATED

import backend.server.stores.upload_document_extractor as extractor


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def write_docx(path: Path, document_xml: str) -> None:
    with ZipFile(
        path,
        "w",
        compression=ZIP_DEFLATED,
    ) as archive:
        archive.writestr(
            "word/document.xml",
            document_xml,
        )


def docx_xml(*paragraphs: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        + "".join(paragraphs)
        + "</w:body>"
        "</w:document>"
    )


def docx_paragraph(text: str) -> str:
    return (
        "<w:p>"
        "<w:r>"
        f"<w:t>{text}</w:t>"
        "</w:r>"
        "</w:p>"
    )


def snapshot(path: Path):
    stat = path.stat()
    return {
        "bytes": path.read_bytes(),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "mode": stat.st_mode,
    }


def unchanged(before, after) -> bool:
    return (
        before["bytes"] == after["bytes"]
        and before["size"] == after["size"]
        and before["mtime_ns"] == after["mtime_ns"]
        and before["mode"] == after["mode"]
    )


print("=== U6.16 - SOURCE IMMUTABILITY CONFIRMATION ===")


# ------------------------------------------------------------
# A. Successful extraction source immutability
# ------------------------------------------------------------

print()
print("=== A. SUCCESSFUL EXTRACTION IMMUTABILITY ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    txt = root / "article.txt"
    txt.write_text(
        "Paragraph one.\n\nParagraph two.",
        encoding="utf-8",
    )

    md = root / "article.md"
    md.write_text(
        "# Heading\n\nBody.",
        encoding="utf-8",
    )

    html = root / "article.html"
    html.write_text(
        "<h1>Heading</h1><p>Body.</p>",
        encoding="utf-8",
    )

    docx = root / "article.docx"
    write_docx(
        docx,
        docx_xml(
            docx_paragraph("Heading"),
            docx_paragraph("Body."),
        ),
    )

    cases = [
        ("TXT", txt, extractor.extract_txt_upload_v1),
        ("MARKDOWN", md, extractor.extract_markdown_upload_v1),
        ("HTML", html, extractor.extract_html_upload_v1),
        ("DOCX", docx, extractor.extract_docx_upload_v1),
    ]

    for name, path, func in cases:
        before = snapshot(path)
        result = func(path)
        after = snapshot(path)

        check(
            f"{name}_SUCCESS_STATUS",
            result.extraction_status == "success",
        )

        check(
            f"{name}_SUCCESS_SOURCE_UNCHANGED",
            unchanged(before, after),
        )


# ------------------------------------------------------------
# B. Empty-text handling is read-only
# ------------------------------------------------------------

print()
print("=== B. EMPTY-TEXT IMMUTABILITY ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    txt = root / "empty.txt"
    txt.write_text(
        "   \n\t   ",
        encoding="utf-8",
    )

    md = root / "empty.md"
    md.write_text(
        "   \n\n   ",
        encoding="utf-8",
    )

    html = root / "empty.html"
    html.write_text(
        "<html><body>   </body></html>",
        encoding="utf-8",
    )

    docx = root / "empty.docx"
    write_docx(
        docx,
        docx_xml(),
    )

    cases = [
        ("TXT", txt, extractor.extract_txt_upload_v1),
        ("MARKDOWN", md, extractor.extract_markdown_upload_v1),
        ("HTML", html, extractor.extract_html_upload_v1),
        ("DOCX", docx, extractor.extract_docx_upload_v1),
    ]

    for name, path, func in cases:
        before = snapshot(path)
        result = func(path)
        after = snapshot(path)

        check(
            f"{name}_EMPTY_STATUS",
            result.extraction_status == "empty_text",
        )

        check(
            f"{name}_EMPTY_SOURCE_UNCHANGED",
            unchanged(before, after),
        )


# ------------------------------------------------------------
# C. Missing-file handling creates nothing
# ------------------------------------------------------------

print()
print("=== C. MISSING-FILE IMMUTABILITY ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    paths = [
        root / "missing.txt",
        root / "missing.md",
        root / "missing.html",
        root / "missing.docx",
    ]

    funcs = [
        extractor.extract_txt_upload_v1,
        extractor.extract_markdown_upload_v1,
        extractor.extract_html_upload_v1,
        extractor.extract_docx_upload_v1,
    ]

    for path, func in zip(paths, funcs):
        result = func(path)

        check(
            f"MISSING_{path.suffix.lower().replace('.', '').upper()}_STATUS",
            result.extraction_status == "missing_file",
        )

        check(
            f"MISSING_{path.suffix.lower().replace('.', '').upper()}_NOT_CREATED",
            not path.exists(),
        )


# ------------------------------------------------------------
# D. Unsupported-extension handling is read-only
# ------------------------------------------------------------

print()
print("=== D. UNSUPPORTED-EXTENSION IMMUTABILITY ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    path = root / "wrong.txt"
    path.write_bytes(
        b"ORIGINAL_BYTES"
    )

    before = snapshot(path)

    result = extractor.extract_docx_upload_v1(
        path
    )

    after = snapshot(path)

    check(
        "UNSUPPORTED_EXTENSION_STATUS",
        result.extraction_status
        == "unsupported_extension",
    )

    check(
        "UNSUPPORTED_EXTENSION_SOURCE_UNCHANGED",
        unchanged(before, after),
    )


# ------------------------------------------------------------
# E. Invalid DOCX handling is read-only
# ------------------------------------------------------------

print()
print("=== E. INVALID DOCX IMMUTABILITY ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    missing_xml = root / "invalid.docx"

    with ZipFile(
        missing_xml,
        "w",
        compression=ZIP_DEFLATED,
    ) as archive:
        archive.writestr(
            "word/other.xml",
            "<root/>",
        )

    before = snapshot(missing_xml)

    result = extractor.extract_docx_upload_v1(
        missing_xml
    )

    after = snapshot(missing_xml)

    check(
        "INVALID_DOCX_STATUS",
        result.extraction_status
        == "invalid_docx",
    )

    check(
        "INVALID_DOCX_SOURCE_UNCHANGED",
        unchanged(before, after),
    )


# ------------------------------------------------------------
# F. Extraction-error handling is read-only
# ------------------------------------------------------------

print()
print("=== F. EXTRACTION-ERROR IMMUTABILITY ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "broken.docx"

    path.write_bytes(
        b"not-a-valid-zip-file"
    )

    before = snapshot(path)

    result = extractor.extract_docx_upload_v1(
        path
    )

    after = snapshot(path)

    check(
        "EXTRACTION_ERROR_STATUS",
        result.extraction_status
        == "extraction_error",
    )

    check(
        "EXTRACTION_ERROR_SOURCE_UNCHANGED",
        unchanged(before, after),
    )


# ------------------------------------------------------------
# G. Repeated extraction is non-mutating
# ------------------------------------------------------------

print()
print("=== G. REPEATED EXTRACTION IMMUTABILITY ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "repeat.md"

    path.write_text(
        "# Heading\n\nBody.",
        encoding="utf-8",
    )

    before = snapshot(path)

    first = extractor.extract_markdown_upload_v1(
        path
    )

    middle = snapshot(path)

    second = extractor.extract_markdown_upload_v1(
        path
    )

    after = snapshot(path)

    check(
        "REPEATED_EXTRACTION_FIRST_SUCCESS",
        first.extraction_status == "success",
    )

    check(
        "REPEATED_EXTRACTION_SECOND_SUCCESS",
        second.extraction_status == "success",
    )

    check(
        "REPEATED_EXTRACTION_SOURCE_UNCHANGED",
        unchanged(before, middle)
        and unchanged(middle, after),
    )


# ------------------------------------------------------------
# H. Source-code mutation primitive scan
# ------------------------------------------------------------

print()
print("=== H. MUTATION PRIMITIVE SCAN ===")

functions = [
    extractor.extract_txt_upload_v1,
    extractor.extract_markdown_upload_v1,
    extractor.extract_html_upload_v1,
    extractor.extract_docx_upload_v1,
    extractor.extract_upload_document_v1,
]

combined_source = "\n".join(
    inspect.getsource(func).lower()
    for func in functions
)

for forbidden in (
    ".write_text(",
    ".write_bytes(",
    ".unlink(",
    ".rename(",
    ".replace(",
    ".touch(",
    ".chmod(",
    "shutil.move(",
    "os.remove(",
    "os.unlink(",
    "os.rename(",
    "os.replace(",
):
    check(
        f"EXTRACTOR_DOES_NOT_USE_{forbidden.upper().replace('.', '_').replace('(', '').replace(')', '').replace(' ', '_')}",
        forbidden not in combined_source,
    )

check(
    "EXTRACTOR_DOES_NOT_OPEN_SOURCE_IN_WRITE_MODE",
    'open("w"' not in combined_source
    and "open('w'" not in combined_source
    and 'open("a"' not in combined_source
    and "open('a'" not in combined_source
    and 'open("x"' not in combined_source
    and "open('x'" not in combined_source
    and 'open("r+"' not in combined_source
    and "open('r+'" not in combined_source,
)


# ------------------------------------------------------------
# I. DOCX ZIP access remains read-only
# ------------------------------------------------------------

print()
print("=== I. DOCX ZIP READ-ONLY CONTRACT ===")

docx_helper_source = inspect.getsource(
    extractor._extract_docx_paragraphs_v2
).lower()

check(
    "DOCX_HELPER_USES_ZIPFILE_READ_PATH",
    "zipfile(" in docx_helper_source
    or "zipfile.zipfile(" in docx_helper_source,
)

check(
    "DOCX_HELPER_DOES_NOT_OPEN_ZIP_IN_WRITE_MODE",
    'mode="w"' not in docx_helper_source
    and "mode='w'" not in docx_helper_source
    and 'mode="a"' not in docx_helper_source
    and "mode='a'" not in docx_helper_source,
)


# ------------------------------------------------------------
# J. No sidecar/temp output beside source
# ------------------------------------------------------------

print()
print("=== J. NO SOURCE-SIDECAR OUTPUT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    path = root / "sidecar.html"
    path.write_text(
        "<h1>Heading</h1><p>Body.</p>",
        encoding="utf-8",
    )

    before_names = {
        child.name
        for child in root.iterdir()
    }

    extractor.extract_html_upload_v1(
        path
    )

    after_names = {
        child.name
        for child in root.iterdir()
    }

    check(
        "EXTRACTION_CREATES_NO_SIDECAR_FILES",
        before_names == after_names,
    )


# ------------------------------------------------------------
# K. Serialization cannot mutate source
# ------------------------------------------------------------

print()
print("=== K. SERIALIZATION IMMUTABILITY ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "serialize.txt"

    path.write_text(
        "Body.",
        encoding="utf-8",
    )

    result = extractor.extract_txt_upload_v1(
        path
    )

    before = snapshot(path)

    extractor.serialize_upload_extraction_result(
        result
    )

    after = snapshot(path)

    check(
        "SERIALIZATION_SOURCE_UNCHANGED",
        unchanged(before, after),
    )


# ------------------------------------------------------------
# L. Intake passes persisted source path to extractor
# ------------------------------------------------------------

print()
print("=== L. LIVE INTAKE SOURCE-PATH CONTRACT ===")

intake_module = __import__(
    "backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake",
    fromlist=["run_upload_intake"],
)

intake_source = inspect.getsource(
    intake_module.run_upload_intake
).lower()

check(
    "INTAKE_BUILDS_STORED_PATH",
    "stored_path" in intake_source,
)

check(
    "INTAKE_PASSES_STORED_PATH_TO_CANONICAL_EXTRACTOR",
    "extract_upload_document_v1("
    in intake_source
    and "stored_path"
    in intake_source,
)

check(
    "INTAKE_DOES_NOT_MUTATE_STORED_PATH_BEFORE_EXTRACTION",
    "stored_path.write_" not in intake_source
    and "stored_path.unlink(" not in intake_source
    and "stored_path.replace(" not in intake_source
    and "stored_path.rename(" not in intake_source,
)


# ------------------------------------------------------------
# M. Website / downstream writer isolation
# ------------------------------------------------------------

print()
print("=== M. SOURCE-MUTATION RESPONSIBILITY BOUNDARY ===")

for forbidden in (
    "article_body_cleaning_engine",
    "article_cleaning_pipeline",
    "write_uduc",
    "build_and_write_uduc",
    "highlight",
    "active_target",
    "uucd_persistence",
    "semantic",
    "runtime",
    "scorer",
):
    check(
        f"EXTRACTOR_DOES_NOT_DEPEND_ON_{forbidden.upper()}",
        forbidden not in combined_source,
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
        "U6.16_SOURCE_IMMUTABILITY_CONFIRMATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.16 source immutability confirmation failed."
    )

print(
    "U6.16_SOURCE_IMMUTABILITY_CONFIRMATION: CERTIFIED"
)

print(
    "U6.16_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.17_EXTRACTOR_NORMALIZATION_BOUNDARY_TRANSITION: AUTHORIZED"
)

print(
    "U6.16_FINAL_SOURCE_IMMUTABILITY_VERIFICATION: PASS"
)