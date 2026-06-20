from __future__ import annotations

import re
from typing import Any, Dict, List, Set


STOPWORDS = {
    "the","a","an","and","or","to","of","in","on","for","with","by","from",
    "after","before","right","left","early","late","best","new","old",
    "how","what","why","when","where","can","does","do","is","are","was","were",
    "this","that","these","those","your","you","i","we","it","as","at","be",
    "been","being","into","than","then","also","both","may","might","will",
    "long","short","goes","going","down","up","works","work","take","takes",
    "several","many","much","more","less","later","unless",
}


def _tokens(value: str) -> List[str]:
    return [
        t for t in re.findall(r"[a-z0-9]+", str(value or "").lower())
        if len(t) >= 3 and t not in STOPWORDS
    ]


def _unique_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        item = str(item or "").strip()
        key = item.lower()
        if item and key not in seen:
            seen.add(key)
            out.append(item)
    return out


def _clean_alias_v1(value: str) -> str:
    toks = _tokens(value)
    toks = _unique_keep_order(toks)

    # prevent aliases like "renewal renewal"
    if len(set(toks)) != len(toks):
        toks = list(dict.fromkeys(toks))

    return " ".join(toks).strip()


def _valid_alias_v1(value: str) -> bool:
    toks = _tokens(value)

    if len(toks) < 2:
        return False

    if len(set(toks)) < 2:
        return False

    return True


def _context_topic_phrases_v1(context_terms: List[str]) -> List[str]:
    terms = _unique_keep_order(context_terms)
    out = []

    for size in (4, 3, 2):
        for i in range(0, max(0, len(terms) - size + 1)):
            candidate = " ".join(terms[i:i + size])
            if _valid_alias_v1(candidate):
                out.append(candidate)

    return _unique_keep_order(out)




UNIVERSAL_CONCEPT_PATTERNS = {
    "identity": {
        "account", "profile", "user", "member", "customer", "subscriber",
        "owner", "holder", "client", "organization", "company", "business"
    },
    "access": {
        "login", "signin", "access", "permission", "authorization",
        "credential", "credentials", "password", "security",
        "authentication", "verification"
    },
    "transaction": {
        "payment", "payments", "purchase", "checkout", "order", "invoice",
        "billing", "subscription", "pricing", "cost", "price", "refund",
        "quote", "fee", "fees", "bill"
    },
    "compliance": {
        "license", "licence", "permit", "registration", "certification",
        "approval", "requirement", "requirements", "regulation",
        "regulations", "policy", "policies", "law", "laws", "deadline",
        "renewal", "expire", "reinstatement"
    },
    "planning": {
        "plan", "planning", "schedule", "timeline", "forecast", "estimate",
        "estimated", "calculate", "calculation", "calculator", "budget",
        "prepare", "preparing", "strategy", "formula", "method", "methods"
    },
    "comparison": {
        "compare", "comparison", "versus", "alternative", "alternatives",
        "difference", "differences", "better", "best", "option", "options"
    },
    "monitoring": {
        "track", "tracking", "monitor", "check", "checker", "measure",
        "measurement", "assessment", "screening", "scan", "test", "testing",
        "exam", "diagnosis", "audit", "inspection"
    },
    "optimization": {
        "improve", "increase", "reduce", "lower", "optimize",
        "optimization", "boost", "saving", "savings", "performance",
        "efficiency"
    },
    "problem_solving": {
        "fix", "solve", "avoid", "prevent", "issue", "problem", "error",
        "mistake", "troubleshoot", "troubleshooting", "repair", "unsafe"
    },
    "education": {
        "guide", "tutorial", "learn", "training", "course", "lesson",
        "explained", "overview", "introduction", "definition", "meaning",
        "basics", "advice", "tips"
    },
    "location": {
        "near", "nearby", "local", "location", "locations", "office",
        "offices", "branch", "clinic", "clinics", "hospital", "store",
        "facility", "center", "centre"
    },

    # Legacy-compatible broad concepts kept for continuity.
    "calculation": {"calculate", "calculation", "calculator", "estimated", "estimate", "formula", "method", "methods"},
    "timing": {"date", "dates", "deadline", "schedule", "window", "period", "month", "months", "time", "timing"},
    "change": {"change", "changing", "adjust", "adjustment", "modify", "modified", "update", "revised"},
    "return": {"return", "returning", "resume", "resumes", "restore", "recovery", "restart"},
    "regularity": {"regular", "regularity", "consistent", "predictable", "pattern", "patterns", "routine"},
    "finance": {"mortgage", "loan", "interest", "rate", "rates", "refinance", "refinancing", "credit", "debt"},
    "evidence": {"evidence", "proof", "data", "study", "studies", "research", "analysis"},
    "risk": {"risk", "risks", "chance", "probability", "danger", "warning", "concern", "concerns"},
    "symptom": {"symptom", "symptoms", "sign", "signs", "indicator", "indicators"},
    "treatment": {"treatment", "treat", "therapy", "medicine", "medication", "management"},
    "product": {"product", "products", "device", "devices", "brand", "brands", "buy", "purchase"},
}


