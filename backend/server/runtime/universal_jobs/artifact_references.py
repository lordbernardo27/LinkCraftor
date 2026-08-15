from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping


UNIVERSAL_JOB_ARTIFACT_REFERENCES_VERSION = (
    "universal_job_artifact_references_v2.1.14"
)

UNIVERSAL_JOB_ARTIFACT_REFERENCES_SCHEMA_VERSION = (
    "universal_job_artifact_references_schema_v1"
)

MAX_UNIVERSAL_JOB_ARTIFACT_REFERENCE_LENGTH = 4096


class UniversalJobArtifactReferencesError(
    ValueError
):
    """Raised when Universal Job artifact references are invalid."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
        index: int | None = None,
    ) -> None:

        super().__init__(
            message
        )

        self.code = str(
            code
        )

        self.value = value

        self.index = index


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalJobArtifactReferences:
    """
    Canonical artifact-reference collection for one Universal Job.

    Artifact references identify zero or more supporting/generated
    resources associated with the job. References remain opaque to
    the Universal Runtime.
    """

    values: tuple[str, ...]

    @property
    def has_artifacts(
        self,
    ) -> bool:

        return bool(
            self.values
        )

    @property
    def count(
        self,
    ) -> int:

        return len(
            self.values
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version": (
                UNIVERSAL_JOB_ARTIFACT_REFERENCES_SCHEMA_VERSION
            ),
            "artifact_references":
                list(
                    self.values
                ),
        }


def _normalize_one_artifact_reference(
    value: Any,
    *,
    index: int,
) -> str | None:

    if not isinstance(
        value,
        str,
    ):
        raise UniversalJobArtifactReferencesError(
            (
                "artifact_references members must "
                "be strings."
            ),
            code="invalid_artifact_reference_type",
            value=value,
            index=index,
        )

    normalized = value.strip()

    if not normalized:
        return None

    if (
        len(
            normalized
        )
        > MAX_UNIVERSAL_JOB_ARTIFACT_REFERENCE_LENGTH
    ):
        raise UniversalJobArtifactReferencesError(
            (
                "artifact reference must not exceed "
                f"{MAX_UNIVERSAL_JOB_ARTIFACT_REFERENCE_LENGTH} "
                "characters."
            ),
            code="artifact_reference_too_long",
            value=value,
            index=index,
        )

    return normalized


def normalize_universal_job_artifact_references(
    value: Any,
) -> tuple[str, ...]:
    """
    Normalize Universal Job artifact references.

    Rules:
    - None becomes ().
    - A string is treated as one reference.
    - Otherwise an ordered iterable is required.
    - Each member must be a string.
    - Surrounding whitespace is removed.
    - Blank members are omitted.
    - Each canonical member is limited to 4096 characters.
    - Input order is preserved.
    - Duplicate references are preserved.
    - References remain opaque.
    """

    if value is None:
        return ()

    if isinstance(
        value,
        str,
    ):
        raw_values = (
            value,
        )

    else:
        if isinstance(
            value,
            (
                Mapping,
                set,
                frozenset,
                bytes,
                bytearray,
            ),
        ):
            raise UniversalJobArtifactReferencesError(
                (
                    "artifact_references must be "
                    "an ordered iterable of strings, "
                    "a string, or None."
                ),
                code="invalid_artifact_references_collection",
                value=value,
            )

        try:
            raw_values = tuple(
                value
            )

        except TypeError as exc:
            raise UniversalJobArtifactReferencesError(
                (
                    "artifact_references must be "
                    "an ordered iterable of strings, "
                    "a string, or None."
                ),
                code="invalid_artifact_references_collection",
                value=value,
            ) from exc

    normalized_values: list[str] = []

    for index, item in enumerate(
        raw_values
    ):

        normalized = (
            _normalize_one_artifact_reference(
                item,
                index=index,
            )
        )

        if normalized is None:
            continue

        normalized_values.append(
            normalized
        )

    return tuple(
        normalized_values
    )


def validate_universal_job_artifact_references(
    value: Any,
) -> UniversalJobArtifactReferences:

    return UniversalJobArtifactReferences(
        values=(
            normalize_universal_job_artifact_references(
                value
            )
        )
    )


def is_canonical_universal_job_artifact_references(
    value: Any,
) -> bool:
    """
    Canonical collection representation is tuple[str, ...].

    Every member must already be normalized. Empty tuple is canonical.
    """

    if not isinstance(
        value,
        tuple,
    ):
        return False

    try:
        normalized = (
            normalize_universal_job_artifact_references(
                value
            )
        )

    except UniversalJobArtifactReferencesError:
        return False

    return (
        normalized
        == value
    )


def explain_universal_job_artifact_references_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "2.1.14",
            "component":
                "Universal Job Artifact References",
            "version":
                UNIVERSAL_JOB_ARTIFACT_REFERENCES_VERSION,
            "schema_version":
                UNIVERSAL_JOB_ARTIFACT_REFERENCES_SCHEMA_VERSION,
            "canonical_field":
                "artifact_references",
            "scope":
                "LinkCraftor-wide",
            "cardinality":
                "zero_or_many",
            "canonical_type":
                "tuple[str, ...]",
            "maximum_reference_length":
                MAX_UNIVERSAL_JOB_ARTIFACT_REFERENCE_LENGTH,
            "rules": (
                "None normalizes to an empty tuple",
                "a string is treated as one artifact reference",
                (
                    "ordered iterable inputs normalize "
                    "to an immutable tuple"
                ),
                "each nonblank member must be a string",
                "surrounding whitespace is removed",
                "blank members are omitted",
                (
                    "each canonical reference is limited "
                    "to 4096 characters"
                ),
                "input ordering is preserved",
                "duplicate references are preserved",
                (
                    "references are opaque to "
                    "the Universal Runtime"
                ),
                "URI syntax is not required",
                "filesystem path syntax is not required",
            ),
            "relationship_to_result": (
                "artifact_references identify zero or more "
                "supporting/generated resources; result_reference "
                "is a separate zero-or-one primary logical result"
            ),
            "producer_rule": (
                "artifact-producing stages map their native "
                "supporting resource references into the canonical "
                "artifact_references collection"
            ),
            "prohibitions": (
                "does not create artifacts",
                "does not read artifacts",
                "does not write artifacts",
                "does not persist artifacts",
                "does not delete artifacts",
                "does not deduplicate artifact references",
                "does not sort artifact references",
                "does not interpret artifact types",
                "does not inspect artifact metadata",
                "does not calculate artifact hashes",
                "does not validate URI schemes",
                "does not validate filesystem paths",
                "does not verify referenced-resource existence",
                "does not enforce producer-specific artifact counts",
                "does not inspect result_reference",
                "does not inspect checkpoint_reference",
                "does not infer or mutate job status",
                "does not perform filesystem I/O",
                "does not perform network I/O",
                "does not perform orchestration",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_JOB_ARTIFACT_REFERENCES_VERSION",
    "UNIVERSAL_JOB_ARTIFACT_REFERENCES_SCHEMA_VERSION",
    "MAX_UNIVERSAL_JOB_ARTIFACT_REFERENCE_LENGTH",
    "UniversalJobArtifactReferencesError",
    "UniversalJobArtifactReferences",
    "normalize_universal_job_artifact_references",
    "validate_universal_job_artifact_references",
    "is_canonical_universal_job_artifact_references",
    "explain_universal_job_artifact_references_v1",
]
