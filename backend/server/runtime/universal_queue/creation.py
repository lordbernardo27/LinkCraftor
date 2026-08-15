from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


UNIVERSAL_QUEUE_CREATION_VERSION = (
    "universal_queue_creation_v3.1.1"
)

UNIVERSAL_QUEUE_DEFINITION_SCHEMA_VERSION = (
    "universal_queue_definition_schema_v1"
)

UNIVERSAL_DEFAULT_QUEUE_ID = "uq_default"
UNIVERSAL_DEFAULT_QUEUE_NAME = "default"

MAX_UNIVERSAL_QUEUE_ID_LENGTH = 128
MAX_UNIVERSAL_QUEUE_NAME_LENGTH = 128
MAX_UNIVERSAL_QUEUE_DESCRIPTION_LENGTH = 1024


class UniversalQueueCreationError(
    ValueError
):
    """Raised when a Universal Queue definition is invalid."""

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
        raise UniversalQueueCreationError(
            (
                f"{field_name} must be a string."
            ),
            code=(
                "invalid_"
                + field_name
                + "_type"
            ),
            value=value,
        )

    normalized = (
        value.strip()
    )

    if not normalized:
        raise UniversalQueueCreationError(
            (
                f"{field_name} must not be blank."
            ),
            code=(
                "blank_"
                + field_name
            ),
            value=value,
        )

    if (
        len(
            normalized
        )
        > maximum_length
    ):
        raise UniversalQueueCreationError(
            (
                f"{field_name} must not exceed "
                f"{maximum_length} characters."
            ),
            code=(
                field_name
                + "_too_long"
            ),
            value=value,
        )

    return normalized


def normalize_universal_queue_id(
    value: Any,
) -> str:

    normalized = (
        _normalize_required_text(
            value,
            field_name="queue_id",
            maximum_length=(
                MAX_UNIVERSAL_QUEUE_ID_LENGTH
            ),
        )
    )

    if not normalized.startswith(
        "uq_"
    ):
        raise UniversalQueueCreationError(
            (
                "queue_id must begin with 'uq_'."
            ),
            code="invalid_queue_id_prefix",
            value=value,
        )

    suffix = (
        normalized[
            3:
        ]
    )

    if not suffix:
        raise UniversalQueueCreationError(
            "queue_id requires a suffix.",
            code="invalid_queue_id",
            value=value,
        )

    for character in suffix:

        if not (
            character.islower()
            or character.isdigit()
            or character == "_"
        ):
            raise UniversalQueueCreationError(
                (
                    "queue_id suffix may contain only "
                    "lowercase letters, digits and underscores."
                ),
                code="invalid_queue_id",
                value=value,
            )

    return normalized


def normalize_universal_queue_name(
    value: Any,
) -> str:

    normalized = (
        _normalize_required_text(
            value,
            field_name="queue_name",
            maximum_length=(
                MAX_UNIVERSAL_QUEUE_NAME_LENGTH
            ),
        )
    )

    for character in normalized:

        if not (
            character.islower()
            or character.isdigit()
            or character in {
                "_",
                "-",
            }
        ):
            raise UniversalQueueCreationError(
                (
                    "queue_name may contain only lowercase "
                    "letters, digits, underscores and hyphens."
                ),
                code="invalid_queue_name",
                value=value,
            )

    return normalized


def normalize_universal_queue_description(
    value: Any,
) -> str:

    if value is None:
        return ""

    if not isinstance(
        value,
        str,
    ):
        raise UniversalQueueCreationError(
            "description must be a string or None.",
            code="invalid_description_type",
            value=value,
        )

    normalized = (
        value.strip()
    )

    if (
        len(
            normalized
        )
        > MAX_UNIVERSAL_QUEUE_DESCRIPTION_LENGTH
    ):
        raise UniversalQueueCreationError(
            (
                "description must not exceed "
                f"{MAX_UNIVERSAL_QUEUE_DESCRIPTION_LENGTH} "
                "characters."
            ),
            code="description_too_long",
            value=value,
        )

    return normalized


