from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Set


try:
    from backend.server.stores.universal_noun_families import phrase_domain_cohesion
except ImportError:
    def phrase_domain_cohesion(tokens):
        return {
            "best_domain": "",
            "best_hits": set(),
            "best_hit_count": 0,
            "domain_count": 0,
            "cohesion_ratio": 0.0,
            "is_cohesive": False,
        }


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

WEAK_STARTS: Set[str] = {
    "because", "based", "with", "without", "before", "after", "during",
    "inside", "outside", "back", "such", "most", "many", "some", "few",
    "this", "that", "these", "those", "your", "people", "everyone",
    "someone", "anyone", "rather",
}

WEAK_ENDINGS: Set[str] = {
    "the", "a", "an", "of", "to", "for", "with", "without", "from", "into",
    "on", "at", "by", "because", "afterward", "afterwards", "later",
    "monthly", "financial", "unnecessary", "important", "clear", "short",
    "long", "near", "most",
}

WEAK_HEADS: Set[str] = {
    "thing", "things", "part", "parts", "area", "areas", "way", "ways",
    "type", "types", "point", "points", "example", "examples", "case",
    "cases", "time", "day", "days", "date", "length", "phase", "mix",
    "term", "terms", "stuff", "someone", "anyone",
}

STITCH_RISK_HEADS: Set[str] = {
    "products", "services", "fees", "renewal", "schedule", "payment",
    "payments", "data", "pricing", "plans", "rules", "benefits",
    "expectations", "performance", "information", "equipment", "invoice",
    "invoices", "taxes", "software", "inventory", "suppliers", "customers",
    "marketing", "salary", "revenue", "income", "expenses", "returns",
}

BOUNDARY_SPILLOVER_STARTS: Set[str] = {
    "previous", "next", "some", "many", "good", "better", "strongest",
    "cosmetic", "serious", "minor", "major", "important", "clear",
}

LONG_CLAUSE_LEAK_WORDS: Set[str] = {
    "can", "should", "would", "could", "is", "are", "was", "were",
    "be", "been", "being", "become", "becomes", "handled", "follow",
    "follows", "pay", "pays", "need", "needs", "know", "knows",
}


COHESION_WEAK_CHAIN_WORDS: Set[str] = {
    "expectations", "benefits", "performance", "information",
    "plans", "training", "rules", "reporting", "equipment",
    "price", "invoice", "schedule", "health", "data",
}

STRONG_CONCEPT_HEADS: Set[str] = {
    "strategy", "strategies", "checklist", "management", "software",
    "platform", "dashboard", "calculator", "forecast", "review",
    "analysis", "optimization", "system", "systems", "workflow",
    "workflows", "automation", "integration", "security", "pricing",
    "budget", "plan", "plans", "policy", "guide", "template",
    "framework", "model", "report", "audit", "ranking", "rankings",
    "analytics", "conversion", "traffic", "content", "keyword",
    "keywords", "backlink", "backlinks", "insurance", "mortgage",
    "contract", "agreement", "investment", "portfolio",
    "diversification", "fund", "capital", "revenue", "collection",
    "onboarding", "retention", "churn", "rate", "rates", "trend",
    "trends", "campaign", "landing", "page", "pages", "risk",
    "exposure", "account", "accounts", "receivable", "payable",
    "cash", "flow", "income", "expense", "expenses", "debt", "loan",
    "loans", "payment", "payments", "customer", "customers", "service",
    "services", "product", "products", "app", "application", "tool",
    "tools", "engine", "module", "modules", "schema", "score",
    "scoring", "topic", "topics", "cluster", "clusters", "entity",
    "entities", "schedule", "routine", "assessment", "performance",
    "settings", "benefits", "coverage", "delivery", "reservation",
    "menu", "checkout", "cart", "property", "lease", "tax", "taxes",
    "lesson", "course", "training", "resume", "interview", "symptoms",
    "causes", "treatment", "medication", "dosage", "therapy", "care",
    "support", "quality", "compliance", "flexibility", "construction",
    "allocation", "assets", "operations", "obligations", "invoices",
    "terms", "reminders", "deposits", "receipts", "returns",
}

NEUTRAL_NOUN_LIKE_HEADS: Set[str] = {
    "flexibility", "stability", "growth", "confidence", "priorities",
    "decisions", "goals", "costs", "fees", "repairs", "bills",
    "shortfalls", "emergencies", "suppliers", "employees", "owners",
    "investors", "markets", "sectors", "companies", "currency",
    "economy", "volatility", "maintenance", "appreciation",
}

