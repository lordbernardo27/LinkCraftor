import json, time
from pathlib import Path
from backend.server.stores.upload_normalizer import normalize_upload
from backend.server.stores.smart_phrase_extractor import extract_smart_phrases
from backend.server.stores.candidate_window_guard import candidate_window_guard

ws = "ws_betterhealthcheck_com"
data = json.loads(Path(f"backend/server/data/upload_struct_{ws}.json").read_text(encoding="utf-8"))
doc_id, doc = list(data.get("docs", {}).items())[0]

r = normalize_upload(doc.get("stored_path") or doc.get("path") or "")
phrases = extract_smart_phrases(
    text=r.get("text", "") or "",
    html=r.get("html", "") or "",
    title=doc.get("title") or doc.get("name") or "",
    doc_id=doc_id,
    workspace_id=ws,
    vertical="general",
    max_candidates=50,
)

kept = []
rejected = []

for item in phrases:
    phrase = item.get("text") or item.get("phrase") or ""
    result = candidate_window_guard(
        phrase,
        source_type=item.get("source_type") or "",
        workspace_id=ws,
        document_id=doc_id,
        vertical="general",
    )
    if result.get("keep"):
        kept.append(result)
    else:
        rejected.append(result)

print("smart_count:", len(phrases))
print("guard_kept:", len(kept))
print("guard_rejected:", len(rejected))
print("kept_sample:", [x.get("phrase") for x in kept[:10]])
print("rejected_sample:", [(x.get("phrase"), x.get("reason")) for x in rejected[:10]])
