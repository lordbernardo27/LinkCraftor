from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from backend.server.runtime.universal_jobs.duplicate_detection import (
    UniversalJobDuplicateDetectionMethod,
    UniversalJobDuplicateDetectionResult,
    UniversalJobDuplicateDetectionStatus,
)


UNIVERSAL_JOB_DUPLICATE_HANDLING_VERSION = (
    "universal_job_duplicate_handling_v2.1.12"
)

UNIVERSAL_JOB_DUPLICATE_HANDLING_SCHEMA_VERSION = (
    "universal_job_duplicate_handling_schema_v1"
)


class UniversalJobDuplicateHandlingError(
    ValueError
):
    """Raised when a duplicate-handling decision cannot be formed."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "invalid_duplicate_handling_input",
    ) -> None:

        super().__init__(
            message
        )

        self.code = str(
            code
        )


class UniversalJobDuplicateHandlingAction(
    str,
    Enum,
):
    ALLOW_NEW = "allow_new"
    REUSE_EXISTING = "reuse_existing"


def _normalize_existing_job_id(
    value: Any,
) -> Optional[str]:

    if value is None:
        return None

    if not isinstance(
        value,
        str,
    ):
        raise UniversalJobDuplicateHandlingError(
            (
                "existing_job_id must be "
                "a string or None."
            ),
            code="invalid_existing_job_id",
        )

    normalized = value.strip()

    return (
        normalized
        if normalized
        else None
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalJobDuplicateHandlingDecision:
    action: UniversalJobDuplicateHandlingAction
    detection_status: UniversalJobDuplicateDetectionStatus
    detection_method: UniversalJobDuplicateDetectionMethod
    existing_job_id: Optional[str]
    create_new: bool
    reuse_existing: bool
    reason: str

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version": (
                UNIVERSAL_JOB_DUPLICATE_HANDLING_SCHEMA_VERSION
            ),
            "action":
                self.action.value,
            "detection_status":
                self.detection_status.value,
            "detection_method":
                self.detection_method.value,
            "existing_job_id":
                self.existing_job_id,
            "create_new":
                self.create_new,
            "reuse_existing":
                self.reuse_existing,
            "reason":
                self.reason,
        }


def decide_universal_job_duplicate_handling(
    detection: UniversalJobDuplicateDetectionResult,
    *,
    existing_job_id: Any = None,
) -> UniversalJobDuplicateHandlingDecision:
    """
    Convert a frozen Phase 2.1.11 duplicate-detection fact into
    a pure Phase 2.1.12 handling decision.

    This function does not look up, create, persist, enqueue,
    suppress, reject, merge, cancel, delete, or mutate jobs.
    """

    if not isinstance(
        detection,
        UniversalJobDuplicateDetectionResult,
    ):
        raise UniversalJobDuplicateHandlingError(
            (
                "detection must be "
                "UniversalJobDuplicateDetectionResult."
            ),
            code="invalid_duplicate_detection_result",
        )

    canonical_existing_job_id = (
        _normalize_existing_job_id(
            existing_job_id
        )
    )

    if (
        detection.status
        is UniversalJobDuplicateDetectionStatus.DUPLICATE
    ):

        if not detection.comparable:
            raise UniversalJobDuplicateHandlingError(
                (
                    "A DUPLICATE detection result "
                    "must be comparable."
                ),
                code="inconsistent_duplicate_detection_result",
            )

        if not detection.is_duplicate:
            raise UniversalJobDuplicateHandlingError(
                (
                    "A DUPLICATE detection result "
                    "must have is_duplicate=True."
                ),
                code="inconsistent_duplicate_detection_result",
            )

        if canonical_existing_job_id is None:
            raise UniversalJobDuplicateHandlingError(
                (
                    "existing_job_id is required "
                    "when a logical duplicate is detected."
                ),
                code="missing_existing_job_id",
            )

        return UniversalJobDuplicateHandlingDecision(
            action=(
                UniversalJobDuplicateHandlingAction.REUSE_EXISTING
            ),
            detection_status=(
                detection.status
            ),
            detection_method=(
                detection.method
            ),
            existing_job_id=(
                canonical_existing_job_id
            ),
            create_new=False,
            reuse_existing=True,
            reason=(
                "A logical duplicate was detected; "
                "reuse the existing canonical job."
            ),
        )

    if (
        detection.status
        is UniversalJobDuplicateDetectionStatus.NOT_DUPLICATE
    ):

        if detection.is_duplicate:
            raise UniversalJobDuplicateHandlingError(
                (
                    "A NOT_DUPLICATE detection result "
                    "must have is_duplicate=False."
                ),
                code="inconsistent_duplicate_detection_result",
            )

        return UniversalJobDuplicateHandlingDecision(
            action=(
                UniversalJobDuplicateHandlingAction.ALLOW_NEW
            ),
            detection_status=(
                detection.status
            ),
            detection_method=(
                detection.method
            ),
            existing_job_id=None,
            create_new=True,
            reuse_existing=False,
            reason=(
                "The candidate is not a logical duplicate; "
                "normal job creation may proceed."
            ),
        )

    if (
        detection.status
        is UniversalJobDuplicateDetectionStatus.NOT_DETECTABLE
    ):

        if detection.comparable:
            raise UniversalJobDuplicateHandlingError(
                (
                    "A NOT_DETECTABLE detection result "
                    "must have comparable=False."
                ),
                code="inconsistent_duplicate_detection_result",
            )

        if detection.is_duplicate:
            raise UniversalJobDuplicateHandlingError(
                (
                    "A NOT_DETECTABLE detection result "
                    "must have is_duplicate=False."
                ),
                code="inconsistent_duplicate_detection_result",
            )

        return UniversalJobDuplicateHandlingDecision(
            action=(
                UniversalJobDuplicateHandlingAction.ALLOW_NEW
            ),
            detection_status=(
                detection.status
            ),
            detection_method=(
                detection.method
            ),
            existing_job_id=None,
            create_new=True,
            reuse_existing=False,
            reason=(
                "Duplicate status is not detectable from the "
                "available signals; normal job creation may proceed."
            ),
        )

    raise UniversalJobDuplicateHandlingError(
        (
            "Unsupported duplicate detection status: "
            + str(
                detection.status
            )
        ),
        code="unsupported_duplicate_detection_status",
    )


def explain_universal_job_duplicate_handling_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "2.1.12",
            "component":
                "Universal Job Duplicate Handling",
            "version":
                UNIVERSAL_JOB_DUPLICATE_HANDLING_VERSION,
            "schema_version":
                UNIVERSAL_JOB_DUPLICATE_HANDLING_SCHEMA_VERSION,
            "input_authority":
                "Phase 2.1.11 Universal Job Duplicate Detection",
            "actions": (
                "allow_new",
                "reuse_existing",
            ),
            "policy": (
                (
                    "DUPLICATE -> REUSE_EXISTING "
                    "with an existing canonical job identity"
                ),
                (
                    "NOT_DUPLICATE -> ALLOW_NEW"
                ),
                (
                    "NOT_DETECTABLE -> ALLOW_NEW"
                ),
            ),
            "duplicate_signal_policy": (
                (
                    "explicit idempotency-key duplicates and "
                    "derived idempotency-field duplicates use "
                    "the same REUSE_EXISTING handling action"
                ),
            ),
            "prohibitions": (
                "does not search a queue",
                "does not search a job store",
                "does not find the existing job",
                "does not create a job",
                "does not persist a job",
                "does not enqueue a job",
                "does not execute job reuse",
                "does not reject a duplicate",
                "does not merge jobs",
                "does not cancel jobs",
                "does not delete jobs",
                "does not mutate jobs",
                "does not perform orchestration",
                "does not perform I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_JOB_DUPLICATE_HANDLING_VERSION",
    "UNIVERSAL_JOB_DUPLICATE_HANDLING_SCHEMA_VERSION",
    "UniversalJobDuplicateHandlingError",
    "UniversalJobDuplicateHandlingAction",
    "UniversalJobDuplicateHandlingDecision",
    "decide_universal_job_duplicate_handling",
    "explain_universal_job_duplicate_handling_v1",
]
