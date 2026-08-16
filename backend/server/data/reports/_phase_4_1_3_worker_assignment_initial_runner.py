from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

ASSIGNMENT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "assignment.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_3_worker_assignment_initial_implementation.txt"
)


# ============================================================
# PROTECTED AUTHORITIES
# ============================================================

PROTECTED = {
    "worker_registration": (
        ROOT / "backend/server/runtime/universal_worker/registration.py",
        "00F0D6E620E24A7433C880B722E023AF3C2121563F8E18DFA9979E0F06A36D64",
    ),

    "worker_discovery": (
        ROOT / "backend/server/runtime/universal_worker/discovery.py",
        "DFCAB9080982C8D5E099A40C903F7B4140B0860053DB73CB77B30B966788A228",
    ),

    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "existing_runtime_worker": (
        ROOT / "backend/server/runtime/universal_runtime_worker_v1.py",
        "6CC4EC122C6B8D1E21AFF8B55CAA786148D7E1FC75D840DAE9240FFB69634D44",
    ),

    "runtime_registration": (
        ROOT / "backend/server/runtime/universal_runtime_registration.py",
        "CBFBB0DA1E5D05A040AEC6F60B1251331431956106D90335A8C110FDBCA632E5",
    ),

    "runtime_infrastructure": (
        ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",
        "EE6590D044C6AA20762F2A37AE86B7FFD3300B62610BC2B1F2657D9334CB311C",
    ),

    "orchestration_queue": (
        ROOT / "backend/server/orchestration/queue.py",
        "76F8F7E66578E2B8A4A1FF3BB420B6340A7A1D1D661EB66B7C21987CF3845A97",
    ),

    "orchestration_service": (
        ROOT / "backend/server/orchestration/service.py",
        "4C31CFC6FFDC9AFA8EA6AD8F43ADBC117F8A6D0193ABF045DBFBA39D6EB799BA",
    ),
}


def ast_sha(
    path: Path,
) -> str:

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(source)

    canonical = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest().upper()


