from __future__ import annotations

import ast
import dataclasses
import hashlib
import importlib
import inspect
import json
import py_compile
import sys
import traceback
from pathlib import Path
from typing import Any


ROOT = Path(sys.argv[1]).resolve()
REPORT = Path(sys.argv[2]).resolve()

STAGES = {
    "connect_domain": {
        "module": "backend.server.pipelines.connect_domain.stage",
        "path": ROOT / "backend/server/pipelines/connect_domain/stage.py",
    },
    "site_sources": {
        "module": (
            "backend.server.pipelines.connect_domain."
            "linking_target_pipeline.site_sources.stage"
        ),
        "path": ROOT / (
            "backend/server/pipelines/connect_domain/"
            "linking_target_pipeline/site_sources/stage.py"
        ),
    },
    "url_cleaner": {
        "module": (
            "backend.server.pipelines.connect_domain."
            "linking_target_pipeline.url_cleaner.stage"
        ),
        "path": ROOT / (
            "backend/server/pipelines/connect_domain/"
            "linking_target_pipeline/url_cleaner/stage.py"
        ),
    },
    "site_pages": {
        "module": (
            "backend.server.pipelines.connect_domain."
            "linking_target_pipeline.site_pages.stage"
        ),
        "path": ROOT / (
            "backend/server/pipelines/connect_domain/"
            "linking_target_pipeline/site_pages/stage.py"
        ),
    },
    "live_domain_target_pool": {
        "module": (
            "backend.server.pipelines.connect_domain."
            "linking_target_pipeline.live_domain_target_pool.stage"
        ),
        "path": ROOT / (
            "backend/server/pipelines/connect_domain/"
            "linking_target_pipeline/live_domain_target_pool/stage.py"
        ),
    },
    "active_target_set": {
        "module": (
            "backend.server.pipelines.connect_domain."
            "linking_target_pipeline.active_target_set.stage"
        ),
        "path": ROOT / (
            "backend/server/pipelines/connect_domain/"
            "linking_target_pipeline/active_target_set/stage.py"
        ),
    },
}

PACKAGE_AUTHORITY = (
    ROOT
    / "backend/server/runtime/runtime_registration_package.py"
)

REGISTRATION_AUTHORITY = (
    ROOT
    / "backend/server/runtime/universal_runtime_registration.py"
)

JOB_TYPES = (
    ROOT
    / "backend/server/pipelines/connect_domain/job_types.py"
)

PIPELINE_ROOT = (
    ROOT
    / "backend/server/pipelines/connect_domain"
)


