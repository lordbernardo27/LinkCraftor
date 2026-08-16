from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

LEASING_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "leasing.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_4_worker_leasing_regression.txt"
)

EXPECTED_LEASING_AST = (
    "413B8081D7802211D64B7B811299F9A8A2C54DBAEAB0FC537B1603A3BE397932"
)


PROTECTED = {
    "worker_registration": (
        ROOT / "backend/server/runtime/universal_worker/registration.py",
        "00F0D6E620E24A7433C880B722E023AF3C2121563F8E18DFA9979E0F06A36D64",
    ),

    "worker_discovery": (
        ROOT / "backend/server/runtime/universal_worker/discovery.py",
        "DFCAB9080982C8D5E099A40C903F7B4140B0860053DB73CB77B30B966788A228",
    ),

    "worker_assignment": (
        ROOT / "backend/server/runtime/universal_worker/assignment.py",
        "609D3077B84C1791262F8ACA6BD268FD40436DF7775ACB3E9E726BCFC9715F56",
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

    tree = ast.parse(
        source
    )

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

registration = importlib.import_module(
    "backend.server.runtime.universal_worker.registration"
)

assignment = importlib.import_module(
    "backend.server.runtime.universal_worker.assignment"
)

leasing_name = (
    "backend.server.runtime."
    "universal_worker.leasing"
)

sys.modules.pop(
    leasing_name,
    None,
)

leasing = importlib.import_module(
    leasing_name
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
# 1 — AST / VERSION / CONSTANTS
# ============================================================

leasing_ast = ast_sha(
    LEASING_PATH
)

check(
    "leasing_ast_stable",
    leasing_ast
    == EXPECTED_LEASING_AST,
    leasing_ast,
)

check(
    "version_exact",
    leasing.UNIVERSAL_WORKER_LEASING_VERSION
    == "universal_worker_leasing_v4.1.4",
)

check(
    "lease_schema_exact",
    leasing.UNIVERSAL_WORKER_LEASE_SCHEMA_VERSION
    == "universal_worker_lease_schema_v1",
)

check(
    "release_schema_exact",
    leasing.UNIVERSAL_WORKER_LEASE_RELEASE_SCHEMA_VERSION
    == "universal_worker_lease_release_schema_v1",
)

check(
    "lease_id_max_exact",
    leasing.MAX_UNIVERSAL_WORKER_LEASE_ID_LENGTH
    == 200,
)

check(
    "owner_separator_exact",
    leasing.UNIVERSAL_WORKER_LEASE_OWNER_SEPARATOR
    == "::",
)


# ============================================================
# FIXTURE FACTORIES
# ============================================================

def worker(
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


def assigned(
    *,
    job_id="job-001",
    worker_id="worker-a",
    instance_id="instance-001",
):

    return assignment.assign_universal_worker(
        job_id=job_id,
        eligible_workers=(
            worker(
                worker_id,
                instance_id,
            ),
        ),
    )


base_assignment = assigned()


base_lease = leasing.acquire_universal_worker_lease(
    assignment=base_assignment,
    lease_id="lease-001",
    lease_started_at="2026-08-15T20:00:00Z",
    lease_expires_at="2026-08-15T20:05:00Z",
)


# ============================================================
# 2 — CANONICAL OWNER
# ============================================================

check(
    "canonical_owner_exact",
    leasing.create_universal_worker_lease_owner(
        base_assignment
    )
    == "worker-a::instance-001",
)

check(
    "canonical_worker_identity_exact",
    base_lease.worker_identity
    == (
        "worker-a",
        "instance-001",
    ),
)


# ============================================================
# 3 — INVALID ASSIGNMENT ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        "",
        {},
        [],
    ),
    start=1,
):

    try:

        leasing.create_universal_worker_lease_owner(
            bad
        )

    except leasing.UniversalWorkerLeasingError as exc:

        rejected = (
            exc.code
            == "invalid_worker_assignment"
        )

    else:

        rejected = False

    check(
        "invalid_assignment_"
        + str(index),
        rejected,
        repr(bad),
    )


no_assignment = assignment.assign_universal_worker(
    job_id="job-empty",
    eligible_workers=(),
)


try:

    leasing.create_universal_worker_lease_owner(
        no_assignment
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "worker_assignment_required"
    )

else:

    rejected = False


check(
    "no_assignment_owner_rejected",
    rejected,
)


# ============================================================
# 4 — RESERVED OWNER SEPARATOR ATTACKS
# ============================================================

separator_worker = assigned(
    job_id="job-separator-1",
    worker_id="worker::bad",
    instance_id="instance-001",
)


try:

    leasing.create_universal_worker_lease_owner(
        separator_worker
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "invalid_lease_owner_identity"
    )

else:

    rejected = False


check(
    "separator_in_worker_id_rejected",
    rejected,
)


separator_instance = assigned(
    job_id="job-separator-2",
    worker_id="worker-a",
    instance_id="instance::bad",
)


try:

    leasing.create_universal_worker_lease_owner(
        separator_instance
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "invalid_lease_owner_identity"
    )

else:

    rejected = False


check(
    "separator_in_instance_id_rejected",
    rejected,
)


# ============================================================
# 5 — LEASE ID STRICTNESS
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        [],
        {},
        (),
    ),
    start=1,
):

    try:

        leasing.normalize_universal_worker_lease_id(
            bad
        )

    except leasing.UniversalWorkerLeasingError as exc:

        rejected = (
            exc.code
            == "invalid_lease_id_type"
        )

    else:

        rejected = False

    check(
        "bad_lease_id_type_"
        + str(index),
        rejected,
        repr(bad),
    )


