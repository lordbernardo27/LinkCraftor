# backend/app/services/helix.py
from __future__ import annotations

"""
HELIX_AUTH service layer.

Purpose:
- External authority phrase detection only.
- Produces external/green candidates only.
- Does not use RB2 target pools.
- Does not produce internal/strong or semantic/optional buckets.
- External URLs are attached later by EXT_RESOLVER.
"""

from typing import Any, Dict


def run_helix(
    text: str,
    published_topics: list | None = None,
    draft_topics: list | None = None,
    phase: str = "prepublish",
    buckets: dict | None = None,
) -> Dict[str, Any]:
    """
    Compatibility wrapper.

    Old RB2-style HELIX logic has been removed.
    HELIX_AUTH is now reserved for external authority phrase detection only.
    """

    return {
        "ok": True,
        "external": [],
        "hidden": [],
        "meta": {
            "engine": "HELIX_AUTH",
            "phase": phase,
            "status": "placeholder_independent_service",
            "notes": (
                "Old RB2-style HELIX logic removed. "
                "HELIX_AUTH is independent and reserved for external green highlights only."
            ),
        },
    }
