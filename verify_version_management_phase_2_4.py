from __future__ import annotations

import ast
import hashlib
import importlib
import json
from pathlib import Path

from backend.server.coordination.version_management.manager import (
    VERSION_MANAGEMENT_VERSION,
    VERSION_MANAGEMENT_SCHEMA_VERSION,
    VersionManagementError,
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

from backend.server.coordination.workflow_registry.registry import (
    WORKFLOW_REGISTRY_VERSION,
    register_workflow_definition,
)

from backend.server.coordination.coordinator_registry.registry import (
    COORDINATOR_REGISTRY_VERSION,
    register_coordinator,
)

from backend.server.coordination.registration_validation.validator import (
    REGISTRATION_VALIDATION_VERSION,
)

from backend.server.coordination.pipeline_coordinators.contract import (
    PipelineCoordinatorContract,
    CoordinatorExecutionModel,
    CoordinatorRuntimePolicy,
)

from backend.server.coordination.universal_workflows.contract import (
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)


TARGET = Path(
    "backend/server/coordination/version_management/manager.py"
)

REPORT = Path(
    "version_management_phase_2_4_certification.txt"
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
print("PHASE 2.4 VERSION MANAGEMENT CERTIFICATION")
print("=" * 82)


# ============================================================================
# 1. File / syntax / import
# ============================================================================

check(
    "Canonical Version Management file exists",
    TARGET.exists(),
    str(
        TARGET
    ),
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
        "backend.server.coordination.version_management.manager"
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
    "Version Management imports successfully",
    import_ok,
)


# ============================================================================
# 2. Component identity
# ============================================================================

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


# ============================================================================
# 3. Frozen upstream versions
# ============================================================================

check(
    "Workflow Registry version is canonical",
    WORKFLOW_REGISTRY_VERSION
    == "workflow_registry_v2.1.0",
)

check(
    "Coordinator Registry version is canonical",
    COORDINATOR_REGISTRY_VERSION
    == "coordinator_registry_v2.2.0",
)

check(
    "Registration Validation version is canonical",
    REGISTRATION_VALIDATION_VERSION
    == "registration_validation_v2.3.0",
)


# ============================================================================
# 4. Register workflow versions
# ============================================================================

workflow_v1 = register_workflow_definition(
    workflow_type="phase_2_4_certification_pipeline",
    workflow_version="v1",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
)

workflow_v2 = register_workflow_definition(
    workflow_type="phase_2_4_certification_pipeline",
    workflow_version="v2",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
)

workflow_v10 = register_workflow_definition(
    workflow_type="phase_2_4_certification_pipeline",
    workflow_version="v10",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
)

check(
    "Multiple workflow versions coexist",
    (
        workflow_v1.workflow_version,
        workflow_v2.workflow_version,
        workflow_v10.workflow_version,
    )
    == (
        "v1",
        "v2",
        "v10",
    ),
)


# ============================================================================
# 5. No implicit workflow preference
# ============================================================================

check(
    "No implicit preferred workflow exists",
    get_preferred_workflow_version(
        workflow_type=(
            "phase_2_4_certification_pipeline"
        )
    )
    is None,
)

check(
    "Preferred workflow resolver returns None without policy",
    resolve_preferred_workflow(
        workflow_type=(
            "phase_2_4_certification_pipeline"
        )
    )
    is None,
)


try:

    require_preferred_workflow(
        workflow_type=(
            "phase_2_4_certification_pipeline"
        )
    )

    missing_workflow_preference_rejected = False

except VersionPreferenceNotFoundError:

    missing_workflow_preference_rejected = True

check(
    "Required workflow preference rejects missing policy",
    missing_workflow_preference_rejected,
)


# ============================================================================
# 6. Explicit workflow preference
# ============================================================================

selected_workflow = (
    set_preferred_workflow_version(
        workflow_type=(
            "phase_2_4_certification_pipeline"
        ),
        workflow_version="v2",
    )
)

check(
    "Explicit workflow preference can select v2",
    selected_workflow
    == workflow_v2,
)

check(
    "Workflow preference stores exact v2",
    get_preferred_workflow_version(
        workflow_type=(
            "phase_2_4_certification_pipeline"
        )
    )
    == "v2",
)

check(
    "Preferred workflow resolves exact v2",
    resolve_preferred_workflow(
        workflow_type=(
            "phase_2_4_certification_pipeline"
        )
    )
    == workflow_v2,
)

check(
    "Required preferred workflow resolves exact v2",
    require_preferred_workflow(
        workflow_type=(
            "phase_2_4_certification_pipeline"
        )
    )
    == workflow_v2,
)


# ============================================================================
# 7. Workflow preference can change explicitly
# ============================================================================

selected_workflow_v1 = (
    set_preferred_workflow_version(
        workflow_type=(
            "phase_2_4_certification_pipeline"
        ),
        workflow_version="v1",
    )
)

check(
    "Explicit workflow preference can change from v2 to v1",
    selected_workflow_v1
    == workflow_v1,
)

check(
    "Workflow preference change does not infer v10 as latest",
    get_preferred_workflow_version(
        workflow_type=(
            "phase_2_4_certification_pipeline"
        )
    )
    == "v1",
)


# ============================================================================
# 8. Invalid workflow preference
# ============================================================================

try:

    set_preferred_workflow_version(
        workflow_type=(
            "phase_2_4_certification_pipeline"
        ),
        workflow_version="v999",
    )

    invalid_workflow_rejected = False

except InvalidVersionPreferenceError:

    invalid_workflow_rejected = True

check(
    "Unregistered workflow preference is rejected",
    invalid_workflow_rejected,
)


# ============================================================================
# 9. Coordinator versions
# ============================================================================

coordinator_v1 = build_coordinator(
    coordinator_id=(
        "phase_2_4_certification_coordinator"
    ),
    coordinator_version="v1",
    workflow_type=(
        "phase_2_4_certification_pipeline"
    ),
    workflow_version="v2",
)

coordinator_v2 = build_coordinator(
    coordinator_id=(
        "phase_2_4_certification_coordinator"
    ),
    coordinator_version="v2",
    workflow_type=(
        "phase_2_4_certification_pipeline"
    ),
    workflow_version="v2",
)

register_coordinator(
    coordinator_v1
)

register_coordinator(
    coordinator_v2
)

check(
    "Multiple coordinator versions coexist",
    coordinator_v1.coordinator_version
    == "v1"
    and coordinator_v2.coordinator_version
    == "v2",
)


# ============================================================================
# 10. No implicit coordinator preference
# ============================================================================

check(
    "No implicit preferred coordinator exists",
    get_preferred_coordinator_version(
        coordinator_id=(
            "phase_2_4_certification_coordinator"
        )
    )
    is None,
)

check(
    "Preferred coordinator resolver returns None without policy",
    resolve_preferred_coordinator(
        coordinator_id=(
            "phase_2_4_certification_coordinator"
        )
    )
    is None,
)


try:

    require_preferred_coordinator(
        coordinator_id=(
            "phase_2_4_certification_coordinator"
        )
    )

    missing_coordinator_preference_rejected = False

except VersionPreferenceNotFoundError:

    missing_coordinator_preference_rejected = True

check(
    "Required coordinator preference rejects missing policy",
    missing_coordinator_preference_rejected,
)


# ============================================================================
# 11. Explicit coordinator preference
# ============================================================================

selected_coordinator = (
    set_preferred_coordinator_version(
        coordinator_id=(
            "phase_2_4_certification_coordinator"
        ),
        coordinator_version="v2",
    )
)

check(
    "Explicit coordinator preference selects v2",
    selected_coordinator
    == coordinator_v2,
)

check(
    "Coordinator preference stores exact v2",
    get_preferred_coordinator_version(
        coordinator_id=(
            "phase_2_4_certification_coordinator"
        )
    )
    == "v2",
)

check(
    "Preferred coordinator resolves exact v2",
    resolve_preferred_coordinator(
        coordinator_id=(
            "phase_2_4_certification_coordinator"
        )
    )
    == coordinator_v2,
)

check(
    "Required preferred coordinator resolves exact v2",
    require_preferred_coordinator(
        coordinator_id=(
            "phase_2_4_certification_coordinator"
        )
    )
    == coordinator_v2,
)


# ============================================================================
# 12. Coordinator preference change
# ============================================================================

selected_coordinator_v1 = (
    set_preferred_coordinator_version(
        coordinator_id=(
            "phase_2_4_certification_coordinator"
        ),
        coordinator_version="v1",
    )
)

check(
    "Explicit coordinator preference can change from v2 to v1",
    selected_coordinator_v1
    == coordinator_v1,
)


# ============================================================================
# 13. Invalid coordinator version
# ============================================================================

try:

    set_preferred_coordinator_version(
        coordinator_id=(
            "phase_2_4_certification_coordinator"
        ),
        coordinator_version="v999",
    )

    invalid_coordinator_rejected = False

except InvalidVersionPreferenceError:

    invalid_coordinator_rejected = True

check(
    "Unregistered coordinator preference is rejected",
    invalid_coordinator_rejected,
)


# ============================================================================
# 14. Orphan coordinator
# ============================================================================

orphan = build_coordinator(
    coordinator_id=(
        "phase_2_4_certification_orphan"
    ),
    coordinator_version="v1",
    workflow_type=(
        "phase_2_4_missing_workflow"
    ),
    workflow_version="v1",
)

register_coordinator(
    orphan
)


try:

    set_preferred_coordinator_version(
        coordinator_id=(
            orphan.coordinator_id
        ),
        coordinator_version=(
            orphan.coordinator_version
        ),
    )

    orphan_preference_rejected = False

except InvalidVersionPreferenceError:

    orphan_preference_rejected = True

check(
    "Coordinator failing Phase 2.3 cannot become preferred",
    orphan_preference_rejected,
)


# ============================================================================
# 15. Workflow-bound coordinator preference
# ============================================================================

bound = set_preferred_workflow_coordinator(
    workflow_type=(
        "phase_2_4_certification_pipeline"
    ),
    workflow_version="v2",
    coordinator_id=(
        "phase_2_4_certification_coordinator"
    ),
    coordinator_version="v2",
)

check(
    "Workflow-bound coordinator preference succeeds",
    bound
    == coordinator_v2,
)

identity = (
    get_preferred_workflow_coordinator_identity(
        workflow_type=(
            "phase_2_4_certification_pipeline"
        ),
        workflow_version="v2",
    )
)

check(
    "Workflow-bound coordinator identity is exact",
    identity
    == (
        "phase_2_4_certification_coordinator",
        "v2",
    ),
)

check(
    "Workflow-bound coordinator resolves exactly",
    resolve_preferred_workflow_coordinator(
        workflow_type=(
            "phase_2_4_certification_pipeline"
        ),
        workflow_version="v2",
    )
    == coordinator_v2,
)

check(
    "Required workflow-bound coordinator resolves exactly",
    require_preferred_workflow_coordinator(
        workflow_type=(
            "phase_2_4_certification_pipeline"
        ),
        workflow_version="v2",
    )
    == coordinator_v2,
)


# ============================================================================
# 16. Wrong workflow mapping
# ============================================================================

try:

    set_preferred_workflow_coordinator(
        workflow_type=(
            "phase_2_4_certification_pipeline"
        ),
        workflow_version="v1",
        coordinator_id=(
            "phase_2_4_certification_coordinator"
        ),
        coordinator_version="v2",
    )

    wrong_mapping_rejected = False

except InvalidVersionPreferenceError:

    wrong_mapping_rejected = True

check(
    "Workflow-bound coordinator rejects workflow mismatch",
    wrong_mapping_rejected,
)


# ============================================================================
# 17. Missing workflow-bound policy
# ============================================================================

check(
    "Missing workflow-bound preference resolves to None",
    resolve_preferred_workflow_coordinator(
        workflow_type=(
            "phase_2_4_certification_pipeline"
        ),
        workflow_version="v1",
    )
    is None,
)


try:

    require_preferred_workflow_coordinator(
        workflow_type=(
            "phase_2_4_certification_pipeline"
        ),
        workflow_version="v1",
    )

    missing_bound_rejected = False

except VersionPreferenceNotFoundError:

    missing_bound_rejected = True

check(
    "Required workflow-bound preference rejects missing policy",
    missing_bound_rejected,
)


# ============================================================================
# 18. Snapshot
# ============================================================================

snapshot = version_management_snapshot()

check(
    "Snapshot exposes Version Management version",
    snapshot[
        "version_management_version"
    ]
    == VERSION_MANAGEMENT_VERSION,
)

check(
    "Snapshot exposes Version Management schema",
    snapshot[
        "schema_version"
    ]
    == VERSION_MANAGEMENT_SCHEMA_VERSION,
)

check(
    "Snapshot exposes Workflow Registry version",
    snapshot[
        "workflow_registry_version"
    ]
    == WORKFLOW_REGISTRY_VERSION,
)

check(
    "Snapshot exposes Coordinator Registry version",
    snapshot[
        "coordinator_registry_version"
    ]
    == COORDINATOR_REGISTRY_VERSION,
)

check(
    "Snapshot exposes Registration Validation version",
    snapshot[
        "registration_validation_version"
    ]
    == REGISTRATION_VALIDATION_VERSION,
)

check(
    "Snapshot records one workflow preference",
    snapshot[
        "workflow_preference_count"
    ]
    == 1,
)

check(
    "Snapshot records one coordinator preference",
    snapshot[
        "coordinator_preference_count"
    ]
    == 1,
)

check(
    "Snapshot records one workflow-bound coordinator preference",
    snapshot[
        "workflow_coordinator_preference_count"
    ]
    == 1,
)


# ============================================================================
# 19. Snapshot deterministic values
# ============================================================================

check(
    "Workflow preference snapshot is deterministic",
    snapshot[
        "workflow_preferences"
    ]
    == (
        (
            "phase_2_4_certification_pipeline",
            "v1",
        ),
    ),
)

check(
    "Coordinator preference snapshot is deterministic",
    snapshot[
        "coordinator_preferences"
    ]
    == (
        (
            "phase_2_4_certification_coordinator",
            "v1",
        ),
    ),
)

check(
    "Workflow-bound coordinator snapshot is deterministic",
    snapshot[
        "workflow_coordinator_preferences"
    ]
    == (
        (
            "phase_2_4_certification_pipeline",
            "v2",
            "phase_2_4_certification_coordinator",
            "v2",
        ),
    ),
)


# ============================================================================
# 20. Snapshot boundary flags
# ============================================================================

check(
    "Snapshot declares no automatic latest inference",
    snapshot[
        "automatic_latest_inference"
    ]
    is False,
)

check(
    "Snapshot declares no semantic-version ordering",
    snapshot[
        "semantic_version_ordering"
    ]
    is False,
)

check(
    "Snapshot declares no registry mutation",
    snapshot[
        "registry_mutation"
    ]
    is False,
)

check(
    "Snapshot declares no execution",
    snapshot[
        "execution"
    ]
    is False,
)

check(
    "Snapshot declares no persistence",
    snapshot[
        "persistence"
    ]
    is False,
)


# ============================================================================
# 21. Snapshot immutability
# ============================================================================

snapshot_immutable = False

try:

    snapshot[
        "workflow_preference_count"
    ] = 999

except Exception:

    snapshot_immutable = True

check(
    "Version Management snapshot is immutable",
    snapshot_immutable,
)


# ============================================================================
# 22. Input validation
# ============================================================================

invalid_inputs = (
    (
        "workflow_type",
        lambda: get_preferred_workflow_version(
            workflow_type=""
        ),
    ),
    (
        "coordinator_id",
        lambda: get_preferred_coordinator_version(
            coordinator_id=""
        ),
    ),
    (
        "workflow_version",
        lambda: set_preferred_workflow_version(
            workflow_type=(
                "phase_2_4_certification_pipeline"
            ),
            workflow_version="",
        ),
    ),
    (
        "coordinator_version",
        lambda: set_preferred_coordinator_version(
            coordinator_id=(
                "phase_2_4_certification_coordinator"
            ),
            coordinator_version="",
        ),
    ),
)

for field_name, action in invalid_inputs:

    try:

        action()

        rejected = False

    except VersionManagementError:

        rejected = True

    check(
        f"Empty {field_name} is rejected",
        rejected,
    )


# ============================================================================
# 23. Architecture declaration
# ============================================================================

explanation = (
    explain_version_management_v2_4()
)

check(
    "Architecture declaration identifies Phase 2.4",
    explanation[
        "phase"
    ]
    == "2.4",
)

check(
    "Architecture declaration identifies Version Management",
    explanation[
        "component"
    ]
    == "Version Management",
)

check(
    "Selection policy is explicit_exact_preference",
    explanation[
        "selection_policy"
    ]
    == "explicit_exact_preference",
)

check(
    "Workflow preference identity is workflow_type",
    explanation[
        "workflow_preference_identity"
    ]
    == "workflow_type",
)

check(
    "Coordinator preference identity is coordinator_id",
    explanation[
        "coordinator_preference_identity"
    ]
    == "coordinator_id",
)

check(
    "Workflow-bound coordinator preference identity is exact workflow identity",
    explanation[
        "workflow_coordinator_preference_identity"
    ]
    == (
        "workflow_type",
        "workflow_version",
    ),
)


# ============================================================================
# 24. Ownership
# ============================================================================

required_owns = (
    "explicit workflow version preference",
    "explicit coordinator version preference",
    "explicit workflow-bound coordinator preference",
    "exact preferred-version resolution",
    "preference validation against frozen registries",
    "preferred coordinator validation through Phase 2.3",
    "deterministic preference inspection",
    "immutable version-management snapshot",
)

for item in required_owns:

    check(
        f"Version Management owns: {item}",
        item
        in explanation[
            "owns"
        ],
    )


# ============================================================================
# 25. Exclusions
# ============================================================================

required_exclusions = (
    "workflow registration",
    "coordinator registration",
    "registration validation rules",
    "automatic latest inference",
    "semantic version parsing",
    "registry replacement",
    "registry deletion",
    "coordinator execution",
    "workflow execution",
    "Runtime Registration",
    "runtime job creation",
    "stage ordering",
    "dependency planning",
    "workflow lifecycle transitions",
    "persistence",
    "coordinator lifecycle",
    "coordinator deprecation",
    "migration execution",
)

for item in required_exclusions:

    check(
        f"Version Management excludes: {item}",
        item
        in explanation[
            "does_not_own"
        ],
    )


check(
    "Workflow State Persistence remains Phase 8 authority",
    explanation[
        "future_authority"
    ][
        "8.0"
    ]
    == "Workflow State Persistence",
)

check(
    "Coordinator Lifecycle remains Phase 11.5 authority",
    explanation[
        "future_authority"
    ][
        "11.5"
    ]
    == "Coordinator Lifecycle",
)


# ============================================================================
# 26. Static import boundary
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
        "workflow_registry.registry"
    ),
    (
        "backend.server.coordination."
        "coordinator_registry.registry"
    ),
    (
        "backend.server.coordination."
        "pipeline_coordinators.contract"
    ),
    (
        "backend.server.coordination."
        "registration_validation.validator"
    ),
}

