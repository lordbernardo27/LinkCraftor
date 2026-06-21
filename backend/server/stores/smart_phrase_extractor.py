"""
smart_phrase_extractor.py (v2) — THE single quality gate.

Two changes from v1 that matter:

1. USEFULNESS, not just completeness.  v1 only proved a phrase wasn't *hanging*.
   That let "signs lead", "find answers", "target pay attention" through because
   they are structurally complete but useless as anchors. v2 adds an explicit
   usefulness test: keep only if the phrase ends on a real head, is a known
   compound, is an action+strong-object anchor, or carries genuine specificity.

2. POS IS AUTHORITATIVE, and the backend is reported.  v1 silently fell back to
   a heuristic tagger whose hardcoded verb list had gaps (it tagged "pay",
   "lead", "detect" as nouns). v2 uses real POS tags for interior-verb
   detection, and `get_active_backend()` / the per-call telemetry tell you which
   tagger actually ran so a prod box without spaCy can't regress invisibly.

Output shape is unchanged: {phrase, source_type, section_id, doc_id, snippet,
extractor_intelligence:{score, signals, decision, backend}}.  Score is computed
ONCE here and is meant to be carried downstream, never recomputed.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from backend.server.stores.phrase_lexicon import (  # in prod: backend.server.stores.phrase_lexicon
    ACTION_VERBS, AUX_VERBS, CONJUNCTIONS, DETERMINERS, FUNCTION_WORDS,
    GENERIC_BUT_ALLOWED_HEADS, EXTRA_WEAK_GENERIC_HEADS, GENERIC_WEAK_HEADS, GERUND_FORMS, ING_ED_NOUNS,
    FINITE_VERB_FORMS, LEXICAL_VERBS, NARRATIVE_FRAGMENT_WORDS, PREPOSITIONS, PRONOUNS, STRONG_HEADS,
    STRONG_MODIFIERS, VALID_ORDERED_PAIRS, WEAK_NON_ANCHOR_MODIFIERS, canonical_phrase, contains_canonical_anchor,
    has_valid_ordered_pair, is_exact_canonical_anchor, tokenize,
)

log = logging.getLogger("phrase_extractor")

# Set LINKCRAFTOR_REQUIRE_POS=1 in production. If no real tagger is available,
# the extractor raises instead of silently running the weaker heuristic path.
_REQUIRE_POS = os.environ.get("LINKCRAFTOR_REQUIRE_POS", "") == "1"

# ---------------------------------------------------------------------------
# Optional learning hook (unchanged contract)
# ---------------------------------------------------------------------------
try:
    from backend.server.stores.dis_pipeline_learning import (  # type: ignore
        learn_from_pipeline_rejection,
    )
except Exception:
    def learn_from_pipeline_rejection(**_kwargs: Any) -> None:
        return None


# ---------------------------------------------------------------------------
# Tagger detection (spaCy -> NLTK -> heuristic) with reporting
# ---------------------------------------------------------------------------
_SPACY_NLP = None
_SPACY_TRIED = False
_NLTK_OK: Optional[bool] = None
_ACTIVE_BACKEND: Optional[str] = None


def _get_spacy():
    global _SPACY_NLP, _SPACY_TRIED
    if _SPACY_TRIED:
        return _SPACY_NLP
    _SPACY_TRIED = True
    try:
        import spacy  # type: ignore
        try:
            _SPACY_NLP = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
        except Exception:
            _SPACY_NLP = None
    except Exception:
        _SPACY_NLP = None
    return _SPACY_NLP


def _have_nltk() -> bool:
    global _NLTK_OK
    if _NLTK_OK is not None:
        return _NLTK_OK
    try:
        import nltk  # type: ignore
        nltk.pos_tag(nltk.word_tokenize("test sentence"))
        _NLTK_OK = True
    except Exception:
        _NLTK_OK = False
    return _NLTK_OK


def get_active_backend() -> str:
    """Resolve and cache which POS backend is in use. Logs a loud warning when
    the heuristic fallback is active, because that is a quality cliff."""
    global _ACTIVE_BACKEND
    if _ACTIVE_BACKEND is not None:
        return _ACTIVE_BACKEND
    if _get_spacy() is not None:
        _ACTIVE_BACKEND = "spacy"
    elif _have_nltk():
        _ACTIVE_BACKEND = "nltk"
    else:
        _ACTIVE_BACKEND = "heuristic"
        msg = ("phrase_extractor running on HEURISTIC tagger — phrase quality is "
               "degraded. Install spaCy 'en_core_web_sm' or NLTK tagger data.")
        if _REQUIRE_POS:
            raise RuntimeError(msg + " (LINKCRAFTOR_REQUIRE_POS=1)")
        log.warning(msg)
    return _ACTIVE_BACKEND


# ---------------------------------------------------------------------------
# POS tagging -> coarse tags carried alongside tokens
# ---------------------------------------------------------------------------
_NOUN_SUFFIXES = ("tion", "sion", "ment", "ness", "ity", "ship", "ance",
                  "ence", "ics", "ism", "age", "ure", "ist", "ery")
_VERB_SUFFIXES = ("ize", "ise", "ate", "ify")


def _coarsen_ptb(tag: str) -> str:
    if tag.startswith("NN"):
        return "NOUN"
    # Attributive gerund/participle ("booking confirmation", "timed intercourse",
    # "recorded lesson") behave as noun-modifiers, not clause verbs. Tagging them
    # ADJ keeps real compounds intact while finite verbs (VB/VBP/VBZ/VBD) stay VERB.
    if tag in {"VBG", "VBN"}:
        return "ADJ"
    if tag.startswith("VB"):
        return "VERB"
    if tag.startswith("JJ"):
        return "ADJ"
    if tag.startswith("RB"):
        return "ADV"
    if tag in {"DT", "PDT", "WDT"}:
        return "DET"
    if tag == "IN":
        return "ADP"
    if tag == "CC":
        return "CONJ"
    if tag in {"PRP", "PRP$", "WP", "WP$"}:
        return "PRON"
    if tag == "CD":
        return "NUM"
    if tag == "MD":
        return "AUX"
    return "X"


def _heuristic_tag(word: str) -> str:
    w = word.lower()
    if w in FUNCTION_WORDS:
        if w in DETERMINERS:
            return "DET"
        if w in PREPOSITIONS:
            return "ADP"
        if w in CONJUNCTIONS:
            return "CONJ"
        if w in PRONOUNS:
            return "PRON"
        if w in AUX_VERBS:
            return "AUX"
        return "ADV"
    if w.isdigit():
        return "NUM"
    if w in ING_ED_NOUNS:
        return "NOUN"
    if w in FINITE_VERB_FORMS:
        return "VERB"
    if w in ACTION_VERBS or w in LEXICAL_VERBS:
        return "VERB"
    if w in STRONG_HEADS or w in STRONG_MODIFIERS or w in GENERIC_WEAK_HEADS:
        return "NOUN"
    if w.endswith(_NOUN_SUFFIXES):
        return "NOUN"
    if w.endswith("ly") and len(w) > 4:
        return "ADV"
    if w.endswith(_VERB_SUFFIXES) or w.endswith("ing") or w.endswith("ed"):
        return "VERB"
    return "NOUN"  # unknown content word -> noun (safe for NP chunking)


def tag_sentence(sent: str) -> List[Tuple[str, str]]:
    """Return [(token, coarse_tag)] using the best available tagger."""
    backend = get_active_backend()
    if backend == "spacy":
        nlp = _get_spacy()
        doc = nlp(sent)
        out: List[Tuple[str, str]] = []
        for tok in doc:
            if not tok.text.strip() or tok.is_punct or tok.is_space:
                continue
            out.append((tok.text.lower(), tok.pos_ if tok.pos_ != "PROPN" else "NOUN"))
        return out
    if backend == "nltk":
        try:
            import nltk  # type: ignore
            raw = nltk.pos_tag(nltk.word_tokenize(sent))
            out = []
            for w, t in raw:
                wl = w.lower()
                if not re.match(r"[a-z0-9]", wl):
                    continue
                if wl == "cannot":
                    out.extend([("can", "AUX"), ("not", "ADV")])
                else:
                    out.append((wl, _coarsen_ptb(t)))
            return out
        except Exception:
            pass
    return [(t, _heuristic_tag(t)) for t in tokenize(sent)]


# ---------------------------------------------------------------------------
# Boundary trimming
# ---------------------------------------------------------------------------
TRAILING_BAN: Set[str] = PREPOSITIONS | CONJUNCTIONS | DETERMINERS | {
    "and", "or", "to", "of", "the", "a", "an",
}
LEADING_BAN: Set[str] = FUNCTION_WORDS
STRIP_INTERIOR: Set[str] = {
    "the", "a", "an", "this", "that", "these", "those",
    "my", "your", "his", "her", "its", "our", "their",
}


def _is_adverb_ly(token: str) -> bool:
    return token.endswith("ly") and len(token) > 4 and token not in ING_ED_NOUNS


def _trim(tagged: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Strip leading/trailing function-word / adverb / non-action-verb tokens
    using BOTH the tag and the lexicon, so phrase begins/ends on content."""
    t = list(tagged)
    while t:
        w, tag = t[0]
        bad = (w in LEADING_BAN or _is_adverb_ly(w) or tag in {"DET", "ADP", "CONJ", "PRON", "AUX", "ADV"}
               or (tag == "VERB" and w not in ACTION_VERBS))
        if bad:
            t.pop(0)
        else:
            break
    while t:
        w, tag = t[-1]
        bad = (w in TRAILING_BAN or w in AUX_VERBS or _is_adverb_ly(w)
               or tag in {"DET", "ADP", "CONJ", "PRON", "AUX", "ADV"})
        if bad:
            t.pop()
        else:
            break
    return t


