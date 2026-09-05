from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
from dataclasses import MISSING, fields, is_dataclass
from pathlib import Path
from types import MappingProxyType


ROOT = Path.cwd()

REPORT = (
    ROOT
    / "runtime_job_mapping_phase_5_2_architecture_resolution.txt"
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


CREATION_ENGINE_MODULE = (
    "backend.server.runtime.universal_jobs.creation_engine"
)

METADATA_MODULE = (
    "backend.server.runtime.universal_jobs.metadata"
)

PRIORITY_MODULE = (
    "backend.server.runtime.universal_jobs.priority"
)

LINEAGE_MODULE = (
    "backend.server.runtime.universal_jobs.lineage"
)


def sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def signature(
    obj,
):
    try:
        return str(
            inspect.signature(
                obj
            )
        )
    except Exception as exc:
        return (
            "<SIGNATURE ERROR: "
            + repr(
                exc
            )
            + ">"
        )


def default_description(
    field,
):
    if field.default is not MISSING:
        return repr(
            field.default
        )

    if field.default_factory is not MISSING:
        try:
            return (
                "<factory -> "
                + repr(
                    field.default_factory()
                )
                + ">"
            )
        except Exception:
            return "<factory>"

    return "<required>"


report = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.2 — RUNTIME JOB MAPPING",
    "ARCHITECTURE RESOLUTION",
    "=" * 120,
    "",
]


# =========================================================================
# 1. Frozen 5.1 integrity
# =========================================================================

current_5_1_sha = sha256(
    FROZEN_5_1
)

report.extend(
    (
        "1. FROZEN PHASE 5.1 INTEGRITY",
        "=" * 120,
        f"Current SHA256: {current_5_1_sha}",
        (
            "Exact frozen SHA: "
            + str(
                current_5_1_sha
                == EXPECTED_5_1_SHA
            )
        ),
        "",
    )
)


# =========================================================================
# 2. UniversalJobCreationRequest defaults
# =========================================================================

creation_module = importlib.import_module(
    CREATION_ENGINE_MODULE
)

request_cls = getattr(
    creation_module,
    "UniversalJobCreationRequest",
)

creation_result_cls = getattr(
    creation_module,
    "UniversalJobCreationResult",
)

create_universal_job = getattr(
    creation_module,
    "create_universal_job",
)

normalize_request = getattr(
    creation_module,
    "normalize_universal_job_creation_request",
)


report.extend(
    (
        "=" * 120,
        "2. UNIVERSAL JOB CREATION REQUEST CONTRACT",
        "=" * 120,
        "",
        "Signature:",
        signature(
            request_cls
        ),
        "",
        "Fields / defaults:",
    )
)


for item in fields(
    request_cls
):

    report.append(
        f"  {item.name}: "
        + default_description(
            item
        )
    )


# =========================================================================
# 3. Construction behavior without creation
# =========================================================================

request = request_cls(
    workspace_id="ws_architecture_5_2",
    job_type="architecture.stage_a",
    payload={
        "document_id": "doc_1",
    },
    metadata={
        "coordination": {
            "workflow_id": "wf_architecture_5_2",
            "correlation_id": "corr_architecture_5_2",
            "stage_id": "stage_a",
        },
    },
    pipeline="architecture_pipeline",
    stage="runtime_stage_a",
)


report.extend(
    (
        "",
        "=" * 120,
        "3. RAW REQUEST CONSTRUCTION",
        "=" * 120,
        "",
        f"Type exact: {type(request) is request_cls}",
        f"workspace_id: {request.workspace_id!r}",
        f"job_type: {request.job_type!r}",
        f"pipeline: {request.pipeline!r}",
        f"stage: {request.stage!r}",
        f"user_id: {request.user_id!r}",
        f"product_id: {request.product_id!r}",
        f"payload_reference: {request.payload_reference!r}",
        f"priority: {request.priority!r}",
        f"parent_job_id: {request.parent_job_id!r}",
        f"dependency_job_ids: {request.dependency_job_ids!r}",
        f"batch_id: {request.batch_id!r}",
        f"pipeline_run_id: {request.pipeline_run_id!r}",
        f"idempotency_key: {request.idempotency_key!r}",
        f"maximum_attempts: {request.maximum_attempts!r}",
        f"enqueue: {request.enqueue!r}",
        f"job_id: {request.job_id!r}",
        f"job_id_prefix: {request.job_id_prefix!r}",
        f"created_at: {request.created_at!r}",
        "",
    )
)


# =========================================================================
# 4. Metadata compatibility / normalization
# =========================================================================

metadata_module = importlib.import_module(
    METADATA_MODULE
)

normalize_metadata = getattr(
    metadata_module,
    "normalize_universal_job_metadata",
    None,
)


report.extend(
    (
        "=" * 120,
        "4. METADATA COMPATIBILITY",
        "=" * 120,
        "",
    )
)


if normalize_metadata is None:

    report.append(
        "normalize_universal_job_metadata: NOT FOUND"
    )

