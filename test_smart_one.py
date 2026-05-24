import json, time, traceback
from pathlib import Path
from backend.server.stores.upload_normalizer import normalize_upload
from backend.server.stores.smart_phrase_extractor import extract_smart_phrases

ws = "ws_betterhealthcheck_com"
data = json.loads(Path(f"backend/server/data/upload_struct_{ws}.json").read_text(encoding="utf-8"))
docs = list(data.get("docs", {}).items())

doc_id, doc = docs[0]
print("testing_doc:", doc_id)

r = normalize_upload(doc.get("stored_path") or doc.get("path") or "")
print("normalized:", r.get("ok"), "text_len:", len(r.get("text", "") or ""), "paragraphs:", len(r.get("paragraphs") or []))

t0 = time.time()
try:
    phrases = extract_smart_phrases(
        text=r.get("text", "") or "",
        html=r.get("html", "") or "",
        title=doc.get("title") or doc.get("name") or "",
        doc_id=doc_id,
        workspace_id=ws,
        vertical="general",
        max_candidates=50,
    )
    print("smart_count:", len(phrases))
    print("seconds:", round(time.time() - t0, 2))
    print("sample:", [(p.get("text") or p.get("phrase")) for p in phrases[:10]])
except Exception:
    traceback.print_exc()
