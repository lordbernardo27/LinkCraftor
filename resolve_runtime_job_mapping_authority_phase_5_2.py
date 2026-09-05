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
    / "runtime_job_mapping_phase_5_2_mapping_authority_resolution.txt"
)


MODULES = (
    "backend.server.runtime.universal_job_submission",
    "backend.server.runtime.universal_orchestration.run_identity",
    "backend.server.runtime.uucd_runtime_handoff_v1",
    "backend.server.runtime.universal_jobs.creation_engine",
)


FROZEN_5_1 = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "coordination_runtime_bridge.py"
)

EXPECTED_5_1_SHA = (
    "2DD7AF262C879B4DD58A484AB7470D9E"
    "A9883A80DDE3C77F1DC1ACDFD35CD0E2"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def sig(obj):
    try:
        return str(
            inspect.signature(
                obj
            )
        )
    except Exception as exc:
        return (
            "<SIGNATURE ERROR: "
            + repr(exc)
            + ">"
        )


def source_block(
    source,
    start,
    end,
    pad=2,
):
    lines = source.splitlines()

    lo = max(
        0,
        start - 1 - pad,
    )

    hi = min(
        len(lines),
        end + pad,
    )

    return "\n".join(
        f"{i + 1:05d}: {lines[i]}"
        for i
        in range(
            lo,
            hi,
        )
    )


report = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.2 — RUNTIME JOB MAPPING",
    "MAPPING AUTHORITY RESOLUTION",
    "=" * 120,
    "",
]


# =========================================================================
# 1. Frozen 5.1 integrity
# =========================================================================

current_5_1_sha = sha256(
    FROZEN_5_1
)

report.extend(
    (
        "1. FROZEN PHASE 5.1 INTEGRITY",
        "=" * 120,
        f"Current SHA256: {current_5_1_sha}",
        (
            "Exact frozen SHA: "
            + str(
                current_5_1_sha
                == EXPECTED_5_1_SHA
            )
        ),
        "",
    )
)


# =========================================================================
# 2. Deep module inspection
# =========================================================================

for module_name in MODULES:

    report.extend(
        (
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
            + repr(exc)
        )
        report.append("")
        continue


    path = Path(
        inspect.getfile(
            module
        )
    ).resolve()

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source
    )


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

    report.append("")


    # ---------------------------------------------------------------------
    # Public functions
    # ---------------------------------------------------------------------

    report.append(
        "PUBLIC FUNCTIONS"
    )

    public_functions = []

    for node in tree.body:

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):

            if node.name.startswith(
                "_"
            ):
                continue

            public_functions.append(
                node.name
            )

            obj = getattr(
                module,
                node.name,
                None,
            )

            report.append("")
            report.append(
                node.name
            )

            report.append(
                "  signature: "
                + (
                    sig(obj)
                    if obj is not None
                    else "<missing>"
                )
            )

            report.append(
                f"  lines: {node.lineno}-{node.end_lineno}"
            )

            report.append(
                "  source:"
            )

            report.append(
                source_block(
                    source,
                    node.lineno,
                    node.end_lineno,
                )
            )


    if not public_functions:
        report.append(
            "  NONE"
        )


    # ---------------------------------------------------------------------
    # Public classes
    # ---------------------------------------------------------------------

    report.append("")
    report.append(
        "PUBLIC CLASSES"
    )

    found_class = False

    for node in tree.body:

        if not isinstance(
            node,
            ast.ClassDef,
        ):
            continue

        if node.name.startswith(
            "_"
        ):
            continue

        found_class = True

        obj = getattr(
            module,
            node.name,
            None,
        )

        report.append("")
        report.append(
            node.name
        )

        if obj is not None:

            report.append(
                "  signature: "
                + sig(
                    obj
                )
            )

            if is_dataclass(
                obj
            ):
                report.append(
                    "  dataclass fields:"
                )

                for item in fields(
                    obj
                ):
                    report.append(
                        "    - "
                        + item.name
                    )


    if not found_class:
        report.append(
            "  NONE"
        )


    # ---------------------------------------------------------------------
    # Function call graph
    # ---------------------------------------------------------------------

    report.append("")
    report.append(
        "IMPORTANT CALLS"
    )

    interesting_calls = {
        "create_universal_job",
        "normalize_universal_job_creation_request",
        "submit_universal_job",
        "enqueue_job",
        "append_job",
        "write_job",
        "write_queue",
        "get_runtime_registration",
        "is_runtime_job_type_registered",
        "dispatch_registered_runtime_handler",
        "execute_registered_runtime_job_v1",
        "resolve_pipeline_run_id",
        "create_pipeline_run_id",
        "generate_pipeline_run_id",
    }


    call_hits = []

    for node in ast.walk(
        tree
    ):

        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        func = node.func

        name = None

        if isinstance(
            func,
            ast.Name,
        ):
            name = func.id

        elif isinstance(
            func,
            ast.Attribute,
        ):
            name = func.attr

        if (
            name
            and name
            in interesting_calls
        ):
            call_hits.append(
                (
                    name,
                    node.lineno,
                )
            )


    if call_hits:

        for name, line in call_hits:

            report.append(
                f"  line {line}: {name}(...)"
            )

    else:
        report.append(
            "  NONE"
        )


    # ---------------------------------------------------------------------
    # Specific semantic markers
    # ---------------------------------------------------------------------

    report.append("")
    report.append(
        "SEMANTIC FIELD MARKERS"
    )

    for marker in (
        "pipeline_run_id",
        "correlation_id",
        "workflow_id",
        "stage_id",
        "runtime_stage",
        "job_type",
        "enqueue",
        "priority",
        "maximum_attempts",
        "idempotency_key",
        "parent_job_id",
        "dependency_job_ids",
        "batch_id",
        "metadata",
        "payload",
    ):

        count = source.count(
            marker
        )

        report.append(
            f"  {marker}: {count}"
        )


    # ---------------------------------------------------------------------
    # Runtime/Coordination imports
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

            name = (
                node.module
                or ""
            )

            if name.startswith(
                "backend.server.runtime"
            ):
                runtime_imports.append(
                    name
                )

            if name.startswith(
                "backend.server.coordination"
            ):
                coordination_imports.append(
                    name
                )

        elif isinstance(
            node,
            ast.Import,
        ):

            for alias in node.names:

                name = alias.name

                if name.startswith(
                    "backend.server.runtime"
                ):
                    runtime_imports.append(
                        name
                    )

                if name.startswith(
                    "backend.server.coordination"
                ):
                    coordination_imports.append(
                        name
                    )


    report.append("")
    report.append(
        "RUNTIME IMPORTS"
    )

    for item in sorted(
        set(
            runtime_imports
        )
    ):
        report.append(
            "  -> "
            + item
        )

    if not runtime_imports:
        report.append(
            "  NONE"
        )


    report.append("")
    report.append(
        "COORDINATION IMPORTS"
    )

    for item in sorted(
        set(
            coordination_imports
        )
    ):
        report.append(
            "  -> "
            + item
        )

    if not coordination_imports:
        report.append(
            "  NONE"
        )

    report.append("")


