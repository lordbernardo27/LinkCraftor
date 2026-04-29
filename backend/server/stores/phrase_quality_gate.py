from __future__ import annotations

import re
from typing import Any, Dict, List, Set, Tuple


WORD_RE = re.compile(r"[a-z0-9][a-z0-9\-']*", re.I)


STOPWORDS: Set[str] = {
    "the", "and", "for", "with", "that", "this", "from", "into", "your", "you",
    "are", "was", "were", "will", "can", "could", "should", "would", "have",
    "has", "had", "about", "over", "under", "than", "then", "when", "what",
    "where", "which", "who", "whom", "why", "how", "a", "an", "to", "of",
    "in", "on", "at", "by", "or", "as", "is", "it", "be", "not", "no",
    "if", "but", "so", "because", "after", "before", "during", "while",
    "through", "up", "down", "out", "off", "too", "very", "also",
}

HELPER_VERBS: Set[str] = {
    "is", "are", "was", "were", "be", "being", "been", "am",
    "can", "could", "will", "would", "should", "may", "might",
    "has", "have", "had", "do", "does", "did",
}

PRONOUNS: Set[str] = {
    "you", "your", "yours", "they", "them", "their", "theirs", "it", "its",
    "we", "us", "our", "ours", "he", "she", "him", "her", "his", "hers",
    "this", "that", "these", "those",
}

NARRATIVE_VERBS: Set[str] = {
    "use", "using", "include", "including", "notice", "mark", "say", "says",
    "said", "let", "know", "like", "search", "searches", "raise", "raises",
    "span", "spans", "stretch", "stretches", "avoid", "trying", "get",
    "count", "counts", "identify", "convert", "vary", "working", "appears",
    "appear", "means", "mean", "depends", "depend", "offers", "offer",
    "creates", "create", "helps", "help", "uses", "works", "go", "goes",
    "make", "makes", "made", "take", "takes", "taken",
}

ACTION_STARTS: Set[str] = {
    "create", "review", "reduce", "increase", "improve", "treat", "send",
    "define", "launch", "move", "paying", "grow", "adjust", "adjusts",
    "combine", "build", "fix", "write", "design", "analyze", "monitor",
}

BAD_STARTS: Set[str] = {
    "whether", "rather", "than", "without", "with", "into", "from", "for",
    "to", "at", "on", "by", "if", "while", "so", "then", "this", "that",
    "these", "those", "your", "many", "people", "because", "and", "or",
    "often", "still", "just", "as", "using", "including", "notice", "mark",
    "says", "let", "know", "like", "approach", "search", "searches",
    "count", "counts", "understanding", "useful", "helpful", "strongest",
}

BAD_ENDINGS: Set[str] = {
    "at", "with", "without", "than", "rather", "into", "from", "for", "to",
    "by", "if", "when", "while", "so", "then", "and", "or", "but", "the",
    "your", "someone", "this", "that", "depends", "changes", "ask", "an",
    "a", "because", "about", "before", "after", "during", "through",
    "last", "much", "main", "one", "of", "most", "near", "safe", "same",
    "later", "right", "schedule", "accordingly", "instead", "such",
}

WEAK_TOKENS: Set[str] = {
    "guesswork", "someone", "rather", "whether", "thing", "things", "stuff",
    "people", "ask", "many", "result", "depends", "answer", "changes",
    "maybe", "probably", "simply", "basically",     "risk", "risks", "reality", "monthly", "teams",
}

WEAK_HEADS: Set[str] = {
    "thing", "things", "stuff", "way", "ways", "area", "areas",
    "part", "parts", "result", "results", "question", "answer",
    "idea", "ideas", "reality", "value", "growth", "team", "teams",
    "people", "person", "many", "most", "later", "today", "tomorrow",
    "yesterday", "someone", "everyone", "everything", "anything",
}

GENERIC_MODIFIERS: Set[str] = {
    "exact", "easiest", "simple", "rough", "average", "typical", "true",
    "real", "expected", "working", "first", "last", "next", "single",
    "several", "few", "many", "every", "old", "perfect", "estimated",
    "random", "common", "useful", "helpful", "strongest", "important",
}