STRONG_MODIFIER_WORDS: Set[str] = {
    "cash", "flow", "monthly", "personal", "business", "small",
    "customer", "onboarding", "pricing", "subscription", "email",
    "marketing", "project", "management", "analytics", "usage",
    "based", "technical", "seo", "keyword", "internal", "external",
    "conversion", "setup", "emergency", "working", "capital",
    "investment", "portfolio", "debt", "repayment", "budget",
    "content", "search", "landing", "product", "security",
    "enterprise", "billing", "legal", "real", "estate", "local",
    "medical", "health", "education", "travel", "restaurant",
    "automotive", "insurance", "construction", "manufacturing",
    "logistics", "energy", "telecommunications", "gaming",
    "parenting", "veterinary", "agriculture", "research",
    "wedding", "religion", "cybersecurity", "crypto",
    "sustainability", "accounts", "receivable", "payable",
    "interest", "risk", "late", "rental", "employment", "workplace",
    "unfair", "clinical", "commercial", "residential", "technical",
}

WEAK_ADJECTIVE_STARTS: Set[str] = {
    "useful", "strong", "weak", "good", "bad", "simple", "basic",
    "clear", "full", "important", "better", "best", "general",
    "common", "normal", "regular", "major", "minor", "new", "old",
    "easy", "quick", "perfect", "brief",
}

ACTION_STARTS: Set[str] = {
    "calculate", "track", "confirm", "compare", "choose", "check",
    "measure", "estimate", "build", "create", "fix", "improve",
    "optimize", "reduce", "increase", "manage", "review", "audit",
    "forecast", "plan", "analyze", "monitor", "test", "rank",
    "score", "publish", "import", "export", "sync", "validate",
    "prevent", "protect", "design", "write",
}

STRONG_ACTION_OBJECT_HEADS: Set[str] = {
    "risk", "churn", "retention", "conversion", "rate", "rankings",
    "outcomes", "collection", "cash", "traffic", "costs", "cost",
    "exposure", "frustration", "hesitation", "features", "plans",
    "accounts", "receivable", "payable", "budget", "performance",
    "security", "quality", "workflow", "workflows", "content",
    "links", "ranking", "revenue", "sales", "expenses", "debt",
    "interest", "payments", "flexibility",
}

WEAK_ACTION_OBJECT_HEADS: Set[str] = {
    "mix", "thing", "things", "stuff", "monthly", "financial",
    "unnecessary", "important", "clear", "short", "long", "term",
    "those", "this", "that", "these", "someone", "anyone",
}

VAGUE_ACTION_MODIFIERS: Set[str] = {
    "financial", "general", "basic", "common", "overall",
    "unnecessary", "important", "clear", "better", "strong",
    "weak", "personal",
}

LIST_CHAIN_WORDS: Set[str] = {
    "rent", "amount", "payment", "payments", "schedule", "security",
    "deposit", "maintenance", "responsibilities", "renewal", "terms",
    "rules", "income", "mortgage", "insurance", "costs", "taxes",
    "expenses", "vacancy", "losses", "products", "services", "fees",
    "pricing", "data", "equipment", "software", "inventory",
    "suppliers", "customers", "marketing", "payroll", "invoices",
    "screening", "agreement", "agreements", "property", "late",
    "landlord", "landlords", "lease", "leases",
}

SAFE_LONG_CONNECTORS: Set[str] = {
    "for", "to", "with", "without", "before", "after", "during",
    "when", "how", "why", "what", "which",
}

CLAUSE_VERBS: Set[str] = {
    "is", "are", "was", "were", "has", "have", "had", "do", "does",
    "did", "can", "could", "should", "would", "will", "may", "might",
    "runs", "run", "falls", "fall", "lands", "land", "becomes",
    "become", "means", "mean", "depends", "depend", "explains",
    "explain", "shows", "show", "happens", "happen", "works", "work",
    "holds", "hold", "starts", "start", "ends", "end", "uses", "use",
    "creates", "create", "improves", "improve", "increases",
    "increase", "reduces", "reduce", "guides", "guide", "summarizes",
    "summarize", "maps", "map", "contains", "contain", "mentions",
    "mention", "fits", "fit", "gains", "gain", "supports", "support",
    "combines", "combine", "understands", "understand", "helps", "help",
    "includes", "include", "provides", "provide", "offers", "offer",
    "requires", "require", "reveals", "reveal",
}

LIST_CONTEXT_WORDS: Set[str] = {
    "rent", "utilities", "groceries", "transport", "insurance",
    "subscriptions", "entertainment", "salary", "payments", "revenue",
    "investment", "returns", "income", "expenses", "stocks", "bonds",
    "funds", "cash", "reserves", "taxes", "software", "equipment",
    "payroll", "invoices", "suppliers", "customers", "marketing",
    "inventory", "products", "services", "fees", "renewal", "schedule",
    "payment", "data", "pricing", "plans",
}

