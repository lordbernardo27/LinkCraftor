import json
from pathlib import Path
from backend.server.stores.upload_intel_store import (
    _ws_safe, _data_dir, _tokenize, _ngram_rule_generate, _maximal_phrase_filter, _norm_text, _now_iso
)

ws = "betterhealthcheck_com"
base = _data_dir()

struct_fp = base / f"upload_struct_ws_{_ws_safe(ws)}.json"
out_fp    = base / f"upload_phrase_index_ws_{_ws_safe(ws)}.json"

struct = json.loads(struct_fp.read_text(encoding="utf-8"))
docs = (struct.get("docs") or {})

phrases = {}

for doc_id, doc in docs.items():
    paras = (doc.get("paragraphs") or [])
    for p in paras:
        text = (p.get("text") or "")
        tokens = _tokenize(text)
        grams = _ngram_rule_generate(tokens)
        grams = _maximal_phrase_filter([_norm_text(g) for g in grams])

        for g in grams:
            if not g:
                continue
            rec = phrases.get(g)
            if not rec:
                rec = {
                    "phrase": g,
                    "count_total": 0,
                    "docs": {},
                    "first_seen": _now_iso(),
                    "last_seen": _now_iso(),
                    "examples": [],
                }
                phrases[g] = rec
            rec["count_total"] += 1
            rec["last_seen"] = _now_iso()
            rec["docs"][doc_id] = int(rec["docs"].get(doc_id, 0)) + 1

obj = {
    "workspace_id": _ws_safe(ws),
    "updated_at": _now_iso(),
    "phrases": phrases
}

out_fp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
print("REBUIlT:", out_fp)
print("phrases_count:", len(phrases))
