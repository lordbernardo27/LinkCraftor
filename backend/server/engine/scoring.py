from __future__ import annotations
from typing import Any, Dict, List, Optional
from backend.server.stores.logical_inference_intelligence import analyze_logical_inference_v1
from backend.server.stores.analogical_reasoning_intelligence import analyze_analogical_reasoning_v1
from backend.server.stores.anchor_purpose_intelligence import analyze_anchor_purpose_v1
import math
import re

from backend.server.engine.profiles import get_profile


# -------------------------------------------------------------
# 1) Weight tables & thresholds (base defaults / fallbacks)
# -------------------------------------------------------------

ENTITY_TYPE_WEIGHT: Dict[str, float] = {
    "DRUG": 3.0,
    "DISEASE": 2.5,
    "CONDITION": 2.5,
    "SYMPTOM": 2.0,
    "MECHANISM": 1.5,
    "TOPIC": 1.0,
}

ENTITY_RELATION_WEIGHTS: Dict[str, float] = {
    "EXACT_ID": 1.0,
    "ALIAS": 0.85,
    "CATEGORY": 0.75,
    "PARENT_CHILD": 0.75,
    "SIBLING_CLASS": 0.55,
}

# These remain as base fallbacks for now.
CONTEXT_TOPIC_COMPAT: Dict[str, Dict[str, float]] = {
    "SIDE_EFFECTS": {
        "SIDE_EFFECTS": 1.0,
        "MECHANISM": 0.8,
        "TREATMENT": 0.8,
        "OVERVIEW": 0.5,
        "GENERAL": 0.2,
    },
    "OVERVIEW": {"OVERVIEW": 1.0, "GENERAL": 0.7},
    "TREATMENT": {"TREATMENT": 1.0, "SIDE_EFFECTS": 0.7, "OVERVIEW": 0.5},
    "PREGNANCY": {
        "PREGNANCY": 1.0,
        "SAFETY": 0.9,
        "SIDE_EFFECTS": 0.7,
        "OVERVIEW": 0.4,
    },
}

SECTION_TOPIC_COMPAT: Dict[str, Dict[str, float]] = {
    "INTRO": {"OVERVIEW": 1.0, "GENERAL": 0.8, "PILLAR": 0.9},
    "BODY": {"SIDE_EFFECTS": 0.9, "TREATMENT": 0.9, "DETAIL": 1.0},
    "FAQ": {"FAQ": 1.0, "GENERAL": 0.6},
    "CONCLUSION": {"OVERVIEW": 0.8, "PILLAR": 0.9},
}

INTENT_TOPIC_COMPAT: Dict[str, Dict[str, float]] = {
    "WARNING": {"SIDE_EFFECTS": 1.0, "SAFETY": 1.0, "PREGNANCY": 0.9},
    "RECOMMENDATION": {"TREATMENT": 1.0, "PILLAR": 0.8},
    "COMPARISON": {"COMPARISON": 1.0, "ALTERNATIVES": 0.9},
    "ACTIONABLE": {"CHECKLIST": 1.0, "HOW_TO": 0.9},
}

INTERNAL_SOURCE_BASE: Dict[str, float] = {
    "sitemap": 1.0,
    "backup": 0.9,
    "uploaded": 0.8,
    "draft": 0.6,
}

EXTERNAL_DOMAIN_AUTHORITY: Dict[str, float] = {
    "nhs.uk": 1.0,
    "nih.gov": 1.0,
    "who.int": 1.0,
    "mayoclinic.org": 0.9,
    "healthline.com": 0.8,
}

WEIGHTS_INTERNAL = {"lexical": 0.25, "entity": 0.30, "graph": 0.20, "context": 0.15, "source": 0.10}
WEIGHTS_SEMANTIC = {"lexical": 0.15, "entity": 0.30, "graph": 0.30, "context": 0.15, "source": 0.10}
WEIGHTS_EXTERNAL = {"lexical": 0.25, "entity": 0.30, "graph": 0.15, "context": 0.10, "source": 0.20}


# -------------------------------------------------------------
# 2) Generic helpers
# -------------------------------------------------------------

_non_alnum = re.compile(r"[^a-z0-9\s]+", re.IGNORECASE)


def safe_norm(s: Any) -> str:
    return re.sub(r"\s+", " ", str(s or "").lower().strip())


def tokenize(s: Any) -> List[str]:
    t = _non_alnum.sub(" ", str(s or "").lower())
    return [x for x in t.split() if x]


def as_list(v: Any) -> List[Any]:
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]


def intersect_count(a: List[Any], b: List[Any]) -> int:
    if not a or not b:
        return 0
    set_b = set(b)
    return sum(1 for x in a if x in set_b)


def _feedback_key_for_phrase_candidate(phrase_text: str, cand: Dict[str, Any]) -> Optional[str]:
    pnorm = safe_norm(phrase_text)
    if not pnorm:
        return None
    tkey = cand.get("id") or cand.get("topicId") or cand.get("url") or cand.get("title")
    if not tkey:
        return None
    return f"{pnorm}||{str(tkey).strip()}"


def compute_feedback_delta(accepts: int, rejects: int) -> float:
    total = int(accepts) + int(rejects)
    if total <= 0:
        return 0.0
    ratio = (int(accepts) - int(rejects)) / float(total)
    max_delta = 0.18
    return float(ratio) * max_delta


