# backend/app/engine/external_linking.py
from typing import Any, Dict, Optional, List

def run_external_v2(text: str, settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Minimal placeholder for External V2 local suggestions.
    Return shape mirrors the frontend expectation in app.js:
      { suggestions: [...], meta: { passed, filtered } }
    """
    return {"suggestions": [], "meta": {"passed": 0, "filtered": 0}}
