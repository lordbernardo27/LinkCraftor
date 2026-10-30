"""3.7.4 ? Evidence validation for existing phrase semantic context.

No inference, topic classification, intent detection, scoring or linking.
"""

from __future__ import annotations

from collections.abc import Mapping


_FIELDS = ("detected_topic", "detected_intent", "meaning")
_PROHIBITED_SOURCE_MARKERS = (
    "resolver",
    "target_rank",
    "seo_canonical_selection",
)


def _valid_claim(value):
    return isinstance(value, str) and bool(value.strip())


def _eligible_record(record, index):
    if not isinstance(record, Mapping):
        return False
    if type(record.get("candidate_index")) is not int:
        return False
    if record["candidate_index"] != index:
        return False
    if record.get("certified") is not True:
        return False
    if record.get("validity_status") != "valid":
        return False
    if record.get("stale") is True:
        return False
    source = record.get("source")
    if not isinstance(source, str) or not source.strip():
        return False
    if any(term in source.casefold() for term in _PROHIBITED_SOURCE_MARKERS):
        return False
    if record.get("evidence_type") != "phrase_semantic_context":
        return False
    return True


def validate_phrase_topic_intent(package):
    """Add fail-closed validation metadata to semantic_context."""
    if not isinstance(package, dict):
        raise TypeError("Invalid enrichment package")

    entries = package.get("enriched_candidates")
    registry = package.get("evidence_registry")

    if not isinstance(entries, list) or not isinstance(registry, dict):
        raise ValueError("Invalid enrichment package structure")

    prepared = []

    for index, entry in enumerate(entries):
        if (
            not isinstance(entry, dict)
            or type(entry.get("candidate_index")) is not int
            or entry["candidate_index"] != index
        ):
            raise ValueError("Invalid candidate sequence")

        context = entry.get("semantic_context")
        if not isinstance(context, dict):
            raise ValueError("Missing semantic context")

        status = context.get("status", "not_executed")
        evidence_ids = context.get("evidence_ids", [])
        claims = {
            field: context.get(field)
            for field in _FIELDS
        }

        result = {
            "status": "not_executed",
            "evidence_ids": [],
            "validated_fields": [],
            "topic_verified": False,
            "intent_verified": False,
            "meaning_verified": False,
            "certified": False,
            "automatic_linking_authorized": False,
        }

        if status in ("not_executed", "pending"):
            result["status"] = "not_executed"

        elif status in ("error", "unavailable", "stale", "invalid"):
            result["status"] = status

        elif status == "ambiguous" or context.get(
            "ambiguity_status"
        ) == "ambiguous":
            result["status"] = "ambiguous"

        elif not isinstance(evidence_ids, list):
            result["status"] = "invalid"

        elif not evidence_ids:
            result["status"] = "no_evidence"

        else:
            records = []
            valid = True
            for evidence_id in evidence_ids:
                if not isinstance(evidence_id, str) or not evidence_id:
                    valid = False
                    break
                record = registry.get(evidence_id)
                if not _eligible_record(record, index):
                    valid = False
                    break
                records.append((evidence_id, record))

            if not valid:
                result["status"] = "invalid"
            else:
                verified_fields = []
                conflict = False

                for field, claim in claims.items():
                    if claim is None:
                        continue
                    if not _valid_claim(claim):
                        conflict = True
                        break

                    matches = [
                        evidence_id
                        for evidence_id, record in records
                        if record.get(field) == claim
                    ]
                    if not matches:
                        conflict = True
                        break
                    verified_fields.append(field)

                if conflict:
                    result["status"] = "invalid"
                elif not verified_fields:
                    result["status"] = "no_evidence"
                else:
                    result["status"] = "evidence_validated"
                    result["validated_fields"] = verified_fields
                    result["evidence_ids"] = list(
                        dict.fromkeys(
                            evidence_id
                            for evidence_id, record in records
                            if any(
                                field in verified_fields
                                and record.get(field) == claims[field]
                                for field in _FIELDS
                            )
                        )
                    )
                    result["topic_verified"] = (
                        "detected_topic" in verified_fields
                    )
                    result["intent_verified"] = (
                        "detected_intent" in verified_fields
                    )
                    result["meaning_verified"] = (
                        "meaning" in verified_fields
                    )

        # Verification metadata is not a linking decision.
        prepared.append(result)

    for entry, result in zip(entries, prepared):
        entry["semantic_context"]["evidence_validation"] = result

    return package
