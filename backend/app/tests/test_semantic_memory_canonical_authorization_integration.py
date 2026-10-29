"""PT2C.6 ? Canonical authorization integration regressions."""

from backend.server.runtime.security.runtime_authentication_boundaries import (
    RuntimeAuthenticationBoundary,
    RuntimeAuthenticationBoundaryRequest,
    RuntimePrincipalIdentity,
    RuntimePrincipalType,
    evaluate_runtime_authentication_boundary,
)
from backend.server.runtime.security.runtime_authorization import (
    RuntimeOperation,
    RuntimeAuthorizationEvidence,
    RuntimeAuthorizationRequest,
    BOUNDARY_OPERATION_MAP,
    evaluate_runtime_authorization,
)


OPERATION = RuntimeOperation.SEMANTIC_MEMORY_CERTIFICATION_CONTEXT_READ
BOUNDARY = RuntimeAuthenticationBoundary.SEMANTIC_MEMORY_CERTIFICATION_CONTEXT_READ


def principal(principal_type=RuntimePrincipalType.USER):
    return RuntimePrincipalIdentity(
        principal_type=principal_type,
        principal_id="certification-test-user",
    )


def boundary_decision(user):
    return evaluate_runtime_authentication_boundary(
        RuntimeAuthenticationBoundaryRequest(
            principal=user,
            boundary=BOUNDARY,
        )
    )


def evaluate(*, authenticated=True, grant=True, workspace="ws_a"):
    user = principal()
    decision = boundary_decision(user)

    evidence = RuntimeAuthorizationEvidence(
        authentication_established=authenticated,
        granted_operations=(OPERATION,) if grant else (),
        allowed_resource_ids=(workspace,),
        authorization_source="synthetic-test-only",
        authorization_reference="synthetic-test-only",
    )

    return evaluate_runtime_authorization(
        request=RuntimeAuthorizationRequest(
            principal=user,
            authentication_boundary_decision=decision,
            operation=OPERATION,
            resource_id="ws_a",
        ),
        evidence=evidence,
    )


def test_exact_canonical_operation_mapping():
    assert BOUNDARY_OPERATION_MAP[BOUNDARY] is OPERATION


def test_user_may_enter_structural_boundary():
    decision = boundary_decision(principal())
    assert decision.disposition.value == "PROCEED_TO_AUTHENTICATION"


def test_administrator_has_no_implicit_workspace_access():
    decision = boundary_decision(
        principal(RuntimePrincipalType.ADMINISTRATOR)
    )
    assert decision.disposition.value == "REJECT"


def test_explicit_synthetic_grant_still_denied():
    result = evaluate()
    assert result.disposition.value == "DENY"
    assert result.reason_code == (
        "semantic_memory_production_authority_unavailable"
    )


def test_missing_authentication_denied():
    assert evaluate(authenticated=False).disposition.value == "DENY"


def test_missing_operation_grant_denied():
    assert evaluate(grant=False).disposition.value == "DENY"


def test_other_workspace_denied():
    assert evaluate(workspace="ws_b").disposition.value == "DENY"


def test_generic_runtime_operations_not_equivalent():
    assert OPERATION is not RuntimeOperation.ADMINISTER_RUNTIME
    assert OPERATION is not RuntimeOperation.CALL_INTERNAL_SERVICE
    assert OPERATION is not RuntimeOperation.SUBMIT_JOB
