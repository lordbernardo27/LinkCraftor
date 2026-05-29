
from __future__ import annotations

from typing import Any, Dict, List, Tuple


def validate_required_inputs(
    template: Dict[str, Any],
    inputs: Dict[str, Any],
) -> Tuple[bool, List[str]]:
    """
    Validate required template inputs before orchestration execution.
    """

    required_inputs = template.get("required_inputs") or []
    missing = []

    for key in required_inputs:
        value = inputs.get(key)
        if value is None or value == "":
            missing.append(str(key))

    return len(missing) == 0, missing
