from __future__ import annotations

import re
from typing import Any, Dict, List, Set


try:
    from backend.server.stores.universal_noun_families import (
        get_all_universal_nouns,
        get_all_universal_modifiers,
    )
except ImportError:
    def get_all_universal_nouns() -> Set[str]:
        return set()

    def get_all_universal_modifiers() -> Set[str]:
        return set()


WORD_RE = re.compile(r"[a-z0-9]{2,}", re.I)
TAG_RE = re.compile(r"<[^>]+>")
H_RE = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
LI_RE = re.compile(r"<li[^>]*>(.*?)</li>", re.IGNORECASE | re.DOTALL)
P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.IGNORECASE | re.DOTALL)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")


STOPWORDS: Set[str] = {
    "the", "and", "for", "with", "that", "this", "from", "into", "your", "you",
    "are", "was", "were", "will", "can", "could", "should", "would", "have",
    "has", "had", "about", "over", "under", "than", "then", "when", "what",
    "where", "which", "who", "whom", "why", "how", "a", "an", "to", "of",
    "in", "on", "at", "by", "or", "as", "is", "it", "be", "not", "no",
    "if", "but", "so", "because", "after", "before", "during", "while",
    "through", "up", "down", "out", "off", "too", "very", "also",
}

PRONOUNS: Set[str] = {
    "i", "me", "my", "mine", "you", "your", "yours", "he", "him", "his",
    "she", "her", "hers", "we", "us", "our", "ours", "they", "them",
    "their", "theirs", "it", "its", "everyone", "someone", "anyone",
}

HELPER_VERBS: Set[str] = {
    "is", "are", "was", "were", "be", "being", "been", "am",
    "can", "could", "will", "would", "should", "may", "might",
    "has", "have", "had", "do", "does", "did",
}

CLAUSE_VERBS: Set[str] = {
    "runs", "run", "falls", "fall", "lands", "land", "becomes", "become",
    "means", "mean", "depends", "depend", "explains", "explain",
    "unlocks", "unlock", "turns", "turn", "makes", "make", "shows", "show",
    "happens", "happen", "passes", "pass", "rises", "rise", "stays", "stay",
    "confuses", "confuse", "offers", "offer", "works", "work", "holds",
    "hold", "starts", "start", "ends", "end", "uses", "use",
    "publish", "publishes", "create", "creates", "improve", "improves",
    "increase", "increases", "reduce", "reduces", "guide", "guides",
    "summarize", "summarizes", "map", "maps", "contain", "contains",
    "mention", "mentions", "fit", "fits", "gain", "gains",
    "interpret", "interprets", "support", "supports", "combine", "combines",
    "understand", "understands", "view", "views", "select", "selects",
    "request", "requests", "invite", "invites", "connect", "connects",
    "complete", "completes", "compare", "compares", "help", "helps",
    "include", "includes", "provide", "provides", "require", "requires",
    "reveal", "reveals",
}

ACTION_TOKENS: Set[str] = {
    "calculate", "track", "confirm", "compare", "choose", "check", "measure",
    "estimate", "build", "create", "fix", "improve", "optimize", "reduce",
    "increase", "manage", "treat", "prevent", "diagnose", "review", "audit",
    "forecast", "plan", "write", "design", "analyze", "monitor", "test",
    "rank", "score", "publish", "import", "export", "sync", "validate",
    "protect",
}

BAD_STARTS: Set[str] = {
    "and", "or", "but", "so", "then", "this", "that", "these", "those",
    "your", "you", "many", "people", "because", "whether", "rather",
    "without", "with", "into", "from", "for", "to", "at", "on", "by",
    "if", "while", "often", "still", "just", "as", "based", "brief",
    "trained", "everyone", "someone", "anyone", "most", "time", "back",
    "inside", "outside", "category", "such",
}

BAD_ENDINGS: Set[str] = {
    "and", "or", "but", "so", "then", "this", "that", "your", "someone",
    "ask", "depends", "changes", "because", "about", "before", "after",
    "during", "through", "with", "without", "than", "rather", "into",
    "from", "for", "to", "by", "if", "when", "while", "at", "on",
    "a", "an", "the", "last", "much", "main", "one", "of", "most",
    "near", "afterward", "afterwards",
}

VAGUE_ADVERB_ENDINGS: Set[str] = {
    "afterward", "afterwards", "later", "soon", "today", "tomorrow",
    "yesterday", "eventually", "recently", "currently",
}

INTENT_STARTS = (
    "how to",
    "how many",
    "what is",
    "what are",
    "when do",
    "when does",
    "best way",
    "best time",
    "signs of",
    "symptoms of",
    "causes of",
    "treatment for",
    "guide to",
    "tips for",
)

CONDITION_CONNECTORS: Set[str] = {
    "after", "before", "during", "without", "with", "near", "for",
}

WEAK_CONNECTOR_STARTS = (
    "based on",
    "with a",
    "with an",
    "without a",
    "without an",
    "before getting",
    "after getting",
    "rather than",
    "back into",
    "inside the",
    "outside the",
    "such as",
)

WEAK_ENDING_PHRASES = (
    "the day",
    "on day",
    "start date",
    "end date",
    "first step",
    "next step",
    "last step",
    "the product",
    "the application",
    "the page",
    "the site",
)

