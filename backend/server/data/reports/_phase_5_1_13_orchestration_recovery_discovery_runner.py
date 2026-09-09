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
    / "phase_5_1_13_orchestration_recovery_discovery.txt"
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

    "5.1.11_progress_tracking": (
        SERVER / "runtime/universal_orchestration/progress_tracking.py",
        "92C100E0682F975488F78ED5F0D38CB1F4C6E18F6FEA08D1A8D81BE98A4D8309",
    ),

    "5.1.12_suspension_resume_eligibility": (
        SERVER / "runtime/universal_orchestration/suspension_resume_eligibility.py",
        "476631641C740443FF7B3D1D1D0E9D6D155289BDCAF14526698528432CCF913A",
    ),

    "worker_recovery": (
        SERVER / "runtime/universal_worker/recovery.py",
        "C3EF5DBD81205F0087E05F43F6A67A1E0762930DAAD256F957AABC57296D19A5",
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

    "runtime_shutdown_process": (
        SERVER / "runtime/runtime_shutdown_process.py",
        "7A159E206C73157064B70D15A1CE4A97AB3D77EBBC77B01A2554BC34224EB272",
    ),

    "runtime_lifecycle_manager": (
        SERVER / "runtime/runtime_lifecycle_manager.py",
        "E6200CA0938B5D578954024D6E76E343FB39D9329CFD3ABE4B3AEF86E8204034",
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
# FOCUSED TARGETS
# ============================================================

TARGETS = (
    SERVER / "runtime/universal_jobs/contract.py",

    SERVER / "runtime/universal_worker/recovery.py",
    SERVER / "runtime/universal_worker/stale.py",
    SERVER / "runtime/universal_worker/leasing.py",

    SERVER / "runtime/universal_orchestration/state_model.py",
    SERVER / "runtime/universal_orchestration/dependency_resolution.py",
    SERVER / "runtime/universal_orchestration/execution_planning.py",
    SERVER / "runtime/universal_orchestration/stage_readiness.py",
    SERVER / "runtime/universal_orchestration/runtime_handoff.py",
    SERVER / "runtime/universal_orchestration/conditional_branching.py",
    SERVER / "runtime/universal_orchestration/progress_tracking.py",
    SERVER / "runtime/universal_orchestration/suspension_resume_eligibility.py",

    SERVER / "runtime/runtime_lifecycle_manager.py",
    SERVER / "runtime/runtime_shutdown_process.py",

    SERVER / "runtime/universal_runtime_worker_v1.py",
    SERVER / "runtime/universal_runtime_infrastructure.py",

    SERVER / "orchestration/models.py",
    SERVER / "orchestration/service.py",
    SERVER / "orchestration/queue.py",
    SERVER / "orchestration/job_store.py",

    SERVER / "jobs/universal_knowledge_orchestrator.py",
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
    "venv",
    "node_modules",
}


PATTERNS = {
    "recovery": re.compile(
        r"\b("
        r"recovery|recover|recovering|recovered"
        r")\b",
        re.IGNORECASE,
    ),

    "retry": re.compile(
        r"\b("
        r"retry|retries|retryable|attempt|attempts"
        r")\b",
        re.IGNORECASE,
    ),

    "failure": re.compile(
        r"\b("
        r"failed|failure|dead_letter|expired|error|exception"
        r")\b",
        re.IGNORECASE,
    ),

    "stale": re.compile(
        r"\b("
        r"stale|heartbeat|orphan|abandoned"
        r")\b",
        re.IGNORECASE,
    ),

    "lease": re.compile(
        r"\b("
        r"lease|leased|lease_id|lease_owner|release"
        r")\b",
        re.IGNORECASE,
    ),

    "worker": re.compile(
        r"\b("
        r"worker|worker_id|assignment|capacity|drain"
        r")\b",
        re.IGNORECASE,
    ),

    "queue": re.compile(
        r"\b("
        r"queue|queued|enqueue|dequeue|schedule|claim|dead.?letter"
        r")\b",
        re.IGNORECASE,
    ),

    "state": re.compile(
        r"\b("
        r"RECOVERING|ACTIVE|WAITING|SUSPENDED|SUCCEEDED|FAILED|"
        r"CANCELLED|state transition|orchestration state"
        r")\b",
        re.IGNORECASE,
    ),

    "progress": re.compile(
        r"\b("
        r"progress|terminal_unsuccessful|terminal_job|"
        r"possible_effective|missing_status|unresolved_effective"
        r")\b",
        re.IGNORECASE,
    ),

    "suspension": re.compile(
        r"\b("
        r"suspend|suspended|resume|eligibility"
        r")\b",
        re.IGNORECASE,
    ),

    "checkpoint": re.compile(
        r"\b("
        r"checkpoint|checkpoint_reference|restore|resume_from"
        r")\b",
        re.IGNORECASE,
    ),

    "dependency": re.compile(
        r"\b("
        r"dependency|dependencies|blocked|upstream|downstream"
        r")\b",
        re.IGNORECASE,
    ),

    "persistence": re.compile(
        r"\b("
        r"persist|persistence|state_store|runtime_state_store|"
        r"save|restore"
        r")\b",
        re.IGNORECASE,
    ),

    "completion": re.compile(
        r"\b("
        r"complete|completion|success|terminal"
        r")\b",
        re.IGNORECASE,
    ),

    "cancellation": re.compile(
        r"\b("
        r"cancel|cancelled|termination|terminate"
        r")\b",
        re.IGNORECASE,
    ),

    "evidence": re.compile(
        r"\b("
        r"evidence|decision|reason|cause|snapshot"
        r")\b",
        re.IGNORECASE,
    ),

    "policy": re.compile(
        r"\b("
        r"policy|retry_policy|max_attempts|backoff|budget"
        r")\b",
        re.IGNORECASE,
    ),

    "time": re.compile(
        r"\b("
        r"timeout|deadline|backoff|delay|timestamp|time|duration"
        r")\b",
        re.IGNORECASE,
    ),
}


# ============================================================
# FOCUSED SCAN
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
                    "recover",
                    "retry",
                    "failure",
                    "stale",
                    "lease",
                    "checkpoint",
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
                    "recover",
                    "retry",
                    "failure",
                    "stale",
                    "lease",
                    "checkpoint",
                    "requeue",
                    "restart",
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
                        "recover",
                        "retry",
                        "attempt",
                        "failure",
                        "checkpoint",
                        "lease",
                        "stale",
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
                    "recovery",
                    "worker",
                    "queue",
                    "state_model",
                    "progress_tracking",
                    "runtime_state_store",
                    "checkpoint",
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
# REPOSITORY-WIDE SCAN
# ============================================================

REPO_CATEGORIES = (
    "recovery",
    "retry",
    "failure",
    "stale",
    "lease",
    "worker",
    "queue",
    "state",
    "progress",
    "suspension",
    "checkpoint",
    "dependency",
    "persistence",
    "completion",
    "cancellation",
    "evidence",
    "policy",
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
# SPECIAL SIGNALS
# ============================================================

state_signals = []

state_path = (
    SERVER
    / "runtime"
    / "universal_orchestration"
    / "state_model.py"
)


if state_path.exists():

    source = state_path.read_text(
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
                "RECOVERING",
                "FAILED",
                "ACTIVE",
                "WAITING",
                "SUSPENDED",
                "transition",
                "recovery",
            )
        ):

            state_signals.append(
                (
                    line_number,
                    line.strip()[:600],
                )
            )


worker_recovery_signals = []

worker_recovery_path = (
    SERVER
    / "runtime"
    / "universal_worker"
    / "recovery.py"
)


if worker_recovery_path.exists():

    source = worker_recovery_path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):

        if any(
            token.lower() in line.lower()
            for token in (
                "recover",
                "worker",
                "lease",
                "assignment",
                "stale",
                "job",
                "retry",
            )
        ):

            worker_recovery_signals.append(
                (
                    line_number,
                    line.strip()[:600],
                )
            )


progress_signals = []

progress_path = (
    SERVER
    / "runtime"
    / "universal_orchestration"
    / "progress_tracking.py"
)


if progress_path.exists():

    source = progress_path.read_text(
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
                "terminal_unsuccessful_job_ids",
                "terminal_job_ids",
                "missing_status_job_ids",
                "possible_effective_job_ids",
                "in_progress_job_ids",
                "suspended_job_ids",
                "recovery_boundary",
            )
        ):

            progress_signals.append(
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
        "PHASE 5.1.13 — UNIVERSAL ORCHESTRATION "
        "RECOVERY READ-ONLY DISCOVERY"
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
        "SECTION 7 — RELEVANT FIELDS",
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
        "SECTION 9 — 5.1.3 RECOVERY STATE SIGNALS",
        "-" * 118,
        "",
    ]
)