BAD_FRAGMENT_PATTERNS = (
    r"\b(\w+)\s+\1\b",
    r"\bbased on\b",
    r"\bsuch as\b",
    r"\binside the\b",
    r"\bback into\b",
    r"\boutside the\b",
    r"\brather than\b",
    r"\bis one\b",
    r"\bis one of\b",
    r"\bthe product\b",
    r"\bthe application\b",
    r"\bthe page\b",
    r"\bthe site\b",
    r"\bhelps?\s+\w+\b",
)


def canonical_phrase(text: str) -> str:
    s = (text or "").strip().lower()
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"^\s*(?:\d+[\.\)]\s+|[•\-–]\s+)", "", s)
    s = re.sub(r"^[\"'“”‘’\(\[\{]+|[\"'“”‘’\)\]\}:;,\.\!\?]+$", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _has_boundary_spillover(tokens: List[str]) -> bool:
    if len(tokens) < 4:
        return False

    if tokens[0] in BOUNDARY_SPILLOVER_STARTS:
        return True

    if tokens[0] in STOPWORDS:
        return True

    if len(tokens) >= 5 and tokens[1] in BOUNDARY_SPILLOVER_STARTS:
        return True

    return False


def _has_long_clause_leakage(tokens: List[str]) -> bool:
    if len(tokens) < 5:
        return False

    if _is_query_style_long_anchor(tokens):
        return False

    return any(t in LONG_CLAUSE_LEAK_WORDS for t in tokens)

def _is_multi_cluster_phrase(tokens: List[str]) -> bool:
    if len(tokens) < 4:
        return False

    if _is_query_style_long_anchor(tokens):
        return False

    connector_count = sum(
        1 for t in tokens
        if t in SAFE_LONG_CONNECTORS or t in INTENT_CONNECTORS
    )

    pair_hits = 0
    total_pairs = max(1, len(tokens) - 1)

    for i in range(len(tokens) - 1):
        a = tokens[i]
        b = tokens[i + 1]

        if a in STOPWORDS or b in STOPWORDS:
            continue

        noun_like_a = (
            a in STRONG_MODIFIER_WORDS
            or a in STRONG_CONCEPT_HEADS
            or a in NEUTRAL_NOUN_LIKE_HEADS
            or a in LIST_CHAIN_WORDS
        )

        noun_like_b = (
            b in STRONG_CONCEPT_HEADS
            or b in NEUTRAL_NOUN_LIKE_HEADS
            or b in LIST_CHAIN_WORDS
        )

        if noun_like_a and noun_like_b:
            pair_hits += 1

    ratio = pair_hits / total_pairs

    if len(tokens) >= 4 and ratio >= 0.75 and connector_count == 0:
        return True

    if len(tokens) >= 5 and ratio >= 0.67 and connector_count <= 1:
        return True

    return False

def _has_orphan_tail_start(tokens: List[str]) -> bool:
    if len(tokens) < 3:
        return False

    orphan_starts = {
        "agreements", "payments", "costs", "responsibilities",
        "terms", "rules", "expenses", "taxes", "invoices",
        "fees", "services", "products", "landlords",
    }

    if tokens[0] in orphan_starts:
        return True

    return False


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]


def phrase_key(phrase: str) -> str:
    return " ".join(tokenize(canonical_phrase(phrase)))


def _is_long_list_chain(tokens: List[str]) -> bool:
    if len(tokens) < 5:
        return False

    chain_hits = sum(1 for t in tokens if t in LIST_CHAIN_WORDS)
    connector_hits = sum(1 for t in tokens if t in SAFE_LONG_CONNECTORS)

    if chain_hits >= 4 and connector_hits == 0:
        return True

    if len(tokens) >= 6 and chain_hits / max(1, len(tokens)) >= 0.55 and connector_hits <= 1:
        return True

    return False

def _is_action_phrase(tokens: List[str]) -> bool:
    return bool(tokens and tokens[0] in ACTION_STARTS)


def _content_tokens(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in STOPWORDS]


def _has_bad_fragment_pattern(p: str) -> bool:
    return any(re.search(pat, p) for pat in BAD_FRAGMENT_PATTERNS)


INTENT_CONNECTORS: Set[str] = {
    "for", "to", "at", "before", "after", "with", "without", "during",
    "in", "on", "near", "between", "among", "against",
}

QUERY_STYLE_STARTS: Set[str] = {
    "best", "how", "when", "what", "why", "where", "which",
    "can", "should", "does", "do", "is", "are",
}


