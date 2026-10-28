"""Phase 3.6.1P: V2 context-binding integration regression tests."""

import base64
from copy import deepcopy

import pytest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from backend.app.tests.test_semantic_memory_certification_reference_adapter import (
    MEMORY_ID,
    make_lineage_fixture,
)
from backend.server.semantic_intelligence.semantic_memory_v1 import (
    define_semantic_memory_retrieval_read_contract_v1 as retrieve,
    build_final_semantic_memory_result_v1 as build,
    certify_full_semantic_memory_v1 as certify,
)
from backend.server.engine.semantic_memory_certification_context_v2 import (
    SCHEMA_V2,
    SCOPE_V2,
    DOMAIN_V2,
    canonical_context_attestation_bytes_v2,
)
from backend.server.engine.semantic_memory_certification_context_handoff_v2 import (
    verify_semantic_memory_context_handoff_v2 as handoff,
)
from backend.server.engine.semantic_memory_certification_provisioned_context_v2 import (
    ProvisionedSemanticMemoryContextVerifierV2,
)


@pytest.fixture
def v2_inputs():
    retrieval = retrieve(deepcopy(make_lineage_fixture()))
    final = build(deepcopy(retrieval))
    certification = certify(deepcopy(final))
    package = final["final_semantic_memory_package"]

    context = {
        "workspace_id": "phase361_v2_test",
        "operational_memory_id": "synthetic-operational",
        "canonical_memory_object_id": MEMORY_ID,
    }

    key = Ed25519PrivateKey.generate()
    public_key = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    claims = {
        "schema": SCHEMA_V2,
        "issuer_id": "synthetic-v2-issuer",
        "key_id": "synthetic-v2-key",
        "scope": SCOPE_V2,
        "attestation_id": "synthetic-v2-attestation",
        **context,
        "package_id": package["final_semantic_memory_package_id"],
        "package_digest": package[
            "final_semantic_memory_package_digest"
        ],
    }

    assert DOMAIN_V2.endswith(bytes([10]))

    attestation = {
        **claims,
        "signature": base64.b64encode(
            key.sign(canonical_context_attestation_bytes_v2(claims))
        ).decode("ascii"),
    }

    return {
        "expected_context": context,
        "certification_result": certification,
        "final_package": package,
        "retrieval_bundle": retrieval[
            "semantic_memory_retrieval_read_contract_bundle"
        ],
        "attestation": attestation,
        "trusted_issuers": {
            "synthetic-v2-issuer": {
                "key_id": "synthetic-v2-key",
                "public_key": public_key,
                "scopes": [SCOPE_V2],
            },
        },
    }


@pytest.mark.parametrize(
    "scenario, expected_status",
    [
        ("valid", "SIGNED_CONTEXT_MATCHED"),
        ("tampered_package", "REFERENCE_REJECTED"),
        ("different_workspace", "CONTEXT_REJECTED"),
        ("different_operational", "CONTEXT_REJECTED"),
        ("nonmember_object", "REFERENCE_REJECTED"),
        ("unknown_issuer", "CONTEXT_REJECTED"),
        ("missing_attestation", "CONTEXT_REJECTED"),
        ("tampered_claim", "CONTEXT_REJECTED"),
        ("v1_downgrade", "CONTEXT_REJECTED"),
    ],
)
def test_v2_genuine_handoff(scenario, expected_status, v2_inputs):
    inputs = deepcopy(v2_inputs)

    if scenario == "tampered_package":
        inputs["final_package"][
            "final_semantic_memory_package_digest"
        ] = "0" * 64
    elif scenario == "different_workspace":
        inputs["expected_context"]["workspace_id"] = "other_workspace"
    elif scenario == "different_operational":
        inputs["expected_context"][
            "operational_memory_id"
        ] = "other_operational"
    elif scenario == "nonmember_object":
        inputs["expected_context"][
            "canonical_memory_object_id"
        ] = "phase361_nonmember_object"
    elif scenario == "unknown_issuer":
        inputs["trusted_issuers"] = {}
    elif scenario == "missing_attestation":
        inputs["attestation"] = None
    elif scenario == "tampered_claim":
        inputs["attestation"]["attestation_id"] = "modified"
    elif scenario == "v1_downgrade":
        inputs["attestation"]["schema"] = (
            "semantic_memory_certification_attestation_v1"
        )

    before = deepcopy(inputs)
    result = handoff(**inputs)

    assert inputs == before
    assert result["status"] == expected_status
    assert result["fully_certified"] is False
    assert result["consumption_authorized"] is False

    accepted = scenario == "valid"

    assert result["context_signature_verified"] is accepted
    assert result["context_binding_verified"] is accepted

    if scenario == "nonmember_object":
        assert (
            "missing_trusted_identity_mapping"
            in result["reference_result"]["reasons"]
        )


