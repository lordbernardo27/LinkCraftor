from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("backend/server/data")
WORKSPACE_ID = "ws_whattoexpect_com"

UUCD_PATH = ROOT / "universal_unified_content_documents" / f"universal_unified_content_documents_{WORKSPACE_ID}.json"
BODY_INDEX_PATH = ROOT / "universal_article_body_store" / WORKSPACE_ID / f"universal_article_body_index_{WORKSPACE_ID}.json"
CERT_PATH = ROOT / "uucd_body_store_certifications" / WORKSPACE_ID / f"uucd_body_store_certification_{WORKSPACE_ID}.json"

SEARCH_ROOTS = [
    ROOT,
    Path("."),
]


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def body_value(doc: dict) -> str:
    return str(
        doc.get("content_body")
        or doc.get("body_text")
        or doc.get("article_text")
        or doc.get("text")
        or doc.get("content")
        or ""
    )


def summarize_uucd():
    data = read_json(UUCD_PATH) or {}
    docs = data.get("documents") or []

    body_docs = [d for d in docs if body_value(d).strip()]
    no_body_docs = [d for d in docs if not body_value(d).strip()]

    by_source = {}
    for d in docs:
        st = str(d.get("source_type") or "unknown")
        by_source[st] = by_source.get(st, 0) + 1

    return {
        "exists": UUCD_PATH.exists(),
        "path": str(UUCD_PATH),
        "total_docs": len(docs),
        "docs_with_body": len(body_docs),
        "docs_without_body": len(no_body_docs),
        "by_source": by_source,
        "sample_without_body": [
            {
                "document_id": d.get("document_id"),
                "source_type": d.get("source_type"),
                "title": d.get("title"),
                "source_identity": d.get("source_identity"),
            }
            for d in no_body_docs[:10]
        ],
    }


def summarize_body_index():
    data = read_json(BODY_INDEX_PATH) or {}
    bodies = data.get("bodies") or []
    missing = data.get("missing_bodies") or []
    duplicates = data.get("duplicate_hashes") or []

    body_ids = {b.get("document_id") for b in bodies if isinstance(b, dict)}

    return {
        "exists": BODY_INDEX_PATH.exists(),
        "path": str(BODY_INDEX_PATH),
        "body_records": len(bodies),
        "missing_bodies": len(missing),
        "duplicate_hashes": len(duplicates),
        "body_ids_sample": list(sorted(body_ids))[:20],
        "missing_sample": missing[:20],
    }


def summarize_cert():
    data = read_json(CERT_PATH) or {}

    return {
        "exists": CERT_PATH.exists(),
        "path": str(CERT_PATH),
        "certified": data.get("certified"),
        "semantic_ready": data.get("semantic_ready"),
        "certification_level": data.get("certification_level"),
        "problems": data.get("problems", [])[:50],
        "counts": data.get("counts"),
        "verification": data.get("verification"),
    }


def find_website_candidates():
    candidates = []

    keywords = [
        "website",
        "unified",
        "uucd",
        "html",
        "raw",
        "clean",
        "whattoexpect",
        "crawled",
        "page",
    ]

    for root in SEARCH_ROOTS:
        if not root.exists():
            continue

        for fp in root.rglob("*"):
            if not fp.is_file():
                continue

            if any(skip in str(fp).lower() for skip in [".venv", "node_modules", ".git", "__pycache__"]):
                continue

            name = fp.name.lower()
            full = str(fp).lower()

            if fp.suffix.lower() not in {".json", ".html", ".htm", ".txt"}:
                continue

            if not any(k in full for k in keywords):
                continue

            try:
                size = fp.stat().st_size
            except Exception:
                size = 0

            candidates.append({
                "path": str(fp),
                "suffix": fp.suffix.lower(),
                "size": size,
            })

    candidates = sorted(candidates, key=lambda x: x["size"], reverse=True)

    return candidates[:100]


def find_large_json_docs():
    rows = []

    for fp in ROOT.rglob("*.json"):
        payload = read_json(fp)
        if payload is None:
            continue

        docs = []
        if isinstance(payload, dict) and isinstance(payload.get("documents"), list):
            docs = payload.get("documents")
        elif isinstance(payload, list):
            docs = payload

        if docs:
            source_counts = {}
            with_body = 0

            for d in docs:
                if not isinstance(d, dict):
                    continue
                st = str(d.get("source_type") or d.get("type") or "unknown")
                source_counts[st] = source_counts.get(st, 0) + 1
                if body_value(d).strip():
                    with_body += 1

            rows.append({
                "path": str(fp),
                "doc_count": len(docs),
                "with_body": with_body,
                "source_counts": source_counts,
            })

    return sorted(rows, key=lambda x: x["doc_count"], reverse=True)[:50]


def main():
    print("AUTOMATIC REBUILD AUTOPSY")
    print("=" * 70)

    print("\n1. UUCD SUMMARY")
    print("-" * 70)
    for k, v in summarize_uucd().items():
        print(f"{k}: {v}")

    print("\n2. BODY INDEX SUMMARY")
    print("-" * 70)
    for k, v in summarize_body_index().items():
        print(f"{k}: {v}")

    print("\n3. CERTIFICATION SUMMARY")
    print("-" * 70)
    cert = summarize_cert()
    for k, v in cert.items():
        print(f"{k}: {v}")

    print("\n4. LARGE JSON DOCUMENT COLLECTIONS")
    print("-" * 70)
    for row in find_large_json_docs():
        print(row)

    print("\n5. WEBSITE CANDIDATE FILES")
    print("-" * 70)
    for row in find_website_candidates():
        print(row)


if __name__ == "__main__":
    main()
