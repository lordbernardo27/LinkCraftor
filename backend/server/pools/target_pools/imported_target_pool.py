# backend/server/pools/target_pools/imported_target_pool.py

from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse, unquote


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    server_dir = here.parents[2]  # .../backend/server
    return server_dir / "data"


def _pool_path(ws: str) -> Path:
    return _data_dir() / "target_pools" / "imported" / f"imported_target_pool_{ws}.json"


def _csv_path(ws: str) -> Path:
    return _data_dir() / f"imported_targets_{ws}.csv"


def _txt_path(ws: str) -> Path:
    return _data_dir() / f"imported_targets_{ws}.txt"


def _xml_path(ws: str) -> Path:
    return _data_dir() / f"imported_targets_{ws}.xml"


def _site_sources_path(ws: str) -> Path:
    return _data_dir() / f"site_sources_{ws}.json"


def _active_target_set_path(ws: str) -> Path:
    return _data_dir() / "target_pools" / f"active_target_set_{ws}.json"


def _clean(s: str) -> str:
    return str(s or "").strip().strip("\ufeff").strip()


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _is_http_url(u: str) -> bool:
    u = (u or "").strip().lower()
    return u.startswith("http://") or u.startswith("https://")


def _domain_from_sources_or_ws(ws: str) -> str:
    """
    Derive domain for placeholder URL generation.
    Prefer site_sources_<ws>.json sources[0].domain if present.
    Otherwise derive from ws name: ws_example_com -> example.com
    """
    fp = _site_sources_path(ws)
    if fp.exists():
        try:
            obj = json.loads(fp.read_text(encoding="utf-8"))
            arr = obj.get("sources") or []
            if isinstance(arr, list) and arr:
                dom = str((arr[0] or {}).get("domain") or "").strip().lower()
                dom = dom[4:] if dom.startswith("www.") else dom
                if dom:
                    return dom
        except Exception:
            pass

    s = ws
    if s.startswith("ws_"):
        s = s[3:]
    return s.replace("_", ".").strip(".").lower()


_slug_re = re.compile(r"[^a-z0-9]+")


