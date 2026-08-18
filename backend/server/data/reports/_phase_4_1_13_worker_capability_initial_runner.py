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

CAPABILITY_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "capability.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_13_worker_capability_initial_implementation.txt"
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
                "4.1.13 implementation: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


SOURCE = r'''from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from backend.server.runtime.universal_worker.registration import (
    UniversalWorkerRegistration,
    normalize_universal_worker_id,
    normalize_universal_worker_instance_id,
    normalize_universal_worker_type,
)


UNIVERSAL_WORKER_CAPABILITY_VERSION = (
    "universal_worker_capability_v4.1.13"
)

UNIVERSAL_WORKER_CAPABILITY_SNAPSHOT_SCHEMA_VERSION = (
    "universal_worker_capability_snapshot_schema_v1"
)

UNIVERSAL_WORKER_CAPABILITY_MATCH_SCHEMA_VERSION = (
    "universal_worker_capability_match_schema_v1"
)

MIN_UNIVERSAL_WORKER_CAPABILITY_LENGTH = 2

MAX_UNIVERSAL_WORKER_CAPABILITY_LENGTH = 128

MAX_UNIVERSAL_WORKER_CAPABILITIES = 1024

UNIVERSAL_WORKER_CAPABILITY_IDENTITY_SEPARATOR = "::"


_CAPABILITY_PATTERN = re.compile(
    r"^[a-z0-9][a-z0-9_.:-]*$"
)


class UniversalWorkerCapabilityError(
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


def normalize_universal_worker_capability(
    value: Any,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalWorkerCapabilityError(
            "Worker capability must be a string.",
            code="invalid_worker_capability",
            value=value,
        )

    normalized = (
        value
        .strip()
        .lower()
    )

    if not (
        MIN_UNIVERSAL_WORKER_CAPABILITY_LENGTH
        <= len(normalized)
        <= MAX_UNIVERSAL_WORKER_CAPABILITY_LENGTH
    ):

        raise UniversalWorkerCapabilityError(
            (
                "Worker capability length must be "
                "between 2 and 128 characters."
            ),
            code="invalid_worker_capability_length",
            value=value,
        )

    if (
        _CAPABILITY_PATTERN.fullmatch(
            normalized
        )
        is None
    ):

        raise UniversalWorkerCapabilityError(
            (
                "Worker capability must contain only "
                "lowercase letters, digits, underscore, "
                "hyphen, period or colon and must begin "
                "with a letter or digit."
            ),
            code="invalid_worker_capability_format",
            value=value,
        )

    return normalized


def normalize_universal_worker_capabilities(
    values: Any,
    *,
    field_name: str = "capabilities",
) -> tuple[str, ...]:

    if (
        isinstance(
            values,
            (
                str,
                bytes,
                bytearray,
                Mapping,
            ),
        )
        or
        not isinstance(
            values,
            Iterable,
        )
    ):

        raise UniversalWorkerCapabilityError(
            (
                field_name
                + " must be an iterable of "
                "capability strings."
            ),
            code="invalid_worker_capability_collection",
            value=values,
        )

    normalized_items = []

    seen = set()

    for item in values:

        capability = (
            normalize_universal_worker_capability(
                item
            )
        )

        if capability in seen:

            raise UniversalWorkerCapabilityError(
                (
                    field_name
                    + " contains duplicate capability: "
                    + capability
                ),
                code="duplicate_worker_capability",
                value=capability,
            )

        seen.add(
            capability
        )

        normalized_items.append(
            capability
        )

        if (
            len(normalized_items)
            > MAX_UNIVERSAL_WORKER_CAPABILITIES
        ):

            raise UniversalWorkerCapabilityError(
                (
                    field_name
                    + " exceeds the supported "
                    "capability count."
                ),
                code="worker_capability_count_too_large",
                value=len(
                    normalized_items
                ),
            )

    return tuple(
        sorted(
            normalized_items
        )
    )


def _normalize_worker_identity(
    *,
    worker_id: Any,
    worker_instance_id: Any,
    worker_type: Any,
) -> tuple[str, str, str]:

    try:

        resolved_worker_id = (
            normalize_universal_worker_id(
                worker_id
            )
        )

        resolved_worker_instance_id = (
            normalize_universal_worker_instance_id(
                worker_instance_id
            )
        )

        resolved_worker_type = (
            normalize_universal_worker_type(
                worker_type
            )
        )

    except Exception as exc:

        raise UniversalWorkerCapabilityError(
            (
                "Invalid canonical worker identity "
                "for Worker Capability."
            ),
            code="invalid_worker_capability_identity",
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
        resolved_worker_id,
        resolved_worker_instance_id,
        resolved_worker_type,
    )


def _validate_registration(
    value: Any,
) -> UniversalWorkerRegistration:

    if not isinstance(
        value,
        UniversalWorkerRegistration,
    ):

        raise UniversalWorkerCapabilityError(
            (
                "registration must be canonical "
                "UniversalWorkerRegistration."
            ),
            code="invalid_worker_capability_registration",
            value=value,
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerCapabilitySnapshot:

    worker_id: str

    worker_instance_id: str

    worker_type: str

    capabilities: tuple[str, ...]

    schema_version: str = (
        UNIVERSAL_WORKER_CAPABILITY_SNAPSHOT_SCHEMA_VERSION
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

        capabilities = (
            normalize_universal_worker_capabilities(
                self.capabilities,
                field_name="capabilities",
            )
        )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_CAPABILITY_SNAPSHOT_SCHEMA_VERSION
        ):

            raise UniversalWorkerCapabilityError(
                (
                    "Invalid Worker Capability "
                    "Snapshot schema_version."
                ),
                code=(
                    "invalid_worker_capability_"
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
            "capabilities",
            capabilities,
        )

    @property
    def worker_identity(
        self,
    ) -> str:

        return (
            self.worker_id
            + UNIVERSAL_WORKER_CAPABILITY_IDENTITY_SEPARATOR
            + self.worker_instance_id
        )

    @property
    def capability_count(
        self,
    ) -> int:

        return len(
            self.capabilities
        )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerCapabilityMatchResult:

    worker_id: str

    worker_instance_id: str

    worker_type: str

    worker_capabilities: tuple[str, ...]

    required_capabilities: tuple[str, ...]

    missing_capabilities: tuple[str, ...]

    compatible: bool

    schema_version: str = (
        UNIVERSAL_WORKER_CAPABILITY_MATCH_SCHEMA_VERSION
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

        worker_capabilities = (
            normalize_universal_worker_capabilities(
                self.worker_capabilities,
                field_name="worker_capabilities",
            )
        )

        required_capabilities = (
            normalize_universal_worker_capabilities(
                self.required_capabilities,
                field_name="required_capabilities",
            )
        )

        missing_capabilities = (
            normalize_universal_worker_capabilities(
                self.missing_capabilities,
                field_name="missing_capabilities",
            )
        )

        expected_missing = tuple(
            capability
            for capability in required_capabilities
            if capability
            not in worker_capabilities
        )

        if (
            missing_capabilities
            != expected_missing
        ):

            raise UniversalWorkerCapabilityError(
                (
                    "missing_capabilities is inconsistent "
                    "with worker and required capabilities."
                ),
                code=(
                    "inconsistent_worker_capability_"
                    "missing_set"
                ),
                value={
                    "expected":
                        expected_missing,

                    "actual":
                        missing_capabilities,
                },
            )

        if type(
            self.compatible
        ) is not bool:

            raise UniversalWorkerCapabilityError(
                "compatible must be bool.",
                code="invalid_worker_capability_compatible",
                value=self.compatible,
            )

        expected_compatible = (
            len(
                expected_missing
            )
            == 0
        )

        if (
            self.compatible
            is not expected_compatible
        ):

            raise UniversalWorkerCapabilityError(
                (
                    "compatible is inconsistent with "
                    "required capability coverage."
                ),
                code=(
                    "inconsistent_worker_capability_"
                    "compatibility"
                ),
                value={
                    "expected":
                        expected_compatible,

                    "actual":
                        self.compatible,
                },
            )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_CAPABILITY_MATCH_SCHEMA_VERSION
        ):

            raise UniversalWorkerCapabilityError(
                (
                    "Invalid Worker Capability Match "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_capability_"
                    "match_schema_version"
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
            "worker_capabilities",
            worker_capabilities,
        )

        object.__setattr__(
            self,
            "required_capabilities",
            required_capabilities,
        )

        object.__setattr__(
            self,
            "missing_capabilities",
            missing_capabilities,
        )

    @property
    def worker_identity(
        self,
    ) -> str:

        return (
            self.worker_id
            + UNIVERSAL_WORKER_CAPABILITY_IDENTITY_SEPARATOR
            + self.worker_instance_id
        )

    @property
    def is_compatible(
        self,
    ) -> bool:

        return self.compatible


def create_universal_worker_capability_snapshot(
    *,
    registration: UniversalWorkerRegistration,
    capabilities: Any,
) -> UniversalWorkerCapabilitySnapshot:

    resolved_registration = (
        _validate_registration(
            registration
        )
    )

    return UniversalWorkerCapabilitySnapshot(
        worker_id=(
            resolved_registration.worker_id
        ),
        worker_instance_id=(
            resolved_registration.worker_instance_id
        ),
        worker_type=(
            resolved_registration.worker_type
        ),
        capabilities=(
            normalize_universal_worker_capabilities(
                capabilities
            )
        ),
    )


def supports_universal_worker_capability(
    *,
    snapshot: UniversalWorkerCapabilitySnapshot,
    capability: Any,
) -> bool:

    if not isinstance(
        snapshot,
        UniversalWorkerCapabilitySnapshot,
    ):

        raise UniversalWorkerCapabilityError(
            (
                "snapshot must be canonical "
                "UniversalWorkerCapabilitySnapshot."
            ),
            code="invalid_worker_capability_snapshot",
            value=snapshot,
        )

    required = (
        normalize_universal_worker_capability(
            capability
        )
    )

    return required in snapshot.capabilities


def match_universal_worker_capabilities(
    *,
    snapshot: UniversalWorkerCapabilitySnapshot,
    required_capabilities: Any,
) -> UniversalWorkerCapabilityMatchResult:

    if not isinstance(
        snapshot,
        UniversalWorkerCapabilitySnapshot,
    ):

        raise UniversalWorkerCapabilityError(
            (
                "snapshot must be canonical "
                "UniversalWorkerCapabilitySnapshot."
            ),
            code="invalid_worker_capability_snapshot",
            value=snapshot,
        )

    required = (
        normalize_universal_worker_capabilities(
            required_capabilities,
            field_name="required_capabilities",
        )
    )

    missing = tuple(
        capability
        for capability in required
        if capability
        not in snapshot.capabilities
    )

    compatible = (
        len(
            missing
        )
        == 0
    )

    return UniversalWorkerCapabilityMatchResult(
        worker_id=snapshot.worker_id,
        worker_instance_id=snapshot.worker_instance_id,
        worker_type=snapshot.worker_type,
        worker_capabilities=snapshot.capabilities,
        required_capabilities=required,
        missing_capabilities=missing,
        compatible=compatible,
    )


def explain_universal_worker_capability_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.13",

            "component":
                "Universal Worker Capability Management",

            "version":
                UNIVERSAL_WORKER_CAPABILITY_VERSION,

            "snapshot_schema_version":
                UNIVERSAL_WORKER_CAPABILITY_SNAPSHOT_SCHEMA_VERSION,

            "match_schema_version":
                UNIVERSAL_WORKER_CAPABILITY_MATCH_SCHEMA_VERSION,

            "scope_rule": (
                "4.1.13 owns individual-worker capability "
                "evidence and deterministic capability "
                "compatibility matching"
            ),

            "identity_rule": (
                "capability snapshots preserve canonical "
                "Worker Registration identity "
                "(worker_id, worker_instance_id)"
            ),

            "worker_type_rule": (
                "worker_type remains worker classification "
                "and does not itself imply capabilities"
            ),

            "capability_rule": (
                "capabilities are generic normalized "
                "lowercase executable-ability tokens"
            ),

            "collection_rule": (
                "capability collections are immutable, "
                "duplicate-free and deterministically sorted"
            ),

            "empty_snapshot_rule": (
                "a worker may validly expose zero capabilities"
            ),

            "matching_rule": (
                "compatibility uses ALL-required matching: "
                "every required capability must exist in "
                "the worker snapshot"
            ),

            "empty_requirement_rule": (
                "an empty required capability collection "
                "has no capability constraint and is "
                "therefore compatible"
            ),

            "assignment_boundary": (
                "compatibility is evidence only; 4.1.13 "
                "does not assign workers and callers may "
                "compose capability evidence before "
                "4.1.3 Worker Assignment"
            ),

            "registration_boundary": (
                "4.1.13 does not mutate Worker Registration"
            ),

            "pool_boundary": (
                "Worker Pool membership does not imply "
                "worker capability"
            ),

            "capacity_boundary": (
                "Worker Capacity is separate and is not "
                "calculated by 4.1.13"
            ),

            "runtime_capability_boundary": (
                "Runtime Capability Negotiation is a "
                "separate runtime/component capability layer"
            ),

            "service_registry_boundary": (
                "Runtime Service Registry capabilities "
                "belong to runtime services, not individual "
                "worker capability evidence"
            ),

            "runtime_registration_boundary": (
                "Runtime Registration job_type-to-handler "
                "mapping is separate from Worker Capability"
            ),

            "supported_job_type_boundary": (
                "supported_job_types in job creation or "
                "submission do not define individual-worker "
                "capabilities"
            ),

            "execution_boundary": (
                "4.1.13 does not dispatch or execute jobs"
            ),

            "persistence_boundary": (
                "4.1.13 does not persist capability state "
                "or access Runtime State Store"
            ),

            "purity_rule": (
                "Worker Capability Management is "
                "deterministic over caller-supplied evidence "
                "and performs no external mutation or I/O"
            ),

            "prohibitions": (
                "does not mutate Worker Registration",
                "does not infer capabilities from worker_type",
                "does not infer capabilities from Worker Pool membership",
                "does not inspect Worker Health",
                "does not inspect Stale Worker Detection",
                "does not inspect Worker Drain",
                "does not calculate Worker Capacity",
                "does not perform Worker Assignment",
                "does not acquire worker leases",
                "does not renew worker leases",
                "does not release worker leases",
                "does not perform Worker Scaling",
                "does not perform Worker Shutdown",
                "does not initiate Worker Recovery",
                "does not register runtime handlers",
                "does not unregister runtime handlers",
                "does not dispatch runtime handlers",
                "does not duplicate Runtime Capability Negotiation",
                "does not register Runtime Service Registry services",
                "does not use supported_job_types as worker capabilities",
                "does not route queue jobs",
                "does not access Queue Infrastructure",
                "does not access orchestration",
                "does not access Runtime State Store",
                "does not persist capability state",
                "does not perform filesystem I/O",
                "does not perform network I/O",
                "does not dispatch jobs",
                "does not execute jobs",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_CAPABILITY_VERSION",
    "UNIVERSAL_WORKER_CAPABILITY_SNAPSHOT_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_CAPABILITY_MATCH_SCHEMA_VERSION",
    "MIN_UNIVERSAL_WORKER_CAPABILITY_LENGTH",
    "MAX_UNIVERSAL_WORKER_CAPABILITY_LENGTH",
    "MAX_UNIVERSAL_WORKER_CAPABILITIES",
    "UNIVERSAL_WORKER_CAPABILITY_IDENTITY_SEPARATOR",
    "UniversalWorkerCapabilityError",
    "UniversalWorkerCapabilitySnapshot",
    "UniversalWorkerCapabilityMatchResult",
    "normalize_universal_worker_capability",
    "normalize_universal_worker_capabilities",
    "create_universal_worker_capability_snapshot",
    "supports_universal_worker_capability",
    "match_universal_worker_capabilities",
    "explain_universal_worker_capability_v1",
]
'''


