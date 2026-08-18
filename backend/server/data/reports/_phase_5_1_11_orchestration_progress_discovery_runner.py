from __future__ import annotations

import ast
import hashlib
import re
from collections import Counter
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

SERVER = (
    ROOT
    / "backend"
    / "server"
)

REPORT_PATH = (
    SERVER
    / "data"
    / "reports"
    / "phase_5_1_11_orchestration_progress_discovery.txt"
)


# ============================================================
# FROZEN AUTHORITIES
# ============================================================

PROTECTED = {
    "5.1.1_contract": (
        SERVER / "runtime/universal_orchestration/contract.py",
        "8CC241284B8AF87809A41134FF0FDEB402D5DE49A117D931920CC17346271FD9",
    ),

    "5.1.2_run_identity": (
        SERVER / "runtime/universal_orchestration/run_identity.py",
        "A582564C7D45D96DAB2D6DAF38E8C63B9EA281251F41B02D12DE17F1D68CAFBC",
    ),

    "5.1.3_state_model": (
        SERVER / "runtime/universal_orchestration/state_model.py",
        "B179C6BEB0A232F0170A2ED540D84239A2235A4F0F91528B530E229B61172610",
    ),

    "5.1.4_dependency_resolution": (
        SERVER / "runtime/universal_orchestration/dependency_resolution.py",
        "CF4CE73A8683BFDA1464730F2079058898B2660275C786FA6EBD0816AE574A8E",
    ),

    "5.1.5_execution_planning": (
        SERVER / "runtime/universal_orchestration/execution_planning.py",
        "78F7945AD5592370C21BF919328D6C29627EF209F37A5E864C0588CD40DC7465",
    ),

    "5.1.6_stage_readiness": (
        SERVER / "runtime/universal_orchestration/stage_readiness.py",
        "9BF16440AD057B1C6A89DD9AEEDEADBE32F711EAE2D4FCD8730EB796BF603D6D",
    ),

    "5.1.7_runtime_handoff": (
        SERVER / "runtime/universal_orchestration/runtime_handoff.py",
        "6878FC6F0F2EF071B11A93D793A0CC80B2C91B676C6B6735A78237D8C7D6CB73",
    ),

    "5.1.8_fan_out": (
        SERVER / "runtime/universal_orchestration/fan_out_coordination.py",
        "D60C8629D2490DC41A8DF43E30F00A1D4851941E65CBD2EBE7EED70B75217916",
    ),

    "5.1.9_fan_in": (
        SERVER / "runtime/universal_orchestration/fan_in_coordination.py",
        "98786AEF5E4DBD804FBE5FE32EEE7CD54907FAC6A9C016B6120851834F6CFA0F",
    ),

    "5.1.10_conditional_branching": (
        SERVER / "runtime/universal_orchestration/conditional_branching.py",
        "3799D3BEFB10C77400B40964EBBCCF598B7576BA9034D1C7F29622D0EC65286F",
    ),

    "job_contract": (
        SERVER / "runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "queue_certification": (
        SERVER / "runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "runtime_registration": (
        SERVER / "runtime/universal_runtime_registration.py",
        "CBFBB0DA1E5D05A040AEC6F60B1251331431956106D90335A8C110FDBCA632E5",
    ),

    "runtime_worker": (
        SERVER / "runtime/universal_runtime_worker_v1.py",
        "6CC4EC122C6B8D1E21AFF8B55CAA786148D7E1FC75D840DAE9240FFB69634D44",
    ),

    "runtime_infrastructure": (
        SERVER / "runtime/universal_runtime_infrastructure.py",
        "EE6590D044C6AA20762F2A37AE86B7FFD3300B62610BC2B1F2657D9334CB311C",
    ),

    "orchestration_models": (
        SERVER / "orchestration/models.py",
        "5C9FE5E4F84FA1C369CB45F74B0CB12B7E730ADA3C7CBC95B4F50EC75DC5E92D",
    ),

    "orchestration_queue": (
        SERVER / "orchestration/queue.py",
        "76F8F7E66578E2B8A4A1FF3BB420B6340A7A1D1D661EB66B7C21987CF3845A97",
    ),

    "orchestration_service": (
        SERVER / "orchestration/service.py",
        "4C31CFC6FFDC9AFA8EA6AD8F43ADBC117F8A6D0193ABF045DBFBA39D6EB799BA",
    ),
}


