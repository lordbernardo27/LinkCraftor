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
    / "phase_5_1_12_suspension_resume_eligibility_discovery.txt"
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
    SERVER / "runtime/universal_orchestration/progress_tracking.py",

    SERVER / "runtime/runtime_lifecycle_manager.py",
    SERVER / "runtime/runtime_shutdown_process.py",
    SERVER / "runtime/universal_runtime_worker_v1.py",
    SERVER / "runtime/universal_runtime_infrastructure.py",
    SERVER / "runtime/universal_runtime_registration.py",

    SERVER / "orchestration/models.py",
    SERVER / "orchestration/service.py",
    SERVER / "orchestration/queue.py",
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


# ============================================================
# SEARCH PATTERNS
# ============================================================

PATTERNS = {
    "suspend": re.compile(
        r"\b("
        r"suspend|suspended|suspension"
        r")\b",
        re.IGNORECASE,
    ),

    "resume": re.compile(
        r"\b("
        r"resume|resumed|resuming|resume_eligible|"
        r"resume eligibility|resume eligibility"
        r")\b",
        re.IGNORECASE,
    ),

    "pause": re.compile(
        r"\b("
        r"pause|paused|pausing|checkpoint"
        r")\b",
        re.IGNORECASE,
    ),

    "state": re.compile(
        r"\b("
        r"CREATED|ACTIVE|WAITING|SUSPENDED|RECOVERING|"
        r"SUCCEEDED|FAILED|CANCELLED|"
        r"orchestration state|state transition"
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

    "progress": re.compile(
        r"\b("
        r"progress|possible_effective|definite_effective|"
        r"unresolved_effective|excluded_effective|"
        r"terminal_progress"
        r")\b",
        re.IGNORECASE,
    ),

    "readiness": re.compile(
        r"\b("
        r"readiness|ready|waiting|blocked"
        r")\b",
        re.IGNORECASE,
    ),

    "handoff": re.compile(
        r"\b("
        r"handoff|eligible|deferred|ineligible"
        r")\b",
        re.IGNORECASE,
    ),

    "terminal": re.compile(
        r"\b("
        r"terminal|succeeded|failed|cancelled|"
        r"dead_letter|expired"
        r")\b",
        re.IGNORECASE,
    ),

    "worker": re.compile(
        r"\b("
        r"worker|heartbeat|drain|shutdown|assignment|capacity"
        r")\b",
        re.IGNORECASE,
    ),

    "queue": re.compile(
        r"\b("
        r"queue|queued|schedule|claim|lease"
        r")\b",
        re.IGNORECASE,
    ),

    "recovery": re.compile(
        r"\b("
        r"recover|recovery|retry|restart"
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
        r"completion|complete|completed|success|failure"
        r")\b",
        re.IGNORECASE,
    ),

    "cancellation": re.compile(
        r"\b("
        r"cancel|cancelled|cancellation|terminate|termination"
        r")\b",
        re.IGNORECASE,
    ),

    "control": re.compile(
        r"\b("
        r"control|command|request|signal|intent|operator"
        r")\b",
        re.IGNORECASE,
    ),

    "time": re.compile(
        r"\b("
        r"timeout|deadline|time|timestamp|wall.?clock|duration"
        r")\b",
        re.IGNORECASE,
    ),

    "evidence": re.compile(
        r"\b("
        r"evidence|snapshot|decision|reason|cause"
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
                    "suspend",
                    "resume",
                    "pause",
                    "checkpoint",
                    "state",
                    "lifecycle",
                    "eligibility",
                    "recovery",
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
                    "suspend",
                    "resume",
                    "pause",
                    "checkpoint",
                    "state",
                    "transition",
                    "lifecycle",
                    "eligible",
                    "recovery",
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
                        "suspend",
                        "resume",
                        "pause",
                        "checkpoint",
                        "state",
                        "status",
                        "eligible",
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
                    "state_model",
                    "progress_tracking",
                    "runtime_handoff",
                    "universal_jobs",
                    "worker",
                    "queue",
                    "shutdown",
                    "lifecycle",
                    "recovery",
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
    "suspend",
    "resume",
    "pause",
    "state",
    "job_status",
    "progress",
    "readiness",
    "handoff",
    "terminal",
    "worker",
    "queue",
    "recovery",
    "persistence",
    "completion",
    "cancellation",
    "control",
    "evidence",
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
# 5.1.3 STATE-MODEL SIGNALS
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
                "SUSPENDED",
                "ACTIVE",
                "WAITING",
                "RECOVERING",
                "SUCCEEDED",
                "FAILED",
                "CANCELLED",
                "transition",
                "resume",
                "suspend",
                "completion",
            )
        ):

            state_signals.append(
                (
                    line_number,
                    line.strip()[:600],
                )
            )


# ============================================================
# 5.1.11 PROGRESS SIGNALS
# ============================================================

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
                "suspended_job_ids",
                "suspended_job_count",
                "in_progress_job_ids",
                "pending_job_ids",
                "not_started_job_ids",
                "terminal_job_ids",
                "missing_status_job_ids",
                "possible_effective_job_ids",
                "unresolved_effective_job_ids",
                "completion_boundary",
                "suspension_boundary",
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
# UNIVERSAL JOB STATUS SIGNALS
# ============================================================

job_status_signals = []

job_path = (
    SERVER
    / "runtime"
    / "universal_jobs"
    / "contract.py"
)


if job_path.exists():

    source = job_path.read_text(
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
                "_TERMINAL_STATUSES",
                "checkpoint",
                "progress",
            )
        ):

            job_status_signals.append(
                (
                    line_number,
                    line.strip()[:600],
                )
            )


