from __future__ import annotations

import ast
import hashlib
import importlib
import json
from pathlib import Path

from backend.server.coordination.universal_stages.contract import (
    UNIVERSAL_STAGE_REFERENCE_CONTRACT_ID,
    UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION,
    UNIVERSAL_STAGE_REFERENCE_SCHEMA_VERSION,
    REQUIRED_UNIVERSAL_STAGE_REFERENCE_FIELDS,
    StageExecutionTarget,
    UniversalStageReference,
    UniversalStageReferenceContractError,
    validate_universal_stage_reference,
)

from backend.server.coordination.universal_workflows.contract import (
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)


TARGET = Path(
    "backend/server/coordination/universal_stages/contract.py"
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
print("=" * 78)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 1.3 UNIVERSAL STAGE REFERENCE CONTRACT CERTIFICATION")
print("=" * 78)


# ============================================================================
# 1. File / syntax / import
# ============================================================================

check(
    "Canonical Stage Reference contract file exists",
    TARGET.exists(),
    str(TARGET),
)

source = TARGET.read_text(
    encoding="utf-8-sig"
)

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
        "backend.server.coordination.universal_stages.contract"
    )
    import_ok = True
except Exception as exc:
    import_ok = False
    print(repr(exc))

check(
    "Canonical Stage Reference contract imports successfully",
    import_ok,
)


# ============================================================================
# 2. Contract identity
# ============================================================================

check(
    "Contract ID is canonical",
    UNIVERSAL_STAGE_REFERENCE_CONTRACT_ID
    == (
        "urn:linkcraftor:coordination:"
        "universal-stage-reference-contract"
    ),
)

check(
    "Contract version is canonical",
    UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION
    == "universal_stage_reference_contract_v1.3.0",
)

check(
    "Schema version is canonical",
    UNIVERSAL_STAGE_REFERENCE_SCHEMA_VERSION
    == "universal_stage_reference_schema_v1",
)

check(
    "Required field roster contains 11 fields",
    len(
        REQUIRED_UNIVERSAL_STAGE_REFERENCE_FIELDS
    ) == 11,
    f"count={len(REQUIRED_UNIVERSAL_STAGE_REFERENCE_FIELDS)}",
)


expected_fields = (
    "stage_id",
    "stage_version",
    "pipeline_id",
    "workflow_type",
    "workflow_contract_version",
    "execution_target",
    "job_type",
    "runtime_stage",
    "required_payload_fields",
    "metadata",
    "contract_version",
)

check(
    "Required field roster is canonical",
    REQUIRED_UNIVERSAL_STAGE_REFERENCE_FIELDS
    == expected_fields,
    json.dumps(
        list(
            REQUIRED_UNIVERSAL_STAGE_REFERENCE_FIELDS
        )
    ),
)


# ============================================================================
# 3. Execution target model
# ============================================================================

execution_targets = {
    value.value
    for value in StageExecutionTarget
}

check(
    "Execution target roster is complete",
    execution_targets
    == {
        "universal_runtime",
        "coordination_only",
    },
    json.dumps(
        sorted(
            execution_targets
        )
    ),
)


# ============================================================================
# 4. Canonical runtime-backed Stage Reference
# ============================================================================

stage = UniversalStageReference(
    stage_id="article_validation",
    stage_version="v3",
    pipeline_id="website_source_pipeline",
    workflow_type="website_source_pipeline",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
    execution_target="universal_runtime",
    job_type="article_validation_population_v3",
    runtime_stage="article_validation",
    required_payload_fields=(
        "workspace_id",
    ),
    metadata={
        "phase": "1.3",
        "reference_stage": "article_validation",
    },
)

check(
    "Canonical runtime-backed Stage Reference constructs",
    isinstance(
        stage,
        UniversalStageReference,
    ),
)

check(
    "Universal Workflow Contract compatibility is enforced",
    stage.workflow_contract_version
    == UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)

check(
    "Runtime-backed stage reports Universal Runtime usage",
    stage.uses_universal_runtime,
)

check(
    "Runtime-backed stage is not coordination-only",
    not stage.is_coordination_only,
)

check(
    "Runtime lookup authority resolves to job_type",
    stage.runtime_lookup_key
    == "article_validation_population_v3",
    str(
        stage.runtime_lookup_key
    ),
)

check(
    "Runtime stage identity preserved",
    stage.runtime_stage
    == "article_validation",
)

check(
    "Required payload declaration preserved",
    stage.required_payload_fields
    == (
        "workspace_id",
    ),
)


# ============================================================================
# 5. Serialization / reconstruction
# ============================================================================

mapping = stage.to_dict()

check(
    "Serialized field roster matches canonical roster",
    tuple(
        mapping.keys()
    )
    == REQUIRED_UNIVERSAL_STAGE_REFERENCE_FIELDS,
)

rebuilt = UniversalStageReference.from_dict(
    mapping
)

