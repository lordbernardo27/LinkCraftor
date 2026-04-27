from __future__ import annotations

import re
from typing import Any, Dict, List, Set


WORD_RE = re.compile(r"[a-z0-9]{2,}", re.I)

STOPWORDS: Set[str] = {
    "the", "and", "for", "with", "that", "this", "from", "into", "your", "you",
    "are", "was", "were", "will", "can", "could", "should", "would", "have",
    "has", "had", "about", "over", "under", "than", "then", "when", "what",
    "where", "which", "who", "whom", "why", "how", "a", "an", "to", "of",
    "in", "on", "at", "by", "or", "as", "is", "it", "be", "not", "no",
    "if", "but", "so", "because", "after", "before", "during", "while",
    "through", "up", "down", "out", "off", "too", "very", "also",
}

NUMBER_WORDS: Set[str] = {
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
}

TIME_WORDS: Set[str] = {
    "day", "days", "week", "weeks", "month", "months", "year", "years",
    "hour", "hours", "minute", "minutes",
}

BAD_STARTS: Set[str] = {
    "whether", "rather", "than", "without", "with", "into", "from", "for",
    "to", "at", "on", "by", "if", "while", "so", "then", "this", "that",
    "these", "those", "your", "many", "people", "because", "and", "or",
    "often", "still", "just", "as", "using", "including", "notice", "mark",
    "says", "let", "know", "like", "approach", "search", "searches",
    "count", "counts", "understanding",
}

BAD_ENDINGS: Set[str] = {
    "at", "with", "without", "than", "rather", "into", "from", "for", "to",
    "by", "if", "when", "while", "so", "then", "and", "or", "but", "the",
    "your", "someone", "this", "that", "depends", "changes", "ask", "an",
    "a", "because", "about", "before", "after", "during", "through",
    "last", "much", "main", "one", "of", "most", "near", "safe", "same",
    "later", "right", "schedule", "accordingly",
}

WEAK_TOKENS: Set[str] = {
    "guesswork", "predictable", "someone", "rather", "whether",
    "goal", "question", "mystery", "speak", "thing", "things", "stuff",
    "people", "ask", "many", "result", "depends", "answer", "changes",
}

PRONOUN_TAILS: Set[str] = {
    "you", "your", "they", "them", "their", "it", "its", "we", "us", "our",
    "he", "she", "him", "her",
}

HELPER_VERBS: Set[str] = {
    "is", "are", "was", "were", "be", "being", "been", "am",
    "can", "could", "will", "would", "should", "may", "might",
    "has", "have", "had", "do", "does", "did",
}

NARRATIVE_VERBS: Set[str] = {
    "use", "using", "include", "including", "notice", "mark", "says", "say",
    "let", "know", "like", "approach", "search", "searches", "raise", "raises",
    "span", "spans", "stretch", "stretches", "avoid", "trying", "get",
    "count", "counts", "identify", "convert", "vary", "working", "understanding",
}

ACTION_TOKENS: Set[str] = {
    "calculate", "track", "confirm", "compare", "choose", "check", "measure",
    "estimate", "build", "create", "fix", "improve", "optimize", "reduce",
    "increase", "manage", "treat", "prevent", "diagnose", "review", "audit",
    "forecast", "plan", "write", "design", "analyze", "monitor",
}

WEAK_ACTION_OBJECTS: Set[str] = {
    "safe", "fertile", "answers", "things", "stuff", "more", "much",
}

VAGUE_TOPIC_STARTS: Set[str] = {
    "average", "real", "true", "typical", "old", "perfect", "estimated",
    "rough", "roughly", "simple", "single", "first", "last", "next",
    "few", "many", "several", "around", "near", "together", "anchored",
    "bar", "case", "situations", "every", "exact", "easiest", "working",
    "number", "math", "patterns", "closer", "bleeding",
}

WEAK_TASK_OBJECTS: Set[str] = {
    "accordingly", "intercourse", "days", "day", "routine", "things",
    "stuff", "estimate", "plan",
}

WEAK_HEADS_WHEN_ALONE: Set[str] = {
    "day", "days", "length", "routine", "estimate", "plan", "date",
    "window", "cycle", "period", "phase",
}

