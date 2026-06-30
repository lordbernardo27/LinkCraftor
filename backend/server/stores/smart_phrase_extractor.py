"""
Smart phrase extractor (corrected, niche-agnostic).

Produces *complete* anchor phrases — whole noun phrases or intent phrases that
never hang on a dangling article/preposition/conjunction and are never cut
mid-constituent.

Design (and what changed vs. the previous rewrite)
--------------------------------------------------
The previous version chunked into constituents and trimmed to content-word
boundaries — the right idea — but then re-derived grammar from curated
*noun* vocabulary (UNIVERSAL_HEADS, etc.). That made it implicitly tuned to
SEO/health niches: any head noun the lists didn't know, and any word that was
both a noun and a verb ("support", "research", "review", "study"), was thrown
away. It also over-trimmed adjectival ``-ly`` modifiers ("weekly report",
"monthly budget") and rejected its own verb-bearing intent phrases
("how to calculate ...").

This version fixes the asymmetry that makes an extractor universal:

  * VERBS are a (mostly) closed, niche-independent class -> we keep a broad
    verb lexicon and gate structurally on it.
  * NOUNS are open and vary by niche -> we never require a head to be in a
    curated list. When a POS tagger is available we *trust its tag* for the
    head; otherwise an unknown content word defaults to a valid head.

Curated domain lists now only *score* (a small bonus); they never gate. So the
extractor behaves the same for cooking, legal, automotive, gaming, finance,
travel, SaaS, etc.

It prefers spaCy, then NLTK, then a self-contained heuristic chunker, so it has
**no required dependencies**. ``extract_smart_phrases(...)`` keeps the same
signature and output shape as before (drop-in replacement).
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

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

try:  # extra domain vocabulary — optional (scoring only)
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
            # Keep the lemmatizer: the action-verb branch relies on tok.lemma_.
            _SPACY_NLP = spacy.load("en_core_web_sm", disable=["ner"])
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


# ---------------------------------------------------------------------------
# Lexical resources
# ---------------------------------------------------------------------------

WORD_RE = re.compile(r"[a-z0-9][a-z0-9'-]*", re.I)
TAG_RE = re.compile(r"<[^>]+>")
H_RE = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
LI_RE = re.compile(r"<li[^>]*>(.*?)</li>", re.IGNORECASE | re.DOTALL)
P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.IGNORECASE | re.DOTALL)

# Sentence splitter that does not break on common abbreviations, single
# capital initials, decimals, or "e.g."/"i.e."/"U.S.".
_ABBREV = (
    r"(?<!\b[A-Z])"                       # not a single capital initial
    r"(?<!\be\.g)(?<!\bi\.e)(?<!\bvs)"
    r"(?<!\bMr)(?<!\bMrs)(?<!\bMs)(?<!\bDr)(?<!\bSt)(?<!\bNo)"
    r"(?<!\bInc)(?<!\bLtd)(?<!\bCo)(?<!\bU\.S)(?<!\bU\.K)"
)
SENTENCE_SPLIT_RE = re.compile(
    r"(?:" + _ABBREV + r"(?<!\d\.\d)[.!?])\s+|\n+"
)

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

# Adjectival / temporal ``-ly`` words. These modify nouns ("weekly report",
# "friendly reminder") and must NOT be trimmed or tagged as adverbs.
ADJECTIVAL_LY: Set[str] = {
    "weekly", "biweekly", "daily", "monthly", "bimonthly", "quarterly",
    "yearly", "nightly", "hourly", "early", "friendly", "costly", "deadly",
    "lively", "lovely", "timely", "orderly", "elderly", "lonely", "ghostly",
    "lowly", "kindly", "weekly", "leisurely", "scholarly", "worldly",
    "heavenly", "earthly", "homely", "manly", "womanly", "saintly", "burly",
    "curly", "wily", "holy", "ugly", "silly",
}

# ``-ly`` tokens that are really nouns (so the adverb heuristic skips them).
LY_NOUN_EXCEPTIONS: Set[str] = {
    "family", "supply", "assembly", "anomaly", "ally", "rally", "monopoly",
    "italy", "july", "belly", "jelly", "reply", "duopoly", "homily", "doily",
}


def _is_adverb_ly(token: str) -> bool:
    """True for genuine ``-ly`` adverbs (quickly, easily) but not for
    adjectival/temporal ``-ly`` words or ``-ly`` nouns."""
    return (
        token.endswith("ly")
        and len(token) > 4
        and token not in LY_NOUN_EXCEPTIONS
        and token not in ADJECTIVAL_LY
    )


# Comparative / degree adverbs that should never be a phrase head or tail.
COMPARATIVES: Set[str] = {
    "faster", "slower", "better", "worse", "easier", "harder", "longer",
    "shorter", "higher", "lower", "bigger", "smaller", "greater", "sooner",
    "later", "more", "less", "fewer", "older", "newer", "cheaper", "stronger",
    "weaker", "wider", "deeper", "closer", "further", "farther", "best",
    "worst", "fastest", "slowest", "highest", "lowest", "largest", "smallest",
}

# Words that may NOT end a phrase (cause "hanging" tails).
TRAILING_BAN: Set[str] = PREPOSITIONS | CONJUNCTIONS | DETERMINERS | COMPARATIVES

# Words that may NOT start a phrase.
LEADING_BAN: Set[str] = FUNCTION_WORDS


def _verb_forms(lemmas: Set[str]) -> Set[str]:
    """Expand verb lemmas to common inflected forms (-s/-es/-ed/-ing/-ies)."""
    forms: Set[str] = set()
    for v in lemmas:
        forms.add(v)
        forms.update({v + "s", v + "es", v + "ed", v + "ing"})
        if v.endswith("e"):
            forms.update({v[:-1] + "es", v[:-1] + "ed", v[:-1] + "ing"})
        if v.endswith("y") and len(v) > 1 and v[-2] not in "aeiou":
            forms.update({v[:-1] + "ies", v[:-1] + "ied"})
        # simple final-consonant doubling (run -> running, stop -> stopped)
        if (len(v) >= 3 and v[-1] not in "aeiouwxy"
                and v[-2] in "aeiou" and v[-3] not in "aeiou"):
            forms.update({v + v[-1] + "ing", v + v[-1] + "ed"})
    return forms


# Verbs that head an action/intent anchor ("calculate due date").
ACTION_VERBS: Set[str] = {
    "calculate", "track", "confirm", "compare", "choose", "check", "measure",
    "estimate", "build", "create", "fix", "improve", "optimize", "reduce",
    "increase", "manage", "treat", "prevent", "diagnose", "review", "audit",
    "forecast", "plan", "write", "design", "analyze", "monitor", "test",
    "rank", "score", "publish", "import", "export", "sync", "validate",
    "protect", "find", "convert", "identify", "select", "schedule", "generate",
    "lower", "raise", "boost", "grow", "cut", "save", "earn", "spend", "lose",
    "cook", "bake", "clean", "install", "repair", "paint", "draw", "play",
    "book", "explore", "visit", "pack", "learn", "master", "understand",
}

# Broad, niche-INDEPENDENT lexicon of common English verbs. Verbs (unlike
# nouns) are a roughly closed class, so a generous list here is what makes the
# structural filter universal: it recognises clause signals like "boosts",
# "builds", "offers", "comes" in any domain.
_COMMON_VERB_LEMMAS: Set[str] = {
    "run", "fall", "land", "become", "mean", "depend", "explain", "turn",
    "make", "show", "happen", "rise", "stay", "offer", "work", "hold",
    "start", "end", "use", "give", "get", "go", "come", "take", "need",
    "want", "know", "say", "tell", "grow", "affect", "change", "watch",
    "look", "see", "let", "keep", "try", "read", "note", "avoid", "consider",
    "remember", "ensure", "pick", "add", "put", "ask", "call", "send",
    "follow", "apply", "enter", "click", "tap", "open", "close", "share",
    "help", "allow", "provide", "support", "include", "require", "reveal",
    "contain", "mention", "combine", "request", "invite", "connect",
    "complete", "summarize", "interpret", "guide", "unlock", "confuse",
    "pass", "lean", "bring", "toss", "qualify", "define", "return", "sign",
    "break", "restore", "extend", "reach", "explore", "discover", "feel",
    "think", "believe", "seem", "appear", "remain", "leave", "move", "live",
    "love", "hate", "like", "play", "win", "lose", "buy", "sell", "pay",
    "cost", "spend", "save", "earn", "invest", "borrow", "lend", "owe",
    "build", "boost", "drive", "ride", "fly", "walk", "cook", "bake", "mix",
    "stir", "chop", "slice", "pour", "heat", "cool", "freeze", "serve",
    "wash", "clean", "fix", "repair", "paint", "cut", "drill", "screw",
    "charge", "power", "press", "hit", "push", "pull", "lift", "carry",
    "throw", "catch", "draw", "design", "create", "write", "edit", "delete",
    "update", "upload", "download", "install", "configure", "deploy", "test",
    "debug", "compile", "render", "parse", "store", "fetch", "load", "save",
    "lower", "raise", "reduce", "increase", "improve", "boost", "grow",
    "shrink", "expand", "scale", "convert", "process", "handle", "execute",
    "perform", "achieve", "reach", "meet", "exceed", "match", "compare",
    "rank", "rate", "review", "audit", "monitor", "measure", "calculate",
    "estimate", "forecast", "predict", "plan", "schedule", "book", "reserve",
    "order", "ship", "deliver", "track", "trace", "locate", "search", "filter",
    "sort", "group", "merge", "split", "join", "link", "attach", "remove",
    "replace", "swap", "toggle", "select", "choose", "decide", "determine",
    "identify", "detect", "recognize", "classify", "label", "tag", "name",
    "describe", "summarize", "report", "record", "log", "count", "sum",
    "treat", "cure", "heal", "prevent", "diagnose", "prescribe", "inject",
    "absorb", "digest", "burn", "stretch", "train", "exercise", "rest",
    "sleep", "wake", "breathe", "relax", "focus", "study", "teach", "learn",
    "practice", "master", "memorize", "recall", "understand", "realize",
    "notice", "observe", "examine", "inspect", "analyze", "evaluate", "assess",
    "judge", "rate", "score", "grade", "approve", "reject", "accept", "deny",
    "confirm", "verify", "validate", "authenticate", "authorize", "grant",
    "protect", "secure", "encrypt", "decrypt", "block", "allow", "permit",
    "enable", "disable", "activate", "deactivate", "launch", "release",
    "publish", "promote", "advertise", "market", "brand", "position", "target",
    "engage", "retain", "acquire", "onboard", "subscribe", "renew", "cancel",
    "refund", "charge", "bill", "invoice", "quote", "negotiate", "close",
    "manage", "lead", "organize", "coordinate", "assign", "delegate",
    "collaborate", "communicate", "discuss", "present", "pitch", "propose",
    "recommend", "suggest", "advise", "warn", "remind", "notify", "alert",
    "happen", "occur", "result", "cause", "lead", "trigger", "drive", "shape",
    "form", "develop", "evolve", "transform", "adapt", "adjust", "modify",
    "customize", "personalize", "automate", "streamline", "simplify",
    "clarify", "highlight", "emphasize", "feature", "include", "exclude",
}

# All inflected forms of every verb we know about. Used for reliable verb
# detection in the boundary / completeness logic and the heuristic tagger.
VERB_FORMS: Set[str] = _verb_forms(ACTION_VERBS | _COMMON_VERB_LEMMAS)

# Gerund (-ing) forms frequently act as noun modifiers / nominal heads
# ("tracking guide", "strength training"), so they are allowed inside / at the
# end of a noun phrase. Finite and past forms are clause signals.
GERUND_FORMS: Set[str] = {v for v in VERB_FORMS if v.endswith("ing")}
FINITE_VERB_FORMS: Set[str] = VERB_FORMS - GERUND_FORMS

# Interior determiners/possessives are safe to drop from an anchor.
STRIP_INTERIOR: Set[str] = {
    "the", "a", "an", "this", "that", "these", "those",
    "my", "your", "his", "her", "its", "our", "their",
}

INTENT_STARTS: Tuple[str, ...] = (
    "how to", "how many", "how much", "what is", "what are", "when to",
    "when do", "where to", "why is", "why are", "best way to", "best time to",
    "best ways to", "signs of", "symptoms of", "causes of", "benefits of",
    "treatment for", "guide to", "tips for", "ways to", "steps to",
    "reasons to", "reasons why",
)

INTENT_FIRST_WORDS: Set[str] = {
    "how", "what", "when", "where", "why", "best", "signs", "symptoms",
    "causes", "benefits", "treatment", "guide", "tips", "ways", "steps",
    "reasons",
}

# Generic heads too weak to stand alone unless well qualified.
GENERIC_WEAK_HEADS: Set[str] = {
    "thing", "things", "stuff", "way", "ways", "part", "parts", "case",
    "cases", "point", "points", "area", "areas", "level", "type", "types",
    "form", "forms", "kind", "kinds", "sort", "sorts", "lot", "bit",
}

# Strong content heads — SCORING ONLY (never a gate). Domain vocab can extend
# these via the optional import.
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
    s = re.sub(r"^\s*(?:\d+[.)]\s+|[\u2022\u2013\u2014\-]\s+)", "", s)
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

_NOUN_SUFFIXES = ("tion", "sion", "ment", "ness", "ity", "ship", "ance",
                  "ence", "ics", "ism", "age", "ure", "ist", "ery")
_VERB_SUFFIXES = ("ize", "ise", "ify")
_ING_ED_NOUNS = {
    "marketing", "branding", "onboarding", "training", "ranking", "rankings",
    "pricing", "billing", "listing", "listings", "meeting", "meetings",
    "setting", "settings", "building", "buildings", "reporting", "advertising",
    "engineering", "accounting", "funding", "spending", "earnings", "savings",
    "advanced", "automated", "integrated", "detailed", "dedicated", "related",
    "recommended", "estimated", "extended", "salted", "cooked", "guided",
    "cushioned", "creamy",  # adjectival participles seen as NP modifiers
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
    if w in ADJECTIVAL_LY:
        return "ADJ"
    if w in _ING_ED_NOUNS:
        return "NOUN"
    # inflected verb forms (builds, boosts, tracks) are strong clause signals;
    # the context retag pass can still demote a clause-final one to a plural noun.
    if _is_inflected_verb(w):
        return "VERB"
    if w in GERUND_FORMS:
        return "NOUN"        # gerunds usually nominal/modifier in NP context
    # known noun heads / modifiers and noun morphology win over a *bare* lemma
    # that merely happens to also be a verb (rate, score, support, schedule).
    if w in UNIVERSAL_HEADS or w in UNIVERSAL_MODIFIERS or w in GENERIC_WEAK_HEADS:
        return "NOUN"
    if w.endswith(_NOUN_SUFFIXES):
        return "NOUN"
    # remaining bare verb lemmas (make, reduce, build, drive...) are clause verbs
    if w in FINITE_VERB_FORMS or w in ACTION_VERBS:
        return "VERB"
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

def _trim_boundaries(tokens: Sequence[str]) -> List[str]:
    """Strip leading/trailing function words so the phrase begins and ends on a
    content word. Adjectival ``-ly`` modifiers are preserved at the front.

    Only *inflected* finite verb forms (boosts, builds, tracks) are stripped
    from the front; bare lemmas that double as nouns (search, lean, feature)
    are kept, since here they head/modify a noun phrase."""
    toks = list(tokens)
    while toks and (
        toks[0] in LEADING_BAN
        or (_is_inflected_verb(toks[0]) and toks[0] not in ACTION_VERBS)
    ):
        toks.pop(0)
    while toks and (
        toks[-1] in TRAILING_BAN
        or toks[-1] in AUX_VERBS
        or toks[-1] in PARTICLES_DEGREE
        or _is_adverb_ly(toks[-1])
    ):
        toks.pop()
    return toks


def _head_is_noun_like(token: str, tag: Optional[str]) -> bool:
    """Decide whether ``token`` can be a phrase head. When a tagger supplies a
    tag we trust it (this is what makes heads niche-agnostic); otherwise we use
    morphology + the closed verb class."""
    if token in COMPARATIVES or _is_adverb_ly(token):
        return False
    if tag is not None:
        if tag in {"NOUN", "NUM"}:
            return True
        if tag == "ADJ":
            return False  # adjective tail = hanging ("very large")
        if tag == "VERB":
            # gerund / participle used nominally is OK; finite verb is not.
            return token in _ING_ED_NOUNS or token in GERUND_FORMS
        return False
    # ---- no tagger: morphology-based fallback ----
    if token in _ING_ED_NOUNS or token in GERUND_FORMS:
        return True
    if token in GENERIC_WEAK_HEADS or token in UNIVERSAL_HEADS:
        return True
    if token in FINITE_VERB_FORMS:
        return False
    if token in (AUX_VERBS | PREPOSITIONS | CONJUNCTIONS | PRONOUNS | DETERMINERS):
        return False
    if token.endswith("ed") and token not in _ING_ED_NOUNS:
        return False
    return True


def _is_finite_verb(token: str, tag: Optional[str]) -> bool:
    """Is this token a finite/clause verb (a clause signal), as opposed to a
    nominal gerund/participle modifier? Tags have already been cleaned by the
    retag pass, so when a tag is present we trust it."""
    if _is_gerund(token) or token in _ING_ED_NOUNS or token in GERUND_FORMS:
        return False
    if tag == "VERB":
        return True
    if tag in {"NOUN", "NUM", "ADJ"}:
        return False                         # trust the (retagged) tagger
    # no tag available: fall back to the closed verb class, inflected forms only
    return _is_inflected_verb(token) or (token in ALL_VERB_LEMMAS
                                         and token in FINITE_VERB_FORMS
                                         and token not in _ING_ED_NOUNS)


def _is_complete_phrase(tokens: Sequence[str],
                        tags: Optional[Sequence[str]] = None) -> bool:
    """A phrase is complete iff it is a clean noun-phrase constituent.

    Tag-aware: when ``tags`` are provided they drive the head and interior-verb
    decisions, so any niche's head noun is accepted. ``tags`` must align 1:1
    with ``tokens``.
    """
    toks = list(tokens)
    if not (2 <= len(toks) <= 6):
        return False
    tg: List[Optional[str]] = list(tags) if tags is not None else [None] * len(toks)
    if len(tg) != len(toks):
        tg = [None] * len(toks)

    if toks[0] in LEADING_BAN or toks[-1] in TRAILING_BAN:
        return False
    if not _head_is_noun_like(toks[-1], tg[-1]):
        return False
    if any(t in AUX_VERBS for t in toks):
        return False
    if any(t in PRONOUNS for t in toks):
        return False
    # leading finite verb (not an action verb) => glued clause ("boosts metabolism")
    if _is_finite_verb(toks[0], tg[0]) and toks[0] not in ACTION_VERBS:
        return False
    # any interior finite verb => glued clause
    for t, g in zip(toks[1:-1], tg[1:-1]):
        if _is_finite_verb(t, g):
            return False
    if any(t in STRIP_INTERIOR for t in toks[1:-1]):
        return False
    # interior conjunctions / non-'of' prepositions => fragment
    for t in toks[1:-1]:
        if t in CONJUNCTIONS or (t in PREPOSITIONS and t != "of"):
            return False
    content = [t for t in toks if t not in FUNCTION_WORDS]
    if len(content) < 2:
        return False
    if all(t in GENERIC_WEAK_HEADS or t in FUNCTION_WORDS for t in toks):
        return False
    return True


def _is_complete_intent(tokens: Sequence[str],
                        tags: Optional[Sequence[str]] = None) -> bool:
    """Validate a verb-bearing intent phrase ("how to calculate fertile window").

    Intent phrases legitimately contain an interior verb, so they use their own
    rule: recognised intent prefix, 3..7 tokens, ends on a noun-like head, no
    dangling boundary, no pronouns."""
    toks = list(tokens)
    if not (3 <= len(toks) <= 7):
        return False
    if any(t in PRONOUNS for t in toks):
        return False
    if toks[-1] in TRAILING_BAN or toks[-1] in AUX_VERBS:
        return False
    joined = " ".join(toks)
    if not any(joined.startswith(p) for p in INTENT_STARTS):
        return False
    tg = list(tags) if tags is not None and len(tags) == len(toks) else [None] * len(toks)
    if not _head_is_noun_like(toks[-1], tg[-1]):
        return False
    return True


# ---------------------------------------------------------------------------
# Chunkers — yield (phrase, tags) for COMPLETE constituents only
# ---------------------------------------------------------------------------

Cand = Tuple[str, str, List[str]]   # (phrase, kind, tags)  kind in {np, action, intent}


def _spacy_chunks(sent: str) -> List[Cand]:
    nlp = _get_spacy()
    if nlp is None:
        return []
    out: List[Cand] = []
    doc = nlp(sent)
    for nc in doc.noun_chunks:
        keep: List[str] = []
        tags: List[str] = []
        for t in nc:
            if not WORD_RE.fullmatch(t.text):
                continue
            keep.append(t.text.lower())
            tags.append(_coarsen_ptb(t.tag_) if t.tag_ else _spacy_coarse(t))
        # enumerate sub-anchors so compounds yield their inner phrases too
        out.extend(_windows_from_run(list(zip(keep, tags))))
    return out


def _spacy_coarse(tok) -> str:
    m = {"NOUN": "NOUN", "PROPN": "NOUN", "VERB": "VERB", "ADJ": "ADJ",
         "ADV": "ADV", "DET": "DET", "ADP": "ADP", "CCONJ": "CONJ",
         "SCONJ": "CONJ", "PRON": "PRON", "NUM": "NUM", "AUX": "AUX"}
    return m.get(tok.pos_, "X")


def _trim_with_tags(tokens: List[str], tags: List[str]) -> Tuple[List[str], List[str]]:
    toks, tg = list(tokens), list(tags)
    while toks and (
        toks[0] in LEADING_BAN
        or (_confirmed_finite(toks[0], tg[0]) and toks[0] not in ACTION_VERBS)
    ):
        toks.pop(0)
        tg.pop(0)
    while toks and (
        toks[-1] in TRAILING_BAN or toks[-1] in AUX_VERBS
        or toks[-1] in PARTICLES_DEGREE or _is_adverb_ly(toks[-1])
    ):
        toks.pop()
        tg.pop()
    return toks, tg


# Verbs (base + inflections) we treat as a roughly closed class.
ALL_VERB_LEMMAS: Set[str] = ACTION_VERBS | _COMMON_VERB_LEMMAS


def _is_gerund(w: str) -> bool:
    """True for -ing forms that act as nominal/participial NP modifiers."""
    return len(w) > 4 and w.endswith("ing") and w not in AUX_VERBS


def _confirmed_finite(w: str, t: Optional[str]) -> bool:
    """A *confirmed* finite verb: an inflected known verb form (strong signal),
    or a base verb the tagger also calls a VERB. Base forms that are also common
    nouns (feature, search, rate, ...) are NOT confirmed unless the tagger agrees,
    so we never shatter a noun compound on an ambiguous word."""
    if _is_gerund(w) or w in _ING_ED_NOUNS:
        return False
    if w in FINITE_VERB_FORMS:
        if w in ALL_VERB_LEMMAS:        # base form -> need tagger agreement
            return t == "VERB"
        return True                      # inflected -s/-es/-ed/-ies -> strong verb
    return False


def _np_eligible(w: str, t: Optional[str]) -> bool:
    """May this token sit *inside* a noun phrase run? Tags are already retagged,
    so VERB means a real clause verb here."""
    if w == "to":
        return False
    if t in {"DET", "CONJ", "PRON", "AUX"}:
        return False
    if t == "ADP" and w != "of":
        return False
    if w in DETERMINERS or w in CONJUNCTIONS or w in PRONOUNS or w in AUX_VERBS:
        return False
    if w in PREPOSITIONS and w != "of":
        return False
    if _is_gerund(w) or w in _ING_ED_NOUNS:
        return True
    if t == "VERB":
        return False
    return True


def _is_inflected_verb(w: str) -> bool:
    """A known verb in an inflected (-s/-es/-ed/-ies) form, i.e. NOT a bare
    lemma. These are the forms NLTK most often mislabels as NNS in compounds."""
    return (w in FINITE_VERB_FORMS and w not in ALL_VERB_LEMMAS
            and not _is_gerund(w) and w not in _ING_ED_NOUNS)


_OBJECT_STARTERS = {"NOUN", "ADJ", "NUM", "DET", "PRON"}


def _nominalize_tags(tags: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Context-aware retag that cleans up the two systematic tagger errors that
    fragment noun compounds, then lets everything downstream simply trust tags:

    1. Inflected verb forms (builds, tracks, boosts, rates) are decided by
       right context: a finite verb is followed by an object/predicate; the same
       form at clause end / before a conjunction or preposition is a plural noun.
    2. A bare verb lemma the tagger called VERB but which sits inside an object
       NP after the real clause verb (and not after to/of/det) is a compound
       noun modifier ('tracks feature adoption')."""
    out = list(tags)
    n = len(out)
    block_left = ({"to"} | PREPOSITIONS | CONJUNCTIONS | AUX_VERBS
                  | DETERMINERS | PRONOUNS)
    seen_verb = False
    for i, (w, t) in enumerate(out):
        if w in CONJUNCTIONS or w == "to":
            seen_verb = False
        rt = out[i + 1] if i + 1 < n else None

        # (1) resolve inflected known-verb forms by right context
        if _is_inflected_verb(w):
            obj_start = (
                rt is not None and rt[0] not in CONJUNCTIONS and rt[0] != "to"
                and (rt[1] in _OBJECT_STARTERS
                     or (rt[1] == "VERB" and rt[0] in ALL_VERB_LEMMAS
                         and not _is_gerund(rt[0])))
            )
            out[i] = (w, "VERB" if obj_start else "NOUN")
            if obj_start:
                seen_verb = True
            continue

        # (2) demote a bare verb lemma that is really a compound modifier
        is_base = (w in ALL_VERB_LEMMAS and w not in _ING_ED_NOUNS
                   and not _is_gerund(w))
        if is_base and t == "VERB" and seen_verb:
            lt = out[i - 1] if i > 0 else None
            right_noun = rt is not None and _head_is_noun_like(rt[0], rt[1])
            left_ok = lt is not None and lt[0] not in block_left
            if right_noun and left_ok:
                out[i] = (w, "NOUN")
                continue

        # a real present-tense finite verb marks the clause verb as seen;
        # leading -ed participles (automated, integrated) must NOT count.
        if (t == "VERB" and not _is_gerund(w) and w not in _ING_ED_NOUNS
                and not w.endswith("ed")):
            seen_verb = True
    return out


