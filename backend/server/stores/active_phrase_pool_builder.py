from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from backend.server.stores.active_phrase_set_store import load_active_phrase_set
from backend.server.stores.candidate_window_guard import candidate_window_guard
from backend.server.stores.phrase_strength_scorer import score_phrase_strength


ACTIVE_POOL_BUILD = "2026-05-11-UPLOAD-ONLY-RUNTIME-SUPPORTING-DI"

CONNECTORS = {
    "about", "after", "before", "because", "by", "during", "for",
    "from", "in", "into", "of", "on", "than", "that", "to",
    "with", "without", "while", "whether", "rather",
}

RUNTIME_BAD_STARTS = {
    "from", "with", "without", "before", "after", "during", "because",
    "rather", "inside", "outside", "into", "based", "confirm", "estimate",
    "guess", "guessing", "identify", "put", "shift", "shorter", "longer",
    "early", "late", "adjust",
}

RUNTIME_BAD_ENDS = {
    "from", "with", "without", "before", "after", "during", "because",
    "rather", "the", "a", "an", "of", "to", "and", "or", "but",
    "guesswork", "early", "late",
}

RUNTIME_BAD_PATTERNS = (
    r"\bfrom guesswork\b",
    r"\bconfirm the\b",
    r"\bestimate the\b",
    r"\badjust the\b",
    r"\bshorter adjust\b",
    r"\bsigns an early\b",
    r"\bbased on\b",
    r"\brather than\b",
)

ACTIVE_POOL_INTELLIGENCE_LAYERS = [
    "workspace_isolation",
    "upload_only_runtime_highlight_authority",
    "quality_gate_recheck",
    "phrase_strength_recheck",
    "runtime_cleanliness_quarantine",
    "semantic_fragment_suppression",
    "upload_semantic_duplicate_suppression",
    "supporting_intelligence_metadata_bridge",
    "di_runtime_separation_ready",
    "explainability",
    "qa_regression_readiness",
]

SUPPORTING_INTELLIGENCE_LAYERS = [
    "live_domain_intelligence",
    "draft_intelligence",
    "imported_intelligence",
]

ADAPTIVE_THRESHOLDS = {
    "title": 0.78,
    "heading_h1": 0.78,
    "draft_title": 0.76,
    "import_title": 0.76,
    "entity": 0.52,
    "intent": 0.58,
    "noun_phrase": 0.62,
    "sentence": 0.72,
    "default": 0.68,
}

VERTICAL_THRESHOLD_ADJUSTMENTS = {
    "medical_healthcare": -0.08,
    "pharmacy": -0.08,
    "mental_health": -0.06,
    "fitness": -0.05,
    "nutrition": -0.05,
    "education": -0.04,
    "finance": 0.03,
    "legal": 0.04,
    "construction": 0.04,
    "manufacturing": 0.03,
}


def _data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def _ws_safe(ws: str) -> str:
    raw = (ws or "default").strip()
    if not raw or raw.lower() == "default":
        return "default"
    if raw.lower().startswith("ws_"):
        return raw

    s = raw.lower()
    s = s.replace(".", "_").replace("-", "_").replace(" ", "_")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return f"ws_{s or 'workspace'}"[:80]


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _upload_pool_path(ws: str) -> Path:
    return _data_dir() / "phrase_pools" / "upload" / f"upload_phrase_pool_{_ws_safe(ws)}.json"


def _live_pool_path(ws: str) -> Path:
    return _data_dir() / "phrase_pools" / "live_domain" / f"live_domain_phrase_pool_{_ws_safe(ws)}.json"


def _draft_pool_path(ws: str) -> Path:
    return _data_dir() / "phrase_pools" / "draft" / f"draft_phrase_pool_{_ws_safe(ws)}.json"


def _imported_pool_path(ws: str) -> Path:
    return _data_dir() / "phrase_pools" / "imported" / f"imported_phrase_pool_{_ws_safe(ws)}.json"


def _active_phrase_pool_path(ws: str) -> Path:
    return _data_dir() / "phrase_pools" / "active" / f"active_phrase_pool_{_ws_safe(ws)}.json"