GENERIC_MODIFIERS: Set[str] = {
    "exact", "easiest", "simple", "rough", "average", "typical", "true",
    "real", "expected", "working", "first", "last", "next", "single",
    "several", "few", "many", "every", "old", "perfect", "estimated",
}

BAD_FRAGMENT_PATTERNS = (
    r"\b(\w+)\s+\1\b",
    r"\b(\w+)(?:\s+\w+){0,3}\s+\1\b",
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
    r"\bmany users say\b",
    r"\bbecause they\b",
    r"\bbecause you\b",
    r"\bwith \d+\b",
    r"\bwith (a|an|the)\b",
    r"\bwithout (a|an|the)\b",
    r"\bbased on (last|this|that|these|those)\b",
    r"\b(before|after) getting\b",
    r"\binto highly\b",
    r"\bfind answers\b",
    r"\bmeasure your\b",
    r"\bestimate your\b",
    r"\bconfirm you\b",
    r"\bconfirm the\b",
    r"\bguide explains\b",
    r"\bexplains simple\b",
    r"\bfact unlocks\b",
    r"\b\w+\s+has\s+\w+\b",
    r"\b\w+\s+is\s+one\b",
    r"\bis one of\b",
    r"\bboth\s+\w+\s+and\s+\w+\b",
    r"\bfew days before that\b",
    r"\bdays before that\b",
    r"\bfinish with\b",
    r"\bintimacy during\b",
    r"\bplan\s+\w+\s+later\b",
    r"\bplan\s+\w+\s+the\b",
    r"\bworking with trained\b",
    r"\bconsider working with\b",
    r"\blater that day\b",
    r"\bsame day\b",
    r"\bright on schedule\b",
    r"\bsingle exact day\b",
    r"\bsearch for\b",
    r"\bsearches like\b",
    r"\btime prediction with\b",
    r"\bversion of an\b",
    r"\bpersonalized\s+\w+\b",
    r"\breal time\s+\w+\b",
    r"\bcount the\b",
    r"\bnumber of\b",
    r"\bmath to\b",
    r"\bpatterns to\b",
    r"\bidentify the\b",
    r"\bconceive identify\b",
    r"\btogether in\b",
)

INTENT_STARTS = (
    "how to", "how many", "what is", "what are", "when do", "when does",
    "best way", "best time", "signs of", "symptoms of", "causes of",
    "treatment for",
)

TRUSTED_SOURCE_TYPES = {
    "title", "heading_h1", "heading_h2", "heading_h3",
    "entity", "intent", "list_item",
}

CONDITION_CONNECTORS = {
    "after", "before", "during", "without", "with", "near", "based", "for",
}

UNIVERSAL_ANCHOR_HEADS: Set[str] = {
    "software", "tool", "tools", "platform", "system", "strategy", "workflow",
    "automation", "integration", "pipeline", "dashboard", "api", "app",
    "application", "plugin", "extension", "database", "storage", "security",
    "keyword", "keywords", "content", "backlink", "audit", "optimization",
    "conversion", "page", "traffic", "ranking", "analytics", "yield", "rate",
    "rates", "forecast", "tax", "reporting", "investment", "lease",
    "agreement", "contract", "review", "lawyer", "visa", "property",
    "mortgage", "insurance", "calculator", "checklist", "service", "services",
    "pricing", "prices", "policy", "delivery", "menu", "reservation",
    "restaurant", "hotel", "airport", "coverage", "rental", "checkout",
    "cart", "product", "customer", "tutoring", "study", "management",
    "project", "ideas", "practice", "questions", "resume", "interview",
    "course", "lesson", "training", "symptoms", "causes", "treatment",
    "medication", "dosage", "foods", "antibiotics", "cream", "options",
    "therapy", "pain", "pressure", "temperature", "mucus", "cycle", "period",
    "fertility", "window", "pregnancy", "ovulation", "kits", "phase",
    "length", "date", "day", "days", "ultrasound", "implantation",
    "performance", "settings", "guide", "benefits", "contractor", "estimate",
    "schedule", "routine", "collection", "trends", "quotes", "report",
    "analysis", "assessment", "plan",
}