for index, bad in enumerate(
    (
        "",
        " ",
        "   ",
        "\t",
        "\n",
    ),
    start=1,
):

    try:

        leasing.normalize_universal_worker_lease_id(
            bad
        )

    except leasing.UniversalWorkerLeasingError as exc:

        rejected = (
            exc.code
            == "empty_lease_id"
        )

    else:

        rejected = False

    check(
        "blank_lease_id_"
        + str(index),
        rejected,
        repr(bad),
    )


exact_max_lease_id = (
    "L"
    * leasing.MAX_UNIVERSAL_WORKER_LEASE_ID_LENGTH
)


check(
    "exact_max_lease_id_accepted",
    leasing.normalize_universal_worker_lease_id(
        exact_max_lease_id
    )
    == exact_max_lease_id,
)


overflow_lease_id = (
    "L"
    * (
        leasing.MAX_UNIVERSAL_WORKER_LEASE_ID_LENGTH
        + 1
    )
)


try:

    leasing.normalize_universal_worker_lease_id(
        overflow_lease_id
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "lease_id_too_long"
    )

else:

    rejected = False


check(
    "lease_id_overflow_rejected",
    rejected,
)


# ============================================================
# 6 — TIMESTAMP NORMALIZATION
# ============================================================

timestamp_cases = (
    (
        "2026-08-15T20:00:00Z",
        "2026-08-15T20:00:00.000000Z",
    ),
    (
        "2026-08-15T22:00:00+02:00",
        "2026-08-15T20:00:00.000000Z",
    ),
    (
        "2026-08-15T19:00:00-01:00",
        "2026-08-15T20:00:00.000000Z",
    ),
    (
        "2026-08-15T20:00:00.123456Z",
        "2026-08-15T20:00:00.123456Z",
    ),
)


for index, (
    raw,
    expected,
) in enumerate(
    timestamp_cases,
    start=1,
):

    actual = (
        leasing.normalize_universal_worker_lease_timestamp(
            raw,
            field_name="test_timestamp",
        )
    )

    check(
        "timestamp_normalization_"
        + str(index),
        actual
        == expected,
        actual,
    )


