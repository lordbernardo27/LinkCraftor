"""
LinkCraftor — Universal Coordination Framework

Phase 11.3 — Duplicate Protection.

Protects workflow-instance identity at Coordination scope.

Workflow-definition duplicate rejection remains Phase 2.1 authority.
Coordinator-registration duplicate rejection remains Phase 2.2 authority.
Runtime job/queue deduplication remains Runtime-owned.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Tuple

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflow,
)


DUPLICATE_PROTECTION_VERSION = (
    "duplicate_protection_v11.3.0"
)

DUPLICATE_PROTECTION_SCHEMA_VERSION = (
    "duplicate_protection_schema_v1"
)


class DuplicateDisposition(
    str,
    Enum,
):
    UNIQUE = "UNIQUE"
    DUPLICATE = "DUPLICATE"
    CONFLICT = "CONFLICT"


@dataclass(
    frozen=True,
    slots=True,
)
class DuplicateProtectionDecision:

    disposition: DuplicateDisposition

    workflow_id: str

    matching_workflow_ids: Tuple[
        str,
        ...
    ]

    reason_codes: Tuple[
        str,
        ...
    ]

    protection_version: str = (
        DUPLICATE_PROTECTION_VERSION
    )

    schema_version: str = (
        DUPLICATE_PROTECTION_SCHEMA_VERSION
    )


def evaluate_duplicate_workflow(
    candidate: UniversalWorkflow,
    *,
    existing_workflows: Iterable[
        UniversalWorkflow
    ] = (),
) -> DuplicateProtectionDecision:

    existing = tuple(
        existing_workflows
    )

    same_id = tuple(
        item
        for item in existing
        if item.workflow_id
        == candidate.workflow_id
    )

    if same_id:

        equivalent = all(
            (
                item.workflow_type
                == candidate.workflow_type
                and item.workflow_version
                == candidate.workflow_version
                and item.workspace_id
                == candidate.workspace_id
                and item.correlation_id
                == candidate.correlation_id
            )
            for item
            in same_id
        )

        return DuplicateProtectionDecision(
            disposition=(
                DuplicateDisposition.DUPLICATE
                if equivalent
                else DuplicateDisposition.CONFLICT
            ),

            workflow_id=
                candidate.workflow_id,

            matching_workflow_ids=
                tuple(
                    item.workflow_id
                    for item
                    in same_id
                ),

            reason_codes=(
                (
                    "existing_equivalent_workflow_id"
                    if equivalent
                    else "workflow_id_identity_conflict"
                ),
            ),
        )

    same_correlation = tuple(
        item
        for item in existing
        if (
            item.workspace_id
            == candidate.workspace_id
            and item.workflow_type
            == candidate.workflow_type
            and item.workflow_version
            == candidate.workflow_version
            and item.correlation_id
            == candidate.correlation_id
        )
    )

    if same_correlation:

        return DuplicateProtectionDecision(
            disposition=
                DuplicateDisposition.DUPLICATE,

            workflow_id=
                candidate.workflow_id,

            matching_workflow_ids=
                tuple(
                    item.workflow_id
                    for item
                    in same_correlation
                ),

            reason_codes=(
                "equivalent_workflow_correlation_exists",
            ),
        )

    return DuplicateProtectionDecision(
        disposition=
            DuplicateDisposition.UNIQUE,

        workflow_id=
            candidate.workflow_id,

        matching_workflow_ids=(),

        reason_codes=(
            "workflow_identity_unique",
        ),
    )


__all__ = [
    "DUPLICATE_PROTECTION_VERSION",
    "DUPLICATE_PROTECTION_SCHEMA_VERSION",
    "DuplicateDisposition",
    "DuplicateProtectionDecision",
    "evaluate_duplicate_workflow",
]
