"""
Site Pages artifact repository.

Responsibility:
- persist a normalized SitePagesResult payload
- read a Site Pages artifact
- preserve workspace-specific isolation

No transformation or downstream processing occurs here.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


DEFAULT_DATA_ROOT = Path(
    "backend/server/data"
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


def site_pages_path(
    workspace_id: str,
    *,
    data_root: Path = DEFAULT_DATA_ROOT,
) -> Path:
    safe_workspace_id = _safe_workspace_id(
        workspace_id
    )

    return (
        Path(data_root)
        / f"site_pages_{safe_workspace_id}.json"
    )


def save_site_pages_result(
    result,
    *,
    data_root: Path = DEFAULT_DATA_ROOT,
) -> Path:
    payload = result.to_payload()

    destination = site_pages_path(
        result.workspace_id,
        data_root=data_root,
    )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    serialized = json.dumps(
        payload,
        indent=2,
        ensure_ascii=False,
        sort_keys=False,
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


def load_site_pages_payload(
    workspace_id: str,
    *,
    data_root: Path = DEFAULT_DATA_ROOT,
) -> dict[str, Any]:
    source = site_pages_path(
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
            "Site Pages artifact must be "
            "a JSON object"
        )

    pages = payload.get("pages")

    if not isinstance(pages, list):
        raise ValueError(
            "Site Pages payload.pages must "
            "be a list"
        )

    return payload
