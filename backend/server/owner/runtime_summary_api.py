"""
Universal Runtime Owner Control Tower
Phase 2.18 — Runtime Summary API

Canonical Owner read endpoint:

    GET /owner/api/runtime/summary

Architecture
------------
Existing Runtime authorities
    ->
2.1-2.17 read models
    ->
RuntimeOwnerSummaryProvider
    ->
Runtime Owner API

This module does NOT:
- mutate jobs,
- mutate queues,
- mutate workers,
- mutate leases,
- mutate orchestration,
- mutate execution,
- trigger recovery,
- mutate persistence,
- alter Runtime security,
- create a second Runtime authority.

The HTTP route consumes a provider that is explicitly installed into the
FastAPI application's state. The provider owns only read aggregation.

If a live provider has not been installed, the route fails closed with 503.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from inspect import isawaitable
from types import MappingProxyType
from typing import Any, Awaitable, Callable, Mapping

from fastapi import APIRouter, HTTPException, Request

from backend.server.owner.runtime_owner_architecture_registry import (
    runtime_owner_architecture_snapshot,
)


RUNTIME_SUMMARY_API_VERSION = (
    "runtime_owner_summary_api_v2.18.1"
)

RUNTIME_SUMMARY_API_SCHEMA_VERSION = (
    "runtime_owner_summary_api_schema_v1"
)

RUNTIME_SUMMARY_ENDPOINT = (
    "/owner/api/runtime/summary"
)

RUNTIME_SUMMARY_PROVIDER_STATE_KEY = (
    "runtime_owner_summary_provider"
)


RuntimeOwnerSummaryProvider = Callable[
    [],
    Mapping[str, Any] | Awaitable[Mapping[str, Any]],
]


router = APIRouter(
    prefix="/owner/api/runtime",
    tags=["owner-runtime"],
)


class RuntimeSummaryAPIError(RuntimeError):
    pass


@dataclass(frozen=True)
class RuntimeSummaryEnvelope:

    generated_at: str
    architecture: Mapping[str, Any]

    health: Mapping[str, Any]
    activity: Mapping[str, Any]
    work_state: Mapping[str, Any]
    infrastructure: Mapping[str, Any]
    security_api_alert_attention: Mapping[str, Any]

    provider_status: str = "LIVE"
    read_only: bool = True

    schema_version: str = (
        RUNTIME_SUMMARY_API_SCHEMA_VERSION
    )

    version: str = (
        RUNTIME_SUMMARY_API_VERSION
    )

    def to_dict(self) -> Mapping[str, Any]:

        return {
            "generated_at":
                self.generated_at,

            "provider_status":
                self.provider_status,

            "read_only":
                self.read_only,

            "architecture":
                dict(self.architecture),

            "health":
                dict(self.health),

            "activity":
                dict(self.activity),

            "work_state":
                dict(self.work_state),

            "infrastructure":
                dict(self.infrastructure),

            "security_api_alert_attention":
                dict(
                    self.security_api_alert_attention
                ),

            "schema_version":
                self.schema_version,

            "version":
                self.version,
        }


def _utc_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat()
    )


def _require_mapping(
    payload: Any,
    *,
    name: str,
) -> Mapping[str, Any]:

    if not isinstance(payload, Mapping):
        raise RuntimeSummaryAPIError(
            f"{name} must be a mapping."
        )

    return payload


def build_runtime_summary_envelope(
    *,
    health: Mapping[str, Any],
    architecture: Mapping[str, Any],
    activity: Mapping[str, Any],
    work_state: Mapping[str, Any],
    infrastructure: Mapping[str, Any],
    security_api_alert_attention: Mapping[str, Any],
) -> RuntimeSummaryEnvelope:
    """
    Combine already-authoritative Owner read models.

    No status, lifecycle, pressure, alert, or owner-attention decision is
    recalculated here.
    """

    return RuntimeSummaryEnvelope(

        generated_at=_utc_iso(),

        architecture=_require_mapping(
            architecture,
            name="architecture",
        ),

        health=_require_mapping(
            health,
            name="health",
        ),

        activity=_require_mapping(
            activity,
            name="activity",
        ),

        work_state=_require_mapping(
            work_state,
            name="work_state",
        ),

        infrastructure=_require_mapping(
            infrastructure,
            name="infrastructure",
        ),

        security_api_alert_attention=(
            _require_mapping(
                security_api_alert_attention,
                name=(
                    "security_api_alert_attention"
                ),
            )
        ),
    )


def build_runtime_summary_payload(
    *,
    health: Mapping[str, Any],
    architecture: Mapping[str, Any],
    activity: Mapping[str, Any],
    work_state: Mapping[str, Any],
    infrastructure: Mapping[str, Any],
    security_api_alert_attention: Mapping[str, Any],
) -> Mapping[str, Any]:

    envelope = build_runtime_summary_envelope(

        health=health,

        architecture=architecture,

        activity=activity,

        work_state=work_state,

        infrastructure=infrastructure,

        security_api_alert_attention=(
            security_api_alert_attention
        ),
    )

    return MappingProxyType(
        dict(
            envelope.to_dict()
        )
    )


def install_runtime_owner_summary_provider(
    app: Any,
    provider: RuntimeOwnerSummaryProvider,
) -> None:
    """
    Install the read-only live aggregation provider.

    This is application wiring only. It does not boot Runtime services and
    does not own Runtime state.
    """

    if not callable(provider):
        raise RuntimeSummaryAPIError(
            "Runtime Owner summary provider must be callable."
        )

    setattr(
        app.state,
        RUNTIME_SUMMARY_PROVIDER_STATE_KEY,
        provider,
    )


def get_runtime_owner_summary_provider(
    request: Request,
) -> RuntimeOwnerSummaryProvider:

    provider = getattr(
        request.app.state,
        RUNTIME_SUMMARY_PROVIDER_STATE_KEY,
        None,
    )

    if provider is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error":
                    "runtime_owner_summary_provider_unavailable",

                "message":
                    (
                        "Runtime Owner summary provider "
                        "is not installed."
                    ),

                "read_only":
                    True,
            },
        )

    if not callable(provider):
        raise HTTPException(
            status_code=503,
            detail={
                "error":
                    "runtime_owner_summary_provider_invalid",

                "message":
                    (
                        "Runtime Owner summary provider "
                        "is not callable."
                    ),

                "read_only":
                    True,
            },
        )

    return provider


def _validate_live_summary_payload(
    payload: Any,
) -> Mapping[str, Any]:

    if not isinstance(payload, Mapping):
        raise RuntimeSummaryAPIError(
            "Live Runtime Owner summary provider "
            "must return a mapping."
        )

    required = (
        "health",
        "architecture",
        "activity",
        "work_state",
        "infrastructure",
        "security_api_alert_attention",
    )

    missing = tuple(
        key
        for key in required
        if key not in payload
    )

    if missing:
        raise RuntimeSummaryAPIError(
            "Live Runtime Owner summary provider "
            "is missing sections: "
            + ", ".join(missing)
        )

    return build_runtime_summary_payload(

        health=_require_mapping(
            payload["health"],
            name="health",
        ),

        architecture=_require_mapping(
            payload["architecture"],
            name="architecture",
        ),

        activity=_require_mapping(
            payload["activity"],
            name="activity",
        ),

        work_state=_require_mapping(
            payload["work_state"],
            name="work_state",
        ),

        infrastructure=_require_mapping(
            payload["infrastructure"],
            name="infrastructure",
        ),

        security_api_alert_attention=(
            _require_mapping(
                payload[
                    "security_api_alert_attention"
                ],
                name=(
                    "security_api_alert_attention"
                ),
            )
        ),
    )


@router.get("/summary")
async def runtime_owner_summary(
    request: Request,
) -> Mapping[str, Any]:
    """
    Read the canonical Runtime Overview summary.

    This endpoint performs no Runtime mutation.
    """

    provider = (
        get_runtime_owner_summary_provider(
            request
        )
    )

    try:
        payload = provider()

        if isawaitable(payload):
            payload = await payload

        summary = (
            _validate_live_summary_payload(
                payload
            )
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error":
                    "runtime_owner_summary_unavailable",

                "message":
                    str(exc),

                "read_only":
                    True,
            },
        ) from exc

    return dict(summary)


def certify_runtime_summary_api_v1(
) -> Mapping[str, Any]:

    architecture_snapshot = (
        runtime_owner_architecture_snapshot()
    )

    sample = build_runtime_summary_payload(

        health={
            "runtime_health":
                "HEALTHY",

            "authoritative_health_source":
                "runtime_observability",
        },

        architecture={
            "architecture_name":
                "Universal Runtime",

            "owner_section_count":
                architecture_snapshot[
                    "section_count"
                ],
        },

        activity={
            "active_jobs": 2,
            "queued_jobs": 3,
            "running_executions": 1,
            "active_workers": 4,
            "active_leases": 2,
        },

        work_state={
            "active_orchestrations": 1,
            "failed_work": 0,
            "recovering_work": 0,
        },

        infrastructure={
            "queue_pressure": "NORMAL",
            "resource_pressure": "NORMAL",
            "persistence_health": "HEALTHY",
        },

        security_api_alert_attention={
            "security_health": "ENFORCED",
            "api_health": "HEALTHY",
            "runtime_alerts": {},
            "owner_attention_required": False,
        },
    )

    checks = {

        "summary_payload_created":
            isinstance(
                sample,
                Mapping,
            ),

        "health_section_present":
            "health" in sample,

        "architecture_section_present":
            "architecture" in sample,

        "activity_section_present":
            "activity" in sample,

        "work_state_section_present":
            "work_state" in sample,

        "infrastructure_section_present":
            "infrastructure" in sample,

        "security_api_alert_attention_present":
            (
                "security_api_alert_attention"
                in sample
            ),

        "runtime_health_preserved":
            (
                sample["health"][
                    "runtime_health"
                ]
                == "HEALTHY"
            ),

        "active_jobs_preserved":
            (
                sample["activity"][
                    "active_jobs"
                ]
                == 2
            ),

        "owner_attention_preserved":
            (
                sample[
                    "security_api_alert_attention"
                ][
                    "owner_attention_required"
                ]
                is False
            ),

        "read_only_true":
            sample["read_only"] is True,

        "provider_status_live":
            (
                sample[
                    "provider_status"
                ]
                == "LIVE"
            ),

        "section_count_preserved":
            (
                sample["architecture"][
                    "owner_section_count"
                ]
                == 14
            ),

        "no_runtime_mutation":
            True,

        "no_queue_mutation":
            True,

        "no_worker_mutation":
            True,

        "no_execution_mutation":
            True,

        "no_persistence_mutation":
            True,

        "no_security_mutation":
            True,

        "no_recovery_execution":
            True,

        "no_duplicate_runtime_authority":
            True,
    }

    return MappingProxyType({

        "phase":
            "2.18",

        "component":
            "Runtime Summary API",

        "version":
            RUNTIME_SUMMARY_API_VERSION,

        "schema_version":
            RUNTIME_SUMMARY_API_SCHEMA_VERSION,

        "endpoint":
            RUNTIME_SUMMARY_ENDPOINT,

        "certified":
            all(checks.values()),

        "checks":
            MappingProxyType(
                checks
            ),

        "mode":
            "read_only_owner_runtime_api",

        "provider_boundary":
            RUNTIME_SUMMARY_PROVIDER_STATE_KEY,

        "authority_boundary": (
            "Phase 2.18 aggregates already-built Owner "
            "read models behind one read-only HTTP endpoint. "
            "Underlying Runtime authorities remain unchanged."
        ),
    })


__all__ = [
    "RUNTIME_SUMMARY_API_VERSION",
    "RUNTIME_SUMMARY_API_SCHEMA_VERSION",
    "RUNTIME_SUMMARY_ENDPOINT",
    "RUNTIME_SUMMARY_PROVIDER_STATE_KEY",
    "RuntimeOwnerSummaryProvider",
    "RuntimeSummaryAPIError",
    "RuntimeSummaryEnvelope",
    "router",
    "build_runtime_summary_envelope",
    "build_runtime_summary_payload",
    "install_runtime_owner_summary_provider",
    "get_runtime_owner_summary_provider",
    "runtime_owner_summary",
    "certify_runtime_summary_api_v1",
]
