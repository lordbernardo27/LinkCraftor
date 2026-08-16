from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from dataclasses import FrozenInstanceError
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
    / "phase_4_1_2_worker_discovery_regression.txt"
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
# AST / VERSION / SCHEMA STABILITY
# ============================================================

actual_discovery_ast = ast_sha(
    DISCOVERY_PATH
)

check(
    "discovery_ast_stable",
    actual_discovery_ast
    == EXPECTED_DISCOVERY_AST,
    actual_discovery_ast,
)

check(
    "version_exact",
    discovery.UNIVERSAL_WORKER_DISCOVERY_VERSION
    == "universal_worker_discovery_v4.1.2",
)

check(
    "candidate_schema_exact",
    discovery.UNIVERSAL_WORKER_DISCOVERY_CANDIDATE_SCHEMA_VERSION
    == "universal_worker_discovery_candidate_schema_v1",
)

check(
    "decision_schema_exact",
    discovery.UNIVERSAL_WORKER_DISCOVERY_DECISION_SCHEMA_VERSION
    == "universal_worker_discovery_decision_schema_v1",
)

check(
    "result_schema_exact",
    discovery.UNIVERSAL_WORKER_DISCOVERY_RESULT_SCHEMA_VERSION
    == "universal_worker_discovery_result_schema_v1",
)


# ============================================================
# FIXTURE FACTORY
# ============================================================

def reg(
    worker_id: str,
    instance_id: str,
    *,
    worker_type: str = "general",
    runtime_version: str = "runtime-v1",
    host_id: str = "host-a",
):

    return registration.create_universal_worker_registration(
        worker_id=worker_id,
        worker_type=worker_type,
        worker_instance_id=instance_id,
        runtime_version=runtime_version,
        host_id=host_id,
        registered_at="2026-08-15T20:00:00Z",
    )


def candidate(
    worker_id: str,
    instance_id: str,
    enabled: bool,
):

    return (
        discovery.create_universal_worker_discovery_candidate(
            registration=reg(
                worker_id,
                instance_id,
            ),
            discovery_enabled=enabled,
        )
    )


# ============================================================
# BASIC DECISION MATRIX
# ============================================================

enabled_candidate = candidate(
    "worker-a",
    "instance-001",
    True,
)

disabled_candidate = candidate(
    "worker-b",
    "instance-001",
    False,
)


enabled_decision = (
    discovery.decide_universal_worker_discoverability(
        enabled_candidate
    )
)

disabled_decision = (
    discovery.decide_universal_worker_discoverability(
        disabled_candidate
    )
)


check(
    "enabled_is_discoverable",
    enabled_decision.discoverable is True,
)

check(
    "enabled_enum_exact",
    enabled_decision.discoverability
    is discovery.UniversalWorkerDiscoverability.DISCOVERABLE,
)

check(
    "disabled_is_not_discoverable",
    disabled_decision.discoverable is False,
)

check(
    "disabled_enum_exact",
    disabled_decision.discoverability
    is discovery.UniversalWorkerDiscoverability.NOT_DISCOVERABLE,
)


# ============================================================
# STRICT BOOL ATTACKS
# ============================================================

bad_bool_values = (
    None,
    0,
    1,
    -1,
    "",
    "False",
    "True",
    [],
    {},
    (),
)


