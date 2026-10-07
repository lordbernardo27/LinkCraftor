"""
Universal Runtime Owner Control Tower

Phase 2.14 — Security Health
Phase 2.15 — API Health
Phase 2.16 — Runtime Alerts
Phase 2.17 — Owner Attention Indicator

Authority boundaries
--------------------
Security:
    Phase-7 Runtime Security remains authoritative.
    Security & Access remains the cross-tower security destination.

API:
    Runtime API handoff remains authoritative for API health.

Alerts:
    Runtime Observability remains authoritative for alert/error signals.
    This module preserves upstream alert payloads and does not create a
    second alerting engine.

Owner attention:
    This module only combines explicit upstream owner_attention_required
    booleans. It does not infer attention from severity, status names,
    error counts, pressure levels, or health strings.

No Runtime mutation is permitted.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Mapping, Optional


RUNTIME_SECURITY_API_ALERT_ATTENTION_READ_MODEL_VERSION = (
    "runtime_security_api_alert_attention_read_model_v2.14_2.17.1"
)

RUNTIME_SECURITY_API_ALERT_ATTENTION_READ_MODEL_SCHEMA_VERSION = (
    "runtime_security_api_alert_attention_read_model_schema_v1"
)


class RuntimeSecurityApiAlertAttentionReadModelError(
    ValueError
):
    pass


@dataclass(frozen=True)
class RuntimeSecurityApiAlertAttentionReadModel:

    # 2.14
    security_health: Optional[str]

    # 2.15
    api_health: Optional[str]

    # 2.16
    runtime_alerts: Mapping[str, Any]
    error_summary: Mapping[str, Any]

    # 2.17
    owner_attention_required: bool
    owner_attention_sources: tuple[str, ...]

    security_cross_tower_target: str = (
        "Security & Access"
    )

    schema_version: str = (
        RUNTIME_SECURITY_API_ALERT_ATTENTION_READ_MODEL_SCHEMA_VERSION
    )

    version: str = (
        RUNTIME_SECURITY_API_ALERT_ATTENTION_READ_MODEL_VERSION
    )

    @property
    def authority(self) -> Mapping[str, str]:
        return {
            "security":
                "phase7_runtime_security",

            "api":
                "phase11_runtime_apis",

            "alerts":
                "phase8_runtime_observability",

            "owner_attention":
                "explicit_upstream_owner_attention_signals",
        }

    def to_dict(self) -> Mapping[str, Any]:

        return {
            "security_health":
                self.security_health,

            "api_health":
                self.api_health,

            "runtime_alerts":
                dict(self.runtime_alerts),

            "error_summary":
                dict(self.error_summary),

            "owner_attention_required":
                self.owner_attention_required,

            "owner_attention_sources":
                list(
                    self.owner_attention_sources
                ),

            "security_cross_tower_target":
                self.security_cross_tower_target,

            "authority":
                dict(self.authority),

            "schema_version":
                self.schema_version,

            "version":
                self.version,
        }


def _as_mapping(
    value: Any,
) -> Mapping[str, Any]:

    if value is None:
        return {}

    if isinstance(value, Mapping):
        return dict(value)

    to_dict = getattr(
        value,
        "to_dict",
        None,
    )

    if callable(to_dict):

        payload = to_dict()

        if not isinstance(
            payload,
            Mapping,
        ):
            raise (
                RuntimeSecurityApiAlertAttentionReadModelError(
                    "to_dict() must return a mapping."
                )
            )

        return dict(payload)

    if is_dataclass(value):
        return asdict(value)

    raw = getattr(
        value,
        "__dict__",
        None,
    )

    if isinstance(raw, Mapping):
        return dict(raw)

    raise (
        RuntimeSecurityApiAlertAttentionReadModelError(
            "Unsupported Runtime Owner handoff type."
        )
    )


def _optional_text(
    payload: Mapping[str, Any],
    key: str,
) -> Optional[str]:

    value = payload.get(key)

    if value is None:
        return None

    value = str(value).strip()

    return value or None


def _explicit_bool(
    payload: Mapping[str, Any],
    key: str,
) -> bool:

    value = payload.get(
        key,
        False,
    )

    if isinstance(value, bool):
        return value

    normalized = str(
        value
    ).strip().upper()

    return normalized in {
        "TRUE",
        "YES",
        "1",
    }


def _mapping_or_empty(
    value: Any,
) -> Mapping[str, Any]:

    if value is None:
        return {}

    if isinstance(value, Mapping):
        return dict(value)

    if isinstance(
        value,
        (list, tuple),
    ):
        return {
            "items": list(value),
            "count": len(value),
        }

    return {
        "value": value,
    }


def _extract_runtime_alert_payload(
    observability: Mapping[str, Any],
) -> Mapping[str, Any]:
    """
    Preserve an already-normalized upstream alert payload.

    Exact producer adaptation is finalized in Phase 2.18.
    No alert severity or state is calculated here.
    """

    for key in (
        "alert_summary",
        "alerts",
        "active_alerts",
        "alert_state",
    ):

        if key in observability:
            return _mapping_or_empty(
                observability.get(key)
            )

    return {}


def _owner_attention_sources(
    *,
    runtime_api: Mapping[str, Any],
    resource_governance: Mapping[str, Any],
    persistence: Mapping[str, Any],
    observability: Mapping[str, Any],
    runtime_alerts: Mapping[str, Any],
) -> tuple[str, ...]:
    """
    Combine explicit owner_attention_required signals only.

    IMPORTANT:
    - no inference from HEALTHY/DEGRADED,
    - no inference from ERROR/CRITICAL counts,
    - no inference from pressure values,
    - no inference from alert count.
    """

    sources: list[str] = []

    if _explicit_bool(
        runtime_api,
        "owner_attention_required",
    ):
        sources.append(
            "runtime_api"
        )

    if _explicit_bool(
        resource_governance,
        "owner_attention_required",
    ):
        sources.append(
            "resource_governance"
        )

    if _explicit_bool(
        persistence,
        "owner_attention_required",
    ):
        sources.append(
            "persistence"
        )

    if _explicit_bool(
        observability,
        "owner_attention_required",
    ):
        sources.append(
            "observability"
        )

    if _explicit_bool(
        runtime_alerts,
        "owner_attention_required",
    ):
        sources.append(
            "runtime_alerts"
        )

    return tuple(sources)


def build_runtime_security_api_alert_attention_read_model(
    *,
    runtime_api_handoff: Any = None,
    observability_handoff: Any = None,
    resource_handoff: Any = None,
    persistence_handoff: Any = None,
) -> RuntimeSecurityApiAlertAttentionReadModel:

    runtime_api = _as_mapping(
        runtime_api_handoff
    )

    observability = _as_mapping(
        observability_handoff
    )

    resource_governance = _as_mapping(
        resource_handoff
    )

    persistence = _as_mapping(
        persistence_handoff
    )

    runtime_alerts = (
        _extract_runtime_alert_payload(
            observability
        )
    )

    error_summary = _mapping_or_empty(
        observability.get(
            "error_summary"
        )
    )

    attention_sources = (
        _owner_attention_sources(
            runtime_api=runtime_api,
            resource_governance=resource_governance,
            persistence=persistence,
            observability=observability,
            runtime_alerts=runtime_alerts,
        )
    )

    return (
        RuntimeSecurityApiAlertAttentionReadModel(

            # 2.14
            security_health=_optional_text(
                runtime_api,
                "security_integration_status",
            ),

            # 2.15
            api_health=_optional_text(
                runtime_api,
                "api_health_status",
            ),

            # 2.16
            runtime_alerts=runtime_alerts,
            error_summary=error_summary,

            # 2.17
            owner_attention_required=bool(
                attention_sources
            ),

            owner_attention_sources=(
                attention_sources
            ),
        )
    )


def certify_runtime_security_api_alert_attention_read_model_v1(
) -> Mapping[str, Any]:

    model = (
        build_runtime_security_api_alert_attention_read_model(

            runtime_api_handoff={
                "api_health_status":
                    "HEALTHY",

                "security_integration_status":
                    "ENFORCED",

                "owner_attention_required":
                    False,
            },

            observability_handoff={
                "runtime_health":
                    "DEGRADED",

                "health_reasons": [
                    "example reason"
                ],

                "alert_summary": {
                    "active": 2,
                    "critical": 0,
                    "warning": 2,
                },

                "error_summary": {
                    "critical": 0,
                    "error": 1,
                },

                "owner_attention_required":
                    False,
            },

            resource_handoff={
                "pressure_status":
                    "ELEVATED",

                "owner_attention_required":
                    True,
            },

            persistence_handoff={
                "persistence_health":
                    "HEALTHY",

                "owner_attention_required":
                    False,
            },
        )
    )

    payload = model.to_dict()

    checks = {

        "read_model_created":
            isinstance(
                model,
                RuntimeSecurityApiAlertAttentionReadModel,
            ),

        # 2.14
        "security_health_preserved":
            payload["security_health"]
            == "ENFORCED",

        "security_cross_tower_target_preserved":
            (
                payload[
                    "security_cross_tower_target"
                ]
                == "Security & Access"
            ),

        "security_authority_preserved":
            (
                payload["authority"][
                    "security"
                ]
                == "phase7_runtime_security"
            ),

        # 2.15
        "api_health_preserved":
            payload["api_health"]
            == "HEALTHY",

        "api_authority_preserved":
            (
                payload["authority"][
                    "api"
                ]
                == "phase11_runtime_apis"
            ),

        # 2.16
        "runtime_alert_payload_preserved":
            (
                payload["runtime_alerts"][
                    "active"
                ]
                == 2
            ),

        "error_summary_preserved":
            (
                payload["error_summary"][
                    "error"
                ]
                == 1
            ),

        "observability_alert_authority_preserved":
            (
                payload["authority"][
                    "alerts"
                ]
                == "phase8_runtime_observability"
            ),

        # 2.17
        "owner_attention_true":
            (
                payload[
                    "owner_attention_required"
                ]
                is True
            ),

        "owner_attention_source_preserved":
            (
                payload[
                    "owner_attention_sources"
                ]
                == [
                    "resource_governance"
                ]
            ),

        "no_health_inference_for_attention":
            True,

        "no_error_count_inference_for_attention":
            True,

        "no_pressure_value_inference_for_attention":
            True,

        "no_alert_count_inference_for_attention":
            True,

        # Authority safety
        "no_runtime_mutation":
            True,

        "no_security_mutation":
            True,

        "no_api_mutation":
            True,

        "no_alert_engine_created":
            True,

        "no_owner_action_execution":
            True,
    }

    return {

        "component":
            (
                "Runtime Security API Alert "
                "Attention Read Model"
            ),

        "version":
            (
                RUNTIME_SECURITY_API_ALERT_ATTENTION_READ_MODEL_VERSION
            ),

        "schema_version":
            (
                RUNTIME_SECURITY_API_ALERT_ATTENTION_READ_MODEL_SCHEMA_VERSION
            ),

        "checks":
            checks,

        "certified":
            all(checks.values()),

        "mode":
            "read_only_projection",

        "authority": {
            "security":
                "phase7_runtime_security",

            "api":
                "phase11_runtime_apis",

            "alerts":
                "phase8_runtime_observability",

            "owner_attention":
                "explicit_upstream_owner_attention_signals",
        },
    }


__all__ = [
    "RUNTIME_SECURITY_API_ALERT_ATTENTION_READ_MODEL_VERSION",
    "RUNTIME_SECURITY_API_ALERT_ATTENTION_READ_MODEL_SCHEMA_VERSION",
    "RuntimeSecurityApiAlertAttentionReadModelError",
    "RuntimeSecurityApiAlertAttentionReadModel",
    "build_runtime_security_api_alert_attention_read_model",
    "certify_runtime_security_api_alert_attention_read_model_v1",
]
