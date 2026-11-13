from __future__ import annotations

"""Protected Owner Actions & Recovery request gateway.

This module is separate from monitoring projections. Preview is read-only. Mutation
dispatch is disabled by default and cannot occur unless a trusted server-side adapter,
owner identity, signed grant and explicit activation have all been provisioned.
"""

# PART F 15-B6B THROUGH 15-B6I OWNER ACTIONS AND RECOVERY

import hashlib
import hmac
import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from backend.server.owner.runtime_infrastructure_projection import (
    build_runtime_infrastructure_snapshot,
)


OWNER_ACTION_GATEWAY_VERSION = "owner_action_gateway_v1.0.0"
OWNER_ACTION_SCHEMA_VERSION = "owner_action_request_schema_v1"
OWNER_ACTIONS_ENABLED_ENV = "LINKCRAFTOR_OWNER_ACTIONS_ENABLED"
OWNER_ACTION_SECRET_ENV = "LINKCRAFTOR_OWNER_ACTION_SIGNING_SECRET"
OWNER_ACTION_ISSUER_ENV = "LINKCRAFTOR_OWNER_ACTION_TRUSTED_ISSUER"

ACTION_CONTRACTS: dict[str, dict[str, Any]] = {
    "job_claim": {
        "family": "jobs_queues", "states": {"queued"}, "risk": "HIGH",
        "result": "Assign one eligible queued job through canonical claim authority.",
        "impact": ["May assign worker ownership.", "May create a lease.", "Must revalidate queue eligibility atomically."],
    },
    "job_retry": {
        "family": "jobs_queues", "states": {"failed"}, "risk": "HIGH",
        "result": "Create one authorized retry attempt for a failed job.",
        "impact": ["May enqueue a new attempt.", "Must preserve attempt limits.", "Must not erase failure evidence."],
    },
    "job_requeue": {
        "family": "jobs_queues", "states": {"failed", "cancelled", "canceled"}, "risk": "HIGH",
        "result": "Return an eligible job to its canonical queue.",
        "impact": ["May make work claimable again.", "Must prevent duplicate queue entries.", "Requires fresh dependency checks."],
    },
    "job_cancel": {
        "family": "jobs_queues", "states": {"queued", "running", "in_progress", "processing"}, "risk": "HIGH",
        "result": "Request cancellation of one non-terminal job.",
        "impact": ["May stop future processing.", "Running work may require cooperative cancellation.", "Existing evidence remains retained."],
    },
    "workflow_retry": {
        "family": "workflows_stages", "states": {"failed"}, "risk": "HIGH",
        "result": "Retry eligible failed work in one workflow.",
        "impact": ["May create new job attempts.", "Completed stages remain immutable.", "Dependencies must be revalidated."],
    },
    "workflow_cancel": {
        "family": "workflows_stages", "states": {"active", "running", "queued", "failed"}, "risk": "CRITICAL",
        "result": "Request cancellation of remaining workflow work.",
        "impact": ["May affect multiple jobs.", "Completed outputs remain retained.", "Requires critical confirmation."],
    },
    "stage_recover": {
        "family": "workflows_stages", "states": {"failed", "blocked"}, "risk": "CRITICAL",
        "result": "Request recovery of one eligible failed or blocked stage.",
        "impact": ["May enqueue replacement work.", "Must preserve stage ordering.", "Must not bypass predecessor requirements."],
    },
    "lease_release": {
        "family": "workers_leases", "states": {"expired", "stale"}, "risk": "CRITICAL",
        "result": "Release one canonically expired or stale lease.",
        "impact": ["May make work claimable again.", "Must prove lease expiry atomically.", "Active leases cannot be released."],
    },
    "worker_drain": {
        "family": "workers_leases", "states": {"active", "busy", "idle"}, "risk": "CRITICAL",
        "result": "Prevent a worker from receiving new work while preserving active work.",
        "impact": ["Reduces available worker capacity.", "Does not terminate active work.", "Requires trusted worker authority."],
    },
    "execution_cancel": {
        "family": "executions", "states": {"running", "in_progress", "processing"}, "risk": "CRITICAL",
        "result": "Request cooperative cancellation of one active execution.",
        "impact": ["May stop an active handler.", "Partial work may remain.", "Compensation requirements must be recorded."],
    },
    "execution_terminate": {
        "family": "executions", "states": {"running", "in_progress", "processing"}, "risk": "CRITICAL",
        "result": "Request forced termination only through certified execution authority.",
        "impact": ["May interrupt work immediately.", "May require compensation or cleanup.", "Highest confirmation level required."],
    },
}

TARGET_NAMESPACE = {
    "jobs_queues": "jobs",
    "workflows_stages": "orchestration",
    "workers_leases": "workers_leases",
    "executions": "execution",
}

