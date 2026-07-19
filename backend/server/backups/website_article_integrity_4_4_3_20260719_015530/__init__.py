"""Website Article Integrity Phase 4.4 package."""

from .website_article_structure_validator import (
    PHASE as STRUCTURE_PHASE,
    PHASE_NAME as STRUCTURE_PHASE_NAME,
    VALIDATOR_VERSION as STRUCTURE_VALIDATOR_VERSION,
    StructureValidationResult,
    run_structure_validation,
    validate_article_structure,
)

from .website_article_component_validator import (
    PHASE as COMPONENT_PHASE,
    PHASE_NAME as COMPONENT_PHASE_NAME,
    VALIDATOR_VERSION as COMPONENT_VALIDATOR_VERSION,
    ComponentValidationResult,
    run_component_validation,
    validate_required_components,
)

__all__ = [
    "STRUCTURE_PHASE",
    "STRUCTURE_PHASE_NAME",
    "STRUCTURE_VALIDATOR_VERSION",
    "StructureValidationResult",
    "run_structure_validation",
    "validate_article_structure",
    "COMPONENT_PHASE",
    "COMPONENT_PHASE_NAME",
    "COMPONENT_VALIDATOR_VERSION",
    "ComponentValidationResult",
    "run_component_validation",
    "validate_required_components",
]
