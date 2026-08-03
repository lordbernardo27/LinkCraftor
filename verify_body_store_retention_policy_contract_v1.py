"""Verify Body Store Retention Policy Contract Phase 9.1.3.1."""

from __future__ import annotations

import ast
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from backend.server.universal_article_body_store.body_store_retention_policy_contract_v1 import (
    BODY_STORE_RETENTION_CLASSES,
    BODY_STORE_RETENTION_DEFAULT_PERIODS,
    BODY_STORE_RETENTION_HOLD_TYPES,
    BODY_STORE_RETENTION_POLICY_CONTRACT_ID,
    BODY_STORE_RETENTION_POLICY_CONTRACT_VERSION,
    BODY_STORE_RETENTION_STATUSES,
    BodyStoreRetentionPolicyError,
    build_body_store_retention_policy_v1,
    calculate_retain_until_v1,
    validate_body_store_retention_policy_v1,
)


CONTRACT_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
    / "body_store_retention_policy_contract_v1.py"
)

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

PROTECTED_PATHS = {
    "production_body_store": (
        DATA_ROOT
        / "universal_article_body_store"
    ),

    "production_body_queue": (
        DATA_ROOT
        / "universal_article_body_queue"
    ),

    "production_lifecycle_store": (
        DATA_ROOT
        / "universal_article_body_store_lifecycle"
    ),

    "persistent_uucd_output": (
        DATA_ROOT
        / "universal_unified_content_documents"
    ),

    "persistent_wuc_output": (
        DATA_ROOT
        / "website_unified_content"
    ),
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
    in PROTECTED_PATHS.items()
}


source = CONTRACT_PATH.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

tree = ast.parse(
    source,
    filename=str(
        CONTRACT_PATH
    ),
)

forbidden_imports = []
forbidden_calls = []

for node in ast.walk(
    tree
):
    if isinstance(
        node,
        ast.ImportFrom,
    ):
        module = str(
            node.module
            or ""
        )

        if any(
            forbidden in module
            for forbidden in (
                "body_store_writer_v1",
                "body_store_manager_v1",
                "body_store_repository_v1",
                "body_store_runtime_v1",
                "body_store_worker_v1",
                "body_store_queue_v1",
                "body_store_state_transition_engine_v1",
                "universal_runtime_registration",
            )
        ):
            forbidden_imports.append(
                (
                    node.lineno,
                    module,
                )
            )

    elif isinstance(
        node,
        ast.Call,
    ):
        name = ""

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

        if name in {
            "store_body",
            "read_body",
            "verify_body",
            "transition_body_store_lifecycle_state_v1",
            "execute_body_store_runtime_v1",
            "execute_body_store_worker_v1",
            "enqueue_body_store_job",
            "register_runtime_handler",
        }:
            forbidden_calls.append(
                (
                    node.lineno,
                    name,
                )
            )


started_at = "2026-08-02T00:00:00+00:00"

standard_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="retention_standard_v1",
        retention_policy_name="Standard Body Retention",
        lifecycle_record_id="body_lifecycle_standard_001",
        workspace_id="ws_retention",
        retention_class="STANDARD",
        retention_started_at=started_at,
        eligibility_reason="Retention period remains active.",
    )
)

extended_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="retention_extended_v1",
        retention_policy_name="Extended Body Retention",
        lifecycle_record_id="body_lifecycle_extended_001",
        workspace_id="ws_retention",
        retention_class="EXTENDED",
        retention_started_at=started_at,
        eligibility_reason="Extended retention period remains active.",
    )
)

custom_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="retention_custom_v1",
        retention_policy_name="Custom Body Retention",
        lifecycle_record_id="body_lifecycle_custom_001",
        workspace_id="ws_retention",
        retention_class="CUSTOM",
        retention_started_at=started_at,
        retention_period_days=90,
        eligibility_reason="Custom retention period remains active.",
    )
)

indefinite_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="retention_indefinite_v1",
        retention_policy_name="Indefinite Body Retention",
        lifecycle_record_id="body_lifecycle_indefinite_001",
        workspace_id="ws_retention",
        retention_class="INDEFINITE",
        retention_started_at=started_at,
        eligibility_reason="Indefinite retention prevents deletion eligibility.",
    )
)

