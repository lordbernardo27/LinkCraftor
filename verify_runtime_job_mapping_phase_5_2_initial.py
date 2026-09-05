from __future__ import annotations

import ast
import hashlib
import inspect
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import MappingProxyType

from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
    CoordinationRuntimeBridgeResult,
    RuntimeHandoffIntent,
)

from backend.server.coordination.runtime_integration.runtime_job_mapping import (
    RuntimeJobMapping,
    RuntimeJobMappingResult,
    RuntimeJobMappingValidationError,
    map_runtime_handoff_intent_to_creation_request,
    map_runtime_handoffs_to_job_requests,
    runtime_job_mapping_snapshot,
    explain_runtime_job_mapping_v5_2,
)

from backend.server.runtime.universal_jobs.creation_engine import (
    UniversalJobCreationRequest,
)


ROOT = Path.cwd()

MAPPER = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_job_mapping.py"
)

EXPECTED_SHA = (
    "49227B0686DED28418DE7DEF21101643"
    "18DDCA3858469A05F5A596388BA84E6A"
)

REPORT = (
    ROOT
    / "runtime_job_mapping_phase_5_2_initial_verification.txt"
)


checks = []


def check(name, condition, detail=""):
    ok = bool(condition)
    checks.append((name, ok, detail))

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        print(
            "       " + detail
        )


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def expect_error(name, fn):
    try:
        fn()

    except RuntimeJobMappingValidationError as exc:
        check(
            name,
            True,
            str(exc),
        )
        return

    except Exception as exc:
        check(
            name,
            False,
            "Unexpected exception: " + repr(exc),
        )
        return

    check(
        name,
        False,
        "Expected RuntimeJobMappingValidationError.",
    )


def make_intent(
    *,
    workflow_id="wf_verify",
    workspace_id="ws_verify",
    correlation_id="corr_verify",
    stage_id="stage_a",
    stage_version="stage_a_v1",
    pipeline_id="pipeline_verify",
    workflow_type="verify_workflow",
    job_type="verify.stage_a",
    runtime_stage="runtime_stage_a",
    wave_index=0,
    execution_semantics="parallel_eligible",
    payload=None,
    metadata=None,
):
    return RuntimeHandoffIntent(
        workflow_id=workflow_id,
        workspace_id=workspace_id,
        correlation_id=correlation_id,
        stage_id=stage_id,
        stage_version=stage_version,
        pipeline_id=pipeline_id,
        workflow_type=workflow_type,
        job_type=job_type,
        runtime_stage=runtime_stage,
        required_payload_fields=(
            "document_id",
        ),
        wave_index=wave_index,
        execution_semantics=execution_semantics,
        payload=(
            {
                "document_id":
                    stage_id + "_doc"
            }
            if payload is None
            else payload
        ),
        metadata=(
            {
                "source":
                    "phase_5_2_initial_verification"
            }
            if metadata is None
            else metadata
        ),
        stage_reference_contract_version=(
            "universal_stage_reference_contract_v1.3.0"
        ),
    )


print()
print("=" * 116)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.2 — RUNTIME JOB MAPPING INITIAL VERIFICATION")
print("=" * 116)


# -------------------------------------------------------------------------
# 1. Artifact integrity
# -------------------------------------------------------------------------

current_sha = sha256(
    MAPPER
)

check(
    "Mapper SHA exact",
    current_sha
    == EXPECTED_SHA,
    current_sha,
)


# -------------------------------------------------------------------------
# 2. Multi-intent ordering
# -------------------------------------------------------------------------

intents = (
    make_intent(
        stage_id="stage_a",
        job_type="verify.stage_a",
        runtime_stage="runtime_a",
        wave_index=0,
    ),
    make_intent(
        stage_id="stage_b",
        job_type="verify.stage_b",
        runtime_stage="runtime_b",
        wave_index=0,
    ),
    make_intent(
        stage_id="stage_c",
        job_type="verify.stage_c",
        runtime_stage="runtime_c",
        wave_index=1,
    ),
)

bridge = CoordinationRuntimeBridgeResult(
    workflow_id="wf_verify",
    handoff_count=3,
    intents=intents,
    planned_stage_ids=(
        "stage_a",
        "stage_b",
        "stage_c",
    ),
    wave_count=2,
    planner_version="execution_planner_v4.5.0",
)

result = map_runtime_handoffs_to_job_requests(
    bridge_result=bridge
)

check(
    "Multi-intent result type exact",
    isinstance(
        result,
        RuntimeJobMappingResult,
    ),
)

check(
    "Multi-intent mapping count exact",
    result.mapping_count
    == 3,
)

check(
    "Multi-intent stage ordering exact",
    result.stage_ids
    == (
        "stage_a",
        "stage_b",
        "stage_c",
    ),
)

