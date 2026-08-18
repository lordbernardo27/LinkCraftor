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
    "planning_certification_phase_4_6_final_certification.txt"
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
print("=" * 112)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 4.6 — PLANNING CERTIFICATION FINAL CERTIFICATION")
print("=" * 112)


# =============================================================================
# Canonical source integrity
# =============================================================================

for phase, path in FILES.items():

    check(
        f"Frozen Phase {phase} file exists",
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
    "Phase 4.6 syntax parses",
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
# Exact SHA freeze candidates
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
# Identity and schema
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
    "PlanningCertificationCheck exact field contract",
    tuple(
        item.name
        for item
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
    "PlanningCertificationResult exact field contract",
    tuple(
        item.name
        for item
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
# Embedded authority
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
        f"Embedded Phase {phase} SHA exact",
        EXPECTED_COMPONENT_SHAS[
            phase
        ]
        == EXPECTED_SHAS[
            phase
        ],
    )


# =============================================================================
# Canonical certification execution
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
    "Phase 4 certification succeeds",
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
    "Certification passed count equals total",
    result.passed_check_count
    == result.check_count,
)

check(
    "Every internal certification check passes",
    all(
        item.passed
        for item
        in result.checks
    ),
)


# =============================================================================
# Frozen component SHA result authority
# =============================================================================

check(
    "Result component SHAs immutable",
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
        f"Certified Phase {phase} SHA exact",
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
    "Phase 4 composite fingerprint exact",
    result.composite_fingerprint
    == EXPECTED_COMPOSITE,
    result.composite_fingerprint,
)

check(
    "Composite fingerprint length exact",
    len(
        result.composite_fingerprint
    )
    == 64,
)

check(
    "Composite fingerprint uppercase hexadecimal",
    all(
        ch
        in "0123456789ABCDEF"
        for ch
        in result.composite_fingerprint
    ),
)


# =============================================================================
# Required internal evidence
# =============================================================================

required_checks = (
    "Frozen Phase 4.1 SHA exact",
    "Frozen Phase 4.2 SHA exact",
    "Frozen Phase 4.3 SHA exact",
    "Frozen Phase 4.4 SHA exact",
    "Frozen Phase 4.5 SHA exact",
    "Phase 4.1 version exact",
    "Phase 4.2 version exact",
    "Phase 4.3 version exact",
    "Phase 4.4 version exact",
    "Phase 4.5 version exact",
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


names = tuple(
    item.name
    for item
    in result.checks
)


for name in required_checks:

    matches = tuple(
        item
        for item
        in result.checks
        if item.name
        == name
    )

    check(
        f"Required certification evidence exactly once: {name}",
        len(
            matches
        )
        == 1,
    )

    if matches:

        check(
            f"Required certification evidence passes: {name}",
            matches[
                0
            ].passed,
        )


# =============================================================================
# Deep-chain regression freeze
# =============================================================================

check(
    "Deep-chain certification node count exact",
    result.deep_chain_node_count
    == 2500,
)


deep = tuple(
    item
    for item
    in result.checks
    if item.name
    == "2500-stage deep chain is acyclic"
)


check(
    "Deep-chain regression certification exactly once",
    len(
        deep
    )
    == 1,
)

if deep:

    check(
        "Deep-chain regression certification passes",
        deep[
            0
        ].passed,
    )


# =============================================================================
# Result and nested immutability
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
    ].detail = "mutated"

except Exception:
    blocked = True


check(
    "Nested certification check immutable",
    blocked,
)


mapping = (
    result.to_dict()
)


check(
    "Result mapping immutable",
    isinstance(
        mapping,
        MappingProxyType,
    ),
)


check(
    "Result checks serialized tuple",
    isinstance(
        mapping[
            "checks"
        ],
        tuple,
    ),
)


check(
    "Result nested check mapping immutable",
    isinstance(
        mapping[
            "checks"
        ][0],
        MappingProxyType,
    ),
)


check(
    "Result nested component SHAs immutable",
    isinstance(
        mapping[
            "component_shas"
        ],
        MappingProxyType,
    ),
)


blocked = False

try:
    mapping[
        "component_shas"
    ][
        "4.3"
    ] = "BAD"

except Exception:
    blocked = True


check(
    "Result deep mutation blocked",
    blocked,
)


# =============================================================================
# Snapshot certification
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
    "Snapshot check count exact",
    snapshot[
        "check_count"
    ]
    == result.check_count,
)

