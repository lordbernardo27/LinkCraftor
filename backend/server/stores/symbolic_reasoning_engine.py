
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


BUILD_ID = "PHASE-2.6.1.1-SYMBOL-EXTRACTION-V1-SHADOW-RUNTIME"


SYMBOL_KEYWORDS = {
    "TOOL_INTENT": [
        "calculator",
        "checker",
        "generator",
        "converter",
        "tool",
        "estimator",
        "planner",
    ],
    "INFORMATIONAL_INTENT": [
        "what is",
        "how to",
        "guide",
        "meaning",
        "definition",
        "learn",
        "understand",
    ],
    "COMPARISON_INTENT": [
        "vs",
        "versus",
        "compare",
        "comparison",
        "best",
        "alternative",
    ],
    "ACTIONABLE_INTENT": [
        "checklist",
        "steps",
        "fix",
        "improve",
        "audit",
        "optimize",
    ],
    "HEALTH_DOMAIN": [
        "bmi",
        "pregnancy",
        "ovulation",
        "calorie",
        "blood pressure",
        "amlodipine",
        "dose",
    ],
    "SEO_DOMAIN": [
        "seo",
        "internal link",
        "backlink",
        "keyword",
        "ranking",
        "topic cluster",
        "authority",
    ],
    "CALCULATOR_PAGE": [
        "calculator",
        "calculate",
        "estimator",
    ],
    "GUIDE_PAGE": [
        "guide",
        "how to",
        "what is",
        "learn",
    ],
}


@dataclass(frozen=True)
class SymbolExtractionResult:
    build_id: str
    layer: str
    shadow_runtime: bool
    can_influence_runtime: bool

    input_text: str
    symbols: List[Dict[str, Any]] = field(default_factory=list)
    symbol_count: int = 0

    symbolic_score: float = 0.0
    reasoning_chain: List[str] = field(default_factory=list)

    safety_flags: Dict[str, bool] = field(default_factory=dict)

    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def extract_symbols_v1(
    text: str,
    *,
    source: str = "unknown",
) -> Dict[str, Any]:
    """
    2.6.1.1 Symbol Extraction.

    Shadow runtime:
    - Extracts symbolic concepts from anchor/context/target text.
    - Does not modify score, target, URL, highlight, or link decisions.
    """

    raw_text = str(text or "")
    clean = _clean_text(raw_text)

    symbols: List[Dict[str, Any]] = []
    reasoning_chain: List[str] = []

    for symbol_type, keywords in SYMBOL_KEYWORDS.items():
        matched_keywords = []

        for kw in keywords:
            k = _clean_text(kw)
            if not k:
                continue

            if k in clean:
                matched_keywords.append(kw)

        if matched_keywords:
            confidence = min(1.0, round(0.45 + (len(matched_keywords) * 0.15), 4))

            symbols.append({
                "symbol": symbol_type,
                "source": source,
                "matched_keywords": matched_keywords,
                "confidence": confidence,
            })

            reasoning_chain.append(
                f"{symbol_type} detected from {len(matched_keywords)} keyword match(es)."
            )

    symbolic_score = round(
        sum(float(x.get("confidence") or 0) for x in symbols) / max(1, len(symbols)),
        4,
    )

    result = SymbolExtractionResult(
        build_id=BUILD_ID,
        layer="2.6.1.1 Symbol Extraction",
        shadow_runtime=True,
        can_influence_runtime=False,
        input_text=raw_text,
        symbols=symbols,
        symbol_count=len(symbols),
        symbolic_score=symbolic_score,
        reasoning_chain=reasoning_chain,
        safety_flags={
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "runtime_shadow_only": True,
            "metadata_only": True,
        },
    )

    return asdict(result)


def explain_symbol_extraction_v1() -> Dict[str, Any]:
    return {
        "build_id": BUILD_ID,
        "layer": "2.6.1.1 Symbol Extraction",
        "mode": "shadow_runtime",
        "can_influence_runtime": False,
        "purpose": "Extract symbolic concepts from text for future symbolic-neural reasoning.",
        "symbol_types": sorted(SYMBOL_KEYWORDS.keys()),
    }



def _safe_workspace_id(workspace_id: str | None) -> str:
    value = str(workspace_id or "default").strip()
    value = re.sub(r"[^a-zA-Z0-9_.-]+", "_", value)
    return value or "default"


def _symbol_data_dir_v1() -> "Path":
    from pathlib import Path
    path = Path("backend/server/data/symbolic_reasoning")
    path.mkdir(parents=True, exist_ok=True)
    return path


def symbol_store_path_v1(workspace_id: str | None) -> "Path":
    """
    2.6.1.2 Symbol Storage Path.

    Workspace-scoped symbol memory path.
    """
    return _symbol_data_dir_v1() / f"{_safe_workspace_id(workspace_id)}_symbols.json"


def load_workspace_symbols_v1(
    workspace_id: str | None,
) -> Dict[str, Any]:
    """
    2.6.1.2 Load Workspace Symbols.

    Shadow runtime:
    - Loads persisted symbolic memory.
    - Does not affect scoring, targets, URLs, highlights, or linking.
    """
    import json

    path = symbol_store_path_v1(workspace_id)

    if not path.exists():
        return {
            "build_id": BUILD_ID,
            "layer": "2.6.1.2 Symbol Storage",
            "workspace_id": _safe_workspace_id(workspace_id),
            "symbols": [],
            "symbol_count": 0,
            "shadow_runtime": True,
            "can_influence_runtime": False,
        }

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "build_id": BUILD_ID,
            "layer": "2.6.1.2 Symbol Storage",
            "workspace_id": _safe_workspace_id(workspace_id),
            "symbols": [],
            "symbol_count": 0,
            "shadow_runtime": True,
            "can_influence_runtime": False,
            "load_error": True,
        }

    symbols = data.get("symbols") if isinstance(data.get("symbols"), list) else []

    return {
        **data,
        "symbols": symbols,
        "symbol_count": len(symbols),
        "shadow_runtime": True,
        "can_influence_runtime": False,
    }


def save_workspace_symbols_v1(
    workspace_id: str | None,
    symbols: List[Dict[str, Any]] | None,
) -> Dict[str, Any]:
    """
    2.6.1.2 Save Workspace Symbols.

    Shadow runtime:
    - Persists symbolic memory for later analysis.
    - Does not affect scoring, targets, URLs, highlights, or linking.
    """
    import json

    clean_symbols = [
        dict(x)
        for x in (symbols or [])
        if isinstance(x, dict)
    ]

    payload = {
        "build_id": BUILD_ID,
        "layer": "2.6.1.2 Symbol Storage",
        "workspace_id": _safe_workspace_id(workspace_id),
        "symbols": clean_symbols,
        "symbol_count": len(clean_symbols),
        "shadow_runtime": True,
        "can_influence_runtime": False,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "safety_flags": {
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "runtime_shadow_only": True,
            "metadata_only": True,
        },
    }

    path = symbol_store_path_v1(workspace_id)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return payload


