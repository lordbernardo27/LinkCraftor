from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

STALE_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "stale.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_11_stale_worker_initial_implementation.txt"
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

    tree = ast.parse(source)

    canonical = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest().upper()


for name, (path, expected) in PROTECTED.items():

    actual = ast_sha(path)

    if actual != expected:
        raise SystemExit(
            (
                "Protected authority mismatch before "
                "4.1.11 implementation: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


SOURCE = r'''from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.universal_worker.heartbeat import (
    UniversalWorkerHeartbeat,
    normalize_universal_worker_heartbeat_timestamp,
)


UNIVERSAL_STALE_WORKER_DETECTION_VERSION = (
    "universal_stale_worker_detection_v4.1.11"
)

UNIVERSAL_STALE_WORKER_RESULT_SCHEMA_VERSION = (
    "universal_stale_worker_result_schema_v1"
)

MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS = (
    2_147_483_647
)


class UniversalStaleWorkerError(
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


class UniversalWorkerStalenessState(
    str,
    Enum,
):

    ACTIVE = "ACTIVE"

    STALE = "STALE"


def normalize_universal_stale_worker_threshold_seconds(
    value: Any,
) -> int:

    if (
        type(value) is not int
        or
        value <= 0
    ):

        raise UniversalStaleWorkerError(
            (
                "stale_threshold_seconds must be "
                "an integer greater than zero."
            ),
            code="invalid_stale_worker_threshold",
            value=value,
        )

    if (
        value
        > MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS
    ):

        raise UniversalStaleWorkerError(
            (
                "stale_threshold_seconds exceeds "
                "the supported maximum."
            ),
            code="stale_worker_threshold_too_large",
            value=value,
        )

    return value


def normalize_universal_stale_worker_evaluated_at(
    value: Any,
) -> str:

    try:

        return (
            normalize_universal_worker_heartbeat_timestamp(
                value
            )
        )

    except Exception as exc:

        code = getattr(
            exc,
            "code",
            "invalid_stale_worker_evaluated_at",
        )

        raise UniversalStaleWorkerError(
            (
                "evaluated_at must be a valid "
                "timezone-aware UTC timestamp."
            ),
            code=(
                "invalid_stale_worker_evaluated_at_"
                + str(code)
            ),
            value=value,
        ) from exc


def _parse_timestamp(
    value: str,
) -> datetime:

    return datetime.fromisoformat(
        value
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalStaleWorkerResult:

    worker_id: str

    worker_instance_id: str

    worker_type: str

    heartbeat_at: str

    heartbeat_sequence: int

    evaluated_at: str

    stale_threshold_seconds: int

    age_seconds: float

    state: UniversalWorkerStalenessState

    schema_version: str = (
        UNIVERSAL_STALE_WORKER_RESULT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        if not isinstance(
            self.worker_id,
            str,
        ) or not self.worker_id:

            raise UniversalStaleWorkerError(
                "Invalid worker_id in stale result.",
                code="invalid_stale_worker_result_worker_id",
                value=self.worker_id,
            )

        if not isinstance(
            self.worker_instance_id,
            str,
        ) or not self.worker_instance_id:

            raise UniversalStaleWorkerError(
                (
                    "Invalid worker_instance_id "
                    "in stale result."
                ),
                code=(
                    "invalid_stale_worker_result_"
                    "worker_instance_id"
                ),
                value=self.worker_instance_id,
            )

        if not isinstance(
            self.worker_type,
            str,
        ) or not self.worker_type:

            raise UniversalStaleWorkerError(
                "Invalid worker_type in stale result.",
                code="invalid_stale_worker_result_worker_type",
                value=self.worker_type,
            )

        heartbeat_at = (
            normalize_universal_worker_heartbeat_timestamp(
                self.heartbeat_at
            )
        )

        evaluated_at = (
            normalize_universal_worker_heartbeat_timestamp(
                self.evaluated_at
            )
        )

        threshold = (
            normalize_universal_stale_worker_threshold_seconds(
                self.stale_threshold_seconds
            )
        )

        if (
            type(self.heartbeat_sequence) is not int
            or
            self.heartbeat_sequence < 1
        ):

            raise UniversalStaleWorkerError(
                (
                    "Invalid heartbeat_sequence "
                    "in stale result."
                ),
                code=(
                    "invalid_stale_worker_result_"
                    "heartbeat_sequence"
                ),
                value=self.heartbeat_sequence,
            )

        if not isinstance(
            self.age_seconds,
            float,
        ):

            raise UniversalStaleWorkerError(
                "age_seconds must be float.",
                code="invalid_stale_worker_result_age",
                value=self.age_seconds,
            )

        if self.age_seconds < 0.0:

            raise UniversalStaleWorkerError(
                "age_seconds must not be negative.",
                code="negative_stale_worker_result_age",
                value=self.age_seconds,
            )

        if not isinstance(
            self.state,
            UniversalWorkerStalenessState,
        ):

            raise UniversalStaleWorkerError(
                "Invalid staleness state.",
                code="invalid_stale_worker_state",
                value=self.state,
            )

        expected_age = (
            _parse_timestamp(
                evaluated_at
            )
            -
            _parse_timestamp(
                heartbeat_at
            )
        ).total_seconds()

        if expected_age < 0:

            raise UniversalStaleWorkerError(
                (
                    "heartbeat_at must not be later "
                    "than evaluated_at."
                ),
                code="future_worker_heartbeat",
                value={
                    "heartbeat_at":
                        heartbeat_at,
                    "evaluated_at":
                        evaluated_at,
                },
            )

        if self.age_seconds != float(
            expected_age
        ):

            raise UniversalStaleWorkerError(
                "Inconsistent stale-worker age.",
                code="inconsistent_stale_worker_age",
                value=self.age_seconds,
            )

        expected_state = (
            UniversalWorkerStalenessState.STALE
            if expected_age >= threshold
            else
            UniversalWorkerStalenessState.ACTIVE
        )

        if self.state is not expected_state:

            raise UniversalStaleWorkerError(
                "Inconsistent stale-worker state.",
                code="inconsistent_stale_worker_state",
                value=self.state,
            )

        if (
            self.schema_version
            != UNIVERSAL_STALE_WORKER_RESULT_SCHEMA_VERSION
        ):

            raise UniversalStaleWorkerError(
                (
                    "Invalid Stale Worker Result "
                    "schema_version."
                ),
                code=(
                    "invalid_stale_worker_result_"
                    "schema_version"
                ),
                value=self.schema_version,
            )

        object.__setattr__(
            self,
            "heartbeat_at",
            heartbeat_at,
        )

        object.__setattr__(
            self,
            "evaluated_at",
            evaluated_at,
        )

        object.__setattr__(
            self,
            "stale_threshold_seconds",
            threshold,
        )

    @property
    def worker_identity(
        self,
    ) -> str:

        return (
            self.worker_id
            + "::"
            + self.worker_instance_id
        )

    @property
    def is_stale(
        self,
    ) -> bool:

        return (
            self.state
            is UniversalWorkerStalenessState.STALE
        )

    @property
    def is_active(
        self,
    ) -> bool:

        return (
            self.state
            is UniversalWorkerStalenessState.ACTIVE
        )


def evaluate_universal_stale_worker(
    *,
    heartbeat: UniversalWorkerHeartbeat,
    evaluated_at: str,
    stale_threshold_seconds: int,
) -> UniversalStaleWorkerResult:

    if not isinstance(
        heartbeat,
        UniversalWorkerHeartbeat,
    ):

        raise UniversalStaleWorkerError(
            (
                "heartbeat must be canonical "
                "UniversalWorkerHeartbeat evidence."
            ),
            code="invalid_stale_worker_heartbeat",
            value=heartbeat,
        )

    normalized_evaluated_at = (
        normalize_universal_stale_worker_evaluated_at(
            evaluated_at
        )
    )

    threshold = (
        normalize_universal_stale_worker_threshold_seconds(
            stale_threshold_seconds
        )
    )

    heartbeat_time = (
        _parse_timestamp(
            heartbeat.heartbeat_at
        )
    )

    evaluation_time = (
        _parse_timestamp(
            normalized_evaluated_at
        )
    )

    if heartbeat_time > evaluation_time:

        raise UniversalStaleWorkerError(
            (
                "heartbeat_at must not be later "
                "than evaluated_at."
            ),
            code="future_worker_heartbeat",
            value={
                "heartbeat_at":
                    heartbeat.heartbeat_at,
                "evaluated_at":
                    normalized_evaluated_at,
            },
        )

    age_seconds = (
        evaluation_time
        - heartbeat_time
    ).total_seconds()

    state = (
        UniversalWorkerStalenessState.STALE
        if age_seconds >= threshold
        else
        UniversalWorkerStalenessState.ACTIVE
    )

    return UniversalStaleWorkerResult(
        worker_id=heartbeat.worker_id,
        worker_instance_id=heartbeat.worker_instance_id,
        worker_type=heartbeat.worker_type,
        heartbeat_at=heartbeat.heartbeat_at,
        heartbeat_sequence=heartbeat.sequence,
        evaluated_at=normalized_evaluated_at,
        stale_threshold_seconds=threshold,
        age_seconds=float(
            age_seconds
        ),
        state=state,
    )


def explain_universal_stale_worker_detection_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.11",

            "component":
                "Universal Stale Worker Detection",

            "version":
                UNIVERSAL_STALE_WORKER_DETECTION_VERSION,

            "result_schema_version":
                UNIVERSAL_STALE_WORKER_RESULT_SCHEMA_VERSION,

            "input_rule": (
                "4.1.11 consumes canonical 4.1.10 "
                "UniversalWorkerHeartbeat evidence plus "
                "caller-supplied evaluated_at and "
                "stale_threshold_seconds"
            ),

            "time_rule": (
                "evaluated_at is caller-supplied, "
                "timezone-aware UTC; 4.1.11 does not "
                "read the wall clock"
            ),

            "threshold_rule": (
                "stale_threshold_seconds is a positive "
                "caller-supplied integer"
            ),

            "active_rule": (
                "heartbeat age strictly less than the "
                "threshold is ACTIVE"
            ),

            "stale_rule": (
                "heartbeat age greater than or equal "
                "to the threshold is STALE"
            ),

            "equality_rule": (
                "age equal to stale_threshold_seconds "
                "is STALE"
            ),

            "future_heartbeat_rule": (
                "heartbeat_at later than evaluated_at "
                "is contradictory evidence and is rejected"
            ),

            "missing_heartbeat_rule": (
                "missing heartbeat evidence is invalid "
                "input rather than ACTIVE, STALE or UNKNOWN"
            ),

            "age_rule": (
                "4.1.11 owns deterministic heartbeat "
                "age calculation"
            ),

            "health_boundary": (
                "STALE is not UNHEALTHY and 4.1.11 does "
                "not invoke or mutate 4.1.5 Worker Health"
            ),

            "lease_boundary": (
                "STALE is independent from ACTIVE or "
                "EXPIRED Worker Leasing state"
            ),

            "recovery_boundary": (
                "STALE is evidence only; 4.1.11 does not "
                "authorize or initiate Worker Recovery"
            ),

            "queue_recovery_boundary": (
                "Queue Recovery may later consume "
                "stale-worker evidence but 4.1.11 does "
                "not requeue, fail or mutate jobs"
            ),

            "registration_pool_boundary": (
                "STALE does not deregister workers or "
                "remove Worker Pool membership"
            ),

            "shutdown_drain_boundary": (
                "STALE does not automatically shut down "
                "or drain workers"
            ),

            "persistence_boundary": (
                "4.1.11 does not persist stale state or "
                "access Runtime State Store"
            ),

            "purity_rule": (
                "Stale Worker Detection is deterministic "
                "over caller-supplied evidence and "
                "performs no external mutation or I/O"
            ),

            "prohibitions": (
                "does not read the wall clock",
                "does not generate evaluation timestamps",
                "does not define a global stale threshold",
                "does not define heartbeat interval",
                "does not accept missing heartbeat as STALE",
                "does not accept missing heartbeat as ACTIVE",
                "does not create UNKNOWN staleness",
                "does not determine Worker Health",
                "does not mark workers UNHEALTHY",
                "does not initiate Worker Recovery",
                "does not mark jobs FAILED",
                "does not requeue jobs",
                "does not cancel jobs",
                "does not acquire leases",
                "does not renew leases",
                "does not release leases",
                "does not equate stale worker with expired lease",
                "does not modify Worker Registration",
                "does not deregister workers",
                "does not modify Worker Pool membership",
                "does not discover workers",
                "does not assign workers",
                "does not scale workers",
                "does not shut down workers",
                "does not drain workers",
                "does not inspect worker capabilities",
                "does not calculate worker capacity",
                "does not access Runtime State Store",
                "does not access orchestration",
                "does not persist stale state",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_STALE_WORKER_DETECTION_VERSION",
    "UNIVERSAL_STALE_WORKER_RESULT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS",
    "UniversalStaleWorkerError",
    "UniversalWorkerStalenessState",
    "UniversalStaleWorkerResult",
    "normalize_universal_stale_worker_threshold_seconds",
    "normalize_universal_stale_worker_evaluated_at",
    "evaluate_universal_stale_worker",
    "explain_universal_stale_worker_detection_v1",
]
'''


ast.parse(
    SOURCE
)

STALE_PATH.write_text(
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

heartbeat = importlib.import_module(
    "backend.server.runtime.universal_worker.heartbeat"
)

module_name = (
    "backend.server.runtime."
    "universal_worker.stale"
)

sys.modules.pop(
    module_name,
    None,
)

stale = importlib.import_module(
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

hb = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg,
        heartbeat_at="2026-08-17T00:00:00Z",
        sequence=10,
    )
)


# ============================================================
# CONSTANTS
# ============================================================

check(
    "version",
    stale.UNIVERSAL_STALE_WORKER_DETECTION_VERSION
    == "universal_stale_worker_detection_v4.1.11",
)

check(
    "result_schema",
    stale.UNIVERSAL_STALE_WORKER_RESULT_SCHEMA_VERSION
    == "universal_stale_worker_result_schema_v1",
)

check(
    "threshold_max",
    stale.MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS
    == 2_147_483_647,
)

check(
    "states_exact",
    tuple(
        x.value
        for x in stale.UniversalWorkerStalenessState
    )
    == (
        "ACTIVE",
        "STALE",
    ),
)


# ============================================================
# THRESHOLD VALIDATION
# ============================================================

for value in (
    1,
    30,
    60,
    300,
    stale.MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS,
):

    check(
        "valid_threshold_"
        + str(value),
        stale.normalize_universal_stale_worker_threshold_seconds(
            value
        )
        == value,
    )


for bad in (
    None,
    True,
    False,
    0,
    -1,
    1.0,
    "1",
    "",
    [],
    {},
    (),
):

    try:

        stale.normalize_universal_stale_worker_threshold_seconds(
            bad
        )

    except stale.UniversalStaleWorkerError as exc:

        rejected = (
            exc.code
            == "invalid_stale_worker_threshold"
        )

    else:

        rejected = False

    check(
        "invalid_threshold_"
        + repr(bad),
        rejected,
    )


try:

    stale.normalize_universal_stale_worker_threshold_seconds(
        stale.MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS
        + 1
    )

except stale.UniversalStaleWorkerError as exc:

    rejected = (
        exc.code
        == "stale_worker_threshold_too_large"
    )

else:

    rejected = False


check(
    "threshold_overflow_rejected",
    rejected,
)


# ============================================================
# ACTIVE / STALE BOUNDARY
# ============================================================

active = (
    stale.evaluate_universal_stale_worker(
        heartbeat=hb,
        evaluated_at="2026-08-17T00:00:59Z",
        stale_threshold_seconds=60,
    )
)

check(
    "age_59",
    active.age_seconds
    == 59.0,
)

check(
    "age_59_active",
    active.state
    is stale.UniversalWorkerStalenessState.ACTIVE,
)

check(
    "active_property",
    active.is_active
    is True,
)

check(
    "active_not_stale",
    active.is_stale
    is False,
)


equal = (
    stale.evaluate_universal_stale_worker(
        heartbeat=hb,
        evaluated_at="2026-08-17T00:01:00Z",
        stale_threshold_seconds=60,
    )
)

check(
    "age_60",
    equal.age_seconds
    == 60.0,
)

check(
    "age_equal_threshold_stale",
    equal.state
    is stale.UniversalWorkerStalenessState.STALE,
)

check(
    "equal_stale_property",
    equal.is_stale
    is True,
)


older = (
    stale.evaluate_universal_stale_worker(
        heartbeat=hb,
        evaluated_at="2026-08-17T00:01:01Z",
        stale_threshold_seconds=60,
    )
)

check(
    "age_61",
    older.age_seconds
    == 61.0,
)

check(
    "age_above_threshold_stale",
    older.state
    is stale.UniversalWorkerStalenessState.STALE,
)


# ============================================================
# ZERO AGE
# ============================================================

zero_age = (
    stale.evaluate_universal_stale_worker(
        heartbeat=hb,
        evaluated_at="2026-08-17T00:00:00Z",
        stale_threshold_seconds=60,
    )
)

check(
    "zero_age_allowed",
    zero_age.age_seconds
    == 0.0,
)

check(
    "zero_age_active",
    zero_age.state
    is stale.UniversalWorkerStalenessState.ACTIVE,
)


# ============================================================
# FUTURE HEARTBEAT CONTRADICTION
# ============================================================

try:

    stale.evaluate_universal_stale_worker(
        heartbeat=hb,
        evaluated_at="2026-08-16T23:59:59Z",
        stale_threshold_seconds=60,
    )

except stale.UniversalStaleWorkerError as exc:

    rejected = (
        exc.code
        == "future_worker_heartbeat"
    )

else:

    rejected = False


check(
    "future_heartbeat_rejected",
    rejected,
)


# ============================================================
# MISSING / INVALID HEARTBEAT
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

        stale.evaluate_universal_stale_worker(
            heartbeat=bad,
            evaluated_at="2026-08-17T00:01:00Z",
            stale_threshold_seconds=60,
        )

    except stale.UniversalStaleWorkerError as exc:

        rejected = (
            exc.code
            == "invalid_stale_worker_heartbeat"
        )

    else:

        rejected = False

    check(
        "invalid_heartbeat_"
        + repr(bad),
        rejected,
    )


# ============================================================
# RESULT ECHO
# ============================================================

check(
    "worker_id_echo",
    equal.worker_id
    == hb.worker_id,
)

check(
    "worker_instance_echo",
    equal.worker_instance_id
    == hb.worker_instance_id,
)

check(
    "worker_type_echo",
    equal.worker_type
    == hb.worker_type,
)

check(
    "heartbeat_timestamp_echo",
    equal.heartbeat_at
    == hb.heartbeat_at,
)

check(
    "heartbeat_sequence_echo",
    equal.heartbeat_sequence
    == hb.sequence,
)

check(
    "evaluation_echo",
    equal.evaluated_at
    == "2026-08-17T00:01:00+00:00",
)

check(
    "threshold_echo",
    equal.stale_threshold_seconds
    == 60,
)

check(
    "worker_identity",
    equal.worker_identity
    == "worker-a::instance-1",
)


# ============================================================
# RESULT FORGERY
# ============================================================

try:

    stale.UniversalStaleWorkerResult(
        worker_id=hb.worker_id,
        worker_instance_id=hb.worker_instance_id,
        worker_type=hb.worker_type,
        heartbeat_at=hb.heartbeat_at,
        heartbeat_sequence=hb.sequence,
        evaluated_at="2026-08-17T00:00:59Z",
        stale_threshold_seconds=60,
        age_seconds=59.0,
        state=stale.UniversalWorkerStalenessState.STALE,
    )

except stale.UniversalStaleWorkerError as exc:

    rejected = (
        exc.code
        == "inconsistent_stale_worker_state"
    )

else:

    rejected = False


check(
    "forged_state_rejected",
    rejected,
)


try:

    stale.UniversalStaleWorkerResult(
        worker_id=hb.worker_id,
        worker_instance_id=hb.worker_instance_id,
        worker_type=hb.worker_type,
        heartbeat_at=hb.heartbeat_at,
        heartbeat_sequence=hb.sequence,
        evaluated_at="2026-08-17T00:01:00Z",
        stale_threshold_seconds=60,
        age_seconds=59.0,
        state=stale.UniversalWorkerStalenessState.STALE,
    )

except stale.UniversalStaleWorkerError as exc:

    rejected = (
        exc.code
        == "inconsistent_stale_worker_age"
    )

else:

    rejected = False


check(
    "forged_age_rejected",
    rejected,
)


# ============================================================
# SCHEMA
# ============================================================

try:

    stale.UniversalStaleWorkerResult(
        worker_id=hb.worker_id,
        worker_instance_id=hb.worker_instance_id,
        worker_type=hb.worker_type,
        heartbeat_at=hb.heartbeat_at,
        heartbeat_sequence=hb.sequence,
        evaluated_at="2026-08-17T00:01:00Z",
        stale_threshold_seconds=60,
        age_seconds=60.0,
        state=stale.UniversalWorkerStalenessState.STALE,
        schema_version="tampered",
    )

except stale.UniversalStaleWorkerError as exc:

    rejected = (
        exc.code
        == "invalid_stale_worker_result_schema_version"
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
    "heartbeat_sequence",
    "evaluated_at",
    "stale_threshold_seconds",
    "age_seconds",
    "state",
    "schema_version",
):

    try:

        setattr(
            equal,
            field_name,
            None,
        )

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
# DETERMINISM
# ============================================================

equal_again = (
    stale.evaluate_universal_stale_worker(
        heartbeat=hb,
        evaluated_at="2026-08-17T00:01:00Z",
        stale_threshold_seconds=60,
    )
)

check(
    "deterministic_result",
    equal
    == equal_again,
)


# ============================================================
# EXPLANATION
# ============================================================

explanation = (
    stale.explain_universal_stale_worker_detection_v1()
)


check(
    "explanation_phase",
    explanation.get(
        "phase"
    )
    == "4.1.11",
)

check(
    "explanation_component",
    explanation.get(
        "component"
    )
    == "Universal Stale Worker Detection",
)

check(
    "canonical_heartbeat_input",
    "4.1.10"
    in explanation.get(
        "input_rule",
        "",
    ),
)

check(
    "caller_evaluation_time",
    "caller-supplied"
    in explanation.get(
        "time_rule",
        "",
    ),
)

check(
    "no_wall_clock",
    "does not read the wall clock"
    in explanation.get(
        "time_rule",
        "",
    ),
)

check(
    "positive_threshold",
    "positive"
    in explanation.get(
        "threshold_rule",
        "",
    ),
)

check(
    "active_less_than",
    "strictly less"
    in explanation.get(
        "active_rule",
        "",
    ),
)

check(
    "stale_greater_equal",
    "greater than or equal"
    in explanation.get(
        "stale_rule",
        "",
    ),
)

check(
    "equality_stale",
    "is STALE"
    in explanation.get(
        "equality_rule",
        "",
    ),
)

check(
    "future_rejected",
    "rejected"
    in explanation.get(
        "future_heartbeat_rule",
        "",
    ),
)

check(
    "missing_invalid",
    "invalid input"
    in explanation.get(
        "missing_heartbeat_rule",
        "",
    ),
)

check(
    "health_separate",
    "not UNHEALTHY"
    in explanation.get(
        "health_boundary",
        "",
    ),
)

check(
    "lease_separate",
    "independent"
    in explanation.get(
        "lease_boundary",
        "",
    ),
)

check(
    "recovery_separate",
    "does not authorize or initiate"
    in explanation.get(
        "recovery_boundary",
        "",
    ),
)

check(
    "persistence_separate",
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
    "does not read the wall clock",
    "does not generate evaluation timestamps",
    "does not define a global stale threshold",
    "does not define heartbeat interval",
    "does not accept missing heartbeat as STALE",
    "does not accept missing heartbeat as ACTIVE",
    "does not create UNKNOWN staleness",
    "does not determine Worker Health",
    "does not mark workers UNHEALTHY",
    "does not initiate Worker Recovery",
    "does not mark jobs FAILED",
    "does not requeue jobs",
    "does not cancel jobs",
    "does not acquire leases",
    "does not renew leases",
    "does not release leases",
    "does not equate stale worker with expired lease",
    "does not modify Worker Registration",
    "does not deregister workers",
    "does not modify Worker Pool membership",
    "does not discover workers",
    "does not assign workers",
    "does not scale workers",
    "does not shut down workers",
    "does not drain workers",
    "does not inspect worker capabilities",
    "does not calculate worker capacity",
    "does not access Runtime State Store",
    "does not access orchestration",
    "does not persist stale state",
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

source = STALE_PATH.read_text(
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
        "backend.server.runtime.universal_worker.heartbeat",
    ],
    backend_imports,
)


# ============================================================
# API
# ============================================================

expected_all = (
    "UNIVERSAL_STALE_WORKER_DETECTION_VERSION",
    "UNIVERSAL_STALE_WORKER_RESULT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS",
    "UniversalStaleWorkerError",
    "UniversalWorkerStalenessState",
    "UniversalStaleWorkerResult",
    "normalize_universal_stale_worker_threshold_seconds",
    "normalize_universal_stale_worker_evaluated_at",
    "evaluate_universal_stale_worker",
    "explain_universal_stale_worker_detection_v1",
)


check(
    "api_surface_exact",
    tuple(
        stale.__all__
    )
    == expected_all,
    stale.__all__,
)


# ============================================================
# SIDE EFFECT SCAN
# ============================================================

forbidden_call_names = {
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

    "worker_heartbeat",

    "evaluate_universal_worker_health",
    "evaluate_universal_worker_recovery",
    "evaluate_universal_worker_scaling",
    "evaluate_universal_worker_shutdown",

    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",

    "enqueue_job",
    "dequeue_job",
    "requeue_job",
    "cancel_job",
    "mark_job_failed",

    "assign_universal_worker",
    "discover_universal_workers",

    "add_universal_worker_pool_member",
    "remove_universal_worker_pool_member",

    "record_worker_status",
    "get_latest_worker_statuses",

    "get_runtime_state_store_registry",

    "dispatch_job",
    "execute_job",

    "persist",
    "save",
}


found_forbidden = []


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

        found_forbidden.append(
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
    not found_forbidden,
    found_forbidden,
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


stale_ast = ast_sha(
    STALE_PATH
)


check(
    "stale_ast_generated",
    len(
        stale_ast
    )
    == 64,
    stale_ast,
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
        "PHASE 4.1.11 — UNIVERSAL STALE WORKER "
        "DETECTION INITIAL IMPLEMENTATION"
    ),
    "=" * 112,
    "",
    (
        "STALE WORKER AST SHA256: "
        + stale_ast
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
            "INITIAL STALE WORKER RESULT: "
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
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "WALL CLOCK READ: NO",
        "EVALUATION TIME GENERATED INTERNALLY: NO",
        "GLOBAL STALE THRESHOLD DEFINED: NO",
        "MISSING HEARTBEAT CLASSIFIED STALE: NO",
        "UNKNOWN STALENESS CREATED: NO",
        "WORKER HEALTH MODIFIED: NO",
        "WORKER RECOVERY INITIATED: NO",
        "LEASE MUTATED: NO",
        "JOB FAILED/REQUEUED/CANCELLED: NO",
        "WORKER REGISTRATION MUTATED: NO",
        "WORKER DEREGISTERED: NO",
        "WORKER POOL MEMBERSHIP MODIFIED: NO",
        "WORKER DISCOVERED/ASSIGNED: NO",
        "WORKER SCALING PERFORMED: NO",
        "WORKER SHUTDOWN PERFORMED: NO",
        "WORKER DRAIN PERFORMED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "STALE STATE PERSISTED: NO",
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
        "Phase 4.1.11 Stale Worker initial implementation failed."
    )
