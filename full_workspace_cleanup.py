from pathlib import Path
import shutil

ROOT = Path("backend/server/data")
workspaces = [
    "default",
    "ws_whattoexpect_com",
    "ws_betterhealthcheck_com",
    "ws_betterhealthcheck_com_2",
]

targets = []

for ws in workspaces:
    targets += [
        ROOT / "docs" / ws,
        ROOT / "uploaded_document_unified_content" / ws,
        ROOT / "universal_article_body_store" / ws,
        ROOT / "uucd_body_store_certifications" / ws,
        ROOT / "universal_unified_content_documents" / ws,
        ROOT / "universal_unified_content_documents" / f"universal_unified_content_documents_{ws}.json",
    ]

for target in targets:
    if target.exists():
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
        print("Deleted:", target)

print("FULL source + generated cleanup complete.")