# ============================================================
# LIFECYCLE / SHUTDOWN SIGNALS
# ============================================================

lifecycle_signals = []


for path in (
    SERVER / "runtime/runtime_lifecycle_manager.py",
    SERVER / "runtime/runtime_shutdown_process.py",
    SERVER / "runtime/universal_runtime_worker_v1.py",
):

    if not path.exists():

        continue

    relative = str(
        path.relative_to(
            ROOT
        )
    )

    source = path.read_text(
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
                "suspend",
                "resume",
                "pause",
                "drain",
                "shutdown",
                "checkpoint",
                "running",
                "worker",
                "lease",
                "cancel",
                "recover",
            )
        ):

            lifecycle_signals.append(
                (
                    relative,
                    line_number,
                    line.strip()[:600],
                )
            )


# ============================================================
# REPORT
# ============================================================

out = [
    (
        "PHASE 5.1.12 — UNIVERSAL ORCHESTRATION "
        "SUSPENSION & RESUME ELIGIBILITY READ-ONLY DISCOVERY"
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
        "SECTION 9 — 5.1.3 STATE MODEL SIGNALS",
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
        "SECTION 10 — 5.1.11 PROGRESS SIGNALS",
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
        "SECTION 11 — UNIVERSAL JOB STATUS SIGNALS",
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
        "SECTION 12 — RUNTIME LIFECYCLE / SHUTDOWN SIGNALS",
        "-" * 118,
        "",
    ]
)


for relative, line_number, text in lifecycle_signals:

    out.append(
        (
            relative
            + ":"
            + str(line_number)
            + " | "
            + text
        )
    )


