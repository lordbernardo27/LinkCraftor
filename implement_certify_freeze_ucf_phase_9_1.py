from __future__ import annotations

import ast
import hashlib
import importlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

RECOVERY_ROOT = (
    ROOT
    / "backend/server/coordination/coordination_recovery"
)

RECOVERY_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

INIT = RECOVERY_ROOT / "__init__.py"
P91 = RECOVERY_ROOT / "failure_policy.py"
F91 = RECOVERY_ROOT / "failure_policy.phase_9_1.freeze.json"

REPORT = (
    ROOT
    / "failure_policy_phase_9_1_final_certification.txt"
)

PHASE8_MASTER = (
    ROOT
    / "backend/server/coordination/workflow_persistence/"
    "phase_8_workflow_state_persistence.freeze.json"
)

PROCESSED_RESULT = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
    "stage_result_processor.py"
)

RUNTIME_FAILURE_CLASSIFICATION = (
    ROOT
    / "backend/server/runtime/reliability/"
    "failure_classification_containment.py"
)

RUNTIME_RETRY_GOVERNANCE = (
    ROOT
    / "backend/server/runtime/reliability/"
    "retry_governance.py"
)

RUNTIME_RECOVERY_COORDINATION = (
    ROOT
    / "backend/server/runtime/reliability/"
    "recovery_coordination.py"
)


EXPECTED = {
    PHASE8_MASTER:
        "C50FC64AB7CEB3443B5C15CEF9AEAB406644152434B181559E4F40E05F8DF6C3",

    PROCESSED_RESULT:
        "6028FED380B0E4E970F7DB30179EE2ED48C81CE00313314FF8449DA9C6A6480E",

    RUNTIME_FAILURE_CLASSIFICATION:
        "A64C6AEB8F82ED955E65AC26CFE0B1F09594CF118C00EE9B1A3796721956429A",

    RUNTIME_RETRY_GOVERNANCE:
        "40244A8C16A424ED83BDB48FA4A66169BC2F941638638FEA8A11976F238129B1",

    RUNTIME_RECOVERY_COORDINATION:
        "F73D5A612F63CC2C13CDC879F8C4E72CCAD0A80875705E2B5313DEF95F009FE9",
}


def sha256(
    path: Path,
) -> str:

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def section(
    title: str,
) -> None:

    print()
    print("=" * 120)
    print(title)
    print("=" * 120)


checks = []