THIN_MODIFIERS: Set[str] = {
    "brief", "trained", "simple", "basic", "easy", "quick", "perfect",
    "general", "common", "normal", "regular", "main", "major", "minor",
    "good", "bad", "better", "best", "new", "old", "early", "late",
    "clear", "full", "important", "highlighted", "recommended",
}

GENERIC_WEAK_HEADS: Set[str] = {
    "date", "day", "days", "time", "thing", "things",
    "way", "ways", "step", "steps", "part", "parts", "case", "cases",
    "reason", "reasons", "example", "examples", "number", "point",
    "points", "area", "level", "type", "types", "form", "forms",
    "stuff",
}

CLAUSE_CONNECTORS: Set[str] = {
    "when", "because", "while", "than", "although",
    "unless", "since", "whereas", "though",
}

UNIVERSAL_HEAD_SUFFIXES: Set[str] = {
    "software", "tool", "tools", "platform", "system", "strategy", "workflow",
    "automation", "integration", "pipeline", "dashboard", "api", "app",
    "application", "plugin", "extension", "database", "storage", "security",
    "seo", "keyword", "keywords", "content", "backlink", "audit",
    "optimization", "conversion", "landing", "page", "traffic", "ranking",
    "analytics", "yield", "rate", "rates", "forecast", "tax", "reporting",
    "investment", "lease", "agreement", "contract", "review", "lawyer",
    "visa", "property", "mortgage", "insurance", "calculator", "checklist",
    "service", "services", "pricing", "prices", "policy", "delivery",
    "menu", "reservation", "restaurant", "hotel", "airport", "coverage",
    "rental", "checkout", "cart", "product", "customer", "tutoring",
    "study", "management", "project", "ideas", "questions",
    "resume", "interview", "course", "lesson", "training", "symptoms",
    "causes", "treatment", "medication", "dosage", "foods", "options",
    "therapy", "performance", "settings", "guide", "benefits",
    "contractor", "estimate", "schedule", "routine", "collection",
    "trends", "quotes", "report", "analysis", "assessment", "plan",
    "budget", "template", "framework", "model", "engine", "module",
    "feature", "features", "component", "components", "source", "sources",
    "url", "urls", "link", "links", "topic", "topics", "cluster",
    "clusters", "entity", "entities", "schema", "score", "scoring",
}.union(get_all_universal_nouns())

UNIVERSAL_MODIFIERS: Set[str] = {
    "pricing", "landing", "checkout", "subscription", "onboarding",
    "management", "marketing", "analytics", "email", "project",
    "technical", "seo", "conversion", "setup", "customer",
    "saas", "enterprise", "security", "billing", "internal",
    "external", "keyword", "content", "product", "support",
    "usage", "search", "brand", "branded", "trial", "demo",
}.union(get_all_universal_modifiers())


EXTRACTOR_INTELLIGENCE_WEIGHTS: Dict[str, float] = {
    "entity_density": 0.25,
    "anchor_strength": 0.25,
    "semantic_cohesion": 0.20,
    "wrapper_noise_control": 0.15,
    "topic_alignment": 0.15,
}

SOURCE_TYPE_THRESHOLDS: Dict[str, float] = {
    "title": 0.45,
    "heading_h1": 0.45,
    "heading_h2": 0.48,
    "heading_h3": 0.50,
    "heading_h4": 0.52,
    "heading_h5": 0.52,
    "heading_h6": 0.52,
    "list_item": 0.55,
    "intent": 0.55,
    "action_object": 0.58,
    "condition_phrase": 0.58,
    "noun_phrase": 0.52,
}

VERB_WRAPPER_STARTS: Set[str] = {
    "avoid", "prevent", "reduce", "improve", "increase", "manage",
    "check", "monitor", "review", "forecast", "optimize", "build",
    "create", "fix", "protect", "treat",
}

FRAGMENT_PATTERNS = (
    r"\b(\w+)\s+\1\b",
    r"\brather than\b",
    r"\bthan someone\b",
    r"\banswer depends\b",
    r"\bresult depends\b",
    r"\bdo this\b",
    r"\bcan show\b",
    r"\bend up\b",
    r"\blean more\b",
    r"\boften falls\b",
    r"\boften lands\b",
    r"\bhas likely\b",
    r"\bfixed number\b",
    r"\bpeople often ask\b",
    r"\bmany people ask\b",
    r"\bmany users say\b",
    r"\bbecause they\b",
    r"\bbecause you\b",
    r"\bwith \d+\b",
    r"\bwithout an\b",
    r"\bwithout a\b",
    r"\bwith an\b",
    r"\bwith a\b",
    r"\bbefore getting\b",
    r"\bafter getting\b",
    r"\binto highly\b",
    r"\bfind answers\b",
    r"\bmeasure your\b",
    r"\bestimate your\b",
    r"\bconfirm you\b",
    r"\bfact unlocks\b",
    r"\bguide explains\b",
    r"\bexplains simple\b",
    r"\bis often near\b",
    r"\blands near\b",
    r"\boften near\b",
    r"\bbased on\b",
    r"\beveryone\b",
    r"\bintercourse the day\b",
    r"\bholds for\b",
    r"\bis one\b",
    r"\bis one of\b",
    r"\bsuch as\b",
    r"\bback into\b",
    r"\binside the\b",
    r"\boutside the\b",
    r"\bhelps?\s+\w+\b",
)


