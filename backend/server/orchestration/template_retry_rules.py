
from __future__ import annotations

from typing import Any, Dict


DEFAULT_RETRY_POLICY = {
    "max_retries": 3,
    "retry_delay_seconds": 5,
}


def resolve_retry_policy(
    template: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Resolve retry rules for an orchestration template.
    """

    policy = dict(DEFAULT_RETRY_POLICY)
    policy.update(template.get("retry_policy") or {})

    policy["max_retries"] = int(policy.get("max_retries", 3) or 3)
    policy["retry_delay_seconds"] = int(policy.get("retry_delay_seconds", 5) or 5)

    return policy


def should_retry_step(
    step: Dict[str, Any],
    attempt_count: int,
    retry_policy: Dict[str, Any],
) -> bool:
    """
    Decide whether a failed step should retry.
    """

    if step.get("retryable", True) is False:
        return False

    max_retries = int(retry_policy.get("max_retries", 3) or 3)

    return attempt_count < max_retries