for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(path)

    if actual != expected:

        raise SystemExit(
            (
                "Protected authority mismatch before "
                "4.1.3 implementation: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


# ============================================================
# PRODUCTION AUTHORITY
# ============================================================

SOURCE = r'''from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from backend.server.runtime.universal_worker.registration import (
    UniversalWorkerRegistration,
)


UNIVERSAL_WORKER_ASSIGNMENT_VERSION = (
    "universal_worker_assignment_v4.1.3"
)

UNIVERSAL_WORKER_ASSIGNMENT_RESULT_SCHEMA_VERSION = (
    "universal_worker_assignment_result_schema_v1"
)

MAX_UNIVERSAL_WORKER_ASSIGNMENT_JOB_ID_LENGTH = 200


class UniversalWorkerAssignmentError(
    ValueError
):

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:

        super().__init__(message)

        self.code = str(code)
        self.value = value


class UniversalWorkerAssignmentStatus(
    str,
    Enum,
):

    ASSIGNED = "ASSIGNED"
    NO_ASSIGNMENT = "NO_ASSIGNMENT"


def normalize_universal_worker_assignment_job_id(
    value: Any,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalWorkerAssignmentError(
            "job_id must be a string.",
            code="invalid_assignment_job_id_type",
            value=value,
        )

    normalized = value.strip()

    if not normalized:

        raise UniversalWorkerAssignmentError(
            "job_id must not be empty.",
            code="empty_assignment_job_id",
            value=value,
        )

    if (
        len(normalized)
        > MAX_UNIVERSAL_WORKER_ASSIGNMENT_JOB_ID_LENGTH
    ):

        raise UniversalWorkerAssignmentError(
            (
                "job_id exceeds maximum length "
                f"{MAX_UNIVERSAL_WORKER_ASSIGNMENT_JOB_ID_LENGTH}."
            ),
            code="assignment_job_id_too_long",
            value=value,
        )

    return normalized


def _validate_worker(
    value: Any,
) -> UniversalWorkerRegistration:

    if not isinstance(
        value,
        UniversalWorkerRegistration,
    ):

        raise UniversalWorkerAssignmentError(
            (
                "Every eligible worker must be a "
                "UniversalWorkerRegistration."
            ),
            code="invalid_assignment_worker",
            value=value,
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerAssignmentResult:

    job_id: str
    status: UniversalWorkerAssignmentStatus
    worker: UniversalWorkerRegistration | None
    candidate_count: int

    schema_version: str = (
        UNIVERSAL_WORKER_ASSIGNMENT_RESULT_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "job_id",
            normalize_universal_worker_assignment_job_id(
                self.job_id
            ),
        )

        if not isinstance(
            self.status,
            UniversalWorkerAssignmentStatus,
        ):

            raise UniversalWorkerAssignmentError(
                (
                    "status must be a "
                    "UniversalWorkerAssignmentStatus."
                ),
                code="invalid_assignment_status",
                value=self.status,
            )

        if (
            type(self.candidate_count)
            is not int
            or self.candidate_count < 0
        ):

            raise UniversalWorkerAssignmentError(
                (
                    "candidate_count must be a "
                    "non-negative integer."
                ),
                code="invalid_assignment_candidate_count",
                value=self.candidate_count,
            )

        if (
            self.status
            is UniversalWorkerAssignmentStatus.ASSIGNED
        ):

            if self.worker is None:

                raise UniversalWorkerAssignmentError(
                    (
                        "ASSIGNED requires a selected "
                        "worker."
                    ),
                    code="assigned_worker_required",
                    value=self.worker,
                )

            _validate_worker(
                self.worker
            )

            if self.candidate_count < 1:

                raise UniversalWorkerAssignmentError(
                    (
                        "ASSIGNED requires candidate_count "
                        "of at least one."
                    ),
                    code="assigned_candidate_count_invalid",
                    value=self.candidate_count,
                )

        else:

            if self.worker is not None:

                raise UniversalWorkerAssignmentError(
                    (
                        "NO_ASSIGNMENT must not contain "
                        "a worker."
                    ),
                    code="no_assignment_worker_forbidden",
                    value=self.worker,
                )

            if self.candidate_count != 0:

                raise UniversalWorkerAssignmentError(
                    (
                        "NO_ASSIGNMENT requires "
                        "candidate_count=0."
                    ),
                    code=(
                        "no_assignment_candidate_count_"
                        "must_be_zero"
                    ),
                    value=self.candidate_count,
                )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_ASSIGNMENT_RESULT_SCHEMA_VERSION
        ):

            raise UniversalWorkerAssignmentError(
                (
                    "Invalid Worker Assignment "
                    "result schema_version."
                ),
                code=(
                    "invalid_worker_assignment_"
                    "result_schema_version"
                ),
                value=self.schema_version,
            )

    @property
    def assigned(
        self,
    ) -> bool:

        return (
            self.status
            is UniversalWorkerAssignmentStatus.ASSIGNED
        )

    @property
    def worker_id(
        self,
    ) -> str | None:

        if self.worker is None:

            return None

        return self.worker.worker_id

    @property
    def worker_instance_id(
        self,
    ) -> str | None:

        if self.worker is None:

            return None

        return self.worker.worker_instance_id

    @property
    def worker_identity(
        self,
    ) -> tuple[str, str] | None:

        if self.worker is None:

            return None

        return self.worker.canonical_identity


def assign_universal_worker(
    *,
    job_id: str,
    eligible_workers: Iterable[
        UniversalWorkerRegistration
    ],
) -> UniversalWorkerAssignmentResult:

    canonical_job_id = (
        normalize_universal_worker_assignment_job_id(
            job_id
        )
    )

    if isinstance(
        eligible_workers,
        (
            str,
            bytes,
            Mapping,
        ),
    ):

        raise UniversalWorkerAssignmentError(
            (
                "eligible_workers must be an iterable "
                "of UniversalWorkerRegistration records."
            ),
            code="invalid_eligible_workers",
            value=eligible_workers,
        )

    try:

        materialized = tuple(
            eligible_workers
        )

    except TypeError as exc:

        raise UniversalWorkerAssignmentError(
            (
                "eligible_workers must be an iterable "
                "of UniversalWorkerRegistration records."
            ),
            code="invalid_eligible_workers",
            value=eligible_workers,
        ) from exc

    validated = []

    seen_identities = set()

    for worker in materialized:

        validated_worker = (
            _validate_worker(
                worker
            )
        )

        identity = (
            validated_worker.canonical_identity
        )

        if identity in seen_identities:

            raise UniversalWorkerAssignmentError(
                (
                    "Duplicate eligible worker "
                    "identity."
                ),
                code=(
                    "duplicate_eligible_worker_"
                    "identity"
                ),
                value=identity,
            )

        seen_identities.add(
            identity
        )

        validated.append(
            validated_worker
        )

    if not validated:

        return UniversalWorkerAssignmentResult(
            job_id=canonical_job_id,
            status=(
                UniversalWorkerAssignmentStatus.NO_ASSIGNMENT
            ),
            worker=None,
            candidate_count=0,
        )

    ordered = tuple(
        sorted(
            validated,
            key=lambda worker: (
                worker.worker_id,
                worker.worker_instance_id,
            ),
        )
    )

    selected = ordered[0]

    return UniversalWorkerAssignmentResult(
        job_id=canonical_job_id,
        status=(
            UniversalWorkerAssignmentStatus.ASSIGNED
        ),
        worker=selected,
        candidate_count=len(
            ordered
        ),
    )


def explain_universal_worker_assignment_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.3",

            "component":
                "Universal Worker Assignment",

            "version":
                UNIVERSAL_WORKER_ASSIGNMENT_VERSION,

            "result_schema_version":
                UNIVERSAL_WORKER_ASSIGNMENT_RESULT_SCHEMA_VERSION,

            "input_rule": (
                "4.1.3 consumes a canonical job_id and "
                "caller-supplied already-eligible "
                "UniversalWorkerRegistration records"
            ),

            "eligibility_rule": (
                "4.1.3 does not determine eligibility; "
                "the caller owns construction of the "
                "eligible worker population"
            ),

            "selection_rule": (
                "when eligible workers exist, select the "
                "lexicographically first worker by "
                "worker_id then worker_instance_id"
            ),

            "empty_rule": (
                "an empty eligible worker population "
                "produces NO_ASSIGNMENT"
            ),

            "duplicate_rule": (
                "duplicate (worker_id, worker_instance_id) "
                "eligible worker identities are rejected"
            ),

            "job_evidence_rule": (
                "job_id is the only job evidence consumed "
                "by the assignment authority"
            ),

            "meaning": (
                "ASSIGNED is a deterministic selection "
                "decision only; it does not create runtime "
                "ownership of the job"
            ),

            "purity_rule": (
                "Worker Assignment is deterministic over "
                "caller-supplied evidence and performs no "
                "state lookup, mutation or persistence"
            ),

            "prohibitions": (
                "does not discover workers",
                "does not determine worker health",
                "does not read worker heartbeats",
                "does not detect stale workers",
                "does not inspect worker pools",
                "does not inspect worker capabilities",
                "does not inspect worker capacity",
                "does not maintain round-robin state",
                "does not persist assignments",
                "does not write worker_id into job metadata",
                "does not mutate job status",
                "does not transition jobs to RUNNING",
                "does not claim jobs",
                "does not dequeue jobs",
                "does not acquire leases",
                "does not renew leases",
                "does not release leases",
                "does not dispatch jobs",
                "does not execute jobs",
                "does not access orchestration",
                "does not access Runtime State Store",
                "does not mutate Queue Infrastructure",
                "does not register runtime handlers",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_ASSIGNMENT_VERSION",
    "UNIVERSAL_WORKER_ASSIGNMENT_RESULT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_ASSIGNMENT_JOB_ID_LENGTH",
    "UniversalWorkerAssignmentError",
    "UniversalWorkerAssignmentStatus",
    "UniversalWorkerAssignmentResult",
    "normalize_universal_worker_assignment_job_id",
    "assign_universal_worker",
    "explain_universal_worker_assignment_v1",
]
'''


ast.parse(
    SOURCE
)

ASSIGNMENT_PATH.write_text(
    SOURCE,
    encoding="utf-8",
)


# ============================================================
# IMPORT NEW AUTHORITY
# ============================================================

sys.path.insert(
    0,
    str(ROOT),
)

registration_name = (
    "backend.server.runtime."
    "universal_worker.registration"
)

assignment_name = (
    "backend.server.runtime."
    "universal_worker.assignment"
)

sys.modules.pop(
    assignment_name,
    None,
)

registration = importlib.import_module(
    registration_name
)

assignment = importlib.import_module(
    assignment_name
)


checks = []


def check(
    name,
    condition,
    detail="",
):

    checks.append(
        (
            name,
            bool(condition),
            str(detail),
        )
    )


# ============================================================
# VERSION / SCHEMA
# ============================================================

check(
    "version",
    assignment.UNIVERSAL_WORKER_ASSIGNMENT_VERSION
    == "universal_worker_assignment_v4.1.3",
)

check(
    "result_schema",
    assignment.UNIVERSAL_WORKER_ASSIGNMENT_RESULT_SCHEMA_VERSION
    == "universal_worker_assignment_result_schema_v1",
)


# ============================================================
# FIXTURES
# ============================================================

def worker(
    worker_id,
    instance_id,
):

    return (
        registration.create_universal_worker_registration(
            worker_id=worker_id,
            worker_type="general",
            worker_instance_id=instance_id,
            runtime_version="runtime-v1",
            host_id="host-a",
            registered_at="2026-08-15T20:00:00Z",
        )
    )


worker_b = worker(
    "worker-b",
    "instance-001",
)

worker_a2 = worker(
    "worker-a",
    "instance-002",
)

worker_a1 = worker(
    "worker-a",
    "instance-001",
)


# ============================================================
# DETERMINISTIC ASSIGNMENT
# ============================================================

result = (
    assignment.assign_universal_worker(
        job_id=" job-001 ",
        eligible_workers=(
            worker_b,
            worker_a2,
            worker_a1,
        ),
    )
)


check(
    "job_id_normalized",
    result.job_id
    == "job-001",
)

check(
    "assigned_true",
    result.assigned
    is True,
)

check(
    "assigned_status",
    result.status
    is assignment.UniversalWorkerAssignmentStatus.ASSIGNED,
)

check(
    "selected_worker_id",
    result.worker_id
    == "worker-a",
)

check(
    "selected_instance_id",
    result.worker_instance_id
    == "instance-001",
)

check(
    "selected_identity",
    result.worker_identity
    == (
        "worker-a",
        "instance-001",
    ),
)

check(
    "candidate_count",
    result.candidate_count
    == 3,
)


# ============================================================
# ORDER INDEPENDENCE
# ============================================================

reordered = (
    assignment.assign_universal_worker(
        job_id="job-001",
        eligible_workers=(
            worker_a2,
            worker_a1,
            worker_b,
        ),
    )
)


check(
    "input_order_independent",
    reordered
    == result,
)


# ============================================================
# NO ASSIGNMENT
# ============================================================

empty = (
    assignment.assign_universal_worker(
        job_id="job-002",
        eligible_workers=(),
    )
)


check(
    "empty_no_assignment",
    empty.status
    is assignment.UniversalWorkerAssignmentStatus.NO_ASSIGNMENT,
)

check(
    "empty_assigned_false",
    empty.assigned
    is False,
)

check(
    "empty_worker_none",
    empty.worker
    is None,
)

check(
    "empty_identity_none",
    empty.worker_identity
    is None,
)

check(
    "empty_candidate_count",
    empty.candidate_count
    == 0,
)


# ============================================================
# JOB ID VALIDATION
# ============================================================

for bad in (
    None,
    True,
    0,
    1,
    "",
    "   ",
    [],
    {},
):

    try:

        assignment.assign_universal_worker(
            job_id=bad,
            eligible_workers=(),
        )

    except assignment.UniversalWorkerAssignmentError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_job_id_"
        + type(bad).__name__
        + "_"
        + repr(bad),
        rejected,
    )


# ============================================================
# INVALID COLLECTIONS
# ============================================================

for bad in (
    None,
    "workers",
    b"workers",
    {},
    1,
    True,
):

    try:

        assignment.assign_universal_worker(
            job_id="job-x",
            eligible_workers=bad,
        )

    except assignment.UniversalWorkerAssignmentError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_collection_"
        + type(bad).__name__,
        rejected,
    )


