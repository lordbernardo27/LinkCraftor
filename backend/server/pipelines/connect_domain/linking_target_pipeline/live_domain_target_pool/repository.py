"""
Live Domain Target Pool repository.

Persists and reloads the basic live-domain target pool only.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


DEFAULT_DATA_ROOT = Path(
    "backend/server/data/target_pools/live_domain"
)


def _safe_workspace_id(
    workspace_id: str,
) -> str:
    value = str(
        workspace_id
        or ""
    ).strip()

    if not value:
        raise ValueError(
            "workspace_id is required"
        )

    safe = "".join(
        character
        if (
            character.isalnum()
            or character in {"_", "-"}
        )
        else "_"
        for character in value
    )

    if not safe:
        raise ValueError(
            "workspace_id is invalid"
        )

    return safe


def live_domain_target_pool_path(
    workspace_id: str,
    *,
    data_root: Path = DEFAULT_DATA_ROOT,
) -> Path:
    safe_workspace_id = _safe_workspace_id(
        workspace_id
    )

    return (
        Path(data_root)
        / (
            "live_domain_target_pool_"
            f"{safe_workspace_id}.json"
        )
    )


def save_live_domain_target_pool(
    result,
    *,
    data_root: Path = DEFAULT_DATA_ROOT,
) -> Path:
    destination = (
        live_domain_target_pool_path(
            result.workspace_id,
            data_root=data_root,
        )
    )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    serialized = json.dumps(
        result.to_payload(),
        indent=2,
        ensure_ascii=False,
    ) + "\n"

    with NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=destination.parent,
        prefix=destination.name + ".",
        suffix=".tmp",
        delete=False,
    ) as temporary:
        temporary.write(serialized)
        temporary_path = Path(
            temporary.name
        )

    os.replace(
        temporary_path,
        destination,
    )

    return destination


def load_live_domain_target_pool(
    workspace_id: str,
    *,
    data_root: Path = DEFAULT_DATA_ROOT,
) -> dict[str, Any]:
    source = live_domain_target_pool_path(
        workspace_id,
        data_root=data_root,
    )

    if not source.exists():
        raise FileNotFoundError(source)

    payload = json.loads(
        source.read_text(
            encoding="utf-8-sig"
        )
    )

    if not isinstance(payload, dict):
        raise ValueError(
            "Live Domain Target Pool artifact "
            "must be a JSON object"
        )

    items = payload.get("items")

    if not isinstance(items, list):
        raise ValueError(
            "Live Domain Target Pool items "
            "must be a list"
        )

    return payload
