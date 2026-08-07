from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path
from typing import Any, Callable

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.server.crawler import (
    UNIVERSAL_WEB_SEED_PROTECTION_SCHEMA_VERSION,
    SeedComparisonFamily,
    SeedProtectionClassification,
    SeedProtectionDecision,
    archive_seed,
    build_seed_comparison_target,
    explain_universal_web_seed_protection_v1,
    generate_seed_target_fingerprint,
    get_universal_web_seed,
    inspect_seed_protection,
    protect_universal_web_seed,
    register_universal_web_seed,
    universal_web_seed_store_path,
)


ROOT = PROJECT_ROOT

PROTECTION_PATH = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
    / "seed_protection.py"
)

INIT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
    / "__init__.py"
)


WORKSPACES = {
    "allow": "ws_seed_protection_allow_test",
    "exact": "ws_seed_protection_exact_test",
    "canonical": "ws_seed_protection_canonical_test",
    "domain": "ws_seed_protection_domain_test",
    "type_conflict": "ws_seed_protection_type_conflict_test",
    "related": "ws_seed_protection_related_test",
    "archived": "ws_seed_protection_archived_test",
    "isolation_a": "ws_seed_protection_isolation_a",
    "isolation_b": "ws_seed_protection_isolation_b",
    "persistence": "ws_seed_protection_persistence_test",
}


results: list[dict[str, Any]] = []


def record(
    name: str,
    passed: bool,
    detail: str = "",
) -> None:
    results.append(
        {
            "check": name,
            "passed": passed,
            "detail": detail,
        }
    )

    status = "PASS" if passed else "FAIL"

    print(f"[{status}] {name}")

    if detail:
        print(f"       {detail}")