def normalize_universal_queue_enabled(
    value: Any,
) -> bool:

    if not isinstance(
        value,
        bool,
    ):
        raise UniversalQueueCreationError(
            "enabled must be a bool.",
            code="invalid_enabled_type",
            value=value,
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueDefinition:
    """
    Immutable logical Universal Queue definition.

    This object defines queue identity only. It does not create a
    physical backing queue and does not enqueue or dequeue jobs.
    """

    queue_id: str
    queue_name: str
    description: str = ""
    enabled: bool = True
    schema_version: str = (
        UNIVERSAL_QUEUE_DEFINITION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = (
            object.__setattr__
        )

        set_(
            self,
            "queue_id",
            normalize_universal_queue_id(
                self.queue_id
            ),
        )

        set_(
            self,
            "queue_name",
            normalize_universal_queue_name(
                self.queue_name
            ),
        )

        set_(
            self,
            "description",
            normalize_universal_queue_description(
                self.description
            ),
        )

        set_(
            self,
            "enabled",
            normalize_universal_queue_enabled(
                self.enabled
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_DEFINITION_SCHEMA_VERSION
        ):
            raise UniversalQueueCreationError(
                (
                    "schema_version must be "
                    + UNIVERSAL_QUEUE_DEFINITION_SCHEMA_VERSION
                    + "."
                ),
                code="invalid_schema_version",
                value=self.schema_version,
            )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "queue_id":
                self.queue_id,

            "queue_name":
                self.queue_name,

            "description":
                self.description,

            "enabled":
                self.enabled,
        }


def create_universal_queue_definition(
    *,
    queue_id: str = UNIVERSAL_DEFAULT_QUEUE_ID,
    queue_name: str = UNIVERSAL_DEFAULT_QUEUE_NAME,
    description: str | None = None,
    enabled: bool = True,
) -> UniversalQueueDefinition:
    """
    Create one logical Universal Queue definition.

    No filesystem, database, network, queue-store or orchestration
    operation is performed.
    """

    return UniversalQueueDefinition(
        queue_id=queue_id,
        queue_name=queue_name,
        description=(
            ""
            if description is None
            else description
        ),
        enabled=enabled,
    )


def create_default_universal_queue_definition(
) -> UniversalQueueDefinition:

    return create_universal_queue_definition(
        queue_id=(
            UNIVERSAL_DEFAULT_QUEUE_ID
        ),
        queue_name=(
            UNIVERSAL_DEFAULT_QUEUE_NAME
        ),
        description=(
            "Default LinkCraftor Universal Runtime queue."
        ),
        enabled=True,
    )


def is_canonical_universal_queue_definition(
    value: Any,
) -> bool:

    if not isinstance(
        value,
        UniversalQueueDefinition,
    ):
        return False

    try:
        canonical = (
            UniversalQueueDefinition(
                queue_id=value.queue_id,
                queue_name=value.queue_name,
                description=value.description,
                enabled=value.enabled,
                schema_version=value.schema_version,
            )
        )

    except UniversalQueueCreationError:
        return False

    return (
        canonical
        == value
    )


def explain_universal_queue_creation_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "3.1.1",

            "component":
                "Universal Queue Creation",

            "version":
                UNIVERSAL_QUEUE_CREATION_VERSION,

            "schema_version":
                UNIVERSAL_QUEUE_DEFINITION_SCHEMA_VERSION,

            "scope":
                "LinkCraftor-wide",

            "canonical_operation":
                "create_universal_queue_definition",

            "default_queue_id":
                UNIVERSAL_DEFAULT_QUEUE_ID,

            "default_queue_name":
                UNIVERSAL_DEFAULT_QUEUE_NAME,

            "queue_model":
                (
                    "logical queue definition; physical "
                    "queue backend is not created here"
                ),

            "relationship_to_current_orchestration":
                (
                    "existing orchestration queue currently "
                    "derives queue membership from persisted "
                    "QUEUED job status; Phase 3.1.1 does not "
                    "modify that behavior"
                ),

            "future_extension_boundary": (
                "routing and partitioning may introduce "
                "additional queue definitions without "
                "changing Queue Creation semantics"
            ),

            "prohibitions": (
                "does not create Universal Jobs",
                "does not persist jobs",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not schedule jobs",
                "does not prioritize jobs",
                "does not route jobs",
                "does not balance queues",
                "does not partition queues",
                "does not lease jobs",
                "does not start workers",
                "does not retry jobs",
                "does not create dead-letter queues",
                "does not apply backpressure",
                "does not enforce queue capacity",
                "does not enforce queue fairness",
                "does not rate-limit queues",
                "does not deduplicate queued jobs",
                "does not create filesystem directories",
                "does not create database tables",
                "does not create Redis queues",
                "does not create cloud queues",
                "does not access orchestration",
                "does not access the job store",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_QUEUE_CREATION_VERSION",
    "UNIVERSAL_QUEUE_DEFINITION_SCHEMA_VERSION",
    "UNIVERSAL_DEFAULT_QUEUE_ID",
    "UNIVERSAL_DEFAULT_QUEUE_NAME",
    "MAX_UNIVERSAL_QUEUE_ID_LENGTH",
    "MAX_UNIVERSAL_QUEUE_NAME_LENGTH",
    "MAX_UNIVERSAL_QUEUE_DESCRIPTION_LENGTH",
    "UniversalQueueCreationError",
    "UniversalQueueDefinition",
    "normalize_universal_queue_id",
    "normalize_universal_queue_name",
    "normalize_universal_queue_description",
    "normalize_universal_queue_enabled",
    "create_universal_queue_definition",
    "create_default_universal_queue_definition",
    "is_canonical_universal_queue_definition",
    "explain_universal_queue_creation_v1",
]
