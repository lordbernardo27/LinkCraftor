from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
from dataclasses import fields, is_dataclass
from pathlib import Path


ROOT = Path.cwd()

REPORT = (
    ROOT
    / "runtime_job_mapping_phase_5_2_discovery_scan.txt"
)


MODULES = (
    "backend.server.coordination.runtime_integration.coordination_runtime_bridge",
    "backend.server.runtime.universal_jobs.creation_engine",
    "backend.server.runtime.universal_jobs.contract",
    "backend.server.runtime.universal_jobs.metadata",
    "backend.server.runtime.universal_jobs.lineage",
    "backend.server.runtime.universal_jobs.idempotency_key",
    "backend.server.runtime.universal_jobs.payload_reference",
    "backend.server.runtime.universal_jobs.priority",
    "backend.server.runtime.universal_jobs.status",
    "backend.server.runtime.universal_runtime_registration",
)


TARGETS = {
    "backend.server.coordination.runtime_integration.coordination_runtime_bridge": (
        "RuntimeHandoffContext",
        "RuntimeHandoffIntent",
        "CoordinationRuntimeBridgeResult",
        "bridge_execution_plan_to_runtime",
    ),

    "backend.server.runtime.universal_jobs.creation_engine": (
        "UniversalJobCreationRequest",
        "UniversalJobCreationResult",
        "normalize_universal_job_creation_request",
        "create_universal_job",
    ),

    "backend.server.runtime.universal_jobs.contract": (
        "UniversalJob",
        "validate_universal_job",
    ),

    "backend.server.runtime.universal_runtime_registration": (
        "get_runtime_registration",
        "is_runtime_job_type_registered",
    ),
}


FROZEN_5_1_FILE = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "coordination_runtime_bridge.py"
)

FROZEN_5_1_EXPECTED_SHA = (
    "2DD7AF262C879B4DD58A484AB7470D9E"
    "A9883A80DDE3C77F1DC1ACDFD35CD0E2"
)


def sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def safe_signature(
    obj,
):
    try:
        return str(
            inspect.signature(
                obj
            )
        )
    except Exception as exc:
        return (
            "<SIGNATURE ERROR: "
            + repr(
                exc
            )
            + ">"
        )


def dataclass_fields(
    obj,
):
    if not is_dataclass(
        obj
    ):
        return ()

    return tuple(
        item.name
        for item
        in fields(
            obj
        )
    )


def public_functions_from_ast(
    path: Path,
):
    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source
    )

    functions = []

    for node in tree.body:

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            if not node.name.startswith(
                "_"
            ):
                functions.append(
                    (
                        node.name,
                        node.lineno,
                        node.end_lineno,
                    )
                )

    return (
        source,
        tree,
        functions,
    )


def source_excerpt(
    source: str,
    start: int,
    end: int,
    padding: int = 2,
):
    lines = source.splitlines()

    lo = max(
        0,
        start - 1 - padding,
    )

    hi = min(
        len(
            lines
        ),
        end + padding,
    )

    return "\n".join(
        f"{index + 1:05d}: {lines[index]}"
        for index
        in range(
            lo,
            hi,
        )
    )


report = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.2 — RUNTIME JOB MAPPING",
    "DISCOVERY SCAN",
    "=" * 120,
    "",
]


# =========================================================================
# 1. Frozen Phase 5.1 integrity
# =========================================================================

report.extend(
    (
        "1. FROZEN PHASE 5.1 INTEGRITY",
        "=" * 120,
    )
)

if FROZEN_5_1_FILE.exists():

    actual_5_1_sha = sha256(
        FROZEN_5_1_FILE
    )

    report.append(
        f"5.1 file exists: True"
    )

    report.append(
        f"5.1 current SHA256: {actual_5_1_sha}"
    )

    report.append(
        "5.1 frozen SHA exact: "
        + str(
            actual_5_1_sha
            == FROZEN_5_1_EXPECTED_SHA
        )
    )

