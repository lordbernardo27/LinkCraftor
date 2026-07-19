from __future__ import annotations

import ast
from pathlib import Path


path = Path(
    "run_udare_phase_4_3b_full_population.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)


# ---------------------------------------------------------------
# Import the index builder for one final rebuild.
# ---------------------------------------------------------------

index_import = '''from backend.server.stores.udare_store_index_builder import (
    build_udare_store_index_v1,
)

'''

if "build_udare_store_index_v1" not in text:
    marker = '''from backend.server.stores.udare_store import (
    refresh_udare_store_manifest_v1,
    verify_udare_store_v1,
)

'''

    if marker not in text:
        raise RuntimeError(
            "UDARE store import block was not found."
        )

    text = text.replace(
        marker,
        marker + index_import,
        1,
    )


# ---------------------------------------------------------------
# Replace rigid five/2220 initial gate with resumable invariants.
# ---------------------------------------------------------------

gate_start = text.find(
    "initial_checks = {\n"
)

gate_end_marker = (
    "\n\nfailed_initial = [\n"
)

gate_end = text.find(
    gate_end_marker,
    gate_start,
)

if gate_start < 0 or gate_end < 0:
    raise RuntimeError(
        "Initial Phase 4.3B gate was not found."
    )


new_gate = '''initial_checks = {
    "initial_queue_not_negative":
        len(
            initial_queue
        )
        >= 0,

    "initial_articles_at_least_5":
        initial_articles
        >= EXPECTED_INITIAL_STORE_COUNT,

    "initial_reviews_match_articles":
        initial_reviews
        == initial_articles,

    "initial_metadata_matches_articles":
        initial_metadata
        == initial_articles,

    "completed_plus_queued_equals_2225":
        (
            initial_articles
            + len(
                initial_queue
            )
        )
        == EXPECTED_FINAL_COUNT,

    "index_exists":
        INDEX_PATH.is_file(),

    "manifest_exists":
        MANIFEST_PATH.is_file(),
}
'''

text = (
    text[:gate_start]
    + new_gate
    + text[gate_end:]
)


# ---------------------------------------------------------------
# Make final execution checks use the actual queue count seen when
# this resumed run begins.
# ---------------------------------------------------------------

text = text.replace(
    '''    "executed_remaining_2220":
        total_executed
        == EXPECTED_INITIAL_QUEUE_COUNT,

    "successful_2220":
        total_successful
        == EXPECTED_INITIAL_QUEUE_COUNT,
''',
    '''    "executed_all_jobs_present_at_resume":
        total_executed
        == len(
            initial_queue
        ),

    "successful_all_jobs_present_at_resume":
        total_successful
        == len(
            initial_queue
        ),
''',
    1,
)


# ---------------------------------------------------------------
# Rebuild the global index once after all jobs finish.
# ---------------------------------------------------------------

marker = '''refresh_udare_store_manifest_v1(
    WORKSPACE_ID
)

store_verification = verify_udare_store_v1(
    WORKSPACE_ID
)
'''

replacement = '''refresh_udare_store_manifest_v1(
    WORKSPACE_ID
)

final_index_result = build_udare_store_index_v1(
    WORKSPACE_ID
)

if (
    not isinstance(
        final_index_result,
        dict,
    )
    or final_index_result.get(
        "ok"
    )
    is not True
):
    raise RuntimeError(
        "Final UDARE index rebuild failed."
    )

store_verification = verify_udare_store_v1(
    WORKSPACE_ID
)
'''

if marker not in text:
    raise RuntimeError(
        "Final manifest-refresh section was not found."
    )

text = text.replace(
    marker,
    replacement,
    1,
)


# ---------------------------------------------------------------
# Add final index result to report.
# ---------------------------------------------------------------

if '"final_index_result":' not in text:
    marker = '''    "store_verification":
        store_verification,

    "checks":
'''

    replacement = '''    "store_verification":
        store_verification,

    "final_index_result":
        final_index_result,

    "checks":
'''

    if marker not in text:
        raise RuntimeError(
            "Final report insertion point was not found."
        )

    text = text.replace(
        marker,
        replacement,
        1,
    )


ast.parse(
    text,
    filename=str(path),
)

path.write_text(
    text,
    encoding="utf-8",
)

print(
    "PHASE 4.3B RESUMABLE OPTIMIZATION: PASS"
)
