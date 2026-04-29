from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.server.stores.active_phrase_set_store import load_active_phrase_set
from backend.server.stores.live_phrase_selector import select_live_phrases
from backend.server.utils.text_normalization import fix_mojibake_text


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    server_dir = here.parents[1]
    return server_dir / "data"


def _ws_safe(ws: str) -> str:
    raw = (ws or "default").strip()
    if not raw:
        return "default"
    if raw.lower() == "default":
        return "default"
    if raw.lower().startswith("ws_"):
        return raw

    s = raw.lower()
    s = s.replace(".", "_").replace("-", "_").replace(" ", "_")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        s = "workspace"

    return f"ws_{s}"[:80]


def _site_phrase_index_path(ws: str) -> Path:
    return _data_dir() / f"site_phrase_index_{_ws_safe(ws)}.json"


def _live_domain_phrase_pool_path(ws: str) -> Path:
    return _data_dir() / "phrase_pools" / "live_domain" / f"live_domain_phrase_pool_{_ws_safe(ws)}.json"


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _clean_text(s: Any) -> str:
    s = fix_mojibake_text(str(s or ""))
    return re.sub(r"\s+", " ", s).strip()


def _canonical_phrase(s: Any) -> str:
    s = _clean_text(s).lower()
    s = s.replace("_", " ").replace("-", " ")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _clean_aliases(v: Any) -> List[str]:
    if not isinstance(v, list):
        return []

    out: List[str] = []
    seen = set()

    for item in v:
        x = _clean_text(item)
        if x and x not in seen:
            seen.add(x)
            out.append(x)

    return out


def _quality_gate_phrase(phrase: str, rec: Dict[str, Any]) -> bool:
    p = _canonical_phrase(phrase)
    if not p:
        return False

    toks = p.split()

    if len(toks) < 2 or len(toks) > 10:
        return False

    if len(set(toks)) < len(toks):
        return False

    weak = {
        "the", "and", "for", "with", "from", "after",
        "before", "that", "this", "those", "these"
    }

    if toks[0] in weak:
        return False

    if toks[-1] in weak:
        return False

    score = int(rec.get("score", 0))
    if score <= 0:
        return False

    return True


def _rec_to_selector_entry(phrase: str, rec: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "phrase": _clean_text(phrase),
        "norm": _canonical_phrase(rec.get("norm") or phrase or ""),
        "type": _clean_text(rec.get("type") or ""),
        "bucket": _clean_text(rec.get("bucket") or ""),
        "confidence": float(rec.get("confidence") or 0.0),
        "aliases": _clean_aliases(rec.get("aliases")),
        "source_url": _clean_text(rec.get("source_url") or ""),
        "section_id": _clean_text(rec.get("section_id") or ""),
        "snippet": _clean_text(rec.get("snippet") or rec.get("phrase") or phrase or ""),
    }


def build_live_domain_phrase_pool(workspace_id: str) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)
    src_path = _site_phrase_index_path(ws)
    out_path = _live_domain_phrase_pool_path(ws)

    if not src_path.exists():
        raise FileNotFoundError(f"Missing live-domain phrase index file: {src_path}")

    raw = _safe_read_json(src_path)
    if not isinstance(raw, dict):
        raw = {}

    source_phrases = raw.get("phrases")
    if not isinstance(source_phrases, dict):
        source_phrases = {}

    active_obj = load_active_phrase_set(ws)

    active_live_domain_urls = [
        _clean_text(x)
        for x in (active_obj.get("active_live_domain_urls") or [])
        if _clean_text(x)
    ]
    active_live_domain_url_set = set(active_live_domain_urls)

    source_phrase_count = 0
    eligible_phrase_count = 0

    entries_by_url: Dict[str, List[Dict[str, Any]]] = {}
    record_by_phrase_and_url: Dict[tuple[str, str], Dict[str, Any]] = {}

    for phrase, rec in source_phrases.items():
        if not isinstance(rec, dict):
            continue

        source_phrase_count += 1

        source_url = _clean_text(rec.get("source_url") or "")
        if not source_url:
            continue

        if active_live_domain_url_set and source_url not in active_live_domain_url_set:
            continue

        eligible_phrase_count += 1

        entry = _rec_to_selector_entry(str(phrase), rec)
        entries_by_url.setdefault(source_url, []).append(entry)

        key = (
            _canonical_phrase(entry.get("norm") or phrase),
            source_url
        )
        record_by_phrase_and_url[key] = rec

    phrases: Dict[str, Dict[str, Any]] = {}

    for source_url, entries in entries_by_url.items():
        selected_obj = select_live_phrases(
            workspace_id=ws,
            source_url=source_url,
            entries=entries,
            page_text="",
        )

        for item in selected_obj.get("phrases") or []:
            norm = _canonical_phrase(item.get("norm") or item.get("phrase") or "")
            if not norm:
                continue

            original = record_by_phrase_and_url.get((norm, source_url), {})

            merged = dict(original) if isinstance(original, dict) else {}

            merged["phrase"] = _clean_text(item.get("phrase") or norm)
            merged["norm"] = norm
            merged["source_url"] = source_url
            merged["type"] = _clean_text(item.get("type") or merged.get("type") or "unknown")
            merged["bucket"] = _clean_text(item.get("bucket") or merged.get("bucket") or "unknown")
            merged["confidence"] = (
                item.get("confidence")
                if item.get("confidence") is not None
                else merged.get("confidence", 0.0)
            )
            merged["score"] = int(item.get("score", merged.get("score", 0)))
            merged["aliases"] = _clean_aliases(item.get("aliases") or merged.get("aliases") or [])
            merged["section_id"] = _clean_text(item.get("section_id") or merged.get("section_id") or "")
            merged["snippet"] = _clean_text(
                item.get("snippet")
                or merged.get("snippet")
                or merged.get("phrase")
                or norm
            )
            merged["vertical"] = _clean_text(
                item.get("vertical")
                or merged.get("vertical")
                or ""
            )

            if not _quality_gate_phrase(norm, merged):
                continue

            existing = phrases.get(norm)

            if existing is None:
                phrases[norm] = merged
            else:
                if int(merged["score"]) > int(existing.get("score", 0)):
                    phrases[norm] = merged

    sorted_items = sorted(
        phrases.items(),
        key=lambda kv: (-int(kv[1].get("score", 0)), kv[0])
    )

    final_phrases = {k: v for k, v in sorted_items}

    out_obj = {
        "workspace_id": ws,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source_phrase_count": source_phrase_count,
        "eligible_phrase_count": eligible_phrase_count,
        "phrase_count": len(final_phrases),
        "active_phrase_set_used": bool(active_live_domain_url_set),
        "active_live_domain_urls_count": len(active_live_domain_urls),
        "phrases": final_phrases,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(out_obj, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return out_obj