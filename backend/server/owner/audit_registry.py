
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import json


DATA_ROOT = Path("backend/server/data")


@dataclass(frozen=True)
class UnifiedAuditEvent:
    event_id: str
    event_type: str
    source: str
    severity: str
    timestamp: str
    title: str
    details: Dict[str, Any]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_load_json(path: Path, fallback: Any) -> Any:
    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def _safe_load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    try:
        if not path.exists():
            return rows
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                if isinstance(item, dict):
                    rows.append(item)
            except Exception:
                continue
    except Exception:
        return rows
    return rows


def normalize_audit_event(
    raw: Dict[str, Any],
    *,
    source: str,
    fallback_type: str = "audit_event",
    fallback_severity: str = "info",
) -> UnifiedAuditEvent:
    timestamp = (
        raw.get("timestamp")
        or raw.get("created_at")
        or raw.get("event_time")
        or raw.get("time")
        or _now_iso()
    )

    event_type = str(
        raw.get("event_type")
        or raw.get("type")
        or raw.get("action")
        or fallback_type
    )

    severity = str(
        raw.get("severity")
        or raw.get("level")
        or raw.get("priority")
        or fallback_severity
    ).lower()

    event_id = str(
        raw.get("event_id")
        or raw.get("id")
        or raw.get("job_id")
        or f"{source}:{event_type}:{timestamp}"
    )

    title = str(
        raw.get("title")
        or raw.get("summary")
        or raw.get("message")
        or event_type.replace("_", " ").title()
    )

    return UnifiedAuditEvent(
        event_id=event_id,
        event_type=event_type,
        source=source,
        severity=severity,
        timestamp=str(timestamp),
        title=title,
        details=raw,
    )



def _rows_from_json_file(path: Path) -> List[Dict[str, Any]]:
    data = _safe_load_json(path, [])

    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]

    rows: List[Dict[str, Any]] = []

    if isinstance(data, dict):
        for key in ("items", "events", "tickets", "messages", "notes", "assignments", "status_events"):
            value = data.get(key)
            if isinstance(value, list):
                rows.extend([x for x in value if isinstance(x, dict)])

        if rows:
            return rows

        for parent_id, value in data.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        row = dict(item)
                        row.setdefault("parent_id", parent_id)
                        rows.append(row)
            elif isinstance(value, dict):
                row = dict(value)
                row.setdefault("parent_id", parent_id)
                rows.append(row)

        if rows:
            return rows

        return [data]

    return []


def collect_tms_json_events(limit: int = 100) -> List[UnifiedAuditEvent]:
    files = [
        ("tms_tickets", DATA_ROOT / "tms" / "tickets.json", "ticket_event"),
        ("tms_messages", DATA_ROOT / "tms" / "messages.json", "message_event"),
        ("tms_notes", DATA_ROOT / "tms" / "notes.json", "note_event"),
        ("tms_assignments", DATA_ROOT / "tms" / "assignments.json", "assignment_event"),
        ("tms_status", DATA_ROOT / "tms" / "status_events.json", "status_event"),
    ]

    events: List[UnifiedAuditEvent] = []
    for source, path, fallback_type in files:
        rows = _rows_from_json_file(path)
        for row in rows[-limit:]:
            events.append(
                normalize_audit_event(
                    row,
                    source=source,
                    fallback_type=fallback_type,
                )
            )

    return events[-limit:]

def collect_tms_staff_audit_events(limit: int = 100) -> List[UnifiedAuditEvent]:
    path = DATA_ROOT / "tms" / "staff_audit_log.jsonl"
    rows = _safe_load_jsonl(path)
    return [
        normalize_audit_event(row, source="tms_staff_audit", fallback_type="staff_audit")
        for row in rows[-limit:]
    ]


def collect_tms_email_events(limit: int = 100) -> List[UnifiedAuditEvent]:
    path = DATA_ROOT / "tms" / "email_monitoring" / "email_events.jsonl"
    rows = _safe_load_jsonl(path)
    return [
        normalize_audit_event(row, source="tms_email", fallback_type="email_event")
        for row in rows[-limit:]
    ]


def collect_tms_sla_events(limit: int = 100) -> List[UnifiedAuditEvent]:
    path = DATA_ROOT / "tms" / "sla" / "sla_events.jsonl"
    rows = _safe_load_jsonl(path)
    return [
        normalize_audit_event(row, source="tms_sla", fallback_type="sla_event")
        for row in rows[-limit:]
    ]


