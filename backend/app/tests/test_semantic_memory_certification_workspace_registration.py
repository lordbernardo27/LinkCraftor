"""PT2C.4B ? Fail-closed workspace kernel registration tests."""

from types import SimpleNamespace

import pytest

from backend.server.runtime.universal_runtime_kernel import (
    UniversalRuntimeKernel,
)
from backend.server.runtime.semantic_memory_certification_identity_registration import (
    register_semantic_memory_certification_identity,
)
from backend.server.runtime.semantic_memory_certification_workspace_registration import (
    CERTIFICATION_WORKSPACE_POLICY_COMPONENT_KEY,
    CertificationWorkspaceRegistrationError,
    register_semantic_memory_certification_workspace,
)
from backend.server.engine.semantic_memory_certification_workspace_policy import (
    CERTIFICATION_WORKSPACE_OPERATION,
    CertificationWorkspacePolicyDenied,
    ProvisionedCertificationWorkspacePolicy,
)


def make_composition():
    return SimpleNamespace(
        kernel=UniversalRuntimeKernel(
            runtime_id="certification-workspace-registration-test",
            product_name="LinkCraftor",
        )
    )


def register_identity(composition):
    return register_semantic_memory_certification_identity(
        composition
    )


def test_requires_existing_identity_component():
    composition = make_composition()

    with pytest.raises(CertificationWorkspaceRegistrationError):
        register_semantic_memory_certification_workspace(
            composition
        )

    assert not composition.kernel.has_component(
        CERTIFICATION_WORKSPACE_POLICY_COMPONENT_KEY
    )


def test_registers_workspace_policy_in_canonical_kernel():
    composition = make_composition()
    register_identity(composition)

    policy = register_semantic_memory_certification_workspace(
        composition
    )

    assert composition.kernel.get_component(
        CERTIFICATION_WORKSPACE_POLICY_COMPONENT_KEY,
        ProvisionedCertificationWorkspacePolicy,
    ) is policy


def test_duplicate_registration_rejected():
    composition = make_composition()
    register_identity(composition)

    policy = register_semantic_memory_certification_workspace(
        composition
    )

    with pytest.raises(CertificationWorkspaceRegistrationError):
        register_semantic_memory_certification_workspace(
            composition
        )

    assert composition.kernel.get_component(
        CERTIFICATION_WORKSPACE_POLICY_COMPONENT_KEY
    ) is policy


def test_unprovisioned_workspace_policy_denies():
    composition = make_composition()
    register_identity(composition)

    policy = register_semantic_memory_certification_workspace(
        composition
    )

    with pytest.raises(CertificationWorkspacePolicyDenied):
        policy.evaluate(
            request_lookup="synthetic-request",
            workspace_id="ws_test_a",
            operation=CERTIFICATION_WORKSPACE_OPERATION,
        )


def test_injected_workspace_resolver_does_not_grant_access():
    composition = make_composition()
    register_identity(composition)

    policy = register_semantic_memory_certification_workspace(
        composition,
        workspace_access_resolver=lambda **_: {
            "principal_id": "fabricated",
            "workspace_id": "ws_test_a",
            "access_granted": True,
            "authorization_source": "fabricated",
            "authorization_reference": "fabricated",
        },
    )

    with pytest.raises(CertificationWorkspacePolicyDenied):
        policy.evaluate(
            request_lookup="synthetic-request",
            workspace_id="ws_test_a",
            operation=CERTIFICATION_WORKSPACE_OPERATION,
        )


def test_preserves_unrelated_kernel_component():
    composition = make_composition()
    marker = object()

    composition.kernel.bind_component(
        "test.unrelated.component",
        marker,
    )

    register_identity(composition)
    register_semantic_memory_certification_workspace(
        composition
    )

    assert composition.kernel.get_component(
        "test.unrelated.component"
    ) is marker


def test_missing_kernel_fails_without_fallback():
    with pytest.raises(AttributeError):
        register_semantic_memory_certification_workspace(
            SimpleNamespace()
        )
