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

VERTICAL_KEYWORD_MAP: Dict[str, Set[str]] = {
    "finance": {"cash", "flow", "revenue", "profit", "invoice", "invoices", "payroll", "tax", "taxes", "loan", "loans", "credit", "banking", "investment", "insurance", "accounting"},
    "real_estate": {"property", "mortgage", "lease", "rent", "tenant", "landlord", "listing", "home", "buyer", "seller", "appraisal", "closing"},
    "legal": {"law", "legal", "contract", "compliance", "court", "attorney", "lawyer", "claim", "liability", "agreement", "clause"},
    "ecommerce": {"product", "products", "cart", "checkout", "shopify", "woocommerce", "marketplace", "category", "pages", "inventory", "orders"},
    "saas": {"software", "subscription", "platform", "dashboard", "workflow", "crm", "analytics", "integration", "automation", "users"},
    "marketing": {"seo", "content", "campaign", "conversion", "keyword", "keywords", "brand", "email", "traffic", "search", "intent"},
    "small_business": {"business", "cash", "flow", "payroll", "operations", "customers", "suppliers", "expenses", "forecast", "invoicing"},
    "hr_recruiting": {"hiring", "recruiting", "onboarding", "payroll", "benefits", "employee", "employees", "performance", "staffing"},
    "medical_healthcare": {"health", "blood", "pressure", "diagnosis", "treatment", "symptoms", "clinic", "patient", "screening", "condition"},
    "pharmacy": {"medication", "medicine", "dose", "dosing", "side", "effects", "prescription", "otc", "adherence", "pharmacist"},
    "mental_health": {"anxiety", "therapy", "counseling", "stress", "depression", "mental", "health", "wellbeing", "support"},
    "fitness": {"exercise", "training", "strength", "mobility", "workout", "endurance", "muscle", "recovery", "fitness"},
    "nutrition": {"diet", "nutrition", "meal", "meals", "protein", "calories", "supplements", "weight", "healthy", "eating"},
    "beauty_skincare": {"skin", "skincare", "hair", "cosmetics", "dermatology", "grooming", "acne", "moisturizer"},
    "home_improvement": {"plumbing", "roofing", "hvac", "painting", "remodeling", "repair", "tools", "contractor"},
    "interior_design": {"furniture", "decor", "layout", "renovation", "lighting", "style", "room", "design"},
    "gardening": {"plants", "garden", "landscaping", "lawn", "soil", "irrigation", "pest", "compost"},
    "parenting_family": {"pregnancy", "baby", "child", "children", "parenting", "family", "development", "school"},
    "pets": {"dog", "dogs", "cat", "cats", "pet", "pets", "training", "grooming", "veterinary", "food"},
    "food_recipes": {"recipe", "recipes", "cooking", "baking", "kitchen", "meal", "restaurant", "ingredients"},
    "travel": {"flight", "hotel", "visa", "itinerary", "tourism", "destination", "travel", "guide", "booking"},
    "automotive": {"car", "cars", "auto", "repair", "vehicle", "ev", "insurance", "detailing", "maintenance"},
    "education": {"school", "student", "students", "course", "exam", "tutoring", "lesson", "study", "learning"},
    "careers": {"resume", "interview", "salary", "career", "freelancing", "job", "promotion", "skills"},
    "professional_training": {"certification", "license", "training", "continuing", "education", "professional", "exam"},
    "consumer_tech": {"phone", "laptop", "gadget", "wearable", "accessory", "device", "tablet", "smartphone"},
    "it_cybersecurity": {"network", "cloud", "security", "cybersecurity", "infrastructure", "compliance", "server", "endpoint"},
    "programming_development": {"code", "coding", "api", "database", "framework", "devops", "frontend", "backend", "deployment"},
    "ai_machine_learning": {"ai", "machine", "learning", "model", "models", "prompt", "automation", "dataset", "training"},
    "gaming": {"game", "gaming", "console", "pc", "mobile", "esports", "guide", "level", "players"},
    "sports": {"sports", "team", "teams", "player", "players", "training", "match", "league", "equipment"},
    "entertainment": {"movie", "movies", "tv", "celebrity", "streaming", "series", "show", "culture"},
    "music": {"music", "artist", "artists", "instrument", "production", "lesson", "gear", "song"},
    "manufacturing": {"manufacturing", "production", "machinery", "quality", "supply", "chain", "factory", "materials"},
    "construction": {"construction", "contractor", "materials", "bidding", "project", "site", "building"},
    "logistics": {"shipping", "freight", "warehouse", "warehousing", "fleet", "delivery", "logistics", "carrier"},
    "agriculture": {"farming", "livestock", "crops", "irrigation", "soil", "agritech", "harvest", "farm"},
    "energy": {"solar", "energy", "utilities", "sustainability", "oil", "gas", "renewable", "grid"},
    "telecom": {"internet", "mobile", "network", "telecom", "broadband", "provider", "device", "signal"},
    "government": {"permit", "policy", "public", "service", "services", "program", "government", "license"},
    "nonprofit": {"donation", "fundraising", "volunteer", "outreach", "nonprofit", "charity", "community"},
    "religion_faith": {"faith", "ministry", "church", "teaching", "religion", "community", "worship"},
    "local_services": {"dentist", "plumber", "cleaner", "lawyer", "contractor", "local", "service", "nearby"},
    "blogging": {"blog", "blogging", "affiliate", "content", "authority", "niche", "publisher", "posts"},
    "youtube_video_creators": {"youtube", "video", "thumbnail", "script", "monetization", "creator", "channel"},
    "influencers_personal_brands": {"influencer", "brand", "audience", "sponsorship", "community", "followers"},
    "courses_info_products": {"course", "courses", "membership", "coaching", "digital", "product", "products", "lesson"},
    "web3_crypto": {"crypto", "blockchain", "wallet", "token", "tokens", "defi", "nft", "web3"},
    "sustainability": {"green", "carbon", "eco", "sustainable", "sustainability", "climate", "recycling"},
    "remote_work": {"remote", "work", "distributed", "team", "teams", "home", "digital", "nomad"},
    "multi_niche_publishers": {"publisher", "publishers", "content", "network", "topics", "authority", "articles"},
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
    ("risk", "management"),
    ("customer", "service"),
    ("data", "security"),
    ("keyword", "research"),
    ("content", "optimization"),
    ("conversion", "rate"),
    ("payment", "schedule"),
    ("late", "payment"),
    ("late", "fee"),
}

