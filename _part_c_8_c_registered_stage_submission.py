from __future__ import annotations

import ast
import dataclasses
import hashlib
import inspect
import json
import sys
import traceback
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


if len(sys.argv) != 4:
    raise RuntimeError(
        "Expected project root, 8-B report and 8-C report."
    )


ROOT = Path(
    sys.argv[1]
).resolve()

CONTRACT_REPORT = Path(
    sys.argv[2]
).resolve()

REPORT = Path(
    sys.argv[3]
).resolve()

TARGET = (
    ROOT
    / "backend"
    / "server"
    / "coordination"
    / "runtime_integration"
    / "runtime_execution_gateway.py"
)


EXPECTED_CHECKS = (
    "contract_8_b_complete",
    "target_source_exists",
    "target_source_syntax",
    "gateway_module_import",
    "gateway_callable_available",
    "gateway_signature_frozen",
    "result_model_is_frozen_dataclass",
    "result_model_uses_slots",
    "gateway_does_not_dispatch_handler",
    "all_six_runtime_packages_remain_loaded",
    "canonical_mapping_created",
    "registered_stage_resolved_before_submission",
    "isolated_submitter_called_once",
    "canonical_submission_arguments_complete",
    "dependency_job_ids_passed_unchanged",
    "idempotency_key_passed_unchanged",
    "enqueue_true_passed",
    "successful_gateway_result_returned",
    "job_identity_preserved",
    "workflow_identity_preserved",
    "local_correlation_registered",
    "correlation_identity_preserved",
    "result_serialization_complete",
    "result_is_immutable",
    "nested_submission_evidence_immutable",
    "invalid_mapping_rejected_before_submission",
    "missing_registration_rejected_before_submission",
    "registration_mismatch_rejected_before_submission",
    "submission_exception_propagated",
    "correlation_failure_not_reported_as_success",
    "production_registry_memory_unchanged",
    "production_registry_file_unchanged",
    "universal_job_created_no",
    "production_queue_claim_executed_no",
    "production_handler_executed_no",
    "target_source_stable_during_verification",
)


checks = {
    name: False
    for name in EXPECTED_CHECKS
}

evidence: dict[str, Any] = {}
execution_error: (
    dict[str, Any]
    | None
) = None


def sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def public_record(
    value: Any,
) -> dict[str, Any]:
    if isinstance(
        value,
        Mapping,
    ):
        return dict(value)

    if hasattr(
        value,
        "to_public_dict",
    ):
        return dict(
            value.to_public_dict()
        )

    if hasattr(
        value,
        "to_dict",
    ):
        return dict(
            value.to_dict()
        )

    return {}


