from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


UNIVERSAL_QUEUE_INFRASTRUCTURE_CERTIFICATION_VERSION = (
    "universal_queue_infrastructure_certification_v3.1.15"
)

UNIVERSAL_QUEUE_INFRASTRUCTURE_MANIFEST_SCHEMA_VERSION = (
    "universal_queue_infrastructure_manifest_schema_v1"
)

UNIVERSAL_QUEUE_INFRASTRUCTURE_CERTIFICATION_SCHEMA_VERSION = (
    "universal_queue_infrastructure_certification_schema_v1"
)


UNIVERSAL_QUEUE_PHASE_ORDER = (
    "3.1.1",
    "3.1.2",
    "3.1.3",
    "3.1.4",
    "3.1.5",
    "3.1.6",
    "3.1.7",
    "3.1.8",
    "3.1.9",
    "3.1.10",
    "3.1.11",
    "3.1.12",
    "3.1.13",
    "3.1.14",
)


UNIVERSAL_QUEUE_AUTHORITY_NAMES = MappingProxyType(
    {
        "3.1.1": "Queue Creation",
        "3.1.2": "Queue Scheduling",
        "3.1.3": "Queue Prioritization",
        "3.1.4": "Queue Routing",
        "3.1.5": "Queue Balancing",
        "3.1.6": "Queue Partitioning",
        "3.1.7": "Queue Recovery",
        "3.1.8": "Dead Letter Queues",
        "3.1.9": "Queue Cleanup",
        "3.1.10": "Queue Backpressure",
        "3.1.11": "Queue Capacity Limits",
        "3.1.12": "Queue Fairness",
        "3.1.13": "Queue Rate Limiting",
        "3.1.14": "Queue Deduplication",
    }
)


UNIVERSAL_QUEUE_AUTHORITY_FILES = MappingProxyType(
    {
        "3.1.1": "creation.py",
        "3.1.2": "scheduling.py",
        "3.1.3": "prioritization.py",
        "3.1.4": "routing.py",
        "3.1.5": "balancing.py",
        "3.1.6": "partitioning.py",
        "3.1.7": "recovery.py",
        "3.1.8": "dead_letter.py",
        "3.1.9": "cleanup.py",
        "3.1.10": "backpressure.py",
        "3.1.11": "capacity_limits.py",
        "3.1.12": "fairness.py",
        "3.1.13": "rate_limiting.py",
        "3.1.14": "deduplication.py",
    }
)


UNIVERSAL_QUEUE_AUTHORITY_AST_SHA256 = MappingProxyType(
    {
        "3.1.1":
            "5ED908A9AFB9D102915EC1A2C8DA1D4B97D8A6CC2FDDCE3CB2EDF4E6159590BD",

        "3.1.2":
            "61563B1AA20A9C419A7B9BADC7AC9A7632835E2C8FC04AF42A9A86860B6CA0AC",

        "3.1.3":
            "C3C34C37CB6D30B5BCB22C07B2E26F825F97D7E76DEEDC6476954522B8211680",

        "3.1.4":
            "99AEEA931EC1DC4533CEE7A4E0BC07EA01FF120792A3BCC92C41CE9C253E6502",

        "3.1.5":
            "6811E385C802B743411534DBEE00BB65C51A59353A6491327EBFB230AB506CD5",

        "3.1.6":
            "E01247DECCAD5734B57CAE832D916727AE6D0F8AC02871E5F7CE631DE28B0575",

        "3.1.7":
            "D7AA19721DEFB1D40A24A22EBA04BDA776216520CFB31B9FAA1309242F1CF650",

        "3.1.8":
            "0628EBEF79EB8F2F7E0D9CF55D84B93FD5B66AAA36702D25699AF3E4DCC6D1B4",

        "3.1.9":
            "406EC0488C01742FAF8B551335157B315B04A4D4276D4A6E6CD121D4B7FF329F",

        "3.1.10":
            "AA8A1C29D832AF8BFA01703734D40CBB7C0D9F75D6DA67D407D398AE296BEE16",

        "3.1.11":
            "AFB3ADC980D432F329FD76E471EDB8DA571E2ED00708F37B04D888BFB178E8A5",

        "3.1.12":
            "905AB94AC692D343489CD6840A7AFDEE166A0BA6832366BCB9D4F9841BDEB0B1",

        "3.1.13":
            "879EF24F1FA0DC36D2F92619C64085913DC4F38A9E0CDF001B92FAE7DC32E598",

        "3.1.14":
            "F55FD3543558FEAC3C3D681C9CD8500F9EBE685CA349F298625C28C934962930",
    }
)


