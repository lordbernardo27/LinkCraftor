from __future__ import annotations

import ast
import hashlib

from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

ORCH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
)

REPORT = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_18_runtime_orchestration_certification_discovery.txt"
)


AUTHORITIES = (
    (
        "5.1.1",
        "contract.py",
        "8CC241284B8AF87809A41134FF0FDEB402D5DE49A117D931920CC17346271FD9",
    ),
    (
        "5.1.2",
        "run_identity.py",
        "A582564C7D45D96DAB2D6DAF38E8C63B9EA281251F41B02D12DE17F1D68CAFBC",
    ),
    (
        "5.1.3",
        "state_model.py",
        "B179C6BEB0A232F0170A2ED540D84239A2235A4F0F91528B530E229B61172610",
    ),
    (
        "5.1.4",
        "dependency_resolution.py",
        "CF4CE73A8683BFDA1464730F2079058898B2660275C786FA6EBD0816AE574A8E",
    ),
    (
        "5.1.5",
        "execution_planning.py",
        "78F7945AD5592370C21BF919328D6C29627EF209F37A5E864C0588CD40DC7465",
    ),
    (
        "5.1.6",
        "stage_readiness.py",
        "9BF16440AD057B1C6A89DD9AEEDEADBE32F711EAE2D4FCD8730EB796BF603D6D",
    ),
    (
        "5.1.7",
        "runtime_handoff.py",
        "6878FC6F0F2EF071B11A93D793A0CC80B2C91B676C6B6735A78237D8C7D6CB73",
    ),
    (
        "5.1.8",
        "fan_out_coordination.py",
        "D60C8629D2490DC41A8DF43E30F00A1D4851941E65CBD2EBE7EED70B75217916",
    ),
    (
        "5.1.9",
        "fan_in_coordination.py",
        "98786AEF5E4DBD804FBE5FE32EEE7CD54907FAC6A9C016B6120851834F6CFA0F",
    ),
    (
        "5.1.10",
        "conditional_branching.py",
        "3799D3BEFB10C77400B40964EBBCCF598B7576BA9034D1C7F29622D0EC65286F",
    ),
    (
        "5.1.11",
        "progress_tracking.py",
        "92C100E0682F975488F78ED5F0D38CB1F4C6E18F6FEA08D1A8D81BE98A4D8309",
    ),
    (
        "5.1.12",
        "suspension_resume_eligibility.py",
        "476631641C740443FF7B3D1D1D0E9D6D155289BDCAF14526698528432CCF913A",
    ),
    (
        "5.1.13",
        "recovery.py",
        "4465A7AF795512594023D19E27A175CA060ACD2845BB4530B77FF8D69C40B16F",
    ),
    (
        "5.1.14",
        "persistence_interface.py",
        "5B7F640250498B4B5320C3702112D163E16B6878C412447623E5C0FF93608CCA",
    ),
    (
        "5.1.15",
        "completion_resolution.py",
        "1311EEBEB9622AF5D4CF6F4D7CB14FF83B169C748A01DDD144A8000301A5CBD4",
    ),
    (
        "5.1.16",
        "cancellation_termination.py",
        "3D2095E4B546596554875BB8FB1E289489FAFD26C013DBE40A7066DB197E25CB",
    ),
    (
        "5.1.17",
        "evidence_records.py",
        "6BF84A9D3E8B120D5506DFF31D4BEB8718ECF488820E69782C7F0F7C85758FD9",
    ),
)


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


rows = []
failures = []


for phase, filename, expected in AUTHORITIES:

    path = (
        ORCH
        / filename
    )

    if not path.exists():

        rows.append(
            (
                phase,
                filename,
                "MISSING",
                expected,
                None,
            )
        )

        failures.append(
            phase
            + " missing"
        )

        continue

    try:

        actual = ast_sha(
            path
        )

    except Exception as exc:

        rows.append(
            (
                phase,
                filename,
                "ERROR",
                expected,
                repr(exc),
            )
        )

        failures.append(
            phase
            + " parse error"
        )

        continue

    status = (
        "PASS"
        if actual == expected
        else "FAIL"
    )

    rows.append(
        (
            phase,
            filename,
            status,
            expected,
            actual,
        )
    )

    if status != "PASS":

        failures.append(
            phase
            + " AST mismatch"
        )


python_files = tuple(
    path
    for path
    in ORCH.glob(
        "*.py"
    )
    if (
        not path.name.startswith(
            "__"
        )
        and
        "before_" not in path.name
    )
)


imports = []


