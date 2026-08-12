"""Canonical Universal Job Metadata — Phase 2.1.4.

This module owns creation-time Universal Job metadata normalization.

Canonical Job Metadata is an immutable JSON-safe sidecar associated with
Universal Job creation. It is distinct from mutable orchestration/worker
metadata and is not embedded as a generic field inside the UniversalJob
contract.

This module performs no persistence, queue, Runtime Registration, worker,
ledger, filesystem, network, or process I/O.
"""

from __future__ import annotations

import hashlib
import json
import math
from types import MappingProxyType
from typing import Any, Final, Mapping


UNIVERSAL_JOB_METADATA_VERSION: Final[str] = (
    "universal_job_metadata_v2.1.4"
)

UNIVERSAL_JOB_METADATA_SCHEMA_VERSION: Final[str] = (
    "universal_job_metadata_schema_v1"
)


_EMPTY_METADATA: Final[Mapping[str, Any]] = MappingProxyType({})


class UniversalJobMetadataError(ValueError):
    """Raised when canonical Universal Job metadata is invalid."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        violations: tuple[str, ...] = (),
    ) -> None:
        super().__init__(message)

        self.code = str(
            code or "universal_job_metadata_error"
        )

        self.violations = tuple(
            str(item)
            for item in violations
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": "UniversalJobMetadataError",
            "code": self.code,
            "message": str(self),
            "violations": list(self.violations),
            "metadata_version": (
                UNIVERSAL_JOB_METADATA_VERSION
            ),
        }


def _validate_metadata_json_value(
    value: Any,
    *,
    path: str,
) -> None:
    """Validate one metadata value against the canonical JSON-safe boundary."""

    if value is None or isinstance(
        value,
        (
            str,
            int,
            bool,
        ),
    ):
        return

    if isinstance(
        value,
        float,
    ):
        if not math.isfinite(
            value
        ):
            raise UniversalJobMetadataError(
                f"{path} contains a non-finite float.",
                code="non_json_metadata",
                violations=(
                    f"{path} must contain only finite JSON values",
                ),
            )

        return

    if isinstance(
        value,
        Mapping,
    ):
        for key, item in value.items():
            if not isinstance(
                key,
                str,
            ):
                raise UniversalJobMetadataError(
                    f"{path} contains a non-string mapping key.",
                    code="non_json_metadata",
                    violations=(
                        f"{path} mapping keys must be strings",
                    ),
                )

            _validate_metadata_json_value(
                item,
                path=f"{path}.{key}",
            )

        return

    if isinstance(
        value,
        (
            list,
            tuple,
        ),
    ):
        for index, item in enumerate(
            value
        ):
            _validate_metadata_json_value(
                item,
                path=f"{path}[{index}]",
            )

        return

    raise UniversalJobMetadataError(
        (
            f"{path} contains unsupported type "
            f"{type(value).__name__}."
        ),
        code="non_json_metadata",
        violations=(
            f"{path} must be JSON-safe",
        ),
    )


def _freeze_metadata_json(
    value: Any,
) -> Any:
    """Recursively freeze validated metadata into immutable structures."""

    if isinstance(
        value,
        Mapping,
    ):
        return MappingProxyType(
            {
                key: _freeze_metadata_json(
                    item
                )
                for key, item in value.items()
            }
        )

    if isinstance(
        value,
        (
            list,
            tuple,
        ),
    ):
        return tuple(
            _freeze_metadata_json(
                item
            )
            for item in value
        )

    return value


def _thaw_metadata_json(
    value: Any,
) -> Any:
    """Recursively convert canonical metadata containers to JSON-native ones."""

    if isinstance(
        value,
        Mapping,
    ):
        return {
            key: _thaw_metadata_json(
                item
            )
            for key, item in value.items()
        }

    if isinstance(
        value,
        tuple,
    ):
        return [
            _thaw_metadata_json(
                item
            )
            for item in value
        ]

    if isinstance(
        value,
        list,
    ):
        return [
            _thaw_metadata_json(
                item
            )
            for item in value
        ]

    return value


def thaw_universal_job_metadata(
    value: Mapping[str, Any],
) -> dict[str, Any]:
    """Return a mutable JSON-compatible copy of canonical metadata."""

    if not isinstance(
        value,
        Mapping,
    ):
        raise UniversalJobMetadataError(
            "metadata must be a mapping.",
            code="invalid_metadata",
            violations=(
                "metadata must be a mapping",
            ),
        )

    return _thaw_metadata_json(
        value
    )


def normalize_universal_job_metadata(
    value: Any = None,
) -> Mapping[str, Any]:
    """Validate and freeze creation-time Universal Job metadata."""

    if value is None:
        return _EMPTY_METADATA

    if not isinstance(
        value,
        Mapping,
    ):
        raise UniversalJobMetadataError(
            "metadata must be a mapping.",
            code="invalid_metadata",
            violations=(
                "metadata must be a mapping",
            ),
        )

    _validate_metadata_json_value(
        value,
        path="metadata",
    )

    serializable_value = (
        _thaw_metadata_json(
            value
        )
    )

    try:
        json.dumps(
            serializable_value,
            ensure_ascii=False,
            allow_nan=False,
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise UniversalJobMetadataError(
            "metadata is not JSON serializable.",
            code="non_json_metadata",
            violations=(
                str(exc),
            ),
        ) from exc

    return _freeze_metadata_json(
        serializable_value
    )


def is_canonical_universal_job_metadata(
    value: Any,
) -> bool:
    """Return True when value can serve as canonical Job Metadata."""

    if not isinstance(
        value,
        Mapping,
    ):
        return False

    try:
        normalized = normalize_universal_job_metadata(
            value
        )
    except UniversalJobMetadataError:
        return False

    return (
        thaw_universal_job_metadata(
            normalized
        )
        == thaw_universal_job_metadata(
            value
        )
    )


def universal_job_metadata_fingerprint(
    value: Mapping[str, Any],
) -> str:
    """Return the stable SHA-256 fingerprint of canonical metadata content."""

    normalized = normalize_universal_job_metadata(
        value
    )

    canonical_json = json.dumps(
        thaw_universal_job_metadata(
            normalized
        ),
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(
            ",",
            ":",
        ),
    )

    return hashlib.sha256(
        canonical_json.encode(
            "utf-8"
        )
    ).hexdigest()


def build_universal_job_metadata_envelope(
    value: Any = None,
) -> Mapping[str, Any]:
    """Build an immutable metadata sidecar envelope for creation results."""

    metadata = normalize_universal_job_metadata(
        value
    )

    return MappingProxyType(
        {
            "schema_version": (
                UNIVERSAL_JOB_METADATA_SCHEMA_VERSION
            ),
            "metadata_version": (
                UNIVERSAL_JOB_METADATA_VERSION
            ),
            "metadata": metadata,
            "metadata_fingerprint": (
                universal_job_metadata_fingerprint(
                    metadata
                )
            ),
        }
    )


def explain_universal_job_metadata_v1() -> dict[str, Any]:
    """Return the canonical Phase 2.1.4 metadata design."""

    return {
        "phase": "2.1.4",
        "component": "Universal Job Metadata",
        "metadata_version": (
            UNIVERSAL_JOB_METADATA_VERSION
        ),
        "schema_version": (
            UNIVERSAL_JOB_METADATA_SCHEMA_VERSION
        ),
        "classification": (
            "immutable creation-time metadata sidecar"
        ),
        "canonical_location": (
            "UniversalJobCreationResult sidecar"
        ),
        "embedded_in_universal_job_contract": False,
        "mutable_orchestration_metadata": False,
        "responsibilities": [
            "validate creation-time metadata",
            "enforce JSON-safe metadata values",
            "freeze metadata immutably",
            "thaw metadata for serialization",
            "fingerprint canonical metadata content",
            "build the canonical metadata sidecar envelope",
        ],
        "boundaries": [
            "not UniversalJob contract state",
            "not payload content",
            "not Runtime Registration metadata",
            "not orchestration worker metadata",
            "not status-transition metadata",
            "not retry-state metadata",
        ],
        "prohibitions": [
            "no persistence writes",
            "no queue writes",
            "no Runtime Registration loading",
            "no worker execution",
            "no ledger writes",
            "no filesystem I/O",
            "no network I/O",
        ],
    }


__all__ = [
    "UNIVERSAL_JOB_METADATA_VERSION",
    "UNIVERSAL_JOB_METADATA_SCHEMA_VERSION",
    "UniversalJobMetadataError",
    "normalize_universal_job_metadata",
    "thaw_universal_job_metadata",
    "is_canonical_universal_job_metadata",
    "universal_job_metadata_fingerprint",
    "build_universal_job_metadata_envelope",
    "explain_universal_job_metadata_v1",
]