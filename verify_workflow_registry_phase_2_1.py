from __future__ import annotations

import ast
import hashlib
import importlib
import json
from pathlib import Path

from backend.server.coordination.workflow_registry.registry import (
    WORKFLOW_REGISTRY_VERSION,
    WORKFLOW_REGISTRY_ENTRY_SCHEMA_VERSION,
    WorkflowRegistryEntry,
    WorkflowRegistryError,
    WorkflowAlreadyRegisteredError,
    WorkflowNotRegisteredError,
    workflow_registry_key,
    register_workflow,
    register_workflow_definition,
    get_registered_workflow,
    require_registered_workflow,
    is_workflow_registered,
    registered_workflow_count,
    list_registered_workflows,
    workflow_registry_snapshot,
    explain_workflow_registry_v2_1,
)

from backend.server.coordination.universal_workflows.contract import (
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)


TARGET = Path(
    "backend/server/coordination/workflow_registry/registry.py"
)

REPORT = Path(
    "workflow_registry_phase_2_1_certification.txt"
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
            f"       {detail}"
        )

    return ok


print()
print("=" * 82)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 2.1 WORKFLOW REGISTRY CERTIFICATION")
print("=" * 82)


# ============================================================================
# 1. File / syntax / import
# ============================================================================

check(
    "Canonical Workflow Registry file exists",
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
        "backend.server.coordination.workflow_registry.registry"
    )
    import_ok = True
except Exception as exc:
    import_ok = False
    print(repr(exc))

check(
    "Workflow Registry imports successfully",
    import_ok,
)


# ============================================================================
# 2. Registry identity
# ============================================================================

check(
    "Registry version is canonical",
    WORKFLOW_REGISTRY_VERSION
    == "workflow_registry_v2.1.0",
)

check(
    "Entry schema version is canonical",
    WORKFLOW_REGISTRY_ENTRY_SCHEMA_VERSION
    == "workflow_registry_entry_schema_v1",
)


# ============================================================================
# 3. Canonical key
# ============================================================================

key = workflow_registry_key(
    workflow_type="linking_target_pipeline",
    workflow_version="linking_target_pipeline_v1",
)

check(
    "Canonical registry key is workflow_type + workflow_version",
    key
    == (
        "linking_target_pipeline",
        "linking_target_pipeline_v1",
    ),
    repr(key),
)


# ============================================================================
# 4. Canonical entry
# ============================================================================

entry = WorkflowRegistryEntry(
    workflow_type="linking_target_pipeline",
    workflow_version="linking_target_pipeline_v1",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
    description=(
        "Canonical Linking Target Pipeline workflow."
    ),
    metadata={
        "reference_pipeline":
            "linking_target_pipeline",
        "nested": {
            "enabled": True,
        },
    },
)

check(
    "Canonical WorkflowRegistryEntry constructs",
    isinstance(
        entry,
        WorkflowRegistryEntry,
    ),
)

check(
    "Entry key is canonical",
    entry.key == key,
)

check(
    "Workflow Contract compatibility preserved",
    entry.workflow_contract_version
    == UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)

check(
    "Description preserved",
    entry.description
    == "Canonical Linking Target Pipeline workflow.",
)

check(
    "Metadata preserved",
    entry.metadata.get(
        "reference_pipeline"
    )
    == "linking_target_pipeline",
)


# ============================================================================
# 5. Serialization
# ============================================================================

serialized = entry.to_dict()

check(
    "Entry serialization has exact field roster",
    tuple(
        serialized.keys()
    )
    == (
        "workflow_type",
        "workflow_version",
        "workflow_contract_version",
        "description",
        "metadata",
    ),
    json.dumps(
        list(
            serialized.keys()
        )
    ),
)

canonical_json_1 = (
    entry.canonical_json()
)

canonical_json_2 = (
    entry.canonical_json()
)

check(
    "Canonical JSON is deterministic",
    canonical_json_1
    == canonical_json_2,
)


# ============================================================================
# 6. Fingerprints
# ============================================================================

identity_1 = (
    entry.identity_fingerprint()
)

identity_2 = (
    entry.identity_fingerprint()
)

check(
    "Identity fingerprint is deterministic",
    identity_1 == identity_2
    and len(identity_1) == 64,
    identity_1,
)