# ============================================================
# INVALID WORKER
# ============================================================

for bad in (
    None,
    True,
    1,
    "",
    {},
    [],
):

    try:

        assignment.assign_universal_worker(
            job_id="job-x",
            eligible_workers=(
                worker_a1,
                bad,
            ),
        )

    except assignment.UniversalWorkerAssignmentError as exc:

        rejected = (
            exc.code
            == "invalid_assignment_worker"
        )

    else:

        rejected = False

    check(
        "invalid_worker_"
        + type(bad).__name__,
        rejected,
    )


# ============================================================
# DUPLICATE IDENTITY
# ============================================================

duplicate = (
    registration.create_universal_worker_registration(
        worker_id="worker-a",
        worker_type="specialized",
        worker_instance_id="instance-001",
        runtime_version="runtime-v2",
        host_id="host-z",
        registered_at="2026-08-15T21:00:00Z",
    )
)


try:

    assignment.assign_universal_worker(
        job_id="job-dup",
        eligible_workers=(
            worker_a1,
            duplicate,
        ),
    )

except assignment.UniversalWorkerAssignmentError as exc:

    duplicate_rejected = (
        exc.code
        == "duplicate_eligible_worker_identity"
    )

else:

    duplicate_rejected = False


check(
    "duplicate_identity_rejected",
    duplicate_rejected,
)


