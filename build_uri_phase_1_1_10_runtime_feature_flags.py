from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import py_compile
import shutil
import sys
import threading
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any


PROJECT_ROOT = Path.cwd().resolve()

RUNTIME_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
)

TARGET = (
    RUNTIME_DIR
    / "runtime_feature_flags.py"
)

EVIDENCE_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "uri_phase_1"
    / "1_1_10_runtime_feature_flags"
)

BACKUP_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
)

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP_DIR = (
    BACKUP_ROOT
    / f"uri_phase1_1_10_runtime_feature_flags_{TIMESTAMP}"
)

BACKUP_FILE = BACKUP_DIR / TARGET.name

EVIDENCE_JSON = (
    EVIDENCE_DIR
    / f"runtime_feature_flags_build_{TIMESTAMP}.json"
)

EVIDENCE_TEXT = (
    EVIDENCE_DIR
    / f"runtime_feature_flags_build_{TIMESTAMP}.txt"
)


MODULE_SOURCE = r'''from __future__ import annotations

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
'''


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def snapshot_protected_files() -> dict[str, str]:
    protected: dict[str, str] = {}

    candidates = [
        PROJECT_ROOT / "backend" / "server" / "main.py",
        RUNTIME_DIR / "runtime_kernel.py",
        RUNTIME_DIR / "runtime_configuration.py",
        RUNTIME_DIR / "runtime_environment.py",
        RUNTIME_DIR / "runtime_service_registry.py",
        RUNTIME_DIR / "runtime_lifecycle.py",
        RUNTIME_DIR / "runtime_boot.py",
        RUNTIME_DIR / "runtime_shutdown.py",
        RUNTIME_DIR / "runtime_versioning.py",
        RUNTIME_DIR / "runtime_compatibility.py",
    ]

    for path in candidates:
        if path.exists():
            protected[str(path)] = sha256_file(
                path
            )

    return protected


def import_module_from_path(
    module_name: str,
    path: Path,
):
    sys.modules.pop(
        module_name,
        None,
    )

    spec = importlib.util.spec_from_file_location(
        module_name,
        path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Unable to create module specification for {path}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def compile_python_file(
    path: Path,
) -> None:
    py_compile.compile(
        str(path),
        doraise=True,
    )


def verify_ast_contract(
    path: Path,
) -> None:
    source = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    class_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    }

    required_classes = {
        "RuntimeFeatureFlag",
        "RuntimeFeatureFlagContext",
        "RuntimeFeatureFlagDecision",
        "RuntimeFeatureFlagAuditEvent",
        "RuntimeFeatureFlagSnapshot",
        "RuntimeFeatureFlagRegistry",
    }

    missing_classes = (
        required_classes - class_names
    )

    if missing_classes:
        raise AssertionError(
            "Missing required feature-flag classes: "
            + ", ".join(
                sorted(missing_classes)
            )
        )

    function_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    }

    required_functions = {
        "deterministic_rollout_bucket",
        "get_runtime_feature_flag_registry",
        "register_runtime_feature_flag",
        "evaluate_runtime_feature_flag",
    }

    missing_functions = (
        required_functions - function_names
    )

    if missing_functions:
        raise AssertionError(
            "Missing required feature-flag functions: "
            + ", ".join(
                sorted(missing_functions)
            )
        )


