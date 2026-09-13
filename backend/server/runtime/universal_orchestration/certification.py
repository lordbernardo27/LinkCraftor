from __future__ import annotations

import hashlib

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final, Mapping


UNIVERSAL_RUNTIME_ORCHESTRATION_CERTIFICATION_VERSION: Final[str] = (
    "universal_runtime_orchestration_certification_v5.1.18"
)

UNIVERSAL_RUNTIME_ORCHESTRATION_CERTIFICATION_SCHEMA_VERSION: Final[str] = (
    "universal_runtime_orchestration_certification_schema_v1"
)

UNIVERSAL_RUNTIME_ORCHESTRATION_CERTIFICATION_HASH_ALGORITHM: Final[str] = (
    "sha256"
)


_FROZEN_AUTHORITY_AST_HASHES: Final[Mapping[str, str]] = MappingProxyType(
    {
        "5.1.1":
            "8CC241284B8AF87809A41134FF0FDEB402D5DE49A117D931920CC17346271FD9",

        "5.1.2":
            "A582564C7D45D96DAB2D6DAF38E8C63B9EA281251F41B02D12DE17F1D68CAFBC",

        "5.1.3":
            "B179C6BEB0A232F0170A2ED540D84239A2235A4F0F91528B530E229B61172610",

        "5.1.4":
            "CF4CE73A8683BFDA1464730F2079058898B2660275C786FA6EBD0816AE574A8E",

        "5.1.5":
            "78F7945AD5592370C21BF919328D6C29627EF209F37A5E864C0588CD40DC7465",

        "5.1.6":
            "9BF16440AD057B1C6A89DD9AEEDEADBE32F711EAE2D4FCD8730EB796BF603D6D",

        "5.1.7":
            "6878FC6F0F2EF071B11A93D793A0CC80B2C91B676C6B6735A78237D8C7D6CB73",

        "5.1.8":
            "D60C8629D2490DC41A8DF43E30F00A1D4851941E65CBD2EBE7EED70B75217916",

        "5.1.9":
            "98786AEF5E4DBD804FBE5FE32EEE7CD54907FAC6A9C016B6120851834F6CFA0F",

        "5.1.10":
            "3799D3BEFB10C77400B40964EBBCCF598B7576BA9034D1C7F29622D0EC65286F",

        "5.1.11":
            "92C100E0682F975488F78ED5F0D38CB1F4C6E18F6FEA08D1A8D81BE98A4D8309",

        "5.1.12":
            "476631641C740443FF7B3D1D1D0E9D6D155289BDCAF14526698528432CCF913A",

        "5.1.13":
            "4465A7AF795512594023D19E27A175CA060ACD2845BB4530B77FF8D69C40B16F",

        "5.1.14":
            "5B7F640250498B4B5320C3702112D163E16B6878C412447623E5C0FF93608CCA",

        "5.1.15":
            "1311EEBEB9622AF5D4CF6F4D7CB14FF83B169C748A01DDD144A8000301A5CBD4",

        "5.1.16":
            "3D2095E4B546596554875BB8FB1E289489FAFD26C013DBE40A7066DB197E25CB",

        "5.1.17":
            "6BF84A9D3E8B120D5506DFF31D4BEB8718ECF488820E69782C7F0F7C85758FD9",
    }
)


_FROZEN_AUTHORITY_FINGERPRINTS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "5.1.1":
            "6EB4FBA61E7FF764FA5CD64BBF3F13972D3F61954AC78B1AAA0D93B9AA74A155",

        "5.1.2":
            "6F0475D76C0A629827FA6B74F755F89C63CD5E75D7E70F2087469B69F1B76299",

        "5.1.3":
            "D46F580CA2E18CA666F0BB597623FDFAA98F75EED64224F7690A3724C11826AA",

        "5.1.4":
            "66ABE78758EFD3FE25A36D80A87A14B43A96AE8C806A20DBEB273C69C1050942",

        "5.1.5":
            "E89F767158E43C2DF78B8E65E9B1BF7C2B948238683F04DC2014AC18CAC3957A",

        "5.1.6":
            "8BDEF91879B5851355844B941DAE53899FCB51ADE46557DD72B4FA1F76D51D29",

        "5.1.7":
            "E016E782AC306C62505386D7D11F9254275EF9E9E34B7FB52DF1FCCC2AE095BC",

        "5.1.8":
            "B59238FA3050850AEF25BD111E49719B65E036DF8F4A3F8C9021A90C5B71F03D",

        "5.1.9":
            "02135980C7275A5C3713156C7021D391E1BD160AFF3AB9696D26A57FDA504D20",

        "5.1.10":
            "A4AACA0AB85E9C43F64B385C3853E0555D191CEC1DCA69583857DBC4F003D046",

        "5.1.11":
            "58CA16BC4DC8B9AFA7DE15DCF8184FDF253FAE0CDC98EABB750AFC6252303BAF",

        "5.1.12":
            "CC2A68A007E71BC1FE2DAC3E01E0F40F90D694CDE67F00D0559478A0BA96BFAE",

        "5.1.13":
            "09AA8290AF5DD557937750C5220E7292090458240E5D8719E730C33236284E38",

        "5.1.14":
            "C4D44944254E8BFBC867FDD96BA0346A119FBC3D0A5C3B0B9478F7E8383B48AA",

        "5.1.15":
            "6DECC6FD7917E08C08607E4914EEA056750A9BBF7B41E4859F3DB8A895772C36",

        "5.1.16":
            "BD694423C0C8266DA09166C2593AF020C6FF08E9DF2FF408447DE08A18BFC048",

        "5.1.17":
            "363E53AF5760ED08AC53CC6D72711923053E1960F76172B83025366BF3A8698E",
    }
)


