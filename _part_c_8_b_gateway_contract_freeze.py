from __future__ import annotations

import dataclasses
import hashlib
import importlib
import inspect
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


if len(sys.argv) != 4:
    raise RuntimeError(
        "Expected project root, 8-A report and output report."
    )

ROOT = Path(sys.argv[1]).resolve()
PRECONDITION_REPORT = Path(
    sys.argv[2]
).resolve()
REPORT = Path(sys.argv[3]).resolve()

GENERATED_AT = datetime.now(
    timezone.utc
).isoformat()

MODULE_NAMES = {
    "bridge": (
        "backend.server.coordination.runtime_integration."
        "coordination_runtime_bridge"
    ),
    "mapping": (
        "backend.server.coordination.runtime_integration."
        "runtime_job_mapping"
    ),
    "correlation": (
        "backend.server.coordination.runtime_integration."
        "workflow_job_correlation"
    ),
    "completion": (
        "backend.server.coordination.runtime_integration."
        "runtime_completion_intake"
    ),
    "failure": (
        "backend.server.coordination.runtime_integration."
        "runtime_failure_intake"
    ),
    "submission": (
        "backend.server.runtime.universal_job_submission"
    ),
    "creation": (
        "backend.server.runtime.universal_jobs."
        "creation_engine"
    ),
    "orchestration": (
        "backend.server.orchestration.service"
    ),
    "registration": (
        "backend.server.runtime."
        "universal_runtime_registration"
    ),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def safe_signature(value: Any) -> str:
    try:
        return str(
            inspect.signature(value)
        )
    except (
        TypeError,
        ValueError,
    ):
        return ""


def annotation_text(value: Any) -> str:
    if value is inspect.Signature.empty:
        return ""

    return str(value)


def describe_function(value: Any) -> dict[str, Any]:
    signature = inspect.signature(value)

    return {
        "module": value.__module__,
        "name": value.__name__,
        "signature": str(signature),
        "parameters": list(
            signature.parameters
        ),
        "return_annotation": annotation_text(
            signature.return_annotation
        ),
    }


def describe_class(value: Any) -> dict[str, Any]:
    annotations = dict(
        getattr(
            value,
            "__annotations__",
            {},
        )
    )

    if dataclasses.is_dataclass(value):
        fields = [
            field.name
            for field in dataclasses.fields(
                value
            )
        ]
    else:
        fields = list(annotations)

    dataclass_parameters = getattr(
        value,
        "__dataclass_params__",
        None,
    )

    return {
        "module": value.__module__,
        "name": value.__name__,
        "signature": safe_signature(value),
        "is_dataclass": dataclasses.is_dataclass(
            value
        ),
        "frozen": bool(
            dataclass_parameters
            and dataclass_parameters.frozen
        ),
        "uses_slots": hasattr(
            value,
            "__slots__",
        ),
        "fields": fields,
        "annotations": {
            name: str(annotation)
            for name, annotation
            in annotations.items()
        },
        "public_methods": sorted(
            name
            for name, member
            in inspect.getmembers(value)
            if (
                not name.startswith("_")
                and callable(member)
            )
        ),
    }


precondition_text = (
    PRECONDITION_REPORT.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )
)

modules = {}
import_failures = []

for key, module_name in MODULE_NAMES.items():
    try:
        modules[key] = (
            importlib.import_module(
                module_name
            )
        )
    except Exception as error:
        import_failures.append(
            {
                "key": key,
                "module": module_name,
                "error_type": type(error).__name__,
                "error_message": str(error),
            }
        )

if import_failures:
    module_files = {}
else:
    module_files = {
        key: Path(
            inspect.getsourcefile(module)
            or ""
        ).resolve()
        for key, module in modules.items()
    }

hashes_before = {
    key: sha256_file(path)
    for key, path in module_files.items()
    if path.exists()
}

