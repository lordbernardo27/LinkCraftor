from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


GENERAL_PROFILE: Dict[str, Any] = {
    "id": "general",
    "display_name": "General",
    "entity_importance": {
        "TOPIC": 1.0,
        "ENTITY": 1.2,
        "PRODUCT": 1.3,
        "FEATURE": 1.2,
        "API": 1.2,
        "USE_CASE": 1.1,
    },
    "context_rules": {
        "GUIDE": ["TOPIC", "FEATURE", "USE_CASE"],
        "COMPARISON": ["TOPIC", "PRODUCT", "FEATURE"],
        "BENEFIT": ["FEATURE", "USE_CASE"],
        "WARNING": ["TOPIC"],
    },
    "external_trust": {},
    "internal_priority": {
        "sitemap": 1.0,
        "backup": 0.9,
        "uploaded": 0.8,
        "draft": 0.6,
        "docs": 1.0,
        "blog": 0.8,
    },
    "thresholds": {
        "internal_min": 0.35,
        "semantic_min": 0.12,
        "external_min": 0.55,
    },
}


MEDICAL_PROFILE: Dict[str, Any] = {
    "id": "medical",
    "display_name": "Medical / Health",
    "entity_importance": {
        "DRUG": 3.0,
        "DISEASE": 2.5,
        "CONDITION": 2.5,
        "SYMPTOM": 2.0,
        "MECHANISM": 1.8,
        "TOPIC": 1.0,
    },
    "context_rules": {
        "SIDE_EFFECTS": ["SYMPTOM", "MECHANISM"],
        "WARNING": ["RISK", "CONDITION"],
        "TREATMENT": ["DRUG", "THERAPY"],
        "GUIDE": ["TOPIC", "CONDITION", "DRUG"],
    },
    "external_trust": {
        "nhs.uk": 1.0,
        "nih.gov": 1.0,
        "who.int": 1.0,
        "mayoclinic.org": 0.95,
        "healthline.com": 0.85,
    },
    "internal_priority": {
        "sitemap": 1.0,
        "backup": 0.9,
        "uploaded": 0.8,
        "draft": 0.6,
    },
    "thresholds": {
        "internal_min": 0.35,
        "semantic_min": 0.12,
        "external_min": 0.55,
    },
}


SAAS_PROFILE: Dict[str, Any] = {
    "id": "saas",
    "display_name": "SaaS / Tech",
    "entity_importance": {
        "PRODUCT": 3.0,
        "FEATURE": 2.8,
        "API": 2.5,
        "INTEGRATION": 2.2,
        "USE_CASE": 2.0,
        "SYSTEM": 1.8,
        "TOPIC": 1.0,
    },
    "context_rules": {
        "USE_CASE": ["FEATURE", "INTEGRATION"],
        "PRICING": ["PLAN", "FEATURE"],
        "LIMITATION": ["API", "SYSTEM"],
        "GUIDE": ["FEATURE", "USE_CASE", "API"],
    },
    "external_trust": {
        "docs.aws.amazon.com": 1.0,
        "developer.mozilla.org": 1.0,
        "cloud.google.com": 0.95,
        "stripe.com": 0.95,
        "github.com": 0.90,
    },
    "internal_priority": {
        "docs": 1.0,
        "sitemap": 0.95,
        "blog": 0.8,
        "uploaded": 0.75,
        "draft": 0.6,
    },
    "thresholds": {
        "internal_min": 0.30,
        "semantic_min": 0.15,
        "external_min": 0.50,
    },
}

FINANCE_PROFILE: Dict[str, Any] = {
    "id": "finance",
    "display_name": "Finance / Investing",
    "entity_importance": {
        "ASSET": 3.0,
        "METRIC": 2.8,
        "STRATEGY": 2.5,
        "RISK": 2.3,
        "MARKET": 2.0,
        "COMPANY": 1.8,
        "TOPIC": 1.0,
    },
    "context_rules": {
        "GUIDE": ["STRATEGY", "TOPIC", "METRIC"],
        "COMPARISON": ["ASSET", "STRATEGY", "MARKET"],
        "RISK": ["RISK", "ASSET", "MARKET"],
        "ANALYSIS": ["METRIC", "MARKET", "COMPANY"],
        "ACTIONABLE": ["STRATEGY", "ASSET"],
    },
    "external_trust": {
        "investopedia.com": 1.0,
        "morningstar.com": 0.95,
        "sec.gov": 1.0,
        "federalreserve.gov": 1.0,
        "finance.yahoo.com": 0.85,
    },
    "internal_priority": {
        "sitemap": 1.0,
        "backup": 0.9,
        "uploaded": 0.8,
        "draft": 0.6,
        "research": 0.95,
        "blog": 0.8,
    },
    "thresholds": {
        "internal_min": 0.32,
        "semantic_min": 0.14,
        "external_min": 0.55,
    },
}

ECOMMERCE_PROFILE: Dict[str, Any] = {
    "id": "ecommerce",
    "display_name": "Ecommerce / Product Content",
    "entity_importance": {
        "PRODUCT": 3.0,
        "CATEGORY": 2.6,
        "FEATURE": 2.5,
        "BRAND": 2.2,
        "USE_CASE": 2.0,
        "SPEC": 1.8,
        "TOPIC": 1.0,
    },
    "context_rules": {
        "GUIDE": ["PRODUCT", "CATEGORY", "USE_CASE"],
        "COMPARISON": ["PRODUCT", "FEATURE", "BRAND"],
        "BUYING_GUIDE": ["PRODUCT", "CATEGORY", "FEATURE"],
        "REVIEW": ["PRODUCT", "FEATURE", "SPEC"],
        "ACTIONABLE": ["PRODUCT", "USE_CASE"],
    },
    "external_trust": {
        "amazon.com": 0.9,
        "bestbuy.com": 0.9,
        "walmart.com": 0.85,
        "target.com": 0.85,
        "shopify.com": 0.8,
    },
    "internal_priority": {
        "sitemap": 1.0,
        "backup": 0.9,
        "uploaded": 0.8,
        "draft": 0.6,
        "catalog": 0.95,
        "blog": 0.8,
    },
    "thresholds": {
        "internal_min": 0.30,
        "semantic_min": 0.14,
        "external_min": 0.55,
    },
}

PROFILES: Dict[str, Dict[str, Any]] = {
    "general": GENERAL_PROFILE,
    "medical": MEDICAL_PROFILE,
    "saas": SAAS_PROFILE,
    "finance": FINANCE_PROFILE,
    "ecommerce": ECOMMERCE_PROFILE,
}

ALLOWED_PROFILE_IDS = set(PROFILES.keys())

def normalize_profile_id(profile_id: str | None, default: str = "general") -> str:
    key = str(profile_id or "").strip().lower()
    if key in ALLOWED_PROFILE_IDS:
        return key
    return default


def get_profile(profile_id: str | None = None) -> Dict[str, Any]:
    """
    Return a safe copy of the requested profile.
    Falls back to GENERAL_PROFILE if profile_id is missing or unknown.
    """
    key = str(profile_id or "").strip().lower()
    profile = PROFILES.get(key, GENERAL_PROFILE)
    return deepcopy(profile)