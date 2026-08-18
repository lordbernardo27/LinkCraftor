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
    / "phase_5_1_5_execution_planning_scan.txt"
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
                repr(
                    exc
                ),
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
    SERVER / "runtime/universal_orchestration/contract.py",
    SERVER / "runtime/universal_orchestration/run_identity.py",
    SERVER / "runtime/universal_orchestration/state_model.py",
    SERVER / "runtime/universal_orchestration/dependency_resolution.py",

    SERVER / "runtime/universal_jobs/contract.py",
    SERVER / "runtime/universal_jobs/lineage.py",
    SERVER / "runtime/universal_jobs/status.py",

    SERVER / "runtime/universal_queue/certification.py",

    SERVER / "runtime/universal_runtime_worker_v1.py",
    SERVER / "runtime/universal_runtime_registration.py",
    SERVER / "runtime/universal_runtime_infrastructure.py",

    SERVER / "orchestration/models.py",
    SERVER / "orchestration/service.py",
    SERVER / "orchestration/queue.py",
    SERVER / "orchestration/job_store.py",

    SERVER / "coordination/universal_workflows/contract.py",
    SERVER / "coordination/universal_stages/contract.py",
    SERVER / "coordination/universal_stages/result_contract.py",
)


# ============================================================
# REPOSITORY-WIDE FOCUSED PYTHON SEARCH ROOTS
# ============================================================

SEARCH_ROOTS = (
    SERVER / "runtime",
    SERVER / "orchestration",
    SERVER / "coordination",
    SERVER / "pipelines",
    SERVER / "jobs",
)


SKIP_PARTS = {
    "__pycache__",
    ".git",
    ".venv",
    "node_modules",
    "backups",
    "backup",
}


# ============================================================
# SEARCH PATTERNS
# ============================================================

