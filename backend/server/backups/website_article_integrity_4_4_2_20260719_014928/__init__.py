"""Website Article Integrity Phase 4.4 package."""

from .website_article_structure_validator import (
    PHASE,
    PHASE_NAME,
    VALIDATOR_VERSION,
    StructureValidationResult,
    run_structure_validation,
    validate_article_structure,
)

__all__ = [
    "PHASE",
    "PHASE_NAME",
    "VALIDATOR_VERSION",
    "StructureValidationResult",
    "run_structure_validation",
    "validate_article_structure",
]
