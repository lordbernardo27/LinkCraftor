from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.server.stores.active_phrase_set_store import load_active_phrase_set


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


def _csv_input_path(ws: str) -> Path:
    return _data_dir() / f"imported_targets_{_ws_safe(ws)}.csv"


def _txt_input_path(ws: str) -> Path:
    return _data_dir() / f"imported_targets_{_ws_safe(ws)}.txt"


def _xml_input_path(ws: str) -> Path:
    return _data_dir() / f"imported_targets_{_ws_safe(ws)}.xml"


def _imported_phrase_index_path(ws: str) -> Path:
    return _data_dir() / f"imported_phrase_index_{_ws_safe(ws)}.json"


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _clean_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()


def _slug_to_text(slug_or_url: str) -> str:
    s = str(slug_or_url or "").strip()
    s = s.rsplit("/", 1)[-1]
    s = s.strip("/")
    s = s.replace("-", " ").replace("_", " ")
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
                rows.append({
                    "id": str(r.get("url") or r.get("URL") or r.get("link") or "").strip(),
                    "title": str(r.get("title") or r.get("Title") or r.get("topic") or "").strip(),
                    "url": str(r.get("url") or r.get("URL") or r.get("link") or "").strip(),
                })

    elif txt_path.exists():
        for line in txt_path.read_text(encoding="utf-8").splitlines():
            u = str(line or "").strip()
            if not u:
                continue
            rows.append({
                "id": u,
                "title": "",
                "url": u,
            })

    elif xml_path.exists():
        xml_text = xml_path.read_text(encoding="utf-8", errors="ignore")
        locs = re.findall(r"<loc>(.*?)</loc>", xml_text, flags=re.IGNORECASE)
        for u in locs:
            u = str(u or "").strip()
            if not u:
                continue
            rows.append({
                "id": u,
                "title": "",
                "url": u,
            })

    else:
        raise FileNotFoundError(
            f"Missing imported input file. Looked for: {csv_path.name}, {txt_path.name}, {xml_path.name}"
        )

    raw = rows

    phrases: Dict[str, Dict[str, Any]] = {}
    rows_seen = 0
    rows_used = 0

    for item in raw:
        if not isinstance(item, dict):
            continue

        rows_seen += 1

        item_id = str(
            item.get("id")
            or item.get("import_id")
            or item.get("url")
            or item.get("source_url")
            or ""
        ).strip()

        if active_imported_url_set and item_id not in active_imported_url_set:
            continue

        title = _clean_spaces(item.get("title") or item.get("topic") or item.get("name") or "")
        url = str(item.get("url") or item.get("source_url") or "").strip()
        slug_text = _slug_to_text(url)

        text_sources: List[str] = []
        if title:
            text_sources.append(title)
        if slug_text:
            text_sources.append(slug_text)

        item_added_any = False

        for source_text in text_sources:
            extracted = _extract_phrases_from_text(source_text)
            for phrase in extracted:
                rec = phrases.get(phrase)
                if rec is None:
                    phrases[phrase] = {
                        "phrase": phrase,
                        "source": "imported_urls",
                        "import_ids": [item_id] if item_id else [],
                        "urls": [url] if url else [],
                        "occurrences": 1,
                    }
                else:
                    rec["occurrences"] = int(rec.get("occurrences") or 0) + 1
                    if item_id and item_id not in rec.get("import_ids", []):
                        rec.setdefault("import_ids", []).append(item_id)
                    if url and url not in rec.get("urls", []):
                        rec.setdefault("urls", []).append(url)
                item_added_any = True

        if item_added_any:
            rows_used += 1

    out_obj = {
        "workspace_id": ws,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "rows_seen": rows_seen,
        "rows_used": rows_used,
        "phrase_count": len(phrases),
        "active_phrase_set_used": bool(active_imported_url_set),
        "active_imported_urls_count": len(active_imported_urls),
        "phrases": phrases,
    }

    out_path.write_text(json.dumps(out_obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_obj