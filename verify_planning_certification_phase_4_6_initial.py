from __future__ import annotations

import ast
import hashlib
import importlib
from dataclasses import fields
from pathlib import Path
from types import MappingProxyType

import backend.server.coordination.dependency_planning.planning_certification as pc

from backend.server.coordination.dependency_planning.planning_certification import (
    PLANNING_CERTIFICATION_VERSION,
    PLANNING_CERTIFICATION_SCHEMA_VERSION,
    PLANNING_CERTIFICATION_CHECK_FIELD_COUNT,
    PLANNING_CERTIFICATION_RESULT_FIELD_COUNT,
    PLANNING_CERTIFICATION_DEEP_CHAIN_NODE_COUNT,
    EXPECTED_COMPONENT_VERSIONS,
    EXPECTED_COMPONENT_SHAS,
    PlanningCertificationError,
    PlanningCertificationFailedError,
    PlanningCertificationCheck,
    PlanningCertificationResult,
    certify_dependency_planning,
    planning_certification_snapshot,
    explain_planning_certification_v4_6,
)


ROOT = Path.cwd()

PACKAGE = ROOT / (
    "backend/server/coordination/"
    "dependency_planning"
)

FILES = {
    "4.1": PACKAGE / "dependency_graph.py",
    "4.2": PACKAGE / "dependency_validation.py",
    "4.3": PACKAGE / "cycle_detection.py",
    "4.4": PACKAGE / "runnable_stage_resolver.py",
    "4.5": PACKAGE / "execution_planner.py",
    "4.6": PACKAGE / "planning_certification.py",
}

EXPECTED_SHAS = {
    "4.1":
        "4F6BA62D011C31D9D851FBBABC37C12B"
        "7DDAA1FD9A91E34788EBCE25741A1F70",

    "4.2":
        "1D053C0036EA9F7A8AEDFAFC36F6EB82"
        "A681EDC7EF206409E9FFB8C7F212852D",

    "4.3":
        "E77BF605724F991E85C7FE2E5329051E"
        "16ECB2F30ACDAEA8AA40A2FD47487CEA",

    "4.4":
        "2779D432A2F3337F3557C61664499669"
        "CC852773AB74447297E98D6188289483",

    "4.5":
        "808743F566978530B2FC774DBD70A5FFA"
        "820F0EFE431512E882E0CF0F7B81958",

    "4.6":
        "8DB96F931C4C3B4F35C308400D838D18"
        "BA67E22ACAC08D5597394D29B9FD5723",
}

EXPECTED_COMPOSITE = (
    "E14A56652D850362C909DC4782A893F9"
    "A8AE891472E38F96EF76462916240B65"
)