def test_v2_provisioned_resolver_controls_workspace(v2_inputs):
    inputs = deepcopy(v2_inputs)
    registry = inputs.pop("trusted_issuers")
    original_context = inputs.pop("expected_context")
    resolved = {"selected": dict(original_context)}

    verifier = ProvisionedSemanticMemoryContextVerifierV2(
        trusted_issuers=registry,
        context_resolver=lambda lookup: resolved.get(lookup),
    )

    request = {
        "record_lookup": "selected",
        **inputs,
    }

    valid = verifier.verify(**deepcopy(request))
    assert valid["status"] == "SIGNED_CONTEXT_MATCHED"
    assert valid["consumption_authorized"] is False

    resolved["selected"]["workspace_id"] = "other_workspace"

    denied = verifier.verify(**deepcopy(request))
    assert denied["status"] == "CONTEXT_REJECTED"
    assert denied["context_binding_verified"] is False

    resolved.clear()
    missing = verifier.verify(**deepcopy(request))
    assert missing["status"] == "TRUSTED_CONTEXT_UNAVAILABLE"

    with pytest.raises(TypeError):
        verifier.verify(
            **request,
            trusted_issuers=registry,
        )

    with pytest.raises(TypeError):
        verifier.verify(
            **request,
            expected_context=original_context,
        )

    with pytest.raises(TypeError):
        verifier.verify(
            **request,
            reference_result={"reference_integrity_valid": True},
        )
@pytest.mark.parametrize(
    "signed_record,requested_record,expected_status",
    [
        ("A", "A", "SIGNED_CONTEXT_MATCHED"),
        ("A", "B", "CONTEXT_REJECTED"),
        ("B", "B", "SIGNED_CONTEXT_MATCHED"),
        ("B", "A", "CONTEXT_REJECTED"),
    ],
)
def test_v2_same_package_record_isolation(
    signed_record, requested_record, expected_status
):
    """A genuine package member cannot borrow another member's signature."""
    from backend.server.engine.semantic_memory_certification_reference_adapter import (
        inspect_semantic_memory_certification_reference as inspect,
    )

    record_ids = {
        "A": MEMORY_ID,
        "B": "semanticmemoryobject:v1:" + "b" * 64,
    }

    fixture = deepcopy(make_lineage_fixture())
    lineage = fixture["semantic_memory_provenance_lineage_bundle"]

    first_object = deepcopy(lineage["lineage_bound_memory_objects"][0])
    first_record = deepcopy(lineage["lineage_records"][0])

    second_object = deepcopy(first_object)
    second_object.update({
        "memory_object_id": record_ids["B"],
        "memory_lineage_record_id": "synthetic-lineage-record-002",
        "source_learning_object_id": "synthetic-learning-object-002",
    })

    second_record = deepcopy(first_record)
    second_record.update({
        "memory_object_id": record_ids["B"],
        "memory_lineage_record_id": "synthetic-lineage-record-002",
    })

    lineage["lineage_bound_memory_objects"] = (
        first_object, second_object,
    )
    lineage["lineage_records"] = (
        first_record, second_record,
    )

    retrieval = retrieve(deepcopy(fixture))
    final = build(deepcopy(retrieval))
    certification = certify(deepcopy(final))
    package = final["final_semantic_memory_package"]
    bundle = retrieval["semantic_memory_retrieval_read_contract_bundle"]

    assert {
        item["memory_object_id"]
        for item in package["final_memory_objects"]
    } == set(record_ids.values())

    def expected_context(record):
        return {
            "workspace_id": "phase361_multiobject_test",
            "operational_memory_id": "synthetic-operational",
            "canonical_memory_object_id": record_ids[record],
        }

    # Both records must be genuinely valid package members.
    for record in ("A", "B"):
        reference = inspect(
            **expected_context(record),
            certification_result=deepcopy(certification),
            final_package=deepcopy(package),
            retrieval_bundle=deepcopy(bundle),
        )
        assert reference["reference_integrity_valid"] is True

    key = Ed25519PrivateKey.generate()
    public_key = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    claims = {
        "schema": SCHEMA_V2,
        "issuer_id": "multiobject-test-issuer",
        "key_id": "multiobject-test-key",
        "scope": SCOPE_V2,
        "attestation_id": "signed-for-" + signed_record,
        **expected_context(signed_record),
        "package_id": package["final_semantic_memory_package_id"],
        "package_digest": package[
            "final_semantic_memory_package_digest"
        ],
    }

    attestation = {
        **claims,
        "signature": base64.b64encode(
            key.sign(canonical_context_attestation_bytes_v2(claims))
        ).decode("ascii"),
    }

    arguments = {
        "expected_context": expected_context(requested_record),
        "certification_result": certification,
        "final_package": package,
        "retrieval_bundle": bundle,
        "attestation": attestation,
        "trusted_issuers": {
            "multiobject-test-issuer": {
                "key_id": "multiobject-test-key",
                "public_key": public_key,
                "scopes": [SCOPE_V2],
            },
        },
    }

    snapshot = deepcopy(arguments)
    result = handoff(**arguments)

    assert arguments == snapshot
    assert result["reference_integrity_valid"] is True
    assert result["status"] == expected_status
    assert result["fully_certified"] is False
    assert result["consumption_authorized"] is False

    matched = signed_record == requested_record
    assert result["context_signature_verified"] is matched
    assert result["context_binding_verified"] is matched

    if not matched:
        assert result["context_result"]["reason"] == (
            "signed_context_mismatch:canonical_memory_object_id"
        )
