from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


from backend.server.universal_article_body_store.body_store_lifecycle_repair_executor_contract_v1 import (
    BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_VERSION,
)

from backend.server.universal_article_body_store.body_store_lifecycle_repair_executor_engine_v1 import (
    BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION,
    execute_lifecycle_repair_plan_v1,
    prepare_lifecycle_repair_execution_v1,
    validate_lifecycle_repair_execution_context_v1,
)


BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_VERIFIER_SCHEMA = (
    "body_store_lifecycle_repair_executor_verifier.v1"
)

BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_VERIFICATION_SCHEMA = (
    "body_store_lifecycle_repair_executor_verification.v1"
)

BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_VERIFIER_VERSION = (
    "1.0"
)


EXPECTED_EXECUTOR_ENGINE_SHA256 = (
    "751c97e95aecd7bb537e33a834123c93305970e9e8eb1c1c9b93dd9926539100"
)


EXPECTED_EXECUTOR_ENGINE_FUNCTION_COUNT = 60


LEGACY_EXECUTOR_HELPER_NAME = (
    "_validate_target_descriptor_checksum_v1"
)


PROTECTED_PRODUCTION_OUTPUTS = MappingProxyType(
    {
        "body_store":
            "backend/server/data/universal_article_body_store",

        "queue":
            "backend/server/data/universal_knowledge_queue",

        "lifecycle":
            "backend/server/data/universal_article_body_store_lifecycle",

        "archive_store":
            "backend/server/data/universal_article_body_store_archive",

        "tombstone_store":
            "backend/server/data/universal_article_body_store_tombstones",

        "uucd":
            "backend/server/data/universal_unified_content_document",

        "wuc":
            "backend/server/data/website_unified_content",

        "runtime_registration":
            "backend/server/data/universal_article_body_store_runtime_registration",
    }
)


class LifecycleRepairExecutorVerificationError(
    ValueError
):
    pass


def _freeze(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):

        return MappingProxyType(
            {
                str(key):
                    _freeze(item)

                for key, item
                in value.items()
            }
        )


    if isinstance(
        value,
        list,
    ):

        return tuple(
            _freeze(item)
            for item in value
        )


    if isinstance(
        value,
        tuple,
    ):

        return tuple(
            _freeze(item)
            for item in value
        )


    if isinstance(
        value,
        set,
    ):

        return tuple(
            sorted(
                (
                    _freeze(item)
                    for item in value
                ),
                key=repr,
            )
        )


    return value


def _json_ready(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):

        return {
            str(key):
                _json_ready(item)

            for key, item
            in value.items()
        }


    if isinstance(
        value,
        tuple,
    ):

        return [
            _json_ready(item)
            for item in value
        ]


    if isinstance(
        value,
        list,
    ):

        return [
            _json_ready(item)
            for item in value
        ]


    return value


def _require_mapping(
    value: Any,
    *,
    field_name: str,
) -> Mapping[str, Any]:

    if not isinstance(
        value,
        Mapping,
    ):

        raise LifecycleRepairExecutorVerificationError(
            field_name
            + " must be a mapping."
        )

    return value


def _require_string(
    value: Any,
    *,
    field_name: str,
) -> str:

    if (
        not isinstance(
            value,
            str,
        )
        or not value.strip()
    ):

        raise LifecycleRepairExecutorVerificationError(
            field_name
            + " must be a non-empty string."
        )

    return value.strip()


def calculate_lifecycle_repair_executor_verification_checksum_v1(
    *,
    payload: Mapping[str, Any],
) -> str:

    normalized = _json_ready(
        _require_mapping(
            payload,
            field_name="payload",
        )
    )


    serialized = json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )


    return hashlib.sha256(
        serialized.encode(
            "utf-8"
        )
    ).hexdigest()


def _resolve_project_root_v1(
    project_root: str | Path | None = None,
) -> Path:

    if project_root is None:

        return (
            Path(__file__)
            .resolve()
            .parents[3]
        )


    return Path(
        project_root
    ).resolve()


def _resolve_executor_engine_path_v1(
    *,
    project_root: str | Path | None = None,
) -> Path:

    root = _resolve_project_root_v1(
        project_root
    )


    return (
        root
        / "backend"
        / "server"
        / "universal_article_body_store"
        / "body_store_lifecycle_repair_executor_engine_v1.py"
    ).resolve()


