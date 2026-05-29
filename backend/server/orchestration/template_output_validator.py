
from __future__ import annotations

from typing import Any, Dict, List, Tuple


def validate_required_outputs(
    template: Dict[str, Any],
    outputs: Dict[str, Any],
) -> Tuple[bool, List[str]]:
    """
    Validate orchestration template outputs
    after workflow execution.
    """

    required_outputs = template.get("outputs") or []
    missing = []

    for key in required_outputs:
        value = outputs.get(key)

        if value is None:
            missing.append(str(key))

    return len(missing) == 0, missing
