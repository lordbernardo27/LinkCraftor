from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


UNIVERSAL_JOB_PAYLOAD_REFERENCE_VERSION = (
    "universal_job_payload_reference_v2.1.5"
)

UNIVERSAL_JOB_PAYLOAD_REFERENCE_SCHEMA_VERSION = (
    "universal_job_payload_reference_schema_v1"
)

MAX_UNIVERSAL_JOB_PAYLOAD_REFERENCE_LENGTH = 4096


class UniversalJobPayloadReferenceError(ValueError):
    """Raised when a Universal Job payload reference is invalid."""

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
class UniversalJobPayloadReference:
    """
    Canonical validated payload reference for one Universal Job.

    The Universal Runtime treats the reference as opaque. It does not
    interpret path semantics, URI schemes, storage providers, document
    types, pipeline names, or producer-specific field names.
    """

    value: Optional[str]

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "schema_version": (
                UNIVERSAL_JOB_PAYLOAD_REFERENCE_SCHEMA_VERSION
            ),
            "payload_reference": self.value,
        }


def normalize_universal_job_payload_reference(
    value: Any,
) -> Optional[str]:
    """
    Validate and normalize one canonical Universal Job payload reference.

    Rules:
    - None remains None.
    - Only strings are accepted.
    - Surrounding whitespace is removed.
    - Blank strings normalize to None.
    - Maximum canonical length is 4096 characters.
    - The reference remains opaque.
    - No URI requirement is imposed.
    - No path rewriting is performed.
    - No producer-specific aliases are resolved here.
    """

    if value is None:
        return None

    if not isinstance(
        value,
        str,
    ):
        raise UniversalJobPayloadReferenceError(
            (
                "payload_reference must be a string "
                "or None."
            ),
            code="invalid_payload_reference_type",
            value=value,
        )

    normalized = value.strip()

    if not normalized:
        return None

    if (
        len(normalized)
        > MAX_UNIVERSAL_JOB_PAYLOAD_REFERENCE_LENGTH
    ):
        raise UniversalJobPayloadReferenceError(
            (
                "payload_reference exceeds the maximum "
                f"length of "
                f"{MAX_UNIVERSAL_JOB_PAYLOAD_REFERENCE_LENGTH} "
                "characters."
            ),
            code="payload_reference_too_long",
            value=value,
        )

    return normalized


def validate_universal_job_payload_reference(
    value: Any,
) -> UniversalJobPayloadReference:
    """
    Return the canonical immutable payload-reference value object.
    """

    return UniversalJobPayloadReference(
        value=(
            normalize_universal_job_payload_reference(
                value
            )
        )
    )


def is_canonical_universal_job_payload_reference(
    value: Any,
) -> bool:
    """
    Return True only when the supplied value is already canonical.

    Canonical values are:
    - None
    - a non-blank string with no surrounding whitespace
    - at most 4096 characters
    """

    if value is None:
        return True

    if not isinstance(
        value,
        str,
    ):
        return False

    if not value:
        return False

    if value != value.strip():
        return False

    if (
        len(value)
        > MAX_UNIVERSAL_JOB_PAYLOAD_REFERENCE_LENGTH
    ):
        return False

    return True


def explain_universal_job_payload_reference_v1(
) -> dict[str, Any]:
    """
    Describe the Phase 2.1.5 universal authority boundary.
    """

    return {
        "phase": "2.1.5",
        "component": (
            "Universal Job Payload Reference"
        ),
        "version": (
            UNIVERSAL_JOB_PAYLOAD_REFERENCE_VERSION
        ),
        "schema_version": (
            UNIVERSAL_JOB_PAYLOAD_REFERENCE_SCHEMA_VERSION
        ),
        "canonical_field": (
            "payload_reference"
        ),
        "scope": "LinkCraftor-wide",
        "maximum_length": (
            MAX_UNIVERSAL_JOB_PAYLOAD_REFERENCE_LENGTH
        ),
        "rules": [
            "None remains None",
            "only strings or None are accepted",
            "surrounding whitespace is removed",
            "blank strings normalize to None",
            (
                "references longer than 4096 characters "
                "are rejected"
            ),
            "references are opaque to the Universal Runtime",
            "URI syntax is not required",
            "filesystem path syntax is not required",
            "references are not rewritten",
        ],
        "producer_rule": (
            "Each pipeline or stage maps its native source "
            "reference into the canonical payload_reference "
            "field before entering the Universal Job model."
        ),
        "prohibitions": [
            (
                "does not inspect payload dictionaries for "
                "producer-specific aliases"
            ),
            (
                "does not resolve payload_ref, source_record_id, "
                "html_id, or any other pipeline-native field"
            ),
            (
                "does not know UUCD, UDARE, uploaded-document, "
                "website, semantic, billing, or other pipeline "
                "semantics"
            ),
            "does not perform filesystem I/O",
            "does not verify that the referenced resource exists",
            "does not modify the referenced resource",
        ],
    }


__all__ = [
    "UNIVERSAL_JOB_PAYLOAD_REFERENCE_VERSION",
    "UNIVERSAL_JOB_PAYLOAD_REFERENCE_SCHEMA_VERSION",
    "MAX_UNIVERSAL_JOB_PAYLOAD_REFERENCE_LENGTH",
    "UniversalJobPayloadReferenceError",
    "UniversalJobPayloadReference",
    "normalize_universal_job_payload_reference",
    "validate_universal_job_payload_reference",
    "is_canonical_universal_job_payload_reference",
    "explain_universal_job_payload_reference_v1",
]
