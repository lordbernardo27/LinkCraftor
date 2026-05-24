import json, time, os
from pathlib import Path
from datetime import datetime

from backend.server.stores.upload_normalizer import normalize_upload
from backend.server.stores.smart_phrase_extractor import extract_smart_phrases
from backend.server.stores.candidate_window_guard import candidate_window_guard
from backend.server.stores.phrase_strength_scorer import score_phrase_strength

ws = "ws_betterhealthcheck_com"
struct_path = Path(f"backend/server/data/upload_struct_{ws}.json")
index_path = Path(f"backend/server/data/upload_phrase_index_{ws}.json")

data = json.loads(struct_path.read_text(encoding="utf-8"))
docs = data.get("docs", {})

out = {
    "workspace_id": ws,
    "updated_at": datetime.utcnow().isoformat() + "Z",
    "mode": "fast_workspace_upload_reindexer",
    "phrases": {},
    "docs": {},
}

print("fast_reindex_docs:", len(docs))

for i, (doc_id, doc) in enumerate(docs.items(), 1):
    t0 = time.time()
    stored_path = doc.get("stored_path") or doc.get("path") or ""
    original_name = doc.get("original_name") or doc.get("name") or Path(stored_path).name

    n = normalize_upload(stored_path)
    text = n.get("text", "") or ""
    html = n.get("html", "") or ""

    candidates = extract_smart_phrases(
        text=text,
        html=html,
        title=original_name,
        doc_id=doc_id,
        workspace_id=ws,
        vertical="general",
        max_candidates=80,
    )

    kept = 0
    seen_doc = set()

    for c in candidates:
        phrase = str(c.get("phrase") or c.get("text") or "").strip().lower()
        if not phrase or phrase in seen_doc:
            continue

        source_type = str(c.get("source_type") or "quality_pipeline")
        guard = candidate_window_guard(
            phrase,
            source_type=source_type,
            workspace_id=ws,
            document_id=doc_id,
            vertical="general",
        )
        if not guard.get("keep"):
            continue

        guarded = str(guard.get("phrase") or phrase).strip().lower()
        score = score_phrase_strength(
            guarded,
            source_type=source_type,
            workspace_id=ws,
            document_id=doc_id,
            vertical="general",
        )
        if not score.get("keep"):
            continue

        final = str(score.get("phrase") or guarded).strip().lower()
        if not final or final in seen_doc:
            continue

        seen_doc.add(final)
        kept += 1

        rec = out["phrases"].setdefault(final, {
            "phrase": final,
            "canonical": final,
            "source_type": source_type,
            "tier": "B",
            "count_total": 0,
            "quality_score": float(score.get("score") or 0.0),
            "docs": {},
            "sections": [],
            "examples": [],
            "strength": score,
            "first_seen": out["updated_at"],
            "last_seen": out["updated_at"],
        })

        rec["count_total"] = int(rec.get("count_total") or 0) + 1
        rec["docs"][doc_id] = int(rec["docs"].get(doc_id) or 0) + 1
        rec["quality_score"] = max(float(rec.get("quality_score") or 0.0), float(score.get("score") or 0.0))
        rec["last_seen"] = out["updated_at"]

    out["docs"][doc_id] = {
        "original_name": original_name,
        "stored_path": stored_path,
        "text_len": len(text),
        "candidate_count": len(candidates),
        "kept_count": kept,
        "seconds": round(time.time() - t0, 2),
    }

    print(i, original_name, "candidates=", len(candidates), "kept=", kept, "seconds=", round(time.time() - t0, 2))

tmp = index_path.with_suffix(index_path.suffix + ".tmp")
tmp.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
os.replace(tmp, index_path)

print("FINAL_INDEX:", index_path)
print("FINAL_PHRASES:", len(out["phrases"]))
