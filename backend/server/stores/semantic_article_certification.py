from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    return f"{prefix}_{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:12]}"


def certify_semantic_article_pipeline_v1(
    reading_model: Dict[str, Any],
    context_model: Dict[str, Any],
    extraction_model: Dict[str, Any],
    neighborhood_model: Dict[str, Any],
    intent_model: Dict[str, Any],
    evidence_model: Dict[str, Any],
    graph_model: Dict[str, Any],
    learning_pack: Dict[str, Any],
) -> Dict[str, Any]:

    checks = []

    def check(name: str, passed: bool, details: Dict[str, Any] | None = None):
        checks.append({
            "name": name,
            "passed": bool(passed),
            "details": details or {},
        })

    article_id = reading_model.get("article", {}).get("article_id")

    check("4.6.1 reader phase", reading_model.get("phase") == "4.6.1")
    check("4.6.1 reader valid", reading_model.get("validation", {}).get("valid") is True)

    check("4.6.2 context phase", context_model.get("phase") == "4.6.2")
    check("4.6.2A context patch", context_model.get("patch") == "4.6.2A")

    check("4.6.3 extraction phase", extraction_model.get("phase") == "4.6.3")
    check("4.6.3C extraction patch", extraction_model.get("patch") == "4.6.3C")

    check("4.6.4 neighborhood phase", neighborhood_model.get("phase") == "4.6.4")
    check("4.6.4B neighborhood patch", neighborhood_model.get("patch") == "4.6.4B")

    check("4.6.5 intent phase", intent_model.get("phase") == "4.6.5")
    check("4.6.5B intent patch", intent_model.get("patch") == "4.6.5B")

    check("4.6.6 evidence phase", evidence_model.get("phase") == "4.6.6")
    check("4.6.6A evidence patch", evidence_model.get("patch") == "4.6.6A")

    check("4.6.7 graph phase", graph_model.get("phase") == "4.6.7")
    check("4.6.7A graph patch", graph_model.get("patch") == "4.6.7A")

    check("4.6.8 learning export phase", learning_pack.get("phase") == "4.6.8")
    check("4.6.8A learning export patch", learning_pack.get("patch") == "4.6.8A")

    ids = {
        "reader_article_id": reading_model.get("article", {}).get("article_id"),
        "context_article_id": context_model.get("article", {}).get("article_id"),
        "extraction_article_id": extraction_model.get("article", {}).get("article_id"),
        "neighborhood_article_id": neighborhood_model.get("article", {}).get("article_id"),
        "intent_article_id": intent_model.get("article", {}).get("article_id"),
        "evidence_article_id": evidence_model.get("article", {}).get("article_id"),
        "graph_article_id": graph_model.get("article", {}).get("article_id"),
        "learning_pack_article_id": learning_pack.get("article", {}).get("article_id"),
    }

    check(
        "article id consistency",
        len(set(ids.values())) == 1 and article_id in set(ids.values()),
        ids,
    )

    check(
        "semantic objects exist",
        extraction_model.get("metadata", {}).get("semantic_object_count", 0) > 0,
        extraction_model.get("metadata", {}),
    )

    check(
        "typed neighborhoods exist",
        neighborhood_model.get("metadata", {}).get("neighborhood_count", 0) > 0
        and "relationship_type_counts" in neighborhood_model.get("metadata", {})
        and "relationship_family_counts" in neighborhood_model.get("metadata", {}),
        neighborhood_model.get("metadata", {}),
    )

    check(
        "article intent exists",
        bool(intent_model.get("article_intent"))
        and intent_model.get("article_intent", {}).get("intent_scope") == "article",
        intent_model.get("article_intent", {}),
    )

    check(
        "section intents exist",
        len(intent_model.get("section_intents", [])) > 0
        and all(item.get("intent_scope") == "section" for item in intent_model.get("section_intents", [])),
        {"section_intent_count": len(intent_model.get("section_intents", []))},
    )

    check(
        "section evidence lineage exists",
        all(
            "evidence_lineage" in record
            and "semantic_object_ids" in record["evidence_lineage"]
            and "relationship_ids" in record["evidence_lineage"]
            and "article_intent_id" in record["evidence_lineage"]
            for record in evidence_model.get("section_evidence", [])
        ),
        {"section_evidence_count": len(evidence_model.get("section_evidence", []))},
    )

    check(
        "graph lineage exists",
        bool(graph_model.get("graph_lineage"))
        and graph_model.get("graph_lineage", {}).get("section_evidence_model", {}).get("patch") == "4.6.6A",
        graph_model.get("graph_lineage", {}),
    )

    check(
        "graph layering exists",
        "node_layer_counts" in graph_model.get("metadata", {})
        and "partition_counts" in graph_model.get("metadata", {}),
        graph_model.get("metadata", {}),
    )

    check(
        "learning fingerprint exists",
        bool(learning_pack.get("learning_fingerprint", {}).get("overall_signature")),
        learning_pack.get("learning_fingerprint", {}),
    )

    check(
        "learning statistics exist",
        "semantic_richness_score" in learning_pack.get("learning_statistics", {}),
        learning_pack.get("learning_statistics", {}),
    )

    export_contract = learning_pack.get("export_contract", {})

    check(
        "learning export contract valid",
        export_contract.get("consumer") == "Semantic Workspace Learner"
        and export_contract.get("contract_type") == "compiled_semantic_learning_pack"
        and export_contract.get("graph_internal_details_hidden") is True
        and export_contract.get("memory_write_performed") is False
        and export_contract.get("resolver_decision_performed") is False,
        export_contract,
    )

    boundary_text = " ".join([
        reading_model.get("boundary_rule", ""),
        context_model.get("boundary_rule", ""),
        extraction_model.get("boundary_rule", ""),
        neighborhood_model.get("boundary_rule", ""),
        intent_model.get("boundary_rule", ""),
        evidence_model.get("boundary_rule", ""),
        graph_model.get("boundary_rule", ""),
        learning_pack.get("boundary_rule", ""),
    ]).lower()

    check(
        "boundary rules mention no resolver highlights",
        "blue highlights" in boundary_text and "yellow highlights" in boundary_text,
    )

    check(
        "no memory write performed",
        learning_pack.get("export_contract", {}).get("memory_write_performed") is False,
    )

    check(
        "no resolver decision performed",
        learning_pack.get("export_contract", {}).get("resolver_decision_performed") is False,
    )

    failed = [item for item in checks if not item["passed"]]

    status = "PASSED" if not failed else "FAILED"

    certification_id = _stable_id(
        "semantic_article_certification",
        article_id,
        learning_pack.get("learning_fingerprint", {}).get("overall_signature"),
        status,
    )

    return {
        "schema_version": "semantic_article_certification_v1",
        "phase": "4.6.9",
        "created_at": _now_iso(),
        "certification_id": certification_id,
        "status": status,
        "article_id": article_id,
        "certified_pipeline": [
            "4.6.1",
            "4.6.2A",
            "4.6.3C",
            "4.6.4B",
            "4.6.5B",
            "4.6.6A",
            "4.6.7A",
            "4.6.8A",
        ],
        "checks": checks,
        "failed_checks": failed,
        "final_learning_pack": {
            "learning_pack_id": learning_pack.get("learning_pack_id"),
            "overall_signature": learning_pack.get("learning_fingerprint", {}).get("overall_signature"),
            "semantic_richness_score": learning_pack.get("learning_statistics", {}).get("semantic_richness_score"),
            "canonical_concept_count": learning_pack.get("metadata", {}).get("canonical_concept_count"),
            "learned_relationship_count": learning_pack.get("metadata", {}).get("learned_relationship_count"),
            "intent_pattern_count": learning_pack.get("metadata", {}).get("intent_pattern_count"),
        },
        "metadata": {
            "check_count": len(checks),
            "passed_check_count": len([item for item in checks if item["passed"]]),
            "failed_check_count": len(failed),
        },
        "boundary_rule": (
            "End-to-End Semantic Article Certification verifies the full semantic article pipeline only. "
            "It does not resolve links, create blue highlights, create yellow highlights, score target pages, "
            "write memory, perform reasoning, or generate explanations."
        ),
    }


