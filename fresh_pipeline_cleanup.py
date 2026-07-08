from pathlib import Path
import shutil

ROOT = Path("backend/server/data")
workspace = "ws_whattoexpect_com"

targets = [
    ROOT / "uploaded_document_unified_content" / workspace,
    ROOT / "universal_unified_content_documents" / workspace,
    ROOT / "universal_unified_content_documents" / f"universal_unified_content_documents_{workspace}.json",
    ROOT / "universal_article_body_store" / workspace,
    ROOT / "uucd_body_store_certifications" / workspace,
]

for target in targets:
    if target.exists():
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
        print("Deleted:", target)

print("Fresh pipeline cleanup complete.")
