from __future__ import annotations

import ast
import hashlib
import importlib
from dataclasses import fields
from pathlib import Path
from types import MappingProxyType

from backend.server.coordination.workflow_lifecycle.state_machine import (
    WORKFLOW_STATE_MACHINE_VERSION,
    workflow_states,
    terminal_workflow_states,
    transition_edges,
)

from backend.server.coordination.workflow_lifecycle.transition_validation import (
    TRANSITION_VALIDATION_VERSION,
)

from backend.server.coordination.workflow_lifecycle.lifecycle_history import (
    LIFECYCLE_HISTORY_VERSION,
    explain_lifecycle_history_v3_3,
)

from backend.server.coordination.workflow_lifecycle.terminal_state_protection import (
    TERMINAL_STATE_PROTECTION_VERSION,
)

from backend.server.coordination.workflow_lifecycle.lifecycle_certification import (
    LIFECYCLE_CERTIFICATION_VERSION,
    LIFECYCLE_CERTIFICATION_SCHEMA_VERSION,
    LIFECYCLE_CERTIFICATION_RESULT_FIELD_COUNT,
    WORKFLOW_STATE_MACHINE_SHA256,
    TRANSITION_VALIDATION_SHA256,
    LIFECYCLE_HISTORY_SHA256,
    TERMINAL_STATE_PROTECTION_SHA256,
    PHASE_3_COMPOSITE_FINGERPRINT,
    LifecycleCertificationResult,
    certify_workflow_lifecycle,
    workflow_lifecycle_certification_snapshot,
    explain_lifecycle_certification_v3_5,
)


ROOT = Path.cwd()

P31 = ROOT / (
    "backend/server/coordination/"
    "workflow_lifecycle/state_machine.py"
)

P32 = ROOT / (
    "backend/server/coordination/"
    "workflow_lifecycle/transition_validation.py"
)

P33 = ROOT / (
    "backend/server/coordination/"
    "workflow_lifecycle/lifecycle_history.py"
)

P34 = ROOT / (
    "backend/server/coordination/"
    "workflow_lifecycle/terminal_state_protection.py"
)

P35 = ROOT / (
    "backend/server/coordination/"
    "workflow_lifecycle/lifecycle_certification.py"
)

REPORT = ROOT / (
    "workflow_lifecycle_phase_3_5_final_recertification.txt"
)


EXPECTED_31 = (
    "144327A4E9C8989FCF0F4DBD10BCF6D"
    "7203F503930D81CB8E24644D86D2BB662"
)

EXPECTED_32 = (
    "69A952141E920E63B32B12AF1E9FB79D"
    "6296961FED40BCB94F007123BF9BD746"
)

EXPECTED_33 = (
    "D89F1D4FBC54307C7B8155E670CDD3C"
    "6C8771185DC8AFBE382A87BB34EDA8464"
)

EXPECTED_34 = (
    "7632A838D9CEAD7ED95DB0099D08FB20"
    "D01B4E2BD25BFF48D68CBEB89065A7B7"
)

EXPECTED_COMPOSITE = (
    "63A2038DF85AFC3BF621AAC13FEECF29"
    "F0B3E672E2B3590CF29401D3FB6790FE"
)

OLD_33 = (
    "739CD8D959F4176071FE7698D3098A1D"
    "C5DE23FF056D118F3DF32FEEDB79E5ED"
)

