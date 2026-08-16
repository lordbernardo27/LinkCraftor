from __future__ import annotations

import ast
import hashlib
import importlib
import json
from pathlib import Path

from backend.server.coordination.universal_stages.result_contract import (
    UNIVERSAL_STAGE_RESULT_CONTRACT_ID,
    UNIVERSAL_STAGE_RESULT_CONTRACT_VERSION,
    UNIVERSAL_STAGE_RESULT_SCHEMA_VERSION,
    REQUIRED_UNIVERSAL_STAGE_RESULT_FIELDS,
    UniversalStageResultStatus,
    UniversalStageResult,
    UniversalStageResultContractError,
    validate_universal_stage_result,
)

from backend.server.coordination.universal_stages.contract import (
    UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION,
    StageExecutionTarget,
)

from backend.server.coordination.universal_workflows.contract import (
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)


TARGET = Path(
    "backend/server/coordination/universal_stages/result_contract.py"
)

REPORT = Path(
    "universal_stage_result_phase_1_4_certification.txt"
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
print("=" * 82)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 1.4 UNIVERSAL STAGE RESULT CONTRACT CERTIFICATION")
print("=" * 82)


# ============================================================================
# 1. File / syntax / import
# ============================================================================

check(
    "Canonical Stage Result contract file exists",
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
        "backend.server.coordination.universal_stages.result_contract"
    )
    import_ok = True
except Exception as exc:
    import_ok = False
    print(repr(exc))

check(
    "Canonical Stage Result contract imports successfully",
    import_ok,
)


# ============================================================================
# 2. Identity
# ============================================================================

check(
    "Contract ID is canonical",
    UNIVERSAL_STAGE_RESULT_CONTRACT_ID
    == (
        "urn:linkcraftor:coordination:"
        "universal-stage-result-contract"
    ),
)

check(
    "Contract version is canonical",
    UNIVERSAL_STAGE_RESULT_CONTRACT_VERSION
    == "universal_stage_result_contract_v1.4.0",
)

check(
    "Schema version is canonical",
    UNIVERSAL_STAGE_RESULT_SCHEMA_VERSION
    == "universal_stage_result_schema_v1",
)


expected_fields = (
    "result_id",
    "workflow_id",
    "correlation_id",
    "stage_id",
    "stage_version",
    "pipeline_id",
    "workflow_type",
    "workspace_id",
    "execution_target",
    "job_id",
    "job_type",
    "status",
    "output",
    "result_reference",
    "artifact_references",
    "started_at",
    "finished_at",
    "failure_code",
    "failure_message",
    "failure_details",
    "metadata",
    "workflow_contract_version",
    "stage_reference_contract_version",
    "contract_version",
)

check(
    "Required field count is exactly 24",
    len(REQUIRED_UNIVERSAL_STAGE_RESULT_FIELDS) == 24,
    f"count={len(REQUIRED_UNIVERSAL_STAGE_RESULT_FIELDS)}",
)

check(
    "Required field roster is canonical",
    REQUIRED_UNIVERSAL_STAGE_RESULT_FIELDS
    == expected_fields,
    json.dumps(
        list(
            REQUIRED_UNIVERSAL_STAGE_RESULT_FIELDS
        )
    ),
)


# ============================================================================
# 3. Terminal status model
# ============================================================================

statuses = {
    value.value
    for value
    in UniversalStageResultStatus
}

check(
    "Terminal status roster is complete",
    statuses
    == {
        "completed",
        "failed",
        "skipped",
        "cancelled",
    },
    json.dumps(sorted(statuses)),
)


# ============================================================================
# 4. Canonical successful runtime result
# ============================================================================

result = UniversalStageResult(
    result_id="stage-result-001",
    workflow_id="workflow-001",
    correlation_id="correlation-001",
    stage_id="article_validation",
    stage_version="v3",
    pipeline_id="website_source_pipeline",
    workflow_type="website_source_pipeline",
    workspace_id="ws-test",
    execution_target="universal_runtime",
    job_id="job-001",
    job_type="article_validation_population_v3",
    status="completed",
    output={
        "ok": True,
        "processed_count": 10,
        "pass_count": 10,
        "fail_count": 0,
    },
    result_reference="article-validation-result-001",
    artifact_references=(
        "artifact://validation/report.json",
        "artifact://validation/certificate.json",
    ),
    started_at="2026-08-15T22:00:00+00:00",
    finished_at="2026-08-15T22:01:00+00:00",
    failure_code="",
    failure_message="",
    failure_details={},
    metadata={
        "phase": "1.4",
        "reference_stage": "article_validation",
    },
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
    stage_reference_contract_version=(
        UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION
    ),
)

check(
    "Canonical runtime-backed result constructs",
    isinstance(
        result,
        UniversalStageResult,
    ),
)

check(
    "Completed status property is correct",
    result.completed,
)

check(
    "Failed property is false for completed result",
    not result.failed,
)

check(
    "Skipped property is false for completed result",
    not result.skipped,
)

check(
    "Cancelled property is false for completed result",
    not result.cancelled,
)

check(
    "All Stage Results are terminal",
    result.terminal,
)

check(
    "Workflow Contract compatibility preserved",
    result.workflow_contract_version
    == UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)

check(
    "Stage Reference Contract compatibility preserved",
    result.stage_reference_contract_version
    == UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION,
)

check(
    "Runtime job_id preserved",
    result.job_id == "job-001",
)

check(
    "Runtime job_type preserved",
    result.job_type
    == "article_validation_population_v3",
)

check(
    "Opaque business output preserved",
    result.output.get("ok") is True
    and result.output.get("processed_count") == 10,
)

check(
    "Result reference preserved",
    result.result_reference
    == "article-validation-result-001",
)

check(
    "Artifact references preserved",
    len(
        result.artifact_references
    ) == 2,
)


# ============================================================================
# 5. Serialization
# ============================================================================

mapping = result.to_dict()

check(
    "Serialized field order matches canonical roster",
    tuple(mapping.keys())
    == REQUIRED_UNIVERSAL_STAGE_RESULT_FIELDS,
)

rebuilt = UniversalStageResult.from_dict(
    mapping
)

check(
    "Mapping reconstruction is lossless",
    rebuilt == result,
)

json_text = result.to_canonical_json()

json_rebuilt = UniversalStageResult.from_json(
    json_text
)

check(
    "JSON reconstruction is lossless",
    json_rebuilt == result,
)

check(
    "Canonical JSON is deterministic",
    json_text
    == result.to_canonical_json(),
)

validation = validate_universal_stage_result(
    mapping
)

check(
    "Standalone validation accepts canonical result",
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
    result.result_id = "mutated"
except Exception:
    immutable_ok = True

check(
    "UniversalStageResult is immutable",
    immutable_ok,
)

output_immutable = False

try:
    result.output[
        "illegal"
    ] = True
except Exception:
    output_immutable = True

check(
    "Business output mapping is immutable",
    output_immutable,
)

metadata_immutable = False

try:
    result.metadata[
        "illegal"
    ] = True
except Exception:
    metadata_immutable = True

check(
    "Metadata mapping is immutable",
    metadata_immutable,
)

failure_details_immutable = False

failed_fixture = UniversalStageResult(
    result_id="stage-result-failed",
    workflow_id="workflow-001",
    correlation_id="correlation-001",
    stage_id="article_validation",
    stage_version="v3",
    pipeline_id="website_source_pipeline",
    workflow_type="website_source_pipeline",
    workspace_id="ws-test",
    execution_target="universal_runtime",
    job_id="job-failed",
    job_type="article_validation_population_v3",
    status="failed",
    output={"ok": False},
    result_reference="",
    artifact_references=(),
    started_at="2026-08-15T22:00:00+00:00",
    finished_at="2026-08-15T22:00:30+00:00",
    failure_code="validation_failed",
    failure_message="Validation failed.",
    failure_details={
        "failed_count": 1,
    },
    metadata={},
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
    stage_reference_contract_version=(
        UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION
    ),
)

try:
    failed_fixture.failure_details[
        "illegal"
    ] = True
except Exception:
    failure_details_immutable = True

check(
    "Failure details mapping is immutable",
    failure_details_immutable,
)


# ============================================================================
# 7. Required field enforcement
# ============================================================================

for field_name in REQUIRED_UNIVERSAL_STAGE_RESULT_FIELDS:

    broken = dict(mapping)
    del broken[field_name]

    try:
        UniversalStageResult.from_dict(
            broken
        )
        rejected = False
    except UniversalStageResultContractError:
        rejected = True

    check(
        f"Missing {field_name} is rejected",
        rejected,
    )


# ============================================================================
# 8. Unknown field rejection
# ============================================================================

for illegal_field in (
    "ok",
    "handler_ref",
    "retry_policy",
    "next_stage",
    "queue_state",
    "worker_id",
):

    broken = dict(mapping)
    broken[
        illegal_field
    ] = "illegal"

    try:
        UniversalStageResult.from_dict(
            broken
        )
        rejected = False
    except UniversalStageResultContractError:
        rejected = True

    check(
        f"Unknown authority field {illegal_field} is rejected",
        rejected,
    )


# ============================================================================
# 9. Runtime correlation invariants
# ============================================================================

for field_name in (
    "job_id",
    "job_type",
):

    broken = dict(mapping)
    broken[
        field_name
    ] = ""

    try:
        UniversalStageResult.from_dict(
            broken
        )
        rejected = False
    except UniversalStageResultContractError:
        rejected = True

    check(
        f"Runtime-backed result requires {field_name}",
        rejected,
    )


# ============================================================================
# 10. Coordination-only invariants
# ============================================================================

coordination_result = UniversalStageResult(
    result_id="stage-result-coordination",
    workflow_id="workflow-001",
    correlation_id="correlation-001",
    stage_id="workflow_join",
    stage_version="v1",
    pipeline_id="example_pipeline",
    workflow_type="example_pipeline",
    workspace_id="ws-test",
    execution_target="coordination_only",
    job_id="",
    job_type="",
    status="completed",
    output={
        "joined": True,
    },
    result_reference="",
    artifact_references=(),
    started_at="2026-08-15T22:02:00+00:00",
    finished_at="2026-08-15T22:02:01+00:00",
    failure_code="",
    failure_message="",
    failure_details={},
    metadata={},
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
    stage_reference_contract_version=(
        UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION
    ),
)

check(
    "Coordination-only result constructs",
    coordination_result.completed,
)

for field_name, value in (
    ("job_id", "illegal-job"),
    ("job_type", "illegal-job-type"),
):

    broken = coordination_result.to_dict()
    broken[
        field_name
    ] = value

    try:
        UniversalStageResult.from_dict(
            broken
        )
        rejected = False
    except UniversalStageResultContractError:
        rejected = True

    check(
        f"Coordination-only result rejects {field_name}",
        rejected,
    )


# ============================================================================
# 11. Status coverage
# ============================================================================

skipped_result = UniversalStageResult(
    **{
        **coordination_result.to_dict(),
        "result_id": "stage-result-skipped",
        "status": "skipped",
        "output": {},
    }
)

check(
    "Skipped status constructs correctly",
    skipped_result.skipped,
)

cancelled_result = UniversalStageResult(
    **{
        **coordination_result.to_dict(),
        "result_id": "stage-result-cancelled",
        "status": "cancelled",
        "output": {},
    }
)

check(
    "Cancelled status constructs correctly",
    cancelled_result.cancelled,
)

check(
    "Failed status constructs correctly",
    failed_fixture.failed,
)


# ============================================================================
# 12. Failure invariants
# ============================================================================

broken = failed_fixture.to_dict()
broken["failure_code"] = ""

try:
    UniversalStageResult.from_dict(
        broken
    )
    rejected = False
except UniversalStageResultContractError:
    rejected = True

check(
    "Failed status requires failure_code",
    rejected,
)


broken = failed_fixture.to_dict()
broken["failure_message"] = ""

try:
    UniversalStageResult.from_dict(
        broken
    )
    rejected = False
except UniversalStageResultContractError:
    rejected = True

check(
    "Failed status requires failure_message",
    rejected,
)


broken = result.to_dict()
broken["failure_code"] = "illegal_failure"

try:
    UniversalStageResult.from_dict(
        broken
    )
    rejected = False
except UniversalStageResultContractError:
    rejected = True

check(
    "Completed result rejects failure_code",
    rejected,
)


broken = result.to_dict()
broken["failure_message"] = "Illegal failure"

try:
    UniversalStageResult.from_dict(
        broken
    )
    rejected = False
except UniversalStageResultContractError:
    rejected = True

check(
    "Completed result rejects failure_message",
    rejected,
)


broken = result.to_dict()

broken[
    "failure_details"
] = {
    "illegal": True,
}

try:
    UniversalStageResult.from_dict(
        broken
    )
    rejected = False
except UniversalStageResultContractError:
    rejected = True

check(
    "Completed result rejects failure_details",
    rejected,
)


# ============================================================================
# 13. Timestamp validation
# ============================================================================

broken = result.to_dict()

broken[
    "started_at"
] = "not-a-timestamp"

try:
    UniversalStageResult.from_dict(
        broken
    )
    rejected = False
except UniversalStageResultContractError:
    rejected = True

check(
    "Malformed started_at is rejected",
    rejected,
)


broken = result.to_dict()

broken[
    "finished_at"
] = "not-a-timestamp"

try:
    UniversalStageResult.from_dict(
        broken
    )
    rejected = False
except UniversalStageResultContractError:
    rejected = True

check(
    "Malformed finished_at is rejected",
    rejected,
)


broken = result.to_dict()

broken[
    "started_at"
] = "2026-08-15T22:00:00"

try:
    UniversalStageResult.from_dict(
        broken
    )
    rejected = False
except UniversalStageResultContractError:
    rejected = True

check(
    "Timezone-naive started_at is rejected",
    rejected,
)


broken = result.to_dict()

broken[
    "finished_at"
] = "2026-08-15T21:59:00+00:00"

try:
    UniversalStageResult.from_dict(
        broken
    )
    rejected = False
except UniversalStageResultContractError:
    rejected = True

check(
    "finished_at before started_at is rejected",
    rejected,
)


# ============================================================================
# 14. Type validation
# ============================================================================

broken = result.to_dict()
broken["output"] = []

try:
    UniversalStageResult.from_dict(
        broken
    )
    rejected = False
except UniversalStageResultContractError:
    rejected = True

check(
    "Output must be a mapping",
    rejected,
)


broken = result.to_dict()
broken["metadata"] = []

try:
    UniversalStageResult.from_dict(
        broken
    )
    rejected = False
except UniversalStageResultContractError:
    rejected = True

check(
    "Metadata must be a mapping",
    rejected,
)


broken = result.to_dict()
broken["failure_details"] = []

try:
    UniversalStageResult.from_dict(
        broken
    )
    rejected = False
except UniversalStageResultContractError:
    rejected = True

check(
    "Failure details must be a mapping",
    rejected,
)


broken = result.to_dict()

broken[
    "artifact_references"
] = "artifact://bad"

try:
    UniversalStageResult.from_dict(
        broken
    )
    rejected = False
except UniversalStageResultContractError:
    rejected = True

check(
    "Artifact references must be a collection",
    rejected,
)


# ============================================================================
# 15. Artifact normalization
# ============================================================================

broken = result.to_dict()

broken[
    "artifact_references"
] = [
    "artifact://validation/report.json",
    "artifact://validation/report.json",
]

deduped = UniversalStageResult.from_dict(
    broken
)

check(
    "Duplicate artifact references are normalized",
    deduped.artifact_references
    == (
        "artifact://validation/report.json",
    ),
)


# ============================================================================
# 16. Version protection
# ============================================================================

for field_name, bad_value in (
    (
        "workflow_contract_version",
        "wrong_workflow_contract",
    ),
    (
        "stage_reference_contract_version",
        "wrong_stage_reference_contract",
    ),
    (
        "contract_version",
        "wrong_stage_result_contract",
    ),
):

    broken = result.to_dict()
    broken[
        field_name
    ] = bad_value

    try:
        UniversalStageResult.from_dict(
            broken
        )
        rejected = False
    except UniversalStageResultContractError:
        rejected = True

    check(
        f"Wrong {field_name} is rejected",
        rejected,
    )


# ============================================================================
# 17. Fingerprints
# ============================================================================

identity_1 = result.identity_fingerprint()
identity_2 = rebuilt.identity_fingerprint()

check(
    "Identity fingerprint is stable across reconstruction",
    identity_1 == identity_2,
    identity_1,
)


content_1 = result.content_fingerprint()
content_2 = rebuilt.content_fingerprint()

check(
    "Content fingerprint is stable across reconstruction",
    content_1 == content_2,
    content_1,
)


changed_identity_data = result.to_dict()
changed_identity_data[
    "result_id"
] = "stage-result-different"

changed_identity = (
    UniversalStageResult.from_dict(
        changed_identity_data
    )
)

check(
    "Identity fingerprint changes when identity changes",
    changed_identity.identity_fingerprint()
    != identity_1,
)


changed_content_data = result.to_dict()

changed_content_data[
    "output"
] = {
    "ok": True,
    "processed_count": 11,
}

changed_content = (
    UniversalStageResult.from_dict(
        changed_content_data
    )
)

check(
    "Content fingerprint changes when output changes",
    changed_content.content_fingerprint()
    != content_1,
)


# ============================================================================
# 18. Schema authority
# ============================================================================

schema = dict(
    UniversalStageResult.schema()
)

check(
    "Schema declares status as coordination outcome authority",
    schema.get(
        "coordination_status_authority"
    )
    == "status",
)

check(
    "Schema declares output as business-output authority",
    schema.get(
        "business_output_authority"
    )
    == "output",
)

check(
    "Schema declares exact Workflow Contract dependency",
    schema.get(
        "workflow_contract_version"
    )
    == UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)

check(
    "Schema declares exact Stage Reference dependency",
    schema.get(
        "stage_reference_contract_version"
    )
    == UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION,
)


# ============================================================================
# 19. Architectural purity
# ============================================================================

tree = ast.parse(
    source
)

backend_imports = []

for node in ast.walk(tree):

    if isinstance(
        node,
        ast.Import,
    ):
        for alias in node.names:
            if alias.name.startswith(
                "backend."
            ):
                backend_imports.append(
                    alias.name
                )

    elif isinstance(
        node,
        ast.ImportFrom,
    ):
        module = (
            node.module
            or ""
        )

        if module.startswith(
            "backend."
        ):
            backend_imports.append(
                module
            )


allowed_backend_imports = {
    (
        "backend.server.coordination."
        "universal_workflows.contract"
    ),
    (
        "backend.server.coordination."
        "universal_stages.contract"
    ),
}

check(
    "Only frozen coordination contracts are imported",
    set(
        backend_imports
    ).issubset(
        allowed_backend_imports
    ),
    json.dumps(
        backend_imports
    ),
)


forbidden_import_fragments = (
    "backend.server.runtime",
    "backend.server.jobs",
    "backend.server.workers",
    "backend.server.pipelines",
    "backend.server.routes",
    "fastapi",
    "requests",
    "boto3",
    "sqlalchemy",
)

violating_imports = [
    name
    for name in backend_imports
    if any(
        fragment in name
        for fragment
        in forbidden_import_fragments
    )
]

check(
    "No runtime/job/worker/pipeline execution imports exist",
    not violating_imports,
    json.dumps(
        violating_imports
    ),
)


forbidden_calls = (
    "open(",
    "Path.write",
    "Path.mkdir",
    "Path.unlink",
    "requests.",
    "subprocess.",
    "os.system",
)

violating_calls = [
    marker
    for marker
    in forbidden_calls
    if marker in source
]

check(
    "Stage Result contract performs no I/O or external execution",
    not violating_calls,
    json.dumps(
        violating_calls
    ),
)


forbidden_authority_fields = (
    "retry_policy:",
    "next_stage:",
    "handler_ref:",
    "worker_id:",
    "queue_state:",
    "dependency_graph:",
)

violating_authorities = [
    marker
    for marker
    in forbidden_authority_fields
    if marker in source
]

check(
    "Stage Result does not own runtime or planning authority",
    not violating_authorities,
    json.dumps(
        violating_authorities
    ),
)


# ============================================================================
# 20. SHA256
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
# 21. Final certification
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

lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 1.4 UNIVERSAL STAGE RESULT CONTRACT CERTIFICATION",
    "=" * 82,
    "",
    f"Contract ID: {UNIVERSAL_STAGE_RESULT_CONTRACT_ID}",
    f"Version: {UNIVERSAL_STAGE_RESULT_CONTRACT_VERSION}",
    f"Schema: {UNIVERSAL_STAGE_RESULT_SCHEMA_VERSION}",
    (
        "Workflow Contract: "
        + UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
    (
        "Stage Reference Contract: "
        + UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION
    ),
    (
        "Required fields: "
        + str(
            len(
                REQUIRED_UNIVERSAL_STAGE_RESULT_FIELDS
            )
        )
    ),
    f"Checks: {len(checks)}",
    f"Passed: {passed}",
    f"Failed: {failed}",
    f"SHA256: {sha256}",
    "",
    (
        "STATUS: CERTIFICATION PASSED"
        if failed == 0
        else "STATUS: CERTIFICATION FAILED"
    ),
    "",
]

for name, ok, detail in checks:
    lines.append(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        lines.append(
            f"    {detail}"
        )


REPORT.write_text(
    "\n".join(
        lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 82)
print("CERTIFICATION RESULT")
print("=" * 82)
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

print()
print(
    "REPORT:",
    REPORT,
)

print("=" * 82)

raise SystemExit(
    0
    if failed == 0
    else 1
)
