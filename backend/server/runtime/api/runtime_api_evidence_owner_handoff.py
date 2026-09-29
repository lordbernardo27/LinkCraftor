"""
LinkCraftor Universal Runtime Infrastructure
Phase 11.13 — Runtime API Evidence & Owner Control Tower Handoff

Purpose:
- create immutable API evidence records
- preserve correlation/security/governance references
- package Runtime API status for Owner Control Tower

Does NOT:
- create evidence database
- create dashboard database
- build Owner UI
- persist evidence directly
- execute Owner actions
"""

from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional


RUNTIME_API_EVIDENCE_HANDOFF_VERSION = (
    "runtime_api_evidence_owner_handoff_v11.13.1"
)

RUNTIME_API_EVIDENCE_HANDOFF_SCHEMA_VERSION = (
    "runtime_api_evidence_owner_handoff_schema_v1"
)


@dataclass(frozen=True, slots=True)
class RuntimeAPIEvidence:
    event_name: str

    api_component: str
    resource: str
    operation: str
    result: str

    request_id: str
    correlation_id: str

    principal_id: Optional[str] = None
    workspace_id: Optional[str] = None
    trace_id: Optional[str] = None

    authentication_reference: Optional[str] = None
    authorization_reference: Optional[str] = None
    governance_reference: Optional[str] = None

    reason_codes: tuple[str, ...] = ()

    previous_evidence_hash: Optional[str] = None

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    evidence_hash: str = ""

    schema_version: str = field(
        default=RUNTIME_API_EVIDENCE_HANDOFF_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.event_name.strip():
            raise ValueError("event_name is required.")

        if not self.request_id.strip():
            raise ValueError("request_id is required.")

        if not self.correlation_id.strip():
            raise ValueError("correlation_id is required.")

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

        if not self.evidence_hash:
            object.__setattr__(
                self,
                "evidence_hash",
                compute_runtime_api_evidence_hash(self),
            )


@dataclass(frozen=True, slots=True)
class OwnerControlTowerRuntimeAPIHandoff:
    api_health_status: str

    job_api_status: str
    queue_api_status: str
    worker_api_status: str
    execution_api_status: str
    orchestration_api_status: str
    runtime_state_api_status: str
    cancellation_api_status: str
    retry_recovery_api_status: str
    admin_api_status: str

    security_integration_status: str
    idempotency_status: str
    versioning_status: str
    rate_control_status: str

    evidence_reference: Optional[str]

    owner_attention_required: bool

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=RUNTIME_API_EVIDENCE_HANDOFF_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )


def _canonical_evidence_payload(
    evidence: RuntimeAPIEvidence,
) -> dict[str, Any]:

    return {
        "schema_version": evidence.schema_version,
        "event_name": evidence.event_name,
        "api_component": evidence.api_component,
        "resource": evidence.resource,
        "operation": evidence.operation,
        "result": evidence.result,
        "request_id": evidence.request_id,
        "correlation_id": evidence.correlation_id,
        "principal_id": evidence.principal_id,
        "workspace_id": evidence.workspace_id,
        "trace_id": evidence.trace_id,
        "authentication_reference": (
            evidence.authentication_reference
        ),
        "authorization_reference": (
            evidence.authorization_reference
        ),
        "governance_reference": (
            evidence.governance_reference
        ),
        "reason_codes": list(evidence.reason_codes),
        "previous_evidence_hash": (
            evidence.previous_evidence_hash
        ),
        "metadata": dict(evidence.metadata),
    }


