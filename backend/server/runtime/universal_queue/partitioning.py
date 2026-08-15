from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.universal_queue.creation import (
    UniversalQueueCreationError,
    normalize_universal_queue_id,
)


UNIVERSAL_QUEUE_PARTITIONING_VERSION = (
    "universal_queue_partitioning_v3.1.6"
)

UNIVERSAL_QUEUE_PARTITION_DECISION_SCHEMA_VERSION = (
    "universal_queue_partition_decision_schema_v1"
)

UNIVERSAL_QUEUE_PARTITION_ALGORITHM = (
    "sha256_mod_v1"
)


class UniversalQueuePartitioningError(
    ValueError
):
    """
    Raised when Universal Queue partitioning input is invalid.
    """

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
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise UniversalQueuePartitioningError(
            f"{field_name} must be a string.",
            code=(
                "invalid_"
                + field_name
                + "_type"
            ),
            value=value,
        )

    normalized = value.strip()

    if not normalized:

        raise UniversalQueuePartitioningError(
            f"{field_name} must not be blank.",
            code=(
                "blank_"
                + field_name
            ),
            value=value,
        )

    return normalized


def normalize_universal_queue_partition_queue_id(
    value: Any,
) -> str:

    try:
        return normalize_universal_queue_id(
            value
        )

    except UniversalQueueCreationError as exc:

        raise UniversalQueuePartitioningError(
            "Invalid canonical Universal Queue queue_id.",
            code="invalid_partition_queue_id",
            value=value,
        ) from exc


def normalize_universal_queue_partition_workspace_id(
    value: Any,
) -> str:

    return _normalize_required_text(
        value,
        field_name="workspace_id",
    )


def normalize_universal_queue_partition_count(
    value: Any,
) -> int:
    """
    Partition count is explicit queue topology input.

    Capacity policy is deliberately not imposed here.
    """

    if isinstance(
        value,
        bool,
    ):
        raise UniversalQueuePartitioningError(
            "partition_count must be an integer >= 1.",
            code="invalid_partition_count_type",
            value=value,
        )

    if not isinstance(
        value,
        int,
    ):
        raise UniversalQueuePartitioningError(
            "partition_count must be an integer >= 1.",
            code="invalid_partition_count_type",
            value=value,
        )

    if value < 1:

        raise UniversalQueuePartitioningError(
            "partition_count must be >= 1.",
            code="invalid_partition_count",
            value=value,
        )

    return value


def canonical_universal_queue_partition_material(
    *,
    queue_id: str,
    workspace_id: str,
) -> bytes:
    """
    Return the canonical bytes hashed by sha256_mod_v1.

    JSON array encoding prevents ambiguous delimiter parsing.
    """

    normalized_queue_id = (
        normalize_universal_queue_partition_queue_id(
            queue_id
        )
    )

    normalized_workspace_id = (
        normalize_universal_queue_partition_workspace_id(
            workspace_id
        )
    )

    canonical = json.dumps(
        [
            normalized_queue_id,
            normalized_workspace_id,
        ],
        ensure_ascii=False,
        separators=(
            ",",
            ":",
        ),
    )

    return canonical.encode(
        "utf-8"
    )


def universal_queue_partition_digest(
    *,
    queue_id: str,
    workspace_id: str,
) -> str:

    material = (
        canonical_universal_queue_partition_material(
            queue_id=queue_id,
            workspace_id=workspace_id,
        )
    )

    return hashlib.sha256(
        material
    ).hexdigest()


def universal_queue_partition_index(
    *,
    queue_id: str,
    workspace_id: str,
    partition_count: int,
) -> int:

    normalized_count = (
        normalize_universal_queue_partition_count(
            partition_count
        )
    )

    digest = universal_queue_partition_digest(
        queue_id=queue_id,
        workspace_id=workspace_id,
    )

    return (
        int(
            digest,
            16,
        )
        % normalized_count
    )


