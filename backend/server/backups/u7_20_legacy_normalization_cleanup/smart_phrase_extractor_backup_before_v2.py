"""
Smart phrase extractor (rewritten).

Goal: produce *complete* anchor phrases — phrases that read as a whole noun
phrase or intent and never hang on a dangling article, preposition, or
conjunction, and are never cut mid-constituent.

Why the previous version produced "hanging" phrases
---------------------------------------------------
The old extractor slid fixed 2/3/4-word windows across a token stream and then
tried to *reject* the bad ones with several hundred hand-written blocklists and
regexes. Sliding windows inherently slice through the middle of grammatical
constituents, so "calculate the fertile window" becomes "calculate the",
"the fertile", "fertile window", etc. The blocklists can never enumerate every
truncation, so fragments leak through.

This version flips the approach: instead of cutting arbitrary windows and
filtering, it (1) chunks each sentence into whole noun-phrase / verb-object
constituents, then (2) trims both ends down to content-word boundaries and
rejects anything that still starts or ends on a function word. A phrase is kept
only if it begins and ends on a content word and ends on a noun-like head. That
single structural rule removes essentially all "hanging" output.

It prefers spaCy or NLTK if installed (best accuracy) and otherwise falls back
to a self-contained heuristic chunker, so it has **no required dependencies**.

The public function `extract_smart_phrases(...)` keeps the same signature and
output shape as before, so this is a drop-in replacement.
"""

from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Optional, soft dependencies. Everything degrades gracefully.
# ---------------------------------------------------------------------------

try:  # learning hook — optional
    from backend.server.stores.dis_pipeline_learning import (  # type: ignore
        learn_from_pipeline_rejection,
    )
except Exception:  # pragma: no cover - fallback when running standalone
    def learn_from_pipeline_rejection(**_kwargs: Any) -> None:
        return None

try:  # extra domain vocabulary — optional
    from backend.server.stores.universal_noun_families import (  # type: ignore
        get_all_universal_nouns,
        get_all_universal_modifiers,
    )
except Exception:
    def get_all_universal_nouns() -> Set[str]:
        return set()

    def get_all_universal_modifiers() -> Set[str]:
        return set()


# spaCy / NLTK are auto-detected once, lazily.
_SPACY_NLP = None
_SPACY_TRIED = False
_NLTK_OK: Optional[bool] = None


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

        # Probe so we fail fast if NLTK data is not downloaded.
        nltk.pos_tag(nltk.word_tokenize("test sentence"))
        _NLTK_OK = True
    except Exception:
        _NLTK_OK = False

    return _NLTK_OK


# ---------------------------------------------------------------------------
# Lexical resources
# ---------------------------------------------------------------------------

WORD_RE = re.compile(r"[a-z0-9][a-z0-9'-]*", re.I)
TAG_RE = re.compile(r"<[^>]+>")
H_RE = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
LI_RE = re.compile(r"<li[^>]*>(.*?)</li>", re.IGNORECASE | re.DOTALL)
P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.IGNORECASE | re.DOTALL)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")

DETERMINERS: Set[str] = {
    "a", "an", "the", "this", "that", "these", "those", "my", "your", "his",
    "her", "its", "our", "their", "some", "any", "each", "every", "no",
    "another", "such", "much", "many", "more", "most", "all", "both", "either",
    "neither", "which", "what", "whose",
}

PREPOSITIONS: Set[str] = {
    "about", "above", "across", "after", "against", "along", "among", "around",
    "as", "at", "before", "behind", "below", "beneath", "beside", "between",
    "beyond", "by", "down", "during", "except", "for", "from", "in", "inside",
    "into", "near", "of", "off", "on", "onto", "out", "outside", "over", "per",
    "since", "than", "through", "throughout", "to", "toward", "towards",
    "under", "until", "up", "upon", "via", "with", "within", "without", "like",
}

CONJUNCTIONS: Set[str] = {
    "and", "or", "but", "nor", "so", "yet", "because", "although", "though",
    "while", "whereas", "unless", "until", "whether", "if", "then",
}

