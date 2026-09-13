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
    / "phase_5_1_16_orchestration_termination_discovery.txt"
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

    "5.1.12_suspension_resume": (
        SERVER / "runtime/universal_orchestration/suspension_resume_eligibility.py",
        "476631641C740443FF7B3D1D1D0E9D6D155289BDCAF14526698528432CCF913A",
    ),

    "5.1.13_recovery": (
        SERVER / "runtime/universal_orchestration/recovery.py",
        "4465A7AF795512594023D19E27A175CA060ACD2845BB4530B77FF8D69C40B16F",
    ),

    "5.1.14_persistence": (
        SERVER / "runtime/universal_orchestration/persistence_interface.py",
        "5B7F640250498B4B5320C3702112D163E16B6878C412447623E5C0FF93608CCA",
    ),

    "5.1.15_completion": (
        SERVER / "runtime/universal_orchestration/completion_resolution.py",
        "1311EEBEB9622AF5D4CF6F4D7CB14FF83B169C748A01DDD144A8000301A5CBD4",
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
        canonical.encode(
            "utf-8"
        )
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
# SEARCH CONFIGURATION
# ============================================================

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
    "cancel": re.compile(
        r"\b("
        r"cancel|cancelled|cancellation|cancel_request|"
        r"cancel_requested"
        r")\b",
        re.IGNORECASE,
    ),

    "termination": re.compile(
        r"\b("
        r"terminate|termination|terminated|terminating|"
        r"shutdown|abort|aborted"
        r")\b",
        re.IGNORECASE,
    ),

    "state": re.compile(
        r"\b("
        r"CREATED|ACTIVE|WAITING|SUSPENDED|RECOVERING|"
        r"SUCCEEDED|FAILED|CANCELLED|state transition"
        r")\b",
        re.IGNORECASE,
    ),

    "job_status": re.compile(
        r"\b("
        r"CREATED|QUEUED|SCHEDULED|LEASED|RUNNING|SUSPENDED|"
        r"SUCCEEDED|FAILED|CANCELLED|DEAD_LETTER|EXPIRED"
        r")\b",
        re.IGNORECASE,
    ),

    "progress": re.compile(
        r"\b("
        r"progress_snapshot|possible_effective_job|"
        r"missing_status|in_progress|pending|terminal_job"
        r")\b",
        re.IGNORECASE,
    ),

    "completion": re.compile(
        r"\b("
        r"completion|complete|succeeded|failed|"
        r"deferred_to_termination"
        r")\b",
        re.IGNORECASE,
    ),

    "worker": re.compile(
        r"\b("
        r"worker|interrupt|stop_worker|restart|drain"
        r")\b",
        re.IGNORECASE,
    ),

    "queue": re.compile(
        r"\b("
        r"queue|dequeue|enqueue|purge|remove|claim|requeue"
        r")\b",
        re.IGNORECASE,
    ),

    "lease": re.compile(
        r"\b("
        r"lease|leased|release_lease|revoke|fencing"
        r")\b",
        re.IGNORECASE,
    ),

    "request": re.compile(
        r"\b("
        r"request|requested|reason|actor|initiator|source"
        r")\b",
        re.IGNORECASE,
    ),

    "policy": re.compile(
        r"\b("
        r"policy|force|graceful|immediate|timeout|deadline"
        r")\b",
        re.IGNORECASE,
    ),

    "evidence": re.compile(
        r"\b("
        r"evidence|snapshot|decision|record|reason"
        r")\b",
        re.IGNORECASE,
    ),

    "persistence": re.compile(
        r"\b("
        r"persist|persistence|save|state_store|runtime_state_store"
        r")\b",
        re.IGNORECASE,
    ),

    "idempotency": re.compile(
        r"\b("
        r"idempotent|idempotency|duplicate|already_cancelled|"
        r"already_terminated"
        r")\b",
        re.IGNORECASE,
    ),
}


repo_findings = []
repo_counts = Counter()
repo_file_counts = Counter()

