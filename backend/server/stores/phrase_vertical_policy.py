from __future__ import annotations

import re
from typing import Any, Dict, Set


NON_ALNUM_RE = re.compile(r"[^a-z0-9\s]+")
SPACE_RE = re.compile(r"\s+")


def _normalize(text: str) -> str:
    text = (text or "").lower()
    text = NON_ALNUM_RE.sub(" ", text)
    text = SPACE_RE.sub(" ", text).strip()
    return text


def _token_set(text: str) -> Set[str]:
    t = _normalize(text)
    return set(t.split()) if t else set()


def _contains_phrase(text: str, phrase: str) -> bool:
    t = f" {_normalize(text)} "
    p = _normalize(phrase)
    return bool(p and f" {p} " in t)


VERTICAL_PRIORITY: Dict[str, int] = {
    "medical_healthcare": 100,
    "pharmacy": 99,
    "mental_health": 98,
    "legal": 96,
    "finance": 94,
    "real_estate": 92,
    "ecommerce": 90,
    "saas": 88,
    "marketing": 86,
    "small_business": 84,
    "hr_recruiting": 82,
    "it_cybersecurity": 80,
    "programming_development": 79,
    "ai_machine_learning": 78,
    "education": 76,
    "careers": 74,
    "professional_training": 73,
    "fitness": 72,
    "nutrition": 71,
    "beauty_skincare": 70,
    "home_improvement": 68,
    "interior_design": 67,
    "gardening": 66,
    "parenting_family": 65,
    "pets": 64,
    "food_recipes": 63,
    "travel": 62,
    "automotive": 61,
    "consumer_tech": 60,
    "gaming": 58,
    "sports": 57,
    "entertainment": 56,
    "music": 55,
    "manufacturing": 54,
    "construction": 53,
    "logistics": 52,
    "agriculture": 51,
    "energy": 50,
    "telecom": 49,
    "government": 48,
    "nonprofit": 47,
    "religion_faith": 46,
    "local_services": 45,
    "blogging": 44,
    "youtube_video_creators": 43,
    "influencers_personal_brands": 42,
    "courses_info_products": 41,
    "web3_crypto": 40,
    "sustainability": 39,
    "remote_work": 38,
    "multi_niche_publishers": 37,
    "generic": 0,
}