check(
    "Version Management imports only allowed coordination components",
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
        fragment
        in name
        for fragment
        in forbidden_import_fragments
    )
]

check(
    "Version Management has no runtime/stage/pipeline execution imports",
    not violating_imports,
    json.dumps(
        violating_imports
    ),
)


# ============================================================================
# 27. No registry mutation imports
# ============================================================================

check(
    "Version Management does not import workflow registration operations",
    "register_workflow" not in source
    and "register_workflow_definition" not in source,
)

check(
    "Version Management does not import coordinator registration operations",
    "register_coordinator" not in source,
)


# ============================================================================
# 28. No automatic latest inference
# ============================================================================

forbidden_latest_markers = (
    "resolve_latest",
    "get_latest",
    "latest_version(",
    "max(version",
    "max(versions",
    "packaging.version",
    "Version(",
    "parse_version(",
)

latest_violations = [
    marker
    for marker
    in forbidden_latest_markers
    if marker in source
]

check(
    "Version Management performs no automatic latest inference",
    not latest_violations,
    json.dumps(
        latest_violations
    ),
)


# ============================================================================
# 29. No execution
# ============================================================================

forbidden_execution_markers = (
    "create_universal",
    "dispatch(",
    "execute(",
    "run_coordinator(",
    "invoke_coordinator(",
    "handler_ref",
    "job_id",
    "worker_id",
)