else:

    report.append(
        "5.1 file exists: False"
    )


# =========================================================================
# 2. Module inspection
# =========================================================================

for module_name in MODULES:

    report.extend(
        (
            "",
            "=" * 120,
            f"MODULE: {module_name}",
            "=" * 120,
        )
    )

    try:

        module = importlib.import_module(
            module_name
        )

    except Exception as exc:

        report.append(
            "IMPORT FAILED: "
            + repr(
                exc
            )
        )

        continue


    path = Path(
        inspect.getfile(
            module
        )
    ).resolve()

    report.append(
        "FILE: "
        + str(
            path.relative_to(
                ROOT
            )
        )
    )

    report.append(
        "SHA256: "
        + sha256(
            path
        )
    )


    source, tree, ast_functions = (
        public_functions_from_ast(
            path
        )
    )


    configured = TARGETS.get(
        module_name,
        (),
    )

    if configured:

        report.append("")
        report.append(
            "TARGET OBJECTS"
        )

        for name in configured:

            obj = getattr(
                module,
                name,
                None,
            )

            report.append("")
            report.append(
                name
            )

            report.append(
                "  exists: "
                + str(
                    obj
                    is not None
                )
            )

            if obj is None:
                continue

            report.append(
                "  signature: "
                + safe_signature(
                    obj
                )
            )

            dc_fields = dataclass_fields(
                obj
            )

            if dc_fields:

                report.append(
                    "  dataclass fields:"
                )

                for field_name in dc_fields:

                    report.append(
                        "    - "
                        + field_name
                    )


            ast_match = next(
                (
                    item
                    for item
                    in ast_functions
                    if item[
                        0
                    ]
                    == name
                ),
                None,
            )

            if ast_match:

                _, start, end = ast_match

                report.append(
                    f"  lines: {start}-{end}"
                )

                report.append(
                    "  source:"
                )

                report.append(
                    source_excerpt(
                        source,
                        start,
                        end,
                    )
                )


    # ---------------------------------------------------------------------
    # Imports
    # ---------------------------------------------------------------------

    runtime_imports = []
    coordination_imports = []

    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.ImportFrom,
        ):

            imported = (
                node.module
                or ""
            )

            if imported.startswith(
                "backend.server.runtime"
            ):
                runtime_imports.append(
                    imported
                )

            if imported.startswith(
                "backend.server.coordination"
            ):
                coordination_imports.append(
                    imported
                )

        elif isinstance(
            node,
            ast.Import,
        ):

            for alias in node.names:

                imported = (
                    alias.name
                )

                if imported.startswith(
                    "backend.server.runtime"
                ):
                    runtime_imports.append(
                        imported
                    )

                if imported.startswith(
                    "backend.server.coordination"
                ):
                    coordination_imports.append(
                        imported
                    )


    report.append("")
    report.append(
        "RUNTIME IMPORTS"
    )

    if runtime_imports:

        for item in sorted(
            set(
                runtime_imports
            )
        ):
            report.append(
                "  -> "
                + item
            )

    else:

        report.append(
            "  NONE"
        )


    report.append("")
    report.append(
        "COORDINATION IMPORTS"
    )

    if coordination_imports:

        for item in sorted(
            set(
                coordination_imports
            )
        ):
            report.append(
                "  -> "
                + item
            )

    else:

        report.append(
            "  NONE"
        )


# =========================================================================
# 3. Direct field comparison: 5.1 Intent → Job Creation Request
# =========================================================================

report.extend(
    (
        "",
        "=" * 120,
        "3. FIELD COMPARISON — 5.1 INTENT → UNIVERSAL JOB CREATION REQUEST",
        "=" * 120,
    )
)


bridge_module = importlib.import_module(
    "backend.server.coordination.runtime_integration.coordination_runtime_bridge"
)

creation_module = importlib.import_module(
    "backend.server.runtime.universal_jobs.creation_engine"
)