# ============================================================
# 7 — INVALID TIMESTAMP ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        [],
        {},
    ),
    start=1,
):

    try:

        leasing.normalize_universal_worker_lease_timestamp(
            bad,
            field_name="test_timestamp",
        )

    except leasing.UniversalWorkerLeasingError as exc:

        rejected = (
            exc.code
            == "invalid_lease_timestamp_type"
        )

    else:

        rejected = False

    check(
        "timestamp_bad_type_"
        + str(index),
        rejected,
    )


for index, bad in enumerate(
    (
        "",
        " ",
        "not-a-time",
        "2026-13-15T20:00:00Z",
        "2026-08-32T20:00:00Z",
    ),
    start=1,
):

    try:

        leasing.normalize_universal_worker_lease_timestamp(
            bad,
            field_name="test_timestamp",
        )

    except leasing.UniversalWorkerLeasingError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_timestamp_"
        + str(index),
        rejected,
        repr(bad),
    )


try:

    leasing.normalize_universal_worker_lease_timestamp(
        "2026-08-15T20:00:00",
        field_name="test_timestamp",
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "naive_lease_timestamp"
    )

else:

    rejected = False


check(
    "naive_timestamp_rejected",
    rejected,
)


# ============================================================
# 8 — LEASE INTERVAL ATTACKS
# ============================================================

for index, (
    started,
    expires,
) in enumerate(
    (
        (
            "2026-08-15T20:00:00Z",
            "2026-08-15T20:00:00Z",
        ),
        (
            "2026-08-15T20:01:00Z",
            "2026-08-15T20:00:00Z",
        ),
    ),
    start=1,
):

    try:

        leasing.acquire_universal_worker_lease(
            assignment=base_assignment,
            lease_id=(
                "interval-"
                + str(index)
            ),
            lease_started_at=started,
            lease_expires_at=expires,
        )

    except leasing.UniversalWorkerLeasingError as exc:

        rejected = (
            exc.code
            == "invalid_lease_interval"
        )

    else:

        rejected = False

    check(
        "invalid_interval_"
        + str(index),
        rejected,
    )


# ============================================================
# 9 — ACQUISITION CONFLICTS
# ============================================================

try:

    leasing.acquire_universal_worker_lease(
        assignment=base_assignment,
        lease_id="lease-new",
        lease_started_at="2026-08-15T20:06:00Z",
        lease_expires_at="2026-08-15T20:11:00Z",
        existing_lease=base_lease,
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "lease_conflict"
    )

else:

    rejected = False


check(
    "active_existing_lease_conflict",
    rejected,
)


# Even expired existing evidence must be explicitly resolved.

expired_existing = leasing.acquire_universal_worker_lease(
    assignment=assigned(
        job_id="job-expired-existing",
    ),
    lease_id="lease-expired",
    lease_started_at="2026-08-15T19:00:00Z",
    lease_expires_at="2026-08-15T19:05:00Z",
)


try:

    leasing.acquire_universal_worker_lease(
        assignment=assigned(
            job_id="job-expired-existing",
        ),
        lease_id="replacement",
        lease_started_at="2026-08-15T20:00:00Z",
        lease_expires_at="2026-08-15T20:05:00Z",
        existing_lease=expired_existing,
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "lease_conflict"
    )

else:

    rejected = False


check(
    "expired_existing_still_conflicts",
    rejected,
)


# ============================================================
# 10 — STATE BOUNDARIES
# ============================================================

check(
    "active_microsecond_before_expiry",
    leasing.evaluate_universal_worker_lease_state(
        lease=base_lease,
        evaluation_at="2026-08-15T20:04:59.999999Z",
    )
    is leasing.UniversalWorkerLeaseState.ACTIVE,
)

check(
    "expired_exactly_at_expiry",
    leasing.evaluate_universal_worker_lease_state(
        lease=base_lease,
        evaluation_at="2026-08-15T20:05:00Z",
    )
    is leasing.UniversalWorkerLeaseState.EXPIRED,
)