ast.parse(
    SOURCE
)

CAPABILITY_PATH.write_text(
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
    "universal_worker.capability"
)

sys.modules.pop(
    module_name,
    None,
)

capability = importlib.import_module(
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
        registered_at="2026-08-17T00:00:00+00:00",
    )
)


# ============================================================
# CONSTANTS
# ============================================================

check(
    "version",
    capability.UNIVERSAL_WORKER_CAPABILITY_VERSION
    == "universal_worker_capability_v4.1.13",
)

check(
    "snapshot_schema",
    capability.UNIVERSAL_WORKER_CAPABILITY_SNAPSHOT_SCHEMA_VERSION
    == "universal_worker_capability_snapshot_schema_v1",
)

check(
    "match_schema",
    capability.UNIVERSAL_WORKER_CAPABILITY_MATCH_SCHEMA_VERSION
    == "universal_worker_capability_match_schema_v1",
)

check(
    "min_length",
    capability.MIN_UNIVERSAL_WORKER_CAPABILITY_LENGTH
    == 2,
)

check(
    "max_length",
    capability.MAX_UNIVERSAL_WORKER_CAPABILITY_LENGTH
    == 128,
)

check(
    "max_capabilities",
    capability.MAX_UNIVERSAL_WORKER_CAPABILITIES
    == 1024,
)

