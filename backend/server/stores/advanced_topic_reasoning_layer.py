
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
            "advisory_only": True,
            "separate_from_runtime_engine": True,
            "does_not_modify_uploaded_article": True,
            "does_not_edit_article_text": True,
            "does_not_publish_content": True,
            "does_not_create_runtime_router": True,
            "does_not_create_new_target_selector": True,
            "does_not_replace_existing_scoring": True,
            "does_not_force_link_decisions": True,
            "does_not_force_highlights": True,
            "does_not_alter_internal_linking_logic": True,
            "does_not_alter_semantic_linking_logic": True,
        },
    }


def establish_advisory_reasoning_foundation_v1(inputs: Dict[str, Any] | None = None) -> Dict[str, Any]:
    inputs = inputs or {}

    return _make_response(
        "1.17.1",
        "Advisory Reasoning Foundation",
        "Establishes ATR as a separate advisory intelligence layer.",
        [
            "advisory_reasoning_foundation",
            "runtime_isolation_boundary",
            "module_advisory_support",
            "domain_advisory_support",
            "editor_agent_future_support",
            "backlink_intelligence_future_support",
            "advisory_only_governance",
        ],
    ) | {
        "capabilities": [
            "topic_strategy_advice",
            "topic_gap_advice",
            "cluster_strategy_advice",
            "multi_hop_topic_reasoning_support",
            "module_intelligence_support",
            "domain_advisory_support",
            "editor_advisory_agent_support",
            "backlink_intelligence_support",
        ],
        "boundaries": {
            "can_advise_modules": True,
            "can_advise_users": True,
            "can_generate_reports": True,
            "can_generate_recommendations": True,
            "can_support_future_agent": True,
            "can_support_domain_intelligence": True,
            "can_support_backlink_intelligence": True,
            "can_modify_runtime": False,
            "can_insert_links": False,
            "can_select_targets": False,
            "can_change_scores": False,
            "can_force_highlights": False,
            "can_edit_article_text": False,
            "can_publish_content": False,
        },
        "input_summary": {
            "workspace_id": _safe_text(inputs.get("workspace_id")),
            "domain": _safe_text(inputs.get("domain")),
            "module": _safe_text(inputs.get("module")),
        },
    }


def reason_topic_gaps_v1(existing_topics: List[Dict[str, Any]], expected_topics: List[Dict[str, Any]]) -> Dict[str, Any]:
    existing = {
        _normalize(item.get("topic") or item.get("title") or item.get("name") if isinstance(item, dict) else item)
        for item in existing_topics or []
        if _safe_text(item.get("topic") or item.get("title") or item.get("name") if isinstance(item, dict) else item)
    }

    missing = []
    covered = []

    for item in expected_topics or []:
        topic = _safe_text(item.get("topic") or item.get("title") or item.get("name") if isinstance(item, dict) else item)
        if not topic:
            continue

        key = _normalize(topic)

        if key in existing:
            covered.append({"topic": topic, "status": "covered", "gap_role": "topic_gap_covered"})
        else:
            missing.append({
                "topic": topic,
                "status": "missing",
                "priority": _safe_text(item.get("priority", "medium") if isinstance(item, dict) else "medium"),
                "reason": _safe_text(item.get("reason", "expected_topic_not_found") if isinstance(item, dict) else "expected_topic_not_found"),
                "gap_role": "advisory_topic_gap",
                "recommendation_type": "create_or_strengthen_topic_coverage",
            })

    return _make_response(
        "1.17.2",
        "Topic Gap Reasoning",
        "Identifies missing or weak topic coverage as advisory intelligence only.",
        [
            "topic_gap_reasoning",
            "missing_topic_detection",
            "coverage_gap_reporting",
            "advisory_gap_recommendations",
            "gap_reasoning_audit",
        ],
    ) | {
        "existing_topic_count": len(existing),
        "expected_topic_count": len(expected_topics or []),
        "missing_topics": missing,
        "covered_topics": covered,
    }


def reason_cluster_strategy_v1(clusters: List[Dict[str, Any]]) -> Dict[str, Any]:
    strategy = []

    for cluster in clusters or []:
        name = _safe_text(cluster.get("cluster") or cluster.get("topic") or cluster.get("name") if isinstance(cluster, dict) else cluster)
        page_count = int(cluster.get("page_count", cluster.get("documents", 0)) if isinstance(cluster, dict) else 0)
        strength = _safe_text(cluster.get("strength", "") if isinstance(cluster, dict) else "")

        if not name:
            continue

        if page_count <= 1 or strength == "weak":
            advice = "strengthen_cluster_with_supporting_content"
            priority = "high"
        elif page_count < 4:
            advice = "expand_cluster_depth"
            priority = "medium"
        else:
            advice = "maintain_and_interlink_cluster"
            priority = "low"

        strategy.append({
            "cluster": name,
            "page_count": page_count,
            "priority": priority,
            "advice": advice,
            "strategy_role": "advisory_cluster_strategy",
        })

    return _make_response(
        "1.17.3",
        "Cluster Strategy Reasoning",
        "Produces advisory cluster strategy recommendations without changing links or content.",
        [
            "cluster_strategy_reasoning",
            "weak_cluster_detection",
            "cluster_expansion_advice",
            "cluster_strategy_reporting",
            "cluster_strategy_audit",
        ],
    ) | {
        "cluster_strategy": strategy,
    }