def _resolve_profile(profile: Optional[Dict[str, Any] | str]) -> Dict[str, Any]:
    """
    Accept either:
    - None -> default to medical (to preserve current scoring behavior)
    - string profile id, e.g. 'medical', 'saas'
    - a profile dict returned by get_profile(...)
    """
    if profile is None:
     return get_profile("general")
    if isinstance(profile, str):
        return get_profile(profile)
    return dict(profile)


# -------------------------------------------------------------
# 3) Individual signal computations
# -------------------------------------------------------------

def lexical_score(phrase_text: str, candidate_title: str) -> float:
    p_tokens = tokenize(phrase_text)
    t_tokens = tokenize(candidate_title)
    if not p_tokens or not t_tokens:
        return 0.0

    p_set = set(p_tokens)
    t_set = set(t_tokens)

    overlap = sum(1 for tok in p_set if tok in t_set)
    union_size = len(p_set) + len(t_set) - overlap
    jaccard = (overlap / union_size) if union_size else 0.0

    title_str = " ".join(t_tokens)
    phrase_str = " ".join(p_tokens)

    contains_phrase = 1.0 if phrase_str and phrase_str in title_str else 0.0
    prefix_match = 1.0 if p_tokens and title_str.startswith(p_tokens[0]) else 0.0

    score = 0.4 * jaccard + 0.3 * contains_phrase + 0.3 * prefix_match
    return max(0.0, min(1.0, score))


def entity_score(
    phrase_entities: List[Dict[str, Any]],
    candidate_entities: List[Dict[str, Any]],
    profile: Optional[Dict[str, Any]] = None,
) -> float:
    if not phrase_entities or not candidate_entities:
        return 0.0

    profile = _resolve_profile(profile)
    entity_importance = profile.get("entity_importance") or ENTITY_TYPE_WEIGHT

    max_possible = 0.0
    actual = 0.0

    for pe in phrase_entities:
        if not pe:
            continue
        p_type = pe.get("type")
        type_weight = float(entity_importance.get(p_type, 1.0))
        max_possible += type_weight

        p_id = pe.get("id")
        p_ali = as_list(pe.get("aliases") or (pe.get("meta") or {}).get("aliases"))
        p_cats = as_list(pe.get("categories") or (pe.get("meta") or {}).get("categories"))
        p_par = as_list(pe.get("parents") or (pe.get("meta") or {}).get("parents"))
        p_chi = as_list(pe.get("children") or (pe.get("meta") or {}).get("children"))

        best_local = 0.0

        for ce in candidate_entities:
            if not ce:
                continue
            c_id = ce.get("id")
            c_ali = as_list(ce.get("aliases") or (ce.get("meta") or {}).get("aliases"))
            c_cats = as_list(ce.get("categories") or (ce.get("meta") or {}).get("categories"))
            c_par = as_list(ce.get("parents") or (ce.get("meta") or {}).get("parents"))
            c_chi = as_list(ce.get("children") or (ce.get("meta") or {}).get("children"))

            rel_weight = 0.0

            if p_id and c_id and p_id == c_id:
                rel_weight = ENTITY_RELATION_WEIGHTS["EXACT_ID"]
            else:
                p_ali_n = [safe_norm(x) for x in p_ali]
                c_ali_n = [safe_norm(x) for x in c_ali]
                alias_overlap = (
                    intersect_count(p_ali_n, [safe_norm(c_id), *c_ali_n])
                    or intersect_count(c_ali_n, [safe_norm(p_id), *p_ali_n])
                )
                if alias_overlap > 0:
                    rel_weight = max(rel_weight, ENTITY_RELATION_WEIGHTS["ALIAS"])

                if intersect_count(p_cats, c_cats) > 0:
                    rel_weight = max(rel_weight, ENTITY_RELATION_WEIGHTS["CATEGORY"])

                shared_parent = (
                    intersect_count(p_par, c_par)
                    or intersect_count(p_par, c_chi)
                    or intersect_count(p_chi, c_par)
                )
                if shared_parent > 0:
                    rel_weight = max(rel_weight, ENTITY_RELATION_WEIGHTS["PARENT_CHILD"])

                sib_parents = any(x in set(c_par) for x in set(p_par))
                if sib_parents and rel_weight == 0.0:
                    rel_weight = max(rel_weight, ENTITY_RELATION_WEIGHTS["SIBLING_CLASS"])

            best_local = max(best_local, rel_weight)

        if best_local > 0.0:
            actual += type_weight * best_local

    if not max_possible:
        return 0.0
    return min(1.0, actual / max_possible)


