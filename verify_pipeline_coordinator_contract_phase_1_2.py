from __future__ import annotations

import ast
import hashlib
import importlib
import json
from pathlib import Path

from backend.server.coordination.pipeline_coordinators.contract import (
    PIPELINE_COORDINATOR_CONTRACT_ID,
    PIPELINE_COORDINATOR_CONTRACT_VERSION,
    PIPELINE_COORDINATOR_SCHEMA_VERSION,
    REQUIRED_PIPELINE_COORDINATOR_FIELDS,
    CANONICAL_COORDINATOR_CAPABILITIES,
    REQUIRED_COORDINATOR_CAPABILITIES,
    CoordinatorExecutionModel,
    CoordinatorRuntimePolicy,
    PipelineCoordinatorContract,
    PipelineCoordinatorContractError,
    validate_pipeline_coordinator_contract,
)

from backend.server.coordination.universal_workflows.contract import (
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)

TARGET = Path(
    "backend/server/coordination/pipeline_coordinators/contract.py"
)

checks = []


def check(name, condition, detail=""):
    ok = bool(condition)
    checks.append((name, ok, detail))

    label = "PASS" if ok else "FAIL"
    print(f"[{label}] {name}")

    if detail:
        print(f"       {detail}")

    return ok


print()
print("=" * 72)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 1.2 PIPELINE COORDINATOR CONTRACT CERTIFICATION")
print("=" * 72)


# --------------------------------------------------------------------------
# 1. File / syntax / import
# --------------------------------------------------------------------------

check(
    "Canonical coordinator contract file exists",
    TARGET.exists(),
    str(TARGET),
)

source = TARGET.read_text(encoding="utf-8-sig")

try:
    ast.parse(source)
    syntax_ok = True
except SyntaxError as exc:
    syntax_ok = False
    print(exc)

check(
    "Python syntax parses successfully",
    syntax_ok,
)

try:
    importlib.import_module(
        "backend.server.coordination.pipeline_coordinators.contract"
    )
    import_ok = True
except Exception as exc:
    import_ok = False
    print(repr(exc))

check(
    "Canonical coordinator contract imports successfully",
    import_ok,
)


# --------------------------------------------------------------------------
# 2. Contract identity
# --------------------------------------------------------------------------

check(
    "Contract ID is canonical",
    PIPELINE_COORDINATOR_CONTRACT_ID
    == "urn:linkcraftor:coordination:pipeline-coordinator-contract",
)

check(
    "Contract version is canonical",
    PIPELINE_COORDINATOR_CONTRACT_VERSION
    == "pipeline_coordinator_contract_v1.2.0",
)

check(
    "Schema version is canonical",
    PIPELINE_COORDINATOR_SCHEMA_VERSION
    == "pipeline_coordinator_schema_v1",
)

check(
    "Required field roster contains 14 fields",
    len(REQUIRED_PIPELINE_COORDINATOR_FIELDS) == 14,
    f"count={len(REQUIRED_PIPELINE_COORDINATOR_FIELDS)}",
)

check(
    "workflow_contract_version is required",
    "workflow_contract_version"
    in REQUIRED_PIPELINE_COORDINATOR_FIELDS,
)

check(
    "runtime_policy is required",
    "runtime_policy"
    in REQUIRED_PIPELINE_COORDINATOR_FIELDS,
)

check(
    "contract_version is required",
    "contract_version"
    in REQUIRED_PIPELINE_COORDINATOR_FIELDS,
)


# --------------------------------------------------------------------------
# 3. Capability model
# --------------------------------------------------------------------------

expected_capabilities = {
    "start",
    "advance",
    "stage_completed",
    "stage_failed",
    "pause",
    "resume",
    "cancel",
    "recover",
    "inspect",
}

check(
    "Canonical capability roster is complete",
    set(CANONICAL_COORDINATOR_CAPABILITIES)
    == expected_capabilities,
    json.dumps(
        sorted(CANONICAL_COORDINATOR_CAPABILITIES)
    ),
)

check(
    "start is mandatory",
    REQUIRED_COORDINATOR_CAPABILITIES
    == frozenset({"start"}),
)


