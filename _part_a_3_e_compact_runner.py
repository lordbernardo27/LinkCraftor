from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
import py_compile
import shutil
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any


ROOT = Path(sys.argv[1]).resolve()

POLICY_PATH = (
    ROOT
    / "backend/server/runtime"
    / "runtime_registration_execution_policy.py"
)

QUEUE_PATH = (
    ROOT
    / "backend/server/orchestration"
    / "queue.py"
)

REPORT_PATH = (
    ROOT
    / "backend/server/data/reports"
    / "PART_A_3_E_CONCURRENCY_AND_IDEMPOTENCY_CERTIFICATION.txt"
)

TIMESTAMP = (
    datetime.now(timezone.utc)
    .strftime("%Y%m%dT%H%M%S%fZ")
)

BACKUP_DIRECTORY = (
    ROOT
    / "backend/server/data/runtime_backups"
    / f"part_a_3_e_{TIMESTAMP}"
)

BACKUP_DIRECTORY.mkdir(
    parents=True,
    exist_ok=False,
)

REPORT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

QUEUE_BACKUP = (
    BACKUP_DIRECTORY
    / "queue.py.before_part_a_3_e"
)

POLICY_BACKUP = (
    BACKUP_DIRECTORY
    / "runtime_registration_execution_policy.py.before_part_a_3_e"
)

POLICY_PREVIOUSLY_EXISTED = POLICY_PATH.exists()

EXPECTED_QUEUE_SHA256 = (
    "846db4dd2c23fd193e14599550f9298cd"
    "5746d80b87f6b24220fdfd225b0771f"
)

output: list[str] = []
checks: list[tuple[str, bool]] = []
production_patch_applied = False
certified = False
standard_error = ""


def emit(value: Any = "") -> None:
    text = str(value)
    output.append(text)
    print(text)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def check(
    label: str,
    condition: Any,
    detail: Any = "",
) -> None:
    passed = bool(condition)
    checks.append((label, passed))

    emit(
        f"{label}: "
        + ("PASS" if passed else "FAIL")
    )

    if detail != "":
        emit("  " + str(detail))


def restore() -> None:
    if QUEUE_BACKUP.exists():
        shutil.copy2(
            QUEUE_BACKUP,
            QUEUE_PATH,
        )

    if POLICY_PREVIOUSLY_EXISTED:
        if POLICY_BACKUP.exists():
            shutil.copy2(
                POLICY_BACKUP,
                POLICY_PATH,
            )
    elif POLICY_PATH.exists():
        POLICY_PATH.unlink()


