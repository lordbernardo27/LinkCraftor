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
    / "runtime_completion_intake_phase_5_4_discovery_scan.txt"
)


FROZEN_5_3 = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.py"
)

FROZEN_5_3_MANIFEST = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.freeze.json"
)

STAGE_RESULT = (
    ROOT
    / "backend/server/coordination/universal_stages/"
      "result_contract.py"
)

EXPECTED_5_3_SHA = (
    "C0D88ECC69680106B6833DF8CB3113FC"
    "9ABD23C1EE8B7D413BA4AAE3375648FA"
)

EXPECTED_5_3_MANIFEST_SHA = (
    "53F2B149EF904CE5692D85F349038CEA"
    "B901E00B06C6C273CA5B74EB31ACE8E5"
)

EXPECTED_STAGE_RESULT_SHA = (
    "B3469B10BB2F8F9372E4336784D09A14"
    "3C78FABE45BF039B61B76F4A2DC33B24"
)


MODULES = (
    "backend.server.coordination.runtime_integration.workflow_job_correlation",
    "backend.server.coordination.universal_stages.result_contract",
    "backend.server.runtime.universal_runtime_registration",
    "backend.server.runtime.universal_jobs.contract",
    "backend.server.runtime.universal_job_submission",
    "backend.server.orchestration.service",
)


SEARCH_ROOTS = (
    ROOT / "backend/server/runtime",
    ROOT / "backend/server/orchestration",
    ROOT / "backend/server/jobs",
    ROOT / "backend/server/coordination",
)


