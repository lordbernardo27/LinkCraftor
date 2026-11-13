"""
LinkCraftor — Universal Coordination Framework

Phase 7.7 — Skip Semantics

Resolves whether a deliberate stage skip is authorized by advanced
orchestration and whether that authorized skip may waive a downstream
prerequisite.

Base authority remains unchanged:
- Phase 4 treats ordinary SKIPPED as prerequisite-unsatisfied.
- Phase 6.1 treats SKIPPED as no normal downstream handoff.

Phase 7.7 adds explicit advanced evidence:
- Optional Stage OMIT may authorize skip.
- Conditional Execution EXCLUDED may authorize skip.
- An authorized skip is NOT a completed stage.
- An authorized skip may satisfy the effective advanced prerequisite
  through an explicit waiver.
- An unauthorized skip remains prerequisite-unsatisfied.

No Phase 4 or Phase 6 production source is mutated.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Final

from backend.server.coordination.advanced_orchestration.optional_stages import (
    OPTIONAL_STAGES_VERSION,
    OptionalStageEvaluation,
)

from backend.server.coordination.advanced_orchestration.conditional_execution import (
    CONDITIONAL_EXECUTION_VERSION,
    BranchDisposition,
    ConditionalExecutionDecision,
)


SKIP_SEMANTICS_VERSION: Final[str] = (
    "skip_semantics_v7.7.0"
)

SKIP_SEMANTICS_SCHEMA_VERSION: Final[str] = (
    "skip_semantics_schema_v1"
)


class SkipSemanticsError(ValueError):
    pass


class SkipAuthorization(str, Enum):
    UNAUTHORIZED = "unauthorized"
    OPTIONAL_OMISSION = "optional_omission"
    CONDITIONAL_EXCLUSION = "conditional_exclusion"
    OPTIONAL_AND_CONDITIONAL = "optional_and_conditional"


@dataclass(frozen=True, slots=True)
class SkipSemanticsResolution:

    workflow_id: str
    stage_id: str

    authorization: SkipAuthorization

    skip_authorized: bool

    base_prerequisite_satisfied: bool
    effective_prerequisite_satisfied: bool

    prerequisite_waived: bool

    stage_completed: bool
    normal_handoff_allowed: bool

    optional_omission: bool
    conditional_exclusion: bool

    optional_stages_version: str | None
    conditional_execution_version: str | None

    skip_semantics_version: str = SKIP_SEMANTICS_VERSION
    schema_version: str = SKIP_SEMANTICS_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:

        return {
            "workflow_id":
                self.workflow_id,

            "stage_id":
                self.stage_id,

            "authorization":
                self.authorization.value,

            "skip_authorized":
                self.skip_authorized,

            "base_prerequisite_satisfied":
                self.base_prerequisite_satisfied,

            "effective_prerequisite_satisfied":
                self.effective_prerequisite_satisfied,

            "prerequisite_waived":
                self.prerequisite_waived,

            "stage_completed":
                self.stage_completed,

            "normal_handoff_allowed":
                self.normal_handoff_allowed,

            "optional_omission":
                self.optional_omission,

            "conditional_exclusion":
                self.conditional_exclusion,

            "optional_stages_version":
                self.optional_stages_version,

            "conditional_execution_version":
                self.conditional_execution_version,

            "skip_semantics_version":
                self.skip_semantics_version,

            "schema_version":
                self.schema_version,
        }


def resolve_skip_semantics(
    *,
    workflow_id: str,
    stage_id: str,
    optional_evaluation: OptionalStageEvaluation | None = None,
    conditional_decision: ConditionalExecutionDecision | None = None,
) -> SkipSemanticsResolution:

    if not isinstance(workflow_id, str) or not workflow_id.strip():
        raise SkipSemanticsError(
            "workflow_id must be a non-empty string"
        )

    workflow_id = workflow_id.strip()

    if not isinstance(stage_id, str) or not stage_id.strip():
        raise SkipSemanticsError(
            "stage_id must be a non-empty string"
        )

    stage_id = stage_id.strip()

    optional_omission = False
    conditional_exclusion = False

    optional_version = None
    conditional_version = None

    if optional_evaluation is not None:

        if not isinstance(
            optional_evaluation,
            OptionalStageEvaluation,
        ):
            raise SkipSemanticsError(
                "optional_evaluation must be OptionalStageEvaluation"
            )

        if (
            optional_evaluation.optional_stages_version
            != OPTIONAL_STAGES_VERSION
        ):
            raise SkipSemanticsError(
                "optional-stage version mismatch"
            )

        if optional_evaluation.workflow_id != workflow_id:
            raise SkipSemanticsError(
                "optional-stage workflow identity mismatch"
            )

        optional_omission = (
            stage_id
            in optional_evaluation.omitted_optional_stage_ids
        )

        optional_version = (
            optional_evaluation.optional_stages_version
        )

    if conditional_decision is not None:

        if not isinstance(
            conditional_decision,
            ConditionalExecutionDecision,
        ):
            raise SkipSemanticsError(
                "conditional_decision must be ConditionalExecutionDecision"
            )

        if (
            conditional_decision.conditional_execution_version
            != CONDITIONAL_EXECUTION_VERSION
        ):
            raise SkipSemanticsError(
                "conditional-execution version mismatch"
            )

        if conditional_decision.workflow_id != workflow_id:
            raise SkipSemanticsError(
                "conditional workflow identity mismatch"
            )

        dispositions = dict(
            conditional_decision.branch_dispositions
        )

        conditional_exclusion = (
            dispositions.get(stage_id)
            is BranchDisposition.EXCLUDED
        )

        conditional_version = (
            conditional_decision.conditional_execution_version
        )

    if optional_omission and conditional_exclusion:
        authorization = SkipAuthorization.OPTIONAL_AND_CONDITIONAL

    elif optional_omission:
        authorization = SkipAuthorization.OPTIONAL_OMISSION

    elif conditional_exclusion:
        authorization = SkipAuthorization.CONDITIONAL_EXCLUSION

    else:
        authorization = SkipAuthorization.UNAUTHORIZED

    authorized = (
        authorization
        is not SkipAuthorization.UNAUTHORIZED
    )

    # Frozen Phase 4 / Phase 6 base semantics are never rewritten.
    base_prerequisite_satisfied = False

    # Advanced Phase-7 semantics explicitly waive the prerequisite only
    # when a deliberate skip has valid orchestration authority.
    effective_prerequisite_satisfied = authorized

    return SkipSemanticsResolution(
        workflow_id=
            workflow_id,

        stage_id=
            stage_id,

        authorization=
            authorization,

        skip_authorized=
            authorized,

        base_prerequisite_satisfied=
            base_prerequisite_satisfied,

        effective_prerequisite_satisfied=
            effective_prerequisite_satisfied,

        prerequisite_waived=
            authorized,

        # A waived/skipped stage is never represented as completed.
        stage_completed=
            False,

        # Phase 6.1 base SKIPPED semantics remain no normal handoff.
        normal_handoff_allowed=
            False,

        optional_omission=
            optional_omission,

        conditional_exclusion=
            conditional_exclusion,

        optional_stages_version=
            optional_version,

        conditional_execution_version=
            conditional_version,
    )


__all__ = [
    "SKIP_SEMANTICS_VERSION",
    "SKIP_SEMANTICS_SCHEMA_VERSION",
    "SkipSemanticsError",
    "SkipAuthorization",
    "SkipSemanticsResolution",
    "resolve_skip_semantics",
]
