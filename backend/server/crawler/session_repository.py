"""
LinkCraftor Autonomous Public-Web Crawler
Crawler Session Repository

This module persists canonical CrawlSession records.

Responsibilities:
- workspace-scoped crawler-session storage;
- atomic JSON persistence;
- validated session creation;
- session retrieval;
- session updates;
- session listing;
- session deletion;
- duplicate-session protection;
- corruption-aware reads.

This module does not:
- create crawler-session lifecycle transitions;
- start or stop crawler workers;
- schedule URLs;
- fetch web pages;
- manage the URL frontier;
- coordinate the crawler pipeline.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping

from .session_models import (
    CRAWLER_SESSION_SCHEMA_VERSION,
    CrawlSession,
    required_string,
)


CRAWLER_SESSION_REPOSITORY_SCHEMA_VERSION = (
    "crawler_session_repository.v1"
)

DATA_ROOT = Path("backend/server/data")
CRAWLER_DATA_ROOT = DATA_ROOT / "crawler"
CRAWLER_SESSION_STORE_ROOT = (
    CRAWLER_DATA_ROOT / "sessions"
)


def utc_now_iso() -> str:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(
        timezone.utc
    ).isoformat()


def safe_storage_identifier(
    value: Any,
    *,
    field_name: str,
) -> str:
    """
    Validate and normalize an identifier for filesystem use.

    The returned value preserves letters, numbers, underscores,
    and hyphens. Other characters become underscores.
    """

    cleaned = required_string(
        value,
        field_name=field_name,
    )

    safe_value = "".join(
        character
        if (
            character.isalnum()
            or character in ("_", "-")
        )
        else "_"
        for character in cleaned
    )

    safe_value = safe_value.strip("_")

    if not safe_value:
        raise ValueError(
            f"{field_name} does not contain a valid "
            "storage identifier."
        )

    return safe_value


def crawler_session_store_path(
    workspace_id: str,
) -> Path:
    """Return the canonical session-store path for a workspace."""

    safe_workspace_id = safe_storage_identifier(
        workspace_id,
        field_name="workspace_id",
    )

    CRAWLER_SESSION_STORE_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        CRAWLER_SESSION_STORE_ROOT
        / (
            "crawler_sessions_"
            f"{safe_workspace_id}.json"
        )
    )


def empty_crawler_session_store(
    workspace_id: str,
) -> Dict[str, Any]:
    """Create an empty canonical crawler-session store."""

    clean_workspace_id = required_string(
        workspace_id,
        field_name="workspace_id",
    )

    now = utc_now_iso()

    return {
        "schema_version": (
            CRAWLER_SESSION_REPOSITORY_SCHEMA_VERSION
        ),
        "crawler_session_schema_version": (
            CRAWLER_SESSION_SCHEMA_VERSION
        ),
        "workspace_id": clean_workspace_id,
        "sessions": {},
        "created_at": now,
        "updated_at": now,
    }


def validate_crawler_session_store(
    store: Mapping[str, Any],
    *,
    workspace_id: str,
) -> Dict[str, Any]:
    """Validate and normalize a loaded repository document."""

    if not isinstance(store, Mapping):
        raise ValueError(
            "Crawler session store root must be "
            "a JSON object."
        )

    normalized = dict(store)

    stored_workspace_id = required_string(
        normalized.get("workspace_id"),
        field_name="store.workspace_id",
    )

    expected_workspace_id = required_string(
        workspace_id,
        field_name="workspace_id",
    )

    if stored_workspace_id != expected_workspace_id:
        raise ValueError(
            "Crawler session store workspace does not "
            "match the requested workspace."
        )

    sessions = normalized.get("sessions")

    if not isinstance(sessions, dict):
        raise ValueError(
            "Crawler session store sessions field must "
            "be a JSON object."
        )

    repository_schema = required_string(
        normalized.get("schema_version"),
        field_name="store.schema_version",
    )

    if (
        repository_schema
        != CRAWLER_SESSION_REPOSITORY_SCHEMA_VERSION
    ):
        raise ValueError(
            "Unsupported crawler session repository "
            f"schema: {repository_schema}"
        )

    session_schema = required_string(
        normalized.get(
            "crawler_session_schema_version"
        ),
        field_name=(
            "store.crawler_session_schema_version"
        ),
    )

    if session_schema != CRAWLER_SESSION_SCHEMA_VERSION:
        raise ValueError(
            "Unsupported crawler session model schema: "
            f"{session_schema}"
        )

    validated_sessions: Dict[str, Dict[str, Any]] = {}

    for session_id, session_payload in sessions.items():
        if not isinstance(session_payload, Mapping):
            raise ValueError(
                "Crawler session repository contains a "
                "non-object session record."
            )

        session = CrawlSession.from_dict(
            session_payload
        )

        if session.crawl_session_id != str(session_id):
            raise ValueError(
                "Crawler session repository key does not "
                "match its record identity."
            )

        if session.workspace_id != expected_workspace_id:
            raise ValueError(
                "Crawler session record belongs to a "
                "different workspace."
            )

        validated_sessions[
            session.crawl_session_id
        ] = session.to_dict()

    normalized["sessions"] = validated_sessions

    normalized.setdefault(
        "created_at",
        utc_now_iso(),
    )
    normalized.setdefault(
        "updated_at",
        utc_now_iso(),
    )

    return normalized


def load_crawler_session_store(
    workspace_id: str,
) -> Dict[str, Any]:
    """
    Load and validate one workspace's crawler-session store.

    The reader retries transient filesystem and partial-write errors
    three times before raising RuntimeError.
    """

    path = crawler_session_store_path(
        workspace_id
    )

    if not path.exists():
        return empty_crawler_session_store(
            workspace_id
        )

    last_error: Exception | None = None

    for attempt in range(1, 4):
        try:
            raw_text = path.read_text(
                encoding="utf-8"
            )

            raw_store = json.loads(
                raw_text
            )

            return validate_crawler_session_store(
                raw_store,
                workspace_id=workspace_id,
            )

        except (
            OSError,
            UnicodeError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ) as exc:
            last_error = exc

            if attempt < 3:
                time.sleep(
                    0.05 * attempt
                )

    raise RuntimeError(
        "Unable to read a valid crawler session "
        f"store after 3 attempts: {path}. "
        "Underlying error: "
        f"{type(last_error).__name__}: "
        f"{last_error}"
    ) from last_error


def save_crawler_session_store(
    workspace_id: str,
    store: Mapping[str, Any],
) -> Path:
    """
    Validate and atomically save a crawler-session store.

    The destination file is replaced only after the complete JSON
    document has been written and flushed successfully.
    """

    path = crawler_session_store_path(
        workspace_id
    )

    validated_store = (
        validate_crawler_session_store(
            store,
            workspace_id=workspace_id,
        )
    )

    validated_store["updated_at"] = (
        utc_now_iso()
    )

    serialized = json.dumps(
        validated_store,
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


def create_crawler_session(
    session: CrawlSession,
    *,
    overwrite: bool = False,
) -> CrawlSession:
    """
    Persist a new crawler session.

    Duplicate identities are rejected unless overwrite=True is
    explicitly supplied.
    """

    if not isinstance(session, CrawlSession):
        raise ValueError(
            "session must be a CrawlSession instance."
        )

    store = load_crawler_session_store(
        session.workspace_id
    )

    sessions = store.setdefault(
        "sessions",
        {},
    )

    if (
        session.crawl_session_id in sessions
        and not overwrite
    ):
        raise ValueError(
            "Crawler session already exists: "
            f"{session.crawl_session_id}"
        )

    sessions[
        session.crawl_session_id
    ] = session.to_dict()

    save_crawler_session_store(
        session.workspace_id,
        store,
    )

    return CrawlSession.from_dict(
        sessions[
            session.crawl_session_id
        ]
    )


def update_crawler_session(
    session: CrawlSession,
    *,
    create_if_missing: bool = False,
) -> CrawlSession:
    """
    Replace an existing crawler-session record.

    The lifecycle manager will later modify the model before calling
    this repository function.
    """

    if not isinstance(session, CrawlSession):
        raise ValueError(
            "session must be a CrawlSession instance."
        )

    store = load_crawler_session_store(
        session.workspace_id
    )

    sessions = store.setdefault(
        "sessions",
        {},
    )

    exists = (
        session.crawl_session_id
        in sessions
    )

    if not exists and not create_if_missing:
        raise KeyError(
            "Crawler session does not exist: "
            f"{session.crawl_session_id}"
        )

    sessions[
        session.crawl_session_id
    ] = session.to_dict()

    save_crawler_session_store(
        session.workspace_id,
        store,
    )

    return CrawlSession.from_dict(
        sessions[
            session.crawl_session_id
        ]
    )


def get_crawler_session(
    *,
    workspace_id: str,
    crawl_session_id: str,
) -> CrawlSession | None:
    """Return one crawler session or None when it does not exist."""

    clean_session_id = required_string(
        crawl_session_id,
        field_name="crawl_session_id",
    )

    store = load_crawler_session_store(
        workspace_id
    )

    payload = store.get(
        "sessions",
        {},
    ).get(
        clean_session_id
    )

    if payload is None:
        return None

    return CrawlSession.from_dict(
        payload
    )


def require_crawler_session(
    *,
    workspace_id: str,
    crawl_session_id: str,
) -> CrawlSession:
    """Return one crawler session or raise KeyError."""

    session = get_crawler_session(
        workspace_id=workspace_id,
        crawl_session_id=crawl_session_id,
    )

    if session is None:
        raise KeyError(
            "Crawler session does not exist: "
            f"{crawl_session_id}"
        )

    return session


def list_crawler_sessions(
    *,
    workspace_id: str,
) -> List[CrawlSession]:
    """
    Return all crawler sessions for a workspace.

    Records are ordered newest first using created_at.
    """

    store = load_crawler_session_store(
        workspace_id
    )

    sessions = [
        CrawlSession.from_dict(
            payload
        )
        for payload in store.get(
            "sessions",
            {},
        ).values()
    ]

    return sorted(
        sessions,
        key=lambda session: (
            session.created_at,
            session.crawl_session_id,
        ),
        reverse=True,
    )


def crawler_session_exists(
    *,
    workspace_id: str,
    crawl_session_id: str,
) -> bool:
    """Return True when the crawler-session identity exists."""

    return (
        get_crawler_session(
            workspace_id=workspace_id,
            crawl_session_id=crawl_session_id,
        )
        is not None
    )


def count_crawler_sessions(
    *,
    workspace_id: str,
) -> int:
    """Return the number of crawler sessions in one workspace."""

    store = load_crawler_session_store(
        workspace_id
    )

    return len(
        store.get(
            "sessions",
            {},
        )
    )


def delete_crawler_session(
    *,
    workspace_id: str,
    crawl_session_id: str,
    missing_ok: bool = False,
) -> bool:
    """
    Delete one crawler-session repository record.

    Operational retention policy may later restrict when this
    function can be called.
    """

    clean_session_id = required_string(
        crawl_session_id,
        field_name="crawl_session_id",
    )

    store = load_crawler_session_store(
        workspace_id
    )

    sessions = store.setdefault(
        "sessions",
        {},
    )

    if clean_session_id not in sessions:
        if missing_ok:
            return False

        raise KeyError(
            "Crawler session does not exist: "
            f"{clean_session_id}"
        )

    del sessions[
        clean_session_id
    ]

    save_crawler_session_store(
        workspace_id,
        store,
    )

    return True


def explain_crawler_session_repository_v1() -> Dict[str, Any]:
    """Return an inspectable repository contract description."""

    return {
        "ok": True,
        "component": "crawler_session_repository",
        "schema_version": (
            CRAWLER_SESSION_REPOSITORY_SCHEMA_VERSION
        ),
        "session_schema_version": (
            CRAWLER_SESSION_SCHEMA_VERSION
        ),
        "storage_root": str(
            CRAWLER_SESSION_STORE_ROOT
        ),
        "storage_scope": "workspace",
        "persistence_format": "json",
        "atomic_write": True,
        "read_retry_attempts": 3,
        "responsibilities": [
            "persist crawler session records",
            "isolate crawler sessions by workspace",
            "validate repository documents",
            "create crawler session records",
            "retrieve crawler session records",
            "update crawler session records",
            "list crawler session records",
            "count crawler session records",
            "delete crawler session records",
            "reject duplicate session identities",
            "detect corrupt repository documents",
        ],
        "excluded_responsibilities": [
            "crawler session lifecycle transitions",
            "crawler session identity generation",
            "URL frontier management",
            "crawl scheduling",
            "web page fetching",
            "worker execution",
            "left-arm handoff",
        ],
    }


__all__ = [
    "CRAWLER_SESSION_REPOSITORY_SCHEMA_VERSION",
    "CRAWLER_SESSION_STORE_ROOT",
    "count_crawler_sessions",
    "crawler_session_exists",
    "crawler_session_store_path",
    "create_crawler_session",
    "delete_crawler_session",
    "empty_crawler_session_store",
    "explain_crawler_session_repository_v1",
    "get_crawler_session",
    "list_crawler_sessions",
    "load_crawler_session_store",
    "require_crawler_session",
    "safe_storage_identifier",
    "save_crawler_session_store",
    "update_crawler_session",
    "validate_crawler_session_store",
]