_CERTIFIED_INVARIANTS: Final[tuple[str, ...]] = (
    "contract_authority_unique",
    "run_identity_authority_unique",
    "state_legality_authority_unique",
    "dependency_resolution_authority_unique",
    "execution_planning_is_planning_only",
    "stage_readiness_is_decision_only",
    "runtime_handoff_is_eligibility_only",
    "fan_out_preserves_structural_planning",
    "fan_in_preserves_join_semantics",
    "conditional_unknown_is_not_false",
    "progress_authority_unique",
    "excluded_work_ignored_downstream",
    "uncertainty_preserved",
    "suspension_resume_eligibility_is_not_execution",
    "recovery_decision_is_not_recovery_execution",
    "persistence_interface_is_not_persistence_backend",
    "completion_is_not_state_mutation",
    "completion_is_not_cancellation",
    "cancellation_requires_explicit_intent",
    "cancellation_is_not_cancellation_execution",
    "evidence_record_is_not_physical_audit_backend",
    "state_persistence_is_not_decision_evidence",
    "no_job_execution",
    "no_queue_execution",
    "no_worker_execution",
    "no_lease_manipulation",
    "no_runtime_handler_dispatch",
    "no_direct_concrete_persistence",
    "no_ucf_ownership",
    "no_pipeline_coordinator_ownership",
    "phase_6_owns_execution",
)