# ============================================================
# SAME LOGICAL WORKER / DIFFERENT INSTANCE
# ============================================================

same_logical = (
    assignment.assign_universal_worker(
        job_id="job-same",
        eligible_workers=(
            worker(
                "worker-c",
                "instance-002",
            ),
            worker(
                "worker-c",
                "instance-001",
            ),
        ),
    )
)


check(
    "different_instances_allowed",
    same_logical.candidate_count
    == 2,
)

check(
    "different_instances_tiebreak",
    same_logical.worker_identity
    == (
        "worker-c",
        "instance-001",
    ),
)


# ============================================================
# IMMUTABILITY
# ============================================================

try:

    result.worker = worker_b

except Exception:

    immutable = True

else:

    immutable = False


check(
    "assignment_result_immutable",
    immutable,
)


# ============================================================
# REGISTRATIONS NOT MUTATED
# ============================================================

before_worker = (
    worker_a1.to_dict()
)

assignment.assign_universal_worker(
    job_id="job-mutation",
    eligible_workers=(
        worker_a1,
    ),
)

after_worker = (
    worker_a1.to_dict()
)


check(
    "worker_registration_not_mutated",
    before_worker
    == after_worker,
)


# ============================================================
# EXPLANATION
# ============================================================

explanation = (
    assignment.explain_universal_worker_assignment_v1()
)