REVERSED_ORDERED_PAIRS: Set[Tuple[str, str]] = {
    (b, a) for a, b in VALID_ORDERED_PAIRS
}

CANONICAL_ANCHOR_PHRASES: Set[str] = {
    "cash flow",
    "cash flow management",
    "blood pressure",
    "blood pressure control",
    "internal linking",
    "internal linking strategy",
    "external linking",
    "search intent",
    "ecommerce category pages",
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
    "risk management",
    "customer service",
    "data security",
    "keyword research",
    "content optimization",
    "conversion rate",
    "payment schedule",
    "late payment",
    "late fee",
}

EDU_ACTION_FRAGMENT_STARTS: Set[str] = {
    "explaining",
    "teaching",
    "learning",
    "reviewing",
    "studying",
    "covering",
    "revising",
}

EDU_VALID_PATTERN_PHRASES: Set[str] = {
    # 1. Exam preparation
    "exam preparation",
    "exam format",
    "mock exams",
    "past questions",
    "practice questions",
    "timed practice",
    "revision schedule",
    "exam performance",

    # 2. Online learning
    "online course",
    "virtual classroom",
    "learning platform",
    "video lesson",
    "course module",
    "digital learning",

    # 3. Student productivity
    "study plan",
    "study schedule",
    "time blocking",
    "study environment",
    "progress tracking",
    "academic goals",

    # 4. Tutoring
    "tutoring session",
    "private tutor",
    "math tutor",
    "reading tutor",
    "student support",
    "learning gaps",

    # 5. Study skills
    "active learning methods",
    "spaced repetition",
    "retrieval practice",
    "summary notes",
    "flashcards",
    "memory recall",
    "learning strategy",
}

