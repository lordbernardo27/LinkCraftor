from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Optional


UNIVERSAL_JOB_LINEAGE_VERSION = (
    "universal_job_lineage_v2.1.9"
)

UNIVERSAL_JOB_LINEAGE_SCHEMA_VERSION = (
    "universal_job_lineage_schema_v1"
)


class UniversalJobLineageError(ValueError):
    """Raised when Universal Job lineage values are structurally invalid."""

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


def _clean_optional_lineage_identifier(
    value: Any,
    *,
    field_name: str,
) -> Optional[str]:
    """
    Normalize an optional lineage/correlation identifier.

    Phase 2.1.9 owns relationship representation, not the frozen
    Phase 2.1.3 Universal Job identity namespace.
    """

    if value is None:
        return None

    if not isinstance(
        value,
        str,
    ):
        raise UniversalJobLineageError(
            f"{field_name} must be a string or None.",
            code=f"invalid_{field_name}",
            value=value,
        )

    normalized = value.strip()

    if not normalized:
        return None

    return normalized


def normalize_parent_job_id(
    value: Any,
) -> Optional[str]:
    """Normalize an optional parent Universal Job reference."""

    return _clean_optional_lineage_identifier(
        value,
        field_name="parent_job_id",
    )


def normalize_dependency_job_ids(
    value: Any,
) -> tuple[str, ...]:
    """
    Normalize dependency references.

    Duplicate identifiers are removed while preserving first-seen order.
    """

    if value is None:
        return ()

    if isinstance(
        value,
        (
            str,
            bytes,
            Mapping,
        ),
    ):
        raise UniversalJobLineageError(
            (
                "dependency_job_ids must be an "
                "iterable of identifiers."
            ),
            code="invalid_dependency_job_ids",
            value=value,
        )

    try:
        iterator = iter(
            value
        )

    except TypeError as exc:
        raise UniversalJobLineageError(
            (
                "dependency_job_ids must be an "
                "iterable of identifiers."
            ),
            code="invalid_dependency_job_ids",
            value=value,
        ) from exc

    normalized: dict[str, None] = {}

    for item in iterator:

        if not isinstance(
            item,
            str,
        ):
            raise UniversalJobLineageError(
                (
                    "dependency_job_ids must contain "
                    "only strings."
                ),
                code="invalid_dependency_job_ids",
                value=item,
            )

        identifier = item.strip()

        if not identifier:
            raise UniversalJobLineageError(
                (
                    "dependency_job_ids must not "
                    "contain empty values."
                ),
                code="invalid_dependency_job_ids",
                value=item,
            )

        normalized.setdefault(
            identifier,
            None,
        )

    return tuple(
        normalized
    )


def normalize_batch_id(
    value: Any,
) -> Optional[str]:
    """Normalize an optional batch correlation identifier."""

    return _clean_optional_lineage_identifier(
        value,
        field_name="batch_id",
    )