def _is_sha256(
    value: Any,
) -> bool:

    return (
        isinstance(
            value,
            str,
        )
        and
        len(
            value
        )
        == 64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character
            in value
        )
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalRuntimeOrchestrationCertificationManifest:

    authority_ast_hashes: Mapping[str, str]

    authority_fingerprints: Mapping[str, str]

    certified_invariants: tuple[str, ...]

    schema_version: str = (
        UNIVERSAL_RUNTIME_ORCHESTRATION_CERTIFICATION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        ast_hashes = dict(
            self.authority_ast_hashes
        )

        fingerprints = dict(
            self.authority_fingerprints
        )

        invariants = tuple(
            self.certified_invariants
        )

        expected_keys = tuple(
            f"5.1.{index}"
            for index
            in range(
                1,
                18,
            )
        )

        if tuple(
            ast_hashes.keys()
        ) != expected_keys:

            raise ValueError(
                "authority_ast_hashes must contain exactly 5.1.1 through 5.1.17."
            )

        if tuple(
            fingerprints.keys()
        ) != expected_keys:

            raise ValueError(
                "authority_fingerprints must contain exactly 5.1.1 through 5.1.17."
            )

        if not all(
            _is_sha256(
                value
            )
            for value
            in ast_hashes.values()
        ):

            raise ValueError(
                "All authority AST hashes must be uppercase SHA-256 values."
            )

        if not all(
            _is_sha256(
                value
            )
            for value
            in fingerprints.values()
        ):

            raise ValueError(
                "All authority fingerprints must be uppercase SHA-256 values."
            )

        if (
            invariants
            !=
            _CERTIFIED_INVARIANTS
        ):

            raise ValueError(
                "certified_invariants must match the frozen 5.1.18 invariant set."
            )

        if (
            self.schema_version
            !=
            UNIVERSAL_RUNTIME_ORCHESTRATION_CERTIFICATION_SCHEMA_VERSION
        ):

            raise ValueError(
                "Invalid runtime orchestration certification schema_version."
            )

        object.__setattr__(
            self,
            "authority_ast_hashes",
            MappingProxyType(
                ast_hashes
            ),
        )

        object.__setattr__(
            self,
            "authority_fingerprints",
            MappingProxyType(
                fingerprints
            ),
        )

        object.__setattr__(
            self,
            "certified_invariants",
            invariants,
        )

    @property
    def authority_count(
        self,
    ) -> int:

        return len(
            self.authority_ast_hashes
        )

    @property
    def invariant_count(
        self,
    ) -> int:

        return len(
            self.certified_invariants
        )

    @property
    def runtime_orchestration_fingerprint(
        self,
    ) -> str:

        material: list[str] = [
            "universal_runtime_orchestration_certification_manifest_v1",
            UNIVERSAL_RUNTIME_ORCHESTRATION_CERTIFICATION_VERSION,
            self.schema_version,
            UNIVERSAL_RUNTIME_ORCHESTRATION_CERTIFICATION_HASH_ALGORITHM,
        ]

        for phase, ast_hash in self.authority_ast_hashes.items():

            material.extend(
                (
                    phase,
                    ast_hash,
                    self.authority_fingerprints[
                        phase
                    ],
                )
            )

        material.extend(
            self.certified_invariants
        )

        return hashlib.sha256(
            "|".join(
                material
            ).encode(
                "utf-8"
            )
        ).hexdigest().upper()

    @property
    def certification_id(
        self,
    ) -> str:

        return (
            "phase_5_1_18_"
            + self.runtime_orchestration_fingerprint[
                :16
            ].lower()
        )

    @property
    def manifest(
        self,
    ) -> Mapping[str, Any]:

        return MappingProxyType(
            {
                "version":
                    UNIVERSAL_RUNTIME_ORCHESTRATION_CERTIFICATION_VERSION,

                "schema_version":
                    self.schema_version,

                "hash_algorithm":
                    UNIVERSAL_RUNTIME_ORCHESTRATION_CERTIFICATION_HASH_ALGORITHM,

                "authority_count":
                    self.authority_count,

                "authority_ast_hashes":
                    self.authority_ast_hashes,

                "authority_fingerprints":
                    self.authority_fingerprints,

                "certified_invariants":
                    self.certified_invariants,

                "invariant_count":
                    self.invariant_count,

                "runtime_orchestration_fingerprint":
                    self.runtime_orchestration_fingerprint,

                "certification_id":
                    self.certification_id,
            }
        )


def create_universal_runtime_orchestration_certification_manifest(
) -> UniversalRuntimeOrchestrationCertificationManifest:

    return (
        UniversalRuntimeOrchestrationCertificationManifest(
            authority_ast_hashes=_FROZEN_AUTHORITY_AST_HASHES,
            authority_fingerprints=_FROZEN_AUTHORITY_FINGERPRINTS,
            certified_invariants=_CERTIFIED_INVARIANTS,
        )
    )


def explain_universal_runtime_orchestration_certification_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "5.1.18",

            "component":
                "Universal Runtime Orchestration Certification",

            "authority_count":
                17,

            "certified_invariant_count":
                len(
                    _CERTIFIED_INVARIANTS
                ),

            "stored_fields": (
                "authority_ast_hashes",
                "authority_fingerprints",
                "certified_invariants",
                "schema_version",
            ),

            "purpose": (
                "Bind all frozen Phase-5.1 orchestration authorities, "
                "their semantic fingerprints and whole-layer invariants "
                "into one deterministic certification identity."
            ),

            "execution_boundary": (
                "Phase 5.1 models, decides and coordinates. "
                "Phase 6 owns actual execution."
            ),

            "prohibitions": (
                "does not modify 5.1.1 through 5.1.17",
                "does not execute orchestration",
                "does not transition orchestration state",
                "does not recompute orchestration progress",
                "does not recompute orchestration decisions",
                "does not persist runtime state",
                "does not write audit events",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not assign workers",
                "does not terminate workers",
                "does not manipulate leases",
                "does not dispatch runtime handlers",
                "does not execute jobs",
                "does not access Runtime State Store",
                "does not perform filesystem I/O",
                "does not perform database I/O",
                "does not perform network I/O",
                "does not import Universal Coordination Framework",
                "does not invoke pipeline coordinators",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_RUNTIME_ORCHESTRATION_CERTIFICATION_VERSION",
    "UNIVERSAL_RUNTIME_ORCHESTRATION_CERTIFICATION_SCHEMA_VERSION",
    "UNIVERSAL_RUNTIME_ORCHESTRATION_CERTIFICATION_HASH_ALGORITHM",
    "UniversalRuntimeOrchestrationCertificationManifest",
    "create_universal_runtime_orchestration_certification_manifest",
    "explain_universal_runtime_orchestration_certification_v1",
]