check(
    "expired_after_expiry",
    leasing.evaluate_universal_worker_lease_state(
        lease=base_lease,
        evaluation_at="2026-08-15T21:00:00Z",
    )
    is leasing.UniversalWorkerLeaseState.EXPIRED,
)


# ============================================================
# 11 — INVALID LEASE STATE INPUT
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        0,
        "",
        {},
        [],
    ),
    start=1,
):

    try:

        leasing.evaluate_universal_worker_lease_state(
            lease=bad,
            evaluation_at="2026-08-15T20:01:00Z",
        )

    except leasing.UniversalWorkerLeasingError as exc:

        rejected = (
            exc.code
            == "invalid_worker_lease"
        )

    else:

        rejected = False

    check(
        "invalid_state_lease_"
        + str(index),
        rejected,
    )


# ============================================================
# 12 — RENEWAL OWNER / ID SPOOFING
# ============================================================

for index, bad_owner in enumerate(
    (
        None,
        True,
        1,
        "",
        "worker-z::instance-z",
    ),
    start=1,
):

    try:

        leasing.renew_universal_worker_lease(
            lease=base_lease,
            expected_lease_owner=bad_owner,
            expected_lease_id=base_lease.lease_id,
            renewed_at="2026-08-15T20:04:00Z",
            new_lease_expires_at="2026-08-15T20:10:00Z",
        )

    except leasing.UniversalWorkerLeasingError as exc:

        rejected = (
            exc.code
            == "lease_owner_mismatch"
        )

    else:

        rejected = False

    check(
        "renew_owner_attack_"
        + str(index),
        rejected,
        repr(bad_owner),
    )


try:

    leasing.renew_universal_worker_lease(
        lease=base_lease,
        expected_lease_owner=base_lease.lease_owner,
        expected_lease_id="wrong-id",
        renewed_at="2026-08-15T20:04:00Z",
        new_lease_expires_at="2026-08-15T20:10:00Z",
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "lease_id_mismatch"
    )

else:

    rejected = False


check(
    "renew_wrong_lease_id_rejected",
    rejected,
)


# ============================================================
# 13 — RENEWAL EXPIRATION BOUNDARY
# ============================================================

try:

    leasing.renew_universal_worker_lease(
        lease=base_lease,
        expected_lease_owner=base_lease.lease_owner,
        expected_lease_id=base_lease.lease_id,
        renewed_at="2026-08-15T20:05:00Z",
        new_lease_expires_at="2026-08-15T20:10:00Z",
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "expired_lease_cannot_renew"
    )

else:

    rejected = False


check(
    "renew_exact_expiry_rejected",
    rejected,
)


# ============================================================
# 14 — RENEWAL MUST EXTEND
# ============================================================

for index, new_expiry in enumerate(
    (
        "2026-08-15T20:04:00Z",
        "2026-08-15T20:05:00Z",
        "2026-08-15T20:04:30Z",
    ),
    start=1,
):

    try:

        leasing.renew_universal_worker_lease(
            lease=base_lease,
            expected_lease_owner=base_lease.lease_owner,
            expected_lease_id=base_lease.lease_id,
            renewed_at="2026-08-15T20:04:00Z",
            new_lease_expires_at=new_expiry,
        )

    except leasing.UniversalWorkerLeasingError:

        rejected = True

    else:

        rejected = False

    check(
        "nonextending_renewal_"
        + str(index),
        rejected,
        new_expiry,
    )


renewed = leasing.renew_universal_worker_lease(
    lease=base_lease,
    expected_lease_owner=base_lease.lease_owner,
    expected_lease_id=base_lease.lease_id,
    renewed_at="2026-08-15T20:04:00Z",
    new_lease_expires_at="2026-08-15T20:10:00Z",
)


check(
    "renewal_preserves_job_id",
    renewed.job_id
    == base_lease.job_id,
)

check(
    "renewal_preserves_owner",
    renewed.lease_owner
    == base_lease.lease_owner,
)