REPORT = ROOT / (
    "planning_certification_phase_4_6_initial_verification.txt"
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


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


print()
print("=" * 108)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 4.6 — PLANNING CERTIFICATION INITIAL VERIFICATION")
print("=" * 108)


# =============================================================================
# Files / syntax / imports
# =============================================================================

for phase, path in FILES.items():
    check(
        f"Phase {phase} canonical file exists",
        path.exists(),
        str(
            path.relative_to(ROOT)
        ),
    )


source = FILES[
    "4.6"
].read_text(
    encoding="utf-8-sig"
)

try:
    tree = ast.parse(
        source
    )
    syntax_ok = True

except Exception:
    tree = None
    syntax_ok = False

check(
    "Phase 4.6 Python syntax parses",
    syntax_ok,
)

try:
    importlib.import_module(
        "backend.server.coordination."
        "dependency_planning.planning_certification"
    )
    import_ok = True
    import_detail = ""

except Exception as exc:
    import_ok = False
    import_detail = repr(
        exc
    )

check(
    "Phase 4.6 module imports successfully",
    import_ok,
    import_detail,
)


# =============================================================================
# Exact SHA authority
# =============================================================================

actual_shas = {}

for phase, path in FILES.items():
    actual = sha256(
        path
    )

    actual_shas[
        phase
    ] = actual

    check(
        f"Phase {phase} SHA exact",
        actual
        == EXPECTED_SHAS[
            phase
        ],
        actual,
    )


# =============================================================================
# Identity / contracts
# =============================================================================

check(
    "Planning Certification version exact",
    PLANNING_CERTIFICATION_VERSION
    == "planning_certification_v4.6.0",
)

check(
    "Planning Certification schema exact",
    PLANNING_CERTIFICATION_SCHEMA_VERSION
    == "planning_certification_schema_v1",
)

check(
    "Certification check field-count constant exact",
    PLANNING_CERTIFICATION_CHECK_FIELD_COUNT
    == 3,
)

check(
    "Certification result field-count constant exact",
    PLANNING_CERTIFICATION_RESULT_FIELD_COUNT
    == 16,
)

check(
    "Deep-chain node count exact",
    PLANNING_CERTIFICATION_DEEP_CHAIN_NODE_COUNT
    == 2500,
)

check(
    "PlanningCertificationCheck exact fields",
    tuple(
        field.name
        for field
        in fields(
            PlanningCertificationCheck
        )
    )
    == (
        "name",
        "passed",
        "detail",
    ),
)

check(
    "PlanningCertificationResult exact fields",
    tuple(
        field.name
        for field
        in fields(
            PlanningCertificationResult
        )
    )
    == (
        "is_certified",
        "check_count",
        "passed_check_count",
        "failed_check_count",
        "failed_checks",
        "checks",
        "component_shas",
        "composite_fingerprint",
        "dependency_graph_version",
        "dependency_validation_version",
        "cycle_detection_version",
        "runnable_stage_resolver_version",
        "execution_planner_version",
        "deep_chain_node_count",
        "certification_version",
        "schema_version",
    ),
)


# =============================================================================
# Embedded frozen authority
# =============================================================================

check(
    "Expected component versions immutable",
    isinstance(
        EXPECTED_COMPONENT_VERSIONS,
        MappingProxyType,
    ),
)

check(
    "Expected component SHAs immutable",
    isinstance(
        EXPECTED_COMPONENT_SHAS,
        MappingProxyType,
    ),
)

for phase in (
    "4.1",
    "4.2",
    "4.3",
    "4.4",
    "4.5",
):
    check(
        f"Embedded Phase {phase} SHA authority exact",
        EXPECTED_COMPONENT_SHAS[
            phase
        ]
        == EXPECTED_SHAS[
            phase
        ],
    )


# =============================================================================
# Successful certification
# =============================================================================

result = (
    certify_dependency_planning()
)

check(
    "Certification result type exact",
    isinstance(
        result,
        PlanningCertificationResult,
    ),
)

check(
    "Certification succeeds",
    result.is_certified,
)

check(
    "Certification failed count zero",
    result.failed_check_count
    == 0,
)

check(
    "Certification failed checks empty",
    result.failed_checks
    == (),
)

check(
    "Passed count equals total count",
    result.passed_check_count
    == result.check_count,
)

check(
    "Certification contains checks",
    result.check_count
    > 0,
)

check(
    "All embedded certification checks pass",
    all(
        item.passed
        for item
        in result.checks
    ),
)


# =============================================================================
# Exact component SHAs in result
# =============================================================================

check(
    "Result component SHA mapping immutable",
    isinstance(
        result.component_shas,
        MappingProxyType,
    ),
)

for phase in (
    "4.1",
    "4.2",
    "4.3",
    "4.4",
    "4.5",
):
    check(
        f"Result Phase {phase} SHA exact",
        result.component_shas[
            phase
        ]
        == EXPECTED_SHAS[
            phase
        ],
    )


# =============================================================================
# Composite fingerprint
# =============================================================================

check(
    "Composite fingerprint exact",
    result.composite_fingerprint
    == EXPECTED_COMPOSITE,
    result.composite_fingerprint,
)

check(
    "Composite fingerprint SHA256 length",
    len(
        result.composite_fingerprint
    )
    == 64,
)

check(
    "Composite fingerprint uppercase hexadecimal",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in result.composite_fingerprint
    ),
)


# =============================================================================
# Deep-chain regression evidence
# =============================================================================