def _calculate_file_sha256_v1(
    path: Path,
) -> str:

    if not path.is_file():

        raise LifecycleRepairExecutorVerificationError(
            "Required verification file does not exist: "
            + str(
                path
            )
        )


    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _fingerprint_path_v1(
    path: Path,
) -> str:

    if not path.exists():

        return "ABSENT"


    digest = hashlib.sha256()


    if path.is_file():

        digest.update(
            path.name.encode(
                "utf-8"
            )
        )

        digest.update(
            path.read_bytes()
        )

        return digest.hexdigest()


    files = sorted(
        candidate
        for candidate in path.rglob("*")
        if candidate.is_file()
    )


    for file_path in files:

        relative = (
            file_path
            .relative_to(path)
        )


        digest.update(
            str(relative)
            .replace(
                "\\",
                "/",
            )
            .encode(
                "utf-8"
            )
        )


        digest.update(
            file_path.read_bytes()
        )


    return digest.hexdigest()


def fingerprint_lifecycle_repair_executor_protected_outputs_v1(
    *,
    project_root: str | Path | None = None,
) -> Mapping[str, str]:

    root = _resolve_project_root_v1(
        project_root
    )


    fingerprints = {}


    for (
        output_name,
        relative_path,
    ) in PROTECTED_PRODUCTION_OUTPUTS.items():

        fingerprints[
            output_name
        ] = _fingerprint_path_v1(
            (
                root
                / relative_path
            ).resolve()
        )


    return _freeze(
        fingerprints
    )


