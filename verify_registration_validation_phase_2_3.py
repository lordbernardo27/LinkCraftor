from __future__ import annotations

import ast
import hashlib
import importlib
import json
from pathlib import Path

from backend.server.coordination.registration_validation.validator import (
    REGISTRATION_VALIDATION_VERSION,
    REGISTRATION_VALIDATION_SCHEMA_VERSION,
    VIOLATION_COORDINATOR_TYPE,
    VIOLATION_COORDINATOR_CONTRACT_VERSION,
    VIOLATION_WORKFLOW_NOT_REGISTERED,
    VIOLATION_WORKFLOW_TYPE_MISMATCH,
    VIOLATION_WORKFLOW_VERSION_MISMATCH,
    VIOLATION_WORKFLOW_CONTRACT_MISMATCH,
    VIOLATION_UNIVERSAL_WORKFLOW_CONTRACT,
    RegistrationValidationResult,
    validate_coordinator_registration,
    validate_registered_coordinator,
    validate_registration_registry,
    explain_registration_validation_v2_3,
)

from backend.server.coordination.workflow_registry.registry import (
    WORKFLOW_REGISTRY_VERSION,
    register_workflow_definition,
)

from backend.server.coordination.coordinator_registry.registry import (
    COORDINATOR_REGISTRY_VERSION,
    register_coordinator,
)

from backend.server.coordination.pipeline_coordinators.contract import (
    PIPELINE_COORDINATOR_CONTRACT_VERSION,
    PipelineCoordinatorContract,
    CoordinatorExecutionModel,
    CoordinatorRuntimePolicy,
)

from backend.server.coordination.universal_workflows.contract import (
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)


TARGET = Path(
    "backend/server/coordination/registration_validation/validator.py"
)

