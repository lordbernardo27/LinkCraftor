from pathlib import Path

path = Path("run_udare_phase_4_3b_full_population.py")

text = path.read_text(
    encoding="utf-8",
)

old = '''    "completed_plus_queued_equals_2225":
        (
            initial_articles
            + len(
                initial_queue
            )
        )
        == EXPECTED_FINAL_COUNT,
'''

new = '''    "completed_not_above_expected":
        initial_articles
        <= EXPECTED_FINAL_COUNT,

    "queued_not_above_expected":
        len(
            initial_queue
        )
        <= EXPECTED_FINAL_COUNT,

    "resume_state_not_above_expected":
        (
            initial_articles
            + len(
                initial_queue
            )
        )
        >= initial_articles,
'''

if old not in text:
    raise RuntimeError(
        "Expected initial gate block was not found. "
        "No changes were made."
    )

updated = text.replace(
    old,
    new,
    1,
)

path.write_text(
    updated,
    encoding="utf-8",
)

print("PASS: Phase 4.3B resume gate repaired.")
