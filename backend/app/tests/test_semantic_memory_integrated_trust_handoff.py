
"""PT5 ? Integrated fail-closed handoff tests."""

import pytest

from backend.server.engine.semantic_memory_certification_identity_boundary import (
    ProvisionedCertificationIdentityBoundary,
)
from backend.server.engine.semantic_memory_certification_workspace_boundary import (
    ProvisionedCertificationWorkspaceBoundary,
)
from backend.server.engine.semantic_memory_certification_workspace_policy import (
    ProvisionedCertificationWorkspacePolicy,
)
from backend.server.runtime.semantic_memory_certification_issuer_registration import (
    UnprovisionedCertificationIssuerAuthority,
)
from backend.server.runtime.security.semantic_memory_integrated_trust_handoff import (
    IntegratedTrustHandoffDenied,
    SemanticMemoryIntegratedTrustHandoff,
)


def make_handoff(*, identity_available=True, membership=True):
    def identity_resolver(request_lookup):
        if not identity_available:
            raise RuntimeError("Identity unavailable")
        return {
            "principal_id": "principal_a",
            "principal_type": "USER",
            "authentication_established": True,
            "identity_authority": "synthetic_test",
            "identity_reference": "synthetic_test",
        }

    def workspace_resolver(*, identity, workspace_id):
        if not membership:
            raise RuntimeError("Membership unavailable")
        return {
            "principal_id": identity["principal_id"],
            "workspace_id": workspace_id,
            "access_granted": True,
            "authorization_source": "synthetic_test",
            "authorization_reference": "synthetic_test",
        }

    identity = ProvisionedCertificationIdentityBoundary(
        identity_resolver=identity_resolver
    )
    boundary = ProvisionedCertificationWorkspaceBoundary(
        identity_boundary=identity,
        workspace_access_resolver=workspace_resolver,
    )
    policy = ProvisionedCertificationWorkspacePolicy(
        workspace_boundary=boundary
    )

    return SemanticMemoryIntegratedTrustHandoff(
        workspace_policy=policy,
        issuer_authority=UnprovisionedCertificationIssuerAuthority(),
    )


def record(workspace="ws_alpha", identifier="record_1"):
    return {
        "workspace_id": workspace,
        "record_id": identifier,
    }


def evaluate(handoff, value=None, **kwargs):
    return handoff.evaluate(
        request_lookup=object(),
        workspace_id=kwargs.get("workspace_id", "ws_alpha"),
        record=record() if value is None else value,
        record_id=kwargs.get("record_id", "record_1"),
    )


def test_missing_identity_denied():
    with pytest.raises(IntegratedTrustHandoffDenied):
        evaluate(make_handoff(identity_available=False))


def test_missing_workspace_membership_denied():
    with pytest.raises(IntegratedTrustHandoffDenied):
        evaluate(make_handoff(membership=False))


def test_cross_workspace_record_denied():
    with pytest.raises(IntegratedTrustHandoffDenied):
        evaluate(
            make_handoff(),
            record("ws_beta"),
        )


def test_record_substitution_denied():
    with pytest.raises(IntegratedTrustHandoffDenied):
        evaluate(
            make_handoff(),
            record("ws_alpha", "record_2"),
        )


def test_missing_record_ownership_denied():
    with pytest.raises(IntegratedTrustHandoffDenied):
        evaluate(make_handoff(), {"record_id": "record_1"})


def test_valid_synthetic_evidence_still_denied():
    with pytest.raises(IntegratedTrustHandoffDenied):
        evaluate(make_handoff())


def test_forged_issuer_configuration_argument_denied():
    with pytest.raises(TypeError):
        evaluate(
            make_handoff(),
            trusted_issuers={"attacker": {}},
        ) if False else make_handoff().evaluate(
            request_lookup=object(),
            workspace_id="ws_alpha",
            record=record(),
            record_id="record_1",
            trusted_issuers={"attacker": {}},
        )


def test_arbitrary_workspace_policy_rejected():
    with pytest.raises(IntegratedTrustHandoffDenied):
        SemanticMemoryIntegratedTrustHandoff(
            workspace_policy=lambda **_: {"access_granted": True},
            issuer_authority=UnprovisionedCertificationIssuerAuthority(),
        )


def test_arbitrary_issuer_rejected():
    with pytest.raises(IntegratedTrustHandoffDenied):
        SemanticMemoryIntegratedTrustHandoff(
            workspace_policy=object(),
            issuer_authority=object(),
        )


def test_no_production_consumption_enabled():
    import inspect

    source = inspect.getsource(
        SemanticMemoryIntegratedTrustHandoff.evaluate
    )
    assert '"consumption_authorized": False' in source
    assert '"fully_certified": False' in source