PATTERNS = {
    "execution_plan": re.compile(
        r"\b("
        r"execution_plan|execution planning|"
        r"executionplan|planner"
        r")\b",
        re.IGNORECASE,
    ),

    "execution_order": re.compile(
        r"\b("
        r"execution_order|execution order|"
        r"ordered_jobs|ordered_stages|"
        r"ordered_nodes"
        r")\b",
        re.IGNORECASE,
    ),

    "topological": re.compile(
        r"\b("
        r"topological|toposort|topo_sort|"
        r"topological_sort"
        r")\b",
        re.IGNORECASE,
    ),

    "dag": re.compile(
        r"\b("
        r"dag|directed acyclic graph|"
        r"acyclic"
        r")\b",
        re.IGNORECASE,
    ),

    "cycle": re.compile(
        r"\b("
        r"cycle|cycles|cyclic|circular|"
        r"cycle_detect|cycle_detection"
        r")\b",
        re.IGNORECASE,
    ),

    "dependency_graph": re.compile(
        r"\b("
        r"dependency_graph|dependency graph|"
        r"graph_dependencies|dependencies_graph"
        r")\b",
        re.IGNORECASE,
    ),

    "dependency_job_ids": re.compile(
        r"\bdependency_job_ids\b",
        re.IGNORECASE,
    ),

    "parent_job_id": re.compile(
        r"\bparent_job_id\b",
        re.IGNORECASE,
    ),

    "root_nodes": re.compile(
        r"\b("
        r"root_nodes|root_jobs|root_stages|"
        r"roots"
        r")\b",
        re.IGNORECASE,
    ),

    "leaf_nodes": re.compile(
        r"\b("
        r"leaf_nodes|leaf_jobs|leaf_stages|"
        r"leaves"
        r")\b",
        re.IGNORECASE,
    ),

    "in_degree": re.compile(
        r"\b("
        r"indegree|in_degree|in-degree"
        r")\b",
        re.IGNORECASE,
    ),

    "out_degree": re.compile(
        r"\b("
        r"outdegree|out_degree|out-degree"
        r")\b",
        re.IGNORECASE,
    ),

    "adjacency": re.compile(
        r"\b("
        r"adjacency|adjacency_list|adjacency_map"
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

    "wave": re.compile(
        r"\b("
        r"execution_wave|execution_waves|"
        r"wave|waves|level|levels"
        r")\b",
        re.IGNORECASE,
    ),

    "stage_order": re.compile(
        r"\b("
        r"stage_order|stage order|"
        r"job_order|job order"
        r")\b",
        re.IGNORECASE,
    ),

    "scheduler": re.compile(
        r"\b("
        r"scheduler|scheduling|schedule"
        r")\b",
        re.IGNORECASE,
    ),

    "priority": re.compile(
        r"\bpriority\b",
        re.IGNORECASE,
    ),

    "ready": re.compile(
        r"\b("
        r"ready|readiness|eligible"
        r")\b",
        re.IGNORECASE,
    ),

    "blocked": re.compile(
        r"\bblocked\b",
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
        r"worker|lease|assignment"
        r")\b",
        re.IGNORECASE,
    ),

    "dispatch": re.compile(
        r"\b("
        r"dispatch|handler|execute|execution"
        r")\b",
        re.IGNORECASE,
    ),
}


# ============================================================
# SCAN TARGET AUTHORITIES
# ============================================================

target_findings = []

target_counts = Counter()

target_file_counts = Counter()

relevant_classes = []

relevant_functions = []

declared_fields = []

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
                repr(
                    exc
                ),
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

            lower = (
                node.name.lower()
            )

            if any(
                token in lower
                for token in (
                    "plan",
                    "graph",
                    "dependency",
                    "dag",
                    "schedule",
                    "execution",
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

            lower = (
                node.name.lower()
            )

            if any(
                token in lower
                for token in (
                    "plan",
                    "graph",
                    "cycle",
                    "topolog",
                    "order",
                    "dependency",
                    "schedule",
                    "fan",
                    "join",
                    "wave",
                    "level",
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

                name = (
                    node.target.id
                )

                if any(
                    token in name.lower()
                    for token in (
                        "plan",
                        "graph",
                        "order",
                        "dependency",
                        "wave",
                        "level",
                        "root",
                        "leaf",
                    )
                ):

                    declared_fields.append(
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
                    "graph",
                    "plan",
                    "schedule",
                    "dependency",
                    "orchestration",
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
# REPOSITORY-WIDE FOCUSED SEARCH
# ============================================================

repo_findings = []

repo_file_counts = Counter()

repo_counts = Counter()

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
                    + repr(
                        exc
                    ),
                )
            )

            continue

        for line_number, line in enumerate(
            source.splitlines(),
            start=1,
        ):

            matched_categories = []

            for category in (
                "execution_plan",
                "execution_order",
                "topological",
                "dag",
                "cycle",
                "dependency_graph",
                "root_nodes",
                "leaf_nodes",
                "in_degree",
                "out_degree",
                "adjacency",
                "fan_out",
                "fan_in",
                "wave",
                "stage_order",
            ):

                if PATTERNS[
                    category
                ].search(
                    line
                ):

                    matched_categories.append(
                        category
                    )

            if not matched_categories:

                continue

            for category in (
                matched_categories
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
        "PHASE 5.1.5 — EXECUTION PLANNING "
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
        "SECTION 3 — TARGET AUTHORITY FINDING COUNTS",
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
        "SECTION 7 — DECLARED PLANNING / GRAPH FIELDS",
        "-" * 118,
        "",
    ]
)


if declared_fields:

    for relative, line, name in sorted(
        declared_fields
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

    for _, relative, line, text in (
        items
    ):

        out.append(
            f"{relative}:{line} | {text}"
        )


out.extend(
    [
        "",
        "SECTION 10 — REPOSITORY-WIDE EXECUTION-PLANNING SEARCH",
        "-" * 118,
        "",
        (
            "Python files scanned: "
            + str(
                python_files_scanned
            )
        ),
        (
            "Files with focused planning findings: "
            + str(
                len(
                    repo_file_counts
                )
            )
        ),
        (
            "Total focused planning findings: "
            + str(
                len(
                    repo_findings
                )
            )
        ),
        "",
    ]
)


for category in (
    "execution_plan",
    "execution_order",
    "topological",
    "dag",
    "cycle",
    "dependency_graph",
    "root_nodes",
    "leaf_nodes",
    "in_degree",
    "out_degree",
    "adjacency",
    "fan_out",
    "fan_in",
    "wave",
    "stage_order",
):

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
        "SECTION 12 — REPOSITORY PLANNING FINDINGS",
        "-" * 118,
    ]
)


for category in (
    "execution_plan",
    "execution_order",
    "topological",
    "dag",
    "cycle",
    "dependency_graph",
    "root_nodes",
    "leaf_nodes",
    "in_degree",
    "out_degree",
    "adjacency",
    "fan_out",
    "fan_in",
    "wave",
    "stage_order",
):

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

    for _, relative, line, text in (
        items[:500]
    ):

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
                    len(
                        items
                    )
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

    for relative, error in (
        combined_errors
    ):

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
        "SECTION 14 — 5.1.5 ARCHITECTURE QUESTIONS",
        "-" * 118,
        "",
        "1. Does a canonical Runtime Orchestration execution planner already exist?",
        "2. Does any existing authority build a dependency DAG from Universal Jobs?",
        "3. Does any existing authority perform cross-job cycle detection?",
        "4. Does any existing authority perform deterministic topological sorting?",
        "5. Does any existing authority define roots and leaves for a job graph?",
        "6. Does any existing authority compute execution waves / graph levels?",
        "7. Does any existing authority calculate in-degree or adjacency maps?",
        "8. Does Universal Job lineage define graph semantics beyond dependency_job_ids?",
        "9. Does 5.1.4 Dependency Resolution define graph ordering? Expected NO.",
        "10. Does queue priority constitute orchestration execution order? Expected NO.",
        "11. Must queue priority remain separate from dependency topological order?",
        "12. Must worker assignment remain separate from execution planning?",
        "13. Must handler registration remain separate from execution planning?",
        "14. Must actual execution remain Phase 6 responsibility?",
        "15. Should the plan operate only over jobs in identity.contract.job_ids?",
        "16. Must every planned job be supplied as a canonical UniversalJob?",
        "17. Must each supplied job_id exactly match a contract member?",
        "18. Must duplicate job objects be rejected?",
        "19. Must missing contract jobs be rejected or represented as incomplete plan evidence?",
        "20. Should a complete 5.1.5 plan require one UniversalJob for every contract job_id?",
        "21. Must each job workspace_id match the orchestration identity?",
        "22. Must each job pipeline match the orchestration identity?",
        "23. Must every dependency_job_id belong to the same orchestration contract?",
        "24. Should parent_job_id remain irrelevant to graph edges unless also present in dependency_job_ids?",
        "25. Should dependency edges be dependency -> dependent?",
        "26. Should a job with zero dependencies be a root node?",
        "27. Should a job depended on by no other job be a leaf node?",
        "28. Should an isolated job be both root and leaf?",
        "29. Should cycles be rejected as invalid execution plans?",
        "30. Should self-dependency remain impossible because Universal Job already rejects it?",
        "31. Should multi-node cycles still be detected by 5.1.5?",
        "32. Should disconnected acyclic components be allowed in one orchestration plan?",
        "33. Should deterministic lexical job_id ordering break ties between independent nodes?",
        "34. Should priority affect topological ordering? Expected NO unless later explicitly designed.",
        "35. Should created_at affect topological ordering? Expected NO.",
        "36. Should queue order affect execution planning? Expected NO.",
        "37. Should execution waves contain jobs that are structurally parallel?",
        "38. Should wave 0 contain all roots?",
        "39. Should each later wave contain nodes whose dependencies are in earlier waves?",
        "40. Should topological_order flatten the waves deterministically?",
        "41. Should fan-out degree be derived from graph structure?",
        "42. Should fan-in degree be derived from graph structure?",
        "43. Should 5.1.5 coordinate actual fan-out? Expected NO; defer 5.1.8.",
        "44. Should 5.1.5 coordinate actual fan-in/join? Expected NO; defer 5.1.9.",
        "45. Should 5.1.5 evaluate dependency statuses? Expected NO; 5.1.4 owns status evidence.",
        "46. Should 5.1.5 determine READY/BLOCKED? Expected NO; defer 5.1.6.",
        "47. Should 5.1.5 evaluate conditions/branches? Expected NO; defer 5.1.10.",
        "48. Should 5.1.5 transition orchestration state? Expected NO.",
        "49. Should 5.1.5 enqueue jobs? Expected NO.",
        "50. Should 5.1.5 claim jobs? Expected NO.",
        "51. Should 5.1.5 assign workers? Expected NO.",
        "52. Should 5.1.5 acquire worker leases? Expected NO.",
        "53. Should 5.1.5 dispatch handlers? Expected NO.",
        "54. Should 5.1.5 execute jobs? Expected NO.",
        "55. Should 5.1.5 read Runtime State Store? Expected NO.",
        "56. Should 5.1.5 persist plans? Expected NO; persistence belongs 5.1.14.",
        "57. Should 5.1.5 import Universal Coordination Framework? Expected NO.",
        "58. Should 5.1.5 invoke pipeline coordinators? Expected NO.",
        "59. Should the plan be an immutable deterministic object?",
        "60. What exact stored fields should define the plan?",
        "61. Should identity be stored directly?",
        "62. Should canonical jobs be stored directly or only job graph records?",
        "63. Should adjacency/dependency maps be stored or derived?",
        "64. Should topological order be stored or derived?",
        "65. Should execution waves be stored or derived?",
        "66. Should root_job_ids be derived?",
        "67. Should leaf_job_ids be derived?",
        "68. Should edge_count be derived?",
        "69. Should graph width/depth be derived here or deferred?",
        "70. What exact graph semantics should become canonical for 5.1.5?",
        "",
        (
            "NEXT: analyze findings and freeze the exact "
            "5.1.5 Execution Planning boundary "
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
    "PHASE 5.1.5 EXECUTION PLANNING DISCOVERY COMPLETE"
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
    "Repo files with focused planning findings:",
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
    "Repo planning findings:",
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

for category in (
    "execution_plan",
    "execution_order",
    "topological",
    "dag",
    "cycle",
    "dependency_graph",
    "root_nodes",
    "leaf_nodes",
    "in_degree",
    "out_degree",
    "adjacency",
    "fan_out",
    "fan_in",
    "wave",
    "stage_order",
):

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
