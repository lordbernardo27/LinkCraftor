from __future__ import annotations

import ast
import hashlib
from dataclasses import FrozenInstanceError, fields
from pathlib import Path
from types import MappingProxyType

from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
    CoordinationRuntimeBridgeResult,
    RuntimeHandoffIntent,
)

import backend.server.coordination.runtime_integration.runtime_job_mapping as mapper

from backend.server.coordination.runtime_integration.runtime_job_mapping import (
    RUNTIME_JOB_MAPPING_VERSION,
    RUNTIME_JOB_MAPPING_SCHEMA_VERSION,
    RUNTIME_JOB_MAPPING_ENTRY_VERSION,
    RUNTIME_JOB_MAPPING_FIELD_COUNT,
    RUNTIME_JOB_MAPPING_RESULT_FIELD_COUNT,
    COORDINATION_METADATA_KEY,
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

FROZEN_5_1 = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "coordination_runtime_bridge.py"
)

EXPECTED_5_1_SHA = (
    "2DD7AF262C879B4DD58A484AB7470D9E"
    "A9883A80DDE3C77F1DC1ACDFD35CD0E2"
)

REPORT = (
    ROOT
    / "runtime_job_mapping_phase_5_2_installation_smoke.txt"
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


def expect_mapping_error(
    name,
    fn,
):
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
            "Unexpected exception: "
            + repr(exc),
        )
        return

    check(
        name,
        False,
        "Expected RuntimeJobMappingValidationError.",
    )


print()
print("=" * 116)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.2 — RUNTIME JOB MAPPING INSTALLATION SMOKE")
print("=" * 116)


# -------------------------------------------------------------------------
# 1. Artifact identity
# -------------------------------------------------------------------------

check(
    "Phase 5.2 mapper file exists",
    MAPPER.exists(),
)

source = MAPPER.read_text(
    encoding="utf-8"
)

try:
    ast.parse(source)
    syntax_ok = True
except SyntaxError:
    syntax_ok = False

check(
    "Phase 5.2 Python syntax parses",
    syntax_ok,
)

check(
    "Mapper version exact",
    RUNTIME_JOB_MAPPING_VERSION
    == "runtime_job_mapping_v5.2.0",
)

check(
    "Mapper schema exact",
    RUNTIME_JOB_MAPPING_SCHEMA_VERSION
    == "runtime_job_mapping_schema_v1",
)

check(
    "Mapping entry version exact",
    RUNTIME_JOB_MAPPING_ENTRY_VERSION
    == "runtime_job_mapping_entry_v5.2.0",
)

check(
    "Reserved metadata key exact",
    COORDINATION_METADATA_KEY
    == "coordination",
)


# -------------------------------------------------------------------------
# 2. Frozen upstream integrity
# -------------------------------------------------------------------------

frozen_sha = sha256(
    FROZEN_5_1
)

check(
    "Frozen Phase 5.1 SHA exact",
    frozen_sha
    == EXPECTED_5_1_SHA,
    frozen_sha,
)


# -------------------------------------------------------------------------
# 3. Dataclass shapes
# -------------------------------------------------------------------------

check(
    "RuntimeJobMapping field count exact",
    len(
        fields(
            RuntimeJobMapping
        )
    )
    == RUNTIME_JOB_MAPPING_FIELD_COUNT
    == 6,
)

check(
    "RuntimeJobMappingResult field count exact",
    len(
        fields(
            RuntimeJobMappingResult
        )
    )
    == RUNTIME_JOB_MAPPING_RESULT_FIELD_COUNT
    == 6,
)


# -------------------------------------------------------------------------
# 4. One-intent mapping
# -------------------------------------------------------------------------

intent = RuntimeHandoffIntent(
    workflow_id="wf_smoke",
    workspace_id="ws_smoke",
    correlation_id="corr_smoke",
    stage_id="stage_a",
    stage_version="stage_a_v1",
    pipeline_id="pipeline_a",
    workflow_type="smoke_workflow",
    job_type="smoke.stage_a",
    runtime_stage="runtime_stage_a",
    required_payload_fields=(
        "document_id",
    ),
    wave_index=0,
    execution_semantics="parallel_eligible",
    payload={
        "document_id": "doc_1",
        "nested": {
            "enabled": True,
        },
    },
    metadata={
        "source": "installation_smoke",
    },
    stage_reference_contract_version=(
        "universal_stage_reference_contract_v1.3.0"
    ),
)

mapping = (
    map_runtime_handoff_intent_to_creation_request(
        intent=intent
    )
)

request = mapping.creation_request

check(
    "One intent returns RuntimeJobMapping",
    isinstance(
        mapping,
        RuntimeJobMapping,
    ),
)

check(
    "Creation request type exact",
    isinstance(
        request,
        UniversalJobCreationRequest,
    ),
)

check(
    "workflow_id preserved",
    mapping.workflow_id
    == "wf_smoke",
)

check(
    "correlation_id preserved",
    mapping.correlation_id
    == "corr_smoke",
)

check(
    "coordination stage_id preserved",
    mapping.stage_id
    == "stage_a",
)

check(
    "wave_index preserved",
    mapping.wave_index
    == 0,
)

