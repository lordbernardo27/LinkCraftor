"""Canonical Topic Intent Intelligence v1.

Phase 4.6.4.

Consumes the certified Phase 4.6.3 Phrase Neighborhood Intelligence
result together with the certified Phase 4.6.1 Runtime Reader result.

Responsibilities:
- article content intent
- section content intent
- link intent
- anchor purpose
- evidence aggregation
- confidence and ambiguity handling

This stage does not score links, resolve targets, infer causal or logical
relationships, perform ontology alignment, write Semantic Memory, learn
from users, or create editor highlights.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Mapping


TOPIC_INTENT_INTELLIGENCE_VERSION = (
    "topic_intent_intelligence_v1"
)


class TopicIntentIntelligenceError(RuntimeError):
    """Base fail-closed error for Phase 4.6.4."""



_CONTENT_INTENT_RULES = {
    "definition_or_overview": {
        "family": "informational",
        "heading_terms": (
            "what is",
            "overview",
            "introduction",
            "meaning",
            "definition",
        ),
        "text_terms": (
            "is a",
            "refers to",
            "means",
            "defined as",
            "overview",
        ),
        "reader_goal":
            "understand what the subject is and its basic context",
    },
    "explanation": {
        "family": "explanatory",
        "heading_terms": (
            "how",
            "why",
            "works",
            "role",
            "support",
            "importance",
        ),
        "text_terms": (
            "because",
            "allows",
            "enable",
            "helps",
            "works by",
            "used for",
            "designed for",
        ),
        "reader_goal":
            "understand how or why the subject works or matters",
    },
    "process_or_instruction": {
        "family": "instructional",
        "heading_terms": (
            "how to",
            "steps",
            "process",
            "guide",
            "workflow",
        ),
        "text_terms": (
            "first",
            "next",
            "then",
            "step",
            "follow",
            "you can",
        ),
        "reader_goal":
            "follow a process or perform an action",
    },
    "comparison_or_evaluation": {
        "family": "evaluative",
        "heading_terms": (
            "comparison",
            "versus",
            "vs",
            "difference",
            "advantages",
            "disadvantages",
        ),
        "text_terms": (
            "compared with",
            "compared to",
            "whereas",
            "better than",
            "advantage",
            "disadvantage",
        ),
        "reader_goal":
            "compare or evaluate alternatives, characteristics, or tradeoffs",
    },
    "risk_or_safety": {
        "family": "assessment",
        "heading_terms": (
            "risk",
            "risks",
            "safety",
            "danger",
            "problem",
            "problems",
            "challenge",
            "challenges",
            "limitation",
            "limitations",
        ),
        "text_terms": (
            "risk",
            "danger",
            "unsafe",
            "warning",
            "hazard",
            "problem",
        ),
        "reader_goal":
            "understand risks, safety considerations, or potential problems",
    },
    "measurement_or_monitoring": {
        "family": "assessment",
        "heading_terms": (
            "monitor",
            "monitoring",
            "measurement",
            "tracking",
            "observation",
            "detection",
        ),
        "text_terms": (
            "monitor",
            "measure",
            "track",
            "observe",
            "detect",
            "collect data",
        ),
        "reader_goal":
            "understand how something is observed, measured, or monitored",
    },
    "summary_or_conclusion": {
        "family": "synthesis",
        "heading_terms": (
            "conclusion",
            "summary",
            "key takeaways",
            "takeaways",
            "final thoughts",
        ),
        "text_terms": (
            "in conclusion",
            "in summary",
            "overall",
            "to summarize",
            "taken together",
        ),
        "reader_goal":
            "consolidate the main ideas or conclusions of the subject",
    },
    "practical_application": {
        "family": "applied_information",
        "heading_terms": (
            "uses",
            "applications",
            "everyday",
            "daily life",
            "benefits",
            "communication",
            "communications",
            "navigation",
            "weather",
            "mapping",
            "planning",
        ),
        "text_terms": (
            "use",
            "used",
            "support",
            "helps",
            "provide",
            "service",
            "application",
        ),
        "reader_goal":
            "understand practical uses, applications, or benefits",
    },
}


def _normalize_intent_text(text: Any) -> str:
    return re.sub(
        r"\s+",
        " ",
        str(text or "").strip().casefold(),
    )


def _term_hits(
    text: str,
    terms: tuple[str, ...],
) -> list[str]:
    normalized = _normalize_intent_text(text)

    hits = []

    for term in terms:
        needle = _normalize_intent_text(term)

        if not needle:
            continue

        if re.search(
            r"(?<!\w)"
            + re.escape(needle)
            + r"(?!\w)",
            normalized,
        ):
            hits.append(term)

    return hits


def _section_text_v1(
    section: Mapping[str, Any],
    blocks_by_id: Mapping[str, Mapping[str, Any]],
) -> str:
    parts: list[str] = []

    for block_id in section.get("block_ids", []):
        block = blocks_by_id.get(str(block_id))

        if not isinstance(block, Mapping):
            continue

        if block.get("block_type") == "heading":
            continue

        text = str(block.get("text") or "").strip()

        if text:
            parts.append(text)

    return "\n".join(parts)


def _infer_content_intent_v1(
    *,
    heading: str,
    text: str,
) -> dict[str, Any]:
    scores: dict[str, float] = {}
    evidence: dict[str, dict[str, Any]] = {}

    for intent_name, rule in _CONTENT_INTENT_RULES.items():
        heading_hits = _term_hits(
            heading,
            rule["heading_terms"],
        )
        text_hits = _term_hits(
            text,
            rule["text_terms"],
        )

        heading_score = min(
            len(heading_hits) * 2.5,
            7.5,
        )
        text_score = min(
            len(text_hits) * 1.0,
            8.0,
        )

        total = heading_score + text_score

        scores[intent_name] = round(total, 3)

        evidence[intent_name] = {
            "heading_hits": heading_hits,
            "text_hits": text_hits,
            "heading_score": heading_score,
            "text_score": text_score,
        }

    ranked = sorted(
        scores.items(),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    )

    best_intent, best_score = ranked[0]
    second_score = (
        ranked[1][1]
        if len(ranked) > 1
        else 0.0
    )

    if best_score <= 0:
        return {
            "content_intent":
                "general_information",
            "intent_family":
                "informational",
            "reader_goal":
                "understand general information about the subject",
            "confidence":
                0.40,
            "ambiguity_status":
                "LOW_EVIDENCE",
            "score_margin":
                0.0,
            "intent_scores":
                scores,
            "decision_evidence":
                evidence,
        }

    margin = round(
        best_score - second_score,
        3,
    )

    confidence = 0.48
    confidence += min(best_score, 10.0) * 0.035
    confidence += min(max(margin, 0.0), 5.0) * 0.025
    confidence = round(
        min(confidence, 0.95),
        3,
    )

    if margin < 1.0:
        ambiguity_status = "AMBIGUOUS"
    elif margin < 2.5:
        ambiguity_status = "MIXED"
    else:
        ambiguity_status = "CLEAR"

    rule = _CONTENT_INTENT_RULES[
        best_intent
    ]

    return {
        "content_intent":
            best_intent,
        "intent_family":
            rule["family"],
        "reader_goal":
            rule["reader_goal"],
        "confidence":
            confidence,
        "ambiguity_status":
            ambiguity_status,
        "score_margin":
            margin,
        "intent_scores":
            scores,
        "decision_evidence":
            evidence,
    }


def build_section_content_intents_v1(
    runtime_reader_result: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Infer content intent for every canonical section."""

    runtime_model = runtime_reader_result[
        "semantic_reading_model"
    ]

    sections = runtime_model["sections"]
    blocks = runtime_model["blocks"]

    blocks_by_id = {
        str(block["block_id"]): block
        for block in blocks
        if isinstance(block, Mapping)
        and block.get("block_id")
    }

    section_intents: list[dict[str, Any]] = []

    for section in sections:
        if not isinstance(section, Mapping):
            raise TopicIntentIntelligenceError(
                "Invalid canonical section record."
            )

        section_id = str(
            section.get("section_id") or ""
        ).strip()

        section_title = str(
            section.get("section_title") or ""
        ).strip()

        if not section_id:
            raise TopicIntentIntelligenceError(
                "Canonical section is missing section_id."
            )

        section_text = _section_text_v1(
            section,
            blocks_by_id,
        )

        inferred = _infer_content_intent_v1(
            heading=section_title,
            text=section_text,
        )

        section_intents.append({
            "section_id":
                section_id,
            "section_index":
                section.get("section_index"),
            "section_title":
                section_title,
            "heading_level":
                section.get("heading_level"),
            "content_intent":
                inferred["content_intent"],
            "intent_family":
                inferred["intent_family"],
            "reader_goal":
                inferred["reader_goal"],
            "intent_confidence":
                inferred["confidence"],
            "ambiguity_status":
                inferred["ambiguity_status"],
            "score_margin":
                inferred["score_margin"],
            "intent_scores":
                inferred["intent_scores"],
            "decision_evidence":
                inferred["decision_evidence"],
            "source_block_ids":
                list(section.get("block_ids") or []),
            "source_paragraph_ids":
                list(section.get("paragraph_ids") or []),
            "raw_section_text_persisted":
                False,
        })

    return section_intents