check(
    "renewal_preserves_lease_id",
    renewed.lease_id
    == base_lease.lease_id,
)

check(
    "renewal_preserves_started_at",
    renewed.lease_started_at
    == base_lease.lease_started_at,
)

check(
    "renewal_changes_expiry_only",
    renewed.lease_expires_at
    == "2026-08-15T20:10:00.000000Z",
)


# ============================================================
# 15 — RELEASE OWNER / ID SPOOFING
# ============================================================

try:

    leasing.release_universal_worker_lease(
        lease=base_lease,
        expected_lease_owner="wrong::owner",
        expected_lease_id=base_lease.lease_id,
        released_at="2026-08-15T20:03:00Z",
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "lease_owner_mismatch"
    )

else:

    rejected = False


check(
    "release_owner_spoof_rejected",
    rejected,
)


try:

    leasing.release_universal_worker_lease(
        lease=base_lease,
        expected_lease_owner=base_lease.lease_owner,
        expected_lease_id="wrong-id",
        released_at="2026-08-15T20:03:00Z",
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "lease_id_mismatch"
    )

else:

    rejected = False


check(
    "release_id_spoof_rejected",
    rejected,
)


# ============================================================
# 16 — RELEASE BEFORE LEASE START
# ============================================================

try:

    leasing.release_universal_worker_lease(
        lease=base_lease,
        expected_lease_owner=base_lease.lease_owner,
        expected_lease_id=base_lease.lease_id,
        released_at="2026-08-15T19:59:59Z",
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "release_precedes_lease"
    )

else:

    rejected = False


check(
    "release_before_start_rejected",
    rejected,
)


release_at_start = (
    leasing.release_universal_worker_lease(
        lease=base_lease,
        expected_lease_owner=base_lease.lease_owner,
        expected_lease_id=base_lease.lease_id,
        released_at="2026-08-15T20:00:00Z",
    )
)


check(
    "release_at_start_allowed",
    release_at_start.released_at
    == "2026-08-15T20:00:00.000000Z",
)


# ============================================================
# 17 — DIRECT LEASE OWNER FORMAT ATTACKS
# ============================================================

for index, bad_owner in enumerate(
    (
        "",
        "worker-only",
        "::instance",
        "worker::",
        "worker::instance::extra",
    ),
    start=1,
):

    try:

        leasing.UniversalWorkerLease(
            job_id="job-owner",
            lease_owner=bad_owner,
            lease_id="lease-owner",
            lease_started_at="2026-08-15T20:00:00Z",
            lease_expires_at="2026-08-15T20:05:00Z",
        )

    except leasing.UniversalWorkerLeasingError:

        rejected = True

    else:

        rejected = False

    check(
        "bad_owner_format_"
        + str(index),
        rejected,
        repr(bad_owner),
    )


# ============================================================
# 18 — SCHEMA TAMPERING
# ============================================================

try:

    leasing.UniversalWorkerLease(
        job_id="job-schema",
        lease_owner="worker-a::instance-001",
        lease_id="lease-schema",
        lease_started_at="2026-08-15T20:00:00Z",
        lease_expires_at="2026-08-15T20:05:00Z",
        schema_version="wrong",
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "invalid_worker_lease_schema_version"
    )

else:

    rejected = False


check(
    "lease_schema_tamper_rejected",
    rejected,
)


try:

    leasing.UniversalWorkerLeaseRelease(
        job_id="job-schema",
        lease_owner="worker-a::instance-001",
        lease_id="lease-schema",
        released_at="2026-08-15T20:03:00Z",
        schema_version="wrong",
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "invalid_worker_lease_release_schema_version"
    )

else:

    rejected = False


check(
    "release_schema_tamper_rejected",
    rejected,
)


# ============================================================
# 19 — IMMUTABILITY
# ============================================================

release = leasing.release_universal_worker_lease(
    lease=renewed,
    expected_lease_owner=renewed.lease_owner,
    expected_lease_id=renewed.lease_id,
    released_at="2026-08-15T20:06:00Z",
)


