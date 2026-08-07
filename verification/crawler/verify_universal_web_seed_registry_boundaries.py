from __future__ import annotations

import ast
import json
import py_compile
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.server.crawler import (
    explain_universal_web_seed_controls_v1,
    explain_universal_web_seed_models_v1,
    explain_universal_web_seed_protection_v1,
    explain_universal_web_seed_registration_engine_v1,
    explain_universal_web_seed_repository_v1,
)


ROOT = PROJECT_ROOT

CRAWLER_DIR = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
)

REGISTRY_COMPONENTS = {
    "seed_models": (
        CRAWLER_DIR
        / "seed_models.py"
    ),
    "seed_repository": (
        CRAWLER_DIR
        / "seed_repository.py"
    ),
    "seed_registration_engine": (
        CRAWLER_DIR
        / "seed_registration_engine.py"
    ),
    "seed_controls": (
        CRAWLER_DIR
        / "seed_controls.py"
    ),
    "seed_protection": (
        CRAWLER_DIR
        / "seed_protection.py"
    ),
}


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


def read_source(
    path: Path,
) -> str:
    return path.read_text(
        encoding="utf-8-sig"
    )


def parse_tree(
    path: Path,
) -> ast.Module:
    return ast.parse(
        read_source(path),
        filename=str(path),
    )


