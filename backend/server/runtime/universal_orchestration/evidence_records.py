from __future__ import annotations

import enum
import hashlib

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final, Mapping


UNIVERSAL_ORCHESTRATION_EVIDENCE_RECORDS_VERSION: Final[str] = (
    "universal_orchestration_evidence_records_v5.1.17"
)

UNIVERSAL_ORCHESTRATION_EVIDENCE_RECORD_SCHEMA_VERSION: Final[str] = (
    "universal_orchestration_evidence_record_schema_v1"
)

UNIVERSAL_ORCHESTRATION_EVIDENCE_HASH_ALGORITHM: Final[str] = (
    "sha256"
)


class UniversalOrchestrationEvidenceError(
    ValueError
):

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


class UniversalOrchestrationDecisionKind(
    str,
    enum.Enum,
):

    SUSPENSION_RESUME_ELIGIBILITY = (
        "suspension_resume_eligibility"
    )

    RECOVERY = (
        "recovery"
    )

    COMPLETION = (
        "completion"
    )

    CANCELLATION_TERMINATION = (
        "cancellation_termination"
    )


_DECISION_KIND_PHASES: Final[
    Mapping[
        UniversalOrchestrationDecisionKind,
        str,
    ]
] = MappingProxyType(
    {
        UniversalOrchestrationDecisionKind.SUSPENSION_RESUME_ELIGIBILITY:
            "5.1.12",

        UniversalOrchestrationDecisionKind.RECOVERY:
            "5.1.13",

        UniversalOrchestrationDecisionKind.COMPLETION:
            "5.1.15",

        UniversalOrchestrationDecisionKind.CANCELLATION_TERMINATION:
            "5.1.16",
    }
)


