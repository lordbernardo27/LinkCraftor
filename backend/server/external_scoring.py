# LinkCraftor/backend/server/external_scoring.py
# ---------------------------------------------------------
# External URL confidence & gating layer for the global
# External URL Dataset.
#
# This is backend-only logic (no FastAPI here).
# It is conceptually similar to assets/js/engine/scoring.js:
#  - compute a 0–1 confidence score
#  - decide if a mapping should be saved to the global dataset
#  - produce a canonical / semantic key for grouping phrases
#
# Later, /api/external/resolve in server/main.py will call
# these helpers when it wants to auto-save a mapping.

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict
import math
import re
from urllib.parse import urlparse


# ---------------------------------------------------------
# 1) Basic configuration
# ---------------------------------------------------------

# Domain authority, similar idea as EXTERNAL_DOMAIN_AUTHORITY in scoring.js
# You can extend this over time. Unknown domains get a neutral base.
DOMAIN_AUTHORITY: Dict[str, float] = {
    "nhs.uk":                         1.0,
    "www.nhs.uk":                     1.0,
    "nih.gov":                        1.0,
    "www.nih.gov":                    1.0,
    "who.int":                        1.0,
    "www.who.int":                    1.0,
    "mayoclinic.org":                 0.9,
    "www.mayoclinic.org":             0.9,
    "healthline.com":                 0.8,
    "www.healthline.com":             0.8,
    "pubmed.ncbi.nlm.nih.gov":        0.95,
    "www.cochranelibrary.com":        0.95,
    "www.nice.org.uk":                0.95,
    "www.acog.org":                   0.95,
    # everything else falls back to ~0.6–0.7 starting point
}

# Provider trust levels (OPTIONAL, works for 24 or 200+ providers)
# If a provider is not listed, we just treat it as medium trust.
PROVIDER_TRUST: Dict[str, float] = {
    # core medical / guideline
    "acog":         1.0,
    "pubmed":       0.95,
    "cochrane":     0.95,
    "nice":         0.95,
    "who":          0.9,
    "who_maternal": 0.95,
    "who_reproductive": 0.9,
    "cdc":          0.9,
    "nih":          0.9,

    # hospital & patient education
    "mayo":             0.9,
    "clevelandclinic":  0.85,
    "cleveland_obgyn":  0.9,
    "stanford_childrens": 0.85,
    "hopkins":          0.9,
    "mount_sinai":      0.85,

    # drugs
    "drugs":        0.9,
    "rxlist":       0.85,
    "webmd":        0.75,

    # child / public health
    "unicef":       0.85,
    "medlineplus":  0.85,
    "nhs":          0.95,
    "healthline":   0.75,
}

# Origin trust: how much we trust this mapping source before scoring.
# This lets you enforce:
#  - canonical > user CSV > global dataset reuse
# Fallback providers are *never* stored, so they can use a low weight.
ORIGIN_TRUST: Dict[str, float] = {
    "canonical":          1.0,
    "user_external_csv":  0.9,
    "global_dataset":     0.85,
    "fallback_provider":  0.5,   # but we will NEVER store these
}

# Thresholds for auto-saving into the Global External URL Dataset
# You can tune these later. Start conservative.
CONFIDENCE_THRESHOLD_STRICT = 0.82   # only above this we store globally
CONFIDENCE_THRESHOLD_SOFT   = 0.70   # below this: never auto-store


# ---------------------------------------------------------
# 2) Normalization & lexical helpers (mini port of scoring.js)
# ---------------------------------------------------------

STOPWORDS = {
    "the", "a", "an", "of", "for", "to", "and", "in", "on", "with",
    "is", "are", "be", "can", "how", "what", "when", "why", "does",
    "do", "it", "that", "this", "these", "those", "your", "my"
}


def safe_norm(text: str) -> str:
    """Lowercase, trim, collapse whitespace."""
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def tokenize(text: str) -> List[str]:
    """Simple tokenization similar to scoring.js."""
    clean = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
    tokens = re.split(r"\s+", clean)
    return [t for t in tokens if t]


def phrase_to_semantic_key(phrase: str) -> str:
    """
    Semantic normalization for grouping:
    - lowercase
    - remove punctuation
    - remove stopwords
    - collapse spaces
    Examples:
      "White cervical mucus" -> "white cervical mucus"
      "What is cervical mucus?" -> "cervical mucus"
    """
    tokens = tokenize(phrase)
    tokens = [t for t in tokens if t not in STOPWORDS]
    if not tokens:
        return safe_norm(phrase)
    return " ".join(tokens)


def lexical_similarity(a: str, b: str) -> float:
    """
    Rough Jaccard + containment, similar spirit to lexicalScore in scoring.js,
    but simplified for backend.
    """
    ta = set(tokenize(a))
    tb = set(tokenize(b))
    if not ta or not tb:
        return 0.0

    overlap = len(ta & tb)
    union = len(ta | tb)
    jaccard = overlap / union if union else 0.0

    a_str = " ".join(sorted(ta))
    b_str = " ".join(sorted(tb))
    contains = 1.0 if (a_str in b_str or b_str in a_str) else 0.0

    score = 0.6 * jaccard + 0.4 * contains
    if score < 0:
        score = 0.0
    if score > 1:
        score = 1.0
    return score


# ---------------------------------------------------------
# 3) Semantic cluster / “similar meaning” boost
# ---------------------------------------------------------

