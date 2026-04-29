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


def _quality_gate_phrase(phrase: str, source_type: str = "") -> str:
    phrase = _extract_canonical_core_phrase(phrase) or _canonical_phrase(phrase)

    if not phrase:
        return ""

    guard = candidate_window_guard(phrase, source_type=source_type or "")
    if not isinstance(guard, dict) or not guard.get("keep"):
        return ""

    guarded_phrase = _canonical_phrase(str(guard.get("phrase") or phrase))

    scored = score_phrase_strength(
        phrase=guarded_phrase,
        source_type=source_type or "",
    )

    if not isinstance(scored, dict) or not scored.get("keep"):
        return ""

    return _canonical_phrase(str(scored.get("phrase") or guarded_phrase))


def _record_score(rec: Dict[str, Any]) -> float:
    for key in ("score", "quality_score", "strength_score"):
        try:
            val = float(rec.get(key) or 0.0)
            if val:
                return val
        except Exception:
            continue
    return 0.0


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

    for rec in records:
        count_total += int(rec.get("count_total") or 0)
        best_score = max(best_score, _record_score(rec))

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

        candidate_aliases: List[str] = []
        rec_source_type = str(rec.get("source_type") or "")

        old_phrase = _quality_gate_phrase(str(rec.get("phrase") or ""), rec_source_type)
        old_canonical = _quality_gate_phrase(str(rec.get("canonical") or ""), rec_source_type)

        if old_phrase and old_phrase != target_key:
            candidate_aliases.append(old_phrase)

        if old_canonical and old_canonical != target_key:
            candidate_aliases.append(old_canonical)

        rec_aliases = rec.get("aliases") if isinstance(rec.get("aliases"), list) else []
        for a in rec_aliases:
            aa = _quality_gate_phrase(str(a or ""), rec_source_type)
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
    first["first_seen"] = min(first_seen_vals) if first_seen_vals else first.get("first_seen", "")
    first["last_seen"] = max(last_seen_vals) if last_seen_vals else first.get("last_seen", "")

    return first


def _canonical_merge_phrases(phrases: Dict[str, Any]) -> Dict[str, Any]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}

    for old_key, rec in phrases.items():
        if not isinstance(rec, dict):
            continue

        source_type = _clean_text(rec.get("source_type") or "")
        target_key = _quality_gate_phrase(old_key, source_type)

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
            -float(kv[1].get("score") or kv[1].get("quality_score") or 0.0)
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

        phrase_text = _clean_text(clean_rec.get("phrase") or nk)
        canonical_text = _clean_text(clean_rec.get("canonical") or phrase_text)

        phrase_text = _extract_canonical_core_phrase(phrase_text) or _canonical_phrase(phrase_text)
        if not phrase_text:
            continue

        canonical_text = _extract_canonical_core_phrase(canonical_text) or _canonical_phrase(canonical_text)
        if not canonical_text:
            canonical_text = phrase_text

        scored_check = score_phrase_strength(
           phrase=phrase_text,
           source_type=source_type or "",
)

        clean_rec["phrase"] = phrase_text
        clean_rec["canonical"] = canonical_text

        if "score" not in clean_rec:
            clean_rec["score"] = (
                float(scored_check.get("score") or 0.0)
                if isinstance(scored_check, dict)
                else 0.0
            )

        if isinstance(clean_rec.get("aliases"), list):
            clean_aliases: List[str] = []
            seen_aliases: Set[str] = set()

            for x in clean_rec["aliases"]:
                ax = _extract_canonical_core_phrase(str(x or "")) or _canonical_phrase(str(x or ""))

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
                gated_phrase = _extract_canonical_core_phrase(phrase) or _canonical_phrase(phrase)
                if gated_phrase:
                    filtered[gated_phrase] = rec
    else:
        for phrase, rec in phrases.items():
            if not isinstance(rec, dict):
                continue

            gated_phrase = _extract_canonical_core_phrase(phrase) or _canonical_phrase(phrase)
            if gated_phrase:
                filtered[gated_phrase] = rec

    filtered = _canonical_merge_phrases(filtered)
    filtered = _sort_phrase_dict(filtered)

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
        "phrases": filtered,
    }

    _write_json(pool_path, obj)
    return obj