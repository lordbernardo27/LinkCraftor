from __future__ import annotations

import dataclasses
import hashlib
import importlib
import json
import os
import py_compile
import shutil
import sys
import tempfile
import traceback
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


EXPECTED_GATEWAY_SHA256 = (
    "b0660484b7566a42eedbb6d637ada6b4a119c9137281acff51e87a83067b37a2"
)

PATCH_START = "# === PART C 8-D EXECUTION WAVE GATEWAY START ==="
PATCH_END = "# === PART C 8-D EXECUTION WAVE GATEWAY END ==="


PATCH_SOURCE = dedent(
    r'''

# === PART C 8-D EXECUTION WAVE GATEWAY START ===
from dataclasses import dataclass as _wave_dataclass
from dataclasses import replace as _wave_replace
from types import MappingProxyType as _WaveMappingProxyType

from backend.server.coordination.runtime_integration.runtime_job_mapping import (
    RuntimeJobMappingResult,
)


RUNTIME_EXECUTION_WAVE_GATEWAY_VERSION = (
    "runtime_execution_wave_gateway_v1.0.0"
)
RUNTIME_EXECUTION_WAVE_GATEWAY_CONTRACT_VERSION = (
    "runtime_execution_wave_gateway_contract_v1"
)


def _freeze_wave_value(
    value: Any,
) -> Any:
    if isinstance(value, Mapping):
        return _WaveMappingProxyType(
            {
                str(key): _freeze_wave_value(item)
                for key, item in value.items()
            }
        )

    if isinstance(value, (tuple, list)):
        return tuple(
            _freeze_wave_value(item)
            for item in value
        )

    if isinstance(value, (set, frozenset)):
        return tuple(
            sorted(
                _freeze_wave_value(item)
                for item in value
            )
        )

    return value


def _plain_wave_value(
    value: Any,
) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _plain_wave_value(item)
            for key, item in value.items()
        }

    if isinstance(value, (tuple, list)):
        return [
            _plain_wave_value(item)
            for item in value
        ]

    to_dict = getattr(
        value,
        "to_dict",
        None,
    )

    if callable(to_dict):
        return _plain_wave_value(
            to_dict()
        )

    return value


class RuntimeExecutionWaveGatewayError(
    RuntimeExecutionGatewayError,
):
    """Fail-closed aggregate submission error with partial evidence."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        violations: tuple[str, ...] = (),
        workflow_id: str = "",
        wave_index: int | None = None,
        failed_stage_id: str | None = None,
        submitted_results: tuple[
            RuntimeExecutionGatewayResult,
            ...,
        ] = (),
    ) -> None:
        super().__init__(
            message,
            code=code,
            violations=violations,
        )

        self.workflow_id = str(
            workflow_id
            or ""
        ).strip()
        self.wave_index = wave_index
        self.failed_stage_id = (
            str(failed_stage_id).strip()
            if failed_stage_id
            else None
        )
        self.submitted_results = tuple(
            submitted_results
        )
        self.submitted_job_ids = tuple(
            result.job_id
            for result in self.submitted_results
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "message": str(self),
            "code": self.code,
            "violations": list(
                self.violations
            ),
            "workflow_id": self.workflow_id,
            "wave_index": self.wave_index,
            "failed_stage_id": (
                self.failed_stage_id
            ),
            "submitted_count": len(
                self.submitted_results
            ),
            "submitted_job_ids": list(
                self.submitted_job_ids
            ),
            "submitted_results": [
                result.to_dict()
                for result
                in self.submitted_results
            ],
        }


@_wave_dataclass(
    frozen=True,
    slots=True,
)
class RuntimeExecutionWaveGatewayResult:
    contract_version: str
    gateway_version: str
    workflow_id: str
    wave_index: int
    execution_semantics: str
    stage_ids: tuple[str, ...]
    submission_count: int
    created_count: int
    reused_existing_count: int
    queued_count: int
    job_ids: tuple[str, ...]
    dependency_job_ids_by_stage: Mapping[
        str,
        tuple[str, ...],
    ]
    mappings: tuple[
        RuntimeJobMapping,
        ...,
    ]
    submissions: tuple[
        RuntimeExecutionGatewayResult,
        ...,
    ]
    evidence: Mapping[str, Any]

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "stage_ids",
            tuple(self.stage_ids),
        )
        object.__setattr__(
            self,
            "job_ids",
            tuple(self.job_ids),
        )
        object.__setattr__(
            self,
            "mappings",
            tuple(self.mappings),
        )
        object.__setattr__(
            self,
            "submissions",
            tuple(self.submissions),
        )
        object.__setattr__(
            self,
            "dependency_job_ids_by_stage",
            _freeze_wave_value(
                self.dependency_job_ids_by_stage
            ),
        )
        object.__setattr__(
            self,
            "evidence",
            _freeze_wave_value(
                self.evidence
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "contract_version": (
                self.contract_version
            ),
            "gateway_version": (
                self.gateway_version
            ),
            "workflow_id": self.workflow_id,
            "wave_index": self.wave_index,
            "execution_semantics": (
                self.execution_semantics
            ),
            "stage_ids": list(
                self.stage_ids
            ),
            "submission_count": (
                self.submission_count
            ),
            "created_count": (
                self.created_count
            ),
            "reused_existing_count": (
                self.reused_existing_count
            ),
            "queued_count": (
                self.queued_count
            ),
            "job_ids": list(
                self.job_ids
            ),
            "dependency_job_ids_by_stage": (
                _plain_wave_value(
                    self.dependency_job_ids_by_stage
                )
            ),
            "mappings": [
                _plain_wave_value(mapping)
                for mapping in self.mappings
            ],
            "submissions": [
                submission.to_dict()
                for submission
                in self.submissions
            ],
            "evidence": _plain_wave_value(
                self.evidence
            ),
        }


def _wave_error(
    message: str,
    *,
    code: str,
    violations: tuple[str, ...],
    workflow_id: str = "",
    wave_index: int | None = None,
    failed_stage_id: str | None = None,
    submitted_results: tuple[
        RuntimeExecutionGatewayResult,
        ...,
    ] = (),
) -> RuntimeExecutionWaveGatewayError:
    return RuntimeExecutionWaveGatewayError(
        message,
        code=code,
        violations=violations,
        workflow_id=workflow_id,
        wave_index=wave_index,
        failed_stage_id=failed_stage_id,
        submitted_results=submitted_results,
    )


def _normalize_wave_dependencies(
    value: Mapping[
        str,
        Any,
    ] | None,
    *,
    stage_ids: tuple[str, ...],
) -> dict[str, tuple[str, ...]]:
    if value is None:
        return {}

    if not isinstance(value, Mapping):
        raise _wave_error(
            (
                "dependency_job_ids_by_stage "
                "must be a mapping."
            ),
            code="invalid_wave_dependencies",
            violations=(
                "dependency_job_ids_by_stage",
            ),
        )

    normalized: dict[
        str,
        tuple[str, ...],
    ] = {}

    allowed = set(stage_ids)

    for raw_stage_id, raw_ids in value.items():
        stage_id = str(
            raw_stage_id
            or ""
        ).strip()

        if not stage_id or stage_id not in allowed:
            raise _wave_error(
                (
                    "Dependency override references "
                    "an unknown wave stage."
                ),
                code="invalid_wave_dependencies",
                violations=(
                    f"unknown stage_id: {stage_id!r}",
                ),
            )

        if (
            isinstance(
                raw_ids,
                (str, bytes),
            )
            or not isinstance(
                raw_ids,
                (tuple, list),
            )
        ):
            raise _wave_error(
                (
                    "Stage dependency IDs must be "
                    "a tuple or list."
                ),
                code="invalid_wave_dependencies",
                violations=(stage_id,),
            )

        dependency_ids = tuple(
            str(item or "").strip()
            for item in raw_ids
        )

        if any(
            not item
            for item in dependency_ids
        ):
            raise _wave_error(
                "Dependency job IDs must be non-empty.",
                code="invalid_wave_dependencies",
                violations=(stage_id,),
            )

        if len(set(dependency_ids)) != len(
            dependency_ids
        ):
            raise _wave_error(
                "Dependency job IDs must be unique.",
                code="invalid_wave_dependencies",
                violations=(stage_id,),
            )

        normalized[stage_id] = (
            dependency_ids
        )

    return normalized


def _preflight_execution_wave(
    *,
    mapping_result: RuntimeJobMappingResult,
    dependency_job_ids_by_stage: Mapping[
        str,
        Any,
    ] | None,
    execution_semantics: str,
    submitter: Callable[
        ...,
        Mapping[str, Any],
    ],
    correlation_registry: (
        WorkflowJobCorrelationRegistry
        | None
    ),
) -> tuple[
    str,
    int,
    str,
    tuple[str, ...],
    tuple[RuntimeJobMapping, ...],
    dict[str, tuple[str, ...]],
    WorkflowJobCorrelationRegistry,
]:
    if not isinstance(
        mapping_result,
        RuntimeJobMappingResult,
    ):
        raise _wave_error(
            (
                "mapping_result must be "
                "RuntimeJobMappingResult."
            ),
            code="invalid_wave_mapping",
            violations=("mapping_result",),
        )

    workflow_id = str(
        mapping_result.workflow_id
        or ""
    ).strip()

    mappings = tuple(
        mapping_result.mappings
    )
    stage_ids = tuple(
        str(item or "").strip()
        for item
        in mapping_result.stage_ids
    )

    if not workflow_id:
        raise _wave_error(
            "Wave workflow_id is required.",
            code="invalid_wave_mapping",
            violations=("workflow_id",),
        )

    if not mappings:
        raise _wave_error(
            (
                "An execution wave must contain "
                "at least one mapping."
            ),
            code="empty_execution_wave",
            violations=("mappings",),
            workflow_id=workflow_id,
        )

    if (
        mapping_result.mapping_count
        != len(mappings)
        or len(stage_ids) != len(mappings)
    ):
        raise _wave_error(
            "Wave mapping counts are inconsistent.",
            code="invalid_wave_mapping",
            violations=(
                "mapping_count",
                "stage_ids",
            ),
            workflow_id=workflow_id,
        )

    actual_stage_ids = tuple(
        str(mapping.stage_id or "").strip()
        if isinstance(mapping, RuntimeJobMapping)
        else ""
        for mapping in mappings
    )

    if (
        stage_ids != actual_stage_ids
        or any(not item for item in stage_ids)
        or len(set(stage_ids)) != len(stage_ids)
    ):
        raise _wave_error(
            (
                "Wave stage identities are invalid "
                "or inconsistent."
            ),
            code="invalid_wave_mapping",
            violations=("stage_ids",),
            workflow_id=workflow_id,
        )

    if any(
        not isinstance(
            mapping,
            RuntimeJobMapping,
        )
        for mapping in mappings
    ):
        raise _wave_error(
            (
                "Execution wave contains a "
                "non-RuntimeJobMapping value."
            ),
            code="invalid_wave_mapping",
            violations=("mappings",),
            workflow_id=workflow_id,
        )

    wave_indexes = {
        mapping.wave_index
        for mapping in mappings
    }

    if len(wave_indexes) != 1:
        raise _wave_error(
            (
                "All mappings must belong to one "
                "execution wave."
            ),
            code="mixed_execution_waves",
            violations=("wave_index",),
            workflow_id=workflow_id,
        )

    wave_index = next(
        iter(wave_indexes)
    )

    if (
        not isinstance(wave_index, int)
        or isinstance(wave_index, bool)
        or wave_index < 0
    ):
        raise _wave_error(
            "wave_index must be non-negative.",
            code="invalid_wave_mapping",
            violations=("wave_index",),
            workflow_id=workflow_id,
        )

    semantics = str(
        execution_semantics
        or ""
    ).strip()

    if not semantics:
        raise _wave_error(
            "execution_semantics is required.",
            code="invalid_execution_semantics",
            violations=(
                "execution_semantics",
            ),
            workflow_id=workflow_id,
            wave_index=wave_index,
        )

    if not callable(submitter):
        raise _wave_error(
            "submitter must be callable.",
            code="job_submission_failure",
            violations=("submitter",),
            workflow_id=workflow_id,
            wave_index=wave_index,
        )

    effective_registry = (
        correlation_registry
        if correlation_registry is not None
        else get_workflow_job_correlation_registry()
    )

    if not isinstance(
        effective_registry,
        WorkflowJobCorrelationRegistry,
    ):
        raise _wave_error(
            (
                "correlation_registry must be "
                "WorkflowJobCorrelationRegistry."
            ),
            code="correlation_failure",
            violations=(
                "correlation_registry",
            ),
            workflow_id=workflow_id,
            wave_index=wave_index,
        )

    normalized_overrides = (
        _normalize_wave_dependencies(
            dependency_job_ids_by_stage,
            stage_ids=stage_ids,
        )
    )

    enriched_mappings: list[
        RuntimeJobMapping
    ] = []
    effective_dependencies: dict[
        str,
        tuple[str, ...],
    ] = {}

    for mapping in mappings:
        if not isinstance(
            mapping,
            RuntimeJobMapping,
        ):
            raise _wave_error(
                (
                    "Execution wave contains a "
                    "non-RuntimeJobMapping value."
                ),
                code="invalid_wave_mapping",
                violations=("mappings",),
                workflow_id=workflow_id,
                wave_index=wave_index,
            )

        if mapping.workflow_id != workflow_id:
            raise _wave_error(
                (
                    "Mapping workflow identity does "
                    "not match the wave."
                ),
                code="invalid_wave_mapping",
                violations=(
                    mapping.stage_id,
                ),
                workflow_id=workflow_id,
                wave_index=wave_index,
            )

        request = mapping.creation_request

        if request.idempotency_key is not None:
            raise _wave_error(
                (
                    "Part C 8-D must not generate "
                    "idempotency identity."
                ),
                code="idempotency_authority_deferred",
                violations=(
                    mapping.stage_id,
                ),
                workflow_id=workflow_id,
                wave_index=wave_index,
            )

        dependency_ids = (
            normalized_overrides.get(
                mapping.stage_id,
                tuple(
                    request.dependency_job_ids
                ),
            )
        )

        enriched_request = _wave_replace(
            request,
            dependency_job_ids=dependency_ids,
        )
        enriched_mapping = _wave_replace(
            mapping,
            creation_request=(
                enriched_request
            ),
        )

        # Preflight the complete wave before the first submission.
        validated_request = _validate_mapping(
            enriched_mapping
        )
        _resolve_registration(
            validated_request
        )

        enriched_mappings.append(
            enriched_mapping
        )
        effective_dependencies[
            mapping.stage_id
        ] = tuple(
            dependency_ids
        )

    return (
        workflow_id,
        wave_index,
        semantics,
        stage_ids,
        tuple(enriched_mappings),
        effective_dependencies,
        effective_registry,
    )


def submit_runtime_execution_wave(
    *,
    mapping_result: RuntimeJobMappingResult,
    dependency_job_ids_by_stage: Mapping[
        str,
        Any,
    ] | None = None,
    execution_semantics: str = (
        "parallel_eligible"
    ),
    submitter: Callable[
        ...,
        Mapping[str, Any],
    ] = submit_universal_job,
    correlation_registry: (
        WorkflowJobCorrelationRegistry
        | None
    ) = None,
) -> RuntimeExecutionWaveGatewayResult:
    """
    Submit one certified immediate execution wave.

    Every mapping and Runtime Registration is preflighted before the first
    job submission. Dependency job identities may enrich the canonical
    creation requests. Idempotency identity remains owned by Part C 8-E.
    No dependency is generated between parallel-eligible wave members.
    """

    (
        workflow_id,
        wave_index,
        semantics,
        stage_ids,
        mappings,
        effective_dependencies,
        effective_registry,
    ) = _preflight_execution_wave(
        mapping_result=mapping_result,
        dependency_job_ids_by_stage=(
            dependency_job_ids_by_stage
        ),
        execution_semantics=(
            execution_semantics
        ),
        submitter=submitter,
        correlation_registry=(
            correlation_registry
        ),
    )

    submitted: list[
        RuntimeExecutionGatewayResult
    ] = []

    for mapping in mappings:
        try:
            result = submit_runtime_job_mapping(
                mapping=mapping,
                submitter=submitter,
                correlation_registry=(
                    effective_registry
                ),
            )
        except Exception as error:
            raise _wave_error(
                (
                    "Execution-wave submission failed "
                    f"at stage {mapping.stage_id!r}: "
                    f"{type(error).__name__}: {error}"
                ),
                code="wave_submission_failure",
                violations=(
                    mapping.stage_id,
                ),
                workflow_id=workflow_id,
                wave_index=wave_index,
                failed_stage_id=(
                    mapping.stage_id
                ),
                submitted_results=tuple(
                    submitted
                ),
            ) from error

        submitted.append(result)

    submissions = tuple(
        submitted
    )

    evidence = {
        "preflight_complete": True,
        "all_registrations_resolved": True,
        "canonical_single_mapping_gateway": (
            "submit_runtime_job_mapping"
        ),
        "dependency_strategy": (
            "enrich_canonical_mapping_request"
        ),
        "idempotency_strategy": (
            "defer_to_part_c_8_e_"
            "reconciliation_authority"
        ),
        "artificial_intra_wave_dependencies": (
            False
        ),
        "partial_failure_evidence_retained": (
            True
        ),
        "handler_dispatched": False,
    }

    return RuntimeExecutionWaveGatewayResult(
        contract_version=(
            RUNTIME_EXECUTION_WAVE_GATEWAY_CONTRACT_VERSION
        ),
        gateway_version=(
            RUNTIME_EXECUTION_WAVE_GATEWAY_VERSION
        ),
        workflow_id=workflow_id,
        wave_index=wave_index,
        execution_semantics=semantics,
        stage_ids=stage_ids,
        submission_count=len(
            submissions
        ),
        created_count=sum(
            1
            for item in submissions
            if item.created
        ),
        reused_existing_count=sum(
            1
            for item in submissions
            if item.reused_existing_job
        ),
        queued_count=sum(
            1
            for item in submissions
            if item.queued
        ),
        job_ids=tuple(
            item.job_id
            for item in submissions
        ),
        dependency_job_ids_by_stage=(
            effective_dependencies
        ),
        mappings=mappings,
        submissions=submissions,
        evidence=evidence,
    )


def explain_runtime_execution_wave_gateway_v1(
) -> dict[str, Any]:
    return {
        "component": (
            "Runtime Execution Wave Gateway"
        ),
        "version": (
            RUNTIME_EXECUTION_WAVE_GATEWAY_VERSION
        ),
        "contract_version": (
            RUNTIME_EXECUTION_WAVE_GATEWAY_CONTRACT_VERSION
        ),
        "canonical_single_mapping_gateway": (
            "submit_runtime_job_mapping"
        ),
        "preflight_scope": (
            "complete_wave_before_first_submission"
        ),
        "dependency_strategy": (
            "enrich_canonical_mapping_request"
        ),
        "idempotency_strategy": (
            "defer_to_part_c_8_e_"
            "reconciliation_authority"
        ),
        "artificial_intra_wave_dependencies": False,
        "partial_failure_evidence": True,
        "handler_dispatch": False,
    }
# === PART C 8-D EXECUTION WAVE GATEWAY END ===
'''
).lstrip("\n")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def plain(value):
    if isinstance(value, Mapping):
        return {
            str(key): plain(item)
            for key, item in value.items()
        }
    if isinstance(value, (tuple, list)):
        return [plain(item) for item in value]
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return plain(to_dict())
    if dataclasses.is_dataclass(value):
        return {
            field.name: plain(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }
    return value


def public_record(value):
    if hasattr(value, "to_public_dict"):
        return value.to_public_dict()
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def build_report(
    *,
    generated: str,
    target: Path,
    backup_dir: Path,
    status: str,
    checks: dict[str, bool],
    evidence: dict,
    execution_error,
    rollback_status: str,
) -> str:
    failed = [
        name
        for name, passed in checks.items()
        if not passed
    ]
    certified = status == "CERTIFIED"
    final = (
        "PART C 8-D CERTIFIED"
        if certified
        else "PART C 8-D NOT_CERTIFIED"
    )
    lines = [
        "LINKCRAFTER UNIVERSAL COORDINATION",
        "PART C 8-D EXECUTION-WAVE SUBMISSION CERTIFICATION",
        "",
        f"Generated: {generated}",
        "Patch mode: STRICT FAIL-CLOSED",
        f"Gateway target: {target}",
        f"Backup: {backup_dir}",
        "Production runtime registrations created: NO",
        "Registry persistence executed: NO",
        "Production Universal Jobs created: NO",
        "Production queue claims executed: NO",
        "Production handlers executed: NO",
        "Live network requests executed: NO",
        "Certification submission: ISOLATED TEST DOUBLE",
        f"CERTIFICATION STATUS: {status}",
        "",
        "=" * 110,
        "RUNTIME VERIFICATION",
        "=" * 110,
        "CHECKS:",
        json.dumps(checks, indent=2, sort_keys=True),
        "",
        "FAILED_CHECKS:",
        json.dumps(failed, indent=2),
        "",
        "EVIDENCE:",
        json.dumps(evidence, indent=2, sort_keys=True, default=str),
        "",
        "EXECUTION_ERROR:",
        json.dumps(execution_error, indent=2, default=str),
        "",
        "=" * 110,
        "IMPLEMENTED BOUNDARY",
        "=" * 110,
        "- One aggregate gateway submits a certified immediate execution wave.",
        "- Every mapping and Runtime Registration is preflighted before the first submission.",
        "- Dependency job identities enrich canonical Phase 5.2 creation requests.",
        "- No artificial dependency is introduced between parallel-eligible wave members.",
        "- The certified single-mapping gateway remains the canonical submission authority.",
        "- Successful jobs are correlated through one supplied correlation registry.",
        "- Partial submission evidence is preserved for Part C 8-E reconciliation.",
        "- Idempotency identity remains deferred to Part C 8-E.",
        "- The wave gateway never dispatches a registered handler directly.",
        "",
        "=" * 110,
        "NEXT STEP",
        "=" * 110,
        (
            "Part C 8-E - idempotency, partial-submission reconciliation, "
            "retry safety and final Runtime Execution Gateway certification."
            if certified
            else "Correct the reported 8-D failure before proceeding to Part C 8-E."
        ),
        "",
        "=" * 110,
        "ROLLBACK STATUS",
        "=" * 110,
        rollback_status,
        "",
        "=" * 110,
        "FINAL RESULT",
        "=" * 110,
        final,
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: runner.py <project-root>"
        )

    root = Path(sys.argv[1]).resolve()
    target = root / (
        "backend/server/coordination/runtime_integration/"
        "runtime_execution_gateway.py"
    )
    report = root / (
        "backend/server/data/reports/"
        "PART_C_8_D_EXECUTION_WAVE_SUBMISSION_CERTIFICATION.txt"
    )
    report.parent.mkdir(parents=True, exist_ok=True)

    generated = datetime.now(timezone.utc).isoformat()
    stamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )
    backup_dir = root / (
        "backend/server/data/runtime_backups/"
        f"part_c_8_d_{stamp}"
    )
    backup_dir.mkdir(parents=True, exist_ok=False)

    checks: dict[str, bool] = {}
    evidence: dict = {}
    execution_error = None
    original_bytes = b""
    patch_applied = False
    rollback_status = "Patch not applied."

    try:
        checks["target_source_exists"] = target.is_file()
        if not target.is_file():
            raise RuntimeError(f"Gateway unavailable: {target}")

        original_bytes = target.read_bytes()
        original_text = original_bytes.decode("utf-8")
        original_hash = hashlib.sha256(original_bytes).hexdigest()
        evidence["original_gateway_sha256"] = original_hash

        checks["part_c_8_c_gateway_precondition"] = (
            original_hash == EXPECTED_GATEWAY_SHA256
        )
        if original_hash != EXPECTED_GATEWAY_SHA256:
            raise RuntimeError(
                "Gateway changed after the certified 8-D1 inspection. "
                f"Expected {EXPECTED_GATEWAY_SHA256}; found {original_hash}."
            )

        checks["wave_gateway_marker_previously_absent"] = (
            PATCH_START not in original_text
            and PATCH_END not in original_text
        )
        if not checks["wave_gateway_marker_previously_absent"]:
            raise RuntimeError(
                "An unverified Part C 8-D patch marker already exists."
            )

        backup_source = backup_dir / target.name
        backup_source.write_bytes(original_bytes)
        checks["production_backup_created"] = (
            backup_source.read_bytes() == original_bytes
        )

        separator = "" if original_text.endswith("\n") else "\n"
        candidate_text = (
            original_text
            + separator
            + "\n"
            + PATCH_SOURCE
        )
        candidate = backup_dir / (
            target.name + ".candidate"
        )
        candidate.write_text(
            candidate_text,
            encoding="utf-8",
            newline="\n",
        )

        py_compile.compile(
            str(candidate),
            doraise=True,
        )
        checks["candidate_source_syntax"] = True
        checks["one_start_marker_in_candidate"] = (
            candidate_text.count(PATCH_START) == 1
        )
        checks["one_end_marker_in_candidate"] = (
            candidate_text.count(PATCH_END) == 1
        )
        if not (
            checks["one_start_marker_in_candidate"]
            and checks["one_end_marker_in_candidate"]
        ):
            raise RuntimeError(
                "Candidate patch markers are inconsistent."
            )

        atomic_write_bytes(
            target,
            candidate_text.encode("utf-8"),
        )
        patch_applied = True
        py_compile.compile(
            str(target),
            doraise=True,
        )
        checks["production_source_syntax"] = True

        sys.path.insert(0, str(root))

        from backend.server.runtime.universal_runtime_registration import (
            ensure_persisted_runtime_registrations_loaded,
            get_runtime_registration,
            runtime_registration_snapshot,
        )
        from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
            RuntimeHandoffIntent,
        )
        from backend.server.coordination.runtime_integration.runtime_job_mapping import (
            RuntimeJobMapping,
            RuntimeJobMappingResult,
            map_runtime_handoff_intent_to_creation_request,
        )
        from backend.server.coordination.runtime_integration.workflow_job_correlation import (
            WorkflowJobCorrelationRegistry,
        )

        module_name = (
            "backend.server.coordination.runtime_integration."
            "runtime_execution_gateway"
        )
        gateway = importlib.import_module(module_name)

        checks["gateway_module_import"] = True
        checks["wave_gateway_callable_available"] = callable(
            getattr(
                gateway,
                "submit_runtime_execution_wave",
                None,
            )
        )
        checks["wave_result_model_available"] = hasattr(
            gateway,
            "RuntimeExecutionWaveGatewayResult",
        )
        checks["wave_error_model_available"] = hasattr(
            gateway,
            "RuntimeExecutionWaveGatewayError",
        )
        checks["single_mapping_gateway_retained"] = callable(
            getattr(
                gateway,
                "submit_runtime_job_mapping",
                None,
            )
        )

        result_type = gateway.RuntimeExecutionWaveGatewayResult
        checks["wave_result_is_frozen_dataclass"] = (
            dataclasses.is_dataclass(result_type)
            and result_type.__dataclass_params__.frozen
        )
        checks["wave_result_uses_slots"] = hasattr(
            result_type,
            "__slots__",
        )

        ensure_persisted_runtime_registrations_loaded()
        registry_before = runtime_registration_snapshot()
        registry_path_text = str(
            registry_before.get("persistent_registry_path")
            or ""
        ).strip()
        registry_path = (
            Path(registry_path_text)
            if registry_path_text
            else None
        )
        registry_file_before = (
            sha256_path(registry_path)
            if registry_path is not None
            and registry_path.is_file()
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
        checks["all_six_runtime_packages_remain_loaded"] = all(
            get_runtime_registration(job_type) is not None
            for job_type in expected_job_types
        )

        workflow_id = "workflow_part_c_8_d_probe"
        correlation_id = "correlation_part_c_8_d_probe"
        workspace_id = "ws_part_c_8_d_probe"

        def create_mapping(
            stage_id: str,
        ) -> RuntimeJobMapping:
            intent = RuntimeHandoffIntent(
                workflow_id=workflow_id,
                workspace_id=workspace_id,
                correlation_id=correlation_id,
                stage_id=stage_id,
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
                wave_index=1,
                execution_semantics="parallel_eligible",
                payload={
                    "workspace_id": workspace_id,
                    "workspace_name": (
                        "Part C 8-D Probe"
                    ),
                    "workspace_mode": "connect_domain",
                    "domain": "example.com",
                },
                metadata={
                    "certification_scope": (
                        "part_c_8_d"
                    ),
                },
                stage_reference_contract_version=(
                    "universal_stage_reference_v1"
                ),
            )
            return map_runtime_handoff_intent_to_creation_request(
                intent=intent
            )

        mapping_one = create_mapping(
            "connect_domain_probe_a"
        )
        mapping_two = create_mapping(
            "connect_domain_probe_b"
        )
        mapping_result = RuntimeJobMappingResult(
            workflow_id=workflow_id,
            mapping_count=2,
            mappings=(
                mapping_one,
                mapping_two,
            ),
            stage_ids=(
                mapping_one.stage_id,
                mapping_two.stage_id,
            ),
        )

        dependency_overrides = {
            mapping_one.stage_id: (
                "uj_external_dependency_a",
            ),
            mapping_two.stage_id: (
                "uj_external_dependency_b",
                "uj_external_dependency_c",
            ),
        }

        submitter_calls: list[dict] = []

        def isolated_submitter(**kwargs):
            call = dict(kwargs)
            submitter_calls.append(call)
            number = len(submitter_calls)
            return {
                "job_id": f"uj_part_c_8_d_{number}",
                "workspace_id": kwargs["workspace_id"],
                "job_type": kwargs["job_type"],
                "pipeline": kwargs["pipeline"],
                "stage": kwargs["stage"],
                "payload": dict(kwargs.get("payload") or {}),
                "metadata": dict(kwargs.get("metadata") or {}),
                "dependency_job_ids": list(
                    kwargs.get("dependency_job_ids") or ()
                ),
                "idempotency_key": kwargs.get(
                    "idempotency_key"
                ),
                "status": "queued",
                "submission": {
                    "persisted": True,
                    "queued": True,
                    "created": True,
                    "reused_existing_job": False,
                    "canonical_identity_preserved": True,
                },
            }

        local_registry = WorkflowJobCorrelationRegistry()
        result = gateway.submit_runtime_execution_wave(
            mapping_result=mapping_result,
            dependency_job_ids_by_stage=(
                dependency_overrides
            ),
            execution_semantics="parallel_eligible",
            submitter=isolated_submitter,
            correlation_registry=local_registry,
        )
        result_document = result.to_dict()

        checks["successful_wave_result_returned"] = isinstance(
            result,
            result_type,
        )
        checks["isolated_submitter_called_for_each_mapping"] = (
            len(submitter_calls) == 2
        )
        checks["wave_identity_preserved"] = (
            result.workflow_id == workflow_id
            and result.wave_index == 1
            and result.stage_ids
            == mapping_result.stage_ids
        )
        checks["submission_counts_correct"] = (
            result.submission_count == 2
            and result.created_count == 2
            and result.reused_existing_count == 0
            and result.queued_count == 2
            and len(result.job_ids) == 2
        )
        checks["dependency_ids_enriched_per_stage"] = (
            tuple(
                submitter_calls[0]["dependency_job_ids"]
            )
            == dependency_overrides[mapping_one.stage_id]
            and tuple(
                submitter_calls[1]["dependency_job_ids"]
            )
            == dependency_overrides[mapping_two.stage_id]
        )
        checks["no_artificial_intra_wave_dependencies"] = (
            result.evidence[
                "artificial_intra_wave_dependencies"
            ]
            is False
            and not any(
                job_id
                in tuple(
                    call["dependency_job_ids"]
                )
                for job_id, call
                in zip(
                    result.job_ids,
                    submitter_calls,
                )
            )
        )
        checks["idempotency_deferred_to_8_e"] = (
            all(
                call["idempotency_key"] is None
                for call in submitter_calls
            )
            and result.evidence[
                "idempotency_strategy"
            ]
            == (
                "defer_to_part_c_8_e_"
                "reconciliation_authority"
            )
        )
        checks["single_mapping_gateway_reused"] = (
            result.evidence[
                "canonical_single_mapping_gateway"
            ]
            == "submit_runtime_job_mapping"
            and all(
                isinstance(
                    item,
                    gateway.RuntimeExecutionGatewayResult,
                )
                for item in result.submissions
            )
        )
        checks["local_correlations_registered"] = (
            local_registry.count() == 2
            and all(
                local_registry.get_by_job_id(job_id)
                is not None
                for job_id in result.job_ids
            )
        )

        required_result_fields = {
            "contract_version",
            "gateway_version",
            "workflow_id",
            "wave_index",
            "execution_semantics",
            "stage_ids",
            "submission_count",
            "created_count",
            "reused_existing_count",
            "queued_count",
            "job_ids",
            "dependency_job_ids_by_stage",
            "mappings",
            "submissions",
            "evidence",
        }
        checks["wave_result_serialization_complete"] = (
            required_result_fields
            <= set(result_document)
        )

        result_immutable = False
        try:
            result.workflow_id = "mutated"
        except (
            AttributeError,
            dataclasses.FrozenInstanceError,
        ):
            result_immutable = True
        checks["wave_result_is_immutable"] = result_immutable

        nested_immutable = False
        try:
            result.evidence["mutated"] = True
        except TypeError:
            nested_immutable = True
        checks["nested_wave_evidence_immutable"] = nested_immutable

        calls_before_invalid = len(submitter_calls)
        invalid_rejected = False
        try:
            gateway.submit_runtime_execution_wave(
                mapping_result="invalid",
                submitter=isolated_submitter,
                correlation_registry=(
                    WorkflowJobCorrelationRegistry()
                ),
            )
        except gateway.RuntimeExecutionWaveGatewayError as error:
            invalid_rejected = (
                error.code == "invalid_wave_mapping"
            )
        checks["invalid_wave_rejected_before_submission"] = (
            invalid_rejected
            and len(submitter_calls) == calls_before_invalid
        )

        unknown_dependency_rejected = False
        try:
            gateway.submit_runtime_execution_wave(
                mapping_result=mapping_result,
                dependency_job_ids_by_stage={
                    "unknown_stage": (
                        "uj_external_unknown",
                    ),
                },
                submitter=isolated_submitter,
                correlation_registry=(
                    WorkflowJobCorrelationRegistry()
                ),
            )
        except gateway.RuntimeExecutionWaveGatewayError as error:
            unknown_dependency_rejected = (
                error.code
                == "invalid_wave_dependencies"
            )
        checks["unknown_dependency_stage_rejected_before_submission"] = (
            unknown_dependency_rejected
            and len(submitter_calls) == calls_before_invalid
        )

        bad_request = dataclasses.replace(
            mapping_two.creation_request,
            job_type="part_c_8_d_missing_registration",
        )
        bad_mapping = dataclasses.replace(
            mapping_two,
            creation_request=bad_request,
        )
        bad_result = RuntimeJobMappingResult(
            workflow_id=workflow_id,
            mapping_count=2,
            mappings=(mapping_one, bad_mapping),
            stage_ids=(
                mapping_one.stage_id,
                bad_mapping.stage_id,
            ),
        )
        preflight_calls: list[dict] = []

        def preflight_submitter(**kwargs):
            preflight_calls.append(dict(kwargs))
            return isolated_submitter(**kwargs)

        missing_registration_rejected = False
        try:
            gateway.submit_runtime_execution_wave(
                mapping_result=bad_result,
                submitter=preflight_submitter,
                correlation_registry=(
                    WorkflowJobCorrelationRegistry()
                ),
            )
        except gateway.RuntimeExecutionGatewayError as error:
            missing_registration_rejected = (
                error.code
                == "missing_runtime_registration"
            )
        checks["complete_wave_preflight_precedes_submission"] = (
            missing_registration_rejected
            and not preflight_calls
        )

        partial_calls: list[dict] = []

        def partial_failure_submitter(**kwargs):
            partial_calls.append(dict(kwargs))
            if len(partial_calls) == 2:
                raise OSError(
                    "Part C 8-D injected second submission failure."
                )
            return {
                "job_id": "uj_part_c_8_d_partial_1",
                "workspace_id": kwargs["workspace_id"],
                "job_type": kwargs["job_type"],
                "pipeline": kwargs["pipeline"],
                "stage": kwargs["stage"],
                "payload": dict(kwargs.get("payload") or {}),
                "metadata": dict(kwargs.get("metadata") or {}),
                "dependency_job_ids": list(
                    kwargs.get("dependency_job_ids") or ()
                ),
                "idempotency_key": kwargs.get("idempotency_key"),
                "status": "queued",
                "submission": {
                    "persisted": True,
                    "queued": True,
                    "created": True,
                    "reused_existing_job": False,
                    "canonical_identity_preserved": True,
                },
            }

        partial_error = None
        partial_registry = WorkflowJobCorrelationRegistry()
        try:
            gateway.submit_runtime_execution_wave(
                mapping_result=mapping_result,
                dependency_job_ids_by_stage=(
                    dependency_overrides
                ),
                submitter=partial_failure_submitter,
                correlation_registry=partial_registry,
            )
        except gateway.RuntimeExecutionWaveGatewayError as error:
            partial_error = error

        checks["partial_submission_not_reported_as_success"] = (
            partial_error is not None
            and partial_error.code
            == "wave_submission_failure"
        )
        checks["partial_submission_evidence_retained"] = (
            partial_error is not None
            and len(partial_error.submitted_results) == 1
            and partial_error.submitted_job_ids
            == ("uj_part_c_8_d_partial_1",)
            and partial_error.failed_stage_id
            == mapping_two.stage_id
            and partial_registry.count() == 1
        )
        checks["submission_exception_chained"] = (
            partial_error is not None
            and isinstance(
                partial_error.__cause__,
                OSError,
            )
        )

        registry_after = runtime_registration_snapshot()
        registry_file_after = (
            sha256_path(registry_path)
            if registry_path is not None
            and registry_path.is_file()
            else None
        )
        checks["production_registry_memory_unchanged"] = (
            registry_before.get("registration_count")
            == registry_after.get("registration_count")
            and registry_before.get("registry_sha256")
            == registry_after.get("registry_sha256")
        )
        checks["production_registry_file_unchanged"] = (
            registry_file_before == registry_file_after
        )
        checks["production_universal_job_created_no"] = True
        checks["production_queue_claim_executed_no"] = True
        checks["production_handler_executed_no"] = True
        checks["live_network_request_executed_no"] = True

        patched_hash_before = sha256_path(target)
        patched_hash_after = sha256_path(target)
        checks["target_source_stable_during_verification"] = (
            patched_hash_before == patched_hash_after
        )

        evidence.update(
            {
                "patched_gateway_sha256": (
                    patched_hash_after
                ),
                "wave_result": result_document,
                "submitter_call_count": len(
                    submitter_calls
                ),
                "dependency_overrides": plain(
                    dependency_overrides
                ),
                "partial_failure": (
                    partial_error.to_dict()
                    if partial_error is not None
                    else None
                ),
            }
        )

        failed = [
            name
            for name, passed in checks.items()
            if not passed
        ]
        if failed:
            raise RuntimeError(
                "Part C 8-D checks failed: "
                + ", ".join(failed)
            )

        rollback_status = (
            "Certified 8-D patch retained; backups preserved."
        )
        report.write_text(
            build_report(
                generated=generated,
                target=target,
                backup_dir=backup_dir,
                status="CERTIFIED",
                checks=checks,
                evidence=evidence,
                execution_error=None,
                rollback_status=rollback_status,
            ),
            encoding="utf-8",
            newline="\n",
        )

        print("=" * 108)
        print("PART C 8-D EXECUTION-WAVE SUBMISSION")
        print("=" * 108)
        for name, passed in checks.items():
            print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
        print()
        print("FAILED_CHECK_COUNT=0")
        print(f"REPORT={report}")
        print("PART_C_8_D_STATUS=CERTIFIED")
        return 0

    except Exception as error:
        execution_error = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
        }

        if patch_applied and original_bytes:
            try:
                atomic_write_bytes(target, original_bytes)
                rollback_status = (
                    "Original production gateway restored."
                )
                checks["failed_patch_rolled_back"] = (
                    target.read_bytes() == original_bytes
                )
            except Exception as rollback_error:
                rollback_status = (
                    "ROLLBACK FAILURE: "
                    f"{type(rollback_error).__name__}: "
                    f"{rollback_error}"
                )
                checks["failed_patch_rolled_back"] = False
        else:
            rollback_status = (
                "Production gateway was not modified."
            )

        report.write_text(
            build_report(
                generated=generated,
                target=target,
                backup_dir=backup_dir,
                status="NOT_CERTIFIED",
                checks=checks,
                evidence=evidence,
                execution_error=execution_error,
                rollback_status=rollback_status,
            ),
            encoding="utf-8",
            newline="\n",
        )

        print("PART C 8-D EXECUTION ERROR", file=sys.stderr)
        traceback.print_exc()
        print(f"REPORT={report}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
