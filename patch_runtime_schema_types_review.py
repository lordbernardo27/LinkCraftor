from __future__ import annotations

import importlib.util
import py_compile
import shutil
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path.cwd().resolve()

TARGET = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_schema"
    / "types.py"
)

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_schema_types_review_{TIMESTAMP}"
    / TARGET.name
)


OLD_LIFECYCLE = '''class SchemaLifecycleState(str, Enum):
    """Lifecycle of a registered schema version.

    Legal transitions are enforced by :mod:`runtime_schema.deprecation`.
    """

    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"
'''


NEW_LIFECYCLE = '''class SchemaLifecycleState(str, Enum):
    """Lifecycle of a registered schema version.

    Legal transitions are enforced by :mod:`runtime_schema.deprecation`.

    ``REGISTERED`` separates durable registration from activation.
    ``SUSPENDED`` temporarily prevents normal use without retiring the
    schema. ``QUARANTINED`` isolates definitions whose integrity or safety
    requires investigation.
    """

    DRAFT = "draft"
    REGISTERED = "registered"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"
    RETIRED = "retired"
    QUARANTINED = "quarantined"
'''


OLD_TRANSITION = '''class TransitionDirection(str, Enum):
    """Direction of a schema version transition."""

    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"


class EnforcementLevel(str, Enum):
'''


NEW_TRANSITION = '''class TransitionDirection(str, Enum):
    """Direction of a version-to-version data transition."""

    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"


class SchemaTransitionType(str, Enum):
    """Broader schema lifecycle or version transition operation."""

    CREATE = "create"
    REGISTER = "register"
    ACTIVATE = "activate"
    SUSPEND = "suspend"
    RESUME = "resume"
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"
    DEPRECATE = "deprecate"
    RETIRE = "retire"
    QUARANTINE = "quarantine"
    RESTORE = "restore"


class RuntimeScope(str, Enum):
    """Scope at which a schema-management operation applies."""

    GLOBAL = "global"
    RUNTIME = "runtime"
    ORGANIZATION = "organization"
    TENANT = "tenant"
    WORKSPACE = "workspace"


class SchemaIdentityType(str, Enum):
    """Kinds of deterministic identity used by schema management."""

    SCHEMA_ID = "schema_id"
    CONTENT_FINGERPRINT = "content_fingerprint"
    SNAPSHOT_ID = "snapshot_id"
    DIFF_ID = "diff_id"
    MIGRATION_PLAN_ID = "migration_plan_id"
    CERTIFICATE_ID = "certificate_id"


class SchemaActorType(str, Enum):
    """Kinds of actors that may perform schema-management actions."""

    SYSTEM = "system"
    RUNTIME = "runtime"
    OWNER = "owner"
    OPERATOR = "operator"
    SERVICE = "service"
    SUBSYSTEM = "subsystem"
    WORKER = "worker"
    CERTIFICATION = "certification"
    TENANT = "tenant"


class SchemaManagementCapability(str, Enum):
    """Capabilities offered by the Runtime Schema Management subsystem."""

    REGISTRY = "registry"
    DEFINITION = "definition"
    OWNERSHIP = "ownership"
    NAMESPACE = "namespace"
    VERSIONING = "versioning"
    COMPATIBILITY = "compatibility"
    VALIDATION = "validation"
    FINGERPRINTING = "fingerprinting"
    SERIALIZATION = "serialization"
    MIGRATION_PLANNING = "migration_planning"
    TRANSITION_VALIDATION = "transition_validation"
    DEPRECATION = "deprecation"
    SNAPSHOTS = "snapshots"
    CHANGE_DETECTION = "change_detection"
    DIFF = "diff"
    AUDIT = "audit"
    CERTIFICATION = "certification"


class EnforcementLevel(str, Enum):
'''


OLD_FORMATS = '''# ---------------------------------------------------------------------------
# Identifier and timestamp formats
# ---------------------------------------------------------------------------

#: Lowercase dotted namespace, e.g. ``runtime.job`` or ``product.reports``.
'''


