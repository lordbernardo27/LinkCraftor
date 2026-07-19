from pathlib import Path

worker = Path(
    "backend/server/workers/"
    "udare_reconstruction_worker.py"
).read_text(
    encoding="utf-8",
    errors="strict",
)

runner = Path(
    "run_udare_phase_4_3b_full_population.py"
).read_text(
    encoding="utf-8",
    errors="strict",
)

checks = {
    "worker_reads_defer_flag":
        "UDARE_DEFER_GLOBAL_ARTIFACTS"
        in worker,

    "worker_still_builds_review":
        "build_udare_review_document_v1("
        in worker,

    "worker_can_defer_manifest":
        '"deferred":'
        in worker,

    "worker_can_defer_index":
        "global_artifacts_deferred"
        in worker,

    "runner_is_resumable":
        "completed_plus_queued_equals_2225"
        in runner,

    "runner_rebuilds_final_index":
        "final_index_result = "
        "build_udare_store_index_v1("
        in runner,

    "runner_refreshes_manifest_once_at_end":
        "refresh_udare_store_manifest_v1("
        in runner,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

print()
print("=" * 104)
print("PHASE 4.3B SPEED OPTIMIZATION VERIFICATION")
print("=" * 104)

for name, passed in checks.items():
    print(
        f"  {name}:",
        "PASS" if passed else "FAIL",
    )

print()
print("=" * 104)

if failed:
    print("PHASE 4.3B SPEED OPTIMIZATION: FAIL")
    print(
        "Failed checks:",
        ", ".join(failed),
    )
else:
    print("PHASE 4.3B SPEED OPTIMIZATION: PASS")

print("=" * 104)

raise SystemExit(
    0 if not failed else 1
)
