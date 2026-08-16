from __future__ import annotations

import ast
import hashlib
import importlib
import json
from pathlib import Path

from backend.server.coordination.coordinator_registry.registry import (
    COORDINATOR_REGISTRY_VERSION,
    COORDINATOR_REGISTRY_SCHEMA_VERSION,
    CoordinatorRegistryError,
    CoordinatorAlreadyRegisteredError,
    CoordinatorNotRegisteredError,
    coordinator_registry_key,
    register_coordinator,
    get_registered_coordinator,
    require_registered_coordinator,
    is_coordinator_registered,
    registered_coordinator_count,
    list_registered_coordinators,
    list_coordinators_for_workflow,
    coordinator_registry_snapshot,
    explain_coordinator_registry_v2_2,
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
    "backend/server/coordination/coordinator_registry/registry.py"
)

REPORT = Path(
    "coordinator_registration_phase_2_2_certification.txt"
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
    workflow_type="linking_target_pipeline",
    workflow_version="linking_target_pipeline_v1",
    capabilities=("start",),
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
            "backend.server.pipelines.connect_domain."
            "linking_target_pipeline.coordinator:"
            "run_linking_target_pipeline"
        ),
        execution_model=(
            CoordinatorExecutionModel.SYNCHRONOUS
        ),
        runtime_policy=(
            CoordinatorRuntimePolicy.UNIVERSAL_RUNTIME_REQUIRED
        ),
        capabilities=capabilities,
        stage_job_types=(
            "site_sources",
            "url_cleaner",
            "site_pages",
            "live_domain_target_pool",
            "active_target_set",
        ),
        responsibilities=(
            "coordinate linking target pipeline",
        ),
        excluded_responsibilities=(
            "execute stage business logic",
            "own Runtime Registration",
        ),
        metadata={
            "certification": True,
        },
    )


print()
print("=" * 82)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 2.2 COORDINATOR REGISTRATION CERTIFICATION")
print("=" * 82)


# ============================================================================
# 1. File / syntax / import
# ============================================================================

check(
    "Canonical Coordinator Registry file exists",
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
        "backend.server.coordination.coordinator_registry.registry"
    )
    import_ok = True
except Exception as exc:
    import_ok = False
    print(
        repr(exc)
    )

check(
    "Coordinator Registry imports successfully",
    import_ok,
)


# ============================================================================
# 2. Registry identity
# ============================================================================

check(
    "Coordinator Registry version is canonical",
    COORDINATOR_REGISTRY_VERSION
    == "coordinator_registry_v2.2.0",
)

check(
    "Coordinator Registry schema version is canonical",
    COORDINATOR_REGISTRY_SCHEMA_VERSION
    == "coordinator_registry_schema_v1",
)


# ============================================================================
# 3. Canonical identity key
# ============================================================================

key = coordinator_registry_key(
    coordinator_id="certification_coordinator",
    coordinator_version="v1",
)

check(
    "Canonical coordinator identity is coordinator_id + coordinator_version",
    key
    == (
        "certification_coordinator",
        "v1",
    ),
    repr(
        key
    ),
)


# ============================================================================
# 4. Frozen contract remains registered object
# ============================================================================

coordinator = build_coordinator(
    coordinator_id="certification_coordinator",
    coordinator_version="v1",
    capabilities=(
        "start",
        "advance",
        "inspect",
    ),
)

check(
    "Canonical PipelineCoordinatorContract constructs",
    isinstance(
        coordinator,
        PipelineCoordinatorContract,
    ),
)

check(
    "Coordinator Contract version preserved",
    coordinator.contract_version
    == PIPELINE_COORDINATOR_CONTRACT_VERSION,
)

check(
    "Workflow Contract version preserved",
    coordinator.workflow_contract_version
    == UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)

check(
    "Coordinator identity preserved",
    (
        coordinator.coordinator_id,
        coordinator.coordinator_version,
    )
    == key,
)

check(
    "Workflow identity preserved",
    (
        coordinator.workflow_type,
        coordinator.workflow_version,
    )
    == (
        "linking_target_pipeline",
        "linking_target_pipeline_v1",
    ),
)

check(
    "Entrypoint preserved",
    coordinator.entrypoint.endswith(
        ":run_linking_target_pipeline"
    ),
)

check(
    "Runtime policy remains coordinator contract data",
    coordinator.runtime_policy
    == CoordinatorRuntimePolicy.UNIVERSAL_RUNTIME_REQUIRED,
)


# ============================================================================
# 5. Registration
# ============================================================================

registered = register_coordinator(
    coordinator
)

