from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")
BASE = ROOT / "backend" / "server"

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

CANDIDATES = {
    "backend.server.stores.dom_article_structure_extractor":
        BASE / "stores" / "dom_article_structure_extractor.py",

    "backend.server.stores.helix_smart_extractor":
        BASE / "stores" / "helix_smart_extractor.py",

    "backend.server.stores.main_content_extraction_engine":
        BASE / "stores" / "main_content_extraction_engine.py",

    "backend.server.stores.smart_phrase_extractor_backup_before_v2":
        BASE / "stores" / "smart_phrase_extractor_backup_before_v2.py",
}


def live_files():
    for path in BASE.rglob("*.py"):
        if set(path.parts) & EXCLUDED:
            continue
        yield path


files = list(live_files())

print("=== U6.19 EXACT CANDIDATE DEPENDENCY SCAN ===")
print(f"LIVE_FILES={len(files)}")
print()

for module_name, candidate_path in CANDIDATES.items():
    print(f"=== {module_name} ===")

    importers = []

    for path in files:
        if path.resolve() == candidate_path.resolve():
            continue

        try:
            source = path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            tree = ast.parse(source)

        except SyntaxError:
            continue

        matched = False

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if (
                        alias.name == module_name
                        or alias.name.startswith(
                            module_name + "."
                        )
                    ):
                        matched = True

            elif isinstance(node, ast.ImportFrom):
                imported_module = node.module or ""

                if (
                    imported_module == module_name
                    or imported_module.startswith(
                        module_name + "."
                    )
                ):
                    matched = True

                parent = module_name.rsplit(".", 1)[0]
                leaf = module_name.rsplit(".", 1)[1]

                if imported_module == parent:
                    if any(
                        alias.name == leaf
                        for alias in node.names
                    ):
                        matched = True

        if matched:
            importers.append(
                path.relative_to(ROOT)
            )

    if importers:
        print("EXACT_IMPORTERS:")

        for importer in importers:
            print(f"  {importer}")

    else:
        print("EXACT_IMPORTERS: NONE")

    print()

print("U6.19_EXACT_DEPENDENCY_SCAN_COMPLETE: YES")
print("NO_FILES_MODIFIED: YES")