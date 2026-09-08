from __future__ import annotations

from pathlib import Path


ROOT = Path.cwd()

TARGET = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_completion_intake.py"
)


source = TARGET.read_text(
    encoding="utf-8"
)


# =========================================================================
# PATCH 1 — COMPLETED event must be RUNNING -> COMPLETED
# =========================================================================

old_completion = '''        if (
            _status_text(
                event.get(
                    "new_status"
                )
            )
            == "completed"
        ):
            completion_index = index
            break
'''

new_completion = '''        if (
            _status_text(
                event.get(
                    "new_status"
                )
            )
            == "completed"
        ):
            if (
                _status_text(
                    event.get(
                        "old_status"
                    )
                )
                != "running"
            ):
                raise RuntimeCompletionValidationError(
                    (
                        "Selected COMPLETED event must represent "
                        "RUNNING -> COMPLETED."
                    ),
                    violations=(
                        "completion transition must be running -> completed",
                    ),
                )

            completion_index = index
            break
'''


if old_completion not in source:
    raise SystemExit(
        "PATCH REFUSED: completion transition block not found."
    )


source = source.replace(
    old_completion,
    new_completion,
    1,
)


# =========================================================================
# PATCH 2 — selected attempt start must be QUEUED -> RUNNING
# =========================================================================

old_running = '''        if (
            _status_text(
                event.get(
                    "new_status"
                )
            )
            == "running"
        ):
            started_index = index
            break
'''

new_running = '''        if (
            _status_text(
                event.get(
                    "new_status"
                )
            )
            == "running"
        ):
            if (
                _status_text(
                    event.get(
                        "old_status"
                    )
                )
                != "queued"
            ):
                raise RuntimeCompletionValidationError(
                    (
                        "Selected RUNNING event must represent "
                        "QUEUED -> RUNNING."
                    ),
                    violations=(
                        "started transition must be queued -> running",
                    ),
                )

            started_index = index
            break
'''


if old_running not in source:
    raise SystemExit(
        "PATCH REFUSED: running transition block not found."
    )


source = source.replace(
    old_running,
    new_running,
    1,
)


# =========================================================================
# PATCH 3 — timestamp ordering belongs to Phase 5.4 intake validation
# =========================================================================

old_timestamp_block = '''    finished_at = _timestamp_text(
        completion_event.get(
            "created_at"
        ),
        name="completion_event.created_at",
    )

    result_reference = (
'''

new_timestamp_block = '''    finished_at = _timestamp_text(
        completion_event.get(
            "created_at"
        ),
        name="completion_event.created_at",
    )

    try:
        started_dt = datetime.fromisoformat(
            started_at.replace(
                "Z",
                "+00:00",
            )
        )

        finished_dt = datetime.fromisoformat(
            finished_at.replace(
                "Z",
                "+00:00",
            )
        )

    except ValueError as exc:
        raise RuntimeCompletionValidationError(
            "Runtime completion event timestamp is invalid.",
            violations=(
                "invalid Runtime completion timestamp",
            ),
        ) from exc

    if (
        started_dt.tzinfo is not None
        and finished_dt.tzinfo is not None
        and finished_dt < started_dt
    ):
        raise RuntimeCompletionValidationError(
            "Runtime completion timestamp ordering is invalid.",
            violations=(
                "finished_at cannot be earlier than started_at",
            ),
        )

    result_reference = (
'''


if old_timestamp_block not in source:
    raise SystemExit(
        "PATCH REFUSED: timestamp block not found."
    )


source = source.replace(
    old_timestamp_block,
    new_timestamp_block,
    1,
)


TARGET.write_text(
    source,
    encoding="utf-8",
)


print()
print("=" * 120)
print("PHASE 5.4 CORRECTIVE PATCH INSTALLED")
print("=" * 120)
print(
    "Patched:",
    TARGET.relative_to(ROOT),
)
print("Fix 1: COMPLETED requires RUNNING -> COMPLETED")
print("Fix 2: RUNNING attempt requires QUEUED -> RUNNING")
print("Fix 3: timestamp ordering validated inside Phase 5.4")
print("Runtime production modified: False")
print("Orchestration production modified: False")
print("Phase 5.3 modified: False")
print("StageResult contract modified: False")
print("=" * 120)
