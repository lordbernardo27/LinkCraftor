from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

HEARTBEAT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "heartbeat.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_10_worker_heartbeat_initial_implementation.txt"
)


# ============================================================
# FROZEN AUTHORITIES
# ============================================================

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

    "worker_leasing": (
        ROOT / "backend/server/runtime/universal_worker/leasing.py",
        "413B8081D7802211D64B7B811299F9A8A2C54DBAEAB0FC537B1603A3BE397932",
    ),

    "worker_health": (
        ROOT / "backend/server/runtime/universal_worker/health.py",
        "DCC43E77BDC12188DFD15044DA4DA41022B3CEF40F9C4ED06371EE66AA4E5F65",
    ),

    "worker_recovery": (
        ROOT / "backend/server/runtime/universal_worker/recovery.py",
        "C3EF5DBD81205F0087E05F43F6A67A1E0762930DAAD256F957AABC57296D19A5",
    ),

    "worker_scaling": (
        ROOT / "backend/server/runtime/universal_worker/scaling.py",
        "8EC818E4EF4CA7DBCADCFCB93FD99BC80AAD4CE8AEBE1CDE63CCC44FA8488FF6",
    ),

    "worker_shutdown": (
        ROOT / "backend/server/runtime/universal_worker/shutdown.py",
        "DB2197CA791988B01C73CE426ED29891C8BD9FE46DFEC1AC5AE79D1D131C34DD",
    ),

    "worker_pool": (
        ROOT / "backend/server/runtime/universal_worker/pool.py",
        "4BA8E641A88A5BB38F78D2B981216765B3327D639EB3BC78E5294C152E84A308",
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

    "runtime_shutdown_process": (
        ROOT / "backend/server/runtime/runtime_shutdown_process.py",
        "7A159E206C73157064B70D15A1CE4A97AB3D77EBBC77B01A2554BC34224EB272",
    ),

    "runtime_lifecycle_manager": (
        ROOT / "backend/server/runtime/runtime_lifecycle_manager.py",
        "E6200CA0938B5D578954024D6E76E343FB39D9329CFD3ABE4B3AEF86E8204034",
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


# Existing heartbeat-adjacent surfaces discovered by scan.
# These are captured before implementation and then rechecked.
DYNAMIC_PROTECTED = {
    "orchestration_models": (
        ROOT
        / "backend"
        / "server"
        / "orchestration"
        / "models.py"
    ),

    "tms_orchestration_governance": (
        ROOT
        / "backend"
        / "server"
        / "tms"
        / "orchestration_governance.py"
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


dynamic_asts = {}


for name, path in (
    DYNAMIC_PROTECTED.items()
):

    if not path.exists():

        raise SystemExit(
            "Heartbeat-adjacent protected surface missing: "
            + str(path)
        )

    dynamic_asts[
        name
    ] = ast_sha(
        path
    )


for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(
        path
    )

    if actual != expected:

        raise SystemExit(
            (
                "Protected authority mismatch before "
                "4.1.10 implementation: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


# ============================================================
# PRODUCTION AUTHORITY
# ============================================================

SOURCE = r'''from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.universal_worker.registration import (
    UniversalWorkerRegistration,
    normalize_universal_worker_id,
    normalize_universal_worker_instance_id,
    normalize_universal_worker_type,
)


UNIVERSAL_WORKER_HEARTBEAT_VERSION = (
    "universal_worker_heartbeat_v4.1.10"
)

UNIVERSAL_WORKER_HEARTBEAT_SCHEMA_VERSION = (
    "universal_worker_heartbeat_schema_v1"
)

MAX_UNIVERSAL_WORKER_HEARTBEAT_SEQUENCE = (
    2_147_483_647
)

UNIVERSAL_WORKER_HEARTBEAT_IDENTITY_SEPARATOR = (
    "::"
)


class UniversalWorkerHeartbeatError(
    ValueError
):

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:

        super().__init__(
            message
        )

        self.code = str(
            code
        )

        self.value = value


def normalize_universal_worker_heartbeat_timestamp(
    value: Any,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalWorkerHeartbeatError(
            "heartbeat_at must be str.",
            code="invalid_worker_heartbeat_timestamp_type",
            value=value,
        )

    normalized = value.strip()

    if not normalized:

        raise UniversalWorkerHeartbeatError(
            "heartbeat_at must not be empty.",
            code="empty_worker_heartbeat_timestamp",
            value=value,
        )

    parse_value = normalized

    if parse_value.endswith(
        "Z"
    ):

        parse_value = (
            parse_value[:-1]
            + "+00:00"
        )

    try:

        parsed = datetime.fromisoformat(
            parse_value
        )

    except ValueError as exc:

        raise UniversalWorkerHeartbeatError(
            (
                "heartbeat_at must be a valid "
                "ISO-8601 timestamp."
            ),
            code="invalid_worker_heartbeat_timestamp",
            value=value,
        ) from exc

    if (
        parsed.tzinfo is None
        or
        parsed.utcoffset() is None
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "heartbeat_at must be "
                "timezone-aware UTC."
            ),
            code="naive_worker_heartbeat_timestamp",
            value=value,
        )

    if parsed.utcoffset() != timedelta(0):

        raise UniversalWorkerHeartbeatError(
            (
                "heartbeat_at must use UTC."
            ),
            code="non_utc_worker_heartbeat_timestamp",
            value=value,
        )

    canonical = (
        parsed.astimezone(
            timezone.utc
        )
        .isoformat()
    )

    return canonical


def _parse_canonical_heartbeat_timestamp(
    value: str,
) -> datetime:

    return datetime.fromisoformat(
        value
    )


def normalize_universal_worker_heartbeat_sequence(
    value: Any,
) -> int:

    if (
        type(value) is not int
        or
        value < 1
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "sequence must be an integer "
                "greater than or equal to 1."
            ),
            code="invalid_worker_heartbeat_sequence",
            value=value,
        )

    if (
        value
        > MAX_UNIVERSAL_WORKER_HEARTBEAT_SEQUENCE
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "sequence exceeds the supported "
                "maximum."
            ),
            code="worker_heartbeat_sequence_too_large",
            value=value,
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerHeartbeat:

    worker_id: str

    worker_instance_id: str

    worker_type: str

    heartbeat_at: str

    sequence: int

    schema_version: str = (
        UNIVERSAL_WORKER_HEARTBEAT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "worker_id",
            normalize_universal_worker_id(
                self.worker_id
            ),
        )

        object.__setattr__(
            self,
            "worker_instance_id",
            normalize_universal_worker_instance_id(
                self.worker_instance_id
            ),
        )

        object.__setattr__(
            self,
            "worker_type",
            normalize_universal_worker_type(
                self.worker_type
            ),
        )

        object.__setattr__(
            self,
            "heartbeat_at",
            normalize_universal_worker_heartbeat_timestamp(
                self.heartbeat_at
            ),
        )

        object.__setattr__(
            self,
            "sequence",
            normalize_universal_worker_heartbeat_sequence(
                self.sequence
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_HEARTBEAT_SCHEMA_VERSION
        ):

            raise UniversalWorkerHeartbeatError(
                (
                    "Invalid Universal Worker "
                    "Heartbeat schema_version."
                ),
                code=(
                    "invalid_worker_heartbeat_"
                    "schema_version"
                ),
                value=self.schema_version,
            )

    @property
    def worker_identity(
        self,
    ) -> str:

        return (
            self.worker_id
            + UNIVERSAL_WORKER_HEARTBEAT_IDENTITY_SEPARATOR
            + self.worker_instance_id
        )


def validate_universal_worker_heartbeat_progression(
    *,
    previous: UniversalWorkerHeartbeat,
    current: UniversalWorkerHeartbeat,
) -> None:

    if not isinstance(
        previous,
        UniversalWorkerHeartbeat,
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "previous must be "
                "UniversalWorkerHeartbeat."
            ),
            code="invalid_previous_worker_heartbeat",
            value=previous,
        )

    if not isinstance(
        current,
        UniversalWorkerHeartbeat,
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "current must be "
                "UniversalWorkerHeartbeat."
            ),
            code="invalid_current_worker_heartbeat",
            value=current,
        )

    if (
        previous.worker_identity
        != current.worker_identity
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "Heartbeat progression requires "
                "the same worker identity."
            ),
            code="worker_heartbeat_identity_mismatch",
            value={
                "previous":
                    previous.worker_identity,

                "current":
                    current.worker_identity,
            },
        )

    if (
        previous.worker_type
        != current.worker_type
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "Heartbeat progression requires "
                "the same worker_type."
            ),
            code="worker_heartbeat_type_mismatch",
            value={
                "previous":
                    previous.worker_type,

                "current":
                    current.worker_type,
            },
        )

    if (
        current.sequence
        == previous.sequence
    ):

        raise UniversalWorkerHeartbeatError(
            "Duplicate heartbeat sequence.",
            code="duplicate_worker_heartbeat_sequence",
            value=current.sequence,
        )

    if (
        current.sequence
        < previous.sequence
    ):

        raise UniversalWorkerHeartbeatError(
            "Out-of-order heartbeat sequence.",
            code="out_of_order_worker_heartbeat_sequence",
            value={
                "previous":
                    previous.sequence,

                "current":
                    current.sequence,
            },
        )

    previous_at = (
        _parse_canonical_heartbeat_timestamp(
            previous.heartbeat_at
        )
    )

    current_at = (
        _parse_canonical_heartbeat_timestamp(
            current.heartbeat_at
        )
    )

    if (
        current_at
        <= previous_at
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "heartbeat_at must increase "
                "across heartbeat progression."
            ),
            code="non_increasing_worker_heartbeat_timestamp",
            value={
                "previous":
                    previous.heartbeat_at,

                "current":
                    current.heartbeat_at,
            },
        )


def create_universal_worker_heartbeat(
    *,
    registration: UniversalWorkerRegistration,
    heartbeat_at: str,
    sequence: int,
    previous_heartbeat: UniversalWorkerHeartbeat | None = None,
) -> UniversalWorkerHeartbeat:

    if not isinstance(
        registration,
        UniversalWorkerRegistration,
    ):

        raise UniversalWorkerHeartbeatError(
            (
                "registration must be "
                "UniversalWorkerRegistration."
            ),
            code="invalid_worker_heartbeat_registration",
            value=registration,
        )

    heartbeat = (
        UniversalWorkerHeartbeat(
            worker_id=(
                registration.worker_id
            ),
            worker_instance_id=(
                registration.worker_instance_id
            ),
            worker_type=(
                registration.worker_type
            ),
            heartbeat_at=heartbeat_at,
            sequence=sequence,
        )
    )

    if previous_heartbeat is not None:

        validate_universal_worker_heartbeat_progression(
            previous=previous_heartbeat,
            current=heartbeat,
        )

    return heartbeat


def explain_universal_worker_heartbeat_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.10",

            "component":
                "Universal Worker Heartbeats",

            "version":
                UNIVERSAL_WORKER_HEARTBEAT_VERSION,

            "schema_version":
                UNIVERSAL_WORKER_HEARTBEAT_SCHEMA_VERSION,

            "identity_rule": (
                "heartbeat identity is the canonical "
                "Worker Registration identity "
                "(worker_id, worker_instance_id)"
            ),

            "registration_rule": (
                "canonical heartbeat creation consumes "
                "immutable UniversalWorkerRegistration "
                "identity evidence"
            ),

            "timestamp_rule": (
                "heartbeat_at is caller-supplied, "
                "timezone-aware UTC and deterministic; "
                "4.1.10 does not read the wall clock"
            ),

            "sequence_rule": (
                "heartbeat sequence is caller-supplied "
                "and strictly increases when prior "
                "heartbeat evidence is supplied"
            ),

            "duplicate_rule": (
                "an equal sequence relative to the "
                "supplied prior heartbeat is rejected "
                "as duplicate"
            ),

            "ordering_rule": (
                "a lower sequence or non-increasing "
                "heartbeat timestamp relative to the "
                "supplied prior heartbeat is rejected"
            ),

            "prior_evidence_rule": (
                "progression validation occurs only "
                "against caller-supplied prior heartbeat "
                "evidence for the same worker identity"
            ),

            "interval_boundary": (
                "heartbeat emission interval and "
                "frequency configuration remain "
                "outside 4.1.10"
            ),

            "freshness_boundary": (
                "4.1.11 Stale Worker Detection owns "
                "heartbeat age, freshness and stale "
                "classification"
            ),

            "health_boundary": (
                "4.1.5 Worker Health remains separate; "
                "heartbeat evidence does not classify "
                "HEALTHY, DEGRADED, UNHEALTHY or UNKNOWN"
            ),

            "recovery_boundary": (
                "4.1.6 Worker Recovery remains separate; "
                "heartbeat evidence does not authorize "
                "or initiate recovery"
            ),

            "legacy_runtime_boundary": (
                "4.1.10 does not replace or invoke the "
                "existing universal_runtime_infrastructure "
                "worker_heartbeat filesystem publisher"
            ),

            "orchestration_boundary": (
                "4.1.10 does not replace or mutate "
                "existing orchestration WorkerHeartbeat "
                "or TMS WorkerStatus mechanisms"
            ),

            "payload_boundary": (
                "canonical heartbeat evidence does not "
                "carry workspace, current job, lease, "
                "pool, health, capability or capacity "
                "state"
            ),

            "persistence_boundary": (
                "4.1.10 does not persist heartbeat "
                "evidence or access Runtime State Store"
            ),

            "purity_rule": (
                "Worker Heartbeats is deterministic over "
                "caller-supplied evidence and performs "
                "no filesystem, network, clock, thread, "
                "persistence or runtime mutation"
            ),

            "prohibitions": (
                "does not generate heartbeat timestamps",
                "does not read the wall clock",
                "does not define heartbeat interval",
                "does not sleep between heartbeats",
                "does not run a heartbeat loop",
                "does not start heartbeat threads",
                "does not publish heartbeat over network",
                "does not write heartbeat files",
                "does not access Runtime State Store",
                "does not persist heartbeat evidence",
                "does not calculate heartbeat age",
                "does not calculate heartbeat freshness",
                "does not detect stale workers",
                "does not determine worker liveness",
                "does not determine worker health",
                "does not initiate worker recovery",
                "does not release worker leases",
                "does not requeue jobs",
                "does not cancel jobs",
                "does not mutate Worker Registration",
                "does not modify Worker Pool membership",
                "does not discover workers",
                "does not assign workers",
                "does not scale workers",
                "does not shut down workers",
                "does not drain workers",
                "does not inspect worker capabilities",
                "does not calculate worker capacity",
                "does not include current job state",
                "does not include workspace state",
                "does not invoke legacy runtime heartbeat publisher",
                "does not mutate orchestration heartbeat models",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_HEARTBEAT_VERSION",
    "UNIVERSAL_WORKER_HEARTBEAT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_HEARTBEAT_SEQUENCE",
    "UNIVERSAL_WORKER_HEARTBEAT_IDENTITY_SEPARATOR",
    "UniversalWorkerHeartbeatError",
    "UniversalWorkerHeartbeat",
    "normalize_universal_worker_heartbeat_timestamp",
    "normalize_universal_worker_heartbeat_sequence",
    "validate_universal_worker_heartbeat_progression",
    "create_universal_worker_heartbeat",
    "explain_universal_worker_heartbeat_v1",
]
'''


ast.parse(
    SOURCE
)

HEARTBEAT_PATH.write_text(
    SOURCE,
    encoding="utf-8",
)


# ============================================================
# IMPORT
# ============================================================

sys.path.insert(
    0,
    str(ROOT),
)

registration = importlib.import_module(
    "backend.server.runtime.universal_worker.registration"
)

module_name = (
    "backend.server.runtime."
    "universal_worker.heartbeat"
)

sys.modules.pop(
    module_name,
    None,
)

heartbeat = importlib.import_module(
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


def make_registration(
    worker_id="worker-a",
    worker_instance_id="instance-1",
    worker_type="semantic_worker",
):

    return registration.create_universal_worker_registration(
        worker_id=worker_id,
        worker_type=worker_type,
        worker_instance_id=worker_instance_id,
        runtime_version="runtime-v1",
        host_id="host-1",
        registered_at="2026-08-17T00:00:00+00:00",
    )


# ============================================================
# CONSTANTS
# ============================================================

check(
    "version",
    heartbeat.UNIVERSAL_WORKER_HEARTBEAT_VERSION
    == "universal_worker_heartbeat_v4.1.10",
)

check(
    "schema",
    heartbeat.UNIVERSAL_WORKER_HEARTBEAT_SCHEMA_VERSION
    == "universal_worker_heartbeat_schema_v1",
)

check(
    "max_sequence",
    heartbeat.MAX_UNIVERSAL_WORKER_HEARTBEAT_SEQUENCE
    == 2_147_483_647,
)

check(
    "identity_separator",
    heartbeat.UNIVERSAL_WORKER_HEARTBEAT_IDENTITY_SEPARATOR
    == "::",
)


# ============================================================
# TIMESTAMP NORMALIZATION
# ============================================================

check(
    "timestamp_z_normalized",
    heartbeat.normalize_universal_worker_heartbeat_timestamp(
        "2026-08-17T00:10:00Z"
    )
    == "2026-08-17T00:10:00+00:00",
)

check(
    "timestamp_utc_offset_preserved_canonically",
    heartbeat.normalize_universal_worker_heartbeat_timestamp(
        "2026-08-17T00:10:00+00:00"
    )
    == "2026-08-17T00:10:00+00:00",
)


for bad in (
    None,
    True,
    False,
    0,
    1,
    [],
    {},
    (),
):

    try:

        heartbeat.normalize_universal_worker_heartbeat_timestamp(
            bad
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "invalid_worker_heartbeat_timestamp_type"
        )

    else:

        rejected = False

    check(
        "timestamp_bad_type_"
        + repr(bad),
        rejected,
    )


for bad in (
    "",
    " ",
    "\t",
    "\n",
):

    try:

        heartbeat.normalize_universal_worker_heartbeat_timestamp(
            bad
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "empty_worker_heartbeat_timestamp"
        )

    else:

        rejected = False

    check(
        "timestamp_blank_"
        + repr(bad),
        rejected,
    )


for bad in (
    "not-a-date",
    "2026-99-99",
):

    try:

        heartbeat.normalize_universal_worker_heartbeat_timestamp(
            bad
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "invalid_worker_heartbeat_timestamp"
        )

    else:

        rejected = False

    check(
        "timestamp_invalid_"
        + repr(bad),
        rejected,
    )


try:

    heartbeat.normalize_universal_worker_heartbeat_timestamp(
        "2026-08-17T00:10:00"
    )

except heartbeat.UniversalWorkerHeartbeatError as exc:

    rejected = (
        exc.code
        == "naive_worker_heartbeat_timestamp"
    )

else:

    rejected = False


check(
    "naive_timestamp_rejected",
    rejected,
)


try:

    heartbeat.normalize_universal_worker_heartbeat_timestamp(
        "2026-08-17T01:10:00+01:00"
    )

except heartbeat.UniversalWorkerHeartbeatError as exc:

    rejected = (
        exc.code
        == "non_utc_worker_heartbeat_timestamp"
    )

else:

    rejected = False


check(
    "non_utc_timestamp_rejected",
    rejected,
)


# ============================================================
# SEQUENCE VALIDATION
# ============================================================

for good in (
    1,
    2,
    100,
    heartbeat.MAX_UNIVERSAL_WORKER_HEARTBEAT_SEQUENCE,
):

    check(
        "sequence_valid_"
        + str(good),
        heartbeat.normalize_universal_worker_heartbeat_sequence(
            good
        )
        == good,
    )


for bad in (
    None,
    True,
    False,
    0,
    -1,
    -100,
    1.0,
    "",
    "1",
    [],
    {},
    (),
):

    try:

        heartbeat.normalize_universal_worker_heartbeat_sequence(
            bad
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "invalid_worker_heartbeat_sequence"
        )

    else:

        rejected = False

    check(
        "sequence_invalid_"
        + repr(bad),
        rejected,
    )


try:

    heartbeat.normalize_universal_worker_heartbeat_sequence(
        heartbeat.MAX_UNIVERSAL_WORKER_HEARTBEAT_SEQUENCE
        + 1
    )

except heartbeat.UniversalWorkerHeartbeatError as exc:

    rejected = (
        exc.code
        == "worker_heartbeat_sequence_too_large"
    )

else:

    rejected = False


check(
    "sequence_overflow_rejected",
    rejected,
)


# ============================================================
# CREATION / IDENTITY
# ============================================================

reg = make_registration()

hb1 = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg,
        heartbeat_at="2026-08-17T00:10:00Z",
        sequence=1,
    )
)

check(
    "heartbeat_worker_id",
    hb1.worker_id
    == "worker-a",
)

check(
    "heartbeat_instance_id",
    hb1.worker_instance_id
    == "instance-1",
)

check(
    "heartbeat_worker_type",
    hb1.worker_type
    == "semantic_worker",
)

check(
    "heartbeat_identity",
    hb1.worker_identity
    == "worker-a::instance-1",
)

check(
    "heartbeat_timestamp",
    hb1.heartbeat_at
    == "2026-08-17T00:10:00+00:00",
)

check(
    "heartbeat_sequence",
    hb1.sequence
    == 1,
)


for bad in (
    None,
    True,
    False,
    0,
    "",
    [],
    {},
    (),
):

    try:

        heartbeat.create_universal_worker_heartbeat(
            registration=bad,
            heartbeat_at="2026-08-17T00:10:00Z",
            sequence=1,
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "invalid_worker_heartbeat_registration"
        )

    else:

        rejected = False

    check(
        "invalid_registration_"
        + repr(bad),
        rejected,
    )


# ============================================================
# VALID PROGRESSION
# ============================================================

hb2 = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg,
        heartbeat_at="2026-08-17T00:10:01Z",
        sequence=2,
        previous_heartbeat=hb1,
    )
)

check(
    "valid_progression_sequence",
    hb2.sequence
    == 2,
)

check(
    "valid_progression_timestamp",
    hb2.heartbeat_at
    == "2026-08-17T00:10:01+00:00",
)


# Sequence jumps are allowed: strictly increasing,
# not necessarily contiguous.
hb10 = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg,
        heartbeat_at="2026-08-17T00:10:10Z",
        sequence=10,
        previous_heartbeat=hb2,
    )
)

check(
    "sequence_jump_allowed",
    hb10.sequence
    == 10,
)


# ============================================================
# DUPLICATE / OUT-OF-ORDER SEQUENCE
# ============================================================

try:

    heartbeat.create_universal_worker_heartbeat(
        registration=reg,
        heartbeat_at="2026-08-17T00:10:02Z",
        sequence=1,
        previous_heartbeat=hb1,
    )

except heartbeat.UniversalWorkerHeartbeatError as exc:

    rejected = (
        exc.code
        == "duplicate_worker_heartbeat_sequence"
    )

else:

    rejected = False


check(
    "duplicate_sequence_rejected",
    rejected,
)


hb5 = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg,
        heartbeat_at="2026-08-17T00:10:05Z",
        sequence=5,
    )
)


