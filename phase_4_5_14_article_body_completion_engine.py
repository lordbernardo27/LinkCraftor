import json
import hashlib
import os
import re
import time
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser

WORKSPACE_ID = "ws_whattoexpect_com"
ROOT = Path("backend/server")

ARTICLE_INDEX_PATH = ROOT / "data/semantic/article_body_index_ws_whattoexpect_com.json"
UUCD_PATH = ROOT / "data/universal_unified_content_documents" / f"universal_unified_content_documents_{WORKSPACE_ID}.json"

BODY_STORE_DIR = ROOT / "data/universal_article_body_store" / WORKSPACE_ID
BODY_DIR = BODY_STORE_DIR / "bodies"
BODY_INDEX_PATH = BODY_STORE_DIR / f"universal_article_body_index_{WORKSPACE_ID}.json"

REPORT_DIR = ROOT / "data/article_body_completion_reports"
REPORT_PATH = REPORT_DIR / f"article_body_completion_report_{WORKSPACE_ID}.json"

MAX_TO_PROCESS = int(os.environ.get("MAX_TO_PROCESS", "50"))
REQUEST_DELAY_SECONDS = float(os.environ.get("REQUEST_DELAY_SECONDS", "0.5"))

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def stable_hash(value):
    return hashlib.sha256((value or "").encode("utf-8")).hexdigest()

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