# ---------------------------------------------------------------------------
# Completeness — structural (uses real POS tags for interior verb detection)
# ---------------------------------------------------------------------------
def _is_noun_like_head(w: str, tag: str) -> bool:
    # Curated noun heads win over a tagger's false-VERB guess ("template",
    # "guide", "review" are often mistagged VERB out of context).
    if w in STRONG_HEADS or w in GENERIC_BUT_ALLOWED_HEADS or w in ING_ED_NOUNS:
        return True
    # A phrase must not END on a modifier-only word. "egg white cervical" is a
    # truncation of "...cervical mucus"; "cervical"/"hormonal"/"luteal" modify,
    # they don't head. (Words that are both modifier and head passed above.)
    if w in STRONG_MODIFIERS:
        return False
    if w in GENERIC_WEAK_HEADS:
        return True  # noun, but usefulness gate may still reject
    if tag == "VERB" and w not in ING_ED_NOUNS:
        return False
    if tag in {"ADV", "ADP", "CONJ", "PRON", "DET", "AUX"}:
        return False
    if w in FINITE_VERB_FORMS or w in LEXICAL_VERBS:
        return False
    if w.endswith("ed") and w not in ING_ED_NOUNS:
        return False
    return tag in {"NOUN", "NUM", "ADJ"} or True


