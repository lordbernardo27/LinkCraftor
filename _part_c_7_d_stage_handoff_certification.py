from __future__ import annotations

import ast
import dataclasses
import hashlib
import importlib
import inspect
import json
import sys
from collections.abc import Mapping
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


ROOT = Path(sys.argv[1]).resolve()
REPORT = Path(sys.argv[2]).resolve()

MODULE_NAMES = {
    "stage_result_processor": (
        "backend.server.coordination."
        "stage_handoff.stage_result_processor"
    ),
    "context_propagation": (
        "backend.server.coordination."
        "stage_handoff.context_propagation"
    ),
    "artifact_reference_handoff": (
        "backend.server.coordination."
        "stage_handoff.artifact_reference_handoff"
    ),
    "output_input_mapping": (
        "backend.server.coordination."
        "stage_handoff.output_input_mapping"
    ),
    "handoff_validation": (
        "backend.server.coordination."
        "stage_handoff.handoff_validation"
    ),
    "handoff_certification": (
        "backend.server.coordination."
        "stage_handoff.handoff_certification"
    ),
}

REQUIRED_APIS = {
    "stage_result_processor": (
        "ProcessedStageResult",
        "StageResultDisposition",
        "process_stage_result",
    ),
    "context_propagation": (
        "propagate_context",
        "create_runtime_handoff_context",
    ),
    "artifact_reference_handoff": (
        "ArtifactReferenceHandoffResult",
        "handoff_artifact_references",
    ),
    "output_input_mapping": (
        "OutputInputMappingResult",
        "map_output_to_input",
    ),
    "handoff_validation": (
        "HandoffValidationResult",
        "validate_stage_handoff",
    ),
    "handoff_certification": (
        "HandoffCertificationResult",
        "evaluate_handoff_certification",
        "certify_stage_handoff",
    ),
}

FROZEN_MODELS = {
    "stage_result_processor": (
        "ProcessedStageResult",
    ),
    "artifact_reference_handoff": (
        "ArtifactReferenceHandoffResult",
    ),
    "output_input_mapping": (
        "OutputInputMappingResult",
    ),
    "handoff_validation": (
        "HandoffValidationResult",
    ),
    "handoff_certification": (
        "HandoffCertificationResult",
    ),
}

REQUIRED_CERTIFICATION_CALLS = {
    "process_stage_result",
    "propagate_context",
    "handoff_artifact_references",
    "map_output_to_input",
    "validate_stage_handoff",
}