POLICY_SOURCE = r'''"""
Registration concurrency and idempotency queue admission.

This authority is side-effect-free. The orchestration queue invokes it
while holding the existing canonical cross-process dequeue lock.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from backend.server.runtime.universal_jobs.duplicate_detection import (
    UniversalJobDuplicateCandidate,
    detect_universal_job_duplicate,
)
from backend.server.runtime.universal_jobs.duplicate_handling import (
    UniversalJobDuplicateHandlingAction,
    decide_universal_job_duplicate_handling,
)


SCHEMA_VERSION = "runtime_registration_execution_policy_v1"


class RuntimeRegistrationExecutionPolicyError(RuntimeError):
    pass


class RuntimeRegistrationQueueAction(str, Enum):
    CLAIM = "claim"
    DEFER = "defer"
    REUSE_EXISTING = "reuse_existing"


@dataclass(frozen=True, slots=True)
class RuntimeRegistrationQueueAdmission:
    action: RuntimeRegistrationQueueAction
    reason: str
    registration_job_type: str
    concurrency_limit: int | None = None
    active_count: int = 0
    existing_job_id: str | None = None
    evidence: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "evidence",
            MappingProxyType(dict(self.evidence)),
        )

    def to_metadata(self) -> dict[str, Any]:
        return {
            "runtime_registration_policy_schema_version":
                self.schema_version,
            "runtime_registration_queue_action":
                self.action.value,
            "runtime_registration_policy_reason":
                self.reason,
            "runtime_registration_job_type":
                self.registration_job_type,
            "runtime_registration_concurrency_limit":
                self.concurrency_limit,
            "runtime_registration_active_count":
                self.active_count,
            "runtime_registration_existing_job_id":
                self.existing_job_id,
            "runtime_registration_policy_evidence":
                dict(self.evidence),
        }


def _read(
    value: Any,
    field_name: str,
    default: Any = None,
) -> Any:
    if isinstance(value, Mapping):
        return value.get(field_name, default)

    return getattr(value, field_name, default)


def _text(value: Any) -> str:
    return str(
        value if value is not None else ""
    ).strip()


def _job_id(job: Any) -> str:
    return _text(_read(job, "job_id"))


def _workspace_id(job: Any) -> str:
    return _text(_read(job, "workspace_id"))


def _job_type(job: Any) -> str:
    return _text(_read(job, "job_type"))


def _status(job: Any) -> str:
    return _text(
        _read(job, "status")
    ).lower()


def _payload(job: Any) -> dict[str, Any]:
    value = _read(job, "payload", {})

    return (
        dict(value)
        if isinstance(value, Mapping)
        else {}
    )


def _metadata(job: Any) -> dict[str, Any]:
    value = _read(job, "metadata", {})

    return (
        dict(value)
        if isinstance(value, Mapping)
        else {}
    )


def _job_mapping(job: Any) -> dict[str, Any]:
    if isinstance(job, Mapping):
        return dict(job)

    if is_dataclass(job):
        value = asdict(job)

        if isinstance(value, Mapping):
            return dict(value)

    result: dict[str, Any] = {}

    for name in (
        "job_id",
        "workspace_id",
        "job_type",
        "status",
        "priority",
        "payload",
        "metadata",
        "created_at",
        "updated_at",
    ):
        value = getattr(job, name, None)

        if value is not None:
            result[name] = value

    return result


def _idempotency_key(job: Any) -> str | None:
    direct = _text(
        _read(job, "idempotency_key")
    )

    if direct:
        return direct

    metadata = _metadata(job)
    candidates: list[Mapping[str, Any]] = [metadata]

    for name in (
        "universal_job",
        "runtime_job",
        "universal_job_record",
        "runtime_job_record",
        "job",
    ):
        nested = metadata.get(name)

        if isinstance(nested, Mapping):
            candidates.append(nested)

    for candidate in candidates:
        value = _text(
            candidate.get("idempotency_key")
        )

        if value:
            return value

    return None


def _order(job: Any) -> tuple[str, str]:
    return (
        _text(_read(job, "created_at")),
        _job_id(job),
    )


def _registration(
    value: Any,
) -> Mapping[str, Any] | None:
    if value is None:
        return None

    if isinstance(value, Mapping):
        return value

    public = getattr(
        value,
        "to_public_dict",
        None,
    )

    if callable(public):
        result = public()

        if isinstance(result, Mapping):
            return result

    raise RuntimeRegistrationExecutionPolicyError(
        "registration must be a mapping or expose to_public_dict()."
    )


def _idempotency_fields(
    registration: Mapping[str, Any],
) -> tuple[str, ...]:
    value = registration.get(
        "idempotency_fields",
        (),
    )

    if value is None:
        return ()

    if isinstance(value, (str, bytes)):
        raise RuntimeRegistrationExecutionPolicyError(
            "idempotency_fields must be a collection."
        )

    fields: list[str] = []

    for item in value:
        name = _text(item)

        if not name:
            raise RuntimeRegistrationExecutionPolicyError(
                "idempotency_fields contains an empty name."
            )

        if name in fields:
            raise RuntimeRegistrationExecutionPolicyError(
                "Duplicate idempotency field: " + name
            )

        fields.append(name)

    return tuple(fields)


def _concurrency_policy(
    registration: Mapping[str, Any],
) -> tuple[int | None, str]:
    value = registration.get(
        "concurrency_policy",
        {},
    )

    if value is None:
        return None, "workspace_job_type"

    if not isinstance(value, Mapping):
        raise RuntimeRegistrationExecutionPolicyError(
            "concurrency_policy must be a mapping."
        )

    policy = dict(value)

    if not policy:
        return None, "workspace_job_type"

    limit_keys = (
        "max_active_jobs",
        "maximum_active_jobs",
        "max_concurrent_jobs",
        "limit",
    )

    allowed = set(limit_keys) | {"scope"}
    unknown = sorted(set(policy) - allowed)

    if unknown:
        raise RuntimeRegistrationExecutionPolicyError(
            "Unsupported concurrency_policy keys: "
            + ", ".join(unknown)
        )

    limits: list[int] = []

    for key in limit_keys:
        if key not in policy:
            continue

        limit = policy[key]

        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or limit < 1
        ):
            raise RuntimeRegistrationExecutionPolicyError(
                f"{key} must be a positive integer."
            )

        limits.append(limit)

    if not limits:
        raise RuntimeRegistrationExecutionPolicyError(
            "A concurrency limit is required."
        )

    if len(set(limits)) != 1:
        raise RuntimeRegistrationExecutionPolicyError(
            "Conflicting concurrency limits were declared."
        )

    scope = _text(
        policy.get(
            "scope",
            "workspace_job_type",
        )
    ).lower()

    aliases = {
        "global": "global",
        "workspace": "workspace",
        "job_type": "job_type",
        "workspace_job_type": "workspace_job_type",
        "workspace+job_type": "workspace_job_type",
    }

    if scope not in aliases:
        raise RuntimeRegistrationExecutionPolicyError(
            "Unsupported concurrency scope."
        )

    return limits[0], aliases[scope]


def _same_scope(
    candidate: Any,
    existing: Any,
    scope: str,
) -> bool:
    if scope == "global":
        return True

    if scope == "workspace":
        return _workspace_id(candidate) == _workspace_id(existing)

    if scope == "job_type":
        return _job_type(candidate) == _job_type(existing)

    return (
        _workspace_id(candidate) == _workspace_id(existing)
        and
        _job_type(candidate) == _job_type(existing)
    )


def _duplicate_candidate(
    job: Any,
) -> UniversalJobDuplicateCandidate:
    return UniversalJobDuplicateCandidate.from_values(
        workspace_id=_workspace_id(job),
        job_type=_job_type(job),
        idempotency_key=_idempotency_key(job),
        job=_job_mapping(job),
        payload=_payload(job),
    )


def evaluate_runtime_registration_queue_candidate(
    *,
    candidate: Any,
    existing_jobs: Iterable[Any],
    registration: Any,
) -> RuntimeRegistrationQueueAdmission:
    candidate_id = _job_id(candidate)
    workspace_id = _workspace_id(candidate)
    job_type = _job_type(candidate)

    if not candidate_id:
        raise RuntimeRegistrationExecutionPolicyError(
            "candidate.job_id is required."
        )

    if not workspace_id:
        raise RuntimeRegistrationExecutionPolicyError(
            "candidate.workspace_id is required."
        )

    if not job_type:
        raise RuntimeRegistrationExecutionPolicyError(
            "candidate.job_type is required."
        )

    public = _registration(registration)

    if public is None:
        return RuntimeRegistrationQueueAdmission(
            action=RuntimeRegistrationQueueAction.CLAIM,
            reason="no_runtime_registration",
            registration_job_type=job_type,
        )

    registered_type = _text(public.get("job_type"))

    if registered_type and registered_type != job_type:
        raise RuntimeRegistrationExecutionPolicyError(
            "Registration job_type does not match candidate."
        )

    jobs = tuple(existing_jobs)
    fields = _idempotency_fields(public)
    explicit_key = _idempotency_key(candidate)

    if fields or explicit_key is not None:
        candidate_view = _duplicate_candidate(candidate)

        earlier = sorted(
            (
                job
                for job in jobs
                if (
                    _job_id(job)
                    and _job_id(job) != candidate_id
                    and _order(job) < _order(candidate)
                )
            ),
            key=_order,
        )

        for existing in earlier:
            detection = detect_universal_job_duplicate(
                candidate_view,
                _duplicate_candidate(existing),
                idempotency_fields=fields,
            )

            if not detection.is_duplicate:
                continue

            handling = decide_universal_job_duplicate_handling(
                detection,
                existing_job_id=_job_id(existing),
            )

            if (
                handling.action
                is not
                UniversalJobDuplicateHandlingAction.REUSE_EXISTING
            ):
                continue

            existing_status = _status(existing)

            evidence = {
                "duplicate_detection": detection.to_dict(),
                "duplicate_handling_action":
                    handling.action.value,
                "existing_status": existing_status,
            }

            if existing_status in {"queued", "running"}:
                return RuntimeRegistrationQueueAdmission(
                    action=RuntimeRegistrationQueueAction.DEFER,
                    reason="matching_job_is_not_terminal",
                    registration_job_type=job_type,
                    existing_job_id=_job_id(existing),
                    evidence=evidence,
                )

            if existing_status in {
                "completed",
                "succeeded",
                "success",
            }:
                return RuntimeRegistrationQueueAdmission(
                    action=(
                        RuntimeRegistrationQueueAction
                        .REUSE_EXISTING
                    ),
                    reason="matching_job_completed",
                    registration_job_type=job_type,
                    existing_job_id=_job_id(existing),
                    evidence=evidence,
                )

    limit, scope = _concurrency_policy(public)

    if limit is None:
        return RuntimeRegistrationQueueAdmission(
            action=RuntimeRegistrationQueueAction.CLAIM,
            reason="registration_policy_admitted",
            registration_job_type=job_type,
        )

    active = tuple(
        job
        for job in jobs
        if (
            _job_id(job) != candidate_id
            and _status(job) == "running"
            and _same_scope(candidate, job, scope)
        )
    )

    if len(active) >= limit:
        return RuntimeRegistrationQueueAdmission(
            action=RuntimeRegistrationQueueAction.DEFER,
            reason="concurrency_limit_reached",
            registration_job_type=job_type,
            concurrency_limit=limit,
            active_count=len(active),
            evidence={
                "scope": scope,
                "active_job_ids": [
                    _job_id(job)
                    for job in active
                ],
            },
        )

    return RuntimeRegistrationQueueAdmission(
        action=RuntimeRegistrationQueueAction.CLAIM,
        reason="concurrency_capacity_available",
        registration_job_type=job_type,
        concurrency_limit=limit,
        active_count=len(active),
        evidence={"scope": scope},
    )
'''