def ast_sha(
    path: Path,
) -> str:

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source
    )

    canonical = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest().upper()


protected_results = []


for name, (
    path,
    expected,
) in PROTECTED.items():

    if not path.exists():

        protected_results.append(
            (
                name,
                "MISSING",
                expected,
                None,
            )
        )

        continue

    try:

        actual = ast_sha(
            path
        )

    except Exception as exc:

        protected_results.append(
            (
                name,
                "ERROR",
                expected,
                repr(exc),
            )
        )

        continue

    protected_results.append(
        (
            name,
            (
                "PASS"
                if actual == expected
                else "FAIL"
            ),
            expected,
            actual,
        )
    )


# ============================================================
# TARGET FILES
# ============================================================

TARGETS = (
    SERVER / "runtime/universal_jobs/contract.py",

    SERVER / "runtime/universal_orchestration/contract.py",
    SERVER / "runtime/universal_orchestration/run_identity.py",
    SERVER / "runtime/universal_orchestration/state_model.py",
    SERVER / "runtime/universal_orchestration/dependency_resolution.py",
    SERVER / "runtime/universal_orchestration/execution_planning.py",
    SERVER / "runtime/universal_orchestration/stage_readiness.py",
    SERVER / "runtime/universal_orchestration/runtime_handoff.py",
    SERVER / "runtime/universal_orchestration/fan_out_coordination.py",
    SERVER / "runtime/universal_orchestration/fan_in_coordination.py",
    SERVER / "runtime/universal_orchestration/conditional_branching.py",

    SERVER / "runtime/universal_runtime_worker_v1.py",
    SERVER / "runtime/universal_runtime_registration.py",

    SERVER / "orchestration/models.py",
    SERVER / "orchestration/queue.py",
    SERVER / "orchestration/service.py",
    SERVER / "orchestration/job_store.py",
)


SEARCH_ROOTS = (
    SERVER / "runtime",
    SERVER / "orchestration",
    SERVER / "coordination",
    SERVER / "jobs",
    SERVER / "pipelines",
)


SKIP_PARTS = {
    "__pycache__",
    ".git",
    ".venv",
    "node_modules",
    "backup",
    "backups",
}


# ============================================================
# DISCOVERY PATTERNS
# ============================================================

