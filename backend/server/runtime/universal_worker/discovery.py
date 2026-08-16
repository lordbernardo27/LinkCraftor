from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from backend.server.runtime.universal_worker.registration import (
    UniversalWorkerRegistration,
)


UNIVERSAL_WORKER_DISCOVERY_VERSION = (
    "universal_worker_discovery_v4.1.2"
)

UNIVERSAL_WORKER_DISCOVERY_CANDIDATE_SCHEMA_VERSION = (
    "universal_worker_discovery_candidate_schema_v1"
)

UNIVERSAL_WORKER_DISCOVERY_DECISION_SCHEMA_VERSION = (
    "universal_worker_discovery_decision_schema_v1"
)

UNIVERSAL_WORKER_DISCOVERY_RESULT_SCHEMA_VERSION = (
    "universal_worker_discovery_result_schema_v1"
)


class UniversalWorkerDiscoveryError(
    ValueError
):

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:

        super().__init__(message)

        self.code = str(code)
        self.value = value


class UniversalWorkerDiscoverability(
    str,
    Enum,
):

    DISCOVERABLE = "DISCOVERABLE"
    NOT_DISCOVERABLE = "NOT_DISCOVERABLE"


def _validate_registration(
    value: Any,
) -> UniversalWorkerRegistration:

    if not isinstance(
        value,
        UniversalWorkerRegistration,
    ):

        raise UniversalWorkerDiscoveryError(
            (
                "registration must be a "
                "UniversalWorkerRegistration."
            ),
            code="invalid_worker_registration",
            value=value,
        )

    return value


