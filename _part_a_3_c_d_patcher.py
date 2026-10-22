from __future__ import annotations

import ast
import hashlib
import pathlib
import py_compile
import sys


root = pathlib.Path(sys.argv[1]).resolve()
backup_directory = pathlib.Path(sys.argv[2]).resolve()
runtime_directory = root / "backend" / "server" / "runtime"

admission_path = runtime_directory / "runtime_registration_admission.py"
gateway_path = runtime_directory / "runtime_registration_gateway.py"
worker_path = runtime_directory / "universal_runtime_worker_v1.py"

admission_candidate = (
    backup_directory / "runtime_registration_admission.py.candidate"
)
gateway_candidate = (
    backup_directory / "runtime_registration_gateway.py.candidate"
)
worker_candidate = (
    backup_directory / "universal_runtime_worker_v1.py.candidate"
)

EXPECTED_GATEWAY_HASH = (
    "9abf349280104c840e7c7ce835ed1f808"
    "b0e6c15557c416c2b9b0e883ccc9547"
)
EXPECTED_WORKER_HASH = (
    "11eea0ab8fe2e5e226a9f0a3f548f1d4"
    "059f9967c1ec357b5ddc2bfa2ac12b2a"
)


def file_hash(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise RuntimeError(message)


gateway_hash = file_hash(gateway_path)
worker_hash = file_hash(worker_path)

if gateway_hash != EXPECTED_GATEWAY_HASH:
    fail(
        "Registration gateway precondition changed. "
        f"Expected {EXPECTED_GATEWAY_HASH}, found {gateway_hash}."
    )

if worker_hash != EXPECTED_WORKER_HASH:
    fail(
        "Worker precondition changed. "
        f"Expected {EXPECTED_WORKER_HASH}, found {worker_hash}."
    )


admission_source = '''"""Registration-specific runtime admission enforcement.

This authority evaluates the certified registration-package declarations
before capability admission and handler dispatch.

Supported lifecycle_policy declarations:

- allowed_kernel_states: collection of permitted kernel-state strings;
- require_worker_enabled: Boolean requirement.

configuration_requirements maps canonical RuntimeConfiguration field
names to exact required effective values.

feature_flag_key uses the canonical RuntimeFeatureFlagGateway.

runtime_version_requirements uses RuntimeVersionRequirement and the
canonical Runtime Compatibility authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.runtime_compatibility import (
    RuntimeCompatibilityLayer,
    RuntimeCompatibilityMode,
    RuntimeCompatibilityPolicy,
    RuntimeVersionRequirement,
)
from backend.server.runtime.runtime_feature_flag_gateway import (
    GATEWAY_KEY as FEATURE_FLAG_GATEWAY_KEY,
)
from backend.server.runtime.runtime_feature_flags import (
    RuntimeFeatureFlagDecisionReason,
)
from backend.server.runtime.runtime_versioning import (
    RuntimeSemanticVersion,
)


RUNTIME_VERSION_MANAGER_KEY = "runtime_version_manager"
REGISTRATION_ADMISSION_SCHEMA_VERSION = (
    "runtime_registration_admission_v1"
)

_ALLOWED_LIFECYCLE_POLICY_KEYS = frozenset(
    {
        "allowed_kernel_states",
        "require_worker_enabled",
    }
)

_binding_lock = RLock()
_binding: tuple[Any, Any] | None = None


class RuntimeRegistrationAdmissionError(RuntimeError):
    """Registration declarations rejected runtime execution."""


@dataclass(frozen=True, slots=True)
class RuntimeRegistrationAdmissionReport:
    schema_version: str
    admitted: bool
    job_type: str
    lifecycle_checked: bool
    configuration_checked: bool
    feature_flag_checked: bool
    version_compatibility_checked: bool
    feature_flag_key: str | None
    evaluated_contracts: tuple[str, ...]
    evidence: Mapping[str, Any]


def bind_runtime_registration_admission(
    *,
    configuration: Any,
    kernel: Any,
) -> None:
    if configuration is None:
        raise RuntimeRegistrationAdmissionError(
            "Runtime configuration is required for registration admission."
        )

    if kernel is None:
        raise RuntimeRegistrationAdmissionError(
            "Runtime kernel is required for registration admission."
        )

    if not callable(getattr(configuration, "to_dict", None)):
        raise RuntimeRegistrationAdmissionError(
            "Runtime configuration must expose to_dict()."
        )

    for method_name in (
        "snapshot",
        "has_component",
        "get_component",
    ):
        if not callable(getattr(kernel, method_name, None)):
            raise RuntimeRegistrationAdmissionError(
                "Runtime kernel does not expose "
                f"{method_name}()."
            )

    global _binding

    with _binding_lock:
        _binding = (configuration, kernel)


def clear_runtime_registration_admission_binding() -> None:
    global _binding

    with _binding_lock:
        _binding = None


def _current_binding() -> tuple[Any, Any] | None:
    with _binding_lock:
        return _binding


def _mapping(
    registration: Mapping[str, Any],
    field_name: str,
) -> Mapping[str, Any]:
    value = registration.get(field_name, {})

    if value is None:
        return MappingProxyType({})

    if not isinstance(value, Mapping):
        raise RuntimeRegistrationAdmissionError(
            f"{field_name} must be a mapping."
        )

    return value


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip()

    return normalized or None


def _state_value(kernel: Any) -> str:
    snapshot = kernel.snapshot()
    state = getattr(snapshot, "state", None)

    if state is None:
        raise RuntimeRegistrationAdmissionError(
            "Runtime kernel snapshot has no state."
        )

    value = getattr(state, "value", state)
    normalized = str(value or "").strip().lower()

    if not normalized:
        raise RuntimeRegistrationAdmissionError(
            "Runtime kernel state is empty."
        )

    return normalized


def _string_collection(
    value: Any,
    field_name: str,
) -> tuple[str, ...]:
    if isinstance(value, str):
        raise RuntimeRegistrationAdmissionError(
            f"{field_name} must be a collection, not a string."
        )

    try:
        raw_values = tuple(value)
    except TypeError as exc:
        raise RuntimeRegistrationAdmissionError(
            f"{field_name} must be a collection."
        ) from exc

    normalized = tuple(
        str(item or "").strip().lower()
        for item in raw_values
    )

    if any(not item for item in normalized):
        raise RuntimeRegistrationAdmissionError(
            f"{field_name} contains an empty value."
        )

    if len(set(normalized)) != len(normalized):
        raise RuntimeRegistrationAdmissionError(
            f"{field_name} contains duplicate values."
        )

    return normalized


def _require_lifecycle_policy(
    policy: Mapping[str, Any],
    *,
    configuration: Any,
    kernel: Any,
) -> dict[str, Any]:
    unknown_keys = sorted(
        set(policy) - _ALLOWED_LIFECYCLE_POLICY_KEYS
    )

    if unknown_keys:
        raise RuntimeRegistrationAdmissionError(
            "Unsupported lifecycle_policy declarations: "
            + ", ".join(unknown_keys)
        )

    kernel_state = _state_value(kernel)

    allowed_states_value = policy.get(
        "allowed_kernel_states",
        (),
    )

    allowed_states = (
        _string_collection(
            allowed_states_value,
            "lifecycle_policy.allowed_kernel_states",
        )
        if allowed_states_value
        else ()
    )

    if allowed_states and kernel_state not in allowed_states:
        raise RuntimeRegistrationAdmissionError(
            "Registration lifecycle policy rejected kernel state "
            f"{kernel_state!r}; allowed states: "
            + ", ".join(allowed_states)
        )

    require_worker_enabled = policy.get(
        "require_worker_enabled",
        False,
    )

    if not isinstance(require_worker_enabled, bool):
        raise RuntimeRegistrationAdmissionError(
            "lifecycle_policy.require_worker_enabled "
            "must be a Boolean."
        )

    worker_enabled = getattr(
        configuration,
        "worker_enabled",
        None,
    )

    if require_worker_enabled and worker_enabled is not True:
        raise RuntimeRegistrationAdmissionError(
            "Registration lifecycle policy requires an enabled worker."
        )

    return {
        "kernel_state": kernel_state,
        "allowed_kernel_states": list(allowed_states),
        "require_worker_enabled": require_worker_enabled,
        "worker_enabled": worker_enabled,
    }


def _normalize_effective_value(value: Any) -> Any:
    if hasattr(value, "__fspath__"):
        return str(value)

    return value


def _require_configuration(
    requirements: Mapping[str, Any],
    *,
    configuration: Any,
) -> dict[str, Any]:
    effective = configuration.to_dict(
        include_sources=False,
        redact_sensitive=False,
    )

    if not isinstance(effective, Mapping):
        raise RuntimeRegistrationAdmissionError(
            "Runtime configuration to_dict() did not return a mapping."
        )

    mismatches: list[str] = []
    observed: dict[str, Any] = {}

    for field_name, expected in requirements.items():
        if field_name not in effective:
            raise RuntimeRegistrationAdmissionError(
                "Registration references an unavailable runtime "
                f"configuration field: {field_name!r}"
            )

        actual = _normalize_effective_value(
            effective[field_name]
        )
        required = _normalize_effective_value(expected)

        observed[field_name] = actual

        if actual != required:
            mismatches.append(
                f"{field_name}: expected {required!r}, "
                f"actual {actual!r}"
            )

    if mismatches:
        raise RuntimeRegistrationAdmissionError(
            "Runtime configuration requirements failed: "
            + "; ".join(mismatches)
        )

    return observed


def _runtime_manifest(kernel: Any) -> Any:
    if not kernel.has_component(
        RUNTIME_VERSION_MANAGER_KEY
    ):
        raise RuntimeRegistrationAdmissionError(
            "Runtime version manager is not bound to the kernel."
        )

    manager = kernel.get_component(
        RUNTIME_VERSION_MANAGER_KEY
    )
    manifest = getattr(manager, "manifest", None)

    if manifest is None:
        raise RuntimeRegistrationAdmissionError(
            "Runtime version manager has no manifest."
        )

    return manifest


def _requirement_from_public_record(
    contract_key: str,
    value: Any,
) -> RuntimeVersionRequirement:
    if isinstance(value, RuntimeVersionRequirement):
        requirement = value
    elif isinstance(value, Mapping):
        record_contract = _optional_text(
            value.get("contract")
        ) or contract_key

        maximum_exclusive = value.get(
            "maximum_exclusive"
        )

        requirement = RuntimeVersionRequirement(
            contract=record_contract,
            mode=RuntimeCompatibilityMode(
                str(value.get("mode") or "").strip()
            ),
            expected_version=RuntimeSemanticVersion.parse(
                value.get("expected_version")
            ),
            maximum_exclusive=(
                None
                if maximum_exclusive is None
                else RuntimeSemanticVersion.parse(
                    maximum_exclusive
                )
            ),
            allow_prerelease=bool(
                value.get("allow_prerelease", False)
            ),
            required=bool(
                value.get("required", True)
            ),
            description=_optional_text(
                value.get("description")
            ),
        )
    else:
        raise RuntimeRegistrationAdmissionError(
            "runtime_version_requirements values must be "
            "RuntimeVersionRequirement records."
        )

    if requirement.contract != contract_key:
        raise RuntimeRegistrationAdmissionError(
            "Runtime version requirement key does not match its "
            f"contract: {contract_key!r} != "
            f"{requirement.contract!r}"
        )

    return requirement


def _require_versions(
    requirements: Mapping[str, Any],
    *,
    job_type: str,
    kernel: Any,
) -> dict[str, Any]:
    resolved = tuple(
        _requirement_from_public_record(
            str(contract_key),
            value,
        )
        for contract_key, value in requirements.items()
    )

    if not resolved:
        return {
            "contracts": [],
            "manifest_fingerprint": None,
            "policy_fingerprint": None,
        }

    policy = RuntimeCompatibilityPolicy(
        policy_name=(
            "runtime.registration."
            + job_type.replace(":", ".")
        )[:128],
        policy_version=RuntimeSemanticVersion.parse(
            "1.0.0"
        ),
        strict=True,
        requirements=resolved,
    )

    layer = RuntimeCompatibilityLayer(policy)
    report = layer.require_compatible(
        _runtime_manifest(kernel)
    )

    return {
        "contracts": [
            item.contract
            for item in report.results
        ],
        "manifest_fingerprint": (
            report.manifest_fingerprint
        ),
        "policy_fingerprint": (
            report.policy_fingerprint
        ),
    }


def _require_feature_flag(
    feature_flag_key: str,
    *,
    runtime_job: Mapping[str, Any],
    worker_id: str,
    kernel: Any,
) -> dict[str, Any]:
    if not kernel.has_component(
        FEATURE_FLAG_GATEWAY_KEY
    ):
        raise RuntimeRegistrationAdmissionError(
            "Runtime feature-flag gateway is not bound to the kernel."
        )

    gateway = kernel.get_component(
        FEATURE_FLAG_GATEWAY_KEY
    )
    manifest = _runtime_manifest(kernel)

    decision = gateway.evaluate(
        feature_flag_key,
        evaluation_key=(
            str(runtime_job.get("job_id") or worker_id)
        ),
        workspace_id=_optional_text(
            runtime_job.get("workspace_id")
        ),
        worker_class="universal_runtime_worker",
        runtime_version=str(
            manifest.runtime_version
        ),
        attributes={
            "job_type": str(
                runtime_job.get("job_type") or ""
            ),
            "pipeline": str(
                runtime_job.get("pipeline") or ""
            ),
            "stage": str(
                runtime_job.get("stage") or ""
            ),
        },
        actor="runtime_registration_admission",
    )

    reason = getattr(
        getattr(decision, "reason", None),
        "value",
        getattr(decision, "reason", None),
    )

    if not (
        decision.enabled is True
        and decision.reason
        is RuntimeFeatureFlagDecisionReason.ENABLED
    ):
        raise RuntimeRegistrationAdmissionError(
            "Registration feature flag denied execution: "
            f"{feature_flag_key!r}; reason={reason!r}"
        )

    return {
        "feature_flag_key": feature_flag_key,
        "enabled": True,
        "reason": reason,
        "flag_fingerprint": getattr(
            decision,
            "flag_fingerprint",
            None,
        ),
    }


def require_runtime_registration_admission(
    *,
    registration: Mapping[str, Any],
    runtime_job: Mapping[str, Any],
    worker_id: str,
) -> RuntimeRegistrationAdmissionReport:
    if not isinstance(registration, Mapping):
        raise RuntimeRegistrationAdmissionError(
            "Runtime registration must be a mapping."
        )

    if not isinstance(runtime_job, Mapping):
        raise RuntimeRegistrationAdmissionError(
            "Runtime job must be a mapping."
        )

    job_type = _optional_text(
        registration.get("job_type")
    )

    if job_type is None:
        raise RuntimeRegistrationAdmissionError(
            "Runtime registration has no job_type."
        )

    lifecycle_policy = _mapping(
        registration,
        "lifecycle_policy",
    )
    configuration_requirements = _mapping(
        registration,
        "configuration_requirements",
    )
    version_requirements = _mapping(
        registration,
        "runtime_version_requirements",
    )
    feature_flag_key = _optional_text(
        registration.get("feature_flag_key")
    )

    declared_policy = bool(
        lifecycle_policy
        or configuration_requirements
        or version_requirements
        or feature_flag_key
    )

    binding = _current_binding()

    if binding is None:
        if declared_policy:
            raise RuntimeRegistrationAdmissionError(
                "Registration policy authority is not bound."
            )

        return RuntimeRegistrationAdmissionReport(
            schema_version=(
                REGISTRATION_ADMISSION_SCHEMA_VERSION
            ),
            admitted=True,
            job_type=job_type,
            lifecycle_checked=False,
            configuration_checked=False,
            feature_flag_checked=False,
            version_compatibility_checked=False,
            feature_flag_key=None,
            evaluated_contracts=(),
            evidence=MappingProxyType(
                {
                    "reason": "no_policy_declared",
                }
            ),
        )

    configuration, kernel = binding
    evidence: dict[str, Any] = {}

    if lifecycle_policy:
        evidence["lifecycle"] = _require_lifecycle_policy(
            lifecycle_policy,
            configuration=configuration,
            kernel=kernel,
        )

    if configuration_requirements:
        evidence["configuration"] = _require_configuration(
            configuration_requirements,
            configuration=configuration,
        )

    version_evidence = None

    if version_requirements:
        version_evidence = _require_versions(
            version_requirements,
            job_type=job_type,
            kernel=kernel,
        )
        evidence["version_compatibility"] = version_evidence

    if feature_flag_key:
        evidence["feature_flag"] = _require_feature_flag(
            feature_flag_key,
            runtime_job=runtime_job,
            worker_id=worker_id,
            kernel=kernel,
        )

    evaluated_contracts = (
        ()
        if version_evidence is None
        else tuple(
            version_evidence["contracts"]
        )
    )

    return RuntimeRegistrationAdmissionReport(
        schema_version=(
            REGISTRATION_ADMISSION_SCHEMA_VERSION
        ),
        admitted=True,
        job_type=job_type,
        lifecycle_checked=bool(lifecycle_policy),
        configuration_checked=bool(
            configuration_requirements
        ),
        feature_flag_checked=feature_flag_key is not None,
        version_compatibility_checked=bool(
            version_requirements
        ),
        feature_flag_key=feature_flag_key,
        evaluated_contracts=evaluated_contracts,
        evidence=MappingProxyType(evidence),
    )


__all__ = [
    "REGISTRATION_ADMISSION_SCHEMA_VERSION",
    "RuntimeRegistrationAdmissionError",
    "RuntimeRegistrationAdmissionReport",
    "bind_runtime_registration_admission",
    "clear_runtime_registration_admission_binding",
    "require_runtime_registration_admission",
]
'''


def patch_gateway(source: str) -> str:
    import_anchor = (
        "from backend.server.runtime."
        "universal_runtime_registration import ("
    )

    if source.count(import_anchor) != 1:
        fail(
            "Expected one registration gateway import anchor, "
            f"found {source.count(import_anchor)}."
        )

    admission_import = '''from backend.server.runtime.runtime_registration_admission import (
    bind_runtime_registration_admission,
)

'''

    source = source.replace(
        import_anchor,
        admission_import + import_anchor,
        1,
    )

    registrar_anchor = '''    ensure_persisted_runtime_registrations_loaded()

    gateway = RuntimeRegistrationGateway()
'''

    if source.count(registrar_anchor) != 1:
        fail(
            "Expected one registration registrar activation anchor, "
            f"found {source.count(registrar_anchor)}."
        )

    registrar_replacement = '''    ensure_persisted_runtime_registrations_loaded()

    bind_runtime_registration_admission(
        configuration=composition.configuration,
        kernel=kernel,
    )

    gateway = RuntimeRegistrationGateway()
'''

    source = source.replace(
        registrar_anchor,
        registrar_replacement,
        1,
    )

    ast.parse(source)

    return source


def patch_worker(source: str) -> str:
    function_anchor = (
        "def run_one_universal_runtime_job_v1("
    )

    if source.count(function_anchor) != 1:
        fail(
            "Expected one canonical worker function, "
            f"found {source.count(function_anchor)}."
        )

    admission_import = '''from backend.server.runtime.runtime_registration_admission import (
    RuntimeRegistrationAdmissionError,
    require_runtime_registration_admission,
)


'''

    source = source.replace(
        function_anchor,
        admission_import + function_anchor,
        1,
    )

    enforcement_anchor = '''        registration_metadata = registration.get("metadata", {})
'''

    if source.count(enforcement_anchor) != 1:
        fail(
            "Expected one worker registration-metadata anchor, "
            f"found {source.count(enforcement_anchor)}."
        )

    enforcement_block = '''        try:
            registration_admission = (
                require_runtime_registration_admission(
                    registration=registration,
                    runtime_job=runtime_job,
                    worker_id=canonical_worker_id,
                )
            )
        except RuntimeRegistrationAdmissionError as exc:
            raise UniversalRuntimeWorkerContractError(
                "Runtime registration admission failed: "
                + str(exc)
            ) from exc

        if not registration_admission.admitted:
            raise UniversalRuntimeWorkerContractError(
                "Runtime registration admission was not granted."
            )

        registration_metadata = registration.get("metadata", {})
'''

    source = source.replace(
        enforcement_anchor,
        enforcement_block,
        1,
    )

    tree = ast.parse(source)

    worker_function = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name
            == "run_one_universal_runtime_job_v1"
        ),
        None,
    )

    if worker_function is None:
        fail("Patched canonical worker was not found.")

    calls: list[tuple[str, int]] = []

    for node in ast.walk(worker_function):
        if not isinstance(node, ast.Call):
            continue

        if isinstance(node.func, ast.Name):
            calls.append((node.func.id, node.lineno))
        elif isinstance(node.func, ast.Attribute):
            calls.append((node.func.attr, node.lineno))

    lookup = [
        line
        for name, line in calls
        if name == "get_runtime_registration"
    ]
    admission = [
        line
        for name, line in calls
        if name == "require_runtime_registration_admission"
    ]
    capability = [
        line
        for name, line in calls
        if name == "match_universal_worker_capabilities"
    ]
    dispatch = [
        line
        for name, line in calls
        if name in {
            "dispatcher",
            "dispatch_registered_runtime_handler",
        }
    ]

    if not (
        len(lookup) == 1
        and len(admission) == 1
        and len(capability) == 1
        and len(dispatch) == 1
        and lookup[0] < admission[0]
        and admission[0] < capability[0]
        and admission[0] < dispatch[0]
    ):
        fail(
            "Registration admission was not placed in the required "
            "execution order: "
            f"lookup={lookup}, admission={admission}, "
            f"capability={capability}, dispatch={dispatch}"
        )

    return source


