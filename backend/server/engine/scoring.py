# backend/server/engine/scoring.py
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import math
import re

# -------------------------------------------------------------
# 1) Weight tables & thresholds (ported from scoring.js)
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
    return str(s or "").lower().strip().replace("\s+", " ")

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
    ratio = (int(accepts) - int(rejects)) / float(total)  # [-1, +1]
    MAX_DELTA = 0.18
    return float(ratio) * MAX_DELTA



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


def entity_score(phrase_entities: List[Dict[str, Any]], candidate_entities: List[Dict[str, Any]]) -> float:
    if not phrase_entities or not candidate_entities:
        return 0.0

    max_possible = 0.0
    actual = 0.0

    for pe in phrase_entities:
        if not pe:
            continue
        p_type = pe.get("type")
        type_weight = ENTITY_TYPE_WEIGHT.get(p_type, 1.0)
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

            # A) Exact same canonical entity id
            if p_id and c_id and p_id == c_id:
                rel_weight = ENTITY_RELATION_WEIGHTS["EXACT_ID"]
            else:
                # B) Alias overlap
                p_ali_n = [safe_norm(x) for x in p_ali]
                c_ali_n = [safe_norm(x) for x in c_ali]
                alias_overlap = (
                    intersect_count(p_ali_n, [safe_norm(c_id), *c_ali_n])
                    or intersect_count(c_ali_n, [safe_norm(p_id), *p_ali_n])
                )
                if alias_overlap > 0:
                    rel_weight = max(rel_weight, ENTITY_RELATION_WEIGHTS["ALIAS"])

                # C) Category overlap
                if intersect_count(p_cats, c_cats) > 0:
                    rel_weight = max(rel_weight, ENTITY_RELATION_WEIGHTS["CATEGORY"])

                # D) Parent–child
                shared_parent = (
                    intersect_count(p_par, c_par)
                    or intersect_count(p_par, c_chi)
                    or intersect_count(p_chi, c_par)
                )
                if shared_parent > 0:
                    rel_weight = max(rel_weight, ENTITY_RELATION_WEIGHTS["PARENT_CHILD"])

                # E) Siblings
                sib_parents = any(x in set(c_par) for x in set(p_par))
                if sib_parents and rel_weight == 0.0:
                    rel_weight = max(rel_weight, ENTITY_RELATION_WEIGHTS["SIBLING_CLASS"])

            best_local = max(best_local, rel_weight)

        if best_local > 0.0:
            actual += type_weight * best_local

    if not max_possible:
        return 0.0
    return min(1.0, actual / max_possible)


def graph_score(phrase_ctx: Dict[str, Any], candidate: Dict[str, Any]) -> float:
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
        base = entity_score(phrase_ctx.get("entities") or [], candidate.get("entities") or []) * 0.7

    # Typed relation overlap boost
    p_rel = phrase_ctx.get("graphRelations") or []
    c_rel = candidate.get("graphRelations") or []
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


def context_score(phrase_ctx: Dict[str, Any], candidate: Dict[str, Any]) -> float:
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
    if ctx_type and ctx_type in CONTEXT_TOPIC_COMPAT and topic_types:
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


def internal_source_score(candidate: Dict[str, Any]) -> float:
    st = candidate.get("sourceType")
    base = INTERNAL_SOURCE_BASE.get(st, 0.6)

    topic_types = candidate.get("topicTypes") or []
    section_roles = candidate.get("sectionRoles") or []
    entities = candidate.get("entities") or []

    role = ("PILLAR" in topic_types) or ("PILLAR" in section_roles) or any((e or {}).get("meta", {}).get("role") == "PILLAR" for e in entities)
    canonical_boost = 0.1 if candidate.get("isCanonicalTopic") or role else 0.0

    score = base + canonical_boost
    return min(1.0, score)


def external_source_score(candidate: Dict[str, Any]) -> float:
    host = str(candidate.get("domain") or "").lower()
    base = EXTERNAL_DOMAIN_AUTHORITY.get(host, 0.5)
    return float(base)


# -------------------------------------------------------------
# 4) Mode-specific combination
# -------------------------------------------------------------

def compute_internal_score(phrase_ctx: Dict[str, Any], candidate: Dict[str, Any], s: Dict[str, float]) -> float:
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


def classify_internal_tier(score: float) -> Optional[str]:
    if score >= 0.75:
        return "high"
    if score >= 0.55:
        return "mid"
    if score >= 0.35:
        return "low"
    return None


