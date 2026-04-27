from __future__ import annotations

import re
from typing import Dict, List, Set, Any


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

CLAUSE_VERBS: Set[str] = {
    "is", "are", "was", "were", "has", "have", "had", "do", "does", "did",
    "can", "could", "should", "would", "will", "may", "might", "be", "been",
    "being", "become", "becomes", "became", "means", "mean", "depends",
    "depend", "helps", "help", "improves", "improve", "reduces", "reduce",
    "increases", "increase", "supports", "support", "contains", "contain",
    "requires", "require", "reveals", "reveal", "respond", "responds",
    "handled", "handle", "affect", "affects",
}

LOW_VALUE_GENERIC_SURVIVORS: Set[str] = {
    "management strategies",
    "rapid plan",
    "dieting plan",
    "strongest tools",
    "helpful medication",
    "repeatable systems",
}

CONNECTORS: Set[str] = {
    "for", "to", "with", "without", "before", "after", "during", "at", "in",
    "on", "between", "among", "against", "through",
}

ACTION_LEAK_STARTS: Set[str] = {
    "neglect", "avoid", "reduce", "improve", "manage", "check", "monitor",
    "track", "review", "choose", "define", "send", "skip", "treat",
}

WEAK_CARRYOVER_WORDS: Set[str] = {
    "meals", "routines", "choices", "checks", "effects", "cost", "risk",
    "footwear", "infections", "daily", "proper", "consistent",
}

QUERY_STARTS: Set[str] = {
    "best", "how", "when", "what", "why", "where", "which",
}

GENERIC_ADJECTIVES: Set[str] = {
    "good", "better", "best", "strong", "weak", "useful", "helpful",
    "important", "clear", "simple", "basic", "common", "general",
    "successful", "strongest", "regular", "normal",
}

GENERIC_HEADS: Set[str] = {
    "tools", "tool", "things", "thing", "ways", "way", "areas", "area",
    "parts", "part", "problem", "problems", "issue", "issues",
    "result", "results", "system", "systems",
}

NOUN_CHAIN_WORDS: Set[str] = {
    "blood", "pressure", "control", "cholesterol", "management",
    "foot", "inspections", "checks", "monitoring", "medication",
    "movement", "income", "mortgage", "payment", "payments",
    "insurance", "costs", "property", "taxes", "maintenance",
    "expenses", "screening", "lease", "agreements", "agreement",
    "late", "fee", "policy", "reminders", "security", "deposit",
    "renewal", "terms", "rules", "products", "services", "pricing",
    "data", "software", "equipment", "customers", "suppliers",
    "marketing", "inventory",
}


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]


def _is_action_leak_start(tokens: List[str]) -> bool:
    if len(tokens) < 2:
        return False

    if tokens[0] not in ACTION_LEAK_STARTS:
        return False

    # Allow clean query/action phrases only when they have a connector.
    if any(t in CONNECTORS for t in tokens):
        return False

    return True


def _is_short_multi_head_collision(tokens: List[str]) -> bool:
    if len(tokens) not in {2, 3, 4}:
        return False

    if any(t in CONNECTORS for t in tokens):
        return False

    head_like = 0
    for t in tokens:
        if (
            t in NOUN_CHAIN_WORDS
            or t in GENERIC_HEADS
            or t in WEAK_CARRYOVER_WORDS
        ):
            head_like += 1

    return head_like >= 2


def _is_long_carryover_stack(tokens: List[str]) -> bool:
    if len(tokens) < 4:
        return False

    if _is_query_like(tokens):
        return False

    if any(t in CONNECTORS for t in tokens):
        return False

    carryover_hits = sum(1 for t in tokens if t in WEAK_CARRYOVER_WORDS)
    noun_hits = sum(1 for t in tokens if t in NOUN_CHAIN_WORDS)

    return (carryover_hits + noun_hits) >= 3

