from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.server.stores.active_phrase_set_store import load_active_phrase_set
from backend.server.stores.imported_phrase_selector import select_imported_phrases


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


def _csv_input_path(ws: str) -> Path:
    return _data_dir() / f"imported_targets_{_ws_safe(ws)}.csv"


def _txt_input_path(ws: str) -> Path:
    return _data_dir() / f"imported_targets_{_ws_safe(ws)}.txt"


def _xml_input_path(ws: str) -> Path:
    return _data_dir() / f"imported_targets_{_ws_safe(ws)}.xml"


def _imported_phrase_index_path(ws: str) -> Path:
    return _data_dir() / f"imported_phrase_index_{_ws_safe(ws)}.json"


def _imported_phrase_pool_path(ws: str) -> Path:
    return _data_dir() / "phrase_pools" / "imported" / f"imported_phrase_pool_{_ws_safe(ws)}.json"


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _clean_spaces(s: Any) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()


def _canonical_phrase(s: Any) -> str:
    s = _clean_spaces(s).lower()
    s = s.replace("_", " ").replace("-", " ")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
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


def _quality_gate_phrase(phrase: str, rec: Dict[str, Any]) -> bool:
    p = _canonical_phrase(phrase)
    if not p:
        return False

    toks = p.split()

    if len(toks) < 2 or len(toks) > 8:
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


def _load_rows(ws: str) -> List[Dict[str, Any]]:
    csv_path = _csv_input_path(ws)
    txt_path = _txt_input_path(ws)
    xml_path = _xml_input_path(ws)

    rows: List[Dict[str, Any]] = []

    if csv_path.exists():
        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for r in reader:
                if not isinstance(r, dict):
                    continue

                url = _clean_spaces(
                    r.get("url") or r.get("URL") or r.get("link") or ""
                )

                title = _clean_spaces(
                    r.get("title") or r.get("Title") or r.get("topic") or ""
                )

                rows.append({
                    "id": url,
                    "title": title,
                    "url": url,
                })

    elif txt_path.exists():
        for line in txt_path.read_text(encoding="utf-8").splitlines():
            u = _clean_spaces(line)
            if not u:
                continue

            rows.append({
                "id": u,
                "title": "",
                "url": u,
            })

    elif xml_path.exists():
        xml_text = xml_path.read_text(encoding="utf-8", errors="ignore")
        locs = re.findall(r"<loc>(.*?)</loc>", xml_text, flags=re.I)

        for u in locs:
            u = _clean_spaces(u)
            if not u:
                continue

            rows.append({
                "id": u,
                "title": "",
                "url": u,
            })

    else:
        raise FileNotFoundError(
            f"Missing imported input file. Looked for: "
            f"{csv_path.name}, {txt_path.name}, {xml_path.name}"
        )

    return rows