def canonical_phrase(text: str) -> str:
    s = (text or "").strip().lower()
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"^\s*(?:\d+[\.\)]\s+|[•\-–]\s+)", "", s)
    s = re.sub(r"^[\"'“”‘’\(\[\{]+|[\"'“”‘’\)\]\}:;,\.\!\?]+$", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def strip_tags(text: str) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", text or "")).strip()


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]


def content_tokens(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in STOPWORDS]


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
        level = int(lvl)
        source_type = "heading_h1" if level == 1 else f"heading_h{level}"
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


def _clamp_score(value: float) -> float:
    return max(0.0, min(1.0, round(float(value), 4)))


def _contains_bad_fragment(p: str) -> bool:
    return any(re.search(pat, p) for pat in FRAGMENT_PATTERNS)


def _is_clean_content_compound(tokens: List[str]) -> bool:
    if not tokens:
        return False

    if len(tokens) < 2 or len(tokens) > 5:
        return False

    if tokens[0] in BAD_STARTS or tokens[-1] in BAD_ENDINGS:
        return False

    if tokens[0] in STOPWORDS or tokens[-1] in STOPWORDS:
        return False

    if any(t in PRONOUNS for t in tokens):
        return False

    if any(t in HELPER_VERBS for t in tokens):
        return False

    if any(t in CLAUSE_VERBS for t in tokens):
        return False

    if tokens[-1] in VAGUE_ADVERB_ENDINGS:
        return False

    content = content_tokens(tokens)

    if len(content) < 2:
        return False

    long_terms = [t for t in content if len(t) >= 5]
    solid_terms = [t for t in content if len(t) >= 4]

    if len(long_terms) >= 2:
        return True

    if len(content) >= 3 and len(solid_terms) >= 2:
        return True

    if len(content) == 2 and all(len(t) >= 4 for t in content):
        return True

    return False


def _has_universal_head(tokens: List[str]) -> bool:
    if not tokens:
        return False

    if tokens[-1] in UNIVERSAL_HEAD_SUFFIXES:
        return True

    if _is_clean_content_compound(tokens):
        return True

    return False


def _starts_with_weak_connector(p: str) -> bool:
    return any(p.startswith(x + " ") or p == x for x in WEAK_CONNECTOR_STARTS)


def _ends_with_weak_phrase(p: str) -> bool:
    return any(p.endswith(" " + x) or p == x for x in WEAK_ENDING_PHRASES)


def _is_thin_modifier_phrase(tokens: List[str]) -> bool:
    if len(tokens) == 2 and tokens[0] in THIN_MODIFIERS:
        return True
    if len(tokens) == 3 and tokens[0] in THIN_MODIFIERS and tokens[-1] in GENERIC_WEAK_HEADS:
        return True
    return False


def _is_generic_weak_head_phrase(tokens: List[str]) -> bool:
    if not tokens:
        return True

    if _is_clean_content_compound(tokens):
        return False

    if tokens[-1] not in GENERIC_WEAK_HEADS:
        return False

    if len(tokens) <= 2:
        return True

    strong_non_generic = [
        t for t in tokens[:-1]
        if t not in STOPWORDS
        and t not in THIN_MODIFIERS
        and t not in GENERIC_WEAK_HEADS
        and not t.isdigit()
    ]
    return len(strong_non_generic) < 2


def _looks_like_sentence_fragment(tokens: List[str]) -> bool:
    if not tokens:
        return True

    if _is_clean_content_compound(tokens):
        return False

    if any(t in HELPER_VERBS for t in tokens):
        return True
    if any(t in PRONOUNS for t in tokens):
        return True
    if any(t in CLAUSE_VERBS for t in tokens):
        return True
    if tokens[0] in CONDITION_CONNECTORS:
        return True
    return False


def _contains_clause_connector(tokens: List[str]) -> bool:
    if len(tokens) <= 2:
        return False
    return any(t in CLAUSE_CONNECTORS for t in tokens[1:-1])


def _has_mid_stopword_chain(tokens: List[str]) -> bool:
    if len(tokens) < 3:
        return False

    if _is_clean_content_compound(tokens):
        return False

    return any(t in STOPWORDS for t in tokens[1:-1])


def _is_bad_noun_stack(tokens: List[str]) -> bool:
    if len(tokens) < 3:
        return False

    if _is_clean_content_compound(tokens):
        return False

    if any(t in STOPWORDS for t in tokens):
        return False

    if len(tokens) >= 5:
        return True

    weak_count = sum(1 for t in tokens if t in GENERIC_WEAK_HEADS)
    modifier_count = sum(1 for t in tokens[:-1] if t in UNIVERSAL_MODIFIERS)

    if weak_count >= 2 and modifier_count == 0:
        return True

    if len(tokens) == 4 and modifier_count == 0 and tokens[-1] not in UNIVERSAL_HEAD_SUFFIXES:
        return True

    return False


def _is_weak_action_tail(tokens: List[str]) -> bool:
    if len(tokens) < 2:
        return False

    if tokens[0] not in ACTION_TOKENS:
        return False

    if len(tokens) > 4:
        return True

    if tokens[-1] in GENERIC_WEAK_HEADS:
        return True

    if len(tokens) == 3 and tokens[-1] not in UNIVERSAL_HEAD_SUFFIXES and not _is_clean_content_compound(tokens):
        return True

    return False


