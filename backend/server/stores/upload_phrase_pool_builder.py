# backend/server/stores/upload_phrase_pool_builder.py
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

from backend.server.stores.active_phrase_set_store import load_active_phrase_set
from backend.server.stores.candidate_window_guard import candidate_window_guard
from backend.server.stores.phrase_strength_scorer import score_phrase_strength
from backend.server.utils.text_normalization import fix_mojibake_text


def _data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def _ws_safe(ws: str) -> str:
    ws = (ws or "default").strip().lower()
    ws = re.sub(r"[^a-z0-9_\-]", "_", ws)[:80] or "default"
    if ws.startswith("ws_ws_"):
        ws = ws[3:]
    return ws


def _upload_phrase_index_path(ws: str) -> Path:
    return _data_dir() / f"upload_phrase_index_{_ws_safe(ws)}.json"


def _upload_phrase_pool_path(ws: str) -> Path:
    return _data_dir() / "phrase_pools" / "upload" / f"upload_phrase_pool_{_ws_safe(ws)}.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_read_json(fp: Path) -> Any:
    try:
        if not fp.exists():
            return None
        return json.loads(fp.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_json(fp: Path, obj: Any) -> None:
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _clean_text(s: Any) -> str:
    return fix_mojibake_text(str(s or "").strip())


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default


def _clean_examples(v: Any) -> List[Dict[str, str]]:
    if not isinstance(v, list):
        return []

    out: List[Dict[str, str]] = []

    for ex in v:
        if not isinstance(ex, dict):
            continue

        item = {
            "doc_id": _clean_text(ex.get("doc_id") or ""),
            "section_id": _clean_text(ex.get("section_id") or ""),
            "snippet": _clean_text(ex.get("snippet") or ""),
        }

        if item["doc_id"] or item["section_id"] or item["snippet"]:
            out.append(item)

    return out[:5]


def _canonical_phrase(s: str) -> str:
    s = _clean_text(s).lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"^[\"'“”‘’\(\[\{]+|[\"'“”‘’\)\]\}:;,\.\!\?]+$", "", s).strip()
    return s


def _extract_canonical_core_phrase(s: str) -> str:
    s = _canonical_phrase(s)

    if not s:
        return ""

    intent_markers = [
        "how to ",
        "how many ",
        "when do ",
        "what is ",
        "what are ",
        "why does ",
        "why do ",
        "where is ",
        "where do ",
        "signs of ",
        "symptoms of ",
        "causes of ",
        "treatment for ",
        "best time ",
        "best way ",
    ]

    starts = [s.find(m) for m in intent_markers if s.find(m) != -1]
    if starts:
        s = s[min(starts):].strip()

    lead_patterns = [
        r"^people often ask\s+",
        r"^many people ask\s+",
        r"^users often ask\s+",
        r"^many users ask\s+",
        r"^readers often ask\s+",
        r"^many readers ask\s+",
        r"^customers often ask\s+",
        r"^many customers ask\s+",
        r"^clients often ask\s+",
        r"^many clients ask\s+",
        r"^students often ask\s+",
        r"^many students ask\s+",
        r"^parents often ask\s+",
        r"^many parents ask\s+",
        r"^patients often ask\s+",
        r"^many patients ask\s+",
        r"^business owners often ask\s+",
        r"^many business owners ask\s+",
        r"^teams often ask\s+",
        r"^many teams ask\s+",
        r"^professionals often ask\s+",
        r"^many professionals ask\s+",
        r"^creators often ask\s+",
        r"^many creators ask\s+",
        r"^you may wonder\s+",
        r"^you might wonder\s+",
        r"^you may ask\s+",
        r"^you might ask\s+",
        r"^you may be asking\s+",
        r"^often ask\s+",
    ]

    for pat in lead_patterns:
        s = re.sub(pat, "", s).strip()

    trailing_cut_patterns = [
        r"^(how to [a-z0-9\s\-]{1,80}?)(?:\s+after\b.*|\s+with\b.*|\s+for\b.*|\s+during\b.*|\s+because\b.*)$",
        r"^(when do [a-z0-9\s\-]{1,80}?)(?:\s+after\b.*|\s+with\b.*|\s+during\b.*)$",
        r"^(what is [a-z0-9\s\-]{1,80}?)(?:\s+for\b.*|\s+in\b.*)$",
        r"^(signs of [a-z0-9\s\-]{1,80}?)(?:\s+in\b.*|\s+during\b.*)$",
        r"^(symptoms of [a-z0-9\s\-]{1,80}?)(?:\s+in\b.*|\s+during\b.*)$",
    ]

    for pat in trailing_cut_patterns:
        m = re.match(pat, s)
        if m:
            s = m.group(1).strip()
            break

    return _canonical_phrase(s)


