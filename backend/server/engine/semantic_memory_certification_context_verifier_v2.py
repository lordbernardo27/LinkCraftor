"""Phase 3.6.1P: V2 Semantic Memory context signature verification.

Expected identities and trusted issuers MUST originate from trusted
backend resolution, not from an incoming attestation or request.
This primitive never grants certification or consumption.
"""

import base64
import binascii
import hmac
import re
from collections.abc import Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)

from backend.server.engine.semantic_memory_certification_context_v2 import (
    SIGNED_FIELDS_V2,
    SCOPE_V2,
    canonical_context_attestation_bytes_v2,
)

IDENTITY_FIELDS = (
    "workspace_id",
    "operational_memory_id",
    "canonical_memory_object_id",
)
HEX64 = re.compile(r"[0-9a-f]{64}")


def verify_semantic_memory_context_v2(
    *,
    reference_result,
    final_package,
    attestation,
    expected_context,
    trusted_issuers,
):
    """Verify signed V2 context; return a non-authorizing decision."""
    result = {
        "schema": "semantic_memory_context_verification_v2",
        "context_signature_verified": False,
        "context_binding_verified": False,
        "fully_certified": False,
        "consumption_authorized": False,
        "status": "UNVERIFIED",
        "reason": "evidence_unavailable",
    }

    def reject(reason):
        result["reason"] = reason
        return result

    if not isinstance(reference_result, Mapping):
        return reject("reference_result_unavailable")
    if reference_result.get("reference_integrity_valid") is not True:
        return reject("reference_integrity_not_verified")

    if not isinstance(final_package, Mapping):
        return reject("package_unavailable")
    if not isinstance(attestation, Mapping):
        return reject("attestation_unavailable")
    if not isinstance(expected_context, Mapping):
        return reject("trusted_context_unavailable")
    if not isinstance(trusted_issuers, Mapping):
        return reject("trust_registry_unavailable")

    if set(attestation) != set(SIGNED_FIELDS_V2) | {"signature"}:
        return reject("invalid_v2_attestation_schema")

    claims = {
        field: attestation[field]
        for field in SIGNED_FIELDS_V2
    }

    try:
        message = canonical_context_attestation_bytes_v2(claims)
    except (ValueError, TypeError, UnicodeError):
        return reject("invalid_v2_signed_claims")

    if set(expected_context) != set(IDENTITY_FIELDS):
        return reject("invalid_expected_context")

    if any(
        not isinstance(expected_context[field], str)
        or not expected_context[field]
        or expected_context[field] != expected_context[field].strip()
        for field in IDENTITY_FIELDS
    ):
        return reject("invalid_expected_context")

    for field in IDENTITY_FIELDS:
        if not hmac.compare_digest(
            claims[field], expected_context[field]
        ):
            return reject("signed_context_mismatch:" + field)

    package_id = final_package.get(
        "final_semantic_memory_package_id"
    )
    package_digest = final_package.get(
        "final_semantic_memory_package_digest"
    )

    if (
        not isinstance(package_id, str)
        or not package_id
        or not isinstance(package_digest, str)
        or not HEX64.fullmatch(package_digest)
    ):
        return reject("invalid_package_identity")

    if (
        not hmac.compare_digest(claims["package_id"], package_id)
        or not hmac.compare_digest(
            claims["package_digest"], package_digest
        )
    ):
        return reject("signed_package_mismatch")

    issuer_id = claims["issuer_id"]
    issuer = trusted_issuers.get(issuer_id)

    if not isinstance(issuer, Mapping):
        return reject("untrusted_issuer")

    if issuer.get("key_id") != claims["key_id"]:
        return reject("untrusted_key")

    scopes = issuer.get("scopes")
    if (
        not isinstance(scopes, (list, tuple, frozenset))
        or SCOPE_V2 not in scopes
    ):
        return reject("unauthorized_issuer_scope")

    public_key_bytes = issuer.get("public_key")
    if (
        not isinstance(public_key_bytes, bytes)
        or len(public_key_bytes) != 32
    ):
        return reject("invalid_public_key")

    signature_text = attestation.get("signature")
    if not isinstance(signature_text, str):
        return reject("invalid_signature_encoding")

    try:
        signature = base64.b64decode(
            signature_text, validate=True
        )
    except (ValueError, binascii.Error):
        return reject("invalid_signature_encoding")

    if len(signature) != 64:
        return reject("invalid_signature_length")

    try:
        Ed25519PublicKey.from_public_bytes(
            public_key_bytes
        ).verify(signature, message)
    except (InvalidSignature, ValueError, TypeError):
        return reject("invalid_signature")

    result.update({
        "context_signature_verified": True,
        "context_binding_verified": True,
        "status": "SIGNED_CONTEXT_MATCHED",
        "reason": "trusted_resolution_and_revocation_pending",
    })
    return result
