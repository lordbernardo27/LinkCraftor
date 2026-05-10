from __future__ import annotations

import re
from typing import Any, Dict, List, Set, Tuple


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
    "handled", "handle", "affect", "affects", "struggle", "struggles",
}

CONNECTORS: Set[str] = {
    "for", "to", "with", "without", "before", "after", "during", "at", "in",
    "on", "between", "among", "against", "through", "into", "across", "near",
    "within", "around", "under", "over", "beyond",
}

ACTION_LEAK_STARTS: Set[str] = {
    "neglect", "avoid", "reduce", "improve", "manage", "check", "monitor",
    "track", "review", "choose", "define", "send", "skip", "treat",
}

WEAK_SUBJECTS: Set[str] = {
    "business", "businesses", "people", "person", "students", "student",
    "patients", "patient", "users", "user", "customers", "customer",
    "owners", "owner", "parents", "parent", "workers", "worker",
    "teams", "team", "companies", "company",
}

WEAK_SUBJECT_VERBS: Set[str] = {
    "struggle", "struggles", "face", "faces", "need", "needs", "want",
    "wants", "use", "uses", "make", "makes", "get", "gets",
}

WEAK_CARRYOVER_WORDS: Set[str] = {
    "meals", "routines", "choices", "checks", "effects", "cost", "risk",
    "footwear", "infections", "daily", "proper", "consistent", "quickly",
    "face", "thing", "things", "many", "several", "various", "different",
    "common", "important", "simple", "basic", "major", "minor",
}

QUERY_STARTS: Set[str] = {
    "best", "how", "when", "what", "why", "where", "which",
}

GENERIC_ADJECTIVES: Set[str] = {
    "good", "better", "best", "strong", "weak", "useful", "helpful",
    "important", "clear", "simple", "basic", "common", "general",
    "successful", "strongest", "regular", "normal", "same", "valuable",
    "healthy", "traditional", "different", "various", "certain",
}

GENERIC_HEADS: Set[str] = {
    "tools", "tool", "things", "thing", "ways", "way", "areas", "area",
    "parts", "part", "problem", "problems", "issue", "issues",
    "result", "results", "system", "systems", "topic", "topics",
    "factor", "factors", "method", "methods", "option", "options",
    "course", "courses", "care", "routine", "routines",
}

UNIVERSAL_WEAK_PREFIXES: Set[str] = {
    "same", "another", "various", "different", "valuable",
    "general", "specific", "certain", "particular",
    "healthy", "simple", "basic", "normal", "regular",
    "traditional", "random", "minor", "major",
}

UNIVERSAL_WEAK_HEADS: Set[str] = {
    "system", "systems", "course", "courses", "care",
    "routine", "routines", "thing", "things", "area",
    "areas", "part", "parts", "method", "methods",
    "option", "options", "way", "ways",
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
    "marketing", "inventory", "cash", "flow", "revenue", "payroll",
    "rent", "supplier", "invoices", "invoice", "loan", "loans",
    "study", "plan", "learning", "platform", "progress", "tracking",
    "lesson", "rates", "completion", "strategy", "environment",
}

VALID_ORDERED_PAIRS: Set[Tuple[str, str]] = {
    ("cash", "flow"),
    ("blood", "pressure"),
    ("internal", "linking"),
    ("external", "linking"),
    ("search", "intent"),
    ("supply", "chain"),
    ("remote", "work"),
    ("content", "marketing"),
    ("email", "marketing"),
    ("social", "media"),
    ("machine", "learning"),
    ("artificial", "intelligence"),
    ("real", "estate"),
    ("credit", "card"),
    ("credit", "cards"),
    ("interest", "rate"),
    ("interest", "rates"),
    ("rental", "agreement"),
    ("lease", "agreement"),
    ("category", "pages"),
    ("product", "pages"),
    ("side", "effects"),
    ("study", "plan"),
    ("learning", "platform"),
    ("progress", "tracking"),
    ("recorded", "lesson"),
    ("completion", "rates"),
}

REVERSED_ORDERED_PAIRS: Set[Tuple[str, str]] = {
    (b, a) for a, b in VALID_ORDERED_PAIRS
}

BAD_BOUNDARY_STARTS: Set[str] = {
    "quickly", "slowly", "often", "usually", "sometimes", "thing", "things",
    "face", "facing", "many", "several", "various", "different", "some",
    "any", "each", "every", "other", "another", "certain", "same", "re",
}

