
from __future__ import annotations

from typing import Any, Dict, List


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize(text: str) -> str:
    return " ".join(_safe_text(text).lower().split())


def _make_response(layer: str, name: str, summary: str, actions: List[str]) -> Dict[str, Any]:
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
            "does_not_force_highlights": True,
            "workspace_safe": True,
        },
    }


def register_context_snapshots_v1(
    snapshots: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.13.1 Context Snapshot Registry.
    """

    registered = []
    rejected = []
    seen = set()

    for item in snapshots or []:
        snapshot_id = _safe_text(item.get("snapshot_id") or item.get("id") if isinstance(item, dict) else "")
        context_text = _safe_text(item.get("context") or item.get("text") or item.get("summary") if isinstance(item, dict) else item)

        key = _normalize(snapshot_id or context_text)

        if not key:
            rejected.append({"reason": "missing_snapshot_identifier_or_context"})
            continue

        if key in seen:
            rejected.append({"snapshot_id": snapshot_id, "reason": "duplicate_context_snapshot"})
            continue

        seen.add(key)

        registered.append({
            "snapshot_id": (snapshot_id or key).replace(" ", "_"),
            "context": context_text,
            "metadata": item.get("metadata", {}) if isinstance(item, dict) else {},
            "snapshot_role": "context_snapshot_registry",
        })

    return _make_response(
        "1.13.1",
        "Context Snapshot Registry",
        "Registers governed context snapshots and snapshot metadata.",
        [
            "context_snapshot_registry",
            "snapshot_identifier_storage",
            "snapshot_metadata_storage",
            "snapshot_governance_rules",
            "snapshot_registry_audit",
        ],
    ) | {
        "registered_snapshots": registered,
        "rejected_snapshots": rejected,
    }


def persist_semantic_context_v1(
    workspace_id: str,
    snapshots: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.13.2 Context Persistence Engine.
    """

    registered = register_context_snapshots_v1(snapshots)

    persisted = [
        {
            **item,
            "workspace_id": _safe_text(workspace_id),
            "persistence_role": "semantic_context_persistence",
            "retention_policy": "workspace_scoped_context",
        }
        for item in registered["registered_snapshots"]
    ]

    return _make_response(
        "1.13.2",
        "Context Persistence Engine",
        "Creates workspace-safe semantic context persistence records.",
        [
            "context_persistence_contract",
            "workspace_safe_context_records",
            "context_retention_metadata",
            "persistence_governance",
            "context_persistence_audit",
        ],
    ) | {
        "persisted_context": persisted,
        "rejected_snapshots": registered["rejected_snapshots"],
    }


def restore_semantic_context_v1(
    snapshot_id: str,
    persisted_context: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.13.3 Context Restoration Engine.
    """

    target = _normalize(snapshot_id)
    restored = []
    rejected = []

    for item in persisted_context or []:
        sid = _safe_text(item.get("snapshot_id") if isinstance(item, dict) else "")
        if _normalize(sid) == target:
            restored.append({
                "snapshot_id": sid,
                "context": item.get("context", "") if isinstance(item, dict) else "",
                "workspace_id": item.get("workspace_id", "") if isinstance(item, dict) else "",
                "restoration_role": "semantic_context_restoration",
            })

    if not restored:
        rejected.append({
            "snapshot_id": snapshot_id,
            "reason": "snapshot_not_found",
        })

    return _make_response(
        "1.13.3",
        "Context Restoration Engine",
        "Restores semantic context from registered workspace-safe snapshots.",
        [
            "context_restoration_support",
            "snapshot_based_restoration",
            "restoration_validation",
            "restoration_governance",
            "context_restoration_audit",
        ],
    ) | {
        "restored_context": restored,
        "rejected_restoration": rejected,
    }


def govern_context_continuity_v1(
    context_events: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.13.4 Context Continuity Governance.
    """

    continuity = []
    rejected = []
    previous_snapshot = None

    for item in context_events or []:
        snapshot_id = _safe_text(item.get("snapshot_id") or item.get("id") if isinstance(item, dict) else "")
        event_type = _safe_text(item.get("event_type", "context_event") if isinstance(item, dict) else "context_event")

        if not snapshot_id:
            rejected.append({"reason": "missing_snapshot_id"})
            continue

        continuity.append({
            "snapshot_id": snapshot_id,
            "event_type": event_type,
            "previous_snapshot_id": previous_snapshot,
            "continuity_role": "context_continuity_governance",
        })

        previous_snapshot = snapshot_id

    return _make_response(
        "1.13.4",
        "Context Continuity Governance",
        "Tracks context continuity and lifecycle transitions safely.",
        [
            "continuity_tracking",
            "context_lifecycle_support",
            "continuity_validation",
            "continuity_governance",
            "context_continuity_audit",
        ],
    ) | {
        "continuity_events": continuity,
        "rejected_events": rejected,
    }


def support_runtime_context_assistance_v1(
    runtime_context: Dict[str, Any],
    persisted_context: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.13.5 Runtime Context Assistance.
    """

    query = _safe_text(runtime_context.get("query") or runtime_context.get("phrase") or runtime_context.get("topic") if isinstance(runtime_context, dict) else "")
    q = _normalize(query)

    matches = []

    for item in persisted_context or []:
        context = _safe_text(item.get("context") if isinstance(item, dict) else "")
        snapshot_id = _safe_text(item.get("snapshot_id") if isinstance(item, dict) else "")

        key = _normalize(context)

        if q and (q in key or any(part in key for part in q.split())):
            matches.append({
                "snapshot_id": snapshot_id,
                "context": context,
                "runtime_context_role": "runtime_context_assistance",
            })

    return _make_response(
        "1.13.5",
        "Runtime Context Assistance",
        "Provides runtime context assistance and continuity-aware semantic support.",
        [
            "runtime_context_assistance",
            "context_restoration_reporting",
            "continuity_aware_semantic_support",
            "runtime_context_audit",
        ],
    ) | {
        "runtime_query": query,
        "context_assistance": matches,
        "context_assistance_count": len(matches),
    }


def explain_semantic_context_persistence_v1() -> Dict[str, Any]:
    return {
        "layer": "1.13",
        "name": "Semantic Context Persistence Layer",
        "status": "active",
        "scope": "semantic_context_persistence_governance",
        "sub_layers": [
            "1.13.1 Context Snapshot Registry",
            "1.13.2 Context Persistence Engine",
            "1.13.3 Context Restoration Engine",
            "1.13.4 Context Continuity Governance",
            "1.13.5 Runtime Context Assistance",
        ],
        "safety_rules": {
            "governance_only": True,
            "runtime_support_only": True,
            "does_not_modify_uploaded_article": True,
            "does_not_create_runtime_router": True,
            "does_not_create_new_target_selector": True,
            "does_not_replace_existing_scoring": True,
            "does_not_force_link_decisions": True,
            "does_not_force_highlights": True,
            "workspace_safe": True,
        },
    }
