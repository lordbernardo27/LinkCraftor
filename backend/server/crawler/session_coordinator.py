"""
LinkCraftor Autonomous Public-Web Crawler
Crawler Session Coordinator

This coordinator controls the canonical lifecycle of crawler sessions.

Responsibilities:
- generate crawler-session identities;
- validate lifecycle requests;
- create crawler sessions;
- start crawler sessions;
- pause crawler sessions;
- resume crawler sessions;
- request controlled session stopping;
- complete crawler sessions;
- fail crawler sessions;
- cancel crawler sessions;
- retrieve crawler-session status;
- persist lifecycle changes through the certified repository.

This coordinator does not:
- register seed URLs;
- manage the crawl frontier;
- schedule URLs;
- claim worker jobs;
- fetch web pages;
- inspect or classify pages;
- perform left-arm handoff.

Those components will be integrated later through the top-level
Autonomous Crawler Coordinator after they are built and certified.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Mapping
from uuid import uuid4

from .session_models import (
    CrawlSession,
    CrawlSessionLimits,
    CrawlSessionStatistics,
    CrawlSessionStatus,
    required_string,
)
from .session_repository import (
    create_crawler_session,
    require_crawler_session,
    update_crawler_session,
)


CRAWLER_SESSION_COORDINATOR_SCHEMA_VERSION = (
    "crawler_session_coordinator.v1"
)


ALLOWED_CRAWLER_SESSION_TRANSITIONS = {
    CrawlSessionStatus.CREATED: frozenset(
        {
            CrawlSessionStatus.RUNNING,
            CrawlSessionStatus.CANCELLED,
            CrawlSessionStatus.FAILED,
        }
    ),
    CrawlSessionStatus.RUNNING: frozenset(
        {
            CrawlSessionStatus.PAUSED,
            CrawlSessionStatus.STOPPING,
            CrawlSessionStatus.COMPLETED,
            CrawlSessionStatus.FAILED,
            CrawlSessionStatus.CANCELLED,
        }
    ),
    CrawlSessionStatus.PAUSED: frozenset(
        {
            CrawlSessionStatus.RUNNING,
            CrawlSessionStatus.STOPPING,
            CrawlSessionStatus.FAILED,
            CrawlSessionStatus.CANCELLED,
        }
    ),
    CrawlSessionStatus.STOPPING: frozenset(
        {
            CrawlSessionStatus.COMPLETED,
            CrawlSessionStatus.FAILED,
            CrawlSessionStatus.CANCELLED,
        }
    ),
    CrawlSessionStatus.COMPLETED: frozenset(),
    CrawlSessionStatus.FAILED: frozenset(),
    CrawlSessionStatus.CANCELLED: frozenset(),
}


def utc_now_iso() -> str:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(
        timezone.utc
    ).isoformat()


def generate_crawler_session_id() -> str:
    """
    Generate a globally unique crawler-session identity.

    The timestamp supports operational inspection while UUID entropy
    protects against collisions across workers and environments.
    """

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%S%fZ")

    random_suffix = uuid4().hex[:12]

    return (
        "crawl_session_"
        f"{timestamp}_"
        f"{random_suffix}"
    )


def normalize_optional_string(
    value: Any,
) -> str | None:
    """Normalize an optional string value."""

    if value is None:
        return None

    cleaned = str(value).strip()

    return cleaned or None


def normalize_metadata(
    metadata: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    """Return a validated independent metadata dictionary."""

    if metadata is None:
        return {}

    if not isinstance(metadata, Mapping):
        raise ValueError(
            "metadata must be a mapping."
        )

    return dict(metadata)


def normalize_limits(
    limits: CrawlSessionLimits
    | Mapping[str, Any]
    | None,
) -> CrawlSessionLimits:
    """Normalize crawler-session safety limits."""

    if limits is None:
        return CrawlSessionLimits()

    if isinstance(
        limits,
        CrawlSessionLimits,
    ):
        return CrawlSessionLimits.from_mapping(
            limits.to_dict()
        )

    if isinstance(limits, Mapping):
        return CrawlSessionLimits.from_mapping(
            limits
        )

    raise ValueError(
        "limits must be CrawlSessionLimits, "
        "a mapping, or None."
    )


def validate_transition(
    *,
    current_status: CrawlSessionStatus,
    target_status: CrawlSessionStatus,
) -> None:
    """Reject invalid crawler-session lifecycle transitions."""

    allowed_targets = (
        ALLOWED_CRAWLER_SESSION_TRANSITIONS.get(
            current_status
        )
    )

    if allowed_targets is None:
        raise ValueError(
            "Current crawler-session status is not "
            "registered in the transition table."
        )

    if target_status not in allowed_targets:
        raise ValueError(
            "Invalid crawler-session transition: "
            f"{current_status.value} -> "
            f"{target_status.value}"
        )


def create_crawler_session_request(
    *,
    workspace_id: str,
    session_name: str,
    limits: CrawlSessionLimits
    | Mapping[str, Any]
    | None = None,
    metadata: Mapping[str, Any]
    | None = None,
    crawl_session_id: str | None = None,
) -> CrawlSession:
    """
    Create and persist a crawler session in CREATED state.

    This function creates session identity and state only. It does not
    register seeds, initialize a frontier, or start workers.
    """

    clean_workspace_id = required_string(
        workspace_id,
        field_name="workspace_id",
    )

    clean_session_name = required_string(
        session_name,
        field_name="session_name",
    )

    resolved_session_id = (
        required_string(
            crawl_session_id,
            field_name="crawl_session_id",
        )
        if crawl_session_id is not None
        else generate_crawler_session_id()
    )

    normalized_metadata = normalize_metadata(
        metadata
    )

    normalized_metadata.setdefault(
        "created_by",
        "crawler_session_coordinator",
    )
    normalized_metadata.setdefault(
        "execution_initialized",
        False,
    )
    normalized_metadata.setdefault(
        "seed_registry_initialized",
        False,
    )
    normalized_metadata.setdefault(
        "crawl_frontier_initialized",
        False,
    )
    normalized_metadata.setdefault(
        "scheduler_initialized",
        False,
    )
    normalized_metadata.setdefault(
        "worker_cluster_initialized",
        False,
    )

    session = CrawlSession(
        crawl_session_id=resolved_session_id,
        workspace_id=clean_workspace_id,
        session_name=clean_session_name,
        status=CrawlSessionStatus.CREATED,
        current_phase="session_created",
        limits=normalize_limits(
            limits
        ),
        statistics=CrawlSessionStatistics(),
        metadata=normalized_metadata,
    )

    return create_crawler_session(
        session
    )


def transition_crawler_session(
    *,
    workspace_id: str,
    crawl_session_id: str,
    target_status: CrawlSessionStatus,
    current_phase: str,
    failure_reason: str | None = None,
    metadata_updates: Mapping[str, Any]
    | None = None,
) -> CrawlSession:
    """
    Perform one validated crawler-session lifecycle transition.

    All public lifecycle operations delegate to this function.
    """

    if not isinstance(
        target_status,
        CrawlSessionStatus,
    ):
        try:
            target_status = CrawlSessionStatus(
                str(target_status).strip().lower()
            )
        except ValueError as exc:
            raise ValueError(
                "target_status is not a supported "
                "CrawlSessionStatus."
            ) from exc

    session = require_crawler_session(
        workspace_id=workspace_id,
        crawl_session_id=crawl_session_id,
    )

    validate_transition(
        current_status=session.status,
        target_status=target_status,
    )

    now = utc_now_iso()

    session.status = target_status
    session.current_phase = required_string(
        current_phase,
        field_name="current_phase",
    )
    session.updated_at = now

    if target_status == CrawlSessionStatus.RUNNING:
        if session.started_at is None:
            session.started_at = now
        else:
            session.resumed_at = now

        session.paused_at = None
        session.failure_reason = None

    elif target_status == CrawlSessionStatus.PAUSED:
        session.paused_at = now

    elif target_status == CrawlSessionStatus.STOPPING:
        session.stop_requested_at = now

    elif target_status == CrawlSessionStatus.COMPLETED:
        session.completed_at = now
        session.failure_reason = None

    elif target_status == CrawlSessionStatus.FAILED:
        clean_failure_reason = normalize_optional_string(
            failure_reason
        )

        if clean_failure_reason is None:
            raise ValueError(
                "failure_reason is required when "
                "failing a crawler session."
            )

        session.failed_at = now
        session.failure_reason = (
            clean_failure_reason
        )

    elif target_status == CrawlSessionStatus.CANCELLED:
        session.cancelled_at = now

        clean_reason = normalize_optional_string(
            failure_reason
        )

        if clean_reason is not None:
            session.failure_reason = clean_reason

    if metadata_updates is not None:
        session.metadata.update(
            normalize_metadata(
                metadata_updates
            )
        )

    return update_crawler_session(
        session
    )


def start_crawler_session(
    *,
    workspace_id: str,
    crawl_session_id: str,
) -> CrawlSession:
    """
    Mark a CREATED session as RUNNING.

    This currently authorizes execution only. Actual seed, frontier,
    scheduler, and worker startup will be connected after those
    components are built and certified.
    """

    return transition_crawler_session(
        workspace_id=workspace_id,
        crawl_session_id=crawl_session_id,
        target_status=CrawlSessionStatus.RUNNING,
        current_phase="session_running",
        metadata_updates={
            "execution_authorized": True,
        },
    )


def pause_crawler_session(
    *,
    workspace_id: str,
    crawl_session_id: str,
) -> CrawlSession:
    """Pause a running crawler session."""

    return transition_crawler_session(
        workspace_id=workspace_id,
        crawl_session_id=crawl_session_id,
        target_status=CrawlSessionStatus.PAUSED,
        current_phase="session_paused",
        metadata_updates={
            "execution_authorized": False,
        },
    )


def resume_crawler_session(
    *,
    workspace_id: str,
    crawl_session_id: str,
) -> CrawlSession:
    """Resume a paused crawler session."""

    return transition_crawler_session(
        workspace_id=workspace_id,
        crawl_session_id=crawl_session_id,
        target_status=CrawlSessionStatus.RUNNING,
        current_phase="session_running",
        metadata_updates={
            "execution_authorized": True,
        },
    )


def request_stop_crawler_session(
    *,
    workspace_id: str,
    crawl_session_id: str,
) -> CrawlSession:
    """
    Request a controlled crawler-session stop.

    Later worker and scheduler components will observe STOPPING and
    finish or release their active work safely.
    """

    return transition_crawler_session(
        workspace_id=workspace_id,
        crawl_session_id=crawl_session_id,
        target_status=CrawlSessionStatus.STOPPING,
        current_phase="controlled_stop_requested",
        metadata_updates={
            "execution_authorized": False,
            "controlled_stop_requested": True,
        },
    )


def complete_crawler_session(
    *,
    workspace_id: str,
    crawl_session_id: str,
) -> CrawlSession:
    """Mark a RUNNING or STOPPING session as completed."""

    return transition_crawler_session(
        workspace_id=workspace_id,
        crawl_session_id=crawl_session_id,
        target_status=CrawlSessionStatus.COMPLETED,
        current_phase="session_completed",
        metadata_updates={
            "execution_authorized": False,
            "execution_completed": True,
        },
    )


def fail_crawler_session(
    *,
    workspace_id: str,
    crawl_session_id: str,
    failure_reason: str,
) -> CrawlSession:
    """Mark a non-terminal crawler session as failed."""

    return transition_crawler_session(
        workspace_id=workspace_id,
        crawl_session_id=crawl_session_id,
        target_status=CrawlSessionStatus.FAILED,
        current_phase="session_failed",
        failure_reason=failure_reason,
        metadata_updates={
            "execution_authorized": False,
            "execution_failed": True,
        },
    )


def cancel_crawler_session(
    *,
    workspace_id: str,
    crawl_session_id: str,
    cancellation_reason: str | None = None,
) -> CrawlSession:
    """Cancel a non-terminal crawler session."""

    return transition_crawler_session(
        workspace_id=workspace_id,
        crawl_session_id=crawl_session_id,
        target_status=CrawlSessionStatus.CANCELLED,
        current_phase="session_cancelled",
        failure_reason=cancellation_reason,
        metadata_updates={
            "execution_authorized": False,
            "execution_cancelled": True,
        },
    )


def get_crawler_session_status(
    *,
    workspace_id: str,
    crawl_session_id: str,
) -> Dict[str, Any]:
    """Return a stable crawler-session status response."""

    session = require_crawler_session(
        workspace_id=workspace_id,
        crawl_session_id=crawl_session_id,
    )

    return {
        "ok": True,
        "component": "crawler_session_coordinator",
        "schema_version": (
            CRAWLER_SESSION_COORDINATOR_SCHEMA_VERSION
        ),
        "crawl_session_id": (
            session.crawl_session_id
        ),
        "workspace_id": session.workspace_id,
        "session_name": session.session_name,
        "status": session.status.value,
        "current_phase": session.current_phase,
        "is_terminal": session.is_terminal,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "started_at": session.started_at,
        "paused_at": session.paused_at,
        "resumed_at": session.resumed_at,
        "stop_requested_at": (
            session.stop_requested_at
        ),
        "completed_at": session.completed_at,
        "failed_at": session.failed_at,
        "cancelled_at": session.cancelled_at,
        "failure_reason": session.failure_reason,
        "limits": session.limits.to_dict(),
        "statistics": (
            session.statistics.to_dict()
        ),
        "metadata": dict(session.metadata),
    }


def explain_crawler_session_coordinator_v1() -> Dict[str, Any]:
    """Return the inspectable coordinator contract."""

    return {
        "ok": True,
        "component": "crawler_session_coordinator",
        "schema_version": (
            CRAWLER_SESSION_COORDINATOR_SCHEMA_VERSION
        ),
        "responsibilities": [
            "generate crawler session identities",
            "create crawler sessions",
            "validate crawler session lifecycle transitions",
            "start crawler sessions",
            "pause crawler sessions",
            "resume crawler sessions",
            "request controlled session stopping",
            "complete crawler sessions",
            "fail crawler sessions",
            "cancel crawler sessions",
            "return crawler session status",
            "persist lifecycle changes through the session repository",
        ],
        "excluded_responsibilities": [
            "seed URL registration",
            "crawl frontier management",
            "URL scheduling",
            "worker job claiming",
            "web page fetching",
            "HTML parsing",
            "page classification",
            "page lifecycle analysis",
            "left-arm handoff",
        ],
        "allowed_transitions": {
            source.value: sorted(
                target.value
                for target in targets
            )
            for source, targets
            in ALLOWED_CRAWLER_SESSION_TRANSITIONS.items()
        },
        "future_integrations": [
            "Seed Registry",
            "Crawl Frontier",
            "Crawl Scheduler",
            "Crawler Worker Cluster",
            "Crawler Statistics",
            "Top-Level Autonomous Crawler Coordinator",
        ],
    }


__all__ = [
    "ALLOWED_CRAWLER_SESSION_TRANSITIONS",
    "CRAWLER_SESSION_COORDINATOR_SCHEMA_VERSION",
    "cancel_crawler_session",
    "complete_crawler_session",
    "create_crawler_session_request",
    "explain_crawler_session_coordinator_v1",
    "fail_crawler_session",
    "generate_crawler_session_id",
    "get_crawler_session_status",
    "pause_crawler_session",
    "request_stop_crawler_session",
    "resume_crawler_session",
    "start_crawler_session",
    "transition_crawler_session",
    "validate_transition",
]
