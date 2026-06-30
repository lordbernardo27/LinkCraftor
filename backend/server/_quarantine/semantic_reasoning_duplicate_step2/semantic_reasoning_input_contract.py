from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.server.stores.yellow_semantic_phrase_registry import (
    transition_yellow_phrase_state_v1,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    return f"{prefix}_{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:12]}"


def _workspace_semantic_lookup_v1(normalized_text: str) -> Dict[str, Any] | None:
    """
    Temporary workspace-style semantic lookup.
    Later this will query:
    - Semantic Workspace Learner
    - Memory Engine
    - Learning Engine
    - Certified Semantic Learning Packs
    """

    semantic_map = {
        "hypertension": {
            "semantic_object_id": "semantic_object_high_blood_pressure",
            "canonical_concept": "high blood pressure",
            "identity_confidence": 0.98,
            "identity_source": "semantic_workspace_memory",
            "semantic_bridge": {
                "bridge_type": "alias_equivalence",
                "from": "hypertension",
                "to": "high blood pressure",
                "confidence": 0.98,
            },
        },
        "high blood pressure": {
            "semantic_object_id": "semantic_object_high_blood_pressure",
            "canonical_concept": "high blood pressure",
            "identity_confidence": 0.97,
            "identity_source": "semantic_workspace_memory",
            "semantic_bridge": {
                "bridge_type": "direct_canonical_match",
                "from": "high blood pressure",
                "to": "high blood pressure",
                "confidence": 0.97,
            },
        },
        "blood pressure monitoring": {
            "semantic_object_id": "semantic_object_blood_pressure_monitoring",
            "canonical_concept": "blood pressure monitoring",
            "identity_confidence": 0.96,
            "identity_source": "semantic_workspace_memory",
            "semantic_bridge": {
                "bridge_type": "direct_canonical_match",
                "from": "blood pressure monitoring",
                "to": "blood pressure monitoring",
                "confidence": 0.96,
            },
        },
        "morning sickness": {
            "semantic_object_id": "semantic_object_morning_sickness",
            "canonical_concept": "morning sickness",
            "identity_confidence": 0.94,
            "identity_source": "semantic_workspace_memory",
            "semantic_bridge": {
                "bridge_type": "direct_canonical_match",
                "from": "morning sickness",
                "to": "morning sickness",
                "confidence": 0.94,
            },
        },
    }

    return semantic_map.get(normalized_text)


def reason_yellow_semantic_phrase_v1(
    yellow_phrase: Dict[str, Any],
    *,
    workspace_id: str | None = None,
) -> Dict[str, Any]:
    phrase_id = yellow_phrase.get("phrase_id")
    normalized_text = yellow_phrase.get("normalized_text")

    working_phrase = transition_yellow_phrase_state_v1(
        yellow_phrase,
        "reasoning_pending",
        source="semantic_reasoning_engine",
        note="Phrase received by Semantic Reasoning Engine.",
    )

    match = _workspace_semantic_lookup_v1(normalized_text)

    if not match:
        working_phrase = transition_yellow_phrase_state_v1(
            working_phrase,
            "rejected",
            source="semantic_reasoning_engine",
            note="No semantic identity found for phrase.",
        )

        working_phrase["semantic_identity"] = {
            "identity_status": "rejected",
            "semantic_object_id": None,
            "canonical_concept": None,
            "identity_confidence": 0.0,
            "identity_source": "semantic_reasoning_engine",
            "rejection_reason": "No semantic identity found.",
        }

        working_phrase["semantic_interpretation"] = {
            "interpretation_status": "rejected",
            "bridge_type": None,
            "bridge_path": [],
            "interpretation_reason": "No semantic bridge or canonical concept was found.",
            "evidence": [],
        }

        working_phrase["workspace_snapshot"] = {
            "workspace_id": workspace_id or working_phrase.get("workspace_id"),
            "semantic_map_version": "semantic_map_v2",
            "memory_revision": "memory_engine_current",
            "learning_revision": "learning_engine_current",
            "reasoning_revision": "semantic_reasoning_step_2B",
        }

        working_phrase["confidence_breakdown"] = {
            "alias_confidence": 0.0,
            "context_confidence": 0.0,
            "relationship_confidence": 0.0,
            "memory_confidence": 0.0,
            "learning_confidence": 0.0,
            "overall_confidence": 0.0,
        }

        working_phrase["reasoning_result"] = {
            "reasoning_id": _stable_id("semantic_reasoning", phrase_id, normalized_text, "rejected"),
            "reasoned_at": _now_iso(),
            "semantic_match_found": False,
            "eligible_for_target_discovery": False,
            "confidence": 0.0,
        }

        return working_phrase

    bridge = match["semantic_bridge"]
    bridge_type = bridge.get("bridge_type")

    confidence_breakdown = {
        "alias_confidence": bridge.get("confidence", 0.0) if bridge_type == "alias_equivalence" else 0.0,
        "context_confidence": 0.86,
        "relationship_confidence": bridge.get("confidence", match["identity_confidence"]),
        "memory_confidence": match["identity_confidence"],
        "learning_confidence": round(max(match["identity_confidence"] - 0.02, 0.0), 2),
        "overall_confidence": match["identity_confidence"],
    }

    working_phrase["semantic_identity"] = {
        "identity_status": "bound",
        "semantic_object_id": match["semantic_object_id"],
        "canonical_concept": match["canonical_concept"],
        "identity_confidence": match["identity_confidence"],
        "identity_source": match["identity_source"],
    }

    working_phrase["semantic_interpretation"] = {
        "interpretation_status": "interpreted",
        "bridge_type": bridge_type,
        "bridge_path": [
            bridge.get("from"),
            bridge.get("to"),
        ],
        "interpretation_reason": (
            f"Phrase '{normalized_text}' was mapped to canonical concept "
            f"'{match['canonical_concept']}' using {bridge_type}."
        ),
        "evidence": [
            {
                "evidence_type": "semantic_bridge",
                "bridge": bridge,
                "confidence": bridge.get("confidence"),
            },
            {
                "evidence_type": "workspace_memory",
                "source": match["identity_source"],
                "confidence": match["identity_confidence"],
            },
        ],
    }

    working_phrase["workspace_snapshot"] = {
        "workspace_id": workspace_id or working_phrase.get("workspace_id"),
        "semantic_map_version": "semantic_map_v2",
        "memory_revision": "memory_engine_current",
        "learning_revision": "learning_engine_current",
        "reasoning_revision": "semantic_reasoning_step_2B",
    }

    working_phrase["confidence_breakdown"] = confidence_breakdown

    recommended_topics = []

    primary_topic = {
        "topic_id": _stable_id("target_topic", match["canonical_concept"], "primary"),
        "canonical_concept": match["canonical_concept"],
        "relationship": "primary",
        "source_phrase": normalized_text,
        "confidence": match["identity_confidence"],
        "target_search_strategy": {
            "priority": 1,
            "match_mode": "canonical",
            "allow_alias_expansion": True,
            "allow_parent_concepts": True,
            "allow_child_concepts": True,
            "allow_related_concepts": True,
        },
        "target_search_plan": [
            {
                "provider": {
                    "provider_id": "provider_active_target_set",
                    "provider_type": "internal_index",
                    "provider_name": "Active Target Set",
                },
                "priority": 1,
                "match_mode": "canonical",
                "required": True,
            },
            {
                "provider": {
                    "provider_id": "provider_topic_clusters",
                    "provider_type": "semantic_cluster_index",
                    "provider_name": "Topic Clusters",
                },
                "priority": 2,
                "match_mode": "canonical",
                "required": False,
            },
            {
                "provider": {
                    "provider_id": "provider_section_clusters",
                    "provider_type": "structural_cluster_index",
                    "provider_name": "Section Clusters",
                },
                "priority": 3,
                "match_mode": "semantic",
                "required": False,
            },
        ],
        "search_intent": {
            "goal": "discover_best_target_url",
            "expected_output": "candidate_urls",
            "minimum_candidates": 1,
            "maximum_candidates": 25,
        },
    }
    recommended_topics.append(primary_topic)

    if normalized_text and normalized_text != match["canonical_concept"]:
        alias_topic = {
            "topic_id": _stable_id("target_topic", normalized_text, "alias"),
            "canonical_concept": normalized_text,
            "relationship": "alias",
            "source_phrase": normalized_text,
            "confidence": bridge.get("confidence", match["identity_confidence"]),
            "target_search_strategy": {
                "priority": 2,
                "match_mode": "alias",
                "allow_alias_expansion": False,
                "allow_parent_concepts": False,
                "allow_child_concepts": False,
                "allow_related_concepts": False,
            },
            "target_search_plan": [
                {
                    "provider": {
                        "provider_id": "provider_active_target_set",
                        "provider_type": "internal_index",
                        "provider_name": "Active Target Set",
                    },
                    "priority": 1,
                    "match_mode": "alias",
                    "required": True,
                },
                {
                    "provider": {
                        "provider_id": "provider_topic_clusters",
                        "provider_type": "semantic_cluster_index",
                        "provider_name": "Topic Clusters",
                    },
                    "priority": 2,
                    "match_mode": "alias",
                    "required": False,
                },
            ],
            "search_intent": {
                "goal": "discover_best_target_url",
                "expected_output": "candidate_urls",
                "minimum_candidates": 1,
                "maximum_candidates": 15,
            },
        }
        recommended_topics.append(alias_topic)

    working_phrase["reasoning_result"] = {
        "reasoning_id": _stable_id(
            "semantic_reasoning",
            phrase_id,
            normalized_text,
            match["canonical_concept"],
        ),
        "reasoned_at": _now_iso(),
        "semantic_match_found": True,
        "eligible_for_target_discovery": True,
        "confidence": confidence_breakdown["overall_confidence"],
        "recommended_target_topics": recommended_topics,
        "boundary_rule": (
            "Semantic Reasoning Engine resolves phrase semantic identity and interpretation only. "
            "It does not query target URLs, choose targets, create highlights, write memory, or generate explanations."
        ),
    }

    working_phrase["routing"]["requires_target_discovery"] = True
    working_phrase["routing"]["send_to_yellow_resolver"] = False
    working_phrase["routing"]["requires_explainability"] = False

    working_phrase = transition_yellow_phrase_state_v1(
        working_phrase,
        "reasoned",
        source="semantic_reasoning_engine",
        note="Semantic identity resolved and phrase is ready for target discovery.",
    )

    return working_phrase



def _group_semantic_reasoning_output_v1(phrase: Dict[str, Any]) -> Dict[str, Any]:
    grouped = dict(phrase)

    grouped["semantic_reasoning"] = {
        "semantic_identity": grouped.pop("semantic_identity", {}),
        "semantic_interpretation": grouped.pop("semantic_interpretation", {}),
        "workspace_snapshot": grouped.pop("workspace_snapshot", {}),
        "confidence_breakdown": grouped.pop("confidence_breakdown", {}),
        "reasoning_result": grouped.pop("reasoning_result", {}),
    }

    return grouped


def reason_yellow_semantic_phrase_registry_v1(
    phrase_registry: Dict[str, Any],
) -> Dict[str, Any]:
    reasoned_phrases = []

    for phrase in phrase_registry.get("yellow_semantic_phrases", []):
        reasoned_phrase = reason_yellow_semantic_phrase_v1(
            phrase,
            workspace_id=phrase_registry.get("workspace_id"),
        )

        # Safety normalization: ensure Step 2C always returns grouped semantic_reasoning.
        if "semantic_reasoning" not in reasoned_phrase:
            reasoned_phrase = _group_semantic_reasoning_output_v1(reasoned_phrase)

        reasoned_phrases.append(reasoned_phrase)

    bound_count = 0
    rejected_count = 0

    for phrase in reasoned_phrases:
        sr = phrase.get("semantic_reasoning", {})
        identity = sr.get("semantic_identity", {})

        status = identity.get("identity_status")

        if status == "bound":
            bound_count += 1
        elif status == "rejected":
            rejected_count += 1

    return {
        "schema_version": "semantic_reasoning_input_contract_v1",
        "phase": "semantic_linking_execution.step_2",
        "patch": "step_2G",
        "name": "Semantic Reasoning Engine Input Contract",
        "created_at": _now_iso(),
        "workspace_id": phrase_registry.get("workspace_id"),
        "document": phrase_registry.get("document", {}),
        "source_registry": {
            "schema_version": phrase_registry.get("schema_version"),
            "phase": phrase_registry.get("phase"),
            "patch": phrase_registry.get("patch"),
        },
        "reasoned_yellow_phrases": reasoned_phrases,
        "metadata": {
            "input_phrase_count": len(phrase_registry.get("yellow_semantic_phrases", [])),
            "reasoned_phrase_count": len(reasoned_phrases),
            "bound_identity_count": bound_count,
            "rejected_identity_count": rejected_count,
            "semantic_interpretation_enabled": True,
            "workspace_snapshot_enabled": True,
            "confidence_breakdown_enabled": True,
            "grouped_reasoning_output": True,
            "structured_recommended_target_topics": True,
            "target_search_strategy_enabled": True,
            "target_search_plan_enabled": True,
            "typed_search_providers_enabled": True,
            "search_intent_enabled": True,
        },
        "boundary_rule": (
            "Semantic Reasoning Engine Input Contract resolves yellow phrase semantic identity and interpretation only. "
            "It does not perform target discovery, yellow resolving, blue resolving, final highlighting, memory writing, or explainability."
        ),
    }


def save_semantic_reasoning_input_contract_v1(
    phrase_registry: Dict[str, Any],
    output_path: str | Path,
) -> Dict[str, Any]:
    model = reason_yellow_semantic_phrase_registry_v1(phrase_registry)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(model, indent=2, ensure_ascii=False), encoding="utf-8")
    return model