class UniversalQueueInfrastructureCertificationError(
    ValueError
):

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:

        super().__init__(
            message
        )

        self.code = str(code)
        self.value = value


def _normalize_ast_digest(
    value: Any,
    *,
    phase: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalQueueInfrastructureCertificationError(
            "AST digest must be a string.",
            code="invalid_queue_authority_ast_type",
            value=value,
        )

    normalized = (
        value.strip().upper()
    )

    if (
        len(normalized) != 64
        or any(
            character
            not in "0123456789ABCDEF"
            for character in normalized
        )
    ):

        raise UniversalQueueInfrastructureCertificationError(
            (
                "AST digest must be a canonical "
                "64-character uppercase SHA-256 digest."
            ),
            code="invalid_queue_authority_ast_digest",
            value={
                "phase": phase,
                "digest": value,
            },
        )

    return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueInfrastructureManifest:

    authority_ast_sha256: Mapping[str, str]

    schema_version: str = (
        UNIVERSAL_QUEUE_INFRASTRUCTURE_MANIFEST_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        if not isinstance(
            self.authority_ast_sha256,
            Mapping,
        ):

            raise UniversalQueueInfrastructureCertificationError(
                "authority_ast_sha256 must be a mapping.",
                code="invalid_queue_manifest_ast_mapping",
                value=self.authority_ast_sha256,
            )

        supplied_keys = set(
            self.authority_ast_sha256.keys()
        )

        expected_keys = set(
            UNIVERSAL_QUEUE_PHASE_ORDER
        )

        if supplied_keys != expected_keys:

            raise UniversalQueueInfrastructureCertificationError(
                "Queue manifest phase keys are not exact.",
                code="invalid_queue_manifest_phase_keys",
                value={
                    "expected": sorted(expected_keys),
                    "actual": sorted(
                        str(key)
                        for key in supplied_keys
                    ),
                },
            )

        normalized = {}

        for phase in (
            UNIVERSAL_QUEUE_PHASE_ORDER
        ):

            normalized[
                phase
            ] = _normalize_ast_digest(
                self.authority_ast_sha256[
                    phase
                ],
                phase=phase,
            )

        object.__setattr__(
            self,
            "authority_ast_sha256",
            MappingProxyType(
                normalized
            ),
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_INFRASTRUCTURE_MANIFEST_SCHEMA_VERSION
        ):

            raise UniversalQueueInfrastructureCertificationError(
                "Invalid queue manifest schema_version.",
                code="invalid_queue_manifest_schema_version",
                value=self.schema_version,
            )

    @property
    def authority_count(
        self,
    ) -> int:

        return len(
            self.authority_ast_sha256
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "phase_order":
                list(
                    UNIVERSAL_QUEUE_PHASE_ORDER
                ),

            "authority_count":
                self.authority_count,

            "authorities": [
                {
                    "phase":
                        phase,

                    "name":
                        UNIVERSAL_QUEUE_AUTHORITY_NAMES[
                            phase
                        ],

                    "file":
                        UNIVERSAL_QUEUE_AUTHORITY_FILES[
                            phase
                        ],

                    "ast_sha256":
                        self.authority_ast_sha256[
                            phase
                        ],
                }

                for phase in (
                    UNIVERSAL_QUEUE_PHASE_ORDER
                )
            ],
        }


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalQueueInfrastructureCertification:

    manifest: UniversalQueueInfrastructureManifest

    certified: bool

    certification_id: str

    mutation_required: bool = False

    schema_version: str = (
        UNIVERSAL_QUEUE_INFRASTRUCTURE_CERTIFICATION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        if not isinstance(
            self.manifest,
            UniversalQueueInfrastructureManifest,
        ):

            raise UniversalQueueInfrastructureCertificationError(
                (
                    "manifest must be a "
                    "UniversalQueueInfrastructureManifest."
                ),
                code="invalid_queue_certification_manifest",
                value=self.manifest,
            )

        if not isinstance(
            self.certified,
            bool,
        ):

            raise UniversalQueueInfrastructureCertificationError(
                "certified must be bool.",
                code="invalid_queue_certified_flag",
                value=self.certified,
            )

        if self.certified is not True:

            raise UniversalQueueInfrastructureCertificationError(
                (
                    "A Queue Infrastructure certification "
                    "object may only represent a successful certification."
                ),
                code="queue_infrastructure_not_certified",
                value=self.certified,
            )

        if not isinstance(
            self.certification_id,
            str,
        ):

            raise UniversalQueueInfrastructureCertificationError(
                "certification_id must be a string.",
                code="invalid_queue_certification_id_type",
                value=self.certification_id,
            )

        certification_id = (
            self.certification_id.strip()
        )

        if not certification_id.startswith(
            "phase_3_1_15_"
        ):

            raise UniversalQueueInfrastructureCertificationError(
                "Invalid Phase 3.1.15 certification_id.",
                code="invalid_queue_certification_id",
                value=self.certification_id,
            )

        if not isinstance(
            self.mutation_required,
            bool,
        ):

            raise UniversalQueueInfrastructureCertificationError(
                "mutation_required must be bool.",
                code="invalid_queue_certification_mutation_flag",
                value=self.mutation_required,
            )

        if self.mutation_required is not False:

            raise UniversalQueueInfrastructureCertificationError(
                (
                    "3.1.15 certifies the subsystem "
                    "but does not mutate Queue Infrastructure."
                ),
                code="queue_certification_mutation_not_owned",
                value=self.mutation_required,
            )

        object.__setattr__(
            self,
            "certification_id",
            certification_id,
        )

        if (
            self.schema_version
            != UNIVERSAL_QUEUE_INFRASTRUCTURE_CERTIFICATION_SCHEMA_VERSION
        ):

            raise UniversalQueueInfrastructureCertificationError(
                "Invalid queue certification schema_version.",
                code="invalid_queue_certification_schema_version",
                value=self.schema_version,
            )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "certified":
                self.certified,

            "certification_id":
                self.certification_id,

            "mutation_required":
                self.mutation_required,

            "manifest":
                self.manifest.to_dict(),
        }


def create_universal_queue_infrastructure_manifest(
    *,
    authority_ast_sha256: Mapping[str, str],
) -> UniversalQueueInfrastructureManifest:

    return UniversalQueueInfrastructureManifest(
        authority_ast_sha256=(
            authority_ast_sha256
        )
    )


def compare_universal_queue_infrastructure_manifest(
    *,
    manifest: UniversalQueueInfrastructureManifest,
) -> tuple[str, ...]:

    if not isinstance(
        manifest,
        UniversalQueueInfrastructureManifest,
    ):

        raise UniversalQueueInfrastructureCertificationError(
            (
                "manifest must be a "
                "UniversalQueueInfrastructureManifest."
            ),
            code="invalid_queue_manifest",
            value=manifest,
        )

    mismatches = []

    for phase in (
        UNIVERSAL_QUEUE_PHASE_ORDER
    ):

        expected = (
            UNIVERSAL_QUEUE_AUTHORITY_AST_SHA256[
                phase
            ]
        )

        actual = (
            manifest.authority_ast_sha256[
                phase
            ]
        )

        if actual != expected:

            mismatches.append(
                phase
            )

    return tuple(
        mismatches
    )


def certify_universal_queue_infrastructure(
    *,
    manifest: UniversalQueueInfrastructureManifest,
    certification_id: str,
) -> UniversalQueueInfrastructureCertification:

    mismatches = (
        compare_universal_queue_infrastructure_manifest(
            manifest=manifest
        )
    )

    if mismatches:

        raise UniversalQueueInfrastructureCertificationError(
            "Queue Infrastructure manifest contains AST drift.",
            code="queue_infrastructure_ast_drift",
            value=mismatches,
        )

    return UniversalQueueInfrastructureCertification(
        manifest=manifest,
        certified=True,
        certification_id=certification_id,
        mutation_required=False,
    )


def explain_universal_queue_infrastructure_certification_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "3.1.15",

            "component":
                "Universal Queue Infrastructure Certification",

            "version":
                UNIVERSAL_QUEUE_INFRASTRUCTURE_CERTIFICATION_VERSION,

            "manifest_schema":
                UNIVERSAL_QUEUE_INFRASTRUCTURE_MANIFEST_SCHEMA_VERSION,

            "certification_schema":
                UNIVERSAL_QUEUE_INFRASTRUCTURE_CERTIFICATION_SCHEMA_VERSION,

            "certified_phase_range":
                "3.1.1 through 3.1.14",

            "authority_count":
                14,

            "phase_order":
                UNIVERSAL_QUEUE_PHASE_ORDER,

            "certification_rule": (
                "all 14 canonical Queue Infrastructure authority "
                "AST digests must exactly match the frozen manifest"
            ),

            "manifest_rule": (
                "the manifest is immutable, complete, ordered by "
                "canonical phase and contains exactly one digest "
                "for each authority from 3.1.1 through 3.1.14"
            ),

            "integration_rule": (
                "3.1.15 certifies authority integrity and subsystem "
                "coherence; it does not compose all queue authorities "
                "into one mandatory execution chain"
            ),

            "package_rule": (
                "3.1.15 does not modify universal_queue/__init__.py "
                "or create package-level runtime integration"
            ),

            "runtime_boundary": (
                "workers, leases, claims, dispatch, orchestration, "
                "persistence and physical queue execution remain "
                "outside Phase 3.1 certification authority"
            ),

            "prohibitions": (
                "does not modify Queue Creation",
                "does not modify Queue Scheduling",
                "does not modify Queue Prioritization",
                "does not modify Queue Routing",
                "does not modify Queue Balancing",
                "does not modify Queue Partitioning",
                "does not modify Queue Recovery",
                "does not modify Dead Letter Queues",
                "does not modify Queue Cleanup",
                "does not modify Queue Backpressure",
                "does not modify Queue Capacity Limits",
                "does not modify Queue Fairness",
                "does not modify Queue Rate Limiting",
                "does not modify Queue Deduplication",
                "does not modify universal_queue/__init__.py",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not lease jobs",
                "does not dispatch jobs",
                "does not requeue jobs",
                "does not select workers",
                "does not access orchestration",
                "does not access the Job Store",
                "does not access Runtime State Store",
                "does not create physical queues",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_QUEUE_INFRASTRUCTURE_CERTIFICATION_VERSION",
    "UNIVERSAL_QUEUE_INFRASTRUCTURE_MANIFEST_SCHEMA_VERSION",
    "UNIVERSAL_QUEUE_INFRASTRUCTURE_CERTIFICATION_SCHEMA_VERSION",
    "UNIVERSAL_QUEUE_PHASE_ORDER",
    "UNIVERSAL_QUEUE_AUTHORITY_NAMES",
    "UNIVERSAL_QUEUE_AUTHORITY_FILES",
    "UNIVERSAL_QUEUE_AUTHORITY_AST_SHA256",
    "UniversalQueueInfrastructureCertificationError",
    "UniversalQueueInfrastructureManifest",
    "UniversalQueueInfrastructureCertification",
    "create_universal_queue_infrastructure_manifest",
    "compare_universal_queue_infrastructure_manifest",
    "certify_universal_queue_infrastructure",
    "explain_universal_queue_infrastructure_certification_v1",
]
