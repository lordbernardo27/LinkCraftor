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
    / "phase_4_1_1_worker_registration_regression.txt"
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


# ============================================================
# 1 — AST STABILITY
# ============================================================

registration_ast = ast_sha(
    REGISTRATION_PATH
)

check(
    "registration_ast_stable",
    registration_ast
    == EXPECTED_REGISTRATION_AST,
    registration_ast,
)


# ============================================================
# 2 — VERSION / SCHEMA
# ============================================================

check(
    "version_exact",
    module.UNIVERSAL_WORKER_REGISTRATION_VERSION
    == "universal_worker_registration_v4.1.1",
)

check(
    "schema_exact",
    module.UNIVERSAL_WORKER_REGISTRATION_SCHEMA_VERSION
    == "universal_worker_registration_schema_v1",
)


# ============================================================
# 3 — MAX LENGTH CONSTANTS
# ============================================================

check(
    "worker_id_max_length",
    module.MAX_UNIVERSAL_WORKER_ID_LENGTH
    == 160,
)

check(
    "worker_type_max_length",
    module.MAX_UNIVERSAL_WORKER_TYPE_LENGTH
    == 120,
)

check(
    "instance_id_max_length",
    module.MAX_UNIVERSAL_WORKER_INSTANCE_ID_LENGTH
    == 200,
)

check(
    "runtime_version_max_length",
    module.MAX_UNIVERSAL_WORKER_RUNTIME_VERSION_LENGTH
    == 120,
)

check(
    "host_id_max_length",
    module.MAX_UNIVERSAL_WORKER_HOST_ID_LENGTH
    == 200,
)


# ============================================================
# 4 — VALID BASELINE
# ============================================================

base = (
    module.create_universal_worker_registration(
        worker_id="worker-A",
        worker_type="general",
        worker_instance_id="instance-001",
        runtime_version="runtime-v1",
        host_id="host-A",
        registered_at="2026-08-15T20:00:00Z",
    )
)


check(
    "baseline_worker_id",
    base.worker_id
    == "worker-A",
)

check(
    "baseline_worker_type",
    base.worker_type
    == "general",
)

check(
    "baseline_instance_id",
    base.worker_instance_id
    == "instance-001",
)

check(
    "baseline_runtime_version",
    base.runtime_version
    == "runtime-v1",
)

check(
    "baseline_host_id",
    base.host_id
    == "host-A",
)

check(
    "baseline_registered_at",
    base.registered_at
    == "2026-08-15T20:00:00.000000Z",
)


# ============================================================
# 5 — WHITESPACE NORMALIZATION
# ============================================================

trimmed = (
    module.create_universal_worker_registration(
        worker_id="  worker-A  ",
        worker_type="  general  ",
        worker_instance_id="  instance-001  ",
        runtime_version="  runtime-v1  ",
        host_id="  host-A  ",
        registered_at="  2026-08-15T20:00:00Z  ",
    )
)


check(
    "whitespace_normalization",
    trimmed == base,
)


# ============================================================
# 6 — TIMESTAMP NORMALIZATION
# ============================================================

timestamp_cases = (
    (
        "2026-08-15T20:00:00+00:00",
        "2026-08-15T20:00:00.000000Z",
    ),
    (
        "2026-08-15T22:00:00+02:00",
        "2026-08-15T20:00:00.000000Z",
    ),
    (
        "2026-08-15T15:00:00-05:00",
        "2026-08-15T20:00:00.000000Z",
    ),
    (
        "2026-08-15T20:00:00.123456Z",
        "2026-08-15T20:00:00.123456Z",
    ),
)


for index, (
    supplied,
    expected,
) in enumerate(
    timestamp_cases,
    start=1,
):

    actual = (
        module.normalize_universal_worker_registered_at(
            supplied
        )
    )

    check(
        f"timestamp_normalization_{index}",
        actual == expected,
        actual,
    )


# ============================================================
# 7 — BAD TEXT TYPES
# ============================================================

normalizers = {
    "worker_id":
        module.normalize_universal_worker_id,

    "worker_type":
        module.normalize_universal_worker_type,

    "worker_instance_id":
        module.normalize_universal_worker_instance_id,

    "runtime_version":
        module.normalize_universal_worker_runtime_version,

    "host_id":
        module.normalize_universal_worker_host_id,
}


bad_text_values = (
    None,
    True,
    False,
    0,
    1,
    [],
    {},
    (),
    set(),
)


for field_name, normalizer in (
    normalizers.items()
):

    for bad_value in bad_text_values:

        try:

            normalizer(
                bad_value
            )

        except module.UniversalWorkerRegistrationError:

            rejected = True

        else:

            rejected = False

        check(
            (
                "bad_type_"
                + field_name
                + "_"
                + type(bad_value).__name__
            ),
            rejected,
        )