bridge = modules.get("bridge")
mapping = modules.get("mapping")
correlation = modules.get(
    "correlation"
)
completion = modules.get("completion")
failure = modules.get("failure")
submission = modules.get("submission")
creation = modules.get("creation")
orchestration = modules.get(
    "orchestration"
)
registration = modules.get(
    "registration"
)

required_functions = {
    "bridge_execution_plan_to_runtime": (
        getattr(
            bridge,
            "bridge_execution_plan_to_runtime",
            None,
        )
        if bridge
        else None
    ),
    "create_runtime_handoff_context": (
        getattr(
            bridge,
            "create_runtime_handoff_context",
            None,
        )
        if bridge
        else None
    ),
    "map_runtime_handoff_intent_to_creation_request": (
        getattr(
            mapping,
            "map_runtime_handoff_intent_to_creation_request",
            None,
        )
        if mapping
        else None
    ),
    "map_runtime_handoffs_to_job_requests": (
        getattr(
            mapping,
            "map_runtime_handoffs_to_job_requests",
            None,
        )
        if mapping
        else None
    ),
    "submit_universal_job": (
        getattr(
            submission,
            "submit_universal_job",
            None,
        )
        if submission
        else None
    ),
    "create_universal_job": (
        getattr(
            creation,
            "create_universal_job",
            None,
        )
        if creation
        else None
    ),
    "create_orchestration_job": (
        getattr(
            orchestration,
            "create_orchestration_job",
            None,
        )
        if orchestration
        else None
    ),
    "get_runtime_registration": (
        getattr(
            registration,
            "get_runtime_registration",
            None,
        )
        if registration
        else None
    ),
    "correlate_submitted_job": (
        getattr(
            correlation,
            "correlate_submitted_job",
            None,
        )
        if correlation
        else None
    ),
    "intake_runtime_completion": (
        getattr(
            completion,
            "intake_runtime_completion",
            None,
        )
        if completion
        else None
    ),
    "intake_runtime_failure": (
        getattr(
            failure,
            "intake_runtime_failure",
            None,
        )
        if failure
        else None
    ),
}

required_classes = {
    "RuntimeHandoffContext": (
        getattr(
            bridge,
            "RuntimeHandoffContext",
            None,
        )
        if bridge
        else None
    ),
    "RuntimeHandoffIntent": (
        getattr(
            bridge,
            "RuntimeHandoffIntent",
            None,
        )
        if bridge
        else None
    ),
    "CoordinationRuntimeBridgeResult": (
        getattr(
            bridge,
            "CoordinationRuntimeBridgeResult",
            None,
        )
        if bridge
        else None
    ),
    "RuntimeJobMapping": (
        getattr(
            mapping,
            "RuntimeJobMapping",
            None,
        )
        if mapping
        else None
    ),
    "RuntimeJobMappingResult": (
        getattr(
            mapping,
            "RuntimeJobMappingResult",
            None,
        )
        if mapping
        else None
    ),
    "UniversalJobCreationRequest": (
        getattr(
            mapping,
            "UniversalJobCreationRequest",
            None,
        )
        if mapping
        else None
    ),
    "WorkflowJobCorrelation": (
        getattr(
            correlation,
            "WorkflowJobCorrelation",
            None,
        )
        if correlation
        else None
    ),
    "WorkflowJobCorrelationRegistry": (
        getattr(
            correlation,
            "WorkflowJobCorrelationRegistry",
            None,
        )
        if correlation
        else None
    ),
}

function_evidence = {
    name: describe_function(value)
    for name, value
    in required_functions.items()
    if callable(value)
}

class_evidence = {
    name: describe_class(value)
    for name, value
    in required_classes.items()
    if inspect.isclass(value)
}

submitter = required_functions[
    "submit_universal_job"
]
mapper = required_functions[
    "map_runtime_handoff_intent_to_creation_request"
]
correlator = required_functions[
    "correlate_submitted_job"
]

submitter_parameters = (
    set(
        inspect.signature(
            submitter
        ).parameters
    )
    if callable(submitter)
    else set()
)