def create_universal_queue_partition_id(
    *,
    queue_id: str,
    partition_index: int,
) -> str:

    normalized_queue_id = (
        normalize_universal_queue_partition_queue_id(
            queue_id
        )
    )

    if (
        isinstance(
            partition_index,
            bool,
        )
        or not isinstance(
            partition_index,
            int,
        )
        or partition_index < 0
    ):
        raise UniversalQueuePartitioningError(
            "partition_index must be a non-negative integer.",
            code="invalid_partition_index",
            value=partition_index,
        )

    return (
        normalized_queue_id
        + "__p"
        + str(
            partition_index
        ).zfill(
            8
        )
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueuePartitionDecision:
    """
    Immutable logical queue-partition decision.

    This does not represent a physical broker shard.
    """

    queue_id: str
    workspace_id: str
    partition_count: int
    partition_index: int
    partition_id: str
    partition_digest: str
    algorithm: str = (
        UNIVERSAL_QUEUE_PARTITION_ALGORITHM
    )
    schema_version: str = (
        UNIVERSAL_QUEUE_PARTITION_DECISION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        normalized_queue_id = (
            normalize_universal_queue_partition_queue_id(
                self.queue_id
            )
        )

        normalized_workspace_id = (
            normalize_universal_queue_partition_workspace_id(
                self.workspace_id
            )
        )

        normalized_count = (
            normalize_universal_queue_partition_count(
                self.partition_count
            )
        )

        if (
            isinstance(
                self.partition_index,
                bool,
            )
            or not isinstance(
                self.partition_index,
                int,
            )
            or self.partition_index < 0
            or self.partition_index >= normalized_count
        ):
            raise UniversalQueuePartitioningError(
                (
                    "partition_index must satisfy "
                    "0 <= partition_index < partition_count."
                ),
                code="invalid_partition_index",
                value=self.partition_index,
            )

        expected_partition_id = (
            create_universal_queue_partition_id(
                queue_id=normalized_queue_id,
                partition_index=self.partition_index,
            )
        )

        if self.partition_id != expected_partition_id:

            raise UniversalQueuePartitioningError(
                "partition_id is inconsistent with queue_id and partition_index.",
                code="partition_id_mismatch",
                value=self.partition_id,
            )

        expected_digest = (
            universal_queue_partition_digest(
                queue_id=normalized_queue_id,
                workspace_id=normalized_workspace_id,
            )
        )

        if self.partition_digest != expected_digest:

            raise UniversalQueuePartitioningError(
                (
                    "partition_digest is inconsistent with "
                    "queue_id and workspace_id."
                ),
                code="partition_digest_mismatch",
                value=self.partition_digest,
            )

        if (
            self.algorithm
            != UNIVERSAL_QUEUE_PARTITION_ALGORITHM
        ):
            raise UniversalQueuePartitioningError(
                "Invalid queue partition algorithm.",
                code="invalid_partition_algorithm",
                value=self.algorithm,
            )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_PARTITION_DECISION_SCHEMA_VERSION
        ):
            raise UniversalQueuePartitioningError(
                "Invalid queue-partition decision schema_version.",
                code="invalid_partition_decision_schema_version",
                value=self.schema_version,
            )

        set_(
            self,
            "queue_id",
            normalized_queue_id,
        )

        set_(
            self,
            "workspace_id",
            normalized_workspace_id,
        )

        set_(
            self,
            "partition_count",
            normalized_count,
        )

    @property
    def partition_key(
        self,
    ) -> str:

        return self.workspace_id

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "algorithm":
                self.algorithm,

            "queue_id":
                self.queue_id,

            "workspace_id":
                self.workspace_id,

            "partition_key":
                self.partition_key,

            "partition_count":
                self.partition_count,

            "partition_index":
                self.partition_index,

            "partition_id":
                self.partition_id,

            "partition_digest":
                self.partition_digest,
        }


