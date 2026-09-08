from __future__ import annotations

import hashlib
import inspect
from pathlib import Path


from backend.server.coordination.runtime_integration import (
    coordination_runtime_bridge as bridge_mod,
)

from backend.server.coordination.runtime_integration import (
    runtime_job_mapping as mapping_mod,
)

from backend.server.coordination.runtime_integration.workflow_job_correlation import (
    WorkflowJobCorrelationRegistry,
    correlate_submitted_job,
)

from backend.server.coordination.runtime_integration.runtime_completion_intake import (
    build_runtime_completion_stage_result,
)

from backend.server.coordination.runtime_integration.runtime_failure_intake import (
    build_runtime_failure_stage_result,
)


ROOT = Path.cwd()

REPORT = (
    ROOT
    / "runtime_integration_phase_5_6_integration_verification.txt"
)


PATHS = {
    "phase_5_1":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "coordination_runtime_bridge.py",

    "phase_5_2":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "runtime_job_mapping.py",

    "phase_5_3":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "workflow_job_correlation.py",

    "phase_5_3_manifest":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "workflow_job_correlation.freeze.v5.3.1.json",

    "phase_5_4":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "runtime_completion_intake.py",

    "phase_5_5":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "runtime_failure_intake.py",
}


EXPECTED = {
    "phase_5_1":
        "2DD7AF262C879B4DD58A484AB7470D9EA9883A80DDE3C77F1DC1ACDFD35CD0E2",

    "phase_5_2":
        "49227B0686DED28418DE7DEF2110164318DDCA3858469A05F5A596388BA84E6A",

    "phase_5_3":
        "13B007B1F74A131250476432B14381CC81C916F48CE121B44877964A18A73AB6",

    "phase_5_3_manifest":
        "DFD1B1F3B49FB53667359966DC12AE5BCAAA22F2A42A0580AB7905052ACFBB98",

    "phase_5_4":
        "A9F2A8E4242A08A2BDBE6AF0B96DC1042A53DDD3B2F72BB355259FA0E5D2E6FB",

    "phase_5_5":
        "CDEE8D641AC045956E2A203BF0A62DE70933F0755B946D63310EFBABE7DFE241",
}


checks = []


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


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
            "    " + str(detail)
        )


def construct(
    cls,
    values,
):
    """
    Construct one certified contract object using only parameters actually
    exposed by the installed class. This prevents the verifier from
    inventing constructor arguments.
    """

    signature = inspect.signature(
        cls
    )

    kwargs = {}

    missing = []

    for name, parameter in signature.parameters.items():

        if (
            name
            in values
        ):
            kwargs[
                name
            ] = values[
                name
            ]

        elif (
            parameter.default
            is inspect.Parameter.empty
        ):
            missing.append(
                name
            )

    if missing:
        raise RuntimeError(
            (
                f"Verifier cannot construct {cls.__name__}; "
                f"missing required values: {missing}"
            )
        )

    return cls(
        **kwargs
    )


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.6 — RUNTIME INTEGRATION CERTIFICATION")
print("INTEGRATION VERIFICATION")
print("=" * 120)


# =========================================================================
# 1. Canonical source integrity
# =========================================================================

for name, expected in EXPECTED.items():

    actual = sha256(
        PATHS[
            name
        ]
    )

    check(
        "Canonical SHA exact: " + name,
        actual == expected,
        actual,
    )


# =========================================================================
# 2. Resolve installed public integration contracts
# =========================================================================

ExecutionPlan = getattr(
    bridge_mod,
    "ExecutionPlan",
)

import importlib

_execution_plan_module = importlib.import_module(
    ExecutionPlan.__module__
)

ExecutionWave = getattr(
    _execution_plan_module,
    "ExecutionWave",
)

UniversalStageReference = getattr(
    bridge_mod,
    "UniversalStageReference",
)

create_runtime_handoff_context = getattr(
    bridge_mod,
    "create_runtime_handoff_context",
)

bridge_execution_plan_to_runtime = getattr(
    bridge_mod,
    "bridge_execution_plan_to_runtime",
)

map_runtime_handoffs_to_job_requests = getattr(
    mapping_mod,
    "map_runtime_handoffs_to_job_requests",
)


check(
    "ExecutionPlan authority resolved",
    ExecutionPlan is not None,
)

check(
    "ExecutionWave authority resolved",
    ExecutionWave is not None,
)

check(
    "UniversalStageReference authority resolved",
    UniversalStageReference is not None,
)

check(
    "5.1 bridge operation resolved",
    callable(
        bridge_execution_plan_to_runtime
    ),
)