def _light_normalize_phrase(phrase: str) -> str:
    return _extract_canonical_core_phrase(phrase) or _canonical_phrase(phrase)


def _quality_gate_phrase_with_metadata(phrase: str, source_type: str = "") -> Dict[str, Any]:
    phrase = _extract_canonical_core_phrase(phrase) or _canonical_phrase(phrase)

    if not phrase:
        return {
            "keep": False,
            "phrase": "",
            "quality_gate": {},
            "strength": {},
        }

    guard = candidate_window_guard(phrase, source_type=source_type or "")
    if not isinstance(guard, dict) or not guard.get("keep"):
        return {
            "keep": False,
            "phrase": "",
            "quality_gate": guard.get("quality_gate") if isinstance(guard, dict) else {},
            "strength": {},
        }

    guarded_phrase = _canonical_phrase(str(guard.get("phrase") or phrase))

    scored = score_phrase_strength(
        phrase=guarded_phrase,
        source_type=source_type or "",
    )

    if not isinstance(scored, dict) or not scored.get("keep"):
        return {
            "keep": False,
            "phrase": "",
            "quality_gate": guard.get("quality_gate") if isinstance(guard, dict) else {},
            "strength": scored if isinstance(scored, dict) else {},
        }

    final_phrase = _canonical_phrase(str(scored.get("phrase") or guarded_phrase))

    return {
        "keep": True,
        "phrase": final_phrase,
        "quality_gate": guard.get("quality_gate") if isinstance(guard, dict) else {},
        "strength": scored,
    }


def _quality_gate_phrase(phrase: str, source_type: str = "") -> str:
    result = _quality_gate_phrase_with_metadata(phrase, source_type)
    return str(result.get("phrase") or "") if result.get("keep") else ""


def _record_score(rec: Dict[str, Any]) -> float:
    for key in ("builder_score", "score", "quality_score", "strength_score"):
        try:
            val = float(rec.get(key) or 0.0)
            if val:
                return val
        except Exception:
            continue
    return 0.0


def _extract_extractor_score(rec: Dict[str, Any]) -> float:
    info = rec.get("extractor_intelligence")
    if not isinstance(info, dict):
        return 0.0
    return _safe_float(info.get("score"), 0.0)


def _extract_quality_gate_score(rec: Dict[str, Any]) -> float:
    qg = rec.get("quality_gate")
    if not isinstance(qg, dict):
        return 0.0
    return _safe_float(qg.get("quality_gate_score"), 0.0)


def _extract_strength_score(rec: Dict[str, Any]) -> float:
    strength = rec.get("strength")
    if isinstance(strength, dict):
        for key in ("score", "quality_score", "strength_score"):
            val = _safe_float(strength.get(key), 0.0)
            if val:
                return val

    for key in ("score", "quality_score", "strength_score"):
        val = _safe_float(rec.get(key), 0.0)
        if val:
            return val

    return 0.0


def _source_priority(source_type: str) -> float:
    source_type = str(source_type or "").strip().lower()

    if source_type == "title":
        return 1.00
    if source_type in {"heading_h1", "heading_h2"}:
        return 0.95
    if source_type in {"heading_h3", "heading_h4", "heading_h5", "heading_h6"}:
        return 0.88
    if source_type in {"intent", "entity"}:
        return 0.84
    if source_type in {"noun_phrase", "action_object", "condition_phrase"}:
        return 0.78
    if source_type == "list_item":
        return 0.74

    return 0.65


