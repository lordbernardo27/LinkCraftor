
from __future__ import annotations

from typing import Any, Dict


DEFAULT_FAILURE_HANDLING = {
    "continue_on_noncritical_failure": False,
    "store_failure_snapshot": True,
}


def resolve_failure_handling(
    template: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Resolve failure handling rules for an orchestration template.
    """

    rules = dict(DEFAULT_FAILURE_HANDLING)
    rules.update(template.get("failure_handling") or {})
    return rules


def should_continue_after_failure(
    step: Dict[str, Any],
    failure_rules: Dict[str, Any],
) -> bool:
    """
    Decide whether orchestration can continue after a step failure.
    """

    step_is_critical = step.get("critical", True)

    if step_is_critical:
        return False

    return bool(failure_rules.get("continue_on_noncritical_failure", False))
