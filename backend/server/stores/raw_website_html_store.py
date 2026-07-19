from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DATA_ROOT = Path("backend/server/data")
STORE_DIR = DATA_ROOT / "raw_website_html"


def _safe_workspace_id_v1(workspace_id: str) -> str:
    return "".join(
        c if c.isalnum() or c in ("_", "-") else "_"
        for c in str(workspace_id or "default")
    )


def html_id_for_url_v1(url: str) -> str:
    digest = hashlib.sha256(str(url or "").strip().encode("utf-8")).hexdigest()[:16]
    return f"raw_html_{digest}"


def _store_path_v1(workspace_id: str) -> Path:
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    return STORE_DIR / f"raw_website_html_{_safe_workspace_id_v1(workspace_id)}.json"


def load_raw_website_html_store_v1(workspace_id: str) -> Dict[str, Any]:
    path = _store_path_v1(workspace_id)

    if not path.exists():
        return {
            "version": "raw_website_html_store_v1",
            "workspace_id": workspace_id,
            "pages": {},
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    last_error: Exception | None = None

    for attempt in range(1, 4):
        try:
            raw_text = path.read_text(
                encoding="utf-8"
            )

            store = json.loads(
                raw_text
            )

            if not isinstance(store, dict):
                raise ValueError(
                    "Raw HTML store root must be a JSON object."
                )

            pages = store.get("pages")

            if not isinstance(pages, dict):
                raise ValueError(
                    "Raw HTML store pages field must be a JSON object."
                )

            return store

        except (
            OSError,
            UnicodeError,
            json.JSONDecodeError,
            ValueError,
        ) as exc:
            last_error = exc

            if attempt < 3:
                time.sleep(
                    0.05 * attempt
                )

    raise RuntimeError(
        "Unable to read a valid Raw HTML store after "
        f"3 attempts: {path}. "
        f"Underlying error: "
        f"{type(last_error).__name__}: {last_error}"
    ) from last_error


def save_raw_website_html_store_v1(
    workspace_id: str,
    store: Dict[str, Any],
) -> Path:
    path = _store_path_v1(workspace_id)

    store["updated_at_utc"] = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    serialized = json.dumps(
        store,
        indent=2,
        ensure_ascii=False,
    )

    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=str(path.parent),
            prefix=path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_file.write(
                serialized
            )
            temporary_file.flush()
            os.fsync(
                temporary_file.fileno()
            )

            temporary_path = Path(
                temporary_file.name
            )

        os.replace(
            temporary_path,
            path,
        )

    except Exception:
        if (
            temporary_path is not None
            and temporary_path.exists()
        ):
            temporary_path.unlink(
                missing_ok=True
            )

        raise

    return path


def upsert_raw_website_html_v1(
    *,
    workspace_id: str,
    url: str,
    html: str,
    title: str = "",
    status_code: int | None = None,
    content_type: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    store = load_raw_website_html_store_v1(workspace_id)

    html_id = html_id_for_url_v1(url)
    now = datetime.now(timezone.utc).isoformat()

    record = {
        "html_id": html_id,
        "workspace_id": workspace_id,
        "url": url,
        "title": title,
        "html": str(html or ""),
        "html_length": len(str(html or "")),
        "status_code": status_code,
        "content_type": content_type,
        "metadata": metadata or {},
        "captured_at_utc": now,
        "source_type": "raw_website_html",
    }

    store.setdefault("pages", {})
    store["pages"][html_id] = record

    save_raw_website_html_store_v1(workspace_id, store)

    return record


def get_raw_website_html_v1(
    *,
    workspace_id: str,
    url: str | None = None,
    html_id: str | None = None,
) -> Dict[str, Any] | None:
    store = load_raw_website_html_store_v1(workspace_id)

    if html_id:
        return store.get("pages", {}).get(html_id)

    if url:
        return store.get("pages", {}).get(html_id_for_url_v1(url))

    return None
