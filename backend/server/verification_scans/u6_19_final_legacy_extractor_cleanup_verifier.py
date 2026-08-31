from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")
BASE = ROOT / "backend" / "server"

CANONICAL = (
    BASE
    / "stores"
    / "upload_document_extractor.py"
).resolve()

EXCLUDED = {
    "backups",
    "verification_scans",
    "runtime_backups",
    "__pycache__",
    ".pytest_cache",
    "tests",
    "test",
    "logs",
}

results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def live_python_files():
    for path in BASE.rglob("*.py"):
        if set(path.parts) & EXCLUDED:
            continue
        yield path


files = list(live_python_files())

print("=== U6.19 - FINAL LEGACY EXTRACTOR CLEANUP VERIFICATION ===")
print(f"LIVE_PYTHON_FILES={len(files)}")
print()


# ------------------------------------------------------------
# A. Canonical extractor exists
# ------------------------------------------------------------

print("=== A. CANONICAL EXTRACTION AUTHORITY ===")

check(
    "CANONICAL_UPLOAD_DOCUMENT_EXTRACTOR_EXISTS",
    CANONICAL.exists(),
)

canonical_source = CANONICAL.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

for symbol in (
    "extract_upload_document_v1",
    "extract_txt_upload_v1",
    "extract_markdown_upload_v1",
    "extract_html_upload_v1",
    "extract_docx_upload_v1",
    "UploadExtractionResult",
):
    check(
        f"CANONICAL_EXTRACTOR_HAS_{symbol.upper()}",
        symbol in canonical_source,
    )


# ------------------------------------------------------------
# B. No legacy upload-extractor APIs elsewhere
# ------------------------------------------------------------

print()
print("=== B. LEGACY UPLOAD EXTRACTION API ABSENCE ===")

legacy_patterns = (
    r"\bextract_uploaded_document\b",
    r"\bparse_uploaded_document\b",
    r"\bparse_document_upload\b",
    r"\bupload_extractor\b",
    r"\bdocument_upload_extractor\b",
)

legacy_hits = []

for path in files:
    if path.resolve() == CANONICAL:
        continue

    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    for pattern in legacy_patterns:
        if re.search(
            pattern,
            source,
            flags=re.IGNORECASE,
        ):
            legacy_hits.append(
                (
                    path,
                    pattern,
                )
            )

check(
    "NO_LEGACY_UPLOAD_EXTRACTOR_API_OUTSIDE_CANONICAL_MODULE",
    not legacy_hits,
)

if legacy_hits:
    for path, pattern in legacy_hits:
        print(
            "LEGACY_HIT:",
            path.relative_to(ROOT),
            pattern,
        )


# ------------------------------------------------------------
# C. No direct format-extractor bypass
# ------------------------------------------------------------

print()
print("=== C. FORMAT EXTRACTOR BYPASS ABSENCE ===")

format_symbols = (
    "extract_txt_upload_v1",
    "extract_markdown_upload_v1",
    "extract_html_upload_v1",
    "extract_docx_upload_v1",
)

format_bypasses = []

for path in files:
    if path.resolve() == CANONICAL:
        continue

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
        format_bypasses.append(
            (
                path,
                hits,
            )
        )

check(
    "NO_DIRECT_FORMAT_EXTRACTOR_BYPASS",
    not format_bypasses,
)

if format_bypasses:
    for path, hits in format_bypasses:
        print(
            "FORMAT_BYPASS:",
            path.relative_to(ROOT),
            hits,
        )


# ------------------------------------------------------------
# D. Canonical dispatcher live usage
# ------------------------------------------------------------

print()
print("=== D. CANONICAL DISPATCHER LIVE USAGE ===")

dispatcher_users = []

for path in files:
    if path.resolve() == CANONICAL:
        continue

    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    if "extract_upload_document_v1" in source:
        dispatcher_users.append(
            path.relative_to(ROOT)
        )

expected_intake = Path(
    "backend/server/pipelines/upload_document/"
    "uploaded_document_to_uduc_pipeline/upload_intake.py"
)

check(
    "CANONICAL_DISPATCHER_USED_BY_UPLOAD_INTAKE",
    expected_intake in dispatcher_users,
)

check(
    "CANONICAL_DISPATCHER_HAS_SINGLE_LIVE_EXTERNAL_USER",
    dispatcher_users == [expected_intake],
)

print(
    "DISPATCHER_USERS="
    + ", ".join(
        str(path)
        for path in dispatcher_users
    )
)


# ------------------------------------------------------------
# E. Upload pipeline does not reread persisted source
# ------------------------------------------------------------

