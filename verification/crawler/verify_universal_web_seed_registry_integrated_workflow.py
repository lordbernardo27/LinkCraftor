from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.server.crawler import (
    SeedProtectionDecision,
    UniversalWebSeedStatus,
    archive_seed,
    disable_seed,
    enable_seed,
    get_universal_web_seed,
    inspect_seed_protection,
    protect_universal_web_seed,
    register_universal_web_seed,
    restore_seed,
    universal_web_seed_store_path,
    update_metadata,
    update_priority,
)


ROOT = PROJECT_ROOT

CRAWLER_DIR = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
)

COMPONENT_PATHS = [
    CRAWLER_DIR / "seed_models.py",
    CRAWLER_DIR / "seed_repository.py",
    CRAWLER_DIR / "seed_registration_engine.py",
    CRAWLER_DIR / "seed_controls.py",
    CRAWLER_DIR / "seed_protection.py",
    CRAWLER_DIR / "__init__.py",
]


TEST_WORKSPACE_ID = (
    "ws_seed_registry_integrated_workflow_test"
)

ISOLATION_WORKSPACE_ID = (
    "ws_seed_registry_integrated_isolation_test"
)

PRIMARY_SEED_ID = (
    "seed_integrated_primary"
)

DUPLICATE_SEED_ID = (
    "seed_integrated_duplicate"
)

ISOLATION_SEED_ID = (
    "seed_integrated_isolation"
)


results: list[dict[str, Any]] = []


