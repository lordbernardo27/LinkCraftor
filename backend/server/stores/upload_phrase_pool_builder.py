# backend/server/stores/upload_phrase_pool_builder.py
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

from backend.server.stores.active_phrase_set_store import load_active_phrase_set
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


def _clean_aliases(v: Any) -> List[str]:
    if not isinstance(v, list):
        return []
    out: List[str] = []
    seen: Set[str] = set()
    for item in v:
        x = _clean_text(item)
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _clean_examples(v: Any) -> List[Dict[str, str]]:
    if not isinstance(v, list):
        return []
    out: List[Dict[str, str]] = []
    for ex in v:
        if not isinstance(ex, dict):
            continue
        out.append(
            {
                "doc_id": _clean_text(ex.get("doc_id") or ""),
                "section_id": _clean_text(ex.get("section_id") or ""),
                "snippet": _clean_text(ex.get("snippet") or ""),
            }
        )
    return out


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
        r"^many women ask\s+",
        r"^women often ask\s+",
        r"^doctors are often asked\s+",
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


def _merge_phrase_records(target_key: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
    first = dict(records[0])
    first["phrase"] = target_key
    first["canonical"] = target_key

    count_total = 0
    docs: Dict[str, int] = {}
    sections: List[str] = []
    examples: List[Dict[str, Any]] = []
    aliases: List[str] = []
    seen_aliases: Set[str] = set()
    source_type = first.get("source_type", "sentence")
    tier = first.get("tier", "C")
    first_seen_vals: List[str] = []
    last_seen_vals: List[str] = []

    for rec in records:
        count_total += int(rec.get("count_total") or 0)

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
            clean_ex = {
                "doc_id": _clean_text(ex.get("doc_id") or ""),
                "section_id": _clean_text(ex.get("section_id") or ""),
                "snippet": _clean_text(ex.get("snippet") or ""),
            }
            examples.append(clean_ex)

        candidate_aliases: List[str] = []
        old_phrase = _canonical_phrase(str(rec.get("phrase") or ""))
        old_canonical = _canonical_phrase(str(rec.get("canonical") or ""))
        if old_phrase and old_phrase != target_key:
            candidate_aliases.append(old_phrase)
        if old_canonical and old_canonical != target_key:
            candidate_aliases.append(old_canonical)

        rec_aliases = rec.get("aliases") if isinstance(rec.get("aliases"), list) else []
        candidate_aliases.extend([_canonical_phrase(a) for a in rec_aliases])

        for a in candidate_aliases:
            if a and a != target_key and a not in seen_aliases:
                aliases.append(a)
                seen_aliases.add(a)

        rec_source_type = str(rec.get("source_type") or "")
        if rec_source_type in {"title", "heading_h1", "heading_h2", "heading_h3", "list_item"}:
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
    first["examples"] = examples
    first["aliases"] = aliases[:5]
    first["source_type"] = source_type
    first["tier"] = tier
    first["first_seen"] = min(first_seen_vals) if first_seen_vals else first.get("first_seen", "")
    first["last_seen"] = max(last_seen_vals) if last_seen_vals else first.get("last_seen", "")
    return first


def _canonical_merge_phrases(phrases: Dict[str, Any]) -> Dict[str, Any]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}

    for old_key, rec in phrases.items():
        if not isinstance(rec, dict):
            continue
        target_key = _extract_canonical_core_phrase(old_key) or _canonical_phrase(old_key)
        if not target_key:
            continue
        grouped.setdefault(target_key, []).append(rec)

    merged: Dict[str, Any] = {}
    for target_key, records in grouped.items():
        merged[target_key] = _merge_phrase_records(target_key, records)

    return merged


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

        if "phrase" in clean_rec:
            clean_rec["phrase"] = _clean_text(clean_rec.get("phrase"))

        if "canonical" in clean_rec:
            clean_rec["canonical"] = _clean_text(clean_rec.get("canonical"))

        if isinstance(clean_rec.get("aliases"), list):
            clean_rec["aliases"] = [_clean_text(x) for x in clean_rec["aliases"]]

        if isinstance(clean_rec.get("sections"), list):
            clean_rec["sections"] = [_clean_text(x) for x in clean_rec["sections"]]

        if isinstance(clean_rec.get("examples"), list):
            clean_rec["examples"] = _clean_examples(clean_rec["examples"])

        phrases[nk] = clean_rec

    active = load_active_phrase_set(ws)
    active_doc_ids = active.get("active_upload_ids") if isinstance(active.get("active_upload_ids"), list) else []
    if not active_doc_ids:
        active_doc_ids = active.get("active_document_ids") if isinstance(active.get("active_document_ids"), list) else []

    active_doc_ids = [str(x).strip() for x in active_doc_ids if str(x).strip()]
    active_doc_set = set(active_doc_ids)

    active_phrase_set_used = bool(active_doc_set)

    filtered: Dict[str, Any] = {}
    if active_phrase_set_used:
        for phrase, rec in phrases.items():
            if not isinstance(rec, dict):
                continue
            docs = rec.get("docs") if isinstance(rec.get("docs"), dict) else {}
            if any(doc_id in active_doc_set for doc_id in docs.keys()):
                filtered[_clean_text(phrase)] = rec
    else:
        filtered = {_clean_text(k): v for k, v in phrases.items()}

    filtered = _canonical_merge_phrases(filtered)

    obj = {
        "workspace_id": ws,
        "updated_at": _now_iso(),
        "source_phrase_count": len(phrases),
        "phrase_count": len(filtered),
        "active_phrase_set_used": active_phrase_set_used,
        "active_document_ids_count": len(active_doc_set),
        "phrases": filtered,
    }

    _write_json(pool_path, obj)
    return obj