
from __future__ import annotations

from typing import Any, Dict, List


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize(text: str) -> str:
    return " ".join(_safe_text(text).lower().split())


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _clamp_score(value: Any) -> float:
    score = _safe_float(value, 0.0)
    if score > 1:
        score = score / 100
    return round(max(0.0, min(1.0, score)), 4)


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
            "does_not_alter_internal_linking_logic": True,
            "does_not_alter_semantic_linking_logic": True,
        },
    }


def register_semantic_families_v1(
    families: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.6.1 Semantic Family Registry.
    """

    registry: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    seen = set()

    for item in families or []:
        family_id = _safe_text(item.get("family_id") or item.get("id") or item.get("name") if isinstance(item, dict) else item)
        label = _safe_text(item.get("label") or item.get("name") or family_id if isinstance(item, dict) else item)

        key = _normalize(family_id or label)

        if not key:
            rejected.append({"reason": "missing_family_identifier"})
            continue

        if key in seen:
            rejected.append({"family_id": family_id, "label": label, "reason": "duplicate_family"})
            continue

        seen.add(key)

        registry.append({
            "family_id": key.replace(" ", "_"),
            "label": label,
            "metadata": item.get("metadata", {}) if isinstance(item, dict) else {},
            "family_role": "semantic_family_registry",
        })

    return _make_response(
        "1.6.1",
        "Semantic Family Registry",
        "Registers governed semantic families and family metadata.",
        [
            "register_semantic_families",
            "store_family_identifiers",
            "store_family_metadata",
            "family_governance_rules",
            "family_registry_audit",
        ],
    ) | {
        "registered_families": registry,
        "rejected_families": rejected,
    }


def assign_family_membership_v1(
    phrases: List[Dict[str, Any]],
    families: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.6.2 Family Membership Engine.
    """

    family_result = register_semantic_families_v1(families)
    registered = family_result["registered_families"]

    memberships: List[Dict[str, Any]] = []
    unassigned: List[Dict[str, Any]] = []

    for phrase_item in phrases or []:
        phrase = _safe_text(phrase_item.get("phrase") or phrase_item.get("text") if isinstance(phrase_item, dict) else phrase_item)
        requested_family = _normalize(phrase_item.get("family_id") or phrase_item.get("family") if isinstance(phrase_item, dict) else "")

        if not phrase:
            continue

        matched_family = None

        if requested_family:
            for family in registered:
                if requested_family in {family["family_id"], _normalize(family["label"])}:
                    matched_family = family
                    break

        if not matched_family and registered:
            phrase_norm = _normalize(phrase)
            for family in registered:
                label_norm = _normalize(family["label"])
                if label_norm and (label_norm in phrase_norm or phrase_norm in label_norm):
                    matched_family = family
                    break

        if not matched_family:
            unassigned.append({"phrase": phrase, "reason": "no_family_match"})
            continue

        confidence = _clamp_score(phrase_item.get("confidence", 0.65) if isinstance(phrase_item, dict) else 0.65)

        memberships.append({
            "phrase": phrase,
            "family_id": matched_family["family_id"],
            "family_label": matched_family["label"],
            "membership_score": confidence,
            "membership_role": "semantic_family_member",
        })

    return _make_response(
        "1.6.2",
        "Family Membership Engine",
        "Assigns phrases to semantic families with membership scoring and governance.",
        [
            "assign_phrases_to_families",
            "family_membership_scoring",
            "membership_validation",
            "membership_governance",
            "membership_audit",
        ],
    ) | {
        "memberships": memberships,
        "unassigned_phrases": unassigned,
    }


def group_semantic_clusters_v1(
    memberships: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.6.3 Semantic Cluster Grouping.
    """

    clusters: Dict[str, Dict[str, Any]] = {}

    for item in memberships or []:
        family_id = _safe_text(item.get("family_id") if isinstance(item, dict) else "")
        family_label = _safe_text(item.get("family_label") if isinstance(item, dict) else family_id)
        phrase = _safe_text(item.get("phrase") if isinstance(item, dict) else "")

        if not family_id or not phrase:
            continue

        if family_id not in clusters:
            clusters[family_id] = {
                "family_id": family_id,
                "family_label": family_label,
                "members": [],
                "cluster_role": "semantic_cluster",
            }

        clusters[family_id]["members"].append(phrase)

    return _make_response(
        "1.6.3",
        "Semantic Cluster Grouping",
        "Groups semantic family members into governed semantic clusters.",
        [
            "semantic_cluster_grouping",
            "cluster_aggregation",
            "cluster_relationship_support",
            "cluster_governance",
            "cluster_audit",
        ],
    ) | {
        "clusters": list(clusters.values()),
    }


def suppress_duplicate_semantics_v1(
    memberships: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.6.4 Duplicate Semantic Suppression.
    """

    kept: List[Dict[str, Any]] = []
    suppressed: List[Dict[str, Any]] = []
    seen = set()

    for item in memberships or []:
        phrase = _safe_text(item.get("phrase") if isinstance(item, dict) else item)
        family_id = _safe_text(item.get("family_id", "unknown") if isinstance(item, dict) else "unknown")

        key = (_normalize(phrase), _normalize(family_id))

        if not phrase:
            continue

        if key in seen:
            suppressed.append({
                "phrase": phrase,
                "family_id": family_id,
                "reason": "duplicate_semantic_family_member",
            })
            continue

        seen.add(key)
        kept.append(item if isinstance(item, dict) else {"phrase": phrase, "family_id": family_id})

    return _make_response(
        "1.6.4",
        "Duplicate Semantic Suppression",
        "Suppresses duplicate semantic variants at the family-membership level.",
        [
            "duplicate_family_member_detection",
            "redundant_semantic_variant_suppression",
            "family_level_duplicate_controls",
            "duplicate_governance",
            "duplicate_suppression_audit",
        ],
    ) | {
        "kept_memberships": kept,
        "suppressed_memberships": suppressed,
    }


def support_family_aware_linking_v1(
    link_candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.6.5 Family-Aware Linking.
    """

    supported: List[Dict[str, Any]] = []

    for item in link_candidates or []:
        phrase = _safe_text(item.get("phrase") or item.get("text") if isinstance(item, dict) else item)
        family_id = _safe_text(item.get("family_id", "unknown") if isinstance(item, dict) else "unknown")
        target = _safe_text(item.get("target") or item.get("url") if isinstance(item, dict) else "")

        if not phrase:
            continue

        supported.append({
            "phrase": phrase,
            "family_id": family_id,
            "target": target,
            "family_linking_role": "family_aware_linking_support",
            "requires_existing_link_decision_flow": True,
        })

    return _make_response(
        "1.6.5",
        "Family-Aware Linking",
        "Provides family-aware support for existing linking workflows without forcing links.",
        [
            "family_aware_linking_support",
            "family_relevance_assistance",
            "family_based_linking_governance",
            "linking_support_reporting",
            "family_linking_audit",
        ],
    ) | {
        "family_linking_support": supported,
    }


def support_family_aware_highlighting_v1(
    highlight_candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.6.6 Family-Aware Highlighting.
    """

    supported: List[Dict[str, Any]] = []
    family_seen = set()

    for item in highlight_candidates or []:
        phrase = _safe_text(item.get("phrase") or item.get("text") if isinstance(item, dict) else item)
        family_id = _safe_text(item.get("family_id", "unknown") if isinstance(item, dict) else "unknown")
        bucket = _safe_text(item.get("bucket", "semantic") if isinstance(item, dict) else "semantic")

        if not phrase:
            continue

        diversity_flag = "first_family_highlight" if family_id not in family_seen else "additional_family_highlight"
        family_seen.add(family_id)

        supported.append({
            "phrase": phrase,
            "family_id": family_id,
            "bucket": bucket,
            "diversity_flag": diversity_flag,
            "family_highlight_role": "family_aware_highlighting_support",
            "does_not_force_highlight": True,
        })

    return _make_response(
        "1.6.6",
        "Family-Aware Highlighting",
        "Provides family-aware highlight support and diversity protection without forcing highlights.",
        [
            "family_aware_highlight_support",
            "highlight_diversity_protection",
            "family_based_highlight_governance",
            "highlight_support_reporting",
            "family_highlighting_audit",
        ],
    ) | {
        "family_highlight_support": supported,
    }


def explain_semantic_family_clustering_v1() -> Dict[str, Any]:
    return {
        "layer": "1.6",
        "name": "Semantic Family Clustering",
        "status": "active",
        "scope": "semantic_family_clustering_governance",
        "sub_layers": [
            "1.6.1 Semantic Family Registry",
            "1.6.2 Family Membership Engine",
            "1.6.3 Semantic Cluster Grouping",
            "1.6.4 Duplicate Semantic Suppression",
            "1.6.5 Family-Aware Linking",
            "1.6.6 Family-Aware Highlighting",
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
            "does_not_alter_internal_linking_logic": True,
            "does_not_alter_semantic_linking_logic": True,
        },
    }
