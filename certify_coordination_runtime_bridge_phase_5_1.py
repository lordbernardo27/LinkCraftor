from __future__ import annotations

import ast
import hashlib
import inspect
import subprocess
from dataclasses import fields
from pathlib import Path
from types import MappingProxyType

from backend.server.coordination.dependency_planning.execution_planner import (
    ExecutionPlan,
    ExecutionWave,
)

from backend.server.coordination.universal_stages.contract import (
    UniversalStageReference,
)

from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
    COORDINATION_RUNTIME_BRIDGE_VERSION,
    COORDINATION_RUNTIME_BRIDGE_SCHEMA_VERSION,
    RUNTIME_HANDOFF_CONTEXT_VERSION,
    RUNTIME_HANDOFF_INTENT_VERSION,
    RUNTIME_HANDOFF_CONTEXT_FIELD_COUNT,
    RUNTIME_HANDOFF_INTENT_FIELD_COUNT,
    COORDINATION_RUNTIME_BRIDGE_RESULT_FIELD_COUNT,
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

INIT = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "__init__.py"
)

REPORT = (
    ROOT
    / "coordination_runtime_bridge_phase_5_1_final_certification.txt"
)


EXPECTED_SHA = (
    "2DD7AF262C879B4DD58A484AB7470D9E"
    "A9883A80DDE3C77F1DC1ACDFD35CD0E2"
)


FROZEN_UPSTREAM = {
    "execution_planner": (
        ROOT
        / "backend/server/coordination/dependency_planning/"
          "execution_planner.py",
        "808743F566978530B2FC774DBD70A5FFA820F0EFE431512E882E0CF0F7B81958",
    ),
    "stage_reference": (
        ROOT
        / "backend/server/coordination/universal_stages/"
          "contract.py",
        "EAECFC26666CDE338ED2D3988A312B3812AB85B82F588EACD0D97633F656D00F",
    ),
}


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
            "       "
            + detail
        )


def sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def expect_bridge_error(
    name,
    fn,
):
    try:
        fn()

    except CoordinationRuntimeBridgeValidationError:
        check(
            name,
            True,
        )
        return

    except Exception as exc:
        check(
            name,
            False,
            "Unexpected exception: "
            + repr(
                exc
            ),
        )
        return

    check(
        name,
        False,
        "Expected bridge validation error.",
    )


def ref(
    stage_id,
    *,
    required=(),
):
    return UniversalStageReference(
        stage_id=stage_id,
        stage_version=f"{stage_id}_v1",
        pipeline_id="cert_pipeline",
        workflow_type="cert_workflow",
        workflow_contract_version=(
            "universal_workflow_contract_v1.1.0"
        ),
        execution_target="UNIVERSAL_RUNTIME",
        job_type=f"cert.{stage_id}",
        runtime_stage=stage_id,
        required_payload_fields=required,
        metadata={
            "certification": True,
        },
    )


def plan(
    stage_ids=(),
):
    if not stage_ids:
        return ExecutionPlan(
            workflow_id="wf_cert_5_1",
            wave_count=0,
            waves=(),
            planned_stage_ids=(),
            graph_version="dependency_graph_v4.1.0",
            cycle_detection_version="cycle_detection_v4.3.0",
            runnable_stage_resolver_version=(
                "runnable_stage_resolver_v4.4.0"
            ),
            planner_version="execution_planner_v4.5.0",
        )

    return ExecutionPlan(
        workflow_id="wf_cert_5_1",
        wave_count=1,
        waves=(
            ExecutionWave(
                wave_index=0,
                stage_ids=tuple(
                    stage_ids
                ),
                execution_semantics=(
                    "parallel_eligible"
                ),
            ),
        ),
        planned_stage_ids=tuple(
            stage_ids
        ),
        graph_version="dependency_graph_v4.1.0",
        cycle_detection_version="cycle_detection_v4.3.0",
        runnable_stage_resolver_version=(
            "runnable_stage_resolver_v4.4.0"
        ),
        planner_version="execution_planner_v4.5.0",
    )


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.1 — COORDINATION -> RUNTIME BRIDGE")
print("FINAL CERTIFICATION")
print("=" * 120)


# =========================================================================
# A. Production artifact identity
# =========================================================================

check(
    "Production bridge exists",
    BRIDGE.exists(),
)

check(
    "Runtime integration package exists",
    INIT.exists(),
)

current_sha = sha256(
    BRIDGE
)