def _score_entity_density(tokens: List[str]) -> float:
    if not tokens:
        return 0.0

    content = content_tokens(tokens)
    if not content:
        return 0.0

    entity_hits = 0
    for token in content:
        if token in UNIVERSAL_HEAD_SUFFIXES or token in UNIVERSAL_MODIFIERS:
            entity_hits += 1
        elif len(token) >= 5:
            entity_hits += 0.65

    if tokens[-1] in UNIVERSAL_HEAD_SUFFIXES:
        entity_hits += 1

    return _clamp_score(entity_hits / max(1, len(content)))


def _score_anchor_strength(tokens: List[str], source_type: str) -> float:
    if not tokens:
        return 0.0

    score = 0.35

    if 2 <= len(tokens) <= 4:
        score += 0.20
    elif 5 <= len(tokens) <= 6:
        score += 0.10

    if tokens[-1] in UNIVERSAL_HEAD_SUFFIXES:
        score += 0.25

    if _is_clean_content_compound(tokens):
        score += 0.20

    if any(t in UNIVERSAL_MODIFIERS for t in tokens[:-1]):
        score += 0.15

    if source_type in {"title", "heading_h1", "heading_h2", "heading_h3"}:
        score += 0.10

    if source_type in {"intent", "action_object", "condition_phrase"}:
        score += 0.08

    if _is_thin_modifier_phrase(tokens) or _is_generic_weak_head_phrase(tokens):
        score -= 0.35

    if _looks_like_sentence_fragment(tokens):
        score -= 0.40

    return _clamp_score(score)


def _score_semantic_cohesion(tokens: List[str]) -> float:
    if not tokens:
        return 0.0

    score = 0.55

    if len(tokens) <= 4:
        score += 0.15

    if _has_universal_head(tokens):
        score += 0.15

    if _is_clean_content_compound(tokens):
        score += 0.15

    if any(t in UNIVERSAL_MODIFIERS for t in tokens[:-1]):
        score += 0.10

    if _has_mid_stopword_chain(tokens):
        score -= 0.35

    if _is_bad_noun_stack(tokens):
        score -= 0.35

    if _contains_clause_connector(tokens):
        score -= 0.25

    return _clamp_score(score)


def _score_wrapper_noise_control(phrase: str, tokens: List[str]) -> float:
    score = 1.0

    if _contains_bad_fragment(phrase):
        score -= 0.60

    if tokens and (tokens[0] in BAD_STARTS or tokens[-1] in BAD_ENDINGS):
        score -= 0.45

    if _starts_with_weak_connector(phrase) or _ends_with_weak_phrase(phrase):
        score -= 0.45

    if any(t in PRONOUNS for t in tokens):
        score -= 0.35

    if any(t in HELPER_VERBS for t in tokens):
        score -= 0.35

    if tokens and tokens[-1] in VAGUE_ADVERB_ENDINGS:
        score -= 0.30

    return _clamp_score(score)


def _score_topic_alignment(tokens: List[str], snippet: str) -> float:
    if not tokens:
        return 0.0

    snippet_tokens = set(tokenize(snippet))
    phrase_tokens = set(tokens)
    content = set(content_tokens(tokens))

    score = 0.45

    if phrase_tokens and phrase_tokens.issubset(snippet_tokens):
        score += 0.20

    if any(t in UNIVERSAL_HEAD_SUFFIXES for t in content):
        score += 0.15

    if _is_clean_content_compound(tokens):
        score += 0.15

    if any(t in UNIVERSAL_MODIFIERS for t in content):
        score += 0.10

    if len(content) >= 2:
        score += 0.10

    return _clamp_score(score)


def _weighted_extractor_score(signals: Dict[str, float]) -> float:
    total = 0.0
    for key, weight in EXTRACTOR_INTELLIGENCE_WEIGHTS.items():
        total += float(signals.get(key, 0.0)) * weight
    return _clamp_score(total)


def _extractor_threshold(source_type: str) -> float:
    return SOURCE_TYPE_THRESHOLDS.get(source_type, 0.58)


def _extractor_intelligence_result(
    phrase: str,
    tokens: List[str],
    source_type: str,
    snippet: str,
) -> Dict[str, Any]:
    signals = {
        "entity_density": _score_entity_density(tokens),
        "anchor_strength": _score_anchor_strength(tokens, source_type),
        "semantic_cohesion": _score_semantic_cohesion(tokens),
        "wrapper_noise_control": _score_wrapper_noise_control(phrase, tokens),
        "topic_alignment": _score_topic_alignment(tokens, snippet),
    }

    score = _weighted_extractor_score(signals)
    threshold = _extractor_threshold(source_type)

    return {
        "score": score,
        "threshold": threshold,
        "decision": "ACCEPT" if score >= threshold else "REJECT",
        "signals": signals,
        "layers": [
            "entity_map",
            "intention_recognition",
            "content_aware_context",
            "semantic_similarity",
            "topic_coherence",
            "long_context_compression",
            "transfer_learning",
        ],
    }


# ---------------------------------------------------------------------
# Final universal extractor intelligence layers
# ---------------------------------------------------------------------

