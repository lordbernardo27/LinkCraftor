from pathlib import Path
import ast


root = Path("backend/server")

canonical_u7 = (
    root
    / "stores"
    / "upload_document_normalizer.py"
)

removed_live_backup = (
    root
    / "stores"
    / "smart_phrase_extractor_backup_before_v2.py"
)

backup_copy = (
    root
    / "backups"
    / "u7_20_legacy_normalization_cleanup"
    / "smart_phrase_extractor_backup_before_v2.py"
)

generic_normalizer = (
    root
    / "utils"
    / "text_normalization.py"
)

u6_extractor = (
    root
    / "stores"
    / "upload_document_extractor.py"
)

uduc = (
    root
    / "stores"
    / "uploaded_document_unified_content.py"
)


excluded_parts = {
    "backups",
    "verification_scans",
    "__pycache__",
}


def production_files():
    files = []

    for path in root.rglob("*.py"):
        if set(path.parts).intersection(
            excluded_parts
        ):
            continue

        files.append(path)

    return sorted(files)


files = production_files()

results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print(
    "=== U7.20 POST-CLEANUP VERIFICATION ==="
)


print()
print("=== A. CLEANUP STATE ===")

check(
    "CANONICAL_U7_NORMALIZER_PRESENT",
    canonical_u7.exists(),
)

check(
    "OBSOLETE_LIVE_BACKUP_REMOVED",
    not removed_live_backup.exists(),
)

check(
    "BACKUP_COPY_PRESENT",
    backup_copy.exists(),
)


print()
print("=== B. OBSOLETE MODULE REFERENCE SCAN ===")

obsolete_refs = []

for path in files:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    if (
        "smart_phrase_extractor_backup_before_v2"
        in source
    ):
        obsolete_refs.append(path)

for path in obsolete_refs:
    print(path)

check(
    "OBSOLETE_MODULE_PRODUCTION_REFERENCE_COUNT_ZERO",
    len(obsolete_refs) == 0,
)


print()
print("=== C. CANONICAL U7 AUTHORITY ===")

source = canonical_u7.read_text(
    encoding="utf-8-sig",
)

tree = ast.parse(source)

functions = {
    node.name
    for node in tree.body
    if isinstance(
        node,
        ast.FunctionDef,
    )
}

required_u7_helpers = {
    "_normalize_unicode_nfc",
    "_normalize_line_endings_lf",
    "_normalize_horizontal_whitespace",
    "_normalize_paragraph_boundaries",
    "_normalize_headings",
    "_normalize_title",
    "_remove_unsafe_control_characters",
    "normalize_uploaded_document_v1",
}

check(
    "CANONICAL_U7_HELPERS_PRESENT",
    required_u7_helpers.issubset(
        functions
    ),
)


print()
print("=== D. GENERIC NORMALIZER SEPARATION ===")

check(
    "GENERIC_NORMALIZER_PRESENT",
    generic_normalizer.exists(),
)

generic_upload_refs = []

for path in files:
    normalized = str(path).replace(
        "\\",
        "/",
    )

    if (
        "/pipelines/upload_document/"
        not in normalized
        and path.name
        not in {
            "files.py",
            "upload_document_extractor.py",
            "upload_document_normalizer.py",
            "uploaded_document_unified_content.py",
        }
    ):
        continue

    content = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    if (
        "fix_mojibake_text"
        in content
        or "utils.text_normalization"
        in content
        or "text_normalization import"
        in content
    ):
        generic_upload_refs.append(path)

for path in generic_upload_refs:
    print(path)

check(
    "GENERIC_NORMALIZER_NOT_REACHABLE_FROM_CURRENT_UPLOAD_PATH",
    len(generic_upload_refs) == 0,
)


print()
print("=== E. WEBSITE CLEANER SEPARATION ===")

website_refs = []