candidate4 = (
    heartbeat.UniversalWorkerHeartbeat(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        heartbeat_at="2026-08-17T00:10:06Z",
        sequence=4,
    )
)


try:

    heartbeat.validate_universal_worker_heartbeat_progression(
        previous=hb5,
        current=candidate4,
    )

except heartbeat.UniversalWorkerHeartbeatError as exc:

    rejected = (
        exc.code
        == "out_of_order_worker_heartbeat_sequence"
    )

else:

    rejected = False


check(
    "out_of_order_sequence_rejected",
    rejected,
)


# ============================================================
# TIMESTAMP ORDERING
# ============================================================

candidate_same_time = (
    heartbeat.UniversalWorkerHeartbeat(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        heartbeat_at=hb1.heartbeat_at,
        sequence=2,
    )
)


try:

    heartbeat.validate_universal_worker_heartbeat_progression(
        previous=hb1,
        current=candidate_same_time,
    )

except heartbeat.UniversalWorkerHeartbeatError as exc:

    rejected = (
        exc.code
        == "non_increasing_worker_heartbeat_timestamp"
    )

else:

    rejected = False


check(
    "equal_timestamp_rejected",
    rejected,
)


candidate_older_time = (
    heartbeat.UniversalWorkerHeartbeat(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        heartbeat_at="2026-08-17T00:09:59Z",
        sequence=2,
    )
)