REPORT = Path(
    "registration_validation_phase_2_3_certification.txt"
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

    return ok


def build_coordinator(
    *,
    coordinator_id,
    coordinator_version,
    workflow_type,
    workflow_version,
):
    return PipelineCoordinatorContract(
        coordinator_id=coordinator_id,
        coordinator_version=coordinator_version,
        workflow_type=workflow_type,
        workflow_version=workflow_version,
        workflow_contract_version=(
            UNIVERSAL_WORKFLOW_CONTRACT_VERSION
        ),
        entrypoint=(
            "backend.server.pipelines.example:"
            "run_example_pipeline"
        ),
        execution_model=(
            CoordinatorExecutionModel.SYNCHRONOUS
        ),
        runtime_policy=(
            CoordinatorRuntimePolicy.UNIVERSAL_RUNTIME_REQUIRED
        ),
        capabilities=(
            "start",
        ),
        stage_job_types=(
            "example_stage",
        ),
        responsibilities=(
            "coordinate certification workflow",
        ),
        excluded_responsibilities=(
            "execute stage business logic",
        ),
        metadata={
            "certification": True,
        },
    )


print()
print("=" * 82)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 2.3 REGISTRATION VALIDATION CERTIFICATION")
print("=" * 82)


# ============================================================================
# 1. File / syntax / import
# ============================================================================

check(
    "Canonical Registration Validation file exists",
    TARGET.exists(),
    str(TARGET),
)

source = TARGET.read_text(
    encoding="utf-8-sig"
)

try:
    ast.parse(
        source
    )
    syntax_ok = True
except SyntaxError as exc:
    syntax_ok = False
    print(
        exc
    )

check(
    "Python syntax parses successfully",
    syntax_ok,
)

try:
    importlib.import_module(
        "backend.server.coordination.registration_validation.validator"
    )
    import_ok = True
except Exception as exc:
    import_ok = False
    print(
        repr(exc)
    )

check(
    "Registration Validation imports successfully",
    import_ok,
)


# ============================================================================
# 2. Component identity
# ============================================================================

check(
    "Registration Validation version is canonical",
    REGISTRATION_VALIDATION_VERSION
    == "registration_validation_v2.3.0",
)

check(
    "Registration Validation schema is canonical",
    REGISTRATION_VALIDATION_SCHEMA_VERSION
    == "registration_validation_schema_v1",
)


# ============================================================================
# 3. Violation code roster
# ============================================================================

violation_codes = {
    VIOLATION_COORDINATOR_TYPE,
    VIOLATION_COORDINATOR_CONTRACT_VERSION,
    VIOLATION_WORKFLOW_NOT_REGISTERED,
    VIOLATION_WORKFLOW_TYPE_MISMATCH,
    VIOLATION_WORKFLOW_VERSION_MISMATCH,
    VIOLATION_WORKFLOW_CONTRACT_MISMATCH,
    VIOLATION_UNIVERSAL_WORKFLOW_CONTRACT,
}

check(
    "Seven canonical violation codes exist",
    len(
        violation_codes
    )
    == 7,
    json.dumps(
        sorted(
            violation_codes
        )
    ),
)


# ============================================================================
# 4. Canonical workflow
# ============================================================================

workflow = register_workflow_definition(
    workflow_type="phase_2_3_certification_pipeline",
    workflow_version="v1",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
)

check(
    "Canonical workflow registration succeeds",
    workflow.workflow_type
    == "phase_2_3_certification_pipeline",
)

check(
    "Workflow Registry version is frozen expected version",
    WORKFLOW_REGISTRY_VERSION
    == "workflow_registry_v2.1.0",
)


# ============================================================================
# 5. Canonical coordinator
# ============================================================================

coordinator = build_coordinator(
    coordinator_id="phase_2_3_certification_coordinator",
    coordinator_version="v1",
    workflow_type="phase_2_3_certification_pipeline",
    workflow_version="v1",
)

check(
    "Canonical coordinator constructs",
    isinstance(
        coordinator,
        PipelineCoordinatorContract,
    ),
)

check(
    "Coordinator Registry version is frozen expected version",
    COORDINATOR_REGISTRY_VERSION
    == "coordinator_registry_v2.2.0",
)

check(
    "Coordinator Contract version is frozen expected version",
    coordinator.contract_version
    == PIPELINE_COORDINATOR_CONTRACT_VERSION,
)

check(
    "Workflow Contract version is frozen expected version",
    coordinator.workflow_contract_version
    == UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)


# ============================================================================
# 6. Direct valid coordinator validation
# ============================================================================

result = validate_coordinator_registration(
    coordinator
)

check(
    "Direct coordinator validation returns RegistrationValidationResult",
    isinstance(
        result,
        RegistrationValidationResult,
    ),
)

check(
    "Valid coordinator passes",
    result.is_valid is True,
)

check(
    "Valid coordinator executes all seven rules",
    result.checked_rule_count == 7,
)

check(
    "Valid coordinator has no violations",
    result.violations == (),
)

check(
    "Validation result identity matches coordinator",
    (
        result.coordinator_id,
        result.coordinator_version,
    )
    == (
        coordinator.coordinator_id,
        coordinator.coordinator_version,
    ),
)

check(
    "Validation result workflow identity matches coordinator",
    (
        result.workflow_type,
        result.workflow_version,
    )
    == (
        coordinator.workflow_type,
        coordinator.workflow_version,
    ),
)


# ============================================================================
# 7. Result immutability
# ============================================================================

result_immutable = False

try:
    result.is_valid = False
except Exception:
    result_immutable = True

check(
    "RegistrationValidationResult is immutable",
    result_immutable,
)


# ============================================================================
# 8. Invalid object type
# ============================================================================

invalid_object_result = (
    validate_coordinator_registration(
        "not-a-coordinator"
    )
)

check(
    "Invalid coordinator object fails",
    invalid_object_result.is_valid is False,
)

check(
    "Invalid coordinator object stops after rule 1",
    invalid_object_result.checked_rule_count == 1,
)

check(
    "Invalid coordinator object emits canonical violation",
    len(
        invalid_object_result.violations
    )
    == 1
    and invalid_object_result.violations[
        0
    ][
        "code"
    ]
    == VIOLATION_COORDINATOR_TYPE,
)


# ============================================================================
# 9. Orphan coordinator
# ============================================================================

orphan = build_coordinator(
    coordinator_id="phase_2_3_certification_orphan",
    coordinator_version="v1",
    workflow_type="missing_phase_2_3_certification_pipeline",
    workflow_version="v1",
)

orphan_result = (
    validate_coordinator_registration(
        orphan
    )
)

check(
    "Orphan coordinator is invalid",
    orphan_result.is_valid is False,
)

check(
    "Orphan coordinator stops after workflow-existence rule",
    orphan_result.checked_rule_count == 3,
)

check(
    "Orphan coordinator emits workflow_not_registered",
    len(
        orphan_result.violations
    )
    == 1
    and orphan_result.violations[
        0
    ][
        "code"
    ]
    == VIOLATION_WORKFLOW_NOT_REGISTERED,
)


# ============================================================================
# 10. Violation evidence
# ============================================================================

violation = orphan_result.violations[
    0
]

check(
    "Violation evidence contains code",
    violation[
        "code"
    ]
    == VIOLATION_WORKFLOW_NOT_REGISTERED,
)

check(
    "Violation evidence contains field",
    violation[
        "field"
    ]
    == "workflow_type+workflow_version",
)

check(
    "Violation evidence contains expected value",
    violation[
        "expected"
    ]
    == "exact registered workflow",
)

check(
    "Violation evidence contains actual identity",
    violation[
        "actual"
    ]
    == (
        "missing_phase_2_3_certification_pipeline@v1"
    ),
)


violation_immutable = False

try:

    violation[
        "code"
    ] = "mutated"

except Exception:
    violation_immutable = True

check(
    "Violation evidence is immutable",
    violation_immutable,
)


# ============================================================================
# 11. Exact registered coordinator validation
# ============================================================================

register_coordinator(
    coordinator
)

registered_result = (
    validate_registered_coordinator(
        coordinator_id=(
            coordinator.coordinator_id
        ),
        coordinator_version=(
            coordinator.coordinator_version
        ),
    )
)

check(
    "Exact registered coordinator validation succeeds",
    registered_result.is_valid is True,
)


try:

    validate_registered_coordinator(
        coordinator_id="missing_coordinator",
        coordinator_version="v1",
    )

    missing_lookup_rejected = False

except LookupError:
    missing_lookup_rejected = True

check(
    "Missing registered coordinator raises LookupError",
    missing_lookup_rejected,
)


# ============================================================================
# 12. Register orphan for registry-wide test
# ============================================================================

register_coordinator(
    orphan
)

check(
    "Orphan coordinator can exist in registry before validation",
    True,
)


# ============================================================================
# 13. Multiple valid coordinator versions
# ============================================================================

coordinator_v2 = build_coordinator(
    coordinator_id="phase_2_3_certification_coordinator",
    coordinator_version="v2",
    workflow_type="phase_2_3_certification_pipeline",
    workflow_version="v1",
)

register_coordinator(
    coordinator_v2
)

coordinator_v2_result = (
    validate_coordinator_registration(
        coordinator_v2
    )
)

check(
    "Second coordinator version targeting same workflow is valid",
    coordinator_v2_result.is_valid is True,
)


# ============================================================================
# 14. Unbound workflow
# ============================================================================

unbound = register_workflow_definition(
    workflow_type="phase_2_3_certification_unbound",
    workflow_version="v1",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
)

check(
    "Unbound workflow registration succeeds",
    unbound.workflow_type
    == "phase_2_3_certification_unbound",
)


# ============================================================================
# 15. Registry-wide validation
# ============================================================================

report = (
    validate_registration_registry()
)

check(
    "Registry-wide report exposes validation version",
    report[
        "validation_version"
    ]
    == REGISTRATION_VALIDATION_VERSION,
)

check(
    "Registry-wide report exposes schema version",
    report[
        "schema_version"
    ]
    == REGISTRATION_VALIDATION_SCHEMA_VERSION,
)

check(
    "Registry-wide report exposes Workflow Registry version",
    report[
        "workflow_registry_version"
    ]
    == WORKFLOW_REGISTRY_VERSION,
)

check(
    "Registry-wide report exposes Coordinator Registry version",
    report[
        "coordinator_registry_version"
    ]
    == COORDINATOR_REGISTRY_VERSION,
)

check(
    "Registry-wide report exposes Workflow Contract version",
    report[
        "universal_workflow_contract_version"
    ]
    == UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)

check(
    "Registry-wide report exposes Coordinator Contract version",
    report[
        "pipeline_coordinator_contract_version"
    ]
    == PIPELINE_COORDINATOR_CONTRACT_VERSION,
)

check(
    "Registry-wide report detects invalid coordinator",
    report[
        "invalid_coordinator_count"
    ]
    >= 1,
)

check(
    "Registry-wide report counts violations",
    report[
        "violation_count"
    ]
    >= 1,
)

check(
    "Registry-wide validity fails when coordinator registration is invalid",
    report[
        "is_valid"
    ]
    is False,
)


# ============================================================================
# 16. Unbound workflow evidence
# ============================================================================

unbound_keys = {
    (
        item[
            "workflow_type"
        ],
        item[
            "workflow_version"
        ],
    )
    for item
    in report[
        "unbound_workflows"
    ]
}

check(
    "Unbound workflow is reported",
    (
        "phase_2_3_certification_unbound",
        "v1",
    )
    in unbound_keys,
)

check(
    "Unbound workflow is not a Phase 2.3 violation",
    report[
        "unbound_workflows_are_violations"
    ]
    is False,
)


# ============================================================================
# 17. Registry-wide immutability
# ============================================================================

report_immutable = False

try:

    report[
        "is_valid"
    ] = True

except Exception:
    report_immutable = True

check(
    "Registry-wide validation report is immutable",
    report_immutable,
)


# ============================================================================
# 18. Boundary flags
# ============================================================================

check(
    "Validation report declares no persistence",
    report[
        "persistence"
    ]
    is False,
)

check(
    "Validation report declares no version selection",
    report[
        "version_selection"
    ]
    is False,
)

check(
    "Validation report declares no runtime validation",
    report[
        "runtime_validation"
    ]
    is False,
)

check(
    "Validation report declares no dependency validation",
    report[
        "dependency_validation"
    ]
    is False,
)


# ============================================================================
# 19. Architecture declaration
# ============================================================================

explanation = (
    explain_registration_validation_v2_3()
)

check(
    "Architecture declaration identifies Phase 2.3",
    explanation[
        "phase"
    ]
    == "2.3",
)

check(
    "Architecture declaration identifies Registration Validation",
    explanation[
        "component"
    ]
    == "Registration Validation",
)

check(
    "Validation direction is coordinator_to_workflow",
    explanation[
        "validation_direction"
    ]
    == "coordinator_to_workflow",
)


required_owns = (
    "Workflow Registry to Coordinator Registry consistency",
    "exact workflow existence validation",
    "exact workflow identity agreement",
    "Workflow Contract compatibility",
    "Pipeline Coordinator Contract compatibility",
    "deterministic validation results",
    "deterministic registry-wide validation report",
    "validation violations and evidence",
)

for item in required_owns:

    check(
        f"Registration Validation owns: {item}",
        item
        in explanation[
            "owns"
        ],
    )


required_exclusions = (
    "workflow registration",
    "coordinator registration",
    "version selection",
    "latest coordinator selection",
    "default coordinator selection",
    "coordinator activation",
    "coordinator deactivation",
    "stage ordering",
    "dependency graphs",
    "Runtime Registration",
    "runtime handler lookup",
    "runtime job creation",
    "coordinator invocation",
    "workflow execution",
    "lifecycle transitions",
    "persistence",
    "recovery",
)

for item in required_exclusions:

    check(
        f"Registration Validation excludes: {item}",
        item
        in explanation[
            "does_not_own"
        ],
    )


check(
    "Version Management remains Phase 2.4 authority",
    explanation[
        "future_authority"
    ][
        "2.4"
    ]
    == "Version Management",
)

check(
    "Dependency planning remains Phase 4 authority",
    explanation[
        "future_authority"
    ][
        "4.0"
    ]
    == "Dependency & Planning",
)

check(
    "Runtime Integration remains Phase 5 authority",
    explanation[
        "future_authority"
    ][
        "5.0"
    ]
    == "Runtime Integration",
)


# ============================================================================
# 20. Static import boundary
# ============================================================================

tree = ast.parse(
    source
)

backend_imports = []

for node in ast.walk(
    tree
):

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
        "pipeline_coordinators.contract"
    ),
    (
        "backend.server.coordination."
        "workflow_registry.registry"
    ),
    (
        "backend.server.coordination."
        "coordinator_registry.registry"
    ),
}