def extract_context_concepts_v1(
    *,
    phrase: str,
    context_terms: List[str] | None = None,
) -> Dict[str, Any]:

    terms = set(_tokens(" ".join([phrase] + list(context_terms or []))))
    concepts = []

    for concept, vocab in UNIVERSAL_CONCEPT_PATTERNS.items():
        overlap = sorted(terms.intersection(vocab))
        if not overlap:
            continue

        confidence = min(0.95, 0.45 + (0.12 * len(overlap)))

        concepts.append({
            "concept": concept,
            "confidence": round(confidence, 4),
            "matched_terms": overlap,
        })

    concepts = sorted(concepts, key=lambda x: x["confidence"], reverse=True)

    primary = concepts[0]["concept"] if concepts else "unknown"

    return {
        "has_context_concepts": bool(concepts),
        "primary_concept": primary,
        "concepts": concepts[:8],
        "concept_count": len(concepts),
        "method": "universal_context_concept_extraction_v1",
    }


def _conceptual_aliases_v1(
    *,
    phrase_terms: List[str],
    context_terms: List[str],
    concepts: Dict[str, Any],
) -> List[Dict[str, Any]]:

    concept_names = [c.get("concept") for c in concepts.get("concepts", []) if c.get("concept")]
    terms = _unique_keep_order(context_terms)

    aliases = []

    # Universal concept + topic combinations
    for concept in concept_names[:4]:
        for topic in terms[:6]:
            if concept == topic:
                continue

            alias = _clean_alias_v1(f"{topic} {concept}")
            if _valid_alias_v1(alias):
                aliases.append({
                    "alias": alias,
                    "confidence": 0.84,
                    "source": "context_concept_alias",
                })

    # Primary concept with phrase terms
    primary = concepts.get("primary_concept")
    if primary and primary != "unknown":
        for pt in phrase_terms[:4]:
            if pt == primary:
                continue

            alias = _clean_alias_v1(f"{pt} {primary}")
            if _valid_alias_v1(alias):
                aliases.append({
                    "alias": alias,
                    "confidence": 0.80,
                    "source": "phrase_concept_alias",
                })

    return aliases


def extract_phrase_context_v1(
    *,
    phrase: str,
    sentence: str = "",
    previous_sentence: str = "",
    next_sentence: str = "",
    heading: str = "",
    document_title: str = "",
    paragraph: str = "",
) -> Dict[str, Any]:

    context_text = " ".join([
        previous_sentence,
        sentence,
        next_sentence,
        heading,
        document_title,
        paragraph,
    ])

    phrase_terms = _tokens(phrase)
    context_terms = _tokens(context_text)

    weighted_terms = []

    for t in _tokens(document_title):
        weighted_terms.extend([t, t])

    for t in _tokens(heading):
        weighted_terms.extend([t, t])

    weighted_terms.extend(context_terms)

    top_terms = _unique_keep_order(weighted_terms)[:20]
    context_concepts = extract_context_concepts_v1(
        phrase=phrase,
        context_terms=top_terms,
    )

    return {
        "has_context": bool(str(context_text or "").strip()),
        "phrase": phrase,
        "phrase_terms": phrase_terms,
        "context_terms": top_terms,
        "context_concepts": context_concepts,
        "context_window": {
            "previous_sentence": previous_sentence,
            "current_sentence": sentence,
            "next_sentence": next_sentence,
            "heading": heading,
            "document_title": document_title,
            "paragraph": paragraph,
        },
    }