def _is_complete(tagged: List[Tuple[str, str]]) -> bool:
    words = [w for w, _ in tagged]
    tags = [t for _, t in tagged]
    if not (2 <= len(tagged) <= 6):
        return False
    if words[0] in LEADING_BAN or words[-1] in TRAILING_BAN:
        return False
    if not _is_noun_like_head(words[-1], tags[-1]):
        return False
    if any(t == "AUX" or w in AUX_VERBS for w, t in tagged):
        return False
    if any(t == "PRON" or w in PRONOUNS for w, t in tagged):
        return False
    # LEXICON BACKSTOP: a real verb anywhere signals a glued clause even if the
    # tagger mislabelled it. BUT many words are noun-or-verb ("plan", "score",
    # "review"); for those we trust the tagger when it says NOUN/ADJ. We only
    # override the tagger for verb-ONLY words it fumbled ("deserves", "pay",
    # "lead"). This is what catches "perimenopause deserves" / "target pay
    # attention" while keeping "study plan template".
    # tokens that participate in a curated ordered pair are compound members
    # ("study plan", "internal linking") and must not be read as clause verbs,
    # whatever the tagger guessed.
    pair_idx: Set[int] = set()
    for i in range(len(words) - 1):
        if (words[i], words[i + 1]) in VALID_ORDERED_PAIRS:
            pair_idx.add(i)
            pair_idx.add(i + 1)
    noun_capable = (STRONG_HEADS | STRONG_MODIFIERS | GENERIC_BUT_ALLOWED_HEADS
                    | GENERIC_WEAK_HEADS | ING_ED_NOUNS)
    for idx, (w, t) in enumerate(tagged):
        gerundish = w in GERUND_FORMS or w in ING_ED_NOUNS
        verbish = (w in LEXICAL_VERBS or w in FINITE_VERB_FORMS) and not gerundish
        if not verbish:
            continue
        if idx == 0 and w in ACTION_VERBS:
            continue
        if idx in pair_idx:
            continue
        if w in noun_capable and t in {"NOUN", "ADJ", "NUM"}:
            continue  # tagger says noun and the word can be one -> trust tagger
        return False
    # interior verb (per POS) => glued clause; the head is validated separately,
    # so scan true interior only, and trust noun-capable / compound tokens.
    for idx, (w, t) in enumerate(tagged[1:-1], start=1):
        if (t == "VERB" and w not in GERUND_FORMS and w not in ING_ED_NOUNS
                and w not in noun_capable and idx not in pair_idx):
            return False
    # leading verb tag => clause start, UNLESS the tagger is wrong about a word
    # that starts a known compound ("study plan", "track record")
    if tags[0] == "VERB" and words[0] not in ACTION_VERBS:
        pair_ok = len(words) >= 2 and (words[0], words[1]) in VALID_ORDERED_PAIRS
        if not (pair_ok or is_exact_canonical_anchor(words) or contains_canonical_anchor(words)):
            return False
    # interior determiner / conjunction / non-'of' preposition => fragment
    interior = tagged[1:-1]
    if any(w in STRIP_INTERIOR for w, _ in interior):
        return False
    if any((t == "CONJ" or w in CONJUNCTIONS) for w, t in interior):
        return False
    if any((t == "ADP" or w in PREPOSITIONS) and w != "of" for w, t in interior):
        return False
    content = [w for w, t in tagged if w not in FUNCTION_WORDS]
    if len(content) < 2:
        return False
    if all(w in GENERIC_WEAK_HEADS or w in FUNCTION_WORDS for w in words):
        return False
    return True