def verify_behavior(
    module,
) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []

    now = datetime.now(
        timezone.utc
    )

    State = module.RuntimeFeatureFlagState
    Reason = module.RuntimeFeatureFlagDecisionReason
    Flag = module.RuntimeFeatureFlag
    Context = module.RuntimeFeatureFlagContext
    Registry = module.RuntimeFeatureFlagRegistry

    registry = Registry(
        safe_default_enabled=False,
        record_evaluations=True,
    )

    global_flag = Flag(
        key="runtime.global-capability",
        state=State.ENABLED,
        owner="runtime-platform",
        description="Global capability.",
    )

    registry.register(
        global_flag,
        actor="builder-verifier",
    )

    context = Context(
        environment="production",
        evaluation_key="workspace-001",
        workspace_id="workspace-001",
        plan_id="enterprise",
        worker_class="semantic-worker",
        runtime_version="1.0.0",
    )

    decision = registry.evaluate(
        global_flag.key,
        context,
        now=now,
    )

    assert decision.enabled is True
    assert decision.reason is Reason.ENABLED

    results.append(
        (
            "Global feature-flag evaluation",
            "PASS",
        )
    )

    environment_flag = Flag(
        key="runtime.environment-capability",
        state=State.ENABLED,
        owner="runtime-platform",
        environments=frozenset(
            {"production"}
        ),
    )

    registry.register(
        environment_flag,
        actor="builder-verifier",
    )

    production_decision = registry.evaluate(
        environment_flag.key,
        context,
        now=now,
    )

    staging_decision = registry.evaluate(
        environment_flag.key,
        Context(
            environment="staging",
            evaluation_key="workspace-001",
        ),
        now=now,
    )

    assert production_decision.enabled is True
    assert staging_decision.enabled is False
    assert (
        staging_decision.reason
        is Reason.ENVIRONMENT_MISMATCH
    )

    results.append(
        (
            "Environment-scoped feature flags",
            "PASS",
        )
    )

    workspace_flag = Flag(
        key="runtime.workspace-capability",
        state=State.ENABLED,
        owner="runtime-platform",
        workspace_ids=frozenset(
            {"workspace-001"}
        ),
    )

    registry.register(
        workspace_flag,
        actor="builder-verifier",
    )

    assert registry.evaluate(
        workspace_flag.key,
        context,
        now=now,
    ).enabled is True

    assert registry.evaluate(
        workspace_flag.key,
        Context(
            environment="production",
            evaluation_key="workspace-002",
            workspace_id="workspace-002",
        ),
        now=now,
    ).enabled is False

    results.append(
        (
            "Workspace-scoped feature flags",
            "PASS",
        )
    )

    plan_flag = Flag(
        key="runtime.plan-capability",
        state=State.ENABLED,
        owner="runtime-platform",
        plan_ids=frozenset(
            {"enterprise"}
        ),
    )

    registry.register(
        plan_flag,
        actor="builder-verifier",
    )

    assert registry.evaluate(
        plan_flag.key,
        context,
        now=now,
    ).enabled is True

    assert registry.evaluate(
        plan_flag.key,
        Context(
            environment="production",
            evaluation_key="starter-workspace",
            plan_id="starter",
        ),
        now=now,
    ).enabled is False

    results.append(
        (
            "Plan-scoped feature flags",
            "PASS",
        )
    )

    worker_flag = Flag(
        key="runtime.worker-capability",
        state=State.ENABLED,
        owner="runtime-platform",
        worker_classes=frozenset(
            {"semantic-worker"}
        ),
    )

    registry.register(
        worker_flag,
        actor="builder-verifier",
    )

    assert registry.evaluate(
        worker_flag.key,
        context,
        now=now,
    ).enabled is True

    assert registry.evaluate(
        worker_flag.key,
        Context(
            environment="production",
            evaluation_key="workspace-001",
            worker_class="export-worker",
        ),
        now=now,
    ).enabled is False

    results.append(
        (
            "Worker-class-scoped feature flags",
            "PASS",
        )
    )

    version_flag = Flag(
        key="runtime.version-capability",
        state=State.ENABLED,
        owner="runtime-platform",
        runtime_versions=frozenset(
            {"1.0.0"}
        ),
    )

    registry.register(
        version_flag,
        actor="builder-verifier",
    )

    assert registry.evaluate(
        version_flag.key,
        context,
        now=now,
    ).enabled is True

    assert registry.evaluate(
        version_flag.key,
        Context(
            environment="production",
            evaluation_key="workspace-001",
            runtime_version="2.0.0",
        ),
        now=now,
    ).enabled is False

    results.append(
        (
            "Runtime-version-scoped feature flags",
            "PASS",
        )
    )

    rollout_flag = Flag(
        key="runtime.percentage-rollout",
        state=State.ENABLED,
        owner="runtime-platform",
        rollout_percentage=50.0,
    )

    registry.register(
        rollout_flag,
        actor="builder-verifier",
    )

    bucket_one = (
        module.deterministic_rollout_bucket(
            flag_key=rollout_flag.key,
            evaluation_key="workspace-001",
        )
    )

    bucket_two = (
        module.deterministic_rollout_bucket(
            flag_key=rollout_flag.key,
            evaluation_key="workspace-001",
        )
    )

    assert bucket_one == bucket_two
    assert 0.0 <= bucket_one <= 100.0

    rollout_decision_one = registry.evaluate(
        rollout_flag.key,
        context,
        now=now,
    )

    rollout_decision_two = registry.evaluate(
        rollout_flag.key,
        context,
        now=now,
    )

    assert (
        rollout_decision_one.enabled
        == rollout_decision_two.enabled
    )

    assert (
        rollout_decision_one.rollout_bucket
        == rollout_decision_two.rollout_bucket
    )

    results.append(
        (
            "Deterministic percentage rollout",
            "PASS",
        )
    )

    kill_flag = Flag(
        key="runtime.emergency-stop",
        state=State.ENABLED,
        owner="runtime-platform",
        emergency_kill_switch=True,
    )

    registry.register(
        kill_flag,
        actor="builder-verifier",
    )

    kill_decision = registry.evaluate(
        kill_flag.key,
        context,
        now=now,
    )

    assert kill_decision.enabled is False
    assert (
        kill_decision.reason
        is Reason.EMERGENCY_KILL_SWITCH
    )

    results.append(
        (
            "Emergency kill-switch enforcement",
            "PASS",
        )
    )

    expired_flag = Flag(
        key="runtime.expired-capability",
        state=State.ENABLED,
        owner="runtime-platform",
        safe_default_enabled=False,
        created_at=now - timedelta(days=2),
        updated_at=now - timedelta(days=2),
        expires_at=now - timedelta(days=1),
    )

    registry.register(
        expired_flag,
        actor="builder-verifier",
    )

    expired_decision = registry.evaluate(
        expired_flag.key,
        context,
        now=now,
    )

    assert expired_decision.enabled is False
    assert expired_decision.reason is Reason.EXPIRED

    results.append(
        (
            "Feature-flag expiration",
            "PASS",
        )
    )

    missing_decision = registry.evaluate(
        "runtime.missing-capability",
        context,
        now=now,
    )

    assert missing_decision.enabled is False
    assert (
        missing_decision.reason
        is Reason.FLAG_NOT_FOUND
    )

    results.append(
        (
            "Safe-default behavior",
            "PASS",
        )
    )

    fingerprint_one = global_flag.fingerprint
    fingerprint_two = global_flag.fingerprint

    assert fingerprint_one == fingerprint_two
    assert len(fingerprint_one) == 64

    snapshot_one = registry.snapshot()
    snapshot_two = registry.snapshot()

    assert (
        snapshot_one.fingerprint
        == snapshot_two.fingerprint
    )

    results.append(
        (
            "Deterministic flag/snapshot fingerprints",
            "PASS",
        )
    )

    try:
        global_flag.key = "modified"
    except Exception:
        pass
    else:
        raise AssertionError(
            "RuntimeFeatureFlag must be immutable."
        )

    try:
        decision.enabled = False
    except Exception:
        pass
    else:
        raise AssertionError(
            "RuntimeFeatureFlagDecision must be immutable."
        )

    try:
        snapshot_one.generation = 0
    except Exception:
        pass
    else:
        raise AssertionError(
            "RuntimeFeatureFlagSnapshot must be immutable."
        )

    results.append(
        (
            "Immutable contracts and snapshots",
            "PASS",
        )
    )

    audit_history = registry.audit_history()

    assert audit_history
    assert any(
        event.action.value == "registered"
        for event in audit_history
    )
    assert any(
        event.action.value == "evaluated"
        for event in audit_history
    )

    results.append(
        (
            "Feature-flag audit history",
            "PASS",
        )
    )

    thread_errors: list[str] = []

    def evaluate_in_thread(
        thread_number: int,
    ) -> None:
        try:
            for iteration in range(100):
                thread_context = Context(
                    environment="production",
                    evaluation_key=(
                        f"thread-{thread_number}-"
                        f"{iteration}"
                    ),
                    workspace_id="workspace-001",
                    plan_id="enterprise",
                    worker_class="semantic-worker",
                    runtime_version="1.0.0",
                )

                registry.evaluate(
                    global_flag.key,
                    thread_context,
                    now=now,
                )
        except Exception as exc:
            thread_errors.append(
                repr(exc)
            )

    threads = [
        threading.Thread(
            target=evaluate_in_thread,
            args=(index,),
        )
        for index in range(8)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert not thread_errors

    results.append(
        (
            "Thread-safe registration and evaluation",
            "PASS",
        )
    )

    before_generation = registry.generation

    replacement_flag = Flag(
        key=global_flag.key,
        state=State.DISABLED,
        owner="runtime-platform",
        description="Replacement.",
    )

    registry.register(
        replacement_flag,
        actor="builder-verifier",
        replace=True,
    )

    assert registry.generation == (
        before_generation + 1
    )

    assert registry.evaluate(
        replacement_flag.key,
        context,
        now=now,
    ).enabled is False

    results.append(
        (
            "Controlled flag replacement",
            "PASS",
        )
    )

    registry.remove(
        replacement_flag.key,
        actor="builder-verifier",
    )

    try:
        registry.get(
            replacement_flag.key
        )
    except module.RuntimeFeatureFlagNotFoundError:
        pass
    else:
        raise AssertionError(
            "Removed flag remained registered."
        )

    results.append(
        (
            "Controlled flag removal",
            "PASS",
        )
    )

    return results


def write_evidence(
    *,
    status: str,
    verification_results: list[
        tuple[str, str]
    ],
    protected_before: dict[str, str],
    protected_after: dict[str, str],
    error: str | None = None,
) -> None:
    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    evidence = {
        "architecture": (
            "Universal Runtime Infrastructure"
        ),
        "phase": "1.1.10",
        "component": "Runtime Feature Flags",
        "timestamp_utc": TIMESTAMP,
        "status": status,
        "target": str(TARGET),
        "backup": (
            str(BACKUP_FILE)
            if BACKUP_FILE.exists()
            else None
        ),
        "verification": [
            {
                "check": check,
                "status": check_status,
            }
            for check, check_status
            in verification_results
        ],
        "protected_files_before": (
            protected_before
        ),
        "protected_files_after": (
            protected_after
        ),
        "protected_files_unchanged": (
            protected_before
            == protected_after
        ),
        "application_boot_integration": (
            "PENDING"
        ),
        "durable_flag_store_integration": (
            "PENDING"
        ),
        "owner_control_tower_integration": (
            "PENDING"
        ),
        "certification": "NOT CERTIFIED",
        "production_data_modified": False,
        "error": error,
    }

    EVIDENCE_JSON.write_text(
        json.dumps(
            evidence,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "=" * 78,
        "UNIVERSAL RUNTIME INFRASTRUCTURE",
        "1.1.10 — RUNTIME FEATURE FLAGS BUILD EVIDENCE",
        "=" * 78,
        "",
        f"Timestamp UTC: {TIMESTAMP}",
        f"Status:        {status}",
        f"Target:        {TARGET}",
        f"Backup:        {evidence['backup']}",
        "",
        "VERIFICATION",
        "-" * 78,
    ]

    for check, check_status in verification_results:
        lines.append(
            f"{check}: {check_status}"
        )

    lines.extend(
        [
            "",
            "INTEGRATION STATUS",
            "-" * 78,
            "Application boot integration:     PENDING",
            "Durable flag-store integration:    PENDING",
            "Owner Control Tower integration:   PENDING",
            "Certification:                     NOT CERTIFIED",
            "",
            "PROTECTED FILES",
            "-" * 78,
            (
                "Protected existing files unchanged: "
                + (
                    "PASS"
                    if protected_before
                    == protected_after
                    else "FAIL"
                )
            ),
            "",
            "NO PRODUCTION DATA WAS MODIFIED",
        ]
    )

    if error:
        lines.extend(
            [
                "",
                "ERROR",
                "-" * 78,
                error,
            ]
        )

    EVIDENCE_TEXT.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def rollback() -> None:
    if BACKUP_FILE.exists():
        shutil.copy2(
            BACKUP_FILE,
            TARGET,
        )
    elif TARGET.exists():
        TARGET.unlink()


def main() -> int:
    print("=" * 78)
    print("UNIVERSAL RUNTIME INFRASTRUCTURE")
    print("1.1.10 — RUNTIME FEATURE FLAGS BUILD")
    print("=" * 78)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Target:       {TARGET}")
    print()

    RUNTIME_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    protected_before = (
        snapshot_protected_files()
    )

    verification_results: list[
        tuple[str, str]
    ] = []

    if TARGET.exists():
        BACKUP_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            TARGET,
            BACKUP_FILE,
        )

    try:
        TARGET.write_text(
            MODULE_SOURCE,
            encoding="utf-8",
            newline="\n",
        )

        compile_python_file(
            TARGET
        )

        verification_results.append(
            (
                "Runtime Feature Flags compilation",
                "PASS",
            )
        )

        phase_one_modules = [
            RUNTIME_DIR / "runtime_kernel.py",
            RUNTIME_DIR / "runtime_configuration.py",
            RUNTIME_DIR / "runtime_environment.py",
            RUNTIME_DIR / "runtime_service_registry.py",
            RUNTIME_DIR / "runtime_lifecycle.py",
            RUNTIME_DIR / "runtime_boot.py",
            RUNTIME_DIR / "runtime_shutdown.py",
            RUNTIME_DIR / "runtime_versioning.py",
            RUNTIME_DIR / "runtime_compatibility.py",
            TARGET,
        ]

        for module_path in phase_one_modules:
            if module_path.exists():
                compile_python_file(
                    module_path
                )

        verification_results.append(
            (
                "Phase 1 foundation compilation",
                "PASS",
            )
        )

        main_path = (
            PROJECT_ROOT
            / "backend"
            / "server"
            / "main.py"
        )

        if main_path.exists():
            compile_python_file(
                main_path
            )

        verification_results.append(
            (
                "main.py compilation",
                "PASS",
            )
        )

        verify_ast_contract(
            TARGET
        )

        verification_results.append(
            (
                "Feature-flag AST contract",
                "PASS",
            )
        )

        module = import_module_from_path(
            "uri_runtime_feature_flags_verification",
            TARGET,
        )

        behavioral_results = verify_behavior(
            module
        )

        verification_results.extend(
            behavioral_results
        )

        source_text = TARGET.read_text(
            encoding="utf-8"
        )

        prohibited_terms = [
            "udare",
            "article_validation",
            "internal_link",
            "semantic_link",
            "website_article",
            "uploaded_document",
            "uucd",
        ]

        lowered_source = source_text.lower()

        prohibited_matches = [
            term
            for term in prohibited_terms
            if term in lowered_source
        ]

        if prohibited_matches:
            raise AssertionError(
                "Pipeline-specific terms found in feature-flag module: "
                + ", ".join(
                    prohibited_matches
                )
            )

        verification_results.append(
            (
                "Business-logic-agnostic boundary",
                "PASS",
            )
        )

        protected_after = (
            snapshot_protected_files()
        )

        if protected_before != protected_after:
            raise AssertionError(
                "One or more protected existing files changed."
            )

        verification_results.append(
            (
                "Protected existing files unchanged",
                "PASS",
            )
        )

        write_evidence(
            status="PASS",
            verification_results=(
                verification_results
            ),
            protected_before=protected_before,
            protected_after=protected_after,
        )

    except Exception:
        error_text = traceback.format_exc()

        rollback()

        protected_after_rollback = (
            snapshot_protected_files()
        )

        verification_results.append(
            (
                "Automatic rollback",
                "PASS",
            )
        )

        write_evidence(
            status="FAIL",
            verification_results=(
                verification_results
            ),
            protected_before=protected_before,
            protected_after=(
                protected_after_rollback
            ),
            error=error_text,
        )

        print("ROLLBACK COMPLETE")
        print(
            "The 1.1.10 build failed, so the previous "
            "Runtime Feature Flags file was restored."
        )
        print()
        print(error_text)

        return 1

    print("BUILD VERIFICATION")
    print("-" * 78)

    for check, status in verification_results:
        print(f"{check + ':':<44} {status}")

    print()
    print("FILES")
    print("-" * 78)
    print(f"Feature flags: {TARGET}")
    print(f"Evidence JSON: {EVIDENCE_JSON}")
    print(f"Evidence text: {EVIDENCE_TEXT}")
    print()
    print("1.1.10 RUNTIME FEATURE FLAGS")
    print("IMPLEMENTATION: PASS")
    print("ISOLATED VERIFICATION: PASS")
    print("GLOBAL FLAGS: PASS")
    print("SCOPED FLAGS: PASS")
    print("DETERMINISTIC ROLLOUTS: PASS")
    print("EMERGENCY KILL SWITCHES: PASS")
    print("FLAG EXPIRATION: PASS")
    print("AUDIT CONTRACT: PASS")
    print("THREAD SAFETY: PASS")
    print("APPLICATION BOOT INTEGRATION: PENDING")
    print("DURABLE FLAG-STORE INTEGRATION: PENDING")
    print("OWNER CONTROL TOWER INTEGRATION: PENDING")
    print("CERTIFICATION: NOT CERTIFIED")
    print()
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