def _validate_discovery_enabled(
    value: Any,
) -> bool:

    if type(value) is not bool:

        raise UniversalWorkerDiscoveryError(
            "discovery_enabled must be a bool.",
            code="invalid_discovery_enabled",
            value=value,
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerDiscoveryCandidate:

    registration: UniversalWorkerRegistration
    discovery_enabled: bool

    schema_version: str = (
        UNIVERSAL_WORKER_DISCOVERY_CANDIDATE_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "registration",
            _validate_registration(
                self.registration
            ),
        )

        object.__setattr__(
            self,
            "discovery_enabled",
            _validate_discovery_enabled(
                self.discovery_enabled
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_DISCOVERY_CANDIDATE_SCHEMA_VERSION
        ):

            raise UniversalWorkerDiscoveryError(
                (
                    "Invalid Worker Discovery "
                    "candidate schema_version."
                ),
                code=(
                    "invalid_worker_discovery_"
                    "candidate_schema_version"
                ),
                value=self.schema_version,
            )

    @property
    def worker_id(
        self,
    ) -> str:

        return self.registration.worker_id

    @property
    def worker_instance_id(
        self,
    ) -> str:

        return self.registration.worker_instance_id

    @property
    def canonical_identity(
        self,
    ) -> tuple[str, str]:

        return self.registration.canonical_identity


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerDiscoveryDecision:

    worker_id: str
    worker_instance_id: str
    discoverability: UniversalWorkerDiscoverability
    discovery_enabled: bool

    schema_version: str = (
        UNIVERSAL_WORKER_DISCOVERY_DECISION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        if (
            not isinstance(
                self.worker_id,
                str,
            )
            or not self.worker_id
        ):

            raise UniversalWorkerDiscoveryError(
                "worker_id must be a non-empty string.",
                code="invalid_discovery_decision_worker_id",
                value=self.worker_id,
            )

        if (
            not isinstance(
                self.worker_instance_id,
                str,
            )
            or not self.worker_instance_id
        ):

            raise UniversalWorkerDiscoveryError(
                (
                    "worker_instance_id must be "
                    "a non-empty string."
                ),
                code=(
                    "invalid_discovery_decision_"
                    "worker_instance_id"
                ),
                value=self.worker_instance_id,
            )

        if not isinstance(
            self.discoverability,
            UniversalWorkerDiscoverability,
        ):

            raise UniversalWorkerDiscoveryError(
                (
                    "discoverability must be a "
                    "UniversalWorkerDiscoverability."
                ),
                code="invalid_discoverability",
                value=self.discoverability,
            )

        _validate_discovery_enabled(
            self.discovery_enabled
        )

        expected = (
            UniversalWorkerDiscoverability.DISCOVERABLE
            if self.discovery_enabled
            else
            UniversalWorkerDiscoverability.NOT_DISCOVERABLE
        )

        if self.discoverability is not expected:

            raise UniversalWorkerDiscoveryError(
                (
                    "discoverability is inconsistent "
                    "with discovery_enabled."
                ),
                code="inconsistent_discovery_decision",
                value=self.discoverability,
            )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_DISCOVERY_DECISION_SCHEMA_VERSION
        ):

            raise UniversalWorkerDiscoveryError(
                (
                    "Invalid Worker Discovery "
                    "decision schema_version."
                ),
                code=(
                    "invalid_worker_discovery_"
                    "decision_schema_version"
                ),
                value=self.schema_version,
            )

    @property
    def discoverable(
        self,
    ) -> bool:

        return (
            self.discoverability
            is UniversalWorkerDiscoverability.DISCOVERABLE
        )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerDiscoveryResult:

    decisions: tuple[
        UniversalWorkerDiscoveryDecision,
        ...
    ]

    discoverable_workers: tuple[
        UniversalWorkerRegistration,
        ...
    ]

    schema_version: str = (
        UNIVERSAL_WORKER_DISCOVERY_RESULT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        if not isinstance(
            self.decisions,
            tuple,
        ):

            raise UniversalWorkerDiscoveryError(
                "decisions must be a tuple.",
                code="invalid_discovery_decisions",
                value=self.decisions,
            )

        if not isinstance(
            self.discoverable_workers,
            tuple,
        ):

            raise UniversalWorkerDiscoveryError(
                (
                    "discoverable_workers must "
                    "be a tuple."
                ),
                code=(
                    "invalid_discoverable_workers"
                ),
                value=self.discoverable_workers,
            )

        for decision in self.decisions:

            if not isinstance(
                decision,
                UniversalWorkerDiscoveryDecision,
            ):

                raise UniversalWorkerDiscoveryError(
                    (
                        "Every decision must be a "
                        "UniversalWorkerDiscoveryDecision."
                    ),
                    code="invalid_discovery_decision",
                    value=decision,
                )

        for registration in self.discoverable_workers:

            _validate_registration(
                registration
            )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_DISCOVERY_RESULT_SCHEMA_VERSION
        ):

            raise UniversalWorkerDiscoveryError(
                (
                    "Invalid Worker Discovery "
                    "result schema_version."
                ),
                code=(
                    "invalid_worker_discovery_"
                    "result_schema_version"
                ),
                value=self.schema_version,
            )

    @property
    def discoverable_count(
        self,
    ) -> int:

        return len(
            self.discoverable_workers
        )


def create_universal_worker_discovery_candidate(
    *,
    registration: UniversalWorkerRegistration,
    discovery_enabled: bool,
) -> UniversalWorkerDiscoveryCandidate:

    return UniversalWorkerDiscoveryCandidate(
        registration=registration,
        discovery_enabled=discovery_enabled,
    )


def decide_universal_worker_discoverability(
    candidate: UniversalWorkerDiscoveryCandidate,
) -> UniversalWorkerDiscoveryDecision:

    if not isinstance(
        candidate,
        UniversalWorkerDiscoveryCandidate,
    ):

        raise UniversalWorkerDiscoveryError(
            (
                "candidate must be a "
                "UniversalWorkerDiscoveryCandidate."
            ),
            code="invalid_worker_discovery_candidate",
            value=candidate,
        )

    discoverability = (
        UniversalWorkerDiscoverability.DISCOVERABLE
        if candidate.discovery_enabled
        else
        UniversalWorkerDiscoverability.NOT_DISCOVERABLE
    )

    return UniversalWorkerDiscoveryDecision(
        worker_id=candidate.worker_id,
        worker_instance_id=(
            candidate.worker_instance_id
        ),
        discoverability=discoverability,
        discovery_enabled=(
            candidate.discovery_enabled
        ),
    )


def discover_universal_workers(
    candidates: Iterable[
        UniversalWorkerDiscoveryCandidate
    ],
) -> UniversalWorkerDiscoveryResult:

    if isinstance(
        candidates,
        (
            str,
            bytes,
            Mapping,
        ),
    ):

        raise UniversalWorkerDiscoveryError(
            (
                "candidates must be an iterable "
                "of Worker Discovery candidates."
            ),
            code="invalid_worker_discovery_candidates",
            value=candidates,
        )

    try:

        materialized = tuple(
            candidates
        )

    except TypeError as exc:

        raise UniversalWorkerDiscoveryError(
            (
                "candidates must be an iterable "
                "of Worker Discovery candidates."
            ),
            code="invalid_worker_discovery_candidates",
            value=candidates,
        ) from exc

    validated = []

    seen_identities = set()

    for candidate in materialized:

        if not isinstance(
            candidate,
            UniversalWorkerDiscoveryCandidate,
        ):

            raise UniversalWorkerDiscoveryError(
                (
                    "Every discovery candidate must be a "
                    "UniversalWorkerDiscoveryCandidate."
                ),
                code="invalid_worker_discovery_candidate",
                value=candidate,
            )

        identity = (
            candidate.canonical_identity
        )

        if identity in seen_identities:

            raise UniversalWorkerDiscoveryError(
                (
                    "Duplicate worker discovery "
                    "candidate identity."
                ),
                code=(
                    "duplicate_worker_discovery_"
                    "candidate_identity"
                ),
                value=identity,
            )

        seen_identities.add(
            identity
        )

        validated.append(
            candidate
        )

    ordered = tuple(
        sorted(
            validated,
            key=lambda item: (
                item.worker_id,
                item.worker_instance_id,
            ),
        )
    )

    decisions = tuple(
        decide_universal_worker_discoverability(
            candidate
        )
        for candidate in ordered
    )

    discoverable_workers = tuple(
        candidate.registration
        for candidate in ordered
        if candidate.discovery_enabled
    )

    return UniversalWorkerDiscoveryResult(
        decisions=decisions,
        discoverable_workers=(
            discoverable_workers
        ),
    )


def explain_universal_worker_discovery_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.2",

            "component":
                "Universal Worker Discovery",

            "version":
                UNIVERSAL_WORKER_DISCOVERY_VERSION,

            "candidate_schema_version":
                UNIVERSAL_WORKER_DISCOVERY_CANDIDATE_SCHEMA_VERSION,

            "decision_schema_version":
                UNIVERSAL_WORKER_DISCOVERY_DECISION_SCHEMA_VERSION,

            "result_schema_version":
                UNIVERSAL_WORKER_DISCOVERY_RESULT_SCHEMA_VERSION,

            "input_rule": (
                "4.1.2 consumes already-created "
                "UniversalWorkerRegistration records plus "
                "caller-supplied discovery_enabled evidence"
            ),

            "discoverability_rule": (
                "discovery_enabled=True means DISCOVERABLE; "
                "discovery_enabled=False means NOT_DISCOVERABLE"
            ),

            "ordering_rule": (
                "discovery candidates and decisions are ordered "
                "by worker_id then worker_instance_id"
            ),

            "duplicate_rule": (
                "duplicate (worker_id, worker_instance_id) "
                "candidate identities are rejected"
            ),

            "meaning": (
                "discoverability means the worker may be "
                "enumerated for later runtime consideration; "
                "it does not mean healthy, live, capable, "
                "within capacity, assignable or leased"
            ),

            "purity_rule": (
                "Worker Discovery is deterministic over "
                "caller-supplied evidence and performs no "
                "live state lookup or mutation"
            ),

            "prohibitions": (
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
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_DISCOVERY_VERSION",
    "UNIVERSAL_WORKER_DISCOVERY_CANDIDATE_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_DISCOVERY_DECISION_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_DISCOVERY_RESULT_SCHEMA_VERSION",
    "UniversalWorkerDiscoveryError",
    "UniversalWorkerDiscoverability",
    "UniversalWorkerDiscoveryCandidate",
    "UniversalWorkerDiscoveryDecision",
    "UniversalWorkerDiscoveryResult",
    "create_universal_worker_discovery_candidate",
    "decide_universal_worker_discoverability",
    "discover_universal_workers",
    "explain_universal_worker_discovery_v1",
]