def _runs_from_tags(tags: List[Tuple[str, str]]) -> List[List[Tuple[str, str]]]:
    runs: List[List[Tuple[str, str]]] = []
    cur: List[Tuple[str, str]] = []
    for w, t in tags:
        if _np_eligible(w, t):
            cur.append((w, t))
        else:
            if cur:
                runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return runs


def _windows_from_run(run: List[Tuple[str, str]]) -> List[Cand]:
    """Every contiguous sub-window that ends on a noun head and survives the
    completeness check. This is what yields both the full compound
    ('weekly strength training') and its sub-anchors ('strength training')."""
    out: List[Cand] = []
    m = len(run)
    for e in range(m):
        we, te = run[e]
        if not _head_is_noun_like(we, te):
            continue
        for s in range(e):                       # window length >= 2
            if e - s + 1 > 6:
                continue
            toks = [w for w, _ in run[s:e + 1]]
            tgs = [t for _, t in run[s:e + 1]]
            tt, tg = _trim_with_tags(toks, tgs)
            if _is_complete_phrase(tt, tg):
                out.append((" ".join(tt), "np", tg))
    return out


def _noun_chunks_pos(sent: str) -> List[Cand]:
    tokens = tokenize(sent)
    if not tokens:
        return []
    tags = _nominalize_tags(pos_tag(tokens))
    out: List[Cand] = []
    for run in _runs_from_tags(tags):
        out.extend(_windows_from_run(run))
    return out


