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
    / "workflow_job_correlation_phase_5_3_discovery_scan.txt"
)


FROZEN_5_1 = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "coordination_runtime_bridge.py"
)

FROZEN_5_2 = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_job_mapping.py"
)

EXPECTED_5_1_SHA = (
    "2DD7AF262C879B4DD58A484AB7470D9E"
    "A9883A80DDE3C77F1DC1ACDFD35CD0E2"
)

EXPECTED_5_2_SHA = (
    "49227B0686DED28418DE7DEF21101643"
    "18DDCA3858469A05F5A596388BA84E6A"
)


MODULES = (
    "backend.server.coordination.runtime_integration.runtime_job_mapping",
    "backend.server.coordination.universal_stages.result_contract",
    "backend.server.coordination.universal_workflows.contract",
    "backend.server.runtime.universal_jobs.contract",
    "backend.server.runtime.universal_jobs.creation_engine",
    "backend.server.runtime.universal_jobs.lineage",
    "backend.server.runtime.universal_job_submission",
    "backend.server.runtime.runtime_state_store",
    "backend.server.runtime.universal_orchestration.run_identity",
    "backend.server.runtime.universal_runtime_registration",
)


SEARCH_ROOTS = (
    ROOT / "backend/server/coordination",
    ROOT / "backend/server/runtime",
    ROOT / "backend/server/orchestration",
    ROOT / "backend/server/jobs",
)


SEARCH_TERMS = (
    "workflow_id",
    "correlation_id",
    "stage_id",
    "job_id",
    "pipeline_run_id",
    "workflow_job",
    "job_correlation",
    "correlation_registry",
    "correlation_store",
    "runtime_state_store",
    "StageResult",
    "result_contract",
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
    source: str,
    start: int,
    end: int,
    pad: int = 2,
) -> str:

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
    "PHASE 5.3 — WORKFLOW/JOB CORRELATION",
    "DISCOVERY SCAN",
    "=" * 120,
    "",
]


# =========================================================================
# 1. Frozen upstream integrity
# =========================================================================

sha_5_1 = sha256(
    FROZEN_5_1
)

sha_5_2 = sha256(
    FROZEN_5_2
)

report.extend(
    (
        "1. FROZEN UPSTREAM INTEGRITY",
        "=" * 120,
        f"5.1 SHA256: {sha_5_1}",
        (
            "5.1 exact frozen SHA: "
            + str(
                sha_5_1
                == EXPECTED_5_1_SHA
            )
        ),
        f"5.2 SHA256: {sha_5_2}",
        (
            "5.2 exact frozen SHA: "
            + str(
                sha_5_2
                == EXPECTED_5_2_SHA
            )
        ),
        "",
    )
)