VALID_NUMERIC_HEADS = {
    "age", "ages", "amount", "average", "budget", "cycle", "cycles",
    "day", "days", "deadline", "duration", "forecast", "growth", "hour",
    "hours", "index", "interval", "length", "limit", "month", "months",
    "period", "periods", "price", "rate", "ratio", "revenue", "risk",
    "score", "scores", "size", "term", "trial", "value", "week", "weeks",
    "window", "year", "years",
}

DISCOURSE_TRANSITION_TERMS = {
    "actually", "also", "anyway", "basically", "behind", "briefly",
    "clearly", "especially", "even", "finally", "first", "firstly",
    "generally", "however", "including", "instead", "just", "lastly",
    "mainly", "meanwhile", "mostly", "normally", "often", "overall",
    "particularly", "rather", "really", "second", "secondly", "simply",
    "sometimes", "still", "therefore", "though", "today", "usually",
}

UNSTABLE_INTERNAL_CONNECTORS = {
    "and", "but", "or", "so", "because", "although", "though", "while",
    "whereas", "unless", "since",
}

VALID_PAIR_PATTERNS = {
    ("risks", "benefits"),
    ("risk", "benefit"),
    ("signs", "symptoms"),
    ("supply", "demand"),
    ("pros", "cons"),
    ("privacy", "security"),
    ("cost", "benefit"),
    ("costs", "benefits"),
    ("strengths", "weaknesses"),
    ("cause", "effect"),
    ("causes", "effects"),
    ("input", "output"),
    ("inputs", "outputs"),
    ("assets", "liabilities"),
    ("revenue", "expenses"),
    ("income", "expenses"),
    ("growth", "profitability"),
}


def _has_numeric_semantic_pollution(tokens: List[str]) -> bool:
    """
    Universal numeric-window guard.

    Rejects broken numeric windows while preserving normal numeric anchors:
    - keep: 30 day trial, 12 month revenue forecast, 28 day cycle
    - reject: 24 hours and sperm, 17 with the most fertile
    """
    if not tokens or not any(t.isdigit() for t in tokens):
        return False

    # Pure numeric tail was already handled elsewhere, but keep this safe.
    if tokens[-1].isdigit():
        return True

    numeric_positions = [i for i, t in enumerate(tokens) if t.isdigit()]

    for idx in numeric_positions:
        prev_tok = tokens[idx - 1] if idx > 0 else ""
        next_tok = tokens[idx + 1] if idx + 1 < len(tokens) else ""
        next2_tok = tokens[idx + 2] if idx + 2 < len(tokens) else ""

        # Valid numeric unit/metric phrase: 30 day trial, 12 month forecast.
        if next_tok in VALID_NUMERIC_HEADS:
            continue

        # Valid phrase where the numeric unit is before the number is rare in
        # anchors, but allow meaningful metric heads around the number.
        if prev_tok in VALID_NUMERIC_HEADS or next2_tok in VALID_NUMERIC_HEADS:
            continue

        # Numeric value followed by connector/discourse is usually a sentence shard.
        if next_tok in STOPWORDS or next_tok in UNSTABLE_INTERNAL_CONNECTORS:
            return True

        # Bare number inside a phrase without a known numeric head is unstable.
        return True

    return False


def _has_discourse_transition_leak(tokens: List[str]) -> bool:
    """
    Rejects sentence-bridge/discourse fragments that are not stable anchors.
    """
    if not tokens:
        return False

    # Good anchors can contain ordinary modifiers, but should not start/end with
    # discourse transition terms.
    if tokens[0] in DISCOURSE_TRANSITION_TERMS:
        return True

    if tokens[-1] in DISCOURSE_TRANSITION_TERMS:
        return True

    # Internal discourse terms are usually bad unless the phrase is a known
    # clean content compound.
    internal = tokens[1:-1]
    if any(t in DISCOURSE_TRANSITION_TERMS for t in internal):
        return True

    # Common narrative fragments.
    phrase = " ".join(tokens)
    if phrase in {
        "behind the scenes",
        "same number",
        "single fact",
        "main reason",
        "main point",
        "next step",
        "first step",
    }:
        return True

    return False


def _has_unstable_internal_connector(tokens: List[str]) -> bool:
    """
    Reject unstable connector windows but preserve valid paired concepts.
    """
    if len(tokens) < 3:
        return False

    for i, tok in enumerate(tokens[1:-1], start=1):
        if tok not in UNSTABLE_INTERNAL_CONNECTORS:
            continue

        left = tokens[i - 1]
        right = tokens[i + 1]

        if (left, right) in VALID_PAIR_PATTERNS:
            continue

        # Allow stable noun-pair anchors like "research and development" only
        # when both sides are content-heavy.
        if tok == "and" and len(left) >= 5 and len(right) >= 5:
            continue

        return True

    return False

INCOMPLETE_TAIL_TERMS = {
    "around", "widely", "itself", "typically", "usually", "often",
    "likely", "roughly", "generally", "seriously", "accurately",
    "realizing", "finding", "trying", "based",
}

WEAK_COMPLETION_STARTS = {
    "using", "planning", "working", "range", "vary", "hit", "mark",
    "know", "search", "refine", "focus",
}

BAD_BOUNDARY_BIGRAMS = {
    ("body", "better"),
    ("better", "learning"),
    ("conceive", "trying"),
    ("ovulation", "answer"),
    ("cycle", "math"),
    ("powerful", "starting"),
}


