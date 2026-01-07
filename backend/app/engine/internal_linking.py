# backend/app/engine/internal_linking.py
from __future__ import annotations
from typing import Dict, Any

def run_internal(html: str = "", text: str = "") -> Dict[str, Any]:
    """
    Return deterministic demo results so the UI can render.
    Replace with the HELIX/RB2 logic later.
    """
    sample_anchor = "content strategy"
    return {
        "recommended": [
            {
                "anchor": sample_anchor,
                "target_title": "Content Strategy: The Complete Guide",
                "target_url": "https://example.com/content-strategy",
                "score": 0.92,
                "kind": "published",
            }
        ],
        "optional": [
            {
                "anchor": sample_anchor,
                "target_title": "What is Content Strategy",
                "target_url": "",
                "score": 0.64,
                "kind": "draft",
            }
        ],
    }
