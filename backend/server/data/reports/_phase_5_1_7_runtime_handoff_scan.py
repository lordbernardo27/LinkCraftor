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
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_7_runtime_handoff_scan.txt"
)


# ============================================================
# PROTECTED AUTHORITIES
# ============================================================

PROTECTED = {
    "5.1.1_orchestration_contract": (
        ROOT / "backend/server/runtime/universal_orchestration/contract.py",
        "8CC241284B8AF87809A41134FF0FDEB402D5DE49A117D931920CC17346271FD9",
    ),

    "5.1.2_run_identity": (
        ROOT / "backend/server/runtime/universal_orchestration/run_identity.py",
        "A582564C7D45D96DAB2D6DAF38E8C63B9EA281251F41B02D12DE17F1D68CAFBC",
    ),

    "5.1.3_state_model": (
        ROOT / "backend/server/runtime/universal_orchestration/state_model.py",
        "B179C6BEB0A232F0170A2ED540D84239A2235A4F0F91528B530E229B61172610",
    ),

    "5.1.4_dependency_resolution": (
        ROOT / "backend/server/runtime/universal_orchestration/dependency_resolution.py",
        "CF4CE73A8683BFDA1464730F2079058898B2660275C786FA6EBD0816AE574A8E",
    ),

    "5.1.5_execution_planning": (
        ROOT / "backend/server/runtime/universal_orchestration/execution_planning.py",
        "78F7945AD5592370C21BF919328D6C29627EF209F37A5E864C0588CD40DC7465",
    ),

    "5.1.6_stage_readiness": (
        ROOT / "backend/server/runtime/universal_orchestration/stage_readiness.py",
        "9BF16440AD057B1C6A89DD9AEEDEADBE32F711EAE2D4FCD8730EB796BF603D6D",
    ),

    "worker_registration": (
        ROOT / "backend/server/runtime/universal_worker/registration.py",
        "00F0D6E620E24A7433C880B722E023AF3C2121563F8E18DFA9979E0F06A36D64",
    ),

    "worker_discovery": (
        ROOT / "backend/server/runtime/universal_worker/discovery.py",
        "DFCAB9080982C8D5E099A40C903F7B4140B0860053DB73CB77B30B966788A228",
    ),

    "worker_assignment": (
        ROOT / "backend/server/runtime/universal_worker/assignment.py",
        "609D3077B84C1791262F8ACA6BD268FD40436DF7775ACB3E9E726BCFC9715F56",
    ),

    "worker_leasing": (
        ROOT / "backend/server/runtime/universal_worker/leasing.py",
        "413B8081D7802211D64B7B811299F9A8A2C54DBAEAB0FC537B1603A3BE397932",
    ),

    "worker_health": (
        ROOT / "backend/server/runtime/universal_worker/health.py",
        "DCC43E77BDC12188DFD15044DA4DA41022B3CEF40F9C4ED06371EE66AA4E5F65",
    ),

    "worker_recovery": (
        ROOT / "backend/server/runtime/universal_worker/recovery.py",
        "C3EF5DBD81205F0087E05F43F6A67A1E0762930DAAD256F957AABC57296D19A5",
    ),

    "worker_scaling": (
        ROOT / "backend/server/runtime/universal_worker/scaling.py",
        "8EC818E4EF4CA7DBCADCFCB93FD99BC80AAD4CE8AEBE1CDE63CCC44FA8488FF6",
    ),

    "worker_shutdown": (
        ROOT / "backend/server/runtime/universal_worker/shutdown.py",
        "DB2197CA791988B01C73CE426ED29891C8BD9FE46DFEC1AC5AE79D1D131C34DD",
    ),

    "worker_pool": (
        ROOT / "backend/server/runtime/universal_worker/pool.py",
        "4BA8E641A88A5BB38F78D2B981216765B3327D639EB3BC78E5294C152E84A308",
    ),

    "worker_heartbeat": (
        ROOT / "backend/server/runtime/universal_worker/heartbeat.py",
        "A58BDEE660CA903453DA6D968A2B02FBFBE3920E9BBE6C64BC75A597DB7C11EE",
    ),

    "worker_stale": (
        ROOT / "backend/server/runtime/universal_worker/stale.py",
        "22105ACBF984E26019080E53939617CE14BDF51BF5A9B149BD39E10B6B87B9DD",
    ),

    "worker_drain": (
        ROOT / "backend/server/runtime/universal_worker/drain.py",
        "629AA6B5D9269B3164A1524F3C176B2EA34CB4952A0D32F5E2EE4A7C6984FA78",
    ),

    "worker_capability": (
        ROOT / "backend/server/runtime/universal_worker/capability.py",
        "200A42478283CDAC92965EAF0DEDFAB3FAB8834F5FB734E3A4874F1EE571C51D",
    ),

    "worker_capacity": (
        ROOT / "backend/server/runtime/universal_worker/capacity.py",
        "92A626B59250333885ABF1D81A0AA00759A47359C3B9D25FCD948915521CBF55",
    ),

    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "runtime_registration": (
        ROOT / "backend/server/runtime/universal_runtime_registration.py",
        "CBFBB0DA1E5D05A040AEC6F60B1251331431956106D90335A8C110FDBCA632E5",
    ),

    "runtime_worker": (
        ROOT / "backend/server/runtime/universal_runtime_worker_v1.py",
        "6CC4EC122C6B8D1E21AFF8B55CAA786148D7E1FC75D840DAE9240FFB69634D44",
    ),

    "runtime_infrastructure": (
        ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",
        "EE6590D044C6AA20762F2A37AE86B7FFD3300B62610BC2B1F2657D9334CB311C",
    ),

    "orchestration_models": (
        ROOT / "backend/server/orchestration/models.py",
        "5C9FE5E4F84FA1C369CB45F74B0CB12B7E730ADA3C7CBC95B4F50EC75DC5E92D",
    ),

    "orchestration_queue": (
        ROOT / "backend/server/orchestration/queue.py",
        "76F8F7E66578E2B8A4A1FF3BB420B6340A7A1D1D661EB66B7C21987CF3845A97",
    ),

    "orchestration_service": (
        ROOT / "backend/server/orchestration/service.py",
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
# FOCUSED TARGETS
# ============================================================

TARGETS = (
    SERVER / "runtime/universal_orchestration/contract.py",
    SERVER / "runtime/universal_orchestration/run_identity.py",
    SERVER / "runtime/universal_orchestration/state_model.py",
    SERVER / "runtime/universal_orchestration/dependency_resolution.py",
    SERVER / "runtime/universal_orchestration/execution_planning.py",
    SERVER / "runtime/universal_orchestration/stage_readiness.py",

    SERVER / "runtime/universal_jobs/contract.py",
    SERVER / "runtime/universal_jobs/status.py",
    SERVER / "runtime/universal_jobs/lineage.py",
    SERVER / "runtime/universal_jobs/creation.py",

    SERVER / "runtime/universal_queue/certification.py",

    SERVER / "runtime/universal_worker/registration.py",
    SERVER / "runtime/universal_worker/discovery.py",
    SERVER / "runtime/universal_worker/assignment.py",
    SERVER / "runtime/universal_worker/leasing.py",
    SERVER / "runtime/universal_worker/health.py",
    SERVER / "runtime/universal_worker/capability.py",
    SERVER / "runtime/universal_worker/capacity.py",

    SERVER / "runtime/universal_runtime_registration.py",
    SERVER / "runtime/universal_runtime_worker_v1.py",
    SERVER / "runtime/universal_runtime_infrastructure.py",

    SERVER / "orchestration/models.py",
    SERVER / "orchestration/queue.py",
    SERVER / "orchestration/service.py",
    SERVER / "orchestration/job_store.py",

    SERVER / "coordination/universal_workflows/contract.py",
    SERVER / "coordination/universal_stages/contract.py",
    SERVER / "coordination/universal_stages/result_contract.py",
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
    "backups",
    "backup",
}


PATTERNS = {
    "handoff": re.compile(
        r"\b("
        r"handoff|hand_off|hand-off|"
        r"handover|hand_over|hand-over"
        r")\b",
        re.IGNORECASE,
    ),

    "handoff_eligible": re.compile(
        r"\b("
        r"handoff_eligible|handoff eligibility|"
        r"eligible_for_handoff|can_handoff|"
        r"may_handoff|handoff_allowed"
        r")\b",
        re.IGNORECASE,
    ),

    "admission": re.compile(
        r"\b("
        r"admission|admit|admissible|"
        r"admission_gate"
        r")\b",
        re.IGNORECASE,
    ),

    "submit": re.compile(
        r"\b("
        r"submit|submission|forward|forwarding"
        r")\b",
        re.IGNORECASE,
    ),

    "dispatch": re.compile(
        r"\b("
        r"dispatch|dispatcher|dispatching"
        r")\b",
        re.IGNORECASE,
    ),

    "runtime_registration": re.compile(
        r"\b("
        r"runtime_registration|runtime registry|"
        r"register_runtime_handler|"
        r"registered_runtime_handler"
        r")\b",
        re.IGNORECASE,
    ),

    "handler": re.compile(
        r"\b("
        r"handler|handlers|job_handler|"
        r"runtime_handler"
        r")\b",
        re.IGNORECASE,
    ),

    "execute": re.compile(
        r"\b("
        r"execute|execution|executing|"
        r"run_job|process_job"
        r")\b",
        re.IGNORECASE,
    ),

    "ready": re.compile(
        r"\b("
        r"ready|readiness|is_ready"
        r")\b",
        re.IGNORECASE,
    ),

    "waiting": re.compile(
        r"\b("
        r"waiting|is_waiting"
        r")\b",
        re.IGNORECASE,
    ),

    "blocked": re.compile(
        r"\b("
        r"blocked|is_blocked"
        r")\b",
        re.IGNORECASE,
    ),

    "job_status": re.compile(
        r"\b("
        r"UniversalJobStatus|job_status|"
        r"created|queued|scheduled|leased|running|"
        r"suspended|succeeded|failed|cancelled|"
        r"dead_letter|expired"
        r")\b",
        re.IGNORECASE,
    ),

    "terminal": re.compile(
        r"\b("
        r"terminal|is_terminal"
        r")\b",
        re.IGNORECASE,
    ),

    "queue": re.compile(
        r"\b("
        r"queue|queued|enqueue|dequeue|"
        r"claim|queue_id"
        r")\b",
        re.IGNORECASE,
    ),

    "worker": re.compile(
        r"\b("
        r"worker|workers|assignment|"
        r"worker_id"
        r")\b",
        re.IGNORECASE,
    ),

    "lease": re.compile(
        r"\b("
        r"lease|leased|lease_id|"
        r"lease_owner|acquire_lease"
        r")\b",
        re.IGNORECASE,
    ),

    "capacity": re.compile(
        r"\b("
        r"capacity|available_capacity|"
        r"has_available_capacity"
        r")\b",
        re.IGNORECASE,
    ),

    "capability": re.compile(
        r"\b("
        r"capability|capabilities"
        r")\b",
        re.IGNORECASE,
    ),

    "health": re.compile(
        r"\b("
        r"health|healthy|unhealthy"
        r")\b",
        re.IGNORECASE,
    ),

    "state_transition": re.compile(
        r"\b("
        r"transition.*state|state.*transition|"
        r"orchestration_state"
        r")\b",
        re.IGNORECASE,
    ),

    "runtime_state_store": re.compile(
        r"\b("
        r"runtime_state_store|state store|"
        r"persistence"
        r")\b",
        re.IGNORECASE,
    ),

    "fan_out": re.compile(
        r"\b("
        r"fan_out|fan-out|fan out"
        r")\b",
        re.IGNORECASE,
    ),

    "fan_in": re.compile(
        r"\b("
        r"fan_in|fan-in|fan in|join"
        r")\b",
        re.IGNORECASE,
    ),

    "condition": re.compile(
        r"\b("
        r"conditional|condition|branch"
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

classes = []

functions = []

fields = []

imports = []

errors = []


for path in TARGETS:

    relative = str(
        path.relative_to(
            ROOT
        )
    )

    if not path.exists():

        errors.append(
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

        errors.append(
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
                        line.strip()[:500],
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
                    "handoff",
                    "admission",
                    "dispatch",
                    "bridge",
                    "forward",
                    "submission",
                )
            ):

                classes.append(
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
                    "handoff",
                    "admit",
                    "admission",
                    "dispatch",
                    "forward",
                    "submit",
                    "bridge",
                    "eligible",
                )
            ):

                functions.append(
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
                        "handoff",
                        "admission",
                        "dispatch",
                        "eligible",
                        "forward",
                    )
                ):

                    fields.append(
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
                    "runtime",
                    "queue",
                    "worker",
                    "orchestration",
                    "coordination",
                    "dispatch",
                    "handler",
                )
            ):

                imports.append(
                    (
                        relative,
                        node.lineno,
                        module,
                    )
                )


# ============================================================
# REPOSITORY-WIDE FOCUSED SEARCH
# ============================================================

repo_findings = []

repo_counts = Counter()

repo_file_counts = Counter()

python_files_scanned = 0

parse_errors = []


repo_categories = (
    "handoff",
    "handoff_eligible",
    "admission",
    "submit",
    "dispatch",
    "runtime_registration",
)


for search_root in SEARCH_ROOTS:

    if not search_root.exists():

        continue

    for path in search_root.rglob(
        "*.py"
    ):

        if any(
            part.lower()
            in SKIP_PARTS
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

            for category in repo_categories:

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
                            line.strip()[:500],
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
                        f"SYNTAX_ERROR line={exc.lineno} "
                        f"msg={exc.msg}"
                    ),
                )
            )


