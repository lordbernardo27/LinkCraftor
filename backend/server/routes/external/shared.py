# backend/server/routes/external/shared.py
from __future__ import annotations

"""
Shared utilities for the External Intelligence route package.

Phase 1.16 only creates the package structure.
Actual helpers/constants will be migrated gradually from:

    retired legacy external router

Do not delete the legacy external router yet.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = PROJECT_ROOT / "backend" / "data"

AUTO_PATH = DATA_DIR / "global_external_auto.json"
MANUAL_PATH = DATA_DIR / "global_external_manual.json"
BLACKLIST_PATH = DATA_DIR / "blacklist_url.json"
AUDIT_PATH = DATA_DIR / "owner_audit_log.jsonl"
SOURCES_PATH = DATA_DIR / "owner_sources.json"
SNAPSHOT_DIR = DATA_DIR / "import_snapshots"
IMPORT_RUNS_INDEX_PATH = DATA_DIR / "import_runs_index.json"
