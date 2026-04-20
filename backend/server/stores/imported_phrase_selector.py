from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List, Optional, Set, Tuple

from backend.server.stores.phrase_vertical_policy import (
    apply_vertical_policy_score,
    detect_vertical,
    get_vertical_min_score,
)


WORD_RE = re.compile(r"[a-z0-9]{2,}", re.I)
NON_ALNUM_RE = re.compile(r"[^a-z0-9\s\-]")
SPACE_RE = re.compile(r"\s+")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")

STOPWORDS: Set[str] = {
    "the", "and", "for", "with", "that", "this", "from", "into", "your", "you", "are", "was", "were",
    "will", "can", "could", "should", "would", "have", "has", "had", "about", "over", "under", "than",
    "then", "when", "what", "where", "which", "who", "whom", "why", "how", "a", "an", "to", "of", "in",
    "on", "at", "by", "or", "as", "is", "it", "be", "not", "no", "if", "but", "so", "because", "after",
    "before", "during", "while", "through", "up", "down", "out", "off", "too", "very", "also"
}

WEAK_STARTS: Set[str] = {
    "the", "this", "that", "these", "those", "your", "is", "are", "was", "were",
    "while", "so", "then", "after", "before", "with", "for", "by", "from"
}

WEAK_ENDINGS: Set[str] = {
    "about", "around", "roughly", "always", "usually", "often", "matter",
    "like", "such", "each", "one", "after", "before", "with", "for", "by", "from"
}

NARRATIVE_VERBS: Set[str] = {
    "is", "are", "was", "were", "can", "will", "would", "may", "might", "should"
}