def check(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise AssertionError(message)


def remove_workspace_store(
    workspace_id: str,
) -> None:
    path = universal_web_seed_store_path(
        workspace_id
    )

    if path.exists():
        path.unlink()


def cleanup_all_test_stores() -> None:
    for workspace_id in WORKSPACES.values():
        remove_workspace_store(
            workspace_id
        )


def register_seed(
    *,
    workspace_id: str,
    seed_type: str,
    original_value: str,
    seed_id: str,
) -> dict[str, Any]:
    return register_universal_web_seed(
        workspace_id=workspace_id,
        seed_type=seed_type,
        original_value=original_value,
        seed_id=seed_id,
        registered_by="seed_protection_verification",
        registered_source="verification_suite",
    )


def classifications(
    result: dict[str, Any],
) -> set[str]:
    return {
        str(match.get("classification"))
        for match in result.get(
            "matches",
            [],
        )
    }


def matching_seed_ids(
    result: dict[str, Any],
) -> set[str]:
    return {
        str(match.get("seed_id"))
        for match in result.get(
            "matches",
            [],
        )
    }


print("")
print("============================================================")
print(" PHASE 1.5.4 - UNIVERSAL WEB SEED PROTECTION")
print(" VERIFICATION")
print("============================================================")
print("")

cleanup_all_test_stores()

try:
    # --------------------------------------------------------
    # 1. FILES AND COMPILATION
    # --------------------------------------------------------

    check(
        PROTECTION_PATH.is_file(),
        "seed_protection.py is missing.",
    )

    record(
        "seed_protection.py exists",
        True,
        str(PROTECTION_PATH),
    )

    check(
        INIT_PATH.is_file(),
        "__init__.py is missing.",
    )

    record(
        "__init__.py exists",
        True,
        str(INIT_PATH),
    )

    py_compile.compile(
        str(PROTECTION_PATH),
        doraise=True,
    )

    record(
        "seed_protection.py compiles",
        True,
    )

    py_compile.compile(
        str(INIT_PATH),
        doraise=True,
    )

    record(
        "__init__.py compiles",
        True,
    )

    # --------------------------------------------------------
    # 2. SCHEMA
    # --------------------------------------------------------

    check(
        UNIVERSAL_WEB_SEED_PROTECTION_SCHEMA_VERSION
        == "universal_web_seed_protection.v1",
        "Unexpected Seed Protection schema version.",
    )

    record(
        "Seed Protection schema version is correct",
        True,
    )

    # --------------------------------------------------------
    # 3. DOMAIN COMPARISON CANONICALIZATION
    # --------------------------------------------------------

    domain_comparison = build_seed_comparison_target(
        seed_type="domain",
        original_value=(
            "HTTPS://WWW.Example.COM/path?q=1#section"
        ),
    )

    check(
        domain_comparison["comparison_family"]
        == "domain_target",
        "Domain comparison family is incorrect.",
    )

    check(
        domain_comparison["comparison_target"]
        == "example.com",
        "Domain comparison target is incorrect.",
    )

    record(
        "domain comparison canonicalization works",
        True,
        domain_comparison["comparison_target"],
    )

    # --------------------------------------------------------
    # 4. URL COMPARISON CANONICALIZATION
    # --------------------------------------------------------

    url_comparison = build_seed_comparison_target(
        seed_type="url",
        original_value=(
            "HTTPS://Example.COM:443/articles/"
            "?b=2&a=1#introduction"
        ),
    )

    check(
        url_comparison["comparison_family"]
        == "web_page_target",
        "URL comparison family is incorrect.",
    )

    check(
        url_comparison["comparison_target"]
        == "https://example.com/articles?a=1&b=2",
        (
            "URL comparison did not normalize scheme, host, "
            "port, path, query and fragment correctly."
        ),
    )

    record(
        "URL comparison canonicalization works",
        True,
        url_comparison["comparison_target"],
    )

    # --------------------------------------------------------
    # 5. SITEMAP AND FEED FAMILIES
    # --------------------------------------------------------

    sitemap_comparison = build_seed_comparison_target(
        seed_type="sitemap",
        original_value="https://Example.com/sitemap.xml#top",
    )

    feed_comparison = build_seed_comparison_target(
        seed_type="rss_feed",
        original_value="https://Example.com/feed/",
    )

    check(
        sitemap_comparison["comparison_family"]
        == "sitemap_target",
        "Sitemap comparison family is incorrect.",
    )

    check(
        feed_comparison["comparison_family"]
        == "feed_target",
        "Feed comparison family is incorrect.",
    )

    check(
        feed_comparison["comparison_target"]
        == "https://example.com/feed",
        "Feed trailing-slash normalization is incorrect.",
    )

    record(
        "sitemap and feed comparison families are correct",
        True,
    )

    # --------------------------------------------------------
    # 6. FINGERPRINTS
    # --------------------------------------------------------

    fingerprint_1 = generate_seed_target_fingerprint(
        workspace_id="ws_fingerprint_test",
        comparison_family="web_page_target",
        comparison_target="https://example.com/article",
    )

    fingerprint_2 = generate_seed_target_fingerprint(
        workspace_id="ws_fingerprint_test",
        comparison_family="web_page_target",
        comparison_target="https://example.com/article",
    )

    fingerprint_other_workspace = (
        generate_seed_target_fingerprint(
            workspace_id="ws_fingerprint_other",
            comparison_family="web_page_target",
            comparison_target="https://example.com/article",
        )
    )

    check(
        fingerprint_1.startswith("sha256:"),
        "Fingerprint does not use the sha256 prefix.",
    )

    check(
        fingerprint_1 == fingerprint_2,
        "Fingerprint generation is not deterministic.",
    )

    check(
        fingerprint_1 != fingerprint_other_workspace,
        "Fingerprints are not workspace-scoped.",
    )

    record(
        "workspace-scoped SHA-256 fingerprinting works",
        True,
        fingerprint_1,
    )

    # Verify enum input because runtime inspection uses enum values.
    enum_fingerprint = generate_seed_target_fingerprint(
        workspace_id="ws_fingerprint_enum",
        comparison_family=(
            SeedComparisonFamily.WEB_PAGE_TARGET
        ),
        comparison_target="https://example.com/article",
    )

    check(
        enum_fingerprint.startswith("sha256:"),
        "Fingerprint generator rejected enum-family input.",
    )

    record(
        "fingerprint generator accepts comparison-family enum",
        True,
    )

    # --------------------------------------------------------
    # 7. NO-CONFLICT / SELF-MATCH EXCLUSION
    # --------------------------------------------------------

    allow_workspace = WORKSPACES["allow"]

    allow_result = register_seed(
        workspace_id=allow_workspace,
        seed_type="url",
        original_value="https://example.com/unique",
        seed_id="seed_allow_unique",
    )

    allow_inspection = inspect_seed_protection(
        workspace_id=allow_workspace,
        seed_id=allow_result["seed_id"],
    )

    check(
        allow_inspection["decision"]
        == SeedProtectionDecision.ALLOW.value,
        "A unique seed was not allowed.",
    )

    check(
        allow_inspection["match_count"] == 0,
        "A seed incorrectly matched itself.",
    )

    check(
        allow_inspection["persisted"] is False,
        "Read-only inspection unexpectedly persisted evidence.",
    )

    record(
        "unique seed is allowed and self-match is excluded",
        True,
    )

    # --------------------------------------------------------
    # 8. EXACT DUPLICATE
    # --------------------------------------------------------

    exact_workspace = WORKSPACES["exact"]

    register_seed(
        workspace_id=exact_workspace,
        seed_type="url",
        original_value="https://example.com/exact",
        seed_id="seed_exact_existing",
    )

    register_seed(
        workspace_id=exact_workspace,
        seed_type="url",
        original_value="https://example.com/exact",
        seed_id="seed_exact_candidate",
    )

    exact_result = inspect_seed_protection(
        workspace_id=exact_workspace,
        seed_id="seed_exact_candidate",
    )

    check(
        exact_result["decision"]
        == SeedProtectionDecision.BLOCK_DUPLICATE.value,
        "Exact duplicate did not produce block_duplicate.",
    )

    check(
        exact_result["blocking"] is True,
        "Exact duplicate was not marked blocking.",
    )

    check(
        SeedProtectionClassification.EXACT_DUPLICATE.value
        in classifications(exact_result),
        "Exact duplicate classification is missing.",
    )

    record(
        "exact duplicate detection works",
        True,
    )

    # --------------------------------------------------------
    # 9. CANONICAL DUPLICATE
    # --------------------------------------------------------

    canonical_workspace = WORKSPACES["canonical"]

    register_seed(
        workspace_id=canonical_workspace,
        seed_type="url",
        original_value=(
            "HTTPS://EXAMPLE.COM/article/?b=2&a=1#intro"
        ),
        seed_id="seed_canonical_existing",
    )

    register_seed(
        workspace_id=canonical_workspace,
        seed_type="url",
        original_value=(
            "https://example.com/article?a=1&b=2"
        ),
        seed_id="seed_canonical_candidate",
    )

    canonical_result = inspect_seed_protection(
        workspace_id=canonical_workspace,
        seed_id="seed_canonical_candidate",
    )

    check(
        canonical_result["decision"]
        == SeedProtectionDecision.BLOCK_DUPLICATE.value,
        "Canonical duplicate did not produce block_duplicate.",
    )

    check(
        SeedProtectionClassification.CANONICAL_DUPLICATE.value
        in classifications(canonical_result),
        "Canonical duplicate classification is missing.",
    )

    record(
        "canonical duplicate detection works",
        True,
    )

    # --------------------------------------------------------
    # 10. DOMAIN DUPLICATE
    # --------------------------------------------------------

    domain_workspace = WORKSPACES["domain"]

    register_seed(
        workspace_id=domain_workspace,
        seed_type="domain",
        original_value="www.example.com",
        seed_id="seed_domain_existing",
    )

    register_seed(
        workspace_id=domain_workspace,
        seed_type="domain",
        original_value="HTTPS://EXAMPLE.COM/path",
        seed_id="seed_domain_candidate",
    )

    domain_result = inspect_seed_protection(
        workspace_id=domain_workspace,
        seed_id="seed_domain_candidate",
    )

    check(
        domain_result["decision"]
        == SeedProtectionDecision.BLOCK_DUPLICATE.value,
        "Domain duplicate did not produce block_duplicate.",
    )

    check(
        SeedProtectionClassification.DOMAIN_DUPLICATE.value
        in classifications(domain_result),
        "Domain duplicate classification is missing.",
    )

    record(
        "domain duplicate detection works",
        True,
    )

    # --------------------------------------------------------
    # 11. TYPE CONFLICT
    # --------------------------------------------------------

    type_workspace = WORKSPACES["type_conflict"]

    register_seed(
        workspace_id=type_workspace,
        seed_type="rss_feed",
        original_value="https://example.com/feed",
        seed_id="seed_feed_existing",
    )

    register_seed(
        workspace_id=type_workspace,
        seed_type="url",
        original_value="https://example.com/feed",
        seed_id="seed_url_candidate",
    )

    type_result = inspect_seed_protection(
        workspace_id=type_workspace,
        seed_id="seed_url_candidate",
    )

    check(
        type_result["decision"]
        == SeedProtectionDecision.BLOCK_TYPE_CONFLICT.value,
        "Type conflict did not produce block_type_conflict.",
    )

    check(
        SeedProtectionClassification.TYPE_CONFLICT.value
        in classifications(type_result),
        "Type-conflict classification is missing.",
    )

    record(
        "seed-type conflict detection works",
        True,
    )

    # --------------------------------------------------------
    # 12. RELATED DOMAIN
    # --------------------------------------------------------

    related_workspace = WORKSPACES["related"]

    register_seed(
        workspace_id=related_workspace,
        seed_type="domain",
        original_value="example.com",
        seed_id="seed_related_domain",
    )

    register_seed(
        workspace_id=related_workspace,
        seed_type="url",
        original_value="https://example.com/article",
        seed_id="seed_related_url",
    )

    related_result = inspect_seed_protection(
        workspace_id=related_workspace,
        seed_id="seed_related_url",
    )

    check(
        related_result["decision"]
        == SeedProtectionDecision.ALLOW.value,
        "Related domain relationship should not block.",
    )

    check(
        related_result["blocking"] is False,
        "Related domain relationship was marked blocking.",
    )

    check(
        SeedProtectionClassification.RELATED_DOMAIN.value
        in classifications(related_result),
        "Related-domain classification is missing.",
    )

    record(
        "related-domain relationship is non-blocking",
        True,
    )

    # --------------------------------------------------------
    # 13. ARCHIVED DUPLICATE POLICY
    # --------------------------------------------------------

    archived_workspace = WORKSPACES["archived"]

    register_seed(
        workspace_id=archived_workspace,
        seed_type="url",
        original_value="https://example.com/archived",
        seed_id="seed_archived_existing",
    )

    archive_seed(
        workspace_id=archived_workspace,
        seed_id="seed_archived_existing",
        actor="seed_protection_verification",
        reason="Verify archived duplicate review policy.",
    )

    register_seed(
        workspace_id=archived_workspace,
        seed_type="url",
        original_value="https://example.com/archived/",
        seed_id="seed_archived_candidate",
    )

    archived_result = inspect_seed_protection(
        workspace_id=archived_workspace,
        seed_id="seed_archived_candidate",
    )

    check(
        archived_result["decision"]
        == SeedProtectionDecision.REVIEW.value,
        "Archived duplicate did not produce review.",
    )

    check(
        archived_result["blocking"] is False,
        "Archived duplicate should not be directly blocking.",
    )

    check(
        archived_result["review_required"] is True,
        "Archived duplicate did not require review.",
    )

    record(
        "archived duplicate policy produces review",
        True,
    )

    # --------------------------------------------------------
    # 14. WORKSPACE ISOLATION
    # --------------------------------------------------------

    isolation_a = WORKSPACES["isolation_a"]
    isolation_b = WORKSPACES["isolation_b"]

    register_seed(
        workspace_id=isolation_a,
        seed_type="url",
        original_value="https://example.com/shared",
        seed_id="seed_isolation_a",
    )

    register_seed(
        workspace_id=isolation_b,
        seed_type="url",
        original_value="https://example.com/shared",
        seed_id="seed_isolation_b",
    )

    isolation_result = inspect_seed_protection(
        workspace_id=isolation_b,
        seed_id="seed_isolation_b",
    )

    check(
        isolation_result["decision"]
        == SeedProtectionDecision.ALLOW.value,
        "Seed in another workspace incorrectly caused a block.",
    )

    check(
        "seed_isolation_a"
        not in matching_seed_ids(isolation_result),
        "Cross-workspace seed appeared in protection matches.",
    )

    record(
        "Seed Protection preserves workspace isolation",
        True,
    )

    # --------------------------------------------------------
    # 15. PERSISTENCE
    # --------------------------------------------------------

    persistence_workspace = WORKSPACES["persistence"]

    register_seed(
        workspace_id=persistence_workspace,
        seed_type="url",
        original_value="https://example.com/persist",
        seed_id="seed_persistence_existing",
    )

    register_seed(
        workspace_id=persistence_workspace,
        seed_type="url",
        original_value="https://example.com/persist/",
        seed_id="seed_persistence_candidate",
    )

    before_protection = get_universal_web_seed(
        workspace_id=persistence_workspace,
        seed_id="seed_persistence_candidate",
    )

    check(
        before_protection is not None,
        "Persistence candidate could not be loaded.",
    )

    check(
        "seed_protection"
        not in before_protection.metadata,
        "Protection evidence existed before protection ran.",
    )

    protected_result = protect_universal_web_seed(
        workspace_id=persistence_workspace,
        seed_id="seed_persistence_candidate",
    )

    check(
        protected_result["operation"] == "protect",
        "Protection operation result is incorrect.",
    )

    check(
        protected_result["persisted"] is True,
        "Protection result did not confirm persistence.",
    )

    persisted_seed = get_universal_web_seed(
        workspace_id=persistence_workspace,
        seed_id="seed_persistence_candidate",
    )

    check(
        persisted_seed is not None,
        "Protected seed could not be reloaded.",
    )

    protection_metadata = persisted_seed.metadata.get(
        "seed_protection"
    )

    check(
        isinstance(protection_metadata, dict),
        "Structured protection metadata was not persisted.",
    )

    check(
        protection_metadata.get("evaluated") is True,
        "Persisted protection evidence is not marked evaluated.",
    )

    check(
        protection_metadata.get("decision")
        == SeedProtectionDecision.BLOCK_DUPLICATE.value,
        "Persisted protection decision is incorrect.",
    )

    check(
        persisted_seed.metadata.get(
            "protection_blocking"
        )
        is True,
        "Top-level protection blocking flag is incorrect.",
    )

    record(
        "protection evidence persists through certified repository",
        True,
    )

    # --------------------------------------------------------
    # 16. EXPLANATION CONTRACT
    # --------------------------------------------------------

    explanation = (
        explain_universal_web_seed_protection_v1()
    )

    check(
        explanation.get("ok") is True,
        "Protection explanation did not return ok=True.",
    )

    check(
        explanation.get("component")
        == "universal_web_seed_protection",
        "Protection explanation component is incorrect.",
    )

    check(
        explanation.get("schema_version")
        == UNIVERSAL_WEB_SEED_PROTECTION_SCHEMA_VERSION,
        "Protection explanation schema is incorrect.",
    )

    check(
        explanation.get("comparison_scope")
        == "workspace",
        "Protection comparison scope is incorrect.",
    )

    check(
        explanation.get("canonicalization_scope")
        == "comparison-only",
        "Protection canonicalization boundary is incorrect.",
    )

    check(
        explanation.get("fingerprint_algorithm")
        == "sha256",
        "Protection fingerprint algorithm is incorrect.",
    )

    check(
        set(
            explanation.get(
                "comparison_families",
                [],
            )
        )
        == {
            "web_page_target",
            "domain_target",
            "sitemap_target",
            "feed_target",
        },
        "Protection comparison families are incorrect.",
    )

    check(
        set(
            explanation.get(
                "decisions",
                [],
            )
        )
        == {
            "allow",
            "block_duplicate",
            "block_type_conflict",
            "review",
        },
        "Protection decisions are incorrect.",
    )

    check(
        "full crawl-pipeline URL normalization"
        in explanation.get(
            "excluded_responsibilities",
            [],
        ),
        "Full URL normalization boundary is missing.",
    )

    check(
        "seed eligibility validation"
        in explanation.get(
            "excluded_responsibilities",
            [],
        ),
        "Seed eligibility boundary is missing.",
    )

    check(
        explanation.get("next_pipeline_stage")
        == "Seed Eligibility Validation",
        "Protection explanation points to the wrong next stage.",
    )

    record(
        "Seed Protection explanation contract is correct",
        True,
    )

finally:
    cleanup_all_test_stores()


# ------------------------------------------------------------
# FINAL CLEANUP VERIFICATION
# ------------------------------------------------------------

remaining_stores = [
    str(
        universal_web_seed_store_path(
            workspace_id
        )
    )
    for workspace_id in WORKSPACES.values()
    if universal_web_seed_store_path(
        workspace_id
    ).exists()
]

check(
    not remaining_stores,
    "Some Seed Protection test stores remain after cleanup.",
)

record(
    "all Seed Protection test repositories removed",
    True,
)


# ------------------------------------------------------------
# FINAL RESULT
# ------------------------------------------------------------

failed = [
    result
    for result in results
    if result["passed"] is not True
]

print("")
print("============================================================")
print(" VERIFICATION SUMMARY")
print("============================================================")
print(f"Checks executed: {len(results)}")
print(f"Checks passed:   {len(results) - len(failed)}")
print(f"Checks failed:   {len(failed)}")

if failed:
    print("")
    print(
        "UNIVERSAL WEB SEED PROTECTION "
        "VERIFICATION: FAIL"
    )

    for failure in failed:
        print(
            " - "
            + str(failure.get("check"))
        )

    raise SystemExit(1)

print("")
print(
    "UNIVERSAL WEB SEED PROTECTION "
    "VERIFICATION: PASS"
)

print("")
print(
    json.dumps(
        explanation,
        indent=2,
        ensure_ascii=False,
    )
)
