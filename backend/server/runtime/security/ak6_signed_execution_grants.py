"""AK.6: verify externally issued, narrowly scoped worker execution grants.

THIS MODULE CANNOT ISSUE GRANTS. It only verifies signatures using an externally
provisioned Ed25519 public key. The private signing key must stay OUTSIDE the
worker environment and repository. No key or grant => PermissionError.

This is authorization verification, NOT independent worker-process authentication.
Production requires a separately trusted issuer and deployment/IAM controls.
"""
from __future__ import annotations

import base64
import json
import os
import time
from collections.abc import Mapping

from backend.server.runtime.universal_runtime_worker_scope_contract import (
    EXPECTED_SCOPE, STAGES, WORKSPACE_ID, WORKFLOW_ID,
)

WORKER_ID = "universal_runtime_worker_v1"
KEY_ENV = "LC_AK6_AUTHORITY_PUBLIC_KEY_B64"
GRANTS_ENV = "LC_AK6_SIGNED_JOB_GRANTS_JSON"
_MAX_WINDOW_SECONDS = 900


def _decoded(value: str) -> bytes:
    if not isinstance(value, str) or not value or len(value) > 8192:
        raise PermissionError("AK6_DENY_INVALID_ENCODING")
    try:
        return base64.b64decode(value, validate=True)
    except (ValueError, Exception) as exc:
        raise PermissionError("AK6_DENY_INVALID_ENCODING") from exc


def _canonical(payload: Mapping) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def require_signed_ak6_execution_authority(*, job, worker_id: str, action: str, phase: str = "claim") -> str:
    """Deny if grant, job identity, state, or signature cannot be verified.

    Queue invokes this UNDER its claim lock, before registration policy/mutation.
    Handler invokes before either registered handler entry point.
    """
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    if action not in ("claim", "execute") or worker_id != WORKER_ID:
        raise PermissionError("AK6_DENY_WORKER_OR_ACTION")
    if not isinstance(job, Mapping):
        # OrchestrationJob is a canonical dataclass, not a user mapping.
        job_id = getattr(job, "job_id", None)
        workspace_id = getattr(job, "workspace_id", None)
        stage = getattr(job, "job_type", None)
        metadata = getattr(job, "metadata", None)
        status = getattr(job, "status", None)
    else:
        job_id = job.get("job_id")
        workspace_id = job.get("workspace_id")
        stage = job.get("job_type") or job.get("stage")
        metadata = job.get("metadata")
        status = job.get("status")

    if job_id not in EXPECTED_SCOPE or workspace_id != WORKSPACE_ID:
        raise PermissionError("AK6_DENY_JOB_WORKSPACE")
    expected = next((x for x in STAGES if x[1] == job_id), None)
    if expected is None or stage != expected[0] or not isinstance(metadata, Mapping):
        raise PermissionError("AK6_DENY_STAGE_METADATA")
    ref = metadata.get("stage_reference")
    coordination = metadata.get("coordination")
    if not isinstance(ref, Mapping) or not isinstance(coordination, Mapping):
        raise PermissionError("AK6_DENY_LINEAGE_MISSING")
    if (ref.get("handler_ref") != expected[2]
        or ref.get("registration_fingerprint") != expected[3]
        or coordination.get("workflow_id") != WORKFLOW_ID
        or coordination.get("workflow_type") != "connect_domain"):
        raise PermissionError("AK6_DENY_LINEAGE")

    if action == "claim":
        if status != "queued":
            raise PermissionError("AK6_DENY_NOT_QUEUED")
    else:
        # No invocation merely because a caller constructed job mapping.
        if status != "running" or metadata.get("claimed_by_dequeue") is not True:
            raise PermissionError("AK6_DENY_NOT_CLAIMED")
        if metadata.get("worker_id") != WORKER_ID:
            raise PermissionError("AK6_DENY_CLAIM_WORKER")
        if not metadata.get("lease_id") or metadata.get("assigned_worker_id") != WORKER_ID:
            raise PermissionError("AK6_DENY_LEASE_BINDING")

    public_key_b64 = os.environ.get(KEY_ENV, "")
    grants_raw = os.environ.get(GRANTS_ENV, "")
    if not public_key_b64 or not grants_raw:
        raise PermissionError("AK6_DENY_AUTHORITY_UNPROVISIONED")
    raw_public = _decoded(public_key_b64)
    if len(raw_public) != 32 or len(grants_raw) > 120000:
        raise PermissionError("AK6_DENY_AUTHORITY_CONFIG")
    try:
        grants = json.loads(grants_raw)
    except (ValueError, TypeError) as exc:
        raise PermissionError("AK6_DENY_GRANT_DOCUMENT") from exc
    if not isinstance(grants, dict) or set(grants) - EXPECTED_SCOPE:
        raise PermissionError("AK6_DENY_GRANT_COLLECTION")
    envelope = grants.get(job_id)
    if not isinstance(envelope, dict) or set(envelope) != {"payload", "signature"}:
        raise PermissionError("AK6_DENY_GRANT_ABSENT")
    payload = envelope["payload"]
    if not isinstance(payload, dict):
        raise PermissionError("AK6_DENY_GRANT_PAYLOAD")
    required = {"version", "job_id", "workspace_id", "workflow_id", "stage",
                "handler_ref", "registration_fingerprint", "worker_id",
                "not_before", "expires_at", "nonce", "actions"}
    if set(payload) != required:
        raise PermissionError("AK6_DENY_GRANT_FIELDS")
    if (payload["version"] != "AK6-ED25519-v1"
        or payload["job_id"] != job_id
        or payload["workspace_id"] != WORKSPACE_ID
        or payload["workflow_id"] != WORKFLOW_ID
        or payload["stage"] != expected[0]
        or payload["handler_ref"] != expected[2]
        or payload["registration_fingerprint"] != expected[3]
        or payload["worker_id"] != WORKER_ID
        or payload["actions"] != ["claim", "execute"]
        or not isinstance(payload["nonce"], str)
        or len(payload["nonce"]) < 32):
        raise PermissionError("AK6_DENY_GRANT_BINDING")
    start, end = payload["not_before"], payload["expires_at"]
    if (type(start) is not int or type(end) is not int
        or end <= start or end - start > _MAX_WINDOW_SECONDS):
        raise PermissionError("AK6_DENY_WINDOW")
    now = int(time.time())
    if now < start or now >= end:
        raise PermissionError("AK6_DENY_GRANT_EXPIRED")
    signature = _decoded(envelope["signature"])
    if len(signature) != 64:
        raise PermissionError("AK6_DENY_SIGNATURE_FORMAT")
    try:
        Ed25519PublicKey.from_public_bytes(raw_public).verify(signature, _canonical(payload))
    except (InvalidSignature, ValueError) as exc:
        raise PermissionError("AK6_DENY_SIGNATURE_INVALID") from exc
    if action == "execute":
        # AK6_AUTHORITATIVE_PERSISTED_LEASE_ENFORCED
        # Never trust self-declared claimed status or lease metadata.
        from backend.server.runtime.security.ak6_authoritative_lease import (
            require_persisted_ak6_lease,
        )
        require_persisted_ak6_lease(job=job, worker_id=worker_id)
    # AK6_FOUR_CONTROLS_OPERATIONAL_BOUNDARY
    # Attested worker SID, protected pinned issuer, durable replay/revocation.
    from backend.server.runtime.security.ak6_operational_trust import (
        require_operational_ak6_trust,
    )
    return require_operational_ak6_trust(
        job=job, worker_id=worker_id, action=action, phase=phase,
        payload=payload, public_key_bytes=raw_public, nonce=payload["nonce"],
    )