def verify_lifecycle_repair_executor_identity_v1(
    *,
    project_root: str | Path | None = None,
) -> Mapping[str, Any]:

    engine_path = (
        _resolve_executor_engine_path_v1(
            project_root=project_root
        )
    )


    if not engine_path.is_file():

        raise LifecycleRepairExecutorVerificationError(
            "Canonical Lifecycle Repair Executor Engine "
            "was not found."
        )


    source = engine_path.read_text(
        encoding="utf-8"
    )


    try:

        tree = ast.parse(
            source,
            filename=str(
                engine_path
            ),
        )

    except SyntaxError as exc:

        raise LifecycleRepairExecutorVerificationError(
            "Canonical Executor Engine failed AST parsing: "
            + str(
                exc
            )
        ) from exc


    top_level_functions = [
        node
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    ]


    function_names = [
        node.name
        for node in top_level_functions
    ]


    duplicate_functions = tuple(
        sorted(
            {
                name
                for name in function_names
                if function_names.count(
                    name
                ) > 1
            }
        )
    )


    engine_sha256 = (
        _calculate_file_sha256_v1(
            engine_path
        )
    )


    checks = {
        "engine_file_present":
            True,

        "engine_ast_parse_passed":
            True,

        "engine_sha256_match":
            engine_sha256
            == EXPECTED_EXECUTOR_ENGINE_SHA256,

        "engine_schema_match":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA
            == (
                "body_store_lifecycle_repair_executor_engine.v1"
            ),

        "engine_version_match":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION
            == "1.0",

        "contract_schema_match":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_SCHEMA
            == (
                "body_store_lifecycle_repair_executor_contract.v1"
            ),

        "contract_version_match":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_VERSION
            == "1.0",

        "function_count_match":
            len(
                function_names
            )
            == EXPECTED_EXECUTOR_ENGINE_FUNCTION_COUNT,

        "duplicate_definitions_zero":
            len(
                duplicate_functions
            )
            == 0,

        "legacy_helper_absent":
            LEGACY_EXECUTOR_HELPER_NAME
            not in function_names,

        "legacy_helper_text_absent":
            LEGACY_EXECUTOR_HELPER_NAME
            not in source,

        "context_validator_callable":
            callable(
                validate_lifecycle_repair_execution_context_v1
            ),

        "preflight_callable":
            callable(
                prepare_lifecycle_repair_execution_v1
            ),

        "executor_callable":
            callable(
                execute_lifecycle_repair_plan_v1
            ),
    }


    failures = tuple(
        name
        for name, passed
        in checks.items()
        if passed is not True
    )


    identity_payload = {
        "schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_VERIFICATION_SCHEMA,

        "verifier_schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_VERIFIER_SCHEMA,

        "verifier_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_VERIFIER_VERSION,

        "verification_scope":
            "EXECUTOR_IDENTITY_ONLY",

        "engine_path":
            str(
                engine_path
            ),

        "engine_sha256":
            engine_sha256,

        "expected_engine_sha256":
            EXPECTED_EXECUTOR_ENGINE_SHA256,

        "engine_function_count":
            len(
                function_names
            ),

        "expected_engine_function_count":
            EXPECTED_EXECUTOR_ENGINE_FUNCTION_COUNT,

        "duplicate_functions":
            duplicate_functions,

        "checks":
            checks,

        "failures":
            failures,

        "identity_verified":
            len(
                failures
            )
            == 0,

        "repair_execution_started":
            False,

        "repair_executed":
            False,

        "production_mutation_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }


    verification_checksum = (
        calculate_lifecycle_repair_executor_verification_checksum_v1(
            payload=identity_payload
        )
    )


    return _freeze(
        {
            **identity_payload,

            "verification_checksum":
                verification_checksum,
        }
    )


def summarize_lifecycle_repair_executor_identity_verification_v1(
    *,
    verification: Mapping[str, Any],
) -> Mapping[str, Any]:

    record = _require_mapping(
        verification,
        field_name="verification",
    )


    checks = _require_mapping(
        record.get(
            "checks"
        ),
        field_name="verification.checks",
    )


    return _freeze(
        {
            "schema":
                BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_VERIFIER_SCHEMA,

            "verifier_version":
                BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_VERIFIER_VERSION,

            "verification_scope":
                record.get(
                    "verification_scope"
                ),

            "identity_verified":
                record.get(
                    "identity_verified"
                ),

            "engine_sha256":
                record.get(
                    "engine_sha256"
                ),

            "engine_function_count":
                record.get(
                    "engine_function_count"
                ),

            "checks_passed":
                sum(
                    1
                    for passed
                    in checks.values()
                    if passed is True
                ),

            "checks_total":
                len(
                    checks
                ),

            "failures":
                tuple(
                    record.get(
                        "failures",
                        (),
                    )
                ),

            "repair_execution_started":
                record.get(
                    "repair_execution_started"
                ),

            "repair_executed":
                record.get(
                    "repair_executed"
                ),

            "production_mutation_performed":
                record.get(
                    "production_mutation_performed"
                ),

            "runtime_job_created":
                record.get(
                    "runtime_job_created"
                ),

            "queue_job_created":
                record.get(
                    "queue_job_created"
                ),
        }
    )

# ============================================================
# PHASE 9.1.13.3 - PART 1B
# Independent DRY_RUN verification helpers
# ============================================================


def _build_executor_dry_run_verification_fixture_v1(
    *,
    project_root: str | Path | None = None,
) -> Mapping[str, Any]:

    import shutil

    root = _resolve_project_root_v1(
        project_root
    )

    sandbox_parent = (
        root
        / "_sandbox"
    ).resolve()

    sandbox_root = (
        sandbox_parent
        / "phase_9_1_13_3_executor_dry_run"
    ).resolve()

    try:

        sandbox_root.relative_to(
            sandbox_parent
        )

    except ValueError as exc:

        raise LifecycleRepairExecutorVerificationError(
            "DRY_RUN verification sandbox escaped "
            "the approved _sandbox boundary."
        ) from exc

    if sandbox_root.exists():

        shutil.rmtree(
            sandbox_root
        )

    sandbox_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    workspace_id = (
        "ws_executor_verifier_dry_run"
    )

    execution_request_id = (
        "executor_verifier_dry_run_execution_v1"
    )

    lifecycle_root = (
        sandbox_root
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_lifecycle"
        / workspace_id
    )

    lifecycle_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    target_path = (
        lifecycle_root
        / "unsupported_state.json"
    )

    original_record = {
        "workspace_id":
            workspace_id,

        "body_id":
            "body_executor_verifier_dry_run",

        "lifecycle_state":
            "BROKEN_STATE",

        "body_ref":
            "body_executor_verifier_dry_run.json",

        "test_fixture":
            True,
    }

    target_path.write_text(
        json.dumps(
            original_record,
            indent=2,
            sort_keys=True,
        )
        + "`n",
        encoding="utf-8",
    )

    return _freeze(
        {
            "sandbox_root":
                str(
                    sandbox_root
                ),

            "workspace_id":
                workspace_id,

            "execution_request_id":
                execution_request_id,

            "target_path":
                str(
                    target_path
                ),

            "original_record":
                original_record,

            "target_checksum_before":
                _calculate_file_sha256_v1(
                    target_path
                ),
        }
    )

def _build_executor_dry_run_repair_plan_fixture_v1(
    *,
    fixture: Mapping[str, Any],
) -> Mapping[str, Any]:

    from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_contract_v1 import (
        create_lifecycle_repair_planner_request_v1,
    )

    from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_engine_v1 import (
        build_lifecycle_repair_plan_v1,
        validate_lifecycle_repair_plan_v1,
    )

    workspace_id = _require_string(
        fixture.get(
            "workspace_id"
        ),
        field_name="fixture.workspace_id",
    )

    scanner_certification = {
        "certified":
            True,

        "verification_passed":
            True,

        "workspace_id":
            workspace_id,

        "scan_request_id":
            "executor_verifier_dry_run_scanner_v1",

        "verification_checksum":
            "4" * 64,
    }

    findings = (
        {
            "finding_id":
                "finding_executor_verifier_dry_run",

            "finding_type":
                "UNSUPPORTED_LIFECYCLE_STATE",

            "severity":
                "ERROR",

            "workspace_id":
                workspace_id,

            "body_id":
                "body_executor_verifier_dry_run",

            "target_store":
                "LIFECYCLE",

            "record_path":
                "unsupported_state.json",

            "normalized_state":
                "ACTIVE",
        },
    )

    planner_request = (
        create_lifecycle_repair_planner_request_v1(
            repair_plan_request_id=(
                "executor_verifier_dry_run_plan_v1"
            ),
            workspace_id=workspace_id,
            repair_scope="FINDING_SET",
            finding_ids=(
                "finding_executor_verifier_dry_run",
            ),
            allow_automatic_planning=True,
            require_manual_review_for_critical=True,
        )
    )

    repair_plan = (
        build_lifecycle_repair_plan_v1(
            planner_request=planner_request,
            scanner_certification=scanner_certification,
            findings=findings,
        )
    )

    plan_validation = (
        validate_lifecycle_repair_plan_v1(
            repair_plan=repair_plan
        )
    )

    repair_actions = tuple(
        repair_plan[
            "repair_actions"
        ]
    )

    if len(repair_actions) != 1:

        raise LifecycleRepairExecutorVerificationError(
            "Expected exactly one DRY_RUN repair action."
        )

    repair_action = (
        repair_actions[0]
    )

    if (
        repair_action.get(
            "repair_action_type"
        )
        != "NORMALIZE_LIFECYCLE_STATE"
    ):

        raise LifecycleRepairExecutorVerificationError(
            "Expected NORMALIZE_LIFECYCLE_STATE."
        )

    if (
        plan_validation.get(
            "plan_valid"
        )
        is not True
    ):

        raise LifecycleRepairExecutorVerificationError(
            "DRY_RUN Repair Plan validation failed."
        )

    return _freeze(
        {
            "scanner_certification":
                scanner_certification,

            "findings":
                findings,

            "planner_request":
                planner_request,

            "repair_plan":
                repair_plan,

            "plan_validation":
                plan_validation,

            "repair_action":
                repair_action,

            "repair_action_id":
                repair_action[
                    "repair_action_id"
                ],

            "repair_action_type":
                repair_action[
                    "repair_action_type"
                ],
        }
    )


def _execute_executor_dry_run_fixture_v1(
    *,
    fixture: Mapping[str, Any],
    planner: Mapping[str, Any],
) -> Mapping[str, Any]:

    from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_certification_v1 import (
        build_lifecycle_repair_planner_certification_v1,
        validate_lifecycle_repair_planner_certification_v1,
    )

    from backend.server.universal_article_body_store.body_store_lifecycle_repair_executor_contract_v1 import (
        create_lifecycle_repair_execution_authorization_v1,
        create_lifecycle_repair_execution_request_v1,
    )

    workspace_id = _require_string(
        fixture.get(
            "workspace_id"
        ),
        field_name="fixture.workspace_id",
    )

    repair_plan = _require_mapping(
        planner.get(
            "repair_plan"
        ),
        field_name="planner.repair_plan",
    )

    planner_request = _require_mapping(
        planner.get(
            "planner_request"
        ),
        field_name="planner.planner_request",
    )

    scanner_certification = _require_mapping(
        planner.get(
            "scanner_certification"
        ),
        field_name="planner.scanner_certification",
    )

    findings = tuple(
        planner.get(
            "findings",
            (),
        )
    )

    repair_action_id = _require_string(
        planner.get(
            "repair_action_id"
        ),
        field_name="planner.repair_action_id",
    )

    repair_action_type = _require_string(
        planner.get(
            "repair_action_type"
        ),
        field_name="planner.repair_action_type",
    )

    if (
        repair_action_type
        != "NORMALIZE_LIFECYCLE_STATE"
    ):

        raise LifecycleRepairExecutorVerificationError(
            "Patch 3 expected "
            "NORMALIZE_LIFECYCLE_STATE."
        )

    # ========================================================
    # SANDBOX ROOT
    # ========================================================

    sandbox_root_value = fixture.get(
        "sandbox_root"
    )

    target_path_value = fixture.get(
        "target_path"
    )

    if sandbox_root_value is not None:

        sandbox_root = Path(
            sandbox_root_value
        ).resolve()

    elif target_path_value is not None:

        candidate_target = Path(
            target_path_value
        ).resolve()

        parts = candidate_target.parts

        marker = (
            "backend",
            "server",
            "data",
            "universal_article_body_store_lifecycle",
        )

        backend_index = None

        for index in range(
            0,
            len(parts) - len(marker) + 1,
        ):

            if (
                tuple(
                    parts[
                        index:
                        index + len(marker)
                    ]
                )
                == marker
            ):

                backend_index = index
                break

        if backend_index is None:

            raise LifecycleRepairExecutorVerificationError(
                "Unable to derive sandbox root "
                "from fixture.target_path."
            )

        sandbox_root = Path(
            *parts[
                :backend_index
            ]
        ).resolve()

    else:

        raise LifecycleRepairExecutorVerificationError(
            "DRY_RUN fixture does not expose "
            "sandbox_root or target_path."
        )

    # ========================================================
    # TARGET
    # ========================================================

    if target_path_value is not None:

        target_path = Path(
            target_path_value
        ).resolve()

    else:

        target_path = (
            sandbox_root
            / "backend"
            / "server"
            / "data"
            / "universal_article_body_store_lifecycle"
            / workspace_id
            / "unsupported_state.json"
        ).resolve()

    if not target_path.exists():

        raise LifecycleRepairExecutorVerificationError(
            "DRY_RUN target does not exist: "
            + str(
                target_path
            )
        )

    if not target_path.is_file():

        raise LifecycleRepairExecutorVerificationError(
            "DRY_RUN target is not a file: "
            + str(
                target_path
            )
        )

    target_checksum_before = (
        hashlib.sha256(
            target_path.read_bytes()
        ).hexdigest()
    )

    target_record_before = json.loads(
        target_path.read_text(
            encoding="utf-8"
        )
    )

    # ========================================================
    # PLANNER CERTIFICATION
    # ========================================================

    planner_certification = (
        build_lifecycle_repair_planner_certification_v1(
            planner_request=planner_request,
            scanner_certification=scanner_certification,
            findings=findings,
            repair_plan=repair_plan,
        )
    )

    planner_certification_validation = (
        validate_lifecycle_repair_planner_certification_v1(
            certification=planner_certification
        )
    )

    if (
        planner_certification_validation.get(
            "certification_valid"
        )
        is not True
    ):

        raise LifecycleRepairExecutorVerificationError(
            "DRY_RUN Planner Certification failed."
        )

    # ========================================================
    # EXECUTOR AUTHORIZATION
    # ========================================================

    authorization = (
        create_lifecycle_repair_execution_authorization_v1(
            authorization_id=(
                "executor_verifier_dry_run_authorization_v1"
            ),
            workspace_id=workspace_id,
            repair_plan_id=(
                repair_plan[
                    "repair_plan_id"
                ]
            ),
            repair_plan_checksum=(
                repair_plan[
                    "repair_plan_checksum"
                ]
            ),
            planner_certification_id=(
                planner_certification[
                    "certification_id"
                ]
            ),
            planner_certification_checksum=(
                planner_certification[
                    "certification_checksum"
                ]
            ),
            authorization_state="AUTHORIZED",
            authorized_action_ids=(
                repair_action_id,
            ),
            authorized_by=(
                "phase_9_1_13_3_executor_verifier"
            ),
            authorization_reason=(
                "Independent sandbox DRY_RUN verification."
            ),
        )
    )

    # ========================================================
    # DRY_RUN EXECUTION REQUEST
    # ========================================================

    execution_request_id = (
        "executor_verifier_dry_run_execution_v1"
    )

    execution_request = (
        create_lifecycle_repair_execution_request_v1(
            execution_request_id=(
                execution_request_id
            ),
            workspace_id=workspace_id,
            repair_plan_id=(
                repair_plan[
                    "repair_plan_id"
                ]
            ),
            repair_plan_checksum=(
                repair_plan[
                    "repair_plan_checksum"
                ]
            ),
            planner_certification_id=(
                planner_certification[
                    "certification_id"
                ]
            ),
            planner_certification_checksum=(
                planner_certification[
                    "certification_checksum"
                ]
            ),
            authorization_id=(
                authorization[
                    "authorization_id"
                ]
            ),
            authorization_checksum=(
                authorization[
                    "authorization_checksum"
                ]
            ),
            execution_mode="DRY_RUN",
            requested_action_ids=(
                repair_action_id,
            ),
            require_all_actions_authorized=True,
        )
    )

    # ========================================================
    # EXECUTOR CONTEXT
    # ========================================================

    context = (
        validate_lifecycle_repair_execution_context_v1(
            repair_plan=repair_plan,
            planner_certification=planner_certification,
            authorization=authorization,
            execution_request=execution_request,
            findings=findings,
        )
    )

    if (
        context.get(
            "context_valid"
        )
        is not True
    ):

        raise LifecycleRepairExecutorVerificationError(
            "DRY_RUN Executor context validation failed."
        )

    if (
        context.get(
            "all_safety_gates_passed"
        )
        is not True
    ):

        raise LifecycleRepairExecutorVerificationError(
            "DRY_RUN Executor safety gates failed."
        )

    if (
        context.get(
            "dry_run_eligible"
        )
        is not True
    ):

        raise LifecycleRepairExecutorVerificationError(
            "Executor context is not DRY_RUN eligible."
        )

    # ========================================================
    # PREFLIGHT
    # ========================================================

    preflight = (
        prepare_lifecycle_repair_execution_v1(
            project_root=sandbox_root,
            repair_plan=repair_plan,
            planner_certification=planner_certification,
            authorization=authorization,
            execution_request=execution_request,
            findings=findings,
        )
    )

    if (
        preflight.get(
            "all_preflight_checks_passed"
        )
        is not True
    ):

        raise LifecycleRepairExecutorVerificationError(
            "DRY_RUN Executor preflight failed."
        )

    if (
        preflight.get(
            "prepared_action_count"
        )
        != 1
    ):

        raise LifecycleRepairExecutorVerificationError(
            "Expected exactly one prepared DRY_RUN action."
        )

    if (
        preflight.get(
            "mutation_performed"
        )
        is not False
    ):

        raise LifecycleRepairExecutorVerificationError(
            "Executor preflight unexpectedly mutated data."
        )

    # ========================================================
    # REAL EXECUTOR — DRY_RUN
    # ========================================================

    executor_result = (
        execute_lifecycle_repair_plan_v1(
            project_root=sandbox_root,
            repair_plan=repair_plan,
            planner_certification=planner_certification,
            authorization=authorization,
            execution_request=execution_request,
            findings=findings,
        )
    )

    # ========================================================
    # VERIFY ZERO MUTATION
    # ========================================================

    target_checksum_after = (
        hashlib.sha256(
            target_path.read_bytes()
        ).hexdigest()
    )

    target_record_after = json.loads(
        target_path.read_text(
            encoding="utf-8"
        )
    )

    backup_root = (
        sandbox_root
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_repair_backups"
        / workspace_id
        / execution_request_id
    )

    quarantine_root = (
        sandbox_root
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_repair_quarantine"
        / workspace_id
    )

    checks = {
        "planner_certification_valid":
            planner_certification_validation.get(
                "certification_valid"
            )
            is True,

        "context_valid":
            context.get(
                "context_valid"
            )
            is True,

        "all_safety_gates_passed":
            context.get(
                "all_safety_gates_passed"
            )
            is True,

        "dry_run_eligible":
            context.get(
                "dry_run_eligible"
            )
            is True,

        "preflight_passed":
            preflight.get(
                "all_preflight_checks_passed"
            )
            is True,

        "prepared_action_count_one":
            preflight.get(
                "prepared_action_count"
            )
            == 1,

        "preflight_no_mutation":
            preflight.get(
                "mutation_performed"
            )
            is False,

        "execution_mode_dry_run":
            executor_result.get(
                "execution_mode"
            )
            == "DRY_RUN",

        "execution_succeeded":
            executor_result.get(
                "execution_succeeded"
            )
            is True,

        "execution_authorized_false":
            executor_result.get(
                "execution_authorized"
            )
            is False,

        "executed_action_count_zero":
            executor_result.get(
                "executed_action_count"
            )
            == 0,

        "dry_run_validated_action_count_one":
            executor_result.get(
                "dry_run_validated_action_count"
            )
            == 1,

        "committed_mutation_count_zero":
            executor_result.get(
                "committed_mutation_count"
            )
            == 0,

        "repair_not_executed":
            executor_result.get(
                "repair_executed"
            )
            is False,

        "mutation_not_performed":
            executor_result.get(
                "mutation_performed"
            )
            is False,

        "target_checksum_unchanged":
            target_checksum_before
            == target_checksum_after,

        "target_record_unchanged":
            target_record_before
            == target_record_after,

        "backup_root_absent":
            not backup_root.exists(),

        "quarantine_root_absent":
            not quarantine_root.exists(),

        "runtime_job_not_created":
            executor_result.get(
                "runtime_job_created"
            )
            is False,

        "queue_job_not_created":
            executor_result.get(
                "queue_job_created"
            )
            is False,
    }

    failures = tuple(
        name
        for name, passed
        in checks.items()
        if passed is not True
    )

    return _freeze(
        {
            "planner_certification":
                planner_certification,

            "planner_certification_validation":
                planner_certification_validation,

            "authorization":
                authorization,

            "execution_request":
                execution_request,

            "context":
                context,

            "preflight":
                preflight,

            "executor_result":
                executor_result,

            "target_checksum_before":
                target_checksum_before,

            "target_checksum_after":
                target_checksum_after,

            "checks":
                checks,

            "failures":
                failures,

            "verification_passed":
                len(
                    failures
                )
                == 0,
        }
    )



def verify_lifecycle_repair_executor_dry_run_v1(
    *,
    project_root: Any = None,
) -> Mapping[str, Any]:
    """
    Independently verify the Lifecycle Repair Executor in DRY_RUN mode.

    The verifier:
    - creates/resets an isolated sandbox lifecycle record,
    - builds a real Repair Plan,
    - certifies the plan,
    - constructs real Executor authorization,
    - performs Executor context validation,
    - performs Executor preflight,
    - invokes the real Executor in DRY_RUN mode,
    - proves zero mutation,
    - proves no backup/quarantine side effect,
    - proves no Runtime/Queue job creation,
    - fingerprints protected production outputs before and after.
    """

    import json
    import shutil
    from pathlib import Path

    # ========================================================
    # 1. RESOLVE PROJECT ROOT
    # ========================================================

    if project_root is None:

        root = (
            Path(
                __file__
            )
            .resolve()
            .parents[3]
        )

    else:

        root = Path(
            project_root
        ).resolve()


    if not root.exists():

        raise LifecycleRepairExecutorVerificationError(
            "Executor verifier project root does not exist: "
            + str(
                root
            )
        )


    # ========================================================
    # 2. PROTECTED PRODUCTION FINGERPRINT ? BEFORE
    # ========================================================

    protected_before = (
        fingerprint_lifecycle_repair_executor_protected_outputs_v1(
            project_root=root
        )
    )


    # ========================================================
    # 3. BUILD ISOLATED SANDBOX FIXTURE
    # ========================================================

    fixture = (
        _build_executor_dry_run_verification_fixture_v1()
    )


    workspace_id = _require_string(
        fixture.get(
            "workspace_id"
        ),
        field_name="fixture.workspace_id",
    )


    sandbox_root_value = fixture.get(
        "sandbox_root"
    )

    target_path_value = fixture.get(
        "target_path"
    )


    if sandbox_root_value is not None:

        sandbox_root = Path(
            sandbox_root_value
        ).resolve()

    elif target_path_value is not None:

        candidate_target = Path(
            target_path_value
        ).resolve()

        parts = candidate_target.parts

        marker = (
            "backend",
            "server",
            "data",
            "universal_article_body_store_lifecycle",
        )

        marker_index = None

        for index in range(
            0,
            len(parts) - len(marker) + 1,
        ):

            if (
                tuple(
                    parts[
                        index:
                        index + len(marker)
                    ]
                )
                == marker
            ):

                marker_index = index
                break


        if marker_index is None:

            raise LifecycleRepairExecutorVerificationError(
                "Unable to derive sandbox root "
                "from fixture target."
            )


        sandbox_root = Path(
            *parts[
                :marker_index
            ]
        ).resolve()

    else:

        raise LifecycleRepairExecutorVerificationError(
            "Executor verifier fixture exposes neither "
            "sandbox_root nor target_path."
        )


    if target_path_value is not None:

        target_path = Path(
            target_path_value
        ).resolve()

    else:

        target_path = (
            sandbox_root
            / "backend"
            / "server"
            / "data"
            / "universal_article_body_store_lifecycle"
            / workspace_id
            / "unsupported_state.json"
        ).resolve()


    # ========================================================
    # 4. RESET FIXTURE TO ONE CANONICAL JSON RECORD
    #
    # This makes the public verifier idempotent and prevents
    # stale/concatenated sandbox JSON from earlier test runs.
    # ========================================================

    target_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    original_record = {
        "workspace_id":
            workspace_id,

        "body_id":
            "body_executor_verifier_dry_run",

        "lifecycle_state":
            "BROKEN_STATE",

        "body_ref":
            "body_executor_verifier_dry_run.json",

        "test_fixture":
            True,
    }


    target_path.write_text(
        json.dumps(
            original_record,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


    parsed_record = json.loads(
        target_path.read_text(
            encoding="utf-8"
        )
    )


    if parsed_record != original_record:

        raise LifecycleRepairExecutorVerificationError(
            "Executor verifier failed to establish "
            "canonical sandbox JSON."
        )


    # ========================================================
    # 5. BUILD REAL PLANNER FIXTURE
    # ========================================================

    planner = (
        _build_executor_dry_run_repair_plan_fixture_v1(
            fixture=fixture
        )
    )


    repair_action_id = _require_string(
        planner.get(
            "repair_action_id"
        ),
        field_name="planner.repair_action_id",
    )


    repair_action_type = _require_string(
        planner.get(
            "repair_action_type"
        ),
        field_name="planner.repair_action_type",
    )


    plan_validation = _require_mapping(
        planner.get(
            "plan_validation"
        ),
        field_name="planner.plan_validation",
    )


    # ========================================================
    # 6. CLEAR STALE SANDBOX-ONLY EXECUTOR OUTPUTS
    # ========================================================

    execution_request_id = (
        "executor_verifier_dry_run_execution_v1"
    )


    backup_root = (
        sandbox_root
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_repair_backups"
        / workspace_id
        / execution_request_id
    )


    quarantine_root = (
        sandbox_root
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_repair_quarantine"
        / workspace_id
    )


    for sandbox_output in (
        backup_root,
        quarantine_root,
    ):

        if sandbox_output.exists():

            shutil.rmtree(
                sandbox_output
            )


    # ========================================================
    # 7. EXECUTE TESTED PATCH-3 DRY_RUN HELPER
    # ========================================================

    execution = (
        _execute_executor_dry_run_fixture_v1(
            fixture=fixture,
            planner=planner,
        )
    )


    executor_result = _require_mapping(
        execution.get(
            "executor_result"
        ),
        field_name="execution.executor_result",
    )


    # ========================================================
    # 8. PROTECTED PRODUCTION FINGERPRINT ? AFTER
    # ========================================================

    protected_after = (
        fingerprint_lifecycle_repair_executor_protected_outputs_v1(
            project_root=root
        )
    )


    production_outputs_unchanged = (
        dict(
            protected_before
        )
        ==
        dict(
            protected_after
        )
    )


    # ========================================================
    # 9. FINAL INDEPENDENT CHECK SET
    # ========================================================

    helper_checks = dict(
        _require_mapping(
            execution.get(
                "checks"
            ),
            field_name="execution.checks",
        )
    )


    checks = {
        "repair_plan_valid":
            plan_validation.get(
                "plan_valid"
            )
            is True,

        "correct_repair_action":
            repair_action_type
            == "NORMALIZE_LIFECYCLE_STATE",

        **helper_checks,

        "production_outputs_unchanged":
            production_outputs_unchanged,
    }


    failures = tuple(
        name
        for name, passed
        in checks.items()
        if passed is not True
    )


    # ========================================================
    # 10. PUBLIC VERIFICATION PAYLOAD
    # ========================================================

    payload = {
        "schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_VERIFICATION_SCHEMA,

        "verifier_schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_VERIFIER_SCHEMA,

        "verifier_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_VERIFIER_VERSION,

        "verification_scope":
            "EXECUTOR_DRY_RUN_BEHAVIOR",

        "workspace_id":
            workspace_id,

        "execution_request_id":
            execution_request_id,

        "repair_action_id":
            repair_action_id,

        "repair_action_type":
            repair_action_type,

        "target_checksum_before":
            execution.get(
                "target_checksum_before"
            ),

        "target_checksum_after":
            execution.get(
                "target_checksum_after"
            ),

        "checks":
            checks,

        "failures":
            failures,

        "verification_passed":
            len(
                failures
            )
            == 0,

        "authorized_apply_executed":
            False,

        "production_mutation_performed":
            False,

        "runtime_job_created":
            executor_result.get(
                "runtime_job_created"
            ),

        "queue_job_created":
            executor_result.get(
                "queue_job_created"
            ),

        "protected_outputs_before":
            dict(
                protected_before
            ),

        "protected_outputs_after":
            dict(
                protected_after
            ),
    }


    verification_checksum = (
        calculate_lifecycle_repair_executor_verification_checksum_v1(
            payload=payload
        )
    )


    return _freeze(
        {
            **payload,

            "verification_checksum":
                verification_checksum,
        }
    )



def summarize_lifecycle_repair_executor_dry_run_verification_v1(
    *,
    verification: Mapping[str, Any],
) -> Mapping[str, Any]:

    record = _require_mapping(
        verification,
        field_name="verification",
    )


    checks = _require_mapping(
        record.get(
            "checks"
        ),
        field_name="verification.checks",
    )


    return _freeze(
        {
            "verification_scope":
                record.get(
                    "verification_scope"
                ),

            "verification_passed":
                record.get(
                    "verification_passed"
                ),

            "checks_passed":
                sum(
                    1
                    for passed
                    in checks.values()
                    if passed is True
                ),

            "checks_total":
                len(
                    checks
                ),

            "repair_action_type":
                record.get(
                    "repair_action_type"
                ),

            "target_checksum_unchanged":
                checks.get(
                    "target_checksum_unchanged"
                ),

            "mutation_not_performed":
                checks.get(
                    "mutation_not_performed"
                ),

            "repair_not_executed":
                checks.get(
                    "repair_not_executed"
                ),

            "backup_root_absent":
                checks.get(
                    "backup_root_absent"
                ),

            "quarantine_root_absent":
                checks.get(
                    "quarantine_root_absent"
                ),

            "production_outputs_unchanged":
                checks.get(
                    "production_outputs_unchanged"
                ),

            "runtime_job_created":
                record.get(
                    "runtime_job_created"
                ),

            "queue_job_created":
                record.get(
                    "queue_job_created"
                ),

            "authorized_apply_executed":
                record.get(
                    "authorized_apply_executed"
                ),

            "production_mutation_performed":
                record.get(
                    "production_mutation_performed"
                ),

            "failures":
                tuple(
                    record.get(
                        "failures",
                        (),
                    )
                ),

            "verification_checksum":
                record.get(
                    "verification_checksum"
                ),
        }
    )