EDU_WEAK_PREFIXES: Set[str] = {
    "one", "same", "each", "another", "average", "light", "lighter",
    "extreme", "some", "many", "several", "different", "various",
    "general", "basic", "simple", "clear", "strong", "weak",
}

EDU_GENERIC_HEADS: Set[str] = {
    "topic", "topics", "subject", "subjects", "chapter", "chapters",
    "review", "reviews", "schedule", "system", "systems", "method",
    "methods", "performance", "skills", "tools", "material",
    "materials", "content", "lesson", "lessons",
}

EDU_ACTION_FRAGMENT_STARTS: Set[str] = {
    "explaining", "teaching", "learning", "reviewing", "studying",
    "covering", "revising", "reading", "writing", "practicing",
}

EDU_GENERIC_OBJECT_HEADS: Set[str] = {
    "topic",
    "topics",
    "subject",
    "subjects",
    "chapter",
    "chapters",
    "material",
    "materials",
    "content",
}

VALID_EDUCATION_PHRASES: Set[str] = {
    "effective study plan",
    "exam preparation",
    "study plan",
    "active learning methods",
    "spaced repetition",
    "past questions",
    "mock exams",
    "past questions and mock exams",
    "academic assessment",
    "exam format",
    "practice questions",
    "retrieval practice",
    "study environment",
    "timed practice",
}

BAD_EDUCATION_FRAGMENTS: Set[str] = {
    "students time motivation system",
    "study biology today",
    "preparation exam",
    "learning new material to revision",
    "students time",
    "motivation system",
    "subjects topic",
    "explaining topics",
    "influence learning performance",
    "study science",
}

WEAK_STARTS: Set[str] = {
    "because", "based", "with", "without", "before", "after", "during",
    "inside", "outside", "back", "such", "most", "many", "some", "few",
    "this", "that", "these", "those", "your", "people", "everyone",
    "someone", "anyone", "rather", "quickly", "slowly", "face", "facing",
    "thing", "things", "various", "different",
}

WEAK_ENDINGS: Set[str] = {
    "the", "a", "an", "of", "to", "for", "with", "without", "from", "into",
    "on", "at", "by", "because", "afterward", "afterwards", "later",
    "monthly", "financial", "unnecessary", "important", "clear", "short",
    "long", "near", "most", "thing", "things", "way", "ways", "area",
    "areas", "part", "parts",
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
    "quickly", "face", "facing", "thing", "things", "various", "different",
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
    "blood", "pressure", "remote", "machine", "learning", "supply",
    "chain", "ecommerce", "category",
}

WEAK_EDU_PREFIXES: Set[str] = {
    "one",
    "same",
    "each",
    "another",
    "average",
    "light",
    "lighter",
    "extreme",
    "some",
    "many",
}

GENERIC_EDU_HEADS: Set[str] = {
    "topic",
    "topics",
    "review",
    "reviews",
    "schedule",
    "system",
    "method",
    "methods",
    "performance",
    "skills",
    "tools",
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
    "landlord", "landlords", "lease", "leases", "loan", "loans",
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
    "requires", "require", "reveals", "reveal",
}

LIST_CONTEXT_WORDS: Set[str] = {
    "rent", "utilities", "groceries", "transport", "insurance",
    "subscriptions", "entertainment", "salary", "payments", "revenue",
    "investment", "returns", "income", "expenses", "stocks", "bonds",
    "funds", "cash", "reserves", "taxes", "software", "equipment",
    "payroll", "invoices", "suppliers", "customers", "marketing",
    "inventory", "products", "services", "fees", "renewal", "schedule",
    "payment", "data", "pricing", "plans", "loan", "loans", "rent",
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


def canonical_phrase(text: str) -> str:
    s = (text or "").strip().lower()
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"^\s*(?:\d+[\.\)]\s+|[•\-–]\s+)", "", s)
    s = re.sub(r"^[\"'“”‘’\(\[\{]+|[\"'“”‘’\)\]\}:;,\.\!\?]+$", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]