for line_number, text in state_signals:

    out.append(
        (
            "backend\\server\\runtime\\universal_orchestration\\"
            "state_model.py:"
            + str(line_number)
            + " | "
            + text
        )
    )


out.extend(
    [
        "",
        "SECTION 10 — PHASE 4 WORKER RECOVERY SIGNALS",
        "-" * 118,
        "",
    ]
)


for line_number, text in worker_recovery_signals:

    out.append(
        (
            "backend\\server\\runtime\\universal_worker\\recovery.py:"
            + str(line_number)
            + " | "
            + text
        )
    )


out.extend(
    [
        "",
        "SECTION 11 — 5.1.11 PROGRESS RECOVERY SIGNALS",
        "-" * 118,
        "",
    ]
)


for line_number, text in progress_signals:

    out.append(
        (
            "backend\\server\\runtime\\universal_orchestration\\"
            "progress_tracking.py:"
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
        "SECTION 13 — REPOSITORY-WIDE SUMMARY",
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
        "SECTION 17 — 5.1.13 ARCHITECTURE QUESTIONS",
        "-" * 118,
        "",

        "1. Does a canonical Phase-5 orchestration recovery authority already exist?",
        "2. What existing recovery code is strictly worker-level rather than orchestration-level?",
        "3. Does Phase 4 Worker Recovery recover worker availability only?",
        "4. Does any existing authority already retry/requeue UniversalJobs?",
        "5. Which retry mechanics belong later to Phase 6 Execution Engine?",

        "6. Does 5.1.3 define RECOVERING as an orchestration lifecycle state?",
        "7. Which states may transition to RECOVERING?",
        "8. Which states may follow RECOVERING?",
        "9. Should 5.1.13 consume 5.1.3 state evidence but never transition state itself?",

        "10. Should 5.1.13 consume frozen 5.1.11 progress snapshots?",
        "11. Which effective job states can create a recovery candidate?",
        "12. FAILED?",
        "13. DEAD_LETTER?",
        "14. EXPIRED?",
        "15. CANCELLED?",
        "16. SUSPENDED?",
        "17. Missing status evidence?",
        "18. Contradictory running evidence?",

        "19. Is CANCELLED ever recoverable, or should cancellation remain authoritative under 5.1.16?",
        "20. Is DEAD_LETTER recoverable at orchestration level or only via explicit later retry policy?",
        "21. Is EXPIRED recoverable or must a new attempt/job be created later?",
        "22. Should FAILED be the principal generic recovery candidate?",

        "23. Should 5.1.13 distinguish RECOVERABLE / UNRECOVERABLE / UNRESOLVED / NOT_REQUIRED?",
        "24. Should it identify recovery_candidate_job_ids?",
        "25. Should it identify unrecoverable_job_ids?",
        "26. Should it identify missing_evidence_job_ids?",
        "27. Should excluded jobs be ignored via 5.1.11 possible-effective population?",

        "28. Should recovery eligibility depend on attempt counts?",
        "29. Does UniversalJob currently store attempt_count or retry metadata?",
        "30. If retry policy is absent from frozen contracts, should 5.1.13 avoid inventing one?",
        "31. Should caller-supplied recovery policy evidence be considered?",
        "32. Or should retry-budget mechanics be deferred to Phase 6?",

        "33. Should 5.1.13 ever mutate FAILED → CREATED/QUEUED? Expected NO.",
        "34. Should it requeue a failed job? Expected NO.",
        "35. Should it acquire/release worker leases? Expected NO.",
        "36. Should it restart workers? Expected NO.",
        "37. Should it restore checkpoints? Expected NO.",
        "38. Should it execute handlers? Expected NO.",

        "39. Should 5.1.13 decide whether orchestration MAY ENTER RECOVERING?",
        "40. Should it decide whether a RECOVERING orchestration MAY EXIT recovery?",
        "41. Or should exit-state selection remain 5.1.3 plus later completion logic?",
        "42. Should recovery decision be descriptive rather than perform transition?",

        "43. How should SUSPENDED orchestration interact with recovery?",
        "44. Should 5.1.12 eligibility be an input?",
        "45. Or should recovery stay independent of suspend/resume eligibility?",
        "46. Could a suspended job also be a recovery candidate?",
        "47. Should actual resume/recovery ordering remain a coordinator concern later?",

        "48. Should terminal orchestration states SUCCEEDED/FAILED/CANCELLED be recovery-ineligible?",
        "49. Or can orchestration FAILED be considered for a future retry/recovery attempt?",
        "50. If 5.1.3 marks FAILED terminal, should 5.1.13 respect terminality and not reopen it?",

        "51. Should RECOVERING state mean recovery has been authorized but not executed?",
        "52. Should 5.1.13 only determine recovery eligibility/plan?",
        "53. Does actual retry belong Phase 6?",
        "54. Does orchestration state transition into RECOVERING belong another authority/controller?",

        "55. Should recovery planning identify only affected jobs?",
        "56. Should downstream descendants of failed jobs be included?",
        "57. Or should downstream impact remain dependency/readiness responsibility?",
        "58. Should 5.1.13 avoid recomputing dependency resolution?",

        "59. Should missing status evidence yield UNRESOLVED rather than a recovery guess?",
        "60. Should unresolved branch activity yield UNRESOLVED?",
        "61. Should active RUNNING/LEASED jobs prevent declaring recovery complete?",
        "62. Should partial failures coexist with healthy active jobs?",

        "63. What exact stored fields should recovery decision contain?",
        "64. state_snapshot + progress_snapshot + recovery_evidence + schema_version?",
        "65. Is additional caller-supplied failure evidence needed?",
        "66. Should identity be derived?",

        "67. Should a deterministic recovery_decision_id be generated?",
        "68. Should it hash run identity + state + progress snapshot + normalized recovery evidence?",
        "69. Should identical evidence produce identical decisions?",
        "70. Should changed failed-job population change recovery decision ID?",

        "71. Should recovery reasons be explicit enums?",
        "72. FAILED_EFFECTIVE_WORK?",
        "73. DEAD_LETTER_EFFECTIVE_WORK?",
        "74. EXPIRED_EFFECTIVE_WORK?",
        "75. MISSING_EVIDENCE?",
        "76. NO_RECOVERY_REQUIRED?",
        "77. TERMINAL_ORCHESTRATION?",

        "78. Should 5.1.13 use wall clock/backoff? Expected NO.",
        "79. Should retry delay/backoff remain Phase 6/runtime execution policy?",
        "80. Should max attempts remain outside 5.1.13 unless already frozen elsewhere?",

        "81. Should 5.1.13 access Runtime State Store? Expected NO.",
        "82. Should 5.1.13 persist? Expected NO; 5.1.14.",
        "83. Should it decide final completion? Expected NO; 5.1.15.",
        "84. Should it decide cancellation/termination? Expected NO; 5.1.16.",
        "85. Should it record permanent recovery evidence? Expected NO; 5.1.17.",

        "86. Should it invoke Phase 4 Worker Recovery? Expected NO.",
        "87. Should it invoke queue recovery? Expected NO.",
        "88. Should it invoke runtime lifecycle manager? Expected NO.",
        "89. Should it invoke Universal Coordination Framework? Expected NO.",
        "90. Should it invoke pipeline coordinators? Expected NO.",

        "",
        (
            "NEXT: analyze the discovery and freeze the exact "
            "5.1.13 Orchestration Recovery boundary before implementation."
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
    "PHASE 5.1.13 ORCHESTRATION RECOVERY "
    "DISCOVERY COMPLETE"
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