def check(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise AssertionError(message)


def record(
    name: str,
    detail: str = "",
) -> None:
    results.append(
        {
            "check": name,
            "passed": True,
            "detail": detail,
        }
    )

    print(f"[PASS] {name}")

    if detail:
        print(f"       {detail}")


def remove_workspace_store(
    workspace_id: str,
) -> None:
    path = universal_web_seed_store_path(
        workspace_id
    )

    if path.exists():
        path.unlink()


def cleanup() -> None:
    remove_workspace_store(
        TEST_WORKSPACE_ID
    )

    remove_workspace_store(
        ISOLATION_WORKSPACE_ID
    )


def require_seed(
    *,
    workspace_id: str,
    seed_id: str,
):
    seed = get_universal_web_seed(
        workspace_id=workspace_id,
        seed_id=seed_id,
    )

    check(
        seed is not None,
        (
            "Expected seed could not be loaded: "
            f"{workspace_id}/{seed_id}"
        ),
    )

    return seed


print("")
print("============================================================")
print(" PHASE 1.6.2 - UNIVERSAL WEB SEED REGISTRY")
print(" INTEGRATED WORKFLOW VERIFICATION")
print("============================================================")
print("")

cleanup()

try:
    # --------------------------------------------------------
    # 1. COMPONENT COMPILATION
    # --------------------------------------------------------

    for path in COMPONENT_PATHS:
        check(
            path.is_file(),
            f"Required crawler component is missing: {path}",
        )

        py_compile.compile(
            str(path),
            doraise=True,
        )

    record(
        "all integrated registry components exist and compile",
    )

    # --------------------------------------------------------
    # 2. REGISTER PRIMARY SEED
    # --------------------------------------------------------

    registration = register_universal_web_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_type="url",
        original_value=(
            "https://example.com/integrated-article"
        ),
        seed_id=PRIMARY_SEED_ID,
        crawler_session_id=(
            "crawl_session_integrated_workflow"
        ),
        priority=100,
        registered_by=(
            "integrated_workflow_verification"
        ),
        registered_source=(
            "registry_certification"
        ),
        metadata={
            "workflow": "integrated_registry_test",
            "initial_tag": "primary",
        },
    )

    check(
        registration.get("ok") is True,
        "Primary seed registration did not return ok=True.",
    )

    check(
        registration.get("seed_id")
        == PRIMARY_SEED_ID,
        "Primary seed ID was not preserved.",
    )

    check(
        registration.get("created") is True,
        "Primary seed was not reported as newly created.",
    )

    record(
        "primary seed registers successfully",
        PRIMARY_SEED_ID,
    )

    # --------------------------------------------------------
    # 3. RELOAD PRIMARY SEED
    # --------------------------------------------------------

    primary = require_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
    )

    check(
        primary.status
        == UniversalWebSeedStatus.REGISTERED,
        "New primary seed is not registered.",
    )

    check(
        primary.enabled is True,
        "New primary seed is not enabled.",
    )

    check(
        primary.priority == 100,
        "New primary seed priority is incorrect.",
    )

    check(
        primary.original_value
        == "https://example.com/integrated-article",
        "Primary original value is incorrect.",
    )

    record(
        "primary seed reloads from certified repository",
    )

    immutable_snapshot = {
        "seed_id": primary.seed_id,
        "workspace_id": primary.workspace_id,
        "seed_type": primary.seed_type.value,
        "original_value": primary.original_value,
        "crawler_session_id": (
            primary.crawler_session_id
        ),
        "registered_by": primary.registered_by,
        "registered_source": (
            primary.registered_source
        ),
        "registered_at": primary.registered_at,
        "created_at": primary.created_at,
    }

    # --------------------------------------------------------
    # 4. PROTECT UNIQUE PRIMARY SEED
    # --------------------------------------------------------

    initial_inspection = inspect_seed_protection(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
    )

    check(
        initial_inspection.get("decision")
        == SeedProtectionDecision.ALLOW.value,
        "Unique primary seed was not allowed.",
    )

    check(
        initial_inspection.get("blocking") is False,
        "Unique primary seed was incorrectly blocked.",
    )

    check(
        initial_inspection.get("match_count") == 0,
        "Unique primary seed unexpectedly has matches.",
    )

    check(
        initial_inspection.get("persisted") is False,
        "Read-only protection inspection persisted evidence.",
    )

    record(
        "unique primary seed passes read-only protection",
    )

    initial_protection = protect_universal_web_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
    )

    check(
        initial_protection.get("persisted") is True,
        "Primary protection evidence was not persisted.",
    )

    check(
        initial_protection.get("decision")
        == SeedProtectionDecision.ALLOW.value,
        "Persisted primary protection decision is incorrect.",
    )

    primary = require_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
    )

    initial_protection_metadata = (
        primary.metadata.get(
            "seed_protection"
        )
    )

    check(
        isinstance(
            initial_protection_metadata,
            dict,
        ),
        "Primary seed lacks structured protection evidence.",
    )

    check(
        initial_protection_metadata.get(
            "evaluated"
        )
        is True,
        "Protection metadata is not marked evaluated.",
    )

    record(
        "primary protection evidence persists",
    )

    # --------------------------------------------------------
    # 5. REGISTER CANONICAL DUPLICATE
    # --------------------------------------------------------

    duplicate_registration = (
        register_universal_web_seed(
            workspace_id=TEST_WORKSPACE_ID,
            seed_type="url",
            original_value=(
                "HTTPS://EXAMPLE.COM/"
                "integrated-article/#section"
            ),
            seed_id=DUPLICATE_SEED_ID,
            priority=50,
            registered_by=(
                "integrated_workflow_verification"
            ),
            registered_source=(
                "registry_certification"
            ),
        )
    )

    check(
        duplicate_registration.get("created")
        is True,
        "Duplicate test record was not registered.",
    )

    duplicate_inspection = inspect_seed_protection(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=DUPLICATE_SEED_ID,
    )

    check(
        duplicate_inspection.get("decision")
        == SeedProtectionDecision
        .BLOCK_DUPLICATE.value,
        "Canonical duplicate was not blocked.",
    )

    check(
        duplicate_inspection.get("blocking")
        is True,
        "Canonical duplicate was not marked blocking.",
    )

    check(
        duplicate_inspection.get("match_count", 0)
        >= 1,
        "Canonical duplicate has no match record.",
    )

    duplicate_match_ids = {
        str(match.get("seed_id"))
        for match
        in duplicate_inspection.get(
            "matches",
            [],
        )
    }

    check(
        PRIMARY_SEED_ID in duplicate_match_ids,
        "Duplicate protection did not identify primary seed.",
    )

    record(
        "canonical duplicate is detected and blocked",
    )

    duplicate_protection = protect_universal_web_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=DUPLICATE_SEED_ID,
    )

    check(
        duplicate_protection.get("persisted")
        is True,
        "Duplicate protection evidence was not persisted.",
    )

    check(
        duplicate_protection.get("decision")
        == SeedProtectionDecision
        .BLOCK_DUPLICATE.value,
        "Persisted duplicate decision is incorrect.",
    )

    record(
        "duplicate blocking evidence persists",
    )

    # --------------------------------------------------------
    # 6. WORKSPACE ISOLATION
    # --------------------------------------------------------

    isolation_registration = (
        register_universal_web_seed(
            workspace_id=ISOLATION_WORKSPACE_ID,
            seed_type="url",
            original_value=(
                "https://example.com/integrated-article"
            ),
            seed_id=ISOLATION_SEED_ID,
            priority=100,
            registered_by=(
                "integrated_workflow_verification"
            ),
            registered_source=(
                "registry_certification"
            ),
        )
    )

    check(
        isolation_registration.get("created")
        is True,
        "Isolation seed registration failed.",
    )

    isolation_inspection = inspect_seed_protection(
        workspace_id=ISOLATION_WORKSPACE_ID,
        seed_id=ISOLATION_SEED_ID,
    )

    check(
        isolation_inspection.get("decision")
        == SeedProtectionDecision.ALLOW.value,
        "Cross-workspace target incorrectly caused a block.",
    )

    check(
        isolation_inspection.get("match_count")
        == 0,
        "Cross-workspace records appeared as matches.",
    )

    record(
        "integrated registry preserves workspace isolation",
    )

    # --------------------------------------------------------
    # 7. DISABLE PRIMARY SEED
    # --------------------------------------------------------

    disabled_result = disable_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
        actor=(
            "integrated_workflow_verification"
        ),
        reason=(
            "Verify registered-to-disabled transition."
        ),
        metadata={
            "workflow_step": "disable",
        },
    )

    check(
        disabled_result.get("current_status")
        == "disabled",
        "Disable result status is incorrect.",
    )

    check(
        disabled_result.get("enabled") is False,
        "Disabled result still reports enabled=True.",
    )

    primary = require_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
    )

    check(
        primary.status
        == UniversalWebSeedStatus.DISABLED,
        "Primary seed did not persist disabled status.",
    )

    check(
        primary.enabled is False,
        "Primary seed remained enabled after disable.",
    )

    check(
        primary.disabled_at is not None,
        "Primary seed lacks disabled_at timestamp.",
    )

    record(
        "registered seed disables and persists correctly",
    )

    # --------------------------------------------------------
    # 8. ENABLE PRIMARY SEED
    # --------------------------------------------------------

    enabled_result = enable_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
        actor=(
            "integrated_workflow_verification"
        ),
        reason=(
            "Verify disabled-to-registered transition."
        ),
        metadata={
            "workflow_step": "enable",
        },
    )

    check(
        enabled_result.get("current_status")
        == "registered",
        "Enable result status is incorrect.",
    )

    check(
        enabled_result.get("enabled") is True,
        "Enable result does not report enabled=True.",
    )

    primary = require_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
    )

    check(
        primary.status
        == UniversalWebSeedStatus.REGISTERED,
        "Primary seed did not return to registered.",
    )

    check(
        primary.enabled is True,
        "Primary seed did not persist enabled state.",
    )

    check(
        primary.enabled_at is not None,
        "Enabled primary seed lacks enabled_at.",
    )

    record(
        "disabled seed enables and persists correctly",
    )

    # --------------------------------------------------------
    # 9. UPDATE PRIORITY
    # --------------------------------------------------------

    priority_result = update_priority(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
        priority=750,
        actor=(
            "integrated_workflow_verification"
        ),
        reason=(
            "Verify priority update through Seed Controls."
        ),
        metadata={
            "workflow_step": "update_priority",
        },
    )

    check(
        priority_result.get("previous_priority")
        == 100,
        "Previous priority in result is incorrect.",
    )

    check(
        priority_result.get("current_priority")
        == 750,
        "Current priority in result is incorrect.",
    )

    primary = require_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
    )

    check(
        primary.priority == 750,
        "Updated priority did not persist.",
    )

    check(
        primary.status
        == UniversalWebSeedStatus.REGISTERED,
        "Priority update changed lifecycle status.",
    )

    record(
        "priority update persists without lifecycle mutation",
    )

    # --------------------------------------------------------
    # 10. UPDATE METADATA
    # --------------------------------------------------------

    metadata_result = update_metadata(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
        metadata_updates={
            "department": "crawler_operations",
            "tags": [
                "integrated",
                "certification",
            ],
            "review_note": (
                "Registry integrated workflow verified."
            ),
        },
        actor=(
            "integrated_workflow_verification"
        ),
        reason=(
            "Verify operational metadata update."
        ),
    )

    check(
        metadata_result.get("changed") is True,
        "Metadata update did not report changed=True.",
    )

    primary = require_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
    )

    check(
        primary.metadata.get("department")
        == "crawler_operations",
        "Department metadata did not persist.",
    )

    check(
        primary.metadata.get("tags")
        == [
            "integrated",
            "certification",
        ],
        "Tags metadata did not persist.",
    )

    check(
        primary.metadata.get("review_note")
        == "Registry integrated workflow verified.",
        "Review-note metadata did not persist.",
    )

    check(
        "seed_protection" in primary.metadata,
        (
            "Metadata update removed previously persisted "
            "protection evidence."
        ),
    )

    record(
        "operational metadata updates while preserving protection evidence",
    )

    # --------------------------------------------------------
    # 11. ARCHIVE PRIMARY SEED
    # --------------------------------------------------------

    archived_result = archive_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
        actor=(
            "integrated_workflow_verification"
        ),
        reason=(
            "Verify registered-to-archived transition."
        ),
        metadata={
            "workflow_step": "archive",
        },
    )

    check(
        archived_result.get("current_status")
        == "archived",
        "Archive result status is incorrect.",
    )

    check(
        archived_result.get("enabled") is False,
        "Archived result still reports enabled=True.",
    )

    primary = require_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
    )

    check(
        primary.status
        == UniversalWebSeedStatus.ARCHIVED,
        "Primary seed did not persist archived status.",
    )

    check(
        primary.enabled is False,
        "Archived seed remained enabled.",
    )

    check(
        primary.archived_at is not None,
        "Archived seed lacks archived_at timestamp.",
    )

    record(
        "registered seed archives and persists correctly",
    )

    # --------------------------------------------------------
    # 12. RESTORE PRIMARY SEED
    # --------------------------------------------------------

    restored_result = restore_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
        actor=(
            "integrated_workflow_verification"
        ),
        reason=(
            "Verify archived-to-disabled restoration."
        ),
        metadata={
            "workflow_step": "restore",
        },
    )

    check(
        restored_result.get("current_status")
        == "disabled",
        "Restored seed did not return to disabled.",
    )

    check(
        restored_result.get("enabled") is False,
        "Restored seed was automatically enabled.",
    )

    primary = require_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
    )

    check(
        primary.status
        == UniversalWebSeedStatus.DISABLED,
        "Restored status did not persist as disabled.",
    )

    check(
        primary.enabled is False,
        "Restored seed persisted as enabled.",
    )

    check(
        primary.archived_at is None,
        "Restoration did not clear archived_at.",
    )

    check(
        primary.metadata.get("restored_at")
        is not None,
        "Restoration evidence was not recorded.",
    )

    record(
        "archived seed restores safely to disabled",
    )

    # --------------------------------------------------------
    # 13. EXPLICITLY ENABLE RESTORED PRIMARY SEED
    # --------------------------------------------------------

    final_enable_result = enable_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
        actor=(
            "integrated_workflow_verification"
        ),
        reason=(
            "Explicitly enable restored seed."
        ),
        metadata={
            "workflow_step": "final_enable",
        },
    )

    check(
        final_enable_result.get("current_status")
        == "registered",
        "Final enable did not return seed to registered.",
    )

    check(
        final_enable_result.get("enabled") is True,
        "Final enable did not activate the seed.",
    )

    record(
        "restored seed requires and accepts explicit enable",
    )

    # --------------------------------------------------------
    # 14. FINAL RELOAD AND INTEGRITY REVIEW
    # --------------------------------------------------------

    final_seed = require_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=PRIMARY_SEED_ID,
    )

    check(
        final_seed.status
        == UniversalWebSeedStatus.REGISTERED,
        "Final seed status is not registered.",
    )

    check(
        final_seed.enabled is True,
        "Final seed is not enabled.",
    )

    check(
        final_seed.priority == 750,
        "Final priority was not preserved.",
    )

    check(
        final_seed.metadata.get("department")
        == "crawler_operations",
        "Final operational metadata was not preserved.",
    )

    check(
        isinstance(
            final_seed.metadata.get(
                "seed_protection"
            ),
            dict,
        ),
        "Final seed lost protection evidence.",
    )

    record(
        "final seed state reloads with all integrated evidence",
    )

    # --------------------------------------------------------
    # 15. IMMUTABLE FIELDS
    # --------------------------------------------------------

    final_immutable_snapshot = {
        "seed_id": final_seed.seed_id,
        "workspace_id": final_seed.workspace_id,
        "seed_type": final_seed.seed_type.value,
        "original_value": final_seed.original_value,
        "crawler_session_id": (
            final_seed.crawler_session_id
        ),
        "registered_by": final_seed.registered_by,
        "registered_source": (
            final_seed.registered_source
        ),
        "registered_at": final_seed.registered_at,
        "created_at": final_seed.created_at,
    }

    check(
        final_immutable_snapshot
        == immutable_snapshot,
        (
            "One or more immutable seed fields changed "
            "during the integrated workflow."
        ),
    )

    record(
        "immutable seed identity and provenance remain unchanged",
    )

    # --------------------------------------------------------
    # 16. CONTROL HISTORY
    # --------------------------------------------------------

    control_history = final_seed.metadata.get(
        "control_history"
    )

    check(
        isinstance(control_history, list),
        "Final seed lacks control-history list.",
    )

    expected_operations = [
        "disable",
        "enable",
        "update_priority",
        "update_metadata",
        "archive",
        "restore",
        "enable",
    ]

    actual_operations = [
        str(event.get("operation"))
        for event in control_history
        if isinstance(event, dict)
    ]

    check(
        actual_operations
        == expected_operations,
        (
            "Control history sequence is incorrect: "
            f"{actual_operations!r}"
        ),
    )

    check(
        len(control_history)
        == len(expected_operations),
        "Unexpected number of control-history events.",
    )

    record(
        "complete control-history sequence is preserved",
        " → ".join(actual_operations),
    )

    # --------------------------------------------------------
    # 17. DUPLICATE RECORD REMAINS INDEPENDENT
    # --------------------------------------------------------

    duplicate_seed = require_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=DUPLICATE_SEED_ID,
    )

    check(
        duplicate_seed.seed_id
        != final_seed.seed_id,
        "Duplicate and primary seed identities were merged.",
    )

    check(
        duplicate_seed.metadata.get(
            "protection_blocking"
        )
        is True,
        "Duplicate blocking evidence was not preserved.",
    )

    check(
        final_seed.metadata.get(
            "protection_blocking"
        )
        is False,
        "Primary seed was incorrectly marked blocking.",
    )

    record(
        "protection blocks without deleting or merging seed records",
    )