UNIVERSAL_ANCHOR_HEADS: Set[str] = {
    # tech / SaaS / engineering
    "software", "tool", "tools", "platform", "system", "workflow", "automation",
    "integration", "pipeline", "dashboard", "api", "app", "application",
    "plugin", "extension", "database", "storage", "security", "server",
    "backend", "frontend", "architecture", "infrastructure", "latency",
    "observability", "monitoring", "alerts", "deployment", "model", "models",

    # SEO / content / marketing
    "keyword", "keywords", "content", "backlink", "audit", "optimization",
    "conversion", "page", "traffic", "ranking", "analytics", "cluster",
    "clusters", "anchor", "anchors", "schema", "crawl", "indexing",

    # finance / business
    "yield", "rate", "rates", "forecast", "tax", "reporting", "investment",
    "pricing", "price", "prices", "cost", "costs", "budget", "revenue",
    "margin", "profit", "subscription", "billing", "invoice", "finops",

    # legal / real estate
    "lease", "agreement", "contract", "review", "lawyer", "visa", "property",
    "mortgage", "insurance", "policy", "compliance", "governance",

    # ecommerce / local / travel
    "service", "services", "delivery", "menu", "reservation", "restaurant",
    "hotel", "airport", "coverage", "rental", "checkout", "cart", "product",
    "customer", "customers", "order", "orders", "inventory",

    # education / career
    "tutoring", "study", "management", "project", "practice", "questions",
    "resume", "interview", "course", "lesson", "training", "exam",

    # health / medical
    "symptoms", "causes", "treatment", "medication", "dosage", "foods",
    "antibiotics", "cream", "options", "therapy", "pain", "pressure",
    "temperature", "mucus", "cycle", "period", "fertility", "window",
    "pregnancy", "ovulation", "kits", "phase", "ultrasound", "implantation",
    "glucose", "insulin", "rash", "infection", "risk", "care",

    # general high-value heads
    "strategy", "checklist", "calculator", "guide", "benefits", "estimate",
    "routine", "collection", "trends", "quotes", "report", "analysis",
    "assessment", "plan", "quality", "discipline", "network", "networks",
    "environment", "environments",
}

STRONG_MODIFIERS: Set[str] = {
    "cloud", "cost", "internal", "external", "technical", "seo", "content",
    "customer", "pricing", "ecommerce", "medical", "health", "financial",
    "legal", "rental", "property", "blood", "sugar", "insulin", "continuous",
    "glucose", "cardiovascular", "late", "fee", "enterprise", "backend",
    "serverless", "network", "data", "storage", "reserved", "usage",
    "anomaly", "budget", "operational", "regulatory", "security", "semantic",
    "clinical", "local", "organic", "automated", "predictive", "real-time",
}

TRUSTED_SOURCE_TYPES: Set[str] = {
    "title", "heading_h1", "heading_h2", "heading_h3",
    "entity", "intent", "list_item", "sitemap_title",
    "draft_title", "draft_topic", "imported_topic",
}

INTENT_PREFIXES: Tuple[str, ...] = (
    "how to",
    "best way to",
    "best time to",
    "symptoms of",
    "signs of",
    "causes of",
    "treatment for",
    "benefits of",
    "cost of",
    "price of",
    "types of",
    "examples of",
    "side effects of",
    "risk factors for",
)