def append_workspace_symbol_snapshot_v1(
    workspace_id: str | None,
    extraction_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    2.6.1.2 Append Workspace Symbol Snapshot.

    Shadow runtime:
    - Adds newly extracted symbols to workspace symbolic memory.
    - Does not deduplicate aggressively yet.
    - Does not affect runtime decisions.
    """

    current = load_workspace_symbols_v1(workspace_id)
    existing = current.get("symbols") if isinstance(current.get("symbols"), list) else []

    new_symbols = (
        extraction_result.get("symbols")
        if isinstance(extraction_result.get("symbols"), list)
        else []
    )

    merged = existing + [
        dict(x)
        for x in new_symbols
        if isinstance(x, dict)
    ]

    saved = save_workspace_symbols_v1(
        workspace_id=workspace_id,
        symbols=merged,
    )

    return {
        "build_id": BUILD_ID,
        "layer": "2.6.1.2 Symbol Storage",
        "workspace_id": _safe_workspace_id(workspace_id),
        "appended_count": len(new_symbols),
        "total_symbol_count": saved.get("symbol_count", 0),
        "shadow_runtime": True,
        "can_influence_runtime": False,
        "store_path": str(symbol_store_path_v1(workspace_id)),
        "safety_flags": saved.get("safety_flags", {}),
    }



SYMBOLIC_RULES_V1 = [
    {
        "rule_id": "SYM_RULE_001",
        "name": "tool_page_alignment",
        "required_symbols": ["TOOL_INTENT", "CALCULATOR_PAGE"],
        "rule_score": 0.85,
        "reason": "Tool intent aligns with calculator/tool page behavior.",
    },
    {
        "rule_id": "SYM_RULE_002",
        "name": "informational_guide_alignment",
        "required_symbols": ["INFORMATIONAL_INTENT", "GUIDE_PAGE"],
        "rule_score": 0.80,
        "reason": "Informational intent aligns with guide-style content.",
    },
    {
        "rule_id": "SYM_RULE_003",
        "name": "comparison_content_alignment",
        "required_symbols": ["COMPARISON_INTENT"],
        "rule_score": 0.70,
        "reason": "Comparison intent detected and should be treated as comparison-aware content.",
    },
    {
        "rule_id": "SYM_RULE_004",
        "name": "seo_actionable_alignment",
        "required_symbols": ["SEO_DOMAIN", "ACTIONABLE_INTENT"],
        "rule_score": 0.82,
        "reason": "SEO domain content with actionable intent supports tactical SEO guidance.",
    },
    {
        "rule_id": "SYM_RULE_005",
        "name": "health_tool_alignment",
        "required_symbols": ["HEALTH_DOMAIN", "TOOL_INTENT"],
        "rule_score": 0.82,
        "reason": "Health-domain content with tool intent supports calculator/checker style linking.",
    },
]


def evaluate_symbolic_rules_v1(
    symbol_extraction_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    2.6.1.3 Symbolic Rule Engine.

    Shadow runtime:
    - Evaluates symbolic rules from extracted symbols.
    - Produces rule matches and symbolic rule score.
    - Does not modify score, target, URL, highlight, or link decisions.
    """

    symbols = (
        symbol_extraction_result.get("symbols")
        if isinstance(symbol_extraction_result.get("symbols"), list)
        else []
    )

    symbol_names = {
        str(item.get("symbol") or "").strip()
        for item in symbols
        if isinstance(item, dict) and item.get("symbol")
    }

    matched_rules: List[Dict[str, Any]] = []
    reasoning_chain: List[str] = []

    for rule in SYMBOLIC_RULES_V1:
        required = set(rule.get("required_symbols") or [])

        if required and required.issubset(symbol_names):
            matched = {
                "rule_id": rule.get("rule_id"),
                "name": rule.get("name"),
                "required_symbols": sorted(required),
                "rule_score": float(rule.get("rule_score") or 0),
                "reason": rule.get("reason"),
            }

            matched_rules.append(matched)
            reasoning_chain.append(
                f"{rule.get('name')} matched because {', '.join(sorted(required))} were present."
            )

    symbolic_rule_score = round(
        sum(float(x.get("rule_score") or 0) for x in matched_rules)
        / max(1, len(matched_rules)),
        4,
    )

    if matched_rules:
        rule_decision = "symbolic_support_found"
    else:
        rule_decision = "no_symbolic_rule_match"

    return {
        "build_id": BUILD_ID,
        "layer": "2.6.1.3 Symbolic Rule Engine",
        "shadow_runtime": True,
        "can_influence_runtime": False,
        "input_symbol_count": len(symbol_names),
        "matched_rule_count": len(matched_rules),
        "matched_rules": matched_rules,
        "symbolic_rule_score": symbolic_rule_score,
        "rule_decision": rule_decision,
        "reasoning_chain": reasoning_chain,
        "safety_flags": {
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "runtime_shadow_only": True,
            "metadata_only": True,
        },
    }


def explain_symbolic_rules_v1() -> Dict[str, Any]:
    return {
        "build_id": BUILD_ID,
        "layer": "2.6.1.3 Symbolic Rule Engine",
        "mode": "shadow_runtime",
        "can_influence_runtime": False,
        "rule_count": len(SYMBOLIC_RULES_V1),
        "rules": SYMBOLIC_RULES_V1,
    }



SYMBOL_RELATIONSHIP_RULES_V1 = [
    {
        "source_symbol": "TOOL_INTENT",
        "relationship": "supports",
        "target_symbol": "CALCULATOR_PAGE",
        "confidence": 0.86,
        "reason": "Tool intent supports calculator/tool page alignment.",
    },
    {
        "source_symbol": "INFORMATIONAL_INTENT",
        "relationship": "supports",
        "target_symbol": "GUIDE_PAGE",
        "confidence": 0.82,
        "reason": "Informational intent supports guide-style content alignment.",
    },
    {
        "source_symbol": "COMPARISON_INTENT",
        "relationship": "modifies",
        "target_symbol": "GUIDE_PAGE",
        "confidence": 0.72,
        "reason": "Comparison intent can modify guide content into comparison-guide behavior.",
    },
    {
        "source_symbol": "SEO_DOMAIN",
        "relationship": "contextualizes",
        "target_symbol": "ACTIONABLE_INTENT",
        "confidence": 0.80,
        "reason": "SEO domain context strengthens actionable optimization intent.",
    },
    {
        "source_symbol": "HEALTH_DOMAIN",
        "relationship": "contextualizes",
        "target_symbol": "TOOL_INTENT",
        "confidence": 0.78,
        "reason": "Health domain context supports calculator/checker/tool intent.",
    },
]


def map_symbol_relationships_v1(
    symbol_extraction_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    2.6.1.4 Symbol Relationship Mapping.

    Shadow runtime:
    - Maps relationships between extracted symbols.
    - Produces symbolic relationship graph edges.
    - Does not modify score, target, URL, highlight, or link decisions.
    """

    symbols = (
        symbol_extraction_result.get("symbols")
        if isinstance(symbol_extraction_result.get("symbols"), list)
        else []
    )

    symbol_names = {
        str(item.get("symbol") or "").strip()
        for item in symbols
        if isinstance(item, dict) and item.get("symbol")
    }

    relationships: List[Dict[str, Any]] = []
    reasoning_chain: List[str] = []

    for rule in SYMBOL_RELATIONSHIP_RULES_V1:
        source_symbol = str(rule.get("source_symbol") or "").strip()
        target_symbol = str(rule.get("target_symbol") or "").strip()

        if source_symbol in symbol_names and target_symbol in symbol_names:
            edge = {
                "source_symbol": source_symbol,
                "relationship": rule.get("relationship"),
                "target_symbol": target_symbol,
                "confidence": float(rule.get("confidence") or 0),
                "reason": rule.get("reason"),
            }

            relationships.append(edge)

            reasoning_chain.append(
                f"{source_symbol} {rule.get('relationship')} {target_symbol}: {rule.get('reason')}"
            )

    relationship_score = round(
        sum(float(x.get("confidence") or 0) for x in relationships)
        / max(1, len(relationships)),
        4,
    )

    if relationships:
        relationship_decision = "symbol_relationships_found"
    else:
        relationship_decision = "no_symbol_relationships_found"

    return {
        "build_id": BUILD_ID,
        "layer": "2.6.1.4 Symbol Relationship Mapping",
        "shadow_runtime": True,
        "can_influence_runtime": False,
        "input_symbol_count": len(symbol_names),
        "relationship_count": len(relationships),
        "relationships": relationships,
        "relationship_score": relationship_score,
        "relationship_decision": relationship_decision,
        "reasoning_chain": reasoning_chain,
        "safety_flags": {
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "runtime_shadow_only": True,
            "metadata_only": True,
        },
    }


def explain_symbol_relationship_mapping_v1() -> Dict[str, Any]:
    return {
        "build_id": BUILD_ID,
        "layer": "2.6.1.4 Symbol Relationship Mapping",
        "mode": "shadow_runtime",
        "can_influence_runtime": False,
        "relationship_rule_count": len(SYMBOL_RELATIONSHIP_RULES_V1),
        "relationship_rules": SYMBOL_RELATIONSHIP_RULES_V1,
    }



def build_symbol_knowledge_graph_v1(
    symbol_extraction_result: Dict[str, Any],
    symbolic_rule_result: Dict[str, Any],
    symbol_relationship_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    2.6.1.5 Symbol Knowledge Graph.

    Shadow runtime:
    - Builds a lightweight symbol knowledge graph from symbols, rules, and relationships.
    - Does not modify score, target, URL, highlight, or link decisions.
    """

    symbols = (
        symbol_extraction_result.get("symbols")
        if isinstance(symbol_extraction_result.get("symbols"), list)
        else []
    )

    matched_rules = (
        symbolic_rule_result.get("matched_rules")
        if isinstance(symbolic_rule_result.get("matched_rules"), list)
        else []
    )

    relationships = (
        symbol_relationship_result.get("relationships")
        if isinstance(symbol_relationship_result.get("relationships"), list)
        else []
    )

    nodes: List[Dict[str, Any]] = []
    node_ids = set()

    for item in symbols:
        if not isinstance(item, dict):
            continue

        symbol = str(item.get("symbol") or "").strip()
        if not symbol or symbol in node_ids:
            continue

        node_ids.add(symbol)
        nodes.append({
            "node_id": symbol,
            "node_type": "symbol",
            "confidence": float(item.get("confidence") or 0),
            "source": item.get("source") or "unknown",
            "matched_keywords": item.get("matched_keywords") or [],
        })

    edges: List[Dict[str, Any]] = []

    for rel in relationships:
        if not isinstance(rel, dict):
            continue

        source_symbol = str(rel.get("source_symbol") or "").strip()
        target_symbol = str(rel.get("target_symbol") or "").strip()

        if not source_symbol or not target_symbol:
            continue

        edges.append({
            "edge_type": "symbol_relationship",
            "source": source_symbol,
            "relationship": rel.get("relationship") or "related_to",
            "target": target_symbol,
            "confidence": float(rel.get("confidence") or 0),
            "reason": rel.get("reason"),
        })

    for rule in matched_rules:
        if not isinstance(rule, dict):
            continue

        rule_id = str(rule.get("rule_id") or "").strip()
        required_symbols = (
            rule.get("required_symbols")
            if isinstance(rule.get("required_symbols"), list)
            else []
        )

        for symbol in required_symbols:
            symbol = str(symbol or "").strip()
            if not symbol:
                continue

            edges.append({
                "edge_type": "rule_support",
                "source": symbol,
                "relationship": "supports_rule",
                "target": rule_id,
                "confidence": float(rule.get("rule_score") or 0),
                "reason": rule.get("reason"),
            })

        if rule_id and rule_id not in node_ids:
            node_ids.add(rule_id)
            nodes.append({
                "node_id": rule_id,
                "node_type": "symbolic_rule",
                "name": rule.get("name"),
                "confidence": float(rule.get("rule_score") or 0),
                "reason": rule.get("reason"),
            })

    node_score = round(
        sum(float(x.get("confidence") or 0) for x in nodes)
        / max(1, len(nodes)),
        4,
    )

    edge_score = round(
        sum(float(x.get("confidence") or 0) for x in edges)
        / max(1, len(edges)),
        4,
    )

    graph_score = round(
        (node_score * 0.45) + (edge_score * 0.55),
        4,
    )

    if nodes and edges:
        graph_decision = "symbol_knowledge_graph_built"
    elif nodes:
        graph_decision = "symbol_nodes_only"
    else:
        graph_decision = "no_symbol_graph_data"

    return {
        "build_id": BUILD_ID,
        "layer": "2.6.1.5 Symbol Knowledge Graph",
        "shadow_runtime": True,
        "can_influence_runtime": False,

        "node_count": len(nodes),
        "edge_count": len(edges),

        "nodes": nodes,
        "edges": edges,

        "node_score": node_score,
        "edge_score": edge_score,
        "graph_score": graph_score,
        "graph_decision": graph_decision,

        "safety_flags": {
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "runtime_shadow_only": True,
            "metadata_only": True,
        },
    }


def explain_symbol_knowledge_graph_v1() -> Dict[str, Any]:
    return {
        "build_id": BUILD_ID,
        "layer": "2.6.1.5 Symbol Knowledge Graph",
        "mode": "shadow_runtime",
        "can_influence_runtime": False,
        "purpose": "Builds a lightweight symbolic knowledge graph from extracted symbols, symbolic rules, and symbol relationships.",
        "graph_parts": [
            "symbol_nodes",
            "symbol_relationship_edges",
            "rule_support_edges",
            "symbolic_rule_nodes",
        ],
    }



def _safe_signal_float(value: Any) -> float:
    try:
        return max(0.0, min(1.0, float(value or 0.0)))
    except Exception:
        return 0.0


def aggregate_neural_semantic_signals_v1(
    *,
    semantic_similarity: float = 0.0,
    semantic_confidence: float = 0.0,
    semantic_evidence: float = 0.0,
    semantic_support: float = 0.0,
    candidate_fusion: float = 0.0,
    graph_score: float = 0.0,
    semantic_relationship_score: float = 0.0,
    semantic_stability: float = 0.0,
) -> Dict[str, Any]:
    """
    2.6.2.1 Neural Signal Aggregation.

    Shadow runtime:
    - Aggregates existing semantic/neural-like signals into one unified neural signal.
    - Does not modify score, target, URL, highlight, or link decisions.
    """

    signals = {
        "semantic_similarity": _safe_signal_float(semantic_similarity),
        "semantic_confidence": _safe_signal_float(semantic_confidence),
        "semantic_evidence": _safe_signal_float(semantic_evidence),
        "semantic_support": _safe_signal_float(semantic_support),
        "candidate_fusion": _safe_signal_float(candidate_fusion),
        "graph_score": _safe_signal_float(graph_score),
        "semantic_relationship_score": _safe_signal_float(semantic_relationship_score),
        "semantic_stability": _safe_signal_float(semantic_stability),
    }

    weights = {
        "semantic_similarity": 0.22,
        "semantic_confidence": 0.18,
        "semantic_evidence": 0.12,
        "semantic_support": 0.12,
        "candidate_fusion": 0.14,
        "graph_score": 0.10,
        "semantic_relationship_score": 0.08,
        "semantic_stability": 0.04,
    }

    weighted_parts = {
        key: round(signals[key] * weights[key], 4)
        for key in signals
    }

    unified_neural_signal_score = round(
        sum(weighted_parts.values()),
        4,
    )

    available_signals = [
        key for key, value in signals.items()
        if value > 0
    ]

    if unified_neural_signal_score >= 0.75:
        neural_signal_strength = "strong"
    elif unified_neural_signal_score >= 0.50:
        neural_signal_strength = "moderate"
    elif unified_neural_signal_score > 0:
        neural_signal_strength = "weak"
    else:
        neural_signal_strength = "none"

    return {
        "build_id": BUILD_ID,
        "layer": "2.6.2.1 Neural Signal Aggregation",
        "shadow_runtime": True,
        "can_influence_runtime": False,

        "unified_neural_signal_score": unified_neural_signal_score,
        "neural_signal_strength": neural_signal_strength,

        "available_signal_count": len(available_signals),
        "available_signals": available_signals,

        "signals": signals,
        "weights": weights,
        "weighted_parts": weighted_parts,

        "neural_signal_summary": {
            "semantic_similarity_available": signals["semantic_similarity"] > 0,
            "semantic_confidence_available": signals["semantic_confidence"] > 0,
            "semantic_evidence_available": signals["semantic_evidence"] > 0,
            "candidate_fusion_available": signals["candidate_fusion"] > 0,
            "graph_signal_available": signals["graph_score"] > 0,
            "relationship_signal_available": signals["semantic_relationship_score"] > 0,
        },

        "safety_flags": {
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "runtime_shadow_only": True,
            "metadata_only": True,
        },
    }


def explain_neural_signal_aggregation_v1() -> Dict[str, Any]:
    return {
        "build_id": BUILD_ID,
        "layer": "2.6.2.1 Neural Signal Aggregation",
        "mode": "shadow_runtime",
        "can_influence_runtime": False,
        "purpose": "Aggregates existing semantic, confidence, evidence, fusion, graph, relationship, and stability signals into one unified neural signal object.",
        "signals": [
            "semantic_similarity",
            "semantic_confidence",
            "semantic_evidence",
            "semantic_support",
            "candidate_fusion",
            "graph_score",
            "semantic_relationship_score",
            "semantic_stability",
        ],
    }



def consolidate_neural_evidence_v1(
    evidence_items: List[Dict[str, Any]] | None,
) -> Dict[str, Any]:
    """
    2.6.2.2 Neural Evidence Consolidation.

    Shadow runtime:
    - Consolidates semantic/neural evidence items.
    - Deduplicates weakly by text/source/role.
    - Does not modify score, target, URL, highlight, or link decisions.
    """

    cleaned: List[Dict[str, Any]] = []
    seen = set()

    for item in evidence_items or []:
        if not isinstance(item, dict):
            continue

        text = str(
            item.get("text")
            or item.get("evidence")
            or item.get("summary")
            or ""
        ).strip()

        source = str(
            item.get("source")
            or item.get("engine")
            or item.get("evidence_source")
            or "unknown"
        ).strip()

        role = str(
            item.get("role")
            or item.get("evidence_role")
            or "semantic_evidence"
        ).strip()

        score = _safe_signal_float(
            item.get("score")
            or item.get("evidence_score")
            or item.get("confidence")
            or item.get("evidence_confidence")
            or 0.0
        )

        key = (
            text.lower(),
            source.lower(),
            role.lower(),
        )

        if key in seen:
            continue

        seen.add(key)

        cleaned.append({
            "text": text,
            "source": source,
            "role": role,
            "evidence_score": score,
            "raw": item,
        })

    cleaned.sort(
        key=lambda x: float(x.get("evidence_score") or 0.0),
        reverse=True,
    )

    evidence_sources = sorted({
        str(x.get("source") or "unknown")
        for x in cleaned
    })

    evidence_roles = sorted({
        str(x.get("role") or "semantic_evidence")
        for x in cleaned
    })

    evidence_score = round(
        sum(float(x.get("evidence_score") or 0.0) for x in cleaned)
        / max(1, len(cleaned)),
        4,
    )

    if evidence_score >= 0.75:
        evidence_strength = "strong"
    elif evidence_score >= 0.50:
        evidence_strength = "moderate"
    elif evidence_score > 0:
        evidence_strength = "weak"
    else:
        evidence_strength = "none"

    return {
        "build_id": BUILD_ID,
        "layer": "2.6.2.2 Neural Evidence Consolidation",
        "shadow_runtime": True,
        "can_influence_runtime": False,

        "evidence_count": len(cleaned),
        "evidence_score": evidence_score,
        "evidence_strength": evidence_strength,

        "evidence_sources": evidence_sources,
        "evidence_roles": evidence_roles,
        "consolidated_evidence": cleaned,

        "evidence_summary": {
            "has_evidence": bool(cleaned),
            "source_count": len(evidence_sources),
            "role_count": len(evidence_roles),
            "duplicate_suppression_applied": True,
        },

        "safety_flags": {
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "runtime_shadow_only": True,
            "metadata_only": True,
        },
    }


def explain_neural_evidence_consolidation_v1() -> Dict[str, Any]:
    return {
        "build_id": BUILD_ID,
        "layer": "2.6.2.2 Neural Evidence Consolidation",
        "mode": "shadow_runtime",
        "can_influence_runtime": False,
        "purpose": "Consolidates semantic/neural evidence from retrieval, confidence, graph, runtime, and support layers into one evidence object.",
        "outputs": [
            "evidence_count",
            "evidence_score",
            "evidence_strength",
            "evidence_sources",
            "evidence_roles",
            "consolidated_evidence",
        ],
    }



def build_neural_confidence_layer_v1(
    neural_signal_result: Dict[str, Any],
    neural_evidence_result: Dict[str, Any],
    *,
    semantic_confidence: float = 0.0,
) -> Dict[str, Any]:
    """
    2.6.2.3 Neural Confidence Layer.

    Shadow runtime:
    - Builds a confidence layer from neural signal aggregation and evidence consolidation.
    - Does not modify score, target, URL, highlight, or link decisions.
    """

    neural_signal_score = _safe_signal_float(
        neural_signal_result.get("unified_neural_signal_score")
        if isinstance(neural_signal_result, dict)
        else 0.0
    )

    evidence_score = _safe_signal_float(
        neural_evidence_result.get("evidence_score")
        if isinstance(neural_evidence_result, dict)
        else 0.0
    )

    semantic_confidence_score = _safe_signal_float(semantic_confidence)

    neural_confidence_score = round(
        (
            neural_signal_score * 0.45
            + evidence_score * 0.35
            + semantic_confidence_score * 0.20
        ),
        4,
    )

    if neural_confidence_score >= 0.75:
        neural_confidence_level = "high"
    elif neural_confidence_score >= 0.50:
        neural_confidence_level = "moderate"
    elif neural_confidence_score > 0:
        neural_confidence_level = "low"
    else:
        neural_confidence_level = "none"

    confidence_reasons: List[str] = []

    if neural_signal_score > 0:
        confidence_reasons.append(
            f"Neural signal score available: {neural_signal_score}."
        )

    if evidence_score > 0:
        confidence_reasons.append(
            f"Evidence score available: {evidence_score}."
        )

    if semantic_confidence_score > 0:
        confidence_reasons.append(
            f"Semantic confidence score available: {semantic_confidence_score}."
        )

    if not confidence_reasons:
        confidence_reasons.append(
            "No neural confidence support signals were available."
        )

    return {
        "build_id": BUILD_ID,
        "layer": "2.6.2.3 Neural Confidence Layer",
        "shadow_runtime": True,
        "can_influence_runtime": False,

        "neural_confidence_score": neural_confidence_score,
        "neural_confidence_level": neural_confidence_level,
        "confidence_reasons": confidence_reasons,

        "confidence_inputs": {
            "neural_signal_score": neural_signal_score,
            "evidence_score": evidence_score,
            "semantic_confidence_score": semantic_confidence_score,
        },

        "confidence_summary": {
            "confidence_available": neural_confidence_score > 0,
            "evidence_available": evidence_score > 0,
            "neural_signal_available": neural_signal_score > 0,
            "semantic_confidence_available": semantic_confidence_score > 0,
        },

        "safety_flags": {
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "runtime_shadow_only": True,
            "metadata_only": True,
        },
    }


def explain_neural_confidence_layer_v1() -> Dict[str, Any]:
    return {
        "build_id": BUILD_ID,
        "layer": "2.6.2.3 Neural Confidence Layer",
        "mode": "shadow_runtime",
        "can_influence_runtime": False,
        "purpose": "Combines unified neural signal score, consolidated evidence score, and semantic confidence into one neural confidence object.",
        "inputs": [
            "unified_neural_signal_score",
            "evidence_score",
            "semantic_confidence",
        ],
        "outputs": [
            "neural_confidence_score",
            "neural_confidence_level",
            "confidence_reasons",
            "confidence_summary",
        ],
    }



def generate_neural_semantic_explanation_v1(
    neural_signal_result: Dict[str, Any],
    neural_evidence_result: Dict[str, Any],
    neural_confidence_result: Dict[str, Any],
    symbolic_rule_result: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    2.6.2.4 Neural Semantic Explanation.

    Shadow runtime:
    - Explains neural semantic support using signal, evidence, confidence, and optional symbolic rules.
    - Does not modify score, target, URL, highlight, or link decisions.
    """

    signal_score = _safe_signal_float(
        neural_signal_result.get("unified_neural_signal_score")
        if isinstance(neural_signal_result, dict)
        else 0.0
    )

    evidence_score = _safe_signal_float(
        neural_evidence_result.get("evidence_score")
        if isinstance(neural_evidence_result, dict)
        else 0.0
    )

    confidence_score = _safe_signal_float(
        neural_confidence_result.get("neural_confidence_score")
        if isinstance(neural_confidence_result, dict)
        else 0.0
    )

    matched_rules = (
        symbolic_rule_result.get("matched_rules")
        if isinstance(symbolic_rule_result, dict)
        and isinstance(symbolic_rule_result.get("matched_rules"), list)
        else []
    )

    symbolic_rule_score = _safe_signal_float(
        symbolic_rule_result.get("symbolic_rule_score")
        if isinstance(symbolic_rule_result, dict)
        else 0.0
    )

    explanation_chain: List[str] = []

    explanation_chain.append(
        f"Neural signal score is {signal_score}."
    )

    explanation_chain.append(
        f"Neural evidence score is {evidence_score}."
    )

    explanation_chain.append(
        f"Neural confidence score is {confidence_score}."
    )

    if matched_rules:
        explanation_chain.append(
            f"{len(matched_rules)} symbolic rule match(es) support the reasoning."
        )
    else:
        explanation_chain.append(
            "No symbolic rule support was attached to this explanation."
        )

    confidence_reasons = (
        neural_confidence_result.get("confidence_reasons")
        if isinstance(neural_confidence_result, dict)
        and isinstance(neural_confidence_result.get("confidence_reasons"), list)
        else []
    )

    for reason in confidence_reasons:
        explanation_chain.append(str(reason))

    consolidated_evidence = (
        neural_evidence_result.get("consolidated_evidence")
        if isinstance(neural_evidence_result, dict)
        and isinstance(neural_evidence_result.get("consolidated_evidence"), list)
        else []
    )

    top_evidence = [
        {
            "text": x.get("text"),
            "source": x.get("source"),
            "role": x.get("role"),
            "evidence_score": x.get("evidence_score"),
        }
        for x in consolidated_evidence[:5]
        if isinstance(x, dict)
    ]

    explainability_score = round(
        (
            signal_score * 0.30
            + evidence_score * 0.25
            + confidence_score * 0.30
            + symbolic_rule_score * 0.15
        ),
        4,
    )

    if explainability_score >= 0.75:
        explanation_strength = "strong"
    elif explainability_score >= 0.50:
        explanation_strength = "moderate"
    elif explainability_score > 0:
        explanation_strength = "weak"
    else:
        explanation_strength = "none"

    return {
        "build_id": BUILD_ID,
        "layer": "2.6.2.4 Neural Semantic Explanation",
        "shadow_runtime": True,
        "can_influence_runtime": False,

        "explainability_score": explainability_score,
        "explanation_strength": explanation_strength,

        "explanation_summary": {
            "has_neural_signal": signal_score > 0,
            "has_evidence": evidence_score > 0,
            "has_confidence": confidence_score > 0,
            "has_symbolic_support": bool(matched_rules),
            "top_evidence_count": len(top_evidence),
        },

        "neural_reasoning": {
            "signal_score": signal_score,
            "evidence_score": evidence_score,
            "confidence_score": confidence_score,
        },

        "symbolic_reasoning": {
            "matched_rule_count": len(matched_rules),
            "symbolic_rule_score": symbolic_rule_score,
            "matched_rules": matched_rules,
        },

        "top_evidence": top_evidence,
        "explanation_chain": explanation_chain,

        "safety_flags": {
            "changes_highlight_selection": False,
            "changes_target_selection": False,
            "changes_phrase_scoring": False,
            "changes_url_assignment": False,
            "changes_runtime_linking": False,
            "runtime_shadow_only": True,
            "metadata_only": True,
        },
    }


def explain_neural_semantic_explanation_v1() -> Dict[str, Any]:
    return {
        "build_id": BUILD_ID,
        "layer": "2.6.2.4 Neural Semantic Explanation",
        "mode": "shadow_runtime",
        "can_influence_runtime": False,
        "purpose": "Creates a unified explanation from neural signal aggregation, neural evidence consolidation, neural confidence, and optional symbolic reasoning.",
        "outputs": [
            "explainability_score",
            "explanation_strength",
            "explanation_summary",
            "neural_reasoning",
            "symbolic_reasoning",
            "top_evidence",
            "explanation_chain",
        ],
    }


def bridge_symbolic_neural_reasoning_v1(
    symbolic_rule_result: Dict[str, Any] | None = None,
    neural_signal_result: Dict[str, Any] | None = None,
    neural_confidence_result: Dict[str, Any] | None = None,
    neural_explanation_result: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    2.6.2.5 Symbolic-Neural Bridge.

    Shadow-runtime only.
    Combines symbolic rule evidence and neural semantic evidence into a bridge
    diagnostic layer without mutating runtime scoring, ranking, selection,
    persistence, or link application behavior.
    """
    symbolic_rule_result = symbolic_rule_result or {}
    neural_signal_result = neural_signal_result or {}
    neural_confidence_result = neural_confidence_result or {}
    neural_explanation_result = neural_explanation_result or {}

    symbolic_rule_score = _safe_signal_float(
        symbolic_rule_result.get("symbolic_rule_score")
    )
    unified_neural_signal_score = _safe_signal_float(
        neural_signal_result.get("unified_neural_signal_score")
    )
    neural_confidence_score = _safe_signal_float(
        neural_confidence_result.get("neural_confidence_score")
    )
    explainability_score = _safe_signal_float(
        neural_explanation_result.get("explainability_score")
    )

    symbolic_support = symbolic_rule_score > 0
    neural_support = unified_neural_signal_score > 0
    confidence_support = neural_confidence_score > 0
    explanation_support = explainability_score > 0

    matched_rules = symbolic_rule_result.get("matched_rules") or []
    evidence_items = neural_signal_result.get("evidence_items") or []
    explanation_chain = neural_explanation_result.get("explanation_chain") or []

    bridge_alignment_score = round(
        (
            symbolic_rule_score * 0.30
            + unified_neural_signal_score * 0.30
            + neural_confidence_score * 0.20
            + explainability_score * 0.20
        ),
        4,
    )

    agreement_score = 0.0
    if symbolic_support and neural_support:
        agreement_score += 0.45
    if symbolic_support and explanation_support:
        agreement_score += 0.20
    if neural_support and confidence_support:
        agreement_score += 0.20
    if matched_rules and evidence_items:
        agreement_score += 0.15
    agreement_score = round(min(1.0, agreement_score), 4)

    hybrid_score = round(
        (bridge_alignment_score * 0.70) + (agreement_score * 0.30),
        4,
    )

    if hybrid_score >= 0.75:
        bridge_strength = "strong"
        bridge_decision = "symbolic_neural_alignment_strong"
    elif hybrid_score >= 0.50:
        bridge_strength = "moderate"
        bridge_decision = "symbolic_neural_alignment_moderate"
    elif hybrid_score > 0:
        bridge_strength = "weak"
        bridge_decision = "symbolic_neural_alignment_weak"
    else:
        bridge_strength = "none"
        bridge_decision = "symbolic_neural_alignment_not_found"

    conflicts = []
    if symbolic_support and not neural_support:
        conflicts.append("symbolic_support_without_neural_support")
    if neural_support and not symbolic_support:
        conflicts.append("neural_support_without_symbolic_support")
    if neural_confidence_score >= 0.70 and explainability_score < 0.40:
        conflicts.append("high_neural_confidence_low_explainability")
    if symbolic_rule_score >= 0.70 and neural_confidence_score < 0.40:
        conflicts.append("high_symbolic_support_low_neural_confidence")

    bridge_chain = [
        {
            "step": "symbolic_rule_layer",
            "score": symbolic_rule_score,
            "support": symbolic_support,
            "evidence_count": len(matched_rules) if isinstance(matched_rules, list) else 0,
        },
        {
            "step": "neural_signal_layer",
            "score": unified_neural_signal_score,
            "support": neural_support,
            "evidence_count": len(evidence_items) if isinstance(evidence_items, list) else 0,
        },
        {
            "step": "neural_confidence_layer",
            "score": neural_confidence_score,
            "support": confidence_support,
        },
        {
            "step": "neural_explanation_layer",
            "score": explainability_score,
            "support": explanation_support,
            "chain_available": bool(explanation_chain),
        },
        {
            "step": "symbolic_neural_bridge",
            "hybrid_score": hybrid_score,
            "agreement_score": agreement_score,
            "bridge_strength": bridge_strength,
        },
    ]

    return {
        "version": "2.6.2.5",
        "layer": "symbolic_neural_bridge",
        "shadow_runtime_only": True,
        "can_influence_runtime": False,
        "runtime_mutation_permissions": [],
        "symbolic_support": symbolic_support,
        "neural_support": neural_support,
        "confidence_support": confidence_support,
        "explanation_support": explanation_support,
        "symbolic_rule_score": symbolic_rule_score,
        "unified_neural_signal_score": unified_neural_signal_score,
        "neural_confidence_score": neural_confidence_score,
        "explainability_score": explainability_score,
        "bridge_alignment_score": bridge_alignment_score,
        "agreement_score": agreement_score,
        "hybrid_score": hybrid_score,
        "bridge_strength": bridge_strength,
        "bridge_decision": bridge_decision,
        "conflicts": conflicts,
        "bridge_chain": bridge_chain,
        "diagnostics": {
            "matched_symbolic_rules": len(matched_rules) if isinstance(matched_rules, list) else 0,
            "neural_evidence_items": len(evidence_items) if isinstance(evidence_items, list) else 0,
            "explanation_chain_steps": len(explanation_chain) if isinstance(explanation_chain, list) else 0,
            "has_conflict": bool(conflicts),
            "bridge_ready": hybrid_score > 0,
        },
    }


def explain_symbolic_neural_bridge_v1() -> Dict[str, Any]:
    """
    Explain the 2.6.2.5 Symbolic-Neural Bridge capability.
    """
    return {
        "version": "2.6.2.5",
        "layer": "symbolic_neural_bridge",
        "purpose": "Bridge symbolic rule evidence and neural semantic evidence into one shadow diagnostic layer.",
        "shadow_runtime_only": True,
        "can_influence_runtime": False,
        "runtime_mutation_permissions": [],
        "inputs": [
            "symbolic_rule_result",
            "neural_signal_result",
            "neural_confidence_result",
            "neural_explanation_result",
        ],
        "outputs": [
            "symbolic_support",
            "neural_support",
            "bridge_alignment_score",
            "agreement_score",
            "hybrid_score",
            "bridge_strength",
            "bridge_decision",
            "conflicts",
            "bridge_chain",
        ],
        "safety": {
            "does_not_rank_targets": True,
            "does_not_select_links": True,
            "does_not_apply_links": True,
            "does_not_mutate_runtime": True,
            "does_not_write_persistence": True,
        },
    }


def detect_hybrid_reasoning_conflicts_v1(
    symbolic_rule_result: Dict[str, Any] | None = None,
    neural_signal_result: Dict[str, Any] | None = None,
    neural_confidence_result: Dict[str, Any] | None = None,
    neural_explanation_result: Dict[str, Any] | None = None,
    symbolic_neural_bridge_result: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    2.6.2.6 Hybrid Reasoning Conflict Detector.

    Shadow-runtime only.
    Detects disagreement between symbolic reasoning, neural semantic signals,
    neural confidence, neural explanations, and the symbolic-neural bridge.
    """
    symbolic_rule_result = symbolic_rule_result or {}
    neural_signal_result = neural_signal_result or {}
    neural_confidence_result = neural_confidence_result or {}
    neural_explanation_result = neural_explanation_result or {}
    symbolic_neural_bridge_result = symbolic_neural_bridge_result or {}

    symbolic_rule_score = _safe_signal_float(symbolic_rule_result.get("symbolic_rule_score"))
    unified_neural_signal_score = _safe_signal_float(neural_signal_result.get("unified_neural_signal_score"))
    neural_confidence_score = _safe_signal_float(neural_confidence_result.get("neural_confidence_score"))
    explainability_score = _safe_signal_float(neural_explanation_result.get("explainability_score"))
    hybrid_score = _safe_signal_float(symbolic_neural_bridge_result.get("hybrid_score"))

    symbolic_support = symbolic_rule_score > 0
    neural_support = unified_neural_signal_score > 0
    confidence_support = neural_confidence_score > 0
    explanation_support = explainability_score > 0

    bridge_conflicts = symbolic_neural_bridge_result.get("conflicts") or []
    if not isinstance(bridge_conflicts, list):
        bridge_conflicts = []

    conflict_items = []

    def _add_conflict(code: str, severity: str, weight: float, reason: str) -> None:
        conflict_items.append({
            "code": code,
            "severity": severity,
            "weight": round(float(weight), 4),
            "reason": reason,
        })

    if symbolic_support and not neural_support:
        _add_conflict(
            "symbolic_support_without_neural_support",
            "moderate",
            0.45,
            "Symbolic rules found support, but neural semantic signals did not.",
        )

    if neural_support and not symbolic_support:
        _add_conflict(
            "neural_support_without_symbolic_support",
            "moderate",
            0.45,
            "Neural semantic signals found support, but symbolic rules did not.",
        )

    if neural_confidence_score >= 0.70 and explainability_score < 0.40:
        _add_conflict(
            "high_neural_confidence_low_explainability",
            "high",
            0.70,
            "Neural confidence is high, but explanation quality is low.",
        )

    if symbolic_rule_score >= 0.70 and neural_confidence_score < 0.40:
        _add_conflict(
            "high_symbolic_support_low_neural_confidence",
            "high",
            0.70,
            "Symbolic support is high, but neural confidence is low.",
        )

    if symbolic_rule_score >= 0.70 and unified_neural_signal_score < 0.35:
        _add_conflict(
            "strong_symbolic_weak_neural_signal",
            "high",
            0.75,
            "Symbolic reasoning is strong, but neural semantic signal is weak.",
        )

    if unified_neural_signal_score >= 0.70 and symbolic_rule_score < 0.35:
        _add_conflict(
            "strong_neural_weak_symbolic_signal",
            "high",
            0.75,
            "Neural semantic signal is strong, but symbolic reasoning is weak.",
        )

    if hybrid_score >= 0.70 and bridge_conflicts:
        _add_conflict(
            "high_hybrid_score_with_bridge_conflicts",
            "moderate",
            0.50,
            "Bridge score is high, but bridge-level conflicts are present.",
        )

    for item in bridge_conflicts:
        _add_conflict(
            f"bridge_conflict::{item}",
            "low",
            0.25,
            "Conflict inherited from symbolic-neural bridge diagnostics.",
        )

    if conflict_items:
        conflict_score = round(
            min(1.0, sum(float(x["weight"]) for x in conflict_items) / max(1, len(conflict_items))),
            4,
        )
    else:
        conflict_score = 0.0

    if conflict_score >= 0.70:
        conflict_severity = "high"
        conflict_decision = "hybrid_reasoning_conflict_high"
    elif conflict_score >= 0.40:
        conflict_severity = "moderate"
        conflict_decision = "hybrid_reasoning_conflict_moderate"
    elif conflict_score > 0:
        conflict_severity = "low"
        conflict_decision = "hybrid_reasoning_conflict_low"
    else:
        conflict_severity = "none"
        conflict_decision = "hybrid_reasoning_conflict_not_found"

    return {
        "version": "2.6.2.6",
        "layer": "hybrid_reasoning_conflict_detector",
        "shadow_runtime_only": True,
        "can_influence_runtime": False,
        "runtime_mutation_permissions": [],
        "conflict_detected": bool(conflict_items),
        "conflict_score": conflict_score,
        "conflict_severity": conflict_severity,
        "conflict_decision": conflict_decision,
        "conflict_items": conflict_items,
        "support_state": {
            "symbolic_support": symbolic_support,
            "neural_support": neural_support,
            "confidence_support": confidence_support,
            "explanation_support": explanation_support,
        },
        "score_state": {
            "symbolic_rule_score": symbolic_rule_score,
            "unified_neural_signal_score": unified_neural_signal_score,
            "neural_confidence_score": neural_confidence_score,
            "explainability_score": explainability_score,
            "hybrid_score": hybrid_score,
        },
        "diagnostics": {
            "bridge_conflict_count": len(bridge_conflicts),
            "detected_conflict_count": len(conflict_items),
            "has_high_conflict": conflict_severity == "high",
            "has_moderate_conflict": conflict_severity == "moderate",
            "safe_shadow_diagnostic_only": True,
        },
    }


def explain_hybrid_reasoning_conflict_detector_v1() -> Dict[str, Any]:
    """
    Explain the 2.6.2.6 Hybrid Reasoning Conflict Detector capability.
    """
    return {
        "version": "2.6.2.6",
        "layer": "hybrid_reasoning_conflict_detector",
        "purpose": "Detect disagreement between symbolic reasoning, neural signals, confidence, explanations, and bridge diagnostics.",
        "shadow_runtime_only": True,
        "can_influence_runtime": False,
        "runtime_mutation_permissions": [],
        "inputs": [
            "symbolic_rule_result",
            "neural_signal_result",
            "neural_confidence_result",
            "neural_explanation_result",
            "symbolic_neural_bridge_result",
        ],
        "outputs": [
            "conflict_detected",
            "conflict_score",
            "conflict_severity",
            "conflict_decision",
            "conflict_items",
            "support_state",
            "score_state",
        ],
        "safety": {
            "does_not_rank_targets": True,
            "does_not_select_links": True,
            "does_not_apply_links": True,
            "does_not_mutate_runtime": True,
            "does_not_write_persistence": True,
        },
    }


def build_hybrid_reasoning_final_diagnostic_v1(
    symbolic_rule_result: Dict[str, Any] | None = None,
    neural_signal_result: Dict[str, Any] | None = None,
    neural_confidence_result: Dict[str, Any] | None = None,
    neural_explanation_result: Dict[str, Any] | None = None,
    symbolic_neural_bridge_result: Dict[str, Any] | None = None,
    hybrid_conflict_result: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    2.6.2.7 Hybrid Reasoning Final Diagnostic Layer.

    Shadow-runtime only.
    Produces a final diagnostic summary across symbolic reasoning,
    neural semantic signals, neural confidence, explanation quality,
    bridge alignment, and conflict detection.
    """
    symbolic_rule_result = symbolic_rule_result or {}
    neural_signal_result = neural_signal_result or {}
    neural_confidence_result = neural_confidence_result or {}
    neural_explanation_result = neural_explanation_result or {}
    symbolic_neural_bridge_result = symbolic_neural_bridge_result or {}
    hybrid_conflict_result = hybrid_conflict_result or {}

    symbolic_rule_score = _safe_signal_float(symbolic_rule_result.get("symbolic_rule_score"))
    unified_neural_signal_score = _safe_signal_float(neural_signal_result.get("unified_neural_signal_score"))
    neural_confidence_score = _safe_signal_float(neural_confidence_result.get("neural_confidence_score"))
    explainability_score = _safe_signal_float(neural_explanation_result.get("explainability_score"))
    hybrid_score = _safe_signal_float(symbolic_neural_bridge_result.get("hybrid_score"))
    conflict_score = _safe_signal_float(hybrid_conflict_result.get("conflict_score"))

    conflict_severity = str(hybrid_conflict_result.get("conflict_severity") or "none")
    bridge_strength = str(symbolic_neural_bridge_result.get("bridge_strength") or "none")

    conflict_penalty = {
        "none": 0.00,
        "low": 0.08,
        "moderate": 0.18,
        "high": 0.35,
    }.get(conflict_severity, 0.18)

    diagnostic_score = round(
        max(
            0.0,
            min(
                1.0,
                (
                    symbolic_rule_score * 0.18
                    + unified_neural_signal_score * 0.18
                    + neural_confidence_score * 0.18
                    + explainability_score * 0.16
                    + hybrid_score * 0.30
                )
                - conflict_penalty,
            ),
        ),
        4,
    )

    if diagnostic_score >= 0.75 and conflict_severity in ("none", "low"):
        diagnostic_strength = "strong"
        diagnostic_decision = "hybrid_reasoning_diagnostic_strong"
    elif diagnostic_score >= 0.50 and conflict_severity in ("none", "low", "moderate"):
        diagnostic_strength = "moderate"
        diagnostic_decision = "hybrid_reasoning_diagnostic_moderate"
    elif diagnostic_score > 0:
        diagnostic_strength = "weak"
        diagnostic_decision = "hybrid_reasoning_diagnostic_weak"
    else:
        diagnostic_strength = "none"
        diagnostic_decision = "hybrid_reasoning_diagnostic_not_found"

    final_diagnostic_chain = [
        {
            "step": "symbolic_reasoning",
            "score": symbolic_rule_score,
            "available": symbolic_rule_score > 0,
        },
        {
            "step": "neural_signal_aggregation",
            "score": unified_neural_signal_score,
            "available": unified_neural_signal_score > 0,
        },
        {
            "step": "neural_confidence",
            "score": neural_confidence_score,
            "available": neural_confidence_score > 0,
        },
        {
            "step": "neural_explanation",
            "score": explainability_score,
            "available": explainability_score > 0,
        },
        {
            "step": "symbolic_neural_bridge",
            "score": hybrid_score,
            "strength": bridge_strength,
            "available": hybrid_score > 0,
        },
        {
            "step": "hybrid_conflict_detector",
            "score": conflict_score,
            "severity": conflict_severity,
            "penalty": conflict_penalty,
            "conflict_detected": bool(hybrid_conflict_result.get("conflict_detected")),
        },
        {
            "step": "final_hybrid_diagnostic",
            "diagnostic_score": diagnostic_score,
            "diagnostic_strength": diagnostic_strength,
            "diagnostic_decision": diagnostic_decision,
        },
    ]

    readiness_flags = {
        "symbolic_ready": symbolic_rule_score > 0,
        "neural_ready": unified_neural_signal_score > 0,
        "confidence_ready": neural_confidence_score > 0,
        "explanation_ready": explainability_score > 0,
        "bridge_ready": hybrid_score > 0,
        "conflict_detector_ready": "conflict_score" in hybrid_conflict_result,
        "final_diagnostic_ready": diagnostic_score > 0,
    }

    return {
        "version": "2.6.2.7",
        "layer": "hybrid_reasoning_final_diagnostic",
        "shadow_runtime_only": True,
        "can_influence_runtime": False,
        "runtime_mutation_permissions": [],
        "diagnostic_score": diagnostic_score,
        "diagnostic_strength": diagnostic_strength,
        "diagnostic_decision": diagnostic_decision,
        "conflict_penalty": conflict_penalty,
        "final_diagnostic_chain": final_diagnostic_chain,
        "readiness_flags": readiness_flags,
        "score_state": {
            "symbolic_rule_score": symbolic_rule_score,
            "unified_neural_signal_score": unified_neural_signal_score,
            "neural_confidence_score": neural_confidence_score,
            "explainability_score": explainability_score,
            "hybrid_score": hybrid_score,
            "conflict_score": conflict_score,
        },
        "diagnostics": {
            "bridge_strength": bridge_strength,
            "conflict_severity": conflict_severity,
            "conflict_detected": bool(hybrid_conflict_result.get("conflict_detected")),
            "safe_shadow_diagnostic_only": True,
            "does_not_affect_runtime": True,
        },
    }


def explain_hybrid_reasoning_final_diagnostic_v1() -> Dict[str, Any]:
    """
    Explain the 2.6.2.7 Hybrid Reasoning Final Diagnostic Layer capability.
    """
    return {
        "version": "2.6.2.7",
        "layer": "hybrid_reasoning_final_diagnostic",
        "purpose": "Produce the final shadow diagnostic summary across symbolic reasoning, neural signals, confidence, explanations, bridge alignment, and conflict detection.",
        "shadow_runtime_only": True,
        "can_influence_runtime": False,
        "runtime_mutation_permissions": [],
        "inputs": [
            "symbolic_rule_result",
            "neural_signal_result",
            "neural_confidence_result",
            "neural_explanation_result",
            "symbolic_neural_bridge_result",
            "hybrid_conflict_result",
        ],
        "outputs": [
            "diagnostic_score",
            "diagnostic_strength",
            "diagnostic_decision",
            "conflict_penalty",
            "final_diagnostic_chain",
            "readiness_flags",
            "score_state",
        ],
        "safety": {
            "does_not_rank_targets": True,
            "does_not_select_links": True,
            "does_not_apply_links": True,
            "does_not_mutate_runtime": True,
            "does_not_write_persistence": True,
        },
    }


def build_entity_graph_builder_v1(
    symbols_result: Dict[str, Any] | None = None,
    symbolic_graph_result: Dict[str, Any] | None = None,
    entity_relationship_result: Dict[str, Any] | None = None,
    semantic_topic_graph_result: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    2.6.3.1 Entity Graph Builder.

    Shadow-runtime only.
    Builds a normalized diagnostic entity graph view from existing symbolic,
    relationship, and semantic graph foundations.
    """
    symbols_result = symbols_result or {}
    symbolic_graph_result = symbolic_graph_result or {}
    entity_relationship_result = entity_relationship_result or {}
    semantic_topic_graph_result = semantic_topic_graph_result or {}

    symbols = symbols_result.get("symbols") or symbols_result.get("items") or []
    symbolic_nodes = symbolic_graph_result.get("nodes") or {}
    symbolic_edges = symbolic_graph_result.get("edges") or []
    relationship_edges = entity_relationship_result.get("relationships") or entity_relationship_result.get("edges") or []
    topic_nodes = semantic_topic_graph_result.get("nodes") or {}
    topic_edges = semantic_topic_graph_result.get("edges") or []

    if not isinstance(symbols, list):
        symbols = []
    if not isinstance(symbolic_nodes, dict):
        symbolic_nodes = {}
    if not isinstance(symbolic_edges, list):
        symbolic_edges = []
    if not isinstance(relationship_edges, list):
        relationship_edges = []
    if not isinstance(topic_nodes, dict):
        topic_nodes = {}
    if not isinstance(topic_edges, list):
        topic_edges = []

    entity_nodes = {}

    for item in symbols:
        if isinstance(item, dict):
            name = str(item.get("symbol") or item.get("text" ) or item.get("value") or "").strip()
            kind = str(item.get("type") or item.get("kind") or "symbol")
        else:
            name = str(item or "").strip()
            kind = "symbol"

        if name:
            key = name.lower()
            entity_nodes[key] = {
                "id": key,
                "label": name,
                "type": kind,
                "sources": ["symbols"],
            }

    for key, node in symbolic_nodes.items():
        node_id = str(key or "").strip().lower()
        if not node_id:
            continue
        existing = entity_nodes.get(node_id, {
            "id": node_id,
            "label": str(key),
            "type": "symbolic_node",
            "sources": [],
        })
        existing["sources"] = sorted(set(existing.get("sources", []) + ["symbolic_graph"]))
        if isinstance(node, dict):
            existing["metadata"] = node
        entity_nodes[node_id] = existing

    for key, node in topic_nodes.items():
        node_id = str(key or "").strip().lower()
        if not node_id:
            continue
        existing = entity_nodes.get(node_id, {
            "id": node_id,
            "label": str(key),
            "type": "topic_node",
            "sources": [],
        })
        existing["sources"] = sorted(set(existing.get("sources", []) + ["semantic_topic_graph"]))
        if isinstance(node, dict):
            existing["topic_metadata"] = node
        entity_nodes[node_id] = existing

    entity_edges = []

    def _normalize_edge(edge: Any, source_layer: str) -> Dict[str, Any] | None:
        if not isinstance(edge, dict):
            return None
        source = str(edge.get("source") or edge.get("from") or edge.get("subject") or "").strip().lower()
        target = str(edge.get("target") or edge.get("to") or edge.get("object") or "").strip().lower()
        if not source or not target or source == target:
            return None
        score = _safe_signal_float(
            edge.get("score")
            or edge.get("relationship_score")
            or edge.get("confidence")
            or edge.get("weight")
        )
        return {
            "source": source,
            "target": target,
            "source_layer": source_layer,
            "relationship_type": str(edge.get("type") or edge.get("relationship") or "related_to"),
            "score": score,
            "metadata": edge,
        }

    for edge in symbolic_edges:
        normalized = _normalize_edge(edge, "symbolic_graph")
        if normalized:
            entity_edges.append(normalized)

    for edge in relationship_edges:
        normalized = _normalize_edge(edge, "entity_relationship")
        if normalized:
            entity_edges.append(normalized)

    for edge in topic_edges:
        normalized = _normalize_edge(edge, "semantic_topic_graph")
        if normalized:
            entity_edges.append(normalized)

    graph_density = round(
        len(entity_edges) / max(1, len(entity_nodes)),
        4,
    )

    if len(entity_nodes) >= 5 and len(entity_edges) >= 4:
        graph_strength = "strong"
    elif len(entity_nodes) >= 3 and len(entity_edges) >= 2:
        graph_strength = "moderate"
    elif len(entity_nodes) > 0:
        graph_strength = "weak"
    else:
        graph_strength = "none"

    return {
        "version": "2.6.3.1",
        "layer": "entity_graph_builder",
        "shadow_runtime_only": True,
        "can_influence_runtime": False,
        "runtime_mutation_permissions": [],
        "entity_nodes": entity_nodes,
        "entity_edges": entity_edges,
        "entity_node_count": len(entity_nodes),
        "entity_edge_count": len(entity_edges),
        "graph_density": graph_density,
        "graph_strength": graph_strength,
        "graph_ready": len(entity_nodes) > 0,
        "diagnostics": {
            "symbol_count": len(symbols),
            "symbolic_node_count": len(symbolic_nodes),
            "symbolic_edge_count": len(symbolic_edges),
            "relationship_edge_count": len(relationship_edges),
            "topic_node_count": len(topic_nodes),
            "topic_edge_count": len(topic_edges),
            "safe_shadow_diagnostic_only": True,
        },
    }


def explain_entity_graph_builder_v1() -> Dict[str, Any]:
    """
    Explain the 2.6.3.1 Entity Graph Builder capability.
    """
    return {
        "version": "2.6.3.1",
        "layer": "entity_graph_builder",
        "purpose": "Build a normalized shadow entity graph view from existing symbols, symbolic graphs, relationship graphs, and semantic topic graphs.",
        "shadow_runtime_only": True,
        "can_influence_runtime": False,
        "runtime_mutation_permissions": [],
        "inputs": [
            "symbols_result",
            "symbolic_graph_result",
            "entity_relationship_result",
            "semantic_topic_graph_result",
        ],
        "outputs": [
            "entity_nodes",
            "entity_edges",
            "entity_node_count",
            "entity_edge_count",
            "graph_density",
            "graph_strength",
            "graph_ready",
        ],
        "safety": {
            "does_not_rank_targets": True,
            "does_not_select_links": True,
            "does_not_apply_links": True,
            "does_not_mutate_runtime": True,
            "does_not_write_persistence": True,
        },
    }


def build_relationship_graph_engine_v1(
    entity_graph_result: Dict[str, Any] | None = None,
    symbol_relationship_result: Dict[str, Any] | None = None,
    entity_relationship_result: Dict[str, Any] | None = None,
    semantic_relationship_result: Dict[str, Any] | None = None,
    grown_relationship_result: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    2.6.3.2 Relationship Graph Engine.

    Shadow-runtime only.
    Normalizes and summarizes relationship edges from entity graph,
    symbolic relationships, entity relationships, semantic relationships,
    and grown graph relationships.
    """
    entity_graph_result = entity_graph_result or {}
    symbol_relationship_result = symbol_relationship_result or {}
    entity_relationship_result = entity_relationship_result or {}
    semantic_relationship_result = semantic_relationship_result or {}
    grown_relationship_result = grown_relationship_result or {}

    relationship_edges = []

    def _edge_score(edge: Dict[str, Any]) -> float:
        return _safe_signal_float(
            edge.get("score")
            or edge.get("relationship_score")
            or edge.get("semantic_relationship_score")
            or edge.get("relationship_strength")
            or edge.get("confidence")
            or edge.get("weight")
        )

    def _strength(score: float) -> str:
        if score >= 0.75:
            return "strong"
        if score >= 0.50:
            return "moderate"
        if score > 0:
            return "weak"
        return "none"

    def _normalize_edges(raw_edges: Any, source_layer: str) -> None:
        if not isinstance(raw_edges, list):
            return

        for edge in raw_edges:
            if not isinstance(edge, dict):
                continue

            source = str(
                edge.get("source")
                or edge.get("from")
                or edge.get("subject")
                or edge.get("source_entity")
                or ""
            ).strip().lower()

            target = str(
                edge.get("target")
                or edge.get("to")
                or edge.get("object")
                or edge.get("target_entity")
                or ""
            ).strip().lower()

            if not source or not target or source == target:
                continue

            score = _edge_score(edge)

            relationship_edges.append({
                "source": source,
                "target": target,
                "relationship_type": str(
                    edge.get("relationship")
                    or edge.get("type")
                    or edge.get("edge_type")
                    or "related_to"
                ),
                "score": score,
                "strength": _strength(score),
                "source_layer": source_layer,
                "metadata": edge,
            })

    _normalize_edges(entity_graph_result.get("entity_edges"), "entity_graph")
    _normalize_edges(symbol_relationship_result.get("relationships"), "symbol_relationship")
    _normalize_edges(symbol_relationship_result.get("edges"), "symbol_relationship")
    _normalize_edges(entity_relationship_result.get("relationships"), "entity_relationship")
    _normalize_edges(entity_relationship_result.get("edges"), "entity_relationship")
    _normalize_edges(semantic_relationship_result.get("relationships"), "semantic_relationship")
    _normalize_edges(semantic_relationship_result.get("edges"), "semantic_relationship")
    _normalize_edges(semantic_relationship_result.get("items"), "semantic_relationship")
    _normalize_edges(grown_relationship_result.get("relationships"), "grown_relationship")
    _normalize_edges(grown_relationship_result.get("accepted"), "grown_relationship")
    _normalize_edges(grown_relationship_result.get("edges"), "grown_relationship")

    deduped = {}
    for edge in relationship_edges:
        key = (
            edge["source"],
            edge["target"],
            edge["relationship_type"],
            edge["source_layer"],
        )
        current = deduped.get(key)
        if current is None or edge["score"] > current["score"]:
            deduped[key] = edge

    relationship_edges = list(deduped.values())

    relationship_count = len(relationship_edges)
    total_score = sum(float(edge.get("score", 0.0) or 0.0) for edge in relationship_edges)
    average_relationship_score = round(total_score / max(1, relationship_count), 4)

    strength_distribution = {
        "strong": 0,
        "moderate": 0,
        "weak": 0,
        "none": 0,
    }

    source_layer_distribution = {}

    for edge in relationship_edges:
        strength_distribution[edge["strength"]] = strength_distribution.get(edge["strength"], 0) + 1
        layer = edge.get("source_layer") or "unknown"
        source_layer_distribution[layer] = source_layer_distribution.get(layer, 0) + 1

    if average_relationship_score >= 0.75 and relationship_count >= 3:
        relationship_graph_strength = "strong"
        relationship_decision = "relationship_graph_strong"
    elif average_relationship_score >= 0.50 and relationship_count >= 2:
        relationship_graph_strength = "moderate"
        relationship_decision = "relationship_graph_moderate"
    elif relationship_count > 0:
        relationship_graph_strength = "weak"
        relationship_decision = "relationship_graph_weak"
    else:
        relationship_graph_strength = "none"
        relationship_decision = "relationship_graph_not_found"

    return {
        "version": "2.6.3.2",
        "layer": "relationship_graph_engine",
        "shadow_runtime_only": True,
        "can_influence_runtime": False,
        "runtime_mutation_permissions": [],
        "relationship_edges": relationship_edges,
        "relationship_count": relationship_count,
        "average_relationship_score": average_relationship_score,
        "relationship_graph_strength": relationship_graph_strength,
        "relationship_decision": relationship_decision,
        "strength_distribution": strength_distribution,
        "source_layer_distribution": source_layer_distribution,
        "relationship_graph_ready": relationship_count > 0,
        "diagnostics": {
            "entity_graph_edge_count": len(entity_graph_result.get("entity_edges") or []),
            "symbol_relationship_count": len(symbol_relationship_result.get("relationships") or symbol_relationship_result.get("edges") or []),
            "entity_relationship_count": len(entity_relationship_result.get("relationships") or entity_relationship_result.get("edges") or []),
            "semantic_relationship_count": len(
                semantic_relationship_result.get("relationships")
                or semantic_relationship_result.get("edges")
                or semantic_relationship_result.get("items")
                or []
            ),
            "grown_relationship_count": len(
                grown_relationship_result.get("relationships")
                or grown_relationship_result.get("accepted")
                or grown_relationship_result.get("edges")
                or []
            ),
            "safe_shadow_diagnostic_only": True,
        },
    }


def explain_relationship_graph_engine_v1() -> Dict[str, Any]:
    """
    Explain the 2.6.3.2 Relationship Graph Engine capability.
    """
    return {
        "version": "2.6.3.2",
        "layer": "relationship_graph_engine",
        "purpose": "Normalize and summarize relationship edges across existing symbolic, entity, semantic, and grown graph relationship systems.",
        "shadow_runtime_only": True,
        "can_influence_runtime": False,
        "runtime_mutation_permissions": [],
        "inputs": [
            "entity_graph_result",
            "symbol_relationship_result",
            "entity_relationship_result",
            "semantic_relationship_result",
            "grown_relationship_result",
        ],
        "outputs": [
            "relationship_edges",
            "relationship_count",
            "average_relationship_score",
            "relationship_graph_strength",
            "relationship_decision",
            "strength_distribution",
            "source_layer_distribution",
            "relationship_graph_ready",
        ],
        "safety": {
            "does_not_rank_targets": True,
            "does_not_select_links": True,
            "does_not_apply_links": True,
            "does_not_mutate_runtime": True,
            "does_not_write_persistence": True,
        },
    }

