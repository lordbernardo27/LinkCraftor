import json, time, traceback
from pathlib import Path
from backend.server.stores.upload_intel_store_v2 import build_upload_intelligence
from backend.server.stores.upload_normalizer import normalize_upload

ws = "ws_betterhealthcheck_com"
struct_path = Path(f"backend/server/data/upload_struct_{ws}.json")
data = json.loads(struct_path.read_text(encoding="utf-8"))
docs = data.get("docs", {})

print("docs_to_reindex:", len(docs))

for i, (doc_id, doc) in enumerate(docs.items(), 1):
    stored_path = doc.get("stored_path") or doc.get("path") or ""
    original_name = doc.get("original_name") or doc.get("name") or Path(stored_path).name

    n = normalize_upload(stored_path)
    print("\nREINDEX", i, doc_id, original_name)
    print("normalized:", n.get("ok"), "text_len:", len(n.get("text", "") or ""), "paragraphs:", len(n.get("paragraphs") or []))

    t0 = time.time()
    try:
        r = build_upload_intelligence(
            workspace_id=ws,
            doc_id=doc_id,
            stored_path=stored_path,
            original_name=original_name,
            html=n.get("html", "") or "",
            text=n.get("text", "") or "",
        )
        print("ok:", r.get("ok"), "seconds:", round(time.time() - t0, 2))
        print("counts:", r.get("counts"))
    except Exception:
        traceback.print_exc()

index_path = Path(f"backend/server/data/upload_phrase_index_{ws}.json")
idx = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {}
print("\nFINAL_INDEX_EXISTS:", index_path.exists())
print("FINAL_INDEX_PHRASES:", len(idx.get("phrases", {}) or {}))