def _has_mid_stopword(tokens: List[str]) -> bool:
    if len(tokens) < 3:
        return False

    middle = tokens[1:-1]

    if len(tokens) >= 5:
        bad_middle = [
            t for t in middle
            if t in STOPWORDS and t not in INTENT_CONNECTORS
        ]
        return bool(bad_middle)

    return any(t in STOPWORDS for t in middle)

def _is_query_style_long_anchor(tokens: List[str]) -> bool:
    if len(tokens) < 5:
        return False

    if tokens[0] not in QUERY_STYLE_STARTS:
        return False

    middle = tokens[1:-1]

    has_intent_connector = any(t in INTENT_CONNECTORS for t in middle)
    content_count = len(_content_tokens(tokens))

    return has_intent_connector and content_count >= 3

def _has_clause_verb_leakage(tokens: List[str]) -> bool:
    if not tokens:
        return True

    if _is_action_phrase(tokens):
        return any(t in CLAUSE_VERBS for t in tokens[1:])

    return any(t in CLAUSE_VERBS for t in tokens)


def _is_weak_adjective_phrase(tokens: List[str]) -> bool:
    if not tokens:
        return True
    if tokens[0] not in WEAK_ADJECTIVE_STARTS:
        return False
    
    if _is_query_style_long_anchor(tokens):
     return False

    strong_mods = sum(1 for t in tokens[1:-1] if t in STRONG_MODIFIER_WORDS)
    has_strong_head = bool(tokens and tokens[-1] in STRONG_CONCEPT_HEADS)

    return not (len(tokens) >= 4 and strong_mods >= 1 and has_strong_head)


def _is_list_pair_fragment(tokens: List[str]) -> bool:
    if len(tokens) != 2:
        return False

    left, right = tokens

    if left in LIST_CONTEXT_WORDS and right in LIST_CONTEXT_WORDS:
        if left in STRONG_MODIFIER_WORDS and right in STRONG_CONCEPT_HEADS:
            return False
        return True

    if right in {"software", "insurance", "mortgage", "investment", "taxes"}:
        if left not in STRONG_MODIFIER_WORDS:
            return True

    return False


def _is_list_style_stack(tokens: List[str]) -> bool:
    if len(tokens) < 3:
        return False

    if _is_action_phrase(tokens):
        head = tokens[-1]
        if head in STRONG_ACTION_OBJECT_HEADS or head in STRONG_CONCEPT_HEADS:
            return False

    list_count = sum(1 for t in tokens if t in LIST_CONTEXT_WORDS)
    if list_count >= 3:
        return True

    stitch_count = sum(1 for t in tokens if t in STITCH_RISK_HEADS)
    if len(tokens) in {3, 4} and stitch_count >= 2:
        strong_mods = sum(1 for t in tokens[:-1] if t in STRONG_MODIFIER_WORDS)
        if strong_mods == 0:
            return True

    if len(tokens) >= 3 and tokens[-1] not in STRONG_CONCEPT_HEADS:
        strong_mods = sum(1 for t in tokens[:-1] if t in STRONG_MODIFIER_WORDS)
        if strong_mods == 0:
            return True

    return False


def _should_trim_bad_long_phrase(tokens: List[str]) -> bool:
    if len(tokens) < 5:
        return False

    # Keep true query-style long anchors
    if _is_query_style_long_anchor(tokens):
        return False

    # Keep connector-rich unified phrases
    connector_count = sum(
        1 for t in tokens
        if t in INTENT_CONNECTORS or t in SAFE_LONG_CONNECTORS
    )
    if connector_count >= 2:
        return False

    # Trim only obvious action/list/chained phrases
    if _is_long_list_chain(tokens):
        return True

    if _is_multi_cluster_phrase(tokens):
        return True

    if _is_action_phrase(tokens) and len(tokens) >= 5:
        return True

    return False


def trim_bad_long_phrase(tokens: List[str]) -> List[str]:
    if len(tokens) < 5:
        return tokens

    best_span = tokens
    best_rank = -1.0

    max_window = min(5, len(tokens))

    for size in range(2, max_window + 1):
        for i in range(0, len(tokens) - size + 1):
            span = tokens[i:i + size]
            phrase = " ".join(span)

            result = score_phrase_strength(phrase)

            if not result.get("keep"):
                continue

            score = float(result.get("score") or 0.0)

            specificity = 0.0
            specificity += 0.04 * sum(1 for t in span if t in STRONG_MODIFIER_WORDS)
            specificity += 0.03 * sum(1 for t in span if t in STRONG_CONCEPT_HEADS)
            specificity += 0.03 * sum(1 for t in span if t in INTENT_CONNECTORS)
            specificity += 0.02 * len(span)

            # Prefer meaningful specific spans, not blindly shortest spans.
            rank = score + specificity

            if rank > best_rank:
                best_rank = rank
                best_span = span

    return best_span


