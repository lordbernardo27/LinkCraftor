from __future__ import annotations

import re
from typing import Any, Dict, List, Set, Tuple


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

VALID_ORDERED_PAIRS: Set[Tuple[str, str]] = {
    ("cash", "flow"), ("blood", "pressure"), ("internal", "linking"),
    ("external", "linking"), ("search", "intent"), ("supply", "chain"),
    ("remote", "work"), ("content", "marketing"), ("email", "marketing"),
    ("social", "media"), ("machine", "learning"), ("artificial", "intelligence"),
    ("real", "estate"), ("credit", "card"), ("credit", "cards"),
    ("interest", "rate"), ("interest", "rates"), ("rental", "agreement"),
    ("lease", "agreement"), ("category", "pages"), ("product", "pages"),
    ("side", "effects"), ("risk", "management"), ("customer", "service"),
    ("data", "security"), ("keyword", "research"), ("content", "optimization"),
    ("conversion", "rate"), ("payment", "schedule"), ("late", "payment"),
    ("late", "fee"), ("study", "plan"), ("learning", "platform"),
    ("progress", "tracking"), ("recorded", "lesson"), ("completion", "rates"),

    # Universal health/fertility compound patterns
    ("fertile", "window"), ("cycle", "length"), ("follicular", "phase"),
    ("luteal", "phase"), ("cervical", "mucus"), ("menstrual", "period"),
    ("basal", "body"), ("body", "temperature"), ("birth", "control"),
    ("fertility", "tracking"), ("ovulation", "predictor"),
    ("ovulation", "calculator"), ("expected", "ovulation"),
    ("irregular", "periods"),
}

REVERSED_ORDERED_PAIRS: Set[Tuple[str, str]] = {(b, a) for a, b in VALID_ORDERED_PAIRS}

CANONICAL_ANCHOR_PHRASES: Set[str] = {
    "cash flow", "cash flow management", "blood pressure", "blood pressure control",
    "internal linking", "internal linking strategy", "external linking", "search intent",
    "category pages", "product pages", "rental agreement", "lease agreement",
    "side effects", "supply chain", "remote work", "content marketing",
    "email marketing", "machine learning", "risk management", "customer service",
    "data security", "keyword research", "content optimization", "conversion rate",
    "payment schedule", "late payment", "late fee", "study plan", "learning platform",
    "progress tracking", "recorded lesson", "completion rates",

    # Fertility / cycle tracking anchors
    "fertile window", "cycle length", "follicular phase", "luteal phase",
    "cervical mucus", "cervical mucus patterns", "ovulation predictor kits",
    "last menstrual period", "typical cycle length", "shortest and longest cycle",
    "expected ovulation", "irregular periods", "stopping birth control",
    "fertility tracking", "basal body temperature", "strong positive opk",
}

WEAK_STARTS: Set[str] = {
    "because", "based", "with", "without", "before", "after", "during",
    "inside", "outside", "back", "such", "most", "many", "some", "few",
    "this", "that", "these", "those", "your", "people", "everyone",
    "someone", "anyone", "rather", "quickly", "slowly", "face", "facing",
    "thing", "things", "various", "different", "same", "another", "re",
}

WEAK_ENDINGS: Set[str] = {
    "the", "a", "an", "of", "to", "for", "with", "without", "from", "into",
    "on", "at", "by", "because", "afterward", "afterwards", "later",
    "monthly", "financial", "unnecessary", "important", "clear", "short",
    "long", "near", "most", "thing", "things", "way", "ways", "area",
    "areas", "part", "parts", "one", "such", "instead", "ahead", "faster",
    "slower", "well", "better", "valuable", "based", "depended", "anywhere",
}

WEAK_HEADS: Set[str] = {
    "thing", "things", "part", "parts", "area", "areas", "way", "ways",
    "type", "types", "point", "points", "example", "examples", "case",
    "cases", "time", "day", "days", "date", "mix", "term",
    "terms", "stuff", "someone", "anyone", "routine", "routines",
}

GENERIC_BUT_ALLOWED_HEADS: Set[str] = {
    "time", "day", "days", "date", "length", "method", "methods",
    "option", "options", "routine", "routines", "system", "systems",
    "course", "courses", "care", "plan", "plans", "process", "processes",
    "window", "cycle", "cycles", "phase", "phases", "pattern", "patterns",
    "signal", "signals", "tool", "tools", "kit", "kits", "calculator",
    "tracking", "guide", "strategy", "framework", "checklist", "template",
    "score", "rate", "rates", "period", "periods", "temperature",
}

STRONG_CONCEPT_HEADS: Set[str] = {
    "strategy", "strategies", "checklist", "management", "software",
    "platform", "dashboard", "calculator", "forecast", "review",
    "analysis", "optimization", "system", "systems", "workflow",
    "workflows", "automation", "integration", "security", "pricing",
    "budget", "plan", "plans", "policy", "guide", "template",
    "framework", "model", "report", "audit", "ranking", "rankings",
    "analytics", "conversion", "traffic", "content", "keyword",
    "keywords", "insurance", "mortgage", "contract", "agreement",
    "investment", "portfolio", "revenue", "collection", "onboarding",
    "retention", "churn", "rate", "rates", "trend", "trends",
    "campaign", "page", "pages", "risk", "account", "accounts",
    "cash", "flow", "income", "expense", "expenses", "debt", "loan",
    "loans", "payment", "payments", "customer", "customers", "service",
    "services", "product", "products", "app", "application", "tool",
    "tools", "engine", "module", "modules", "schema", "score",
    "scoring", "topic", "topics", "cluster", "clusters", "entity",
    "entities", "schedule", "assessment", "performance", "settings",
    "benefits", "coverage", "delivery", "property", "lease", "tax",
    "taxes", "lesson", "course", "training", "resume", "interview",
    "symptoms", "causes", "treatment", "medication", "dosage",
    "therapy", "support", "quality", "compliance", "flexibility",
    "operations", "invoices", "terms", "environment", "tracking",

    # Health/fertility heads
    "ovulation", "fertility", "period", "periods", "cycle", "cycles",
    "phase", "phases", "window", "length", "temperature", "mucus",
    "patterns", "kit", "kits", "opk",
}

