from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping


UNIVERSAL_WORKER_REGISTRATION_VERSION = (
    "universal_worker_registration_v4.1.1"
)

UNIVERSAL_WORKER_REGISTRATION_SCHEMA_VERSION = (
    "universal_worker_registration_schema_v1"
)

MAX_UNIVERSAL_WORKER_ID_LENGTH = 160
MAX_UNIVERSAL_WORKER_TYPE_LENGTH = 120
MAX_UNIVERSAL_WORKER_INSTANCE_ID_LENGTH = 200
MAX_UNIVERSAL_WORKER_RUNTIME_VERSION_LENGTH = 120
MAX_UNIVERSAL_WORKER_HOST_ID_LENGTH = 200


class UniversalWorkerRegistrationError(
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


def _normalize_required_text(
    value: Any,
    *,
    field_name: str,
    maximum_length: int,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalWorkerRegistrationError(
            f"{field_name} must be a string.",
            code=f"invalid_{field_name}_type",
            value=value,
        )

    normalized = value.strip()

    if not normalized:

        raise UniversalWorkerRegistrationError(
            f"{field_name} must not be empty.",
            code=f"empty_{field_name}",
            value=value,
        )

    if len(normalized) > maximum_length:

        raise UniversalWorkerRegistrationError(
            (
                f"{field_name} exceeds maximum length "
                f"{maximum_length}."
            ),
            code=f"{field_name}_too_long",
            value=value,
        )

    return normalized


def normalize_universal_worker_id(
    value: Any,
) -> str:

    return _normalize_required_text(
        value,
        field_name="worker_id",
        maximum_length=MAX_UNIVERSAL_WORKER_ID_LENGTH,
    )


def normalize_universal_worker_type(
    value: Any,
) -> str:

    return _normalize_required_text(
        value,
        field_name="worker_type",
        maximum_length=MAX_UNIVERSAL_WORKER_TYPE_LENGTH,
    )


def normalize_universal_worker_instance_id(
    value: Any,
) -> str:

    return _normalize_required_text(
        value,
        field_name="worker_instance_id",
        maximum_length=(
            MAX_UNIVERSAL_WORKER_INSTANCE_ID_LENGTH
        ),
    )


def normalize_universal_worker_runtime_version(
    value: Any,
) -> str:

    return _normalize_required_text(
        value,
        field_name="runtime_version",
        maximum_length=(
            MAX_UNIVERSAL_WORKER_RUNTIME_VERSION_LENGTH
        ),
    )


def normalize_universal_worker_host_id(
    value: Any,
) -> str:

    return _normalize_required_text(
        value,
        field_name="host_id",
        maximum_length=MAX_UNIVERSAL_WORKER_HOST_ID_LENGTH,
    )


def normalize_universal_worker_registered_at(
    value: Any,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalWorkerRegistrationError(
            "registered_at must be a string.",
            code="invalid_registered_at_type",
            value=value,
        )

    text = value.strip()

    if not text:

        raise UniversalWorkerRegistrationError(
            "registered_at must not be empty.",
            code="empty_registered_at",
            value=value,
        )

    parse_value = text

    if parse_value.endswith("Z"):

        parse_value = (
            parse_value[:-1]
            + "+00:00"
        )

    try:

        parsed = datetime.fromisoformat(
            parse_value
        )

    except ValueError as exc:

        raise UniversalWorkerRegistrationError(
            (
                "registered_at must be a valid "
                "ISO-8601 timestamp."
            ),
            code="invalid_registered_at",
            value=value,
        ) from exc

    if parsed.tzinfo is None:

        raise UniversalWorkerRegistrationError(
            (
                "registered_at must include "
                "timezone information."
            ),
            code="registered_at_timezone_required",
            value=value,
        )

    canonical = parsed.astimezone(
        timezone.utc
    )

    return (
        canonical.isoformat(
            timespec="microseconds"
        )
        .replace(
            "+00:00",
            "Z",
        )
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerRegistration:

    worker_id: str
    worker_type: str
    worker_instance_id: str
    runtime_version: str
    host_id: str
    registered_at: str

    schema_version: str = (
        UNIVERSAL_WORKER_REGISTRATION_SCHEMA_VERSION
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
            "worker_type",
            normalize_universal_worker_type(
                self.worker_type
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
            "runtime_version",
            normalize_universal_worker_runtime_version(
                self.runtime_version
            ),
        )

        object.__setattr__(
            self,
            "host_id",
            normalize_universal_worker_host_id(
                self.host_id
            ),
        )

        object.__setattr__(
            self,
            "registered_at",
            normalize_universal_worker_registered_at(
                self.registered_at
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_REGISTRATION_SCHEMA_VERSION
        ):

            raise UniversalWorkerRegistrationError(
                (
                    "Invalid Worker Registration "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_registration_"
                    "schema_version"
                ),
                value=self.schema_version,
            )

    @property
    def canonical_identity(
        self,
    ) -> tuple[str, str]:

        return (
            self.worker_id,
            self.worker_instance_id,
        )

    def to_dict(
        self,
    ) -> dict[str, str]:

        return {
            "schema_version":
                self.schema_version,

            "worker_id":
                self.worker_id,

            "worker_type":
                self.worker_type,

            "worker_instance_id":
                self.worker_instance_id,

            "runtime_version":
                self.runtime_version,

            "host_id":
                self.host_id,

            "registered_at":
                self.registered_at,
        }


def create_universal_worker_registration(
    *,
    worker_id: str,
    worker_type: str,
    worker_instance_id: str,
    runtime_version: str,
    host_id: str,
    registered_at: str,
) -> UniversalWorkerRegistration:

    return UniversalWorkerRegistration(
        worker_id=worker_id,
        worker_type=worker_type,
        worker_instance_id=worker_instance_id,
        runtime_version=runtime_version,
        host_id=host_id,
        registered_at=registered_at,
    )


def is_same_universal_worker_registration_identity(
    *,
    left: UniversalWorkerRegistration,
    right: UniversalWorkerRegistration,
) -> bool:

    if not isinstance(
        left,
        UniversalWorkerRegistration,
    ):

        raise UniversalWorkerRegistrationError(
            (
                "left must be a "
                "UniversalWorkerRegistration."
            ),
            code="invalid_left_worker_registration",
            value=left,
        )

    if not isinstance(
        right,
        UniversalWorkerRegistration,
    ):

        raise UniversalWorkerRegistrationError(
            (
                "right must be a "
                "UniversalWorkerRegistration."
            ),
            code="invalid_right_worker_registration",
            value=right,
        )

    return (
        left.canonical_identity
        == right.canonical_identity
    )


def explain_universal_worker_registration_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.1",

            "component":
                "Universal Worker Registration",

            "version":
                UNIVERSAL_WORKER_REGISTRATION_VERSION,

            "schema_version":
                UNIVERSAL_WORKER_REGISTRATION_SCHEMA_VERSION,

            "canonical_identity": (
                "worker_id",
                "worker_instance_id",
            ),

            "identity_semantics": (
                "worker_id identifies the logical worker; "
                "worker_instance_id identifies one concrete "
                "running instance of that logical worker"
            ),

            "owned_fields": (
                "worker_id",
                "worker_type",
                "worker_instance_id",
                "runtime_version",
                "host_id",
                "registered_at",
            ),

            "registered_at_rule": (
                "registered_at is caller-supplied registration "
                "evidence and is normalized to canonical UTC"
            ),

            "immutability_rule": (
                "a Worker Registration record is immutable"
            ),

            "purity_rule": (
                "4.1.1 validates and represents registration "
                "evidence only; it does not persist, discover, "
                "assign, lease, heartbeat or execute workers"
            ),

            "prohibitions": (
                "does not create worker pools",
                "does not declare worker capabilities",
                "does not determine worker health",
                "does not determine worker availability",
                "does not determine worker capacity",
                "does not assign jobs",
                "does not claim jobs",
                "does not lease jobs",
                "does not renew leases",
                "does not release leases",
                "does not emit heartbeats",
                "does not detect stale workers",
                "does not recover workers",
                "does not scale workers",
                "does not drain workers",
                "does not shut down workers",
                "does not dispatch jobs",
                "does not execute jobs",
                "does not register runtime handlers",
                "does not access orchestration",
                "does not access Runtime State Store",
                "does not mutate Queue Infrastructure",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_REGISTRATION_VERSION",
    "UNIVERSAL_WORKER_REGISTRATION_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_ID_LENGTH",
    "MAX_UNIVERSAL_WORKER_TYPE_LENGTH",
    "MAX_UNIVERSAL_WORKER_INSTANCE_ID_LENGTH",
    "MAX_UNIVERSAL_WORKER_RUNTIME_VERSION_LENGTH",
    "MAX_UNIVERSAL_WORKER_HOST_ID_LENGTH",
    "UniversalWorkerRegistrationError",
    "UniversalWorkerRegistration",
    "normalize_universal_worker_id",
    "normalize_universal_worker_type",
    "normalize_universal_worker_instance_id",
    "normalize_universal_worker_runtime_version",
    "normalize_universal_worker_host_id",
    "normalize_universal_worker_registered_at",
    "create_universal_worker_registration",
    "is_same_universal_worker_registration_identity",
    "explain_universal_worker_registration_v1",
]