def phrase_key(phrase: str) -> str:
    return " ".join(tokenize(canonical_phrase(phrase)))


def _content_tokens(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in STOPWORDS]


def _has_bad_fragment_pattern(p: str) -> bool:
    return any(re.search(pat, p) for pat in BAD_FRAGMENT_PATTERNS)


def _phrase_from_tokens(tokens: List[str]) -> str:
    return " ".join(tokens)


def _vertical_keyword_hits(tokens: List[str]) -> int:
    token_set = set(tokens)
    hits = 0
    for terms in VERTICAL_KEYWORD_MAP.values():
        if token_set & terms:
            hits += 1
    return hits


def _vertical_term_total_hits(tokens: List[str]) -> int:
    token_set = set(tokens)
    total = 0
    for terms in VERTICAL_KEYWORD_MAP.values():
        total += len(token_set & terms)
    return total


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


def _is_cross_niche_stitched_stack(tokens: List[str]) -> bool:
    if len(tokens) < 4:
        return False

    if _is_query_style_long_anchor(tokens):
        return False

    if _contains_canonical_anchor(tokens):
        return False

    connector_count = sum(1 for t in tokens if t in INTENT_CONNECTORS or t in SAFE_LONG_CONNECTORS)
    if connector_count > 0:
        return False

    vertical_hits = _vertical_keyword_hits(tokens)
    total_term_hits = _vertical_term_total_hits(tokens)

    return vertical_hits >= 3 and total_term_hits >= 4

def _is_valid_education_pattern_phrase(tokens: List[str]) -> bool:
    return " ".join(tokens) in EDU_VALID_PATTERN_PHRASES


def _is_weak_education_pattern(tokens: List[str]) -> bool:
    if len(tokens) < 2:
        return False

    if _is_valid_education_pattern_phrase(tokens):
        return False

    first = tokens[0]
    last = tokens[-1]

    if first in EDU_WEAK_PREFIXES and last in EDU_GENERIC_HEADS:
        return True

    if first in EDU_ACTION_FRAGMENT_STARTS and last in EDU_GENERIC_HEADS:
        return True

    return False


def _universal_precision_score(tokens: List[str]) -> tuple[float, List[str]]:
    score = 0.0
    reasons: List[str] = []

    if _has_reversed_ordered_pair(tokens):
        score -= 0.80
        reasons.append("reversed_ordered_pair")

    if _has_valid_ordered_pair(tokens):
        score += 0.18
        reasons.append("valid_ordered_pair")

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

def _is_valid_education_phrase(tokens: List[str]) -> bool:
    return " ".join(tokens) in VALID_EDUCATION_PHRASES


def _is_bad_education_fragment(tokens: List[str]) -> bool:
    return " ".join(tokens) in BAD_EDUCATION_FRAGMENTS


def _has_boundary_spillover(tokens: List[str]) -> bool:
    if len(tokens) < 4:
        return False

    if _contains_canonical_anchor(tokens) and len(tokens) <= 5:
        return False

    if tokens[0] in BOUNDARY_SPILLOVER_STARTS:
        return True

    if tokens[0] in STOPWORDS:
        return True

    if len(tokens) >= 5 and tokens[1] in BOUNDARY_SPILLOVER_STARTS:
        return True

    return False

def _is_education_action_fragment(tokens: List[str]) -> bool:
    if len(tokens) < 2:
        return False

    if " ".join(tokens) in VALID_EDUCATION_PHRASES:
        return False

    return tokens[0] in EDU_ACTION_FRAGMENT_STARTS and tokens[-1] in EDU_GENERIC_OBJECT_HEADS


def _has_long_clause_leakage(tokens: List[str]) -> bool:
    if len(tokens) < 5:
        return False

    if _is_query_style_long_anchor(tokens):
        return False

    if _contains_canonical_anchor(tokens) and len(tokens) <= 5:
        return False

    return any(t in LONG_CLAUSE_LEAK_WORDS for t in tokens)