intent_cls = getattr(
    bridge_module,
    "RuntimeHandoffIntent"
)

request_cls = getattr(
    creation_module,
    "UniversalJobCreationRequest"
)


intent_fields = dataclass_fields(
    intent_cls
)

request_fields = dataclass_fields(
    request_cls
)


report.append(
    "RuntimeHandoffIntent fields:"
)

for name in intent_fields:
    report.append(
        "  - "
        + name
    )


report.append("")
report.append(
    "UniversalJobCreationRequest fields:"
)

for name in request_fields:
    report.append(
        "  - "
        + name
    )


direct_overlap = tuple(
    name
    for name
    in intent_fields
    if name
    in request_fields
)


report.append("")
report.append(
    "Direct field-name overlap:"
)

for name in direct_overlap:
    report.append(
        "  - "
        + name
    )


intent_only = tuple(
    name
    for name
    in intent_fields
    if name
    not in request_fields
)

request_only = tuple(
    name
    for name
    in request_fields
    if name
    not in intent_fields
)


report.append("")
report.append(
    "Intent-only fields:"
)

for name in intent_only:
    report.append(
        "  - "
        + name
    )


report.append("")
report.append(
    "Creation-request-only fields:"
)

for name in request_only:
    report.append(
        "  - "
        + name
    )


# =========================================================================
# 4. Candidate semantic mapping questions
# =========================================================================

report.extend(
    (
        "",
        "=" * 120,
        "4. PHASE 5.2 SEMANTIC MAPPING QUESTIONS",
        "=" * 120,
        "",
        "Direct candidates:",
        "  RuntimeHandoffIntent.workspace_id -> UniversalJobCreationRequest.workspace_id",
        "  RuntimeHandoffIntent.job_type -> UniversalJobCreationRequest.job_type",
        "  RuntimeHandoffIntent.payload -> UniversalJobCreationRequest.payload",
        "  RuntimeHandoffIntent.runtime_stage -> UniversalJobCreationRequest.stage ?",
        "  RuntimeHandoffIntent.pipeline_id -> UniversalJobCreationRequest.pipeline ?",
        "  RuntimeHandoffIntent.metadata -> UniversalJobCreationRequest.metadata",
        "",
        "Correlation candidates requiring resolution:",
        "  RuntimeHandoffIntent.workflow_id -> UniversalJobCreationRequest.pipeline_run_id ?",
        "  RuntimeHandoffIntent.correlation_id -> metadata ?",
        "  RuntimeHandoffIntent.stage_id -> metadata ? stage ?",
        "  RuntimeHandoffIntent.wave_index -> metadata ?",
        "  RuntimeHandoffIntent.execution_semantics -> metadata ?",
        "",
        "Fields with no direct 5.1 authority:",
        "  user_id",
        "  product_id",
        "  payload_reference",
        "  priority",
        "  parent_job_id",
        "  dependency_job_ids",
        "  batch_id",
        "  idempotency_key",
        "  maximum_attempts",
        "  enqueue",
        "  job_id",
        "  job_id_prefix",
        "  created_at",
        "",
        "Questions:",
        "- Which creation-request fields may Phase 5.2 populate directly?",
        "- Which fields must remain defaults owned by the Universal Job Creation Engine?",
        "- Should workflow_id map to pipeline_run_id or remain metadata until Phase 5.3?",
        "- Should correlation_id remain metadata only until Phase 5.3?",
        "- Should stage_id map to request.stage, or should runtime_stage map to request.stage?",
        "- Should pipeline_id map directly to request.pipeline?",
        "- Should Phase 5.2 call get_runtime_registration(), or receive registration metadata from another layer?",
        "- Should Phase 5.2 call create_universal_job() directly?",
        "- Or should Phase 5.2 only construct UniversalJobCreationRequest / mapping and leave actual creation to Runtime?",
        "- Should enqueue be False at mapping time to preserve separation from Runtime submission?",
        "- Who owns priority?",
        "- Who owns maximum_attempts?",
        "- Who owns idempotency_key?",
        "- Who owns parent/dependency job IDs?",
        "- Can Phase 5.2 create jobs without any queue/persistence/dispatch side effect?",
    )
)


