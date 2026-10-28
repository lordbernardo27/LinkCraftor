"""PT2C.5.5F ? Read-only membership provider tests."""

import hashlib
import json

import pytest

from backend.server.runtime.security.semantic_memory_workspace_membership_provider import (
    OPERATION,
    ReadOnlyWorkspaceMembershipResolver,
    WorkspaceMembershipUnavailable,
)


def setup_records(tmp_path):
    workspaces = tmp_path / "workspaces"
    memberships = tmp_path / "security_memberships"
    profile_dir = workspaces / "ws_a"
    profile_dir.mkdir(parents=True)
    memberships.mkdir()

    profile = {
        "schema_version": "workspace_profile_v2",
        "workspace_id": "ws_a",
        "connection_status": "connected",
    }

    (profile_dir / "workspace_profile.json").write_text(
        json.dumps(profile), encoding="utf-8"
    )

    record = {
        "schema_version": "workspace_membership_v1",
        "principal_id": "principal-a",
        "workspace_id": "ws_a",
        "status": "ACTIVE",
        "operations": [OPERATION],
        "authorization_reference": "test-provisioning-reference",
    }

    record_id = hashlib.sha256(
        json.dumps(
            ["ws_a", "principal-a"],
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    record_path = memberships / (record_id + ".json")
    record_path.write_text(json.dumps(record), encoding="utf-8")

    resolver = ReadOnlyWorkspaceMembershipResolver(
        workspace_root=workspaces,
        membership_root=memberships,
    )

    return resolver, profile_dir / "workspace_profile.json", record_path


def resolve(resolver, **overrides):
    values = {
        "principal_id": "principal-a",
        "workspace_id": "ws_a",
        "operation": OPERATION,
    }
    values.update(overrides)
    return resolver(**values)


def test_matching_synthetic_records(tmp_path):
    resolver, _, _ = setup_records(tmp_path)
    result = resolve(resolver)
    assert result["access_granted"] is True
    assert result["workspace_id"] == "ws_a"


def test_missing_membership_denied(tmp_path):
    resolver, _, record = setup_records(tmp_path)
    record.unlink()
    with pytest.raises(WorkspaceMembershipUnavailable):
        resolve(resolver)


@pytest.mark.parametrize(
    "field,value",
    [
        ("status", "REVOKED"),
        ("status", "SUSPENDED"),
        ("principal_id", "principal-b"),
        ("workspace_id", "ws_b"),
        ("operations", []),
        ("operations", ["SUBMIT_JOB"]),
        ("authorization_reference", ""),
    ],
)
def test_invalid_membership_denied(tmp_path, field, value):
    resolver, _, path = setup_records(tmp_path)
    record = json.loads(path.read_text(encoding="utf-8"))
    record[field] = value
    path.write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(WorkspaceMembershipUnavailable):
        resolve(resolver)


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema_version", "invalid"),
        ("workspace_id", "ws_b"),
        ("connection_status", "processing"),
    ],
)
def test_unverified_workspace_denied(tmp_path, field, value):
    resolver, profile_path, _ = setup_records(tmp_path)
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    profile[field] = value
    profile_path.write_text(json.dumps(profile), encoding="utf-8")

    with pytest.raises(WorkspaceMembershipUnavailable):
        resolve(resolver)


@pytest.mark.parametrize(
    "overrides",
    [
        {"principal_id": "another-principal"},
        {"workspace_id": "ws_other"},
        {"workspace_id": "../ws_a"},
        {"workspace_id": ""},
        {"operation": "ADMINISTER_RUNTIME"},
        {"operation": "CALL_INTERNAL_SERVICE"},
    ],
)
def test_unrequested_scope_denied(tmp_path, overrides):
    resolver, _, _ = setup_records(tmp_path)
    with pytest.raises(WorkspaceMembershipUnavailable):
        resolve(resolver, **overrides)


def test_malformed_membership_json_denied(tmp_path):
    resolver, _, record = setup_records(tmp_path)
    record.write_text("{invalid", encoding="utf-8")
    with pytest.raises(WorkspaceMembershipUnavailable):
        resolve(resolver)


def test_malformed_profile_json_denied(tmp_path):
    resolver, profile, _ = setup_records(tmp_path)
    profile.write_text("{invalid", encoding="utf-8")
    with pytest.raises(WorkspaceMembershipUnavailable):
        resolve(resolver)


def test_unexpected_membership_fields_denied(tmp_path):
    resolver, _, record_path = setup_records(tmp_path)
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["admin_override"] = True
    record_path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(WorkspaceMembershipUnavailable):
        resolve(resolver)


def test_missing_workspace_root_denied(tmp_path):
    resolver, profile, _ = setup_records(tmp_path)
    profile.unlink()
    with pytest.raises(WorkspaceMembershipUnavailable):
        resolve(resolver)
