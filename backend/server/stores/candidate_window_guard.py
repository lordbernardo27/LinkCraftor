from __future__ import annotations

import re
from typing import Dict, List, Set, Any, Tuple


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
    "on", "between", "among", "against", "through", "into", "across", "near",
    "within", "around", "under", "over",
}

ACTION_LEAK_STARTS: Set[str] = {
    "neglect", "avoid", "reduce", "improve", "manage", "check", "monitor",
    "track", "review", "choose", "define", "send", "skip", "treat",
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
    "successful", "strongest", "regular", "normal",
}

GENERIC_HEADS: Set[str] = {
    "tools", "tool", "things", "thing", "ways", "way", "areas", "area",
    "parts", "part", "problem", "problems", "issue", "issues",
    "result", "results", "system", "systems", "topic", "topics",
    "factor", "factors", "method", "methods", "option", "options",
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

BAD_EDUCATION_FRAGMENTS: Set[str] = {
    "students time motivation system",
    "study biology today",
    "preparation exam",
    "learning new material to revision",
    "students time",
    "motivation system",
    "subjects topic",
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
}

REVERSED_ORDERED_PAIRS: Set[Tuple[str, str]] = {
    (b, a) for a, b in VALID_ORDERED_PAIRS
}

BAD_BOUNDARY_STARTS: Set[str] = {
    "quickly", "slowly", "often", "usually", "sometimes", "thing", "things",
    "face", "facing", "many", "several", "various", "different", "some",
    "any", "each", "every", "other", "another", "certain",
}

BAD_BOUNDARY_ENDS: Set[str] = {
    "thing", "things", "way", "ways", "area", "areas", "part", "parts",
    "issue", "issues", "problem", "problems", "result", "results",
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

ANCHOR_CORE_PHRASES: Set[str] = {
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
}


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]


def _vertical_keyword_hits(tokens: List[str]) -> int:
    token_set = set(tokens)
    hits = 0
    for terms in VERTICAL_KEYWORD_MAP.values():
        if token_set & terms:
            hits += 1
    return hits


def _phrase_from_tokens(tokens: List[str]) -> str:
    return " ".join(tokens)


def _contains_valid_core_phrase(tokens: List[str]) -> str:
    if not tokens:
        return ""

    joined = _phrase_from_tokens(tokens)

    for core in sorted(ANCHOR_CORE_PHRASES, key=lambda x: len(x.split()), reverse=True):
        if core in joined:
            return core

    return ""

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

def _is_weak_education_pattern(tokens: List[str]) -> bool:
    if len(tokens) < 2:
        return False

    first = tokens[0]
    last = tokens[-1]

    return first in WEAK_EDU_PREFIXES and last in GENERIC_EDU_HEADS


def _has_reversed_ordered_pair(tokens: List[str]) -> bool:
    if len(tokens) < 2:
        return False

    pairs = list(zip(tokens, tokens[1:]))
    return any(pair in REVERSED_ORDERED_PAIRS for pair in pairs)


def _has_valid_ordered_pair(tokens: List[str]) -> bool:
    if len(tokens) < 2:
        return False

    pairs = list(zip(tokens, tokens[1:]))
    return any(pair in VALID_ORDERED_PAIRS for pair in pairs)

def _is_valid_education_phrase(tokens: List[str]) -> bool:
    return " ".join(tokens) in VALID_EDUCATION_PHRASES


def _is_bad_education_fragment(tokens: List[str]) -> bool:
    return " ".join(tokens) in BAD_EDUCATION_FRAGMENTS


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
        if (
            t in NOUN_CHAIN_WORDS
            or t in GENERIC_HEADS
            or t in WEAK_CARRYOVER_WORDS
        ):
            head_like += 1

    return head_like >= 2

def _is_education_action_fragment(tokens: List[str]) -> bool:
    if len(tokens) < 2:
        return False

    if " ".join(tokens) in VALID_EDUCATION_PHRASES:
        return False

    return tokens[0] in EDU_ACTION_FRAGMENT_STARTS and tokens[-1] in EDU_GENERIC_OBJECT_HEADS


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

    if _contains_valid_core_phrase(tokens) and len(tokens) <= 6:
        return False

    return any(t in CLAUSE_VERBS for t in tokens)


def _starts_or_ends_badly(tokens: List[str]) -> bool:
    if not tokens:
        return True

    if tokens[0] in STOPWORDS:
        return True

    if tokens[-1] in STOPWORDS:
        return True

    if tokens[0] in BAD_BOUNDARY_STARTS:
        return True

    if tokens[-1] in BAD_BOUNDARY_ENDS:
        return True

    if len(tokens) >= 3 and tokens[0] in GENERIC_ADJECTIVES and tokens[-1] in GENERIC_HEADS:
        return True

    return False


def _is_low_value_generic_survivor(tokens: List[str]) -> bool:
    phrase = _phrase_from_tokens(tokens)
    return phrase in LOW_VALUE_GENERIC_SURVIVORS


def _is_dense_noun_chain(tokens: List[str]) -> bool:
    if len(tokens) < 4:
        return False

    if _is_query_like(tokens):
        return False

    if _contains_valid_core_phrase(tokens):
        return False

    connector_count = sum(1 for t in tokens if t in CONNECTORS)
    chain_hits = sum(1 for t in tokens if t in NOUN_CHAIN_WORDS)
    vertical_hits = _vertical_keyword_hits(tokens)

    if len(tokens) >= 4 and chain_hits / max(1, len(tokens)) >= 0.75 and connector_count == 0:
        return True

    if len(tokens) >= 5 and chain_hits / max(1, len(tokens)) >= 0.60 and connector_count <= 1:
        return True

    if len(tokens) >= 5 and vertical_hits >= 3 and connector_count == 0:
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

    weak_pairs = {
        ("movement", "medication"),
        ("helpful", "medication"),
        ("successful", "management"),
        ("strongest", "tools"),
        ("thing", "revenue"),
        ("face", "cash"),
        ("quickly", "cash"),
    }

    return (left, right) in weak_pairs


def _has_repeated_or_duplicate_noise(tokens: List[str]) -> bool:
    if len(tokens) < 3:
        return False

    unique_ratio = len(set(tokens)) / max(1, len(tokens))
    return unique_ratio < 0.75


def _is_stitched_vertical_list(tokens: List[str]) -> bool:
    if len(tokens) < 4:
        return False

    if _is_query_like(tokens):
        return False

    if _contains_valid_core_phrase(tokens):
        return False

    connector_count = sum(1 for t in tokens if t in CONNECTORS)
    if connector_count > 0:
        return False

    token_set = set(tokens)
    total_vertical_term_hits = 0

    for terms in VERTICAL_KEYWORD_MAP.values():
        total_vertical_term_hits += len(token_set & terms)

    return total_vertical_term_hits >= 4


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
        return {"keep": False, "reason": "empty_candidate", "phrase": ""}

    tokens = phrase.split()

    if _is_valid_education_pattern_phrase(tokens):
        return {"keep": True, "reason": "valid_education_pattern_phrase", "phrase": phrase}

    if _is_weak_education_pattern(tokens):
        return {"keep": False, "reason": "weak_education_pattern", "phrase": phrase}

    if _is_education_action_fragment(tokens):
        return {
            "keep": False,
            "reason": "education_action_fragment",
            "phrase": phrase,
        }

    if _is_weak_education_pattern(tokens):
        return {
            "keep": False,
            "reason": "weak_education_pattern",
            "phrase": phrase,
        }

    if _is_valid_education_phrase(tokens):
        return {"keep": True, "reason": "valid_education_phrase", "phrase": phrase}

    if _is_bad_education_fragment(tokens):
        return {"keep": False, "reason": "bad_education_fragment", "phrase": phrase}

    if len(tokens) < 2:
        return {"keep": False, "reason": "too_short", "phrase": phrase}

    compressed_phrase = _compress_long_wrapper(tokens)
    compressed_tokens = compressed_phrase.split()

    if compressed_phrase != phrase and len(compressed_tokens) >= 2:
        phrase = compressed_phrase
        tokens = compressed_tokens

    if len(tokens) > 10:
        return {"keep": False, "reason": "too_long", "phrase": phrase}

    if _starts_or_ends_badly(tokens):
        return {"keep": False, "reason": "bad_boundary", "phrase": phrase}

    if _has_reversed_ordered_pair(tokens):
        return {"keep": False, "reason": "reversed_ordered_pair", "phrase": phrase}

    if _is_action_leak_start(tokens):
        return {"keep": False, "reason": "action_leak_start", "phrase": phrase}

    if _is_short_multi_head_collision(tokens):
        return {"keep": False, "reason": "short_multi_head_collision", "phrase": phrase}

    if _is_long_carryover_stack(tokens):
        return {"keep": False, "reason": "long_carryover_stack", "phrase": phrase}

    if _has_clause_leak(tokens):
        return {"keep": False, "reason": "clause_leak", "phrase": phrase}

    if _is_stitched_vertical_list(tokens):
        return {"keep": False, "reason": "stitched_vertical_list", "phrase": phrase}

    if _is_dense_noun_chain(tokens):
        return {"keep": False, "reason": "dense_noun_chain", "phrase": phrase}

    if _has_repeated_or_duplicate_noise(tokens):
        return {"keep": False, "reason": "duplicate_noise", "phrase": phrase}

    if _is_generic_short_false_positive(tokens):
        return {"keep": False, "reason": "generic_short_false_positive", "phrase": phrase}

    if _is_low_value_generic_survivor(tokens):
        return {"keep": False, "reason": "low_value_generic_survivor", "phrase": phrase}

    return {"keep": True, "reason": "guard_pass", "phrase": phrase}