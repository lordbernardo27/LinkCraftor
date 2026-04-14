from __future__ import annotations

import re
from typing import Any, Dict, Set, Tuple


NON_ALNUM_RE = re.compile(r"[^a-z0-9\s]+")
SPACE_RE = re.compile(r"\s+")


def _normalize(text: str) -> str:
    text = (text or "").lower()
    text = NON_ALNUM_RE.sub(" ", text)
    text = SPACE_RE.sub(" ", text).strip()
    return text


def _token_set(text: str) -> Set[str]:
    t = _normalize(text)
    if not t:
        return set()
    return set(t.split())


def _contains_phrase(text: str, phrase: str) -> bool:
    t = f" {_normalize(text)} "
    p = _normalize(phrase)
    if not p:
        return False
    return f" {p} " in t


def _contains_word(text: str, word: str) -> bool:
    t = f" {_normalize(text)} "
    w = _normalize(word)
    if not w or " " in w:
        return False
    return f" {w} " in t


VERTICAL_PRIORITY: Dict[str, int] = {
    "health": 100,
    "legal": 95,
    "finance": 90,
    "tech": 85,
    "marketing_seo": 80,
    "business_saas": 75,
    "real_estate": 70,
    "local": 68,
    "ecommerce": 66,
    "education": 64,
    "parenting": 63,
    "beauty_skincare": 62,
    "fitness_wellness": 61,
    "food_nutrition": 60,
    "travel": 58,
    "home_services": 56,
    "automotive": 54,
    "media_entertainment": 52,
    "generic": 0,
}


