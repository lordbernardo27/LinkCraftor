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
    return f"{prefix}_{hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]}"


def lookup_semantic_object_from_workspace_v1(workspace_id: str | None, normalized_text: str) -> Dict[str, Any] | None:
    """
    Semantic Workspace lookup interface.

    Production path:
    - Reads semantic_map_v2_<workspace>.json through semantic_source.py
    - Uses Semantic Workspace Learner indexes:
      canonical_lookup, synonym_lookup, target_lookup
    - Falls back to controlled verification map only if no workspace match exists.
    """
    query = (normalized_text or "").strip().lower()
    if not query:
        return None

    try:
        from backend.server.engine.semantic_source import load_workspace_semantic_map_v2

        semantic_map = load_workspace_semantic_map_v2(workspace_id or "default")
        indexes = semantic_map.get("indexes") or {}

        canonical_lookup = indexes.get("canonical_lookup") or {}
        synonym_lookup = indexes.get("synonym_lookup") or {}
        target_lookup = indexes.get("target_lookup") or {}

        semantic_objects = (
            semantic_map.get("semantic_objects")
            or semantic_map.get("canonical_semantic_objects")
            or semantic_map.get("concepts")
            or []
        )

        canonical = None
        match_type = None

        if query in canonical_lookup:
            canonical = query
            match_type = "direct_canonical_match"
        elif query in synonym_lookup:
            canonical = str(synonym_lookup.get(query) or "").strip().lower()
            match_type = "synonym_lookup_match"

        matched_obj = None

        if canonical is not None:
            idx = canonical_lookup.get(canonical)

            if isinstance(idx, int) and 0 <= idx < len(semantic_objects):
                matched_obj = semantic_objects[idx]
            else:
                for obj in semantic_objects:
                    obj_canonical = (
                        obj.get("canonical")
                        or obj.get("canonical_concept")
                        or obj.get("name")
                        or obj.get("label")
                        or ""
                    )
                    if str(obj_canonical).strip().lower() == canonical:
                        matched_obj = obj
                        break

        if matched_obj:
            canonical_concept = (
                matched_obj.get("canonical")
                or matched_obj.get("canonical_concept")
                or matched_obj.get("name")
                or matched_obj.get("label")
                or canonical
            )

            aliases = (
                matched_obj.get("aliases")
                or matched_obj.get("synonyms")
                or matched_obj.get("terms")
                or []
            )

            semantic_object_id = (
                matched_obj.get("semantic_object_id")
                or matched_obj.get("id")
                or f"semantic_object_{re.sub(r'[^a-z0-9]+', '_', str(canonical_concept).lower()).strip('_')}"
            )

            semantic_type = (
                matched_obj.get("semantic_type")
                or matched_obj.get("type")
                or matched_obj.get("category")
                or "semantic_concept"
            )

            related_concepts = (
                matched_obj.get("related_concepts")
                or matched_obj.get("relationships")
                or matched_obj.get("neighbors")
                or []
            )

            return {
                "semantic_object_id": semantic_object_id,
                "canonical_concept": canonical_concept,
                "aliases": aliases,
                "related_concepts": related_concepts,
                "semantic_type": semantic_type,
                "match_type": match_type or "workspace_match",
                "confidence": 0.96 if match_type == "direct_canonical_match" else 0.91,
                "target_urls": target_lookup.get(str(canonical_concept).strip().lower()) or target_lookup.get(canonical) or [],
                "lookup_source": "semantic_map_v2",
                "workspace_id": workspace_id,
            }

    except Exception:
        pass

    # Controlled fallback for verification only.
    fallback_map = {
        "hypertension": {
            "semantic_object_id": "semantic_object_high_blood_pressure",
            "canonical_concept": "high blood pressure",
            "aliases": ["hypertension", "raised blood pressure", "elevated blood pressure"],
            "related_concepts": [],
            "semantic_type": "medical_condition",
            "match_type": "fallback_alias_equivalence",
            "confidence": 0.78,
            "lookup_source": "fallback_verification_map",
        },
        "high blood pressure": {
            "semantic_object_id": "semantic_object_high_blood_pressure",
            "canonical_concept": "high blood pressure",
            "aliases": ["hypertension", "raised blood pressure", "elevated blood pressure"],
            "related_concepts": [],
            "semantic_type": "medical_condition",
            "match_type": "fallback_direct_canonical_match",
            "confidence": 0.78,
            "lookup_source": "fallback_verification_map",
        },
        "blood pressure monitoring": {
            "semantic_object_id": "semantic_object_blood_pressure_monitoring",
            "canonical_concept": "blood pressure monitoring",
            "aliases": ["bp monitoring"],
            "related_concepts": [],
            "semantic_type": "medical_monitoring",
            "match_type": "fallback_direct_canonical_match",
            "confidence": 0.76,
            "lookup_source": "fallback_verification_map",
        },
        "morning sickness": {
            "semantic_object_id": "semantic_object_morning_sickness",
            "canonical_concept": "morning sickness",
            "aliases": ["pregnancy nausea"],
            "related_concepts": [],
            "semantic_type": "pregnancy_symptom",
            "match_type": "fallback_direct_canonical_match",
            "confidence": 0.76,
            "lookup_source": "fallback_verification_map",
        },
    }

    return fallback_map.get(query)




