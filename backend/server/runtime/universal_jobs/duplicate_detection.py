from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Optional


UNIVERSAL_JOB_DUPLICATE_DETECTION_VERSION = (
    "universal_job_duplicate_detection_v2.1.11"
)

UNIVERSAL_JOB_DUPLICATE_DETECTION_SCHEMA_VERSION = (
    "universal_job_duplicate_detection_schema_v1"
)


class UniversalJobDuplicateDetectionError(
    ValueError
):
    """Raised for structurally invalid duplicate-comparison input."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "invalid_duplicate_detection_input",
    ) -> None:

        super().__init__(
            message
        )

        self.code = str(
            code
        )


class UniversalJobDuplicateDetectionStatus(
    str,
    Enum,
):
    DUPLICATE = "duplicate"
    NOT_DUPLICATE = "not_duplicate"
    NOT_DETECTABLE = "not_detectable"


class UniversalJobDuplicateDetectionMethod(
    str,
    Enum,
):
    SCOPE_MISMATCH = "scope_mismatch"
    EXPLICIT_IDEMPOTENCY_KEY = (
        "explicit_idempotency_key"
    )
    IDEMPOTENCY_FIELDS = "idempotency_fields"
    NO_COMPARISON_SIGNAL = "no_comparison_signal"


def _clean_required_text(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise UniversalJobDuplicateDetectionError(
            f"{field_name} must be a string.",
            code=(
                "invalid_"
                + field_name
            ),
        )

    normalized = value.strip()

    if not normalized:
        raise UniversalJobDuplicateDetectionError(
            f"{field_name} is required.",
            code=(
                "missing_"
                + field_name
            ),
        )

    return normalized


def _clean_optional_text(
    value: Any,
    *,
    field_name: str,
) -> Optional[str]:

    if value is None:
        return None

    if not isinstance(
        value,
        str,
    ):
        raise UniversalJobDuplicateDetectionError(
            (
                f"{field_name} must be "
                "a string or None."
            ),
            code=(
                "invalid_"
                + field_name
            ),
        )

    normalized = value.strip()

    return (
        normalized
        if normalized
        else None
    )


def _normalize_mapping(
    value: Any,
    *,
    field_name: str,
) -> Mapping[str, Any]:

    if value is None:
        return MappingProxyType(
            {}
        )

    if not isinstance(
        value,
        Mapping,
    ):
        raise UniversalJobDuplicateDetectionError(
            f"{field_name} must be a mapping.",
            code=(
                "invalid_"
                + field_name
            ),
        )

    return MappingProxyType(
        dict(
            value
        )
    )


def _normalize_idempotency_fields(
    value: Optional[
        Iterable[Any]
    ],
) -> tuple[str, ...]:

    if value is None:
        return ()

    if isinstance(
        value,
        (
            str,
            bytes,
            Mapping,
        ),
    ):
        raise UniversalJobDuplicateDetectionError(
            (
                "idempotency_fields must be "
                "an iterable of strings."
            ),
            code="invalid_idempotency_fields",
        )

    try:
        values = list(
            value
        )

    except TypeError as exc:
        raise UniversalJobDuplicateDetectionError(
            (
                "idempotency_fields must be "
                "an iterable of strings."
            ),
            code="invalid_idempotency_fields",
        ) from exc

    normalized: dict[
        str,
        None,
    ] = {}

    for item in values:

        if not isinstance(
            item,
            str,
        ):
            raise UniversalJobDuplicateDetectionError(
                (
                    "idempotency_fields members "
                    "must be strings."
                ),
                code="invalid_idempotency_fields",
            )

        field = item.strip()

        if not field:
            raise UniversalJobDuplicateDetectionError(
                (
                    "idempotency_fields members "
                    "must not be blank."
                ),
                code="invalid_idempotency_fields",
            )

        normalized[
            field
        ] = None

    return tuple(
        normalized
    )


def _freeze_json_value(
    value: Any,
) -> Any:
    """
    Validate that a comparison-field value is JSON-safe and
    return a detached canonical value.
    """

    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            ensure_ascii=False,
            allow_nan=False,
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise UniversalJobDuplicateDetectionError(
            (
                "idempotency comparison field "
                "contains a non-JSON-safe value."
            ),
            code="invalid_idempotency_field_value",
        ) from exc

    return json.loads(
        encoded
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalJobDuplicateCandidate:
    """
    Pure duplicate-comparison view.

    `job` represents canonical Universal Job fields.
    `payload` represents creation/runtime payload fields.
    """

    workspace_id: str
    job_type: str
    idempotency_key: Optional[str]
    job: Mapping[str, Any]
    payload: Mapping[str, Any]

    @classmethod
    def from_values(
        cls,
        *,
        workspace_id: Any,
        job_type: Any,
        idempotency_key: Any = None,
        job: Any = None,
        payload: Any = None,
    ) -> "UniversalJobDuplicateCandidate":

        return cls(
            workspace_id=(
                _clean_required_text(
                    workspace_id,
                    field_name="workspace_id",
                )
            ),
            job_type=(
                _clean_required_text(
                    job_type,
                    field_name="job_type",
                )
            ),
            idempotency_key=(
                _clean_optional_text(
                    idempotency_key,
                    field_name="idempotency_key",
                )
            ),
            job=_normalize_mapping(
                job,
                field_name="job",
            ),
            payload=_normalize_mapping(
                payload,
                field_name="payload",
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalJobDuplicateSignature:
    workspace_id: str
    job_type: str
    fields: tuple[str, ...]
    values: tuple[Any, ...]
    signature: str

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version": (
                UNIVERSAL_JOB_DUPLICATE_DETECTION_SCHEMA_VERSION
            ),
            "workspace_id":
                self.workspace_id,
            "job_type":
                self.job_type,
            "fields":
                list(
                    self.fields
                ),
            "values":
                list(
                    self.values
                ),
            "signature":
                self.signature,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalJobDuplicateDetectionResult:
    status: UniversalJobDuplicateDetectionStatus
    method: UniversalJobDuplicateDetectionMethod
    comparable: bool
    is_duplicate: bool
    reason: str
    signature_a: Optional[str] = None
    signature_b: Optional[str] = None

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version": (
                UNIVERSAL_JOB_DUPLICATE_DETECTION_SCHEMA_VERSION
            ),
            "status":
                self.status.value,
            "method":
                self.method.value,
            "comparable":
                self.comparable,
            "is_duplicate":
                self.is_duplicate,
            "reason":
                self.reason,
            "signature_a":
                self.signature_a,
            "signature_b":
                self.signature_b,
        }


def _resolve_field(
    candidate: UniversalJobDuplicateCandidate,
    field_name: str,
) -> tuple[
    bool,
    Any,
]:
    """
    Resolve registered idempotency fields.

    Resolution order:
    1. canonical duplicate scope fields
    2. canonical job mapping
    3. payload mapping

    Exact field names are used. No aliases are invented.
    """

    if field_name == "workspace_id":
        return (
            True,
            candidate.workspace_id,
        )

    if field_name == "job_type":
        return (
            True,
            candidate.job_type,
        )

    if field_name == "idempotency_key":
        return (
            True,
            candidate.idempotency_key,
        )

    if field_name in candidate.job:
        return (
            True,
            candidate.job[
                field_name
            ],
        )

    if field_name in candidate.payload:
        return (
            True,
            candidate.payload[
                field_name
            ],
        )

    return (
        False,
        None,
    )


def build_universal_job_duplicate_signature(
    candidate: UniversalJobDuplicateCandidate,
    *,
    idempotency_fields: Optional[
        Iterable[Any]
    ] = None,
) -> Optional[
    UniversalJobDuplicateSignature
]:
    """
    Build a dedicated logical-duplicate signature from registered
    idempotency_fields.

    The signature is intentionally separate from Universal Job identity,
    contract, and content fingerprints.
    """

    if not isinstance(
        candidate,
        UniversalJobDuplicateCandidate,
    ):
        raise UniversalJobDuplicateDetectionError(
            (
                "candidate must be "
                "UniversalJobDuplicateCandidate."
            ),
            code="invalid_duplicate_candidate",
        )

    fields = (
        _normalize_idempotency_fields(
            idempotency_fields
        )
    )

    if not fields:
        return None

    values = []

    for field_name in fields:

        found, value = _resolve_field(
            candidate,
            field_name,
        )

        if not found:
            return None

        values.append(
            _freeze_json_value(
                value
            )
        )

    material = {
        "schema_version": (
            UNIVERSAL_JOB_DUPLICATE_DETECTION_SCHEMA_VERSION
        ),
        "workspace_id":
            candidate.workspace_id,
        "job_type":
            candidate.job_type,
        "fields":
            list(
                fields
            ),
        "values":
            values,
    }

    compact = json.dumps(
        material,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
        allow_nan=False,
    )

    signature = (
        "sha256:"
        + hashlib.sha256(
            compact.encode(
                "utf-8"
            )
        ).hexdigest()
    )

    return UniversalJobDuplicateSignature(
        workspace_id=(
            candidate.workspace_id
        ),
        job_type=(
            candidate.job_type
        ),
        fields=fields,
        values=tuple(
            values
        ),
        signature=signature,
    )


def detect_universal_job_duplicate(
    candidate_a: UniversalJobDuplicateCandidate,
    candidate_b: UniversalJobDuplicateCandidate,
    *,
    idempotency_fields: Optional[
        Iterable[Any]
    ] = None,
) -> UniversalJobDuplicateDetectionResult:
    """
    Compare two logical Universal Job candidates.

    This function only reports duplicate-detection facts.
    It never performs persistence, queue access, job lookup,
    suppression, reuse, rejection, cancellation, or mutation.
    """

    if not isinstance(
        candidate_a,
        UniversalJobDuplicateCandidate,
    ):
        raise UniversalJobDuplicateDetectionError(
            (
                "candidate_a must be "
                "UniversalJobDuplicateCandidate."
            ),
            code="invalid_duplicate_candidate",
        )

    if not isinstance(
        candidate_b,
        UniversalJobDuplicateCandidate,
    ):
        raise UniversalJobDuplicateDetectionError(
            (
                "candidate_b must be "
                "UniversalJobDuplicateCandidate."
            ),
            code="invalid_duplicate_candidate",
        )

    # Duplicate identity is never global.
    if (
        candidate_a.workspace_id
        != candidate_b.workspace_id
        or
        candidate_a.job_type
        != candidate_b.job_type
    ):
        return UniversalJobDuplicateDetectionResult(
            status=(
                UniversalJobDuplicateDetectionStatus.NOT_DUPLICATE
            ),
            method=(
                UniversalJobDuplicateDetectionMethod.SCOPE_MISMATCH
            ),
            comparable=True,
            is_duplicate=False,
            reason=(
                "workspace_id and job_type "
                "duplicate scope does not match."
            ),
        )

    key_a = (
        candidate_a.idempotency_key
    )

    key_b = (
        candidate_b.idempotency_key
    )

    # Explicit caller identity always wins over derived fields.
    if (
        key_a is not None
        or key_b is not None
    ):

        if (
            key_a is not None
            and key_b is not None
            and key_a == key_b
        ):
            return UniversalJobDuplicateDetectionResult(
                status=(
                    UniversalJobDuplicateDetectionStatus.DUPLICATE
                ),
                method=(
                    UniversalJobDuplicateDetectionMethod
                    .EXPLICIT_IDEMPOTENCY_KEY
                ),
                comparable=True,
                is_duplicate=True,
                reason=(
                    "same duplicate scope and same "
                    "explicit idempotency_key."
                ),
            )

        return UniversalJobDuplicateDetectionResult(
            status=(
                UniversalJobDuplicateDetectionStatus.NOT_DUPLICATE
            ),
            method=(
                UniversalJobDuplicateDetectionMethod
                .EXPLICIT_IDEMPOTENCY_KEY
            ),
            comparable=True,
            is_duplicate=False,
            reason=(
                "same duplicate scope but explicit "
                "idempotency keys do not match."
            ),
        )

    fields = (
        _normalize_idempotency_fields(
            idempotency_fields
        )
    )

    if not fields:
        return UniversalJobDuplicateDetectionResult(
            status=(
                UniversalJobDuplicateDetectionStatus.NOT_DETECTABLE
            ),
            method=(
                UniversalJobDuplicateDetectionMethod
                .NO_COMPARISON_SIGNAL
            ),
            comparable=False,
            is_duplicate=False,
            reason=(
                "neither candidate has an explicit "
                "idempotency_key and no idempotency_fields "
                "were supplied."
            ),
        )

    signature_a = (
        build_universal_job_duplicate_signature(
            candidate_a,
            idempotency_fields=fields,
        )
    )

    signature_b = (
        build_universal_job_duplicate_signature(
            candidate_b,
            idempotency_fields=fields,
        )
    )

    if (
        signature_a is None
        or signature_b is None
    ):
        return UniversalJobDuplicateDetectionResult(
            status=(
                UniversalJobDuplicateDetectionStatus.NOT_DETECTABLE
            ),
            method=(
                UniversalJobDuplicateDetectionMethod
                .IDEMPOTENCY_FIELDS
            ),
            comparable=False,
            is_duplicate=False,
            reason=(
                "one or more registered idempotency_fields "
                "could not be resolved for both candidates."
            ),
            signature_a=(
                signature_a.signature
                if signature_a is not None
                else None
            ),
            signature_b=(
                signature_b.signature
                if signature_b is not None
                else None
            ),
        )

    duplicate = (
        signature_a.signature
        == signature_b.signature
    )

    return UniversalJobDuplicateDetectionResult(
        status=(
            UniversalJobDuplicateDetectionStatus.DUPLICATE
            if duplicate
            else UniversalJobDuplicateDetectionStatus.NOT_DUPLICATE
        ),
        method=(
            UniversalJobDuplicateDetectionMethod.IDEMPOTENCY_FIELDS
        ),
        comparable=True,
        is_duplicate=duplicate,
        reason=(
            (
                "derived idempotency-field signatures match."
            )
            if duplicate
            else (
                "derived idempotency-field signatures differ."
            )
        ),
        signature_a=(
            signature_a.signature
        ),
        signature_b=(
            signature_b.signature
        ),
    )


def explain_universal_job_duplicate_detection_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "2.1.11",
            "component":
                "Universal Job Duplicate Detection",
            "version":
                UNIVERSAL_JOB_DUPLICATE_DETECTION_VERSION,
            "schema_version":
                UNIVERSAL_JOB_DUPLICATE_DETECTION_SCHEMA_VERSION,
            "duplicate_scope": (
                "workspace_id",
                "job_type",
            ),
            "signal_precedence": (
                "explicit idempotency_key",
                "registered idempotency_fields",
                "not detectable",
            ),
            "fingerprint_policy": (
                "uses a dedicated duplicate signature",
                (
                    "does not use Universal Job "
                    "identity_fingerprint"
                ),
                (
                    "does not use Universal Job "
                    "contract_fingerprint"
                ),
                (
                    "does not use Universal Job "
                    "content_fingerprint"
                ),
            ),
            "result_states": (
                "duplicate",
                "not_duplicate",
                "not_detectable",
            ),
            "prohibitions": (
                "does not load jobs",
                "does not search a queue",
                "does not search a job store",
                "does not persist",
                "does not enqueue",
                "does not suppress duplicates",
                "does not reuse jobs",
                "does not reject jobs",
                "does not merge jobs",
                "does not cancel jobs",
                "does not mutate candidates",
                (
                    "does not perform Phase 2.1.12 "
                    "duplicate handling"
                ),
            ),
        }
    )


__all__ = [
    "UNIVERSAL_JOB_DUPLICATE_DETECTION_VERSION",
    "UNIVERSAL_JOB_DUPLICATE_DETECTION_SCHEMA_VERSION",
    "UniversalJobDuplicateDetectionError",
    "UniversalJobDuplicateDetectionStatus",
    "UniversalJobDuplicateDetectionMethod",
    "UniversalJobDuplicateCandidate",
    "UniversalJobDuplicateSignature",
    "UniversalJobDuplicateDetectionResult",
    "build_universal_job_duplicate_signature",
    "detect_universal_job_duplicate",
    "explain_universal_job_duplicate_detection_v1",
]
