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

DRAIN_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "drain.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_12_worker_drain_initial_implementation.txt"
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
                "4.1.12 implementation: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


SOURCE = r'''from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.universal_worker.registration import (
    UniversalWorkerRegistration,
    normalize_universal_worker_id,
    normalize_universal_worker_instance_id,
    normalize_universal_worker_type,
)


UNIVERSAL_WORKER_DRAIN_VERSION = (
    "universal_worker_drain_v4.1.12"
)

UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION = (
    "universal_worker_drain_evidence_schema_v1"
)

UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION = (
    "universal_worker_drain_result_schema_v1"
)

MAX_UNIVERSAL_WORKER_DRAIN_COUNT = (
    2_147_483_647
)

UNIVERSAL_WORKER_DRAIN_IDENTITY_SEPARATOR = (
    "::"
)


class UniversalWorkerDrainError(
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


class UniversalWorkerDrainState(
    str,
    Enum,
):

    NOT_REQUESTED = "NOT_REQUESTED"

    DRAINING = "DRAINING"

    DRAINED = "DRAINED"


def normalize_universal_worker_drain_requested(
    value: Any,
) -> bool:

    if type(value) is not bool:

        raise UniversalWorkerDrainError(
            "drain_requested must be bool.",
            code="invalid_worker_drain_requested",
            value=value,
        )

    return value


def normalize_universal_worker_drain_count(
    value: Any,
    *,
    field_name: str,
) -> int:

    if (
        type(value) is not int
        or
        value < 0
    ):

        raise UniversalWorkerDrainError(
            (
                field_name
                + " must be an integer "
                "greater than or equal to zero."
            ),
            code="invalid_worker_drain_count",
            value={
                "field_name":
                    field_name,

                "value":
                    value,
            },
        )

    if (
        value
        > MAX_UNIVERSAL_WORKER_DRAIN_COUNT
    ):

        raise UniversalWorkerDrainError(
            (
                field_name
                + " exceeds the supported maximum."
            ),
            code="worker_drain_count_too_large",
            value={
                "field_name":
                    field_name,

                "value":
                    value,
            },
        )

    return value


def _validate_registration(
    value: Any,
) -> UniversalWorkerRegistration:

    if not isinstance(
        value,
        UniversalWorkerRegistration,
    ):

        raise UniversalWorkerDrainError(
            (
                "registration must be canonical "
                "UniversalWorkerRegistration."
            ),
            code="invalid_worker_drain_registration",
            value=value,
        )

    return value


def decide_universal_worker_drain_state(
    *,
    drain_requested: bool,
    active_work_count: int,
    active_lease_count: int,
) -> UniversalWorkerDrainState:

    requested = (
        normalize_universal_worker_drain_requested(
            drain_requested
        )
    )

    work_count = (
        normalize_universal_worker_drain_count(
            active_work_count,
            field_name="active_work_count",
        )
    )

    lease_count = (
        normalize_universal_worker_drain_count(
            active_lease_count,
            field_name="active_lease_count",
        )
    )

    if not requested:

        return (
            UniversalWorkerDrainState.NOT_REQUESTED
        )

    if (
        work_count > 0
        or
        lease_count > 0
    ):

        return (
            UniversalWorkerDrainState.DRAINING
        )

    return (
        UniversalWorkerDrainState.DRAINED
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerDrainEvidence:

    worker_id: str

    worker_instance_id: str

    worker_type: str

    drain_requested: bool

    active_work_count: int

    active_lease_count: int

    schema_version: str = (
        UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        try:

            worker_id = (
                normalize_universal_worker_id(
                    self.worker_id
                )
            )

            worker_instance_id = (
                normalize_universal_worker_instance_id(
                    self.worker_instance_id
                )
            )

            worker_type = (
                normalize_universal_worker_type(
                    self.worker_type
                )
            )

        except Exception as exc:

            raise UniversalWorkerDrainError(
                (
                    "Invalid canonical worker identity "
                    "in drain evidence."
                ),
                code="invalid_worker_drain_identity",
                value={
                    "worker_id":
                        self.worker_id,

                    "worker_instance_id":
                        self.worker_instance_id,

                    "worker_type":
                        self.worker_type,
                },
            ) from exc

        requested = (
            normalize_universal_worker_drain_requested(
                self.drain_requested
            )
        )

        work_count = (
            normalize_universal_worker_drain_count(
                self.active_work_count,
                field_name="active_work_count",
            )
        )

        lease_count = (
            normalize_universal_worker_drain_count(
                self.active_lease_count,
                field_name="active_lease_count",
            )
        )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION
        ):

            raise UniversalWorkerDrainError(
                (
                    "Invalid Worker Drain Evidence "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_drain_evidence_"
                    "schema_version"
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
            "drain_requested",
            requested,
        )

        object.__setattr__(
            self,
            "active_work_count",
            work_count,
        )

        object.__setattr__(
            self,
            "active_lease_count",
            lease_count,
        )

    @property
    def worker_identity(
        self,
    ) -> str:

        return (
            self.worker_id
            + UNIVERSAL_WORKER_DRAIN_IDENTITY_SEPARATOR
            + self.worker_instance_id
        )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerDrainResult:

    worker_id: str

    worker_instance_id: str

    worker_type: str

    drain_requested: bool

    active_work_count: int

    active_lease_count: int

    state: UniversalWorkerDrainState

    schema_version: str = (
        UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        try:

            worker_id = (
                normalize_universal_worker_id(
                    self.worker_id
                )
            )

            worker_instance_id = (
                normalize_universal_worker_instance_id(
                    self.worker_instance_id
                )
            )

            worker_type = (
                normalize_universal_worker_type(
                    self.worker_type
                )
            )

        except Exception as exc:

            raise UniversalWorkerDrainError(
                (
                    "Invalid canonical worker identity "
                    "in drain result."
                ),
                code="invalid_worker_drain_result_identity",
                value={
                    "worker_id":
                        self.worker_id,

                    "worker_instance_id":
                        self.worker_instance_id,

                    "worker_type":
                        self.worker_type,
                },
            ) from exc

        requested = (
            normalize_universal_worker_drain_requested(
                self.drain_requested
            )
        )

        work_count = (
            normalize_universal_worker_drain_count(
                self.active_work_count,
                field_name="active_work_count",
            )
        )

        lease_count = (
            normalize_universal_worker_drain_count(
                self.active_lease_count,
                field_name="active_lease_count",
            )
        )

        if not isinstance(
            self.state,
            UniversalWorkerDrainState,
        ):

            raise UniversalWorkerDrainError(
                "Invalid Worker Drain state.",
                code="invalid_worker_drain_state",
                value=self.state,
            )

        expected_state = (
            decide_universal_worker_drain_state(
                drain_requested=requested,
                active_work_count=work_count,
                active_lease_count=lease_count,
            )
        )

        if self.state is not expected_state:

            raise UniversalWorkerDrainError(
                "Inconsistent Worker Drain state.",
                code="inconsistent_worker_drain_state",
                value={
                    "expected":
                        expected_state.value,

                    "actual":
                        self.state.value,
                },
            )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION
        ):

            raise UniversalWorkerDrainError(
                (
                    "Invalid Worker Drain Result "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_drain_result_"
                    "schema_version"
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
            "drain_requested",
            requested,
        )

        object.__setattr__(
            self,
            "active_work_count",
            work_count,
        )

        object.__setattr__(
            self,
            "active_lease_count",
            lease_count,
        )

    @property
    def worker_identity(
        self,
    ) -> str:

        return (
            self.worker_id
            + UNIVERSAL_WORKER_DRAIN_IDENTITY_SEPARATOR
            + self.worker_instance_id
        )

    @property
    def drain_complete(
        self,
    ) -> bool:

        return (
            self.state
            is UniversalWorkerDrainState.DRAINED
        )

    @property
    def accepts_new_work(
        self,
    ) -> bool:

        return (
            self.state
            is UniversalWorkerDrainState.NOT_REQUESTED
        )

    @property
    def is_draining(
        self,
    ) -> bool:

        return (
            self.state
            is UniversalWorkerDrainState.DRAINING
        )

    @property
    def is_drained(
        self,
    ) -> bool:

        return (
            self.state
            is UniversalWorkerDrainState.DRAINED
        )


def create_universal_worker_drain_evidence(
    *,
    registration: UniversalWorkerRegistration,
    drain_requested: bool,
    active_work_count: int,
    active_lease_count: int,
) -> UniversalWorkerDrainEvidence:

    resolved_registration = (
        _validate_registration(
            registration
        )
    )

    return UniversalWorkerDrainEvidence(
        worker_id=(
            resolved_registration.worker_id
        ),
        worker_instance_id=(
            resolved_registration.worker_instance_id
        ),
        worker_type=(
            resolved_registration.worker_type
        ),
        drain_requested=drain_requested,
        active_work_count=active_work_count,
        active_lease_count=active_lease_count,
    )


def evaluate_universal_worker_drain(
    *,
    evidence: UniversalWorkerDrainEvidence,
) -> UniversalWorkerDrainResult:

    if not isinstance(
        evidence,
        UniversalWorkerDrainEvidence,
    ):

        raise UniversalWorkerDrainError(
            (
                "evidence must be canonical "
                "UniversalWorkerDrainEvidence."
            ),
            code="invalid_worker_drain_evidence",
            value=evidence,
        )

    state = (
        decide_universal_worker_drain_state(
            drain_requested=evidence.drain_requested,
            active_work_count=evidence.active_work_count,
            active_lease_count=evidence.active_lease_count,
        )
    )

    return UniversalWorkerDrainResult(
        worker_id=evidence.worker_id,
        worker_instance_id=evidence.worker_instance_id,
        worker_type=evidence.worker_type,
        drain_requested=evidence.drain_requested,
        active_work_count=evidence.active_work_count,
        active_lease_count=evidence.active_lease_count,
        state=state,
    )


def explain_universal_worker_drain_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.12",

            "component":
                "Universal Worker Drain",

            "version":
                UNIVERSAL_WORKER_DRAIN_VERSION,

            "evidence_schema_version":
                UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION,

            "result_schema_version":
                UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION,

            "scope_rule": (
                "4.1.12 is individual-worker drain "
                "authority and is separate from whole-"
                "runtime RuntimeLifecyclePhase.DRAINING"
            ),

            "identity_rule": (
                "drain evidence uses canonical Worker "
                "Registration identity "
                "(worker_id, worker_instance_id)"
            ),

            "input_rule": (
                "caller supplies drain_requested, "
                "active_work_count and active_lease_count"
            ),

            "not_requested_rule": (
                "drain_requested=false yields NOT_REQUESTED "
                "regardless of active work or lease counts"
            ),

            "draining_rule": (
                "drain_requested=true with any active work "
                "or active leases yields DRAINING"
            ),

            "drained_rule": (
                "drain_requested=true with zero active work "
                "and zero active leases yields DRAINED"
            ),

            "new_work_rule": (
                "NOT_REQUESTED does not prohibit new work; "
                "DRAINING and DRAINED produce "
                "accepts_new_work=false evidence"
            ),

            "assignment_boundary": (
                "4.1.12 does not modify or invoke Worker "
                "Assignment; callers may use drain evidence "
                "when constructing the eligible worker set"
            ),

            "leasing_boundary": (
                "4.1.12 does not acquire, renew or release "
                "leases; callers may use drain evidence to "
                "prevent new ownership acquisition"
            ),

            "existing_work_rule": (
                "draining preserves existing work and lease "
                "ownership until external completion"
            ),

            "shutdown_boundary": (
                "4.1.8 Worker Shutdown may consume "
                "drain_complete derived from a DRAINED result"
            ),

            "scaling_boundary": (
                "Worker Scaling remains independent; a "
                "drain result does not perform scale-down"
            ),

            "pool_boundary": (
                "draining or drained state does not remove "
                "Worker Pool membership"
            ),

            "health_stale_recovery_boundary": (
                "drain state is independent from Worker "
                "Health, Stale Worker Detection and "
                "Worker Recovery"
            ),

            "persistence_boundary": (
                "4.1.12 does not persist drain state or "
                "access Runtime State Store"
            ),

            "purity_rule": (
                "Worker Drain is deterministic over "
                "caller-supplied evidence and performs "
                "no external mutation or I/O"
            ),

            "prohibitions": (
                "does not use whole-runtime DRAINING as worker drain state",
                "does not mutate Runtime Lifecycle Manager",
                "does not assign workers",
                "does not modify Assignment eligibility directly",
                "does not acquire worker leases",
                "does not renew worker leases",
                "does not release worker leases",
                "does not cancel running work",
                "does not requeue jobs",
                "does not fail jobs",
                "does not terminate workers",
                "does not perform Worker Shutdown",
                "does not perform Worker Scaling",
                "does not modify Worker Registration",
                "does not deregister workers",
                "does not modify Worker Pool membership",
                "does not determine Worker Health",
                "does not detect stale workers",
                "does not initiate Worker Recovery",
                "does not inspect worker capabilities",
                "does not calculate worker capacity",
                "does not access Queue Infrastructure",
                "does not access orchestration",
                "does not access Runtime State Store",
                "does not persist drain state",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_DRAIN_VERSION",
    "UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_DRAIN_COUNT",
    "UNIVERSAL_WORKER_DRAIN_IDENTITY_SEPARATOR",
    "UniversalWorkerDrainError",
    "UniversalWorkerDrainState",
    "UniversalWorkerDrainEvidence",
    "UniversalWorkerDrainResult",
    "normalize_universal_worker_drain_requested",
    "normalize_universal_worker_drain_count",
    "decide_universal_worker_drain_state",
    "create_universal_worker_drain_evidence",
    "evaluate_universal_worker_drain",
    "explain_universal_worker_drain_v1",
]
'''