def _canonical_phrase(text: Any) -> str:
    s = str(text or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"^[\"'“”‘’\(\[\{]+|[\"'“”‘’\)\]\}:;,\.\!\?]+$", "", s)
    return s.strip()


def _tokens(phrase: str) -> List[str]:
    return re.findall(r"[a-z0-9]{2,}", str(phrase or "").lower())


def _content_tokens(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in CONNECTORS]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _normalize_unit_score(value: Any) -> float:
    v = _safe_float(value, 0.0)
    if v > 1.0:
        v = v / 100.0
    return max(0.0, min(1.0, v))


def _is_runtime_dirty_phrase(phrase: str) -> Tuple[bool, str]:
    p = _canonical_phrase(phrase)
    toks = _tokens(p)

    if not p or not toks:
        return True, "empty_or_tokenless"
    if len(toks) < 2:
        return True, "too_short_runtime"
    if len(toks) > 6:
        return True, "too_long_runtime"
    if toks[0] in RUNTIME_BAD_STARTS:
        return True, "runtime_bad_start"
    if toks[-1] in RUNTIME_BAD_ENDS:
        return True, "runtime_bad_end"

    for pattern in RUNTIME_BAD_PATTERNS:
        if re.search(pattern, p):
            return True, "runtime_bad_pattern"

    return False, ""


def _semantic_root(phrase: str) -> str:
    toks = _content_tokens(_tokens(phrase))
    if not toks:
        toks = _tokens(phrase)
    return " ".join(toks[:2])


