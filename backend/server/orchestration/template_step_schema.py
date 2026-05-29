
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class OrchestrationStep:
    """
    Standard orchestration workflow step schema.
    """

    step_id: str
    worker: str
    action: str

    execution_order: int = 0

    retryable: bool = True
    critical: bool = True

    timeout_seconds: int = 300

    depends_on: List[str] = field(default_factory=list)

    description: Optional[str] = None