OLD_COMPOSITE = (
    "7EBEB4357A555A93BDE885922E561A7B8"
    "7AD1751CACDED5C10641C61A0BB778D"
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


def sha(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


print()
print("=" * 100)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 3.5 — WORKFLOW LIFECYCLE FINAL RE-CERTIFICATION")
print("=" * 100)


# ============================================================================
# 1. Canonical files
# ============================================================================

for phase, path in (
    ("3.1", P31),
    ("3.2", P32),
    ("3.3", P33),
    ("3.4", P34),
    ("3.5", P35),
):
    check(
        f"Phase {phase} canonical file exists",
        path.exists(),
        str(path.relative_to(ROOT)),
    )


# ============================================================================
# 2. Phase 3.5 syntax / import
# ============================================================================

source = P35.read_text(
    encoding="utf-8-sig"
)

try:
    tree = ast.parse(source)
    syntax_ok = True
except SyntaxError:
    tree = None
    syntax_ok = False

check(
    "Phase 3.5 Python syntax parses",
    syntax_ok,
)


try:
    importlib.import_module(
        "backend.server.coordination."
        "workflow_lifecycle.lifecycle_certification"
    )
    import_ok = True
except Exception:
    import_ok = False

check(
    "Phase 3.5 module imports successfully",
    import_ok,
)


# ============================================================================
# 3. Component identities
# ============================================================================

check(
    "3.1 version exact",
    WORKFLOW_STATE_MACHINE_VERSION
    == "workflow_state_machine_v3.1.0",
)

check(
    "3.2 version exact",
    TRANSITION_VALIDATION_VERSION
    == "transition_validation_v3.2.0",
)

check(
    "3.3 version exact",
    LIFECYCLE_HISTORY_VERSION
    == "lifecycle_history_v3.3.0",
)

check(
    "3.4 version exact",
    TERMINAL_STATE_PROTECTION_VERSION
    == "terminal_state_protection_v3.4.0",
)

check(
    "3.5 version exact",
    LIFECYCLE_CERTIFICATION_VERSION
    == "lifecycle_certification_v3.5.0",
)

check(
    "3.5 schema exact",
    LIFECYCLE_CERTIFICATION_SCHEMA_VERSION
    == "lifecycle_certification_schema_v1",
)

check(
    "3.5 result field-count constant exact",
    LIFECYCLE_CERTIFICATION_RESULT_FIELD_COUNT
    == 16,
)


# ============================================================================
# 4. Exact LifecycleCertificationResult contract
# ============================================================================

expected_result_fields = (
    "is_certified",
    "checks_run",
    "checks_passed",
    "checks_failed",
    "state_count",
    "terminal_state_count",
    "non_terminal_state_count",
    "transition_edge_count",
    "state_pair_count",
    "terminal_pair_count",
    "non_terminal_pair_count",
    "history_edge_count",
    "violations",
    "component_versions",
    "component_hashes",
    "certification_version",
)

actual_result_fields = tuple(
    field.name
    for field
    in fields(
        LifecycleCertificationResult
    )
)

check(
    "LifecycleCertificationResult has exactly 16 fields",
    len(actual_result_fields) == 16,
)

check(
    "LifecycleCertificationResult field order exact",
    actual_result_fields
    == expected_result_fields,
)


# ============================================================================
# 5. Disk hashes
# ============================================================================

actual_31 = sha(P31)
actual_32 = sha(P32)
actual_33 = sha(P33)
actual_34 = sha(P34)
actual_35 = sha(P35)

check(
    "Phase 3.1 SHA exact",
    actual_31 == EXPECTED_31,
    actual_31,
)

check(
    "Phase 3.2 SHA exact",
    actual_32 == EXPECTED_32,
    actual_32,
)

check(
    "Repaired Phase 3.3 SHA exact",
    actual_33 == EXPECTED_33,
    actual_33,
)

check(
    "Phase 3.4 SHA exact",
    actual_34 == EXPECTED_34,
    actual_34,
)


# ============================================================================
# 6. Embedded component hashes
# ============================================================================

check(
    "3.5 embedded Phase 3.1 SHA exact",
    WORKFLOW_STATE_MACHINE_SHA256
    == EXPECTED_31,
)

check(
    "3.5 embedded Phase 3.2 SHA exact",
    TRANSITION_VALIDATION_SHA256
    == EXPECTED_32,
)

check(
    "3.5 embedded repaired Phase 3.3 SHA exact",
    LIFECYCLE_HISTORY_SHA256
    == EXPECTED_33,
)

check(
    "3.5 embedded Phase 3.4 SHA exact",
    TERMINAL_STATE_PROTECTION_SHA256
    == EXPECTED_34,
)


check(
    "Embedded Phase 3.1 SHA matches disk",
    WORKFLOW_STATE_MACHINE_SHA256
    == actual_31,
)

check(
    "Embedded Phase 3.2 SHA matches disk",
    TRANSITION_VALIDATION_SHA256
    == actual_32,
)

check(
    "Embedded Phase 3.3 SHA matches disk",
    LIFECYCLE_HISTORY_SHA256
    == actual_33,
)

check(
    "Embedded Phase 3.4 SHA matches disk",
    TERMINAL_STATE_PROTECTION_SHA256
    == actual_34,
)


# ============================================================================
# 7. Composite fingerprint
# ============================================================================

independent_composite = hashlib.sha256(
    (
        actual_31
        + actual_32
        + actual_33
        + actual_34
    ).encode(
        "utf-8"
    )
).hexdigest().upper()


check(
    "Independent Phase-3 composite exact",
    independent_composite
    == EXPECTED_COMPOSITE,
    independent_composite,
)

check(
    "3.5 exported Phase-3 composite exact",
    PHASE_3_COMPOSITE_FINGERPRINT
    == EXPECTED_COMPOSITE,
)

check(
    "Exported composite equals independent disk computation",
    PHASE_3_COMPOSITE_FINGERPRINT
    == independent_composite,
)


# ============================================================================
# 8. No stale Phase 3.3 identity in production 3.5
# ============================================================================

check(
    "Old Phase 3.3 SHA absent from Phase 3.5 source",
    OLD_33 not in source.replace(
        '"',
        "",
    ).replace(
        "\n",
        "",
    ).replace(
        " ",
        "",
    ),
)

check(
    "Old composite fingerprint absent as hard-coded authority",
    OLD_COMPOSITE not in source.replace(
        '"',
        "",
    ).replace(
        "\n",
        "",
    ).replace(
        " ",
        "",
    ),
)


# ============================================================================
# 9. Canonical lifecycle counts
# ============================================================================

states = workflow_states()
terminals = terminal_workflow_states()
edges = transition_edges()

check(
    "Canonical workflow-state count is 10",
    len(states) == 10,
)

check(
    "Canonical terminal-state count is 4",
    len(terminals) == 4,
)

check(
    "Canonical non-terminal-state count is 6",
    len(states) - len(terminals) == 6,
)

check(
    "Canonical transition-edge count is 32",
    len(edges) == 32,
)

check(
    "Canonical ordered state-pair count is 100",
    len(states) * len(states) == 100,
)

check(
    "Terminal-current state-pair count is 40",
    len(terminals) * len(states) == 40,
)

check(
    "Non-terminal-current state-pair count is 60",
    (
        len(states)
        - len(terminals)
    )
    * len(states)
    == 60,
)


# ============================================================================
# 10. Built-in Phase-3 composite certification
# ============================================================================

result = certify_workflow_lifecycle()

check(
    "Certification returns LifecycleCertificationResult",
    isinstance(
        result,
        LifecycleCertificationResult,
    ),
)

check(
    "Built-in Phase-3 certification reports certified",
    result.is_certified is True,
)

check(
    "Built-in certification reports zero failures",
    result.checks_failed == 0,
)

check(
    "Built-in certification passed every check",
    result.checks_passed
    == result.checks_run,
)

check(
    "Built-in certification has no violations",
    result.violations == (),
)

check(
    "Built-in certification check count remains 330",
    result.checks_run == 330,
)

check(
    "Result state count exact",
    result.state_count == 10,
)

check(
    "Result terminal-state count exact",
    result.terminal_state_count == 4,
)

check(
    "Result non-terminal-state count exact",
    result.non_terminal_state_count == 6,
)

check(
    "Result transition-edge count exact",
    result.transition_edge_count == 32,
)

check(
    "Result state-pair count exact",
    result.state_pair_count == 100,
)

check(
    "Result terminal-pair count exact",
    result.terminal_pair_count == 40,
)

check(
    "Result non-terminal-pair count exact",
    result.non_terminal_pair_count == 60,
)

check(
    "Result history-edge count exact",
    result.history_edge_count == 32,
)


# ============================================================================
# 11. Result component identities
# ============================================================================

check(
    "Result component version 3.1 exact",
    result.component_versions["3.1"]
    == WORKFLOW_STATE_MACHINE_VERSION,
)

check(
    "Result component version 3.2 exact",
    result.component_versions["3.2"]
    == TRANSITION_VALIDATION_VERSION,
)

check(
    "Result component version 3.3 exact",
    result.component_versions["3.3"]
    == LIFECYCLE_HISTORY_VERSION,
)

check(
    "Result component version 3.4 exact",
    result.component_versions["3.4"]
    == TERMINAL_STATE_PROTECTION_VERSION,
)

check(
    "Result component version 3.5 exact",
    result.component_versions["3.5"]
    == LIFECYCLE_CERTIFICATION_VERSION,
)


check(
    "Result component hash 3.1 exact",
    result.component_hashes["3.1"]
    == EXPECTED_31,
)

check(
    "Result component hash 3.2 exact",
    result.component_hashes["3.2"]
    == EXPECTED_32,
)

check(
    "Result component hash 3.3 exact",
    result.component_hashes["3.3"]
    == EXPECTED_33,
)

check(
    "Result component hash 3.4 exact",
    result.component_hashes["3.4"]
    == EXPECTED_34,
)

check(
    "Result Phase-3 composite exact",
    result.component_hashes["phase_3_composite"]
    == EXPECTED_COMPOSITE,
)


# ============================================================================
# 12. Deep result immutability
# ============================================================================

result_mutation_blocked = False

try:
    result.checks_failed = 999
except Exception:
    result_mutation_blocked = True

check(
    "LifecycleCertificationResult is immutable",
    result_mutation_blocked,
)


component_versions_mutation_blocked = False

try:
    result.component_versions[
        "3.3"
    ] = "MUTATED"
except Exception:
    component_versions_mutation_blocked = True

check(
    "component_versions mapping immutable",
    component_versions_mutation_blocked,
)


component_hashes_mutation_blocked = False

try:
    result.component_hashes[
        "3.3"
    ] = "MUTATED"
except Exception:
    component_hashes_mutation_blocked = True

check(
    "component_hashes mapping immutable",
    component_hashes_mutation_blocked,
)


# ============================================================================
# 13. CRITICAL: repaired Phase 3.3 nested immutability
# ============================================================================

history_explanation = explain_lifecycle_history_v3_3()

check(
    "3.3 explanation remains immutable",
    isinstance(
        history_explanation,
        MappingProxyType,
    ),
)

future_authority = history_explanation[
    "future_authority"
]

check(
    "3.3 future_authority is MappingProxyType",
    isinstance(
        future_authority,
        MappingProxyType,
    ),
)

check(
    "3.3 future_authority 3.4 exact",
    future_authority["3.4"]
    == "Terminal-State Protection",
)

check(
    "3.3 future_authority 8.0 exact",
    future_authority["8.0"]
    == "Workflow State Persistence",
)

check(
    "3.3 future_authority 9.0 exact",
    future_authority["9.0"]
    == "Coordination Recovery",
)

check(
    "3.3 future_authority 10.5 exact",
    future_authority["10.5"]
    == "Audit Trail",
)


nested_mutation_blocked = False

try:
    future_authority[
        "3.4"
    ] = "MUTATED"
except Exception:
    nested_mutation_blocked = True

check(
    "3.3 future_authority nested mutation blocked",
    nested_mutation_blocked,
)


# ============================================================================
# 14. Snapshot
# ============================================================================

snapshot = workflow_lifecycle_certification_snapshot()

check(
    "3.5 snapshot is immutable mapping",
    isinstance(
        snapshot,
        MappingProxyType,
    ),
)

check(
    "Snapshot certification version exact",
    snapshot["certification_version"]
    == LIFECYCLE_CERTIFICATION_VERSION,
)

check(
    "Snapshot schema exact",
    snapshot["schema_version"]
    == LIFECYCLE_CERTIFICATION_SCHEMA_VERSION,
)

check(
    "Snapshot result field count exact",
    snapshot["result_field_count"]
    == 16,
)

check(
    "Snapshot certified",
    snapshot["is_certified"] is True,
)

check(
    "Snapshot failed-check count zero",
    snapshot["checks_failed"] == 0,
)

check(
    "Snapshot composite fingerprint exact",
    snapshot["composite_fingerprint"]
    == EXPECTED_COMPOSITE,
)


for key in (
    "workflow_mutation",
    "transition_execution",
    "history_mutation",
    "terminal_state_mutation",
    "durable_persistence",
    "runtime_execution",
    "recovery_execution",
    "coordinator_execution",
):
    check(
        f"Snapshot {key}=False",
        snapshot[key] is False,
    )


snapshot_mutation_blocked = False

try:
    snapshot[
        "is_certified"
    ] = False
except Exception:
    snapshot_mutation_blocked = True

check(
    "Snapshot mapping immutable",
    snapshot_mutation_blocked,
)


# ============================================================================
# 15. Architecture explanation
# ============================================================================

architecture = explain_lifecycle_certification_v3_5()

check(
    "3.5 architecture explanation immutable",
    isinstance(
        architecture,
        MappingProxyType,
    ),
)

check(
    "Architecture phase exact",
    architecture["phase"] == "3.5",
)

check(
    "Architecture component exact",
    architecture["component"]
    == "Lifecycle Certification",
)

check(
    "Architecture version exact",
    architecture["version"]
    == LIFECYCLE_CERTIFICATION_VERSION,
)

check(
    "Architecture schema exact",
    architecture["schema_version"]
    == LIFECYCLE_CERTIFICATION_SCHEMA_VERSION,
)

check(
    "Architecture composite fingerprint exact",
    architecture["composite_fingerprint"]
    == EXPECTED_COMPOSITE,
)


execution = architecture[
    "execution_properties"
]

check(
    "Architecture declares read-only",
    execution["read_only"] is True,
)

check(
    "Architecture declares deterministic",
    execution["deterministic"] is True,
)

check(
    "Architecture declares side-effect free",
    execution["side_effect_free"] is True,
)


# ============================================================================
# 16. Determinism
# ============================================================================

result_again = certify_workflow_lifecycle()

check(
    "Repeated certification deterministic",
    result_again
    == result,
)

snapshot_again = workflow_lifecycle_certification_snapshot()

check(
    "Repeated snapshot deterministic",
    dict(snapshot_again)
    == dict(snapshot),
)


# ============================================================================
# 17. Static imports / authority boundary
# ============================================================================

backend_imports = []

if tree is not None:

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
        "workflow_lifecycle.state_machine"
    ),
    (
        "backend.server.coordination."
        "workflow_lifecycle.transition_validation"
    ),
    (
        "backend.server.coordination."
        "workflow_lifecycle.lifecycle_history"
    ),
    (
        "backend.server.coordination."
        "workflow_lifecycle.terminal_state_protection"
    ),
}

