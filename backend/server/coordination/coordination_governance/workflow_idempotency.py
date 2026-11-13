"""
LinkCraftor — Universal Coordination Framework

Phase 11.2 — Workflow Idempotency.

Workflow-level idempotency governance only.

Runtime Universal Job idempotency remains owned by the Universal Runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Tuple

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflow,
)


WORKFLOW_IDEMPOTENCY_VERSION = (
    "workflow_idempotency_v11.2.0"
)

WORKFLOW_IDEMPOTENCY_SCHEMA_VERSION = (
    "workflow_idempotency_schema_v1"
)


class WorkflowIdempotencyDisposition(
    str,
    Enum,
):
    ALLOW_NEW = "ALLOW_NEW"
    REUSE_EXISTING = "REUSE_EXISTING"
    DENY_CONFLICT = "DENY_CONFLICT"


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowIdempotencyDecision:

    disposition: WorkflowIdempotencyDisposition

    workflow_id: str
    idempotency_key: str | None

    matching_workflow_ids: Tuple[
        str,
        ...
    ]

    reason_codes: Tuple[
        str,
        ...
    ]

    idempotency_version: str = (
        WORKFLOW_IDEMPOTENCY_VERSION
    )

    schema_version: str = (
        WORKFLOW_IDEMPOTENCY_SCHEMA_VERSION
    )


def evaluate_workflow_idempotency(
    candidate: UniversalWorkflow,
    *,
    existing_workflows: Iterable[
        UniversalWorkflow
    ] = (),
) -> WorkflowIdempotencyDecision:

    if not isinstance(
        candidate,
        UniversalWorkflow,
    ):
        raise TypeError(
            "candidate must be UniversalWorkflow"
        )

    existing = tuple(
        existing_workflows
    )

    for item in existing:

        if not isinstance(
            item,
            UniversalWorkflow,
        ):
            raise TypeError(
                "existing_workflows must contain UniversalWorkflow"
            )

    key = candidate.idempotency_key

    if not key:
        return WorkflowIdempotencyDecision(
            disposition=
                WorkflowIdempotencyDisposition.ALLOW_NEW,

            workflow_id=
                candidate.workflow_id,

            idempotency_key=
                None,

            matching_workflow_ids=(),

            reason_codes=(
                "no_workflow_idempotency_key",
            ),
        )

    matches = tuple(
        item
        for item in existing
        if item.idempotency_key
        == key
    )

    if not matches:
        return WorkflowIdempotencyDecision(
            disposition=
                WorkflowIdempotencyDisposition.ALLOW_NEW,

            workflow_id=
                candidate.workflow_id,

            idempotency_key=
                key,

            matching_workflow_ids=(),

            reason_codes=(
                "idempotency_key_unused",
            ),
        )

    compatible = tuple(
        item
        for item in matches
        if (
            item.workflow_type
            == candidate.workflow_type
            and item.workflow_version
            == candidate.workflow_version
            and item.workspace_id
            == candidate.workspace_id
        )
    )

    if len(compatible) == len(matches):

        return WorkflowIdempotencyDecision(
            disposition=
                WorkflowIdempotencyDisposition.REUSE_EXISTING,

            workflow_id=
                candidate.workflow_id,

            idempotency_key=
                key,

            matching_workflow_ids=
                tuple(
                    item.workflow_id
                    for item
                    in compatible
                ),

            reason_codes=(
                "matching_workflow_idempotency_identity",
            ),
        )

    return WorkflowIdempotencyDecision(
        disposition=
            WorkflowIdempotencyDisposition.DENY_CONFLICT,

        workflow_id=
            candidate.workflow_id,

        idempotency_key=
            key,

        matching_workflow_ids=
            tuple(
                item.workflow_id
                for item
                in matches
            ),

        reason_codes=(
            "idempotency_key_reused_with_conflicting_identity",
        ),
    )


__all__ = [
    "WORKFLOW_IDEMPOTENCY_VERSION",
    "WORKFLOW_IDEMPOTENCY_SCHEMA_VERSION",
    "WorkflowIdempotencyDisposition",
    "WorkflowIdempotencyDecision",
    "evaluate_workflow_idempotency",
]
