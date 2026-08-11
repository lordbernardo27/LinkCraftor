"""Canonical Universal Job Identity & Naming — Phase 2.1.3.

This module owns the canonical Universal Job identity grammar and job-type
naming rules.

It performs no persistence, queue, registry, worker, ledger, status-file,
progress-file, duplicate-detection, or idempotency I/O.
"""

from __future__ import annotations

import re
import secrets
from typing import Any, Final


UNIVERSAL_JOB_IDENTITY_VERSION: Final[str] = (
    "universal_job_identity_v2.1.3"
)

UNIVERSAL_JOB_ID_PREFIX: Final[str] = "uj"

UNIVERSAL_JOB_ID_HEX_LENGTH: Final[int] = 32

UNIVERSAL_JOB_ID_LENGTH: Final[int] = (
    len(UNIVERSAL_JOB_ID_PREFIX)
    + 1
    + UNIVERSAL_JOB_ID_HEX_LENGTH
)

UNIVERSAL_JOB_TYPE_MAX_LENGTH: Final[int] = 512


_UNIVERSAL_JOB_ID_RE: Final[re.Pattern[str]] = re.compile(
    r"^uj_[0-9a-f]{32}$"
)

_UNIVERSAL_JOB_TYPE_RE: Final[re.Pattern[str]] = re.compile(
    r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$"
)


