"""
LinkCraftor Universal Coordination Framework
Phase 4.6 ? Planning Certification

Canonical responsibility
------------------------
Phase 4.6 certifies the frozen Phase 4.1?4.5 dependency/planning chain.

It does not introduce new graph, validation, cycle, runnability, or
execution-planning semantics.

Certification chain:

    4.1 Dependency Graph
        ->
    4.2 Dependency Validation
        ->
    4.3 Cycle Detection
        ->
    4.4 Runnable Stage Resolver
        ->
    4.5 Execution Planner
        ->
    4.6 Planning Certification

The component is:

- read-only,
- deterministic,
- side-effect free except for reading canonical source files,
- Runtime independent,
- dispatch free,
- persistence free,
- fail closed.

The Phase 4 composite fingerprint covers frozen production components
4.1 through 4.5. Phase 4.6 receives its own independent SHA freeze after
its certification and therefore is intentionally excluded from its own
composite fingerprint.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.coordination.dependency_planning.dependency_graph import (
    DEPENDENCY_GRAPH_VERSION,
    create_dependency_graph,
)

from backend.server.coordination.dependency_planning.dependency_validation import (
    DEPENDENCY_VALIDATION_VERSION,
    require_valid_dependency_graph,
)

from backend.server.coordination.dependency_planning.cycle_detection import (
    CYCLE_DETECTION_VERSION,
    detect_dependency_cycles,
)

from backend.server.coordination.dependency_planning.runnable_stage_resolver import (
    RUNNABLE_STAGE_RESOLVER_VERSION,
    create_runnable_stage_state,
    resolve_runnable_stages,
)

from backend.server.coordination.dependency_planning.execution_planner import (
    EXECUTION_PLANNER_VERSION,
    create_execution_plan,
)


PLANNING_CERTIFICATION_VERSION = (
    "planning_certification_v4.6.0"
)

PLANNING_CERTIFICATION_SCHEMA_VERSION = (
    "planning_certification_schema_v1"
)

PLANNING_CERTIFICATION_CHECK_FIELD_COUNT = 3

PLANNING_CERTIFICATION_RESULT_FIELD_COUNT = 16

PLANNING_CERTIFICATION_DEEP_CHAIN_NODE_COUNT = 2500


EXPECTED_COMPONENT_VERSIONS = MappingProxyType(
    {
        "4.1": "dependency_graph_v4.1.0",
        "4.2": "dependency_validation_v4.2.0",
        "4.3": "cycle_detection_v4.3.0",
        "4.4": "runnable_stage_resolver_v4.4.0",
        "4.5": "execution_planner_v4.5.0",
    }
)


EXPECTED_COMPONENT_SHAS = MappingProxyType(
    {
        "4.1":
            "4F6BA62D011C31D9D851FBBABC37C12B"
            "7DDAA1FD9A91E34788EBCE25741A1F70",

        "4.2":
            "1D053C0036EA9F7A8AEDFAFC36F6EB82"
            "A681EDC7EF206409E9FFB8C7F212852D",

        "4.3":
            "E77BF605724F991E85C7FE2E5329051E"
            "16ECB2F30ACDAEA8AA40A2FD47487CEA",

        "4.4":
            "2779D432A2F3337F3557C61664499669"
            "CC852773AB74447297E98D6188289483",

        "4.5":
            "808743F566978530B2FC774DBD70A5FFA"
            "820F0EFE431512E882E0CF0F7B81958",
    }
)


_COMPONENT_FILENAMES = MappingProxyType(
    {
        "4.1": "dependency_graph.py",
        "4.2": "dependency_validation.py",
        "4.3": "cycle_detection.py",
        "4.4": "runnable_stage_resolver.py",
        "4.5": "execution_planner.py",
    }
)


class PlanningCertificationError(
    ValueError
):
    """Base Phase 4.6 certification error."""


class PlanningCertificationFailedError(
    PlanningCertificationError
):
    """Raised when canonical Phase 4 certification fails."""

    def __init__(
        self,
        result: "PlanningCertificationResult",
    ) -> None:
        self.result = result

        super().__init__(
            "Phase 4 planning certification failed: "
            f"{result.failed_check_count} "
            "certification check(s) failed."
        )


def _freeze(
    value: Any,
) -> Any:
    if isinstance(
        value,
        Mapping,
    ):
        return MappingProxyType(
            {
                key: _freeze(item)
                for key, item
                in value.items()
            }
        )

    if isinstance(
        value,
        tuple,
    ):
        return tuple(
            _freeze(item)
            for item
            in value
        )

    if isinstance(
        value,
        list,
    ):
        return tuple(
            _freeze(item)
            for item
            in value
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class PlanningCertificationCheck:
    name: str
    passed: bool
    detail: str

    def to_dict(
        self,
    ) -> Mapping[str, Any]:
        return _freeze(
            {
                "name":
                    self.name,

                "passed":
                    self.passed,

                "detail":
                    self.detail,
            }
        )


@dataclass(
    frozen=True,
    slots=True,
)
class PlanningCertificationResult:
    is_certified: bool
    check_count: int
    passed_check_count: int
    failed_check_count: int
    failed_checks: tuple[str, ...]
    checks: tuple[PlanningCertificationCheck, ...]
    component_shas: Mapping[str, str]
    composite_fingerprint: str
    dependency_graph_version: str
    dependency_validation_version: str
    cycle_detection_version: str
    runnable_stage_resolver_version: str
    execution_planner_version: str
    deep_chain_node_count: int
    certification_version: str
    schema_version: str

    def to_dict(
        self,
    ) -> Mapping[str, Any]:
        return _freeze(
            {
                "is_certified":
                    self.is_certified,

                "check_count":
                    self.check_count,

                "passed_check_count":
                    self.passed_check_count,

                "failed_check_count":
                    self.failed_check_count,

                "failed_checks":
                    self.failed_checks,

                "checks":
                    tuple(
                        check.to_dict()
                        for check
                        in self.checks
                    ),

                "component_shas":
                    dict(
                        self.component_shas
                    ),

                "composite_fingerprint":
                    self.composite_fingerprint,

                "dependency_graph_version":
                    self.dependency_graph_version,

                "dependency_validation_version":
                    self.dependency_validation_version,

                "cycle_detection_version":
                    self.cycle_detection_version,

                "runnable_stage_resolver_version":
                    self.runnable_stage_resolver_version,

                "execution_planner_version":
                    self.execution_planner_version,

                "deep_chain_node_count":
                    self.deep_chain_node_count,

                "certification_version":
                    self.certification_version,

                "schema_version":
                    self.schema_version,
            }
        )


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def _component_source_shas(
) -> Mapping[str, str]:
    package = Path(
        __file__
    ).resolve().parent

    return _freeze(
        {
            phase: _sha256(
                package
                / filename
            )
            for phase, filename
            in _COMPONENT_FILENAMES.items()
        }
    )


def _phase_4_composite_fingerprint(
    *,
    component_shas: Mapping[str, str],
) -> str:
    versions = {
        "4.1":
            DEPENDENCY_GRAPH_VERSION,

        "4.2":
            DEPENDENCY_VALIDATION_VERSION,

        "4.3":
            CYCLE_DETECTION_VERSION,

        "4.4":
            RUNNABLE_STAGE_RESOLVER_VERSION,

        "4.5":
            EXECUTION_PLANNER_VERSION,
    }

    payload = "\n".join(
        (
            phase
            + ":"
            + versions[
                phase
            ]
            + ":"
            + component_shas[
                phase
            ]
        )
        for phase
        in (
            "4.1",
            "4.2",
            "4.3",
            "4.4",
            "4.5",
        )
    )

    return hashlib.sha256(
        payload.encode(
            "utf-8"
        )
    ).hexdigest().upper()


def _evaluate_planning_certification(
) -> PlanningCertificationResult:
    checks: list[
        PlanningCertificationCheck
    ] = []

    def record(
        name: str,
        passed: bool,
        detail: str = "",
    ) -> None:
        checks.append(
            PlanningCertificationCheck(
                name=name,
                passed=bool(
                    passed
                ),
                detail=detail,
            )
        )

    component_shas = (
        _component_source_shas()
    )

    # ---------------------------------------------------------------------
    # Exact frozen SHA authority
    # ---------------------------------------------------------------------

    for phase in (
        "4.1",
        "4.2",
        "4.3",
        "4.4",
        "4.5",
    ):
        actual = component_shas[
            phase
        ]

        expected = EXPECTED_COMPONENT_SHAS[
            phase
        ]

        record(
            f"Frozen Phase {phase} SHA exact",
            actual == expected,
            actual,
        )

    # ---------------------------------------------------------------------
    # Exact component version authority
    # ---------------------------------------------------------------------

    actual_versions = {
        "4.1":
            DEPENDENCY_GRAPH_VERSION,

        "4.2":
            DEPENDENCY_VALIDATION_VERSION,

        "4.3":
            CYCLE_DETECTION_VERSION,

        "4.4":
            RUNNABLE_STAGE_RESOLVER_VERSION,

        "4.5":
            EXECUTION_PLANNER_VERSION,
    }

    for phase in (
        "4.1",
        "4.2",
        "4.3",
        "4.4",
        "4.5",
    ):
        actual = actual_versions[
            phase
        ]

        expected = EXPECTED_COMPONENT_VERSIONS[
            phase
        ]

        record(
            f"Phase {phase} version exact",
            actual == expected,
            actual,
        )

    # ---------------------------------------------------------------------
    # Canonical dependency/planning chain
    # ---------------------------------------------------------------------

    try:
        graph = create_dependency_graph(
            workflow_id=(
                "planning-certification-chain"
            ),
            edges=(
                ("a", "join"),
                ("b", "join"),
            ),
        )

        require_valid_dependency_graph(
            graph
        )

        record(
            "Canonical graph passes Phase 4.2 validation",
            True,
        )

    except Exception as exc:
        graph = None

        record(
            "Canonical graph passes Phase 4.2 validation",
            False,
            (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )

    if graph is not None:

        try:
            cycle_result = (
                detect_dependency_cycles(
                    graph
                )
            )

            record(
                "Canonical graph is acyclic",
                (
                    cycle_result.is_acyclic
                    and not cycle_result.has_cycle
                    and cycle_result.cycle_witness_count
                    == 0
                ),
            )

        except Exception as exc:
            record(
                "Canonical graph is acyclic",
                False,
                (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            )

        try:
            initial_state = (
                create_runnable_stage_state(
                    workflow_id=(
                        "planning-certification-chain"
                    ),
                    pending_stage_ids=(
                        "join",
                        "b",
                        "a",
                    ),
                )
            )

            initial_resolution = (
                resolve_runnable_stages(
                    graph,
                    initial_state,
                )
            )

            record(
                "Initial runnable roots exact",
                (
                    initial_resolution.runnable_stage_ids
                    == (
                        "a",
                        "b",
                    )
                ),
            )

            record(
                "Initial blocked join exact",
                (
                    initial_resolution.blocked_stage_ids
                    == (
                        "join",
                    )
                ),
            )

            initial_plan = (
                create_execution_plan(
                    graph,
                    initial_resolution,
                )
            )

            record(
                "Initial execution wave exact",
                (
                    initial_plan.wave_count
                    == 1
                    and initial_plan.planned_stage_ids
                    == (
                        "a",
                        "b",
                    )
                ),
            )

            record(
                "Parallel roots remain one wave",
                (
                    initial_plan.waves[
                        0
                    ].stage_ids
                    == (
                        "a",
                        "b",
                    )
                    and initial_plan.waves[
                        0
                    ].execution_semantics
                    == "parallel_eligible"
                ),
            )

        except Exception as exc:
            record(
                "Initial runnable/planning chain executes",
                False,
                (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            )

        try:
            completed_state = (
                create_runnable_stage_state(
                    workflow_id=(
                        "planning-certification-chain"
                    ),
                    completed_stage_ids=(
                        "a",
                        "b",
                    ),
                    pending_stage_ids=(
                        "join",
                    ),
                )
            )

            completed_resolution = (
                resolve_runnable_stages(
                    graph,
                    completed_state,
                )
            )

            record(
                "Join becomes runnable after prerequisites complete",
                (
                    completed_resolution.runnable_stage_ids
                    == (
                        "join",
                    )
                ),
            )

            completed_plan = (
                create_execution_plan(
                    graph,
                    completed_resolution,
                )
            )

            record(
                "Join execution wave exact",
                (
                    completed_plan.wave_count
                    == 1
                    and completed_plan.planned_stage_ids
                    == (
                        "join",
                    )
                ),
            )

        except Exception as exc:
            record(
                "Completed-prerequisite planning chain executes",
                False,
                (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            )

    # ---------------------------------------------------------------------
    # Cycle evidence
    # ---------------------------------------------------------------------

    try:
        cyclic_graph = (
            create_dependency_graph(
                workflow_id=(
                    "planning-certification-cycle"
                ),
                edges=(
                    ("a", "b"),
                    ("b", "a"),
                ),
            )
        )

        cyclic_result = (
            detect_dependency_cycles(
                cyclic_graph
            )
        )

        record(
            "Directed cycle detected",
            (
                cyclic_result.has_cycle
                and not cyclic_result.is_acyclic
                and cyclic_result.cycle_witness_count
                >= 1
            ),
        )

    except Exception as exc:
        record(
            "Directed cycle detected",
            False,
            (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )

    # ---------------------------------------------------------------------
    # Repaired Phase 4.3 deep-chain regression certification
    # ---------------------------------------------------------------------

    try:
        deep_count = (
            PLANNING_CERTIFICATION_DEEP_CHAIN_NODE_COUNT
        )

        deep_edges = tuple(
            (
                f"deep-{index:04d}",
                f"deep-{index + 1:04d}",
            )
            for index
            in range(
                deep_count - 1
            )
        )

        deep_graph = (
            create_dependency_graph(
                workflow_id=(
                    "planning-certification-deep-chain"
                ),
                edges=deep_edges,
            )
        )

        deep_result = (
            detect_dependency_cycles(
                deep_graph
            )
        )

        record(
            "2500-stage deep chain is acyclic",
            (
                deep_result.is_acyclic
                and not deep_result.has_cycle
                and deep_result.node_count
                == deep_count
                and deep_result.edge_count
                == deep_count - 1
                and deep_result.cycle_witness_count
                == 0
            ),
        )

    except RecursionError as exc:
        record(
            "2500-stage deep chain is acyclic",
            False,
            (
                "RecursionError: "
                + str(
                    exc
                )
            ),
        )

    except Exception as exc:
        record(
            "2500-stage deep chain is acyclic",
            False,
            (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )

    # ---------------------------------------------------------------------
    # Determinism
    # ---------------------------------------------------------------------

    try:
        deterministic_graph = (
            create_dependency_graph(
                workflow_id=(
                    "planning-certification-determinism"
                ),
                edges=(
                    ("a", "join"),
                    ("b", "join"),
                    ("c", "join"),
                ),
            )
        )

        deterministic_state = (
            create_runnable_stage_state(
                workflow_id=(
                    "planning-certification-determinism"
                ),
                pending_stage_ids=(
                    "join",
                    "c",
                    "b",
                    "a",
                ),
            )
        )

        resolution_one = (
            resolve_runnable_stages(
                deterministic_graph,
                deterministic_state,
            )
        )

        resolution_two = (
            resolve_runnable_stages(
                deterministic_graph,
                deterministic_state,
            )
        )

        plan_one = (
            create_execution_plan(
                deterministic_graph,
                resolution_one,
            )
        )

        plan_two = (
            create_execution_plan(
                deterministic_graph,
                resolution_two,
            )
        )

        record(
            "Runnability certification deterministic",
            (
                resolution_one
                == resolution_two
            ),
        )

        record(
            "Planning certification deterministic",
            (
                plan_one
                == plan_two
            ),
        )

    except Exception as exc:
        record(
            "Deterministic planning chain executes",
            False,
            (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )

    # ---------------------------------------------------------------------
    # Composite fingerprint
    # ---------------------------------------------------------------------

    composite = (
        _phase_4_composite_fingerprint(
            component_shas=component_shas,
        )
    )

    record(
        "Composite fingerprint is SHA256",
        (
            len(
                composite
            )
            == 64
            and all(
                character
                in "0123456789ABCDEF"
                for character
                in composite
            )
        ),
        composite,
    )

    frozen_checks = tuple(
        checks
    )

    failed_checks = tuple(
        check.name
        for check
        in frozen_checks
        if not check.passed
    )

    passed_count = sum(
        1
        for check
        in frozen_checks
        if check.passed
    )

    failed_count = (
        len(
            frozen_checks
        )
        - passed_count
    )

    return PlanningCertificationResult(
        is_certified=(
            failed_count
            == 0
        ),

        check_count=len(
            frozen_checks
        ),

        passed_check_count=(
            passed_count
        ),

        failed_check_count=(
            failed_count
        ),

        failed_checks=(
            failed_checks
        ),

        checks=(
            frozen_checks
        ),

        component_shas=(
            component_shas
        ),

        composite_fingerprint=(
            composite
        ),

        dependency_graph_version=(
            DEPENDENCY_GRAPH_VERSION
        ),

        dependency_validation_version=(
            DEPENDENCY_VALIDATION_VERSION
        ),

        cycle_detection_version=(
            CYCLE_DETECTION_VERSION
        ),

        runnable_stage_resolver_version=(
            RUNNABLE_STAGE_RESOLVER_VERSION
        ),

        execution_planner_version=(
            EXECUTION_PLANNER_VERSION
        ),

        deep_chain_node_count=(
            PLANNING_CERTIFICATION_DEEP_CHAIN_NODE_COUNT
        ),

        certification_version=(
            PLANNING_CERTIFICATION_VERSION
        ),

        schema_version=(
            PLANNING_CERTIFICATION_SCHEMA_VERSION
        ),
    )


def certify_dependency_planning(
) -> PlanningCertificationResult:
    """
    Certify the complete frozen Phase 4.1?4.5 dependency/planning chain.

    Certification is fail closed. A failed check raises
    PlanningCertificationFailedError containing the complete immutable
    certification result.
    """

    result = (
        _evaluate_planning_certification()
    )

    if not result.is_certified:
        raise PlanningCertificationFailedError(
            result
        )

    return result


def planning_certification_snapshot(
) -> Mapping[str, Any]:
    """
    Return an immutable snapshot of successful Phase 4 certification.

    Certification failures propagate fail closed.
    """

    result = (
        certify_dependency_planning()
    )

    return _freeze(
        result.to_dict()
    )


def explain_planning_certification_v4_6(
) -> Mapping[str, Any]:
    return _freeze(
        {
            "phase":
                "4.6",

            "component":
                "Planning Certification",

            "version":
                PLANNING_CERTIFICATION_VERSION,

            "schema_version":
                PLANNING_CERTIFICATION_SCHEMA_VERSION,

            "certification_scope":
                (
                    "frozen Phase 4.1 through "
                    "Phase 4.5 dependency/planning chain"
                ),

            "upstream_versions": {
                "4.1":
                    DEPENDENCY_GRAPH_VERSION,

                "4.2":
                    DEPENDENCY_VALIDATION_VERSION,

                "4.3":
                    CYCLE_DETECTION_VERSION,

                "4.4":
                    RUNNABLE_STAGE_RESOLVER_VERSION,

                "4.5":
                    EXECUTION_PLANNER_VERSION,
            },

            "owns": (
                "exact frozen Phase 4.1-4.5 SHA verification",
                "exact Phase 4.1-4.5 version verification",
                "cross-component planning-chain certification",
                "cycle-detection certification",
                "deep-chain regression certification",
                "runnability certification",
                "immediate-wave planning certification",
                "deterministic certification evidence",
                "Phase 4 composite fingerprint",
                "fail-closed certification",
                "immutable certification snapshot",
            ),

            "does_not_own": (
                "dependency graph construction semantics",
                "dependency semantic validation semantics",
                "cycle detection semantics",
                "runnable-stage semantics",
                "execution planning semantics",
                "topological full-workflow planning",
                "Runtime Registration",
                "Runtime jobs",
                "Runtime dispatch",
                "worker selection",
                "stage result handoff",
                "advanced orchestration",
                "workflow persistence",
                "workflow recovery",
            ),

            "fingerprint_policy": {
                "algorithm":
                    "SHA256",

                "covers":
                    "Phase 4.1-4.5 production source SHAs and versions",

                "includes_phase_4_6":
                    False,

                "reason_phase_4_6_excluded":
                    "avoid self-referential certification hash",
            },

            "failure_policy": {
                "mode":
                    "fail_closed",

                "failed_check":
                    "certification failure",

                "exception":
                    "PlanningCertificationFailedError",
            },

            "deep_chain_policy": {
                "node_count":
                    PLANNING_CERTIFICATION_DEEP_CHAIN_NODE_COUNT,

                "purpose":
                    (
                        "prevent regression of the "
                        "Phase 4.3 recursion-depth defect"
                    ),
            },

            "execution_properties": {
                "read_only":
                    True,

                "deterministic":
                    True,

                "graph_mutation":
                    False,

                "workflow_mutation":
                    False,

                "runtime_execution":
                    False,

                "runtime_job_creation":
                    False,

                "dispatch":
                    False,

                "persistence":
                    False,

                "recovery":
                    False,
            },

            "future_authority": {
                "5.0":
                    "Runtime Integration",

                "6.0":
                    "Stage Handoff",

                "7.0":
                    "Advanced Orchestration",

                "8.0":
                    "Workflow State Persistence",

                "9.0":
                    "Coordination Recovery",
            },
        }
    )


__all__ = (
    "PLANNING_CERTIFICATION_VERSION",
    "PLANNING_CERTIFICATION_SCHEMA_VERSION",
    "PLANNING_CERTIFICATION_CHECK_FIELD_COUNT",
    "PLANNING_CERTIFICATION_RESULT_FIELD_COUNT",
    "PLANNING_CERTIFICATION_DEEP_CHAIN_NODE_COUNT",
    "PlanningCertificationError",
    "PlanningCertificationFailedError",
    "PlanningCertificationCheck",
    "PlanningCertificationResult",
    "certify_dependency_planning",
    "planning_certification_snapshot",
    "explain_planning_certification_v4_6",
)
