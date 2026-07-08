import json
from pathlib import Path

workspace = "ws_whattoexpect_com"
p = Path("backend/server/data/universal_article_body_store") / workspace / f"universal_article_body_index_{workspace}.json"

data = json.loads(p.read_text(encoding="utf-8"))
dups = data.get("duplicate_hashes") or []

print("DUPLICATE HASH GROUPS:", len(dups))
print("=" * 80)

for i, d in enumerate(dups, 1):
    print(f"\nGROUP {i}")
    print("content_hash:", d.get("content_hash"))
    print("duplicate_count:", d.get("duplicate_count"))
    print("document_ids:")
    for doc_id in d.get("document_ids", []):
        print(" -", doc_id)