def _semantic_overlap(a: str, b: str) -> float:
    ta = set(_tokens(a))
    tb = set(_tokens(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(1, len(ta | tb))

def _is_semantic_competitor(a: str, b: str) -> bool:
    a = _canonical_phrase(a)
    b = _canonical_phrase(b)

    if not a or not b:
        return False

    if a == b:
        return True

    ta = _tokens(a)
    tb = _tokens(b)

    if len(ta) < 2 or len(tb) < 2:
        return False

    set_a = set(ta)
    set_b = set(tb)

    shorter_len = min(len(ta), len(tb))
    longer_len = max(len(ta), len(tb))

    overlap = len(set_a & set_b) / max(1, len(set_a | set_b))

    # Exact containment can still be duplicate, but only when the longer phrase
    # looks like a weak wrapper around the shorter phrase.
    if a in b or b in a:
        longer_phrase = b if len(tb) > len(ta) else a
        longer_tokens = _tokens(longer_phrase)

        starts_weak = longer_tokens[0] in RUNTIME_WEAK_STARTS if longer_tokens else False
        ends_weak = longer_tokens[-1] in RUNTIME_WEAK_ENDS if longer_tokens else False
        too_long_wrapper = longer_len >= 5

        if starts_weak or ends_weak or too_long_wrapper:
            return True

        # Keep useful variants like:
        # personalized ovulation calculator
        # real time ovulation calculator
        # luteal phase length
        return False

    # Strong overlap only. This prevents related phrases from being removed
    # just because they share the same semantic root.
    if overlap >= 0.78 and shorter_len >= 2:
        return True

    return False


def _record_score(rec: Dict[str, Any]) -> float:
    builder = rec.get("builder_intelligence") if isinstance(rec.get("builder_intelligence"), dict) else {}
    selector = rec.get("selector_intelligence") if isinstance(rec.get("selector_intelligence"), dict) else {}
    strength = rec.get("strength") if isinstance(rec.get("strength"), dict) else {}
    qg = rec.get("quality_gate") if isinstance(rec.get("quality_gate"), dict) else {}

    candidates = [
        builder.get("builder_score"),
        selector.get("selector_score"),
        strength.get("score"),
        qg.get("quality_gate_score"),
        rec.get("builder_score"),
        rec.get("score"),
        rec.get("quality_score"),
        rec.get("strength_score"),
    ]

    return max(_normalize_unit_score(x) for x in candidates)


def _source_priority(source_name: str, rec: Dict[str, Any]) -> float:
    source_type = str(rec.get("source_type") or "").lower()

    if source_name == "upload":
        base = 0.96
    else:
        base = 0.70

    if source_type in {"title", "heading_h1"}:
        base += 0.04
    elif source_type in {"entity", "intent"}:
        base += 0.03

    return max(0.0, min(1.0, base))


def _adaptive_threshold(source_type: str, vertical: str) -> float:
    source_type = str(source_type or "").strip().lower()
    vertical = str(vertical or "").strip().lower()

    threshold = ADAPTIVE_THRESHOLDS.get(source_type, ADAPTIVE_THRESHOLDS["default"])
    threshold += VERTICAL_THRESHOLD_ADJUSTMENTS.get(vertical, 0.0)

    return max(0.40, min(0.92, threshold))


def _multi_layer_confidence(
    quality_gate_score: float,
    strength_score: float,
    source_priority: float,
) -> float:
    return round(
        (quality_gate_score * 0.40)
        + (strength_score * 0.40)
        + (source_priority * 0.20),
        4,
    )


def _quarantine_phrase(
    phrase: str,
    rec: Dict[str, Any],
    source_name: str,
) -> Tuple[bool, str, Dict[str, Any]]:
    phrase = _canonical_phrase(phrase)

    if not phrase:
        return False, "empty_phrase", {}

    runtime_dirty, runtime_reason = _is_runtime_dirty_phrase(phrase)
    if runtime_dirty:
        return False, runtime_reason, {}

    source_type = str(rec.get("source_type") or "")

    guard = candidate_window_guard(phrase, source_type=source_type)
    if isinstance(guard, dict) and not guard.get("keep"):
        return False, f"quality_gate_{guard.get('reason') or 'reject'}", {
            "quality_gate": guard.get("quality_gate") if isinstance(guard.get("quality_gate"), dict) else {}
        }

    guarded_phrase = _canonical_phrase(
        str(guard.get("phrase") or phrase) if isinstance(guard, dict) else phrase
    )

    strength = score_phrase_strength(phrase=guarded_phrase, source_type=source_type)

    if isinstance(strength, dict) and not strength.get("keep"):
        return False, f"strength_{strength.get('reason') or 'reject'}", {
            "quality_gate": guard.get("quality_gate") if isinstance(guard, dict) else {},
            "strength": strength,
        }

    enriched = dict(rec)
    enriched["phrase"] = guarded_phrase
    enriched["canonical"] = guarded_phrase
    enriched["runtime_source"] = "upload_phrase_pool"
    enriched["highlight_authority"] = "upload_only"

    if isinstance(guard, dict) and isinstance(guard.get("quality_gate"), dict):
        enriched["quality_gate"] = guard.get("quality_gate")

    if isinstance(strength, dict):
        enriched["strength"] = strength

    base_score = _record_score(enriched)
    source_score = _source_priority(source_name, enriched)

    quality_gate_score = _normalize_unit_score(
        (enriched.get("quality_gate") or {}).get("quality_gate_score", 0.0)
    )

    strength_score = _normalize_unit_score(
        (enriched.get("strength") or {}).get("score", 0.0)
    )

    confidence_stack = _multi_layer_confidence(
        quality_gate_score=quality_gate_score,
        strength_score=strength_score,
        source_priority=source_score,
    )

    adaptive_threshold = _adaptive_threshold(
        source_type=str(enriched.get("source_type") or ""),
        vertical=str(enriched.get("vertical") or ""),
    )

    active_score = round(
        (base_score * 0.35)
        + (quality_gate_score * 0.20)
        + (strength_score * 0.20)
        + (confidence_stack * 0.25),
        4,
    )

    if active_score < adaptive_threshold:
        return False, "adaptive_threshold_reject", {
            "active_score": active_score,
            "adaptive_threshold": adaptive_threshold,
            "confidence_stack": confidence_stack,
        }

    enriched["active_pool_intelligence"] = {
        "active_score": active_score,
        "source_priority": round(source_score, 4),
        "base_phrase_score": round(base_score, 4),
        "adaptive_threshold": adaptive_threshold,
        "confidence_stack": confidence_stack,
        "decision": "ACCEPT",
        "reason": "upload_only_active_pool_accept",
        "highlight_authority": "upload_phrase_pool_only",
        "supporting_pools_allowed_to_highlight": False,
        "layers": ACTIVE_POOL_INTELLIGENCE_LAYERS,
    }

    enriched["di_metadata"] = {
        "runtime_role": "primary_highlight_phrase",
        "highlight_layer": "PRIMARY_HIGHLIGHT_LAYER",
        "supporting_intelligence_eligible": True,
        "supporting_sources": SUPPORTING_INTELLIGENCE_LAYERS,
    }

    enriched["active_score"] = active_score

    return True, "upload_only_active_pool_accept", enriched

RUNTIME_WEAK_STARTS = {
    "using", "know", "mark", "track", "tracking", "calculate", "predict",
    "understand", "confirm", "estimate", "adjust", "count", "counting",
    "record", "check", "watch", "look", "looking",
}

RUNTIME_WEAK_ENDS = {
    "for", "with", "without", "from", "into", "during", "before",
    "after", "because", "than", "that", "care", "natural",
}

RUNTIME_WEAK_WRAPPERS = {
    "using", "know", "mark", "track", "tracking", "calculate", "predict",
    "understand", "confirm", "estimate", "adjust", "count", "counting",
    "record", "check", "watch", "look", "looking", "expected", "typical",
}

RUNTIME_STRONG_HEADS = {
    "ovulation", "fertile", "fertility", "cycle", "period", "mucus",
    "temperature", "bbt", "luteal", "phase", "calculator", "kits",
    "symptoms", "date", "window", "days", "clues", "patterns",
}


def _runtime_phrase_quality(phrase: str) -> float:
    p = _canonical_phrase(phrase)
    toks = _tokens(p)

    if not p or not toks:
        return 0.0

    score = 0.50
    token_count = len(toks)

    if 2 <= token_count <= 4:
        score += 0.18
    elif token_count == 5:
        score += 0.08
    elif token_count >= 6:
        score -= 0.16

    if toks[0] in RUNTIME_STRONG_HEADS:
        score += 0.12

    if any(t in RUNTIME_STRONG_HEADS for t in toks):
        score += 0.10

    if toks[0] in RUNTIME_WEAK_STARTS:
        score -= 0.18

    if toks[-1] in RUNTIME_WEAK_ENDS:
        score -= 0.22

    weak_wrapper_count = sum(1 for t in toks if t in RUNTIME_WEAK_WRAPPERS)
    if weak_wrapper_count:
        score -= min(0.20, weak_wrapper_count * 0.07)

    if re.search(r"\b(for|with|without|from|into|during|before|after)\s+[a-z0-9]+$", p):
        score -= 0.12

    if re.search(r"\b(know|mark|using|calculate|track|tracking)\s+the\b", p):
        score -= 0.18

    if re.search(r"\b(months|days)\s+for\b", p):
        score -= 0.16

    if re.search(r"\bfor\s+(natural|care)$", p):
        score -= 0.20

    return round(max(0.0, min(1.0, score)), 4)


def _runtime_selection_score(rec: Dict[str, Any]) -> float:
    phrase = str(rec.get("phrase") or "")
    active_score = _safe_float(rec.get("active_score"), _record_score(rec))
    quality = _runtime_phrase_quality(phrase)

    toks = _tokens(phrase)
    length_bonus = 0.0

    if 2 <= len(toks) <= 4:
        length_bonus = 0.05
    elif len(toks) == 5:
        length_bonus = 0.02
    elif len(toks) >= 6:
        length_bonus = -0.06

    return round(
        (active_score * 0.60)
        + (quality * 0.35)
        + length_bonus,
        4,
    )


def _better_record(current: Dict[str, Any], challenger: Dict[str, Any]) -> Dict[str, Any]:
    current_selection_score = _runtime_selection_score(current)
    challenger_selection_score = _runtime_selection_score(challenger)

    current_phrase = str(current.get("phrase") or "")
    challenger_phrase = str(challenger.get("phrase") or "")

    current["runtime_selection_quality"] = {
        "phrase_quality": _runtime_phrase_quality(current_phrase),
        "selection_score": current_selection_score,
    }

    challenger["runtime_selection_quality"] = {
        "phrase_quality": _runtime_phrase_quality(challenger_phrase),
        "selection_score": challenger_selection_score,
    }

    if challenger_selection_score > current_selection_score:
        return challenger

    if challenger_selection_score == current_selection_score:
        current_tokens = len(_tokens(current_phrase))
        challenger_tokens = len(_tokens(challenger_phrase))

        if 2 <= challenger_tokens <= 4 and challenger_tokens < current_tokens:
            return challenger

    return current


def _supporting_pool_metadata(ws: str, active_obj: Dict[str, Any]) -> Dict[str, Any]:
    supporting = {
        "enabled": True,
        "runtime_highlight_injection_allowed": False,
        "purpose": "DI_SUPPORTING_INTELLIGENCE_ONLY",
        "layers": SUPPORTING_INTELLIGENCE_LAYERS,
        "sources": {},
    }

    configs = {
        "live_domain": {
            "path": _live_pool_path(ws),
            "active_refs": active_obj.get("active_live_domain_urls") or [],
            "di_roles": [
                "internal_url_relevance",
                "sitemap_relationships",
                "existing_page_authority",
                "topical_proximity",
                "link_confidence",
            ],
        },
        "draft": {
            "path": _draft_pool_path(ws),
            "active_refs": active_obj.get("active_draft_ids") or [],
            "di_roles": [
                "future_content_opportunities",
                "topic_gap_intelligence",
                "planned_article_relationships",
                "expansion_suggestions",
            ],
        },
        "imported": {
            "path": _imported_pool_path(ws),
            "active_refs": active_obj.get("active_imported_urls")
            or active_obj.get("active_import_ids")
            or [],
            "di_roles": [
                "manual_target_matching",
                "imported_url_relevance",
                "external_internal_mapping",
                "curated_target_confidence",
            ],
        },
    }

    for name, cfg in configs.items():
        path = cfg["path"]
        obj = _safe_read_json(path) if path.exists() else None
        phrases = obj.get("phrases") if isinstance(obj, dict) and isinstance(obj.get("phrases"), dict) else {}

        supporting["sources"][name] = {
            "pool_exists": path.exists(),
            "phrase_count": len(phrases),
            "active_reference_count": len([x for x in cfg["active_refs"] if str(x).strip()]),
            "runtime_role": "supporting_intelligence_only",
            "feeds_di": True,
            "feeds_runtime_highlights": False,
            "di_roles": cfg["di_roles"],
        }

    return supporting


def build_active_phrase_pool(workspace_id: str) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)
    active_obj = load_active_phrase_set(ws)

    active_document_ids = [
        str(x).strip()
        for x in (
            active_obj.get("active_upload_ids")
            or active_obj.get("active_document_ids")
            or []
        )
        if str(x).strip()
    ]

    upload_path = _upload_pool_path(ws)

    merged: Dict[str, Dict[str, Any]] = {}
    rejected: Dict[str, Dict[str, Any]] = {}

    counts_by_source: Dict[str, int] = {
        "upload": 0,
        "live_domain": 0,
        "draft": 0,
        "imported": 0,
    }

    accepted_by_source: Dict[str, int] = {
        "upload": 0,
        "live_domain": 0,
        "draft": 0,
        "imported": 0,
    }

    rejected_by_source: Dict[str, int] = {
        "upload": 0,
        "live_domain": 0,
        "draft": 0,
        "imported": 0,
    }

    sources_used: Dict[str, bool] = {
        "upload": False,
        "live_domain": False,
        "draft": False,
        "imported": False,
    }

    rejection_reasons: Counter[str] = Counter()

    upload_obj = _safe_read_json(upload_path) if upload_path.exists() else None
    upload_phrases = (
        upload_obj.get("phrases")
        if isinstance(upload_obj, dict) and isinstance(upload_obj.get("phrases"), dict)
        else {}
    )

    counts_by_source["upload"] = len(upload_phrases)
    sources_used["upload"] = bool(upload_path.exists() and active_document_ids)

    if active_document_ids and upload_phrases:
        for phrase, rec in upload_phrases.items():
            if not isinstance(rec, dict):
                continue

            raw_key = _canonical_phrase(phrase)
            if not raw_key:
                continue

            keep, reason, enriched = _quarantine_phrase(raw_key, rec, "upload")

            if not keep:
                rejected_by_source["upload"] += 1
                rejection_reasons[reason] += 1
                rejected[raw_key] = {
                    "phrase": raw_key,
                    "source": "upload",
                    "reason": reason,
                }
                continue

            key = _canonical_phrase(enriched.get("phrase") or raw_key)

            if not key:
                continue

            accepted_by_source["upload"] += 1

            if key not in merged:
                enriched.setdefault("pool_sources", [])
                if "upload" not in enriched["pool_sources"]:
                    enriched["pool_sources"].append("upload")
                merged[key] = enriched
            else:
                merged[key] = _better_record(merged[key], enriched)

    semantic_selected: Dict[str, Dict[str, Any]] = {}
    semantic_collisions: List[Dict[str, Any]] = []

    for phrase, rec in sorted(
        merged.items(),
        key=lambda kv: -_safe_float(kv[1].get("active_score"), _record_score(kv[1])),
    ):
        competitor_key = ""
        for existing_phrase in semantic_selected.keys():
            if _is_semantic_competitor(phrase, existing_phrase):
                competitor_key = existing_phrase
                break

        if competitor_key:
            candidate = rec
            existing = semantic_selected[competitor_key]
            winner = _better_record(existing, candidate)
            loser = candidate if winner is existing else existing

            semantic_collisions.append({
                "phrase": phrase,
                "competitor": competitor_key,
                "winner": winner.get("phrase"),
                "loser": loser.get("phrase"),
                "reason": "upload_semantic_competitor_suppressed",
            })

            if winner is candidate:
                semantic_selected.pop(competitor_key, None)
                semantic_selected[phrase] = candidate

            continue

        semantic_selected[phrase] = rec

    final_phrases = dict(sorted(
        semantic_selected.items(),
        key=lambda kv: (
            -_safe_float(kv[1].get("active_score"), _record_score(kv[1])),
            kv[0],
        ),
    ))

    supporting_intelligence = _supporting_pool_metadata(ws, active_obj)

    for source_name, meta in supporting_intelligence["sources"].items():
        counts_by_source[source_name] = meta["phrase_count"]
        sources_used[source_name] = meta["pool_exists"]

    out = {
        "workspace_id": ws,
        "type": "active_phrase_pool",
        "build": ACTIVE_POOL_BUILD,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "architecture": {
            "runtime_model": "UPLOAD_ONLY_PRIMARY_HIGHLIGHT_LAYER",
            "primary_highlight_source": "upload_phrase_pool",
            "supporting_pools_runtime_highlight_injection_allowed": False,
            "supporting_pools_di_only": ["live_domain", "draft", "imported"],
            "result": "ARTICLE_TRUE_HIGHLIGHTS_NOT_POOL_TRUE_HIGHLIGHTS",
        },
        "counts_by_source": counts_by_source,
        "accepted_by_source": accepted_by_source,
        "rejected_by_source": rejected_by_source,
        "sources_used": sources_used,
        "active_phrase_set_used": {
            "active_document_ids_count": len(active_document_ids),
            "active_draft_ids_count": len(active_obj.get("active_draft_ids") or []),
            "active_live_domain_urls_count": len(active_obj.get("active_live_domain_urls") or []),
            "active_imported_urls_count": len(
                active_obj.get("active_imported_urls")
                or active_obj.get("active_import_ids")
                or []
            ),
        },
        "supporting_intelligence_inputs": supporting_intelligence,
        "active_pool_intelligence_summary": {
            "enabled": True,
            "layers": ACTIVE_POOL_INTELLIGENCE_LAYERS,
            "runtime_highlight_source": "upload_only",
            "supporting_pools_excluded_from_runtime_merge": True,
            "rejected_phrase_count": len(rejected),
            "rejection_reasons": dict(rejection_reasons),
            "semantic_collision_count": len(semantic_collisions),
            "semantic_collisions_sample": semantic_collisions[:20],
        },
        "phrase_count": len(final_phrases),
        "phrases": final_phrases,
    }

    out_path = _active_phrase_pool_path(ws)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    return out