def _intent_phrases(sent: str) -> List[Cand]:
    s = canonical_phrase(sent)
    out: List[Cand] = []
    for start in INTENT_STARTS:
        idx = s.find(start)
        if idx == -1:
            continue
        # ensure it's a word boundary start
        if idx > 0 and s[idx - 1].isalnum():
            continue
        tail = tokenize(s[idx:])
        cand: List[str] = []
        nstart = len(start.split())
        for t in tail:
            # stop at a clause boundary or a trailing prepositional phrase once
            # the core anchor is captured ("...track cycle length | over time")
            if len(cand) >= nstart and (
                t in CONJUNCTIONS or t in AUX_VERBS
                or (t in PREPOSITIONS and t != "of")
            ):
                break
            cand.append(t)
            if len(cand) >= 8:
                break
        # drop interior possessives/determiners ("calculate your due date")
        if len(cand) > nstart:
            cand = cand[:nstart] + [t for t in cand[nstart:] if t not in STRIP_INTERIOR]
        while cand and (cand[-1] in TRAILING_BAN or cand[-1] in AUX_VERBS
                        or not _head_is_noun_like(cand[-1], None)):
            cand.pop()
        if _is_complete_intent(cand):
            out.append((" ".join(cand), "intent", []))
    return out


def _candidate_phrases(sent: str) -> List[Cand]:
    """Dispatch to the best chunker available, plus intent phrases."""
    if _get_spacy() is not None:
        chunks = _spacy_chunks(sent)
    else:
        chunks = _noun_chunks_pos(sent)
    chunks.extend(_intent_phrases(sent))
    seen: Set[str] = set()
    uniq: List[Cand] = []
    for phrase, kind, tg in chunks:
        if phrase and phrase not in seen:
            seen.add(phrase)
            uniq.append((phrase, kind, tg))
    return uniq