# --------------------------------------------------------------------------
# 4. Execution / runtime policy rosters
# --------------------------------------------------------------------------

execution_models = {
    value.value
    for value in CoordinatorExecutionModel
}

check(
    "Execution model roster is complete",
    execution_models
    == {
        "synchronous",
        "asynchronous",
    },
    json.dumps(sorted(execution_models)),
)

runtime_policies = {
    value.value
    for value in CoordinatorRuntimePolicy
}

check(
    "Runtime policy roster is complete",
    runtime_policies
    == {
        "universal_runtime_required",
        "transitional_direct_execution",
        "no_runtime_execution",
    },
    json.dumps(sorted(runtime_policies)),
)


# --------------------------------------------------------------------------
# 5. Canonical reference contract
# --------------------------------------------------------------------------

contract = PipelineCoordinatorContract(
    coordinator_id="linking_target_pipeline_coordinator",
    coordinator_version="v1",
    workflow_type="linking_target_pipeline",
    workflow_version="linking_target_pipeline_v1",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
    entrypoint=(
        "backend.server.pipelines.connect_domain."
        "linking_target_pipeline.coordinator:"
        "run_linking_target_pipeline"
    ),
    execution_model="synchronous",
    runtime_policy="universal_runtime_required",
    capabilities=(
        "start",
        "advance",
        "stage_completed",
        "stage_failed",
        "inspect",
    ),
    stage_job_types=(
        "site_sources",
        "url_cleaner",
        "site_pages",
        "live_domain_target_pool",
        "active_target_set",
    ),
    responsibilities=(
        "own linking target pipeline sequencing",
        "determine eligible next stages",
        "request stage execution through universal runtime",
        "react to stage completion",
        "react to terminal stage failure",
    ),
    excluded_responsibilities=(
        "execute worker jobs",
        "implement runtime queues",
        "implement runtime retries",
        "replace runtime registration",
        "perform stage business logic",
    ),
    metadata={
        "phase": "1.2",
        "reference_pipeline": "linking_target_pipeline",
    },
)

check(
    "Canonical coordinator contract constructs successfully",
    isinstance(
        contract,
        PipelineCoordinatorContract,
    ),
)

check(
    "Workflow contract compatibility is enforced",
    contract.workflow_contract_version
    == UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)

check(
    "Universal Runtime policy recognized",
    contract.uses_universal_runtime,
)

check(
    "Canonical start capability available",
    contract.supports("start"),
)

check(
    "Canonical advance capability available",
    contract.supports("advance"),
)


# --------------------------------------------------------------------------
# 6. Serialization / reconstruction
# --------------------------------------------------------------------------

mapping = contract.to_dict()

check(
    "Serialized field roster matches canonical roster",
    tuple(mapping.keys())
    == REQUIRED_PIPELINE_COORDINATOR_FIELDS,
)

rebuilt = PipelineCoordinatorContract.from_dict(
    mapping
)

check(
    "Mapping reconstruction is lossless",
    rebuilt == contract,
)

json_text = contract.to_canonical_json()

json_rebuilt = PipelineCoordinatorContract.from_json(
    json_text
)

check(
    "JSON reconstruction is lossless",
    json_rebuilt == contract,
)

check(
    "Canonical JSON is deterministic",
    json_text == contract.to_canonical_json(),
)

validation = validate_pipeline_coordinator_contract(
    mapping
)

check(
    "Standalone validation accepts canonical coordinator",
    validation.is_valid,
    json.dumps(validation.to_dict(), indent=2),
)


# --------------------------------------------------------------------------
# 7. Immutability
# --------------------------------------------------------------------------

immutable_ok = False

try:
    contract.coordinator_id = "mutated"
except Exception:
    immutable_ok = True

check(
    "PipelineCoordinatorContract is immutable",
    immutable_ok,
)

metadata_immutable = False

try:
    contract.metadata["illegal"] = True
except Exception:
    metadata_immutable = True

check(
    "Coordinator metadata is immutable",
    metadata_immutable,
)


# --------------------------------------------------------------------------
# 8. Required field enforcement
# --------------------------------------------------------------------------