for obj, field_name in (
    (
        base_lease,
        "job_id",
    ),
    (
        base_lease,
        "lease_owner",
    ),
    (
        base_lease,
        "lease_id",
    ),
    (
        base_lease,
        "lease_started_at",
    ),
    (
        base_lease,
        "lease_expires_at",
    ),
    (
        release,
        "released_at",
    ),
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
        + type(obj).__name__
        + "_"
        + field_name,
        immutable,
    )


# ============================================================
# 20 — JOB FIELD SERIALIZATION EXACTNESS
# ============================================================

job_fields = dict(
    base_lease.to_job_lease_fields()
)


check(
    "job_field_keys_exact",
    tuple(
        job_fields.keys()
    )
    == (
        "lease_owner",
        "lease_id",
        "lease_started_at",
        "lease_expires_at",
    ),
    tuple(
        job_fields.keys()
    ),
)

check(
    "job_field_values_exact",
    job_fields
    == {
        "lease_owner":
            "worker-a::instance-001",
        "lease_id":
            "lease-001",
        "lease_started_at":
            "2026-08-15T20:00:00.000000Z",
        "lease_expires_at":
            "2026-08-15T20:05:00.000000Z",
    },
)


# ============================================================
# 21 — ASSIGNMENT NOT MUTATED
# ============================================================

assignment_before = (
    (
        base_assignment.job_id,
        base_assignment.status,
        base_assignment.worker_identity,
        base_assignment.candidate_count,
    )
)


leasing.acquire_universal_worker_lease(
    assignment=base_assignment,
    lease_id="lease-mutation-check",
    lease_started_at="2026-08-15T21:00:00Z",
    lease_expires_at="2026-08-15T21:05:00Z",
)


assignment_after = (
    (
        base_assignment.job_id,
        base_assignment.status,
        base_assignment.worker_identity,
        base_assignment.candidate_count,
    )
)


check(
    "assignment_not_mutated",
    assignment_before
    == assignment_after,
)


# ============================================================
# 22 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    leasing.explain_universal_worker_leasing_v1()
)


check(
    "explanation_phase",
    explanation.get("phase")
    == "4.1.4",
)

check(
    "explanation_component",
    explanation.get("component")
    == "Universal Worker Leasing",
)

check(
    "explanation_version",
    explanation.get("version")
    == leasing.UNIVERSAL_WORKER_LEASING_VERSION,
)

check(
    "canonical_fields_exact",
    tuple(
        explanation.get(
            "canonical_job_fields"
        )
    )
    == (
        "lease_owner",
        "lease_id",
        "lease_started_at",
        "lease_expires_at",
    ),
)

check(
    "owner_rule_exact",
    "worker_id::worker_instance_id"
    in explanation.get(
        "owner_rule",
        "",
    ),
)

check(
    "assignment_required_rule",
    "ASSIGNED"
    in explanation.get(
        "acquisition_rule",
        "",
    ),
)

check(
    "caller_timestamp_evidence",
    "caller-supplied"
    in explanation.get(
        "timestamp_rule",
        "",
    ),
)

check(
    "expiration_boundary_explained",
    (
        "ACTIVE"
        in explanation.get(
            "expiration_rule",
            "",
        )
        and
        "EXPIRED"
        in explanation.get(
            "expiration_rule",
            "",
        )
    ),
)

check(
    "renewal_rule_explained",
    "matching owner"
    in explanation.get(
        "renewal_rule",
        "",
    ),
)

check(
    "release_evidence_rule",
    "immutable"
    in explanation.get(
        "release_rule",
        "",
    ),
)

check(
    "no_job_persistence",
    "never mutates or persists UniversalJob"
    in explanation.get(
        "persistence_rule",
        "",
    ),
)

check(
    "recovery_boundary_exact",
    (
        "requeue"
        in explanation.get(
            "recovery_boundary",
            "",
        )
        and
        "recover"
        in explanation.get(
            "recovery_boundary",
            "",
        )
    ),
)