def save_semantic_article_certification_v1(
    certification_model: Dict[str, Any],
    output_path: str | Path,
) -> Dict[str, Any]:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(certification_model, indent=2, ensure_ascii=False), encoding="utf-8")
    return certification_model


def explain_semantic_article_certification_v1() -> Dict[str, Any]:
    return {
        "phase": "4.6.9",
        "name": "End-to-End Semantic Article Certification",
        "purpose": "Certify the full Semantic Article Intelligence pipeline from reader to learner-ready Learning Pack.",
        "input": [
            "4.6.1 Semantic Article Reader",
            "4.6.2A Semantic Context Builder",
            "4.6.3C Entity & Concept Extraction",
            "4.6.4B Phrase Neighborhood Intelligence",
            "4.6.5B Topic Intent Intelligence",
            "4.6.6A Section Evidence Builder",
            "4.6.7A Semantic Relationship Graph",
            "4.6.8A Semantic Learning Export",
        ],
        "output": "Semantic Article Certification Model",
        "does": [
            "certifies all refined phase versions",
            "validates article ID consistency",
            "validates semantic objects",
            "validates typed neighborhoods",
            "validates article and section intents",
            "validates section evidence lineage",
            "validates graph lineage",
            "validates graph layering and partitions",
            "validates learning fingerprints",
            "validates semantic statistics",
            "validates learning export contract",
            "validates no resolver or memory boundary violations",
        ],
        "does_not": [
            "perform internal link resolving",
            "perform semantic link resolving",
            "create blue highlights",
            "create yellow highlights",
            "score target pages",
            "write memory",
            "perform reasoning",
            "generate explanations",
        ],
    }