check(
    "Registration Validation imports only allowed frozen coordination components",
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
    "backend.server.coordination.universal_stages",
    "fastapi",
    "requests",
    "sqlalchemy",
    "boto3",
)

violating_imports = [
    name
    for name
    in backend_imports
    if any(
        fragment in name
        for fragment
        in forbidden_import_fragments
    )
]

check(
    "Registration Validation has no runtime/stage/pipeline execution imports",
    not violating_imports,
    json.dumps(
        violating_imports
    ),
)


# ============================================================================
# 21. Read-only registry boundary
# ============================================================================

check(
    "Validator does not import register_workflow",
    "register_workflow" not in source,
)

check(
    "Validator does not import register_coordinator",
    (
        "register_coordinator"
        not in source
    ),
)


# ============================================================================
# 22. No runtime execution authority
# ============================================================================

forbidden_execution_markers = (
    "create_universal",
    "dispatch(",
    "execute(",
    "run_coordinator(",
    "invoke_coordinator(",
    "ensure_runtime",
    "register_runtime",
    "handler_ref",
    "job_id",
    "worker_id",
)

violating_execution = [
    marker
    for marker
    in forbidden_execution_markers
    if marker in source
]

check(
    "Registration Validation performs no runtime/coordinator execution",
    not violating_execution,
    json.dumps(
        violating_execution
    ),
)