PRONOUNS: Set[str] = {
    "i", "me", "my", "mine", "myself", "you", "yours", "yourself", "he", "him",
    "his", "she", "her", "hers", "we", "us", "our", "ours", "they", "them",
    "their", "theirs", "it", "its", "itself", "who", "whom", "whose", "anyone",
    "someone", "everyone", "everybody", "somebody", "anybody", "nobody",
    "something", "anything", "everything", "nothing", "one", "ones",
}

AUX_VERBS: Set[str] = {
    "is", "are", "was", "were", "be", "being", "been", "am", "can", "could",
    "will", "would", "shall", "should", "may", "might", "must", "has", "have",
    "had", "do", "does", "did", "ought",
}

PARTICLES_DEGREE: Set[str] = {
    "not", "very", "too", "also", "just", "only", "even", "still", "quite",
    "rather", "really", "almost", "always", "never", "often", "sometimes",
    "usually", "generally", "typically", "currently", "recently", "soon",
    "later", "now", "today", "tomorrow", "yesterday", "here", "there",
    "however", "therefore", "meanwhile", "instead", "anyway", "actually",
    "basically", "simply", "clearly", "finally", "first", "firstly",
    "second", "secondly", "lastly", "overall", "especially", "particularly",
}

# Function words = closed-class words that should never start/end a phrase.
FUNCTION_WORDS: Set[str] = (
    DETERMINERS | PREPOSITIONS | CONJUNCTIONS | PRONOUNS | AUX_VERBS | PARTICLES_DEGREE
)

# A few -ly words that are actually nouns, so the adverb heuristic skips them.
LY_NOUN_EXCEPTIONS: Set[str] = {
    "family", "supply", "assembly", "anomaly", "ally", "rally", "monopoly",
    "italy", "july", "belly", "jelly", "reply", "apply", "supply",
}


def _is_adverb_ly(token: str) -> bool:
    return token.endswith("ly") and len(token) > 4 and token not in LY_NOUN_EXCEPTIONS


# Comparative / degree adverbs that should never be a phrase head or tail.
COMPARATIVES: Set[str] = {
    "faster", "slower", "better", "worse", "easier", "harder", "longer",
    "shorter", "higher", "lower", "bigger", "smaller", "greater", "sooner",
    "later", "more", "less", "fewer", "older", "newer", "cheaper", "stronger",
    "weaker", "wider", "deeper", "closer", "further", "farther", "best",
    "worst", "fastest", "slowest", "highest", "lowest", "largest", "smallest",
}

# Words that may NOT end a phrase (cause "hanging" tails).
TRAILING_BAN: Set[str] = PREPOSITIONS | CONJUNCTIONS | DETERMINERS | COMPARATIVES | {
    "and", "or", "to", "of", "the", "a", "an",
}

# Words that may NOT start a phrase.
LEADING_BAN: Set[str] = FUNCTION_WORDS


def _verb_forms(lemmas: Set[str]) -> Set[str]:
    """Expand verb lemmas to their common inflected forms (-s/-es/-ed/-ing)."""
    forms: Set[str] = set()
    for v in lemmas:
        forms.add(v)
        forms.update({v + "s", v + "es", v + "ed", v + "ing"})
        if v.endswith("e"):
            forms.update({v[:-1] + "es", v[:-1] + "ed", v[:-1] + "ing"})
        if v.endswith("y"):
            forms.add(v[:-1] + "ies")
    return forms


# Lexical verbs we treat as clause signals (a phrase containing one mid-stream
# is usually a sentence fragment, not a noun phrase). Kept deliberately small;
# the chunker handles the rest structurally.
COMMON_LEXICAL_VERBS: Set[str] = {
    "runs", "run", "falls", "fall", "lands", "land", "becomes", "become",
    "means", "mean", "depends", "depend", "explains", "explain", "turns",
    "turn", "makes", "make", "shows", "show", "happens", "happen", "rises",
    "rise", "stays", "stay", "offers", "offer", "works", "work", "holds",
    "hold", "starts", "start", "ends", "end", "uses", "use", "gives", "give",
    "gets", "get", "goes", "go", "comes", "come", "takes", "take", "needs",
    "need", "wants", "want", "knows", "know", "says", "say", "tells", "tell",
    "grows", "grow", "affects", "affect", "changes", "change",
    "watch", "look", "see", "let", "keep", "try", "learn", "read", "note",
    "avoid", "consider", "remember", "ensure", "pick", "set", "add", "put",
    "ask", "tell", "call", "send", "give", "show", "let", "follow", "apply",
    "enter", "click", "tap", "visit", "open", "close", "save", "share",
}

