from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Optional


UNIVERSAL_JOB_RESULT_REFERENCE_VERSION = (
    "universal_job_result_reference_v2.1.13"
)

UNIVERSAL_JOB_RESULT_REFERENCE_SCHEMA_VERSION = (
    "universal_job_result_reference_schema_v1"
)

MAX_UNIVERSAL_JOB_RESULT_REFERENCE_LENGTH = 4096


class UniversalJobResultReferenceError(
    ValueError
):
    """Raised when a Universal Job result reference is invalid."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:

        super().__init__(
            message
        )

        self.code = str(
            code
        )

        self.value = value


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalJobResultReference:
    """
    Canonical validated result reference for one Universal Job.

    The reference identifies the primary logical result of a job.

    The Universal Runtime treats the value as opaque. This authority
    does not interpret URI schemes, filesystem paths, storage providers,
    result formats, artifact semantics, producer-specific field names,
    or job lifecycle state.
    """

    value: Optional[str]

    @property
    def has_reference(
        self,
    ) -> bool:

        return (
            self.value
            is not None
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version": (
                UNIVERSAL_JOB_RESULT_REFERENCE_SCHEMA_VERSION
            ),
            "result_reference":
                self.value,
        }


def normalize_universal_job_result_reference(
    value: Any,
) -> Optional[str]:
    """
    Validate and normalize one canonical Universal Job result reference.

    Rules:
    - None remains None.
    - Only strings or None are accepted.
    - Surrounding whitespace is removed.
    - Blank strings normalize to None.
    - Maximum canonical length is 4096 characters.
    - Case is preserved.
    - Internal characters are preserved.
    - URI syntax is not required.
    - Filesystem syntax is not required.
    - No existence check is performed.
    """

    if value is None:
        return None

    if not isinstance(
        value,
        str,
    ):
        raise UniversalJobResultReferenceError(
            (
                "result_reference must be "
                "a string or None."
            ),
            code="invalid_result_reference_type",
            value=value,
        )

    normalized = value.strip()

    if not normalized:
        return None

    if (
        len(
            normalized
        )
        > MAX_UNIVERSAL_JOB_RESULT_REFERENCE_LENGTH
    ):
        raise UniversalJobResultReferenceError(
            (
                "result_reference must not exceed "
                f"{MAX_UNIVERSAL_JOB_RESULT_REFERENCE_LENGTH} "
                "characters."
            ),
            code="result_reference_too_long",
            value=value,
        )

    return normalized


def validate_universal_job_result_reference(
    value: Any,
) -> UniversalJobResultReference:
    """Return the canonical immutable result-reference representation."""

    return UniversalJobResultReference(
        value=(
            normalize_universal_job_result_reference(
                value
            )
        )
    )


def is_canonical_universal_job_result_reference(
    value: Any,
) -> bool:
    """
    Return True only when value is already in canonical representation.

    None is canonical.
    A non-empty string is canonical when normalization does not alter it.
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
            normalize_universal_job_result_reference(
                value
            )
        )
    except UniversalJobResultReferenceError:
        return False

    return (
        normalized is not None
        and normalized == value
    )


def explain_universal_job_result_reference_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "2.1.13",
            "component":
                "Universal Job Result Reference",
            "version":
                UNIVERSAL_JOB_RESULT_REFERENCE_VERSION,
            "schema_version":
                UNIVERSAL_JOB_RESULT_REFERENCE_SCHEMA_VERSION,
            "canonical_field":
                "result_reference",
            "scope":
                "LinkCraftor-wide",
            "cardinality":
                "zero_or_one",
            "semantic_role": (
                "primary logical result reference "
                "for one Universal Job"
            ),
            "maximum_length":
                MAX_UNIVERSAL_JOB_RESULT_REFERENCE_LENGTH,
            "rules": (
                "None remains None",
                "only strings or None are accepted",
                "surrounding whitespace is removed",
                "blank strings normalize to None",
                (
                    "references longer than 4096 "
                    "characters are rejected"
                ),
                "case is preserved",
                "internal characters are preserved",
                (
                    "references are opaque to "
                    "the Universal Runtime"
                ),
                "URI syntax is not required",
                "filesystem path syntax is not required",
                "references are not rewritten",
            ),
            "relationship_to_artifacts": (
                "result_reference identifies the primary "
                "logical result; artifact_references are "
                "separate supporting/generated references"
            ),
            "lifecycle_rule": (
                "this authority does not require, infer, "
                "or mutate any Universal Job status"
            ),
            "producer_rule": (
                "the producing runtime/stage supplies a native "
                "primary-result reference which is mapped into "
                "the canonical result_reference field"
            ),
            "prohibitions": (
                (
                    "does not determine whether a job "
                    "has succeeded or completed"
                ),
                "does not perform status transitions",
                "does not write job results",
                "does not read job results",
                "does not persist result references",
                "does not inspect result stores",
                "does not inspect artifact_references",
                "does not resolve producer-specific aliases",
                "does not validate URI schemes",
                "does not validate filesystem paths",
                "does not verify referenced-resource existence",
                "does not perform filesystem I/O",
                "does not perform network I/O",
                "does not modify the referenced resource",
                "does not perform orchestration",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_JOB_RESULT_REFERENCE_VERSION",
    "UNIVERSAL_JOB_RESULT_REFERENCE_SCHEMA_VERSION",
    "MAX_UNIVERSAL_JOB_RESULT_REFERENCE_LENGTH",
    "UniversalJobResultReferenceError",
    "UniversalJobResultReference",
    "normalize_universal_job_result_reference",
    "validate_universal_job_result_reference",
    "is_canonical_universal_job_result_reference",
    "explain_universal_job_result_reference_v1",
]
