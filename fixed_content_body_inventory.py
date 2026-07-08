from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("backend/server/data")
ARCHIVES = ROOT / "_canonical_reset_archives"

SCAN_DIRS = {
    "active_website_unified_content": ROOT / "website_unified_content",
    "active_uploaded_document_unified_content": ROOT / "uploaded_document_unified_content",
    "active_uucd": ROOT / "universal_unified_content_documents",
    "active_body_store": ROOT / "universal_article_body_store",

    "preserved_docs": ROOT / "docs",
    "preserved_uploads": ROOT / "uploads",
    "preserved_raw_website_html": ROOT / "raw_website_html",
    "preserved_clean_website_html": ROOT / "clean_website_html",
}


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def text_file_has_body(path: Path) -> bool:
    try:
        return bool(path.read_text(encoding="utf-8", errors="ignore").strip())
    except Exception:
        return False


def extract_docs(payload):
    if isinstance(payload, dict):
        if isinstance(payload.get("documents"), list):
            return [d for d in payload["documents"] if isinstance(d, dict)]
        if isinstance(payload.get("items"), list):
            return [d for d in payload["items"] if isinstance(d, dict)]
        if "document_id" in payload or "doc_id" in payload:
            return [payload]
    if isinstance(payload, list):
        return [d for d in payload if isinstance(d, dict)]
    return []


def body_text(doc):
    return (
        doc.get("content_body")
        or doc.get("body_text")
        or doc.get("article_text")
        or doc.get("text")
        or doc.get("content")
        or ""
    )


def scan_json_folder(path: Path):
    total_json = 0
    docs = 0
    docs_with_body = 0
    by_source = {}

    if not path.exists():
        return {
            "exists": False,
            "json_files": 0,
            "docs": 0,
            "docs_with_body": 0,
            "by_source": {},
        }

    for fp in path.rglob("*.json"):
        total_json += 1
        payload = read_json(fp)
        rows = extract_docs(payload)

        for row in rows:
            docs += 1
            source = str(row.get("source_type") or row.get("type") or row.get("source") or "unknown")
            by_source[source] = by_source.get(source, 0) + 1
            if str(body_text(row)).strip():
                docs_with_body += 1

    return {
        "exists": True,
        "json_files": total_json,
        "docs": docs,
        "docs_with_body": docs_with_body,
        "by_source": by_source,
    }


def scan_text_like_folder(path: Path):
    if not path.exists():
        return {"exists": False, "files": 0, "files_with_text": 0}

    exts = {".txt", ".html", ".htm", ".md", ".json"}
    files = [p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in exts]

    with_text = sum(1 for p in files if text_file_has_body(p))

    return {
        "exists": True,
        "files": len(files),
        "files_with_text": with_text,
    }


def latest_archive():
    if not ARCHIVES.exists():
        return None
    items = [p for p in ARCHIVES.iterdir() if p.is_dir()]
    if not items:
        return None
    return sorted(items, key=lambda p: p.name)[-1]


def main():
    print("FIXED CURRENT CONTENT BODY INVENTORY")
    print("=" * 70)

    print("\nACTIVE + PRESERVED STORES")
    print("-" * 70)

    for name, path in SCAN_DIRS.items():
        print(f"\n{name}")
        print("Path:", path)

        if "raw_website_html" in name or "clean_website_html" in name or name in {"preserved_docs", "preserved_uploads"}:
            result = scan_text_like_folder(path)
        else:
            result = scan_json_folder(path)

        for k, v in result.items():
            print(f"{k}: {v}")

    archive = latest_archive()
    print("\nLATEST RESET ARCHIVE")
    print("-" * 70)

    if not archive:
        print("No archive found.")
        return

    print("Archive:", archive)

    for sub in [
        "uploaded_document_unified_content",
        "universal_unified_content_documents",
        "universal_article_body_store",
    ]:
        path = archive / sub
        print(f"\narchive_{sub}")
        print("Path:", path)

        if sub == "universal_article_body_store":
            result = scan_text_like_folder(path)
        else:
            result = scan_json_folder(path)

        for k, v in result.items():
            print(f"{k}: {v}")

    print("\nINTERPRETATION")
    print("-" * 70)
    print("Active generated stores may be 0 because we reset them.")
    print("Preserved source stores and latest archive show what can be rebuilt or restored.")
    print("If preserved clean/raw HTML and uploads contain files, the source data still exists.")


if __name__ == "__main__":
    main()