out.extend(
    [
        "",
        "SECTION 13 — FOCUSED FINDINGS",
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
        "SECTION 14 — REPOSITORY-WIDE SEARCH SUMMARY",
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
        "SECTION 15 — HIGHEST-VALUE REPOSITORY FILES",
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
        "SECTION 16 — REPOSITORY FINDINGS",
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
        "SECTION 17 — ERRORS / PARSE ISSUES",
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
        "SECTION 18 — 5.1.12 ARCHITECTURE QUESTIONS",
        "-" * 118,
        "",

        "1. Does a canonical Phase-5 suspension/resume eligibility authority already exist?",
        "2. Are existing suspend/resume implementations worker-level, runtime-level, pipeline-specific, or orchestration-wide?",
        "3. Does frozen 5.1.3 State Model already define legal SUSPENDED transitions?",
        "4. Which 5.1.3 source states can legally become SUSPENDED?",
        "5. Which 5.1.3 target states can legally follow SUSPENDED?",
        "6. Should 5.1.12 consume a 5.1.3 state snapshot rather than transition state itself?",
        "7. Should 5.1.12 consume frozen 5.1.11 progress evidence?",
        "8. Should one eligibility decision belong to exactly one orchestration identity?",

        "9. What is SUSPEND_ELIGIBLE?",
        "10. Must the orchestration be non-terminal?",
        "11. Can CREATED orchestration be suspend-eligible before any work begins?",
        "12. Can ACTIVE orchestration be suspend-eligible?",
        "13. Can WAITING orchestration be suspend-eligible?",
        "14. Can RECOVERING orchestration be suspend-eligible?",
        "15. Can an already SUSPENDED orchestration be suspend-eligible again?",
        "16. Can SUCCEEDED/FAILED/CANCELLED ever be suspend-eligible? Expected NO.",

        "17. Should suspend eligibility depend on actual RUNNING jobs?",
        "18. Should it depend on LEASED jobs?",
        "19. Should QUEUED/SCHEDULED jobs block eligibility?",
        "20. Should terminal jobs affect eligibility?",
        "21. Should missing status evidence block a positive eligibility decision?",
        "22. Should unresolved conditional branch activity block suspension?",
        "23. Should excluded jobs be ignored because 5.1.11 already removes them from effective work?",

        "24. Does suspend eligibility mean 'safe to request suspension' or 'suspension already accomplished'?",
        "25. Expected: eligibility only; no worker pause/drain/checkpoint execution.",
        "26. Should active work merely produce SUSPEND_DEFERRED rather than INELIGIBLE?",
        "27. Should terminal orchestration produce SUSPEND_INELIGIBLE?",
        "28. Should missing evidence produce UNRESOLVED rather than a guessed result?",

        "29. What is RESUME_ELIGIBLE?",
        "30. Must orchestration state be exactly SUSPENDED?",
        "31. Should a non-SUSPENDED orchestration ever be resume-eligible? Expected NO.",
        "32. Should resume eligibility require all effective suspended jobs to have resumable evidence?",
        "33. What constitutes resumable evidence at Phase 5?",
        "34. Does UniversalJob checkpoint data belong here? Likely NO.",
        "35. Does checkpoint restoration belong Phase 6 Execution? Expected YES.",
        "36. Should 5.1.12 therefore avoid reading checkpoint payloads entirely?",

        "37. Should resume eligibility depend on terminal jobs?",
        "38. Should terminal jobs simply be irrelevant because they do not resume?",
        "39. Should nonterminal effective jobs with SUSPENDED status support resume eligibility?",
        "40. What if possible-effective jobs are CREATED/QUEUED/SCHEDULED rather than SUSPENDED?",
        "41. Does resume eligibility require every nonterminal effective job to be SUSPENDED?",
        "42. Or only that the orchestration state itself is SUSPENDED?",

        "43. How should unresolved branches affect resume eligibility?",
        "44. Should unresolved possible jobs remain part of the safety population?",
        "45. Should missing status evidence prevent a definitive RESUME_ELIGIBLE result?",
        "46. Should 5.1.11 possible_effective_job_ids be the population authority?",

        "47. Should eligibility use descriptive outcomes instead of booleans?",
        "48. Possible suspension dispositions: ELIGIBLE / DEFERRED / INELIGIBLE / UNRESOLVED?",
        "49. Possible resume dispositions: ELIGIBLE / INELIGIBLE / UNRESOLVED?",
        "50. Is DEFERRED meaningful for resume, or should it remain unresolved/ineligible?",
        "51. Should reason codes be deterministic and explicit?",

        "52. Should eligibility distinguish orchestration-state reason from job-progress reason?",
        "53. Should derived blocking_job_ids be exposed?",
        "54. Should derived missing_status_job_ids be exposed?",
        "55. Should derived running_job_ids / leased_job_ids / suspended_job_ids be exposed?",
        "56. Should branch-unresolved job IDs be exposed?",

        "57. Should 5.1.12 ever call 5.1.3 transition functions? Expected NO.",
        "58. Should it call 5.1.6 readiness? Expected NO.",
        "59. Should it call 5.1.7 runtime handoff? Expected NO.",
        "60. Should it reevaluate 5.1.10 branches? Expected NO.",
        "61. Should it recompute 5.1.11 progress topology? Expected NO; consume snapshot.",
        "62. Should it perform recovery? Expected NO; 5.1.13.",
        "63. Should it persist suspension state? Expected NO; 5.1.14.",
        "64. Should it determine completion? Expected NO; 5.1.15.",
        "65. Should it cancel/terminate orchestration? Expected NO; 5.1.16.",
        "66. Should it record permanent evidence? Expected NO; 5.1.17.",

        "67. Should 5.1.12 enqueue/dequeue jobs? Expected NO.",
        "68. Should it pause queues? Expected NO.",
        "69. Should it drain workers? Expected NO.",
        "70. Should it release/acquire leases? Expected NO.",
        "71. Should it dispatch handlers? Expected NO.",
        "72. Should it execute checkpoint save/restore? Expected NO.",
        "73. Should it mutate UniversalJob.status? Expected NO.",
        "74. Should it mutate UniversalJob.progress/checkpoint? Expected NO.",

        "75. Should it access Runtime State Store? Expected NO.",
        "76. Should it use wall clock or timeouts? Expected NO.",
        "77. Should it perform filesystem/network/database I/O? Expected NO.",
        "78. Should it import Universal Coordination Framework? Expected NO.",
        "79. Should it invoke pipeline coordinators? Expected NO.",

        "80. What should exact stored fields be?",
        "81. progress_snapshot + orchestration_state_snapshot + schema_version?",
        "82. Or separate normalized evidence fields?",
        "83. Should identity be derived from progress_snapshot?",
        "84. Should suspension and resume dispositions both be derived?",

        "85. Should eligibility_decision_id be deterministic?",
        "86. Should it hash orchestration identity + state snapshot + progress snapshot ID?",
        "87. Should same evidence yield same eligibility decision ID?",
        "88. Should changed orchestration state change decision ID?",
        "89. Should changed job status/progress evidence change decision ID?",

        "90. Should terminal orchestration states override every other signal?",
        "91. Should already-SUSPENDED state make suspend decision INELIGIBLE but resume decision evaluable?",
        "92. Should ACTIVE/WAITING states make resume INELIGIBLE?",
        "93. Should RECOVERING be owned entirely by 5.1.13 and therefore not resume-eligible?",
        "94. Should CREATED be resumable? Expected NO.",

        "95. Should suspension eligibility require no effective LEASED/RUNNING jobs?",
        "96. Or can suspension be eligible while work is active because Phase 6 can checkpoint it?",
        "97. Since 5.1.12 cannot guarantee checkpoint capability yet, should active execution result in DEFERRED?",
        "98. Should fully quiescent possible-effective work permit immediate suspend eligibility?",
        "99. Should all-terminal effective work be ineligible because completion/termination authorities should own it?",
        "100. Should zero possible-effective jobs remain non-terminal evidence only and avoid guessing completion?",

        "",
        (
            "NEXT: analyze discovery findings and freeze "
            "the exact 5.1.12 Suspension & Resume Eligibility "
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
    "PHASE 5.1.12 ORCHESTRATION SUSPENSION & RESUME "
    "ELIGIBILITY DISCOVERY COMPLETE"
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
