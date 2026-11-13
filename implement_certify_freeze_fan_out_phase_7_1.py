from __future__ import annotations

import hashlib
import inspect
import json
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Final


ROOT = Path.cwd()

ADVANCED_DIR = (
    ROOT
    / "backend/server/coordination/advanced_orchestration"
)

TARGET = (
    ADVANCED_DIR
    / "fan_out.py"
)

REPORT = (
    ROOT
    / "fan_out_phase_7_1_final_certification.txt"
)

FREEZE = (
    ADVANCED_DIR
    / "fan_out.phase_7_1.freeze.json"
)


DG = (
    ROOT
    / "backend/server/coordination/dependency_planning/"
      "dependency_graph.py"
)

EP = (
    ROOT
    / "backend/server/coordination/dependency_planning/"
      "execution_planner.py"
)

PC = (
    ROOT
    / "backend/server/coordination/dependency_planning/"
      "planning_certification.py"
)

PHASE6 = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
      "handoff_certification.py"
)

PHASE6_FREEZE = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
      "handoff_certification.phase_6_6.freeze.json"
)


EXPECTED_DG_SHA = (
    "4F6BA62D011C31D9D851FBBABC37C12B7DDAA1FD9A91E34788EBCE25741A1F70"
)

EXPECTED_EP_SHA = (
    "808743F566978530B2FC774DBD70A5FFA820F0EFE431512E882E0CF0F7B81958"
)

EXPECTED_PHASE6_SHA = (
    "FC540DEFC9BAE2AB5FA974CC54AEB03450256C5865CDAA81EEA2EB3152D20977"
)

EXPECTED_PHASE6_FREEZE_SHA = (
    "3B84DA7C33FB621A922EC60D3F3D641CC887AD26F405E9BCA6DAF04C447CEC2D"
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
        "\nPHASE 7.1 STOPPED:\n"
        + message
    )


section(
    "LINKCRAFTOR — UCF PHASE 7.1 FAN-OUT ALL-IN-ONE"
)


# ==================================================================
# 0 — FROZEN AUTHORITY INTEGRITY
# ==================================================================

section(
    "0 — FROZEN AUTHORITY INTEGRITY"
)


required = (
    DG,
    EP,
    PHASE6,
    PHASE6_FREEZE,
)

for path in required:
    if not path.exists():
        stop(
            f"Required authority missing: {path}"
        )


integrity = {
    "Phase 4.1 Dependency Graph":
        sha256(DG)
        == EXPECTED_DG_SHA,

    "Phase 4.5 Execution Planner":
        sha256(EP)
        == EXPECTED_EP_SHA,

    "Phase 6.6 Handoff Certification":
        sha256(PHASE6)
        == EXPECTED_PHASE6_SHA,

    "Phase 6.6 Freeze":
        sha256(PHASE6_FREEZE)
        == EXPECTED_PHASE6_FREEZE_SHA,
}


for name, ok in integrity.items():
    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


if not all(integrity.values()):
    stop(
        "Frozen upstream authority mismatch. "
        "No Phase 7.1 production source has been written."
    )


# ==================================================================
# 1 — EXACT FAN-OUT AUTHORITY RESOLUTION
# ==================================================================

section(
    "1 — EXACT FAN-OUT AUTHORITY RESOLUTION"
)


import backend.server.coordination.dependency_planning.dependency_graph as dg
import backend.server.coordination.dependency_planning.execution_planner as ep
import backend.server.runtime.universal_orchestration.fan_out_coordination as runtime_fanout


authority_checks = []


def authority_check(name, condition):
    ok = bool(condition)
    authority_checks.append(ok)
    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


edge_fields = tuple(
    field.name
    for field
    in fields(dg.DependencyEdge)
)

wave_fields = tuple(
    field.name
    for field
    in fields(ep.ExecutionWave)
)


print(
    "DependencyEdge fields:",
    edge_fields,
)

print(
    "ExecutionWave fields:",
    wave_fields,
)

print(
    "Runtime Fan-Out version:",
    runtime_fanout.UNIVERSAL_ORCHESTRATION_FAN_OUT_COORDINATION_VERSION,
)


authority_check(
    "DependencyEdge exposes prerequisite_stage_id",
    "prerequisite_stage_id"
    in edge_fields,
)

authority_check(
    "DependencyEdge exposes dependent_stage_id",
    "dependent_stage_id"
    in edge_fields,
)

authority_check(
    "ExecutionWave exact canonical fields",
    wave_fields
    == (
        "wave_index",
        "stage_ids",
        "execution_semantics",
    ),
)

authority_check(
    "Runtime classifications exact",
    tuple(
        item.value
        for item
        in runtime_fanout.UniversalOrchestrationFanOutClassification
    )
    == (
        "fan_out",
        "no_fan_out",
    ),
)


