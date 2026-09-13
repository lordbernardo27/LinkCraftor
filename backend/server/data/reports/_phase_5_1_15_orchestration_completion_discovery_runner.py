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
    / "phase_5_1_15_orchestration_completion_discovery.txt"
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

    "job_contract": (
        SERVER / "runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
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
)


SKIP_PARTS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
}


PATTERNS = {
    "completion": re.compile(
        r"\b("
        r"completion|complete|completed|completion_resolution"
        r")\b",
        re.IGNORECASE,
    ),

    "success": re.compile(
        r"\b("
        r"succeeded|success|successful"
        r")\b",
        re.IGNORECASE,
    ),

    "failure": re.compile(
        r"\b("
        r"failed|failure|dead_letter|expired"
        r")\b",
        re.IGNORECASE,
    ),

    "terminal": re.compile(
        r"\b("
        r"terminal|terminal_state|terminal_job|terminal_success|"
        r"terminal_unsuccessful"
        r")\b",
        re.IGNORECASE,
    ),

    "cancel": re.compile(
        r"\b("
        r"cancel|cancelled|cancellation|termination|terminate"
        r")\b",
        re.IGNORECASE,
    ),

    "progress": re.compile(
        r"\b("
        r"progress_snapshot|possible_effective_job|terminal_job|"
        r"missing_status|unresolved_effective|in_progress|pending"
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

    "recovery": re.compile(
        r"\b("
        r"recovery|recoverable|unrecoverable|unresolved"
        r")\b",
        re.IGNORECASE,
    ),

    "branch": re.compile(
        r"\b("
        r"conditional|branch|excluded_effective|possible_effective"
        r")\b",
        re.IGNORECASE,
    ),

    "missing": re.compile(
        r"\b("
        r"missing|unknown|unresolved"
        r")\b",
        re.IGNORECASE,
    ),

    "status": re.compile(
        r"\b("
        r"CREATED|QUEUED|SCHEDULED|LEASED|RUNNING|SUSPENDED|"
        r"SUCCEEDED|FAILED|CANCELLED|DEAD_LETTER|EXPIRED"
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
# FOCUSED SIGNALS
# ============================================================

FOCUSED_FILES = (
    SERVER / "runtime/universal_jobs/contract.py",
    SERVER / "runtime/universal_orchestration/state_model.py",
    SERVER / "runtime/universal_orchestration/progress_tracking.py",
    SERVER / "runtime/universal_orchestration/recovery.py",
    SERVER / "runtime/universal_orchestration/persistence_interface.py",
    SERVER / "runtime/universal_orchestration/fan_in_coordination.py",
    SERVER / "runtime/universal_orchestration/conditional_branching.py",
)


focused = []


for path in FOCUSED_FILES:

    relative = str(
        path.relative_to(
            ROOT
        )
    )

    if not path.exists():

        focused.append(
            (
                relative,
                0,
                "MISSING",
            )
        )
        continue

    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

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

            focused.append(
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
        "PHASE 5.1.15 — UNIVERSAL ORCHESTRATION "
        "COMPLETION RESOLUTION READ-ONLY DISCOVERY"
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
        "SECTION 4 — FOCUSED COMPLETION SIGNALS",
        "-" * 118,
        "",
    ]
)


for relative, line, text in focused:

    out.append(
        f"{relative}:{line} | {text}"
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
        "SECTION 7 — 5.1.15 ARCHITECTURE QUESTIONS",
        "-" * 118,
        "",

        "1. Does any canonical Phase-5 completion resolver already exist?",
        "2. Does any legacy orchestration code already decide success/failure?",
        "3. Which legacy completion logic must not become 5.1.15 authority?",

        "4. Should frozen 5.1.11 progress be the principal completion evidence?",
        "5. Should possible_effective_job_ids define the completion population?",
        "6. Should excluded branch work be ignored?",
        "7. Should structural-but-excluded jobs block completion? Expected NO.",

        "8. Is completion possible while any effective job is CREATED?",
        "9. QUEUED?",
        "10. SCHEDULED?",
        "11. LEASED?",
        "12. RUNNING?",
        "13. SUSPENDED?",
        "14. Expected NO for all nonterminal effective work.",

        "15. Should missing status evidence yield UNRESOLVED?",
        "16. Should unresolved conditional branch activity yield UNRESOLVED?",
        "17. Should completion ever guess around incomplete evidence? Expected NO.",

        "18. If every possible-effective job is SUCCEEDED, should outcome be SUCCEEDED?",
        "19. What about zero possible-effective jobs?",
        "20. Can an empty effective population be considered completed successfully?",
        "21. Or should it be NOT_READY / UNRESOLVED?",

        "22. If any effective FAILED job remains, should completion outcome be FAILED?",
        "23. If any effective DEAD_LETTER job remains, FAILED?",
        "24. If any effective EXPIRED job remains, FAILED?",
        "25. Should 5.1.13 recovery disposition affect this?",
        "26. If FAILED is RECOVERABLE, should completion wait rather than resolve FAILED?",
        "27. Should completion resolve failure only when recovery is impossible/exhausted?",
        "28. Or should job terminal failure always mean orchestration failure once all work terminal?",

        "29. How should CANCELLED effective jobs be handled?",
        "30. Should CANCELLED imply orchestration cancellation rather than failure?",
        "31. If so, should 5.1.15 defer all cancellation semantics to 5.1.16?",
        "32. Should completion return NOT_APPLICABLE / BLOCKED when cancellation is present?",

        "33. Should mixed SUCCEEDED + FAILED terminal work resolve FAILED?",
        "34. SUCCEEDED + DEAD_LETTER?",
        "35. SUCCEEDED + EXPIRED?",
        "36. SUCCEEDED + CANCELLED?",
        "37. What precedence should terminal outcomes use?",

        "38. Should completion distinguish:",
        "39. NOT_READY",
        "40. SUCCEEDED",
        "41. FAILED",
        "42. UNRESOLVED",
        "43. DEFERRED_TO_TERMINATION?",
        "44. Or another exact enum?",

        "45. Should frozen terminal orchestration states override progress evidence?",
        "46. If state is already SUCCEEDED, should resolver return SUCCEEDED regardless of stale job evidence?",
        "47. If state is already FAILED, should resolver return FAILED?",
        "48. If state is CANCELLED, should 5.1.15 defer to 5.1.16 rather than reinterpret it?",

        "49. Should 5.1.15 determine a target terminal state but never perform transition?",
        "50. Should target state be 5.1.3 SUCCEEDED or FAILED only?",
        "51. Should CANCELLED target be prohibited because 5.1.16 owns cancellation?",

        "52. Should 5.1.15 call transition_universal_orchestration_state? Expected NO.",
        "53. Should it persist? Expected NO.",
        "54. Should it call 5.1.14? Expected NO.",
        "55. Should it record audit evidence? Expected NO; 5.1.17.",

        "56. Should 5.1.15 import 5.1.13 recovery?",
        "57. Is recovery evidence necessary to know whether FAILED work is final?",
        "58. Or should 5.1.15 consume only state + progress and remain independent?",
        "59. Could importing recovery create undesirable coupling?",

        "60. Should a RECOVERING orchestration be completion-eligible?",
        "61. If all effective jobs become SUCCEEDED during RECOVERING, should completion resolve SUCCEEDED?",
        "62. If failed work remains during RECOVERING, should resolution remain NOT_READY rather than FAILED?",

        "63. Should a SUSPENDED orchestration be completion-eligible if every effective job is terminal?",
        "64. Or should suspension itself block completion resolution?",

        "65. Should WAITING state block successful completion?",
        "66. If all effective jobs are terminal-success, should current nonterminal orchestration state matter?",
        "67. Or should state only constrain whether transition is legal?",

        "68. Should 5.1.15 expose may_transition_to_target using 5.1.3 legality?",
        "69. Similar to 5.1.13 may_enter_recovering?",
        "70. Should it distinguish resolution from transition legality?",

        "71. Should completion_decision_id be deterministic?",
        "72. Should it hash identity + state + progress_snapshot_id?",
        "73. Should same evidence produce same ID?",
        "74. Should state change alter ID?",
        "75. Should progress change alter ID?",

        "76. Exact stored fields?",
        "77. state_snapshot?",
        "78. progress_snapshot?",
        "79. schema_version?",
        "80. Everything else derived?",

        "81. Should 5.1.15 use wall clock? Expected NO.",
        "82. Should it inspect retry attempts? Probably NO.",
        "83. Should it inspect retry policy? Probably NO.",
        "84. Should it access queue/worker/leases? Expected NO.",
        "85. Should it execute jobs? Expected NO.",

        "86. Should it recompute branches? Expected NO.",
        "87. Should it recompute progress? Expected NO.",
        "88. Should it recompute recovery? Expected NO.",
        "89. Should it access persistence backend? Expected NO.",

        "90. What exact completion semantics preserve strict separation among:",
        "    5.1.13 recovery,",
        "    5.1.15 completion,",
        "    5.1.16 cancellation/termination,",
        "    and actual 5.1.3 state transition?",

        "",
        (
            "NEXT: analyze discovery and freeze the exact "
            "5.1.15 Orchestration Completion Resolution boundary "
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
    "PHASE 5.1.15 ORCHESTRATION COMPLETION "
    "RESOLUTION DISCOVERY COMPLETE"
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