check(
    "Coordinator registration succeeds",
    registered == coordinator,
)

check(
    "Registered coordinator count is non-zero",
    registered_coordinator_count()
    >= 1,
)


# ============================================================================
# 6. Exact lookup
# ============================================================================

resolved = get_registered_coordinator(
    coordinator_id="certification_coordinator",
    coordinator_version="v1",
)

check(
    "Exact coordinator lookup succeeds",
    resolved == coordinator,
)

required = require_registered_coordinator(
    coordinator_id="certification_coordinator",
    coordinator_version="v1",
)

check(
    "Required exact coordinator lookup succeeds",
    required == coordinator,
)

check(
    "Coordinator registered predicate succeeds",
    is_coordinator_registered(
        coordinator_id="certification_coordinator",
        coordinator_version="v1",
    ),
)


# ============================================================================
# 7. No implicit version resolution
# ============================================================================

check(
    "Unknown coordinator version is not implicitly resolved",
    get_registered_coordinator(
        coordinator_id="certification_coordinator",
        coordinator_version="v2",
    )
    is None,
)


try:

    require_registered_coordinator(
        coordinator_id="certification_coordinator",
        coordinator_version="missing",
    )

    missing_rejected = False

except CoordinatorNotRegisteredError:
    missing_rejected = True

check(
    "Missing coordinator raises CoordinatorNotRegisteredError",
    missing_rejected,
)


# ============================================================================
# 8. Duplicate protection
# ============================================================================

try:

    register_coordinator(
        coordinator
    )

    duplicate_rejected = False

except CoordinatorAlreadyRegisteredError:
    duplicate_rejected = True

check(
    "Duplicate exact coordinator identity is rejected",
    duplicate_rejected,
)


# ============================================================================
# 9. Independent coordinator versions
# ============================================================================

coordinator_v2 = build_coordinator(
    coordinator_id="certification_coordinator",
    coordinator_version="v2",
)

register_coordinator(
    coordinator_v2
)

check(
    "Independent coordinator versions coexist",
    is_coordinator_registered(
        coordinator_id="certification_coordinator",
        coordinator_version="v1",
    )
    and is_coordinator_registered(
        coordinator_id="certification_coordinator",
        coordinator_version="v2",
    ),
)


# ============================================================================
# 10. Different coordinators may target same workflow
# ============================================================================

secondary = build_coordinator(
    coordinator_id="secondary_certification_coordinator",
    coordinator_version="v1",
)

register_coordinator(
    secondary
)

workflow_matches = (
    list_coordinators_for_workflow(
        workflow_type="linking_target_pipeline",
        workflow_version="linking_target_pipeline_v1",
    )
)

check(
    "Workflow identity inspection returns matching coordinators",
    coordinator in workflow_matches
    and coordinator_v2 in workflow_matches
    and secondary in workflow_matches,
)


# ============================================================================
# 11. Exact workflow inspection
# ============================================================================

check(
    "Different workflow version returns no accidental matches",
    list_coordinators_for_workflow(
        workflow_type="linking_target_pipeline",
        workflow_version="linking_target_pipeline_v999",
    )
    == (),
)


# ============================================================================
# 12. Deterministic listing
# ============================================================================

coordinators = (
    list_registered_coordinators()
)

check(
    "Coordinator listing is deterministic",
    coordinators
    == tuple(
        sorted(
            coordinators,
            key=lambda item: (
                item.coordinator_id,
                item.coordinator_version,
            ),
        )
    ),
)

check(
    "Coordinator count matches listing",
    registered_coordinator_count()
    == len(
        coordinators
    ),
)


# ============================================================================
# 13. Snapshot
# ============================================================================

snapshot = (
    coordinator_registry_snapshot()
)

check(
    "Snapshot reports Coordinator Registry version",
    snapshot[
        "registry_version"
    ]
    == COORDINATOR_REGISTRY_VERSION,
)

check(
    "Snapshot reports Coordinator Registry schema",
    snapshot[
        "schema_version"
    ]
    == COORDINATOR_REGISTRY_SCHEMA_VERSION,
)

check(
    "Snapshot reports frozen Coordinator Contract version",
    snapshot[
        "pipeline_coordinator_contract_version"
    ]
    == PIPELINE_COORDINATOR_CONTRACT_VERSION,
)

check(
    "Snapshot declares canonical identity",
    snapshot[
        "identity_fields"
    ]
    == (
        "coordinator_id",
        "coordinator_version",
    ),
)

check(
    "Snapshot count matches registry",
    snapshot[
        "count"
    ]
    == registered_coordinator_count(),
)

