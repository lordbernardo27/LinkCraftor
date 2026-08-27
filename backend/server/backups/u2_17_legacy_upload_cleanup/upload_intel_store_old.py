# backend/server/stores/upload_intel_store.py
from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


WORD_RE = re.compile(r"[a-z0-9]{2,}", re.I)
H_RE = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.IGNORECASE | re.DOTALL)
LI_RE = re.compile(r"<li[^>]*>(.*?)</li>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")

NGRAM_MIN_N = 2
NGRAM_MAX_N = 5
MAX_NGRAMS_PER_SENTENCE = 120
MAX_EXAMPLES_PER_PHRASE = 5

STOPWORDS: Set[str] = {
    "the", "and", "for", "with", "that", "this", "from", "into", "your", "you", "are", "was", "were",
    "will", "can", "could", "should", "would", "have", "has", "had", "about", "over", "under", "than",
    "then", "when", "what", "where", "which", "who", "whom", "why", "how", "a", "an", "to", "of", "in",
    "on", "at", "by", "or", "as", "is", "it", "be", "not", "no", "if", "but", "so", "because", "after",
    "before", "during", "while", "through", "up", "down", "out", "off", "too", "very", "also"
}


META_NOISE_PHRASES: Set[str] = {
    "long tail phrases",
    "helpful long tail phrases",
    "this guide",
    "guide explains",
    "no jargon guide",
    "you ll also see",
    "you will also see",
    "you may even",
    "you might know",
    "can search deeper",
    "clinic or app",
    "special situations",
    "actual day",
    "each one",
}

BOUNDARY_WEAK_WORDS: Set[str] = {
    "the", "a", "an", "and", "or", "but", "about", "this", "that", "these", "those", "to", "of", "for",
    "from", "with", "by", "in", "on", "at", "as", "is", "are", "was", "were", "be", "been", "being",
    "it", "its", "their", "there", "here", "what", "which", "who"
}

UI_JUNK_TERMS: Set[str] = {
    "faq", "skip", "menu", "share", "home", "read more", "previous", "next", "written by", "contact us",
    "about us", "privacy policy", "terms", "cookie", "login", "register", "subscribe", "follow us",
    "facebook", "instagram", "twitter", "youtube", "whatsapp", "telegram"
}

NAME_NOISE_PATTERNS: List[re.Pattern[str]] = [
    re.compile(r"^[a-z]+ [a-z]+$"),
]

ENTITY_SEEDS: List[Tuple[str, str]] = [
    ("lmp", "CLINICAL_TERM"),
    ("ovulation", "CLINICAL_TERM"),
    ("basal body temperature", "MEASUREMENT"),
    ("bbt", "MEASUREMENT"),
    ("ultrasound", "PROCEDURE"),
    ("gestational age", "MEASUREMENT"),
    ("conception date", "CLINICAL_TERM"),
    ("due date", "CLINICAL_TERM"),
    ("fertile window", "CLINICAL_TERM"),
    ("cervical mucus", "CLINICAL_TERM"),
    ("morning sickness", "CLINICAL_TERM"),
    ("first trimester", "CLINICAL_TERM"),
    ("postpartum", "CLINICAL_TERM"),
    ("breastfeeding", "CLINICAL_TERM"),
    ("newborn", "CLINICAL_TERM"),
]

STRUCTURED_SOURCE_PRIORITY = {
    "title": 1.00,
    "heading_h1": 1.00,
    "heading_h2": 0.95,
    "heading_h3": 0.90,
    "list_item": 0.85,
    "sentence": 0.70,
    "alias": 0.60,
}

INTENT_FIRST_WORDS: Set[str] = {
    "how", "when", "what", "why", "where", "best", "signs", "symptoms", "causes", "treatment"
}

INTENT_SECOND_WORDS: Set[str] = {
    "to", "do", "does", "did", "is", "are", "for", "of", "time", "way"
}

SEMANTIC_HEAD_WORDS: Set[str] = {
    "window", "timing", "cycle", "date", "age", "symptoms", "signs", "treatment", "cause", "causes",
    "tracking", "method", "methods", "temperature", "mucus", "ovulation", "fertility", "pregnancy",
    "ultrasound", "trimester", "postpartum", "newborn", "breastfeeding", "conception", "planning",
    "period", "luteal", "gestational", "body"
}

LOW_VALUE_PATTERNS: Tuple[str, ...] = (
    "part of",
    "type of",
    "kind of",
    "one of",
    "some of",
    "based on",
    "related to",
    "in terms of",
    "as part of",
)

TRANSFORMATION_PATTERN_RE = re.compile(r"\b(?:turn|turns|turned|turning)\b.*\binto\b")
BECOMES_PATTERN_RE = re.compile(r"\b(?:become|becomes|became|becoming)\b")
MID_SENTENCE_FRAGMENT_RE = re.compile(
    r"\b(?:turns|becomes|become|helps|makes|allows|lets|keeps|provides|shows|means)\b"
)

