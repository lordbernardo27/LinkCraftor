from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.universal_jobs.contract import (
    UniversalJobContractError,
    UniversalJobStatus,
)

from backend.server.runtime.universal_jobs.attempts import (
    UniversalJobAttemptsError,
    normalize_universal_job_attempts,
    normalize_universal_job_maximum_attempts,
)

from backend.server.runtime.universal_queue.creation import (
    UniversalQueueCreationError,
    normalize_universal_queue_id,
)


UNIVERSAL_DEAD_LETTER_QUEUES_VERSION = (
    "universal_dead_letter_queues_v3.1.8"
)

UNIVERSAL_DEAD_LETTER_EVIDENCE_SCHEMA_VERSION = (
    "universal_dead_letter_evidence_schema_v1"
)

UNIVERSAL_DEAD_LETTER_DECISION_SCHEMA_VERSION = (
    "universal_dead_letter_decision_schema_v1"
)

UNIVERSAL_DEAD_LETTER_RECORD_SCHEMA_VERSION = (
    "universal_dead_letter_record_schema_v1"
)


class UniversalDeadLetterQueueError(
    ValueError
):
    """
    Raised when Universal Dead Letter Queue evidence is invalid.
    """

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


def _normalize_required_text(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise UniversalDeadLetterQueueError(
            f"{field_name} must be a string.",
            code=(
                "invalid_"
                + field_name
                + "_type"
            ),
            value=value,
        )

    normalized = value.strip()

    if not normalized:

        raise UniversalDeadLetterQueueError(
            f"{field_name} must not be blank.",
            code=(
                "blank_"
                + field_name
            ),
            value=value,
        )

    return normalized


def _normalize_optional_text(
    value: Any,
    *,
    field_name: str,
) -> str | None:

    if value is None:
        return None

    return _normalize_required_text(
        value,
        field_name=field_name,
    )


def _freeze_json_value(
    value: Any,
    *,
    field_name: str,
) -> Any:

    if value is None:
        return None

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return value

    if isinstance(
        value,
        Mapping,
    ):

        frozen = {}

        for key, item in value.items():

            if not isinstance(
                key,
                str,
            ):
                raise UniversalDeadLetterQueueError(
                    (
                        field_name
                        + " mapping keys must be strings."
                    ),
                    code="invalid_error_details_key",
                    value=key,
                )

            frozen[
                key
            ] = _freeze_json_value(
                item,
                field_name=field_name,
            )

        return MappingProxyType(
            frozen
        )

    if isinstance(
        value,
        (
            list,
            tuple,
        ),
    ):

        return tuple(
            _freeze_json_value(
                item,
                field_name=field_name,
            )
            for item in value
        )

    raise UniversalDeadLetterQueueError(
        (
            field_name
            + " must contain JSON-compatible values."
        ),
        code="invalid_error_details_value",
        value=value,
    )


def _thaw_json_value(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):

        return {
            str(key):
                _thaw_json_value(
                    item
                )
            for key, item
            in value.items()
        }

    if isinstance(
        value,
        tuple,
    ):

        return [
            _thaw_json_value(
                item
            )
            for item in value
        ]

    return value


def normalize_universal_dead_letter_job_id(
    value: Any,
) -> str:

    return _normalize_required_text(
        value,
        field_name="job_id",
    )


def normalize_universal_dead_letter_queue_id(
    value: Any,
) -> str:

    try:

        return normalize_universal_queue_id(
            value
        )

    except UniversalQueueCreationError as exc:

        raise UniversalDeadLetterQueueError(
            "Invalid canonical Universal Queue queue_id.",
            code="invalid_dead_letter_queue_id",
            value=value,
        ) from exc


def normalize_universal_dead_letter_partition_id(
    value: Any,
) -> str | None:

    return _normalize_optional_text(
        value,
        field_name="partition_id",
    )


def normalize_universal_dead_letter_status(
    value: Any,
) -> UniversalJobStatus:

    try:

        return UniversalJobStatus.coerce(
            value
        )

    except UniversalJobContractError as exc:

        raise UniversalDeadLetterQueueError(
            "Invalid Universal Job status.",
            code="invalid_dead_letter_status",
            value=value,
        ) from exc


def normalize_universal_dead_letter_attempts(
    value: Any,
) -> int:

    try:

        return normalize_universal_job_attempts(
            value
        )

    except UniversalJobAttemptsError as exc:

        raise UniversalDeadLetterQueueError(
            "Invalid attempts evidence.",
            code="invalid_dead_letter_attempts",
            value=value,
        ) from exc


def normalize_universal_dead_letter_maximum_attempts(
    value: Any,
) -> int:
    """
    Normalize explicit maximum-attempt evidence for a DLQ record.

    Universal Job Attempts may support broader/default semantics,
    but Phase 3.1.8 requires the retry ceiling to be explicitly
    present as historical dead-letter evidence.
    """

    if value is None:

        raise UniversalDeadLetterQueueError(
            (
                "maximum_attempts evidence must be "
                "explicitly supplied."
            ),
            code="missing_dead_letter_maximum_attempts",
            value=value,
        )

    try:

        return normalize_universal_job_maximum_attempts(
            value
        )

    except UniversalJobAttemptsError as exc:

        raise UniversalDeadLetterQueueError(
            "Invalid maximum_attempts evidence.",
            code="invalid_dead_letter_maximum_attempts",
            value=value,
        ) from exc


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalDeadLetterEvidence:
    """
    Caller-supplied dead-letter eligibility and failure evidence.

    Dead Letter Queues does not determine retryability.
    """

    job_id: str
    source_status: UniversalJobStatus | str
    queue_id: str
    partition_id: str | None
    attempts: int
    maximum_attempts: int
    dead_letter_eligible: bool
    eligibility_basis: str
    dead_letter_reason: str
    error_code: str | None = None
    error_message: str | None = None
    error_details: Any = None
    schema_version: str = (
        UNIVERSAL_DEAD_LETTER_EVIDENCE_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        set_(
            self,
            "job_id",
            normalize_universal_dead_letter_job_id(
                self.job_id
            ),
        )

        set_(
            self,
            "source_status",
            normalize_universal_dead_letter_status(
                self.source_status
            ),
        )

        set_(
            self,
            "queue_id",
            normalize_universal_dead_letter_queue_id(
                self.queue_id
            ),
        )

        set_(
            self,
            "partition_id",
            normalize_universal_dead_letter_partition_id(
                self.partition_id
            ),
        )

        normalized_attempts = (
            normalize_universal_dead_letter_attempts(
                self.attempts
            )
        )

        normalized_maximum = (
            normalize_universal_dead_letter_maximum_attempts(
                self.maximum_attempts
            )
        )

        if (
            normalized_attempts
            > normalized_maximum
        ):
            raise UniversalDeadLetterQueueError(
                (
                    "attempts must not exceed "
                    "maximum_attempts."
                ),
                code="dead_letter_attempts_exceed_maximum",
                value={
                    "attempts":
                        normalized_attempts,

                    "maximum_attempts":
                        normalized_maximum,
                },
            )

        set_(
            self,
            "attempts",
            normalized_attempts,
        )

        set_(
            self,
            "maximum_attempts",
            normalized_maximum,
        )

        if not isinstance(
            self.dead_letter_eligible,
            bool,
        ):
            raise UniversalDeadLetterQueueError(
                "dead_letter_eligible must be bool.",
                code="invalid_dead_letter_eligible_flag",
                value=self.dead_letter_eligible,
            )

        set_(
            self,
            "eligibility_basis",
            _normalize_required_text(
                self.eligibility_basis,
                field_name="eligibility_basis",
            ),
        )

        set_(
            self,
            "dead_letter_reason",
            _normalize_required_text(
                self.dead_letter_reason,
                field_name="dead_letter_reason",
            ),
        )

        set_(
            self,
            "error_code",
            _normalize_optional_text(
                self.error_code,
                field_name="error_code",
            ),
        )

        set_(
            self,
            "error_message",
            _normalize_optional_text(
                self.error_message,
                field_name="error_message",
            ),
        )

        set_(
            self,
            "error_details",
            _freeze_json_value(
                self.error_details,
                field_name="error_details",
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_DEAD_LETTER_EVIDENCE_SCHEMA_VERSION
        ):
            raise UniversalDeadLetterQueueError(
                "Invalid dead-letter evidence schema_version.",
                code="invalid_dead_letter_evidence_schema_version",
                value=self.schema_version,
            )

    @property
    def retry_exhausted(
        self,
    ) -> bool:

        return (
            self.attempts
            >= self.maximum_attempts
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "job_id":
                self.job_id,

            "source_status":
                self.source_status.value,

            "queue_id":
                self.queue_id,

            "partition_id":
                self.partition_id,

            "attempts":
                self.attempts,

            "maximum_attempts":
                self.maximum_attempts,

            "retry_exhausted":
                self.retry_exhausted,

            "dead_letter_eligible":
                self.dead_letter_eligible,

            "eligibility_basis":
                self.eligibility_basis,

            "dead_letter_reason":
                self.dead_letter_reason,

            "error_code":
                self.error_code,

            "error_message":
                self.error_message,

            "error_details":
                _thaw_json_value(
                    self.error_details
                ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalDeadLetterRecord:
    """
    Immutable logical Universal Dead Letter record.

    This is not physical DLQ storage.
    """

    job_id: str
    source_status: UniversalJobStatus | str
    target_status: UniversalJobStatus | str
    queue_id: str
    partition_id: str | None
    attempts: int
    maximum_attempts: int
    eligibility_basis: str
    dead_letter_reason: str
    error_code: str | None
    error_message: str | None
    error_details: Any
    schema_version: str = (
        UNIVERSAL_DEAD_LETTER_RECORD_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        set_(
            self,
            "job_id",
            normalize_universal_dead_letter_job_id(
                self.job_id
            ),
        )

        set_(
            self,
            "source_status",
            normalize_universal_dead_letter_status(
                self.source_status
            ),
        )

        target_status = (
            normalize_universal_dead_letter_status(
                self.target_status
            )
        )

        if (
            target_status
            is not UniversalJobStatus.DEAD_LETTER
        ):
            raise UniversalDeadLetterQueueError(
                (
                    "Dead-letter record target_status "
                    "must be DEAD_LETTER."
                ),
                code="invalid_dead_letter_target_status",
                value=target_status.value,
            )

        set_(
            self,
            "target_status",
            target_status,
        )

        set_(
            self,
            "queue_id",
            normalize_universal_dead_letter_queue_id(
                self.queue_id
            ),
        )

        set_(
            self,
            "partition_id",
            normalize_universal_dead_letter_partition_id(
                self.partition_id
            ),
        )

        normalized_attempts = (
            normalize_universal_dead_letter_attempts(
                self.attempts
            )
        )

        normalized_maximum = (
            normalize_universal_dead_letter_maximum_attempts(
                self.maximum_attempts
            )
        )

        if (
            normalized_attempts
            > normalized_maximum
        ):
            raise UniversalDeadLetterQueueError(
                (
                    "attempts must not exceed "
                    "maximum_attempts."
                ),
                code="dead_letter_attempts_exceed_maximum",
            )

        set_(
            self,
            "attempts",
            normalized_attempts,
        )

        set_(
            self,
            "maximum_attempts",
            normalized_maximum,
        )

        set_(
            self,
            "eligibility_basis",
            _normalize_required_text(
                self.eligibility_basis,
                field_name="eligibility_basis",
            ),
        )

        set_(
            self,
            "dead_letter_reason",
            _normalize_required_text(
                self.dead_letter_reason,
                field_name="dead_letter_reason",
            ),
        )

        set_(
            self,
            "error_code",
            _normalize_optional_text(
                self.error_code,
                field_name="error_code",
            ),
        )

        set_(
            self,
            "error_message",
            _normalize_optional_text(
                self.error_message,
                field_name="error_message",
            ),
        )

        set_(
            self,
            "error_details",
            _freeze_json_value(
                self.error_details,
                field_name="error_details",
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_DEAD_LETTER_RECORD_SCHEMA_VERSION
        ):
            raise UniversalDeadLetterQueueError(
                "Invalid dead-letter record schema_version.",
                code="invalid_dead_letter_record_schema_version",
                value=self.schema_version,
            )

    @property
    def retry_exhausted(
        self,
    ) -> bool:

        return (
            self.attempts
            >= self.maximum_attempts
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "job_id":
                self.job_id,

            "source_status":
                self.source_status.value,

            "target_status":
                self.target_status.value,

            "queue_id":
                self.queue_id,

            "partition_id":
                self.partition_id,

            "attempts":
                self.attempts,

            "maximum_attempts":
                self.maximum_attempts,

            "retry_exhausted":
                self.retry_exhausted,

            "eligibility_basis":
                self.eligibility_basis,

            "dead_letter_reason":
                self.dead_letter_reason,

            "error_code":
                self.error_code,

            "error_message":
                self.error_message,

            "error_details":
                _thaw_json_value(
                    self.error_details
                ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalDeadLetterDecision:
    """
    Immutable 3.1.8 logical dead-letter decision.
    """

    job_id: str
    source_status: UniversalJobStatus | str
    queue_id: str
    partition_id: str | None
    dead_letter_required: bool
    target_status: UniversalJobStatus | str | None
    action: str
    mutation_required: bool
    record: UniversalDeadLetterRecord | None
    reason: str
    schema_version: str = (
        UNIVERSAL_DEAD_LETTER_DECISION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        set_(
            self,
            "job_id",
            normalize_universal_dead_letter_job_id(
                self.job_id
            ),
        )

        set_(
            self,
            "source_status",
            normalize_universal_dead_letter_status(
                self.source_status
            ),
        )

        set_(
            self,
            "queue_id",
            normalize_universal_dead_letter_queue_id(
                self.queue_id
            ),
        )

        set_(
            self,
            "partition_id",
            normalize_universal_dead_letter_partition_id(
                self.partition_id
            ),
        )

        if not isinstance(
            self.dead_letter_required,
            bool,
        ):
            raise UniversalDeadLetterQueueError(
                "dead_letter_required must be bool.",
                code="invalid_dead_letter_required_flag",
                value=self.dead_letter_required,
            )

        if not isinstance(
            self.mutation_required,
            bool,
        ):
            raise UniversalDeadLetterQueueError(
                "mutation_required must be bool.",
                code="invalid_dead_letter_mutation_flag",
                value=self.mutation_required,
            )

        if self.mutation_required is not False:

            raise UniversalDeadLetterQueueError(
                (
                    "Phase 3.1.8 decisions must not "
                    "perform job mutation."
                ),
                code="dead_letter_mutation_not_owned",
                value=self.mutation_required,
            )

        set_(
            self,
            "action",
            _normalize_required_text(
                self.action,
                field_name="action",
            ),
        )

        set_(
            self,
            "reason",
            _normalize_required_text(
                self.reason,
                field_name="reason",
            ),
        )

        if self.target_status is None:

            normalized_target = None

        else:

            normalized_target = (
                normalize_universal_dead_letter_status(
                    self.target_status
                )
            )

            if (
                normalized_target
                is not UniversalJobStatus.DEAD_LETTER
            ):
                raise UniversalDeadLetterQueueError(
                    (
                        "Dead-letter decision target_status "
                        "must be DEAD_LETTER or None."
                    ),
                    code="invalid_dead_letter_decision_target",
                    value=normalized_target.value,
                )

        set_(
            self,
            "target_status",
            normalized_target,
        )

        if self.dead_letter_required:

            if (
                self.target_status
                is not UniversalJobStatus.DEAD_LETTER
            ):
                raise UniversalDeadLetterQueueError(
                    "Eligible decision must target DEAD_LETTER.",
                    code="missing_dead_letter_target",
                )

            if not isinstance(
                self.record,
                UniversalDeadLetterRecord,
            ):
                raise UniversalDeadLetterQueueError(
                    "Eligible decision must contain a dead-letter record.",
                    code="missing_dead_letter_record",
                )

            if self.action != "create_logical_dead_letter_record":

                raise UniversalDeadLetterQueueError(
                    "Invalid eligible dead-letter action.",
                    code="invalid_dead_letter_action",
                    value=self.action,
                )

        else:

            if self.target_status is not None:

                raise UniversalDeadLetterQueueError(
                    (
                        "Ineligible decision must not "
                        "declare target_status."
                    ),
                    code="unexpected_dead_letter_target",
                )

            if self.record is not None:

                raise UniversalDeadLetterQueueError(
                    (
                        "Ineligible decision must not "
                        "contain a dead-letter record."
                    ),
                    code="unexpected_dead_letter_record",
                )

            if self.action != "no_dead_letter_action":

                raise UniversalDeadLetterQueueError(
                    "Invalid ineligible dead-letter action.",
                    code="invalid_no_dead_letter_action",
                    value=self.action,
                )

        if (
            self.schema_version
            != UNIVERSAL_DEAD_LETTER_DECISION_SCHEMA_VERSION
        ):
            raise UniversalDeadLetterQueueError(
                "Invalid dead-letter decision schema_version.",
                code="invalid_dead_letter_decision_schema_version",
                value=self.schema_version,
            )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "job_id":
                self.job_id,

            "source_status":
                self.source_status.value,

            "queue_id":
                self.queue_id,

            "partition_id":
                self.partition_id,

            "dead_letter_required":
                self.dead_letter_required,

            "target_status":
                (
                    None
                    if self.target_status is None
                    else self.target_status.value
                ),

            "action":
                self.action,

            "mutation_required":
                self.mutation_required,

            "record":
                (
                    None
                    if self.record is None
                    else self.record.to_dict()
                ),

            "reason":
                self.reason,
        }


def create_universal_dead_letter_evidence(
    *,
    job_id: str,
    source_status: UniversalJobStatus | str,
    queue_id: str,
    partition_id: str | None = None,
    attempts: int,
    maximum_attempts: int,
    dead_letter_eligible: bool,
    eligibility_basis: str,
    dead_letter_reason: str,
    error_code: str | None = None,
    error_message: str | None = None,
    error_details: Any = None,
) -> UniversalDeadLetterEvidence:

    return UniversalDeadLetterEvidence(
        job_id=job_id,
        source_status=source_status,
        queue_id=queue_id,
        partition_id=partition_id,
        attempts=attempts,
        maximum_attempts=maximum_attempts,
        dead_letter_eligible=dead_letter_eligible,
        eligibility_basis=eligibility_basis,
        dead_letter_reason=dead_letter_reason,
        error_code=error_code,
        error_message=error_message,
        error_details=error_details,
    )


def evaluate_universal_dead_letter(
    *,
    evidence: UniversalDeadLetterEvidence,
) -> UniversalDeadLetterDecision:
    """
    Convert caller-supplied eligibility evidence into a logical
    dead-letter decision.

    This function deliberately does not decide retryability and
    does not mutate or persist the Universal Job.
    """

    if not isinstance(
        evidence,
        UniversalDeadLetterEvidence,
    ):
        raise UniversalDeadLetterQueueError(
            (
                "evidence must be a "
                "UniversalDeadLetterEvidence instance."
            ),
            code="invalid_dead_letter_evidence",
            value=evidence,
        )

    if not evidence.dead_letter_eligible:

        return UniversalDeadLetterDecision(
            job_id=evidence.job_id,
            source_status=evidence.source_status,
            queue_id=evidence.queue_id,
            partition_id=evidence.partition_id,
            dead_letter_required=False,
            target_status=None,
            action="no_dead_letter_action",
            mutation_required=False,
            record=None,
            reason=(
                "Caller-supplied eligibility does not authorize "
                "logical dead-letter entry."
            ),
        )

    record = UniversalDeadLetterRecord(
        job_id=evidence.job_id,
        source_status=evidence.source_status,
        target_status=UniversalJobStatus.DEAD_LETTER,
        queue_id=evidence.queue_id,
        partition_id=evidence.partition_id,
        attempts=evidence.attempts,
        maximum_attempts=evidence.maximum_attempts,
        eligibility_basis=evidence.eligibility_basis,
        dead_letter_reason=evidence.dead_letter_reason,
        error_code=evidence.error_code,
        error_message=evidence.error_message,
        error_details=evidence.error_details,
    )

    return UniversalDeadLetterDecision(
        job_id=evidence.job_id,
        source_status=evidence.source_status,
        queue_id=evidence.queue_id,
        partition_id=evidence.partition_id,
        dead_letter_required=True,
        target_status=UniversalJobStatus.DEAD_LETTER,
        action="create_logical_dead_letter_record",
        mutation_required=False,
        record=record,
        reason=(
            "Caller-supplied dead-letter eligibility authorizes "
            "logical DEAD_LETTER membership."
        ),
    )


def explain_universal_dead_letter_queues_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "3.1.8",

            "component":
                "Universal Dead Letter Queues",

            "version":
                UNIVERSAL_DEAD_LETTER_QUEUES_VERSION,

            "evidence_schema":
                UNIVERSAL_DEAD_LETTER_EVIDENCE_SCHEMA_VERSION,

            "decision_schema":
                UNIVERSAL_DEAD_LETTER_DECISION_SCHEMA_VERSION,

            "record_schema":
                UNIVERSAL_DEAD_LETTER_RECORD_SCHEMA_VERSION,

            "scope":
                "LinkCraftor-wide",

            "canonical_target_status":
                "dead_letter",

            "eligibility_rule": (
                "dead_letter_eligible is explicit caller-supplied "
                "eligibility; 3.1.8 does not decide retryability"
            ),

            "attempts_rule": (
                "attempts and maximum_attempts are preserved as "
                "evidence and are never incremented by 3.1.8"
            ),

            "retry_exhaustion_rule": (
                "attempt exhaustion may support caller eligibility "
                "but is not the only valid dead-letter basis"
            ),

            "identity_rule": (
                "job_id, source queue_id and optional partition_id "
                "are preserved for provenance"
            ),

            "failure_evidence_rule": (
                "eligibility basis, dead-letter reason, error_code, "
                "error_message and error_details are preserved"
            ),

            "logical_record_rule": (
                "the dead-letter record is logical evidence and not "
                "physical broker or filesystem storage"
            ),

            "recovery_relationship": (
                "3.1.7 delegates DEAD_LETTER handling to 3.1.8"
            ),

            "redrive_boundary": (
                "redrive, replay and dead-letter recovery are "
                "outside the initial 3.1.8 authority"
            ),

            "persistence_boundary": (
                "job-status transition and physical dead-letter "
                "persistence belong to later lifecycle/persistence "
                "authorities"
            ),

            "prohibitions": (
                "does not create Universal Jobs",
                "does not mutate Universal Jobs",
                "does not mutate job status",
                "does not transition jobs to DEAD_LETTER",
                "does not increment attempts",
                "does not decide retryability",
                "does not calculate retry backoff",
                "does not schedule retries",
                "does not requeue jobs",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not select workers",
                "does not read live queue state",
                "does not access the Job Store",
                "does not access orchestration",
                "does not access Runtime State Store",
                "does not physically move jobs",
                "does not create filesystem dead-letter queues",
                "does not create Redis dead-letter queues",
                "does not create cloud dead-letter queues",
                "does not create Kafka dead-letter topics",
                "does not perform redrive",
                "does not replay dead-letter jobs",
                "does not recover dead-letter jobs",
                "does not delete dead-letter records",
                "does not apply dead-letter retention",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_DEAD_LETTER_QUEUES_VERSION",
    "UNIVERSAL_DEAD_LETTER_EVIDENCE_SCHEMA_VERSION",
    "UNIVERSAL_DEAD_LETTER_DECISION_SCHEMA_VERSION",
    "UNIVERSAL_DEAD_LETTER_RECORD_SCHEMA_VERSION",
    "UniversalDeadLetterQueueError",
    "UniversalDeadLetterEvidence",
    "UniversalDeadLetterRecord",
    "UniversalDeadLetterDecision",
    "normalize_universal_dead_letter_job_id",
    "normalize_universal_dead_letter_queue_id",
    "normalize_universal_dead_letter_partition_id",
    "normalize_universal_dead_letter_status",
    "normalize_universal_dead_letter_attempts",
    "normalize_universal_dead_letter_maximum_attempts",
    "create_universal_dead_letter_evidence",
    "evaluate_universal_dead_letter",
    "explain_universal_dead_letter_queues_v1",
]