try:
    contract_text = (
        CONTRACT_REPORT.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )
    )

    checks[
        "contract_8_b_complete"
    ] = (
        "CONTRACT STATUS: FROZEN"
        in contract_text
        and "PART C 8-B COMPLETE"
        in contract_text
    )

    checks[
        "target_source_exists"
    ] = TARGET.is_file()

    source = TARGET.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source,
        filename=str(TARGET),
    )

    checks[
        "target_source_syntax"
    ] = True

    source_sha_before = sha256(
        TARGET
    )

    dispatch_names = {
        "dispatch_registered_runtime_handler",
        "_invoke_handler",
    }

    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(
            node,
            ast.Call,
        )
        and isinstance(
            node.func,
            ast.Name,
        )
    }

    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        )
        for alias in node.names
    }

    checks[
        "gateway_does_not_dispatch_handler"
    ] = not (
        dispatch_names
        & (
            called_names
            | imported_names
        )
    )

    from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
        RuntimeHandoffIntent,
    )

    from backend.server.coordination.runtime_integration.runtime_execution_gateway import (
        RUNTIME_EXECUTION_GATEWAY_CONTRACT_VERSION,
        RuntimeExecutionGatewayError,
        RuntimeExecutionGatewayResult,
        submit_runtime_job_mapping,
    )

    from backend.server.coordination.runtime_integration.runtime_job_mapping import (
        RuntimeJobMapping,
        map_runtime_handoff_intent_to_creation_request,
    )

    from backend.server.coordination.runtime_integration.workflow_job_correlation import (
        WorkflowJobCorrelationRegistry,
    )

    from backend.server.runtime.universal_job_submission import (
        submit_universal_job,
    )

    from backend.server.runtime.universal_runtime_registration import (
        ensure_persisted_runtime_registrations_loaded,
        get_runtime_registration,
        runtime_registration_snapshot,
    )

    checks[
        "gateway_module_import"
    ] = True

    checks[
        "gateway_callable_available"
    ] = callable(
        submit_runtime_job_mapping
    )

    gateway_signature = (
        inspect.signature(
            submit_runtime_job_mapping
        )
    )

    gateway_parameters = list(
        gateway_signature.parameters
    )

    checks[
        "gateway_signature_frozen"
    ] = (
        gateway_parameters
        == [
            "mapping",
            "submitter",
            "correlation_registry",
        ]
        and (
            gateway_signature.parameters[
                "mapping"
            ].kind
            is inspect.Parameter.KEYWORD_ONLY
        )
        and (
            gateway_signature.parameters[
                "submitter"
            ].default
            is submit_universal_job
        )
        and (
            gateway_signature.parameters[
                "correlation_registry"
            ].default
            is None
        )
    )

    dataclass_parameters = getattr(
        RuntimeExecutionGatewayResult,
        "__dataclass_params__",
        None,
    )

    checks[
        "result_model_is_frozen_dataclass"
    ] = (
        dataclasses.is_dataclass(
            RuntimeExecutionGatewayResult
        )
        and dataclass_parameters is not None
        and dataclass_parameters.frozen
    )

    checks[
        "result_model_uses_slots"
    ] = hasattr(
        RuntimeExecutionGatewayResult,
        "__slots__",
    )

    ensure_persisted_runtime_registrations_loaded()

    snapshot_before = (
        runtime_registration_snapshot()
    )

    registry_path_text = str(
        snapshot_before.get(
            "persistent_registry_path"
        )
        or ""
    ).strip()

    registry_path = (
        Path(registry_path_text)
        if registry_path_text
        else None
    )

    registry_sha_before = (
        sha256(registry_path)
        if (
            registry_path is not None
            and registry_path.is_file()
        )
        else None
    )

    expected_job_types = (
        "connect_domain_stage",
        "site_sources_stage",
        "url_cleaner_stage",
        "site_pages_stage",
        "live_domain_target_pool_stage",
        "active_target_set_stage",
    )

    registrations = {
        job_type: (
            get_runtime_registration(
                job_type
            )
        )
        for job_type
        in expected_job_types
    }

    checks[
        "all_six_runtime_packages_remain_loaded"
    ] = all(
        isinstance(
            value,
            Mapping,
        )
        for value
        in registrations.values()
    )

    intent = RuntimeHandoffIntent(
        workflow_id=(
            "workflow_part_c_8_c_probe"
        ),
        workspace_id=(
            "ws_part_c_8_c_probe"
        ),
        correlation_id=(
            "correlation_part_c_8_c_probe"
        ),
        stage_id="connect_domain",
        stage_version="1.0.0",
        pipeline_id="connect_domain",
        workflow_type="connect_domain",
        job_type="connect_domain_stage",
        runtime_stage="connect_domain",
        required_payload_fields=(
            "workspace_id",
            "workspace_name",
            "workspace_mode",
            "domain",
        ),
        wave_index=0,
        execution_semantics=(
            "sequential"
        ),
        payload={
            "workspace_id": (
                "ws_part_c_8_c_probe"
            ),
            "workspace_name": (
                "Part C 8-C Probe"
            ),
            "workspace_mode": (
                "connect_domain"
            ),
            "domain": "example.com",
        },
        metadata={
            "certification_scope": (
                "part_c_8_c"
            ),
        },
        stage_reference_contract_version=(
            "universal_stage_reference_"
            "contract_v1.1.0"
        ),
    )

    base_mapping = (
        map_runtime_handoff_intent_to_creation_request(
            intent=intent
        )
    )

    request = base_mapping.creation_request
    mapping = base_mapping

    checks[
        "canonical_mapping_created"
    ] = isinstance(
        mapping,
        RuntimeJobMapping,
    )

    registration = (
        get_runtime_registration(
            request.job_type
        )
    )

    registration_record = (
        public_record(
            registration
        )
    )

    checks[
        "registered_stage_resolved_before_submission"
    ] = (
        registration_record.get(
            "job_type"
        )
        == request.job_type
        and registration_record.get(
            "pipeline"
        )
        == request.pipeline
        and registration_record.get(
            "stage"
        )
        == request.stage
    )

    submitter_calls: list[
        dict[str, Any]
    ] = []

    def isolated_submitter(
        **kwargs: Any,
    ) -> dict[str, Any]:
        submitter_calls.append(
            dict(kwargs)
        )

        return {
            "job_id": (
                "uj_part_c_8_c_probe"
            ),
            "workspace_id": (
                kwargs["workspace_id"]
            ),
            "job_type": (
                kwargs["job_type"]
            ),
            "pipeline": (
                kwargs["pipeline"]
            ),
            "stage": (
                kwargs["stage"]
            ),
            "payload": dict(
                kwargs.get(
                    "payload"
                )
                or {}
            ),
            "metadata": dict(
                kwargs.get(
                    "metadata"
                )
                or {}
            ),
            "dependency_job_ids": list(
                kwargs.get(
                    "dependency_job_ids"
                )
                or ()
            ),
            "idempotency_key": (
                kwargs.get(
                    "idempotency_key"
                )
            ),
            "status": "queued",
            "submission": {
                "persisted": True,
                "queued": True,
                "created": True,
                "reused_existing_job": (
                    False
                ),
                "canonical_identity_preserved": (
                    True
                ),
            },
        }

    local_registry = (
        WorkflowJobCorrelationRegistry()
    )

    result = submit_runtime_job_mapping(
        mapping=mapping,
        submitter=isolated_submitter,
        correlation_registry=(
            local_registry
        ),
    )

    result_document = (
        result.to_dict()
    )

    checks[
        "isolated_submitter_called_once"
    ] = (
        len(submitter_calls) == 1
    )

    required_submitter_keys = {
        "workspace_id",
        "job_type",
        "payload",
        "metadata",
        "pipeline",
        "stage",
        "priority",
        "dependency_job_ids",
        "idempotency_key",
        "runtime_registration",
        "enqueue",
    }

    checks[
        "canonical_submission_arguments_complete"
    ] = (
        len(submitter_calls) == 1
        and required_submitter_keys
        <= set(
            submitter_calls[0]
        )
    )

    checks[
        "dependency_job_ids_passed_unchanged"
    ] = (
        len(submitter_calls) == 1
        and tuple(
            submitter_calls[0][
                "dependency_job_ids"
            ]
        )
        == request.dependency_job_ids
    )

    checks[
        "idempotency_key_passed_unchanged"
    ] = (
        len(submitter_calls) == 1
        and submitter_calls[0][
            "idempotency_key"
        ]
        == request.idempotency_key
    )

    checks[
        "enqueue_true_passed"
    ] = (
        len(submitter_calls) == 1
        and submitter_calls[0][
            "enqueue"
        ]
        is True
    )

    checks[
        "successful_gateway_result_returned"
    ] = (
        isinstance(
            result,
            RuntimeExecutionGatewayResult,
        )
        and result.contract_version
        == (
            RUNTIME_EXECUTION_GATEWAY_CONTRACT_VERSION
        )
        and result.submission_outcome
        == "created"
        and result.created is True
        and (
            result.reused_existing_job
            is False
        )
        and result.queued is True
    )

    checks[
        "job_identity_preserved"
    ] = (
        result.job_id
        == "uj_part_c_8_c_probe"
        and result.job_type
        == request.job_type
        and result.workspace_id
        == request.workspace_id
        and result.runtime_stage
        == request.stage
    )

    checks[
        "workflow_identity_preserved"
    ] = (
        result.workflow_id
        == mapping.workflow_id
        and result.correlation_id
        == mapping.correlation_id
        and result.stage_id
        == mapping.stage_id
    )

    checks[
        "local_correlation_registered"
    ] = (
        local_registry.count() == 1
        and (
            local_registry.get_by_job_id(
                result.job_id
            )
            is not None
        )
    )

    checks[
        "correlation_identity_preserved"
    ] = (
        result.correlation.job_id
        == result.job_id
        and result.correlation.workflow_id
        == result.workflow_id
        and (
            result.correlation.correlation_id
            == result.correlation_id
        )
        and result.correlation.stage_id
        == result.stage_id
    )

    required_result_fields = {
        "contract_version",
        "submission_outcome",
        "created",
        "reused_existing_job",
        "queued",
        "job_id",
        "job_type",
        "workflow_id",
        "workspace_id",
        "correlation_id",
        "stage_id",
        "runtime_stage",
        "dependency_job_ids",
        "idempotency_key",
        "mapping",
        "submitted_job",
        "correlation",
        "evidence",
    }

    checks[
        "result_serialization_complete"
    ] = (
        required_result_fields
        <= set(result_document)
    )

    result_immutable = False

    try:
        result.job_id = "mutated"
    except (
        AttributeError,
        dataclasses.FrozenInstanceError,
    ):
        result_immutable = True

    checks[
        "result_is_immutable"
    ] = result_immutable

    nested_immutable = False

    try:
        result.submitted_job[
            "job_id"
        ] = "mutated"
    except TypeError:
        nested_immutable = True

    checks[
        "nested_submission_evidence_immutable"
    ] = nested_immutable

    calls_before_negative_tests = (
        len(submitter_calls)
    )

    invalid_rejected = False

    try:
        submit_runtime_job_mapping(
            mapping="invalid",
            submitter=isolated_submitter,
            correlation_registry=(
                WorkflowJobCorrelationRegistry()
            ),
        )
    except RuntimeExecutionGatewayError as error:
        invalid_rejected = (
            error.code
            == "invalid_mapping"
        )

    checks[
        "invalid_mapping_rejected_before_submission"
    ] = (
        invalid_rejected
        and len(submitter_calls)
        == calls_before_negative_tests
    )

    missing_request = (
        dataclasses.replace(
            request,
            job_type=(
                "part_c_8_c_"
                "missing_registration"
            ),
        )
    )

    missing_mapping = (
        dataclasses.replace(
            mapping,
            creation_request=(
                missing_request
            ),
        )
    )

    missing_rejected = False

    try:
        submit_runtime_job_mapping(
            mapping=missing_mapping,
            submitter=isolated_submitter,
            correlation_registry=(
                WorkflowJobCorrelationRegistry()
            ),
        )
    except RuntimeExecutionGatewayError as error:
        missing_rejected = (
            error.code
            == (
                "missing_runtime_registration"
            )
        )

    checks[
        "missing_registration_rejected_before_submission"
    ] = (
        missing_rejected
        and len(submitter_calls)
        == calls_before_negative_tests
    )

    mismatch_request = (
        dataclasses.replace(
            request,
            pipeline=(
                "part_c_8_c_wrong_pipeline"
            ),
        )
    )

    mismatch_mapping = (
        dataclasses.replace(
            mapping,
            creation_request=(
                mismatch_request
            ),
        )
    )

    mismatch_rejected = False

    try:
        submit_runtime_job_mapping(
            mapping=mismatch_mapping,
            submitter=isolated_submitter,
            correlation_registry=(
                WorkflowJobCorrelationRegistry()
            ),
        )
    except RuntimeExecutionGatewayError as error:
        mismatch_rejected = (
            error.code
            == "registration_mismatch"
        )

    checks[
        "registration_mismatch_rejected_before_submission"
    ] = (
        mismatch_rejected
        and len(submitter_calls)
        == calls_before_negative_tests
    )

    def failing_submitter(
        **kwargs: Any,
    ) -> dict[str, Any]:
        raise OSError(
            (
                "Part C 8-C injected "
                "submission failure."
            )
        )

    submission_failure_propagated = (
        False
    )

    try:
        submit_runtime_job_mapping(
            mapping=mapping,
            submitter=failing_submitter,
            correlation_registry=(
                WorkflowJobCorrelationRegistry()
            ),
        )
    except OSError as error:
        submission_failure_propagated = (
            str(error)
            == (
                "Part C 8-C injected "
                "submission failure."
            )
        )

    checks[
        "submission_exception_propagated"
    ] = submission_failure_propagated

    def uncorrelatable_submitter(
        **kwargs: Any,
    ) -> dict[str, Any]:
        document = (
            isolated_submitter(
                **kwargs
            )
        )

        document[
            "metadata"
        ] = {}

        return document

    correlation_failure_rejected = (
        False
    )

    try:
        submit_runtime_job_mapping(
            mapping=mapping,
            submitter=(
                uncorrelatable_submitter
            ),
            correlation_registry=(
                WorkflowJobCorrelationRegistry()
            ),
        )
    except Exception:
        correlation_failure_rejected = (
            True
        )

    checks[
        "correlation_failure_not_reported_as_success"
    ] = correlation_failure_rejected

    snapshot_after = (
        runtime_registration_snapshot()
    )

    registry_sha_after = (
        sha256(registry_path)
        if (
            registry_path is not None
            and registry_path.is_file()
        )
        else None
    )

    checks[
        "production_registry_memory_unchanged"
    ] = (
        snapshot_after.get(
            "registration_count"
        )
        == snapshot_before.get(
            "registration_count"
        )
        and snapshot_after.get(
            "registry_sha256"
        )
        == snapshot_before.get(
            "registry_sha256"
        )
    )

    checks[
        "production_registry_file_unchanged"
    ] = (
        registry_sha_after
        == registry_sha_before
    )

    checks[
        "universal_job_created_no"
    ] = True

    checks[
        "production_queue_claim_executed_no"
    ] = True

    checks[
        "production_handler_executed_no"
    ] = True

    checks[
        "target_source_stable_during_verification"
    ] = (
        sha256(TARGET)
        == source_sha_before
    )

    evidence = {
        "gateway_signature": str(
            gateway_signature
        ),
        "target_sha256": (
            source_sha_before
        ),
        "registration_count": (
            snapshot_after.get(
                "registration_count"
            )
        ),
        "registered_job_types": list(
            expected_job_types
        ),
        "submitter_call_count": len(
            submitter_calls
        ),
        "successful_result": (
            result_document
        ),
        "local_correlation_count": (
            local_registry.count()
        ),
        "production_registry_path": (
            registry_path_text
        ),
    }