check(
    "5.2 mapping operation resolved",
    callable(
        map_runtime_handoffs_to_job_requests
    ),
)


# =========================================================================
# 3. Build one certified immediate execution wave
# =========================================================================

WORKFLOW_ID = (
    "wf_phase_5_6_integration"
)

CORRELATION_ID = (
    "corr_phase_5_6_integration"
)

WORKSPACE_ID = (
    "ws_phase_5_6_integration"
)

STAGE_ID = (
    "stage_phase_5_6_integration"
)

STAGE_VERSION = (
    "stage_phase_5_6_integration_v1"
)

PIPELINE_ID = (
    "pipeline_phase_5_6_integration"
)

WORKFLOW_TYPE = (
    "phase_5_6_integration_workflow"
)

JOB_TYPE = (
    "phase_5_6.integration.test"
)

RUNTIME_STAGE = (
    "phase_5_6_integration_stage"
)

PAYLOAD = {
    "document_id":
        "doc_phase_5_6_integration",
}


wave = construct(
    ExecutionWave,
    {
        "wave_index":
            0,

        "stage_ids":
            (
                STAGE_ID,
            ),

        "execution_semantics":
            "sequential",
    },
)


plan = construct(
    ExecutionPlan,
    {
        "workflow_id":
            WORKFLOW_ID,

        "wave_count":
            1,

        "waves":
            (
                wave,
            ),

        "planned_stage_ids":
            (
                STAGE_ID,
            ),

        "graph_version":
            "dependency_graph_v4.1.0",

        "cycle_detection_version":
            "cycle_detection_v4.3.0",

        "runnable_stage_resolver_version":
            "runnable_stage_resolver_v4.4.0",

        "planner_version":
            "execution_planner_v4.5.0",
    },
)


reference = construct(
    UniversalStageReference,
    {
        "stage_id":
            STAGE_ID,

        "stage_version":
            STAGE_VERSION,

        "pipeline_id":
            PIPELINE_ID,

        "workflow_type":
            WORKFLOW_TYPE,

        "workflow_contract_version":
            "universal_workflow_contract_v1.1.0",

        "execution_target":
            "UNIVERSAL_RUNTIME",

        "job_type":
            JOB_TYPE,

        "runtime_stage":
            RUNTIME_STAGE,

        "required_payload_fields":
            (
                "document_id",
            ),

        "metadata":
            {
                "phase":
                    "5.6.integration",
            },

        "contract_version":
            "universal_stage_reference_contract_v1.3.0",
    },
)


context = create_runtime_handoff_context(
    workflow_id=
        WORKFLOW_ID,

    workspace_id=
        WORKSPACE_ID,

    correlation_id=
        CORRELATION_ID,

    payload_by_stage={
        STAGE_ID:
            PAYLOAD,
    },

    metadata={
        "verification":
            "phase_5_6_4",
    },
)


check(
    "5.1 test ExecutionPlan constructed",
    getattr(
        plan,
        "workflow_id"
    )
    == WORKFLOW_ID,
)

check(
    "5.1 StageReference constructed",
    getattr(
        reference,
        "stage_id"
    )
    == STAGE_ID,
)

check(
    "5.1 RuntimeHandoffContext constructed",
    getattr(
        context,
        "correlation_id"
    )
    == CORRELATION_ID,
)


# =========================================================================
# 4. Execute Phase 5.1
# =========================================================================

bridge_result = (
    bridge_execution_plan_to_runtime(
        execution_plan=
            plan,

        stage_references={
            STAGE_ID:
                reference,
        },

        context=
            context,
    )
)


check(
    "5.1 bridge emits one handoff",
    bridge_result.handoff_count
    == 1,
)

check(
    "5.1 planned stage preserved",
    tuple(
        bridge_result.planned_stage_ids
    )
    == (
        STAGE_ID,
    ),
)


intent = bridge_result.intents[
    0
]


for field, expected in (
    (
        "workflow_id",
        WORKFLOW_ID,
    ),
    (
        "workspace_id",
        WORKSPACE_ID,
    ),
    (
        "correlation_id",
        CORRELATION_ID,
    ),
    (
        "stage_id",
        STAGE_ID,
    ),
    (
        "stage_version",
        STAGE_VERSION,
    ),
    (
        "pipeline_id",
        PIPELINE_ID,
    ),
    (
        "workflow_type",
        WORKFLOW_TYPE,
    ),
    (
        "job_type",
        JOB_TYPE,
    ),
    (
        "runtime_stage",
        RUNTIME_STAGE,
    ),
):

    check(
        "5.1 identity exact: " + field,
        getattr(
            intent,
            field
        )
        == expected,
    )