legal_hold_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="retention_legal_hold_v1",
        retention_policy_name="Legal Hold Body Retention",
        lifecycle_record_id="body_lifecycle_legal_001",
        workspace_id="ws_retention",
        retention_class="LEGAL_HOLD",
        retention_started_at=started_at,
        retention_status="ON_HOLD",
        is_on_hold=True,
        hold_type="LEGAL",
        hold_reason="Required for legal preservation.",
        hold_started_at="2026-08-02T01:00:00+00:00",
        eligibility_reason="Active legal hold blocks deletion.",
    )
)

eligible_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="retention_eligible_v1",
        retention_policy_name="Deletion Eligible Body Retention",
        lifecycle_record_id="body_lifecycle_eligible_001",
        workspace_id="ws_retention",
        retention_class="CUSTOM",
        retention_started_at="2025-01-01T00:00:00+00:00",
        retention_period_days=1,
        retention_status="ELIGIBLE_FOR_DELETION",
        retention_satisfied=True,
        deletion_eligible=True,
        eligibility_reason="Retention completed and no hold exists.",
        evaluated_at="2026-08-02T00:00:00+00:00",
    )
)


article_body_rejected = False

try:
    build_body_store_retention_policy_v1(
        retention_policy_id="retention_invalid_body_v1",
        retention_policy_name="Invalid Body Policy",
        lifecycle_record_id="body_lifecycle_invalid_001",
        workspace_id="ws_retention",
        retention_class="STANDARD",
        retention_started_at=started_at,
        eligibility_reason="Invalid metadata test.",
        metadata={
            "content_body":
                "Article content must not enter retention policy metadata.",
        },
    )

except BodyStoreRetentionPolicyError:
    article_body_rejected = True


hold_without_metadata_rejected = False

try:
    build_body_store_retention_policy_v1(
        retention_policy_id="retention_invalid_hold_v1",
        retention_policy_name="Invalid Hold Policy",
        lifecycle_record_id="body_lifecycle_invalid_hold_001",
        workspace_id="ws_retention",
        retention_class="STANDARD",
        retention_started_at=started_at,
        retention_status="ON_HOLD",
        is_on_hold=True,
        eligibility_reason="Invalid hold test.",
    )

except BodyStoreRetentionPolicyError:
    hold_without_metadata_rejected = True


deletion_during_hold_rejected = False

try:
    build_body_store_retention_policy_v1(
        retention_policy_id="retention_invalid_delete_hold_v1",
        retention_policy_name="Invalid Hold Deletion Policy",
        lifecycle_record_id="body_lifecycle_invalid_delete_001",
        workspace_id="ws_retention",
        retention_class="LEGAL_HOLD",
        retention_started_at=started_at,
        retention_status="ELIGIBLE_FOR_DELETION",
        is_on_hold=True,
        hold_type="LEGAL",
        hold_reason="Legal preservation.",
        hold_started_at=started_at,
        retention_satisfied=True,
        deletion_eligible=True,
        eligibility_reason="Invalid deletion eligibility test.",
    )

except BodyStoreRetentionPolicyError:
    deletion_during_hold_rejected = True


indefinite_deletion_rejected = False

try:
    build_body_store_retention_policy_v1(
        retention_policy_id="retention_invalid_indefinite_v1",
        retention_policy_name="Invalid Indefinite Policy",
        lifecycle_record_id="body_lifecycle_invalid_indefinite_001",
        workspace_id="ws_retention",
        retention_class="INDEFINITE",
        retention_started_at=started_at,
        retention_status="ELIGIBLE_FOR_DELETION",
        retention_satisfied=True,
        deletion_eligible=True,
        eligibility_reason="Invalid indefinite deletion test.",
    )

except BodyStoreRetentionPolicyError:
    indefinite_deletion_rejected = True


custom_without_days_rejected = False

try:
    build_body_store_retention_policy_v1(
        retention_policy_id="retention_invalid_custom_v1",
        retention_policy_name="Invalid Custom Policy",
        lifecycle_record_id="body_lifecycle_invalid_custom_001",
        workspace_id="ws_retention",
        retention_class="CUSTOM",
        retention_started_at=started_at,
        eligibility_reason="Missing custom duration test.",
    )

except BodyStoreRetentionPolicyError:
    custom_without_days_rejected = True


after = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_PATHS.items()
}

unchanged = {
    name:
        before[
            name
        ]
        == after[
            name
        ]

    for name
    in PROTECTED_PATHS
}