# ---------------------------------------------------------------------------
# Usefulness — the new gate. Structural-complete != useful anchor.
# ---------------------------------------------------------------------------
def _is_useful(tagged: List[Tuple[str, str]]) -> Tuple[bool, str]:
    words = [w for w, _ in tagged]
    head = words[-1]
    mods = words[:-1]
    content = [w for w in words if w not in FUNCTION_WORDS]

    # Universal weak standalone noun-phrase rejection.
    weak_head = head in GENERIC_WEAK_HEADS or head in EXTRA_WEAK_GENERIC_HEADS
    protected = (
        is_exact_canonical_anchor(words)
        or has_valid_ordered_pair(words)
        or bool(contains_canonical_anchor(words))
    )

    if not protected:
        if weak_head:
            return False, "weak_generic_head"
        if len(words) == 2 and words[0] in WEAK_NON_ANCHOR_MODIFIERS:
            return False, "weak_standalone_noun_phrase"

    # Reject narrative fragments that are grammatically plausible but poor anchors.
    if not protected:
        narrative_hits = sum(1 for w in words if w in NARRATIVE_FRAGMENT_WORDS)
        if narrative_hits >= 2:
            return False, "narrative_fragment_phrase"
        if len(words) <= 3 and narrative_hits >= 1 and head not in STRONG_HEADS:
            return False, "weak_narrative_short_phrase"

    # 1. known compound / canonical anchor -> always good
    if is_exact_canonical_anchor(words) or has_valid_ordered_pair(words) or contains_canonical_anchor(words):
        return True, "known_compound"

    # 2. action verb + strong object head -> action anchor
    if words[0] in ACTION_VERBS:
        if head in STRONG_HEADS or head in GENERIC_BUT_ALLOWED_HEADS:
            return True, "action_strong_object"
        return False, "action_weak_object"

    # 3. strong concept head + >=1 real modifier
    if head in STRONG_HEADS:
        if any(m in STRONG_MODIFIERS for m in mods) or any(len(m) >= 5 for m in mods) or len(content) >= 3:
            return True, "strong_head_qualified"
        return True, "strong_head"  # e.g. "ovulation calculator"

    # 4. bare generic/weak head -> reject unless qualified into a compound
    if head in GENERIC_WEAK_HEADS:
        return False, "weak_generic_head"

    # 5. generic-but-allowed head needs a strong modifier
    if head in GENERIC_BUT_ALLOWED_HEADS:
        if any(m in STRONG_MODIFIERS for m in mods) or any(len(m) >= 6 for m in mods):
            return True, "allowed_head_qualified"
        return False, "allowed_head_unqualified"

    # 6. unknown head -> require genuine specificity to generalise to thin niches
    long_content = [w for w in content if len(w) >= 6]
    known_mod = any(m in STRONG_MODIFIERS for m in mods)
    if len(content) >= 2 and (len(long_content) >= 1 or known_mod or len(content) >= 3):
        return True, "specific_unknown_head"

    return False, "insufficient_specificity"


