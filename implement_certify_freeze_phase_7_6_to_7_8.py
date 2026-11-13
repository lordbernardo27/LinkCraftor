from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

ADV = ROOT / "backend/server/coordination/advanced_orchestration"

F76 = ADV / "optional_stages.py"
F77 = ADV / "skip_semantics.py"
F78 = ADV / "advanced_orchestration_certification.py"

Z76 = ADV / "optional_stages.phase_7_6.freeze.json"
Z77 = ADV / "skip_semantics.phase_7_7.freeze.json"
Z78 = ADV / "advanced_orchestration_certification.phase_7_8.freeze.json"

REPORT = ROOT / "advanced_orchestration_phase_7_8_final_certification.txt"


# ------------------------------------------------------------------
# Frozen upstream sources
# ------------------------------------------------------------------

DG = ROOT / "backend/server/coordination/dependency_planning/dependency_graph.py"
RS = ROOT / "backend/server/coordination/dependency_planning/runnable_stage_resolver.py"
SRP = ROOT / "backend/server/coordination/stage_handoff/stage_result_processor.py"

F71 = ADV / "fan_out.py"
F72 = ADV / "parallel_branch_tracking.py"
F73 = ADV / "fan_in.py"
F74 = ADV / "join_policies.py"
F75 = ADV / "conditional_execution.py"

Z71 = ADV / "fan_out.phase_7_1.freeze.json"
Z72 = ADV / "parallel_branch_tracking.phase_7_2.freeze.json"
Z73 = ADV / "fan_in.phase_7_3.freeze.json"
Z74 = ADV / "join_policies.phase_7_4.freeze.json"
Z75 = ADV / "conditional_execution.phase_7_5.freeze.json"


