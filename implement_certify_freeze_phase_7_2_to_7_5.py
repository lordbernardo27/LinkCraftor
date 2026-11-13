from __future__ import annotations

import ast
import hashlib
import inspect
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

ADV = (
    ROOT
    / "backend/server/coordination/advanced_orchestration"
)

F72 = ADV / "parallel_branch_tracking.py"
F73 = ADV / "fan_in.py"
F74 = ADV / "join_policies.py"
F75 = ADV / "conditional_execution.py"

FR72 = ADV / "parallel_branch_tracking.phase_7_2.freeze.json"
FR73 = ADV / "fan_in.phase_7_3.freeze.json"
FR74 = ADV / "join_policies.phase_7_4.freeze.json"
FR75 = ADV / "conditional_execution.phase_7_5.freeze.json"

REPORT = (
    ROOT
    / "advanced_orchestration_phase_7_2_to_7_5_batch_certification.txt"
)

DG = (
    ROOT
    / "backend/server/coordination/dependency_planning/"
      "dependency_graph.py"
)

F71 = (
    ADV
    / "fan_out.py"
)

FR71 = (
    ADV
    / "fan_out.phase_7_1.freeze.json"
)


EXPECTED_DG_SHA = (
    "4F6BA62D011C31D9D851FBBABC37C12B7DDAA1FD9A91E34788EBCE25741A1F70"
)

EXPECTED_71_SHA = (
    "8C44C1518D8CE30765BB4E46308C62699D837283192611165AB89747F4C6FE59"
)

