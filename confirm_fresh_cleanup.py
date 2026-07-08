from pathlib import Path

ROOT = Path("backend/server/data")
workspace = "ws_whattoexpect_com"

paths = {
    "docs_original_uploads": ROOT / "docs" / workspace,
    "UDUC": ROOT / "uploaded_document_unified_content" / workspace,
    "UUCD_workspace_folder": ROOT / "universal_unified_content_documents" / workspace,
    "UUCD_main_collection": ROOT / "universal_unified_content_documents" / f"universal_unified_content_documents_{workspace}.json",
    "Body_Store": ROOT / "universal_article_body_store" / workspace,
    "Certification": ROOT / "uucd_body_store_certifications" / workspace,
}

print("FRESH CLEANUP CONFIRMATION")
print("=" * 70)

for name, path in paths.items():
    exists = path.exists()
    if path.is_dir():
        count = len(list(path.rglob("*")))
    else:
        count = 1 if path.exists() else 0

    print(f"{name}: exists={exists} | items={count} | {path}")

print("=" * 70)
print("Expected after cleanup:")
print("UDUC=False or 0 items")
print("UUCD main collection=False")
print("Body Store=False or 0 items")
print("Certification=False or 0 items")
print("docs_original_uploads may still exist because source uploads were preserved.")