# ============================================================
# REPORT
# ============================================================

out = [
    (
        "PHASE 5.1.7 — RUNTIME HANDOFF MANAGEMENT "
        "READ-ONLY DISCOVERY"
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
        "SECTION 2 — FOCUSED TARGET FILES",
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
        "SECTION 3 — HANDOFF FINDING COUNTS",
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
        "SECTION 4 — HIGHEST-VALUE TARGET FILES",
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
        (
            f"{index:03d}. "
            f"hits={count} "
            + filename
        )
    )


out.extend(
    [
        "",
        "SECTION 5 — RELEVANT CLASSES",
        "-" * 118,
        "",
    ]
)


if classes:

    for relative, line, name in sorted(
        classes
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


if functions:

    for relative, line, name in sorted(
        functions
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
        "SECTION 7 — DECLARED HANDOFF / ADMISSION FIELDS",
        "-" * 118,
        "",
    ]
)


if fields:

    for relative, line, name in sorted(
        fields
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


if imports:

    for relative, line, module in sorted(
        imports
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
        "SECTION 9 — FOCUSED TARGET FINDINGS",
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
        "SECTION 10 — REPOSITORY-WIDE HANDOFF / DISPATCH SEARCH",
        "-" * 118,
        "",
        (
            "Python files scanned: "
            + str(
                python_files_scanned
            )
        ),
        (
            "Files with focused handoff findings: "
            + str(
                len(
                    repo_file_counts
                )
            )
        ),
        (
            "Total focused handoff findings: "
            + str(
                len(
                    repo_findings
                )
            )
        ),
        "",
    ]
)


for category in repo_categories:

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
        "SECTION 11 — HIGHEST-VALUE REPOSITORY FILES",
        "-" * 118,
        "",
    ]
)


