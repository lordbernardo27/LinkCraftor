from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from backend.server.runtime.universal_queue.creation import (
    UNIVERSAL_DEFAULT_QUEUE_ID,
    UniversalQueueCreationError,
    normalize_universal_queue_id,
)


UNIVERSAL_QUEUE_ROUTING_VERSION = (
    "universal_queue_routing_v3.1.4"
)

UNIVERSAL_QUEUE_ROUTE_RULE_SCHEMA_VERSION = (
    "universal_queue_route_rule_schema_v1"
)

UNIVERSAL_QUEUE_ROUTE_DECISION_SCHEMA_VERSION = (
    "universal_queue_route_decision_schema_v1"
)


class UniversalQueueRoutingError(
    ValueError
):
    """Raised when Universal Queue routing input is invalid."""

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
        raise UniversalQueueRoutingError(
            f"{field_name} must be a string.",
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

        raise UniversalQueueRoutingError(
            f"{field_name} must not be blank.",
            code=(
                "blank_"
                + field_name
            ),
            value=value,
        )

    return normalized


def _normalize_optional_text(
    value: Any,
    *,
    field_name: str,
) -> str | None:

    if value is None:
        return None

    return _normalize_required_text(
        value,
        field_name=field_name,
    )


def normalize_universal_queue_route_id(
    value: Any,
) -> str:

    normalized = (
        _normalize_required_text(
            value,
            field_name="route_id",
        )
    )

    if not normalized.startswith(
        "ur_"
    ):
        raise UniversalQueueRoutingError(
            "route_id must begin with 'ur_'.",
            code="invalid_route_id_prefix",
            value=value,
        )

    suffix = (
        normalized[3:]
    )

    if not suffix:

        raise UniversalQueueRoutingError(
            "route_id requires a suffix.",
            code="invalid_route_id",
            value=value,
        )

    for character in suffix:

        if not (
            character.isascii()
            and (
                character.islower()
                or character.isdigit()
                or character == "_"
            )
        ):
            raise UniversalQueueRoutingError(
                (
                    "route_id suffix may contain only "
                    "lowercase ASCII letters, digits "
                    "and underscores."
                ),
                code="invalid_route_id",
                value=value,
            )

    return normalized


def normalize_universal_queue_route_queue_id(
    value: Any,
) -> str:

    try:
        return normalize_universal_queue_id(
            value
        )

    except UniversalQueueCreationError as exc:

        raise UniversalQueueRoutingError(
            "Invalid canonical Universal Queue queue_id.",
            code="invalid_route_queue_id",
            value=value,
        ) from exc


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueRouteRule:
    """
    One immutable logical queue-routing rule.

    job_type is the primary selector.

    product_id, pipeline and stage are optional refinements.

    workspace_id is deliberately absent; workspace-level isolation
    belongs to Queue Partitioning rather than logical Queue Routing.
    """

    route_id: str
    queue_id: str
    job_type: str
    product_id: str | None = None
    pipeline: str | None = None
    stage: str | None = None
    enabled: bool = True
    schema_version: str = (
        UNIVERSAL_QUEUE_ROUTE_RULE_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        set_(
            self,
            "route_id",
            normalize_universal_queue_route_id(
                self.route_id
            ),
        )

        set_(
            self,
            "queue_id",
            normalize_universal_queue_route_queue_id(
                self.queue_id
            ),
        )

        set_(
            self,
            "job_type",
            _normalize_required_text(
                self.job_type,
                field_name="job_type",
            ),
        )

        set_(
            self,
            "product_id",
            _normalize_optional_text(
                self.product_id,
                field_name="product_id",
            ),
        )

        set_(
            self,
            "pipeline",
            _normalize_optional_text(
                self.pipeline,
                field_name="pipeline",
            ),
        )

        set_(
            self,
            "stage",
            _normalize_optional_text(
                self.stage,
                field_name="stage",
            ),
        )

        if not isinstance(
            self.enabled,
            bool,
        ):
            raise UniversalQueueRoutingError(
                "enabled must be bool.",
                code="invalid_route_enabled_type",
                value=self.enabled,
            )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_ROUTE_RULE_SCHEMA_VERSION
        ):
            raise UniversalQueueRoutingError(
                "Invalid route-rule schema_version.",
                code="invalid_route_rule_schema_version",
                value=self.schema_version,
            )

    @property
    def specificity(
        self,
    ) -> int:

        return (
            1
            + int(
                self.product_id
                is not None
            )
            + int(
                self.pipeline
                is not None
            )
            + int(
                self.stage
                is not None
            )
        )

    def matches(
        self,
        *,
        job_type: str,
        product_id: str | None,
        pipeline: str | None,
        stage: str | None,
    ) -> bool:

        if not self.enabled:
            return False

        if self.job_type != job_type:
            return False

        if (
            self.product_id
            is not None
            and self.product_id
            != product_id
        ):
            return False

        if (
            self.pipeline
            is not None
            and self.pipeline
            != pipeline
        ):
            return False

        if (
            self.stage
            is not None
            and self.stage
            != stage
        ):
            return False

        return True

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "route_id":
                self.route_id,

            "queue_id":
                self.queue_id,

            "job_type":
                self.job_type,

            "product_id":
                self.product_id,

            "pipeline":
                self.pipeline,

            "stage":
                self.stage,

            "enabled":
                self.enabled,

            "specificity":
                self.specificity,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueRouteDecision:
    """
    Immutable logical queue destination decision.
    """

    queue_id: str
    job_type: str
    product_id: str | None
    pipeline: str | None
    stage: str | None
    matched_route_id: str | None
    used_default: bool
    reason: str
    schema_version: str = (
        UNIVERSAL_QUEUE_ROUTE_DECISION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        set_ = object.__setattr__

        set_(
            self,
            "queue_id",
            normalize_universal_queue_route_queue_id(
                self.queue_id
            ),
        )

        set_(
            self,
            "job_type",
            _normalize_required_text(
                self.job_type,
                field_name="job_type",
            ),
        )

        set_(
            self,
            "product_id",
            _normalize_optional_text(
                self.product_id,
                field_name="product_id",
            ),
        )

        set_(
            self,
            "pipeline",
            _normalize_optional_text(
                self.pipeline,
                field_name="pipeline",
            ),
        )

        set_(
            self,
            "stage",
            _normalize_optional_text(
                self.stage,
                field_name="stage",
            ),
        )

        if self.matched_route_id is not None:

            set_(
                self,
                "matched_route_id",
                normalize_universal_queue_route_id(
                    self.matched_route_id
                ),
            )

        if not isinstance(
            self.used_default,
            bool,
        ):
            raise UniversalQueueRoutingError(
                "used_default must be bool.",
                code="invalid_used_default_type",
                value=self.used_default,
            )

        reason = _normalize_required_text(
            self.reason,
            field_name="reason",
        )

        set_(
            self,
            "reason",
            reason,
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_ROUTE_DECISION_SCHEMA_VERSION
        ):
            raise UniversalQueueRoutingError(
                "Invalid route-decision schema_version.",
                code="invalid_route_decision_schema_version",
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

            "job_type":
                self.job_type,

            "product_id":
                self.product_id,

            "pipeline":
                self.pipeline,

            "stage":
                self.stage,

            "matched_route_id":
                self.matched_route_id,

            "used_default":
                self.used_default,

            "reason":
                self.reason,
        }


def create_universal_queue_route_rule(
    *,
    route_id: str,
    queue_id: str,
    job_type: str,
    product_id: str | None = None,
    pipeline: str | None = None,
    stage: str | None = None,
    enabled: bool = True,
) -> UniversalQueueRouteRule:

    return UniversalQueueRouteRule(
        route_id=route_id,
        queue_id=queue_id,
        job_type=job_type,
        product_id=product_id,
        pipeline=pipeline,
        stage=stage,
        enabled=enabled,
    )


def route_universal_queue(
    *,
    job_type: str,
    product_id: str | None = None,
    pipeline: str | None = None,
    stage: str | None = None,
    rules: Iterable[
        UniversalQueueRouteRule
    ] = (),
    default_queue_id: str = (
        UNIVERSAL_DEFAULT_QUEUE_ID
    ),
) -> UniversalQueueRouteDecision:
    """
    Return one logical queue destination.

    No enqueue, persistence, partitioning, balancing, worker
    selection or handler dispatch occurs here.
    """

    normalized_job_type = (
        _normalize_required_text(
            job_type,
            field_name="job_type",
        )
    )

    normalized_product_id = (
        _normalize_optional_text(
            product_id,
            field_name="product_id",
        )
    )

    normalized_pipeline = (
        _normalize_optional_text(
            pipeline,
            field_name="pipeline",
        )
    )

    normalized_stage = (
        _normalize_optional_text(
            stage,
            field_name="stage",
        )
    )

    normalized_default_queue_id = (
        normalize_universal_queue_route_queue_id(
            default_queue_id
        )
    )

    if isinstance(
        rules,
        (
            str,
            bytes,
            bytearray,
        ),
    ):
        raise UniversalQueueRoutingError(
            "rules must be an iterable of route rules.",
            code="invalid_route_rule_collection",
            value=rules,
        )

    try:
        materialized = tuple(
            rules
        )

    except TypeError as exc:

        raise UniversalQueueRoutingError(
            "rules must be iterable.",
            code="invalid_route_rule_collection",
            value=rules,
        ) from exc

    for rule in materialized:

        if not isinstance(
            rule,
            UniversalQueueRouteRule,
        ):
            raise UniversalQueueRoutingError(
                (
                    "rules must contain only "
                    "UniversalQueueRouteRule members."
                ),
                code="invalid_route_rule_member",
                value=rule,
            )

    matches = tuple(
        rule
        for rule in materialized
        if rule.matches(
            job_type=normalized_job_type,
            product_id=normalized_product_id,
            pipeline=normalized_pipeline,
            stage=normalized_stage,
        )
    )

    if not matches:

        return UniversalQueueRouteDecision(
            queue_id=normalized_default_queue_id,
            job_type=normalized_job_type,
            product_id=normalized_product_id,
            pipeline=normalized_pipeline,
            stage=normalized_stage,
            matched_route_id=None,
            used_default=True,
            reason="default_route",
        )

    highest_specificity = max(
        rule.specificity
        for rule in matches
    )

    strongest = tuple(
        rule
        for rule in matches
        if rule.specificity
        == highest_specificity
    )

    if len(
        strongest
    ) != 1:

        raise UniversalQueueRoutingError(
            (
                "Ambiguous Universal Queue route: "
                "multiple equally specific rules matched."
            ),
            code="ambiguous_queue_route",
            value=tuple(
                rule.route_id
                for rule in strongest
            ),
        )

    selected = (
        strongest[0]
    )

    return UniversalQueueRouteDecision(
        queue_id=selected.queue_id,
        job_type=normalized_job_type,
        product_id=normalized_product_id,
        pipeline=normalized_pipeline,
        stage=normalized_stage,
        matched_route_id=selected.route_id,
        used_default=False,
        reason="matched_route_rule",
    )


def explain_universal_queue_routing_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "3.1.4",

            "component":
                "Universal Queue Routing",

            "version":
                UNIVERSAL_QUEUE_ROUTING_VERSION,

            "rule_schema":
                UNIVERSAL_QUEUE_ROUTE_RULE_SCHEMA_VERSION,

            "decision_schema":
                UNIVERSAL_QUEUE_ROUTE_DECISION_SCHEMA_VERSION,

            "scope":
                "LinkCraftor-wide",

            "default_queue_id":
                UNIVERSAL_DEFAULT_QUEUE_ID,

            "primary_selector":
                "job_type",

            "optional_route_constraints": (
                "product_id",
                "pipeline",
                "stage",
            ),

            "selection_rule": (
                "choose the single most-specific enabled "
                "matching route rule"
            ),

            "ambiguity_rule": (
                "multiple equally specific matching rules "
                "are rejected"
            ),

            "fallback_rule": (
                "no matching route rule selects uq_default"
            ),

            "workspace_boundary": (
                "workspace_id does not select the logical "
                "queue in 3.1.4; workspace isolation belongs "
                "to Queue Partitioning"
            ),

            "runtime_registration_boundary": (
                "Runtime Registration resolves job_type to "
                "runtime handler; Queue Routing resolves job "
                "attributes to logical queue_id"
            ),

            "prohibitions": (
                "does not create Universal Queues",
                "does not create Universal Jobs",
                "does not mutate jobs",
                "does not mutate queues",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not persist route decisions",
                "does not dispatch runtime handlers",
                "does not load Runtime Registration",
                "does not select workers",
                "does not inspect worker capability",
                "does not schedule jobs",
                "does not prioritize jobs",
                "does not balance queues",
                "does not partition queues",
                "does not use workspace_id as a route selector",
                "does not create physical queues",
                "does not create filesystem queues",
                "does not implement retry routing",
                "does not implement dead-letter routing",
                "does not enforce SLA policy",
                "does not enforce subscription entitlement",
                "does not access orchestration",
                "does not access the job store",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_QUEUE_ROUTING_VERSION",
    "UNIVERSAL_QUEUE_ROUTE_RULE_SCHEMA_VERSION",
    "UNIVERSAL_QUEUE_ROUTE_DECISION_SCHEMA_VERSION",
    "UniversalQueueRoutingError",
    "UniversalQueueRouteRule",
    "UniversalQueueRouteDecision",
    "normalize_universal_queue_route_id",
    "normalize_universal_queue_route_queue_id",
    "create_universal_queue_route_rule",
    "route_universal_queue",
    "explain_universal_queue_routing_v1",
]
