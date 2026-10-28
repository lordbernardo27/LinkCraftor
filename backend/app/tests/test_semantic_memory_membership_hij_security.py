
"""PT2C.5.5H-I-J combined security regression tests."""

import hashlib
import hmac
import json

import pytest

from backend.server.runtime.security.semantic_memory_membership_integrity import (
    OPERATION,
    MembershipIntegrityDenied,
    MembershipIntegrityVerifier,
    canonical_bytes,
)
from backend.server.runtime.security.semantic_memory_membership_revision import (
    MembershipRevisionDenied,
    ProvisionedMembershipRevisionAuthority,
)
from backend.server.runtime.security.semantic_memory_verified_membership_provider import (
    VerifiedMembershipUnavailable,
    VerifiedWorkspaceMembershipResolver,
)


KEY = b"synthetic-security-test-key-0000000000000001"


def payload(revision=1):
    return {
        "schema_version": "workspace_membership_signed_v1",
        "principal_id": "principal-a",
        "workspace_id": "ws_a",
        "status": "ACTIVE",
        "operations": [OPERATION],
        "authorization_reference": "synthetic-only",
        "revision": revision,
    }


def signed(record):
    return {
        "algorithm": "HMAC-SHA256",
        "payload": record,
        "signature": hmac.new(
            KEY, canonical_bytes(record), hashlib.sha256
        ).hexdigest(),
    }


def setup(tmp_path, state=None):
    ws = tmp_path / "workspaces"
    memberships = tmp_path / "memberships"
    (ws / "ws_a").mkdir(parents=True)
    memberships.mkdir()

    (ws / "ws_a" / "workspace_profile.json").write_text(
        json.dumps({
            "schema_version": "workspace_profile_v2",
            "workspace_id": "ws_a",
            "connection_status": "connected",
        }),
        encoding="utf-8",
    )

    record_id = hashlib.sha256(
        json.dumps(
            ["ws_a", "principal-a"],
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    path = memberships / (record_id + ".json")
    path.write_text(
        json.dumps(signed(payload())),
        encoding="utf-8",
    )

    state = state or {
        "principal_id": "principal-a",
        "workspace_id": "ws_a",
        "revision": 1,
        "status": "ACTIVE",
    }

    provider = VerifiedWorkspaceMembershipResolver(
        workspace_root=ws,
        membership_root=memberships,
        integrity_verifier=MembershipIntegrityVerifier(
            verification_key=KEY
        ),
        revision_authority=ProvisionedMembershipRevisionAuthority(
            revision_resolver=lambda **_: state
        ),
    )

    return provider, path


def resolve(provider, **overrides):
    request = {
        "principal_id": "principal-a",
        "workspace_id": "ws_a",
        "operation": OPERATION,
    }
    request.update(overrides)
    return provider(**request)


def test_valid_synthetic_membership(tmp_path):
    provider, _ = setup(tmp_path)
    assert resolve(provider)["access_granted"] is True


def test_tampered_record_denied(tmp_path):
    provider, path = setup(tmp_path)
    envelope = json.loads(path.read_text())
    envelope["payload"]["workspace_id"] = "ws_b"
    path.write_text(json.dumps(envelope))
    with pytest.raises(VerifiedMembershipUnavailable):
        resolve(provider)


def test_unsigned_record_denied(tmp_path):
    provider, path = setup(tmp_path)
    path.write_text(json.dumps(payload()))
    with pytest.raises(VerifiedMembershipUnavailable):
        resolve(provider)


def test_old_signature_after_revocation_denied(tmp_path):
    state = {
        "principal_id": "principal-a",
        "workspace_id": "ws_a",
        "revision": 2,
        "status": "REVOKED",
    }
    provider, _ = setup(tmp_path, state)
    with pytest.raises(VerifiedMembershipUnavailable):
        resolve(provider)


def test_old_signature_after_revision_change_denied(tmp_path):
    state = {
        "principal_id": "principal-a",
        "workspace_id": "ws_a",
        "revision": 2,
        "status": "ACTIVE",
    }
    provider, _ = setup(tmp_path, state)
    with pytest.raises(VerifiedMembershipUnavailable):
        resolve(provider)


@pytest.mark.parametrize("status", ["REVOKED", "SUSPENDED"])
def test_current_status_denied(tmp_path, status):
    state = {
        "principal_id": "principal-a",
        "workspace_id": "ws_a",
        "revision": 1,
        "status": status,
    }
    provider, _ = setup(tmp_path, state)
    with pytest.raises(VerifiedMembershipUnavailable):
        resolve(provider)


@pytest.mark.parametrize("field,value", [
    ("principal_id", "principal-b"),
    ("workspace_id", "ws_b"),
    ("operation", "ADMINISTER_RUNTIME"),
    ("workspace_id", "../ws_a"),
])
def test_scope_mismatch_denied(tmp_path, field, value):
    provider, _ = setup(tmp_path)
    with pytest.raises(VerifiedMembershipUnavailable):
        resolve(provider, **{field: value})


def test_corrupt_record_denied(tmp_path):
    provider, path = setup(tmp_path)
    path.write_text("{invalid")
    with pytest.raises(VerifiedMembershipUnavailable):
        resolve(provider)


def test_missing_membership_denied(tmp_path):
    provider, path = setup(tmp_path)
    path.unlink()
    with pytest.raises(VerifiedMembershipUnavailable):
        resolve(provider)


def test_missing_revision_authority_denied():
    with pytest.raises(MembershipRevisionDenied):
        ProvisionedMembershipRevisionAuthority(
            revision_resolver=None
        )


def test_weak_key_denied():
    with pytest.raises(MembershipIntegrityDenied):
        MembershipIntegrityVerifier(verification_key=b"weak")


def test_duplicate_operations_denied():
    record = payload()
    record["operations"] = [OPERATION, OPERATION]
    with pytest.raises(MembershipIntegrityDenied):
        canonical_bytes(record)


def test_boolean_revision_denied():
    record = payload()
    record["revision"] = True
    with pytest.raises(MembershipIntegrityDenied):
        canonical_bytes(record)


def test_verification_failure_does_not_call_revision_authority(tmp_path):
    calls = []

    provider, path = setup(tmp_path)
    provider.revisions = ProvisionedMembershipRevisionAuthority(
        revision_resolver=lambda **kwargs: calls.append(kwargs)
    )

    envelope = json.loads(path.read_text())
    envelope["signature"] = "0" * 64
    path.write_text(json.dumps(envelope))

    with pytest.raises(VerifiedMembershipUnavailable):
        resolve(provider)

    assert not calls


def test_no_production_registration_in_package():
    from pathlib import Path

    modules = [
        "backend/server/runtime/security/"
        "semantic_memory_membership_integrity.py",
        "backend/server/runtime/security/"
        "semantic_memory_membership_revision.py",
        "backend/server/runtime/security/"
        "semantic_memory_verified_membership_provider.py",
    ]

    for filename in modules:
        text = Path(filename).read_text(encoding="utf-8")
        assert "register_semantic_memory_certification_workspace(" not in text