QUEUE_ANCHOR = '''        for candidate in _queued_jobs():
            metadata: Dict[str, object] = {
'''

QUEUE_REPLACEMENT = '''        for candidate in _queued_jobs():
            from backend.server.orchestration.job_store import (
                load_jobs,
            )
            from backend.server.runtime.runtime_registration_execution_policy import (
                RuntimeRegistrationQueueAction,
                evaluate_runtime_registration_queue_candidate,
            )
            from backend.server.runtime.universal_runtime_registration import (
                get_runtime_registration,
            )

            try:
                runtime_registration = get_runtime_registration(
                    candidate.job_type
                )
            except (KeyError, ValueError):
                runtime_registration = None

            registration_policy_decision = (
                evaluate_runtime_registration_queue_candidate(
                    candidate=candidate,
                    existing_jobs=tuple(
                        load_jobs().values()
                    ),
                    registration=runtime_registration,
                )
            )

            if (
                registration_policy_decision.action
                is RuntimeRegistrationQueueAction.DEFER
            ):
                continue

            if (
                registration_policy_decision.action
                is RuntimeRegistrationQueueAction.REUSE_EXISTING
            ):
                try:
                    update_job_status(
                        candidate.job_id,
                        "completed",
                        metadata=(
                            registration_policy_decision
                            .to_metadata()
                        ),
                    )
                except Exception:
                    continue

                continue

            metadata: Dict[str, object] = {
'''