# Verbs that head an action/intent anchor ("calculate due date").
ACTION_VERBS: Set[str] = {
    "calculate", "track", "confirm", "compare", "choose", "check", "measure",
    "estimate", "build", "create", "fix", "improve", "optimize", "reduce",
    "increase", "manage", "treat", "prevent", "diagnose", "review", "audit",
    "forecast", "plan", "write", "design", "analyze", "monitor", "test",
    "rank", "score", "publish", "import", "export", "sync", "validate",
    "protect", "find", "convert", "identify", "select", "schedule", "generate",
}

# All inflected forms of every verb we know about -> reliable verb detection
# in the heuristic tagger (catches "improves", "falls", "uses", "helps"...).
VERB_FORMS: Set[str] = _verb_forms(ACTION_VERBS | COMMON_LEXICAL_VERBS | {
    "help", "allow", "provide", "support", "include", "require", "reveal",
    "publish", "contain", "mention", "combine", "understand", "request",
    "invite", "connect", "complete", "summarize", "interpret", "guide",
    "depend", "explain", "unlock", "confuse", "pass", "lean",
})

# Gerund (-ing) forms frequently act as noun modifiers ("tracking guide",
# "marketing strategy"), so they are allowed inside a noun phrase. Finite and
# past-participle forms ("improves", "improved") are clause signals.
GERUND_FORMS: Set[str] = {v for v in VERB_FORMS if v.endswith("ing")}
FINITE_VERB_FORMS: Set[str] = VERB_FORMS - GERUND_FORMS

# Interior determiners/possessives are safe to drop from an anchor.
STRIP_INTERIOR: Set[str] = {
    "the", "a", "an", "this", "that", "these", "those",
    "my", "your", "his", "her", "its", "our", "their",
}

INTENT_STARTS: Tuple[str, ...] = (
    "how to", "how many", "what is", "what are", "when to", "when do",
    "best way to", "best time to", "signs of", "symptoms of", "causes of",
    "treatment for", "guide to", "tips for", "ways to",
)

# Generic heads that are too weak to stand alone unless well qualified.
GENERIC_WEAK_HEADS: Set[str] = {
    "thing", "things", "stuff", "way", "ways", "part", "parts", "case",
    "cases", "point", "points", "area", "areas", "level", "type", "types",
    "form", "forms", "kind", "kinds", "sort", "sorts", "lot", "bit",
}

# Strong content heads (domain vocab can extend these via the optional import).
UNIVERSAL_HEADS: Set[str] = {
    "software", "tool", "tools", "platform", "system", "strategy", "workflow",
    "automation", "integration", "pipeline", "dashboard", "api", "app",
    "application", "plugin", "extension", "database", "storage", "security",
    "keyword", "keywords", "content", "backlink", "audit", "optimization",
    "conversion", "page", "traffic", "ranking", "analytics", "rate", "rates",
    "forecast", "tax", "investment", "lease", "agreement", "contract",
    "review", "property", "mortgage", "insurance", "calculator", "checklist",
    "service", "services", "pricing", "policy", "menu", "reservation",
    "restaurant", "hotel", "rental", "product", "customer", "study",
    "management", "project", "resume", "interview", "course", "lesson",
    "training", "symptoms", "causes", "treatment", "medication", "dosage",
    "therapy", "performance", "settings", "guide", "benefits", "estimate",
    "schedule", "routine", "report", "analysis", "assessment", "plan",
    "budget", "template", "framework", "model", "engine", "module", "feature",
    "features", "component", "source", "topic", "topics", "cluster", "score",
    "window", "cycle", "length", "date", "checkout", "subscription",
} | set(get_all_universal_nouns())