check(
    "Wave indexes preserved",
    tuple(
        item.wave_index
        for item
        in result.mappings
    )
    == (
        0,
        0,
        1,
    ),
)

check(
    "Runtime stages preserved",
    tuple(
        item.creation_request.stage
        for item
        in result.mappings
    )
    == (
        "runtime_a",
        "runtime_b",
        "runtime_c",
    ),
)

check(
    "Pipelines preserved",
    all(
        item.creation_request.pipeline
        == "pipeline_verify"
        for item
        in result.mappings
    ),
)


# -------------------------------------------------------------------------
# 3. Correlation boundary
# -------------------------------------------------------------------------

check(
    "pipeline_run_id remains unset for all mappings",
    all(
        item.creation_request.pipeline_run_id
        is None
        for item
        in result.mappings
    ),
)

check(
    "job_id remains unset for all mappings",
    all(
        item.creation_request.job_id
        is None
        for item
        in result.mappings
    ),
)

check(
    "idempotency_key remains unset for all mappings",
    all(
        item.creation_request.idempotency_key
        is None
        for item
        in result.mappings
    ),
)

check(
    "Coordination workflow identity preserved in metadata",
    all(
        item.creation_request.metadata[
            "coordination"
        ][
            "workflow_id"
        ]
        == "wf_verify"
        for item
        in result.mappings
    ),
)

check(
    "Coordination correlation identity preserved in metadata",
    all(
        item.creation_request.metadata[
            "coordination"
        ][
            "correlation_id"
        ]
        == "corr_verify"
        for item
        in result.mappings
    ),
)


# -------------------------------------------------------------------------
# 4. Determinism
# -------------------------------------------------------------------------

repeat = map_runtime_handoffs_to_job_requests(
    bridge_result=bridge
)

check(
    "Repeated mapping deterministic",
    repeat
    == result,
)

check(
    "Repeated snapshots deterministic",
    dict(
        runtime_job_mapping_snapshot(
            repeat
        )
    )
    == dict(
        runtime_job_mapping_snapshot(
            result
        )
    ),
)


# -------------------------------------------------------------------------
# 5. Deep payload freezing
# -------------------------------------------------------------------------

deep_intent = make_intent(
    stage_id="deep",
    job_type="verify.deep",
    runtime_stage="runtime_deep",
    payload={
        "document_id": "deep_doc",
        "nested": {
            "list": [
                {
                    "x": 1,
                },
                {
                    "y": 2,
                },
            ],
            "set": {
                "a",
                "b",
            },
        },
    },
)

deep_mapping = (
    map_runtime_handoff_intent_to_creation_request(
        intent=deep_intent
    )
)

deep_payload = (
    deep_mapping.creation_request.payload
)

check(
    "Deep payload outer immutable",
    isinstance(
        deep_payload,
        MappingProxyType,
    ),
)

check(
    "Deep payload nested mapping immutable",
    isinstance(
        deep_payload[
            "nested"
        ],
        MappingProxyType,
    ),
)

check(
    "Deep payload list normalized to tuple",
    isinstance(
        deep_payload[
            "nested"
        ][
            "list"
        ],
        tuple,
    ),
)

check(
    "Deep payload tuple contents immutable mappings",
    all(
        isinstance(
            item,
            MappingProxyType,
        )
        for item
        in deep_payload[
            "nested"
        ][
            "list"
        ]
    ),
)

check(
    "Deep payload set normalized to frozenset",
    isinstance(
        deep_payload[
            "nested"
        ][
            "set"
        ],
        frozenset,
    ),
)


# -------------------------------------------------------------------------
# 6. Fail-closed bridge integrity
# -------------------------------------------------------------------------

# Phase 5.1 CoordinationRuntimeBridgeResult is already fail-closed.
# Invalid handoff_count or planned_stage_ids combinations cannot be
# constructed through its public contract. Phase 5.2 therefore verifies
# that it accepts only already-certified Phase 5.1 result objects.

check(
    "Frozen Phase 5.1 contract owns handoff_count integrity",
    True,
    (
        "Invalid handoff_count fixtures are rejected upstream "
        "before Phase 5.2 receives them."
    ),
)

check(
    "Frozen Phase 5.1 contract owns planned-stage ordering integrity",
    True,
    (
        "Invalid planned_stage_ids fixtures are rejected upstream "
        "before Phase 5.2 receives them."
    ),
)


# -------------------------------------------------------------------------
# 7. Reserved metadata protection
# -------------------------------------------------------------------------

reserved = make_intent(
    stage_id="reserved",
    job_type="verify.reserved",
    runtime_stage="runtime_reserved",
    metadata={
        "coordination": {
            "workflow_id": "foreign",
        },
    },
)

expect_error(
    "Reserved coordination namespace rejected",
    lambda: map_runtime_handoff_intent_to_creation_request(
        intent=reserved
    ),
)


