"""
LinkCraftor Universal Runtime Infrastructure
Phase 2.1.5 — Job Payload Reference

Canonical authority for Universal Job payload-reference normalization
and resolution.

A payload reference identifies the job's primary persisted payload or
content record. It does not contain the payload itself and does not
replace payload-level references such as body_ref.

This component is deliberately I/O-free.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final, Optional


UNIVERSAL_JOB_PAYLOAD_REFERENCE_VERSION: Final[str] = (
    "universal_job_payload_reference_v2.1.5"
)

UNIVERSAL_JOB_PAYLOAD_REFERENCE_SCHEMA_VERSION: Final[str] = (
    "universal_job_payload_reference_schema_v1"
)

UNIVERSAL_JOB_PAYLOAD_REFERENCE_MAX_LENGTH: Final[int] = 4096


PAYLOAD_REFERENCE_SOURCE_NONE: Final[str] = (
    "none"
)

PAYLOAD_REFERENCE_SOURCE_EXPLICIT: Final[str] = (
    "explicit_payload_reference"
)

PAYLOAD_REFERENCE_SOURCE_CANONICAL_PAYLOAD: Final[str] = (
    "payload.payload_reference"
)

PAYLOAD_REFERENCE_SOURCE_LEGACY_PAYLOAD_REF: Final[str] = (
    "payload.payload_ref"
)

PAYLOAD_REFERENCE_SOURCE_LEGACY_SOURCE_RECORD_ID: Final[str] = (
    "payload.source_record_id"
)

PAYLOAD_REFERENCE_SOURCE_LEGACY_HTML_ID: Final[str] = (
    "payload.html_id"
)


UNIVERSAL_JOB_PAYLOAD_REFERENCE_RESOLUTION_ORDER: Final[
    tuple[str, ...]
] = (
    PAYLOAD_REFERENCE_SOURCE_EXPLICIT,
    PAYLOAD_REFERENCE_SOURCE_CANONICAL_PAYLOAD,
    PAYLOAD_REFERENCE_SOURCE_LEGACY_PAYLOAD_REF,
    PAYLOAD_REFERENCE_SOURCE_LEGACY_SOURCE_RECORD_ID,
    PAYLOAD_REFERENCE_SOURCE_LEGACY_HTML_ID,
)


LEGACY_PAYLOAD_REFERENCE_SOURCES: Final[
    frozenset[str]
] = frozenset(
    {
        PAYLOAD_REFERENCE_SOURCE_LEGACY_PAYLOAD_REF,
        PAYLOAD_REFERENCE_SOURCE_LEGACY_SOURCE_RECORD_ID,
        PAYLOAD_REFERENCE_SOURCE_LEGACY_HTML_ID,
    }
)


class UniversalJobPayloadReferenceError(
    ValueError
):
    """Raised when a Universal Job payload reference is invalid."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "invalid_payload_reference",
        violations: tuple[str, ...] = (),
    ) -> None:
        super().__init__(
            message
        )

        self.code = str(
            code
        )

        self.violations = tuple(
            str(item)
            for item in violations
        )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalJobPayloadReferenceResolution:
    """
    Immutable result of canonical payload-reference resolution.

    payload_reference:
        Canonical normalized reference or None.

    source:
        Which creation input supplied the selected reference.

    legacy_alias_used:
        True only when a legacy compatibility alias supplied the
        selected reference.
    """

    payload_reference: Optional[str]

    source: str

    legacy_alias_used: bool

    resolution_version: str = (
        UNIVERSAL_JOB_PAYLOAD_REFERENCE_VERSION
    )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "schema_version":
                UNIVERSAL_JOB_PAYLOAD_REFERENCE_SCHEMA_VERSION,

            "payload_reference":
                self.payload_reference,

            "source":
                self.source,

            "legacy_alias_used":
                self.legacy_alias_used,

            "resolution_version":
                self.resolution_version,
        }