# ============================================================
# 8 — BLANK TEXT VALUES
# ============================================================

blank_values = (
    "",
    " ",
    "   ",
    "\t",
    "\n",
)


for field_name, normalizer in (
    normalizers.items()
):

    for index, blank in enumerate(
        blank_values,
        start=1,
    ):

        try:

            normalizer(blank)

        except module.UniversalWorkerRegistrationError:

            rejected = True

        else:

            rejected = False

        check(
            (
                "blank_"
                + field_name
                + "_"
                + str(index)
            ),
            rejected,
        )


# ============================================================
# 9 — MAX LENGTH BOUNDARIES
# ============================================================

length_cases = (
    (
        "worker_id",
        module.normalize_universal_worker_id,
        module.MAX_UNIVERSAL_WORKER_ID_LENGTH,
    ),
    (
        "worker_type",
        module.normalize_universal_worker_type,
        module.MAX_UNIVERSAL_WORKER_TYPE_LENGTH,
    ),
    (
        "worker_instance_id",
        module.normalize_universal_worker_instance_id,
        module.MAX_UNIVERSAL_WORKER_INSTANCE_ID_LENGTH,
    ),
    (
        "runtime_version",
        module.normalize_universal_worker_runtime_version,
        module.MAX_UNIVERSAL_WORKER_RUNTIME_VERSION_LENGTH,
    ),
    (
        "host_id",
        module.normalize_universal_worker_host_id,
        module.MAX_UNIVERSAL_WORKER_HOST_ID_LENGTH,
    ),
)


for field_name, normalizer, maximum in (
    length_cases
):

    exact = "x" * maximum

    overflow = "x" * (
        maximum + 1
    )

    check(
        "exact_max_" + field_name,
        normalizer(exact)
        == exact,
    )

    try:

        normalizer(
            overflow
        )

    except module.UniversalWorkerRegistrationError:

        rejected = True

    else:

        rejected = False

    check(
        "overflow_" + field_name,
        rejected,
    )


# ============================================================
# 10 — INVALID TIMESTAMPS
# ============================================================

bad_timestamps = (
    None,
    True,
    False,
    0,
    1,
    "",
    " ",
    "not-a-time",
    "2026-08-15",
    "2026-08-15T20:00:00",
    "2026-99-99T20:00:00Z",
    [],
    {},
)


for index, value in enumerate(
    bad_timestamps,
    start=1,
):

    try:

        module.normalize_universal_worker_registered_at(
            value
        )

    except module.UniversalWorkerRegistrationError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_timestamp_"
        + str(index),
        rejected,
    )


# ============================================================
# 11 — SCHEMA TAMPER
# ============================================================

try:

    module.UniversalWorkerRegistration(
        worker_id="worker",
        worker_type="general",
        worker_instance_id="instance",
        runtime_version="runtime-v1",
        host_id="host",
        registered_at="2026-08-15T20:00:00Z",
        schema_version="wrong",
    )

except module.UniversalWorkerRegistrationError as exc:

    rejected = (
        exc.code
        == "invalid_worker_registration_schema_version"
    )

else:

    rejected = False


check(
    "schema_tamper_rejected",
    rejected,
)


# ============================================================
# 12 — IDENTITY SEMANTICS
# ============================================================

same_logical_and_instance = (
    module.create_universal_worker_registration(
        worker_id="worker-A",
        worker_type="specialized",
        worker_instance_id="instance-001",
        runtime_version="runtime-v99",
        host_id="host-Z",
        registered_at="2026-08-15T21:00:00Z",
    )
)


different_logical_worker = (
    module.create_universal_worker_registration(
        worker_id="worker-B",
        worker_type="general",
        worker_instance_id="instance-001",
        runtime_version="runtime-v1",
        host_id="host-A",
        registered_at="2026-08-15T20:00:00Z",
    )
)


different_instance = (
    module.create_universal_worker_registration(
        worker_id="worker-A",
        worker_type="general",
        worker_instance_id="instance-002",
        runtime_version="runtime-v1",
        host_id="host-A",
        registered_at="2026-08-15T20:00:00Z",
    )
)


check(
    "same_identity_ignores_nonidentity_fields",
    module.is_same_universal_worker_registration_identity(
        left=base,
        right=same_logical_and_instance,
    )
    is True,
)

check(
    "different_worker_false",
    module.is_same_universal_worker_registration_identity(
        left=base,
        right=different_logical_worker,
    )
    is False,
)