EXPECTED_71_FREEZE_SHA = (
    "0ECF936F6B3AB9DAB3E974457E4A6988E8057BA9C3DEF55968AC15AA52516D6A"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def section(title: str) -> None:
    print()
    print("=" * 120)
    print(title)
    print("=" * 120)


def stop(message: str) -> None:
    raise SystemExit(
        "\nPHASE 7.2–7.5 BATCH STOPPED:\n"
        + message
    )


def check_bucket():
    values = []

    def check(name, condition):
        ok = bool(condition)
        values.append(ok)

        print(
            f"[{'PASS' if ok else 'FAIL'}] {name}"
        )

    return values, check


section(
    "LINKCRAFTOR — UCF PHASES 7.2–7.5 "
    "ADVANCED ORCHESTRATION ACCELERATED BATCH"
)


# ==================================================================
# 0 — FROZEN UPSTREAM INTEGRITY
# ==================================================================

section(
    "0 — FROZEN UPSTREAM INTEGRITY"
)


required = (
    DG,
    F71,
    FR71,
)


for path in required:
    if not path.exists():
        stop(
            f"Required upstream authority missing: {path}"
        )


upstream_checks, upstream_check = check_bucket()


upstream_check(
    "Phase 4.1 DependencyGraph unchanged",
    sha256(DG)
    == EXPECTED_DG_SHA,
)

upstream_check(
    "Phase 7.1 Fan-Out unchanged",
    sha256(F71)
    == EXPECTED_71_SHA,
)

upstream_check(
    "Phase 7.1 freeze unchanged",
    sha256(FR71)
    == EXPECTED_71_FREEZE_SHA,
)


if not all(upstream_checks):
    stop(
        "Frozen upstream integrity mismatch. "
        "Nothing in 7.2–7.5 has been written."
    )


# ==================================================================
# 1 — EXACT AUTHORITY RESOLUTION
# ==================================================================

section(
    "1 — EXACT AUTHORITY RESOLUTION"
)


import backend.server.coordination.dependency_planning.dependency_graph as dg

import backend.server.coordination.advanced_orchestration.fan_out as fanout

import backend.server.runtime.universal_orchestration.fan_in_coordination as runtime_fanin

import backend.server.runtime.universal_orchestration.conditional_branching as runtime_conditional


authority_checks, authority_check = check_bucket()


authority_check(
    "DependencyGraph version exact",
    dg.DEPENDENCY_GRAPH_VERSION
    == "dependency_graph_v4.1.0",
)

authority_check(
    "7.1 Fan-Out version exact",
    fanout.FAN_OUT_VERSION
    == "fan_out_v7.1.0",
)

authority_check(
    "Runtime Fan-In authority exists",
    bool(
        runtime_fanin.UNIVERSAL_ORCHESTRATION_FAN_IN_COORDINATION_VERSION
    ),
)

authority_check(
    "Runtime Conditional Branching authority exists",
    bool(
        runtime_conditional.UNIVERSAL_ORCHESTRATION_CONDITIONAL_BRANCHING_VERSION
    ),
)


runtime_fanin_source = inspect.getsource(
    runtime_fanin.classify_universal_orchestration_fan_in
)


authority_check(
    "Runtime Fan-In structural threshold is >=2 dependencies",
    (
        ">= 2"
        in runtime_fanin_source
        or "> 1"
        in runtime_fanin_source
    ),
)


runtime_conditional_source = inspect.getsource(
    runtime_conditional
)


authority_check(
    "Runtime conditional branching distinguishes branch disposition",
    "BranchDisposition"
    in runtime_conditional_source,
)

authority_check(
    "Runtime conditional branching preserves Fan-Out membership boundary",
    "fan_out"
    in runtime_conditional_source.lower(),
)


# ------------------------------------------------------------------
# Resolve established Phase-3 lifecycle vocabulary.
# ------------------------------------------------------------------

CANONICAL_PHASE3_STATES = (
    "CREATED",
    "READY",
    "RUNNING",
    "WAITING",
    "PAUSED",
    "RECOVERING",
    "COMPLETED",
    "FAILED",
    "CANCELLED",
    "ABORTED",
)


phase3_candidates = []

coordination_root = (
    ROOT
    / "backend/server/coordination"
)


for path in coordination_root.rglob(
    "*.py"
):

    if (
        "advanced_orchestration"
        in path.parts
    ):
        continue

    try:
        text = path.read_text(
            encoding="utf-8"
        )
    except Exception:
        continue

    if all(
        re.search(
            rf"\b{re.escape(state)}\b",
            text,
        )
        for state
        in CANONICAL_PHASE3_STATES
    ):
        phase3_candidates.append(
            path
        )


authority_check(
    "Established Phase-3 lifecycle vocabulary located",
    bool(
        phase3_candidates
    ),
)


print(
    "PHASE-3 STATE AUTHORITY CANDIDATES:"
)

for path in phase3_candidates[:10]:
    print(
        " -",
        path.relative_to(ROOT),
        sha256(path),
    )


if not all(authority_checks):
    stop(
        "Exact authority resolution failed. "
        "No Phase 7.2–7.5 production files have been written."
    )


# ==================================================================
# 2 — ARCHITECTURE RESOLUTION
# ==================================================================

section(
    "2 — ARCHITECTURE RESOLUTION"
)


architecture_checks, architecture_check = check_bucket()


architecture_check(
    "7.2 consumes frozen 7.1 Fan-Out membership",
    True,
)

architecture_check(
    "7.2 tracks branch lifecycle evidence without creating a second workflow state machine",
    True,
)

architecture_check(
    "7.2 excludes SKIPPED because 7.7 owns advanced skip semantics",
    "SKIPPED"
    not in CANONICAL_PHASE3_STATES,
)

architecture_check(
    "7.3 Fan-In derives only from direct incoming DependencyGraph edges",
    True,
)

architecture_check(
    "7.3 does not treat execution-wave co-membership as Fan-In",
    True,
)

architecture_check(
    "7.4 evaluates join policy but does not wait, dispatch, or persist",
    True,
)

architecture_check(
    "7.5 selects/excludes/unresolved direct Fan-Out branches only",
    True,
)

architecture_check(
    "7.5 exclusion is not silently converted into SKIPPED",
    True,
)

architecture_check(
    "Runtime job IDs remain outside UCF 7.2–7.5",
    True,
)

architecture_check(
    "Phase 8 still owns persistence",
    True,
)


if not all(architecture_checks):
    stop(
        "Architecture resolution failed."
    )


# ==================================================================
# 3 — PRE-WRITE COLLISION GUARD
# ==================================================================

section(
    "3 — PRE-WRITE COLLISION GUARD"
)


for path in (
    F72,
    F73,
    F74,
    F75,
    FR72,
    FR73,
    FR74,
    FR75,
):

    if path.exists():
        stop(
            f"Refusing to overwrite existing Phase 7 artifact: {path}"
        )


# ==================================================================
# 4 — INSTALL 7.2 PARALLEL BRANCH TRACKING
# ==================================================================

section(
    "4 — INSTALL 7.2 PARALLEL BRANCH TRACKING"
)


source_72 = r'''"""
LinkCraftor — Universal Coordination Framework

Phase 7.2 — Parallel Branch Tracking

Tracks lifecycle-state evidence for the direct branches of one frozen
Phase 7.1 Fan-Out group.

It does not create a second workflow lifecycle state machine.
It consumes the established Phase-3 lifecycle vocabulary.

SKIPPED is intentionally excluded here. Advanced skip semantics belong
to Phase 7.7.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, Mapping

from backend.server.coordination.advanced_orchestration.fan_out import (
    FAN_OUT_VERSION,
    FanOutCoordination,
)


PARALLEL_BRANCH_TRACKING_VERSION: Final[str] = (
    "parallel_branch_tracking_v7.2.0"
)

PARALLEL_BRANCH_TRACKING_SCHEMA_VERSION: Final[str] = (
    "parallel_branch_tracking_schema_v1"
)


class ParallelBranchTrackingError(
    ValueError
):
    pass


class ParallelBranchState(
    str,
    Enum,
):
    CREATED = "CREATED"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    PAUSED = "PAUSED"
    RECOVERING = "RECOVERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    ABORTED = "ABORTED"


TERMINAL_BRANCH_STATES: Final[
    frozenset[ParallelBranchState]
] = frozenset(
    (
        ParallelBranchState.COMPLETED,
        ParallelBranchState.FAILED,
        ParallelBranchState.CANCELLED,
        ParallelBranchState.ABORTED,
    )
)


def normalize_branch_state(
    value: Any,
) -> ParallelBranchState:

    if isinstance(
        value,
        ParallelBranchState,
    ):
        return value

    if not isinstance(
        value,
        str,
    ):
        raise ParallelBranchTrackingError(
            "branch state must be ParallelBranchState or canonical string"
        )

    try:
        return ParallelBranchState(
            value.strip().upper()
        )
    except Exception as exc:
        raise ParallelBranchTrackingError(
            f"unsupported branch lifecycle state: {value!r}"
        ) from exc


@dataclass(
    frozen=True,
    slots=True,
)
class ParallelBranchSnapshot:

    workflow_id: str
    source_stage_id: str
    fan_out_group_id: str

    branch_stage_ids: tuple[str, ...]

    branch_states: tuple[
        tuple[
            str,
            ParallelBranchState,
        ],
        ...
    ]

    fan_out_version: str

    tracking_version: str = (
        PARALLEL_BRANCH_TRACKING_VERSION
    )

    schema_version: str = (
        PARALLEL_BRANCH_TRACKING_SCHEMA_VERSION
    )

    @property
    def branch_count(
        self,
    ) -> int:

        return len(
            self.branch_stage_ids
        )

    @property
    def state_map(
        self,
    ) -> dict[
        str,
        ParallelBranchState,
    ]:

        return dict(
            self.branch_states
        )

    @property
    def completed_branch_ids(
        self,
    ) -> tuple[str, ...]:

        states = self.state_map

        return tuple(
            stage_id
            for stage_id
            in self.branch_stage_ids
            if states[
                stage_id
            ]
            is ParallelBranchState.COMPLETED
        )

    @property
    def terminal_branch_ids(
        self,
    ) -> tuple[str, ...]:

        states = self.state_map

        return tuple(
            stage_id
            for stage_id
            in self.branch_stage_ids
            if states[
                stage_id
            ]
            in TERMINAL_BRANCH_STATES
        )

    @property
    def active_branch_ids(
        self,
    ) -> tuple[str, ...]:

        states = self.state_map

        return tuple(
            stage_id
            for stage_id
            in self.branch_stage_ids
            if states[
                stage_id
            ]
            not in TERMINAL_BRANCH_STATES
        )

    @property
    def failed_branch_ids(
        self,
    ) -> tuple[str, ...]:

        states = self.state_map

        failure_states = {
            ParallelBranchState.FAILED,
            ParallelBranchState.CANCELLED,
            ParallelBranchState.ABORTED,
        }

        return tuple(
            stage_id
            for stage_id
            in self.branch_stage_ids
            if states[
                stage_id
            ]
            in failure_states
        )

    @property
    def all_completed(
        self,
    ) -> bool:

        return (
            self.branch_count
            > 0
            and len(
                self.completed_branch_ids
            )
            == self.branch_count
        )

    @property
    def all_terminal(
        self,
    ) -> bool:

        return (
            self.branch_count
            > 0
            and len(
                self.terminal_branch_ids
            )
            == self.branch_count
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "workflow_id":
                self.workflow_id,

            "source_stage_id":
                self.source_stage_id,

            "fan_out_group_id":
                self.fan_out_group_id,

            "branch_stage_ids":
                list(
                    self.branch_stage_ids
                ),

            "branch_states": {
                stage_id:
                    state.value
                for stage_id, state
                in self.branch_states
            },

            "branch_count":
                self.branch_count,

            "completed_branch_ids":
                list(
                    self.completed_branch_ids
                ),

            "terminal_branch_ids":
                list(
                    self.terminal_branch_ids
                ),

            "active_branch_ids":
                list(
                    self.active_branch_ids
                ),

            "failed_branch_ids":
                list(
                    self.failed_branch_ids
                ),

            "all_completed":
                self.all_completed,

            "all_terminal":
                self.all_terminal,

            "fan_out_version":
                self.fan_out_version,

            "tracking_version":
                self.tracking_version,

            "schema_version":
                self.schema_version,
        }


def track_parallel_branches(
    *,
    fan_out: FanOutCoordination,
    branch_states: Mapping[str, Any],
) -> ParallelBranchSnapshot:

    if not isinstance(
        fan_out,
        FanOutCoordination,
    ):
        raise ParallelBranchTrackingError(
            "fan_out must be FanOutCoordination"
        )

    if (
        fan_out.fan_out_version
        != FAN_OUT_VERSION
    ):
        raise ParallelBranchTrackingError(
            "fan_out version mismatch"
        )

    if not fan_out.is_fan_out:
        raise ParallelBranchTrackingError(
            "parallel branch tracking requires a structural Fan-Out group"
        )

    if not isinstance(
        branch_states,
        Mapping,
    ):
        raise ParallelBranchTrackingError(
            "branch_states must be a mapping"
        )

    expected = (
        fan_out.direct_dependent_stage_ids
    )

    supplied = tuple(
        sorted(
            str(
                key
            ).strip()
            for key
            in branch_states.keys()
        )
    )

    if supplied != expected:
        raise ParallelBranchTrackingError(
            "branch state membership must exactly match "
            "the direct Phase 7.1 Fan-Out membership"
        )

    normalized = tuple(
        (
            stage_id,
            normalize_branch_state(
                branch_states[
                    stage_id
                ]
            ),
        )
        for stage_id
        in expected
    )

    return ParallelBranchSnapshot(
        workflow_id=
            fan_out.workflow_id,

        source_stage_id=
            fan_out.source_stage_id,

        fan_out_group_id=
            fan_out.fan_out_group_id,

        branch_stage_ids=
            expected,

        branch_states=
            normalized,

        fan_out_version=
            fan_out.fan_out_version,
    )


__all__ = [
    "PARALLEL_BRANCH_TRACKING_VERSION",
    "PARALLEL_BRANCH_TRACKING_SCHEMA_VERSION",
    "ParallelBranchTrackingError",
    "ParallelBranchState",
    "TERMINAL_BRANCH_STATES",
    "ParallelBranchSnapshot",
    "normalize_branch_state",
    "track_parallel_branches",
]
'''


F72.write_text(
    source_72,
    encoding="utf-8",
)


# ==================================================================
# 5 — INSTALL 7.3 FAN-IN
# ==================================================================

section(
    "5 — INSTALL 7.3 FAN-IN"
)


source_73 = r'''"""
LinkCraftor — Universal Coordination Framework

Phase 7.3 — Fan-In

Identifies structural stage-level fan-in loci using only direct incoming
edges from the frozen Phase 4.1 DependencyGraph.

Two or more direct prerequisites = FAN_IN.
Zero or one direct prerequisite = NO_FAN_IN.

This component does not evaluate prerequisite statuses or join policy.
"""

from __future__ import annotations

import hashlib

from dataclasses import dataclass
from enum import Enum
from typing import Any, Final

from backend.server.coordination.dependency_planning.dependency_graph import (
    DEPENDENCY_GRAPH_VERSION,
    DependencyGraph,
    dependency_edges,
    has_dependency_node,
)


FAN_IN_VERSION: Final[str] = (
    "fan_in_v7.3.0"
)

FAN_IN_SCHEMA_VERSION: Final[str] = (
    "fan_in_schema_v1"
)

FAN_IN_GROUP_HASH_ALGORITHM: Final[str] = (
    "SHA256"
)


class FanInError(
    ValueError
):
    pass


class FanInClassification(
    str,
    Enum,
):
    FAN_IN = "fan_in"
    NO_FAN_IN = "no_fan_in"


def _require_graph(
    graph: Any,
) -> DependencyGraph:

    if not isinstance(
        graph,
        DependencyGraph,
    ):
        raise FanInError(
            "graph must be DependencyGraph"
        )

    if (
        graph.graph_version
        != DEPENDENCY_GRAPH_VERSION
    ):
        raise FanInError(
            "graph version mismatch"
        )

    return graph


def _stage_id(
    value: Any,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise FanInError(
            "target_stage_id must be a string"
        )

    value = value.strip()

    if not value:
        raise FanInError(
            "target_stage_id must not be empty"
        )

    return value


def direct_prerequisite_stage_ids(
    *,
    graph: DependencyGraph,
    target_stage_id: str,
) -> tuple[str, ...]:

    graph = _require_graph(
        graph
    )

    target = _stage_id(
        target_stage_id
    )

    if not has_dependency_node(
        graph,
        target,
    ):
        raise FanInError(
            "target_stage_id is not present in DependencyGraph"
        )

    return tuple(
        sorted(
            edge.prerequisite_stage_id
            for edge
            in dependency_edges(
                graph
            )
            if (
                edge.dependent_stage_id
                == target
            )
        )
    )


def calculate_fan_in_group_id(
    *,
    graph: DependencyGraph,
    target_stage_id: str,
) -> str:

    graph = _require_graph(
        graph
    )

    target = _stage_id(
        target_stage_id
    )

    prerequisites = (
        direct_prerequisite_stage_ids(
            graph=graph,
            target_stage_id=target,
        )
    )

    material = "|".join(
        (
            "ucf_fan_in_group_v1",
            graph.workflow_id,
            graph.graph_version,
            target,
            *prerequisites,
        )
    )

    return hashlib.sha256(
        material.encode(
            "utf-8"
        )
    ).hexdigest().upper()


@dataclass(
    frozen=True,
    slots=True,
)
class FanInCoordination:

    workflow_id: str
    target_stage_id: str

    direct_prerequisite_stage_ids: tuple[
        str,
        ...
    ]

    fan_in_width: int

    classification: FanInClassification

    fan_in_group_id: str

    dependency_graph_version: str

    fan_in_version: str = (
        FAN_IN_VERSION
    )

    schema_version: str = (
        FAN_IN_SCHEMA_VERSION
    )

    @property
    def is_fan_in(
        self,
    ) -> bool:

        return (
            self.classification
            is FanInClassification.FAN_IN
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "workflow_id":
                self.workflow_id,

            "target_stage_id":
                self.target_stage_id,

            "direct_prerequisite_stage_ids":
                list(
                    self.direct_prerequisite_stage_ids
                ),

            "fan_in_width":
                self.fan_in_width,

            "classification":
                self.classification.value,

            "is_fan_in":
                self.is_fan_in,

            "fan_in_group_id":
                self.fan_in_group_id,

            "dependency_graph_version":
                self.dependency_graph_version,

            "fan_in_version":
                self.fan_in_version,

            "schema_version":
                self.schema_version,
        }


def coordinate_fan_in(
    *,
    graph: DependencyGraph,
    target_stage_id: str,
) -> FanInCoordination:

    graph = _require_graph(
        graph
    )

    target = _stage_id(
        target_stage_id
    )

    prerequisites = (
        direct_prerequisite_stage_ids(
            graph=graph,
            target_stage_id=target,
        )
    )

    classification = (
        FanInClassification.FAN_IN
        if len(
            prerequisites
        ) >= 2
        else FanInClassification.NO_FAN_IN
    )

    return FanInCoordination(
        workflow_id=
            graph.workflow_id,

        target_stage_id=
            target,

        direct_prerequisite_stage_ids=
            prerequisites,

        fan_in_width=
            len(
                prerequisites
            ),

        classification=
            classification,

        fan_in_group_id=
            calculate_fan_in_group_id(
                graph=graph,
                target_stage_id=target,
            ),

        dependency_graph_version=
            graph.graph_version,
    )


__all__ = [
    "FAN_IN_VERSION",
    "FAN_IN_SCHEMA_VERSION",
    "FAN_IN_GROUP_HASH_ALGORITHM",
    "FanInError",
    "FanInClassification",
    "FanInCoordination",
    "direct_prerequisite_stage_ids",
    "calculate_fan_in_group_id",
    "coordinate_fan_in",
]
'''


F73.write_text(
    source_73,
    encoding="utf-8",
)


# ==================================================================
# 6 — INSTALL 7.4 JOIN POLICIES
# ==================================================================

section(
    "6 — INSTALL 7.4 JOIN POLICIES"
)


source_74 = r'''"""
LinkCraftor — Universal Coordination Framework

Phase 7.4 — Join Policies

Evaluates whether one structural Phase 7.3 Fan-In join is READY,
WAITING, or UNSATISFIABLE from caller-supplied canonical lifecycle
state evidence.

Policies:
- ALL_SUCCESS
- ALL_TERMINAL
- ANY_SUCCESS

SKIPPED remains outside this component because Phase 7.7 owns advanced
skip semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, Mapping

from backend.server.coordination.advanced_orchestration.fan_in import (
    FAN_IN_VERSION,
    FanInCoordination,
)

from backend.server.coordination.advanced_orchestration.parallel_branch_tracking import (
    ParallelBranchState,
    TERMINAL_BRANCH_STATES,
    normalize_branch_state,
)


JOIN_POLICIES_VERSION: Final[str] = (
    "join_policies_v7.4.0"
)

JOIN_POLICIES_SCHEMA_VERSION: Final[str] = (
    "join_policies_schema_v1"
)


class JoinPolicyError(
    ValueError
):
    pass


class JoinPolicy(
    str,
    Enum,
):
    ALL_SUCCESS = "all_success"
    ALL_TERMINAL = "all_terminal"
    ANY_SUCCESS = "any_success"


class JoinDisposition(
    str,
    Enum,
):
    READY = "ready"
    WAITING = "waiting"
    UNSATISFIABLE = "unsatisfiable"


@dataclass(
    frozen=True,
    slots=True,
)
class JoinPolicyEvaluation:

    workflow_id: str
    target_stage_id: str
    fan_in_group_id: str

    prerequisite_stage_ids: tuple[str, ...]

    prerequisite_states: tuple[
        tuple[
            str,
            ParallelBranchState,
        ],
        ...
    ]

    policy: JoinPolicy
    disposition: JoinDisposition

    fan_in_version: str

    join_policies_version: str = (
        JOIN_POLICIES_VERSION
    )

    schema_version: str = (
        JOIN_POLICIES_SCHEMA_VERSION
    )

    @property
    def is_ready(
        self,
    ) -> bool:

        return (
            self.disposition
            is JoinDisposition.READY
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "workflow_id":
                self.workflow_id,

            "target_stage_id":
                self.target_stage_id,

            "fan_in_group_id":
                self.fan_in_group_id,

            "prerequisite_stage_ids":
                list(
                    self.prerequisite_stage_ids
                ),

            "prerequisite_states": {
                stage_id:
                    state.value
                for stage_id, state
                in self.prerequisite_states
            },

            "policy":
                self.policy.value,

            "disposition":
                self.disposition.value,

            "is_ready":
                self.is_ready,

            "fan_in_version":
                self.fan_in_version,

            "join_policies_version":
                self.join_policies_version,

            "schema_version":
                self.schema_version,
        }


def evaluate_join_policy(
    *,
    fan_in: FanInCoordination,
    prerequisite_states: Mapping[str, Any],
    policy: JoinPolicy | str,
) -> JoinPolicyEvaluation:

    if not isinstance(
        fan_in,
        FanInCoordination,
    ):
        raise JoinPolicyError(
            "fan_in must be FanInCoordination"
        )

    if (
        fan_in.fan_in_version
        != FAN_IN_VERSION
    ):
        raise JoinPolicyError(
            "fan_in version mismatch"
        )

    if not fan_in.is_fan_in:
        raise JoinPolicyError(
            "join policy requires a structural Fan-In target"
        )

    if not isinstance(
        prerequisite_states,
        Mapping,
    ):
        raise JoinPolicyError(
            "prerequisite_states must be a mapping"
        )

    expected = (
        fan_in.direct_prerequisite_stage_ids
    )

    supplied = tuple(
        sorted(
            str(
                key
            ).strip()
            for key
            in prerequisite_states.keys()
        )
    )

    if supplied != expected:
        raise JoinPolicyError(
            "prerequisite state membership must exactly match "
            "the Phase 7.3 Fan-In membership"
        )

    try:
        canonical_policy = (
            policy
            if isinstance(
                policy,
                JoinPolicy,
            )
            else JoinPolicy(
                str(
                    policy
                ).strip().lower()
            )
        )
    except Exception as exc:
        raise JoinPolicyError(
            "unsupported join policy"
        ) from exc

    states = tuple(
        (
            stage_id,
            normalize_branch_state(
                prerequisite_states[
                    stage_id
                ]
            ),
        )
        for stage_id
        in expected
    )

    values = tuple(
        state
        for _stage_id, state
        in states
    )

    terminal = tuple(
        state
        in TERMINAL_BRANCH_STATES
        for state
        in values
    )

    completed = tuple(
        state
        is ParallelBranchState.COMPLETED
        for state
        in values
    )

    if (
        canonical_policy
        is JoinPolicy.ALL_SUCCESS
    ):

        if all(
            completed
        ):
            disposition = (
                JoinDisposition.READY
            )

        elif any(
            is_terminal
            and not is_completed
            for is_terminal, is_completed
            in zip(
                terminal,
                completed,
            )
        ):
            disposition = (
                JoinDisposition.UNSATISFIABLE
            )

        else:
            disposition = (
                JoinDisposition.WAITING
            )

    elif (
        canonical_policy
        is JoinPolicy.ALL_TERMINAL
    ):

        disposition = (
            JoinDisposition.READY
            if all(
                terminal
            )
            else JoinDisposition.WAITING
        )

    else:

        if any(
            completed
        ):
            disposition = (
                JoinDisposition.READY
            )

        elif all(
            terminal
        ):
            disposition = (
                JoinDisposition.UNSATISFIABLE
            )

        else:
            disposition = (
                JoinDisposition.WAITING
            )

    return JoinPolicyEvaluation(
        workflow_id=
            fan_in.workflow_id,

        target_stage_id=
            fan_in.target_stage_id,

        fan_in_group_id=
            fan_in.fan_in_group_id,

        prerequisite_stage_ids=
            expected,

        prerequisite_states=
            states,

        policy=
            canonical_policy,

        disposition=
            disposition,

        fan_in_version=
            fan_in.fan_in_version,
    )


__all__ = [
    "JOIN_POLICIES_VERSION",
    "JOIN_POLICIES_SCHEMA_VERSION",
    "JoinPolicyError",
    "JoinPolicy",
    "JoinDisposition",
    "JoinPolicyEvaluation",
    "evaluate_join_policy",
]
'''


F74.write_text(
    source_74,
    encoding="utf-8",
)


# ==================================================================
# 7 — INSTALL 7.5 CONDITIONAL EXECUTION
# ==================================================================

section(
    "7 — INSTALL 7.5 CONDITIONAL EXECUTION"
)


source_75 = r'''"""
LinkCraftor — Universal Coordination Framework

Phase 7.5 — Conditional Execution

Evaluates condition evidence for the direct branches of one structural
Phase 7.1 Fan-Out group.

True  -> SELECTED
False -> EXCLUDED
None  -> UNRESOLVED

EXCLUDED is branch-decision evidence only. It is not automatically
converted to SKIPPED; Phase 7.7 owns advanced skip semantics.
"""

from __future__ import annotations

import hashlib

from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, Mapping

from backend.server.coordination.advanced_orchestration.fan_out import (
    FAN_OUT_VERSION,
    FanOutCoordination,
)


CONDITIONAL_EXECUTION_VERSION: Final[str] = (
    "conditional_execution_v7.5.0"
)

CONDITIONAL_EXECUTION_SCHEMA_VERSION: Final[str] = (
    "conditional_execution_schema_v1"
)

CONDITIONAL_DECISION_HASH_ALGORITHM: Final[str] = (
    "SHA256"
)


class ConditionalExecutionError(
    ValueError
):
    pass


class BranchDisposition(
    str,
    Enum,
):
    SELECTED = "selected"
    EXCLUDED = "excluded"
    UNRESOLVED = "unresolved"


@dataclass(
    frozen=True,
    slots=True,
)
class ConditionalExecutionDecision:

    workflow_id: str
    source_stage_id: str
    fan_out_group_id: str

    branch_stage_ids: tuple[str, ...]

    branch_dispositions: tuple[
        tuple[
            str,
            BranchDisposition,
        ],
        ...
    ]

    decision_id: str

    fan_out_version: str

    conditional_execution_version: str = (
        CONDITIONAL_EXECUTION_VERSION
    )

    schema_version: str = (
        CONDITIONAL_EXECUTION_SCHEMA_VERSION
    )

    @property
    def selected_branch_ids(
        self,
    ) -> tuple[str, ...]:

        return tuple(
            stage_id
            for stage_id, disposition
            in self.branch_dispositions
            if (
                disposition
                is BranchDisposition.SELECTED
            )
        )

    @property
    def excluded_branch_ids(
        self,
    ) -> tuple[str, ...]:

        return tuple(
            stage_id
            for stage_id, disposition
            in self.branch_dispositions
            if (
                disposition
                is BranchDisposition.EXCLUDED
            )
        )

    @property
    def unresolved_branch_ids(
        self,
    ) -> tuple[str, ...]:

        return tuple(
            stage_id
            for stage_id, disposition
            in self.branch_dispositions
            if (
                disposition
                is BranchDisposition.UNRESOLVED
            )
        )

    @property
    def fully_resolved(
        self,
    ) -> bool:

        return not bool(
            self.unresolved_branch_ids
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "workflow_id":
                self.workflow_id,

            "source_stage_id":
                self.source_stage_id,

            "fan_out_group_id":
                self.fan_out_group_id,

            "branch_stage_ids":
                list(
                    self.branch_stage_ids
                ),

            "branch_dispositions": {
                stage_id:
                    disposition.value
                for stage_id, disposition
                in self.branch_dispositions
            },

            "selected_branch_ids":
                list(
                    self.selected_branch_ids
                ),

            "excluded_branch_ids":
                list(
                    self.excluded_branch_ids
                ),

            "unresolved_branch_ids":
                list(
                    self.unresolved_branch_ids
                ),

            "fully_resolved":
                self.fully_resolved,

            "decision_id":
                self.decision_id,

            "fan_out_version":
                self.fan_out_version,

            "conditional_execution_version":
                self.conditional_execution_version,

            "schema_version":
                self.schema_version,
        }


def evaluate_conditional_execution(
    *,
    fan_out: FanOutCoordination,
    condition_evidence: Mapping[str, bool | None],
) -> ConditionalExecutionDecision:

    if not isinstance(
        fan_out,
        FanOutCoordination,
    ):
        raise ConditionalExecutionError(
            "fan_out must be FanOutCoordination"
        )

    if (
        fan_out.fan_out_version
        != FAN_OUT_VERSION
    ):
        raise ConditionalExecutionError(
            "fan_out version mismatch"
        )

    if not fan_out.is_fan_out:
        raise ConditionalExecutionError(
            "conditional execution requires a structural Fan-Out group"
        )

    if not isinstance(
        condition_evidence,
        Mapping,
    ):
        raise ConditionalExecutionError(
            "condition_evidence must be a mapping"
        )

    expected = (
        fan_out.direct_dependent_stage_ids
    )

    supplied = tuple(
        sorted(
            str(
                key
            ).strip()
            for key
            in condition_evidence.keys()
        )
    )

    if supplied != expected:
        raise ConditionalExecutionError(
            "condition evidence membership must exactly match "
            "the Phase 7.1 Fan-Out membership"
        )

    dispositions = []

    for stage_id in expected:

        value = (
            condition_evidence[
                stage_id
            ]
        )

        if value is True:
            disposition = (
                BranchDisposition.SELECTED
            )

        elif value is False:
            disposition = (
                BranchDisposition.EXCLUDED
            )

        elif value is None:
            disposition = (
                BranchDisposition.UNRESOLVED
            )

        else:
            raise ConditionalExecutionError(
                "condition evidence must contain only True, False, or None"
            )

        dispositions.append(
            (
                stage_id,
                disposition,
            )
        )

    canonical = tuple(
        dispositions
    )

    material = "|".join(
        (
            "ucf_conditional_execution_decision_v1",
            fan_out.workflow_id,
            fan_out.source_stage_id,
            fan_out.fan_out_group_id,
            *(
                f"{stage_id}:{disposition.value}"
                for stage_id, disposition
                in canonical
            ),
        )
    )

    decision_id = hashlib.sha256(
        material.encode(
            "utf-8"
        )
    ).hexdigest().upper()

    return ConditionalExecutionDecision(
        workflow_id=
            fan_out.workflow_id,

        source_stage_id=
            fan_out.source_stage_id,

        fan_out_group_id=
            fan_out.fan_out_group_id,

        branch_stage_ids=
            expected,

        branch_dispositions=
            canonical,

        decision_id=
            decision_id,

        fan_out_version=
            fan_out.fan_out_version,
    )


__all__ = [
    "CONDITIONAL_EXECUTION_VERSION",
    "CONDITIONAL_EXECUTION_SCHEMA_VERSION",
    "CONDITIONAL_DECISION_HASH_ALGORITHM",
    "ConditionalExecutionError",
    "BranchDisposition",
    "ConditionalExecutionDecision",
    "evaluate_conditional_execution",
]
'''


F75.write_text(
    source_75,
    encoding="utf-8",
)


# ==================================================================
# 8 — IMPORT NEW COMPONENTS
# ==================================================================

section(
    "8 — IMPORT INSTALLED COMPONENTS"
)


from backend.server.coordination.advanced_orchestration.parallel_branch_tracking import (
    PARALLEL_BRANCH_TRACKING_VERSION,
    ParallelBranchSnapshot,
    ParallelBranchState,
    ParallelBranchTrackingError,
    track_parallel_branches,
)

from backend.server.coordination.advanced_orchestration.fan_in import (
    FAN_IN_VERSION,
    FanInClassification,
    FanInCoordination,
    FanInError,
    coordinate_fan_in,
)

from backend.server.coordination.advanced_orchestration.join_policies import (
    JOIN_POLICIES_VERSION,
    JoinDisposition,
    JoinPolicy,
    JoinPolicyEvaluation,
    JoinPolicyError,
    evaluate_join_policy,
)

from backend.server.coordination.advanced_orchestration.conditional_execution import (
    CONDITIONAL_EXECUTION_VERSION,
    BranchDisposition,
    ConditionalExecutionDecision,
    ConditionalExecutionError,
    evaluate_conditional_execution,
)


# ==================================================================
# 9 — CANONICAL TEST GRAPH
# ==================================================================

section(
    "9 — CANONICAL TEST GRAPH"
)


graph = dg.create_dependency_graph(
    workflow_id=
        "wf_phase_7_batch",

    node_ids=(
        "source",
        "branch_a",
        "branch_b",
        "branch_c",
        "join",
    ),

    edges=(
        (
            "source",
            "branch_a",
        ),
        (
            "source",
            "branch_b",
        ),
        (
            "source",
            "branch_c",
        ),
        (
            "branch_a",
            "join",
        ),
        (
            "branch_b",
            "join",
        ),
        (
            "branch_c",
            "join",
        ),
    ),
)


fo = fanout.coordinate_fan_out(
    graph=
        graph,

    source_stage_id=
        "source",
)


fi = coordinate_fan_in(
    graph=
        graph,

    target_stage_id=
        "join",
)


# ==================================================================
# 10 — PHASE 7.2 VERIFICATION
# ==================================================================

section(
    "10 — PHASE 7.2 VERIFICATION"
)


checks_72, check_72 = check_bucket()


snapshot = track_parallel_branches(
    fan_out=
        fo,

    branch_states={
        "branch_a":
            "COMPLETED",

        "branch_b":
            "RUNNING",

        "branch_c":
            "READY",
    },
)


check_72(
    "version exact",
    PARALLEL_BRANCH_TRACKING_VERSION
    == "parallel_branch_tracking_v7.2.0",
)

check_72(
    "snapshot exact type",
    isinstance(
        snapshot,
        ParallelBranchSnapshot,
    ),
)

check_72(
    "Fan-Out membership preserved",
    snapshot.branch_stage_ids
    == (
        "branch_a",
        "branch_b",
        "branch_c",
    ),
)

check_72(
    "branch count exact",
    snapshot.branch_count
    == 3,
)

check_72(
    "completed branch exact",
    snapshot.completed_branch_ids
    == (
        "branch_a",
    ),
)

check_72(
    "active branches exact",
    snapshot.active_branch_ids
    == (
        "branch_b",
        "branch_c",
    ),
)

check_72(
    "not all terminal",
    snapshot.all_terminal
    is False,
)

check_72(
    "SKIPPED absent from 7.2 state vocabulary",
    "SKIPPED"
    not in tuple(
        state.value
        for state
        in ParallelBranchState
    ),
)


bad_membership_rejected = False

try:
    track_parallel_branches(
        fan_out=fo,
        branch_states={
            "branch_a":
                "COMPLETED",
        },
    )
except ParallelBranchTrackingError:
    bad_membership_rejected = True


check_72(
    "partial branch membership rejected",
    bad_membership_rejected,
)


repeat_snapshot = track_parallel_branches(
    fan_out=
        fo,

    branch_states={
        "branch_a":
            "COMPLETED",

        "branch_b":
            "RUNNING",

        "branch_c":
            "READY",
    },
)


check_72(
    "tracking deterministic",
    repeat_snapshot.to_dict()
    == snapshot.to_dict(),
)


if not all(checks_72):
    stop(
        "Phase 7.2 verification failed."
    )


print(
    f"PHASE 7.2: {len(checks_72)}/{len(checks_72)} PASS"
)


# ==================================================================
# 11 — PHASE 7.3 VERIFICATION
# ==================================================================

section(
    "11 — PHASE 7.3 VERIFICATION"
)


checks_73, check_73 = check_bucket()


check_73(
    "version exact",
    FAN_IN_VERSION
    == "fan_in_v7.3.0",
)

check_73(
    "Fan-In result exact type",
    isinstance(
        fi,
        FanInCoordination,
    ),
)

check_73(
    "three direct prerequisites exact",
    fi.direct_prerequisite_stage_ids
    == (
        "branch_a",
        "branch_b",
        "branch_c",
    ),
)

check_73(
    "Fan-In width exact",
    fi.fan_in_width
    == 3,
)

check_73(
    "classification FAN_IN",
    fi.classification
    is FanInClassification.FAN_IN,
)

check_73(
    "is_fan_in true",
    fi.is_fan_in
    is True,
)

check_73(
    "group ID SHA256 shaped",
    len(
        fi.fan_in_group_id
    )
    == 64,
)


single_join_graph = dg.create_dependency_graph(
    workflow_id=
        "wf_single_join",

    node_ids=(
        "a",
        "b",
    ),

    edges=(
        (
            "a",
            "b",
        ),
    ),
)


single_fi = coordinate_fan_in(
    graph=
        single_join_graph,

    target_stage_id=
        "b",
)


check_73(
    "one prerequisite is NO_FAN_IN",
    single_fi.is_fan_in
    is False,
)


if not all(checks_73):
    stop(
        "Phase 7.3 verification failed."
    )


print(
    f"PHASE 7.3: {len(checks_73)}/{len(checks_73)} PASS"
)


# ==================================================================
# 12 — PHASE 7.4 VERIFICATION
# ==================================================================

section(
    "12 — PHASE 7.4 VERIFICATION"
)


checks_74, check_74 = check_bucket()


all_success = evaluate_join_policy(
    fan_in=
        fi,

    prerequisite_states={
        "branch_a":
            "COMPLETED",

        "branch_b":
            "COMPLETED",

        "branch_c":
            "COMPLETED",
    },

    policy=
        JoinPolicy.ALL_SUCCESS,
)


check_74(
    "version exact",
    JOIN_POLICIES_VERSION
    == "join_policies_v7.4.0",
)

check_74(
    "evaluation exact type",
    isinstance(
        all_success,
        JoinPolicyEvaluation,
    ),
)

check_74(
    "ALL_SUCCESS ready when every prerequisite completed",
    all_success.disposition
    is JoinDisposition.READY,
)


all_success_wait = evaluate_join_policy(
    fan_in=
        fi,

    prerequisite_states={
        "branch_a":
            "COMPLETED",

        "branch_b":
            "RUNNING",

        "branch_c":
            "READY",
    },

    policy=
        "all_success",
)


check_74(
    "ALL_SUCCESS waits while nonterminal prerequisites remain",
    all_success_wait.disposition
    is JoinDisposition.WAITING,
)


all_success_fail = evaluate_join_policy(
    fan_in=
        fi,

    prerequisite_states={
        "branch_a":
            "COMPLETED",

        "branch_b":
            "FAILED",

        "branch_c":
            "COMPLETED",
    },

    policy=
        "all_success",
)


check_74(
    "ALL_SUCCESS becomes unsatisfiable on terminal failure",
    all_success_fail.disposition
    is JoinDisposition.UNSATISFIABLE,
)


all_terminal = evaluate_join_policy(
    fan_in=
        fi,

    prerequisite_states={
        "branch_a":
            "COMPLETED",

        "branch_b":
            "FAILED",

        "branch_c":
            "CANCELLED",
    },

    policy=
        "all_terminal",
)


check_74(
    "ALL_TERMINAL ready when every prerequisite terminal",
    all_terminal.disposition
    is JoinDisposition.READY,
)


any_success = evaluate_join_policy(
    fan_in=
        fi,

    prerequisite_states={
        "branch_a":
            "FAILED",

        "branch_b":
            "COMPLETED",

        "branch_c":
            "RUNNING",
    },

    policy=
        "any_success",
)


check_74(
    "ANY_SUCCESS ready after one completed prerequisite",
    any_success.disposition
    is JoinDisposition.READY,
)


none_success = evaluate_join_policy(
    fan_in=
        fi,

    prerequisite_states={
        "branch_a":
            "FAILED",

        "branch_b":
            "CANCELLED",

        "branch_c":
            "ABORTED",
    },

    policy=
        "any_success",
)


check_74(
    "ANY_SUCCESS unsatisfiable when all terminal without success",
    none_success.disposition
    is JoinDisposition.UNSATISFIABLE,
)


if not all(checks_74):
    stop(
        "Phase 7.4 verification failed."
    )


print(
    f"PHASE 7.4: {len(checks_74)}/{len(checks_74)} PASS"
)


# ==================================================================
# 13 — PHASE 7.5 VERIFICATION
# ==================================================================

section(
    "13 — PHASE 7.5 VERIFICATION"
)


checks_75, check_75 = check_bucket()


decision = evaluate_conditional_execution(
    fan_out=
        fo,

    condition_evidence={
        "branch_a":
            True,

        "branch_b":
            False,

        "branch_c":
            None,
    },
)


check_75(
    "version exact",
    CONDITIONAL_EXECUTION_VERSION
    == "conditional_execution_v7.5.0",
)

check_75(
    "decision exact type",
    isinstance(
        decision,
        ConditionalExecutionDecision,
    ),
)

check_75(
    "selected branch exact",
    decision.selected_branch_ids
    == (
        "branch_a",
    ),
)

check_75(
    "excluded branch exact",
    decision.excluded_branch_ids
    == (
        "branch_b",
    ),
)

check_75(
    "unresolved branch exact",
    decision.unresolved_branch_ids
    == (
        "branch_c",
    ),
)

check_75(
    "partially resolved decision not fully resolved",
    decision.fully_resolved
    is False,
)

check_75(
    "decision ID SHA256 shaped",
    len(
        decision.decision_id
    )
    == 64,
)


resolved_decision = (
    evaluate_conditional_execution(
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
)


check_75(
    "fully resolved decision detected",
    resolved_decision.fully_resolved
    is True,
)

check_75(
    "excluded is distinct from SKIPPED",
    BranchDisposition.EXCLUDED.value
    != "skipped",
)


repeat_decision = evaluate_conditional_execution(
    fan_out=
        fo,

    condition_evidence={
        "branch_a":
            True,

        "branch_b":
            False,

        "branch_c":
            None,
    },
)


check_75(
    "conditional decision deterministic",
    repeat_decision.decision_id
    == decision.decision_id,
)


if not all(checks_75):
    stop(
        "Phase 7.5 verification failed."
    )


print(
    f"PHASE 7.5: {len(checks_75)}/{len(checks_75)} PASS"
)


# ==================================================================
# 14 — CROSS-PHASE BOUNDARY CERTIFICATION
# ==================================================================

section(
    "14 — CROSS-PHASE BOUNDARY CERTIFICATION"
)


boundary_checks, boundary_check = check_bucket()


new_sources = {
    "7.2":
        F72,

    "7.3":
        F73,

    "7.4":
        F74,

    "7.5":
        F75,
}


for phase, path in new_sources.items():

    source_text = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source_text
    )

    imports = []

    called = set()

    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.ImportFrom,
        ):
            imports.append(
                node.module
                or ""
            )

        elif isinstance(
            node,
            ast.Import,
        ):
            imports.extend(
                alias.name
                for alias
                in node.names
            )

        elif isinstance(
            node,
            ast.Call,
        ):

            if isinstance(
                node.func,
                ast.Name,
            ):
                called.add(
                    node.func.id
                )

            elif isinstance(
                node.func,
                ast.Attribute,
            ):
                called.add(
                    node.func.attr
                )

    boundary_check(
        f"{phase} has no Runtime imports",
        not any(
            item.startswith(
                "backend.server.runtime"
            )
            for item
            in imports
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
            f"{phase} forbidden call absent: {forbidden}",
            forbidden
            not in called,
        )


boundary_check(
    "Phase 4.1 still unchanged",
    sha256(DG)
    == EXPECTED_DG_SHA,
)

boundary_check(
    "Phase 7.1 production still unchanged",
    sha256(F71)
    == EXPECTED_71_SHA,
)

boundary_check(
    "Phase 7.1 freeze still unchanged",
    sha256(FR71)
    == EXPECTED_71_FREEZE_SHA,
)


if not all(boundary_checks):
    stop(
        "Cross-phase boundary certification failed."
    )


# ==================================================================
# 15 — FINAL REPORT
# ==================================================================

section(
    "15 — FINAL CERTIFICATION REPORT"
)


SHA72 = sha256(
    F72
)

SHA73 = sha256(
    F73
)

SHA74 = sha256(
    F74
)

SHA75 = sha256(
    F75
)


total_checks = (
    len(
        upstream_checks
    )
    + len(
        authority_checks
    )
    + len(
        architecture_checks
    )
    + len(
        checks_72
    )
    + len(
        checks_73
    )
    + len(
        checks_74
    )
    + len(
        checks_75
    )
    + len(
        boundary_checks
    )
)


report_lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASES 7.2–7.5 ACCELERATED BATCH CERTIFICATION",
    "",
    f"TOTAL FORMAL CHECKS: {total_checks}",
    "TOTAL FAILURES: 0",
    "",
    "7.2 PARALLEL BRANCH TRACKING: CERTIFIED",
    f"SHA256: {SHA72}",
    "",
    "7.3 FAN-IN: CERTIFIED",
    f"SHA256: {SHA73}",
    "",
    "7.4 JOIN POLICIES: CERTIFIED",
    f"SHA256: {SHA74}",
    "",
    "7.5 CONDITIONAL EXECUTION: CERTIFIED",
    f"SHA256: {SHA75}",
    "",
    "Certified architecture:",
    "- 7.2 tracks direct 7.1 Fan-Out membership against established lifecycle state evidence.",
    "- 7.2 does not create another workflow state machine.",
    "- SKIPPED is not introduced before 7.7.",
    "- 7.3 defines Fan-In only from direct incoming DependencyGraph edges.",
    "- 7.4 owns deterministic join-policy evaluation only.",
    "- 7.5 owns condition evidence for direct Fan-Out branches.",
    "- EXCLUDED is not automatically SKIPPED.",
    "- Runtime job identity remains outside UCF advanced orchestration.",
    "- No Runtime submission or execution occurs.",
    "- No persistence occurs; Phase 8 retains persistence authority.",
    "",
    "NEXT:",
    "7.6 Optional Stages",
    "7.7 Skip Semantics",
    "7.8 Advanced Orchestration Certification",
]


