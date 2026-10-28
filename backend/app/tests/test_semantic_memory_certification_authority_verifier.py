"""Phase 3.6.1O: isolated authority-verifier security tests."""

import base64
from copy import deepcopy

import pytest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from backend.server.engine.semantic_memory_certification_authority_verifier import (
    SCHEMA,
    SCOPE,
    canonical_attestation_bytes,
    verify_semantic_memory_authority,
)


@pytest.fixture
def signed_inputs():
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    digest = "a" * 64
    package_id = "finalsemanticmemory:v1:" + digest

    claims = {
        "schema": SCHEMA,
        "issuer_id": "test-issuer",
        "key_id": "test-key-001",
        "scope": SCOPE,
        "package_id": package_id,
        "package_digest": digest,
        "attestation_id": "test-attestation-001",
    }

    signature = private_key.sign(
        canonical_attestation_bytes(claims)
    )

    return {
        "reference_result": {
            "reference_integrity_valid": True,
        },
        "final_package": {
            "final_semantic_memory_package_id": package_id,
            "final_semantic_memory_package_digest": digest,
        },
        "attestation": {
            **claims,
            "signature": base64.b64encode(signature).decode("ascii"),
        },
        "trusted_issuers": {
            "test-issuer": {
                "key_id": "test-key-001",
                "public_key": public_key,
                "scopes": [SCOPE],
            },
        },
    }


def verify(inputs):
    before = deepcopy(inputs)
    result = verify_semantic_memory_authority(**inputs)

    assert inputs == before, "Verifier mutated its input"

    assert result["fully_certified"] is False
    assert result["consumption_authorized"] is False

    return result


def test_valid_authorized_signature(signed_inputs):
    result = verify(signed_inputs)

    assert result["authority_signature_verified"] is True
    assert result["status"] == "ISSUER_SIGNATURE_VERIFIED"
    assert result["issuer_id"] == "test-issuer"


def test_reject_forged_signature(signed_inputs):
    forged_key = Ed25519PrivateKey.generate()

    claims = {
        key: value
        for key, value in signed_inputs["attestation"].items()
        if key != "signature"
    }

    signed_inputs["attestation"]["signature"] = (
        base64.b64encode(
            forged_key.sign(canonical_attestation_bytes(claims))
        ).decode("ascii")
    )

    result = verify(signed_inputs)

    assert result["authority_signature_verified"] is False
    assert result["reason"] == "invalid_signature"


def test_reject_untrusted_issuer(signed_inputs):
    signed_inputs["trusted_issuers"] = {}

    result = verify(signed_inputs)

    assert result["authority_signature_verified"] is False
    assert result["reason"] == "untrusted_issuer"


def test_reject_wrong_issuer_scope(signed_inputs):
    signed_inputs["trusted_issuers"]["test-issuer"][
        "scopes"
    ] = ["semantic_memory.read"]

    result = verify(signed_inputs)

    assert result["reason"] == "issuer_scope_not_authorized"


def test_reject_wrong_key_id(signed_inputs):
    signed_inputs["trusted_issuers"]["test-issuer"][
        "key_id"
    ] = "another-key"

    result = verify(signed_inputs)

    assert result["reason"] == "untrusted_key"


def test_reject_package_substitution(signed_inputs):
    signed_inputs["final_package"][
        "final_semantic_memory_package_digest"
    ] = "b" * 64

    result = verify(signed_inputs)

    assert result["reason"] == "signed_package_mismatch"


def test_reject_claim_tampering(signed_inputs):
    signed_inputs["attestation"]["attestation_id"] = (
        "modified-attestation"
    )

    result = verify(signed_inputs)

    assert result["reason"] == "invalid_signature"


def test_reject_unverified_reference(signed_inputs):
    signed_inputs["reference_result"][
        "reference_integrity_valid"
    ] = False

    result = verify(signed_inputs)

    assert result["reason"] == "reference_integrity_not_verified"


def test_reject_missing_attestation(signed_inputs):
    signed_inputs["attestation"] = None

    result = verify(signed_inputs)

    assert result["reason"] == "evidence_unavailable"


def test_reject_missing_trust_registry(signed_inputs):
    signed_inputs["trusted_issuers"] = None

    result = verify(signed_inputs)

    assert result["reason"] == "trust_registry_unavailable"


def test_reject_invalid_signature_encoding(signed_inputs):
    signed_inputs["attestation"]["signature"] = "!!!"

    result = verify(signed_inputs)

    assert result["reason"] == "invalid_signature_encoding"


def test_reject_unsupported_algorithm_field(signed_inputs):
    signed_inputs["attestation"]["algorithm"] = "NONE"

    result = verify(signed_inputs)

    assert result["reason"] == "invalid_attestation_schema"


