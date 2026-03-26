import json
from pathlib import Path

ws = "ws_prettiereveryday_com"
data_dir = Path("backend/server/data")

pages_path = data_dir / f"site_pages_{ws}.json"
phrases_path = data_dir / f"site_phrase_index_{ws}.json"

pages = json.loads(pages_path.read_text(encoding="utf-8", errors="ignore")).get("pages", {})
phrases = json.loads(phrases_path.read_text(encoding="utf-8", errors="ignore")).get("phrases", {})

urls = sorted(pages.keys())
print("PAGES_SAMPLE", len(urls))
for u in urls[:25]:
    print(u)

items = list(phrases.values())

def sort_key(r):
    bucket = r.get("bucket")
    bucket_rank = 0 if bucket == "internal_strong" else 1
    conf = float(r.get("confidence", 0) or 0)
    sc = int(r.get("source_count", 0) or 0)
    plen = len(str(r.get("phrase", "") or ""))
    return (bucket_rank, -conf, -sc, -plen)

items.sort(key=sort_key)

print("\nPHRASES_SAMPLE", len(items))
for i in items[:25]:
    print(f"{i.get('bucket')} :: {i.get('type')} :: {i.get('confidence')} :: {i.get('phrase')}")