def _is_query_like(tokens: List[str]) -> bool:
    if len(tokens) < 5:
        return False
    return tokens[0] in QUERY_STARTS and any(t in CONNECTORS for t in tokens[1:-1])


def _has_clause_leak(tokens: List[str]) -> bool:
    if len(tokens) < 4:
        return False

    if _is_query_like(tokens):
        return False

    return any(t in CLAUSE_VERBS for t in tokens)


def _starts_or_ends_badly(tokens: List[str]) -> bool:
    if not tokens:
        return True

    if tokens[0] in STOPWORDS:
        return True

    if tokens[-1] in STOPWORDS:
        return True

    if len(tokens) >= 3 and tokens[0] in GENERIC_ADJECTIVES and tokens[-1] in GENERIC_HEADS:
        return True

    return False

def _is_low_value_generic_survivor(tokens: List[str]) -> bool:
    phrase = " ".join(tokens)
    return phrase in LOW_VALUE_GENERIC_SURVIVORS


def _is_dense_noun_chain(tokens: List[str]) -> bool:
    if len(tokens) < 4:
        return False

    if _is_query_like(tokens):
        return False

    connector_count = sum(1 for t in tokens if t in CONNECTORS)
    chain_hits = sum(1 for t in tokens if t in NOUN_CHAIN_WORDS)

    if len(tokens) >= 4 and chain_hits / max(1, len(tokens)) >= 0.75 and connector_count == 0:
        return True

    if len(tokens) >= 5 and chain_hits / max(1, len(tokens)) >= 0.60 and connector_count <= 1:
        return True

    return False

def _is_generic_short_false_positive(tokens: List[str]) -> bool:
    if len(tokens) != 2:
        return False

    left, right = tokens

    if left in GENERIC_ADJECTIVES and right in GENERIC_HEADS:
        return True

    weak_pairs = {
        ("movement", "medication"),
        ("helpful", "medication"),
        ("successful", "management"),
        ("strongest", "tools"),
    }

    return (left, right) in weak_pairs


def _has_repeated_or_duplicate_noise(tokens: List[str]) -> bool:
    if len(tokens) < 3:
        return False

    unique_ratio = len(set(tokens)) / max(1, len(tokens))
    return unique_ratio < 0.75


def candidate_window_guard(candidate: str, *, source_type: str = "") -> Dict[str, Any]:
    phrase = " ".join(tokenize(candidate))

    if not phrase:
        return {"keep": False, "reason": "empty_candidate", "phrase": ""}

    tokens = phrase.split()

    if len(tokens) < 2:
        return {"keep": False, "reason": "too_short", "phrase": phrase}

    if len(tokens) > 10:
        return {"keep": False, "reason": "too_long", "phrase": phrase}

    if _starts_or_ends_badly(tokens):
        return {"keep": False, "reason": "bad_boundary", "phrase": phrase}
    if _is_action_leak_start(tokens):
        return {"keep": False, "reason": "action_leak_start", "phrase": phrase}

    if _is_short_multi_head_collision(tokens):
        return {"keep": False, "reason": "short_multi_head_collision", "phrase": phrase}

    if _is_long_carryover_stack(tokens):
        return {"keep": False, "reason": "long_carryover_stack", "phrase": phrase}
    if _has_clause_leak(tokens):
        return {"keep": False, "reason": "clause_leak", "phrase": phrase}

    if _is_dense_noun_chain(tokens):
        return {"keep": False, "reason": "dense_noun_chain", "phrase": phrase}

    if _has_repeated_or_duplicate_noise(tokens):
        return {"keep": False, "reason": "duplicate_noise", "phrase": phrase}
    if _is_generic_short_false_positive(tokens):
        return {"keep": False, "reason": "generic_short_false_positive", "phrase": phrase}
    if _is_low_value_generic_survivor(tokens):
        return {"keep": False, "reason": "low_value_generic_survivor", "phrase": phrase}
    return {"keep": True, "reason": "guard_pass", "phrase": phrase}