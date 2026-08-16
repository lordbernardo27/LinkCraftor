from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

DISCOVERY_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "discovery.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_2_worker_discovery_final_certification.txt"
)

EXPECTED_DISCOVERY_AST = (
    "DFCAB9080982C8D5E099A40C903F7B4140B0860053DB73CB77B30B966788A228"
)


PROTECTED = {
    "worker_registration": (
        ROOT / "backend/server/runtime/universal_worker/registration.py",
        "00F0D6E620E24A7433C880B722E023AF3C2121563F8E18DFA9979E0F06A36D64",
    ),

    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "existing_runtime_worker": (
        ROOT / "backend/server/runtime/universal_runtime_worker_v1.py",
        "6CC4EC122C6B8D1E21AFF8B55CAA786148D7E1FC75D840DAE9240FFB69634D44",
    ),

    "runtime_registration": (
        ROOT / "backend/server/runtime/universal_runtime_registration.py",
        "CBFBB0DA1E5D05A040AEC6F60B1251331431956106D90335A8C110FDBCA632E5",
    ),

    "runtime_infrastructure": (
        ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",
        "EE6590D044C6AA20762F2A37AE86B7FFD3300B62610BC2B1F2657D9334CB311C",
    ),

    "orchestration_queue": (
        ROOT / "backend/server/orchestration/queue.py",
        "76F8F7E66578E2B8A4A1FF3BB420B6340A7A1D1D661EB66B7C21987CF3845A97",
    ),

    "orchestration_service": (
        ROOT / "backend/server/orchestration/service.py",
        "4C31CFC6FFDC9AFA8EA6AD8F43ADBC117F8A6D0193ABF045DBFBA39D6EB799BA",
    ),
}


def ast_sha(
    path: Path,
) -> str:

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(source)

    canonical = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest().upper()


# ============================================================
# IMPORT
# ============================================================

sys.path.insert(
    0,
    str(ROOT),
)

registration_name = (
    "backend.server.runtime."
    "universal_worker.registration"
)

discovery_name = (
    "backend.server.runtime."
    "universal_worker.discovery"
)

sys.modules.pop(
    discovery_name,
    None,
)

registration = importlib.import_module(
    registration_name
)

discovery = importlib.import_module(
    discovery_name
)


checks = []


def check(
    name,
    condition,
    detail="",
):

    checks.append(
        (
            name,
            bool(condition),
            str(detail),
        )
    )


# ============================================================
# 1 — FINAL AST
# ============================================================

discovery_ast = ast_sha(
    DISCOVERY_PATH
)

check(
    "worker_discovery_ast",
    discovery_ast
    == EXPECTED_DISCOVERY_AST,
    discovery_ast,
)


# ============================================================
# 2 — VERSION / SCHEMAS
# ============================================================

check(
    "version",
    discovery.UNIVERSAL_WORKER_DISCOVERY_VERSION
    == "universal_worker_discovery_v4.1.2",
)

check(
    "candidate_schema",
    discovery.UNIVERSAL_WORKER_DISCOVERY_CANDIDATE_SCHEMA_VERSION
    == "universal_worker_discovery_candidate_schema_v1",
)

check(
    "decision_schema",
    discovery.UNIVERSAL_WORKER_DISCOVERY_DECISION_SCHEMA_VERSION
    == "universal_worker_discovery_decision_schema_v1",
)

check(
    "result_schema",
    discovery.UNIVERSAL_WORKER_DISCOVERY_RESULT_SCHEMA_VERSION
    == "universal_worker_discovery_result_schema_v1",
)


# ============================================================
# 3 — CANONICAL REGISTRATIONS
# ============================================================

def reg(
    worker_id,
    instance_id,
):

    return registration.create_universal_worker_registration(
        worker_id=worker_id,
        worker_type="general",
        worker_instance_id=instance_id,
        runtime_version="runtime-v1",
        host_id="host-a",
        registered_at="2026-08-15T20:00:00Z",
    )