def _is_short_orphan_collision(tokens: List[str]) -> bool:
    if len(tokens) not in {2, 3}:
        return False

    if _is_query_style_long_anchor(tokens):
        return False

    phrase_tuple = tuple(tokens)

    safe_pairs = {
        ("cash", "flow"),
        ("lease", "agreement"),
        ("late", "payment"),
        ("late", "fee"),
        ("fee", "policy"),
        ("rental", "income"),
        ("rental", "property"),
        ("property", "management"),
        ("property", "maintenance"),
        ("payment", "reminders"),
        ("mortgage", "payments"),
        ("insurance", "costs"),
        ("emergency", "repairs"),
        ("keyword", "research"),
        ("content", "optimization"),
        ("internal", "linking"),
        ("conversion", "rate"),
        ("risk", "management"),
        ("customer", "service"),
        ("data", "security"),
    }

    safe_triples = {
        ("late", "fee", "policy"),
        ("rental", "property", "management"),
        ("internal", "linking", "strategy"),
        ("content", "optimization", "strategy"),
        ("customer", "service", "workflow"),
        ("risk", "management", "framework"),
        ("data", "security", "policy"),
    }

    if phrase_tuple in safe_pairs or phrase_tuple in safe_triples:
        return False

    orphan_starts = {
        "agreements", "payments", "costs", "responsibilities",
        "terms", "rules", "expenses", "taxes", "invoices",
        "fees", "services", "products", "landlords",
        "schedule", "tenancy", "serious", "previous",
    }

    if tokens[0] in orphan_starts:
        return True

    noun_like_count = 0
    for t in tokens:
        if (
            t in STRONG_CONCEPT_HEADS
            or t in NEUTRAL_NOUN_LIKE_HEADS
            or t in LIST_CHAIN_WORDS
            or t in STITCH_RISK_HEADS
        ):
            noun_like_count += 1

    if noun_like_count == len(tokens):
        has_strong_modifier = any(t in STRONG_MODIFIER_WORDS for t in tokens[:-1])
        has_natural_head = tokens[-1] in STRONG_CONCEPT_HEADS or tokens[-1] in NEUTRAL_NOUN_LIKE_HEADS

        if not has_strong_modifier and has_natural_head:
            return True

    return False


def _has_vague_action_modifier(tokens: List[str]) -> bool:
    if len(tokens) < 3:
        return False

    if not _is_action_phrase(tokens):
        return False

    return any(t in VAGUE_ACTION_MODIFIERS for t in tokens[1:-1])


def _is_prefix_suffix_spillover(tokens: List[str]) -> bool:
    if len(tokens) < 2:
        return False

    if tokens[0] in STOPWORDS:
        return True

    if len(tokens) >= 3 and tokens[1] in WEAK_ADJECTIVE_STARTS:
        return True

    if len(tokens) == 3:
        first_two = tuple(tokens[:2])
        last_two = tuple(tokens[1:])

        known_safe_pairs = {
            ("cash", "flow"),
            ("lease", "agreement"),
            ("late", "payment"),
            ("late", "fee"),
            ("fee", "policy"),
            ("rental", "income"),
            ("rental", "property"),
            ("property", "management"),
            ("property", "maintenance"),
            ("payment", "reminders"),
            ("mortgage", "payments"),
            ("insurance", "costs"),
            ("emergency", "repairs"),
            ("keyword", "research"),
            ("content", "optimization"),
            ("internal", "linking"),
            ("conversion", "rate"),
            ("risk", "management"),
            ("customer", "service"),
            ("data", "security"),
        }

        if first_two in known_safe_pairs and last_two not in known_safe_pairs:
            return True

    return False

def _has_structural_signal(tokens: List[str], source_type: str) -> tuple[bool, List[str]]:
    signals: List[str] = []

    if not tokens:
        return False, signals

    head = tokens[-1]
    modifiers = tokens[:-1]

    if head in STRONG_CONCEPT_HEADS:
        signals.append("structural_strong_head")

    if any(t in STRONG_MODIFIER_WORDS for t in modifiers) and (
        head in STRONG_CONCEPT_HEADS
        or head in NEUTRAL_NOUN_LIKE_HEADS
        or head in STRONG_ACTION_OBJECT_HEADS
    ):
        signals.append("structural_modifier_head")

    if source_type in {"title", "heading_h1", "heading_h2", "heading_h3", "intent", "list"}:
        signals.append("structural_trusted_source")

    cohesion = phrase_domain_cohesion(set(tokens))
    if bool(cohesion.get("is_cohesive")):
        signals.append("structural_domain_cohesion")

    if _is_action_phrase(tokens) and head in STRONG_ACTION_OBJECT_HEADS:
        signals.append("structural_action_object")

    return bool(signals), signals


