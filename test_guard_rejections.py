import json
from pathlib import Path
from collections import Counter, defaultdict

from backend.server.stores.smart_phrase_extractor import extract_smart_phrases
from backend.server.stores.candidate_window_guard import candidate_window_guard

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

    reasons = Counter()
    kept_samples = []
    rejected_samples = defaultdict(list)

    for c in candidates:
        phrase = c.get("phrase", "")
        source_type = c.get("source_type", "")
        g = candidate_window_guard(phrase, source_type=source_type)

        if g.get("keep"):
            if len(kept_samples) < 25:
                kept_samples.append(phrase)
        else:
            reason = g.get("reason", "unknown")
            reasons[reason] += 1
            if len(rejected_samples[reason]) < 15:
                rejected_samples[reason].append(phrase)

    kept = sum(1 for c in candidates if candidate_window_guard(c.get("phrase", ""), source_type=c.get("source_type", "")).get("keep"))

    print("\n==============================")
    print(doc.get("original_name"))
    print("raw_candidates:", len(candidates))
    print("guard_kept:", kept)
    print("guard_rejected:", len(candidates) - kept)
    print("top_rejection_reasons:", reasons.most_common(10))

    print("\nKEPT SAMPLE:")
    for x in kept_samples:
        print("  +", x)

    print("\nREJECTED SAMPLE BY REASON:")
    for reason, samples in rejected_samples.items():
        print(f"\n  {reason}:")
        for x in samples:
            print("   -", x)