from __future__ import annotations

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
