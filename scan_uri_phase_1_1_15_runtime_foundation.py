from __future__ import annotations

import ast
import hashlib
import importlib
import json
import py_compile
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path.cwd().resolve()

RUNTIME_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
)

EVIDENCE_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "uri_phase_1"
    / "1_1_15_runtime_foundation_certification"
)

TIMESTAMP = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

REPORT_JSON = (
    EVIDENCE_DIR
    / f"runtime_foundation_scan_{TIMESTAMP}.json"
)

REPORT_TEXT = (
    EVIDENCE_DIR
    / f"runtime_foundation_scan_{TIMESTAMP}.txt"
)


EXPECTED_COMPONENTS = [
    {
        "item": "1.1.1",
        "name": "Universal Runtime Kernel",
        "files": [
            "universal_runtime_kernel.py",
        ],
    },
    {
        "item": "1.1.2",
        "name": "Runtime Configuration",
        "files": [
            "runtime_configuration.py",
        ],
    },
    {
        "item": "1.1.3",
        "name": "Runtime Environment Management",
        "files": [
            "runtime_environment.py",
        ],
    },
    {
        "item": "1.1.4",
        "name": "Runtime Service Registry",
        "files": [
            "runtime_service_registry.py",
        ],
    },
    {
        "item": "1.1.5",
        "name": "Runtime Lifecycle Manager",
        "files": [
            "runtime_lifecycle_manager.py",
        ],
    },
    {
        "item": "1.1.6",
        "name": "Runtime Boot Process",
        "files": [
            "runtime_boot_process.py",
        ],
    },
    {
        "item": "1.1.7",
        "name": "Runtime Shutdown Process",
        "files": [
            "runtime_shutdown_process.py",
        ],
    },
    {
        "item": "1.1.8",
        "name": "Runtime Versioning",
        "files": [
            "runtime_versioning.py",
        ],
    },
    {
        "item": "1.1.9",
        "name": "Runtime Compatibility Layer",
        "files": [
            "runtime_compatibility.py",
        ],
    },
    {
        "item": "1.1.10",
        "name": "Runtime Feature Flags",
        "files": [
            "runtime_feature_flags.py",
        ],
    },
    {
        "item": "1.1.11",
        "name": "Runtime Capability Negotiation",
        "files": [
            "runtime_capability_negotiation.py",
        ],
    },
    {
        "item": "1.1.12",
        "name": "Runtime Persistence Interface",
        "files": [
            "runtime_persistence.py",
        ],
    },
    {
        "item": "1.1.13",
        "name": "Runtime State Store Abstraction",
        "files": [
            "runtime_state_store.py",
        ],
    },
    {
        "item": "1.1.14",
        "name": "Runtime Schema Management",
        "files": [
            "runtime_schema/types.py",
            "runtime_schema/fingerprint.py",
            "runtime_schema/serialization.py",
            "runtime_schema/versioning.py",
            "runtime_schema/definitions.py",
            "runtime_schema/namespaces.py",
            "runtime_schema/ownership.py",
            "runtime_schema/validation.py",
            "runtime_schema/diff_engine.py",
            "runtime_schema/change_detection.py",
            "runtime_schema/compatibility.py",
            "runtime_schema/migration.py",
            "runtime_schema/transition_validation.py",
            "runtime_schema/deprecation.py",
            "runtime_schema/audit.py",
            "runtime_schema/snapshots.py",
            "runtime_schema/ports.py",
            "runtime_schema/registry.py",
            "runtime_schema/loader.py",
            "runtime_schema/certification.py",
        ],
    },
]


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def scan_file(
    relative_path: str,
) -> dict:
    path = RUNTIME_DIR / relative_path

    result = {
        "relative_path": relative_path,
        "absolute_path": str(path),
        "exists": path.exists(),
        "size": None,
        "sha256": None,
        "compile": "NOT_RUN",
        "ast_parse": "NOT_RUN",
        "import": "NOT_RUN",
        "error": None,
    }

    if not path.exists():
        result["error"] = "FILE_MISSING"
        return result

    result["size"] = path.stat().st_size
    result["sha256"] = sha256_file(path)

    try:
        py_compile.compile(
            str(path),
            doraise=True,
        )
        result["compile"] = "PASS"
    except Exception as exc:
        result["compile"] = "FAIL"
        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )
        return result

    try:
        source = path.read_text(
            encoding="utf-8-sig"
        )
        ast.parse(source)
        result["ast_parse"] = "PASS"
    except Exception as exc:
        result["ast_parse"] = "FAIL"
        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )
        return result

    module_name = relative_path.removesuffix(
        ".py"
    ).replace("/", ".")

    try:
        runtime_path = str(RUNTIME_DIR)

        if runtime_path not in sys.path:
            sys.path.insert(
                0,
                runtime_path,
            )

        importlib.invalidate_caches()
        importlib.import_module(module_name)

        result["import"] = "PASS"

    except Exception as exc:
        result["import"] = "FAIL"
        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

    return result


