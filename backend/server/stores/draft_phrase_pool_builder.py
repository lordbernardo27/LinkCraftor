# backend/server/stores/draft_phrase_pool_builder.py
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.server.stores.active_phrase_set_store import load_active_phrase_set
from backend.server.stores.draft_phrase_selector import select_draft_phrases

def _data_dir() -> Path:
    here = Path(__file__).resolve()
    server_dir = here.parents[1]  # .../backend/server
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


def _draft_topics_path(ws: str) -> Path:
    return _data_dir() / f"draft_topics_{_ws_safe(ws)}.json"


def _draft_phrase_index_path(ws: str) -> Path:
    return _data_dir() / f"draft_phrase_index_{_ws_safe(ws)}.json"


def _draft_phrase_pool_path(ws: str) -> Path:
    return _data_dir() / "phrase_pools" / "draft" / f"draft_phrase_pool_{_ws_safe(ws)}.json"


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _clean_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()


def _strip_drafts_prefix(title: str) -> str:
    s = _clean_spaces(title)
    if s.lower().startswith("drafts "):
        s = s[7:].strip()
    return s


def _slug_to_text(slug: str) -> str:
    s = str(slug or "").strip().strip("/")
    s = s.replace("-", " ")
    s = s.replace("_", " ")
    return _clean_spaces(s)


def _tokenize(text: str) -> List[str]:
    return [t for t in re.findall(r"[A-Za-z0-9]+", (text or "").lower()) if t]


STOPWORDS = {
    "and", "or", "the", "a", "an", "of", "to", "in", "on", "for", "with",
    "by", "at", "from", "as", "is", "are", "was", "were", "be", "can",
    "during"
}


def _is_meaningful_phrase(tokens: List[str]) -> bool:
    if len(tokens) < 2 or len(tokens) > 8:
        return False
    if tokens[0] in STOPWORDS or tokens[-1] in STOPWORDS:
        return False

    meaningful = [t for t in tokens if t not in STOPWORDS]
    if len(meaningful) < 2:
        return False

    return True


def _extract_phrases_from_text(text: str) -> List[str]:
    tokens = _tokenize(text)
    if len(tokens) < 2:
        return []

    out: List[str] = []
    seen = set()

    if _is_meaningful_phrase(tokens):
        full = " ".join(tokens)
        seen.add(full)
        out.append(full)

    n = len(tokens)
    for size in range(2, min(8, n) + 1):
        for i in range(0, n - size + 1):
            gram = tokens[i:i + size]
            if not _is_meaningful_phrase(gram):
                continue
            phrase = " ".join(gram)
            if phrase in seen:
                continue
            seen.add(phrase)
            out.append(phrase)

    return out