def records(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ["articles", "documents", "records", "items", "pages", "data"]:
            if isinstance(payload.get(key), list):
                return payload[key]
    return []

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = False
        self.parts = []
        self.skip_tags = {"script", "style", "noscript", "svg", "header", "footer", "nav"}

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.skip_tags:
            self.skip = True

    def handle_endtag(self, tag):
        if tag.lower() in self.skip_tags:
            self.skip = False

    def handle_data(self, data):
        if not self.skip:
            text = data.strip()
            if text:
                self.parts.append(text)

    def text(self):
        raw = "\n".join(self.parts)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        raw = re.sub(r"[ \t]{2,}", " ", raw)
        return raw.strip()

def fetch_body(url):
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 LinkCraftorBot/1.0",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urlopen(req, timeout=20) as res:
        html = res.read().decode("utf-8", errors="ignore")

    parser = TextExtractor()
    parser.feed(html)
    text = parser.text()

    if len(text) < 1000:
        return "", "extracted_text_too_short"

    return text, None

def normalize_title(value):
    return str(value or "").strip().lower()

def load_body_index():
    if BODY_INDEX_PATH.exists():
        return read_json(BODY_INDEX_PATH)
    return {
        "schema_version": "universal_article_body_store.v1",
        "workspace_id": WORKSPACE_ID,
        "store_type": "universal_article_body_store",
        "generated_at": now_iso(),
        "body_directory": str(BODY_DIR),
        "counts": {},
        "rules": {
            "all_sources_share_one_body_store": True,
            "website_and_uploaded_documents_are_not_separated": True,
            "semantic_reader_loads_body_from_body_ref": True,
        },
        "bodies": [],
        "missing_bodies": [],
    }

def upsert_body(index, body_record):
    bodies = index.setdefault("bodies", [])
    existing = {b.get("document_id"): i for i, b in enumerate(bodies)}
    doc_id = body_record["document_id"]

    if doc_id in existing:
        bodies[existing[doc_id]] = body_record
    else:
        bodies.append(body_record)

    index["missing_bodies"] = [
        m for m in index.get("missing_bodies", [])
        if m.get("document_id") != doc_id
    ]

def main():
    BODY_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    article_payload = read_json(ARTICLE_INDEX_PATH)
    article_records = records(article_payload)

    uucd = read_json(UUCD_PATH)
    uucd_docs = uucd.get("documents", [])

    uucd_by_url = {d.get("canonical_url"): d for d in uucd_docs if d.get("canonical_url")}
    uucd_by_title = {normalize_title(d.get("title")): d for d in uucd_docs if d.get("title")}

    body_index = load_body_index()

    stored_existing = 0
    fetched_new = 0
    failed = []
    skipped_no_match = []
    processed_missing = 0

    for article in article_records:
        url = article.get("url")
        title = article.get("title")
        body_text = (article.get("body_text") or "").strip()

        uucd_doc = uucd_by_url.get(url) or uucd_by_title.get(normalize_title(title))

        if not uucd_doc:
            skipped_no_match.append({"url": url, "title": title})
            continue

        document_id = uucd_doc.get("document_id")

        if body_text:
            source = "existing_article_body_index"
        else:
            if processed_missing >= MAX_TO_PROCESS:
                continue

            processed_missing += 1
            try:
                body_text, error = fetch_body(url)
                time.sleep(REQUEST_DELAY_SECONDS)
                if error:
                    failed.append({"url": url, "title": title, "error": error})
                    continue
                article["body_text"] = body_text
                article["status"] = "body_completed"
                article["extracted_at_utc"] = now_iso()
                source = "fetched_and_extracted"
                fetched_new += 1
            except (HTTPError, URLError, TimeoutError, Exception) as exc:
                failed.append({"url": url, "title": title, "error": str(exc)})
                continue

        content_hash = stable_hash(body_text)
        body_ref = BODY_DIR / f"{document_id}.txt"
        body_ref.write_text(body_text, encoding="utf-8")

        body_record = {
            "document_id": document_id,
            "workspace_id": WORKSPACE_ID,
            "source_type": "crawled_web_page",
            "source_name": "whattoexpect.com",
            "title": uucd_doc.get("title") or title,
            "canonical_url": uucd_doc.get("canonical_url") or url,
            "body_status": "available",
            "body_key_used": "body_text",
            "body_ref": str(body_ref),
            "body_length": len(body_text),
            "content_hash": content_hash,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "completion_source": source,
        }

        upsert_body(body_index, body_record)

        uucd_doc["content_ref"] = str(body_ref)
        uucd_doc["body_status"] = "available"
        uucd_doc["content_hash"] = content_hash
        uucd_doc.setdefault("metadata", {})["content_ref"] = str(body_ref)
        uucd_doc.setdefault("metadata", {})["content_hash"] = content_hash

        if source == "existing_article_body_index":
            stored_existing += 1

    article_payload["updated_at_utc"] = now_iso()
    write_json(ARTICLE_INDEX_PATH, article_payload)

    body_index["generated_at"] = now_iso()
    body_index["uucd_path"] = str(UUCD_PATH)
    body_index["article_index_path"] = str(ARTICLE_INDEX_PATH)

    body_index["counts"] = {
        "uucd_documents": len(uucd_docs),
        "bodies_available": len(body_index.get("bodies", [])),
        "bodies_missing": len([d for d in uucd_docs if not d.get("content_ref") and d.get("source_type") == "crawled_web_page"]),
    }

    write_json(BODY_INDEX_PATH, body_index)
    write_json(UUCD_PATH, uucd)

    report = {
        "schema_version": "article_body_completion_report.v1",
        "workspace_id": WORKSPACE_ID,
        "generated_at": now_iso(),
        "max_to_process": MAX_TO_PROCESS,
        "stored_existing_from_article_index": stored_existing,
        "fetched_new_bodies": fetched_new,
        "failed_count": len(failed),
        "skipped_no_match_count": len(skipped_no_match),
        "failed": failed[:50],
        "skipped_no_match": skipped_no_match[:50],
        "body_index_path": str(BODY_INDEX_PATH),
    }

    write_json(REPORT_PATH, report)

    print("PHASE 4.5.14 ARTICLE BODY COMPLETION ENGINE RUN COMPLETE")
    print("stored_existing_from_article_index =", stored_existing)
    print("fetched_new_bodies =", fetched_new)
    print("failed_count =", len(failed))
    print("skipped_no_match_count =", len(skipped_no_match))
    print("body_index_path =", BODY_INDEX_PATH)
    print("report_path =", REPORT_PATH)

if __name__ == "__main__":
    main()
