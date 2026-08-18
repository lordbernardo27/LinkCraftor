from __future__ import annotations

import ast
import hashlib
import re
from collections import Counter
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

SERVER = ROOT / "backend" / "server"

REPORT_PATH = (
    SERVER
    / "data"
    / "reports"
    / "phase_5_1_10_conditional_branching_discovery.txt"
)


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


def ast_sha(path: Path) -> str:

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(source)

    canonical = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest().upper()


protected_results = []


for name, (path, expected) in PROTECTED.items():

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

        actual = ast_sha(path)

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
            "PASS" if actual == expected else "FAIL",
            expected,
            actual,
        )
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


PATTERNS = {
    "condition": re.compile(
        r"\bcondition(?:al|s)?\b",
        re.IGNORECASE,
    ),

    "branch": re.compile(
        r"\bbranch(?:es|ing|ed)?\b",
        re.IGNORECASE,
    ),

    "predicate": re.compile(
        r"\bpredicate\b",
        re.IGNORECASE,
    ),

    "rule": re.compile(
        r"\brule(?:s)?\b",
        re.IGNORECASE,
    ),

    "expression": re.compile(
        r"\bexpression\b",
        re.IGNORECASE,
    ),

    "decision": re.compile(
        r"\bdecision(?:s)?\b",
        re.IGNORECASE,
    ),

    "route": re.compile(
        r"\broute|routing|router\b",
        re.IGNORECASE,
    ),

    "select": re.compile(
        r"\bselect|selected|selection\b",
        re.IGNORECASE,
    ),

    "enable_disable": re.compile(
        r"\benable|enabled|disable|disabled\b",
        re.IGNORECASE,
    ),

    "skip": re.compile(
        r"\bskip|skipped|skipping\b",
        re.IGNORECASE,
    ),

    "dependency": re.compile(
        r"\bdependency|dependencies|dependency_map\b",
        re.IGNORECASE,
    ),

    "fan_out": re.compile(
        r"\bfan[_ -]?out\b",
        re.IGNORECASE,
    ),

    "fan_in": re.compile(
        r"\bfan[_ -]?in|join\b",
        re.IGNORECASE,
    ),

    "readiness": re.compile(
        r"\bready|waiting|blocked|readiness\b",
        re.IGNORECASE,
    ),

    "status": re.compile(
        r"\bstatus|created|queued|running|succeeded|failed|cancelled\b",
        re.IGNORECASE,
    ),

    "metadata": re.compile(
        r"\bmetadata\b",
        re.IGNORECASE,
    ),

    "payload": re.compile(
        r"\bpayload\b",
        re.IGNORECASE,
    ),

    "context": re.compile(
        r"\bcontext\b",
        re.IGNORECASE,
    ),

    "queue_worker": re.compile(
        r"\bqueue|worker|lease|dispatch|execute\b",
        re.IGNORECASE,
    ),

    "persistence": re.compile(
        r"\bpersist|persistence|state_store\b",
        re.IGNORECASE,
    ),
}


repo_findings = []

repo_counts = Counter()

repo_file_counts = Counter()

python_files_scanned = 0

parse_errors = []


