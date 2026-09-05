from __future__ import annotations

import ast
import hashlib
import inspect
from dataclasses import FrozenInstanceError, fields
from pathlib import Path
from types import MappingProxyType

from backend.server.coordination.dependency_planning.execution_planner import (
    ExecutionPlan,
    ExecutionWave,
)

from backend.server.coordination.universal_stages.contract import (
    UniversalStageReference,
)

import backend.server.coordination.runtime_integration.coordination_runtime_bridge as bridge

from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
    COORDINATION_RUNTIME_BRIDGE_VERSION,
    COORDINATION_RUNTIME_BRIDGE_SCHEMA_VERSION,
    RUNTIME_HANDOFF_CONTEXT_VERSION,
    RUNTIME_HANDOFF_INTENT_VERSION,
    RUNTIME_HANDOFF_CONTEXT_FIELD_COUNT,
    RUNTIME_HANDOFF_INTENT_FIELD_COUNT,
    COORDINATION_RUNTIME_BRIDGE_RESULT_FIELD_COUNT,
    UNIVERSAL_RUNTIME_EXECUTION_TARGET,
    CoordinationRuntimeBridgeError,
    CoordinationRuntimeBridgeValidationError,
    RuntimeHandoffContext,
    RuntimeHandoffIntent,
    CoordinationRuntimeBridgeResult,
    create_runtime_handoff_context,
    bridge_execution_plan_to_runtime,
    coordination_runtime_bridge_snapshot,
    explain_coordination_runtime_bridge_v5_1,
)


ROOT = Path.cwd()

BRIDGE = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "coordination_runtime_bridge.py"
)

REPORT = (
    ROOT
    / "coordination_runtime_bridge_phase_5_1_initial_verification.txt"
)


EXPECTED_SHA = (
    "2DD7AF262C879B4DD58A484AB7470D9E"
    "A9883A80DDE3C77F1DC1ACDFD35CD0E2"
)


checks = []