try:

    heartbeat.validate_universal_worker_heartbeat_progression(
        previous=hb1,
        current=candidate_older_time,
    )

except heartbeat.UniversalWorkerHeartbeatError as exc:

    rejected = (
        exc.code
        == "non_increasing_worker_heartbeat_timestamp"
    )

else:

    rejected = False


check(
    "older_timestamp_rejected",
    rejected,
)


# ============================================================
# IDENTITY MISMATCH
# ============================================================

other_reg = make_registration(
    worker_id="worker-b",
    worker_instance_id="instance-1",
)

other_hb = (
    heartbeat.create_universal_worker_heartbeat(
        registration=other_reg,
        heartbeat_at="2026-08-17T00:10:01Z",
        sequence=2,
    )
)


try:

    heartbeat.validate_universal_worker_heartbeat_progression(
        previous=hb1,
        current=other_hb,
    )

except heartbeat.UniversalWorkerHeartbeatError as exc:

    rejected = (
        exc.code
        == "worker_heartbeat_identity_mismatch"
    )

else:

    rejected = False


check(
    "identity_mismatch_rejected",
    rejected,
)


other_instance_reg = make_registration(
    worker_id="worker-a",
    worker_instance_id="instance-2",
)

other_instance_hb = (
    heartbeat.create_universal_worker_heartbeat(
        registration=other_instance_reg,
        heartbeat_at="2026-08-17T00:10:01Z",
        sequence=2,
    )
)