def canonical_phrase(text: str) -> str:
    s = (text or "").strip().lower()
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"^\s*(?:\d+[\.\)]\s+|[•\-–]\s+)", "", s)
    s = re.sub(r"^[\"'“”‘’\(\[\{]+|[\"'“”‘’\)\]\}:;,\.\!\?]+$", "", s)
    return re.sub(r"\s+", " ", s).strip()


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]


def content_tokens(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in STOPWORDS]


def _has_bad_fragment_pattern(p: str) -> bool:
    return any(re.search(pat, p) for pat in BAD_FRAGMENT_PATTERNS)


def _looks_like_intent_phrase(p: str) -> bool:
    return p.startswith(INTENT_STARTS)


def _is_numeric_time_phrase(tokens: List[str]) -> bool:
    if not tokens:
        return False

    if len(tokens) == 2 and (tokens[0].isdigit() or tokens[0] in NUMBER_WORDS) and tokens[1] in TIME_WORDS:
        return True

    if len(tokens) == 3 and tokens[0].isdigit() and tokens[1] == "to" and tokens[2].isdigit():
        return True

    if (tokens[0].isdigit() or tokens[0] in NUMBER_WORDS) and any(t in TIME_WORDS for t in tokens):
        if tokens[-1] not in {"cycle", "rate", "plan", "schedule", "forecast", "estimate"}:
            return True

    return False


def _has_anchor_head(tokens: List[str]) -> bool:
    if not tokens:
        return False

    if tokens[-1] not in UNIVERSAL_ANCHOR_HEADS:
        return False

    if tokens[0] in NARRATIVE_VERBS:
        return False

    if any(t in {"or", "and"} for t in tokens[1:-1]):
        return False

    return True


def _is_weak_generic_topic(tokens: List[str]) -> bool:
    if not tokens:
        return True

    if _is_numeric_time_phrase(tokens):
        return True

    if tokens[0] in VAGUE_TOPIC_STARTS:
        return True

    if len(tokens) == 2:
        if tokens[0] in GENERIC_MODIFIERS and tokens[-1] in WEAK_HEADS_WHEN_ALONE:
            return True

        if tokens[-1] in {"day", "days", "length", "routine", "estimate"}:
            return True

    if len(tokens) == 3:
        if tokens[0] in GENERIC_MODIFIERS and tokens[-1] in WEAK_HEADS_WHEN_ALONE:
            return True

    return False


def _looks_like_clear_task(tokens: List[str]) -> bool:
    if len(tokens) < 2:
        return False

    if tokens[0] not in ACTION_TOKENS:
        return False

    if tokens[-1] in WEAK_ACTION_OBJECTS or tokens[-1] in WEAK_TASK_OBJECTS:
        return False

    if tokens[-1] in BAD_ENDINGS or tokens[-1] in PRONOUN_TAILS:
        return False

    if tokens[-1].isdigit():
        return False

    if any(t in HELPER_VERBS for t in tokens[1:]):
        return False

    if any(t in NARRATIVE_VERBS for t in tokens[1:]):
        return False

    if any(t in {"or", "and"} for t in tokens[1:-1]):
        return False

    if len(tokens) == 2:
        if tokens[-1] in {"accordingly", "day", "days", "estimate", "routine", "plan"}:
            return False
        return True

    return _has_anchor_head(tokens)


def _looks_like_standalone_topic(tokens: List[str], content: List[str]) -> bool:
    if len(tokens) < 2 or len(tokens) > 5:
        return False

    if len(content) < 2:
        return False

    if _is_numeric_time_phrase(tokens) or _is_weak_generic_topic(tokens):
        return False

    if any(t in HELPER_VERBS for t in tokens):
        return False

    if any(t in NARRATIVE_VERBS for t in tokens):
        return False

    if any(t in {"or", "and"} for t in tokens[1:-1]):
        return False

    return _has_anchor_head(tokens)