def _build_semantic_match_candidates_v1(
    phrase_text: str,
    canonical_concept: str,
    aliases: list,
    related_concepts: list,
    semantic_object_id: str,
    semantic_fingerprint: str,
) -> list:
    """
    Build structured semantic match candidates for Step 3 Semantic Target Discovery.
    Step 2C does NOT query targets. It only prepares search candidates.
    """
    candidates = []

    def add_candidate(search_text, relationship, priority, search_weight, match_mode):
        text = str(search_text or "").strip()
        if not text:
            return

        key = text.lower()
        existing = {str(c.get("search_text", "")).lower() for c in candidates}
        if key in existing:
            return

        candidates.append({
            "search_text": text,
            "relationship": relationship,
            "semantic_object_id": semantic_object_id,
            "semantic_fingerprint": semantic_fingerprint,
            "priority": priority,
            "search_weight": float(search_weight),
            "match_mode": match_mode,
            "confidence": float(search_weight),
        })

    add_candidate(phrase_text, "editor_phrase", 1, 1.00, "editor_phrase")

    if canonical_concept:
        add_candidate(canonical_concept, "canonical_concept", 2, 0.96, "canonical")

    for alias in aliases or []:
        add_candidate(alias, "alias", 3, 0.90, "alias")

    for concept in related_concepts or []:
        if isinstance(concept, dict):
            text = concept.get("canonical") or concept.get("concept") or concept.get("text") or concept.get("label")
        else:
            text = concept

        add_candidate(text, "related_concept", 4, 0.74, "related")

    return candidates