def digest(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def public(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)

    if isinstance(value, dict):
        return {
            str(key): public(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set, frozenset)):
        return [
            public(item)
            for item in value
        ]

    return value


def declared_functions(
    tree: ast.AST,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []

    for node in tree.body:
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        output.append({
            "name": node.name,
            "async": isinstance(
                node,
                ast.AsyncFunctionDef,
            ),
            "line": node.lineno,
            "decorators": [
                ast.unparse(item)
                for item in node.decorator_list
            ],
            "calls": sorted({
                (
                    call.func.id
                    if isinstance(
                        call.func,
                        ast.Name,
                    )
                    else call.func.attr
                    if isinstance(
                        call.func,
                        ast.Attribute,
                    )
                    else ast.unparse(
                        call.func
                    )
                )
                for call in ast.walk(node)
                if isinstance(
                    call,
                    ast.Call,
                )
            }),
        })

    return output


def declared_classes(
    tree: ast.AST,
) -> list[dict[str, Any]]:
    return [
        {
            "name": node.name,
            "line": node.lineno,
            "decorators": [
                ast.unparse(item)
                for item in node.decorator_list
            ],
        }
        for node in tree.body
        if isinstance(
            node,
            ast.ClassDef,
        )
    ]


def registration_calls(
    path: Path,
) -> list[dict[str, Any]]:
    source = path.read_text(
        encoding="utf-8",
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    calls: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        name = None

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

        if name not in {
            "register_runtime_handler",
            "runtime_handler",
            "create_runtime_registration_package",
        }:
            continue

        calls.append({
            "name": name,
            "line": node.lineno,
            "source": ast.get_source_segment(
                source,
                node,
            ),
        })

    return calls


result: dict[str, Any] = {
    "project_root": str(ROOT),
    "production_source_changes": "NONE",
    "runtime_registrations_created": "NO",
    "registry_persistence_executed": "NO",
    "handlers_executed": "NO",
    "stages": {},
    "registration_authorities": {},
    "existing_registration_files": [],
    "job_types": {},
}

standard_error = ""

try:
    sys.path.insert(
        0,
        str(ROOT),
    )

    required_files = [
        PACKAGE_AUTHORITY,
        REGISTRATION_AUTHORITY,
        JOB_TYPES,
        *[
            stage["path"]
            for stage in STAGES.values()
        ],
    ]

    for path in required_files:
        if not path.is_file():
            raise FileNotFoundError(
                f"Required source unavailable: {path}"
            )

        py_compile.compile(
            str(path),
            doraise=True,
        )

    for stage_name, specification in STAGES.items():
        path = specification["path"]
        module_name = specification["module"]

        source = path.read_text(
            encoding="utf-8",
        )

        tree = ast.parse(
            source,
            filename=str(path),
        )

        module = importlib.import_module(
            module_name
        )

        runtime_signatures: dict[str, str] = {}
        dataclass_fields: dict[str, list[str]] = {}

        for name, value in vars(module).items():
            if inspect.isfunction(value):
                if (
                    getattr(
                        value,
                        "__module__",
                        "",
                    )
                    == module_name
                ):
                    runtime_signatures[name] = str(
                        inspect.signature(
                            value
                        )
                    )

            if inspect.isclass(value):
                if dataclasses.is_dataclass(
                    value
                ):
                    dataclass_fields[name] = [
                        field.name
                        for field in dataclasses.fields(
                            value
                        )
                    ]

        result["stages"][stage_name] = {
            "path": str(path),
            "module": module_name,
            "sha256": digest(path),
            "syntax": "PASS",
            "declared_functions": declared_functions(
                tree
            ),
            "declared_classes": declared_classes(
                tree
            ),
            "runtime_signatures": runtime_signatures,
            "dataclass_fields": dataclass_fields,
        }

    package_module = importlib.import_module(
        "backend.server.runtime."
        "runtime_registration_package"
    )

    registration_module = importlib.import_module(
        "backend.server.runtime."
        "universal_runtime_registration"
    )

    package_names = [
        "create_runtime_registration_package",
        "registration_fingerprint_payload",
        "calculate_registration_fingerprint",
    ]

    registration_names = [
        "register_runtime_handler",
        "runtime_handler",
        "get_runtime_registration",
        "dispatch_registered_runtime_handler",
        "runtime_registration_snapshot",
    ]

    result["registration_authorities"] = {
        "package_source": {
            "path": str(
                PACKAGE_AUTHORITY
            ),
            "sha256": digest(
                PACKAGE_AUTHORITY
            ),
        },
        "registration_source": {
            "path": str(
                REGISTRATION_AUTHORITY
            ),
            "sha256": digest(
                REGISTRATION_AUTHORITY
            ),
        },
        "package_api": {
            name: (
                str(
                    inspect.signature(
                        getattr(
                            package_module,
                            name,
                        )
                    )
                )
                if hasattr(
                    package_module,
                    name,
                )
                else "MISSING"
            )
            for name in package_names
        },
        "registration_api": {
            name: (
                str(
                    inspect.signature(
                        getattr(
                            registration_module,
                            name,
                        )
                    )
                )
                if hasattr(
                    registration_module,
                    name,
                )
                else "MISSING"
            )
            for name in registration_names
        },
    }

    job_source = JOB_TYPES.read_text(
        encoding="utf-8",
    )

    job_tree = ast.parse(
        job_source,
        filename=str(JOB_TYPES),
    )

    for node in job_tree.body:
        if not isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            continue

        targets = (
            node.targets
            if isinstance(
                node,
                ast.Assign,
            )
            else [node.target]
        )

        value = node.value

        if not isinstance(
            value,
            ast.Constant,
        ):
            continue

        for target in targets:
            if isinstance(
                target,
                ast.Name,
            ):
                result["job_types"][
                    target.id
                ] = value.value

    for path in sorted(
        PIPELINE_ROOT.rglob(
            "*.py"
        )
    ):
        calls = registration_calls(
            path
        )

        if calls:
            result[
                "existing_registration_files"
            ].append({
                "path": str(
                    path.relative_to(
                        ROOT
                    )
                ),
                "sha256": digest(path),
                "calls": calls,
            })

except Exception:
    standard_error = traceback.format_exc()


complete = not standard_error

lines = [
    "LINKCRAFTER PIPELINE REGISTRATION",
    "PART B STEP 5 REGISTRATION PACKAGE PREFLIGHT",
    "",
    "Mode: READ-ONLY CONTRACT DISCOVERY",
    "Production source changes: NONE",
    "Runtime registrations created: NO",
    "Registry persistence executed: NO",
    "Handlers executed: NO",
    (
        "PREFLIGHT STATUS: COMPLETE"
        if complete
        else "PREFLIGHT STATUS: NOT_COMPLETE"
    ),
    "",
    "=" * 112,
    "DISCOVERED CONTRACT",
    "=" * 112,
    json.dumps(
        public(result),
        indent=2,
        sort_keys=True,
        default=str,
    ),
    "",
    "=" * 112,
    "STANDARD ERROR",
    "=" * 112,
    standard_error,
    "",
    "=" * 112,
    "NEXT ACTION",
    "=" * 112,
    (
        "Create and load the six certified 11-part "
        "stage registration packages."
        if complete
        else
        "Resolve the preflight failure before creating registrations."
    ),
    "",
    "=" * 112,
    "FINAL RESULT",
    "=" * 112,
    (
        "PART B STEP 5 PREFLIGHT COMPLETE"
        if complete
        else
        "PART B STEP 5 PREFLIGHT NOT_COMPLETE"
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
    if complete
    else 1
)