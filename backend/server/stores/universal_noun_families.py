from __future__ import annotations

from typing import Dict, List, Set


DOMAIN_NOUN_FAMILIES: Dict[str, Set[str]] = {
    "marketing_seo": {
        "seo", "keyword", "keywords", "ranking", "rankings", "traffic",
        "backlink", "backlinks", "content", "search", "intent", "schema",
        "metadata", "title", "headings", "crawl", "indexing", "sitemap",
        "internal", "external", "anchor", "conversion", "campaign",
        "landing", "page", "pages", "optimization", "analytics",
    },

    "business_saas": {
        "saas", "software", "subscription", "pricing", "onboarding",
        "churn", "retention", "activation", "dashboard", "workflow",
        "customer", "customers", "support", "success", "trial", "demo",
        "revenue", "billing", "plan", "plans", "feature", "features",
        "integration", "automation", "usage", "account", "accounts",
    },

    "finance": {
        "budget", "cash", "flow", "income", "expense", "expenses",
        "debt", "loan", "loans", "interest", "payment", "payments",
        "portfolio", "investment", "investments", "asset", "assets",
        "stock", "stocks", "bond", "bonds", "fund", "funds", "tax",
        "taxes", "invoice", "invoices", "revenue", "capital",
        "forecast", "collection", "risk", "savings",
    },

    "legal": {
        "law", "legal", "contract", "contracts", "agreement", "agreements",
        "lease", "liability", "compliance", "policy", "policies",
        "clause", "clauses", "terms", "dispute", "resolution", "mediation",
        "arbitration", "court", "venue", "confidentiality", "privacy",
        "rights", "obligations", "termination", "renewal", "deposit",
        "fee", "fees", "employment", "workplace",
    },

    "real_estate": {
        "property", "properties", "mortgage", "listing", "listings",
        "tenant", "tenants", "landlord", "landlords", "rent", "rental",
        "lease", "appraisal", "inspection", "closing", "escrow",
        "title", "agent", "broker", "buyer", "seller", "zoning",
        "valuation", "equity", "foreclosure", "maintenance",
    },

    "ecommerce_retail": {
        "product", "products", "cart", "checkout", "inventory", "sku",
        "order", "orders", "shipping", "delivery", "return", "returns",
        "refund", "pricing", "discount", "coupon", "customer", "review",
        "reviews", "conversion", "catalog", "store", "retail", "payment",
        "fulfillment", "subscription",
    },

    "health_medical": {
        "health", "medical", "symptom", "symptoms", "diagnosis",
        "treatment", "medication", "dosage", "therapy", "disease",
        "condition", "conditions", "patient", "patients", "doctor",
        "clinic", "hospital", "screening", "prevention", "risk",
        "side", "effects", "blood", "pressure", "pain", "infection",
        "care",
    },

    "education": {
        "education", "student", "students", "teacher", "teachers",
        "lesson", "lessons", "course", "courses", "curriculum",
        "assessment", "exam", "exams", "quiz", "training", "learning",
        "school", "classroom", "assignment", "grade", "grades",
        "tutoring", "study", "skills", "certificate",
    },

    "travel_hospitality": {
        "travel", "hotel", "booking", "reservation", "flight", "airport",
        "tour", "tourism", "destination", "guest", "guests", "hospitality",
        "itinerary", "visa", "passport", "luggage", "resort", "checkin",
        "checkout", "room", "rooms", "rate", "rates", "trip",
    },

    "local_services": {
        "service", "services", "appointment", "booking", "customer",
        "estimate", "quote", "repair", "maintenance", "cleaning",
        "plumbing", "electrician", "landscaping", "contractor",
        "delivery", "schedule", "pricing", "review", "reviews",
    },

    "technology_developer": {
        "technology", "developer", "api", "database", "server", "frontend",
        "backend", "deployment", "code", "repository", "framework",
        "library", "sdk", "module", "plugin", "security", "authentication",
        "authorization", "endpoint", "request", "response", "cache",
        "pipeline", "workflow", "integration",
    },

    "news_media": {
        "news", "media", "article", "articles", "editorial", "publisher",
        "publication", "story", "stories", "headline", "report", "coverage",
        "journalist", "press", "broadcast", "audience", "subscription",
        "newsletter", "source", "sources",
    },

    "careers_hr": {
        "career", "careers", "job", "jobs", "resume", "interview",
        "hiring", "recruitment", "employee", "employees", "payroll",
        "benefits", "leave", "policy", "handbook", "performance",
        "onboarding", "training", "workplace", "compliance",
    },

    "home_improvement": {
        "home", "renovation", "repair", "remodel", "roofing", "flooring",
        "plumbing", "electrical", "kitchen", "bathroom", "paint",
        "contractor", "estimate", "inspection", "maintenance",
        "installation", "materials", "tools",
    },

    "sports_fitness": {
        "sport", "sports", "fitness", "training", "workout", "exercise",
        "strength", "cardio", "team", "player", "players", "coach",
        "match", "game", "league", "performance", "nutrition", "recovery",
        "routine", "injury",
    },

    "nonprofit": {
        "nonprofit", "donation", "donor", "donors", "fundraising",
        "grant", "grants", "volunteer", "volunteers", "mission",
        "program", "programs", "impact", "campaign", "community",
        "charity", "outreach", "beneficiary", "compliance",
    },

    "government_public_sector": {
        "government", "public", "policy", "agency", "department",
        "permit", "license", "compliance", "regulation", "citizen",
        "service", "services", "program", "infrastructure", "budget",
        "procurement", "records", "security",
    },

    "automotive": {
        "automotive", "vehicle", "vehicles", "car", "cars", "truck",
        "engine", "transmission", "brake", "brakes", "tire", "tires",
        "maintenance", "repair", "inspection", "dealer", "dealership",
        "warranty", "insurance", "fuel", "battery",
    },

    "insurance": {
        "insurance", "policy", "premium", "coverage", "claim", "claims",
        "deductible", "risk", "liability", "underwriting", "beneficiary",
        "exclusion", "renewal", "quote", "agent", "health", "life",
        "auto", "property",
    },

    "construction": {
        "construction", "contractor", "project", "site", "permit",
        "materials", "labor", "schedule", "budget", "estimate",
        "safety", "inspection", "equipment", "subcontractor",
        "blueprint", "foundation", "structure", "compliance",
    },

    "manufacturing": {
        "manufacturing", "production", "factory", "equipment", "machine",
        "machines", "quality", "inventory", "supply", "materials",
        "process", "workflow", "maintenance", "automation", "assembly",
        "defect", "defects", "compliance",
    },

    "logistics_supply_chain": {
        "logistics", "supply", "chain", "shipping", "freight", "warehouse",
        "inventory", "delivery", "carrier", "route", "routes", "tracking",
        "fulfillment", "procurement", "supplier", "suppliers", "shipment",
        "distribution",
    },

    "energy_utilities": {
        "energy", "utility", "utilities", "electricity", "power", "grid",
        "water", "gas", "solar", "renewable", "meter", "billing",
        "efficiency", "consumption", "infrastructure", "outage",
        "maintenance",
    },

    "telecommunications": {
        "telecommunications", "telecom", "network", "broadband", "fiber",
        "mobile", "signal", "coverage", "bandwidth", "router", "latency",
        "data", "plan", "plans", "carrier", "tower", "internet",
    },

    "food_restaurant": {
        "food", "restaurant", "menu", "reservation", "order", "orders",
        "delivery", "kitchen", "chef", "recipe", "recipes", "ingredient",
        "ingredients", "meal", "meals", "dining", "catering", "customer",
        "review", "reviews",
    },

    "beauty_fashion": {
        "beauty", "fashion", "style", "skincare", "makeup", "hair",
        "salon", "clothing", "outfit", "brand", "collection", "trend",
        "trends", "fabric", "size", "sizes", "treatment", "routine",
    },

    "entertainment": {
        "entertainment", "movie", "movies", "film", "series", "show",
        "music", "artist", "artists", "concert", "event", "events",
        "ticket", "tickets", "audience", "streaming", "performance",
        "production",
    },

    "gaming": {
        "gaming", "game", "games", "player", "players", "level", "levels",
        "quest", "quests", "character", "characters", "score", "ranking",
        "match", "server", "console", "strategy", "streaming", "esports",
    },

    "parenting_family": {
        "parenting", "family", "child", "children", "baby", "toddler",
        "school", "routine", "discipline", "sleep", "nutrition", "safety",
        "development", "care", "support", "behavior", "activities",
    },

    "pets_veterinary": {
        "pet", "pets", "veterinary", "vet", "dog", "dogs", "cat", "cats",
        "animal", "animals", "food", "nutrition", "vaccine", "vaccines",
        "grooming", "training", "behavior", "clinic", "treatment",
    },

    "agriculture": {
        "agriculture", "farm", "farms", "crop", "crops", "soil", "seed",
        "seeds", "irrigation", "fertilizer", "harvest", "livestock",
        "pest", "yield", "weather", "equipment", "market", "storage",
    },

    "science_research": {
        "science", "research", "study", "studies", "data", "experiment",
        "experiments", "method", "methods", "analysis", "model",
        "hypothesis", "sample", "samples", "laboratory", "trial",
        "evidence", "publication", "dataset",
    },

    "events_weddings": {
        "event", "events", "wedding", "venue", "guest", "guests",
        "invitation", "catering", "planner", "schedule", "budget",
        "vendor", "vendors", "ceremony", "reception", "booking",
        "decoration", "photography",
    },

    "religion_faith": {
        "religion", "faith", "church", "mosque", "temple", "prayer",
        "scripture", "sermon", "worship", "ministry", "community",
        "doctrine", "belief", "service", "pastor", "imam", "teaching",
    },

    "security_cybersecurity": {
        "security", "cybersecurity", "threat", "threats", "malware",
        "phishing", "firewall", "encryption", "authentication",
        "authorization", "breach", "incident", "vulnerability",
        "password", "access", "network", "monitoring", "compliance",
    },

    "cryptocurrency_web3": {
        "crypto", "cryptocurrency", "blockchain", "wallet", "token",
        "tokens", "defi", "nft", "smart", "contract", "exchange",
        "staking", "mining", "protocol", "ledger", "transaction",
        "gas", "governance",
    },

    "arts_design": {
        "art", "arts", "design", "designer", "illustration", "painting",
        "drawing", "portfolio", "brand", "branding", "typography",
        "color", "layout", "composition", "gallery", "creative",
        "visual", "style",
    },

    "publishing_authors": {
        "publishing", "author", "authors", "book", "books", "manuscript",
        "editor", "editing", "chapter", "chapters", "publisher",
        "royalty", "royalties", "isbn", "cover", "distribution",
        "literary", "agent",
    },

    "photography_creative_services": {
        "photography", "photo", "photos", "camera", "portrait",
        "wedding", "event", "lighting", "editing", "portfolio",
        "client", "clients", "shoot", "session", "gallery", "lens",
        "creative", "service", "services",
    },

    "environment_sustainability": {
        "environment", "sustainability", "climate", "carbon", "emissions",
        "recycling", "waste", "energy", "renewable", "water",
        "conservation", "biodiversity", "pollution", "green", "policy",
        "impact", "ecosystem",
    },
}