def partition_universal_queue(
    *,
    queue_id: str,
    workspace_id: str,
    partition_count: int,
) -> UniversalQueuePartitionDecision:
    """
    Deterministically select one logical partition.

    Canonical algorithm:
        SHA256(canonical [queue_id, workspace_id])
        MOD partition_count

    No live infrastructure state is consulted.
    """

    normalized_queue_id = (
        normalize_universal_queue_partition_queue_id(
            queue_id
        )
    )

    normalized_workspace_id = (
        normalize_universal_queue_partition_workspace_id(
            workspace_id
        )
    )

    normalized_count = (
        normalize_universal_queue_partition_count(
            partition_count
        )
    )

    digest = universal_queue_partition_digest(
        queue_id=normalized_queue_id,
        workspace_id=normalized_workspace_id,
    )

    partition_index = (
        int(
            digest,
            16,
        )
        % normalized_count
    )

    partition_id = (
        create_universal_queue_partition_id(
            queue_id=normalized_queue_id,
            partition_index=partition_index,
        )
    )

    return UniversalQueuePartitionDecision(
        queue_id=normalized_queue_id,
        workspace_id=normalized_workspace_id,
        partition_count=normalized_count,
        partition_index=partition_index,
        partition_id=partition_id,
        partition_digest=digest,
    )


def explain_universal_queue_partitioning_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "3.1.6",

            "component":
                "Universal Queue Partitioning",

            "version":
                UNIVERSAL_QUEUE_PARTITIONING_VERSION,

            "decision_schema":
                UNIVERSAL_QUEUE_PARTITION_DECISION_SCHEMA_VERSION,

            "scope":
                "LinkCraftor-wide",

            "partition_algorithm":
                UNIVERSAL_QUEUE_PARTITION_ALGORITHM,

            "canonical_partition_key":
                "workspace_id",

            "canonical_material":
                "[queue_id, workspace_id]",

            "selection_rule": (
                "SHA-256 of canonical queue_id + workspace_id "
                "material modulo partition_count"
            ),

            "stability_rule": (
                "identical queue_id, workspace_id and "
                "partition_count produce the same logical partition"
            ),

            "partition_count_rule": (
                "partition_count is explicit caller-supplied "
                "logical topology input"
            ),

            "logical_partition_rule": (
                "partition_id represents a logical Universal Queue "
                "partition and not a physical broker shard"
            ),

            "routing_relationship": (
                "3.1.4 selects a logical queue before partitioning"
            ),

            "balancing_relationship": (
                "3.1.5 may select among equivalent logical queues "
                "before 3.1.6 partitions the selected queue"
            ),

            "workspace_relationship": (
                "workspace_id supplies deterministic workspace "
                "affinity and isolation within a logical queue"
            ),

            "worker_boundary": (
                "worker assignment and worker capability remain "
                "owned by Worker Infrastructure"
            ),

            "capacity_boundary": (
                "capacity enforcement remains owned by "
                "3.1.11 Queue Capacity Limits"
            ),

            "fairness_boundary": (
                "fairness and starvation policy remain owned by "
                "3.1.12 Queue Fairness"
            ),

            "prohibitions": (
                "does not create Universal Queues",
                "does not create Universal Jobs",
                "does not mutate jobs",
                "does not mutate queues",
                "does not move jobs",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not read live queue state",
                "does not discover partition_count from infrastructure",
                "does not evaluate Queue Routing rules",
                "does not perform Queue Balancing",
                "does not select workers",
                "does not inspect worker capability",
                "does not enforce queue capacity",
                "does not apply backpressure",
                "does not implement queue fairness",
                "does not implement priority aging",
                "does not implement rate limiting",
                "does not implement queue deduplication",
                "does not create Kafka partitions",
                "does not create broker shards",
                "does not create Redis queues",
                "does not create cloud queues",
                "does not create filesystem directories",
                "does not access orchestration",
                "does not access the job store",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_QUEUE_PARTITIONING_VERSION",
    "UNIVERSAL_QUEUE_PARTITION_DECISION_SCHEMA_VERSION",
    "UNIVERSAL_QUEUE_PARTITION_ALGORITHM",
    "UniversalQueuePartitioningError",
    "UniversalQueuePartitionDecision",
    "normalize_universal_queue_partition_queue_id",
    "normalize_universal_queue_partition_workspace_id",
    "normalize_universal_queue_partition_count",
    "canonical_universal_queue_partition_material",
    "universal_queue_partition_digest",
    "universal_queue_partition_index",
    "create_universal_queue_partition_id",
    "partition_universal_queue",
    "explain_universal_queue_partitioning_v1",
]