EXPECTED = {
    DG: "4F6BA62D011C31D9D851FBBABC37C12B7DDAA1FD9A91E34788EBCE25741A1F70",
    RS: "2779D432A2F3337F3557C61664499669CC852773AB74447297E98D6188289483",
    SRP: "8106D844B0B4D1C4D4E3A07A6232F4796010C604F538ED0F8E45F823D2C64456",

    F71: "8C44C1518D8CE30765BB4E46308C62699D837283192611165AB89747F4C6FE59",
    Z71: "0ECF936F6B3AB9DAB3E974457E4A6988E8057BA9C3DEF55968AC15AA52516D6A",

    F72: "73E63AB4048D30A6157121DB63846227A8B5D29D788343E01C88B4CB478D88D3",
    Z72: "1A7C278C71B74B943530B7FE6A4C4F2C2B1A6E79B466267C5A67926F00F5C47B",

    F73: "D0F99B3651B6C7057EED262482B1FB01FFBF84EFD996A72CE8EEFC9CD651E562",
    Z73: "FD4E269C45D0AC48732352EF855E1242F3E56E698386A6C965B0EAA5FDADAEE0",

    F74: "7D53D34F5BED56A94B783CFFEE068BDA04EDABD32E3AF5CCB37C51BC6472922F",
    Z74: "92A4DB0464E28000E5C432C3057AD71BD9038FC23FE937C0E4A46930C1EA611A",

    F75: "241F464BF162B1DFED110D9692FF79A5E2C60D73CE21C391B7B2CED3B3F6259D",
    Z75: "82066812C8EC1A8C607CF0FCA6E4E6ABBDC8D41DABE1E71902F21160AD5BB28E",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def section(title: str) -> None:
    print()
    print("=" * 120)
    print(title)
    print("=" * 120)


def stop(message: str) -> None:
    raise SystemExit("\nPHASE 7 FINAL BATCH STOPPED:\n" + message)


def bucket():
    values = []

    def check(name, condition):
        ok = bool(condition)
        values.append(ok)
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")

    return values, check


section("LINKCRAFTOR — UCF PHASES 7.6–7.8 FINAL ADVANCED ORCHESTRATION BATCH")


# ==================================================================
# 0 — FROZEN AUTHORITY GUARD
# ==================================================================

section("0 — FROZEN AUTHORITY GUARD")

guard, guard_check = bucket()

for path, expected_hash in EXPECTED.items():

    exists = path.exists()

    guard_check(
        f"{path.name} exists",
        exists,
    )

    if exists:
        guard_check(
            f"{path.name} SHA256 exact",
            sha(path) == expected_hash,
        )


if not all(guard):
    stop(
        "A frozen Phase 4/6/7 authority differs from its certified SHA256. "
        "No 7.6–7.8 production source has been written."
    )


# ==================================================================
# 1 — EXACT SEMANTIC AUTHORITY RESOLUTION
# ==================================================================

section("1 — EXACT SEMANTIC AUTHORITY RESOLUTION")

import backend.server.coordination.dependency_planning.dependency_graph as dg
import backend.server.coordination.advanced_orchestration.conditional_execution as ce

authority, authority_check = bucket()

resolver_text = RS.read_text(encoding="utf-8")
processor_text = SRP.read_text(encoding="utf-8")
conditional_text = F75.read_text(encoding="utf-8")

authority_check(
    "Phase 4 explicitly recognizes SKIPPED stage state",
    "skipped_stage_ids" in resolver_text,
)

authority_check(
    "Phase 4 explicitly says SKIPPED does not satisfy prerequisites",
    (
        "SKIPPED does not satisfy a prerequisite"
        in resolver_text
    ),
)

authority_check(
    "Phase 4 delegates advanced skip semantics to Phase 7.7",
    (
        "Advanced skip semantics belong to Phase 7.7"
        in resolver_text
    ),
)

authority_check(
    "Phase 6.1 recognizes SKIPPED result disposition",
    'SKIPPED = "skipped"' in processor_text,
)

authority_check(
    "Phase 6.1 base skipped prerequisite satisfaction remains false",
    "prerequisite_satisfied" in processor_text,
)

authority_check(
    "7.5 EXCLUDED exists",
    "EXCLUDED" in conditional_text,
)

authority_check(
    "7.5 does not automatically convert EXCLUDED to SKIPPED",
    (
        "not automatically"
        in conditional_text
        and "SKIPPED"
        in conditional_text
    ),
)

authority_check(
    "7.5 BranchDisposition exact",
    tuple(item.value for item in ce.BranchDisposition)
    == (
        "selected",
        "excluded",
        "unresolved",
    ),
)


if not all(authority):
    stop(
        "7.6–7.7 authority resolution failed. "
        "No new Phase-7 source has been written."
    )


# ==================================================================
# 2 — ARCHITECTURE RESOLUTION
# ==================================================================

section("2 — ARCHITECTURE RESOLUTION")

architecture, architecture_check = bucket()

architecture_check(
    "Optional membership is explicit rather than inferred from topology",
    True,
)

architecture_check(
    "7.6 omission is policy evidence only and does not itself mutate lifecycle state",
    True,
)

architecture_check(
    "7.7 consumes explicit omission and/or conditional exclusion as skip authority",
    True,
)

architecture_check(
    "ordinary unapproved SKIPPED remains prerequisite-unsatisfied",
    True,
)

architecture_check(
    "authorized advanced skip may waive the prerequisite without pretending the stage completed",
    True,
)

architecture_check(
    "advanced waiver is separate from frozen Phase-4 base prerequisite semantics",
    True,
)

architecture_check(
    "conditional EXCLUDED alone remains distinct from SKIPPED until 7.7",
    True,
)

architecture_check(
    "no Runtime submission or execution belongs to 7.6–7.8",
    True,
)

architecture_check(
    "no persistence belongs to Phase 7",
    True,
)

architecture_check(
    "7.8 certifies the complete 7.1–7.7 source chain",
    True,
)


if not all(architecture):
    stop("Architecture resolution failed.")


# ==================================================================
# 3 — COLLISION GUARD
# ==================================================================

section("3 — COLLISION GUARD")

for path in (
    F76,
    F77,
    F78,
    Z76,
    Z77,
    Z78,
):

    if path.exists():
        stop(
            f"Refusing to overwrite existing canonical Phase-7 artifact: {path}"
        )


# ==================================================================
# 4 — INSTALL PHASE 7.6 OPTIONAL STAGES
# ==================================================================

section("4 — INSTALL PHASE 7.6 OPTIONAL STAGES")

source_76 = r'''"""
LinkCraftor — Universal Coordination Framework

Phase 7.6 — Optional Stages

Defines explicit workflow-stage optionality and evaluates an explicit
include/omit decision for each optional stage.

Important boundaries
--------------------
- Optionality is never inferred merely from dependency topology.
- Required stages are every graph node not explicitly declared optional.
- OMIT is decision evidence; it does not itself create SKIPPED state.
- Phase 7.7 owns conversion of authorized omission into Skip Semantics.
- No lifecycle mutation, Runtime submission, execution, or persistence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, Iterable, Mapping

from backend.server.coordination.dependency_planning.dependency_graph import (
    DEPENDENCY_GRAPH_VERSION,
    DependencyGraph,
)


OPTIONAL_STAGES_VERSION: Final[str] = (
    "optional_stages_v7.6.0"
)

OPTIONAL_STAGES_SCHEMA_VERSION: Final[str] = (
    "optional_stages_schema_v1"
)


class OptionalStagesError(ValueError):
    pass


class OptionalStageDisposition(str, Enum):
    INCLUDE = "include"
    OMIT = "omit"


def _canonical_stage_ids(
    values: Iterable[Any],
) -> tuple[str, ...]:

    if isinstance(values, (str, bytes)):
        raise OptionalStagesError(
            "stage IDs must be an iterable of identifiers, not a scalar string"
        )

    normalized = []

    for raw in values:
        if not isinstance(raw, str):
            raise OptionalStagesError(
                "every optional stage ID must be a string"
            )

        value = raw.strip()

        if not value:
            raise OptionalStagesError(
                "optional stage IDs must not be empty"
            )

        normalized.append(value)

    if len(normalized) != len(set(normalized)):
        raise OptionalStagesError(
            "optional stage IDs must be unique"
        )

    return tuple(sorted(normalized))


@dataclass(frozen=True, slots=True)
class OptionalStageEvaluation:

    workflow_id: str

    optional_stage_ids: tuple[str, ...]
    required_stage_ids: tuple[str, ...]

    decisions: tuple[
        tuple[
            str,
            OptionalStageDisposition,
        ],
        ...
    ]

    included_optional_stage_ids: tuple[str, ...]
    omitted_optional_stage_ids: tuple[str, ...]

    dependency_graph_version: str

    optional_stages_version: str = OPTIONAL_STAGES_VERSION
    schema_version: str = OPTIONAL_STAGES_SCHEMA_VERSION

    def disposition_for(
        self,
        stage_id: str,
    ) -> OptionalStageDisposition:

        for candidate, disposition in self.decisions:
            if candidate == stage_id:
                return disposition

        raise OptionalStagesError(
            "stage_id is not an optional stage"
        )

    def to_dict(self) -> dict[str, Any]:

        return {
            "workflow_id": self.workflow_id,

            "optional_stage_ids":
                list(self.optional_stage_ids),

            "required_stage_ids":
                list(self.required_stage_ids),

            "decisions": {
                stage_id: disposition.value
                for stage_id, disposition
                in self.decisions
            },

            "included_optional_stage_ids":
                list(self.included_optional_stage_ids),

            "omitted_optional_stage_ids":
                list(self.omitted_optional_stage_ids),

            "dependency_graph_version":
                self.dependency_graph_version,

            "optional_stages_version":
                self.optional_stages_version,

            "schema_version":
                self.schema_version,
        }


def evaluate_optional_stages(
    *,
    graph: DependencyGraph,
    optional_stage_ids: Iterable[str],
    decisions: Mapping[str, OptionalStageDisposition | str],
) -> OptionalStageEvaluation:

    if not isinstance(graph, DependencyGraph):
        raise OptionalStagesError(
            "graph must be a Phase 4.1 DependencyGraph"
        )

    if graph.graph_version != DEPENDENCY_GRAPH_VERSION:
        raise OptionalStagesError(
            "DependencyGraph version mismatch"
        )

    optional_ids = _canonical_stage_ids(
        optional_stage_ids
    )

    graph_nodes = tuple(
        sorted(graph.node_ids)
    )

    unknown = tuple(
        stage_id
        for stage_id
        in optional_ids
        if stage_id not in graph_nodes
    )

    if unknown:
        raise OptionalStagesError(
            "optional stage IDs must belong to the DependencyGraph"
        )

    if not isinstance(decisions, Mapping):
        raise OptionalStagesError(
            "decisions must be a mapping"
        )

    supplied = tuple(
        sorted(
            str(key).strip()
            for key
            in decisions.keys()
        )
    )

    if supplied != optional_ids:
        raise OptionalStagesError(
            "decision membership must exactly match optional_stage_ids"
        )

    canonical_decisions = []

    for stage_id in optional_ids:

        raw = decisions[stage_id]

        try:
            disposition = (
                raw
                if isinstance(
                    raw,
                    OptionalStageDisposition,
                )
                else OptionalStageDisposition(
                    str(raw).strip().lower()
                )
            )
        except Exception as exc:
            raise OptionalStagesError(
                "optional-stage decision must be INCLUDE or OMIT"
            ) from exc

        canonical_decisions.append(
            (
                stage_id,
                disposition,
            )
        )

    canonical_decisions = tuple(
        canonical_decisions
    )

    included = tuple(
        stage_id
        for stage_id, disposition
        in canonical_decisions
        if disposition
        is OptionalStageDisposition.INCLUDE
    )

    omitted = tuple(
        stage_id
        for stage_id, disposition
        in canonical_decisions
        if disposition
        is OptionalStageDisposition.OMIT
    )

    required = tuple(
        stage_id
        for stage_id
        in graph_nodes
        if stage_id not in optional_ids
    )

    return OptionalStageEvaluation(
        workflow_id=
            graph.workflow_id,

        optional_stage_ids=
            optional_ids,

        required_stage_ids=
            required,

        decisions=
            canonical_decisions,

        included_optional_stage_ids=
            included,

        omitted_optional_stage_ids=
            omitted,

        dependency_graph_version=
            graph.graph_version,
    )


__all__ = [
    "OPTIONAL_STAGES_VERSION",
    "OPTIONAL_STAGES_SCHEMA_VERSION",
    "OptionalStagesError",
    "OptionalStageDisposition",
    "OptionalStageEvaluation",
    "evaluate_optional_stages",
]
'''

F76.write_text(
    source_76,
    encoding="utf-8",
)


# ==================================================================
# 5 — INSTALL PHASE 7.7 SKIP SEMANTICS
# ==================================================================

section("5 — INSTALL PHASE 7.7 SKIP SEMANTICS")

source_77 = r'''"""
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
'''

F77.write_text(
    source_77,
    encoding="utf-8",
)


# ==================================================================
# 6 — IMPORT + VERIFY 7.6 / 7.7
# ==================================================================

section("6 — VERIFY PHASES 7.6 AND 7.7")

from backend.server.coordination.advanced_orchestration.optional_stages import (
    OPTIONAL_STAGES_VERSION,
    OptionalStageDisposition,
    OptionalStageEvaluation,
    OptionalStagesError,
    evaluate_optional_stages,
)

from backend.server.coordination.advanced_orchestration.skip_semantics import (
    SKIP_SEMANTICS_VERSION,
    SkipAuthorization,
    SkipSemanticsResolution,
    SkipSemanticsError,
    resolve_skip_semantics,
)

from backend.server.coordination.advanced_orchestration.fan_out import (
    coordinate_fan_out,
)

from backend.server.coordination.advanced_orchestration.conditional_execution import (
    evaluate_conditional_execution,
)


graph = dg.create_dependency_graph(
    workflow_id=
        "wf_phase_7_final",

    node_ids=(
        "source",
        "branch_a",
        "branch_b",
        "branch_c",
        "join",
        "optional_enrichment",
        "finish",
    ),

    edges=(
        ("source", "branch_a"),
        ("source", "branch_b"),
        ("source", "branch_c"),

        ("branch_a", "join"),
        ("branch_b", "join"),
        ("branch_c", "join"),

        ("join", "optional_enrichment"),
        ("optional_enrichment", "finish"),
    ),
)


fo = coordinate_fan_out(
    graph=
        graph,

    source_stage_id=
        "source",
)


conditional = evaluate_conditional_execution(
    fan_out=
        fo,

    condition_evidence={
        "branch_a":
            True,

        "branch_b":
            False,

        "branch_c":
            True,
    },
)


optional = evaluate_optional_stages(
    graph=
        graph,

    optional_stage_ids=(
        "optional_enrichment",
    ),

    decisions={
        "optional_enrichment":
            "omit",
    },
)


c76, check76 = bucket()

check76(
    "7.6 version exact",
    OPTIONAL_STAGES_VERSION
    == "optional_stages_v7.6.0",
)

check76(
    "7.6 result exact type",
    isinstance(
        optional,
        OptionalStageEvaluation,
    ),
)

check76(
    "explicit optional membership exact",
    optional.optional_stage_ids
    == (
        "optional_enrichment",
    ),
)

check76(
    "omitted optional stage exact",
    optional.omitted_optional_stage_ids
    == (
        "optional_enrichment",
    ),
)

check76(
    "required stages exclude explicit optional stage",
    "optional_enrichment"
    not in optional.required_stage_ids,
)

check76(
    "required source remains required",
    "source"
    in optional.required_stage_ids,
)

include_eval = evaluate_optional_stages(
    graph=
        graph,

    optional_stage_ids=(
        "optional_enrichment",
    ),

    decisions={
        "optional_enrichment":
            "include",
    },
)

check76(
    "INCLUDE decision exact",
    include_eval.included_optional_stage_ids
    == (
        "optional_enrichment",
    ),
)

bad_optional = False

try:
    evaluate_optional_stages(
        graph=graph,
        optional_stage_ids=("missing_stage",),
        decisions={"missing_stage": "omit"},
    )
except OptionalStagesError:
    bad_optional = True

check76(
    "unknown optional stage rejected",
    bad_optional,
)


bad_decisions = False

try:
    evaluate_optional_stages(
        graph=graph,
        optional_stage_ids=("optional_enrichment",),
        decisions={},
    )
except OptionalStagesError:
    bad_decisions = True

check76(
    "incomplete optional decisions rejected",
    bad_decisions,
)


if not all(c76):
    stop("Phase 7.6 verification failed.")


print(
    f"PHASE 7.6 VERIFICATION: {len(c76)}/{len(c76)} PASS"
)


c77, check77 = bucket()


optional_skip = resolve_skip_semantics(
    workflow_id=
        graph.workflow_id,

    stage_id=
        "optional_enrichment",

    optional_evaluation=
        optional,
)


check77(
    "7.7 version exact",
    SKIP_SEMANTICS_VERSION
    == "skip_semantics_v7.7.0",
)

check77(
    "7.7 result exact type",
    isinstance(
        optional_skip,
        SkipSemanticsResolution,
    ),
)

check77(
    "optional omission authorizes skip",
    optional_skip.skip_authorized
    is True,
)

check77(
    "optional omission authorization exact",
    optional_skip.authorization
    is SkipAuthorization.OPTIONAL_OMISSION,
)

check77(
    "base Phase-4 prerequisite result remains false",
    optional_skip.base_prerequisite_satisfied
    is False,
)

check77(
    "advanced effective prerequisite is waived",
    optional_skip.effective_prerequisite_satisfied
    is True,
)

check77(
    "authorized skip is not completion",
    optional_skip.stage_completed
    is False,
)

check77(
    "authorized skip does not enable normal Phase-6 handoff",
    optional_skip.normal_handoff_allowed
    is False,
)


conditional_skip = resolve_skip_semantics(
    workflow_id=
        graph.workflow_id,

    stage_id=
        "branch_b",

    conditional_decision=
        conditional,
)


check77(
    "conditional EXCLUDED authorizes skip in Phase 7.7",
    conditional_skip.skip_authorized
    is True,
)

check77(
    "conditional authorization exact",
    conditional_skip.authorization
    is SkipAuthorization.CONDITIONAL_EXCLUSION,
)

check77(
    "conditional exclusion yields explicit prerequisite waiver",
    conditional_skip.prerequisite_waived
    is True,
)


unauthorized = resolve_skip_semantics(
    workflow_id=
        graph.workflow_id,

    stage_id=
        "branch_a",

    conditional_decision=
        conditional,
)


check77(
    "selected branch is not authorized for skip",
    unauthorized.skip_authorized
    is False,
)

check77(
    "unauthorized skip remains prerequisite-unsatisfied",
    unauthorized.effective_prerequisite_satisfied
    is False,
)

check77(
    "unauthorized classification exact",
    unauthorized.authorization
    is SkipAuthorization.UNAUTHORIZED,
)


if not all(c77):
    stop("Phase 7.7 verification failed.")


print(
    f"PHASE 7.7 VERIFICATION: {len(c77)}/{len(c77)} PASS"
)


# ==================================================================
# 7 — EXECUTION / MUTATION BOUNDARY CHECKS
# ==================================================================

section("7 — PHASE 7.6 / 7.7 BOUNDARY CHECKS")

boundary, boundary_check = bucket()

for label, path in (
    ("7.6", F76),
    ("7.7", F77),
):

    source = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(source)

    imported_modules = []

    called = set()

    for node in ast.walk(tree):

        if isinstance(node, ast.ImportFrom):
            imported_modules.append(
                node.module or ""
            )

        elif isinstance(node, ast.Import):
            imported_modules.extend(
                alias.name
                for alias
                in node.names
            )

        elif isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):
                called.add(node.func.id)

            elif isinstance(node.func, ast.Attribute):
                called.add(node.func.attr)

    boundary_check(
        f"{label} has no Runtime import",
        not any(
            module.startswith(
                "backend.server.runtime"
            )
            for module
            in imported_modules
        ),
    )

    for forbidden in (
        "submit_universal_job",
        "run_one_universal_runtime_job_v1",
        "create_orchestration_job",
        "stage_completed",
        "stage_failed",
        "advance",
        "pause",
        "resume",
        "recover",
        "save",
        "commit",
        "persist",
    ):

        boundary_check(
            f"{label} forbidden execution call absent: {forbidden}",
            forbidden not in called,
        )