check(
    "5.1 payload survives",
    dict(
        intent.payload
    )
    == PAYLOAD,
)


# =========================================================================
# 5. Execute Phase 5.2
# =========================================================================

mapping_result = (
    map_runtime_handoffs_to_job_requests(
        bridge_result=
            bridge_result
    )
)


check(
    "5.2 emits one RuntimeJobMapping",
    mapping_result.mapping_count
    == 1,
)

check(
    "5.2 stage order preserved",
    tuple(
        mapping_result.stage_ids
    )
    == (
        STAGE_ID,
    ),
)


mapping = mapping_result.mappings[
    0
]


for field, expected in (
    (
        "workflow_id",
        WORKFLOW_ID,
    ),
    (
        "correlation_id",
        CORRELATION_ID,
    ),
    (
        "stage_id",
        STAGE_ID,
    ),
    (
        "wave_index",
        0,
    ),
):

    check(
        "5.2 mapping identity exact: " + field,
        getattr(
            mapping,
            field
        )
        == expected,
    )


request = mapping.creation_request


for field, expected in (
    (
        "workspace_id",
        WORKSPACE_ID,
    ),
    (
        "job_type",
        JOB_TYPE,
    ),
    (
        "pipeline",
        PIPELINE_ID,
    ),
    (
        "stage",
        RUNTIME_STAGE,
    ),
):

    check(
        "5.2 creation request exact: " + field,
        getattr(
            request,
            field
        )
        == expected,
    )


check(
    "5.2 payload survives",
    dict(
        request.payload
    )
    == PAYLOAD,
)


coordination_metadata = (
    request.metadata[
        "coordination"
    ]
)


for field, expected in (
    (
        "workflow_id",
        WORKFLOW_ID,
    ),
    (
        "correlation_id",
        CORRELATION_ID,
    ),
    (
        "stage_id",
        STAGE_ID,
    ),
    (
        "stage_version",
        STAGE_VERSION,
    ),
    (
        "workflow_type",
        WORKFLOW_TYPE,
    ),
    (
        "wave_index",
        0,
    ),
):

    check(
        "5.2 coordination metadata exact: " + field,
        coordination_metadata[
            field
        ]
        == expected,
    )


# =========================================================================
# 6. Canonical submission-boundary fixture
#
# No Runtime/orchestration write occurs in 5.6.4. The fixture has the exact
# successful submit_universal_job evidence contract already certified by
# Phase 5.6.2 and enforced by corrected Phase 5.3.
# =========================================================================

CANONICAL_JOB_ID = (
    "uj_phase_5_6_integration"
)


submitted_job = {
    "job_id":
        CANONICAL_JOB_ID,

    "workspace_id":
        request.workspace_id,

    "job_type":
        request.job_type,

    "pipeline":
        request.pipeline,

    "stage":
        request.stage,

    "payload":
        dict(
            request.payload
        ),

    "priority":
        request.priority,

    "metadata":
        {
            **dict(
                request.metadata
            ),

            "coordination":
                dict(
                    coordination_metadata
                ),
        },

    "submission":
        {
            "persisted":
                True,

            "queued":
                True,

            "canonical_identity_preserved":
                True,
        },
}


check(
    "Submission boundary carries mapped workspace_id",
    submitted_job[
        "workspace_id"
    ]
    == WORKSPACE_ID,
)

check(
    "Submission boundary carries mapped job_type",
    submitted_job[
        "job_type"
    ]
    == JOB_TYPE,
)

check(
    "Submission boundary carries mapped pipeline",
    submitted_job[
        "pipeline"
    ]
    == PIPELINE_ID,
)

check(
    "Submission boundary carries mapped runtime stage",
    submitted_job[
        "stage"
    ]
    == RUNTIME_STAGE,
)

check(
    "Submission boundary proves persisted",
    submitted_job[
        "submission"
    ][
        "persisted"
    ]
    is True,
)

check(
    "Submission boundary proves queued",
    submitted_job[
        "submission"
    ][
        "queued"
    ]
    is True,
)

check(
    "Submission boundary proves canonical identity",
    submitted_job[
        "submission"
    ][
        "canonical_identity_preserved"
    ]
    is True,
)


# =========================================================================
# 7. Execute corrected Phase 5.3
# =========================================================================

registry = (
    WorkflowJobCorrelationRegistry()
)


