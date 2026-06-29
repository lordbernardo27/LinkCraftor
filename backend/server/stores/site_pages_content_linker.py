from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DATA_ROOT = Path("backend/server/data")


def content_id_for_url_v1(url: str) -> str:
    digest = hashlib.sha256(str(url or "").strip().encode("utf-8")).hexdigest()[:16]
    return f"web_content_{digest}"


def _site_pages_path_v1(workspace_id: str) -> Path:
    return DATA_ROOT / f"site_pages_{workspace_id}.json"


def link_site_pages_to_unified_content_v1(
    *,
    workspace_id: str,
    site_pages_path: str | None = None,
) -> Dict[str, Any]:
    path = Path(site_pages_path) if site_pages_path else _site_pages_path_v1(workspace_id)

    if not path.exists():
        raise FileNotFoundError(f"Site pages file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))

    pages = data.get("pages", [])
    linked = 0
    skipped = 0

    for page in pages:
        if not isinstance(page, dict):
            skipped += 1
            continue

        url = page.get("url") or page.get("loc") or page.get("href")

        if not url:
            skipped += 1
            continue

        page["content_id"] = content_id_for_url_v1(url)
        page["unified_content_ref"] = {
            "store": "website_unified_content_store_v1",
            "content_id": page["content_id"],
            "source_type": "website_crawl",
        }

        linked += 1

    data["pages"] = pages
    data["content_linking"] = {
        "linked_count": linked,
        "skipped_count": skipped,
        "linked_at_utc": datetime.now(timezone.utc).isoformat(),
        "content_store": "website_unified_content_store_v1",
    }
    data["updated_at"] = datetime.now(timezone.utc).isoformat()

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "status": "passed",
        "workspace_id": workspace_id,
        "site_pages_path": str(path),
        "linked_count": linked,
        "skipped_count": skipped,
    }