check(
    "identity_separator",
    capability.UNIVERSAL_WORKER_CAPABILITY_IDENTITY_SEPARATOR
    == "::",
)


# ============================================================
# TOKEN NORMALIZATION
# ============================================================

valid_tokens = {
    "ab":
        "ab",

    "document.extract":
        "document.extract",

    " Semantic.Read ":
        "semantic.read",

    "body_store.repair":
        "body_store.repair",

    "article-validate":
        "article-validate",

    "runtime:v1":
        "runtime:v1",

    "a1":
        "a1",
}


for raw, expected in (
    valid_tokens.items()
):

    check(
        "valid_token_"
        + repr(raw),
        (
            capability.normalize_universal_worker_capability(
                raw
            )
            == expected
        ),
    )


invalid_tokens = (
    None,
    True,
    False,
    0,
    1,
    "",
    " ",
    "a",
    "_abc",
    "-abc",
    ".abc",
    ":abc",
    "a b",
    "a/b",
    "a\\b",
    "a@b",
    "a#b",
    "x" * 129,
    [],
    {},
    (),
)


for index, bad in enumerate(
    invalid_tokens,
    start=1,
):

    try:

        capability.normalize_universal_worker_capability(
            bad
        )

    except capability.UniversalWorkerCapabilityError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_token_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# COLLECTION
