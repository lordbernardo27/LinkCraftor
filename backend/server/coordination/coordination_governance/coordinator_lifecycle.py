"""
LinkCraftor — Universal Coordination Framework

Phase 11.5 — Coordinator Lifecycle.

Governance lifecycle for already-registered coordinator identities.

This does not execute coordinators, mutate the Coordinator Registry,
or choose versions. Phase 2 retains registration/version authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple


COORDINATOR_LIFECYCLE_VERSION = (
    "coordinator_lifecycle_v11.5.0"
)

COORDINATOR_LIFECYCLE_SCHEMA_VERSION = (
    "coordinator_lifecycle_schema_v1"
)


class CoordinatorLifecycleState(
    str,
    Enum,
):
    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"


_ALLOWED = {
    CoordinatorLifecycleState.REGISTERED: (
        CoordinatorLifecycleState.ACTIVE,
        CoordinatorLifecycleState.DEPRECATED,
        CoordinatorLifecycleState.RETIRED,
    ),

    CoordinatorLifecycleState.ACTIVE: (
        CoordinatorLifecycleState.DEPRECATED,
        CoordinatorLifecycleState.RETIRED,
    ),

    CoordinatorLifecycleState.DEPRECATED: (
        CoordinatorLifecycleState.ACTIVE,
        CoordinatorLifecycleState.RETIRED,
    ),

    CoordinatorLifecycleState.RETIRED:
        (),
}


@dataclass(
    frozen=True,
    slots=True,
)
class CoordinatorLifecycleDecision:

    coordinator_id: str
    coordinator_version: str

    current_state: CoordinatorLifecycleState
    requested_state: CoordinatorLifecycleState

    allowed: bool

    reason_codes: Tuple[
        str,
        ...
    ]

    lifecycle_version: str = (
        COORDINATOR_LIFECYCLE_VERSION
    )

    schema_version: str = (
        COORDINATOR_LIFECYCLE_SCHEMA_VERSION
    )


def evaluate_coordinator_lifecycle_transition(
    *,
    coordinator_id: str,
    coordinator_version: str,
    current_state: CoordinatorLifecycleState,
    requested_state: CoordinatorLifecycleState,
    registration_valid: bool,
) -> CoordinatorLifecycleDecision:

    reasons = []

    if not coordinator_id.strip():
        reasons.append(
            "coordinator_id_missing"
        )

    if not coordinator_version.strip():
        reasons.append(
            "coordinator_version_missing"
        )

    if not registration_valid:
        reasons.append(
            "registration_not_valid"
        )

    if (
        requested_state
        not in _ALLOWED[
            current_state
        ]
    ):
        reasons.append(
            "lifecycle_transition_not_allowed"
        )

    canonical = tuple(
        dict.fromkeys(
            reasons
        )
    )

    return CoordinatorLifecycleDecision(
        coordinator_id=
            coordinator_id,

        coordinator_version=
            coordinator_version,

        current_state=
            current_state,

        requested_state=
            requested_state,

        allowed=
            not canonical,

        reason_codes=
            canonical,
    )


__all__ = [
    "COORDINATOR_LIFECYCLE_VERSION",
    "COORDINATOR_LIFECYCLE_SCHEMA_VERSION",
    "CoordinatorLifecycleState",
    "CoordinatorLifecycleDecision",
    "evaluate_coordinator_lifecycle_transition",
]
