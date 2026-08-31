from __future__ import annotations

import importlib
import inspect
import py_compile
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


def snapshot(path: Path) -> bytes:
    return path.read_bytes()


def write_docx(path: Path, text: str) -> None:
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>'
        '<w:p>'
        '<w:r>'
        f'<w:t>{text}</w:t>'
        '</w:r>'
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


print("=== U6.21 - BUILD / INTEGRATION VERIFICATION ===")


# ------------------------------------------------------------
# A. Production module compilation
# ------------------------------------------------------------

print()
print("=== A. PRODUCTION MODULE COMPILATION ===")

compile_targets = {
    "UPLOAD_EXTRACTOR":
        BASE / "stores" / "upload_document_extractor.py",

    "UPLOAD_INTAKE":
        BASE
        / "pipelines"
        / "upload_document"
        / "uploaded_document_to_uduc_pipeline"
        / "upload_intake.py",

    "UPLOAD_COORDINATOR":
        BASE
        / "pipelines"
        / "upload_document"
        / "coordinator.py",

    "UDUC_COORDINATOR":
        BASE
        / "pipelines"
        / "upload_document"
        / "uploaded_document_to_uduc_pipeline"
        / "coordinator.py",

    "UDUC_STORE":
        BASE
        / "stores"
        / "uploaded_document_unified_content.py",
}

for name, path in compile_targets.items():
    try:
        py_compile.compile(
            str(path),
            doraise=True,
        )
        compiled = True

    except Exception as exc:
        compiled = False
        print(
            f"{name}_COMPILE_ERROR="
            f"{type(exc).__name__}: {exc}"
        )

    check(
        f"{name}_COMPILES",
        compiled,
    )


# ------------------------------------------------------------
# B. Canonical module imports
# ------------------------------------------------------------

print()
print("=== B. CANONICAL MODULE IMPORTS ===")

module_names = {
    "UPLOAD_EXTRACTOR":
        "backend.server.stores.upload_document_extractor",

    "UPLOAD_INTAKE":
        "backend.server.pipelines.upload_document."
        "uploaded_document_to_uduc_pipeline.upload_intake",

    "UPLOAD_COORDINATOR":
        "backend.server.pipelines.upload_document.coordinator",

    "UDUC_COORDINATOR":
        "backend.server.pipelines.upload_document."
        "uploaded_document_to_uduc_pipeline.coordinator",

    "UDUC_STORE":
        "backend.server.stores.uploaded_document_unified_content",
}

modules = {}

for name, module_name in module_names.items():
    try:
        modules[name] = importlib.import_module(
            module_name
        )
        imported = True

    except Exception as exc:
        imported = False
        print(
            f"{name}_IMPORT_ERROR="
            f"{type(exc).__name__}: {exc}"
        )

    check(
        f"{name}_IMPORTS",
        imported,
    )


extractor = modules.get("UPLOAD_EXTRACTOR")
intake = modules.get("UPLOAD_INTAKE")
upload_coordinator = modules.get(
    "UPLOAD_COORDINATOR"
)
uduc_coordinator = modules.get(
    "UDUC_COORDINATOR"
)
uduc_store = modules.get("UDUC_STORE")


# ------------------------------------------------------------
# C. Canonical symbols
# ------------------------------------------------------------

print()
print("=== C. CANONICAL SYMBOL AVAILABILITY ===")

check(
    "UPLOAD_EXTRACTION_RESULT_IMPORTABLE",
    extractor is not None
    and hasattr(
        extractor,
        "UploadExtractionResult",
    ),
)

check(
    "CANONICAL_DISPATCHER_IMPORTABLE",
    extractor is not None
    and callable(
        getattr(
            extractor,
            "extract_upload_document_v1",
            None,
        )
    ),
)

check(
    "EXTRACTION_SERIALIZER_IMPORTABLE",
    extractor is not None
    and callable(
        getattr(
            extractor,
            "serialize_upload_extraction_result",
            None,
        )
    ),
)

check(
    "UPLOAD_INTAKE_ENTRY_IMPORTABLE",
    intake is not None
    and callable(
        getattr(
            intake,
            "run_upload_intake",
            None,
        )
    ),
)