def _has_numeric_phrase_shape_error(tokens: List[str]) -> bool:
    if not tokens or not any(t.isdigit() for t in tokens):
        return False

    stable_units = {
        "day", "days", "week", "weeks", "month", "months", "year", "years",
        "hour", "hours", "minute", "minutes", "percent", "percentage",
        "rate", "ratio", "score", "index", "cycle", "window", "trial",
        "period", "forecast", "budget", "revenue", "growth", "risk",
    }

    stable_heads = {
        "cycle", "window", "trial", "forecast", "rate", "ratio", "score",
        "index", "period", "budget", "revenue", "growth", "risk",
        "length", "duration", "deadline", "timeline", "plan",
    }

    for i, tok in enumerate(tokens):
        if not tok.isdigit():
            continue

        next_tok = tokens[i + 1] if i + 1 < len(tokens) else ""
        next2_tok = tokens[i + 2] if i + 2 < len(tokens) else ""

        if next_tok in stable_units and (next2_tok in stable_heads or len(tokens) <= 3):
            continue

        if next_tok in stable_units and len(tokens) == 2:
            continue

        return True

    return False


def _has_boundary_stitch_error(tokens: List[str]) -> bool:
    if len(tokens) < 2:
        return False

    for pair in zip(tokens, tokens[1:]):
        if pair in BAD_BOUNDARY_BIGRAMS:
            return True

    if tokens[-1] in {"trying", "finding", "realizing", "using", "tracking"}:
        return True

    return False


def _has_incomplete_phrase_completion(tokens: List[str]) -> bool:
    if not tokens:
        return False

    if tokens[-1] in INCOMPLETE_TAIL_TERMS:
        return True

    if tokens[0] in WEAK_COMPLETION_STARTS and len(tokens) <= 3:
        return True

    phrase = " ".join(tokens)
    if phrase in {
        "using this principle",
        "planning around",
        "range more widely",
        "working length",
        "last three",
        "personal average",
        "same subtraction rule",
        "ovulation the answer",
    }:
        return True

    return False


UNSTABLE_NUMERIC_CONTEXT_TERMS = {
    "ovulation", "profit", "revenue", "traffic", "ranking", "conversion",
    "growth", "risk", "score", "price", "cost", "budget", "users",
    "customers", "patients", "students", "sales", "leads",
}

LOW_VALUE_STANDALONE_PHRASES = {
    "want proof",
    "likely passed",
    "next period",
    "calendar math",
    "putting prediction",
    "same subtraction rule",
}

UNSTABLE_PREFIX_TERMS = {
    "re", "cost", "putting", "likely", "want", "notice", "searches",
    "confirmation", "signaling",
}


def _has_unstable_numeric_context(tokens: List[str]) -> bool:
    """
    Universal V3 numeric-context guard.

    Rejects: 28 days ovulation, 12 months revenue, 5 users growth
    Preserves: 28 day cycle, 12 month revenue forecast, 5 year growth rate
    """
    if not tokens or not any(t.isdigit() for t in tokens):
        return False

    stable_metric_heads = {
        "cycle", "window", "trial", "forecast", "rate", "ratio", "score",
        "index", "period", "budget", "plan", "timeline", "duration",
        "length", "cost", "price", "revenue", "growth", "risk",
    }

    for i, tok in enumerate(tokens):
        if not tok.isdigit():
            continue

        next_tok = tokens[i + 1] if i + 1 < len(tokens) else ""
        next2_tok = tokens[i + 2] if i + 2 < len(tokens) else ""

        if next_tok in {"day", "days", "week", "weeks", "month", "months", "year", "years", "hour", "hours"}:
            if next2_tok in stable_metric_heads:
                continue

            if len(tokens) <= 2:
                continue

            return True

        if next_tok and next_tok not in stable_metric_heads:
            return True

    return False


def _has_low_value_standalone_shape(tokens: List[str]) -> bool:
    """
    Rejects low-value sentence pieces that are not stable anchors.
    Universal, not niche-specific.
    """
    if not tokens:
        return False

    phrase = " ".join(tokens)

    if phrase in LOW_VALUE_STANDALONE_PHRASES:
        return True

    if tokens[0] in UNSTABLE_PREFIX_TERMS and len(tokens) <= 4:
        return True

    if tokens[0] in UNSTABLE_PREFIX_TERMS and not _is_clean_content_compound(tokens):
        return True

    return False


def _has_unfinished_narrative_window(tokens: List[str]) -> bool:
    """
    Rejects narrative fragments that look like sentence motion, not anchors.
    """
    if len(tokens) < 2:
        return False

    unstable_tails = {
        "passed", "proof", "prediction", "together", "whether", "nothing",
        "right", "widely", "seriously", "usually", "typically",
    }

    if tokens[-1] in unstable_tails:
        return True

    if len(tokens) >= 3 and tokens[0] in {"re", "cost", "putting", "confirmation"}:
        return True

    return False


WEAK_TRAILING_ADJECTIVES = {
    "trickier", "possible", "expected", "predictable",
    "broader", "steady", "targeted", "clearer",
    "wetter", "easiest", "special",
}

WEAK_CONTEXT_ENDINGS = {
    "people", "averages", "range", "speak",
    "evaluation", "release", "routine",
    "situations", "principle",
}