# ============================================================

normalized = (
    capability.normalize_universal_worker_capabilities(
        (
            "semantic.read",
            "document.extract",
            "article.validate",
        )
    )
)


check(
    "collection_sorted",
    normalized
    == (
        "article.validate",
        "document.extract",
        "semantic.read",
    ),
    normalized,
)

check(
    "empty_collection_valid",
    capability.normalize_universal_worker_capabilities(
        ()
    )
    == (),
)


for bad in (
    None,
    "semantic.read",
    b"semantic.read",
    bytearray(b"semantic.read"),
    {
        "semantic.read":
            True
    },
    1,
    True,
):

    try:

        capability.normalize_universal_worker_capabilities(
            bad
        )

    except capability.UniversalWorkerCapabilityError as exc:

        rejected = (
            exc.code
            == "invalid_worker_capability_collection"
        )

    else:

        rejected = False

    check(
        "invalid_collection_"
        + repr(bad),
        rejected,
    )


for duplicate_collection in (
    (
        "semantic.read",
        "semantic.read",
    ),
    (
        "Semantic.Read",
        "semantic.read",
    ),
    (
        " semantic.read ",
        "semantic.read",
    ),
):

    try:

        capability.normalize_universal_worker_capabilities(
            duplicate_collection
        )

    except capability.UniversalWorkerCapabilityError as exc:

        rejected = (
            exc.code
            == "duplicate_worker_capability"
        )

    else:

        rejected = False

    check(
        "duplicate_rejected_"
        + repr(
            duplicate_collection
        ),
        rejected,
    )


