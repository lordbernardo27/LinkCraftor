"""
LinkCraftor — Universal Coordination Framework

Phase 10.5 — Audit Trail.

Deterministic read-only audit projection of existing lifecycle and
stage-state evidence.

It does not replace Phase 3 lifecycle history, mutate records, persist an
audit database or reuse Runtime Schema audit authority.
"""

from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Tuple

from backend.server.coordination.workflow_lifecycle.lifecycle_history import (
    LifecycleHistoryEntry,
    sort_lifecycle_history,
    validate_lifecycle_history,
)

from backend.server.coordination.workflow_persistence.stage_state_store import (
    StageStateRecord,
)


AUDIT_TRAIL_VERSION = (
    "audit_trail_v10.5.0"
)

AUDIT_TRAIL_SCHEMA_VERSION = (
    "audit_trail_schema_v1"
)


class AuditTrailError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowAuditEntry:

    audit_id: str

    workflow_id: str
    correlation_id: str

    event_type: str
    occurred_at: str

    subject_id: str
    status: str

    source: str | None

    details: Mapping[
        str,
        Any,
    ]


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowAuditTrail:

    workflow_id: str
    entries: Tuple[
        WorkflowAuditEntry,
        ...
    ]

    trail_fingerprint: str

    audit_version: str = (
        AUDIT_TRAIL_VERSION
    )

    schema_version: str = (
        AUDIT_TRAIL_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> Mapping[str, Any]:

        return MappingProxyType({
            "workflow_id":
                self.workflow_id,

            "entries":
                tuple(
                    {
                        "audit_id":
                            entry.audit_id,

                        "workflow_id":
                            entry.workflow_id,

                        "correlation_id":
                            entry.correlation_id,

                        "event_type":
                            entry.event_type,

                        "occurred_at":
                            entry.occurred_at,

                        "subject_id":
                            entry.subject_id,

                        "status":
                            entry.status,

                        "source":
                            entry.source,

                        "details":
                            dict(
                                entry.details
                            ),
                    }
                    for entry
                    in self.entries
                ),

            "trail_fingerprint":
                self.trail_fingerprint,

            "audit_version":
                self.audit_version,

            "schema_version":
                self.schema_version,
        })


def _audit_id(
    payload: Mapping[
        str,
        Any,
    ],
) -> str:

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        default=str,
    )

    return hashlib.sha256(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest().upper()


def build_workflow_audit_trail(
    *,
    lifecycle_history: Iterable[
        LifecycleHistoryEntry
    ] = (),
    stage_states: Iterable[
        StageStateRecord
    ] = (),
) -> WorkflowAuditTrail:

    history = tuple(
        lifecycle_history
    )

    states = tuple(
        stage_states
    )

    validation = validate_lifecycle_history(
        history
    )

    if not validation.is_valid:
        raise AuditTrailError(
            "Lifecycle history invalid: "
            + "; ".join(
                validation.violations
            )
        )

    workflow_ids = {
        entry.workflow_id
        for entry
        in history
    } | {
        state.workflow_id
        for state
        in states
    }

    if len(workflow_ids) > 1:
        raise AuditTrailError(
            "audit sources span multiple workflows"
        )

    workflow_id = (
        next(
            iter(
                workflow_ids
            )
        )
        if workflow_ids
        else ""
    )

    entries = []

    for entry in sort_lifecycle_history(
        history
    ):

        payload = {
            "workflow_id":
                entry.workflow_id,

            "correlation_id":
                entry.correlation_id,

            "event_type":
                "WORKFLOW_TRANSITION",

            "occurred_at":
                entry.occurred_at,

            "subject_id":
                entry.workflow_id,

            "status":
                entry.to_state.value,

            "source":
                entry.source,

            "details": {
                "event_id":
                    entry.event_id,

                "from_state":
                    entry.from_state.value,

                "to_state":
                    entry.to_state.value,

                "reason":
                    entry.reason,

                "actor_id":
                    entry.actor_id,
            },
        }

        entries.append(
            WorkflowAuditEntry(
                audit_id=
                    _audit_id(
                        payload
                    ),

                workflow_id=
                    entry.workflow_id,

                correlation_id=
                    entry.correlation_id,

                event_type=
                    "WORKFLOW_TRANSITION",

                occurred_at=
                    entry.occurred_at,

                subject_id=
                    entry.workflow_id,

                status=
                    entry.to_state.value,

                source=
                    entry.source,

                details=
                    payload[
                        "details"
                    ],
            )
        )

    for state in sorted(
        states,
        key=lambda item: (
            item.recorded_at,
            item.stage_id,
        ),
    ):

        payload = {
            "workflow_id":
                state.workflow_id,

            "correlation_id":
                state.correlation_id,

            "event_type":
                "STAGE_STATE",

            "occurred_at":
                state.recorded_at,

            "subject_id":
                state.stage_id,

            "status":
                state.status,

            "source":
                "stage_state_store",

            "details": {
                "stage_version":
                    state.stage_version,

                "result_id":
                    state.result_id,

                "result_reference":
                    state.result_reference,

                "failure_code":
                    state.failure_code,

                "record_fingerprint":
                    state.record_fingerprint,
            },
        }

        entries.append(
            WorkflowAuditEntry(
                audit_id=
                    _audit_id(
                        payload
                    ),

                workflow_id=
                    state.workflow_id,

                correlation_id=
                    state.correlation_id,

                event_type=
                    "STAGE_STATE",

                occurred_at=
                    state.recorded_at,

                subject_id=
                    state.stage_id,

                status=
                    state.status,

                source=
                    "stage_state_store",

                details=
                    payload[
                        "details"
                    ],
            )
        )

    entries = tuple(
        sorted(
            entries,
            key=lambda item: (
                item.occurred_at,
                item.event_type,
                item.subject_id,
                item.audit_id,
            ),
        )
    )

    canonical = json.dumps(
        [
            {
                "audit_id":
                    item.audit_id,

                "occurred_at":
                    item.occurred_at,

                "event_type":
                    item.event_type,

                "subject_id":
                    item.subject_id,

                "status":
                    item.status,
            }
            for item
            in entries
        ],
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )

    fingerprint = hashlib.sha256(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest().upper()

    return WorkflowAuditTrail(
        workflow_id=
            workflow_id,

        entries=
            entries,

        trail_fingerprint=
            fingerprint,
    )


__all__ = [
    "AUDIT_TRAIL_VERSION",
    "AUDIT_TRAIL_SCHEMA_VERSION",
    "AuditTrailError",
    "WorkflowAuditEntry",
    "WorkflowAuditTrail",
    "build_workflow_audit_trail",
]