VERTICAL_SIGNALS: Dict[str, Dict[str, Set[str]]] = {
    "finance": {
        "strong_phrases": {"cash flow", "cash flow management", "credit score", "tax return", "loan interest", "accounts receivable", "working capital"},
        "strong_words": {"cash", "flow", "revenue", "profit", "invoice", "invoices", "payroll", "tax", "taxes", "loan", "loans", "credit", "banking", "investment", "insurance", "accounting", "budget", "debt", "mortgage"},
        "weak_words": {"asset", "assets", "payment", "payments", "income", "expenses"},
        "negative_words": {"pregnancy", "ovulation", "skincare", "retinol", "webhook"},
    },
    "real_estate": {
        "strong_phrases": {"real estate", "rental property", "lease agreement", "property management", "commercial property"},
        "strong_words": {"property", "mortgage", "lease", "rent", "tenant", "landlord", "listing", "home", "buyer", "seller", "appraisal", "closing", "apartment", "realtor", "broker"},
        "weak_words": {"house", "houses", "agent"},
        "negative_words": {"symptoms", "retinol", "oauth", "pregnancy"},
    },
    "legal": {
        "strong_phrases": {"privacy policy", "breach of contract", "legal liability", "terms and conditions", "lease agreement"},
        "strong_words": {"law", "legal", "contract", "compliance", "court", "attorney", "lawyer", "claim", "liability", "agreement", "clause", "regulation", "lawsuit", "rights", "judge"},
        "weak_words": {"case", "terms", "policy"},
        "negative_words": {"pregnancy", "retinol", "oauth"},
    },
    "ecommerce": {
        "strong_phrases": {"product pages", "category pages", "checkout cart", "shipping options", "product review"},
        "strong_words": {"product", "products", "cart", "checkout", "shopify", "woocommerce", "marketplace", "category", "pages", "inventory", "orders", "shipping", "delivery", "discount", "sale", "warranty"},
        "weak_words": {"price", "buy", "shop", "customer", "customers"},
        "negative_words": {"pregnancy", "ovulation", "lawsuit", "oauth"},
    },
    "saas": {
        "strong_phrases": {"monthly recurring revenue", "annual recurring revenue", "customer onboarding", "subscription pricing", "enterprise dashboard"},
        "strong_words": {"software", "subscription", "platform", "dashboard", "workflow", "crm", "analytics", "integration", "automation", "users", "saas", "mrr", "arr", "churn", "retention", "billing", "workspace"},
        "weak_words": {"plan", "plans", "trial", "pipeline"},
        "negative_words": {"pregnancy", "ovulation", "ivf", "retinol"},
    },
    "marketing": {
        "strong_phrases": {"internal linking", "anchor text", "topic cluster", "search intent", "content marketing", "technical seo", "meta description"},
        "strong_words": {"seo", "content", "campaign", "conversion", "keyword", "keywords", "brand", "email", "traffic", "search", "intent", "backlink", "ranking", "serp", "ctr"},
        "weak_words": {"cluster", "metadata", "audit"},
        "negative_words": {"pregnancy", "mortgage", "retinol"},
    },
    "small_business": {
        "strong_phrases": {"cash flow", "cash flow forecast", "small business", "business operations"},
        "strong_words": {"business", "cash", "flow", "payroll", "operations", "customers", "suppliers", "expenses", "forecast", "invoicing", "revenue", "profit", "owner"},
        "weak_words": {"bills", "systems", "process"},
        "negative_words": {"pregnancy", "retinol", "oauth"},
    },
    "hr_recruiting": {
        "strong_phrases": {"employee onboarding", "performance review", "job description", "hiring process"},
        "strong_words": {"hiring", "recruiting", "onboarding", "payroll", "benefits", "employee", "employees", "performance", "staffing", "resume", "interview", "workplace"},
        "weak_words": {"team", "teams", "policy"},
        "negative_words": {"pregnancy", "mortgage", "retinol"},
    },
    "medical_healthcare": {
        "strong_phrases": {"blood pressure", "blood pressure control", "treatment plan", "side effects", "pregnancy test", "gestational age"},
        "strong_words": {"health", "blood", "pressure", "diagnosis", "treatment", "symptoms", "clinic", "patient", "screening", "condition", "doctor", "hospital", "disease", "infection"},
        "weak_words": {"medical", "care", "therapy"},
        "negative_words": {"pricing", "subscription", "webhook", "mortgage"},
    },
    "pharmacy": {
        "strong_phrases": {"side effects", "medication adherence", "prescription medicine", "otc medicine"},
        "strong_words": {"medication", "medicine", "dose", "dosing", "dosage", "effects", "prescription", "otc", "adherence", "pharmacist", "drug", "drugs", "tablet", "capsule"},
        "weak_words": {"treatment", "therapy"},
        "negative_words": {"mortgage", "webhook", "backlink"},
    },
    "mental_health": {
        "strong_phrases": {"mental health", "anxiety symptoms", "therapy session", "stress management"},
        "strong_words": {"anxiety", "therapy", "counseling", "stress", "depression", "mental", "wellbeing", "support", "trauma", "mindfulness"},
        "weak_words": {"mood", "emotion"},
        "negative_words": {"mortgage", "webhook", "checkout"},
    },
    "fitness": {
        "strong_phrases": {"strength training", "weight loss", "fat loss", "workout plan"},
        "strong_words": {"exercise", "training", "strength", "mobility", "workout", "endurance", "muscle", "recovery", "fitness", "gym", "cardio"},
        "weak_words": {"routine", "hydration"},
        "negative_words": {"lawsuit", "webhook", "mortgage"},
    },
    "nutrition": {
        "strong_phrases": {"healthy eating", "meal plan", "protein intake", "calorie deficit"},
        "strong_words": {"diet", "nutrition", "meal", "meals", "protein", "calories", "supplements", "weight", "healthy", "eating", "vitamins", "minerals"},
        "weak_words": {"food", "snack"},
        "negative_words": {"webhook", "lawsuit", "mortgage"},
    },
    "beauty_skincare": {
        "strong_phrases": {"skin care", "hair care", "acne treatment", "sunscreen routine"},
        "strong_words": {"skin", "skincare", "hair", "cosmetics", "dermatology", "grooming", "acne", "moisturizer", "serum", "retinol", "sunscreen", "spf"},
        "weak_words": {"beauty", "glow", "aging"},
        "negative_words": {"mortgage", "oauth", "webhook"},
    },
    "home_improvement": {
        "strong_phrases": {"roof repair", "pest control", "hvac maintenance", "plumbing repair"},
        "strong_words": {"plumbing", "roofing", "hvac", "painting", "remodeling", "repair", "tools", "contractor", "electrician", "installation"},
        "weak_words": {"home", "service"},
        "negative_words": {"pregnancy", "stock", "oauth"},
    },
    "interior_design": {
        "strong_phrases": {"interior design", "room layout", "furniture placement"},
        "strong_words": {"furniture", "decor", "layout", "renovation", "lighting", "style", "room", "design", "color", "curtains"},
        "weak_words": {"space", "home"},
        "negative_words": {"pregnancy", "webhook", "mortgage"},
    },
    "gardening": {
        "strong_phrases": {"lawn care", "pest control", "garden soil", "plant care"},
        "strong_words": {"plants", "garden", "landscaping", "lawn", "soil", "irrigation", "pest", "compost", "seeds", "flowers"},
        "weak_words": {"green", "water"},
        "negative_words": {"webhook", "mortgage", "lawsuit"},
    },
    "parenting_family": {
        "strong_phrases": {"baby milestones", "sleep training", "child development"},
        "strong_words": {"pregnancy", "baby", "child", "children", "parenting", "family", "development", "school", "newborn", "toddler", "teething", "breastfeeding"},
        "weak_words": {"sleep", "feeding"},
        "negative_words": {"oauth", "mortgage", "stock"},
    },
    "pets": {
        "strong_phrases": {"dog training", "cat food", "pet grooming", "veterinary care"},
        "strong_words": {"dog", "dogs", "cat", "cats", "pet", "pets", "training", "grooming", "veterinary", "food", "vet", "puppy", "kitten"},
        "weak_words": {"animal", "care"},
        "negative_words": {"mortgage", "webhook", "retinol"},
    },
    "food_recipes": {
        "strong_phrases": {"recipe ideas", "meal prep", "baking tips", "kitchen tools"},
        "strong_words": {"recipe", "recipes", "cooking", "baking", "kitchen", "meal", "restaurant", "ingredients", "dish", "flavor"},
        "weak_words": {"food", "taste"},
        "negative_words": {"webhook", "lawsuit", "mortgage"},
    },

        "travel": {
        "strong_phrases": {"flight booking", "travel itinerary", "hotel booking", "visa application"},
        "strong_words": {"flight", "hotel", "visa", "itinerary", "tourism", "destination", "travel", "guide", "booking", "trip", "airport", "vacation"},
        "weak_words": {"tour", "holiday"},
        "negative_words": {"webhook", "mortgage", "retinol"},
    },
    "automotive": {
        "strong_phrases": {"oil change", "car repair", "vehicle maintenance", "dashboard light"},
        "strong_words": {"car", "cars", "auto", "repair", "vehicle", "ev", "insurance", "detailing", "maintenance", "engine", "brake", "tire", "battery"},
        "weak_words": {"mechanic", "fuel"},
        "negative_words": {"pregnancy", "retinol", "conception"},
    },
    "education": {
        "strong_phrases": {"study plan", "lesson plan", "online course", "exam preparation"},
        "strong_words": {"school", "student", "students", "course", "exam", "tutoring", "lesson", "study", "learning", "teacher", "classroom", "curriculum"},
        "weak_words": {"assignment", "tutorial"},
        "negative_words": {"mortgage", "shipping", "retinol"},
    },
    "careers": {
        "strong_phrases": {"resume writing", "job interview", "career growth", "salary negotiation"},
        "strong_words": {"resume", "interview", "salary", "career", "freelancing", "job", "promotion", "skills", "employment", "workplace"},
        "weak_words": {"role", "position"},
        "negative_words": {"pregnancy", "mortgage", "retinol"},
    },
    "professional_training": {
        "strong_phrases": {"certification exam", "continuing education", "professional license"},
        "strong_words": {"certification", "license", "training", "continuing", "education", "professional", "exam", "credential", "course"},
        "weak_words": {"learning", "skills"},
        "negative_words": {"mortgage", "retinol", "webhook"},
    },
    "consumer_tech": {
        "strong_phrases": {"smartphone review", "laptop comparison", "wearable device"},
        "strong_words": {"phone", "laptop", "gadget", "wearable", "accessory", "device", "tablet", "smartphone", "camera", "charger"},
        "weak_words": {"screen", "battery"},
        "negative_words": {"pregnancy", "mortgage", "lawsuit"},
    },
    "it_cybersecurity": {
        "strong_phrases": {"data security", "network security", "cloud security", "endpoint protection"},
        "strong_words": {"network", "cloud", "security", "cybersecurity", "infrastructure", "compliance", "server", "endpoint", "firewall", "malware", "breach"},
        "weak_words": {"system", "access"},
        "negative_words": {"pregnancy", "retinol", "mortgage"},
    },
    "programming_development": {
        "strong_phrases": {"api endpoint", "database migration", "backend deployment", "frontend framework"},
        "strong_words": {"code", "coding", "api", "database", "framework", "devops", "frontend", "backend", "deployment", "python", "javascript", "react", "flutter"},
        "weak_words": {"bug", "debug", "server"},
        "negative_words": {"pregnancy", "mortgage", "retinol"},
    },
    "ai_machine_learning": {
        "strong_phrases": {"machine learning", "artificial intelligence", "training data", "prompt engineering"},
        "strong_words": {"ai", "machine", "learning", "model", "models", "prompt", "automation", "dataset", "training", "neural", "embedding"},
        "weak_words": {"data", "agent"},
        "negative_words": {"pregnancy", "mortgage", "retinol"},
    },
    "gaming": {
        "strong_phrases": {"gaming guide", "level guide", "console gaming", "esports team"},
        "strong_words": {"game", "gaming", "console", "pc", "mobile", "esports", "guide", "level", "players", "quest", "match"},
        "weak_words": {"skill", "rank"},
        "negative_words": {"mortgage", "pregnancy", "retinol"},
    },
    "sports": {
        "strong_phrases": {"sports training", "team performance", "league match"},
        "strong_words": {"sports", "team", "teams", "player", "players", "training", "match", "league", "equipment", "coach", "tournament"},
        "weak_words": {"score", "fitness"},
        "negative_words": {"mortgage", "webhook", "retinol"},
    },
    "entertainment": {
        "strong_phrases": {"movie trailer", "celebrity news", "streaming series"},
        "strong_words": {"movie", "movies", "tv", "celebrity", "streaming", "series", "show", "culture", "film", "trailer", "actor"},
        "weak_words": {"episode", "season"},
        "negative_words": {"mortgage", "dosage", "oauth"},
    },
    "music": {
        "strong_phrases": {"music production", "guitar lesson", "artist promotion"},
        "strong_words": {"music", "artist", "artists", "instrument", "production", "lesson", "gear", "song", "songs", "album", "guitar"},
        "weak_words": {"sound", "audio"},
        "negative_words": {"mortgage", "pregnancy", "oauth"},
    },
    "manufacturing": {
        "strong_phrases": {"supply chain", "quality control", "production system"},
        "strong_words": {"manufacturing", "production", "machinery", "quality", "supply", "chain", "factory", "materials", "assembly", "process"},
        "weak_words": {"equipment", "output"},
        "negative_words": {"pregnancy", "retinol", "mortgage"},
    },
    "construction": {
        "strong_phrases": {"construction project", "building materials", "project bidding"},
        "strong_words": {"construction", "contractor", "materials", "bidding", "project", "site", "building", "concrete", "permit"},
        "weak_words": {"labor", "tools"},
        "negative_words": {"pregnancy", "retinol", "webhook"},
    },
    "logistics": {
        "strong_phrases": {"supply chain", "fleet management", "warehouse operations", "freight shipping"},
        "strong_words": {"shipping", "freight", "warehouse", "warehousing", "fleet", "delivery", "logistics", "carrier", "route", "inventory", "fulfillment"},
        "weak_words": {"tracking", "package"},
        "negative_words": {"pregnancy", "retinol", "lawsuit"},
    },
    "agriculture": {
        "strong_phrases": {"crop rotation", "livestock farming", "irrigation system", "soil health"},
        "strong_words": {"farming", "livestock", "crops", "irrigation", "soil", "agritech", "harvest", "farm", "fertilizer", "seeds"},
        "weak_words": {"field", "yield"},
        "negative_words": {"webhook", "mortgage", "retinol"},
    },
    "energy": {
        "strong_phrases": {"solar energy", "renewable energy", "utility bill", "energy efficiency"},
        "strong_words": {"solar", "energy", "utilities", "sustainability", "oil", "gas", "renewable", "grid", "electricity", "battery"},
        "weak_words": {"power", "fuel"},
        "negative_words": {"pregnancy", "retinol", "oauth"},
    },
    "telecom": {
        "strong_phrases": {"mobile network", "internet provider", "broadband plan", "signal strength"},
        "strong_words": {"internet", "mobile", "network", "telecom", "broadband", "provider", "device", "signal", "router", "fiber"},
        "weak_words": {"data", "coverage"},
        "negative_words": {"pregnancy", "retinol", "mortgage"},
    },
    "government": {
        "strong_phrases": {"public service", "permit application", "government program"},
        "strong_words": {"permit", "policy", "public", "service", "services", "program", "government", "license", "agency", "municipal"},
        "weak_words": {"office", "department"},
        "negative_words": {"retinol", "checkout", "webhook"},
    },
    "nonprofit": {
        "strong_phrases": {"fundraising campaign", "volunteer program", "donation drive"},
        "strong_words": {"donation", "fundraising", "volunteer", "outreach", "nonprofit", "charity", "community", "donor", "grant"},
        "weak_words": {"mission", "support"},
        "negative_words": {"mortgage", "checkout", "webhook"},
    },
    "religion_faith": {
        "strong_phrases": {"faith community", "church ministry", "worship service"},
        "strong_words": {"faith", "ministry", "church", "teaching", "religion", "community", "worship", "sermon", "prayer"},
        "weak_words": {"belief", "spiritual"},
        "negative_words": {"webhook", "mortgage", "checkout"},
    },
    "local_services": {
        "strong_phrases": {"near me", "local service", "service area", "nearby dentist"},
        "strong_words": {"dentist", "plumber", "cleaner", "lawyer", "contractor", "local", "service", "nearby", "location", "city", "area"},
        "weak_words": {"office", "branch"},
        "negative_words": {"oauth", "webhook", "mrr"},
    },
    "blogging": {
        "strong_phrases": {"affiliate blog", "authority site", "blog post", "content niche"},
        "strong_words": {"blog", "blogging", "affiliate", "content", "authority", "niche", "publisher", "posts", "article", "articles"},
        "weak_words": {"topic", "topics"},
        "negative_words": {"pregnancy", "retinol", "mortgage"},
    },
    "youtube_video_creators": {
        "strong_phrases": {"youtube script", "video thumbnail", "channel growth"},
        "strong_words": {"youtube", "video", "thumbnail", "script", "monetization", "creator", "channel", "views", "subscribers"},
        "weak_words": {"content", "audience"},
        "negative_words": {"mortgage", "webhook", "retinol"},
    },
    "influencers_personal_brands": {
        "strong_phrases": {"personal brand", "audience growth", "sponsorship deal"},
        "strong_words": {"influencer", "brand", "audience", "sponsorship", "community", "followers", "creator", "engagement"},
        "weak_words": {"content", "profile"},
        "negative_words": {"mortgage", "webhook", "dosage"},
    },
    "courses_info_products": {
        "strong_phrases": {"online course", "digital product", "membership site", "coaching program"},
        "strong_words": {"course", "courses", "membership", "coaching", "digital", "product", "products", "lesson", "module", "students"},
        "weak_words": {"training", "content"},
        "negative_words": {"mortgage", "retinol", "webhook"},
    },
    "web3_crypto": {
        "strong_phrases": {"crypto wallet", "blockchain network", "defi protocol", "nft marketplace"},
        "strong_words": {"crypto", "blockchain", "wallet", "token", "tokens", "defi", "nft", "web3", "exchange", "staking"},
        "weak_words": {"coin", "coins"},
        "negative_words": {"pregnancy", "retinol", "mortgage"},
    },
    "sustainability": {
        "strong_phrases": {"carbon footprint", "green living", "eco products", "climate action"},
        "strong_words": {"green", "carbon", "eco", "sustainable", "sustainability", "climate", "recycling", "environment", "renewable"},
        "weak_words": {"energy", "waste"},
        "negative_words": {"oauth", "retinol", "mortgage"},
    },
    "remote_work": {
        "strong_phrases": {"remote work", "distributed team", "work from home", "digital nomad"},
        "strong_words": {"remote", "work", "distributed", "team", "teams", "home", "digital", "nomad", "hybrid", "async"},
        "weak_words": {"workspace", "productivity"},
        "negative_words": {"pregnancy", "retinol", "mortgage"},
    },
    "multi_niche_publishers": {
        "strong_phrases": {"content network", "authority site", "multi niche", "publisher network"},
        "strong_words": {"publisher", "publishers", "content", "network", "topics", "authority", "articles", "editorial", "category"},
        "weak_words": {"blog", "site"},
        "negative_words": {"webhook", "oauth", "retinol"},
    },
}

