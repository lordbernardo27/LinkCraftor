from __future__ import annotations

import ast
import hashlib
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
    UNIVERSAL_RUNTIME_EXECUTION_TARGET,
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
    / "coordination_runtime_bridge_phase_5_1_installation_smoke.txt"
)


checks = []


def check(name, condition, detail=""):
    ok = bool(condition)

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


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


print()
print("=" * 112)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.1 — COORDINATION → RUNTIME BRIDGE INSTALLATION SMOKE")
print("=" * 112)


# -------------------------------------------------------------------------
# File / syntax
# -------------------------------------------------------------------------

check(
    "Phase 5.1 bridge file exists",
    BRIDGE.exists(),
    str(
        BRIDGE.relative_to(ROOT)
    ),
)

source = BRIDGE.read_text(
    encoding="utf-8"
)

try:
    tree = ast.parse(
        source
    )

    syntax_ok = True

except Exception as exc:
    tree = None
    syntax_ok = False
    syntax_error = repr(
        exc
    )

check(
    "Phase 5.1 Python syntax parses",
    syntax_ok,
    ""
    if syntax_ok
    else syntax_error,
)


# -------------------------------------------------------------------------
# Identity
# -------------------------------------------------------------------------

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
    "Universal Runtime execution target exact",
    UNIVERSAL_RUNTIME_EXECUTION_TARGET
    == "UNIVERSAL_RUNTIME",
)


# -------------------------------------------------------------------------
# Dataclass contracts
# -------------------------------------------------------------------------

context_fields = tuple(
    item.name
    for item
    in fields(
        RuntimeHandoffContext
    )
)

intent_fields = tuple(
    item.name
    for item
    in fields(
        RuntimeHandoffIntent
    )
)

result_fields = tuple(
    item.name
    for item
    in fields(
        CoordinationRuntimeBridgeResult
    )
)


check(
    "Context field count exact",
    len(
        context_fields
    )
    == RUNTIME_HANDOFF_CONTEXT_FIELD_COUNT
    == 6,
)

check(
    "Intent field count exact",
    len(
        intent_fields
    )
    == RUNTIME_HANDOFF_INTENT_FIELD_COUNT
    == 16,
)

check(
    "Result field count exact",
    len(
        result_fields
    )
    == COORDINATION_RUNTIME_BRIDGE_RESULT_FIELD_COUNT
    == 8,
)


# -------------------------------------------------------------------------
# Context construction / immutability
# -------------------------------------------------------------------------

context = create_runtime_handoff_context(
    workflow_id="wf_smoke_5_1",
    workspace_id="ws_smoke",
    correlation_id="corr_smoke",
    payload_by_stage={
        "stage_a": {
            "document_id": "doc_1",
        },
    },
    metadata={
        "source": "phase_5_1_smoke",
    },
)


check(
    "Context type exact",
    isinstance(
        context,
        RuntimeHandoffContext,
    ),
)

check(
    "Context payload mapping immutable",
    isinstance(
        context.payload_by_stage,
        MappingProxyType,
    ),
)

check(
    "Nested stage payload immutable",
    isinstance(
        context.payload_by_stage[
            "stage_a"
        ],
        MappingProxyType,
    ),
)

blocked = False

try:
    context.workspace_id = "mutated"

except Exception:
    blocked = True

check(
    "Context dataclass immutable",
    blocked,
)


# -------------------------------------------------------------------------
# Empty plan behavior
# -------------------------------------------------------------------------

empty_plan = ExecutionPlan(
    workflow_id="wf_smoke_5_1",
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


empty_result = bridge_execution_plan_to_runtime(
    execution_plan=empty_plan,
    stage_references={},
    context=context,
)


check(
    "Empty plan returns bridge result",
    isinstance(
        empty_result,
        CoordinationRuntimeBridgeResult,
    ),
)

check(
    "Empty plan handoff count zero",
    empty_result.handoff_count
    == 0,
)

check(
    "Empty plan intents empty",
    empty_result.intents
    == (),
)

check(
    "Empty plan preserves zero waves",
    empty_result.wave_count
    == 0,
)


# -------------------------------------------------------------------------
# One-stage Runtime handoff
# -------------------------------------------------------------------------

reference = UniversalStageReference(
    stage_id="stage_a",
    stage_version="stage_a_v1",
    pipeline_id="smoke_pipeline",
    workflow_type="smoke_workflow",
    workflow_contract_version=(
        "universal_workflow_contract_v1.1.0"
    ),
    execution_target="UNIVERSAL_RUNTIME",
    job_type="smoke.stage_a",
    runtime_stage="stage_a",
    required_payload_fields=(
        "document_id",
    ),
    metadata={
        "smoke": True,
    },
)


plan = ExecutionPlan(
    workflow_id="wf_smoke_5_1",
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
        "stage_a",
    ),
    graph_version="dependency_graph_v4.1.0",
    cycle_detection_version="cycle_detection_v4.3.0",
    runnable_stage_resolver_version=(
        "runnable_stage_resolver_v4.4.0"
    ),
    planner_version="execution_planner_v4.5.0",
)


result = bridge_execution_plan_to_runtime(
    execution_plan=plan,
    stage_references={
        "stage_a": reference,
    },
    context=context,
)


check(
    "One-stage bridge result type exact",
    isinstance(
        result,
        CoordinationRuntimeBridgeResult,
    ),
)