UI_JUNK_TERMS: Set[str] = {
    "faq", "skip", "menu", "share", "home", "read more", "previous", "next",
    "written by", "contact us", "about us", "privacy policy", "terms", "cookie",
    "login", "register", "subscribe", "follow us", "facebook", "instagram",
    "twitter", "youtube", "whatsapp", "telegram"
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

IMPORTED_ALIAS_MAP: Dict[str, List[str]] = {
    "ivf": ["in vitro fertilization"],
    "bbt": ["basal body temperature"],
    "lmp": ["last menstrual period"],
    "otc": ["over the counter"],
    "uti": ["urinary tract infection"],
    "bp": ["blood pressure"],
}


def _canonical_phrase(s: str) -> str:
    s = (s or "").strip().lower()
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    s = s.replace("_", " ").replace("/", " ").replace("\\", " ")
    s = NON_ALNUM_RE.sub(" ", s)
    s = re.sub(r"^\s*(?:\d+[\.\)]\s+|[•\-–]\s+)", "", s)
    s = re.sub(r"^[\"'“”‘’\(\[\{]+|[\"'“”‘’\)\]\}:;,\.\!\?]+$", "", s).strip()
    s = SPACE_RE.sub(" ", s).strip()

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

    tail_words = ("and", "or", "but", "as", "to", "from", "with", "by", "vs")
    changed = True
    while changed and s:
        changed = False
        for w in tail_words:
            suffix = " " + w
            if s.endswith(suffix):
                s = s[:-len(suffix)].strip()
                changed = True

    s = SPACE_RE.sub(" ", s).strip()
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

    return _canonical_phrase(s)


def _looks_like_intent_phrase(phrase: str) -> bool:
    p = _canonical_phrase(phrase)
    return any(rx.match(p) for rx in INTENT_PATTERNS)


def _is_link_worthy_shape(phrase: str) -> bool:
    p = _canonical_phrase(phrase)
    if not p or _looks_like_ui_junk(p):
        return False

    tokens = _tokenize(p)
    if len(tokens) < 2 or len(tokens) > 7:
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

def _reject_weak_imported_fragment(phrase: str, full_title: str) -> bool:
    p = _canonical_phrase(phrase)
    full = _canonical_phrase(full_title)

    if not p:
        return True

    tokens = _tokenize(p)
    if len(tokens) < 2:
        return True

    if tokens[0] in {"after", "before", "with", "for", "from", "by", "your"}:
        return True
    if tokens[-1] in {"after", "before", "with", "for", "from", "by", "your"}:
        return True

    if len(tokens) == 2 and any(t in {"after", "before", "with", "for", "your"} for t in tokens):
        return True

    if p != full and full.startswith(p) and len(tokens) >= 3 and tokens[-1] in {
        "during", "with", "for", "after", "before", "and", "in", "of", "to", "your"
    }:
        return True

    if p != full and full.endswith(p) and tokens[0] in {
        "during", "with", "for", "after", "before", "and", "in", "of", "to", "your"
    }:
        return True

    if len(tokens) == 2 and not _looks_like_intent_phrase(p):
        content = _content_tokens(tokens)
        if len(content) < 2:
            return True

    return False

def _reject_weak_imported_subphrase(phrase: str, full_title: str) -> bool:
    p = _canonical_phrase(phrase)
    full = _canonical_phrase(full_title)

    if not p:
        return True

    if _reject_weak_imported_fragment(p, full):
        return True

    pt = _tokenize(p)
    ft = _tokenize(full)

    if len(pt) < 2:
        return True

    weak_connectors = {
        "during", "with", "for", "after", "before", "and", "in", "of", "to",
        "your", "the", "a", "an", "at"
    }

    weak_starts = {
        "how", "what", "when", "why", "long", "does", "it", "understanding",
        "managing", "planning", "dealing", "care", "guide"
    }

    weak_ends = {
        "naturally", "safely", "works", "explained", "guide", "tips",
        "basics", "checklist"
    }

    bad_patterns = {
        "cycle naturally",
        "conception timeline how long",
        "conception timeline how long does",
        "does it take to get",
        "it take to get pregnant",
        "timeline how long does",
        "timeline how long does it",
        "nutrition guide for the first",
        "sickness during early pregnancy",
        "managing morning sickness during early",
        "morning sickness during early",
        "how to create birth",
        "create birth plan that",
        "101 the first week",
        "101 the first week at",
        "care 101 the first",
        "care 101 the first week",
        "cord care for new",
        "breastfeeding positions for better",
        "how to increase breast",
        "pumping and storing breast",
        "floor exercises after birth",
        "options after pregnancy",
        "emotional health during the postpartum",
        "health during the postpartum period",
    }

    if p in bad_patterns:
        return True

    # reject truncated edge fragments from longer titles
    if len(ft) >= 4 and len(pt) < len(ft):
        if full.startswith(p) and pt[-1] in weak_connectors:
            return True
        if full.endswith(p) and pt[0] in weak_connectors:
            return True

    # reject short helper / explainer fragments
    if pt[-1] in weak_ends and len(pt) <= 3:
        return True

    # reject weak verb-chain or helper-led fragments
    if len(pt) <= 4 and pt[0] in weak_starts and not _looks_like_intent_phrase(p):
        return True

    # reject weak 2-word fragments unless clearly specific
    if len(pt) == 2 and not _looks_like_intent_phrase(p):
        content = _content_tokens(pt)
        if len(content) < 2:
            return True
        if pt[0] in {"how", "long", "does", "your", "the", "care"}:
            return True
        if pt[1] in {"your", "the", "period", "naturally", "safely"}:
            return True

    # reject many weak 3-word fragments ending in helper words
    if len(pt) == 3 and pt[-1] in weak_connectors:
        return True

    return False


def _score_candidate(phrase: str, source_type: str, freq: int = 1) -> int:
    p = _canonical_phrase(phrase)
    if not p:
        return 0

    tokens = _tokenize(p)
    content = _content_tokens(tokens)
    score = 0

    if _looks_like_intent_phrase(p):
        score += 30

    if source_type == "import_title":
        score += 34
    elif source_type == "import_title_subphrase":
        score += 22
    elif source_type == "import_slug":
        score += 16
    elif source_type == "import_alias":
        score += 12
    elif source_type == "import_summary_intent":
        score += 12
    elif source_type == "import_summary_phrase":
        score += 8

    if _is_link_worthy_shape(p):
        score += 20

    if len(content) >= 3:
        score += 10

    if 2 <= len(tokens) <= 5:
        score += 6

    if freq >= 2:
        score += min(freq * 3, 10)

    if tokens and tokens[0] in WEAK_STARTS and not _looks_like_intent_phrase(p):
        score -= 25

    if len(tokens) >= 2 and tokens[1] in NARRATIVE_VERBS and not _looks_like_intent_phrase(p):
        score -= 20

    if tokens and tokens[-1] in WEAK_ENDINGS:
        score -= 15

    return score


def _slug_to_phrase(slug_or_url: str) -> str:
    s = (slug_or_url or "").strip().lower()
    s = s.split("?")[0].split("#")[0]
    s = s.rstrip("/").rsplit("/", 1)[-1]
    s = s.replace(".html", "").replace(".htm", "")
    s = s.replace("_", " ").replace("-", " ")
    return _canonical_phrase(s)


def _extract_title_candidates(title: str) -> List[Dict[str, Any]]:
    full = _extract_canonical_core_phrase(title) or _canonical_phrase(title)
    if not full:
        return []

    out: List[Dict[str, Any]] = [{
        "phrase": full,
        "source_type": "import_title",
        "section_id": "title_0",
        "snippet": title,
    }]

    tokens = _tokenize(full)
    if len(tokens) >= 2:
        spans: Set[str] = set()

        for n in (2, 3, 4, 5):
            if len(tokens) >= n:
                spans.add(" ".join(tokens[:n]))
                spans.add(" ".join(tokens[-n:]))

        for n in (2, 3, 4, 5):
            if len(tokens) >= n:
                for i in range(0, len(tokens) - n + 1):
                    spans.add(" ".join(tokens[i:i+n]))

        for sp in sorted(spans):
            if sp == full:
                continue
            if _reject_weak_imported_subphrase(sp, full):
                continue
            out.append({
                "phrase": sp,
                "source_type": "import_title_subphrase",
                "section_id": f"title_span_{len(out)}",
                "snippet": title,
            })

    return out


def _extract_slug_candidates(url: str, full_title: str) -> List[Dict[str, Any]]:
    slug_phrase = _slug_to_phrase(url)
    if not slug_phrase:
        return []

    out: List[Dict[str, Any]] = []
    if slug_phrase != _canonical_phrase(full_title):
        out.append({
            "phrase": slug_phrase,
            "source_type": "import_slug",
            "section_id": "slug_0",
            "snippet": url,
        })

    tokens = _tokenize(slug_phrase)
    spans: Set[str] = set()
    for n in (2, 3, 4, 5):
        if len(tokens) >= n:
            spans.add(" ".join(tokens[:n]))
            spans.add(" ".join(tokens[-n:]))

    for sp in sorted(spans):
        if sp == slug_phrase:
            continue
        if _reject_weak_imported_subphrase(sp, full_title or slug_phrase):
            continue
        out.append({
            "phrase": sp,
            "source_type": "import_slug",
            "section_id": f"slug_span_{len(out)}",
            "snippet": url,
        })

    return out


def _extract_alias_candidates(title: str, url: str) -> List[Dict[str, Any]]:
    source = _canonical_phrase(title + " " + url)
    if not source:
        return []

    out: List[Dict[str, Any]] = []
    for canonical, variants in IMPORTED_ALIAS_MAP.items():
        if canonical in source or any(_canonical_phrase(v) in source for v in variants):
            all_forms = {canonical, *[_canonical_phrase(v) for v in variants]}
            for form in all_forms:
                if not form:
                    continue
                out.append({
                    "phrase": form,
                    "source_type": "import_alias",
                    "section_id": f"alias_{canonical}",
                    "snippet": title or url,
                })

    return out


def _extract_summary_candidates(summary: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if not summary:
        return out

    for i, sent in enumerate(_split_sentences(summary)):
        sent_core = _extract_canonical_core_phrase(sent)

        if sent_core and _looks_like_intent_phrase(sent_core):
            intent_tokens = _tokenize(sent_core)
            if 3 <= len(intent_tokens) <= 7:
                out.append({
                    "phrase": sent_core,
                    "source_type": "import_summary_intent",
                    "section_id": f"summary_intent_{i}",
                    "snippet": sent,
                })

        tokens = _tokenize(sent)
        if len(tokens) < 2:
            continue

        for n in (2, 3, 4, 5):
            if len(tokens) < n:
                continue

            for j in range(0, len(tokens) - n + 1):
                cand = _canonical_phrase(" ".join(tokens[j:j+n]))
                if not cand:
                    continue
                if _reject_weak_imported_fragment(cand, sent):
                    continue
                if not _is_link_worthy_shape(cand):
                    continue

                out.append({
                    "phrase": cand,
                    "source_type": "import_summary_phrase",
                    "section_id": f"summary_phrase_{i}_{j}_{n}",
                    "snippet": sent,
                })

    return out


def _dedupe_and_rank(
    candidates: List[Dict[str, Any]],
    vertical: str,
) -> List[Dict[str, Any]]:
    counter = Counter(_canonical_phrase(c["phrase"]) for c in candidates if c.get("phrase"))
    best: Dict[str, Dict[str, Any]] = {}
    keep_threshold = get_vertical_min_score(vertical)

    for c in candidates:
        phrase = _canonical_phrase(c.get("phrase", ""))
        if not phrase:
            continue

        base_score = _score_candidate(
            phrase,
            str(c.get("source_type") or ""),
            counter.get(phrase, 1),
        )
        score = apply_vertical_policy_score(phrase, base_score, vertical)

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

    return sorted(best.values(), key=lambda x: (-int(x["score"]), x["phrase"]))


def select_imported_phrases(
    workspace_id: str,
    import_id: str,
    title: str,
    url: str,
    summary: str = "",
    aliases: Optional[List[str]] = None,
) -> Dict[str, Any]:
    aliases = aliases or []
    title = title or ""
    url = url or ""
    summary = summary or ""

    candidates: List[Dict[str, Any]] = []
    candidates.extend(_extract_title_candidates(title))
    candidates.extend(_extract_slug_candidates(url, title))
    candidates.extend(_extract_alias_candidates(title + " " + " ".join(aliases), url))

    for idx, alias in enumerate(aliases):
        alias_p = _canonical_phrase(alias)
        if alias_p and not _reject_weak_imported_fragment(alias_p, title or alias_p):
            candidates.append({
                "phrase": alias_p,
                "source_type": "import_alias",
                "section_id": f"user_alias_{idx}",
                "snippet": alias,
            })

    candidates.extend(_extract_summary_candidates(summary))

    combined_text = "\n".join([
        title,
        url,
        summary,
        " ".join(aliases),
    ]).lower()

    vertical = detect_vertical(combined_text)
    selected = _dedupe_and_rank(candidates, vertical=vertical)

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "import_id": import_id,
        "vertical": vertical,
        "candidate_count": len(candidates),
        "selected_count": len(selected),
        "phrases": selected,
    }