# ============================================================================
# 23. No persistence/external I/O
# ============================================================================

forbidden_io_markers = (
    "open(",
    ".write_text(",
    ".write_bytes(",
    ".mkdir(",
    ".unlink(",
    "json.dump(",
    "pickle.",
    "sqlite",
    "requests.",
    "boto3.",
)

violating_io = [
    marker
    for marker
    in forbidden_io_markers
    if marker in source
]

check(
    "Registration Validation performs no persistence or external I/O",
    not violating_io,
    json.dumps(
        violating_io
    ),
)


# ============================================================================
# 24. No Version Management authority
# ============================================================================

check(
    "Validator exposes no latest coordinator resolver",
    "latest_coordinator" not in source
    and "resolve_latest" not in source
    and "get_latest" not in source,
)

check(
    "Validator exposes no default coordinator resolver",
    "default_coordinator" not in source,
)

check(
    "Validator exposes no activation authority",
    "activate_coordinator(" not in source
    and "deactivate_coordinator(" not in source,
)


# ============================================================================
# 25. Frozen upstream hash verification
# ============================================================================

WORKFLOW_REGISTRY_PATH = Path(
    "backend/server/coordination/workflow_registry/registry.py"
)

COORDINATOR_REGISTRY_PATH = Path(
    "backend/server/coordination/coordinator_registry/registry.py"
)

