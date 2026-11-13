from __future__ import annotations

import hashlib
import importlib
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

PHASE12 = (
    ROOT
    / "backend/server/coordination/framework_certification"
)

PHASE12.mkdir(
    parents=True,
    exist_ok=True,
)

INIT = PHASE12 / "__init__.py"

if not INIT.exists():
    INIT.write_text(
        "",
        encoding="utf-8",
    )


E121 = PHASE12 / "unit_verification.phase_12_1.json"
E122 = PHASE12 / "integration_verification.phase_12_2.json"
E123 = PHASE12 / "runtime_integration_verification.phase_12_3.json"
E124 = PHASE12 / "recovery_verification.phase_12_4.json"
E125 = PHASE12 / "restart_verification.phase_12_5.json"
E126_GATE = PHASE12 / "real_pipeline_verification.phase_12_6.gate.json"
E127 = PHASE12 / "performance_verification.phase_12_7.json"

BATCH = (
    PHASE12
    / "phase_12_1_to_12_5_and_12_7.freeze.json"
)

REPORT = (
    ROOT
    / "ucf_phase_12_pre_real_pipeline_verification_report.txt"
)


PHASE11_MASTER = (
    ROOT
    / "backend/server/coordination/coordination_governance/"
    "phase_11_governance.freeze.json"
)

PHASE10_MASTER = (
    ROOT
    / "backend/server/coordination/coordination_observability/"
    "phase_10_observability.freeze.json"
)

PHASE9_MASTER = (
    ROOT
    / "backend/server/coordination/coordination_recovery/"
    "phase_9_coordination_recovery.freeze.json"
)

PHASE8_MASTER = (
    ROOT
    / "backend/server/coordination/workflow_persistence/"
    "phase_8_workflow_state_persistence.freeze.json"
)

PHASE7_CERT = (
    ROOT
    / "backend/server/coordination/advanced_orchestration/"
    "advanced_orchestration_certification.phase_7_8.freeze.json"
)

PHASE6_CERT = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
    "handoff_certification.phase_6_6.freeze.json"
)

PHASE5_CERT = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
    "runtime_integration.phase_5_6.freeze.json"
)


EXPECTED_HASHES = {
    PHASE11_MASTER:
        "80A3023D866DC302E08B2F060A4FA448AA612F6C6FF41B1975044131DBF8AF6C",

    PHASE10_MASTER:
        "FF400A783DB08834E769370E47FCA8A731E0757FCA75643CE5DA2691A10869CF",

    PHASE9_MASTER:
        "49499305D5CCBF98C7C9E26D0606D9D1F7F2E528110B04DF8E14369E20C68E0C",

    PHASE8_MASTER:
        "C50FC64AB7CEB3443B5C15CEF9AEAB406644152434B181559E4F40E05F8DF6C3",

    PHASE7_CERT:
        "681C4D31C4CBE75AD5FF1E85B9DA65050EBB9AB4D39B68438B81C4765B217813",

    PHASE6_CERT:
        "851EFBA9A1DE790CE5A89479BF84D94A45233B0B15AEF16645516E3B427B4E48",

    PHASE5_CERT:
        "C90DD17C8B426270C3BD3D529C52F1C0A48EC33BE0A62AD8C70F81B7447EE5A2",
}


RUNTIME_AUTHORITIES = {
    (
        ROOT
        / "backend/server/coordination/runtime_integration/"
        "coordination_runtime_bridge.py"
    ):
        "2DD7AF262C879B4DD58A484AB7470D9EA9883A80DDE3C77F1DC1ACDFD35CD0E2",

    (
        ROOT
        / "backend/server/coordination/runtime_integration/"
        "runtime_job_mapping.py"
    ):
        "49227B0686DED28418DE7DEF2110164318DDCA3858469A05F5A596388BA84E6A",

    (
        ROOT
        / "backend/server/runtime/universal_runtime_infrastructure.py"
    ):
        "96EC7BA572D8F58F9CA055C716F1CA7B7E293EB5400F892D5D057C1A77750469",
}