python_files_scanned = 0
errors = []


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

            errors.append(
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
# FOCUSED TARGETS
# ============================================================

FOCUSED_FILES = (
    SERVER / "runtime/universal_jobs/contract.py",

    SERVER / "runtime/universal_orchestration/state_model.py",
    SERVER / "runtime/universal_orchestration/progress_tracking.py",
    SERVER / "runtime/universal_orchestration/completion_resolution.py",
    SERVER / "runtime/universal_orchestration/recovery.py",
    SERVER / "runtime/universal_orchestration/suspension_resume_eligibility.py",
    SERVER / "runtime/universal_orchestration/persistence_interface.py",

    SERVER / "runtime/universal_queue/cancellation.py",
    SERVER / "runtime/universal_queue/dead_letter.py",
    SERVER / "runtime/universal_queue/recovery.py",

    SERVER / "runtime/universal_worker/lifecycle.py",
    SERVER / "runtime/universal_worker/recovery.py",

    SERVER / "runtime/runtime_lifecycle_manager.py",

    SERVER / "coordination/workflow_lifecycle/state_machine.py",
    SERVER / "coordination/workflow_lifecycle/terminal_state_protection.py",
)


focused_results = []


for path in FOCUSED_FILES:

    relative = str(
        path.relative_to(
            ROOT
        )
    )

    if not path.exists():

        focused_results.append(
            (
                relative,
                "OPTIONAL_MISSING",
                [],
            )
        )

        continue

    try:

        source = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )

    except Exception as exc:

        focused_results.append(
            (
                relative,
                "READ_ERROR",
                [
                    repr(exc)
                ],
            )
        )
        continue

    matches = []

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):

        if any(
            pattern.search(
                line
            )
            for pattern
            in PATTERNS.values()
        ):

            matches.append(
                (
                    line_number,
                    line.strip()[:700],
                )
            )

    focused_results.append(
        (
            relative,
            "FOUND",
            matches,
        )
    )


# ============================================================
# REPORT
# ============================================================

out = [
    (
        "PHASE 5.1.16 — UNIVERSAL ORCHESTRATION "
        "CANCELLATION / TERMINATION RESOLUTION READ-ONLY DISCOVERY"
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
        "SECTION 2 — REPOSITORY SUMMARY",
        "-" * 118,
        "",
        f"Python files scanned: {python_files_scanned}",
        f"Files with findings: {len(repo_file_counts)}",
        f"Total findings: {len(repo_findings)}",
        f"Errors / parse issues: {len(errors)}",
        "",
    ]
)


for category in PATTERNS:

    out.append(
        f"{category}: {repo_counts[category]}"
    )


out.extend(
    [
        "",
        "SECTION 3 — HIGHEST-HIT FILES",
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
        "SECTION 4 — FOCUSED CANCELLATION / TERMINATION TARGETS",
        "-" * 118,
        "",
    ]
)


for relative, status, matches in focused_results:

    out.append(
        f"[{status}] {relative}"
    )

    if status == "FOUND":

        if matches:

            for line_number, text in matches[:500]:

                out.append(
                    f"    L{line_number}: {text}"
                )

        else:

            out.append(
                "    NO RELEVANT MATCHES"
            )

    elif matches:

        for item in matches:

            out.append(
                "    "
                + str(item)
            )

    out.append(
        ""
    )