NEW_FORMATS = '''# ---------------------------------------------------------------------------
# Canonical limits and reserved runtime namespaces
# ---------------------------------------------------------------------------

MAX_SCHEMA_NAME_LENGTH: Final[int] = 128
MAX_NAMESPACE_LENGTH: Final[int] = 256
MAX_IDENTIFIER_LENGTH: Final[int] = 256
MAX_DESCRIPTION_LENGTH: Final[int] = 4096
MAX_METADATA_SIZE_BYTES: Final[int] = 65536
MAX_TAG_COUNT: Final[int] = 128

RESERVED_RUNTIME_ROOT: Final[str] = "runtime"
RESERVED_RUNTIME_PREFIX: Final[str] = "runtime."
RESERVED_SCHEMA_NAMESPACE: Final[str] = "runtime.schema"
RESERVED_SCHEMA_REGISTRY_NAMESPACE: Final[str] = "runtime.schema.registry"
RESERVED_SCHEMA_CERTIFICATION_NAMESPACE: Final[str] = (
    "runtime.schema.certification"
)


# ---------------------------------------------------------------------------
# Identifier and timestamp formats
# ---------------------------------------------------------------------------

#: Lowercase dotted namespace, e.g. ``runtime.job`` or ``product.reports``.
'''


OLD_NAMESPACE_VALIDATION = '''def is_valid_namespace(value: object) -> bool:
    """True if *value* is a syntactically valid namespace."""
    return isinstance(value, str) and bool(NAMESPACE_RE.match(value)) and len(value) <= 256


def is_valid_name(value: object) -> bool:
    """True if *value* is a syntactically valid schema/field name."""
    return isinstance(value, str) and bool(NAME_RE.match(value))


def is_valid_identifier(value: object) -> bool:
    """True if *value* is a syntactically valid free-form identifier."""
    return isinstance(value, str) and bool(IDENTIFIER_RE.match(value))
'''


NEW_NAMESPACE_VALIDATION = '''def is_valid_namespace(value: object) -> bool:
    """True if *value* is a syntactically valid namespace."""
    return (
        isinstance(value, str)
        and len(value) <= MAX_NAMESPACE_LENGTH
        and bool(NAMESPACE_RE.fullmatch(value))
    )


def is_valid_name(value: object) -> bool:
    """True if *value* is a syntactically valid schema or field name."""
    return (
        isinstance(value, str)
        and len(value) <= MAX_SCHEMA_NAME_LENGTH
        and bool(NAME_RE.fullmatch(value))
    )


def is_valid_identifier(value: object) -> bool:
    """True if *value* is a syntactically valid free-form identifier."""
    return (
        isinstance(value, str)
        and len(value) <= MAX_IDENTIFIER_LENGTH
        and bool(IDENTIFIER_RE.fullmatch(value))
    )


def is_reserved_runtime_namespace(value: object) -> bool:
    """True when *value* belongs to the frozen ``runtime.*`` namespace."""
    return (
        isinstance(value, str)
        and (
            value == RESERVED_RUNTIME_ROOT
            or value.startswith(RESERVED_RUNTIME_PREFIX)
        )
    )
'''


def replace_exactly_once(
    source: str,
    old: str,
    new: str,
    label: str,
) -> str:
    count = source.count(old)

    if count != 1:
        raise RuntimeError(
            f"{label}: expected exactly one match, found {count}."
        )

    return source.replace(old, new, 1)