content_1 = (
    entry.content_fingerprint()
)

content_2 = (
    entry.content_fingerprint()
)

check(
    "Content fingerprint is deterministic",
    content_1 == content_2
    and len(content_1) == 64,
    content_1,
)

changed_content = WorkflowRegistryEntry(
    workflow_type="linking_target_pipeline",
    workflow_version="linking_target_pipeline_v1",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
    description="Changed description.",
)

check(
    "Identity fingerprint ignores non-identity content",
    changed_content.identity_fingerprint()
    == identity_1,
)

check(
    "Content fingerprint changes when content changes",
    changed_content.content_fingerprint()
    != content_1,
)

changed_identity = WorkflowRegistryEntry(
    workflow_type="linking_target_pipeline",
    workflow_version="linking_target_pipeline_v2",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
)

check(
    "Identity fingerprint changes when workflow identity changes",
    changed_identity.identity_fingerprint()
    != identity_1,
)


# ============================================================================
# 7. Immutability
# ============================================================================

entry_immutable = False

try:
    entry.workflow_type = "mutated"
except Exception:
    entry_immutable = True

check(
    "WorkflowRegistryEntry is immutable",
    entry_immutable,
)

metadata_immutable = False

try:
    entry.metadata[
        "illegal"
    ] = True
except Exception:
    metadata_immutable = True

check(
    "Entry metadata is immutable",
    metadata_immutable,
)

nested_metadata_immutable = False

try:
    entry.metadata[
        "nested"
    ][
        "enabled"
    ] = False
except Exception:
    nested_metadata_immutable = True

check(
    "Nested metadata is deeply immutable",
    nested_metadata_immutable,
)


# ============================================================================
# 8. Registration
# ============================================================================

registered = register_workflow_definition(
    workflow_type="phase_2_1_test_pipeline",
    workflow_version="v1",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
    description="Certification workflow.",
    metadata={
        "certification": True,
    },
)

check(
    "Workflow registration succeeds",
    registered.workflow_type
    == "phase_2_1_test_pipeline",
)

check(
    "Registry contains registered workflow",
    is_workflow_registered(
        workflow_type="phase_2_1_test_pipeline",
        workflow_version="v1",
    ),
)


# ============================================================================
# 9. Exact lookup
# ============================================================================

resolved = get_registered_workflow(
    workflow_type="phase_2_1_test_pipeline",
    workflow_version="v1",
)

check(
    "Exact workflow lookup succeeds",
    resolved == registered,
)

check(
    "Different workflow version is not implicitly resolved",
    get_registered_workflow(
        workflow_type="phase_2_1_test_pipeline",
        workflow_version="v2",
    )
    is None,
)

required = require_registered_workflow(
    workflow_type="phase_2_1_test_pipeline",
    workflow_version="v1",
)

check(
    "Required exact lookup succeeds",
    required == registered,
)


# ============================================================================
# 10. Missing lookup protection
# ============================================================================

try:
    require_registered_workflow(
        workflow_type="phase_2_1_missing",
        workflow_version="v1",
    )
    missing_rejected = False
except WorkflowNotRegisteredError:
    missing_rejected = True

check(
    "Missing exact workflow raises WorkflowNotRegisteredError",
    missing_rejected,
)


# ============================================================================
# 11. Duplicate protection
# ============================================================================

try:
    register_workflow_definition(
        workflow_type="phase_2_1_test_pipeline",
        workflow_version="v1",
        workflow_contract_version=(
            UNIVERSAL_WORKFLOW_CONTRACT_VERSION
        ),
    )
    duplicate_rejected = False
except WorkflowAlreadyRegisteredError:
    duplicate_rejected = True

check(
    "Duplicate exact workflow identity is rejected",
    duplicate_rejected,
)


# ============================================================================
# 12. Independent versions
# ============================================================================