UNIVERSAL_MODIFIERS: Set[str] = {
    "pricing", "landing", "checkout", "subscription", "onboarding",
    "management", "marketing", "analytics", "email", "project", "technical",
    "conversion", "setup", "customer", "saas", "enterprise", "security",
    "billing", "internal", "external", "keyword", "content", "product",
    "support", "usage", "search", "brand", "branded", "trial", "demo",
} | set(get_all_universal_modifiers())


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

def canonical_phrase(text: str) -> str:
    s = (text or "").strip().lower()
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    # strip leading list markers / numbering
    s = re.sub(r"^\s*(?:\d+[.)]\s+|[\u2022\u2013\u2014\-]\s+)", "", s)
    # strip wrapping punctuation
    s = re.sub(r"^[\"'(\[{]+|[\"')\]}:;,.!?]+$", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def strip_tags(text: str) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", text or "")).strip()


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]


def split_sentences(text: str) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    return [s.strip() for s in SENTENCE_SPLIT_RE.split(text) if s and s.strip()]


def extract_paragraphs(html: str = "", text: str = "") -> List[str]:
    paras = [strip_tags(x) for x in P_RE.findall(html or "")]
    paras = [p for p in paras if p]
    if paras:
        return paras
    raw = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    return [x.strip() for x in re.split(r"\n\s*\n+", raw) if x.strip()]


def extract_headings_and_lists(html: str = "") -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for lvl, inner in H_RE.findall(html or ""):
        txt = strip_tags(inner)
        if not txt:
            continue
        source_type = f"heading_h{int(lvl)}"
        out.append({
            "phrase": canonical_phrase(txt),
            "source_type": source_type,
            "section_id": f"{source_type}_{len(out)}",
            "snippet": txt,
        })
    for li in [strip_tags(x) for x in LI_RE.findall(html or "")]:
        if li:
            out.append({
                "phrase": canonical_phrase(li),
                "source_type": "list_item",
                "section_id": f"list_item_{len(out)}",
                "snippet": li,
            })
    return out


# ---------------------------------------------------------------------------
# POS tagging (spaCy -> NLTK -> heuristic)
# ---------------------------------------------------------------------------

# Heuristic suffixes that strongly suggest a noun.
_NOUN_SUFFIXES = ("tion", "sion", "ment", "ness", "ity", "ship", "ance",
                  "ence", "ics", "ism", "age", "ure", "or", "er", "ist", "ery")
# Suffixes that suggest a (lexical) verb when not in the noun exception set.
_VERB_SUFFIXES = ("ize", "ise", "ate", "ify", "ed", "ing")
# Common -ing / -ed words that are actually nouns/adjectives.
_ING_ED_NOUNS = {
    "marketing", "branding", "onboarding", "training", "ranking", "rankings",
    "pricing", "billing", "listing", "listings", "meeting", "meetings",
    "setting", "settings", "building", "buildings", "reporting", "advertising",
    "engineering", "accounting", "funding", "spending", "earnings", "savings",
    "advanced", "automated", "integrated", "detailed", "dedicated", "related",
    "recommended", "estimated", "extended",
}


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
    if w in FINITE_VERB_FORMS and w not in _ING_ED_NOUNS:
        return "VERB"
    if w in ACTION_VERBS or w in COMMON_LEXICAL_VERBS:
        return "VERB"
    if w in UNIVERSAL_HEADS or w in UNIVERSAL_MODIFIERS or w in GENERIC_WEAK_HEADS:
        return "NOUN"
    if w in _ING_ED_NOUNS:
        return "NOUN"
    if w.endswith(_NOUN_SUFFIXES):
        return "NOUN"
    if w.endswith("ly") and len(w) > 4:
        return "ADV"
    if w.endswith(_VERB_SUFFIXES):
        return "VERB"
    # default: treat unknown content words as nouns (safer for NP chunking)
    return "NOUN"


def pos_tag(tokens: List[str]) -> List[Tuple[str, str]]:
    """Return [(token, coarse_tag), ...] using the best available tagger."""
    if not tokens:
        return []
    if _have_nltk():
        try:
            import nltk  # type: ignore
            raw = nltk.pos_tag(tokens)
            return [(w, _coarsen_ptb(t)) for w, t in raw]
        except Exception:
            pass
    return [(t, _heuristic_tag(t)) for t in tokens]