finally:
    cleanup()


# ------------------------------------------------------------
# 18. CLEANUP VERIFICATION
# ------------------------------------------------------------

remaining_stores = [
    str(
        universal_web_seed_store_path(
            workspace_id
        )
    )
    for workspace_id in (
        TEST_WORKSPACE_ID,
        ISOLATION_WORKSPACE_ID,
    )
    if universal_web_seed_store_path(
        workspace_id
    ).exists()
]

check(
    not remaining_stores,
    (
        "Integrated workflow test stores remain: "
        + ", ".join(remaining_stores)
    ),
)

record(
    "all integrated workflow test repositories removed",
)


# ------------------------------------------------------------
# FINAL REPORT
# ------------------------------------------------------------

failed = [
    result
    for result in results
    if result.get("passed") is not True
]

report = {
    "ok": not failed,
    "component": (
        "universal_web_seed_registry_integrated_workflow"
    ),
    "schema_version": (
        "universal_web_seed_registry_integrated_workflow.v1"
    ),
    "pipeline_stage": (
        "Universal Web Seed Registry"
    ),
    "workflow": [
        "register",
        "reload",
        "protect",
        "detect_duplicate",
        "verify_workspace_isolation",
        "disable",
        "enable",
        "update_priority",
        "update_metadata",
        "archive",
        "restore_to_disabled",
        "explicit_enable",
        "final_reload",
        "verify_history",
        "cleanup",
    ],
    "checks_executed": len(results),
    "checks_passed": (
        len(results) - len(failed)
    ),
    "checks_failed": len(failed),
    "workflow_status": (
        "ready_for_boundary_verification"
        if not failed
        else "integrated_workflow_failed"
    ),
    "next_step": (
        "Phase 1.6.3 Boundary Verification"
    ),
}

print("")
print("============================================================")
print(" INTEGRATED WORKFLOW SUMMARY")
print("============================================================")
print(
    f"Checks executed: {report['checks_executed']}"
)
print(
    f"Checks passed:   {report['checks_passed']}"
)
print(
    f"Checks failed:   {report['checks_failed']}"
)

if failed:
    print("")
    print(
        "UNIVERSAL WEB SEED REGISTRY "
        "INTEGRATED WORKFLOW: FAIL"
    )

    raise SystemExit(1)

print("")
print(
    "UNIVERSAL WEB SEED REGISTRY "
    "INTEGRATED WORKFLOW: PASS"
)

print("")
print(
    json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
    )
)