def _short_window_structure_penalty(tokens: List[str], source_type: str) -> tuple[float, List[str]]:
    reasons: List[str] = []
    score = 0.0

    if len(tokens) not in {2, 3, 4}:
        return score, reasons

    has_signal, signal_reasons = _has_structural_signal(tokens, source_type)
    reasons.extend(signal_reasons)

    if not has_signal:
        score -= 0.45
        reasons.append("short_window_missing_structure")

    if _is_list_style_stack(tokens):
        score -= 0.30
        reasons.append("short_window_stitched_sequence")

    return score, reasons


def _long_phrase_naturalness_score(tokens: List[str], source_type: str) -> tuple[float, List[str]]:
    reasons: List[str] = []
    score = 0.0

    if len(tokens) < 5:
        return score, reasons

    if _is_long_list_chain(tokens):
        score -= 0.95
        reasons.append("long_list_chain")

    content_count = len(_content_tokens(tokens))
    head = tokens[-1]

    if content_count >= 4:
        score += 0.12
        reasons.append("long_contentful_phrase")

    if head in STRONG_CONCEPT_HEADS or head in STRONG_ACTION_OBJECT_HEADS:
        score += 0.12
        reasons.append("long_clear_head")

    if source_type in {"title", "heading_h1", "heading_h2", "heading_h3", "intent"}:
        score += 0.10
        reasons.append("long_trusted_source")

    if _has_mid_stopword(tokens):
        score -= 0.18
        reasons.append("long_mid_stopword_risk")

    if _is_list_style_stack(tokens):
        has_signal, _signals = _has_structural_signal(tokens, source_type)
        if _is_query_style_long_anchor(tokens):
            score += 0.40
            reasons.append("long_query_style_anchor")
        elif has_signal:
            score += 0.08
            reasons.append("long_structured_phrase")
        else:
            score -= 0.45
            reasons.append("long_list_stack")

    if len(tokens) >= 9:
        score -= 0.35
        reasons.append("overlong_anchor")

    return score, reasons


def _modifier_quality_score(tokens: List[str]) -> tuple[float, List[str]]:
    reasons: List[str] = []
    score = 0.0

    if len(tokens) < 2:
        return -0.50, ["missing_modifier"]

    modifiers = tokens[:-1]

    strong_mod_count = sum(1 for t in modifiers if t in STRONG_MODIFIER_WORDS)
    weak_adj_count = sum(1 for t in modifiers if t in WEAK_ADJECTIVE_STARTS)
    stopword_count = sum(1 for t in modifiers if t in STOPWORDS)

    if strong_mod_count >= 1:
        score += 0.18
        reasons.append("specific_modifier")

    if strong_mod_count >= 2:
        score += 0.10
        reasons.append("multi_specific_modifier")

    if weak_adj_count >= 1:
        score -= 0.20
        reasons.append("weak_modifier")

    if stopword_count:
        score -= 0.25
        reasons.append("stopword_modifier")

    if len(modifiers) == 1 and modifiers[0] in WEAK_ADJECTIVE_STARTS:
        score -= 0.25
        reasons.append("thin_modifier")

    return score, reasons


def _head_quality_score(tokens: List[str]) -> tuple[float, List[str]]:
    reasons: List[str] = []
    score = 0.0

    if not tokens:
        return -1.0, ["missing_head"]

    head = tokens[-1]

    if head in STRONG_CONCEPT_HEADS:
        score += 0.35
        reasons.append("strong_head")
    elif head in WEAK_HEADS:
        score -= 0.45
        reasons.append("weak_head")
    elif head in NEUTRAL_NOUN_LIKE_HEADS:
        score += 0.05
        reasons.append("neutral_noun_head")
    else:
        score -= 0.02
        reasons.append("unknown_head")

    return score, reasons


