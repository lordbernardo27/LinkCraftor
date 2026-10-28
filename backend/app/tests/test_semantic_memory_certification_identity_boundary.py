"""PT2B.3 ? Fail-closed identity boundary regression tests."""

from copy import deepcopy

import pytest

from backend.server.engine.semantic_memory_certification_identity_boundary import (
    CertificationIdentityConfigurationError,
    CertificationIdentityUnavailable,
    ProvisionedCertificationIdentityBoundary,
)


def valid_evidence():
    return {
        "principal_id": "synthetic-service-001",
        "principal_type": "SERVICE",
        "authentication_established": True,
        "identity_authority": "synthetic-test-authority",
        "authentication_reference": "synthetic-auth-reference",
    }


def make_boundary(result):
    return ProvisionedCertificationIdentityBoundary(
        identity_resolver=lambda lookup: deepcopy(result)
    )


def test_valid_synthetic_identity():
    evidence = valid_evidence()
    boundary = make_boundary(evidence)

    actual = boundary.resolve(request_lookup="synthetic-request")

    assert dict(actual) == evidence
    assert actual["authentication_established"] is True


@pytest.mark.parametrize(
    "resolver",
    [None, {}, "untrusted", 123],
)
def test_noncallable_resolver_rejected(resolver):
    with pytest.raises(CertificationIdentityConfigurationError):
        ProvisionedCertificationIdentityBoundary(
            identity_resolver=resolver
        )


@pytest.mark.parametrize(
    "evidence",
    [
        None,
        {},
        [],
        "authenticated",
        {"principal_id": "synthetic-service-001"},
    ],
)
def test_missing_or_invalid_evidence_rejected(evidence):
    with pytest.raises(CertificationIdentityUnavailable):
        make_boundary(evidence).resolve(
            request_lookup="synthetic-request"
        )


@pytest.mark.parametrize(
    "field",
    [
        "principal_id",
        "principal_type",
        "identity_authority",
        "authentication_reference",
    ],
)
def test_blank_identity_fields_rejected(field):
    evidence = valid_evidence()
    evidence[field] = " "

    with pytest.raises(CertificationIdentityUnavailable):
        make_boundary(evidence).resolve(
            request_lookup="synthetic-request"
        )


@pytest.mark.parametrize(
    "value",
    [False, None, 0, 1, "true"],
)
def test_unverified_authentication_rejected(value):
    evidence = valid_evidence()
    evidence["authentication_established"] = value

    with pytest.raises(CertificationIdentityUnavailable):
        make_boundary(evidence).resolve(
            request_lookup="synthetic-request"
        )


def test_unknown_principal_type_rejected():
    evidence = valid_evidence()
    evidence["principal_type"] = "UNKNOWN"

    with pytest.raises(CertificationIdentityUnavailable):
        make_boundary(evidence).resolve(
            request_lookup="synthetic-request"
        )


def test_extra_identity_fields_rejected():
    evidence = valid_evidence()
    evidence["caller_supplied_workspace"] = "untrusted"

    with pytest.raises(CertificationIdentityUnavailable):
        make_boundary(evidence).resolve(
            request_lookup="synthetic-request"
        )


def test_resolver_failure_rejected():
    def unavailable(_lookup):
        raise RuntimeError("synthetic authority failure")

    boundary = ProvisionedCertificationIdentityBoundary(
        identity_resolver=unavailable
    )

    with pytest.raises(CertificationIdentityUnavailable):
        boundary.resolve(
            request_lookup="synthetic-request"
        )


def test_returned_evidence_is_immutable():
    boundary = make_boundary(valid_evidence())

    actual = boundary.resolve(request_lookup="synthetic-request")

    with pytest.raises(TypeError):
        actual["principal_id"] = "attacker"


def test_resolve_does_not_accept_resolver_override():
    boundary = make_boundary(valid_evidence())

    with pytest.raises(TypeError):
        boundary.resolve(
            request_lookup="synthetic-request",
            identity_resolver=lambda _: valid_evidence(),
        )