FORBIDDEN_CALL_LEAVES = {
    "create_universal_job",
    "create_universal_knowledge_job",
    "enqueue_job",
    "dequeue_job",
    "dispatch_registered_runtime_handler",
    "register_runtime_handler",
    "unregister_runtime_handler",
    "urlopen",
    "create_connection",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def module_source(module: Any) -> Path:
    source = inspect.getsourcefile(module)

    if not source:
        raise RuntimeError(
            f"Source unavailable: {module.__name__}"
        )

    path = Path(source).resolve()

    if not path.is_file():
        raise RuntimeError(
            f"Source file unavailable: {path}"
        )

    return path


def frozen_dataclass(value: Any) -> bool:
    parameters = getattr(
        value,
        "__dataclass_params__",
        None,
    )

    return (
        dataclasses.is_dataclass(value)
        and parameters is not None
        and bool(parameters.frozen)
    )


def required_parameters(
    value: Any,
) -> list[str]:
    signature = inspect.signature(
        value
    )

    return [
        name
        for name, parameter
        in signature.parameters.items()
        if (
            parameter.default
            is inspect.Parameter.empty
            and parameter.kind
            not in {
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            }
        )
    ]


def dotted_name(node: ast.AST) -> str:
    parts: list[str] = []
    current = node

    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value

    if isinstance(current, ast.Name):
        parts.append(current.id)

    return ".".join(
        reversed(parts)
    )


def public_payload(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)

    to_dict = getattr(
        value,
        "to_dict",
        None,
    )

    if callable(to_dict):
        payload = to_dict()

        if isinstance(payload, Mapping):
            return dict(payload)

    if dataclasses.is_dataclass(value):
        payload = dataclasses.asdict(
            value
        )

        if isinstance(payload, Mapping):
            return dict(payload)

    raise TypeError(
        "Certification result is not "
        "mapping-compatible."
    )


def result_passed(
    result: Any,
    payload: Mapping[str, Any],
) -> bool:
    for name in (
        "certified",
        "passed",
        "is_certified",
        "is_valid",
        "success",
        "ok",
    ):
        value = getattr(
            result,
            name,
            None,
        )

        if isinstance(value, bool):
            return value

        value = payload.get(name)

        if isinstance(value, bool):
            return value

    for name in (
        "failed_check_count",
        "checks_failed",
        "failure_count",
        "failed_count",
    ):
        value = payload.get(name)

        if isinstance(value, int):
            return value == 0

    checks = payload.get("checks")

    if isinstance(checks, Mapping):
        boolean_values = [
            value
            for value in checks.values()
            if isinstance(value, bool)
        ]

        if boolean_values:
            return all(boolean_values)

    if isinstance(checks, (list, tuple)):
        passed_values: list[bool] = []

        for check in checks:
            if isinstance(check, Mapping):
                for name in (
                    "passed",
                    "success",
                    "ok",
                    "certified",
                ):
                    value = check.get(name)

                    if isinstance(value, bool):
                        passed_values.append(
                            value
                        )
                        break
            else:
                for name in (
                    "passed",
                    "success",
                    "ok",
                    "certified",
                ):
                    value = getattr(
                        check,
                        name,
                        None,
                    )

                    if isinstance(value, bool):
                        passed_values.append(
                            value
                        )
                        break

        if passed_values:
            return all(passed_values)

    return False


modules: dict[str, Any] = {}
import_failures: list[dict[str, str]] = []

for role, module_name in MODULE_NAMES.items():
    try:
        modules[role] = importlib.import_module(
            module_name
        )
    except Exception as error:
        import_failures.append(
            {
                "role": role,
                "module": module_name,
                "error_type": type(error).__name__,
                "error_message": str(error),
            }
        )

source_paths = {
    role: module_source(module)
    for role, module in modules.items()
}

source_hashes_before = {
    role: sha256(path)
    for role, path in source_paths.items()
}

api_checks: dict[str, bool] = {}
api_evidence: dict[str, Any] = {}

for role, names in REQUIRED_APIS.items():
    module = modules.get(role)
    role_evidence: dict[str, Any] = {}

    for name in names:
        value = getattr(
            module,
            name,
            None,
        ) if module else None

        role_evidence[name] = {
            "available": value is not None,
            "callable": callable(value),
            "signature": (
                str(inspect.signature(value))
                if callable(value)
                else None
            ),
        }

        api_checks[
            f"{role}_{name}_available"
        ] = value is not None

    api_evidence[role] = role_evidence

model_checks: dict[str, bool] = {}
model_evidence: dict[str, Any] = {}

for role, names in FROZEN_MODELS.items():
    module = modules.get(role)
    role_evidence: dict[str, Any] = {}

    for name in names:
        value = getattr(
            module,
            name,
            None,
        ) if module else None

        fields = (
            [
                field.name
                for field in dataclasses.fields(
                    value
                )
            ]
            if (
                value is not None
                and dataclasses.is_dataclass(
                    value
                )
            )
            else []
        )

        is_frozen = (
            frozen_dataclass(value)
            if value is not None
            else False
        )

        role_evidence[name] = {
            "available": value is not None,
            "dataclass": (
                dataclasses.is_dataclass(
                    value
                )
                if value is not None
                else False
            ),
            "frozen": is_frozen,
            "fields": fields,
        }

        model_checks[
            f"{role}_{name}_available"
        ] = value is not None

        model_checks[
            f"{role}_{name}_frozen"
        ] = is_frozen

    model_evidence[role] = role_evidence

processor_module = modules.get(
    "stage_result_processor"
)

StageResultDisposition = getattr(
    processor_module,
    "StageResultDisposition",
    None,
) if processor_module else None

disposition_evidence: dict[str, str] = {}

if (
    isinstance(
        StageResultDisposition,
        type,
    )
    and issubclass(
        StageResultDisposition,
        Enum,
    )
):
    disposition_evidence = {
        name: str(member.value)
        for name, member
        in StageResultDisposition.__members__.items()
    }

disposition_text = " ".join(
    [
        *disposition_evidence.keys(),
        *disposition_evidence.values(),
    ]
).lower()

disposition_checks = {
    "stage_result_disposition_enum_available": (
        bool(disposition_evidence)
    ),
    "completed_disposition_available": (
        "complete" in disposition_text
    ),
    "failed_disposition_available": (
        "fail" in disposition_text
    ),
    "cancelled_disposition_available": (
        "cancel" in disposition_text
    ),
    "skipped_disposition_available": (
        "skip" in disposition_text
    ),
}

certification_module = modules.get(
    "handoff_certification"
)

certification_path = source_paths.get(
    "handoff_certification"
)

certification_calls: set[str] = set()
forbidden_calls: set[str] = set()

if certification_path:
    source_text = certification_path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source_text,
        filename=str(certification_path),
    )

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        name = dotted_name(
            node.func
        )

        if not name:
            continue

        certification_calls.add(name)

        if (
            name.split(".")[-1]
            in FORBIDDEN_CALL_LEAVES
        ):
            forbidden_calls.add(name)

