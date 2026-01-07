# backend/app/engine/entity_detection.py
from __future__ import annotations
from typing import Dict, List, Tuple
import re

WORD_RE = re.compile(r"[\w’'-]+")

def normalize_entity(text: str) -> str:
    s = (text or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("—", "-").replace("–", "-")
    return s

def extract_candidates(text: str) -> List[str]:
    # very naive: sequences of 2–5 tokens as entity candidates
    tokens = WORD_RE.findall(text or "")
    tokens = [t for t in tokens if t and not t.isdigit()]
    out: List[str] = []
    for n in range(2, 6):
        for i in range(0, max(0, len(tokens) - n + 1)):
            span = " ".join(tokens[i:i+n])
            if len(span) >= 4:
                out.append(span)
    return out

def build_entity_map(html: str = "", text: str = "") -> Dict:
    raw = (html or "") + "\n" + (text or "")
    # strip very basic tags
    clean = re.sub(r"<[^>]+>", " ", raw)
    clean = re.sub(r"\s+", " ", clean).strip()

    cands = extract_candidates(clean)
    counts: Dict[str, int] = {}
    first_surface: Dict[str, str] = {}

    for c in cands:
        norm = normalize_entity(c)
        counts[norm] = counts.get(norm, 0) + 1
        if norm not in first_surface:
            first_surface[norm] = c

    entities: List[Dict] = []
    for norm, cnt in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        entities.append({
            "surface": first_surface.get(norm, norm),
            "norm": norm,
            "count": int(cnt),
            "type": "phrase" if " " in norm else "token",
        })

    return {
        "entities": entities,
        "meta": {
            "total": len(entities),
            "source_len": len(clean),
        }
    }