class UniversalJobIdentityError(ValueError):
    """Raised when Universal Job identity or naming is invalid."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        violations: tuple[str, ...] = (),
    ) -> None:
        super().__init__(message)

        self.code = str(
            code or "universal_job_identity_error"
        )

        self.violations = tuple(
            str(item)
            for item in violations
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": "UniversalJobIdentityError",
            "code": self.code,
            "message": str(self),
            "violations": list(self.violations),
            "identity_version": (
                UNIVERSAL_JOB_IDENTITY_VERSION
            ),
        }


def is_canonical_universal_job_id(
    value: Any,
) -> bool:
    """Return True only for the canonical Universal Job ID grammar."""

    return (
        isinstance(value, str)
        and bool(
            _UNIVERSAL_JOB_ID_RE.fullmatch(
                value
            )
        )
    )


def validate_universal_job_id(
    value: Any,
) -> str:
    """Validate one explicit Universal Job ID without coercion."""

    if not isinstance(value, str):
        raise UniversalJobIdentityError(
            "job_id must be a string.",
            code="invalid_job_id_type",
            violations=(
                "job_id must be a string",
            ),
        )

    if not value:
        raise UniversalJobIdentityError(
            "job_id is required.",
            code="missing_job_id",
            violations=(
                "job_id is required",
            ),
        )

    if value != value.strip():
        raise UniversalJobIdentityError(
            "job_id must not contain surrounding whitespace.",
            code="invalid_job_id_format",
            violations=(
                "job_id must already satisfy the canonical grammar",
            ),
        )

    if not _UNIVERSAL_JOB_ID_RE.fullmatch(
        value
    ):
        raise UniversalJobIdentityError(
            "job_id does not satisfy the canonical Universal Job ID grammar.",
            code="invalid_job_id_format",
            violations=(
                "job_id must match uj_<32 lowercase hexadecimal characters>",
            ),
        )

    return value


def generate_universal_job_id() -> str:
    """Generate one opaque 128-bit Universal Job identifier."""

    job_id = (
        f"{UNIVERSAL_JOB_ID_PREFIX}_"
        f"{secrets.token_hex(16)}"
    )

    if not is_canonical_universal_job_id(
        job_id
    ):
        raise UniversalJobIdentityError(
            "Generated Universal Job ID failed canonical validation.",
            code="generated_job_id_invalid",
            violations=(
                "generated job_id must satisfy the canonical grammar",
            ),
        )

    return job_id


def resolve_universal_job_id(
    explicit_job_id: Any = None,
) -> str:
    """Validate an explicit ID or generate a new canonical ID."""

    if explicit_job_id is None:
        return generate_universal_job_id()

    return validate_universal_job_id(
        explicit_job_id
    )


def is_canonical_universal_job_type(
    value: Any,
) -> bool:
    """Return True only for canonical lowercase snake_case job types."""

    return (
        isinstance(value, str)
        and len(value) <= UNIVERSAL_JOB_TYPE_MAX_LENGTH
        and bool(
            _UNIVERSAL_JOB_TYPE_RE.fullmatch(
                value
            )
        )
    )


def validate_universal_job_type(
    value: Any,
) -> str:
    """Validate canonical Universal Job type naming without coercion."""

    if not isinstance(value, str):
        raise UniversalJobIdentityError(
            "job_type must be a string.",
            code="invalid_job_type_type",
            violations=(
                "job_type must be a string",
            ),
        )

    if not value:
        raise UniversalJobIdentityError(
            "job_type is required.",
            code="missing_job_type",
            violations=(
                "job_type is required",
            ),
        )

    if value != value.strip():
        raise UniversalJobIdentityError(
            "job_type must not contain surrounding whitespace.",
            code="invalid_job_type_format",
            violations=(
                "job_type must already be canonical lowercase snake_case",
            ),
        )

    if len(value) > UNIVERSAL_JOB_TYPE_MAX_LENGTH:
        raise UniversalJobIdentityError(
            "job_type exceeds the maximum permitted length.",
            code="job_type_too_long",
            violations=(
                (
                    "job_type must not exceed "
                    f"{UNIVERSAL_JOB_TYPE_MAX_LENGTH} characters"
                ),
            ),
        )

    if not _UNIVERSAL_JOB_TYPE_RE.fullmatch(
        value
    ):
        raise UniversalJobIdentityError(
            "job_type does not satisfy canonical naming rules.",
            code="invalid_job_type_format",
            violations=(
                "job_type must use lowercase snake_case",
            ),
        )

    return value


def explain_universal_job_identity_v1() -> dict[str, Any]:
    """Return the certified Phase 2.1.3 identity design."""

    return {
        "phase": "2.1.3",
        "component": (
            "Universal Job Identity & Naming"
        ),
        "identity_version": (
            UNIVERSAL_JOB_IDENTITY_VERSION
        ),
        "job_id": {
            "prefix": (
                UNIVERSAL_JOB_ID_PREFIX
            ),
            "grammar": (
                "uj_<32 lowercase hexadecimal characters>"
            ),
            "entropy_bits": 128,
            "opaque": True,
            "contains_workspace_id": False,
            "contains_job_type": False,
            "contains_timestamp": False,
            "contains_payload_data": False,
        },
        "job_type": {
            "grammar": (
                "lowercase snake_case"
            ),
            "maximum_length": (
                UNIVERSAL_JOB_TYPE_MAX_LENGTH
            ),
        },
        "responsibilities": [
            "generate canonical Universal Job IDs",
            "validate explicit Universal Job IDs",
            "validate canonical Universal Job type names",
            "enforce the fixed Universal Job namespace prefix",
        ],
        "prohibitions": [
            "no persistence writes",
            "no queue writes",
            "no Runtime Registration loading",
            "no worker execution",
            "no ledger writes",
            "no duplicate detection",
            "no idempotency resolution",
            "no payload-derived identity",
            "no timestamp-derived identity",
        ],
    }


__all__ = [
    "UNIVERSAL_JOB_IDENTITY_VERSION",
    "UNIVERSAL_JOB_ID_PREFIX",
    "UNIVERSAL_JOB_ID_HEX_LENGTH",
    "UNIVERSAL_JOB_ID_LENGTH",
    "UNIVERSAL_JOB_TYPE_MAX_LENGTH",
    "UniversalJobIdentityError",
    "is_canonical_universal_job_id",
    "validate_universal_job_id",
    "generate_universal_job_id",
    "resolve_universal_job_id",
    "is_canonical_universal_job_type",
    "validate_universal_job_type",
    "explain_universal_job_identity_v1",
]