PATTERNS = {
    "progress": re.compile(
        r"\b("
        r"progress|progression|progressed|percent|percentage|"
        r"completion_ratio|completion_percent|progress_ratio"
        r")\b",
        re.IGNORECASE,
    ),

    "counting": re.compile(
        r"\b("
        r"count|total|completed_count|pending_count|active_count|"
        r"terminal_count|remaining_count"
        r")\b",
        re.IGNORECASE,
    ),

    "job_status": re.compile(
        r"\b("
        r"UniversalJobStatus|CREATED|QUEUED|SCHEDULED|LEASED|"
        r"RUNNING|SUSPENDED|SUCCEEDED|FAILED|CANCELLED|"
        r"DEAD_LETTER|EXPIRED"
        r")\b",
        re.IGNORECASE,
    ),

    "terminal": re.compile(
        r"\b("
        r"terminal|terminal_status|terminal statuses|terminal state"
        r")\b",
        re.IGNORECASE,
    ),

    "success_failure": re.compile(
        r"\b("
        r"succeeded|failed|cancelled|dead_letter|expired|"
        r"successful|failure|success"
        r")\b",
        re.IGNORECASE,
    ),

    "branch": re.compile(
        r"\b("
        r"selected|excluded|unresolved|branch|conditional"
        r")\b",
        re.IGNORECASE,
    ),

    "skipped": re.compile(
        r"\b("
        r"skipped|skip"
        r")\b",
        re.IGNORECASE,
    ),

    "active_inactive": re.compile(
        r"\b("
        r"active|inactive|effective|eligible|excluded"
        r")\b",
        re.IGNORECASE,
    ),

    "completion": re.compile(
        r"\b("
        r"complete|completed|completion|finished|done"
        r")\b",
        re.IGNORECASE,
    ),

    "readiness": re.compile(
        r"\b("
        r"ready|waiting|blocked|readiness"
        r")\b",
        re.IGNORECASE,
    ),

    "handoff": re.compile(
        r"\b("
        r"handoff|eligible|deferred|ineligible"
        r")\b",
        re.IGNORECASE,
    ),

    "state": re.compile(
        r"\b("
        r"CREATED|ACTIVE|WAITING|SUSPENDED|RECOVERING|"
        r"SUCCEEDED|FAILED|CANCELLED|orchestration state"
        r")\b",
        re.IGNORECASE,
    ),

    "evidence": re.compile(
        r"\b("
        r"evidence|status_evidence|job_statuses|status_map|snapshot"
        r")\b",
        re.IGNORECASE,
    ),

    "execution_plan": re.compile(
        r"\b("
        r"execution_plan|job_ids|job_count|job_map|"
        r"execution_waves|topological_order"
        r")\b",
        re.IGNORECASE,
    ),

    "persistence": re.compile(
        r"\b("
        r"persist|persistence|state_store|runtime_state_store"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_queue": re.compile(
        r"\b("
        r"queue|worker|lease|dispatch|execute"
        r")\b",
        re.IGNORECASE,
    ),

    "metrics": re.compile(
        r"\b("
        r"metric|metrics|counter|gauge|telemetry|observability"
        r")\b",
        re.IGNORECASE,
    ),
}


# ============================================================
# FOCUSED TARGET SCAN
# ============================================================

target_findings = []

target_counts = Counter()

target_file_counts = Counter()

relevant_classes = []

relevant_functions = []

relevant_fields = []

relevant_imports = []

focused_errors = []


for path in TARGETS:

    relative = str(
        path.relative_to(
            ROOT
        )
    )

    if not path.exists():

        focused_errors.append(
            (
                relative,
                "MISSING",
            )
        )

        continue

    try:

        source = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )

        tree = ast.parse(
            source
        )

    except Exception as exc:

        focused_errors.append(
            (
                relative,
                repr(exc),
            )
        )

        continue

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):

        for category, pattern in PATTERNS.items():

            if pattern.search(
                line
            ):

                target_counts[
                    category
                ] += 1

                target_file_counts[
                    relative
                ] += 1

                target_findings.append(
                    (
                        category,
                        relative,
                        line_number,
                        line.strip()[:600],
                    )
                )

    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.ClassDef,
        ):

            lower = node.name.lower()

            if any(
                token in lower
                for token in (
                    "progress",
                    "completion",
                    "status",
                    "snapshot",
                    "summary",
                    "metric",
                )
            ):

                relevant_classes.append(
                    (
                        relative,
                        node.lineno,
                        node.name,
                    )
                )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):

            lower = node.name.lower()

            if any(
                token in lower
                for token in (
                    "progress",
                    "completion",
                    "status",
                    "count",
                    "summary",
                    "snapshot",
                    "metric",
                )
            ):

                relevant_functions.append(
                    (
                        relative,
                        node.lineno,
                        node.name,
                    )
                )

        elif isinstance(
            node,
            ast.AnnAssign,
        ):

            if isinstance(
                node.target,
                ast.Name,
            ):

                name = node.target.id

                if any(
                    token in name.lower()
                    for token in (
                        "progress",
                        "count",
                        "status",
                        "completed",
                        "remaining",
                        "total",
                        "excluded",
                    )
                ):

                    relevant_fields.append(
                        (
                            relative,
                            node.lineno,
                            name,
                        )
                    )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):

            module = (
                node.module
                or ""
            )

            if any(
                token in module.lower()
                for token in (
                    "conditional_branching",
                    "execution_planning",
                    "state_model",
                    "dependency_resolution",
                    "stage_readiness",
                    "runtime_handoff",
                    "universal_jobs",
                    "queue",
                    "worker",
                )
            ):

                relevant_imports.append(
                    (
                        relative,
                        node.lineno,
                        module,
                    )
                )