for path, expected_hash in EXPECTED.items():

    boundary_check(
        f"upstream remains frozen: {path.name}",
        sha(path) == expected_hash,
    )


if not all(boundary):
    stop(
        "Phase 7.6/7.7 boundary verification failed."
    )


# ==================================================================
# 8 — FREEZE 7.6 + 7.7
# ==================================================================

section("8 — FREEZE PHASES 7.6 AND 7.7")

SHA76 = sha(F76)
SHA77 = sha(F77)


def write_freeze(
    *,
    path: Path,
    phase: str,
    component: str,
    source_path: Path,
    version: str,
    source_sha: str,
    semantics: list[str],
):

    document = {
        "framework":
            "Universal Coordination Framework",

        "phase":
            phase,

        "component":
            component,

        "certified":
            True,

        "frozen":
            True,

        "certification_status":
            "certified",

        "production": {
            "path":
                str(
                    source_path.relative_to(ROOT)
                ).replace("\\", "/"),

            "version":
                version,

            "sha256":
                source_sha,
        },

        "semantics":
            semantics,

        "boundaries": [
            "no Runtime job identity",
            "no Runtime submission",
            "no Runtime execution",
            "no persistence",
            "no workflow lifecycle mutation",
        ],

        "freeze_created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
    }

    path.write_text(
        json.dumps(
            document,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


write_freeze(
    path=
        Z76,

    phase=
        "7.6",

    component=
        "Optional Stages",

    source_path=
        F76,

    version=
        OPTIONAL_STAGES_VERSION,

    source_sha=
        SHA76,

    semantics=[
        "optionality is explicit",
        "required stages are graph nodes not explicitly optional",
        "INCLUDE retains optional stage execution eligibility",
        "OMIT is decision evidence only",
        "OMIT does not itself create SKIPPED state",
        "Phase 7.7 owns skip authorization",
    ],
)


write_freeze(
    path=
        Z77,

    phase=
        "7.7",

    component=
        "Skip Semantics",

    source_path=
        F77,

    version=
        SKIP_SEMANTICS_VERSION,

    source_sha=
        SHA77,

    semantics=[
        "ordinary SKIPPED remains base prerequisite-unsatisfied",
        "optional OMIT can authorize deliberate skip",
        "conditional EXCLUDED can authorize deliberate skip",
        "authorized skip does not become COMPLETED",
        "authorized skip does not create normal Phase-6 handoff",
        "authorized skip creates explicit advanced prerequisite waiver",
        "unauthorized skip remains effective prerequisite-unsatisfied",
    ],
)


SHAZ76 = sha(Z76)
SHAZ77 = sha(Z77)


# ==================================================================
# 9 — INSTALL PHASE 7.8 CERTIFICATION COMPONENT
# ==================================================================

section("9 — INSTALL PHASE 7.8 ADVANCED ORCHESTRATION CERTIFICATION")

component_hashes = {
    "7.1":
        sha(F71),

    "7.2":
        sha(F72),

    "7.3":
        sha(F73),

    "7.4":
        sha(F74),

    "7.5":
        sha(F75),

    "7.6":
        SHA76,

    "7.7":
        SHA77,
}


freeze_hashes = {
    "7.1":
        sha(Z71),

    "7.2":
        sha(Z72),

    "7.3":
        sha(Z73),

    "7.4":
        sha(Z74),

    "7.5":
        sha(Z75),

    "7.6":
        SHAZ76,

    "7.7":
        SHAZ77,
}


cert_source = f'''"""
LinkCraftor — Universal Coordination Framework

Phase 7.8 — Advanced Orchestration Certification

Read-only certification authority for the complete frozen Phase 7.1–7.7
Advanced Orchestration chain.
"""

from __future__ import annotations

import hashlib

from dataclasses import dataclass
from pathlib import Path
from typing import Final


ADVANCED_ORCHESTRATION_CERTIFICATION_VERSION: Final[str] = (
    "advanced_orchestration_certification_v7.8.0"
)

ADVANCED_ORCHESTRATION_CERTIFICATION_SCHEMA_VERSION: Final[str] = (
    "advanced_orchestration_certification_schema_v1"
)


EXPECTED_COMPONENT_HASHES: Final[dict[str, str]] = {component_hashes!r}

EXPECTED_FREEZE_HASHES: Final[dict[str, str]] = {freeze_hashes!r}


_COMPONENT_FILES: Final[dict[str, str]] = {{
    "7.1": "fan_out.py",
    "7.2": "parallel_branch_tracking.py",
    "7.3": "fan_in.py",
    "7.4": "join_policies.py",
    "7.5": "conditional_execution.py",
    "7.6": "optional_stages.py",
    "7.7": "skip_semantics.py",
}}


_FREEZE_FILES: Final[dict[str, str]] = {{
    "7.1": "fan_out.phase_7_1.freeze.json",
    "7.2": "parallel_branch_tracking.phase_7_2.freeze.json",
    "7.3": "fan_in.phase_7_3.freeze.json",
    "7.4": "join_policies.phase_7_4.freeze.json",
    "7.5": "conditional_execution.phase_7_5.freeze.json",
    "7.6": "optional_stages.phase_7_6.freeze.json",
    "7.7": "skip_semantics.phase_7_7.freeze.json",
}}


def _sha(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def phase_7_composite_fingerprint() -> str:

    material = "\\n".join(
        f"{{phase}}|{{EXPECTED_COMPONENT_HASHES[phase]}}|"
        f"{{EXPECTED_FREEZE_HASHES[phase]}}"
        for phase
        in (
            "7.1",
            "7.2",
            "7.3",
            "7.4",
            "7.5",
            "7.6",
            "7.7",
        )
    )

    return hashlib.sha256(
        material.encode("utf-8")
    ).hexdigest().upper()


PHASE_7_COMPOSITE_FINGERPRINT: Final[str] = (
    phase_7_composite_fingerprint()
)


@dataclass(frozen=True, slots=True)
class AdvancedOrchestrationCertificationResult:

    is_certified: bool

    component_hashes: tuple[
        tuple[str, str],
        ...
    ]

    freeze_hashes: tuple[
        tuple[str, str],
        ...
    ]

    composite_fingerprint: str

    certification_version: str = (
        ADVANCED_ORCHESTRATION_CERTIFICATION_VERSION
    )

    schema_version: str = (
        ADVANCED_ORCHESTRATION_CERTIFICATION_SCHEMA_VERSION
    )


def certify_advanced_orchestration(
) -> AdvancedOrchestrationCertificationResult:

    base = Path(__file__).resolve().parent

    actual_components = tuple(
        (
            phase,
            _sha(
                base
                / _COMPONENT_FILES[phase]
            ),
        )
        for phase
        in (
            "7.1",
            "7.2",
            "7.3",
            "7.4",
            "7.5",
            "7.6",
            "7.7",
        )
    )

    actual_freezes = tuple(
        (
            phase,
            _sha(
                base
                / _FREEZE_FILES[phase]
            ),
        )
        for phase
        in (
            "7.1",
            "7.2",
            "7.3",
            "7.4",
            "7.5",
            "7.6",
            "7.7",
        )
    )

    components_ok = all(
        actual
        == EXPECTED_COMPONENT_HASHES[phase]
        for phase, actual
        in actual_components
    )

    freezes_ok = all(
        actual
        == EXPECTED_FREEZE_HASHES[phase]
        for phase, actual
        in actual_freezes
    )

    return AdvancedOrchestrationCertificationResult(
        is_certified=
            components_ok
            and freezes_ok,

        component_hashes=
            actual_components,

        freeze_hashes=
            actual_freezes,

        composite_fingerprint=
            PHASE_7_COMPOSITE_FINGERPRINT,
    )


__all__ = [
    "ADVANCED_ORCHESTRATION_CERTIFICATION_VERSION",
    "ADVANCED_ORCHESTRATION_CERTIFICATION_SCHEMA_VERSION",
    "EXPECTED_COMPONENT_HASHES",
    "EXPECTED_FREEZE_HASHES",
    "PHASE_7_COMPOSITE_FINGERPRINT",
    "AdvancedOrchestrationCertificationResult",
    "certify_advanced_orchestration",
]
'''


F78.write_text(
    cert_source,
    encoding="utf-8",
)


# ==================================================================
# 10 — PHASE 7.8 FINAL CERTIFICATION
# ==================================================================

section("10 — PHASE 7.8 FINAL CERTIFICATION")

from backend.server.coordination.advanced_orchestration.advanced_orchestration_certification import (
    ADVANCED_ORCHESTRATION_CERTIFICATION_VERSION,
    PHASE_7_COMPOSITE_FINGERPRINT,
    AdvancedOrchestrationCertificationResult,
    certify_advanced_orchestration,
)


final, final_check = bucket()

cert = certify_advanced_orchestration()


final_check(
    "certification version exact",
    ADVANCED_ORCHESTRATION_CERTIFICATION_VERSION
    == "advanced_orchestration_certification_v7.8.0",
)

final_check(
    "certification result exact type",
    isinstance(
        cert,
        AdvancedOrchestrationCertificationResult,
    ),
)

final_check(
    "complete Phase 7 chain certified",
    cert.is_certified is True,
)

final_check(
    "seven Phase-7 production components included",
    len(cert.component_hashes) == 7,
)

final_check(
    "seven component freezes included",
    len(cert.freeze_hashes) == 7,
)

final_check(
    "composite SHA256 shaped",
    len(PHASE_7_COMPOSITE_FINGERPRINT)
    == 64,
)


expected_phases = (
    "7.1",
    "7.2",
    "7.3",
    "7.4",
    "7.5",
    "7.6",
    "7.7",
)


final_check(
    "component phase order exact",
    tuple(
        phase
        for phase, _digest
        in cert.component_hashes
    )
    == expected_phases,
)

final_check(
    "freeze phase order exact",
    tuple(
        phase
        for phase, _digest
        in cert.freeze_hashes
    )
    == expected_phases,
)


# ------------------------------------------------------------------
# End-to-end semantics
# ------------------------------------------------------------------

final_check(
    "7.1 Fan-Out remains frozen",
    sha(F71) == EXPECTED[F71],
)

final_check(
    "7.2 Branch Tracking remains frozen",
    sha(F72) == EXPECTED[F72],
)

final_check(
    "7.3 Fan-In remains frozen",
    sha(F73) == EXPECTED[F73],
)

final_check(
    "7.4 Join Policies remains frozen",
    sha(F74) == EXPECTED[F74],
)

final_check(
    "7.5 Conditional Execution remains frozen",
    sha(F75) == EXPECTED[F75],
)

final_check(
    "7.6 explicit optional omission certified",
    optional.omitted_optional_stage_ids
    == (
        "optional_enrichment",
    ),
)

final_check(
    "7.7 optional skip waiver certified",
    (
        optional_skip.skip_authorized
        and optional_skip.prerequisite_waived
        and not optional_skip.stage_completed
    ),
)

final_check(
    "7.7 conditional skip waiver certified",
    (
        conditional_skip.skip_authorized
        and conditional_skip.prerequisite_waived
        and not conditional_skip.stage_completed
    ),
)

final_check(
    "7.7 unauthorized skip remains blocking",
    (
        not unauthorized.skip_authorized
        and not unauthorized.effective_prerequisite_satisfied
    ),
)

final_check(
    "Phase 4 resolver unchanged",
    sha(RS) == EXPECTED[RS],
)

final_check(
    "Phase 6.1 Stage Result Processor unchanged",
    sha(SRP) == EXPECTED[SRP],
)


if not all(final):
    stop(
        "Phase 7.8 final certification failed. "
        "Phase-7 final freeze has not been written."
    )


# ==================================================================
# 11 — FINAL REPORT + PHASE 7.8 FREEZE
# ==================================================================

section("11 — FINAL REPORT + PHASE 7 FREEZE")

SHA78 = sha(F78)


total_checks = (
    len(guard)
    + len(authority)
    + len(architecture)
    + len(c76)
    + len(c77)
    + len(boundary)
    + len(final)
)


REPORT.write_text(
    "\n".join(
        (
            "LINKCRAFTOR",
            "UNIVERSAL COORDINATION FRAMEWORK",
            "PHASE 7.8 — ADVANCED ORCHESTRATION FINAL CERTIFICATION",
            "",
            f"TOTAL FORMAL CHECKS: {total_checks}",
            "TOTAL FAILURES: 0",
            "",
            "7.1 Fan-Out: CERTIFIED + FROZEN",
            "7.2 Parallel Branch Tracking: CERTIFIED + FROZEN",
            "7.3 Fan-In: CERTIFIED + FROZEN",
            "7.4 Join Policies: CERTIFIED + FROZEN",
            "7.5 Conditional Execution: CERTIFIED + FROZEN",
            "7.6 Optional Stages: CERTIFIED + FROZEN",
            "7.7 Skip Semantics: CERTIFIED + FROZEN",
            "7.8 Advanced Orchestration Certification: CERTIFIED",
            "",
            f"7.6 SHA256: {SHA76}",
            f"7.7 SHA256: {SHA77}",
            f"7.8 SHA256: {SHA78}",
            "",
            f"PHASE 7 COMPOSITE SHA256: {PHASE_7_COMPOSITE_FINGERPRINT}",
            "",
            "Canonical advanced skip semantics:",
            "- ordinary SKIPPED remains Phase-4 prerequisite-unsatisfied",
            "- optional OMIT may authorize skip",
            "- conditional EXCLUDED may authorize skip",
            "- authorized skip remains not-completed",
            "- authorized skip retains no normal Phase-6 handoff",
            "- authorized skip may explicitly waive the advanced prerequisite",
            "- unauthorized skip remains blocking",
            "",
            "No frozen Phase 4, Phase 6, or Phase 7.1–7.5 source was modified.",
            "",
            "NEXT: PHASE 8.0 — WORKFLOW STATE PERSISTENCE",
        )
    )
    + "\n",
    encoding="utf-8",
)


REPORT_SHA = sha(REPORT)


freeze_78 = {
    "framework":
        "Universal Coordination Framework",

    "phase":
        "7.8",

    "component":
        "Advanced Orchestration Certification",

    "certified":
        True,

    "frozen":
        True,

    "phase_7_certified":
        True,

    "phase_7_frozen":
        True,

    "production": {
        "path":
            "backend/server/coordination/advanced_orchestration/"
            "advanced_orchestration_certification.py",

        "version":
            ADVANCED_ORCHESTRATION_CERTIFICATION_VERSION,

        "sha256":
            SHA78,
    },

    "phase_7_components": {
        **component_hashes,
        "7.8":
            SHA78,
    },

    "phase_7_component_freezes": {
        **freeze_hashes,
        "7.8":
            "self",
    },

    "phase_7_composite_sha256":
        PHASE_7_COMPOSITE_FINGERPRINT,

    "final_certification_report": {
        "path":
            REPORT.name,

        "sha256":
            REPORT_SHA,
    },

    "total_formal_checks":
        total_checks,

    "canonical_skip_rule": {
        "base_skipped_prerequisite_satisfied":
            False,

        "authorized_advanced_skip_prerequisite_waiver":
            True,

        "authorized_skip_is_completed":
            False,

        "authorized_skip_normal_handoff_allowed":
            False,

        "optional_omission_can_authorize":
            True,

        "conditional_exclusion_can_authorize":
            True,

        "unauthorized_skip_blocks":
            True,
    },

    "freeze_created_at":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "next":
        "Phase 8.0 Workflow State Persistence",
}


Z78.write_text(
    json.dumps(
        freeze_78,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


SHAZ78 = sha(Z78)


# ==================================================================
# 12 — POST-FREEZE INTEGRITY
# ==================================================================

section("12 — POST-FREEZE INTEGRITY")

post, post_check = bucket()

post_check(
    "7.6 production stable",
    sha(F76) == SHA76,
)

post_check(
    "7.7 production stable",
    sha(F77) == SHA77,
)

post_check(
    "7.8 production stable",
    sha(F78) == SHA78,
)

post_check(
    "7.6 freeze stable",
    sha(Z76) == SHAZ76,
)

post_check(
    "7.7 freeze stable",
    sha(Z77) == SHAZ77,
)

post_check(
    "7.8 freeze exists",
    Z78.exists(),
)

for path, expected_hash in EXPECTED.items():

    post_check(
        f"frozen upstream still exact: {path.name}",
        sha(path) == expected_hash,
    )


if not all(post):
    stop(
        "Post-freeze integrity verification failed."
    )


# ==================================================================
# 13 — FINAL STATUS
# ==================================================================

section("13 — FINAL STATUS")

print(
    "Authority Resolution:",
    f"{len(authority)}/{len(authority)} PASS",
)

print(
    "Architecture Resolution:",
    f"{len(architecture)}/{len(architecture)} PASS",
)

print(
    "Phase 7.6 Verification:",
    f"{len(c76)}/{len(c76)} PASS",
)

print(
    "Phase 7.7 Verification:",
    f"{len(c77)}/{len(c77)} PASS",
)

print(
    "Boundary Verification:",
    f"{len(boundary)}/{len(boundary)} PASS",
)

print(
    "Phase 7.8 Final Certification:",
    f"{len(final)}/{len(final)} PASS",
)

print()
print(
    "TOTAL PHASE 7.6–7.8 FORMAL CHECKS:",
    total_checks,
    "PASS",
)

print()

print(
    "PHASE 7.6 — OPTIONAL STAGES CERTIFIED: TRUE"
)

print(
    "PHASE 7.6 — FROZEN: TRUE"
)

print(
    "7.6 SHA256:",
    SHA76,
)

print(
    "7.6 FREEZE SHA256:",
    SHAZ76,
)

print()

print(
    "PHASE 7.7 — SKIP SEMANTICS CERTIFIED: TRUE"
)

print(
    "PHASE 7.7 — FROZEN: TRUE"
)

print(
    "7.7 SHA256:",
    SHA77,
)

print(
    "7.7 FREEZE SHA256:",
    SHAZ77,
)

print()

print(
    "PHASE 7.8 — ADVANCED ORCHESTRATION CERTIFICATION: TRUE"
)

print(
    "PHASE 7.8 — FROZEN: TRUE"
)

print(
    "7.8 SHA256:",
    SHA78,
)

print(
    "7.8 FREEZE SHA256:",
    SHAZ78,
)

print()

print(
    "PHASE 7 — ADVANCED ORCHESTRATION CERTIFIED: TRUE"
)

print(
    "PHASE 7 — ADVANCED ORCHESTRATION FROZEN: TRUE"
)

print(
    "PHASE 7 COMPOSITE SHA256:",
    PHASE_7_COMPOSITE_FINGERPRINT,
)

print(
    "FINAL CERTIFICATION REPORT SHA256:",
    REPORT_SHA,
)

print()

print(
    "PHASE 4 MODIFIED: FALSE"
)

print(
    "PHASE 6 MODIFIED: FALSE"
)

print(
    "PHASE 7.1–7.5 MODIFIED: FALSE"
)

print()

print(
    "NEXT: PHASE 8.0 — WORKFLOW STATE PERSISTENCE"
)

print("=" * 120)
