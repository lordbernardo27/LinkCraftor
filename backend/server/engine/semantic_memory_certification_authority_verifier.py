"""Phase 3.6.1O: independent Semantic Memory issuer verification.

Verifies attestation authenticity only. Does not approve consumption,
workspace binding, record binding, revocation, or semantic truth.
"""

import base64
import binascii
import hmac
import json
import re
from collections.abc import Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)


SCHEMA = "semantic_memory_certification_attestation_v1"
SCOPE = "semantic_memory.certify"
DOMAIN = b'LINKCRAFTOR:SEMANTIC_MEMORY:CERTIFICATION:V1\n'

SIGNED_FIELDS = (
    "schema",
    "issuer_id",
    "key_id",
    "scope",
    "package_id",
    "package_digest",
    "attestation_id",
)

HEX64 = re.compile(r"^[0-9a-f]{64}$")


def canonical_attestation_bytes(claims):
    """Canonical domain-separated bytes for issuer signing.

    Callers must independently validate claims before trusting them.
    """
    if not isinstance(claims, Mapping):
        raise ValueError("Invalid attestation claims")

    if set(claims) != set(SIGNED_FIELDS):
        raise ValueError("Unexpected attestation claims")

    if any(not isinstance(claims[k], str) for k in SIGNED_FIELDS):
        raise ValueError("Attestation claims must be strings")

    serialized = json.dumps(
        dict(claims),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return DOMAIN + serialized.encode("ascii")


def verify_semantic_memory_authority(
    *,
    reference_result,
    final_package,
    attestation,
    trusted_issuers,
):
    """Verify issuer signature, without granting full certification.

    trusted_issuers is an independently provisioned mapping:
      issuer_id -> {
          "key_id": str,
          "public_key": 32-byte Ed25519 public key,
          "scopes": sequence of authorized scope strings,
      }

    It must never be sourced from the untrusted attestation.
    """
    result = {
        "schema": "semantic_memory_authority_verification_result_v1",
        "authority_signature_verified": False,
        "fully_certified": False,
        "consumption_authorized": False,
        "status": "UNVERIFIED",
        "issuer_id": None,
        "attestation_id": None,
        "reason": "evidence_unavailable",
    }

    def reject(reason):
        result["reason"] = reason
        return result

    if not isinstance(reference_result, Mapping):
        return reject("invalid_reference_result")

    if reference_result.get("reference_integrity_valid") is not True:
        return reject("reference_integrity_not_verified")

    if not isinstance(final_package, Mapping):
        return reject("invalid_final_package")

    if not isinstance(attestation, Mapping):
        return reject("evidence_unavailable")

    if not isinstance(trusted_issuers, Mapping):
        return reject("trust_registry_unavailable")

    if set(attestation) != set(SIGNED_FIELDS) | {"signature"}:
        return reject("invalid_attestation_schema")

    claims = {field: attestation[field] for field in SIGNED_FIELDS}

    try:
        message = canonical_attestation_bytes(claims)
    except (TypeError, ValueError, UnicodeError):
        return reject("invalid_attestation_claims")

    if claims["schema"] != SCHEMA:
        return reject("unsupported_attestation_schema")

    if claims["scope"] != SCOPE:
        return reject("unsupported_certification_scope")

    if not (
        claims["issuer_id"]
        and claims["key_id"]
        and claims["attestation_id"]
    ):
        return reject("invalid_attestation_identity")

    if not HEX64.fullmatch(claims["package_digest"]):
        return reject("invalid_package_digest")

    package_id = final_package.get(
        "final_semantic_memory_package_id"
    )
    package_digest = final_package.get(
        "final_semantic_memory_package_digest"
    )

    if not (
        isinstance(package_id, str)
        and isinstance(package_digest, str)
        and HEX64.fullmatch(package_digest)
    ):
        return reject("invalid_final_package_identity")

    if not (
        hmac.compare_digest(claims["package_id"], package_id)
        and hmac.compare_digest(
            claims["package_digest"], package_digest
        )
    ):
        return reject("signed_package_mismatch")

    issuer = trusted_issuers.get(claims["issuer_id"])

    if not isinstance(issuer, Mapping):
        return reject("untrusted_issuer")

    if issuer.get("key_id") != claims["key_id"]:
        return reject("untrusted_key")

    scopes = issuer.get("scopes")

    if (
        not isinstance(scopes, (list, tuple, frozenset))
        or SCOPE not in scopes
    ):
        return reject("issuer_scope_not_authorized")

    public_key_bytes = issuer.get("public_key")

    if (
        not isinstance(public_key_bytes, bytes)
        or len(public_key_bytes) != 32
    ):
        return reject("invalid_trusted_public_key")

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
        public_key = Ed25519PublicKey.from_public_bytes(
            public_key_bytes
        )
        public_key.verify(signature, message)
    except (InvalidSignature, ValueError, TypeError):
        return reject("invalid_signature")

    result.update({
        "authority_signature_verified": True,
        "status": "ISSUER_SIGNATURE_VERIFIED",
        "issuer_id": claims["issuer_id"],
        "attestation_id": claims["attestation_id"],
        "reason": "workspace_record_binding_and_revocation_pending",
    })

    return result
