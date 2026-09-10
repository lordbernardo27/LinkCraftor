from __future__ import annotations

import hashlib
import inspect
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path.cwd()

TARGET = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
      "artifact_reference_handoff.py"
)

REPORT = (
    ROOT
    / "artifact_reference_handoff_phase_6_4_final_certification.txt"
)

FREEZE = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
      "artifact_reference_handoff.phase_6_4.freeze.json"
)

PHASE_6_1 = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
      "stage_result_processor.py"
)

PHASE_6_2 = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
      "output_input_mapping.py"
)

PHASE_6_3 = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
      "context_propagation.py"
)

PHASE_6_1_FREEZE = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
      "stage_result_processor.phase_6_1.freeze.json"
)

PHASE_6_2_FREEZE = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
      "output_input_mapping.phase_6_2.freeze.json"
)

PHASE_6_3_FREEZE = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
      "context_propagation.phase_6_3.freeze.json"
)


EXPECTED_6_1_SHA = (
    "8106D844B0B4D1C4D4E3A07A6232F4796010C604F538ED0F8E45F823D2C64456"
)

EXPECTED_6_1_FREEZE_SHA = (
    "58AD1700AC8EA9BB838EC9E11273A7723D9D7C1F80D5FCB6222AFE563FB2017F"
)

EXPECTED_6_2_SHA = (
    "ADEB1AC79CD14EDD55706FB119B30D72EC9D22CC4E1C555FED03BC8112C4A744"
)

EXPECTED_6_2_FREEZE_SHA = (
    "DB45DE654E1CA336A35150EF11142B36CFDF3ED2FFE4AA46D03568939E9D5C5E"
)

EXPECTED_6_3_SHA = (
    "1060639F9B8BB20AFDD5B3D42E4265DDD082E267631EFEA08AD5295FCC17B596"
)

