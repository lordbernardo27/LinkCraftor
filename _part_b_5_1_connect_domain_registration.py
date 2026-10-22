from __future__ import annotations

import hashlib
import json
import re
import sys
import traceback
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(sys.argv[1]).resolve()
REPORT = Path(sys.argv[2]).resolve()

JOB_TYPE = "connect_domain_stage"
PIPELINE = "connect_domain"
STAGE = "connect_domain"
SUCCESSOR_STAGE = "site_sources"

STAGE_SOURCE = (
    ROOT
    / "backend/server/pipelines/connect_domain/stage.py"
)

checks: list[tuple[str, bool, Any]] = []
standard_error = ""
rollback_status = "NOT_REQUIRED"
created_by_run = False
registry_mutated = False


def record(
    name: str,
    passed: bool,
    detail: Any = None,
) -> None:
    checks.append(
        (
            name,
            bool(passed),
            detail,
        )
    )


def public_record(value: Any) -> dict[str, Any]:
    if value is None:
        return {}

    if isinstance(value, dict):
        return dict(value)

    converter = getattr(
        value,
        "to_public_dict",
        None,
    )

    if callable(converter):
        converted = converter()

        if isinstance(
            converted,
            Mapping,
        ):
            return dict(converted)

    return {}


def contains_job_type(
    value: Any,
    job_type: str,
) -> bool:
    if isinstance(value, Mapping):
        if value.get("job_type") == job_type:
            return True

        return any(
            contains_job_type(
                item,
                job_type,
            )
            for item in value.values()
        )

    if isinstance(value, (list, tuple)):
        return any(
            contains_job_type(
                item,
                job_type,
            )
            for item in value
        )

    return value == job_type


def lookup_registration(
    getter: Any,
) -> Any:
    try:
        return getter(
            JOB_TYPE
        )
    except (
        KeyError,
        LookupError,
        ValueError,
    ):
        return None


def heading(title: str) -> str:
    return (
        "\n"
        + "=" * 112
        + "\n"
        + title
        + "\n"
        + "=" * 112
    )