def _looks_like_condition_topic(tokens: List[str]) -> bool:
    if len(tokens) < 3:
        return False

    if _is_numeric_time_phrase(tokens) or _is_weak_generic_topic(tokens):
        return False

    if not any(t in CONDITION_CONNECTORS for t in tokens[1:-1]):
        return False

    if tokens[-1] in BAD_ENDINGS or tokens[-1] in PRONOUN_TAILS:
        return False

    if tokens[-1].isdigit():
        return False

    if any(t in HELPER_VERBS for t in tokens):
        return False

    if any(t in NARRATIVE_VERBS for t in tokens):
        return False

    if any(t in {"or", "and"} for t in tokens[1:-1]):
        return False

    if tokens[0] in {
        "days", "months", "several", "few", "time", "prediction",
        "suppressed", "holds", "14", "18", "day",
    }:
        return False

    return _has_anchor_head(tokens)


def _source_score(source: str) -> float:
    if source in {"title", "heading_h1"}:
        return 0.25
    if source in {"heading_h2", "heading_h3"}:
        return 0.20
    if source in {"entity", "intent"}:
        return 0.22
    if source == "list_item":
        return 0.15
    if source == "sentence":
        return -0.12
    return 0.0


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

    if not p:
        return {"keep": False, "strength": "weak", "score": 0.0, "reason": "empty"}

    if _is_numeric_time_phrase(tokens):
        return {"keep": False, "strength": "weak", "score": 0.16, "reason": "numeric_time_phrase"}

    if len(tokens) < 2:
        return {"keep": False, "strength": "weak", "score": 0.05, "reason": "too_short"}

    if len(tokens) > 7:
        return {"keep": False, "strength": "weak", "score": 0.15, "reason": "too_long"}

    if len(content) < 2:
        return {"keep": False, "strength": "weak", "score": 0.1, "reason": "low_content"}

    if tokens[0] in BAD_STARTS:
        return {"keep": False, "strength": "weak", "score": 0.18, "reason": "bad_start"}

    if tokens[-1] in BAD_ENDINGS:
        return {"keep": False, "strength": "weak", "score": 0.18, "reason": "bad_ending"}

    if tokens[-1].isdigit():
        return {"keep": False, "strength": "weak", "score": 0.18, "reason": "number_tail"}

    if tokens[-1] in PRONOUN_TAILS:
        return {"keep": False, "strength": "weak", "score": 0.18, "reason": "pronoun_tail"}

    if any(t in WEAK_TOKENS for t in tokens):
        return {"keep": False, "strength": "weak", "score": 0.2, "reason": "weak_token"}

    if _has_bad_fragment_pattern(p):
        return {"keep": False, "strength": "weak", "score": 0.2, "reason": "fragment_pattern"}

    anchor_reasons: List[str] = []

    if _looks_like_intent_phrase(p):
        if len(tokens) >= 5 and not _has_anchor_head(tokens):
            return {"keep": False, "strength": "weak", "score": 0.24, "reason": "intent_not_anchor_worthy"}
        anchor_reasons.append("intent_phrase")

    if _looks_like_clear_task(tokens):
        anchor_reasons.append("clear_task")

    if _looks_like_standalone_topic(tokens, content):
        anchor_reasons.append("standalone_topic")

    if _looks_like_condition_topic(tokens):
        anchor_reasons.append("condition_topic")

    if not anchor_reasons:
        return {"keep": False, "strength": "weak", "score": 0.32, "reason": "not_anchor_worthy"}

    score = 0.40 + _source_score(source)

    if "intent_phrase" in anchor_reasons:
        score += 0.20
    if "clear_task" in anchor_reasons:
        score += 0.18
    if "standalone_topic" in anchor_reasons:
        score += 0.20
    if "condition_topic" in anchor_reasons:
        score += 0.12
    if 2 <= len(tokens) <= 5:
        score += 0.08
    if len(content) >= 3:
        score += 0.05
    if source in TRUSTED_SOURCE_TYPES:
        score += 0.05
    if vertical and vertical != "general":
        score += 0.03
    if context and p in canonical_phrase(context):
        score += 0.04

    score = max(0.0, min(1.0, round(score, 4)))

    if score >= 0.72:
        return {
            "keep": True,
            "strength": "strong",
            "score": score,
            "reason": "+".join(anchor_reasons),
        }

    return {"keep": False, "strength": "weak", "score": score, "reason": "below_threshold"}


def is_strong_phrase(
    phrase: str,
    source_type: str = "",
    vertical: str = "general",
    context: str = "",
) -> bool:
    return bool(classify_phrase_strength(phrase, source_type, vertical, context).get("keep"))