def _is_clean_graph_target_id(target_id: Any) -> bool:
    """
    Prevent noisy graph fragment nodes from influencing semantic scoring.
    Safe scoring-time filter only. Does not delete graph data.
    """
    tid = str(target_id or "").strip().lower()

    if not tid:
        return False

    if tid.startswith("ent:"):
        return True

    if not tid.startswith("phrase:"):
        return False

    phrase = tid.replace("phrase:", "", 1).strip()
    tokens = re.findall(r"[a-z0-9]+", phrase)

    if len(tokens) < 2 or len(tokens) > 6:
        return False

    weak_starts = {
        "can", "will", "would", "could", "should", "may", "might",
        "is", "are", "was", "were", "be", "being", "been",
        "the", "this", "that", "these", "those",
        "and", "or", "but", "so",
    }

    weak_ends = {
        "can", "will", "would", "could", "should", "may", "might",
        "is", "are", "was", "were", "be", "being", "been",
        "to", "of", "in", "on", "for", "with", "by",
        "due", "because", "while", "when",
    }

    if tokens[0] in weak_starts:
        return False

    if tokens[-1] in weak_ends:
        return False

    weak_verbs = {
        "affects", "refine", "make", "take", "get", "go", "come",
        "seem", "become", "appear", "show", "shows",
    }

    if len(tokens) <= 3 and any(t in weak_verbs for t in tokens):
        return False

    return True


def _clean_graph_relations(relations: Any) -> List[Dict[str, Any]]:
    if not isinstance(relations, list):
        return []

    clean: List[Dict[str, Any]] = []

    for r in relations:
        if not isinstance(r, dict):
            continue

        if not _is_clean_graph_target_id(r.get("targetId")):
            continue

        clean.append(r)

    return clean


def graph_score(
    phrase_ctx: Dict[str, Any],
    candidate: Dict[str, Any],
    profile: Optional[Dict[str, Any]] = None,
) -> float:
    phrase_vec = phrase_ctx.get("graphVector")
    cand_vec = candidate.get("graphVector")

    base = 0.0
    if isinstance(phrase_vec, list) and isinstance(cand_vec, list) and phrase_vec and cand_vec:
        dot = 0.0
        na = 0.0
        nb = 0.0
        for i in range(min(len(phrase_vec), len(cand_vec))):
            a = float(phrase_vec[i] or 0.0)
            b = float(cand_vec[i] or 0.0)
            dot += a * b
            na += a * a
            nb += b * b
        if na and nb:
            base = dot / (math.sqrt(na) * math.sqrt(nb))
            base = max(0.0, min(1.0, base))
    else:
        base = entity_score(
            phrase_ctx.get("entities") or [],
            candidate.get("entities") or [],
            profile=profile,
        ) * 0.7

        p_rel = _clean_graph_relations(phrase_ctx.get("graphRelations"))
    c_rel = _clean_graph_relations(candidate.get("graphRelations"))

    rel_boost = 0.0

    if p_rel and c_rel:
        def key_of(r: Dict[str, Any]) -> str:
            return f"{r.get('type') or 'GEN'}::{r.get('targetId') or ''}"

        p_map: Dict[str, float] = {}
        for r in p_rel:
            tid = (r or {}).get("targetId")
            if not tid:
                continue
            p_map[key_of(r)] = float((r or {}).get("weight", 1.0))

        hits = 0
        total_weight = 0.0
        for r in c_rel:
            tid = (r or {}).get("targetId")
            if not tid:
                continue
            k = key_of(r)
            if k in p_map:
                hits += 1
                total_weight += (p_map[k] + float((r or {}).get("weight", 1.0))) / 2.0

        if hits:
            avg = total_weight / hits
            rel_boost = min(0.2, avg * 0.2 + hits * 0.02)

    final = base + rel_boost
    return max(0.0, min(1.0, final))


def context_score(
    phrase_ctx: Dict[str, Any],
    candidate: Dict[str, Any],
    profile: Optional[Dict[str, Any]] = None,
) -> float:
    profile = _resolve_profile(profile)

    ctx_type = phrase_ctx.get("contextType")
    section_type = phrase_ctx.get("sectionType")
    intent = phrase_ctx.get("intent")
    discourse = phrase_ctx.get("discourseRole")

    topic_types = candidate.get("topicTypes") or []
    section_roles = candidate.get("sectionRoles") or []
    intent_tags = candidate.get("intentTags") or []
    discourse_tags = candidate.get("discourseTags") or []

    if not (topic_types or section_roles or intent_tags or discourse_tags):
        return 0.0

    ctx_s = 0.0
    profile_context_rules = profile.get("context_rules") or {}
    if ctx_type and ctx_type in profile_context_rules and topic_types:
        allowed_types = profile_context_rules.get(ctx_type) or []
        ctx_s = 1.0 if any(t in allowed_types for t in topic_types) else 0.0
    elif ctx_type and ctx_type in CONTEXT_TOPIC_COMPAT and topic_types:
        row = CONTEXT_TOPIC_COMPAT[ctx_type]
        ctx_s = max((row.get(t, 0.0) for t in topic_types), default=0.0)

    sec_s = 0.0
    if section_type and section_type in SECTION_TOPIC_COMPAT:
        row = SECTION_TOPIC_COMPAT[section_type]
        pool = list(topic_types) + list(section_roles)
        sec_s = max((row.get(t, 0.0) for t in pool), default=0.0)

    intent_s = 0.0
    if intent and intent in INTENT_TOPIC_COMPAT:
        row = INTENT_TOPIC_COMPAT[intent]
        pool = list(topic_types) + list(intent_tags)
        intent_s = max((row.get(t, 0.0) for t in pool), default=0.0)

    disc_s = 0.0
    if discourse and discourse_tags:
        nd = safe_norm(discourse)
        disc_s = 1.0 if any(safe_norm(d) == nd for d in discourse_tags) else 0.0

    combined = 0.45 * ctx_s + 0.30 * sec_s + 0.20 * intent_s + 0.05 * disc_s
    return min(1.0, combined)