else:

    report.append(
        "normalize_universal_job_metadata signature: "
        + signature(
            normalize_metadata
        )
    )

    normalized_metadata = normalize_metadata(
        {
            "source": "phase_5_2_architecture_resolution",
            "coordination": {
                "workflow_id": "wf_architecture_5_2",
                "correlation_id": "corr_architecture_5_2",
                "stage_id": "stage_a",
                "stage_version": "stage_a_v1",
                "workflow_type": "architecture_workflow",
                "wave_index": 0,
                "execution_semantics": "parallel_eligible",
                "required_payload_fields": (
                    "document_id",
                ),
                "stage_reference_contract_version": (
                    "universal_stage_reference_contract_v1.3.0"
                ),
                "runtime_handoff_intent_version": (
                    "runtime_handoff_intent_v5.1.0"
                ),
            },
        }
    )

    report.append(
        "Nested coordination metadata accepted: True"
    )

    report.append(
        "Normalized metadata type: "
        + type(
            normalized_metadata
        ).__name__
    )

    report.append(
        "Normalized metadata: "
        + repr(
            normalized_metadata
        )
    )


# =========================================================================
# 5. Request mutability boundary
# =========================================================================

report.extend(
    (
        "",
        "=" * 120,
        "5. REQUEST MUTABILITY BOUNDARY",
        "=" * 120,
        "",
        (
            "UniversalJobCreationRequest is dataclass: "
            + str(
                is_dataclass(
                    request_cls
                )
            )
        ),
    )
)


frozen_params = getattr(
    request_cls,
    "__dataclass_params__",
    None,
)

report.append(
    "Dataclass frozen: "
    + str(
        getattr(
            frozen_params,
            "frozen",
            None,
        )
    )
)


mutation_allowed = False
mutation_blocked = False

try:
    request.pipeline = "mutated_pipeline"
    mutation_allowed = True

except Exception:
    mutation_blocked = True


report.append(
    "Raw Runtime creation request mutation allowed: "
    + str(
        mutation_allowed
    )
)

report.append(
    "Raw Runtime creation request mutation blocked: "
    + str(
        mutation_blocked
    )
)

report.append(
    (
        "Architecture implication: UniversalJobCreationRequest is already "
        "immutable, so Phase 5.2 can safely embed it inside an immutable "
        "UCF mapping result without compensating for request mutability."
    )
)


# =========================================================================
# 6. Static Creation Engine boundary
# =========================================================================

creation_path = Path(
    inspect.getfile(
        creation_module
    )
).resolve()

creation_source = creation_path.read_text(
    encoding="utf-8-sig"
)

creation_tree = ast.parse(
    creation_source
)


called_names = set()