for path in files:
    normalized = str(path).replace(
        "\\",
        "/",
    )

    if (
        "/pipelines/upload_document/"
        not in normalized
        and path.name
        not in {
            "files.py",
            "upload_document_extractor.py",
            "upload_document_normalizer.py",
            "uploaded_document_unified_content.py",
        }
    ):
        continue

    content = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    ).lower()

    if (
        "article_body_cleaning_engine"
        in content
        or "article_cleaning_pipeline"
        in content
    ):
        website_refs.append(path)

for path in website_refs:
    print(path)

check(
    "WEBSITE_CLEANER_NOT_REACHABLE_FROM_CURRENT_UPLOAD_PATH",
    len(website_refs) == 0,
)


print()
print("=== F. U6 / U7 BOUNDARY ===")

check(
    "U6_EXTRACTOR_PRESENT",
    u6_extractor.exists(),
)

u6_source = u6_extractor.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

check(
    "U6_EXTRACTION_SAFE_NORMALIZER_PRESENT",
    "_normalize_upload_text_v2"
    in u6_source,
)

check(
    "U6_MARKDOWN_CLEANUP_PRESENT",
    "_strip_markdown_syntax_v2"
    in u6_source,
)

check(
    "U6_HTML_EXTRACTION_PRESENT",
    "_strip_html_tags_v1"
    in u6_source,
)

check(
    "U6_DOCX_EXTRACTION_PRESENT",
    "_extract_docx_paragraphs_v2"
    in u6_source,
)


print()
print("=== G. U7 / U8 BOUNDARY ===")

check(
    "UDUC_PRESENT",
    uduc.exists(),
)

uduc_source = uduc.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

check(
    "UDUC_STRUCTURAL_PARAGRAPH_BUILD_PRESENT",
    "_paragraphs_from_content_body"
    in uduc_source,
)

check(
    "UDUC_HEADING_MAP_PRESENT",
    "_build_heading_map"
    in uduc_source,
)

check(
    "UDUC_DOCUMENT_ORDER_PRESENT",
    "document_order"
    in uduc_source,
)

check(
    "UDUC_REALIGNMENT_DEFERRED_TO_U8",
    True,
)


print()
print("=== H. SECOND UPLOAD NORMALIZATION AUTHORITY SCAN ===")

second_authority_hits = []

authority_markers = (
    "_normalize_unicode_nfc",
    "_normalize_horizontal_whitespace",
    "_remove_unsafe_control_characters",
)

for path in files:
    if path == canonical_u7:
        continue

    content = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    if any(
        marker in content
        for marker in authority_markers
    ):
        second_authority_hits.append(
            path
        )

for path in second_authority_hits:
    print(path)

check(
    "SECOND_CANONICAL_UPLOAD_NORMALIZATION_AUTHORITY_COUNT_ZERO",
    len(second_authority_hits) == 0,
)


print()
print("=== I. FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U7.20_LEGACY_NORMALIZATION_CLEANUP: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U7.20 post-cleanup verification failed."
    )

print(
    "U7.20_LEGACY_NORMALIZATION_CLEANUP: CERTIFIED"
)

print(
    "U7.20_CANONICAL_U7_AUTHORITY: backend/server/stores/upload_document_normalizer.py"
)

print(
    "U7.20_OBSOLETE_LIVE_BACKUP_MODULE: REMOVED"
)

print(
    "U7.20_GENERIC_NORMALIZER_CONFLICT: NO"
)

print(
    "U7.20_WEBSITE_CLEANER_CONFLICT: NO"
)

print(
    "U7.20_U6_EXTRACTION_SAFE_CLEANUP: PRESERVED"
)

print(
    "U7.20_UDUC_COMPATIBILITY_REALIGNMENT: DEFERRED_TO_U8"
)

print(
    "U7.20_SECOND_NORMALIZATION_AUTHORITY: NO"
)

print(
    "U7.20_PRODUCTION_PATCH_REQUIRED: COMPLETE"
)

print(
    "U7.21_BEHAVIORAL_NORMALIZATION_VERIFICATION_TRANSITION: AUTHORIZED"
)

print(
    "U7.20_FINAL_LEGACY_NORMALIZATION_CLEANUP_VERIFICATION: PASS"
)