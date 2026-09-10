from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ChangeLevel(str, Enum):
    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"


@dataclass(frozen=True)
class ChangeClassification:
    architecture_id: str
    previous_version: str
    proposed_version: str
    level: ChangeLevel
    migration_required: bool
    owner_approval_required: bool
    sarb_review_required: bool
    reasons: List[str]


class ArchitectureChangeClassificationEngine:
    """
    Central LinkCraftor architecture change classifier.

    This engine classifies architecture changes as Patch, Minor, or Major and
    determines whether migration, owner approval, or SARB review is required.

    It does not execute migrations and does not silently approve changes.
    """

    SECURITY_ARCHITECTURE_ID = "platform-security-architecture"

    def classify(
        self,
        architecture_id: str,
        previous_version: str,
        proposed_version: str,
        *,
        breaking_change: bool = False,
        schema_change: bool = False,
        trust_boundary_change: bool = False,
        security_control_change: bool = False,
        dependency_change: bool = False,
        canonical_path_change: bool = False,
        documentation_only: bool = False,
    ) -> ChangeClassification:

        architecture_id = architecture_id.strip().lower()

        if not architecture_id:
            raise ValueError("architecture_id cannot be empty")

        self._validate_version(previous_version)
        self._validate_version(proposed_version)

        reasons: List[str] = []

        if breaking_change:
            reasons.append("breaking architecture change")

        if schema_change:
            reasons.append("architecture schema change")

        if trust_boundary_change:
            reasons.append("trust boundary change")

        if security_control_change:
            reasons.append("security control change")

        if dependency_change:
            reasons.append("architecture dependency change")

        if canonical_path_change:
            reasons.append("canonical architecture path change")

        if documentation_only:
            reasons.append("documentation-only change")

        previous_major, previous_minor, previous_patch = self._parse_version(
            previous_version
        )
        proposed_major, proposed_minor, proposed_patch = self._parse_version(
            proposed_version
        )

        if proposed_major < previous_major:
            raise ValueError("proposed version cannot reduce major version")

        if (
            proposed_major == previous_major
            and proposed_minor < previous_minor
        ):
            raise ValueError("proposed version cannot reduce minor version")

        if (
            proposed_major == previous_major
            and proposed_minor == previous_minor
            and proposed_patch < previous_patch
        ):
            raise ValueError("proposed version cannot reduce patch version")

        level = ChangeLevel.PATCH

        if proposed_major > previous_major:
            level = ChangeLevel.MAJOR
            reasons.append("major semantic version increment")

        elif proposed_minor > previous_minor:
            level = ChangeLevel.MINOR
            reasons.append("minor semantic version increment")

        elif proposed_patch > previous_patch:
            level = ChangeLevel.PATCH
            reasons.append("patch semantic version increment")

        if breaking_change or trust_boundary_change:
            level = ChangeLevel.MAJOR

        elif schema_change or security_control_change:
            if level != ChangeLevel.MAJOR:
                level = ChangeLevel.MINOR

        elif dependency_change or canonical_path_change:
            if level == ChangeLevel.PATCH:
                level = ChangeLevel.MINOR

        migration_required = (
            breaking_change
            or schema_change
            or trust_boundary_change
            or canonical_path_change
            or level == ChangeLevel.MAJOR
        )

        owner_approval_required = (
            level == ChangeLevel.MAJOR
            or trust_boundary_change
            or security_control_change
        )

        sarb_review_required = (
            architecture_id == self.SECURITY_ARCHITECTURE_ID
            and (
                level == ChangeLevel.MAJOR
                or trust_boundary_change
                or security_control_change
            )
        )

        return ChangeClassification(
            architecture_id=architecture_id,
            previous_version=previous_version,
            proposed_version=proposed_version,
            level=level,
            migration_required=migration_required,
            owner_approval_required=owner_approval_required,
            sarb_review_required=sarb_review_required,
            reasons=reasons,
        )

    @staticmethod
    def _validate_version(version: str) -> None:
        ArchitectureChangeClassificationEngine._parse_version(version)

    @staticmethod
    def _parse_version(version: str):
        parts = version.split(".")

        if len(parts) != 3:
            raise ValueError(
                "version must use semantic format MAJOR.MINOR.PATCH"
            )

        try:
            parsed = tuple(int(part) for part in parts)
        except ValueError as exc:
            raise ValueError(
                "version must contain numeric semantic version fields"
            ) from exc

        if any(part < 0 for part in parsed):
            raise ValueError("version values cannot be negative")

        return parsed


_default_engine: Optional[ArchitectureChangeClassificationEngine] = None


def get_change_classification_engine():
    global _default_engine

    if _default_engine is None:
        _default_engine = ArchitectureChangeClassificationEngine()

    return _default_engine