workflow_registry_sha = hashlib.sha256(
    WORKFLOW_REGISTRY_PATH.read_bytes()
).hexdigest().upper()

coordinator_registry_sha = hashlib.sha256(
    COORDINATOR_REGISTRY_PATH.read_bytes()
).hexdigest().upper()

check(
    "Frozen Phase 2.1 Workflow Registry hash unchanged",
    workflow_registry_sha
    == (
        "34786F74443BAC9049F3CD805CBF8BDB"
        "6275C6EF05B94C9BF42579E114CA4564"
    ),
    workflow_registry_sha,
)

check(
    "Frozen Phase 2.2 Coordinator Registry hash unchanged",
    coordinator_registry_sha
    == (
        "C9E324DF0C4D5AEA8D1D0C91D8FB3A3"
        "B479BB9A0830B0C4494186C01C298F071"
    ),
    coordinator_registry_sha,
)


# ============================================================================
# 26. Canonical SHA256
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
# 27. Final result
# ============================================================================

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
    "PHASE 2.3 REGISTRATION VALIDATION CERTIFICATION",
    "=" * 82,
    "",
    (
        "Validation Version: "
        + REGISTRATION_VALIDATION_VERSION
    ),
    (
        "Validation Schema: "
        + REGISTRATION_VALIDATION_SCHEMA_VERSION
    ),
    (
        "Workflow Registry: "
        + WORKFLOW_REGISTRY_VERSION
    ),
    (
        "Coordinator Registry: "
        + COORDINATOR_REGISTRY_VERSION
    ),
    (
        "Universal Workflow Contract: "
        + UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
    (
        "Pipeline Coordinator Contract: "
        + PIPELINE_COORDINATOR_CONTRACT_VERSION
    ),
    "Validation Direction: coordinator_to_workflow",
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


for (
    name,
    ok,
    detail,
) in checks:

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

print()

print(
    "STATUS: CERTIFICATION PASSED"
    if failed == 0
    else "STATUS: CERTIFICATION FAILED"
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