def collect_orchestration_job_events(limit: int = 100) -> List[UnifiedAuditEvent]:
    path = DATA_ROOT / "orchestration" / "job_events.json"
    data = _safe_load_json(path, [])
    rows = data if isinstance(data, list) else []
    return [
        normalize_audit_event(row, source="orchestration", fallback_type="job_event")
        for row in rows[-limit:]
        if isinstance(row, dict)
    ]


def collect_workspace_governance_events(limit: int = 100) -> List[UnifiedAuditEvent]:
    gov_dir = DATA_ROOT / "workspace_governance"
    events: List[UnifiedAuditEvent] = []

    if not gov_dir.exists():
        return events

    for path in gov_dir.glob("*_state.json"):
        data = _safe_load_json(path, {})
        if not isinstance(data, dict):
            continue

        recent = data.get("recent_activity", [])
        if not isinstance(recent, list):
            continue

        for row in recent[-limit:]:
            if isinstance(row, dict):
                event = dict(row)
                event.setdefault("workspace_file", path.name)
                events.append(
                    normalize_audit_event(
                        event,
                        source="workspace_governance",
                        fallback_type="workspace_activity",
                    )
                )

    return events[-limit:]


def collect_unified_audit_events(
    limit: int = 250,
    *,
    source: str | None = None,
    severity: str | None = None,
    event_type: str | None = None,
    query: str | None = None,
) -> List[Dict[str, Any]]:
    events: List[UnifiedAuditEvent] = []

    collectors = [
        collect_tms_json_events,
        collect_tms_staff_audit_events,
        collect_tms_email_events,
        collect_tms_sla_events,
        collect_orchestration_job_events,
        collect_workspace_governance_events,
    ]

    for collector in collectors:
        try:
            events.extend(collector(limit=max(limit, 500)))
        except Exception:
            continue

    if source:
        events = [e for e in events if e.source == source]

    if severity:
        sev = severity.lower()
        events = [e for e in events if e.severity.lower() == sev]

    if event_type:
        events = [e for e in events if e.event_type == event_type]

    if query:
        q = query.lower()
        filtered: List[UnifiedAuditEvent] = []
        for event in events:
            haystack = " ".join([
                event.event_id,
                event.event_type,
                event.source,
                event.severity,
                event.timestamp,
                event.title,
                json.dumps(event.details, ensure_ascii=False, default=str),
            ]).lower()
            if q in haystack:
                filtered.append(event)
        events = filtered

    events.sort(key=lambda e: e.timestamp, reverse=True)
    return [asdict(e) for e in events[:limit]]


def get_unified_audit_summary() -> Dict[str, Any]:
    events = collect_unified_audit_events(limit=500)

    by_source: Dict[str, int] = {}
    by_severity: Dict[str, int] = {}

    for event in events:
        by_source[event["source"]] = by_source.get(event["source"], 0) + 1
        by_severity[event["severity"]] = by_severity.get(event["severity"], 0) + 1

    return {
        "total_events": len(events),
        "sources": by_source,
        "severity": by_severity,
        "latest_events": events[:20],
    }



def get_unified_audit_filters() -> Dict[str, Any]:
    events = collect_unified_audit_events(limit=1000)

    sources = sorted({str(event.get("source", "unknown")) for event in events})
    severities = sorted({str(event.get("severity", "info")) for event in events})
    event_types = sorted({str(event.get("event_type", "audit_event")) for event in events})

    return {
        "total_events": len(events),
        "sources": sources,
        "severities": severities,
        "event_types": event_types,
    }



def get_unified_audit_timeline(limit: int = 100) -> Dict[str, Any]:
    events = collect_unified_audit_events(limit=limit)

    timeline = []
    for event in events:
        timeline.append({
            "timestamp": event.get("timestamp"),
            "source": event.get("source"),
            "severity": event.get("severity"),
            "event_type": event.get("event_type"),
            "title": event.get("title"),
            "event_id": event.get("event_id"),
        })

    return {
        "total_events": len(events),
        "timeline": timeline,
    }



def export_unified_audit_events(
    limit: int = 1000,
    *,
    source: str | None = None,
    severity: str | None = None,
    event_type: str | None = None,
    query: str | None = None,
) -> Dict[str, Any]:
    events = collect_unified_audit_events(
        limit=limit,
        source=source,
        severity=severity,
        event_type=event_type,
        query=query,
    )

    return {
        "export_type": "unified_audit_events",
        "format": "json",
        "total_events": len(events),
        "filters": {
            "source": source,
            "severity": severity,
            "event_type": event_type,
            "query": query,
            "limit": limit,
        },
        "events": events,
    }
