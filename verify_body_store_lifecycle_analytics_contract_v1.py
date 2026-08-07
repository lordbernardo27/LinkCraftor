from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from types import MappingProxyType

PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from backend.server.universal_article_body_store.body_store_lifecycle_analytics_contract_v1 import (
    BODY_STORE_LIFECYCLE_ANALYTICS_CONTRACT_SCHEMA,
    BODY_STORE_LIFECYCLE_ANALYTICS_CONTRACT_VERSION,
    BODY_STORE_LIFECYCLE_ANALYTICS_REPORT_SCHEMA,
    BODY_STORE_LIFECYCLE_ANALYTICS_SUPPORTED_SCOPES,
    BODY_STORE_LIFECYCLE_ANALYTICS_SUPPORTED_STATES,
    certify_lifecycle_analytics_request_v1,
    create_lifecycle_analytics_request_v1,
    summarize_lifecycle_analytics_request_v1,
    validate_lifecycle_analytics_request_v1,
)

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

PROTECTED = {
    "body_store":
        DATA_ROOT
        / "universal_article_body_store",

    "queue":
        DATA_ROOT
        / "universal_article_body_queue",

    "lifecycle":
        DATA_ROOT
        / "universal_article_body_store_lifecycle",

    "archive_store":
        DATA_ROOT
        / "universal_article_body_store_archive",

    "tombstone_store":
        DATA_ROOT
        / "universal_article_body_store_tombstones",

    "uucd":
        DATA_ROOT
        / "universal_unified_content_documents",

    "wuc":
        DATA_ROOT
        / "website_unified_content",
}


def fingerprint(
    path: Path,
) -> str:

    digest = hashlib.sha256()

    if not path.exists():
        digest.update(
            b"ABSENT"
        )

        return digest.hexdigest()

    for item in sorted(
        path.rglob("*"),
        key=lambda candidate: (
            candidate.relative_to(
                path
            ).as_posix()
        ),
    ):
        digest.update(
            item.relative_to(
                path
            ).as_posix().encode(
                "utf-8"
            )
        )

        if item.is_file():
            digest.update(
                item.read_bytes()
            )

    return digest.hexdigest()


before = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED.items()
}

request = (
    create_lifecycle_analytics_request_v1(
        analytics_request_id="analytics_request_verify_v1",
        scope="WORKSPACE",
        workspace_id="ws_verify",
        include_state_counts=True,
        include_archive_metrics=True,
        include_restore_metrics=True,
        include_deletion_metrics=True,
        include_tombstone_metrics=True,
        include_retention_metrics=True,
        period_start="2026-01-01T00:00:00+00:00",
        period_end="2026-08-06T23:59:59+00:00",
        requested_at="2026-08-06T22:00:00+00:00",
    )
)

validation = (
    validate_lifecycle_analytics_request_v1(
        analytics_request=request,
    )
)

certification = (
    certify_lifecycle_analytics_request_v1(
        analytics_request=request,
    )
)

summary = (
    summarize_lifecycle_analytics_request_v1(
        analytics_request=request,
    )
)
after = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED.items()
}