try:

    heartbeat.validate_universal_worker_heartbeat_progression(
        previous=hb1,
        current=other_instance_hb,
    )

except heartbeat.UniversalWorkerHeartbeatError as exc:

    rejected = (
        exc.code
        == "worker_heartbeat_identity_mismatch"
    )

else:

    rejected = False


check(
    "instance_mismatch_rejected",
    rejected,
)


# ============================================================
# WORKER TYPE CONTRADICTION
# ============================================================

type_contradiction = (
    heartbeat.UniversalWorkerHeartbeat(
        worker_id=hb1.worker_id,
        worker_instance_id=hb1.worker_instance_id,
        worker_type="other_worker",
        heartbeat_at="2026-08-17T00:10:01Z",
        sequence=2,
    )
)


try:

    heartbeat.validate_universal_worker_heartbeat_progression(
        previous=hb1,
        current=type_contradiction,
    )

except heartbeat.UniversalWorkerHeartbeatError as exc:

    rejected = (
        exc.code
        == "worker_heartbeat_type_mismatch"
    )

else:

    rejected = False


check(
    "worker_type_contradiction_rejected",
    rejected,
)


# ============================================================
# INVALID PROGRESSION OBJECTS
# ============================================================

for bad in (
    None,
    True,
    False,
    0,
    "",
    [],
    {},
    (),
):

    try:

        heartbeat.validate_universal_worker_heartbeat_progression(
            previous=bad,
            current=hb1,
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "invalid_previous_worker_heartbeat"
        )

    else:

        rejected = False

    check(
        "invalid_previous_"
        + repr(bad),
        rejected,
    )


