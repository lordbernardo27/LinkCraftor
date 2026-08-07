from __future__ import annotations

import ast
import json
import py_compile
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import backend.server.crawler as crawler

from backend.server.crawler import (
    CRAWLER_SESSION_SCHEMA_VERSION,
    UNIVERSAL_WEB_SEED_CONTROLS_SCHEMA_VERSION,
    UNIVERSAL_WEB_SEED_PROTECTION_SCHEMA_VERSION,
    UNIVERSAL_WEB_SEED_REGISTRATION_SCHEMA_VERSION,
    UNIVERSAL_WEB_SEED_REPOSITORY_SCHEMA_VERSION,
    UNIVERSAL_WEB_SEED_SCHEMA_VERSION,
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

INIT_PATH = (
    CRAWLER_DIR
    / "__init__.py"
)

COMPONENT_PATHS = {
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

VERIFICATION_PATHS = {
    "seed_models": (
        ROOT
        / "verification"
        / "crawler"
        / "verify_universal_web_seed_models.py"
    ),
    "seed_repository": (
        ROOT
        / "verification"
        / "crawler"
        / "verify_universal_web_seed_repository.py"
    ),
    "seed_registration_engine": (
        ROOT
        / "verification"
        / "crawler"
        / "verify_universal_web_seed_registration_engine.py"
    ),
    "seed_controls": (
        ROOT
        / "verification"
        / "crawler"
        / "verify_seed_controls.py"
    ),
    "seed_protection": (
        ROOT
        / "verification"
        / "crawler"
        / "verify_seed_protection.py"
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


def read_python_source(
    path: Path,
) -> str:
    return path.read_text(
        encoding="utf-8-sig"
    )


def top_level_function_names(
    path: Path,
) -> set[str]:
    source = read_python_source(
        path
    )

    tree = ast.parse(
        source
    )

    return {
        node.name
        for node in tree.body
        if isinstance(
            node,
            ast.FunctionDef,
        )
    }


print("")
print("============================================================")
print(" PHASE 1.6.1 - UNIVERSAL WEB SEED REGISTRY")
print(" FULL ARCHITECTURE REVIEW")
print("============================================================")
print("")


# ------------------------------------------------------------
# 1. COMPONENT FILES
# ------------------------------------------------------------

for component, path in COMPONENT_PATHS.items():
    check(
        path.is_file(),
        f"Missing registry component: {path}",
    )

    record(
        f"{component}.py exists",
        str(path),
    )


check(
    INIT_PATH.is_file(),
    "Crawler package __init__.py is missing.",
)

record(
    "crawler package __init__.py exists",
    str(INIT_PATH),
)


# ------------------------------------------------------------
# 2. COMPILATION
# ------------------------------------------------------------

for component, path in COMPONENT_PATHS.items():
    py_compile.compile(
        str(path),
        doraise=True,
    )

    record(
        f"{component}.py compiles",
    )

py_compile.compile(
    str(INIT_PATH),
    doraise=True,
)

record(
    "crawler package __init__.py compiles",
)


# ------------------------------------------------------------
# 3. SCHEMA CONTRACTS
# ------------------------------------------------------------

expected_schemas = {
    "seed_model": (
        UNIVERSAL_WEB_SEED_SCHEMA_VERSION,
        "universal_web_seed.v1",
    ),
    "seed_repository": (
        UNIVERSAL_WEB_SEED_REPOSITORY_SCHEMA_VERSION,
        "universal_web_seed_repository.v1",
    ),
    "seed_registration": (
        UNIVERSAL_WEB_SEED_REGISTRATION_SCHEMA_VERSION,
        "universal_web_seed_registration.v1",
    ),
    "seed_controls": (
        UNIVERSAL_WEB_SEED_CONTROLS_SCHEMA_VERSION,
        "universal_web_seed_controls.v1",
    ),
    "seed_protection": (
        UNIVERSAL_WEB_SEED_PROTECTION_SCHEMA_VERSION,
        "universal_web_seed_protection.v1",
    ),
}

for component, (
    actual,
    expected,
) in expected_schemas.items():
    check(
        actual == expected,
        (
            f"{component} schema mismatch: "
            f"{actual!r} != {expected!r}"
        ),
    )

record(
    "all Universal Web Seed Registry schema versions are correct",
)


# ------------------------------------------------------------
# 4. CANONICAL FUNCTION INVENTORY
# ------------------------------------------------------------

required_functions = {
    "seed_models": {
        "explain_universal_web_seed_models_v1",
    },
    "seed_repository": {
        "create_universal_web_seed",
        "update_universal_web_seed",
        "get_universal_web_seed",
        "require_universal_web_seed",
        "list_universal_web_seeds",
        "delete_universal_web_seed",
        "explain_universal_web_seed_repository_v1",
    },
    "seed_registration_engine": {
        "register_universal_web_seed",
        "build_universal_web_seed_registration_record",
        "build_universal_web_seed_registration_result",
        "explain_universal_web_seed_registration_engine_v1",
    },
    "seed_controls": {
        "validate_seed_transition",
        "enable_seed",
        "disable_seed",
        "archive_seed",
        "restore_seed",
        "update_priority",
        "update_metadata",
        "explain_universal_web_seed_controls_v1",
    },
    "seed_protection": {
        "build_seed_comparison_target",
        "generate_seed_target_fingerprint",
        "inspect_seed_protection",
        "protect_universal_web_seed",
        "explain_universal_web_seed_protection_v1",
    },
}

for component, expected_functions in required_functions.items():
    actual_functions = top_level_function_names(
        COMPONENT_PATHS[
            component
        ]
    )

    missing = (
        expected_functions
        - actual_functions
    )

    check(
        not missing,
        (
            f"{component} is missing canonical functions: "
            + ", ".join(
                sorted(missing)
            )
        ),
    )

    record(
        f"{component} canonical function inventory is complete",
        ", ".join(
            sorted(expected_functions)
        ),
    )


# ------------------------------------------------------------
# 5. PACKAGE EXPORTS
# ------------------------------------------------------------

required_exports = {
    "UniversalWebSeed",
    "UniversalWebSeedType",
    "UniversalWebSeedStatus",
    "create_universal_web_seed",
    "update_universal_web_seed",
    "get_universal_web_seed",
    "require_universal_web_seed",
    "list_universal_web_seeds",
    "register_universal_web_seed",
    "validate_seed_transition",
    "enable_seed",
    "disable_seed",
    "archive_seed",
    "restore_seed",
    "update_priority",
    "update_metadata",
    "build_seed_comparison_target",
    "generate_seed_target_fingerprint",
    "inspect_seed_protection",
    "protect_universal_web_seed",
}

missing_exports = {
    export_name
    for export_name in required_exports
    if not hasattr(
        crawler,
        export_name,
    )
}

check(
    not missing_exports,
    (
        "Crawler package is missing exports: "
        + ", ".join(
            sorted(missing_exports)
        )
    ),
)

record(
    "crawler package exports the full registry public surface",
)


# ------------------------------------------------------------
# 6. EXPLANATION CONTRACTS
# ------------------------------------------------------------

explanations = {
    "models": (
        explain_universal_web_seed_models_v1()
    ),
    "repository": (
        explain_universal_web_seed_repository_v1()
    ),
    "registration": (
        explain_universal_web_seed_registration_engine_v1()
    ),
    "controls": (
        explain_universal_web_seed_controls_v1()
    ),
    "protection": (
        explain_universal_web_seed_protection_v1()
    ),
}

for component, explanation in explanations.items():
    check(
        explanation.get("ok") is True,
        f"{component} explanation did not return ok=True.",
    )

    check(
        explanation.get("pipeline_stage")
        == "Universal Web Seed Registry",
        (
            f"{component} reports the wrong "
            "pipeline stage."
        ),
    )

    record(
        f"{component} explanation contract is valid",
    )


# ------------------------------------------------------------
# 7. COMPONENT ORDER AND NEXT-STAGE CONTRACTS
# ------------------------------------------------------------

check(
    explanations[
        "repository"
    ].get(
        "next_component"
    )
    == "Seed Registration Engine",
    "Repository points to the wrong next component.",
)

check(
    explanations[
        "registration"
    ].get(
        "next_component"
    )
    == "Seed Controls",
    "Registration points to the wrong next component.",
)

check(
    explanations[
        "controls"
    ].get(
        "next_component"
    )
    == "Seed Protection",
    "Seed Controls points to the wrong next component.",
)

check(
    explanations[
        "protection"
    ].get(
        "next_component"
    )
    == "Universal Web Seed Registry Certification",
    "Seed Protection points to the wrong next component.",
)

for component in (
    "registration",
    "controls",
    "protection",
):
    check(
        explanations[
            component
        ].get(
            "next_pipeline_stage"
        )
        == "Seed Eligibility Validation",
        (
            f"{component} points to the wrong "
            "next pipeline stage."
        ),
    )

record(
    "registry component order and next-stage contracts are correct",
)


# ------------------------------------------------------------
# 8. RESPONSIBILITY BOUNDARIES
# ------------------------------------------------------------

boundary_expectations = {
    "models": {
        "domain normalization",
        "seed persistence",
    },
    "repository": {
        "duplicate seed-target detection",
        "seed eligibility validation",
        "URL normalization",
    },
    "registration": {
        "duplicate seed-target detection",
        "seed eligibility validation",
        "Crawl Frontier insertion",
    },
    "controls": {
        "duplicate seed-target detection",
        "seed eligibility validation",
        "Crawl Frontier insertion",
    },
    "protection": {
        "full crawl-pipeline URL normalization",
        "seed eligibility validation",
        "Crawl Frontier insertion",
        "web page fetching",
    },
}

for component, required_exclusions in boundary_expectations.items():
    exclusions = set(
        explanations[
            component
        ].get(
            "excluded_responsibilities",
            [],
        )
    )

    missing_exclusions = (
        required_exclusions
        - exclusions
    )

    check(
        not missing_exclusions,
        (
            f"{component} is missing boundary exclusions: "
            + ", ".join(
                sorted(missing_exclusions)
            )
        ),
    )

    record(
        f"{component} responsibility boundaries are preserved",
    )


# ------------------------------------------------------------
# 9. VERIFICATION SUITES
# ------------------------------------------------------------

for component, path in VERIFICATION_PATHS.items():
    check(
        path.is_file(),
        (
            f"Missing verification suite for "
            f"{component}: {path}"
        ),
    )

    py_compile.compile(
        str(path),
        doraise=True,
    )

    record(
        f"{component} verification suite exists and compiles",
        str(path),
    )


# ------------------------------------------------------------
# 10. WINDOWS-SAFE ATOMIC PERSISTENCE HARDENING
# ------------------------------------------------------------

repository_source = read_python_source(
    COMPONENT_PATHS[
        "seed_repository"
    ]
)

required_repository_hardening = (
    "replace_attempts = 5",
    "except PermissionError:",
    "time.sleep(",
    "os.replace(",
    "os.fsync(",
)

for marker in required_repository_hardening:
    check(
        marker in repository_source,
        (
            "Repository atomic-save hardening "
            f"marker is missing: {marker}"
        ),
    )

record(
    "Windows-safe atomic repository persistence is present",
)


# ------------------------------------------------------------
# 11. STATIC BOUNDARY REVIEW
# ------------------------------------------------------------

registration_source = read_python_source(
    COMPONENT_PATHS[
        "seed_registration_engine"
    ]
)

controls_source = read_python_source(
    COMPONENT_PATHS[
        "seed_controls"
    ]
)

protection_source = read_python_source(
    COMPONENT_PATHS[
        "seed_protection"
    ]
)

check(
    "protect_universal_web_seed(" not in registration_source,
    (
        "Registration Engine unexpectedly owns "
        "Seed Protection execution."
    ),
)

check(
    "register_universal_web_seed(" not in protection_source,
    (
        "Seed Protection unexpectedly owns "
        "seed registration."
    ),
)

check(
    "requests." not in protection_source
    and "httpx." not in protection_source,
    (
        "Seed Protection unexpectedly contains "
        "network-fetching logic."
    ),
)

check(
    "requests." not in controls_source
    and "httpx." not in controls_source,
    (
        "Seed Controls unexpectedly contains "
        "network-fetching logic."
    ),
)

record(
    "static registry component boundaries are clean",
)


# ------------------------------------------------------------
# FINAL RESULT
# ------------------------------------------------------------

failed = [
    result
    for result in results
    if result.get("passed") is not True
]

report = {
    "ok": not failed,
    "component": (
        "universal_web_seed_registry_full_review"
    ),
    "schema_version": (
        "universal_web_seed_registry_review.v1"
    ),
    "pipeline_stage": (
        "Universal Web Seed Registry"
    ),
    "components_reviewed": list(
        COMPONENT_PATHS.keys()
    ),
    "component_count": len(
        COMPONENT_PATHS
    ),
    "verification_suites_reviewed": list(
        VERIFICATION_PATHS.keys()
    ),
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
    "review_status": (
        "ready_for_integrated_workflow_verification"
        if not failed
        else "review_failed"
    ),
    "next_step": (
        "Phase 1.6.2 Integrated Workflow Verification"
    ),
}

print("")
print("============================================================")
print(" FULL REGISTRY REVIEW SUMMARY")
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
        "FULL REVIEW: FAIL"
    )

    raise SystemExit(1)

print("")
print(
    "UNIVERSAL WEB SEED REGISTRY "
    "FULL REVIEW: PASS"
)

print("")
print(
    json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
    )
)
