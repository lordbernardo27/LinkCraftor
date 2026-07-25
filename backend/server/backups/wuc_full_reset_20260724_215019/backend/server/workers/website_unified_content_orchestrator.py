from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Set

from backend.server.jobs.universal_knowledge_orchestrator import (
    create_universal_knowledge_job,
)


DATA_ROOT = Path("backend/server/data")


def _safe_workspace_id_v1(
    workspace_id: str,
) -> str:
    return "".join(
        character
        if (
            character.isalnum()
            or character in ("_", "-")
        )
        else "_"
        for character in str(
            workspace_id or "default"
        )
    )


def _raw_store_path_v1(
    workspace_id: str,
) -> Path:
    workspace = _safe_workspace_id_v1(
        workspace_id
    )

    return (
        DATA_ROOT
        / "raw_website_html"
        / f"raw_website_html_{workspace}.json"
    )


def _website_store_path_v1(
    workspace_id: str,
) -> Path:
    workspace = _safe_workspace_id_v1(
        workspace_id
    )

    return (
        DATA_ROOT
        / "website_unified_content"
        / f"website_unified_content_{workspace}.json"
    )


def _content_id_for_url_v1(
    url: str,
) -> str:
    digest = hashlib.sha256(
        str(url or "")
        .strip()
        .encode("utf-8")
    ).hexdigest()[:16]

    return f"web_content_{digest}"


def _existing_content_ids_v1(
    workspace_id: str,
) -> Set[str]:
    path = _website_store_path_v1(
        workspace_id
    )

    if not path.exists():
        return set()

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        return set()

    documents = data.get("documents") or {}

    return (
        set(documents.keys())
        if isinstance(documents, dict)
        else set()
    )


def create_website_unified_content_batch_jobs_v1(
    *,
    workspace_id: str,
    batch_size: int = 50,
    max_batches: int | None = None,
) -> Dict[str, Any]:
    """
    Raw HTML Store
    -> WUC batch jobs
    -> UUCD batch jobs
    """

    raw_path = _raw_store_path_v1(
        workspace_id
    )

    if not raw_path.exists():
        raise FileNotFoundError(
            f"Raw HTML Store not found: {raw_path}"
        )

    raw_store = json.loads(
        raw_path.read_text(
            encoding="utf-8"
        )
    )

    raw_pages = raw_store.get("pages") or {}

    existing_content_ids = (
        _existing_content_ids_v1(
            workspace_id
        )
    )

    remaining_html_ids: List[str] = []

    for html_id, record in raw_pages.items():
        if not isinstance(record, dict):
            continue

        url = str(
            record.get("url") or ""
        ).strip()

        raw_html = str(
            record.get("html") or ""
        )

        if not url or not raw_html.strip():
            continue

        content_id = _content_id_for_url_v1(
            url
        )

        if content_id not in existing_content_ids:
            remaining_html_ids.append(
                str(html_id)
            )

    batches = [
        remaining_html_ids[
            index:index + int(batch_size)
        ]
        for index in range(
            0,
            len(remaining_html_ids),
            int(batch_size),
        )
    ]

    if max_batches is not None:
        batches = batches[
            :int(max_batches)
        ]

    batch_group_id = (
        "website_content_batch_"
        + hashlib.sha256(
            (
                f"{workspace_id}:"
                f"{len(raw_pages)}:"
                f"{len(existing_content_ids)}:"
                f"{len(remaining_html_ids)}"
            ).encode("utf-8")
        ).hexdigest()[:16]
    )

    created_jobs = []

    for index, html_ids in enumerate(
        batches,
        start=1,
    ):
        job = create_universal_knowledge_job(
            workspace_id=workspace_id,
            job_type=
                "build_website_unified_content",
            payload={
                "workspace_id":
                    workspace_id,
                "mode":
                    "assigned_raw_html_ids",
                "assigned_html_ids":
                    html_ids,
                "assigned_count":
                    len(html_ids),
                "batch_index":
                    index,
                "batch_count":
                    len(batches),
                "batch_id":
                    batch_group_id,
                "trigger":
                    "website_content_fanout_orchestrator",
                "source_stage":
                    "raw_website_html_store",
                "html_cleaner_used":
                    False,
            },
            batch_id=batch_group_id,
        )

        created_jobs.append({
            "job_id":
                job.get("job_id"),
            "batch_index":
                index,
            "assigned_count":
                len(html_ids),
        })

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "input_store":
            "raw_website_html_store_v1",
        "raw_html_count":
            len(raw_pages),
        "existing_website_content_count":
            len(existing_content_ids),
        "remaining_website_content_count":
            len(remaining_html_ids),
        "batch_size":
            int(batch_size),
        "batch_count":
            len(batches),
        "created_job_count":
            len(created_jobs),
        "batch_group_id":
            batch_group_id,
        "created_jobs":
            created_jobs[:100],
        "html_cleaner_used":
            False,
        "clean_html_store_used":
            False,
    }