def build_draft_phrase_index(workspace_id: str) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)
    topics_path = _draft_topics_path(ws)
    out_path = _draft_phrase_index_path(ws)

    active_obj = load_active_phrase_set(ws)
    active_draft_ids = [
        str(x).strip()
        for x in (active_obj.get("active_draft_ids") or [])
        if str(x).strip()
    ]
    active_draft_id_set = set(active_draft_ids)

    if not topics_path.exists():
        raise FileNotFoundError(f"Missing draft topics file: {topics_path}")

    raw = _safe_read_json(topics_path)
    if not isinstance(raw, list):
        raw = []

    phrases: Dict[str, Dict[str, Any]] = {}

    topics_seen = 0
    topics_used = 0

    for item in raw:
        if not isinstance(item, dict):
            continue

        topics_seen += 1

        working_title = _strip_drafts_prefix(item.get("working_title") or item.get("title") or "")
        aliases = item.get("aliases") if isinstance(item.get("aliases"), list) else []
        aliases = [_clean_spaces(a) for a in aliases if _clean_spaces(a)]
        planned_slug_raw = str(item.get("planned_slug") or "").strip()
        planned_slug = planned_slug_raw
        item_topic_id = str(item.get("topic_id") or item.get("id") or "").strip()
        item_url = str(item.get("planned_url") or "").strip()
        summary = _clean_spaces(
            item.get("summary")
            or item.get("description")
            or item.get("notes")
            or item.get("excerpt")
            or ""
        )

        if active_draft_id_set and item_topic_id not in active_draft_id_set:
            continue

        item_added_any = False

        selected_obj = select_draft_phrases(
            workspace_id=ws,
            topic_id=item_topic_id or "draft_topic",
            title=working_title,
            slug=planned_slug,
            planned_url=item_url,
            summary=summary,
            aliases=aliases,
        )

        extracted_items = selected_obj.get("phrases") or []
        for phrase_obj in extracted_items:
            if not isinstance(phrase_obj, dict):
                continue

            phrase = _clean_spaces(phrase_obj.get("phrase") or "")
            if not phrase:
                continue

            rec = phrases.get(phrase)
            if rec is None:
                phrases[phrase] = {
                    "phrase": phrase,
                    "source": "draft_topics",
                    "source_type": phrase_obj.get("source_type") or "unknown",
                    "score": int(phrase_obj.get("score") or 0),
                    "vertical": selected_obj.get("vertical") or "generic",
                    "topic_ids": [item_topic_id] if item_topic_id else [],
                    "planned_urls": [item_url] if item_url else [],
                    "occurrences": 1,
                    "section_ids": [phrase_obj.get("section_id")] if phrase_obj.get("section_id") else [],
                    "snippets": [phrase_obj.get("snippet")] if phrase_obj.get("snippet") else [],
                }
            else:
                rec["occurrences"] = int(rec.get("occurrences") or 0) + 1

                existing_score = int(rec.get("score") or 0)
                new_score = int(phrase_obj.get("score") or 0)
                if new_score > existing_score:
                    rec["score"] = new_score
                    rec["source_type"] = phrase_obj.get("source_type") or rec.get("source_type") or "unknown"

                if item_topic_id and item_topic_id not in rec.get("topic_ids", []):
                    rec.setdefault("topic_ids", []).append(item_topic_id)

                if item_url and item_url not in rec.get("planned_urls", []):
                    rec.setdefault("planned_urls", []).append(item_url)

                section_id = phrase_obj.get("section_id")
                if section_id and section_id not in rec.get("section_ids", []):
                    rec.setdefault("section_ids", []).append(section_id)

                snippet = phrase_obj.get("snippet")
                if snippet and snippet not in rec.get("snippets", []):
                    rec.setdefault("snippets", []).append(snippet)

            item_added_any = True


        if item_added_any:
            topics_used += 1

    out_obj = {
        "workspace_id": ws,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "topic_count": topics_seen,
        "topics_used": topics_used,
        "phrase_count": len(phrases),
        "active_phrase_set_used": bool(active_draft_id_set),
        "active_draft_ids_count": len(active_draft_ids),
        "phrases": phrases,
    }

    out_path.write_text(json.dumps(out_obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_obj


def build_draft_phrase_pool(workspace_id: str) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)
    src_path = _draft_phrase_index_path(ws)

    if not src_path.exists():
        raise FileNotFoundError(f"Missing draft phrase index file: {src_path}")

    raw = _safe_read_json(src_path)
    if not isinstance(raw, dict):
        raw = {}

    source_phrases = raw.get("phrases") if isinstance(raw.get("phrases"), dict) else {}

    active_obj = load_active_phrase_set(ws)
    active_draft_ids = [
        str(x).strip()
        for x in (active_obj.get("active_draft_ids") or [])
        if str(x).strip()
    ]
    active_draft_id_set = set(active_draft_ids)

    phrases: Dict[str, Dict[str, Any]] = {}
    source_phrase_count = 0
    kept_phrase_count = 0

    for phrase, rec in source_phrases.items():
        if not isinstance(rec, dict):
            continue

        source_phrase_count += 1

        topic_ids = rec.get("topic_ids") if isinstance(rec.get("topic_ids"), list) else []

        if active_draft_id_set:
            matched_ids = [t for t in topic_ids if t in active_draft_id_set]
            if not matched_ids:
                continue

        phrases[str(phrase)] = rec
        kept_phrase_count += 1

    out_obj = {
        "workspace_id": ws,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source_phrase_count": source_phrase_count,
        "phrase_count": kept_phrase_count,
        "active_phrase_set_used": bool(active_draft_id_set),
        "active_draft_ids_count": len(active_draft_ids),
        "phrases": phrases,
    }

    out_path = _draft_phrase_pool_path(ws)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out_obj, ensure_ascii=False, indent=2), encoding="utf-8")

    return out_obj