check(
    "3.5 imports only Phase-3 lifecycle dependencies",
    set(
        backend_imports
    ).issubset(
        allowed_backend_imports
    ),
    repr(
        backend_imports
    ),
)


forbidden_import_fragments = (
    ".runtime",
    "workflow_registry",
    "coordinator_registry",
    "registration_validation",
    "version_management",
    "dependency_planning",
)

bad_imports = [
    item
    for item
    in backend_imports
    if any(
        fragment in item
        for fragment
        in forbidden_import_fragments
    )
]

check(
    "3.5 has no Runtime/registry/planning imports",
    not bad_imports,
    repr(
        bad_imports
    ),
)


# ============================================================================
# 18. No hidden execution / persistence / random generation
# ============================================================================

forbidden_calls = {
    "uuid4",
    "uuid1",
    "now",
    "utcnow",
    "dispatch",
    "enqueue",
    "execute",
    "commit",
    "save",
    "register_workflow",
    "register_coordinator",
}

bad_calls = []

if tree is not None:

    for node in ast.walk(tree):

        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        func = node.func

        if isinstance(
            func,
            ast.Name,
        ):
            name = func.id

        elif isinstance(
            func,
            ast.Attribute,
        ):
            name = func.attr

        else:
            continue

        if name in forbidden_calls:
            bad_calls.append(
                name
            )


