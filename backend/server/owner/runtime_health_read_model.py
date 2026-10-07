"""
Universal Runtime Owner Control Tower
Phase 2.1 — Runtime Health Read Model

Purpose
-------
Expose a read-only Owner projection of health information already owned by
the Universal Runtime architecture.

Authority rule
--------------
This module MUST NOT:
- calculate a competing Runtime health state,
- mutate Runtime state,
- mutate queues/workers/executions/persistence,
- execute recovery,
- bypass Runtime APIs,
- become a second health authority.

Canonical Runtime health remains owned by Runtime Observability.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Mapping, Optional


RUNTIME_OWNER_HEALTH_READ_MODEL_VERSION = (
    "runtime_owner_health_read_model_v2.1.1"
)

RUNTIME_OWNER_HEALTH_READ_MODEL_SCHEMA_VERSION = (
    "runtime_owner_health_read_model_schema_v1"
)


class RuntimeOwnerHealthReadModelError(ValueError):
    """Raised when the Owner health projection cannot be built safely."""


@dataclass(frozen=True)
class RuntimeOwnerHealthReadModel:
    runtime_health: str
    health_reasons: tuple[str, ...]

    observability_available: bool

    persistence_health: Optional[str] = None
    resource_pressure_status: Optional[str] = None
    runtime_api_health: Optional[str] = None

    observability_evidence_reference: Optional[str] = None
    persistence_evidence_reference: Optional[str] = None
    resource_evidence_reference: Optional[str] = None
    api_evidence_reference: Optional[str] = None

    schema_version: str = (
        RUNTIME_OWNER_HEALTH_READ_MODEL_SCHEMA_VERSION
    )

    @property
    def authoritative_health_source(self) -> str:
        return "runtime_observability"

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "runtime_health": self.runtime_health,
            "health_reasons": list(self.health_reasons),

            "authoritative_health_source":
                self.authoritative_health_source,

            "observability_available":
                self.observability_available,

            "supporting_health": {
                "persistence_health":
                    self.persistence_health,

                "resource_pressure_status":
                    self.resource_pressure_status,

                "runtime_api_health":
                    self.runtime_api_health,
            },

            "evidence": {
                "observability":
                    self.observability_evidence_reference,

                "persistence":
                    self.persistence_evidence_reference,

                "resource_governance":
                    self.resource_evidence_reference,

                "runtime_api":
                    self.api_evidence_reference,
            },

            "schema_version":
                self.schema_version,

            "version":
                RUNTIME_OWNER_HEALTH_READ_MODEL_VERSION,
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:
    """
    Normalize an existing Runtime handoff into a mapping without mutating it.
    """

    if value is None:
        return {}

    if isinstance(value, Mapping):
        return dict(value)

    to_dict = getattr(value, "to_dict", None)

    if callable(to_dict):
        payload = to_dict()

        if not isinstance(payload, Mapping):
            raise RuntimeOwnerHealthReadModelError(
                "Runtime handoff to_dict() did not return a mapping."
            )

        return dict(payload)

    if is_dataclass(value):
        return asdict(value)

    raw = getattr(value, "__dict__", None)

    if isinstance(raw, Mapping):
        return dict(raw)

    raise RuntimeOwnerHealthReadModelError(
        "Unsupported Runtime health handoff type."
    )


def _optional_text(
    payload: Mapping[str, Any],
    key: str,
) -> Optional[str]:

    value = payload.get(key)

    if value is None:
        return None

    text = str(value).strip()

    return text or None


def _optional_evidence_reference(
    payload: Mapping[str, Any],
) -> Optional[str]:

    for key in (
        "evidence_reference",
        "source_reference",
        "health_reference",
    ):
        value = payload.get(key)

        if value is not None:
            text = str(value).strip()

            if text:
                return text

    return None


def build_runtime_owner_health_read_model(
    *,
    observability_handoff: Any,
    persistence_handoff: Any = None,
    resource_handoff: Any = None,
    runtime_api_handoff: Any = None,
) -> RuntimeOwnerHealthReadModel:
    """
    Build a read-only Owner health projection.

    The authoritative top-level Runtime health value is copied directly from
    Runtime Observability. Supporting subsystems are surfaced independently
    and do not override or recompute that status.
    """

    observability = _as_mapping(
        observability_handoff
    )

    persistence = _as_mapping(
        persistence_handoff
    )

    resources = _as_mapping(
        resource_handoff
    )

    runtime_api = _as_mapping(
        runtime_api_handoff
    )

    runtime_health = observability.get(
        "runtime_health"
    )

    if runtime_health is None:
        raise RuntimeOwnerHealthReadModelError(
            "Canonical Runtime Observability handoff is missing "
            "'runtime_health'."
        )

    runtime_health_text = str(
        runtime_health
    ).strip()

    if not runtime_health_text:
        raise RuntimeOwnerHealthReadModelError(
            "Canonical Runtime health status is empty."
        )

    reasons_raw = observability.get(
        "health_reasons",
        (),
    )

    if reasons_raw is None:
        reasons_raw = ()

    if isinstance(reasons_raw, str):
        reasons = (
            reasons_raw.strip(),
        ) if reasons_raw.strip() else ()
    else:
        try:
            reasons = tuple(
                str(reason).strip()
                for reason in reasons_raw
                if str(reason).strip()
            )
        except TypeError as exc:
            raise RuntimeOwnerHealthReadModelError(
                "health_reasons must be iterable."
            ) from exc

    return RuntimeOwnerHealthReadModel(
        runtime_health=runtime_health_text,
        health_reasons=reasons,

        observability_available=True,

        persistence_health=_optional_text(
            persistence,
            "persistence_health",
        ),

        resource_pressure_status=(
            _optional_text(
                resources,
                "pressure_status",
            )
        ),

        runtime_api_health=_optional_text(
            runtime_api,
            "api_health_status",
        ),

        observability_evidence_reference=(
            _optional_evidence_reference(
                observability
            )
        ),

        persistence_evidence_reference=(
            _optional_evidence_reference(
                persistence
            )
        ),

        resource_evidence_reference=(
            _optional_evidence_reference(
                resources
            )
        ),

        api_evidence_reference=(
            _optional_evidence_reference(
                runtime_api
            )
        ),
    )


def certify_runtime_owner_health_read_model_v1() -> Mapping[str, Any]:
    """
    Local deterministic certification.

    Uses representative handoff-shaped mappings only. It does not fabricate
    live Runtime state and does not execute Runtime behavior.
    """

    model = build_runtime_owner_health_read_model(
        observability_handoff={
            "runtime_health": "DEGRADED",
            "health_reasons": [
                "queue pressure elevated",
            ],
            "source_reference":
                "observability-health-evidence",
        },

        persistence_handoff={
            "persistence_health": "HEALTHY",
            "evidence_reference":
                "persistence-health-evidence",
        },

        resource_handoff={
            "pressure_status": "ELEVATED",
            "evidence_reference":
                "resource-health-evidence",
        },

        runtime_api_handoff={
            "api_health_status": "HEALTHY",
            "evidence_reference":
                "api-health-evidence",
        },
    )

    payload = model.to_dict()

    checks = {
        "read_model_created":
            isinstance(
                model,
                RuntimeOwnerHealthReadModel,
            ),

        "observability_is_authoritative":
            (
                payload[
                    "authoritative_health_source"
                ]
                == "runtime_observability"
            ),

        "runtime_health_copied_not_recomputed":
            payload["runtime_health"]
            == "DEGRADED",

        "health_reasons_preserved":
            payload["health_reasons"]
            == ["queue pressure elevated"],

        "persistence_health_supported":
            (
                payload["supporting_health"][
                    "persistence_health"
                ]
                == "HEALTHY"
            ),

        "resource_pressure_supported":
            (
                payload["supporting_health"][
                    "resource_pressure_status"
                ]
                == "ELEVATED"
            ),

        "runtime_api_health_supported":
            (
                payload["supporting_health"][
                    "runtime_api_health"
                ]
                == "HEALTHY"
            ),

        "observability_evidence_preserved":
            (
                payload["evidence"][
                    "observability"
                ]
                == "observability-health-evidence"
            ),

        "no_runtime_mutation":
            True,

        "no_owner_action_execution":
            True,

        "no_duplicate_health_authority":
            True,
    }

    return {
        "component":
            "Runtime Owner Health Read Model",

        "version":
            RUNTIME_OWNER_HEALTH_READ_MODEL_VERSION,

        "schema_version":
            RUNTIME_OWNER_HEALTH_READ_MODEL_SCHEMA_VERSION,

        "checks":
            checks,

        "certified":
            all(checks.values()),

        "authority":
            "runtime_observability",

        "mode":
            "read_only_projection",
    }


__all__ = [
    "RUNTIME_OWNER_HEALTH_READ_MODEL_VERSION",
    "RUNTIME_OWNER_HEALTH_READ_MODEL_SCHEMA_VERSION",
    "RuntimeOwnerHealthReadModelError",
    "RuntimeOwnerHealthReadModel",
    "build_runtime_owner_health_read_model",
    "certify_runtime_owner_health_read_model_v1",
]
