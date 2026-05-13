import json
from pathlib import Path
from collections import Counter

from backend.server.stores.smart_phrase_extractor import extract_smart_phrases
from backend.server.stores.candidate_window_guard import candidate_window_guard
from backend.server.stores.phrase_strength_scorer import score_phrase_strength

ws = "ws_betterhealthcheck_com"
struct = json.loads(Path(f"backend/server/data/upload_struct_{ws}.json").read_text(encoding="utf-8"))

for doc_id, doc in struct.get("docs", {}).items():
    text = " ".join(
        p.get("text", "")
        for p in doc.get("paragraphs", [])
        if p.get("text")
    )

    candidates = extract_smart_phrases(
        text=text,
        html="",
        title=doc.get("original_name", ""),
        doc_id=doc_id,
        max_candidates=1000,
    )

    guard_kept = []
    for c in candidates:
        g = candidate_window_guard(c.get("phrase", ""), source_type=c.get("source_type", ""))
        if g.get("keep"):
            guard_kept.append((g.get("phrase") or c.get("phrase", ""), c.get("source_type", "")))

    scorer_reasons = Counter()
    scorer_kept = 0

    for phrase, source_type in guard_kept:
        s = score_phrase_strength(phrase=phrase, source_type=source_type)

        if s.get("keep"):
            scorer_kept += 1
        else:
            scorer_reasons[s.get("reason", "unknown")] += 1

    print("\n==============================")
    print(doc.get("original_name"))
    print("raw_candidates:", len(candidates))
    print("guard_kept:", len(guard_kept))
    print("scorer_kept:", scorer_kept)
    print("scorer_rejected:", len(guard_kept) - scorer_kept)
    print("top_scorer_rejection_reasons:", scorer_reasons.most_common(10))
