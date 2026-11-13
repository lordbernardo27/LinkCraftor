"""
LinkCraftor — Universal Coordination Framework

Phase 11.4 — Version Governance.

Read-only governance over frozen Phase-2 workflow/coordinator registration
and explicit version-preference authorities.

This module does not modify either registry or version preferences.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Tuple

from backend.server.coordination.workflow_registry.registry import (
    WorkflowRegistryEntry,
)

from backend.server.coordination.registration_validation.validator import (
    RegistrationValidationResult,
)


VERSION_GOVERNANCE_VERSION = (
    "version_governance_v11.4.0"
)

VERSION_GOVERNANCE_SCHEMA_VERSION = (
    "version_governance_schema_v1"
)


class VersionGovernanceDisposition(
    str,
    Enum,
):
    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass(
    frozen=True,
    slots=True,
)
class VersionGovernanceDecision:

    disposition: VersionGovernanceDisposition

    workflow_type: str
    workflow_version: str

    coordinator_id: str
    coordinator_version: str

    preferred_workflow_version: str | None
    preferred_coordinator_version: str | None

    violations: Tuple[
        str,
        ...
    ]

    governance_version: str = (
        VERSION_GOVERNANCE_VERSION
    )

    schema_version: str = (
        VERSION_GOVERNANCE_SCHEMA_VERSION
    )


def evaluate_version_governance(
    *,
    workflow_entry: WorkflowRegistryEntry,
    coordinator: Any,
    registration_validation: RegistrationValidationResult,
    preferred_workflow_version: str | None = None,
    preferred_coordinator_version: str | None = None,
) -> VersionGovernanceDecision:

    violations = []

    coordinator_id = str(
        getattr(
            coordinator,
            "coordinator_id",
            "",
        )
    )

    coordinator_version = str(
        getattr(
            coordinator,
            "coordinator_version",
            "",
        )
    )

    coordinator_workflow_type = str(
        getattr(
            coordinator,
            "workflow_type",
            "",
        )
    )

    coordinator_workflow_version = str(
        getattr(
            coordinator,
            "workflow_version",
            "",
        )
    )

    if not registration_validation.is_valid:
        violations.append(
            "registration_validation_failed"
        )

    if (
        coordinator_workflow_type
        != workflow_entry.workflow_type
    ):
        violations.append(
            "workflow_type_mismatch"
        )

    if (
        coordinator_workflow_version
        != workflow_entry.workflow_version
    ):
        violations.append(
            "workflow_version_mismatch"
        )

    if (
        preferred_workflow_version
        is not None
        and preferred_workflow_version
        != workflow_entry.workflow_version
    ):
        violations.append(
            "non_preferred_workflow_version"
        )

    if (
        preferred_coordinator_version
        is not None
        and preferred_coordinator_version
        != coordinator_version
    ):
        violations.append(
            "non_preferred_coordinator_version"
        )

    canonical = tuple(
        dict.fromkeys(
            violations
        )
    )

    return VersionGovernanceDecision(
        disposition=(
            VersionGovernanceDisposition.DENY
            if canonical
            else VersionGovernanceDisposition.ALLOW
        ),

        workflow_type=
            workflow_entry.workflow_type,

        workflow_version=
            workflow_entry.workflow_version,

        coordinator_id=
            coordinator_id,

        coordinator_version=
            coordinator_version,

        preferred_workflow_version=
            preferred_workflow_version,

        preferred_coordinator_version=
            preferred_coordinator_version,

        violations=
            canonical,
    )


__all__ = [
    "VERSION_GOVERNANCE_VERSION",
    "VERSION_GOVERNANCE_SCHEMA_VERSION",
    "VersionGovernanceDisposition",
    "VersionGovernanceDecision",
    "evaluate_version_governance",
]
