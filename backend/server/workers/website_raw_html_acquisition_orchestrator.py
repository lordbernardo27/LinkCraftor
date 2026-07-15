from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Set

from backend.server.jobs.universal_knowledge_orchestrator import create_universal_knowledge_job


DATA_ROOT = Path("backend/server/data")


def _safe_workspace_id_v1(workspace_id: str) -> str:
    return str(workspace_id or "").strip().replace("/", "_").replace("\\", "_")


def _site_pages_path_v1(workspace_id: str) -> Path:
    return DATA_ROOT / f"site_pages_{_safe_workspace_id_v1(workspace_id)}.json"


def _raw_html_store_path_v1(workspace_id: str) -> Path:
    return DATA_ROOT / "raw_website_html" / f"raw_website_html_{_safe_workspace_id_v1(workspace_id)}.json"


def _extract_url_v1(page: Any) -> str:
    if isinstance(page, str):
        return page.strip()
    if isinstance(page, dict):
        return str(
            page.get("url")
            or page.get("loc")
            or page.get("canonical_url")
            or page.get("source_url")
            or ""
        ).strip()
    return ""


def _html_id_for_url_v1(url: str) -> str:
    digest = hashlib.sha256(str(url or "").strip().encode("utf-8")).hexdigest()[:16]
    return f"raw_html_{digest}"


def _load_site_pages_v1(workspace_id: str) -> List[Dict[str, Any]]:
    path = _site_pages_path_v1(workspace_id)
    data = json.loads(path.read_text(encoding="utf-8"))

    pages = data.get("items") or data.get("pages") or data.get("urls") or []
    if isinstance(pages, dict):
        pages = list(pages.values())

    out = []
    for item in pages:
        url = _extract_url_v1(item)
        if url:
            if isinstance(item, dict):
                row = dict(item)
                row["url"] = url
            else:
                row = {"url": url}
            row["html_id"] = _html_id_for_url_v1(url)
            out.append(row)

    return out


def _existing_raw_html_ids_v1(workspace_id: str) -> Set[str]:
    path = _raw_html_store_path_v1(workspace_id)
    if not path.exists():
        return set()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return set()

    pages = data.get("pages") or {}
    if isinstance(pages, dict):
        return set(pages.keys())

    return set()


def create_raw_html_acquisition_batch_jobs_v1(
    *,
    workspace_id: str,
    batch_size: int = 100,
    checkpoint_every: int = 25,
    sleep_seconds: float = 0.15,
    max_batches: int | None = None,
) -> Dict[str, Any]:
    """
    Fan-out orchestrator for website Raw HTML acquisition.

    Reads Site Pages, subtracts already-acquired Raw HTML records,
    splits remaining URLs into batches, and creates queued jobs.

    Workers should process assigned_urls only.
    Workers should not create successor jobs.
    """

    pages = _load_site_pages_v1(workspace_id)
    existing_ids = _existing_raw_html_ids_v1(workspace_id)

    remaining = [
        page for page in pages
        if page.get("html_id") not in existing_ids
    ]

    batches = [
        remaining[i:i + int(batch_size)]
        for i in range(0, len(remaining), int(batch_size))
    ]

    if max_batches is not None:
        batches = batches[: int(max_batches)]

    created_jobs = []
    batch_group_id = "raw_html_batch_" + hashlib.sha256(
        f"{workspace_id}:{len(pages)}:{len(existing_ids)}:{len(remaining)}".encode("utf-8")
    ).hexdigest()[:16]

    for index, batch in enumerate(batches, start=1):
        job = create_universal_knowledge_job(
            workspace_id=workspace_id,
            job_type="raw_html_acquisition",
            payload={
                "workspace_id": workspace_id,
                "mode": "assigned_urls",
                "assigned_urls": [page["url"] for page in batch],
                "assigned_count": len(batch),
                "batch_index": index,
                "batch_count": len(batches),
                "batch_size": int(batch_size),
                "checkpoint_every": int(checkpoint_every),
                "sleep_seconds": float(sleep_seconds),
                "auto_continue": False,
                "trigger": "raw_html_fanout_orchestrator",
            },
            batch_id=batch_group_id,
        )
        created_jobs.append({
            "job_id": job.get("job_id"),
            "batch_index": index,
            "assigned_count": len(batch),
        })

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "site_pages_count": len(pages),
        "existing_raw_html_count": len(existing_ids),
        "remaining_raw_html_count": len(remaining),
        "batch_size": int(batch_size),
        "batch_count": len(batches),
        "created_job_count": len(created_jobs),
        "batch_group_id": batch_group_id,
        "created_jobs": created_jobs[:50],
    }
