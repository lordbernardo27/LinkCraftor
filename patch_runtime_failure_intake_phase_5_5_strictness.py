from __future__ import annotations

from pathlib import Path


ROOT = Path.cwd()

TARGET = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_failure_intake.py"
)


source = TARGET.read_text(
    encoding="utf-8"
)


old_block = '''    failure_code = _required_text(
        metadata.get(
            "runtime_dispatch_error_type"
        ),
        name=(
            "metadata.runtime_dispatch_error_type"
        ),
    )
'''


new_block = '''    missing_failure_detail_keys = tuple(
        key
        for key
        in _RUNTIME_FAILURE_DETAIL_KEYS
        if key not in metadata
    )

    if missing_failure_detail_keys:
        raise RuntimeFailureValidationError(
            (
                "Runtime terminal failure evidence is incomplete."
            ),
            violations=tuple(
                (
                    "missing canonical Runtime failure detail: "
                    + key
                )
                for key
                in missing_failure_detail_keys
            ),
        )

    failure_code = _required_text(
        metadata.get(
            "runtime_dispatch_error_type"
        ),
        name=(
            "metadata.runtime_dispatch_error_type"
        ),
    )
'''


if old_block not in source:
    raise SystemExit(
        (
            "PATCH REFUSED: expected failure-code "
            "authority block not found."
        )
    )


source = source.replace(
    old_block,
    new_block,
    1,
)


TARGET.write_text(
    source,
    encoding="utf-8",
)


print()
print("=" * 120)
print("PHASE 5.5 — CORRECTIVE STRICTNESS PATCH INSTALLED")
print("=" * 120)
print(
    "Patched:",
    TARGET.relative_to(ROOT),
)
print(
    "Canonical Runtime failure-detail completeness "
    "is now mandatory."
)
print("Runtime production modified: False")
print("Orchestration production modified: False")
print("Phase 5.3 modified: False")
print("Phase 5.4 modified: False")
print("StageResult contract modified: False")
print("=" * 120)