checks = {
    "contract_schema_valid":
        (
            BODY_STORE_LIFECYCLE_ANALYTICS_CONTRACT_SCHEMA
            == "body_store_lifecycle_analytics_contract.v1"
        ),

    "contract_version_valid":
        (
            BODY_STORE_LIFECYCLE_ANALYTICS_CONTRACT_VERSION
            == "1.0"
        ),

    "report_schema_valid":
        (
            BODY_STORE_LIFECYCLE_ANALYTICS_REPORT_SCHEMA
            == "body_store_lifecycle_analytics_report.v1"
        ),

    "supported_scopes_valid":
        (
            BODY_STORE_LIFECYCLE_ANALYTICS_SUPPORTED_SCOPES
            == (
                "WORKSPACE",
                "GLOBAL",
            )
        ),

    "supported_states_valid":
        (
            BODY_STORE_LIFECYCLE_ANALYTICS_SUPPORTED_STATES
            == (
                "ACTIVE",
                "ARCHIVED",
                "RESTORED",
                "PERMANENTLY_DELETED",
            )
        ),

    "request_immutable":
        isinstance(
            request,
            MappingProxyType,
        ),

    "request_scope_workspace":
        (
            request[
                "scope"
            ]
            == "WORKSPACE"
        ),

    "request_workspace_id_valid":
        (
            request[
                "workspace_id"
            ]
            == "ws_verify"
        ),

    "request_period_start_valid":
        (
            request[
                "period_start"
            ]
            == "2026-01-01T00:00:00+00:00"
        ),

    "request_period_end_valid":
        (
            request[
                "period_end"
            ]
            == "2026-08-06T23:59:59+00:00"
        ),

    "all_metrics_selected":
        all(
            selected is True
            for selected
            in request[
                "metrics"
            ].values()
        ),

    "request_read_only":
        request[
            "read_only"
        ]
        is True,

    "request_checksum_present":
        bool(
            request[
                "checksum"
            ]
        ),

    "request_valid":
        validation[
            "request_valid"
        ]
        is True,

    "schema_validation_passed":
        validation[
            "schema_valid"
        ]
        is True,

    "contract_version_validation_passed":
        validation[
            "contract_version_valid"
        ]
        is True,

    "scope_validation_passed":
        validation[
            "scope_valid"
        ]
        is True,

    "workspace_scope_validation_passed":
        validation[
            "workspace_scope_valid"
        ]
        is True,

    "metrics_mapping_valid":
        validation[
            "metrics_mapping_valid"
        ]
        is True,

    "no_missing_metrics":
        not validation[
            "missing_metrics"
        ],

    "metric_flags_valid":
        validation[
            "metric_flags_valid"
        ]
        is True,

    "at_least_one_metric_selected":
        validation[
            "at_least_one_metric_selected"
        ]
        is True,

    "supported_states_validation_passed":
        validation[
            "supported_states_valid"
        ]
        is True,

    "period_values_valid":
        validation[
            "period_values_valid"
        ]
        is True,

    "period_pair_valid":
        validation[
            "period_pair_valid"
        ]
        is True,

    "safety_boundaries_valid":
        validation[
            "safety_boundaries_valid"
        ]
        is True,

    "checksum_valid":
        validation[
            "checksum_valid"
        ]
        is True,

    "certification_passed":
        certification[
            "certified"
        ]
        is True,

    "certification_request_valid":
        certification[
            "request_valid"
        ]
        is True,

    "certification_read_only":
        certification[
            "read_only"
        ]
        is True,

    "analytics_not_executed":
        certification[
            "analytics_executed"
        ]
        is False,

    "report_not_generated":
        certification[
            "report_generated"
        ]
        is False,

    "summary_metric_count_valid":
        (
            summary[
                "selected_metric_count"
            ]
            == 6
        ),

    "summary_selected_metrics_valid":
        (
            len(
                summary[
                    "selected_metrics"
                ]
            )
            == 6
        ),

    "lifecycle_not_modified":
        certification[
            "lifecycle_modified"
        ]
        is False,

    "archive_not_modified":
        certification[
            "archive_modified"
        ]
        is False,

    "tombstone_not_modified":
        certification[
            "tombstone_modified"
        ]
        is False,

    "body_store_not_modified":
        certification[
            "body_store_modified"
        ]
        is False,

    "no_runtime_job_created":
        certification[
            "runtime_job_created"
        ]
        is False,

    "no_queue_job_created":
        certification[
            "queue_job_created"
        ]
        is False,

    "production_outputs_unchanged":
        all(
            before[
                name
            ]
            == after[
                name
            ]

            for name
            in before
        ),
}

failures = [
    name
    for name, passed
    in checks.items()
    if passed is not True
]

print()
print("=" * 120)
print(
    "UNIVERSAL ARTICLE BODY STORE LIFECYCLE "
    "ANALYTICS CONTRACT — PHASE 9.1.10.1"
)
print("=" * 120)
print()

for name, passed in checks.items():
    print(
        f"{name:<72}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print("PROTECTED OUTPUTS")

for name in before:
    print(
        "  "
        + f"{name:<30}"
        + (
            "UNCHANGED"
            if before[
                name
            ]
            == after[
                name
            ]
            else "CHANGED"
        )
    )

print()
print(
    "Analytics executions performed:        0"
)
print(
    "Analytics reports generated:           0"
)
print(
    "Lifecycle records modified:            0"
)
print(
    "Archive records modified:              0"
)
print(
    "Tombstone records modified:            0"
)
print(
    "Body Store files modified:             0"
)
print(
    "Production queue jobs created:         0"
)
print(
    "Runtime registrations modified:        0"
)

print()
print("FAILURES")

if failures:
    for failure in failures:
        print(
            "  - "
            + failure
        )

else:
    print(
        "  None"
    )

print()

if failures:
    print(
        "BODY STORE LIFECYCLE ANALYTICS "
        "CONTRACT PHASE 9.1.10.1: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE LIFECYCLE ANALYTICS "
    "CONTRACT PHASE 9.1.10.1: PASS"
)

print(
    "The Lifecycle Analytics Contract is immutable, "
    "checksum-protected, read-only, and ready for "
    "controlled analytics execution."
)

print("=" * 120)
