from __future__ import annotations

"""
Universal Runtime Infrastructure
Phase 1.1.10 — Runtime Feature Flags

This module provides the product-wide, business-logic-agnostic runtime
feature-flag infrastructure.

It supports:

- Global flags.
- Environment-scoped flags.
- Workspace-scoped flags.
- Plan-scoped flags.
- Worker-class-scoped flags.
- Runtime-version-scoped flags.
- Deterministic percentage rollouts.
- Emergency kill switches.
- Flag expiration.
- Flag ownership.
- Immutable decisions and snapshots.
- Thread-safe registration and evaluation.
- Persistent audit-event contracts.
- Safe defaults.

This module does not contain product pipeline business logic.
"""

import hashlib
import json
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping


class RuntimeFeatureFlagError(RuntimeError):
    """Base exception for runtime feature-flag failures."""


class RuntimeFeatureFlagValidationError(RuntimeFeatureFlagError):
    """Raised when a feature-flag contract is invalid."""


class RuntimeFeatureFlagConflictError(RuntimeFeatureFlagError):
    """Raised when registration conflicts with an existing flag."""


class RuntimeFeatureFlagNotFoundError(RuntimeFeatureFlagError):
    """Raised when a requested feature flag does not exist."""


class RuntimeFeatureFlagState(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class RuntimeFeatureFlagDecisionReason(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    SAFE_DEFAULT = "safe_default"
    FLAG_NOT_FOUND = "flag_not_found"
    EXPIRED = "expired"
    ENVIRONMENT_MISMATCH = "environment_mismatch"
    WORKSPACE_MISMATCH = "workspace_mismatch"
    PLAN_MISMATCH = "plan_mismatch"
    WORKER_CLASS_MISMATCH = "worker_class_mismatch"
    RUNTIME_VERSION_MISMATCH = "runtime_version_mismatch"
    ROLLOUT_EXCLUDED = "rollout_excluded"
    EMERGENCY_KILL_SWITCH = "emergency_kill_switch"


class RuntimeFeatureFlagAuditAction(str, Enum):
    REGISTERED = "registered"
    REPLACED = "replaced"
    REMOVED = "removed"
    EVALUATED = "evaluated"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalise_text(
    value: str,
    *,
    field_name: str,
) -> str:
    if not isinstance(value, str):
        raise RuntimeFeatureFlagValidationError(
            f"{field_name} must be a string."
        )

    normalised = value.strip()

    if not normalised:
        raise RuntimeFeatureFlagValidationError(
            f"{field_name} must not be empty."
        )

    return normalised


def _normalise_optional_text(
    value: str | None,
    *,
    field_name: str,
) -> str | None:
    if value is None:
        return None

    return _normalise_text(
        value,
        field_name=field_name,
    )


def _normalise_scope(
    values: Iterable[str] | None,
    *,
    field_name: str,
) -> frozenset[str]:
    if values is None:
        return frozenset()

    normalised: set[str] = set()

    for value in values:
        normalised.add(
            _normalise_text(
                value,
                field_name=field_name,
            )
        )

    return frozenset(normalised)


def _normalise_datetime(
    value: datetime | None,
    *,
    field_name: str,
) -> datetime | None:
    if value is None:
        return None

    if not isinstance(value, datetime):
        raise RuntimeFeatureFlagValidationError(
            f"{field_name} must be a datetime."
        )

    if value.tzinfo is None:
        raise RuntimeFeatureFlagValidationError(
            f"{field_name} must be timezone-aware."
        )

    return value.astimezone(timezone.utc)


def _freeze_mapping(
    values: Mapping[str, Any] | None,
) -> Mapping[str, Any]:
    if values is None:
        return MappingProxyType({})

    return MappingProxyType(
        dict(values)
    )


def _canonical_json(
    value: Mapping[str, Any],
) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _fingerprint(
    value: Mapping[str, Any],
) -> str:
    return hashlib.sha256(
        _canonical_json(value).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class RuntimeFeatureFlagContext:
    environment: str
    evaluation_key: str
    workspace_id: str | None = None
    plan_id: str | None = None
    worker_class: str | None = None
    runtime_version: str | None = None
    attributes: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "environment",
            _normalise_text(
                self.environment,
                field_name="environment",
            ),
        )

        object.__setattr__(
            self,
            "evaluation_key",
            _normalise_text(
                self.evaluation_key,
                field_name="evaluation_key",
            ),
        )

        object.__setattr__(
            self,
            "workspace_id",
            _normalise_optional_text(
                self.workspace_id,
                field_name="workspace_id",
            ),
        )

        object.__setattr__(
            self,
            "plan_id",
            _normalise_optional_text(
                self.plan_id,
                field_name="plan_id",
            ),
        )

        object.__setattr__(
            self,
            "worker_class",
            _normalise_optional_text(
                self.worker_class,
                field_name="worker_class",
            ),
        )

        object.__setattr__(
            self,
            "runtime_version",
            _normalise_optional_text(
                self.runtime_version,
                field_name="runtime_version",
            ),
        )

        object.__setattr__(
            self,
            "attributes",
            _freeze_mapping(
                self.attributes
            ),
        )


@dataclass(frozen=True, slots=True)
class RuntimeFeatureFlag:
    key: str
    state: RuntimeFeatureFlagState
    owner: str
    description: str = ""
    safe_default_enabled: bool = False
    emergency_kill_switch: bool = False
    rollout_percentage: float = 100.0
    environments: frozenset[str] = field(
        default_factory=frozenset
    )
    workspace_ids: frozenset[str] = field(
        default_factory=frozenset
    )
    plan_ids: frozenset[str] = field(
        default_factory=frozenset
    )
    worker_classes: frozenset[str] = field(
        default_factory=frozenset
    )
    runtime_versions: frozenset[str] = field(
        default_factory=frozenset
    )
    created_at: datetime = field(
        default_factory=_utc_now
    )
    updated_at: datetime = field(
        default_factory=_utc_now
    )
    expires_at: datetime | None = None
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "key",
            _normalise_text(
                self.key,
                field_name="key",
            ),
        )

        if not isinstance(
            self.state,
            RuntimeFeatureFlagState,
        ):
            try:
                object.__setattr__(
                    self,
                    "state",
                    RuntimeFeatureFlagState(
                        self.state
                    ),
                )
            except Exception as exc:
                raise RuntimeFeatureFlagValidationError(
                    "state is invalid."
                ) from exc

        object.__setattr__(
            self,
            "owner",
            _normalise_text(
                self.owner,
                field_name="owner",
            ),
        )

        if not isinstance(
            self.description,
            str,
        ):
            raise RuntimeFeatureFlagValidationError(
                "description must be a string."
            )

        percentage = float(
            self.rollout_percentage
        )

        if percentage < 0.0 or percentage > 100.0:
            raise RuntimeFeatureFlagValidationError(
                "rollout_percentage must be between 0 and 100."
            )

        object.__setattr__(
            self,
            "rollout_percentage",
            percentage,
        )

        object.__setattr__(
            self,
            "environments",
            _normalise_scope(
                self.environments,
                field_name="environments",
            ),
        )

        object.__setattr__(
            self,
            "workspace_ids",
            _normalise_scope(
                self.workspace_ids,
                field_name="workspace_ids",
            ),
        )

        object.__setattr__(
            self,
            "plan_ids",
            _normalise_scope(
                self.plan_ids,
                field_name="plan_ids",
            ),
        )

        object.__setattr__(
            self,
            "worker_classes",
            _normalise_scope(
                self.worker_classes,
                field_name="worker_classes",
            ),
        )

        object.__setattr__(
            self,
            "runtime_versions",
            _normalise_scope(
                self.runtime_versions,
                field_name="runtime_versions",
            ),
        )

        created_at = _normalise_datetime(
            self.created_at,
            field_name="created_at",
        )

        updated_at = _normalise_datetime(
            self.updated_at,
            field_name="updated_at",
        )

        expires_at = _normalise_datetime(
            self.expires_at,
            field_name="expires_at",
        )

        if created_at is None or updated_at is None:
            raise RuntimeFeatureFlagValidationError(
                "created_at and updated_at are required."
            )

        if updated_at < created_at:
            raise RuntimeFeatureFlagValidationError(
                "updated_at must not be earlier than created_at."
            )

        if (
            expires_at is not None
            and expires_at <= created_at
        ):
            raise RuntimeFeatureFlagValidationError(
                "expires_at must be later than created_at."
            )

        object.__setattr__(
            self,
            "created_at",
            created_at,
        )

        object.__setattr__(
            self,
            "updated_at",
            updated_at,
        )

        object.__setattr__(
            self,
            "expires_at",
            expires_at,
        )

        object.__setattr__(
            self,
            "metadata",
            _freeze_mapping(
                self.metadata
            ),
        )

    @property
    def fingerprint(self) -> str:
        return _fingerprint(
            self.to_dict()
        )

    def is_expired(
        self,
        *,
        now: datetime | None = None,
    ) -> bool:
        if self.expires_at is None:
            return False

        reference = now or _utc_now()

        if reference.tzinfo is None:
            raise RuntimeFeatureFlagValidationError(
                "now must be timezone-aware."
            )

        return (
            reference.astimezone(timezone.utc)
            >= self.expires_at
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "state": self.state.value,
            "owner": self.owner,
            "description": self.description,
            "safe_default_enabled": (
                self.safe_default_enabled
            ),
            "emergency_kill_switch": (
                self.emergency_kill_switch
            ),
            "rollout_percentage": (
                self.rollout_percentage
            ),
            "environments": sorted(
                self.environments
            ),
            "workspace_ids": sorted(
                self.workspace_ids
            ),
            "plan_ids": sorted(
                self.plan_ids
            ),
            "worker_classes": sorted(
                self.worker_classes
            ),
            "runtime_versions": sorted(
                self.runtime_versions
            ),
            "created_at": (
                self.created_at.isoformat()
            ),
            "updated_at": (
                self.updated_at.isoformat()
            ),
            "expires_at": (
                self.expires_at.isoformat()
                if self.expires_at is not None
                else None
            ),
            "metadata": dict(
                self.metadata
            ),
        }


@dataclass(frozen=True, slots=True)
class RuntimeFeatureFlagDecision:
    flag_key: str
    enabled: bool
    reason: RuntimeFeatureFlagDecisionReason
    evaluation_key: str
    evaluated_at: datetime
    flag_fingerprint: str | None
    rollout_bucket: float | None = None
    details: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "flag_key",
            _normalise_text(
                self.flag_key,
                field_name="flag_key",
            ),
        )

        object.__setattr__(
            self,
            "evaluation_key",
            _normalise_text(
                self.evaluation_key,
                field_name="evaluation_key",
            ),
        )

        evaluated_at = _normalise_datetime(
            self.evaluated_at,
            field_name="evaluated_at",
        )

        if evaluated_at is None:
            raise RuntimeFeatureFlagValidationError(
                "evaluated_at is required."
            )

        object.__setattr__(
            self,
            "evaluated_at",
            evaluated_at,
        )

        object.__setattr__(
            self,
            "details",
            _freeze_mapping(
                self.details
            ),
        )