for bad in (
    None,
    True,
    False,
    0,
    "",
    [],
    {},
    (),
):

    try:

        heartbeat.validate_universal_worker_heartbeat_progression(
            previous=hb1,
            current=bad,
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "invalid_current_worker_heartbeat"
        )

    else:

        rejected = False

    check(
        "invalid_current_"
        + repr(bad),
        rejected,
    )


# ============================================================
# SCHEMA TAMPERING
# ============================================================

try:

    heartbeat.UniversalWorkerHeartbeat(
        worker_id="worker-a",
        worker_instance_id="instance-1",
        worker_type="semantic_worker",
        heartbeat_at="2026-08-17T00:10:00Z",
        sequence=1,
        schema_version="tampered",
    )

except heartbeat.UniversalWorkerHeartbeatError as exc:

    rejected = (
        exc.code
        == "invalid_worker_heartbeat_schema_version"
    )

else:

    rejected = False


check(
    "schema_tamper_rejected",
    rejected,
)


# ============================================================
# IMMUTABILITY
# ============================================================

for field_name in (
    "worker_id",
    "worker_instance_id",
    "worker_type",
    "heartbeat_at",
    "sequence",
    "schema_version",
):

    try:

        setattr(
            hb1,
            field_name,
            None,
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        "immutable_heartbeat_"
        + field_name,
        immutable,
    )