def _standalone_score(tokens: List[str], source_type: str) -> tuple[float, List[str]]:
    reasons: List[str] = []
    score = 0.0

    if len(tokens) in {2, 3, 4}:
        score += 0.08
        reasons.append("clean_short_length")
    elif 5 <= len(tokens) <= 8:
        score += 0.02
        reasons.append("allowed_long_anchor")
    elif len(tokens) >= 9:
        score -= 0.20
        reasons.append("too_long_for_anchor")

    if source_type in {"title", "heading_h1", "heading_h2", "heading_h3", "intent", "list"}:
        score += 0.10
        reasons.append("trusted_source")

    content_count = len(_content_tokens(tokens))
    if content_count >= 2:
        score += 0.10
        reasons.append("contentful")
    else:
        score -= 0.30
        reasons.append("low_content")

    if len(tokens) >= 3:
        unique_ratio = len(set(tokens)) / max(1, len(tokens))
        if unique_ratio < 0.80:
            score -= 0.12
            reasons.append("low_unique_ratio")

    return score, reasons


def _action_object_score(tokens: List[str]) -> tuple[float, List[str]]:
    reasons: List[str] = []
    score = 0.0

    if not _is_action_phrase(tokens):
        return 0.0, []

    if len(tokens) < 2:
        return -0.60, ["missing_action_object"]

    obj = tokens[-1]

    if len(tokens) > 6:
        score -= 0.20
        reasons.append("overextended_action")

    if obj in WEAK_ACTION_OBJECT_HEADS or obj in WEAK_HEADS:
        score -= 0.45
        reasons.append("weak_action_object")
    elif obj in STRONG_ACTION_OBJECT_HEADS or obj in STRONG_CONCEPT_HEADS:
        score += 0.35
        reasons.append("clear_action_object")
    elif obj in NEUTRAL_NOUN_LIKE_HEADS:
        score += 0.08
        reasons.append("neutral_action_object")
    else:
        score -= 0.10
        reasons.append("unclear_action_object")

    if len(tokens) >= 3 and tokens[1] in WEAK_ENDINGS:
        score -= 0.20
        reasons.append("weak_action_modifier")

    if _has_vague_action_modifier(tokens):
        score -= 0.45
        reasons.append("vague_action_modifier")

    return score, reasons


def _cohesion_penalty(tokens: List[str]) -> tuple[float, List[str]]:
    reasons: List[str] = []
    score = 0.0

    if len(tokens) < 2:
        return score, reasons

    natural_patterns = (
        ("lease", "agreement"),
        ("rental", "contract"),
        ("late", "fee", "policy"),
        ("contract", "risk", "management"),
        ("risk", "management"),
        ("invoice", "schedule"),
        ("employment", "policy"),
        ("workplace", "policy"),
        ("unfair", "treatment"),
        ("cash", "flow"),
        ("budget", "review"),
        ("conversion", "rate"),
        ("setup", "checklist"),
        ("pricing", "strategy"),
        ("payment", "schedule"),
        ("product", "pricing"),
        ("customer", "service"),
        ("renewal", "schedule"),
        ("subscription", "pricing"),
        ("data", "security"),
        ("internal", "linking", "strategy"),
        ("keyword", "research"),
        ("content", "optimization"),
    )

    for pattern in natural_patterns:
        if tuple(tokens) == pattern:
            score += 0.20
            reasons.append("natural_phrase_pattern")
            return score, reasons

    if len(tokens) == 2:
        a, b = tokens

        if a in COHESION_WEAK_CHAIN_WORDS and b in COHESION_WEAK_CHAIN_WORDS:
            score -= 0.45
            reasons.append("weak_cohesion_pair")

    if len(tokens) >= 3:
        weak_count = sum(1 for t in tokens if t in COHESION_WEAK_CHAIN_WORDS)

        if weak_count >= 2 and tokens[-1] not in {
            "policy", "contract", "agreement", "management",
            "checklist", "strategy", "review", "schedule",
            "security", "pricing", "plan", "plans",
        }:
            score -= 0.50
            reasons.append("weak_cohesion_chain")

    return score, reasons


def _domain_cohesion_score(tokens: List[str]) -> tuple[float, List[str]]:
    reasons: List[str] = []
    score = 0.0

    if len(tokens) < 2:
        return score, reasons

    info = phrase_domain_cohesion(set(tokens))

    is_cohesive = bool(info.get("is_cohesive"))
    cohesion_ratio = float(info.get("cohesion_ratio") or 0.0)
    best_hit_count = int(info.get("best_hit_count") or 0)
    domain_count = int(info.get("domain_count") or 0)

    if is_cohesive:
        score += 0.18
        reasons.append("domain_cohesive")
    elif len(tokens) >= 3 and best_hit_count <= 1:
        score -= 0.35
        reasons.append("low_domain_cohesion")
    elif len(tokens) >= 3 and domain_count >= 3 and cohesion_ratio < 0.67:
        score -= 0.25
        reasons.append("scattered_domain_terms")

    return score, reasons