# ============================================================
# SNAPSHOT
# ============================================================

snapshot = (
    capability.create_universal_worker_capability_snapshot(
        registration=reg,
        capabilities=(
            "semantic.read",
            "document.extract",
            "article.validate",
        ),
    )
)


check(
    "snapshot_worker_id",
    snapshot.worker_id
    == reg.worker_id,
)

check(
    "snapshot_instance",
    snapshot.worker_instance_id
    == reg.worker_instance_id,
)

check(
    "snapshot_worker_type",
    snapshot.worker_type
    == reg.worker_type,
)

check(
    "snapshot_identity",
    snapshot.worker_identity
    == "worker-a::instance-1",
)

check(
    "snapshot_capability_count",
    snapshot.capability_count
    == 3,
)

check(
    "snapshot_order",
    snapshot.capabilities
    == (
        "article.validate",
        "document.extract",
        "semantic.read",
    ),
)


empty_snapshot = (
    capability.create_universal_worker_capability_snapshot(
        registration=reg,
        capabilities=(),
    )
)


check(
    "zero_capability_worker_valid",
    empty_snapshot.capabilities
    == (),
)

check(
    "zero_capability_count",
    empty_snapshot.capability_count
    == 0,
)


# ============================================================
# SUPPORT CHECK
# ============================================================

