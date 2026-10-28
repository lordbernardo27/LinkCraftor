"""PT2C.5.4B ? Entitlement contract security tests."""

import pytest

from backend.server.runtime.security.semantic_memory_workspace_entitlement import (
    CERTIFICATION_ENTITLEMENT_OPERATION,
    ProvisionedWorkspaceEntitlementAuthority,
    WorkspaceEntitlementConfigurationError,
    WorkspaceEntitlementDenied,
)


def identity():
    return {
        "principal_id": "principal-a",
        "authentication_established": True,
    }


def evidence():
    return {
        "principal_id": "principal-a",
        "workspace_id": "ws_a",
        "operation": CERTIFICATION_ENTITLEMENT_OPERATION,
        "access_granted": True,
        "authorization_source": "synthetic-test-only",
        "authorization_reference": "synthetic-record",
    }


def authority(result=None, resolver=None):
    if resolver is None:
        resolver = lambda **_: evidence() if result is None else result
    return ProvisionedWorkspaceEntitlementAuthority(
        entitlement_resolver=resolver
    )


def check(provider, principal=None, workspace="ws_a",
          operation=CERTIFICATION_ENTITLEMENT_OPERATION):
    return provider.resolve(
        identity=identity() if principal is None else principal,
        workspace_id=workspace,
        operation=operation,
    )


def test_matching_synthetic_evidence():
    result = check(authority())
    assert result["principal_id"] == "principal-a"
    assert result["workspace_id"] == "ws_a"
    assert result["access_granted"] is True


@pytest.mark.parametrize(
    "principal",
    [
        {},
        [],
        {"principal_id": "", "authentication_established": True},
        {"principal_id": "principal-a", "authentication_established": False},
        {"principal_id": "principal-a", "authentication_established": 1},
    ],
)
def test_invalid_identity_denied(principal):
    with pytest.raises(WorkspaceEntitlementDenied):
        check(authority(), principal=principal)


@pytest.mark.parametrize("workspace", ["", " ws_a", "ws_a ", None, 10])
def test_invalid_workspace_denied(workspace):
    with pytest.raises(WorkspaceEntitlementDenied):
        check(authority(), workspace=workspace)


@pytest.mark.parametrize(
    "operation",
    ["ADMINISTER_RUNTIME", "CALL_INTERNAL_SERVICE", "", None, 1],
)
def test_unsupported_operation_denied(operation):
    with pytest.raises(WorkspaceEntitlementDenied):
        check(authority(), operation=operation)


@pytest.mark.parametrize(
    "field,value",
    [
        ("principal_id", "principal-b"),
        ("workspace_id", "ws_b"),
        ("operation", "SUBMIT_JOB"),
        ("access_granted", False),
        ("access_granted", 1),
        ("authorization_source", ""),
        ("authorization_reference", " "),
    ],
)
def test_mismatched_evidence_denied(field, value):
    result = evidence()
    result[field] = value
    with pytest.raises(WorkspaceEntitlementDenied):
        check(authority(result=result))


@pytest.mark.parametrize("result", [{}, [], "granted"])
def test_malformed_evidence_denied(result):
    with pytest.raises(WorkspaceEntitlementDenied):
        check(authority(result=result))


def test_explicit_none_evidence_denied():
    provider = authority(resolver=lambda **_: None)
    with pytest.raises(WorkspaceEntitlementDenied):
        check(provider)


def test_resolver_failure_denied():
    def unavailable(**_):
        raise RuntimeError("provider unavailable")

    with pytest.raises(WorkspaceEntitlementDenied):
        check(authority(resolver=unavailable))


def test_missing_provider_rejected():
    with pytest.raises(WorkspaceEntitlementConfigurationError):
        ProvisionedWorkspaceEntitlementAuthority(
            entitlement_resolver=None
        )


def test_immutable_result():
    result = check(authority())
    with pytest.raises(TypeError):
        result["access_granted"] = False


def test_resolver_receives_exact_principal_workspace_and_operation():
    captured = []

    def resolver(**kwargs):
        captured.append(kwargs)
        return evidence()

    check(authority(resolver=resolver))
    assert captured == [{
        "principal_id": "principal-a",
        "workspace_id": "ws_a",
        "operation": CERTIFICATION_ENTITLEMENT_OPERATION,
    }]


def test_unavailable_identity_never_calls_entitlement_resolver():
    called = []

    def resolver(**kwargs):
        called.append(kwargs)
        return evidence()

    with pytest.raises(WorkspaceEntitlementDenied):
        check(
            authority(resolver=resolver),
            principal={
                "principal_id": "principal-a",
                "authentication_established": False,
            },
        )

    assert not called
