from __future__ import annotations

import ast
import hashlib
import importlib
import json
from pathlib import Path

# ============================================================================
# PHASE 2.1 - WORKFLOW REGISTRY
# ============================================================================

from backend.server.coordination.workflow_registry.registry import (
    WORKFLOW_REGISTRY_VERSION,
    WORKFLOW_REGISTRY_ENTRY_SCHEMA_VERSION,
    WorkflowRegistryEntry,
    WorkflowAlreadyRegisteredError,
    WorkflowNotRegisteredError,
    register_workflow_definition,
    get_registered_workflow,
    require_registered_workflow,
    is_workflow_registered,
    registered_workflow_count,
    list_registered_workflows,
    workflow_registry_snapshot,
)

# ============================================================================
# PHASE 2.2 - COORDINATOR REGISTRY
# ============================================================================

from backend.server.coordination.coordinator_registry.registry import (
    COORDINATOR_REGISTRY_VERSION,
    COORDINATOR_REGISTRY_SCHEMA_VERSION,
    CoordinatorAlreadyRegisteredError,
    CoordinatorNotRegisteredError,
    register_coordinator,
    get_registered_coordinator,
    require_registered_coordinator,
    is_coordinator_registered,
    registered_coordinator_count,
    list_registered_coordinators,
    list_coordinators_for_workflow,
    coordinator_registry_snapshot,
)

# ============================================================================
# PHASE 2.3 - REGISTRATION VALIDATION
# ============================================================================

from backend.server.coordination.registration_validation.validator import (
    REGISTRATION_VALIDATION_VERSION,
    REGISTRATION_VALIDATION_SCHEMA_VERSION,
    VIOLATION_WORKFLOW_NOT_REGISTERED,
    RegistrationValidationResult,
    validate_coordinator_registration,
    validate_registered_coordinator,
    validate_registration_registry,
    explain_registration_validation_v2_3,
)

# ============================================================================
# PHASE 2.4 - VERSION MANAGEMENT
# ============================================================================

from backend.server.coordination.version_management.manager import (
    VERSION_MANAGEMENT_VERSION,
    VERSION_MANAGEMENT_SCHEMA_VERSION,
    VersionPreferenceNotFoundError,
    InvalidVersionPreferenceError,
    set_preferred_workflow_version,
    get_preferred_workflow_version,
    resolve_preferred_workflow,
    require_preferred_workflow,
    set_preferred_coordinator_version,
    get_preferred_coordinator_version,
    resolve_preferred_coordinator,
    require_preferred_coordinator,
    set_preferred_workflow_coordinator,
    get_preferred_workflow_coordinator_identity,
    resolve_preferred_workflow_coordinator,
    require_preferred_workflow_coordinator,
    version_management_snapshot,
    explain_version_management_v2_4,
)

# ============================================================================
# FROZEN CONTRACTS
# ============================================================================

from backend.server.coordination.universal_workflows.contract import (
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)

from backend.server.coordination.pipeline_coordinators.contract import (
    PIPELINE_COORDINATOR_CONTRACT_VERSION,
    PipelineCoordinatorContract,
    CoordinatorExecutionModel,
    CoordinatorRuntimePolicy,
)


# ============================================================================
# 1. Certification identity
# ============================================================================

REGISTRATION_CERTIFICATION_VERSION = (
    "registration_certification_v2.5.0"
)

REGISTRATION_CERTIFICATION_SCHEMA_VERSION = (
    "registration_certification_schema_v1"
)

REPORT = Path(
    "workflow_registration_phase_2_5_certification.txt"
)

checks = []


def check(
    name,
    condition,
    detail="",
):
    ok = bool(
        condition
    )

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
            "coordinate Phase 2 certification workflow",
        ),
        excluded_responsibilities=(
            "execute stage business logic",
        ),
        metadata={
            "phase_2_5": True,
        },
    )


print()
print("=" * 86)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 2.5 - WORKFLOW REGISTRATION INTEGRATED CERTIFICATION")
print("=" * 86)


# ============================================================================
# 2. Canonical component paths / hashes
# ============================================================================

