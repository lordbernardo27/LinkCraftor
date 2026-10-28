"""Phase 3.6.1O: trusted Semantic Memory verification handoff.

Use only within a trusted backend boundary. The issuer registry must
come from trusted configuration, never untrusted request data.
"""

from backend.server.engine.semantic_memory_certification_reference_adapter import (
    inspect_semantic_memory_certification_reference,
)
from backend.server.engine.semantic_memory_certification_authority_verifier import (
    verify_semantic_memory_authority,
)


def verify_semantic_memory_certification_handoff(
    *,
    workspace_id,
    operational_memory_id,
    canonical_memory_object_id,
    certification_result,
    final_package,
    retrieval_bundle,
    attestation,
    trusted_issuers,
):
    """Execute reference verification before issuer verification.

    This function does not accept a caller-supplied reference_result.
    All outputs remain non-authorizing until later mandatory checks.
    """
    reference = inspect_semantic_memory_certification_reference(
        workspace_id=workspace_id,
        operational_memory_id=operational_memory_id,
        canonical_memory_object_id=canonical_memory_object_id,
        certification_result=certification_result,
        final_package=final_package,
        retrieval_bundle=retrieval_bundle,
    )

    if reference.get("reference_integrity_valid") is not True:
        return {
            "schema":
                "semantic_memory_trusted_handoff_result_v1",
            "reference_result": reference,
            "authority_result": None,
            "reference_integrity_valid": False,
            "authority_signature_verified": False,
            "fully_certified": False,
            "consumption_authorized": False,
            "status": "REFERENCE_REJECTED",
        }

    authority = verify_semantic_memory_authority(
        reference_result=reference,
        final_package=final_package,
        attestation=attestation,
        trusted_issuers=trusted_issuers,
    )

    verified = (
        authority.get("authority_signature_verified") is True
    )

    return {
        "schema": "semantic_memory_trusted_handoff_result_v1",
        "reference_result": reference,
        "authority_result": authority,
        "reference_integrity_valid": True,
        "authority_signature_verified": verified,
        "fully_certified": False,
        "consumption_authorized": False,
        "status": (
            "ISSUER_SIGNATURE_VERIFIED"
            if verified
            else "AUTHORITY_REJECTED"
        ),
    }
