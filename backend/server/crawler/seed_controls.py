"""
LinkCraftor Autonomous Public-Web Crawler
Universal Web Seed Controls

This module manages the operational lifecycle and editable control
fields of registered Universal Web Seeds.

Public operations:
- enable a disabled seed;
- disable a registered seed;
- archive a registered or disabled seed;
- restore an archived seed to disabled status;
- update seed priority;
- update operational metadata.

A single canonical transition validator owns all lifecycle transition
rules.

This module does not:
- register new seeds;
- generate seed identities;
- normalize seed targets;
- detect duplicate seed targets;
- determine seed eligibility;
- insert seeds into the Crawl Frontier;
- schedule crawler work;
- fetch web pages;
- parse sitemaps or feeds.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Mapping

from .seed_models import (
    UniversalWebSeed,
    UniversalWebSeedStatus,
    normalize_metadata,
    normalize_seed_status,
)
from .seed_repository import (
    require_universal_web_seed,
    update_universal_web_seed,
)
from .session_models import (
    non_negative_integer,
    required_string,
)


UNIVERSAL_WEB_SEED_CONTROLS_SCHEMA_VERSION = (
    "universal_web_seed_controls.v1"
)


ALLOWED_UNIVERSAL_WEB_SEED_TRANSITIONS = {
    UniversalWebSeedStatus.REGISTERED: {
        UniversalWebSeedStatus.DISABLED,
        UniversalWebSeedStatus.ARCHIVED,
    },
    UniversalWebSeedStatus.DISABLED: {
        UniversalWebSeedStatus.REGISTERED,
        UniversalWebSeedStatus.ARCHIVED,
    },
    UniversalWebSeedStatus.ARCHIVED: {
        UniversalWebSeedStatus.DISABLED,
    },
}


PROTECTED_SEED_METADATA_KEYS = {
    "seed_id",
    "workspace_id",
    "crawler_session_id",
    "seed_type",
    "original_value",
    "normalized_value",
    "domain",
    "root_domain",
    "priority",
    "enabled",
    "status",
    "registered_by",
    "registered_source",
    "registered_at",
    "created_at",
    "updated_at",
    "enabled_at",
    "disabled_at",
    "archived_at",
    "schema_version",
}


def utc_now_iso() -> str:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(
        timezone.utc
    ).isoformat()


def normalize_control_actor(
    actor: Any,
) -> str:
    """Validate the actor responsible for a control operation."""

    return required_string(
        actor,
        field_name="actor",
    )


def normalize_control_reason(
    reason: Any,
) -> str:
    """Validate the reason for a control operation."""

    return required_string(
        reason,
        field_name="reason",
    )


def validate_seed_transition(
    current_status: UniversalWebSeedStatus | str,
    target_status: UniversalWebSeedStatus | str,
) -> None:
    """
    Validate one Universal Web Seed lifecycle transition.

    This is the single canonical authority for seed lifecycle changes.
    It returns None when the transition is allowed and raises
    ValueError when it is forbidden.
    """

    normalized_current = normalize_seed_status(
        current_status
    )

    normalized_target = normalize_seed_status(
        target_status
    )

    allowed_targets = (
        ALLOWED_UNIVERSAL_WEB_SEED_TRANSITIONS.get(
            normalized_current,
            set(),
        )
    )

    if normalized_target not in allowed_targets:
        raise ValueError(
            "Invalid Universal Web Seed transition: "
            f"{normalized_current.value} -> "
            f"{normalized_target.value}"
        )


def append_seed_control_event(
    *,
    seed: UniversalWebSeed,
    operation: str,
    actor: str,
    reason: str,
    previous_status: UniversalWebSeedStatus,
    current_status: UniversalWebSeedStatus,
    changed_at: str,
    metadata: Mapping[str, Any] | None = None,
) -> None:
    """Append one lifecycle or control event to seed metadata."""

    normalized_metadata = normalize_metadata(
        metadata
    )

    event = {
        "operation": required_string(
            operation,
            field_name="operation",
        ),
        "actor": normalize_control_actor(
            actor
        ),
        "reason": normalize_control_reason(
            reason
        ),
        "previous_status": previous_status.value,
        "current_status": current_status.value,
        "changed_at": required_string(
            changed_at,
            field_name="changed_at",
        ),
        "metadata": normalized_metadata,
    }

    history = seed.metadata.get(
        "control_history"
    )

    if history is None:
        history = []

    if not isinstance(history, list):
        raise ValueError(
            "seed metadata control_history must be a list."
        )

    history = [
        dict(item)
        if isinstance(item, Mapping)
        else item
        for item in history
    ]

    history.append(
        event
    )

    seed.metadata["control_history"] = history
    seed.metadata["last_control_operation"] = (
        event["operation"]
    )
    seed.metadata["last_control_actor"] = actor
    seed.metadata["last_control_reason"] = reason
    seed.metadata["last_control_at"] = changed_at


def build_seed_control_result(
    *,
    seed: UniversalWebSeed,
    operation: str,
    previous_status: UniversalWebSeedStatus,
    changed: bool,
    message: str,
    previous_priority: int | None = None,
) -> Dict[str, Any]:
    """Build the stable Seed Controls result contract."""

    if not isinstance(seed, UniversalWebSeed):
        raise ValueError(
            "seed must be a UniversalWebSeed instance."
        )

    if not isinstance(
        previous_status,
        UniversalWebSeedStatus,
    ):
        raise ValueError(
            "previous_status must be a "
            "UniversalWebSeedStatus."
        )

    if not isinstance(changed, bool):
        raise ValueError(
            "changed must be a boolean."
        )

    result = {
        "ok": True,
        "component": "universal_web_seed_controls",
        "schema_version": (
            UNIVERSAL_WEB_SEED_CONTROLS_SCHEMA_VERSION
        ),
        "operation": required_string(
            operation,
            field_name="operation",
        ),
        "changed": changed,
        "seed_id": seed.seed_id,
        "workspace_id": seed.workspace_id,
        "previous_status": previous_status.value,
        "current_status": seed.status.value,
        "enabled": seed.enabled,
        "priority": seed.priority,
        "updated_at": seed.updated_at,
        "message": required_string(
            message,
            field_name="message",
        ),
        "seed": seed.to_dict(),
        "next_pipeline_stage": (
            "Seed Eligibility Validation"
        ),
    }

    if previous_priority is not None:
        result["previous_priority"] = previous_priority
        result["current_priority"] = seed.priority

    return result


def enable_seed(
    *,
    workspace_id: str,
    seed_id: str,
    actor: str,
    reason: str,
    metadata: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Enable a disabled seed."""

    seed = require_universal_web_seed(
        workspace_id=workspace_id,
        seed_id=seed_id,
    )

    previous_status = seed.status

    validate_seed_transition(
        previous_status,
        UniversalWebSeedStatus.REGISTERED,
    )

    now = utc_now_iso()

    seed.status = UniversalWebSeedStatus.REGISTERED
    seed.enabled = True
    seed.enabled_at = now
    seed.disabled_at = None
    seed.updated_at = now

    append_seed_control_event(
        seed=seed,
        operation="enable",
        actor=actor,
        reason=reason,
        previous_status=previous_status,
        current_status=seed.status,
        changed_at=now,
        metadata=metadata,
    )

    persisted = update_universal_web_seed(
        seed
    )

    return build_seed_control_result(
        seed=persisted,
        operation="enable",
        previous_status=previous_status,
        changed=True,
        message="Universal Web Seed enabled.",
    )