worker_b2 = reg(
    "worker-b",
    "instance-002",
)

worker_a2 = reg(
    "worker-a",
    "instance-002",
)

worker_a1 = reg(
    "worker-a",
    "instance-001",
)


# ============================================================
# 4 — CANONICAL CANDIDATES
# ============================================================

candidate_b2 = (
    discovery.create_universal_worker_discovery_candidate(
        registration=worker_b2,
        discovery_enabled=True,
    )
)

candidate_a2 = (
    discovery.create_universal_worker_discovery_candidate(
        registration=worker_a2,
        discovery_enabled=False,
    )
)

candidate_a1 = (
    discovery.create_universal_worker_discovery_candidate(
        registration=worker_a1,
        discovery_enabled=True,
    )
)


check(
    "candidate_identity_a1",
    candidate_a1.canonical_identity
    == (
        "worker-a",
        "instance-001",
    ),
)

check(
    "candidate_identity_a2",
    candidate_a2.canonical_identity
    == (
        "worker-a",
        "instance-002",
    ),
)


# ============================================================
# 5 — DECISION RULE
# ============================================================

enabled_decision = (
    discovery.decide_universal_worker_discoverability(
        candidate_a1
    )
)

disabled_decision = (
    discovery.decide_universal_worker_discoverability(
        candidate_a2
    )
)


check(
    "enabled_discoverable",
    enabled_decision.discoverability
    is discovery.UniversalWorkerDiscoverability.DISCOVERABLE,
)

check(
    "enabled_boolean",
    enabled_decision.discoverable
    is True,
)

check(
    "disabled_not_discoverable",
    disabled_decision.discoverability
    is discovery.UniversalWorkerDiscoverability.NOT_DISCOVERABLE,
)

check(
    "disabled_boolean",
    disabled_decision.discoverable
    is False,
)


# ============================================================
# 6 — COLLECTION DISCOVERY
# ============================================================

result = (
    discovery.discover_universal_workers(
        (
            candidate_b2,
            candidate_a2,
            candidate_a1,
        )
    )
)


check(
    "decision_count",
    len(
        result.decisions
    )
    == 3,
)

check(
    "discoverable_count",
    result.discoverable_count
    == 2,
)


expected_decisions = (
    (
        "worker-a",
        "instance-001",
        "DISCOVERABLE",
    ),
    (
        "worker-a",
        "instance-002",
        "NOT_DISCOVERABLE",
    ),
    (
        "worker-b",
        "instance-002",
        "DISCOVERABLE",
    ),
)


actual_decisions = tuple(
    (
        item.worker_id,
        item.worker_instance_id,
        item.discoverability.value,
    )
    for item in result.decisions
)


check(
    "decision_order_and_classification",
    actual_decisions
    == expected_decisions,
    actual_decisions,
)


expected_discoverable = (
    (
        "worker-a",
        "instance-001",
    ),
    (
        "worker-b",
        "instance-002",
    ),
)


actual_discoverable = tuple(
    item.canonical_identity
    for item in result.discoverable_workers
)


check(
    "discoverable_set_exact",
    actual_discoverable
    == expected_discoverable,
    actual_discoverable,
)


# ============================================================
# 7 — EMPTY BEHAVIOR
# ============================================================

empty = (
    discovery.discover_universal_workers(
        ()
    )
)


check(
    "empty_decisions",
    empty.decisions
    == (),
)

check(
    "empty_workers",
    empty.discoverable_workers
    == (),
)

check(
    "empty_count",
    empty.discoverable_count
    == 0,
)


# ============================================================
# 8 — DETERMINISM
# ============================================================

reordered = (
    discovery.discover_universal_workers(
        (
            candidate_a1,
            candidate_b2,
            candidate_a2,
        )
    )
)


check(
    "deterministic_decisions",
    reordered.decisions
    == result.decisions,
)

check(
    "deterministic_workers",
    reordered.discoverable_workers
    == result.discoverable_workers,
)


