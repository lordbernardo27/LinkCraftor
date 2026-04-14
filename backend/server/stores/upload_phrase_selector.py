from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List, Optional, Set, Tuple


WORD_RE = re.compile(r"[a-z0-9]{2,}", re.I)
TAG_RE = re.compile(r"<[^>]+>")
H_RE = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
LI_RE = re.compile(r"<li[^>]*>(.*?)</li>", re.IGNORECASE | re.DOTALL)
P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.IGNORECASE | re.DOTALL)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")

STOPWORDS: Set[str] = {
    "the", "and", "for", "with", "that", "this", "from", "into", "your", "you", "are", "was", "were",
    "will", "can", "could", "should", "would", "have", "has", "had", "about", "over", "under", "than",
    "then", "when", "what", "where", "which", "who", "whom", "why", "how", "a", "an", "to", "of", "in",
    "on", "at", "by", "or", "as", "is", "it", "be", "not", "no", "if", "but", "so", "because", "after",
    "before", "during", "while", "through", "up", "down", "out", "off", "too", "very", "also"
}

WEAK_STARTS: Set[str] = {
    "the", "this", "that", "these", "those", "your", "is", "are", "was", "were", "while", "so", "then"
}

NARRATIVE_VERBS: Set[str] = {
    "is", "are", "was", "were", "can", "will", "would", "may", "might", "should"
}

WEAK_ENDINGS: Set[str] = {
    "about", "around", "roughly", "always", "usually", "often", "matter", "like", "such", "each", "one"
}

UI_JUNK_TERMS: Set[str] = {
    "faq", "skip", "menu", "share", "home", "read more", "previous", "next", "written by", "contact us",
    "about us", "privacy policy", "terms", "cookie", "login", "register", "subscribe", "follow us",
    "facebook", "instagram", "twitter", "youtube", "whatsapp", "telegram"
}

INTENT_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"^how to [a-z0-9\s\-]+$"),
    re.compile(r"^how many [a-z0-9\s\-]+$"),
    re.compile(r"^when do [a-z0-9\s\-]+$"),
    re.compile(r"^what is [a-z0-9\s\-]+$"),
    re.compile(r"^what are [a-z0-9\s\-]+$"),
    re.compile(r"^signs of [a-z0-9\s\-]+$"),
    re.compile(r"^symptoms of [a-z0-9\s\-]+$"),
    re.compile(r"^causes of [a-z0-9\s\-]+$"),
    re.compile(r"^treatment for [a-z0-9\s\-]+$"),
    re.compile(r"^best time [a-z0-9\s\-]+$"),
    re.compile(r"^best way [a-z0-9\s\-]+$"),
)

ENTITY_SEEDS: List[str] = [
    "ovulation",
    "fertile window",
    "due date",
    "conception date",
    "gestational age",
    "lmp",
    "basal body temperature",
    "bbt",
    "cervical mucus",
    "ultrasound",
    "embryo transfer",
    "implantation",
    "period",
    "menstrual cycle",
    "pregnancy test",
    "ovulation estimate",
    "cycle length",
]


def _strip_tags(s: str) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", s or "")).strip()


def _canonical_phrase(s: str) -> str:
    s = (s or "").strip().lower()
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')

    s = re.sub(r"^\s*(?:\d+[\.\)]\s+|[•\-–]\s+)", "", s)
    s = re.sub(r"^[\"'“”‘’\(\[\{]+|[\"'“”‘’\)\]\}:;,\.\!\?]+$", "", s).strip()
    s = re.sub(r"\s+", " ", s).strip()

    # remove leading connectors / filler words repeatedly
    lead_words = (
        "and", "or", "but", "so", "as", "to", "from", "with", "by",
        "can", "will", "would", "should", "could", "may", "might",
        "the", "a", "an", "vs"
    )

    changed = True
    while changed and s:
        changed = False
        for w in lead_words:
            prefix = w + " "
            if s.startswith(prefix):
                s = s[len(prefix):].strip()
                changed = True

    # remove trailing loose connectors
    tail_words = ("and", "or", "but", "as", "to", "from", "with", "by", "vs")
    changed = True
    while changed and s:
        changed = False
        for w in tail_words:
            suffix = " " + w
            if s.endswith(suffix):
                s = s[:-len(suffix)].strip()
                changed = True

    s = re.sub(r"\s+", " ", s).strip()
    return s


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]


def _content_tokens(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in STOPWORDS]


def _split_sentences(text: str) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    return [p.strip() for p in SENTENCE_SPLIT_RE.split(text) if p and p.strip()]