BAD_FRAGMENT_PATTERNS: Tuple[str, ...] = (
    r"\b(\w+)\s+\1\b",
    r"\brather than\b",
    r"\bthan someone\b",
    r"\banswer depends\b",
    r"\bresult depends\b",
    r"\bdepends on\b",
    r"\bdo this\b",
    r"\bcan show\b",
    r"\bend up\b",
    r"\blean more\b",
    r"\bhas likely\b",
    r"\bfixed number\b",
    r"\bpeople often ask\b",
    r"\bmany people ask\b",
    r"\bbecause they\b",
    r"\bbecause you\b",
    r"\bwith \d+\b",
    r"\bwith (a|an|the)\b",
    r"\bwithout (a|an|the)\b",
    r"\bbased on (last|this|that|these|those)\b",
    r"\b(before|after) getting\b",
    r"\bfind answers\b",
    r"\bmeasure your\b",
    r"\bestimate your\b",
    r"\bconfirm you\b",
    r"\bguide explains\b",
    r"\bexplains simple\b",
    r"\bfact unlocks\b",
    r"\bis one of\b",
    r"\bboth\s+\w+\s+and\s+\w+\b",
    r"\bfew days before that\b",
    r"\bdays before that\b",
    r"\bfinish with\b",
    r"\blater that day\b",
    r"\bsame day\b",
    r"\bright on schedule\b",
    r"\bsingle exact day\b",
    r"\bsearch for\b",
    r"\bsearches like\b",
    r"\bnumber of\b",
    r"\bidentify the\b",
    r"\btogether in\b",
)


