import json, hashlib, os, time
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from backend.server.stores.website_source_pipeline_orchestrator import process_website_html_to_ucd_v1
from backend.server.stores.website_unified_content_store import get_website_unified_content_document_v1

WORKSPACE_ID = "ws_whattoexpect_com"
ROOT = Path("backend/server")

ARTICLE_INDEX_PATH = ROOT / "data/semantic/article_body_index_ws_whattoexpect_com.json"
UUCD_PATH = ROOT / "data/universal_unified_content_documents" / f"universal_unified_content_documents_{WORKSPACE_ID}.json"
BODY_STORE_DIR = ROOT / "data/universal_article_body_store" / WORKSPACE_ID
BODY_DIR = BODY_STORE_DIR / "bodies"
BODY_INDEX_PATH = BODY_STORE_DIR / f"universal_article_body_index_{WORKSPACE_ID}.json"

MAX_TO_PROCESS = int(os.environ.get("MAX_TO_PROCESS", "25"))
REQUEST_DELAY_SECONDS = float(os.environ.get("REQUEST_DELAY_SECONDS", "0.2"))

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def stable_hash(text):
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def norm_title(x):
    return str(x or "").strip().lower()

def fetch_html(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 LinkCraftorBot/1.0"})
    with urlopen(req, timeout=25) as res:
        return res.read().decode("utf-8", errors="ignore")

def article_records(payload):
    return payload.get("articles", []) if isinstance(payload, dict) else []

def body_is_clean_enough(text):
    bad_terms = [
        "get the app",
        "recommended reading",
        "see all getting pregnant topics",
        "popular articles",
        "follow us on",
        "do not sell my personal information",
    ]
    lower = text.lower()
    hits = [t for t in bad_terms if t in lower]
    return len(text.split()) >= 300 and len(hits) <= 2, hits

def upsert_body(index, record):
    bodies = index.setdefault("bodies", [])
    pos = {b.get("document_id"): i for i, b in enumerate(bodies)}
    if record["document_id"] in pos:
        bodies[pos[record["document_id"]]] = record
    else:
        bodies.append(record)

def main():
    BODY_DIR.mkdir(parents=True, exist_ok=True)

    article_payload = read_json(ARTICLE_INDEX_PATH)
    uucd = read_json(UUCD_PATH)
    body_index = read_json(BODY_INDEX_PATH)

    docs = uucd.get("documents", [])
    by_url = {d.get("canonical_url"): d for d in docs if d.get("canonical_url")}
    by_title = {norm_title(d.get("title")): d for d in docs if d.get("title")}

    existing_doc_ids = {b.get("document_id") for b in body_index.get("bodies", [])}

    processed = 0
    stored = 0
    failed = []

    for article in article_records(article_payload):
        if processed >= MAX_TO_PROCESS:
            break

        url = article.get("url")
        title = article.get("title")
        doc = by_url.get(url) or by_title.get(norm_title(title))

        if not doc:
            continue

        doc_id = doc.get("document_id")
        if doc_id in existing_doc_ids:
            continue

        try:
            html = fetch_html(url)

            process_website_html_to_ucd_v1(
                workspace_id=WORKSPACE_ID,
                url=url,
                html=html,
                title=title or doc.get("title") or "",
                h1=article.get("h1") or "",
                status_code=200,
                content_type="text/html",
                metadata={"source": "phase_4_5_14_clean_pipeline_completion"},
            )

            stored_doc = get_website_unified_content_document_v1(
                workspace_id=WORKSPACE_ID,
                url=url,
            )

            clean_body = ""
            if stored_doc:
                clean_body = (
                    stored_doc.get("primary_content")
                    or stored_doc.get("article_body")
                    or ""
                ).strip()

            ok, hits = body_is_clean_enough(clean_body)
            if not ok:
                failed.append({"url": url, "title": title, "reason": "clean_body_failed_quality_gate", "hits": hits})
                processed += 1
                time.sleep(REQUEST_DELAY_SECONDS)
                continue

            content_hash = stable_hash(clean_body)
            body_ref = BODY_DIR / f"{doc_id}.txt"
            body_ref.write_text(clean_body, encoding="utf-8")

            record = {
                "document_id": doc_id,
                "workspace_id": WORKSPACE_ID,
                "source_type": "crawled_web_page",
                "source_name": "whattoexpect.com",
                "title": doc.get("title") or title,
                "canonical_url": doc.get("canonical_url") or url,
                "body_status": "available",
                "body_key_used": "official_cleaned_article_body",
                "body_ref": str(body_ref),
                "body_length": len(clean_body),
                "content_hash": content_hash,
                "completion_source": "official_website_source_pipeline_orchestrator",
                "updated_at": now_iso(),
            }

            upsert_body(body_index, record)

            doc["content_ref"] = str(body_ref)
            doc["body_status"] = "available"
            doc["content_hash"] = content_hash
            doc.setdefault("metadata", {})["content_ref"] = str(body_ref)
            doc.setdefault("metadata", {})["content_hash"] = content_hash

            article["body_text"] = clean_body
            article["status"] = "clean_body_completed"
            article["extracted_at_utc"] = now_iso()

            stored += 1
            existing_doc_ids.add(doc_id)

        except Exception as exc:
            failed.append({"url": url, "title": title, "reason": str(exc)})

        processed += 1
        time.sleep(REQUEST_DELAY_SECONDS)

    body_index["generated_at"] = now_iso()
    body_index["counts"] = {
        "uucd_documents": len(docs),
        "bodies_available": len(body_index.get("bodies", [])),
        "website_bodies_available": sum(1 for b in body_index.get("bodies", []) if b.get("source_type") == "crawled_web_page"),
        "uploaded_bodies_available": sum(1 for b in body_index.get("bodies", []) if b.get("source_type") == "uploaded_document"),
    }

    write_json(BODY_INDEX_PATH, body_index)
    write_json(UUCD_PATH, uucd)
    write_json(ARTICLE_INDEX_PATH, article_payload)

    print("OFFICIAL CLEAN PIPELINE BATCH COMPLETE")
    print("processed =", processed)
    print("stored_clean_bodies =", stored)
    print("failed =", len(failed))
    print("sample_failures =", failed[:5])
    print("bodies_available =", body_index["counts"]["bodies_available"])
    print("website_bodies_available =", body_index["counts"]["website_bodies_available"])
    print("uploaded_bodies_available =", body_index["counts"]["uploaded_bodies_available"])

if __name__ == "__main__":
    main()