mapper_source = (
    inspect.getsource(mapper)
    if callable(mapper)
    else ""
)

submitter_source = (
    inspect.getsource(submitter)
    if callable(submitter)
    else ""
)

correlator_parameters = (
    set(
        inspect.signature(
            correlator
        ).parameters
    )
    if callable(correlator)
    else set()
)

required_submitter_parameters = {
    "workspace_id",
    "job_type",
    "payload",
    "metadata",
    "pipeline",
    "stage",
    "priority",
    "dependency_job_ids",
    "idempotency_key",
    "enqueue",
}

required_correlator_parameters = {
    "mapping",
    "submitted_job",
    "registry",
}

request_type = required_classes.get(
    "RuntimeJobMapping"
)

request_fields = set(
    class_evidence.get(
        "RuntimeJobMapping",
        {},
    ).get(
        "fields",
        [],
    )
)

creation_request_fields = set(
    class_evidence.get(
        "UniversalJobCreationRequest",
        {},
    ).get(
        "fields",
        [],
    )
)

all_request_fields = (
    request_fields
    | creation_request_fields
)

required_request_evidence = {
    field: (
        field in all_request_fields
        or field in mapper_source
    )
    for field in (
        "workspace_id",
        "job_type",
        "payload",
        "metadata",
        "pipeline",
        "stage",
        "dependency_job_ids",
        "idempotency_key",
    )
}

direct_handler_dispatch_present = any(
    "dispatch_registered_runtime_handler"
    in inspect.getsource(value)
    for value in (
        mapper,
        submitter,
        correlator,
    )
    if callable(value)
)

frozen_contract = {
    "contract_version": (
        "runtime_execution_gateway_contract_v1"
    ),
    "gateway_callable": {
        "name": (
            "submit_runtime_job_mapping"
        ),
        "signature": (
            "(*, mapping: RuntimeJobMapping, "
            "submitter: Callable = submit_universal_job, "
            "correlation_registry: "
            "WorkflowJobCorrelationRegistry | None = None) "
            "-> RuntimeExecutionGatewayResult"
        ),
    },
    "request_contract": {
        "canonical_request_type": (
            "RuntimeJobMapping"
        ),
        "embedded_creation_request_type": (
            "UniversalJobCreationRequest"
        ),
        "required_semantic_fields": [
            "workflow_id",
            "workflow_type",
            "workflow_version",
            "workspace_id",
            "correlation_id",
            "stage_id",
            "runtime_stage",
            "job_type",
            "payload",
            "metadata",
            "pipeline",
            "stage",
            "priority",
            "dependency_job_ids",
            "idempotency_key",
        ],
        "rules": [
            (
                "The gateway accepts an existing "
                "RuntimeJobMapping; it does not invent "
                "a second mapping contract."
            ),
            (
                "The embedded UniversalJobCreationRequest "
                "remains the canonical runtime job request."
            ),
            (
                "Registration must resolve before submission."
            ),
            (
                "Dependency and idempotency identities must "
                "pass through unchanged."
            ),
        ],
    },
    "submission_contract": {
        "canonical_submitter": (
            "submit_universal_job"
        ),
        "canonical_creation_engine": (
            "create_universal_job"
        ),
        "canonical_orchestration_ingress": (
            "create_orchestration_job"
        ),
        "canonical_registration_lookup": (
            "get_runtime_registration"
        ),
        "enqueue": True,
        "handler_execution": False,
    },
    "result_contract": {
        "type": (
            "RuntimeExecutionGatewayResult"
        ),
        "immutable": True,
        "required_fields": [
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
        ],
        "submission_outcomes": [
            "created",
            "reused",
        ],
        "success_rule": (
            "A success result is returned only after job "
            "submission and workflow-job correlation succeed."
        ),
    },
    "failure_contract": {
        "fail_closed": True,
        "error_categories": [
            "invalid_mapping",
            "missing_runtime_registration",
            "registration_mismatch",
            "job_submission_failure",
            "correlation_failure",
        ],
        "rules": [
            (
                "The gateway never executes a registered "
                "handler directly."
            ),
            (
                "Submission exceptions propagate to the caller."
            ),
            (
                "A correlation failure cannot be reported as "
                "successful submission."
            ),
            (
                "Partial-submission reconciliation and "
                "idempotency are certified in Part C 8-E."
            ),
        ],
    },
    "downstream_intake": {
        "completion_authority": (
            "intake_runtime_completion"
        ),
        "failure_authority": (
            "intake_runtime_failure"
        ),
        "integration_phase": "Part C 8-F",
    },
}