# ============================================================
# DETERMINISM
# ============================================================

hb1_again = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg,
        heartbeat_at="2026-08-17T00:10:00Z",
        sequence=1,
    )
)

check(
    "deterministic_creation",
    hb1
    == hb1_again,
)


# ============================================================
# EXPLANATION CONTRACT
# ============================================================

explanation = (
    heartbeat.explain_universal_worker_heartbeat_v1()
)


check(
    "explanation_phase",
    explanation.get(
        "phase"
    )
    == "4.1.10",
)

check(
    "explanation_component",
    explanation.get(
        "component"
    )
    == "Universal Worker Heartbeats",
)

check(
    "identity_rule",
    (
        "worker_id"
        in explanation.get(
            "identity_rule",
            "",
        )
        and
        "worker_instance_id"
        in explanation.get(
            "identity_rule",
            "",
        )
    ),
)

check(
    "registration_rule",
    "UniversalWorkerRegistration"
    in explanation.get(
        "registration_rule",
        "",
    ),
)

check(
    "caller_supplied_timestamp_rule",
    "caller-supplied"
    in explanation.get(
        "timestamp_rule",
        "",
    ),
)

check(
    "no_wall_clock_rule",
    "does not read the wall clock"
    in explanation.get(
        "timestamp_rule",
        "",
    ),
)