NEUTRAL_NOUN_LIKE_HEADS: Set[str] = {
    "flexibility", "stability", "growth", "confidence", "priorities",
    "decisions", "goals", "costs", "fees", "repairs", "bills",
    "suppliers", "employees", "owners", "investors", "markets",
    "sectors", "companies", "currency", "economy", "maintenance",
}

STRONG_MODIFIER_WORDS: Set[str] = {
    "cash", "flow", "monthly", "personal", "business", "small",
    "customer", "pricing", "subscription", "email", "marketing",
    "project", "management", "analytics", "technical", "seo",
    "keyword", "internal", "external", "conversion", "content",
    "search", "product", "security", "enterprise", "billing",
    "legal", "real", "estate", "local", "medical", "health",
    "education", "travel", "insurance", "construction", "research",
    "risk", "late", "rental", "clinical", "commercial", "blood",
    "pressure", "remote", "machine", "learning", "supply", "chain",
    "category", "study", "progress", "recorded", "completion",
    "online", "effective", "digital", "student", "students",

    # Fertility modifiers
    "fertile", "cycle", "typical", "shortest", "longest", "follicular",
    "luteal", "cervical", "mucus", "ovulation", "predictor", "last",
    "menstrual", "expected", "irregular", "fertility", "basal", "body",
    "birth", "control", "strong", "positive",
}

WEAK_ADJECTIVE_STARTS: Set[str] = {
    "useful", "weak", "good", "bad", "simple", "basic",
    "clear", "full", "important", "better", "best", "general",
    "common", "normal", "regular", "major", "minor", "new", "old",
    "easy", "quick", "perfect", "brief", "same", "valuable",
    "healthy", "traditional", "different", "various",
}

UNIVERSAL_WEAK_PREFIXES: Set[str] = {
    "same", "another", "various", "different", "valuable", "general",
    "specific", "certain", "particular", "healthy", "simple", "basic",
    "normal", "regular", "traditional", "random", "minor", "major",
}

UNIVERSAL_WEAK_HEADS: Set[str] = {
    "system", "systems", "course", "courses", "care", "routine",
    "routines", "thing", "things", "area", "areas", "part", "parts",
    "method", "methods", "option", "options", "way", "ways",
}

ACTION_STARTS: Set[str] = {
    "calculate", "track", "confirm", "compare", "choose", "check",
    "measure", "estimate", "build", "create", "fix", "improve",
    "optimize", "reduce", "increase", "manage", "review", "audit",
    "forecast", "plan", "analyze", "monitor", "test", "rank",
    "score", "publish", "import", "export", "sync", "validate",
    "prevent", "protect", "design", "write", "stopping",
}

STRONG_ACTION_OBJECT_HEADS: Set[str] = {
    "risk", "churn", "retention", "conversion", "rate", "rankings",
    "outcomes", "collection", "cash", "traffic", "costs", "cost",
    "features", "plans", "accounts", "budget", "performance",
    "security", "quality", "workflow", "workflows", "content",
    "links", "ranking", "revenue", "sales", "expenses", "debt",
    "interest", "payments", "flexibility", "plan", "control",
}

WEAK_ACTION_OBJECT_HEADS: Set[str] = {
    "mix", "thing", "things", "stuff", "monthly", "financial",
    "unnecessary", "important", "clear", "short", "long", "term",
    "those", "this", "that", "these", "someone", "anyone",
}

VAGUE_ACTION_MODIFIERS: Set[str] = {
    "financial", "general", "basic", "common", "overall",
    "unnecessary", "important", "clear", "better", "weak", "personal",
}

LIST_CHAIN_WORDS: Set[str] = {
    "rent", "amount", "payment", "payments", "schedule", "security",
    "deposit", "maintenance", "responsibilities", "renewal", "terms",
    "rules", "income", "mortgage", "insurance", "costs", "taxes",
    "expenses", "products", "services", "fees", "pricing", "data",
    "equipment", "software", "inventory", "suppliers", "customers",
    "marketing", "payroll", "invoices", "screening", "agreement",
    "agreements", "property", "late", "lease", "loan", "loans",
    "revenue", "cash", "flow",
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
    "requires", "require", "reveals", "reveal", "depended", "designed",
    "move", "moves",
}