deep_checks = tuple(
    item
    for item
    in result.checks
    if item.name
    == "2500-stage deep chain is acyclic"
)

check(
    "Deep-chain regression check present exactly once",
    len(
        deep_checks
    )
    == 1,
)

if deep_checks:
    check(
        "Deep-chain regression check passes",
        deep_checks[
            0
        ].passed,
    )


check(
    "Result deep-chain count exact",
    result.deep_chain_node_count
    == 2500,
)


# =============================================================================
# Cross-component certification evidence
# =============================================================================

required_certification_checks = (
    "Canonical graph passes Phase 4.2 validation",
    "Canonical graph is acyclic",
    "Initial runnable roots exact",
    "Initial blocked join exact",
    "Initial execution wave exact",
    "Parallel roots remain one wave",
    "Join becomes runnable after prerequisites complete",
    "Join execution wave exact",
    "Directed cycle detected",
    "2500-stage deep chain is acyclic",
    "Runnability certification deterministic",
    "Planning certification deterministic",
    "Composite fingerprint is SHA256",
)

result_check_names = tuple(
    item.name
    for item
    in result.checks
)

for name in required_certification_checks:
    check(
        f"Certification evidence present: {name}",
        name
        in result_check_names,
    )


# =============================================================================
# Result immutability
# =============================================================================

blocked = False

try:
    result.is_certified = False

except Exception:
    blocked = True

check(
    "PlanningCertificationResult immutable",
    blocked,
)

blocked = False

try:
    result.checks[
        0
    ].passed = False

except Exception:
    blocked = True

check(
    "Nested PlanningCertificationCheck immutable",
    blocked,
)

result_map = (
    result.to_dict()
)

check(
    "Result to_dict immutable",
    isinstance(
        result_map,
        MappingProxyType,
    ),
)

check(
    "Result serialized checks tuple",
    isinstance(
        result_map[
            "checks"
        ],
        tuple,
    ),
)

check(
    "Result nested check mapping immutable",
    isinstance(
        result_map[
            "checks"
        ][0],
        MappingProxyType,
    ),
)

blocked = False

try:
    result_map[
        "component_shas"
    ][
        "4.1"
    ] = "BAD"

except Exception:
    blocked = True

check(
    "Result deep mapping mutation blocked",
    blocked,
)


# =============================================================================
# Snapshot
# =============================================================================

snapshot = (
    planning_certification_snapshot()
)

check(
    "Snapshot MappingProxyType",
    isinstance(
        snapshot,
        MappingProxyType,
    ),
)

check(
    "Snapshot certified exact",
    snapshot[
        "is_certified"
    ] is True,
)

check(
    "Snapshot version exact",
    snapshot[
        "certification_version"
    ]
    == PLANNING_CERTIFICATION_VERSION,
)

check(
    "Snapshot schema exact",
    snapshot[
        "schema_version"
    ]
    == PLANNING_CERTIFICATION_SCHEMA_VERSION,
)

check(
    "Snapshot composite fingerprint exact",
    snapshot[
        "composite_fingerprint"
    ]
    == EXPECTED_COMPOSITE,
)

check(
    "Snapshot nested checks tuple",
    isinstance(
        snapshot[
            "checks"
        ],
        tuple,
    ),
)

check(
    "Snapshot nested check immutable",
    isinstance(
        snapshot[
            "checks"
        ][0],
        MappingProxyType,
    ),
)


# =============================================================================
# Architecture
# =============================================================================

architecture = (
    explain_planning_certification_v4_6()
)

check(
    "Architecture MappingProxyType",
    isinstance(
        architecture,
        MappingProxyType,
    ),
)

check(
    "Architecture phase exact",
    architecture[
        "phase"
    ]
    == "4.6",
)

check(
    "Architecture component exact",
    architecture[
        "component"
    ]
    == "Planning Certification",
)

check(
    "Architecture version exact",
    architecture[
        "version"
    ]
    == PLANNING_CERTIFICATION_VERSION,
)

check(
    "Architecture schema exact",
    architecture[
        "schema_version"
    ]
    == PLANNING_CERTIFICATION_SCHEMA_VERSION,
)