def _is_multi_cluster_phrase(tokens: List[str]) -> bool:
    if len(tokens) < 4:
        return False

    if _is_query_style_long_anchor(tokens):
        return False

    if _contains_canonical_anchor(tokens):
        return False

    connector_count = sum(1 for t in tokens if t in SAFE_LONG_CONNECTORS or t in INTENT_CONNECTORS)

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

    return tokens[0] in orphan_starts


def _is_long_list_chain(tokens: List[str]) -> bool:
    if len(tokens) < 5:
        return False

    if _contains_canonical_anchor(tokens):
        return False

    chain_hits = sum(1 for t in tokens if t in LIST_CHAIN_WORDS)
    connector_hits = sum(1 for t in tokens if t in SAFE_LONG_CONNECTORS)

    if chain_hits >= 4 and connector_hits == 0:
        return True

    if len(tokens) >= 6 and chain_hits / max(1, len(tokens)) >= 0.55 and connector_hits <= 1:
        return True

    return False

def _is_weak_education_pattern(tokens: List[str]) -> bool:
    if len(tokens) < 2:
        return False

    first = tokens[0]
    last = tokens[-1]

    return first in WEAK_EDU_PREFIXES and last in GENERIC_EDU_HEADS


def _is_action_phrase(tokens: List[str]) -> bool:
    return bool(tokens and tokens[0] in ACTION_STARTS)


def _is_query_style_long_anchor(tokens: List[str]) -> bool:
    if len(tokens) < 5:
        return False

    if tokens[0] not in QUERY_STYLE_STARTS:
        return False

    middle = tokens[1:-1]

    has_intent_connector = any(t in INTENT_CONNECTORS for t in middle)
    content_count = len(_content_tokens(tokens))

    return has_intent_connector and content_count >= 3


def _has_mid_stopword(tokens: List[str]) -> bool:
    if len(tokens) < 3:
        return False

    middle = tokens[1:-1]

    if len(tokens) >= 5:
        bad_middle = [t for t in middle if t in STOPWORDS and t not in INTENT_CONNECTORS]
        return bool(bad_middle)

    return any(t in STOPWORDS for t in middle)


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

    if _is_exact_canonical_anchor(tokens):
        return False

    strong_mods = sum(1 for t in tokens[1:-1] if t in STRONG_MODIFIER_WORDS)
    has_strong_head = bool(tokens and tokens[-1] in STRONG_CONCEPT_HEADS)

    return not (len(tokens) >= 4 and strong_mods >= 1 and has_strong_head)


def _is_list_pair_fragment(tokens: List[str]) -> bool:
    if len(tokens) != 2:
        return False

    if tuple(tokens) in VALID_ORDERED_PAIRS:
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

    if _contains_canonical_anchor(tokens):
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


def _has_action_chain_tail(tokens: List[str]) -> bool:
    if len(tokens) < 5:
        return False

    if tokens[0] in ACTION_STARTS:
        return True

    action_like_words = {
        "define", "send", "monitor", "track", "review", "manage",
        "create", "build", "check", "compare", "choose", "improve",
        "optimize", "reduce", "increase",
    }

    action_hits = sum(1 for t in tokens if t in action_like_words)
    return action_hits >= 2


def _should_trim_bad_long_phrase(tokens: List[str]) -> bool:
    if len(tokens) < 4:
        return False

    if _is_query_style_long_anchor(tokens):
        return False

    connector_count = sum(1 for t in tokens if t in INTENT_CONNECTORS or t in SAFE_LONG_CONNECTORS)

    if connector_count >= 2:
        return False

    if _contains_canonical_anchor(tokens) and len(tokens) >= 5:
        return True

    if _is_action_phrase(tokens) and len(tokens) >= 4:
        return True

    if _has_action_chain_tail(tokens):
        return True

    if _is_long_list_chain(tokens):
        return True

    if _is_multi_cluster_phrase(tokens):
        return True

    if _is_cross_niche_stitched_stack(tokens):
        return True

    return False