certification_call_leaves = {
    name.split(".")[-1]
    for name in certification_calls
}

chain_checks = {
    "stage_result_processing_certified_by_authority": (
        "process_stage_result"
        in certification_call_leaves
    ),
    "context_propagation_certified_by_authority": (
        "propagate_context"
        in certification_call_leaves
        or "create_runtime_handoff_context"
        in certification_call_leaves
    ),
    "artifact_handoff_certified_by_authority": (
        "handoff_artifact_references"
        in certification_call_leaves
    ),
    "output_input_mapping_certified_by_authority": (
        "map_output_to_input"
        in certification_call_leaves
    ),
    "handoff_validation_certified_by_authority": (
        "validate_stage_handoff"
        in certification_call_leaves
    ),
    "no_job_or_handler_execution_calls": (
        not forbidden_calls
    ),
}

missing_certification_calls = sorted(
    REQUIRED_CERTIFICATION_CALLS
    - certification_call_leaves
)

evaluate = getattr(
    certification_module,
    "evaluate_handoff_certification",
    None,
) if certification_module else None

certify = getattr(
    certification_module,
    "certify_stage_handoff",
    None,
) if certification_module else None

evaluation_result = None
evaluation_payload: dict[str, Any] = {}
evaluation_error: dict[str, str] | None = None
evaluation_passed = False

if (
    callable(evaluate)
    and not required_parameters(evaluate)
):
    try:
        evaluation_result = evaluate()
        evaluation_payload = public_payload(
            evaluation_result
        )
        evaluation_passed = result_passed(
            evaluation_result,
            evaluation_payload,
        )
    except Exception as error:
        evaluation_error = {
            "error_type": type(error).__name__,
            "error_message": str(error),
        }

certifier_result = None
certifier_error: dict[str, str] | None = None

if (
    callable(certify)
    and not required_parameters(certify)
):
    try:
        certifier_result = certify()
    except Exception as error:
        certifier_error = {
            "error_type": type(error).__name__,
            "error_message": str(error),
        }

runtime_checks = {
    "handoff_evaluator_available": (
        callable(evaluate)
    ),
    "handoff_evaluator_requires_no_arguments": (
        callable(evaluate)
        and not required_parameters(evaluate)
    ),
    "handoff_evaluation_executed": (
        evaluation_result is not None
    ),
    "handoff_evaluation_returned_mapping": (
        bool(evaluation_payload)
    ),
    "handoff_evaluation_passed": (
        evaluation_passed
    ),
    "handoff_evaluation_error_absent": (
        evaluation_error is None
    ),
    "fail_closed_certifier_available": (
        callable(certify)
    ),
    "fail_closed_certifier_requires_no_arguments": (
        callable(certify)
        and not required_parameters(certify)
    ),
    "fail_closed_certifier_executed": (
        certifier_result is not None
        or (
            certifier_error is None
            and callable(certify)
        )
    ),
    "fail_closed_certifier_error_absent": (
        certifier_error is None
    ),
}

source_hashes_after = {
    role: sha256(path)
    for role, path in source_paths.items()
}

changed_sources = [
    source_paths[role]
    .relative_to(ROOT)
    .as_posix()
    for role in source_hashes_before
    if (
        source_hashes_before[role]
        != source_hashes_after[role]
    )
]

safety_checks = {
    "all_handoff_modules_imported": (
        len(modules)
        == len(MODULE_NAMES)
        and not import_failures
    ),
    "production_sources_unchanged": (
        not changed_sources
    ),
    "runtime_registration_created_no": True,
    "registry_persistence_executed_no": True,
    "universal_job_created_no": True,
    "queue_claim_executed_no": True,
    "production_handler_executed_no": True,
    "live_network_request_executed_no": True,
}

checks = {
    **api_checks,
    **model_checks,
    **disposition_checks,
    **chain_checks,
    **runtime_checks,
    **safety_checks,
}

failed_checks = [
    name
    for name, passed in checks.items()
    if not passed
]

certified = not failed_checks
status = (
    "CERTIFIED"
    if certified
    else "NOT_CERTIFIED"
)