@dataclass(frozen=True, slots=True)
class RuntimeFeatureFlagAuditEvent:
    sequence: int
    action: RuntimeFeatureFlagAuditAction
    flag_key: str
    actor: str
    occurred_at: datetime
    flag_fingerprint: str | None = None
    details: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if self.sequence < 1:
            raise RuntimeFeatureFlagValidationError(
                "sequence must be at least 1."
            )

        object.__setattr__(
            self,
            "flag_key",
            _normalise_text(
                self.flag_key,
                field_name="flag_key",
            ),
        )

        object.__setattr__(
            self,
            "actor",
            _normalise_text(
                self.actor,
                field_name="actor",
            ),
        )

        occurred_at = _normalise_datetime(
            self.occurred_at,
            field_name="occurred_at",
        )

        if occurred_at is None:
            raise RuntimeFeatureFlagValidationError(
                "occurred_at is required."
            )

        object.__setattr__(
            self,
            "occurred_at",
            occurred_at,
        )

        object.__setattr__(
            self,
            "details",
            _freeze_mapping(
                self.details
            ),
        )


@dataclass(frozen=True, slots=True)
class RuntimeFeatureFlagSnapshot:
    generation: int
    captured_at: datetime
    flags: tuple[RuntimeFeatureFlag, ...]
    fingerprint: str

    def __post_init__(self) -> None:
        if self.generation < 0:
            raise RuntimeFeatureFlagValidationError(
                "generation must not be negative."
            )

        captured_at = _normalise_datetime(
            self.captured_at,
            field_name="captured_at",
        )

        if captured_at is None:
            raise RuntimeFeatureFlagValidationError(
                "captured_at is required."
            )

        object.__setattr__(
            self,
            "captured_at",
            captured_at,
        )

        object.__setattr__(
            self,
            "flags",
            tuple(self.flags),
        )