def compute_semantic_score(phrase_ctx: Dict[str, Any], candidate: Dict[str, Any], s: Dict[str, float]) -> float:
    lexical, entity, graph, context, source = s["lexical"], s["entity"], s["graph"], s["context"], s["source"]

    if entity == 0.0 and graph == 0.0 and context == 0.0 and lexical < 0.20:
        return 0.0

    has_entity_graph = (entity + graph) >= 0.15
    has_lexical = lexical >= 0.30
    if not has_entity_graph and not has_lexical:
        return 0.0

    score = (
        WEIGHTS_SEMANTIC["lexical"] * lexical +
        WEIGHTS_SEMANTIC["entity"] * entity +
        WEIGHTS_SEMANTIC["graph"] * graph +
        WEIGHTS_SEMANTIC["context"] * context +
        WEIGHTS_SEMANTIC["source"] * source
    )

    if entity >= 0.70 and lexical >= 0.80:
        score *= 0.4

    return max(0.0, min(1.0, score))


def classify_semantic_tier(score: float) -> Optional[str]:
    if score >= 0.40:
        return "high"
    if score >= 0.22:
        return "mid"
    if score >= 0.12:
        return "low"
    return None


def compute_external_score(phrase_ctx: Dict[str, Any], candidate: Dict[str, Any], s: Dict[str, float]) -> float:
    lexical, entity, graph, context, source = s["lexical"], s["entity"], s["graph"], s["context"], s["source"]

    if source < 0.5:
        return 0.0
    if entity < 0.3:
        return 0.0

    score = (
        WEIGHTS_EXTERNAL["lexical"] * lexical +
        WEIGHTS_EXTERNAL["entity"] * entity +
        WEIGHTS_EXTERNAL["graph"] * graph +
        WEIGHTS_EXTERNAL["context"] * context +
        WEIGHTS_EXTERNAL["source"] * source
    )
    return max(0.0, min(1.0, score))


def classify_external_tier(score: float) -> Optional[str]:
    if score >= 0.75:
        return "high"
    if score >= 0.55:
        return "mid"
    return None


# -------------------------------------------------------------
# 5) Main API (pure function)
# -------------------------------------------------------------

def score_candidates_for_phrase(
    phrase_ctx: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    feedback_map: Optional[Dict[str, Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:

    results: List[Dict[str, Any]] = []  # <-- FIX: define results first

    if not phrase_ctx or not candidates:
        return results  # <-- FIX: return the empty list

    for cand in candidates:
        lexical = lexical_score(phrase_ctx.get("phraseText", ""), cand.get("title", ""))
        entity  = entity_score(phrase_ctx.get("entities") or [], cand.get("entities") or [])
        graph   = graph_score(phrase_ctx, cand)
        context = context_score(phrase_ctx, cand)
        source  = external_source_score(cand) if cand.get("isExternal") else internal_source_score(cand)

        signals = {"lexical": lexical, "entity": entity, "graph": graph, "context": context, "source": source}

        best_kind = None
        best_score = 0.0
        tier = None

        if cand.get("isExternal"):
            s_ext = compute_external_score(phrase_ctx, cand, signals)
            t_ext = classify_external_tier(s_ext) if s_ext > 0 else None
            if t_ext:
                best_kind, best_score, tier = "external", s_ext, t_ext
        else:
            s_int = compute_internal_score(phrase_ctx, cand, signals)
            s_sem = compute_semantic_score(phrase_ctx, cand, signals)

            t_int = classify_internal_tier(s_int) if s_int > 0 else None
            t_sem = classify_semantic_tier(s_sem) if s_sem > 0 else None

            if t_int and not t_sem:
                best_kind, best_score, tier = "internal", s_int, t_int
            elif (not t_int) and t_sem:
                best_kind, best_score, tier = "semantic", s_sem, t_sem
            elif t_int and t_sem:
                if s_int >= s_sem + 0.10:
                    best_kind, best_score, tier = "internal", s_int, t_int
                else:
                    best_kind, best_score, tier = "semantic", s_sem, t_sem

        if not best_kind or not tier:
            continue

        # ---- Decision Memory (feedback) ----
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

        final_score = best_score + delta
        final_score = max(0.0, min(1.0, float(final_score)))

        results.append({
            "id": cand.get("id"),
            "title": cand.get("title"),
            "url": cand.get("url"),
            "topicId": cand.get("id"),
            "kind": best_kind,
            "tier": tier,
            "score": float(final_score),
            "scores": signals,
            "feedback": {
                "accepts": accepts,
                "rejects": rejects,
                "delta": float(delta),
            },
        })

    results.sort(key=lambda x: float(x.get("score", 0.0)), reverse=True)
    return results