IDENTITY_FIELDS = (
    "job_id", "job_identity", "workflow_id", "workflow_identity", "worker_identity",
    "worker_id", "lease_identity", "execution_identity", "queue_identity", "queue_name",
)
STATE_FIELDS = ("status", "state", "lifecycle", "lease_status", "execution_status")
REQUIRED_REQUEST_FIELDS = (
    "action_type", "target_type", "target_id", "expected_state", "reason",
    "confirmation", "confirmation_token", "idempotency_key",
)

_ADAPTERS: dict[str, Callable[[Mapping[str, Any]], Mapping[str, Any]]] = {}
_IDEMPOTENCY: dict[str, Mapping[str, Any]] = {}
_LOCK = threading.RLock()


class OwnerActionValidationError(ValueError):
    pass


class OwnerActionBlocked(RuntimeError):
    def __init__(self, code: str, message: str, **evidence: Any) -> None:
        self.detail = {
            "error": code,
            "message": message,
            "action_executed": False,
            **evidence,
        }
        super().__init__(message)


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _normalized_state(value: Any) -> str:
    return _text(value).lower().replace(" ", "_") or "unavailable"


def _record_identity(record: Mapping[str, Any]) -> str:
    for field in IDENTITY_FIELDS:
        value = _text(record.get(field))
        if value:
            return value
    return ""


def _record_state(record: Mapping[str, Any]) -> str:
    for field in STATE_FIELDS:
        value = _normalized_state(record.get(field))
        if value != "unavailable":
            return value
    return "unavailable"


def _find_target(snapshot: Mapping[str, Any], target_type: str, target_id: str) -> Mapping[str, Any]:
    namespace_name = TARGET_NAMESPACE.get(target_type)
    if not namespace_name:
        raise OwnerActionValidationError("Unknown target_type.")
    namespace = snapshot.get(namespace_name, {})
    records = namespace.get("records", []) if isinstance(namespace, Mapping) else []
    if not isinstance(records, list):
        raise OwnerActionBlocked("target_evidence_unavailable", "Canonical target evidence is unavailable.")
    for value in records:
        if isinstance(value, Mapping) and _record_identity(value) == target_id:
            return dict(value)
    raise OwnerActionBlocked("target_not_found", "The target is absent from the fresh canonical snapshot.")


def _confirmation_phrase(action_type: str, target_id: str) -> str:
    return f"CONFIRM {action_type.upper()} {target_id}"


def _token(secret: str, action_type: str, target_id: str, state: str) -> str:
    message = f"{action_type}|{target_id}|{state}|{OWNER_ACTION_SCHEMA_VERSION}".encode()
    return hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()


def _preview(payload: Mapping[str, Any], snapshot: Mapping[str, Any]) -> dict[str, Any]:
    action_type = _text(payload.get("action_type"))
    target_type = _text(payload.get("target_type"))
    target_id = _text(payload.get("target_id"))
    expected_state = _normalized_state(payload.get("expected_state"))
    if not action_type or not target_type or not target_id:
        raise OwnerActionValidationError("action_type, target_type and target_id are required.")
    contract = ACTION_CONTRACTS.get(action_type)
    if not contract or contract["family"] != target_type:
        raise OwnerActionValidationError("The action is not valid for the selected target family.")
    record = _find_target(snapshot, target_type, target_id)
    current_state = _record_state(record)
    eligible = current_state in contract["states"]
    if expected_state not in {"unavailable", current_state}:
        eligible = False
        blocked_reason = "Expected state does not match fresh canonical evidence."
    elif not eligible:
        blocked_reason = f"State {current_state!r} is not eligible for {action_type}."
    else:
        blocked_reason = None
    secret = os.environ.get(OWNER_ACTION_SECRET_ENV, "preview-only-not-a-dispatch-secret")
    return {
        "gateway_version": OWNER_ACTION_GATEWAY_VERSION,
        "schema_version": OWNER_ACTION_SCHEMA_VERSION,
        "preview_only": True,
        "action_executed": False,
        "action_type": action_type,
        "target_type": target_type,
        "target_id": target_id,
        "current_state": current_state,
        "eligible": eligible,
        "blocked_reason": blocked_reason,
        "risk_level": contract["risk"],
        "expected_result": contract["result"],
        "impact": list(contract["impact"]),
        "confirmation_phrase": _confirmation_phrase(action_type, target_id),
        "confirmation_token": _token(secret, action_type, target_id, current_state),
    }


def preview_owner_action(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping):
        raise OwnerActionValidationError("The preview payload must be an object.")
    return _preview(payload, build_runtime_infrastructure_snapshot())


def register_owner_action_adapter(
    action_type: str,
    adapter: Callable[[Mapping[str, Any]], Mapping[str, Any]],
) -> None:
    """Server-only adapter registration; browser requests cannot register adapters."""
    if action_type not in ACTION_CONTRACTS or not callable(adapter):
        raise OwnerActionValidationError("Invalid owner action adapter registration.")
    with _LOCK:
        _ADAPTERS[action_type] = adapter


