from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def _data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def _safe_workspace_id(workspace_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\\-]+", "_", str(workspace_id or "default")).strip("_") or "default"


def _active_target_set_path(workspace_id: str) -> Path:
    ws = _safe_workspace_id(workspace_id)
    return _data_dir() / "target_pools" / f"active_target_set_{ws}.json"


def _load_active_target_set(workspace_id: str) -> Dict[str, Any]:
    fp = _active_target_set_path(workspace_id)
    if not fp.exists():
        return {
            "ok": False,
            "workspace_id": workspace_id,
            "path": str(fp),
            "items": [],
            "error": "active_target_set_missing",
        }

    with fp.open("r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items") or data.get("targets") or []
    if not isinstance(items, list):
        items = []

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "path": str(fp),
        "items": items,
        "metadata": data.get("metadata", {}),
        "counts": data.get("counts", {}),
    }


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()


def _tokens(value: Any) -> set:
    text = _norm(value)
    return {t for t in re.findall(r"[a-z0-9]+", text) if len(t) >= 2}



def _flatten_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(_flatten_text(v) for v in value)
    if isinstance(value, dict):
        return " ".join(_flatten_text(v) for v in value.values())
    return str(value)


def _target_text(target: Dict[str, Any]) -> str:
    parts = [
        target.get("url"),
        target.get("title"),
        target.get("label"),
        target.get("h1"),
        target.get("path"),
        target.get("slug"),
        target.get("aliases"),
        target.get("matched_phrases"),
        target.get("active_phrase_matches"),
        target.get("phrase_match_details"),
        target.get("cluster_names"),
        target.get("cluster_keywords"),
        target.get("cluster_matched_terms"),
        target.get("section_names"),
        target.get("section_keywords"),
        target.get("section_matched_terms"),
        target.get("semantic_keywords"),
        target.get("keywords"),
        target.get("metadata"),
    ]
    return " ".join(_flatten_text(p) for p in parts if p)


def _field_contains(target: Dict[str, Any], field: str, search_norm: str) -> bool:
    return bool(search_norm and search_norm in _norm(_flatten_text(target.get(field))))


def _candidate_relationship_weight(candidate: Dict[str, Any]) -> float:
    relationship = _norm(candidate.get("relationship"))
    match_mode = _norm(candidate.get("match_mode"))

    if relationship in {"editor_phrase", "canonical_concept"} or match_mode in {"editor_phrase", "canonical"}:
        return 1.00
    if relationship == "alias" or match_mode == "alias":
        return 0.92
    if relationship in {"related_concept", "broader_concept", "narrower_concept"} or match_mode == "related":
        return 0.38
    return 0.75


def _score_candidate_against_target(candidate: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, Any]:
    search_text = candidate.get("search_text") or ""
    search_norm = _norm(search_text)

    target_blob = _norm(_target_text(target))
    search_tokens = _tokens(search_text)
    target_tokens = _tokens(target_blob)

    overlap = len(search_tokens & target_tokens)
    coverage = overlap / max(len(search_tokens), 1)

    relationship_weight = _candidate_relationship_weight(candidate)
    explicit_search_weight = max(0.10, float(candidate.get("search_weight") or 1.0))

    evidence = {
        "matched_search_text": search_text,
        "relationship": candidate.get("relationship"),
        "match_mode": candidate.get("match_mode"),
        "search_weight": explicit_search_weight,
        "relationship_weight": relationship_weight,
        "matched_title": _field_contains(target, "title", search_norm),
        "matched_label": _field_contains(target, "label", search_norm),
        "matched_h1": _field_contains(target, "h1", search_norm),
        "matched_path": _field_contains(target, "path", search_norm),
        "matched_url": _field_contains(target, "url", search_norm),
        "matched_aliases": _field_contains(target, "aliases", search_norm),
        "matched_active_phrase_matches": _field_contains(target, "active_phrase_matches", search_norm),
        "matched_cluster_names": _field_contains(target, "cluster_names", search_norm),
        "matched_cluster_keywords": _field_contains(target, "cluster_keywords", search_norm),
        "matched_section_names": _field_contains(target, "section_names", search_norm),
        "matched_section_keywords": _field_contains(target, "section_keywords", search_norm),
        "token_overlap": overlap,
        "token_coverage": round(coverage, 4),
    }

    score = 0.0

    if evidence["matched_title"]:
        score += 0.36
    if evidence["matched_label"]:
        score += 0.34
    if evidence["matched_h1"]:
        score += 0.30
    if evidence["matched_path"]:
        score += 0.22
    if evidence["matched_url"]:
        score += 0.18
    if evidence["matched_aliases"]:
        score += 0.24
    if evidence["matched_active_phrase_matches"]:
        score += 0.24
    if evidence["matched_cluster_names"]:
        score += 0.18
    if evidence["matched_cluster_keywords"]:
        score += 0.18
    if evidence["matched_section_names"]:
        score += 0.15
    if evidence["matched_section_keywords"]:
        score += 0.15

    # Token fallback should not allow weak related concepts to dominate.
    if relationship_weight >= 0.90:
        score += min(0.22, coverage * 0.22)
    elif relationship_weight >= 0.70:
        score += min(0.14, coverage * 0.14)
    else:
        score += min(0.08, coverage * 0.08)
    score *= relationship_weight
    score *= explicit_search_weight

    return {
        "score": round(min(score, 1.0), 4),
        "evidence": evidence,
    }