BAD_BOUNDARY_ENDS: Set[str] = {
    "thing", "things", "way", "ways", "area", "areas", "part", "parts",
    "issue", "issues", "problem", "problems", "result", "results",
}

ANCHOR_CORE_PHRASES: Set[str] = {
    "cash flow",
    "cash flow management",
    "blood pressure",
    "blood pressure control",
    "internal linking",
    "internal linking strategy",
    "external linking",
    "search intent",
    "category pages",
    "product pages",
    "rental agreement",
    "lease agreement",
    "side effects",
    "supply chain",
    "remote work",
    "content marketing",
    "email marketing",
    "machine learning",
    "study plan",
    "learning platform",
    "progress tracking",
}

QUALITY_GATE_WEIGHTS: Dict[str, float] = {
    "logical_structure": 0.20,
    "context_fit": 0.20,
    "pragmatic_anchor_value": 0.25,
    "topic_coherence": 0.15,
    "trust_risk_safety": 0.10,
    "rule_hybrid_check": 0.10,
}


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]


def make_quality_gate_result(
    phrase: str,
    score: float,
    decision: str,
    signals: Dict[str, float],
    reasons: List[str] | None = None,
) -> Dict[str, Any]:
    return {
        "phrase": phrase,
        "quality_gate_score": round(float(score), 4),
        "decision": decision,
        "signals": signals or {},
        "reasons": reasons or [],
    }


def _weighted_quality_score(signals: Dict[str, float]) -> float:
    total = 0.0
    for key, weight in QUALITY_GATE_WEIGHTS.items():
        total += float(signals.get(key, 0.0)) * weight
    return round(total, 4)


def _quality_decision(score: float) -> str:
    if score >= 0.80:
        return "ACCEPT"
    if score >= 0.65:
        return "REVIEW"
    return "REJECT"


def _base_quality_signals() -> Dict[str, float]:
    return {
        "logical_structure": 1.0,
        "context_fit": 1.0,
        "pragmatic_anchor_value": 1.0,
        "topic_coherence": 1.0,
        "trust_risk_safety": 1.0,
        "rule_hybrid_check": 1.0,
    }


def _attach_quality_gate(
    result: Dict[str, Any],
    *,
    signals: Dict[str, float] | None = None,
    reasons: List[str] | None = None,
) -> Dict[str, Any]:
    phrase = result.get("phrase", "")
    keep = bool(result.get("keep"))

    final_signals = _base_quality_signals()
    if signals:
        final_signals.update(signals)

    if not keep:
        final_signals["rule_hybrid_check"] = 0.0
        reasons = reasons or [str(result.get("reason", "rejected_by_guard"))]

    score = _weighted_quality_score(final_signals)
    decision = "REJECT" if not keep else _quality_decision(score)

    result["quality_gate"] = make_quality_gate_result(
        phrase=phrase,
        score=score,
        decision=decision,
        signals=final_signals,
        reasons=reasons or [str(result.get("reason", ""))],
    )

    return result


def _reject(phrase: str, reason: str, signals: Dict[str, float] | None = None) -> Dict[str, Any]:
    return _attach_quality_gate(
        {"keep": False, "reason": reason, "phrase": phrase},
        signals=signals,
        reasons=[reason],
    )


def _accept(phrase: str, reason: str, signals: Dict[str, float] | None = None) -> Dict[str, Any]:
    return _attach_quality_gate(
        {"keep": True, "reason": reason, "phrase": phrase},
        signals=signals,
        reasons=[reason],
    )


def _phrase_from_tokens(tokens: List[str]) -> str:
    return " ".join(tokens)


def _contains_valid_core_phrase(tokens: List[str]) -> str:
    joined = _phrase_from_tokens(tokens)
    for core in sorted(ANCHOR_CORE_PHRASES, key=lambda x: len(x.split()), reverse=True):
        if core in joined:
            return core
    return ""


def _has_reversed_ordered_pair(tokens: List[str]) -> bool:
    return any(pair in REVERSED_ORDERED_PAIRS for pair in zip(tokens, tokens[1:]))


def _has_valid_ordered_pair(tokens: List[str]) -> bool:
    return any(pair in VALID_ORDERED_PAIRS for pair in zip(tokens, tokens[1:]))


def _is_weak_subject_verb_fragment(tokens: List[str]) -> bool:
    if len(tokens) != 2:
        return False
    left, right = tokens
    return left in WEAK_SUBJECTS and right in WEAK_SUBJECT_VERBS