LIST_CONTEXT_WORDS: Set[str] = {
    "rent", "utilities", "groceries", "transport", "insurance",
    "subscriptions", "salary", "payments", "revenue", "investment",
    "returns", "income", "expenses", "stocks", "bonds", "funds",
    "cash", "reserves", "taxes", "software", "equipment", "payroll",
    "invoices", "suppliers", "customers", "marketing", "inventory",
    "products", "services", "fees", "schedule", "payment", "data",
    "pricing", "plans", "loan", "loans",
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

INTENT_CONNECTORS: Set[str] = {
    "for", "to", "at", "before", "after", "with", "without", "during",
    "in", "on", "near", "between", "among", "against",
}

QUERY_STYLE_STARTS: Set[str] = {
    "best", "how", "when", "what", "why", "where", "which",
    "can", "should", "does", "do", "is", "are",
}

ADVERB_FRAGMENT_STARTS: Set[str] = {
    "especially", "almost", "passively", "today", "yesterday",
    "quickly", "slowly", "currently", "recently", "otherwise",
}

SENTENCE_FRAGMENT_ENDS: Set[str] = {
    "instead", "ahead", "faster", "slower", "well", "better",
    "valuable", "based", "depended", "anywhere", "often",
}


def canonical_phrase(text: str) -> str:
    s = (text or "").strip().lower()
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2013", "-").replace("\u2014", "-")
    s = s.replace("\u2026", "...")
    s = s.replace("\u00a0", " ")
    s = re.sub(r"^\s*(?:\d+[\.\)]\s+|[•\-]\s+)", "", s)
    s = re.sub(r"^[\"'\(\[\{]+|[\"'\)\]\}:;,\.\!\?]+$", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]


def phrase_key(phrase: str) -> str:
    return " ".join(tokenize(canonical_phrase(phrase)))


def _content_tokens(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in STOPWORDS]


def _phrase_from_tokens(tokens: List[str]) -> str:
    return " ".join(tokens)


def _has_bad_fragment_pattern(p: str) -> bool:
    return any(re.search(pat, p) for pat in BAD_FRAGMENT_PATTERNS)


def _has_valid_ordered_pair(tokens: List[str]) -> bool:
    return any(pair in VALID_ORDERED_PAIRS for pair in zip(tokens, tokens[1:]))


def _has_reversed_ordered_pair(tokens: List[str]) -> bool:
    return any(pair in REVERSED_ORDERED_PAIRS for pair in zip(tokens, tokens[1:]))


def _contains_canonical_anchor(tokens: List[str]) -> str:
    phrase = _phrase_from_tokens(tokens)
    for core in sorted(CANONICAL_ANCHOR_PHRASES, key=lambda x: len(x.split()), reverse=True):
        if core in phrase:
            return core
    return ""


def _is_exact_canonical_anchor(tokens: List[str]) -> bool:
    return _phrase_from_tokens(tokens) in CANONICAL_ANCHOR_PHRASES


def _is_action_phrase(tokens: List[str]) -> bool:
    return bool(tokens and tokens[0] in ACTION_STARTS)


def _is_query_style_long_anchor(tokens: List[str]) -> bool:
    if len(tokens) < 5:
        return False
    if tokens[0] not in QUERY_STYLE_STARTS:
        return False
    middle = tokens[1:-1]
    return any(t in INTENT_CONNECTORS for t in middle) and len(_content_tokens(tokens)) >= 3


def _is_natural_compound_phrase(tokens: List[str]) -> bool:
    if len(tokens) not in {2, 3, 4}:
        return False

    phrase = _phrase_from_tokens(tokens)

    if phrase in CANONICAL_ANCHOR_PHRASES:
        return True

    if _has_valid_ordered_pair(tokens):
        return True

    if tokens[-1] in GENERIC_BUT_ALLOWED_HEADS:
        meaningful_mods = [
            t for t in tokens[:-1]
            if t not in STOPWORDS
            and t not in UNIVERSAL_WEAK_PREFIXES
            and t not in WEAK_ADJECTIVE_STARTS
        ]
        if meaningful_mods:
            return True

    return False


def _is_universal_weak_semantic_phrase(tokens: List[str]) -> bool:
    if len(tokens) < 2:
        return False

    if _is_natural_compound_phrase(tokens):
        return False

    first = tokens[0]
    last = tokens[-1]

    if first in UNIVERSAL_WEAK_PREFIXES:
        return True

    if last in UNIVERSAL_WEAK_HEADS and first in WEAK_ADJECTIVE_STARTS:
        return True

    if last in UNIVERSAL_WEAK_HEADS and len(tokens) <= 3:
        non_generic = [
            t for t in tokens
            if t not in UNIVERSAL_WEAK_PREFIXES
            and t not in UNIVERSAL_WEAK_HEADS
            and t not in WEAK_ADJECTIVE_STARTS
            and t not in STOPWORDS
        ]
        return len(non_generic) < 2

    return False


def _is_sentence_fragment_phrase(tokens: List[str]) -> bool:
    if len(tokens) < 2:
        return False

    if _is_natural_compound_phrase(tokens):
        return False

    if tokens[0] in ADVERB_FRAGMENT_STARTS:
        return True

    if tokens[-1] in SENTENCE_FRAGMENT_ENDS:
        return True

    if any(t in CLAUSE_VERBS for t in tokens):
        if not _is_action_phrase(tokens):
            return True

    if len(tokens) == 2:
        a, b = tokens
        if a.endswith("ly") or b.endswith("ly"):
            return True
        if b in {"ahead", "faster", "slower", "well"}:
            return True

    return False


def _vertical_keyword_hits(tokens: List[str]) -> int:
    token_set = set(tokens)
    hits = 0
    for terms in (
        {"cash", "flow", "revenue", "invoice", "tax", "loan", "credit"},
        {"blood", "pressure", "symptoms", "treatment", "medication"},
        {"course", "exam", "lesson", "study", "learning", "student"},
        {"software", "platform", "dashboard", "workflow", "automation"},
        {"seo", "content", "keyword", "traffic", "search"},
        {"property", "mortgage", "lease", "rent"},
        {"cycle", "phase", "period", "window", "fertile", "fertility",
         "ovulation", "cervical", "mucus", "menstrual", "basal",
         "temperature", "opk", "tracking", "predictor", "kits"},
    ):
        if token_set & terms:
            hits += 1
    return hits


def _vertical_term_total_hits(tokens: List[str]) -> int:
    token_set = set(tokens)
    terms = {
        "cash", "flow", "revenue", "invoice", "tax", "loan", "credit",
        "blood", "pressure", "symptoms", "treatment", "medication",
        "course", "exam", "lesson", "study", "learning", "student",
        "software", "platform", "dashboard", "workflow", "automation",
        "seo", "content", "keyword", "traffic", "search",
        "property", "mortgage", "lease", "rent",
        "cycle", "phase", "period", "window", "fertile", "fertility",
        "ovulation", "cervical", "mucus", "menstrual", "basal",
        "temperature", "opk", "tracking", "predictor", "kits",
    }
    return len(token_set & terms)


def _is_cross_niche_stitched_stack(tokens: List[str]) -> bool:
    if len(tokens) < 4:
        return False
    if _is_natural_compound_phrase(tokens):
        return False
    if _is_query_style_long_anchor(tokens):
        return False
    if _contains_canonical_anchor(tokens):
        return False
    if any(t in INTENT_CONNECTORS or t in SAFE_LONG_CONNECTORS for t in tokens):
        return False
    return _vertical_keyword_hits(tokens) >= 3 and _vertical_term_total_hits(tokens) >= 4


def _has_mid_stopword(tokens: List[str]) -> bool:
    if len(tokens) < 3:
        return False
    if _is_natural_compound_phrase(tokens):
        return False
    middle = tokens[1:-1]
    if len(tokens) >= 5:
        return any(t in STOPWORDS and t not in INTENT_CONNECTORS for t in middle)
    return any(t in STOPWORDS for t in middle)


def _has_clause_verb_leakage(tokens: List[str]) -> bool:
    if not tokens:
        return True
    if _is_natural_compound_phrase(tokens):
        return False
    if _is_action_phrase(tokens):
        return any(t in CLAUSE_VERBS for t in tokens[1:])
    return any(t in CLAUSE_VERBS for t in tokens)


def _has_boundary_spillover(tokens: List[str]) -> bool:
    if len(tokens) < 4:
        return False
    if _is_natural_compound_phrase(tokens):
        return False
    if _contains_canonical_anchor(tokens) and len(tokens) <= 5:
        return False
    return tokens[0] in {
        "previous", "next", "some", "many", "good", "better", "strongest",
        "minor", "major", "important", "clear", "quickly", "face",
        "facing", "thing", "things", "various", "different",
    }


def _has_long_clause_leakage(tokens: List[str]) -> bool:
    if len(tokens) < 5:
        return False
    if _is_query_style_long_anchor(tokens):
        return False
    if _contains_canonical_anchor(tokens) and len(tokens) <= 5:
        return False
    return any(t in CLAUSE_VERBS for t in tokens)


def _is_long_list_chain(tokens: List[str]) -> bool:
    if len(tokens) < 5:
        return False
    if _contains_canonical_anchor(tokens):
        return False
    chain_hits = sum(1 for t in tokens if t in LIST_CHAIN_WORDS)
    connector_hits = sum(1 for t in tokens if t in SAFE_LONG_CONNECTORS)
    return chain_hits >= 4 and connector_hits == 0


def _is_multi_cluster_phrase(tokens: List[str]) -> bool:
    if len(tokens) < 4:
        return False
    if _is_natural_compound_phrase(tokens):
        return False
    if _is_query_style_long_anchor(tokens) or _contains_canonical_anchor(tokens):
        return False

    connector_count = sum(1 for t in tokens if t in SAFE_LONG_CONNECTORS or t in INTENT_CONNECTORS)
    pair_hits = 0
    total_pairs = max(1, len(tokens) - 1)

    for i in range(len(tokens) - 1):
        a, b = tokens[i], tokens[i + 1]
        if a in STOPWORDS or b in STOPWORDS:
            continue

        noun_like_a = (
            a in STRONG_MODIFIER_WORDS
            or a in STRONG_CONCEPT_HEADS
            or a in NEUTRAL_NOUN_LIKE_HEADS
            or a in GENERIC_BUT_ALLOWED_HEADS
            or a in LIST_CHAIN_WORDS
        )
        noun_like_b = (
            b in STRONG_CONCEPT_HEADS
            or b in NEUTRAL_NOUN_LIKE_HEADS
            or b in GENERIC_BUT_ALLOWED_HEADS
            or b in LIST_CHAIN_WORDS
        )

        if noun_like_a and noun_like_b:
            pair_hits += 1

    ratio = pair_hits / total_pairs
    return len(tokens) >= 4 and ratio >= 0.85 and connector_count == 0


def _has_orphan_tail_start(tokens: List[str]) -> bool:
    return len(tokens) >= 3 and tokens[0] in {
        "agreements", "payments", "costs", "responsibilities", "terms",
        "rules", "expenses", "taxes", "invoices", "fees", "services",
        "products", "landlords",
    }


def _is_short_orphan_collision(tokens: List[str]) -> bool:
    if len(tokens) not in {2, 3}:
        return False
    if _is_natural_compound_phrase(tokens):
        return False
    if _is_query_style_long_anchor(tokens) or tuple(tokens) in VALID_ORDERED_PAIRS or _is_exact_canonical_anchor(tokens):
        return False

    noun_like_count = sum(
        1 for t in tokens
        if t in STRONG_CONCEPT_HEADS
        or t in NEUTRAL_NOUN_LIKE_HEADS
        or t in GENERIC_BUT_ALLOWED_HEADS
        or t in LIST_CHAIN_WORDS
    )

    if noun_like_count == len(tokens):
        has_strong_modifier = any(t in STRONG_MODIFIER_WORDS for t in tokens[:-1])
        has_natural_head = (
            tokens[-1] in STRONG_CONCEPT_HEADS
            or tokens[-1] in NEUTRAL_NOUN_LIKE_HEADS
            or tokens[-1] in GENERIC_BUT_ALLOWED_HEADS
        )
        return not has_strong_modifier and has_natural_head

    return False


def _is_prefix_suffix_spillover(tokens: List[str]) -> bool:
    if len(tokens) < 2:
        return False
    if _is_natural_compound_phrase(tokens):
        return False
    if _is_exact_canonical_anchor(tokens):
        return False
    if tokens[0] in STOPWORDS:
        return True
    if len(tokens) >= 3 and tokens[1] in WEAK_ADJECTIVE_STARTS:
        return True
    if len(tokens) == 3:
        return tuple(tokens[:2]) in VALID_ORDERED_PAIRS and tuple(tokens[1:]) not in VALID_ORDERED_PAIRS
    return False


def _has_vague_action_modifier(tokens: List[str]) -> bool:
    return len(tokens) >= 3 and _is_action_phrase(tokens) and any(t in VAGUE_ACTION_MODIFIERS for t in tokens[1:-1])


def _is_list_pair_fragment(tokens: List[str]) -> bool:
    if len(tokens) != 2:
        return False
    if _is_natural_compound_phrase(tokens):
        return False
    if tuple(tokens) in VALID_ORDERED_PAIRS:
        return False
    left, right = tokens
    if left in LIST_CONTEXT_WORDS and right in LIST_CONTEXT_WORDS:
        return not (left in STRONG_MODIFIER_WORDS and right in STRONG_CONCEPT_HEADS)
    return right in {"software", "insurance", "mortgage", "investment", "taxes"} and left not in STRONG_MODIFIER_WORDS


def _is_list_style_stack(tokens: List[str]) -> bool:
    if len(tokens) < 3:
        return False
    if _is_natural_compound_phrase(tokens):
        return False
    if _contains_canonical_anchor(tokens):
        return False
    if _is_action_phrase(tokens) and tokens[-1] in STRONG_ACTION_OBJECT_HEADS:
        return False

    list_count = sum(1 for t in tokens if t in LIST_CONTEXT_WORDS)
    if list_count >= 3:
        return True

    if len(tokens) >= 3 and tokens[-1] not in STRONG_CONCEPT_HEADS:
        strong_mods = sum(1 for t in tokens[:-1] if t in STRONG_MODIFIER_WORDS)
        return strong_mods == 0

    return False


def _has_action_chain_tail(tokens: List[str]) -> bool:
    if len(tokens) < 5:
        return False
    if tokens[0] in ACTION_STARTS:
        return True
    action_hits = sum(1 for t in tokens if t in ACTION_STARTS)
    return action_hits >= 2


def _should_trim_bad_long_phrase(tokens: List[str]) -> bool:
    if len(tokens) < 4:
        return False
    if _is_natural_compound_phrase(tokens):
        return False
    if _is_query_style_long_anchor(tokens):
        return False
    if sum(1 for t in tokens if t in INTENT_CONNECTORS or t in SAFE_LONG_CONNECTORS) >= 2:
        return False
    return (
        (_contains_canonical_anchor(tokens) and len(tokens) >= 5)
        or (_is_action_phrase(tokens) and len(tokens) >= 4)
        or _has_action_chain_tail(tokens)
        or _is_long_list_chain(tokens)
        or _is_multi_cluster_phrase(tokens)
        or _is_cross_niche_stitched_stack(tokens)
    )


def _cut_semantic_tail(tokens: List[str]) -> List[str]:
    if len(tokens) < 4:
        return tokens
    core = _contains_canonical_anchor(tokens)
    if core:
        return core.split()

    for span in (tokens[:3], tokens[:2]):
        result = score_phrase_strength(" ".join(span), allow_trim=False)
        if result.get("keep"):
            return span

    return tokens


def trim_bad_long_phrase(tokens: List[str]) -> List[str]:
    if len(tokens) < 4:
        return tokens

    tail_cut = _cut_semantic_tail(tokens)
    if tail_cut != tokens:
        return tail_cut

    best_span = tokens
    best_rank = -1.0

    for size in range(2, min(5, len(tokens)) + 1):
        for i in range(0, len(tokens) - size + 1):
            span = tokens[i:i + size]
            result = score_phrase_strength(" ".join(span), allow_trim=False)
            if not result.get("keep"):
                continue

            rank = float(result.get("score") or 0.0)
            rank += 0.04 * sum(1 for t in span if t in STRONG_MODIFIER_WORDS)
            rank += 0.03 * sum(1 for t in span if t in STRONG_CONCEPT_HEADS)
            rank += 0.02 * len(span)

            if _is_exact_canonical_anchor(span):
                rank += 0.30
            elif _has_valid_ordered_pair(span):
                rank += 0.18

            if rank > best_rank:
                best_rank = rank
                best_span = span

    return best_span

def _has_structural_signal(tokens: List[str], source_type: str) -> tuple[bool, List[str]]:
    signals: List[str] = []

    if not tokens:
        return False, signals

    head = tokens[-1]
    modifiers = tokens[:-1]

    if _is_exact_canonical_anchor(tokens):
        signals.append("structural_canonical_anchor")

    if _has_valid_ordered_pair(tokens):
        signals.append("structural_valid_ordered_pair")

    if _is_natural_compound_phrase(tokens):
        signals.append("structural_natural_compound")

    if head in STRONG_CONCEPT_HEADS:
        signals.append("structural_strong_head")

    if head in GENERIC_BUT_ALLOWED_HEADS and any(
        t in STRONG_MODIFIER_WORDS or t in STRONG_CONCEPT_HEADS
        for t in modifiers
    ):
        signals.append("structural_generic_allowed_compound")

    if any(t in STRONG_MODIFIER_WORDS for t in modifiers) and (
        head in STRONG_CONCEPT_HEADS
        or head in NEUTRAL_NOUN_LIKE_HEADS
        or head in STRONG_ACTION_OBJECT_HEADS
        or head in GENERIC_BUT_ALLOWED_HEADS
    ):
        signals.append("structural_modifier_head")

    if source_type in {"title", "heading_h1", "heading_h2", "heading_h3", "intent"}:
        signals.append("structural_trusted_source")

    cohesion = phrase_domain_cohesion(set(tokens))
    if bool(cohesion.get("is_cohesive")):
        signals.append("structural_domain_cohesion")

    if _is_action_phrase(tokens) and head in STRONG_ACTION_OBJECT_HEADS:
        signals.append("structural_action_object")

    return bool(signals), signals


def _short_window_structure_penalty(tokens: List[str], source_type: str) -> tuple[float, List[str]]:
    if len(tokens) not in {2, 3, 4}:
        return 0.0, []

    if _is_natural_compound_phrase(tokens):
        return 0.18, ["short_window_natural_compound"]

    has_signal, reasons = _has_structural_signal(tokens, source_type)

    if not has_signal:
        return -0.45, reasons + ["short_window_missing_structure"]

    if _is_list_style_stack(tokens):
        return -0.30, reasons + ["short_window_stitched_sequence"]

    return 0.0, reasons


def _long_phrase_naturalness_score(tokens: List[str], source_type: str) -> tuple[float, List[str]]:
    if len(tokens) < 5:
        return 0.0, []

    score = 0.0
    reasons: List[str] = []

    if _is_long_list_chain(tokens):
        score -= 0.95
        reasons.append("long_list_chain")

    if _is_cross_niche_stitched_stack(tokens):
        score -= 0.75
        reasons.append("long_cross_niche_stitch")

    if len(_content_tokens(tokens)) >= 4:
        score += 0.12
        reasons.append("long_contentful_phrase")

    if tokens[-1] in STRONG_CONCEPT_HEADS or tokens[-1] in STRONG_ACTION_OBJECT_HEADS:
        score += 0.12
        reasons.append("long_clear_head")

    if source_type in {"title", "heading_h1", "heading_h2", "heading_h3", "intent"}:
        score += 0.10
        reasons.append("long_trusted_source")

    if _has_mid_stopword(tokens):
        score -= 0.18
        reasons.append("long_mid_stopword_risk")

    if len(tokens) >= 9:
        score -= 0.35
        reasons.append("overlong_anchor")

    return score, reasons


def _modifier_quality_score(tokens: List[str]) -> tuple[float, List[str]]:
    if len(tokens) < 2:
        return -0.50, ["missing_modifier"]

    score = 0.0
    reasons: List[str] = []
    modifiers = tokens[:-1]

    strong_mod_count = sum(1 for t in modifiers if t in STRONG_MODIFIER_WORDS)
    weak_adj_count = sum(1 for t in modifiers if t in WEAK_ADJECTIVE_STARTS)
    stopword_count = sum(1 for t in modifiers if t in STOPWORDS)

    if _is_natural_compound_phrase(tokens):
        score += 0.20
        reasons.append("natural_compound_modifier")

    if strong_mod_count >= 1:
        score += 0.18
        reasons.append("specific_modifier")

    if strong_mod_count >= 2:
        score += 0.10
        reasons.append("multi_specific_modifier")

    if weak_adj_count >= 1 and not _has_valid_ordered_pair(tokens):
        score -= 0.20
        reasons.append("weak_modifier")

    if stopword_count and not _is_natural_compound_phrase(tokens):
        score -= 0.25
        reasons.append("stopword_modifier")

    if len(modifiers) == 1 and modifiers[0] in WEAK_ADJECTIVE_STARTS:
        score -= 0.25
        reasons.append("thin_modifier")

    return score, reasons


def _head_quality_score(tokens: List[str]) -> tuple[float, List[str]]:
    if not tokens:
        return -1.0, ["missing_head"]

    score = 0.0
    reasons: List[str] = []
    head = tokens[-1]

    if _is_exact_canonical_anchor(tokens):
        score += 0.25
        reasons.append("canonical_head_phrase")

    if _is_natural_compound_phrase(tokens):
        score += 0.25
        reasons.append("natural_compound_head")

    if head in STRONG_CONCEPT_HEADS:
        score += 0.35
        reasons.append("strong_head")
    elif head in GENERIC_BUT_ALLOWED_HEADS:
        score += 0.08
        reasons.append("generic_allowed_head")
    elif head in WEAK_HEADS:
        score -= 0.45
        reasons.append("weak_head")
    elif head in NEUTRAL_NOUN_LIKE_HEADS:
        score += 0.05
        reasons.append("neutral_noun_head")
    else:
        score -= 0.10
        reasons.append("unknown_head")

    return score, reasons


def _standalone_score(tokens: List[str], source_type: str) -> tuple[float, List[str]]:
    score = 0.0
    reasons: List[str] = []

    if len(tokens) in {2, 3, 4}:
        score += 0.08
        reasons.append("clean_short_length")
    elif 5 <= len(tokens) <= 8:
        score += 0.02
        reasons.append("allowed_long_anchor")
    elif len(tokens) >= 9:
        score -= 0.20
        reasons.append("too_long_for_anchor")

    if source_type in {"title", "heading_h1", "heading_h2", "heading_h3", "intent"}:
        score += 0.10
        reasons.append("trusted_source")

    if len(_content_tokens(tokens)) >= 2:
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
    if not _is_action_phrase(tokens):
        return 0.0, []

    if len(tokens) < 2:
        return -0.60, ["missing_action_object"]

    score = 0.0
    reasons: List[str] = []
    obj = tokens[-1]

    if len(tokens) > 6:
        score -= 0.20
        reasons.append("overextended_action")

    if obj in WEAK_ACTION_OBJECT_HEADS or obj in WEAK_HEADS:
        score -= 0.45
        reasons.append("weak_action_object")
    elif obj in STRONG_ACTION_OBJECT_HEADS or obj in STRONG_CONCEPT_HEADS or obj in GENERIC_BUT_ALLOWED_HEADS:
        score += 0.35
        reasons.append("clear_action_object")
    elif obj in NEUTRAL_NOUN_LIKE_HEADS:
        score += 0.08
        reasons.append("neutral_action_object")
    else:
        score -= 0.10
        reasons.append("unclear_action_object")

    if _has_vague_action_modifier(tokens):
        score -= 0.45
        reasons.append("vague_action_modifier")

    return score, reasons


def _cohesion_penalty(tokens: List[str]) -> tuple[float, List[str]]:
    phrase_tuple = tuple(tokens)

    natural_patterns = tuple(VALID_ORDERED_PAIRS) + (
        ("late", "fee", "policy"),
        ("contract", "risk", "management"),
        ("budget", "review"),
        ("pricing", "strategy"),
        ("product", "pricing"),
        ("internal", "linking", "strategy"),
        ("content", "optimization", "strategy"),
        ("fertile", "window"),
        ("cycle", "length"),
        ("follicular", "phase"),
        ("luteal", "phase"),
        ("cervical", "mucus", "patterns"),
        ("ovulation", "predictor", "kits"),
        ("last", "menstrual", "period"),
        ("typical", "cycle", "length"),
        ("shortest", "and", "longest", "cycle"),
        ("expected", "ovulation"),
        ("basal", "body", "temperature"),
        ("strong", "positive", "opk"),
    )

    if phrase_tuple in natural_patterns:
        return 0.20, ["natural_phrase_pattern"]

    return 0.0, []


def _domain_cohesion_score(tokens: List[str]) -> tuple[float, List[str]]:
    if len(tokens) < 2:
        return 0.0, []

    if _is_natural_compound_phrase(tokens):
        return 0.12, ["natural_compound_cohesion"]

    info = phrase_domain_cohesion(set(tokens))
    if bool(info.get("is_cohesive")):
        return 0.18, ["domain_cohesive"]

    if len(tokens) >= 3 and int(info.get("best_hit_count") or 0) <= 1:
        return -0.20, ["low_domain_cohesion"]

    return 0.0, []


def _fragment_penalty(tokens: List[str], p: str) -> tuple[float, List[str]]:
    score = 0.0
    reasons: List[str] = []

    if _is_natural_compound_phrase(tokens):
        return 0.0, ["natural_compound_fragment_safe"]

    if _has_bad_fragment_pattern(p):
        score -= 0.60
        reasons.append("bad_fragment_pattern")

    if _has_mid_stopword(tokens):
        score -= 0.45
        reasons.append("mid_stopword_fragment")

    if _has_clause_verb_leakage(tokens):
        if not (_contains_canonical_anchor(tokens) and len(tokens) <= 5):
            score -= 0.55
            reasons.append("clause_verb_leakage")

    if _is_list_pair_fragment(tokens):
        score -= 0.50
        reasons.append("list_pair_fragment")

    if _is_list_style_stack(tokens):
        has_signal, _ = _has_structural_signal(tokens, "")
        if not has_signal:
            score -= 0.50
            reasons.append("list_style_stack")

    return score, reasons


def _universal_precision_score(tokens: List[str]) -> tuple[float, List[str]]:
    score = 0.0
    reasons: List[str] = []

    if _has_reversed_ordered_pair(tokens):
        score -= 0.80
        reasons.append("reversed_ordered_pair")

    if _has_valid_ordered_pair(tokens):
        score += 0.18
        reasons.append("valid_ordered_pair")

    if _is_natural_compound_phrase(tokens):
        score += 0.20
        reasons.append("natural_compound_precision")

    if _is_exact_canonical_anchor(tokens):
        score += 0.25
        reasons.append("canonical_anchor_exact")
    elif _contains_canonical_anchor(tokens):
        score += 0.08
        reasons.append("canonical_anchor_contained")
        if len(tokens) >= 5:
            score -= 0.22
            reasons.append("wrapper_inflation_risk")

    if _is_cross_niche_stitched_stack(tokens):
        score -= 0.75
        reasons.append("cross_niche_stitched_stack")

    if _is_universal_weak_semantic_phrase(tokens):
        score -= 0.55
        reasons.append("universal_weak_semantic_phrase")

    vertical_hits = _vertical_keyword_hits(tokens)
    if vertical_hits == 1 and len(tokens) in {2, 3, 4}:
        score += 0.06
        reasons.append("single_vertical_signal")
    elif vertical_hits >= 2 and len(tokens) in {2, 3, 4}:
        score += 0.10
        reasons.append("multi_vertical_signal")
    elif vertical_hits >= 3 and len(tokens) >= 5:
        score -= 0.12
        reasons.append("vertical_overstack_risk")

    return score, reasons


def score_phrase_strength(
    phrase: str,
    *,
    source_type: str = "",
    allow_trim: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:
    p = canonical_phrase(phrase)
    tokens = tokenize(p)

    if not p or len(tokens) < 2:
        return {"keep": False, "score": 0.0, "phrase": p, "reason": "too_short"}

    if len(tokens) > 10:
        return {"keep": False, "score": 0.0, "phrase": p, "reason": "too_long"}

    if _is_universal_weak_semantic_phrase(tokens):
        return {"keep": False, "score": 0.0, "phrase": p, "reason": "universal_weak_semantic_phrase"}

    if _is_sentence_fragment_phrase(tokens):
        return {"keep": False, "score": 0.0, "phrase": p, "reason": "sentence_fragment_phrase"}

    if _has_reversed_ordered_pair(tokens):
        return {"keep": False, "score": 0.0, "phrase": p, "reason": "reversed_ordered_pair"}

    if allow_trim and _should_trim_bad_long_phrase(tokens):
        trimmed = trim_bad_long_phrase(tokens)
        if trimmed != tokens:
            p = " ".join(trimmed)
            tokens = trimmed

    hard_rejects = [
        (_is_cross_niche_stitched_stack(tokens), "cross_niche_stitched_stack"),
        (_is_long_list_chain(tokens), "long_list_chain"),
        (_is_multi_cluster_phrase(tokens), "multi_cluster_phrase"),
        (_is_short_orphan_collision(tokens), "short_orphan_collision"),
        (_is_prefix_suffix_spillover(tokens), "prefix_suffix_spillover"),
        (_has_orphan_tail_start(tokens), "orphan_tail_start"),
        (_has_boundary_spillover(tokens), "boundary_spillover"),
        (_has_long_clause_leakage(tokens), "long_clause_leakage"),
    ]

    for bad, reason in hard_rejects:
        if bad:
            return {"keep": False, "score": 0.0, "phrase": p, "reason": reason}

    if tokens[0] in WEAK_STARTS and not _is_exact_canonical_anchor(tokens) and not _is_natural_compound_phrase(tokens):
        return {"keep": False, "score": 0.10, "phrase": p, "reason": "weak_start"}

    if tokens[-1] in WEAK_ENDINGS and not _is_exact_canonical_anchor(tokens) and not _is_natural_compound_phrase(tokens):
        return {"keep": False, "score": 0.10, "phrase": p, "reason": "weak_ending"}

    score = 0.40
    reasons: List[str] = []

    scoring_layers = [
        _head_quality_score(tokens),
        _modifier_quality_score(tokens),
        _standalone_score(tokens, source_type),
        _fragment_penalty(tokens, p),
        _cohesion_penalty(tokens),
        _domain_cohesion_score(tokens),
        _action_object_score(tokens),
        _short_window_structure_penalty(tokens, source_type),
        _long_phrase_naturalness_score(tokens, source_type),
        _universal_precision_score(tokens),
    ]

    for layer_score, layer_reasons in scoring_layers:
        score += layer_score
        reasons.extend(layer_reasons)

    score = max(0.0, min(1.0, round(score, 3)))

    if _is_query_style_long_anchor(tokens) and len(_content_tokens(tokens)) >= 4:
        score = max(score, 0.78)
        reasons.append("query_style_score_floor")

    if _is_exact_canonical_anchor(tokens):
        score = max(score, 0.84)
        reasons.append("canonical_score_floor")
    elif _is_natural_compound_phrase(tokens):
        score = max(score, 0.76)
        reasons.append("natural_compound_score_floor")
    elif _has_valid_ordered_pair(tokens) and len(tokens) in {2, 3, 4}:
        score = max(score, 0.80)
        reasons.append("ordered_pair_score_floor")

    threshold = 0.66
    token_len = len(tokens)

    has_canonical_anchor = _is_exact_canonical_anchor(tokens)
    has_valid_pair = _has_valid_ordered_pair(tokens)
    has_natural_compound = _is_natural_compound_phrase(tokens)
    query_style = _is_query_style_long_anchor(tokens)

    structural_signal, structural_reasons = _has_structural_signal(tokens, source_type)
    vertical_hits = _vertical_keyword_hits(tokens)

    if has_canonical_anchor:
        threshold = 0.52
    elif has_valid_pair:
        threshold = 0.58
    elif has_natural_compound:
        threshold = 0.58

    if query_style:
        threshold = min(threshold, 0.60)

    if structural_signal:
        threshold -= 0.05
        reasons.extend(structural_reasons)

    cohesion = phrase_domain_cohesion(set(tokens))
    if bool(cohesion.get("is_cohesive")):
        threshold -= 0.04

    if vertical_hits >= 2 and token_len <= 5:
        threshold -= 0.04

    if _is_action_phrase(tokens):
        head = tokens[-1]
        if (
            head not in STRONG_ACTION_OBJECT_HEADS
            and head not in STRONG_CONCEPT_HEADS
            and head not in GENERIC_BUT_ALLOWED_HEADS
        ):
            threshold += 0.08

    if token_len >= 7:
        threshold += 0.06
    elif token_len >= 5:
        threshold += 0.02

    if not structural_signal and token_len in {2, 3, 4} and not has_valid_pair and not has_natural_compound:
        threshold += 0.10

    if (
        source_type == "noun_phrase"
        and not structural_signal
        and not has_valid_pair
        and not has_canonical_anchor
        and not has_natural_compound
    ):
        threshold += 0.08

    threshold = max(0.50, min(0.86, threshold))
    keep = score >= threshold

    return {
        "keep": keep,
        "score": score,
        "phrase": p,
        "reason": "+".join(reasons) if reasons else "neutral",
    }