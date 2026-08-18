from __future__ import annotations

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
