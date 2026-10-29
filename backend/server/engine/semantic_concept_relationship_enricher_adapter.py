
"""Read-only persisted semantic workspace concept relationship evidence.

Observations are advisory, never certifications or link approvals.
Does not rebuild or modify the semantic workspace learner graph.
"""
from __future__ import annotations

from copy import deepcopy
import json
import math
import re
from typing import Any

from backend.server.engine.semantic_workspace_learner import (
    _workspace_map_path,
)


def _normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def retrieve_persisted_concept_relationships(
    *,
    workspace_id: str,
    phrase: str,
    max_results: int = 25,
) -> dict[str, Any]:
    if not isinstance(workspace_id, str) or not re.fullmatch(
        r"[A-Za-z0-9_-]+", workspace_id
    ):
        raise ValueError("Valid workspace_id required.")

    if not isinstance(phrase, str) or not phrase.strip():
        raise ValueError("Nonempty phrase required.")

    if type(max_results) is not int or not 1 <= max_results <= 100:
        raise ValueError("max_results must be between 1 and 100.")

    output = {
        "status": "no_evidence",
        "workspace_id": workspace_id,
        "query": phrase.strip(),
        "source": "semantic_map_v2_concept_graph",
        "relationship_records": [],
        "relationship_count": 0,
        "blocked_concept_count": 0,
        "certified": False,
        "linking_decision_performed": False,
    }

    path = _workspace_map_path(workspace_id)

    if not path.is_file():
        output["storage_status"] = "missing"
        return output

    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise RuntimeError("Semantic map unreadable") from exc

    if not isinstance(data, dict):
        raise RuntimeError("Invalid semantic map root.")

    if data.get("workspace_id") != workspace_id:
        raise RuntimeError("Semantic map workspace mismatch.")

    if data.get("version") != "semantic_map_v2":
        raise RuntimeError("Unexpected semantic map version.")

    graph = data.get("concept_graph")
    if not isinstance(graph, list):
        raise RuntimeError("Invalid persisted concept graph.")

    output["storage_status"] = "loaded"

    query = _normalize(phrase)
    records = []

    for concept_index, concept in enumerate(graph):
        if not isinstance(concept, dict):
            raise RuntimeError("Malformed persisted concept.")

        canonical = concept.get("canonical_phrase")
        synonyms = concept.get("synonyms", [])
        related_concepts = concept.get("related_concepts", [])
        evidence = concept.get("evidence", [])
        conflict = concept.get("conflict_resolution")

        if (
            not isinstance(canonical, str)
            or not isinstance(synonyms, list)
            or not isinstance(related_concepts, list)
            or not isinstance(evidence, list)
            or any(not isinstance(x, str) for x in synonyms)
            or any(not isinstance(x, str) for x in related_concepts)
        ):
            raise RuntimeError("Invalid persisted concept schema.")

        match_type = (
            "canonical" if _normalize(canonical) == query
            else "synonym" if any(
                _normalize(x) == query for x in synonyms
            )
            else None
        )

        if match_type is None:
            continue

        # A missing conflict-resolution state does not prove safety.
        if not isinstance(conflict, dict):
            output["blocked_concept_count"] += 1
            continue

        if conflict.get("hard_blocked") is not False:
            output["blocked_concept_count"] += 1
            continue

        try:
            confidence = float(concept.get("confidence"))
        except (TypeError, ValueError):
            output["blocked_concept_count"] += 1
            continue

        if not math.isfinite(confidence) or not 0 < confidence <= 1:
            output["blocked_concept_count"] += 1
            continue

        if not isinstance(evidence, list):
            raise RuntimeError("Invalid concept evidence.")

        # Related names alone are insufficient. Require a matching
        # persisted evidence record with identifiable source and type.
        allowed_related = {
            _normalize(item) for item in related_concepts
        }

        for evidence_index, item in enumerate(evidence):
            if not isinstance(item, dict):
                raise RuntimeError("Malformed relationship evidence.")

            related = item.get("related_phrase")
            relation_type = item.get("relation_type")
            source = item.get("source")
            role = item.get("source_role")

            if (
                not isinstance(related, str)
                or not isinstance(relation_type, str)
                or not isinstance(source, str)
                or not related.strip()
                or not relation_type.strip()
                or not source.strip()
            ):
                continue

            normalized_related = _normalize(related)

            is_synonym = (
                relation_type == "synonym"
                and normalized_related in {
                    _normalize(x) for x in synonyms
                }
            )

            is_related = (
                relation_type != "synonym"
                and normalized_related in allowed_related
            )

            if not (is_synonym or is_related):
                continue

            try:
                evidence_confidence = float(item.get("confidence"))
            except (TypeError, ValueError):
                continue

            if (
                not math.isfinite(evidence_confidence)
                or not 0 <= evidence_confidence <= 1
            ):
                continue

            records.append({
                "concept_index": concept_index,
                "canonical_phrase": canonical,
                "matched_phrase": phrase.strip(),
                "match_type": match_type,
                "related_phrase": related,
                "relation_type": relation_type,
                "relationship_category": (
                    "synonym_observation" if is_synonym
                    else "related_concept_observation"
                ),
                "source": source,
                "source_role": role,
                "evidence_confidence": evidence_confidence,
                "concept_confidence": confidence,
                "conflict_resolution": deepcopy(conflict),
                "evidence_index": evidence_index,
                "original_evidence": deepcopy(item),
                "certified": False,
                "semantic_equivalence_asserted": False,
                "approved_link_target": False,
            })

            if len(records) >= max_results:
                break

        if len(records) >= max_results:
            break

    output["relationship_records"] = records
    output["relationship_count"] = len(records)

    if records:
        output["status"] = "relationship_evidence_found"

    return output


__all__ = ["retrieve_persisted_concept_relationships"]
