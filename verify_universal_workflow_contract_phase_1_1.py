from __future__ import annotations

import ast
import hashlib
import importlib
import json
from pathlib import Path

from backend.server.coordination.universal_workflows.contract import (
    UNIVERSAL_WORKFLOW_CONTRACT_ID,
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
    REQUIRED_UNIVERSAL_WORKFLOW_FIELDS,
    TERMINAL_WORKFLOW_STATUSES,
    UniversalWorkflow,
    UniversalWorkflowStatus,
    UniversalWorkflowContractError,
    validate_universal_workflow,
)

TARGET = Path(
    "backend/server/coordination/universal_workflows/contract.py"
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
print("PHASE 1.1 UNIVERSAL WORKFLOW CONTRACT CERTIFICATION")
print("=" * 72)


# --------------------------------------------------------------------------
# 1. File / import
# --------------------------------------------------------------------------

check(
    "Canonical contract file exists",
    TARGET.exists(),
    str(TARGET),
)

source = TARGET.read_text(encoding="utf-8")

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
    module = importlib.import_module(
        "backend.server.coordination.universal_workflows.contract"
    )
    import_ok = True
except Exception as exc:
    module = None
    import_ok = False
    print(repr(exc))

check(
    "Canonical module imports successfully",
    import_ok,
)


# --------------------------------------------------------------------------
# 2. Contract identity
# --------------------------------------------------------------------------

check(
    "Contract ID is canonical",
    UNIVERSAL_WORKFLOW_CONTRACT_ID
    == "urn:linkcraftor:coordination:universal-workflow-contract",
)

check(
    "Contract version is canonical",
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    == "universal_workflow_contract_v1.1.0",
)

check(
    "Required field roster contains 31 fields",
    len(REQUIRED_UNIVERSAL_WORKFLOW_FIELDS) == 31,
    f"count={len(REQUIRED_UNIVERSAL_WORKFLOW_FIELDS)}",
)

check(
    "contract_version belongs to required field roster",
    "contract_version" in REQUIRED_UNIVERSAL_WORKFLOW_FIELDS,
)

check(
    "workflow_type belongs to required field roster",
    "workflow_type" in REQUIRED_UNIVERSAL_WORKFLOW_FIELDS,
)

check(
    "created_at belongs to required field roster",
    "created_at" in REQUIRED_UNIVERSAL_WORKFLOW_FIELDS,
)


# --------------------------------------------------------------------------
# 3. Status model
# --------------------------------------------------------------------------

expected_statuses = {
    "CREATED",
    "READY",
    "RUNNING",
    "WAITING",
    "PAUSED",
    "RECOVERING",
    "COMPLETED",
    "FAILED",
    "CANCELLED",
    "ABORTED",
}

actual_statuses = {
    status.value
    for status in UniversalWorkflowStatus
}

check(
    "Workflow status roster is complete",
    actual_statuses == expected_statuses,
    json.dumps(sorted(actual_statuses)),
)

terminal_values = {
    status.value
    for status in TERMINAL_WORKFLOW_STATUSES
}

check(
    "Terminal workflow statuses are correct",
    terminal_values
    == {
        "COMPLETED",
        "FAILED",
        "CANCELLED",
        "ABORTED",
    },
    json.dumps(sorted(terminal_values)),
)


# --------------------------------------------------------------------------
# 4. Construct canonical workflow
# --------------------------------------------------------------------------

workflow = UniversalWorkflow(
    workflow_id="wf_certification_001",
    workflow_type="linking_target_pipeline",
    workflow_version="linking_target_pipeline_v1",
    workspace_id="ws_certification",
    coordinator_id="linking_target_pipeline_coordinator",
    coordinator_version="v1",
    correlation_id="corr_certification_001",
    parent_workflow_id=None,
    root_workflow_id="wf_certification_001",
    status=UniversalWorkflowStatus.CREATED,
    input_reference="artifact://certification/input",
    context={"domain": "example.com"},
    metadata={"source": "phase_1_1_certification"},
    current_stage=None,
    completed_stages=(),
    pending_stages=(
        "site_sources",
        "url_cleaner",
        "site_pages",
        "live_domain_target_pool",
        "active_target_set",
    ),
    failed_stages=(),
    skipped_stages=(),
    result_reference=None,
    artifact_references=(),
    idempotency_key="phase-1-1-certification-001",
    created_at="2026-08-09T02:35:00Z",
    started_at=None,
    updated_at="2026-08-09T02:35:00Z",
    completed_at=None,
    failed_at=None,
    cancelled_at=None,
    failure_code=None,
    failure_message=None,
    failure_details={},
)

check(
    "Canonical workflow constructs successfully",
    isinstance(workflow, UniversalWorkflow),
)

check(
    "Workflow begins in CREATED state",
    workflow.status == UniversalWorkflowStatus.CREATED,
)

check(
    "Root workflow identity is preserved",
    workflow.root_workflow_id == workflow.workflow_id,
)


# --------------------------------------------------------------------------
# 5. Serialization / reconstruction
# --------------------------------------------------------------------------

mapping = workflow.to_dict()

check(
    "Serialized field roster matches canonical roster",
    tuple(mapping.keys())
    == REQUIRED_UNIVERSAL_WORKFLOW_FIELDS,
)

rebuilt = UniversalWorkflow.from_dict(mapping)

check(
    "Mapping reconstruction is lossless",
    rebuilt == workflow,
)

json_text = workflow.to_canonical_json()
json_rebuilt = UniversalWorkflow.from_json(json_text)

check(
    "JSON reconstruction is lossless",
    json_rebuilt == workflow,
)

check(
    "Canonical JSON is deterministic",
    json_text == workflow.to_canonical_json(),
)

validation = validate_universal_workflow(mapping)

check(
    "Standalone validation accepts canonical workflow",
    validation.is_valid,
    json.dumps(validation.to_dict(), indent=2),
)


# --------------------------------------------------------------------------
# 6. Immutable contract behavior
# --------------------------------------------------------------------------

immutable_ok = False

try:
    workflow.workflow_id = "mutated"
except Exception:
    immutable_ok = True

check(
    "UniversalWorkflow is immutable",
    immutable_ok,
)

context_immutable = False

try:
    workflow.context["illegal"] = True
except Exception:
    context_immutable = True

check(
    "Workflow context is immutable",
    context_immutable,
)


# --------------------------------------------------------------------------
# 7. Required-field enforcement
# --------------------------------------------------------------------------

missing = dict(mapping)
del missing["workflow_type"]

try:
    UniversalWorkflow.from_dict(missing)
    rejected = False
except UniversalWorkflowContractError:
    rejected = True

check(
    "Missing workflow_type is rejected",
    rejected,
)

missing = dict(mapping)
del missing["created_at"]

try:
    UniversalWorkflow.from_dict(missing)
    rejected = False
except UniversalWorkflowContractError:
    rejected = True

check(
    "Missing created_at is rejected",
    rejected,
)

missing = dict(mapping)
del missing["contract_version"]

try:
    UniversalWorkflow.from_dict(missing)
    rejected = False
except UniversalWorkflowContractError:
    rejected = True

check(
    "Missing contract_version is rejected",
    rejected,
)


# --------------------------------------------------------------------------
# 8. Unknown-field protection
# --------------------------------------------------------------------------

bad = dict(mapping)
bad["not_canonical"] = True

try:
    UniversalWorkflow.from_dict(bad)
    rejected = False
except UniversalWorkflowContractError:
    rejected = True

check(
    "Unknown workflow fields are rejected",
    rejected,
)


# --------------------------------------------------------------------------
# 9. Relationship invariants
# --------------------------------------------------------------------------

bad = dict(mapping)
bad["root_workflow_id"] = "wf_wrong_root"

try:
    UniversalWorkflow.from_dict(bad)
    rejected = False
except UniversalWorkflowContractError:
    rejected = True

check(
    "Invalid root workflow relationship is rejected",
    rejected,
)

bad = dict(mapping)
bad["parent_workflow_id"] = workflow.workflow_id

try:
    UniversalWorkflow.from_dict(bad)
    rejected = False
except UniversalWorkflowContractError:
    rejected = True

check(
    "Self-parent workflow relationship is rejected",
    rejected,
)


# --------------------------------------------------------------------------
# 10. Stage-state invariants
# --------------------------------------------------------------------------

bad = dict(mapping)
bad["completed_stages"] = ["site_sources"]
bad["pending_stages"] = [
    "site_sources",
    "url_cleaner",
]

try:
    UniversalWorkflow.from_dict(bad)
    rejected = False
except UniversalWorkflowContractError:
    rejected = True

check(
    "Stage cannot occupy completed and pending simultaneously",
    rejected,
)


# --------------------------------------------------------------------------
# 11. Terminal-state invariants
# --------------------------------------------------------------------------

bad = dict(mapping)
bad["status"] = "COMPLETED"
bad["completed_at"] = None

try:
    UniversalWorkflow.from_dict(bad)
    rejected = False
except UniversalWorkflowContractError:
    rejected = True

check(
    "COMPLETED requires completed_at",
    rejected,
)

bad = dict(mapping)
bad["status"] = "FAILED"
bad["failed_at"] = None
bad["failure_code"] = None

try:
    UniversalWorkflow.from_dict(bad)
    rejected = False
except UniversalWorkflowContractError:
    rejected = True

check(
    "FAILED requires failure timestamp and failure code",
    rejected,
)

bad = dict(mapping)
bad["status"] = "CANCELLED"
bad["cancelled_at"] = None

try:
    UniversalWorkflow.from_dict(bad)
    rejected = False
except UniversalWorkflowContractError:
    rejected = True

check(
    "CANCELLED requires cancelled_at",
    rejected,
)


# --------------------------------------------------------------------------
# 12. Time invariants
# --------------------------------------------------------------------------

bad = dict(mapping)
bad["updated_at"] = "2026-08-08T02:35:00Z"

try:
    UniversalWorkflow.from_dict(bad)
    rejected = False
except UniversalWorkflowContractError:
    rejected = True

check(
    "updated_at cannot precede created_at",
    rejected,
)


# --------------------------------------------------------------------------
# 13. Fingerprints
# --------------------------------------------------------------------------

identity_1 = workflow.identity_fingerprint()
identity_2 = rebuilt.identity_fingerprint()

check(
    "Identity fingerprint is stable across reconstruction",
    identity_1 == identity_2,
    identity_1,
)

content_1 = workflow.content_fingerprint()
content_2 = rebuilt.content_fingerprint()

check(
    "Content fingerprint is stable across reconstruction",
    content_1 == content_2,
    content_1,
)


# --------------------------------------------------------------------------
# 14. Purity / architectural boundaries
# --------------------------------------------------------------------------

tree = ast.parse(source)

imports = []

for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        imports.extend(alias.name for alias in node.names)

    elif isinstance(node, ast.ImportFrom):
        if node.module:
            imports.append(node.module)

forbidden_import_fragments = (
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

violating_imports = [
    name
    for name in imports
    if any(
        fragment in name
        for fragment in forbidden_import_fragments
    )
]

check(
    "Contract has no runtime/pipeline/framework execution imports",
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
# 15. SHA256
# --------------------------------------------------------------------------

sha256 = hashlib.sha256(
    TARGET.read_bytes()
).hexdigest().upper()

print()
print("Canonical SHA256:")
print(sha256)


# --------------------------------------------------------------------------
# Final result
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