for field_name in (
    "coordinator_id",
    "workflow_type",
    "entrypoint",
    "runtime_policy",
    "contract_version",
):
    broken = dict(mapping)
    del broken[field_name]

    try:
        PipelineCoordinatorContract.from_dict(
            broken
        )
        rejected = False
    except PipelineCoordinatorContractError:
        rejected = True

    check(
        f"Missing {field_name} is rejected",
        rejected,
    )


# --------------------------------------------------------------------------
# 9. Unknown fields
# --------------------------------------------------------------------------

broken = dict(mapping)
broken["illegal_field"] = True

try:
    PipelineCoordinatorContract.from_dict(
        broken
    )
    rejected = False
except PipelineCoordinatorContractError:
    rejected = True

check(
    "Unknown coordinator fields are rejected",
    rejected,
)


# --------------------------------------------------------------------------
# 10. Capability enforcement
# --------------------------------------------------------------------------

broken = dict(mapping)
broken["capabilities"] = ["advance"]

try:
    PipelineCoordinatorContract.from_dict(
        broken
    )
    rejected = False
except PipelineCoordinatorContractError:
    rejected = True

check(
    "Missing start capability is rejected",
    rejected,
)

broken = dict(mapping)
broken["capabilities"] = [
    "start",
    "invented_capability",
]

try:
    PipelineCoordinatorContract.from_dict(
        broken
    )
    rejected = False
except PipelineCoordinatorContractError:
    rejected = True

check(
    "Unknown capability is rejected",
    rejected,
)


# --------------------------------------------------------------------------
# 11. Entrypoint enforcement
# --------------------------------------------------------------------------

broken = dict(mapping)
broken["entrypoint"] = "bad_entrypoint"

try:
    PipelineCoordinatorContract.from_dict(
        broken
    )
    rejected = False
except PipelineCoordinatorContractError:
    rejected = True

check(
    "Malformed entrypoint is rejected",
    rejected,
)

broken = dict(mapping)
broken["entrypoint"] = ":run_pipeline"

try:
    PipelineCoordinatorContract.from_dict(
        broken
    )
    rejected = False
except PipelineCoordinatorContractError:
    rejected = True

check(
    "Empty entrypoint module is rejected",
    rejected,
)

broken = dict(mapping)
broken["entrypoint"] = (
    "backend.server.example:"
)

try:
    PipelineCoordinatorContract.from_dict(
        broken
    )
    rejected = False
except PipelineCoordinatorContractError:
    rejected = True

check(
    "Empty entrypoint function is rejected",
    rejected,
)


# --------------------------------------------------------------------------
# 12. Runtime policy invariants
# --------------------------------------------------------------------------

broken = dict(mapping)
broken["stage_job_types"] = []

try:
    PipelineCoordinatorContract.from_dict(
        broken
    )
    rejected = False
except PipelineCoordinatorContractError:
    rejected = True

check(
    "Universal Runtime policy requires stage job types",
    rejected,
)

broken = dict(mapping)
broken["runtime_policy"] = "no_runtime_execution"

try:
    PipelineCoordinatorContract.from_dict(
        broken
    )
    rejected = False
except PipelineCoordinatorContractError:
    rejected = True

check(
    "No-runtime policy rejects stage job types",
    rejected,
)


# --------------------------------------------------------------------------
# 13. Transitional migration policy
# --------------------------------------------------------------------------

transitional = PipelineCoordinatorContract(
    coordinator_id="legacy_pipeline_coordinator",
    coordinator_version="legacy_v1",
    workflow_type="legacy_pipeline",
    workflow_version="legacy_pipeline_v1",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
    entrypoint=(
        "backend.server.example.coordinator:"
        "run_legacy_pipeline"
    ),
    execution_model="synchronous",
    runtime_policy="transitional_direct_execution",
    capabilities=("start",),
    stage_job_types=(),
    responsibilities=(
        "coordinate legacy pipeline",
    ),
    excluded_responsibilities=(
        "universal runtime ownership",
    ),
    metadata={
        "migration_required": True,
    },
)

check(
    "Transitional direct-execution coordinator is representable",
    transitional.is_transitional,
)