def _coarsen_ptb(tag: str) -> str:
    if tag.startswith("NN"):
        return "NOUN"
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


# ---------------------------------------------------------------------------
# Boundary trimming — the core "no hanging phrases" logic
# ---------------------------------------------------------------------------

def _trim_boundaries(tokens: List[str]) -> List[str]:
    """Strip leading/trailing function words so the phrase begins and ends on
    a content word. This is what removes 'hanging' phrases."""
    toks = list(tokens)
    while toks and ((toks[0] in LEADING_BAN or _is_adverb_ly(toks[0]))
                    or (toks[0] in COMMON_LEXICAL_VERBS
                        and toks[0] not in ACTION_VERBS)):
        toks.pop(0)
    while toks and (toks[-1] in TRAILING_BAN or toks[-1] in AUX_VERBS
                    or toks[-1] in PARTICLES_DEGREE or _is_adverb_ly(toks[-1])):
        toks.pop()
    return toks


def _is_noun_like_head(token: str) -> bool:
    if token in COMPARATIVES or _is_adverb_ly(token):
        return False
    if token in _ING_ED_NOUNS:
        return True
    if token in UNIVERSAL_HEADS:
        return True
    if token in FINITE_VERB_FORMS:
        return False
    if token in GENERIC_WEAK_HEADS:
        return True  # weak but still a noun; quality filter handles it
    if token in COMMON_LEXICAL_VERBS:
        return False
    if token in AUX_VERBS or token in PREPOSITIONS or token in CONJUNCTIONS:
        return False
    if token in PRONOUNS or token in DETERMINERS:
        return False
    # past participle head is usually a clause fragment ("rate improved");
    # gerund head is usually nominal ("cycle tracking") and allowed.
    if token.endswith("ed") and token not in _ING_ED_NOUNS:
        return False
    return True


def _is_complete_phrase(tokens: List[str]) -> bool:
    """A phrase is complete iff it is a clean constituent:
    - 2..6 tokens, >=2 content words
    - starts and ends on a content word
    - ends on a noun-like head (no dangling preposition/verb/article)
    - contains no finite clause verb / auxiliary / pronoun in the interior
    - not purely generic filler
    """
    if not (2 <= len(tokens) <= 6):
        return False
    if tokens[0] in LEADING_BAN or tokens[-1] in TRAILING_BAN:
        return False
    if not _is_noun_like_head(tokens[-1]):
        return False
    if any(t in AUX_VERBS for t in tokens):
        return False
    if any(t in PRONOUNS for t in tokens):
        return False
    # a finite verb in the true interior, or a non-action finite verb in front,
    # signals a glued-together clause. (Gerund modifiers and noun/verb-ambiguous
    # heads like "guide" / "review" are handled by head + boundary checks.)
    if tokens[0] in FINITE_VERB_FORMS and tokens[0] not in ACTION_VERBS:
        return False
    if any(t in FINITE_VERB_FORMS for t in tokens[1:-1]):
        return False
    if any(t in STRIP_INTERIOR for t in tokens[1:-1]):
        return False
    # interior conjunctions/prepositions usually mean a glued-together fragment,
    # except a single linking "of"/"for"/"and" between two content words.
    interior = tokens[1:-1]
    bad_interior = [t for t in interior if t in CONJUNCTIONS
                    or (t in PREPOSITIONS and t != "of")]
    if bad_interior:
        return False
    # finite lexical verb in the interior => clause fragment
    if any(t in COMMON_LEXICAL_VERBS and t not in ACTION_VERBS for t in tokens):
        return False
    content = [t for t in tokens if t not in FUNCTION_WORDS]
    if len(content) < 2:
        return False
    # reject "all generic" phrases (e.g. "the main thing")
    if all(t in GENERIC_WEAK_HEADS or t in FUNCTION_WORDS for t in tokens):
        return False
    return True


# ---------------------------------------------------------------------------
# Chunkers — yield COMPLETE constituents (never mid-constituent windows)
# ---------------------------------------------------------------------------