print()
print("=== E. UPLOAD PIPELINE SOURCE REREAD ABSENCE ===")

pipeline_root = (
    BASE
    / "pipelines"
    / "upload_document"
)

reread_hits = []

for path in pipeline_root.rglob("*.py"):
    if set(path.parts) & EXCLUDED:
        continue

    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    tokens = [
        token
        for token in (
            ".read_text(",
            ".read_bytes(",
            "Path.read_text(",
            "Path.read_bytes(",
        )
        if token in source
    ]

    if tokens:
        reread_hits.append(
            (
                path,
                tokens,
            )
        )

check(
    "UPLOAD_PIPELINE_DOES_NOT_REREAD_SOURCE",
    not reread_hits,
)

if reread_hits:
    for path, tokens in reread_hits:
        print(
            "REREAD_HIT:",
            path.relative_to(ROOT),
            tokens,
        )


# ------------------------------------------------------------
# F. DOCX source parsing remains canonical
# ------------------------------------------------------------

print()
print("=== F. DOCX PARSING AUTHORITY ===")

docx_parser_hits = []

for path in files:
    if path.resolve() == CANONICAL:
        continue

    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    ).lower()

    if (
        "zipfile" in source
        and "word/document.xml" in source
    ):
        docx_parser_hits.append(
            path.relative_to(ROOT)
        )

check(
    "NO_DOCX_UPLOAD_PARSER_OUTSIDE_CANONICAL_EXTRACTOR",
    not docx_parser_hits,
)

if docx_parser_hits:
    print(
        "DOCX_PARSER_HITS=",
        docx_parser_hits,
    )


# ------------------------------------------------------------
# G. Known live upload entry points remain clean
# ------------------------------------------------------------

print()
print("=== G. LIVE UPLOAD ENTRY POINT CLEANLINESS ===")

known_entries = [
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

for path in known_entries:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    ).lower()

    forbidden = (
        "word/document.xml",
        "_strip_markdown_syntax",
        "_strip_html_tags",
        "_extract_docx_paragraphs",
        "_normalize_upload_text_v2",
    )

    check(
        "ENTRY_CLEAN_"
        + path.stem.upper()
        + "_"
        + str(
            abs(
                hash(
                    str(
                        path.relative_to(ROOT)
                    )
                )
            )
        ),
        not any(
            token in source
            for token in forbidden
        ),
    )


# ------------------------------------------------------------
# H. Previously identified candidates are not upload extractors
# ------------------------------------------------------------

print()
print("=== H. NON-UPLOAD EXTRACTOR CLASSIFICATION ===")

candidate_expectations = {
    BASE
    / "stores"
    / "dom_article_structure_extractor.py":
        "extract_dom_article_structure_v1",

    BASE
    / "stores"
    / "helix_smart_extractor.py":
        "extract_helix_authority_phrases",

    BASE
    / "stores"
    / "main_content_extraction_engine.py":
        "extract_main_content_from_html_v1",

    BASE
    / "stores"
    / "smart_phrase_extractor_backup_before_v2.py":
        "extract_smart_phrases",
}

for path, expected_symbol in candidate_expectations.items():
    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    check(
        f"CANDIDATE_{path.stem.upper()}_HAS_NON_UPLOAD_RESPONSIBILITY",
        expected_symbol in source,
    )

    check(
        f"CANDIDATE_{path.stem.upper()}_DOES_NOT_DEFINE_CANONICAL_UPLOAD_DISPATCHER",
        "def extract_upload_document_v1"
        not in source,
    )


# ------------------------------------------------------------
# I. No production cleanup required
# ------------------------------------------------------------

print()
print("=== I. CLEANUP DECISION ===")

check(
    "CANONICAL_EXTRACTOR_IS_SOLE_LIVE_UPLOAD_EXTRACTION_AUTHORITY",
    (
        not legacy_hits
        and not format_bypasses
        and not reread_hits
        and not docx_parser_hits
        and dispatcher_users
        == [expected_intake]
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
        "U6.19_LEGACY_EXTRACTOR_CLEANUP: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.19 legacy extractor cleanup verification failed."
    )

print(
    "U6.19_LEGACY_EXTRACTOR_CLEANUP: CERTIFIED"
)

print(
    "U6.19_PRODUCTION_CLEANUP_REQUIRED: NO"
)

print(
    "U6.19_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.20_BEHAVIORAL_EXTRACTION_VERIFICATION_TRANSITION: AUTHORIZED"
)

print(
    "U6.19_FINAL_LEGACY_EXTRACTOR_CLEANUP_VERIFICATION: PASS"
)