def main() -> int:
    print("=" * 78)
    print("UNIVERSAL RUNTIME INFRASTRUCTURE")
    print("1.1.15 — RUNTIME FOUNDATION CERTIFICATION PRE-BUILD SCAN")
    print("=" * 78)
    print(f"Runtime directory: {RUNTIME_DIR}")
    print()

    component_results = []

    for component in EXPECTED_COMPONENTS:
        files = [
            scan_file(relative_path)
            for relative_path
            in component["files"]
        ]

        exists = all(
            item["exists"]
            for item in files
        )

        compiles = all(
            item["compile"] == "PASS"
            for item in files
        )

        imports = all(
            item["import"] == "PASS"
            for item in files
        )

        status = (
            "PASS"
            if exists and compiles and imports
            else "FAIL"
        )

        component_results.append(
            {
                "item": component["item"],
                "name": component["name"],
                "status": status,
                "files": files,
            }
        )

    missing_files = [
        file_result["relative_path"]
        for component
        in component_results
        for file_result
        in component["files"]
        if not file_result["exists"]
    ]

    compile_failures = [
        file_result["relative_path"]
        for component
        in component_results
        for file_result
        in component["files"]
        if file_result["compile"] == "FAIL"
    ]

    import_failures = [
        {
            "file": file_result["relative_path"],
            "error": file_result["error"],
        }
        for component
        in component_results
        for file_result
        in component["files"]
        if file_result["import"] == "FAIL"
    ]

    overall_status = (
        "PASS"
        if not missing_files
        and not compile_failures
        and not import_failures
        else "FAIL"
    )

    report = {
        "scan": (
            "URI 1.1.15 Runtime Foundation "
            "Certification Pre-Build Scan"
        ),
        "generated_at": TIMESTAMP,
        "runtime_directory": str(RUNTIME_DIR),
        "overall_status": overall_status,
        "component_count": len(
            component_results
        ),
        "missing_files": missing_files,
        "compile_failures": compile_failures,
        "import_failures": import_failures,
        "components": component_results,
        "application_boot_integration": "PENDING",
        "certification_built": False,
    }

    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_JSON.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    lines = [
        "=" * 78,
        "URI 1.1.15 RUNTIME FOUNDATION CERTIFICATION PRE-BUILD SCAN",
        "=" * 78,
        "",
    ]

    for component in component_results:
        lines.append(
            f"{component['status']:4} "
            f"{component['item']} "
            f"{component['name']}"
        )

        for file_result in component[
            "files"
        ]:
            lines.append(
                "     "
                f"{file_result['relative_path']} | "
                f"exists={file_result['exists']} | "
                f"compile={file_result['compile']} | "
                f"import={file_result['import']}"
            )

            if file_result["error"]:
                lines.append(
                    "       ERROR: "
                    + file_result["error"]
                )

    lines.extend(
        [
            "",
            f"Missing files:     {len(missing_files)}",
            f"Compile failures:  {len(compile_failures)}",
            f"Import failures:   {len(import_failures)}",
            "",
            f"OVERALL STATUS: {overall_status}",
            "CERTIFICATION BUILT: NO",
            "APPLICATION BOOT INTEGRATION: PENDING",
        ]
    )

    REPORT_TEXT.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    for component in component_results:
        marker = (
            "PASS"
            if component["status"] == "PASS"
            else "FAIL"
        )

        print(
            f"{marker:4} "
            f"{component['item']} "
            f"{component['name']}"
        )

    print()
    print(f"Missing files:    {len(missing_files)}")
    print(f"Compile failures: {len(compile_failures)}")
    print(f"Import failures:  {len(import_failures)}")
    print()
    print(f"Evidence JSON: {REPORT_JSON}")
    print(f"Evidence text: {REPORT_TEXT}")
    print()
    print(
        "RUNTIME FOUNDATION PRE-BUILD SCAN: "
        + overall_status
    )
    print(
        "NO PRODUCTION DATA WAS MODIFIED"
    )

    return (
        0
        if overall_status == "PASS"
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