def disable_seed(
    *,
    workspace_id: str,
    seed_id: str,
    actor: str,
    reason: str,
    metadata: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Disable a registered seed."""

    seed = require_universal_web_seed(
        workspace_id=workspace_id,
        seed_id=seed_id,
    )

    previous_status = seed.status

    validate_seed_transition(
        previous_status,
        UniversalWebSeedStatus.DISABLED,
    )

    now = utc_now_iso()

    seed.status = UniversalWebSeedStatus.DISABLED
    seed.enabled = False
    seed.enabled_at = None
    seed.disabled_at = now
    seed.updated_at = now

    append_seed_control_event(
        seed=seed,
        operation="disable",
        actor=actor,
        reason=reason,
        previous_status=previous_status,
        current_status=seed.status,
        changed_at=now,
        metadata=metadata,
    )

    persisted = update_universal_web_seed(
        seed
    )

    return build_seed_control_result(
        seed=persisted,
        operation="disable",
        previous_status=previous_status,
        changed=True,
        message="Universal Web Seed disabled.",
    )


def archive_seed(
    *,
    workspace_id: str,
    seed_id: str,
    actor: str,
    reason: str,
    metadata: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Archive a registered or disabled seed."""

    seed = require_universal_web_seed(
        workspace_id=workspace_id,
        seed_id=seed_id,
    )

    previous_status = seed.status

    validate_seed_transition(
        previous_status,
        UniversalWebSeedStatus.ARCHIVED,
    )

    now = utc_now_iso()

    seed.status = UniversalWebSeedStatus.ARCHIVED
    seed.enabled = False
    seed.enabled_at = None
    seed.archived_at = now
    seed.updated_at = now

    append_seed_control_event(
        seed=seed,
        operation="archive",
        actor=actor,
        reason=reason,
        previous_status=previous_status,
        current_status=seed.status,
        changed_at=now,
        metadata=metadata,
    )

    persisted = update_universal_web_seed(
        seed
    )

    return build_seed_control_result(
        seed=persisted,
        operation="archive",
        previous_status=previous_status,
        changed=True,
        message="Universal Web Seed archived.",
    )


def restore_seed(
    *,
    workspace_id: str,
    seed_id: str,
    actor: str,
    reason: str,
    metadata: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Restore an archived seed to disabled status.

    Restoration never enables a seed automatically. A separate explicit
    enable operation is required before the seed becomes active.
    """

    seed = require_universal_web_seed(
        workspace_id=workspace_id,
        seed_id=seed_id,
    )

    previous_status = seed.status

    validate_seed_transition(
        previous_status,
        UniversalWebSeedStatus.DISABLED,
    )

    now = utc_now_iso()

    seed.status = UniversalWebSeedStatus.DISABLED
    seed.enabled = False
    seed.enabled_at = None
    seed.disabled_at = now
    seed.archived_at = None
    seed.updated_at = now
    seed.metadata["restored_at"] = now

    append_seed_control_event(
        seed=seed,
        operation="restore",
        actor=actor,
        reason=reason,
        previous_status=previous_status,
        current_status=seed.status,
        changed_at=now,
        metadata=metadata,
    )

    persisted = update_universal_web_seed(
        seed
    )

    return build_seed_control_result(
        seed=persisted,
        operation="restore",
        previous_status=previous_status,
        changed=True,
        message=(
            "Universal Web Seed restored to disabled status."
        ),
    )


def update_priority(
    *,
    workspace_id: str,
    seed_id: str,
    priority: int,
    actor: str,
    reason: str,
    metadata: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Update seed priority without changing lifecycle status."""

    seed = require_universal_web_seed(
        workspace_id=workspace_id,
        seed_id=seed_id,
    )

    normalized_priority = non_negative_integer(
        priority,
        field_name="priority",
    )

    actor = normalize_control_actor(
        actor
    )

    reason = normalize_control_reason(
        reason
    )

    previous_status = seed.status
    previous_priority = seed.priority

    if previous_priority == normalized_priority:
        raise ValueError(
            "The requested seed priority is already active."
        )

    now = utc_now_iso()

    seed.priority = normalized_priority
    seed.updated_at = now

    event_metadata = normalize_metadata(
        metadata
    )
    event_metadata["previous_priority"] = (
        previous_priority
    )
    event_metadata["current_priority"] = (
        normalized_priority
    )

    append_seed_control_event(
        seed=seed,
        operation="update_priority",
        actor=actor,
        reason=reason,
        previous_status=previous_status,
        current_status=seed.status,
        changed_at=now,
        metadata=event_metadata,
    )

    persisted = update_universal_web_seed(
        seed
    )

    return build_seed_control_result(
        seed=persisted,
        operation="update_priority",
        previous_status=previous_status,
        previous_priority=previous_priority,
        changed=True,
        message="Universal Web Seed priority updated.",
    )


def update_metadata(
    *,
    workspace_id: str,
    seed_id: str,
    metadata_updates: Mapping[str, Any],
    actor: str,
    reason: str,
) -> Dict[str, Any]:
    """Merge approved operational metadata into a seed record."""

    seed = require_universal_web_seed(
        workspace_id=workspace_id,
        seed_id=seed_id,
    )

    updates = normalize_metadata(
        metadata_updates
    )

    if not updates:
        raise ValueError(
            "metadata_updates must not be empty."
        )

    protected_updates = (
        PROTECTED_SEED_METADATA_KEYS
        & set(updates.keys())
    )

    if protected_updates:
        raise ValueError(
            "Seed metadata update contains protected keys: "
            + ", ".join(
                sorted(protected_updates)
            )
        )

    actor = normalize_control_actor(
        actor
    )

    reason = normalize_control_reason(
        reason
    )

    previous_status = seed.status

    unchanged_keys = {
        key
        for key, value in updates.items()
        if seed.metadata.get(key) == value
    }

    if len(unchanged_keys) == len(updates):
        raise ValueError(
            "The requested metadata values are already active."
        )

    now = utc_now_iso()

    seed.metadata.update(
        updates
    )
    seed.updated_at = now

    append_seed_control_event(
        seed=seed,
        operation="update_metadata",
        actor=actor,
        reason=reason,
        previous_status=previous_status,
        current_status=seed.status,
        changed_at=now,
        metadata={
            "updated_keys": sorted(
                updates.keys()
            ),
        },
    )

    persisted = update_universal_web_seed(
        seed
    )

    return build_seed_control_result(
        seed=persisted,
        operation="update_metadata",
        previous_status=previous_status,
        changed=True,
        message="Universal Web Seed metadata updated.",
    )


def explain_universal_web_seed_controls_v1() -> Dict[str, Any]:
    """Return the inspectable Seed Controls contract."""

    return {
        "ok": True,
        "component": "universal_web_seed_controls",
        "schema_version": (
            UNIVERSAL_WEB_SEED_CONTROLS_SCHEMA_VERSION
        ),
        "pipeline_stage": (
            "Universal Web Seed Registry"
        ),
        "transition_validator": (
            "validate_seed_transition"
        ),
        "allowed_transitions": {
            status.value: sorted(
                target.value
                for target
                in targets
            )
            for status, targets
            in ALLOWED_UNIVERSAL_WEB_SEED_TRANSITIONS.items()
        },
        "public_operations": [
            "enable_seed",
            "disable_seed",
            "archive_seed",
            "restore_seed",
            "update_priority",
            "update_metadata",
        ],
        "responsibilities": [
            "validate Universal Web Seed lifecycle transitions",
            "enable disabled seeds",
            "disable registered seeds",
            "archive registered or disabled seeds",
            "restore archived seeds to disabled status",
            "update seed priority",
            "update operational seed metadata",
            "record seed control history",
            "persist seed control changes through the certified repository",
            "return stable seed control results",
        ],
        "excluded_responsibilities": [
            "seed registration",
            "seed identity generation",
            "duplicate seed-target detection",
            "seed eligibility validation",
            "URL normalization",
            "domain normalization",
            "robots.txt processing",
            "sitemap parsing",
            "feed parsing",
            "Crawl Frontier insertion",
            "crawl scheduling",
            "worker execution",
            "web page fetching",
        ],
        "restore_rule": (
            "Archived seeds restore to disabled status "
            "and require a separate enable operation."
        ),
        "next_component": "Seed Protection",
        "next_pipeline_stage": (
            "Seed Eligibility Validation"
        ),
    }


__all__ = [
    "ALLOWED_UNIVERSAL_WEB_SEED_TRANSITIONS",
    "PROTECTED_SEED_METADATA_KEYS",
    "UNIVERSAL_WEB_SEED_CONTROLS_SCHEMA_VERSION",
    "append_seed_control_event",
    "archive_seed",
    "build_seed_control_result",
    "disable_seed",
    "enable_seed",
    "explain_universal_web_seed_controls_v1",
    "normalize_control_actor",
    "normalize_control_reason",
    "restore_seed",
    "update_metadata",
    "update_priority",
    "validate_seed_transition",
]