# =========================================================================
# 2. Module inspection
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
    # Public classes
    # ---------------------------------------------------------------------

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
    # Public functions touching identities
    # ---------------------------------------------------------------------

    report.append("")
    report.append(
        "IDENTITY / CORRELATION FUNCTIONS"
    )

    found_fn = False

    for node in tree.body:

        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        if node.name.startswith(
            "_"
        ):
            continue

        body_source = source_block(
            source,
            node.lineno,
            node.end_lineno,
            pad=0,
        )

        if not any(
            term in body_source
            or term in node.name
            for term
            in SEARCH_TERMS
        ):
            continue

        found_fn = True

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


    if not found_fn:
        report.append(
            "  NONE"
        )


    # ---------------------------------------------------------------------
    # Identity markers
    # ---------------------------------------------------------------------

    report.append("")
    report.append(
        "IDENTITY FIELD COUNTS"
    )

    for term in (
        "workflow_id",
        "correlation_id",
        "stage_id",
        "job_id",
        "workspace_id",
        "pipeline_run_id",
        "batch_id",
        "orchestration_run_id",
    ):

        report.append(
            f"  {term}: "
            + str(
                source.count(
                    term
                )
            )
        )


    # ---------------------------------------------------------------------
    # Imports
    # ---------------------------------------------------------------------

    coordination_imports = []
    runtime_imports = []

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
                "backend.server.coordination"
            ):
                coordination_imports.append(
                    name
                )

            if name.startswith(
                "backend.server.runtime"
            ):
                runtime_imports.append(
                    name
                )

        elif isinstance(
            node,
            ast.Import,
        ):

            for alias in node.names:

                name = alias.name

                if name.startswith(
                    "backend.server.coordination"
                ):
                    coordination_imports.append(
                        name
                    )

                if name.startswith(
                    "backend.server.runtime"
                ):
                    runtime_imports.append(
                        name
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


# =========================================================================
# 3. Repository correlation candidate scan
# =========================================================================

report.extend(
    (
        "=" * 120,
        "3. REPOSITORY CORRELATION CANDIDATES",
        "=" * 120,
        "",
    )
)


candidate_files = []

for root in SEARCH_ROOTS:

    if not root.exists():
        continue

    for path in root.rglob(
        "*.py"
    ):

        try:
            source = path.read_text(
                encoding="utf-8-sig"
            )

        except Exception:
            continue

        hits = tuple(
            term
            for term
            in SEARCH_TERMS
            if term in source
        )

        identity_hits = sum(
            1
            for term
            in (
                "workflow_id",
                "correlation_id",
                "stage_id",
                "job_id",
            )
            if term in source
        )

        if (
            identity_hits >= 2
            or "job_correlation" in source
            or "correlation_registry" in source
            or "correlation_store" in source
        ):

            candidate_files.append(
                (
                    path,
                    hits,
                )
            )


candidate_files.sort(
    key=lambda item: str(
        item[0]
    )
)


for path, hits in candidate_files:

    report.append(
        str(
            path.relative_to(
                ROOT
            )
        )
    )

    report.append(
        "  matches: "
        + ", ".join(
            hits
        )
    )


if not candidate_files:
    report.append(
        "NONE"
    )


# =========================================================================
# 4. Existing StageResult correlation capacity
# =========================================================================

report.extend(
    (
        "",
        "=" * 120,
        "4. STAGE RESULT CORRELATION QUESTIONS",
        "=" * 120,
        "",
        "Verify whether StageResult already carries:",
        "  workflow_id",
        "  correlation_id",
        "  stage_id",
        "  workspace_id",
        "  job_id",
        "  job_type",
        "  execution_target",
        "",
        "If yes:",
        "  Phase 5.3 should likely produce the authoritative",
        "  workflow/stage/job binding needed by 5.4 and 5.5.",
        "",
    )
)


# =========================================================================
# 5. Correlation architecture questions
# =========================================================================

report.extend(
    (
        "=" * 120,
        "5. PHASE 5.3 ARCHITECTURE QUESTIONS",
        "=" * 120,
        "",
        "A. CREATION POINT",
        "- At what exact point does canonical job_id first exist?",
        "- Is UniversalJobCreationResult the first trustworthy job identity?",
        "- Does submit_universal_job return the same canonical job_id?",
        "",
        "B. BINDING",
        "- Should Phase 5.3 bind:",
        "    workflow_id",
        "    correlation_id",
        "    stage_id",
        "    workspace_id",
        "    job_id",
        "    job_type",
        "    pipeline_id",
        "    runtime_stage",
        "?",
        "",
        "C. PIPELINE RUN ID",
        "- Should Phase 5.3 populate UniversalJob.pipeline_run_id?",
        "- Or should pipeline_run_id remain Runtime lineage only?",
        "- Is there an existing pipeline_run_id authority elsewhere?",
        "",
        "D. STORAGE",
        "- Is there an existing correlation registry/store?",
        "- Can runtime_state_store own this binding?",
        "- Or should UCF own a dedicated workflow/job correlation registry?",
        "",
        "E. RETURN PATH",
        "- How will 5.4 Runtime Completion Intake resolve:",
        "    job_id -> workflow_id/correlation_id/stage_id ?",
        "- How will 5.5 Runtime Failure Intake perform the same lookup?",
        "",
        "F. MULTIPLE JOBS",
        "- Can one workflow stage have more than one runtime job?",
        "- Can one workflow have many stage/job bindings?",
        "- Must duplicate correlation registration fail closed?",
        "",
    )
)


# =========================================================================
# 6. Preliminary boundary
# =========================================================================

report.extend(
    (
        "=" * 120,
        "6. PROVISIONAL PHASE 5.3 RESPONSIBILITY",
        "=" * 120,
        "",
        "Likely responsibility:",
        "  Bind Coordination identity to an actual canonical Runtime job_id",
        "  after Universal Job creation and before completion/failure intake.",
        "",
        "Likely correlation tuple:",
        "  workflow_id",
        "  correlation_id",
        "  stage_id",
        "  workspace_id",
        "  job_id",
        "  job_type",
        "  pipeline_id",
        "  runtime_stage",
        "",
        "Likely NOT owned by Phase 5.3:",
        "  Universal Job creation",
        "  Runtime Registration lookup",
        "  queue persistence",
        "  handler dispatch",
        "  worker execution",
        "  workflow lifecycle transitions",
        "  completion processing",
        "  failure processing",
        "",
        "NOT YET FROZEN.",
        "",
    )
)


# =========================================================================
# 7. Discovery status
# =========================================================================

report.extend(
    (
        "=" * 120,
        "7. DISCOVERY STATUS",
        "=" * 120,
        "",
        "Discovery only.",
        "Production modified: False",
        "Architecture frozen: False",
        "Installation performed: False",
        "Next: Phase 5.3 Correlation Authority Resolution",
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
print("PHASE 5.3 — WORKFLOW/JOB CORRELATION")
print("DISCOVERY SCAN COMPLETE")
print("=" * 120)

print(
    "Frozen 5.1 exact:",
    sha_5_1
    == EXPECTED_5_1_SHA,
)

print(
    "Frozen 5.2 exact:",
    sha_5_2
    == EXPECTED_5_2_SHA,
)

print(
    "Candidate files:",
    len(
        candidate_files
    ),
)

print(
    "Production modified:",
    False,
)

print(
    "Architecture frozen:",
    False,
)

print(
    "NEXT:",
    "5.3 Correlation Authority Resolution",
)

print(
    "REPORT:",
    REPORT.name,
)

print("=" * 120)
