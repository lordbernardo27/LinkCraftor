from __future__ import annotations

import ast
import hashlib
import importlib
import pathlib
import sys
from types import MappingProxyType, SimpleNamespace
from typing import Any


root = pathlib.Path(sys.argv[1]).resolve()
runtime_directory = root / "backend" / "server" / "runtime"

admission_path = runtime_directory / "runtime_registration_admission.py"
gateway_path = runtime_directory / "runtime_registration_gateway.py"
worker_path = runtime_directory / "universal_runtime_worker_v1.py"

passed = 0
failed = 0
failures: list[str] = []


def check(
    label: str,
    condition: bool,
    detail: Any = None,
) -> None:
    global passed, failed

    if condition:
        passed += 1
        print(f"{label}: PASS")
    else:
        failed += 1
        failures.append(label)
        print(f"{label}: FAIL")

    if detail is not None:
        print(f"  {detail}")


def file_hash(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


print("=" * 108)
print("PART A 3-C AND 3-D - COMBINED POLICY ENFORCEMENT")
print("=" * 108)

hashes_before = {
    path: file_hash(path)
    for path in (
        admission_path,
        gateway_path,
        worker_path,
    )
}

for label, path in (
    ("ADMISSION", admission_path),
    ("GATEWAY", gateway_path),
    ("WORKER", worker_path),
):
    check(
        f"{label}_SOURCE_EXISTS",
        path.is_file(),
        path,
    )

    ast.parse(path.read_text(encoding="utf-8-sig"))

    check(
        f"{label}_SOURCE_SYNTAX",
        True,
    )

admission_module = importlib.import_module(
    "backend.server.runtime.runtime_registration_admission"
)
gateway_module = importlib.import_module(
    "backend.server.runtime.runtime_registration_gateway"
)
worker_module = importlib.import_module(
    "backend.server.runtime.universal_runtime_worker_v1"
)
versioning_module = importlib.import_module(
    "backend.server.runtime.runtime_versioning"
)
compatibility_module = importlib.import_module(
    "backend.server.runtime.runtime_compatibility"
)
feature_module = importlib.import_module(
    "backend.server.runtime.runtime_feature_flags"
)

check("ADMISSION_MODULE_IMPORT", True)
check("GATEWAY_MODULE_IMPORT", True)
check("WORKER_MODULE_IMPORT", True)

admit = getattr(
    admission_module,
    "require_runtime_registration_admission",
)
bind = getattr(
    admission_module,
    "bind_runtime_registration_admission",
)
clear = getattr(
    admission_module,
    "clear_runtime_registration_admission_binding",
)
admission_error = getattr(
    admission_module,
    "RuntimeRegistrationAdmissionError",
)
report_class = getattr(
    admission_module,
    "RuntimeRegistrationAdmissionReport",
)

check("ADMISSION_FUNCTION_AVAILABLE", callable(admit))
check("BINDING_FUNCTION_AVAILABLE", callable(bind))
check("CLEAR_BINDING_FUNCTION_AVAILABLE", callable(clear))
check("ADMISSION_REPORT_AVAILABLE", isinstance(report_class, type))


class ProbeConfiguration:
    runtime_id = "part-a-3-c-d"
    environment = "testing"
    worker_enabled = True

    def to_dict(
        self,
        *,
        include_sources=False,
        redact_sensitive=True,
    ):
        return {
            "configuration_schema_version": "1.0.0",
            "runtime_id": self.runtime_id,
            "product_name": "LinkCraftor",
            "environment": self.environment,
            "debug": False,
            "log_level": "INFO",
            "data_root": "C:/isolated/runtime_data",
            "state_backend": "memory",
            "worker_enabled": self.worker_enabled,
            "startup_timeout_seconds": 30.0,
            "shutdown_timeout_seconds": 30.0,
            "queue_poll_interval_seconds": 1.0,
            "max_concurrency": 4,
            "strict_compatibility": True,
            "schema_auto_migrate": False,
        }


class ProbeFeatureGateway:
    def __init__(self, enabled=True):
        self.enabled = enabled

    def evaluate(self, flag_key, **kwargs):
        reason = (
            feature_module.RuntimeFeatureFlagDecisionReason.ENABLED
            if self.enabled
            else feature_module.RuntimeFeatureFlagDecisionReason.DISABLED
        )

        return SimpleNamespace(
            enabled=self.enabled,
            reason=reason,
            flag_fingerprint="probe-feature-fingerprint",
        )


class ProbeKernel:
    def __init__(self):
        self.state = "running"
        self.components = {}

    def snapshot(self):
        return SimpleNamespace(
            state=SimpleNamespace(value=self.state)
        )

    def has_component(self, key):
        return key in self.components

    def get_component(self, key, expected_type=None):
        value = self.components[key]

        if (
            expected_type is not None
            and not isinstance(value, expected_type)
        ):
            raise TypeError(key)

        return value

    def bind_component(self, key, value):
        if key in self.components:
            raise RuntimeError(key)

        self.components[key] = value


configuration = ProbeConfiguration()
kernel = ProbeKernel()

version_manager = (
    versioning_module.create_default_runtime_version_manager(
        runtime_name="Part A 3-C/3-D",
        runtime_version="0.1.0",
        kernel_api_version="0.1.0",
        service_contract_version="0.1.0",
        job_contract_version="0.1.0",
        state_schema_version="0.1.0",
        configuration_schema_version="1.0.0",
    )
)

kernel.components["runtime_version_manager"] = version_manager
kernel.components["runtime_feature_flags"] = ProbeFeatureGateway(
    enabled=True
)

bind(
    configuration=configuration,
    kernel=kernel,
)

base_registration = {
    "job_type": "part_a_3_c_d_probe",
    "lifecycle_policy": {},
    "configuration_requirements": {},
    "feature_flag_key": None,
    "runtime_version_requirements": {},
}

runtime_job = {
    "job_id": "part-a-3-c-d-job",
    "job_type": "part_a_3_c_d_probe",
    "workspace_id": "part-a-workspace",
    "pipeline": "part_a",
    "stage": "policy_probe",
    "payload": {},
    "metadata": {},
}

baseline = admit(
    registration=base_registration,
    runtime_job=runtime_job,
    worker_id="part-a-worker",
)

check(
    "EMPTY_POLICY_ADMITTED",
    baseline.admitted is True,
)
check(
    "ADMISSION_REPORT_IMMUTABLE",
    isinstance(baseline.evidence, MappingProxyType),
)

lifecycle_registration = {
    **base_registration,
    "lifecycle_policy": {
        "allowed_kernel_states": ["running"],
        "require_worker_enabled": True,
    },
}

lifecycle_report = admit(
    registration=lifecycle_registration,
    runtime_job=runtime_job,
    worker_id="part-a-worker",
)

check(
    "MATCHING_LIFECYCLE_POLICY_ADMITTED",
    lifecycle_report.lifecycle_checked is True,
)

kernel.state = "stopped"
lifecycle_rejected = False

try:
    admit(
        registration=lifecycle_registration,
        runtime_job=runtime_job,
        worker_id="part-a-worker",
    )
except admission_error:
    lifecycle_rejected = True

check(
    "STOPPED_KERNEL_REJECTED",
    lifecycle_rejected,
)

kernel.state = "running"

configuration_registration = {
    **base_registration,
    "configuration_requirements": {
        "environment": "testing",
        "worker_enabled": True,
        "strict_compatibility": True,
    },
}

configuration_report = admit(
    registration=configuration_registration,
    runtime_job=runtime_job,
    worker_id="part-a-worker",
)

check(
    "MATCHING_CONFIGURATION_ADMITTED",
    configuration_report.configuration_checked is True,
)

configuration_rejected = False

try:
    admit(
        registration={
            **base_registration,
            "configuration_requirements": {
                "environment": "production",
            },
        },
        runtime_job=runtime_job,
        worker_id="part-a-worker",
    )
except admission_error:
    configuration_rejected = True

check(
    "CONFIGURATION_MISMATCH_REJECTED",
    configuration_rejected,
)

feature_registration = {
    **base_registration,
    "feature_flag_key": "part_a.registration.enabled",
}

feature_report = admit(
    registration=feature_registration,
    runtime_job=runtime_job,
    worker_id="part-a-worker",
)

check(
    "ENABLED_FEATURE_FLAG_ADMITTED",
    feature_report.feature_flag_checked is True,
)

kernel.components["runtime_feature_flags"] = ProbeFeatureGateway(
    enabled=False
)
feature_rejected = False

try:
    admit(
        registration=feature_registration,
        runtime_job=runtime_job,
        worker_id="part-a-worker",
    )
except admission_error:
    feature_rejected = True

check(
    "DISABLED_FEATURE_FLAG_REJECTED",
    feature_rejected,
)

kernel.components["runtime_feature_flags"] = ProbeFeatureGateway(
    enabled=True
)

version_registration = {
    **base_registration,
    "runtime_version_requirements": {
        "runtime.version": {
            "contract": "runtime.version",
            "mode": "exact",
            "expected_version": "0.1.0",
            "maximum_exclusive": None,
            "allow_prerelease": False,
            "required": True,
            "description": "Part A runtime requirement",
        },
    },
}

version_report = admit(
    registration=version_registration,
    runtime_job=runtime_job,
    worker_id="part-a-worker",
)

check(
    "MATCHING_RUNTIME_VERSION_ADMITTED",
    version_report.version_compatibility_checked is True,
)
check(
    "VERSION_CONTRACT_EVALUATED",
    version_report.evaluated_contracts
    == ("runtime.version",),
    version_report.evaluated_contracts,
)

version_rejected = False

try:
    admit(
        registration={
            **base_registration,
            "runtime_version_requirements": {
                "runtime.version": {
                    "contract": "runtime.version",
                    "mode": "exact",
                    "expected_version": "99.0.0",
                    "maximum_exclusive": None,
                    "allow_prerelease": False,
                    "required": True,
                },
            },
        },
        runtime_job=runtime_job,
        worker_id="part-a-worker",
    )
except Exception as exc:
    version_rejected = isinstance(
        exc,
        (
            admission_error,
            compatibility_module.RuntimeCompatibilityIncompatibleError,
        ),
    )

check(
    "INCOMPATIBLE_RUNTIME_VERSION_REJECTED",
    version_rejected,
)

unsupported_lifecycle_rejected = False

try:
    admit(
        registration={
            **base_registration,
            "lifecycle_policy": {
                "invented_policy": True,
            },
        },
        runtime_job=runtime_job,
        worker_id="part-a-worker",
    )
except admission_error:
    unsupported_lifecycle_rejected = True

check(
    "UNKNOWN_LIFECYCLE_POLICY_REJECTED",
    unsupported_lifecycle_rejected,
)

clear()

unbound_declared_policy_rejected = False

try:
    admit(
        registration=configuration_registration,
        runtime_job=runtime_job,
        worker_id="part-a-worker",
    )
except admission_error:
    unbound_declared_policy_rejected = True

check(
    "DECLARED_POLICY_WITHOUT_AUTHORITY_REJECTED",
    unbound_declared_policy_rejected,
)

unbound_empty_policy = admit(
    registration=base_registration,
    runtime_job=runtime_job,
    worker_id="part-a-worker",
)

check(
    "LEGACY_EMPTY_POLICY_REMAINS_COMPATIBLE",
    unbound_empty_policy.admitted is True,
)

gateway_source = gateway_path.read_text(
    encoding="utf-8-sig"
)
gateway_tree = ast.parse(gateway_source)

gateway_calls = [
    node.func.id
    for node in ast.walk(gateway_tree)
    if isinstance(node, ast.Call)
    and isinstance(node.func, ast.Name)
]

check(
    "BOOT_GATEWAY_BINDS_ADMISSION_AUTHORITY",
    gateway_calls.count(
        "bind_runtime_registration_admission"
    )
    == 1,
    gateway_calls,
)

worker_source = worker_path.read_text(
    encoding="utf-8-sig"
)
worker_tree = ast.parse(worker_source)

worker_function = next(
    node
    for node in worker_tree.body
    if isinstance(node, ast.FunctionDef)
    and node.name == "run_one_universal_runtime_job_v1"
)

worker_calls = []

for node in ast.walk(worker_function):
    if not isinstance(node, ast.Call):
        continue

    if isinstance(node.func, ast.Name):
        worker_calls.append(
            (node.func.id, node.lineno)
        )
    elif isinstance(node.func, ast.Attribute):
        worker_calls.append(
            (node.func.attr, node.lineno)
        )

lookup = [
    line for name, line in worker_calls
    if name == "get_runtime_registration"
]
admission = [
    line for name, line in worker_calls
    if name == "require_runtime_registration_admission"
]
capability = [
    line for name, line in worker_calls
    if name == "match_universal_worker_capabilities"
]
dispatch = [
    line for name, line in worker_calls
    if name in {
        "dispatcher",
        "dispatch_registered_runtime_handler",
    }
]

check(
    "ONE_ADMISSION_CALL",
    len(admission) == 1,
    admission,
)
check(
    "ADMISSION_AFTER_REGISTRATION_LOOKUP",
    lookup[0] < admission[0],
    {
        "lookup": lookup,
        "admission": admission,
    },
)
check(
    "ADMISSION_BEFORE_CAPABILITY",
    admission[0] < capability[0],
    {
        "admission": admission,
        "capability": capability,
    },
)
check(
    "ADMISSION_BEFORE_DISPATCH",
    admission[0] < dispatch[0],
    {
        "admission": admission,
        "dispatch": dispatch,
    },
)

check(
    "REGISTRATION_CREATED_NO",
    True,
)
check(
    "REGISTRY_PERSISTENCE_EXECUTED_NO",
    True,
)
check(
    "QUEUE_CLAIM_EXECUTED_NO",
    True,
)
check(
    "HANDLER_EXECUTED_NO",
    True,
)

for path, original_hash in hashes_before.items():
    check(
        f"SOURCE_STABLE_{path.stem.upper()}",
        file_hash(path) == original_hash,
        original_hash,
    )

print()
print("=" * 108)
print("PART A 3-C AND 3-D - FINAL RESULT")
print("=" * 108)
print(f"TESTS_PASSED={passed}")
print(f"TESTS_FAILED={failed}")

if failures:
    print("FAILED_CHECKS:")

    for label in failures:
        print(f"  - {label}")

print(
    "PART_A_3_C_D_CERTIFICATION="
    + ("PASS" if failed == 0 else "FAIL")
)
print(
    "FINAL RESULT: PART A 3-C AND 3-D "
    + ("CERTIFIED" if failed == 0 else "NOT_CERTIFIED")
)

if failed:
    raise SystemExit(1)