for search_root in SEARCH_ROOTS:

    if not search_root.exists():

        continue

    for path in search_root.rglob("*.py"):

        if any(
            part.lower() in SKIP_PARTS
            for part in path.parts
        ):
            continue

        python_files_scanned += 1

        relative = str(
            path.relative_to(ROOT)
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

            for category, pattern in PATTERNS.items():

                if pattern.search(line):

                    repo_counts[category] += 1

                    repo_file_counts[relative] += 1

                    repo_findings.append(
                        (
                            category,
                            relative,
                            line_number,
                            line.strip()[:500],
                        )
                    )

        try:

            ast.parse(source)

        except SyntaxError as exc:

            parse_errors.append(
                (
                    relative,
                    (
                        f"SYNTAX_ERROR "
                        f"line={exc.lineno} "
                        f"msg={exc.msg}"
                    ),
                )
            )


focused_candidates = []


for relative, count in repo_file_counts.most_common(150):

    lowered = relative.lower()

    if any(
        token in lowered
        for token in (
            "condition",
            "branch",
            "workflow",
            "stage",
            "coordinator",
            "orchestration",
            "runtime",
            "router",
            "routing",
        )
    ):

        focused_candidates.append(
            (
                relative,
                count,
            )
        )


out = [
    (
        "PHASE 5.1.10 — UNIVERSAL ORCHESTRATION "
        "CONDITIONAL BRANCHING READ-ONLY DISCOVERY"
    ),
    "=" * 118,
    "",
    "PRODUCTION CODE MODIFIED: NO",
    "",
    "SECTION 1 — FROZEN AUTHORITY PROTECTION",
    "-" * 118,
    "",
]


for name, status, expected, actual in protected_results:

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
        f"Errors / parse issues: {len(parse_errors)}",
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
        "SECTION 3 — HIGHEST-VALUE FILES",
        "-" * 118,
        "",
    ]
)


for index, (
    filename,
    count,
) in enumerate(
    repo_file_counts.most_common(150),
    start=1,
):

    out.append(
        f"{index:03d}. hits={count} {filename}"
    )


out.extend(
    [
        "",
        "SECTION 4 — FOCUSED CONDITIONAL / BRANCHING CANDIDATES",
        "-" * 118,
        "",
    ]
)


if focused_candidates:

    for index, (
        filename,
        count,
    ) in enumerate(
        focused_candidates,
        start=1,
    ):

        out.append(
            f"{index:03d}. hits={count} {filename}"
        )

else:

    out.append("NONE")