check(
    "supports_existing",
    capability.supports_universal_worker_capability(
        snapshot=snapshot,
        capability="semantic.read",
    )
    is True,
)

check(
    "supports_normalized",
    capability.supports_universal_worker_capability(
        snapshot=snapshot,
        capability=" Semantic.Read ",
    )
    is True,
)

check(
    "does_not_support_missing",
    capability.supports_universal_worker_capability(
        snapshot=snapshot,
        capability="body_store.repair",
    )
    is False,
)


# ============================================================
# MATCHING
# ============================================================

compatible = (
    capability.match_universal_worker_capabilities(
        snapshot=snapshot,
        required_capabilities=(
            "semantic.read",
            "article.validate",
        ),
    )
)


check(
    "compatible_true",
    compatible.compatible
    is True,
)

check(
    "is_compatible_true",
    compatible.is_compatible
    is True,
)

check(
    "compatible_missing_empty",
    compatible.missing_capabilities
    == (),
)

check(
    "compatible_requirements_sorted",
    compatible.required_capabilities
    == (
        "article.validate",
        "semantic.read",
    ),
)


incompatible = (
    capability.match_universal_worker_capabilities(
        snapshot=snapshot,
        required_capabilities=(
            "semantic.read",
            "body_store.repair",
        ),
    )
)


check(
    "incompatible_false",
    incompatible.compatible
    is False,
)

check(
    "missing_exact",
    incompatible.missing_capabilities
    == (
        "body_store.repair",
    ),
)


empty_requirement = (
    capability.match_universal_worker_capabilities(
        snapshot=empty_snapshot,
        required_capabilities=(),
    )
)


check(
    "empty_requirement_compatible",
    empty_requirement.compatible
    is True,
)

check(
    "empty_requirement_missing",
    empty_requirement.missing_capabilities
    == (),
)


zero_worker_required = (
    capability.match_universal_worker_capabilities(
        snapshot=empty_snapshot,
        required_capabilities=(
            "semantic.read",
        ),
    )
)


check(
    "zero_worker_required_incompatible",
    zero_worker_required.compatible
    is False,
)

check(
    "zero_worker_required_missing",
    zero_worker_required.missing_capabilities
    == (
        "semantic.read",
    ),
)


# ============================================================
# INVALID REGISTRATION / SNAPSHOT
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

        capability.create_universal_worker_capability_snapshot(
            registration=bad,
            capabilities=(),
        )

    except capability.UniversalWorkerCapabilityError as exc:

        rejected = (
            exc.code
            == "invalid_worker_capability_registration"
        )

    else:

        rejected = False

    check(
        "invalid_registration_"
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

        capability.supports_universal_worker_capability(
            snapshot=bad,
            capability="semantic.read",
        )

    except capability.UniversalWorkerCapabilityError as exc:

        rejected = (
            exc.code
            == "invalid_worker_capability_snapshot"
        )

    else:

        rejected = False

    check(
        "invalid_support_snapshot_"
        + repr(bad),
        rejected,
    )


# ============================================================
# FORGED RESULT
# ============================================================

try:

    capability.UniversalWorkerCapabilityMatchResult(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        worker_capabilities=(
            "semantic.read",
        ),
        required_capabilities=(
            "semantic.read",
            "body_store.repair",
        ),
        missing_capabilities=(),
        compatible=True,
    )

except capability.UniversalWorkerCapabilityError as exc:

    rejected = (
        exc.code
        == "inconsistent_worker_capability_missing_set"
    )

else:

    rejected = False


check(
    "forged_missing_set_rejected",
    rejected,
)


try:

    capability.UniversalWorkerCapabilityMatchResult(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        worker_capabilities=(
            "semantic.read",
        ),
        required_capabilities=(
            "semantic.read",
        ),
        missing_capabilities=(),
        compatible=False,
    )

except capability.UniversalWorkerCapabilityError as exc:

    rejected = (
        exc.code
        == "inconsistent_worker_capability_compatibility"
    )

else:

    rejected = False


check(
    "forged_compatibility_rejected",
    rejected,
)


# ============================================================
# SCHEMA TAMPER
# ============================================================

try:

    capability.UniversalWorkerCapabilitySnapshot(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        capabilities=(),
        schema_version="tampered",
    )

except capability.UniversalWorkerCapabilityError as exc:

    rejected = (
        exc.code
        == "invalid_worker_capability_snapshot_schema_version"
    )

else:

    rejected = False


check(
    "snapshot_schema_tamper_rejected",
    rejected,
)


try:

    capability.UniversalWorkerCapabilityMatchResult(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        worker_capabilities=(),
        required_capabilities=(),
        missing_capabilities=(),
        compatible=True,
        schema_version="tampered",
    )

except capability.UniversalWorkerCapabilityError as exc:

    rejected = (
        exc.code
        == "invalid_worker_capability_match_schema_version"
    )

else:

    rejected = False


check(
    "match_schema_tamper_rejected",
    rejected,
)


# ============================================================
# IMMUTABILITY
# ============================================================

for obj in (
    snapshot,
    compatible,
):

    for field in fields(
        obj
    ):

        try:

            setattr(
                obj,
                field.name,
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
                + field.name
            ),
            immutable,
        )