check(
    "Snapshot declares no persistence",
    snapshot[
        "persistence"
    ]
    is False,
)

check(
    "Snapshot declares exact-version lookup only",
    snapshot[
        "exact_version_lookup_only"
    ]
    is True,
)

check(
    "Snapshot declares cross-registry validation deferred",
    snapshot[
        "cross_registry_validation"
    ]
    is False,
)

check(
    "Snapshot declares version selection deferred",
    snapshot[
        "version_selection"
    ]
    is False,
)


snapshot_immutable = False

try:

    snapshot[
        "count"
    ] = 999

except Exception:
    snapshot_immutable = True

check(
    "Coordinator Registry snapshot is immutable",
    snapshot_immutable,
)


# ============================================================================
# 14. Coordinator contract immutability
# ============================================================================

coordinator_immutable = False

try:

    coordinator.coordinator_id = (
        "mutated"
    )

except Exception:
    coordinator_immutable = True

check(
    "Registered PipelineCoordinatorContract remains immutable",
    coordinator_immutable,
)


# ============================================================================
# 15. Invalid registry key inputs
# ============================================================================

invalid_key_cases = (
    (
        "empty coordinator_id",
        "",
        "v1",
    ),
    (
        "whitespace coordinator_id",
        "   ",
        "v1",
    ),
    (
        "empty coordinator_version",
        "example",
        "",
    ),
    (
        "whitespace coordinator_version",
        "example",
        "   ",
    ),
)

for (
    label,
    coordinator_id,
    coordinator_version,
) in invalid_key_cases:

    try:

        coordinator_registry_key(
            coordinator_id=coordinator_id,
            coordinator_version=coordinator_version,
        )

        rejected = False

    except CoordinatorRegistryError:
        rejected = True

    check(
        f"Invalid key {label} is rejected",
        rejected,
    )


try:

    coordinator_registry_key(
        coordinator_id=123,
        coordinator_version="v1",
    )

    non_string_id_rejected = False

except CoordinatorRegistryError:
    non_string_id_rejected = True

check(
    "Non-string coordinator_id is rejected",
    non_string_id_rejected,
)


try:

    coordinator_registry_key(
        coordinator_id="example",
        coordinator_version=123,
    )

    non_string_version_rejected = False

except CoordinatorRegistryError:
    non_string_version_rejected = True

check(
    "Non-string coordinator_version is rejected",
    non_string_version_rejected,
)


# ============================================================================
# 16. Invalid registration input
# ============================================================================

try:

    register_coordinator(
        "not-a-contract"
    )

    invalid_registration_rejected = False

except CoordinatorRegistryError:
    invalid_registration_rejected = True

check(
    "Non-PipelineCoordinatorContract registration is rejected",
    invalid_registration_rejected,
)


# ============================================================================
# 17. Workflow inspection validation
# ============================================================================

invalid_workflow_cases = (
    (
        "",
        "v1",
        "empty workflow_type",
    ),
    (
        "   ",
        "v1",
        "whitespace workflow_type",
    ),
    (
        "example",
        "",
        "empty workflow_version",
    ),
    (
        "example",
        "   ",
        "whitespace workflow_version",
    ),
)

for (
    workflow_type,
    workflow_version,
    label,
) in invalid_workflow_cases:

    try:

        list_coordinators_for_workflow(
            workflow_type=workflow_type,
            workflow_version=workflow_version,
        )

        rejected = False

    except CoordinatorRegistryError:
        rejected = True

    check(
        f"Invalid workflow inspection {label} is rejected",
        rejected,
    )


# ============================================================================
# 18. Architecture declaration
# ============================================================================

explanation = (
    explain_coordinator_registry_v2_2()
)

check(
    "Architecture declaration identifies Phase 2.2",
    explanation[
        "phase"
    ]
    == "2.2",
)

check(
    "Architecture declaration identifies Coordinator Registration",
    explanation[
        "component"
    ]
    == "Coordinator Registration",
)

check(
    "Registered object authority is PipelineCoordinatorContract",
    explanation[
        "registered_object"
    ]
    == "PipelineCoordinatorContract",
)

check(
    "Architecture declares canonical coordinator identity",
    explanation[
        "canonical_identity"
    ]
    == (
        "coordinator_id",
        "coordinator_version",
    ),
)


required_owns = (
    "coordinator existence declaration",
    "exact-version coordinator registration",
    "exact-version coordinator lookup",
    "duplicate coordinator identity rejection",
    "deterministic coordinator inspection",
    "workflow-identity inspection",
)

for item in required_owns:

    check(
        f"Coordinator Registration owns: {item}",
        item
        in explanation[
            "owns"
        ],
    )