check(
    "workspace_id direct mapping",
    request.workspace_id
    == "ws_smoke",
)

check(
    "job_type direct mapping",
    request.job_type
    == "smoke.stage_a",
)

check(
    "pipeline_id maps to pipeline",
    request.pipeline
    == "pipeline_a",
)

check(
    "runtime_stage maps to stage",
    request.stage
    == "runtime_stage_a",
)

check(
    "enqueue intent remains True",
    request.enqueue
    is True,
)


# -------------------------------------------------------------------------
# 5. Runtime defaults retained
# -------------------------------------------------------------------------

check(
    "user_id Runtime default retained",
    request.user_id
    == "system",
)

check(
    "product_id Runtime default retained",
    request.product_id
    == "linkcraftor",
)

check(
    "payload_reference remains None",
    request.payload_reference
    is None,
)

check(
    "parent_job_id remains None",
    request.parent_job_id
    is None,
)

check(
    "dependency_job_ids remain empty",
    request.dependency_job_ids
    == (),
)

check(
    "batch_id remains None",
    request.batch_id
    is None,
)

check(
    "pipeline_run_id remains None",
    request.pipeline_run_id
    is None,
)

check(
    "idempotency_key remains None",
    request.idempotency_key
    is None,
)

check(
    "maximum_attempts remains None",
    request.maximum_attempts
    is None,
)

check(
    "job_id remains None",
    request.job_id
    is None,
)

check(
    "job_id_prefix canonical default retained",
    request.job_id_prefix
    == "uj",
)

check(
    "created_at remains None",
    request.created_at
    is None,
)


# -------------------------------------------------------------------------
# 6. Metadata preservation
# -------------------------------------------------------------------------

check(
    "Original intent metadata preserved",
    request.metadata[
        "source"
    ]
    == "installation_smoke",
)

coordination = request.metadata[
    "coordination"
]

check(
    "Coordination metadata immutable",
    isinstance(
        coordination,
        MappingProxyType,
    ),
)

check(
    "Metadata workflow_id exact",
    coordination[
        "workflow_id"
    ]
    == "wf_smoke",
)

check(
    "Metadata correlation_id exact",
    coordination[
        "correlation_id"
    ]
    == "corr_smoke",
)

check(
    "Metadata stage_id exact",
    coordination[
        "stage_id"
    ]
    == "stage_a",
)

check(
    "Metadata stage_version exact",
    coordination[
        "stage_version"
    ]
    == "stage_a_v1",
)

check(
    "Metadata workflow_type exact",
    coordination[
        "workflow_type"
    ]
    == "smoke_workflow",
)

check(
    "Metadata wave_index exact",
    coordination[
        "wave_index"
    ]
    == 0,
)

check(
    "Metadata execution semantics exact",
    coordination[
        "execution_semantics"
    ]
    == "parallel_eligible",
)

check(
    "Metadata required fields exact",
    coordination[
        "required_payload_fields"
    ]
    == (
        "document_id",
    ),
)


# -------------------------------------------------------------------------
# 7. Deep immutability
# -------------------------------------------------------------------------

check(
    "Request payload immutable",
    isinstance(
        request.payload,
        MappingProxyType,
    ),
)

check(
    "Nested request payload immutable",
    isinstance(
        request.payload[
            "nested"
        ],
        MappingProxyType,
    ),
)

mapping_frozen = False

try:
    mapping.stage_id = "mutated"
except (
    FrozenInstanceError,
    AttributeError,
):
    mapping_frozen = True

check(
    "RuntimeJobMapping frozen",
    mapping_frozen,
)

request_frozen = False

try:
    request.stage = "mutated"
except (
    FrozenInstanceError,
    AttributeError,
):
    request_frozen = True

check(
    "UniversalJobCreationRequest remains frozen",
    request_frozen,
)


# -------------------------------------------------------------------------
# 8. Complete bridge-result mapping
# -------------------------------------------------------------------------

bridge_result = CoordinationRuntimeBridgeResult(
    workflow_id="wf_smoke",
    handoff_count=1,
    intents=(
        intent,
    ),
    planned_stage_ids=(
        "stage_a",
    ),
    wave_count=1,
    planner_version="execution_planner_v4.5.0",
)

result = map_runtime_handoffs_to_job_requests(
    bridge_result=bridge_result
)

check(
    "Bridge result maps successfully",
    isinstance(
        result,
        RuntimeJobMappingResult,
    ),
)

check(
    "Mapping count exact",
    result.mapping_count
    == 1,
)

check(
    "Stage ordering preserved",
    result.stage_ids
    == (
        "stage_a",
    ),
)

check(
    "Mapped request identity preserved",
    result.mappings[
        0
    ].creation_request
    == request,
)


# -------------------------------------------------------------------------
# 9. Empty bridge behavior
# -------------------------------------------------------------------------

empty_bridge = CoordinationRuntimeBridgeResult(
    workflow_id="wf_empty",
    handoff_count=0,
    intents=(),
    planned_stage_ids=(),
    wave_count=0,
    planner_version="execution_planner_v4.5.0",
)