gateway_source = gateway_path.read_text(encoding="utf-8-sig")
worker_source = worker_path.read_text(encoding="utf-8-sig")

gateway_patched = patch_gateway(
    gateway_source.replace("\r\n", "\n")
)
worker_patched = patch_worker(
    worker_source.replace("\r\n", "\n")
)

admission_candidate.write_text(
    admission_source,
    encoding="utf-8",
)
gateway_candidate.write_text(
    gateway_patched,
    encoding="utf-8",
)
worker_candidate.write_text(
    worker_patched,
    encoding="utf-8",
)

for candidate in (
    admission_candidate,
    gateway_candidate,
    worker_candidate,
):
    py_compile.compile(
        str(candidate),
        doraise=True,
    )

print("ADMISSION_AUTHORITY_CANDIDATE_CREATED: PASS")
print(f"  {admission_candidate}")
print("REGISTRATION_GATEWAY_CANDIDATE_CREATED: PASS")
print(f"  {gateway_candidate}")
print("WORKER_CANDIDATE_CREATED: PASS")
print(f"  {worker_candidate}")
print("ALL_CANDIDATE_SYNTAX: PASS")
print("LIFECYCLE_POLICY_ENFORCEMENT_ADDED: PASS")
print("CONFIGURATION_REQUIREMENT_ENFORCEMENT_ADDED: PASS")
print("FEATURE_FLAG_ENFORCEMENT_ADDED: PASS")
print("VERSION_COMPATIBILITY_ENFORCEMENT_ADDED: PASS")
print("ADMISSION_PRECEDES_CAPABILITY_AND_DISPATCH: PASS")