UNIVERSAL_CONCEPT_HEADS: Set[str] = set().union(*DOMAIN_NOUN_FAMILIES.values())


UNIVERSAL_DOMAIN_MODIFIERS: Set[str] = {
    word
    for words in DOMAIN_NOUN_FAMILIES.values()
    for word in words
}


def get_all_universal_nouns() -> Set[str]:
    return set(UNIVERSAL_CONCEPT_HEADS)


def get_all_universal_modifiers() -> Set[str]:
    return set(UNIVERSAL_DOMAIN_MODIFIERS)


def get_domain_family(domain: str) -> Set[str]:
    return set(DOMAIN_NOUN_FAMILIES.get(domain, set()))

def get_matching_domains(tokens: Set[str]) -> Dict[str, Set[str]]:
    """
    Return domains where at least one token belongs to that domain family.
    """
    out: Dict[str, Set[str]] = {}

    clean_tokens = {str(t or "").strip().lower() for t in tokens if str(t or "").strip()}

    for domain, words in DOMAIN_NOUN_FAMILIES.items():
        hits = clean_tokens.intersection(words)
        if hits:
            out[domain] = hits

    return out


def phrase_domain_cohesion(tokens: List[str]) -> Dict[str, object]:
    """
    Universal cohesion check.

    Strong phrase:
      most meaningful tokens belong to the same domain family.

    Weak stitched phrase:
      tokens belong to different unrelated families, or only one token has domain support.
    """
    clean_tokens = [
        str(t or "").strip().lower()
        for t in tokens
        if str(t or "").strip()
    ]

    if not clean_tokens:
        return {
            "best_domain": "",
            "best_hits": set(),
            "best_hit_count": 0,
            "domain_count": 0,
            "cohesion_ratio": 0.0,
            "is_cohesive": False,
        }

    token_set = set(clean_tokens)
    matches = get_matching_domains(token_set)

    if not matches:
        return {
            "best_domain": "",
            "best_hits": set(),
            "best_hit_count": 0,
            "domain_count": 0,
            "cohesion_ratio": 0.0,
            "is_cohesive": False,
        }

    best_domain = ""
    best_hits: Set[str] = set()

    for domain, hits in matches.items():
        if len(hits) > len(best_hits):
            best_domain = domain
            best_hits = hits

    meaningful_count = max(1, len(clean_tokens))
    cohesion_ratio = len(best_hits) / meaningful_count

    return {
        "best_domain": best_domain,
        "best_hits": best_hits,
        "best_hit_count": len(best_hits),
        "domain_count": len(matches),
        "cohesion_ratio": round(cohesion_ratio, 3),
        "is_cohesive": cohesion_ratio >= 0.67 and len(best_hits) >= 2,
    }