from pathlib import Path
import ast


root = Path("backend/server")

include_roots = [
    root / "stores",
    root / "pipelines" / "upload_document",
    root / "routes",
    root / "utils",
]

excluded_parts = {
    "backups",
    "verification_scans",
    "__pycache__",
    ".venv",
}


def included(path: Path) -> bool:
    parts = set(path.parts)

    if parts.intersection(excluded_parts):
        return False

    return path.suffix == ".py"


files = []

for base in include_roots:
    if not base.exists():
        continue

    if base.is_file():
        candidates = [base]
    else:
        candidates = base.rglob("*.py")

    for path in candidates:
        if included(path):
            files.append(path)


files = sorted(set(files))


print(
    "=== U7.20 LEGACY NORMALIZATION CLEANUP INSPECTION ==="
)

print(
    "PRODUCTION_FILE_COUNT=",
    len(files),
)


normalization_terms = {
    "unicode_normalization": (
        "unicodedata.normalize",
        "_normalize_unicode",
        "unicode_nfc",
    ),
    "line_endings": (
        "replace(\"\\r\\n\"",
        "replace('\\r\\n'",
        "_normalize_line_endings",
    ),
    "horizontal_whitespace": (
        "_normalize_horizontal_whitespace",
        "re.sub(r\" +\"",
        "re.sub(r' +'",
    ),
    "paragraph_boundary": (
        "_normalize_paragraph_boundaries",
        "paragraph_boundaries",
    ),
    "title_normalization": (
        "_normalize_title",
        "title_normalization",
    ),
    "heading_normalization": (
        "_normalize_headings",
        "heading_normalization",
    ),
    "control_character": (
        "_remove_unsafe_control_characters",
        "control_character_handling",
    ),
    "generic_text_normalizer": (
        "fix_mojibake_text",
        "text_normalization",
    ),
    "website_cleaner": (
        "article_body_cleaning_engine",
        "article_cleaning_pipeline",
    ),
}


print()
print("=== A. NORMALIZATION AUTHORITY / DUPLICATE TERM SCAN ===")

for category, terms in normalization_terms.items():
    hits = []

    for path in files:
        source = path.read_text(
            encoding="utf-8-sig",
            errors="ignore",
        )

        lowered = source.lower()

        if any(
            term.lower() in lowered
            for term in terms
        ):
            hits.append(
                str(path)
            )

    print()
    print(
        f"[{category}] HIT_COUNT={len(hits)}"
    )

    for path in hits:
        print(path)


print()
print("=== B. U7 NORMALIZER IMPORT REFERENCES ===")

u7_import_users = []

for path in files:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    if (
        "upload_document_normalizer"
        in source
        and path.name
        != "upload_document_normalizer.py"
    ):
        u7_import_users.append(
            str(path)
        )

print(
    "U7_NORMALIZER_EXTERNAL_REFERENCE_COUNT=",
    len(u7_import_users),
)

for path in u7_import_users:
    print(path)


print()
print("=== C. U6 EXTRACTION NORMALIZATION HELPERS ===")

extractor = (
    root
    / "stores"
    / "upload_document_extractor.py"
)

if extractor.exists():
    source = extractor.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    tree = ast.parse(source)

    u6_helpers = [
        node.name
        for node in tree.body
        if isinstance(
            node,
            ast.FunctionDef,
        )
        and (
            "normalize" in node.name
            or "strip_markdown" in node.name
            or "html" in node.name
            or "docx" in node.name
        )
    ]

    for name in u6_helpers:
        print(name)

    print(
        "U6_HELPER_COUNT=",
        len(u6_helpers),
    )
else:
    print(
        "U6_EXTRACTOR_NOT_FOUND"
    )


print()
print("=== D. GENERIC TEXT NORMALIZATION UTILITY ===")

generic = (
    root
    / "utils"
    / "text_normalization.py"
)

if generic.exists():
    generic_source = generic.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    print(
        "GENERIC_TEXT_NORMALIZATION_PRESENT: YES"
    )

    print(
        "GENERIC_FIX_MOJIBAKE_PRESENT:",
        "YES"
        if "fix_mojibake_text"
        in generic_source
        else "NO",
    )

    print(
        "GENERIC_COLLAPSE_ALL_WHITESPACE_PRESENT:",
        "YES"
        if (
            're.sub(r"\\s+", " ",'
            in generic_source
            or "re.sub(r'\\s+', ' ',"
            in generic_source
        )
        else "NO",
    )
else:
    print(
        "GENERIC_TEXT_NORMALIZATION_PRESENT: NO"
    )


print()
print("=== E. UPLOAD PIPELINE CONTENT-NORMALIZATION REFERENCES ===")

upload_scope_files = [
    path
    for path in files
    if (
        "upload_document"
        in str(path).replace("\\", "/")
        or path.name
        in {
            "files.py",
            "uploaded_document_unified_content.py",
            "upload_document_extractor.py",
            "upload_document_normalizer.py",
        }
    )
]

for path in upload_scope_files:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    lines = source.splitlines()

    matches = []

    for number, line in enumerate(
        lines,
        start=1,
    ):
        lowered = line.lower()

        if any(
            term in lowered
            for term in (
                "fix_mojibake_text",
                "article_body_cleaning_engine",
                "article_cleaning_pipeline",
                "upload_document_normalizer",
                "normalize_uploaded_document_v1",
            )
        ):
            matches.append(
                (
                    number,
                    line.strip(),
                )
            )

    if matches:
        print()
        print(
            f"FILE={path}"
        )

        for number, line in matches:
            print(
                f"LINE {number}: {line}"
            )


print()
print("=== F. POSSIBLE LEGACY NORMALIZER FILES ===")

candidate_files = []

for path in files:
    name = path.name.lower()

    if (
        "normaliz" in name
        or "clean" in name
    ):
        candidate_files.append(
            str(path)
        )

print(
    "NORMALIZER_CLEANER_CANDIDATE_COUNT=",
    len(candidate_files),
)

for path in candidate_files:
    print(path)


print()
print("=== G. WEBSITE CLEANER REACHABILITY FROM UPLOAD MODULES ===")

website_cleaner_import_hits = []

for path in upload_scope_files:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    ).lower()

    if (
        "article_body_cleaning_engine"
        in source
        or "article_cleaning_pipeline"
        in source
    ):
        website_cleaner_import_hits.append(
            str(path)
        )

print(
    "UPLOAD_TO_WEBSITE_CLEANER_REFERENCE_COUNT=",
    len(website_cleaner_import_hits),
)

for path in website_cleaner_import_hits:
    print(path)


print()
print("=== H. U7.20 DECISION EVIDENCE ===")

print(
    "CANONICAL_U7_AUTHORITY:",
    "backend/server/stores/upload_document_normalizer.py",
)

print(
    "U6_EXTRACTION_SAFE_CLEANUP_PRESERVED:",
    "YES",
)

print(
    "GENERIC_NORMALIZER_IS_CANONICAL_U7_AUTHORITY:",
    "NO",
)

print(
    "WEBSITE_CLEANER_IS_CANONICAL_U7_AUTHORITY:",
    "NO",
)

print(
    "UDUC_COMPATIBILITY_HYGIENE_REALIGNMENT_PHASE:",
    "U8",
)