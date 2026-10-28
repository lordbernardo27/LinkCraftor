"""Phase 3.6.1P: provisioned V2 context-verification entry point.

Internal capability. Trusted backend bootstrap must provide both the
issuer registry and an independently authorized context resolver.
Never expose construction or configuration to untrusted callers.
"""

from collections.abc import Mapping
from types import MappingProxyType

from backend.server.engine.semantic_memory_certification_provisioned_verifier import (
    SemanticMemoryTrustConfigurationError,
)
from backend.server.engine.semantic_memory_certification_context_handoff_v2 import (
    verify_semantic_memory_context_handoff_v2,
)


class ProvisionedSemanticMemoryContextVerifierV2:
    """Resolve expected identities and use a fixed trust registry."""

    __slots__ = ("__resolver", "__trusted_issuers")

    def __init__(self, *, trusted_issuers, context_resolver):
        if not callable(context_resolver):
            raise ValueError("Trusted context resolver is required")

        if not isinstance(trusted_issuers, Mapping):
            raise SemanticMemoryTrustConfigurationError(
                "Trusted issuer registry must be a mapping"
            )

        registry = {}

        for issuer_id, entry in trusted_issuers.items():
            if not isinstance(issuer_id, str) or not issuer_id:
                raise SemanticMemoryTrustConfigurationError(
                    "Invalid issuer identity"
                )

            if not isinstance(entry, Mapping):
                raise SemanticMemoryTrustConfigurationError(
                    "Invalid issuer entry"
                )

            if set(entry) != {"key_id", "public_key", "scopes"}:
                raise SemanticMemoryTrustConfigurationError(
                    "Unexpected issuer registration fields"
                )

            key_id = entry["key_id"]
            key = entry["public_key"]
            scopes = entry["scopes"]

            if not isinstance(key_id, str) or not key_id:
                raise SemanticMemoryTrustConfigurationError(
                    "Invalid key identity"
                )

            if not isinstance(key, bytes) or len(key) != 32:
                raise SemanticMemoryTrustConfigurationError(
                    "Invalid Ed25519 public key"
                )

            if not isinstance(scopes, (list, tuple, frozenset)):
                raise SemanticMemoryTrustConfigurationError(
                    "Invalid issuer scopes"
                )

            if not scopes or any(
                not isinstance(scope, str) or not scope
                for scope in scopes
            ):
                raise SemanticMemoryTrustConfigurationError(
                    "Invalid issuer scope value"
                )

            registry[issuer_id] = MappingProxyType({
                "key_id": key_id,
                "public_key": bytes(key),
                "scopes": tuple(scopes),
            })

        self.__trusted_issuers = MappingProxyType(registry)
        self.__resolver = context_resolver

    def verify(
        self,
        *,
        record_lookup,
        certification_result,
        final_package,
        retrieval_bundle,
        attestation,
    ):
        """Use trusted resolution rather than request-supplied context.

        record_lookup is a selector, not proof of ownership. The resolver
        must authorize the request using backend-controlled identity.
        """
        denied = {
            "schema": "semantic_memory_provisioned_context_result_v2",
            "status": "TRUSTED_CONTEXT_UNAVAILABLE",
            "reference_integrity_valid": False,
            "context_signature_verified": False,
            "context_binding_verified": False,
            "fully_certified": False,
            "consumption_authorized": False,
        }

        try:
            resolved = self.__resolver(record_lookup)
        except Exception:
            return denied

        required = {
            "workspace_id",
            "operational_memory_id",
            "canonical_memory_object_id",
        }

        if not isinstance(resolved, Mapping):
            return denied

        if set(resolved) != required or any(
            not isinstance(resolved[field], str)
            or not resolved[field]
            or resolved[field] != resolved[field].strip()
            for field in required
        ):
            return denied

        context = {
            field: resolved[field]
            for field in required
        }

        return verify_semantic_memory_context_handoff_v2(
            expected_context=context,
            certification_result=certification_result,
            final_package=final_package,
            retrieval_bundle=retrieval_bundle,
            attestation=attestation,
            trusted_issuers=self.__trusted_issuers,
        )
