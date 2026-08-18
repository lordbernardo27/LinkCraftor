from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

POOL_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "pool.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_9_worker_pool_initial_implementation.txt"
)


# ============================================================
# PROTECTED AUTHORITIES
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
                "4.1.9 implementation: "
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
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from backend.server.runtime.universal_worker.registration import (
    UniversalWorkerRegistration,
    normalize_universal_worker_id,
    normalize_universal_worker_instance_id,
    normalize_universal_worker_type,
)


UNIVERSAL_WORKER_POOL_VERSION = (
    "universal_worker_pool_v4.1.9"
)

UNIVERSAL_WORKER_POOL_MEMBER_SCHEMA_VERSION = (
    "universal_worker_pool_member_schema_v1"
)

UNIVERSAL_WORKER_POOL_SNAPSHOT_SCHEMA_VERSION = (
    "universal_worker_pool_snapshot_schema_v1"
)

MAX_UNIVERSAL_WORKER_POOL_ID_LENGTH = 200

UNIVERSAL_WORKER_POOL_IDENTITY_SEPARATOR = "::"


class UniversalWorkerPoolError(
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

        self.code = str(code)
        self.value = value


def normalize_universal_worker_pool_id(
    value: Any,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalWorkerPoolError(
            "pool_id must be str.",
            code="invalid_worker_pool_id_type",
            value=value,
        )

    normalized = value.strip()

    if not normalized:

        raise UniversalWorkerPoolError(
            "pool_id must not be empty.",
            code="empty_worker_pool_id",
            value=value,
        )

    if len(normalized) > MAX_UNIVERSAL_WORKER_POOL_ID_LENGTH:

        raise UniversalWorkerPoolError(
            "pool_id exceeds supported maximum length.",
            code="worker_pool_id_too_long",
            value=value,
        )

    if UNIVERSAL_WORKER_POOL_IDENTITY_SEPARATOR in normalized:

        raise UniversalWorkerPoolError(
            (
                "pool_id must not contain the reserved "
                "worker identity separator."
            ),
            code="reserved_worker_pool_id_separator",
            value=value,
        )

    return normalized


@dataclass(
    frozen=True,
    slots=True,
    order=True,
)
class UniversalWorkerPoolMember:

    worker_id: str
    worker_instance_id: str
    worker_type: str

    schema_version: str = (
        UNIVERSAL_WORKER_POOL_MEMBER_SCHEMA_VERSION
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

        if (
            self.schema_version
            != UNIVERSAL_WORKER_POOL_MEMBER_SCHEMA_VERSION
        ):

            raise UniversalWorkerPoolError(
                "Invalid Worker Pool Member schema_version.",
                code=(
                    "invalid_worker_pool_member_"
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
            + UNIVERSAL_WORKER_POOL_IDENTITY_SEPARATOR
            + self.worker_instance_id
        )


def create_universal_worker_pool_member(
    registration: UniversalWorkerRegistration,
) -> UniversalWorkerPoolMember:

    if not isinstance(
        registration,
        UniversalWorkerRegistration,
    ):

        raise UniversalWorkerPoolError(
            (
                "registration must be "
                "UniversalWorkerRegistration."
            ),
            code="invalid_worker_pool_registration",
            value=registration,
        )

    return UniversalWorkerPoolMember(
        worker_id=registration.worker_id,
        worker_instance_id=registration.worker_instance_id,
        worker_type=registration.worker_type,
    )


def _normalize_members(
    members: Iterable[UniversalWorkerPoolMember],
    *,
    worker_type: str,
) -> tuple[UniversalWorkerPoolMember, ...]:

    try:
        supplied_members = tuple(members)

    except TypeError as exc:

        raise UniversalWorkerPoolError(
            "members must be iterable.",
            code="invalid_worker_pool_members",
            value=members,
        ) from exc

    normalized = []

    identities = set()

    for member in supplied_members:

        if not isinstance(
            member,
            UniversalWorkerPoolMember,
        ):

            raise UniversalWorkerPoolError(
                (
                    "every pool member must be "
                    "UniversalWorkerPoolMember."
                ),
                code="invalid_worker_pool_member",
                value=member,
            )

        if member.worker_type != worker_type:

            raise UniversalWorkerPoolError(
                (
                    "worker member type does not match "
                    "pool worker_type."
                ),
                code="worker_pool_type_mismatch",
                value={
                    "pool_worker_type":
                        worker_type,

                    "member_worker_type":
                        member.worker_type,

                    "worker_identity":
                        member.worker_identity,
                },
            )

        if member.worker_identity in identities:

            raise UniversalWorkerPoolError(
                "Duplicate worker pool membership.",
                code="duplicate_worker_pool_member",
                value=member.worker_identity,
            )

        identities.add(
            member.worker_identity
        )

        normalized.append(
            member
        )

    normalized.sort(
        key=lambda item: (
            item.worker_id,
            item.worker_instance_id,
        )
    )

    return tuple(normalized)


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerPoolSnapshot:

    pool_id: str
    worker_type: str

    members: tuple[
        UniversalWorkerPoolMember,
        ...,
    ] = ()

    schema_version: str = (
        UNIVERSAL_WORKER_POOL_SNAPSHOT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        pool_id = (
            normalize_universal_worker_pool_id(
                self.pool_id
            )
        )

        worker_type = (
            normalize_universal_worker_type(
                self.worker_type
            )
        )

        members = (
            _normalize_members(
                self.members,
                worker_type=worker_type,
            )
        )

        object.__setattr__(
            self,
            "pool_id",
            pool_id,
        )

        object.__setattr__(
            self,
            "worker_type",
            worker_type,
        )

        object.__setattr__(
            self,
            "members",
            members,
        )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_POOL_SNAPSHOT_SCHEMA_VERSION
        ):

            raise UniversalWorkerPoolError(
                (
                    "Invalid Worker Pool Snapshot "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_pool_snapshot_"
                    "schema_version"
                ),
                value=self.schema_version,
            )

    @property
    def member_count(
        self,
    ) -> int:

        return len(
            self.members
        )

    @property
    def worker_identities(
        self,
    ) -> tuple[str, ...]:

        return tuple(
            member.worker_identity
            for member in self.members
        )


def create_universal_worker_pool_snapshot(
    *,
    pool_id: str,
    worker_type: str,
    members: Iterable[
        UniversalWorkerPoolMember
    ] = (),
) -> UniversalWorkerPoolSnapshot:

    return UniversalWorkerPoolSnapshot(
        pool_id=pool_id,
        worker_type=worker_type,
        members=tuple(members),
    )


def create_universal_worker_pool_from_registrations(
    *,
    pool_id: str,
    worker_type: str,
    registrations: Iterable[
        UniversalWorkerRegistration
    ],
) -> UniversalWorkerPoolSnapshot:

    try:
        supplied = tuple(
            registrations
        )

    except TypeError as exc:

        raise UniversalWorkerPoolError(
            "registrations must be iterable.",
            code="invalid_worker_pool_registrations",
            value=registrations,
        ) from exc

    members = []

    normalized_pool_worker_type = (
        normalize_universal_worker_type(
            worker_type
        )
    )

    for registration in supplied:

        member = (
            create_universal_worker_pool_member(
                registration
            )
        )

        if (
            member.worker_type
            != normalized_pool_worker_type
        ):

            raise UniversalWorkerPoolError(
                (
                    "registration worker_type does not "
                    "match pool worker_type."
                ),
                code="worker_pool_type_mismatch",
                value={
                    "pool_worker_type":
                        normalized_pool_worker_type,

                    "registration_worker_type":
                        member.worker_type,

                    "worker_identity":
                        member.worker_identity,
                },
            )

        members.append(
            member
        )

    return UniversalWorkerPoolSnapshot(
        pool_id=pool_id,
        worker_type=normalized_pool_worker_type,
        members=tuple(members),
    )


def is_universal_worker_pool_member(
    pool: UniversalWorkerPoolSnapshot,
    registration: UniversalWorkerRegistration,
) -> bool:

    if not isinstance(
        pool,
        UniversalWorkerPoolSnapshot,
    ):

        raise UniversalWorkerPoolError(
            (
                "pool must be "
                "UniversalWorkerPoolSnapshot."
            ),
            code="invalid_worker_pool_snapshot",
            value=pool,
        )

    member = (
        create_universal_worker_pool_member(
            registration
        )
    )

    return (
        member.worker_type
        == pool.worker_type
        and
        member.worker_identity
        in pool.worker_identities
    )


def add_universal_worker_pool_member(
    pool: UniversalWorkerPoolSnapshot,
    registration: UniversalWorkerRegistration,
) -> UniversalWorkerPoolSnapshot:

    if not isinstance(
        pool,
        UniversalWorkerPoolSnapshot,
    ):

        raise UniversalWorkerPoolError(
            (
                "pool must be "
                "UniversalWorkerPoolSnapshot."
            ),
            code="invalid_worker_pool_snapshot",
            value=pool,
        )

    member = (
        create_universal_worker_pool_member(
            registration
        )
    )

    if member.worker_type != pool.worker_type:

        raise UniversalWorkerPoolError(
            (
                "registration worker_type does not "
                "match pool worker_type."
            ),
            code="worker_pool_type_mismatch",
            value={
                "pool_worker_type":
                    pool.worker_type,

                "registration_worker_type":
                    member.worker_type,

                "worker_identity":
                    member.worker_identity,
            },
        )

    if (
        member.worker_identity
        in pool.worker_identities
    ):

        raise UniversalWorkerPoolError(
            "Worker is already a pool member.",
            code="duplicate_worker_pool_member",
            value=member.worker_identity,
        )

    return UniversalWorkerPoolSnapshot(
        pool_id=pool.pool_id,
        worker_type=pool.worker_type,
        members=(
            pool.members
            + (member,)
        ),
    )


def remove_universal_worker_pool_member(
    pool: UniversalWorkerPoolSnapshot,
    registration: UniversalWorkerRegistration,
) -> UniversalWorkerPoolSnapshot:

    if not isinstance(
        pool,
        UniversalWorkerPoolSnapshot,
    ):

        raise UniversalWorkerPoolError(
            (
                "pool must be "
                "UniversalWorkerPoolSnapshot."
            ),
            code="invalid_worker_pool_snapshot",
            value=pool,
        )

    member = (
        create_universal_worker_pool_member(
            registration
        )
    )

    if (
        member.worker_identity
        not in pool.worker_identities
    ):

        raise UniversalWorkerPoolError(
            "Worker is not a member of the pool.",
            code="worker_pool_member_not_found",
            value=member.worker_identity,
        )

    remaining = tuple(
        existing
        for existing in pool.members
        if (
            existing.worker_identity
            != member.worker_identity
        )
    )

    return UniversalWorkerPoolSnapshot(
        pool_id=pool.pool_id,
        worker_type=pool.worker_type,
        members=remaining,
    )


def explain_universal_worker_pool_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.9",

            "component":
                "Universal Worker Pool Infrastructure",

            "version":
                UNIVERSAL_WORKER_POOL_VERSION,

            "member_schema_version":
                UNIVERSAL_WORKER_POOL_MEMBER_SCHEMA_VERSION,

            "snapshot_schema_version":
                UNIVERSAL_WORKER_POOL_SNAPSHOT_SCHEMA_VERSION,

            "identity_rule": (
                "pool_id is stable caller-supplied "
                "logical identity"
            ),

            "membership_rule": (
                "worker membership is explicit and "
                "is never inferred from worker_type"
            ),

            "worker_type_rule": (
                "a pool has one worker_type and every "
                "member registration must match it"
            ),

            "snapshot_rule": (
                "pool membership changes return a new "
                "immutable deterministic snapshot"
            ),

            "global_exclusivity_rule": (
                "4.1.9 validates one pool snapshot at "
                "a time and does not claim global "
                "one-pool-per-worker exclusivity"
            ),

            "default_pool_rule": (
                "4.1.9 creates no implicit default pool"
            ),

            "taxonomy_rule": (
                "shared, dedicated and system pool "
                "taxonomy is not invented in v1"
            ),

            "workspace_product_boundary": (
                "workspace and product isolation policy "
                "remain outside the base pool contract"
            ),

            "registration_boundary": (
                "4.1.9 consumes immutable Worker "
                "Registration identity but does not "
                "create, alter or delete registrations"
            ),

            "discovery_assignment_boundary": (
                "4.1.9 does not discover or assign "
                "workers; callers may provide pool "
                "members as eligibility evidence to "
                "those authorities"
            ),

            "scaling_boundary": (
                "4.1.7 may later consume caller-composed "
                "per-pool counts but 4.1.9 does not "
                "perform scaling"
            ),

            "shutdown_drain_boundary": (
                "shutdown and drain do not implicitly "
                "remove Worker Pool membership"
            ),

            "capability_capacity_boundary": (
                "Worker Capability and Worker Capacity "
                "remain independent authorities"
            ),

            "persistence_boundary": (
                "4.1.9 does not persist pool definitions "
                "or membership snapshots"
            ),

            "purity_rule": (
                "Worker Pool Infrastructure performs "
                "deterministic immutable transformations "
                "with no external state mutation"
            ),

            "prohibitions": (
                "does not infer membership from worker_type",
                "does not create an implicit default pool",
                "does not invent shared pool policy",
                "does not invent dedicated pool policy",
                "does not enforce workspace isolation policy",
                "does not enforce product isolation policy",
                "does not create worker registrations",
                "does not modify worker registrations",
                "does not delete worker registrations",
                "does not discover workers",
                "does not assign workers",
                "does not lease workers",
                "does not inspect worker health",
                "does not inspect worker heartbeats",
                "does not detect stale workers",
                "does not recover workers",
                "does not scale workers",
                "does not shut down workers",
                "does not drain workers",
                "does not inspect worker capabilities",
                "does not calculate worker capacity",
                "does not provision workers",
                "does not terminate workers",
                "does not mutate Queue Infrastructure",
                "does not access Runtime State Store",
                "does not access orchestration",
                "does not persist pool state",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_POOL_VERSION",
    "UNIVERSAL_WORKER_POOL_MEMBER_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_POOL_SNAPSHOT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_POOL_ID_LENGTH",
    "UNIVERSAL_WORKER_POOL_IDENTITY_SEPARATOR",
    "UniversalWorkerPoolError",
    "UniversalWorkerPoolMember",
    "UniversalWorkerPoolSnapshot",
    "normalize_universal_worker_pool_id",
    "create_universal_worker_pool_member",
    "create_universal_worker_pool_snapshot",
    "create_universal_worker_pool_from_registrations",
    "is_universal_worker_pool_member",
    "add_universal_worker_pool_member",
    "remove_universal_worker_pool_member",
    "explain_universal_worker_pool_v1",
]
'''


ast.parse(SOURCE)

POOL_PATH.write_text(
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
    "universal_worker.pool"
)

sys.modules.pop(
    module_name,
    None,
)

pool = importlib.import_module(
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
    worker_id,
    instance_id,
    worker_type="semantic_worker",
):

    return registration.create_universal_worker_registration(
        worker_id=worker_id,
        worker_type=worker_type,
        worker_instance_id=instance_id,
        runtime_version="runtime-v1",
        host_id="host-1",
        registered_at="2026-08-17T00:00:00+00:00",
    )


# ============================================================
# CONSTANTS / SURFACE
# ============================================================

check(
    "version",
    pool.UNIVERSAL_WORKER_POOL_VERSION
    == "universal_worker_pool_v4.1.9",
)

check(
    "member_schema",
    pool.UNIVERSAL_WORKER_POOL_MEMBER_SCHEMA_VERSION
    == "universal_worker_pool_member_schema_v1",
)

check(
    "snapshot_schema",
    pool.UNIVERSAL_WORKER_POOL_SNAPSHOT_SCHEMA_VERSION
    == "universal_worker_pool_snapshot_schema_v1",
)

check(
    "max_pool_id",
    pool.MAX_UNIVERSAL_WORKER_POOL_ID_LENGTH
    == 200,
)

check(
    "identity_separator",
    pool.UNIVERSAL_WORKER_POOL_IDENTITY_SEPARATOR
    == "::",
)


# ============================================================
# POOL ID
# ============================================================

check(
    "pool_id_normalized",
    pool.normalize_universal_worker_pool_id(
        "  semantic-main  "
    )
    == "semantic-main",
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
        pool.normalize_universal_worker_pool_id(
            bad
        )

    except pool.UniversalWorkerPoolError as exc:
        rejected = (
            exc.code
            == "invalid_worker_pool_id_type"
        )

    else:
        rejected = False

    check(
        "pool_id_bad_type_"
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
        pool.normalize_universal_worker_pool_id(
            bad
        )

    except pool.UniversalWorkerPoolError as exc:
        rejected = (
            exc.code
            == "empty_worker_pool_id"
        )

    else:
        rejected = False

    check(
        "pool_id_blank_"
        + repr(bad),
        rejected,
    )


exact_max = (
    "p"
    * pool.MAX_UNIVERSAL_WORKER_POOL_ID_LENGTH
)

check(
    "pool_id_exact_max",
    pool.normalize_universal_worker_pool_id(
        exact_max
    )
    == exact_max,
)


try:
    pool.normalize_universal_worker_pool_id(
        exact_max + "x"
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "worker_pool_id_too_long"
    )

else:
    rejected = False


check(
    "pool_id_overflow",
    rejected,
)


try:
    pool.normalize_universal_worker_pool_id(
        "pool::one"
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "reserved_worker_pool_id_separator"
    )

else:
    rejected = False


check(
    "reserved_separator_rejected",
    rejected,
)


# ============================================================
# MEMBER CREATION
# ============================================================

r1 = make_registration(
    "worker-a",
    "instance-2",
)

r2 = make_registration(
    "worker-a",
    "instance-1",
)

r3 = make_registration(
    "worker-b",
    "instance-1",
)

other_type = make_registration(
    "worker-c",
    "instance-1",
    "other_worker",
)


m1 = pool.create_universal_worker_pool_member(
    r1
)

check(
    "member_worker_id",
    m1.worker_id == "worker-a",
)

check(
    "member_instance",
    m1.worker_instance_id == "instance-2",
)

check(
    "member_type",
    m1.worker_type == "semantic_worker",
)

check(
    "member_identity",
    m1.worker_identity
    == "worker-a::instance-2",
)


# ============================================================
# SNAPSHOT / SORTING
# ============================================================

snapshot = (
    pool.create_universal_worker_pool_from_registrations(
        pool_id="semantic-main",
        worker_type="semantic_worker",
        registrations=(
            r1,
            r3,
            r2,
        ),
    )
)

check(
    "snapshot_pool_id",
    snapshot.pool_id
    == "semantic-main",
)

check(
    "snapshot_worker_type",
    snapshot.worker_type
    == "semantic_worker",
)

check(
    "snapshot_count",
    snapshot.member_count
    == 3,
)

check(
    "snapshot_deterministic_order",
    snapshot.worker_identities
    == (
        "worker-a::instance-1",
        "worker-a::instance-2",
        "worker-b::instance-1",
    ),
)


empty = (
    pool.create_universal_worker_pool_snapshot(
        pool_id="empty",
        worker_type="semantic_worker",
    )
)

check(
    "empty_pool_allowed",
    empty.member_count
    == 0,
)


# ============================================================
# MEMBERSHIP
# ============================================================

check(
    "member_true",
    pool.is_universal_worker_pool_member(
        snapshot,
        r1,
    )
    is True,
)

outsider = make_registration(
    "worker-z",
    "instance-9",
)

check(
    "outsider_false",
    pool.is_universal_worker_pool_member(
        snapshot,
        outsider,
    )
    is False,
)

check(
    "wrong_type_false",
    pool.is_universal_worker_pool_member(
        snapshot,
        other_type,
    )
    is False,
)


# ============================================================
# TYPE CONSTRAINT
# ============================================================

try:
    pool.create_universal_worker_pool_from_registrations(
        pool_id="bad-type",
        worker_type="semantic_worker",
        registrations=(
            r1,
            other_type,
        ),
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "worker_pool_type_mismatch"
    )

else:
    rejected = False


check(
    "mixed_worker_type_rejected",
    rejected,
)


# ============================================================
# DUPLICATE MEMBERSHIP
# ============================================================

try:
    pool.create_universal_worker_pool_from_registrations(
        pool_id="duplicate",
        worker_type="semantic_worker",
        registrations=(
            r1,
            r1,
        ),
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "duplicate_worker_pool_member"
    )

else:
    rejected = False


check(
    "duplicate_member_rejected",
    rejected,
)


# ============================================================
# PURE ADD
# ============================================================

base = (
    pool.create_universal_worker_pool_from_registrations(
        pool_id="semantic-main",
        worker_type="semantic_worker",
        registrations=(
            r1,
        ),
    )
)

added = (
    pool.add_universal_worker_pool_member(
        base,
        r2,
    )
)

check(
    "add_returns_new_snapshot",
    added is not base,
)

check(
    "original_unchanged_after_add",
    base.member_count
    == 1,
)

check(
    "added_count",
    added.member_count
    == 2,
)

check(
    "added_membership",
    pool.is_universal_worker_pool_member(
        added,
        r2,
    )
    is True,
)


try:
    pool.add_universal_worker_pool_member(
        base,
        r1,
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "duplicate_worker_pool_member"
    )

else:
    rejected = False


check(
    "duplicate_add_rejected",
    rejected,
)


try:
    pool.add_universal_worker_pool_member(
        base,
        other_type,
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "worker_pool_type_mismatch"
    )

else:
    rejected = False


check(
    "wrong_type_add_rejected",
    rejected,
)


# ============================================================
# PURE REMOVE
# ============================================================

removed = (
    pool.remove_universal_worker_pool_member(
        added,
        r2,
    )
)

check(
    "remove_returns_new_snapshot",
    removed is not added,
)

check(
    "source_unchanged_after_remove",
    added.member_count
    == 2,
)

check(
    "removed_count",
    removed.member_count
    == 1,
)

check(
    "removed_membership_false",
    pool.is_universal_worker_pool_member(
        removed,
        r2,
    )
    is False,
)


try:
    pool.remove_universal_worker_pool_member(
        base,
        outsider,
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "worker_pool_member_not_found"
    )

else:
    rejected = False


check(
    "missing_remove_rejected",
    rejected,
)


# ============================================================
# IMMUTABILITY
# ============================================================

for obj, field_name in (
    (m1, "worker_id"),
    (m1, "worker_instance_id"),
    (m1, "worker_type"),
    (m1, "schema_version"),
    (snapshot, "pool_id"),
    (snapshot, "worker_type"),
    (snapshot, "members"),
    (snapshot, "schema_version"),
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
            + type(obj).__name__
            + "_"
            + field_name
        ),
        immutable,
    )


# ============================================================
# DETERMINISM
# ============================================================

snapshot_again = (
    pool.create_universal_worker_pool_from_registrations(
        pool_id="semantic-main",
        worker_type="semantic_worker",
        registrations=(
            r3,
            r2,
            r1,
        ),
    )
)

check(
    "snapshot_order_input_independent",
    snapshot
    == snapshot_again,
)


# ============================================================
# SCHEMA TAMPERING
# ============================================================

try:
    pool.UniversalWorkerPoolMember(
        worker_id="worker-a",
        worker_instance_id="instance-1",
        worker_type="semantic_worker",
        schema_version="tampered",
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "invalid_worker_pool_member_schema_version"
    )

else:
    rejected = False


check(
    "member_schema_tamper",
    rejected,
)


try:
    pool.UniversalWorkerPoolSnapshot(
        pool_id="semantic-main",
        worker_type="semantic_worker",
        members=(),
        schema_version="tampered",
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "invalid_worker_pool_snapshot_schema_version"
    )

else:
    rejected = False


check(
    "snapshot_schema_tamper",
    rejected,
)


# ============================================================
# EXPLANATION
# ============================================================

explanation = (
    pool.explain_universal_worker_pool_v1()
)

check(
    "explanation_phase",
    explanation.get("phase")
    == "4.1.9",
)

check(
    "explanation_component",
    explanation.get("component")
    == "Universal Worker Pool Infrastructure",
)

check(
    "explicit_membership",
    "never inferred"
    in explanation.get(
        "membership_rule",
        "",
    ),
)

check(
    "one_worker_type",
    "one worker_type"
    in explanation.get(
        "worker_type_rule",
        "",
    ),
)

check(
    "immutable_snapshot_rule",
    "new immutable"
    in explanation.get(
        "snapshot_rule",
        "",
    ),
)

check(
    "no_global_exclusivity_claim",
    "does not claim global"
    in explanation.get(
        "global_exclusivity_rule",
        "",
    ),
)

check(
    "no_default_pool",
    "no implicit default pool"
    in explanation.get(
        "default_pool_rule",
        "",
    ),
)

check(
    "no_taxonomy_invented",
    "not invented"
    in explanation.get(
        "taxonomy_rule",
        "",
    ),
)

check(
    "registration_boundary",
    "does not create"
    in explanation.get(
        "registration_boundary",
        "",
    ),
)

check(
    "assignment_boundary",
    "does not discover or assign"
    in explanation.get(
        "discovery_assignment_boundary",
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

check(
    "purity_rule",
    "no external state mutation"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


# ============================================================
# PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not infer membership from worker_type",
    "does not create an implicit default pool",
    "does not invent shared pool policy",
    "does not invent dedicated pool policy",
    "does not enforce workspace isolation policy",
    "does not enforce product isolation policy",
    "does not create worker registrations",
    "does not modify worker registrations",
    "does not delete worker registrations",
    "does not discover workers",
    "does not assign workers",
    "does not lease workers",
    "does not inspect worker health",
    "does not inspect worker heartbeats",
    "does not detect stale workers",
    "does not recover workers",
    "does not scale workers",
    "does not shut down workers",
    "does not drain workers",
    "does not inspect worker capabilities",
    "does not calculate worker capacity",
    "does not provision workers",
    "does not terminate workers",
    "does not mutate Queue Infrastructure",
    "does not access Runtime State Store",
    "does not access orchestration",
    "does not persist pool state",
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

source = POOL_PATH.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(source)

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


check(
    "backend_imports_exact",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.registration",
    ],
    backend_imports,
)


# ============================================================
# FORBIDDEN SIDE EFFECT CALLS
# ============================================================

forbidden_names = {
    "open",
    "read_text",
    "write_text",
    "mkdir",
    "unlink",
    "remove",
    "now",
    "utcnow",
    "time",
    "sleep",
    "worker_heartbeat",
    "inspect_workers",
    "discover_universal_workers",
    "assign_universal_worker",
    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",
    "evaluate_universal_worker_health",
    "evaluate_universal_worker_recovery",
    "evaluate_universal_worker_scaling",
    "evaluate_universal_worker_shutdown",
    "get_runtime_state_store_registry",
    "enqueue_job",
    "dequeue_job",
    "requeue_job",
    "dispatch_job",
    "execute_job",
    "shutdown",
    "terminate",
    "provision",
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
        call_name = node.func.id

    elif isinstance(
        node.func,
        ast.Attribute,
    ):
        call_name = node.func.attr

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
# PROTECTED AUTHORITIES
# ============================================================

for name, (path, expected) in PROTECTED.items():

    actual = ast_sha(path)

    check(
        "protected_"
        + name,
        actual == expected,
        actual,
    )


pool_ast = ast_sha(
    POOL_PATH
)


check(
    "pool_ast_generated",
    len(pool_ast)
    == 64,
    pool_ast,
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

total = len(checks)


lines = [
    (
        "PHASE 4.1.9 — UNIVERSAL WORKER POOL "
        "INFRASTRUCTURE INITIAL IMPLEMENTATION"
    ),
    "=" * 112,
    "",
    "WORKER POOL AST SHA256: "
    + pool_ast,
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
            "INITIAL WORKER POOL RESULT: "
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
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "RUNTIME SHUTDOWN PROCESS MODIFIED: NO",
        "RUNTIME LIFECYCLE MANAGER MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "IMPLICIT DEFAULT POOL CREATED: NO",
        "SHARED/DEDICATED TAXONOMY INVENTED: NO",
        "MEMBERSHIP INFERRED FROM WORKER TYPE: NO",
        "WORKER REGISTRATION MUTATED: NO",
        "WORKER DISCOVERED: NO",
        "WORKER ASSIGNED: NO",
        "WORKER LEASED: NO",
        "WORKER HEALTH INSPECTED: NO",
        "WORKER HEARTBEAT INSPECTED: NO",
        "STALE WORKER DETECTED: NO",
        "WORKER RECOVERY PERFORMED: NO",
        "WORKER SCALING PERFORMED: NO",
        "WORKER SHUTDOWN PERFORMED: NO",
        "WORKER DRAIN PERFORMED: NO",
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER CAPACITY CALCULATED: NO",
        "WORKER PROVISIONED/TERMINATED: NO",
        "QUEUE MUTATED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "POOL STATE PERSISTED: NO",
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
        "Phase 4.1.9 Worker Pool initial implementation failed."
    )