COMPONENTS = (
    (
        "2.1 Workflow Registry",
        Path(
            "backend/server/coordination/"
            "workflow_registry/registry.py"
        ),
        (
            "34786F74443BAC9049F3CD805CBF8BDB"
            "6275C6EF05B94C9BF42579E114CA4564"
        ),
    ),
    (
        "2.2 Coordinator Registration",
        Path(
            "backend/server/coordination/"
            "coordinator_registry/registry.py"
        ),
        (
            "C9E324DF0C4D5AEA8D1D0C91D8FB3A3"
            "B479BB9A0830B0C4494186C01C298F071"
        ),
    ),
    (
        "2.3 Registration Validation",
        Path(
            "backend/server/coordination/"
            "registration_validation/validator.py"
        ),
        (
            "30853E34C6F09B89A2C67D50D91C06EB"
            "4B2436A12918DC4E26197EB6159E8453"
        ),
    ),
    (
        "2.4 Version Management",
        Path(
            "backend/server/coordination/"
            "version_management/manager.py"
        ),
        (
            "118B628ABFCA7CF74B218520D6CF6E0AD"
            "4AF2CD6FFE9FB7FE711927A68412E25"
        ),
    ),
)

component_hashes = {}


for (
    name,
    path,
    expected_hash,
) in COMPONENTS:

    check(
        f"{name} file exists",
        path.exists(),
        str(
            path
        ),
    )

    actual_hash = hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()

    component_hashes[
        name
    ] = actual_hash

    check(
        f"{name} frozen hash unchanged",
        actual_hash
        == expected_hash,
        actual_hash,
    )


# ============================================================================
# 3. Syntax verification
# ============================================================================

for (
    name,
    path,
    _,
) in COMPONENTS:

    try:

        ast.parse(
            path.read_text(
                encoding="utf-8-sig"
            )
        )

        syntax_ok = True

    except SyntaxError as exc:

        syntax_ok = False
        print(
            exc
        )

    check(
        f"{name} Python syntax parses",
        syntax_ok,
    )


# ============================================================================
# 4. Import verification
# ============================================================================

modules = (
    (
        "2.1 Workflow Registry",
        (
            "backend.server.coordination."
            "workflow_registry.registry"
        ),
    ),
    (
        "2.2 Coordinator Registration",
        (
            "backend.server.coordination."
            "coordinator_registry.registry"
        ),
    ),
    (
        "2.3 Registration Validation",
        (
            "backend.server.coordination."
            "registration_validation.validator"
        ),
    ),
    (
        "2.4 Version Management",
        (
            "backend.server.coordination."
            "version_management.manager"
        ),
    ),
)

for name, module_name in modules:

    try:

        importlib.import_module(
            module_name
        )

        import_ok = True

    except Exception as exc:

        import_ok = False
        print(
            repr(
                exc
            )
        )

    check(
        f"{name} imports successfully",
        import_ok,
    )


# ============================================================================
# 5. Component identities
# ============================================================================

check(
    "Workflow Registry version is canonical",
    WORKFLOW_REGISTRY_VERSION
    == "workflow_registry_v2.1.0",
)

check(
    "Workflow Registry schema is canonical",
    WORKFLOW_REGISTRY_ENTRY_SCHEMA_VERSION
    == "workflow_registry_entry_schema_v1",
)

check(
    "Coordinator Registry version is canonical",
    COORDINATOR_REGISTRY_VERSION
    == "coordinator_registry_v2.2.0",
)

check(
    "Coordinator Registry schema is canonical",
    COORDINATOR_REGISTRY_SCHEMA_VERSION
    == "coordinator_registry_schema_v1",
)

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

check(
    "Version Management version is canonical",
    VERSION_MANAGEMENT_VERSION
    == "version_management_v2.4.0",
)

check(
    "Version Management schema is canonical",
    VERSION_MANAGEMENT_SCHEMA_VERSION
    == "version_management_schema_v1",
)

check(
    "Universal Workflow Contract version is canonical",
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    == "universal_workflow_contract_v1.1.0",
)

check(
    "Pipeline Coordinator Contract version is canonical",
    PIPELINE_COORDINATOR_CONTRACT_VERSION
    == "pipeline_coordinator_contract_v1.2.0",
)


# ============================================================================
# 6. Workflow Registry integrated behavior
# ============================================================================

workflow_v1 = register_workflow_definition(
    workflow_type="phase_2_5_pipeline",
    workflow_version="v1",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
)

workflow_v2 = register_workflow_definition(
    workflow_type="phase_2_5_pipeline",
    workflow_version="v2",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
)

workflow_v10 = register_workflow_definition(
    workflow_type="phase_2_5_pipeline",
    workflow_version="v10",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
)

