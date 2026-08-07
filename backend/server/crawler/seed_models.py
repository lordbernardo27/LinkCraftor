"""
LinkCraftor Autonomous Public-Web Crawler
Universal Web Seed Record Contract

This module defines the canonical record for a seed registered in the
Universal Web Seed Registry.

Responsibilities:
- define seed identity;
- define supported seed types;
- define seed ownership;
- define seed target information;
- define seed priority and control state;
- preserve seed registration provenance;
- preserve seed lifecycle timestamps;
- validate seed-record fields;
- serialize and reconstruct seed records.

This module does not:
- persist seed records;
- perform seed eligibility validation;
- normalize URLs or domains;
- resolve DNS or public-network safety;
- retrieve robots.txt;
- parse sitemaps or feeds;
- insert URLs into the Crawl Frontier;
- schedule crawl jobs;
- fetch web pages;
- perform HTML acquisition.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Mapping

from .session_models import (
    non_negative_integer,
    required_string,
)


UNIVERSAL_WEB_SEED_SCHEMA_VERSION = (
    "universal_web_seed.v1"
)


class UniversalWebSeedType(str, Enum):
    """Supported Universal Web Seed types."""

    URL = "url"
    DOMAIN = "domain"
    SITEMAP = "sitemap"
    RSS_FEED = "rss_feed"


class UniversalWebSeedStatus(str, Enum):
    """Canonical Universal Web Seed lifecycle states."""

    REGISTERED = "registered"
    DISABLED = "disabled"
    ARCHIVED = "archived"


def utc_now_iso() -> str:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(
        timezone.utc
    ).isoformat()


def optional_string(
    value: Any,
) -> str | None:
    """Normalize an optional string."""

    if value is None:
        return None

    cleaned = str(value).strip()

    return cleaned or None


def normalize_seed_type(
    value: UniversalWebSeedType | str,
) -> UniversalWebSeedType:
    """Normalize and validate a seed type."""

    if isinstance(
        value,
        UniversalWebSeedType,
    ):
        return value

    try:
        return UniversalWebSeedType(
            required_string(
                value,
                field_name="seed_type",
            ).lower()
        )
    except ValueError as exc:
        raise ValueError(
            "Unsupported Universal Web Seed type: "
            f"{value}"
        ) from exc


def normalize_seed_status(
    value: UniversalWebSeedStatus | str,
) -> UniversalWebSeedStatus:
    """Normalize and validate a seed status."""

    if isinstance(
        value,
        UniversalWebSeedStatus,
    ):
        return value

    try:
        return UniversalWebSeedStatus(
            required_string(
                value,
                field_name="status",
            ).lower()
        )
    except ValueError as exc:
        raise ValueError(
            "Unsupported Universal Web Seed status: "
            f"{value}"
        ) from exc


def normalize_metadata(
    value: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    """Return an independent metadata dictionary."""

    if value is None:
        return {}

    if not isinstance(value, Mapping):
        raise ValueError(
            "metadata must be a mapping."
        )

    return dict(value)


@dataclass
class UniversalWebSeed:
    """
    Canonical Universal Web Seed record.

    A seed represents an explicitly registered starting point for the
    autonomous crawler. Eligibility is determined by the later
    Seed Eligibility Validation stage.
    """

    seed_id: str
    workspace_id: str
    seed_type: UniversalWebSeedType
    original_value: str

    normalized_value: str | None = None
    domain: str | None = None
    root_domain: str | None = None
    crawler_session_id: str | None = None

    priority: int = 0
    enabled: bool = True
    status: UniversalWebSeedStatus = (
        UniversalWebSeedStatus.REGISTERED
    )

    registered_by: str = (
        "crawler_seed_registration"
    )
    registered_source: str = (
        "autonomous_public_web_crawler"
    )

    registered_at: str = field(
        default_factory=utc_now_iso
    )
    created_at: str = field(
        default_factory=utc_now_iso
    )
    updated_at: str = field(
        default_factory=utc_now_iso
    )

    enabled_at: str | None = field(
        default_factory=utc_now_iso
    )
    disabled_at: str | None = None
    archived_at: str | None = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    schema_version: str = (
        UNIVERSAL_WEB_SEED_SCHEMA_VERSION
    )

    def __post_init__(self) -> None:
        """Validate and normalize the seed record."""

        self.seed_id = required_string(
            self.seed_id,
            field_name="seed_id",
        )

        self.workspace_id = required_string(
            self.workspace_id,
            field_name="workspace_id",
        )

        self.seed_type = normalize_seed_type(
            self.seed_type
        )

        self.original_value = required_string(
            self.original_value,
            field_name="original_value",
        )

        self.normalized_value = optional_string(
            self.normalized_value
        )

        self.domain = optional_string(
            self.domain
        )

        self.root_domain = optional_string(
            self.root_domain
        )

        self.crawler_session_id = optional_string(
            self.crawler_session_id
        )

        self.priority = non_negative_integer(
            self.priority,
            field_name="priority",
        )

        if not isinstance(self.enabled, bool):
            raise ValueError(
                "enabled must be a boolean."
            )

        self.status = normalize_seed_status(
            self.status
        )

        self.registered_by = required_string(
            self.registered_by,
            field_name="registered_by",
        )

        self.registered_source = required_string(
            self.registered_source,
            field_name="registered_source",
        )

        self.registered_at = required_string(
            self.registered_at,
            field_name="registered_at",
        )

        self.created_at = required_string(
            self.created_at,
            field_name="created_at",
        )

        self.updated_at = required_string(
            self.updated_at,
            field_name="updated_at",
        )

        self.enabled_at = optional_string(
            self.enabled_at
        )

        self.disabled_at = optional_string(
            self.disabled_at
        )

        self.archived_at = optional_string(
            self.archived_at
        )

        self.metadata = normalize_metadata(
            self.metadata
        )

        self.schema_version = required_string(
            self.schema_version,
            field_name="schema_version",
        )

        if (
            self.schema_version
            != UNIVERSAL_WEB_SEED_SCHEMA_VERSION
        ):
            raise ValueError(
                "Unsupported Universal Web Seed "
                f"schema version: {self.schema_version}"
            )

        self._validate_control_state()

    def _validate_control_state(self) -> None:
        """Validate enabled and lifecycle-state consistency."""

        if (
            self.status
            == UniversalWebSeedStatus.REGISTERED
            and not self.enabled
        ):
            raise ValueError(
                "A registered seed must be enabled. "
                "Use status='disabled' for a disabled seed."
            )

        if (
            self.status
            == UniversalWebSeedStatus.DISABLED
            and self.enabled
        ):
            raise ValueError(
                "A disabled seed cannot have enabled=True."
            )

        if (
            self.status
            == UniversalWebSeedStatus.ARCHIVED
            and self.enabled
        ):
            raise ValueError(
                "An archived seed cannot have enabled=True."
            )

        if (
            self.status
            == UniversalWebSeedStatus.DISABLED
            and self.disabled_at is None
        ):
            raise ValueError(
                "A disabled seed requires disabled_at."
            )

        if (
            self.status
            == UniversalWebSeedStatus.ARCHIVED
            and self.archived_at is None
        ):
            raise ValueError(
                "An archived seed requires archived_at."
            )

    @property
    def is_active(self) -> bool:
        """Return whether the seed is currently active."""

        return (
            self.enabled
            and self.status
            == UniversalWebSeedStatus.REGISTERED
        )

    def touch(self) -> None:
        """Update the record modification timestamp."""

        self.updated_at = utc_now_iso()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the Universal Web Seed record."""

        return {
            "schema_version": self.schema_version,
            "seed_id": self.seed_id,
            "workspace_id": self.workspace_id,
            "crawler_session_id": (
                self.crawler_session_id
            ),
            "seed_type": self.seed_type.value,
            "original_value": self.original_value,
            "normalized_value": (
                self.normalized_value
            ),
            "domain": self.domain,
            "root_domain": self.root_domain,
            "priority": self.priority,
            "enabled": self.enabled,
            "status": self.status.value,
            "registered_by": self.registered_by,
            "registered_source": (
                self.registered_source
            ),
            "registered_at": self.registered_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "enabled_at": self.enabled_at,
            "disabled_at": self.disabled_at,
            "archived_at": self.archived_at,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(
        cls,
        source: Mapping[str, Any],
    ) -> "UniversalWebSeed":
        """Reconstruct a Universal Web Seed from a mapping."""

        if not isinstance(source, Mapping):
            raise ValueError(
                "Universal Web Seed source must be "
                "a mapping."
            )

        metadata = source.get(
            "metadata"
        )

        return cls(
            seed_id=source.get(
                "seed_id"
            ),
            workspace_id=source.get(
                "workspace_id"
            ),
            crawler_session_id=source.get(
                "crawler_session_id"
            ),
            seed_type=source.get(
                "seed_type"
            ),
            original_value=source.get(
                "original_value"
            ),
            normalized_value=source.get(
                "normalized_value"
            ),
            domain=source.get(
                "domain"
            ),
            root_domain=source.get(
                "root_domain"
            ),
            priority=source.get(
                "priority",
                0,
            ),
            enabled=source.get(
                "enabled",
                True,
            ),
            status=source.get(
                "status",
                UniversalWebSeedStatus.REGISTERED.value,
            ),
            registered_by=source.get(
                "registered_by",
                "crawler_seed_registration",
            ),
            registered_source=source.get(
                "registered_source",
                "autonomous_public_web_crawler",
            ),
            registered_at=source.get(
                "registered_at",
                utc_now_iso(),
            ),
            created_at=source.get(
                "created_at",
                utc_now_iso(),
            ),
            updated_at=source.get(
                "updated_at",
                utc_now_iso(),
            ),
            enabled_at=source.get(
                "enabled_at"
            ),
            disabled_at=source.get(
                "disabled_at"
            ),
            archived_at=source.get(
                "archived_at"
            ),
            metadata=(
                dict(metadata)
                if isinstance(metadata, Mapping)
                else metadata
            ),
            schema_version=source.get(
                "schema_version",
                UNIVERSAL_WEB_SEED_SCHEMA_VERSION,
            ),
        )


def explain_universal_web_seed_models_v1() -> Dict[str, Any]:
    """Return the inspectable Seed Record Contract."""

    return {
        "ok": True,
        "component": "universal_web_seed_models",
        "schema_version": (
            UNIVERSAL_WEB_SEED_SCHEMA_VERSION
        ),
        "pipeline_stage": (
            "Universal Web Seed Registry"
        ),
        "supported_seed_types": [
            seed_type.value
            for seed_type
            in UniversalWebSeedType
        ],
        "supported_statuses": [
            status.value
            for status
            in UniversalWebSeedStatus
        ],
        "responsibilities": [
            "define the canonical Universal Web Seed record",
            "define seed identity",
            "define supported seed types",
            "define seed ownership",
            "define seed target fields",
            "define seed control state",
            "define seed registration provenance",
            "define seed lifecycle timestamps",
            "validate seed record fields",
            "serialize and reconstruct seed records",
        ],
        "excluded_responsibilities": [
            "seed persistence",
            "seed eligibility validation",
            "URL normalization",
            "domain normalization",
            "public-network safety validation",
            "robots.txt processing",
            "sitemap parsing",
            "feed parsing",
            "Crawl Frontier insertion",
            "crawl scheduling",
            "worker execution",
            "web page fetching",
            "HTML acquisition",
        ],
        "next_pipeline_stage": (
            "Seed Eligibility Validation"
        ),
    }


__all__ = [
    "UNIVERSAL_WEB_SEED_SCHEMA_VERSION",
    "UniversalWebSeed",
    "UniversalWebSeedStatus",
    "UniversalWebSeedType",
    "explain_universal_web_seed_models_v1",
    "normalize_metadata",
    "normalize_seed_status",
    "normalize_seed_type",
    "optional_string",
]
