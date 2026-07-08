from pathlib import Path
import json
import re
from collections import Counter

ROOT = Path("backend/server")

CODE_EXTS = {".py"}
DATA_EXTS = {".json", ".jsonl", ".txt", ".md", ".html", ".htm"}

SEARCH_TERMS = [
    "article_body",
    "clean_text",
    "extracted_text",
    "main_content",
    "body_text",
    "page_text",
    "readability",
    "crawler",
    "extractor",
    "cleaner",
    "whattoexpect",
    "live_domain",
    "target_pool",
]

BODY_KEYS = [
    "text", "content", "body", "article_body", "clean_text",
    "markdown", "raw_text", "extracted_text", "html_text",
    "main_content", "body_text", "page_text", "readable_text",
    "cleaned_content", "normalized_content"
]

def safe_read(path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def records_from_json(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ["documents", "records", "items", "pages", "data", "articles", "results"]:
            if isinstance(payload.get(key), list):
                return payload[key]
        return [payload]
    return []

print("=" * 90)
print("WEBSITE ARTICLE BODY PIPELINE LOCATOR")
print("=" * 90)

print("\n[1] CODE FILES THAT MENTION CRAWLER / EXTRACTOR / BODY TERMS")
matches = []
for path in ROOT.rglob("*.py"):
    text = safe_read(path)
    lowered = text.lower()
    hits = [t for t in SEARCH_TERMS if t.lower() in lowered]
    if hits:
        matches.append((str(path), hits[:10]))

for path, hits in matches[:80]:
    print("-" * 80)
    print("path =", path)
    print("hits =", hits)

print("\n[2] DATA FILES WITH POSSIBLE ARTICLE BODY FIELDS")
candidates = []
for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in DATA_EXTS:
        continue

    p = str(path).replace("\\", "/").lower()
    if "_quarantine" in p:
        continue

    if path.suffix.lower() in {".json", ".jsonl"}:
        if path.suffix.lower() == ".json":
            try:
                payload = json.loads(safe_read(path))
            except Exception:
                continue
            records = records_from_json(payload)
        else:
            records = []
            for line in safe_read(path).splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass

        usable = 0
        max_len = 0
        key_counts = Counter()

        for rec in records:
            if not isinstance(rec, dict):
                continue
            for key in BODY_KEYS:
                val = rec.get(key)
                if isinstance(val, str) and len(val.strip()) > 300:
                    usable += 1
                    max_len = max(max_len, len(val.strip()))
                    key_counts[key] += 1
                    break

        if usable:
            candidates.append((str(path), len(records), usable, max_len, dict(key_counts)))

    else:
        text = safe_read(path)
        if len(text.strip()) > 1000 and ("whattoexpect" in text.lower() or "<article" in text.lower() or len(text.strip()) > 5000):
            candidates.append((str(path), 1, 1, len(text.strip()), {"file_text": 1}))

candidates.sort(key=lambda x: (x[2], x[3]), reverse=True)

for path, seen, usable, max_len, keys in candidates[:80]:
    print("-" * 80)
    print("path =", path)
    print("records_seen =", seen)
    print("usable_bodies =", usable)
    print("max_body_length =", max_len)
    print("keys =", keys)

print("\n[3] FILE/FOLDER NAMES THAT LOOK LIKE CRAWLER OUTPUTS")
name_hits = []
for path in ROOT.rglob("*"):
    p = str(path).replace("\\", "/").lower()
    if any(term in p for term in ["crawl", "extract", "clean", "article", "page", "html", "snapshot", "whattoexpect", "live_domain"]):
        name_hits.append(str(path))

for item in name_hits[:150]:
    print(item)