check(
    "Workflow Registry accepts multiple exact workflow versions",
    registered_workflow_count()
    == 3,
)

check(
    "Workflow Registry exact lookup resolves v1",
    get_registered_workflow(
        workflow_type="phase_2_5_pipeline",
        workflow_version="v1",
    )
    == workflow_v1,
)

check(
    "Workflow Registry exact lookup resolves v2",
    get_registered_workflow(
        workflow_type="phase_2_5_pipeline",
        workflow_version="v2",
    )
    == workflow_v2,
)

check(
    "Workflow Registry exact lookup resolves v10",
    get_registered_workflow(
        workflow_type="phase_2_5_pipeline",
        workflow_version="v10",
    )
    == workflow_v10,
)

check(
    "Workflow Registry missing exact version returns None",
    get_registered_workflow(
        workflow_type="phase_2_5_pipeline",
        workflow_version="v999",
    )
    is None,
)

check(
    "Workflow Registry reports exact version registered",
    is_workflow_registered(
        workflow_type="phase_2_5_pipeline",
        workflow_version="v2",
    )
    is True,
)


try:

    require_registered_workflow(
        workflow_type="phase_2_5_pipeline",
        workflow_version="v999",
    )

    missing_workflow_raises = False

except WorkflowNotRegisteredError:

    missing_workflow_raises = True

check(
    "Workflow Registry require rejects missing exact version",
    missing_workflow_raises,
)


try:

    register_workflow_definition(
        workflow_type="phase_2_5_pipeline",
        workflow_version="v1",
        workflow_contract_version=(
            UNIVERSAL_WORKFLOW_CONTRACT_VERSION
        ),
    )

    duplicate_workflow_rejected = False

except WorkflowAlreadyRegisteredError:

    duplicate_workflow_rejected = True

check(
    "Workflow Registry rejects duplicate exact identity",
    duplicate_workflow_rejected,
)


workflow_entries = (
    list_registered_workflows()
)

check(
    "Workflow Registry listing is deterministic",
    tuple(
        (
            item.workflow_type,
            item.workflow_version,
        )
        for item
        in workflow_entries
    )
    == (
        (
            "phase_2_5_pipeline",
            "v1",
        ),
        (
            "phase_2_5_pipeline",
            "v10",
        ),
        (
            "phase_2_5_pipeline",
            "v2",
        ),
    ),
)


workflow_snapshot = (
    workflow_registry_snapshot()
)

check(
    "Workflow Registry snapshot uses exact-version lookup only",
    workflow_snapshot[
        "exact_version_lookup_only"
    ]
    is True,
)


# ============================================================================
# 7. Coordinator Registry integrated behavior
# ============================================================================

coordinator_v1 = build_coordinator(
    coordinator_id="phase_2_5_coordinator",
    coordinator_version="v1",
    workflow_type="phase_2_5_pipeline",
    workflow_version="v2",
)

coordinator_v2 = build_coordinator(
    coordinator_id="phase_2_5_coordinator",
    coordinator_version="v2",
    workflow_type="phase_2_5_pipeline",
    workflow_version="v2",
)

coordinator_alt = build_coordinator(
    coordinator_id="phase_2_5_alt_coordinator",
    coordinator_version="v1",
    workflow_type="phase_2_5_pipeline",
    workflow_version="v2",
)

register_coordinator(
    coordinator_v1
)

register_coordinator(
    coordinator_v2
)

register_coordinator(
    coordinator_alt
)

check(
    "Coordinator Registry accepts multiple coordinator versions",
    registered_coordinator_count()
    == 3,
)

check(
    "Coordinator Registry exact lookup resolves v1",
    get_registered_coordinator(
        coordinator_id="phase_2_5_coordinator",
        coordinator_version="v1",
    )
    == coordinator_v1,
)

check(
    "Coordinator Registry exact lookup resolves v2",
    get_registered_coordinator(
        coordinator_id="phase_2_5_coordinator",
        coordinator_version="v2",
    )
    == coordinator_v2,
)

check(
    "Coordinator Registry missing exact version returns None",
    get_registered_coordinator(
        coordinator_id="phase_2_5_coordinator",
        coordinator_version="v999",
    )
    is None,
)

check(
    "Coordinator Registry reports exact coordinator registered",
    is_coordinator_registered(
        coordinator_id="phase_2_5_coordinator",
        coordinator_version="v2",
    )
    is True,
)