def check(
    name: str,
    condition,
) -> None:

    ok = bool(
        condition
    )

    checks.append(
        (
            name,
            ok,
        )
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if not ok:
        raise RuntimeError(
            f"CHECK FAILED: {name}"
        )


def write_json(
    path: Path,
    data,
) -> None:

    path.write_text(
        json.dumps(
            data,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def purge() -> None:

    prefixes = (
        "backend.server.coordination.coordination_recovery",
    )

    for name in tuple(
        sys.modules
    ):

        if name.startswith(
            prefixes
        ):
            sys.modules.pop(
                name,
                None,
            )

    importlib.invalidate_caches()


section(
    "LINKCRAFTOR — UCF PHASE 9.1 FAILURE POLICY"
)


# ==================================================================
# 0 — AUTHORITY GUARD
# ==================================================================

section(
    "0 — FROZEN AUTHORITY GUARD"
)


for path, expected in EXPECTED.items():

    check(
        f"exact authority: {path.name}",
        path.exists()
        and sha256(path)
        == expected,
    )


check(
    "9.1 production not already installed",
    not P91.exists(),
)

check(
    "9.1 freeze not already installed",
    not F91.exists(),
)


# Preserve existing Coordination files before installation.

coord_root = (
    ROOT
    / "backend/server/coordination"
)

coord_before = {}

for path in coord_root.rglob("*"):

    if (
        path.is_file()
        and RECOVERY_ROOT
        not in path.parents
    ):
        coord_before[
            path.resolve()
        ] = sha256(
            path
        )


# ==================================================================
# 1 — BACKUP
# ==================================================================

section(
    "1 — PRE-INSTALL BACKUP"
)


stamp = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

backup = (
    ROOT
    / "backend/server/data/runtime_backups"
    / f"ucf_phase9_1_{stamp}"
)

backup.mkdir(
    parents=True,
    exist_ok=False,
)


print(
    "BACKUP:",
    backup,
)


created = [
    P91,
    F91,
    REPORT,
]

init_created = False

if not INIT.exists():
    INIT.write_text(
        "",
        encoding="utf-8",
    )
    init_created = True


try:

    # ==============================================================
    # 2 — INSTALL 9.1
    # ==============================================================

    section(
        "2 — INSTALL PHASE 9.1 FAILURE POLICY"
    )


    P91.write_text(
r'''"""
LinkCraftor — Universal Coordination Framework

Phase 9.1 — Failure Policy

Deterministic workflow-level policy classification for one terminal
failed ProcessedStageResult.

Canonical input authority:
- Phase 6.1 ProcessedStageResult.

Optional supporting Runtime reliability authorities:
- Runtime Failure Classification & Containment,
- Runtime Retry Governance,
- Runtime Recovery Coordination.

This component decides only the workflow-level policy posture:

- RECOVER
- COMPENSATE
- MANUAL_INTERVENTION
- FAIL_WORKFLOW

This component does NOT:
- retry or requeue Runtime jobs,
- execute Runtime recovery,
- mutate Runtime jobs, queues, workers or executions,
- mutate workflow lifecycle state,
- persist workflow recovery state,
- perform compensation,
- perform manual intervention,
- enforce recovery-attempt ceilings.

Those mechanics belong to their owning later phases/components.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple

from backend.server.coordination.stage_handoff.stage_result_processor import (
    ProcessedStageResult,
    StageResultDisposition,
)

from backend.server.runtime.reliability.failure_classification_containment import (
    ContainmentAction,
    FailureContainmentDecision,
    FailureContainmentDisposition,
    FailureRetryability,
    RuntimeFailureDomain,
    RuntimeFailureSeverity,
)

from backend.server.runtime.reliability.retry_governance import (
    RetryGovernanceDecision,
    RetryGovernanceDisposition,
)

from backend.server.runtime.reliability.recovery_coordination import (
    RecoveryCoordinationDecision,
    RecoveryRoute,
)


FAILURE_POLICY_VERSION = "failure_policy_v9.1.0"
FAILURE_POLICY_SCHEMA_VERSION = "failure_policy_schema_v1"


class FailurePolicyError(ValueError):
    pass


class WorkflowFailurePolicyOutcome(
    str,
    Enum,
):
    RECOVER = "RECOVER"
    COMPENSATE = "COMPENSATE"
    MANUAL_INTERVENTION = "MANUAL_INTERVENTION"
    FAIL_WORKFLOW = "FAIL_WORKFLOW"


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowFailurePolicyDecision:

    outcome: WorkflowFailurePolicyOutcome

    reason_codes: Tuple[
        str,
        ...
    ]

    source_result_id: str
    workflow_id: str
    correlation_id: str
    stage_id: str
    job_id: str

    failure_code: str

    runtime_failure_domain: Optional[str]
    runtime_failure_severity: Optional[str]
    runtime_retry_disposition: Optional[str]
    runtime_recovery_primary_route: Optional[str]

    compensation_required: bool
    manual_intervention_required: bool

    source_processor_version: str

    policy_version: str = FAILURE_POLICY_VERSION
    schema_version: str = FAILURE_POLICY_SCHEMA_VERSION

    def to_dict(
        self,
    ) -> Mapping[
        str,
        Any,
    ]:

        return MappingProxyType({
            "outcome":
                self.outcome.value,

            "reason_codes":
                self.reason_codes,

            "source_result_id":
                self.source_result_id,

            "workflow_id":
                self.workflow_id,

            "correlation_id":
                self.correlation_id,

            "stage_id":
                self.stage_id,

            "job_id":
                self.job_id,

            "failure_code":
                self.failure_code,

            "runtime_failure_domain":
                self.runtime_failure_domain,

            "runtime_failure_severity":
                self.runtime_failure_severity,

            "runtime_retry_disposition":
                self.runtime_retry_disposition,

            "runtime_recovery_primary_route":
                self.runtime_recovery_primary_route,

            "compensation_required":
                self.compensation_required,

            "manual_intervention_required":
                self.manual_intervention_required,

            "source_processor_version":
                self.source_processor_version,

            "policy_version":
                self.policy_version,

            "schema_version":
                self.schema_version,
        })


def _flag(
    source: ProcessedStageResult,
    name: str,
) -> bool:

    values = (
        source.failure_details,
        source.metadata,
    )

    for mapping in values:

        value = mapping.get(
            name
        )

        if value is True:
            return True

    return False


def _validate_source(
    source: ProcessedStageResult,
) -> None:

    if not isinstance(
        source,
        ProcessedStageResult,
    ):
        raise FailurePolicyError(
            "source must be ProcessedStageResult"
        )

    if not source.terminal:
        raise FailurePolicyError(
            "source must be terminal"
        )

    if (
        source.disposition
        is not StageResultDisposition.FAILED
    ):
        raise FailurePolicyError(
            "Phase 9.1 requires FAILED ProcessedStageResult"
        )

    if source.normal_handoff_allowed:
        raise FailurePolicyError(
            "FAILED source cannot allow normal handoff"
        )

    if source.prerequisite_satisfied:
        raise FailurePolicyError(
            "FAILED source cannot satisfy prerequisite"
        )


def evaluate_failure_policy(
    source: ProcessedStageResult,
    *,
    containment_decision: Optional[
        FailureContainmentDecision
    ] = None,
    retry_decision: Optional[
        RetryGovernanceDecision
    ] = None,
    recovery_decision: Optional[
        RecoveryCoordinationDecision
    ] = None,
) -> WorkflowFailurePolicyDecision:

    _validate_source(
        source
    )

    if (
        containment_decision is not None
        and not isinstance(
            containment_decision,
            FailureContainmentDecision,
        )
    ):
        raise FailurePolicyError(
            "containment_decision must be FailureContainmentDecision or None"
        )

    if (
        retry_decision is not None
        and not isinstance(
            retry_decision,
            RetryGovernanceDecision,
        )
    ):
        raise FailurePolicyError(
            "retry_decision must be RetryGovernanceDecision or None"
        )

    if (
        recovery_decision is not None
        and not isinstance(
            recovery_decision,
            RecoveryCoordinationDecision,
        )
    ):
        raise FailurePolicyError(
            "recovery_decision must be RecoveryCoordinationDecision or None"
        )

    reasons = []

    compensation_required = (
        _flag(
            source,
            "compensation_required",
        )
    )

    manual_intervention_required = (
        _flag(
            source,
            "manual_intervention_required",
        )
    )

    # --------------------------------------------------------------
    # Highest priority: explicit Coordination safety requirements.
    # --------------------------------------------------------------

    if compensation_required:
        reasons.append(
            "explicit_compensation_required"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.COMPENSATE
        )

    elif manual_intervention_required:
        reasons.append(
            "explicit_manual_intervention_required"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.MANUAL_INTERVENTION
        )

    # --------------------------------------------------------------
    # Runtime containment evidence can force human intervention.
    # --------------------------------------------------------------

    elif (
        containment_decision is not None
        and (
            containment_decision.severity
            is RuntimeFailureSeverity.CRITICAL

            or containment_decision.domain
            in (
                RuntimeFailureDomain.SECURITY,
                RuntimeFailureDomain.AUTHENTICATION,
                RuntimeFailureDomain.AUTHORIZATION,
                RuntimeFailureDomain.PERSISTENCE,
            )

            or containment_decision.disposition
            is FailureContainmentDisposition.ESCALATE

            or containment_decision.containment_action
            is ContainmentAction.ESCALATE
        )
    ):
        reasons.append(
            "runtime_failure_requires_escalation"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.MANUAL_INTERVENTION
        )

    # --------------------------------------------------------------
    # Runtime recovery route can support UCF workflow recovery.
    # UCF does not execute the route.
    # --------------------------------------------------------------

    elif (
        recovery_decision is not None
        and recovery_decision.primary_route
        in (
            RecoveryRoute.WORKER_RECOVERY,
            RecoveryRoute.QUEUE_RECOVERY,
            RecoveryRoute.EXECUTION_RECOVERY,
            RecoveryRoute.ORCHESTRATION_RECOVERY,
            RecoveryRoute.CRASH_RESTART_RECOVERY,
        )
    ):
        reasons.append(
            "runtime_recovery_route_available"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.RECOVER
        )

    elif (
        recovery_decision is not None
        and recovery_decision.primary_route
        in (
            RecoveryRoute.DEGRADED_MODE,
            RecoveryRoute.ESCALATION,
        )
    ):
        reasons.append(
            "runtime_recovery_requires_escalation"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.MANUAL_INTERVENTION
        )

    # --------------------------------------------------------------
    # Runtime retry governance is authoritative for Runtime retries.
    # RETRY_ALLOWED supports recovery posture but does not execute it.
    # --------------------------------------------------------------

    elif (
        retry_decision is not None
        and retry_decision.disposition
        is RetryGovernanceDisposition.RETRY_ALLOWED
    ):
        reasons.append(
            "runtime_retry_allowed"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.RECOVER
        )

    elif (
        retry_decision is not None
        and retry_decision.disposition
        in (
            RetryGovernanceDisposition.RETRY_DENIED,
            RetryGovernanceDisposition.RETRY_EXHAUSTED,
        )
    ):
        reasons.append(
            (
                "runtime_retry_denied"
                if retry_decision.disposition
                is RetryGovernanceDisposition.RETRY_DENIED
                else "runtime_retry_exhausted"
            )
        )

        outcome = (
            WorkflowFailurePolicyOutcome.FAIL_WORKFLOW
        )

    # --------------------------------------------------------------
    # Terminal Phase-5.5 failure evidence may directly prove retry
    # exhaustion even when no Runtime RetryGovernanceDecision object
    # is supplied to UCF.
    # --------------------------------------------------------------

    elif (
        source.failure_details.get(
            "runtime_retry_exhausted"
        )
        is True
    ):
        reasons.append(
            "terminal_runtime_retry_exhausted"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.FAIL_WORKFLOW
        )

    # --------------------------------------------------------------
    # Non-retryable Runtime classification also closes automatic
    # recovery unless stronger explicit evidence above supersedes it.
    # --------------------------------------------------------------

    elif (
        containment_decision is not None
        and containment_decision.retryability
        is FailureRetryability.NON_RETRYABLE
    ):
        reasons.append(
            "runtime_failure_non_retryable"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.FAIL_WORKFLOW
        )

    # --------------------------------------------------------------
    # Unknown or absent policy evidence fails closed to workflow
    # failure rather than inventing automatic recovery.
    # --------------------------------------------------------------

    else:
        reasons.append(
            "no_authorized_recovery_evidence"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.FAIL_WORKFLOW
        )

    return WorkflowFailurePolicyDecision(
        outcome=
            outcome,

        reason_codes=
            tuple(
                reasons
            ),

        source_result_id=
            source.result_id,

        workflow_id=
            source.workflow_id,

        correlation_id=
            source.correlation_id,

        stage_id=
            source.stage_id,

        job_id=
            source.job_id,

        failure_code=
            source.failure_code,

        runtime_failure_domain=
            (
                containment_decision.domain.value
                if containment_decision
                is not None
                else None
            ),

        runtime_failure_severity=
            (
                containment_decision.severity.value
                if containment_decision
                is not None
                else None
            ),

        runtime_retry_disposition=
            (
                retry_decision.disposition.value
                if retry_decision
                is not None
                else None
            ),

        runtime_recovery_primary_route=
            (
                recovery_decision.primary_route.value
                if recovery_decision
                is not None
                else None
            ),

        compensation_required=
            compensation_required,

        manual_intervention_required=
            manual_intervention_required,

        source_processor_version=
            source.processor_version,
    )


__all__ = [
    "FAILURE_POLICY_VERSION",
    "FAILURE_POLICY_SCHEMA_VERSION",
    "FailurePolicyError",
    "WorkflowFailurePolicyOutcome",
    "WorkflowFailurePolicyDecision",
    "evaluate_failure_policy",
]
''',
        encoding="utf-8",
    )


    SHA91 = sha256(
        P91
    )


    print(
        "9.1 SHA256:",
        SHA91,
    )


    # ==============================================================
    # 3 — STATIC ARCHITECTURE VERIFICATION
    # ==============================================================

    section(
        "3 — STATIC ARCHITECTURE VERIFICATION"
    )


    source = P91.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source
    )


    forbidden_symbols = (
        "submit_universal_job",
        "enqueue",
        "requeue",
        "claim_job",
        "run_one_universal_runtime_job_v1",
        "save_workflow",
        "pause_workflow",
        "resume_workflow",
        "prepare_restart_recovery",
    )


    executable_names = set()

    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.Call,
        ):

            if isinstance(
                node.func,
                ast.Name,
            ):
                executable_names.add(
                    node.func.id
                )

            elif isinstance(
                node.func,
                ast.Attribute,
            ):
                executable_names.add(
                    node.func.attr
                )


    for name in forbidden_symbols:

        check(
            f"9.1 executable mutation authority absent: {name}",
            name
            not in executable_names,
        )


    check(
        "9.1 imports ProcessedStageResult",
        "ProcessedStageResult"
        in source,
    )

    check(
        "9.1 consumes Runtime containment evidence",
        "FailureContainmentDecision"
        in source,
    )

    check(
        "9.1 consumes Runtime retry evidence",
        "RetryGovernanceDecision"
        in source,
    )

    check(
        "9.1 consumes Runtime recovery-routing evidence",
        "RecoveryCoordinationDecision"
        in source,
    )


    # ==============================================================
    # 4 — IMPORT CONTRACT
    # ==============================================================

    section(
        "4 — IMPORT / CONTRACT VERIFICATION"
    )


    purge()


    policy = importlib.import_module(
        "backend.server.coordination.coordination_recovery.failure_policy"
    )


    check(
        "9.1 version exact",
        policy.FAILURE_POLICY_VERSION
        == "failure_policy_v9.1.0",
    )

    check(
        "9.1 schema exact",
        policy.FAILURE_POLICY_SCHEMA_VERSION
        == "failure_policy_schema_v1",
    )

    check(
        "9.1 outcome vocabulary exact",
        tuple(
            item.value
            for item
            in policy.WorkflowFailurePolicyOutcome
        )
        == (
            "RECOVER",
            "COMPENSATE",
            "MANUAL_INTERVENTION",
            "FAIL_WORKFLOW",
        ),
    )


    # ==============================================================
    # 5 — FUNCTIONAL POLICY TESTS
    # ==============================================================

    section(
        "5 — FUNCTIONAL POLICY VERIFICATION"
    )


    from backend.server.coordination.stage_handoff.stage_result_processor import (
        ProcessedStageResult,
        StageResultDisposition,
    )

    from backend.server.coordination.universal_stages.contract import (
        StageExecutionTarget,
    )

    from backend.server.runtime.reliability.failure_classification_containment import (
        ContainmentAction,
        FailureContainmentDecision,
        FailureContainmentDisposition,
        FailureRetryability,
        RuntimeFailureDomain,
        RuntimeFailureScope,
        RuntimeFailureSeverity,
    )

    from backend.server.runtime.reliability.retry_governance import (
        RetryGovernanceDecision,
        RetryGovernanceDisposition,
    )

    from backend.server.runtime.reliability.recovery_coordination import (
        RecoveryCoordinationDecision,
        RecoveryRoute,
    )


    def failed_source(
        *,
        failure_details=None,
        metadata=None,
    ):

        return ProcessedStageResult(
            result_id=
                "result-91",

            workflow_id=
                "workflow-91",

            correlation_id=
                "correlation-91",

            stage_id=
                "stage-91",

            stage_version=
                "1.0.0",

            pipeline_id=
                "pipeline-91",

            workflow_type=
                "failure-policy-test",

            workspace_id=
                "workspace-91",

            execution_target=
                StageExecutionTarget.UNIVERSAL_RUNTIME,

            job_id=
                "job-91",

            job_type=
                "test-job",

            disposition=
                StageResultDisposition.FAILED,

            normal_handoff_allowed=
                False,

            prerequisite_satisfied=
                False,

            output={},

            result_reference=
                "result://91",

            artifact_references=(),

            started_at=
                "2026-11-08T00:00:00+00:00",

            finished_at=
                "2026-11-08T00:00:01+00:00",

            failure_code=
                "TEST_FAILURE",

            failure_message=
                "test terminal failure",

            failure_details=
                failure_details
                or {},

            metadata=
                metadata
                or {},

            workflow_contract_version=
                "universal_workflow_contract_v1.1.0",

            stage_reference_contract_version=
                "universal_stage_reference_v1.3.0",

            source_result_contract_version=
                "universal_stage_result_v1.4.0",
        )


    # RECOVER from Runtime recovery route.
    recover_decision = (
        RecoveryCoordinationDecision(
            primary_route=
                RecoveryRoute.EXECUTION_RECOVERY,

            secondary_routes=(),

            reason_codes=(
                "execution_recovery",
            ),

            source_reference=
                "runtime-91",
        )
    )


    recovered = policy.evaluate_failure_policy(
        failed_source(),
        recovery_decision=
            recover_decision,
    )


    check(
        "9.1 RECOVER from authorized Runtime recovery route",
        recovered.outcome
        is policy.WorkflowFailurePolicyOutcome.RECOVER,
    )


    # COMPENSATE only from explicit Coordination evidence.
    compensated = policy.evaluate_failure_policy(
        failed_source(
            failure_details={
                "compensation_required":
                    True,
            }
        )
    )


    check(
        "9.1 COMPENSATE from explicit requirement",
        compensated.outcome
        is policy.WorkflowFailurePolicyOutcome.COMPENSATE,
    )


    # MANUAL_INTERVENTION from critical Runtime evidence.
    critical = FailureContainmentDecision(
        disposition=
            FailureContainmentDisposition.ESCALATE,

        domain=
            RuntimeFailureDomain.SECURITY,

        severity=
            RuntimeFailureSeverity.CRITICAL,

        scope=
            RuntimeFailureScope.WORKSPACE,

        retryability=
            FailureRetryability.NON_RETRYABLE,

        containment_action=
            ContainmentAction.ESCALATE,

        reason_codes=(
            "critical-security",
        ),

        source_reference=
            "runtime-critical-91",
    )


    manual = policy.evaluate_failure_policy(
        failed_source(),
        containment_decision=
            critical,
    )


    check(
        "9.1 MANUAL_INTERVENTION from critical escalation",
        manual.outcome
        is policy.WorkflowFailurePolicyOutcome.MANUAL_INTERVENTION,
    )


    # FAIL_WORKFLOW from retry exhaustion.
    exhausted = RetryGovernanceDecision(
        disposition=
            RetryGovernanceDisposition.RETRY_EXHAUSTED,

        next_attempt=
            None,

        delay_seconds=
            None,

        reason_codes=(
            "attempt_limit",
        ),

        source_reference=
            "runtime-retry-91",
    )


    failed = policy.evaluate_failure_policy(
        failed_source(),
        retry_decision=
            exhausted,
    )


    check(
        "9.1 FAIL_WORKFLOW from Runtime retry exhaustion",
        failed.outcome
        is policy.WorkflowFailurePolicyOutcome.FAIL_WORKFLOW,
    )


    # Terminal failure intake evidence alone may prove exhaustion.
    failed_from_terminal = (
        policy.evaluate_failure_policy(
            failed_source(
                failure_details={
                    "runtime_retry_exhausted":
                        True,
                }
            )
        )
    )


    check(
        "9.1 FAIL_WORKFLOW from terminal failure exhaustion evidence",
        failed_from_terminal.outcome
        is policy.WorkflowFailurePolicyOutcome.FAIL_WORKFLOW,
    )


    # Fail closed when no recovery evidence exists.
    fail_closed = policy.evaluate_failure_policy(
        failed_source()
    )


    check(
        "9.1 fails closed without authorized recovery evidence",
        fail_closed.outcome
        is policy.WorkflowFailurePolicyOutcome.FAIL_WORKFLOW,
    )


    check(
        "9.1 preserves workflow identity",
        fail_closed.workflow_id
        == "workflow-91"
        and fail_closed.correlation_id
        == "correlation-91"
        and fail_closed.stage_id
        == "stage-91"
        and fail_closed.job_id
        == "job-91",
    )


    # ==============================================================
    # 6 — CERTIFICATION REPORT
    # ==============================================================

    section(
        "6 — PHASE 9.1 CERTIFICATION REPORT"
    )


    passed = sum(
        1
        for _name, ok
        in checks
        if ok
    )


    REPORT.write_text(
        "\n".join(
            (
                "LINKCRAFTOR",
                "UNIVERSAL COORDINATION FRAMEWORK",
                "PHASE 9.1 — FAILURE POLICY FINAL CERTIFICATION",
                "",
                "Workflow-level outcomes:",
                "- RECOVER",
                "- COMPENSATE",
                "- MANUAL_INTERVENTION",
                "- FAIL_WORKFLOW",
                "",
                "Authority boundary:",
                "- consumes terminal ProcessedStageResult",
                "- may consume Runtime containment/retry/recovery decisions",
                "- does not execute Runtime recovery",
                "- does not retry/requeue Runtime work",
                "- does not mutate workflow lifecycle",
                "- does not persist recovery",
                "- does not perform compensation",
                "- does not perform manual intervention",
                "",
                f"Production SHA256: {SHA91}",
                f"Formal checks passed: {passed}",
                "Formal checks failed: 0",
                "",
                "STATUS: CERTIFIED + FROZEN",
            )
        )
        + "\n",
        encoding="utf-8",
    )


    REPORT_SHA = sha256(
        REPORT
    )


    # ==============================================================
    # 7 — FREEZE
    # ==============================================================

    section(
        "7 — PHASE 9.1 FREEZE"
    )


    write_json(
        F91,
        {
            "framework":
                "Universal Coordination Framework",

            "phase":
                "9.1",

            "component":
                "Failure Policy",

            "certified":
                True,

            "frozen":
                True,

            "production": {
                "path":
                    "backend/server/coordination/"
                    "coordination_recovery/failure_policy.py",

                "version":
                    "failure_policy_v9.1.0",

                "schema_version":
                    "failure_policy_schema_v1",

                "sha256":
                    SHA91,
            },

            "workflow_outcomes": [
                "RECOVER",
                "COMPENSATE",
                "MANUAL_INTERVENTION",
                "FAIL_WORKFLOW",
            ],

            "input_authorities": {
                "processed_stage_result_sha256":
                    sha256(
                        PROCESSED_RESULT
                    ),

                "runtime_failure_classification_sha256":
                    sha256(
                        RUNTIME_FAILURE_CLASSIFICATION
                    ),

                "runtime_retry_governance_sha256":
                    sha256(
                        RUNTIME_RETRY_GOVERNANCE
                    ),

                "runtime_recovery_coordination_sha256":
                    sha256(
                        RUNTIME_RECOVERY_COORDINATION
                    ),
            },

            "certified_boundaries": [
                "no Runtime retry execution",
                "no Runtime requeue",
                "no Runtime recovery execution",
                "no Runtime mutation",
                "no workflow lifecycle mutation",
                "no recovery persistence",
                "no compensation execution",
                "no manual-intervention execution",
                "no recovery-loop enforcement",
            ],

            "final_certification_report": {
                "path":
                    REPORT.name,

                "sha256":
                    REPORT_SHA,
            },

            "formal_checks_passed":
                passed,

            "freeze_created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "next":
                "9.2 Terminal Runtime Failure Handling",
        },
    )


    F91_SHA = sha256(
        F91
    )


    # ==============================================================
    # 8 — POST-FREEZE IMMUTABILITY
    # ==============================================================

    section(
        "8 — POST-FREEZE IMMUTABILITY"
    )


    for path, expected in EXPECTED.items():

        check(
            f"upstream authority unchanged: {path.name}",
            sha256(path)
            == expected,
        )


    coord_after = {}

    for path in coord_root.rglob("*"):

        if (
            path.is_file()
            and RECOVERY_ROOT
            not in path.parents
        ):
            coord_after[
                path.resolve()
            ] = sha256(
                path
            )


    check(
        "existing Coordination inventory unchanged",
        set(
            coord_after
        )
        == set(
            coord_before
        ),
    )


    check(
        "existing Coordination hashes unchanged",
        coord_after
        == coord_before,
    )


    purge()


    final_policy = importlib.import_module(
        "backend.server.coordination.coordination_recovery.failure_policy"
    )


    check(
        "final 9.1 import succeeds",
        final_policy.FAILURE_POLICY_VERSION
        == "failure_policy_v9.1.0",
    )


    # ==============================================================
    # 9 — FINAL STATUS
    # ==============================================================

    section(
        "9 — PHASE 9.1 FINAL STATUS"
    )


    total = sum(
        1
        for _name, ok
        in checks
        if ok
    )


    print(
        "TOTAL FORMAL CHECKS:",
        total,
        "PASS",
    )

    print(
        "PHASE 9.1 FAILURE POLICY: CERTIFIED + FROZEN"
    )

    print(
        "9.1 SOURCE SHA256:",
        SHA91,
    )

    print(
        "9.1 FREEZE SHA256:",
        F91_SHA,
    )

    print(
        "9.1 REPORT SHA256:",
        REPORT_SHA,
    )

    print()

    print(
        "PHASE 8 MODIFIED: FALSE"
    )

    print(
        "EXISTING COORDINATION COMPONENTS MODIFIED: FALSE"
    )

    print(
        "UNIVERSAL RUNTIME MODIFIED: FALSE"
    )

    print()

    print(
        "NEXT: PHASE 9.2 — TERMINAL RUNTIME FAILURE HANDLING"
    )

    print("=" * 120)


except Exception:

    print()
    print("=" * 120)
    print("PHASE 9.1 FAILED — ROLLING BACK NEW FILES")
    print("=" * 120)

    for path in created:

        if path.exists():
            path.unlink()

    if (
        init_created
        and INIT.exists()
    ):
        INIT.unlink()

    try:
        if (
            RECOVERY_ROOT.exists()
            and not any(
                RECOVERY_ROOT.iterdir()
            )
        ):
            RECOVERY_ROOT.rmdir()
    except Exception:
        pass

    print(
        "ROLLBACK COMPLETE."
    )

    raise
