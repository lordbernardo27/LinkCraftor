"""
LinkCraftor Autonomous Public-Web Crawler
Crawler Session Models

This module defines the canonical data contract for one autonomous
crawler session.

It contains models and validation only.

It does not:
- persist session records;
- start crawler workers;
- schedule URLs;
- fetch web pages;
- coordinate the crawler pipeline.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Mapping


CRAWLER_SESSION_SCHEMA_VERSION = "crawler_session.v1"


def utc_now_iso() -> str:
    """Return a timezone-aware UTC timestamp in ISO-8601 form."""

    return datetime.now(timezone.utc).isoformat()


def required_string(
    value: Any,
    *,
    field_name: str,
) -> str:
    """Normalize and validate a required non-empty string."""

    cleaned = str(value or "").strip()

    if not cleaned:
        raise ValueError(
            f"{field_name} must be a non-empty string."
        )

    return cleaned


def non_negative_integer(
    value: Any,
    *,
    field_name: str,
) -> int:
    """Normalize and validate a non-negative integer."""

    if isinstance(value, bool):
        raise ValueError(
            f"{field_name} must be a non-negative integer."
        )

    try:
        cleaned = int(value)
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            f"{field_name} must be a non-negative integer."
        ) from exc

    if cleaned < 0:
        raise ValueError(
            f"{field_name} must be a non-negative integer."
        )

    return cleaned


class CrawlSessionStatus(str, Enum):
    """
    Canonical lifecycle states for a crawler session.

    CREATED:
        Session identity exists but crawling has not started.

    RUNNING:
        The crawler is actively allowed to process work.

    PAUSED:
        New work must not be claimed until the session resumes.

    STOPPING:
        A controlled stop has been requested.

    COMPLETED:
        The session completed its configured scope successfully.

    FAILED:
        The session ended because of an unrecoverable failure.

    CANCELLED:
        The session was intentionally cancelled.
    """

    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


TERMINAL_CRAWL_SESSION_STATUSES = frozenset(
    {
        CrawlSessionStatus.COMPLETED,
        CrawlSessionStatus.FAILED,
        CrawlSessionStatus.CANCELLED,
    }
)


@dataclass
class CrawlSessionStatistics:
    """
    Cumulative operational counters for one crawler session.

    These counters describe session progress only. Detailed URL and
    page records will belong to later crawler components.
    """

    seeds_registered: int = 0
    urls_discovered: int = 0
    urls_scheduled: int = 0
    urls_claimed: int = 0
    fetches_attempted: int = 0
    fetches_succeeded: int = 0
    fetches_failed: int = 0
    pages_accepted: int = 0
    pages_rejected: int = 0
    pages_unchanged: int = 0
    pages_changed: int = 0
    pages_redirected: int = 0
    pages_deleted: int = 0
    pages_restored: int = 0
    left_arm_handoffs_succeeded: int = 0
    left_arm_handoffs_failed: int = 0

    def __post_init__(self) -> None:
        for field_name, value in asdict(self).items():
            setattr(
                self,
                field_name,
                non_negative_integer(
                    value,
                    field_name=field_name,
                ),
            )

    def to_dict(self) -> Dict[str, int]:
        return {
            key: int(value)
            for key, value in asdict(self).items()
        }

    @classmethod
    def from_mapping(
        cls,
        source: Mapping[str, Any] | None,
    ) -> "CrawlSessionStatistics":
        clean_source = dict(source or {})

        allowed_fields = cls.__dataclass_fields__.keys()

        return cls(
            **{
                field_name: clean_source.get(
                    field_name,
                    0,
                )
                for field_name in allowed_fields
            }
        )


@dataclass
class CrawlSessionLimits:
    """
    Optional safety boundaries for one crawler session.

    A value of zero means that the specific limit is not imposed by
    the session contract. Later policy components may still impose
    platform-wide limits.
    """

    maximum_urls: int = 0
    maximum_domains: int = 0
    maximum_depth: int = 0
    maximum_runtime_seconds: int = 0

    def __post_init__(self) -> None:
        for field_name, value in asdict(self).items():
            setattr(
                self,
                field_name,
                non_negative_integer(
                    value,
                    field_name=field_name,
                ),
            )

    def to_dict(self) -> Dict[str, int]:
        return {
            key: int(value)
            for key, value in asdict(self).items()
        }

    @classmethod
    def from_mapping(
        cls,
        source: Mapping[str, Any] | None,
    ) -> "CrawlSessionLimits":
        clean_source = dict(source or {})

        return cls(
            maximum_urls=clean_source.get(
                "maximum_urls",
                0,
            ),
            maximum_domains=clean_source.get(
                "maximum_domains",
                0,
            ),
            maximum_depth=clean_source.get(
                "maximum_depth",
                0,
            ),
            maximum_runtime_seconds=clean_source.get(
                "maximum_runtime_seconds",
                0,
            ),
        )


@dataclass
class CrawlSession:
    """
    Canonical crawler-session record.

    The model represents the complete lifecycle identity and summary
    state of one autonomous crawl operation.
    """

    crawl_session_id: str
    workspace_id: str
    session_name: str
    status: CrawlSessionStatus = CrawlSessionStatus.CREATED

    source_type: str = "autonomous_public_web_crawler"
    schema_version: str = CRAWLER_SESSION_SCHEMA_VERSION

    created_at: str = field(
        default_factory=utc_now_iso
    )
    updated_at: str = field(
        default_factory=utc_now_iso
    )

    started_at: str | None = None
    paused_at: str | None = None
    resumed_at: str | None = None
    stop_requested_at: str | None = None
    completed_at: str | None = None
    failed_at: str | None = None
    cancelled_at: str | None = None

    current_phase: str = "session_created"
    failure_reason: str | None = None

    limits: CrawlSessionLimits = field(
        default_factory=CrawlSessionLimits
    )
    statistics: CrawlSessionStatistics = field(
        default_factory=CrawlSessionStatistics
    )
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        self.crawl_session_id = required_string(
            self.crawl_session_id,
            field_name="crawl_session_id",
        )
        self.workspace_id = required_string(
            self.workspace_id,
            field_name="workspace_id",
        )
        self.session_name = required_string(
            self.session_name,
            field_name="session_name",
        )
        self.source_type = required_string(
            self.source_type,
            field_name="source_type",
        )
        self.schema_version = required_string(
            self.schema_version,
            field_name="schema_version",
        )
        self.current_phase = required_string(
            self.current_phase,
            field_name="current_phase",
        )

        if not isinstance(
            self.status,
            CrawlSessionStatus,
        ):
            try:
                self.status = CrawlSessionStatus(
                    str(self.status).strip().lower()
                )
            except ValueError as exc:
                raise ValueError(
                    "status is not a supported "
                    "CrawlSessionStatus."
                ) from exc

        if not isinstance(
            self.limits,
            CrawlSessionLimits,
        ):
            self.limits = (
                CrawlSessionLimits.from_mapping(
                    self.limits
                    if isinstance(self.limits, Mapping)
                    else None
                )
            )

        if not isinstance(
            self.statistics,
            CrawlSessionStatistics,
        ):
            self.statistics = (
                CrawlSessionStatistics.from_mapping(
                    self.statistics
                    if isinstance(
                        self.statistics,
                        Mapping,
                    )
                    else None
                )
            )

        if not isinstance(self.metadata, dict):
            raise ValueError(
                "metadata must be a dictionary."
            )

    @property
    def is_terminal(self) -> bool:
        return (
            self.status
            in TERMINAL_CRAWL_SESSION_STATUSES
        )

    def touch(self) -> None:
        self.updated_at = utc_now_iso()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "crawl_session_id": self.crawl_session_id,
            "workspace_id": self.workspace_id,
            "session_name": self.session_name,
            "source_type": self.source_type,
            "status": self.status.value,
            "current_phase": self.current_phase,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "started_at": self.started_at,
            "paused_at": self.paused_at,
            "resumed_at": self.resumed_at,
            "stop_requested_at": (
                self.stop_requested_at
            ),
            "completed_at": self.completed_at,
            "failed_at": self.failed_at,
            "cancelled_at": self.cancelled_at,
            "failure_reason": self.failure_reason,
            "limits": self.limits.to_dict(),
            "statistics": (
                self.statistics.to_dict()
            ),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(
        cls,
        source: Mapping[str, Any],
    ) -> "CrawlSession":
        if not isinstance(source, Mapping):
            raise ValueError(
                "Crawler session source must be a mapping."
            )

        return cls(
            crawl_session_id=source.get(
                "crawl_session_id",
                "",
            ),
            workspace_id=source.get(
                "workspace_id",
                "",
            ),
            session_name=source.get(
                "session_name",
                "",
            ),
            source_type=source.get(
                "source_type",
                "autonomous_public_web_crawler",
            ),
            schema_version=source.get(
                "schema_version",
                CRAWLER_SESSION_SCHEMA_VERSION,
            ),
            status=source.get(
                "status",
                CrawlSessionStatus.CREATED.value,
            ),
            current_phase=source.get(
                "current_phase",
                "session_created",
            ),
            created_at=source.get(
                "created_at",
                utc_now_iso(),
            ),
            updated_at=source.get(
                "updated_at",
                utc_now_iso(),
            ),
            started_at=source.get("started_at"),
            paused_at=source.get("paused_at"),
            resumed_at=source.get("resumed_at"),
            stop_requested_at=source.get(
                "stop_requested_at"
            ),
            completed_at=source.get(
                "completed_at"
            ),
            failed_at=source.get("failed_at"),
            cancelled_at=source.get(
                "cancelled_at"
            ),
            failure_reason=source.get(
                "failure_reason"
            ),
            limits=CrawlSessionLimits.from_mapping(
                source.get("limits")
            ),
            statistics=(
                CrawlSessionStatistics.from_mapping(
                    source.get("statistics")
                )
            ),
            metadata=dict(
                source.get("metadata") or {}
            ),
        )


def explain_crawler_session_models_v1() -> Dict[str, Any]:
    """Return an inspectable description of the model contract."""

    return {
        "ok": True,
        "schema_version": (
            CRAWLER_SESSION_SCHEMA_VERSION
        ),
        "component": "crawler_session_models",
        "source_type": (
            "autonomous_public_web_crawler"
        ),
        "statuses": [
            status.value
            for status in CrawlSessionStatus
        ],
        "terminal_statuses": sorted(
            status.value
            for status in (
                TERMINAL_CRAWL_SESSION_STATUSES
            )
        ),
        "responsibilities": [
            "define crawler session identity",
            "define crawler session lifecycle states",
            "define crawler session safety limits",
            "define crawler session summary statistics",
            "serialize and reconstruct crawler sessions",
            "validate crawler session model fields",
        ],
        "excluded_responsibilities": [
            "session persistence",
            "session lifecycle transitions",
            "URL frontier management",
            "crawl scheduling",
            "web page fetching",
            "worker execution",
            "left-arm handoff",
        ],
    }


__all__ = [
    "CRAWLER_SESSION_SCHEMA_VERSION",
    "CrawlSession",
    "CrawlSessionLimits",
    "CrawlSessionStatistics",
    "CrawlSessionStatus",
    "TERMINAL_CRAWL_SESSION_STATUSES",
    "explain_crawler_session_models_v1",
    "non_negative_integer",
    "required_string",
    "utc_now_iso",
]