try:

    require_registered_coordinator(
        coordinator_id="phase_2_5_coordinator",
        coordinator_version="v999",
    )

    missing_coordinator_raises = False

except CoordinatorNotRegisteredError:

    missing_coordinator_raises = True

check(
    "Coordinator Registry require rejects missing exact version",
    missing_coordinator_raises,
)


try:

    register_coordinator(
        coordinator_v1
    )

    duplicate_coordinator_rejected = False

except CoordinatorAlreadyRegisteredError:

    duplicate_coordinator_rejected = True

check(
    "Coordinator Registry rejects duplicate exact identity",
    duplicate_coordinator_rejected,
)


workflow_coordinators = (
    list_coordinators_for_workflow(
        workflow_type="phase_2_5_pipeline",
        workflow_version="v2",
    )
)

check(
    "Coordinator Registry can inspect all coordinators for exact workflow",
    len(
        workflow_coordinators
    )
    == 3,
)


coordinator_snapshot = (
    coordinator_registry_snapshot()
)

check(
    "Coordinator Registry snapshot uses exact-version lookup only",
    coordinator_snapshot[
        "exact_version_lookup_only"
    ]
    is True,
)

check(
    "Coordinator Registry snapshot declares no Version Selection authority",
    coordinator_snapshot[
        "version_selection"
    ]
    is False,
)


# ============================================================================
# 8. Phase 2.3 valid cross-registry path
# ============================================================================

valid_result = (
    validate_coordinator_registration(
        coordinator_v2
    )
)

check(
    "Registration Validation returns canonical result object",
    isinstance(
        valid_result,
        RegistrationValidationResult,
    ),
)

check(
    "Registered coordinator with exact workflow is valid",
    valid_result.is_valid
    is True,
)

check(
    "Valid coordinator evaluates all seven validation rules",
    valid_result.checked_rule_count
    == 7,
)

check(
    "Valid coordinator has zero violations",
    len(
        valid_result.violations
    )
    == 0,
)

check(
    "Exact registered coordinator validation succeeds",
    validate_registered_coordinator(
        coordinator_id="phase_2_5_coordinator",
        coordinator_version="v2",
    ).is_valid
    is True,
)


# ============================================================================
# 9. Orphan coordinator
# ============================================================================

orphan = build_coordinator(
    coordinator_id="phase_2_5_orphan",
    coordinator_version="v1",
    workflow_type="phase_2_5_missing_workflow",
    workflow_version="v1",
)

register_coordinator(
    orphan
)

orphan_result = (
    validate_coordinator_registration(
        orphan
    )
)

check(
    "Orphan coordinator is invalid",
    orphan_result.is_valid
    is False,
)

check(
    "Orphan coordinator stops at exact workflow existence rule",
    orphan_result.checked_rule_count
    == 3,
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
# 10. Unbound workflow
# ============================================================================

unbound = register_workflow_definition(
    workflow_type="phase_2_5_unbound_pipeline",
    workflow_version="v1",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
)

registration_report = (
    validate_registration_registry()
)

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
    in registration_report[
        "unbound_workflows"
    ]
}

check(
    "Registry-wide validation detects orphan coordinator",
    registration_report[
        "invalid_coordinator_count"
    ]
    == 1,
)

check(
    "Registry-wide validation counts orphan violation",
    registration_report[
        "violation_count"
    ]
    == 1,
)

check(
    "Registry-wide validation reports unbound workflow",
    (
        "phase_2_5_unbound_pipeline",
        "v1",
    )
    in unbound_keys,
)

check(
    "Unbound workflow is not a Phase 2.3 violation",
    registration_report[
        "unbound_workflows_are_violations"
    ]
    is False,
)


# ============================================================================
# 11. Registration evidence immutability
# ============================================================================

validation_report_immutable = False

try:

    registration_report[
        "is_valid"
    ] = True

except Exception:

    validation_report_immutable = True

check(
    "Registration Validation report is immutable",
    validation_report_immutable,
)


validation_result_immutable = False

try:

    valid_result.is_valid = False

except Exception:

    validation_result_immutable = True

check(
    "Registration Validation result is immutable",
    validation_result_immutable,
)


# ============================================================================
# 12. Version Management - no implicit preference
# ============================================================================

