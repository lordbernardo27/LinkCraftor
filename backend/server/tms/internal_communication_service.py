
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")

COMMUNICATION_SERVICE_PATH = (
    DATA_DIR / "internal_communication_service.jsonl"
)

COMMUNICATION_SERVICE_AUDIT_PATH = (
    DATA_DIR / "internal_communication_service_audit.jsonl"
)

COMMUNICATION_SERVICE_EVENTS_PATH = (
    DATA_DIR / "internal_communication_service_events.jsonl"
)


ALLOWED_SERVICE_STATUSES = {
    "registered",
    "starting",
    "active",
    "degraded",
    "paused",
    "stopping",
    "stopped",
    "failed",
}


@dataclass(frozen=True)
class InternalCommunicationService:
    service_id: str
    service_name: str
    workspace_id: str
    status: str = "registered"
    service_version: str = "22A.1.1"
    channels_enabled: bool = True
    direct_messages_enabled: bool = True
    realtime_enabled: bool = False
    presence_enabled: bool = False
    notifications_enabled: bool = False
    configuration: Dict[str, Any] = field(
        default_factory=dict
    )
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )
    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )
    started_at: str | None = None
    stopped_at: str | None = None
    last_health_check_at: str | None = None
    failure_reason: str | None = None


@dataclass(frozen=True)
class CommunicationServiceEvent:
    event_id: str
    service_id: str
    workspace_id: str
    event_type: str
    actor_id: str | None = None
    status: str | None = None
    message: str = ""
    payload: Dict[str, Any] = field(
        default_factory=dict
    )
    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )


def _ensure_store() -> None:
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for path in (
        COMMUNICATION_SERVICE_PATH,
        COMMUNICATION_SERVICE_AUDIT_PATH,
        COMMUNICATION_SERVICE_EVENTS_PATH,
    ):
        if not path.exists():
            path.write_text(
                "",
                encoding="utf-8",
            )


def _utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _new_id(prefix: str) -> str:
    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%d%H%M%S%f"
    )

    return f"{prefix}_{timestamp}"


def _validate_required_text(
    value: str,
    field_name: str,
) -> str:
    normalized = str(
        value or ""
    ).strip()

    if not normalized:
        raise ValueError(
            f"{field_name} must be a non-empty string."
        )

    return normalized


def _validate_status(
    status: str,
) -> str:
    normalized = _validate_required_text(
        status,
        "status",
    )

    if normalized not in ALLOWED_SERVICE_STATUSES:
        raise ValueError(
            f"Unsupported communication service status: "
            f"{normalized}"
        )

    return normalized


def _append_jsonl(
    path: Path,
    payload: Dict[str, Any],
) -> None:
    _ensure_store()

    with path.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                payload,
                ensure_ascii=False,
            )
            + "\n"
        )


def _read_jsonl(
    path: Path,
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    _ensure_store()

    if limit <= 0:
        return []

    lines = path.read_text(
        encoding="utf-8"
    ).splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]


def _write_service(
    service: InternalCommunicationService,
) -> Dict[str, Any]:
    payload = asdict(service)

    _append_jsonl(
        COMMUNICATION_SERVICE_PATH,
        payload,
    )

    return payload


def _write_service_event(
    event: CommunicationServiceEvent,
) -> Dict[str, Any]:
    payload = asdict(event)

    _append_jsonl(
        COMMUNICATION_SERVICE_EVENTS_PATH,
        payload,
    )

    return payload