# ============================================================
# EXACT FIELDS
# ============================================================

snapshot_fields = tuple(
    field.name
    for field in fields(
        capability.UniversalWorkerCapabilitySnapshot
    )
)

match_fields = tuple(
    field.name
    for field in fields(
        capability.UniversalWorkerCapabilityMatchResult
    )
)


check(
    "snapshot_fields_exact",
    snapshot_fields
    == (
        "worker_id",
        "worker_instance_id",
        "worker_type",
        "capabilities",
        "schema_version",
    ),
    snapshot_fields,
)

check(
    "match_fields_exact",
    match_fields
    == (
        "worker_id",
        "worker_instance_id",
        "worker_type",
        "worker_capabilities",
        "required_capabilities",
        "missing_capabilities",
        "compatible",
        "schema_version",
    ),
    match_fields,
)


# ============================================================
# DETERMINISM
# ============================================================

snapshot_again = (
    capability.create_universal_worker_capability_snapshot(
        registration=reg,
        capabilities=(
            "article.validate",
            "semantic.read",
            "document.extract",
        ),
    )
)


check(
    "deterministic_snapshot",
    snapshot_again
    == snapshot,
)


match_again = (
    capability.match_universal_worker_capabilities(
        snapshot=snapshot_again,
        required_capabilities=(
            "article.validate",
            "semantic.read",
        ),
    )
)


check(
    "deterministic_match",
    match_again
    == compatible,
)


# ============================================================
# EXPLANATION CONTRACT
# ============================================================

explanation = (
    capability.explain_universal_worker_capability_v1()
)


check(
    "phase",
    explanation.get(
        "phase"
    )
    == "4.1.13",
)

check(
    "component",
    explanation.get(
        "component"
    )
    == "Universal Worker Capability Management",
)

check(
    "worker_type_separate",
    "does not itself imply capabilities"
    in explanation.get(
        "worker_type_rule",
        "",
    ),
)

check(
    "generic_tokens",
    "generic normalized"
    in explanation.get(
        "capability_rule",
        "",
    ),
)

check(
    "empty_worker_valid",
    "zero capabilities"
    in explanation.get(
        "empty_snapshot_rule",
        "",
    ),
)

check(
    "all_required",
    "ALL-required"
    in explanation.get(
        "matching_rule",
        "",
    ),
)

check(
    "empty_requirement",
    "therefore compatible"
    in explanation.get(
        "empty_requirement_rule",
        "",
    ),
)

check(
    "assignment_external",
    "does not assign workers"
    in explanation.get(
        "assignment_boundary",
        "",
    ),
)

check(
    "capacity_external",
    "separate"
    in explanation.get(
        "capacity_boundary",
        "",
    ),
)

check(
    "runtime_capability_external",
    "separate"
    in explanation.get(
        "runtime_capability_boundary",
        "",
    ),
)

check(
    "service_registry_external",
    "runtime services"
    in explanation.get(
        "service_registry_boundary",
        "",
    ),
)

check(
    "runtime_registration_external",
    "job_type-to-handler"
    in explanation.get(
        "runtime_registration_boundary",
        "",
    ),
)

check(
    "supported_job_types_external",
    "do not define individual-worker"
    in explanation.get(
        "supported_job_type_boundary",
        "",
    ),
)

