
"""3.7.3: Evidence-referenced advisory alias enrichment.

Existing intelligence remains authoritative. This module creates no
aliases, canonical identities, scores, links, or certifications.
"""

from __future__ import annotations

from collections.abc import Mapping


def _empty(status):
    return {
        "status": status,
        "alias_candidates": [],
        "alias_evidence_ids": [],
        "canonical_identity_status": "unavailable",
        "identity_verified": False,
        "certified": False,
        "automatic_alias_linking_blocked": True,
    }


def _explicit_aliases(record):
    """Read explicit stored names only; never synthesize synonyms."""
    if not isinstance(record, Mapping):
        return [], False

    if "aliases" not in record:
        return [], True

    values = record["aliases"]
    if not isinstance(values, (list, tuple)):
        return [], False

    if any(
        not isinstance(value, str) or not value.strip()
        for value in values
    ):
        return [], False

    return list(dict.fromkeys(value.strip() for value in values)), True


def enrich_phrase_aliases(package):
    """Append alias summaries without changing existing source evidence."""
    if not isinstance(package, dict):
        raise TypeError("Invalid enrichment package")

    entries = package.get("enriched_candidates")
    registry = package.get("evidence_registry")

    if not isinstance(entries, list) or not isinstance(registry, dict):
        raise ValueError("Invalid Enricher package contract")

    prepared = []

    for index, entry in enumerate(entries):
        if (
            not isinstance(entry, dict)
            or type(entry.get("candidate_index")) is not int
            or entry["candidate_index"] != index
        ):
            raise ValueError("Invalid candidate order")

        identity = entry.get("canonical_concept_entity")
        identity_status = (
            identity.get("status")
            if isinstance(identity, Mapping)
            else "unavailable"
        )

        memory = entry.get("semantic_memory")
        graph = entry.get("intelligence_graph")

        records = []
        invalid = False
        seen = set()

        # Semantic Memory aliases require an exact evidence association.
        if isinstance(memory, Mapping):
            matches = memory.get("memory_matches", [])
            ids = memory.get("evidence_ids", [])

            if not isinstance(matches, list) or not isinstance(ids, list):
                invalid = True
            elif matches and len(matches) != len(ids):
                # Do not guess which memory evidence belongs to a match.
                invalid = True
            else:
                for match, eid in zip(matches, ids):
                    if (
                        not isinstance(match, Mapping)
                        or not isinstance(eid, str)
                        or not isinstance(registry.get(eid), Mapping)
                        or registry[eid].get("candidate_index") != index
                    ):
                        invalid = True
                        break

                    aliases, valid = _explicit_aliases(match)
                    if not valid:
                        invalid = True
                        break

                    for name in aliases:
                        key = (name.casefold(), eid)
                        if key not in seen:
                            seen.add(key)
                            records.append({
                                "alias": name,
                                "evidence_id": eid,
                                "source": "semantic_memory",
                                "verified": False,
                            })

        # Concept-store aliases are taken from registered source records.
        # match_type alone is not proof of alias equivalence.
        if not invalid and isinstance(graph, Mapping):
            concept_matches = graph.get("concept_matches", [])

            if concept_matches is not None and not isinstance(
                concept_matches, list
            ):
                invalid = True
            elif isinstance(concept_matches, list):
                for position, match in enumerate(concept_matches):
                    eid = f"graph_concept_{index}_{position}"
                    evidence = registry.get(eid)

                    if (
                        not isinstance(match, Mapping)
                        or not isinstance(evidence, Mapping)
                        or evidence.get("candidate_index") != index
                        or evidence.get("source") != "workspace_concept_store"
                        or evidence.get("evidence_type")
                            != "concept_or_alias_match"
                        or evidence.get("concept_key")
                            != match.get("concept_key")
                        or evidence.get("match_type")
                            != match.get("match_type")
                        or evidence.get("certified") is not False
                    ):
                        invalid = True
                        break

                    aliases, valid = _explicit_aliases(
                        evidence.get("source_record")
                    )
                    if not valid:
                        invalid = True
                        break

                    for name in aliases:
                        key = (name.casefold(), eid)
                        if key not in seen:
                            seen.add(key)
                            records.append({
                                "alias": name,
                                "evidence_id": eid,
                                "source": "workspace_concept_store",
                                "verified": False,
                            })

        if invalid:
            result = _empty("invalid")
        elif records:
            result = _empty(
                "ambiguous"
                if identity_status == "ambiguous"
                else "evidence_found_unverified"
            )
            result["alias_candidates"] = records
            result["alias_evidence_ids"] = list(dict.fromkeys(
                item["evidence_id"] for item in records
            ))
        elif identity_status == "not_executed":
            result = _empty("not_executed")
        else:
            result = _empty("no_evidence")

        result["canonical_identity_status"] = identity_status

        # Phase 3.7.3 does not authorize linking. In particular,
        # ambiguous identities must never be auto-linked via aliases.
        result["automatic_alias_linking_blocked"] = True
        prepared.append(result)

    for entry, result in zip(entries, prepared):
        entry["alias_enrichment"] = result

    return package
