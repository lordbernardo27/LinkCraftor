from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from dataclasses import fields
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

CAPACITY_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "capacity.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_14_worker_capacity_initial_implementation.txt"
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
    "worker_heartbeat": (
        ROOT / "backend/server/runtime/universal_worker/heartbeat.py",
        "A58BDEE660CA903453DA6D968A2B02FBFBE3920E9BBE6C64BC75A597DB7C11EE",
    ),
    "stale_worker_detection": (
        ROOT / "backend/server/runtime/universal_worker/stale.py",
        "22105ACBF984E26019080E53939617CE14BDF51BF5A9B149BD39E10B6B87B9DD",
    ),
    "worker_drain": (
        ROOT / "backend/server/runtime/universal_worker/drain.py",
        "629AA6B5D9269B3164A1524F3C176B2EA34CB4952A0D32F5E2EE4A7C6984FA78",
    ),
    "worker_capability": (
        ROOT / "backend/server/runtime/universal_worker/capability.py",
        "200A42478283CDAC92965EAF0DEDFAB3FAB8834F5FB734E3A4874F1EE571C51D",
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
    "orchestration_models": (
        ROOT / "backend/server/orchestration/models.py",
        "5C9FE5E4F84FA1C369CB45F74B0CB12B7E730ADA3C7CBC95B4F50EC75DC5E92D",
    ),
    "tms_orchestration_governance": (
        ROOT / "backend/server/tms/orchestration_governance.py",
        "2AAA15B7283C6F0B4BB67A47FE58F1FD0EF2815A09CA048EA0CFE7DEF232B4E1",
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


def ast_sha(path: Path) -> str:

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
                "4.1.14 implementation: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


SOURCE = r'''from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.universal_worker.registration import (
    UniversalWorkerRegistration,
    normalize_universal_worker_id,
    normalize_universal_worker_instance_id,
    normalize_universal_worker_type,
)


UNIVERSAL_WORKER_CAPACITY_VERSION = (
    "universal_worker_capacity_v4.1.14"
)

UNIVERSAL_WORKER_CAPACITY_SNAPSHOT_SCHEMA_VERSION = (
    "universal_worker_capacity_snapshot_schema_v1"
)

MAX_UNIVERSAL_WORKER_CAPACITY_COUNT = 2_147_483_647

UNIVERSAL_WORKER_CAPACITY_IDENTITY_SEPARATOR = "::"


class UniversalWorkerCapacityError(
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


def normalize_universal_worker_capacity_count(
    value: Any,
    *,
    field_name: str,
) -> int:

    if type(
        value
    ) is not int:

        raise UniversalWorkerCapacityError(
            (
                field_name
                + " must be an exact integer."
            ),
            code="invalid_worker_capacity_count",
            value=value,
        )

    if value < 0:

        raise UniversalWorkerCapacityError(
            (
                field_name
                + " must be greater than or equal to zero."
            ),
            code="invalid_worker_capacity_count",
            value=value,
        )

    if (
        value
        > MAX_UNIVERSAL_WORKER_CAPACITY_COUNT
    ):

        raise UniversalWorkerCapacityError(
            (
                field_name
                + " exceeds the supported worker "
                "capacity count."
            ),
            code="worker_capacity_count_too_large",
            value=value,
        )

    return value


def _normalize_worker_identity(
    *,
    worker_id: Any,
    worker_instance_id: Any,
    worker_type: Any,
) -> tuple[str, str, str]:

    try:

        normalized_worker_id = (
            normalize_universal_worker_id(
                worker_id
            )
        )

        normalized_instance_id = (
            normalize_universal_worker_instance_id(
                worker_instance_id
            )
        )

        normalized_worker_type = (
            normalize_universal_worker_type(
                worker_type
            )
        )

    except Exception as exc:

        raise UniversalWorkerCapacityError(
            (
                "Invalid canonical worker identity "
                "for Worker Capacity."
            ),
            code="invalid_worker_capacity_identity",
            value={
                "worker_id":
                    worker_id,

                "worker_instance_id":
                    worker_instance_id,

                "worker_type":
                    worker_type,
            },
        ) from exc

    return (
        normalized_worker_id,
        normalized_instance_id,
        normalized_worker_type,
    )


def _validate_registration(
    value: Any,
) -> UniversalWorkerRegistration:

    if not isinstance(
        value,
        UniversalWorkerRegistration,
    ):

        raise UniversalWorkerCapacityError(
            (
                "registration must be canonical "
                "UniversalWorkerRegistration."
            ),
            code="invalid_worker_capacity_registration",
            value=value,
        )

    return value


def calculate_universal_worker_available_capacity(
    *,
    capacity_limit: Any,
    active_work_count: Any,
) -> int:

    limit = (
        normalize_universal_worker_capacity_count(
            capacity_limit,
            field_name="capacity_limit",
        )
    )

    active = (
        normalize_universal_worker_capacity_count(
            active_work_count,
            field_name="active_work_count",
        )
    )

    if active > limit:

        raise UniversalWorkerCapacityError(
            (
                "active_work_count cannot exceed "
                "capacity_limit."
            ),
            code="worker_capacity_active_work_exceeds_limit",
            value={
                "capacity_limit":
                    limit,

                "active_work_count":
                    active,
            },
        )

    return (
        limit
        - active
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerCapacitySnapshot:

    worker_id: str

    worker_instance_id: str

    worker_type: str

    capacity_limit: int

    active_work_count: int

    schema_version: str = (
        UNIVERSAL_WORKER_CAPACITY_SNAPSHOT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        (
            worker_id,
            worker_instance_id,
            worker_type,
        ) = _normalize_worker_identity(
            worker_id=self.worker_id,
            worker_instance_id=self.worker_instance_id,
            worker_type=self.worker_type,
        )

        capacity_limit = (
            normalize_universal_worker_capacity_count(
                self.capacity_limit,
                field_name="capacity_limit",
            )
        )

        active_work_count = (
            normalize_universal_worker_capacity_count(
                self.active_work_count,
                field_name="active_work_count",
            )
        )

        calculate_universal_worker_available_capacity(
            capacity_limit=capacity_limit,
            active_work_count=active_work_count,
        )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_CAPACITY_SNAPSHOT_SCHEMA_VERSION
        ):

            raise UniversalWorkerCapacityError(
                (
                    "Invalid Worker Capacity Snapshot "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_capacity_"
                    "snapshot_schema_version"
                ),
                value=self.schema_version,
            )

        object.__setattr__(
            self,
            "worker_id",
            worker_id,
        )

        object.__setattr__(
            self,
            "worker_instance_id",
            worker_instance_id,
        )

        object.__setattr__(
            self,
            "worker_type",
            worker_type,
        )

        object.__setattr__(
            self,
            "capacity_limit",
            capacity_limit,
        )

        object.__setattr__(
            self,
            "active_work_count",
            active_work_count,
        )

    @property
    def worker_identity(
        self,
    ) -> str:

        return (
            self.worker_id
            + UNIVERSAL_WORKER_CAPACITY_IDENTITY_SEPARATOR
            + self.worker_instance_id
        )

    @property
    def available_capacity(
        self,
    ) -> int:

        return (
            self.capacity_limit
            - self.active_work_count
        )

    @property
    def has_available_capacity(
        self,
    ) -> bool:

        return (
            self.available_capacity
            > 0
        )

    @property
    def is_saturated(
        self,
    ) -> bool:

        return (
            self.available_capacity
            == 0
        )


def create_universal_worker_capacity_snapshot(
    *,
    registration: UniversalWorkerRegistration,
    capacity_limit: Any,
    active_work_count: Any,
) -> UniversalWorkerCapacitySnapshot:

    resolved_registration = (
        _validate_registration(
            registration
        )
    )

    return UniversalWorkerCapacitySnapshot(
        worker_id=(
            resolved_registration.worker_id
        ),
        worker_instance_id=(
            resolved_registration.worker_instance_id
        ),
        worker_type=(
            resolved_registration.worker_type
        ),
        capacity_limit=capacity_limit,
        active_work_count=active_work_count,
    )


def explain_universal_worker_capacity_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.14",

            "component":
                "Universal Worker Capacity Management",

            "version":
                UNIVERSAL_WORKER_CAPACITY_VERSION,

            "snapshot_schema_version":
                UNIVERSAL_WORKER_CAPACITY_SNAPSHOT_SCHEMA_VERSION,

            "scope_rule": (
                "4.1.14 owns immutable individual-worker "
                "generic work-slot capacity evidence"
            ),

            "identity_rule": (
                "Worker Capacity preserves canonical "
                "Worker Registration identity "
                "(worker_id, worker_instance_id)"
            ),

            "capacity_limit_rule": (
                "capacity_limit is caller-supplied maximum "
                "simultaneous capacity-consuming work units "
                "for this worker snapshot"
            ),

            "active_work_rule": (
                "active_work_count is caller-supplied "
                "already-composed capacity-consuming work "
                "evidence; 4.1.14 does not determine which "
                "job statuses count as active work"
            ),

            "available_capacity_rule": (
                "available_capacity equals capacity_limit "
                "minus active_work_count and can never "
                "be negative"
            ),

            "zero_capacity_rule": (
                "capacity_limit=0 with active_work_count=0 "
                "is valid and represents a saturated worker "
                "with zero available capacity"
            ),

            "contradiction_rule": (
                "active_work_count greater than "
                "capacity_limit is contradictory evidence "
                "and is rejected"
            ),

            "lease_boundary": (
                "active leases are separate ownership "
                "evidence and do not independently consume "
                "Worker Capacity inside 4.1.14"
            ),

            "assignment_boundary": (
                "capacity evidence does not perform Worker "
                "Assignment; callers may compose capacity "
                "before supplying eligible workers to 4.1.3"
            ),

            "scaling_boundary": (
                "4.1.14 does not scale workers; callers may "
                "aggregate Worker Capacity evidence into the "
                "caller-composed available_capacity consumed "
                "by 4.1.7 Worker Scaling"
            ),

            "runtime_concurrency_boundary": (
                "runtime/workspace max_concurrency settings "
                "are separate configuration/concurrency "
                "authorities and are not read by 4.1.14"
            ),

            "queue_capacity_boundary": (
                "3.1.11 Queue Capacity Limits is separate "
                "queue-depth admission authority"
            ),

            "capability_boundary": (
                "Worker Capability defines what a worker can "
                "perform; Worker Capacity defines how much "
                "capacity-consuming work it can accept"
            ),

            "drain_boundary": (
                "Worker Drain determines new-work acceptance; "
                "Capacity does not inspect or apply drain state"
            ),

            "resource_boundary": (
                "CPU, memory, GPU, throughput and resource "
                "scheduling are outside 4.1.14"
            ),

            "utilization_boundary": (
                "utilization and historical worker-load "
                "analytics remain observability concerns"
            ),

            "persistence_boundary": (
                "4.1.14 does not persist capacity state or "
                "access Runtime State Store"
            ),

            "purity_rule": (
                "Worker Capacity is deterministic over "
                "caller-supplied evidence and performs no "
                "external mutation, wall-clock access or I/O"
            ),

            "prohibitions": (
                "does not mutate Worker Registration",
                "does not inspect Worker Capability",
                "does not inspect Worker Pool membership",
                "does not inspect Worker Health",
                "does not inspect Stale Worker Detection",
                "does not inspect Worker Drain",
                "does not inspect active worker leases",
                "does not infer active work from leases",
                "does not acquire worker leases",
                "does not renew worker leases",
                "does not release worker leases",
                "does not perform Worker Assignment",
                "does not perform Worker Scaling",
                "does not perform Worker Shutdown",
                "does not initiate Worker Recovery",
                "does not read runtime max_concurrency",
                "does not read workspace concurrency policy",
                "does not calculate utilization",
                "does not calculate CPU capacity",
                "does not calculate memory capacity",
                "does not calculate GPU capacity",
                "does not enforce Queue Capacity Limits",
                "does not access Queue Infrastructure",
                "does not access orchestration",
                "does not access Runtime State Store",
                "does not persist capacity state",
                "does not maintain capacity history",
                "does not use wall clock",
                "does not perform filesystem I/O",
                "does not perform network I/O",
                "does not dispatch jobs",
                "does not execute jobs",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_CAPACITY_VERSION",
    "UNIVERSAL_WORKER_CAPACITY_SNAPSHOT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_CAPACITY_COUNT",
    "UNIVERSAL_WORKER_CAPACITY_IDENTITY_SEPARATOR",
    "UniversalWorkerCapacityError",
    "UniversalWorkerCapacitySnapshot",
    "normalize_universal_worker_capacity_count",
    "calculate_universal_worker_available_capacity",
    "create_universal_worker_capacity_snapshot",
    "explain_universal_worker_capacity_v1",
]
'''


ast.parse(
    SOURCE
)

CAPACITY_PATH.write_text(
    SOURCE,
    encoding="utf-8",
)


sys.path.insert(
    0,
    str(ROOT),
)

registration = importlib.import_module(
    "backend.server.runtime.universal_worker.registration"
)

module_name = (
    "backend.server.runtime."
    "universal_worker.capacity"
)

sys.modules.pop(
    module_name,
    None,
)

capacity = importlib.import_module(
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


reg = (
    registration.create_universal_worker_registration(
        worker_id="worker-a",
        worker_type="semantic_worker",
        worker_instance_id="instance-1",
        runtime_version="runtime-v1",
        host_id="host-1",
        registered_at="2026-08-17T01:00:00+00:00",
    )
)


# ============================================================
# CONSTANTS
# ============================================================

check(
    "version",
    capacity.UNIVERSAL_WORKER_CAPACITY_VERSION
    == "universal_worker_capacity_v4.1.14",
)

check(
    "snapshot_schema",
    capacity.UNIVERSAL_WORKER_CAPACITY_SNAPSHOT_SCHEMA_VERSION
    == "universal_worker_capacity_snapshot_schema_v1",
)

check(
    "maximum_count",
    capacity.MAX_UNIVERSAL_WORKER_CAPACITY_COUNT
    == 2_147_483_647,
)

check(
    "identity_separator",
    capacity.UNIVERSAL_WORKER_CAPACITY_IDENTITY_SEPARATOR
    == "::",
)


# ============================================================
# COUNT NORMALIZATION
# ============================================================

for value in (
    0,
    1,
    2,
    100,
    capacity.MAX_UNIVERSAL_WORKER_CAPACITY_COUNT,
):

    for field_name in (
        "capacity_limit",
        "active_work_count",
    ):

        check(
            (
                "valid_count_"
                + field_name
                + "_"
                + str(value)
            ),
            (
                capacity.normalize_universal_worker_capacity_count(
                    value,
                    field_name=field_name,
                )
                == value
            ),
        )


for index, bad in enumerate(
    (
        None,
        True,
        False,
        -1,
        -100,
        0.0,
        1.0,
        "0",
        "1",
        "",
        [],
        {},
        (),
        object(),
    ),
    start=1,
):

    for field_name in (
        "capacity_limit",
        "active_work_count",
    ):

        try:

            capacity.normalize_universal_worker_capacity_count(
                bad,
                field_name=field_name,
            )

        except capacity.UniversalWorkerCapacityError as exc:

            rejected = (
                exc.code
                == "invalid_worker_capacity_count"
            )

        else:

            rejected = False

        check(
            (
                "invalid_count_"
                + field_name
                + "_"
                + str(index)
            ),
            rejected,
            repr(bad),
        )


for field_name in (
    "capacity_limit",
    "active_work_count",
):

    try:

        capacity.normalize_universal_worker_capacity_count(
            capacity.MAX_UNIVERSAL_WORKER_CAPACITY_COUNT
            + 1,
            field_name=field_name,
        )

    except capacity.UniversalWorkerCapacityError as exc:

        rejected = (
            exc.code
            == "worker_capacity_count_too_large"
        )

    else:

        rejected = False

    check(
        field_name
        + "_overflow_rejected",
        rejected,
    )


# ============================================================
# AVAILABLE CAPACITY CALCULATION
# ============================================================

calculation_cases = (
    (
        0,
        0,
        0,
    ),
    (
        1,
        0,
        1,
    ),
    (
        1,
        1,
        0,
    ),
    (
        10,
        3,
        7,
    ),
    (
        100,
        99,
        1,
    ),
    (
        capacity.MAX_UNIVERSAL_WORKER_CAPACITY_COUNT,
        0,
        capacity.MAX_UNIVERSAL_WORKER_CAPACITY_COUNT,
    ),
    (
        capacity.MAX_UNIVERSAL_WORKER_CAPACITY_COUNT,
        capacity.MAX_UNIVERSAL_WORKER_CAPACITY_COUNT,
        0,
    ),
)


for index, (
    limit,
    active,
    expected,
) in enumerate(
    calculation_cases,
    start=1,
):

    actual = (
        capacity.calculate_universal_worker_available_capacity(
            capacity_limit=limit,
            active_work_count=active,
        )
    )

    check(
        "available_capacity_case_"
        + str(index),
        actual
        == expected,
        actual,
    )


for limit, active in (
    (
        0,
        1,
    ),
    (
        1,
        2,
    ),
    (
        10,
        11,
    ),
):

    try:

        capacity.calculate_universal_worker_available_capacity(
            capacity_limit=limit,
            active_work_count=active,
        )

    except capacity.UniversalWorkerCapacityError as exc:

        rejected = (
            exc.code
            == "worker_capacity_active_work_exceeds_limit"
        )

    else:

        rejected = False

    check(
        (
            "contradiction_rejected_"
            + str(limit)
            + "_"
            + str(active)
        ),
        rejected,
    )


# ============================================================
# SNAPSHOT
# ============================================================

available = (
    capacity.create_universal_worker_capacity_snapshot(
        registration=reg,
        capacity_limit=10,
        active_work_count=3,
    )
)


check(
    "snapshot_worker_id",
    available.worker_id
    == reg.worker_id,
)

check(
    "snapshot_instance",
    available.worker_instance_id
    == reg.worker_instance_id,
)

check(
    "snapshot_worker_type",
    available.worker_type
    == reg.worker_type,
)

check(
    "snapshot_identity",
    available.worker_identity
    == "worker-a::instance-1",
)

check(
    "snapshot_limit",
    available.capacity_limit
    == 10,
)

check(
    "snapshot_active",
    available.active_work_count
    == 3,
)

check(
    "snapshot_available",
    available.available_capacity
    == 7,
)

check(
    "snapshot_has_available",
    available.has_available_capacity
    is True,
)

check(
    "snapshot_not_saturated",
    available.is_saturated
    is False,
)


saturated = (
    capacity.create_universal_worker_capacity_snapshot(
        registration=reg,
        capacity_limit=10,
        active_work_count=10,
    )
)


check(
    "saturated_available_zero",
    saturated.available_capacity
    == 0,
)

check(
    "saturated_has_available_false",
    saturated.has_available_capacity
    is False,
)

check(
    "saturated_true",
    saturated.is_saturated
    is True,
)


zero_capacity = (
    capacity.create_universal_worker_capacity_snapshot(
        registration=reg,
        capacity_limit=0,
        active_work_count=0,
    )
)


check(
    "zero_capacity_valid",
    zero_capacity.capacity_limit
    == 0,
)

check(
    "zero_capacity_available_zero",
    zero_capacity.available_capacity
    == 0,
)

check(
    "zero_capacity_saturated",
    zero_capacity.is_saturated
    is True,
)


# ============================================================
# INVALID REGISTRATION
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        "",
        [],
        {},
        (),
        object(),
    ),
    start=1,
):

    try:

        capacity.create_universal_worker_capacity_snapshot(
            registration=bad,
            capacity_limit=1,
            active_work_count=0,
        )

    except capacity.UniversalWorkerCapacityError as exc:

        rejected = (
            exc.code
            == "invalid_worker_capacity_registration"
        )

    else:

        rejected = False

    check(
        "invalid_registration_"
        + str(index),
        rejected,
    )


# ============================================================
# DIRECT SNAPSHOT CONTRADICTION / FORGERY
# ============================================================

try:

    capacity.UniversalWorkerCapacitySnapshot(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        capacity_limit=3,
        active_work_count=4,
    )

except capacity.UniversalWorkerCapacityError as exc:

    rejected = (
        exc.code
        == "worker_capacity_active_work_exceeds_limit"
    )

else:

    rejected = False


check(
    "direct_snapshot_contradiction_rejected",
    rejected,
)


for field_name, bad_value in (
    (
        "worker_id",
        "",
    ),
    (
        "worker_id",
        " ",
    ),
    (
        "worker_instance_id",
        "",
    ),
    (
        "worker_instance_id",
        " ",
    ),
    (
        "worker_type",
        "",
    ),
    (
        "worker_type",
        " ",
    ),
):

    kwargs = {
        "worker_id":
            reg.worker_id,

        "worker_instance_id":
            reg.worker_instance_id,

        "worker_type":
            reg.worker_type,

        "capacity_limit":
            1,

        "active_work_count":
            0,
    }

    kwargs[
        field_name
    ] = bad_value

    try:

        capacity.UniversalWorkerCapacitySnapshot(
            **kwargs
        )

    except capacity.UniversalWorkerCapacityError:

        rejected = True

    else:

        rejected = False

    check(
        (
            "identity_forgery_"
            + field_name
            + "_"
            + repr(bad_value)
        ),
        rejected,
    )


# ============================================================
# SCHEMA TAMPER
# ============================================================

try:

    capacity.UniversalWorkerCapacitySnapshot(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        capacity_limit=1,
        active_work_count=0,
        schema_version="tampered",
    )

except capacity.UniversalWorkerCapacityError as exc:

    rejected = (
        exc.code
        == "invalid_worker_capacity_snapshot_schema_version"
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

for field in fields(
    available
):

    try:

        setattr(
            available,
            field.name,
            None,
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        "immutable_"
        + field.name,
        immutable,
    )


# ============================================================
# EXACT FIELD CONTRACT
# ============================================================

snapshot_fields = tuple(
    field.name
    for field in fields(
        capacity.UniversalWorkerCapacitySnapshot
    )
)


check(
    "snapshot_fields_exact",
    snapshot_fields
    == (
        "worker_id",
        "worker_instance_id",
        "worker_type",
        "capacity_limit",
        "active_work_count",
        "schema_version",
    ),
    snapshot_fields,
)


for forbidden_field in (
    "available_capacity",
    "has_available_capacity",
    "is_saturated",
    "active_lease_count",
    "lease_id",
    "lease_owner",
    "job_id",
    "job_type",
    "capabilities",
    "pool_id",
    "health",
    "health_state",
    "stale",
    "drain_state",
    "max_concurrency",
    "utilization",
    "cpu",
    "memory",
    "gpu",
    "queue_id",
):

    check(
        "forbidden_field_"
        + forbidden_field,
        forbidden_field
        not in snapshot_fields,
    )


# ============================================================
# DETERMINISM
# ============================================================

available_again = (
    capacity.create_universal_worker_capacity_snapshot(
        registration=reg,
        capacity_limit=10,
        active_work_count=3,
    )
)


check(
    "deterministic_snapshot",
    available_again
    == available,
)


# ============================================================
# EXPLANATION CONTRACT
# ============================================================

explanation = (
    capacity.explain_universal_worker_capacity_v1()
)


check(
    "phase",
    explanation.get(
        "phase"
    )
    == "4.1.14",
)

check(
    "component",
    explanation.get(
        "component"
    )
    == "Universal Worker Capacity Management",
)

check(
    "individual_worker_scope",
    "individual-worker"
    in explanation.get(
        "scope_rule",
        "",
    ),
)

check(
    "capacity_limit_caller_supplied",
    "caller-supplied"
    in explanation.get(
        "capacity_limit_rule",
        "",
    ),
)

check(
    "active_work_caller_supplied",
    "caller-supplied"
    in explanation.get(
        "active_work_rule",
        "",
    ),
)

check(
    "job_statuses_external",
    "does not determine which"
    in explanation.get(
        "active_work_rule",
        "",
    ),
)

check(
    "formula_exact",
    "minus active_work_count"
    in explanation.get(
        "available_capacity_rule",
        "",
    ),
)

check(
    "zero_capacity_valid_rule",
    "capacity_limit=0"
    in explanation.get(
        "zero_capacity_rule",
        "",
    ),
)

check(
    "contradiction_rule",
    "contradictory evidence"
    in explanation.get(
        "contradiction_rule",
        "",
    ),
)

check(
    "leases_separate",
    "separate ownership"
    in explanation.get(
        "lease_boundary",
        "",
    ),
)

check(
    "assignment_external",
    "does not perform Worker Assignment"
    in explanation.get(
        "assignment_boundary",
        "",
    ),
)

check(
    "scaling_external",
    "does not scale workers"
    in explanation.get(
        "scaling_boundary",
        "",
    ),
)

check(
    "scaling_composition",
    "caller-composed available_capacity"
    in explanation.get(
        "scaling_boundary",
        "",
    ),
)

check(
    "runtime_concurrency_external",
    "not read by 4.1.14"
    in explanation.get(
        "runtime_concurrency_boundary",
        "",
    ),
)

check(
    "queue_capacity_external",
    "separate"
    in explanation.get(
        "queue_capacity_boundary",
        "",
    ),
)

check(
    "capability_external",
    "Worker Capability"
    in explanation.get(
        "capability_boundary",
        "",
    ),
)

check(
    "drain_external",
    "does not inspect or apply"
    in explanation.get(
        "drain_boundary",
        "",
    ),
)

check(
    "resource_external",
    "outside 4.1.14"
    in explanation.get(
        "resource_boundary",
        "",
    ),
)

check(
    "utilization_external",
    "observability"
    in explanation.get(
        "utilization_boundary",
        "",
    ),
)

check(
    "persistence_external",
    "does not persist"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)

check(
    "purity",
    "no external mutation"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


# ============================================================
# PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not mutate Worker Registration",
    "does not inspect Worker Capability",
    "does not inspect Worker Pool membership",
    "does not inspect Worker Health",
    "does not inspect Stale Worker Detection",
    "does not inspect Worker Drain",
    "does not inspect active worker leases",
    "does not infer active work from leases",
    "does not acquire worker leases",
    "does not renew worker leases",
    "does not release worker leases",
    "does not perform Worker Assignment",
    "does not perform Worker Scaling",
    "does not perform Worker Shutdown",
    "does not initiate Worker Recovery",
    "does not read runtime max_concurrency",
    "does not read workspace concurrency policy",
    "does not calculate utilization",
    "does not calculate CPU capacity",
    "does not calculate memory capacity",
    "does not calculate GPU capacity",
    "does not enforce Queue Capacity Limits",
    "does not access Queue Infrastructure",
    "does not access orchestration",
    "does not access Runtime State Store",
    "does not persist capacity state",
    "does not maintain capacity history",
    "does not use wall clock",
    "does not perform filesystem I/O",
    "does not perform network I/O",
    "does not dispatch jobs",
    "does not execute jobs",
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
# IMPORT / API BOUNDARY
# ============================================================

source = CAPACITY_PATH.read_text(
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


expected_all = (
    "UNIVERSAL_WORKER_CAPACITY_VERSION",
    "UNIVERSAL_WORKER_CAPACITY_SNAPSHOT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_CAPACITY_COUNT",
    "UNIVERSAL_WORKER_CAPACITY_IDENTITY_SEPARATOR",
    "UniversalWorkerCapacityError",
    "UniversalWorkerCapacitySnapshot",
    "normalize_universal_worker_capacity_count",
    "calculate_universal_worker_available_capacity",
    "create_universal_worker_capacity_snapshot",
    "explain_universal_worker_capacity_v1",
)


check(
    "api_surface_exact",
    tuple(
        capacity.__all__
    )
    == expected_all,
    capacity.__all__,
)


# ============================================================
# FORBIDDEN CALLS
# ============================================================

forbidden_calls = {
    "open",
    "read_text",
    "write_text",
    "write_json",
    "mkdir",
    "unlink",
    "remove",

    "assign_universal_worker",
    "discover_universal_workers",

    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",

    "evaluate_universal_worker_health",
    "evaluate_universal_stale_worker",
    "evaluate_universal_worker_drain",
    "evaluate_universal_worker_recovery",
    "evaluate_universal_worker_scaling",
    "evaluate_universal_worker_shutdown",

    "match_universal_worker_capabilities",

    "add_universal_worker_pool_member",
    "remove_universal_worker_pool_member",

    "workspace_concurrency_decision",

    "enqueue_job",
    "dequeue_job",
    "route_job",

    "get_runtime_state_store_registry",

    "persist",
    "save",
    "dispatch_job",
    "execute_job",
}


found_forbidden_calls = []


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

        call_name = node.func.id

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        call_name = node.func.attr

    else:

        continue

    if call_name in forbidden_calls:

        found_forbidden_calls.append(
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
    not found_forbidden_calls,
    found_forbidden_calls,
)


# ============================================================
# PROTECTED MATRIX
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


capacity_ast = ast_sha(
    CAPACITY_PATH
)


check(
    "worker_capacity_ast_generated",
    len(
        capacity_ast
    )
    == 64,
    capacity_ast,
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
        "PHASE 4.1.14 — UNIVERSAL WORKER "
        "CAPACITY MANAGEMENT INITIAL IMPLEMENTATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER CAPACITY AST SHA256: "
        + capacity_ast
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
            "INITIAL WORKER CAPACITY RESULT: "
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
        "4.1.10 WORKER HEARTBEAT MODIFIED: NO",
        "4.1.11 STALE WORKER DETECTION MODIFIED: NO",
        "4.1.12 WORKER DRAIN MODIFIED: NO",
        "4.1.13 WORKER CAPABILITY MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "RUNTIME LIFECYCLE MANAGER MODIFIED: NO",
        "RUNTIME SHUTDOWN PROCESS MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "WORKER REGISTRATION MUTATED: NO",
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER POOL INSPECTED: NO",
        "WORKER HEALTH INSPECTED: NO",
        "STALE WORKER DETECTION INSPECTED: NO",
        "WORKER DRAIN INSPECTED: NO",
        "ACTIVE LEASES INSPECTED: NO",
        "ACTIVE WORK INFERRED FROM LEASES: NO",
        "WORKER ASSIGNMENT PERFORMED: NO",
        "WORKER SCALING PERFORMED: NO",
        "WORKER SHUTDOWN PERFORMED: NO",
        "WORKER RECOVERY INITIATED: NO",
        "RUNTIME MAX_CONCURRENCY READ: NO",
        "WORKSPACE CONCURRENCY POLICY READ: NO",
        "UTILIZATION CALCULATED: NO",
        "CPU/MEMORY/GPU RESOURCE CAPACITY CALCULATED: NO",
        "QUEUE CAPACITY ENFORCED: NO",
        "QUEUE INFRASTRUCTURE ACCESSED: NO",
        "ORCHESTRATION ACCESSED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "CAPACITY STATE PERSISTED: NO",
        "CAPACITY HISTORY MAINTAINED: NO",
        "WALL CLOCK USED: NO",
        "FILESYSTEM I/O: NO",
        "NETWORK I/O: NO",
        "JOB DISPATCH/EXECUTION: NO",
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
    "\n".join(
        lines
    ),
    encoding="utf-8",
)

print(
    "\n".join(
        lines
    )
)


if passed != total:

    raise SystemExit(
        "Phase 4.1.14 Worker Capacity initial implementation failed."
    )