def build_imported_phrase_index(workspace_id: str) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)
    out_path = _imported_phrase_index_path(ws)

    active_obj = load_active_phrase_set(ws)

    active_imported_urls = [
        str(x).strip()
        for x in (active_obj.get("active_imported_urls") or [])
        if str(x).strip()
    ]
    active_imported_url_set = set(active_imported_urls)

    rows = _load_rows(ws)

    phrases: Dict[str, Dict[str, Any]] = {}
    rows_seen = 0
    rows_used = 0

    for item in rows:
        if not isinstance(item, dict):
            continue

        rows_seen += 1

        item_id = _clean_spaces(
            item.get("id")
            or item.get("import_id")
            or item.get("url")
            or item.get("source_url")
            or ""
        )

        if active_imported_url_set and item_id not in active_imported_url_set:
            continue

        title = _clean_spaces(
            item.get("title") or item.get("topic") or item.get("name") or ""
        )

        url = _clean_spaces(item.get("url") or item.get("source_url") or "")

        summary = _clean_spaces(
            item.get("summary")
            or item.get("description")
            or item.get("excerpt")
            or item.get("notes")
            or ""
        )

        selected_obj = select_imported_phrases(
            workspace_id=ws,
            import_id=item_id or "import_row",
            title=title,
            url=url,
            summary=summary,
            aliases=[],
        )

        item_added_any = False

        for phrase_obj in selected_obj.get("phrases") or []:
            if not isinstance(phrase_obj, dict):
                continue

            phrase = _canonical_phrase(phrase_obj.get("phrase") or "")
            if not phrase:
                continue

            score = int(phrase_obj.get("score") or 0)
            source_type = _clean_spaces(phrase_obj.get("source_type") or "unknown")
            section_id = _clean_spaces(phrase_obj.get("section_id") or "")
            snippet = _clean_spaces(phrase_obj.get("snippet") or "")
            vertical = _clean_spaces(selected_obj.get("vertical") or "generic")

            rec = phrases.get(phrase)

            if rec is None:
                rec = {
                    "phrase": phrase,
                    "source": "imported_urls",
                    "source_type": source_type,
                    "score": score,
                    "vertical": vertical,
                    "import_ids": [item_id] if item_id else [],
                    "urls": [url] if url else [],
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

                if item_id and item_id not in rec["import_ids"]:
                    rec["import_ids"].append(item_id)

                if url and url not in rec["urls"]:
                    rec["urls"].append(url)

                if section_id and section_id not in rec["section_ids"]:
                    rec["section_ids"].append(section_id)

                if snippet and snippet not in rec["snippets"]:
                    rec["snippets"].append(snippet)

            item_added_any = True

        if item_added_any:
            rows_used += 1

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
        "rows_seen": rows_seen,
        "rows_used": rows_used,
        "phrase_count": len(final_phrases),
        "active_phrase_set_used": bool(active_imported_url_set),
        "active_imported_urls_count": len(active_imported_urls),
        "phrases": final_phrases,
    }

    out_path.write_text(
        json.dumps(out_obj, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return out_obj


def build_imported_phrase_pool(workspace_id: str) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)
    src_path = _imported_phrase_index_path(ws)
    out_path = _imported_phrase_pool_path(ws)

    if not src_path.exists():
        raise FileNotFoundError(f"Missing imported phrase index file: {src_path}")

    raw = _safe_read_json(src_path)
    if not isinstance(raw, dict):
        raw = {}

    source_phrases = raw.get("phrases")
    if not isinstance(source_phrases, dict):
        source_phrases = {}

    active_obj = load_active_phrase_set(ws)

    active_imported_urls = [
        str(x).strip()
        for x in (active_obj.get("active_imported_urls") or [])
        if str(x).strip()
    ]
    active_imported_url_set = set(active_imported_urls)

    phrases: Dict[str, Dict[str, Any]] = {}
    source_phrase_count = 0

    for phrase, rec in source_phrases.items():
        if not isinstance(rec, dict):
            continue

        source_phrase_count += 1

        urls = _clean_list(rec.get("urls"))

        if active_imported_url_set:
            matched = [u for u in urls if u in active_imported_url_set]
            if not matched:
                continue

        key = _canonical_phrase(phrase)
        if not key:
            continue

        clean_rec = dict(rec)
        clean_rec["phrase"] = key
        clean_rec["urls"] = urls
        clean_rec["import_ids"] = _clean_list(rec.get("import_ids"))
        clean_rec["section_ids"] = _clean_list(rec.get("section_ids"))
        clean_rec["snippets"] = _clean_list(rec.get("snippets"))
        clean_rec["source_type"] = _clean_spaces(rec.get("source_type"))
        clean_rec["vertical"] = _clean_spaces(rec.get("vertical"))

        if _quality_gate_phrase(key, clean_rec):
            existing = phrases.get(key)

            if existing is None:
                phrases[key] = clean_rec
            else:
                if int(clean_rec.get("score", 0)) > int(existing.get("score", 0)):
                    phrases[key] = clean_rec

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
        "active_phrase_set_used": bool(active_imported_url_set),
        "active_imported_urls_count": len(active_imported_urls),
        "phrases": final_phrases,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(out_obj, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return out_obj