def internal_source_score(candidate: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> float:
    profile = _resolve_profile(profile)
    internal_priority = profile.get("internal_priority") or INTERNAL_SOURCE_BASE

    # Backward compatible source detection:
    # old candidates may use sourceType; imported v2 uses source_type.
    st = candidate.get("sourceType") or candidate.get("source_type")
    base = float(internal_priority.get(st, 0.6))

    # Imported Target Pool v2 awareness.
    if st == "imported":
        base = max(base, 0.72)

    topic_types = candidate.get("topicTypes") or []
    section_roles = candidate.get("sectionRoles") or []
    entities = candidate.get("entities") or []

    role = (
        ("PILLAR" in topic_types)
        or ("PILLAR" in section_roles)
        or any((e or {}).get("meta", {}).get("role") == "PILLAR" for e in entities)
    )
    canonical_boost = 0.1 if candidate.get("isCanonicalTopic") or role else 0.0

    metadata = candidate.get("metadata") if isinstance(candidate.get("metadata"), dict) else {}

    priority_bucket = str(candidate.get("priority_bucket") or metadata.get("priority_bucket") or "").lower()
    page_type_hint = str(candidate.get("page_type_hint") or metadata.get("page_type_hint") or "").lower()
    import_source = str(candidate.get("import_source") or metadata.get("import_source") or "").lower()
    path = str(candidate.get("path") or metadata.get("path") or "")

    priority_boosts = {
        "core": 0.12,
        "high": 0.09,
        "standard": 0.04,
        "supporting": 0.02,
    }

    page_type_boosts = {
        "homepage": 0.10,
        "category": 0.08,
        "service": 0.08,
        "product": 0.06,
        "article": 0.04,
        "page": 0.02,
    }

    import_source_boosts = {
        "csv": 0.03,
        "txt": 0.02,
        "xml": 0.02,
    }

    priority_boost = priority_boosts.get(priority_bucket, 0.0)
    page_type_boost = page_type_boosts.get(page_type_hint, 0.0)
    import_source_boost = import_source_boosts.get(import_source, 0.0)

    # Prefer cleaner/shallower internal paths slightly.
    clean_path = path.strip("/")
    path_depth = len([x for x in clean_path.split("/") if x]) if clean_path else 0
    path_boost = 0.03 if path_depth <= 2 else 0.01 if path_depth <= 4 else 0.0

    score = (
        base
        + canonical_boost
        + priority_boost
        + page_type_boost
        + import_source_boost
        + path_boost
    )

    return max(0.0, min(1.0, score))


def external_source_score(candidate: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> float:
    profile = _resolve_profile(profile)
    external_trust = profile.get("external_trust") or EXTERNAL_DOMAIN_AUTHORITY

    host = str(candidate.get("domain") or "").lower()
    base = external_trust.get(host, 0.5)
    return float(base)


# -------------------------------------------------------------
# 4) Mode-specific combination
# -------------------------------------------------------------

def compute_internal_score(
    phrase_ctx: Dict[str, Any],
    candidate: Dict[str, Any],
    s: Dict[str, float],
    profile: Optional[Dict[str, Any]] = None,
) -> float:
    lexical, entity, graph, context, source = s["lexical"], s["entity"], s["graph"], s["context"], s["source"]
    has_entities = bool((phrase_ctx.get("entities") or []) and (candidate.get("entities") or []))
    has_graph = bool(phrase_ctx.get("graphVector") and candidate.get("graphVector"))

    if has_entities and entity < 0.25:
        return 0.0
    if has_graph and graph < 0.30:
        return 0.0
    if (has_entities or has_graph) and (entity + graph) < 0.40 and lexical < 0.60:
        return 0.0

    score = (
        WEIGHTS_INTERNAL["lexical"] * lexical +
        WEIGHTS_INTERNAL["entity"] * entity +
        WEIGHTS_INTERNAL["graph"] * graph +
        WEIGHTS_INTERNAL["context"] * context +
        WEIGHTS_INTERNAL["source"] * source
    )
    return max(0.0, min(1.0, score))


def classify_internal_tier(score: float, profile: Optional[Dict[str, Any]] = None) -> Optional[str]:
    profile = _resolve_profile(profile)
    threshold = profile.get("thresholds") or {}

    low = float(threshold.get("internal_min", 0.35))
    mid = 0.55
    high = 0.75

    if score >= high:
        return "high"
    if score >= mid:
        return "mid"
    if score >= low:
        return "low"
    return None

def synonym_alias_boost(
    phrase_a: Any,
    phrase_b: Any,
) -> float:
    """
    Controlled synonym/alias boost.
    Safe: only handles known universal synonym families.
    """
    a = safe_norm(str(phrase_a or ""))
    b = safe_norm(str(phrase_b or ""))

    if not a or not b:
        return 0.0

    synonym_groups = [
        {"high blood pressure", "hypertension", "elevated blood pressure"},
        {"heart attack", "myocardial infarction"},
        {"liver damage", "hepatotoxicity"},
        {"blood sugar", "glucose", "blood glucose"},
        {"scaling problems", "scalability issues", "system scalability", "system scalability issues", "difficult to scale"},
        {"website ranking", "google ranking", "search ranking", "rank on google"},
        {"cash flow problems", "negative cash flow", "cash flow issues"},
    ]

    for group in synonym_groups:
        if a in group and b in group:
            return 0.95

    return 0.0

def ontology_categories_for_phrase(
    phrase: Any,
) -> List[str]:
    """
    Assign broad ontology categories to a phrase.
    Safe: category tagging only. Does not create phrases or links.
    """
    p = safe_norm(str(phrase or ""))
    toks = set(tokenize(p))

    categories: List[str] = []

    ontology_rules = {
        "medical_condition": {
            "hypertension", "pressure", "diabetes", "disease", "condition",
            "osteoporosis", "fractures", "pain", "deficiency",
        },
        "medication_topic": {
            "amlodipine", "medication", "medications", "drug", "drugs",
            "dose", "dosage", "therapy", "treatment",
        },
        "business_finance": {
            "cash", "flow", "revenue", "profit", "profits", "sales",
            "expenses", "costs", "capital", "financial", "finance",
            "budget", "forecast", "forecasts",
        },
        "legal_compliance": {
            "legal", "law", "laws", "regulation", "regulations",
            "compliance", "copyright", "trademark", "trademarks",
            "contract", "contracts", "liability",
        },
        "seo_search": {
            "seo", "ranking", "rank", "google", "search", "traffic",
            "articles", "content", "keywords", "website", "websites",
        },
        "technology_scaling": {
            "system", "systems", "technology", "scaling", "scale",
            "scalability", "infrastructure", "performance", "latency",
            "architecture",
        },
        "ecommerce_operations": {
            "ecommerce", "stores", "store", "inventory", "checkout",
            "conversion", "cart", "customers", "orders", "products",
        },
    }

    for category, terms in ontology_rules.items():
        if toks & terms:
            categories.append(category)

    return categories


def ontology_alignment_score(
    phrase_a: Any,
    phrase_b: Any,
) -> float:
    """
    Score whether two phrases belong to the same ontology/topic category.
    """
    cats_a = set(ontology_categories_for_phrase(phrase_a))
    cats_b = set(ontology_categories_for_phrase(phrase_b))

    if not cats_a or not cats_b:
        return 0.0

    overlap = cats_a & cats_b

    if not overlap:
        return 0.0

    return min(1.0, len(overlap) / max(len(cats_a | cats_b), 1))


def semantic_similarity_score(
    phrase_a: Any,
    phrase_b: Any,
) -> float:
    """
    Safe lexical-semantic similarity.
    Does not use external AI and does not create new phrases.
    """
    a = safe_norm(str(phrase_a or ""))
    b = safe_norm(str(phrase_b or ""))

    if not a or not b:
        return 0.0

    if a == b:
        return 1.0

    alias_boost = synonym_alias_boost(a, b)
    if alias_boost:
        return alias_boost

    a_tokens = set(tokenize(a))
    b_tokens = set(tokenize(b))

    if not a_tokens or not b_tokens:
        return 0.0

    overlap = len(a_tokens & b_tokens)
    union = len(a_tokens | b_tokens)

    jaccard = overlap / max(union, 1)

    containment = 0.0
    if a in b or b in a:
        shorter = min(len(a_tokens), len(b_tokens))
        longer = max(len(a_tokens), len(b_tokens))
        containment = shorter / max(longer, 1)

    root_overlap = 0.0
    if overlap >= 2:
        root_overlap = min(
            1.0,
            overlap / max(min(len(a_tokens), len(b_tokens)), 1),
        )

    score = max(
        jaccard,
        containment,
        root_overlap * 0.85,
    )

    return max(0.0, min(1.0, round(score, 4)))

def compute_semantic_score(
    phrase_ctx: Dict[str, Any],
    candidate: Dict[str, Any],
    s: Dict[str, float],
    profile: Optional[Dict[str, Any]] = None,
) -> float:
    lexical, entity, graph, context, source = s["lexical"], s["entity"], s["graph"], s["context"], s["source"]

    semantic_similarity = semantic_similarity_score(
        phrase_ctx.get("phrase"),
        candidate.get("phrase"),
    )

    ontology_alignment = ontology_alignment_score(
        phrase_ctx.get("phrase"),
        candidate.get("phrase"),
    )

    semantic_intelligence = (
        semantic_similarity >= 0.70
        and ontology_alignment >= 0.50
    )

    if (
        entity == 0.0
        and graph == 0.0
        and context == 0.0
        and lexical < 0.20
        and not semantic_intelligence
    ):
        return 0.0

    has_entity_graph = (entity + graph) >= 0.15
    has_lexical = lexical >= 0.30

    if not has_entity_graph and not has_lexical and not semantic_intelligence:
        return 0.0


    ontology_alignment = ontology_alignment_score(
        phrase_ctx.get("phrase"),
        candidate.get("phrase"),
    )

    semantic_bonus = (
        semantic_similarity * 0.12 +
        ontology_alignment * 0.08
    )

    score = (
        WEIGHTS_SEMANTIC["lexical"] * lexical +
        WEIGHTS_SEMANTIC["entity"] * entity +
        WEIGHTS_SEMANTIC["graph"] * graph +
        WEIGHTS_SEMANTIC["context"] * context +
        WEIGHTS_SEMANTIC["source"] * source
    )

    score += semantic_bonus

    if entity >= 0.70 and lexical >= 0.80:
        score *= 0.4

    return max(0.0, min(1.0, score))


def classify_semantic_tier(score: float, profile: Optional[Dict[str, Any]] = None) -> Optional[str]:
    profile = _resolve_profile(profile)
    threshold = profile.get("thresholds") or {}

    low = float(threshold.get("semantic_min", 0.12))
    mid = 0.22
    high = 0.40

    if score >= high:
        return "high"
    if score >= mid:
        return "mid"
    if score >= low:
        return "low"
    return None


def compute_external_score(
    phrase_ctx: Dict[str, Any],
    candidate: Dict[str, Any],
    s: Dict[str, float],
    profile: Optional[Dict[str, Any]] = None,
) -> float:
    profile = _resolve_profile(profile)
    threshold = profile.get("thresholds") or {}

    lexical, entity, graph, context, source = s["lexical"], s["entity"], s["graph"], s["context"], s["source"]

    external_min = float(threshold.get("external_min", 0.55))

    if source < external_min:
        return 0.0
    if entity < 0.30:
        return 0.0

    score = (
        WEIGHTS_EXTERNAL["lexical"] * lexical +
        WEIGHTS_EXTERNAL["entity"] * entity +
        WEIGHTS_EXTERNAL["graph"] * graph +
        WEIGHTS_EXTERNAL["context"] * context +
        WEIGHTS_EXTERNAL["source"] * source
    )
    return max(0.0, min(1.0, score))


def classify_external_tier(score: float, profile: Optional[Dict[str, Any]] = None) -> Optional[str]:
    profile = _resolve_profile(profile)
    threshold = profile.get("thresholds") or {}

    mid = float(threshold.get("external_min", 0.55))
    high = 0.75

    if score >= high:
        return "high"
    if score >= mid:
        return "mid"
    return None


def candidate_is_strong_internal(candidate: Dict[str, Any], internal_score: float, semantic_score: float) -> bool:
    """
    Balanced internal-vs-semantic separation.

    Internal should win only when it is clearly/directly stronger.
    Semantic should survive when it carries meaningful optional relevance.

    Fixes:
    1. Better internal-vs-semantic separation
    2. Semantic preservation
    3. Reduced canonical override aggression
    4. Dedicated semantic retention threshold
    """

    is_canonical = bool(candidate.get("isCanonicalTopic"))

    # Dedicated semantic preservation threshold.
    semantic_preserve = semantic_score >= 0.40

    # Internal must be truly strong before it can override semantic.
    strong_internal = internal_score >= 0.82

    # Internal must beat semantic by a real margin, not just be "close".
    clear_internal_margin = (internal_score - semantic_score) >= 0.14

    # Canonical pages get a small advantage, but no longer swallow semantic matches.
    canonical_direct_match = (
        is_canonical
        and internal_score >= 0.86
        and (internal_score - semantic_score) >= 0.10
    )

    # If semantic is strong enough and internal is not clearly better, preserve yellow.
    if semantic_preserve and not clear_internal_margin and not canonical_direct_match:
        return False

    if strong_internal and clear_internal_margin:
        return True

    if canonical_direct_match:
        return True

    return False

# -------------------------------------------------------------
# 5) Main API (pure function)
# -------------------------------------------------------------



def score_candidates_for_phrase(
    phrase_ctx: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    feedback_map: Optional[Dict[str, Dict[str, Any]]] = None,
    profile: Optional[Dict[str, Any] | str] = None,
    debug: bool = False,
    imported_di_signal: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    profile can be:
    - None -> defaults to medical
    - "medical", "saas", "general"
    - a profile dict from get_profile(...)
    """
    resolved_profile = _resolve_profile(profile)
    results: List[Dict[str, Any]] = []

    if not phrase_ctx or not candidates:
        return results

    for cand in candidates:
        lexical = lexical_score(phrase_ctx.get("phraseText", ""), cand.get("title", ""))
        entity = entity_score(
            phrase_ctx.get("entities") or [],
            cand.get("entities") or [],
            profile=resolved_profile,
        )
        graph = graph_score(phrase_ctx, cand, profile=resolved_profile)
        context = context_score(phrase_ctx, cand, profile=resolved_profile)
        source = (
            external_source_score(cand, profile=resolved_profile)
            if cand.get("isExternal")
            else internal_source_score(cand, profile=resolved_profile)
        )

        signals = {
            "lexical": lexical,
            "entity": entity,
            "graph": graph,
            "context": context,
            "source": source,
        }

        best_kind = None
        best_score = 0.0
        tier = None
        debug_mode_scores = {
            "internal": 0.0,
            "semantic": 0.0,
            "external": 0.0,
        }
        debug_mode_tiers = {
            "internal": None,
            "semantic": None,
            "external": None,
        }

        if cand.get("isExternal"):
            s_ext = compute_external_score(phrase_ctx, cand, signals, profile=resolved_profile)
            t_ext = classify_external_tier(s_ext, profile=resolved_profile) if s_ext > 0 else None

            debug_mode_scores["external"] = float(s_ext)
            debug_mode_tiers["external"] = t_ext

            if t_ext:
                best_kind, best_score, tier = "external", s_ext, t_ext
        else:
            s_int = compute_internal_score(phrase_ctx, cand, signals, profile=resolved_profile)
            s_sem = compute_semantic_score(phrase_ctx, cand, signals, profile=resolved_profile)

            t_int = classify_internal_tier(s_int, profile=resolved_profile) if s_int > 0 else None
            t_sem = classify_semantic_tier(s_sem, profile=resolved_profile) if s_sem > 0 else None

            debug_mode_scores["internal"] = float(s_int)
            debug_mode_scores["semantic"] = float(s_sem)
            debug_mode_tiers["internal"] = t_int
            debug_mode_tiers["semantic"] = t_sem

            if t_int and not t_sem:
                best_kind, best_score, tier = "internal", s_int, t_int
            elif (not t_int) and t_sem:
                best_kind, best_score, tier = "semantic", s_sem, t_sem
            elif t_int and t_sem:
                # Balanced strong-vs-optional decision.
                # Keep direct, clearly superior internal matches blue.
                # Preserve meaningful semantic matches as yellow/optional.
                if candidate_is_strong_internal(cand, s_int, s_sem):
                    best_kind, best_score, tier = "internal", s_int, t_int
                else:
                    best_kind, best_score, tier = "semantic", s_sem, t_sem
        if not best_kind or not tier:
            continue

        accepts = 0
        rejects = 0
        delta = 0.0

        if feedback_map:
            fkey = _feedback_key_for_phrase_candidate(phrase_ctx.get("phraseText", ""), cand)
            if fkey and fkey in feedback_map:
                rec = feedback_map[fkey] or {}
                accepts = int(rec.get("accepts", 0) or 0)
                rejects = int(rec.get("rejects", 0) or 0)
                delta = compute_feedback_delta(accepts, rejects)

        imported_boost = 0.0
        imported_best_match = None

        imported_signal = imported_di_signal if isinstance(imported_di_signal, dict) else {}
        if imported_signal.get("has_match"):
            imported_best_match = imported_signal.get("best_match") if isinstance(imported_signal.get("best_match"), dict) else {}
            imported_urls = imported_best_match.get("urls") if isinstance(imported_best_match.get("urls"), list) else []
            candidate_url = str(cand.get("url") or "").strip().rstrip("/")

            normalized_imported_urls = [
                str(u or "").strip().rstrip("/")
                for u in imported_urls
                if str(u or "").strip()
            ]

            if candidate_url and any(
                candidate_url == u or candidate_url.endswith(u) or u.endswith(candidate_url)
                for u in normalized_imported_urls
            ):
                imported_boost = 0.06

        # ---------------------------------------------------------
        # Live-Domain Target Intelligence
        # ---------------------------------------------------------
        target_intelligence = (
            cand.get("_target_intelligence")
            if isinstance(cand.get("_target_intelligence"), dict)
            else {}
        )

        semantic_route_score = float(target_intelligence.get("semantic_route_score", 0.0) or 0.0)
        authority_score = float(target_intelligence.get("authority_score", 0.0) or 0.0)
        topic_graph_score = float(target_intelligence.get("topic_graph_score", 0.0) or 0.0)
        rb2_weight_score = float(target_intelligence.get("rb2_weight_score", 0.0) or 0.0)
        target_score = float(target_intelligence.get("target_score", 0.0) or 0.0)

        # Normalize intelligence contribution
        intelligence_boost = min(
            0.25,
            (
                (semantic_route_score * 0.0004)
                + (authority_score * 0.0005)
                + (topic_graph_score * 0.0003)
                + (rb2_weight_score * 0.0006)
                + (target_score * 0.0002)
            )
        )

        # ---------------------------------------------------------
        # Imported Target Pool v2 Diagnostics
        # ---------------------------------------------------------
        imported_meta = (
            cand.get("metadata")
            if isinstance(cand.get("metadata"), dict)
            else {}
        )

        imported_diag = {
            "source_type": cand.get("source_type") or cand.get("sourceType"),
            "priority_bucket": (
                cand.get("priority_bucket")
                or imported_meta.get("priority_bucket")
            ),
            "page_type_hint": (
                cand.get("page_type_hint")
                or imported_meta.get("page_type_hint")
            ),
            "import_source": (
                cand.get("import_source")
                or imported_meta.get("import_source")
            ),
            "path": (
                cand.get("path")
                or imported_meta.get("path")
            ),
        }

        live_domain_diag = {
            "source_type": cand.get("source_type") or cand.get("sourceType"),
            "source_origin": (
                cand.get("source_origin")
                or imported_meta.get("source_origin")
            ),
            "priority_bucket": (
                cand.get("priority_bucket")
                or imported_meta.get("priority_bucket")
            ),
            "seed_priority_bucket": (
                cand.get("seed_priority_bucket")
                or imported_meta.get("seed_priority_bucket")
            ),
            "seed_path_match": (
                cand.get("seed_path_match")
                or imported_meta.get("seed_path_match")
            ),
            "page_type_hint": (
                cand.get("page_type_hint")
                or imported_meta.get("page_type_hint")
            ),
            "path": (
                cand.get("path")
                or imported_meta.get("path")
            ),
        }

        final_score = (
            best_score
            + delta
            + imported_boost
            + intelligence_boost
        )

        final_score = max(0.0, min(1.0, float(final_score)))
        logical_inference = analyze_logical_inference_v1(
            anchor_phrase=str(
                phrase_ctx.get("phraseText")
                or phrase_ctx.get("phrase")
                or ""
            ),
            target_title=str(cand.get("title") or ""),
            target_url=str(cand.get("url") or ""),
            context=str(
                phrase_ctx.get("context")
                or phrase_ctx.get("sentence")
                or ""
            ),
            link_type=str(best_kind or "internal"),
        )

        analogical_reasoning = analyze_analogical_reasoning_v1(
            anchor_phrase=str(
                phrase_ctx.get("phraseText")
                or phrase_ctx.get("phrase")
                or ""
            ),
            target_title=str(cand.get("title") or ""),
            target_url=str(cand.get("url") or ""),
            context=str(
                phrase_ctx.get("context")
                or phrase_ctx.get("sentence")
                or ""
            ),
            link_type=str(best_kind or "internal"),
        )

        anchor_purpose = analyze_anchor_purpose_v1(
            anchor_phrase=str(
                phrase_ctx.get("phraseText")
                or phrase_ctx.get("phrase")
                or ""
            ),
            context=str(
                phrase_ctx.get("context")
                or phrase_ctx.get("sentence")
                or ""
            ),
            link_type=str(best_kind or "internal"),
        )

        result_item = {
            "id": cand.get("id"),
            "title": cand.get("title"),
            "url": cand.get("url"),
            "topicId": cand.get("id"),
            "kind": best_kind,
            "tier": tier,
            "score": float(final_score),
            "logical_inference": logical_inference,
            "analogical_reasoning": analogical_reasoning,
            "anchor_purpose": anchor_purpose,
            "scores": signals,
            "feedback": {
                "accepts": accepts,
                "rejects": rejects,
                "delta": float(delta),
            },
            "di_score_adjustments": {
                "imported_url_match_boost": float(imported_boost),
                "live_domain_intelligence_boost": float(intelligence_boost),
                "semantic_route_score": float(semantic_route_score),
                "authority_score": float(authority_score),
                "topic_graph_score": float(topic_graph_score),
                "rb2_weight_score": float(rb2_weight_score),
                "target_score": float(target_score),

                # Target Pool diagnostics
                "imported_target_diagnostics": imported_diag,
                "live_domain_target_diagnostics": live_domain_diag,
            },
            "profile_id": resolved_profile.get("id"),
        }

        if debug:
            result_item["mode_scores"] = debug_mode_scores
            result_item["mode_tiers"] = debug_mode_tiers

        results.append(result_item)

    results.sort(key=lambda x: float(x.get("score", 0.0)), reverse=True)
    return results

# -------------------------------------------------------------
# RB2 Runtime Highlight Bucket Classification
# -------------------------------------------------------------

def classify_highlight_buckets(final_highlights: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Classify final RB2 highlight candidates into LinkCraftor runtime buckets.

    This function is used after:
    Upload Phrase Pool -> Highlight Selection Engine -> Highlight Density Engine

    It decides:
    - internal_strong: direct/high-confidence highlight
    - semantic_optional: useful semantic/optional highlight

    engine_run.py should orchestrate only; this function owns bucket intelligence.
    """

    internal_strong: List[Dict[str, Any]] = []
    semantic_optional: List[Dict[str, Any]] = []

    for candidate in final_highlights or []:
        if not isinstance(candidate, dict):
            continue

        phrase = str(candidate.get("phrase") or "").strip()
        if not phrase:
            continue

        selection_score = int(candidate.get("selection_score") or 0)
        anchor_quality = int(candidate.get("anchor_quality_score") or 0)
        article_relevance = int(candidate.get("article_relevance_score") or 0)
        link_opportunity = int(candidate.get("link_opportunity_score") or 0)
        occurrence_count = int(candidate.get("occurrence_count") or 0)

        source_type = str(candidate.get("source_type") or candidate.get("type") or "").lower()

        # Strong/direct signals:
        # High selection score, strong anchor quality, repeated article relevance,
        # and strong link opportunity should become internal/strong.
        is_direct_strong = (
            selection_score >= 120
            or (
                anchor_quality >= 75
                and article_relevance >= 20
                and link_opportunity >= 25
            )
            or (
                occurrence_count >= 3
                and article_relevance >= 20
                and anchor_quality >= 70
            )
        )

        # Semantic/optional preservation:
        # Useful lower-confidence or context/condition phrases should remain yellow,
        # not be forced into blue.
        is_semantic_optional = (
            not is_direct_strong
            and (
                selection_score >= 80
                or link_opportunity >= 20
                or "condition" in source_type
                or "semantic" in source_type
            )
        )

        if is_direct_strong:
            enriched = dict(candidate)
            enriched["scoring_bucket_reason"] = "direct_high_confidence_runtime_match"
            internal_strong.append(enriched)

        elif is_semantic_optional:
            enriched = dict(candidate)
            enriched["scoring_bucket_reason"] = "semantic_optional_runtime_match"
            semantic_optional.append(enriched)

        else:
            # Conservative fallback: still useful but not strong enough.
            enriched = dict(candidate)
            enriched["scoring_bucket_reason"] = "fallback_semantic_optional"
            semantic_optional.append(enriched)

    return {
        "internal_strong": internal_strong,
        "semantic_optional": semantic_optional,
    }

