"""Retirement guard for the original Phase 2.1.1 patch.

The original Universal Job Contract patch targeted the superseded pre-R1
contract and must never be executed against the corrected contract.

The complete historical patch source is preserved as a non-executable
``.retired_source.txt`` artifact and inside its retirement evidence directory.

This guard performs no patching, installation, import, runtime execution,
queue operation, worker operation, job creation, or production-data mutation.
"""

from __future__ import annotations

from typing import Final


RETIRED: Final[bool] = True

REPLACEMENT_CONTRACT_VERSION: Final[str] = (
    "universal_job_contract_v2.1.1-r1"
)

RETIREMENT_REASON: Final[str] = (
    "The original patch targets the superseded pre-R1 contract and could "
    "overwrite or reject the corrected R1 contract."
)


def explain_retirement() -> dict[str, object]:
    """Return retirement metadata without changing any file or runtime."""
    return {
        "retired": RETIRED,
        "replacement_contract_version": REPLACEMENT_CONTRACT_VERSION,
        "reason": RETIREMENT_REASON,
        "patch_performed": False,
        "installation_performed": False,
    }


def main() -> int:
    metadata = explain_retirement()

    print("")
    print("=" * 78)
    print("PHASE 2.1.1 ORIGINAL CONTRACT PATCH — RETIRED")
    print("=" * 78)
    print(metadata["reason"])
    print(
        "Replacement contract version: "
        + str(metadata["replacement_contract_version"])
    )
    print("No file was modified.")
    print("=" * 78)
    print("")

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