# ---------------------------------------------------------------------------
# Scoring — computed ONCE here, carried downstream
# ---------------------------------------------------------------------------
SOURCE_WEIGHT: Dict[str, float] = {
    "title": 0.20, "heading_h1": 0.18, "heading_h2": 0.16, "heading_h3": 0.14,
    "heading_h4": 0.12, "heading_h5": 0.12, "heading_h6": 0.12,
    "list_item": 0.08, "intent": 0.12, "action_object": 0.10, "noun_phrase": 0.10,
}


def _score(words: List[str], source_type: str, useful_reason: str) -> Dict[str, Any]:
    content = [w for w in words if w not in FUNCTION_WORDS]
    n = max(1, len(content))
    head = words[-1]
    if useful_reason in {"known_compound"}:
        headed = 1.0
    elif head in STRONG_HEADS:
        headed = 0.9
    elif head in GENERIC_BUT_ALLOWED_HEADS:
        headed = 0.55
    else:
        headed = 0.6
    strong = sum(1 for w in content if w in STRONG_HEADS or w in STRONG_MODIFIERS or len(w) >= 6)
    density = strong / n
    has_mod = any(w in STRONG_MODIFIERS for w in words[:-1]) or any(len(w) >= 5 for w in words[:-1])
    specificity = 0.7 if has_mod else 0.35
    length = 1.0 if 2 <= len(content) <= 4 else 0.6
    score = (0.30 * headed + 0.24 * density + 0.18 * specificity
             + 0.14 * length + SOURCE_WEIGHT.get(source_type, 0.08))
    score = max(0.0, min(1.0, round(score, 4)))
    return {
        "score": score,
        "decision": "ACCEPT",
        "backend": get_active_backend(),
        "useful_reason": useful_reason,
        "signals": {"headedness": round(headed, 3), "entity_density": round(density, 3),
                    "specificity": round(specificity, 3), "length": round(length, 3)},
    }


