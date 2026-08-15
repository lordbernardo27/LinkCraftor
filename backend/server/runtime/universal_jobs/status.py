from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.server.runtime.universal_jobs.contract import (
    UniversalJobContractError,
    UniversalJobStatus,
)


UNIVERSAL_JOB_STATUS_VERSION = (
    "universal_job_status_v2.1.7"
)

UNIVERSAL_JOB_STATUS_SCHEMA_VERSION = (
    "universal_job_status_schema_v1"
)


TERMINAL_UNIVERSAL_JOB_STATUSES = frozenset(
    {
        UniversalJobStatus.SUCCEEDED,
        UniversalJobStatus.FAILED,
        UniversalJobStatus.CANCELLED,
        UniversalJobStatus.DEAD_LETTER,
        UniversalJobStatus.EXPIRED,
    }
)


NON_TERMINAL_UNIVERSAL_JOB_STATUSES = frozenset(
    status
    for status in UniversalJobStatus
    if status not in TERMINAL_UNIVERSAL_JOB_STATUSES
)


class UniversalJobStatusError(ValueError):
    """Raised when a Universal Job status is invalid."""

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
class UniversalJobStatusValue:
    """
    Immutable normalized representation of one Universal Job status.
    """

    status: UniversalJobStatus

    @property
    def value(self) -> str:
        return str(self.status)

    @property
    def terminal(self) -> bool:
        return (
            self.status
            in TERMINAL_UNIVERSAL_JOB_STATUSES
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "schema_version": (
                UNIVERSAL_JOB_STATUS_SCHEMA_VERSION
            ),
            "status": self.value,
            "terminal": self.terminal,
        }


def normalize_universal_job_status(
    value: Any,
) -> UniversalJobStatus:
    """
    Normalize one Universal Job lifecycle status.

    Accepted:
    - UniversalJobStatus enum member
    - canonical status string, case-insensitive
    - surrounding string whitespace is ignored

    No legacy or subsystem-specific aliases are accepted.
    """

    try:
        return UniversalJobStatus.coerce(
            value
        )

    except UniversalJobContractError as exc:
        raise UniversalJobStatusError(
            "Invalid Universal Job status.",
            code="invalid_job_status",
            value=value,
        ) from exc


def validate_universal_job_status(
    value: Any,
) -> UniversalJobStatusValue:
    """Return an immutable normalized status value object."""

    return UniversalJobStatusValue(
        status=(
            normalize_universal_job_status(
                value
            )
        )
    )


def is_canonical_universal_job_status(
    value: Any,
) -> bool:
    """
    Return True only when the value is already a canonical enum member.
    """

    return isinstance(
        value,
        UniversalJobStatus,
    )


def is_terminal_universal_job_status(
    value: Any,
) -> bool:
    """Return whether a Universal Job status is terminal."""

    return (
        normalize_universal_job_status(
            value
        )
        in TERMINAL_UNIVERSAL_JOB_STATUSES
    )


def is_non_terminal_universal_job_status(
    value: Any,
) -> bool:
    """Return whether a Universal Job status is non-terminal."""

    return (
        normalize_universal_job_status(
            value
        )
        in NON_TERMINAL_UNIVERSAL_JOB_STATUSES
    )


def initial_universal_job_status(
    *,
    enqueue: bool,
) -> UniversalJobStatus:
    """
    Return the canonical creation-time status.

    enqueue=True  -> queued
    enqueue=False -> created

    This helper does not enqueue, schedule, lease, execute, or mutate
    a job.
    """

    if not isinstance(
        enqueue,
        bool,
    ):
        raise UniversalJobStatusError(
            "enqueue must be a boolean.",
            code="invalid_initial_status_enqueue",
            value=enqueue,
        )

    if enqueue:
        return UniversalJobStatus.QUEUED

    return UniversalJobStatus.CREATED


def explain_universal_job_status_v1(
) -> dict[str, Any]:
    """Describe the Phase 2.1.7 authority boundary."""

    return {
        "phase": "2.1.7",
        "component": "Universal Job Status",
        "version": (
            UNIVERSAL_JOB_STATUS_VERSION
        ),
        "schema_version": (
            UNIVERSAL_JOB_STATUS_SCHEMA_VERSION
        ),
        "scope": "Universal Job Model",
        "statuses": [
            status.value
            for status in UniversalJobStatus
        ],
        "terminal_statuses": [
            status.value
            for status
            in UniversalJobStatus
            if status
            in TERMINAL_UNIVERSAL_JOB_STATUSES
        ],
        "non_terminal_statuses": [
            status.value
            for status
            in UniversalJobStatus
            if status
            in NON_TERMINAL_UNIVERSAL_JOB_STATUSES
        ],
        "initial_status_rule": {
            "enqueue_true": "queued",
            "enqueue_false": "created",
        },
        "prohibitions": [
            "does not define lifecycle transition rules",
            "does not mutate job status",
            "does not enqueue jobs",
            "does not lease jobs",
            "does not schedule jobs",
            "does not execute workers",
            "does not implement retry policy",
            "does not implement dead-letter movement",
            "does not implement orchestration status mapping",
            "does not perform I/O",
        ],
    }


__all__ = [
    "UNIVERSAL_JOB_STATUS_VERSION",
    "UNIVERSAL_JOB_STATUS_SCHEMA_VERSION",
    "TERMINAL_UNIVERSAL_JOB_STATUSES",
    "NON_TERMINAL_UNIVERSAL_JOB_STATUSES",
    "UniversalJobStatusError",
    "UniversalJobStatusValue",
    "normalize_universal_job_status",
    "validate_universal_job_status",
    "is_canonical_universal_job_status",
    "is_terminal_universal_job_status",
    "is_non_terminal_universal_job_status",
    "initial_universal_job_status",
    "explain_universal_job_status_v1",
]
