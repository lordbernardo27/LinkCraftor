
"""PT2C.5.5H ? Signed membership integrity verification."""

from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Mapping
from types import MappingProxyType


OPERATION = "SEMANTIC_MEMORY_CERTIFICATION_CONTEXT_READ"

FIELDS = frozenset({
    "schema_version",
    "principal_id",
    "workspace_id",
    "status",
    "operations",
    "authorization_reference",
    "revision",
})


class MembershipIntegrityDenied(RuntimeError):
    pass


def canonical_bytes(payload):
    if not isinstance(payload, Mapping) or set(payload) != FIELDS:
        raise MembershipIntegrityDenied("Invalid record schema")

    for field in (
        "principal_id",
        "workspace_id",
        "authorization_reference",
    ):
        value = payload[field]
        if (
            type(value) is not str
            or not value.strip()
            or value != value.strip()
        ):
            raise MembershipIntegrityDenied("Invalid identity or provenance")

    if (
        payload["schema_version"] != "workspace_membership_signed_v1"
        or payload["status"] not in ("ACTIVE", "REVOKED")
        or type(payload["operations"]) is not list
        or not all(type(x) is str for x in payload["operations"])
        or len(payload["operations"]) != len(set(payload["operations"]))
        or type(payload["revision"]) is not int
        or payload["revision"] < 1
    ):
        raise MembershipIntegrityDenied("Invalid membership values")

    try:
        return json.dumps(
            dict(payload),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise MembershipIntegrityDenied("Serialization failed") from exc


class MembershipIntegrityVerifier:
    def __init__(self, *, verification_key):
        if (
            type(verification_key) is not bytes
            or len(verification_key) < 32
        ):
            raise MembershipIntegrityDenied(
                "Externally provisioned verification key required"
            )
        self._key = verification_key

    def verify(self, *, envelope, principal_id, workspace_id):
        if (
            not isinstance(envelope, Mapping)
            or set(envelope) != {"payload", "signature", "algorithm"}
        ):
            raise MembershipIntegrityDenied("Signed envelope required")

        if envelope["algorithm"] != "HMAC-SHA256":
            raise MembershipIntegrityDenied("Unsupported algorithm")

        signature = envelope["signature"]
        if (
            type(signature) is not str
            or len(signature) != 64
            or any(c not in "0123456789abcdef" for c in signature)
        ):
            raise MembershipIntegrityDenied("Invalid signature")

        payload = envelope["payload"]
        raw = canonical_bytes(payload)

        expected = hmac.new(
            self._key, raw, hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected):
            raise MembershipIntegrityDenied(
                "Membership signature invalid"
            )

        if (
            type(principal_id) is not str
            or type(workspace_id) is not str
            or payload["principal_id"] != principal_id
            or payload["workspace_id"] != workspace_id
            or payload["status"] != "ACTIVE"
            or OPERATION not in payload["operations"]
        ):
            raise MembershipIntegrityDenied(
                "Membership scope or status denied"
            )

        return MappingProxyType(dict(payload))
