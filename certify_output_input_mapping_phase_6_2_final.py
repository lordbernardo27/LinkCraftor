from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

from backend.server.coordination.stage_handoff.output_input_mapping import (
    OUTPUT_INPUT_MAPPING_SCHEMA_VERSION,
    OUTPUT_INPUT_MAPPING_VERSION,
    OutputInputMappingError,
    OutputInputMappingResult,
    map_output_to_input,
)

from backend.server.coordination.stage_handoff.stage_result_processor import (
    STAGE_RESULT_PROCESSOR_VERSION,
    process_stage_result,
)

from backend.server.coordination.universal_stages.contract import (
    StageExecutionTarget,
    UniversalStageReference,
)

from backend.server.coordination.universal_stages.result_contract import (
    UniversalStageResult,
    UniversalStageResultStatus,
)


TARGET = Path(
    "backend/server/coordination/stage_handoff/output_input_mapping.py"
)

EXPECTED_SHA256 = (
    "ADEB1AC79CD14EDD55706FB119B30D72EC9D22CC4E1C555FED03BC8112C4A744"
)

REPORT = Path(
    "output_input_mapping_phase_6_2_final_certification.txt"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


checks = []


def check(name, condition):
    ok = bool(condition)
    checks.append((name, ok))
    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 6.2 — OUTPUT -> INPUT MAPPING FINAL CERTIFICATION")
print("=" * 120)


# ------------------------------------------------------------------
# SOURCE AUTHORITY
# ------------------------------------------------------------------

check(
    "mapper source exists",
    TARGET.exists(),
)

actual_sha = sha256(
    TARGET
)

check(
    "mapper SHA256 exact",
    actual_sha == EXPECTED_SHA256,
)

check(
    "mapper version exact",
    OUTPUT_INPUT_MAPPING_VERSION
    == "output_input_mapping_v6.2.0",
)

check(
    "mapper schema exact",
    OUTPUT_INPUT_MAPPING_SCHEMA_VERSION
    == "output_input_mapping_schema_v1",
)

check(
    "mapper API signature exact",
    str(
        inspect.signature(
            map_output_to_input
        )
    )
    == "(source: 'ProcessedStageResult', target: 'UniversalStageReference') -> 'OutputInputMappingResult'",
)


# ------------------------------------------------------------------
# CANONICAL FACTORIES
# ------------------------------------------------------------------

def make_source(
    *,
    suffix,
    output,
    status=
        UniversalStageResultStatus.COMPLETED,
):

    failed = (
        status
        == UniversalStageResultStatus.FAILED
    )

    result = UniversalStageResult(
        result_id=
            f"usr_phase_6_2_final_{suffix}",

        workflow_id=
            "wf_phase_6_2_final",

        correlation_id=
            "corr_phase_6_2_final",

        stage_id=
            f"source_{suffix}",

        stage_version=
            "6.2.0",

        pipeline_id=
            "phase_6_2_final_pipeline",

        workflow_type=
            "phase_6_2_final_workflow",

        workspace_id=
            "ws_phase_6_2_final",

        execution_target=
            StageExecutionTarget.UNIVERSAL_RUNTIME,

        job_id=
            f"uj_phase_6_2_final_{suffix}",

        job_type=
            "linking_target_pipeline_batch",

        status=
            status,

        output=
            output,

        result_reference=
            f"result://phase-6-2/final/{suffix}",

        artifact_references=
            (
                f"artifact://phase-6-2/final/{suffix}/a",
                f"artifact://phase-6-2/final/{suffix}/b",
            ),

        started_at=
            "2026-09-09T04:35:00+00:00",

        finished_at=
            "2026-09-09T04:36:00+00:00",

        failure_code=
            (
                "phase_6_2_final_failure"
                if failed
                else ""
            ),

        failure_message=
            (
                "deterministic final failure"
                if failed
                else ""
            ),

        failure_details=
            (
                {
                    "retry_exhausted":
                        True,
                }
                if failed
                else {}
            ),

        metadata=
            {
                "certification":
                    "phase_6_2_final",
            },
    )

    return process_stage_result(
        result
    )


def make_target(
    *,
    suffix,
    required_fields,
    execution_target=
        StageExecutionTarget.UNIVERSAL_RUNTIME,
):

    runtime = (
        execution_target
        == StageExecutionTarget.UNIVERSAL_RUNTIME
    )

    return UniversalStageReference(
        stage_id=
            f"target_{suffix}",

        stage_version=
            "6.2.0",

        pipeline_id=
            "phase_6_2_final_pipeline",

        workflow_type=
            "phase_6_2_final_workflow",

        workflow_contract_version=
            "universal_workflow_contract_v1.1.0",

        execution_target=
            execution_target,

        job_type=
            (
                "linking_target_pipeline_batch"
                if runtime
                else ""
            ),

        runtime_stage=
            (
                f"runtime_{suffix}"
                if runtime
                else ""
            ),

        required_payload_fields=
            tuple(
                required_fields
            ),
    )


# ------------------------------------------------------------------
# COMPLETE PROJECTION
# ------------------------------------------------------------------

source = make_source(
    suffix=
        "complete",

    output={
        "workspace_id":
            "ws_phase_6_2_final",

        "domain":
            "example.com",

        "pages":
            [
                {
                    "url":
                        "/one",
                },
                {
                    "url":
                        "/two",
                },
            ],

        "count":
            0,

        "enabled":
            False,

        "items":
            [],

        "settings":
            {},

        "extra":
            "must-not-project",
    },
)

target = make_target(
    suffix=
        "complete",

    required_fields=(
        "domain",
        "workspace_id",
        "pages",
        "count",
        "enabled",
        "items",
        "settings",
    ),
)

source_before = source.to_dict()
target_before = target.to_dict()

mapped = map_output_to_input(
    source,
    target,
)

check(
    "mapping result exact type",
    isinstance(
        mapped,
        OutputInputMappingResult,
    ),
)

check(
    "complete mapping true",
    mapped.complete is True,
)

check(
    "required ordering exact",
    mapped.required_payload_fields
    == target.required_payload_fields,
)

check(
    "satisfied ordering exact",
    mapped.satisfied_payload_fields
    == target.required_payload_fields,
)

check(
    "missing fields empty",
    mapped.missing_payload_fields
    == (),
)

check(
    "payload order exact",
    tuple(
        mapped.to_dict()["payload"].keys()
    )
    == target.required_payload_fields,
)

check(
    "extra field excluded",
    "extra"
    not in mapped.payload,
)

check(
    "source identity exact",
    (
        mapped.source_result_id
        == source.result_id
        and mapped.source_workflow_id
        == source.workflow_id
        and mapped.source_correlation_id
        == source.correlation_id
        and mapped.source_stage_id
        == source.stage_id
        and mapped.source_stage_version
        == source.stage_version
        and mapped.source_pipeline_id
        == source.pipeline_id
        and mapped.source_workspace_id
        == source.workspace_id
        and mapped.source_job_id
        == source.job_id
    ),
)

check(
    "target identity exact",
    (
        mapped.target_stage_id
        == target.stage_id
        and mapped.target_stage_version
        == target.stage_version
        and mapped.target_pipeline_id
        == target.pipeline_id
        and mapped.target_workflow_type
        == target.workflow_type
        and mapped.target_execution_target
        == target.execution_target.value
        and mapped.target_job_type
        == target.job_type
        and mapped.target_runtime_stage
        == target.runtime_stage
    ),
)

check(
    "version lineage exact",
    (
        mapped.source_processor_version
        == STAGE_RESULT_PROCESSOR_VERSION
        and mapped.target_stage_reference_contract_version
        == target.contract_version
        and mapped.mapper_version
        == OUTPUT_INPUT_MAPPING_VERSION
        and mapped.schema_version
        == OUTPUT_INPUT_MAPPING_SCHEMA_VERSION
    ),
)

check(
    "source unchanged",
    source.to_dict()
    == source_before,
)

check(
    "target unchanged",
    target.to_dict()
    == target_before,
)


# ------------------------------------------------------------------
# INCOMPLETE PROJECTION
# ------------------------------------------------------------------

incomplete_source = make_source(
    suffix=
        "incomplete",

    output={
        "a":
            None,

        "b":
            "",

        "d":
            False,

        "e":
            0,

        "f":
            [],

        "g":
            {},
    },
)

incomplete_target = make_target(
    suffix=
        "incomplete",

    required_fields=(
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
    ),
)

incomplete = map_output_to_input(
    incomplete_source,
    incomplete_target,
)

check(
    "incomplete mapping false",
    incomplete.complete is False,
)

check(
    "missing semantics exact",
    incomplete.missing_payload_fields
    == (
        "a",
        "b",
        "c",
    ),
)

check(
    "satisfied semantics exact",
    incomplete.satisfied_payload_fields
    == (
        "d",
        "e",
        "f",
        "g",
    ),
)

check(
    "missing values excluded",
    (
        "a" not in incomplete.payload
        and "b" not in incomplete.payload
        and "c" not in incomplete.payload
    ),
)

check(
    "Runtime-compatible falsey values preserved",
    (
        incomplete.payload["d"] is False
        and incomplete.payload["e"] == 0
        and incomplete.to_dict()["payload"]["f"] == []
        and incomplete.to_dict()["payload"]["g"] == {}
    ),
)


# ------------------------------------------------------------------
# TOP-LEVEL ONLY
# ------------------------------------------------------------------

nested_source = make_source(
    suffix=
        "nested",

    output={
        "container":
            {
                "domain":
                    "nested.example.com",
            },
    },
)

nested_target = make_target(
    suffix=
        "nested",

    required_fields=(
        "domain",
    ),
)

nested = map_output_to_input(
    nested_source,
    nested_target,
)

check(
    "nested paths not traversed",
    (
        nested.complete is False
        and nested.missing_payload_fields
        == (
            "domain",
        )
        and nested.to_dict()["payload"]
        == {}
    ),
)


# ------------------------------------------------------------------
# ZERO REQUIREMENTS
# ------------------------------------------------------------------

coordination_target = make_target(
    suffix=
        "coordination",

    required_fields=
        (),

    execution_target=
        StageExecutionTarget.COORDINATION_ONLY,
)

coordination = map_output_to_input(
    source,
    coordination_target,
)

check(
    "zero requirement mapping complete",
    coordination.complete is True,
)

check(
    "zero requirement payload empty",
    coordination.to_dict()["payload"]
    == {},
)


# ------------------------------------------------------------------
# SOURCE DISPOSITION GUARDS
# ------------------------------------------------------------------

for status in (
    UniversalStageResultStatus.FAILED,
    UniversalStageResultStatus.SKIPPED,
    UniversalStageResultStatus.CANCELLED,
):

    prohibited = make_source(
        suffix=
            status.value,

        output={
            "domain":
                "example.com",
        },

        status=
            status,
    )

    rejected = False

    try:
        map_output_to_input(
            prohibited,
            target,
        )
    except OutputInputMappingError:
        rejected = True

    check(
        f"{status.value}: prohibited from normal mapping",
        rejected,
    )


# ------------------------------------------------------------------
# INVALID TYPES
# ------------------------------------------------------------------

try:
    map_output_to_input(
        object(),
        target,
    )
except OutputInputMappingError:
    invalid_source_rejected = True
else:
    invalid_source_rejected = False

check(
    "invalid source rejected",
    invalid_source_rejected,
)


try:
    map_output_to_input(
        source,
        object(),
    )
except OutputInputMappingError:
    invalid_target_rejected = True
else:
    invalid_target_rejected = False

check(
    "invalid target rejected",
    invalid_target_rejected,
)


# ------------------------------------------------------------------
# IMMUTABILITY / DETERMINISM
# ------------------------------------------------------------------

try:
    mapped.payload[
        "pages"
    ][
        0
    ][
        "url"
    ] = "/mutated"
except (
    TypeError,
    AttributeError,
):
    deep_immutable = True
else:
    deep_immutable = False

check(
    "mapped payload deeply immutable",
    deep_immutable,
)


serial_1 = json.dumps(
    mapped.to_dict(),
    sort_keys=True,
    separators=(",", ":"),
)

serial_2 = json.dumps(
    map_output_to_input(
        source,
        target,
    ).to_dict(),
    sort_keys=True,
    separators=(",", ":"),
)

check(
    "mapping deterministic",
    serial_1 == serial_2,
)


# ------------------------------------------------------------------
# EXECUTION / OWNERSHIP BOUNDARIES
# ------------------------------------------------------------------

source_text = TARGET.read_text(
    encoding="utf-8"
)

for forbidden in (
    "submit_universal_job(",
    "run_one_universal_runtime_job_v1(",
    "create_orchestration_job(",
    "dequeue_job(",
    "mark_job_completed(",
    "mark_job_failed(",
    "stage_completed(",
    "stage_failed(",
    "advance(",
    "pause(",
    "resume(",
    "recover(",
    "propagate_context(",
    "handoff_artifact",
):

    check(
        f"forbidden execution surface absent: {forbidden}",
        forbidden not in source_text,
    )


check(
    "rename mapping not introduced",
    (
        "source_field"
        not in source_text
        and "target_field"
        not in source_text
    ),
)

check(
    "nested path mapping not introduced",
    (
        "jsonpath"
        not in source_text.lower()
        and "dot_path"
        not in source_text.lower()
    ),
)


# ------------------------------------------------------------------
# SOURCE INTEGRITY
# ------------------------------------------------------------------

check(
    "mapper source unchanged",
    sha256(
        TARGET
    )
    == EXPECTED_SHA256,
)


# ------------------------------------------------------------------
# SUMMARY / REPORT
# ------------------------------------------------------------------

passed = sum(
    1
    for _, ok in checks
    if ok
)

failed = (
    len(checks)
    - passed
)

certified = (
    failed == 0
)


report_lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 6.2 — OUTPUT -> INPUT MAPPING FINAL CERTIFICATION",
    "",
    f"Checks: {len(checks)}",
    f"Passed: {passed}",
    f"Failed: {failed}",
    f"FINAL CERTIFIED: {certified}",
    "",
    f"Mapper Version: {OUTPUT_INPUT_MAPPING_VERSION}",
    f"Schema Version: {OUTPUT_INPUT_MAPPING_SCHEMA_VERSION}",
    f"Mapper SHA256: {actual_sha}",
    "",
    "Certified mapping model:",
    "- source: ProcessedStageResult.output",
    "- target requirements: UniversalStageReference.required_payload_fields",
    "- exact top-level field-name projection only",
    "- absent key / None / empty string are missing",
    "- 0 / False / [] / {} remain valid values",
    "- extra upstream fields are not projected",
    "- incomplete mappings are represented, not silently promoted",
    "",
    "Certified boundaries:",
    "- no source-field -> target-field rename mapping",
    "- no nested-path mapping",
    "- no context propagation",
    "- no artifact-reference handoff",
    "- no Runtime submission",
    "- no coordinator invocation",
    "- no workflow lifecycle mutation",
    "- Runtime remains final required-payload enforcement authority",
    "",
    "NEXT: 6.2 SHA256 Freeze"
    if certified
    else "NEXT: Diagnose final certification failure",
]

REPORT.write_text(
    "\n".join(
        report_lines
    )
    + "\n",
    encoding="utf-8",
)

report_sha = sha256(
    REPORT
)


print("-" * 120)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print(
    "FINAL CERTIFIED:",
    certified,
)
print(
    "MAPPER SHA256:",
    actual_sha,
)
print(
    "REPORT:",
    REPORT,
)
print(
    "REPORT SHA256:",
    report_sha,
)
print(
    "NEXT:",
    (
        "6.2 SHA256 Freeze"
        if certified
        else "Diagnose final certification failure"
    ),
)
print("=" * 120)