def _spacy_chunks(sent: str) -> List[str]:
    nlp = _get_spacy()
    if nlp is None:
        return []
    out: List[str] = []
    doc = nlp(sent)
    for nc in doc.noun_chunks:
        toks = tokenize(nc.text)
        toks = _trim_boundaries(toks)
        if _is_complete_phrase(toks):
            out.append(" ".join(toks))
    # verb + direct object -> action phrase
    for tok in doc:
        if tok.pos_ == "VERB" and tok.lemma_.lower() in ACTION_VERBS:
            for child in tok.children:
                if child.dep_ in {"dobj", "obj"}:
                    span = doc[tok.i:child.right_edge.i + 1]
                    cand = _trim_action(tokenize(span.text))
                    if cand:
                        out.append(cand)
    return out


def _noun_chunks_pos(sent: str) -> List[str]:
    """POS-driven NP chunking for the NLTK / heuristic paths.

    Grammar: an NP is a run of (NOUN|ADJ|NUM) tokens optionally joined by a
    single 'of'/'for'. We always anchor the phrase on the rightmost noun head
    and trim the left boundary, so output is never cut mid-head."""
    out: List[str] = []
    # split on clause punctuation so phrases never glue across a comma/clause
    for segment in re.split(r"[,;:()\u2013\u2014\u2022]| - ", sent):
        out.extend(_noun_chunks_segment(segment))
    return out


def _noun_chunks_segment(sent: str) -> List[str]:
    tokens = tokenize(sent)
    tags = pos_tag(tokens)
    out: List[str] = []

    np_tags = {"NOUN", "ADJ", "NUM"}
    i = 0
    n = len(tags)
    while i < n:
        if tags[i][1] not in np_tags:
            i += 1
            continue
        j = i
        while j < n:
            w, t = tags[j]
            if t in np_tags:
                j += 1
                continue
            # allow a single linking 'of' inside an NP ("rate of return")
            if w == "of" and j + 1 < n and tags[j + 1][1] in np_tags:
                j += 2
                continue
            break
        chunk = [w for w, _ in tags[i:j]]
        # Emit the full chunk and its head-anchored suffixes, so we keep the
        # head noun but also offer tighter sub-phrases. Every variant still
        # ends on the same noun head -> never hanging.
        for start in range(0, len(chunk) - 1):
            cand = _trim_boundaries(chunk[start:])
            if _is_complete_phrase(cand):
                out.append(" ".join(cand))
        i = j

    # action verb + following NP head
    for k, (w, t) in enumerate(tags):
        if w in ACTION_VERBS:
            tail = [tw for tw, tt in tags[k + 1:k + 5]]
            cand = _trim_action([w] + tail)
            if cand:
                out.append(cand)
    return out


def _trim_action(tokens: List[str]) -> Optional[str]:
    """Build a complete action phrase: verb + its object NP (ending on a head)."""
    if len(tokens) < 2 or tokens[0] not in ACTION_VERBS:
        return None
    head = tokens[0]
    # take following tokens until we hit a function word that ends the object
    obj: List[str] = []
    for t in tokens[1:]:
        if t in DETERMINERS and not obj:
            continue  # skip a leading determiner in the object
        if t in (PREPOSITIONS | CONJUNCTIONS | AUX_VERBS | PRONOUNS):
            break
        if t in PARTICLES_DEGREE:
            break
        obj.append(t)
        if len(obj) >= 3:
            break
    # trim trailing weak boundary on the object
    while obj and (obj[-1] in TRAILING_BAN or not _is_noun_like_head(obj[-1])):
        obj.pop()
    if not obj:
        return None
    phrase = [head] + obj
    if not (2 <= len(phrase) <= 5):
        return None
    return " ".join(phrase)


def _intent_phrases(sent: str) -> List[str]:
    s = canonical_phrase(sent)
    out: List[str] = []
    for start in INTENT_STARTS:
        idx = s.find(start)
        if idx == -1:
            continue
        tail = tokenize(s[idx:])
        # grow from the intent start to the next clause boundary, then trim
        cand: List[str] = []
        for t in tail:
            if t in (CONJUNCTIONS | AUX_VERBS) and len(cand) >= len(start.split()):
                break
            cand.append(t)
            if len(cand) >= 7:
                break
        # trim trailing function words, keep a noun-like head
        while cand and (cand[-1] in TRAILING_BAN or cand[-1] in AUX_VERBS
                        or not _is_noun_like_head(cand[-1])):
            cand.pop()
        if len(cand) >= 3 and not any(t in PRONOUNS for t in cand):
            out.append(" ".join(cand))
    return out


