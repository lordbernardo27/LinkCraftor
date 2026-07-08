import json
from pathlib import Path
from collections import Counter

ROOT = Path("backend/server")

BODY_KEYS = [
    "text", "content", "body", "article_body", "clean_text",
    "markdown", "raw_text", "extracted_text", "html_text"
]

SEARCH_ROOTS = [
    ROOT / "data",
    ROOT / "stores",
    ROOT / "artifacts",
    ROOT / "uploads",
    ROOT / "documents",
]

def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def extract_records(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ["documents", "records", "items", "pages", "data", "articles"]:
            if isinstance(payload.get(key), list):
                return payload[key]
        return [payload]
    return []

def best_body(record):
    best_key = None
    best_text = ""
    if not isinstance(record, dict):
        return None, ""
    for key in BODY_KEYS:
        value = record.get(key)
        if isinstance(value, str) and len(value.strip()) > len(best_text):
            best_key = key
            best_text = value.strip()
    return best_key, best_text

def main():
    candidates = []

    for base in SEARCH_ROOTS:
        if not base.exists():
            continue

        for path in base.rglob("*.json"):
            p = str(path).replace("\\", "/").lower()

            if "_quarantine" in p:
                continue

            payload = read_json(path)
            if payload is None:
                continue

            records = extract_records(payload)

            usable = 0
            max_len = 0
            body_keys = Counter()

            for record in records:
                key, body = best_body(record)
                if body:
                    usable += 1
                    max_len = max(max_len, len(body))
                    body_keys[key] += 1

            if usable:
                candidates.append({
                    "path": str(path),
                    "records_seen": len(records),
                    "usable_bodies": usable,
                    "max_body_length": max_len,
                    "body_keys": dict(body_keys),
                })

    candidates.sort(key=lambda x: (x["usable_bodies"], x["max_body_length"]), reverse=True)

    print("=" * 90)
    print("EXTRACTED ARTICLE BODY SOURCE LOCATOR")
    print("=" * 90)

    print("candidate_files_found =", len(candidates))

    for c in candidates[:50]:
        print("-" * 90)
        print("path =", c["path"])
        print("records_seen =", c["records_seen"])
        print("usable_bodies =", c["usable_bodies"])
        print("max_body_length =", c["max_body_length"])
        print("body_keys =", c["body_keys"])

if __name__ == "__main__":
    main()
