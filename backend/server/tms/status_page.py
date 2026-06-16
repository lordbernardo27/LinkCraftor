
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.server.tms.incident_management import read_incidents


DATA_DIR = Path("backend/server/data/tms")

STATUS_PAGE_SERVICES_PATH = DATA_DIR / "status_page_services.jsonl"
STATUS_PAGE_UPDATES_PATH = DATA_DIR / "status_page_updates.jsonl"
STATUS_PAGE_AUDIT_PATH = DATA_DIR / "status_page_audit.jsonl"


@dataclass(frozen=True)
class ServiceStatus:
    service_id: str
    name: str
    description: str = ""
    status: str = "operational"
    workspace_id: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class StatusPageUpdate:
    update_id: str
    incident_id: str
    title: str
    message: str
    status: str = "published"
    visibility: str = "public"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for path in (
        STATUS_PAGE_SERVICES_PATH,
        STATUS_PAGE_UPDATES_PATH,
        STATUS_PAGE_AUDIT_PATH,
    ):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id(prefix: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}_{ts}"


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_store()

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path, limit: int = 1000) -> List[Dict[str, Any]]:
    _ensure_store()

    lines = path.read_text(encoding="utf-8").splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]


def _audit(event_type: str, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = {
        "event_type": event_type,
        "metadata": metadata or {},
        "created_at": _utc_now(),
    }

    _append_jsonl(STATUS_PAGE_AUDIT_PATH, payload)
    return payload


def register_status_page_service(
    *,
    name: str,
    description: str = "",
    status: str = "operational",
    workspace_id: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    service = ServiceStatus(
        service_id=_id("service"),
        name=name,
        description=description,
        status=status,
        workspace_id=workspace_id,
        metadata=metadata or {},
    )

    payload = asdict(service)
    _append_jsonl(STATUS_PAGE_SERVICES_PATH, payload)

    _audit(
        "status_page_service_registered",
        {
            "service_id": service.service_id,
            "name": name,
            "status": status,
        },
    )

    return payload


def update_service_status(
    *,
    service: Dict[str, Any],
    status: str,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    updated = {
        **service,
        "status": status,
        "metadata": {
            **(service.get("metadata") or {}),
            **(metadata or {}),
        },
        "updated_at": _utc_now(),
    }

    _append_jsonl(STATUS_PAGE_SERVICES_PATH, updated)

    _audit(
        "service_status_updated",
        {
            "service_id": updated.get("service_id"),
            "status": status,
        },
    )

    return updated


def publish_status_page_update(
    *,
    incident_id: str,
    title: str,
    message: str,
    visibility: str = "public",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    update = StatusPageUpdate(
        update_id=_id("status_update"),
        incident_id=incident_id,
        title=title,
        message=message,
        visibility=visibility,
        metadata=metadata or {},
    )

    payload = asdict(update)
    _append_jsonl(STATUS_PAGE_UPDATES_PATH, payload)

    _audit(
        "status_page_update_published",
        {
            "update_id": update.update_id,
            "incident_id": incident_id,
            "visibility": visibility,
        },
    )

    return payload


def read_status_page_services(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(STATUS_PAGE_SERVICES_PATH, limit)


def read_status_page_updates(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(STATUS_PAGE_UPDATES_PATH, limit)


def build_active_incidents_feed() -> List[Dict[str, Any]]:
    incidents = read_incidents(limit=100000)

    return [
        incident
        for incident in incidents
        if str(incident.get("status") or "") not in {"resolved", "closed"}
    ]


def build_historical_incidents_feed() -> List[Dict[str, Any]]:
    incidents = read_incidents(limit=100000)

    return [
        incident
        for incident in incidents
        if str(incident.get("status") or "") in {"resolved", "closed"}
    ]


def build_status_page_payload() -> Dict[str, Any]:
    services = read_status_page_services(limit=100000)
    updates = read_status_page_updates(limit=100000)
    active_incidents = build_active_incidents_feed()
    historical_incidents = build_historical_incidents_feed()

    degraded_services = [
        service
        for service in services
        if str(service.get("status") or "") != "operational"
    ]

    overall_status = "operational"

    if active_incidents or degraded_services:
        overall_status = "degraded"

    if any(str(i.get("severity") or "") == "sev_0" for i in active_incidents):
        overall_status = "major_outage"

    return {
        "overall_status": overall_status,
        "services": services,
        "active_incidents": active_incidents,
        "historical_incidents": historical_incidents,
        "updates": updates,
        "service_count": len(services),
        "active_incident_count": len(active_incidents),
        "historical_incident_count": len(historical_incidents),
        "generated_at": _utc_now(),
    }


def read_status_page_audit(limit: int = 1000) -> List[Dict[str, Any]]:
    return _read_jsonl(STATUS_PAGE_AUDIT_PATH, limit)