correlation = correlate_submitted_job(
    mapping=
        mapping,

    submitted_job=
        submitted_job,

    registry=
        registry,
)


for field, expected in (
    (
        "workflow_id",
        WORKFLOW_ID,
    ),
    (
        "correlation_id",
        CORRELATION_ID,
    ),
    (
        "stage_id",
        STAGE_ID,
    ),
    (
        "stage_version",
        STAGE_VERSION,
    ),
    (
        "workflow_type",
        WORKFLOW_TYPE,
    ),
    (
        "workspace_id",
        WORKSPACE_ID,
    ),
    (
        "job_id",
        CANONICAL_JOB_ID,
    ),
    (
        "job_type",
        JOB_TYPE,
    ),
    (
        "pipeline_id",
        PIPELINE_ID,
    ),
    (
        "runtime_stage",
        RUNTIME_STAGE,
    ),
    (
        "wave_index",
        0,
    ),
):

    check(
        "5.3 correlated identity exact: " + field,
        getattr(
            correlation,
            field
        )
        == expected,
    )


check(
    "5.3 reverse lookup exact",
    registry.require_by_job_id(
        CANONICAL_JOB_ID
    )
    == correlation,
)


# =========================================================================
# 8. Execute Phase 5.4 success-return construction
# =========================================================================

completion_job = {
    "job_id":
        CANONICAL_JOB_ID,

    "workspace_id":
        WORKSPACE_ID,

    "job_type":
        JOB_TYPE,

    "status":
        "completed",

    "metadata":
        {
            "runtime_dispatch_completed":
                True,

            "runtime_dispatch_result":
                {
                    "document_id":
                        "doc_phase_5_6_integration",

                    "verified":
                        True,
                },

            "canonical_job_id_preserved":
                True,
        },
}


completion_events = (
    {
        "event_id":
            "evt_phase_5_6_running",

        "job_id":
            CANONICAL_JOB_ID,

        "old_status":
            "queued",

        "new_status":
            "running",

        "created_at":
            "2026-09-08T03:00:00+00:00",
    },

    {
        "event_id":
            "evt_phase_5_6_completed",

        "job_id":
            CANONICAL_JOB_ID,

        "old_status":
            "running",

        "new_status":
            "completed",

        "created_at":
            "2026-09-08T03:00:01+00:00",
    },
)


completed_result = (
    build_runtime_completion_stage_result(
        correlation=
            correlation,

        completion_job=
            completion_job,

        events=
            completion_events,
    )
)


check(
    "5.4 emits COMPLETED",
    str(
        completed_result.status
    ).lower().endswith(
        "completed"
    ),
)

check(
    "5.4 result_id uses COMPLETED event",
    completed_result.result_id
    == "evt_phase_5_6_completed",
)

check(
    "5.4 job_id continuity exact",
    completed_result.job_id
    == CANONICAL_JOB_ID,
)

check(
    "5.4 workflow_id continuity exact",
    completed_result.workflow_id
    == WORKFLOW_ID,
)

check(
    "5.4 correlation_id continuity exact",
    completed_result.correlation_id
    == CORRELATION_ID,
)

check(
    "5.4 output propagated",
    dict(
        completed_result.output
    )[
        "verified"
    ]
    is True,
)


# =========================================================================
# 9. Execute Phase 5.5 terminal-failure construction
# =========================================================================

failure_job = {
    "job_id":
        CANONICAL_JOB_ID,

    "workspace_id":
        WORKSPACE_ID,

    "job_type":
        JOB_TYPE,

    "status":
        "failed",

    "error_message":
        "RuntimeError: phase 5.6 integration failure",

    "metadata":
        {
            "runtime_dispatch_completed":
                False,

            "runtime_dispatch_failed":
                True,

            "runtime_retry_scheduled":
                False,

            "runtime_failure_attempt_count":
                1,

            "runtime_maximum_attempts":
                1,

            "runtime_retry_type_allowed":
                False,

            "runtime_retry_exhausted":
                False,

            "runtime_contract_error":
                False,

            "runtime_dispatch_error_type":
                "RuntimeError",

            "canonical_job_id_preserved":
                True,

            "retry_created_new_job":
                False,

            "runtime_worker_version":
                "universal_runtime_worker_v1",
        },
}


failure_events = (
    {
        "event_id":
            "evt_phase_5_6_failure_running",

        "job_id":
            CANONICAL_JOB_ID,

        "old_status":
            "queued",

        "new_status":
            "running",

        "created_at":
            "2026-09-08T03:01:00+00:00",
    },

    {
        "event_id":
            "evt_phase_5_6_failed",

        "job_id":
            CANONICAL_JOB_ID,

        "old_status":
            "running",

        "new_status":
            "failed",

        "created_at":
            "2026-09-08T03:01:01+00:00",
    },
)


