from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

REGISTRATION_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "registration.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_1_worker_registration_final_certification.txt"
)


EXPECTED_REGISTRATION_AST = (
    "00F0D6E620E24A7433C880B722E023AF3C2121563F8E18DFA9979E0F06A36D64"
)


PROTECTED = {
    "queue_creation": (
        ROOT / "backend/server/runtime/universal_queue/creation.py",
        "5ED908A9AFB9D102915EC1A2C8DA1D4B97D8A6CC2FDDCE3CB2EDF4E6159590BD",
    ),

    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "job_status": (
        ROOT / "backend/server/runtime/universal_jobs/status.py",
        "4636EF770005A6CCC84A37596622880C2244D4C12FFDEDAAC02078C20AA29EEE",
    ),

    "job_attempts": (
        ROOT / "backend/server/runtime/universal_jobs/attempts.py",
        "2662BC9A968D3F37B9072FA9551A70681E5CE9BEB78E65DAF6550580893DEE24",
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
# IMPORT AUTHORITY
# ============================================================

sys.path.insert(
    0,
    str(ROOT),
)

module_name = (
    "backend.server.runtime."
    "universal_worker.registration"
)

sys.modules.pop(
    module_name,
    None,
)

module = importlib.import_module(
    module_name
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


registration_ast = ast_sha(
    REGISTRATION_PATH
)


# ============================================================
# 1 — FINAL AST
# ============================================================

check(
    "worker_registration_ast",
    registration_ast
    == EXPECTED_REGISTRATION_AST,
    registration_ast,
)


# ============================================================
# 2 — VERSION / SCHEMA
# ============================================================

check(
    "version",
    module.UNIVERSAL_WORKER_REGISTRATION_VERSION
    == "universal_worker_registration_v4.1.1",
)

check(
    "schema",
    module.UNIVERSAL_WORKER_REGISTRATION_SCHEMA_VERSION
    == "universal_worker_registration_schema_v1",
)


# ============================================================
# 3 — CANONICAL RECORD
# ============================================================

record = (
    module.create_universal_worker_registration(
        worker_id="universal-runtime-worker",
        worker_type="general",
        worker_instance_id="instance-001",
        runtime_version="runtime-v1",
        host_id="host-a",
        registered_at="2026-08-15T20:00:00Z",
    )
)


check(
    "canonical_worker_id",
    record.worker_id
    == "universal-runtime-worker",
)

check(
    "canonical_worker_type",
    record.worker_type
    == "general",
)

check(
    "canonical_instance_id",
    record.worker_instance_id
    == "instance-001",
)

check(
    "canonical_runtime_version",
    record.runtime_version
    == "runtime-v1",
)

check(
    "canonical_host_id",
    record.host_id
    == "host-a",
)

check(
    "canonical_registered_at",
    record.registered_at
    == "2026-08-15T20:00:00.000000Z",
)

check(
    "canonical_identity",
    record.canonical_identity
    == (
        "universal-runtime-worker",
        "instance-001",
    ),
)


# ============================================================
# 4 — IDENTITY SEMANTICS
# ============================================================

same_identity = (
    module.create_universal_worker_registration(
        worker_id="universal-runtime-worker",
        worker_type="specialized",
        worker_instance_id="instance-001",
        runtime_version="runtime-v2",
        host_id="host-b",
        registered_at="2026-08-15T21:00:00Z",
    )
)


new_instance = (
    module.create_universal_worker_registration(
        worker_id="universal-runtime-worker",
        worker_type="general",
        worker_instance_id="instance-002",
        runtime_version="runtime-v1",
        host_id="host-a",
        registered_at="2026-08-15T20:00:00Z",
    )
)


check(
    "same_identity_true",
    module.is_same_universal_worker_registration_identity(
        left=record,
        right=same_identity,
    )
    is True,
)

check(
    "new_instance_false",
    module.is_same_universal_worker_registration_identity(
        left=record,
        right=new_instance,
    )
    is False,
)


# ============================================================
# 5 — IMMUTABILITY
# ============================================================

try:

    record.worker_id = "changed"

except Exception:

    immutable = True

else:

    immutable = False


check(
    "registration_immutable",
    immutable,
)


# ============================================================
# 6 — SERIALIZATION
# ============================================================

serialized = (
    record.to_dict()
)


check(
    "serialized_schema",
    serialized.get(
        "schema_version"
    )
    == "universal_worker_registration_schema_v1",
)

check(
    "serialized_identity",
    (
        serialized.get("worker_id"),
        serialized.get("worker_instance_id"),
    )
    == (
        "universal-runtime-worker",
        "instance-001",
    ),
)

check(
    "serialized_field_count",
    len(serialized)
    == 7,
)


# ============================================================
# 7 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    module.explain_universal_worker_registration_v1()
)


check(
    "explanation_phase",
    explanation.get("phase")
    == "4.1.1",
)

check(
    "explanation_component",
    explanation.get("component")
    == "Universal Worker Registration",
)

check(
    "explanation_version",
    explanation.get("version")
    == module.UNIVERSAL_WORKER_REGISTRATION_VERSION,
)

check(
    "identity_exact",
    tuple(
        explanation.get(
            "canonical_identity"
        )
    )
    == (
        "worker_id",
        "worker_instance_id",
    ),
)

check(
    "owned_fields_exact",
    tuple(
        explanation.get(
            "owned_fields"
        )
    )
    == (
        "worker_id",
        "worker_type",
        "worker_instance_id",
        "runtime_version",
        "host_id",
        "registered_at",
    ),
)

check(
    "registered_at_is_evidence",
    "caller-supplied"
    in explanation.get(
        "registered_at_rule",
        "",
    ),
)

check(
    "registration_is_immutable",
    "immutable"
    in explanation.get(
        "immutability_rule",
        "",
    ),
)

check(
    "registration_is_pure",
    "does not persist"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


# ============================================================
# 8 — FINAL PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not create worker pools",
    "does not declare worker capabilities",
    "does not determine worker health",
    "does not determine worker availability",
    "does not determine worker capacity",
    "does not assign jobs",
    "does not claim jobs",
    "does not lease jobs",
    "does not renew leases",
    "does not release leases",
    "does not emit heartbeats",
    "does not detect stale workers",
    "does not recover workers",
    "does not scale workers",
    "does not drain workers",
    "does not shut down workers",
    "does not dispatch jobs",
    "does not execute jobs",
    "does not register runtime handlers",
    "does not access orchestration",
    "does not access Runtime State Store",
    "does not mutate Queue Infrastructure",
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
        item
        in prohibitions,
        item,
    )


# ============================================================
# 9 — STATIC AUTHORITY BOUNDARY
# ============================================================

source = REGISTRATION_PATH.read_text(
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

        imported = (
            node.module
            or ""
        )

        if imported.startswith(
            "backend.server"
        ):

            backend_imports.append(
                imported
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
    "no_backend_imports",
    not backend_imports,
    backend_imports,
)


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

        name = node.func.id

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        name = node.func.attr

    else:

        continue

    if name in {
        "open",
        "write_text",
        "read_text",
        "mkdir",
        "unlink",
        "remove",
        "enqueue_job",
        "dequeue_job",
        "claim_job",
        "lease_job",
        "renew_lease",
        "release_lease",
        "dispatch_job",
        "execute_job",
        "worker_heartbeat",
        "register_handler",
        "register_worker",
        "save_job",
        "get_job",
        "write_json",
        "read_json",
    }:

        forbidden_calls.append(
            (
                name,
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
# 10 — NO CROSS-PHASE OWNERSHIP
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
    "discover",
    "assign",
    "lease",
    "heartbeat",
    "health",
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
# 11 — PROTECTED AST MATRIX
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
# 12 — FINAL WORKER REGISTRATION FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_4_1_1_worker_registration",
        module.UNIVERSAL_WORKER_REGISTRATION_VERSION,
        module.UNIVERSAL_WORKER_REGISTRATION_SCHEMA_VERSION,
        registration_ast,
        "worker_id",
        "worker_instance_id",
        "worker_type",
        "runtime_version",
        "host_id",
        "registered_at",
    )
)


worker_registration_fingerprint = (
    hashlib.sha256(
        fingerprint_material.encode(
            "utf-8"
        )
    ).hexdigest().upper()
)


check(
    "fingerprint_generated",
    len(
        worker_registration_fingerprint
    )
    == 64,
    worker_registration_fingerprint,
)


# ============================================================
# 13 — FINAL AST RECHECK
# ============================================================

final_ast = ast_sha(
    REGISTRATION_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_REGISTRATION_AST,
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
        "PHASE 4.1.1 — UNIVERSAL WORKER "
        "REGISTRATION FINAL CERTIFICATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER REGISTRATION AST SHA256: "
        + registration_ast
    ),
    (
        "WORKER REGISTRATION FINGERPRINT: "
        + worker_registration_fingerprint
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
            "FINAL WORKER REGISTRATION CERTIFICATION: "
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
        "WORKER REGISTRATION MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB AUTHORITIES MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "LIVE WORKER REGISTRY CREATED: NO",
        "WORKER DISCOVERED: NO",
        "JOB ASSIGNED: NO",
        "JOB CLAIMED: NO",
        "JOB LEASED: NO",
        "WORKER HEARTBEAT EMITTED: NO",
        "WORKER HEALTH DECIDED: NO",
        "WORKER RECOVERY PERFORMED: NO",
        "WORKER SCALED: NO",
        "WORKER DRAINED: NO",
        "WORKER SHUT DOWN: NO",
        "WORKER POOL CREATED: NO",
        "WORKER CAPABILITY DECLARED: NO",
        "WORKER CAPACITY DECIDED: NO",
        "JOB DISPATCHED: NO",
        "JOB EXECUTED: NO",
        "FILESYSTEM / NETWORK I/O BY AUTHORITY: NO",
        "",
        (
            "PHASE 4.1.1 FREEZE CANDIDATE: "
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
        "Phase 4.1.1 final certification failed."
    )