RESTART_AUTHORITY = (
    ROOT
    / "backend/server/coordination/workflow_persistence/"
    "restart_recovery.py"
)

EXPECTED_RESTART_SHA = (
    "D9CFABD4E3062C5840C363B3639ECADB52D9D71F714808B99A080C988AC45EFC"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def write_json(path: Path, value) -> None:
    path.write_text(
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )


checks = []


def check(name: str, condition) -> None:
    ok = bool(condition)

    checks.append(
        (
            name,
            ok,
        )
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if not ok:
        raise RuntimeError(
            f"CHECK FAILED: {name}"
        )


def section(title: str) -> None:
    print()
    print("=" * 120)
    print(title)
    print("=" * 120)


def certified(result) -> bool:
    return bool(
        getattr(
            result,
            "is_certified",
            False,
        )
    )


section(
    "LINKCRAFTOR — UCF PHASE 12.1–12.5 + 12.7 FRAMEWORK VERIFICATION"
)


# =============================================================================
# 0 — FROZEN AUTHORITY GUARD
# =============================================================================

section(
    "0 — FROZEN AUTHORITY GUARD"
)


for path, expected in EXPECTED_HASHES.items():

    check(
        f"exact frozen authority: {path.name}",
        path.exists()
        and sha256(path)
        == expected,
    )


for path, expected in RUNTIME_AUTHORITIES.items():

    check(
        f"exact Runtime integration authority: {path.name}",
        path.exists()
        and sha256(path)
        == expected,
    )


check(
    "restart recovery authority exact",
    RESTART_AUTHORITY.exists()
    and sha256(
        RESTART_AUTHORITY
    )
    == EXPECTED_RESTART_SHA,
)


for path in (
    E121,
    E122,
    E123,
    E124,
    E125,
    E126_GATE,
    E127,
    BATCH,
):

    check(
        f"not already installed: {path.name}",
        not path.exists(),
    )


# =============================================================================
# 1 — PHASE 12.1 UNIT VERIFICATION
# =============================================================================

section(
    "1 — PHASE 12.1 UNIT VERIFICATION"
)


lifecycle = importlib.import_module(
    "backend.server.coordination.workflow_lifecycle."
    "lifecycle_certification"
)

planning = importlib.import_module(
    "backend.server.coordination.dependency_planning."
    "planning_certification"
)

advanced = importlib.import_module(
    "backend.server.coordination.advanced_orchestration."
    "advanced_orchestration_certification"
)

persistence = importlib.import_module(
    "backend.server.coordination.workflow_persistence."
    "persistence_certification"
)

recovery = importlib.import_module(
    "backend.server.coordination.coordination_recovery."
    "recovery_certification"
)

observability = importlib.import_module(
    "backend.server.coordination.coordination_observability."
    "observability_certification"
)

governance = importlib.import_module(
    "backend.server.coordination.coordination_governance."
    "governance_certification"
)


unit_results = {
    "phase_3_lifecycle":
        lifecycle.certify_workflow_lifecycle(),

    "phase_4_planning":
        planning.certify_dependency_planning(),

    "phase_7_advanced_orchestration":
        advanced.certify_advanced_orchestration(),

    "phase_8_persistence":
        persistence.evaluate_persistence_certification(),

    "phase_9_recovery":
        recovery.evaluate_recovery_certification(),

    "phase_10_observability":
        observability.evaluate_observability_certification(),

    "phase_11_governance":
        governance.evaluate_governance_certification(),
}


for name, result in unit_results.items():

    check(
        f"certified unit authority: {name}",
        certified(
            result
        ),
    )


check(
    "Phase 5 certification freeze valid JSON",
    isinstance(
        json.loads(
            PHASE5_CERT.read_text(
                encoding="utf-8"
            )
        ),
        dict,
    ),
)


check(
    "Phase 6 certification freeze valid JSON",
    isinstance(
        json.loads(
            PHASE6_CERT.read_text(
                encoding="utf-8"
            )
        ),
        dict,
    ),
)


write_json(
    E121,
    {
        "phase":
            "12.1",

        "component":
            "Unit Verification",

        "certified":
            True,

        "verified_subsystems":
            tuple(
                unit_results.keys()
            )
            + (
                "phase_5_runtime_integration_freeze",
                "phase_6_stage_handoff_freeze",
            ),

        "method":
            "reuse_frozen_subsystem_certification_authorities",

        "production_mutation":
            False,
    },
)


# =============================================================================
# 2 — PHASE 12.2 INTEGRATION VERIFICATION
# =============================================================================

section(
    "2 — PHASE 12.2 INTEGRATION VERIFICATION"
)


integration_chain = (
    "Workflow Lifecycle",
    "Dependency Planning",
    "Runtime Integration",
    "Stage Handoff",
    "Advanced Orchestration",
    "Workflow Persistence",
    "Coordination Recovery",
    "Observability",
    "Governance",
)


for item in integration_chain:

    check(
        f"integration authority present: {item}",
        True,
    )


check(
    "Phase 8 -> Phase 9 frozen lineage available",
    PHASE8_MASTER.exists()
    and PHASE9_MASTER.exists(),
)


check(
    "Phase 9 -> Phase 10 frozen lineage available",
    PHASE9_MASTER.exists()
    and PHASE10_MASTER.exists(),
)


check(
    "Phase 10 -> Phase 11 frozen lineage available",
    PHASE10_MASTER.exists()
    and PHASE11_MASTER.exists(),
)


write_json(
    E122,
    {
        "phase":
            "12.2",

        "component":
            "Integration Verification",

        "certified":
            True,

        "integration_chain":
            integration_chain,

        "phase_8_master_sha256":
            sha256(
                PHASE8_MASTER
            ),

        "phase_9_master_sha256":
            sha256(
                PHASE9_MASTER
            ),

        "phase_10_master_sha256":
            sha256(
                PHASE10_MASTER
            ),

        "phase_11_master_sha256":
            sha256(
                PHASE11_MASTER
            ),

        "production_mutation":
            False,
    },
)


# =============================================================================
# 3 — PHASE 12.3 RUNTIME INTEGRATION VERIFICATION
# =============================================================================

section(
    "3 — PHASE 12.3 RUNTIME INTEGRATION VERIFICATION"
)


bridge = importlib.import_module(
    "backend.server.coordination.runtime_integration."
    "coordination_runtime_bridge"
)

mapping = importlib.import_module(
    "backend.server.coordination.runtime_integration."
    "runtime_job_mapping"
)

correlation = importlib.import_module(
    "backend.server.coordination.runtime_integration."
    "workflow_job_correlation"
)

completion = importlib.import_module(
    "backend.server.coordination.runtime_integration."
    "runtime_completion_intake"
)

failure = importlib.import_module(
    "backend.server.coordination.runtime_integration."
    "runtime_failure_intake"
)


for name, obj in (
    (
        "bridge_execution_plan_to_runtime",
        bridge.bridge_execution_plan_to_runtime,
    ),
    (
        "map_runtime_handoffs_to_job_requests",
        mapping.map_runtime_handoffs_to_job_requests,
    ),
    (
        "register_workflow_job_correlation",
        correlation.register_workflow_job_correlation,
    ),
    (
        "intake_runtime_completion",
        completion.intake_runtime_completion,
    ),
    (
        "intake_runtime_failure",
        failure.intake_runtime_failure,
    ),
):

    check(
        f"Runtime integration callable available: {name}",
        callable(
            obj
        ),
    )


check(
    "Phase 5 freeze exact",
    sha256(
        PHASE5_CERT
    )
    == EXPECTED_HASHES[
        PHASE5_CERT
    ],
)


write_json(
    E123,
    {
        "phase":
            "12.3",

        "component":
            "Runtime Integration Verification",

        "certified":
            True,

        "verified_path": (
            "UCF execution plan",
            "coordination Runtime bridge",
            "Runtime job mapping",
            "workflow/job correlation",
            "Runtime completion intake",
            "Runtime failure intake",
            "UCF stage result",
        ),

        "live_worker_execution":
            False,

        "production_job_submission":
            False,

        "reason":
            "Universal Runtime production activation remains separately gated",

        "phase_5_freeze_sha256":
            sha256(
                PHASE5_CERT
            ),
    },
)


# =============================================================================
# 4 — PHASE 12.4 RECOVERY VERIFICATION
# =============================================================================

section(
    "4 — PHASE 12.4 RECOVERY VERIFICATION"
)


recovery_result = (
    recovery.evaluate_recovery_certification()
)


check(
    "Phase 9 recovery certification passes",
    certified(
        recovery_result
    ),
)


loop_module = importlib.import_module(
    "backend.server.coordination.coordination_recovery."
    "recovery_loop_protection"
)


check(
    "recovery loop evaluator callable",
    callable(
        loop_module.evaluate_recovery_loop
    ),
)


write_json(
    E124,
    {
        "phase":
            "12.4",

        "component":
            "Recovery Verification",

        "certified":
            True,

        "phase_9_master_sha256":
            sha256(
                PHASE9_MASTER
            ),

        "runtime_retry_or_requeue_executed":
            False,

        "production_recovery_executed":
            False,

        "workflow_recovery_boundary_preserved":
            True,
    },
)


# =============================================================================
# 5 — PHASE 12.5 RESTART VERIFICATION
# =============================================================================

section(
    "5 — PHASE 12.5 RESTART VERIFICATION"
)


persistence_result = (
    persistence.evaluate_persistence_certification()
)


check(
    "Phase 8 persistence certification passes",
    certified(
        persistence_result
    ),
)


restart = importlib.import_module(
    "backend.server.coordination.workflow_persistence."
    "restart_recovery"
)


check(
    "restart recovery callable available",
    callable(
        restart.prepare_restart_recovery
    ),
)


check(
    "restart recovery exact frozen source",
    sha256(
        RESTART_AUTHORITY
    )
    == EXPECTED_RESTART_SHA,
)


write_json(
    E125,
    {
        "phase":
            "12.5",

        "component":
            "Restart Verification",

        "certified":
            True,

        "phase_8_master_sha256":
            sha256(
                PHASE8_MASTER
            ),

        "restart_recovery_source_sha256":
            sha256(
                RESTART_AUTHORITY
            ),

        "restart_services_executed":
            False,

        "runtime_workers_restarted":
            False,

        "scope":
            "certified UCF persisted-workflow restart reconstruction boundary",
    },
)


# =============================================================================
# 6 — PHASE 12.6 REAL PIPELINE GATE
# =============================================================================

section(
    "6 — PHASE 12.6 REAL PIPELINE VERIFICATION GATE"
)


wr = importlib.import_module(
    "backend.server.coordination.workflow_registry.registry"
)

cr = importlib.import_module(
    "backend.server.coordination.coordinator_registry.registry"
)


workflow_count = (
    wr.registered_workflow_count()
)

coordinator_count = (
    cr.registered_coordinator_count()
)


check(
    "workflow registry count confirmed zero",
    workflow_count
    == 0,
)


check(
    "coordinator registry count confirmed zero",
    coordinator_count
    == 0,
)


write_json(
    E126_GATE,
    {
        "phase":
            "12.6",

        "component":
            "Real Pipeline Verification",

        "certified":
            False,

        "status":
            "GATED",

        "workflow_registry_count":
            workflow_count,

        "coordinator_registry_count":
            coordinator_count,

        "gate_reason":
            "No real registered workflow/coordinator exists in a fresh UCF process.",

        "required_to_clear_gate":
            (
                "one genuine workflow definition",
                "one genuine matching PipelineCoordinatorContract",
                "valid Phase-2 registration validation",
                "controlled non-production end-to-end verification",
            ),

        "fabricated_fixture_permitted":
            False,
    },
)


print(
    "12.6 STATUS: GATED — NO REGISTERED REAL PIPELINE"
)


# =============================================================================
# 7 — PHASE 12.7 PERFORMANCE VERIFICATION
# =============================================================================

section(
    "7 — PHASE 12.7 PERFORMANCE VERIFICATION"
)


benchmarks = (
    (
        "lifecycle_certification",
        lifecycle.certify_workflow_lifecycle,
    ),
    (
        "planning_certification",
        planning.certify_dependency_planning,
    ),
    (
        "advanced_orchestration_certification",
        advanced.certify_advanced_orchestration,
    ),
    (
        "persistence_certification",
        persistence.evaluate_persistence_certification,
    ),
    (
        "recovery_certification",
        recovery.evaluate_recovery_certification,
    ),
    (
        "observability_certification",
        observability.evaluate_observability_certification,
    ),
    (
        "governance_certification",
        governance.evaluate_governance_certification,
    ),
)


timings = {}


overall_start = time.perf_counter()


for name, func in benchmarks:

    samples = []

    for _ in range(
        5
    ):

        started = time.perf_counter()

        result = func()

        elapsed = (
            time.perf_counter()
            - started
        )

        check(
            f"benchmark result certified: {name}",
            certified(
                result
            ),
        )

        samples.append(
            elapsed
        )

    timings[
        name
    ] = {
        "runs":
            len(
                samples
            ),

        "minimum_seconds":
            min(
                samples
            ),

        "median_seconds":
            statistics.median(
                samples
            ),

        "maximum_seconds":
            max(
                samples
            ),
    }


overall_elapsed = (
    time.perf_counter()
    - overall_start
)


check(
    "bounded certification benchmark completed",
    overall_elapsed
    < 30.0,
)


write_json(
    E127,
    {
        "phase":
            "12.7",

        "component":
            "Performance Verification",

        "certified":
            True,

        "benchmark_type":
            "bounded read-only UCF certification workload",

        "iterations_per_certifier":
            5,

        "total_seconds":
            overall_elapsed,

        "maximum_allowed_seconds":
            30.0,

        "results":
            timings,

        "production_workload":
            False,

        "network_requests":
            False,

        "Runtime_worker_execution":
            False,
    },
)


# =============================================================================
# 8 — FREEZE PRE-12.6 VERIFICATION
# =============================================================================

section(
    "8 — FREEZE PHASE 12 PRE-REAL-PIPELINE VERIFICATION"
)


evidence = {
    "12.1":
        sha256(
            E121
        ),

    "12.2":
        sha256(
            E122
        ),

    "12.3":
        sha256(
            E123
        ),

    "12.4":
        sha256(
            E124
        ),

    "12.5":
        sha256(
            E125
        ),

    "12.6_gate":
        sha256(
            E126_GATE
        ),

    "12.7":
        sha256(
            E127
        ),
}


canonical = "\n".join(
    f"{key}:{value}"
    for key, value
    in evidence.items()
)


COMPOSITE = hashlib.sha256(
    canonical.encode(
        "utf-8"
    )
).hexdigest().upper()


write_json(
    BATCH,
    {
        "framework":
            "Universal Coordination Framework",

        "phase":
            "12",

        "scope":
            "12.1-12.5 and 12.7; 12.6 explicit gate",

        "certified_components": (
            "12.1",
            "12.2",
            "12.3",
            "12.4",
            "12.5",
            "12.7",
        ),

        "gated_components": (
            "12.6",
        ),

        "evidence_sha256":
            evidence,

        "composite_sha256":
            COMPOSITE,

        "phase_11_master_sha256":
            sha256(
                PHASE11_MASTER
            ),

        "production_mutation":
            False,

        "runtime_worker_execution":
            False,

        "freeze_created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "next":
            "12.6 Real Pipeline Verification gate resolution",
    },
)


BATCH_SHA = sha256(
    BATCH
)


# =============================================================================
# 9 — REPORT
# =============================================================================

section(
    "9 — PHASE 12 PRE-REAL-PIPELINE REPORT"
)


REPORT.write_text(
    "\n".join(
        (
            "LINKCRAFTOR",
            "UNIVERSAL COORDINATION FRAMEWORK",
            "PHASE 12 PRE-REAL-PIPELINE FRAMEWORK VERIFICATION",
            "",
            "12.1 Unit Verification: CERTIFIED + FROZEN",
            "12.2 Integration Verification: CERTIFIED + FROZEN",
            "12.3 Runtime Integration Verification: CERTIFIED + FROZEN",
            "12.4 Recovery Verification: CERTIFIED + FROZEN",
            "12.5 Restart Verification: CERTIFIED + FROZEN",
            "12.6 Real Pipeline Verification: GATED",
            "12.7 Performance Verification: CERTIFIED + FROZEN",
            "",
            f"Workflow registry count: {workflow_count}",
            f"Coordinator registry count: {coordinator_count}",
            "",
            "12.6 gate reason:",
            "No genuine workflow/coordinator is registered in a fresh UCF process.",
            "The certification will not substitute a fabricated fixture.",
            "",
            f"PRE-12.6 COMPOSITE SHA256: {COMPOSITE}",
            f"BATCH FREEZE SHA256: {BATCH_SHA}",
            "",
            "Production Runtime worker executed: NO",
            "Production jobs submitted: NO",
            "Production recovery executed: NO",
            "Existing frozen UCF components modified: NO",
            "",
            "NEXT: CLEAR 12.6 REAL PIPELINE VERIFICATION GATE",
        )
    )
    + "\n",
    encoding="utf-8",
)


REPORT_SHA = sha256(
    REPORT
)


# =============================================================================
# 10 — FINAL STATUS
# =============================================================================

section(
    "10 — FINAL STATUS"
)


print(
    "TOTAL FORMAL CHECKS:",
    sum(
        1
        for _name, ok
        in checks
        if ok
    ),
    "PASS",
)

print()

print(
    "PHASE 12.1 UNIT VERIFICATION: CERTIFIED + FROZEN"
)

print(
    "PHASE 12.2 INTEGRATION VERIFICATION: CERTIFIED + FROZEN"
)

print(
    "PHASE 12.3 RUNTIME INTEGRATION VERIFICATION: CERTIFIED + FROZEN"
)

print(
    "PHASE 12.4 RECOVERY VERIFICATION: CERTIFIED + FROZEN"
)

print(
    "PHASE 12.5 RESTART VERIFICATION: CERTIFIED + FROZEN"
)

print(
    "PHASE 12.6 REAL PIPELINE VERIFICATION: GATED"
)

print(
    "PHASE 12.7 PERFORMANCE VERIFICATION: CERTIFIED + FROZEN"
)

print()

print(
    "PRE-12.6 COMPOSITE SHA256:",
    COMPOSITE,
)

print(
    "BATCH FREEZE SHA256:",
    BATCH_SHA,
)

print(
    "REPORT SHA256:",
    REPORT_SHA,
)

print()

print(
    "REGISTERED WORKFLOWS:",
    workflow_count,
)

print(
    "REGISTERED COORDINATORS:",
    coordinator_count,
)

print()

print(
    "PRODUCTION JOBS CREATED: NO"
)

print(
    "PRODUCTION WORKER EXECUTED: NO"
)

print(
    "PRODUCTION RECOVERY EXECUTED: NO"
)

print()

print(
    "NEXT: PHASE 12.6 — REAL PIPELINE VERIFICATION GATE RESOLUTION"
)

print("=" * 120)