# ============================================================
# REPOSITORY-WIDE SEARCH
# ============================================================

REPO_CATEGORIES = (
    "progress",
    "counting",
    "job_status",
    "terminal",
    "branch",
    "skipped",
    "active_inactive",
    "completion",
    "evidence",
    "metrics",
)


repo_findings = []

repo_counts = Counter()

repo_file_counts = Counter()

python_files_scanned = 0

parse_errors = []


for search_root in SEARCH_ROOTS:

    if not search_root.exists():

        continue

    for path in search_root.rglob(
        "*.py"
    ):

        if any(
            part.lower() in SKIP_PARTS
            for part in path.parts
        ):

            continue

        python_files_scanned += 1

        relative = str(
            path.relative_to(
                ROOT
            )
        )

        try:

            source = path.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )

        except Exception as exc:

            parse_errors.append(
                (
                    relative,
                    "READ_ERROR: "
                    + repr(exc),
                )
            )

            continue

        for line_number, line in enumerate(
            source.splitlines(),
            start=1,
        ):

            for category in REPO_CATEGORIES:

                if PATTERNS[
                    category
                ].search(
                    line
                ):

                    repo_counts[
                        category
                    ] += 1

                    repo_file_counts[
                        relative
                    ] += 1

                    repo_findings.append(
                        (
                            category,
                            relative,
                            line_number,
                            line.strip()[:600],
                        )
                    )

        try:

            ast.parse(
                source
            )

        except SyntaxError as exc:

            parse_errors.append(
                (
                    relative,
                    (
                        "SYNTAX_ERROR "
                        f"line={exc.lineno} "
                        f"msg={exc.msg}"
                    ),
                )
            )


# ============================================================
# UNIVERSAL JOB STATUS SIGNALS
# ============================================================

job_status_signals = []

job_contract_path = (
    SERVER
    / "runtime"
    / "universal_jobs"
    / "contract.py"
)


if job_contract_path.exists():

    source = job_contract_path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):

        if any(
            token in line
            for token in (
                "class UniversalJobStatus",
                "CREATED",
                "QUEUED",
                "SCHEDULED",
                "LEASED",
                "RUNNING",
                "SUSPENDED",
                "SUCCEEDED",
                "FAILED",
                "CANCELLED",
                "DEAD_LETTER",
                "EXPIRED",
                "TERMINAL",
                "terminal",
            )
        ):

            job_status_signals.append(
                (
                    line_number,
                    line.strip()[:600],
                )
            )


# ============================================================
# CONDITIONAL BRANCHING SIGNALS
# ============================================================

branch_signals = []

conditional_path = (
    SERVER
    / "runtime"
    / "universal_orchestration"
    / "conditional_branching.py"
)


if conditional_path.exists():

    source = conditional_path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):

        if any(
            token in line
            for token in (
                "SELECTED",
                "EXCLUDED",
                "UNRESOLVED",
                "selected_job_ids",
                "excluded_job_ids",
                "unresolved_job_ids",
                "resolution",
                "progress_boundary",
                "completion_boundary",
            )
        ):

            branch_signals.append(
                (
                    line_number,
                    line.strip()[:600],
                )
            )


# ============================================================
# EXECUTION PLAN SIGNALS
# ============================================================

execution_plan_signals = []

execution_plan_path = (
    SERVER
    / "runtime"
    / "universal_orchestration"
    / "execution_planning.py"
)


