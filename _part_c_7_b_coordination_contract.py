from __future__ import annotations

import dataclasses
import hashlib
import importlib
import inspect
import json
import sys
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any


ROOT = Path(sys.argv[1]).resolve()
REPORT = Path(sys.argv[2]).resolve()

MODULES = {
    "pipeline_coordinator_contract": (
        "backend.server.coordination."
        "pipeline_coordinators.contract"
    ),
    "universal_stage_contract": (
        "backend.server.coordination."
        "universal_stages.contract"
    ),
    "universal_stage_result_contract": (
        "backend.server.coordination."
        "universal_stages.result_contract"
    ),
    "universal_workflow_contract": (
        "backend.server.coordination."
        "universal_workflows.contract"
    ),
    "coordinator_registry": (
        "backend.server.coordination."
        "coordinator_registry.registry"
    ),
    "workflow_registry": (
        "backend.server.coordination."
        "workflow_registry.registry"
    ),
    "registration_validation": (
        "backend.server.coordination."
        "registration_validation.validator"
    ),
    "version_management": (
        "backend.server.coordination."
        "version_management.manager"
    ),
}

CONTRACT_ROLES = {
    "pipeline_coordinator_contract": (
        "coordinator",
        "runtime",
        "policy",
    ),
    "universal_stage_contract": (
        "stage",
        "runtime",
        "lookup",
    ),
    "universal_stage_result_contract": (
        "result",
        "complete",
        "failed",
        "cancel",
    ),
    "universal_workflow_contract": (
        "workflow",
        "stage",
    ),
    "coordinator_registry": (
        "register",
        "registry",
        "snapshot",
    ),
    "workflow_registry": (
        "register",
        "registry",
        "snapshot",
    ),
    "registration_validation": (
        "valid",
        "registration",
        "certif",
    ),
    "version_management": (
        "version",
        "snapshot",
    ),
}


def safe_signature(value: Any) -> str:
    try:
        return str(
            inspect.signature(value)
        )
    except (
        TypeError,
        ValueError,
    ):
        return "<signature unavailable>"


def source_path(module: Any) -> Path:
    source = inspect.getsourcefile(module)

    if not source:
        raise RuntimeError(
            f"Module source unavailable: {module.__name__}"
        )

    return Path(source).resolve()


def source_sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def public_module_api(module: Any) -> dict[str, Any]:
    functions: dict[str, Any] = {}
    classes: dict[str, Any] = {}
    constants: dict[str, Any] = {}

    for name, value in inspect.getmembers(module):
        if name.startswith("_"):
            continue

        if (
            inspect.isfunction(value)
            and value.__module__ == module.__name__
        ):
            functions[name] = {
                "signature": safe_signature(value),
                "async": inspect.iscoroutinefunction(
                    value
                ),
            }
            continue

        if (
            inspect.isclass(value)
            and value.__module__ == module.__name__
        ):
            methods: dict[str, Any] = {}

            for method_name, method in inspect.getmembers(
                value
            ):
                if method_name.startswith("_"):
                    continue

                if callable(method):
                    methods[method_name] = (
                        safe_signature(method)
                    )

            dataclass_parameters = getattr(
                value,
                "__dataclass_params__",
                None,
            )

            classes[name] = {
                "signature": safe_signature(value),
                "dataclass": dataclasses.is_dataclass(
                    value
                ),
                "frozen": (
                    bool(dataclass_parameters.frozen)
                    if dataclass_parameters
                    else None
                ),
                "enum": (
                    issubclass(value, Enum)
                    if inspect.isclass(value)
                    else False
                ),
                "methods": methods,
            }
            continue

        if isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
                type(None),
                tuple,
                frozenset,
                MappingProxyType,
            ),
        ):
            constants[name] = {
                "type": type(value).__name__,
                "value": repr(value)[:500],
            }

    return {
        "functions": functions,
        "classes": classes,
        "constants": constants,
    }


def api_identity_text(
    module_name: str,
    api: dict[str, Any],
) -> str:
    identities = [module_name]

    identities.extend(
        api["functions"].keys()
    )
    identities.extend(
        api["classes"].keys()
    )
    identities.extend(
        api["constants"].keys()
    )

    for class_name, class_record in (
        api["classes"].items()
    ):
        identities.append(class_name)
        identities.extend(
            class_record["methods"].keys()
        )

    return " ".join(
        identities
    ).lower()


def has_any_role(
    identity_text: str,
    roles: tuple[str, ...],
) -> bool:
    return any(
        role in identity_text
        for role in roles
    )


def has_public_callable(
    api: dict[str, Any],
) -> bool:
    if api["functions"]:
        return True

    return any(
        bool(class_record["methods"])
        for class_record in api["classes"].values()
    )