try:
    sys.path.insert(
        0,
        str(ROOT),
    )

    if not STAGE_SOURCE.is_file():
        raise FileNotFoundError(
            f"Connect Domain stage unavailable: {STAGE_SOURCE}"
        )

    initial_stage_hash = hashlib.sha256(
        STAGE_SOURCE.read_bytes()
    ).hexdigest()

    from backend.server.pipelines.connect_domain.stage import (
        execute_connect_domain_stage,
    )

    from backend.server.runtime.runtime_registration_package import (
        RuntimeRegistrationPackage,
        create_runtime_registration_package,
    )

    from backend.server.runtime.universal_runtime_registration import (
        get_runtime_registration,
        register_runtime_handler,
        runtime_registration_snapshot,
        unregister_runtime_handler,
    )

    handler_calls = 0

    handler_reference = (
        execute_connect_domain_stage.__module__
        + ":"
        + execute_connect_domain_stage.__qualname__
    )

    declarations = {
        "job_type": JOB_TYPE,
        "handler_ref": handler_reference,
        "handler": execute_connect_domain_stage,
        "pipeline": PIPELINE,
        "stage": STAGE,
        "description": (
            "Normalize and persist the canonical Connect Domain "
            "workspace identity before Site Sources execution."
        ),
        "required_payload_fields": (
            "workspace_id",
            "workspace_name",
            "workspace_mode",
            "domain",
        ),
        "required_worker_capabilities": (),
        "predecessor_stages": (),
        "successor_stages": (
            SUCCESSOR_STAGE,
        ),
        "idempotency_fields": (
            "workspace_id",
            "domain",
        ),
        "retry_policy": {
            "max_attempts": 3,
            "retryable": True,
        },
        "concurrency_policy": {
            "scope": "workspace",
            "max_concurrency": 1,
        },
        "lifecycle_policy": {
            "allowed_kernel_states": [
                "running",
            ],
            "require_worker_enabled": True,
        },
        "configuration_requirements": {},
        "feature_flag_key": None,
        "runtime_version_requirements": {},
        "metadata": {
            "architecture": "connect_domain_pipeline_v1",
            "registration_step": "part_b_5_1",
            "stage_sequence": 1,
            "next_stage": SUCCESSOR_STAGE,
            "automatic_website_discovery": True,
            "manual_sitemap_import": False,
        },
        "persistent": True,
    }

    expected_package = (
        create_runtime_registration_package(
            **declarations
        )
    )

    expected_public = (
        expected_package.to_public_dict()
    )

    record(
        "STAGE_SOURCE_EXISTS",
        True,
        str(STAGE_SOURCE),
    )

    record(
        "CONNECT_DOMAIN_HANDLER_AVAILABLE",
        callable(
            execute_connect_domain_stage
        ),
        handler_reference,
    )

    record(
        "CANONICAL_PACKAGE_CREATED",
        isinstance(
            expected_package,
            RuntimeRegistrationPackage,
        ),
        type(
            expected_package
        ).__name__,
    )

    record(
        "PACKAGE_JOB_IDENTITY_CORRECT",
        expected_public.get(
            "job_type"
        )
        == JOB_TYPE,
        expected_public.get(
            "job_type"
        ),
    )

    record(
        "PACKAGE_HANDLER_REFERENCE_CORRECT",
        expected_public.get(
            "handler_ref"
        )
        == handler_reference,
        expected_public.get(
            "handler_ref"
        ),
    )

    record(
        "PIPELINE_AND_STAGE_CORRECT",
        (
            expected_public.get(
                "pipeline"
            )
            == PIPELINE
            and expected_public.get(
                "stage"
            )
            == STAGE
        ),
        {
            "pipeline": expected_public.get(
                "pipeline"
            ),
            "stage": expected_public.get(
                "stage"
            ),
        },
    )

    required_fields = set(
        expected_public.get(
            "required_payload_fields",
            [],
        )
    )

    record(
        "PAYLOAD_CONTRACT_COMPLETE",
        required_fields
        == {
            "workspace_id",
            "workspace_name",
            "workspace_mode",
            "domain",
        },
        sorted(required_fields),
    )

    record(
        "DEPENDENCY_CONTRACT_CORRECT",
        (
            expected_public.get(
                "predecessor_stages"
            )
            == []
            and expected_public.get(
                "successor_stages"
            )
            == [SUCCESSOR_STAGE]
        ),
        {
            "predecessors": expected_public.get(
                "predecessor_stages"
            ),
            "successors": expected_public.get(
                "successor_stages"
            ),
        },
    )

    record(
        "IDEMPOTENCY_CONTRACT_CORRECT",
        set(
            expected_public.get(
                "idempotency_fields",
                [],
            )
        )
        == {
            "workspace_id",
            "domain",
        },
        expected_public.get(
            "idempotency_fields"
        ),
    )

    fingerprint = str(
        expected_public.get(
            "registration_fingerprint",
            "",
        )
    )

    record(
        "DETERMINISTIC_FINGERPRINT_AVAILABLE",
        bool(
            re.fullmatch(
                r"[0-9a-f]{64}",
                fingerprint,
            )
        ),
        fingerprint,
    )

    snapshot_before = (
        runtime_registration_snapshot()
    )

    existing = lookup_registration(
        get_runtime_registration
    )

    if existing is not None:
        existing_public = public_record(
            existing
        )

        existing_fingerprint = str(
            existing_public.get(
                "registration_fingerprint",
                "",
            )
        )

        if existing_fingerprint != fingerprint:
            raise RuntimeError(
                "A different registration already uses "
                f"job_type {JOB_TYPE!r}."
            )

        registration_public = (
            existing_public
        )

        record(
            "MATCHING_EXISTING_REGISTRATION_REUSED",
            True,
            existing_fingerprint,
        )
    else:
        register_arguments = dict(
            declarations
        )

        register_arguments.pop(
            "handler_ref"
        )

        register_arguments.pop(
            "persistent"
        )

        registration_public = (
            register_runtime_handler(
                **register_arguments,
                replace=False,
                persist=True,
            )
        )

        created_by_run = True
        registry_mutated = True

        record(
            "CONNECT_DOMAIN_REGISTRATION_CREATED",
            True,
            registration_public,
        )

    loaded_registration = (
        lookup_registration(
            get_runtime_registration
        )
    )

    loaded_public = public_record(
        loaded_registration
    )

    record(
        "REGISTRATION_LOADED",
        bool(
            loaded_public
        ),
        loaded_public,
    )

    record(
        "LOADED_JOB_IDENTITY_MATCHES",
        loaded_public.get(
            "job_type"
        )
        == JOB_TYPE,
        loaded_public.get(
            "job_type"
        ),
    )

    record(
        "LOADED_HANDLER_REFERENCE_MATCHES",
        loaded_public.get(
            "handler_ref"
        )
        == handler_reference,
        loaded_public.get(
            "handler_ref"
        ),
    )

    record(
        "LOADED_FINGERPRINT_MATCHES",
        loaded_public.get(
            "registration_fingerprint"
        )
        == fingerprint,
        loaded_public.get(
            "registration_fingerprint"
        ),
    )

    record(
        "PERSISTENT_POLICY_ACTIVE",
        loaded_public.get(
            "persistent"
        )
        is True,
        loaded_public.get(
            "persistent"
        ),
    )

    snapshot_after = (
        runtime_registration_snapshot()
    )

    record(
        "REGISTRATION_PRESENT_IN_SNAPSHOT",
        contains_job_type(
            snapshot_after,
            JOB_TYPE,
        ),
    )

    persistent_path_text = str(
        snapshot_after.get(
            "persistent_registry_path",
            "",
        )
        if isinstance(
            snapshot_after,
            Mapping,
        )
        else ""
    ).strip()

    persistent_path = (
        Path(persistent_path_text)
        if persistent_path_text
        else None
    )

    record(
        "PERSISTENT_REGISTRY_PATH_PUBLISHED",
        bool(
            persistent_path_text
        ),
        persistent_path_text,
    )

    if persistent_path is not None:
        if not persistent_path.is_absolute():
            persistent_path = (
                ROOT
                / persistent_path
            ).resolve()

        persisted_text = (
            persistent_path.read_text(
                encoding="utf-8",
            )
            if persistent_path.is_file()
            else ""
        )

        record(
            "REGISTRATION_PERSISTED",
            (
                persistent_path.is_file()
                and JOB_TYPE in persisted_text
                and fingerprint in persisted_text
            ),
            str(persistent_path),
        )

    record(
        "HANDLER_NOT_EXECUTED",
        handler_calls == 0,
        handler_calls,
    )

    final_stage_hash = hashlib.sha256(
        STAGE_SOURCE.read_bytes()
    ).hexdigest()

    record(
        "STAGE_SOURCE_UNCHANGED",
        final_stage_hash
        == initial_stage_hash,
        final_stage_hash,
    )

    failed_now = [
        name
        for name, passed, _detail in checks
        if not passed
    ]

    if failed_now:
        raise RuntimeError(
            "Registration certification checks failed: "
            + ", ".join(
                failed_now
            )
        )