SEARCH_TERMS = (
    "completed",
    "completion",
    "completed_at",
    "result",
    "result_reference",
    "artifact_references",
    "job_id",
    "update_job_status",
    "mark_completed",
    "complete_job",
    "job_completed",
    "record_completion",
    "completion_event",
    "UniversalStageResult",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def sig(obj):
    try:
        return str(
            inspect.signature(obj)
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
    "PHASE 5.4 — RUNTIME COMPLETION INTAKE",
    "DISCOVERY SCAN",
    "=" * 120,
    "",
]


# =========================================================================
# 1. Frozen upstream integrity
# =========================================================================

sha_5_3 = sha256(
    FROZEN_5_3
)

sha_5_3_manifest = sha256(
    FROZEN_5_3_MANIFEST
)

sha_stage_result = sha256(
    STAGE_RESULT
)


report.extend(
    (
        "1. FROZEN UPSTREAM INTEGRITY",
        "=" * 120,
        f"5.3 SHA256: {sha_5_3}",
        (
            "5.3 exact frozen SHA: "
            + str(
                sha_5_3
                == EXPECTED_5_3_SHA
            )
        ),
        (
            "5.3 freeze manifest SHA256: "
            + sha_5_3_manifest
        ),
        (
            "5.3 freeze manifest exact SHA: "
            + str(
                sha_5_3_manifest
                == EXPECTED_5_3_MANIFEST_SHA
            )
        ),
        (
            "StageResult SHA256: "
            + sha_stage_result
        ),
        (
            "StageResult exact SHA: "
            + str(
                sha_stage_result
                == EXPECTED_STAGE_RESULT_SHA
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
            path.relative_to(ROOT)
        )
    )

    report.append(
        "SHA256: "
        + sha256(path)
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

        if node.name.startswith("_"):
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
                + sig(obj)
            )

            if is_dataclass(obj):

                report.append(
                    "  dataclass fields:"
                )

                for item in fields(obj):
                    report.append(
                        "    - "
                        + item.name
                    )

    if not found_class:
        report.append(
            "  NONE"
        )

    # ---------------------------------------------------------------------
    # Completion-related public functions
    # ---------------------------------------------------------------------

    report.append("")
    report.append(
        "COMPLETION-RELATED PUBLIC FUNCTIONS"
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

        if node.name.startswith("_"):
            continue

        block = source_block(
            source,
            node.lineno,
            node.end_lineno,
            pad=0,
        )

        if not any(
            term.lower()
            in (
                node.name
                + "\n"
                + block
            ).lower()
            for term in SEARCH_TERMS
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
    # Completion field counts
    # ---------------------------------------------------------------------

    report.append("")
    report.append(
        "COMPLETION / RESULT FIELD COUNTS"
    )

    for term in (
        "job_id",
        "status",
        "completed",
        "completed_at",
        "result",
        "result_reference",
        "artifact_references",
        "started_at",
        "error_code",
        "error_message",
    ):

        report.append(
            f"  {term}: "
            + str(
                source.count(term)
            )
        )

    report.append("")


# =========================================================================
# 3. Repository completion authority scan
# =========================================================================

report.extend(
    (
        "=" * 120,
        "3. REPOSITORY COMPLETION AUTHORITY CANDIDATES",
        "=" * 120,
        "",
    )
)


candidates = []

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

        lowered = source.lower()

        hits = tuple(
            term
            for term in SEARCH_TERMS
            if term.lower() in lowered
        )

        important_hits = sum(
            1
            for term in (
                "job_id",
                "completed",
                "result",
            )
            if term in lowered
        )

        semantic_completion = any(
            term in lowered
            for term in (
                "complete_job",
                "mark_completed",
                "record_completion",
                "update_job_status",
                "job_completed",
                "completion_event",
            )
        )

        if (
            important_hits >= 2
            or semantic_completion
        ):
            candidates.append(
                (
                    path,
                    hits,
                )
            )


candidates.sort(
    key=lambda item: str(
        item[0]
    )
)


for path, hits in candidates:

    report.append(
        str(
            path.relative_to(ROOT)
        )
    )

    report.append(
        "  matches: "
        + ", ".join(hits)
    )


if not candidates:
    report.append(
        "NONE"
    )


# =========================================================================
# 4. Existing StageResult contract requirements
# =========================================================================

report.extend(
    (
        "",
        "=" * 120,
        "4. UNIVERSAL STAGE RESULT REQUIREMENTS",
        "=" * 120,
        "",
        "Phase 5.4 must determine authoritative Runtime sources for:",
        "  result_id",
        "  workflow_id",
        "  correlation_id",
        "  stage_id",
        "  stage_version",
        "  pipeline_id",
        "  workflow_type",
        "  workspace_id",
        "  execution_target",
        "  job_id",
        "  job_type",
        "  status",
        "  output",
        "  result_reference",
        "  artifact_references",
        "  started_at",
        "  finished_at",
        "  failure_code",
        "  failure_message",
        "  failure_details",
        "  metadata",
        "",
        "For a successful completion, failure fields should remain empty",
        "according to the existing StageResult contract.",
        "",
    )
)


# =========================================================================
# 5. Phase 5.3 correlation usage
# =========================================================================

report.extend(
    (
        "=" * 120,
        "5. PHASE 5.3 CORRELATION INPUT",
        "=" * 120,
        "",
        "Phase 5.4 should resolve:",
        "",
        "  Runtime completion job_id",
        "      -> WorkflowJobCorrelation",
        "",
        "Expected recovered Coordination identity:",
        "  workflow_id",
        "  correlation_id",
        "  stage_id",
        "  stage_version",
        "  workflow_type",
        "  workspace_id",
        "  job_type",
        "  pipeline_id",
        "  runtime_stage",
        "",
        "Phase 5.4 must not create a second correlation authority.",
        "",
    )
)


# =========================================================================
# 6. Completion authority questions
# =========================================================================

report.extend(
    (
        "=" * 120,
        "6. PHASE 5.4 AUTHORITY QUESTIONS",
        "=" * 120,
        "",
        "A. COMPLETION SOURCE",
        "- Which Runtime component first authoritatively marks a job completed?",
        "- Is completion represented by status='completed'?",
        "- Is there a canonical completion record/event/return payload?",
        "",
        "B. RESULT SOURCE",
        "- Where is handler/business output stored?",
        "- Is result inline, referenced, or both?",
        "- Where does result_reference become authoritative?",
        "- Where do artifact_references become authoritative?",
        "",
        "C. TIMESTAMPS",
        "- Which component owns started_at?",
        "- Which component owns completed_at?",
        "- Can Phase 5.4 safely map completed_at -> finished_at?",
        "",
        "D. JOB LOOKUP",
        "- Can Runtime completion be retrieved deterministically by job_id?",
        "- Which store/API is authoritative for the completed job?",
        "",
        "E. STAGE RESULT CONSTRUCTION",
        "- Should Phase 5.4 construct UniversalStageResult directly?",
        "- Which execution_target value should be used?",
        "- How should result_id be generated or derived?",
        "",
        "F. BOUNDARY",
        "- Phase 5.4 must NOT mark Runtime jobs complete.",
        "- Phase 5.4 must NOT update Runtime status.",
        "- Phase 5.4 must NOT execute handlers.",
        "- Phase 5.4 must NOT own persistence.",
        "- Phase 5.4 must NOT process Runtime failures.",
        "",
    )
)


# =========================================================================
# 7. Provisional flow
# =========================================================================

report.extend(
    (
        "=" * 120,
        "7. PROVISIONAL COMPLETION INTAKE FLOW",
        "=" * 120,
        "",
        "Runtime completes canonical job",
        "        ↓",
        "authoritative completed Runtime job/result",
        "        ↓",
        "Phase 5.4 receives completion evidence",
        "        ↓",
        "resolve Phase 5.3 correlation by job_id",
        "        ↓",
        "cross-check Runtime identity",
        "        ↓",
        "construct canonical UniversalStageResult(status=COMPLETED)",
        "        ↓",
        "return to UCF / coordinator",
        "",
        "NOT YET FROZEN.",
        "",
    )
)


# =========================================================================
# 8. Discovery status
# =========================================================================

report.extend(
    (
        "=" * 120,
        "8. DISCOVERY STATUS",
        "=" * 120,
        "",
        "Discovery only.",
        "Production modified: False",
        "Architecture frozen: False",
        "Installation performed: False",
        "Next: 5.4 Completion Authority Resolution",
    )
)


REPORT.write_text(
    "\n".join(report)
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 120)
print("PHASE 5.4 — RUNTIME COMPLETION INTAKE")
print("DISCOVERY SCAN COMPLETE")
print("=" * 120)

print(
    "Frozen 5.3 exact:",
    sha_5_3
    == EXPECTED_5_3_SHA,
)

print(
    "Frozen 5.3 manifest exact:",
    sha_5_3_manifest
    == EXPECTED_5_3_MANIFEST_SHA,
)

print(
    "StageResult exact:",
    sha_stage_result
    == EXPECTED_STAGE_RESULT_SHA,
)

print(
    "Completion candidate files:",
    len(candidates),
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
    "5.4 Completion Authority Resolution",
)

print(
    "REPORT:",
    REPORT.name,
)

print("=" * 120)
