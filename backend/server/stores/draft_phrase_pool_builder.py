# backend/server/stores/draft_phrase_pool_builder.py
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.server.stores.active_phrase_set_store import load_active_phrase_set
from backend.server.stores.draft_phrase_selector import select_draft_phrases
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


def _clean_spaces(s: Any) -> str:
    s = fix_mojibake_text(str(s or ""))
    return re.sub(r"\s+", " ", s).strip()


def _clean_list(values: Any) -> List[str]:
    if not isinstance(values, list):
        return []

    out: List[str] = []
    seen = set()

    for v in values:
        x = _clean_spaces(v)
        if x and x not in seen:
            seen.add(x)
            out.append(x)

    return out


def _strip_drafts_prefix(title: str) -> str:
    s = _clean_spaces(title)
    if s.lower().startswith("drafts "):
        s = s[7:].strip()
    return s


def _canonical_phrase(s: str) -> str:
    s = _clean_spaces(s).lower()
    s = s.replace("_", " ").replace("-", " ")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _quality_gate_phrase(phrase: str, rec: Dict[str, Any]) -> bool:
    p = _canonical_phrase(phrase)
    if not p:
        return False

    tokens = p.split()

    if len(tokens) < 2 or len(tokens) > 6:
        return False

    if len(set(tokens)) < len(tokens):
        return False

    weak = {
        "the", "and", "for", "with", "after", "before",
        "from", "into", "that", "this", "those", "these"
    }

    if tokens[0] in weak:
        return False

    if tokens[-1] in weak:
        return False

    score = int(rec.get("score", 0))
    if score <= 0:
        return False

    return True


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

        working_title = _strip_drafts_prefix(
            item.get("working_title") or item.get("title") or ""
        )

        aliases = _clean_list(item.get("aliases"))
        planned_slug = _clean_spaces(item.get("planned_slug") or "")
        item_topic_id = _clean_spaces(item.get("topic_id") or item.get("id") or "")
        item_url = _clean_spaces(item.get("planned_url") or "")

        summary = _clean_spaces(
            item.get("summary")
            or item.get("description")
            or item.get("notes")
            or item.get("excerpt")
            or ""
        )

        if active_draft_id_set:
         if item_topic_id not in active_draft_id_set and not item_topic_id.startswith("www-"):
          continue

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
        item_added_any = False

        for phrase_obj in extracted_items:
            if not isinstance(phrase_obj, dict):
                continue

            phrase = _canonical_phrase(phrase_obj.get("phrase") or "")
            if not phrase:
                continue

            source_type = _clean_spaces(phrase_obj.get("source_type") or "unknown")
            section_id = _clean_spaces(phrase_obj.get("section_id") or "")
            snippet = _clean_spaces(phrase_obj.get("snippet") or "")
            vertical = _clean_spaces(selected_obj.get("vertical") or "generic")
            score = int(phrase_obj.get("score") or 0)

            rec = phrases.get(phrase)

            if rec is None:
                rec = {
                    "phrase": phrase,
                    "source": "draft_topics",
                    "source_type": source_type,
                    "score": score,
                    "vertical": vertical,
                    "topic_ids": [item_topic_id] if item_topic_id else [],
                    "planned_urls": [item_url] if item_url else [],
                    "occurrences": 1,
                    "section_ids": [section_id] if section_id else [],
                    "snippets": [snippet] if snippet else [],
                }
                phrases[phrase] = rec
            else:
                rec["occurrences"] = int(rec.get("occurrences", 0)) + 1

                if score > int(rec.get("score", 0)):
                    rec["score"] = score
                    rec["source_type"] = source_type

                if item_topic_id and item_topic_id not in rec["topic_ids"]:
                    rec["topic_ids"].append(item_topic_id)

                if item_url and item_url not in rec["planned_urls"]:
                    rec["planned_urls"].append(item_url)

                if section_id and section_id not in rec["section_ids"]:
                    rec["section_ids"].append(section_id)

                if snippet and snippet not in rec["snippets"]:
                    rec["snippets"].append(snippet)

            item_added_any = True

        if item_added_any:
            topics_used += 1

    # final gate
    gated: Dict[str, Dict[str, Any]] = {}
    for phrase, rec in phrases.items():
        if _quality_gate_phrase(phrase, rec):
            gated[phrase] = rec

    sorted_items = sorted(
        gated.items(),
        key=lambda kv: (-int(kv[1].get("score", 0)), kv[0])
    )

    final_phrases = {k: v for k, v in sorted_items}

    out_obj = {
        "workspace_id": ws,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "topic_count": topics_seen,
        "topics_used": topics_used,
        "phrase_count": len(final_phrases),
        "active_phrase_set_used": bool(active_draft_id_set),
        "active_draft_ids_count": len(active_draft_ids),
        "phrases": final_phrases,
    }

    out_path.write_text(
        json.dumps(out_obj, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return out_obj


def build_draft_phrase_pool(workspace_id: str) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)
    src_path = _draft_phrase_index_path(ws)

    if not src_path.exists():
        raise FileNotFoundError(f"Missing draft phrase index file: {src_path}")

    raw = _safe_read_json(src_path)
    if not isinstance(raw, dict):
        raw = {}

    source_phrases = raw.get("phrases")
    if not isinstance(source_phrases, dict):
        source_phrases = {}

    active_obj = load_active_phrase_set(ws)
    active_draft_ids = [
        str(x).strip()
        for x in (active_obj.get("active_draft_ids") or [])
        if str(x).strip()
    ]
    active_draft_id_set = set(active_draft_ids)

    phrases: Dict[str, Dict[str, Any]] = {}
    source_phrase_count = 0

    for phrase, rec in source_phrases.items():
        if not isinstance(rec, dict):
            continue

        source_phrase_count += 1

        topic_ids = _clean_list(rec.get("topic_ids"))


        if active_draft_id_set:
         matched_ids = [t for t in topic_ids if t in active_draft_id_set]
         has_real_topic_ids = any(str(t).startswith("www-") for t in topic_ids)
        if not matched_ids and not has_real_topic_ids:
         continue

        clean_key = _canonical_phrase(phrase)
        clean_rec = dict(rec)

        clean_rec["phrase"] = clean_key
        clean_rec["topic_ids"] = topic_ids
        clean_rec["planned_urls"] = _clean_list(rec.get("planned_urls"))
        clean_rec["section_ids"] = _clean_list(rec.get("section_ids"))
        clean_rec["snippets"] = _clean_list(rec.get("snippets"))
        clean_rec["source_type"] = _clean_spaces(rec.get("source_type"))
        clean_rec["vertical"] = _clean_spaces(rec.get("vertical"))

        if _quality_gate_phrase(clean_key, clean_rec):
            phrases[clean_key] = clean_rec

    sorted_items = sorted(
        phrases.items(),
        key=lambda kv: (-int(kv[1].get("score", 0)), kv[0])
    )

    final_phrases = {k: v for k, v in sorted_items}

    out_obj = {
        "workspace_id": ws,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source_phrase_count": source_phrase_count,
        "phrase_count": len(final_phrases),
        "active_phrase_set_used": bool(active_draft_id_set),
        "active_draft_ids_count": len(active_draft_ids),
        "phrases": final_phrases,
    }

    out_path = _draft_phrase_pool_path(ws)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(out_obj, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return out_obj