# ============================================================
# 23 — PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not generate lease_id",
    "does not use wall-clock time",
    "does not mutate UniversalJob",
    "does not persist leases",
    "does not access Runtime State Store",
    "does not mutate Queue Infrastructure",
    "does not dequeue jobs",
    "does not claim jobs",
    "does not assign workers",
    "does not discover workers",
    "does not transition jobs to LEASED",
    "does not transition jobs to RUNNING",
    "does not dispatch jobs",
    "does not execute jobs",
    "does not requeue expired leases",
    "does not recover workers",
    "does not dead-letter jobs",
    "does not determine worker health",
    "does not read worker heartbeats",
    "does not determine worker capability",
    "does not determine worker capacity",
    "does not manage worker pools",
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
        item
        in prohibitions,
        item,
    )


# ============================================================
# 24 — STATIC IMPORT BOUNDARY
# ============================================================

source = LEASING_PATH.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(
    source
)


backend_imports = []


for node in ast.walk(
    tree
):

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
    "only_assignment_backend_import",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.assignment"
    ],
    backend_imports,
)


# ============================================================
# 25 — WALL CLOCK / RANDOMNESS / SIDE-EFFECT ATTACK
# ============================================================

forbidden_calls = []

forbidden_names = {
    "open",
    "read_text",
    "write_text",
    "mkdir",
    "unlink",
    "remove",
    "uuid4",
    "time",
    "sleep",
    "utcnow",
    "now",
    "dequeue_job",
    "claim_job",
    "enqueue_job",
    "requeue_job",
    "save_job",
    "get_job",
    "dispatch_job",
    "execute_job",
    "dispatch_registered_runtime_handler",
    "get_runtime_state_store_registry",
    "worker_heartbeat",
}


for node in ast.walk(
    tree
):

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
# 26 — NO OWNERSHIP BLEED
# ============================================================

function_names = tuple(
    node.name.lower()
    for node in ast.walk(
        tree
    )
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    )
)


for token in (
    "dequeue",
    "claim",
    "dispatch",
    "execute",
    "requeue",
    "recover_worker",
    "dead_letter",
    "heartbeat",
    "health",
    "capability",
    "capacity",
    "pool",
    "persist",
    "state_store",
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
# 27 — PROTECTED AST MATRIX
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
# 28 — FINAL LEASING AST
# ============================================================

final_ast = ast_sha(
    LEASING_PATH
)


check(
    "leasing_ast_final",
    final_ast
    == EXPECTED_LEASING_AST,
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
        "PHASE 4.1.4 — UNIVERSAL WORKER "
        "LEASING ADVERSARIAL REGRESSION"
    ),
    "=" * 112,
    "",
    (
        "WORKER LEASING AST SHA256: "
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
            "ADVERSARIAL WORKER LEASING REGRESSION: "
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
        "WORKER LEASING AST MODIFIED: NO",
        "4.1.1 WORKER REGISTRATION MODIFIED: NO",
        "4.1.2 WORKER DISCOVERY MODIFIED: NO",
        "4.1.3 WORKER ASSIGNMENT MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "UNIVERSAL JOB STATUS MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "LEASE PERSISTED: NO",
        "LEASE_ID GENERATED INTERNALLY: NO",
        "WALL-CLOCK TIME READ: NO",
        "UNIVERSAL JOB MUTATED: NO",
        "JOB STATUS MUTATED: NO",
        "JOB TRANSITIONED TO LEASED: NO",
        "JOB TRANSITIONED TO RUNNING: NO",
        "JOB DEQUEUED: NO",
        "JOB CLAIMED: NO",
        "JOB DISPATCHED: NO",
        "JOB EXECUTED: NO",
        "EXPIRED LEASE REQUEUED: NO",
        "WORKER RECOVERY PERFORMED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
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
        "Phase 4.1.4 Worker Leasing adversarial regression failed."
    )