def test_reject_missing_signed_claim(signed_inputs):
    del signed_inputs["attestation"]["package_digest"]

    result = verify(signed_inputs)

    assert result["reason"] == "invalid_attestation_schema"


def test_valid_signature_never_grants_consumption(signed_inputs):
    result = verify(signed_inputs)

    assert result["authority_signature_verified"] is True
    assert result["fully_certified"] is False
    assert result["consumption_authorized"] is False
    assert result["reason"] == (
        "workspace_record_binding_and_revocation_pending"
    )


def test_genuine_producer_reference_authority_handoff():
    from backend.app.tests.test_semantic_memory_certification_reference_adapter import (
        MEMORY_ID,
        make_lineage_fixture,
    )
    from backend.server.semantic_intelligence.semantic_memory_v1 import (
        define_semantic_memory_retrieval_read_contract_v1 as retrieve,
        build_final_semantic_memory_result_v1 as build,
        certify_full_semantic_memory_v1 as certify,
    )
    from backend.server.engine.semantic_memory_certification_reference_adapter import (
        inspect_semantic_memory_certification_reference as inspect_reference,
    )

    retrieval = retrieve(deepcopy(make_lineage_fixture()))
    final = build(deepcopy(retrieval))
    certification = certify(deepcopy(final))
    package = final["final_semantic_memory_package"]

    reference = inspect_reference(
        workspace_id="phase361_authority_handoff",
        operational_memory_id="synthetic-operational",
        canonical_memory_object_id=MEMORY_ID,
        certification_result=certification,
        final_package=package,
        retrieval_bundle=retrieval[
            "semantic_memory_retrieval_read_contract_bundle"
        ],
    )

    assert reference["reference_integrity_valid"] is True
    assert reference["certified"] is False

    key = Ed25519PrivateKey.generate()
    public_key = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    claims = {
        "schema": SCHEMA,
        "issuer_id": "synthetic-test-issuer",
        "key_id": "synthetic-test-key",
        "scope": SCOPE,
        "package_id": package["final_semantic_memory_package_id"],
        "package_digest": package[
            "final_semantic_memory_package_digest"
        ],
        "attestation_id": "synthetic-test-attestation",
    }

    inputs = {
        "reference_result": reference,
        "final_package": package,
        "attestation": {
            **claims,
            "signature": base64.b64encode(
                key.sign(canonical_attestation_bytes(claims))
            ).decode("ascii"),
        },
        "trusted_issuers": {
            "synthetic-test-issuer": {
                "key_id": "synthetic-test-key",
                "public_key": public_key,
                "scopes": [SCOPE],
            },
        },
    }

    result = verify(inputs)
    assert result["authority_signature_verified"] is True
    assert result["fully_certified"] is False
    assert result["consumption_authorized"] is False

    for scenario in (
        "untrusted_issuer",
        "package_mismatch",
        "unverified_reference",
    ):
        modified = deepcopy(inputs)

        if scenario == "untrusted_issuer":
            modified["trusted_issuers"] = {}
        elif scenario == "package_mismatch":
            modified["attestation"]["package_digest"] = "0" * 64
        else:
            modified["reference_result"]["reference_integrity_valid"] = False

        rejected = verify(modified)
        assert rejected["authority_signature_verified"] is False
        assert rejected["fully_certified"] is False
        assert rejected["consumption_authorized"] is False