version_2 = register_workflow_definition(
    workflow_type="phase_2_1_test_pipeline",
    workflow_version="v2",
    workflow_contract_version=(
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
)

check(
    "Independent workflow versions can coexist",
    is_workflow_registered(
        workflow_type="phase_2_1_test_pipeline",
        workflow_version="v1",
    )
    and is_workflow_registered(
        workflow_type="phase_2_1_test_pipeline",
        workflow_version="v2",
    ),
)


# ============================================================================
# 13. Deterministic listing
# ============================================================================

entries = (
    list_registered_workflows()
)

check(
    "Workflow listing is deterministic",
    entries
    == tuple(
        sorted(
            entries,
            key=lambda item: (
                item.workflow_type,
                item.workflow_version,
            ),
        )
    ),
)


# ============================================================================
# 14. Registry count
# ============================================================================

check(
    "Registry count matches listing",
    registered_workflow_count()
    == len(entries),
)


# ============================================================================
# 15. Snapshot
# ============================================================================

snapshot = (
    workflow_registry_snapshot()
)

check(
    "Snapshot reports registry version",
    snapshot[
        "registry_version"
    ]
    == WORKFLOW_REGISTRY_VERSION,
)

check(
    "Snapshot reports entry schema version",
    snapshot[
        "entry_schema_version"
    ]
    == WORKFLOW_REGISTRY_ENTRY_SCHEMA_VERSION,
)

check(
    "Snapshot reports frozen Workflow Contract version",
    snapshot[
        "workflow_contract_version"
    ]
    == UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)

check(
    "Snapshot declares canonical identity fields",
    snapshot[
        "identity_fields"
    ]
    == (
        "workflow_type",
        "workflow_version",
    ),
)

check(
    "Snapshot count matches registry",
    snapshot[
        "count"
    ]
    == registered_workflow_count(),
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

snapshot_immutable = False

try:
    snapshot[
        "count"
    ] = 999
except Exception:
    snapshot_immutable = True

check(
    "Registry snapshot is immutable",
    snapshot_immutable,
)


# ============================================================================
# 16. Input validation
# ============================================================================

invalid_cases = (
    (
        "workflow_type",
        {
            "workflow_type": "",
            "workflow_version": "v1",
        },
    ),
    (
        "workflow_type whitespace",
        {
            "workflow_type": "   ",
            "workflow_version": "v1",
        },
    ),
    (
        "workflow_type characters",
        {
            "workflow_type": "invalid workflow",
            "workflow_version": "v1",
        },
    ),
    (
        "workflow_version",
        {
            "workflow_type": "example_pipeline",
            "workflow_version": "",
        },
    ),
    (
        "workflow_version whitespace",
        {
            "workflow_type": "example_pipeline",
            "workflow_version": "   ",
        },
    ),
    (
        "workflow_version characters",
        {
            "workflow_type": "example_pipeline",
            "workflow_version": "invalid version",
        },
    ),
)

for label, values in invalid_cases:

    try:

        WorkflowRegistryEntry(
            workflow_type=(
                values[
                    "workflow_type"
                ]
            ),
            workflow_version=(
                values[
                    "workflow_version"
                ]
            ),
            workflow_contract_version=(
                UNIVERSAL_WORKFLOW_CONTRACT_VERSION
            ),
        )

        rejected = False

    except WorkflowRegistryError:
        rejected = True

    check(
        f"Invalid {label} is rejected",
        rejected,
    )


try:

    WorkflowRegistryEntry(
        workflow_type="example_pipeline",
        workflow_version="v1",
        workflow_contract_version=(
            "wrong_workflow_contract"
        ),
    )

    wrong_contract_rejected = False

except WorkflowRegistryError:
    wrong_contract_rejected = True

check(
    "Wrong Workflow Contract version is rejected",
    wrong_contract_rejected,
)


try:

    WorkflowRegistryEntry(
        workflow_type="example_pipeline",
        workflow_version="v1",
        workflow_contract_version=(
            UNIVERSAL_WORKFLOW_CONTRACT_VERSION
        ),
        metadata=[
            "invalid"
        ],
    )

    invalid_metadata_rejected = False

except WorkflowRegistryError:
    invalid_metadata_rejected = True

check(
    "Non-mapping metadata is rejected",
    invalid_metadata_rejected,
)


try:

    WorkflowRegistryEntry(
        workflow_type="example_pipeline",
        workflow_version="v1",
        workflow_contract_version=(
            UNIVERSAL_WORKFLOW_CONTRACT_VERSION
        ),
        description=123,
    )

    invalid_description_rejected = False

except WorkflowRegistryError:
    invalid_description_rejected = True

check(
    "Non-string description is rejected",
    invalid_description_rejected,
)


try:
    register_workflow(
        "not-an-entry"
    )
    invalid_entry_rejected = False
except WorkflowRegistryError:
    invalid_entry_rejected = True

check(
    "register_workflow rejects non-entry objects",
    invalid_entry_rejected,
)


# ============================================================================
# 17. Architecture explanation
# ============================================================================

explanation = (
    explain_workflow_registry_v2_1()
)

check(
    "Architecture explanation identifies Phase 2.1",
    explanation[
        "phase"
    ]
    == "2.1",
)

check(
    "Architecture explanation identifies Workflow Registry",
    explanation[
        "component"
    ]
    == "Workflow Registry",
)

check(
    "Architecture explanation declares exact identity",
    explanation[
        "canonical_identity"
    ]
    == (
        "workflow_type",
        "workflow_version",
    ),
)


required_owns = (
    "workflow existence declaration",
    "exact-version registration",
    "exact-version lookup",
    "duplicate identity rejection",
    "immutable registry entries",
    "registry inspection",
)

for item in required_owns:

    check(
        f"Registry owns: {item}",
        item
        in explanation[
            "owns"
        ],
    )


required_exclusions = (
    "coordinator registration",
    "coordinator resolution",
    "stage ordering",
    "dependency graphs",
    "runnable-stage selection",
    "execution planning",
    "Runtime Registration",
    "runtime handlers",
    "runtime job creation",
    "workflow lifecycle state",
    "workflow execution state",
    "persistence",
    "latest-version selection",
    "workflow migration",
)

for item in required_exclusions:

    check(
        f"Registry excludes: {item}",
        item
        in explanation[
            "does_not_own"
        ],
    )


# ============================================================================
# 18. Static architecture boundary
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
}

check(
    "Workflow Registry imports only frozen Workflow Contract",
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
        "pipeline_coordinators"
    ),
    (
        "backend.server.coordination."
        "universal_stages"
    ),
    "fastapi",
    "sqlalchemy",
    "boto3",
    "requests",
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
    "Registry has no runtime/coordinator/stage execution imports",
    not violating_imports,
    json.dumps(
        violating_imports
    ),
)


