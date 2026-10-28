
"""PT2C.5.5K-L ? Integration guard tests."""

import pytest

from backend.server.runtime.security.semantic_memory_trusted_entitlement_adapter import (
    CertificationEntitlementIntegration,
    TrustedEntitlementIntegrationUnavailable,
)


def test_missing_verified_provider_denied():
    with pytest.raises(TrustedEntitlementIntegrationUnavailable):
        CertificationEntitlementIntegration(
            membership_resolver=None
        )


def test_arbitrary_callback_denied():
    with pytest.raises(TrustedEntitlementIntegrationUnavailable):
        CertificationEntitlementIntegration(
            membership_resolver=lambda **_: {
                "access_granted": True
            }
        )


def test_arbitrary_object_denied():
    with pytest.raises(TrustedEntitlementIntegrationUnavailable):
        CertificationEntitlementIntegration(
            membership_resolver=object()
        )


def test_no_runtime_registration():
    from pathlib import Path

    module = Path(
        "backend/server/runtime/security/"
        "semantic_memory_trusted_entitlement_adapter.py"
    )
    source = module.read_text(encoding="utf-8")

    assert "kernel.bind_component(" not in source
    assert "register_semantic_memory_certification_workspace(" not in source