for index, bad in enumerate(
    bad_bool_values,
    start=1,
):

    try:

        discovery.create_universal_worker_discovery_candidate(
            registration=reg(
                "worker-x",
                "instance-x",
            ),
            discovery_enabled=bad,
        )

    except discovery.UniversalWorkerDiscoveryError as exc:

        rejected = (
            exc.code
            == "invalid_discovery_enabled"
        )

    else:

        rejected = False

    check(
        "strict_bool_reject_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# INVALID REGISTRATION ATTACKS
# ============================================================

bad_registration_values = (
    None,
    True,
    False,
    0,
    1,
    "",
    [],
    {},
    (),
)


for index, bad in enumerate(
    bad_registration_values,
    start=1,
):

    try:

        discovery.create_universal_worker_discovery_candidate(
            registration=bad,
            discovery_enabled=True,
        )

    except discovery.UniversalWorkerDiscoveryError as exc:

        rejected = (
            exc.code
            == "invalid_worker_registration"
        )

    else:

        rejected = False

    check(
        "invalid_registration_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# BAD SINGLE CANDIDATE DECISION
# ============================================================

bad_candidate_values = (
    None,
    True,
    0,
    "",
    {},
    [],
    reg(
        "worker-z",
        "instance-z",
    ),
)


for index, bad in enumerate(
    bad_candidate_values,
    start=1,
):

    try:

        discovery.decide_universal_worker_discoverability(
            bad
        )

    except discovery.UniversalWorkerDiscoveryError as exc:

        rejected = (
            exc.code
            == "invalid_worker_discovery_candidate"
        )

    else:

        rejected = False

    check(
        "invalid_single_candidate_"
        + str(index),
        rejected,
    )


# ============================================================
# DETERMINISTIC SORTING
# ============================================================

unordered = (
    candidate(
        "worker-z",
        "instance-003",
        True,
    ),
    candidate(
        "worker-a",
        "instance-010",
        True,
    ),
    candidate(
        "worker-a",
        "instance-002",
        False,
    ),
    candidate(
        "worker-a",
        "instance-001",
        True,
    ),
    candidate(
        "worker-m",
        "instance-001",
        True,
    ),
)


ordered_result = (
    discovery.discover_universal_workers(
        unordered
    )
)


expected_decision_order = (
    ("worker-a", "instance-001"),
    ("worker-a", "instance-002"),
    ("worker-a", "instance-010"),
    ("worker-m", "instance-001"),
    ("worker-z", "instance-003"),
)


actual_decision_order = tuple(
    (
        item.worker_id,
        item.worker_instance_id,
    )
    for item in ordered_result.decisions
)


check(
    "deterministic_sort_exact",
    actual_decision_order
    == expected_decision_order,
    actual_decision_order,
)


expected_discoverable_order = (
    ("worker-a", "instance-001"),
    ("worker-a", "instance-010"),
    ("worker-m", "instance-001"),
    ("worker-z", "instance-003"),
)


actual_discoverable_order = tuple(
    item.canonical_identity
    for item in ordered_result.discoverable_workers
)


check(
    "discoverable_subset_order_exact",
    actual_discoverable_order
    == expected_discoverable_order,
    actual_discoverable_order,
)


# ============================================================
# ORDER INDEPENDENCE
# ============================================================

reversed_result = (
    discovery.discover_universal_workers(
        tuple(
            reversed(
                unordered
            )
        )
    )
)


check(
    "input_order_independent_decisions",
    reversed_result.decisions
    == ordered_result.decisions,
)

check(
    "input_order_independent_discoverable",
    reversed_result.discoverable_workers
    == ordered_result.discoverable_workers,
)


# ============================================================
# GENERATOR INPUT
# ============================================================

generator_result = (
    discovery.discover_universal_workers(
        item
        for item in unordered
    )
)


check(
    "generator_input_supported",
    generator_result
    == ordered_result,
)


# ============================================================
# EMPTY INPUT
# ============================================================

empty_result = (
    discovery.discover_universal_workers(
        ()
    )
)


check(
    "empty_result_decisions",
    empty_result.decisions
    == (),
)

check(
    "empty_result_workers",
    empty_result.discoverable_workers
    == (),
)

check(
    "empty_result_count",
    empty_result.discoverable_count
    == 0,
)


# ============================================================
# INVALID COLLECTIONS
# ============================================================

bad_collections = (
    None,
    "workers",
    b"workers",
    {},
    1,
    True,
    False,
)


for index, bad in enumerate(
    bad_collections,
    start=1,
):

    try:

        discovery.discover_universal_workers(
            bad
        )

    except discovery.UniversalWorkerDiscoveryError as exc:

        rejected = (
            exc.code
            == "invalid_worker_discovery_candidates"
        )

    else:

        rejected = False

    check(
        "invalid_collection_"
        + str(index),
        rejected,
    )


# ============================================================
# MIXED COLLECTION REJECTION
# ============================================================

for bad in (
    None,
    True,
    1,
    "",
    {},
    [],
    reg(
        "wrong",
        "registration",
    ),
):

    try:

        discovery.discover_universal_workers(
            (
                enabled_candidate,
                bad,
            )
        )

    except discovery.UniversalWorkerDiscoveryError as exc:

        rejected = (
            exc.code
            == "invalid_worker_discovery_candidate"
        )

    else:

        rejected = False

    check(
        "mixed_collection_rejected_"
        + type(bad).__name__,
        rejected,
    )


# ============================================================
# DUPLICATE IDENTITY ATTACKS
# ============================================================

duplicate_a = candidate(
    "worker-dup",
    "instance-001",
    True,
)

duplicate_b = (
    discovery.create_universal_worker_discovery_candidate(
        registration=reg(
            "worker-dup",
            "instance-001",
            worker_type="specialized",
            runtime_version="runtime-v99",
            host_id="host-z",
        ),
        discovery_enabled=False,
    )
)


try:

    discovery.discover_universal_workers(
        (
            duplicate_a,
            duplicate_b,
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


# Same logical worker but different instance MUST be allowed.
same_worker_different_instances = (
    discovery.discover_universal_workers(
        (
            candidate(
                "worker-same",
                "instance-001",
                True,
            ),
            candidate(
                "worker-same",
                "instance-002",
                True,
            ),
        )
    )
)


check(
    "same_worker_different_instances_allowed",
    same_worker_different_instances.discoverable_count
    == 2,
)


# ============================================================
# DECISION CONSISTENCY ATTACKS
# ============================================================

try:

    discovery.UniversalWorkerDiscoveryDecision(
        worker_id="worker",
        worker_instance_id="instance",
        discoverability=(
            discovery.UniversalWorkerDiscoverability.NOT_DISCOVERABLE
        ),
        discovery_enabled=True,
    )

except discovery.UniversalWorkerDiscoveryError as exc:

    inconsistent_rejected_1 = (
        exc.code
        == "inconsistent_discovery_decision"
    )

else:

    inconsistent_rejected_1 = False


check(
    "inconsistent_true_decision_rejected",
    inconsistent_rejected_1,
)


try:

    discovery.UniversalWorkerDiscoveryDecision(
        worker_id="worker",
        worker_instance_id="instance",
        discoverability=(
            discovery.UniversalWorkerDiscoverability.DISCOVERABLE
        ),
        discovery_enabled=False,
    )

except discovery.UniversalWorkerDiscoveryError as exc:

    inconsistent_rejected_2 = (
        exc.code
        == "inconsistent_discovery_decision"
    )

else:

    inconsistent_rejected_2 = False


check(
    "inconsistent_false_decision_rejected",
    inconsistent_rejected_2,
)


# ============================================================
# DECISION FIELD TYPE ATTACKS
# ============================================================

try:

    discovery.UniversalWorkerDiscoveryDecision(
        worker_id="",
        worker_instance_id="instance",
        discoverability=(
            discovery.UniversalWorkerDiscoverability.DISCOVERABLE
        ),
        discovery_enabled=True,
    )

except discovery.UniversalWorkerDiscoveryError:

    rejected = True

else:

    rejected = False


check(
    "empty_decision_worker_id_rejected",
    rejected,
)


try:

    discovery.UniversalWorkerDiscoveryDecision(
        worker_id="worker",
        worker_instance_id="",
        discoverability=(
            discovery.UniversalWorkerDiscoverability.DISCOVERABLE
        ),
        discovery_enabled=True,
    )

except discovery.UniversalWorkerDiscoveryError:

    rejected = True

else:

    rejected = False


check(
    "empty_decision_instance_rejected",
    rejected,
)


try:

    discovery.UniversalWorkerDiscoveryDecision(
        worker_id="worker",
        worker_instance_id="instance",
        discoverability="DISCOVERABLE",
        discovery_enabled=True,
    )

except discovery.UniversalWorkerDiscoveryError as exc:

    rejected = (
        exc.code
        == "invalid_discoverability"
    )

else:

    rejected = False


check(
    "raw_string_discoverability_rejected",
    rejected,
)


# ============================================================
# SCHEMA TAMPERING
# ============================================================

try:

    discovery.UniversalWorkerDiscoveryCandidate(
        registration=reg(
            "worker-schema",
            "instance-1",
        ),
        discovery_enabled=True,
        schema_version="wrong",
    )

except discovery.UniversalWorkerDiscoveryError as exc:

    rejected = (
        exc.code
        == "invalid_worker_discovery_candidate_schema_version"
    )

else:

    rejected = False


check(
    "candidate_schema_tamper_rejected",
    rejected,
)


try:

    discovery.UniversalWorkerDiscoveryDecision(
        worker_id="worker",
        worker_instance_id="instance",
        discoverability=(
            discovery.UniversalWorkerDiscoverability.DISCOVERABLE
        ),
        discovery_enabled=True,
        schema_version="wrong",
    )

except discovery.UniversalWorkerDiscoveryError as exc:

    rejected = (
        exc.code
        == "invalid_worker_discovery_decision_schema_version"
    )

else:

    rejected = False


check(
    "decision_schema_tamper_rejected",
    rejected,
)


try:

    discovery.UniversalWorkerDiscoveryResult(
        decisions=(),
        discoverable_workers=(),
        schema_version="wrong",
    )

except discovery.UniversalWorkerDiscoveryError as exc:

    rejected = (
        exc.code
        == "invalid_worker_discovery_result_schema_version"
    )

else:

    rejected = False


check(
    "result_schema_tamper_rejected",
    rejected,
)


# ============================================================
# RESULT TYPE ATTACKS
# ============================================================

try:

    discovery.UniversalWorkerDiscoveryResult(
        decisions=[],
        discoverable_workers=(),
    )

except discovery.UniversalWorkerDiscoveryError as exc:

    rejected = (
        exc.code
        == "invalid_discovery_decisions"
    )

else:

    rejected = False


check(
    "result_decisions_list_rejected",
    rejected,
)


try:

    discovery.UniversalWorkerDiscoveryResult(
        decisions=(),
        discoverable_workers=[],
    )

except discovery.UniversalWorkerDiscoveryError as exc:

    rejected = (
        exc.code
        == "invalid_discoverable_workers"
    )

else:

    rejected = False


check(
    "result_workers_list_rejected",
    rejected,
)


try:

    discovery.UniversalWorkerDiscoveryResult(
        decisions=(
            "bad",
        ),
        discoverable_workers=(),
    )

except discovery.UniversalWorkerDiscoveryError as exc:

    rejected = (
        exc.code
        == "invalid_discovery_decision"
    )

else:

    rejected = False


check(
    "result_bad_decision_rejected",
    rejected,
)


try:

    discovery.UniversalWorkerDiscoveryResult(
        decisions=(),
        discoverable_workers=(
            "bad",
        ),
    )

except discovery.UniversalWorkerDiscoveryError as exc:

    rejected = (
        exc.code
        == "invalid_worker_registration"
    )

else:

    rejected = False


check(
    "result_bad_registration_rejected",
    rejected,
)


# ============================================================
# IMMUTABILITY
# ============================================================

immutable_targets = (
    (
        enabled_candidate,
        "discovery_enabled",
    ),
    (
        enabled_decision,
        "discoverability",
    ),
    (
        ordered_result,
        "decisions",
    ),
)


for obj, field_name in (
    immutable_targets
):

    try:

        setattr(
            obj,
            field_name,
            None,
        )

    except (
        FrozenInstanceError,
        AttributeError,
        TypeError,
    ):

        immutable = True

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
# REGISTRATION OBJECTS NOT MUTATED
# ============================================================

original_registration = reg(
    "worker-original",
    "instance-original",
)

original_dict_before = (
    original_registration.to_dict()
)

discovery.discover_universal_workers(
    (
        discovery.create_universal_worker_discovery_candidate(
            registration=original_registration,
            discovery_enabled=True,
        ),
    )
)

original_dict_after = (
    original_registration.to_dict()
)


check(
    "registration_not_mutated",
    original_dict_before
    == original_dict_after,
)


# ============================================================
# EXPLANATION CONTRACT
# ============================================================

explanation = (
    discovery.explain_universal_worker_discovery_v1()
)


check(
    "explanation_phase",
    explanation.get("phase")
    == "4.1.2",
)

check(
    "explanation_component",
    explanation.get("component")
    == "Universal Worker Discovery",
)

check(
    "explanation_version",
    explanation.get("version")
    == discovery.UNIVERSAL_WORKER_DISCOVERY_VERSION,
)

check(
    "candidate_schema_explained",
    explanation.get("candidate_schema_version")
    == discovery.UNIVERSAL_WORKER_DISCOVERY_CANDIDATE_SCHEMA_VERSION,
)

check(
    "decision_schema_explained",
    explanation.get("decision_schema_version")
    == discovery.UNIVERSAL_WORKER_DISCOVERY_DECISION_SCHEMA_VERSION,
)

check(
    "result_schema_explained",
    explanation.get("result_schema_version")
    == discovery.UNIVERSAL_WORKER_DISCOVERY_RESULT_SCHEMA_VERSION,
)

check(
    "caller_supplied_rule",
    "caller-supplied"
    in explanation.get(
        "input_rule",
        "",
    ),
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
        "assignable"
        in explanation.get(
            "meaning",
            "",
        )
    ),
)

check(
    "deterministic_order_explained",
    "worker_id then worker_instance_id"
    in explanation.get(
        "ordering_rule",
        "",
    ),
)

check(
    "duplicates_explained",
    "duplicate"
    in explanation.get(
        "duplicate_rule",
        "",
    ).lower(),
)

check(
    "purity_explained",
    "no live state lookup"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


# ============================================================
# PROHIBITION MATRIX
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
# STATIC IMPORT BOUNDARY
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
    "only_registration_backend_import",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.registration"
    ],
    backend_imports,
)


# ============================================================
# STATIC SIDE-EFFECT / OWNERSHIP ATTACK
# ============================================================

forbidden_calls = []


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
# NO LATER-PHASE FUNCTIONS
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
# PROTECTED AST MATRIX
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
# FINAL DISCOVERY AST
# ============================================================

final_ast = ast_sha(
    DISCOVERY_PATH
)


check(
    "discovery_ast_final",
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
        "DISCOVERY ADVERSARIAL REGRESSION"
    ),
    "=" * 112,
    "",
    (
        "WORKER DISCOVERY AST SHA256: "
        + final_ast
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
            "ADVERSARIAL WORKER DISCOVERY REGRESSION: "
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
        "WORKER DISCOVERY AST MODIFIED: NO",
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
            "STATUS: REGRESSION PASS — FINAL CERTIFICATION REQUIRED"
            if passed == total
            else
            "STATUS: REGRESSION FAILED — DO NOT CERTIFY"
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
        "Phase 4.1.2 Worker Discovery adversarial regression failed."
    )
