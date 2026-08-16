from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from backend.server.runtime.universal_queue.creation import (
    UniversalQueueCreationError,
    normalize_universal_queue_id,
)


UNIVERSAL_QUEUE_DEDUPLICATION_VERSION = (
    "universal_queue_deduplication_v3.1.14"
)

UNIVERSAL_QUEUE_DEDUPLICATION_SNAPSHOT_SCHEMA_VERSION = (
    "universal_queue_deduplication_snapshot_schema_v1"
)

UNIVERSAL_QUEUE_DEDUPLICATION_DECISION_SCHEMA_VERSION = (
    "universal_queue_deduplication_decision_schema_v1"
)


class UniversalQueueDeduplicationAdmission(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


class UniversalQueueDeduplicationClassification(str, Enum):
    UNIQUE = "unique"
    DUPLICATE = "duplicate"


class UniversalQueueDeduplicationError(ValueError):
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


def _normalize_nonblank_string(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(value, str):
        raise UniversalQueueDeduplicationError(
            f"{field_name} must be a string.",
            code=f"invalid_{field_name}_type",
            value=value,
        )

    normalized = value.strip()

    if not normalized:
        raise UniversalQueueDeduplicationError(
            f"{field_name} must not be blank.",
            code=f"blank_{field_name}",
            value=value,
        )

    return normalized


def normalize_universal_queue_deduplication_queue_id(
    value: Any,
) -> str:

    try:
        return normalize_universal_queue_id(value)

    except UniversalQueueCreationError as exc:
        raise UniversalQueueDeduplicationError(
            "Invalid canonical Universal Queue queue_id.",
            code="invalid_deduplication_queue_id",
            value=value,
        ) from exc


def normalize_universal_queue_deduplication_job_id(
    value: Any,
) -> str:

    return _normalize_nonblank_string(
        value,
        field_name="job_id",
    )


def normalize_universal_queue_existing_job_ids(
    value: Any,
) -> tuple[str, ...]:

    if isinstance(value, (str, bytes, Mapping)):
        raise UniversalQueueDeduplicationError(
            (
                "existing_job_ids must be an iterable "
                "of canonical job_id strings."
            ),
            code="invalid_existing_job_ids",
            value=value,
        )

    try:
        raw_items = tuple(value)

    except TypeError as exc:
        raise UniversalQueueDeduplicationError(
            "existing_job_ids must be iterable.",
            code="invalid_existing_job_ids",
            value=value,
        ) from exc

    normalized = tuple(
        normalize_universal_queue_deduplication_job_id(item)
        for item in raw_items
    )

    if len(set(normalized)) != len(normalized):
        raise UniversalQueueDeduplicationError(
            (
                "existing_job_ids contains duplicate "
                "queue-membership evidence."
            ),
            code="duplicate_existing_membership_evidence",
            value=normalized,
        )

    return tuple(sorted(normalized))


def normalize_universal_queue_deduplication_admission(
    value: Any,
) -> UniversalQueueDeduplicationAdmission:

    if isinstance(
        value,
        UniversalQueueDeduplicationAdmission,
    ):
        return value

    if not isinstance(value, str):
        raise UniversalQueueDeduplicationError(
            "admission must be a supported string.",
            code="invalid_deduplication_admission_type",
            value=value,
        )

    try:
        return UniversalQueueDeduplicationAdmission(
            value.strip().lower()
        )

    except ValueError as exc:
        raise UniversalQueueDeduplicationError(
            "Unsupported queue-deduplication admission.",
            code="unsupported_deduplication_admission",
            value=value,
        ) from exc


def normalize_universal_queue_deduplication_classification(
    value: Any,
) -> UniversalQueueDeduplicationClassification:

    if isinstance(
        value,
        UniversalQueueDeduplicationClassification,
    ):
        return value

    if not isinstance(value, str):
        raise UniversalQueueDeduplicationError(
            "classification must be a supported string.",
            code="invalid_deduplication_classification_type",
            value=value,
        )

    try:
        return UniversalQueueDeduplicationClassification(
            value.strip().lower()
        )

    except ValueError as exc:
        raise UniversalQueueDeduplicationError(
            "Unsupported queue-deduplication classification.",
            code="unsupported_deduplication_classification",
            value=value,
        ) from exc


@dataclass(frozen=True, slots=True)
class UniversalQueueDeduplicationSnapshot:
    queue_id: str
    job_id: str
    existing_job_ids: tuple[str, ...]
    schema_version: str = (
        UNIVERSAL_QUEUE_DEDUPLICATION_SNAPSHOT_SCHEMA_VERSION
    )

    def __post_init__(self) -> None:
        set_ = object.__setattr__

        set_(
            self,
            "queue_id",
            normalize_universal_queue_deduplication_queue_id(
                self.queue_id
            ),
        )

        set_(
            self,
            "job_id",
            normalize_universal_queue_deduplication_job_id(
                self.job_id
            ),
        )

        set_(
            self,
            "existing_job_ids",
            normalize_universal_queue_existing_job_ids(
                self.existing_job_ids
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_DEDUPLICATION_SNAPSHOT_SCHEMA_VERSION
        ):
            raise UniversalQueueDeduplicationError(
                "Invalid deduplication snapshot schema_version.",
                code="invalid_deduplication_snapshot_schema_version",
                value=self.schema_version,
            )

    @property
    def identity(self) -> tuple[str, str]:
        return (
            self.queue_id,
            self.job_id,
        )

    @property
    def existing_membership_count(self) -> int:
        return len(self.existing_job_ids)

    @property
    def duplicate_present(self) -> bool:
        return self.job_id in self.existing_job_ids

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "queue_id": self.queue_id,
            "job_id": self.job_id,
            "existing_job_ids": list(self.existing_job_ids),
            "existing_membership_count":
                self.existing_membership_count,
            "duplicate_present": self.duplicate_present,
        }


@dataclass(frozen=True, slots=True)
class UniversalQueueDeduplicationDecision:
    queue_id: str
    job_id: str
    existing_membership_count: int
    duplicate_present: bool
    matched_job_id: str | None
    admission: UniversalQueueDeduplicationAdmission | str
    classification: (
        UniversalQueueDeduplicationClassification
        | str
    )
    mutation_required: bool
    reason: str
    schema_version: str = (
        UNIVERSAL_QUEUE_DEDUPLICATION_DECISION_SCHEMA_VERSION
    )

    def __post_init__(self) -> None:
        set_ = object.__setattr__

        queue_id = (
            normalize_universal_queue_deduplication_queue_id(
                self.queue_id
            )
        )

        job_id = (
            normalize_universal_queue_deduplication_job_id(
                self.job_id
            )
        )

        if (
            isinstance(self.existing_membership_count, bool)
            or not isinstance(
                self.existing_membership_count,
                int,
            )
            or self.existing_membership_count < 0
        ):
            raise UniversalQueueDeduplicationError(
                (
                    "existing_membership_count must be "
                    "a non-negative integer."
                ),
                code="invalid_existing_membership_count",
                value=self.existing_membership_count,
            )

        if not isinstance(self.duplicate_present, bool):
            raise UniversalQueueDeduplicationError(
                "duplicate_present must be bool.",
                code="invalid_duplicate_present_flag",
                value=self.duplicate_present,
            )

        matched_job_id = (
            None
            if self.matched_job_id is None
            else normalize_universal_queue_deduplication_job_id(
                self.matched_job_id
            )
        )

        admission = (
            normalize_universal_queue_deduplication_admission(
                self.admission
            )
        )

        classification = (
            normalize_universal_queue_deduplication_classification(
                self.classification
            )
        )

        if not isinstance(self.mutation_required, bool):
            raise UniversalQueueDeduplicationError(
                "mutation_required must be bool.",
                code="invalid_deduplication_mutation_flag",
                value=self.mutation_required,
            )

        if self.mutation_required is not False:
            raise UniversalQueueDeduplicationError(
                (
                    "3.1.14 classifies queue membership "
                    "but does not mutate or suppress enqueue."
                ),
                code="deduplication_mutation_not_owned",
                value=self.mutation_required,
            )

        if not isinstance(self.reason, str):
            raise UniversalQueueDeduplicationError(
                "reason must be a string.",
                code="invalid_deduplication_reason_type",
                value=self.reason,
            )

        reason = self.reason.strip()

        if not reason:
            raise UniversalQueueDeduplicationError(
                "reason must not be blank.",
                code="blank_deduplication_reason",
                value=self.reason,
            )

        expected_admission = (
            UniversalQueueDeduplicationAdmission.DENY
            if self.duplicate_present
            else UniversalQueueDeduplicationAdmission.ALLOW
        )

        expected_classification = (
            UniversalQueueDeduplicationClassification.DUPLICATE
            if self.duplicate_present
            else UniversalQueueDeduplicationClassification.UNIQUE
        )

        expected_matched_job_id = (
            job_id
            if self.duplicate_present
            else None
        )

        if admission is not expected_admission:
            raise UniversalQueueDeduplicationError(
                "admission is inconsistent with duplicate_present.",
                code="inconsistent_deduplication_admission",
                value=admission.value,
            )

        if classification is not expected_classification:
            raise UniversalQueueDeduplicationError(
                (
                    "classification is inconsistent with "
                    "duplicate_present."
                ),
                code="inconsistent_deduplication_classification",
                value=classification.value,
            )

        if matched_job_id != expected_matched_job_id:
            raise UniversalQueueDeduplicationError(
                (
                    "matched_job_id is inconsistent with "
                    "the canonical queue job identity."
                ),
                code="inconsistent_deduplication_matched_job_id",
                value=matched_job_id,
            )

        if (
            self.duplicate_present
            and self.existing_membership_count < 1
        ):
            raise UniversalQueueDeduplicationError(
                (
                    "duplicate_present=True requires at least "
                    "one existing membership."
                ),
                code="inconsistent_existing_membership_count",
                value=self.existing_membership_count,
            )

        set_(self, "queue_id", queue_id)
        set_(self, "job_id", job_id)
        set_(self, "matched_job_id", matched_job_id)
        set_(self, "admission", admission)
        set_(self, "classification", classification)
        set_(self, "reason", reason)

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_DEDUPLICATION_DECISION_SCHEMA_VERSION
        ):
            raise UniversalQueueDeduplicationError(
                "Invalid deduplication decision schema_version.",
                code="invalid_deduplication_decision_schema_version",
                value=self.schema_version,
            )

    @property
    def identity(self) -> tuple[str, str]:
        return (
            self.queue_id,
            self.job_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "queue_id": self.queue_id,
            "job_id": self.job_id,
            "existing_membership_count":
                self.existing_membership_count,
            "duplicate_present": self.duplicate_present,
            "matched_job_id": self.matched_job_id,
            "admission": self.admission.value,
            "classification": self.classification.value,
            "mutation_required": self.mutation_required,
            "reason": self.reason,
        }


def create_universal_queue_deduplication_snapshot(
    *,
    queue_id: str,
    job_id: str,
    existing_job_ids: Iterable[str],
) -> UniversalQueueDeduplicationSnapshot:

    return UniversalQueueDeduplicationSnapshot(
        queue_id=queue_id,
        job_id=job_id,
        existing_job_ids=tuple(existing_job_ids),
    )


def evaluate_universal_queue_deduplication(
    *,
    snapshot: UniversalQueueDeduplicationSnapshot,
) -> UniversalQueueDeduplicationDecision:

    if not isinstance(
        snapshot,
        UniversalQueueDeduplicationSnapshot,
    ):
        raise UniversalQueueDeduplicationError(
            (
                "snapshot must be a "
                "UniversalQueueDeduplicationSnapshot."
            ),
            code="invalid_deduplication_snapshot",
            value=snapshot,
        )

    if snapshot.duplicate_present:
        return UniversalQueueDeduplicationDecision(
            queue_id=snapshot.queue_id,
            job_id=snapshot.job_id,
            existing_membership_count=(
                snapshot.existing_membership_count
            ),
            duplicate_present=True,
            matched_job_id=snapshot.job_id,
            admission=UniversalQueueDeduplicationAdmission.DENY,
            classification=(
                UniversalQueueDeduplicationClassification.DUPLICATE
            ),
            mutation_required=False,
            reason="job_already_represented_in_queue",
        )

    return UniversalQueueDeduplicationDecision(
        queue_id=snapshot.queue_id,
        job_id=snapshot.job_id,
        existing_membership_count=(
            snapshot.existing_membership_count
        ),
        duplicate_present=False,
        matched_job_id=None,
        admission=UniversalQueueDeduplicationAdmission.ALLOW,
        classification=(
            UniversalQueueDeduplicationClassification.UNIQUE
        ),
        mutation_required=False,
        reason="job_not_represented_in_queue",
    )


def explain_universal_queue_deduplication_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase": "3.1.14",
            "component": "Universal Queue Deduplication",
            "version": UNIVERSAL_QUEUE_DEDUPLICATION_VERSION,
            "snapshot_schema":
                UNIVERSAL_QUEUE_DEDUPLICATION_SNAPSHOT_SCHEMA_VERSION,
            "decision_schema":
                UNIVERSAL_QUEUE_DEDUPLICATION_DECISION_SCHEMA_VERSION,
            "scope": "LinkCraftor-wide",
            "canonical_queue_dedup_identity":
                "[queue_id, job_id]",
            "membership_rule": (
                "caller supplies the canonical candidate job_id "
                "and existing job_id membership evidence for "
                "one logical queue"
            ),
            "deduplication_rule": (
                "candidate job_id already present in existing_job_ids "
                "is DUPLICATE and DENY; absence is UNIQUE and ALLOW"
            ),
            "job_duplicate_boundary": (
                "Phase 2.1.11 Universal Job Duplicate Detection owns "
                "logical job equivalence using workspace_id + job_type "
                "with explicit idempotency_key or registered "
                "idempotency_fields"
            ),
            "job_duplicate_handling_boundary": (
                "Phase 2.1.12 Universal Job Duplicate Handling owns "
                "ALLOW_NEW versus REUSE_EXISTING"
            ),
            "idempotency_boundary": (
                "3.1.14 does not inspect, create, compare or derive "
                "idempotency_key values"
            ),
            "retry_requeue_boundary": (
                "Retry, Recovery and lifecycle authorities decide whether "
                "a historical canonical job_id may legitimately re-enter "
                "a queue; 3.1.14 only prevents duplicate current membership"
            ),
            "membership_evidence_rule": (
                "existing_job_ids is caller-supplied current logical "
                "membership evidence; 3.1.14 does not read live queues "
                "or persisted job status"
            ),
            "enforcement_rule": (
                "ALLOW and DENY are authoritative logical queue "
                "deduplication decisions; actual enqueue suppression "
                "is downstream"
            ),
            "prohibitions": (
                "does not detect logical Universal Job duplicates",
                "does not perform Universal Job Duplicate Handling",
                "does not inspect idempotency_key",
                "does not build duplicate signatures",
                "does not authorize retries",
                "does not authorize requeues",
                "does not read live queue state",
                "does not read persisted job status",
                "does not access orchestration",
                "does not access the Job Store",
                "does not mutate queues",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not lease jobs",
                "does not dispatch jobs",
                "does not requeue jobs",
                "does not suppress enqueue execution",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_QUEUE_DEDUPLICATION_VERSION",
    "UNIVERSAL_QUEUE_DEDUPLICATION_SNAPSHOT_SCHEMA_VERSION",
    "UNIVERSAL_QUEUE_DEDUPLICATION_DECISION_SCHEMA_VERSION",
    "UniversalQueueDeduplicationAdmission",
    "UniversalQueueDeduplicationClassification",
    "UniversalQueueDeduplicationError",
    "UniversalQueueDeduplicationSnapshot",
    "UniversalQueueDeduplicationDecision",
    "normalize_universal_queue_deduplication_queue_id",
    "normalize_universal_queue_deduplication_job_id",
    "normalize_universal_queue_existing_job_ids",
    "normalize_universal_queue_deduplication_admission",
    "normalize_universal_queue_deduplication_classification",
    "create_universal_queue_deduplication_snapshot",
    "evaluate_universal_queue_deduplication",
    "explain_universal_queue_deduplication_v1",
]