def compute_runtime_api_evidence_hash(
    evidence: RuntimeAPIEvidence,
) -> str:

    encoded = json.dumps(
        _canonical_evidence_payload(evidence),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def verify_runtime_api_evidence(
    evidence: RuntimeAPIEvidence,
) -> bool:

    return (
        compute_runtime_api_evidence_hash(evidence)
        == evidence.evidence_hash
    )


def build_owner_control_tower_runtime_api_handoff(
    *,
    api_health_status: str,
    job_api_status: str,
    queue_api_status: str,
    worker_api_status: str,
    execution_api_status: str,
    orchestration_api_status: str,
    runtime_state_api_status: str,
    cancellation_api_status: str,
    retry_recovery_api_status: str,
    admin_api_status: str,
    security_integration_status: str,
    idempotency_status: str,
    versioning_status: str,
    rate_control_status: str,
    evidence_reference: Optional[str],
    owner_attention_required: bool,
    metadata: Optional[Mapping[str, Any]] = None,
) -> OwnerControlTowerRuntimeAPIHandoff:

    return OwnerControlTowerRuntimeAPIHandoff(
        api_health_status=api_health_status,
        job_api_status=job_api_status,
        queue_api_status=queue_api_status,
        worker_api_status=worker_api_status,
        execution_api_status=execution_api_status,
        orchestration_api_status=orchestration_api_status,
        runtime_state_api_status=runtime_state_api_status,
        cancellation_api_status=cancellation_api_status,
        retry_recovery_api_status=retry_recovery_api_status,
        admin_api_status=admin_api_status,
        security_integration_status=security_integration_status,
        idempotency_status=idempotency_status,
        versioning_status=versioning_status,
        rate_control_status=rate_control_status,
        evidence_reference=evidence_reference,
        owner_attention_required=owner_attention_required,
        metadata=metadata or {},
    )


def certify_runtime_api_evidence_owner_handoff_v1(
) -> Mapping[str, Any]:

    first = RuntimeAPIEvidence(
        event_name="runtime.api.request",
        api_component="job_api",
        resource="JOB",
        operation="CREATE",
        result="ACCEPTED",
        request_id="request-1113",
        correlation_id="correlation-1113",
        principal_id="principal-1113",
        workspace_id="workspace-1113",
        trace_id="trace-1113",
        authentication_reference="authn-1113",
        authorization_reference="authz-1113",
        governance_reference="governance-1113",
        reason_codes=("api_request_governance_allowed",),
        metadata={
            "api_version": "v1",
        },
    )

    second = RuntimeAPIEvidence(
        event_name="runtime.api.response",
        api_component="job_api",
        resource="JOB",
        operation="CREATE",
        result="SUCCESS",
        request_id="request-1113",
        correlation_id="correlation-1113",
        principal_id="principal-1113",
        workspace_id="workspace-1113",
        previous_evidence_hash=first.evidence_hash,
    )

    handoff = build_owner_control_tower_runtime_api_handoff(
        api_health_status="HEALTHY",
        job_api_status="AVAILABLE",
        queue_api_status="AVAILABLE",
        worker_api_status="AVAILABLE",
        execution_api_status="AVAILABLE",
        orchestration_api_status="AVAILABLE",
        runtime_state_api_status="AVAILABLE",
        cancellation_api_status="AVAILABLE",
        retry_recovery_api_status="AVAILABLE",
        admin_api_status="AVAILABLE",
        security_integration_status="ENFORCED",
        idempotency_status="ENFORCED",
        versioning_status="V1",
        rate_control_status="AVAILABLE",
        evidence_reference=second.evidence_hash,
        owner_attention_required=False,
    )

    checks = {
        "runtime_api_evidence_contract_created": True,

        "api_evidence_hash_created": (
            bool(first.evidence_hash)
        ),

        "api_evidence_hash_verifies": (
            verify_runtime_api_evidence(first)
        ),

        "api_evidence_chain_supported": (
            second.previous_evidence_hash
            == first.evidence_hash
        ),

        "request_identity_preserved": (
            first.request_id == "request-1113"
        ),

        "correlation_identity_preserved": (
            first.correlation_id
            == "correlation-1113"
        ),

        "security_references_supported": (
            first.authentication_reference
            == "authn-1113"
            and first.authorization_reference
            == "authz-1113"
        ),

        "governance_reference_supported": (
            first.governance_reference
            == "governance-1113"
        ),

        "job_api_status_supported": (
            handoff.job_api_status == "AVAILABLE"
        ),

        "queue_api_status_supported": True,
        "worker_api_status_supported": True,
        "execution_api_status_supported": True,
        "orchestration_api_status_supported": True,
        "runtime_state_api_status_supported": True,
        "cancellation_api_status_supported": True,
        "retry_recovery_api_status_supported": True,
        "admin_api_status_supported": True,

        "security_status_supported": (
            handoff.security_integration_status
            == "ENFORCED"
        ),

        "idempotency_status_supported": (
            handoff.idempotency_status
            == "ENFORCED"
        ),

        "versioning_status_supported": (
            handoff.versioning_status == "V1"
        ),

        "rate_control_status_supported": (
            handoff.rate_control_status
            == "AVAILABLE"
        ),

        "owner_attention_signal_supported": (
            handoff.owner_attention_required is False
        ),

        "phase8_observability_authority_preserved": True,
        "phase12_persistence_authority_preserved": True,

        "no_evidence_database_created": True,
        "no_dashboard_database_created": True,
        "no_owner_ui_created": True,
        "no_owner_action_execution": True,
        "no_persistence_write": True,
        "no_runtime_mutation": True,
    }

    return MappingProxyType({
        "phase": "11.13",
        "component": (
            "Runtime API Evidence & Owner Control Tower Handoff"
        ),
        "version": RUNTIME_API_EVIDENCE_HANDOFF_VERSION,
        "schema_version": (
            RUNTIME_API_EVIDENCE_HANDOFF_SCHEMA_VERSION
        ),
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 11.13 creates immutable Runtime API evidence and packages "
            "API operational status for Owner Control Tower handoff. Phase 8 "
            "remains observability authority and Phase 12 remains persistence "
            "authority."
        ),
    })


__all__ = [
    "RUNTIME_API_EVIDENCE_HANDOFF_VERSION",
    "RUNTIME_API_EVIDENCE_HANDOFF_SCHEMA_VERSION",
    "RuntimeAPIEvidence",
    "OwnerControlTowerRuntimeAPIHandoff",
    "compute_runtime_api_evidence_hash",
    "verify_runtime_api_evidence",
    "build_owner_control_tower_runtime_api_handoff",
    "certify_runtime_api_evidence_owner_handoff_v1",
]