VERTICAL_SIGNALS: Dict[str, Dict[str, Set[str]]] = {
    "health": {
        "strong_phrases": {
            "due date",
            "estimated due date",
            "official due date",
            "conception date",
            "calculate conception date",
            "how to calculate conception date",
            "date from due date",
            "embryo transfer",
            "ivf embryo transfer",
            "implantation bleeding",
            "fertile window",
            "last menstrual period",
            "basal body temperature",
            "ovulation predictor kits",
            "pregnancy test",
            "gestational age",
            "hcg trigger",
            "irregular periods",
        },
        "strong_words": {
            "pregnancy",
            "ovulation",
            "fertility",
            "gestational",
            "conception",
            "implantation",
            "ivf",
            "embryo",
            "menstrual",
            "period",
            "lmp",
            "bbt",
            "hcg",
            "symptom",
            "symptoms",
            "treatment",
            "diagnosis",
            "medication",
            "dosage",
            "disease",
            "doctor",
            "clinic",
            "infection",
        },
        "weak_words": {
            "date",
            "cycle",
            "bleeding",
            "window",
            "transfer",
            "basal",
            "temperature",
            "fertile",
            "due",
            "pregnant",
            "hospital",
            "medical",
        },
        "negative_words": {
            "pricing",
            "subscription",
            "billing",
            "dashboard",
            "webhook",
            "oauth",
            "mortgage",
            "backlink",
        },
    },
    "ecommerce": {
        "strong_phrases": {
            "best price",
            "where to buy",
            "buy now",
            "product review",
            "shipping options",
        },
        "strong_words": {
            "buy",
            "price",
            "shop",
            "review",
            "reviews",
            "brand",
            "model",
            "size",
            "color",
            "discount",
            "shipping",
            "delivery",
            "product",
            "products",
            "sale",
            "checkout",
            "cart",
            "warranty",
        },
        "weak_words": {
            "cheap",
            "order",
            "orders",
            "customer",
            "customers",
            "spec",
            "specs",
        },
        "negative_words": {
            "pregnancy",
            "ovulation",
            "conception",
            "ivf",
            "api",
            "lawsuit",
        },
    },
    "local": {
        "strong_phrases": {
            "near me",
            "nearby clinic",
            "service area",
        },
        "strong_words": {
            "nearby",
            "location",
            "locations",
            "service",
            "services",
            "city",
            "town",
            "area",
            "local",
            "accra",
            "kumasi",
            "tema",
            "restaurant",
            "dentist",
            "plumber",
            "branch",
            "office",
            "store",
            "stores",
        },
        "weak_words": {
            "near",
            "clinic",
            "hospital",
        },
        "negative_words": {
            "oauth",
            "webhook",
            "mrr",
            "pregnancy",
        },
    },
    "tech": {
        "strong_phrases": {
            "api endpoint",
            "oauth token",
            "access token",
            "webhook signature",
            "database migration",
        },
        "strong_words": {
            "api",
            "sdk",
            "webhook",
            "oauth",
            "token",
            "auth",
            "endpoint",
            "integration",
            "server",
            "client",
            "database",
            "deploy",
            "deployment",
            "bug",
            "debug",
            "code",
            "python",
            "javascript",
            "flutter",
            "react",
            "backend",
            "frontend",
            "docker",
            "cloud",
        },
        "weak_words": {
            "version",
            "microservice",
        },
        "negative_words": {
            "pregnancy",
            "conception",
            "ovulation",
            "mortgage",
        },
    },
    "finance": {
        "strong_phrases": {
            "cash flow",
            "loan interest",
            "credit score",
            "stock market",
            "tax return",
        },
        "strong_words": {
            "loan",
            "loans",
            "interest",
            "bank",
            "banking",
            "credit",
            "debt",
            "mortgage",
            "insurance",
            "invest",
            "investment",
            "tax",
            "taxes",
            "budget",
            "income",
            "salary",
            "dividend",
            "shares",
            "stock",
            "portfolio",
            "retirement",
            "financial",
        },
        "weak_words": {
            "asset",
            "assets",
        },
        "negative_words": {
            "pregnancy",
            "conception",
            "skincare",
            "webhook",
        },
    },
    "legal": {
        "strong_phrases": {
            "terms and conditions",
            "privacy policy",
            "breach of contract",
            "legal liability",
        },
        "strong_words": {
            "law",
            "legal",
            "lawyer",
            "attorney",
            "court",
            "contract",
            "claim",
            "policy",
            "rights",
            "compliance",
            "regulation",
            "regulations",
            "statute",
            "lawsuit",
            "liability",
            "agreement",
            "judge",
        },
        "weak_words": {
            "case",
            "terms",
        },
        "negative_words": {
            "pregnancy",
            "oauth",
            "retinol",
        },
    },
    "marketing_seo": {
        "strong_phrases": {
            "anchor text",
            "internal linking",
            "topic cluster",
            "organic traffic",
            "search engine",
            "technical seo",
            "semantic seo",
            "meta description",
            "title tag",
        },
        "strong_words": {
            "seo",
            "keyword",
            "keywords",
            "ranking",
            "rankings",
            "backlink",
            "backlinks",
            "serp",
            "metadata",
            "audit",
            "ctr",
        },
        "weak_words": {
            "cluster",
            "traffic",
            "content",
        },
        "negative_words": {
            "pregnancy",
            "mortgage",
            "ovulation",
        },
    },
    "business_saas": {
        "strong_phrases": {
            "customer acquisition",
            "enterprise onboarding",
            "monthly recurring revenue",
            "annual recurring revenue",
        },
        "strong_words": {
            "saas",
            "subscription",
            "subscriptions",
            "mrr",
            "arr",
            "churn",
            "cac",
            "ltv",
            "crm",
            "onboarding",
            "pricing",
            "trial",
            "conversion",
            "retention",
            "enterprise",
            "workspace",
            "dashboard",
            "billing",
            "workflow",
            "automation",
            "pipeline",
        },
        "weak_words": {
            "plan",
            "plans",
            "ops",
            "operation",
            "operations",
        },
        "negative_words": {
            "pregnancy",
            "conception",
            "implantation",
            "ivf",
            "gestational",
            "menstrual",
            "bleeding",
            "ovulation",
            "hcg",
            "bbt",
        },
    },
    "education": {
        "strong_phrases": {
            "study plan",
            "lesson plan",
            "online course",
        },
        "strong_words": {
            "school",
            "student",
            "students",
            "teacher",
            "teachers",
            "class",
            "classroom",
            "lesson",
            "lessons",
            "curriculum",
            "exam",
            "exams",
            "course",
            "courses",
            "learning",
            "education",
            "university",
            "college",
            "assignment",
            "tutorial",
            "certificate",
        },
        "weak_words": {
            "study",
            "studying",
        },
        "negative_words": {
            "mortgage",
            "pregnancy",
            "shipping",
        },
    },
    "parenting": {
        "strong_phrases": {
            "sleep training",
            "baby milestones",
        },
        "strong_words": {
            "baby",
            "toddler",
            "child",
            "children",
            "parent",
            "parents",
            "parenting",
            "newborn",
            "infant",
            "breastfeeding",
            "formula",
            "weaning",
            "diaper",
            "milestone",
            "milestones",
            "teething",
            "family",
            "postpartum",
        },
        "weak_words": {
            "maternal",
            "sleep",
            "feeding",
        },
        "negative_words": {
            "oauth",
            "mortgage",
            "stock",
        },
    },
    "beauty_skincare": {
        "strong_phrases": {
            "skin care",
            "hair care",
        },
        "strong_words": {
            "skincare",
            "acne",
            "moisturizer",
            "serum",
            "cleanser",
            "retinol",
            "sunscreen",
            "spf",
            "hyperpigmentation",
            "beauty",
            "makeup",
            "cosmetic",
            "cosmetics",
            "shampoo",
            "conditioner",
        },
        "weak_words": {
            "glow",
            "anti",
            "aging",
        },
        "negative_words": {
            "mortgage",
            "oauth",
            "pregnancy",
        },
    },
    "fitness_wellness": {
        "strong_phrases": {
            "weight loss",
            "strength training",
            "fat loss",
        },
        "strong_words": {
            "fitness",
            "workout",
            "exercise",
            "training",
            "gym",
            "muscle",
            "cardio",
            "strength",
            "wellness",
            "recovery",
            "protein",
            "stretching",
            "mobility",
            "hydration",
        },
        "weak_words": {
            "routine",
        },
        "negative_words": {
            "lawsuit",
            "shipping",
            "pregnancy",
        },
    },
    "travel": {
        "strong_phrases": {
            "flight booking",
            "travel itinerary",
        },
        "strong_words": {
            "travel",
            "trip",
            "trips",
            "tour",
            "tours",
            "destination",
            "destinations",
            "visa",
            "flight",
            "flights",
            "hotel",
            "hotels",
            "resort",
            "itinerary",
            "vacation",
            "holiday",
            "airport",
            "booking",
            "tourist",
            "tourism",
        },
        "weak_words": set(),
        "negative_words": {
            "pregnancy",
            "webhook",
            "mortgage",
        },
    },
    "real_estate": {
        "strong_phrases": {
            "real estate",
            "commercial property",
        },
        "strong_words": {
            "property",
            "properties",
            "home",
            "homes",
            "house",
            "houses",
            "apartment",
            "apartments",
            "rent",
            "rental",
            "landlord",
            "tenant",
            "mortgage",
            "listing",
            "listings",
            "agent",
            "broker",
            "realtor",
            "lease",
        },
        "weak_words": set(),
        "negative_words": {
            "symptoms",
            "retinol",
            "oauth",
        },
    },
    "food_nutrition": {
        "strong_phrases": {
            "healthy eating",
            "meal plan",
        },
        "strong_words": {
            "nutrition",
            "diet",
            "meal",
            "meals",
            "recipe",
            "recipes",
            "calories",
            "protein",
            "carbs",
            "fat",
            "vitamin",
            "vitamins",
            "mineral",
            "minerals",
            "food",
            "foods",
            "snack",
            "snacks",
        },
        "weak_words": set(),
        "negative_words": {
            "webhook",
            "lawsuit",
            "mortgage",
        },
    },
    "automotive": {
        "strong_phrases": {
            "oil change",
            "dashboard light",
        },
        "strong_words": {
            "car",
            "cars",
            "vehicle",
            "vehicles",
            "engine",
            "transmission",
            "brake",
            "brakes",
            "tire",
            "tires",
            "mechanic",
            "repair",
            "repairs",
            "fuel",
            "battery",
            "automotive",
            "maintenance",
        },
        "weak_words": set(),
        "negative_words": {
            "pregnancy",
            "retinol",
            "conception",
        },
    },
    "home_services": {
        "strong_phrases": {
            "roof repair",
            "pest control",
            "appliance repair",
            "repair service",
        },
        "strong_words": {
            "plumber",
            "electrician",
            "roofing",
            "hvac",
            "cleaning",
            "cleaner",
            "renovation",
            "contractor",
            "painting",
            "locksmith",
            "installation",
            "home",
            "service",
            "services",
        },
        "weak_words": set(),
        "negative_words": {
            "oauth",
            "pregnancy",
            "stock",
        },
    },
    "media_entertainment": {
        "strong_phrases": {
            "movie trailer",
            "celebrity news",
        },
        "strong_words": {
            "movie",
            "movies",
            "music",
            "song",
            "songs",
            "show",
            "shows",
            "series",
            "episode",
            "episodes",
            "streaming",
            "celebrity",
            "celebrities",
            "actor",
            "actress",
            "game",
            "gaming",
            "entertainment",
            "trailer",
            "film",
        },
        "weak_words": set(),
        "negative_words": {
            "mortgage",
            "dosage",
            "oauth",
        },
    },
}


