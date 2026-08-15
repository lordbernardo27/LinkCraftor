from __future__ import annotations

from dataclasses import dataclass
from typing import Any


UNIVERSAL_JOB_ATTEMPTS_VERSION = (
    "universal_job_attempts_v2.1.8"
)

UNIVERSAL_JOB_ATTEMPTS_SCHEMA_VERSION = (
    "universal_job_attempts_schema_v1"
)

DEFAULT_UNIVERSAL_JOB_MAXIMUM_ATTEMPTS = 3
INITIAL_UNIVERSAL_JOB_ATTEMPTS = 0


class UniversalJobAttemptsError(ValueError):
    """Raised when Universal Job attempt values are invalid."""

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
class UniversalJobAttemptsValue:
    """
    Immutable normalized view of the Universal Job attempt window.
    """

    attempts: int
    maximum_attempts: int

    @property
    def attempts_remaining(self) -> int:
        return max(
            0,
            self.maximum_attempts
            - self.attempts,
        )

    @property
    def at_limit(self) -> bool:
        return (
            self.attempts
            >= self.maximum_attempts
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "schema_version": (
                UNIVERSAL_JOB_ATTEMPTS_SCHEMA_VERSION
            ),
            "attempts": self.attempts,
            "maximum_attempts": (
                self.maximum_attempts
            ),
            "attempts_remaining": (
                self.attempts_remaining
            ),
            "at_limit": self.at_limit,
        }


def normalize_universal_job_attempts(
    value: Any,
) -> int:
    """
    Normalize an executed-attempt count.

    attempts:
    - must be an integer
    - booleans are rejected
    - must be >= 0
    """

    if (
        isinstance(
            value,
            bool,
        )
        or not isinstance(
            value,
            int,
        )
    ):
        raise UniversalJobAttemptsError(
            "attempts must be an integer.",
            code="invalid_job_attempts",
            value=value,
        )

    if value < 0:
        raise UniversalJobAttemptsError(
            "attempts must be at least 0.",
            code="invalid_job_attempts",
            value=value,
        )

    return value


def normalize_universal_job_maximum_attempts(
    value: Any,
    *,
    default: int = (
        DEFAULT_UNIVERSAL_JOB_MAXIMUM_ATTEMPTS
    ),
) -> int:
    """
    Normalize the maximum number of permitted attempts.

    None means use the caller-supplied canonical default.
    """

    if value is None:
        value = default

    if (
        isinstance(
            value,
            bool,
        )
        or not isinstance(
            value,
            int,
        )
    ):
        raise UniversalJobAttemptsError(
            "maximum_attempts must be an integer.",
            code="invalid_maximum_attempts",
            value=value,
        )

    if value < 1:
        raise UniversalJobAttemptsError(
            "maximum_attempts must be at least 1.",
            code="invalid_maximum_attempts",
            value=value,
        )

    return value


def validate_universal_job_attempt_window(
    *,
    attempts: Any,
    maximum_attempts: Any,
) -> UniversalJobAttemptsValue:
    """
    Validate the canonical relationship between attempts and its ceiling.
    """

    normalized_attempts = (
        normalize_universal_job_attempts(
            attempts
        )
    )

    normalized_maximum = (
        normalize_universal_job_maximum_attempts(
            maximum_attempts
        )
    )

    if (
        normalized_attempts
        > normalized_maximum
    ):
        raise UniversalJobAttemptsError(
            (
                "attempts must not exceed "
                "maximum_attempts."
            ),
            code="attempts_exceed_maximum",
            value={
                "attempts":
                    normalized_attempts,
                "maximum_attempts":
                    normalized_maximum,
            },
        )

    return UniversalJobAttemptsValue(
        attempts=normalized_attempts,
        maximum_attempts=normalized_maximum,
    )


def initial_universal_job_attempts(
) -> int:
    """Return the canonical attempt count for a newly created job."""

    return INITIAL_UNIVERSAL_JOB_ATTEMPTS


def default_universal_job_maximum_attempts(
) -> int:
    """Return the canonical Creation Engine default maximum attempts."""

    return DEFAULT_UNIVERSAL_JOB_MAXIMUM_ATTEMPTS


def explain_universal_job_attempts_v1(
) -> dict[str, Any]:
    """Describe the Phase 2.1.8 authority boundary."""

    return {
        "phase": "2.1.8",
        "component": "Universal Job Attempts",
        "version": (
            UNIVERSAL_JOB_ATTEMPTS_VERSION
        ),
        "schema_version": (
            UNIVERSAL_JOB_ATTEMPTS_SCHEMA_VERSION
        ),
        "scope": "Universal Job Model",
        "initial_attempts": (
            INITIAL_UNIVERSAL_JOB_ATTEMPTS
        ),
        "default_maximum_attempts": (
            DEFAULT_UNIVERSAL_JOB_MAXIMUM_ATTEMPTS
        ),
        "invariants": [
            "attempts is an integer",
            "attempts >= 0",
            "maximum_attempts is an integer",
            "maximum_attempts >= 1",
            "attempts <= maximum_attempts",
        ],
        "prohibitions": [
            "does not increment attempts",
            "does not execute retries",
            "does not schedule retries",
            "does not calculate retry delay or backoff",
            "does not decide retryability",
            "does not mutate job status",
            "does not move jobs to dead letter",
            "does not perform queue operations",
            "does not perform worker execution",
            "does not perform I/O",
        ],
    }


__all__ = [
    "UNIVERSAL_JOB_ATTEMPTS_VERSION",
    "UNIVERSAL_JOB_ATTEMPTS_SCHEMA_VERSION",
    "DEFAULT_UNIVERSAL_JOB_MAXIMUM_ATTEMPTS",
    "INITIAL_UNIVERSAL_JOB_ATTEMPTS",
    "UniversalJobAttemptsError",
    "UniversalJobAttemptsValue",
    "normalize_universal_job_attempts",
    "normalize_universal_job_maximum_attempts",
    "validate_universal_job_attempt_window",
    "initial_universal_job_attempts",
    "default_universal_job_maximum_attempts",
    "explain_universal_job_attempts_v1",
]
