"""
LinkCraftor Autonomous Public-Web Crawler
Universal Web Seed Registry Repository

This module persists canonical UniversalWebSeed records.

Responsibilities:
- workspace-scoped seed storage;
- atomic JSON persistence;
- repository-document validation;
- seed-model schema validation;
- seed identity integrity;
- workspace isolation;
- seed creation and replacement;
- seed retrieval;
- filtered seed listing;
- filtered seed counting;
- low-level physical seed deletion;
- corruption-aware reads.

This module does not:
- generate seed identities;
- orchestrate seed registration;
- enable, disable, or archive seeds;
- detect duplicate seed targets;
- determine seed eligibility;
- normalize URLs or domains;
- parse sitemaps or feeds;
- insert URLs into the Crawl Frontier;
- schedule or execute crawler work.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping

from .seed_models import (
    UNIVERSAL_WEB_SEED_SCHEMA_VERSION,
    UniversalWebSeed,
    UniversalWebSeedStatus,
    UniversalWebSeedType,
    normalize_seed_status,
    normalize_seed_type,
)
from .session_models import required_string
from .session_repository import safe_storage_identifier


UNIVERSAL_WEB_SEED_REPOSITORY_SCHEMA_VERSION = (
    "universal_web_seed_repository.v1"
)

DATA_ROOT = Path("backend/server/data")
CRAWLER_DATA_ROOT = DATA_ROOT / "crawler"
UNIVERSAL_WEB_SEED_STORE_ROOT = (
    CRAWLER_DATA_ROOT / "seeds"
)


def utc_now_iso() -> str:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(
        timezone.utc
    ).isoformat()


def universal_web_seed_store_path(
    workspace_id: str,
) -> Path:
    """Return the canonical seed-store path for one workspace."""

    safe_workspace_id = safe_storage_identifier(
        workspace_id,
        field_name="workspace_id",
    )

    UNIVERSAL_WEB_SEED_STORE_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        UNIVERSAL_WEB_SEED_STORE_ROOT
        / (
            "universal_web_seeds_"
            f"{safe_workspace_id}.json"
        )
    )


def empty_universal_web_seed_store(
    workspace_id: str,
) -> Dict[str, Any]:
    """Create an empty canonical seed repository document."""

    clean_workspace_id = required_string(
        workspace_id,
        field_name="workspace_id",
    )

    now = utc_now_iso()

    return {
        "schema_version": (
            UNIVERSAL_WEB_SEED_REPOSITORY_SCHEMA_VERSION
        ),
        "seed_schema_version": (
            UNIVERSAL_WEB_SEED_SCHEMA_VERSION
        ),
        "workspace_id": clean_workspace_id,
        "seeds": {},
        "created_at": now,
        "updated_at": now,
    }


def validate_universal_web_seed_store(
    store: Mapping[str, Any],
    *,
    workspace_id: str,
) -> Dict[str, Any]:
    """
    Validate and normalize one seed repository document.

    Every repository key must match its seed record identity, and every
    stored seed must belong to the requested workspace.
    """

    if not isinstance(store, Mapping):
        raise ValueError(
            "Universal Web Seed store root must be "
            "a JSON object."
        )

    normalized = dict(store)

    expected_workspace_id = required_string(
        workspace_id,
        field_name="workspace_id",
    )

    stored_workspace_id = required_string(
        normalized.get("workspace_id"),
        field_name="store.workspace_id",
    )

    if stored_workspace_id != expected_workspace_id:
        raise ValueError(
            "Universal Web Seed store workspace does not "
            "match the requested workspace."
        )

    repository_schema = required_string(
        normalized.get("schema_version"),
        field_name="store.schema_version",
    )

    if (
        repository_schema
        != UNIVERSAL_WEB_SEED_REPOSITORY_SCHEMA_VERSION
    ):
        raise ValueError(
            "Unsupported Universal Web Seed repository "
            f"schema: {repository_schema}"
        )

    seed_schema = required_string(
        normalized.get("seed_schema_version"),
        field_name="store.seed_schema_version",
    )

    if seed_schema != UNIVERSAL_WEB_SEED_SCHEMA_VERSION:
        raise ValueError(
            "Unsupported Universal Web Seed model schema: "
            f"{seed_schema}"
        )

    seeds = normalized.get("seeds")

    if not isinstance(seeds, dict):
        raise ValueError(
            "Universal Web Seed store seeds field must "
            "be a JSON object."
        )

    validated_seeds: Dict[str, Dict[str, Any]] = {}

    for repository_seed_id, seed_payload in seeds.items():
        if not isinstance(seed_payload, Mapping):
            raise ValueError(
                "Universal Web Seed repository contains "
                "a non-object seed record."
            )

        seed = UniversalWebSeed.from_dict(
            seed_payload
        )

        if seed.seed_id != str(repository_seed_id):
            raise ValueError(
                "Universal Web Seed repository key does "
                "not match its record identity."
            )

        if seed.workspace_id != expected_workspace_id:
            raise ValueError(
                "Universal Web Seed record belongs to "
                "a different workspace."
            )

        validated_seeds[
            seed.seed_id
        ] = seed.to_dict()

    normalized["seeds"] = validated_seeds

    normalized.setdefault(
        "created_at",
        utc_now_iso(),
    )
    normalized.setdefault(
        "updated_at",
        utc_now_iso(),
    )

    return normalized


def load_universal_web_seed_store(
    workspace_id: str,
) -> Dict[str, Any]:
    """
    Load and validate one workspace's seed repository.

    Missing repositories return a new empty repository document.
    Existing invalid repositories are retried three times before a
    RuntimeError is raised.
    """

    path = universal_web_seed_store_path(
        workspace_id
    )

    if not path.exists():
        return empty_universal_web_seed_store(
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

            return validate_universal_web_seed_store(
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
        "Unable to read a valid Universal Web Seed "
        f"store after 3 attempts: {path}. "
        "Underlying error: "
        f"{type(last_error).__name__}: "
        f"{last_error}"
    ) from last_error


def save_universal_web_seed_store(
    workspace_id: str,
    store: Mapping[str, Any],
) -> Path:
    """
    Validate and atomically save one seed repository document.

    The final file is replaced only after the complete JSON document
    has been written, flushed, and synchronized.
    """

    path = universal_web_seed_store_path(
        workspace_id
    )

    validated_store = (
        validate_universal_web_seed_store(
            store,
            workspace_id=workspace_id,
        )
    )

    validated_store["updated_at"] = utc_now_iso()

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

        replace_attempts = 5
        replace_delay_seconds = 0.05

        for replace_attempt in range(
            1,
            replace_attempts + 1,
        ):
            try:
                os.replace(
                    temporary_path,
                    path,
                )
                break
            except PermissionError:
                if replace_attempt >= replace_attempts:
                    raise

                time.sleep(
                    replace_delay_seconds
                    * replace_attempt
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


def create_universal_web_seed(
    seed: UniversalWebSeed,
    *,
    overwrite: bool = False,
) -> UniversalWebSeed:
    """
    Persist a Universal Web Seed record.

    Existing seed identities are rejected unless overwrite=True is
    explicitly supplied.
    """

    if not isinstance(seed, UniversalWebSeed):
        raise ValueError(
            "seed must be a UniversalWebSeed instance."
        )

    store = load_universal_web_seed_store(
        seed.workspace_id
    )

    seeds = store.setdefault(
        "seeds",
        {},
    )

    if (
        seed.seed_id in seeds
        and not overwrite
    ):
        raise ValueError(
            "Universal Web Seed already exists: "
            f"{seed.seed_id}"
        )

    seeds[
        seed.seed_id
    ] = seed.to_dict()

    save_universal_web_seed_store(
        seed.workspace_id,
        store,
    )

    return UniversalWebSeed.from_dict(
        seeds[
            seed.seed_id
        ]
    )


def update_universal_web_seed(
    seed: UniversalWebSeed,
    *,
    create_if_missing: bool = False,
) -> UniversalWebSeed:
    """
    Replace an existing Universal Web Seed record.

    Lifecycle transitions are performed by the later Seed Controls
    component before this repository operation is called.
    """

    if not isinstance(seed, UniversalWebSeed):
        raise ValueError(
            "seed must be a UniversalWebSeed instance."
        )

    store = load_universal_web_seed_store(
        seed.workspace_id
    )

    seeds = store.setdefault(
        "seeds",
        {},
    )

    exists = seed.seed_id in seeds

    if not exists and not create_if_missing:
        raise KeyError(
            "Universal Web Seed does not exist: "
            f"{seed.seed_id}"
        )

    seeds[
        seed.seed_id
    ] = seed.to_dict()

    save_universal_web_seed_store(
        seed.workspace_id,
        store,
    )

    return UniversalWebSeed.from_dict(
        seeds[
            seed.seed_id
        ]
    )


def get_universal_web_seed(
    *,
    workspace_id: str,
    seed_id: str,
) -> UniversalWebSeed | None:
    """Return one seed or None when it does not exist."""

    clean_seed_id = required_string(
        seed_id,
        field_name="seed_id",
    )

    store = load_universal_web_seed_store(
        workspace_id
    )

    payload = store.get(
        "seeds",
        {},
    ).get(
        clean_seed_id
    )

    if payload is None:
        return None

    return UniversalWebSeed.from_dict(
        payload
    )


def require_universal_web_seed(
    *,
    workspace_id: str,
    seed_id: str,
) -> UniversalWebSeed:
    """Return one seed or raise KeyError."""

    seed = get_universal_web_seed(
        workspace_id=workspace_id,
        seed_id=seed_id,
    )

    if seed is None:
        raise KeyError(
            "Universal Web Seed does not exist: "
            f"{seed_id}"
        )

    return seed


def normalize_optional_seed_type_filter(
    value: UniversalWebSeedType | str | None,
) -> UniversalWebSeedType | None:
    """Normalize an optional seed-type listing filter."""

    if value is None:
        return None

    return normalize_seed_type(
        value
    )


def normalize_optional_seed_status_filter(
    value: UniversalWebSeedStatus | str | None,
) -> UniversalWebSeedStatus | None:
    """Normalize an optional seed-status listing filter."""

    if value is None:
        return None

    return normalize_seed_status(
        value
    )


def list_universal_web_seeds(
    *,
    workspace_id: str,
    seed_type: UniversalWebSeedType | str | None = None,
    status: UniversalWebSeedStatus | str | None = None,
    enabled: bool | None = None,
    active_only: bool = False,
) -> List[UniversalWebSeed]:
    """
    Return filtered seeds for one workspace.

    Ordering is deterministic:
    1. highest priority first;
    2. oldest registration timestamp first;
    3. seed identity.
    """

    if enabled is not None and not isinstance(
        enabled,
        bool,
    ):
        raise ValueError(
            "enabled filter must be a boolean or None."
        )

    if not isinstance(active_only, bool):
        raise ValueError(
            "active_only must be a boolean."
        )

    normalized_seed_type = (
        normalize_optional_seed_type_filter(
            seed_type
        )
    )

    normalized_status = (
        normalize_optional_seed_status_filter(
            status
        )
    )

    store = load_universal_web_seed_store(
        workspace_id
    )

    seeds = [
        UniversalWebSeed.from_dict(
            payload
        )
        for payload in store.get(
            "seeds",
            {},
        ).values()
    ]

    filtered: List[UniversalWebSeed] = []

    for seed in seeds:
        if (
            normalized_seed_type is not None
            and seed.seed_type
            != normalized_seed_type
        ):
            continue

        if (
            normalized_status is not None
            and seed.status
            != normalized_status
        ):
            continue

        if (
            enabled is not None
            and seed.enabled is not enabled
        ):
            continue

        if active_only and not seed.is_active:
            continue

        filtered.append(
            seed
        )

    return sorted(
        filtered,
        key=lambda seed: (
            -seed.priority,
            seed.registered_at,
            seed.seed_id,
        ),
    )


def universal_web_seed_exists(
    *,
    workspace_id: str,
    seed_id: str,
) -> bool:
    """Return True when the seed identity exists."""

    return (
        get_universal_web_seed(
            workspace_id=workspace_id,
            seed_id=seed_id,
        )
        is not None
    )


def count_universal_web_seeds(
    *,
    workspace_id: str,
    seed_type: UniversalWebSeedType | str | None = None,
    status: UniversalWebSeedStatus | str | None = None,
    enabled: bool | None = None,
    active_only: bool = False,
) -> int:
    """Return the filtered seed count for one workspace."""

    return len(
        list_universal_web_seeds(
            workspace_id=workspace_id,
            seed_type=seed_type,
            status=status,
            enabled=enabled,
            active_only=active_only,
        )
    )


def delete_universal_web_seed(
    *,
    workspace_id: str,
    seed_id: str,
    missing_ok: bool = False,
) -> bool:
    """
    Physically delete one seed repository record.

    Normal seed retirement should use the later Seed Controls component
    to disable or archive the record. Physical deletion is a low-level
    repository operation.
    """

    if not isinstance(missing_ok, bool):
        raise ValueError(
            "missing_ok must be a boolean."
        )

    clean_seed_id = required_string(
        seed_id,
        field_name="seed_id",
    )

    store = load_universal_web_seed_store(
        workspace_id
    )

    seeds = store.setdefault(
        "seeds",
        {},
    )

    if clean_seed_id not in seeds:
        if missing_ok:
            return False

        raise KeyError(
            "Universal Web Seed does not exist: "
            f"{clean_seed_id}"
        )

    del seeds[
        clean_seed_id
    ]

    save_universal_web_seed_store(
        workspace_id,
        store,
    )

    return True


def explain_universal_web_seed_repository_v1() -> Dict[str, Any]:
    """Return the inspectable seed repository contract."""

    return {
        "ok": True,
        "component": "universal_web_seed_repository",
        "schema_version": (
            UNIVERSAL_WEB_SEED_REPOSITORY_SCHEMA_VERSION
        ),
        "seed_schema_version": (
            UNIVERSAL_WEB_SEED_SCHEMA_VERSION
        ),
        "pipeline_stage": (
            "Universal Web Seed Registry"
        ),
        "storage_root": str(
            UNIVERSAL_WEB_SEED_STORE_ROOT
        ),
        "storage_scope": "workspace",
        "persistence_format": "json",
        "atomic_write": True,
        "read_retry_attempts": 3,
        "ordering": [
            "priority descending",
            "registered_at ascending",
            "seed_id ascending",
        ],
        "supported_filters": [
            "seed_type",
            "status",
            "enabled",
            "active_only",
        ],
        "responsibilities": [
            "persist Universal Web Seed records",
            "isolate seed records by workspace",
            "validate seed repository documents",
            "validate seed model schema compatibility",
            "protect seed record identity integrity",
            "create seed records",
            "retrieve seed records",
            "update seed records",
            "filter and list seed records",
            "filter and count seed records",
            "delete seed records at repository level",
            "reject duplicate seed identities",
            "detect corrupt repository documents",
        ],
        "excluded_responsibilities": [
            "seed identity generation",
            "seed registration orchestration",
            "seed lifecycle transitions",
            "seed enablement and disablement",
            "seed archival orchestration",
            "duplicate seed-target detection",
            "seed eligibility validation",
            "URL normalization",
            "domain normalization",
            "sitemap parsing",
            "feed parsing",
            "Crawl Frontier insertion",
            "crawl scheduling",
            "worker execution",
            "web page fetching",
        ],
        "physical_deletion_boundary": (
            "Normal seed retirement should use disable "
            "or archive controls. Physical deletion is "
            "a low-level repository operation."
        ),
        "next_component": (
            "Seed Registration Engine"
        ),
    }


__all__ = [
    "UNIVERSAL_WEB_SEED_REPOSITORY_SCHEMA_VERSION",
    "UNIVERSAL_WEB_SEED_STORE_ROOT",
    "count_universal_web_seeds",
    "create_universal_web_seed",
    "delete_universal_web_seed",
    "empty_universal_web_seed_store",
    "explain_universal_web_seed_repository_v1",
    "get_universal_web_seed",
    "list_universal_web_seeds",
    "load_universal_web_seed_store",
    "require_universal_web_seed",
    "save_universal_web_seed_store",
    "universal_web_seed_exists",
    "universal_web_seed_store_path",
    "update_universal_web_seed",
    "validate_universal_web_seed_store",
]