def deterministic_rollout_bucket(
    *,
    flag_key: str,
    evaluation_key: str,
) -> float:
    normalised_flag_key = _normalise_text(
        flag_key,
        field_name="flag_key",
    )

    normalised_evaluation_key = _normalise_text(
        evaluation_key,
        field_name="evaluation_key",
    )

    digest = hashlib.sha256(
        (
            normalised_flag_key
            + ":"
            + normalised_evaluation_key
        ).encode("utf-8")
    ).digest()

    integer = int.from_bytes(
        digest[:8],
        byteorder="big",
        signed=False,
    )

    return (
        integer
        / float((1 << 64) - 1)
        * 100.0
    )


class RuntimeFeatureFlagRegistry:
    """
    Thread-safe feature-flag registry and evaluator.

    Registration is separate from persistence. A durable adapter may persist
    RuntimeFeatureFlag, RuntimeFeatureFlagSnapshot, and
    RuntimeFeatureFlagAuditEvent contracts without changing evaluation logic.
    """

    def __init__(
        self,
        *,
        safe_default_enabled: bool = False,
        record_evaluations: bool = True,
    ) -> None:
        self._safe_default_enabled = bool(
            safe_default_enabled
        )
        self._record_evaluations = bool(
            record_evaluations
        )
        self._flags: dict[
            str,
            RuntimeFeatureFlag,
        ] = {}
        self._audit_events: list[
            RuntimeFeatureFlagAuditEvent
        ] = []
        self._generation = 0
        self._audit_sequence = 0
        self._lock = threading.RLock()

    @property
    def generation(self) -> int:
        with self._lock:
            return self._generation

    def register(
        self,
        flag: RuntimeFeatureFlag,
        *,
        actor: str,
        replace: bool = False,
    ) -> RuntimeFeatureFlag:
        if not isinstance(
            flag,
            RuntimeFeatureFlag,
        ):
            raise RuntimeFeatureFlagValidationError(
                "flag must be a RuntimeFeatureFlag."
            )

        normalised_actor = _normalise_text(
            actor,
            field_name="actor",
        )

        with self._lock:
            existing = self._flags.get(
                flag.key
            )

            if existing is not None and not replace:
                raise RuntimeFeatureFlagConflictError(
                    f"Feature flag already exists: {flag.key}"
                )

            self._flags[flag.key] = flag
            self._generation += 1

            action = (
                RuntimeFeatureFlagAuditAction.REPLACED
                if existing is not None
                else RuntimeFeatureFlagAuditAction.REGISTERED
            )

            self._append_audit_event(
                action=action,
                flag_key=flag.key,
                actor=normalised_actor,
                flag_fingerprint=flag.fingerprint,
                details={
                    "generation": self._generation,
                },
            )

            return flag

    def remove(
        self,
        flag_key: str,
        *,
        actor: str,
    ) -> RuntimeFeatureFlag:
        normalised_key = _normalise_text(
            flag_key,
            field_name="flag_key",
        )

        normalised_actor = _normalise_text(
            actor,
            field_name="actor",
        )

        with self._lock:
            try:
                flag = self._flags.pop(
                    normalised_key
                )
            except KeyError as exc:
                raise RuntimeFeatureFlagNotFoundError(
                    f"Feature flag does not exist: {normalised_key}"
                ) from exc

            self._generation += 1

            self._append_audit_event(
                action=RuntimeFeatureFlagAuditAction.REMOVED,
                flag_key=normalised_key,
                actor=normalised_actor,
                flag_fingerprint=flag.fingerprint,
                details={
                    "generation": self._generation,
                },
            )

            return flag

    def get(
        self,
        flag_key: str,
    ) -> RuntimeFeatureFlag:
        normalised_key = _normalise_text(
            flag_key,
            field_name="flag_key",
        )

        with self._lock:
            flag = self._flags.get(
                normalised_key
            )

            if flag is None:
                raise RuntimeFeatureFlagNotFoundError(
                    f"Feature flag does not exist: {normalised_key}"
                )

            return flag

    def evaluate(
        self,
        flag_key: str,
        context: RuntimeFeatureFlagContext,
        *,
        now: datetime | None = None,
        actor: str = "runtime",
    ) -> RuntimeFeatureFlagDecision:
        if not isinstance(
            context,
            RuntimeFeatureFlagContext,
        ):
            raise RuntimeFeatureFlagValidationError(
                "context must be a RuntimeFeatureFlagContext."
            )

        normalised_key = _normalise_text(
            flag_key,
            field_name="flag_key",
        )

        normalised_actor = _normalise_text(
            actor,
            field_name="actor",
        )

        reference = now or _utc_now()

        if reference.tzinfo is None:
            raise RuntimeFeatureFlagValidationError(
                "now must be timezone-aware."
            )

        reference = reference.astimezone(
            timezone.utc
        )

        with self._lock:
            flag = self._flags.get(
                normalised_key
            )

            if flag is None:
                decision = RuntimeFeatureFlagDecision(
                    flag_key=normalised_key,
                    enabled=self._safe_default_enabled,
                    reason=(
                        RuntimeFeatureFlagDecisionReason.FLAG_NOT_FOUND
                    ),
                    evaluation_key=context.evaluation_key,
                    evaluated_at=reference,
                    flag_fingerprint=None,
                    details={
                        "safe_default_enabled": (
                            self._safe_default_enabled
                        ),
                    },
                )

                self._record_decision(
                    decision,
                    actor=normalised_actor,
                )

                return decision

            decision = self._evaluate_flag(
                flag,
                context,
                now=reference,
            )

            self._record_decision(
                decision,
                actor=normalised_actor,
            )

            return decision

    def snapshot(
        self,
    ) -> RuntimeFeatureFlagSnapshot:
        with self._lock:
            flags = tuple(
                sorted(
                    self._flags.values(),
                    key=lambda item: item.key,
                )
            )

            payload = {
                "generation": self._generation,
                "flags": [
                    flag.to_dict()
                    for flag in flags
                ],
            }

            return RuntimeFeatureFlagSnapshot(
                generation=self._generation,
                captured_at=_utc_now(),
                flags=flags,
                fingerprint=_fingerprint(
                    payload
                ),
            )

    def audit_history(
        self,
    ) -> tuple[RuntimeFeatureFlagAuditEvent, ...]:
        with self._lock:
            return tuple(
                self._audit_events
            )

    def _evaluate_flag(
        self,
        flag: RuntimeFeatureFlag,
        context: RuntimeFeatureFlagContext,
        *,
        now: datetime,
    ) -> RuntimeFeatureFlagDecision:
        base = {
            "flag_key": flag.key,
            "evaluation_key": context.evaluation_key,
            "evaluated_at": now,
            "flag_fingerprint": flag.fingerprint,
        }

        if flag.emergency_kill_switch:
            return RuntimeFeatureFlagDecision(
                **base,
                enabled=False,
                reason=(
                    RuntimeFeatureFlagDecisionReason.EMERGENCY_KILL_SWITCH
                ),
            )

        if flag.is_expired(now=now):
            return RuntimeFeatureFlagDecision(
                **base,
                enabled=flag.safe_default_enabled,
                reason=RuntimeFeatureFlagDecisionReason.EXPIRED,
                details={
                    "safe_default_enabled": (
                        flag.safe_default_enabled
                    ),
                },
            )

        if (
            flag.state
            is RuntimeFeatureFlagState.DISABLED
        ):
            return RuntimeFeatureFlagDecision(
                **base,
                enabled=False,
                reason=RuntimeFeatureFlagDecisionReason.DISABLED,
            )

        if (
            flag.environments
            and context.environment
            not in flag.environments
        ):
            return RuntimeFeatureFlagDecision(
                **base,
                enabled=flag.safe_default_enabled,
                reason=(
                    RuntimeFeatureFlagDecisionReason.ENVIRONMENT_MISMATCH
                ),
            )

        if (
            flag.workspace_ids
            and context.workspace_id
            not in flag.workspace_ids
        ):
            return RuntimeFeatureFlagDecision(
                **base,
                enabled=flag.safe_default_enabled,
                reason=(
                    RuntimeFeatureFlagDecisionReason.WORKSPACE_MISMATCH
                ),
            )

        if (
            flag.plan_ids
            and context.plan_id
            not in flag.plan_ids
        ):
            return RuntimeFeatureFlagDecision(
                **base,
                enabled=flag.safe_default_enabled,
                reason=(
                    RuntimeFeatureFlagDecisionReason.PLAN_MISMATCH
                ),
            )

        if (
            flag.worker_classes
            and context.worker_class
            not in flag.worker_classes
        ):
            return RuntimeFeatureFlagDecision(
                **base,
                enabled=flag.safe_default_enabled,
                reason=(
                    RuntimeFeatureFlagDecisionReason.WORKER_CLASS_MISMATCH
                ),
            )

        if (
            flag.runtime_versions
            and context.runtime_version
            not in flag.runtime_versions
        ):
            return RuntimeFeatureFlagDecision(
                **base,
                enabled=flag.safe_default_enabled,
                reason=(
                    RuntimeFeatureFlagDecisionReason.RUNTIME_VERSION_MISMATCH
                ),
            )

        rollout_bucket = deterministic_rollout_bucket(
            flag_key=flag.key,
            evaluation_key=context.evaluation_key,
        )

        if (
            rollout_bucket
            >= flag.rollout_percentage
        ):
            return RuntimeFeatureFlagDecision(
                **base,
                enabled=flag.safe_default_enabled,
                reason=(
                    RuntimeFeatureFlagDecisionReason.ROLLOUT_EXCLUDED
                ),
                rollout_bucket=rollout_bucket,
                details={
                    "rollout_percentage": (
                        flag.rollout_percentage
                    ),
                },
            )

        return RuntimeFeatureFlagDecision(
            **base,
            enabled=True,
            reason=RuntimeFeatureFlagDecisionReason.ENABLED,
            rollout_bucket=rollout_bucket,
            details={
                "rollout_percentage": (
                    flag.rollout_percentage
                ),
            },
        )

    def _record_decision(
        self,
        decision: RuntimeFeatureFlagDecision,
        *,
        actor: str,
    ) -> None:
        if not self._record_evaluations:
            return

        self._append_audit_event(
            action=RuntimeFeatureFlagAuditAction.EVALUATED,
            flag_key=decision.flag_key,
            actor=actor,
            flag_fingerprint=decision.flag_fingerprint,
            details={
                "enabled": decision.enabled,
                "reason": decision.reason.value,
                "evaluation_key": (
                    decision.evaluation_key
                ),
                "rollout_bucket": (
                    decision.rollout_bucket
                ),
            },
        )

    def _append_audit_event(
        self,
        *,
        action: RuntimeFeatureFlagAuditAction,
        flag_key: str,
        actor: str,
        flag_fingerprint: str | None,
        details: Mapping[str, Any],
    ) -> None:
        self._audit_sequence += 1

        self._audit_events.append(
            RuntimeFeatureFlagAuditEvent(
                sequence=self._audit_sequence,
                action=action,
                flag_key=flag_key,
                actor=actor,
                occurred_at=_utc_now(),
                flag_fingerprint=flag_fingerprint,
                details=details,
            )
        )