# ============================================================================
# 19. Persistence prohibition
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
    "Workflow Registry performs no persistence or external I/O",
    not violating_io,
    json.dumps(
        violating_io
    ),
)


# ============================================================================
# 20. Authority prohibition
# ============================================================================

forbidden_authority_fragments = (
    "coordinator_id:",
    "coordinator_version:",
    "stage_id:",
    "stage_job_types:",
    "predecessor_stages:",
    "successor_stages:",
    "dependency_graph:",
    "retry_policy:",
    "handler_ref:",
    "job_id:",
    "next_stage:",
)

violating_authorities = [
    marker
    for marker
    in forbidden_authority_fragments
    if marker in source
]

check(
    "Workflow Registry owns no coordinator/stage/runtime/planning fields",
    not violating_authorities,
    json.dumps(
        violating_authorities
    ),
)


# ============================================================================
# 21. No premature version management
# ============================================================================

check(
    "Registry exposes no replace parameter",
    "replace=" not in source
    and "replace: bool" not in source,
)

check(
    "Registry exposes no latest-version resolver",
    "get_latest" not in source
    and "resolve_latest" not in source
    and "latest_workflow_version" not in source,
)

check(
    "Registry exposes no default-version resolver",
    "default_version" not in source,
)


# ============================================================================
# 22. Thread-safety foundation
# ============================================================================

check(
    "Registry has synchronization lock",
    "_REGISTRY_LOCK" in source
    and "RLock" in source,
)


# ============================================================================
# 23. SHA256
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
# 24. Final result
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
    "PHASE 2.1 WORKFLOW REGISTRY CERTIFICATION",
    "=" * 82,
    "",
    (
        "Registry Version: "
        + WORKFLOW_REGISTRY_VERSION
    ),
    (
        "Entry Schema: "
        + WORKFLOW_REGISTRY_ENTRY_SCHEMA_VERSION
    ),
    (
        "Workflow Contract: "
        + UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
    "Canonical Identity: workflow_type + workflow_version",
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