def _candidate_phrases(sent: str) -> List[str]:
    """Dispatch to the best chunker available."""
    if _get_spacy() is not None:
        chunks = _spacy_chunks(sent)
    else:
        chunks = _noun_chunks_pos(sent)
    chunks.extend(_intent_phrases(sent))
    # dedupe preserving order
    seen: Set[str] = set()
    uniq: List[str] = []
    for c in chunks:
        if c and c not in seen:
            seen.add(c)
            uniq.append(c)
    return uniq


# ---------------------------------------------------------------------------
# Lightweight, transparent quality scoring
# ---------------------------------------------------------------------------

SOURCE_WEIGHT: Dict[str, float] = {
    "title": 0.20, "heading_h1": 0.18, "heading_h2": 0.16, "heading_h3": 0.14,
    "heading_h4": 0.12, "heading_h5": 0.12, "heading_h6": 0.12,
    "list_item": 0.08, "intent": 0.12, "action_object": 0.10, "noun_phrase": 0.10,
}

ACCEPT_THRESHOLD = 0.50


def _score_phrase(tokens: List[str], source_type: str, snippet: str) -> Dict[str, Any]:
    content = [t for t in tokens if t not in FUNCTION_WORDS]
    n_content = max(1, len(content))

    # headedness: phrase ends on a strong/known head
    head = 0.0
    if tokens[-1] in UNIVERSAL_HEADS:
        head = 1.0
    elif tokens[-1] in GENERIC_WEAK_HEADS:
        head = 0.25
    else:
        head = 0.6  # plausible noun head

    # entity density: share of strong/long content tokens
    strong = sum(1 for t in content
                 if t in UNIVERSAL_HEADS or t in UNIVERSAL_MODIFIERS or len(t) >= 6)
    density = strong / n_content

    # specificity: modifier + head reads as a real concept
    has_modifier = any(t in UNIVERSAL_MODIFIERS for t in tokens[:-1]) or \
        any(len(t) >= 5 for t in tokens[:-1])
    specificity = 0.6 if has_modifier else 0.3

    # length sweet spot (2-4 content words)
    length = 1.0 if 2 <= len(content) <= 4 else 0.55

    # coverage in source snippet
    snip = set(tokenize(snippet))
    coverage = 1.0 if set(tokens).issubset(snip) else 0.6

    score = (
        0.28 * head +
        0.24 * density +
        0.18 * specificity +
        0.15 * length +
        0.15 * coverage +
        SOURCE_WEIGHT.get(source_type, 0.08)
    )
    score = max(0.0, min(1.0, round(score, 4)))

    return {
        "score": score,
        "threshold": ACCEPT_THRESHOLD,
        "decision": "ACCEPT" if score >= ACCEPT_THRESHOLD else "REJECT",
        "signals": {
            "headedness": round(head, 3),
            "entity_density": round(density, 3),
            "specificity": round(specificity, 3),
            "length": round(length, 3),
            "coverage": round(coverage, 3),
        },
    }


# ---------------------------------------------------------------------------
# Candidate assembly
# ---------------------------------------------------------------------------

def _reject(candidate: Dict[str, Any], reason: str,
            workspace_id: str, doc_id: str, vertical: str) -> None:
    learn_from_pipeline_rejection(
        workspace_id=workspace_id,
        document_id=doc_id,
        vertical=vertical,
        pipeline_stage="smart_extractor",
        candidate=candidate,
        rejection_reason=reason,
    )