# ============================================================
# 9 — DUPLICATE IDENTITY REJECTION
# ============================================================

duplicate = (
    discovery.create_universal_worker_discovery_candidate(
        registration=worker_a1,
        discovery_enabled=False,
    )
)


try:

    discovery.discover_universal_workers(
        (
            candidate_a1,
            duplicate,
        )
    )

except discovery.UniversalWorkerDiscoveryError as exc:

    duplicate_rejected = (
        exc.code
        == "duplicate_worker_discovery_candidate_identity"
    )

else:

    duplicate_rejected = False


check(
    "duplicate_identity_rejected",
    duplicate_rejected,
)


# ============================================================
# 10 — SAME LOGICAL WORKER / DIFFERENT INSTANCE
# ============================================================

same_worker_instances = (
    discovery.discover_universal_workers(
        (
            discovery.create_universal_worker_discovery_candidate(
                registration=reg(
                    "worker-c",
                    "instance-001",
                ),
                discovery_enabled=True,
            ),
            discovery.create_universal_worker_discovery_candidate(
                registration=reg(
                    "worker-c",
                    "instance-002",
                ),
                discovery_enabled=True,
            ),
        )
    )
)


check(
    "different_instances_are_distinct",
    same_worker_instances.discoverable_count
    == 2,
)


# ============================================================
# 11 — IMMUTABILITY
# ============================================================

immutability_targets = (
    (
        candidate_a1,
        "discovery_enabled",
    ),
    (
        enabled_decision,
        "discoverability",
    ),
    (
        result,
        "decisions",
    ),
)


for obj, field_name in (
    immutability_targets
):

    try:

        setattr(
            obj,
            field_name,
            None,
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        "immutable_"
        + type(obj).__name__,
        immutable,
    )


# ============================================================
# 12 — REGISTRATION REMAINS UNMUTATED
# ============================================================

before_registration = (
    worker_a1.to_dict()
)


discovery.discover_universal_workers(
    (
        candidate_a1,
    )
)


after_registration = (
    worker_a1.to_dict()
)


check(
    "worker_registration_not_mutated",
    before_registration
    == after_registration,
)


# ============================================================
# 13 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    discovery.explain_universal_worker_discovery_v1()
)


check(
    "phase",
    explanation.get(
        "phase"
    )
    == "4.1.2",
)

check(
    "component",
    explanation.get(
        "component"
    )
    == "Universal Worker Discovery",
)

check(
    "explanation_version",
    explanation.get(
        "version"
    )
    == discovery.UNIVERSAL_WORKER_DISCOVERY_VERSION,
)

check(
    "candidate_schema_explanation",
    explanation.get(
        "candidate_schema_version"
    )
    == discovery.UNIVERSAL_WORKER_DISCOVERY_CANDIDATE_SCHEMA_VERSION,
)

check(
    "decision_schema_explanation",
    explanation.get(
        "decision_schema_version"
    )
    == discovery.UNIVERSAL_WORKER_DISCOVERY_DECISION_SCHEMA_VERSION,
)

check(
    "result_schema_explanation",
    explanation.get(
        "result_schema_version"
    )
    == discovery.UNIVERSAL_WORKER_DISCOVERY_RESULT_SCHEMA_VERSION,
)

check(
    "input_is_registration_plus_caller_evidence",
    (
        "UniversalWorkerRegistration"
        in explanation.get(
            "input_rule",
            "",
        )
        and
        "caller-supplied"
        in explanation.get(
            "input_rule",
            "",
        )
    ),
)

check(
    "discoverability_rule_exact",
    (
        "DISCOVERABLE"
        in explanation.get(
            "discoverability_rule",
            "",
        )
        and
        "NOT_DISCOVERABLE"
        in explanation.get(
            "discoverability_rule",
            "",
        )
    ),
)

check(
    "ordering_exact",
    "worker_id then worker_instance_id"
    in explanation.get(
        "ordering_rule",
        "",
    ),
)