def _normalize_payload_reference_candidate(
    value: Any,
    *,
    field_name: str,
) -> Optional[str]:
    """
    Normalize one candidate without coercing arbitrary values.

    None and blank strings represent absence.

    Non-string values are rejected because the frozen UniversalJob
    contract declares payload_reference as Optional[str].
    """

    if value is None:
        return None

    if not isinstance(
        value,
        str,
    ):
        raise UniversalJobPayloadReferenceError(
            (
                f"{field_name} must be a string "
                "or null."
            ),
            code="invalid_payload_reference",
            violations=(
                (
                    f"{field_name} must be a "
                    "string or null"
                ),
            ),
        )

    normalized = value.strip()

    if not normalized:
        return None

    if (
        len(normalized)
        > UNIVERSAL_JOB_PAYLOAD_REFERENCE_MAX_LENGTH
    ):
        raise UniversalJobPayloadReferenceError(
            (
                f"{field_name} exceeds the "
                "maximum payload-reference "
                "length."
            ),
            code="payload_reference_too_long",
            violations=(
                (
                    f"{field_name} must not "
                    f"exceed "
                    f"{UNIVERSAL_JOB_PAYLOAD_REFERENCE_MAX_LENGTH} "
                    "characters"
                ),
            ),
        )

    return normalized


def normalize_universal_job_payload_reference(
    value: Any,
) -> Optional[str]:
    """
    Normalize one canonical Universal Job payload reference.

    The reference remains opaque. This component intentionally does
    not require or invent URI schemes and does not rewrite path
    separators.
    """

    return _normalize_payload_reference_candidate(
        value,
        field_name="payload_reference",
    )


def resolve_universal_job_payload_reference(
    *,
    explicit_reference: Any = None,
    payload: Optional[Mapping[str, Any]] = None,
) -> UniversalJobPayloadReferenceResolution:
    """
    Resolve the canonical payload reference using the certified
    compatibility precedence.

    Resolution order:

    1. explicit payload_reference argument
    2. payload.payload_reference
    3. payload.payload_ref
    4. payload.source_record_id
    5. payload.html_id
    6. None

    The last three payload keys are legacy compatibility aliases.
    They are accepted only as strings and are not new canonical
    contract fields.
    """

    if payload is None:
        normalized_payload: Mapping[str, Any] = {}

    elif isinstance(
        payload,
        Mapping,
    ):
        normalized_payload = payload

    else:
        raise UniversalJobPayloadReferenceError(
            "payload must be a mapping when resolving payload_reference.",
            code="invalid_payload_reference_payload",
            violations=(
                (
                    "payload must be a mapping "
                    "when resolving payload_reference"
                ),
            ),
        )

    candidates = (
        (
            PAYLOAD_REFERENCE_SOURCE_EXPLICIT,
            explicit_reference,
            "payload_reference",
        ),
        (
            PAYLOAD_REFERENCE_SOURCE_CANONICAL_PAYLOAD,
            normalized_payload.get(
                "payload_reference"
            ),
            "payload.payload_reference",
        ),
        (
            PAYLOAD_REFERENCE_SOURCE_LEGACY_PAYLOAD_REF,
            normalized_payload.get(
                "payload_ref"
            ),
            "payload.payload_ref",
        ),
        (
            PAYLOAD_REFERENCE_SOURCE_LEGACY_SOURCE_RECORD_ID,
            normalized_payload.get(
                "source_record_id"
            ),
            "payload.source_record_id",
        ),
        (
            PAYLOAD_REFERENCE_SOURCE_LEGACY_HTML_ID,
            normalized_payload.get(
                "html_id"
            ),
            "payload.html_id",
        ),
    )

    for (
        source,
        candidate,
        field_name,
    ) in candidates:

        normalized = (
            _normalize_payload_reference_candidate(
                candidate,
                field_name=field_name,
            )
        )

        if normalized is None:
            continue

        return (
            UniversalJobPayloadReferenceResolution(
                payload_reference=normalized,
                source=source,
                legacy_alias_used=(
                    source
                    in LEGACY_PAYLOAD_REFERENCE_SOURCES
                ),
            )
        )

    return (
        UniversalJobPayloadReferenceResolution(
            payload_reference=None,
            source=PAYLOAD_REFERENCE_SOURCE_NONE,
            legacy_alias_used=False,
        )
    )