# ---------------------------------------------------------------------------
# Chunking -> complete constituents
# ---------------------------------------------------------------------------
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")
_CLAUSE_SPLIT_RE = re.compile(r"[,;:()\u2013\u2014\u2022]| - ")
TAG_RE = re.compile(r"<[^>]+>")
H_RE = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
LI_RE = re.compile(r"<li[^>]*>(.*?)</li>", re.IGNORECASE | re.DOTALL)
P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.IGNORECASE | re.DOTALL)
_NP_TAGS = {"NOUN", "ADJ", "NUM", "PROPN"}


def _strip_tags(text: str) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", text or "")).strip()


def _split_sentences(text: str) -> List[str]:
    text = (text or "").strip()
    return [s.strip() for s in _SENTENCE_SPLIT_RE.split(text) if s and s.strip()] if text else []


def _np_chunks(tagged: List[Tuple[str, str]]) -> List[List[Tuple[str, str]]]:
    out: List[List[Tuple[str, str]]] = []
    i, n = 0, len(tagged)
    while i < n:
        if tagged[i][1] not in _NP_TAGS:
            i += 1
            continue
        j = i
        while j < n:
            w, t = tagged[j]
            if t in _NP_TAGS:
                j += 1
                continue
            if w == "of" and j + 1 < n and tagged[j + 1][1] in _NP_TAGS:
                j += 2
                continue
            break
        chunk = tagged[i:j]
        # head-anchored suffixes (every variant ends on the same head)
        for start in range(0, max(1, len(chunk) - 1)):
            out.append(chunk[start:])
        i = j
    return out



ANCHOR_ACTION_VERBS = {
    "calculate", "track", "estimate", "check", "compare", "choose",
    "find", "identify", "select", "review", "audit", "analyze",
    "monitor", "test", "rank", "score", "generate", "convert",
    "schedule", "plan"
}


def _is_anchor_action_candidate(words: List[str]) -> bool:
    """
    Universal action-anchor gate.

    Allows search/link-intent action phrases:
    - calculate ovulation
    - estimate due date
    - compare pricing plans
    - track keyword rankings

    Rejects ordinary sentence predicates:
    - control expenses
    - forecast revenue
    - improve internal linking strategy
    - students prepare
    """
    if not words or len(words) < 2:
        return False

    verb = words[0]
    obj = words[1:]
    head = words[-1]

    if verb not in ANCHOR_ACTION_VERBS:
        return False

    # Object must be concept-like, not just a generic noun.
    has_known_anchor = (
        is_exact_canonical_anchor(obj)
        or has_valid_ordered_pair(obj)
        or bool(contains_canonical_anchor(obj))
    )

    if has_known_anchor:
        return True

    has_strong_head = head in STRONG_HEADS or head in GENERIC_BUT_ALLOWED_HEADS
    has_specific_object = any(
        len(w) >= 6 or w in STRONG_HEADS or w in STRONG_MODIFIERS
        for w in obj
    )

    return bool(has_strong_head and has_specific_object)


def _action_chunks(tagged: List[Tuple[str, str]]) -> List[List[Tuple[str, str]]]:
    out: List[List[Tuple[str, str]]] = []
    for k, (w, t) in enumerate(tagged):
        if w in ACTION_VERBS:
            obj: List[Tuple[str, str]] = []
            for wj, tj in tagged[k + 1:k + 5]:
                if tj in {"DET"} and not obj:
                    continue
                if tj in {"ADP", "CONJ", "AUX", "PRON"} or wj in PREPOSITIONS | CONJUNCTIONS | AUX_VERBS | PRONOUNS:
                    break
                obj.append((wj, tj))
                if len(obj) >= 3:
                    break
            if obj:
                candidate_words = [w] + [x for x, _ in obj]
                if _is_anchor_action_candidate(candidate_words):
                    out.append([(w, t)] + obj)
    return out