WEAK_VERB_STARTS: Set[str] = {
    "turns", "turn", "turned", "turning",
    "makes", "make", "made", "making",
    "helps", "help", "helped", "helping",
    "allows", "allow", "allowed", "allowing",
    "gives", "give", "gave", "giving",
    "lets", "let",
    "keeps", "keep", "kept", "keeping",
    "provides", "provide", "provided", "providing",
    "shows", "show", "showed", "showing",
    "means", "mean", "meant",
    "becomes", "become", "became", "becoming",
    "understand", "understanding",
    "discover", "discovering",
    "find", "finding",
    "use", "using",
    "trying", "practice"
}


def _ws_safe(ws: str) -> str:
    ws = (ws or "default").strip().lower()
    ws = re.sub(r"[^a-z0-9_\-]", "_", ws)[:80] or "default"
    if ws.startswith("ws_ws_"):
        ws = ws[3:]
    return ws


def _data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _strip_tags(s: str) -> str:
    s = TAG_RE.sub(" ", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _norm_text(s: str) -> str:
    s = (s or "").strip().lower()
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _strip_leading_numbering(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"^\s*(?:\d+[\.\)]\s+|[•\-–]\s+)", "", s)
    return s.strip()


def _collapse_repeated_adjacent_words(s: str) -> str:
    toks = s.split()
    if not toks:
        return ""
    out = [toks[0]]
    for tok in toks[1:]:
        if tok != out[-1]:
            out.append(tok)
    return " ".join(out).strip()


def _canonical_phrase(s: str) -> str:
    s = _strip_leading_numbering(s)
    s = _norm_text(s)
    s = re.sub(r"^[\"'“”‘’\(\[\{]+|[\"'“”‘’\)\]\}:;,\.\!\?]+$", "", s).strip()
    s = re.sub(r"^drafts\s+", "", s).strip()
    s = re.sub(r"\s+", " ", s).strip()
    s = _collapse_repeated_adjacent_words(s)
    return s


def _extract_canonical_core_phrase(s: str) -> str:
    s = _canonical_phrase(s)
    if not s:
        return ""

    intent_markers = [
        "how to ",
        "when do ",
        "what is ",
        "what are ",
        "why does ",
        "why do ",
        "where is ",
        "where do ",
        "signs of ",
        "symptoms of ",
        "causes of ",
        "treatment for ",
        "best time ",
        "best way ",
    ]

    starts = [s.find(m) for m in intent_markers if s.find(m) != -1]
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

    trailing_cut_patterns = [
        r"^(how to [a-z0-9\s\-]{1,80}?)(?:\s+after\b.*|\s+with\b.*|\s+for\b.*|\s+during\b.*|\s+because\b.*)$",
        r"^(when do [a-z0-9\s\-]{1,80}?)(?:\s+after\b.*|\s+with\b.*|\s+during\b.*)$",
        r"^(what is [a-z0-9\s\-]{1,80}?)(?:\s+for\b.*|\s+in\b.*)$",
        r"^(signs of [a-z0-9\s\-]{1,80}?)(?:\s+in\b.*|\s+during\b.*)$",
        r"^(symptoms of [a-z0-9\s\-]{1,80}?)(?:\s+in\b.*|\s+during\b.*)$",
    ]
    for pat in trailing_cut_patterns:
        m = re.match(pat, s)
        if m:
            s = m.group(1).strip()
            break

    return _canonical_phrase(s)


def _aliases_for_phrase(s: str) -> List[str]:
    raw = (s or "").strip()
    if not raw:
        return []

    base = _canonical_phrase(raw)
    no_punct = re.sub(r"[^a-z0-9\s\-]", "", base)
    no_punct = re.sub(r"\s+", " ", no_punct).strip()
    hy = no_punct.replace(" ", "-")

    seen: Set[str] = set()
    out: List[str] = []

    for v in (base, no_punct, hy):
        v = (v or "").strip()
        if v and v not in seen:
            out.append(v)
            seen.add(v)

    for m in re.findall(r"\(([A-Za-z]{2,6})\)", raw):
        a = m.strip().upper()
        if a and a not in seen:
            out.append(a)
            seen.add(a)

    for tok in re.findall(r"\b[A-Z]{2,6}\b", raw):
        if tok not in seen:
            out.append(tok)
            seen.add(tok)

    return out


def _tokenize(text: str) -> List[str]:
    if not text:
        return []
    return [t.lower() for t in WORD_RE.findall(text.lower())]


def _split_paragraphs(html: str, text: str) -> List[str]:
    html = html or ""
    paras: List[str] = []

    for inner in P_RE.findall(html):
        t = _strip_tags(inner)
        if t:
            paras.append(t)

    if paras:
        return paras

    t = (text or "").replace("\r\n", "\n")
    return [c.strip() for c in re.split(r"\n\s*\n+", t) if c.strip()]

def _split_sentences(text: str) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    return [p.strip() for p in SENTENCE_SPLIT_RE.split(text) if p and p.strip()]


def _is_valid_content_sentence(text: str) -> bool:
    t = _canonical_phrase(text)
    if not t:
        return False

    if re.search(r"\b(long tail phrases?|helpful phrases?|phrases such as)\b", t):
        return False

    if re.search(r"\b(guide|explains|explained|explaining)\b", t):
        return False

    if re.search(r"\b(you will|you ll|you may|you might|you can)\b", t):
        return False

    if re.search(r"\b(for example|example of|such as)\b", t):
        return False

    return True


def _extract_headings(html: str) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    html = html or ""
    found = [(lvl, _strip_tags(inner)) for (lvl, inner) in H_RE.findall(html)]
    found2: List[Tuple[int, str]] = []
    for l, t in found:
        try:
            lvl = int(l)
        except Exception:
            continue
        if t:
            found2.append((lvl, t))

    h1 = next((t for (lvl, t) in found2 if lvl == 1 and t), None)

    headings: List[Dict[str, Any]] = []
    for lvl, t in found2:
        if lvl in (2, 3):
            headings.append({
                "level": lvl,
                "text": t,
                "aliases": _aliases_for_phrase(t),
            })

    return h1, headings


def _extract_list_items(html: str) -> List[str]:
    html = html or ""
    out: List[str] = []
    for inner in LI_RE.findall(html):
        t = _strip_tags(inner)
        if t:
            out.append(t)
    return out


def _looks_like_ui_junk(s: str) -> bool:
    t = _canonical_phrase(s)
    if not t:
        return True
    return any(junk in t for junk in UI_JUNK_TERMS)


def _numeric_ratio(tokens: List[str]) -> float:
    if not tokens:
        return 0.0
    num = sum(1 for t in tokens if any(ch.isdigit() for ch in t))
    return num / max(len(tokens), 1)


def _stopword_ratio(tokens: List[str]) -> float:
    if not tokens:
        return 1.0
    sw = sum(1 for t in tokens if t in STOPWORDS)
    return sw / max(len(tokens), 1)


def _looks_like_name_noise(s: str) -> bool:
    t = _canonical_phrase(s)
    toks = t.split()
    if len(toks) == 2 and all(tok.isalpha() and len(tok) >= 3 for tok in toks):
        if t not in {seed for seed, _ in ENTITY_SEEDS}:
            return any(pat.match(t) for pat in NAME_NOISE_PATTERNS)
    return False


def _is_numeric_fragment(tokens: List[str]) -> bool:
    if not tokens:
        return True
    if _numeric_ratio(tokens) >= 0.5:
        return True

    joined = " ".join(tokens)
    return bool(
        re.fullmatch(
            r"(?:\d+|day|days|week|weeks|month|months|year|years)(?:\s+(?:\d+|day|days|week|weeks|month|months|year|years))*",
            joined,
        )
    )


def _looks_like_intent_phrase(tokens: List[str]) -> bool:
    if not tokens:
        return False

    if len(tokens) >= 3:
        if tokens[0] in {"how", "when", "what", "why", "where"}:
            if tokens[1] in {"to", "do", "does", "did", "is", "are", "can", "should", "will"}:
                return True

    if len(tokens) >= 3:
        if tokens[0] == "best" and tokens[1] in {"time", "way"}:
            return True

    if len(tokens) >= 3:
        if tokens[0] in {"signs", "symptoms", "causes", "treatment"} and tokens[1] in {"of", "for"}:
            return True

    if tokens[0] in {"want", "trying", "just", "need"}:
        return False

    return False


def _bad_boundary(tokens: List[str]) -> bool:
    if not tokens:
        return True
    if _looks_like_intent_phrase(tokens):
        return False
    if tokens[0] in BOUNDARY_WEAK_WORDS:
        return True
    if tokens[-1] in BOUNDARY_WEAK_WORDS:
        return True
    return False


def _content_tokens(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in STOPWORDS]


def _semantic_seed_hits(joined: str) -> int:
    hits = 0
    for seed, _etype in ENTITY_SEEDS:
        if seed in joined:
            hits += 1
    return hits


def _is_nounish_token(tok: str) -> bool:
    if not tok:
        return False
    if tok in STOPWORDS:
        return False
    if tok in WEAK_VERB_STARTS:
        return False
    if tok in {"becomes", "become", "became", "becoming", "turns", "turn", "turned", "turning"}:
        return False
    return True


def _looks_like_clause_fragment(tokens: List[str]) -> bool:
    if not tokens:
        return True

    joined = " ".join(tokens)

    if TRANSFORMATION_PATTERN_RE.search(joined):
        return True

    if BECOMES_PATTERN_RE.search(joined):
        return True

    if len(tokens) >= 2 and tokens[0] in WEAK_VERB_STARTS:
        return True

    if len(tokens) >= 2 and tokens[0] in {"your", "this", "that", "these", "those"}:
        return True

    if tokens[0] in {"want", "trying", "try", "need", "just"}:
        return True

    if "want to" in joined:
        return True

    if "trying to" in joined:
        return True

    if "just want to" in joined:
        return True

    if "question becomes" in joined:
        return True

    if "method turns" in joined:
        return True

    return False


def _looks_like_clean_noun_phrase(tokens: List[str]) -> bool:
    if not tokens:
        return False

    if len(tokens) < 2 or len(tokens) > 4:
        return False

    if _looks_like_intent_phrase(tokens):
        return False

    if _looks_like_clause_fragment(tokens):
        return False

    if tokens[0] in BOUNDARY_WEAK_WORDS or tokens[-1] in BOUNDARY_WEAK_WORDS:
        return False

    content = _content_tokens(tokens)
    if len(content) < 2:
        return False

    if any(tok in WEAK_VERB_STARTS for tok in tokens):
        return False

    if any(tok in {"becomes", "become", "became", "becoming", "turns", "turn", "turned", "turning"} for tok in tokens):
        return False

    nounish = sum(1 for tok in tokens if _is_nounish_token(tok))
    if nounish < 2:
        return False

    return True


def _classify_candidate(tokens: List[str]) -> str:
    if not tokens:
        return "bad"

    joined = " ".join(tokens)

    if _looks_like_clause_fragment(tokens):
        return "clause_fragment"

    if _looks_like_intent_phrase(tokens):
        return "intent"

    if joined in {seed for seed, _ in ENTITY_SEEDS}:
        return "entity"

    if _semantic_seed_hits(joined) > 0 and _looks_like_clean_noun_phrase(tokens):
        return "entityish"

    if _looks_like_clean_noun_phrase(tokens):
        return "noun_phrase"

    return "fragment"


def _structure_score(tokens: List[str]) -> float:
    if not tokens:
        return 0.0

    if len(tokens) < NGRAM_MIN_N or len(tokens) > NGRAM_MAX_N:
        return 0.0

    if _bad_boundary(tokens):
        return 0.0

    if _is_numeric_fragment(tokens):
        return 0.0

    sw_ratio = _stopword_ratio(tokens)
    if _looks_like_intent_phrase(tokens):
        if sw_ratio > 0.60:
            return 0.0
    else:
        if sw_ratio > 0.34:
            return 0.0

    alpha_tokens = sum(1 for t in tokens if re.search(r"[a-z]", t))
    if alpha_tokens < max(2, len(tokens) - 1):
        return 0.0

    base = 0.50
    if 2 <= len(tokens) <= 4:
        base += 0.15
    elif len(tokens) == 5:
        base += 0.05

    if sw_ratio < 0.20:
        base += 0.10

    return min(base, 1.0)


def _semantic_independence_score(tokens: List[str]) -> float:
    if not tokens:
        return 0.0

    joined = " ".join(tokens)
    content = _content_tokens(tokens)
    score = 0.0

    if len(content) >= 2:
        score += 0.35

    if _semantic_seed_hits(joined) > 0:
        score += 0.30

    if tokens[-1] in SEMANTIC_HEAD_WORDS:
        score += 0.20

    if _looks_like_intent_phrase(tokens):
        score += 0.25

    if len(tokens) <= 4 and len(content) >= 2:
        score += 0.10

    return min(score, 1.0)


def _anchor_fitness_score(tokens: List[str]) -> float:
    if not tokens:
        return 0.0

    joined = " ".join(tokens)
    score = 0.0

    if _looks_like_intent_phrase(tokens):
        score += 0.45

    if 2 <= len(tokens) <= 4:
        score += 0.30
    elif len(tokens) == 5:
        score += 0.15

    if tokens[-1] in SEMANTIC_HEAD_WORDS:
        score += 0.15

    if _semantic_seed_hits(joined) > 0:
        score += 0.15

    return min(score, 1.0)


def _context_dependency_penalty(tokens: List[str]) -> float:
    if not tokens:
        return 1.0

    joined = " ".join(tokens)
    penalty = 0.0

    if _looks_like_clause_fragment(tokens):
        penalty += 0.85

    if TRANSFORMATION_PATTERN_RE.search(joined):
        penalty += 0.85

    if BECOMES_PATTERN_RE.search(joined):
        penalty += 0.65

    if MID_SENTENCE_FRAGMENT_RE.search(joined) and not _looks_like_intent_phrase(tokens):
        penalty += 0.30

    if any(p in joined for p in LOW_VALUE_PATTERNS):
        penalty += 0.35

    if len(tokens) >= 3 and tokens[0] in {"your", "this", "that", "these", "those"}:
        penalty += 0.45

    return min(penalty, 1.0)


def _score_candidate(tokens: List[str]) -> float:
    if not tokens:
        return 0.0

    ctype = _classify_candidate(tokens)
    if ctype == "bad":
        return 0.0

    structure = _structure_score(tokens)
    if structure <= 0.0:
        return 0.0

    semantic = _semantic_independence_score(tokens)
    anchor = _anchor_fitness_score(tokens)
    penalty = _context_dependency_penalty(tokens)

    type_bonus = {
        "intent": 0.20,
        "entity": 0.20,
        "entityish": 0.12,
        "noun_phrase": 0.15,
        "general_phrase": 0.05,
        "fragment": -0.20,
        "clause_fragment": -0.40,
    }.get(ctype, 0.0)

    final = (0.40 * structure) + (0.35 * semantic) + (0.25 * anchor) + type_bonus - penalty
    return round(max(0.0, min(final, 1.0)), 4)


def _accept_candidate(tokens: List[str]) -> bool:
    if not tokens:
        return False

    ctype = _classify_candidate(tokens)
    score = _score_candidate(tokens)

    if ctype == "intent":
        return score >= 0.48

    if ctype in {"entity", "entityish"}:
        return score >= 0.50

    if ctype == "noun_phrase":
        return score >= 0.55

    return False

def _fails_semantic_filter(phrase: str) -> bool:
    p = _canonical_phrase(phrase)
    if not p:
        return True

    if re.search(r"\b(long tail phrases?|helpful phrases?|phrases such as)\b", p):
        return True

    if re.search(r"\b(you ll|you will|you may|you might|you can)\b", p):
        return True

    if re.search(r"\b(guide|explains|explained|explaining)\b", p):
        return True

    if re.search(r"\b(such as|for example|example of)\b", p):
        return True

    if re.search(r"\b(actual day|each one|small mystery)\b", p):
        return True

    tokens = _tokenize(p)
    if not tokens:
        return True

    if len(tokens) <= 3 and p in {
        "clinic or app",
        "can search deeper",
        "do you turn",
        "actual day",
        "each one",
    }:
        return True

    bad_starts = {
        "you", "your", "we", "this", "that", "these", "those",
        "explains", "guide", "helpful", "special", "actual"
    }
    if tokens[0] in bad_starts and not _looks_like_intent_phrase(tokens):
        return True

    bad_ends = {"small", "one", "such", "each", "actual"}
    if tokens[-1] in bad_ends:
        return True

    content = _content_tokens(tokens)
    if len(content) < 2 and not _looks_like_intent_phrase(tokens):
        return True

    return False


def _qualify_phrase(raw_phrase: str) -> Tuple[bool, str]:
    phrase = _extract_canonical_core_phrase(raw_phrase)
    if not phrase:
        return False, ""

    if _looks_like_ui_junk(phrase):
        return False, ""

    if _looks_like_name_noise(phrase):
        return False, ""

    if _fails_semantic_filter(phrase):
        return False, ""


    tokens = _tokenize(phrase)
    if not _accept_candidate(tokens):
        return False, ""

    return True, phrase

def _generate_sentence_candidates(sentence: str) -> List[str]:
    s = _canonical_phrase(sentence)
    if not s or _looks_like_ui_junk(s):
        return []

    if not _is_valid_content_sentence(s):
        return []

    clause_parts = [
        _canonical_phrase(x)
        for x in re.split(r"[,;:\-\u2013\u2014]\s+|\s+\bor\b\s+|\s+\band\b\s+", s)
        if _canonical_phrase(x)
    ]

    out: List[str] = []
    made = 0

    for part in clause_parts:
        if not _is_valid_content_sentence(part):
            continue

        tokens = _tokenize(part)
        if len(tokens) < NGRAM_MIN_N or _numeric_ratio(tokens) >= 0.6:
            continue

        for n in range(NGRAM_MIN_N, NGRAM_MAX_N + 1):
            if n > len(tokens):
                break

            for i in range(0, len(tokens) - n + 1):
                cand_tokens = tokens[i:i + n]
                cand = " ".join(cand_tokens).strip()

                # HARD FILTER FIRST
                if _fails_semantic_filter(cand):
                    continue

                ok, norm = _qualify_phrase(cand)
                if not ok or not norm:
                    continue

                out.append(norm)
                made += 1
                if made >= MAX_NGRAMS_PER_SENTENCE:
                    return out

    return out


def _canonical_dominance_filter(phrases: List[str]) -> List[str]:
    cleaned = []
    seen = set()

    for p in phrases:
        p2 = _canonical_phrase(p)
        if not p2:
            continue
        core = _extract_canonical_core_phrase(p2)
        final = core or p2
        if final not in seen:
            cleaned.append(final)
            seen.add(final)

    return cleaned



def _dominance_filter(phrases: List[str]) -> List[str]:
    uniq = sorted(
        set(_canonical_phrase(p) for p in phrases if _canonical_phrase(p)),
        key=lambda x: (-_score_candidate(_tokenize(x)), len(x.split()), x),
        reverse=True,
    )
    kept: List[str] = []

    protected_short_phrases = {
        "ovulation", "ultrasound", "postpartum", "newborn", "breastfeeding",
        "conception date", "due date", "fertile window", "cervical mucus",
        "gestational age", "morning sickness", "first trimester", "lmp", "bbt",
    }

    for p in uniq:
        p_toks = p.split()
        p_score = _score_candidate(_tokenize(p))
        drop = False

        for k in kept:
            k_toks = k.split()

            if len(k_toks) >= len(p_toks) + 1 and " ".join(p_toks) in " ".join(k_toks):
                if len(p_toks) <= 2 and p in protected_short_phrases:
                    continue
                if _looks_like_intent_phrase(p_toks):
                    continue
                if p_score < 0.72:
                    drop = True
                    break

        if not drop:
            kept.append(p)

    return kept


def _derive_alias_variants(phrase: str) -> List[str]:
    p = _canonical_phrase(phrase)
    toks = p.split()
    out: List[str] = []

    if len(toks) >= 3:
        out.append(" ".join(toks[-2:]))
        out.append(" ".join(toks[:2]))
    if len(toks) >= 4:
        out.append(" ".join(toks[1:]))
        out.append(" ".join(toks[:-1]))

    cleaned: List[str] = []
    seen: Set[str] = set()
    for x in out:
        ok, norm = _qualify_phrase(x)
        if ok and norm and norm != p and norm not in seen:
            cleaned.append(norm)
            seen.add(norm)
    return cleaned[:3]


def _detect_entities(paragraph_text: str) -> List[Tuple[str, str]]:
    t = _canonical_phrase(paragraph_text)
    hits: List[Tuple[str, str]] = []

    for label, etype in ENTITY_SEEDS:
        if label in t:
            hits.append((label, etype))

    for tok in re.findall(r"\b[A-Z]{2,6}\b", paragraph_text or ""):
        k = tok.strip().lower()
        if k in {"lmp", "bbt", "edd", "ivf"}:
            hits.append((k, "ACRONYM"))

    seen: Set[Tuple[str, str]] = set()
    out: List[Tuple[str, str]] = []
    for e, et in hits:
        key = (e, et)
        if key in seen:
            continue
        seen.add(key)
        out.append((e, et))
    return out


def _read_json(fp: Path, default: Any) -> Any:
    try:
        if not fp.exists():
            return default
        return json.loads(fp.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json_atomic(fp: Path, obj: Any) -> None:
    fp.parent.mkdir(parents=True, exist_ok=True)
    tmp = fp.with_suffix(fp.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, fp)


def _paths_for_ws(workspace_id: str) -> Dict[str, Path]:
    ws = _ws_safe(workspace_id)
    d = _data_dir()
    return {
        "struct": d / f"upload_struct_{ws}.json",
        "phrases": d / f"upload_phrase_index_{ws}.json",
        "entities": d / f"upload_entity_map_{ws}.json",
        "graph": d / f"upload_entity_graph_{ws}.json",
    }


def _tier_for_source(source_type: str) -> str:
    if source_type in {"title", "heading_h1", "heading_h2", "heading_h3"}:
        return "A"
    if source_type == "list_item":
        return "A"
    if source_type == "sentence":
        return "B"
    return "C"


def _quality_score_for(source_type: str, repeats: int = 1) -> float:
    base = STRUCTURED_SOURCE_PRIORITY.get(source_type, 0.50)
    bonus = min(max(repeats - 1, 0) * 0.05, 0.20)
    return round(min(base + bonus, 1.0), 3)

def _upsert_phrase_record(
    ph: Dict[str, Any],
    phrase: str,
    source_type: str,
    doc_id: str,
    section_id: str,
    snippet: str,
) -> None:
    phrase = _canonical_phrase(phrase)
    core = _extract_canonical_core_phrase(phrase)
    final_phrase = core or phrase

    if _fails_semantic_filter(final_phrase):
        return

    phrase = final_phrase

    now = _now_iso()
    tier = _tier_for_source(source_type)

    rec = ph.get(phrase)
    if not isinstance(rec, dict):
        rec = {
            "phrase": phrase,
            "canonical": phrase,
            "source_type": source_type,
            "tier": tier,
            "count_total": 0,
            "quality_score": _quality_score_for(source_type, 1),
            "docs": {},
            "sections": [],
            "first_seen": now,
            "last_seen": now,
            "examples": [],
            "aliases": _derive_alias_variants(phrase),
        }
        ph[phrase] = rec

    rec["count_total"] = int(rec.get("count_total") or 0) + 1
    rec["last_seen"] = now

    old_tier = str(rec.get("tier") or "C")
    if old_tier == "C" and tier in {"A", "B"}:
        rec["tier"] = tier
    elif old_tier == "B" and tier == "A":
        rec["tier"] = tier

    docs = rec.get("docs") if isinstance(rec.get("docs"), dict) else {}
    rec["docs"] = docs
    docs[doc_id] = int(docs.get(doc_id) or 0) + 1

    sections = rec.get("sections") if isinstance(rec.get("sections"), list) else []
    rec["sections"] = sections
    if section_id and section_id not in sections:
        sections.append(section_id)

    rec["quality_score"] = _quality_score_for(
        str(rec.get("source_type") or source_type),
        int(rec["count_total"])
    )

    ex = rec.get("examples") if isinstance(rec.get("examples"), list) else []
    rec["examples"] = ex
    if len(ex) < MAX_EXAMPLES_PER_PHRASE:
        ex.append({
            "doc_id": doc_id,
            "section_id": section_id,
            "snippet": snippet[:160] + ("…" if len(snippet) > 160 else ""),
        })


def build_upload_intelligence(
    workspace_id: str,
    doc_id: str,
    stored_path: str,
    original_name: str,
    html: str,
    text: str,
) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)
    doc_id = (doc_id or "").strip()
    if not doc_id:
        raise ValueError("doc_id required")

    p = _paths_for_ws(ws)

    struct = _read_json(p["struct"], default={"workspace_id": ws, "updated_at": _now_iso(), "docs": {}})
    if not isinstance(struct, dict):
        struct = {"workspace_id": ws, "updated_at": _now_iso(), "docs": {}}
    struct_docs = struct.get("docs") if isinstance(struct.get("docs"), dict) else {}
    struct["docs"] = struct_docs

    h1, headings = _extract_headings(html or "")
    list_items = _extract_list_items(html or "")
    paragraphs = _split_paragraphs(html or "", text or "")

    doc_rec = {
        "doc_id": doc_id,
        "stored_path": stored_path,
        "original_name": original_name,
        "updated_at": _now_iso(),
        "h1": {"text": h1 or "", "aliases": _aliases_for_phrase(h1 or "") if h1 else []},
        "headings": headings,
        "list_items": [{"text": x, "aliases": _aliases_for_phrase(x)} for x in list_items[:200]],
        "paragraphs": [{"pid": f"p{i}", "text": para} for i, para in enumerate(paragraphs)],
    }
    struct_docs[doc_id] = doc_rec
    struct["updated_at"] = _now_iso()
    _write_json_atomic(p["struct"], struct)

    phrase_index = _read_json(p["phrases"], default={"workspace_id": ws, "updated_at": _now_iso(), "phrases": {}})
    if not isinstance(phrase_index, dict):
        phrase_index = {"workspace_id": ws, "updated_at": _now_iso(), "phrases": {}}
    ph = phrase_index.get("phrases") if isinstance(phrase_index.get("phrases"), dict) else {}
    phrase_index["phrases"] = ph

    entity_map = _read_json(p["entities"], default={"workspace_id": ws, "updated_at": _now_iso(), "entities": {}})
    if not isinstance(entity_map, dict):
        entity_map = {"workspace_id": ws, "updated_at": _now_iso(), "entities": {}}
    em = entity_map.get("entities") if isinstance(entity_map.get("entities"), dict) else {}
    entity_map["entities"] = em

    graph = _read_json(p["graph"], default={"workspace_id": ws, "updated_at": _now_iso(), "nodes": {}, "edges": []})
    if not isinstance(graph, dict):
        graph = {"workspace_id": ws, "updated_at": _now_iso(), "nodes": {}, "edges": []}
    nodes = graph.get("nodes") if isinstance(graph.get("nodes"), dict) else {}
    edges = graph.get("edges") if isinstance(graph.get("edges"), list) else []
    graph["nodes"] = nodes
    graph["edges"] = edges

    def upsert_node(node_id: str, ntype: str, label: str) -> None:
        if not node_id:
            return
        if node_id not in nodes:
            nodes[node_id] = {"type": ntype, "label": label, "w": 0}
        nodes[node_id]["w"] = int(nodes[node_id].get("w") or 0) + 1

    def add_edge(src: str, dst: str, etype: str, w_inc: int = 1) -> None:
        if not src or not dst:
            return
        edges.append({"src": src, "dst": dst, "type": etype, "w": int(w_inc)})

    structured_candidates: List[Tuple[str, str, str, str]] = []

    if h1:
        structured_candidates.append((h1, "heading_h1", "h1", h1))

    for idx, h in enumerate(headings):
        txt = str(h.get("text") or "").strip()
        lvl = int(h.get("level") or 0)
        if txt:
            structured_candidates.append((txt, f"heading_h{lvl}", f"h{lvl}_{idx}", txt))

    for idx, li in enumerate(list_items[:200]):
        structured_candidates.append((li, "list_item", f"li_{idx}", li))

    if original_name:
        title_like = Path(original_name).stem.replace("_", " ").replace("-", " ")
        structured_candidates.append((title_like, "title", "title_0", title_like))

    for raw_text, source_type, section_id, snippet in structured_candidates:
        canonical_raw = _extract_canonical_core_phrase(raw_text)
        ok, phrase = _qualify_phrase(canonical_raw)
        if ok and phrase:
            _upsert_phrase_record(ph, phrase, source_type, doc_id, section_id, snippet)
            upsert_node(f"phrase:{phrase}", "PHRASE", phrase)

        for i, para in enumerate(paragraphs):
          pid = f"p{i}"
        para_snippet = para

        sentence_candidates_all: List[str] = []
        for sentence in _split_sentences(para):
            if not _is_valid_content_sentence(sentence):
                continue
            sentence_candidates = _generate_sentence_candidates(sentence)
            sentence_candidates_all.extend(sentence_candidates)

        sentence_candidates_all = _dominance_filter(sentence_candidates_all)

        seen_in_para: Set[str] = set()
        for g_norm in sentence_candidates_all:
            if not g_norm or g_norm in seen_in_para:
                continue
            seen_in_para.add(g_norm)

            _upsert_phrase_record(ph, g_norm, "sentence", doc_id, pid, para_snippet)
            upsert_node(f"phrase:{g_norm}", "PHRASE", g_norm)

        ents = _detect_entities(para)
        ent_nodes: List[str] = []
        for ent_norm, ent_type in ents:
            ent_norm2 = _canonical_phrase(ent_norm)
            if not ent_norm2:
                continue

            ent_node = f"ent:{ent_norm2}"
            ent_nodes.append(ent_node)

            erec = em.get(ent_norm2)
            if not isinstance(erec, dict):
                erec = {
                    "entity": ent_norm2,
                    "type": ent_type,
                    "mentions_total": 0,
                    "docs": {},
                    "first_seen": _now_iso(),
                    "last_seen": _now_iso(),
                    "examples": [],
                }
                em[ent_norm2] = erec

            erec["mentions_total"] = int(erec.get("mentions_total") or 0) + 1
            erec["last_seen"] = _now_iso()

            edocs = erec.get("docs") if isinstance(erec.get("docs"), dict) else {}
            erec["docs"] = edocs
            edocs[doc_id] = int(edocs.get(doc_id) or 0) + 1

            eex = erec.get("examples") if isinstance(erec.get("examples"), list) else []
            erec["examples"] = eex
            if len(eex) < MAX_EXAMPLES_PER_PHRASE:
                eex.append({
                    "doc_id": doc_id,
                    "pid": pid,
                    "snippet": para[:160] + ("…" if len(para) > 160 else ""),
                })

            upsert_node(ent_node, "ENTITY", ent_norm2)

        for a in range(len(ent_nodes)):
            for b in range(a + 1, len(ent_nodes)):
                add_edge(ent_nodes[a], ent_nodes[b], "CO_OCCUR", 1)

        phrase_nodes = [f"phrase:{x}" for x in list(seen_in_para)[:50]]
        for ent_node in ent_nodes:
            for pn in phrase_nodes:
                add_edge(ent_node, pn, "MENTIONS_NEAR", 1)

        all_phrases = list(ph.keys())

    canonical_phrases = _canonical_dominance_filter(all_phrases)
    filtered_phrases = set(_dominance_filter(canonical_phrases))

    tier_a = set()
    for k, v in ph.items():
        if not isinstance(v, dict):
            continue
        if str(v.get("tier") or "") == "A":
            core = _extract_canonical_core_phrase(k)
            tier_a.add(core or k)

    filtered_phrases |= tier_a

    ph_final: Dict[str, Any] = {}
    for old_key, old_val in ph.items():
        if not isinstance(old_val, dict):
            continue

        new_key = _extract_canonical_core_phrase(old_key) or old_key
        if new_key not in filtered_phrases:
            continue

        rec = ph_final.get(new_key)
        if not isinstance(rec, dict):
            rec = dict(old_val)
            rec["phrase"] = new_key
            rec["canonical"] = new_key
            ph_final[new_key] = rec
            continue

        rec["count_total"] = int(rec.get("count_total") or 0) + int(old_val.get("count_total") or 0)

        old_docs = old_val.get("docs") if isinstance(old_val.get("docs"), dict) else {}
        rec_docs = rec.get("docs") if isinstance(rec.get("docs"), dict) else {}
        rec["docs"] = rec_docs
        for d, c in old_docs.items():
            rec_docs[d] = int(rec_docs.get(d) or 0) + int(c or 0)

        old_sections = old_val.get("sections") if isinstance(old_val.get("sections"), list) else []
        rec_sections = rec.get("sections") if isinstance(rec.get("sections"), list) else []
        rec["sections"] = rec_sections
        for s in old_sections:
            if s not in rec_sections:
                rec_sections.append(s)

        old_examples = old_val.get("examples") if isinstance(old_val.get("examples"), list) else []
        rec_examples = rec.get("examples") if isinstance(rec.get("examples"), list) else []
        rec["examples"] = rec_examples
        for ex in old_examples:
            if len(rec_examples) >= MAX_EXAMPLES_PER_PHRASE:
                break
            rec_examples.append(ex)

        old_aliases = old_val.get("aliases") if isinstance(old_val.get("aliases"), list) else []
        rec_aliases = rec.get("aliases") if isinstance(rec.get("aliases"), list) else []
        merged_aliases = []
        seen_aliases = set()
        for a in rec_aliases + old_aliases:
            if a and a not in seen_aliases and a != new_key:
                merged_aliases.append(a)
                seen_aliases.add(a)
        rec["aliases"] = merged_aliases[:5]

        if str(old_val.get("tier") or "") == "A":
            rec["tier"] = "A"
        elif str(old_val.get("tier") or "") == "B" and str(rec.get("tier") or "") != "A":
            rec["tier"] = "B"

        rec["first_seen"] = min(str(rec.get("first_seen") or ""), str(old_val.get("first_seen") or ""))
        rec["last_seen"] = max(str(rec.get("last_seen") or ""), str(old_val.get("last_seen") or ""))

    phrase_index["phrases"] = ph_final

    phrase_index["updated_at"] = _now_iso()
    _write_json_atomic(p["phrases"], phrase_index)

    entity_map["updated_at"] = _now_iso()
    _write_json_atomic(p["entities"], entity_map)

    graph["updated_at"] = _now_iso()
    _write_json_atomic(p["graph"], graph)

    return {
        "ok": True,
        "workspace_id": ws,
        "doc_id": doc_id,
        "written": {
            "upload_struct": str(p["struct"]),
            "upload_phrase_index": str(p["phrases"]),
            "upload_entity_map": str(p["entities"]),
            "upload_entity_graph": str(p["graph"]),
        },
        "counts": {
            "paragraphs": len(paragraphs),
            "headings_h2h3": len(headings),
            "list_items": len(list_items),
            "phrases_total": len(phrase_index["phrases"]),
        },
    }