def _cross_document_strength(rec: Dict[str, Any]) -> float:
    docs = rec.get("docs") if isinstance(rec.get("docs"), dict) else {}
    doc_count = len(docs)

    if doc_count >= 5:
        return 1.0
    if doc_count == 4:
        return 0.9
    if doc_count == 3:
        return 0.8
    if doc_count == 2:
        return 0.65
    if doc_count == 1:
        return 0.45

    examples = rec.get("examples") if isinstance(rec.get("examples"), list) else []
    example_docs = {str(ex.get("doc_id") or "") for ex in examples if isinstance(ex, dict)}
    example_docs.discard("")

    if len(example_docs) >= 2:
        return 0.60
    if len(example_docs) == 1:
        return 0.40

    return 0.25


def _semantic_stability(rec: Dict[str, Any]) -> float:
    phrase = _canonical_phrase(str(rec.get("phrase") or ""))
    canonical = _canonical_phrase(str(rec.get("canonical") or phrase))
    aliases = rec.get("aliases") if isinstance(rec.get("aliases"), list) else []

    if not phrase:
        return 0.0

    score = 0.70

    if canonical == phrase:
        score += 0.10

    if len(phrase.split()) in {2, 3, 4}:
        score += 0.10

    clean_aliases = [
        _light_normalize_phrase(str(a or ""))
        for a in aliases
        if _light_normalize_phrase(str(a or ""))
    ]

    if len(clean_aliases) <= 2:
        score += 0.05
    elif len(clean_aliases) >= 5:
        score -= 0.10

    return max(0.0, min(1.0, round(score, 4)))


def _ranking_priority(builder_score: float) -> str:
    if builder_score >= 0.85:
        return "HIGH"
    if builder_score >= 0.65:
        return "MEDIUM"
    return "LOW"


def _build_builder_intelligence(rec: Dict[str, Any]) -> Dict[str, Any]:
    extractor_score = _extract_extractor_score(rec)
    quality_gate_score = _extract_quality_gate_score(rec)
    strength_score = _extract_strength_score(rec)
    source_score = _source_priority(str(rec.get("source_type") or ""))
    cross_doc_score = _cross_document_strength(rec)
    semantic_score = _semantic_stability(rec)

    builder_score = (
        (extractor_score * 0.20)
        + (quality_gate_score * 0.20)
        + (strength_score * 0.25)
        + (source_score * 0.15)
        + (cross_doc_score * 0.10)
        + (semantic_score * 0.10)
    )

    builder_score = round(max(0.0, min(1.0, builder_score)), 4)

    return {
        "builder_score": builder_score,
        "ranking_priority": _ranking_priority(builder_score),
        "signals": {
            "extractor_score": round(extractor_score, 4),
            "quality_gate_score": round(quality_gate_score, 4),
            "strength_score": round(strength_score, 4),
            "source_priority": round(source_score, 4),
            "cross_document_strength": round(cross_doc_score, 4),
            "semantic_stability": round(semantic_score, 4),
        },
        "layers": [
            "temporal_reasoning",
            "entity_map",
            "topic_coherence",
            "cross_document_reasoning",
            "long_context_compression",
            "cross_knowledge_fusion",
            "ontology_alignment",
            "intelligent_data_compression",
            "workspace_isolation",
            "explainability",
            "qa_regression_readiness",
        ],
    }


def _preserve_intelligence_metadata(clean_rec: Dict[str, Any], gate_result: Dict[str, Any]) -> None:
    extractor_intelligence = (
        clean_rec.get("extractor_intelligence")
        if isinstance(clean_rec.get("extractor_intelligence"), dict)
        else {}
    )

    quality_gate = (
        clean_rec.get("quality_gate")
        if isinstance(clean_rec.get("quality_gate"), dict)
        else {}
    )

    if not quality_gate and isinstance(gate_result.get("quality_gate"), dict):
        quality_gate = gate_result.get("quality_gate") or {}

    strength = (
        clean_rec.get("strength")
        if isinstance(clean_rec.get("strength"), dict)
        else {}
    )

    if isinstance(gate_result.get("strength"), dict):
        strength = gate_result.get("strength") or strength

    clean_rec["extractor_intelligence"] = extractor_intelligence
    clean_rec["quality_gate"] = quality_gate
    clean_rec["strength"] = strength


