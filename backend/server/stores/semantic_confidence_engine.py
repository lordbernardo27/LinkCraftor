
from __future__ import annotations

from typing import Any, Dict, List


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _normalize_confidence(value: Any) -> float:
    score = _safe_float(value, 0.0)

    if score > 1:
        score = score / 100

    return round(max(0.0, min(1.0, score)), 4)


def _make_response(
    layer: str,
    name: str,
    summary: str,
    actions: List[str],
) -> Dict[str, Any]:
    return {
        "layer": layer,
        "name": name,
        "status": "active",
        "summary": summary,
        "actions": actions,
        "safety": {
            "governance_only": True,
            "runtime_support_only": True,
            "does_not_modify_uploaded_article": True,
            "does_not_create_runtime_router": True,
            "does_not_create_new_target_selector": True,
            "does_not_replace_existing_scoring": True,
            "does_not_force_link_decisions": True,
        },
    }


def calculate_unified_semantic_confidence_v1(
    signals: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.10.1 Unified Semantic Confidence.
    """

    normalized: List[Dict[str, Any]] = []

    for signal in signals or []:
        name = _safe_text(signal.get("name") or signal.get("source") or signal.get("layer") if isinstance(signal, dict) else "signal")
        raw_score = signal.get("score", signal.get("confidence", 0.0)) if isinstance(signal, dict) else 0.0
        score = _normalize_confidence(raw_score)

        normalized.append({
            "signal": name,
            "normalized_confidence": score,
            "confidence_role": "semantic_confidence_signal",
        })

    if normalized:
        unified = round(sum(x["normalized_confidence"] for x in normalized) / len(normalized), 4)
    else:
        unified = 0.0

    return _make_response(
        "1.10.1",
        "Unified Semantic Confidence",
        "Aggregates and normalizes semantic confidence signals across support layers.",
        [
            "unified_semantic_confidence_scoring",
            "confidence_normalization",
            "cross_layer_confidence_aggregation",
            "confidence_governance",
            "confidence_explainability",
            "confidence_audit",
        ],
    ) | {
        "unified_confidence": unified,
        "signals": normalized,
    }


def track_semantic_evidence_v1(
    evidence_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.10.2 Semantic Evidence Tracking.
    """

    seen = set()
    tracked: List[Dict[str, Any]] = []
    duplicates: List[Dict[str, Any]] = []

    for item in evidence_items or []:
        evidence = _safe_text(item.get("evidence") or item.get("text") or item.get("phrase") if isinstance(item, dict) else item)
        source = _safe_text(item.get("source") or item.get("layer") or "unknown" if isinstance(item, dict) else "unknown")
        key = (evidence.lower(), source.lower())

        if not evidence:
            continue

        if key in seen:
            duplicates.append({
                "evidence": evidence,
                "source": source,
                "reason": "duplicate_evidence",
            })
            continue

        seen.add(key)
        tracked.append({
            "evidence": evidence,
            "source": source,
            "lineage": [source],
            "evidence_role": "semantic_evidence",
        })

    return _make_response(
        "1.10.2",
        "Semantic Evidence Tracking",
        "Tracks semantic evidence, source lineage, and duplicate evidence suppression.",
        [
            "semantic_evidence_tracking",
            "evidence_lineage_tracking",
            "evidence_source_aggregation",
            "duplicate_evidence_suppression",
            "evidence_governance",
            "evidence_audit",
        ],
    ) | {
        "tracked_evidence": tracked,
        "duplicate_evidence": duplicates,
    }


def explain_semantic_reasoning_v1(
    confidence: Dict[str, Any],
    evidence: Dict[str, Any],
    relationships: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """
    1.10.3 Semantic Explainability.
    """

    unified_confidence = _normalize_confidence(confidence.get("unified_confidence", 0.0) if isinstance(confidence, dict) else 0.0)
    evidence_count = len(evidence.get("tracked_evidence", []) if isinstance(evidence, dict) else [])
    relationship_count = len(relationships or [])

    explanation = {
        "confidence_summary": f"Unified semantic confidence is {unified_confidence}.",
        "evidence_summary": f"{evidence_count} semantic evidence item(s) are available.",
        "relationship_summary": f"{relationship_count} relationship signal(s) are available.",
        "semantic_trace": {
            "confidence_available": unified_confidence > 0,
            "evidence_available": evidence_count > 0,
            "relationships_available": relationship_count > 0,
        },
    }

    return _make_response(
        "1.10.3",
        "Semantic Explainability",
        "Produces semantic reasoning explanations from confidence, evidence, and relationship signals.",
        [
            "semantic_explainability",
            "semantic_trace_output",
            "reasoning_explanation_support",
            "confidence_explanation_support",
            "relationship_explanation_support",
            "explainability_audit",
        ],
    ) | {
        "explanation": explanation,
    }


def report_semantic_support_layers_v1(
    support_layers: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.10.4 Semantic Support-Layer Reporting.
    """

    reports: List[Dict[str, Any]] = []

    for layer in support_layers or []:
        name = _safe_text(layer.get("layer") or layer.get("name") or "support_layer" if isinstance(layer, dict) else "support_layer")
        status = _safe_text(layer.get("status", "unknown") if isinstance(layer, dict) else "unknown")
        count = len(layer.get("results", []) if isinstance(layer, dict) and isinstance(layer.get("results", []), list) else [])

        reports.append({
            "layer": name,
            "status": status,
            "reported_items": count,
            "support_role": "semantic_support_layer",
        })

    return _make_response(
        "1.10.4",
        "Semantic Support-Layer Reporting",
        "Reports retrieval, graph, runtime, and semantic support-layer contributions.",
        [
            "support_layer_reporting",
            "retrieval_support_reporting",
            "graph_support_reporting",
            "runtime_support_reporting",
            "semantic_aggregation_reporting",
            "support_layer_audit",
        ],
    ) | {
        "support_layer_reports": reports,
    }


def produce_runtime_semantic_reasoning_output_v1(
    confidence: Dict[str, Any],
    evidence: Dict[str, Any],
    explanation: Dict[str, Any],
    support_report: Dict[str, Any],
) -> Dict[str, Any]:
    """
    1.10.5 Runtime Semantic Reasoning Output.
    """

    output = {
        "semantic_confidence": confidence.get("unified_confidence", 0.0) if isinstance(confidence, dict) else 0.0,
        "evidence_count": len(evidence.get("tracked_evidence", []) if isinstance(evidence, dict) else []),
        "support_layer_count": len(support_report.get("support_layer_reports", []) if isinstance(support_report, dict) else []),
        "reasoning_summary": explanation.get("explanation", {}) if isinstance(explanation, dict) else {},
    }

    return _make_response(
        "1.10.5",
        "Runtime Semantic Reasoning Output",
        "Produces governed runtime semantic reasoning output for downstream visibility.",
        [
            "runtime_semantic_reasoning_output",
            "runtime_confidence_output",
            "runtime_evidence_output",
            "runtime_reasoning_summaries",
            "runtime_semantic_governance",
            "runtime_reasoning_audit",
        ],
    ) | {
        "runtime_semantic_output": output,
    }


def explain_semantic_confidence_engine_v1() -> Dict[str, Any]:
    return {
        "layer": "1.10",
        "name": "Semantic Confidence Engine",
        "status": "active",
        "scope": "semantic_confidence_governance",
        "sub_layers": [
            "1.10.1 Unified Semantic Confidence",
            "1.10.2 Semantic Evidence Tracking",
            "1.10.3 Semantic Explainability",
            "1.10.4 Semantic Support-Layer Reporting",
            "1.10.5 Runtime Semantic Reasoning Output",
        ],
        "safety_rules": {
            "governance_only": True,
            "runtime_support_only": True,
            "does_not_modify_uploaded_article": True,
            "does_not_create_runtime_router": True,
            "does_not_create_new_target_selector": True,
            "does_not_replace_existing_scoring": True,
            "does_not_force_link_decisions": True,
        },
    }
