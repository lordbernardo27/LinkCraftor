"""Repository for the canonical Active Target Set."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from .stage import ActiveTargetSetResult


DATA_ROOT = Path(
    "backend/server/data/target_pools"
)


def _safe_workspace_id(
    workspace_id: str,
) -> str:
    safe = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        str(workspace_id or "").strip(),
    ).strip("_")

    if not safe:
        raise ValueError(
            "workspace_id is required"
        )

    return safe


def active_target_set_path(
    workspace_id: str,
) -> Path:
    workspace = _safe_workspace_id(
        workspace_id
    )

    return (
        DATA_ROOT
        / f"active_target_set_{workspace}.json"
    )


def save_active_target_set(
    result: ActiveTargetSetResult,
    *,
    generated_at: str | None = None,
) -> Path:
    timestamp = (
        str(generated_at).strip()
        if generated_at
        else datetime.now(
            timezone.utc
        ).isoformat()
    )

    payload = result.to_dict(
        generated_at=timestamp
    )

    path = active_target_set_path(
        result.workspace_id
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = path.with_suffix(
        ".json.tmp"
    )

    temporary_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    temporary_path.replace(path)

    return path


def load_active_target_set(
    workspace_id: str,
) -> Dict[str, Any]:
    path = active_target_set_path(
        workspace_id
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Active Target Set not found: {path}"
        )

    payload = json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )

    if not isinstance(payload, dict):
        raise ValueError(
            "Active Target Set payload must be an object"
        )

    expected_workspace = _safe_workspace_id(
        workspace_id
    )

    stored_workspace = str(
        payload.get("workspace_id")
        or ""
    ).strip()

    if stored_workspace != expected_workspace:
        raise ValueError(
            "Active Target Set workspace mismatch"
        )

    return payload


def load_optional_source_payload(
    path: Path,
) -> Mapping[str, Any]:
    if not path.exists():
        return {}

    payload = json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )

    if not isinstance(payload, dict):
        raise ValueError(
            f"Source payload must be an object: {path}"
        )

    return payload