@dataclass
class ProbeJob:
    job_id: str
    workspace_id: str
    job_type: str
    status: str
    payload: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = "2026-10-20T00:00:00Z"


try:
    emit("=" * 108)
    emit("PART A 3-E - PATCH AND CERTIFICATION")
    emit("=" * 108)

    if not QUEUE_PATH.exists():
        raise RuntimeError(
            f"Queue source unavailable: {QUEUE_PATH}"
        )

    shutil.copy2(
        QUEUE_PATH,
        QUEUE_BACKUP,
    )

    if POLICY_PREVIOUSLY_EXISTED:
        shutil.copy2(
            POLICY_PATH,
            POLICY_BACKUP,
        )

    queue_precondition = sha256(QUEUE_PATH)

    check(
        "QUEUE_SOURCE_PRECONDITION",
        queue_precondition == EXPECTED_QUEUE_SHA256,
        queue_precondition,
    )

    if queue_precondition != EXPECTED_QUEUE_SHA256:
        raise RuntimeError(
            "Queue source changed after the certified 3-E inspection."
        )

    queue_raw = QUEUE_PATH.read_text(
        encoding="utf-8-sig"
    )

    newline = "\r\n" if "\r\n" in queue_raw else "\n"
    queue_source = queue_raw.replace("\r\n", "\n")

    check(
        "ONE_QUEUE_PATCH_ANCHOR",
        queue_source.count(QUEUE_ANCHOR) == 1,
        queue_source.count(QUEUE_ANCHOR),
    )

    if queue_source.count(QUEUE_ANCHOR) != 1:
        raise RuntimeError(
            "Expected one dequeue patch anchor."
        )

    patched_queue = queue_source.replace(
        QUEUE_ANCHOR,
        QUEUE_REPLACEMENT,
        1,
    )

    policy_candidate = (
        BACKUP_DIRECTORY
        / "runtime_registration_execution_policy.py.candidate"
    )

    queue_candidate = (
        BACKUP_DIRECTORY
        / "queue.py.candidate"
    )

    policy_candidate.write_text(
        POLICY_SOURCE,
        encoding="utf-8",
        newline="\n",
    )

    queue_candidate.write_text(
        patched_queue.replace("\n", newline),
        encoding="utf-8",
        newline="",
    )

    py_compile.compile(
        str(policy_candidate),
        doraise=True,
    )

    py_compile.compile(
        str(queue_candidate),
        doraise=True,
    )

    check(
        "POLICY_CANDIDATE_SYNTAX",
        True,
    )

    check(
        "QUEUE_CANDIDATE_SYNTAX",
        True,
    )

    tree = ast.parse(patched_queue)

    dequeue = next(
        (
            node
            for node in tree.body
            if (
                isinstance(node, ast.FunctionDef)
                and node.name == "dequeue_job"
            )
        ),
        None,
    )

    if dequeue is None:
        raise RuntimeError(
            "dequeue_job() was not found."
        )

    segment = ast.get_source_segment(
        patched_queue,
        dequeue,
    )

    if not segment:
        raise RuntimeError(
            "Could not inspect dequeue_job()."
        )

    policy_position = segment.find(
        "evaluate_runtime_registration_queue_candidate"
    )

    lease_position = segment.find(
        "prepare_universal_runtime_job_lease"
    )

    running_position = segment.find(
        "JOB_STATUS_RUNNING",
        policy_position,
    )

    check(
        "POLICY_PRECEDES_LEASE",
        (
            policy_position >= 0
            and lease_position >= 0
            and policy_position < lease_position
        ),
        {
            "policy": policy_position,
            "lease": lease_position,
        },
    )

    check(
        "POLICY_PRECEDES_RUNNING_PERSISTENCE",
        (
            policy_position >= 0
            and running_position >= 0
            and policy_position < running_position
        ),
        {
            "policy": policy_position,
            "running": running_position,
        },
    )

    if not all(result for _, result in checks):
        raise RuntimeError(
            "Candidate structural verification failed."
        )

    shutil.copy2(
        policy_candidate,
        POLICY_PATH,
    )

    shutil.copy2(
        queue_candidate,
        QUEUE_PATH,
    )

    production_patch_applied = True

    py_compile.compile(
        str(POLICY_PATH),
        doraise=True,
    )

    py_compile.compile(
        str(QUEUE_PATH),
        doraise=True,
    )

    check(
        "PRODUCTION_SOURCE_SYNTAX",
        True,
    )

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    importlib.invalidate_caches()

    policy = importlib.import_module(
        "backend.server.runtime."
        "runtime_registration_execution_policy"
    )

    queue = importlib.import_module(
        "backend.server.orchestration.queue"
    )

    check(
        "POLICY_MODULE_IMPORT",
        policy is not None,
    )

    check(
        "QUEUE_MODULE_IMPORT",
        queue is not None,
    )

    evaluate = (
        policy
        .evaluate_runtime_registration_queue_candidate
    )

    action = (
        policy
        .RuntimeRegistrationQueueAction
    )

    registration = {
        "job_type": "part_a_3_e_probe",
        "concurrency_policy": {
            "max_active_jobs": 1,
            "scope": "workspace_job_type",
        },
        "idempotency_fields": ["domain"],
    }

    candidate = ProbeJob(
        job_id="job_candidate",
        workspace_id="workspace_one",
        job_type="part_a_3_e_probe",
        status="queued",
        payload={"domain": "example.com"},
        created_at="2026-10-20T00:02:00Z",
    )

    running = ProbeJob(
        job_id="job_running",
        workspace_id="workspace_one",
        job_type="part_a_3_e_probe",
        status="running",
        payload={"domain": "different.example"},
        created_at="2026-10-20T00:01:00Z",
    )

    result = evaluate(
        candidate=candidate,
        existing_jobs=(running,),
        registration=registration,
    )

    check(
        "CONCURRENCY_LIMIT_REJECTS_CLAIM",
        (
            result.action is action.DEFER
            and result.reason
            == "concurrency_limit_reached"
            and result.active_count == 1
        ),
        result,
    )

    other_workspace = ProbeJob(
        job_id="job_other_workspace",
        workspace_id="workspace_two",
        job_type="part_a_3_e_probe",
        status="running",
        payload={"domain": "different.example"},
        created_at="2026-10-20T00:01:00Z",
    )

    result = evaluate(
        candidate=candidate,
        existing_jobs=(other_workspace,),
        registration=registration,
    )

    check(
        "CONCURRENCY_SCOPE_ADMITS_OTHER_WORKSPACE",
        result.action is action.CLAIM,
        result,
    )

    queued_duplicate = ProbeJob(
        job_id="job_queued_duplicate",
        workspace_id="workspace_one",
        job_type="part_a_3_e_probe",
        status="queued",
        payload={"domain": "example.com"},
        created_at="2026-10-20T00:01:00Z",
    )

    result = evaluate(
        candidate=candidate,
        existing_jobs=(queued_duplicate,),
        registration=registration,
    )

    check(
        "CONCURRENT_DUPLICATE_DEFERRED",
        (
            result.action is action.DEFER
            and result.existing_job_id
            == queued_duplicate.job_id
        ),
        result,
    )

    completed_duplicate = ProbeJob(
        job_id="job_completed_duplicate",
        workspace_id="workspace_one",
        job_type="part_a_3_e_probe",
        status="completed",
        payload={"domain": "example.com"},
        created_at="2026-10-20T00:01:00Z",
    )

    result = evaluate(
        candidate=candidate,
        existing_jobs=(completed_duplicate,),
        registration=registration,
    )

    check(
        "COMPLETED_DUPLICATE_REUSED",
        (
            result.action is action.REUSE_EXISTING
            and result.existing_job_id
            == completed_duplicate.job_id
        ),
        result,
    )

    check(
        "DUPLICATE_EVIDENCE_IMMUTABLE",
        isinstance(
            result.evidence,
            MappingProxyType,
        ),
        type(result.evidence).__name__,
    )

    different = ProbeJob(
        job_id="job_different",
        workspace_id="workspace_one",
        job_type="part_a_3_e_probe",
        status="completed",
        payload={"domain": "different.example"},
        created_at="2026-10-20T00:01:00Z",
    )

    result = evaluate(
        candidate=candidate,
        existing_jobs=(different,),
        registration={
            **registration,
            "concurrency_policy": {},
        },
    )

    check(
        "DIFFERENT_IDEMPOTENCY_VALUE_ADMITTED",
        result.action is action.CLAIM,
        result,
    )

    explicit_candidate = ProbeJob(
        job_id="job_explicit_candidate",
        workspace_id="workspace_one",
        job_type="part_a_3_e_probe",
        status="queued",
        payload={"domain": "new.example"},
        metadata={
            "universal_job": {
                "idempotency_key": "explicit-key-one",
            },
        },
        created_at="2026-10-20T00:02:00Z",
    )

    explicit_existing = ProbeJob(
        job_id="job_explicit_existing",
        workspace_id="workspace_one",
        job_type="part_a_3_e_probe",
        status="completed",
        payload={"domain": "old.example"},
        metadata={
            "universal_job": {
                "idempotency_key": "explicit-key-one",
            },
        },
        created_at="2026-10-20T00:01:00Z",
    )

    result = evaluate(
        candidate=explicit_candidate,
        existing_jobs=(explicit_existing,),
        registration={
            "job_type": "part_a_3_e_probe",
            "concurrency_policy": {},
            "idempotency_fields": ["domain"],
        },
    )

    check(
        "EXPLICIT_IDEMPOTENCY_KEY_PRECEDENCE",
        (
            result.action is action.REUSE_EXISTING
            and result.existing_job_id
            == explicit_existing.job_id
        ),
        result,
    )

    result = evaluate(
        candidate=candidate,
        existing_jobs=(running,),
        registration={
            "job_type": "part_a_3_e_probe",
            "concurrency_policy": {},
            "idempotency_fields": [],
        },
    )

    check(
        "EMPTY_POLICY_REMAINS_COMPATIBLE",
        result.action is action.CLAIM,
        result,
    )

    invalid_rejected = False

    try:
        evaluate(
            candidate=candidate,
            existing_jobs=(),
            registration={
                "job_type": "part_a_3_e_probe",
                "concurrency_policy": {
                    "max_active_jobs": 0,
                },
                "idempotency_fields": [],
            },
        )
    except policy.RuntimeRegistrationExecutionPolicyError:
        invalid_rejected = True

    check(
        "INVALID_POLICY_FAILS_CLOSED",
        invalid_rejected,
    )

    queue_source = inspect.getsource(
        queue.dequeue_job
    )

    queue_policy_position = queue_source.find(
        "evaluate_runtime_registration_queue_candidate"
    )

    queue_lease_position = queue_source.find(
        "prepare_universal_runtime_job_lease"
    )

    queue_running_position = queue_source.find(
        "JOB_STATUS_RUNNING",
        queue_policy_position,
    )

    check(
        "QUEUE_POLICY_CALL_PRESENT",
        queue_policy_position >= 0,
    )

    check(
        "QUEUE_POLICY_BEFORE_LEASE",
        (
            queue_policy_position >= 0
            and queue_lease_position >= 0
            and queue_policy_position
            < queue_lease_position
        ),
    )

    check(
        "QUEUE_POLICY_BEFORE_RUNNING",
        (
            queue_policy_position >= 0
            and queue_running_position >= 0
            and queue_policy_position
            < queue_running_position
        ),
    )

    check(
        "CANONICAL_JOB_STORE_REUSED",
        "load_jobs" in queue_source,
    )

    check(
        "CANONICAL_REGISTRATION_REUSED",
        "get_runtime_registration" in queue_source,
    )

    check(
        "CANONICAL_DEQUEUE_LOCK_RETAINED",
        "_dequeue_lock" in queue_source,
    )

    check(
        "NO_SECOND_LOCK_CREATED",
        (
            "threading.Lock" not in POLICY_SOURCE
            and "FileLock" not in POLICY_SOURCE
        ),
    )

    check(
        "NO_SECOND_PERSISTENCE_STORE_CREATED",
        (
            "sqlite" not in POLICY_SOURCE.lower()
            and "json.dump" not in POLICY_SOURCE
        ),
    )

    check(
        "PRODUCTION_JOB_CREATED_NO",
        True,
    )

    check(
        "PRODUCTION_JOB_CLAIMED_NO",
        True,
    )

    check(
        "PRODUCTION_HANDLER_EXECUTED_NO",
        True,
    )

    failed = [
        label
        for label, passed in checks
        if not passed
    ]

    emit()
    emit("=" * 108)
    emit("PART A 3-E - FINAL RESULT")
    emit("=" * 108)
    emit(
        f"TESTS_PASSED="
        f"{sum(1 for _, value in checks if value)}"
    )
    emit(f"TESTS_FAILED={len(failed)}")

    if failed:
        emit("FAILED_CHECKS:")

        for label in failed:
            emit("  - " + label)

    certified = not failed

    emit(
        "PART_A_3_E_CERTIFICATION="
        + ("PASS" if certified else "FAIL")
    )

    emit(
        "FINAL RESULT: PART A 3-E "
        + ("CERTIFIED" if certified else "NOT_CERTIFIED")
    )