out.extend(
    [
        "",
        "SECTION 5 — REPOSITORY FINDINGS",
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
        for item in repo_findings
        if item[0] == category
    ]

    if not items:

        out.append(
            "NONE"
        )

        continue

    for _, relative, line, text in items[:800]:

        out.append(
            f"{relative}:{line} | {text}"
        )

    if len(items) > 800:

        out.append(
            (
                "... TRUNCATED: "
                + str(
                    len(items) - 800
                )
                + " additional findings"
            )
        )


out.extend(
    [
        "",
        "SECTION 6 — ERRORS / PARSE ISSUES",
        "-" * 118,
        "",
    ]
)


if errors:

    for relative, error in errors:

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
        "SECTION 7 — 5.1.16 ARCHITECTURE QUESTIONS",
        "-" * 118,
        "",

        "1. Does a canonical Phase-5 orchestration termination authority already exist?",
        "2. Does existing queue code already implement job cancellation mechanics?",
        "3. Does existing worker code already implement graceful/forced stop mechanics?",
        "4. Which existing cancellation mechanisms are execution-level and therefore outside 5.1.16?",

        "5. Is CANCELLED already a terminal orchestration state in frozen 5.1.3?",
        "6. Which orchestration states may legally transition to CANCELLED?",
        "7. Which states may not transition to CANCELLED?",
        "8. Should 5.1.16 consume 5.1.3 legality but never perform the transition?",

        "9. Should 5.1.16 consume frozen 5.1.11 progress evidence?",
        "10. Should only possible-effective jobs matter?",
        "11. Should excluded structural work be ignored?",
        "12. Should missing effective status evidence yield UNRESOLVED?",

        "13. Should an existing orchestration state CANCELLED override progress evidence?",
        "14. Should existing SUCCEEDED remain immutable and non-cancellable?",
        "15. Should existing FAILED remain immutable and non-cancellable?",
        "16. Expected: terminal states must never reopen or cross-transition.",

        "17. Is effective CANCELLED job evidence itself sufficient to request orchestration cancellation?",
        "18. Or does it only indicate cancellation has already happened at job level?",
        "19. Should 5.1.15 DEFERRED_TO_TERMINATION map directly into 5.1.16 eligibility?",
        "20. Should 5.1.16 import 5.1.15 completion resolution?",
        "21. Or should it remain independent and consume state + progress directly?",

        "22. Should caller-supplied cancellation intent be required?",
        "23. For example cancellation_requested=True?",
        "24. Without explicit request, should active/running work ever be cancelled just because one job is CANCELLED?",
        "25. Could job-level cancellation be evidence of an external user/system cancellation request?",

        "26. Should cancellation intent be represented as an immutable caller-supplied snapshot?",
        "27. request_id?",
        "28. request_source?",
        "29. reason?",
        "30. force_requested?",
        "31. Or should 5.1.16 remain minimal and only reason about canonical state/progress evidence?",

        "32. What is the distinction between cancellation and termination?",
        "33. Cancellation = desired orchestration outcome?",
        "34. Termination = execution has reached safe stop?",
        "35. Should 5.1.16 distinguish REQUESTED / WAITING / ELIGIBLE / TERMINATED / UNRESOLVED?",

        "36. If effective jobs are RUNNING or LEASED, should cancellation be WAITING rather than immediately ELIGIBLE?",
        "37. If jobs are QUEUED/SCHEDULED/CREATED, can orchestration cancel immediately?",
        "38. If jobs are SUSPENDED, can orchestration cancel immediately?",
        "39. If every effective job is terminal, can orchestration cancel immediately?",

        "40. Should RUNNING/LEASED require worker/lease shutdown confirmation before orchestration enters CANCELLED?",
        "41. If so, does confirmation belong Phase 6 rather than 5.1.16?",
        "42. Should 5.1.16 merely classify that active execution must first quiesce?",

        "43. What should CREATED effective work imply?",
        "44. QUEUED?",
        "45. SCHEDULED?",
        "46. LEASED?",
        "47. RUNNING?",
        "48. SUSPENDED?",
        "49. SUCCEEDED?",
        "50. FAILED?",
        "51. CANCELLED?",
        "52. DEAD_LETTER?",
        "53. EXPIRED?",

        "54. Should existing terminal successful/failed jobs block cancellation of the orchestration?",
        "55. Or can remaining effective work still be cancelled while preserving completed job history?",
        "56. Should cancellation apply to the orchestration lifecycle rather than rewrite job history?",

        "57. Should all effective work need to be CANCELLED before orchestration target becomes CANCELLED?",
        "58. Or is a quiescent mixture of SUCCEEDED/FAILED/CANCELLED/etc enough?",
        "59. Should terminal jobs be treated as already quiescent?",

        "60. Should DEFERRED_TO_TERMINATION from 5.1.15 mean:",
        "61. orchestration MUST become CANCELLED?",
        "62. or only that completion resolver refuses to reinterpret cancellation as failure?",

        "63. Should 5.1.16 expose target_terminal_state=CANCELLED?",
        "64. Should it expose may_transition_to_cancelled using 5.1.3?",
        "65. Should it distinguish target derivation from actual transition?",

        "66. Should cancellation resolution use wall clock? Expected NO.",
        "67. Should it implement grace periods/timeouts? Expected NO.",
        "68. Should forced termination policy belong Phase 6 / reliability layers?",
        "69. Should it inspect worker health? Expected NO.",
        "70. Should it inspect leases directly? Expected NO.",

        "71. Should it cancel queued jobs? Expected NO.",
        "72. Should it purge queue entries? Expected NO.",
        "73. Should it interrupt workers? Expected NO.",
        "74. Should it release leases? Expected NO.",
        "75. Should it revoke leases? Expected NO.",
        "76. Should it call Runtime Lifecycle Manager? Expected NO.",

        "77. Should it mutate UniversalJob.status? Expected NO.",
        "78. Should it transition orchestration state? Expected NO.",
        "79. Should it recompute progress? Expected NO.",
        "80. Should it reevaluate completion? Expected NO.",
        "81. Should it reevaluate recovery? Expected NO.",

        "82. Should it persist? Expected NO.",
        "83. Should it call 5.1.14 persistence port? Expected NO.",
        "84. Should permanent termination evidence belong 5.1.17? Expected YES.",

        "85. Should cancellation decision be deterministic?",
        "86. Should cancellation_decision_id hash identity + state + progress + request evidence?",
        "87. Should same evidence produce same ID?",
        "88. Should changed request intent alter ID?",
        "89. Should changed progress alter ID?",
        "90. Should changed orchestration state alter ID?",

        "91. Exact stored fields?",
        "92. state_snapshot?",
        "93. progress_snapshot?",
        "94. cancellation_request_snapshot?",
        "95. schema_version?",

        "96. Is a cancellation request snapshot necessary to distinguish:",
        "97. ordinary FAILED/CANCELLED job evidence",
        "98. from explicit orchestration-level cancellation intent?",

        "99. If no explicit request exists but orchestration state is already CANCELLED, should resolver return ALREADY_CANCELLED?",
        "100. If no explicit request exists and state is not CANCELLED, should result be NOT_REQUESTED?",

        "101. Should request_source be free text or enum?",
        "102. USER?",
        "103. OWNER?",
        "104. SYSTEM?",
        "105. POLICY?",
        "106. COORDINATOR?",
        "107. Or should source remain opaque caller-supplied metadata to avoid policy invention?",

        "108. Should forced cancellation be represented now?",
        "109. Or deferred entirely because execution semantics do not belong 5.1.16?",

        "110. Should 5.1.16 classify quiescence?",
        "111. QUIESCENT when no possible-effective LEASED/RUNNING work?",
        "112. ACTIVE_EXECUTION when LEASED/RUNNING exists?",
        "113. UNKNOWN when status evidence missing/unresolved?",

        "114. Should QUEUED/SCHEDULED/CREATED count as quiescent for orchestration transition purposes?",
        "115. Or must job cancellation execution happen first before orchestration becomes CANCELLED?",
        "116. This distinction is important because 5.1.16 itself cannot mutate those jobs.",

        "117. Should all nonterminal job states block final CANCELLED transition until execution layer confirms cancellation?",
        "118. Or only LEASED/RUNNING block it?",
        "119. What does existing Queue/Worker architecture imply?",

        "120. What exact semantics preserve separation among:",
        "     cancellation intent,",
        "     job cancellation execution,",
        "     runtime quiescence,",
        "     orchestration CANCELLED state,",
        "     and permanent evidence recording?",

        "",
        (
            "NEXT: analyze discovery and freeze the exact "
            "5.1.16 Orchestration Cancellation / Termination "
            "Resolution boundary before implementation."
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
    "PHASE 5.1.16 ORCHESTRATION CANCELLATION / "
    "TERMINATION RESOLUTION DISCOVERY COMPLETE"
)

print("=" * 100)

print(
    "Python files scanned:",
    python_files_scanned,
)

print(
    "Files with findings:",
    len(
        repo_file_counts
    ),
)

print(
    "Total findings:",
    len(
        repo_findings
    ),
)

print(
    "Errors / parse issues:",
    len(
        errors
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

for category in PATTERNS:

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
