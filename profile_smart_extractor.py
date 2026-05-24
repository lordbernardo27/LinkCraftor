import cProfile, pstats, io, json
from pathlib import Path

from backend.server.stores.upload_normalizer import normalize_upload
from backend.server.stores.smart_phrase_extractor import extract_smart_phrases

ws = "ws_betterhealthcheck_com"
data = json.loads(Path(f"backend/server/data/upload_struct_{ws}.json").read_text(encoding="utf-8"))
doc_id, doc = list(data.get("docs", {}).items())[0]

r = normalize_upload(doc.get("stored_path") or doc.get("path") or "")

pr = cProfile.Profile()
pr.enable()

phrases = extract_smart_phrases(
    text=r.get("text", "") or "",
    html=r.get("html", "") or "",
    title=doc.get("original_name") or doc.get("name") or Path(doc.get("stored_path") or "").name,
    doc_id=doc_id,
    workspace_id=ws,
    vertical="general",
    max_candidates=50,
)

pr.disable()

print("phrase_count:", len(phrases))

s = io.StringIO()
stats = pstats.Stats(pr, stream=s).sort_stats("cumtime")
stats.print_stats(40)

print(s.getvalue())