check(
    "Production SHA exact",
    current_sha
    == EXPECTED_SHA,
    current_sha,
)

check(
    "Production SHA structurally valid",
    len(
        current_sha
    )
    == 64,
)


# =========================================================================
# B. Frozen upstream integrity
# =========================================================================

for (
    name,
    (
        path,
        expected,
    ),
) in FROZEN_UPSTREAM.items():

    actual = sha256(
        path
    )

    check(
        f"Frozen upstream exact: {name}",
        actual
        == expected,
        actual,
    )


# =========================================================================
# C. Contract/version identity
# =========================================================================

check(
    "Bridge version certified",
    COORDINATION_RUNTIME_BRIDGE_VERSION
    == "coordination_runtime_bridge_v5.1.0",
)

check(
    "Bridge schema certified",
    COORDINATION_RUNTIME_BRIDGE_SCHEMA_VERSION
    == "coordination_runtime_bridge_schema_v1",
)

check(
    "Context version certified",
    RUNTIME_HANDOFF_CONTEXT_VERSION
    == "runtime_handoff_context_v5.1.0",
)

check(
    "Intent version certified",
    RUNTIME_HANDOFF_INTENT_VERSION
    == "runtime_handoff_intent_v5.1.0",
)


# =========================================================================
# D. Contract shape
# =========================================================================

check(
    "Context field count certified",
    len(
        fields(
            RuntimeHandoffContext
        )
    )
    == RUNTIME_HANDOFF_CONTEXT_FIELD_COUNT
    == 6,
)

check(
    "Intent field count certified",
    len(
        fields(
            RuntimeHandoffIntent
        )
    )
    == RUNTIME_HANDOFF_INTENT_FIELD_COUNT
    == 16,
)

check(
    "Result field count certified",
    len(
        fields(
            CoordinationRuntimeBridgeResult
        )
    )
    == COORDINATION_RUNTIME_BRIDGE_RESULT_FIELD_COUNT
    == 8,
)


# =========================================================================
# E. Certified empty-wave behavior
# =========================================================================

context = create_runtime_handoff_context(
    workflow_id="wf_cert_5_1",
    workspace_id="ws_cert",
    correlation_id="corr_cert",
)

empty_result = bridge_execution_plan_to_runtime(
    execution_plan=plan(),
    stage_references={},
    context=context,
)

check(
    "Empty immediate plan accepted",
    empty_result.handoff_count
    == 0,
)

check(
    "Empty immediate plan creates no intents",
    empty_result.intents
    == (),
)


# =========================================================================
# F. Certified parallel-wave behavior
# =========================================================================

context = create_runtime_handoff_context(
    workflow_id="wf_cert_5_1",
    workspace_id="ws_cert",
    correlation_id="corr_cert",
    payload_by_stage={
        "alpha": {
            "document_id": "doc_alpha",
        },
        "beta": {
            "document_id": "doc_beta",
        },
        "gamma": {
            "document_id": "doc_gamma",
        },
    },
)

refs = {
    name: ref(
        name,
        required=(
            "document_id",
        ),
    )
    for name
    in (
        "alpha",
        "beta",
        "gamma",
    )
}

result = bridge_execution_plan_to_runtime(
    execution_plan=plan(
        (
            "alpha",
            "beta",
            "gamma",
        )
    ),
    stage_references=refs,
    context=context,
)

check(
    "Parallel handoff count certified",
    result.handoff_count
    == 3,
)

check(
    "Parallel stage order certified",
    tuple(
        item.stage_id
        for item
        in result.intents
    )
    == (
        "alpha",
        "beta",
        "gamma",
    ),
)

check(
    "Parallel wave identity certified",
    tuple(
        item.wave_index
        for item
        in result.intents
    )
    == (
        0,
        0,
        0,
    ),
)

check(
    "Parallel semantics certified",
    all(
        item.execution_semantics
        == "parallel_eligible"
        for item
        in result.intents
    ),
)

check(
    "Stage Reference job_type preserved",
    tuple(
        item.job_type
        for item
        in result.intents
    )
    == (
        "cert.alpha",
        "cert.beta",
        "cert.gamma",
    ),
)

check(
    "Runtime stage preserved",
    tuple(
        item.runtime_stage
        for item
        in result.intents
    )
    == (
        "alpha",
        "beta",
        "gamma",
    ),
)


# =========================================================================
# G. Identity preservation
# =========================================================================