def _fragment_penalty(tokens: List[str], p: str) -> tuple[float, List[str]]:
    reasons: List[str] = []
    score = 0.0

    if _has_bad_fragment_pattern(p):
        score -= 0.60
        reasons.append("bad_fragment_pattern")

    if _has_mid_stopword(tokens):
        score -= 0.45
        reasons.append("mid_stopword_fragment")

    if _has_clause_verb_leakage(tokens):
        score -= 0.55
        reasons.append("clause_verb_leakage")

    if _is_list_pair_fragment(tokens):
        score -= 0.50
        reasons.append("list_pair_fragment")

    if _is_list_style_stack(tokens):
        has_signal, _signals = _has_structural_signal(tokens, "")
        if _is_query_style_long_anchor(tokens):
            score += 0.35
            reasons.append("query_style_long_anchor")
        elif has_signal:
            score += 0.08
            reasons.append("structured_phrase_not_list_stack")
        else:
            score -= 0.50
            reasons.append("list_style_stack")

    if _is_weak_adjective_phrase(tokens):
        score -= 0.35
        reasons.append("weak_adjective_phrase")

    return score, reasons

def score_phrase_strength(
    phrase: str,
    *,
    source_type: str = "",
    allow_trim: bool = True,
) -> Dict[str, Any]:
    p = canonical_phrase(phrase)
    tokens = tokenize(p)

    if not p or len(tokens) < 2:
        return {"keep": False, "score": 0.0, "reason": "too_short"}

    if len(tokens) > 10:
        return {"keep": False, "score": 0.0, "reason": "too_long"}

    if _should_trim_bad_long_phrase(tokens):
        trimmed = trim_bad_long_phrase(tokens)
        if trimmed != tokens:
            p = " ".join(trimmed)
            tokens = trimmed

    if _is_long_list_chain(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "reason": "long_list_chain",
        }

    if _is_multi_cluster_phrase(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "reason": "multi_cluster_phrase",
        }
    

    if _is_short_orphan_collision(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "reason": "short_orphan_collision",
        }
    
    if _is_prefix_suffix_spillover(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "reason": "prefix_suffix_spillover",
        }

    if _has_orphan_tail_start(tokens):
         return {
            "keep": False,
            "score": 0.0,
            "reason": "orphan_tail_start",
        }

    if _has_boundary_spillover(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "reason": "boundary_spillover",
        }

    if _has_long_clause_leakage(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "reason": "long_clause_leakage",
        }



    if tokens[0] in WEAK_STARTS:
        return {"keep": False, "score": 0.10, "reason": "weak_start"}

    if tokens[-1] in WEAK_ENDINGS:
        return {"keep": False, "score": 0.10, "reason": "weak_ending"}

    score = 0.40
    reasons: List[str] = []

    head_score, head_reasons = _head_quality_score(tokens)
    modifier_score, modifier_reasons = _modifier_quality_score(tokens)
    standalone_score, standalone_reasons = _standalone_score(tokens, source_type)
    fragment_score, fragment_reasons = _fragment_penalty(tokens, p)
    cohesion_score, cohesion_reasons = _cohesion_penalty(tokens)
    domain_score, domain_reasons = _domain_cohesion_score(tokens)
    action_score, action_reasons = _action_object_score(tokens)
    short_window_score, short_window_reasons = _short_window_structure_penalty(tokens, source_type)
    long_phrase_score, long_phrase_reasons = _long_phrase_naturalness_score(tokens, source_type)

    score += head_score
    score += modifier_score
    score += standalone_score
    score += fragment_score
    score += cohesion_score
    score += domain_score
    score += action_score
    score += short_window_score
    score += long_phrase_score

    reasons.extend(head_reasons)
    reasons.extend(modifier_reasons)
    reasons.extend(standalone_reasons)
    reasons.extend(fragment_reasons)
    reasons.extend(cohesion_reasons)
    reasons.extend(domain_reasons)
    reasons.extend(action_reasons)
    reasons.extend(short_window_reasons)
    reasons.extend(long_phrase_reasons)

    score = max(0.0, min(1.0, round(score, 3)))

    if _is_query_style_long_anchor(tokens):
        content_count = len(_content_tokens(tokens))
        if content_count >= 4:
            score = max(score, 0.78)
            reasons.append("query_style_score_floor")

    threshold = 0.72

    if _is_action_phrase(tokens):
        threshold = 0.76

    if len(tokens) in {2, 3, 4}:
        threshold = max(threshold, 0.78)

    if len(tokens) >= 5:
        threshold = 0.74

    keep = score >= threshold

    return {
        "keep": keep,
        "score": score,
        "phrase": p,
        "reason": "+".join(reasons) if reasons else "neutral",
}