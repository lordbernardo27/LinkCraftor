from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.server.runtime.universal_jobs.contract import (
    UniversalJobContractError,
    UniversalJobPriority,
)


UNIVERSAL_JOB_PRIORITY_VERSION = (
    "universal_job_priority_v2.1.6"
)

UNIVERSAL_JOB_PRIORITY_SCHEMA_VERSION = (
    "universal_job_priority_schema_v1"
)


class UniversalJobPriorityError(ValueError):
    """Raised when a Universal Job priority is invalid."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:
        super().__init__(message)

        self.code = str(code)
        self.value = value


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalJobPriorityValue:
    """
    Immutable normalized view of one canonical Universal Job priority.
    """

    priority: UniversalJobPriority

    @property
    def name(self) -> str:
        return str(self.priority)

    @property
    def value(self) -> int:
        return int(self.priority)

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "schema_version": (
                UNIVERSAL_JOB_PRIORITY_SCHEMA_VERSION
            ),
            "priority": self.name,
            "priority_value": self.value,
        }


def normalize_universal_job_priority(
    value: Any,
) -> UniversalJobPriority:
    """
    Normalize a Universal Job priority into its canonical enum.

    Accepted representations:
    - UniversalJobPriority member
    - canonical integer: 10, 20, 30, 40, 50
    - canonical name, case-insensitive
    - canonical numeric string

    Boolean, float, None, unknown names, and unknown numeric values
    are rejected.

    This function defines job-priority representation only. It does
    not perform queue scheduling, worker selection, SLA enforcement,
    plan entitlement, retry policy, or orchestration decisions.
    """

    try:
        return UniversalJobPriority.coerce(
            value
        )

    except UniversalJobContractError as exc:
        raise UniversalJobPriorityError(
            "Invalid Universal Job priority.",
            code="invalid_job_priority",
            value=value,
        ) from exc


def validate_universal_job_priority(
    value: Any,
) -> UniversalJobPriorityValue:
    """Return an immutable canonical priority value object."""

    return UniversalJobPriorityValue(
        priority=(
            normalize_universal_job_priority(
                value
            )
        )
    )


def is_canonical_universal_job_priority(
    value: Any,
) -> bool:
    """
    Return True only when value is already a canonical enum member.
    """

    return isinstance(
        value,
        UniversalJobPriority,
    )


def universal_job_priority_order(
    value: Any,
) -> int:
    """
    Return the canonical ordering value.

    Lower numeric values denote greater urgency.

    This is an ordering semantic only. It does not instruct a queue
    or scheduler how or when a job must execute.
    """

    return int(
        normalize_universal_job_priority(
            value
        )
    )


def explain_universal_job_priority_v1(
) -> dict[str, Any]:
    """Describe the Phase 2.1.6 authority boundary."""

    return {
        "phase": "2.1.6",
        "component": "Universal Job Priority",
        "version": (
            UNIVERSAL_JOB_PRIORITY_VERSION
        ),
        "schema_version": (
            UNIVERSAL_JOB_PRIORITY_SCHEMA_VERSION
        ),
        "scope": "Universal Job Model",
        "default": "normal",
        "priorities": [
            {
                "name": "critical",
                "value": 10,
            },
            {
                "name": "high",
                "value": 20,
            },
            {
                "name": "normal",
                "value": 30,
            },
            {
                "name": "low",
                "value": 40,
            },
            {
                "name": "background",
                "value": 50,
            },
        ],
        "ordering_rule": (
            "Lower numeric value denotes greater job urgency."
        ),
        "accepted_input_forms": [
            "UniversalJobPriority member",
            "canonical integer",
            "canonical name",
            "canonical numeric string",
        ],
        "prohibitions": [
            "does not schedule jobs",
            "does not select workers",
            "does not assign queue position",
            "does not implement SLA policy",
            "does not implement subscription entitlement",
            "does not implement retry policy",
            "does not implement escalation policy",
            "does not modify orchestration priority",
            "does not perform I/O",
        ],
    }


__all__ = [
    "UNIVERSAL_JOB_PRIORITY_VERSION",
    "UNIVERSAL_JOB_PRIORITY_SCHEMA_VERSION",
    "UniversalJobPriorityError",
    "UniversalJobPriorityValue",
    "normalize_universal_job_priority",
    "validate_universal_job_priority",
    "is_canonical_universal_job_priority",
    "universal_job_priority_order",
    "explain_universal_job_priority_v1",
]