def _audit(
    *,
    event_type: str,
    service_id: str,
    workspace_id: str,
    actor_id: str | None = None,
    status: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    payload = {
        "event_type": event_type,
        "service_id": service_id,
        "workspace_id": workspace_id,
        "actor_id": actor_id,
        "status": status,
        "metadata": metadata or {},
        "created_at": _utc_now(),
    }

    _append_jsonl(
        COMMUNICATION_SERVICE_AUDIT_PATH,
        payload,
    )

    return payload


def read_communication_service_events(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return _read_jsonl(
        COMMUNICATION_SERVICE_EVENTS_PATH,
        limit,
    )


def read_communication_service_records(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return _read_jsonl(
        COMMUNICATION_SERVICE_PATH,
        limit,
    )


def _latest_services_by_id(
    *,
    workspace_id: str | None = None,
) -> Dict[str, Dict[str, Any]]:
    records = read_communication_service_records(
        limit=100000,
    )

    latest: Dict[str, Dict[str, Any]] = {}

    for record in records:
        if (
            workspace_id is not None
            and str(record.get("workspace_id"))
            != str(workspace_id)
        ):
            continue

        service_id = str(
            record.get("service_id") or ""
        )

        if service_id:
            latest[service_id] = record

    return latest


def get_internal_communication_service(
    *,
    service_id: str,
    workspace_id: str,
) -> Dict[str, Any] | None:
    normalized_service_id = _validate_required_text(
        service_id,
        "service_id",
    )

    normalized_workspace_id = _validate_required_text(
        workspace_id,
        "workspace_id",
    )

    return _latest_services_by_id(
        workspace_id=normalized_workspace_id,
    ).get(
        normalized_service_id
    )


def register_internal_communication_service(
    *,
    workspace_id: str,
    service_name: str = "internal_communication",
    service_version: str = "22A.1.1",
    channels_enabled: bool = True,
    direct_messages_enabled: bool = True,
    configuration: Dict[str, Any] | None = None,
    metadata: Dict[str, Any] | None = None,
    actor_id: str | None = None,
) -> Dict[str, Any]:
    normalized_workspace_id = _validate_required_text(
        workspace_id,
        "workspace_id",
    )

    normalized_service_name = _validate_required_text(
        service_name,
        "service_name",
    )

    normalized_service_version = _validate_required_text(
        service_version,
        "service_version",
    )

    existing_services = _latest_services_by_id(
        workspace_id=normalized_workspace_id,
    )

    for existing in existing_services.values():
        if (
            str(existing.get("service_name"))
            == normalized_service_name
            and str(existing.get("status"))
            not in {"stopped", "failed"}
        ):
            raise ValueError(
                "An active internal communication service "
                "is already registered for this workspace."
            )

    service = InternalCommunicationService(
        service_id=_new_id(
            "communication_service"
        ),
        service_name=normalized_service_name,
        workspace_id=normalized_workspace_id,
        status="registered",
        service_version=normalized_service_version,
        channels_enabled=bool(
            channels_enabled
        ),
        direct_messages_enabled=bool(
            direct_messages_enabled
        ),
        configuration=dict(
            configuration or {}
        ),
        metadata=dict(
            metadata or {}
        ),
    )

    payload = _write_service(
        service
    )

    _write_service_event(
        CommunicationServiceEvent(
            event_id=_new_id(
                "communication_service_event"
            ),
            service_id=service.service_id,
            workspace_id=service.workspace_id,
            event_type="service_registered",
            actor_id=actor_id,
            status=service.status,
            message=(
                "Internal communication service "
                "registered."
            ),
            payload={
                "service_name": service.service_name,
                "service_version": service.service_version,
            },
        )
    )

    _audit(
        event_type="communication_service_registered",
        service_id=service.service_id,
        workspace_id=service.workspace_id,
        actor_id=actor_id,
        status=service.status,
        metadata={
            "service_name": service.service_name,
            "service_version": service.service_version,
        },
    )

    return payload


def _transition_service_status(
    *,
    service_id: str,
    workspace_id: str,
    status: str,
    actor_id: str | None = None,
    message: str = "",
    failure_reason: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    existing = get_internal_communication_service(
        service_id=service_id,
        workspace_id=workspace_id,
    )

    if existing is None:
        raise LookupError(
            "Internal communication service "
            f"not found: {service_id}"
        )

    normalized_status = _validate_status(
        status
    )

    now = _utc_now()

    started_at = existing.get(
        "started_at"
    )
    stopped_at = existing.get(
        "stopped_at"
    )

    if normalized_status == "active":
        started_at = started_at or now
        stopped_at = None

    if normalized_status == "stopped":
        stopped_at = now

    updated_service = InternalCommunicationService(
        service_id=str(
            existing.get("service_id")
        ),
        service_name=str(
            existing.get("service_name")
        ),
        workspace_id=str(
            existing.get("workspace_id")
        ),
        status=normalized_status,
        service_version=str(
            existing.get("service_version")
            or "22A.1.1"
        ),
        channels_enabled=bool(
            existing.get(
                "channels_enabled",
                True,
            )
        ),
        direct_messages_enabled=bool(
            existing.get(
                "direct_messages_enabled",
                True,
            )
        ),
        realtime_enabled=bool(
            existing.get(
                "realtime_enabled",
                False,
            )
        ),
        presence_enabled=bool(
            existing.get(
                "presence_enabled",
                False,
            )
        ),
        notifications_enabled=bool(
            existing.get(
                "notifications_enabled",
                False,
            )
        ),
        configuration=dict(
            existing.get(
                "configuration"
            )
            or {}
        ),
        metadata={
            **dict(
                existing.get("metadata")
                or {}
            ),
            **dict(metadata or {}),
        },
        created_at=str(
            existing.get("created_at")
        ),
        updated_at=now,
        started_at=started_at,
        stopped_at=stopped_at,
        last_health_check_at=existing.get(
            "last_health_check_at"
        ),
        failure_reason=failure_reason,
    )

    payload = _write_service(
        updated_service
    )

    _write_service_event(
        CommunicationServiceEvent(
            event_id=_new_id(
                "communication_service_event"
            ),
            service_id=updated_service.service_id,
            workspace_id=updated_service.workspace_id,
            event_type="service_status_changed",
            actor_id=actor_id,
            status=normalized_status,
            message=message,
            payload={
                "previous_status": existing.get(
                    "status"
                ),
                "new_status": normalized_status,
                "failure_reason": failure_reason,
            },
        )
    )

    _audit(
        event_type="communication_service_status_changed",
        service_id=updated_service.service_id,
        workspace_id=updated_service.workspace_id,
        actor_id=actor_id,
        status=normalized_status,
        metadata={
            "previous_status": existing.get(
                "status"
            ),
            "new_status": normalized_status,
            "message": message,
            "failure_reason": failure_reason,
        },
    )

    return payload


def start_internal_communication_service(
    *,
    service_id: str,
    workspace_id: str,
    actor_id: str | None = None,
) -> Dict[str, Any]:
    return _transition_service_status(
        service_id=service_id,
        workspace_id=workspace_id,
        status="active",
        actor_id=actor_id,
        message=(
            "Internal communication service started."
        ),
    )


def mark_internal_communication_service_degraded(
    *,
    service_id: str,
    workspace_id: str,
    reason: str,
    actor_id: str | None = None,
) -> Dict[str, Any]:
    normalized_reason = _validate_required_text(
        reason,
        "reason",
    )

    return _transition_service_status(
        service_id=service_id,
        workspace_id=workspace_id,
        status="degraded",
        actor_id=actor_id,
        message=(
            "Internal communication service "
            "entered degraded state."
        ),
        failure_reason=normalized_reason,
    )


def pause_internal_communication_service(
    *,
    service_id: str,
    workspace_id: str,
    actor_id: str | None = None,
    reason: str = "paused_by_operator",
) -> Dict[str, Any]:
    return _transition_service_status(
        service_id=service_id,
        workspace_id=workspace_id,
        status="paused",
        actor_id=actor_id,
        message=reason,
    )


def stop_internal_communication_service(
    *,
    service_id: str,
    workspace_id: str,
    actor_id: str | None = None,
    reason: str = "stopped_by_operator",
) -> Dict[str, Any]:
    return _transition_service_status(
        service_id=service_id,
        workspace_id=workspace_id,
        status="stopped",
        actor_id=actor_id,
        message=reason,
    )


# ============================================================
# SERVICE HEALTH
# ============================================================

def update_internal_communication_health(
    *,
    service_id: str,
    workspace_id: str,
    actor_id: str | None = None,
    healthy: bool = True,
    message: str = "",
) -> Dict[str, Any]:
    return {
        "service_id": service_id,
        "workspace_id": workspace_id,
        "healthy": healthy,
        "message": message,
        "actor_id": actor_id,
        "status": "active" if healthy else "degraded",
    }


# ============================================================
# CONFIGURATION
# ============================================================

def update_internal_communication_configuration(
    *,
    service_id: str,
    workspace_id: str,
    configuration: Dict[str, Any],
    actor_id: str | None = None,
) -> Dict[str, Any]:
    return {
        "service_id": service_id,
        "workspace_id": workspace_id,
        "configuration": configuration,
        "actor_id": actor_id,
        "status": "updated",
    }



# ============================================================
# SERVICE CAPABILITIES
# ============================================================

def enable_realtime(
    *,
    service_id: str,
    workspace_id: str,
) -> Dict[str, Any]:

    service = get_internal_communication_service(
        service_id=service_id,
        workspace_id=workspace_id,
    )

    if service is None:
        raise LookupError(service_id)

    updated = {
        **service,
        "realtime_enabled": True,
        "updated_at": _utc_now(),
    }

    _append_jsonl(
        COMMUNICATION_SERVICE_PATH,
        updated,
    )

    _audit(
        event_type="realtime_enabled",
        service_id=service_id,
        workspace_id=workspace_id,
        status=updated["status"],
    )

    return updated


def enable_presence(
    *,
    service_id: str,
    workspace_id: str,
) -> Dict[str, Any]:

    service = get_internal_communication_service(
        service_id=service_id,
        workspace_id=workspace_id,
    )

    if service is None:
        raise LookupError(service_id)

    updated = {
        **service,
        "presence_enabled": True,
        "updated_at": _utc_now(),
    }

    _append_jsonl(
        COMMUNICATION_SERVICE_PATH,
        updated,
    )

    _audit(
        event_type="presence_enabled",
        service_id=service_id,
        workspace_id=workspace_id,
        status=updated["status"],
    )

    return updated


def enable_notifications(
    *,
    service_id: str,
    workspace_id: str,
) -> Dict[str, Any]:

    service = get_internal_communication_service(
        service_id=service_id,
        workspace_id=workspace_id,
    )

    if service is None:
        raise LookupError(service_id)

    updated = {
        **service,
        "notifications_enabled": True,
        "updated_at": _utc_now(),
    }

    _append_jsonl(
        COMMUNICATION_SERVICE_PATH,
        updated,
    )

    _audit(
        event_type="notifications_enabled",
        service_id=service_id,
        workspace_id=workspace_id,
        status=updated["status"],
    )

    return updated


# ============================================================
# HEALTH SNAPSHOT
# ============================================================

def build_service_snapshot(
    *,
    service_id: str,
    workspace_id: str,
) -> Dict[str, Any]:

    service = get_internal_communication_service(
        service_id=service_id,
        workspace_id=workspace_id,
    )

    if service is None:
        raise LookupError(service_id)

    return {
        "service": service,
        "healthy": service["status"] == "active",
        "generated_at": _utc_now(),
    }



# ============================================================
# SERVICE DISCOVERY
# ============================================================

def list_internal_communication_services(
    *,
    workspace_id: str | None = None,
) -> List[Dict[str, Any]]:

    services = read_communication_service_records(
        limit=100000,
    )

    latest: Dict[str, Dict[str, Any]] = {}

    for service in services:

        if (
            workspace_id is not None
            and str(service.get("workspace_id"))
            != str(workspace_id)
        ):
            continue

        latest[str(service["service_id"])] = service

    return list(latest.values())


def communication_service_statistics() -> Dict[str, Any]:

    services = list_internal_communication_services()

    active = 0
    degraded = 0
    stopped = 0

    for service in services:

        status = str(service.get("status"))

        if status == "active":
            active += 1

        elif status == "degraded":
            degraded += 1

        elif status == "stopped":
            stopped += 1

    return {
        "service_count": len(services),
        "active_services": active,
        "degraded_services": degraded,
        "stopped_services": stopped,
        "generated_at": _utc_now(),
    }


# ============================================================
# AUDIT
# ============================================================

def read_internal_communication_audit(
    limit: int = 1000,
) -> List[Dict[str, Any]]:

    return _read_jsonl(
        COMMUNICATION_SERVICE_AUDIT_PATH,
        limit,
    )


def build_internal_communication_summary() -> Dict[str, Any]:

    return {
        "statistics": communication_service_statistics(),
        "services": list_internal_communication_services(),
        "recent_events": read_communication_service_events(
            limit=100,
        ),
        "generated_at": _utc_now(),
    }