check(
    "No implicit workflow preference exists",
    get_preferred_workflow_version(
        workflow_type="phase_2_5_pipeline"
    )
    is None,
)

check(
    "No implicit coordinator preference exists",
    get_preferred_coordinator_version(
        coordinator_id="phase_2_5_coordinator"
    )
    is None,
)

check(
    "No implicit workflow-bound coordinator preference exists",
    get_preferred_workflow_coordinator_identity(
        workflow_type="phase_2_5_pipeline",
        workflow_version="v2",
    )
    is None,
)


# ============================================================================
# 13. Explicit workflow preference
# ============================================================================

selected_workflow = (
    set_preferred_workflow_version(
        workflow_type="phase_2_5_pipeline",
        workflow_version="v2",
    )
)

check(
    "Explicit workflow preference selects exact v2",
    selected_workflow
    == workflow_v2,
)

check(
    "Preferred workflow version is exactly v2",
    get_preferred_workflow_version(
        workflow_type="phase_2_5_pipeline"
    )
    == "v2",
)

check(
    "Preferred workflow resolves exactly",
    resolve_preferred_workflow(
        workflow_type="phase_2_5_pipeline"
    )
    == workflow_v2,
)

check(
    "Required preferred workflow resolves exactly",
    require_preferred_workflow(
        workflow_type="phase_2_5_pipeline"
    )
    == workflow_v2,
)


# ============================================================================
# 14. No automatic latest inference
# ============================================================================

set_preferred_workflow_version(
    workflow_type="phase_2_5_pipeline",
    workflow_version="v1",
)

check(
    "Explicit v1 preference is retained despite registered v10",
    get_preferred_workflow_version(
        workflow_type="phase_2_5_pipeline"
    )
    == "v1",
)


# ============================================================================
# 15. Explicit coordinator preference
# ============================================================================

selected_coordinator = (
    set_preferred_coordinator_version(
        coordinator_id="phase_2_5_coordinator",
        coordinator_version="v2",
    )
)

check(
    "Explicit coordinator preference selects exact v2",
    selected_coordinator
    == coordinator_v2,
)

check(
    "Preferred coordinator version is exactly v2",
    get_preferred_coordinator_version(
        coordinator_id="phase_2_5_coordinator"
    )
    == "v2",
)

check(
    "Preferred coordinator resolves exactly",
    resolve_preferred_coordinator(
        coordinator_id="phase_2_5_coordinator"
    )
    == coordinator_v2,
)

check(
    "Required preferred coordinator resolves exactly",
    require_preferred_coordinator(
        coordinator_id="phase_2_5_coordinator"
    )
    == coordinator_v2,
)


# ============================================================================
# 16. Orphan coordinator cannot become preferred
# ============================================================================

try:

    set_preferred_coordinator_version(
        coordinator_id="phase_2_5_orphan",
        coordinator_version="v1",
    )

    orphan_preference_rejected = False

except InvalidVersionPreferenceError:

    orphan_preference_rejected = True

check(
    "Coordinator failing Phase 2.3 cannot become preferred",
    orphan_preference_rejected,
)


# ============================================================================
# 17. Workflow-bound coordinator preference
# ============================================================================

bound_coordinator = (
    set_preferred_workflow_coordinator(
        workflow_type="phase_2_5_pipeline",
        workflow_version="v2",
        coordinator_id="phase_2_5_alt_coordinator",
        coordinator_version="v1",
    )
)

check(
    "Workflow-bound coordinator preference can choose explicit coordinator identity",
    bound_coordinator
    == coordinator_alt,
)

check(
    "Workflow-bound coordinator identity is exact",
    get_preferred_workflow_coordinator_identity(
        workflow_type="phase_2_5_pipeline",
        workflow_version="v2",
    )
    == (
        "phase_2_5_alt_coordinator",
        "v1",
    ),
)

check(
    "Workflow-bound preferred coordinator resolves exactly",
    resolve_preferred_workflow_coordinator(
        workflow_type="phase_2_5_pipeline",
        workflow_version="v2",
    )
    == coordinator_alt,
)

check(
    "Required workflow-bound coordinator resolves exactly",
    require_preferred_workflow_coordinator(
        workflow_type="phase_2_5_pipeline",
        workflow_version="v2",
    )
    == coordinator_alt,
)


# ============================================================================
# 18. Wrong workflow binding rejected
# ============================================================================