def _normalize_sha256(
    value: Any,
    *,
    field_name: str,
    code: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalOrchestrationEvidenceError(
            field_name
            + " must be a SHA-256 hexadecimal string.",
            code=code,
            value=value,
        )

    normalized = (
        value
        .strip()
        .upper()
    )

    if (
        len(
            normalized
        )
        != 64
        or
        any(
            character
            not in "0123456789ABCDEF"
            for character
            in normalized
        )
    ):

        raise UniversalOrchestrationEvidenceError(
            field_name
            + " must contain exactly 64 hexadecimal characters.",
            code=code,
            value=value,
        )

    return normalized


def _normalize_optional_sha256(
    value: Any,
    *,
    field_name: str,
    code: str,
) -> str | None:

    if value is None:

        return None

    return (
        _normalize_sha256(
            value,
            field_name=field_name,
            code=code,
        )
    )


def _normalize_decision_kind(
    value: Any,
) -> UniversalOrchestrationDecisionKind:

    if isinstance(
        value,
        UniversalOrchestrationDecisionKind,
    ):

        return value

    if isinstance(
        value,
        str,
    ):

        normalized = (
            value
            .strip()
            .lower()
        )

        try:

            return (
                UniversalOrchestrationDecisionKind(
                    normalized
                )
            )

        except ValueError:

            pass

    raise UniversalOrchestrationEvidenceError(
        "decision_kind is not a canonical orchestration decision kind.",
        code="invalid_evidence_decision_kind",
        value=value,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalOrchestrationDecisionEvidenceRecord:

    identity_fingerprint: str

    decision_kind: UniversalOrchestrationDecisionKind

    decision_id: str

    previous_record_id: str | None = None

    schema_version: str = (
        UNIVERSAL_ORCHESTRATION_EVIDENCE_RECORD_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "identity_fingerprint",
            _normalize_sha256(
                self.identity_fingerprint,
                field_name="identity_fingerprint",
                code="invalid_evidence_identity_fingerprint",
            ),
        )

        object.__setattr__(
            self,
            "decision_kind",
            _normalize_decision_kind(
                self.decision_kind
            ),
        )

        object.__setattr__(
            self,
            "decision_id",
            _normalize_sha256(
                self.decision_id,
                field_name="decision_id",
                code="invalid_evidence_decision_id",
            ),
        )

        object.__setattr__(
            self,
            "previous_record_id",
            _normalize_optional_sha256(
                self.previous_record_id,
                field_name="previous_record_id",
                code="invalid_evidence_previous_record_id",
            ),
        )

        if (
            self.schema_version
            !=
            UNIVERSAL_ORCHESTRATION_EVIDENCE_RECORD_SCHEMA_VERSION
        ):

            raise UniversalOrchestrationEvidenceError(
                "Invalid orchestration evidence schema_version.",
                code="invalid_evidence_schema_version",
                value=self.schema_version,
            )

    @property
    def source_phase(
        self,
    ) -> str:

        return (
            _DECISION_KIND_PHASES[
                self.decision_kind
            ]
        )

    @property
    def is_root_record(
        self,
    ) -> bool:

        return (
            self.previous_record_id
            is None
        )

    @property
    def evidence_record_id(
        self,
    ) -> str:

        predecessor = (
            self.previous_record_id
            if self.previous_record_id
            is not None
            else "ROOT"
        )

        material = "|".join(
            (
                "universal_orchestration_decision_evidence_record_v1",
                self.identity_fingerprint,
                self.decision_kind.value,
                self.decision_id,
                predecessor,
                self.schema_version,
            )
        )

        return hashlib.sha256(
            material.encode(
                "utf-8"
            )
        ).hexdigest().upper()

    @property
    def manifest(
        self,
    ) -> Mapping[
        str,
        Any,
    ]:

        return MappingProxyType(
            {
                "evidence_record_id":
                    self.evidence_record_id,

                "previous_record_id":
                    self.previous_record_id,

                "identity_fingerprint":
                    self.identity_fingerprint,

                "decision_kind":
                    self.decision_kind.value,

                "source_phase":
                    self.source_phase,

                "decision_id":
                    self.decision_id,

                "schema_version":
                    self.schema_version,
            }
        )


def create_universal_orchestration_decision_evidence_record(
    *,
    identity_fingerprint: Any,
    decision_kind: Any,
    decision_id: Any,
    previous_record_id: Any = None,
) -> UniversalOrchestrationDecisionEvidenceRecord:

    return (
        UniversalOrchestrationDecisionEvidenceRecord(
            identity_fingerprint=identity_fingerprint,
            decision_kind=decision_kind,
            decision_id=decision_id,
            previous_record_id=previous_record_id,
        )
    )


def validate_universal_orchestration_evidence_successor(
    *,
    previous_record: Any,
    next_record: Any,
) -> bool:

    if not isinstance(
        previous_record,
        UniversalOrchestrationDecisionEvidenceRecord,
    ):

        raise UniversalOrchestrationEvidenceError(
            (
                "previous_record must be a "
                "UniversalOrchestrationDecisionEvidenceRecord."
            ),
            code="invalid_previous_evidence_record",
            value=previous_record,
        )

    if not isinstance(
        next_record,
        UniversalOrchestrationDecisionEvidenceRecord,
    ):

        raise UniversalOrchestrationEvidenceError(
            (
                "next_record must be a "
                "UniversalOrchestrationDecisionEvidenceRecord."
            ),
            code="invalid_next_evidence_record",
            value=next_record,
        )

    if (
        previous_record.identity_fingerprint
        !=
        next_record.identity_fingerprint
    ):

        raise UniversalOrchestrationEvidenceError(
            (
                "Evidence successor records must belong "
                "to the same orchestration identity."
            ),
            code="evidence_successor_identity_mismatch",
            value=(
                previous_record.identity_fingerprint,
                next_record.identity_fingerprint,
            ),
        )

    if (
        next_record.previous_record_id
        !=
        previous_record.evidence_record_id
    ):

        raise UniversalOrchestrationEvidenceError(
            (
                "Evidence successor must reference the exact "
                "immediately preceding evidence_record_id."
            ),
            code="evidence_successor_link_mismatch",
            value=(
                previous_record.evidence_record_id,
                next_record.previous_record_id,
            ),
        )

    return True


def explain_universal_orchestration_evidence_records_v1(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "5.1.17",

            "component":
                "Universal Orchestration Evidence & Decision Records",

            "version":
                UNIVERSAL_ORCHESTRATION_EVIDENCE_RECORDS_VERSION,

            "schema_version":
                UNIVERSAL_ORCHESTRATION_EVIDENCE_RECORD_SCHEMA_VERSION,

            "stored_fields": (
                "identity_fingerprint",
                "decision_kind",
                "decision_id",
                "previous_record_id",
                "schema_version",
            ),

            "decision_kinds": tuple(
                item.value
                for item
                in UniversalOrchestrationDecisionKind
            ),

            "decision_authorities": (
                "5.1.12 suspension/resume eligibility",
                "5.1.13 recovery",
                "5.1.15 completion resolution",
                "5.1.16 cancellation/termination resolution",
            ),

            "decision_identity_rule": (
                "5.1.17 records canonical deterministic decision IDs "
                "already produced by frozen upstream decision authorities; "
                "it does not recompute those decisions."
            ),

            "state_persistence_boundary": (
                "5.1.14 stores authoritative orchestration state/progress "
                "evidence. 5.1.17 does not duplicate state_snapshot or "
                "progress_snapshot."
            ),

            "record_rule": (
                "Decision evidence records are immutable, deterministic "
                "and append-only through previous_record_id lineage."
            ),

            "ordering_rule": (
                "Canonical ordering is predecessor-based and does not "
                "depend on wall-clock timestamps."
            ),

            "audit_infrastructure_boundary": (
                "Existing Runtime Audit / persistence infrastructure may "
                "store or transport 5.1.17 records later; that infrastructure "
                "does not become the 5.1.17 semantic authority."
            ),

            "persistence_boundary": (
                "5.1.17 performs no physical persistence and defines "
                "no additional persistence backend or storage port."
            ),

            "prohibitions": (
                "does not recompute suspension/resume eligibility",
                "does not recompute recovery",
                "does not recompute completion",
                "does not recompute cancellation/termination",
                "does not transition orchestration state",
                "does not mutate jobs",
                "does not execute recovery",
                "does not execute cancellation",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not manipulate workers",
                "does not manipulate leases",
                "does not dispatch handlers",
                "does not execute jobs",
                "does not duplicate state_snapshot",
                "does not duplicate progress_snapshot",
                "does not invoke 5.1.14 persistence port",
                "does not access Runtime State Store",
                "does not import Runtime Audit infrastructure",
                "does not implement an audit-log backend",
                "does not define a second persistence port",
                "does not use wall clock",
                "does not generate timestamps",
                "does not perform filesystem I/O",
                "does not perform database I/O",
                "does not perform network I/O",
                "does not import Universal Coordination Framework",
                "does not invoke pipeline coordinators",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_ORCHESTRATION_EVIDENCE_RECORDS_VERSION",
    "UNIVERSAL_ORCHESTRATION_EVIDENCE_RECORD_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_EVIDENCE_HASH_ALGORITHM",
    "UniversalOrchestrationEvidenceError",
    "UniversalOrchestrationDecisionKind",
    "UniversalOrchestrationDecisionEvidenceRecord",
    "create_universal_orchestration_decision_evidence_record",
    "validate_universal_orchestration_evidence_successor",
    "explain_universal_orchestration_evidence_records_v1",
]