def _looks_like_ui_junk(s: str) -> bool:
    s = _canonical_phrase(s)
    return (not s) or any(x in s for x in UI_JUNK_TERMS)


def _extract_canonical_core_phrase(s: str) -> str:
    s = _canonical_phrase(s)
    if not s:
        return ""

    markers = [
        "how to ", "how many ", "when do ", "what is ", "what are ",
        "signs of ", "symptoms of ", "causes of ", "treatment for ",
        "best time ", "best way ",
    ]
    starts = [s.find(m) for m in markers if s.find(m) != -1]
    if starts:
        s = s[min(starts):].strip()

    lead_patterns = [
        r"^people often ask\s+",
        r"^many people ask\s+",
        r"^many women ask\s+",
        r"^women often ask\s+",
        r"^doctors are often asked\s+",
        r"^you may wonder\s+",
        r"^you might wonder\s+",
        r"^you may ask\s+",
        r"^you might ask\s+",
        r"^you may be asking\s+",
        r"^often ask\s+",
    ]
    for pat in lead_patterns:
        s = re.sub(pat, "", s).strip()

    return _canonical_phrase(s)


def _looks_like_intent_phrase(phrase: str) -> bool:
    p = _canonical_phrase(phrase)
    return any(rx.match(p) for rx in INTENT_PATTERNS)


def _looks_like_entity_phrase(phrase: str) -> bool:
    p = _canonical_phrase(phrase)
    return p in ENTITY_SEEDS or any(seed in p for seed in ENTITY_SEEDS)


def _is_link_worthy_shape(phrase: str) -> bool:
    p = _canonical_phrase(phrase)
    if not p or _looks_like_ui_junk(p):
        return False

    tokens = _tokenize(p)
    if len(tokens) < 2 or len(tokens) > 6:
        return False

    content = _content_tokens(tokens)
    if len(content) < 2:
        return False

    if tokens[0] in WEAK_STARTS and not _looks_like_intent_phrase(p):
        return False

    if tokens[-1] in WEAK_ENDINGS:
        return False

    if len(tokens) >= 2 and tokens[1] in NARRATIVE_VERBS and not _looks_like_intent_phrase(p):
        return False

    return True


def _score_candidate(phrase: str, source_type: str, freq: int = 1) -> int:
    p = _canonical_phrase(phrase)
    if not p:
        return 0

    tokens = _tokenize(p)
    content = _content_tokens(tokens)
    score = 0

    if _looks_like_entity_phrase(p):
        score += 35

    if _looks_like_intent_phrase(p):
        score += 30

    if source_type in {"title", "heading_h1"}:
        score += 20
    elif source_type in {"heading_h2", "heading_h3", "list_item"}:
        score += 15

    if _is_link_worthy_shape(p):
        score += 20

    if len(content) >= 3:
        score += 10

    if freq >= 2:
        score += min(freq * 3, 10)

    if tokens and tokens[0] in WEAK_STARTS and not _looks_like_intent_phrase(p):
        score -= 25

    if len(tokens) >= 2 and tokens[1] in NARRATIVE_VERBS and not _looks_like_intent_phrase(p):
        score -= 20

    if tokens and tokens[-1] in WEAK_ENDINGS:
        score -= 15

    return score


def _extract_headings_and_lists(html: str) -> Tuple[Optional[str], List[Tuple[str, str]]]:
    found_h = [(int(lvl), _strip_tags(inner)) for lvl, inner in H_RE.findall(html or "")]
    h1 = next((txt for lvl, txt in found_h if lvl == 1 and txt), None)

    out: List[Tuple[str, str]] = []
    for lvl, txt in found_h:
        if not txt:
            continue
        if lvl == 1:
            out.append((txt, "heading_h1"))
        elif lvl in (2, 3):
            out.append((txt, f"heading_h{lvl}"))

    for li in [_strip_tags(x) for x in LI_RE.findall(html or "")]:
        if li:
            out.append((li, "list_item"))

    return h1, out


def _extract_paragraphs(html: str, text: str) -> List[str]:
    paras = [_strip_tags(x) for x in P_RE.findall(html or "")]
    paras = [p for p in paras if p]
    if paras:
        return paras

    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    return [x.strip() for x in re.split(r"\n\s*\n+", text) if x.strip()]