def explain_semantic_reasoning_input_contract_v1() -> Dict[str, Any]:
    return {
        "step": "Step 2",
        "patch": "step_2G",
        "name": "Semantic Reasoning Engine Input Contract",
        "purpose": "Receive yellow semantic phrase objects and resolve their semantic identity before target discovery.",
        "input": "Yellow Semantic Phrase Registry Step 1D",
        "output": "Reasoned yellow phrase objects with semantic_reasoning namespace populated",
        "does": [
            "receives yellow phrase objects",
            "reads phrase_id, normalized_text, editor context, and lifecycle state",
            "consults workspace-style semantic knowledge",
            "resolves canonical concept",
            "populates semantic_reasoning.semantic_identity",
            "separates semantic_reasoning.semantic_interpretation from identity",
            "adds semantic_reasoning semantic bridge path and interpretation evidence",
            "adds semantic_reasoning workspace knowledge snapshot",
            "adds semantic_reasoning confidence breakdown",
            "adds semantic_reasoning reasoning_result",
            "adds structured recommended target topics",
            "adds target search strategy to recommended topics",
            "adds scalable target search plan to recommended topics",
            "adds typed search providers to target search plan",
            "adds search intent to recommended topics",
            "moves phrase state from detected to reasoned",
            "marks phrase eligible for target discovery",
        ],
        "does_not": [
            "query active target sets",
            "choose target URLs",
            "perform yellow resolving",
            "perform blue resolving",
            "create final highlights",
            "write memory",
            "generate explanations",
        ],
    }
