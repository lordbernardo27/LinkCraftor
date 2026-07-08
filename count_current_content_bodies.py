from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("backend/server/data")

PATHS = {
    "website_unified_content": ROOT / "website_unified_content",
    "uploaded_document_unified_content": ROOT / "uploaded_document_unified_content",
    "universal_unified_content_documents": ROOT / "universal_unified_content_documents",
    "universal_article_body_store": ROOT / "universal_article_body_store",
}


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def extract_docs(payload):
    if isinstance(payload, dict):
        if isinstance(payload.get("documents"), list):
            return [d for d in payload["documents"] if isinstance(d, dict)]
        if "document_id" in payload:
            return [payload]
    if isinstance(payload, list):
        return [d for d in payload if isinstance(d, dict)]
    return []


def has_body(doc):
    body = (
        doc.get("content_body")
        or doc.get("body_text")
        or doc.get("article_text")
        or doc.get("text")
        or ""
    )
    return bool(str(body).strip())


def scan_json_docs(folder: Path):
    total = 0
    with_body = 0
    by_source = {}

    if not folder.exists():
        return {"exists": False, "total": 0, "with_body": 0, "by_source": {}}

    for fp in folder.rglob("*.json"):
        payload = read_json(fp)
        docs = extract_docs(payload)

        for doc in docs:
            total += 1
            source = str(doc.get("source_type") or doc.get("type") or "unknown")
            by_source[source] = by_source.get(source, 0) + 1
            if has_body(doc):
                with_body += 1

    return {
        "exists": True,
        "total": total,
        "with_body": with_body,
        "by_source": by_source,
    }


def scan_body_store(folder: Path):
    total_records = 0
    available = 0
    by_source = {}

    if not folder.exists():
        return {"exists": False, "total_records": 0, "available": 0, "by_source": {}}

    for fp in folder.rglob("universal_article_body_index_*.json"):
        payload = read_json(fp) or {}
        bodies = payload.get("bodies") or []

        for body in bodies:
            if not isinstance(body, dict):
                continue
            total_records += 1
            source = str(body.get("source_type") or "unknown")
            by_source[source] = by_source.get(source, 0) + 1
            ref = Path(str(body.get("body_ref") or ""))
            if ref.exists() and ref.read_text(encoding="utf-8", errors="ignore").strip():
                available += 1

    return {
        "exists": True,
        "total_records": total_records,
        "available": available,
        "by_source": by_source,
    }


def main():
    print("CURRENT CONTENT BODY COUNT SCAN")
    print("=" * 60)

    for name, path in PATHS.items():
        print()
        print(name)
        print("-" * 60)
        print("Path:", path)

        if name == "universal_article_body_store":
            result = scan_body_store(path)
        else:
            result = scan_json_docs(path)

        for k, v in result.items():
            print(f"{k}: {v}")

    print()
    print("NOTE:")
    print("If UDUC / UUCD / Body Store counts are 0, that is expected after the safe reset.")
    print("Website Unified Content should show preserved website source bodies if they exist.")


if __name__ == "__main__":
    main()