check(
    "TOP_UPLOAD_COORDINATOR_ENTRY_IMPORTABLE",
    upload_coordinator is not None
    and callable(
        getattr(
            upload_coordinator,
            "run_upload_document",
            None,
        )
    ),
)

check(
    "UDUC_PIPELINE_COORDINATOR_IMPORTABLE",
    uduc_coordinator is not None
    and callable(
        getattr(
            uduc_coordinator,
            "run_uploaded_document_to_uduc_pipeline",
            None,
        )
    ),
)

check(
    "UDUC_BUILDER_IMPORTABLE",
    uduc_store is not None
    and callable(
        getattr(
            uduc_store,
            "build_uduc_from_upload_extraction_result",
            None,
        )
    ),
)


# ------------------------------------------------------------
# D. Canonical dependency direction
# ------------------------------------------------------------

print()
print("=== D. CANONICAL DEPENDENCY DIRECTION ===")

extractor_source = (
    inspect.getsource(extractor)
    if extractor is not None
    else ""
)

intake_source = (
    inspect.getsource(intake)
    if intake is not None
    else ""
)

uduc_store_source = (
    inspect.getsource(uduc_store)
    if uduc_store is not None
    else ""
)

check(
    "INTAKE_REFERENCES_CANONICAL_DISPATCHER",
    "extract_upload_document_v1"
    in intake_source,
)

check(
    "EXTRACTOR_DOES_NOT_IMPORT_UDUC_STORE",
    "uploaded_document_unified_content"
    not in extractor_source,
)

check(
    "EXTRACTOR_DOES_NOT_BUILD_UDUC",
    "build_uduc_from_upload_extraction_result"
    not in extractor_source,
)

check(
    "UDUC_BUILDER_ACCEPTS_EXTRACTION_RESULT",
    "extraction_result"
    in inspect.signature(
        uduc_store.build_uduc_from_upload_extraction_result
    ).parameters
    if uduc_store is not None
    and hasattr(
        uduc_store,
        "build_uduc_from_upload_extraction_result",
    )
    else False,
)


# ------------------------------------------------------------
# E. No direct format-extractor bypass
# ------------------------------------------------------------

print()
print("=== E. DIRECT FORMAT EXTRACTOR BYPASS ===")

format_symbols = (
    "extract_txt_upload_v1",
    "extract_markdown_upload_v1",
    "extract_html_upload_v1",
    "extract_docx_upload_v1",
)

live_upload_files = [
    BASE / "routes" / "files.py",

    BASE
    / "pipelines"
    / "upload_document"
    / "coordinator.py",

    BASE
    / "pipelines"
    / "upload_document"
    / "uploaded_document_to_uduc_pipeline"
    / "coordinator.py",

    BASE
    / "pipelines"
    / "upload_document"
    / "uploaded_document_to_uduc_pipeline"
    / "upload_intake.py",
]

bypasses = []

for path in live_upload_files:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    hits = [
        symbol
        for symbol in format_symbols
        if symbol in source
    ]

    if hits:
        bypasses.append(
            (
                path.relative_to(ROOT),
                hits,
            )
        )

check(
    "NO_DIRECT_FORMAT_EXTRACTOR_BYPASS",
    not bypasses,
)

if bypasses:
    for path, hits in bypasses:
        print(
            "FORMAT_BYPASS=",
            path,
            hits,
        )


# ------------------------------------------------------------
# F. No downstream source reread
# ------------------------------------------------------------

print()
print("=== F. DOWNSTREAM SOURCE REREAD ===")

pipeline_root = (
    BASE
    / "pipelines"
    / "upload_document"
)

rereads = []

for path in pipeline_root.rglob("*.py"):
    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    hits = [
        token
        for token in (
            ".read_text(",
            ".read_bytes(",
            "Path.read_text(",
            "Path.read_bytes(",
        )
        if token in source
    ]

    if hits:
        rereads.append(
            (
                path.relative_to(ROOT),
                hits,
            )
        )

check(
    "NO_UPLOAD_PIPELINE_SOURCE_REREAD",
    not rereads,
)

if rereads:
    for path, hits in rereads:
        print(
            "SOURCE_REREAD=",
            path,
            hits,
        )