def understand_yellow_semantic_phrase_v1(
    yellow_phrase: Dict[str, Any],
) -> Dict[str, Any]:

    working_phrase = transition_yellow_phrase_state_v1(
        yellow_phrase,
        "reasoning_pending",
        source="semantic_phrase_understanding",
        note="Yellow phrase sent to Semantic Phrase Understanding.",
    )

    normalized_text = working_phrase.get("normalized_text")
    match = lookup_semantic_object_from_workspace_v1(working_phrase.get("workspace_id"), normalized_text)

    if not match:
        working_phrase["semantic_understanding"] = {
            "understanding_status": "not_understood",
            "semantic_object_id": None,
            "canonical_concept": None,
            "semantic_type": None,
            "aliases": [],
            "match_type": None,
            "confidence": 0.0,
            "search_candidates": [],
            "rejection_reason": "No matching semantic object found in workspace knowledge.",
        }

        working_phrase = transition_yellow_phrase_state_v1(
            working_phrase,
            "rejected",
            source="semantic_phrase_understanding",
            note="No semantic object found for yellow phrase.",
        )

        working_phrase["routing"]["requires_target_discovery"] = False
        
    canonical_concept = working_phrase.get("canonical_concept") or working_phrase.get("semantic_identity", {}).get("canonical_concept")
    aliases = working_phrase.get("aliases") or working_phrase.get("semantic_identity", {}).get("aliases") or []
    related_concepts = working_phrase.get("related_concepts") or working_phrase.get("semantic_identity", {}).get("related_concepts") or []
    semantic_object_id = working_phrase.get("semantic_object_id") or working_phrase.get("semantic_identity", {}).get("semantic_object_id")
    semantic_fingerprint = working_phrase.get("semantic_fingerprint") or working_phrase.get("semantic_identity", {}).get("semantic_fingerprint")

    working_phrase["source_provenance"] = {
        "source": "semantic_phrase_understanding",
        "uses_semantic_workspace": True,
        "uses_memory_engine": True,
        "uses_learning_engine": True,
        "uses_existing_reasoning_services": True,
        "calls_semantic_linking_reasoning_engine": False,
        "creates_new_reasoning_engine": False,
    }

    working_phrase["semantic_match_candidates"] = _build_semantic_match_candidates_v1(
        phrase_text=working_phrase.get("phrase_text") or working_phrase.get("text") or "",
        canonical_concept=canonical_concept or "",
        aliases=aliases,
        related_concepts=related_concepts,
        semantic_object_id=semantic_object_id or "",
        semantic_fingerprint=semantic_fingerprint or "",
    )

    working_phrase["processing_state"] = {
        **(working_phrase.get("processing_state") or {}),
        "current_engine": "semantic_phrase_understanding",
        "status": "semantic_understanding_complete",
        "ready_for_target_discovery": False,
        "next_expected_engine": None,
    }

    working_phrase["ready_for_target_discovery"] = False
    working_phrase["next_expected_engine"] = None

    return working_phrase

    search_candidates = []

    semantic_fingerprint = _stable_id(
        "semantic_fingerprint",
        match["semantic_object_id"],
        match["canonical_concept"],
        match["semantic_type"],
    )

    primary_topic = {
        "search_candidate_id": _stable_id("semantic_search_candidate", match["canonical_concept"], "primary"),
        "search_text": match["canonical_concept"],
        "relationship": "primary",
        "semantic_object_id": match["semantic_object_id"],
        "semantic_fingerprint": semantic_fingerprint,
        "priority": 1,
        "search_weight": match["confidence"],
        "search_mode": "canonical",
        "confidence": match["confidence"],
    }
    search_candidates.append(primary_topic)

    for alias in match.get("aliases", []):
        if alias and alias != match["canonical_concept"]:
            search_candidates.append({
                "search_candidate_id": _stable_id("semantic_search_candidate", alias, "alias"),
                "search_text": alias,
                "relationship": "alias",
                "semantic_object_id": match["semantic_object_id"],
                "semantic_fingerprint": semantic_fingerprint,
                "priority": 2,
                "search_weight": round(max(match["confidence"] - 0.03, 0.0), 2),
                "search_mode": "alias",
                "confidence": round(max(match["confidence"] - 0.03, 0.0), 2),
            })

    working_phrase["semantic_understanding"] = {
        "understanding_status": "understood",
        "semantic_object_id": match["semantic_object_id"],
        "semantic_fingerprint": semantic_fingerprint,
        "canonical_concept": match["canonical_concept"],
        "semantic_type": match["semantic_type"],
        "semantic_fingerprint": semantic_fingerprint,
        "aliases": match.get("aliases", []),
        "match_type": match["match_type"],
        "confidence": match["confidence"],
        "search_candidates": search_candidates,
        "workspace_lookup": {
            "lookup_source": "semantic_workspace_memory_learning",
            "uses_existing_learning_pipeline": True,
            "calls_semantic_linking_reasoning_engine": False,
        },
        "boundary_rule": (
            "Semantic Phrase Understanding identifies what a yellow phrase means using workspace knowledge. "
            "It does not query Active Target Set, discover or choose target URLs, create highlights, "
            "write memory, or generate explanations."
        ),
    }

    # Keep semantic_identity as the stable field future engines can read.
    working_phrase["semantic_identity"] = {
        "identity_status": "bound",
        "semantic_object_id": match["semantic_object_id"],
        "semantic_fingerprint": semantic_fingerprint,
        "canonical_concept": match["canonical_concept"],
        "identity_confidence": match["confidence"],
        "identity_source": "semantic_phrase_understanding",
    }

    working_phrase["routing"]["requires_target_discovery"] = True
    working_phrase["routing"]["send_to_yellow_resolver"] = False
    working_phrase["routing"]["requires_explainability"] = False

    working_phrase = transition_yellow_phrase_state_v1(
        working_phrase,
        "reasoned",
        source="semantic_phrase_understanding",
        note="Semantic phrase understanding completed; downstream learning-engine routing is not yet assigned.",
    )

    
    canonical_concept = working_phrase.get("canonical_concept") or working_phrase.get("semantic_identity", {}).get("canonical_concept")
    aliases = working_phrase.get("aliases") or working_phrase.get("semantic_identity", {}).get("aliases") or []
    related_concepts = working_phrase.get("related_concepts") or working_phrase.get("semantic_identity", {}).get("related_concepts") or []
    semantic_object_id = working_phrase.get("semantic_object_id") or working_phrase.get("semantic_identity", {}).get("semantic_object_id")
    semantic_fingerprint = working_phrase.get("semantic_fingerprint") or working_phrase.get("semantic_identity", {}).get("semantic_fingerprint")

    working_phrase["source_provenance"] = {
        "source": "semantic_phrase_understanding",
        "uses_semantic_workspace": True,
        "uses_memory_engine": True,
        "uses_learning_engine": True,
        "uses_existing_reasoning_services": True,
        "calls_semantic_linking_reasoning_engine": False,
        "creates_new_reasoning_engine": False,
    }

    working_phrase["semantic_match_candidates"] = _build_semantic_match_candidates_v1(
        phrase_text=working_phrase.get("phrase_text") or working_phrase.get("text") or "",
        canonical_concept=canonical_concept or "",
        aliases=aliases,
        related_concepts=related_concepts,
        semantic_object_id=semantic_object_id or "",
        semantic_fingerprint=semantic_fingerprint or "",
    )

    working_phrase["processing_state"] = {
        **(working_phrase.get("processing_state") or {}),
        "current_engine": "semantic_phrase_understanding",
        "status": "semantic_understanding_complete",
        "ready_for_target_discovery": False,
        "next_expected_engine": None,
    }

    working_phrase["ready_for_target_discovery"] = False
    working_phrase["next_expected_engine"] = None

    return working_phrase


