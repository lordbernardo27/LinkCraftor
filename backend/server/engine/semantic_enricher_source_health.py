"""
Phase 3.8 ? advisory intelligence source-health assessment.

Operational availability is distinct from evidence integrity,
semantic certification and linking authority.
"""

from __future__ import annotations

from typing import Any


SOURCES = (
    "semantic_memory",
    "intelligence_graph",
    "reasoning_intelligence",
    "explainability_intelligence",
    "evidence_integrity",
)


def assess_enricher_source_health(
    *, enrichment_package: dict[str, Any]
) -> dict[str, Any]:
    if not isinstance(enrichment_package, dict):
        raise ValueError("Invalid enrichment package")

    source_map = enrichment_package.get("intelligence_sources")

    if not isinstance(source_map, dict):
        raise ValueError("Missing intelligence source registry")

    results = {}
    degraded = []
    unknown = []
    healthy = []

    for name in SOURCES:
        section = source_map.get(name)

        if not isinstance(section, dict):
            results[name] = {
                "health": "unknown",
                "reason": "source_status_missing",
                "reported_error_count": None,
                "numerical_error_count_complete": False,
            }
            unknown.append(name)
            continue

        status = section.get("status")
        error_fields = (
            "error_count",
            "relationship_error_count",
            "integrity_failed",
        )

        counts = {}
        for field in error_fields:
            value = section.get(field)
            if type(value) is int and value >= 0:
                counts[field] = value

        reported_total = sum(counts.values())

        explicit_failure = (
            isinstance(status, str)
            and (
                "error" in status.lower()
                or "fail" in status.lower()
            )
        )

        failure_detected = (
            explicit_failure or reported_total > 0
        )

        unknown_status = (
            not isinstance(status, str)
            or status.strip() == ""
        )

        if failure_detected:
            health = "degraded"
            degraded.append(name)
        elif unknown_status:
            health = "unknown"
            unknown.append(name)
        else:
            health = "operational"
            healthy.append(name)

        count_complete = not (
            failure_detected and reported_total == 0
        )

        results[name] = {
            "health": health,
            "original_status": status,
            "failure_detected": failure_detected,
            "reported_error_counts": counts,
            "reported_error_count": reported_total,
            "numerical_error_count_complete": count_complete,
            "reason": (
                "source_reported_failure"
                if explicit_failure
                else "error_count_nonzero"
                if reported_total > 0
                else "missing_status"
                if unknown_status
                else "no_reported_failure"
            ),
        }

    if degraded:
        overall = "degraded"
    elif unknown:
        overall = "unknown"
    else:
        overall = "operational"

    return {
        "status": overall,
        "sources_checked": len(SOURCES),
        "degraded_sources": degraded,
        "unknown_sources": unknown,
        "operational_sources": healthy,
        "source_health": results,
        "retrieval_failure_is_not_no_evidence": True,
        "evidence_integrity_unchanged": True,
        "semantic_certification_performed": False,
        "scorer_decision_performed": False,
        "linking_decision_performed": False,
    }


__all__ = ["assess_enricher_source_health"]
