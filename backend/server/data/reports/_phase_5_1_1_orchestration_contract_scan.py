from __future__ import annotations

import ast
import hashlib
import re
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
    / "phase_5_1_1_orchestration_contract_scan.txt"
)


PROTECTED = {
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


protection = []


for name, (
    path,
    expected,
) in PROTECTED.items():

    if not path.exists():

        protection.append(
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

        protection.append(
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

    protection.append(
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


TARGETS = (
    SERVER / "orchestration/models.py",
    SERVER / "orchestration/service.py",
    SERVER / "orchestration/queue.py",
    SERVER / "orchestration/job_store.py",

    SERVER / "runtime/universal_runtime_worker_v1.py",
    SERVER / "runtime/universal_runtime_registration.py",
    SERVER / "runtime/runtime_state_store.py",

    SERVER / "runtime/universal_jobs/contract.py",
    SERVER / "runtime/universal_jobs/lineage.py",
    SERVER / "runtime/universal_jobs/status.py",

    SERVER / "coordination/universal_workflows/contract.py",
    SERVER / "coordination/universal_stages/contract.py",
    SERVER / "coordination/universal_stages/result_contract.py",
)


PATTERNS = {
    "identity": re.compile(
        r"\b("
        r"job_id|workflow_id|run_id|pipeline_run_id|"
        r"batch_id|parent_job_id"
        r")\b",
        re.IGNORECASE,
    ),

    "state": re.compile(
        r"\b("
        r"status|state|transition|lifecycle"
        r")\b",
        re.IGNORECASE,
    ),

    "dependency": re.compile(
        r"\b("
        r"dependency|dependencies|dependency_job_ids"
        r")\b",
        re.IGNORECASE,
    ),

    "execution": re.compile(
        r"\b("
        r"execute|execution|dispatch|handler|worker"
        r")\b",
        re.IGNORECASE,
    ),

    "queue": re.compile(
        r"\b("
        r"queue|queued|enqueue|claim"
        r")\b",
        re.IGNORECASE,
    ),

    "persistence": re.compile(
        r"\b("
        r"persist|persistence|state_store|job_store"
        r")\b",
        re.IGNORECASE,
    ),

    "coordination": re.compile(
        r"\b("
        r"coordination|coordinator|workflow"
        r")\b",
        re.IGNORECASE,
    ),

    "progress": re.compile(
        r"\b("
        r"progress|checkpoint"
        r")\b",
        re.IGNORECASE,
    ),

    "contract": re.compile(
        r"\b("
        r"contract|schema|version"
        r")\b",
        re.IGNORECASE,
    ),
}


findings = []

classes = []

functions = []

fields_found = []

imports = []

errors = []


for path in TARGETS:

    if not path.exists():

        errors.append(
            (
                str(
                    path.relative_to(
                        ROOT
                    )
                ),
                "MISSING",
            )
        )

        continue

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

        for category, pattern in (
            PATTERNS.items()
        ):

            if pattern.search(
                line
            ):

                findings.append(
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

                fields_found.append(
                    (
                        relative,
                        node.lineno,
                        node.target.id,
                    )
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):

            imports.append(
                (
                    relative,
                    node.lineno,
                    node.module or "",
                )
            )


out = [
    (
        "PHASE 5.1.1 — ORCHESTRATION CONTRACT "
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
    protection
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
        "SECTION 2 — TARGET FILES",
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
        "SECTION 3 — CLASSES",
        "-" * 118,
        "",
    ]
)


for relative, line, name in sorted(
    classes
):

    out.append(
        f"{relative}:{line} class {name}"
    )


out.extend(
    [
        "",
        "SECTION 4 — FUNCTIONS",
        "-" * 118,
        "",
    ]
)


for relative, line, name in sorted(
    functions
):

    out.append(
        f"{relative}:{line} {name}()"
    )


out.extend(
    [
        "",
        "SECTION 5 — DECLARED FIELDS",
        "-" * 118,
        "",
    ]
)


for relative, line, name in sorted(
    fields_found
):

    out.append(
        f"{relative}:{line} {name}"
    )


out.extend(
    [
        "",
        "SECTION 6 — IMPORT RELATIONSHIPS",
        "-" * 118,
        "",
    ]
)


for relative, line, module in sorted(
    imports
):

    out.append(
        f"{relative}:{line} -> {module}"
    )


out.extend(
    [
        "",
        "SECTION 7 — CONTRACT-RELEVANT FINDINGS",
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

    category_items = [
        item
        for item in findings
        if item[0] == category
    ]

    if not category_items:

        out.append(
            "NONE"
        )

        continue

    for _, relative, line, text in (
        category_items
    ):

        out.append(
            f"{relative}:{line} | {text}"
        )


out.extend(
    [
        "",
        "SECTION 8 — ERRORS",
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
        "SECTION 9 — 5.1.1 CONTRACT QUESTIONS",
        "-" * 118,
        "",
        "1. Does a canonical Phase-5 runtime orchestration contract already exist?",
        "2. Which existing OrchestrationJob fields are legacy operational fields?",
        "3. Which existing UniversalJob fields should Phase 5 reference rather than duplicate?",
        "4. Should orchestration_run_id be defined here or deferred to 5.1.2?",
        "5. Should 5.1.1 carry run identity or only contract/schema identity?",
        "6. Should pipeline_run_id be consumed directly by 5.1.1?",
        "7. Should batch_id be excluded from orchestration identity?",
        "8. Should parent/dependency job IDs remain Universal Job evidence?",
        "9. Should 5.1.1 own state transitions? Expected: NO, defer to 5.1.3.",
        "10. Should 5.1.1 own dependency resolution? Expected: NO, defer to 5.1.4.",
        "11. Should 5.1.1 execute or dispatch anything? Expected: NO.",
        "12. Should 5.1.1 enqueue or claim jobs? Expected: NO.",
        "13. Should 5.1.1 import Runtime Registration? Expected: NO.",
        "14. Should 5.1.1 import Worker Infrastructure? Expected: NO.",
        "15. Should 5.1.1 import Universal Coordination Framework? Expected: NO.",
        "16. Should 5.1.1 persist state? Expected: NO.",
        "17. Should 5.1.1 access Runtime State Store? Expected: NO.",
        "18. Should the contract be immutable and deterministic?",
        "19. What minimum fields uniquely describe one orchestration definition/request?",
        "20. Which fields must deliberately be deferred to later Phase-5 authorities?",
        "",
        (
            "NEXT: freeze the exact 5.1.1 Orchestration Contract "
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


print()
print("=" * 100)
print(
    "PHASE 5.1.1 ORCHESTRATION CONTRACT DISCOVERY COMPLETE"
)
print("=" * 100)

print(
    "Target files:",
    len(
        TARGETS
    ),
)

print(
    "Findings:",
    len(
        findings
    ),
)

print(
    "Errors:",
    len(
        errors
    ),
)

print(
    "Frozen authority failures:",
    sum(
        1
        for _, status, _, _
        in protection
        if status != "PASS"
    ),
)

print()

print(
    "STATUS: DISCOVERY ONLY — NO PRODUCTION CODE MODIFIED"
)

print(
    "REPORT:",
    REPORT_PATH,
)