check(
    "Workflow identity certified",
    all(
        item.workflow_id
        == "wf_cert_5_1"
        for item
        in result.intents
    ),
)

check(
    "Workspace identity certified",
    all(
        item.workspace_id
        == "ws_cert"
        for item
        in result.intents
    ),
)

check(
    "Correlation identity certified",
    all(
        item.correlation_id
        == "corr_cert"
        for item
        in result.intents
    ),
)


# =========================================================================
# H. Required payload protection
# =========================================================================

bad_context = create_runtime_handoff_context(
    workflow_id="wf_cert_5_1",
    workspace_id="ws_cert",
    correlation_id="corr_cert",
    payload_by_stage={
        "alpha": {},
    },
)

expect_bridge_error(
    "Missing required payload fails closed",
    lambda: bridge_execution_plan_to_runtime(
        execution_plan=plan(
            (
                "alpha",
            )
        ),
        stage_references={
            "alpha": refs[
                "alpha"
            ],
        },
        context=bad_context,
    ),
)


# =========================================================================
# I. Workflow mismatch protection
# =========================================================================

wrong_context = create_runtime_handoff_context(
    workflow_id="wf_wrong",
    workspace_id="ws_cert",
    correlation_id="corr_cert",
)

expect_bridge_error(
    "Workflow mismatch fails closed",
    lambda: bridge_execution_plan_to_runtime(
        execution_plan=plan(),
        stage_references={},
        context=wrong_context,
    ),
)


# =========================================================================
# J. Stage Reference coverage protection
# =========================================================================

expect_bridge_error(
    "Missing Stage Reference fails closed",
    lambda: bridge_execution_plan_to_runtime(
        execution_plan=plan(
            (
                "alpha",
            )
        ),
        stage_references={},
        context=context,
    ),
)


# =========================================================================
# K. Immutability
# =========================================================================

check(
    "Context payload immutable",
    isinstance(
        context.payload_by_stage,
        MappingProxyType,
    ),
)

check(
    "Intent payload immutable",
    all(
        isinstance(
            item.payload,
            MappingProxyType,
        )
        for item
        in result.intents
    ),
)

snapshot = coordination_runtime_bridge_snapshot(
    result
)

check(
    "Snapshot immutable",
    isinstance(
        snapshot,
        MappingProxyType,
    ),
)


# =========================================================================
# L. Determinism
# =========================================================================

repeat = bridge_execution_plan_to_runtime(
    execution_plan=plan(
        (
            "alpha",
            "beta",
            "gamma",
        )
    ),
    stage_references=refs,
    context=context,
)

check(
    "Bridge deterministic across repeated execution",
    result
    == repeat,
)


# =========================================================================
# M. Architecture declaration
# =========================================================================

explain = (
    explain_coordination_runtime_bridge_v5_1()
)

check(
    "Upstream authority certified",
    explain[
        "upstream_authority"
    ]
    == "Phase 4.5 ExecutionPlan",
)

check(
    "Downstream authority certified",
    explain[
        "downstream_authority"
    ]
    == "Phase 5.2 Runtime Job Mapping",
)

check(
    "Canonical operation certified",
    explain[
        "canonical_operation"
    ]
    == "bridge_execution_plan_to_runtime",
)


properties = explain[
    "execution_properties"
]

check(
    "Read-only certified",
    properties[
        "read_only"
    ] is True,
)

check(
    "Deterministic certified",
    properties[
        "deterministic"
    ] is True,
)

check(
    "Fail-closed certified",
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
        f"Forbidden authority absent: {forbidden}",
        properties[
            forbidden
        ] is False,
    )


# =========================================================================
# N. Static boundary certification
# =========================================================================

source = BRIDGE.read_text(
    encoding="utf-8"
)

tree = ast.parse(
    source
)

runtime_imports = []