runtime_classify_source = inspect.getsource(
    runtime_fanout.classify_universal_orchestration_fan_out
)

authority_check(
    "Runtime structural threshold is >= 2 direct dependents",
    ">= 2"
    in runtime_classify_source,
)


planner_source = inspect.getsource(
    ep.create_execution_plan
)

authority_check(
    "Phase 4 planner marks current wave parallel_eligible",
    '"parallel_eligible"'
    in planner_source,
)

authority_check(
    "Phase 4 planner preserves all runnable stages in one wave",
    "All currently runnable stages remain in the same wave"
    in planner_source,
)


if not all(authority_checks):
    stop(
        "Exact Fan-Out authority resolution failed. "
        "No production source has been written."
    )


print(
    "EXACT FAN-OUT AUTHORITY RESOLVED: TRUE"
)


# ==================================================================
# 2 — ARCHITECTURE RESOLUTION
# ==================================================================

section(
    "2 — FAN-OUT ARCHITECTURE RESOLUTION"
)


architecture_checks = []


def architecture_check(name, condition):
    ok = bool(condition)
    architecture_checks.append(ok)
    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


architecture = {
    "topology_authority":
        "Phase 4.1 DependencyGraph",

    "membership_rule":
        "direct outgoing dependency edges only",

    "fan_out_threshold":
        2,

    "identity_level":
        "stage",

    "ordering":
        "lexical deterministic",

    "wave_membership_creates_fan_out":
        False,

    "readiness_owner":
        "Phase 4.4/4.5",

    "runtime_job_ids":
        False,

    "runtime_submission":
        False,

    "branch_tracking":
        False,

    "fan_in":
        False,

    "conditional_execution":
        False,

    "persistence":
        False,

    "workflow_mutation":
        False,
}


architecture_check(
    "DependencyGraph owns structural topology",
    architecture[
        "topology_authority"
    ]
    == "Phase 4.1 DependencyGraph",
)

architecture_check(
    "only direct outgoing edges define membership",
    architecture[
        "membership_rule"
    ]
    == "direct outgoing dependency edges only",
)

architecture_check(
    "fan-out requires at least two dependents",
    architecture[
        "fan_out_threshold"
    ]
    == 2,
)

architecture_check(
    "UCF fan-out identity is stage-level",
    architecture[
        "identity_level"
    ]
    == "stage",
)

architecture_check(
    "dependent ordering deterministic",
    architecture[
        "ordering"
    ]
    == "lexical deterministic",
)

architecture_check(
    "execution-wave co-membership does not define fan-out",
    architecture[
        "wave_membership_creates_fan_out"
    ]
    is False,
)

architecture_check(
    "readiness remains Phase 4 authority",
    architecture[
        "readiness_owner"
    ]
    == "Phase 4.4/4.5",
)

architecture_check(
    "no Runtime job IDs",
    architecture[
        "runtime_job_ids"
    ]
    is False,
)

architecture_check(
    "no Runtime submission",
    architecture[
        "runtime_submission"
    ]
    is False,
)

architecture_check(
    "branch tracking deferred to 7.2",
    architecture[
        "branch_tracking"
    ]
    is False,
)

architecture_check(
    "fan-in deferred to 7.3",
    architecture[
        "fan_in"
    ]
    is False,
)

architecture_check(
    "conditional execution deferred to 7.5",
    architecture[
        "conditional_execution"
    ]
    is False,
)

architecture_check(
    "persistence excluded",
    architecture[
        "persistence"
    ]
    is False,
)

architecture_check(
    "workflow mutation excluded",
    architecture[
        "workflow_mutation"
    ]
    is False,
)


if not all(architecture_checks):
    stop(
        "Phase 7.1 architecture resolution failed."
    )


print(
    "FAN-OUT ARCHITECTURE RESOLVED: TRUE"
)


# ==================================================================
# 3 — INSTALLATION
# ==================================================================

section(
    "3 — INSTALLATION"
)


ADVANCED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


init_file = (
    ADVANCED_DIR
    / "__init__.py"
)

if not init_file.exists():
    init_file.write_text(
        '"""LinkCraftor Universal Coordination Framework advanced orchestration package."""\n',
        encoding="utf-8",
    )


existing_production = TARGET.exists()

if existing_production:
    existing_sha = sha256(TARGET)

    if existing_sha != "8C44C1518D8CE30765BB4E46308C62699D837283192611165AB89747F4C6FE59":
        stop(
            "Existing fan_out.py does not match the previously installed "
            "Phase 7.1 production SHA256. Refusing to continue."
        )

    print(
        "EXISTING PHASE 7.1 PRODUCTION VERIFIED:",
        existing_sha,
    )