def _is_action_leak_start(tokens: List[str]) -> bool:
    if len(tokens) < 2:
        return False
    if tokens[0] not in ACTION_LEAK_STARTS:
        return False
    if any(t in CONNECTORS for t in tokens):
        return False
    return True


def _is_short_multi_head_collision(tokens: List[str]) -> bool:
    if len(tokens) not in {2, 3, 4}:
        return False

    if _has_valid_ordered_pair(tokens):
        return False

    if any(t in CONNECTORS for t in tokens):
        return False

    head_like = 0
    for t in tokens:
        if t in NOUN_CHAIN_WORDS or t in GENERIC_HEADS or t in WEAK_CARRYOVER_WORDS:
            head_like += 1

    return head_like >= 3


def _is_query_like(tokens: List[str]) -> bool:
    if len(tokens) < 5:
        return False
    return tokens[0] in QUERY_STARTS and any(t in CONNECTORS for t in tokens[1:-1])


def _is_long_carryover_stack(tokens: List[str]) -> bool:
    if len(tokens) < 4:
        return False

    if _is_query_like(tokens):
        return False

    if _contains_valid_core_phrase(tokens):
        return False

    if any(t in CONNECTORS for t in tokens):
        return False

    carryover_hits = sum(1 for t in tokens if t in WEAK_CARRYOVER_WORDS)
    noun_hits = sum(1 for t in tokens if t in NOUN_CHAIN_WORDS)

    return (carryover_hits + noun_hits) >= 4


def _has_clause_leak(tokens: List[str]) -> bool:
    if len(tokens) < 4:
        return False

    if _is_query_like(tokens):
        return False

    if _contains_valid_core_phrase(tokens) and len(tokens) <= 6:
        return False

    return any(t in CLAUSE_VERBS for t in tokens)


def _starts_or_ends_badly(tokens: List[str]) -> bool:
    if not tokens:
        return True

    if tokens[0] in STOPWORDS or tokens[-1] in STOPWORDS:
        return True

    if tokens[0] in BAD_BOUNDARY_STARTS or tokens[-1] in BAD_BOUNDARY_ENDS:
        return True

    if len(tokens) >= 3 and tokens[0] in GENERIC_ADJECTIVES and tokens[-1] in GENERIC_HEADS:
        return True

    return False


def _is_dense_noun_chain(tokens: List[str]) -> bool:
    if len(tokens) < 5:
        return False

    if _is_query_like(tokens):
        return False

    if _contains_valid_core_phrase(tokens):
        return False

    connector_count = sum(1 for t in tokens if t in CONNECTORS)
    chain_hits = sum(1 for t in tokens if t in NOUN_CHAIN_WORDS)

    if len(tokens) >= 5 and chain_hits / max(1, len(tokens)) >= 0.75 and connector_count == 0:
        return True

    return False


def _is_generic_short_false_positive(tokens: List[str]) -> bool:
    if len(tokens) != 2:
        return False

    left, right = tokens

    if (left, right) in VALID_ORDERED_PAIRS:
        return False

    if left in GENERIC_ADJECTIVES and right in GENERIC_HEADS:
        return True

    return False


def _is_universal_weak_semantic_phrase(tokens: List[str]) -> bool:
    if len(tokens) < 2:
        return False

    first = tokens[0]
    last = tokens[-1]

    if first in UNIVERSAL_WEAK_PREFIXES:
        return True

    if last in UNIVERSAL_WEAK_HEADS and first in GENERIC_ADJECTIVES:
        return True

    if last in UNIVERSAL_WEAK_HEADS and len(tokens) <= 3:
        non_generic = [
            t for t in tokens
            if t not in UNIVERSAL_WEAK_PREFIXES
            and t not in UNIVERSAL_WEAK_HEADS
            and t not in GENERIC_ADJECTIVES
            and t not in CONNECTORS
        ]
        if len(non_generic) < 2:
            return True

    return False


def _has_repeated_or_duplicate_noise(tokens: List[str]) -> bool:
    if len(tokens) < 3:
        return False

    unique_ratio = len(set(tokens)) / max(1, len(tokens))
    return unique_ratio < 0.75


def _is_stitched_vertical_list(tokens: List[str]) -> bool:
    if len(tokens) < 5:
        return False

    if _is_query_like(tokens):
        return False

    if _contains_valid_core_phrase(tokens):
        return False

    connector_count = sum(1 for t in tokens if t in CONNECTORS)
    if connector_count > 0:
        return False

    chain_hits = sum(1 for t in tokens if t in NOUN_CHAIN_WORDS)
    return chain_hits >= 4


