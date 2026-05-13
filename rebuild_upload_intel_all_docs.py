import json
from pathlib import Path

from backend.server.stores.upload_intel_store_v2 import build_upload_intelligence
from backend.server.stores.upload_phrase_pool_builder import build_upload_phrase_pool

ws = "ws_betterhealthcheck_com"
struct_path = Path(f"backend/server/data/upload_struct_{ws}.json")
data = json.loads(struct_path.read_text(encoding="utf-8"))

for doc_id, doc in data.get("docs", {}).items():
    text = " ".join(
        p.get("text", "")
        for p in doc.get("paragraphs", [])
        if p.get("text")
    )

    result = build_upload_intelligence(
        workspace_id=ws,
        doc_id=doc_id,
        stored_path=str(doc.get("stored_path") or ""),
        original_name=str(doc.get("original_name") or ""),
        html="",
        text=text,
    )

    counts = result.get("counts", {})
    print("\nREBUILT:", doc.get("original_name"))
    print("doc_id:", doc_id)
    print("quality_extractor_candidate_count:", counts.get("quality_extractor_candidate_count"))
    print("quality_guard_kept_count:", counts.get("quality_guard_kept_count"))
    print("quality_scorer_kept_count:", counts.get("quality_scorer_kept_count"))
    print("quality_indexed_count:", counts.get("quality_indexed_count"))

pool = build_upload_phrase_pool(ws)
print("\nPOOL_REBUILT:", pool.get("phrase_count"))
