# -*- coding: utf-8 -*-
"""Runtime Schema Lifecycle and Deprecation Policy.

This module owns:

* the legal schema lifecycle graph;
* lifecycle-transition validation;
* immutable deprecation policies;
* notice-window and sunset evaluation;
* feature-flag-staged enforcement;
* quarantine, suspension, restoration, and retirement rules.

It does not mutate registry state. The registry invokes this policy layer
before replacing immutable schema definitions.

The module remains business-logic agnostic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from types import MappingProxyType
from typing import Any, Final, Mapping, Protocol, runtime_checkable

from .fingerprint import validate_schema_coordinate
from .serialization import structure_fingerprint
from .types import (
    EnforcementLevel,
    SchemaLifecycleState,
    SchemaRegistryError,
    is_canonical_timestamp,
    parse_canonical_timestamp,
    utc_now_iso,
)


DEPRECATION_ENFORCEMENT_FLAG: Final[str] = (
    "runtime.schema.deprecation_enforcement"
)

MAX_NOTICE_PERIOD_DAYS: Final[int] = 3650


@runtime_checkable
class FeatureFlagProvider(
    Protocol
):
    """Minimal feature-flag contract required by deprecation policy."""

    def is_enabled(
        self,
        flag_name: str,
    ) -> bool:
        """Return whether one runtime feature flag is enabled."""


LEGAL_LIFECYCLE_TRANSITIONS: Final[
    Mapping[
        SchemaLifecycleState,
        frozenset[SchemaLifecycleState],
    ]
] = MappingProxyType(
    {
        SchemaLifecycleState.DRAFT: frozenset(
            {
                SchemaLifecycleState.REGISTERED,
                SchemaLifecycleState.QUARANTINED,
                SchemaLifecycleState.RETIRED,
            }
        ),
        SchemaLifecycleState.REGISTERED: frozenset(
            {
                SchemaLifecycleState.ACTIVE,
                SchemaLifecycleState.SUSPENDED,
                SchemaLifecycleState.QUARANTINED,
                SchemaLifecycleState.RETIRED,
            }
        ),
        SchemaLifecycleState.ACTIVE: frozenset(
            {
                SchemaLifecycleState.SUSPENDED,
                SchemaLifecycleState.DEPRECATED,
                SchemaLifecycleState.QUARANTINED,
            }
        ),
        SchemaLifecycleState.SUSPENDED: frozenset(
            {
                SchemaLifecycleState.ACTIVE,
                SchemaLifecycleState.DEPRECATED,
                SchemaLifecycleState.QUARANTINED,
                SchemaLifecycleState.RETIRED,
            }
        ),
        SchemaLifecycleState.DEPRECATED: frozenset(
            {
                SchemaLifecycleState.ACTIVE,
                SchemaLifecycleState.SUSPENDED,
                SchemaLifecycleState.QUARANTINED,
                SchemaLifecycleState.RETIRED,
            }
        ),
        SchemaLifecycleState.QUARANTINED: frozenset(
            {
                SchemaLifecycleState.REGISTERED,
                SchemaLifecycleState.ACTIVE,
                SchemaLifecycleState.SUSPENDED,
                SchemaLifecycleState.DEPRECATED,
                SchemaLifecycleState.RETIRED,
            }
        ),
        SchemaLifecycleState.RETIRED: frozenset(),
    }
)


def _coerce_state(
    value: SchemaLifecycleState | str,
    *,
    field_name: str,
) -> SchemaLifecycleState:
    if isinstance(
        value,
        SchemaLifecycleState,
    ):
        return value

    try:
        return SchemaLifecycleState(
            value
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise SchemaRegistryError(
            f"{field_name} is not a valid lifecycle state"
        ) from exc


def is_legal_transition(
    current: SchemaLifecycleState | str,
    target: SchemaLifecycleState | str,
) -> bool:
    """Return whether one lifecycle transition is legal."""
    current_state = _coerce_state(
        current,
        field_name="current",
    )

    target_state = _coerce_state(
        target,
        field_name="target",
    )

    return target_state in (
        LEGAL_LIFECYCLE_TRANSITIONS[
            current_state
        ]
    )


def require_legal_transition(
    current: SchemaLifecycleState | str,
    target: SchemaLifecycleState | str,
) -> None:
    """Raise when a lifecycle transition is illegal."""
    current_state = _coerce_state(
        current,
        field_name="current",
    )

    target_state = _coerce_state(
        target,
        field_name="target",
    )

    if current_state is target_state:
        raise SchemaRegistryError(
            "lifecycle transition must change state"
        )

    if not is_legal_transition(
        current_state,
        target_state,
    ):
        raise SchemaRegistryError(
            "illegal lifecycle transition "
            f"{current_state.value} -> "
            f"{target_state.value}"
        )


@dataclass(
    frozen=True,
    slots=True,
)
class DeprecationPolicy:
    """Immutable policy attached to a deprecated schema version."""

    notice_period_days: int
    deprecated_at: str = ""
    sunset_at: str | None = None
    replacement_coordinate: str | None = None
    enforcement: EnforcementLevel = EnforcementLevel.WARN
    reason: str = ""

    def __post_init__(self) -> None:
        if (
            not isinstance(
                self.notice_period_days,
                int,
            )
            or isinstance(
                self.notice_period_days,
                bool,
            )
            or self.notice_period_days < 0
            or self.notice_period_days
            > MAX_NOTICE_PERIOD_DAYS
        ):
            raise SchemaRegistryError(
                "notice_period_days must be an integer "
                f"between 0 and {MAX_NOTICE_PERIOD_DAYS}"
            )

        if not self.deprecated_at:
            object.__setattr__(
                self,
                "deprecated_at",
                utc_now_iso(),
            )

        if not is_canonical_timestamp(
            self.deprecated_at
        ):
            raise SchemaRegistryError(
                "deprecated_at must be a canonical UTC timestamp"
            )

        if (
            self.sunset_at is not None
            and not is_canonical_timestamp(
                self.sunset_at
            )
        ):
            raise SchemaRegistryError(
                "sunset_at must be a canonical UTC timestamp"
            )

        if (
            self.replacement_coordinate
            is not None
        ):
            try:
                validate_schema_coordinate(
                    self.replacement_coordinate
                )
            except Exception as exc:
                raise SchemaRegistryError(
                    "replacement_coordinate must be canonical"
                ) from exc

        if not isinstance(
            self.enforcement,
            EnforcementLevel,
        ):
            try:
                object.__setattr__(
                    self,
                    "enforcement",
                    EnforcementLevel(
                        self.enforcement
                    ),
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise SchemaRegistryError(
                    "invalid deprecation enforcement level"
                ) from exc

        if not isinstance(
            self.reason,
            str,
        ):
            raise SchemaRegistryError(
                "reason must be a string"
            )

        deprecated_at = (
            parse_canonical_timestamp(
                self.deprecated_at
            )
        )

        minimum_sunset = (
            deprecated_at
            + timedelta(
                days=self.notice_period_days
            )
        )

        if self.sunset_at is not None:
            sunset_at = (
                parse_canonical_timestamp(
                    self.sunset_at
                )
            )

            if sunset_at < minimum_sunset:
                raise SchemaRegistryError(
                    "sunset_at violates the configured "
                    "notice period"
                )

    @property
    def fingerprint(
        self,
    ) -> str:
        """Return deterministic policy fingerprint."""
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    @property
    def minimum_sunset_at(
        self,
    ) -> str:
        """Return earliest legal sunset timestamp."""
        deprecated_at = (
            parse_canonical_timestamp(
                self.deprecated_at
            )
        )

        return (
            deprecated_at
            + timedelta(
                days=self.notice_period_days
            )
        ).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

    def notice_period_satisfied(
        self,
        now: datetime,
    ) -> bool:
        """Return whether the minimum notice period has elapsed."""
        effective_now = _require_aware_datetime(
            now
        )

        minimum = (
            parse_canonical_timestamp(
                self.minimum_sunset_at
            )
        )

        return effective_now >= minimum

    def sunset_passed(
        self,
        now: datetime,
    ) -> bool:
        """Return whether a configured sunset has passed."""
        if self.sunset_at is None:
            return False

        effective_now = _require_aware_datetime(
            now
        )

        return effective_now >= (
            parse_canonical_timestamp(
                self.sunset_at
            )
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        """Return complete JSON-native policy data."""
        return {
            "notice_period_days": (
                self.notice_period_days
            ),
            "deprecated_at": (
                self.deprecated_at
            ),
            "minimum_sunset_at": (
                self.minimum_sunset_at
            ),
            "sunset_at": self.sunset_at,
            "replacement_coordinate": (
                self.replacement_coordinate
            ),
            "enforcement": (
                self.enforcement.value
            ),
            "reason": self.reason,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class DeprecationEvaluation:
    """Immutable evaluation of one policy at one point in time."""

    policy_fingerprint: str
    evaluated_at: str
    effective_enforcement: EnforcementLevel
    notice_period_satisfied: bool
    sunset_passed: bool
    usage_blocked: bool

    def __post_init__(self) -> None:
        if (
            not isinstance(
                self.policy_fingerprint,
                str,
            )
            or len(
                self.policy_fingerprint
            )
            != 64
        ):
            raise SchemaRegistryError(
                "policy_fingerprint must be a "
                "64-character digest"
            )

        if not is_canonical_timestamp(
            self.evaluated_at
        ):
            raise SchemaRegistryError(
                "evaluated_at must be canonical"
            )

        if not isinstance(
            self.effective_enforcement,
            EnforcementLevel,
        ):
            raise SchemaRegistryError(
                "effective_enforcement must be "
                "an EnforcementLevel"
            )

        expected_blocked = (
            self.effective_enforcement
            is EnforcementLevel.BLOCK
            and self.notice_period_satisfied
            and self.sunset_passed
        )

        if (
            self.usage_blocked
            != expected_blocked
        ):
            raise SchemaRegistryError(
                "usage_blocked is inconsistent"
            )

    @property
    def fingerprint(
        self,
    ) -> str:
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "policy_fingerprint": (
                self.policy_fingerprint
            ),
            "evaluated_at": (
                self.evaluated_at
            ),
            "effective_enforcement": (
                self.effective_enforcement.value
            ),
            "notice_period_satisfied": (
                self.notice_period_satisfied
            ),
            "sunset_passed": (
                self.sunset_passed
            ),
            "usage_blocked": (
                self.usage_blocked
            ),
        }


def _require_aware_datetime(
    value: datetime,
) -> datetime:
    if not isinstance(
        value,
        datetime,
    ):
        raise SchemaRegistryError(
            "now must be a datetime"
        )

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise SchemaRegistryError(
            "now must be timezone-aware"
        )

    return value.astimezone(
        timezone.utc
    )


class DeprecationEngine:
    """Evaluate deprecation policies with staged enforcement."""

    def __init__(
        self,
        feature_flags: FeatureFlagProvider | None = None,
    ) -> None:
        if (
            feature_flags is not None
            and not isinstance(
                feature_flags,
                FeatureFlagProvider,
            )
        ):
            raise SchemaRegistryError(
                "feature_flags does not satisfy "
                "FeatureFlagProvider"
            )

        self._feature_flags = feature_flags

    def effective_enforcement(
        self,
        policy: DeprecationPolicy,
    ) -> EnforcementLevel:
        """Return staged enforcement level.

        BLOCK degrades to WARN until the runtime feature flag is enabled.
        """
        if not isinstance(
            policy,
            DeprecationPolicy,
        ):
            raise SchemaRegistryError(
                "policy must be a DeprecationPolicy"
            )

        if (
            policy.enforcement
            is EnforcementLevel.WARN
        ):
            return EnforcementLevel.WARN

        if self._feature_flags is None:
            return EnforcementLevel.WARN

        try:
            enabled = bool(
                self._feature_flags.is_enabled(
                    DEPRECATION_ENFORCEMENT_FLAG
                )
            )
        except Exception as exc:
            raise SchemaRegistryError(
                "feature-flag provider failed"
            ) from exc

        return (
            EnforcementLevel.BLOCK
            if enabled
            else EnforcementLevel.WARN
        )

    def evaluate(
        self,
        policy: DeprecationPolicy,
        now: datetime,
    ) -> DeprecationEvaluation:
        """Return immutable evaluation evidence."""
        if not isinstance(
            policy,
            DeprecationPolicy,
        ):
            raise SchemaRegistryError(
                "policy must be a DeprecationPolicy"
            )

        effective_now = (
            _require_aware_datetime(
                now
            )
        )

        effective_enforcement = (
            self.effective_enforcement(
                policy
            )
        )

        notice_satisfied = (
            policy.notice_period_satisfied(
                effective_now
            )
        )

        sunset_passed = (
            policy.sunset_passed(
                effective_now
            )
        )

        return DeprecationEvaluation(
            policy_fingerprint=(
                policy.fingerprint
            ),
            evaluated_at=(
                effective_now.strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                )
            ),
            effective_enforcement=(
                effective_enforcement
            ),
            notice_period_satisfied=(
                notice_satisfied
            ),
            sunset_passed=(
                sunset_passed
            ),
            usage_blocked=(
                effective_enforcement
                is EnforcementLevel.BLOCK
                and notice_satisfied
                and sunset_passed
            ),
        )

    def usage_blocked(
        self,
        policy: DeprecationPolicy,
        now: datetime,
    ) -> bool:
        """Return whether use must be rejected."""
        return self.evaluate(
            policy,
            now,
        ).usage_blocked


__all__ = [
    "DEPRECATION_ENFORCEMENT_FLAG",
    "LEGAL_LIFECYCLE_TRANSITIONS",
    "MAX_NOTICE_PERIOD_DAYS",
    "DeprecationEngine",
    "DeprecationEvaluation",
    "DeprecationPolicy",
    "FeatureFlagProvider",
    "is_legal_transition",
    "require_legal_transition",
]
