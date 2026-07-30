"""Retirement guard for the original Phase 2.1.1 installer.

The initial Universal Job Contract installer is historical and must not be
rerun. The installed contract has been corrected and advanced to revision R1.

The complete original installer source is preserved as a non-executable
``.retired_source.txt`` file in the repository root and in the corresponding
retirement evidence directory.

This guard performs no installation, patching, import, runtime operation,
queue operation, worker operation, or production-data mutation.
"""

from __future__ import annotations

from typing import Final


RETIRED: Final[bool] = True

REPLACED_BY_CONTRACT_VERSION: Final[str] = (
    "universal_job_contract_v2.1.1-r1"
)

RETIREMENT_REASON: Final[str] = (
    "The initial installer targets the superseded pre-R1 contract and "
    "must not overwrite the corrected certified contract."
)


def explain_retirement() -> dict[str, object]:
    """Return immutable retirement metadata without performing any work."""
    return {
        "retired": RETIRED,
        "replacement_contract_version": REPLACED_BY_CONTRACT_VERSION,
        "reason": RETIREMENT_REASON,
        "installation_performed": False,
    }


def main() -> int:
    metadata = explain_retirement()

    print("")
    print("=" * 78)
    print("PHASE 2.1.1 ORIGINAL INSTALLER — RETIRED")
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
