from __future__ import annotations

import inspect
from typing import Any, Dict
from unittest.mock import patch


from backend.server.workers.udare_reconstruction_worker import (
    UDARE_ARTICLE_FORMAT,
    UDARE_ENGINE,
    UDARE_JOB_TYPE,
    UDARE_PIPELINE,
    UDARE_SOURCE_STORE,
    UDARE_TARGET_STORE,
    WORKER_NAME,
    run_udare_reconstruction_job_v1,
)

from backend.server.workers import (
    universal_knowledge_worker
    as universal_worker
)

from backend.server.stores.udare_store import (
    refresh_udare_store_manifest_v1,
    verify_udare_store_v1,
)


REAL_WORKSPACE_ID = (
    "ws_whattoexpect_com"
)


refresh_udare_store_manifest_v1(
    REAL_WORKSPACE_ID
)

real_store_before = verify_udare_store_v1(
    REAL_WORKSPACE_ID
)


events: list[str] = []
status_events: list[Dict[str, Any]] = []
progress_events: list[Dict[str, Any]] = []


def fake_concurrency_checker(
    *,
    workspace_id: str,
    max_running: int,
) -> Dict[str, Any]:
    events.append(
        "concurrency"
    )

    return {
        "workspace_id":
            workspace_id,

        "running_jobs":
            0,

        "max_running":
            max_running,

        "can_start_new_job":
            True,

        "decision":
            "allow",
    }


def fake_status_updater(
    **values: Any,
) -> Dict[str, Any]:
    events.append(
        "status:"
        + str(
            values.get(
                "status"
            )
            or ""
        )
    )

    status_events.append(
        dict(
            values
        )
    )

    return dict(
        values
    )


def fake_progress_updater(
    **values: Any,
) -> Dict[str, Any]:
    events.append(
        "progress:"
        + str(
            values.get(
                "percent"
            )
            or ""
        )
    )

    progress_events.append(
        dict(
            values
        )
    )

    return dict(
        values
    )


def fake_failure_recorder(
    **values: Any,
) -> Dict[str, Any]:
    events.append(
        "failure"
    )

    return {
        "ok":
            True,

        **values,
    }


def fake_raw_loader(
    *,
    workspace_id: str,
    html_id: str,
    **_: Any,
) -> Dict[str, Any]:
    events.append(
        "raw_loader"
    )

    return {
        "schema_version":
            UDARE_SOURCE_STORE,

        "workspace_id":
            workspace_id,

        "html_id":
            html_id,

        "source_url":
            "https://phase3d.invalid/article",

        "title":
            "Phase 3D Synthetic Article",

        "raw_html":
            (
                "<!doctype html>"
                "<html>"
                "<head>"
                "<title>Phase 3D Synthetic Article</title>"
                "</head>"
                "<body>"
                "<main>"
                "<h1>Phase 3D Synthetic Article</h1>"
                "<p>This verifies the UDARE worker chain.</p>"
                "</main>"
                "</body>"
                "</html>"
            ),
    }


