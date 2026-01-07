from .textops import tokens, content_ratio, norm, split_into_sections
from ..config import settings

def run_helix(text: str, published_topics:list, draft_topics:list, phase:str, buckets:dict):
    # 1) build sections
    sections = split_into_sections(text or "")
    # 2) discover topics:
    #    - headings/same-doc can be added later once you post HTML too
    topics = []
    topics += published_topics
    topics += draft_topics

    # 3) candidate anchors (n-grams, same as JS)
    #    For brevity, generate simple candidates: 2..6 tokens windows
    cands = []
    STOP = set(["the","a","an","of","to","and","in","on","for","with","by","from","or","vs","&"])
    for s in sections:
        T = tokens(s["text"])
        for n in range(2, 7):
            for i in range(0, max(0, len(T)-n+1)):
                gram = T[i:i+n]
                if gram[0] in STOP or gram[-1] in STOP: continue
                if content_ratio(gram, STOP) < 0.45: continue
                cands.append({"anchor":" ".join(gram), "sectionIdx": s["idx"]})

    # 4) score vs topics (very simplified mirror)
    rec, opt, hid = [], [], []
    for c in cands:
        # toy score: anchor quality only (you’ll port your exact math next)
        a_tok = c["anchor"].split()
        aQ = content_ratio(a_tok, STOP)
        score = 0.6*aQ
        bucket = "strong" if score >= settings.FLOORS_STRONG else "optional" if score >= settings.FLOORS_OPTIONAL else "drop"
        if bucket == "drop":
            hid.append({"anchor": {"text": c["anchor"]}, "rawScore": score})
            continue
        sug = {
            "anchor": {"text": c["anchor"], "sectionIdx": c["sectionIdx"]},
            "target": {"topicId":"", "title": c["anchor"], "kind":"draft", "url":"", "planned_slug":""},
            "bucket": bucket,
            "finalScore": round(score, 4),
            "posCues": [],
            "posBoost": 0.0,
            "suggestions": []
        }
        (rec if bucket=="strong" else opt).append(sug)

    return {
        "recommended": rec,
        "optional": opt,
        "external": [],  # filled by external_v2
        "hidden": hid,
        "meta": {"phase": phase, "floors": {
            "STRONG": settings.FLOORS_STRONG, "OPTIONAL": settings.FLOORS_OPTIONAL
        }}
    }
