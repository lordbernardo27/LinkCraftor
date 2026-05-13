import json
from pathlib import Path

from backend.server.stores.smart_phrase_extractor import extract_smart_phrases
from backend.server.stores.candidate_window_guard import candidate_window_guard
from backend.server.stores.phrase_strength_scorer import score_phrase_strength

ws = "ws_betterhealthcheck_com"
struct = json.loads(Path(f"backend/server/data/upload_struct_{ws}.json").read_text(encoding="utf-8"))

target_docs = {
    "cc6e15d3942a4c1c8507fc30c8a09cc6": "BMI",
    "f03ad1c105cd427c9dd55f8a80c119ee": "Amlodipine",
}

for doc_id, label in target_docs.items():
    doc = struct["docs"][doc_id]
    text = " ".join(p.get("text", "") for p in doc.get("paragraphs", []) if p.get("text"))

    candidates = extract_smart_phrases(
        text=text,
        html="",
        title=doc.get("original_name", ""),
        doc_id=doc_id,
        max_candidates=1000,
    )

    print("\n==============================")
    print(label, doc.get("original_name"))

    shown = 0
    for c in candidates:
        phrase = c.get("phrase", "")
        source_type = c.get("source_type", "")
        g = candidate_window_guard(phrase, source_type=source_type)
        if not g.get("keep"):
            continue

        scored = score_phrase_strength(
            phrase=g.get("phrase") or phrase,
            source_type=source_type,
        )

        if not scored.get("keep"):
            reason = scored.get("reason", "")
            if (
                "short_window_missing_structure" in reason
                or "list_style_stack" in reason
                or "low_domain_cohesion" in reason
                or "mid_stopword_fragment" in reason
            ):
                print("-", g.get("phrase") or phrase, "|", source_type, "|", reason)
                shown += 1
                if shown >= 30:
                    break
