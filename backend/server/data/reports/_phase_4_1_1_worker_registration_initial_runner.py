from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

REGISTRATION_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "registration.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_1_worker_registration_initial_implementation.txt"
)


# ============================================================
# PROTECT EXISTING AUTHORITIES / LEGACY WORKER
# ============================================================

PROTECTED_FILES = {
    "queue_creation":
        ROOT / "backend/server/runtime/universal_queue/creation.py",

    "queue_certification":
        ROOT / "backend/server/runtime/universal_queue/certification.py",

    "job_contract":
        ROOT / "backend/server/runtime/universal_jobs/contract.py",

    "job_status":
        ROOT / "backend/server/runtime/universal_jobs/status.py",

    "job_attempts":
        ROOT / "backend/server/runtime/universal_jobs/attempts.py",

    "existing_runtime_worker":
        ROOT / "backend/server/runtime/universal_runtime_worker_v1.py",

    "runtime_registration":
        ROOT / "backend/server/runtime/universal_runtime_registration.py",

    "runtime_infrastructure":
        ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",

    "orchestration_queue":
        ROOT / "backend/server/orchestration/queue.py",

    "orchestration_service":
        ROOT / "backend/server/orchestration/service.py",
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


before = {
    name: ast_sha(path)
    for name, path
    in PROTECTED_FILES.items()
}


# ============================================================
# PRODUCTION AUTHORITY
# ============================================================

SOURCE = r'''from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping


UNIVERSAL_WORKER_REGISTRATION_VERSION = (
    "universal_worker_registration_v4.1.1"
)

UNIVERSAL_WORKER_REGISTRATION_SCHEMA_VERSION = (
    "universal_worker_registration_schema_v1"
)

MAX_UNIVERSAL_WORKER_ID_LENGTH = 160
MAX_UNIVERSAL_WORKER_TYPE_LENGTH = 120
MAX_UNIVERSAL_WORKER_INSTANCE_ID_LENGTH = 200
MAX_UNIVERSAL_WORKER_RUNTIME_VERSION_LENGTH = 120
MAX_UNIVERSAL_WORKER_HOST_ID_LENGTH = 200


class UniversalWorkerRegistrationError(
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


def _normalize_required_text(
    value: Any,
    *,
    field_name: str,
    maximum_length: int,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalWorkerRegistrationError(
            f"{field_name} must be a string.",
            code=f"invalid_{field_name}_type",
            value=value,
        )

    normalized = value.strip()

    if not normalized:

        raise UniversalWorkerRegistrationError(
            f"{field_name} must not be empty.",
            code=f"empty_{field_name}",
            value=value,
        )

    if len(normalized) > maximum_length:

        raise UniversalWorkerRegistrationError(
            (
                f"{field_name} exceeds maximum length "
                f"{maximum_length}."
            ),
            code=f"{field_name}_too_long",
            value=value,
        )

    return normalized


def normalize_universal_worker_id(
    value: Any,
) -> str:

    return _normalize_required_text(
        value,
        field_name="worker_id",
        maximum_length=MAX_UNIVERSAL_WORKER_ID_LENGTH,
    )


def normalize_universal_worker_type(
    value: Any,
) -> str:

    return _normalize_required_text(
        value,
        field_name="worker_type",
        maximum_length=MAX_UNIVERSAL_WORKER_TYPE_LENGTH,
    )


def normalize_universal_worker_instance_id(
    value: Any,
) -> str:

    return _normalize_required_text(
        value,
        field_name="worker_instance_id",
        maximum_length=(
            MAX_UNIVERSAL_WORKER_INSTANCE_ID_LENGTH
        ),
    )


def normalize_universal_worker_runtime_version(
    value: Any,
) -> str:

    return _normalize_required_text(
        value,
        field_name="runtime_version",
        maximum_length=(
            MAX_UNIVERSAL_WORKER_RUNTIME_VERSION_LENGTH
        ),
    )


def normalize_universal_worker_host_id(
    value: Any,
) -> str:

    return _normalize_required_text(
        value,
        field_name="host_id",
        maximum_length=MAX_UNIVERSAL_WORKER_HOST_ID_LENGTH,
    )


def normalize_universal_worker_registered_at(
    value: Any,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalWorkerRegistrationError(
            "registered_at must be a string.",
            code="invalid_registered_at_type",
            value=value,
        )

    text = value.strip()

    if not text:

        raise UniversalWorkerRegistrationError(
            "registered_at must not be empty.",
            code="empty_registered_at",
            value=value,
        )

    parse_value = text

    if parse_value.endswith("Z"):

        parse_value = (
            parse_value[:-1]
            + "+00:00"
        )

    try:

        parsed = datetime.fromisoformat(
            parse_value
        )

    except ValueError as exc:

        raise UniversalWorkerRegistrationError(
            (
                "registered_at must be a valid "
                "ISO-8601 timestamp."
            ),
            code="invalid_registered_at",
            value=value,
        ) from exc

    if parsed.tzinfo is None:

        raise UniversalWorkerRegistrationError(
            (
                "registered_at must include "
                "timezone information."
            ),
            code="registered_at_timezone_required",
            value=value,
        )

    canonical = parsed.astimezone(
        timezone.utc
    )

    return (
        canonical.isoformat(
            timespec="microseconds"
        )
        .replace(
            "+00:00",
            "Z",
        )
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalWorkerRegistration:

    worker_id: str
    worker_type: str
    worker_instance_id: str
    runtime_version: str
    host_id: str
    registered_at: str

    schema_version: str = (
        UNIVERSAL_WORKER_REGISTRATION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "worker_id",
            normalize_universal_worker_id(
                self.worker_id
            ),
        )

        object.__setattr__(
            self,
            "worker_type",
            normalize_universal_worker_type(
                self.worker_type
            ),
        )

        object.__setattr__(
            self,
            "worker_instance_id",
            normalize_universal_worker_instance_id(
                self.worker_instance_id
            ),
        )

        object.__setattr__(
            self,
            "runtime_version",
            normalize_universal_worker_runtime_version(
                self.runtime_version
            ),
        )

        object.__setattr__(
            self,
            "host_id",
            normalize_universal_worker_host_id(
                self.host_id
            ),
        )

        object.__setattr__(
            self,
            "registered_at",
            normalize_universal_worker_registered_at(
                self.registered_at
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_WORKER_REGISTRATION_SCHEMA_VERSION
        ):

            raise UniversalWorkerRegistrationError(
                (
                    "Invalid Worker Registration "
                    "schema_version."
                ),
                code=(
                    "invalid_worker_registration_"
                    "schema_version"
                ),
                value=self.schema_version,
            )

    @property
    def canonical_identity(
        self,
    ) -> tuple[str, str]:

        return (
            self.worker_id,
            self.worker_instance_id,
        )

    def to_dict(
        self,
    ) -> dict[str, str]:

        return {
            "schema_version":
                self.schema_version,

            "worker_id":
                self.worker_id,

            "worker_type":
                self.worker_type,

            "worker_instance_id":
                self.worker_instance_id,

            "runtime_version":
                self.runtime_version,

            "host_id":
                self.host_id,

            "registered_at":
                self.registered_at,
        }


def create_universal_worker_registration(
    *,
    worker_id: str,
    worker_type: str,
    worker_instance_id: str,
    runtime_version: str,
    host_id: str,
    registered_at: str,
) -> UniversalWorkerRegistration:

    return UniversalWorkerRegistration(
        worker_id=worker_id,
        worker_type=worker_type,
        worker_instance_id=worker_instance_id,
        runtime_version=runtime_version,
        host_id=host_id,
        registered_at=registered_at,
    )


def is_same_universal_worker_registration_identity(
    *,
    left: UniversalWorkerRegistration,
    right: UniversalWorkerRegistration,
) -> bool:

    if not isinstance(
        left,
        UniversalWorkerRegistration,
    ):

        raise UniversalWorkerRegistrationError(
            (
                "left must be a "
                "UniversalWorkerRegistration."
            ),
            code="invalid_left_worker_registration",
            value=left,
        )

    if not isinstance(
        right,
        UniversalWorkerRegistration,
    ):

        raise UniversalWorkerRegistrationError(
            (
                "right must be a "
                "UniversalWorkerRegistration."
            ),
            code="invalid_right_worker_registration",
            value=right,
        )

    return (
        left.canonical_identity
        == right.canonical_identity
    )


def explain_universal_worker_registration_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "4.1.1",

            "component":
                "Universal Worker Registration",

            "version":
                UNIVERSAL_WORKER_REGISTRATION_VERSION,

            "schema_version":
                UNIVERSAL_WORKER_REGISTRATION_SCHEMA_VERSION,

            "canonical_identity": (
                "worker_id",
                "worker_instance_id",
            ),

            "identity_semantics": (
                "worker_id identifies the logical worker; "
                "worker_instance_id identifies one concrete "
                "running instance of that logical worker"
            ),

            "owned_fields": (
                "worker_id",
                "worker_type",
                "worker_instance_id",
                "runtime_version",
                "host_id",
                "registered_at",
            ),

            "registered_at_rule": (
                "registered_at is caller-supplied registration "
                "evidence and is normalized to canonical UTC"
            ),

            "immutability_rule": (
                "a Worker Registration record is immutable"
            ),

            "purity_rule": (
                "4.1.1 validates and represents registration "
                "evidence only; it does not persist, discover, "
                "assign, lease, heartbeat or execute workers"
            ),

            "prohibitions": (
                "does not create worker pools",
                "does not declare worker capabilities",
                "does not determine worker health",
                "does not determine worker availability",
                "does not determine worker capacity",
                "does not assign jobs",
                "does not claim jobs",
                "does not lease jobs",
                "does not renew leases",
                "does not release leases",
                "does not emit heartbeats",
                "does not detect stale workers",
                "does not recover workers",
                "does not scale workers",
                "does not drain workers",
                "does not shut down workers",
                "does not dispatch jobs",
                "does not execute jobs",
                "does not register runtime handlers",
                "does not access orchestration",
                "does not access Runtime State Store",
                "does not mutate Queue Infrastructure",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_WORKER_REGISTRATION_VERSION",
    "UNIVERSAL_WORKER_REGISTRATION_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_ID_LENGTH",
    "MAX_UNIVERSAL_WORKER_TYPE_LENGTH",
    "MAX_UNIVERSAL_WORKER_INSTANCE_ID_LENGTH",
    "MAX_UNIVERSAL_WORKER_RUNTIME_VERSION_LENGTH",
    "MAX_UNIVERSAL_WORKER_HOST_ID_LENGTH",
    "UniversalWorkerRegistrationError",
    "UniversalWorkerRegistration",
    "normalize_universal_worker_id",
    "normalize_universal_worker_type",
    "normalize_universal_worker_instance_id",
    "normalize_universal_worker_runtime_version",
    "normalize_universal_worker_host_id",
    "normalize_universal_worker_registered_at",
    "create_universal_worker_registration",
    "is_same_universal_worker_registration_identity",
    "explain_universal_worker_registration_v1",
]
'''


ast.parse(
    SOURCE
)

REGISTRATION_PATH.write_text(
    SOURCE,
    encoding="utf-8",
)


# ============================================================
# VERIFY PROTECTED FILES UNTOUCHED
# ============================================================

for name, path in PROTECTED_FILES.items():

    actual = ast_sha(path)

    if actual != before[name]:

        raise SystemExit(
            (
                "Protected authority modified: "
                + name
            )
        )


# ============================================================
# IMPORT NEW AUTHORITY
# ============================================================

sys.path.insert(
    0,
    str(ROOT),
)

module_name = (
    "backend.server.runtime."
    "universal_worker.registration"
)

sys.modules.pop(
    module_name,
    None,
)

module = importlib.import_module(
    module_name
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


registration_ast = ast_sha(
    REGISTRATION_PATH
)


# ============================================================
# VERSION / SCHEMA
# ============================================================

check(
    "version",
    module.UNIVERSAL_WORKER_REGISTRATION_VERSION
    == "universal_worker_registration_v4.1.1",
)

check(
    "schema",
    module.UNIVERSAL_WORKER_REGISTRATION_SCHEMA_VERSION
    == "universal_worker_registration_schema_v1",
)


# ============================================================
# VALID REGISTRATION
# ============================================================

registration = (
    module.create_universal_worker_registration(
        worker_id=" universal-runtime-worker ",
        worker_type=" general ",
        worker_instance_id=" instance-001 ",
        runtime_version=" runtime-v1 ",
        host_id=" host-a ",
        registered_at="2026-08-15T20:00:00+00:00",
    )
)


check(
    "worker_id_normalized",
    registration.worker_id
    == "universal-runtime-worker",
)

check(
    "worker_type_normalized",
    registration.worker_type
    == "general",
)

check(
    "instance_normalized",
    registration.worker_instance_id
    == "instance-001",
)

check(
    "runtime_version_normalized",
    registration.runtime_version
    == "runtime-v1",
)

check(
    "host_id_normalized",
    registration.host_id
    == "host-a",
)

check(
    "registered_at_canonical",
    registration.registered_at
    == "2026-08-15T20:00:00.000000Z",
)

check(
    "canonical_identity",
    registration.canonical_identity
    == (
        "universal-runtime-worker",
        "instance-001",
    ),
)


# ============================================================
# SERIALIZATION
# ============================================================

serialized = (
    registration.to_dict()
)


check(
    "serialized_keys",
    tuple(
        serialized.keys()
    )
    == (
        "schema_version",
        "worker_id",
        "worker_type",
        "worker_instance_id",
        "runtime_version",
        "host_id",
        "registered_at",
    ),
)


# ============================================================
# IDENTITY COMPARISON
# ============================================================

same_identity = (
    module.create_universal_worker_registration(
        worker_id="universal-runtime-worker",
        worker_type="other-type",
        worker_instance_id="instance-001",
        runtime_version="runtime-v2",
        host_id="host-b",
        registered_at="2026-08-15T21:00:00Z",
    )
)


different_instance = (
    module.create_universal_worker_registration(
        worker_id="universal-runtime-worker",
        worker_type="general",
        worker_instance_id="instance-002",
        runtime_version="runtime-v1",
        host_id="host-a",
        registered_at="2026-08-15T20:00:00Z",
    )
)


check(
    "same_identity_true",
    module.is_same_universal_worker_registration_identity(
        left=registration,
        right=same_identity,
    )
    is True,
)

check(
    "different_instance_false",
    module.is_same_universal_worker_registration_identity(
        left=registration,
        right=different_instance,
    )
    is False,
)


# ============================================================
# STRICT INVALID VALUE TESTS
# ============================================================

for field_name in (
    "worker_id",
    "worker_type",
    "worker_instance_id",
    "runtime_version",
    "host_id",
):

    kwargs = {
        "worker_id": "worker",
        "worker_type": "general",
        "worker_instance_id": "instance",
        "runtime_version": "runtime-v1",
        "host_id": "host",
        "registered_at": "2026-08-15T20:00:00Z",
    }

    kwargs[
        field_name
    ] = "   "

    try:

        module.create_universal_worker_registration(
            **kwargs
        )

    except module.UniversalWorkerRegistrationError:

        rejected = True

    else:

        rejected = False

    check(
        "blank_"
        + field_name
        + "_rejected",
        rejected,
    )


for bad_timestamp in (
    "",
    "not-a-time",
    "2026-08-15T20:00:00",
    None,
    True,
    123,
):

    kwargs = {
        "worker_id": "worker",
        "worker_type": "general",
        "worker_instance_id": "instance",
        "runtime_version": "runtime-v1",
        "host_id": "host",
        "registered_at": bad_timestamp,
    }

    try:

        module.create_universal_worker_registration(
            **kwargs
        )

    except module.UniversalWorkerRegistrationError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_registered_at_"
        + repr(bad_timestamp),
        rejected,
    )


# ============================================================
# IMMUTABILITY
# ============================================================

try:

    registration.worker_id = "mutated"

except Exception:

    immutable = True

else:

    immutable = False


check(
    "registration_immutable",
    immutable,
)


# ============================================================
# EXPLANATION BOUNDARY
# ============================================================

explanation = (
    module.explain_universal_worker_registration_v1()
)


check(
    "explanation_phase",
    explanation.get(
        "phase"
    )
    == "4.1.1",
)

check(
    "explanation_component",
    explanation.get(
        "component"
    )
    == "Universal Worker Registration",
)

check(
    "identity_semantics",
    "logical worker"
    in explanation.get(
        "identity_semantics",
        "",
    ),
)

check(
    "purity_rule",
    "does not persist"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


required_prohibitions = (
    "does not create worker pools",
    "does not declare worker capabilities",
    "does not determine worker health",
    "does not determine worker availability",
    "does not determine worker capacity",
    "does not assign jobs",
    "does not claim jobs",
    "does not lease jobs",
    "does not emit heartbeats",
    "does not execute jobs",
    "does not register runtime handlers",
    "does not access orchestration",
    "does not access Runtime State Store",
    "does not mutate Queue Infrastructure",
    "does not perform filesystem I/O",
    "does not perform network I/O",
)


prohibitions = tuple(
    explanation.get(
        "prohibitions"
    )
    or ()
)


for item in required_prohibitions:

    check(
        "prohibition_"
        + item.replace(
            " ",
            "_"
        ),
        item
        in prohibitions,
    )


# ============================================================
# AST SIDE-EFFECT CHECK
# ============================================================

production_source = (
    REGISTRATION_PATH.read_text(
        encoding="utf-8-sig"
    )
)

production_tree = ast.parse(
    production_source
)


backend_imports = []


for node in ast.walk(
    production_tree
):

    if isinstance(
        node,
        ast.ImportFrom,
    ):

        name = (
            node.module
            or ""
        )

        if name.startswith(
            "backend.server"
        ):

            backend_imports.append(
                name
            )


check(
    "no_backend_imports",
    not backend_imports,
    backend_imports,
)


forbidden_calls = []


for node in ast.walk(
    production_tree
):

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

    if name in {
        "open",
        "write_text",
        "read_text",
        "enqueue_job",
        "dequeue_job",
        "claim_job",
        "dispatch_job",
        "register_handler",
        "worker_heartbeat",
        "save_job",
        "get_job",
    }:

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
# FINAL PROTECTION CHECK
# ============================================================

for name, path in PROTECTED_FILES.items():

    actual = ast_sha(path)

    check(
        "protected_"
        + name,
        actual
        == before[name],
        actual,
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
        "PHASE 4.1.1 — UNIVERSAL WORKER "
        "REGISTRATION INITIAL IMPLEMENTATION"
    ),
    "=" * 108,
    "",
    (
        "WORKER REGISTRATION AST SHA256: "
        + registration_ast
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
        "=" * 108,
        (
            "INITIAL IMPLEMENTATION RESULT: "
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
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB AUTHORITIES MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "WORKER REGISTERED INTO LIVE STATE: NO",
        "WORKER HEARTBEAT EMITTED: NO",
        "JOB ASSIGNED: NO",
        "JOB CLAIMED: NO",
        "JOB LEASED: NO",
        "JOB DISPATCHED: NO",
        "JOB EXECUTED: NO",
        "WORKER POOL CREATED: NO",
        "WORKER CAPABILITY DECLARED: NO",
        "WORKER CAPACITY DECIDED: NO",
        "FILESYSTEM / NETWORK I/O BY PRODUCTION AUTHORITY: NO",
        "",
        (
            "STATUS: INITIAL IMPLEMENTATION PASS "
            "— REGRESSION REQUIRED"
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
        "Phase 4.1.1 initial implementation failed."
    )