check(
    "explanation_phase",
    explanation.get("phase")
    == "4.1.3",
)

check(
    "explanation_component",
    explanation.get("component")
    == "Universal Worker Assignment",
)

check(
    "caller_supplied_eligible",
    "caller-supplied already-eligible"
    in explanation.get(
        "input_rule",
        "",
    ),
)

check(
    "does_not_determine_eligibility",
    "does not determine eligibility"
    in explanation.get(
        "eligibility_rule",
        "",
    ),
)

check(
    "selection_rule",
    "worker_id then worker_instance_id"
    in explanation.get(
        "selection_rule",
        "",
    ),
)

check(
    "empty_rule",
    "NO_ASSIGNMENT"
    in explanation.get(
        "empty_rule",
        "",
    ),
)

check(
    "job_id_only",
    "job_id is the only job evidence"
    in explanation.get(
        "job_evidence_rule",
        "",
    ),
)

check(
    "assignment_not_ownership",
    "does not create runtime ownership"
    in explanation.get(
        "meaning",
        "",
    ),
)

check(
    "pure_no_persistence",
    "no state lookup, mutation or persistence"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


required_prohibitions = (
    "does not discover workers",
    "does not determine worker health",
    "does not read worker heartbeats",
    "does not detect stale workers",
    "does not inspect worker pools",
    "does not inspect worker capabilities",
    "does not inspect worker capacity",
    "does not maintain round-robin state",
    "does not persist assignments",
    "does not write worker_id into job metadata",
    "does not mutate job status",
    "does not transition jobs to RUNNING",
    "does not claim jobs",
    "does not dequeue jobs",
    "does not acquire leases",
    "does not renew leases",
    "does not release leases",
    "does not dispatch jobs",
    "does not execute jobs",
    "does not access orchestration",
    "does not access Runtime State Store",
    "does not mutate Queue Infrastructure",
    "does not register runtime handlers",
    "does not perform filesystem I/O",
    "does not perform network I/O",
)


prohibitions = tuple(
    explanation.get(
        "prohibitions"
    )
    or ()
)


for index, item in enumerate(
    required_prohibitions,
    start=1,
):

    check(
        "prohibition_"
        + str(index),
        item in prohibitions,
        item,
    )


# ============================================================
# STATIC IMPORT BOUNDARY
# ============================================================

source = ASSIGNMENT_PATH.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(
    source
)


backend_imports = []


for node in ast.walk(tree):

    if isinstance(
        node,
        ast.ImportFrom,
    ):

        module_name = (
            node.module
            or ""
        )

        if module_name.startswith(
            "backend.server"
        ):

            backend_imports.append(
                module_name
            )

    elif isinstance(
        node,
        ast.Import,
    ):

        for alias in node.names:

            if alias.name.startswith(
                "backend.server"
            ):

                backend_imports.append(
                    alias.name
                )


check(
    "only_registration_backend_import",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.registration"
    ],
    backend_imports,
)