VERTICAL_KEYWORDS: Dict[str, Set[str]] = {}

for _vertical, _signals in VERTICAL_SIGNALS.items():
    merged: Set[str] = set()
    for _bucket in ("strong_phrases", "strong_words", "weak_words"):
        merged.update(_signals.get(_bucket, set()))
    VERTICAL_KEYWORDS[_vertical] = merged


VERTICAL_MIN_SCORE: Dict[str, int] = {
    "medical_healthcare": 54,
    "pharmacy": 54,
    "mental_health": 56,
    "legal": 60,
    "finance": 60,
    "real_estate": 58,
    "ecommerce": 58,
    "saas": 58,
    "marketing": 58,
    "small_business": 58,
    "hr_recruiting": 58,
    "it_cybersecurity": 60,
    "programming_development": 60,
    "ai_machine_learning": 60,
    "education": 58,
    "careers": 58,
    "professional_training": 58,
    "fitness": 58,
    "nutrition": 58,
    "beauty_skincare": 58,
    "home_improvement": 58,
    "interior_design": 58,
    "gardening": 58,
    "parenting_family": 58,
    "pets": 58,
    "food_recipes": 58,
    "travel": 58,
    "automotive": 58,
    "consumer_tech": 58,
    "gaming": 58,
    "sports": 58,
    "entertainment": 58,
    "music": 58,
    "manufacturing": 58,
    "construction": 58,
    "logistics": 58,
    "agriculture": 58,
    "energy": 58,
    "telecom": 58,
    "government": 58,
    "nonprofit": 58,
    "religion_faith": 58,
    "local_services": 56,
    "blogging": 58,
    "youtube_video_creators": 58,
    "influencers_personal_brands": 58,
    "courses_info_products": 58,
    "web3_crypto": 60,
    "sustainability": 58,
    "remote_work": 58,
    "multi_niche_publishers": 58,
    "generic": 60,
}


