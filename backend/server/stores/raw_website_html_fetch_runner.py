from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict

from backend.server.stores.raw_website_html_store import upsert_raw_website_html_v1


DATA_ROOT = Path(__file__).resolve().parents[1] / "data"


def _site_pages_path_v1(workspace_id: str) -> Path:
    return DATA_ROOT / f"site_pages_{workspace_id}.json"


def load_connected_site_urls_v1(workspace_id: str) -> list[dict[str, Any]]:
    fp = _site_pages_path_v1(workspace_id)
    data = json.loads(fp.read_text(encoding="utf-8"))

    pages = data.get("pages") or {}
    records = list(pages.values()) if isinstance(pages, dict) else pages

    out = []
    seen = set()

    for rec in records:
        if not isinstance(rec, dict):
            continue

        url = rec.get("url")
        if not url or url in seen:
            continue

        seen.add(url)
        out.append(rec)

    return out


def fetch_url_html_v1(url: str, timeout: int = 20) -> Dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 LinkCraftorBot/1.0",
            "Accept": "text/html,application/xhtml+xml,*/*",
        },
    )

    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read()
        html = raw.decode("utf-8", errors="ignore")

        return {
            "ok": True,
            "url": url,
            "html": html,
            "status_code": getattr(response, "status", None),
            "content_type": response.headers.get("Content-Type", ""),
            "bytes": len(raw),
        }


def build_raw_website_html_store_from_connected_urls_v1(
    *,
    workspace_id: str,
    limit: int | None = None,
    delay_seconds: float = 0.25,
) -> Dict[str, Any]:
    records = load_connected_site_urls_v1(workspace_id)

    if limit is not None:
        records = records[: int(limit)]

    counts = {
        "connected_urls_selected": len(records),
        "attempted": 0,
        "stored": 0,
        "failed": 0,
        "non_html": 0,
    }

    failures = []

    for rec in records:
        url = rec.get("url")
        title = rec.get("title") or rec.get("h1") or ""

        counts["attempted"] += 1

        try:
            fetched = fetch_url_html_v1(url)

            content_type = fetched.get("content_type") or ""
            html = fetched.get("html") or ""

            if "html" not in content_type.lower() and "<html" not in html.lower():
                counts["non_html"] += 1

            upsert_raw_website_html_v1(
                workspace_id=workspace_id,
                url=url,
                html=html,
                title=title,
                status_code=fetched.get("status_code"),
                content_type=content_type,
                metadata={
                    "source_pipeline": "raw_website_html_fetch_runner_v1",
                    "source_stage": "connected_site_pages",
                    "site_page_record": rec,
                    "bytes": fetched.get("bytes"),
                },
            )

            counts["stored"] += 1

        except Exception as exc:
            counts["failed"] += 1
            failures.append({
                "url": url,
                "error": str(exc),
            })

        if delay_seconds:
            time.sleep(delay_seconds)

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "runner": "raw_website_html_fetch_runner_v1",
        "counts": counts,
        "failure_sample": failures[:20],
    }