out.extend(
    [
        "",
        "SECTION 5 — CATEGORY FINDINGS",
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

        out.append("NONE")
        continue

    for _, relative, line, text in items[:700]:

        out.append(
            f"{relative}:{line} | {text}"
        )

    if len(items) > 700:

        out.append(
            (
                "... TRUNCATED: "
                + str(len(items) - 700)
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


if parse_errors:

    for relative, error in parse_errors:

        out.append(
            f"{relative} | {error}"
        )

else:

    out.append("NONE")


out.extend(
    [
        "",
        "SECTION 7 — 5.1.10 ARCHITECTURE QUESTIONS",
        "-" * 118,
        "",

        "1. Does a canonical Universal Runtime Orchestration conditional branching authority already exist?",
        "2. Are existing conditions pipeline-specific, workflow-specific, or universal?",
        "3. Where are branch predicates currently represented, if anywhere?",
        "4. Are branch predicates stored on UniversalJob, workflow definitions, stage definitions, metadata, payload, or nowhere?",
        "5. Should 5.1.10 consume caller-supplied condition evidence rather than reading arbitrary payload/state?",
        "6. Should conditions be declarative rather than executable Python callbacks?",
        "7. Should arbitrary eval/exec expressions be forbidden?",
        "8. Should 5.1.10 define branch outcome only and never execute a branch?",
        "9. Should a condition classification distinguish SELECTED / NOT_SELECTED / UNRESOLVED?",
        "10. Is UNRESOLVED necessary when required condition evidence is absent?",
        "11. Should UNKNOWN and false remain distinct?",
        "12. Should terminal-failure evidence affect branch selection or remain outside 5.1.10?",

        "13. Should 5.1.10 consume frozen 5.1.5 Execution Plan?",
        "14. Should it consume frozen 5.1.8 Fan-Out structure?",
        "15. Should it consume frozen 5.1.9 Join structure?",
        "16. Or should it evaluate a condition independently for one candidate edge/branch?",
        "17. Does a conditional branch select downstream jobs or dependency edges?",
        "18. Should branch selection be source-job scoped?",
        "19. Should one source be allowed multiple mutually-exclusive branch candidates?",
        "20. Should multiple branches be simultaneously selected?",
        "21. Do we need ANY / ALL / FIRST_MATCH semantics?",
        "22. Is exclusive-choice branching distinct from multi-select conditional fan-out?",

        "23. Should branch conditions inspect UniversalJob.status? Likely NO unless caller evidence explicitly represents status.",
        "24. Should branch conditions inspect payload directly? Likely NO.",
        "25. Should branch conditions inspect metadata directly? Likely NO.",
        "26. Should filesystem/network/database lookups be forbidden?",
        "27. Should wall-clock-dependent conditions be forbidden at this layer unless caller supplies normalized evidence?",
        "28. Should caller-supplied evidence be immutable and deterministic?",
        "29. Should evidence key/value types be narrowly constrained?",

        "30. Should 5.1.10 change the frozen 5.1.5 DAG? Expected NO.",
        "31. Should it produce an effective selected-subgraph view instead?",
        "32. Should unselected branches remain structurally present in the original DAG?",
        "33. How should a later join behave when one upstream branch was not selected?",
        "34. Should effective join semantics be derived from branch decisions rather than changing static 5.1.9 membership?",
        "35. Does that require 5.1.10 to expose selected and excluded downstream IDs?",
        "36. Should 5.1.10 itself mark excluded jobs SKIPPED? Expected NO.",
        "37. Is SKIPPED even a UniversalJobStatus? Verify.",
        "38. If SKIPPED is absent, branch exclusion must remain orchestration decision evidence, not job mutation.",

        "39. Should 5.1.10 call 5.1.6 readiness? Expected NO.",
        "40. Should it call 5.1.7 handoff? Expected NO.",
        "41. Should it enqueue selected branches? Expected NO.",
        "42. Should it cancel excluded branches? Expected NO.",
        "43. Should it mutate job status? Expected NO.",
        "44. Should it transition orchestration state? Expected NO.",
        "45. Should it persist decisions? Expected NO; 5.1.14.",
        "46. Should it record evidence permanently? Expected NO; 5.1.17.",

        "47. Should one evaluation represent exactly one branch decision locus?",
        "48. What should stored fields be?",
        "49. Should condition evidence be stored in the immutable decision object?",
        "50. Should selected/excluded branch IDs be derived?",
        "51. Should a deterministic branch_decision_id be derived?",
        "52. Should branch_decision_id include orchestration identity + source + condition definition + normalized evidence?",
        "53. Should branch order be lexical or explicitly declared?",
        "54. Should branch rules have stable IDs?",

        "55. Should branch operators be limited to equality/comparison/membership/boolean composition?",
        "56. Should nested boolean groups be allowed?",
        "57. Should regex conditions be allowed?",
        "58. Should callable predicates be forbidden?",
        "59. Should arbitrary module imports be forbidden?",
        "60. Should condition evaluation be side-effect free?",

        "61. What exact relationship exists between 5.1.10 and later 5.1.11 Progress Tracking?",
        "62. What exact relationship exists between 5.1.10 and 5.1.15 Completion Resolution?",
        "63. How will completion know that unselected branches are intentionally excluded rather than unfinished?",
        "64. Does 5.1.10 need an explicit EXCLUDED branch classification to support later completion?",
        "65. Should branch decisions be declarative evidence consumed later by progress/completion authorities?",

        "",
        (
            "NEXT: analyze discovery and freeze the exact "
            "5.1.10 Conditional Branching boundary before implementation."
        ),
    ]
)


REPORT_PATH.write_text(
    "\n".join(out),
    encoding="utf-8",
)


print()
print("=" * 100)
print(
    "PHASE 5.1.10 CONDITIONAL BRANCHING DISCOVERY COMPLETE"
)
print("=" * 100)

print(
    "Python files scanned:",
    python_files_scanned,
)

print(
    "Files with findings:",
    len(repo_file_counts),
)

print(
    "Total findings:",
    len(repo_findings),
)

print(
    "Errors / parse issues:",
    len(parse_errors),
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