for index, (
    filename,
    count,
) in enumerate(
    repo_file_counts.most_common(
        100
    ),
    start=1,
):

    out.append(
        (
            f"{index:03d}. "
            f"hits={count} "
            + filename
        )
    )


out.extend(
    [
        "",
        "SECTION 12 — REPOSITORY HANDOFF FINDINGS",
        "-" * 118,
    ]
)


for category in repo_categories:

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

    for _, relative, line, text in items[:500]:

        out.append(
            f"{relative}:{line} | {text}"
        )

    if len(
        items
    ) > 500:

        out.append(
            (
                "... TRUNCATED: "
                + str(
                    len(items)
                    - 500
                )
                + " additional findings"
            )
        )


out.extend(
    [
        "",
        "SECTION 13 — ERRORS / PARSE ISSUES",
        "-" * 118,
        "",
    ]
)


combined_errors = (
    errors
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
        "SECTION 14 — 5.1.7 ARCHITECTURE QUESTIONS",
        "-" * 118,
        "",
        "1. Does a canonical Runtime Orchestration handoff-management authority already exist?",
        "2. Does any existing authority define handoff eligibility separately from actual dispatch?",
        "3. Does any existing handoff function already consume 5.1.6 readiness?",
        "4. Does the current runtime worker directly map jobs into Runtime Registration?",
        "5. Does the current runtime worker both select and execute handlers?",
        "6. Is Runtime Registration already the canonical handler registry?",
        "7. Must 5.1.7 stop before Runtime Registration dispatch?",
        "8. Must 5.1.7 stop before Universal Runtime Worker execution?",
        "9. Should 5.1.7 consume the frozen 5.1.6 Stage Readiness object directly?",
        "10. Should 5.1.7 require readiness classification READY?",
        "11. Should WAITING readiness produce NOT_ELIGIBLE rather than error?",
        "12. Should BLOCKED readiness produce NOT_ELIGIBLE rather than error?",
        "13. Should WAITING and BLOCKED have distinct handoff reasons?",
        "14. Should zero-dependency READY targets be handoff-eligible?",
        "15. Must the 5.1.6 identity remain the authoritative orchestration identity?",
        "16. Must the target UniversalJob be derived from 5.1.6 rather than supplied again?",
        "17. Should 5.1.7 inspect target UniversalJob.status?",
        "18. If yes, which statuses are legitimate handoff subjects?",
        "19. Is CREATED eligible for handoff?",
        "20. Is QUEUED already beyond orchestration handoff?",
        "21. Is SCHEDULED already beyond orchestration handoff?",
        "22. Is LEASED already beyond orchestration handoff?",
        "23. Is RUNNING already beyond orchestration handoff?",
        "24. Is SUSPENDED explicitly deferred to 5.1.12?",
        "25. Are terminal target statuses automatically ineligible for handoff?",
        "26. Should 5.1.7 classify lifecycle-ineligible targets rather than mutate them?",
        "27. Should job status belong to handoff eligibility even though it did not belong to 5.1.6 dependency readiness?",
        "28. Should job priority affect handoff eligibility? Expected NO.",
        "29. Should queue priority affect handoff eligibility? Expected NO.",
        "30. Should created_at affect handoff eligibility? Expected NO.",
        "31. Should scheduled_at affect handoff eligibility here or remain scheduling authority?",
        "32. Should worker health affect handoff eligibility? Expected NO.",
        "33. Should worker capability affect handoff eligibility? Expected NO.",
        "34. Should worker capacity affect handoff eligibility? Expected NO.",
        "35. Should queue capacity/backpressure affect handoff eligibility? Expected NO.",
        "36. Should lease availability affect handoff eligibility? Expected NO.",
        "37. Should Runtime Registration handler existence affect handoff eligibility?",
        "38. If handler existence matters, is that already execution/registration responsibility instead?",
        "39. Should 5.1.7 look up a registered handler? Expected NO unless discovery proves otherwise.",
        "40. Should 5.1.7 produce a declarative handoff decision only?",
        "41. Should the decision vocabulary be ELIGIBLE / INELIGIBLE?",
        "42. Or should it be HANDOFF / HOLD / REJECT?",
        "43. Should handoff reasons be canonical enum values?",
        "44. Should readiness WAITING map to a HOLD-style reason?",
        "45. Should readiness BLOCKED map to a BLOCKED/REJECT-style reason?",
        "46. Should lifecycle-ineligible target status have its own reason?",
        "47. Should 5.1.7 mutate UniversalJob.status? Expected NO.",
        "48. Should 5.1.7 enqueue a job? Expected NO.",
        "49. Should 5.1.7 schedule a job? Expected NO.",
        "50. Should 5.1.7 claim a job? Expected NO.",
        "51. Should 5.1.7 assign a worker? Expected NO.",
        "52. Should 5.1.7 acquire a lease? Expected NO.",
        "53. Should 5.1.7 dispatch a runtime handler? Expected NO.",
        "54. Should 5.1.7 execute a runtime handler? Expected NO.",
        "55. Should 5.1.7 execute a job? Expected NO.",
        "56. Should 5.1.7 transition 5.1.3 orchestration state? Expected NO.",
        "57. Should 5.1.7 coordinate fan-out? Expected NO; 5.1.8.",
        "58. Should 5.1.7 coordinate fan-in? Expected NO; 5.1.9.",
        "59. Should 5.1.7 evaluate conditional branches? Expected NO; 5.1.10.",
        "60. Should 5.1.7 access Runtime State Store? Expected NO.",
        "61. Should 5.1.7 persist handoff decisions? Expected NO; 5.1.14.",
        "62. Should 5.1.7 import Universal Coordination Framework? Expected NO.",
        "63. Should 5.1.7 invoke pipeline coordinators? Expected NO.",
        "64. Should the handoff result be immutable and deterministic?",
        "65. Should it store only stage_readiness + schema_version?",
        "66. Should identity, target_job and job_id remain derived?",
        "67. Should handoff eligibility/classification remain derived?",
        "68. Should handoff reason remain derived?",
        "69. Should no queue/worker/handler identifiers be stored?",
        "70. Where exactly is the boundary between 5.1.7 handoff eligibility and the later actual runtime execution path?",
        "",
        (
            "NEXT: analyze findings and freeze the exact "
            "5.1.7 Runtime Handoff Management boundary "
            "before implementation."
        ),
    ]
)


REPORT_PATH.write_text(
    "\n".join(
        out
    ),
    encoding="utf-8",
)


print()
print("=" * 100)
print(
    "PHASE 5.1.7 RUNTIME HANDOFF DISCOVERY COMPLETE"
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
    "Repo files with focused handoff findings:",
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
    "Repo focused handoff findings:",
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

for category in repo_categories:

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