check(
    "duplicate_rule_present",
    "duplicate"
    in explanation.get(
        "duplicate_rule",
        "",
    ).lower(),
)

check(
    "discoverability_not_readiness",
    (
        "does not mean healthy"
        in explanation.get(
            "meaning",
            "",
        )
        and
        "capable"
        in explanation.get(
            "meaning",
            "",
        )
        and
        "assignable"
        in explanation.get(
            "meaning",
            "",
        )
    ),
)

check(
    "pure_caller_evidence_only",
    "no live state lookup"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


# ============================================================
# 14 — PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not create worker registrations",
    "does not persist worker registrations",
    "does not enumerate filesystem worker records",
    "does not access Runtime State Store",
    "does not call inspect_workers",
    "does not emit or read worker heartbeats",
    "does not determine worker health",
    "does not detect stale workers",
    "does not inspect worker capabilities",
    "does not inspect worker pools",
    "does not inspect worker capacity",
    "does not assign workers",
    "does not select a worker for a job",
    "does not claim jobs",
    "does not lease jobs",
    "does not dispatch jobs",
    "does not execute jobs",
    "does not recover workers",
    "does not scale workers",
    "does not drain workers",
    "does not shut down workers",
    "does not register runtime handlers",
    "does not mutate Queue Infrastructure",
    "does not access orchestration",
    "does not perform filesystem I/O",
    "does not perform network I/O",
)


prohibitions = tuple(
    explanation.get(
        "prohibitions"
    )
    or ()
)


for index, item in enumerate(
    required_prohibitions,
    start=1,
):

    check(
        "prohibition_"
        + str(index),
        item in prohibitions,
        item,
    )


# ============================================================
# 15 — STATIC IMPORT BOUNDARY
# ============================================================

source = DISCOVERY_PATH.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(
    source
)


backend_imports = []


for node in ast.walk(tree):

    if isinstance(
        node,
        ast.ImportFrom,
    ):

        module_name = (
            node.module
            or ""
        )

        if module_name.startswith(
            "backend.server"
        ):

            backend_imports.append(
                module_name
            )

    elif isinstance(
        node,
        ast.Import,
    ):

        for alias in node.names:

            if alias.name.startswith(
                "backend.server"
            ):

                backend_imports.append(
                    alias.name
                )


check(
    "only_worker_registration_imported",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.registration"
    ],
    backend_imports,
)


# ============================================================
# 16 — FORBIDDEN CALL BOUNDARY
# ============================================================

forbidden_names = {
    "open",
    "read_text",
    "write_text",
    "mkdir",
    "unlink",
    "remove",
    "read_json",
    "write_json",
    "inspect_workers",
    "worker_heartbeat",
    "get_runtime_state_store_registry",
    "get_latest_worker_statuses",
    "assign_worker",
    "select_worker",
    "claim_job",
    "dequeue_job",
    "lease_job",
    "renew_lease",
    "release_lease",
    "dispatch_job",
    "execute_job",
    "register_handler",
    "save_job",
    "get_job",
}


forbidden_calls = []


for node in ast.walk(tree):

    if not isinstance(
        node,
        ast.Call,
    ):

        continue

    if isinstance(
        node.func,
        ast.Name,
    ):

        call_name = (
            node.func.id
        )

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        call_name = (
            node.func.attr
        )

    else:

        continue

    if call_name in forbidden_names:

        forbidden_calls.append(
            (
                call_name,
                getattr(
                    node,
                    "lineno",
                    0,
                ),
            )
        )


check(
    "no_forbidden_calls",
    not forbidden_calls,
    forbidden_calls,
)


# ============================================================
# 17 — LATER-PHASE OWNERSHIP EXCLUSION
# ============================================================

function_names = tuple(
    node.name.lower()
    for node in ast.walk(tree)
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    )
)