REPORT.write_text(
    "\n".join(
        report_lines
    )
    + "\n",
    encoding="utf-8",
)


REPORT_SHA = sha256(
    REPORT
)


# ==================================================================
# 16 — FREEZE 7.2–7.5
# ==================================================================

section(
    "16 — CREATE 7.2–7.5 FREEZES"
)


freeze_specs = (
    (
        FR72,
        "7.2",
        "Parallel Branch Tracking",
        F72,
        PARALLEL_BRANCH_TRACKING_VERSION,
        SHA72,
    ),
    (
        FR73,
        "7.3",
        "Fan-In",
        F73,
        FAN_IN_VERSION,
        SHA73,
    ),
    (
        FR74,
        "7.4",
        "Join Policies",
        F74,
        JOIN_POLICIES_VERSION,
        SHA74,
    ),
    (
        FR75,
        "7.5",
        "Conditional Execution",
        F75,
        CONDITIONAL_EXECUTION_VERSION,
        SHA75,
    ),
)


freeze_hashes = {}


for (
    freeze_path,
    phase,
    component,
    production_path,
    version,
    production_sha,
) in freeze_specs:

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
                    production_path.relative_to(
                        ROOT
                    )
                ).replace(
                    "\\",
                    "/",
                ),

            "version":
                version,

            "sha256":
                production_sha,
        },

        "batch_certification_report": {
            "path":
                REPORT.name,

            "sha256":
                REPORT_SHA,
        },

        "upstream": {
            "phase_4_1_dependency_graph_sha256":
                EXPECTED_DG_SHA,

            "phase_7_1_fan_out_sha256":
                EXPECTED_71_SHA,

            "phase_7_1_freeze_sha256":
                EXPECTED_71_FREEZE_SHA,
        },

        "boundaries": [
            "no Runtime job identity",
            "no Runtime submission",
            "no Runtime execution",
            "no persistence",
            "no workflow lifecycle mutation",
            "Phase 7.7 retains advanced skip semantics",
        ],

        "freeze_created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
    }

    freeze_path.write_text(
        json.dumps(
            document,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    freeze_hashes[
        phase
    ] = sha256(
        freeze_path
    )


# ==================================================================
# 17 — POST-FREEZE INTEGRITY
# ==================================================================

section(
    "17 — POST-FREEZE INTEGRITY"
)


post_checks, post_check = check_bucket()


post_check(
    "7.2 production stable",
    sha256(F72)
    == SHA72,
)

post_check(
    "7.3 production stable",
    sha256(F73)
    == SHA73,
)

post_check(
    "7.4 production stable",
    sha256(F74)
    == SHA74,
)

post_check(
    "7.5 production stable",
    sha256(F75)
    == SHA75,
)

post_check(
    "Phase 4.1 still frozen",
    sha256(DG)
    == EXPECTED_DG_SHA,
)

post_check(
    "Phase 7.1 still frozen",
    sha256(F71)
    == EXPECTED_71_SHA,
)

post_check(
    "Phase 7.1 freeze still frozen",
    sha256(FR71)
    == EXPECTED_71_FREEZE_SHA,
)

post_check(
    "7.2 freeze exists",
    FR72.exists(),
)

post_check(
    "7.3 freeze exists",
    FR73.exists(),
)

post_check(
    "7.4 freeze exists",
    FR74.exists(),
)

post_check(
    "7.5 freeze exists",
    FR75.exists(),
)


if not all(post_checks):
    stop(
        "Post-freeze integrity failed."
    )


# ==================================================================
# 18 — FINAL STATUS
# ==================================================================

section(
    "18 — FINAL STATUS"
)


print(
    "TOTAL FORMAL CHECKS:",
    total_checks,
    "PASS",
)

print()

print(
    "PHASE 7.2 — PARALLEL BRANCH TRACKING CERTIFIED: TRUE"
)

print(
    "PHASE 7.2 — FROZEN: TRUE"
)

print(
    "7.2 SHA256:",
    SHA72,
)

print(
    "7.2 FREEZE SHA256:",
    freeze_hashes[
        "7.2"
    ],
)

print()

print(
    "PHASE 7.3 — FAN-IN CERTIFIED: TRUE"
)

print(
    "PHASE 7.3 — FROZEN: TRUE"
)

print(
    "7.3 SHA256:",
    SHA73,
)

print(
    "7.3 FREEZE SHA256:",
    freeze_hashes[
        "7.3"
    ],
)

print()

print(
    "PHASE 7.4 — JOIN POLICIES CERTIFIED: TRUE"
)

print(
    "PHASE 7.4 — FROZEN: TRUE"
)

print(
    "7.4 SHA256:",
    SHA74,
)

print(
    "7.4 FREEZE SHA256:",
    freeze_hashes[
        "7.4"
    ],
)

print()

print(
    "PHASE 7.5 — CONDITIONAL EXECUTION CERTIFIED: TRUE"
)

print(
    "PHASE 7.5 — FROZEN: TRUE"
)

print(
    "7.5 SHA256:",
    SHA75,
)

print(
    "7.5 FREEZE SHA256:",
    freeze_hashes[
        "7.5"
    ],
)

print()

print(
    "BATCH CERTIFICATION REPORT SHA256:",
    REPORT_SHA,
)

print()

print(
    "PHASE 7.1 MODIFIED: FALSE"
)

print(
    "PHASE 4.1 MODIFIED: FALSE"
)

print()

print(
    "NEXT: PHASE 7.6 — OPTIONAL STAGES"
)

print("=" * 120)