def imported_modules(
    path: Path,
) -> set[str]:
    modules: set[str] = set()

    for node in ast.walk(
        parse_tree(path)
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                modules.add(
                    alias.name
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            if node.module:
                modules.add(
                    node.module
                )

    return modules


def called_function_names(
    path: Path,
) -> set[str]:
    names: set[str] = set()

    for node in ast.walk(
        parse_tree(path)
    ):
        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        function = node.func

        if isinstance(
            function,
            ast.Name,
        ):
            names.add(
                function.id
            )

        elif isinstance(
            function,
            ast.Attribute,
        ):
            names.add(
                function.attr
            )

    return names


def assigned_string_values(
    path: Path,
) -> set[str]:
    values: set[str] = set()

    for node in ast.walk(
        parse_tree(path)
    ):
        if isinstance(
            node,
            ast.Constant,
        ) and isinstance(
            node.value,
            str,
        ):
            values.add(
                node.value
            )

    return values


print("")
print("============================================================")
print(" PHASE 1.6.3 - UNIVERSAL WEB SEED REGISTRY")
print(" BOUNDARY VERIFICATION")
print("============================================================")
print("")


# ------------------------------------------------------------
# 1. FILE EXISTENCE AND COMPILATION
# ------------------------------------------------------------

for component, path in REGISTRY_COMPONENTS.items():
    check(
        path.is_file(),
        f"Missing registry component: {path}",
    )

    py_compile.compile(
        str(path),
        doraise=True,
    )

    record(
        f"{component} exists and compiles",
        str(path),
    )


# ------------------------------------------------------------
# 2. EXPLANATION CONTRACT BOUNDARIES
# ------------------------------------------------------------

explanations = {
    "seed_models": (
        explain_universal_web_seed_models_v1()
    ),
    "seed_repository": (
        explain_universal_web_seed_repository_v1()
    ),
    "seed_registration_engine": (
        explain_universal_web_seed_registration_engine_v1()
    ),
    "seed_controls": (
        explain_universal_web_seed_controls_v1()
    ),
    "seed_protection": (
        explain_universal_web_seed_protection_v1()
    ),
}

required_exclusions = {
    "seed_models": {
        "seed persistence",
        "domain normalization",
    },
    "seed_repository": {
        "duplicate seed-target detection",
        "seed eligibility validation",
        "URL normalization",
        "Crawl Frontier insertion",
        "crawl scheduling",
        "worker execution",
        "web page fetching",
    },
    "seed_registration_engine": {
        "duplicate seed-target detection",
        "seed eligibility validation",
        "Crawl Frontier insertion",
        "crawl scheduling",
        "worker execution",
        "web page fetching",
    },
    "seed_controls": {
        "duplicate seed-target detection",
        "seed eligibility validation",
        "URL normalization",
        "Crawl Frontier insertion",
        "crawl scheduling",
        "worker execution",
        "web page fetching",
    },
    "seed_protection": {
        "full crawl-pipeline URL normalization",
        "URL reachability validation",
        "DNS resolution",
        "private-network safety validation",
        "robots.txt evaluation",
        "HTTP fetching",
        "redirect resolution",
        "canonical-tag inspection",
        "seed eligibility validation",
        "Crawl Frontier insertion",
        "crawl scheduling",
        "worker execution",
        "web page fetching",
    },
}

for component, exclusions in required_exclusions.items():
    actual = set(
        explanations[
            component
        ].get(
            "excluded_responsibilities",
            [],
        )
    )

    missing = (
        exclusions
        - actual
    )

    check(
        not missing,
        (
            f"{component} is missing boundary exclusions: "
            + ", ".join(
                sorted(missing)
            )
        ),
    )

    record(
        f"{component} explanation preserves downstream boundaries",
    )


# ------------------------------------------------------------
# 3. NO NETWORK CLIENT IMPORTS
# ------------------------------------------------------------

forbidden_network_modules = {
    "requests",
    "httpx",
    "aiohttp",
    "urllib.request",
    "selenium",
    "playwright",
    "pyppeteer",
    "socket",
}

for component, path in REGISTRY_COMPONENTS.items():
    modules = imported_modules(
        path
    )

    violations = {
        module
        for module in modules
        if (
            module in forbidden_network_modules
            or any(
                module.startswith(
                    forbidden + "."
                )
                for forbidden
                in forbidden_network_modules
            )
        )
    }

    check(
        not violations,
        (
            f"{component} imports forbidden network "
            "modules: "
            + ", ".join(
                sorted(violations)
            )
        ),
    )

    record(
        f"{component} contains no network-fetching imports",
    )


# ------------------------------------------------------------
# 4. NO FETCH OR RENDER EXECUTION
# ------------------------------------------------------------

forbidden_fetch_calls = {
    "urlopen",
    "fetch",
    "fetch_url",
    "fetch_page",
    "fetch_html",
    "download",
    "render",
    "render_page",
    "goto",
    "navigate",
    "crawl",
    "crawl_url",
}

for component, path in REGISTRY_COMPONENTS.items():
    calls = called_function_names(
        path
    )

    violations = (
        calls
        & forbidden_fetch_calls
    )

    check(
        not violations,
        (
            f"{component} contains forbidden fetch or "
            "render calls: "
            + ", ".join(
                sorted(violations)
            )
        ),
    )

    record(
        f"{component} does not fetch, crawl or render pages",
    )


# ------------------------------------------------------------
# 5. NO FRONTIER OWNERSHIP
# ------------------------------------------------------------

forbidden_frontier_calls = {
    "insert_into_crawl_frontier",
    "enqueue_crawl_url",
    "add_frontier_url",
    "push_frontier_item",
    "create_frontier_entry",
    "schedule_frontier_url",
    "claim_frontier_url",
    "release_frontier_url",
}

for component, path in REGISTRY_COMPONENTS.items():
    calls = called_function_names(
        path
    )

    violations = (
        calls
        & forbidden_frontier_calls
    )

    check(
        not violations,
        (
            f"{component} contains Crawl Frontier "
            "operations: "
            + ", ".join(
                sorted(violations)
            )
        ),
    )

    record(
        f"{component} does not own Crawl Frontier operations",
    )


# ------------------------------------------------------------
# 6. NO SCHEDULER OR WORKER OWNERSHIP
# ------------------------------------------------------------

forbidden_runtime_calls = {
    "create_universal_knowledge_job",
    "enqueue_job",
    "enqueue_crawl_job",
    "schedule_crawl",
    "schedule_seed",
    "dispatch_job",
    "dispatch_worker",
    "start_worker",
    "run_worker",
    "run_queue",
    "run_universal_knowledge_queue_v1",
    "execute_universal_knowledge_job_v1",
}

for component, path in REGISTRY_COMPONENTS.items():
    calls = called_function_names(
        path
    )

    violations = (
        calls
        & forbidden_runtime_calls
    )

    check(
        not violations,
        (
            f"{component} contains scheduler, queue or "
            "worker operations: "
            + ", ".join(
                sorted(violations)
            )
        ),
    )

    record(
        f"{component} does not schedule or execute crawler work",
    )


# ------------------------------------------------------------
# 7. NO SEED ELIGIBILITY DECISION OWNERSHIP
# ------------------------------------------------------------

forbidden_eligibility_functions = {
    "validate_seed_eligibility",
    "evaluate_seed_eligibility",
    "determine_seed_eligibility",
    "is_seed_eligible",
    "approve_seed_for_crawl",
    "reject_seed_for_crawl",
}

for component, path in REGISTRY_COMPONENTS.items():
    calls = called_function_names(
        path
    )

    violations = (
        calls
        & forbidden_eligibility_functions
    )

    check(
        not violations,
        (
            f"{component} contains Seed Eligibility "
            "Validation operations: "
            + ", ".join(
                sorted(violations)
            )
        ),
    )

    record(
        f"{component} does not decide downstream seed eligibility",
    )


# ------------------------------------------------------------
# 8. NO ROBOTS, DNS OR PRIVATE-NETWORK OWNERSHIP
# ------------------------------------------------------------

forbidden_safety_calls = {
    "read_robots_txt",
    "fetch_robots_txt",
    "evaluate_robots",
    "is_allowed_by_robots",
    "resolve_dns",
    "getaddrinfo",
    "is_private_ip",
    "is_public_ip",
    "validate_public_network_target",
    "check_private_network",
}

for component, path in REGISTRY_COMPONENTS.items():
    calls = called_function_names(
        path
    )

    violations = (
        calls
        & forbidden_safety_calls
    )

    check(
        not violations,
        (
            f"{component} contains robots, DNS or "
            "network-safety operations: "
            + ", ".join(
                sorted(violations)
            )
        ),
    )

    record(
        f"{component} does not own robots, DNS or network safety",
    )


# ------------------------------------------------------------
# 9. NO DISCOVERED-URL PIPELINE OWNERSHIP
# ------------------------------------------------------------

forbidden_url_pipeline_calls = {
    "discover_links",
    "extract_links",
    "normalize_discovered_url",
    "normalize_crawl_url",
    "deduplicate_url",
    "deduplicate_crawl_urls",
    "classify_page_type",
    "inspect_page",
    "detect_page_change",
    "create_page_version",
    "update_page_lifecycle",
}

for component, path in REGISTRY_COMPONENTS.items():
    calls = called_function_names(
        path
    )

    violations = (
        calls
        & forbidden_url_pipeline_calls
    )

    check(
        not violations,
        (
            f"{component} contains discovered-URL or "
            "page-lifecycle operations: "
            + ", ".join(
                sorted(violations)
            )
        ),
    )

    record(
        f"{component} does not own discovered-URL or page lifecycle stages",
    )


# ------------------------------------------------------------
# 10. NO RAW HTML OR LEFT-ARM HANDOFF
# ------------------------------------------------------------

forbidden_handoff_calls = {
    "run_enterprise_raw_html_acquisition",
    "acquire_raw_html",
    "save_raw_html",
    "write_raw_html",
    "store_raw_html",
    "handoff_to_raw_html_engine",
    "run_knowledge_acquisition_coordinator",
    "handoff_to_left_arm",
}

for component, path in REGISTRY_COMPONENTS.items():
    calls = called_function_names(
        path
    )

    violations = (
        calls
        & forbidden_handoff_calls
    )

    check(
        not violations,
        (
            f"{component} contains Raw HTML or left-arm "
            "handoff operations: "
            + ", ".join(
                sorted(violations)
            )
        ),
    )

    record(
        f"{component} does not write Raw HTML or call the left arm",
    )


# ------------------------------------------------------------
# 11. FILESYSTEM WRITE BOUNDARIES
# ------------------------------------------------------------

allowed_write_component = (
    "seed_repository"
)

write_call_names = {
    "write_text",
    "write_bytes",
    "dump",
    "replace",
    "unlink",
    "NamedTemporaryFile",
}

for component, path in REGISTRY_COMPONENTS.items():
    calls = called_function_names(
        path
    )

    write_calls = (
        calls
        & write_call_names
    )

    if component == allowed_write_component:
        check(
            bool(write_calls),
            (
                "Seed Repository is expected to own "
                "registry persistence but no write calls "
                "were found."
            ),
        )

        record(
            "Seed Repository exclusively owns registry-file persistence",
            ", ".join(
                sorted(write_calls)
            ),
        )

        continue

    check(
        not write_calls,
        (
            f"{component} contains direct filesystem "
            "write operations: "
            + ", ".join(
                sorted(write_calls)
            )
        ),
    )

    record(
        f"{component} performs no direct registry-file writes",
    )


# ------------------------------------------------------------
# 12. PROTECTION CANONICALIZATION REMAINS COMPARISON-ONLY
# ------------------------------------------------------------

protection_source = read_source(
    REGISTRY_COMPONENTS[
        "seed_protection"
    ]
)

check(
    '"comparison-only"'
    in protection_source,
    (
        "Seed Protection does not declare its "
        "comparison-only canonicalization boundary."
    ),
)

check(
    "existing_seed.original_value ="
    not in protection_source,
    (
        "Seed Protection appears to mutate an existing "
        "seed original_value."
    ),
)

check(
    "seed.original_value ="
    not in protection_source,
    (
        "Seed Protection appears to mutate the candidate "
        "seed original_value."
    ),
)

check(
    "seed.normalized_value ="
    not in protection_source,
    (
        "Seed Protection appears to mutate the candidate "
        "seed normalized_value."
    ),
)

record(
    "Seed Protection canonicalization remains non-destructive and comparison-only",
)


# ------------------------------------------------------------
# 13. PROTECTION DOES NOT DELETE OR MERGE
# ------------------------------------------------------------

protection_calls = called_function_names(
    REGISTRY_COMPONENTS[
        "seed_protection"
    ]
)

forbidden_mutation_calls = {
    "delete_universal_web_seed",
    "merge_universal_web_seeds",
    "archive_seed",
    "disable_seed",
    "enable_seed",
    "restore_seed",
}

violations = (
    protection_calls
    & forbidden_mutation_calls
)

check(
    not violations,
    (
        "Seed Protection contains forbidden lifecycle, "
        "merge or delete operations: "
        + ", ".join(
            sorted(violations)
        )
    ),
)

record(
    "Seed Protection reports conflicts without deleting, merging or changing lifecycle",
)


# ------------------------------------------------------------
# 14. REGISTRATION DOES NOT EXECUTE PROTECTION
# ------------------------------------------------------------

registration_source = read_source(
    REGISTRY_COMPONENTS[
        "seed_registration_engine"
    ]
)

check(
    "protect_universal_web_seed("
    not in registration_source,
    (
        "Seed Registration currently executes Seed "
        "Protection internally before final registry "
        "certification."
    ),
)

check(
    "inspect_seed_protection("
    not in registration_source,
    (
        "Seed Registration currently executes Seed "
        "Protection inspection internally."
    ),
)

record(
    "Seed Registration and Seed Protection remain separately callable components",
)


# ------------------------------------------------------------
# 15. CONTROLS DO NOT EXECUTE PROTECTION OR ELIGIBILITY
# ------------------------------------------------------------

controls_source = read_source(
    REGISTRY_COMPONENTS[
        "seed_controls"
    ]
)

for forbidden_marker in (
    "protect_universal_web_seed(",
    "inspect_seed_protection(",
    "validate_seed_eligibility(",
    "insert_into_crawl_frontier(",
):
    check(
        forbidden_marker
        not in controls_source,
        (
            "Seed Controls contains downstream operation: "
            f"{forbidden_marker}"
        ),
    )

record(
    "Seed Controls remains limited to lifecycle and editable control fields",
)


# ------------------------------------------------------------
# 16. PIPELINE NEXT-STAGE CONTRACT
# ------------------------------------------------------------

for component in (
    "seed_registration_engine",
    "seed_controls",
    "seed_protection",
):
    check(
        explanations[
            component
        ].get(
            "next_pipeline_stage"
        )
        == "Seed Eligibility Validation",
        (
            f"{component} points to an incorrect "
            "downstream pipeline stage."
        ),
    )

record(
    "registry terminates at Seed Eligibility Validation handoff",
)


# ------------------------------------------------------------
# 17. NO DOWNSTREAM DATA-STORE REFERENCES
# ------------------------------------------------------------

forbidden_store_markers = {
    "crawl_frontier",
    "raw_html_store",
    "raw_website_html",
    "page_version_store",
    "page_lifecycle_store",
    "raw_html_acquisition",
    "enterprise_raw_html",
    "universal_article_body_store",
    "udare_store",
}

for component, path in REGISTRY_COMPONENTS.items():
    source = read_source(
        path
    ).lower()

    violations = {
        marker
        for marker
        in forbidden_store_markers
        if marker in source
    }

    check(
        not violations,
        (
            f"{component} references downstream stores "
            "or engines: "
            + ", ".join(
                sorted(violations)
            )
        ),
    )

    record(
        f"{component} contains no downstream store or engine coupling",
    )


# ------------------------------------------------------------
# FINAL REPORT
# ------------------------------------------------------------

failed = [
    result
    for result in results
    if result.get(
        "passed"
    )
    is not True
]

report = {
    "ok": not failed,
    "component": (
        "universal_web_seed_registry_boundary_verification"
    ),
    "schema_version": (
        "universal_web_seed_registry_boundary_verification.v1"
    ),
    "pipeline_stage": (
        "Universal Web Seed Registry"
    ),
    "verified_boundary": {
        "starts_at": (
            "Universal Web Seed Registry"
        ),
        "ends_before": (
            "Seed Eligibility Validation"
        ),
        "next_pipeline_stage": (
            "Seed Eligibility Validation"
        ),
    },
    "registry_owns": [
        "seed record contracts",
        "workspace-scoped seed persistence",
        "seed registration",
        "seed lifecycle controls",
        "seed priority and metadata controls",
        "comparison-only duplicate protection",
        "protection evidence persistence",
    ],
    "registry_does_not_own": [
        "seed eligibility decisions",
        "robots.txt evaluation",
        "DNS resolution",
        "private-network safety",
        "Crawl Frontier insertion",
        "crawl scheduling",
        "crawler worker execution",
        "HTTP or rendered-page fetching",
        "link discovery",
        "discovered-URL normalization",
        "discovered-URL deduplication",
        "page inspection",
        "page-type classification",
        "page version and lifecycle",
        "Raw HTML acquisition",
        "left-arm handoff",
    ],
    "checks_executed": len(
        results
    ),
    "checks_passed": (
        len(results)
        - len(failed)
    ),
    "checks_failed": len(
        failed
    ),
    "boundary_status": (
        "ready_for_certification_report"
        if not failed
        else "boundary_verification_failed"
    ),
    "next_step": (
        "Phase 1.6.4 Certification Report"
    ),
}

print("")
print("============================================================")
print(" BOUNDARY VERIFICATION SUMMARY")
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
        "BOUNDARY VERIFICATION: FAIL"
    )

    raise SystemExit(1)

print("")
print(
    "UNIVERSAL WEB SEED REGISTRY "
    "BOUNDARY VERIFICATION: PASS"
)

print("")
print(
    json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
    )
)