def _candidates(sent: str) -> List[Tuple[List[str], str]]:
    """Return [(words, source_type)] of complete+useful candidates for one sentence."""
    results: List[Tuple[List[str], str]] = []
    seen: Set[str] = set()
    for seg in _CLAUSE_SPLIT_RE.split(sent):
        tagged = tag_sentence(seg)
        if not tagged:
            continue
        chunks = _np_chunks(tagged) + _action_chunks(tagged)
        for chunk in chunks:
            trimmed = _trim(chunk)
            if len(trimmed) > 2:  # drop interior determiners
                trimmed = [trimmed[0]] + [(w, t) for w, t in trimmed[1:-1]
                                          if w not in STRIP_INTERIOR] + [trimmed[-1]]
                trimmed = _trim(trimmed)
            if not _is_complete(trimmed):
                continue
            useful, reason = _is_useful(trimmed)
            if not useful:
                continue
            words = [w for w, _ in trimmed]
            key = " ".join(words)
            if key in seen:
                continue
            seen.add(key)
            st = ("action_object" if words[0] in ACTION_VERBS else "noun_phrase")
            results.append((words, st))
    return results



def _is_contiguous_subsequence(short: List[str], long: List[str]) -> bool:
    if not short or not long or len(short) >= len(long):
        return False
    n = len(short)
    return any(long[i:i+n] == short for i in range(0, len(long) - n + 1))