called_names = set()

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

    elif isinstance(
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


check(
    "No Runtime production imports",
    runtime_imports
    == [],
    repr(
        runtime_imports
    ),
)


runtime_calls = {
    "create_universal_job",
    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",
    "register_runtime_handler",
    "get_runtime_registration",
    "update_job_status",
    "update_job_progress",
    "record_job_failure",
}

check(
    "No Runtime execution calls",
    not bool(
        called_names
        & runtime_calls
    ),
    repr(
        sorted(
            called_names
            & runtime_calls
        )
    ),
)


write_calls = {
    "open",
    "write_text",
    "write_bytes",
    "mkdir",
    "unlink",
    "replace",
    "rename",
    "touch",
}

check(
    "No bridge persistence writes",
    not bool(
        called_names
        & write_calls
    ),
    repr(
        sorted(
            called_names
            & write_calls
        )
    ),
)


# =========================================================================
# O. API boundary signatures
# =========================================================================

check(
    "Context factory keyword-only",
    str(
        inspect.signature(
            create_runtime_handoff_context
        )
    ).startswith(
        "(*,"
    ),
)

check(
    "Bridge operation keyword-only",
    str(
        inspect.signature(
            bridge_execution_plan_to_runtime
        )
    ).startswith(
        "(*,"
    ),
)


# =========================================================================
# P. Error hierarchy
# =========================================================================

check(
    "Validation error hierarchy certified",
    issubclass(
        CoordinationRuntimeBridgeValidationError,
        CoordinationRuntimeBridgeError,
    ),
)

check(
    "Bridge error ValueError-compatible",
    issubclass(
        CoordinationRuntimeBridgeError,
        ValueError,
    ),
)


# =========================================================================
# Q. Git scope certification
# =========================================================================

git_status = subprocess.run(
    [
        "git",
        "status",
        "--short",
        "--",
        "backend/server/coordination/runtime_integration",
        "backend/server/coordination/dependency_planning",
        "backend/server/coordination/universal_stages",
        "backend/server/runtime",
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()


status_lines = tuple(
    line
    for line
    in git_status.splitlines()
    if line.strip()
)

check(
    "No frozen Phase 4 modification in Git status",
    not any(
        "dependency_planning/"
        in line.replace(
            "\\",
            "/",
        )
        for line
        in status_lines
    ),
    repr(
        status_lines
    ),
)

check(
    "No frozen Stage Reference modification in Git status",
    not any(
        "universal_stages/"
        in line.replace(
            "\\",
            "/",
        )
        for line
        in status_lines
    ),
    repr(
        status_lines
    ),
)

check(
    "No Runtime production modification in Git status",
    not any(
        "backend/server/runtime/"
        in line.replace(
            "\\",
            "/",
        )
        for line
        in status_lines
    ),
    repr(
        status_lines
    ),
)

check(
    "Runtime integration package is only new production scope",
    all(
        "backend/server/coordination/runtime_integration/"
        in line.replace(
            "\\",
            "/",
        )
        for line
        in status_lines
    )
    if status_lines
    else False,
    repr(
        status_lines
    ),
)


# =========================================================================
# R. Source identity markers
# =========================================================================

check(
    "Canonical ASCII component marker present",
    "Coordination -> Runtime Bridge"
    in source,
)

check(
    "Phase 5.1 marker present",
    "Phase 5.1"
    in source,
)

check(
    "Phase 5.2 downstream marker present",
    "Phase 5.2 Runtime Job Mapping"
    in source,
)

check(
    "No Unicode replacement character",
    "\ufffd"
    not in source,
)


# =========================================================================
# Certification result
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


certified = (
    failed
    == 0
)


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.1 — COORDINATION -> RUNTIME BRIDGE",
    "FINAL CERTIFICATION",
    "=" * 120,
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
        "=" * 120,
        "FINAL CERTIFICATION RESULT",
        "=" * 120,
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        (
            "CERTIFIED: TRUE"
            if certified
            else "CERTIFIED: FALSE"
        ),
        (
            "STATUS: FINAL CERTIFICATION PASSED"
            if certified
            else "STATUS: FINAL CERTIFICATION FAILED"
        ),
        f"VERSION: {COORDINATION_RUNTIME_BRIDGE_VERSION}",
        f"SCHEMA: {COORDINATION_RUNTIME_BRIDGE_SCHEMA_VERSION}",
        f"SHA256: {current_sha}",
        (
            "NEXT: 5.1.9 SHA256 Freeze"
            if certified
            else "NEXT: Resolve certification failures"
        ),
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
print("=" * 120)
print("PHASE 5.1 FINAL CERTIFICATION RESULT")
print("=" * 120)
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
    "CERTIFIED:",
    certified,
)
print(
    "VERSION:",
    COORDINATION_RUNTIME_BRIDGE_VERSION,
)
print(
    "SCHEMA:",
    COORDINATION_RUNTIME_BRIDGE_SCHEMA_VERSION,
)
print(
    "SHA256:",
    current_sha,
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 120)

raise SystemExit(
    0
    if certified
    else 1
)