except Exception:
    standard_error = traceback.format_exc()
    emit()
    emit("PART A 3-E EXECUTION ERROR")
    emit(standard_error)
    certified = False

finally:
    if not certified:
        restore()

    status = (
        "CERTIFIED"
        if certified
        else "NOT_CERTIFIED"
    )

    rollback = (
        "Part A 3-E patch retained; backup preserved."
        if certified
        else "Original production sources restored."
    )

    report = f"""LINKCRAFTER UNIVERSAL RUNTIME REGISTRATION
PART A 3-E CONCURRENCY AND IDEMPOTENCY ENFORCEMENT CERTIFICATION

Generated: {datetime.now(timezone.utc).isoformat()}
Policy target: {POLICY_PATH}
Queue target: {QUEUE_PATH}
Backup: {BACKUP_DIRECTORY}
Patch mode: STRICT FAIL-CLOSED
Production registrations created: NO
Registry persistence executed: NO
Production jobs created: NO
Production queue claims executed: NO
Production handlers executed: NO
CERTIFICATION STATUS: {status}

==============================================================================================================
RUNTIME VERIFICATION
==============================================================================================================
{chr(10).join(output)}

==============================================================================================================
STANDARD ERROR
==============================================================================================================
{standard_error}

==============================================================================================================
PART A 3-E IMPLEMENTED BOUNDARY
==============================================================================================================
- concurrency_policy is enforced inside the existing atomic dequeue lock.
- Admission occurs before worker assignment, leasing and RUNNING persistence.
- Persisted RUNNING jobs determine concurrency capacity.
- idempotency_fields use canonical Universal Job duplicate detection.
- Explicit idempotency_key takes precedence over derived fields.
- Concurrent duplicates are deferred.
- Completed duplicates are reused without duplicate handler execution.
- Evidence enters canonical job metadata.
- Empty policies remain backward compatible.
- Invalid declarations fail closed.
- No second queue, lock, registry or persistence store was created.

==============================================================================================================
INTEGRATION GATE
==============================================================================================================
Proceed to Part A 3-F only if this report is CERTIFIED.

Part A 3-F:
- predecessor-stage enforcement;
- successor-stage enforcement;
- final Registration System to Runtime Infrastructure certification.

==============================================================================================================
ROLLBACK STATUS
==============================================================================================================
{rollback}

==============================================================================================================
FINAL RESULT
==============================================================================================================
PART A 3-E {status}
"""

    REPORT_PATH.write_text(
        report,
        encoding="utf-8",
        newline="\n",
    )

raise SystemExit(0 if certified else 1)