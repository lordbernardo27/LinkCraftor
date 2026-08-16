from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

DISCOVERY_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "discovery.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_2_worker_discovery_initial_implementation.txt"
)


# ============================================================
# PROTECTED AUTHORITIES
# ============================================================

PROTECTED = {
    "worker_registration": (
        ROOT / "backend/server/runtime/universal_worker/registration.py",
        "00F0D6E620E24A7433C880B722E023AF3C2121563F8E18DFA9979E0F06A36D64",
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


before = {}


for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(path)

    if actual != expected:

        raise SystemExit(
            (
                "Protected authority mismatch before "
                "4.1.2 implementation: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )

    before[name] = actual


# ============================================================
# PRODUCTION 4.1.2 AUTHORITY
# ============================================================

SOURCE = r'''from __future__ import annotations

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
'''


# Validate before writing
ast.parse(
    SOURCE
)

DISCOVERY_PATH.write_text(
    SOURCE,
    encoding="utf-8",
)


# ============================================================
# VERIFY PROTECTED FILES UNCHANGED
# ============================================================

for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(path)

    if actual != expected:

        raise SystemExit(
            (
                "Protected authority changed during "
                "4.1.2 implementation: "
                + name
            )
        )


# ============================================================
# IMPORT
# ============================================================

sys.path.insert(
    0,
    str(ROOT),
)

registration_module_name = (
    "backend.server.runtime."
    "universal_worker.registration"
)

discovery_module_name = (
    "backend.server.runtime."
    "universal_worker.discovery"
)

sys.modules.pop(
    discovery_module_name,
    None,
)

registration_module = (
    importlib.import_module(
        registration_module_name
    )
)

discovery_module = (
    importlib.import_module(
        discovery_module_name
    )
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
# VERSION / SCHEMAS
# ============================================================

check(
    "version",
    discovery_module.UNIVERSAL_WORKER_DISCOVERY_VERSION
    == "universal_worker_discovery_v4.1.2",
)

check(
    "candidate_schema",
    discovery_module.UNIVERSAL_WORKER_DISCOVERY_CANDIDATE_SCHEMA_VERSION
    == "universal_worker_discovery_candidate_schema_v1",
)

check(
    "decision_schema",
    discovery_module.UNIVERSAL_WORKER_DISCOVERY_DECISION_SCHEMA_VERSION
    == "universal_worker_discovery_decision_schema_v1",
)

check(
    "result_schema",
    discovery_module.UNIVERSAL_WORKER_DISCOVERY_RESULT_SCHEMA_VERSION
    == "universal_worker_discovery_result_schema_v1",
)


# ============================================================
# REGISTRATION FIXTURES
# ============================================================

def registration(
    worker_id,
    instance_id,
):

    return (
        registration_module.create_universal_worker_registration(
            worker_id=worker_id,
            worker_type="general",
            worker_instance_id=instance_id,
            runtime_version="runtime-v1",
            host_id="host-a",
            registered_at="2026-08-15T20:00:00Z",
        )
    )


worker_b = registration(
    "worker-b",
    "instance-002",
)

worker_a2 = registration(
    "worker-a",
    "instance-002",
)

worker_a1 = registration(
    "worker-a",
    "instance-001",
)


candidate_b = (
    discovery_module.create_universal_worker_discovery_candidate(
        registration=worker_b,
        discovery_enabled=True,
    )
)

candidate_a2 = (
    discovery_module.create_universal_worker_discovery_candidate(
        registration=worker_a2,
        discovery_enabled=False,
    )
)

candidate_a1 = (
    discovery_module.create_universal_worker_discovery_candidate(
        registration=worker_a1,
        discovery_enabled=True,
    )
)


# ============================================================
# SINGLE DECISIONS
# ============================================================

decision_true = (
    discovery_module.decide_universal_worker_discoverability(
        candidate_a1
    )
)

decision_false = (
    discovery_module.decide_universal_worker_discoverability(
        candidate_a2
    )
)


check(
    "enabled_discoverable",
    decision_true.discoverable
    is True,
)

check(
    "enabled_classification",
    decision_true.discoverability
    is discovery_module.UniversalWorkerDiscoverability.DISCOVERABLE,
)

check(
    "disabled_not_discoverable",
    decision_false.discoverable
    is False,
)

check(
    "disabled_classification",
    decision_false.discoverability
    is discovery_module.UniversalWorkerDiscoverability.NOT_DISCOVERABLE,
)


# ============================================================
# COLLECTION DISCOVERY
# ============================================================

result = (
    discovery_module.discover_universal_workers(
        (
            candidate_b,
            candidate_a2,
            candidate_a1,
        )
    )
)


check(
    "decision_count",
    len(result.decisions)
    == 3,
)

check(
    "discoverable_count",
    result.discoverable_count
    == 2,
)

check(
    "deterministic_decision_order",
    tuple(
        (
            item.worker_id,
            item.worker_instance_id,
        )
        for item in result.decisions
    )
    == (
        (
            "worker-a",
            "instance-001",
        ),
        (
            "worker-a",
            "instance-002",
        ),
        (
            "worker-b",
            "instance-002",
        ),
    ),
)

check(
    "discoverable_worker_order",
    tuple(
        item.canonical_identity
        for item in result.discoverable_workers
    )
    == (
        (
            "worker-a",
            "instance-001",
        ),
        (
            "worker-b",
            "instance-002",
        ),
    ),
)


# ============================================================
# EMPTY DISCOVERY
# ============================================================

empty = (
    discovery_module.discover_universal_workers(
        ()
    )
)


check(
    "empty_decisions",
    empty.decisions
    == (),
)

check(
    "empty_discoverable_workers",
    empty.discoverable_workers
    == (),
)

check(
    "empty_count",
    empty.discoverable_count
    == 0,
)


# ============================================================
# STRICT BOOL
# ============================================================

for bad in (
    None,
    0,
    1,
    "",
    "true",
    [],
    {},
):

    try:

        discovery_module.create_universal_worker_discovery_candidate(
            registration=worker_a1,
            discovery_enabled=bad,
        )

    except discovery_module.UniversalWorkerDiscoveryError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_enabled_"
        + type(bad).__name__
        + "_"
        + repr(bad),
        rejected,
    )


# ============================================================
# REGISTRATION TYPE
# ============================================================

for bad in (
    None,
    True,
    1,
    "",
    {},
    [],
):

    try:

        discovery_module.create_universal_worker_discovery_candidate(
            registration=bad,
            discovery_enabled=True,
        )

    except discovery_module.UniversalWorkerDiscoveryError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_registration_"
        + type(bad).__name__,
        rejected,
    )


# ============================================================
# DUPLICATE IDENTITY
# ============================================================

duplicate_candidate = (
    discovery_module.create_universal_worker_discovery_candidate(
        registration=worker_a1,
        discovery_enabled=False,
    )
)


try:

    discovery_module.discover_universal_workers(
        (
            candidate_a1,
            duplicate_candidate,
        )
    )

except discovery_module.UniversalWorkerDiscoveryError as exc:

    duplicate_rejected = (
        exc.code
        == "duplicate_worker_discovery_candidate_identity"
    )

else:

    duplicate_rejected = False


check(
    "duplicate_identity_rejected",
    duplicate_rejected,
)


# ============================================================
# BAD COLLECTIONS
# ============================================================

for bad in (
    None,
    "worker",
    b"worker",
    {},
    1,
    True,
):

    try:

        discovery_module.discover_universal_workers(
            bad
        )

    except discovery_module.UniversalWorkerDiscoveryError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_collection_"
        + type(bad).__name__,
        rejected,
    )


# ============================================================
# IMMUTABILITY
# ============================================================

for obj, field in (
    (
        candidate_a1,
        "discovery_enabled",
    ),
    (
        decision_true,
        "discoverability",
    ),
    (
        result,
        "decisions",
    ),
):

    try:

        setattr(
            obj,
            field,
            None,
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        "immutable_"
        + type(obj).__name__,
        immutable,
    )


# ============================================================
# EXPLANATION BOUNDARY
# ============================================================

explanation = (
    discovery_module.explain_universal_worker_discovery_v1()
)


check(
    "explanation_phase",
    explanation.get("phase")
    == "4.1.2",
)

check(
    "explanation_component",
    explanation.get("component")
    == "Universal Worker Discovery",
)

check(
    "administrative_meaning",
    "does not mean healthy"
    in explanation.get(
        "meaning",
        "",
    ),
)

check(
    "caller_supplied_evidence",
    "caller-supplied"
    in explanation.get(
        "input_rule",
        "",
    ),
)

check(
    "ordering_rule",
    "worker_id then worker_instance_id"
    in explanation.get(
        "ordering_rule",
        "",
    ),
)

check(
    "pure_no_live_lookup",
    "no live state lookup"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


required_prohibitions = (
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
# STATIC IMPORT BOUNDARY
# ============================================================

source = DISCOVERY_PATH.read_text(
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


check(
    "only_registration_backend_import",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.registration"
    ],
    backend_imports,
)


# ============================================================
# FORBIDDEN CALLS
# ============================================================

forbidden_names = {
    "open",
    "read_text",
    "write_text",
    "mkdir",
    "unlink",
    "read_json",
    "write_json",
    "inspect_workers",
    "worker_heartbeat",
    "get_runtime_state_store_registry",
    "get_latest_worker_statuses",
    "assign_worker",
    "claim_job",
    "dequeue_job",
    "lease_job",
    "dispatch_job",
    "execute_job",
    "register_handler",
}


found_forbidden_calls = []


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
# PROTECTED AST RECHECK
# ============================================================

for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(path)

    check(
        "protected_"
        + name,
        actual
        == expected,
        actual,
    )


# ============================================================
# DISCOVERY AST
# ============================================================

discovery_ast = ast_sha(
    DISCOVERY_PATH
)


check(
    "discovery_ast_generated",
    len(discovery_ast)
    == 64,
    discovery_ast,
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
        "PHASE 4.1.2 — UNIVERSAL WORKER "
        "DISCOVERY INITIAL IMPLEMENTATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER DISCOVERY AST SHA256: "
        + discovery_ast
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
            "INITIAL WORKER DISCOVERY RESULT: "
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
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB AUTHORITIES MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "FILESYSTEM WORKERS ENUMERATED: NO",
        "HEARTBEATS READ OR EMITTED: NO",
        "WORKER HEALTH DECIDED: NO",
        "STALE WORKER DETECTION PERFORMED: NO",
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER POOL INSPECTED: NO",
        "WORKER CAPACITY INSPECTED: NO",
        "WORKER ASSIGNED: NO",
        "JOB CLAIMED: NO",
        "JOB LEASED: NO",
        "JOB DISPATCHED: NO",
        "JOB EXECUTED: NO",
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
        "Phase 4.1.2 Worker Discovery initial implementation failed."
    )