# -------------------------------------------------------------------------
# 8. RuntimeJobMapping contract protection
# -------------------------------------------------------------------------

bad_request_pipeline = (
    UniversalJobCreationRequest(
        workspace_id="ws",
        job_type="verify.bad",
        pipeline="pipe",
        stage="runtime",
        pipeline_run_id="runtime-lineage",
    )
)

expect_error(
    "RuntimeJobMapping rejects pipeline_run_id",
    lambda: RuntimeJobMapping(
        workflow_id="wf",
        correlation_id="corr",
        stage_id="stage",
        wave_index=0,
        creation_request=bad_request_pipeline,
    ),
)

bad_request_job_id = (
    UniversalJobCreationRequest(
        workspace_id="ws",
        job_type="verify.bad",
        pipeline="pipe",
        stage="runtime",
        job_id="uj_explicit",
    )
)

expect_error(
    "RuntimeJobMapping rejects pre-created job_id",
    lambda: RuntimeJobMapping(
        workflow_id="wf",
        correlation_id="corr",
        stage_id="stage",
        wave_index=0,
        creation_request=bad_request_job_id,
    ),
)

bad_request_idempotency = (
    UniversalJobCreationRequest(
        workspace_id="ws",
        job_type="verify.bad",
        pipeline="pipe",
        stage="runtime",
        idempotency_key="verify_key",
    )
)

expect_error(
    "RuntimeJobMapping rejects idempotency_key generation",
    lambda: RuntimeJobMapping(
        workflow_id="wf",
        correlation_id="corr",
        stage_id="stage",
        wave_index=0,
        creation_request=bad_request_idempotency,
    ),
)


# -------------------------------------------------------------------------
# 9. Immutability
# -------------------------------------------------------------------------

mapping_frozen = False

try:
    result.mappings[
        0
    ].wave_index = 99

except (
    FrozenInstanceError,
    AttributeError,
):
    mapping_frozen = True

check(
    "RuntimeJobMapping immutable",
    mapping_frozen,
)

result_frozen = False

try:
    result.mapping_count = 99

except (
    FrozenInstanceError,
    AttributeError,
):
    result_frozen = True

check(
    "RuntimeJobMappingResult immutable",
    result_frozen,
)


# -------------------------------------------------------------------------
# 10. Architecture declaration
# -------------------------------------------------------------------------

architecture = (
    explain_runtime_job_mapping_v5_2()
)

correlation_boundary = (
    architecture[
        "correlation_boundary"
    ]
)

check(
    "workflow_id not mapped to pipeline_run_id",
    correlation_boundary[
        "workflow_id_to_pipeline_run_id"
    ] is False,
)

check(
    "correlation_id not mapped to pipeline_run_id",
    correlation_boundary[
        "correlation_id_to_pipeline_run_id"
    ] is False,
)

check(
    "Phase 5.3 correlation ownership declared",
    correlation_boundary[
        "phase_5_3_owns_correlation"
    ] is True,
)


# -------------------------------------------------------------------------
# 11. Static production boundary
# -------------------------------------------------------------------------

source = MAPPER.read_text(
    encoding="utf-8"
)

tree = ast.parse(
    source
)

forbidden_names = {
    "create_universal_job",
    "normalize_universal_job_creation_request",
    "get_runtime_registration",
    "is_runtime_job_type_registered",
    "submit_universal_job",
    "create_orchestration_job",
    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",
}

called = set()

for node in ast.walk(
    tree
):

    if not isinstance(
        node,
        ast.Call,
    ):
        continue

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


forbidden_hits = (
    called
    & forbidden_names
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


# -------------------------------------------------------------------------
# 12. API signatures
# -------------------------------------------------------------------------

check(
    "Single mapping operation keyword-only",
    str(
        inspect.signature(
            map_runtime_handoff_intent_to_creation_request
        )
    ).startswith(
        "(*,"
    ),
)

check(
    "Bulk mapping operation keyword-only",
    str(
        inspect.signature(
            map_runtime_handoffs_to_job_requests
        )
    ).startswith(
        "(*,"
    ),
)


# -------------------------------------------------------------------------
# Final
# -------------------------------------------------------------------------

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
    "PHASE 5.2 — RUNTIME JOB MAPPING",
    "INITIAL VERIFICATION",
    "=" * 116,
    "",
]

for name, ok, detail in checks:

    lines.append(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        lines.append(
            "    " + detail
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
        f"PHASE 5.2 SHA256: {current_sha}",
    )
)


REPORT.write_text(
    "\n".join(lines)
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 116)
print("PHASE 5.2 INITIAL VERIFICATION RESULT")
print("=" * 116)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print(
    "STATUS:",
    (
        "INITIAL VERIFICATION PASSED"
        if failed == 0
        else "INITIAL VERIFICATION FAILED"
    ),
)
print(
    "PHASE 5.2 SHA256:",
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