check(
    "sequence_rule",
    "strictly increases"
    in explanation.get(
        "sequence_rule",
        "",
    ),
)

check(
    "duplicate_rule",
    "rejected"
    in explanation.get(
        "duplicate_rule",
        "",
    ),
)

check(
    "ordering_rule",
    "non-increasing"
    in explanation.get(
        "ordering_rule",
        "",
    ),
)

check(
    "interval_boundary",
    "outside 4.1.10"
    in explanation.get(
        "interval_boundary",
        "",
    ),
)

check(
    "freshness_boundary",
    "4.1.11 Stale Worker Detection"
    in explanation.get(
        "freshness_boundary",
        "",
    ),
)

check(
    "health_boundary",
    "4.1.5 Worker Health"
    in explanation.get(
        "health_boundary",
        "",
    ),
)

check(
    "recovery_boundary",
    "4.1.6 Worker Recovery"
    in explanation.get(
        "recovery_boundary",
        "",
    ),
)

check(
    "legacy_runtime_boundary",
    "does not replace or invoke"
    in explanation.get(
        "legacy_runtime_boundary",
        "",
    ),
)

check(
    "orchestration_boundary",
    "does not replace or mutate"
    in explanation.get(
        "orchestration_boundary",
        "",
    ),
)

check(
    "payload_boundary",
    (
        "workspace"
        in explanation.get(
            "payload_boundary",
            "",
        )
        and
        "current job"
        in explanation.get(
            "payload_boundary",
            "",
        )
        and
        "capacity"
        in explanation.get(
            "payload_boundary",
            "",
        )
    ),
)

check(
    "persistence_boundary",
    "does not persist"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)

check(
    "purity_rule",
    "no filesystem, network, clock, thread"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


# ============================================================
# PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not generate heartbeat timestamps",
    "does not read the wall clock",
    "does not define heartbeat interval",
    "does not sleep between heartbeats",
    "does not run a heartbeat loop",
    "does not start heartbeat threads",
    "does not publish heartbeat over network",
    "does not write heartbeat files",
    "does not access Runtime State Store",
    "does not persist heartbeat evidence",
    "does not calculate heartbeat age",
    "does not calculate heartbeat freshness",
    "does not detect stale workers",
    "does not determine worker liveness",
    "does not determine worker health",
    "does not initiate worker recovery",
    "does not release worker leases",
    "does not requeue jobs",
    "does not cancel jobs",
    "does not mutate Worker Registration",
    "does not modify Worker Pool membership",
    "does not discover workers",
    "does not assign workers",
    "does not scale workers",
    "does not shut down workers",
    "does not drain workers",
    "does not inspect worker capabilities",
    "does not calculate worker capacity",
    "does not include current job state",
    "does not include workspace state",
    "does not invoke legacy runtime heartbeat publisher",
    "does not mutate orchestration heartbeat models",
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
# IMPORT BOUNDARY
# ============================================================

source = HEARTBEAT_PATH.read_text(
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
    "backend_imports_exact",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.registration",
    ],
    backend_imports,
)


# ============================================================
# API SURFACE
# ============================================================

expected_all = (
    "UNIVERSAL_WORKER_HEARTBEAT_VERSION",
    "UNIVERSAL_WORKER_HEARTBEAT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_HEARTBEAT_SEQUENCE",
    "UNIVERSAL_WORKER_HEARTBEAT_IDENTITY_SEPARATOR",
    "UniversalWorkerHeartbeatError",
    "UniversalWorkerHeartbeat",
    "normalize_universal_worker_heartbeat_timestamp",
    "normalize_universal_worker_heartbeat_sequence",
    "validate_universal_worker_heartbeat_progression",
    "create_universal_worker_heartbeat",
    "explain_universal_worker_heartbeat_v1",
)


check(
    "api_surface_exact",
    tuple(
        heartbeat.__all__
    )
    == expected_all,
    heartbeat.__all__,
)


# ============================================================
# FORBIDDEN CALLS
# ============================================================

forbidden_names = {
    "open",
    "read_text",
    "write_text",
    "write_json",
    "mkdir",
    "unlink",
    "remove",

    "now",
    "utcnow",
    "now_iso",
    "time",
    "sleep",

    "Thread",
    "start",
    "create_task",

    "requests",
    "post",
    "send",

    "worker_heartbeat",
    "inspect_workers",

    "get_runtime_state_store_registry",

    "evaluate_universal_worker_health",
    "evaluate_universal_worker_recovery",
    "evaluate_universal_worker_scaling",
    "evaluate_universal_worker_shutdown",

    "release_universal_worker_lease",
    "renew_universal_worker_lease",
    "acquire_universal_worker_lease",

    "enqueue_job",
    "dequeue_job",
    "requeue_job",
    "cancel_job",

    "assign_universal_worker",
    "discover_universal_workers",

    "add_universal_worker_pool_member",
    "remove_universal_worker_pool_member",

    "dispatch_job",
    "execute_job",
}