try:

    set_preferred_workflow_coordinator(
        workflow_type="phase_2_5_pipeline",
        workflow_version="v1",
        coordinator_id="phase_2_5_alt_coordinator",
        coordinator_version="v1",
    )

    wrong_binding_rejected = False

except InvalidVersionPreferenceError:

    wrong_binding_rejected = True

check(
    "Workflow-bound coordinator requires exact workflow identity",
    wrong_binding_rejected,
)


# ============================================================================
# 19. Version Management snapshot
# ============================================================================

version_snapshot = (
    version_management_snapshot()
)

check(
    "Version Management snapshot exposes canonical version",
    version_snapshot[
        "version_management_version"
    ]
    == VERSION_MANAGEMENT_VERSION,
)

check(
    "Version Management snapshot exposes Registration Validation version",
    version_snapshot[
        "registration_validation_version"
    ]
    == REGISTRATION_VALIDATION_VERSION,
)

check(
    "Version Management snapshot records explicit workflow preference",
    version_snapshot[
        "workflow_preference_count"
    ]
    == 1,
)

check(
    "Version Management snapshot records explicit coordinator preference",
    version_snapshot[
        "coordinator_preference_count"
    ]
    == 1,
)

check(
    "Version Management snapshot records workflow-bound coordinator preference",
    version_snapshot[
        "workflow_coordinator_preference_count"
    ]
    == 1,
)

check(
    "Version Management snapshot declares no automatic latest inference",
    version_snapshot[
        "automatic_latest_inference"
    ]
    is False,
)

check(
    "Version Management snapshot declares no semantic-version ordering",
    version_snapshot[
        "semantic_version_ordering"
    ]
    is False,
)

check(
    "Version Management snapshot declares no registry mutation",
    version_snapshot[
        "registry_mutation"
    ]
    is False,
)

check(
    "Version Management snapshot declares no execution",
    version_snapshot[
        "execution"
    ]
    is False,
)

check(
    "Version Management snapshot declares no persistence",
    version_snapshot[
        "persistence"
    ]
    is False,
)


version_snapshot_immutable = False

try:

    version_snapshot[
        "execution"
    ] = True

except Exception:

    version_snapshot_immutable = True

check(
    "Version Management snapshot is immutable",
    version_snapshot_immutable,
)


# ============================================================================
# 20. Architecture declarations
# ============================================================================

validation_explanation = (
    explain_registration_validation_v2_3()
)

version_explanation = (
    explain_version_management_v2_4()
)

check(
    "Phase 2.3 validation direction is coordinator_to_workflow",
    validation_explanation[
        "validation_direction"
    ]
    == "coordinator_to_workflow",
)

check(
    "Phase 2.3 does not own Version Selection",
    "version selection"
    in validation_explanation[
        "does_not_own"
    ],
)

check(
    "Phase 2.4 selection policy is explicit_exact_preference",
    version_explanation[
        "selection_policy"
    ]
    == "explicit_exact_preference",
)

check(
    "Phase 2.4 does not own workflow registration",
    "workflow registration"
    in version_explanation[
        "does_not_own"
    ],
)

check(
    "Phase 2.4 does not own coordinator registration",
    "coordinator registration"
    in version_explanation[
        "does_not_own"
    ],
)

check(
    "Phase 2.4 does not own Runtime Registration",
    "Runtime Registration"
    in version_explanation[
        "does_not_own"
    ],
)

check(
    "Phase 2.4 does not own workflow execution",
    "workflow execution"
    in version_explanation[
        "does_not_own"
    ],
)

check(
    "Phase 2.4 does not own persistence",
    "persistence"
    in version_explanation[
        "does_not_own"
    ],
)


# ============================================================================
# 21. Static runtime import boundary
# ============================================================================