check(
    "Mapping reconstruction is lossless",
    rebuilt == stage,
)

json_text = stage.to_canonical_json()

json_rebuilt = UniversalStageReference.from_json(
    json_text
)

check(
    "JSON reconstruction is lossless",
    json_rebuilt == stage,
)

check(
    "Canonical JSON is deterministic",
    json_text
    == stage.to_canonical_json(),
)

validation = validate_universal_stage_reference(
    mapping
)

check(
    "Standalone validation accepts canonical Stage Reference",
    validation.is_valid,
    json.dumps(
        validation.to_dict(),
        indent=2,
    ),
)


# ============================================================================
# 6. Immutability
# ============================================================================

immutable_ok = False

try:
    stage.stage_id = "mutated"
except Exception:
    immutable_ok = True

check(
    "UniversalStageReference is immutable",
    immutable_ok,
)

metadata_immutable = False

try:
    stage.metadata[
        "illegal"
    ] = True
except Exception:
    metadata_immutable = True

check(
    "Stage Reference metadata is immutable",
    metadata_immutable,
)


# ============================================================================
# 7. Missing required field enforcement
# ============================================================================

for field_name in (
    "stage_id",
    "stage_version",
    "pipeline_id",
    "workflow_type",
    "workflow_contract_version",
    "execution_target",
    "job_type",
    "runtime_stage",
    "required_payload_fields",
    "metadata",
    "contract_version",
):
    broken = dict(mapping)
    del broken[field_name]

    try:
        UniversalStageReference.from_dict(
            broken
        )
        rejected = False

    except UniversalStageReferenceContractError:
        rejected = True

    check(
        f"Missing {field_name} is rejected",
        rejected,
    )


# ============================================================================
# 8. Unknown field protection
# ============================================================================

for illegal_field in (
    "handler_ref",
    "handler",
    "retry_policy",
    "concurrency_policy",
    "idempotency_fields",
    "predecessor_stages",
    "successor_stages",
):
    broken = dict(mapping)
    broken[
        illegal_field
    ] = "illegal"

    try:
        UniversalStageReference.from_dict(
            broken
        )
        rejected = False

    except UniversalStageReferenceContractError:
        rejected = True

    check(
        f"Runtime/dependency authority field {illegal_field} is rejected",
        rejected,
    )


# ============================================================================
# 9. Runtime target invariants
# ============================================================================

broken = dict(mapping)
broken["job_type"] = ""

try:
    UniversalStageReference.from_dict(
        broken
    )
    rejected = False
except UniversalStageReferenceContractError:
    rejected = True

check(
    "Universal Runtime target requires job_type",
    rejected,
)

broken = dict(mapping)
broken["runtime_stage"] = ""

try:
    UniversalStageReference.from_dict(
        broken
    )
    rejected = False
except UniversalStageReferenceContractError:
    rejected = True

check(
    "Universal Runtime target requires runtime_stage",
    rejected,
)


# ============================================================================
# 10. Coordination-only reference
# ============================================================================

coordination_stage = UniversalStageReference(
    stage_id="workflow_join",
    stage_version="v1",
    pipeline_id="example_pipeline",
    workflow_type="example_pipeline",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
    execution_target="coordination_only",
    job_type="",
    runtime_stage="",
    required_payload_fields=(),
    metadata={
        "kind": "workflow_control",
    },
)

check(
    "Coordination-only Stage Reference constructs",
    coordination_stage.is_coordination_only,
)

check(
    "Coordination-only Stage Reference does not use Universal Runtime",
    not coordination_stage.uses_universal_runtime,
)

check(
    "Coordination-only Stage Reference has no runtime lookup key",
    coordination_stage.runtime_lookup_key is None,
)


broken = coordination_stage.to_dict()
broken["job_type"] = "illegal_runtime_job"

try:
    UniversalStageReference.from_dict(
        broken
    )
    rejected = False
except UniversalStageReferenceContractError:
    rejected = True

check(
    "Coordination-only reference rejects job_type",
    rejected,
)


broken = coordination_stage.to_dict()
broken["runtime_stage"] = "illegal_runtime_stage"

try:
    UniversalStageReference.from_dict(
        broken
    )
    rejected = False
except UniversalStageReferenceContractError:
    rejected = True

check(
    "Coordination-only reference rejects runtime_stage",
    rejected,
)


broken = coordination_stage.to_dict()

broken["required_payload_fields"] = (
    "workspace_id",
)

try:
    UniversalStageReference.from_dict(
        broken
    )
    rejected = False
except UniversalStageReferenceContractError:
    rejected = True

check(
    "Coordination-only reference rejects payload declaration",
    rejected,
)


# ============================================================================
# 11. Version protection
# ============================================================================

broken = dict(mapping)

broken[
    "workflow_contract_version"
] = "wrong_workflow_contract"

try:
    UniversalStageReference.from_dict(
        broken
    )
    rejected = False