# =========================================================================
# 5. Static search for existing mapping/adapter candidates
# =========================================================================

report.extend(
    (
        "",
        "=" * 120,
        "5. EXISTING MAPPING / ADAPTER CANDIDATES",
        "=" * 120,
    )
)


scan_roots = (
    ROOT
    / "backend/server/coordination",
    ROOT
    / "backend/server/runtime",
)


keywords = (
    "RuntimeHandoffIntent",
    "UniversalJobCreationRequest",
    "create_universal_job(",
    "pipeline_run_id",
    "correlation_id",
    "runtime_job_mapping",
    "job mapping",
)


hits = []


for scan_root in scan_roots:

    if not scan_root.exists():
        continue

    for path in scan_root.rglob(
        "*.py"
    ):

        try:
            text = path.read_text(
                encoding="utf-8-sig"
            )
        except Exception:
            continue

        matched = tuple(
            keyword
            for keyword
            in keywords
            if keyword
            in text
        )

        if matched:

            hits.append(
                (
                    str(
                        path.relative_to(
                            ROOT
                        )
                    ),
                    matched,
                )
            )


if hits:

    for path, matched in hits:

        report.append(
            path
        )

        report.append(
            "  matches: "
            + ", ".join(
                matched
            )
        )

else:

    report.append(
        "NONE"
    )


# =========================================================================
# 6. Boundary collision scan
# =========================================================================

report.extend(
    (
        "",
        "=" * 120,
        "6. PHASE 5.2 RESPONSIBILITY COLLISION SCAN",
        "=" * 120,
        "",
        "Phase 5.2 MUST NOT silently absorb responsibilities belonging to:",
        "  5.1 Coordination -> Runtime Bridge",
        "  5.3 Workflow/Job Correlation",
        "  5.4 Runtime Completion Intake",
        "  5.5 Runtime Failure Intake",
        "  Runtime Registration",
        "  Runtime queue / worker infrastructure",
        "  Runtime business handler dispatch",
        "",
        "Provisional Phase 5.2 responsibility:",
        "  Convert one frozen Phase 5.1 RuntimeHandoffIntent into the exact",
        "  canonical input required by the existing Universal Job Creation Engine,",
        "  without queue writes, persistence, handler lookup, dispatch, execution,",
        "  completion processing, or failure processing.",
        "",
        "NOT YET FROZEN.",
    )
)


# =========================================================================
# 7. Final report summary
# =========================================================================

report.extend(
    (
        "",
        "=" * 120,
        "7. DISCOVERY STATUS",
        "=" * 120,
        "",
        "Discovery only.",
        "Production modified: False",
        "Architecture frozen: False",
        "Installation performed: False",
        "Next: Phase 5.2 Architecture Resolution after reviewing this report.",
    )
)


REPORT.write_text(
    "\n".join(
        report
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 120)
print("PHASE 5.2 — RUNTIME JOB MAPPING")
print("DISCOVERY SCAN COMPLETE")
print("=" * 120)

print(
    "Frozen 5.1 SHA:",
    sha256(
        FROZEN_5_1_FILE
    ),
)

print(
    "Frozen 5.1 exact:",
    sha256(
        FROZEN_5_1_FILE
    )
    == FROZEN_5_1_EXPECTED_SHA,
)

print()
print(
    "RuntimeHandoffIntent fields:",
    intent_fields,
)

print()
print(
    "UniversalJobCreationRequest fields:",
    request_fields,
)

print()
print(
    "Direct overlap:",
    direct_overlap,
)

print()
print(
    "REPORT:",
    REPORT.name,
)

print("=" * 120)
