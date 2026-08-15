from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Optional


UNIVERSAL_JOB_IDEMPOTENCY_KEY_VERSION = (
    "universal_job_idempotency_key_v2.1.10"
)

UNIVERSAL_JOB_IDEMPOTENCY_KEY_SCHEMA_VERSION = (
    "universal_job_idempotency_key_schema_v1"
)


class UniversalJobIdempotencyKeyError(ValueError):
    """Raised when an idempotency key is structurally invalid."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "invalid_idempotency_key",
        value: Any = None,
    ) -> None:
        super().__init__(message)

        self.code = str(code)
        self.value = value


def normalize_universal_job_idempotency_key(
    value: Any,
) -> Optional[str]:
    """
    Normalize an optional caller-supplied Universal Job idempotency key.

    Phase 2.1.10 deliberately does not derive keys, perform duplicate
    detection, inspect job stores, interpret Runtime Registration
    idempotency_fields, or perform duplicate handling.
    """

    if value is None:
        return None

    if not isinstance(
        value,
        str,
    ):
        raise UniversalJobIdempotencyKeyError(
            (
                "idempotency_key must be a string "
                "or None."
            ),
            value=value,
        )

    normalized = value.strip()

    if not normalized:
        return None

    return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalJobIdempotencyKeyValue:
    """Immutable normalized idempotency-key representation."""

    idempotency_key: Optional[str]

    @property
    def has_key(
        self,
    ) -> bool:
        return self.idempotency_key is not None

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "schema_version": (
                UNIVERSAL_JOB_IDEMPOTENCY_KEY_SCHEMA_VERSION
            ),
            "idempotency_key":
                self.idempotency_key,
            "has_key":
                self.has_key,
        }


def validate_universal_job_idempotency_key(
    value: Any,
) -> UniversalJobIdempotencyKeyValue:
    """Return the canonical immutable idempotency-key view."""

    normalized = (
        normalize_universal_job_idempotency_key(
            value
        )
    )

    return UniversalJobIdempotencyKeyValue(
        idempotency_key=normalized,
    )


def explain_universal_job_idempotency_key_v1(
) -> Mapping[str, Any]:
    """Describe the Phase 2.1.10 authority boundary."""

    return MappingProxyType(
        {
            "phase": "2.1.10",
            "component":
                "Universal Job Idempotency Key",
            "version":
                UNIVERSAL_JOB_IDEMPOTENCY_KEY_VERSION,
            "schema_version":
                UNIVERSAL_JOB_IDEMPOTENCY_KEY_SCHEMA_VERSION,
            "field":
                "idempotency_key",
            "semantics": (
                "the field is optional",
                "None remains None",
                "blank strings normalize to None",
                "nonblank strings are trimmed",
                "case is preserved",
                "internal characters are preserved",
                "the key is caller supplied",
            ),
            "prohibitions": (
                "does not generate an idempotency key",
                "does not hash the idempotency key",
                "does not lowercase the idempotency key",
                "does not perform duplicate detection",
                "does not search the queue",
                "does not search a job store",
                (
                    "does not interpret Runtime Registration "
                    "idempotency_fields"
                ),
                "does not suppress duplicate jobs",
                "does not reuse existing jobs",
                "does not reject duplicates",
                "does not perform duplicate handling",
                "does not perform persistence or I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_JOB_IDEMPOTENCY_KEY_VERSION",
    "UNIVERSAL_JOB_IDEMPOTENCY_KEY_SCHEMA_VERSION",
    "UniversalJobIdempotencyKeyError",
    "UniversalJobIdempotencyKeyValue",
    "normalize_universal_job_idempotency_key",
    "validate_universal_job_idempotency_key",
    "explain_universal_job_idempotency_key_v1",
]