ast.parse(
    SOURCE
)

DRAIN_PATH.write_text(
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
    "universal_worker.drain"
)

sys.modules.pop(
    module_name,
    None,
)

drain = importlib.import_module(
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


def make_registration():

    return registration.create_universal_worker_registration(
        worker_id="worker-a",
        worker_type="semantic_worker",
        worker_instance_id="instance-1",
        runtime_version="runtime-v1",
        host_id="host-1",
        registered_at="2026-08-17T00:00:00+00:00",
    )


reg = make_registration()


# ============================================================
# CONSTANTS / STATES
# ============================================================

check(
    "version",
    drain.UNIVERSAL_WORKER_DRAIN_VERSION
    == "universal_worker_drain_v4.1.12",
)

check(
    "evidence_schema",
    drain.UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION
    == "universal_worker_drain_evidence_schema_v1",
)

check(
    "result_schema",
    drain.UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION
    == "universal_worker_drain_result_schema_v1",
)

check(
    "count_max",
    drain.MAX_UNIVERSAL_WORKER_DRAIN_COUNT
    == 2_147_483_647,
)

check(
    "states_exact",
    tuple(
        state.value
        for state in drain.UniversalWorkerDrainState
    )
    == (
        "NOT_REQUESTED",
        "DRAINING",
        "DRAINED",
    ),
)


# ============================================================
# REQUEST VALIDATION
# ============================================================

check(
    "requested_true",
    drain.normalize_universal_worker_drain_requested(
        True
    )
    is True,
)

check(
    "requested_false",
    drain.normalize_universal_worker_drain_requested(
        False
    )
    is False,
)


for bad in (
    None,
    0,
    1,
    "",
    "true",
    [],
    {},
    (),
):

    try:

        drain.normalize_universal_worker_drain_requested(
            bad
        )

    except drain.UniversalWorkerDrainError as exc:

        rejected = (
            exc.code
            == "invalid_worker_drain_requested"
        )

    else:

        rejected = False

    check(
        "invalid_requested_"
        + repr(
            bad
        ),
        rejected,
    )


# ============================================================
# COUNT VALIDATION
# ============================================================

for value in (
    0,
    1,
    10,
    drain.MAX_UNIVERSAL_WORKER_DRAIN_COUNT,
):

    check(
        "valid_count_"
        + str(
            value
        ),
        drain.normalize_universal_worker_drain_count(
            value,
            field_name="active_work_count",
        )
        == value,
    )


for bad in (
    None,
    True,
    False,
    -1,
    1.0,
    "",
    "1",
    [],
    {},
    (),
):

    try:

        drain.normalize_universal_worker_drain_count(
            bad,
            field_name="active_work_count",
        )

    except drain.UniversalWorkerDrainError as exc:

        rejected = (
            exc.code
            == "invalid_worker_drain_count"
        )

    else:

        rejected = False

    check(
        "invalid_count_"
        + repr(
            bad
        ),
        rejected,
    )


try:

    drain.normalize_universal_worker_drain_count(
        drain.MAX_UNIVERSAL_WORKER_DRAIN_COUNT
        + 1,
        field_name="active_work_count",
    )

except drain.UniversalWorkerDrainError as exc:

    rejected = (
        exc.code
        == "worker_drain_count_too_large"
    )

else:

    rejected = False


check(
    "count_overflow_rejected",
    rejected,
)


# ============================================================
# STATE MATRIX
# ============================================================

matrix = (
    (
        False,
        0,
        0,
        "NOT_REQUESTED",
    ),
    (
        False,
        1,
        0,
        "NOT_REQUESTED",
    ),
    (
        False,
        0,
        1,
        "NOT_REQUESTED",
    ),
    (
        False,
        5,
        7,
        "NOT_REQUESTED",
    ),
    (
        True,
        1,
        0,
        "DRAINING",
    ),
    (
        True,
        0,
        1,
        "DRAINING",
    ),
    (
        True,
        1,
        1,
        "DRAINING",
    ),
    (
        True,
        100,
        200,
        "DRAINING",
    ),
    (
        True,
        0,
        0,
        "DRAINED",
    ),
)


for index, (
    requested,
    work,
    leases,
    expected,
) in enumerate(
    matrix,
    start=1,
):

    actual = (
        drain.decide_universal_worker_drain_state(
            drain_requested=requested,
            active_work_count=work,
            active_lease_count=leases,
        )
    )

    check(
        "state_matrix_"
        + str(
            index
        ),
        actual.value
        == expected,
        actual.value,
    )


# ============================================================
# EVIDENCE CREATION
# ============================================================

evidence = (
    drain.create_universal_worker_drain_evidence(
        registration=reg,
        drain_requested=True,
        active_work_count=2,
        active_lease_count=1,
    )
)


check(
    "evidence_worker_id",
    evidence.worker_id
    == reg.worker_id,
)

check(
    "evidence_instance",
    evidence.worker_instance_id
    == reg.worker_instance_id,
)

check(
    "evidence_type",
    evidence.worker_type
    == reg.worker_type,
)

check(
    "evidence_identity",
    evidence.worker_identity
    == "worker-a::instance-1",
)

check(
    "evidence_requested",
    evidence.drain_requested
    is True,
)

check(
    "evidence_work_count",
    evidence.active_work_count
    == 2,
)

check(
    "evidence_lease_count",
    evidence.active_lease_count
    == 1,
)


# ============================================================
# INVALID REGISTRATION
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

        drain.create_universal_worker_drain_evidence(
            registration=bad,
            drain_requested=True,
            active_work_count=0,
            active_lease_count=0,
        )

    except drain.UniversalWorkerDrainError as exc:

        rejected = (
            exc.code
            == "invalid_worker_drain_registration"
        )

    else:

        rejected = False

    check(
        "invalid_registration_"
        + repr(
            bad
        ),
        rejected,
    )


# ============================================================
# EVALUATION
# ============================================================

result = (
    drain.evaluate_universal_worker_drain(
        evidence=evidence
    )
)


check(
    "result_state_draining",
    result.state
    is drain.UniversalWorkerDrainState.DRAINING,
)

check(
    "result_is_draining",
    result.is_draining
    is True,
)

check(
    "result_not_drained",
    result.is_drained
    is False,
)

check(
    "result_drain_incomplete",
    result.drain_complete
    is False,
)

check(
    "result_rejects_new_work",
    result.accepts_new_work
    is False,
)


not_requested_evidence = (
    drain.create_universal_worker_drain_evidence(
        registration=reg,
        drain_requested=False,
        active_work_count=3,
        active_lease_count=2,
    )
)

not_requested = (
    drain.evaluate_universal_worker_drain(
        evidence=not_requested_evidence
    )
)


check(
    "not_requested_state",
    not_requested.state
    is drain.UniversalWorkerDrainState.NOT_REQUESTED,
)

check(
    "not_requested_accepts_new_work",
    not_requested.accepts_new_work
    is True,
)

check(
    "not_requested_not_complete",
    not_requested.drain_complete
    is False,
)


drained_evidence = (
    drain.create_universal_worker_drain_evidence(
        registration=reg,
        drain_requested=True,
        active_work_count=0,
        active_lease_count=0,
    )
)

drained = (
    drain.evaluate_universal_worker_drain(
        evidence=drained_evidence
    )
)


check(
    "drained_state",
    drained.state
    is drain.UniversalWorkerDrainState.DRAINED,
)

check(
    "drained_complete",
    drained.drain_complete
    is True,
)

check(
    "drained_is_drained",
    drained.is_drained
    is True,
)

check(
    "drained_rejects_new_work",
    drained.accepts_new_work
    is False,
)


# ============================================================
# INVALID EVIDENCE
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

        drain.evaluate_universal_worker_drain(
            evidence=bad
        )

    except drain.UniversalWorkerDrainError as exc:

        rejected = (
            exc.code
            == "invalid_worker_drain_evidence"
        )

    else:

        rejected = False

    check(
        "invalid_evidence_"
        + repr(
            bad
        ),
        rejected,
    )


# ============================================================
# RESULT FORGERY
# ============================================================

try:

    drain.UniversalWorkerDrainResult(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        drain_requested=True,
        active_work_count=1,
        active_lease_count=0,
        state=drain.UniversalWorkerDrainState.DRAINED,
    )

except drain.UniversalWorkerDrainError as exc:

    rejected = (
        exc.code
        == "inconsistent_worker_drain_state"
    )

else:

    rejected = False


check(
    "forged_drained_state_rejected",
    rejected,
)


try:

    drain.UniversalWorkerDrainResult(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        drain_requested=False,
        active_work_count=0,
        active_lease_count=0,
        state=drain.UniversalWorkerDrainState.DRAINED,
    )

except drain.UniversalWorkerDrainError as exc:

    rejected = (
        exc.code
        == "inconsistent_worker_drain_state"
    )

else:

    rejected = False


check(
    "forged_not_requested_state_rejected",
    rejected,
)


# ============================================================
# SCHEMA TAMPER
# ============================================================

try:

    drain.UniversalWorkerDrainEvidence(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        drain_requested=True,
        active_work_count=0,
        active_lease_count=0,
        schema_version="tampered",
    )

except drain.UniversalWorkerDrainError as exc:

    rejected = (
        exc.code
        == "invalid_worker_drain_evidence_schema_version"
    )

else:

    rejected = False


check(
    "evidence_schema_tamper_rejected",
    rejected,
)


try:

    drain.UniversalWorkerDrainResult(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        drain_requested=True,
        active_work_count=0,
        active_lease_count=0,
        state=drain.UniversalWorkerDrainState.DRAINED,
        schema_version="tampered",
    )

except drain.UniversalWorkerDrainError as exc:

    rejected = (
        exc.code
        == "invalid_worker_drain_result_schema_version"
    )

else:

    rejected = False


check(
    "result_schema_tamper_rejected",
    rejected,
)


# ============================================================
# IMMUTABILITY
# ============================================================

for obj in (
    evidence,
    result,
):

    for field_name in (
        field.name
        for field in fields(
            obj
        )
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
            (
                "immutable_"
                + type(
                    obj
                ).__name__
                + "_"
                + field_name
            ),
            immutable,
        )


# ============================================================
# EXACT FIELD CONTRACT
# ============================================================

evidence_fields = tuple(
    field.name
    for field in fields(
        drain.UniversalWorkerDrainEvidence
    )
)

result_fields = tuple(
    field.name
    for field in fields(
        drain.UniversalWorkerDrainResult
    )
)


check(
    "evidence_fields_exact",
    evidence_fields
    == (
        "worker_id",
        "worker_instance_id",
        "worker_type",
        "drain_requested",
        "active_work_count",
        "active_lease_count",
        "schema_version",
    ),
    evidence_fields,
)

check(
    "result_fields_exact",
    result_fields
    == (
        "worker_id",
        "worker_instance_id",
        "worker_type",
        "drain_requested",
        "active_work_count",
        "active_lease_count",
        "state",
        "schema_version",
    ),
    result_fields,
)


# ============================================================
# DETERMINISM
# ============================================================

result_again = (
    drain.evaluate_universal_worker_drain(
        evidence=evidence
    )
)


check(
    "deterministic_result",
    result_again
    == result,
)


# ============================================================
# EXPLANATION
# ============================================================

explanation = (
    drain.explain_universal_worker_drain_v1()
)


check(
    "phase",
    explanation.get(
        "phase"
    )
    == "4.1.12",
)

check(
    "component",
    explanation.get(
        "component"
    )
    == "Universal Worker Drain",
)

check(
    "scope_separate_from_runtime_drain",
    "separate from whole-runtime"
    in explanation.get(
        "scope_rule",
        "",
    ),
)

check(
    "canonical_identity",
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
    "caller_supplied_counts",
    "caller supplies"
    in explanation.get(
        "input_rule",
        "",
    ),
)

check(
    "not_requested_rule",
    "NOT_REQUESTED"
    in explanation.get(
        "not_requested_rule",
        "",
    ),
)

check(
    "draining_rule",
    "DRAINING"
    in explanation.get(
        "draining_rule",
        "",
    ),
)

check(
    "drained_rule",
    "DRAINED"
    in explanation.get(
        "drained_rule",
        "",
    ),
)

check(
    "new_work_rule",
    "accepts_new_work=false"
    in explanation.get(
        "new_work_rule",
        "",
    ),
)

check(
    "assignment_boundary",
    "does not modify or invoke"
    in explanation.get(
        "assignment_boundary",
        "",
    ),
)

check(
    "leasing_boundary",
    "does not acquire, renew or release"
    in explanation.get(
        "leasing_boundary",
        "",
    ),
)

check(
    "existing_work_preserved",
    "preserves existing work"
    in explanation.get(
        "existing_work_rule",
        "",
    ),
)

check(
    "shutdown_composition",
    "4.1.8 Worker Shutdown"
    in explanation.get(
        "shutdown_boundary",
        "",
    ),
)

check(
    "pool_boundary",
    "does not remove"
    in explanation.get(
        "pool_boundary",
        "",
    ),
)

check(
    "health_stale_recovery_boundary",
    "independent"
    in explanation.get(
        "health_stale_recovery_boundary",
        "",
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


# ============================================================
# PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not use whole-runtime DRAINING as worker drain state",
    "does not mutate Runtime Lifecycle Manager",
    "does not assign workers",
    "does not modify Assignment eligibility directly",
    "does not acquire worker leases",
    "does not renew worker leases",
    "does not release worker leases",
    "does not cancel running work",
    "does not requeue jobs",
    "does not fail jobs",
    "does not terminate workers",
    "does not perform Worker Shutdown",
    "does not perform Worker Scaling",
    "does not modify Worker Registration",
    "does not deregister workers",
    "does not modify Worker Pool membership",
    "does not determine Worker Health",
    "does not detect stale workers",
    "does not initiate Worker Recovery",
    "does not inspect worker capabilities",
    "does not calculate worker capacity",
    "does not access Queue Infrastructure",
    "does not access orchestration",
    "does not access Runtime State Store",
    "does not persist drain state",
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
        + str(
            index
        ),
        item in prohibitions,
        item,
    )


# ============================================================
# IMPORT / API BOUNDARY
# ============================================================

source = DRAIN_PATH.read_text(
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


check(
    "backend_imports_exact",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.registration",
    ],
    backend_imports,
)


expected_all = (
    "UNIVERSAL_WORKER_DRAIN_VERSION",
    "UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_DRAIN_COUNT",
    "UNIVERSAL_WORKER_DRAIN_IDENTITY_SEPARATOR",
    "UniversalWorkerDrainError",
    "UniversalWorkerDrainState",
    "UniversalWorkerDrainEvidence",
    "UniversalWorkerDrainResult",
    "normalize_universal_worker_drain_requested",
    "normalize_universal_worker_drain_count",
    "decide_universal_worker_drain_state",
    "create_universal_worker_drain_evidence",
    "evaluate_universal_worker_drain",
    "explain_universal_worker_drain_v1",
)


check(
    "api_surface_exact",
    tuple(
        drain.__all__
    )
    == expected_all,
    drain.__all__,
)


# ============================================================
# SIDE-EFFECT BOUNDARY
# ============================================================

forbidden_call_names = {
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
    "evaluate_universal_worker_recovery",
    "evaluate_universal_worker_scaling",
    "evaluate_universal_worker_shutdown",

    "add_universal_worker_pool_member",
    "remove_universal_worker_pool_member",

    "enqueue_job",
    "dequeue_job",
    "requeue_job",
    "cancel_job",
    "mark_job_failed",

    "shutdown",
    "terminate",
    "kill",

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

    if call_name in forbidden_call_names:

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


drain_ast = ast_sha(
    DRAIN_PATH
)


check(
    "worker_drain_ast_generated",
    len(
        drain_ast
    )
    == 64,
    drain_ast,
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
        "PHASE 4.1.12 — UNIVERSAL WORKER "
        "DRAIN INITIAL IMPLEMENTATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER DRAIN AST SHA256: "
        + drain_ast
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
            "INITIAL WORKER DRAIN RESULT: "
            + (
                "PASS"
                if passed == total
                else "FAIL"
            )
        ),
        (
            "CHECKS PASSED: "
            + str(
                passed
            )
            + "/"
            + str(
                total
            )
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
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "RUNTIME LIFECYCLE MANAGER MODIFIED: NO",
        "RUNTIME SHUTDOWN PROCESS MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "WHOLE-RUNTIME DRAIN INVOKED: NO",
        "WORKER ASSIGNMENT INVOKED/MODIFIED: NO",
        "WORKER LEASE ACQUIRED/RENEWED/RELEASED: NO",
        "RUNNING WORK CANCELLED: NO",
        "JOB REQUEUED/FAILED: NO",
        "WORKER TERMINATED: NO",
        "WORKER SHUTDOWN PERFORMED: NO",
        "WORKER SCALING PERFORMED: NO",
        "WORKER REGISTRATION MUTATED: NO",
        "WORKER DEREGISTERED: NO",
        "WORKER POOL MEMBERSHIP MODIFIED: NO",
        "WORKER HEALTH MODIFIED: NO",
        "STALE WORKER DETECTION INVOKED: NO",
        "WORKER RECOVERY INITIATED: NO",
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER CAPACITY CALCULATED: NO",
        "QUEUE INFRASTRUCTURE ACCESSED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "DRAIN STATE PERSISTED: NO",
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
        "Phase 4.1.12 Worker Drain initial implementation failed."
    )
