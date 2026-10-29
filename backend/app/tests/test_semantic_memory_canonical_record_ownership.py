
"""PT3.2?4 ? Canonical record ownership regressions."""

import pytest

from backend.server.runtime.security.semantic_memory_canonical_record_ownership import (
    CanonicalRecordOwnershipDenied,
    certify_record_collection_ownership,
    certify_record_ownership,
    validate_workspace_id,
)


def record(workspace="ws_alpha", identifier="record_1"):
    return {
        "workspace_id": workspace,
        "record_id": identifier,
        "content": "Synthetic testing only",
    }


def test_exact_workspace_ownership_passes():
    result = certify_record_ownership(
        record=record(),
        expected_workspace_id="ws_alpha",
        expected_record_id="record_1",
    )
    assert result["ownership_verified"] is True
    assert result["consumption_authorized"] is False
    assert result["fully_certified"] is False


def test_cross_workspace_substitution_denied():
    with pytest.raises(CanonicalRecordOwnershipDenied):
        certify_record_ownership(
            record=record(workspace="ws_beta"),
            expected_workspace_id="ws_alpha",
            expected_record_id="record_1",
        )


def test_wrong_record_identity_denied():
    with pytest.raises(CanonicalRecordOwnershipDenied):
        certify_record_ownership(
            record=record(identifier="record_2"),
            expected_workspace_id="ws_alpha",
            expected_record_id="record_1",
        )


@pytest.mark.parametrize("workspace", [
    "",
    " ",
    "../ws_alpha",
    "ws/alpha",
    "ws.alpha",
    "ws alpha",
    "ws_alpha ",
    None,
    123,
    True,
    "a" * 129,
])
def test_invalid_workspace_identifiers_denied(workspace):
    with pytest.raises(CanonicalRecordOwnershipDenied):
        validate_workspace_id(workspace)


def test_missing_workspace_ownership_denied():
    value = record()
    del value["workspace_id"]

    with pytest.raises(CanonicalRecordOwnershipDenied):
        certify_record_ownership(
            record=value,
            expected_workspace_id="ws_alpha",
            expected_record_id="record_1",
        )


def test_missing_record_identity_denied():
    value = record()
    del value["record_id"]

    with pytest.raises(CanonicalRecordOwnershipDenied):
        certify_record_ownership(
            record=value,
            expected_workspace_id="ws_alpha",
            expected_record_id="record_1",
        )


def test_duplicate_records_denied():
    with pytest.raises(CanonicalRecordOwnershipDenied):
        certify_record_collection_ownership(
            records=[record(), record()],
            expected_workspace_id="ws_alpha",
        )


def test_mixed_workspace_collection_denied():
    with pytest.raises(CanonicalRecordOwnershipDenied):
        certify_record_collection_ownership(
            records=[
                record("ws_alpha", "record_1"),
                record("ws_beta", "record_2"),
            ],
            expected_workspace_id="ws_alpha",
        )


def test_valid_collection_passes_without_consumption():
    results = certify_record_collection_ownership(
        records=[
            record("ws_alpha", "record_1"),
            record("ws_alpha", "record_2"),
        ],
        expected_workspace_id="ws_alpha",
    )

    assert len(results) == 2
    assert all(
        result["consumption_authorized"] is False
        for result in results
    )


def test_collection_input_rejected():
    with pytest.raises(CanonicalRecordOwnershipDenied):
        certify_record_collection_ownership(
            records={"record_id": "record_1"},
            expected_workspace_id="ws_alpha",
        )


def test_record_does_not_gain_authority_from_extra_fields():
    value = record()
    value["access_granted"] = True
    value["fully_certified"] = True
    value["consumption_authorized"] = True

    result = certify_record_ownership(
        record=value,
        expected_workspace_id="ws_alpha",
        expected_record_id="record_1",
    )

    assert result["consumption_authorized"] is False
    assert result["fully_certified"] is False


def test_ownership_result_is_immutable():
    result = certify_record_ownership(
        record=record(),
        expected_workspace_id="ws_alpha",
        expected_record_id="record_1",
    )

    with pytest.raises(TypeError):
        result["workspace_id"] = "ws_beta"
