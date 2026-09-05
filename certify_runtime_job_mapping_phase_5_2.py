from __future__ import annotations

import ast
import hashlib
import inspect
import subprocess
from dataclasses import FrozenInstanceError, fields
from pathlib import Path
from types import MappingProxyType

from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
    CoordinationRuntimeBridgeResult,
    RuntimeHandoffIntent,
)

from backend.server.coordination.runtime_integration.runtime_job_mapping import (
    RUNTIME_JOB_MAPPING_VERSION,
    RUNTIME_JOB_MAPPING_SCHEMA_VERSION,
    RUNTIME_JOB_MAPPING_ENTRY_VERSION,
    RUNTIME_JOB_MAPPING_FIELD_COUNT,
    RUNTIME_JOB_MAPPING_RESULT_FIELD_COUNT,
    RuntimeJobMapping,
    RuntimeJobMappingResult,
    RuntimeJobMappingError,
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

CREATION_ENGINE = (
    ROOT
    / "backend/server/runtime/universal_jobs/"
      "creation_engine.py"
)

EXPECTED_MAPPER_SHA = (
    "49227B0686DED28418DE7DEF21101643"
    "18DDCA3858469A05F5A596388BA84E6A"
)

EXPECTED_5_1_SHA = (
    "2DD7AF262C879B4DD58A484AB7470D9E"
    "A9883A80DDE3C77F1DC1ACDFD35CD0E2"
)

EXPECTED_CREATION_ENGINE_SHA = (
    "7BFDC36731B7AD48885258BCBA833718"
    "6430EC1C6A7C2E876ACA223E6E05D63F"
)

REPORT = (
    ROOT
    / "runtime_job_mapping_phase_5_2_final_certification.txt"
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


def make_intent(
    stage_id,
    *,
    wave_index=0,
    runtime_stage=None,
):
    return RuntimeHandoffIntent(
        workflow_id="wf_cert_5_2",
        workspace_id="ws_cert_5_2",
        correlation_id="corr_cert_5_2",
        stage_id=stage_id,
        stage_version=stage_id + "_v1",
        pipeline_id="pipeline_cert_5_2",
        workflow_type="cert_workflow",
        job_type="cert." + stage_id,
        runtime_stage=(
            runtime_stage
            or "runtime_" + stage_id
        ),
        required_payload_fields=(
            "document_id",
        ),
        wave_index=wave_index,
        execution_semantics=(
            "parallel_eligible"
            if wave_index == 0
            else "sequential"
        ),
        payload={
            "document_id":
                stage_id + "_doc",
            "nested": {
                "stage":
                    stage_id,
            },
        },
        metadata={
            "source":
                "phase_5_2_final_certification",
        },
        stage_reference_contract_version=(
            "universal_stage_reference_contract_v1.3.0"
        ),
    )


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.2 — RUNTIME JOB MAPPING")
print("FINAL CERTIFICATION")
print("=" * 120)


# =========================================================================
# 1. Artifact integrity
# =========================================================================

mapper_sha = sha256(
    MAPPER
)

check(
    "Phase 5.2 production file exists",
    MAPPER.exists(),
)

check(
    "Phase 5.2 candidate SHA exact",
    mapper_sha
    == EXPECTED_MAPPER_SHA,
    mapper_sha,
)

check(
    "Frozen Phase 5.1 SHA exact",
    sha256(
        FROZEN_5_1
    )
    == EXPECTED_5_1_SHA,
    sha256(
        FROZEN_5_1
    ),
)

check(
    "Universal Job Creation Engine SHA exact",
    sha256(
        CREATION_ENGINE
    )
    == EXPECTED_CREATION_ENGINE_SHA,
    sha256(
        CREATION_ENGINE
    ),
)


# =========================================================================
# 2. Version identity
# =========================================================================

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


# =========================================================================
# 3. Contract shapes
# =========================================================================

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


# =========================================================================
# 4. Canonical multi-stage mapping
# =========================================================================

intents = (
    make_intent(
        "stage_a",
        wave_index=0,
    ),
    make_intent(
        "stage_b",
        wave_index=0,
    ),
    make_intent(
        "stage_c",
        wave_index=1,
    ),
)

bridge = CoordinationRuntimeBridgeResult(
    workflow_id="wf_cert_5_2",
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
    "Canonical result type exact",
    isinstance(
        result,
        RuntimeJobMappingResult,
    ),
)

check(
    "Canonical mapping count exact",
    result.mapping_count
    == 3,
)

check(
    "Canonical stage order preserved",
    result.stage_ids
    == (
        "stage_a",
        "stage_b",
        "stage_c",
    ),
)

check(
    "Canonical wave indexes preserved",
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
    "Each mapping contains UniversalJobCreationRequest",
    all(
        isinstance(
            item.creation_request,
            UniversalJobCreationRequest,
        )
        for item
        in result.mappings
    ),
)


# =========================================================================
# 5. Exact direct mapping
# =========================================================================

check(
    "workspace_id mapping exact",
    all(
        item.creation_request.workspace_id
        == "ws_cert_5_2"
        for item
        in result.mappings
    ),
)

check(
    "job_type mapping exact",
    tuple(
        item.creation_request.job_type
        for item
        in result.mappings
    )
    == (
        "cert.stage_a",
        "cert.stage_b",
        "cert.stage_c",
    ),
)

check(
    "pipeline_id -> pipeline exact",
    all(
        item.creation_request.pipeline
        == "pipeline_cert_5_2"
        for item
        in result.mappings
    ),
)

check(
    "runtime_stage -> stage exact",
    tuple(
        item.creation_request.stage
        for item
        in result.mappings
    )
    == (
        "runtime_stage_a",
        "runtime_stage_b",
        "runtime_stage_c",
    ),
)


# =========================================================================
# 6. Coordination metadata evidence
# =========================================================================

check(
    "workflow_id preserved as coordination metadata",
    all(
        item.creation_request.metadata[
            "coordination"
        ][
            "workflow_id"
        ]
        == "wf_cert_5_2"
        for item
        in result.mappings
    ),
)

check(
    "correlation_id preserved as coordination metadata",
    all(
        item.creation_request.metadata[
            "coordination"
        ][
            "correlation_id"
        ]
        == "corr_cert_5_2"
        for item
        in result.mappings
    ),
)

check(
    "coordination stage_id preserved separately",
    tuple(
        item.creation_request.metadata[
            "coordination"
        ][
            "stage_id"
        ]
        for item
        in result.mappings
    )
    == (
        "stage_a",
        "stage_b",
        "stage_c",
    ),
)


# =========================================================================
# 7. Correlation ownership protection
# =========================================================================

check(
    "pipeline_run_id remains None",
    all(
        item.creation_request.pipeline_run_id
        is None
        for item
        in result.mappings
    ),
)

check(
    "job_id remains None",
    all(
        item.creation_request.job_id
        is None
        for item
        in result.mappings
    ),
)

check(
    "idempotency_key remains None",
    all(
        item.creation_request.idempotency_key
        is None
        for item
        in result.mappings
    ),
)

check(
    "parent_job_id remains None",
    all(
        item.creation_request.parent_job_id
        is None
        for item
        in result.mappings
    ),
)

check(
    "dependency_job_ids remain empty",
    all(
        item.creation_request.dependency_job_ids
        == ()
        for item
        in result.mappings
    ),
)

check(
    "batch_id remains None",
    all(
        item.creation_request.batch_id
        is None
        for item
        in result.mappings
    ),
)


# =========================================================================
# 8. Runtime defaults
# =========================================================================

check(
    "user_id default exact",
    all(
        item.creation_request.user_id
        == "system"
        for item
        in result.mappings
    ),
)

check(
    "product_id default exact",
    all(
        item.creation_request.product_id
        == "linkcraftor"
        for item
        in result.mappings
    ),
)

check(
    "enqueue intent exact",
    all(
        item.creation_request.enqueue
        is True
        for item
        in result.mappings
    ),
)

check(
    "maximum_attempts remains unresolved",
    all(
        item.creation_request.maximum_attempts
        is None
        for item
        in result.mappings
    ),
)

check(
    "created_at remains Creation Engine-owned",
    all(
        item.creation_request.created_at
        is None
        for item
        in result.mappings
    ),
)


# =========================================================================
# 9. Determinism
# =========================================================================

repeat = map_runtime_handoffs_to_job_requests(
    bridge_result=bridge
)

check(
    "Repeated mapping deterministic",
    repeat
    == result,
)

check(
    "Repeated snapshot deterministic",
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


# =========================================================================
# 10. Immutability
# =========================================================================

mapping_frozen = False

try:
    result.mappings[
        0
    ].stage_id = "mutated"

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
    result.mapping_count = 999

except (
    FrozenInstanceError,
    AttributeError,
):
    result_frozen = True

check(
    "RuntimeJobMappingResult immutable",
    result_frozen,
)

check(
    "Creation request payload immutable",
    isinstance(
        result.mappings[
            0
        ].creation_request.payload,
        MappingProxyType,
    ),
)

check(
    "Creation request metadata immutable",
    isinstance(
        result.mappings[
            0
        ].creation_request.metadata,
        MappingProxyType,
    ),
)


# =========================================================================
# 11. Architecture declaration
# =========================================================================

architecture = (
    explain_runtime_job_mapping_v5_2()
)

check(
    "Architecture declaration immutable",
    isinstance(
        architecture,
        MappingProxyType,
    ),
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

check(
    "Canonical operation exact",
    architecture[
        "canonical_operation"
    ]
    == "map_runtime_handoffs_to_job_requests",
)

correlation = architecture[
    "correlation_boundary"
]

check(
    "workflow_id never becomes pipeline_run_id in 5.2",
    correlation[
        "workflow_id_to_pipeline_run_id"
    ] is False,
)

check(
    "correlation_id never becomes pipeline_run_id in 5.2",
    correlation[
        "correlation_id_to_pipeline_run_id"
    ] is False,
)

check(
    "Phase 5.3 correlation ownership exact",
    correlation[
        "phase_5_3_owns_correlation"
    ] is True,
)


properties = architecture[
    "execution_properties"
]

check(
    "Read-only authority exact",
    properties[
        "read_only"
    ] is True,
)

check(
    "Deterministic authority exact",
    properties[
        "deterministic"
    ] is True,
)

check(
    "Fail-closed authority exact",
    properties[
        "fail_closed"
    ] is True,
)

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
        f"Forbidden authority false: {key}",
        properties[
            key
        ] is False,
    )


# =========================================================================
# 12. Static import boundary
# =========================================================================

source = MAPPER.read_text(
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
    "Only UniversalJobCreationRequest Runtime import",
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


# =========================================================================
# 13. Static call boundary
# =========================================================================

forbidden_calls = {
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


# =========================================================================
# 14. No filesystem write authority
# =========================================================================

filesystem_write_methods = {
    "write_text",
    "write_bytes",
    "mkdir",
    "unlink",
    "rename",
    "touch",
}

write_hits = (
    called
    & filesystem_write_methods
)

check(
    "Mapper performs no filesystem writes",
    write_hits
    == set(),
    repr(
        sorted(
            write_hits
        )
    ),
)


# =========================================================================
# 15. API shape
# =========================================================================

check(
    "Single mapping API keyword-only",
    str(
        inspect.signature(
            map_runtime_handoff_intent_to_creation_request
        )
    ).startswith(
        "(*,"
    ),
)

check(
    "Bulk mapping API keyword-only",
    str(
        inspect.signature(
            map_runtime_handoffs_to_job_requests
        )
    ).startswith(
        "(*,"
    ),
)

check(
    "Validation error subclasses mapper error",
    issubclass(
        RuntimeJobMappingValidationError,
        RuntimeJobMappingError,
    ),
)

check(
    "Mapper error subclasses ValueError",
    issubclass(
        RuntimeJobMappingError,
        ValueError,
    ),
)


# =========================================================================
# 16. Git scope certification
# =========================================================================

git_status = subprocess.run(
    [
        "git",
        "status",
        "--short",
        "--",
        "backend/server/coordination/runtime_integration",
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
    "No Runtime production modification",
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
    "Only runtime_integration production scope changed",
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
# Final result
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

certified = (
    failed
    == 0
)


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.2 — RUNTIME JOB MAPPING",
    "FINAL CERTIFICATION",
    "=" * 120,
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
        f"VERSION: {RUNTIME_JOB_MAPPING_VERSION}",
        f"SCHEMA: {RUNTIME_JOB_MAPPING_SCHEMA_VERSION}",
        f"SHA256: {mapper_sha}",
        (
            "NEXT: 5.2.8 SHA256 Freeze"
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
print("PHASE 5.2 FINAL CERTIFICATION RESULT")
print("=" * 120)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print("CERTIFIED:", certified)
print("VERSION:", RUNTIME_JOB_MAPPING_VERSION)
print("SCHEMA:", RUNTIME_JOB_MAPPING_SCHEMA_VERSION)
print("SHA256:", mapper_sha)
print("REPORT:", REPORT.name)
print("=" * 120)

raise SystemExit(
    0
    if certified
    else 1
)