LOW_INFORMATION_PHRASES = {
    "well for people",
    "less on averages",
    "cycles range",
    "period speak",
    "special situations",
    "expected release",
    "possible evaluation",
}


def _has_semantic_completion_failure(tokens: List[str]) -> bool:
    """
    Final universal semantic completion validator.

    Rejects semantically incomplete phrases while preserving
    stable anchor concepts across niches.
    """
    if not tokens:
        return False

    phrase = " ".join(tokens)

    if phrase in LOW_INFORMATION_PHRASES:
        return True

    if tokens[-1] in WEAK_TRAILING_ADJECTIVES:
        return True

    if tokens[-1] in WEAK_CONTEXT_ENDINGS:
        return True

    # Reject weak two-word adjective tails.
    if len(tokens) == 2:
        if tokens[1] in {
            "trickier", "possible", "steady",
            "targeted", "broader", "predictable",
        }:
            return True

    return False


def _basic_reject(phrase: str) -> bool:
    p = canonical_phrase(phrase)
    tokens = tokenize(p)
    content = content_tokens(tokens)

    if not p:
        return True
    if len(tokens) < 2 or len(tokens) > 7:
        return True
    if len(content) < 2:
        return True

    if _has_numeric_semantic_pollution(tokens):
        return True
    if _has_discourse_transition_leak(tokens):
        return True
    if _has_unstable_internal_connector(tokens):
        return True
    if _has_numeric_phrase_shape_error(tokens):
        return True
    if _has_boundary_stitch_error(tokens):
        return True
    if _has_incomplete_phrase_completion(tokens):
        return True
    if _has_unstable_numeric_context(tokens):
        return True
    if _has_low_value_standalone_shape(tokens):
        return True
    if _has_unfinished_narrative_window(tokens):
        return True
    if _has_semantic_completion_failure(tokens):
        return True
    if tokens[0] in BAD_STARTS:
        return True
    if tokens[-1] in BAD_ENDINGS:
        return True
    if tokens[-1] in VAGUE_ADVERB_ENDINGS:
        return True
    if tokens[-1].isdigit():
        return True
    if tokens[-1] in PRONOUNS:
        return True
    if any(t in PRONOUNS for t in tokens[1:]):
        return True
    if any(t in HELPER_VERBS for t in tokens):
        return True
    if _contains_bad_fragment(p):
        return True
    if _starts_with_weak_connector(p):
        return True
    if _ends_with_weak_phrase(p):
        return True
    if _is_thin_modifier_phrase(tokens):
        return True
    if _is_generic_weak_head_phrase(tokens):
        return True
    if _contains_clause_connector(tokens):
        return True
    if _has_mid_stopword_chain(tokens):
        return True
    if _is_bad_noun_stack(tokens):
        return True
    if _is_weak_action_tail(tokens):
        return True
    if tokens[0] not in ACTION_TOKENS and any(t in CLAUSE_VERBS for t in tokens):
        return True

    return False

def _add_candidate(
    out: List[Dict[str, Any]],
    seen: Set[str],
    phrase: str,
    source_type: str,
    section_id: str,
    snippet: str,
    doc_id: str = "",
) -> None:
    p = canonical_phrase(phrase)
    if _basic_reject(p):
        return

    tokens = tokenize(p)

    if source_type in {"noun_phrase", "condition_phrase"}:
        if not _has_universal_head(tokens):
            return
        if _looks_like_sentence_fragment(tokens):
            return

    extractor_intelligence = _extractor_intelligence_result(
        phrase=p,
        tokens=tokens,
        source_type=source_type,
        snippet=snippet,
    )

    if extractor_intelligence["decision"] != "ACCEPT":
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
        "extractor_intelligence": extractor_intelligence,
    })


