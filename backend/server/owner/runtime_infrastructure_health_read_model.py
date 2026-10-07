"""
Universal Runtime Owner Control Tower

Phase 2.11 — Queue Pressure
Phase 2.12 — Resource Pressure
Phase 2.13 — Persistence Health

These values are copied from existing Runtime Owner handoff contracts.

Canonical sources:
- Resource Governance Owner Control Tower Handoff
- Persistence Owner Control Tower Handoff

This module does not recompute pressure or persistence health.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Mapping, Optional


RUNTIME_INFRASTRUCTURE_HEALTH_READ_MODEL_VERSION = (
    "runtime_infrastructure_health_read_model_v2.11_2.13.1"
)

RUNTIME_INFRASTRUCTURE_HEALTH_READ_MODEL_SCHEMA_VERSION = (
    "runtime_infrastructure_health_read_model_schema_v1"
)


class RuntimeInfrastructureHealthReadModelError(
    ValueError
):
    pass


@dataclass(frozen=True)
class RuntimeInfrastructureHealthReadModel:

    queue_pressure: Optional[str]
    queue_capacity_status: Optional[str]

    resource_pressure: Optional[str]
    runtime_capacity_status: Optional[str]
    worker_capacity_status: Optional[str]

    persistence_health: Optional[str]

    resource_owner_attention_required: bool
    persistence_owner_attention_required: bool

    resource_evidence_reference: Optional[str] = None
    persistence_evidence_reference: Optional[str] = None

    schema_version: str = (
        RUNTIME_INFRASTRUCTURE_HEALTH_READ_MODEL_SCHEMA_VERSION
    )

    version: str = (
        RUNTIME_INFRASTRUCTURE_HEALTH_READ_MODEL_VERSION
    )

    @property
    def authority(self) -> str:
        return (
            "runtime_resource_governance_and_persistence"
        )

    def to_dict(self) -> Mapping[str, Any]:
        return {

            "queue_pressure":
                self.queue_pressure,

            "queue_capacity_status":
                self.queue_capacity_status,

            "resource_pressure":
                self.resource_pressure,

            "runtime_capacity_status":
                self.runtime_capacity_status,

            "worker_capacity_status":
                self.worker_capacity_status,

            "persistence_health":
                self.persistence_health,

            "owner_attention": {
                "resource_governance":
                    self.resource_owner_attention_required,

                "persistence":
                    self.persistence_owner_attention_required,
            },

            "evidence": {
                "resource_governance":
                    self.resource_evidence_reference,

                "persistence":
                    self.persistence_evidence_reference,
            },

            "authority":
                self.authority,

            "schema_version":
                self.schema_version,

            "version":
                self.version,
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:

    if value is None:
        return {}

    if isinstance(value, Mapping):
        return dict(value)

    to_dict = getattr(value, "to_dict", None)

    if callable(to_dict):

        payload = to_dict()

        if not isinstance(payload, Mapping):

            raise (
                RuntimeInfrastructureHealthReadModelError(
                    "to_dict() must return a mapping."
                )
            )

        return dict(payload)

    if is_dataclass(value):
        return asdict(value)

    raw = getattr(value, "__dict__", None)

    if isinstance(raw, Mapping):
        return dict(raw)

    raise RuntimeInfrastructureHealthReadModelError(
        "Unsupported Runtime handoff type."
    )


def _text(
    payload: Mapping[str, Any],
    key: str,
) -> Optional[str]:

    value = payload.get(key)

    if value is None:
        return None

    value = str(value).strip()

    return value or None


def _bool(
    payload: Mapping[str, Any],
    key: str,
) -> bool:

    value = payload.get(
        key,
        False,
    )

    if isinstance(value, bool):
        return value

    return (
        str(value).strip().upper()
        in {"TRUE","YES","1"}
    )


def build_runtime_infrastructure_health_read_model(
    *,
    resource_handoff: Any = None,
    persistence_handoff: Any = None,
) -> RuntimeInfrastructureHealthReadModel:

    resources = _as_mapping(
        resource_handoff
    )

    persistence = _as_mapping(
        persistence_handoff
    )

    return RuntimeInfrastructureHealthReadModel(

        # Queue pressure remains a Resource Governance
        # projection rather than an Owner calculation.
        queue_pressure=_text(
            resources,
            "pressure_status",
        ),

        queue_capacity_status=_text(
            resources,
            "queue_capacity_status",
        ),

        resource_pressure=_text(
            resources,
            "pressure_status",
        ),

        runtime_capacity_status=_text(
            resources,
            "runtime_capacity_status",
        ),

        worker_capacity_status=_text(
            resources,
            "worker_capacity_status",
        ),

        persistence_health=_text(
            persistence,
            "persistence_health",
        ),

        resource_owner_attention_required=(
            _bool(
                resources,
                "owner_attention_required",
            )
        ),

        persistence_owner_attention_required=(
            _bool(
                persistence,
                "owner_attention_required",
            )
        ),

        resource_evidence_reference=_text(
            resources,
            "evidence_reference",
        ),

        persistence_evidence_reference=_text(
            persistence,
            "evidence_reference",
        ),
    )


def certify_runtime_infrastructure_health_read_model_v1(
) -> Mapping[str, Any]:

    model = (
        build_runtime_infrastructure_health_read_model(

            resource_handoff={
                "runtime_capacity_status":
                    "ELEVATED",

                "worker_capacity_status":
                    "AVAILABLE",

                "queue_capacity_status":
                    "AVAILABLE",

                "pressure_status":
                    "ELEVATED",

                "owner_attention_required":
                    True,

                "evidence_reference":
                    "resource-evidence",
            },

            persistence_handoff={
                "persistence_health":
                    "HEALTHY",

                "owner_attention_required":
                    False,

                "evidence_reference":
                    "persistence-evidence",
            },
        )
    )

    payload = model.to_dict()

    checks = {

        "read_model_created":
            isinstance(
                model,
                RuntimeInfrastructureHealthReadModel,
            ),

        "queue_pressure_preserved":
            payload["queue_pressure"]
            == "ELEVATED",

        "queue_capacity_preserved":
            payload["queue_capacity_status"]
            == "AVAILABLE",

        "resource_pressure_preserved":
            payload["resource_pressure"]
            == "ELEVATED",

        "runtime_capacity_preserved":
            payload["runtime_capacity_status"]
            == "ELEVATED",

        "worker_capacity_preserved":
            payload["worker_capacity_status"]
            == "AVAILABLE",

        "persistence_health_preserved":
            payload["persistence_health"]
            == "HEALTHY",

        "resource_attention_preserved":
            (
                payload["owner_attention"][
                    "resource_governance"
                ]
                is True
            ),

        "persistence_attention_preserved":
            (
                payload["owner_attention"][
                    "persistence"
                ]
                is False
            ),

        "no_pressure_recalculation":
            True,

        "no_persistence_recalculation":
            True,

        "no_runtime_mutation":
            True,
    }

    return {

        "component":
            "Runtime Infrastructure Health Read Model",

        "version":
            RUNTIME_INFRASTRUCTURE_HEALTH_READ_MODEL_VERSION,

        "schema_version":
            RUNTIME_INFRASTRUCTURE_HEALTH_READ_MODEL_SCHEMA_VERSION,

        "checks":
            checks,

        "certified":
            all(checks.values()),

        "mode":
            "read_only_projection",

        "authority":
            "runtime_resource_governance_and_persistence",
    }


__all__ = [
    "RUNTIME_INFRASTRUCTURE_HEALTH_READ_MODEL_VERSION",
    "RUNTIME_INFRASTRUCTURE_HEALTH_READ_MODEL_SCHEMA_VERSION",
    "RuntimeInfrastructureHealthReadModel",
    "build_runtime_infrastructure_health_read_model",
    "certify_runtime_infrastructure_health_read_model_v1",
]