def check(
    name,
    condition,
    detail="",
):
    ok = bool(
        condition
    )

    checks.append(
        (
            name,
            ok,
            detail,
        )
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        print(
            f"       {detail}"
        )


def sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def expect_validation_error(
    name,
    callable_obj,
    expected_fragment=None,
):
    try:
        callable_obj()

    except CoordinationRuntimeBridgeValidationError as exc:

        ok = True

        detail = (
            str(
                exc
            )
        )

        if expected_fragment is not None:
            ok = (
                expected_fragment.lower()
                in detail.lower()
                or any(
                    expected_fragment.lower()
                    in item.lower()
                    for item
                    in getattr(
                        exc,
                        "violations",
                        (),
                    )
                )
            )

        check(
            name,
            ok,
            detail,
        )

        return

    except Exception as exc:

        check(
            name,
            False,
            "Unexpected exception type: "
            + repr(
                exc
            ),
        )

        return

    check(
        name,
        False,
        "Expected CoordinationRuntimeBridgeValidationError.",
    )


def make_reference(
    *,
    stage_id,
    execution_target="UNIVERSAL_RUNTIME",
    required_payload_fields=(),
    job_type=None,
    runtime_stage=None,
    pipeline_id="verify_pipeline",
):
    return UniversalStageReference(
        stage_id=stage_id,
        stage_version=f"{stage_id}_v1",
        pipeline_id=pipeline_id,
        workflow_type="verify_workflow",
        workflow_contract_version=(
            "universal_workflow_contract_v1.1.0"
        ),
        execution_target=execution_target,
        job_type=(
            job_type
            if job_type is not None
            else f"verify.{stage_id}"
        ),
        runtime_stage=(
            runtime_stage
            if runtime_stage is not None
            else stage_id
        ),
        required_payload_fields=(
            required_payload_fields
        ),
        metadata={
            "source": "initial_verification",
            "stage": stage_id,
        },
    )


def make_plan(
    *,
    workflow_id="wf_verify",
    waves=(),
    planned_stage_ids=(),
):
    return ExecutionPlan(
        workflow_id=workflow_id,
        wave_count=len(
            waves
        ),
        waves=waves,
        planned_stage_ids=planned_stage_ids,
        graph_version="dependency_graph_v4.1.0",
        cycle_detection_version="cycle_detection_v4.3.0",
        runnable_stage_resolver_version=(
            "runnable_stage_resolver_v4.4.0"
        ),
        planner_version=(
            "execution_planner_v4.5.0"
        ),
    )


print()
print("=" * 116)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.1 — COORDINATION → RUNTIME BRIDGE")
print("INITIAL VERIFICATION")
print("=" * 116)


# =========================================================================
# 1. Production identity / SHA
# =========================================================================

check(
    "Bridge production file exists",
    BRIDGE.exists(),
)

current_sha = sha256(
    BRIDGE
)

check(
    "Bridge candidate SHA exact",
    current_sha
    == EXPECTED_SHA,
    current_sha,
)

check(
    "Bridge version exact",
    COORDINATION_RUNTIME_BRIDGE_VERSION
    == "coordination_runtime_bridge_v5.1.0",
)

check(
    "Bridge schema exact",
    COORDINATION_RUNTIME_BRIDGE_SCHEMA_VERSION
    == "coordination_runtime_bridge_schema_v1",
)

check(
    "Context version exact",
    RUNTIME_HANDOFF_CONTEXT_VERSION
    == "runtime_handoff_context_v5.1.0",
)

check(
    "Intent version exact",
    RUNTIME_HANDOFF_INTENT_VERSION
    == "runtime_handoff_intent_v5.1.0",
)

check(
    "Runtime execution target constant exact",
    UNIVERSAL_RUNTIME_EXECUTION_TARGET
    == "UNIVERSAL_RUNTIME",
)


# =========================================================================
# 2. Public API surface
# =========================================================================

expected_public = {
    "COORDINATION_RUNTIME_BRIDGE_VERSION",
    "COORDINATION_RUNTIME_BRIDGE_SCHEMA_VERSION",
    "RUNTIME_HANDOFF_CONTEXT_VERSION",
    "RUNTIME_HANDOFF_INTENT_VERSION",
    "RUNTIME_HANDOFF_CONTEXT_FIELD_COUNT",
    "RUNTIME_HANDOFF_INTENT_FIELD_COUNT",
    "COORDINATION_RUNTIME_BRIDGE_RESULT_FIELD_COUNT",
    "UNIVERSAL_RUNTIME_EXECUTION_TARGET",
    "CoordinationRuntimeBridgeError",
    "CoordinationRuntimeBridgeValidationError",
    "RuntimeHandoffContext",
    "RuntimeHandoffIntent",
    "CoordinationRuntimeBridgeResult",
    "create_runtime_handoff_context",
    "bridge_execution_plan_to_runtime",
    "coordination_runtime_bridge_snapshot",
    "explain_coordination_runtime_bridge_v5_1",
}

actual_public = set(
    bridge.__all__
)

check(
    "__all__ exact",
    actual_public
    == expected_public,
    repr(
        sorted(
            actual_public
        )
    ),
)

check(
    "No Runtime execution function exported",
    not any(
        name in actual_public
        for name
        in (
            "dispatch",
            "dispatch_job",
            "execute_job",
            "execute_registered_runtime_job_v1",
            "create_universal_job",
            "register_runtime_handler",
            "get_runtime_registration",
        )
    ),
)


# =========================================================================
# 3. Field counts
# =========================================================================

check(
    "RuntimeHandoffContext field count exact",
    len(
        fields(
            RuntimeHandoffContext
        )
    )
    == RUNTIME_HANDOFF_CONTEXT_FIELD_COUNT
    == 6,
)

check(
    "RuntimeHandoffIntent field count exact",
    len(
        fields(
            RuntimeHandoffIntent
        )
    )
    == RUNTIME_HANDOFF_INTENT_FIELD_COUNT
    == 16,
)

check(
    "CoordinationRuntimeBridgeResult field count exact",
    len(
        fields(
            CoordinationRuntimeBridgeResult
        )
    )
    == COORDINATION_RUNTIME_BRIDGE_RESULT_FIELD_COUNT
    == 8,
)


# =========================================================================
# 4. Context validation
# =========================================================================

expect_validation_error(
    "Context rejects empty workflow_id",
    lambda: create_runtime_handoff_context(
        workflow_id="",
        workspace_id="ws",
        correlation_id="corr",
    ),
    "workflow_id",
)

expect_validation_error(
    "Context rejects empty workspace_id",
    lambda: create_runtime_handoff_context(
        workflow_id="wf",
        workspace_id="",
        correlation_id="corr",
    ),
    "workspace_id",
)

expect_validation_error(
    "Context rejects empty correlation_id",
    lambda: create_runtime_handoff_context(
        workflow_id="wf",
        workspace_id="ws",
        correlation_id="",
    ),
    "correlation_id",
)

expect_validation_error(
    "Context rejects non-mapping payload_by_stage",
    lambda: RuntimeHandoffContext(
        workflow_id="wf",
        workspace_id="ws",
        correlation_id="corr",
        payload_by_stage=(
            "not",
            "mapping",
        ),
    ),
    "payload_by_stage",
)

expect_validation_error(
    "Context rejects non-mapping metadata",
    lambda: RuntimeHandoffContext(
        workflow_id="wf",
        workspace_id="ws",
        correlation_id="corr",
        metadata=(
            "not",
            "mapping",
        ),
    ),
    "metadata",
)


# =========================================================================
# 5. Immutable context
# =========================================================================

context = create_runtime_handoff_context(
    workflow_id="wf_verify",
    workspace_id="ws_verify",
    correlation_id="corr_verify",
    payload_by_stage={
        "stage_a": {
            "document_id": "doc_a",
            "url": "https://example.com/a",
        },
        "stage_b": {
            "document_id": "doc_b",
        },
        "stage_c": {
            "document_id": "doc_c",
        },
    },
    metadata={
        "request_source": "initial_verification",
        "nested": {
            "enabled": True,
        },
    },
)

check(
    "Context outer payload mapping immutable",
    isinstance(
        context.payload_by_stage,
        MappingProxyType,
    ),
)

check(
    "Context nested payload mapping immutable",
    isinstance(
        context.payload_by_stage[
            "stage_a"
        ],
        MappingProxyType,
    ),
)

check(
    "Context metadata immutable",
    isinstance(
        context.metadata,
        MappingProxyType,
    ),
)

check(
    "Context nested metadata immutable",
    isinstance(
        context.metadata[
            "nested"
        ],
        MappingProxyType,
    ),
)

mutation_blocked = False

try:
    context.metadata[
        "x"
    ] = 1

except TypeError:
    mutation_blocked = True

check(
    "Context metadata mutation blocked",
    mutation_blocked,
)


# =========================================================================
# 6. Empty execution plan
# =========================================================================

empty_plan = make_plan(
    workflow_id="wf_verify",
)

empty_result = bridge_execution_plan_to_runtime(
    execution_plan=empty_plan,
    stage_references={},
    context=context,
)

check(
    "Empty plan is valid",
    empty_result.handoff_count
    == 0,
)

check(
    "Empty plan returns no intents",
    empty_result.intents
    == (),
)

check(
    "Empty plan preserves workflow identity",
    empty_result.workflow_id
    == "wf_verify",
)


# =========================================================================
# 7. Parallel immediate execution wave
# =========================================================================

parallel_plan = make_plan(
    workflow_id="wf_verify",
    waves=(
        ExecutionWave(
            wave_index=0,
            stage_ids=(
                "stage_a",
                "stage_b",
                "stage_c",
            ),
            execution_semantics=(
                "parallel_eligible"
            ),
        ),
    ),
    planned_stage_ids=(
        "stage_a",
        "stage_b",
        "stage_c",
    ),
)

references = {
    "stage_a": make_reference(
        stage_id="stage_a",
        required_payload_fields=(
            "document_id",
            "url",
        ),
    ),
    "stage_b": make_reference(
        stage_id="stage_b",
        required_payload_fields=(
            "document_id",
        ),
    ),
    "stage_c": make_reference(
        stage_id="stage_c",
        required_payload_fields=(
            "document_id",
        ),
    ),
}

parallel_result = bridge_execution_plan_to_runtime(
    execution_plan=parallel_plan,
    stage_references=references,
    context=context,
)

check(
    "Parallel wave produces three intents",
    parallel_result.handoff_count
    == 3,
)

check(
    "Parallel wave stage ordering preserved",
    tuple(
        intent.stage_id
        for intent
        in parallel_result.intents
    )
    == (
        "stage_a",
        "stage_b",
        "stage_c",
    ),
)

check(
    "Parallel wave index preserved for all intents",
    tuple(
        intent.wave_index
        for intent
        in parallel_result.intents
    )
    == (
        0,
        0,
        0,
    ),
)

check(
    "Parallel execution semantics preserved",
    tuple(
        intent.execution_semantics
        for intent
        in parallel_result.intents
    )
    == (
        "parallel_eligible",
        "parallel_eligible",
        "parallel_eligible",
    ),
)

check(
    "Stage Reference job types preserved",
    tuple(
        intent.job_type
        for intent
        in parallel_result.intents
    )
    == (
        "verify.stage_a",
        "verify.stage_b",
        "verify.stage_c",
    ),
)

check(
    "Runtime stage identities preserved",
    tuple(
        intent.runtime_stage
        for intent
        in parallel_result.intents
    )
    == (
        "stage_a",
        "stage_b",
        "stage_c",
    ),
)


# =========================================================================
# 8. Multiple-wave structural preservation
# =========================================================================

multi_wave_plan = make_plan(
    workflow_id="wf_verify",
    waves=(
        ExecutionWave(
            wave_index=0,
            stage_ids=(
                "stage_a",
                "stage_b",
            ),
            execution_semantics="parallel_eligible",
        ),
        ExecutionWave(
            wave_index=1,
            stage_ids=(
                "stage_c",
            ),
            execution_semantics="parallel_eligible",
        ),
    ),
    planned_stage_ids=(
        "stage_a",
        "stage_b",
        "stage_c",
    ),
)

multi_wave_result = bridge_execution_plan_to_runtime(
    execution_plan=multi_wave_plan,
    stage_references=references,
    context=context,
)

check(
    "Multiple wave count preserved",
    multi_wave_result.wave_count
    == 2,
)

check(
    "Multiple wave indexes preserved",
    tuple(
        intent.wave_index
        for intent
        in multi_wave_result.intents
    )
    == (
        0,
        0,
        1,
    ),
)


# =========================================================================
# 9. Determinism
# =========================================================================

repeat_a = bridge_execution_plan_to_runtime(
    execution_plan=parallel_plan,
    stage_references=references,
    context=context,
)

repeat_b = bridge_execution_plan_to_runtime(
    execution_plan=parallel_plan,
    stage_references=references,
    context=context,
)

check(
    "Repeated handoff results deterministic",
    repeat_a
    == repeat_b,
)

check(
    "Repeated snapshots deterministic",
    dict(
        coordination_runtime_bridge_snapshot(
            repeat_a
        )
    )
    == dict(
        coordination_runtime_bridge_snapshot(
            repeat_b
        )
    ),
)


# =========================================================================
# 10. Fail-closed workflow identity
# =========================================================================

wrong_context = create_runtime_handoff_context(
    workflow_id="wf_other",
    workspace_id="ws_verify",
    correlation_id="corr_verify",
)

expect_validation_error(
    "Bridge rejects workflow ID mismatch",
    lambda: bridge_execution_plan_to_runtime(
        execution_plan=parallel_plan,
        stage_references=references,
        context=wrong_context,
    ),
    "workflow",
)


# =========================================================================
# 11. Fail-closed Stage Reference coverage
# =========================================================================

expect_validation_error(
    "Bridge rejects missing Stage Reference",
    lambda: bridge_execution_plan_to_runtime(
        execution_plan=parallel_plan,
        stage_references={
            "stage_a": references[
                "stage_a"
            ],
            "stage_b": references[
                "stage_b"
            ],
        },
        context=context,
    ),
    "missing Stage Reference",
)


# =========================================================================
# 12. Mapping key integrity
# =========================================================================

expect_validation_error(
    "Bridge rejects Stage Reference mapping-key mismatch",
    lambda: bridge_execution_plan_to_runtime(
        execution_plan=make_plan(
            workflow_id="wf_verify",
            waves=(
                ExecutionWave(
                    wave_index=0,
                    stage_ids=(
                        "stage_a",
                    ),
                    execution_semantics="parallel_eligible",
                ),
            ),
            planned_stage_ids=(
                "stage_a",
            ),
        ),
        stage_references={
            "wrong_key": references[
                "stage_a"
            ],
        },
        context=context,
    ),
    "mapping key",
)


# =========================================================================
# 13. Execution target protection
# =========================================================================

coordination_only = make_reference(
    stage_id="stage_a",
    execution_target="COORDINATION_ONLY",
    required_payload_fields=(),
    job_type="",
    runtime_stage="",
)

expect_validation_error(
    "Bridge rejects COORDINATION_ONLY stage",
    lambda: bridge_execution_plan_to_runtime(
        execution_plan=make_plan(
            workflow_id="wf_verify",
            waves=(
                ExecutionWave(
                    wave_index=0,
                    stage_ids=(
                        "stage_a",
                    ),
                    execution_semantics="parallel_eligible",
                ),
            ),
            planned_stage_ids=(
                "stage_a",
            ),
        ),
        stage_references={
            "stage_a": coordination_only,
        },
        context=context,
    ),
    "UNIVERSAL_RUNTIME",
)


# =========================================================================
# 14. Required payload enforcement
# =========================================================================

missing_payload_context = (
    create_runtime_handoff_context(
        workflow_id="wf_verify",
        workspace_id="ws_verify",
        correlation_id="corr_verify",
        payload_by_stage={
            "stage_a": {
                "document_id": "doc_a",
            },
        },
    )
)

expect_validation_error(
    "Bridge rejects missing required payload field",
    lambda: bridge_execution_plan_to_runtime(
        execution_plan=make_plan(
            workflow_id="wf_verify",
            waves=(
                ExecutionWave(
                    wave_index=0,
                    stage_ids=(
                        "stage_a",
                    ),
                    execution_semantics="parallel_eligible",
                ),
            ),
            planned_stage_ids=(
                "stage_a",
            ),
        ),
        stage_references={
            "stage_a": references[
                "stage_a"
            ],
        },
        context=missing_payload_context,
    ),
    "missing required payload field",
)


null_payload_context = (
    create_runtime_handoff_context(
        workflow_id="wf_verify",
        workspace_id="ws_verify",
        correlation_id="corr_verify",
        payload_by_stage={
            "stage_a": {
                "document_id": "doc_a",
                "url": None,
            },
        },
    )
)

expect_validation_error(
    "Bridge treats None required payload as missing",
    lambda: bridge_execution_plan_to_runtime(
        execution_plan=make_plan(
            workflow_id="wf_verify",
            waves=(
                ExecutionWave(
                    wave_index=0,
                    stage_ids=(
                        "stage_a",
                    ),
                    execution_semantics="parallel_eligible",
                ),
            ),
            planned_stage_ids=(
                "stage_a",
            ),
        ),
        stage_references={
            "stage_a": references[
                "stage_a"
            ],
        },
        context=null_payload_context,
    ),
    "missing required payload field",
)


# =========================================================================
# 15. Malformed plan protection
# =========================================================================

malformed_flattened = ExecutionPlan(
    workflow_id="wf_verify",
    wave_count=1,
    waves=(
        ExecutionWave(
            wave_index=0,
            stage_ids=(
                "stage_a",
            ),
            execution_semantics="parallel_eligible",
        ),
    ),
    planned_stage_ids=(
        "stage_b",
    ),
    graph_version="dependency_graph_v4.1.0",
    cycle_detection_version="cycle_detection_v4.3.0",
    runnable_stage_resolver_version=(
        "runnable_stage_resolver_v4.4.0"
    ),
    planner_version="execution_planner_v4.5.0",
)

expect_validation_error(
    "Bridge rejects plan/wave stage mismatch",
    lambda: bridge_execution_plan_to_runtime(
        execution_plan=malformed_flattened,
        stage_references=references,
        context=context,
    ),
    "planned_stage_ids",
)


duplicate_plan = ExecutionPlan(
    workflow_id="wf_verify",
    wave_count=1,
    waves=(
        ExecutionWave(
            wave_index=0,
            stage_ids=(
                "stage_a",
                "stage_a",
            ),
            execution_semantics="parallel_eligible",
        ),
    ),
    planned_stage_ids=(
        "stage_a",
        "stage_a",
    ),
    graph_version="dependency_graph_v4.1.0",
    cycle_detection_version="cycle_detection_v4.3.0",
    runnable_stage_resolver_version=(
        "runnable_stage_resolver_v4.4.0"
    ),
    planner_version="execution_planner_v4.5.0",
)

expect_validation_error(
    "Bridge rejects duplicate planned stage IDs",
    lambda: bridge_execution_plan_to_runtime(
        execution_plan=duplicate_plan,
        stage_references=references,
        context=context,
    ),
    "unique",
)


# =========================================================================
# 16. Result / intent immutability
# =========================================================================

intent = parallel_result.intents[
    0
]

blocked = False

try:
    intent.stage_id = "mutated"

except (
    FrozenInstanceError,
    AttributeError,
):
    blocked = True

check(
    "Intent dataclass frozen",
    blocked,
)

blocked = False

try:
    parallel_result.workflow_id = "mutated"

except (
    FrozenInstanceError,
    AttributeError,
):
    blocked = True

check(
    "Bridge result dataclass frozen",
    blocked,
)

blocked = False

try:
    intent.payload[
        "document_id"
    ] = "mutated"

except TypeError:
    blocked = True

check(
    "Intent payload deeply immutable",
    blocked,
)


# =========================================================================
# 17. Snapshot semantics
# =========================================================================

snapshot = coordination_runtime_bridge_snapshot(
    parallel_result
)

check(
    "Snapshot is immutable mapping",
    isinstance(
        snapshot,
        MappingProxyType,
    ),
)

check(
    "Snapshot handoff count preserved",
    snapshot[
        "handoff_count"
    ]
    == 3,
)

check(
    "Snapshot intent entries immutable",
    all(
        isinstance(
            item,
            MappingProxyType,
        )
        for item
        in snapshot[
            "intents"
        ]
    ),
)


# =========================================================================
# 18. Architecture declaration
# =========================================================================

architecture = (
    explain_coordination_runtime_bridge_v5_1()
)

check(
    "Architecture declaration immutable",
    isinstance(
        architecture,
        MappingProxyType,
    ),
)

check(
    "Upstream authority exact",
    architecture[
        "upstream_authority"
    ]
    == "Phase 4.5 ExecutionPlan",
)

check(
    "Downstream authority exact",
    architecture[
        "downstream_authority"
    ]
    == "Phase 5.2 Runtime Job Mapping",
)

check(
    "Canonical operation exact",
    architecture[
        "canonical_operation"
    ]
    == "bridge_execution_plan_to_runtime",
)


properties = architecture[
    "execution_properties"
]

check(
    "Read-only authority true",
    properties[
        "read_only"
    ] is True,
)

check(
    "Deterministic authority true",
    properties[
        "deterministic"
    ] is True,
)

check(
    "Fail-closed authority true",
    properties[
        "fail_closed"
    ] is True,
)

for forbidden in (
    "workflow_mutation",
    "runtime_job_creation",
    "runtime_registration_lookup",
    "dispatch",
    "business_execution",
    "persistence",
    "queue_write",
    "completion_processing",
    "failure_processing",
):
    check(
        f"Forbidden authority false: {forbidden}",
        properties[
            forbidden
        ] is False,
    )


# =========================================================================
# 19. Static architecture / imports
# =========================================================================

source = BRIDGE.read_text(
    encoding="utf-8"
)

tree = ast.parse(
    source
)

runtime_imports = []

for node in ast.walk(
    tree
):

    if isinstance(
        node,
        ast.ImportFrom,
    ):
        module = (
            node.module
            or ""
        )

        if module.startswith(
            "backend.server.runtime"
        ):
            runtime_imports.append(
                module
            )

    elif isinstance(
        node,
        ast.Import,
    ):

        for alias in node.names:

            if alias.name.startswith(
                "backend.server.runtime"
            ):
                runtime_imports.append(
                    alias.name
                )


check(
    "No backend.server.runtime imports",
    runtime_imports
    == [],
    repr(
        runtime_imports
    ),
)


forbidden_runtime_calls = {
    "create_universal_job",
    "register_runtime_handler",
    "get_runtime_registration",
    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",
    "update_job_status",
    "update_job_progress",
    "record_job_failure",
}

called_names = set()

for node in ast.walk(
    tree
):

    if not isinstance(
        node,
        ast.Call,
    ):
        continue

    func = node.func

    if isinstance(
        func,
        ast.Name,
    ):
        called_names.add(
            func.id
        )

    elif isinstance(
        func,
        ast.Attribute,
    ):
        called_names.add(
            func.attr
        )


forbidden_hits = (
    called_names
    & forbidden_runtime_calls
)

check(
    "No forbidden Runtime calls",
    forbidden_hits
    == set(),
    repr(
        sorted(
            forbidden_hits
        )
    ),
)


# =========================================================================
# 20. No persistence/queue I/O primitives
# =========================================================================

forbidden_io_names = {
    "open",
    "write_text",
    "write_bytes",
    "mkdir",
    "unlink",
    "rename",
    "replace",
    "touch",
}

io_hits = (
    called_names
    & forbidden_io_names
)

check(
    "Bridge performs no filesystem writes",
    io_hits
    == set(),
    repr(
        sorted(
            io_hits
        )
    ),
)


# =========================================================================
# 21. Function signatures
# =========================================================================

check(
    "Context factory signature keyword-only",
    str(
        inspect.signature(
            create_runtime_handoff_context
        )
    ).startswith(
        "(*,"
    ),
)

check(
    "Bridge operation signature keyword-only",
    str(
        inspect.signature(
            bridge_execution_plan_to_runtime
        )
    ).startswith(
        "(*,"
    ),
)


# =========================================================================
# 22. Error hierarchy
# =========================================================================

check(
    "Validation error subclasses bridge error",
    issubclass(
        CoordinationRuntimeBridgeValidationError,
        CoordinationRuntimeBridgeError,
    ),
)

check(
    "Bridge error subclasses ValueError",
    issubclass(
        CoordinationRuntimeBridgeError,
        ValueError,
    ),
)


# =========================================================================
# 23. Source markers
# =========================================================================

check(
    "ASCII-safe canonical component marker present",
    "Coordination -> Runtime Bridge"
    in source,
)

check(
    "No Unicode replacement character",
    "\ufffd"
    not in source,
)

check(
    "Phase 5.2 downstream marker present",
    "Phase 5.2 Runtime Job Mapping"
    in source,
)

check(
    "No UniversalJob import",
    "UniversalJob"
    not in "\n".join(
        line
        for line
        in source.splitlines()
        if line.strip().startswith(
            (
                "from ",
                "import ",
            )
        )
    ),
)


# =========================================================================
# Final result
# =========================================================================

passed = sum(
    1
    for _, ok, _
    in checks
    if ok
)

failed = (
    len(
        checks
    )
    - passed
)


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.1 — COORDINATION → RUNTIME BRIDGE",
    "INITIAL VERIFICATION",
    "=" * 116,
    "",
]

for (
    name,
    ok,
    detail,
) in checks:

    lines.append(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        lines.append(
            "    "
            + detail
        )


lines.extend(
    (
        "",
        "=" * 116,
        "INITIAL VERIFICATION RESULT",
        "=" * 116,
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        (
            "STATUS: INITIAL VERIFICATION PASSED"
            if failed == 0
            else "STATUS: INITIAL VERIFICATION FAILED"
        ),
        f"PHASE 5.1 SHA256: {current_sha}",
    )
)


REPORT.write_text(
    "\n".join(
        lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 116)
print("PHASE 5.1 INITIAL VERIFICATION RESULT")
print("=" * 116)
print(
    "Checks:",
    len(
        checks
    ),
)
print(
    "Passed:",
    passed,
)
print(
    "Failed:",
    failed,
)
print(
    "STATUS:",
    (
        "INITIAL VERIFICATION PASSED"
        if failed == 0
        else "INITIAL VERIFICATION FAILED"
    ),
)
print(
    "PHASE 5.1 SHA256:",
    current_sha,
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 116)

raise SystemExit(
    0
    if failed == 0
    else 1
)
