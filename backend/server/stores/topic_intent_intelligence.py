from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


_INTENT_RULES = {
    "definition": {
        "family": "educational",
        "patterns": ["what is", "meaning", "definition", "overview", "introduction"],
        "section_terms": ["overview", "definition", "what is", "introduction"],
        "reader_goal": "understand what the topic means",
        "section_role": "orientation",
        "information_type": "definition_or_overview",
    },
    "symptoms_or_signs": {
        "family": "diagnostic",
        "patterns": ["symptom", "sign", "warning sign", "notice", "recognize"],
        "section_terms": ["symptoms", "signs", "warning signs"],
        "reader_goal": "recognize signs or indicators",
        "section_role": "recognition",
        "information_type": "diagnostic_or_indicator_guidance",
    },
    "related_topics": {
        "family": "educational",
        "patterns": ["related", "associated", "linked", "connected", "similar"],
        "section_terms": ["related", "related topics", "related conditions", "associated", "similar"],
        "reader_goal": "understand related topics or connected concepts",
        "section_role": "relationship_mapping",
        "information_type": "related_topic_guidance",
    },
    "causes": {
        "family": "explanatory",
        "patterns": ["cause", "caused by", "reason", "why it happens", "trigger"],
        "section_terms": ["causes", "reasons", "why it happens", "triggers"],
        "reader_goal": "understand causes or drivers",
        "section_role": "explanation",
        "information_type": "causal_explanation",
    },
    "risk_factors": {
        "family": "assessment",
        "patterns": ["risk", "risk factor", "more likely", "increase the chance"],
        "section_terms": ["risk factors", "risks"],
        "reader_goal": "understand what increases likelihood or exposure",
        "section_role": "risk_assessment",
        "information_type": "risk_guidance",
    },
    "treatment_or_solution": {
        "family": "action",
        "patterns": ["treatment", "manage", "management", "solution", "fix", "remedy", "therapy"],
        "section_terms": ["treatment", "management", "solutions", "remedies", "how to fix"],
        "reader_goal": "learn possible actions or solutions",
        "section_role": "intervention",
        "information_type": "action_guidance",
    },
    "prevention": {
        "family": "action",
        "patterns": ["prevent", "avoid", "reduce the risk", "protect", "best practice"],
        "section_terms": ["prevention", "how to prevent", "avoidance", "best practices"],
        "reader_goal": "learn how to prevent or reduce future problems",
        "section_role": "prevention",
        "information_type": "preventive_guidance",
    },
    "comparison": {
        "family": "evaluative",
        "patterns": ["vs", "versus", "compared with", "difference between", "better than"],
        "section_terms": ["comparison", "vs", "difference", "differences"],
        "reader_goal": "compare options, concepts, or alternatives",
        "section_role": "comparison",
        "information_type": "comparative_guidance",
    },
    "process_or_steps": {
        "family": "operational",
        "patterns": ["step", "how to", "process", "workflow", "guide", "checklist"],
        "section_terms": ["steps", "how to", "process", "workflow", "checklist", "guide"],
        "reader_goal": "follow a process or sequence",
        "section_role": "instruction",
        "information_type": "procedural_guidance",
    },
    "measurement_or_monitoring": {
        "family": "assessment",
        "patterns": ["measure", "monitor", "track", "test", "calculate", "score"],
        "section_terms": ["monitoring", "measurement", "testing", "tracking", "calculation"],
        "reader_goal": "measure, monitor, test, or calculate something",
        "section_role": "assessment",
        "information_type": "measurement_or_monitoring_guidance",
    },
    "cost_or_pricing": {
        "family": "commercial",
        "patterns": ["cost", "price", "pricing", "fee", "revenue", "profit", "subscription"],
        "section_terms": ["pricing", "cost", "fees", "revenue", "profit"],
        "reader_goal": "understand cost, pricing, or financial value",
        "section_role": "commercial_evaluation",
        "information_type": "financial_or_pricing_guidance",
    },
    "legal_or_policy": {
        "family": "governance",
        "patterns": ["law", "legal", "policy", "terms", "privacy", "compliance", "liability"],
        "section_terms": ["legal", "policy", "terms", "privacy", "compliance"],
        "reader_goal": "understand legal, policy, or compliance requirements",
        "section_role": "governance",
        "information_type": "legal_or_policy_guidance",
    },
    "faq": {
        "family": "support",
        "patterns": ["faq", "question", "commonly asked", "frequently asked"],
        "section_terms": ["faq", "frequently asked questions", "questions"],
        "reader_goal": "answer common questions",
        "section_role": "question_answering",
        "information_type": "faq_guidance",
    },
}


