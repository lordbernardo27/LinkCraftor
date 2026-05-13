import json
from pathlib import Path
from collections import Counter

from backend.server.stores.smart_phrase_extractor import extract_smart_phrases

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

    counts = Counter(c.get("source_type", "unknown") for c in candidates)

    print("\n==============================")
    print(doc.get("original_name"))
    print("doc_id:", doc_id)
    print("word_count:", (doc.get("fingerprint") or {}).get("word_count"))
    print("raw_smart_candidates:", len(candidates))
    print("source_type_counts:", dict(counts))
    print("sample:", [c.get("phrase") for c in candidates[:30]])
