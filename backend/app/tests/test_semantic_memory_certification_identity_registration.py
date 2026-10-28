"""PT2B.4C ? Certification identity kernel registration tests."""

from types import SimpleNamespace

import pytest

from backend.server.runtime.universal_runtime_kernel import (
    UniversalRuntimeKernel,
)
from backend.server.runtime.semantic_memory_certification_identity_registration import (
    CERTIFICATION_IDENTITY_COMPONENT_KEY,
    CertificationIdentityRegistrationError,
    register_semantic_memory_certification_identity,
)
from backend.server.engine.semantic_memory_certification_identity_boundary import (
    CertificationIdentityUnavailable,
    ProvisionedCertificationIdentityBoundary,
)


def make_composition():
    kernel = UniversalRuntimeKernel(
        runtime_id="certification-identity-test",
        product_name="LinkCraftor",
    )
    return SimpleNamespace(kernel=kernel)


def test_registers_inside_existing_kernel():
    composition = make_composition()

    boundary = register_semantic_memory_certification_identity(
        composition
    )

    assert composition.kernel.has_component(
        CERTIFICATION_IDENTITY_COMPONENT_KEY
    )
    assert composition.kernel.get_component(
        CERTIFICATION_IDENTITY_COMPONENT_KEY,
        ProvisionedCertificationIdentityBoundary,
    ) is boundary


def test_registered_identity_denies_without_authority():
    composition = make_composition()
    boundary = register_semantic_memory_certification_identity(
        composition
    )

    with pytest.raises(CertificationIdentityUnavailable):
        boundary.resolve(request_lookup="synthetic-request")


def test_duplicate_registration_rejected():
    composition = make_composition()

    first = register_semantic_memory_certification_identity(
        composition
    )

    with pytest.raises(CertificationIdentityRegistrationError):
        register_semantic_memory_certification_identity(
            composition
        )

    assert composition.kernel.get_component(
        CERTIFICATION_IDENTITY_COMPONENT_KEY
    ) is first


def test_caller_resolver_override_not_accepted():
    composition = make_composition()

    def fabricated_identity(_lookup):
        return {
            "principal_id": "fabricated",
            "principal_type": "SERVICE",
            "authentication_established": True,
            "identity_authority": "fabricated",
            "authentication_reference": "fabricated",
        }

    boundary = register_semantic_memory_certification_identity(
        composition,
        identity_resolver=fabricated_identity,
    )

    with pytest.raises(CertificationIdentityUnavailable):
        boundary.resolve(request_lookup="synthetic-request")


def test_caller_cannot_override_resolve_identity():
    composition = make_composition()
    boundary = register_semantic_memory_certification_identity(
        composition
    )

    with pytest.raises(TypeError):
        boundary.resolve(
            request_lookup="synthetic-request",
            identity_resolver=lambda _: {},
        )


def test_registrar_does_not_replace_other_components():
    composition = make_composition()
    unrelated = object()
    composition.kernel.bind_component(
        "test.unrelated.component",
        unrelated,
    )

    register_semantic_memory_certification_identity(
        composition
    )

    assert composition.kernel.get_component(
        "test.unrelated.component"
    ) is unrelated


def test_missing_kernel_fails_without_fallback():
    with pytest.raises(AttributeError):
        register_semantic_memory_certification_identity(
            SimpleNamespace()
        )