check(
    "Certification scope exact",
    architecture[
        "certification_scope"
    ]
    == (
        "frozen Phase 4.1 through "
        "Phase 4.5 dependency/planning chain"
    ),
)

check(
    "Fingerprint excludes Phase 4.6",
    architecture[
        "fingerprint_policy"
    ][
        "includes_phase_4_6"
    ] is False,
)

check(
    "Fingerprint algorithm SHA256",
    architecture[
        "fingerprint_policy"
    ][
        "algorithm"
    ]
    == "SHA256",
)

check(
    "Certification fail closed",
    architecture[
        "failure_policy"
    ][
        "mode"
    ]
    == "fail_closed",
)

check(
    "Failure exception exact",
    architecture[
        "failure_policy"
    ][
        "exception"
    ]
    == "PlanningCertificationFailedError",
)

check(
    "Deep-chain architecture count exact",
    architecture[
        "deep_chain_policy"
    ][
        "node_count"
    ]
    == 2500,
)


# =============================================================================
# Execution boundaries
# =============================================================================

properties = architecture[
    "execution_properties"
]

for key in (
    "graph_mutation",
    "workflow_mutation",
    "runtime_execution",
    "runtime_job_creation",
    "dispatch",
    "persistence",
    "recovery",
):
    check(
        f"Execution property disabled: {key}",
        properties[
            key
        ] is False,
    )

check(
    "Execution property read_only true",
    properties[
        "read_only"
    ] is True,
)

check(
    "Execution property deterministic true",
    properties[
        "deterministic"
    ] is True,
)


# =============================================================================
# Determinism
# =============================================================================

second = (
    certify_dependency_planning()
)

check(
    "Repeated certification deterministic",
    second
    == result,
)

check(
    "Repeated certification check tuple deterministic",
    second.checks
    == result.checks,
)

check(
    "Repeated component SHAs deterministic",
    dict(
        second.component_shas
    )
    == dict(
        result.component_shas
    ),
)

check(
    "Repeated fingerprint deterministic",
    second.composite_fingerprint
    == EXPECTED_COMPOSITE,
)

check(
    "Repeated snapshot deterministic",
    dict(
        planning_certification_snapshot()
    )
    == dict(
        snapshot
    ),
)

check(
    "Repeated architecture deterministic",
    dict(
        explain_planning_certification_v4_6()
    )
    == dict(
        architecture
    ),
)


# =============================================================================
# Fail-closed behavior
# =============================================================================

original_expected_shas = (
    pc.EXPECTED_COMPONENT_SHAS
)

try:
    pc.EXPECTED_COMPONENT_SHAS = MappingProxyType(
        {
            **dict(
                original_expected_shas
            ),
            "4.1": "0" * 64,
        }
    )

    fail_closed = False
    preserved_result = False

    try:
        pc.certify_dependency_planning()

    except PlanningCertificationFailedError as exc:
        fail_closed = True

        preserved_result = (
            isinstance(
                exc.result,
                PlanningCertificationResult,
            )
            and not exc.result.is_certified
            and exc.result.failed_check_count
            >= 1
            and (
                "Frozen Phase 4.1 SHA exact"
                in exc.result.failed_checks
            )
        )

    check(
        "Certification fails closed on SHA mismatch",
        fail_closed,
    )

    check(
        "Certification failure preserves complete result",
        preserved_result,
    )

finally:
    pc.EXPECTED_COMPONENT_SHAS = (
        original_expected_shas
    )


check(
    "Certification recovers after test authority restored",
    certify_dependency_planning().is_certified,
)


# =============================================================================
# Static imports
# =============================================================================

backend_imports = []