def cluster_semantic_boost(
    phrase: str,
    cluster_phrases: Optional[List[str]] = None
) -> float:
    """
    If multiple *different* phrases already map to the same URL,
    and they are semantically similar, we add a small confidence boost.

    Example:
      - "white cervical mucus"
      - "white mucus in cervix"
      - "cervical mucus white"
    If all of these go to the same URL, our trust should increase.

    Returns a value in [0, 0.15].
    """
    if not cluster_phrases:
        return 0.0

    sims = []
    for existing in cluster_phrases:
        s = lexical_similarity(phrase, existing)
        if s > 0.25:
            sims.append(s)

    if not sims:
        return 0.0

    avg = sum(sims) / len(sims)
    # Up to +0.15 boost, scaled by average similarity and count
    boost = min(0.15, avg * 0.10 + len(sims) * 0.01)
    return boost


# ---------------------------------------------------------
# 4) Domain / provider / origin signals
# ---------------------------------------------------------

def extract_domain(url: str) -> str:
    try:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        # strip common port numbers
        host = host.split(":")[0]
        return host
    except Exception:
        return ""


def domain_score(url: str) -> float:
    host = extract_domain(url)
    if not host:
        return 0.0
    # Exact host match
    if host in DOMAIN_AUTHORITY:
        return DOMAIN_AUTHORITY[host]
    # Try base domain (e.g. pubmed.ncbi.nlm.nih.gov → ncbi.nlm.nih.gov)
    parts = host.split(".")
    if len(parts) > 2:
        base = ".".join(parts[-3:])
        if base in DOMAIN_AUTHORITY:
            return DOMAIN_AUTHORITY[base]
    if len(parts) > 1:
        base2 = ".".join(parts[-2:])
        if base2 in DOMAIN_AUTHORITY:
            return DOMAIN_AUTHORITY[base2]
    # Default medium value
    return 0.65


def provider_trust(provider_id: Optional[str]) -> float:
    if not provider_id:
        return 0.7
    pid = provider_id.lower()
    return PROVIDER_TRUST.get(pid, 0.7)


def origin_trust(origin: Optional[str]) -> float:
    if not origin:
        return 0.7
    return ORIGIN_TRUST.get(origin, 0.7)


# ---------------------------------------------------------
# 5) Confidence result type
# ---------------------------------------------------------

@dataclass
class ExternalConfidenceResult:
    phrase: str
    url: str
    canonical_key: str
    origin: str
    provider_id: Optional[str]
    confidence: float    # 0–1
    tier: str            # "high" | "mid" | "low" | "reject"
    should_store: bool   # can we save into Global External URL Dataset?
    details: dict        # sub-scores & explanation for debugging


# ---------------------------------------------------------
# 6) Main scoring function
# ---------------------------------------------------------

def compute_external_confidence(
    phrase: str,
    url: str,
    *,
    origin: str = "canonical",
    provider_id: Optional[str] = None,
    cluster_phrases: Optional[List[str]] = None
) -> ExternalConfidenceResult:
    """
    Core external confidence calculator:
    - phrase: highlighted phrase from the doc
    - url:   chosen external URL
    - origin: where it came from
      ("canonical" | "user_external_csv" | "global_dataset" | "fallback_provider")
    - provider_id: optional, like "pubmed", "acog", etc.
    - cluster_phrases: other phrases that already map to this URL (for semantic boost)

    Returns ExternalConfidenceResult with:
    - confidence 0–1
    - tier
    - should_store (for global dataset)
    """
    phrase = phrase or ""
    url = url or ""
    origin = origin or "canonical"

    if not phrase.strip() or not url.strip():
        return ExternalConfidenceResult(
            phrase=phrase,
            url=url,
            canonical_key=phrase_to_semantic_key(phrase),
            origin=origin,
            provider_id=provider_id,
            confidence=0.0,
            tier="reject",
            should_store=False,
            details={"reason": "missing_phrase_or_url"}
        )

    # --- base signals ---
    d_score  = domain_score(url)              # 0–1 (domain authority)
    p_trust  = provider_trust(provider_id)    # 0–1 (provider reliability)
    o_trust  = origin_trust(origin)           # 0–1 (mapping origin trust)

    # small semantic cluster boost
    sem_boost = cluster_semantic_boost(phrase, cluster_phrases)

    # Combine into a single confidence value.
    # We bias domain & provider heavily, then origin, then semantic boost.
    # All weights can be tuned later.
    combined = (
        0.40 * d_score +
        0.30 * p_trust +
        0.20 * o_trust +
        sem_boost           # already small (0–0.15)
    )

    # Clip to [0,1]
    if combined < 0:
        combined = 0.0
    if combined > 1:
        combined = 1.0

    # Tiering
    if combined >= 0.88:
        tier = "high"
    elif combined >= 0.75:
        tier = "mid"
    elif combined >= 0.60:
        tier = "low"
    else:
        tier = "reject"

    # Global storage decision:
    #  - never store fallback_provider mappings
    #  - only store if confidence is above strict threshold
    if origin == "fallback_provider":
        should_store = False
    else:
        should_store = combined >= CONFIDENCE_THRESHOLD_STRICT

    canonical_key = phrase_to_semantic_key(phrase)

    details = {
        "domain_score": d_score,
        "provider_trust": p_trust,
        "origin_trust": o_trust,
        "semantic_boost": sem_boost
    }

    # If we're below the soft threshold, treat as reject for dataset purposes.
    if combined < CONFIDENCE_THRESHOLD_SOFT:
        tier = "reject"
        should_store = False

    return ExternalConfidenceResult(
        phrase=phrase,
        url=url,
        canonical_key=canonical_key,
        origin=origin,
        provider_id=provider_id,
        confidence=combined,
        tier=tier,
        should_store=should_store,
        details=details,
    )