def _audit(event: Mapping[str, Any]) -> None:
    root = Path(__file__).resolve().parents[3]
    path = root / "backend/server/data/audit/owner_actions.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(dict(event), sort_keys=True, default=str) + "\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())


def submit_owner_action(payload: Mapping[str, Any], headers: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping) or not isinstance(headers, Mapping):
        raise OwnerActionValidationError("Action payload and request headers are required.")
    missing = [field for field in REQUIRED_REQUEST_FIELDS if not _text(payload.get(field))]
    if missing:
        raise OwnerActionValidationError(f"Missing required action fields: {', '.join(missing)}")

    request_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    idempotency_key = _text(payload["idempotency_key"])
    header_key = _text(headers.get("x-linkcraftor-idempotency-key"))
    if header_key != idempotency_key:
        raise OwnerActionBlocked("idempotency_mismatch", "Header and payload idempotency keys differ.", request_id=request_id)

    with _LOCK:
        previous = _IDEMPOTENCY.get(idempotency_key)
        if previous is not None:
            return dict(previous)

    snapshot = build_runtime_infrastructure_snapshot()
    preview = _preview(payload, snapshot)
    if not preview["eligible"]:
        raise OwnerActionBlocked("fresh_eligibility_failed", preview["blocked_reason"], request_id=request_id)
    if _normalized_state(payload["expected_state"]) != preview["current_state"]:
        raise OwnerActionBlocked("state_conflict", "Target state changed after preview.", request_id=request_id)
    if _text(payload["confirmation"]) != preview["confirmation_phrase"]:
        raise OwnerActionBlocked("confirmation_failed", "The confirmation phrase does not match.", request_id=request_id)

    secret = os.environ.get(OWNER_ACTION_SECRET_ENV, "")
    if not secret:
        raise OwnerActionBlocked("trusted_secret_unavailable", "Owner action signing authority is not provisioned.", request_id=request_id)
    expected_token = _token(secret, preview["action_type"], preview["target_id"], preview["current_state"])
    if not hmac.compare_digest(_text(payload["confirmation_token"]), expected_token):
        raise OwnerActionBlocked("preview_token_invalid", "The preview token is invalid or stale.", request_id=request_id)
    if os.environ.get(OWNER_ACTIONS_ENABLED_ENV) != "1":
        raise OwnerActionBlocked("owner_actions_disabled", "Live owner action dispatch is disabled.", request_id=request_id)

    principal = _text(headers.get("x-linkcraftor-owner-principal"))
    issuer = _text(headers.get("x-linkcraftor-owner-issuer"))
    expected_issuer = os.environ.get(OWNER_ACTION_ISSUER_ENV, "")
    if not principal or not expected_issuer or issuer != expected_issuer:
        raise OwnerActionBlocked("owner_authorization_failed", "Trusted owner identity is absent or invalid.", request_id=request_id)

    adapter = _ADAPTERS.get(preview["action_type"])
    if adapter is None:
        raise OwnerActionBlocked("certified_adapter_unavailable", "No certified server-side mutation adapter is registered.", request_id=request_id)

    request = {
        **dict(payload),
        "request_id": request_id,
        "owner_principal": principal,
        "submitted_at": now,
        "fresh_preview": preview,
    }
    _audit({"event": "owner_action_authorized", **request, "action_executed": False})
    result = dict(adapter(request))
    response = {
        "request_id": request_id,
        "status": _text(result.get("status")) or "COMPLETED",
        "action_type": preview["action_type"],
        "target_id": preview["target_id"],
        "action_executed": True,
        "result": result,
    }
    _audit({"event": "owner_action_completed", **response, "owner_principal": principal})
    with _LOCK:
        _IDEMPOTENCY[idempotency_key] = dict(response)
    return response


def certify_owner_action_gateway_v1() -> Mapping[str, Any]:
    return {
        "gateway_version": OWNER_ACTION_GATEWAY_VERSION,
        "schema_version": OWNER_ACTION_SCHEMA_VERSION,
        "action_contract_count": len(ACTION_CONTRACTS),
        "required_request_fields": list(REQUIRED_REQUEST_FIELDS),
        "activation_default_off": os.environ.get(OWNER_ACTIONS_ENABLED_ENV) != "1",
        "registered_adapter_count": len(_ADAPTERS),
        "preview_is_read_only": True,
        "direct_browser_mutation": False,
    }


__all__ = [
    "ACTION_CONTRACTS",
    "OwnerActionBlocked",
    "OwnerActionValidationError",
    "certify_owner_action_gateway_v1",
    "preview_owner_action",
    "register_owner_action_adapter",
    "submit_owner_action",
]