_default_registry = RuntimeFeatureFlagRegistry()


def get_runtime_feature_flag_registry(
) -> RuntimeFeatureFlagRegistry:
    return _default_registry


def register_runtime_feature_flag(
    flag: RuntimeFeatureFlag,
    *,
    actor: str,
    replace: bool = False,
) -> RuntimeFeatureFlag:
    return _default_registry.register(
        flag,
        actor=actor,
        replace=replace,
    )


def evaluate_runtime_feature_flag(
    flag_key: str,
    context: RuntimeFeatureFlagContext,
    *,
    now: datetime | None = None,
    actor: str = "runtime",
) -> RuntimeFeatureFlagDecision:
    return _default_registry.evaluate(
        flag_key,
        context,
        now=now,
        actor=actor,
    )


__all__ = [
    "RuntimeFeatureFlag",
    "RuntimeFeatureFlagAuditAction",
    "RuntimeFeatureFlagAuditEvent",
    "RuntimeFeatureFlagConflictError",
    "RuntimeFeatureFlagContext",
    "RuntimeFeatureFlagDecision",
    "RuntimeFeatureFlagDecisionReason",
    "RuntimeFeatureFlagError",
    "RuntimeFeatureFlagNotFoundError",
    "RuntimeFeatureFlagRegistry",
    "RuntimeFeatureFlagSnapshot",
    "RuntimeFeatureFlagState",
    "RuntimeFeatureFlagValidationError",
    "deterministic_rollout_bucket",
    "evaluate_runtime_feature_flag",
    "get_runtime_feature_flag_registry",
    "register_runtime_feature_flag",
]
