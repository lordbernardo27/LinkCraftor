
"""PT5 ? Integrated, fail-closed Semantic Memory trust handoff.

Foundation only. Never grants production consumption.
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from backend.server.engine.semantic_memory_certification_workspace_policy import (
    CERTIFICATION_WORKSPACE_OPERATION,
    ProvisionedCertificationWorkspacePolicy,
)
from backend.server.runtime.security.semantic_memory_canonical_record_ownership import (
    certify_record_ownership,
)
from backend.server.runtime.semantic_memory_certification_issuer_registration import (
    UnprovisionedCertificationIssuerAuthority,
)


class IntegratedTrustHandoffDenied(RuntimeError):
    pass


class SemanticMemoryIntegratedTrustHandoff:
    """Coordinate existing authorities without issuing new trust."""

    def __init__(self, *, workspace_policy, issuer_authority):
        if not isinstance(
            workspace_policy, ProvisionedCertificationWorkspacePolicy
        ):
            raise IntegratedTrustHandoffDenied(
                "Canonical workspace policy required"
            )

        if not isinstance(
            issuer_authority, UnprovisionedCertificationIssuerAuthority
        ):
            raise IntegratedTrustHandoffDenied(
                "Registered issuer authority required"
            )

        self._workspace_policy = workspace_policy
        self._issuer_authority = issuer_authority

    def evaluate(
        self,
        *,
        request_lookup,
        workspace_id,
        record,
        record_id,
    ) -> Mapping:
        """Deny unless every prerequisite can be established.

        Current PT4 issuer is deliberately unprovisioned. Consequently
        this handoff never authorizes production consumption.
        """

        try:
            access = self._workspace_policy.evaluate(
                request_lookup=request_lookup,
                workspace_id=workspace_id,
                operation=CERTIFICATION_WORKSPACE_OPERATION,
            )

            if (
                not isinstance(access, Mapping)
                or access.get("workspace_id") != workspace_id
                or access.get("workspace_evidence_matched") is not True
            ):
                raise IntegratedTrustHandoffDenied(
                    "Workspace authorization mismatch"
                )

            ownership = certify_record_ownership(
                record=record,
                expected_workspace_id=workspace_id,
                expected_record_id=record_id,
            )

            if ownership.get("ownership_verified") is not True:
                raise IntegratedTrustHandoffDenied(
                    "Record ownership not established"
                )

            # No attacker-controlled registry, verifier or issuer
            # is accepted as an evaluate() argument.
            self._issuer_authority.verify()

        except Exception as exc:
            raise IntegratedTrustHandoffDenied(
                "Integrated certification trust unavailable"
            ) from exc

        # Defense in depth: even if the authority implementation
        # changes, PT5 cannot independently enable consumption.
        return MappingProxyType({
            "workspace_id": workspace_id,
            "record_id": record_id,
            "fully_certified": False,
            "consumption_authorized": False,
        })