# ---------------------------------------------------------------------------
# Lightweight, transparent, niche-agnostic quality scoring
# ---------------------------------------------------------------------------

SOURCE_WEIGHT: Dict[str, float] = {
    "title": 0.20, "heading_h1": 0.18, "heading_h2": 0.16, "heading_h3": 0.14,
    "heading_h4": 0.12, "heading_h5": 0.12, "heading_h6": 0.12,
    "list_item": 0.10, "intent": 0.14, "action_object": 0.12, "noun_phrase": 0.10,
}

ACCEPT_THRESHOLD = 0.50


def _score_phrase(tokens: Sequence[str], tags: Optional[Sequence[str]],
                  source_type: str, snippet: str) -> Dict[str, Any]:
    toks = list(tokens)
    content = [t for t in toks if t not in FUNCTION_WORDS]
    n_content = max(1, len(content))
    tg = list(tags) if tags and len(tags) == len(toks) else [None] * len(toks)

    # headedness: structural first (tagger/morphology), domain list is a bonus.
    head_tok, head_tag = toks[-1], tg[-1]
    if head_tok in GENERIC_WEAK_HEADS:
        head = 0.30
    elif head_tok in UNIVERSAL_HEADS:
        head = 1.0
    elif head_tag in {"NOUN", "NUM"} or _head_is_noun_like(head_tok, head_tag):
        head = 0.80                      # any real noun head — niche-agnostic
    else:
        head = 0.50

    # entity density: share of "substantial" content tokens (len>=4) plus a
    # small bonus for known-strong vocab. Length-based => works in any niche.
    strong = sum(1 for t in content
                 if len(t) >= 4 or t in UNIVERSAL_HEADS or t in UNIVERSAL_MODIFIERS)
    density = strong / n_content

    # specificity: a modifier + head reads as a real concept.
    has_modifier = (
        len(content) >= 2
        and any((len(t) >= 4) or (t in UNIVERSAL_MODIFIERS) for t in toks[:-1])
    )
    specificity = 0.7 if has_modifier else 0.35

    # length sweet spot (2-4 content words)
    length = 1.0 if 2 <= len(content) <= 4 else 0.55

    # coverage in source snippet
    snip = set(tokenize(snippet))
    coverage = 1.0 if set(toks).issubset(snip) else 0.6

    score = (
        0.30 * head +
        0.22 * density +
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

def _reject(candidate: Dict[str, Any], reason: str, seen_rejects: Set[str],
            workspace_id: str, doc_id: str, vertical: str) -> None:
    # de-duplicate rejection logging so suffix expansion can't spam the hook.
    key = f"{reason}:{candidate.get('phrase','')}"
    if key in seen_rejects:
        return
    seen_rejects.add(key)
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
    seen_rejects: Set[str],
    phrase: str,
    kind: str,
    tags: Optional[Sequence[str]],
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

    # tags coming from the chunker were aligned to the *pre-canonical* tokens;
    # only trust them if they still align, else recompute.
    tg: Optional[List[str]] = None
    if tags and len(tags) == len(tokens):
        tg = list(tags)

    is_intent = kind == "intent" or (tokens and tokens[0] in INTENT_FIRST_WORDS
                                      and " ".join(tokens).startswith(INTENT_STARTS))
    if is_intent:
        if tg is None:
            tg = [t for _, t in pos_tag(tokens)]
        ok = _is_complete_intent(tokens, tg)
    else:
        if tg is None:
            tg = [t for _, t in pos_tag(tokens)]
        ok = _is_complete_phrase(tokens, tg)

    if not ok:
        _reject(record, "incomplete_or_hanging_phrase", seen_rejects,
                workspace_id, doc_id, vertical)
        return

    scoring = _score_phrase(tokens, tg, source_type, snippet)
    if scoring["decision"] != "ACCEPT":
        _reject(record, "below_quality_threshold", seen_rejects,
                workspace_id, doc_id, vertical)
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


def _classify_source(phrase: str, kind: str) -> str:
    first = phrase.split()[0] if phrase else ""
    if kind == "intent" or (first in INTENT_FIRST_WORDS
                            and phrase.startswith(INTENT_STARTS)):
        return "intent"
    return "noun_phrase"


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
    seen_rejects: Set[str] = set()

    if title:
        _add_candidate(out, seen, seen_rejects, title, "np", None,
                       "title", "title_0", title, doc_id, workspace_id, vertical)
        # also mine sub-anchors from the title ("Residential Lease Agreement
        # Basics" -> "lease agreement")
        for phrase, kind, tg in _candidate_phrases(title):
            _add_candidate(out, seen, seen_rejects, phrase, kind, tg,
                           _classify_source(phrase, kind), "title_0", title,
                           doc_id, workspace_id, vertical)

    for h in extract_headings_and_lists(html):
        whole = h.get("phrase") or ""
        src = h.get("source_type") or "list_item"
        sec = h.get("section_id") or "section_0"
        snip = h.get("snippet") or ""
        _add_candidate(out, seen, seen_rejects, whole, "np", None,
                       src, sec, snip, doc_id, workspace_id, vertical)
        for phrase, kind, tg in _candidate_phrases(snip or whole):
            _add_candidate(out, seen, seen_rejects, phrase, kind, tg,
                           _classify_source(phrase, kind), sec, snip,
                           doc_id, workspace_id, vertical)
        if len(out) >= max_candidates:
            return out[:max_candidates]

    paragraphs = extract_paragraphs(html=html, text=text)
    for pi, para in enumerate(paragraphs):
        for si, sent in enumerate(split_sentences(para)):
            section_id = f"p{pi}_s{si}"
            for phrase, kind, tg in _candidate_phrases(sent):
                source_type = _classify_source(phrase, kind)
                _add_candidate(out, seen, seen_rejects, phrase, kind, tg,
                               source_type, section_id, sent,
                               doc_id, workspace_id, vertical)
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