for path in python_files:

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source
    )

    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.ImportFrom,
        ):

            module = (
                node.module
                or ""
            )

            if module.startswith(
                "backend.server.runtime.universal_orchestration"
            ):

                imports.append(
                    (
                        path.name,
                        module,
                    )
                )


lines = [
    (
        "PHASE 5.1.18 — UNIVERSAL RUNTIME ORCHESTRATION "
        "CERTIFICATION READ-ONLY DISCOVERY"
    ),

    "=" * 118,

    "",

    "PRODUCTION CODE MODIFIED: NO",

    "",

    "SECTION 1 — FROZEN AUTHORITY AST MATRIX",
    "-" * 118,
    "",
]


for (
    phase,
    filename,
    status,
    expected,
    actual,
) in rows:

    lines.extend(
        [
            (
                phase
                + " "
                + filename
                + ": "
                + status
            ),

            (
                "  EXPECTED: "
                + expected
            ),

            (
                "  ACTUAL:   "
                + str(
                    actual
                )
            ),

            "",
        ]
    )


lines.extend(
    [
        "SECTION 2 — ORCHESTRATION-INTERNAL IMPORT GRAPH",
        "-" * 118,
        "",
    ]
)


if imports:

    for source_name, target in sorted(
        imports
    ):

        lines.append(
            source_name
            + " -> "
            + target
        )

else:

    lines.append(
        "NONE"
    )


lines.extend(
    [
        "",

        "SECTION 3 — CERTIFICATION QUESTIONS",
        "-" * 118,
        "",

        "1. Are all 17 frozen orchestration authorities present?",
        "2. Do all 17 retain their frozen AST hashes?",

        "3. Is the authority dependency graph acyclic where required?",
        "4. Are downstream decision authorities consuming rather than re-owning upstream semantics?",

        "5. Is 5.1.3 the sole orchestration state-transition legality authority?",
        "6. Is 5.1.11 the canonical orchestration progress authority?",
        "7. Is 5.1.12 eligibility-only rather than execution?",
        "8. Is 5.1.13 recovery-decision-only rather than retry execution?",
        "9. Is 5.1.14 persistence-interface-only rather than concrete backend?",
        "10. Is 5.1.15 completion-decision-only rather than actual transition?",
        "11. Is 5.1.16 cancellation-decision-only rather than cancellation execution?",
        "12. Is 5.1.17 semantic evidence-only rather than audit/backend storage?",

        "13. Are completion and cancellation semantically non-overlapping?",
        "14. Does effective CANCELLED work route to 5.1.16 rather than 5.1.15 FAILED?",
        "15. Does FAILED/DEAD_LETTER/EXPIRED completion remain independent of retryability?",

        "16. Are excluded conditional branches consistently ignored by progress/completion/cancellation?",

        "17. Are missing and unresolved evidence consistently preserved as uncertainty rather than guessed around?",

        "18. Does Phase 5 perform any job execution?",
        "19. Does Phase 5 enqueue/dequeue/claim work?",
        "20. Does Phase 5 assign or terminate workers?",
        "21. Does Phase 5 manipulate leases?",
        "22. Does Phase 5 dispatch runtime handlers?",

        "23. Does Phase 5 directly access Runtime State Store?",
        "24. Does Phase 5 perform concrete database/filesystem/network persistence?",

        "25. Does Phase 5 import Universal Coordination Framework?",
        "26. Does Phase 5 invoke pipeline coordinators?",

        "27. Are 5.1.14 persistence history and 5.1.17 semantic decision evidence cleanly separated?",

        "28. Is actual execution correctly deferred to Phase 6 Execution Engine?",

        "29. Should 5.1.18 create a certification manifest rather than a new runtime capability?",
        "30. Should that manifest bind all 17 authority ASTs and frozen semantic fingerprints?",

        "",

        "NEXT: analyze this discovery and define the final Phase-5 certification contract.",
    ]
)


REPORT.write_text(
    "\n".join(
        lines
    ),
    encoding="utf-8",
)


print("=" * 100)
print(
    "PHASE 5.1.18 RUNTIME ORCHESTRATION CERTIFICATION DISCOVERY COMPLETE"
)
print("=" * 100)

print(
    "Frozen authorities checked:",
    len(
        AUTHORITIES
    ),
)

print(
    "Frozen authority failures:",
    len(
        failures
    ),
)

print(
    "Internal orchestration imports discovered:",
    len(
        imports
    ),
)

print()

print(
    "STATUS: DISCOVERY ONLY — NO PRODUCTION CODE MODIFIED"
)

print(
    "REPORT:",
    REPORT,
)


if failures:

    raise SystemExit(
        "5.1.18 discovery found frozen-authority failures."
    )
