import json
from pathlib import Path

ws = "ws_betterhealthcheck_com"

data = Path(r".\backend\server\data")
active_dir = data / "phrase_pools" / "active"

pool_fp = active_dir / f"active_phrase_pool_{ws}.json"
set_fp = active_dir / f"active_phrase_set_{ws}.json"

if not pool_fp.exists():
    print("❌ Active phrase pool file missing")
    exit()

obj = json.loads(pool_fp.read_text(encoding="utf-8"))
aset = json.loads(set_fp.read_text(encoding="utf-8")) if set_fp.exists() else {}

phrases = obj.get("phrases") or {}

active_document_ids = set(
    str(x).strip()
    for x in (aset.get("active_document_ids") or [])
    if str(x).strip()
)

upload_total = 0
upload_selected_ok = 0
upload_leak_count = 0

duplicate_keys = set()
seen_keys = set()

for k, v in phrases.items():
    if k in seen_keys:
        duplicate_keys.add(k)
    seen_keys.add(k)

    if not isinstance(v, dict):
        continue

    docs = v.get("docs") or {}

    if docs:
        upload_total += 1

        doc_keys = set(str(x).strip() for x in docs.keys() if str(x).strip())

        if doc_keys:
            if "ALL" in active_document_ids or doc_keys.issubset(active_document_ids):
                upload_selected_ok += 1
            else:
                upload_leak_count += 1

print("\n===== ACTIVE POOL CHECK (UPLOAD ONLY) =====")

print("workspace_id:", obj.get("workspace_id"))
print("phrase_count:", len(phrases))

print("\n--- Membership ---")
print("active_document_ids:", active_document_ids)

print("\n--- Upload Stats ---")
print("upload_total:", upload_total)
print("upload_selected_ok:", upload_selected_ok)
print("upload_leak_count:", upload_leak_count)

print("\n--- Checks ---")

print("5.5.1 only_selected_upload_docs_contribute:", upload_leak_count == 0)
print("5.5.5 no_leakage:", upload_leak_count == 0)
print("5.6.1 duplicate_phrases_merged:", len(duplicate_keys) == 0)
print("5.7.1 workspace_correct:", obj.get("workspace_id") == ws)
print("5.7.2 workspace_normalized:",
      isinstance(obj.get("workspace_id"), str) and obj.get("workspace_id", "").startswith("ws_"))
print("5.8.1 file_exists:", pool_fp.exists())

stale = False
if upload_total > 0 and active_document_ids and "ALL" not in active_document_ids:
    if upload_selected_ok < upload_total:
        stale = True

print("5.8.2 reflects_active_set:", not stale)
print("5.8.3 no_stale_phrases:", not stale)

print("\n===== END =====\n")