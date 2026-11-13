"""
LinkCraftor — Universal Coordination Framework

Phase 11.1 — Workspace Isolation.

Pure coordination-level workspace boundary validation.

This module does not authenticate users, provision memberships, mutate
workflows, or duplicate Runtime workspace-resource governance.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Tuple

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflow,
)


WORKSPACE_ISOLATION_VERSION = (
    "workspace_isolation_v11.1.0"
)

WORKSPACE_ISOLATION_SCHEMA_VERSION = (
    "workspace_isolation_schema_v1"
)


class WorkspaceIsolationDisposition(
    str,
    Enum,
):
    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass(
    frozen=True,
    slots=True,
)
class WorkspaceIsolationDecision:

    disposition: WorkspaceIsolationDisposition

    workflow_id: str
    expected_workspace_id: str

    observed_workspace_ids: Tuple[
        str,
        ...
    ]

    violations: Tuple[
        str,
        ...
    ]

    isolation_version: str = (
        WORKSPACE_ISOLATION_VERSION
    )

    schema_version: str = (
        WORKSPACE_ISOLATION_SCHEMA_VERSION
    )


def evaluate_workspace_isolation(
    workflow: UniversalWorkflow,
    *,
    observed_workspace_ids: Iterable[str] = (),
) -> WorkspaceIsolationDecision:

    if not isinstance(
        workflow,
        UniversalWorkflow,
    ):
        raise TypeError(
            "workflow must be UniversalWorkflow"
        )

    validation = workflow.validate()

    if not validation.is_valid:
        return WorkspaceIsolationDecision(
            disposition=
                WorkspaceIsolationDisposition.DENY,

            workflow_id=
                workflow.workflow_id,

            expected_workspace_id=
                workflow.workspace_id,

            observed_workspace_ids=(),

            violations=(
                "invalid_workflow",
            ),
        )

    observed = tuple(
        str(item).strip()
        for item in observed_workspace_ids
    )

    violations = []

    if not workflow.workspace_id:
        violations.append(
            "workflow_workspace_missing"
        )

    for value in observed:

        if not value:
            violations.append(
                "observed_workspace_missing"
            )

        elif (
            value
            != workflow.workspace_id
        ):
            violations.append(
                "cross_workspace_reference"
            )

    canonical = tuple(
        dict.fromkeys(
            violations
        )
    )

    return WorkspaceIsolationDecision(
        disposition=(
            WorkspaceIsolationDisposition.DENY
            if canonical
            else WorkspaceIsolationDisposition.ALLOW
        ),

        workflow_id=
            workflow.workflow_id,

        expected_workspace_id=
            workflow.workspace_id,

        observed_workspace_ids=
            observed,

        violations=
            canonical,
    )


__all__ = [
    "WORKSPACE_ISOLATION_VERSION",
    "WORKSPACE_ISOLATION_SCHEMA_VERSION",
    "WorkspaceIsolationDisposition",
    "WorkspaceIsolationDecision",
    "evaluate_workspace_isolation",
]