def fake_reconstruction_engine(
    *,
    html_text: str,
    source_url: str,
    title: str,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    events.append(
        "reconstruction"
    )

    assert html_text
    assert source_url
    assert metadata[
        "job_id"
    ] == "phase3d_job"

    return {
        "ok":
            True,

        "engine":
            UDARE_ENGINE,

        "url":
            source_url,

        "title":
            title,

        "h1":
            "Phase 3D Synthetic Article",

        "article_body":
            (
                "Phase 3D Synthetic Article\n\n"
                "This verifies the UDARE worker chain."
            ),

        "content_blocks": [
            {
                "index":
                    0,

                "type":
                    "heading",

                "level":
                    1,

                "text":
                    "Phase 3D Synthetic Article",
            },
            {
                "index":
                    1,

                "type":
                    "paragraph",

                "text":
                    "This verifies the UDARE worker chain.",
            },
        ],

        "headings": [
            {
                "level":
                    1,

                "text":
                    "Phase 3D Synthetic Article",
            },
        ],

        "selected_root": {
            "tag":
                "main",
        },
    }


def fake_store_persister(
    **values: Any,
) -> Dict[str, Any]:
    events.append(
        "persistence"
    )

    article_document = values[
        "article_document"
    ]

    if isinstance(
        article_document,
        bytes,
    ):
        article_text = article_document.decode(
            "utf-8"
        )

    else:
        article_text = str(
            article_document
        )

    assert article_text.lower().startswith(
        "<!doctype html>"
    )

    assert "<article" in article_text
    assert values[
        "udare_engine"
    ] == UDARE_ENGINE
    assert values[
        "source_store_version"
    ] == UDARE_SOURCE_STORE
    assert values[
        "allow_replace"
    ] is False

    return {
        "ok":
            True,

        "status":
            "created",

        "document_sha256":
            values[
                "expected_document_sha256"
            ],

        "article_path":
            "isolated://articles/phase3d.html",

        "metadata_path":
            "isolated://metadata/phase3d.json",
    }


def fake_manifest_refresher(
    *,
    workspace_id: str,
) -> Dict[str, Any]:
    events.append(
        "manifest"
    )

    return {
        "ok":
            True,

        "workspace_id":
            workspace_id,

        "record_count":
            1,

        "article_document_count":
            1,
    }


job = {
    "schema_version":
        "universal_knowledge_job_v1",

    "job_id":
        "phase3d_job",

    "workspace_id":
        "ws_udare_phase3d_isolated",

    "user_id":
        "phase3d_verification",

    "product_id":
        "linkcraftor",

    "pipeline":
        UDARE_PIPELINE,

    "stage":
        UDARE_JOB_TYPE,

    "job_type":
        UDARE_JOB_TYPE,

    "priority":
        5,

    "status":
        "queued",

    "attempts":
        0,

    "attempt_count":
        0,

    "max_attempts":
        3,

    "batch_id":
        "phase3d_batch",

    "payload": {
        "schema_version":
            "udare_runtime_contract_v1",

        "workspace_id":
            "ws_udare_phase3d_isolated",

        "source_store_version":
            UDARE_SOURCE_STORE,

        "source_record_id":
            "raw_html_phase3d",

        "html_id":
            "raw_html_phase3d",

        "source_url":
            "https://phase3d.invalid/article",

        "udare_engine":
            UDARE_ENGINE,

        "target_store":
            UDARE_TARGET_STORE,

        "article_document_format":
            UDARE_ARTICLE_FORMAT,

        "correlation_id":
            "phase3d_isolated_verification",

        "metadata": {
            "verification":
                True,
        },

        "execution_controls": {
            "execute_now":
                True,

            "queue_handler_required":
                True,

            "worker_handler_required":
                True,

            "store_population_allowed":
                True,

            "isolated_verification":
                True,

            "workspace_max_running":
                5,

            "phase":
                "phase_3_worker_integration",
        },
    },
}


handler_result = run_udare_reconstruction_job_v1(
    job=
        job,

    raw_record_loader=
        fake_raw_loader,

    reconstruction_engine=
        fake_reconstruction_engine,

    store_persister=
        fake_store_persister,

    manifest_refresher=
        fake_manifest_refresher,

    status_updater=
        fake_status_updater,

    progress_updater=
        fake_progress_updater,

    failure_recorder=
        fake_failure_recorder,

    concurrency_checker=
        fake_concurrency_checker,
)


dispatch_sentinel = {
    "ok":
        True,

    "status":
        "dispatch_verified",

    "worker":
        WORKER_NAME,
}


def invoke_executor(
    function: Any,
    job_value: Dict[str, Any],
) -> Any:
    signature = inspect.signature(
        function
    )

    positional: list[Any] = []
    keywords: Dict[str, Any] = {}

    supplied_job = False

    for parameter in (
        signature.parameters.values()
    ):
        if (
            parameter.kind
            == inspect.Parameter.VAR_POSITIONAL
        ):
            if not supplied_job:
                positional.append(
                    job_value
                )

                supplied_job = True

            continue

        if (
            parameter.kind
            == inspect.Parameter.VAR_KEYWORD
        ):
            if not supplied_job:
                keywords[
                    "job"
                ] = job_value

                supplied_job = True

            continue

        if parameter.name in {
            "job",
            "job_data",
            "job_record",
            "row",
        }:
            value = job_value
            supplied_job = True

        elif (
            parameter.default
            is not inspect.Parameter.empty
        ):
            continue

        elif not supplied_job:
            value = job_value
            supplied_job = True

        else:
            raise RuntimeError(
                "Unable to invoke universal executor parameter: "
                + parameter.name
            )

        if (
            parameter.kind
            == inspect.Parameter.POSITIONAL_ONLY
        ):
            positional.append(
                value
            )

        else:
            keywords[
                parameter.name
            ] = value

    return function(
        *positional,
        **keywords,
    )


with patch(
    "backend.server.workers."
    "udare_reconstruction_worker."
    "run_udare_reconstruction_job_v1",
    return_value=
        dispatch_sentinel,
) as mocked_handler:
    dispatch_result = invoke_executor(
        universal_worker.
        execute_universal_knowledge_job_v1,

        job,
    )


refresh_udare_store_manifest_v1(
    REAL_WORKSPACE_ID
)

real_store_after = verify_udare_store_v1(
    REAL_WORKSPACE_ID
)


expected_stage_order = [
    "concurrency",
    "status:running",
    "progress:10",
    "raw_loader",
    "progress:35",
    "reconstruction",
    "progress:60",
    "progress:80",
    "persistence",
    "manifest",
    "progress:100",
    "status:completed",
]


checks = {
    "handler_completed":
        handler_result.get(
            "ok"
        )
        is True
        and handler_result.get(
            "status"
        )
        == "completed",

    "worker_identity":
        handler_result.get(
            "worker"
        )
        == WORKER_NAME,

    "pipeline_identity":
        handler_result.get(
            "pipeline"
        )
        == UDARE_PIPELINE,

    "stage_identity":
        handler_result.get(
            "stage"
        )
        == UDARE_JOB_TYPE,

    "engine_identity":
        handler_result.get(
            "udare_engine"
        )
        == UDARE_ENGINE,

    "document_format":
        handler_result.get(
            "article_document_format"
        )
        == UDARE_ARTICLE_FORMAT,

    "dependency_sequence":
        events
        == expected_stage_order,

    "running_status_recorded":
        any(
            event.get(
                "status"
            )
            == "running"

            for event
            in status_events
        ),

    "completed_status_recorded":
        any(
            event.get(
                "status"
            )
            == "completed"

            for event
            in status_events
        ),

    "progress_reached_100":
        any(
            event.get(
                "percent"
            )
            == 100

            for event
            in progress_events
        ),

    "failure_not_recorded":
        "failure"
        not in events,

    "universal_dispatch_routed_udare":
        dispatch_result
        == dispatch_sentinel
        and mocked_handler.call_count
        == 1,

    "dispatch_passed_same_job":
        mocked_handler.call_args.kwargs.get(
            "job"
        )
        is job,

    "real_udare_store_unchanged":
        real_store_before[
            "counts"
        ]
        == real_store_after[
            "counts"
        ],

    "real_udare_store_still_empty":
        real_store_after[
            "counts"
        ][
            "metadata_records"
        ]
        == 0
        and real_store_after[
            "counts"
        ][
            "article_documents"
        ]
        == 0,
}


failed = [
    name

    for name, passed
    in checks.items()

    if not passed
]


print()
print("=" * 112)
print(
    "PHASE 3D — UDARE WORKER "
    "AND DISPATCH VERIFICATION"
)
print("=" * 112)

print()
print("DEPENDENCY SEQUENCE")

for event in events:
    print(
        "  -",
        event,
    )

print()
print("CHECKS")

for name, passed in checks.items():
    print(
        f"  {name}:",
        (
            "PASS"
            if passed
            else "FAIL"
        ),
    )

print()
print(
    "Universal executor signature:",
    inspect.signature(
        universal_worker.
        execute_universal_knowledge_job_v1
    ),
)

print(
    "Handler result status:",
    handler_result.get(
        "status"
    ),
)

print(
    "Real UDARE Store records:",
    real_store_after[
        "counts"
    ][
        "metadata_records"
    ],
)

print(
    "Real UDARE article documents:",
    real_store_after[
        "counts"
    ][
        "article_documents"
    ],
)

print()
print("=" * 112)

if failed:
    print(
        "PHASE 3D — UDARE WORKER "
        "AND DISPATCH: FAIL"
    )

    print(
        "Failed checks:",
        ", ".join(
            failed
        ),
    )

else:
    print(
        "PHASE 3D — UDARE WORKER "
        "AND DISPATCH: PASS"
    )

print("=" * 112)

print(
    "No universal queue runner was invoked."
)

print(
    "No real article was reconstructed."
)

print(
    "No real UDARE Store document was written."
)

raise SystemExit(
    0
    if not failed
    else 1
)