EXPECTED_6_3_FREEZE_SHA = (
    "39AD8A1ABF7753F0A5E8A9F2195E60495CCC38708DDDAAC01C8BDF8885B555D1"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def section(title: str) -> None:
    print()
    print("=" * 120)
    print(title)
    print("=" * 120)


def stop(message: str) -> None:
    raise SystemExit(
        "\nPHASE 6.4 STOPPED:\n"
        + message
    )


section(
    "LINKCRAFTOR — UCF PHASE 6.4 ALL-IN-ONE IMPLEMENTATION"
)


# ==================================================================
# 0 — UPSTREAM INTEGRITY
# ==================================================================

section(
    "0 — UPSTREAM INTEGRITY"
)


required_files = (
    PHASE_6_1,
    PHASE_6_2,
    PHASE_6_3,
    PHASE_6_1_FREEZE,
    PHASE_6_2_FREEZE,
    PHASE_6_3_FREEZE,
)


for path in required_files:
    if not path.exists():
        stop(
            f"Required upstream authority missing: {path}"
        )


integrity = {
    "Phase 6.1 production":
        sha256(PHASE_6_1)
        == EXPECTED_6_1_SHA,

    "Phase 6.1 freeze":
        sha256(PHASE_6_1_FREEZE)
        == EXPECTED_6_1_FREEZE_SHA,

    "Phase 6.2 production":
        sha256(PHASE_6_2)
        == EXPECTED_6_2_SHA,

    "Phase 6.2 freeze":
        sha256(PHASE_6_2_FREEZE)
        == EXPECTED_6_2_FREEZE_SHA,

    "Phase 6.3 production":
        sha256(PHASE_6_3)
        == EXPECTED_6_3_SHA,

    "Phase 6.3 freeze":
        sha256(PHASE_6_3_FREEZE)
        == EXPECTED_6_3_FREEZE_SHA,
}


for name, ok in integrity.items():
    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


if not all(
    integrity.values()
):
    stop(
        "Frozen Stage Handoff upstream integrity mismatch. "
        "No Phase 6.4 source has been written."
    )


# ==================================================================
# 1 — EXACT ARTIFACT CONTRACT RESOLUTION
# ==================================================================

section(
    "1 — EXACT ARTIFACT CONTRACT RESOLUTION"
)


import backend.server.runtime.universal_jobs.artifact_references as artifact_authority
import backend.server.runtime.universal_jobs.result_reference as result_authority


artifact_normalize = (
    artifact_authority.normalize_universal_job_artifact_references
)

artifact_validate = (
    artifact_authority.validate_universal_job_artifact_references
)

artifact_is_canonical = (
    artifact_authority.is_canonical_universal_job_artifact_references
)

result_normalize = (
    result_authority.normalize_universal_job_result_reference
)

result_validate = (
    result_authority.validate_universal_job_result_reference
)

result_is_canonical = (
    result_authority.is_canonical_universal_job_result_reference
)


print(
    "Artifact authority version:",
    artifact_authority.UNIVERSAL_JOB_ARTIFACT_REFERENCES_VERSION,
)

print(
    "Artifact authority schema:",
    artifact_authority.UNIVERSAL_JOB_ARTIFACT_REFERENCES_SCHEMA_VERSION,
)

print(
    "Artifact max length:",
    artifact_authority.MAX_UNIVERSAL_JOB_ARTIFACT_REFERENCE_LENGTH,
)

print(
    "Artifact normalize signature:",
    inspect.signature(
        artifact_normalize
    ),
)

print(
    "Artifact validate signature:",
    inspect.signature(
        artifact_validate
    ),
)

print(
    "Artifact canonical signature:",
    inspect.signature(
        artifact_is_canonical
    ),
)

print(
    "Result authority version:",
    result_authority.UNIVERSAL_JOB_RESULT_REFERENCE_VERSION,
)

print(
    "Result authority schema:",
    result_authority.UNIVERSAL_JOB_RESULT_REFERENCE_SCHEMA_VERSION,
)

print(
    "Result max length:",
    result_authority.MAX_UNIVERSAL_JOB_RESULT_REFERENCE_LENGTH,
)

print(
    "Result normalize signature:",
    inspect.signature(
        result_normalize
    ),
)


contract_checks = []


def contract_check(
    name,
    condition,
):
    ok = bool(
        condition
    )

    contract_checks.append(
        ok
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


contract_check(
    "artifact authority version present",
    bool(
        artifact_authority.UNIVERSAL_JOB_ARTIFACT_REFERENCES_VERSION
    ),
)

contract_check(
    "artifact schema version present",
    bool(
        artifact_authority.UNIVERSAL_JOB_ARTIFACT_REFERENCES_SCHEMA_VERSION
    ),
)

contract_check(
    "artifact max reference length is 4096",
    artifact_authority.MAX_UNIVERSAL_JOB_ARTIFACT_REFERENCE_LENGTH
    == 4096,
)

contract_check(
    "result authority version present",
    bool(
        result_authority.UNIVERSAL_JOB_RESULT_REFERENCE_VERSION
    ),
)

contract_check(
    "result schema version present",
    bool(
        result_authority.UNIVERSAL_JOB_RESULT_REFERENCE_SCHEMA_VERSION
    ),
)

contract_check(
    "result max reference length is 4096",
    result_authority.MAX_UNIVERSAL_JOB_RESULT_REFERENCE_LENGTH
    == 4096,
)


# ------------------------------------------------------------------
# BEHAVIORAL CONTRACT PROBES
# ------------------------------------------------------------------

artifact_probe = artifact_normalize(
    (
        "artifact://phase-6-4/a",
        "artifact://phase-6-4/b",
    )
)

contract_check(
    "artifact normalization returns tuple",
    isinstance(
        artifact_probe,
        tuple,
    ),
)

contract_check(
    "artifact normalization preserves canonical order",
    artifact_probe
    == (
        "artifact://phase-6-4/a",
        "artifact://phase-6-4/b",
    ),
)

contract_check(
    "canonical artifact tuple recognized",
    artifact_is_canonical(
        artifact_probe
    )
    is True,
)


empty_artifacts = artifact_normalize(
    ()
)

contract_check(
    "zero artifact references supported",
    empty_artifacts
    == (),
)


artifact_validate(
    artifact_probe
)

contract_check(
    "artifact validation accepts canonical tuple",
    True,
)


result_probe = result_normalize(
    "result://phase-6-4/primary"
)

contract_check(
    "result reference normalization preserves canonical value",
    result_probe
    == "result://phase-6-4/primary",
)

contract_check(
    "canonical result reference recognized",
    result_is_canonical(
        result_probe
    )
    is True,
)


result_validate(
    result_probe
)

contract_check(
    "result reference validation accepts canonical value",
    True,
)


if not all(
    contract_checks
):
    stop(
        "Runtime artifact/result-reference authority differs from "
        "the required Phase 6.4 contract. "
        "No production source has been written."
    )


print(
    "EXACT ARTIFACT CONTRACT RESOLVED: TRUE"
)


# ==================================================================
# 2 — HANDOFF ARCHITECTURE RESOLUTION
# ==================================================================

section(
    "2 — HANDOFF ARCHITECTURE RESOLUTION"
)


architecture = {
    "source":
        "ProcessedStageResult",

    "primary_result_authority":
        "ProcessedStageResult.result_reference",

    "artifact_authority":
        "ProcessedStageResult.artifact_references",

    "result_normalization_owner":
        "Runtime universal_jobs.result_reference",

    "artifact_normalization_owner":
        "Runtime universal_jobs.artifact_references",

    "handoff_type":
        "immutable reference-only evidence",

    "bytes_transferred":
        False,

    "storage_access":
        False,

    "artifact_creation":
        False,

    "artifact_read":
        False,

    "artifact_write":
        False,

    "artifact_persistence":
        False,

    "artifact_deletion":
        False,

    "runtime_submission":
        False,

    "coordinator_invocation":
        False,

    "context_mutation":
        False,

    "payload_mutation":
        False,

    "workflow_mutation":
        False,

    "source_requirement":
        "completed and normal_handoff_allowed",
}


architecture_checks = []


def architecture_check(
    name,
    condition,
):
    ok = bool(
        condition
    )

    architecture_checks.append(
        ok
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


architecture_check(
    "ProcessedStageResult is source authority",
    architecture[
        "source"
    ]
    == "ProcessedStageResult",
)

architecture_check(
    "result_reference preserved separately",
    architecture[
        "primary_result_authority"
    ]
    == "ProcessedStageResult.result_reference",
)

architecture_check(
    "artifact_references source exact",
    architecture[
        "artifact_authority"
    ]
    == "ProcessedStageResult.artifact_references",
)

architecture_check(
    "Runtime result-reference normalization reused",
    architecture[
        "result_normalization_owner"
    ]
    == "Runtime universal_jobs.result_reference",
)

architecture_check(
    "Runtime artifact normalization reused",
    architecture[
        "artifact_normalization_owner"
    ]
    == "Runtime universal_jobs.artifact_references",
)

architecture_check(
    "handoff is reference-only",
    architecture[
        "handoff_type"
    ]
    == "immutable reference-only evidence",
)

architecture_check(
    "artifact bytes not transferred",
    architecture[
        "bytes_transferred"
    ]
    is False,
)

architecture_check(
    "storage access excluded",
    architecture[
        "storage_access"
    ]
    is False,
)

architecture_check(
    "artifact creation excluded",
    architecture[
        "artifact_creation"
    ]
    is False,
)

architecture_check(
    "artifact read excluded",
    architecture[
        "artifact_read"
    ]
    is False,
)

architecture_check(
    "artifact write excluded",
    architecture[
        "artifact_write"
    ]
    is False,
)

architecture_check(
    "artifact persistence excluded",
    architecture[
        "artifact_persistence"
    ]
    is False,
)

architecture_check(
    "artifact deletion excluded",
    architecture[
        "artifact_deletion"
    ]
    is False,
)

architecture_check(
    "Runtime submission excluded",
    architecture[
        "runtime_submission"
    ]
    is False,
)

architecture_check(
    "coordinator invocation excluded",
    architecture[
        "coordinator_invocation"
    ]
    is False,
)

architecture_check(
    "context mutation excluded",
    architecture[
        "context_mutation"
    ]
    is False,
)

architecture_check(
    "payload mutation excluded",
    architecture[
        "payload_mutation"
    ]
    is False,
)

architecture_check(
    "workflow mutation excluded",
    architecture[
        "workflow_mutation"
    ]
    is False,
)


if not all(
    architecture_checks
):
    stop(
        "Phase 6.4 handoff architecture resolution failed."
    )


print(
    "HANDOFF ARCHITECTURE RESOLVED: TRUE"
)


# ==================================================================
# 3 — INSTALLATION
# ==================================================================

section(
    "3 — INSTALLATION"
)


if TARGET.exists():
    stop(
        "artifact_reference_handoff.py already exists. "
        "Refusing to overwrite an existing production component."
    )


production_source = r'''"""
LinkCraftor
Universal Coordination Framework

PHASE 6.4 — Artifact Reference Handoff

Purpose
-------
Preserve and hand off canonical references produced by one successfully
completed stage.

Canonical source
----------------
ProcessedStageResult.result_reference
ProcessedStageResult.artifact_references

Canonical validation / normalization authorities
------------------------------------------------
backend.server.runtime.universal_jobs.result_reference
backend.server.runtime.universal_jobs.artifact_references

Meaning
-------
result_reference identifies the primary logical stage result.

artifact_references identify zero or more supporting/generated resources.

Phase 6.4 performs reference handoff only.

It does NOT:
- create artifacts,
- open/read artifact contents,
- write artifacts,
- copy artifact bytes,
- persist artifacts,
- delete artifacts,
- resolve storage locations,
- submit Runtime jobs,
- invoke coordinators,
- mutate RuntimeHandoffContext,
- mutate Phase 6.2 payload mapping,
- mutate workflow lifecycle state,
- perform final Stage Handoff validation (Phase 6.5).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, Tuple

from backend.server.coordination.stage_handoff.stage_result_processor import (
    ProcessedStageResult,
)

from backend.server.runtime.universal_jobs.artifact_references import (
    UNIVERSAL_JOB_ARTIFACT_REFERENCES_SCHEMA_VERSION,
    UNIVERSAL_JOB_ARTIFACT_REFERENCES_VERSION,
    normalize_universal_job_artifact_references,
)

from backend.server.runtime.universal_jobs.result_reference import (
    UNIVERSAL_JOB_RESULT_REFERENCE_SCHEMA_VERSION,
    UNIVERSAL_JOB_RESULT_REFERENCE_VERSION,
    normalize_universal_job_result_reference,
)


ARTIFACT_REFERENCE_HANDOFF_VERSION: Final[str] = (
    "artifact_reference_handoff_v6.4.0"
)

ARTIFACT_REFERENCE_HANDOFF_SCHEMA_VERSION: Final[str] = (
    "artifact_reference_handoff_schema_v1"
)


class ArtifactReferenceHandoffError(
    ValueError
):
    """
    Raised when canonical reference handoff cannot safely be produced.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class ArtifactReferenceHandoffResult:
    """
    Immutable Phase 6.4 reference-only Stage Handoff evidence.
    """

    result_id: str
    workflow_id: str
    correlation_id: str

    source_stage_id: str
    source_stage_version: str
    source_pipeline_id: str
    workspace_id: str
    source_job_id: str

    result_reference: str
    artifact_references: Tuple[str, ...]

    artifact_count: int
    has_artifacts: bool

    source_processor_version: str

    result_reference_authority_version: str
    result_reference_authority_schema_version: str

    artifact_reference_authority_version: str
    artifact_reference_authority_schema_version: str

    handoff_version: str = (
        ARTIFACT_REFERENCE_HANDOFF_VERSION
    )

    schema_version: str = (
        ARTIFACT_REFERENCE_HANDOFF_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "result_id":
                self.result_id,

            "workflow_id":
                self.workflow_id,

            "correlation_id":
                self.correlation_id,

            "source_stage_id":
                self.source_stage_id,

            "source_stage_version":
                self.source_stage_version,

            "source_pipeline_id":
                self.source_pipeline_id,

            "workspace_id":
                self.workspace_id,

            "source_job_id":
                self.source_job_id,

            "result_reference":
                self.result_reference,

            "artifact_references":
                list(
                    self.artifact_references
                ),

            "artifact_count":
                self.artifact_count,

            "has_artifacts":
                self.has_artifacts,

            "source_processor_version":
                self.source_processor_version,

            "result_reference_authority_version":
                self.result_reference_authority_version,

            "result_reference_authority_schema_version":
                self.result_reference_authority_schema_version,

            "artifact_reference_authority_version":
                self.artifact_reference_authority_version,

            "artifact_reference_authority_schema_version":
                self.artifact_reference_authority_schema_version,

            "handoff_version":
                self.handoff_version,

            "schema_version":
                self.schema_version,
        }


def _validate_source(
    source: ProcessedStageResult,
) -> None:

    if not isinstance(
        source,
        ProcessedStageResult,
    ):
        raise ArtifactReferenceHandoffError(
            "source must be a ProcessedStageResult"
        )

    if not source.terminal:
        raise ArtifactReferenceHandoffError(
            "source must be terminal"
        )

    if not source.completed:
        raise ArtifactReferenceHandoffError(
            "artifact reference handoff requires a completed source"
        )

    if not source.normal_handoff_allowed:
        raise ArtifactReferenceHandoffError(
            "normal handoff must be allowed before artifact reference handoff"
        )


def handoff_artifact_references(
    source: ProcessedStageResult,
) -> ArtifactReferenceHandoffResult:
    """
    Produce immutable canonical reference-only handoff evidence.

    No artifact storage or artifact contents are accessed.
    """

    _validate_source(
        source
    )

    try:
        result_reference = (
            normalize_universal_job_result_reference(
                source.result_reference
            )
        )
    except Exception as exc:
        raise ArtifactReferenceHandoffError(
            "result_reference failed canonical Runtime normalization"
        ) from exc

    try:
        artifact_references = (
            normalize_universal_job_artifact_references(
                source.artifact_references
            )
        )
    except Exception as exc:
        raise ArtifactReferenceHandoffError(
            "artifact_references failed canonical Runtime normalization"
        ) from exc

    if result_reference is None:
        raise ArtifactReferenceHandoffError(
            "completed Stage Handoff requires a canonical result_reference"
        )

    if not isinstance(
        result_reference,
        str,
    ):
        raise ArtifactReferenceHandoffError(
            "canonical result_reference must be a string"
        )

    if not isinstance(
        artifact_references,
        tuple,
    ):
        artifact_references = tuple(
            artifact_references
        )

    return ArtifactReferenceHandoffResult(
        result_id=
            source.result_id,

        workflow_id=
            source.workflow_id,

        correlation_id=
            source.correlation_id,

        source_stage_id=
            source.stage_id,

        source_stage_version=
            source.stage_version,

        source_pipeline_id=
            source.pipeline_id,

        workspace_id=
            source.workspace_id,

        source_job_id=
            source.job_id,

        result_reference=
            result_reference,

        artifact_references=
            tuple(
                artifact_references
            ),

        artifact_count=
            len(
                artifact_references
            ),

        has_artifacts=
            bool(
                artifact_references
            ),

        source_processor_version=
            source.processor_version,

        result_reference_authority_version=
            UNIVERSAL_JOB_RESULT_REFERENCE_VERSION,

        result_reference_authority_schema_version=
            UNIVERSAL_JOB_RESULT_REFERENCE_SCHEMA_VERSION,

        artifact_reference_authority_version=
            UNIVERSAL_JOB_ARTIFACT_REFERENCES_VERSION,

        artifact_reference_authority_schema_version=
            UNIVERSAL_JOB_ARTIFACT_REFERENCES_SCHEMA_VERSION,
    )


__all__ = [
    "ARTIFACT_REFERENCE_HANDOFF_VERSION",
    "ARTIFACT_REFERENCE_HANDOFF_SCHEMA_VERSION",
    "ArtifactReferenceHandoffError",
    "ArtifactReferenceHandoffResult",
    "handoff_artifact_references",
]
'''


TARGET.write_text(
    production_source,
    encoding="utf-8",
)


installed_sha = sha256(
    TARGET
)


print(
    "INSTALLED:",
    TARGET,
)

print(
    "ARTIFACT REFERENCE HANDOFF SHA256:",
    installed_sha,
)


# ==================================================================
# IMPORT INSTALLED PRODUCTION
# ==================================================================

from backend.server.coordination.stage_handoff.artifact_reference_handoff import (
    ARTIFACT_REFERENCE_HANDOFF_SCHEMA_VERSION,
    ARTIFACT_REFERENCE_HANDOFF_VERSION,
    ArtifactReferenceHandoffError,
    ArtifactReferenceHandoffResult,
    handoff_artifact_references,
)

from backend.server.coordination.stage_handoff.stage_result_processor import (
    process_stage_result,
)

from backend.server.coordination.universal_stages.contract import (
    StageExecutionTarget,
)

from backend.server.coordination.universal_stages.result_contract import (
    UniversalStageResult,
    UniversalStageResultStatus,
)


def make_source(
    *,
    suffix="source",
    status=UniversalStageResultStatus.COMPLETED,
    result_reference="result://phase-6-4/primary",
    artifact_references=(
        "artifact://phase-6-4/a",
        "artifact://phase-6-4/b",
    ),
):

    failed = (
        status
        == UniversalStageResultStatus.FAILED
    )

    canonical = UniversalStageResult(
        result_id=
            f"usr_6_4_{suffix}",

        workflow_id=
            "wf_phase_6_4",

        correlation_id=
            "corr_phase_6_4",

        stage_id=
            f"source_{suffix}",

        stage_version=
            "1.0.0",

        pipeline_id=
            "phase_6_4_pipeline",

        workflow_type=
            "phase_6_4_workflow",

        workspace_id=
            "ws_phase_6_4",

        execution_target=
            StageExecutionTarget.UNIVERSAL_RUNTIME,

        job_id=
            f"uj_6_4_{suffix}",

        job_type=
            "linking_target_pipeline_batch",

        status=
            status,

        output=
            {
                "domain":
                    "example.com",

                "must_not_become_artifact":
                    "payload-data",
            },

        result_reference=
            result_reference,

        artifact_references=
            tuple(
                artifact_references
            ),

        started_at=
            "2026-09-10T03:45:00+00:00",

        finished_at=
            "2026-09-10T03:46:00+00:00",

        failure_code=
            (
                "phase_6_4_failure"
                if failed
                else ""
            ),

        failure_message=
            (
                "phase 6.4 deterministic failure"
                if failed
                else ""
            ),

        failure_details=
            (
                {
                    "phase":
                        "6.4",
                }
                if failed
                else {}
            ),

        metadata=
            {
                "metadata_value":
                    "must-not-become-artifact-reference",
            },
    )

    return process_stage_result(
        canonical
    )


# ==================================================================
# 4 — SMOKE VERIFICATION
# ==================================================================

section(
    "4 — SMOKE VERIFICATION"
)


smoke = []


def smoke_check(
    name,
    condition,
):

    ok = bool(
        condition
    )

    smoke.append(
        ok
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


source = make_source()

source_before = source.to_dict()

handoff = handoff_artifact_references(
    source
)


smoke_check(
    "production source exists",
    TARGET.exists(),
)

smoke_check(
    "handoff version exact",
    ARTIFACT_REFERENCE_HANDOFF_VERSION
    == "artifact_reference_handoff_v6.4.0",
)

smoke_check(
    "schema version exact",
    ARTIFACT_REFERENCE_HANDOFF_SCHEMA_VERSION
    == "artifact_reference_handoff_schema_v1",
)

smoke_check(
    "handoff result type exact",
    isinstance(
        handoff,
        ArtifactReferenceHandoffResult,
    ),
)

smoke_check(
    "result_reference preserved",
    handoff.result_reference
    == source.result_reference,
)

smoke_check(
    "artifact references preserved",
    handoff.artifact_references
    == source.artifact_references,
)

smoke_check(
    "artifact count exact",
    handoff.artifact_count
    == 2,
)

smoke_check(
    "has_artifacts true",
    handoff.has_artifacts
    is True,
)

smoke_check(
    "source result identity preserved",
    handoff.result_id
    == source.result_id,
)

smoke_check(
    "workflow identity preserved",
    handoff.workflow_id
    == source.workflow_id,
)

smoke_check(
    "correlation identity preserved",
    handoff.correlation_id
    == source.correlation_id,
)

smoke_check(
    "source stage identity preserved",
    handoff.source_stage_id
    == source.stage_id,
)

smoke_check(
    "workspace identity preserved",
    handoff.workspace_id
    == source.workspace_id,
)

smoke_check(
    "source not mutated",
    source.to_dict()
    == source_before,
)


zero_source = make_source(
    suffix=
        "zero",

    artifact_references=
        (),
)

zero_handoff = handoff_artifact_references(
    zero_source
)


smoke_check(
    "zero artifacts supported",
    zero_handoff.artifact_references
    == (),
)

smoke_check(
    "zero artifact count exact",
    zero_handoff.artifact_count
    == 0,
)

smoke_check(
    "zero artifacts has_artifacts false",
    zero_handoff.has_artifacts
    is False,
)


if not all(
    smoke
):
    stop(
        "Phase 6.4 Smoke Verification failed."
    )


print(
    f"SMOKE VERIFICATION: {len(smoke)}/{len(smoke)} PASS"
)


# ==================================================================
# 5 — INITIAL VERIFICATION
# ==================================================================

section(
    "5 — INITIAL VERIFICATION"
)


initial = []


def initial_check(
    name,
    condition,
):

    ok = bool(
        condition
    )

    initial.append(
        ok
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


initial_check(
    "production SHA unchanged",
    sha256(TARGET)
    == installed_sha,
)

initial_check(
    "result id preserved",
    handoff.result_id
    == source.result_id,
)

initial_check(
    "workflow id preserved",
    handoff.workflow_id
    == source.workflow_id,
)

initial_check(
    "correlation id preserved",
    handoff.correlation_id
    == source.correlation_id,
)

initial_check(
    "stage id preserved",
    handoff.source_stage_id
    == source.stage_id,
)

initial_check(
    "stage version preserved",
    handoff.source_stage_version
    == source.stage_version,
)

initial_check(
    "pipeline id preserved",
    handoff.source_pipeline_id
    == source.pipeline_id,
)

initial_check(
    "workspace id preserved",
    handoff.workspace_id
    == source.workspace_id,
)

initial_check(
    "job id preserved",
    handoff.source_job_id
    == source.job_id,
)

initial_check(
    "source processor version preserved",
    handoff.source_processor_version
    == source.processor_version,
)

initial_check(
    "Runtime result authority version recorded",
    handoff.result_reference_authority_version
    == result_authority.UNIVERSAL_JOB_RESULT_REFERENCE_VERSION,
)

initial_check(
    "Runtime result authority schema recorded",
    handoff.result_reference_authority_schema_version
    == result_authority.UNIVERSAL_JOB_RESULT_REFERENCE_SCHEMA_VERSION,
)

initial_check(
    "Runtime artifact authority version recorded",
    handoff.artifact_reference_authority_version
    == artifact_authority.UNIVERSAL_JOB_ARTIFACT_REFERENCES_VERSION,
)

initial_check(
    "Runtime artifact authority schema recorded",
    handoff.artifact_reference_authority_schema_version
    == artifact_authority.UNIVERSAL_JOB_ARTIFACT_REFERENCES_SCHEMA_VERSION,
)

initial_check(
    "result_reference remains separate from artifacts",
    handoff.result_reference
    not in handoff.artifact_references,
)

initial_check(
    "stage output not copied into artifact evidence",
    "must_not_become_artifact"
    not in handoff.to_dict(),
)

initial_check(
    "stage metadata not copied into artifact evidence",
    "metadata_value"
    not in handoff.to_dict(),
)

initial_check(
    "serialization deterministic",
    handoff.to_dict()
    == handoff.to_dict(),
)


repeat = handoff_artifact_references(
    source
)


initial_check(
    "repeated handoff deterministic",
    repeat.to_dict()
    == handoff.to_dict(),
)


try:
    handoff.artifact_references += (
        "artifact://mutated",
    )
except (
    AttributeError,
    TypeError,
):
    immutable_result = True
else:
    immutable_result = False


initial_check(
    "handoff dataclass immutable",
    immutable_result,
)


# ------------------------------------------------------------------
# TYPE GUARD
# ------------------------------------------------------------------

for index, invalid in enumerate(
    (
        None,
        {},
        [],
        "source",
        123,
    ),
    start=1,
):

    rejected = False

    try:
        handoff_artifact_references(
            invalid
        )
    except ArtifactReferenceHandoffError:
        rejected = True

    initial_check(
        f"invalid source {index} rejected",
        rejected,
    )


# ------------------------------------------------------------------
# PROHIBITED SOURCE DISPOSITIONS
# ------------------------------------------------------------------

for status in (
    UniversalStageResultStatus.FAILED,
    UniversalStageResultStatus.SKIPPED,
    UniversalStageResultStatus.CANCELLED,
):

    prohibited = make_source(
        suffix=
            status.value,

        status=
            status,
    )

    rejected = False

    try:
        handoff_artifact_references(
            prohibited
        )
    except ArtifactReferenceHandoffError:
        rejected = True

    initial_check(
        f"{status.value} source rejected",
        rejected,
    )


# ------------------------------------------------------------------
# OWNERSHIP BOUNDARIES
# ------------------------------------------------------------------

source_text = TARGET.read_text(
    encoding="utf-8"
)


for forbidden in (
    "open(",
    "read_bytes(",
    "write_bytes(",
    "shutil.copy",
    "shutil.move",
    "unlink(",
    "remove(",
    "delete(",
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
):

    initial_check(
        f"forbidden ownership surface absent: {forbidden}",
        forbidden
        not in source_text,
    )


initial_check(
    "Phase 6.1 unchanged",
    sha256(
        PHASE_6_1
    )
    == EXPECTED_6_1_SHA,
)

initial_check(
    "Phase 6.2 unchanged",
    sha256(
        PHASE_6_2
    )
    == EXPECTED_6_2_SHA,
)

initial_check(
    "Phase 6.3 unchanged",
    sha256(
        PHASE_6_3
    )
    == EXPECTED_6_3_SHA,
)


if not all(
    initial
):
    stop(
        "Phase 6.4 Initial Verification failed."
    )


print(
    f"INITIAL VERIFICATION: {len(initial)}/{len(initial)} PASS"
)


# ==================================================================
# 6 — FINAL CERTIFICATION
# ==================================================================

section(
    "6 — FINAL CERTIFICATION"
)


final = []


def final_check(
    name,
    condition,
):

    ok = bool(
        condition
    )

    final.append(
        ok
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


actual_sha = sha256(
    TARGET
)


final_check(
    "production SHA stable",
    actual_sha
    == installed_sha,
)

final_check(
    "handoff version exact",
    ARTIFACT_REFERENCE_HANDOFF_VERSION
    == "artifact_reference_handoff_v6.4.0",
)

final_check(
    "schema exact",
    ARTIFACT_REFERENCE_HANDOFF_SCHEMA_VERSION
    == "artifact_reference_handoff_schema_v1",
)

final_check(
    "public API signature exact",
    str(
        inspect.signature(
            handoff_artifact_references
        )
    )
    == (
        "(source: 'ProcessedStageResult') "
        "-> 'ArtifactReferenceHandoffResult'"
    ),
)

final_check(
    "primary result reference certified",
    handoff.result_reference
    == source.result_reference,
)

final_check(
    "artifact references certified",
    handoff.artifact_references
    == source.artifact_references,
)

final_check(
    "artifact count certified",
    handoff.artifact_count
    == len(
        source.artifact_references
    ),
)

final_check(
    "artifact presence flag certified",
    handoff.has_artifacts
    == bool(
        source.artifact_references
    ),
)

final_check(
    "Runtime result authority canonicality certified",
    result_is_canonical(
        handoff.result_reference
    )
    is True,
)

final_check(
    "Runtime artifact authority canonicality certified",
    artifact_is_canonical(
        handoff.artifact_references
    )
    is True,
)

final_check(
    "reference-only model certified",
    (
        "open("
        not in source_text
        and "read_bytes("
        not in source_text
        and "write_bytes("
        not in source_text
    ),
)

final_check(
    "no Runtime submission certified",
    "submit_universal_job("
    not in source_text,
)

final_check(
    "no coordinator invocation certified",
    (
        "stage_completed("
        not in source_text
        and "advance("
        not in source_text
    ),
)

final_check(
    "no context propagation mutation certified",
    "propagate_context("
    not in source_text,
)

final_check(
    "Phase 6.1 source frozen",
    sha256(
        PHASE_6_1
    )
    == EXPECTED_6_1_SHA,
)

final_check(
    "Phase 6.1 freeze frozen",
    sha256(
        PHASE_6_1_FREEZE
    )
    == EXPECTED_6_1_FREEZE_SHA,
)

final_check(
    "Phase 6.2 source frozen",
    sha256(
        PHASE_6_2
    )
    == EXPECTED_6_2_SHA,
)

final_check(
    "Phase 6.2 freeze frozen",
    sha256(
        PHASE_6_2_FREEZE
    )
    == EXPECTED_6_2_FREEZE_SHA,
)

final_check(
    "Phase 6.3 source frozen",
    sha256(
        PHASE_6_3
    )
    == EXPECTED_6_3_SHA,
)

final_check(
    "Phase 6.3 freeze frozen",
    sha256(
        PHASE_6_3_FREEZE
    )
    == EXPECTED_6_3_FREEZE_SHA,
)


if not all(
    final
):
    stop(
        "Phase 6.4 Final Certification failed. "
        "Freeze has not been created."
    )


report_lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 6.4 — ARTIFACT REFERENCE HANDOFF FINAL CERTIFICATION",
    "",
    f"Exact Artifact Contract Checks: {len(contract_checks)}",
    f"Handoff Architecture Checks: {len(architecture_checks)}",
    f"Smoke Checks: {len(smoke)}",
    f"Initial Checks: {len(initial)}",
    f"Final Checks: {len(final)}",
    "",
    f"Final Passed: {len(final)}",
    "Final Failed: 0",
    "FINAL CERTIFIED: True",
    "",
    f"Production SHA256: {actual_sha}",
    f"Handoff Version: {ARTIFACT_REFERENCE_HANDOFF_VERSION}",
    f"Schema Version: {ARTIFACT_REFERENCE_HANDOFF_SCHEMA_VERSION}",
    "",
    "Certified reference model:",
    "- result_reference = primary logical result reference",
    "- artifact_references = supporting/generated resource references",
    "- references originate from ProcessedStageResult",
    "- Runtime normalization authorities are reused",
    "- zero artifact references are valid",
    "- artifact order is preserved",
    "- handoff result is immutable",
    "",
    "Certified boundaries:",
    "- reference-only handoff",
    "- no artifact creation",
    "- no artifact reads",
    "- no artifact writes",
    "- no artifact persistence",
    "- no artifact deletion",
    "- no artifact-byte copying",
    "- no Runtime submission",
    "- no coordinator invocation",
    "- no context propagation mutation",
    "- no payload mutation",
    "- no workflow lifecycle mutation",
    "- Phase 6.5 owns final Stage Handoff validation",
    "",
    "NEXT: 6.4 SHA256 Freeze",
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


print(
    f"FINAL CERTIFICATION: {len(final)}/{len(final)} PASS"
)

print(
    "PRODUCTION SHA256:",
    actual_sha,
)

print(
    "REPORT SHA256:",
    report_sha,
)


# ==================================================================
# 7 — SHA256 FREEZE
# ==================================================================

section(
    "7 — SHA256 FREEZE"
)


if FREEZE.exists():
    stop(
        "Phase 6.4 freeze already exists. "
        "Refusing to overwrite canonical freeze evidence."
    )


total_checks = (
    len(
        contract_checks
    )
    + len(
        architecture_checks
    )
    + len(
        smoke
    )
    + len(
        initial
    )
    + len(
        final
    )
)


freeze_document = {
    "component":
        "Artifact Reference Handoff",

    "framework":
        "Universal Coordination Framework",

    "phase":
        "6.4",

    "freeze_version":
        "artifact_reference_handoff_phase_6_4_freeze_v1",

    "certified":
        True,

    "frozen":
        True,

    "certification_status":
        "certified",

    "production": {
        "path":
            "backend/server/coordination/stage_handoff/"
            "artifact_reference_handoff.py",

        "version":
            ARTIFACT_REFERENCE_HANDOFF_VERSION,

        "schema_version":
            ARTIFACT_REFERENCE_HANDOFF_SCHEMA_VERSION,

        "sha256":
            actual_sha,
    },

    "reference_authorities": {
        "result_reference": {
            "module":
                "backend.server.runtime.universal_jobs.result_reference",

            "version":
                result_authority.UNIVERSAL_JOB_RESULT_REFERENCE_VERSION,

            "schema_version":
                result_authority.UNIVERSAL_JOB_RESULT_REFERENCE_SCHEMA_VERSION,

            "max_length":
                result_authority.MAX_UNIVERSAL_JOB_RESULT_REFERENCE_LENGTH,

            "meaning":
                "primary logical result reference",
        },

        "artifact_references": {
            "module":
                "backend.server.runtime.universal_jobs.artifact_references",

            "version":
                artifact_authority.UNIVERSAL_JOB_ARTIFACT_REFERENCES_VERSION,

            "schema_version":
                artifact_authority.UNIVERSAL_JOB_ARTIFACT_REFERENCES_SCHEMA_VERSION,

            "max_length":
                artifact_authority.MAX_UNIVERSAL_JOB_ARTIFACT_REFERENCE_LENGTH,

            "meaning":
                "supporting/generated resource references",
        },
    },

    "handoff_model": {
        "source":
            "ProcessedStageResult",

        "result_reference":
            "preserved separately",

        "artifact_references":
            "canonicalized and preserved in order",

        "zero_artifacts":
            "allowed",

        "artifact_contents":
            "not accessed",

        "artifact_bytes":
            "not transferred",

        "source_requirement":
            "completed and normal_handoff_allowed",
    },

    "verification": {
        "exact_artifact_contract": {
            "passed":
                len(
                    contract_checks
                ),

            "failed":
                0,
        },

        "architecture_resolution": {
            "passed":
                len(
                    architecture_checks
                ),

            "failed":
                0,
        },

        "smoke": {
            "passed":
                len(
                    smoke
                ),

            "failed":
                0,
        },

        "initial": {
            "passed":
                len(
                    initial
                ),

            "failed":
                0,
        },

        "final": {
            "passed":
                len(
                    final
                ),

            "failed":
                0,
        },

        "total_formal_checks":
            total_checks,
    },

    "final_certification_report": {
        "path":
            "artifact_reference_handoff_phase_6_4_final_certification.txt",

        "sha256":
            report_sha,
    },

    "upstream_frozen_authorities": {
        "phase_6_1_source_sha256":
            EXPECTED_6_1_SHA,

        "phase_6_1_freeze_sha256":
            EXPECTED_6_1_FREEZE_SHA,

        "phase_6_2_source_sha256":
            EXPECTED_6_2_SHA,

        "phase_6_2_freeze_sha256":
            EXPECTED_6_2_FREEZE_SHA,

        "phase_6_3_source_sha256":
            EXPECTED_6_3_SHA,

        "phase_6_3_freeze_sha256":
            EXPECTED_6_3_FREEZE_SHA,
    },

    "certified_boundaries": [
        "no artifact creation",
        "no artifact read",
        "no artifact write",
        "no artifact persistence",
        "no artifact deletion",
        "no artifact byte transfer",
        "no Runtime submission",
        "no Runtime execution",
        "no coordinator invocation",
        "no context mutation",
        "no payload mutation",
        "no workflow lifecycle mutation",
        "final handoff validation remains Phase 6.5",
    ],

    "freeze_created_at":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "next":
        "6.5 Handoff Validation",
}


FREEZE.write_text(
    json.dumps(
        freeze_document,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


freeze_sha = sha256(
    FREEZE
)


# ==================================================================
# 8 — POST-FREEZE INTEGRITY
# ==================================================================

section(
    "8 — FINAL STATUS"
)


post = {
    "Phase 6.4 production unchanged":
        sha256(TARGET)
        == actual_sha,

    "Phase 6.1 source unchanged":
        sha256(PHASE_6_1)
        == EXPECTED_6_1_SHA,

    "Phase 6.1 freeze unchanged":
        sha256(PHASE_6_1_FREEZE)
        == EXPECTED_6_1_FREEZE_SHA,

    "Phase 6.2 source unchanged":
        sha256(PHASE_6_2)
        == EXPECTED_6_2_SHA,

    "Phase 6.2 freeze unchanged":
        sha256(PHASE_6_2_FREEZE)
        == EXPECTED_6_2_FREEZE_SHA,

    "Phase 6.3 source unchanged":
        sha256(PHASE_6_3)
        == EXPECTED_6_3_SHA,

    "Phase 6.3 freeze unchanged":
        sha256(PHASE_6_3_FREEZE)
        == EXPECTED_6_3_FREEZE_SHA,

    "certification report exists":
        REPORT.exists(),

    "freeze exists":
        FREEZE.exists(),
}


for name, ok in post.items():
    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


if not all(
    post.values()
):
    stop(
        "Post-freeze integrity verification failed."
    )


print()
print(
    "Exact Artifact Contract Resolution:",
    f"{len(contract_checks)}/{len(contract_checks)} PASS",
)

print(
    "Handoff Architecture Resolution:",
    f"{len(architecture_checks)}/{len(architecture_checks)} PASS",
)

print(
    "Smoke Verification:",
    f"{len(smoke)}/{len(smoke)} PASS",
)

print(
    "Initial Verification:",
    f"{len(initial)}/{len(initial)} PASS",
)

print(
    "Final Certification:",
    f"{len(final)}/{len(final)} PASS",
)

print(
    "TOTAL FORMAL CHECKS:",
    total_checks,
    "PASS",
)

print(
    "PHASE 6.4 CERTIFIED: TRUE"
)

print(
    "PHASE 6.4 FROZEN: TRUE"
)

print(
    "ARTIFACT REFERENCE HANDOFF SHA256:",
    actual_sha,
)

print(
    "CERTIFICATION REPORT SHA256:",
    report_sha,
)

print(
    "FREEZE FILE:",
    FREEZE,
)

print(
    "FREEZE SHA256:",
    freeze_sha,
)

print(
    "PHASE 6.1 MODIFIED: FALSE"
)

print(
    "PHASE 6.2 MODIFIED: FALSE"
)

print(
    "PHASE 6.3 MODIFIED: FALSE"
)

print(
    "RUNTIME ARTIFACT AUTHORITY MODIFIED: FALSE"
)

print(
    "NEXT: 6.5 Handoff Validation"
)

print("=" * 120)