@pytest.mark.parametrize(
    "scenario, expected_status",
    [
        ("valid", "ISSUER_SIGNATURE_VERIFIED"),
        ("tampered_package", "REFERENCE_REJECTED"),
        ("untrusted_issuer", "AUTHORITY_REJECTED"),
        ("missing_attestation", "AUTHORITY_REJECTED"),
        ("forged_signature", "AUTHORITY_REJECTED"),
    ],
)
def test_trusted_handoff_security_boundary(scenario, expected_status):
    from backend.app.tests.test_semantic_memory_certification_reference_adapter import (
        MEMORY_ID,
        make_lineage_fixture,
    )
    from backend.server.semantic_intelligence.semantic_memory_v1 import (
        define_semantic_memory_retrieval_read_contract_v1 as retrieve,
        build_final_semantic_memory_result_v1 as build,
        certify_full_semantic_memory_v1 as certify,
    )
    from backend.server.engine.semantic_memory_certification_trusted_handoff import (
        verify_semantic_memory_certification_handoff as handoff,
    )

    retrieval = retrieve(deepcopy(make_lineage_fixture()))
    final = build(deepcopy(retrieval))
    certification = certify(deepcopy(final))
    package = final["final_semantic_memory_package"]

    key = Ed25519PrivateKey.generate()
    public_key = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    claims = {
        "schema": SCHEMA,
        "issuer_id": "handoff-test-issuer",
        "key_id": "handoff-test-key",
        "scope": SCOPE,
        "package_id": package["final_semantic_memory_package_id"],
        "package_digest": package[
            "final_semantic_memory_package_digest"
        ],
        "attestation_id": "handoff-test-attestation",
    }

    signature = key.sign(canonical_attestation_bytes(claims))

    inputs = {
        "workspace_id": "phase361_handoff_test",
        "operational_memory_id": "synthetic-operational",
        "canonical_memory_object_id": MEMORY_ID,
        "certification_result": certification,
        "final_package": package,
        "retrieval_bundle": retrieval[
            "semantic_memory_retrieval_read_contract_bundle"
        ],
        "attestation": {
            **claims,
            "signature": base64.b64encode(signature).decode("ascii"),
        },
        "trusted_issuers": {
            "handoff-test-issuer": {
                "key_id": "handoff-test-key",
                "public_key": public_key,
                "scopes": [SCOPE],
            },
        },
    }

    if scenario == "tampered_package":
        inputs["final_package"][
            "final_semantic_memory_package_digest"
        ] = "0" * 64
    elif scenario == "untrusted_issuer":
        inputs["trusted_issuers"] = {}
    elif scenario == "missing_attestation":
        inputs["attestation"] = None
    elif scenario == "forged_signature":
        forged_key = Ed25519PrivateKey.generate()
        inputs["attestation"]["signature"] = base64.b64encode(
            forged_key.sign(canonical_attestation_bytes(claims))
        ).decode("ascii")

    snapshot = deepcopy(inputs)
    result = handoff(**inputs)

    assert inputs == snapshot
    assert result["status"] == expected_status
    assert result["fully_certified"] is False
    assert result["consumption_authorized"] is False

    valid = scenario == "valid"
    assert result["authority_signature_verified"] is valid
    assert result["reference_integrity_valid"] is (
        scenario != "tampered_package"
    )


def test_provisioned_registry_snapshot(monkeypatch):
    from backend.server.engine import (
        semantic_memory_certification_provisioned_verifier as module,
    )

    seen = []

    def capture_handoff(**kwargs):
        seen.append(kwargs["trusted_issuers"])
        return {
            "authority_signature_verified": False,
            "fully_certified": False,
            "consumption_authorized": False,
        }

    monkeypatch.setattr(
        module,
        "verify_semantic_memory_certification_handoff",
        capture_handoff,
    )

    registry = {
        "test-issuer": {
            "key_id": "key-001",
            "public_key": b"x" * 32,
            "scopes": [SCOPE],
        }
    }

    verifier = module.ProvisionedSemanticMemoryVerifier(
        trusted_issuers=registry
    )

    registry["test-issuer"]["key_id"] = "changed"
    registry["test-issuer"]["scopes"].clear()
    registry.clear()

    inputs = dict(
        workspace_id="workspace",
        operational_memory_id="operational",
        canonical_memory_object_id="memory",
        certification_result={},
        final_package={},
        retrieval_bundle={},
        attestation={},
    )

    result = verifier.verify(**inputs)

    assert result["consumption_authorized"] is False
    assert seen[0]["test-issuer"]["key_id"] == "key-001"
    assert seen[0]["test-issuer"]["scopes"] == (SCOPE,)

    with pytest.raises(TypeError):
        verifier.verify(
            **inputs,
            trusted_issuers={"attacker": {}},
        )

    with pytest.raises(TypeError):
        verifier.verify(
            **inputs,
            reference_result={"reference_integrity_valid": True},
        )


@pytest.mark.parametrize(
    "registry",
    [
        None,
        [],
        {"issuer": {}},
        {
            "issuer": {
                "key_id": "key",
                "public_key": b"short",
                "scopes": [SCOPE],
            }
        },
    ],
)
def test_provisioned_invalid_registry_rejected(registry):
    from backend.server.engine.semantic_memory_certification_provisioned_verifier import (
        ProvisionedSemanticMemoryVerifier,
        SemanticMemoryTrustConfigurationError,
    )

    with pytest.raises(SemanticMemoryTrustConfigurationError):
        ProvisionedSemanticMemoryVerifier(
            trusted_issuers=registry
        )


def test_provisioned_empty_registry_allowed_but_untrusted():
    from backend.server.engine.semantic_memory_certification_provisioned_verifier import (
        ProvisionedSemanticMemoryVerifier,
    )

    verifier = ProvisionedSemanticMemoryVerifier(
        trusted_issuers={}
    )

    assert verifier is not None


def test_attestation_domain_has_real_newline():
    from backend.server.engine.semantic_memory_certification_authority_verifier import (
        DOMAIN,
    )

    expected = (
        b"LINKCRAFTOR:SEMANTIC_MEMORY:CERTIFICATION:V1"
        + bytes([10])
    )

    assert DOMAIN == expected
    assert DOMAIN.endswith(bytes([10]))
    assert not DOMAIN.endswith(bytes([92, 110]))