execution_violations = [
    marker
    for marker
    in forbidden_execution_markers
    if marker in source
]

check(
    "Version Management performs no runtime/coordinator execution",
    not execution_violations,
    json.dumps(
        execution_violations
    ),
)


# ============================================================================
# 30. No persistence / external I/O
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

io_violations = [
    marker
    for marker
    in forbidden_io_markers
    if marker in source
]

check(
    "Version Management performs no persistence or external I/O",
    not io_violations,
    json.dumps(
        io_violations
    ),
)


# ============================================================================
# 31. No lifecycle/deprecation authority
# ============================================================================

check(
    "Version Management exposes no coordinator lifecycle operation",
    "activate_coordinator(" not in source
    and "deactivate_coordinator(" not in source,
)

check(
    "Version Management exposes no deprecation operation",
    "deprecate_coordinator(" not in source
    and "deprecate_workflow(" not in source,
)

check(
    "Version Management exposes no registry deletion operation",
    "delete_workflow(" not in source
    and "delete_coordinator(" not in source
    and "remove_workflow(" not in source
    and "remove_coordinator(" not in source,
)


# ============================================================================
# 32. Frozen upstream hashes
# ============================================================================

frozen_files = (
    (
        "Phase 2.1 Workflow Registry",
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
        "Phase 2.2 Coordinator Registry",
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
        "Phase 2.3 Registration Validation",
        Path(
            "backend/server/coordination/"
            "registration_validation/validator.py"
        ),
        (
            "30853E34C6F09B89A2C67D50D91C06EB"
            "4B2436A12918DC4E26197EB6159E8453"
        ),
    ),
)

for (
    name,
    path,
    expected,
) in frozen_files:

    actual = hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()

    check(
        f"Frozen {name} hash unchanged",
        actual == expected,
        actual,
    )


# ============================================================================
# 33. Canonical SHA256
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
# 34. Final result
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
    "PHASE 2.4 VERSION MANAGEMENT CERTIFICATION",
    "=" * 82,
    "",
    (
        "Version Management Version: "
        + VERSION_MANAGEMENT_VERSION
    ),
    (
        "Version Management Schema: "
        + VERSION_MANAGEMENT_SCHEMA_VERSION
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
        "Registration Validation: "
        + REGISTRATION_VALIDATION_VERSION
    ),
    "Selection Policy: explicit_exact_preference",
    (
        "Workflow Preference Identity: "
        "workflow_type"
    ),
    (
        "Coordinator Preference Identity: "
        "coordinator_id"
    ),
    (
        "Workflow Coordinator Preference Identity: "
        "workflow_type + workflow_version"
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