def build_article_content_intent_v1(
    runtime_reader_result: Mapping[str, Any],
    section_intents: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Synthesize article content intent from title and section evidence."""

    if not section_intents:
        raise TopicIntentIntelligenceError(
            "Article intent requires section intent evidence."
        )

    runtime_model = runtime_reader_result[
        "semantic_reading_model"
    ]

    article = runtime_model["article"]

    title = str(
        article.get("title") or ""
    ).strip()

    blocks = runtime_model["blocks"]

    article_text = "\n".join(
        str(block.get("text") or "").strip()
        for block in blocks
        if isinstance(block, Mapping)
        and block.get("block_type") != "heading"
        and str(block.get("text") or "").strip()
    )

    direct = _infer_content_intent_v1(
        heading=title,
        text=article_text,
    )

    section_counts = Counter(
        str(item.get("content_intent"))
        for item in section_intents
        if item.get("content_intent")
    )

    section_family_counts = Counter(
        str(item.get("intent_family"))
        for item in section_intents
        if item.get("intent_family")
    )

    weighted_scores = {
        key: float(value)
        for key, value in direct[
            "intent_scores"
        ].items()
    }

    for intent_name, count in section_counts.items():
        if intent_name in weighted_scores:
            weighted_scores[intent_name] += (
                count * 1.25
            )

    ranked = sorted(
        weighted_scores.items(),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    )

    best_intent, best_score = ranked[0]
    second_score = (
        ranked[1][1]
        if len(ranked) > 1
        else 0.0
    )

    margin = round(
        best_score - second_score,
        3,
    )

    if best_intent in _CONTENT_INTENT_RULES:
        rule = _CONTENT_INTENT_RULES[
            best_intent
        ]
        family = rule["family"]
        reader_goal = rule["reader_goal"]
    else:
        family = "informational"
        reader_goal = (
            "understand general information "
            "about the subject"
        )

    confidence = 0.50
    confidence += min(best_score, 15.0) * 0.025
    confidence += min(max(margin, 0.0), 6.0) * 0.02
    confidence = round(
        min(confidence, 0.96),
        3,
    )

    if margin < 1.25:
        ambiguity_status = "AMBIGUOUS"
    elif margin < 3.0:
        ambiguity_status = "MIXED"
    else:
        ambiguity_status = "CLEAR"

    return {
        "article_id":
            article.get("article_id"),
        "article_title":
            title,
        "content_intent":
            best_intent,
        "intent_family":
            family,
        "reader_goal":
            reader_goal,
        "intent_confidence":
            confidence,
        "ambiguity_status":
            ambiguity_status,
        "score_margin":
            margin,
        "intent_scores":
            {
                key: round(value, 3)
                for key, value in weighted_scores.items()
            },
        "section_intent_counts":
            dict(section_counts),
        "section_family_counts":
            dict(section_family_counts),
        "supporting_section_count":
            len(section_intents),
        "raw_article_text_persisted":
            False,
    }



_LINK_INTENT_BY_CONTENT_INTENT = {
    "definition_or_overview":
        "DEFINITION_SUPPORT",
    "explanation":
        "CONTEXT_EXPANSION",
    "process_or_instruction":
        "PROCESS_SUPPORT",
    "comparison_or_evaluation":
        "COMPARISON_SUPPORT",
    "risk_or_safety":
        "RISK_SAFETY_SUPPORT",
    "measurement_or_monitoring":
        "EVIDENCE_SUPPORT",
    "practical_application":
        "PRACTICAL_APPLICATION_EXPANSION",
    "summary_or_conclusion":
        "RELATED_CONCEPT_EXPANSION",
    "general_information":
        "GENERAL_CONTEXT_SUPPORT",
}


_ANCHOR_PURPOSE_BY_LINK_INTENT = {
    "DEFINITION_SUPPORT":
        "TERM_CLARIFICATION",
    "CONTEXT_EXPANSION":
        "CONCEPT_DEEPENING",
    "PROCESS_SUPPORT":
        "PROCEDURAL_GUIDANCE",
    "EVIDENCE_SUPPORT":
        "EVIDENCE_CONTEXT",
    "COMPARISON_SUPPORT":
        "COMPARISON_REFERENCE",
    "RISK_SAFETY_SUPPORT":
        "RISK_CONTEXT",
    "RELATED_CONCEPT_EXPANSION":
        "RELATED_CONCEPT_DISCOVERY",
    "PRACTICAL_APPLICATION_EXPANSION":
        "APPLICATION_DEEPENING",
    "REFERENCE_SUPPORT":
        "REFERENCE_LOOKUP",
    "GENERAL_CONTEXT_SUPPORT":
        "GENERAL_CONTEXT",
}


def _section_intents_by_id_v1(
    section_intents: list[Mapping[str, Any]],
) -> dict[str, Mapping[str, Any]]:
    result = {}

    for item in section_intents:
        section_id = str(
            item.get("section_id") or ""
        ).strip()

        if section_id:
            result[section_id] = item

    return result


def build_link_intents_v1(
    phrase_neighborhood_result: Mapping[str, Any],
    section_intents: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Classify the semantic linking purpose of each neighborhood by section."""

    section_map = _section_intents_by_id_v1(
        section_intents
    )

    link_intents: list[dict[str, Any]] = []

    for neighborhood in phrase_neighborhood_result.get(
        "neighborhoods",
        [],
    ):
        if not isinstance(neighborhood, Mapping):
            raise TopicIntentIntelligenceError(
                "Invalid phrase neighborhood record."
            )

        left = str(
            neighborhood.get("left_canonical_text") or ""
        ).strip()

        right = str(
            neighborhood.get("right_canonical_text") or ""
        ).strip()

        neighborhood_id = str(
            neighborhood.get("neighborhood_id") or ""
        ).strip()

        section_ids = neighborhood.get(
            "shared_section_ids"
        )

        if (
            not left
            or not right
            or not neighborhood_id
            or not isinstance(section_ids, list)
        ):
            raise TopicIntentIntelligenceError(
                "Phrase neighborhood lacks link-intent evidence."
            )

        for section_id in section_ids:
            section_id = str(section_id)

            section_intent = section_map.get(
                section_id
            )

            if not isinstance(
                section_intent,
                Mapping,
            ):
                continue

            content_intent = str(
                section_intent.get(
                    "content_intent"
                )
                or "general_information"
            )

            link_intent = (
                _LINK_INTENT_BY_CONTENT_INTENT.get(
                    content_intent,
                    "GENERAL_CONTEXT_SUPPORT",
                )
            )

            section_confidence = float(
                section_intent.get(
                    "intent_confidence",
                    0.0,
                )
            )

            neighborhood_confidence = float(
                neighborhood.get(
                    "neighborhood_confidence",
                    0.0,
                )
            )

            confidence = round(
                min(
                    0.99,
                    (
                        section_confidence * 0.55
                        + neighborhood_confidence * 0.45
                    ),
                ),
                3,
            )

            link_intents.append({
                "neighborhood_id":
                    neighborhood_id,
                "section_id":
                    section_id,
                "section_title":
                    section_intent.get(
                        "section_title"
                    ),
                "left_canonical_text":
                    left,
                "right_canonical_text":
                    right,
                "section_content_intent":
                    content_intent,
                "link_intent":
                    link_intent,
                "link_intent_confidence":
                    confidence,
                "section_intent_confidence":
                    section_confidence,
                "neighborhood_confidence":
                    neighborhood_confidence,
                "shared_paragraph_count":
                    neighborhood.get(
                        "shared_paragraph_count"
                    ),
                "shared_paragraph_ids":
                    list(
                        neighborhood.get(
                            "shared_paragraph_ids"
                        )
                        or []
                    ),
                "target_selected":
                    False,
                "url_selected":
                    False,
                "link_type_selected":
                    False,
                "highlight_color_selected":
                    False,
            })

    return link_intents


def build_anchor_purposes_v1(
    link_intents: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Derive article-local anchor-purpose roles from certified link intent."""

    anchors: list[dict[str, Any]] = []

    seen = set()

    for link_intent in link_intents:
        if not isinstance(link_intent, Mapping):
            raise TopicIntentIntelligenceError(
                "Invalid link-intent record."
            )

        section_id = str(
            link_intent.get("section_id") or ""
        ).strip()

        neighborhood_id = str(
            link_intent.get("neighborhood_id")
            or ""
        ).strip()

        intent = str(
            link_intent.get("link_intent")
            or "GENERAL_CONTEXT_SUPPORT"
        )

        purpose = (
            _ANCHOR_PURPOSE_BY_LINK_INTENT.get(
                intent,
                "GENERAL_CONTEXT",
            )
        )

        confidence = float(
            link_intent.get(
                "link_intent_confidence",
                0.0,
            )
        )

        for side in (
            "left_canonical_text",
            "right_canonical_text",
        ):
            anchor_text = str(
                link_intent.get(side) or ""
            ).strip()

            if not anchor_text:
                continue

            key = (
                neighborhood_id,
                section_id,
                anchor_text,
                purpose,
            )

            if key in seen:
                continue

            seen.add(key)

            anchors.append({
                "neighborhood_id":
                    neighborhood_id,
                "section_id":
                    section_id,
                "section_title":
                    link_intent.get(
                        "section_title"
                    ),
                "anchor_text":
                    anchor_text,
                "anchor_purpose":
                    purpose,
                "supporting_link_intent":
                    intent,
                "anchor_purpose_confidence":
                    round(confidence, 3),
                "phrase_selected_for_linking":
                    False,
                "target_selected":
                    False,
                "url_selected":
                    False,
                "link_type_selected":
                    False,
                "highlight_color_selected":
                    False,
            })

    return anchors



def aggregate_intent_evidence_v1(
    link_intents: list[Mapping[str, Any]],
    anchor_purposes: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Aggregate contextual intent evidence without making linking decisions."""

    link_intent_counts = Counter(
        str(item.get("link_intent"))
        for item in link_intents
        if item.get("link_intent")
    )

    anchor_purpose_counts = Counter(
        str(item.get("anchor_purpose"))
        for item in anchor_purposes
        if item.get("anchor_purpose")
    )

    section_link_intent_counts: dict[str, Counter] = {}

    for item in link_intents:
        section_id = str(
            item.get("section_id") or ""
        ).strip()

        intent = str(
            item.get("link_intent") or ""
        ).strip()

        if not section_id or not intent:
            continue

        section_link_intent_counts.setdefault(
            section_id,
            Counter(),
        )[intent] += 1

    anchor_groups: dict[
        str,
        list[Mapping[str, Any]],
    ] = {}

    for item in anchor_purposes:
        anchor_text = str(
            item.get("anchor_text") or ""
        ).strip()

        if not anchor_text:
            continue

        anchor_groups.setdefault(
            anchor_text,
            [],
        ).append(item)

    anchor_profiles: list[dict[str, Any]] = []

    for anchor_text, records in anchor_groups.items():
        # Canonical aggregation unit:
        # one anchor-purpose vote per section. Multiple neighborhoods in
        # the same section remain supporting evidence but must not
        # multiply the contextual intent vote.
        contextual_units: dict[
            tuple[str, str],
            list[Mapping[str, Any]],
        ] = {}

        for item in records:
            section_id = str(
                item.get("section_id") or ""
            ).strip()

            purpose = str(
                item.get("anchor_purpose") or ""
            ).strip()

            if not section_id or not purpose:
                continue

            contextual_units.setdefault(
                (section_id, purpose),
                [],
            ).append(item)

        purpose_counts = Counter(
            purpose
            for (_, purpose)
            in contextual_units.keys()
        )

        link_counts = Counter()

        contextual_confidences: list[float] = []

        for unit_records in contextual_units.values():
            unit_link_intents = {
                str(item.get("supporting_link_intent"))
                for item in unit_records
                if item.get("supporting_link_intent")
            }

            for intent in unit_link_intents:
                link_counts[intent] += 1

            unit_confidences = [
                float(
                    item.get(
                        "anchor_purpose_confidence",
                        0.0,
                    )
                )
                for item in unit_records
            ]

            if unit_confidences:
                contextual_confidences.append(
                    max(unit_confidences)
                )

        section_ids = sorted({
            str(item.get("section_id"))
            for item in records
            if item.get("section_id")
        })

        neighborhood_ids = sorted({
            str(item.get("neighborhood_id"))
            for item in records
            if item.get("neighborhood_id")
        })

        confidences = contextual_confidences

        ranked_purposes = purpose_counts.most_common()

        top_purpose = (
            ranked_purposes[0][0]
            if ranked_purposes
            else "GENERAL_CONTEXT"
        )

        primary_count = (
            ranked_purposes[0][1]
            if ranked_purposes
            else 0
        )

        second_count = (
            ranked_purposes[1][1]
            if len(ranked_purposes) > 1
            else 0
        )

        total_evidence = sum(
            purpose_counts.values()
        )

        primary_share = (
            primary_count / total_evidence
            if total_evidence
            else 0.0
        )

        top_is_tied = (
            len(ranked_purposes) > 1
            and primary_count == second_count
        )

        if len(purpose_counts) <= 1:
            ambiguity_status = "CONSISTENT"
            primary_purpose = top_purpose
        elif top_is_tied and len(purpose_counts) == 2:
            ambiguity_status = "MIXED"
            primary_purpose = "MIXED_PURPOSE"
        elif top_is_tied:
            ambiguity_status = "MULTI_PURPOSE"
            primary_purpose = "MULTI_PURPOSE"
        elif primary_share >= 0.75:
            ambiguity_status = "DOMINANT_WITH_VARIANTS"
            primary_purpose = top_purpose
        elif primary_share >= 0.50:
            ambiguity_status = "MIXED"
            primary_purpose = top_purpose
        else:
            ambiguity_status = "MULTI_PURPOSE"
            primary_purpose = "MULTI_PURPOSE"

        mean_confidence = (
            sum(confidences) / len(confidences)
            if confidences
            else 0.0
        )

        confidence = round(
            min(
                0.99,
                mean_confidence
                * (
                    0.75
                    + 0.25 * primary_share
                ),
            ),
            3,
        )

        anchor_profiles.append({
            "anchor_text":
                anchor_text,
            "primary_anchor_purpose":
                primary_purpose,
            "anchor_purpose_confidence":
                confidence,
            "ambiguity_status":
                ambiguity_status,
            "primary_purpose_share":
                round(primary_share, 3),
            "purpose_counts":
                dict(purpose_counts),
            "supporting_link_intent_counts":
                dict(link_counts),
            "section_ids":
                section_ids,
            "neighborhood_ids":
                neighborhood_ids,
            "contextual_evidence_count":
                len(contextual_units),
            "neighborhood_evidence_count":
                len(records),
            "evidence_record_count":
                len(contextual_units),
            "phrase_selected_for_linking":
                False,
            "target_selected":
                False,
            "url_selected":
                False,
            "link_type_selected":
                False,
            "highlight_color_selected":
                False,
        })

    anchor_profiles.sort(
        key=lambda item: (
            -item["evidence_record_count"],
            -item["anchor_purpose_confidence"],
            item["anchor_text"],
        )
    )

    return {
        "link_intent_counts":
            dict(link_intent_counts),
        "anchor_purpose_counts":
            dict(anchor_purpose_counts),
        "section_link_intent_counts": {
            section_id: dict(counts)
            for section_id, counts
            in section_link_intent_counts.items()
        },
        "article_anchor_profile_count":
            len(anchor_profiles),
        "article_anchor_profiles":
            anchor_profiles,
        "raw_link_intent_record_count":
            len(link_intents),
        "raw_anchor_purpose_record_count":
            len(anchor_purposes),
        "aggregation_scope":
            "ARTICLE_LOCAL_ONLY",
        "linking_decisions_performed":
            False,
    }



def run_topic_intent_intelligence_v1(
    phrase_neighborhood_result: Mapping[str, Any],
    runtime_reader_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Run canonical Phase 4.6.4 Topic Intent Intelligence."""

    intake = validate_topic_intent_intake_v1(
        phrase_neighborhood_result,
        runtime_reader_result,
    )

    section_intents = build_section_content_intents_v1(
        runtime_reader_result,
    )

    article_intent = build_article_content_intent_v1(
        runtime_reader_result,
        section_intents,
    )

    link_intents = build_link_intents_v1(
        phrase_neighborhood_result,
        section_intents,
    )

    anchor_purposes = build_anchor_purposes_v1(
        link_intents,
    )

    aggregation = aggregate_intent_evidence_v1(
        link_intents,
        anchor_purposes,
    )

    if len(section_intents) != intake["section_count"]:
        raise TopicIntentIntelligenceError(
            "Section intent count does not match canonical section count."
        )

    if article_intent.get("article_id") != intake["article_id"]:
        raise TopicIntentIntelligenceError(
            "Article intent identity mismatch."
        )

    if aggregation.get("aggregation_scope") != "ARTICLE_LOCAL_ONLY":
        raise TopicIntentIntelligenceError(
            "Intent aggregation escaped article-local scope."
        )

    if aggregation.get("linking_decisions_performed") is not False:
        raise TopicIntentIntelligenceError(
            "4.6.4 must not perform linking decisions."
        )

    return {
        "schema_version":
            "topic_intent_intelligence_result_v1",
        "engine_version":
            TOPIC_INTENT_INTELLIGENCE_VERSION,
        "phase":
            "4.6.4",
        "status":
            "TOPIC_INTENT_INTELLIGENCE_COMPLETE",
        "workspace_id":
            intake.get("workspace_id"),
        "document_id":
            intake.get("document_id"),
        "source_type":
            intake.get("source_type"),
        "source_id":
            intake.get("source_id"),
        "content_hash":
            intake.get("content_hash"),
        "body_ref":
            intake.get("body_ref"),
        "article_id":
            intake.get("article_id"),
        "title":
            intake.get("title"),
        "final_primary_topic":
            intake.get("final_primary_topic"),
        "article_content_intent":
            article_intent,
        "section_content_intents":
            section_intents,
        "link_intents":
            link_intents,
        "anchor_purposes":
            anchor_purposes,
        "intent_aggregation":
            aggregation,
        "processing_boundaries": {
            "article_local_only":
                True,
            "content_intent_inferred":
                True,
            "link_intent_inferred":
                True,
            "anchor_purpose_inferred":
                True,
            "section_evidence_intelligence_performed":
                False,
            "logical_reasoning_performed":
                False,
            "causal_reasoning_performed":
                False,
            "analogical_reasoning_performed":
                False,
            "ontology_alignment_performed":
                False,
            "semantic_memory_write_performed":
                False,
            "learning_performed":
                False,
            "link_scoring_performed":
                False,
            "target_resolution_performed":
                False,
            "link_type_selected":
                False,
            "url_selected":
                False,
            "highlighting_performed":
                False,
            "editor_action_performed":
                False,
        },
        "persistence_policy":
            "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE",
        "next_stage":
            "section_evidence_intelligence",
    }


def validate_topic_intent_intake_v1(
    phrase_neighborhood_result: Mapping[str, Any],
    runtime_reader_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate the canonical 4.6.3 + 4.6.1 -> 4.6.4 handoff."""

    if not isinstance(phrase_neighborhood_result, Mapping):
        raise TopicIntentIntelligenceError(
            "phrase_neighborhood_result must be a mapping."
        )

    if not isinstance(runtime_reader_result, Mapping):
        raise TopicIntentIntelligenceError(
            "runtime_reader_result must be a mapping."
        )

    if (
        phrase_neighborhood_result.get("schema_version")
        != "phrase_neighborhood_intelligence_result_v1"
    ):
        raise TopicIntentIntelligenceError(
            "Unsupported Phrase Neighborhood Intelligence result schema."
        )

    if (
        phrase_neighborhood_result.get("status")
        != "PHRASE_NEIGHBORHOOD_INTELLIGENCE_COMPLETE"
    ):
        raise TopicIntentIntelligenceError(
            "Phrase Neighborhood Intelligence is not complete."
        )

    if phrase_neighborhood_result.get("phase") != "4.6.3":
        raise TopicIntentIntelligenceError(
            "Phrase Neighborhood Intelligence phase is invalid."
        )

    if (
        phrase_neighborhood_result.get("next_stage")
        != "topic_intent_intelligence"
    ):
        raise TopicIntentIntelligenceError(
            "Phrase Neighborhood Intelligence is not authorized to hand "
            "off to Topic Intent Intelligence."
        )

    if (
        phrase_neighborhood_result.get("canonical_neighborhood_rule")
        != "SHARED_CANONICAL_PARAGRAPH_REQUIRED"
    ):
        raise TopicIntentIntelligenceError(
            "Phrase Neighborhood Intelligence canonical boundary is invalid."
        )

    phrase_boundaries = phrase_neighborhood_result.get(
        "processing_boundaries"
    )

    if not isinstance(phrase_boundaries, Mapping):
        raise TopicIntentIntelligenceError(
            "Phrase Neighborhood Intelligence boundary evidence is missing."
        )

    if phrase_boundaries.get("article_local_only") is not True:
        raise TopicIntentIntelligenceError(
            "Phrase Neighborhood Intelligence is not article-local."
        )

    if (
        phrase_boundaries.get("topic_intent_intelligence_performed")
        is not False
    ):
        raise TopicIntentIntelligenceError(
            "Topic Intent Intelligence was already performed."
        )

    if (
        phrase_neighborhood_result.get("persistence_policy")
        != "ARTICLE_LOCAL_TRANSIENT_INTELLIGENCE"
    ):
        raise TopicIntentIntelligenceError(
            "Unsupported phrase-neighborhood persistence policy."
        )

    if (
        runtime_reader_result.get("schema_version")
        != "semantic_intelligence_runtime_reader_result_v1"
    ):
        raise TopicIntentIntelligenceError(
            "Unsupported Runtime Reader result schema."
        )

    if (
        runtime_reader_result.get("status")
        != "SEMANTIC_RUNTIME_READING_COMPLETE"
    ):
        raise TopicIntentIntelligenceError(
            "Semantic Intelligence Runtime Reader is not complete."
        )

    runtime_model = runtime_reader_result.get(
        "semantic_reading_model"
    )

    if not isinstance(runtime_model, Mapping):
        raise TopicIntentIntelligenceError(
            "Semantic reading model is missing."
        )

    if runtime_model.get("structure_source") != "canonical_uucd":
        raise TopicIntentIntelligenceError(
            "Semantic reading model is not based on canonical UUCD structure."
        )

    validation = runtime_model.get("validation")

    if (
        not isinstance(validation, Mapping)
        or validation.get("valid") is not True
    ):
        raise TopicIntentIntelligenceError(
            "Semantic reading structure is not certified valid."
        )

    sections = runtime_model.get("sections")
    blocks = runtime_model.get("blocks")

    if not isinstance(sections, list) or not sections:
        raise TopicIntentIntelligenceError(
            "Canonical section structure is missing."
        )

    if not isinstance(blocks, list) or not blocks:
        raise TopicIntentIntelligenceError(
            "Canonical block structure is missing."
        )

    phrase_article_id = str(
        phrase_neighborhood_result.get("article_id") or ""
    ).strip()

    runtime_article = runtime_model.get("article")

    if not isinstance(runtime_article, Mapping):
        raise TopicIntentIntelligenceError(
            "Runtime article identity is missing."
        )

    runtime_article_id = str(
        runtime_article.get("article_id") or ""
    ).strip()

    if (
        not phrase_article_id
        or not runtime_article_id
        or phrase_article_id != runtime_article_id
    ):
        raise TopicIntentIntelligenceError(
            "Phrase Neighborhood and Runtime Reader article identities "
            "do not match."
        )

    identity_fields = (
        "workspace_id",
        "document_id",
        "source_type",
        "source_id",
        "content_hash",
        "body_ref",
    )

    for field in identity_fields:
        left = phrase_neighborhood_result.get(field)
        right = runtime_reader_result.get(field)

        if left != right:
            raise TopicIntentIntelligenceError(
                f"Identity mismatch for {field}."
            )

    return {
        "schema_version":
            "topic_intent_intake_v1",
        "phase":
            "4.6.4",
        "status":
            "TOPIC_INTENT_INTAKE_ACCEPTED",
        "workspace_id":
            phrase_neighborhood_result.get("workspace_id"),
        "document_id":
            phrase_neighborhood_result.get("document_id"),
        "source_type":
            phrase_neighborhood_result.get("source_type"),
        "source_id":
            phrase_neighborhood_result.get("source_id"),
        "content_hash":
            phrase_neighborhood_result.get("content_hash"),
        "body_ref":
            phrase_neighborhood_result.get("body_ref"),
        "article_id":
            phrase_article_id,
        "title":
            phrase_neighborhood_result.get("title"),
        "final_primary_topic":
            phrase_neighborhood_result.get("final_primary_topic"),
        "section_count":
            len(sections),
        "block_count":
            len(blocks),
        "neighborhood_count":
            phrase_neighborhood_result.get("neighborhood_count"),
        "intake_authorized":
            True,
        "next_stage":
            "article_content_intent_intelligence",
    }


__all__ = [
    "TOPIC_INTENT_INTELLIGENCE_VERSION",
    "TopicIntentIntelligenceError",
    "aggregate_intent_evidence_v1",
    "build_anchor_purposes_v1",
    "build_article_content_intent_v1",
    "build_link_intents_v1",
    "build_section_content_intents_v1",
    "run_topic_intent_intelligence_v1",
    "validate_topic_intent_intake_v1",
]
