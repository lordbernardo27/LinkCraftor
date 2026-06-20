
# backend/server/engine/workspace_path_section_fallback_enricher.py

import json
import re
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data")


_BAD_SEGMENTS = {
    "",
    "www",
    "com",
    "html",
    "aspx",
    "amp",
    "page",
}


def _ws(workspace_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", str(workspace_id or "default"))


def _titleize(segment: str) -> str:
    s = re.sub(r"[-_]+", " ", str(segment or "")).strip()
    s = re.sub(r"\s+", " ", s)
    return s.title()


def _keywordize(segment: str) -> str:
    s = re.sub(r"[-_]+", " ", str(segment or "")).strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def _path_segments(path: str, url: str = "") -> List[str]:
    raw = str(path or "").strip()

    if not raw and url:
        try:
            from urllib.parse import urlparse
            raw = urlparse(url).path or ""
        except Exception:
            raw = ""

    raw = raw.split("?")[0].split("#")[0]
    parts = [x.strip() for x in raw.split("/") if x.strip()]

    clean = []
    for part in parts:
        base = re.sub(r"\.(html|htm|aspx|php)$", "", part, flags=re.I).strip()
        key = base.lower()
        if key in _BAD_SEGMENTS:
            continue
        if len(key) <= 1:
            continue
        clean.append(base)

    return clean


def enrich_path_sections(workspace_id: str) -> Dict[str, Any]:
    ws = _ws(workspace_id)

    fp = DATA_DIR / "target_pools" / "live_domain" / f"live_domain_target_pool_{ws}.json"

    if not fp.exists():
        raise FileNotFoundError(f"live domain target pool missing: {fp}")

    data = json.loads(fp.read_text(encoding="utf-8"))
    items = data.get("items", [])

    updated = 0
    already_sectioned = 0
    skipped = 0

    for item in items:
        if not isinstance(item, dict):
            skipped += 1
            continue

        has_section = bool(item.get("section_names") or item.get("section_keywords"))

        if has_section:
            already_sectioned += 1
            continue

        segments = _path_segments(item.get("path", ""), item.get("url", ""))

        if not segments:
            skipped += 1
            continue

        # Use parent path segments as broad section names.
        section_segments = segments[:-1] if len(segments) > 1 else segments

        section_names = []
        section_keywords = []

        for seg in section_segments:
            name = _titleize(seg)
            kw = _keywordize(seg)

            if name and name not in section_names:
                section_names.append(name)

            if kw and kw not in section_keywords:
                section_keywords.append(kw)

        # Add page slug/title as weak section keyword fallback.
        final_slug = segments[-1]
        final_kw = _keywordize(final_slug)
        if final_kw and final_kw not in section_keywords:
            section_keywords.append(final_kw)

        title_kw = _keywordize(item.get("title") or item.get("h1") or "")
        if title_kw and title_kw not in section_keywords:
            section_keywords.append(title_kw)

        if not section_names and not section_keywords:
            skipped += 1
            continue

        item["section_names"] = section_names
        item["section_keywords"] = section_keywords
        item["section_ids"] = item.get("section_ids") or [
            "path_fallback:" + _keywordize(x).replace(" ", "_") for x in section_names
        ]
        item["section_score"] = max(float(item.get("section_score") or 0), 0.55)
        item["section_matched_terms"] = item.get("section_matched_terms") or section_keywords[:8]
        item["section_fallback_source"] = "url_path"
        item["section_fallback_version"] = "path_section_fallback_v1"

        updated += 1

    data["items"] = items
    data.setdefault("counts", {})
    data["counts"]["path_section_fallback_updated"] = updated
    data["counts"]["path_section_fallback_already_sectioned"] = already_sectioned
    data["counts"]["path_section_fallback_skipped"] = skipped

    fp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "workspace_id": ws,
        "path": str(fp),
        "total": len(items),
        "updated": updated,
        "already_sectioned": already_sectioned,
        "skipped": skipped,
    }