def normalize_pipeline_run_id(
    value: Any,
) -> Optional[str]:
    """Normalize an optional pipeline-run correlation identifier."""

    return _clean_optional_lineage_identifier(
        value,
        field_name="pipeline_run_id",
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalJobLineageValue:
    """
    Immutable normalized Universal Job lineage/correlation view.
    """

    job_id: str
    parent_job_id: Optional[str]
    dependency_job_ids: tuple[str, ...]
    batch_id: Optional[str]
    pipeline_run_id: Optional[str]

    @property
    def has_parent(
        self,
    ) -> bool:
        return self.parent_job_id is not None

    @property
    def has_dependencies(
        self,
    ) -> bool:
        return bool(
            self.dependency_job_ids
        )

    @property
    def dependency_count(
        self,
    ) -> int:
        return len(
            self.dependency_job_ids
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "schema_version": (
                UNIVERSAL_JOB_LINEAGE_SCHEMA_VERSION
            ),
            "job_id": self.job_id,
            "parent_job_id":
                self.parent_job_id,
            "dependency_job_ids":
                list(
                    self.dependency_job_ids
                ),
            "batch_id":
                self.batch_id,
            "pipeline_run_id":
                self.pipeline_run_id,
            "has_parent":
                self.has_parent,
            "has_dependencies":
                self.has_dependencies,
            "dependency_count":
                self.dependency_count,
        }


def validate_universal_job_lineage(
    *,
    job_id: Any,
    parent_job_id: Any = None,
    dependency_job_ids: Any = (),
    batch_id: Any = None,
    pipeline_run_id: Any = None,
) -> UniversalJobLineageValue:
    """
    Normalize and validate a job's direct lineage/correlation values.

    This performs no repository lookup and no cross-job graph traversal.
    """

    if not isinstance(
        job_id,
        str,
    ):
        raise UniversalJobLineageError(
            "job_id must be a non-empty string.",
            code="invalid_lineage_job_id",
            value=job_id,
        )

    normalized_job_id = (
        job_id.strip()
    )

    if not normalized_job_id:
        raise UniversalJobLineageError(
            "job_id must be a non-empty string.",
            code="invalid_lineage_job_id",
            value=job_id,
        )

    normalized_parent = (
        normalize_parent_job_id(
            parent_job_id
        )
    )

    normalized_dependencies = (
        normalize_dependency_job_ids(
            dependency_job_ids
        )
    )

    normalized_batch = (
        normalize_batch_id(
            batch_id
        )
    )

    normalized_pipeline_run = (
        normalize_pipeline_run_id(
            pipeline_run_id
        )
    )

    if (
        normalized_parent
        == normalized_job_id
    ):
        raise UniversalJobLineageError(
            (
                "parent_job_id must not equal "
                "job_id."
            ),
            code="self_parent_job",
            value=normalized_parent,
        )

    if (
        normalized_job_id
        in normalized_dependencies
    ):
        raise UniversalJobLineageError(
            (
                "dependency_job_ids must not "
                "contain job_id."
            ),
            code="self_dependency_job",
            value=normalized_job_id,
        )

    return UniversalJobLineageValue(
        job_id=normalized_job_id,
        parent_job_id=normalized_parent,
        dependency_job_ids=(
            normalized_dependencies
        ),
        batch_id=normalized_batch,
        pipeline_run_id=(
            normalized_pipeline_run
        ),
    )


def explain_universal_job_lineage_v1(
) -> Mapping[str, Any]:
    """Describe the Phase 2.1.9 authority boundary."""

    return MappingProxyType(
        {
            "phase": "2.1.9",
            "component":
                "Universal Job Lineage",
            "version":
                UNIVERSAL_JOB_LINEAGE_VERSION,
            "schema_version":
                UNIVERSAL_JOB_LINEAGE_SCHEMA_VERSION,
            "fields": (
                "parent_job_id",
                "dependency_job_ids",
                "batch_id",
                "pipeline_run_id",
            ),
            "invariants": (
                "parent_job_id is optional",
                (
                    "dependency_job_ids are "
                    "deduplicated in first-seen order"
                ),
                (
                    "parent_job_id must not "
                    "equal job_id"
                ),
                (
                    "dependency_job_ids must not "
                    "contain job_id"
                ),
                "batch_id is optional",
                "pipeline_run_id is optional",
            ),
            "prohibitions": (
                "does not resolve referenced jobs",
                "does not verify referenced-job existence",
                "does not execute dependencies",
                "does not wait for dependencies",
                "does not perform cross-job cycle detection",
                "does not schedule batches",
                "does not orchestrate pipeline runs",
                "does not execute retries",
                "does not own retry_of or retry_attempt payload markers",
                "does not perform I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_JOB_LINEAGE_VERSION",
    "UNIVERSAL_JOB_LINEAGE_SCHEMA_VERSION",
    "UniversalJobLineageError",
    "UniversalJobLineageValue",
    "normalize_parent_job_id",
    "normalize_dependency_job_ids",
    "normalize_batch_id",
    "normalize_pipeline_run_id",
    "validate_universal_job_lineage",
    "explain_universal_job_lineage_v1",
]