def discover_semantic_targets_for_phrase_v1(
    understood_phrase: Dict[str, Any],
    workspace_id: str,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Step 3: Semantic Target Discovery.

    Responsibilities:
    - Read only Step 2C-ready phrases.
    - Load Active Target Set.
    - Match semantic_match_candidates against target records.
    - Return ranked candidate URLs with evidence.

    Non-responsibilities:
    - Does not crawl.
    - Does not learn semantic meaning.
    - Does not make final link decision.
    - Does not insert editor links.
    """

    if not understood_phrase.get("ready_for_target_discovery"):
        return {
            "ok": False,
            "error": "phrase_not_ready_for_target_discovery",
            "phrase_id": understood_phrase.get("phrase_id"),
            "candidate_targets": [],
        }

    active = _load_active_target_set(workspace_id)
    if not active.get("ok"):
        return {
            "ok": False,
            "error": active.get("error"),
            "phrase_id": understood_phrase.get("phrase_id"),
            "workspace_id": workspace_id,
            "candidate_targets": [],
            "active_target_set_path": active.get("path"),
        }

    semantic_candidates = understood_phrase.get("semantic_match_candidates") or []
    targets = active.get("items") or []

    ranked: List[Dict[str, Any]] = []

    for target in targets:
        best_score = 0.0
        best_evidence: Optional[Dict[str, Any]] = None

        for candidate in semantic_candidates:
            result = _score_candidate_against_target(candidate, target)
            if result["score"] > best_score:
                best_score = result["score"]
                best_evidence = result["evidence"]

        if best_score > 0:
            ranked.append({
                "url": target.get("url"),
                "title": target.get("title"),
                "slug": target.get("slug"),
                "topic_cluster": target.get("topic_cluster"),
                "section_cluster": target.get("section_cluster"),
                "source_pool": target.get("source_pool"),
                "retrieval_score": round(best_score, 4),
                "candidate_evidence": best_evidence or {},
                "target_record": target,
            })

    ranked.sort(key=lambda x: x.get("retrieval_score", 0), reverse=True)
    ranked = ranked[: max(1, int(limit or 10))]

    output_phrase = dict(understood_phrase)
    output_phrase["candidate_target_urls"] = ranked
    output_phrase["processing_state"] = {
        **(output_phrase.get("processing_state") or {}),
        "current_engine": "semantic_target_discovery",
        "status": "target_candidates_found" if ranked else "no_target_candidates_found",
        "target_candidate_count": len(ranked),
        "next_expected_engine": "yellow_semantic_resolver" if ranked else None,
    }
    output_phrase["next_expected_engine"] = "yellow_semantic_resolver" if ranked else None

    return {
        "ok": True,
        "schema_version": "semantic_target_discovery_model_v1",
        "workspace_id": workspace_id,
        "active_target_set_path": active.get("path"),
        "phrase_id": understood_phrase.get("phrase_id"),
        "phrase_text": understood_phrase.get("phrase_text") or understood_phrase.get("text"),
        "semantic_identity": understood_phrase.get("semantic_identity", {}),
        "semantic_match_candidates": semantic_candidates,
        "candidate_target_urls": ranked,
        "candidate_count": len(ranked),
        "processing_state": output_phrase["processing_state"],
        "output_phrase": output_phrase,
        "responsibility_boundary": {
            "uses_only_active_target_set": True,
            "does_not_crawl": True,
            "does_not_learn_semantic_meaning": True,
            "does_not_resolve_final_link": True,
            "does_not_insert_links": True,
        },
    }


def discover_semantic_targets_for_understanding_model_v1(
    understanding_model: Dict[str, Any],
    workspace_id: str,
    limit_per_phrase: int = 10,
) -> Dict[str, Any]:
    phrases = (
        understanding_model.get("understood_phrases")
        or understanding_model.get("yellow_semantic_phrases")
        or understanding_model.get("phrases")
        or []
    )

    discovered = [
        discover_semantic_targets_for_phrase_v1(p, workspace_id=workspace_id, limit=limit_per_phrase)
        for p in phrases
        if isinstance(p, dict)
    ]

    return {
        "ok": True,
        "schema_version": "semantic_target_discovery_registry_model_v1",
        "workspace_id": workspace_id,
        "input_phrase_count": len(phrases),
        "processed_phrase_count": len(discovered),
        "phrases": discovered,
        "next_expected_engine": "yellow_semantic_resolver",
    }


def save_semantic_target_discovery_v1(
    understanding_model: Dict[str, Any],
    workspace_id: str,
    limit_per_phrase: int = 10,
) -> Dict[str, Any]:
    model = discover_semantic_targets_for_understanding_model_v1(
        understanding_model=understanding_model,
        workspace_id=workspace_id,
        limit_per_phrase=limit_per_phrase,
    )

    out_dir = _data_dir() / "semantic_target_discovery"
    out_dir.mkdir(parents=True, exist_ok=True)

    ws = _safe_workspace_id(workspace_id)
    fp = out_dir / f"semantic_target_discovery_{ws}.json"

    with fp.open("w", encoding="utf-8") as f:
        json.dump(model, f, indent=2, ensure_ascii=False)

    model["saved_to"] = str(fp)
    return model


def explain_semantic_target_discovery_v1() -> Dict[str, Any]:
    return {
        "step": "Step 3",
        "name": "Semantic Target Discovery",
        "input": "Step 2C phrases with ready_for_target_discovery and semantic_match_candidates",
        "url_source": "Active Target Set only",
        "output": "Ranked candidate target URLs with retrieval_score and candidate_evidence",
        "does_not_do": [
            "crawl",
            "learn semantic meaning",
            "make final link decision",
            "insert links",
            "explain final resolver decision",
        ],
        "next_expected_engine": "yellow_semantic_resolver",
    }
