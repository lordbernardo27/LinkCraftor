from pathlib import Path
import ast


root = Path("backend/server")

excluded = {
    "backups",
    "verification_scans",
    "__pycache__",
}


def production_files():
    out = []

    for path in root.rglob("*.py"):
        if set(path.parts).intersection(excluded):
            continue

        out.append(path)

    return sorted(out)


files = production_files()


print(
    "=== U7.20 TARGETED REACHABILITY INSPECTION ==="
)


# ------------------------------------------------------------
# A. Inspect upload_phrase_pool_builder
# ------------------------------------------------------------

upload_phrase_pool = (
    root
    / "stores"
    / "upload_phrase_pool_builder.py"
)

print()
print(
    "=== A. upload_phrase_pool_builder.py ==="
)

if not upload_phrase_pool.exists():
    print("FILE_NOT_FOUND")
else:
    source = upload_phrase_pool.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    tree = ast.parse(source)

    print("IMPORTS:")

    for node in tree.body:
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        ):
            print(
                ast.get_source_segment(
                    source,
                    node,
                )
            )

    print()
    print("FUNCTIONS:")

    for node in tree.body:
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            print(node.name)

    print()
    print("NORMALIZATION CALLS:")

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        code = (
            ast.get_source_segment(
                source,
                node,
            )
            or ""
        )

        lowered = code.lower()

        if (
            "fix_mojibake_text" in lowered
            or "normalize" in lowered
        ):
            print(
                f"LINE {node.lineno}: {code}"
            )


# ------------------------------------------------------------
# B. Find production callers/importers of upload_phrase_pool_builder
# ------------------------------------------------------------

print()
print(
    "=== B. upload_phrase_pool_builder REFERENCES ==="
)

phrase_pool_refs = []

for path in files:
    if path == upload_phrase_pool:
        continue

    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    if (
        "upload_phrase_pool_builder"
        in source
    ):
        phrase_pool_refs.append(path)

print(
    "UPLOAD_PHRASE_POOL_BUILDER_REFERENCE_COUNT=",
    len(phrase_pool_refs),
)

for path in phrase_pool_refs:
    print(path)


# ------------------------------------------------------------
# C. Check whether current Uploaded Document modules reference it
# ------------------------------------------------------------

print()
print(
    "=== C. CURRENT UPLOADED DOCUMENT PATH REFERENCES ==="
)

current_upload_candidates = []

for path in files:
    normalized = str(path).replace(
        "\\",
        "/",
    )

    if (
        "/pipelines/upload_document/"
        in normalized
        or path.name in {
            "files.py",
            "upload_document_extractor.py",
            "upload_document_normalizer.py",
            "uploaded_document_unified_content.py",
        }
    ):
        current_upload_candidates.append(
            path
        )

upload_path_phrase_refs = []

generic_normalizer_refs = []

for path in current_upload_candidates:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    if (
        "upload_phrase_pool_builder"
        in source
    ):
        upload_path_phrase_refs.append(
            path
        )

    if (
        "fix_mojibake_text"
        in source
        or "utils.text_normalization"
        in source
        or "text_normalization import"
        in source
    ):
        generic_normalizer_refs.append(
            path
        )

print(
    "CURRENT_UPLOAD_PATH_TO_UPLOAD_PHRASE_POOL_REFERENCE_COUNT=",
    len(upload_path_phrase_refs),
)

for path in upload_path_phrase_refs:
    print(path)

print(
    "CURRENT_UPLOAD_PATH_TO_GENERIC_NORMALIZER_REFERENCE_COUNT=",
    len(generic_normalizer_refs),
)

for path in generic_normalizer_refs:
    print(path)


# ------------------------------------------------------------
# D. Inspect suspicious live backup-named module
# ------------------------------------------------------------

legacy_backup_module = (
    root
    / "stores"
    / "smart_phrase_extractor_backup_before_v2.py"
)

print()
print(
    "=== D. LIVE BACKUP-NAMED MODULE ==="
)

print(
    "SMART_PHRASE_BACKUP_FILE_PRESENT:",
    "YES"
    if legacy_backup_module.exists()
    else "NO",
)


# ------------------------------------------------------------
# E. Find imports/references to suspicious backup module
# ------------------------------------------------------------

print()
print(
    "=== E. BACKUP MODULE REFERENCES ==="
)

backup_refs = []

if legacy_backup_module.exists():
    for path in files:
        if path == legacy_backup_module:
            continue

        source = path.read_text(
            encoding="utf-8-sig",
            errors="ignore",
        )

        if (
            "smart_phrase_extractor_backup_before_v2"
            in source
        ):
            backup_refs.append(path)

print(
    "SMART_PHRASE_BACKUP_REFERENCE_COUNT=",
    len(backup_refs),
)

for path in backup_refs:
    print(path)


# ------------------------------------------------------------
# F. Decision evidence
# ------------------------------------------------------------

print()
print(
    "=== F. U7.20 TARGETED EVIDENCE ==="
)

print(
    "GENERIC_NORMALIZER_DIRECTLY_REACHABLE_FROM_CURRENT_UPLOAD_PATH:",
    "YES"
    if generic_normalizer_refs
    else "NO",
)

print(
    "UPLOAD_PHRASE_POOL_DIRECTLY_REACHABLE_FROM_CURRENT_UPLOAD_PATH:",
    "YES"
    if upload_path_phrase_refs
    else "NO",
)

print(
    "LIVE_BACKUP_MODULE_HAS_PRODUCTION_REFERENCES:",
    "YES"
    if backup_refs
    else "NO",
)