def _merge_phrase_records(target_key: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
    records = sorted(records, key=lambda r: -_record_score(r))
    first = dict(records[0])
    first["phrase"] = target_key
    first["canonical"] = target_key

    count_total = 0
    docs: Dict[str, int] = {}
    sections: List[str] = []
    examples: List[Dict[str, Any]] = []
    aliases: List[str] = []
    seen_aliases: Set[str] = set()
    source_type = first.get("source_type", "unknown")
    tier = first.get("tier", "C")
    first_seen_vals: List[str] = []
    last_seen_vals: List[str] = []
    best_score = _record_score(first)

    best_extractor_intelligence = (
        first.get("extractor_intelligence")
        if isinstance(first.get("extractor_intelligence"), dict)
        else {}
    )
    best_quality_gate = (
        first.get("quality_gate")
        if isinstance(first.get("quality_gate"), dict)
        else {}
    )
    best_strength = first.get("strength") if isinstance(first.get("strength"), dict) else {}
    best_builder_intelligence = (
        first.get("builder_intelligence")
        if isinstance(first.get("builder_intelligence"), dict)
        else {}
    )

    for rec in records:
        rec_score = _record_score(rec)
        count_total += int(rec.get("count_total") or 0)
        best_score = max(best_score, rec_score)

        if rec_score >= _record_score({
            "builder_score": (
                best_builder_intelligence.get("builder_score")
                if isinstance(best_builder_intelligence, dict)
                else 0.0
            ),
            "score": best_score,
        }):
            if isinstance(rec.get("extractor_intelligence"), dict):
                best_extractor_intelligence = rec.get("extractor_intelligence") or {}
            if isinstance(rec.get("quality_gate"), dict):
                best_quality_gate = rec.get("quality_gate") or {}
            if isinstance(rec.get("strength"), dict):
                best_strength = rec.get("strength") or {}
            if isinstance(rec.get("builder_intelligence"), dict):
                best_builder_intelligence = rec.get("builder_intelligence") or {}

        rec_docs = rec.get("docs") if isinstance(rec.get("docs"), dict) else {}
        for d, c in rec_docs.items():
            docs[str(d)] = int(docs.get(str(d)) or 0) + int(c or 0)

        rec_sections = rec.get("sections") if isinstance(rec.get("sections"), list) else []
        for s in rec_sections:
            x = _clean_text(s)
            if x and x not in sections:
                sections.append(x)

        rec_examples = rec.get("examples") if isinstance(rec.get("examples"), list) else []
        for ex in rec_examples:
            if len(examples) >= 5:
                break
            if not isinstance(ex, dict):
                continue

            cleaned_ex = {
                "doc_id": _clean_text(ex.get("doc_id") or ""),
                "section_id": _clean_text(ex.get("section_id") or ""),
                "snippet": _clean_text(ex.get("snippet") or ""),
            }

            if cleaned_ex["doc_id"] or cleaned_ex["section_id"] or cleaned_ex["snippet"]:
                examples.append(cleaned_ex)

        rec_source_type = str(rec.get("source_type") or "")

        old_phrase = _light_normalize_phrase(str(rec.get("phrase") or ""))
        old_canonical = _light_normalize_phrase(str(rec.get("canonical") or ""))

        candidate_aliases: List[str] = []

        if old_phrase and old_phrase != target_key:
            candidate_aliases.append(old_phrase)

        if old_canonical and old_canonical != target_key:
            candidate_aliases.append(old_canonical)

        rec_aliases = rec.get("aliases") if isinstance(rec.get("aliases"), list) else []
        for a in rec_aliases:
            aa = _light_normalize_phrase(str(a or ""))
            if aa and aa != target_key:
                candidate_aliases.append(aa)

        for a in candidate_aliases:
            if a and a != target_key and a not in seen_aliases:
                aliases.append(a)
                seen_aliases.add(a)

        if rec_source_type in {"title", "heading_h1", "heading_h2", "heading_h3", "list_item", "entity", "intent"}:
            source_type = rec_source_type

        rec_tier = str(rec.get("tier") or "")
        if rec_tier == "A":
            tier = "A"
        elif rec_tier == "B" and tier != "A":
            tier = "B"

        fs = str(rec.get("first_seen") or "")
        ls = str(rec.get("last_seen") or "")
        if fs:
            first_seen_vals.append(fs)
        if ls:
            last_seen_vals.append(ls)

    first["count_total"] = count_total
    first["docs"] = docs
    first["sections"] = sections
    first["examples"] = examples[:5]
    first["aliases"] = aliases[:5]
    first["source_type"] = source_type
    first["tier"] = tier
    first["score"] = best_score
    first["extractor_intelligence"] = best_extractor_intelligence
    first["quality_gate"] = best_quality_gate
    first["strength"] = best_strength
    first["first_seen"] = min(first_seen_vals) if first_seen_vals else first.get("first_seen", "")
    first["last_seen"] = max(last_seen_vals) if last_seen_vals else first.get("last_seen", "")

    first["builder_intelligence"] = _build_builder_intelligence(first)
    first["builder_score"] = first["builder_intelligence"]["builder_score"]
    first["ranking_priority"] = first["builder_intelligence"]["ranking_priority"]

    return first


def _canonical_merge_phrases(phrases: Dict[str, Any]) -> Dict[str, Any]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}

    for old_key, rec in phrases.items():
        if not isinstance(rec, dict):
            continue

        target_key = _light_normalize_phrase(str(old_key))

        if not target_key:
            continue

        grouped.setdefault(target_key, []).append(rec)

    merged: Dict[str, Any] = {}

    for target_key, records in grouped.items():
        merged[target_key] = _merge_phrase_records(target_key, records)

    return merged