forbidden_calls = []


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

        name = (
            node.func.id
        )

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        name = (
            node.func.attr
        )

    else:

        continue

    if name in forbidden_names:

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
# NO RESPONSIBILITY-BLEED FIELDS
# ============================================================

heartbeat_fields = tuple(
    field.name
    for field in __import__(
        "dataclasses"
    ).fields(
        heartbeat.UniversalWorkerHeartbeat
    )
)


expected_fields = (
    "worker_id",
    "worker_instance_id",
    "worker_type",
    "heartbeat_at",
    "sequence",
    "schema_version",
)


check(
    "heartbeat_fields_exact",
    heartbeat_fields
    == expected_fields,
    heartbeat_fields,
)


for forbidden_field in (
    "workspace_id",
    "pool_id",
    "current_job_id",
    "job_id",
    "lease_id",
    "lease_owner",
    "health",
    "health_state",
    "capabilities",
    "capacity",
    "available_slots",
    "state",
    "status",
    "stale",
    "fresh",
):

    check(
        "field_absent_"
        + forbidden_field,
        forbidden_field
        not in heartbeat_fields,
    )


# ============================================================
# PROTECTED AUTHORITIES
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


for name, path in (
    DYNAMIC_PROTECTED.items()
):

    actual = ast_sha(
        path
    )

    check(
        "protected_"
        + name,
        actual
        == dynamic_asts[
            name
        ],
        actual,
    )


# ============================================================
# HEARTBEAT AST
# ============================================================

heartbeat_ast = ast_sha(
    HEARTBEAT_PATH
)


check(
    "heartbeat_ast_generated",
    len(
        heartbeat_ast
    )
    == 64,
    heartbeat_ast,
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
        "PHASE 4.1.10 — UNIVERSAL WORKER "
        "HEARTBEATS INITIAL IMPLEMENTATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER HEARTBEAT AST SHA256: "
        + heartbeat_ast
    ),
    (
        "ORCHESTRATION MODELS AST OBSERVED: "
        + dynamic_asts[
            "orchestration_models"
        ]
    ),
    (
        "TMS ORCHESTRATION GOVERNANCE AST OBSERVED: "
        + dynamic_asts[
            "tms_orchestration_governance"
        ]
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
            "INITIAL WORKER HEARTBEAT RESULT: "
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
        "4.1.1 WORKER REGISTRATION MODIFIED: NO",
        "4.1.2 WORKER DISCOVERY MODIFIED: NO",
        "4.1.3 WORKER ASSIGNMENT MODIFIED: NO",
        "4.1.4 WORKER LEASING MODIFIED: NO",
        "4.1.5 WORKER HEALTH MODIFIED: NO",
        "4.1.6 WORKER RECOVERY MODIFIED: NO",
        "4.1.7 WORKER SCALING MODIFIED: NO",
        "4.1.8 WORKER SHUTDOWN MODIFIED: NO",
        "4.1.9 WORKER POOL MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "RUNTIME SHUTDOWN PROCESS MODIFIED: NO",
        "RUNTIME LIFECYCLE MANAGER MODIFIED: NO",
        "ORCHESTRATION MODELS MODIFIED: NO",
        "TMS ORCHESTRATION GOVERNANCE MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "WALL CLOCK READ: NO",
        "HEARTBEAT TIMESTAMP GENERATED INTERNALLY: NO",
        "HEARTBEAT INTERVAL DEFINED: NO",
        "HEARTBEAT LOOP STARTED: NO",
        "BACKGROUND THREAD STARTED: NO",
        "NETWORK HEARTBEAT PUBLISHED: NO",
        "HEARTBEAT FILE WRITTEN: NO",
        "LEGACY RUNTIME HEARTBEAT INVOKED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "HEARTBEAT EVIDENCE PERSISTED: NO",
        "HEARTBEAT AGE CALCULATED: NO",
        "HEARTBEAT FRESHNESS CALCULATED: NO",
        "STALE WORKER DETECTED: NO",
        "WORKER LIVENESS DECIDED: NO",
        "WORKER HEALTH DECIDED: NO",
        "WORKER RECOVERY INITIATED: NO",
        "LEASE RELEASED: NO",
        "JOB REQUEUED/CANCELLED: NO",
        "WORKER REGISTRATION MUTATED: NO",
        "WORKER POOL MEMBERSHIP MODIFIED: NO",
        "WORKER DISCOVERED/ASSIGNED: NO",
        "WORKER SCALING PERFORMED: NO",
        "WORKER SHUTDOWN PERFORMED: NO",
        "WORKER DRAIN PERFORMED: NO",
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER CAPACITY CALCULATED: NO",
        "",
        (
            "STATUS: INITIAL IMPLEMENTATION PASS "
            "— ADVERSARIAL REGRESSION REQUIRED"
            if passed == total
            else
            "STATUS: INITIAL IMPLEMENTATION FAILED"
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
        "Phase 4.1.10 Worker Heartbeats initial implementation failed."
    )