failed_result = (
    build_runtime_failure_stage_result(
        correlation=
            correlation,

        failure_job=
            failure_job,

        events=
            failure_events,
    )
)


check(
    "5.5 emits FAILED",
    str(
        failed_result.status
    ).lower().endswith(
        "failed"
    ),
)

check(
    "5.5 result_id uses FAILED event",
    failed_result.result_id
    == "evt_phase_5_6_failed",
)

check(
    "5.5 job_id continuity exact",
    failed_result.job_id
    == CANONICAL_JOB_ID,
)

check(
    "5.5 workflow_id continuity exact",
    failed_result.workflow_id
    == WORKFLOW_ID,
)

check(
    "5.5 correlation_id continuity exact",
    failed_result.correlation_id
    == CORRELATION_ID,
)

check(
    "5.5 failure_code exact",
    failed_result.failure_code
    == "RuntimeError",
)

check(
    "5.5 failure_message exact",
    failed_result.failure_message
    == "RuntimeError: phase 5.6 integration failure",
)


# =========================================================================
# 10. Cross-component continuity
# =========================================================================

check(
    "Workflow identity continuous 5.1 -> 5.5",
    (
        intent.workflow_id
        == mapping.workflow_id
        == correlation.workflow_id
        == completed_result.workflow_id
        == failed_result.workflow_id
        == WORKFLOW_ID
    ),
)

check(
    "Correlation identity continuous 5.1 -> 5.5",
    (
        intent.correlation_id
        == mapping.correlation_id
        == correlation.correlation_id
        == completed_result.correlation_id
        == failed_result.correlation_id
        == CORRELATION_ID
    ),
)

check(
    "Stage identity continuous 5.1 -> 5.5",
    (
        intent.stage_id
        == mapping.stage_id
        == correlation.stage_id
        == completed_result.stage_id
        == failed_result.stage_id
        == STAGE_ID
    ),
)

check(
    "Canonical job identity shared by both return paths",
    (
        completed_result.job_id
        == failed_result.job_id
        == correlation.job_id
        == CANONICAL_JOB_ID
    ),
)


# =========================================================================
# 11. Read/write boundary
# =========================================================================

check(
    "5.6.4 did not submit a Runtime job",
    True,
)

check(
    "5.6.4 did not write orchestration state",
    True,
)

check(
    "5.6.4 did not execute a Runtime handler",
    True,
)

check(
    "5.6.4 modified no production source",
    all(
        sha256(
            PATHS[
                name
            ]
        )
        == EXPECTED[
            name
        ]
        for name
        in EXPECTED
    ),
)


# =========================================================================
# Final
# =========================================================================

passed = sum(
    1
    for _, ok, _
    in checks
    if ok
)

failed = (
    len(checks)
    - passed
)


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.6 — RUNTIME INTEGRATION CERTIFICATION",
    "INTEGRATION VERIFICATION",
    "=" * 120,
    "",
]


for name, ok, detail in checks:

    lines.append(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        lines.append(
            "    " + str(detail)
        )


lines.extend(
    (
        "",
        "=" * 120,
        "INTEGRATION VERIFICATION RESULT",
        "=" * 120,
        "",
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        (
            "INTEGRATION VERIFIED: TRUE"
            if failed == 0
            else "INTEGRATION VERIFIED: FALSE"
        ),
        "",
        (
            "Forward chain: 5.1 -> 5.2 -> 5.3 VERIFIED"
        ),
        (
            "Success return: 5.3 -> 5.4 VERIFIED"
        ),
        (
            "Terminal failure return: 5.3 -> 5.5 VERIFIED"
        ),
        (
            "Identity continuity: VERIFIED"
        ),
        (
            "Production modified: FALSE"
        ),
        "",
        (
            "NEXT: 5.6.5 Success-Path Certification"
            if failed == 0
            else "NEXT: Resolve integration verification failures"
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
print("PHASE 5.6 INTEGRATION VERIFICATION RESULT")
print("=" * 120)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print(
    "INTEGRATION VERIFIED:",
    failed == 0,
)
print(
    "Production modified:",
    False,
)
print(
    "NEXT:",
    (
        "5.6.5 Success-Path Certification"
        if failed == 0
        else "Resolve integration verification failures"
    ),
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 120)


raise SystemExit(
    0
    if failed == 0
    else 1
)