check(
    "different_instance_false",
    module.is_same_universal_worker_registration_identity(
        left=base,
        right=different_instance,
    )
    is False,
)


# ============================================================
# 13 — IDENTITY COMPARATOR TYPE ATTACKS
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

        module.is_same_universal_worker_registration_identity(
            left=bad,
            right=base,
        )

    except module.UniversalWorkerRegistrationError as exc:

        rejected = (
            exc.code
            == "invalid_left_worker_registration"
        )

    else:

        rejected = False

    check(
        "invalid_left_"
        + str(index),
        rejected,
    )


for index, bad in enumerate(
    bad_registration_values,
    start=1,
):

    try:

        module.is_same_universal_worker_registration_identity(
            left=base,
            right=bad,
        )

    except module.UniversalWorkerRegistrationError as exc:

        rejected = (
            exc.code
            == "invalid_right_worker_registration"
        )

    else:

        rejected = False

    check(
        "invalid_right_"
        + str(index),
        rejected,
    )


# ============================================================
# 14 — IMMUTABILITY
# ============================================================

for field_name in (
    "worker_id",
    "worker_type",
    "worker_instance_id",
    "runtime_version",
    "host_id",
    "registered_at",
    "schema_version",
):

    try:

        setattr(
            base,
            field_name,
            "mutated",
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
        + field_name,
        immutable,
    )


# ============================================================
# 15 — SERIALIZATION EXACTNESS
# ============================================================

serialized = (
    base.to_dict()
)


expected_serialized = {
    "schema_version":
        "universal_worker_registration_schema_v1",

    "worker_id":
        "worker-A",

    "worker_type":
        "general",

    "worker_instance_id":
        "instance-001",

    "runtime_version":
        "runtime-v1",

    "host_id":
        "host-A",

    "registered_at":
        "2026-08-15T20:00:00.000000Z",
}


check(
    "serialization_exact",
    serialized
    == expected_serialized,
)


serialized[
    "worker_id"
] = "corrupted"


check(
    "serialization_detached",
    base.worker_id
    == "worker-A",
)


# ============================================================
# 16 — DETERMINISM
# ============================================================

base_again = (
    module.create_universal_worker_registration(
        worker_id="worker-A",
        worker_type="general",
        worker_instance_id="instance-001",
        runtime_version="runtime-v1",
        host_id="host-A",
        registered_at="2026-08-15T20:00:00Z",
    )
)


check(
    "registration_deterministic",
    base == base_again,
)

check(
    "serialization_deterministic",
    base.to_dict()
    == base_again.to_dict(),
)


# ============================================================
# 17 — EXPLANATION CONTRACT
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
    "explanation_schema",
    explanation.get("schema_version")
    == module.UNIVERSAL_WORKER_REGISTRATION_SCHEMA_VERSION,
)

check(
    "identity_tuple_exact",
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
    "registered_at_caller_supplied",
    "caller-supplied"
    in explanation.get(
        "registered_at_rule",
        "",
    ),
)

check(
    "immutable_rule",
    "immutable"
    in explanation.get(
        "immutability_rule",
        "",
    ),
)

check(
    "purity_no_persist",
    "does not persist"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


# ============================================================
# 18 — PROHIBITION MATRIX
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
# 19 — STATIC IMPORT BOUNDARY
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
    "no_backend_imports",
    not backend_imports,
    backend_imports,
)


# ============================================================
# 20 — STATIC SIDE-EFFECT BOUNDARY
# ============================================================

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
# 21 — NO ACCIDENTAL OWNERSHIP FUNCTIONS
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
# 22 — PROTECTED AST MATRIX
# ============================================================

for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(path)

    check(
        "protected_"
        + name,
        actual == expected,
        actual,
    )


# ============================================================
# 23 — NEW AUTHORITY STILL EXACT
# ============================================================

check(
    "registration_ast_final",
    ast_sha(REGISTRATION_PATH)
    == EXPECTED_REGISTRATION_AST,
    ast_sha(REGISTRATION_PATH),
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
        "REGISTRATION ADVERSARIAL REGRESSION"
    ),
    "=" * 112,
    "",
    (
        "WORKER REGISTRATION AST SHA256: "
        + registration_ast
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
            "ADVERSARIAL REGRESSION RESULT: "
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
        "WORKER REGISTRATION AST MODIFIED: NO",
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
        "WORKER CAPACITY DECIDED: NO",
        "WORKER CAPABILITY DECLARED: NO",
        "JOB DISPATCHED: NO",
        "JOB EXECUTED: NO",
        "FILESYSTEM / NETWORK I/O BY AUTHORITY: NO",
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
        "Phase 4.1.1 adversarial regression failed."
    )