if execution_plan_path.exists():

    source = execution_plan_path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):

        if any(
            token in line
            for token in (
                "job_ids",
                "job_count",
                "job_map",
                "dependency_map",
                "dependent_map",
                "root_job_ids",
                "leaf_job_ids",
                "execution_waves",
                "topological_order",
            )
        ):

            execution_plan_signals.append(
                (
                    line_number,
                    line.strip()[:600],
                )
            )


# ============================================================
# REPORT
# ============================================================

out = [
    (
        "PHASE 5.1.11 — UNIVERSAL ORCHESTRATION "
        "PROGRESS TRACKING READ-ONLY DISCOVERY"
    ),
    "=" * 118,
    "",
    "PRODUCTION CODE MODIFIED: NO",
    "",
    "SECTION 1 — FROZEN AUTHORITY PROTECTION",
    "-" * 118,
    "",
]


for name, status, expected, actual in (
    protected_results
):

    out.extend(
        [
            f"{name}: {status}",
            f"    EXPECTED: {expected}",
            f"    ACTUAL:   {actual}",
            "",
        ]
    )


out.extend(
    [
        "",
        "SECTION 2 — FOCUSED TARGETS",
        "-" * 118,
        "",
    ]
)


for path in TARGETS:

    out.append(
        str(
            path.relative_to(
                ROOT
            )
        )
        + (
            " — FOUND"
            if path.exists()
            else " — MISSING"
        )
    )


out.extend(
    [
        "",
        "SECTION 3 — FOCUSED FINDING COUNTS",
        "-" * 118,
        "",
    ]
)


for category in PATTERNS:

    out.append(
        (
            category
            + ": "
            + str(
                target_counts[
                    category
                ]
            )
        )
    )


out.extend(
    [
        "",
        "SECTION 4 — HIGHEST-VALUE FOCUSED FILES",
        "-" * 118,
        "",
    ]
)


for index, (
    filename,
    count,
) in enumerate(
    target_file_counts.most_common(),
    start=1,
):

    out.append(
        f"{index:03d}. hits={count} {filename}"
    )


out.extend(
    [
        "",
        "SECTION 5 — RELEVANT CLASSES",
        "-" * 118,
        "",
    ]
)


if relevant_classes:

    for relative, line, name in sorted(
        relevant_classes
    ):

        out.append(
            f"{relative}:{line} class {name}"
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 6 — RELEVANT FUNCTIONS",
        "-" * 118,
        "",
    ]
)


if relevant_functions:

    for relative, line, name in sorted(
        relevant_functions
    ):

        out.append(
            f"{relative}:{line} {name}()"
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 7 — RELEVANT DECLARED FIELDS",
        "-" * 118,
        "",
    ]
)


if relevant_fields:

    for relative, line, name in sorted(
        relevant_fields
    ):

        out.append(
            f"{relative}:{line} {name}"
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 8 — RELEVANT IMPORTS",
        "-" * 118,
        "",
    ]
)


if relevant_imports:

    for relative, line, module in sorted(
        relevant_imports
    ):

        out.append(
            f"{relative}:{line} -> {module}"
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 9 — UNIVERSAL JOB STATUS SIGNALS",
        "-" * 118,
        "",
    ]
)


for line_number, text in job_status_signals:

    out.append(
        (
            "backend\\server\\runtime\\universal_jobs\\contract.py:"
            + str(line_number)
            + " | "
            + text
        )
    )


out.extend(
    [
        "",
        "SECTION 10 — 5.1.10 BRANCH DECISION SIGNALS",
        "-" * 118,
        "",
    ]
)


for line_number, text in branch_signals:

    out.append(
        (
            "backend\\server\\runtime\\universal_orchestration\\"
            "conditional_branching.py:"
            + str(line_number)
            + " | "
            + text
        )
    )


out.extend(
    [
        "",
        "SECTION 11 — 5.1.5 EXECUTION PLAN SIGNALS",
        "-" * 118,
        "",
    ]
)


for line_number, text in execution_plan_signals:

    out.append(
        (
            "backend\\server\\runtime\\universal_orchestration\\"
            "execution_planning.py:"
            + str(line_number)
            + " | "
            + text
        )
    )