# ------------------------------------------------------------
# G. Boundary isolation
# ------------------------------------------------------------

print()
print("=== G. BOUNDARY ISOLATION ===")

combined_upload_source = "\n".join(
    path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    ).lower()
    for path in live_upload_files
)

for forbidden in (
    "article_body_cleaning_engine",
    "article_cleaning_pipeline",
    "uucd_engine_v1",
    "uucd_persistence_v1",
    "write_uucd",
    "semantic_runtime",
    "semantic_score",
    "relevance_score",
    "scorer.py",
):
    check(
        "UPLOAD_CHAIN_ISOLATED_FROM_"
        + forbidden.upper(),
        forbidden
        not in combined_upload_source,
    )


# ------------------------------------------------------------
# H. Format-level integration smoke tests
# ------------------------------------------------------------

print()
print("=== H. FORMAT INTEGRATION SMOKE TESTS ===")

if extractor is None:
    check(
        "SMOKE_TESTS_AVAILABLE",
        False,
    )

else:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)

        txt = root / "sample.txt"
        txt.write_text(
            "First paragraph.\n\nSecond paragraph.",
            encoding="utf-8",
        )

        md = root / "sample.md"
        md.write_text(
            "# Markdown Heading\n\nMarkdown body.",
            encoding="utf-8",
        )

        html = root / "sample.html"
        html.write_text(
            "<html><body>"
            "<h1>HTML Heading</h1>"
            "<p>HTML body.</p>"
            "</body></html>",
            encoding="utf-8",
        )

        docx = root / "sample.docx"
        write_docx(
            docx,
            "DOCX body paragraph.",
        )

        cases = {
            "TXT": txt,
            "MARKDOWN": md,
            "HTML": html,
            "DOCX": docx,
        }

        for name, path in cases.items():
            before = snapshot(path)

            result = (
                extractor.extract_upload_document_v1(
                    path
                )
            )

            after = snapshot(path)

            check(
                f"{name}_SMOKE_RETURNS_CANONICAL_RESULT",
                isinstance(
                    result,
                    extractor.UploadExtractionResult,
                ),
            )

            check(
                f"{name}_SMOKE_SUCCESS",
                result.extraction_status
                == "success",
            )

            check(
                f"{name}_SMOKE_HAS_TEXT",
                isinstance(
                    result.text,
                    str,
                )
                and bool(
                    result.text.strip()
                ),
            )

            check(
                f"{name}_SMOKE_SOURCE_IMMUTABLE",
                before == after,
            )


# ------------------------------------------------------------
# I. Serialization integration
# ------------------------------------------------------------

print()
print("=== I. SERIALIZATION INTEGRATION ===")

if extractor is not None:
    with TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "serialize.txt"
        path.write_text(
            "Serialization smoke body.",
            encoding="utf-8",
        )

        result = (
            extractor.extract_upload_document_v1(
                path
            )
        )

        serialized = (
            extractor.serialize_upload_extraction_result(
                result
            )
        )

        check(
            "SERIALIZATION_INTEGRATION_RETURNS_DICT",
            isinstance(
                serialized,
                dict,
            ),
        )

        check(
            "SERIALIZATION_INTEGRATION_PRESERVES_STATUS",
            serialized.get(
                "extraction_status"
            )
            == result.extraction_status,
        )

        check(
            "SERIALIZATION_INTEGRATION_PRESERVES_TEXT",
            serialized.get(
                "text"
            )
            == result.text,
        )

        check(
            "SERIALIZATION_INTEGRATION_PRESERVES_SOURCE_TYPE",
            serialized.get(
                "source_type"
            )
            == result.source_type,
        )


# ------------------------------------------------------------
# J. Final integration decision
# ------------------------------------------------------------

print()
print("=== J. BUILD / INTEGRATION DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U6.21_BUILD_INTEGRATION_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.21 build/integration verification failed."
    )

print(
    "U6.21_BUILD_INTEGRATION_VERIFICATION: CERTIFIED"
)

print(
    "U6.21_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.22_PHASE_U6_CERTIFICATION_TRANSITION: AUTHORIZED"
)

print(
    "U6.21_FINAL_BUILD_INTEGRATION_VERIFICATION: PASS"
)