def _build_policy(vertical: str) -> Dict[str, Any]:
    signals = VERTICAL_SIGNALS.get(vertical, {})

    strong_phrases = set(signals.get("strong_phrases", set()))
    strong_words = set(signals.get("strong_words", set()))
    weak_words = set(signals.get("weak_words", set()))
    negative_words = set(signals.get("negative_words", set()))

    return {
        "boost_entities": strong_phrases | strong_words,
        "boost_intents": {
            "how to",
            "what is",
            "best",
            "best way",
            "when to",
            "where to",
            "why",
            "guide",
        },
        "boost_terms": strong_phrases | strong_words | weak_words,
        "penalty_terms": negative_words,
        "min_score": VERTICAL_MIN_SCORE.get(vertical, 60),
    }


VERTICAL_POLICIES: Dict[str, Dict[str, Any]] = {
    "generic": {
        "boost_entities": set(),
        "boost_intents": set(),
        "boost_terms": set(),
        "penalty_terms": set(),
        "min_score": 60,
    }
}

for _vertical_name in VERTICAL_SIGNALS.keys():
    VERTICAL_POLICIES[_vertical_name] = _build_policy(_vertical_name)


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
        strong_phrase_hits = sum(
            1 for phrase in signals.get("strong_phrases", set())
            if _contains_phrase(text_n, phrase)
        )

        strong_word_hits = sum(
            1 for word in signals.get("strong_words", set())
            if word in token_set
        )

        weak_word_hits = sum(
            1 for word in signals.get("weak_words", set())
            if word in token_set
        )

        negative_hits = sum(
            1 for word in signals.get("negative_words", set())
            if word in token_set
        )

        score = 0
        score += strong_phrase_hits * 12
        score += strong_word_hits * 6
        score += weak_word_hits * 2
        score -= negative_hits * 6

        total_hits = strong_phrase_hits + strong_word_hits + weak_word_hits
        strong_hits = strong_phrase_hits + strong_word_hits
        priority = VERTICAL_PRIORITY.get(vertical, 0)

        if (
            score > best_score
            or (score == best_score and strong_hits > best_strong_hits)
            or (score == best_score and strong_hits == best_strong_hits and total_hits > best_total_hits)
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
        if term_n and p.startswith(term_n):
            score += 8

    for term in policy.get("boost_terms", set()):
        term_n = _normalize(term)

        if not term_n:
            continue

        if " " in term_n:
            if _contains_phrase(p, term_n):
                score += 4
        else:
            if term_n in _token_set(p):
                score += 4

    for term in policy.get("penalty_terms", set()):
        term_n = _normalize(term)

        if not term_n:
            continue

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