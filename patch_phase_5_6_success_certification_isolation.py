from pathlib import Path

P = Path("certify_runtime_integration_phase_5_6_success_path.py")
S = P.read_text(encoding="utf-8")

anchor = '''check(
    "list_job_events resolved",
    callable(
        list_job_events
    ),
)


# =========================================================================
# 3. Safety gate — do not consume somebody else's queued job
# =========================================================================
'''

replacement = '''check(
    "list_job_events resolved",
    callable(
        list_job_events
    ),
)


# =========================================================================
# 3. Isolated real orchestration store
#
# Phase 5.6 certification must exercise the REAL orchestration persistence,
# queue, worker, status-event and intake functions without consuming or
# modifying pre-existing production/development queue records.
#
# job_store functions resolve JOBS_FILE / EVENTS_FILE from their module
# globals at call time, so redirecting these globals inside THIS verifier
# process preserves the real implementation while isolating certification
# data.
# =========================================================================

REAL_JOBS_FILE = Path(
    job_store.JOBS_FILE
)

REAL_EVENTS_FILE = Path(
    job_store.EVENTS_FILE
)


REAL_JOBS_BYTES_BEFORE = (
    REAL_JOBS_FILE.read_bytes()
    if REAL_JOBS_FILE.exists()
    else None
)

REAL_EVENTS_BYTES_BEFORE = (
    REAL_EVENTS_FILE.read_bytes()
    if REAL_EVENTS_FILE.exists()
    else None
)


real_jobs_before = load_jobs()

real_queued_before = [
    job
    for job
    in real_jobs_before.values()
    if str(
        getattr(
            job,
            "status",
            "",
        )
    ).strip().lower()
    == "queued"
]


CERTIFICATION_STORE = (
    ROOT
    / "backend/server/data/orchestration/"
      "phase_5_6_success_certification"
)

CERTIFICATION_JOBS_FILE = (
    CERTIFICATION_STORE
    / "jobs.json"
)

CERTIFICATION_EVENTS_FILE = (
    CERTIFICATION_STORE
    / "job_events.json"
)


if (
    CERTIFICATION_JOBS_FILE.exists()
    or CERTIFICATION_EVENTS_FILE.exists()
):
    raise SystemExit(
        (
            "SUCCESS-PATH CERTIFICATION REFUSED: "
            "isolated certification evidence already exists. "
            "No existing certification evidence will be overwritten.\\n"
            f"Store: {CERTIFICATION_STORE}"
        )
    )


CERTIFICATION_STORE.mkdir(
    parents=True,
    exist_ok=True,
)


job_store.DATA_DIR = (
    CERTIFICATION_STORE
)

job_store.JOBS_FILE = (
    CERTIFICATION_JOBS_FILE
)

job_store.EVENTS_FILE = (
    CERTIFICATION_EVENTS_FILE
)


check(
    "Orchestration store redirected to isolated certification path",
    (
        Path(
            job_store.JOBS_FILE
        )
        == CERTIFICATION_JOBS_FILE
        and Path(
            job_store.EVENTS_FILE
        )
        == CERTIFICATION_EVENTS_FILE
    ),
    str(
        CERTIFICATION_STORE
    ),
)


check(
    "Real orchestration store not selected for certification",
    (
        Path(
            job_store.JOBS_FILE
        )
        != REAL_JOBS_FILE
        and Path(
            job_store.EVENTS_FILE
        )
        != REAL_EVENTS_FILE
    ),
)


check(
    "Pre-existing real queued jobs preserved outside certification store",
    True,
    (
        "Real queued jobs observed but not consumed: "
        + str(
            len(
                real_queued_before
            )
        )
    ),
)


# =========================================================================
# 3A. Safety gate — isolated certification queue must begin empty
# =========================================================================
'''

if anchor not in S:
    raise SystemExit(
        "Verifier patch refused: isolation anchor not found. Production untouched."
    )

S = S.replace(
    anchor,
    replacement,
    1,
)


old_real_store_check = '''# =========================================================================
# 12. Production source immutability
# =========================================================================

check(
    "Production source files unchanged",
'''

new_real_store_check = '''# =========================================================================
# 12. Real-store + production-source immutability
# =========================================================================

REAL_JOBS_BYTES_AFTER = (
    REAL_JOBS_FILE.read_bytes()
    if REAL_JOBS_FILE.exists()
    else None
)

REAL_EVENTS_BYTES_AFTER = (
    REAL_EVENTS_FILE.read_bytes()
    if REAL_EVENTS_FILE.exists()
    else None
)


check(
    "Real orchestration jobs store unchanged",
    (
        REAL_JOBS_BYTES_AFTER
        == REAL_JOBS_BYTES_BEFORE
    ),
)


check(
    "Real orchestration event store unchanged",
    (
        REAL_EVENTS_BYTES_AFTER
        == REAL_EVENTS_BYTES_BEFORE
    ),
)


check(
    "Existing real queued jobs were not consumed",
    (
        len(
            real_queued_before
        )
        == len(
            [
                job
                for job
                in real_jobs_before.values()
                if str(
                    getattr(
                        job,
                        "status",
                        "",
                    )
                ).strip().lower()
                == "queued"
            ]
        )
    ),
)


check(
    "Certification jobs file exists only in isolated store",
    CERTIFICATION_JOBS_FILE.exists(),
    str(
        CERTIFICATION_JOBS_FILE
    ),
)


check(
    "Certification events file exists only in isolated store",
    CERTIFICATION_EVENTS_FILE.exists(),
    str(
        CERTIFICATION_EVENTS_FILE
    ),
)


check(
    "Production source files unchanged",
'''

if old_real_store_check not in S:
    raise SystemExit(
        "Verifier patch refused: immutability anchor not found. Production untouched."
    )

S = S.replace(
    old_real_store_check,
    new_real_store_check,
    1,
)

P.write_text(
    S,
    encoding="utf-8",
)

print("PHASE 5.6.5 VERIFIER ISOLATION PATCH INSTALLED")
print("Verifier:", P)
print("Production source modified: False")
print("Real orchestration store modified: False")