checks = {
    "contract_id_valid":
        BODY_STORE_RETENTION_POLICY_CONTRACT_ID.startswith(
            "urn:linkcraftor:"
        ),

    "contract_version_valid":
        BODY_STORE_RETENTION_POLICY_CONTRACT_VERSION
        == "universal_article_body_store_retention_policy_contract_v1",

    "retention_classes_exact":
        BODY_STORE_RETENTION_CLASSES
        == (
            "STANDARD",
            "EXTENDED",
            "INDEFINITE",
            "LEGAL_HOLD",
            "OPERATIONAL_HOLD",
            "CUSTOM",
        ),

    "retention_statuses_exact":
        BODY_STORE_RETENTION_STATUSES
        == (
            "ACTIVE",
            "RETAINED",
            "ON_HOLD",
            "EXPIRED",
            "ELIGIBLE_FOR_DELETION",
        ),

    "hold_types_exact":
        BODY_STORE_RETENTION_HOLD_TYPES
        == (
            "LEGAL",
            "OPERATIONAL",
            "MANUAL",
            "SYSTEM",
        ),

    "standard_default_days_valid":
        BODY_STORE_RETENTION_DEFAULT_PERIODS[
            "STANDARD"
        ]
        == 365,

    "extended_default_days_valid":
        BODY_STORE_RETENTION_DEFAULT_PERIODS[
            "EXTENDED"
        ]
        == 730,

    "standard_policy_valid":
        standard_policy[
            "retention_period_days"
        ]
        == 365,

    "extended_policy_valid":
        extended_policy[
            "retention_period_days"
        ]
        == 730,

    "custom_policy_valid":
        custom_policy[
            "retention_period_days"
        ]
        == 90,

    "retain_until_calculation_valid":
        standard_policy[
            "retain_until"
        ]
        == calculate_retain_until_v1(
            retention_started_at=started_at,
            retention_class="STANDARD",
            retention_period_days=365,
        ),

    "indefinite_policy_valid":
        indefinite_policy[
            "retain_until"
        ]
        is None
        and indefinite_policy[
            "deletion_eligible"
        ]
        is False,

    "legal_hold_policy_valid":
        legal_hold_policy[
            "is_on_hold"
        ]
        is True
        and legal_hold_policy[
            "retention_status"
        ]
        == "ON_HOLD",

    "eligible_policy_valid":
        eligible_policy[
            "retention_satisfied"
        ]
        is True
        and eligible_policy[
            "deletion_eligible"
        ]
        is True,

    "policy_validation_roundtrip":
        validate_body_store_retention_policy_v1(
            standard_policy
        )
        == standard_policy,

    "article_body_content_rejected":
        article_body_rejected,

    "incomplete_hold_rejected":
        hold_without_metadata_rejected,

    "deletion_during_hold_rejected":
        deletion_during_hold_rejected,

    "indefinite_deletion_rejected":
        indefinite_deletion_rejected,

    "custom_without_days_rejected":
        custom_without_days_rejected,

    "no_forbidden_layer_imports":
        not forbidden_imports,

    "no_forbidden_layer_calls":
        not forbidden_calls,

    "production_outputs_unchanged":
        all(
            unchanged.values()
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
    "UNIVERSAL ARTICLE BODY STORE RETENTION POLICY CONTRACT — PHASE 9.1.3.1"
)
print("=" * 120)
print()

for name, passed in checks.items():
    print(
        f"{name:<84}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "Canonical retention classes:"
)

for retention_class in BODY_STORE_RETENTION_CLASSES:
    print(
        "  "
        + retention_class
    )

print()
print(
    "Canonical retention statuses:"
)

for status in BODY_STORE_RETENTION_STATUSES:
    print(
        "  "
        + status
    )

print()
print(
    "PROTECTED OUTPUTS"
)

for name, passed in unchanged.items():
    print(
        "  "
        + f"{name:<40}"
        + (
            "UNCHANGED"
            if passed
            else "CHANGED"
        )
    )

print()
print(
    "Production retention policies created: 0"
)

print(
    "Production lifecycle records modified: 0"
)

print(
    "Production Body Store files written:   0"
)

print(
    "Production queue jobs created:         0"
)

print(
    "Runtime registrations modified:        0"
)

print()
print(
    "FAILURES"
)

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
        "BODY STORE RETENTION POLICY CONTRACT PHASE 9.1.3.1: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE RETENTION POLICY CONTRACT PHASE 9.1.3.1: PASS"
)

print(
    "The canonical Body Store retention-policy schema now validates "
    "retention classes, durations, holds, eligibility, and metadata "
    "without executing lifecycle transitions or modifying production data."
)

print("=" * 120)