except UniversalStageReferenceContractError:
    rejected = True

check(
    "Wrong Universal Workflow Contract version is rejected",
    rejected,
)


broken = dict(mapping)

broken[
    "contract_version"
] = "wrong_stage_reference_contract"

try:
    UniversalStageReference.from_dict(
        broken
    )
    rejected = False
except UniversalStageReferenceContractError:
    rejected = True

check(
    "Wrong Stage Reference Contract version is rejected",
    rejected,
)


# ============================================================================
# 12. Name validation
# ============================================================================

for field_name in (
    "stage_id",
    "stage_version",
    "pipeline_id",
    "workflow_type",
):
    broken = dict(mapping)

    broken[
        field_name
    ] = "invalid value with spaces"

    try:
        UniversalStageReference.from_dict(
            broken
        )
        rejected = False
    except UniversalStageReferenceContractError:
        rejected = True

    check(
        f"Invalid {field_name} characters are rejected",
        rejected,
    )


# ============================================================================
# 13. Payload declaration validation
# ============================================================================

broken = dict(mapping)

broken[
    "required_payload_fields"
] = "workspace_id"

try:
    UniversalStageReference.from_dict(
        broken
    )
    rejected = False
except UniversalStageReferenceContractError:
    rejected = True

check(
    "Payload fields must be a collection",
    rejected,
)


broken = dict(mapping)

broken[
    "required_payload_fields"
] = [
    "workspace_id",
    "workspace_id",
]

deduped = UniversalStageReference.from_dict(
    broken
)

check(
    "Duplicate payload declarations are normalized",
    deduped.required_payload_fields
    == (
        "workspace_id",
    ),
)


# ============================================================================
# 14. Fingerprints
# ============================================================================

identity_1 = stage.identity_fingerprint()
identity_2 = rebuilt.identity_fingerprint()

check(
    "Identity fingerprint is stable across reconstruction",
    identity_1 == identity_2,
    identity_1,
)


content_1 = stage.content_fingerprint()
content_2 = rebuilt.content_fingerprint()

check(
    "Content fingerprint is stable across reconstruction",
    content_1 == content_2,
    content_1,
)


# ============================================================================
# 15. Schema authority
# ============================================================================

schema = dict(
    UniversalStageReference.schema()
)

check(
    "Schema declares job_type as Runtime Registration lookup authority",
    schema.get(
        "runtime_lookup_authority"
    )
    == "job_type",
)

check(
    "Schema declares Universal Workflow compatibility",
    schema.get(
        "workflow_contract_version"
    )
    == UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)


# ============================================================================
# 16. Architectural purity
# ============================================================================

tree = ast.parse(
    source
)

imports = []

for node in ast.walk(tree):

    if isinstance(
        node,
        ast.Import,
    ):
        imports.extend(
            alias.name
            for alias in node.names
        )

    elif isinstance(
        node,
        ast.ImportFrom,
    ):
        if node.module:
            imports.append(
                node.module
            )


allowed_coordination_import = (
    "backend.server.coordination.universal_workflows.contract"
)

violating_imports = []

for name in imports:

    if name == allowed_coordination_import:
        continue

    forbidden_fragments = (
        "backend.server.runtime",
        "backend.server.pipelines",
        "backend.server.jobs",
        "backend.server.workers",
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
        violating_imports.append(
            name
        )


check(
    "Stage Reference has no runtime/pipeline execution imports",
    not violating_imports,
    json.dumps(
        violating_imports
    ),
)


forbidden_source_markers = (
    "handler_ref:",
    "handler:",
    "retry_policy:",
    "concurrency_policy:",
    "idempotency_fields:",
    "predecessor_stages:",
    "successor_stages:",
)

violating_authority = [
    marker
    for marker in forbidden_source_markers
    if marker in source
]

check(
    "Stage Reference does not structurally own Runtime Registration or dependency authority",
    not violating_authority,
    json.dumps(
        violating_authority
    ),
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
    "Stage Reference performs no I/O or external execution",
    not violating_calls,
    json.dumps(
        violating_calls
    ),
)


# ============================================================================
# 17. SHA256
# ============================================================================

sha256 = hashlib.sha256(
    TARGET.read_bytes()
).hexdigest().upper()

print()
print("Canonical SHA256:")
print(
    sha256
)


# ============================================================================
# Final
# ============================================================================

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

print()
print("=" * 78)
print("CERTIFICATION RESULT")
print("=" * 78)

print(
    f"Checks: {len(checks)}"
)

print(
    f"Passed: {passed}"
)

print(
    f"Failed: {failed}"
)

if failed == 0:

    print()
    print(
        "STATUS: CERTIFICATION PASSED"
    )

else:

    print()
    print(
        "STATUS: CERTIFICATION FAILED"
    )

print("=" * 78)

raise SystemExit(
    0
    if failed == 0
    else 1
)