def is_canonical_universal_job_payload_reference(
    value: Any,
) -> bool:
    """
    Return True when value is already in canonical optional-reference
    form.

    None is canonical because payload_reference is optional.

    Blank or whitespace-padded strings are not canonical even though
    they can be normalized.
    """

    if value is None:
        return True

    if not isinstance(
        value,
        str,
    ):
        return False

    try:
        normalized = (
            normalize_universal_job_payload_reference(
                value
            )
        )

    except UniversalJobPayloadReferenceError:
        return False

    return (
        normalized is not None
        and normalized == value
    )


def explain_universal_job_payload_reference_v1(
) -> dict[str, Any]:
    """Return the canonical Phase 2.1.5 architecture declaration."""

    return {
        "phase":
            "2.1.5",

        "component":
            "Universal Job Payload Reference",

        "version":
            UNIVERSAL_JOB_PAYLOAD_REFERENCE_VERSION,

        "schema_version":
            UNIVERSAL_JOB_PAYLOAD_REFERENCE_SCHEMA_VERSION,

        "contract_field":
            "payload_reference",

        "contract_type":
            "Optional[str]",

        "maximum_length":
            UNIVERSAL_JOB_PAYLOAD_REFERENCE_MAX_LENGTH,

        "canonical_meaning":
            (
                "reference to the job's primary "
                "persisted payload or content record"
            ),

        "reference_is_payload":
            False,

        "reference_is_metadata":
            False,

        "reference_is_body_ref":
            False,

        "uri_scheme_required":
            False,

        "path_rewriting_performed":
            False,

        "io_performed":
            False,

        "resolution_order":
            list(
                UNIVERSAL_JOB_PAYLOAD_REFERENCE_RESOLUTION_ORDER
            ),

        "legacy_compatibility_aliases": [
            "payload.payload_ref",
            "payload.source_record_id",
            "payload.html_id",
        ],

        "preferred_creation_sources": [
            "explicit_payload_reference",
            "payload.payload_reference",
        ],

        "uucd_mapping":
            (
                "persisted_uucd.content_ref -> "
                "UniversalJob.payload_reference"
            ),

        "body_reference_boundary":
            (
                "body_ref remains payload-level "
                "and does not become "
                "UniversalJob.payload_reference "
                "unless a caller explicitly maps it"
            ),
    }


__all__ = [
    "UNIVERSAL_JOB_PAYLOAD_REFERENCE_VERSION",
    "UNIVERSAL_JOB_PAYLOAD_REFERENCE_SCHEMA_VERSION",
    "UNIVERSAL_JOB_PAYLOAD_REFERENCE_MAX_LENGTH",
    "UNIVERSAL_JOB_PAYLOAD_REFERENCE_RESOLUTION_ORDER",
    "PAYLOAD_REFERENCE_SOURCE_NONE",
    "PAYLOAD_REFERENCE_SOURCE_EXPLICIT",
    "PAYLOAD_REFERENCE_SOURCE_CANONICAL_PAYLOAD",
    "PAYLOAD_REFERENCE_SOURCE_LEGACY_PAYLOAD_REF",
    "PAYLOAD_REFERENCE_SOURCE_LEGACY_SOURCE_RECORD_ID",
    "PAYLOAD_REFERENCE_SOURCE_LEGACY_HTML_ID",
    "LEGACY_PAYLOAD_REFERENCE_SOURCES",
    "UniversalJobPayloadReferenceError",
    "UniversalJobPayloadReferenceResolution",
    "normalize_universal_job_payload_reference",
    "resolve_universal_job_payload_reference",
    "is_canonical_universal_job_payload_reference",
    "explain_universal_job_payload_reference_v1",
]