def import_target():
    module_name = "runtime_schema_types_patch_verification"

    sys.modules.pop(module_name, None)

    spec = importlib.util.spec_from_file_location(
        module_name,
        TARGET,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Unable to import patched target: {TARGET}"
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def verify_behavior(module) -> None:
    assert module.SchemaLifecycleState.REGISTERED.value == "registered"
    assert module.SchemaLifecycleState.SUSPENDED.value == "suspended"
    assert module.SchemaLifecycleState.QUARANTINED.value == "quarantined"

    assert module.TransitionDirection.UPGRADE.value == "upgrade"
    assert module.TransitionDirection.DOWNGRADE.value == "downgrade"
    assert len(module.TransitionDirection) == 2

    assert module.SchemaTransitionType.REGISTER.value == "register"
    assert module.SchemaTransitionType.QUARANTINE.value == "quarantine"

    assert module.RuntimeScope.WORKSPACE.value == "workspace"
    assert module.SchemaIdentityType.SCHEMA_ID.value == "schema_id"
    assert module.SchemaActorType.CERTIFICATION.value == "certification"

    assert (
        module.SchemaManagementCapability.MIGRATION_PLANNING.value
        == "migration_planning"
    )

    assert module.RESERVED_RUNTIME_ROOT == "runtime"
    assert module.RESERVED_RUNTIME_PREFIX == "runtime."
    assert module.RESERVED_SCHEMA_NAMESPACE == "runtime.schema"

    assert module.is_reserved_runtime_namespace("runtime")
    assert module.is_reserved_runtime_namespace("runtime.schema")
    assert not module.is_reserved_runtime_namespace("product.schema")

    assert module.is_valid_namespace("runtime.schema")
    assert not module.is_valid_namespace("Runtime.Schema")
    assert module.is_valid_name("job_record")
    assert not module.is_valid_name("JobRecord")
    assert module.is_valid_identifier("runtime:worker-001")

    frozen = module.deep_freeze(
        {
            "nested": {
                "values": [1, 2, 3],
            }
        }
    )

    assert frozen["nested"]["values"] == (1, 2, 3)

    thawed = module.deep_thaw(frozen)

    assert thawed == {
        "nested": {
            "values": [1, 2, 3],
        }
    }


def rollback() -> None:
    if BACKUP.exists():
        shutil.copy2(BACKUP, TARGET)


def main() -> int:
    print("=" * 78)
    print("RUNTIME SCHEMA MANAGEMENT")
    print("TYPES.PY REVIEW PATCH")
    print("=" * 78)
    print(f"Target: {TARGET}")
    print()

    if not TARGET.exists():
        raise FileNotFoundError(
            "Claude's types.py has not been placed at the expected path: "
            f"{TARGET}"
        )

    original = TARGET.read_text(
        encoding="utf-8-sig"
    )

    BACKUP.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        TARGET,
        BACKUP,
    )

    try:
        patched = original

        patched = replace_exactly_once(
            patched,
            OLD_LIFECYCLE,
            NEW_LIFECYCLE,
            "Schema lifecycle patch",
        )

        patched = replace_exactly_once(
            patched,
            OLD_TRANSITION,
            NEW_TRANSITION,
            "Transition and vocabulary patch",
        )

        patched = replace_exactly_once(
            patched,
            OLD_FORMATS,
            NEW_FORMATS,
            "Canonical constants patch",
        )

        patched = replace_exactly_once(
            patched,
            OLD_NAMESPACE_VALIDATION,
            NEW_NAMESPACE_VALIDATION,
            "Validation helper patch",
        )

        TARGET.write_text(
            patched,
            encoding="utf-8",
            newline="\n",
        )

        py_compile.compile(
            str(TARGET),
            doraise=True,
        )

        package_dir = TARGET.parent

        for path in sorted(
            package_dir.glob("*.py")
        ):
            py_compile.compile(
                str(path),
                doraise=True,
            )

        module = import_target()
        verify_behavior(module)

    except Exception:
        rollback()

        print("ROLLBACK COMPLETE")
        print(
            "The types.py revision failed verification, "
            "so Claude's original file was restored."
        )
        print()
        print(traceback.format_exc())

        return 1

    print("Backup:                         PASS")
    print("Exact-anchor patching:          PASS")
    print("types.py compilation:           PASS")
    print("Package compilation:            PASS")
    print("Lifecycle vocabulary:           PASS")
    print("Transition separation:          PASS")
    print("Runtime scopes:                 PASS")
    print("Identity vocabulary:            PASS")
    print("Actor vocabulary:               PASS")
    print("Capability vocabulary:          PASS")
    print("Reserved namespace constants:   PASS")
    print("Canonical limits:               PASS")
    print("Validation helpers:             PASS")
    print("Deep freeze/thaw regression:    PASS")
    print()
    print(f"Backup file: {BACKUP}")
    print()
    print("TYPES.PY REVIEW: APPROVED AND PATCHED")
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
