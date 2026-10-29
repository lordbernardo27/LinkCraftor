
"""3.7.2: Evidence-referenced, nonauthorizing concept/entity summary."""

from collections.abc import Mapping


def _result(status, references=()):
    return {
        "status": status,
        "canonical_concept_id": None,
        "canonical_entity_id": None,
        "canonical_name": None,
        "candidate_evidence_ids": list(references),
        "identity_verified": False,
        "certified": False,
        "validity_status": "not_evaluated",
        "automatic_concept_linking_blocked": status != "no_evidence",
    }


def enrich_canonical_concept_entities(package):
    """Add summaries; preserve original candidates and source evidence."""
    if not isinstance(package, dict):
        raise TypeError("Invalid enrichment package")

    entries = package.get("enriched_candidates")
    registry = package.get("evidence_registry")

    if not isinstance(entries, list) or not isinstance(registry, dict):
        raise ValueError("Invalid enrichment contract")

    prepared = []

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or type(entry.get("candidate_index")) is not int:
            raise ValueError("Invalid candidate identity")
        if entry["candidate_index"] != index:
            raise ValueError("Candidate order mismatch")

        graph = entry.get("intelligence_graph")
        if not isinstance(graph, Mapping):
            prepared.append(_result("unavailable"))
            continue

        status = graph.get("status")
        if status in {"unavailable", "error", "invalid", "stale"}:
            prepared.append(_result(status))
            continue

        matches = graph.get("concept_matches")
        if not isinstance(matches, list):
            prepared.append(_result("invalid"))
            continue

        if not matches:
            prepared.append(
                _result("no_evidence" if status == "no_evidence" else "invalid")
            )
            continue

        if status != "concept_evidence_found":
            prepared.append(_result("invalid"))
            continue

        evidence_ids = []
        distinct_keys = set()
        valid = True

        for position, match in enumerate(matches):
            evidence_id = f"graph_concept_{index}_{position}"
            evidence = registry.get(evidence_id)

            if (
                not isinstance(match, dict)
                or not isinstance(evidence, Mapping)
                or not isinstance(match.get("concept_key"), str)
                or not match["concept_key"].strip()
                or evidence.get("source") != "workspace_concept_store"
                or evidence.get("evidence_type") != "concept_or_alias_match"
                or evidence.get("candidate_index") != index
                or evidence.get("concept_key") != match.get("concept_key")
                or evidence.get("concept") != match.get("concept")
                or evidence.get("match_type") != match.get("match_type")
                or evidence.get("relationship_asserted") is not False
                or evidence.get("certified") is not False
                or evidence.get("validity_status") != "not_evaluated"
            ):
                valid = False
                break

            evidence_ids.append(evidence_id)
            distinct_keys.add(match["concept_key"])

        if not valid:
            prepared.append(_result("invalid"))
        elif len(distinct_keys) > 1:
            prepared.append(_result("ambiguous", evidence_ids))
        else:
            prepared.append(_result("candidate_unverified", evidence_ids))

    for entry, result in zip(entries, prepared):
        entry["canonical_concept_entity"] = result

    return package