VERTICAL_KEYWORDS: Dict[str, Set[str]] = {}
for _vertical, _signals in VERTICAL_SIGNALS.items():
    merged: Set[str] = set()
    for _bucket in ("strong_phrases", "strong_words", "weak_words"):
        merged.update(_signals.get(_bucket, set()))
    VERTICAL_KEYWORDS[_vertical] = merged


VERTICAL_POLICIES: Dict[str, Dict[str, Any]] = {
    "generic": {
        "boost_entities": set(),
        "boost_intents": set(),
        "boost_terms": set(),
        "penalty_terms": set(),
        "min_score": 60,
    },
    "health": {
        "boost_entities": {
            "pregnancy", "ovulation", "fertility", "conception date", "due date",
            "gestational age", "embryo transfer", "ivf", "implantation bleeding",
            "last menstrual period", "basal body temperature", "ovulation predictor kits",
            "hcg trigger", "pregnancy test",
        },
        "boost_intents": {
            "what is", "signs of", "symptoms of", "causes of", "treatment for",
            "how to calculate conception date", "calculate conception date",
        },
        "boost_terms": {
            "pregnancy", "ovulation", "conception", "due date", "gestational",
            "ivf", "implantation", "menstrual", "lmp", "bbt", "hcg",
            "embryo", "fertile window", "calculator",
        },
        "penalty_terms": {
            "pricing", "subscription", "billing", "dashboard", "webhook",
        },
        "min_score": 54,
    },
    "ecommerce": {
        "boost_entities": {"brand", "model", "price", "review", "shipping", "product"},
        "boost_intents": {"best", "buy", "reviews", "price", "where to buy"},
        "boost_terms": {"buy", "price", "review", "shipping", "product", "discount", "sale"},
        "penalty_terms": {"pregnancy", "ovulation", "conception", "ivf"},
        "min_score": 58,
    },
    "local": {
        "boost_entities": {"near me", "location", "service area", "branch", "office"},
        "boost_intents": {"near me", "best", "where to"},
        "boost_terms": {"location", "service", "nearby", "city", "area", "local"},
        "penalty_terms": {"oauth", "webhook", "mrr"},
        "min_score": 58,
    },
    "tech": {
        "boost_entities": {"api", "sdk", "webhook", "oauth", "token", "endpoint", "database"},
        "boost_intents": {"how to", "what is", "best way"},
        "boost_terms": {"api", "oauth", "token", "endpoint", "integration", "debug", "deploy"},
        "penalty_terms": {"pregnancy", "ovulation", "conception", "ivf", "mortgage"},
        "min_score": 60,
    },
    "finance": {
        "boost_entities": {"loan", "interest", "credit", "mortgage", "tax", "stock", "shares"},
        "boost_intents": {"what is", "how to", "how much"},
        "boost_terms": {"loan", "interest", "credit", "mortgage", "tax", "income", "stock"},
        "penalty_terms": {"pregnancy", "ovulation", "conception", "skincare"},
        "min_score": 60,
    },
    "legal": {
        "boost_entities": {"lawyer", "attorney", "contract", "claim", "compliance", "liability"},
        "boost_intents": {"what is", "how to", "can i"},
        "boost_terms": {"legal", "law", "contract", "policy", "rights", "court"},
        "penalty_terms": {"pregnancy", "oauth", "retinol"},
        "min_score": 60,
    },
    "marketing_seo": {
        "boost_entities": {"seo", "anchor text", "internal linking", "topic cluster", "backlinks"},
        "boost_intents": {"how to", "what is", "best way"},
        "boost_terms": {"seo", "keyword", "ranking", "backlink", "serp", "metadata"},
        "penalty_terms": {"pregnancy", "mortgage", "ovulation"},
        "min_score": 58,
    },
    "business_saas": {
        "boost_entities": {"saas", "subscription", "mrr", "arr", "retention", "billing"},
        "boost_intents": {"how to", "what is", "how much"},
        "boost_terms": {"saas", "subscription", "pricing", "trial", "enterprise", "dashboard", "workflow"},
        "penalty_terms": {
            "pregnancy", "ovulation", "conception", "implantation", "ivf",
            "gestational", "menstrual", "bleeding", "bbt", "hcg",
        },
        "min_score": 58,
    },
    "education": {
        "boost_entities": {"student", "teacher", "course", "exam", "curriculum"},
        "boost_intents": {"how to", "what is"},
        "boost_terms": {"student", "teacher", "course", "learning", "exam", "lesson"},
        "penalty_terms": {"mortgage", "pregnancy", "shipping"},
        "min_score": 58,
    },
    "parenting": {
        "boost_entities": {"baby", "toddler", "newborn", "milestones", "sleep training"},
        "boost_intents": {"how to", "what is", "when do"},
        "boost_terms": {"baby", "toddler", "child", "parenting", "newborn", "teething"},
        "penalty_terms": {"oauth", "mortgage", "stock"},
        "min_score": 58,
    },
    "beauty_skincare": {
        "boost_entities": {"skincare", "acne", "retinol", "sunscreen", "serum"},
        "boost_intents": {"how to", "best", "what is"},
        "boost_terms": {"skincare", "acne", "retinol", "spf", "moisturizer", "beauty"},
        "penalty_terms": {"mortgage", "oauth", "pregnancy"},
        "min_score": 58,
    },
    "fitness_wellness": {
        "boost_entities": {"fitness", "workout", "exercise", "weight loss", "strength training"},
        "boost_intents": {"how to", "best way", "what is"},
        "boost_terms": {"fitness", "workout", "exercise", "cardio", "strength", "recovery"},
        "penalty_terms": {"lawsuit", "shipping", "pregnancy"},
        "min_score": 58,
    },
    "travel": {
        "boost_entities": {"travel", "flight", "hotel", "visa", "itinerary"},
        "boost_intents": {"best", "how to", "where to"},
        "boost_terms": {"travel", "trip", "destination", "flight", "hotel", "booking"},
        "penalty_terms": {"pregnancy", "webhook", "mortgage"},
        "min_score": 58,
    },
    "real_estate": {
        "boost_entities": {"real estate", "property", "apartment", "mortgage", "lease"},
        "boost_intents": {"how to", "what is", "how much"},
        "boost_terms": {"property", "apartment", "rent", "rental", "mortgage", "listing"},
        "penalty_terms": {"symptoms", "retinol", "oauth"},
        "min_score": 58,
    },
    "food_nutrition": {
        "boost_entities": {"nutrition", "diet", "meal", "recipe", "protein"},
        "boost_intents": {"how to", "best", "what is"},
        "boost_terms": {"nutrition", "diet", "meal", "recipe", "calories", "protein"},
        "penalty_terms": {"webhook", "lawsuit", "mortgage"},
        "min_score": 58,
    },
    "automotive": {
        "boost_entities": {"car", "engine", "brake", "oil change", "battery"},
        "boost_intents": {"how to", "what is", "when to"},
        "boost_terms": {"car", "vehicle", "engine", "brake", "repair", "maintenance"},
        "penalty_terms": {"pregnancy", "retinol", "conception"},
        "min_score": 58,
    },
    "home_services": {
        "boost_entities": {"plumber", "electrician", "roof repair", "hvac", "pest control"},
        "boost_intents": {"how to", "best", "near me"},
        "boost_terms": {"plumber", "electrician", "roofing", "hvac", "cleaning", "contractor"},
        "penalty_terms": {"oauth", "pregnancy", "stock"},
        "min_score": 58,
    },
    "media_entertainment": {
        "boost_entities": {"movie", "music", "series", "streaming", "celebrity"},
        "boost_intents": {"best", "what is", "where to watch"},
        "boost_terms": {"movie", "music", "show", "series", "streaming", "trailer"},
        "penalty_terms": {"mortgage", "dosage", "oauth"},
        "min_score": 58,
    },
}