def _suppress_shorter_variants(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Universal variant suppression.

    Keeps the more specific phrase when a shorter phrase is contained inside
    a longer phrase with the same head.

    Example:
    - remove: research tools
    - keep:   keyword research tools

    Preserves exact canonical anchors such as "cervical mucus" when they are
    intentionally valuable standalone anchors.
    """
    parsed = []
    for i, row in enumerate(rows):
        phrase = str(row.get("phrase") or "")
        toks = tokenize(phrase)
        if not toks:
            continue
        parsed.append((i, phrase, toks, row))

    suppress = set()

    for i, short_phrase, short_toks, short_row in parsed:
        if len(short_toks) < 2:
            continue

        # Preserve known standalone canonical anchors.
        if is_exact_canonical_anchor(short_toks):
            continue

        for j, long_phrase, long_toks, long_row in parsed:
            if i == j:
                continue
            if len(long_toks) <= len(short_toks):
                continue
            if len(long_toks) - len(short_toks) > 4:
                continue

            # Same head means shorter is probably a less-specific variant.
            if short_toks[-1] != long_toks[-1]:
                continue

            if _is_contiguous_subsequence(short_toks, long_toks):
                suppress.add(i)
                break

    return [
        row
        for i, row in enumerate(rows)
        if i not in suppress
    ]



# ---------------------------------------------------------------------------
# Backward-compatible helpers used by upload_phrase_selector.py
# ---------------------------------------------------------------------------

def strip_tags(text: str) -> str:
    return _strip_tags(text)


def split_sentences(text: str) -> List[str]:
    return _split_sentences(text)


def extract_paragraphs(html: str = "", text: str = "") -> List[str]:
    paras = [_strip_tags(x) for x in P_RE.findall(html or "")]
    paras = [p for p in paras if p]
    if paras:
        return paras

    raw = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    return [x.strip() for x in re.split(r"\n\s*\n+", raw) if x.strip()] or ([text] if text else [])


def extract_headings_and_lists(html: str = "") -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    for lvl, inner in H_RE.findall(html or ""):
        txt = _strip_tags(inner)
        if txt:
            out.append({
                "phrase": canonical_phrase(txt),
                "source_type": f"heading_h{int(lvl)}",
                "section_id": f"heading_h{int(lvl)}_{len(out)}",
                "snippet": txt,
            })

    for idx, li in enumerate(LI_RE.findall(html or "")):
        txt = _strip_tags(li)
        if txt:
            out.append({
                "phrase": canonical_phrase(txt),
                "source_type": "list_item",
                "section_id": f"list_item_{idx}",
                "snippet": txt,
            })

    return out


# ---------------------------------------------------------------------------
# Public API (signature + output shape unchanged)
# ---------------------------------------------------------------------------
def extract_smart_phrases(
    *, text: str = "", html: str = "", title: str = "", doc_id: str = "",
    max_candidates: int = 500, workspace_id: str = "default", vertical: str = "general",
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    def add(words: List[str], source_type: str, section_id: str, snippet: str) -> None:
        useful, reason = _is_useful([(w, "NOUN") for w in words]) if words else (False, "")
        # words already passed full gate in _candidates; for title/heading paths
        # we re-tag below, so this is only the structural-string add.
        phrase = " ".join(words)
        key = f"{source_type}:{phrase}:{section_id}"
        if not phrase or key in seen:
            return
        seen.add(key)
        out.append({
            "phrase": phrase, "source_type": source_type, "section_id": section_id,
            "doc_id": doc_id, "snippet": snippet[:240],
            "extractor_intelligence": _score(words, source_type, reason),
        })

    def add_from_text(raw: str, source_type: str, section_id: str) -> None:
        for sent in _split_sentences(raw):
            for words, st in _candidates(sent):
                final_st = source_type if source_type in {"title"} or source_type.startswith("heading") or source_type == "list_item" else st
                useful, reason = _is_useful([(w, "NOUN") for w in words])
                tagged_final = tag_sentence(" ".join(words))
                trimmed_final = _trim(tagged_final)
                if len(trimmed_final) > 2:
                    trimmed_final = [trimmed_final[0]] + [
                        (w, t) for w, t in trimmed_final[1:-1]
                        if w not in STRIP_INTERIOR
                    ] + [trimmed_final[-1]]
                    trimmed_final = _trim(trimmed_final)

                if not _is_complete(trimmed_final):
                    continue

                useful_final, reason = _is_useful(trimmed_final)
                if not useful_final:
                    continue

                words = [w for w, _ in trimmed_final]
                phrase = " ".join(words)
                key = f"{final_st}:{phrase}:{section_id}"
                if not phrase or key in seen:
                    continue
                seen.add(key)
                out.append({
                    "phrase": phrase, "source_type": final_st, "section_id": section_id,
                    "doc_id": doc_id, "snippet": sent[:240],
                    "extractor_intelligence": _score(words, final_st, reason),
                })
                if len(out) >= max_candidates:
                    return

    if title:
        add_from_text(title, "title", "title_0")

    for lvl, inner in H_RE.findall(html or ""):
        if len(out) >= max_candidates:
            return _suppress_shorter_variants(out)[:max_candidates]
        add_from_text(_strip_tags(inner), f"heading_h{int(lvl)}", f"heading_h{int(lvl)}_{len(out)}")
    for idx, li in enumerate(LI_RE.findall(html or "")):
        if len(out) >= max_candidates:
            return _suppress_shorter_variants(out)[:max_candidates]
        add_from_text(_strip_tags(li), "list_item", f"list_item_{idx}")

    paras = [_strip_tags(x) for x in P_RE.findall(html or "")]
    paras = [p for p in paras if p]
    if not paras:
        raw = (text or "").replace("\r\n", "\n")
        paras = [x.strip() for x in re.split(r"\n\s*\n+", raw) if x.strip()] or ([text] if text else [])
    for pi, para in enumerate(paras):
        for si, sent in enumerate(_split_sentences(para)):
            if len(out) >= max_candidates:
                return _suppress_shorter_variants(out)[:max_candidates]
            add_from_text(sent, "noun_phrase", f"p{pi}_s{si}")

    return _suppress_shorter_variants(out)[:max_candidates]