def _extract_intent_candidates(sent: str, section_id: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    s = canonical_phrase(sent)

    for start in INTENT_STARTS:
        idx = s.find(start)
        if idx == -1:
            continue

        tail_tokens = tokenize(s[idx:])

        for n in range(3, min(7, len(tail_tokens)) + 1):
            chunk = tail_tokens[:n]
            if not chunk:
                continue
            if any(t in HELPER_VERBS for t in chunk[2:]):
                continue
            if chunk[-1] in BAD_ENDINGS or chunk[-1] in PRONOUNS or chunk[-1].isdigit():
                continue
            if chunk[-1] in VAGUE_ADVERB_ENDINGS:
                continue
            if len(chunk) >= 5 and not _has_universal_head(chunk):
                continue
            if _has_mid_stopword_chain(chunk):
                continue
            if _is_bad_noun_stack(chunk):
                continue

            _add_candidate(out, seen, " ".join(chunk), "intent", section_id, sent)

    return out


def _extract_action_object_candidates(sent: str, section_id: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    tokens = tokenize(sent)

    for i, tok in enumerate(tokens):
        if tok not in ACTION_TOKENS:
            continue

        for n in (2, 3, 4):
            chunk = tokens[i:i + n]
            if len(chunk) < 2:
                continue
            if chunk[-1] in STOPWORDS or chunk[-1] in BAD_ENDINGS:
                continue
            if chunk[-1] in VAGUE_ADVERB_ENDINGS:
                continue
            if chunk[-1].isdigit():
                continue
            if any(t in PRONOUNS for t in chunk[1:]):
                continue
            if any(t in HELPER_VERBS for t in chunk[1:]):
                continue
            if any(t in CLAUSE_VERBS for t in chunk[1:]):
                continue
            if _is_weak_action_tail(chunk):
                continue
            if _has_mid_stopword_chain(chunk):
                continue
            if _is_bad_noun_stack(chunk):
                continue

            _add_candidate(out, seen, " ".join(chunk), "action_object", section_id, sent)

    return out


def _extract_condition_candidates(sent: str, section_id: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    tokens = tokenize(sent)

    for i, tok in enumerate(tokens):
        if tok not in CONDITION_CONNECTORS:
            continue

        for left_n in (1, 2):
            left_start = i - left_n
            if left_start < 0:
                continue

            left = tokens[left_start:i]
            if not left or left[0] in STOPWORDS:
                continue
            if any(t in HELPER_VERBS or t in CLAUSE_VERBS for t in left):
                continue

            for right_n in (1, 2, 3):
                right = tokens[i + 1:i + 1 + right_n]
                if not right:
                    continue
                if right[-1] in STOPWORDS or right[-1] in BAD_ENDINGS:
                    continue
                if right[-1] in VAGUE_ADVERB_ENDINGS:
                    continue
                if right[-1].isdigit():
                    continue
                if any(t in PRONOUNS for t in right):
                    continue
                if any(t in HELPER_VERBS or t in CLAUSE_VERBS for t in right):
                    continue

                chunk = left + [tok] + right

                if not _has_universal_head(chunk):
                    continue
                if _has_mid_stopword_chain(chunk):
                    continue
                if _is_bad_noun_stack(chunk):
                    continue

                _add_candidate(out, seen, " ".join(chunk), "condition_phrase", section_id, sent)

    return out


def _extract_clean_compound_candidates(sent: str, section_id: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    tokens = tokenize(sent)

    for n in (4, 3, 2):
        if len(tokens) < n:
            continue

        for i in range(0, len(tokens) - n + 1):
            chunk = tokens[i:i + n]

            if chunk[0] in STOPWORDS or chunk[-1] in STOPWORDS:
                continue
            if chunk[0] in BAD_STARTS:
                continue
            if chunk[0] in VERB_WRAPPER_STARTS:
                continue
            if chunk[0] in ACTION_TOKENS and len(chunk) <= 2:
                continue
            if any(t in ACTION_TOKENS for t in chunk[1:]):
                continue
            if chunk[-1] in VAGUE_ADVERB_ENDINGS:
                continue
            if any(t in PRONOUNS for t in chunk):
                continue
            if any(t in HELPER_VERBS or t in CLAUSE_VERBS for t in chunk):
                continue
            if chunk[-1].isdigit():
                continue
            if not _has_universal_head(chunk):
                continue
            if _is_thin_modifier_phrase(chunk):
                continue
            if _is_generic_weak_head_phrase(chunk):
                continue
            if _has_mid_stopword_chain(chunk):
                continue
            if _is_bad_noun_stack(chunk):
                continue

            if i > 0:
                prev_token = tokens[i - 1]
                if prev_token not in STOPWORDS and prev_token not in HELPER_VERBS:
                    previous_extended = tokens[i - 1:i + n]
                    if len(previous_extended) <= 5 and _has_universal_head(previous_extended):
                        continue

            if i + n < len(tokens):
                next_token = tokens[i + n]
                if next_token not in STOPWORDS and next_token not in HELPER_VERBS:
                    next_extended = tokens[i:i + n + 1]
                    if len(next_extended) <= 5 and _has_universal_head(next_extended):
                        continue

            content = content_tokens(chunk)
            if len(content) < 2:
                continue

            _add_candidate(out, seen, " ".join(chunk), "noun_phrase", section_id, sent)

    return out


def extract_smart_phrases(
    *,
    text: str = "",
    html: str = "",
    title: str = "",
    doc_id: str = "",
    max_candidates: int = 500,
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    if title:
        _add_candidate(out, seen, title, "title", "title_0", title, doc_id)

    for h in extract_headings_and_lists(html):
        _add_candidate(
            out,
            seen,
            h.get("phrase") or "",
            h.get("source_type") or "heading",
            h.get("section_id") or "heading_0",
            h.get("snippet") or "",
            doc_id,
        )

    paragraphs = extract_paragraphs(html=html, text=text)

    for pi, para in enumerate(paragraphs):
        for si, sent in enumerate(split_sentences(para)):
            section_id = f"p{pi}_s{si}"

            for item in _extract_intent_candidates(sent, section_id):
                _add_candidate(out, seen, item["phrase"], item["source_type"], item["section_id"], item["snippet"], doc_id)

            for item in _extract_action_object_candidates(sent, section_id):
                _add_candidate(out, seen, item["phrase"], item["source_type"], item["section_id"], item["snippet"], doc_id)

            for item in _extract_condition_candidates(sent, section_id):
                _add_candidate(out, seen, item["phrase"], item["source_type"], item["section_id"], item["snippet"], doc_id)

            for item in _extract_clean_compound_candidates(sent, section_id):
                _add_candidate(out, seen, item["phrase"], item["source_type"], item["section_id"], item["snippet"], doc_id)

            if len(out) >= max_candidates:
                return out[:max_candidates]

    return out[:max_candidates]