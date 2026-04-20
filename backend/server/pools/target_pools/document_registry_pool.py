from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.server.utils.text_normalization import fix_mojibake_text


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    server_dir = here.parents[2]  # .../backend/server
    return server_dir / "data"


def _docs_root() -> Path:
    return _data_dir() / "docs"


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


def _ws_docs_dir(ws: str) -> Path:
    return _docs_root() / _ws_safe(ws)


def _index_path(ws: str) -> Path:
    return _ws_docs_dir(ws) / "index.json"


def _pool_path(ws: str) -> Path:
    return (
        _data_dir()
        / "target_pools"
        / "document_registry"
        / f"document_registry_{_ws_safe(ws)}.json"
    )


def _clean_text(s: str) -> str:
    s = str(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("\ufeff", " ")
    s = fix_mojibake_text(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _norm_title(s: str) -> str:
    s = _clean_text(s).lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _filename_to_title(name: str) -> str:
    name = Path(str(name or "")).stem
    name = fix_mojibake_text(name)
    name = re.sub(r"[_\-]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:200]


def _extract_h1_from_html(text: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", text or "", flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return ""
    return _clean_text(m.group(1))[:200]


def _extract_first_heading(text: str) -> str:
    m = re.search(
        r"<h([1-6])[^>]*>(.*?)</h\1>",
        text or "",
        flags=re.IGNORECASE | re.DOTALL,
    )
    if m:
        return _clean_text(m.group(2))[:200]

    for line in (text or "").splitlines():
        t = line.strip()
        if not t:
            continue
        if t.startswith("#"):
            t = re.sub(r"^#+\s*", "", t).strip()
            return _clean_text(t)[:200]

    return ""


def _extract_first_meaningful_line(text: str) -> str:
    for line in (text or "").splitlines():
        t = _clean_text(line)
        if not t:
            continue
        if len(t) < 3:
            continue
        return t[:200]
    return ""


def _is_test_or_demo_title(title: str) -> bool:
    t = (title or "").lower().strip()

    if len(t) < 5:
        return True

    bad_patterns = [
        "doc one",
        "doc1",
        "docpool",
        "test",
        "sample",
        "demo",
        "example",
    ]

    for p in bad_patterns:
        if p in t:
            return True

    return False


def _pick_title(rec: Dict[str, Any], file_text: str) -> Dict[str, str]:
    # 1) Prefer indexed H1 from upload pipeline
    indexed_h1 = _clean_text(rec.get("h1") or "")
    if indexed_h1:
        return {
            "title": indexed_h1[:200],
            "title_source": str(rec.get("h1_source") or "h1"),
        }

    # 2) Try parsing html-ish content
    h1 = _extract_h1_from_html(file_text)
    if h1:
        return {"title": h1, "title_source": "h1"}

    heading = _extract_first_heading(file_text)
    if heading:
        return {"title": heading, "title_source": "first_heading"}

    # 3) Filename from index metadata
    meta_title = _clean_text(rec.get("filename") or rec.get("title") or rec.get("name") or "")
    if meta_title:
        return {"title": meta_title[:200], "title_source": "filename"}

    # 4) Stored filename
    stored_name = rec.get("stored_name") or rec.get("storedName") or ""
    file_name_title = _filename_to_title(stored_name)
    if file_name_title:
        return {"title": file_name_title, "title_source": "filename"}

    # 5) First meaningful line
    first_line = _extract_first_meaningful_line(file_text)
    if first_line:
        return {"title": first_line, "title_source": "first_meaningful_line"}

    return {"title": "", "title_source": ""}


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _uploaded_at_key(rec: Dict[str, Any]) -> str:
    return str(rec.get("uploaded_at") or "")


def build_document_registry_pool(workspace_id: str) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)
    if not ws:
        raise ValueError("workspace_id is required")

    idx_fp = _index_path(ws)
    if not idx_fp.exists():
        raise FileNotFoundError(f"Missing docs index: {idx_fp}")

    rows = _safe_read_json(idx_fp)
    if not isinstance(rows, list):
        rows = []

    active_fp = _data_dir() / "target_pools" / f"active_target_set_{ws}.json"
    active_obj = _safe_read_json(active_fp) if active_fp.exists() else None
    active_document_ids: List[str] = []

    if isinstance(active_obj, dict):
        raw_ids = active_obj.get("active_document_ids") or []
        if isinstance(raw_ids, list):
            active_document_ids = [str(x).strip() for x in raw_ids if str(x).strip()]

    if active_fp.exists():
        active_id_set = set(active_document_ids)
        rows = [
            rec
            for rec in rows
            if isinstance(rec, dict)
            and str(rec.get("doc_id") or rec.get("docId") or "").strip() in active_id_set
        ]

    docs_dir = _ws_docs_dir(ws)

    documents_seen = 0
    documents_written = 0
    missing_title = 0
    duplicate_titles_collapsed = 0
    test_titles_removed = 0

    deduped: Dict[str, Dict[str, Any]] = {}

    for rec in rows:
        if not isinstance(rec, dict):
            continue

        documents_seen += 1

        document_id = str(rec.get("doc_id") or rec.get("docId") or "").strip()
        if not document_id:
            missing_title += 1
            continue

        stored_name = str(rec.get("stored_name") or rec.get("storedName") or "").strip()
        file_text = ""
        if stored_name:
            file_fp = docs_dir / stored_name
            if file_fp.exists():
                file_text = _safe_read_text(file_fp)

        picked = _pick_title(rec, file_text)
        title = (picked.get("title") or "").strip()
        title_source = (picked.get("title_source") or "").strip()

        if not title:
            missing_title += 1
            continue

        if _is_test_or_demo_title(title):
            test_titles_removed += 1
            continue

        norm = _norm_title(title)
        if not norm:
            missing_title += 1
            continue

        candidate = {
            "document_id": document_id,
            "title": title,
            "title_source": title_source,
            "link_target": f"/documents/{document_id}",
            "_uploaded_at": _uploaded_at_key(rec),
        }

        existing = deduped.get(norm)
        if existing is None:
            deduped[norm] = candidate
        else:
            duplicate_titles_collapsed += 1
            # Keep newest uploaded document
            if candidate["_uploaded_at"] >= existing["_uploaded_at"]:
                deduped[norm] = candidate

    items: List[Dict[str, str]] = []
    for _, item in deduped.items():
        items.append(
            {
                "document_id": item["document_id"],
                "title": item["title"],
                "title_source": item["title_source"],
                "link_target": item["link_target"],
            }
        )

    items.sort(key=lambda x: x["title"].lower())
    documents_written = len(items)

    out: Dict[str, Any] = {
        "workspace_id": ws,
        "type": "document_registry",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "documents_seen": documents_seen,
            "documents_written": documents_written,
            "missing_title": missing_title,
            "duplicate_titles_collapsed": duplicate_titles_collapsed,
            "test_titles_removed": test_titles_removed,
        },
        "source": f"docs/{ws}/index.json",
        "active_target_set_used": active_fp.exists(),
        "active_document_ids_count": len(active_document_ids),
        "items": items,
    }

    out_fp = _pool_path(ws)
    out_fp.parent.mkdir(parents=True, exist_ok=True)
    out_fp.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    return out