out.extend(
    [
        "",
        "SECTION 12 — FOCUSED FINDINGS",
        "-" * 118,
    ]
)


for category in PATTERNS:

    out.extend(
        [
            "",
            "[" + category.upper() + "]",
            "~" * 118,
        ]
    )

    items = [
        item
        for item in target_findings
        if item[0] == category
    ]

    if not items:

        out.append(
            "NONE"
        )

        continue

    for _, relative, line, text in items:

        out.append(
            f"{relative}:{line} | {text}"
        )


out.extend(
    [
        "",
        "SECTION 13 — REPOSITORY-WIDE SEARCH SUMMARY",
        "-" * 118,
        "",
        (
            "Python files scanned: "
            + str(
                python_files_scanned
            )
        ),
        (
            "Files with findings: "
            + str(
                len(
                    repo_file_counts
                )
            )
        ),
        (
            "Total findings: "
            + str(
                len(
                    repo_findings
                )
            )
        ),
        (
            "Parse / read errors: "
            + str(
                len(
                    parse_errors
                )
            )
        ),
        "",
    ]
)


for category in REPO_CATEGORIES:

    out.append(
        (
            category
            + ": "
            + str(
                repo_counts[
                    category
                ]
            )
        )
    )


out.extend(
    [
        "",
        "SECTION 14 — HIGHEST-VALUE REPOSITORY FILES",
        "-" * 118,
        "",
    ]
)


for index, (
    filename,
    count,
) in enumerate(
    repo_file_counts.most_common(
        150
    ),
    start=1,
):

    out.append(
        f"{index:03d}. hits={count} {filename}"
    )


out.extend(
    [
        "",
        "SECTION 15 — REPOSITORY FINDINGS",
        "-" * 118,
    ]
)


for category in REPO_CATEGORIES:

    out.extend(
        [
            "",
            "[" + category.upper() + "]",
            "~" * 118,
        ]
    )

    items = [
        item
        for item in repo_findings
        if item[0] == category
    ]

    if not items:

        out.append(
            "NONE"
        )

        continue

    for _, relative, line, text in items[:700]:

        out.append(
            f"{relative}:{line} | {text}"
        )

    if len(items) > 700:

        out.append(
            (
                "... TRUNCATED: "
                + str(
                    len(items) - 700
                )
                + " additional findings"
            )
        )


out.extend(
    [
        "",
        "SECTION 16 — ERRORS / PARSE ISSUES",
        "-" * 118,
        "",
    ]
)


combined_errors = (
    focused_errors
    + parse_errors
)