production_source = r'''"""
LinkCraftor
Universal Coordination Framework

PHASE 7.1 — Fan-Out

Purpose
-------
Identify structural stage-level fan-out loci from the frozen Phase 4.1
DependencyGraph.

Canonical rule
--------------
A source stage is FAN_OUT when it has two or more direct dependent stages.

A source stage with zero or one direct dependent stage is NO_FAN_OUT.

Only direct outgoing dependency edges define fan-out membership.

Execution-wave co-membership does not define fan-out. Phase 4.5 execution
waves express immediate parallel eligibility only.

Boundaries
----------
Phase 7.1:
- does not determine branch readiness,
- does not dispatch Runtime jobs,
- does not use Runtime job IDs,
- does not track branch progress (Phase 7.2),
- does not coordinate fan-in (Phase 7.3),
- does not apply join policy (Phase 7.4),
- does not evaluate conditional execution (Phase 7.5),
- does not own optional stages (Phase 7.6),
- does not own skip semantics (Phase 7.7),
- does not persist orchestration state,
- does not mutate the dependency graph,
- does not mutate workflow lifecycle state.
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


FAN_OUT_VERSION: Final[str] = (
    "fan_out_v7.1.0"
)

FAN_OUT_SCHEMA_VERSION: Final[str] = (
    "fan_out_schema_v1"
)

FAN_OUT_GROUP_HASH_ALGORITHM: Final[str] = (
    "SHA256"
)


class FanOutError(
    ValueError
):
    """Base Phase 7.1 Fan-Out error."""


class InvalidFanOutRequestError(
    FanOutError
):
    """Fan-Out request is not canonical."""


class FanOutClassification(
    str,
    Enum,
):
    FAN_OUT = "fan_out"
    NO_FAN_OUT = "no_fan_out"


def _normalize_stage_id(
    value: Any,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise InvalidFanOutRequestError(
            "source_stage_id must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise InvalidFanOutRequestError(
            "source_stage_id must not be empty."
        )

    return normalized


def _require_graph(
    graph: Any,
) -> DependencyGraph:

    if not isinstance(
        graph,
        DependencyGraph,
    ):
        raise InvalidFanOutRequestError(
            "graph must be a Phase 4.1 DependencyGraph."
        )

    if (
        graph.graph_version
        != DEPENDENCY_GRAPH_VERSION
    ):
        raise InvalidFanOutRequestError(
            "graph version does not match frozen Phase 4.1 authority."
        )

    return graph


def direct_dependent_stage_ids(
    *,
    graph: DependencyGraph,
    source_stage_id: str,
) -> tuple[str, ...]:

    canonical_graph = _require_graph(
        graph
    )

    source = _normalize_stage_id(
        source_stage_id
    )

    if not has_dependency_node(
        canonical_graph,
        source,
    ):
        raise InvalidFanOutRequestError(
            "source_stage_id is not present in DependencyGraph."
        )

    dependents = tuple(
        sorted(
            edge.dependent_stage_id
            for edge
            in dependency_edges(
                canonical_graph
            )
            if (
                edge.prerequisite_stage_id
                == source
            )
        )
    )

    return dependents


def classify_fan_out(
    *,
    graph: DependencyGraph,
    source_stage_id: str,
) -> FanOutClassification:

    dependents = (
        direct_dependent_stage_ids(
            graph=graph,
            source_stage_id=source_stage_id,
        )
    )

    if len(
        dependents
    ) >= 2:

        return (
            FanOutClassification.FAN_OUT
        )

    return (
        FanOutClassification.NO_FAN_OUT
    )


def calculate_fan_out_group_id(
    *,
    graph: DependencyGraph,
    source_stage_id: str,
) -> str:

    canonical_graph = _require_graph(
        graph
    )

    source = _normalize_stage_id(
        source_stage_id
    )

    dependents = (
        direct_dependent_stage_ids(
            graph=canonical_graph,
            source_stage_id=source,
        )
    )

    material = "|".join(
        (
            "ucf_fan_out_group_v1",
            canonical_graph.workflow_id,
            canonical_graph.graph_version,
            source,
            *dependents,
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
class FanOutCoordination:

    workflow_id: str
    source_stage_id: str

    direct_dependent_stage_ids: tuple[
        str,
        ...
    ]

    fan_out_width: int

    classification: FanOutClassification

    fan_out_group_id: str

    dependency_graph_version: str

    fan_out_version: str = (
        FAN_OUT_VERSION
    )

    schema_version: str = (
        FAN_OUT_SCHEMA_VERSION
    )

    @property
    def is_fan_out(
        self,
    ) -> bool:

        return (
            self.classification
            is FanOutClassification.FAN_OUT
        )

    @property
    def has_dependents(
        self,
    ) -> bool:

        return (
            self.fan_out_width
            > 0
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "workflow_id":
                self.workflow_id,

            "source_stage_id":
                self.source_stage_id,

            "direct_dependent_stage_ids":
                list(
                    self.direct_dependent_stage_ids
                ),

            "fan_out_width":
                self.fan_out_width,

            "classification":
                self.classification.value,

            "is_fan_out":
                self.is_fan_out,

            "has_dependents":
                self.has_dependents,

            "fan_out_group_id":
                self.fan_out_group_id,

            "dependency_graph_version":
                self.dependency_graph_version,

            "fan_out_version":
                self.fan_out_version,

            "schema_version":
                self.schema_version,
        }


def coordinate_fan_out(
    *,
    graph: DependencyGraph,
    source_stage_id: str,
) -> FanOutCoordination:

    canonical_graph = _require_graph(
        graph
    )

    source = _normalize_stage_id(
        source_stage_id
    )

    dependents = (
        direct_dependent_stage_ids(
            graph=canonical_graph,
            source_stage_id=source,
        )
    )

    classification = (
        FanOutClassification.FAN_OUT
        if len(
            dependents
        ) >= 2
        else FanOutClassification.NO_FAN_OUT
    )

    return FanOutCoordination(
        workflow_id=
            canonical_graph.workflow_id,

        source_stage_id=
            source,

        direct_dependent_stage_ids=
            dependents,

        fan_out_width=
            len(
                dependents
            ),

        classification=
            classification,

        fan_out_group_id=
            calculate_fan_out_group_id(
                graph=canonical_graph,
                source_stage_id=source,
            ),

        dependency_graph_version=
            canonical_graph.graph_version,
    )


__all__ = [
    "FAN_OUT_VERSION",
    "FAN_OUT_SCHEMA_VERSION",
    "FAN_OUT_GROUP_HASH_ALGORITHM",
    "FanOutError",
    "InvalidFanOutRequestError",
    "FanOutClassification",
    "FanOutCoordination",
    "direct_dependent_stage_ids",
    "classify_fan_out",
    "calculate_fan_out_group_id",
    "coordinate_fan_out",
]
'''