def _slugify(s: str) -> str:
    s = _clean(s).lower()
    s = _slug_re.sub("-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "imported"


def _norm_url(u: str) -> str:
    u = _clean(u)
    return u[:-1] if u.endswith("/") else u


def _clean_label(label: str) -> str:
    label = _clean(label)
    if not label:
        return "Untitled"

    label = label.replace("-", " ").replace("_", " ")
    label = re.sub(r"\s+", " ", label).strip()

    word_map = {
        "whats": "What's",
        "hcg": "HCG",
        "ivf": "IVF",
        "lmp": "LMP",
        "c": "C",
    }

    small_words = {
        "a", "an", "and", "as", "at", "by", "for", "in", "of", "on", "or", "the", "to", "vs"
    }

    parts = label.split(" ")
    out: List[str] = []

    for i, part in enumerate(parts):
        low = part.lower()
        if low in word_map:
            out.append(word_map[low])
        elif low == "section":
            out.append("Section")
        elif low == "api":
            out.append("API")
        elif low == "seo":
            out.append("SEO")
        elif low == "url":
            out.append("URL")
        elif low == "h1":
            out.append("H1")
        elif low == "h2":
            out.append("H2")
        elif low == "h3":
            out.append("H3")
        elif low in small_words and i != 0:
            out.append(low)
        elif low.isdigit():
            out.append(low)
        else:
            out.append(low.capitalize())

    cleaned = " ".join(out)

    cleaned = re.sub(r"\bC Section\b", "C-Section", cleaned)
    cleaned = re.sub(r"\bWeek (\d{1,2}) (\d{1,2})\b", r"Week \1-\2", cleaned)
    cleaned = re.sub(r"\bWhat To\b", "What to", cleaned)
    cleaned = re.sub(r"\bHow To\b", "How to", cleaned)

    return cleaned or "Untitled"


def _slug_label_from_url(url: str) -> str:
    try:
        u = urlparse((url or "").strip())
        path = unquote(u.path or "").strip().rstrip("/")
        seg = path.split("/")[-1] if path else ""
        seg = (seg or "").strip()
        if not seg:
            return "Untitled"
        seg = seg.replace("-", " ").replace("_", " ").strip()
        seg = re.sub(r"\s+", " ", seg)
        return _clean_label(seg)
    except Exception:
        return "Untitled"


def _read_csv(fp: Path) -> List[Tuple[str, str]]:
    """
    Accept:
      - URL
      - Title
      - Title,URL
      - URL,Title
      - header forms supported (url/title/label/topic/name)
    Returns: (title, url_or_empty)
    """
    rows: List[Tuple[str, str]] = []
    with fp.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = None
        for i, r in enumerate(reader):
            if not r:
                continue

            if i == 0:
                low = [_clean(x).lower() for x in r]
                if any(x in {"url", "link", "href"} for x in low) or any(
                    x in {"title", "topic", "label", "name"} for x in low
                ):
                    header = low
                    continue

            if header:
                rec = {header[j]: _clean(r[j]) if j < len(r) else "" for j in range(len(header))}
                url = rec.get("url") or rec.get("link") or rec.get("href") or ""
                title = rec.get("title") or rec.get("topic") or rec.get("name") or rec.get("label") or ""
                rows.append((_clean(title), _clean(url)))
            else:
                c0 = _clean(r[0]) if len(r) >= 1 else ""
                c1 = _clean(r[1]) if len(r) >= 2 else ""

                if len(r) == 1:
                    if _is_http_url(c0):
                        rows.append(("", c0))
                    else:
                        rows.append((c0, ""))
                    continue

                if _is_http_url(c0):
                    rows.append((c1, c0))
                elif _is_http_url(c1):
                    rows.append((c0, c1))
                else:
                    rows.append((c0, ""))
    return rows


def _read_txt(fp: Path) -> List[Tuple[str, str]]:
    """
    Accept:
      - URL per line
      - Title per line
      - Title,URL per line
    Returns: (title, url_or_empty)
    """
    rows: List[Tuple[str, str]] = []
    for line in fp.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        try:
            parsed = next(csv.reader([line]))
        except Exception:
            parsed = [line]

        if not parsed:
            continue

        if len(parsed) == 1:
            c0 = _clean(parsed[0])
            if _is_http_url(c0):
                rows.append(("", c0))
            else:
                rows.append((c0, ""))
            continue

        c0 = _clean(parsed[0])
        c1 = _clean(parsed[1])

        if _is_http_url(c0):
            rows.append((c1, c0))
        elif _is_http_url(c1):
            rows.append((c0, c1))
        else:
            rows.append((c0, ""))
    return rows


def _read_xml_sitemap(fp: Path) -> List[Tuple[str, str]]:
    """
    Accept sitemap-like XML:
      <urlset> ... <loc>https://...</loc> ...
    Returns: (title_empty, url)
    """
    rows: List[Tuple[str, str]] = []
    root = ET.fromstring(fp.read_bytes())
    for el in root.findall(".//{*}loc"):
        if el is not None and el.text and el.text.strip():
            u = el.text.strip()
            if _is_http_url(u):
                rows.append(("", u))
    return rows


def build_imported_target_pool(
    workspace_id: str,
    *,
    placeholder_path: str = "/drafts",
    merge_all: bool = True,
) -> Dict[str, Any]:
    """
    Imported Target Pool (WS ONLY, formats ONLY):
      - Reads ONLY ws-scoped inputs: imported_targets_<ws>.(csv|txt|xml)
      - Topic-only rows become placeholder URLs under placeholder_path.
      - Dedup by URL; prefer an explicit title/label when duplicates exist.
      - Output items: {url, label}
      - if active_target_set_<ws>.json exists, only keeps active imported URLs
    """
    ws = _clean(workspace_id)
    if not ws:
        raise ValueError("workspace_id is required")

    domain = _domain_from_sources_or_ws(ws)
    base = f"https://{domain}".rstrip("/")
    pp = "/" + str(placeholder_path or "/drafts").lstrip("/")
    pp = pp.rstrip("/")

    sources_used: List[str] = []
    per_source_counts: Dict[str, int] = {}
    all_pairs: List[Tuple[str, str]] = []

    def add_pairs(name: str, pairs: List[Tuple[str, str]]) -> None:
        if not pairs:
            return
        sources_used.append(name)
        per_source_counts[name] = len(pairs)
        all_pairs.extend(pairs)

    csv_fp = _csv_path(ws)
    txt_fp = _txt_path(ws)
    xml_fp = _xml_path(ws)

    if merge_all:
        if csv_fp.exists():
            add_pairs(str(csv_fp), _read_csv(csv_fp))
        if txt_fp.exists():
            add_pairs(str(txt_fp), _read_txt(txt_fp))
        if xml_fp.exists():
            add_pairs(str(xml_fp), _read_xml_sitemap(xml_fp))
    else:
        if csv_fp.exists():
            add_pairs(str(csv_fp), _read_csv(csv_fp))
        elif txt_fp.exists():
            add_pairs(str(txt_fp), _read_txt(txt_fp))
        elif xml_fp.exists():
            add_pairs(str(xml_fp), _read_xml_sitemap(xml_fp))

    if not all_pairs:
        raise FileNotFoundError(
            "No imported target inputs found (or all were empty). Looked for: "
            f"{csv_fp.name}, {txt_fp.name}, {xml_fp.name} in backend/server/data/"
        )

    active_fp = _active_target_set_path(ws)
    active_obj = _safe_read_json(active_fp) if active_fp.exists() else None
    active_imported_urls: List[str] = []

    if isinstance(active_obj, dict):
        raw_urls = active_obj.get("active_imported_urls") or []
        if isinstance(raw_urls, list):
            active_imported_urls = [_norm_url(str(x).strip()) for x in raw_urls if str(x).strip()]

    active_imported_url_set = set(active_imported_urls)

    placeholders_generated = 0

    # Dedup map: url -> best_label
    url_to_label: Dict[str, str] = {}

    for title, url in all_pairs:
        title = _clean(title)
        url = _norm_url(url)

        if (not _is_http_url(url)) and title:
            url = f"{base}{pp}/{_slugify(title)}"
            placeholders_generated += 1

        if not _is_http_url(url):
            continue

        label = _clean_label(title) if title else _slug_label_from_url(url)

        existing = url_to_label.get(url)
        if existing is None:
            url_to_label[url] = label
        else:
            if title:
                url_to_label[url] = label

    filtered_urls = sorted(url_to_label.keys())
    if active_fp.exists():
        filtered_urls = [u for u in filtered_urls if u in active_imported_url_set]

    items = [
        {"url": u, "label": _clean_label(url_to_label[u])}
        for u in filtered_urls
        if url_to_label[u].strip().lower() != "untitled"
        and "example.com" not in u.lower()
        and "openai.com" not in u.lower()
    ]

    out: Dict[str, Any] = {
        "workspace_id": ws,
        "type": "imported",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "merge_all": bool(merge_all),
        "sources_used": sources_used,
        "per_source_counts": per_source_counts,
        "placeholder_path": pp,
        "domain": domain,
        "active_target_set_used": active_fp.exists(),
        "active_imported_urls_count": len(active_imported_urls),
        "counts": {
            "rows_read_total": len(all_pairs),
            "placeholders_generated": placeholders_generated,
            "unique_urls_before_active_filter": len(url_to_label),
            "unique_urls_written": len(items),
        },
        "items": items,
    }

    out_fp = _pool_path(ws)
    out_fp.parent.mkdir(parents=True, exist_ok=True)
    out_fp.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out