# =========================================================================
# 3. Explicit architecture questions
# =========================================================================

report.extend(
    (
        "=" * 120,
        "3. PHASE 5.2 AUTHORITY QUESTIONS",
        "=" * 120,
        "",
        "A. UNIVERSAL JOB CREATION",
        "- Does universal_job_submission.py call create_universal_job()?",
        "- Does it own queue/persistence/submission after creation?",
        "- Is create_universal_job() itself still I/O-free?",
        "",
        "B. 5.2 OUTPUT TYPE",
        "- Should Phase 5.2 construct UniversalJobCreationRequest only?",
        "- Should Phase 5.2 call create_universal_job() and return UniversalJobCreationResult?",
        "- Should Phase 5.2 hand to universal_job_submission.py instead?",
        "",
        "C. CORRELATION OWNERSHIP",
        "- Is pipeline_run_id a Runtime run identity rather than Coordination workflow identity?",
        "- Does run_identity.py already own generation/resolution of pipeline_run_id?",
        "- Does correlation_id belong in Runtime metadata until Phase 5.3?",
        "- Should workflow_id remain metadata until Phase 5.3?",
        "",
        "D. STAGE IDENTITY",
        "- Should request.pipeline = RuntimeHandoffIntent.pipeline_id?",
        "- Should request.stage = RuntimeHandoffIntent.runtime_stage?",
        "- Should coordination stage_id remain metadata?",
        "",
        "E. DEFAULT / RUNTIME-OWNED FIELDS",
        "- Should user_id remain Universal Job default unless separately supplied?",
        "- Should product_id remain Universal Job default unless separately supplied?",
        "- Should priority remain Universal Job default?",
        "- Should maximum_attempts remain Creation Engine/registration default?",
        "- Should idempotency_key remain unset here?",
        "- Should parent/dependency IDs remain unset until Runtime lineage exists?",
        "- Should enqueue remain default or be forced False?",
        "",
    )
)


# =========================================================================
# 4. Provisional safe mapping
# =========================================================================

report.extend(
    (
        "=" * 120,
        "4. PROVISIONAL SAFE FIELD MAPPING",
        "=" * 120,
        "",
        "Likely direct mapping:",
        "  intent.workspace_id -> request.workspace_id",
        "  intent.job_type -> request.job_type",
        "  intent.payload -> request.payload",
        "  intent.metadata -> request.metadata base",
        "  intent.pipeline_id -> request.pipeline",
        "  intent.runtime_stage -> request.stage",
        "",
        "Likely metadata preservation:",
        "  intent.workflow_id -> metadata['coordination_workflow_id']",
        "  intent.correlation_id -> metadata['coordination_correlation_id']",
        "  intent.stage_id -> metadata['coordination_stage_id']",
        "  intent.stage_version -> metadata['coordination_stage_version']",
        "  intent.workflow_type -> metadata['coordination_workflow_type']",
        "  intent.wave_index -> metadata['coordination_wave_index']",
        "  intent.execution_semantics -> metadata['coordination_execution_semantics']",
        "  intent.stage_reference_contract_version -> metadata[...]",
        "  intent.intent_version -> metadata[...]",
        "",
        "Likely NOT assigned by 5.2 unless existing authority proves otherwise:",
        "  pipeline_run_id",
        "  parent_job_id",
        "  dependency_job_ids",
        "  batch_id",
        "  idempotency_key",
        "  job_id",
        "  created_at",
        "  maximum_attempts",
        "  priority",
        "",
        "NOT YET FROZEN.",
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
print("PHASE 5.2 — MAPPING AUTHORITY RESOLUTION COMPLETE")
print("=" * 120)
print(
    "Frozen 5.1 exact:",
    current_5_1_sha
    == EXPECTED_5_1_SHA,
)
print(
    "Production modified: False"
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 120)