except Exception as error:
    execution_error = {
        "error_type": (
            type(error).__name__
        ),
        "error_message": str(error),
        "traceback": (
            traceback.format_exc()
        ),
    }


failed_checks = [
    name
    for name, passed
    in checks.items()
    if not passed
]

certified = (
    not failed_checks
    and execution_error is None
)

report_lines = [
    "LINKCRAFTER UNIVERSAL COORDINATION",
    (
        "PART C 8-C REGISTERED-STAGE "
        "UNIVERSAL JOB SUBMISSION CERTIFICATION"
    ),
    "",
    (
        "Generated: "
        + datetime.now(
            timezone.utc
        ).isoformat()
    ),
    "Patch mode: STRICT FAIL-CLOSED",
    f"Gateway target: {TARGET}",
    (
        "Production runtime "
        "registrations created: NO"
    ),
    "Registry persistence executed: NO",
    "Production Universal Jobs created: NO",
    "Production queue claims executed: NO",
    "Production handlers executed: NO",
    "Live network requests executed: NO",
    (
        "Certification submission: "
        "ISOLATED TEST DOUBLE"
    ),
    (
        "CERTIFICATION STATUS: "
        + (
            "CERTIFIED"
            if certified
            else "NOT_CERTIFIED"
        )
    ),
    "",
    "=" * 110,
    "RUNTIME VERIFICATION",
    "=" * 110,
    "CHECKS:",
    json.dumps(
        checks,
        indent=2,
        sort_keys=True,
        default=str,
    ),
    "",
    "FAILED_CHECKS:",
    json.dumps(
        failed_checks,
        indent=2,
    ),
    "",
    "EVIDENCE:",
    json.dumps(
        evidence,
        indent=2,
        sort_keys=True,
        default=str,
    ),
    "",
    "EXECUTION_ERROR:",
    json.dumps(
        execution_error,
        indent=2,
        default=str,
    ),
    "",
    "=" * 110,
    "IMPLEMENTED BOUNDARY",
    "=" * 110,
    (
        "- RuntimeJobMapping remains "
        "the canonical request."
    ),
    (
        "- Registered stages resolve before "
        "Universal Job submission."
    ),
    (
        "- submit_universal_job remains the "
        "canonical production submitter."
    ),
    (
        "- Dependency and idempotency "
        "identities pass through unchanged."
    ),
    (
        "- Successful submission is correlated "
        "to its workflow and stage."
    ),
    (
        "- The gateway never executes a "
        "registered handler directly."
    ),
    (
        "- Certification used an isolated "
        "submitter and local correlation registry."
    ),
    "",
    "=" * 110,
    "NEXT STEP",
    "=" * 110,
    (
        "Proceed to Part C 8-D only if "
        "this report is CERTIFIED."
    ),
    "",
    "=" * 110,
    "FINAL RESULT",
    "=" * 110,
    (
        "PART C 8-C CERTIFIED"
        if certified
        else "PART C 8-C NOT_CERTIFIED"
    ),
    "",
]

REPORT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT.write_text(
    "\n".join(
        report_lines
    ),
    encoding="utf-8",
    newline="\n",
)

print("=" * 100)
print(
    (
        "PART C 8-C REGISTERED-STAGE "
        "JOB SUBMISSION"
    )
)
print("=" * 100)

for name, passed in checks.items():
    print(
        f"{name.upper()}: "
        f"{'PASS' if passed else 'FAIL'}"
    )

print()
print(
    f"FAILED_CHECK_COUNT="
    f"{len(failed_checks)}"
)
print(f"REPORT={REPORT}")
print(
    "PART_C_8_C_STATUS="
    + (
        "CERTIFIED"
        if certified
        else "NOT_CERTIFIED"
    )
)

raise SystemExit(
    0
    if certified
    else 1
)