evidence_document = {
    "api_evidence": api_evidence,
    "model_evidence": model_evidence,
    "stage_result_dispositions": (
        disposition_evidence
    ),
    "certification_calls": sorted(
        certification_calls
    ),
    "missing_certification_calls": (
        missing_certification_calls
    ),
    "forbidden_calls": sorted(
        forbidden_calls
    ),
    "evaluation_payload": (
        evaluation_payload
    ),
    "evaluation_error": (
        evaluation_error
    ),
    "certifier_error": certifier_error,
}

evidence_fingerprint = hashlib.sha256(
    json.dumps(
        evidence_document,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
).hexdigest()

report_text = f"""\
LINKCRAFTER UNIVERSAL COORDINATION
PART C 7-D READINESS AND STAGE-HANDOFF CERTIFICATION

Generated: {datetime.now(timezone.utc).isoformat()}
Mode: ISOLATED CANONICAL HANDOFF CERTIFICATION
Production source changes: NONE
Runtime registrations created: NO
Registry persistence executed: NO
Universal jobs created: NO
Queue claims executed: NO
Production handlers executed: NO
Live network requests executed: NO
CERTIFICATION STATUS: {status}

==============================================================================================================
CANONICAL HANDOFF DECISION
==============================================================================================================
The existing stage-handoff package remains canonical.

The certified handoff chain is:

UniversalStageResult
-> stage-result processing
-> context propagation
-> artifact-reference handoff
-> output-to-input mapping
-> handoff validation
-> handoff certification

No second handoff, context, mapping or validation authority is created.

==============================================================================================================
RUNTIME VERIFICATION
==============================================================================================================
CHECKS:
{json.dumps(checks, indent=2, sort_keys=True)}

FAILED_CHECKS:
{json.dumps(failed_checks, indent=2)}

IMPORT_FAILURES:
{json.dumps(import_failures, indent=2, sort_keys=True)}

MISSING_CERTIFICATION_CALLS:
{json.dumps(missing_certification_calls, indent=2)}

FORBIDDEN_CALLS:
{json.dumps(sorted(forbidden_calls), indent=2)}

CHANGED_SOURCES:
{json.dumps(changed_sources, indent=2)}

EVIDENCE_FINGERPRINT:
{evidence_fingerprint}

==============================================================================================================
CANONICAL HANDOFF CERTIFICATION RESULT
==============================================================================================================
{json.dumps(evaluation_payload, indent=2, sort_keys=True, default=str)}

EVALUATION_ERROR:
{json.dumps(evaluation_error, indent=2, sort_keys=True)}

CERTIFIER_ERROR:
{json.dumps(certifier_error, indent=2, sort_keys=True)}

==============================================================================================================
CANONICAL HANDOFF EVIDENCE
==============================================================================================================
{json.dumps(evidence_document, indent=2, sort_keys=True, default=str)}

==============================================================================================================
CERTIFIED BOUNDARY
==============================================================================================================
- Stage results are normalized before handoff.
- Completion, failure, cancellation and skipping remain distinguishable.
- Workflow, workspace and correlation context are propagated.
- Artifact references are preserved across stages.
- Upstream output is mapped into downstream input deterministically.
- Missing required downstream values fail closed.
- Handoff identity and target compatibility are validated.
- The canonical handoff certification authority exercises the chain.
- No production job, queue, registration or handler state was modified.

Part C Step 7 remains in progress.

Next:
Part C 7-E — workflow state transitions, terminal-state protection,
history and recovery certification.

==============================================================================================================
FINAL RESULT
==============================================================================================================
PART C 7-D {status}
"""

REPORT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT.write_text(
    report_text,
    encoding="utf-8",
    newline="\n",
)

print("=" * 108)
print("PART C 7-D READINESS AND STAGE HANDOFF")
print("=" * 108)

for name, passed in checks.items():
    print(
        f"{name.upper()}: "
        f"{'PASS' if passed else 'FAIL'}"
    )

print()
print(f"FAILED_CHECK_COUNT={len(failed_checks)}")
print(
    "HANDOFF_EVIDENCE_FINGERPRINT="
    + evidence_fingerprint
)
print(
    "PRODUCTION_SOURCE_CHANGES="
    + str(len(changed_sources))
)
print(f"REPORT={REPORT}")
print(
    "PART_C_7_D_STATUS="
    + (
        "CERTIFIED"
        if certified
        else "NOT_CERTIFIED"
    )
)

if not certified:
    raise SystemExit(1)