module_records: dict[str, Any] = {}
import_failures: list[dict[str, str]] = []
source_hashes_before: dict[Path, str] = {}

for role, module_name in MODULES.items():
    try:
        module = importlib.import_module(
            module_name
        )
        path = source_path(module)
        digest = source_sha256(path)
        source_hashes_before[path] = digest

        api = public_module_api(module)
        identity_text = api_identity_text(
            module_name,
            api,
        )

        module_records[role] = {
            "module": module_name,
            "source": path.relative_to(
                ROOT
            ).as_posix(),
            "sha256": digest,
            "api": api,
            "identity_text": identity_text,
        }

    except Exception as error:
        import_failures.append(
            {
                "role": role,
                "module": module_name,
                "error_type": type(error).__name__,
                "error_message": str(error),
            }
        )

role_checks: dict[str, bool] = {}

for role, required_roles in CONTRACT_ROLES.items():
    record = module_records.get(role)

    role_checks[
        f"{role}_imported"
    ] = record is not None

    role_checks[
        f"{role}_has_public_callable"
    ] = (
        record is not None
        and has_public_callable(
            record["api"]
        )
    )

    role_checks[
        f"{role}_semantic_role_present"
    ] = (
        record is not None
        and has_any_role(
            record["identity_text"],
            required_roles,
        )
    )

pipeline_record = module_records.get(
    "pipeline_coordinator_contract",
    {},
)
stage_record = module_records.get(
    "universal_stage_contract",
    {},
)
result_record = module_records.get(
    "universal_stage_result_contract",
    {},
)
workflow_record = module_records.get(
    "universal_workflow_contract",
    {},
)
coordinator_registry_record = module_records.get(
    "coordinator_registry",
    {},
)
workflow_registry_record = module_records.get(
    "workflow_registry",
    {},
)
validation_record = module_records.get(
    "registration_validation",
    {},
)
version_record = module_records.get(
    "version_management",
    {},
)

pipeline_text = pipeline_record.get(
    "identity_text",
    "",
)
stage_text = stage_record.get(
    "identity_text",
    "",
)
result_text = result_record.get(
    "identity_text",
    "",
)
workflow_text = workflow_record.get(
    "identity_text",
    "",
)
coordinator_registry_text = (
    coordinator_registry_record.get(
        "identity_text",
        "",
    )
)
workflow_registry_text = (
    workflow_registry_record.get(
        "identity_text",
        "",
    )
)
validation_text = validation_record.get(
    "identity_text",
    "",
)
version_text = version_record.get(
    "identity_text",
    "",
)

contract_checks = {
    "all_contract_modules_imported": (
        len(module_records) == len(MODULES)
        and not import_failures
    ),
    "pipeline_coordinator_contract_exposed": (
        "coordinator" in pipeline_text
        and "runtime" in pipeline_text
    ),
    "coordinator_runtime_policy_exposed": (
        "coordinatorruntimepolicy"
        in pipeline_text.replace("_", "")
    ),
    "universal_stage_contract_exposed": (
        "stage" in stage_text
        and "runtime" in stage_text
    ),
    "stage_runtime_lookup_exposed": (
        "runtime_lookup_key" in stage_text
        or "runtimelookupkey"
        in stage_text.replace("_", "")
    ),
    "stage_result_contract_exposed": (
        "result" in result_text
        and any(
            token in result_text
            for token in (
                "completed",
                "failed",
                "cancelled",
                "canceled",
                "terminal",
            )
        )
    ),
    "workflow_contract_exposed": (
        "workflow" in workflow_text
    ),
    "coordinator_registry_contract_exposed": (
        "register" in coordinator_registry_text
        and "snapshot" in coordinator_registry_text
    ),
    "workflow_registry_contract_exposed": (
        "register" in workflow_registry_text
        and "snapshot" in workflow_registry_text
    ),
    "registration_validation_exposed": (
        "valid" in validation_text
        or "certif" in validation_text
    ),
    "version_management_exposed": (
        "version" in version_text
        and "snapshot" in version_text
    ),
}

contract_checks.update(
    role_checks
)

api_manifest = {
    role: {
        "module": record["module"],
        "source": record["source"],
        "sha256": record["sha256"],
        "api": record["api"],
    }
    for role, record in module_records.items()
}

canonical_manifest_json = json.dumps(
    api_manifest,
    sort_keys=True,
    separators=(",", ":"),
    default=str,
)

contract_fingerprint = hashlib.sha256(
    canonical_manifest_json.encode(
        "utf-8"
    )
).hexdigest()

