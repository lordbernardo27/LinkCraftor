"""
LinkCraftor — Universal Coordination Framework

Phase 11.6 — Security Boundaries.

Fail-closed Coordination authorization boundary.

Authentication and generic Runtime authorization remain Runtime-owned.
This component consumes already-established authorization posture and
workspace scope; it does not issue credentials or authenticate principals.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from backend.server.coordination.coordination_governance.workspace_isolation import (
    WorkspaceIsolationDecision,
    WorkspaceIsolationDisposition,
)


SECURITY_BOUNDARIES_VERSION = (
    "security_boundaries_v11.6.0"
)

SECURITY_BOUNDARIES_SCHEMA_VERSION = (
    "security_boundaries_schema_v1"
)


class CoordinationSecurityDisposition(
    str,
    Enum,
):
    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass(
    frozen=True,
    slots=True,
)
class CoordinationSecurityDecision:

    disposition: CoordinationSecurityDisposition

    principal_id: str
    action: str

    workflow_id: str
    workspace_id: str

    reason_codes: Tuple[
        str,
        ...
    ]

    security_version: str = (
        SECURITY_BOUNDARIES_VERSION
    )

    schema_version: str = (
        SECURITY_BOUNDARIES_SCHEMA_VERSION
    )


def evaluate_coordination_security_boundary(
    *,
    principal_id: str,
    action: str,
    workflow_id: str,
    workspace_id: str,
    authorization_granted: bool,
    workspace_isolation: WorkspaceIsolationDecision,
) -> CoordinationSecurityDecision:

    reasons = []

    if not principal_id.strip():
        reasons.append(
            "principal_missing"
        )

    if not action.strip():
        reasons.append(
            "action_missing"
        )

    if not workflow_id.strip():
        reasons.append(
            "workflow_id_missing"
        )

    if not workspace_id.strip():
        reasons.append(
            "workspace_id_missing"
        )

    if not authorization_granted:
        reasons.append(
            "authorization_not_granted"
        )

    if (
        workspace_isolation.disposition
        is not WorkspaceIsolationDisposition.ALLOW
    ):
        reasons.append(
            "workspace_isolation_denied"
        )

    if (
        workspace_isolation.workflow_id
        != workflow_id
    ):
        reasons.append(
            "workflow_scope_mismatch"
        )

    if (
        workspace_isolation.expected_workspace_id
        != workspace_id
    ):
        reasons.append(
            "workspace_scope_mismatch"
        )

    canonical = tuple(
        dict.fromkeys(
            reasons
        )
    )

    return CoordinationSecurityDecision(
        disposition=(
            CoordinationSecurityDisposition.DENY
            if canonical
            else CoordinationSecurityDisposition.ALLOW
        ),

        principal_id=
            principal_id,

        action=
            action,

        workflow_id=
            workflow_id,

        workspace_id=
            workspace_id,

        reason_codes=
            canonical,
    )


__all__ = [
    "SECURITY_BOUNDARIES_VERSION",
    "SECURITY_BOUNDARIES_SCHEMA_VERSION",
    "CoordinationSecurityDisposition",
    "CoordinationSecurityDecision",
    "evaluate_coordination_security_boundary",
]