def infer_multi_hop_topics_v1(relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
    adjacency: Dict[str, set] = {}

    for rel in relationships or []:
        source = _safe_text(rel.get("source") if isinstance(rel, dict) else "")
        target = _safe_text(rel.get("target") if isinstance(rel, dict) else "")

        if not source or not target:
            continue

        adjacency.setdefault(source, set()).add(target)

    inferred = []

    for source, mid_targets in adjacency.items():
        for middle in mid_targets:
            for final in adjacency.get(middle, set()):
                if final == source:
                    continue

                inferred.append({
                    "source": source,
                    "via": middle,
                    "target": final,
                    "inference_type": "multi_hop_topic_inference",
                    "advisory_notice": "Inference only; does not create links or alter runtime.",
                })

    return _make_response(
        "1.17.4",
        "Multi-Hop Topic Inference",
        "Infers indirect topic relationships for advisory reasoning only.",
        [
            "multi_hop_topic_inference",
            "indirect_relationship_detection",
            "topic_chain_reasoning",
            "multi_hop_advisory_reporting",
            "multi_hop_audit",
        ],
    ) | {
        "inferred_topic_paths": inferred,
    }


def generate_strategic_recommendations_v1(
    gaps: Dict[str, Any],
    clusters: Dict[str, Any],
    inferences: Dict[str, Any],
) -> Dict[str, Any]:
    recommendations = []

    for gap in gaps.get("missing_topics", []) if isinstance(gaps, dict) else []:
        recommendations.append({
            "type": "topic_gap",
            "priority": gap.get("priority", "medium"),
            "recommendation": f"Create or strengthen coverage for: {gap.get('topic')}",
            "source_layer": "1.17.2",
        })

    for item in clusters.get("cluster_strategy", []) if isinstance(clusters, dict) else []:
        if item.get("priority") in {"high", "medium"}:
            recommendations.append({
                "type": "cluster_strategy",
                "priority": item.get("priority"),
                "recommendation": f"{item.get('advice')} for cluster: {item.get('cluster')}",
                "source_layer": "1.17.3",
            })

    for item in inferences.get("inferred_topic_paths", []) if isinstance(inferences, dict) else []:
        recommendations.append({
            "type": "multi_hop_inference",
            "priority": "medium",
            "recommendation": f"Review indirect topic relationship: {item.get('source')} ? {item.get('target')} via {item.get('via')}",
            "source_layer": "1.17.4",
        })

    return _make_response(
        "1.17.5",
        "Strategic Recommendation Engine",
        "Combines advisory topic gaps, cluster strategy, and multi-hop inference into strategic recommendations.",
        [
            "strategic_recommendation_engine",
            "recommendation_synthesis",
            "topic_strategy_reporting",
            "advisory_recommendation_output",
            "strategy_audit",
        ],
    ) | {
        "recommendations": recommendations,
        "advisory_notice": "Recommendations are advisory only and do not change runtime, links, scores, targets, highlights, publishing, or article text.",
    }




def generate_content_roadmap_intelligence_v1(
    recommendations: Dict[str, Any],
    timeframe: str = "90_days",
) -> Dict[str, Any]:
    """
    1.17.6 Content Roadmap Intelligence.
    Advisory-only roadmap planning from ATR recommendations.
    """

    roadmap = []

    for item in recommendations.get("recommendations", []) if isinstance(recommendations, dict) else []:
        priority = _safe_text(item.get("priority", "medium"))
        recommendation = _safe_text(item.get("recommendation"))

        if not recommendation:
            continue

        phase = "phase_1" if priority == "high" else "phase_2" if priority == "medium" else "phase_3"

        roadmap.append({
            "phase": phase,
            "timeframe": timeframe,
            "priority": priority,
            "recommendation": recommendation,
            "roadmap_role": "advisory_content_roadmap",
        })

    return _make_response(
        "1.17.6",
        "Content Roadmap Intelligence",
        "Turns ATR recommendations into an advisory content roadmap without publishing or editing content.",
        [
            "content_roadmap_intelligence",
            "roadmap_phase_planning",
            "priority_based_content_sequence",
            "advisory_roadmap_reporting",
            "roadmap_audit",
        ],
    ) | {
        "roadmap": roadmap,
        "timeframe": timeframe,
        "advisory_notice": "Roadmap output is advisory only and does not create, edit, schedule, or publish content.",
    }


def analyze_cluster_health_intelligence_v1(
    clusters: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.17.7 Cluster Health Intelligence.
    Advisory-only cluster health analysis.
    """

    health = []

    for item in clusters or []:
        cluster = _safe_text(item.get("cluster") or item.get("topic") or item.get("name") if isinstance(item, dict) else item)
        page_count = int(item.get("page_count", item.get("documents", 0)) if isinstance(item, dict) else 0)
        orphan_count = int(item.get("orphan_count", 0) if isinstance(item, dict) else 0)
        weak_pages = int(item.get("weak_pages", 0) if isinstance(item, dict) else 0)

        if not cluster:
            continue

        score = 100
        if page_count <= 1:
            score -= 45
        elif page_count < 4:
            score -= 20

        score -= min(30, orphan_count * 10)
        score -= min(20, weak_pages * 5)

        score = max(0, min(100, score))

        if score >= 75:
            status = "healthy"
        elif score >= 45:
            status = "needs_attention"
        else:
            status = "weak"

        health.append({
            "cluster": cluster,
            "page_count": page_count,
            "orphan_count": orphan_count,
            "weak_pages": weak_pages,
            "health_score": score,
            "status": status,
            "health_role": "advisory_cluster_health",
        })

    return _make_response(
        "1.17.7",
        "Cluster Health Intelligence",
        "Analyzes cluster health and reports weak topic areas as advisory intelligence only.",
        [
            "cluster_health_intelligence",
            "cluster_health_scoring",
            "weak_cluster_reporting",
            "cluster_health_recommendations",
            "cluster_health_audit",
        ],
    ) | {
        "cluster_health": health,
    }


def reason_topic_expansion_intelligence_v1(
    seed_topics: List[Dict[str, Any]],
    related_topics: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.17.8 Topic Expansion Intelligence.
    Advisory-only topic expansion support.
    """

    seeds = {
        _normalize(item.get("topic") or item.get("title") or item.get("name") if isinstance(item, dict) else item)
        for item in seed_topics or []
        if _safe_text(item.get("topic") or item.get("title") or item.get("name") if isinstance(item, dict) else item)
    }

    expansions = []

    for item in related_topics or []:
        topic = _safe_text(item.get("topic") or item.get("title") or item.get("name") if isinstance(item, dict) else item)
        parent = _safe_text(item.get("parent") or item.get("seed") if isinstance(item, dict) else "")
        reason = _safe_text(item.get("reason", "related_topic_expansion") if isinstance(item, dict) else "related_topic_expansion")

        if not topic:
            continue

        if _normalize(topic) in seeds:
            continue

        expansions.append({
            "topic": topic,
            "parent_topic": parent,
            "reason": reason,
            "expansion_role": "advisory_topic_expansion",
            "recommendation_type": "consider_topic_expansion",
        })

    return _make_response(
        "1.17.8",
        "Topic Expansion Intelligence",
        "Suggests related topic expansion opportunities as advisory intelligence only.",
        [
            "topic_expansion_intelligence",
            "related_topic_suggestion",
            "semantic_expansion_reporting",
            "topic_expansion_advisory",
            "topic_expansion_audit",
        ],
    ) | {
        "topic_expansions": expansions,
    }


def detect_emerging_topic_intelligence_v1(
    topic_signals: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.17.9 Emerging Topic Intelligence.
    Advisory-only emerging topic detection.
    """

    emerging = []

    for item in topic_signals or []:
        topic = _safe_text(item.get("topic") or item.get("name") if isinstance(item, dict) else item)
        growth = float(item.get("growth_score", item.get("growth", 0)) if isinstance(item, dict) else 0)
        frequency = int(item.get("frequency", 0) if isinstance(item, dict) else 0)

        if not topic:
            continue

        if growth >= 0.7 or frequency >= 5:
            emerging.append({
                "topic": topic,
                "growth_score": growth,
                "frequency": frequency,
                "status": "emerging",
                "emerging_role": "advisory_emerging_topic",
                "recommendation_type": "monitor_or_expand_topic",
            })

    return _make_response(
        "1.17.9",
        "Emerging Topic Intelligence",
        "Detects emerging topic opportunities from trend-like signals as advisory intelligence only.",
        [
            "emerging_topic_intelligence",
            "topic_growth_signal_detection",
            "topic_trend_reporting",
            "emerging_topic_advisory",
            "emerging_topic_audit",
        ],
    ) | {
        "emerging_topics": emerging,
    }


def reason_topic_authority_intelligence_v1(
    clusters: List[Dict[str, Any]],
    backlink_signals: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """
    1.17.10 Topic Authority Intelligence.
    Advisory-only topic authority analysis.
    """

    backlink_signals = backlink_signals or []
    backlink_map = {}

    for signal in backlink_signals:
        topic = _normalize(signal.get("topic") if isinstance(signal, dict) else "")
        backlinks = int(signal.get("backlinks", 0) if isinstance(signal, dict) else 0)
        authority = float(signal.get("authority", 0) if isinstance(signal, dict) else 0)
        backlink_map[topic] = {"backlinks": backlinks, "authority": authority}

    authority_report = []

    for item in clusters or []:
        topic = _safe_text(item.get("cluster") or item.get("topic") or item.get("name") if isinstance(item, dict) else item)
        page_count = int(item.get("page_count", item.get("documents", 0)) if isinstance(item, dict) else 0)

        if not topic:
            continue

        signal = backlink_map.get(_normalize(topic), {"backlinks": 0, "authority": 0})
        backlinks = signal["backlinks"]
        external_authority = signal["authority"]

        authority_score = min(100, (page_count * 12) + (backlinks * 4) + int(external_authority * 20))

        if authority_score >= 75:
            status = "strong_authority"
        elif authority_score >= 40:
            status = "moderate_authority"
        else:
            status = "authority_gap"

        authority_report.append({
            "topic": topic,
            "page_count": page_count,
            "backlinks": backlinks,
            "external_authority": external_authority,
            "authority_score": authority_score,
            "status": status,
            "authority_role": "advisory_topic_authority",
        })

    return _make_response(
        "1.17.10",
        "Topic Authority Intelligence",
        "Analyzes topic authority strength using content and optional backlink signals as advisory intelligence only.",
        [
            "topic_authority_intelligence",
            "authority_gap_reporting",
            "topic_authority_scoring",
            "backlink_signal_support",
            "topic_authority_audit",
        ],
    ) | {
        "topic_authority": authority_report,
    }




def support_topic_cluster_generator_v1(
    topics: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.17.11 Topic Cluster Generator Support.
    Advisory intelligence provider for Topic Cluster Generator.
    """

    clusters = []

    for item in topics or []:
        topic = _safe_text(item.get("topic") if isinstance(item, dict) else item)

        if not topic:
            continue

        clusters.append({
            "topic": topic,
            "cluster_support_role": "topic_cluster_generator_support",
            "recommendation": "eligible_for_cluster_generation",
        })

    return _make_response(
        "1.17.11",
        "Topic Cluster Generator Support",
        "Provides advisory intelligence to the Topic Cluster Generator.",
        [
            "topic_cluster_generator_support",
            "cluster_candidate_support",
            "cluster_seed_support",
            "cluster_intelligence_bridge",
            "cluster_support_audit",
        ],
    ) | {
        "cluster_support": clusters,
    }


def support_topic_gap_filler_v1(
    gaps: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.17.12 Topic Gap Filler Support.
    Advisory intelligence provider for Topic Gap Filler.
    """

    opportunities = []

    for item in gaps or []:
        topic = _safe_text(item.get("topic") if isinstance(item, dict) else item)

        if not topic:
            continue

        opportunities.append({
            "topic": topic,
            "gap_support_role": "topic_gap_filler_support",
            "recommendation": "consider_gap_fill_content",
        })

    return _make_response(
        "1.17.12",
        "Topic Gap Filler Support",
        "Provides advisory intelligence to Topic Gap Filler modules.",
        [
            "topic_gap_filler_support",
            "gap_candidate_support",
            "gap_expansion_support",
            "gap_intelligence_bridge",
            "gap_support_audit",
        ],
    ) | {
        "gap_support": opportunities,
    }


def support_writing_intelligence_v1(
    topics: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.17.13 Writing Intelligence Support.
    Advisory intelligence provider for future writing systems.
    """

    writing_guidance = []

    for item in topics or []:
        topic = _safe_text(item.get("topic") if isinstance(item, dict) else item)

        if not topic:
            continue

        writing_guidance.append({
            "topic": topic,
            "writing_support_role": "writing_intelligence_support",
            "guidance": "expand_topic_depth_and_supporting_subtopics",
        })

    return _make_response(
        "1.17.13",
        "Writing Intelligence Support",
        "Provides advisory topic intelligence for future writing systems.",
        [
            "writing_intelligence_support",
            "topic_depth_guidance",
            "supporting_topic_guidance",
            "writing_intelligence_bridge",
            "writing_support_audit",
        ],
    ) | {
        "writing_support": writing_guidance,
    }


def support_media_content_intelligence_v1(
    topics: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.17.14 Media Content Intelligence Support.
    Advisory intelligence provider for future media systems.
    """

    media_support = []

    for item in topics or []:
        topic = _safe_text(item.get("topic") if isinstance(item, dict) else item)

        if not topic:
            continue

        media_support.append({
            "topic": topic,
            "media_support_role": "media_content_intelligence_support",
            "recommendation": "potential_media_content_opportunity",
        })

    return _make_response(
        "1.17.14",
        "Media Content Intelligence Support",
        "Provides advisory intelligence for future media content systems.",
        [
            "media_content_intelligence_support",
            "media_topic_support",
            "media_opportunity_support",
            "media_intelligence_bridge",
            "media_support_audit",
        ],
    ) | {
        "media_support": media_support,
    }


def support_future_models_v1(
    model_requests: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.17.15 Future Model Intelligence Support.
    Advisory intelligence bridge for future LinkCraftor models.
    """

    model_support = []

    for item in model_requests or []:
        model_name = _safe_text(item.get("model") or item.get("name") if isinstance(item, dict) else item)

        if not model_name:
            continue

        model_support.append({
            "model": model_name,
            "support_role": "future_model_intelligence_support",
            "intelligence_source": "advanced_topic_reasoning_layer",
        })

    return _make_response(
        "1.17.15",
        "Future Model Intelligence Support",
        "Provides advisory intelligence to future LinkCraftor models.",
        [
            "future_model_support",
            "intelligence_reuse",
            "module_intelligence_bridge",
            "future_model_advisory_support",
            "future_model_audit",
        ],
    ) | {
        "future_model_support": model_support,
    }




def establish_domain_advisory_scan_foundation_v1(
    domain_context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    1.17.16 Domain Advisory Scan Foundation.
    Advisory-only foundation for future domain/full-site intelligence.
    This does not crawl websites.
    """

    domain = _safe_text(domain_context.get("domain") if isinstance(domain_context, dict) else "")
    workspace_id = _safe_text(domain_context.get("workspace_id") if isinstance(domain_context, dict) else "")
    source_type = _safe_text(domain_context.get("source_type", "domain_context") if isinstance(domain_context, dict) else "domain_context")

    return _make_response(
        "1.17.16",
        "Domain Advisory Scan Foundation",
        "Establishes advisory-only domain scan support for future connected-domain and full-site intelligence.",
        [
            "domain_advisory_scan_foundation",
            "connected_domain_context_support",
            "future_full_site_scan_support",
            "domain_intelligence_boundary",
            "domain_scan_audit",
        ],
    ) | {
        "domain_context": {
            "workspace_id": workspace_id,
            "domain": domain,
            "source_type": source_type,
            "scan_role": "advisory_domain_scan_foundation",
        },
        "boundaries": {
            "does_not_crawl_website": True,
            "does_not_modify_website": True,
            "does_not_publish_content": True,
            "does_not_create_links": True,
            "future_crawler_can_feed_this_layer": True,
        },
    }


def analyze_full_site_topic_intelligence_v1(
    pages: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.17.17 Full-Site Topic Intelligence.
    Advisory-only topic intelligence across provided site page data.
    """

    topic_map: Dict[str, List[Dict[str, Any]]] = {}

    for page in pages or []:
        url = _safe_text(page.get("url") if isinstance(page, dict) else "")
        title = _safe_text(page.get("title") if isinstance(page, dict) else "")
        topics = page.get("topics", []) if isinstance(page, dict) else []

        for topic in topics:
            topic_text = _safe_text(topic)
            topic_key = _normalize(topic_text)

            if not topic_key:
                continue

            topic_map.setdefault(topic_key, []).append({
                "url": url,
                "title": title,
                "topic": topic_text,
            })

    site_topics = [
        {
            "topic": items[0]["topic"],
            "page_count": len(items),
            "pages": items,
            "site_topic_role": "full_site_topic_intelligence",
        }
        for items in topic_map.values()
    ]

    site_topics.sort(key=lambda x: x["page_count"], reverse=True)

    return _make_response(
        "1.17.17",
        "Full-Site Topic Intelligence",
        "Analyzes provided site page data to report site-wide topic coverage as advisory intelligence only.",
        [
            "full_site_topic_intelligence",
            "site_topic_coverage_reporting",
            "topic_distribution_analysis",
            "domain_topic_visibility",
            "full_site_topic_audit",
        ],
    ) | {
        "site_topics": site_topics,
        "page_count": len(pages or []),
    }


def analyze_cross_page_relationship_intelligence_v1(
    pages: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.17.18 Cross-Page Relationship Intelligence.
    Advisory-only relationship analysis across provided page data.
    """

    relationships = []

    for i, source in enumerate(pages or []):
        source_url = _safe_text(source.get("url") if isinstance(source, dict) else "")
        source_title = _safe_text(source.get("title") if isinstance(source, dict) else "")
        source_topics = set(_normalize(t) for t in (source.get("topics", []) if isinstance(source, dict) else []))

        for target in (pages or [])[i + 1:]:
            target_url = _safe_text(target.get("url") if isinstance(target, dict) else "")
            target_title = _safe_text(target.get("title") if isinstance(target, dict) else "")
            target_topics = set(_normalize(t) for t in (target.get("topics", []) if isinstance(target, dict) else []))

            shared = sorted(source_topics & target_topics)

            if not shared:
                continue

            relationships.append({
                "source_url": source_url,
                "source_title": source_title,
                "target_url": target_url,
                "target_title": target_title,
                "shared_topics": shared,
                "relationship_role": "cross_page_relationship_intelligence",
                "advisory_notice": "Relationship only; does not insert links.",
            })

    return _make_response(
        "1.17.18",
        "Cross-Page Relationship Intelligence",
        "Finds cross-page semantic relationships as advisory intelligence only.",
        [
            "cross_page_relationship_intelligence",
            "shared_topic_relationship_detection",
            "page_relationship_reporting",
            "advisory_link_opportunity_context",
            "cross_page_relationship_audit",
        ],
    ) | {
        "cross_page_relationships": relationships,
    }


def analyze_site_cluster_intelligence_v1(
    pages: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.17.19 Site Cluster Intelligence.
    Advisory-only site cluster analysis across provided page data.
    """

    topic_intel = analyze_full_site_topic_intelligence_v1(pages)
    clusters = []

    for topic in topic_intel.get("site_topics", []):
        page_count = int(topic.get("page_count", 0))
        if page_count >= 5:
            cluster_status = "strong_cluster"
        elif page_count >= 2:
            cluster_status = "developing_cluster"
        else:
            cluster_status = "thin_cluster"

        clusters.append({
            "topic": topic.get("topic"),
            "page_count": page_count,
            "cluster_status": cluster_status,
            "cluster_role": "site_cluster_intelligence",
            "recommendation": "expand_cluster" if cluster_status == "thin_cluster" else "strengthen_internal_support",
        })

    return _make_response(
        "1.17.19",
        "Site Cluster Intelligence",
        "Analyzes site-level topic clusters as advisory intelligence only.",
        [
            "site_cluster_intelligence",
            "cluster_status_reporting",
            "thin_cluster_detection",
            "cluster_expansion_context",
            "site_cluster_audit",
        ],
    ) | {
        "site_clusters": clusters,
    }


def analyze_site_opportunity_intelligence_v1(
    pages: List[Dict[str, Any]],
    expected_topics: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """
    1.17.20 Site Opportunity Intelligence.
    Advisory-only opportunity analysis across site topics, clusters, and expected topics.
    """

    expected_topics = expected_topics or []

    site_topics = analyze_full_site_topic_intelligence_v1(pages)
    existing_topics = [{"topic": item.get("topic")} for item in site_topics.get("site_topics", [])]
    gaps = reason_topic_gaps_v1(existing_topics, expected_topics)
    clusters = analyze_site_cluster_intelligence_v1(pages)

    opportunities = []

    for gap in gaps.get("missing_topics", []):
        opportunities.append({
            "type": "missing_topic_opportunity",
            "topic": gap.get("topic"),
            "priority": gap.get("priority", "medium"),
            "recommendation": "consider_new_content_or_cluster_expansion",
        })

    for cluster in clusters.get("site_clusters", []):
        if cluster.get("cluster_status") == "thin_cluster":
            opportunities.append({
                "type": "thin_cluster_opportunity",
                "topic": cluster.get("topic"),
                "priority": "medium",
                "recommendation": "expand_thin_cluster",
            })

    return _make_response(
        "1.17.20",
        "Site Opportunity Intelligence",
        "Combines site topics, clusters, and gaps into advisory opportunity recommendations.",
        [
            "site_opportunity_intelligence",
            "site_gap_opportunity_reporting",
            "thin_cluster_opportunity_detection",
            "domain_advisory_recommendations",
            "site_opportunity_audit",
        ],
    ) | {
        "site_opportunities": opportunities,
        "advisory_notice": "Site opportunities are advisory only and do not crawl, edit, publish, link, score, or alter runtime.",
    }




def establish_editor_advisory_agent_foundation_v1(
    workspace_context: Dict[str, Any],
) -> Dict[str, Any]:
    return _make_response(
        "1.17.21",
        "Editor Advisory Agent Foundation",
        "Establishes the ATR advisory agent foundation.",
        [
            "editor_advisory_agent_foundation",
            "workspace_consultation_support",
            "topic_reasoning_consultation",
            "advisory_only_agent",
            "agent_foundation_audit",
        ],
    ) | {
        "workspace_context": workspace_context or {},
        "agent_role": "advisory_only",
    }


def ask_the_strategist_v1(
    question: str,
    context: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _make_response(
        "1.17.22",
        "Ask-The-Strategist Interface",
        "Allows future users to ask ATR strategic questions.",
        [
            "ask_the_strategist",
            "strategy_question_support",
            "topic_consultation_interface",
            "advisory_question_handling",
            "strategist_audit",
        ],
    ) | {
        "question": _safe_text(question),
        "context": context or {},
        "response_mode": "advisory_only",
    }


def generate_advisory_reasoning_response_v1(
    question: str,
    recommendations: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    recommendations = recommendations or []

    response = {
        "question": _safe_text(question),
        "recommendation_count": len(recommendations),
        "response_type": "advisory_reasoning_response",
        "advisory_notice": "Recommendations are advisory only.",
    }

    return _make_response(
        "1.17.23",
        "Advisory Reasoning Responses",
        "Produces advisory reasoning responses from ATR intelligence.",
        [
            "advisory_reasoning_response",
            "reasoning_synthesis",
            "strategic_response_generation",
            "consultation_output",
            "reasoning_response_audit",
        ],
    ) | {
        "response": response,
    }


def consult_workspace_intelligence_v1(
    workspace_data: Dict[str, Any],
) -> Dict[str, Any]:
    return _make_response(
        "1.17.24",
        "Workspace Intelligence Consultation",
        "Provides advisory consultation from workspace intelligence.",
        [
            "workspace_intelligence_consultation",
            "workspace_strategy_support",
            "workspace_topic_consultation",
            "workspace_advisory_reporting",
            "workspace_consultation_audit",
        ],
    ) | {
        "workspace_summary": workspace_data or {},
        "consultation_role": "advisory_only",
    }




def reason_backlink_opportunities_v1(
    topics: List[Dict[str, Any]],
    backlink_sources: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """
    1.17.25 Backlink Opportunity Reasoning.
    Advisory-only backlink opportunity analysis.
    """

    backlink_sources = backlink_sources or []

    opportunities = []

    for item in topics or []:
        topic = _safe_text(item.get("topic") if isinstance(item, dict) else item)

        if not topic:
            continue

        opportunities.append({
            "topic": topic,
            "opportunity_type": "backlink_opportunity",
            "recommendation": "seek_relevant_authoritative_references",
            "advisory_only": True,
        })

    return _make_response(
        "1.17.25",
        "Backlink Opportunity Reasoning",
        "Identifies backlink opportunities as advisory intelligence only.",
        [
            "backlink_opportunity_reasoning",
            "backlink_gap_analysis",
            "authority_opportunity_detection",
            "backlink_strategy_support",
            "backlink_opportunity_audit",
        ],
    ) | {
        "backlink_opportunities": opportunities,
    }


def detect_authority_gaps_v1(
    topic_authority: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.17.26 Authority Gap Detection.
    Advisory-only authority gap analysis.
    """

    gaps = []

    for item in topic_authority or []:
        topic = _safe_text(item.get("topic") if isinstance(item, dict) else "")
        score = float(item.get("authority_score", 0) if isinstance(item, dict) else 0)

        if not topic:
            continue

        if score < 40:
            gaps.append({
                "topic": topic,
                "authority_score": score,
                "gap_type": "authority_gap",
                "recommendation": "strengthen_topic_authority",
            })

    return _make_response(
        "1.17.26",
        "Authority Gap Detection",
        "Detects authority weaknesses as advisory intelligence only.",
        [
            "authority_gap_detection",
            "authority_weakness_reporting",
            "authority_gap_analysis",
            "authority_growth_support",
            "authority_gap_audit",
        ],
    ) | {
        "authority_gaps": gaps,
    }


def analyze_competitor_backlink_intelligence_v1(
    competitor_data: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.17.27 Competitor Backlink Intelligence.
    Advisory-only competitor backlink insight.
    """

    insights = []

    for item in competitor_data or []:
        competitor = _safe_text(item.get("competitor") if isinstance(item, dict) else "")
        backlinks = int(item.get("backlinks", 0) if isinstance(item, dict) else 0)

        if not competitor:
            continue

        insights.append({
            "competitor": competitor,
            "backlinks": backlinks,
            "insight_type": "competitor_backlink_intelligence",
            "recommendation": "analyze_competitor_authority_sources",
        })

    return _make_response(
        "1.17.27",
        "Competitor Backlink Intelligence",
        "Provides advisory competitor backlink intelligence.",
        [
            "competitor_backlink_intelligence",
            "competitor_authority_analysis",
            "competitor_link_insight",
            "competitive_gap_support",
            "competitor_backlink_audit",
        ],
    ) | {
        "competitor_insights": insights,
    }


def recommend_linkable_assets_v1(
    pages: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    1.17.28 Linkable Asset Recommendations.
    Advisory-only linkable asset identification.
    """

    assets = []

    for page in pages or []:
        title = _safe_text(page.get("title") if isinstance(page, dict) else "")
        page_type = _safe_text(page.get("type", "content") if isinstance(page, dict) else "content")

        if not title:
            continue

        assets.append({
            "title": title,
            "page_type": page_type,
            "asset_role": "linkable_asset_candidate",
            "recommendation": "consider_promoting_as_authority_asset",
        })

    return _make_response(
        "1.17.28",
        "Linkable Asset Recommendations",
        "Identifies potential linkable assets as advisory intelligence only.",
        [
            "linkable_asset_recommendations",
            "authority_asset_identification",
            "content_asset_analysis",
            "asset_growth_support",
            "linkable_asset_audit",
        ],
    ) | {
        "linkable_assets": assets,
    }


def reason_topic_authority_strategy_v1(
    authority_gaps: Dict[str, Any],
    backlink_opportunities: Dict[str, Any],
) -> Dict[str, Any]:
    """
    1.17.29 Topic Authority Strategy.
    Advisory-only authority strategy generation.
    """

    strategies = []

    for gap in authority_gaps.get("authority_gaps", []):
        strategies.append({
            "topic": gap.get("topic"),
            "strategy_type": "authority_growth_strategy",
            "recommendation": "expand_content_depth_and_authority_signals",
        })

    return _make_response(
        "1.17.29",
        "Topic Authority Strategy",
        "Generates advisory topic authority strategies.",
        [
            "topic_authority_strategy",
            "authority_growth_planning",
            "authority_gap_resolution",
            "authority_strategy_support",
            "topic_authority_audit",
        ],
    ) | {
        "authority_strategies": strategies,
        "backlink_opportunity_count": len(backlink_opportunities.get("backlink_opportunities", [])),
    }




def enforce_advisory_only_mode_v1() -> Dict[str, Any]:
    """
    1.17.30 Advisory-Only Enforcement.
    Permanent governance rules for ATR.
    """

    return _make_response(
        "1.17.30",
        "Advisory-Only Enforcement",
        "Permanently enforces advisory-only behavior for ATR.",
        [
            "advisory_only_enforcement",
            "advisory_governance",
            "advisory_boundaries",
            "runtime_protection",
            "advisory_audit",
        ],
    ) | {
        "enforcement_rules": {
            "can_advise": True,
            "can_recommend": True,
            "can_reason": True,
            "can_analyze": True,
            "can_modify_runtime": False,
            "can_insert_links": False,
            "can_modify_scores": False,
            "can_modify_targets": False,
            "can_publish_content": False,
        }
    }


def enforce_runtime_isolation_v1() -> Dict[str, Any]:
    """
    1.17.31 Runtime Isolation Enforcement.
    ATR may observe runtime but cannot control it.
    """

    return _make_response(
        "1.17.31",
        "Runtime Isolation Enforcement",
        "Permanently isolates ATR from runtime control.",
        [
            "runtime_isolation",
            "runtime_observation_only",
            "engine_protection",
            "runtime_boundary_enforcement",
            "runtime_isolation_audit",
        ],
    ) | {
        "runtime_boundaries": {
            "may_observe_runtime": True,
            "may_control_runtime": False,
            "may_change_highlights": False,
            "may_change_scores": False,
            "may_change_targets": False,
            "may_change_linking_logic": False,
        }
    }


def govern_module_access_v1(
    modules: List[str] | None = None,
) -> Dict[str, Any]:
    """
    1.17.32 Module Access Governance.
    Controls which modules may consult ATR.
    """

    modules = modules or []

    approved = []

    for module in modules:
        approved.append({
            "module": _safe_text(module),
            "access_type": "consultation_only",
            "execution_access": False,
        })

    return _make_response(
        "1.17.32",
        "Module Access Governance",
        "Controls advisory consultation access to ATR.",
        [
            "module_access_governance",
            "consultation_access",
            "module_boundary_protection",
            "atr_access_control",
            "module_access_audit",
        ],
    ) | {
        "approved_modules": approved,
    }


def generate_reasoning_audit_v1(
    recommendation: str,
    evidence: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """
    1.17.33 Explainability & Reasoning Audit.
    Produces explainable recommendation evidence chains.
    """

    evidence = evidence or []

    return _make_response(
        "1.17.33",
        "Explainability & Reasoning Audit",
        "Provides evidence-backed advisory reasoning trails.",
        [
            "reasoning_audit",
            "explainability_layer",
            "evidence_chain",
            "recommendation_traceability",
            "reasoning_audit_log",
        ],
    ) | {
        "recommendation": recommendation,
        "evidence_count": len(evidence),
        "evidence": evidence,
        "audit_role": "explainability_only",
    }


def explain_advanced_topic_reasoning_layer_v1() -> Dict[str, Any]:
    return {
        "layer": "1.17",
        "name": "Advanced Topic Reasoning Layer",
        "status": "active",
        "scope": "advisory_topic_reasoning_intelligence",
        "sub_layers": [
            "1.17.1 Advisory Reasoning Foundation",
            "1.17.2 Topic Gap Reasoning",
            "1.17.3 Cluster Strategy Reasoning",
            "1.17.4 Multi-Hop Topic Inference",
            "1.17.5 Strategic Recommendation Engine",
            "1.17.6 Content Roadmap Intelligence",
            "1.17.7 Cluster Health Intelligence",
            "1.17.8 Topic Expansion Intelligence",
            "1.17.9 Emerging Topic Intelligence",
            "1.17.10 Topic Authority Intelligence",
            "1.17.11 Topic Cluster Generator Support",
            "1.17.12 Topic Gap Filler Support",
            "1.17.13 Writing Intelligence Support",
            "1.17.14 Media Content Intelligence Support",
            "1.17.15 Future Model Intelligence Support",
            "1.17.16 Domain Advisory Scan Foundation",
            "1.17.17 Full-Site Topic Intelligence",
            "1.17.18 Cross-Page Relationship Intelligence",
            "1.17.19 Site Cluster Intelligence",
            "1.17.20 Site Opportunity Intelligence",
            "1.17.21 Editor Advisory Agent Foundation",
            "1.17.22 Ask-The-Strategist Interface",
            "1.17.23 Advisory Reasoning Responses",
            "1.17.24 Workspace Intelligence Consultation",
            "1.17.25 Backlink Opportunity Reasoning",
            "1.17.26 Authority Gap Detection",
            "1.17.27 Competitor Backlink Intelligence",
            "1.17.28 Linkable Asset Recommendations",
            "1.17.29 Topic Authority Strategy",
            "1.17.30 Advisory-Only Enforcement",
            "1.17.31 Runtime Isolation Enforcement",
            "1.17.32 Module Access Governance",
            "1.17.33 Explainability & Reasoning Audit",
        ],
        "future_capabilities": [

            "Topic Cluster Generator Support",
            "Topic Gap Filler Support",
            "Writing Intelligence Support",
            "Media Content Intelligence Support",
            "Future Model Intelligence Support",
            "Domain Advisory Scan Foundation",
            "Full-Site Topic Intelligence",
            "Editor Advisory Agent Foundation",
            "Backlink Intelligence Support",
        ],
        "safety_rules": {
            "advisory_only": True,
            "separate_from_runtime_engine": True,
            "does_not_modify_uploaded_article": True,
            "does_not_edit_article_text": True,
            "does_not_publish_content": True,
            "does_not_create_runtime_router": True,
            "does_not_create_new_target_selector": True,
            "does_not_replace_existing_scoring": True,
            "does_not_force_link_decisions": True,
            "does_not_force_highlights": True,
            "does_not_alter_internal_linking_logic": True,
            "does_not_alter_semantic_linking_logic": True,
        },
    }