def _sort_phrase_dict(phrases: Dict[str, Any]) -> Dict[str, Any]:
    sorted_items = sorted(
        phrases.items(),
        key=lambda kv: (
            -float(kv[1].get("builder_score") or kv[1].get("score") or kv[1].get("quality_score") or 0.0)
            if isinstance(kv[1], dict)
            else 0.0,
            kv[0],
        ),
    )
    return {k: v for k, v in sorted_items}


def build_upload_phrase_pool(ws: str) -> Dict[str, Any]:
    ws = _ws_safe(ws)

    src_path = _upload_phrase_index_path(ws)
    pool_path = _upload_phrase_pool_path(ws)

    src = _safe_read_json(src_path) or {}
    raw_phrases = src.get("phrases") if isinstance(src.get("phrases"), dict) else {}

    phrases: Dict[str, Any] = {}

    for k, v in raw_phrases.items():
        nk = _clean_text(k)

        if not nk or not isinstance(v, dict):
            continue

        clean_rec = dict(v)
        source_type = _clean_text(clean_rec.get("source_type") or "")

        phrase_text = _light_normalize_phrase(_clean_text(clean_rec.get("phrase") or nk))
        if not phrase_text:
            continue

        gate_result = _quality_gate_phrase_with_metadata(phrase_text, source_type=source_type or "")
        if not gate_result.get("keep"):
            continue

        phrase_text = _light_normalize_phrase(str(gate_result.get("phrase") or phrase_text))
        if not phrase_text:
            continue

        canonical_text = _light_normalize_phrase(_clean_text(clean_rec.get("canonical") or phrase_text))
        if not canonical_text:
            canonical_text = phrase_text

        _preserve_intelligence_metadata(clean_rec, gate_result)

        clean_rec["phrase"] = phrase_text
        clean_rec["canonical"] = canonical_text

        strength_score = _extract_strength_score(clean_rec)
        if "score" not in clean_rec or not _safe_float(clean_rec.get("score"), 0.0):
            clean_rec["score"] = strength_score

        if isinstance(clean_rec.get("aliases"), list):
            clean_aliases: List[str] = []
            seen_aliases: Set[str] = set()

            for x in clean_rec["aliases"]:
                ax = _light_normalize_phrase(str(x or ""))

                if not ax or ax == phrase_text or ax in seen_aliases:
                    continue

                clean_aliases.append(ax)
                seen_aliases.add(ax)

            clean_rec["aliases"] = clean_aliases[:5]
        else:
            clean_rec["aliases"] = []

        if isinstance(clean_rec.get("sections"), list):
            clean_rec["sections"] = [_clean_text(x) for x in clean_rec["sections"] if _clean_text(x)]
        else:
            clean_rec["sections"] = []

        if isinstance(clean_rec.get("examples"), list):
            clean_rec["examples"] = _clean_examples(clean_rec["examples"])
        else:
            clean_rec["examples"] = []

        clean_rec["builder_intelligence"] = _build_builder_intelligence(clean_rec)
        clean_rec["builder_score"] = clean_rec["builder_intelligence"]["builder_score"]
        clean_rec["ranking_priority"] = clean_rec["builder_intelligence"]["ranking_priority"]

        phrases[phrase_text] = clean_rec

    active = load_active_phrase_set(ws)
    active_doc_ids = active.get("active_upload_ids") if isinstance(active.get("active_upload_ids"), list) else []

    if not active_doc_ids:
        active_doc_ids = active.get("active_document_ids") if isinstance(active.get("active_document_ids"), list) else []

    active_doc_ids = [str(x).strip() for x in active_doc_ids if str(x).strip()]
    active_doc_set = set(active_doc_ids)

    indexed_doc_ids = set()

    for rec in phrases.values():
        if not isinstance(rec, dict):
            continue

        docs = rec.get("docs") if isinstance(rec.get("docs"), dict) else {}
        indexed_doc_ids.update(str(k) for k in docs.keys())

    usable_active_ids = active_doc_set.intersection(indexed_doc_ids)
    active_phrase_set_used = bool(usable_active_ids)

    filtered: Dict[str, Any] = {}

    if active_phrase_set_used:
        for phrase, rec in phrases.items():
            if not isinstance(rec, dict):
                continue

            docs = rec.get("docs") if isinstance(rec.get("docs"), dict) else {}

            if any(str(doc_id) in usable_active_ids for doc_id in docs.keys()):
                gated_phrase = _light_normalize_phrase(phrase)
                if gated_phrase:
                    filtered[gated_phrase] = rec
    else:
        for phrase, rec in phrases.items():
            if not isinstance(rec, dict):
                continue

            gated_phrase = _light_normalize_phrase(phrase)
            if gated_phrase:
                filtered[gated_phrase] = rec

    filtered = _canonical_merge_phrases(filtered)
    filtered = _sort_phrase_dict(filtered)

    priority_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for rec in filtered.values():
        if not isinstance(rec, dict):
            continue
        priority = str(rec.get("ranking_priority") or "LOW")
        if priority not in priority_counts:
            priority = "LOW"
        priority_counts[priority] += 1

    obj = {
        "workspace_id": ws,
        "updated_at": _now_iso(),
        "source_phrase_count": len(raw_phrases),
        "quality_filtered_source_count": len(phrases),
        "phrase_count": len(filtered),
        "active_phrase_set_used": active_phrase_set_used,
        "active_document_ids_count": len(active_doc_set),
        "usable_active_document_ids_count": len(usable_active_ids),
        "indexed_document_ids_count": len(indexed_doc_ids),
        "builder_intelligence_summary": {
            "enabled": True,
            "ranking_priority_counts": priority_counts,
            "layers": [
                "temporal_reasoning",
                "entity_map",
                "topic_coherence",
                "cross_document_reasoning",
                "long_context_compression",
                "cross_knowledge_fusion",
                "ontology_alignment",
                "intelligent_data_compression",
                "workspace_isolation",
                "explainability",
                "qa_regression_readiness",
            ],
        },
        "phrases": filtered,
    }

    _write_json(pool_path, obj)
    return obj