# ============================================================
# FORBIDDEN CALL BOUNDARY
# ============================================================

forbidden_names = {
    "open",
    "read_text",
    "write_text",
    "read_json",
    "write_json",
    "inspect_workers",
    "worker_heartbeat",
    "get_runtime_state_store_registry",
    "get_latest_worker_statuses",
    "save_assignment",
    "save_assignments",
    "mark_job_running",
    "update_job_status",
    "claim_job",
    "dequeue_job",
    "lease_job",
    "renew_lease",
    "release_lease",
    "dispatch_job",
    "dispatch_registered_runtime_handler",
    "execute_job",
    "run_one_job",
    "register_handler",
    "save_job",
    "get_job",
}


forbidden_calls = []


for node in ast.walk(tree):

    if not isinstance(
        node,
        ast.Call,
    ):

        continue

    if isinstance(
        node.func,
        ast.Name,
    ):

        name = node.func.id

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        name = node.func.attr

    else:

        continue

    if name in forbidden_names:

        forbidden_calls.append(
            (
                name,
                getattr(
                    node,
                    "lineno",
                    0,
                ),
            )
        )


check(
    "no_forbidden_calls",
    not forbidden_calls,
    forbidden_calls,
)


# ============================================================
# PROTECTED AUTHORITIES STILL EXACT
# ============================================================

for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(
        path
    )

    check(
        "protected_"
        + name,
        actual
        == expected,
        actual,
    )


# ============================================================
# ASSIGNMENT AST
# ============================================================

assignment_ast = ast_sha(
    ASSIGNMENT_PATH
)


check(
    "assignment_ast_generated",
    len(
        assignment_ast
    )
    == 64,
    assignment_ast,
)


# ============================================================
# REPORT
# ============================================================

passed = sum(
    1
    for _, ok, _
    in checks
    if ok
)

total = len(
    checks
)


lines = [
    (
        "PHASE 4.1.3 — UNIVERSAL WORKER "
        "ASSIGNMENT INITIAL IMPLEMENTATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER ASSIGNMENT AST SHA256: "
        + assignment_ast
    ),
    "",
]


for index, (
    name,
    ok,
    detail,
) in enumerate(
    checks,
    start=1,
):

    lines.append(
        (
            f"{index}. {name}: "
            f"{'PASS' if ok else 'FAIL'}"
        )
    )

    if detail:

        lines.append(
            "   "
            + detail
        )


lines.extend(
    [
        "",
        "=" * 112,
        (
            "INITIAL WORKER ASSIGNMENT RESULT: "
            + (
                "PASS"
                if passed == total
                else "FAIL"
            )
        ),
        (
            "CHECKS PASSED: "
            + str(passed)
            + "/"
            + str(total)
        ),
        "",
        "4.1.1 WORKER REGISTRATION MODIFIED: NO",
        "4.1.2 WORKER DISCOVERY MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "ASSIGNMENT PERSISTED: NO",
        "WORKER_ID WRITTEN TO JOB METADATA: NO",
        "JOB STATUS MUTATED: NO",
        "JOB TRANSITIONED TO RUNNING: NO",
        "JOB CLAIMED: NO",
        "JOB DEQUEUED: NO",
        "JOB LEASED: NO",
        "WORKER HEALTH DECIDED: NO",
        "HEARTBEAT READ: NO",
        "STALE WORKER DETECTED: NO",
        "WORKER POOL INSPECTED: NO",
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER CAPACITY INSPECTED: NO",
        "ROUND-ROBIN STATE CREATED: NO",
        "JOB DISPATCHED: NO",
        "JOB EXECUTED: NO",
        "",
        (
            "STATUS: INITIAL IMPLEMENTATION PASS "
            "— ADVERSARIAL REGRESSION REQUIRED"
            if passed == total
            else
            "STATUS: INITIAL IMPLEMENTATION FAILED"
        ),
    ]
)


REPORT_PATH.write_text(
    "\n".join(lines),
    encoding="utf-8",
)

print(
    "\n".join(lines)
)


if passed != total:

    raise SystemExit(
        "Phase 4.1.3 Worker Assignment initial implementation failed."
    )
