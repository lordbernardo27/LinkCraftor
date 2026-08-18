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
    / "phase_5_1_8_fan_out_coordination_scan.txt"
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
    SERVER / "runtime/universal_orchestration/runtime_handoff.py",

    SERVER / "runtime/universal_jobs/contract.py",
    SERVER / "runtime/universal_jobs/status.py",
    SERVER / "runtime/universal_jobs/lineage.py",

    SERVER / "runtime/universal_queue/certification.py",
    SERVER / "runtime/universal_queue/scheduling.py",
    SERVER / "runtime/universal_queue/prioritization.py",
    SERVER / "runtime/universal_queue/routing.py",
    SERVER / "runtime/universal_queue/balancing.py",

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
    SERVER / "orchestration/template_step_schema.py",

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
    "fan_out": re.compile(
        r"\b("
        r"fan_out|fan-out|fan out|fanout"
        r")\b",
        re.IGNORECASE,
    ),

    "fan_out_group": re.compile(
        r"\b("
        r"fan_out_group|fanout_group|"
        r"fan-out group|parallel group|"
        r"parallel_group"
        r")\b",
        re.IGNORECASE,
    ),

    "parallel": re.compile(
        r"\b("
        r"parallel|parallelism|concurrent|concurrency"
        r")\b",
        re.IGNORECASE,
    ),

    "dependent_map": re.compile(
        r"\b("
        r"dependent_map|dependents|"
        r"dependent_job_ids"
        r")\b",
        re.IGNORECASE,
    ),

    "dependency_map": re.compile(
        r"\b("
        r"dependency_map|dependency_job_ids|dependencies"
        r")\b",
        re.IGNORECASE,
    ),

    "execution_wave": re.compile(
        r"\b("
        r"execution_wave|execution_waves|"
        r"wave_count|graph_depth|"
        r"max_parallel_width"
        r")\b",
        re.IGNORECASE,
    ),

    "root_leaf": re.compile(
        r"\b("
        r"root_job_ids|leaf_job_ids|"
        r"root_nodes|leaf_nodes"
        r")\b",
        re.IGNORECASE,
    ),

    "parent_child": re.compile(
        r"\b("
        r"parent_job_id|child_job|children|"
        r"child_jobs|parent_job"
        r")\b",
        re.IGNORECASE,
    ),

    "branch": re.compile(
        r"\b("
        r"branch|branches|branching|fork"
        r")\b",
        re.IGNORECASE,
    ),

    "join": re.compile(
        r"\b("
        r"join|fan_in|fan-in|fan in|fanin"
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

    "queue": re.compile(
        r"\b("
        r"queue|queued|enqueue|dequeue|claim"
        r")\b",
        re.IGNORECASE,
    ),

    "worker": re.compile(
        r"\b("
        r"worker|workers|assignment|worker_id"
        r")\b",
        re.IGNORECASE,
    ),

    "lease": re.compile(
        r"\b("
        r"lease|leased|lease_id|lease_owner"
        r")\b",
        re.IGNORECASE,
    ),

    "dispatch": re.compile(
        r"\b("
        r"dispatch|handler|execute|execution"
        r")\b",
        re.IGNORECASE,
    ),

    "status": re.compile(
        r"\b("
        r"UniversalJobStatus|created|queued|scheduled|"
        r"leased|running|suspended|succeeded|failed|"
        r"cancelled|dead_letter|expired"
        r")\b",
        re.IGNORECASE,
    ),

    "batch": re.compile(
        r"\b("
        r"batch_id|batch|batch_jobs"
        r")\b",
        re.IGNORECASE,
    ),

    "pipeline_run": re.compile(
        r"\b("
        r"pipeline_run_id|pipeline_run"
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

    "persistence": re.compile(
        r"\b("
        r"persist|persistence|state_store|"
        r"runtime_state_store"
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
                    "fanout",
                    "fan_out",
                    "parallel",
                    "fork",
                    "branch",
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
                    "fanout",
                    "fan_out",
                    "parallel",
                    "fork",
                    "branch",
                    "child",
                    "dependent",
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
                        "fanout",
                        "fan_out",
                        "parallel",
                        "fork",
                        "branch",
                        "child",
                        "dependent",
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
                    "readiness",
                    "handoff",
                    "queue",
                    "worker",
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

repo_categories = (
    "fan_out",
    "fan_out_group",
    "parallel",
    "dependent_map",
    "parent_child",
    "branch",
    "join",
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
# EXECUTION-PLANNING STRUCTURAL INSPECTION
# ============================================================

EXECUTION_PLANNING_PATH = (
    SERVER
    / "runtime"
    / "universal_orchestration"
    / "execution_planning.py"
)


planning_structure = []


if EXECUTION_PLANNING_PATH.exists():

    source = EXECUTION_PLANNING_PATH.read_text(
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
                "dependent_map",
                "dependency_map",
                "execution_waves",
                "topological_order",
                "root_job_ids",
                "leaf_job_ids",
                "max_parallel_width",
                "graph_depth",
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
        "PHASE 5.1.8 — UNIVERSAL ORCHESTRATION "
        "FAN-OUT COORDINATION READ-ONLY DISCOVERY"
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
        "SECTION 3 — FAN-OUT FINDING COUNTS",
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
        "SECTION 7 — DECLARED FAN-OUT / PARALLEL FIELDS",
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
        "SECTION 9 — EXECUTION PLANNING STRUCTURAL SIGNALS",
        "-" * 118,
        "",
    ]
)


if planning_structure:

    for line, text in planning_structure:

        out.append(
            (
                "backend\\server\\runtime\\"
                "universal_orchestration\\"
                "execution_planning.py:"
                + str(line)
                + " | "
                + text
            )
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 10 — FOCUSED TARGET FINDINGS",
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
        "SECTION 11 — REPOSITORY-WIDE FAN-OUT SEARCH",
        "-" * 118,
        "",
        (
            "Python files scanned: "
            + str(
                python_files_scanned
            )
        ),
        (
            "Files with focused fan-out findings: "
            + str(
                len(
                    repo_file_counts
                )
            )
        ),
        (
            "Total focused fan-out findings: "
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
        (
            f"{index:03d}. "
            f"hits={count} "
            + filename
        )
    )


out.extend(
    [
        "",
        "SECTION 13 — REPOSITORY FAN-OUT FINDINGS",
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

    if len(
        items
    ) > 600:

        out.append(
            (
                "... TRUNCATED: "
                + str(
                    len(items)
                    - 600
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
        "SECTION 15 — 5.1.8 ARCHITECTURE QUESTIONS",
        "-" * 118,
        "",

        "1. Does a canonical Universal Runtime Orchestration fan-out authority already exist?",
        "2. Is any existing fan-out implementation pipeline-specific rather than universal?",
        "3. Does frozen 5.1.5 already expose all structural information required for fan-out?",
        "4. Is dependent_map the canonical source of direct downstream dependents?",
        "5. Is execution_waves useful as corroborating structure but not the definition of one fan-out group?",
        "6. Should a fan-out source be one job with two or more direct dependents?",
        "7. Should a source with exactly one direct dependent be classified as NO_FAN_OUT?",
        "8. Should a leaf job with zero dependents be classified as NO_FAN_OUT?",
        "9. Should direct dependents only be included, excluding transitive descendants?",
        "10. Should fan-out membership be determined strictly by graph edges from 5.1.5?",
        "11. Should parent_job_id ever create fan-out membership implicitly? Expected NO.",
        "12. Should batch_id ever create fan-out membership implicitly? Expected NO.",
        "13. Should pipeline_run_id ever create fan-out membership implicitly? Expected NO.",
        "14. Should jobs merely sharing an execution wave be considered one fan-out group? Expected NO.",
        "15. Can unrelated jobs occur in the same execution wave? Expected YES.",
        "16. Should fan-out group members be lexical job_id order for determinism?",
        "17. Should fan-out group identity be deterministic and derived?",
        "18. Should 5.1.8 consume the exact frozen 5.1.5 Execution Plan?",
        "19. Should 5.1.8 consume a source job_id or a source UniversalJob?",
        "20. Can the source UniversalJob be derived from execution_plan.job_map?",
        "21. Should source job_id be normalized through existing orchestration identifier rules?",
        "22. Must source job_id belong to the execution plan?",
        "23. Should 5.1.8 consume 5.1.6 Stage Readiness?",
        "24. Should structural fan-out exist regardless of current readiness? Likely YES.",
        "25. Should 5.1.8 consume 5.1.7 Runtime Handoff decisions?",
        "26. Is 5.1.7 eligibility relevant only when deciding which members may later progress?",
        "27. Should 5.1.8 itself evaluate each child readiness? Expected NO.",
        "28. Should 5.1.8 itself evaluate child handoff eligibility? Expected NO.",
        "29. Should a source job need to be READY or ELIGIBLE to possess a structural fan-out? Expected NO.",
        "30. Should fan-out coordination expose direct dependent IDs even if those dependents are WAITING/BLOCKED?",
        "31. Should fan-out classification distinguish FAN_OUT / NO_FAN_OUT?",
        "32. Is there a need for DEFERRED/BLOCKED inside structural fan-out itself? Expected NO.",
        "33. Should fan-out width equal direct dependent count?",
        "34. Should a fan-out source with N direct dependents expose width=N?",
        "35. Should direct_dependents be immutable tuple?",
        "36. Should source job be both root/non-root capable? Expected YES.",
        "37. Can an internal graph node fan out after depending on upstream jobs? Expected YES.",
        "38. Can a root job fan out? Expected YES.",
        "39. Can a source fan out to jobs that later converge in 5.1.9? Expected YES.",
        "40. Should join/fan-in semantics be explicitly excluded from 5.1.8?",
        "41. Should conditional branch activation be excluded until 5.1.10?",
        "42. If graph contains multiple dependents but a future condition selects only some, does 5.1.8 remain structural before 5.1.10?",
        "43. Should queue state affect fan-out structure? Expected NO.",
        "44. Should target UniversalJob.status affect fan-out structure? Expected NO.",
        "45. Should job priority affect fan-out structure? Expected NO.",
        "46. Should created_at affect fan-out structure? Expected NO.",
        "47. Should worker availability affect fan-out structure? Expected NO.",
        "48. Should worker capacity/capability/health affect fan-out structure? Expected NO.",
        "49. Should lease availability affect fan-out structure? Expected NO.",
        "50. Should 5.1.8 enqueue child jobs? Expected NO.",
        "51. Should 5.1.8 schedule child jobs? Expected NO.",
        "52. Should 5.1.8 claim child jobs? Expected NO.",
        "53. Should 5.1.8 assign child jobs to workers? Expected NO.",
        "54. Should 5.1.8 acquire leases? Expected NO.",
        "55. Should 5.1.8 dispatch runtime handlers? Expected NO.",
        "56. Should 5.1.8 execute jobs in parallel? Expected NO.",
        "57. Should 5.1.8 create threads/processes/tasks? Expected NO.",
        "58. Should 5.1.8 mutate UniversalJob.status? Expected NO.",
        "59. Should 5.1.8 transition orchestration state? Expected NO.",
        "60. Should 5.1.8 access Runtime State Store? Expected NO.",
        "61. Should 5.1.8 persist fan-out decisions? Expected NO; 5.1.14.",
        "62. Should 5.1.8 import Universal Coordination Framework? Expected NO.",
        "63. Should 5.1.8 invoke pipeline coordinators? Expected NO.",
        "64. Should the result be immutable and deterministic?",
        "65. Should it store execution_plan + source_job_id + schema_version?",
        "66. Or should source_job_id remain normalized/stored while source_job remains derived?",
        "67. Should direct_dependents remain derived rather than stored?",
        "68. Should classification and width remain derived rather than stored?",
        "69. Should dependent_map remain owned exclusively by 5.1.5?",
        "70. Should 5.1.8 ever duplicate the full graph? Expected NO.",
        "71. Should source_job_id itself be stored because it selects the fan-out locus?",
        "72. What exact error should occur for source_job_id outside the plan?",
        "73. Should empty/whitespace/non-string source identifiers be rejected?",
        "74. Should bool be rejected as source identifier?",
        "75. Should 5.1.8 use the same 200-character identifier limit as 5.1.1?",
        "76. Should one fan-out evaluation describe exactly one source node?",
        "77. Should whole-plan fan-out enumeration be a separate helper derived by repeated single-source evaluation?",
        "78. Should global fan-out enumeration be excluded from the core stored object?",
        "79. Should fan-out group lexical ordering inherit directly from 5.1.5 dependent_map?",
        "80. Where exactly is the boundary between structural fan-out coordination and actual parallel runtime execution?",
        "",
        (
            "NEXT: analyze findings and freeze the exact "
            "5.1.8 Fan-Out Coordination boundary "
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
    "PHASE 5.1.8 FAN-OUT COORDINATION DISCOVERY COMPLETE"
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
    "Repo files with focused fan-out findings:",
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
    "Repo focused fan-out findings:",
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
