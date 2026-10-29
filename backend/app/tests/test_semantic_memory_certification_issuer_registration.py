
"""PT4 ? Fail-closed issuer registration regressions."""

import inspect

import pytest

from backend.server.runtime.semantic_memory_certification_issuer_registration import (
    CERTIFICATION_ISSUER_COMPONENT_KEY,
    CertificationIssuerRegistrationError,
    CertificationIssuerUnavailable,
    UnprovisionedCertificationIssuerAuthority,
    register_semantic_memory_certification_issuer,
)


class FakeKernel:
    def __init__(self):
        self.components = {}

    def has_component(self, key):
        return key in self.components

    def bind_component(self, key, component):
        if key in self.components:
            raise RuntimeError("Duplicate binding")
        self.components[key] = component


class FakeComposition:
    def __init__(self):
        self.kernel = FakeKernel()


def test_registers_single_backend_authority():
    composition = FakeComposition()

    authority = register_semantic_memory_certification_issuer(
        composition
    )

    assert isinstance(
        authority,
        UnprovisionedCertificationIssuerAuthority,
    )
    assert composition.kernel.components[
        CERTIFICATION_ISSUER_COMPONENT_KEY
    ] is authority


def test_duplicate_registration_denied():
    composition = FakeComposition()

    register_semantic_memory_certification_issuer(composition)

    with pytest.raises(CertificationIssuerRegistrationError):
        register_semantic_memory_certification_issuer(composition)


def test_issuance_unavailable():
    authority = UnprovisionedCertificationIssuerAuthority()

    with pytest.raises(CertificationIssuerUnavailable):
        authority.issue()


def test_verification_unavailable():
    authority = UnprovisionedCertificationIssuerAuthority()

    with pytest.raises(CertificationIssuerUnavailable):
        authority.verify()


def test_attacker_supplied_issuer_configuration_rejected():
    composition = FakeComposition()

    with pytest.raises(TypeError):
        register_semantic_memory_certification_issuer(
            composition,
            trusted_issuers={
                "attacker": {
                    "key_id": "attacker-key",
                }
            },
        )

    assert not composition.kernel.components


def test_no_caller_selected_bootstrap_dependencies():
    signature = inspect.signature(
        register_semantic_memory_certification_issuer
    )

    assert list(signature.parameters) == ["composition"]


def test_no_implicit_trust_capability():
    authority = UnprovisionedCertificationIssuerAuthority()

    assert not hasattr(authority, "trusted_issuers")
    assert not hasattr(authority, "signing_key")
    assert not hasattr(authority, "private_key")