check(
    "3.5 performs no hidden execution/persistence/random generation",
    not bad_calls,
    repr(
        bad_calls
    ),
)


# ============================================================================
# 19. Final Phase 3.5 SHA
# ============================================================================

print()
print(
    "PHASE 3.5 SHA256 CANDIDATE:"
)
print(
    actual_35
)

check(
    "Phase 3.5 SHA matches post-patch candidate",
    actual_35
    == (
        "0A1F2BCFFCFFC56AC96F7383AF3ACCEA"
        "61314952D59CC0CC8A58B1FA0B9060DF"
    ),
    actual_35,
)


# ============================================================================
# FINAL RESULT / REPORT
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


report = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 3.5 — WORKFLOW LIFECYCLE FINAL RE-CERTIFICATION",
    "=" * 100,
    "",
    (
        "Lifecycle Certification Version: "
        + LIFECYCLE_CERTIFICATION_VERSION
    ),
    (
        "Lifecycle Certification Schema: "
        + LIFECYCLE_CERTIFICATION_SCHEMA_VERSION
    ),
    "",
    "Phase 3.1 SHA256: " + actual_31,
    "Phase 3.2 SHA256: " + actual_32,
    "Phase 3.3 SHA256: " + actual_33,
    "Phase 3.4 SHA256: " + actual_34,
    "Phase 3.5 SHA256: " + actual_35,
    "",
    (
        "Phase 3.0 Composite Fingerprint: "
        + independent_composite
    ),
    "",
    f"Checks: {len(checks)}",
    f"Passed: {passed}",
    f"Failed: {failed}",
    "",
    (
        "STATUS: CERTIFICATION PASSED"
        if failed == 0
        else "STATUS: CERTIFICATION FAILED"
    ),
    "",
]


for name, ok, detail in checks:

    report.append(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        report.append(
            "    " + detail
        )


REPORT.write_text(
    "\n".join(
        report
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 100)
print("PHASE 3.5 FINAL RE-CERTIFICATION RESULT")
print("=" * 100)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print(
    "STATUS:",
    (
        "CERTIFICATION PASSED"
        if failed == 0
        else "CERTIFICATION FAILED"
    ),
)
print(
    "PHASE 3 COMPOSITE:",
    independent_composite,
)
print(
    "PHASE 3.5 SHA256:",
    actual_35,
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 100)


raise SystemExit(
    0
    if failed == 0
    else 1
)