check(
    "execution_external",
    "does not dispatch or execute jobs"
    in explanation.get(
        "execution_boundary",
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


# ============================================================
# PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not mutate Worker Registration",
    "does not infer capabilities from worker_type",
    "does not infer capabilities from Worker Pool membership",
    "does not inspect Worker Health",
    "does not inspect Stale Worker Detection",
    "does not inspect Worker Drain",
    "does not calculate Worker Capacity",
    "does not perform Worker Assignment",
    "does not acquire worker leases",
    "does not renew worker leases",
    "does not release worker leases",
    "does not perform Worker Scaling",
    "does not perform Worker Shutdown",
    "does not initiate Worker Recovery",
    "does not register runtime handlers",
    "does not unregister runtime handlers",
    "does not dispatch runtime handlers",
    "does not duplicate Runtime Capability Negotiation",
    "does not register Runtime Service Registry services",
    "does not use supported_job_types as worker capabilities",
    "does not route queue jobs",
    "does not access Queue Infrastructure",
    "does not access orchestration",
    "does not access Runtime State Store",
    "does not persist capability state",
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

source = CAPABILITY_PATH.read_text(
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
    "UNIVERSAL_WORKER_CAPABILITY_VERSION",
    "UNIVERSAL_WORKER_CAPABILITY_SNAPSHOT_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_CAPABILITY_MATCH_SCHEMA_VERSION",
    "MIN_UNIVERSAL_WORKER_CAPABILITY_LENGTH",
    "MAX_UNIVERSAL_WORKER_CAPABILITY_LENGTH",
    "MAX_UNIVERSAL_WORKER_CAPABILITIES",
    "UNIVERSAL_WORKER_CAPABILITY_IDENTITY_SEPARATOR",
    "UniversalWorkerCapabilityError",
    "UniversalWorkerCapabilitySnapshot",
    "UniversalWorkerCapabilityMatchResult",
    "normalize_universal_worker_capability",
    "normalize_universal_worker_capabilities",
    "create_universal_worker_capability_snapshot",
    "supports_universal_worker_capability",
    "match_universal_worker_capabilities",
    "explain_universal_worker_capability_v1",
)


check(
    "api_surface_exact",
    tuple(
        capability.__all__
    )
    == expected_all,
    capability.__all__,
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

    "add_universal_worker_pool_member",
    "remove_universal_worker_pool_member",

    "register_runtime_handler",
    "unregister_runtime_handler",
    "dispatch_registered_runtime_handler",

    "register_runtime_capability_manifest",
    "get_runtime_capability_registry",

    "register",
    "unregister",

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


capability_ast = ast_sha(
    CAPABILITY_PATH
)


check(
    "worker_capability_ast_generated",
    len(
        capability_ast
    )
    == 64,
    capability_ast,
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
        "PHASE 4.1.13 — UNIVERSAL WORKER "
        "CAPABILITY MANAGEMENT INITIAL IMPLEMENTATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER CAPABILITY AST SHA256: "
        + capability_ast
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
            "INITIAL WORKER CAPABILITY RESULT: "
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
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "RUNTIME LIFECYCLE MANAGER MODIFIED: NO",
        "RUNTIME SHUTDOWN PROCESS MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "WORKER REGISTRATION MUTATED: NO",
        "WORKER TYPE USED AS IMPLIED CAPABILITY: NO",
        "WORKER POOL USED AS IMPLIED CAPABILITY: NO",
        "WORKER HEALTH INSPECTED: NO",
        "STALE WORKER DETECTION INSPECTED: NO",
        "WORKER DRAIN INSPECTED: NO",
        "WORKER CAPACITY CALCULATED: NO",
        "WORKER ASSIGNMENT PERFORMED: NO",
        "WORKER LEASE MUTATED: NO",
        "WORKER SCALING PERFORMED: NO",
        "WORKER SHUTDOWN PERFORMED: NO",
        "WORKER RECOVERY INITIATED: NO",
        "RUNTIME HANDLER REGISTERED/DISPATCHED: NO",
        "RUNTIME CAPABILITY NEGOTIATION MUTATED: NO",
        "RUNTIME SERVICE REGISTRY MUTATED: NO",
        "SUPPORTED_JOB_TYPES USED AS WORKER CAPABILITIES: NO",
        "QUEUE INFRASTRUCTURE ACCESSED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "CAPABILITY STATE PERSISTED: NO",
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
        "Phase 4.1.13 Worker Capability initial implementation failed."
    )