empty_result = map_runtime_handoffs_to_job_requests(
    bridge_result=empty_bridge
)

check(
    "Empty bridge maps successfully",
    empty_result.mapping_count
    == 0,
)

check(
    "Empty bridge mappings empty",
    empty_result.mappings
    == (),
)

check(
    "Empty bridge stage_ids empty",
    empty_result.stage_ids
    == (),
)


# -------------------------------------------------------------------------
# 10. Reserved metadata collision
# -------------------------------------------------------------------------

collision_intent = RuntimeHandoffIntent(
    workflow_id="wf_collision",
    workspace_id="ws_collision",
    correlation_id="corr_collision",
    stage_id="stage_collision",
    stage_version="stage_collision_v1",
    pipeline_id="pipeline_collision",
    workflow_type="collision_workflow",
    job_type="smoke.collision",
    runtime_stage="runtime_collision",
    required_payload_fields=(),
    wave_index=0,
    execution_semantics="parallel_eligible",
    payload={},
    metadata={
        "coordination": {
            "foreign": True,
        },
    },
    stage_reference_contract_version=(
        "universal_stage_reference_contract_v1.3.0"
    ),
)

expect_mapping_error(
    "Reserved coordination metadata collision fails closed",
    lambda: map_runtime_handoff_intent_to_creation_request(
        intent=collision_intent
    ),
)


# -------------------------------------------------------------------------
# 11. Snapshot
# -------------------------------------------------------------------------

snapshot = runtime_job_mapping_snapshot(
    result
)

check(
    "Snapshot immutable mapping",
    isinstance(
        snapshot,
        MappingProxyType,
    ),
)

check(
    "Snapshot mapping count exact",
    snapshot[
        "mapping_count"
    ]
    == 1,
)

check(
    "Snapshot mappings tuple",
    isinstance(
        snapshot[
            "mappings"
        ],
        tuple,
    ),
)


# -------------------------------------------------------------------------
# 12. Architecture declaration
# -------------------------------------------------------------------------

architecture = (
    explain_runtime_job_mapping_v5_2()
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
    == "5.2",
)

check(
    "Architecture upstream exact",
    architecture[
        "upstream_authority"
    ]
    == "Phase 5.1 RuntimeHandoffIntent",
)

check(
    "Architecture downstream exact",
    architecture[
        "downstream_authority"
    ]
    == "Universal Job Creation Engine",
)

properties = architecture[
    "execution_properties"
]

for key in (
    "universal_job_creation",
    "job_id_generation",
    "pipeline_run_id_generation",
    "idempotency_key_generation",
    "runtime_registration_lookup",
    "submission",
    "persistence",
    "queue_write",
    "dispatch",
    "business_execution",
    "completion_processing",
    "failure_processing",
    "workflow_job_correlation",
):
    check(
        f"Execution authority disabled: {key}",
        properties[
            key
        ] is False,
    )

check(
    "Mapper read-only",
    properties[
        "read_only"
    ] is True,
)

check(
    "Mapper deterministic",
    properties[
        "deterministic"
    ] is True,
)

check(
    "Mapper fail-closed",
    properties[
        "fail_closed"
    ] is True,
)


# -------------------------------------------------------------------------
# 13. Static import / call boundary
# -------------------------------------------------------------------------

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
                (
                    module,
                    tuple(
                        alias.name
                        for alias
                        in node.names
                    ),
                )
            )


check(
    "Only creation-request Runtime module imported",
    runtime_imports
    == [
        (
            "backend.server.runtime.universal_jobs.creation_engine",
            (
                "UniversalJobCreationRequest",
            ),
        )
    ],
    repr(
        runtime_imports
    ),
)


forbidden_calls = {
    "create_universal_job",
    "normalize_universal_job_creation_request",
    "get_runtime_registration",
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


hits = (
    called
    & forbidden_calls
)

check(
    "No forbidden Runtime calls",
    hits
    == set(),
    repr(
        sorted(
            hits
        )
    ),
)


# -------------------------------------------------------------------------
# Final
# -------------------------------------------------------------------------

candidate_sha = sha256(
    MAPPER
)

check(
    "Candidate SHA256 structurally valid",
    len(
        candidate_sha
    )
    == 64,
    candidate_sha,
)


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
    "PHASE 5.2 — RUNTIME JOB MAPPING INSTALLATION SMOKE",
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
        "PHASE 5.2 INSTALLATION SMOKE RESULT",
        "=" * 116,
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        (
            "STATUS: SMOKE PASSED"
            if failed == 0
            else "STATUS: SMOKE FAILED"
        ),
        (
            "PHASE 5.2 CANDIDATE SHA256: "
            + candidate_sha
        ),
    )
)


REPORT.write_text(
    "\n".join(lines)
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 116)
print("PHASE 5.2 INSTALLATION SMOKE RESULT")
print("=" * 116)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print(
    "STATUS:",
    (
        "SMOKE PASSED"
        if failed == 0
        else "SMOKE FAILED"
    ),
)
print(
    "PHASE 5.2 CANDIDATE SHA256:",
    candidate_sha,
)
print(
    "FROZEN PHASE 5.1 SHA256:",
    frozen_sha,
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
