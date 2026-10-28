"""Phase 3.6.1P: V2 reference-integrity and context handoff.

Internal primitive only. A trusted backend integration must provision
issuer keys and independently resolve expected context before calling.
"""

from backend.server.engine.semantic_memory_certification_reference_adapter import (
    inspect_semantic_memory_certification_reference,
)
from backend.server.engine.semantic_memory_certification_context_verifier_v2 import (
    verify_semantic_memory_context_v2,
)


def verify_semantic_memory_context_handoff_v2(
    *,
    expected_context,
    certification_result,
    final_package,
    retrieval_bundle,
    attestation,
    trusted_issuers,
):
    """Run the genuine reference adapter before V2 signature verification.

    The expected context must be resolved independently by trusted code.
    Never pass caller-provided identities directly into this primitive.
    """
    result = {
        "schema": "semantic_memory_context_handoff_v2",
        "reference_integrity_valid": False,
        "context_signature_verified": False,
        "context_binding_verified": False,
        "fully_certified": False,
        "consumption_authorized": False,
        "status": "UNVERIFIED",
        "reference_result": None,
        "context_result": None,
    }

    if not isinstance(expected_context, dict):
        result["status"] = "TRUSTED_CONTEXT_UNAVAILABLE"
        return result

    required = {
        "workspace_id",
        "operational_memory_id",
        "canonical_memory_object_id",
    }

    if set(expected_context) != required:
        result["status"] = "TRUSTED_CONTEXT_UNAVAILABLE"
        return result

    reference = inspect_semantic_memory_certification_reference(
        workspace_id=expected_context["workspace_id"],
        operational_memory_id=expected_context["operational_memory_id"],
        canonical_memory_object_id=expected_context[
            "canonical_memory_object_id"
        ],
        certification_result=certification_result,
        final_package=final_package,
        retrieval_bundle=retrieval_bundle,
    )

    result["reference_result"] = reference

    if reference.get("reference_integrity_valid") is not True:
        result["status"] = "REFERENCE_REJECTED"
        return result

    result["reference_integrity_valid"] = True

    context = verify_semantic_memory_context_v2(
        reference_result=reference,
        final_package=final_package,
        attestation=attestation,
        expected_context=expected_context,
        trusted_issuers=trusted_issuers,
    )

    result["context_result"] = context

    if (
        context.get("context_signature_verified") is True
        and context.get("context_binding_verified") is True
    ):
        result["context_signature_verified"] = True
        result["context_binding_verified"] = True
        result["status"] = "SIGNED_CONTEXT_MATCHED"
    else:
        result["status"] = "CONTEXT_REJECTED"

    return result