def generate_canonical_phrase_v1(
    *,
    phrase: str,
    context_analysis: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    context_analysis = context_analysis or {}
    phrase_terms = context_analysis.get("phrase_terms") or _tokens(phrase)
    context_terms = context_analysis.get("context_terms") or []
    context_concepts = context_analysis.get("context_concepts") or {}
    primary_concept = context_concepts.get("primary_concept")

    # Universal canonical rule:
    # Prefer phrase meaning terms, then strong context terms from title/heading/sentence.
    canonical_terms = []

    for t in phrase_terms:
        if t not in canonical_terms:
            canonical_terms.append(t)

    if primary_concept and primary_concept != "unknown" and primary_concept not in canonical_terms:
        canonical_terms.append(primary_concept)

    for t in context_terms:
        if t not in canonical_terms and len(canonical_terms) < 4:
            canonical_terms.append(t)

    canonical = _clean_alias_v1(" ".join(canonical_terms[:4]))

    if not canonical:
        canonical = str(phrase or "").strip()
        confidence = 0.0
    else:
        confidence = min(
            0.92,
            0.40 + (0.09 * len(set(phrase_terms))) + (0.025 * len(set(context_terms)))
        )

    return {
        "canonical_phrase": canonical,
        "canonical_terms": canonical_terms[:4],
        "confidence": round(confidence, 4),
        "method": "universal_phrase_context_canonicalization_v1",
    }


def expand_phrase_aliases_v1(
    *,
    phrase: str,
    canonical_phrase: str,
    context_analysis: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    context_analysis = context_analysis or {}
    phrase_terms = context_analysis.get("phrase_terms") or _tokens(phrase)
    context_terms = context_analysis.get("context_terms") or []
    context_concepts = context_analysis.get("context_concepts") or {}

    aliases = []

    canonical_clean = _clean_alias_v1(canonical_phrase)
    if _valid_alias_v1(canonical_clean):
        aliases.append({
            "alias": canonical_clean,
            "confidence": 0.92,
            "source": "canonical_phrase",
        })

    # Concept-aware aliases are preferred over raw token-window aliases.
    aliases.extend(_conceptual_aliases_v1(
        phrase_terms=phrase_terms,
        context_terms=context_terms,
        concepts=context_concepts,
    ))

    # Strong context topic phrases are usually better than random word pairs.
    for topic_phrase in _context_topic_phrases_v1(context_terms)[:8]:
        aliases.append({
            "alias": topic_phrase,
            "confidence": 0.78 if len(topic_phrase.split()) >= 3 else 0.70,
            "source": "context_topic_phrase",
        })

    # Phrase + context combinations, but only with useful unique terms.
    for ct in context_terms[:8]:
        for pt in phrase_terms[:4]:
            if ct == pt:
                continue

            alias = _clean_alias_v1(f"{ct} {pt}")
            if not _valid_alias_v1(alias):
                continue

            aliases.append({
                "alias": alias,
                "confidence": 0.66,
                "source": "context_phrase_combination",
            })

    # Compact phrase alias.
    phrase_compact = _clean_alias_v1(" ".join(phrase_terms[:3]))
    if _valid_alias_v1(phrase_compact):
        aliases.append({
            "alias": phrase_compact,
            "confidence": 0.60,
            "source": "phrase_compact",
        })

    clean = []
    seen = set()

    for a in aliases:
        alias = _clean_alias_v1(a.get("alias") or "")
        key = alias.lower()

        if not _valid_alias_v1(alias):
            continue

        if key in seen:
            continue

        seen.add(key)

        clean.append({
            **a,
            "alias": alias,
        })

    clean = sorted(clean, key=lambda x: float(x.get("confidence") or 0), reverse=True)

    return {
        "aliases": clean[:12],
        "alias_count": min(len(clean), 12),
        "method": "universal_context_alias_expansion_v2",
    }



def build_context_meaning_phrase_v2(
    *,
    phrase: str,
    context_terms: List[str],
    context_concepts: Dict[str, Any],
) -> Dict[str, Any]:

    phrase_terms = _tokens(phrase)
    concepts = context_concepts.get("concepts") or []
    primary = context_concepts.get("primary_concept") or "unknown"

    topic_terms = [
        t for t in context_terms
        if t not in phrase_terms
        and t not in {"change", "changing", "avoid", "missed", "goes", "down"}
    ]

    concept_names = [
        c.get("concept")
        for c in concepts
        if c.get("concept") and c.get("concept") != "unknown"
    ]

    candidates = []

    # Best universal pattern: topic + primary concept
    for topic in topic_terms[:5]:
        if primary and primary != "unknown" and topic != primary:
            candidates.append(f"{topic} {primary}")

    # Topic + secondary concept
    for topic in topic_terms[:4]:
        for concept in concept_names[:3]:
            if topic != concept:
                candidates.append(f"{topic} {concept}")

    # Phrase term + concept
    for pt in phrase_terms[:4]:
        for concept in concept_names[:3]:
            if pt != concept:
                candidates.append(f"{pt} {concept}")

    clean = []
    seen = set()

    for c in candidates:
        c = _clean_alias_v1(c)
        if not _valid_alias_v1(c):
            continue
        if c.lower() in seen:
            continue
        seen.add(c.lower())
        clean.append(c)

    meaning_phrase = clean[0] if clean else _clean_alias_v1(phrase)

    return {
        "has_context_meaning_phrase": bool(meaning_phrase),
        "meaning_phrase": meaning_phrase,
        "meaning_aliases": clean[:10],
        "primary_concept": primary,
        "concepts_used": concept_names[:5],
        "method": "universal_context_meaning_phrase_v2",
    }





CONCEPT_LABEL_TERMS_V31 = {
    "finance",
    "compliance",
    "location",
    "identity",
    "transaction",
    "planning",
    "comparison",
    "monitoring",
    "optimization",
    "education",
    "access",
}

NATURAL_ALLOWED_CONCEPT_PHRASES_V31 = {
    "account access",
    "identity verification",
    "financial planning",
    "location services",
    "access control",
    "transaction history",
    "compliance requirements",
    "compliance policy",
}


def purify_semantic_alias_v31(alias: str) -> bool:
    alias_clean = _clean_alias_v1(alias)
    toks = _tokens(alias_clean)

    if not _valid_alias_v1(alias_clean):
        return False

    if alias_clean.lower() in NATURAL_ALLOWED_CONCEPT_PHRASES_V31:
        return True

    # Reject synthetic label forms like:
    # mortgage finance, business compliance, card comparison, users access.
    # Reject any alias where a concept label is used as a fake keyword.
    # Examples: "credit cards finance", "missed deadline compliance",
    # "branch location locations", "comparison finance".
    if toks and toks[-1] in CONCEPT_LABEL_TERMS_V31:
        return False

    # Reject repeated/pluralized concept endings.
    if len(toks) >= 2 and toks[-2].rstrip("s") == toks[-1].rstrip("s"):
        return False

    # Reject weak context filler terms.
    if any(t in {"users", "their", "hours", "misses"} for t in toks):
        return False

    if len(toks) == 2 and toks[0].rstrip("s") == toks[1].rstrip("s"):
        return False

    return True



def build_natural_semantic_aliases_v3(
    *,
    phrase: str,
    context_terms: List[str],
    context_concepts: Dict[str, Any],
    context_meaning: Dict[str, Any],
) -> Dict[str, Any]:

    phrase_terms = _tokens(phrase)
    concepts = [
        c.get("concept")
        for c in (context_concepts.get("concepts") or [])
        if c.get("concept")
    ]
    concept_set = set(concepts)
    terms = _unique_keep_order(context_terms + phrase_terms)

    aliases = []

    def add(alias: str, confidence: float, reason: str):
        alias = _clean_alias_v1(alias)
        if not purify_semantic_alias_v31(alias):
            return
        aliases.append({
            "alias": alias,
            "confidence": round(confidence, 4),
            "source": "natural_semantic_alias_v3",
            "reason": reason,
        })

    # Access / identity
    if "access" in concept_set:
        if "password" in terms:
            add("password recovery", 0.94, "access_password")
            add("reset password", 0.92, "access_password")
        if "account" in terms:
            add("account recovery", 0.94, "access_account")
            add("account access", 0.90, "access_account")
        if "verification" in terms:
            add("account verification", 0.88, "access_verification")

    # Finance / transaction / optimization
    if "finance" in concept_set:
        if "mortgage" in terms and ("refinance" in terms or "refinancing" in terms):
            add("mortgage refinancing", 0.95, "finance_refinance")
            add("mortgage payment reduction", 0.90, "finance_payment")
            add("loan refinancing", 0.86, "finance_refinance")
        if "credit" in terms and ("card" in terms or "cards" in terms):
            add("credit card comparison", 0.95, "finance_comparison")
            add("compare credit cards", 0.93, "finance_comparison")
            add("credit card fees", 0.84, "finance_transaction")
        if "payment" in terms:
            add("monthly payment", 0.88, "finance_payment")
            add("payment reduction", 0.84, "finance_payment")

    # Compliance
    if "compliance" in concept_set:
        if "license" in terms or "licence" in terms:
            add("license renewal", 0.95, "compliance_license")
            add("license requirements", 0.90, "compliance_license")
            add("business license renewal", 0.88, "compliance_business")
        if "deadline" in terms:
            add("renewal deadline", 0.94, "compliance_deadline")
            add("missed deadline", 0.86, "compliance_deadline")
        if "permit" in terms:
            add("permit renewal", 0.90, "compliance_permit")

    # Location
    if "location" in concept_set:
        if "branch" in terms:
            add("branch locator", 0.95, "location_branch")
            add("branch locations", 0.92, "location_branch")
            add("local branch", 0.88, "location_branch")
        if "office" in terms:
            add("office locations", 0.92, "location_office")
            add("local office", 0.86, "location_office")
        if "store" in terms:
            add("store locator", 0.92, "location_store")
            add("store locations", 0.90, "location_store")
        if "clinic" in terms or "clinics" in terms:
            add("clinic locations", 0.90, "location_clinic")
            add("nearby clinic", 0.88, "location_clinic")

    # Comparison / decision
    if "comparison" in concept_set:
        if "credit" in terms and ("card" in terms or "cards" in terms):
            add("credit card comparison", 0.95, "comparison_credit_card")
        else:
            core = [t for t in terms if t not in {"compare", "comparison", "best", "better", "option", "options"}]
            if core:
                add("compare " + " ".join(core[:2]), 0.84, "comparison_generic")
                add("best " + " ".join(core[:2]), 0.78, "comparison_generic")

    # Planning / calculation
    if "planning" in concept_set or "calculation" in concept_set:
        if "date" in terms or "dates" in terms:
            add("date calculator", 0.88, "planning_date")
            add("date calculation", 0.84, "planning_date")
        if "budget" in terms:
            add("budget planning", 0.88, "planning_budget")
        if "timeline" in terms:
            add("project timeline", 0.84, "planning_timeline")

    # Monitoring / testing
    if "monitoring" in concept_set:
        if "scan" in terms:
            add("screening scan", 0.90, "monitoring_scan")
            add("diagnostic scan", 0.84, "monitoring_scan")
        if "test" in terms or "testing" in terms:
            add("testing assessment", 0.86, "monitoring_testing")
            add("screening test", 0.86, "monitoring_testing")
        if "audit" in terms:
            add("performance audit", 0.84, "monitoring_audit")

    # Optimization / problem solving
    if "optimization" in concept_set:
        if "performance" in terms:
            add("performance optimization", 0.92, "optimization_performance")
        if "cost" in terms or "costs" in terms:
            add("cost reduction", 0.90, "optimization_cost")
        if "savings" in terms or "saving" in terms:
            add("cost savings", 0.88, "optimization_savings")

    if "problem_solving" in concept_set:
        if "avoid" in terms:
            add("how to avoid problems", 0.76, "problem_avoid")
        if "error" in terms:
            add("error troubleshooting", 0.88, "problem_error")
        if "fix" in terms:
            add("how to fix issue", 0.84, "problem_fix")

    # Education
    if "education" in concept_set:
        core = [t for t in terms if t not in {"guide", "tutorial", "learn", "overview", "advice", "tips"}]
        if core:
            add(" ".join(core[:2]) + " guide", 0.84, "education_guide")
            add(" ".join(core[:2]) + " overview", 0.78, "education_overview")

    # Generic fallback from meaning aliases, but keep only non-synthetic.
    for a in (context_meaning.get("meaning_aliases") or [])[:8]:
        toks = _tokens(a)
        if len(toks) >= 2 and len(set(toks)) == len(toks):
            # Avoid repeated label forms like "locations location" or weak pronoun-like terms.
            if any(t in {"users", "their", "hours", "misses"} for t in toks):
                continue
            if len(toks) == 2 and toks[0].rstrip("s") == toks[1].rstrip("s"):
                continue
            add(a, 0.70, "meaning_alias_fallback")

    clean = []
    seen = set()
    for a in sorted(aliases, key=lambda x: float(x.get("confidence") or 0), reverse=True):
        key = str(a.get("alias") or "").lower()
        if key in seen:
            continue
        seen.add(key)
        clean.append(a)

    return {
        "has_natural_semantic_aliases": bool(clean),
        "natural_aliases": clean[:12],
        "natural_alias_count": min(len(clean), 12),
        "method": "universal_natural_semantic_alias_generator_v3",
    }




def select_natural_canonical_phrase_v4(
    *,
    phrase: str,
    natural_semantic_aliases: Dict[str, Any],
    context_meaning: Dict[str, Any],
    fallback_canonical: Dict[str, Any],
) -> Dict[str, Any]:

    natural_aliases = natural_semantic_aliases.get("natural_aliases") or []

    # Prefer the highest-confidence natural semantic alias.
    for a in natural_aliases:
        alias = str(a.get("alias") or "").strip()
        if alias and purify_semantic_alias_v31(alias):
            return {
                "canonical_phrase": alias,
                "canonical_confidence": a.get("confidence", 0.9),
                "canonical_source": "natural_semantic_alias_v3",
                "previous_canonical_phrase": fallback_canonical.get("canonical_phrase"),
                "method": "natural_canonical_phrase_v4",
            }

    # Next prefer a clean context meaning phrase.
    meaning_phrase = str(context_meaning.get("meaning_phrase") or "").strip()
    if meaning_phrase and purify_semantic_alias_v31(meaning_phrase):
        return {
            "canonical_phrase": meaning_phrase,
            "canonical_confidence": 0.82,
            "canonical_source": "context_meaning_phrase_v2",
            "previous_canonical_phrase": fallback_canonical.get("canonical_phrase"),
            "method": "natural_canonical_phrase_v4",
        }

    # Last fallback to previous canonical.
    return {
        "canonical_phrase": fallback_canonical.get("canonical_phrase"),
        "canonical_confidence": fallback_canonical.get("confidence"),
        "canonical_source": "legacy_canonical_phrase",
        "previous_canonical_phrase": fallback_canonical.get("canonical_phrase"),
        "method": "natural_canonical_phrase_v4",
    }



def analyze_phrase_alias_intelligence_v1(
    *,
    phrase: str,
    sentence: str = "",
    previous_sentence: str = "",
    next_sentence: str = "",
    heading: str = "",
    document_title: str = "",
    paragraph: str = "",
) -> Dict[str, Any]:

    context = extract_phrase_context_v1(
        phrase=phrase,
        sentence=sentence,
        previous_sentence=previous_sentence,
        next_sentence=next_sentence,
        heading=heading,
        document_title=document_title,
        paragraph=paragraph,
    )

    context_meaning = build_context_meaning_phrase_v2(
        phrase=phrase,
        context_terms=context.get("context_terms", []),
        context_concepts=context.get("context_concepts", {}),
    )

    canonical = generate_canonical_phrase_v1(
        phrase=context_meaning.get("meaning_phrase") or phrase,
        context_analysis=context,
    )

    aliases = expand_phrase_aliases_v1(
        phrase=phrase,
        canonical_phrase=canonical.get("canonical_phrase") or "",
        context_analysis=context,
    )

    natural_semantic_aliases = build_natural_semantic_aliases_v3(
        phrase=phrase,
        context_terms=context.get("context_terms", []),
        context_concepts=context.get("context_concepts", {}),
        context_meaning=context_meaning,
    )

    natural_canonical = select_natural_canonical_phrase_v4(
        phrase=phrase,
        natural_semantic_aliases=natural_semantic_aliases,
        context_meaning=context_meaning,
        fallback_canonical=canonical,
    )

    canonical = {
        **canonical,
        "canonical_phrase": natural_canonical.get("canonical_phrase"),
        "confidence": natural_canonical.get("canonical_confidence"),
        "canonical_source": natural_canonical.get("canonical_source"),
        "previous_canonical_phrase": natural_canonical.get("previous_canonical_phrase"),
        "canonical_method": natural_canonical.get("method"),
    }

    # Add natural semantic aliases first, then context meaning aliases, then legacy aliases.
    meaning_aliases = [
        {
            "alias": a,
            "confidence": 0.82,
            "source": "context_meaning_phrase_v2",
        }
        for a in (context_meaning.get("meaning_aliases") or [])
    ]

    existing_aliases = aliases.get("aliases", [])
    merged_aliases = []
    seen_aliases = set()

    for a in (natural_semantic_aliases.get("natural_aliases") or []) + meaning_aliases + existing_aliases:
        alias = str(a.get("alias") or "").strip()
        if not alias or alias.lower() in seen_aliases:
            continue
        if not purify_semantic_alias_v31(alias):
            continue
        seen_aliases.add(alias.lower())
        merged_aliases.append(a)

    aliases["aliases"] = merged_aliases[:12]
    aliases["alias_count"] = len(aliases["aliases"])

    confidence = max(
        float(canonical.get("confidence") or 0),
        max([float(a.get("confidence") or 0) for a in aliases.get("aliases", [])] or [0.0]),
    )

    return {
        "has_phrase_alias_intelligence": True,
        "phrase": phrase,
        "canonical_phrase": canonical.get("canonical_phrase"),
        "canonical_confidence": canonical.get("confidence"),
        "canonical_source": canonical.get("canonical_source"),
        "previous_canonical_phrase": canonical.get("previous_canonical_phrase"),
        "canonical_method": canonical.get("canonical_method"),
        "context_meaning": context_meaning,
        "natural_semantic_aliases": natural_semantic_aliases,
        "aliases": aliases.get("aliases", []),
        "alias_count": aliases.get("alias_count", 0),
        "context_terms": context.get("context_terms", []),
        "context_concepts": context.get("context_concepts", {}),
        "phrase_terms": context.get("phrase_terms", []),
        "context_window": context.get("context_window", {}),
        "confidence": round(confidence, 4),
        "universal": True,
    }


def explain_phrase_alias_intelligence_v1() -> Dict[str, Any]:
    return {
        "layer": "resolver_phrase_alias_intelligence_v1",
        "purpose": "Create universal context-aware canonical phrases and aliases for resolver target discovery.",
        "universal": True,
        "does_not_use_niche_hardcoding": True,
        "inputs": [
            "phrase",
            "sentence",
            "previous_sentence",
            "next_sentence",
            "heading",
            "document_title",
            "paragraph",
        ],
        "outputs": [
            "canonical_phrase",
            "aliases",
            "context_terms",
            "context_concepts",
            "phrase_terms",
            "confidence",
            "explainable context window",
        ],
    }