_CATEGORY_INTENT_HINTS = {
    "symptom_or_sign": "symptoms_or_signs",
    "medical_monitoring": "measurement_or_monitoring",
    "medical_measurement": "measurement_or_monitoring",
    "medical_condition": "related_topics",
    "finance_metric": "cost_or_pricing",
    "finance_concept": "cost_or_pricing",
    "finance_market": "cost_or_pricing",
    "legal_document": "legal_or_policy",
    "legal_concept": "legal_or_policy",
    "travel_document": "process_or_steps",
    "travel_action": "process_or_steps",
    "travel_product": "cost_or_pricing",
    "seo_concept": "definition",
    "technology_component": "definition",
    "technology_concept": "definition",
}


_RELATIONSHIP_FAMILY_INTENT_HINTS = {
    "peer": "related_topics",
    "contextual": "related_topics",
    "clinical": "measurement_or_monitoring",
}


_RELATIONSHIP_TYPE_INTENT_HINTS = {
    "peer_symptoms": "symptoms_or_signs",
    "related_conditions": "related_topics",
    "condition_context": "related_topics",
    "monitoring_context": "measurement_or_monitoring",
    "measurement_context": "measurement_or_monitoring",
    "measurement_condition_association": "measurement_or_monitoring",
    "symptom_condition_association": "symptoms_or_signs",
    "symptom_context": "symptoms_or_signs",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    return f"{prefix}_{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:12]}"


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _match_score(text: str, terms: List[str]) -> int:
    lowered = _normalize(text)
    score = 0

    for term in terms:
        if re.search(r"\b" + re.escape(_normalize(term)) + r"\b", lowered):
            score += 1

    return score


def _section_position(section_index: int, total_sections: int) -> str:
    if total_sections <= 1:
        return "single_section"
    if section_index == 0:
        return "opening"
    if section_index == total_sections - 1:
        return "closing"
    return "middle"


def _infer_section_intent(
    section_title: str,
    section_text: str,
    semantic_objects: List[Dict[str, Any]],
    relationship_family_counts: Dict[str, int],
    relationship_type_counts: Dict[str, int],
    section_index: int,
    total_sections: int,
) -> Dict[str, Any]:
    scores: Dict[str, float] = defaultdict(float)
    evidence: Dict[str, List[str]] = defaultdict(list)

    for intent, rule in _INTENT_RULES.items():
        title_score = _match_score(section_title, rule["section_terms"]) * 4
        text_score = _match_score(section_text, rule["patterns"]) * 1.5

        if title_score:
            scores[intent] += title_score
            evidence[intent].append(f"heading_match:+{title_score}")

        if text_score:
            scores[intent] += text_score
            evidence[intent].append(f"text_pattern_match:+{text_score}")

    category_counts = Counter(obj.get("category") for obj in semantic_objects)

    for category, count in category_counts.items():
        hinted_intent = _CATEGORY_INTENT_HINTS.get(category)
        if hinted_intent:
            boost = min(3.0, count * 0.75)
            scores[hinted_intent] += boost
            evidence[hinted_intent].append(f"semantic_category:{category}:+{boost}")

    for family, count in relationship_family_counts.items():
        hinted_intent = _RELATIONSHIP_FAMILY_INTENT_HINTS.get(family)
        if hinted_intent:
            boost = min(2.0, count * 0.35)
            scores[hinted_intent] += boost
            evidence[hinted_intent].append(f"relationship_family:{family}:+{boost}")

    for rel_type, count in relationship_type_counts.items():
        hinted_intent = _RELATIONSHIP_TYPE_INTENT_HINTS.get(rel_type)
        if hinted_intent:
            boost = min(2.5, count * 0.45)
            scores[hinted_intent] += boost
            evidence[hinted_intent].append(f"relationship_type:{rel_type}:+{boost}")

    position = _section_position(section_index, total_sections)

    if position == "opening":
        scores["definition"] += 0.75
        evidence["definition"].append("section_position:opening:+0.75")

    if position == "closing":
        scores["prevention"] += 0.35
        scores["faq"] += 0.15
        evidence["prevention"].append("section_position:closing:+0.35")
        evidence["faq"].append("section_position:closing:+0.15")

    if not scores:
        best_intent = "general_information"
        best_score = 0.0
    else:
        best_intent = max(scores, key=scores.get)
        best_score = scores.get(best_intent, 0.0)

    if best_score <= 0:
        best_intent = "general_information"
        confidence = 0.45
        intent_family = "educational"
        reader_goal = "learn general information about the topic"
        section_role = "information"
        information_type = "general_information"
    else:
        rule = _INTENT_RULES[best_intent]
        confidence = min(0.95, 0.50 + (best_score * 0.06))
        intent_family = rule["family"]
        reader_goal = rule["reader_goal"]
        section_role = rule["section_role"]
        information_type = rule["information_type"]

    return {
        "intent_family": intent_family,
        "topic_intent": best_intent,
        "intent_confidence": round(confidence, 2),
        "reader_goal": reader_goal,
        "section_role": section_role,
        "information_type": information_type,
        "section_position": position,
        "intent_scores": dict(sorted(scores.items(), key=lambda item: item[1], reverse=True)),
        "decision_evidence": dict(evidence),
    }



def _synthesize_article_intent_v1(
    article: Dict[str, Any],
    section_intents: List[Dict[str, Any]],
) -> Dict[str, Any]:
    intent_counts = Counter(item["topic_intent"] for item in section_intents)
    family_counts = Counter(item["intent_family"] for item in section_intents)
    role_counts = Counter(item["section_role"] for item in section_intents)
    info_counts = Counter(item["information_type"] for item in section_intents)

    ordered_intents = [item["topic_intent"] for item in section_intents]
    ordered_roles = [item["section_role"] for item in section_intents]

    has_action = any(item["intent_family"] == "action" for item in section_intents)
    has_assessment = any(item["intent_family"] == "assessment" for item in section_intents)
    has_education = any(item["intent_family"] == "educational" for item in section_intents)
    has_diagnostic = any(item["intent_family"] == "diagnostic" for item in section_intents)
    has_commercial = any(item["intent_family"] == "commercial" for item in section_intents)
    has_governance = any(item["intent_family"] == "governance" for item in section_intents)
    has_operational = any(item["intent_family"] == "operational" for item in section_intents)

    article_title = article.get("title") or "Untitled Article"

    if has_governance:
        article_purpose = "legal or policy guidance"
        primary_reader_goal = "understand requirements, rules, or obligations"
        article_intent = "legal_or_policy_guidance"
        article_family = "governance"
    elif has_commercial:
        article_purpose = "commercial evaluation guidance"
        primary_reader_goal = "evaluate cost, pricing, or business value"
        article_intent = "commercial_evaluation"
        article_family = "commercial"
    elif has_operational:
        article_purpose = "procedural or operational guidance"
        primary_reader_goal = "follow a process or complete a task"
        article_intent = "procedural_guidance"
        article_family = "operational"
    elif has_assessment and has_action:
        article_purpose = "educational guidance with assessment and action support"
        primary_reader_goal = "understand the topic, assess what matters, and learn what actions may help"
        article_intent = "assessment_and_action_guidance"
        article_family = "educational"
    elif has_assessment and has_diagnostic:
        article_purpose = "educational assessment guidance"
        primary_reader_goal = "understand indicators, measurements, or assessment signals"
        article_intent = "assessment_guidance"
        article_family = "assessment"
    elif has_action:
        article_purpose = "action-oriented guidance"
        primary_reader_goal = "learn possible steps, solutions, or prevention actions"
        article_intent = "action_guidance"
        article_family = "action"
    elif has_assessment:
        article_purpose = "assessment-oriented guidance"
        primary_reader_goal = "measure, monitor, compare, or evaluate the topic"
        article_intent = "assessment_guidance"
        article_family = "assessment"
    elif has_education:
        article_purpose = "educational explanation"
        primary_reader_goal = "understand the topic and its related concepts"
        article_intent = "educational_guidance"
        article_family = "educational"
    else:
        article_purpose = "general information"
        primary_reader_goal = "learn general information about the topic"
        article_intent = "general_information"
        article_family = "educational"

    confidence_seed = 0.55
    if len(section_intents) >= 3:
        confidence_seed += 0.10
    if len(set(ordered_intents)) >= 2:
        confidence_seed += 0.10
    if max(family_counts.values(), default=0) >= 2:
        confidence_seed += 0.10

    article_confidence = round(min(confidence_seed, 0.95), 2)

    return {
        "article_intent_id": _stable_id("article_intent", article.get("article_id"), article_intent, article_family),
        "intent_scope": "article",
        "article_id": article.get("article_id"),
        "article_title": article_title,
        "article_intent": article_intent,
        "article_intent_family": article_family,
        "article_purpose": article_purpose,
        "primary_reader_goal": primary_reader_goal,
        "article_intent_confidence": article_confidence,
        "supporting_section_intents": [
            {
                "section_id": item["section_id"],
                "section_title": item["section_title"],
                "intent_scope": "section",
                "intent_family": item["intent_family"],
                "topic_intent": item["topic_intent"],
                "section_role": item["section_role"],
                "information_type": item["information_type"],
                "intent_confidence": item["intent_confidence"],
            }
            for item in section_intents
        ],
        "article_decision_evidence": {
            "intent_counts": dict(intent_counts),
            "intent_family_counts": dict(family_counts),
            "section_role_counts": dict(role_counts),
            "information_type_counts": dict(info_counts),
            "ordered_section_intents": ordered_intents,
            "ordered_section_roles": ordered_roles,
        },
    }

def build_topic_intent_v1(
    semantic_context_model: Dict[str, Any],
    extraction_model: Dict[str, Any],
    neighborhood_model: Dict[str, Any],
) -> Dict[str, Any]:
    article = semantic_context_model.get("article", {})
    section_contexts = semantic_context_model.get("section_contexts", [])

    objects_by_section = defaultdict(list)

    for mention in extraction_model.get("mentions", []):
        section_id = mention.get("location", {}).get("section_id")
        if section_id:
            objects_by_section[section_id].append({
                "semantic_object_id": mention["semantic_object_id"],
                "canonical_text": mention["canonical_text"],
                "category": mention["category"],
            })

    relationship_families_by_section = defaultdict(Counter)
    relationship_types_by_section = defaultdict(Counter)

    for neighborhood in neighborhood_model.get("neighborhoods", []):
        for evidence in neighborhood.get("evidence", []):
            unit_key = evidence.get("unit_key", "")
            if unit_key.startswith("section:"):
                section_id = unit_key.split(":", 1)[1]
                relationship_families_by_section[section_id][neighborhood.get("relationship_family")] += 1
                relationship_types_by_section[section_id][neighborhood.get("relationship_type")] += 1

    section_intents = []
    total_sections = len(section_contexts)

    for section in section_contexts:
        section_id = section["section_id"]
        section_title = section.get("section_title", "")
        section_text = section.get("context", {}).get("section_text", "")

        unique_objects = {
            item["canonical_text"]: item
            for item in objects_by_section.get(section_id, [])
        }

        relationship_family_counts = dict(relationship_families_by_section.get(section_id, {}))
        relationship_type_counts = dict(relationship_types_by_section.get(section_id, {}))

        inferred = _infer_section_intent(
            section_title,
            section_text,
            sorted(unique_objects.values(), key=lambda x: x["canonical_text"]),
            relationship_family_counts,
            relationship_type_counts,
            section.get("section_index", 0),
            total_sections,
        )

        section_intents.append({
            "section_intent_id": _stable_id("section_intent", article.get("article_id"), section_id),
            "article_id": article.get("article_id"),
            "section_id": section_id,
            "intent_scope": "section",
            "section_index": section.get("section_index"),
            "section_position": inferred["section_position"],
            "section_title": section_title,
            "heading_level": section.get("heading_level"),
            "intent_family": inferred["intent_family"],
            "topic_intent": inferred["topic_intent"],
            "intent_confidence": inferred["intent_confidence"],
            "reader_goal": inferred["reader_goal"],
            "section_role": inferred["section_role"],
            "information_type": inferred["information_type"],
            "intent_scores": inferred["intent_scores"],
            "decision_evidence": inferred["decision_evidence"],
            "semantic_objects": sorted(unique_objects.values(), key=lambda x: x["canonical_text"]),
            "relationship_family_counts": relationship_family_counts,
            "relationship_type_counts": relationship_type_counts,
            "evidence": {
                "section_text": section_text,
                "breadcrumb": section.get("context", {}).get("breadcrumb", ""),
                "heading_ancestry": section.get("context", {}).get("heading_ancestry", []),
                "entry_block_id": section.get("context", {}).get("entry_block_id"),
                "exit_block_id": section.get("context", {}).get("exit_block_id"),
            },
        })

    article_intent_counts = Counter(item["topic_intent"] for item in section_intents)
    intent_family_counts = Counter(item["intent_family"] for item in section_intents)
    section_role_counts = Counter(item["section_role"] for item in section_intents)
    information_type_counts = Counter(item["information_type"] for item in section_intents)

    article_intent = _synthesize_article_intent_v1(article, section_intents)

    dominant_article_intent = article_intent["article_intent"]
    dominant_intent_family = article_intent["article_intent_family"]

    return {
        "schema_version": "topic_intent_intelligence_v1",
        "phase": "4.6.5",
        "patch": "4.6.5B",
        "created_at": _now_iso(),
        "source_models": {
            "semantic_context": {
                "schema_version": semantic_context_model.get("schema_version"),
                "phase": semantic_context_model.get("phase"),
                "patch": semantic_context_model.get("patch"),
            },
            "entity_concept_extraction": {
                "schema_version": extraction_model.get("schema_version"),
                "phase": extraction_model.get("phase"),
                "patch": extraction_model.get("patch"),
            },
            "phrase_neighborhoods": {
                "schema_version": neighborhood_model.get("schema_version"),
                "phase": neighborhood_model.get("phase"),
                "patch": neighborhood_model.get("patch"),
            },
        },
        "article": article,
        "domain_label": extraction_model.get("domain_label"),
        "dominant_article_intent": dominant_article_intent,
        "dominant_intent_family": dominant_intent_family,
        "article_intent": article_intent,
        "section_intents": section_intents,
        "metadata": {
            "article_intent_count": 1,
            "section_intent_count": len(section_intents),
            "article_intent_counts": dict(article_intent_counts),
            "intent_family_counts": dict(intent_family_counts),
            "section_role_counts": dict(section_role_counts),
            "information_type_counts": dict(information_type_counts),
        },
        "boundary_rule": (
            "Topic Intent Intelligence detects section-level intent and synthesizes article-level purpose, reader goal, and intent family. "
            "It does not resolve links, create blue highlights, create yellow highlights, score target pages, "
            "write memory, perform reasoning, or build final semantic relationship graphs."
        ),
    }


def save_topic_intent_v1(
    semantic_context_model: Dict[str, Any],
    extraction_model: Dict[str, Any],
    neighborhood_model: Dict[str, Any],
    output_path: str | Path,
) -> Dict[str, Any]:
    model = build_topic_intent_v1(
        semantic_context_model,
        extraction_model,
        neighborhood_model,
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(model, indent=2, ensure_ascii=False), encoding="utf-8")
    return model


def explain_topic_intent_intelligence_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.5",
        "patch": "4.6.5B",
        "name": "Universal Topic Intent Intelligence with Article Intent Synthesizer",
        "purpose": "Detect section-level intent and synthesize article-level purpose across any niche.",
        "input": [
            "Semantic Context Model from Phase 4.6.2A",
            "Entity & Concept Extraction Model from Phase 4.6.3C",
            "Phrase Neighborhood Model from Phase 4.6.4B",
        ],
        "output": "Topic Intent Intelligence Model",
        "does": [
            "detects article-level intent",
            "detects article-level purpose",
            "detects primary reader objective",
            "detects section topic intent",
            "detects intent family",
            "detects reader goal",
            "detects section role",
            "detects information type",
            "uses universal intent rules",
            "uses semantic object categories as decision evidence",
            "uses relationship families as decision evidence",
            "uses relationship types as decision evidence",
            "uses section position as decision evidence",
            "adds intent_scope for article and section records",
            "synthesizes article intent from section intent patterns",
            "attaches semantic objects to section intent",
            "attaches relationship families to section intent",
            "summarizes dominant article intent",
            "works across multiple niches",
        ],
        "does_not": [
            "perform internal link resolving",
            "perform semantic link resolving",
            "create blue highlights",
            "create yellow highlights",
            "score target pages",
            "build final relationship graphs",
            "write memory",
            "perform reasoning",
            "generate explanations",
        ],
    }