def _cut_semantic_tail(tokens: List[str]) -> List[str]:
    if len(tokens) < 4:
        return tokens

    core = _contains_canonical_anchor(tokens)
    if core:
        return core.split()

    first_three = tokens[:3]
    first_two = tokens[:2]

    first_three_result = score_phrase_strength(" ".join(first_three), allow_trim=False)
    if first_three_result.get("keep") and len(tokens) > 3:
        return first_three

    first_two_result = score_phrase_strength(" ".join(first_two), allow_trim=False)
    if first_two_result.get("keep") and len(tokens) > 2:
        return first_two

    return tokens


def trim_bad_long_phrase(tokens: List[str]) -> List[str]:
    if len(tokens) < 4:
        return tokens

    tail_cut = _cut_semantic_tail(tokens)
    if tail_cut != tokens:
        return tail_cut

    best_span = tokens
    best_rank = -1.0

    max_window = min(5, len(tokens))

    for size in range(2, max_window + 1):
        for i in range(0, len(tokens) - size + 1):
            span = tokens[i:i + size]

            result = score_phrase_strength(" ".join(span), allow_trim=False)

            if not result.get("keep"):
                continue

            score = float(result.get("score") or 0.0)
            starts_with_action = span[0] in ACTION_STARTS

            specificity = 0.0

            if span[0] in ACTION_STARTS:
                specificity -= 0.20

            specificity += 0.04 * sum(1 for t in span if t in STRONG_MODIFIER_WORDS)
            specificity += 0.03 * sum(1 for t in span if t in STRONG_CONCEPT_HEADS)
            specificity += 0.03 * sum(1 for t in span if t in INTENT_CONNECTORS)
            specificity += 0.02 * len(span)

            canonical_bonus = 0.0

            if starts_with_action:
                canonical_bonus -= 0.12

            if _is_exact_canonical_anchor(span):
                canonical_bonus += 0.30
            elif _has_valid_ordered_pair(span):
                canonical_bonus += 0.18

            if len(span) in {2, 3}:
                head = span[-1]

                if head in STRONG_CONCEPT_HEADS or head in NEUTRAL_NOUN_LIKE_HEADS:
                    canonical_bonus += 0.18

                if any(t in STRONG_MODIFIER_WORDS for t in span[:-1]):
                    canonical_bonus += 0.10

                if not any(t in STOPWORDS for t in span):
                    canonical_bonus += 0.08

            rank = score + specificity + canonical_bonus

            if rank > best_rank:
                best_rank = rank
                best_span = span

    return best_span


