import json
from pathlib import Path
from collections import Counter

WORKSPACE_ID = "ws_whattoexpect_com"
ROOT = Path("backend/server")

UUCD_PATH = ROOT / "data/universal_unified_content_documents" / f"universal_unified_content_documents_{WORKSPACE_ID}.json"
INDEX_PATH = ROOT / "data/universal_article_body_store" / WORKSPACE_ID / f"universal_article_body_index_{WORKSPACE_ID}.json"

def fail(msg):
    raise AssertionError(msg)

def main():
    if not UUCD_PATH.exists():
        fail(f"Missing UUCD store: {UUCD_PATH}")

    if not INDEX_PATH.exists():
        fail(f"Missing Universal Article Body Store index: {INDEX_PATH}")

    uucd = json.loads(UUCD_PATH.read_text(encoding="utf-8"))
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))

    docs = uucd.get("documents", [])
    bodies = index.get("bodies", [])

    uucd_doc_ids = {d.get("document_id") for d in docs if d.get("document_id")}
    website_doc_ids = {
        d.get("document_id")
        for d in docs
        if d.get("source_type") == "crawled_web_page" and d.get("document_id")
    }
    uploaded_doc_ids = {
        d.get("document_id")
        for d in docs
        if d.get("source_type") == "uploaded_document" and d.get("document_id")
    }

    body_doc_ids = {b.get("document_id") for b in bodies if b.get("document_id")}
    website_body_ids = {
        b.get("document_id")
        for b in bodies
        if b.get("source_type") == "crawled_web_page" and b.get("document_id")
    }
    uploaded_body_ids = {
        b.get("document_id")
        for b in bodies
        if b.get("source_type") == "uploaded_document" and b.get("document_id")
    }

    missing_files = []
    empty_files = []

    for body in bodies:
        ref = Path(body.get("body_ref", ""))
        if not ref.exists():
            missing_files.append(str(ref))
            continue
        if ref.stat().st_size <= 0:
            empty_files.append(str(ref))

    if missing_files:
        fail(f"Body files missing: {missing_files[:20]}")

    if empty_files:
        fail(f"Body files empty: {empty_files[:20]}")

    hashes = Counter(
        b.get("content_hash")
        for b in bodies
        if b.get("source_type") == "crawled_web_page" and b.get("content_hash")
    )
    duplicate_hashes = [h for h, c in hashes.items() if c > 1]

    source_counts = Counter(b.get("source_type") for b in bodies)

    website_missing = website_doc_ids - website_body_ids
    uploaded_missing = uploaded_doc_ids - uploaded_body_ids
    orphan_body_ids = body_doc_ids - uucd_doc_ids

    if orphan_body_ids:
        fail(f"Body records not found in UUCD: {list(orphan_body_ids)[:20]}")

    if duplicate_hashes:
        fail(f"Duplicate website body hashes found: {duplicate_hashes[:20]}")

    print("UNIVERSAL ARTICLE BODY STORE VERIFICATION PASSED")
    print("index_path =", INDEX_PATH)
    print("uucd_documents =", len(uucd_doc_ids))
    print("website_uucd_documents =", len(website_doc_ids))
    print("uploaded_uucd_documents =", len(uploaded_doc_ids))
    print("bodies_available =", len(bodies))
    print("website_bodies_available =", len(website_body_ids))
    print("website_bodies_missing =", len(website_missing))
    print("uploaded_bodies_available =", len(uploaded_body_ids))
    print("uploaded_bodies_missing =", len(uploaded_missing))
    print("available_by_source_type =", dict(source_counts))
    print("duplicate_website_body_hashes =", len(duplicate_hashes))
    print("body_files_verified =", len(bodies))

if __name__ == "__main__":
    main()