check(
    "Transitional coordinator is not reported as Universal Runtime integrated",
    not transitional.uses_universal_runtime,
)


# --------------------------------------------------------------------------
# 14. Responsibility boundary protection
# --------------------------------------------------------------------------

broken = dict(mapping)

broken["responsibilities"] = [
    "perform stage business logic",
]

broken["excluded_responsibilities"] = [
    "perform stage business logic",
]

try:
    PipelineCoordinatorContract.from_dict(
        broken
    )
    rejected = False
except PipelineCoordinatorContractError:
    rejected = True

check(
    "Responsibility/exclusion overlap is rejected",
    rejected,
)


# --------------------------------------------------------------------------
# 15. Wrong version enforcement
# --------------------------------------------------------------------------

broken = dict(mapping)
broken["workflow_contract_version"] = (
    "wrong_workflow_contract"
)

try:
    PipelineCoordinatorContract.from_dict(
        broken
    )
    rejected = False
except PipelineCoordinatorContractError:
    rejected = True

check(
    "Wrong Universal Workflow Contract version is rejected",
    rejected,
)

broken = dict(mapping)
broken["contract_version"] = (
    "wrong_coordinator_contract"
)

try:
    PipelineCoordinatorContract.from_dict(
        broken
    )
    rejected = False
except PipelineCoordinatorContractError:
    rejected = True

check(
    "Wrong Pipeline Coordinator Contract version is rejected",
    rejected,
)


# --------------------------------------------------------------------------
# 16. Fingerprints
# --------------------------------------------------------------------------

identity_1 = contract.identity_fingerprint()
identity_2 = rebuilt.identity_fingerprint()

check(
    "Identity fingerprint is stable across reconstruction",
    identity_1 == identity_2,
    identity_1,
)

content_1 = contract.content_fingerprint()
content_2 = rebuilt.content_fingerprint()

check(
    "Content fingerprint is stable across reconstruction",
    content_1 == content_2,
    content_1,
)


# --------------------------------------------------------------------------
# 17. Architectural purity
# --------------------------------------------------------------------------

tree = ast.parse(source)

imports = []

for node in ast.walk(tree):

    if isinstance(node, ast.Import):
        imports.extend(
            alias.name
            for alias in node.names
        )

    elif isinstance(node, ast.ImportFrom):
        if node.module:
            imports.append(node.module)


allowed_coordination_import = (
    "backend.server.coordination.universal_workflows.contract"
)

violating_imports = []

for name in imports:

    if name == allowed_coordination_import:
        continue

    forbidden_fragments = (
        "backend.server.runtime",
        "backend.server.jobs",
        "backend.server.workers",
        "backend.server.pipelines",
        "backend.server.routes",
        "fastapi",
        "requests",
        "sqlalchemy",
        "boto3",
    )

    if any(
        fragment in name
        for fragment in forbidden_fragments
    ):
        violating_imports.append(name)


check(
    "Contract has no runtime/pipeline execution imports",
    not violating_imports,
    json.dumps(violating_imports),
)


forbidden_calls = (
    "open(",
    "Path.write",
    "Path.mkdir",
    "requests.",
    "subprocess.",
    "os.system",
)

violating_calls = [
    marker
    for marker in forbidden_calls
    if marker in source
]

check(
    "Contract performs no I/O or external execution",
    not violating_calls,
    json.dumps(violating_calls),
)


# --------------------------------------------------------------------------
# 18. SHA256
# --------------------------------------------------------------------------

sha256 = hashlib.sha256(
    TARGET.read_bytes()
).hexdigest().upper()

print()
print("Canonical SHA256:")
print(sha256)


# --------------------------------------------------------------------------
# Final
# --------------------------------------------------------------------------

passed = sum(
    1
    for _, ok, _ in checks
    if ok
)

failed = len(checks) - passed

print()
print("=" * 72)
print("CERTIFICATION RESULT")
print("=" * 72)
print(f"Checks: {len(checks)}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")

if failed == 0:
    print()
    print("STATUS: CERTIFICATION PASSED")
else:
    print()
    print("STATUS: CERTIFICATION FAILED")

print("=" * 72)

raise SystemExit(
    0 if failed == 0 else 1
)