check(
    "One-stage handoff count exact",
    result.handoff_count
    == 1,
)

check(
    "One-stage planned stage exact",
    result.planned_stage_ids
    == (
        "stage_a",
    ),
)

check(
    "Intent type exact",
    isinstance(
        result.intents[
            0
        ],
        RuntimeHandoffIntent,
    ),
)


intent = result.intents[
    0
]


check(
    "Intent workflow identity preserved",
    intent.workflow_id
    == "wf_smoke_5_1",
)

check(
    "Intent workspace identity preserved",
    intent.workspace_id
    == "ws_smoke",
)

check(
    "Intent correlation identity preserved",
    intent.correlation_id
    == "corr_smoke",
)

check(
    "Intent stage identity preserved",
    intent.stage_id
    == "stage_a",
)

check(
    "Intent job type preserved",
    intent.job_type
    == "smoke.stage_a",
)

check(
    "Intent runtime stage preserved",
    intent.runtime_stage
    == "stage_a",
)

check(
    "Intent required payload fields preserved",
    intent.required_payload_fields
    == (
        "document_id",
    ),
)

check(
    "Intent wave index preserved",
    intent.wave_index
    == 0,
)

check(
    "Intent execution semantics preserved",
    intent.execution_semantics
    == "parallel_eligible",
)

check(
    "Intent payload preserved",
    intent.payload[
        "document_id"
    ]
    == "doc_1",
)

check(
    "Intent payload immutable",
    isinstance(
        intent.payload,
        MappingProxyType,
    ),
)

blocked = False

try:
    intent.job_type = "mutated"

except Exception:
    blocked = True

check(
    "Runtime handoff intent immutable",
    blocked,
)


# -------------------------------------------------------------------------
# Snapshot
# -------------------------------------------------------------------------

snapshot = coordination_runtime_bridge_snapshot(
    result
)

check(
    "Bridge snapshot immutable mapping",
    isinstance(
        snapshot,
        MappingProxyType,
    ),
)

check(
    "Snapshot handoff count exact",
    snapshot[
        "handoff_count"
    ]
    == 1,
)

check(
    "Snapshot nested intents tuple",
    isinstance(
        snapshot[
            "intents"
        ],
        tuple,
    ),
)


# -------------------------------------------------------------------------
# Architecture boundaries
# -------------------------------------------------------------------------

architecture = (
    explain_coordination_runtime_bridge_v5_1()
)

check(
    "Architecture mapping immutable",
    isinstance(
        architecture,
        MappingProxyType,
    ),
)

check(
    "Architecture phase exact",
    architecture[
        "phase"
    ]
    == "5.1",
)

check(
    "Architecture upstream Phase 4.5 exact",
    architecture[
        "upstream_authority"
    ]
    == "Phase 4.5 ExecutionPlan",
)

check(
    "Architecture downstream Phase 5.2 exact",
    architecture[
        "downstream_authority"
    ]
    == "Phase 5.2 Runtime Job Mapping",
)


properties = architecture[
    "execution_properties"
]

for name in (
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
        f"Execution authority disabled: {name}",
        properties[
            name
        ] is False,
    )


check(
    "Bridge read-only",
    properties[
        "read_only"
    ] is True,
)

check(
    "Bridge deterministic",
    properties[
        "deterministic"
    ] is True,
)

check(
    "Bridge fail-closed",
    properties[
        "fail_closed"
    ] is True,
)


# -------------------------------------------------------------------------
# Static Runtime-boundary check
# -------------------------------------------------------------------------

runtime_imports = []

if tree is not None:

    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.ImportFrom,
        ):

            module = node.module or ""

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
    "Phase 5.1 imports no Runtime production module",
    runtime_imports
    == [],
    repr(
        runtime_imports
    ),
)


# -------------------------------------------------------------------------
# Unicode/source integrity
# -------------------------------------------------------------------------

check(
    "Source contains canonical component phrase",
    (
        "Coordination → Runtime Bridge"
        in source
        or "Coordination -> Runtime Bridge"
        in source
    ),
)

check(
    "Source contains no replacement character",
    "\ufffd"
    not in source,
)


# -------------------------------------------------------------------------
# Candidate SHA
# -------------------------------------------------------------------------

candidate_sha = sha256(
    BRIDGE
)

check(
    "Candidate SHA256 structurally valid",
    len(
        candidate_sha
    )
    == 64,
    candidate_sha,
)


# -------------------------------------------------------------------------
# Report
# -------------------------------------------------------------------------

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
    "PHASE 5.1 — COORDINATION → RUNTIME BRIDGE INSTALLATION SMOKE",
    "=" * 112,
    "",
]

for name, ok, detail in checks:

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
        "=" * 112,
        "INSTALLATION SMOKE RESULT",
        "=" * 112,
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        (
            "STATUS: SMOKE PASSED"
            if failed == 0
            else "STATUS: SMOKE FAILED"
        ),
        f"PHASE 5.1 CANDIDATE SHA256: {candidate_sha}",
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
print("=" * 112)
print("PHASE 5.1 INSTALLATION SMOKE RESULT")
print("=" * 112)
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
        "SMOKE PASSED"
        if failed == 0
        else "SMOKE FAILED"
    ),
)
print(
    "PHASE 5.1 CANDIDATE SHA256:",
    candidate_sha,
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 112)

raise SystemExit(
    0
    if failed == 0
    else 1
)