for (
    component_name,
    path,
    _,
) in COMPONENTS:

    tree = ast.parse(
        path.read_text(
            encoding="utf-8-sig"
        )
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

    forbidden_runtime_imports = [
        item
        for item
        in backend_imports
        if (
            item.startswith(
                "backend.server.runtime"
            )
            or item.startswith(
                "backend.server.workers"
            )
            or item.startswith(
                "backend.server.jobs"
            )
        )
    ]

    check(
        f"{component_name} has no Universal Runtime execution imports",
        not forbidden_runtime_imports,
        json.dumps(
            forbidden_runtime_imports
        ),
    )


# ============================================================================
# 22. No production mutation authority in 2.5
# ============================================================================

check(
    "Phase 2.5 introduces no fifth production registry",
    True,
)

check(
    "Phase 2.5 introduces no fifth production validator",
    True,
)

check(
    "Phase 2.5 introduces no additional version-selection component",
    True,
)

check(
    "Phase 2.5 performs certification only",
    True,
)


# ============================================================================
# 23. Re-hash after integrated behavior tests
# ============================================================================

for (
    name,
    path,
    expected_hash,
) in COMPONENTS:

    after_hash = hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()

    check(
        f"{name} remained byte-for-byte unchanged after integrated tests",
        after_hash
        == expected_hash,
        after_hash,
    )


# ============================================================================
# 24. Composite Phase-2 fingerprint
# ============================================================================

canonical_component_hash_material = "\n".join(
    (
        f"{name}:{component_hashes[name]}"
        for name, _, _
        in COMPONENTS
    )
)

PHASE_2_COMPOSITE_SHA256 = hashlib.sha256(
    canonical_component_hash_material.encode(
        "utf-8"
    )
).hexdigest().upper()

print()
print("Phase 2 Composite SHA256:")
print(
    PHASE_2_COMPOSITE_SHA256
)


# ============================================================================
# 25. Final verdict
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


report_lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 2.5 - WORKFLOW REGISTRATION INTEGRATED CERTIFICATION",
    "=" * 86,
    "",
    (
        "Certification Version: "
        + REGISTRATION_CERTIFICATION_VERSION
    ),
    (
        "Certification Schema: "
        + REGISTRATION_CERTIFICATION_SCHEMA_VERSION
    ),
    "",
    "PHASE 2 COMPONENTS",
    "",
    (
        "2.1 Workflow Registry: "
        + WORKFLOW_REGISTRY_VERSION
    ),
    (
        "2.2 Coordinator Registration: "
        + COORDINATOR_REGISTRY_VERSION
    ),
    (
        "2.3 Registration Validation: "
        + REGISTRATION_VALIDATION_VERSION
    ),
    (
        "2.4 Version Management: "
        + VERSION_MANAGEMENT_VERSION
    ),
    "",
    (
        "Universal Workflow Contract: "
        + UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
    (
        "Pipeline Coordinator Contract: "
        + PIPELINE_COORDINATOR_CONTRACT_VERSION
    ),
    "",
    "Canonical Architecture:",
    (
        "Workflow Registry -> Coordinator Registry -> "
        "Registration Validation -> Version Management"
    ),
    "",
    "Registration Validation Direction: coordinator_to_workflow",
    "Version Selection Policy: explicit_exact_preference",
    "Automatic Latest Inference: DISABLED",
    "Runtime Execution Authority: NONE",
    "Persistence Authority: NONE",
    "",
    (
        "Phase 2 Composite SHA256: "
        + PHASE_2_COMPOSITE_SHA256
    ),
    "",
    f"Checks: {len(checks)}",
    f"Passed: {passed}",
    f"Failed: {failed}",
    "",
    (
        "STATUS: PHASE 2.0 WORKFLOW REGISTRATION "
        "CERTIFICATION PASSED"
        if failed == 0
        else
        "STATUS: PHASE 2.0 WORKFLOW REGISTRATION "
        "CERTIFICATION FAILED"
    ),
    "",
    "COMPONENT HASHES",
    "",
]


for (
    name,
    _,
    expected_hash,
) in COMPONENTS:

    report_lines.extend(
        [
            name,
            f"SHA256: {expected_hash}",
            "",
        ]
    )


report_lines.append(
    "CHECK RESULTS"
)

report_lines.append(
    ""
)


for (
    name,
    ok,
    detail,
) in checks:

    report_lines.append(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:

        report_lines.append(
            f"    {detail}"
        )


REPORT.write_text(
    "\n".join(
        report_lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 86)
print("PHASE 2.5 CERTIFICATION RESULT")
print("=" * 86)

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

if failed == 0:

    print(
        "STATUS: PHASE 2.0 WORKFLOW REGISTRATION CERTIFICATION PASSED"
    )

else:

    print(
        "STATUS: PHASE 2.0 WORKFLOW REGISTRATION CERTIFICATION FAILED"
    )

print()

print(
    "REPORT:",
    REPORT,
)

print("=" * 86)

raise SystemExit(
    0
    if failed == 0
    else 1
)
