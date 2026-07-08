import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

WORKSPACE_ID = "ws_whattoexpect_com"
ROOT = Path("backend/server")

UUCD_PATH = ROOT / "data/universal_unified_content_documents" / f"universal_unified_content_documents_{WORKSPACE_ID}.json"

STORE_DIR = ROOT / "data/universal_article_body_store" / WORKSPACE_ID
BODY_DIR = STORE_DIR / "bodies"
INDEX_PATH = STORE_DIR / f"universal_article_body_index_{WORKSPACE_ID}.json"

BODY_KEYS = [
    "text",
    "content",
    "body",
    "article_body",
    "clean_text",
    "markdown",
    "raw_text",
    "extracted_text",
    "html_text",
]

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def stable_hash(value):
    return hashlib.sha256((value or "").encode("utf-8")).hexdigest()

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

def best_body(doc):
    best_key = None
    best_text = ""

    for key in BODY_KEYS:
        value = doc.get(key)
        if isinstance(value, str) and len(value.strip()) > len(best_text):
            best_key = key
            best_text = value.strip()

    return best_key, best_text

def main():
    if not UUCD_PATH.exists():
        raise FileNotFoundError(f"Missing UUCD store: {UUCD_PATH}")

    BODY_DIR.mkdir(parents=True, exist_ok=True)

    uucd = read_json(UUCD_PATH)
    docs = uucd.get("documents", [])

    body_records = []
    missing_records = []

    for doc in docs:
        document_id = doc.get("document_id")

        if not document_id:
            continue

        body_key, body_text = best_body(doc)

        if not body_text:
            missing_records.append({
                "document_id": document_id,
                "workspace_id": WORKSPACE_ID,
                "source_type": doc.get("source_type"),
                "source_name": doc.get("source_name"),
                "title": doc.get("title"),
                "canonical_url": doc.get("canonical_url"),
                "body_status": "missing",
                "reason": "No usable extracted article body found yet.",
            })
            continue

        content_hash = stable_hash(body_text)
        body_ref = BODY_DIR / f"{document_id}.txt"
        body_ref.write_text(body_text, encoding="utf-8")

        body_records.append({
            "document_id": document_id,
            "workspace_id": WORKSPACE_ID,
            "source_type": doc.get("source_type"),
            "source_name": doc.get("source_name"),
            "title": doc.get("title"),
            "canonical_url": doc.get("canonical_url"),
            "body_status": "available",
            "body_key_used": body_key,
            "body_ref": str(body_ref),
            "body_length": len(body_text),
            "content_hash": content_hash,
            "created_at": now_iso(),
            "updated_at": now_iso(),
        })

    available_by_source = Counter(b["source_type"] for b in body_records)
    missing_by_source = Counter(m["source_type"] for m in missing_records)

    index = {
        "schema_version": "universal_article_body_store.v1",
        "workspace_id": WORKSPACE_ID,
        "store_type": "universal_article_body_store",
        "generated_at": now_iso(),
        "uucd_path": str(UUCD_PATH),
        "body_directory": str(BODY_DIR),
        "counts": {
            "uucd_documents": len(docs),
            "bodies_available": len(body_records),
            "bodies_missing": len(missing_records),
            "available_by_source_type": dict(available_by_source),
            "missing_by_source_type": dict(missing_by_source),
        },
        "rules": {
            "all_sources_share_one_body_store": True,
            "website_and_uploaded_documents_are_not_separated": True,
            "semantic_reader_loads_body_from_body_ref": True,
            "uucd_remains_identity_metadata_and_routing_layer": True,
            "missing_bodies_are_tracked_not_silently_ignored": True,
        },
        "bodies": body_records,
        "missing_bodies": missing_records,
    }

    write_json(INDEX_PATH, index)

    print("UNIVERSAL ARTICLE BODY STORE BUILT")
    print("index_path =", INDEX_PATH)
    print("body_directory =", BODY_DIR)
    print("uucd_documents =", len(docs))
    print("bodies_available =", len(body_records))
    print("bodies_missing =", len(missing_records))
    print("available_by_source_type =", dict(available_by_source))
    print("missing_by_source_type =", dict(missing_by_source))

if __name__ == "__main__":
    main()