for token in (
    "assign",
    "lease",
    "heartbeat",
    "health",
    "stale",
    "recover",
    "scale",
    "shutdown",
    "drain",
    "pool",
    "capability",
    "capacity",
    "claim",
    "dispatch",
    "execute",
    "persist",
):

    matches = tuple(
        name
        for name in function_names
        if token in name
    )

    check(
        "no_owned_"
        + token,
        not matches,
        matches,
    )


# ============================================================
# 18 — PROTECTED AST MATRIX
# ============================================================

for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(
        path
    )

    check(
        "protected_"
        + name,
        actual
        == expected,
        actual,
    )


# ============================================================
# 19 — DISCOVERY FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_4_1_2_worker_discovery",
        discovery.UNIVERSAL_WORKER_DISCOVERY_VERSION,
        discovery.UNIVERSAL_WORKER_DISCOVERY_CANDIDATE_SCHEMA_VERSION,
        discovery.UNIVERSAL_WORKER_DISCOVERY_DECISION_SCHEMA_VERSION,
        discovery.UNIVERSAL_WORKER_DISCOVERY_RESULT_SCHEMA_VERSION,
        discovery_ast,
        "worker_id",
        "worker_instance_id",
        "discovery_enabled",
        "DISCOVERABLE",
        "NOT_DISCOVERABLE",
        "worker_id_then_worker_instance_id",
    )
)


discovery_fingerprint = hashlib.sha256(
    fingerprint_material.encode(
        "utf-8"
    )
).hexdigest().upper()


check(
    "fingerprint_generated",
    len(
        discovery_fingerprint
    )
    == 64,
    discovery_fingerprint,
)


# ============================================================
# 20 — FINAL AST RECHECK
# ============================================================

final_ast = ast_sha(
    DISCOVERY_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_DISCOVERY_AST,
    final_ast,
)


# ============================================================
# REPORT
# ============================================================

passed = sum(
    1
    for _, ok, _
    in checks
    if ok
)

total = len(
    checks
)


lines = [
    (
        "PHASE 4.1.2 — UNIVERSAL WORKER "
        "DISCOVERY FINAL CERTIFICATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER DISCOVERY AST SHA256: "
        + discovery_ast
    ),
    (
        "WORKER DISCOVERY FINGERPRINT: "
        + discovery_fingerprint
    ),
    "",
]


for index, (
    name,
    ok,
    detail,
) in enumerate(
    checks,
    start=1,
):

    lines.append(
        (
            f"{index}. {name}: "
            f"{'PASS' if ok else 'FAIL'}"
        )
    )

    if detail:

        lines.append(
            "   "
            + detail
        )


lines.extend(
    [
        "",
        "=" * 112,
        (
            "FINAL WORKER DISCOVERY CERTIFICATION: "
            + (
                "PASS"
                if passed == total
                else "FAIL"
            )
        ),
        (
            "CHECKS PASSED: "
            + str(passed)
            + "/"
            + str(total)
        ),
        "",
        "WORKER DISCOVERY MODIFIED DURING CERTIFICATION: NO",
        "4.1.1 WORKER REGISTRATION MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB AUTHORITIES MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "FILESYSTEM WORKERS ENUMERATED: NO",
        "HEARTBEATS READ OR EMITTED: NO",
        "WORKER HEALTH DECIDED: NO",
        "STALE WORKER DETECTION PERFORMED: NO",
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER POOL INSPECTED: NO",
        "WORKER CAPACITY INSPECTED: NO",
        "WORKER ASSIGNED: NO",
        "JOB CLAIMED: NO",
        "JOB LEASED: NO",
        "JOB DISPATCHED: NO",
        "JOB EXECUTED: NO",
        "",
        (
            "PHASE 4.1.2 FREEZE CANDIDATE: "
            + (
                "YES"
                if passed == total
                else "NO"
            )
        ),
    ]
)


REPORT_PATH.write_text(
    "\n".join(lines),
    encoding="utf-8",
)

print(
    "\n".join(lines)
)


if passed != total:

    raise SystemExit(
        "Phase 4.1.2 Worker Discovery final certification failed."
    )
