import json
from pathlib import Path
from collections import Counter

WORKSPACE_ID = "ws_whattoexpect_com"

INDEX_PATH = Path("backend/server/data/semantic/article_body_index_ws_whattoexpect_com.json")
UUCD_PATH = Path(
    "backend/server/data/universal_unified_content_documents/"
    f"universal_unified_content_documents_{WORKSPACE_ID}.json"
)

BODY_KEYS = [
    "body_text",
    "article_body",
    "text",
    "content",
    "clean_text",
    "main_content",
    "page_text",
    "extracted_text",
]

ID_KEYS = [
    "document_id",
    "id",
    "url",
    "canonical_url",
    "title",
    "page_title",
]

def load(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))

def records(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ["documents", "records", "items", "pages", "data", "articles", "index"]:
            if isinstance(payload.get(key), list):
                return payload[key]
        return [payload]
    return []

def best_body(record):
    best_key = None
    best_text = ""
    for key in BODY_KEYS:
        value = record.get(key)
        if isinstance(value, str) and len(value.strip()) > len(best_text):
            best_key = key
            best_text = value.strip()
    return best_key, best_text

def main():
    article_payload = load(INDEX_PATH)
    article_records = records(article_payload)

    uucd = load(UUCD_PATH)
    uucd_docs = uucd.get("documents", [])

    uucd_by_id = {d.get("document_id"): d for d in uucd_docs if d.get("document_id")}
    uucd_by_url = {d.get("canonical_url"): d for d in uucd_docs if d.get("canonical_url")}
    uucd_by_title = {str(d.get("title", "")).strip().lower(): d for d in uucd_docs if d.get("title")}

    print("=" * 90)
    print("ARTICLE BODY INDEX INSPECTION")
    print("=" * 90)

    print("index_path =", INDEX_PATH)
    print("payload_type =", type(article_payload).__name__)
    print("records =", len(article_records))

    if isinstance(article_payload, dict):
        print("top_level_keys =", list(article_payload.keys()))

    print("\n[1] RECORD KEY SHAPES")
    key_shapes = Counter()
    for rec in article_records:
        if isinstance(rec, dict):
            key_shapes[tuple(sorted(rec.keys()))] += 1

    for shape, count in key_shapes.most_common(10):
        print("-" * 70)
        print("count =", count)
        print("keys =", list(shape))

    print("\n[2] BODY FIELD STATUS")
    body_counts = Counter()
    usable = []
    empty = []

    for rec in article_records:
        if not isinstance(rec, dict):
            continue
        key, text = best_body(rec)
        if text:
            body_counts[key] += 1
            usable.append((rec, key, len(text)))
        else:
            empty.append(rec)

    print("usable_body_records =", len(usable))
    print("empty_body_records =", len(empty))
    print("body_counts =", dict(body_counts))

    if usable:
        lengths = [length for _, _, length in usable]
        print("min_body_length =", min(lengths))
        print("max_body_length =", max(lengths))
        print("avg_body_length =", round(sum(lengths) / len(lengths), 2))

    print("\n[3] SAMPLE USABLE RECORDS")
    for rec, key, length in usable[:5]:
        print("-" * 70)
        for k in ID_KEYS:
            if k in rec:
                print(k, "=", rec.get(k))
        print("body_key =", key)
        print("body_length =", length)
        print("all_keys =", list(rec.keys()))

    print("\n[4] SAMPLE EMPTY RECORDS")
    for rec in empty[:5]:
        print("-" * 70)
        for k in ID_KEYS:
            if k in rec:
                print(k, "=", rec.get(k))
        print("all_keys =", list(rec.keys()) if isinstance(rec, dict) else type(rec).__name__)

    print("\n[5] MATCHABILITY TO UUCD")
    match_by_id = 0
    match_by_url = 0
    match_by_title = 0
    no_match = 0

    for rec in article_records:
        if not isinstance(rec, dict):
            continue

        doc_id = rec.get("document_id") or rec.get("id")
        url = rec.get("canonical_url") or rec.get("url")
        title = str(rec.get("title") or rec.get("page_title") or "").strip().lower()

        if doc_id and doc_id in uucd_by_id:
            match_by_id += 1
        elif url and url in uucd_by_url:
            match_by_url += 1
        elif title and title in uucd_by_title:
            match_by_title += 1
        else:
            no_match += 1

    print("match_by_id =", match_by_id)
    print("match_by_url =", match_by_url)
    print("match_by_title =", match_by_title)
    print("no_match =", no_match)

    print("\n[6] DECISION")
    if usable:
        print("This index contains usable article bodies and can be used to populate the Universal Article Body Store.")
    else:
        print("This index does not contain usable article bodies.")

if __name__ == "__main__":
    main()