if combined_errors:

    for relative, error in combined_errors:

        out.append(
            f"{relative} | {error}"
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 17 — 5.1.11 ARCHITECTURE QUESTIONS",
        "-" * 118,
        "",

        "1. Does a canonical Universal Runtime Orchestration progress authority already exist?",
        "2. Are existing progress counters pipeline-specific, worker-specific, or operational rather than orchestration-wide?",
        "3. Should frozen 5.1.5 Execution Plan define the complete structural job population?",
        "4. Should one progress snapshot cover exactly one orchestration run identity?",
        "5. Should progress tracking consume caller-supplied current UniversalJob status evidence?",
        "6. Should it read runtime storage itself? Expected NO.",
        "7. Should omitted status evidence be represented explicitly as unknown/missing rather than guessed?",
        "8. Should extraneous status evidence for jobs outside the execution plan reject?",
        "9. Should every known job status be accepted exactly from frozen UniversalJobStatus?",

        "10. Which statuses count as not-started?",
        "11. Should CREATED count as not-started?",
        "12. Should QUEUED/SCHEDULED count as pending?",
        "13. Should LEASED/RUNNING count as in-progress?",
        "14. Should SUSPENDED count as suspended rather than in-progress?",
        "15. Should SUCCEEDED count as terminal successful?",
        "16. Should FAILED/CANCELLED/DEAD_LETTER/EXPIRED count as terminal unsuccessful?",
        "17. Should terminal unsuccessful jobs still count as 'finished work' for progress accounting?",
        "18. Should progress tracking distinguish terminal_count from successful_count?",
        "19. Should a failed job increase structural progress even though it may prevent final orchestration success?",
        "20. Should 5.1.15 later decide success/completion semantics independently?",

        "21. How should 5.1.10 EXCLUDED branches affect denominator accounting?",
        "22. Should excluded jobs be removed from the effective progress denominator?",
        "23. Or should they remain counted as intentionally inactive/resolved work?",
        "24. Should progress expose structural_total_job_count and effective_total_job_count separately?",
        "25. Should excluded_job_count be explicit?",
        "26. Should unresolved conditional branches prevent a fully determined effective denominator?",
        "27. Should 5.1.11 consume zero, one, or many 5.1.10 Conditional Branching decision objects?",
        "28. How should multiple conditional loci be normalized deterministically?",
        "29. Should duplicate conditional decisions for the same source reject?",
        "30. Must all conditional decisions belong to the exact same orchestration identity/execution plan?",

        "31. How should downstream descendants of an EXCLUDED branch behave?",
        "32. Does excluding direct branch B imply all descendants exclusively reachable through B are effectively excluded?",
        "33. What if a descendant is also reachable from a selected branch?",
        "34. Does 5.1.11 need effective active-subgraph reachability calculation?",
        "35. Or should branch exclusion propagation belong to 5.1.10?",
        "36. Since 5.1.10 freezes only direct branch decisions, which stage should compute transitive effective activity?",
        "37. Can static 5.1.9 joins have dependencies from both selected and excluded branches?",
        "38. How should effective progress treat such join targets before completion semantics exist?",

        "39. Should progress expose selected/excluded/unresolved structural counts?",
        "40. Should progress expose status buckets for active jobs only?",
        "41. Should it also expose raw structural status buckets for auditability?",
        "42. Should unknown/missing job-status evidence have its own count?",
        "43. Should progress percentage be withheld when required status evidence is missing?",
        "44. Or can a deterministic percentage still use unknown jobs as incomplete?",
        "45. Should percentage be an integer, Decimal, rational numerator/denominator, or derived float?",
        "46. Should floating-point rounding be avoided in the canonical stored contract?",
        "47. Should canonical progress expose numerator and denominator and derive percentage?",

        "48. What exactly should the progress numerator mean?",
        "49. terminal effective jobs / effective jobs?",
        "50. succeeded effective jobs / effective jobs?",
        "51. started effective jobs / effective jobs?",
        "52. Should there be multiple ratios instead of one overloaded 'progress' ratio?",
        "53. Should we expose terminal_progress_count separately from success_count?",
        "54. Should execution_progress and success outcome remain distinct?",

        "55. Should 5.1.11 classify orchestration as NOT_STARTED / IN_PROGRESS / QUIESCENT / TERMINAL_SEEN?",
        "56. Or should 5.1.11 avoid high-level lifecycle classifications entirely?",
        "57. Should 5.1.3 remain the only orchestration lifecycle state authority?",
        "58. Should 5.1.11 therefore return descriptive counters rather than transition/state decisions?",

        "59. Should 5.1.11 invoke 5.1.3 State Model? Expected NO.",
        "60. Should it invoke 5.1.4 Dependency Resolution? Expected NO.",
        "61. Should it invoke 5.1.6 Readiness? Expected NO.",
        "62. Should it invoke 5.1.7 Handoff? Expected NO.",
        "63. Should it recompute 5.1.8 Fan-Out? Expected NO.",
        "64. Should it recompute 5.1.9 Fan-In? Expected NO.",
        "65. Should it evaluate 5.1.10 conditions? Expected NO; consume frozen decisions only.",

        "66. Should 5.1.11 determine orchestration completion? Expected NO; 5.1.15.",
        "67. Should it determine orchestration failure? Expected NO.",
        "68. Should it cancel jobs? Expected NO.",
        "69. Should it suspend/resume? Expected NO; 5.1.12.",
        "70. Should it initiate recovery? Expected NO; 5.1.13.",
        "71. Should it persist? Expected NO; 5.1.14.",
        "72. Should it emit permanent evidence records? Expected NO; 5.1.17.",

        "73. Should it enqueue/dequeue/claim jobs? Expected NO.",
        "74. Should it assign workers or acquire leases? Expected NO.",
        "75. Should it dispatch or execute jobs? Expected NO.",
        "76. Should it mutate UniversalJob.status? Expected NO.",
        "77. Should it transition orchestration state? Expected NO.",
        "78. Should it access Runtime State Store? Expected NO.",
        "79. Should it use wall clock? Expected NO.",
        "80. Should it perform filesystem/network/database I/O? Expected NO.",

        "81. Should status evidence be canonical immutable tuple sorted by execution-plan job order?",
        "82. Should branch decisions be canonical immutable tuple sorted by source_job_id?",
        "83. What should exact stored fields be?",
        "84. execution_plan + status_evidence + conditional_branching_decisions + schema_version?",
        "85. Or should identity be stored separately? Likely derived from execution_plan.",
        "86. Should all counters and bucket IDs be derived?",

        "87. Should structural_job_ids always remain exactly execution_plan.job_ids?",
        "88. Should effective_job_ids be derived after branch exclusions?",
        "89. Should excluded_effective_job_ids be explicit?",
        "90. Should unresolved_effective_job_ids be explicit?",
        "91. Should active branch descendants require deterministic graph traversal?",
        "92. Should disconnected DAG components remain independently counted?",

        "93. Should progress snapshot ID be deterministic?",
        "94. Should it hash orchestration identity + normalized status evidence + branch-decision IDs?",
        "95. Should identical evidence produce identical snapshot IDs?",
        "96. Should changed job status change the snapshot ID?",
        "97. Should changed conditional decision change the snapshot ID?",

        "98. Should progress ratios use exact integer numerator/denominator pairs?",
        "99. Should zero effective jobs be legal after all branches are excluded?",
        "100. If zero effective jobs is legal, how should progress fraction be represented without division-by-zero?",
        "101. Should zero-effective-work be left to 5.1.15 completion resolution?",
        "102. Should 5.1.11 merely expose effective_total_job_count=0 and avoid declaring complete?",

        "",
        (
            "NEXT: analyze discovery findings and freeze "
            "the exact 5.1.11 Orchestration Progress Tracking "
            "boundary before implementation."
        ),
    ]
)