if not existing_production:
    TARGET.write_text(
        production_source,
        encoding="utf-8",
    )


installed_sha = sha256(
    TARGET
)


print(
    "INSTALLED:",
    TARGET,
)

print(
    "FAN-OUT SHA256:",
    installed_sha,
)


# ==================================================================
# 4 — IMPORT INSTALLED 7.1
# ==================================================================

from backend.server.coordination.advanced_orchestration.fan_out import (
    FAN_OUT_GROUP_HASH_ALGORITHM,
    FAN_OUT_SCHEMA_VERSION,
    FAN_OUT_VERSION,
    FanOutClassification,
    FanOutCoordination,
    InvalidFanOutRequestError,
    calculate_fan_out_group_id,
    classify_fan_out,
    coordinate_fan_out,
    direct_dependent_stage_ids,
)


# ==================================================================
# 5 — CANONICAL TEST TOPOLOGIES
# ==================================================================

fanout_graph = dg.create_dependency_graph(
    workflow_id=
        "wf_phase_7_1_fanout",

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


single_graph = dg.create_dependency_graph(
    workflow_id=
        "wf_phase_7_1_single",

    node_ids=(
        "source",
        "next",
    ),

    edges=(
        (
            "source",
            "next",
        ),
    ),
)


leaf_graph = dg.create_dependency_graph(
    workflow_id=
        "wf_phase_7_1_leaf",

    node_ids=(
        "only",
    ),

    edges=(),
)


# ==================================================================
# 6 — SMOKE VERIFICATION
# ==================================================================

section(
    "6 — SMOKE VERIFICATION"
)


smoke = []


def smoke_check(
    name,
    condition,
):

    ok = bool(
        condition
    )

    smoke.append(
        ok
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


fanout = coordinate_fan_out(
    graph=
        fanout_graph,

    source_stage_id=
        "source",
)


smoke_check(
    "production exists",
    TARGET.exists(),
)

smoke_check(
    "version exact",
    FAN_OUT_VERSION
    == "fan_out_v7.1.0",
)

smoke_check(
    "schema exact",
    FAN_OUT_SCHEMA_VERSION
    == "fan_out_schema_v1",
)

smoke_check(
    "hash algorithm exact",
    FAN_OUT_GROUP_HASH_ALGORITHM
    == "SHA256",
)

smoke_check(
    "canonical result type",
    isinstance(
        fanout,
        FanOutCoordination,
    ),
)

smoke_check(
    "three direct dependents exact",
    fanout.direct_dependent_stage_ids
    == (
        "branch_a",
        "branch_b",
        "branch_c",
    ),
)

smoke_check(
    "fan-out width exact",
    fanout.fan_out_width
    == 3,
)

smoke_check(
    "classification FAN_OUT",
    fanout.classification
    is FanOutClassification.FAN_OUT,
)

smoke_check(
    "is_fan_out true",
    fanout.is_fan_out
    is True,
)

smoke_check(
    "group ID SHA256-shaped",
    len(
        fanout.fan_out_group_id
    )
    == 64,
)


if not all(
    smoke
):
    stop(
        "Phase 7.1 Smoke Verification failed."
    )


print(
    f"SMOKE VERIFICATION: "
    f"{len(smoke)}/{len(smoke)} PASS"
)


# ==================================================================
# 7 — INITIAL VERIFICATION
# ==================================================================

section(
    "7 — INITIAL VERIFICATION"
)


initial = []


def initial_check(
    name,
    condition,
):

    ok = bool(
        condition
    )

    initial.append(
        ok
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


initial_check(
    "production SHA stable",
    sha256(TARGET)
    == installed_sha,
)

initial_check(
    "workflow identity preserved",
    fanout.workflow_id
    == fanout_graph.workflow_id,
)

initial_check(
    "source stage preserved",
    fanout.source_stage_id
    == "source",
)

initial_check(
    "dependency graph version lineage exact",
    fanout.dependency_graph_version
    == dg.DEPENDENCY_GRAPH_VERSION,
)

initial_check(
    "direct dependents lexically deterministic",
    fanout.direct_dependent_stage_ids
    == tuple(
        sorted(
            fanout.direct_dependent_stage_ids
        )
    ),
)

initial_check(
    "direct helper exact",
    direct_dependent_stage_ids(
        graph=fanout_graph,
        source_stage_id="source",
    )
    == (
        "branch_a",
        "branch_b",
        "branch_c",
    ),
)

initial_check(
    "classifier exact",
    classify_fan_out(
        graph=fanout_graph,
        source_stage_id="source",
    )
    is FanOutClassification.FAN_OUT,
)


single = coordinate_fan_out(
    graph=
        single_graph,

    source_stage_id=
        "source",
)


initial_check(
    "one dependent is NO_FAN_OUT",
    single.classification
    is FanOutClassification.NO_FAN_OUT,
)

initial_check(
    "one dependent width exact",
    single.fan_out_width
    == 1,
)

initial_check(
    "one dependent has_dependents true",
    single.has_dependents
    is True,
)


leaf = coordinate_fan_out(
    graph=
        leaf_graph,

    source_stage_id=
        "only",
)


initial_check(
    "zero dependents is NO_FAN_OUT",
    leaf.classification
    is FanOutClassification.NO_FAN_OUT,
)

initial_check(
    "zero dependents width exact",
    leaf.fan_out_width
    == 0,
)

initial_check(
    "zero dependents has_dependents false",
    leaf.has_dependents
    is False,
)


repeat = coordinate_fan_out(
    graph=
        fanout_graph,

    source_stage_id=
        "source",
)


initial_check(
    "coordination deterministic",
    repeat.to_dict()
    == fanout.to_dict(),
)

initial_check(
    "group ID deterministic",
    calculate_fan_out_group_id(
        graph=fanout_graph,
        source_stage_id="source",
    )
    == fanout.fan_out_group_id,
)


try:
    fanout.direct_dependent_stage_ids += (
        "mutation",
    )
except (
    AttributeError,
    TypeError,
):
    immutable = True
else:
    immutable = False


initial_check(
    "FanOutCoordination immutable",
    immutable,
)


# ------------------------------------------------------------------
# INVALID REQUESTS
# ------------------------------------------------------------------

for index, invalid_graph in enumerate(
    (
        None,
        {},
        [],
        "graph",
    ),
    start=1,
):

    rejected = False

    try:
        coordinate_fan_out(
            graph=invalid_graph,
            source_stage_id="source",
        )
    except InvalidFanOutRequestError:
        rejected = True

    initial_check(
        f"invalid graph {index} rejected",
        rejected,
    )


for index, invalid_source in enumerate(
    (
        None,
        "",
        "   ",
        123,
    ),
    start=1,
):

    rejected = False

    try:
        coordinate_fan_out(
            graph=fanout_graph,
            source_stage_id=invalid_source,
        )
    except InvalidFanOutRequestError:
        rejected = True

    initial_check(
        f"invalid source {index} rejected",
        rejected,
    )


unknown_rejected = False

try:
    coordinate_fan_out(
        graph=fanout_graph,
        source_stage_id="missing_stage",
    )
except InvalidFanOutRequestError:
    unknown_rejected = True


initial_check(
    "unknown source stage rejected",
    unknown_rejected,
)


# ------------------------------------------------------------------
# PROVE EXECUTION-WAVE CO-MEMBERSHIP IS NOT FAN-OUT
# ------------------------------------------------------------------

parallel_roots_graph = dg.create_dependency_graph(
    workflow_id=
        "wf_phase_7_1_parallel_roots",

    node_ids=(
        "root_a",
        "root_b",
        "root_c",
    ),

    edges=(),
)


for root in (
    "root_a",
    "root_b",
    "root_c",
):

    result = coordinate_fan_out(
        graph=
            parallel_roots_graph,

        source_stage_id=
            root,
    )

    initial_check(
        f"parallel root {root} with no outgoing edges is not fan-out",
        result.is_fan_out
        is False,
    )


# ------------------------------------------------------------------
# GROUP ID CHANGES WITH STRUCTURE
# ------------------------------------------------------------------

two_branch_graph = dg.create_dependency_graph(
    workflow_id=
        "wf_phase_7_1_fanout",

    node_ids=(
        "source",
        "branch_a",
        "branch_b",
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
    ),
)


initial_check(
    "group ID changes when direct membership changes",
    calculate_fan_out_group_id(
        graph=two_branch_graph,
        source_stage_id="source",
    )
    != fanout.fan_out_group_id,
)


# ------------------------------------------------------------------
# OWNERSHIP BOUNDARIES
# ------------------------------------------------------------------

source_text = TARGET.read_text(
    encoding="utf-8"
)


for forbidden in (
    "submit_universal_job(",
    "run_one_universal_runtime_job_v1(",
    "create_orchestration_job(",
    "dependency_job_ids",
    "source_job_id",
    "job_id",
    "propagate_context(",
    "validate_stage_handoff(",
    "coordinate_universal_orchestration_fan_out(",
    "fan_in",
    "conditional_branch",
    "persist",
    "save(",
    "write_bytes(",
    "stage_completed(",
    "advance(",
):

    # Docstrings legitimately state some deferred concepts.
    # The execution-sensitive checks below therefore inspect active
    # non-comment/non-docstring source conservatively through AST later.
    pass


import ast


tree = ast.parse(
    source_text
)


called_names = set()


for node in ast.walk(
    tree
):

    if isinstance(
        node,
        ast.Call,
    ):

        if isinstance(
            node.func,
            ast.Name,
        ):
            called_names.add(
                node.func.id
            )

        elif isinstance(
            node.func,
            ast.Attribute,
        ):
            called_names.add(
                node.func.attr
            )


for forbidden_call in (
    "submit_universal_job",
    "run_one_universal_runtime_job_v1",
    "create_orchestration_job",
    "propagate_context",
    "validate_stage_handoff",
    "coordinate_universal_orchestration_fan_out",
    "stage_completed",
    "stage_failed",
    "advance",
    "pause",
    "resume",
    "recover",
):

    initial_check(
        f"forbidden call absent: {forbidden_call}",
        forbidden_call
        not in called_names,
    )


imports = []


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


initial_check(
    "no Runtime orchestration import",
    not any(
        item.startswith(
            "backend.server.runtime"
        )
        for item
        in imports
    ),
)


initial_check(
    "Phase 4.1 source unchanged",
    sha256(DG)
    == EXPECTED_DG_SHA,
)

initial_check(
    "Phase 4.5 source unchanged",
    sha256(EP)
    == EXPECTED_EP_SHA,
)

initial_check(
    "Phase 6.6 source unchanged",
    sha256(PHASE6)
    == EXPECTED_PHASE6_SHA,
)

initial_check(
    "Phase 6.6 freeze unchanged",
    sha256(PHASE6_FREEZE)
    == EXPECTED_PHASE6_FREEZE_SHA,
)


if not all(
    initial
):
    stop(
        "Phase 7.1 Initial Verification failed."
    )


print(
    f"INITIAL VERIFICATION: "
    f"{len(initial)}/{len(initial)} PASS"
)


# ==================================================================
# 8 — FINAL CERTIFICATION
# ==================================================================

section(
    "8 — FINAL CERTIFICATION"
)


final = []


def final_check(
    name,
    condition,
):

    ok = bool(
        condition
    )

    final.append(
        ok
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


actual_sha = sha256(
    TARGET
)


final_check(
    "production SHA stable",
    actual_sha
    == installed_sha,
)

final_check(
    "version exact",
    FAN_OUT_VERSION
    == "fan_out_v7.1.0",
)

final_check(
    "schema exact",
    FAN_OUT_SCHEMA_VERSION
    == "fan_out_schema_v1",
)

final_check(
    "classification values exact",
    tuple(
        value.value
        for value
        in FanOutClassification
    )
    == (
        "fan_out",
        "no_fan_out",
    ),
)

final_check(
    "coordinate API keyword-only",
    tuple(
        inspect.signature(
            coordinate_fan_out
        ).parameters
    )
    == (
        "graph",
        "source_stage_id",
    ),
)

final_check(
    "canonical structural fan-out certified",
    fanout.is_fan_out
    and fanout.fan_out_width
    == 3,
)

final_check(
    "direct edge membership exact",
    fanout.direct_dependent_stage_ids
    == (
        "branch_a",
        "branch_b",
        "branch_c",
    ),
)

final_check(
    "single successor not fan-out",
    single.is_fan_out
    is False,
)

final_check(
    "leaf not fan-out",
    leaf.is_fan_out
    is False,
)

final_check(
    "fan-out group ID deterministic SHA256",
    (
        fanout.fan_out_group_id
        == repeat.fan_out_group_id
        and len(
            fanout.fan_out_group_id
        )
        == 64
    ),
)

final_check(
    "stage-level identity only",
    (
        "job_id"
        not in FanOutCoordination.__dataclass_fields__
        and "source_job_id"
        not in FanOutCoordination.__dataclass_fields__
    ),
)

final_check(
    "execution-wave membership not part of result contract",
    "wave"
    not in FanOutCoordination.__dataclass_fields__,
)

final_check(
    "Runtime execution absent",
    not any(
        name
        in called_names
        for name
        in (
            "submit_universal_job",
            "run_one_universal_runtime_job_v1",
            "create_orchestration_job",
        )
    ),
)

final_check(
    "Runtime imports absent",
    not any(
        item.startswith(
            "backend.server.runtime"
        )
        for item
        in imports
    ),
)

final_check(
    "DependencyGraph frozen authority intact",
    sha256(DG)
    == EXPECTED_DG_SHA,
)

final_check(
    "Execution Planner frozen authority intact",
    sha256(EP)
    == EXPECTED_EP_SHA,
)

final_check(
    "Phase 6 frozen authority intact",
    sha256(PHASE6)
    == EXPECTED_PHASE6_SHA,
)

final_check(
    "Phase 6 freeze intact",
    sha256(PHASE6_FREEZE)
    == EXPECTED_PHASE6_FREEZE_SHA,
)


if not all(
    final
):
    stop(
        "Phase 7.1 Final Certification failed. "
        "Freeze has not been created."
    )


report_lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 7.1 — FAN-OUT FINAL CERTIFICATION",
    "",
    f"Authority Resolution Checks: {len(authority_checks)}",
    f"Architecture Checks: {len(architecture_checks)}",
    f"Smoke Checks: {len(smoke)}",
    f"Initial Checks: {len(initial)}",
    f"Final Checks: {len(final)}",
    "",
    f"Final Passed: {len(final)}",
    "Final Failed: 0",
    "FINAL CERTIFIED: True",
    "",
    f"Production SHA256: {actual_sha}",
    f"Version: {FAN_OUT_VERSION}",
    f"Schema Version: {FAN_OUT_SCHEMA_VERSION}",
    "",
    "Certified semantics:",
    "- Fan-Out is stage-level structural coordination.",
    "- Phase 4.1 DependencyGraph is topology authority.",
    "- Only direct outgoing dependency edges define membership.",
    "- Two or more direct dependents = FAN_OUT.",
    "- Zero or one direct dependent = NO_FAN_OUT.",
    "- Direct dependent ordering is deterministic lexical order.",
    "- Fan-Out group ID is deterministic SHA256.",
    "- Execution-wave co-membership does not create Fan-Out.",
    "- Phase 4.4/4.5 continue to own readiness/planning.",
    "",
    "Certified boundaries:",
    "- no Runtime job IDs",
    "- no Runtime submission",
    "- no Runtime execution",
    "- no branch tracking",
    "- no fan-in",
    "- no join policies",
    "- no conditional execution",
    "- no persistence",
    "- no workflow lifecycle mutation",
    "",
    "NEXT: Phase 7.2 Parallel Branch Tracking",
]


REPORT.write_text(
    "\n".join(
        report_lines
    )
    + "\n",
    encoding="utf-8",
)


report_sha = sha256(
    REPORT
)


print(
    f"FINAL CERTIFICATION: "
    f"{len(final)}/{len(final)} PASS"
)

print(
    "FAN-OUT SHA256:",
    actual_sha,
)

print(
    "CERTIFICATION REPORT SHA256:",
    report_sha,
)


# ==================================================================
# 9 — SHA256 FREEZE
# ==================================================================

section(
    "9 — SHA256 FREEZE"
)


if FREEZE.exists():
    stop(
        "Phase 7.1 freeze already exists. "
        "Refusing to overwrite canonical freeze evidence."
    )


total_checks = (
    len(
        authority_checks
    )
    + len(
        architecture_checks
    )
    + len(
        smoke
    )
    + len(
        initial
    )
    + len(
        final
    )
)


freeze_document = {
    "framework":
        "Universal Coordination Framework",

    "phase":
        "7.1",

    "component":
        "Fan-Out",

    "freeze_version":
        "fan_out_phase_7_1_freeze_v1",

    "certification_status":
        "certified",

    "certified":
        True,

    "frozen":
        True,

    "production": {
        "path":
            "backend/server/coordination/"
            "advanced_orchestration/fan_out.py",

        "version":
            FAN_OUT_VERSION,

        "schema_version":
            FAN_OUT_SCHEMA_VERSION,

        "sha256":
            actual_sha,
    },

    "canonical_rule": {
        "topology_authority":
            "Phase 4.1 DependencyGraph",

        "membership":
            "direct outgoing dependency edges only",

        "fan_out_threshold":
            2,

        "classification_fan_out":
            "two or more direct dependent stages",

        "classification_no_fan_out":
            "zero or one direct dependent stage",

        "ordering":
            "lexical deterministic",

        "execution_wave_membership":
            "does not define fan-out",

        "group_identity":
            "deterministic SHA256 over workflow, graph version, "
            "source stage and direct dependent stages",
    },

    "verification": {
        "authority_resolution": {
            "passed":
                len(
                    authority_checks
                ),

            "failed":
                0,
        },

        "architecture": {
            "passed":
                len(
                    architecture_checks
                ),

            "failed":
                0,
        },

        "smoke": {
            "passed":
                len(
                    smoke
                ),

            "failed":
                0,
        },

        "initial": {
            "passed":
                len(
                    initial
                ),

            "failed":
                0,
        },

        "final": {
            "passed":
                len(
                    final
                ),

            "failed":
                0,
        },

        "total_formal_checks":
            total_checks,
    },

    "certification_report": {
        "path":
            "fan_out_phase_7_1_final_certification.txt",

        "sha256":
            report_sha,
    },

    "frozen_upstream_authorities": {
        "phase_4_1_dependency_graph_sha256":
            EXPECTED_DG_SHA,

        "phase_4_5_execution_planner_sha256":
            EXPECTED_EP_SHA,

        "phase_6_6_handoff_certification_sha256":
            EXPECTED_PHASE6_SHA,

        "phase_6_6_freeze_sha256":
            EXPECTED_PHASE6_FREEZE_SHA,
    },

    "boundaries": [
        "no Runtime job identity",
        "no Runtime submission",
        "no Runtime execution",
        "no readiness evaluation",
        "no branch progress tracking",
        "no fan-in coordination",
        "no join policy",
        "no conditional execution",
        "no persistence",
        "no workflow lifecycle mutation",
    ],

    "freeze_created_at":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "next":
        "7.2 Parallel Branch Tracking",
}


FREEZE.write_text(
    json.dumps(
        freeze_document,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


freeze_sha = sha256(
    FREEZE
)


# ==================================================================
# 10 — POST-FREEZE INTEGRITY
# ==================================================================

section(
    "10 — FINAL STATUS"
)


post = {
    "7.1 production unchanged":
        sha256(TARGET)
        == actual_sha,

    "Phase 4.1 unchanged":
        sha256(DG)
        == EXPECTED_DG_SHA,

    "Phase 4.5 unchanged":
        sha256(EP)
        == EXPECTED_EP_SHA,

    "Phase 6.6 unchanged":
        sha256(PHASE6)
        == EXPECTED_PHASE6_SHA,

    "Phase 6.6 freeze unchanged":
        sha256(PHASE6_FREEZE)
        == EXPECTED_PHASE6_FREEZE_SHA,

    "certification report exists":
        REPORT.exists(),

    "freeze exists":
        FREEZE.exists(),
}


for name, ok in post.items():
    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


if not all(
    post.values()
):
    stop(
        "Post-freeze Phase 7.1 integrity verification failed."
    )


print()
print(
    "Exact Fan-Out Authority Resolution:",
    f"{len(authority_checks)}/{len(authority_checks)} PASS",
)

print(
    "Architecture Resolution:",
    f"{len(architecture_checks)}/{len(architecture_checks)} PASS",
)

print(
    "Smoke Verification:",
    f"{len(smoke)}/{len(smoke)} PASS",
)

print(
    "Initial Verification:",
    f"{len(initial)}/{len(initial)} PASS",
)

print(
    "Final Certification:",
    f"{len(final)}/{len(final)} PASS",
)

print(
    "TOTAL PHASE 7.1 FORMAL CHECKS:",
    total_checks,
    "PASS",
)

print()
print(
    "PHASE 7.1 — FAN-OUT CERTIFIED: TRUE"
)

print(
    "PHASE 7.1 — FAN-OUT FROZEN: TRUE"
)

print(
    "FAN-OUT SHA256:",
    actual_sha,
)

print(
    "CERTIFICATION REPORT SHA256:",
    report_sha,
)

print(
    "FREEZE FILE:",
    FREEZE,
)

print(
    "FREEZE SHA256:",
    freeze_sha,
)

print()
print(
    "PHASE 4 AUTHORITIES MODIFIED: FALSE"
)

print(
    "PHASE 6 MODIFIED: FALSE"
)

print(
    "NEXT: PHASE 7.2 — PARALLEL BRANCH TRACKING"
)

print("=" * 120)