def _compress_long_wrapper(tokens: List[str]) -> str:
    if len(tokens) < 4:
        return _phrase_from_tokens(tokens)

    core = _contains_valid_core_phrase(tokens)
    if core:
        return core

    return _phrase_from_tokens(tokens)


def candidate_window_guard(candidate: str, *, source_type: str = "") -> Dict[str, Any]:
    phrase = " ".join(tokenize(candidate))

    if not phrase:
        return _reject("", "empty_candidate")

    tokens = phrase.split()

    if len(tokens) < 2:
        return _reject(
            phrase,
            "too_short",
            {
                "logical_structure": 0.30,
                "pragmatic_anchor_value": 0.15,
            },
        )

    compressed_phrase = _compress_long_wrapper(tokens)
    compressed_tokens = compressed_phrase.split()

    if compressed_phrase != phrase and len(compressed_tokens) >= 2:
        phrase = compressed_phrase
        tokens = compressed_tokens

    if len(tokens) > 10:
        return _reject(
            phrase,
            "too_long",
            {
                "logical_structure": 0.40,
                "context_fit": 0.45,
                "pragmatic_anchor_value": 0.30,
            },
        )

    if _starts_or_ends_badly(tokens):
        return _reject(
            phrase,
            "bad_boundary",
            {
                "logical_structure": 0.25,
                "pragmatic_anchor_value": 0.20,
            },
        )

    if _has_reversed_ordered_pair(tokens):
        return _reject(
            phrase,
            "reversed_ordered_pair",
            {
                "logical_structure": 0.10,
                "pragmatic_anchor_value": 0.20,
                "topic_coherence": 0.45,
            },
        )

    if _is_weak_subject_verb_fragment(tokens):
        return _reject(
            phrase,
            "weak_subject_verb_fragment",
            {
                "logical_structure": 0.35,
                "context_fit": 0.45,
                "pragmatic_anchor_value": 0.10,
                "topic_coherence": 0.35,
            },
        )

    if _is_action_leak_start(tokens):
        return _reject(
            phrase,
            "action_leak_start",
            {
                "logical_structure": 0.35,
                "pragmatic_anchor_value": 0.20,
            },
        )

    if _is_short_multi_head_collision(tokens):
        return _reject(
            phrase,
            "short_multi_head_collision",
            {
                "logical_structure": 0.30,
                "pragmatic_anchor_value": 0.25,
                "topic_coherence": 0.40,
            },
        )

    if _is_long_carryover_stack(tokens):
        return _reject(
            phrase,
            "long_carryover_stack",
            {
                "logical_structure": 0.25,
                "context_fit": 0.35,
                "pragmatic_anchor_value": 0.15,
            },
        )

    if _has_clause_leak(tokens):
        return _reject(
            phrase,
            "clause_leak",
            {
                "logical_structure": 0.25,
                "context_fit": 0.35,
                "pragmatic_anchor_value": 0.20,
            },
        )

    if _is_stitched_vertical_list(tokens):
        return _reject(
            phrase,
            "stitched_vertical_list",
            {
                "logical_structure": 0.20,
                "context_fit": 0.25,
                "pragmatic_anchor_value": 0.15,
                "topic_coherence": 0.30,
            },
        )

    if _is_dense_noun_chain(tokens):
        return _reject(
            phrase,
            "dense_noun_chain",
            {
                "logical_structure": 0.25,
                "context_fit": 0.35,
                "pragmatic_anchor_value": 0.25,
            },
        )

    if _has_repeated_or_duplicate_noise(tokens):
        return _reject(
            phrase,
            "duplicate_noise",
            {
                "logical_structure": 0.25,
                "pragmatic_anchor_value": 0.20,
            },
        )

    if _is_generic_short_false_positive(tokens):
        return _reject(
            phrase,
            "generic_short_false_positive",
            {
                "logical_structure": 0.40,
                "pragmatic_anchor_value": 0.15,
                "topic_coherence": 0.35,
            },
        )

    if _is_universal_weak_semantic_phrase(tokens):
        return _reject(
            phrase,
            "universal_weak_semantic_phrase",
            {
                "logical_structure": 0.35,
                "context_fit": 0.35,
                "pragmatic_anchor_value": 0.10,
                "topic_coherence": 0.30,
            },
        )

    return _accept(phrase, "guard_pass")