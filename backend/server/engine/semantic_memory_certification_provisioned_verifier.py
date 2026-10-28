"""Phase 3.6.1O: provisioned Semantic Memory trust boundary.

The provisioner must be invoked only by trusted backend bootstrap code,
with independently administered issuer configuration.

No production issuer or signing key is created here.
"""

from collections.abc import Mapping
from types import MappingProxyType

from backend.server.engine.semantic_memory_certification_trusted_handoff import (
    verify_semantic_memory_certification_handoff,
)


class SemanticMemoryTrustConfigurationError(ValueError):
    """Trusted issuer configuration is invalid."""


class ProvisionedSemanticMemoryVerifier:
    """Verifier with an issuer registry fixed at provisioning time.

    This is an internal backend capability, not a public request API.
    Production bootstrap authorization remains an integration requirement.
    """

    __slots__ = ("__trusted_issuers",)

    def __init__(self, *, trusted_issuers):
        if not isinstance(trusted_issuers, Mapping):
            raise SemanticMemoryTrustConfigurationError(
                "Trusted issuer configuration must be a mapping."
            )

        registry = {}

        for issuer_id, entry in trusted_issuers.items():
            if not isinstance(issuer_id, str) or not issuer_id:
                raise SemanticMemoryTrustConfigurationError(
                    "Invalid issuer identity."
                )

            if not isinstance(entry, Mapping):
                raise SemanticMemoryTrustConfigurationError(
                    "Invalid issuer registration."
                )

            if set(entry) != {"key_id", "public_key", "scopes"}:
                raise SemanticMemoryTrustConfigurationError(
                    "Unexpected issuer configuration fields."
                )

            key_id = entry["key_id"]
            public_key = entry["public_key"]
            scopes = entry["scopes"]

            if not isinstance(key_id, str) or not key_id:
                raise SemanticMemoryTrustConfigurationError(
                    "Invalid trusted key identity."
                )

            if not (
                isinstance(public_key, bytes)
                and len(public_key) == 32
            ):
                raise SemanticMemoryTrustConfigurationError(
                    "Invalid Ed25519 public key."
                )

            if not (
                isinstance(scopes, (list, tuple, frozenset))
                and scopes
                and all(
                    isinstance(scope, str) and scope
                    for scope in scopes
                )
            ):
                raise SemanticMemoryTrustConfigurationError(
                    "Invalid trusted issuer scopes."
                )

            registry[issuer_id] = MappingProxyType({
                "key_id": key_id,
                "public_key": bytes(public_key),
                "scopes": tuple(scopes),
            })

        self.__trusted_issuers = MappingProxyType(registry)

    def verify(
        self,
        *,
        workspace_id,
        operational_memory_id,
        canonical_memory_object_id,
        certification_result,
        final_package,
        retrieval_bundle,
        attestation,
    ):
        """Verify using the previously provisioned issuer registry.

        A caller cannot supply trusted_issuers or reference_result here.
        This does not authorize memory consumption.
        """
        return verify_semantic_memory_certification_handoff(
            workspace_id=workspace_id,
            operational_memory_id=operational_memory_id,
            canonical_memory_object_id=canonical_memory_object_id,
            certification_result=certification_result,
            final_package=final_package,
            retrieval_bundle=retrieval_bundle,
            attestation=attestation,
            trusted_issuers=self.__trusted_issuers,
        )