check(
    "Snapshot passed count exact",
    snapshot[
        "passed_check_count"
    ]
    == result.passed_check_count,
)

check(
    "Snapshot failed count exact",
    snapshot[
        "failed_check_count"
    ]
    == 0,
)

check(
    "Snapshot nested checks tuple immutable",
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
# Architecture freeze
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


owns = architecture[
    "owns"
]


for ownership in (
    "exact frozen Phase 4.1-4.5 SHA verification",
    "exact Phase 4.1-4.5 version verification",
    "cross-component planning-chain certification",
    "cycle-detection certification",
    "deep-chain regression certification",
    "runnability certification",
    "immediate-wave planning certification",
    "deterministic certification evidence",
    "Phase 4 composite fingerprint",
    "fail-closed certification",
    "immutable certification snapshot",
):

    check(
        f"Architecture owns: {ownership}",
        ownership
        in owns,
    )


does_not_own = architecture[
    "does_not_own"
]


for excluded in (
    "dependency graph construction semantics",
    "dependency semantic validation semantics",
    "cycle detection semantics",
    "runnable-stage semantics",
    "execution planning semantics",
    "topological full-workflow planning",
    "Runtime Registration",
    "Runtime jobs",
    "Runtime dispatch",
    "worker selection",
    "stage result handoff",
    "advanced orchestration",
    "workflow persistence",
    "workflow recovery",
):

    check(
        f"Architecture excludes: {excluded}",
        excluded
        in does_not_own,
    )


check(
    "Fingerprint algorithm exact",
    architecture[
        "fingerprint_policy"
    ][
        "algorithm"
    ]
    == "SHA256",
)

check(
    "Fingerprint covers 4.1-4.5 exact",
    architecture[
        "fingerprint_policy"
    ][
        "covers"
    ]
    == (
        "Phase 4.1-4.5 production "
        "source SHAs and versions"
    ),
)

check(
    "Phase 4.6 excluded from own composite",
    architecture[
        "fingerprint_policy"
    ][
        "includes_phase_4_6"
    ] is False,
)

check(
    "Fingerprint exclusion reason exact",
    architecture[
        "fingerprint_policy"
    ][
        "reason_phase_4_6_excluded"
    ]
    == (
        "avoid self-referential "
        "certification hash"
    ),
)


check(
    "Failure policy fail closed",
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


# =============================================================================
# Execution authority boundaries
# =============================================================================

properties = architecture[
    "execution_properties"
]


for name in (
    "graph_mutation",
    "workflow_mutation",
    "runtime_execution",
    "runtime_job_creation",
    "dispatch",
    "persistence",
    "recovery",
):

    check(
        f"Execution authority disabled: {name}",
        properties[
            name
        ] is False,
    )


check(
    "Execution property read-only exact",
    properties[
        "read_only"
    ] is True,
)

check(
    "Execution property deterministic exact",
    properties[
        "deterministic"
    ] is True,
)


# =============================================================================
# Future authority boundaries
# =============================================================================

future = architecture[
    "future_authority"
]


check(
    "Runtime Integration deferred to Phase 5",
    future[
        "5.0"
    ]
    == "Runtime Integration",
)

check(
    "Stage Handoff deferred to Phase 6",
    future[
        "6.0"
    ]
    == "Stage Handoff",
)

check(
    "Advanced Orchestration deferred to Phase 7",
    future[
        "7.0"
    ]
    == "Advanced Orchestration",
)

check(
    "Persistence deferred to Phase 8",
    future[
        "8.0"
    ]
    == "Workflow State Persistence",
)

check(
    "Recovery deferred to Phase 9",
    future[
        "9.0"
    ]
    == "Coordination Recovery",
)


# =============================================================================
# Determinism certification
# =============================================================================

second = (
    certify_dependency_planning()
)

third = (
    certify_dependency_planning()
)


check(
    "Repeated certification #2 deterministic",
    second
    == result,
)

check(
    "Repeated certification #3 deterministic",
    third
    == result,
)

check(
    "Repeated internal evidence deterministic",
    second.checks
    == third.checks
    == result.checks,
)

check(
    "Repeated composite fingerprint deterministic",
    second.composite_fingerprint
    == third.composite_fingerprint
    == EXPECTED_COMPOSITE,
)

check(
    "Repeated snapshots deterministic",
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
# Fail-closed corruption verification
# =============================================================================

original = (
    pc.EXPECTED_COMPONENT_SHAS
)


try:

    corrupted = dict(
        original
    )

    corrupted[
        "4.3"
    ] = (
        "F" * 64
    )

    pc.EXPECTED_COMPONENT_SHAS = (
        MappingProxyType(
            corrupted
        )
    )

    raised = False
    preserved = False
    exact_failure = False

    try:
        pc.certify_dependency_planning()

    except PlanningCertificationFailedError as exc:

        raised = True

        preserved = isinstance(
            exc.result,
            PlanningCertificationResult,
        )

        exact_failure = (
            not exc.result.is_certified
            and exc.result.failed_check_count
            >= 1
            and (
                "Frozen Phase 4.3 SHA exact"
                in exc.result.failed_checks
            )
        )

    check(
        "Corrupted Phase 4.3 SHA fails closed",
        raised,
    )

    check(
        "Fail-closed exception preserves certification result",
        preserved,
    )

    check(
        "Fail-closed result identifies Phase 4.3 SHA failure",
        exact_failure,
    )

finally:

    pc.EXPECTED_COMPONENT_SHAS = (
        original
    )


check(
    "Certification succeeds after authority restoration",
    certify_dependency_planning().is_certified,
)


# =============================================================================
# Static import boundary
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


allowed = {
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
    "4.6 imports only frozen Phase 4.1-4.5 components",
    set(
        backend_imports
    ).issubset(
        allowed
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
    "compensate",
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
    "4.6 performs no Runtime/dispatch/persistence/recovery execution",
    not bad_calls,
    repr(
        bad_calls
    ),
)


# =============================================================================
# Public API boundary
# =============================================================================

public_names = tuple(
    name
    for name
    in pc.__all__
)


check(
    "Public API contains certification function",
    "certify_dependency_planning"
    in public_names,
)

check(
    "Public API contains certification snapshot",
    "planning_certification_snapshot"
    in public_names,
)

check(
    "Public API contains architecture explanation",
    "explain_planning_certification_v4_6"
    in public_names,
)


for forbidden_public in (
    "dispatch",
    "create_job",
    "execute_stage",
    "resolve_runnable_stages",
    "create_execution_plan",
    "persist",
    "recover",
):

    check(
        f"Public API excludes authority: {forbidden_public}",
        forbidden_public
        not in public_names,
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
        "Source excludes itself from composite fingerprint",
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
# Final freeze candidate integrity
# =============================================================================

check(
    "Phase 4.6 SHA remains final freeze candidate",
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


check(
    "Phase 4 composite fingerprint remains freeze candidate",
    certify_dependency_planning().composite_fingerprint
    == EXPECTED_COMPOSITE,
    certify_dependency_planning().composite_fingerprint,
)


# =============================================================================
# Final report
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
    "PHASE 4.6 — PLANNING CERTIFICATION FINAL CERTIFICATION",
    "=" * 112,
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
        f"PHASE {phase} SHA256: "
        + actual_shas[
            phase
        ]
    )


report_lines.extend(
    (
        "",
        (
            "PHASE 4 COMPOSITE FINGERPRINT: "
            + result.composite_fingerprint
        ),
        "",
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        (
            "STATUS: CERTIFICATION PASSED"
            if failed == 0
            else "STATUS: CERTIFICATION FAILED"
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
            "    "
            + detail
        )


REPORT.write_text(
    "\n".join(
        report_lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 112)
print("PHASE 4.6 FINAL CERTIFICATION RESULT")
print("=" * 112)
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
        "CERTIFICATION PASSED"
        if failed == 0
        else "CERTIFICATION FAILED"
    ),
)
print(
    "PHASE 4 COMPOSITE FINGERPRINT:",
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
print("=" * 112)


raise SystemExit(
    0
    if failed == 0
    else 1
)