def canonical_phrase(text: str) -> str:
    s = (text or "").strip().lower()
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"^\s*(?:\d+[\.\)]\s+|[•\-–]\s+)", "", s)
    s = re.sub(r"^[\"'“”‘’\(\[\{]+|[\"'“”‘’\)\]\}:;,\.\!\?]+$", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def tokenize(text: str) -> List[str]:
    return [t.lower().strip("-'") for t in WORD_RE.findall(text or "") if t.strip("-'")]


def content_tokens(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in STOPWORDS]


def _source_mode(source_type: str) -> str:
    source = (source_type or "").strip().lower()
    if source in TRUSTED_SOURCE_TYPES:
        return "trusted"
    if source == "intent":
        return "intent"
    return "runtime"


def _has_bad_fragment_pattern(p: str) -> bool:
    return any(re.search(pattern, p) for pattern in BAD_FRAGMENT_PATTERNS)


def _has_anchor_head(tokens: List[str]) -> bool:
    return any(t in UNIVERSAL_ANCHOR_HEADS for t in tokens)


def _head_hits(tokens: List[str]) -> int:
    return sum(1 for t in tokens if t in UNIVERSAL_ANCHOR_HEADS)


def _modifier_hits(tokens: List[str]) -> int:
    return sum(1 for t in tokens if t in STRONG_MODIFIERS)


def _is_numeric_time_phrase(tokens: List[str]) -> bool:
    if not tokens:
        return False

    number_words = {
        "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "twenty", "thirty",
    }
    time_words = {
        "day", "days", "week", "weeks", "month", "months",
        "year", "years", "hour", "hours", "minute", "minutes",
    }

    if len(tokens) == 2 and (tokens[0].isdigit() or tokens[0] in number_words) and tokens[1] in time_words:
        return True

    if (tokens[0].isdigit() or tokens[0] in number_words) and any(t in time_words for t in tokens):
        if tokens[-1] not in {"cycle", "rate", "plan", "schedule", "forecast", "estimate"}:
            return True

    return False


def _base_reject(p: str, tokens: List[str], content: List[str]) -> str:
    if not p:
        return "empty"

    if len(tokens) < 2:
        return "too_short"

    if len(tokens) > 8:
        return "too_long"

    if len(content) < 2:
        return "low_content"

    if _is_numeric_time_phrase(tokens):
        return "numeric_time_phrase"

    if tokens[0] in BAD_STARTS:
        return "bad_start"

    if tokens[-1] in BAD_ENDINGS:
        return "bad_ending"

    if tokens[-1].isdigit():
        return "number_tail"

    if tokens[-1] in PRONOUNS:
        return "pronoun_tail"

    if any(t in WEAK_TOKENS for t in tokens):
        return "weak_token"

    if _has_bad_fragment_pattern(p):
        return "fragment_pattern"

    return ""

def _runtime_lane(tokens: List[str], content: List[str]) -> Tuple[bool, str, float]:
    """
    Lane A:
    Runtime compact anchors.
    This is intentionally strict because runtime sliding windows create the most noise.
    """

    if len(tokens) < 2:
        return False, "runtime_too_short", 0.10

    if len(tokens) > 5:
        return False, "runtime_long_window", 0.20

    if any(t in STOPWORDS for t in tokens):
        return False, "runtime_contains_stopword", 0.18

    if any(t in HELPER_VERBS for t in tokens):
        return False, "runtime_helper_verb", 0.18

    if any(t in PRONOUNS for t in tokens):
        return False, "runtime_pronoun_fragment", 0.18

    if any(t in NARRATIVE_VERBS for t in tokens):
        return False, "runtime_narrative_fragment", 0.20

    if tokens[0] in ACTION_STARTS:
        return False, "runtime_action_fragment", 0.22

    if any(t in {"and", "or"} for t in tokens[1:-1]):
        return False, "runtime_connector_stack", 0.22

    if len(content) < 2:
        return False, "runtime_low_content", 0.16

    head_hits = _head_hits(tokens)
    mod_hits = _modifier_hits(tokens)
    tail = tokens[-1]

    if tail in WEAK_HEADS:
        return False, "runtime_weak_tail_head", 0.22

    if tail not in UNIVERSAL_ANCHOR_HEADS and len(tokens) <= 3:
        return False, "runtime_bad_tail_head", 0.22

    if len(tokens) >= 3 and tokens[0] not in STRONG_MODIFIERS and tokens[0] not in UNIVERSAL_ANCHOR_HEADS:
        return False, "runtime_weak_lead_token", 0.22

    if len(tokens) in {2, 3} and head_hits >= 1:
        return True, "lane_a_runtime_compact_anchor", 0.74

    if len(tokens) == 4 and head_hits >= 1 and mod_hits >= 1:
        return True, "lane_a_runtime_modifier_head_anchor", 0.78

    if len(tokens) == 5 and head_hits >= 1 and mod_hits >= 2:
        return True, "lane_a_runtime_rare_longtail_anchor", 0.76

    return False, "runtime_not_compact_anchor", 0.28


def _trusted_lane(tokens: List[str], content: List[str]) -> Tuple[bool, str, float]:
    """
    Lane B:
    Trusted source anchors.
    Titles, headings, entities, imported topics, sitemap titles, and list items may be broader.
    """

    if len(tokens) < 2:
        return False, "trusted_too_short", 0.10

    if len(tokens) > 8:
        return False, "trusted_too_long", 0.24

    if any(t in PRONOUNS for t in tokens):
        return False, "trusted_pronoun_fragment", 0.20

    if any(t in HELPER_VERBS for t in tokens):
        return False, "trusted_helper_verb", 0.22

    if any(t in NARRATIVE_VERBS for t in tokens):
        return False, "trusted_narrative_fragment", 0.22

    if len(content) < 2:
        return False, "trusted_low_content", 0.18

    head_hits = _head_hits(tokens)
    mod_hits = _modifier_hits(tokens)

    if head_hits >= 1:
        return True, "lane_b_trusted_topic_anchor", 0.72

    if len(tokens) in {2, 3, 4} and content == tokens:
        return True, "lane_b_trusted_clean_noun_phrase", 0.69

    if len(tokens) >= 5 and len(content) >= 4 and (head_hits >= 1 or mod_hits >= 1):
        return True, "lane_b_trusted_longtail_topic", 0.71

    return False, "trusted_not_anchor_worthy", 0.34


def _intent_lane(p: str, tokens: List[str], content: List[str]) -> Tuple[bool, str, float]:
    """
    Lane C:
    Controlled intent anchors.
    Accepts common search-intent phrases only when the phrase has a real object/topic.
    """

    matched = ""
    for prefix in INTENT_PREFIXES:
        if p.startswith(prefix):
            matched = prefix
            break

    if not matched:
        return False, "not_intent_phrase", 0.20

    if len(tokens) < 3:
        return False, "intent_too_short", 0.18

    if len(tokens) > 7:
        return False, "intent_too_long", 0.24

    if any(t in PRONOUNS for t in tokens):
        return False, "intent_pronoun_fragment", 0.20

    if len(content) < 2:
        return False, "intent_low_content", 0.20

    object_tokens = tokens[len(tokenize(matched)):]
    object_content = content_tokens(object_tokens)

    if len(object_content) < 1:
        return False, "intent_missing_object", 0.24

    if object_tokens and object_tokens[-1] in WEAK_HEADS:
        return False, "intent_weak_object", 0.26

    if _has_anchor_head(object_tokens) or len(object_content) >= 2:
        return True, "lane_c_intent_anchor", 0.76

    return False, "intent_not_anchor_worthy", 0.30


def _score_after_lane(
    lane_score: float,
    lane_reason: str,
    tokens: List[str],
    content: List[str],
    source_type: str,
    vertical: str,
    context: str,
    phrase: str,
) -> float:
    score = lane_score

    source = (source_type or "").strip().lower()

    if source in {"title", "heading_h1"}:
        score += 0.08
    elif source in {"heading_h2", "heading_h3", "sitemap_title", "draft_title"}:
        score += 0.06
    elif source in {"entity", "draft_topic", "imported_topic"}:
        score += 0.05
    elif source == "list_item":
        score += 0.03
    elif source in {"sentence", "runtime"}:
        score -= 0.02

    if 2 <= len(tokens) <= 4:
        score += 0.04

    if len(content) >= 3:
        score += 0.03

    if _head_hits(tokens) >= 1:
        score += 0.04

    if _modifier_hits(tokens) >= 1:
        score += 0.03

    if vertical and vertical.strip().lower() != "general":
        score += 0.02

    if context and phrase in canonical_phrase(context):
        score += 0.02

    if lane_reason.startswith("lane_a"):
        score += 0.02

    return max(0.0, min(1.0, round(score, 4)))


def classify_phrase_strength(
    phrase: str,
    source_type: str = "",
    vertical: str = "general",
    context: str = "",
) -> Dict[str, Any]:
    p = canonical_phrase(phrase)
    tokens = tokenize(p)
    content = content_tokens(tokens)
    source = (source_type or "").strip().lower()
    mode = _source_mode(source)

    base_reason = _base_reject(p, tokens, content)
    if base_reason:
        return {
            "keep": False,
            "strength": "weak",
            "score": 0.12,
            "reason": base_reason,
            "lane": "base_reject",
        }

    lane_keep = False
    lane_reason = ""
    lane_score = 0.0
    lane = ""

    intent_keep, intent_reason, intent_score = _intent_lane(p, tokens, content)

    if intent_keep:
        lane_keep = True
        lane_reason = intent_reason
        lane_score = intent_score
        lane = "C"
    elif mode == "trusted":
        lane_keep, lane_reason, lane_score = _trusted_lane(tokens, content)
        lane = "B"
    else:
        lane_keep, lane_reason, lane_score = _runtime_lane(tokens, content)
        lane = "A"

    if not lane_keep:
        return {
            "keep": False,
            "strength": "weak",
            "score": lane_score,
            "reason": lane_reason,
            "lane": lane or mode,
        }

    final_score = _score_after_lane(
        lane_score=lane_score,
        lane_reason=lane_reason,
        tokens=tokens,
        content=content,
        source_type=source,
        vertical=vertical,
        context=context,
        phrase=p,
    )

    threshold = 0.72 if lane == "A" else 0.68

    if final_score >= threshold:
        return {
            "keep": True,
            "strength": "strong",
            "score": final_score,
            "reason": lane_reason,
            "lane": lane,
        }

    return {
        "keep": False,
        "strength": "weak",
        "score": final_score,
        "reason": "below_threshold_after_lane",
        "lane": lane,
    }


def is_strong_phrase(
    phrase: str,
    source_type: str = "",
    vertical: str = "general",
    context: str = "",
) -> bool:
    return bool(
        classify_phrase_strength(
            phrase=phrase,
            source_type=source_type,
            vertical=vertical,
            context=context,
        ).get("keep")
    )