if tree is not None:

    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.ImportFrom,
        ):
            module = node.module or ""

            if module.startswith(
                "backend."
            ):
                backend_imports.append(
                    module
                )

        elif isinstance(
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


allowed_imports = {
    (
        "backend.server.coordination."
        "dependency_planning.dependency_graph"
    ),
    (
        "backend.server.coordination."
        "dependency_planning.dependency_validation"
    ),
    (
        "backend.server.coordination."
        "dependency_planning.cycle_detection"
    ),
    (
        "backend.server.coordination."
        "dependency_planning.runnable_stage_resolver"
    ),
    (
        "backend.server.coordination."
        "dependency_planning.execution_planner"
    ),
}

check(
    "4.6 imports only Phase 4.1-4.5 production components",
    set(
        backend_imports
    ).issubset(
        allowed_imports
    ),
    repr(
        sorted(
            set(
                backend_imports
            )
        )
    ),
)


# =============================================================================
# Static forbidden authority
# =============================================================================

forbidden_calls = {
    "dispatch",
    "dispatch_job",
    "enqueue",
    "enqueue_job",
    "submit_job",
    "create_job",
    "register",
    "register_workflow",
    "register_coordinator",
    "select_worker",
    "save",
    "persist",
    "commit",
    "checkpoint",
    "pause",
    "resume",
    "recover",
}

bad_calls = []

if tree is not None:

    for node in ast.walk(
        tree
    ):

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
    "4.6 performs no Runtime/dispatch/persistence/recovery authority",
    not bad_calls,
    repr(
        bad_calls
    ),
)


# =============================================================================
# Source architecture markers
# =============================================================================

source_markers = (
    (
        "Source declares Phase 4.1-4.5 certification",
        "Phase 4.6 certifies the frozen Phase 4.1",
    ),
    (
        "Source declares read-only",
        "read-only",
    ),
    (
        "Source declares deterministic",
        "deterministic",
    ),
    (
        "Source declares Runtime independent",
        "Runtime independent",
    ),
    (
        "Source declares dispatch free",
        "dispatch free",
    ),
    (
        "Source declares persistence free",
        "persistence free",
    ),
    (
        "Source declares fail closed",
        "fail closed",
    ),
    (
        "Source excludes own SHA from composite",
        "intentionally excluded from its own",
    ),
)

for name, marker in source_markers:
    check(
        name,
        marker
        in source,
    )


# =============================================================================
# Candidate SHA remains exact
# =============================================================================

check(
    "Phase 4.6 candidate SHA unchanged",
    sha256(
        FILES[
            "4.6"
        ]
    )
    == EXPECTED_SHAS[
        "4.6"
    ],
    sha256(
        FILES[
            "4.6"
        ]
    ),
)


# =============================================================================
# Final
# =============================================================================

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
    "PHASE 4.6 — PLANNING CERTIFICATION INITIAL VERIFICATION",
    "=" * 108,
    "",
    (
        "Planning Certification Version: "
        + PLANNING_CERTIFICATION_VERSION
    ),
    (
        "Planning Certification Schema: "
        + PLANNING_CERTIFICATION_SCHEMA_VERSION
    ),
    "",
]

for phase in (
    "4.1",
    "4.2",
    "4.3",
    "4.4",
    "4.5",
    "4.6",
):
    report_lines.append(
        f"Phase {phase} SHA256: "
        + actual_shas[
            phase
        ]
    )

report_lines.extend(
    (
        "",
        (
            "Phase 4 Composite Fingerprint: "
            + result.composite_fingerprint
        ),
        "",
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        "",
        (
            "STATUS: VERIFICATION PASSED"
            if failed == 0
            else "STATUS: VERIFICATION FAILED"
        ),
        "",
    )
)

for name, ok, detail in checks:
    report_lines.append(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        report_lines.append(
            "    " + detail
        )


REPORT.write_text(
    "\n".join(
        report_lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 108)
print("PHASE 4.6 INITIAL VERIFICATION RESULT")
print("=" * 108)
print(
    "Checks:",
    len(
        checks
    ),
)
print(
    "Passed:",
    passed,
)
print(
    "Failed:",
    failed,
)
print(
    "STATUS:",
    (
        "VERIFICATION PASSED"
        if failed == 0
        else "VERIFICATION FAILED"
    ),
)
print(
    "COMPOSITE FINGERPRINT:",
    result.composite_fingerprint,
)
print(
    "PHASE 4.6 SHA256:",
    actual_shas[
        "4.6"
    ],
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 108)


raise SystemExit(
    0
    if failed == 0
    else 1
)
