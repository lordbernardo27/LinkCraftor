"""PT2C.3C ? Scoped workspace policy security regressions."""

from types import SimpleNamespace

import pytest

from backend.server.engine.semantic_memory_certification_identity_boundary import (
    ProvisionedCertificationIdentityBoundary,
)
from backend.server.engine.semantic_memory_certification_workspace_boundary import (
    ProvisionedCertificationWorkspaceBoundary,
)
from backend.server.engine.semantic_memory_certification_workspace_policy import (
    CERTIFICATION_WORKSPACE_OPERATION,
    CertificationWorkspacePolicyDenied,
    ProvisionedCertificationWorkspacePolicy,
)
from backend.server.runtime.semantic_memory_certification_identity_registration import (
    register_semantic_memory_certification_identity,
)
from backend.server.runtime.universal_runtime_kernel import (
    UniversalRuntimeKernel,
)


def make_policy(*, principal="test-principal", workspace="ws_test_a",
                granted=True, identity=None):
    if identity is None:
        identity = ProvisionedCertificationIdentityBoundary(
            identity_resolver=lambda _: {
                "principal_id": "test-principal",
                "principal_type": "SERVICE",
                "authentication_established": True,
                "identity_authority": "synthetic-test",
                "authentication_reference": "test-reference",
            }
        )

    boundary = ProvisionedCertificationWorkspaceBoundary(
        identity_boundary=identity,
        workspace_access_resolver=lambda **_: {
            "principal_id": principal,
            "workspace_id": workspace,
            "access_granted": granted,
            "authorization_source": "synthetic-test",
            "authorization_reference": "test-policy",
        },
    )
    return ProvisionedCertificationWorkspacePolicy(
        workspace_boundary=boundary
    )


def check(policy, operation=CERTIFICATION_WORKSPACE_OPERATION,
          workspace_id="ws_test_a"):
    return policy.evaluate(
        request_lookup="synthetic-request",
        workspace_id=workspace_id,
        operation=operation,
    )


def test_matching_synthetic_workspace():
    result = check(make_policy())
    assert result["workspace_evidence_matched"] is True
    assert result["principal_id"] == "test-principal"
    assert result["workspace_id"] == "ws_test_a"


@pytest.mark.parametrize(
    "operation",
    [
        "ADMINISTER_RUNTIME",
        "CALL_INTERNAL_SERVICE",
        "SUBMIT_JOB",
        "SEMANTIC_MEMORY_CONSUME",
        "",
        None,
        123,
    ],
)
def test_other_operations_denied(operation):
    with pytest.raises(CertificationWorkspacePolicyDenied):
        check(make_policy(), operation=operation)


def test_wrong_principal_denied():
    with pytest.raises(CertificationWorkspacePolicyDenied):
        check(make_policy(principal="another-principal"))


def test_wrong_workspace_denied():
    with pytest.raises(CertificationWorkspacePolicyDenied):
        check(make_policy(workspace="ws_other"))


def test_access_not_granted_denied():
    with pytest.raises(CertificationWorkspacePolicyDenied):
        check(make_policy(granted=False))


def test_requested_other_workspace_denied():
    with pytest.raises(CertificationWorkspacePolicyDenied):
        check(make_policy(), workspace_id="ws_other")


def test_result_is_non_authorizing_and_immutable():
    result = check(make_policy())
    assert result["fully_certified"] is False
    assert result["consumption_authorized"] is False
    with pytest.raises(TypeError):
        result["consumption_authorized"] = True


def test_invalid_policy_configuration_rejected():
    with pytest.raises(ValueError):
        ProvisionedCertificationWorkspacePolicy(
            workspace_boundary=None
        )


def test_real_unprovisioned_identity_denies():
    composition = SimpleNamespace(
        kernel=UniversalRuntimeKernel(
            runtime_id="certification-policy-test",
            product_name="LinkCraftor",
        )
    )
    identity = register_semantic_memory_certification_identity(
        composition
    )
    policy = make_policy(identity=identity)

    with pytest.raises(CertificationWorkspacePolicyDenied):
        check(policy)
