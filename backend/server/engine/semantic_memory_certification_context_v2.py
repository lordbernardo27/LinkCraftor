"""Phase 3.6.1P: versioned signed Semantic Memory context contract.

Defines bytes for V2 Ed25519 attestations.
Does not issue certificates or authorize consumption.
"""

import json
import re
from collections.abc import Mapping

SCHEMA_V2 = "semantic_memory_certification_attestation_v2"
SCOPE_V2 = "semantic_memory.certify"
DOMAIN_V2 = (
    b"LINKCRAFTOR:SEMANTIC_MEMORY:CERTIFICATION:V2"
    + bytes([10])
)

SIGNED_FIELDS_V2 = (
    "schema",
    "issuer_id",
    "key_id",
    "scope",
    "attestation_id",
    "workspace_id",
    "operational_memory_id",
    "canonical_memory_object_id",
    "package_id",
    "package_digest",
)

_DIGEST = re.compile(r"[0-9a-f]{64}")
_WORKSPACE = re.compile(r"[A-Za-z0-9_-]+")


def canonical_context_attestation_bytes_v2(claims):
    """Return deterministic signed bytes for a validated V2 context."""
    if not isinstance(claims, Mapping):
        raise ValueError("V2 claims must be a mapping")

    if set(claims) != set(SIGNED_FIELDS_V2):
        raise ValueError("Unexpected or missing V2 signed fields")

    if any(
        not isinstance(claims[field], str)
        or not claims[field]
        or claims[field] != claims[field].strip()
        for field in SIGNED_FIELDS_V2
    ):
        raise ValueError("Invalid V2 claim value")

    if claims["schema"] != SCHEMA_V2:
        raise ValueError("Unsupported V2 attestation schema")

    if claims["scope"] != SCOPE_V2:
        raise ValueError("Unsupported V2 certification scope")

    if not _WORKSPACE.fullmatch(claims["workspace_id"]):
        raise ValueError("Invalid signed workspace identity")

    if not _DIGEST.fullmatch(claims["package_digest"]):
        raise ValueError("Invalid signed package digest")

    encoded = json.dumps(
        dict(claims),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")

    return DOMAIN_V2 + encoded