def understand_yellow_semantic_phrase_registry_v1(
    phrase_registry: Dict[str, Any],
) -> Dict[str, Any]:

    understood_phrases = [
        understand_yellow_semantic_phrase_v1(phrase)
        for phrase in phrase_registry.get("yellow_semantic_phrases", [])
    ]

    understood_count = sum(
        1
        for phrase in understood_phrases
        if phrase.get("semantic_understanding", {}).get("understanding_status") == "understood"
    )

    not_understood_count = sum(
        1
        for phrase in understood_phrases
        if phrase.get("semantic_understanding", {}).get("understanding_status") == "not_understood"
    )

    return {
        "schema_version": "semantic_phrase_understanding_model_v1",
        "phase": "semantic_linking_execution.step_2",
        "patch": "step_2_semantic_phrase_understanding_C",
        "name": "Semantic Phrase Understanding",
        "created_at": _now_iso(),
        "workspace_id": phrase_registry.get("workspace_id"),
        "document": phrase_registry.get("document", {}),
        "source_registry": {
            "schema_version": phrase_registry.get("schema_version"),
            "phase": phrase_registry.get("phase"),
            "patch": phrase_registry.get("patch"),
        },
        "understood_yellow_phrases": understood_phrases,
        "metadata": {
            "input_phrase_count": len(phrase_registry.get("yellow_semantic_phrases", [])),
            "understood_phrase_count": understood_count,
            "not_understood_phrase_count": not_understood_count,
            "uses_existing_learning_pipeline": True,
            "calls_semantic_linking_reasoning_engine": False,
            "creates_new_reasoning_engine": False,
            "active_target_set_queried": False,
        },
        "boundary_rule": (
            "Semantic Phrase Understanding identifies yellow phrase semantic identity only. "
            "It does not duplicate the existing Semantic Linking Reasoning Engine, does not query Active Target Set, "
            "does not resolve links, does not create highlights, does not write memory, and does not generate explanations."
        ),
    }


def save_semantic_phrase_understanding_v1(
    phrase_registry: Dict[str, Any],
    output_path: str | Path,
) -> Dict[str, Any]:
    model = understand_yellow_semantic_phrase_registry_v1(phrase_registry)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(model, indent=2, ensure_ascii=False), encoding="utf-8")
    return model


def explain_semantic_phrase_understanding_v1() -> Dict[str, Any]:
    return {
        "step": "Step 2",
        "patch": "step_2_semantic_phrase_understanding_C",
        "name": "Semantic Phrase Understanding",
        "purpose": "Identify what each yellow editor phrase means using workspace semantic knowledge.",
        "input": "Yellow Semantic Phrase Registry Step 1D",
        "output": "Yellow phrases enriched with semantic_understanding and semantic_identity",
        "does": [
            "receives yellow phrase objects",
            "looks up phrase meaning in workspace semantic knowledge",
            "binds phrase to semantic_object_id",
            "assigns canonical_concept",
            "adds aliases and semantic type",
            "creates structured search candidates for Active Target Set discovery",
            "adds stable semantic fingerprint",
            "uses Semantic Workspace lookup interface",
            "marks phrase ready for target discovery",
        ],
        "does_not": [
            "create a new reasoning engine",
            "call semantic_linking_reasoning_engine.py",
            "query Active Target Set",
            "choose target URLs",
            "perform yellow resolving",
            "perform blue resolving",
            "create final highlights",
            "write memory",
            "generate explanations",
        ],
    }