def detect_vertical(text: str) -> str:
    text_n = _normalize(text)
    if not text_n:
        return "generic"

    token_set = _token_set(text_n)

    best_vertical = "generic"
    best_score = 0
    best_strong_hits = 0
    best_total_hits = 0
    best_priority = -1

    for vertical, signals in VERTICAL_SIGNALS.items():
        strong_phrase_hits = sum(1 for p in signals.get("strong_phrases", set()) if _contains_phrase(text_n, p))
        strong_word_hits = sum(1 for w in signals.get("strong_words", set()) if w in token_set)
        weak_word_hits = sum(1 for w in signals.get("weak_words", set()) if w in token_set)
        negative_hits = sum(1 for w in signals.get("negative_words", set()) if w in token_set)

        score = 0
        score += strong_phrase_hits * 10
        score += strong_word_hits * 6
        score += weak_word_hits * 2
        score -= negative_hits * 5

        total_hits = strong_phrase_hits + strong_word_hits + weak_word_hits
        strong_hits = strong_phrase_hits + strong_word_hits
        priority = VERTICAL_PRIORITY.get(vertical, 0)

        if (
            score > best_score
            or (
                score == best_score
                and strong_hits > best_strong_hits
            )
            or (
                score == best_score
                and strong_hits == best_strong_hits
                and total_hits > best_total_hits
            )
            or (
                score == best_score
                and strong_hits == best_strong_hits
                and total_hits == best_total_hits
                and priority > best_priority
            )
        ):
            best_vertical = vertical
            best_score = score
            best_strong_hits = strong_hits
            best_total_hits = total_hits
            best_priority = priority

    if best_score < 6:
        return "generic"

    return best_vertical


def get_vertical_policy(vertical: str) -> Dict[str, Any]:
    return VERTICAL_POLICIES.get(vertical, VERTICAL_POLICIES["generic"])


def apply_vertical_policy_score(
    phrase: str,
    base_score: int,
    vertical: str,
) -> int:
    policy = get_vertical_policy(vertical)
    p = _normalize(phrase)

    score = int(base_score)

    for term in policy.get("boost_entities", set()):
        if _contains_phrase(p, term):
            score += 8

    for term in policy.get("boost_intents", set()):
        term_n = _normalize(term)
        if p.startswith(term_n):
            score += 8

    for term in policy.get("boost_terms", set()):
        term_n = _normalize(term)
        if " " in term_n:
            if _contains_phrase(p, term_n):
                score += 4
        else:
            if term_n in _token_set(p):
                score += 4

    for term in policy.get("penalty_terms", set()):
        term_n = _normalize(term)
        if " " in term_n:
            if _contains_phrase(p, term_n):
                score -= 10
        else:
            if term_n in _token_set(p):
                score -= 10

    return score


def get_vertical_min_score(vertical: str) -> int:
    policy = get_vertical_policy(vertical)
    return int(policy.get("min_score", 60))