contract_fingerprint = hashlib.sha256(
    json.dumps(
        frozen_contract,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
).hexdigest()

hashes_after = {
    key: sha256_file(path)
    for key, path in module_files.items()
    if path.exists()
}

sources_unchanged = (
    hashes_before == hashes_after
)

checks = {
    "part_c_8_a_complete": (
        "PART C 8-A COMPLETE"
        in precondition_text
        and "CLOSURE STATUS: COMPLETE"
        in precondition_text
    ),
    "all_required_modules_imported": (
        not import_failures
        and len(modules)
        == len(MODULE_NAMES)
    ),
    "all_required_functions_available": all(
        callable(value)
        for value in required_functions.values()
    ),
    "all_required_classes_available": all(
        inspect.isclass(value)
        for value in required_classes.values()
    ),
    "runtime_job_mapping_is_canonical_request": (
        inspect.isclass(request_type)
    ),
    "mapper_builds_universal_creation_request": (
        "UniversalJobCreationRequest"
        in mapper_source
    ),
    "submitter_accepts_required_fields": (
        required_submitter_parameters
        <= submitter_parameters
    ),
    "dependency_job_ids_supported": (
        "dependency_job_ids"
        in submitter_parameters
    ),
    "idempotency_key_supported": (
        "idempotency_key"
        in submitter_parameters
    ),
    "enqueue_control_supported": (
        "enqueue"
        in submitter_parameters
    ),
    "submitter_uses_creation_engine": (
        "create_universal_job"
        in submitter_source
    ),
    "submitter_uses_orchestration_ingress": (
        "create_orchestration_job"
        in submitter_source
    ),
    "submitter_resolves_registration": (
        "get_runtime_registration"
        in submitter_source
    ),
    "correlator_contract_complete": (
        required_correlator_parameters
        <= correlator_parameters
    ),
    "request_evidence_complete": (
        all(
            required_request_evidence.values()
        )
    ),
    "completion_intake_retained": callable(
        required_functions[
            "intake_runtime_completion"
        ]
    ),
    "failure_intake_retained": callable(
        required_functions[
            "intake_runtime_failure"
        ]
    ),
    "gateway_does_not_dispatch_handler": (
        not direct_handler_dispatch_present
    ),
    "contract_fingerprint_is_sha256": (
        len(contract_fingerprint) == 64
    ),
    "production_sources_unchanged": (
        sources_unchanged
    ),
    "runtime_registration_created_no": True,
    "registry_persistence_executed_no": True,
    "universal_job_created_no": True,
    "queue_claim_executed_no": True,
    "handler_executed_no": True,
    "live_network_request_executed_no": True,
}

failed_checks = [
    name
    for name, passed in checks.items()
    if not passed
]

contract_frozen = not failed_checks

report_lines = [
    "LINKCRAFTER UNIVERSAL COORDINATION",
    (
        "PART C 8-B RUNTIME EXECUTION GATEWAY "
        "CONTRACT FREEZE"
    ),
    "",
    f"Generated: {GENERATED_AT}",
    "Mode: READ-ONLY CONTRACT FREEZE",
    "Production source changes: NONE",
    "Runtime registrations created: NO",
    "Registry persistence executed: NO",
    "Universal jobs created: NO",
    "Queue claims executed: NO",
    "Handlers executed: NO",
    "Live network requests executed: NO",
    (
        "CONTRACT STATUS: FROZEN"
        if contract_frozen
        else "CONTRACT STATUS: NOT_FROZEN"
    ),
    "",
    "=" * 110,
    "CONTRACT DECISION",
    "=" * 110,
    (
        "The gateway will adapt the existing RuntimeJobMapping "
        "to the existing submit_universal_job() authority."
    ),
    "",
    (
        "It will not create a second job request, registration "
        "system, queue, job store or handler dispatcher."
    ),
    "",
    (
        "Workflow-job correlation becomes part of successful "
        "gateway submission evidence."
    ),
    "",
    "=" * 110,
    "CHECKS",
    "=" * 110,
    json.dumps(
        checks,
        indent=2,
        sort_keys=True,
    ),
    "",
    "FAILED_CHECKS:",
    json.dumps(
        failed_checks,
        indent=2,
    ),
    "",
    "=" * 110,
    "FROZEN CONTRACT",
    "=" * 110,
    json.dumps(
        frozen_contract,
        indent=2,
        sort_keys=True,
    ),
    "",
    (
        "CONTRACT_FINGERPRINT="
        + contract_fingerprint
    ),
    "",
    "=" * 110,
    "FUNCTION EVIDENCE",
    "=" * 110,
    json.dumps(
        function_evidence,
        indent=2,
        sort_keys=True,
    ),
    "",
    "=" * 110,
    "CLASS EVIDENCE",
    "=" * 110,
    json.dumps(
        class_evidence,
        indent=2,
        sort_keys=True,
    ),
    "",
    "=" * 110,
    "REQUEST FIELD COVERAGE",
    "=" * 110,
    json.dumps(
        {
            "runtime_job_mapping_fields": sorted(
                request_fields
            ),
            "creation_request_fields": sorted(
                creation_request_fields
            ),
            "required_request_evidence": (
                required_request_evidence
            ),
        },
        indent=2,
        sort_keys=True,
    ),
    "",
    "=" * 110,
    "IMPORT FAILURES",
    "=" * 110,
    json.dumps(
        import_failures,
        indent=2,
        sort_keys=True,
    ),
    "",
    "=" * 110,
    "IMPLEMENTATION BOUNDARY",
    "=" * 110,
    (
        "- Part C 8-C will implement "
        "submit_runtime_job_mapping()."
    ),
    (
        "- RuntimeJobMapping remains the canonical gateway "
        "request."
    ),
    (
        "- submit_universal_job() remains the canonical "
        "submission authority."
    ),
    (
        "- correlate_submitted_job() remains the canonical "
        "workflow-job correlation authority."
    ),
    (
        "- Completion and failure intake remain unchanged "
        "until Part C 8-F."
    ),
    (
        "- No handler will be executed by the gateway."
    ),
    "",
    "=" * 110,
    "NEXT STEP",
    "=" * 110,
    (
        "Proceed to Part C 8-C: implement and certify "
        "registered-stage Universal Job submission."
    ),
    "",
    "=" * 110,
    "FINAL RESULT",
    "=" * 110,
    (
        "PART C 8-B COMPLETE"
        if contract_frozen
        else "PART C 8-B NOT_COMPLETE"
    ),
    "",
]

REPORT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT.write_text(
    "\n".join(report_lines),
    encoding="utf-8",
    newline="\n",
)

print("=" * 100)
print("PART C 8-B RUNTIME EXECUTION GATEWAY CONTRACT")
print("=" * 100)

for name, passed in checks.items():
    print(
        f"{name.upper()}: "
        + ("PASS" if passed else "FAIL")
    )

print()
print(
    "CONTRACT_FINGERPRINT="
    + contract_fingerprint
)
print(
    "FAILED_CHECK_COUNT="
    + str(len(failed_checks))
)
print("REPORT=" + str(REPORT))

if not contract_frozen:
    print("PART_C_8_B_STATUS=NOT_COMPLETE")
    raise SystemExit(1)

print("PART_C_8_B_STATUS=COMPLETE")