REPORT_PATH.write_text(
    "\n".join(
        out
    ),
    encoding="utf-8",
)


# ============================================================
# CONSOLE SUMMARY
# ============================================================

print()
print("=" * 100)

print(
    "PHASE 5.1.11 ORCHESTRATION PROGRESS "
    "TRACKING DISCOVERY COMPLETE"
)

print("=" * 100)

print(
    "Focused target files:",
    len(
        TARGETS
    ),
)

print(
    "Python files scanned repo-wide:",
    python_files_scanned,
)

print(
    "Target files with findings:",
    len(
        target_file_counts
    ),
)

print(
    "Repo files with findings:",
    len(
        repo_file_counts
    ),
)

print(
    "Target findings:",
    len(
        target_findings
    ),
)

print(
    "Repo findings:",
    len(
        repo_findings
    ),
)

print(
    "Errors / parse issues:",
    len(
        combined_errors
    ),
)

print(
    "Frozen authority failures:",
    sum(
        1
        for _, status, _, _
        in protected_results
        if status != "PASS"
    ),
)

print()

for category in REPO_CATEGORIES:

    print(
        f"{category}: "
        f"{repo_counts[category]}"
    )

print()

print(
    "STATUS: DISCOVERY ONLY — NO PRODUCTION CODE MODIFIED"
)

print(
    "REPORT:",
    REPORT_PATH,
)