def _select_structured_candidates(original_name: str, html: str) -> List[Dict[str, Any]]:
    h1, items = _extract_headings_and_lists(html)
    out: List[Dict[str, Any]] = []

    if original_name:
        title_like = _canonical_phrase(re.sub(r"[_\-]+", " ", re.sub(r"\.[a-z0-9]+$", "", original_name, flags=re.I)))
        if title_like:
            out.append({
                "phrase": _extract_canonical_core_phrase(title_like) or title_like,
                "source_type": "title",
                "section_id": "title_0",
                "snippet": title_like,
            })

    for idx, (txt, source_type) in enumerate(items):
        p = _extract_canonical_core_phrase(txt) or _canonical_phrase(txt)
        if p:
            out.append({
                "phrase": p,
                "source_type": source_type,
                "section_id": f"{source_type}_{idx}",
                "snippet": txt,
            })

    if h1:
        p = _extract_canonical_core_phrase(h1) or _canonical_phrase(h1)
        if p:
            out.append({
                "phrase": p,
                "source_type": "heading_h1",
                "section_id": "h1",
                "snippet": h1,
            })

    return out


def _select_entity_candidates(paragraphs: List[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for i, para in enumerate(paragraphs):
        ptxt = _canonical_phrase(para)
        for seed in ENTITY_SEEDS:
            if seed in ptxt:
                out.append({
                    "phrase": seed,
                    "source_type": "entity",
                    "section_id": f"p{i}",
                    "snippet": para,
                })
    return out


def _select_intent_candidates(paragraphs: List[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for i, para in enumerate(paragraphs):
        for sent in _split_sentences(para):
            s = _extract_canonical_core_phrase(sent)
            if s and _looks_like_intent_phrase(s):
                out.append({
                    "phrase": s,
                    "source_type": "intent",
                    "section_id": f"p{i}",
                    "snippet": sent,
                })
    return out

def _select_noun_phrase_candidates(paragraphs: List[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    anchor_words = {
        "date", "age", "window", "ovulation", "pregnancy", "period",
        "cycle", "temperature", "mucus", "transfer", "implantation",
        "calculator", "test", "symptoms", "fertility"
    }

    for i, para in enumerate(paragraphs):
        for sent in _split_sentences(para):
            tokens = _tokenize(sent)
            if len(tokens) < 2:
                continue

            for n in (2, 3, 4):
                if n > len(tokens):
                    continue

                for j in range(0, len(tokens) - n + 1):
                    chunk = tokens[j:j+n]
                    cand = " ".join(chunk).strip()
                    cand = _extract_canonical_core_phrase(cand) or _canonical_phrase(cand)

                    if not cand:
                        continue

                    # must contain anchor noun at start or end
                    if chunk[0] not in anchor_words and chunk[-1] not in anchor_words:
                        continue

                    if not _is_link_worthy_shape(cand):
                        continue

                    out.append({
                        "phrase": cand,
                        "source_type": "noun_phrase",
                        "section_id": f"p{i}",
                        "snippet": sent,
                    })

    return out


def _dedupe_and_rank(candidates: List[Dict[str, Any]], keep_threshold: int = 60) -> List[Dict[str, Any]]:
    counter = Counter(_canonical_phrase(c["phrase"]) for c in candidates if c.get("phrase"))
    best: Dict[str, Dict[str, Any]] = {}

    for c in candidates:
        phrase = _canonical_phrase(c.get("phrase", ""))
        if not phrase:
            continue

        score = _score_candidate(phrase, str(c.get("source_type") or ""), counter.get(phrase, 1))
        if score < keep_threshold:
            continue

        current = best.get(phrase)
        item = {
            "phrase": phrase,
            "canonical": phrase,
            "source_type": c.get("source_type", "unknown"),
            "score": score,
            "section_id": c.get("section_id", ""),
            "snippet": c.get("snippet", ""),
        }

        if current is None or item["score"] > current["score"]:
            best[phrase] = item

    ranked = sorted(best.values(), key=lambda x: (-int(x["score"]), x["phrase"]))
    return ranked


def select_upload_phrases(
    workspace_id: str,
    doc_id: str,
    original_name: str,
    html: str,
    text: str,
) -> Dict[str, Any]:
    paragraphs = _extract_paragraphs(html, text)

    candidates: List[Dict[str, Any]] = []
    candidates.extend(_select_structured_candidates(original_name, html))
    candidates.extend(_select_entity_candidates(paragraphs))
    candidates.extend(_select_intent_candidates(paragraphs))
    candidates.extend(_select_noun_phrase_candidates(paragraphs))

    selected = _dedupe_and_rank(candidates, keep_threshold=60)

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "doc_id": doc_id,
        "paragraph_count": len(paragraphs),
        "candidate_count": len(candidates),
        "selected_count": len(selected),
        "phrases": selected,
    }