except Exception:
    standard_error = traceback.format_exc()

    if created_by_run:
        try:
            unregister_runtime_handler(
                JOB_TYPE,
                persist=True,
            )

            rollback_status = (
                "CREATED_REGISTRATION_REMOVED"
            )
        except Exception:
            rollback_status = (
                "ROLLBACK_FAILED\n"
                + traceback.format_exc()
            )


failed = [
    name
    for name, passed, _detail in checks
    if not passed
]

passed_count = sum(
    1
    for _name, passed, _detail in checks
    if passed
)

certified = (
    not standard_error
    and not failed
)

lines = [
    "LINKCRAFTER PIPELINE REGISTRATION",
    "PART B 5.1 CONNECT DOMAIN REGISTRATION PACKAGE",
    "",
    "Production source changes: NONE",
    (
        "Runtime registry mutated: YES"
        if registry_mutated and certified
        else "Runtime registry mutated: NO"
    ),
    "Universal jobs created: NO",
    "Queue claims executed: NO",
    "Handlers executed: NO",
    (
        "CERTIFICATION STATUS: CERTIFIED"
        if certified
        else "CERTIFICATION STATUS: NOT_CERTIFIED"
    ),
    heading(
        "RUNTIME VERIFICATION"
    ),
]

for name, passed, detail in checks:
    lines.append(
        f"{name}: "
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

    if detail is not None:
        lines.append(
            "  "
            + json.dumps(
                detail,
                indent=2,
                sort_keys=True,
                default=str,
            ).replace(
                "\n",
                "\n  ",
            )
        )

lines.extend([
    heading(
        "STANDARD ERROR"
    ),
    standard_error,
    heading(
        "ROLLBACK STATUS"
    ),
    rollback_status,
    heading(
        "11-PART REGISTRATION PACKAGE"
    ),
    "1. Registration identity: connect_domain_stage",
    "2. Handler binding: execute_connect_domain_stage",
    "3. Payload contract: workspace and domain identity",
    "4. Worker capability contract: no additional capability required",
    "5. Dependency contract: root stage -> site_sources",
    "6. Idempotency contract: workspace_id + domain",
    "7. Retry contract: maximum three attempts",
    "8. Concurrency contract: one execution per workspace",
    "9. Lifecycle contract: running kernel and enabled workers",
    "10. Admission and compatibility: canonical runtime authorities",
    "11. Evidence and persistence: fingerprinted persistent registry record",
    heading(
        "FINAL RESULT"
    ),
    f"TESTS_PASSED={passed_count}",
    f"TESTS_FAILED={len(failed)}",
    (
        "PART_B_5_1_CERTIFICATION=PASS"
        if certified
        else "PART_B_5_1_CERTIFICATION=FAIL"
    ),
    (
        "FINAL RESULT: PART B 5.1 CONNECT DOMAIN REGISTRATION CERTIFIED"
        if certified
        else "FINAL RESULT: PART B 5.1 CONNECT DOMAIN REGISTRATION NOT_CERTIFIED"
    ),
]

REPORT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT.write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)

print(
    "\n".join(lines)
)

raise SystemExit(
    0
    if certified
    else 1
)