def _add_candidate(
    out: List[Dict[str, Any]],
    seen: Set[str],
    phrase: str,
    source_type: str,
    section_id: str,
    snippet: str,
    doc_id: str = "",
    workspace_id: str = "default",
    vertical: str = "general",
) -> None:
    p = canonical_phrase(phrase)
    tokens = _trim_boundaries(tokenize(p))
    # drop interior determiners/possessives ("estimate your due date" -> "estimate due date")
    if len(tokens) > 2:
        tokens = [tokens[0]] + [t for t in tokens[1:-1] if t not in STRIP_INTERIOR] + [tokens[-1]]
    tokens = _trim_boundaries(tokens)
    p = " ".join(tokens)
    record = {"phrase": p, "source_type": source_type, "section_id": section_id}

    if not _is_complete_phrase(tokens):
        _reject(record, "incomplete_or_hanging_phrase", workspace_id, doc_id, vertical)
        return

    scoring = _score_phrase(tokens, source_type, snippet)
    if scoring["decision"] != "ACCEPT":
        _reject(record, "below_quality_threshold", workspace_id, doc_id, vertical)
        return

    key = f"{source_type}:{p}:{section_id}"
    if key in seen:
        return
    seen.add(key)

    out.append({
        "phrase": p,
        "source_type": source_type,
        "section_id": section_id,
        "doc_id": doc_id,
        "snippet": snippet,
        "extractor_intelligence": scoring,
    })


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_smart_phrases(
    *,
    text: str = "",
    html: str = "",
    title: str = "",
    doc_id: str = "",
    max_candidates: int = 500,
    workspace_id: str = "default",
    vertical: str = "general",
) -> List[Dict[str, Any]]:
    """Extract clean, complete anchor phrases from a document.

    Drop-in replacement for the previous version: same signature, same output
    dict shape ({phrase, source_type, section_id, doc_id, snippet,
    extractor_intelligence}).
    """
    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    if title:
        _add_candidate(out, seen, title, "title", "title_0", title,
                       doc_id, workspace_id, vertical)

    for h in extract_headings_and_lists(html):
        _add_candidate(out, seen, h.get("phrase") or "",
                       h.get("source_type") or "list_item",
                       h.get("section_id") or "section_0",
                       h.get("snippet") or "", doc_id, workspace_id, vertical)
        if len(out) >= max_candidates:
            return out[:max_candidates]

    paragraphs = extract_paragraphs(html=html, text=text)
    for pi, para in enumerate(paragraphs):
        for si, sent in enumerate(split_sentences(para)):
            section_id = f"p{pi}_s{si}"
            for phrase in _candidate_phrases(sent):
                source_type = "intent" if phrase.split()[0] in {
                    "how", "what", "when", "best", "signs", "symptoms",
                    "causes", "treatment", "guide", "tips", "ways",
                } else ("action_object" if phrase.split()[0] in ACTION_VERBS
                        else "noun_phrase")
                _add_candidate(out, seen, phrase, source_type, section_id,
                               sent, doc_id, workspace_id, vertical)
                if len(out) >= max_candidates:
                    return out[:max_candidates]

    return out[:max_candidates]


if __name__ == "__main__":
    sample_text = (
        "Many people want to calculate their fertile window before trying to "
        "conceive. The most accurate ovulation calculator uses your average "
        "cycle length and the date of your last period. You can also track "
        "cycle length over time. With a 28 day cycle, ovulation usually falls "
        "around day 14. This guide explains the simple calendar math. "
        "Our keyword research tool helps you build topic clusters and improve "
        "search ranking for your landing page."
    )
    sample_title = "Fertility Tracking Guide"
    sample_html = (
        "<h1>Ovulation Calculator</h1>"
        "<h2>How to calculate your fertile window</h2>"
        "<ul><li>Track cycle length</li><li>Estimate your due date</li></ul>"
        "<p>The conversion rate optimization checklist improves your "
        "landing page performance.</p>"
    )

    backend = "spaCy" if _get_spacy() else ("NLTK" if _have_nltk() else "heuristic")
    print(f"[chunker backend: {backend}]\n")
    results = extract_smart_phrases(
        text=sample_text, html=sample_html, title=sample_title, doc_id="demo",
    )
    for r in results:
        print(f"{r['extractor_intelligence']['score']:.2f}  "
              f"[{r['source_type']:<13}] {r['phrase']}")
    print(f"\nTotal: {len(results)} phrases")