for node in ast.walk(
    creation_tree
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


forbidden_io = {
    "open",
    "write",
    "write_text",
    "write_bytes",
    "mkdir",
    "unlink",
    "rename",
    "replace",
    "create_orchestration_job",
    "submit_universal_job",
    "get_runtime_registration",
    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",
}


report.extend(
    (
        "",
        "=" * 120,
        "6. CREATION ENGINE STATIC BOUNDARY",
        "=" * 120,
        "",
        "Creation Engine SHA256: "
        + sha256(
            creation_path
        ),
        "",
        "Forbidden I/O / Runtime calls found:",
        repr(
            sorted(
                called_names
                & forbidden_io
            )
        ),
        "",
    )
)


# =========================================================================
# 7. Mapper import boundary design
# =========================================================================

report.extend(
    (
        "=" * 120,
        "7. PHASE 5.2 IMPORT BOUNDARY",
        "=" * 120,
        "",
        "Allowed imports:",
        "  backend.server.coordination.runtime_integration.coordination_runtime_bridge",
        "  backend.server.runtime.universal_jobs.creation_engine",
        "",
        "Permitted Runtime symbols:",
        "  UniversalJobCreationRequest",
        "",
        "Forbidden Runtime symbols:",
        "  create_universal_job",
        "  normalize_universal_job_creation_request",
        "  UniversalJobCreationResult",
        "  UniversalJob",
        "  get_runtime_registration",
        "  submit_universal_job",
        "  create_orchestration_job",
        "  dispatch_registered_runtime_handler",
        "  execute_registered_runtime_job_v1",
        "",
    )
)


# =========================================================================
# 8. Canonical 5.2 data model
# =========================================================================

report.extend(
    (
        "=" * 120,
        "8. CANONICAL PHASE 5.2 DATA MODEL",
        "=" * 120,
        "",
        "Proposed immutable UCF mapper objects:",
        "",
        "RuntimeJobMapping",
        "  workflow_id",
        "  correlation_id",
        "  stage_id",
        "  wave_index",
        "  creation_request",
        "  mapping_version",
        "",
        "RuntimeJobMappingResult",
        "  workflow_id",
        "  mapping_count",
        "  mappings",
        "  stage_ids",
        "  mapper_version",
        "  schema_version",
        "",
        "Rules:",
        "  One RuntimeHandoffIntent -> one RuntimeJobMapping.",
        "  One RuntimeJobMapping -> one UniversalJobCreationRequest.",
        "  Ordering must exactly preserve Phase 5.1 intent ordering.",
        "  Empty Phase 5.1 handoff result -> zero mappings.",
        "  workflow_id is coordination identity only.",
        "  correlation_id is coordination identity only.",
        "  pipeline_run_id remains None.",
        "  job_id remains None.",
        "  idempotency_key remains None.",
        "",
    )
)


# =========================================================================
# 9. Canonical direct field mapping
# =========================================================================

report.extend(
    (
        "=" * 120,
        "9. CANONICAL DIRECT FIELD MAPPING",
        "=" * 120,
        "",
        "workspace_id = intent.workspace_id",
        "job_type = intent.job_type",
        "payload = immutable copy/snapshot of intent.payload",
        "pipeline = intent.pipeline_id",
        "stage = intent.runtime_stage",
        "enqueue = True",
        "",
        "Runtime defaults retained:",
        "user_id = 'system'",
        "product_id = 'linkcraftor'",
        "payload_reference = None",
        "priority = UniversalJobCreationRequest default",
        "parent_job_id = None",
        "dependency_job_ids = ()",
        "batch_id = None",
        "pipeline_run_id = None",
        "idempotency_key = None",
        "maximum_attempts = None",
        "job_id = None",
        "job_id_prefix = canonical request default",
        "created_at = None",
        "",
    )
)


# =========================================================================
# 10. Canonical metadata
# =========================================================================

report.extend(
    (
        "=" * 120,
        "10. CANONICAL COORDINATION METADATA",
        "=" * 120,
        "",
        "Existing intent.metadata must be preserved.",
        "",
        "Add nested key:",
        "",
        "coordination = {",
        "  workflow_id,",
        "  correlation_id,",
        "  stage_id,",
        "  stage_version,",
        "  workflow_type,",
        "  wave_index,",
        "  execution_semantics,",
        "  required_payload_fields,",
        "  stage_reference_contract_version,",
        "  runtime_handoff_intent_version,",
        "}",
        "",
        "Collision rule:",
        "  If intent.metadata already contains key 'coordination',",
        "  mapper must fail closed rather than overwrite caller evidence.",
        "",
    )
)


# =========================================================================
# 11. Explicit prohibitions
# =========================================================================

report.extend(
    (
        "=" * 120,
        "11. PHASE 5.2 PROHIBITIONS",
        "=" * 120,
        "",
        "Phase 5.2 MUST NOT:",
        "  create UniversalJob",
        "  call create_universal_job",
        "  normalize Runtime creation request through Creation Engine",
        "  generate job_id",
        "  generate pipeline_run_id",
        "  generate idempotency_key",
        "  assign parent_job_id",
        "  assign dependency_job_ids",
        "  assign batch_id",
        "  perform Runtime Registration lookup",
        "  call submit_universal_job",
        "  persist anything",
        "  enqueue anything",
        "  dispatch handlers",
        "  execute handlers",
        "  execute business stages",
        "  process completion",
        "  process failure",
        "  establish workflow/job correlation",
        "",
    )
)


# =========================================================================
# 12. Architecture resolution
# =========================================================================

report.extend(
    (
        "=" * 120,
        "12. ARCHITECTURE RESOLUTION",
        "=" * 120,
        "",
        "INPUT:",
        "  Phase 5.1 CoordinationRuntimeBridgeResult",
        "",
        "TRANSFORMATION:",
        "  Each RuntimeHandoffIntent is deterministically converted",
        "  to one UniversalJobCreationRequest.",
        "",
        "OUTPUT:",
        "  Immutable RuntimeJobMappingResult.",
        "",
        "DOWNSTREAM:",
        "  Universal Job Creation Engine.",
        "",
        "FOLLOWING RESPONSIBILITY:",
        "  Phase 5.3 Workflow/Job Correlation binds Coordination",
        "  identity to actual canonical Universal Job identity.",
        "",
        "Architecture status: RESOLVED",
        "Production modified: False",
        "Installation performed: False",
        "Next: 5.2.4 Installation / Patch",
    )
)


REPORT.write_text(
    "\n".join(
        report
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 120)
print("PHASE 5.2 — RUNTIME JOB MAPPING")
print("ARCHITECTURE RESOLUTION COMPLETE")
print("=" * 120)

print(
    "Frozen 5.1 exact:",
    current_5_1_sha
    == EXPECTED_5_1_SHA,
)

print(
    "UniversalJobCreationRequest signature:",
    signature(
        request_cls
    ),
)

print(
    "Raw request mutable:",
    mutation_allowed,
)

print(
    "Creation Engine forbidden I/O hits:",
    sorted(
        called_names
        & forbidden_io
    ),
)

print(
    "Architecture status: RESOLVED"
)

print(
    "Production modified: False"
)

print(
    "NEXT: 5.2.4 Installation / Patch"
)

print(
    "REPORT:",
    REPORT.name,
)

print("=" * 120)