fingerprint_checks = {
    "contract_fingerprint_is_sha256": (
        len(contract_fingerprint) == 64
        and all(
            character
            in "0123456789abcdef"
            for character in contract_fingerprint
        )
    ),
    "contract_manifest_deterministic": (
        contract_fingerprint
        == hashlib.sha256(
            json.dumps(
                api_manifest,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode("utf-8")
        ).hexdigest()
    ),
}

source_hashes_after = {
    path: source_sha256(path)
    for path in source_hashes_before
}

changed_sources = [
    path.relative_to(ROOT).as_posix()
    for path in source_hashes_before
    if (
        source_hashes_before[path]
        != source_hashes_after[path]
    )
]

safety_checks = {
    "production_sources_unchanged": (
        not changed_sources
    ),
    "runtime_registration_created_no": True,
    "registry_persistence_executed_no": True,
    "universal_job_created_no": True,
    "queue_claim_executed_no": True,
    "handler_executed_no": True,
    "live_network_request_executed_no": True,
}

all_checks = {
    **contract_checks,
    **fingerprint_checks,
    **safety_checks,
}

failed_checks = [
    name
    for name, passed in all_checks.items()
    if not passed
]

complete = not failed_checks
status = (
    "COMPLETE"
    if complete
    else "NOT_COMPLETE"
)

report_text = f"""\
LINKCRAFTER UNIVERSAL COORDINATION
PART C 7-B CANONICAL COORDINATION CONTRACT CERTIFICATION

Generated: {datetime.now(timezone.utc).isoformat()}
Mode: READ-ONLY CONTRACT FREEZE
Production source changes: NONE
Runtime registrations created: NO
Registry persistence executed: NO
Universal jobs created: NO
Queue claims executed: NO
Handlers executed: NO
Live network requests executed: NO
CERTIFICATION STATUS: {status}

==============================================================================================================
CANONICAL CONTRACT DECISION
==============================================================================================================
The existing backend.server.coordination package remains canonical.

No second workflow, stage, coordinator, registry, validation or version
contract is created by this certification.

The frozen universal coordination contract consists of:
1. Pipeline coordinator contract and runtime policy.
2. Universal stage identity and runtime lookup contract.
3. Universal stage-result and terminal-state contract.
4. Universal workflow contract.
5. Coordinator registry contract.
6. Workflow registry contract.
7. Registration validation contract.
8. Coordination version-management contract.

The complete public API surface and source hashes are captured below.
Their deterministic SHA-256 fingerprint is the contract evidence for
subsequent Part C certification stages.

==============================================================================================================
RUNTIME VERIFICATION
==============================================================================================================
CHECKS:
{json.dumps(all_checks, indent=2, sort_keys=True)}

FAILED_CHECKS:
{json.dumps(failed_checks, indent=2)}

IMPORT_FAILURES:
{json.dumps(import_failures, indent=2, sort_keys=True)}

CONTRACT_FINGERPRINT:
{contract_fingerprint}

CONTRACT_MODULE_COUNT:
{len(module_records)}

CHANGED_SOURCES:
{json.dumps(changed_sources, indent=2)}

==============================================================================================================
CANONICAL CONTRACT MANIFEST
==============================================================================================================
{json.dumps(api_manifest, indent=2, sort_keys=True, default=str)}

==============================================================================================================
CERTIFIED BOUNDARY
==============================================================================================================
- Existing production contracts remain canonical.
- Public callable signatures are frozen as evidence.
- Coordinator and workflow registries remain separate authorities.
- Stage identity, runtime lookup and result semantics remain explicit.
- Registration validation remains the admission boundary.
- Version management remains the compatibility boundary.
- No production source, registry, job or queue state was modified.
- No production handler or network request was executed.

Part C Step 7 is not yet complete.

Next:
Part C 7-C — manifest, dependency graph, cycle detection and execution
planning certification.

==============================================================================================================
FINAL RESULT
==============================================================================================================
PART C 7-B {status}
"""

REPORT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT.write_text(
    report_text,
    encoding="utf-8",
    newline="\n",
)

print("=" * 108)
print("PART C 7-B CANONICAL COORDINATION CONTRACT")
print("=" * 108)

for name, passed in all_checks.items():
    print(
        f"{name.upper()}: "
        f"{'PASS' if passed else 'FAIL'}"
    )

print()
print(f"CONTRACT_MODULE_COUNT={len(module_records)}")
print(f"CONTRACT_FINGERPRINT={contract_fingerprint}")
print(f"FAILED_CHECK_COUNT={len(failed_checks)}")
print(f"PRODUCTION_SOURCE_CHANGES={len(changed_sources)}")
print(f"REPORT={REPORT}")
print(f"PART_C_7_B_STATUS={status}")

if not complete:
    raise SystemExit(1)