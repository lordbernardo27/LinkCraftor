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
    / "phase_5_1_9_fan_in_join_coordination_scan.txt"
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

    "5.1.7_runtime_handoff": (
        ROOT / "backend/server/runtime/universal_orchestration/runtime_handoff.py",
        "6878FC6F0F2EF071B11A93D793A0CC80B2C91B676C6B6735A78237D8C7D6CB73",
    ),

    "5.1.8_fan_out_coordination": (
        ROOT / "backend/server/runtime/universal_orchestration/fan_out_coordination.py",
        "D60C8629D2490DC41A8DF43E30F00A1D4851941E65CBD2EBE7EED70B75217916",
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
# TARGETS
# ============================================================

TARGETS = (
    SERVER / "runtime/universal_orchestration/contract.py",
    SERVER / "runtime/universal_orchestration/run_identity.py",
    SERVER / "runtime/universal_orchestration/state_model.py",
    SERVER / "runtime/universal_orchestration/dependency_resolution.py",
    SERVER / "runtime/universal_orchestration/execution_planning.py",
    SERVER / "runtime/universal_orchestration/stage_readiness.py",
    SERVER / "runtime/universal_orchestration/runtime_handoff.py",
    SERVER / "runtime/universal_orchestration/fan_out_coordination.py",

    SERVER / "runtime/universal_jobs/contract.py",

    SERVER / "runtime/universal_queue/certification.py",

    SERVER / "runtime/universal_worker/assignment.py",
    SERVER / "runtime/universal_worker/leasing.py",

    SERVER / "runtime/universal_runtime_registration.py",
    SERVER / "runtime/universal_runtime_worker_v1.py",

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
    "fan_in": re.compile(
        r"\b("
        r"fan_in|fan-in|fan in|fanin"
        r")\b",
        re.IGNORECASE,
    ),

    "join": re.compile(
        r"\b("
        r"join|joining|joined|join_point|join-point|join point"
        r")\b",
        re.IGNORECASE,
    ),

    "convergence": re.compile(
        r"\b("
        r"converge|convergence|convergent|merge_point|merge-point"
        r")\b",
        re.IGNORECASE,
    ),

    "dependency_map": re.compile(
        r"\b("
        r"dependency_map|dependency_job_ids|dependencies"
        r")\b",
        re.IGNORECASE,
    ),

    "dependent_map": re.compile(
        r"\b("
        r"dependent_map|dependents|dependent_job_ids"
        r")\b",
        re.IGNORECASE,
    ),

    "execution_wave": re.compile(
        r"\b("
        r"execution_wave|execution_waves|wave_count|graph_depth"
        r")\b",
        re.IGNORECASE,
    ),

    "fan_out": re.compile(
        r"\b("
        r"fan_out|fan-out|fan out|fanout"
        r")\b",
        re.IGNORECASE,
    ),

    "readiness": re.compile(
        r"\b("
        r"ready|waiting|blocked|readiness"
        r")\b",
        re.IGNORECASE,
    ),

    "completion": re.compile(
        r"\b("
        r"complete|completed|completion|succeeded|finished"
        r")\b",
        re.IGNORECASE,
    ),

    "terminal": re.compile(
        r"\b("
        r"terminal|failed|cancelled|dead_letter|expired"
        r")\b",
        re.IGNORECASE,
    ),

    "all_dependencies": re.compile(
        r"\b("
        r"all_dependencies_satisfied|all dependencies satisfied|"
        r"dependency_statuses"
        r")\b",
        re.IGNORECASE,
    ),

    "condition": re.compile(
        r"\b("
        r"conditional|condition|branch|branching"
        r")\b",
        re.IGNORECASE,
    ),

    "queue": re.compile(
        r"\b("
        r"queue|queued|enqueue|dequeue|claim"
        r")\b",
        re.IGNORECASE,
    ),

    "worker": re.compile(
        r"\b("
        r"worker|assignment|lease|leased"
        r")\b",
        re.IGNORECASE,
    ),

    "dispatch": re.compile(
        r"\b("
        r"dispatch|handler|execute|execution"
        r")\b",
        re.IGNORECASE,
    ),

    "state": re.compile(
        r"\b("
        r"orchestration_state|transition.*state|state.*transition"
        r")\b",
        re.IGNORECASE,
    ),

    "persistence": re.compile(
        r"\b("
        r"persist|persistence|state_store|runtime_state_store"
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
                    "fanin",
                    "fan_in",
                    "join",
                    "converg",
                    "merge",
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
                    "fanin",
                    "fan_in",
                    "join",
                    "converg",
                    "merge",
                    "dependency",
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
                        "fanin",
                        "fan_in",
                        "join",
                        "converg",
                        "merge",
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
                    "execution_planning",
                    "dependency_resolution",
                    "stage_readiness",
                    "runtime_handoff",
                    "fan_out",
                    "queue",
                    "worker",
                    "coordination",
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
# REPOSITORY-WIDE SEARCH
# ============================================================

repo_categories = (
    "fan_in",
    "join",
    "convergence",
    "dependency_map",
    "all_dependencies",
    "completion",
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
# 5.1.5 STRUCTURAL SIGNALS
# ============================================================

planning_structure = []

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
                "dependency_map",
                "dependent_map",
                "execution_waves",
                "root_job_ids",
                "leaf_job_ids",
                "topological_order",
            )
        ):

            planning_structure.append(
                (
                    line_number,
                    line.strip()[:500],
                )
            )


# ============================================================
# REPORT
# ============================================================

out = [
    (
        "PHASE 5.1.9 — UNIVERSAL ORCHESTRATION "
        "FAN-IN / JOIN COORDINATION READ-ONLY DISCOVERY"
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
        "SECTION 3 — FAN-IN / JOIN FINDING COUNTS",
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
        "SECTION 7 — DECLARED FAN-IN / JOIN FIELDS",
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
        "SECTION 9 — 5.1.5 STRUCTURAL SIGNALS",
        "-" * 118,
        "",
    ]
)


for line, text in planning_structure:

    out.append(
        (
            "backend\\server\\runtime\\"
            "universal_orchestration\\execution_planning.py:"
            + str(line)
            + " | "
            + text
        )
    )


out.extend(
    [
        "",
        "SECTION 10 — FOCUSED FINDINGS",
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
        "SECTION 11 — REPOSITORY-WIDE FAN-IN / JOIN SEARCH",
        "-" * 118,
        "",
        (
            "Python files scanned: "
            + str(
                python_files_scanned
            )
        ),
        (
            "Files with focused findings: "
            + str(
                len(
                    repo_file_counts
                )
            )
        ),
        (
            "Total focused findings: "
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
        f"{category}: {repo_counts[category]}"
    )


out.extend(
    [
        "",
        "SECTION 12 — HIGHEST-VALUE REPOSITORY FILES",
        "-" * 118,
        "",
    ]
)


for index, (
    filename,
    count,
) in enumerate(
    repo_file_counts.most_common(
        120
    ),
    start=1,
):

    out.append(
        f"{index:03d}. hits={count} {filename}"
    )


out.extend(
    [
        "",
        "SECTION 13 — REPOSITORY FINDINGS",
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

    for _, relative, line, text in items[:600]:

        out.append(
            f"{relative}:{line} | {text}"
        )

    if len(items) > 600:

        out.append(
            (
                "... TRUNCATED: "
                + str(
                    len(items) - 600
                )
                + " additional findings"
            )
        )


out.extend(
    [
        "",
        "SECTION 14 — ERRORS / PARSE ISSUES",
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
        "SECTION 15 — 5.1.9 ARCHITECTURE QUESTIONS",
        "-" * 118,
        "",

        "1. Does a canonical Universal Runtime Orchestration fan-in/join authority already exist?",
        "2. Are any existing join implementations pipeline-specific rather than universal?",
        "3. Does frozen 5.1.5 dependency_map already define structural convergence completely?",
        "4. Should a join target be a job with two or more direct dependencies?",
        "5. Should a job with exactly one dependency be classified as NO_JOIN?",
        "6. Should a root job with zero dependencies be classified as NO_JOIN?",
        "7. Should join width equal direct dependency count?",
        "8. Should only direct dependencies define the join, excluding transitive ancestors?",
        "9. Should execution-wave co-membership ever define join membership? Expected NO.",
        "10. Should parent_job_id define join membership? Expected NO.",
        "11. Should batch_id define join membership? Expected NO.",
        "12. Should pipeline_run_id define join membership? Expected NO.",

        "13. Should 5.1.9 consume frozen 5.1.5 Execution Plan directly?",
        "14. Should target_job_id select exactly one convergence locus?",
        "15. Should target_job be derived from execution_plan.job_map?",
        "16. Should target_job_id use 5.1.1 canonical identifier normalization?",
        "17. Must target_job_id belong to the execution plan?",
        "18. Should direct dependency IDs inherit 5.1.5 deterministic ordering?",

        "19. Should structural fan-in exist regardless of current dependency statuses?",
        "20. Should 5.1.9 consume 5.1.4 dependency resolution? Possibly NO for pure structure.",
        "21. Should 5.1.9 consume 5.1.6 Stage Readiness? Expected NO if structural only.",
        "22. Should 5.1.9 consume 5.1.7 Runtime Handoff? Expected NO.",
        "23. Should 5.1.9 consume 5.1.8 Fan-Out objects? Expected NO; both derive independently from 5.1.5.",
        "24. Should structural join detection remain valid if dependencies are RUNNING/FAILED/etc.? Likely YES.",

        "25. Is actual join satisfaction already equivalent to 5.1.4 all_dependencies_satisfied?",
        "26. Would recomputing dependency completion in 5.1.9 duplicate 5.1.4/5.1.6 authority?",
        "27. Should 5.1.9 therefore identify structural join topology only?",
        "28. Should actual progression through a join continue through 5.1.4 → 5.1.6 → 5.1.7?",
        "29. Should 5.1.9 avoid introducing READY/WAITING/BLOCKED classifications?",
        "30. Should classifications therefore be JOIN / NO_JOIN only?",

        "31. Should a convergence target with dependencies A,B,C expose join_width=3?",
        "32. Should direct_dependency_job_ids be immutable tuple?",
        "33. Should direct_dependency_jobs be derived from job_map?",
        "34. Should a deterministic join_group_id be derived?",
        "35. Should join_group_id hash orchestration identity + target_job_id + ordered dependency IDs?",
        "36. Should identical topology in different orchestration runs have different join_group_ids?",
        "37. Should different target jobs have different join_group_ids?",

        "38. Can an internal job be a join point? Expected YES.",
        "39. Can a leaf job be a join point? Expected YES if it has 2+ dependencies.",
        "40. Can a join target later fan out again? Expected YES.",
        "41. Can fan-out and fan-in form a diamond A→B,C→D? Expected YES.",
        "42. Should 5.1.8 and 5.1.9 remain independent structural views of the same DAG?",

        "43. Should conditional branch activation affect structural join membership? Expected NO until 5.1.10.",
        "44. If one branch is conditionally disabled later, does static DAG join membership still remain structural?",
        "45. Should condition-aware effective joins belong to 5.1.10 or later orchestration decision logic?",

        "46. Should UniversalJob.status affect structural join classification? Expected NO.",
        "47. Should priority affect join structure? Expected NO.",
        "48. Should created_at/scheduled_at affect join structure? Expected NO.",
        "49. Should worker health/capability/capacity affect join structure? Expected NO.",
        "50. Should queue/lease state affect join structure? Expected NO.",

        "51. Should 5.1.9 enqueue the join target? Expected NO.",
        "52. Should 5.1.9 schedule the join target? Expected NO.",
        "53. Should 5.1.9 claim the join target? Expected NO.",
        "54. Should 5.1.9 assign a worker? Expected NO.",
        "55. Should 5.1.9 acquire a lease? Expected NO.",
        "56. Should 5.1.9 dispatch a handler? Expected NO.",
        "57. Should 5.1.9 execute the target? Expected NO.",
        "58. Should 5.1.9 wait/block/sleep for dependencies? Expected NO.",
        "59. Should 5.1.9 create threads/processes/tasks? Expected NO.",
        "60. Should 5.1.9 mutate UniversalJob.status? Expected NO.",
        "61. Should 5.1.9 transition orchestration state? Expected NO.",
        "62. Should 5.1.9 persist? Expected NO; 5.1.14.",
        "63. Should 5.1.9 access Runtime State Store? Expected NO.",
        "64. Should 5.1.9 import Universal Coordination Framework? Expected NO.",
        "65. Should 5.1.9 invoke pipeline coordinators? Expected NO.",

        "66. Should stored fields be execution_plan + target_job_id + schema_version?",
        "67. Should identity, target_job, dependency IDs/jobs, join_width, classification and join_group_id all be derived?",
        "68. Should whole-plan join enumeration remain outside the single-target core object?",
        "69. Should one evaluation represent exactly one target join locus?",
        "70. Where exactly is the boundary between structural fan-in and dependency-completion/readiness authority?",

        "",
        (
            "NEXT: analyze findings and freeze the exact "
            "5.1.9 Fan-In / Join Coordination boundary "
            "before implementation."
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
    "PHASE 5.1.9 FAN-IN / JOIN COORDINATION DISCOVERY COMPLETE"
)
print("=" * 100)

print(
    "Focused target files:",
    len(TARGETS),
)

print(
    "Python files scanned repo-wide:",
    python_files_scanned,
)

print(
    "Target files with findings:",
    len(target_file_counts),
)

print(
    "Repo files with focused findings:",
    len(repo_file_counts),
)

print(
    "Target findings:",
    len(target_findings),
)

print(
    "Repo focused findings:",
    len(repo_findings),
)

print(
    "Errors / parse issues:",
    len(combined_errors),
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