def _is_short_orphan_collision(tokens: List[str]) -> bool:
    if len(tokens) not in {2, 3}:
        return False

    if _is_query_style_long_anchor(tokens):
        return False

    if tuple(tokens) in VALID_ORDERED_PAIRS:
        return False

    if _is_exact_canonical_anchor(tokens):
        return False

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

    phrase_tuple = tuple(tokens)

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

    if _is_exact_canonical_anchor(tokens):
        return False

    if tokens[0] in STOPWORDS:
        return True

    if len(tokens) >= 3 and tokens[1] in WEAK_ADJECTIVE_STARTS:
        return True

    if len(tokens) == 3:
        first_two = tuple(tokens[:2])
        last_two = tuple(tokens[1:])

        known_safe_pairs = VALID_ORDERED_PAIRS

        if first_two in known_safe_pairs and last_two not in known_safe_pairs:
            return True

    return False


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

    if _is_cross_niche_stitched_stack(tokens):
        score -= 0.75
        reasons.append("long_cross_niche_stitch")

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

    if weak_adj_count >= 1 and not _has_valid_ordered_pair(tokens):
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

    if _is_exact_canonical_anchor(tokens):
        score += 0.25
        reasons.append("canonical_head_phrase")

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

    natural_patterns = tuple(VALID_ORDERED_PAIRS) + (
        ("late", "fee", "policy"),
        ("contract", "risk", "management"),
        ("invoice", "schedule"),
        ("employment", "policy"),
        ("workplace", "policy"),
        ("unfair", "treatment"),
        ("budget", "review"),
        ("setup", "checklist"),
        ("pricing", "strategy"),
        ("product", "pricing"),
        ("renewal", "schedule"),
        ("subscription", "pricing"),
        ("internal", "linking", "strategy"),
        ("content", "optimization", "strategy"),
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
        if not (_contains_canonical_anchor(tokens) and len(tokens) <= 5):
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

    if _is_valid_education_pattern_phrase(tokens):
        return {
            "keep": True,
            "score": 0.88,
            "phrase": p,
            "reason": "valid_education_pattern_phrase",
        }

    if _is_weak_education_pattern(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "phrase": p,
            "reason": "weak_education_pattern",
        }

    if _is_education_action_fragment(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "phrase": p,
            "reason": "education_action_fragment",
        }

    if _is_weak_education_pattern(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "phrase": p,
            "reason": "weak_education_pattern",
        }

    if _is_bad_education_fragment(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "phrase": p,
            "reason": "bad_education_fragment",
        }

    if _is_valid_education_phrase(tokens):
        return {
            "keep": True,
            "score": 0.88,
            "phrase": p,
            "reason": "valid_education_phrase",
        }

    if not p or len(tokens) < 2:
        return {"keep": False, "score": 0.0, "reason": "too_short"}

    if len(tokens) > 10:
        return {"keep": False, "score": 0.0, "reason": "too_long"}

    if _has_reversed_ordered_pair(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "phrase": p,
            "reason": "reversed_ordered_pair",
        }

    if allow_trim and _should_trim_bad_long_phrase(tokens):
        trimmed = trim_bad_long_phrase(tokens)
        if trimmed != tokens:
            p = " ".join(trimmed)
            tokens = trimmed

    if _is_cross_niche_stitched_stack(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "phrase": p,
            "reason": "cross_niche_stitched_stack",
        }

    if _is_long_list_chain(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "phrase": p,
            "reason": "long_list_chain",
        }

    if _is_multi_cluster_phrase(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "phrase": p,
            "reason": "multi_cluster_phrase",
        }

    if _is_short_orphan_collision(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "phrase": p,
            "reason": "short_orphan_collision",
        }

    if _is_prefix_suffix_spillover(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "phrase": p,
            "reason": "prefix_suffix_spillover",
        }

    if _has_orphan_tail_start(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "phrase": p,
            "reason": "orphan_tail_start",
        }

    if _has_boundary_spillover(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "phrase": p,
            "reason": "boundary_spillover",
        }

    if _has_long_clause_leakage(tokens):
        return {
            "keep": False,
            "score": 0.0,
            "phrase": p,
            "reason": "long_clause_leakage",
        }

    if tokens[0] in WEAK_STARTS and not _is_exact_canonical_anchor(tokens):
        return {"keep": False, "score": 0.10, "phrase": p, "reason": "weak_start"}

    if tokens[-1] in WEAK_ENDINGS and not _is_exact_canonical_anchor(tokens):
        return {"keep": False, "score": 0.10, "phrase": p, "reason": "weak_ending"}

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
    universal_score, universal_reasons = _universal_precision_score(tokens)

    score += head_score
    score += modifier_score
    score += standalone_score
    score += fragment_score
    score += cohesion_score
    score += domain_score
    score += action_score
    score += short_window_score
    score += long_phrase_score
    score += universal_score

    reasons.extend(head_reasons)
    reasons.extend(modifier_reasons)
    reasons.extend(standalone_reasons)
    reasons.extend(fragment_reasons)
    reasons.extend(cohesion_reasons)
    reasons.extend(domain_reasons)
    reasons.extend(action_reasons)
    reasons.extend(short_window_reasons)
    reasons.extend(long_phrase_reasons)
    reasons.extend(universal_reasons)

    score = max(0.0, min(1.0, round(score, 3)))

    if _is_query_style_long_anchor(tokens):
        content_count = len(_content_tokens(tokens))
        if content_count >= 4:
            score = max(score, 0.78)
            reasons.append("query_style_score_floor")

    if _is_exact_canonical_anchor(tokens):
        score = max(score, 0.84)
        reasons.append("canonical_score_floor")

    elif _has_valid_ordered_pair(tokens) and len(tokens) in {2, 3, 4}:
        score = max(score, 0.80)
        reasons.append("ordered_pair_score_floor")

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