required_exclusions = (
    "workflow existence validation",
    "workflow/coordinator cross-registration validation",
    "coordinator selection for execution",
    "latest coordinator selection",
    "default coordinator selection",
    "coordinator activation",
    "coordinator deactivation",
    "stage ordering",
    "dependency planning",
    "Runtime Registration",
    "runtime handler resolution",
    "runtime job creation",
    "coordinator invocation",
    "workflow execution",
    "workflow lifecycle state",
    "workflow execution state",
    "persistence",
    "migration",
    "version governance",
)

for item in required_exclusions:

    check(
        f"Coordinator Registration excludes: {item}",
        item
        in explanation[
            "does_not_own"
        ],
    )


check(
    "Cross-registry validation assigned to Phase 2.3",
    explanation[
        "future_authority"
    ][
        "2.3"
    ]
    == "Registration Validation",
)

check(
    "Version Management assigned to Phase 2.4",
    explanation[
        "future_authority"
    ][
        "2.4"
    ]
    == "Version Management",
)


# ============================================================================
# 19. Static architecture boundary
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
        "pipeline_coordinators.contract"
    ),
}

check(
    "Coordinator Registry imports only frozen Pipeline Coordinator Contract",
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
    (
        "backend.server.coordination."
        "workflow_registry"
    ),
    (
        "backend.server.coordination."
        "universal_stages"
    ),
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
    "Coordinator Registry has no runtime/workflow-registry/stage/pipeline imports",
    not violating_imports,
    json.dumps(
        violating_imports
    ),
)


# ============================================================================
# 20. No persistence or external I/O
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
    "Coordinator Registry performs no persistence or external I/O",
    not violating_io,
    json.dumps(
        violating_io
    ),
)


# ============================================================================
# 21. No execution authority
# ============================================================================

forbidden_execution_markers = (
    "importlib.import_module(",
    "create_universal",
    "dispatch(",
    "execute(",
    "run_coordinator(",
    "invoke_coordinator(",
    "handler_ref:",
    "job_id:",
    "queue_state:",
    "worker_id:",
    "dependency_graph:",
    "next_stage:",
)

violating_execution = [
    marker
    for marker
    in forbidden_execution_markers
    if marker in source
]

check(
    "Coordinator Registry performs no coordinator/runtime execution",
    not violating_execution,
    json.dumps(
        violating_execution
    ),
)


# ============================================================================
# 22. No premature cross-registry validation
# ============================================================================

check(
    "Coordinator Registry does not import Workflow Registry",
    (
        "workflow_registry.registry"
        not in source
    ),
)

check(
    "Coordinator Registry does not require workflow registration",
    (
        "require_registered_workflow"
        not in source
    ),
)


# ============================================================================
# 23. No premature Version Management
# ============================================================================

check(
    "Coordinator Registry exposes no replace parameter",
    "replace=" not in source
    and "replace: bool" not in source,
)

check(
    "Coordinator Registry exposes no latest coordinator resolver",
    "get_latest" not in source
    and "resolve_latest" not in source
    and "latest_coordinator" not in source,
)

check(
    "Coordinator Registry exposes no default coordinator resolver",
    "default_coordinator" not in source,
)

check(
    "Coordinator Registry exposes no activation authority",
    "activate_coordinator(" not in source
    and "deactivate_coordinator(" not in source,
)


# ============================================================================
# 24. Thread-safety
# ============================================================================

check(
    "Coordinator Registry has synchronization lock",
    "_REGISTRY_LOCK" in source
    and "RLock" in source,
)


# ============================================================================
# 25. Canonical SHA256
# ============================================================================

sha256 = hashlib.sha256(
    TARGET.read_bytes()
).hexdigest().upper()

print()
print(
    "Canonical SHA256:"
)

print(
    sha256
)


# ============================================================================
# 26. Final certification result
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
    "PHASE 2.2 COORDINATOR REGISTRATION CERTIFICATION",
    "=" * 82,
    "",
    (
        "Registry Version: "
        + COORDINATOR_REGISTRY_VERSION
    ),
    (
        "Registry Schema: "
        + COORDINATOR_REGISTRY_SCHEMA_VERSION
    ),
    (
        "Pipeline Coordinator Contract: "
        + PIPELINE_COORDINATOR_CONTRACT_VERSION
    ),
    (
        "Workflow Contract: "
        + UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
    (
        "Canonical Identity: "
        "coordinator_id + coordinator_version"
    ),
    (
        "Registered Object: "
        "PipelineCoordinatorContract"
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
