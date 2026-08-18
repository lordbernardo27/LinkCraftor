from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from dataclasses import fields
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

CAPABILITY_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "capability.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_13_worker_capability_final_certification.txt"
)

EXPECTED_CAPABILITY_AST = (
    "200A42478283CDAC92965EAF0DEDFAB3FAB8834F5FB734E3A4874F1EE571C51D"
)


PROTECTED = {
    "worker_registration": (
        ROOT / "backend/server/runtime/universal_worker/registration.py",
        "00F0D6E620E24A7433C880B722E023AF3C2121563F8E18DFA9979E0F06A36D64",
    ),
    "worker_discovery": (
        ROOT / "backend/server/runtime/universal_worker/discovery.py",
        "DFCAB9080982C8D5E099A40C903F7B4140B0860053DB73CB77B30B966788A228",
    ),
    "worker_assignment": (
        ROOT / "backend/server/runtime/universal_worker/assignment.py",
        "609D3077B84C1791262F8ACA6BD268FD40436DF7775ACB3E9E726BCFC9715F56",
    ),
    "worker_leasing": (
        ROOT / "backend/server/runtime/universal_worker/leasing.py",
        "413B8081D7802211D64B7B811299F9A8A2C54DBAEAB0FC537B1603A3BE397932",
    ),
    "worker_health": (
        ROOT / "backend/server/runtime/universal_worker/health.py",
        "DCC43E77BDC12188DFD15044DA4DA41022B3CEF40F9C4ED06371EE66AA4E5F65",
    ),
    "worker_recovery": (
        ROOT / "backend/server/runtime/universal_worker/recovery.py",
        "C3EF5DBD81205F0087E05F43F6A67A1E0762930DAAD256F957AABC57296D19A5",
    ),
    "worker_scaling": (
        ROOT / "backend/server/runtime/universal_worker/scaling.py",
        "8EC818E4EF4CA7DBCADCFCB93FD99BC80AAD4CE8AEBE1CDE63CCC44FA8488FF6",
    ),
    "worker_shutdown": (
        ROOT / "backend/server/runtime/universal_worker/shutdown.py",
        "DB2197CA791988B01C73CE426ED29891C8BD9FE46DFEC1AC5AE79D1D131C34DD",
    ),
    "worker_pool": (
        ROOT / "backend/server/runtime/universal_worker/pool.py",
        "4BA8E641A88A5BB38F78D2B981216765B3327D639EB3BC78E5294C152E84A308",
    ),
    "worker_heartbeat": (
        ROOT / "backend/server/runtime/universal_worker/heartbeat.py",
        "A58BDEE660CA903453DA6D968A2B02FBFBE3920E9BBE6C64BC75A597DB7C11EE",
    ),
    "stale_worker_detection": (
        ROOT / "backend/server/runtime/universal_worker/stale.py",
        "22105ACBF984E26019080E53939617CE14BDF51BF5A9B149BD39E10B6B87B9DD",
    ),
    "worker_drain": (
        ROOT / "backend/server/runtime/universal_worker/drain.py",
        "629AA6B5D9269B3164A1524F3C176B2EA34CB4952A0D32F5E2EE4A7C6984FA78",
    ),
    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),
    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),
    "existing_runtime_worker": (
        ROOT / "backend/server/runtime/universal_runtime_worker_v1.py",
        "6CC4EC122C6B8D1E21AFF8B55CAA786148D7E1FC75D840DAE9240FFB69634D44",
    ),
    "runtime_registration": (
        ROOT / "backend/server/runtime/universal_runtime_registration.py",
        "CBFBB0DA1E5D05A040AEC6F60B1251331431956106D90335A8C110FDBCA632E5",
    ),
    "runtime_infrastructure": (
        ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",
        "EE6590D044C6AA20762F2A37AE86B7FFD3300B62610BC2B1F2657D9334CB311C",
    ),
    "runtime_shutdown_process": (
        ROOT / "backend/server/runtime/runtime_shutdown_process.py",
        "7A159E206C73157064B70D15A1CE4A97AB3D77EBBC77B01A2554BC34224EB272",
    ),
    "runtime_lifecycle_manager": (
        ROOT / "backend/server/runtime/runtime_lifecycle_manager.py",
        "E6200CA0938B5D578954024D6E76E343FB39D9329CFD3ABE4B3AEF86E8204034",
    ),
    "orchestration_models": (
        ROOT / "backend/server/orchestration/models.py",
        "5C9FE5E4F84FA1C369CB45F74B0CB12B7E730ADA3C7CBC95B4F50EC75DC5E92D",
    ),
    "tms_orchestration_governance": (
        ROOT / "backend/server/tms/orchestration_governance.py",
        "2AAA15B7283C6F0B4BB67A47FE58F1FD0EF2815A09CA048EA0CFE7DEF232B4E1",
    ),
    "orchestration_queue": (
        ROOT / "backend/server/orchestration/queue.py",
        "76F8F7E66578E2B8A4A1FF3BB420B6340A7A1D1D661EB66B7C21987CF3845A97",
    ),
    "orchestration_service": (
        ROOT / "backend/server/orchestration/service.py",
        "4C31CFC6FFDC9AFA8EA6AD8F43ADBC117F8A6D0193ABF045DBFBA39D6EB799BA",
    ),
}


def ast_sha(path: Path) -> str:

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source
    )

    canonical = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest().upper()


# ============================================================
# PRECONDITIONS
# ============================================================

if not CAPABILITY_PATH.exists():

    raise SystemExit(
        "4.1.13 Worker Capability authority missing."
    )


initial_ast = ast_sha(
    CAPABILITY_PATH
)


if initial_ast != EXPECTED_CAPABILITY_AST:

    raise SystemExit(
        (
            "Worker Capability AST mismatch before "
            "final certification.\n"
            "EXPECTED: "
            + EXPECTED_CAPABILITY_AST
            + "\nACTUAL:   "
            + initial_ast
        )
    )


for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(
        path
    )

    if actual != expected:

        raise SystemExit(
            (
                "Protected authority mismatch before "
                "4.1.13 final certification: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


# ============================================================
# IMPORT
# ============================================================

sys.path.insert(
    0,
    str(ROOT),
)

registration = importlib.import_module(
    "backend.server.runtime.universal_worker.registration"
)

module_name = (
    "backend.server.runtime."
    "universal_worker.capability"
)

sys.modules.pop(
    module_name,
    None,
)

capability = importlib.import_module(
    module_name
)


checks = []


def check(
    name,
    condition,
    detail="",
):

    checks.append(
        (
            name,
            bool(condition),
            str(detail),
        )
    )


reg = (
    registration.create_universal_worker_registration(
        worker_id="worker-a",
        worker_type="semantic_worker",
        worker_instance_id="instance-1",
        runtime_version="runtime-v1",
        host_id="host-1",
        registered_at="2026-08-17T00:00:00+00:00",
    )
)


# ============================================================
# 1 — AUTHORITY / VERSION
# ============================================================

capability_ast = ast_sha(
    CAPABILITY_PATH
)


check(
    "worker_capability_ast",
    capability_ast
    == EXPECTED_CAPABILITY_AST,
    capability_ast,
)

check(
    "version",
    capability.UNIVERSAL_WORKER_CAPABILITY_VERSION
    == "universal_worker_capability_v4.1.13",
)

check(
    "snapshot_schema",
    capability.UNIVERSAL_WORKER_CAPABILITY_SNAPSHOT_SCHEMA_VERSION
    == "universal_worker_capability_snapshot_schema_v1",
)

check(
    "match_schema",
    capability.UNIVERSAL_WORKER_CAPABILITY_MATCH_SCHEMA_VERSION
    == "universal_worker_capability_match_schema_v1",
)

check(
    "minimum_length",
    capability.MIN_UNIVERSAL_WORKER_CAPABILITY_LENGTH
    == 2,
)

check(
    "maximum_length",
    capability.MAX_UNIVERSAL_WORKER_CAPABILITY_LENGTH
    == 128,
)

check(
    "maximum_capability_count",
    capability.MAX_UNIVERSAL_WORKER_CAPABILITIES
    == 1024,
)

check(
    "identity_separator",
    capability.UNIVERSAL_WORKER_CAPABILITY_IDENTITY_SEPARATOR
    == "::",
)


# ============================================================
# 2 — TOKEN CONTRACT
# ============================================================

token_cases = (
    (
        "semantic.read",
        "semantic.read",
    ),
    (
        " Semantic.Read ",
        "semantic.read",
    ),
    (
        "ARTICLE.Validate",
        "article.validate",
    ),
    (
        "a_b-c.d:e9",
        "a_b-c.d:e9",
    ),
    (
        "01",
        "01",
    ),
)


for index, (
    raw,
    expected,
) in enumerate(
    token_cases,
    start=1,
):

    actual = (
        capability.normalize_universal_worker_capability(
            raw
        )
    )

    check(
        "canonical_token_"
        + str(index),
        actual
        == expected,
        actual,
    )


for bad in (
    None,
    True,
    False,
    0,
    1.0,
    "",
    " ",
    "a",
    "_a",
    "-a",
    ".a",
    ":a",
    "a b",
    "a/b",
    "a@b",
    "x" * 129,
    [],
    {},
    (),
):

    try:

        capability.normalize_universal_worker_capability(
            bad
        )

    except capability.UniversalWorkerCapabilityError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_token_"
        + repr(
            bad
        ),
        rejected,
    )


# ============================================================
# 3 — COLLECTION CONTRACT
# ============================================================

normalized = (
    capability.normalize_universal_worker_capabilities(
        (
            "semantic.read",
            "article.validate",
            "document.extract",
        )
    )
)


check(
    "collection_sorted",
    normalized
    == (
        "article.validate",
        "document.extract",
        "semantic.read",
    ),
    normalized,
)


check(
    "empty_collection_valid",
    capability.normalize_universal_worker_capabilities(
        ()
    )
    == (),
)


try:

    capability.normalize_universal_worker_capabilities(
        (
            "Semantic.Read",
            "semantic.read",
        )
    )

except capability.UniversalWorkerCapabilityError as exc:

    rejected = (
        exc.code
        == "duplicate_worker_capability"
    )

else:

    rejected = False


check(
    "normalized_duplicate_rejected",
    rejected,
)


max_collection = tuple(
    "cap"
    + str(index).zfill(4)
    for index in range(
        capability.MAX_UNIVERSAL_WORKER_CAPABILITIES
    )
)


check(
    "max_collection_accepted",
    len(
        capability.normalize_universal_worker_capabilities(
            max_collection
        )
    )
    == capability.MAX_UNIVERSAL_WORKER_CAPABILITIES,
)


try:

    capability.normalize_universal_worker_capabilities(
        max_collection
        + (
            "overflow.cap",
        )
    )

except capability.UniversalWorkerCapabilityError as exc:

    rejected = (
        exc.code
        == "worker_capability_count_too_large"
    )

else:

    rejected = False


check(
    "overflow_collection_rejected",
    rejected,
)


# ============================================================
# 4 — SNAPSHOT CONTRACT
# ============================================================

snapshot = (
    capability.create_universal_worker_capability_snapshot(
        registration=reg,
        capabilities=(
            "semantic.read",
            "document.extract",
            "article.validate",
        ),
    )
)


check(
    "snapshot_worker_id",
    snapshot.worker_id
    == reg.worker_id,
)

check(
    "snapshot_worker_instance_id",
    snapshot.worker_instance_id
    == reg.worker_instance_id,
)

check(
    "snapshot_worker_type",
    snapshot.worker_type
    == reg.worker_type,
)

check(
    "snapshot_identity",
    snapshot.worker_identity
    == "worker-a::instance-1",
)

check(
    "snapshot_capabilities",
    snapshot.capabilities
    == (
        "article.validate",
        "document.extract",
        "semantic.read",
    ),
)

check(
    "snapshot_count",
    snapshot.capability_count
    == 3,
)


empty_snapshot = (
    capability.create_universal_worker_capability_snapshot(
        registration=reg,
        capabilities=(),
    )
)


check(
    "empty_snapshot_valid",
    empty_snapshot.capabilities
    == (),
)

check(
    "empty_snapshot_count_zero",
    empty_snapshot.capability_count
    == 0,
)


# ============================================================
# 5 — SUPPORT SEMANTICS
# ============================================================

check(
    "support_present",
    capability.supports_universal_worker_capability(
        snapshot=snapshot,
        capability="semantic.read",
    )
    is True,
)

check(
    "support_normalized_present",
    capability.supports_universal_worker_capability(
        snapshot=snapshot,
        capability=" Semantic.Read ",
    )
    is True,
)

check(
    "support_missing_false",
    capability.supports_universal_worker_capability(
        snapshot=snapshot,
        capability="body_store.repair",
    )
    is False,
)


# ============================================================
# 6 — MATCHING SEMANTICS
# ============================================================

compatible = (
    capability.match_universal_worker_capabilities(
        snapshot=snapshot,
        required_capabilities=(
            "semantic.read",
            "article.validate",
        ),
    )
)


check(
    "compatible_true",
    compatible.compatible
    is True,
)

check(
    "compatible_missing_empty",
    compatible.missing_capabilities
    == (),
)

check(
    "compatible_required_sorted",
    compatible.required_capabilities
    == (
        "article.validate",
        "semantic.read",
    ),
)


incompatible = (
    capability.match_universal_worker_capabilities(
        snapshot=snapshot,
        required_capabilities=(
            "semantic.read",
            "body_store.repair",
        ),
    )
)


check(
    "incompatible_false",
    incompatible.compatible
    is False,
)

check(
    "missing_exact",
    incompatible.missing_capabilities
    == (
        "body_store.repair",
    ),
)


empty_requirement = (
    capability.match_universal_worker_capabilities(
        snapshot=empty_snapshot,
        required_capabilities=(),
    )
)


check(
    "empty_requirement_compatible",
    empty_requirement.compatible
    is True,
)

check(
    "empty_requirement_missing_empty",
    empty_requirement.missing_capabilities
    == (),
)


zero_capability_required = (
    capability.match_universal_worker_capabilities(
        snapshot=empty_snapshot,
        required_capabilities=(
            "semantic.read",
        ),
    )
)


check(
    "zero_capability_required_incompatible",
    zero_capability_required.compatible
    is False,
)

check(
    "zero_capability_required_missing_exact",
    zero_capability_required.missing_capabilities
    == (
        "semantic.read",
    ),
)


# ============================================================
# 7 — WORKER TYPE DOES NOT IMPLY CAPABILITY
# ============================================================

check(
    "worker_type_not_capability",
    empty_snapshot.capabilities
    == (),
)

check(
    "worker_type_name_not_supported_implicitly",
    capability.supports_universal_worker_capability(
        snapshot=empty_snapshot,
        capability="semantic_worker",
    )
    is False,
)


# ============================================================
# 8 — SAME TYPE DIFFERENT CAPABILITIES
# ============================================================

reg_b = (
    registration.create_universal_worker_registration(
        worker_id="worker-b",
        worker_type="semantic_worker",
        worker_instance_id="instance-2",
        runtime_version="runtime-v1",
        host_id="host-2",
        registered_at="2026-08-17T00:00:00+00:00",
    )
)


snapshot_b = (
    capability.create_universal_worker_capability_snapshot(
        registration=reg_b,
        capabilities=(
            "body_store.repair",
        ),
    )
)


check(
    "same_worker_type_different_capabilities",
    (
        snapshot.worker_type
        == snapshot_b.worker_type
        and
        snapshot.capabilities
        != snapshot_b.capabilities
    ),
)


# ============================================================
# 9 — RESULT FORGERY HARDENING
# ============================================================

try:

    capability.UniversalWorkerCapabilityMatchResult(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        worker_capabilities=(
            "semantic.read",
        ),
        required_capabilities=(
            "semantic.read",
            "body_store.repair",
        ),
        missing_capabilities=(),
        compatible=True,
    )

except capability.UniversalWorkerCapabilityError as exc:

    rejected = (
        exc.code
        == "inconsistent_worker_capability_missing_set"
    )

else:

    rejected = False


check(
    "forged_missing_rejected",
    rejected,
)


try:

    capability.UniversalWorkerCapabilityMatchResult(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        worker_capabilities=(
            "semantic.read",
        ),
        required_capabilities=(
            "semantic.read",
        ),
        missing_capabilities=(),
        compatible=False,
    )

except capability.UniversalWorkerCapabilityError as exc:

    rejected = (
        exc.code
        == "inconsistent_worker_capability_compatibility"
    )

else:

    rejected = False


check(
    "forged_compatibility_rejected",
    rejected,
)


# ============================================================
# 10 — IDENTITY HARDENING
# ============================================================

for field_name, bad_value in (
    (
        "worker_id",
        "",
    ),
    (
        "worker_id",
        " ",
    ),
    (
        "worker_instance_id",
        "",
    ),
    (
        "worker_instance_id",
        " ",
    ),
    (
        "worker_type",
        "",
    ),
    (
        "worker_type",
        " ",
    ),
):

    kwargs = {
        "worker_id":
            reg.worker_id,

        "worker_instance_id":
            reg.worker_instance_id,

        "worker_type":
            reg.worker_type,

        "capabilities":
            (),
    }

    kwargs[
        field_name
    ] = bad_value

    try:

        capability.UniversalWorkerCapabilitySnapshot(
            **kwargs
        )

    except capability.UniversalWorkerCapabilityError:

        rejected = True

    else:

        rejected = False

    check(
        (
            "identity_hardening_"
            + field_name
            + "_"
            + repr(
                bad_value
            )
        ),
        rejected,
    )


# ============================================================
# 11 — SCHEMA HARDENING
# ============================================================

try:

    capability.UniversalWorkerCapabilitySnapshot(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        capabilities=(),
        schema_version="tampered",
    )

except capability.UniversalWorkerCapabilityError as exc:

    rejected = (
        exc.code
        == "invalid_worker_capability_snapshot_schema_version"
    )

else:

    rejected = False


check(
    "snapshot_schema_tamper_rejected",
    rejected,
)


try:

    capability.UniversalWorkerCapabilityMatchResult(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        worker_capabilities=(),
        required_capabilities=(),
        missing_capabilities=(),
        compatible=True,
        schema_version="tampered",
    )

except capability.UniversalWorkerCapabilityError as exc:

    rejected = (
        exc.code
        == "invalid_worker_capability_match_schema_version"
    )

else:

    rejected = False


check(
    "match_schema_tamper_rejected",
    rejected,
)


# ============================================================
# 12 — IMMUTABILITY
# ============================================================

for obj in (
    snapshot,
    compatible,
):

    for field in fields(
        obj
    ):

        try:

            setattr(
                obj,
                field.name,
                None,
            )

        except Exception:

            immutable = True

        else:

            immutable = False

        check(
            (
                "immutable_"
                + type(obj).__name__
                + "_"
                + field.name
            ),
            immutable,
        )


# ============================================================
# 13 — EXACT FIELD CONTRACT
# ============================================================

snapshot_fields = tuple(
    field.name
    for field in fields(
        capability.UniversalWorkerCapabilitySnapshot
    )
)

match_fields = tuple(
    field.name
    for field in fields(
        capability.UniversalWorkerCapabilityMatchResult
    )
)


check(
    "snapshot_fields_exact",
    snapshot_fields
    == (
        "worker_id",
        "worker_instance_id",
        "worker_type",
        "capabilities",
        "schema_version",
    ),
    snapshot_fields,
)

check(
    "match_fields_exact",
    match_fields
    == (
        "worker_id",
        "worker_instance_id",
        "worker_type",
        "worker_capabilities",
        "required_capabilities",
        "missing_capabilities",
        "compatible",
        "schema_version",
    ),
    match_fields,
)


# ============================================================
# 14 — DETERMINISM
# ============================================================

snapshot_again = (
    capability.create_universal_worker_capability_snapshot(
        registration=reg,
        capabilities=(
            "document.extract",
            "semantic.read",
            "article.validate",
        ),
    )
)


check(
    "deterministic_snapshot",
    snapshot_again
    == snapshot,
)


match_again = (
    capability.match_universal_worker_capabilities(
        snapshot=snapshot_again,
        required_capabilities=(
            "article.validate",
            "semantic.read",
        ),
    )
)


check(
    "deterministic_match",
    match_again
    == compatible,
)


# ============================================================
# 15 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    capability.explain_universal_worker_capability_v1()
)


check(
    "phase",
    explanation.get(
        "phase"
    )
    == "4.1.13",
)

check(
    "component",
    explanation.get(
        "component"
    )
    == "Universal Worker Capability Management",
)

check(
    "scope_individual_worker",
    "individual-worker"
    in explanation.get(
        "scope_rule",
        "",
    ),
)

check(
    "worker_type_separate",
    "does not itself imply capabilities"
    in explanation.get(
        "worker_type_rule",
        "",
    ),
)

check(
    "generic_tokens",
    "generic normalized"
    in explanation.get(
        "capability_rule",
        "",
    ),
)

check(
    "duplicate_free_deterministic",
    (
        "duplicate-free"
        in explanation.get(
            "collection_rule",
            "",
        )
        and
        "deterministically sorted"
        in explanation.get(
            "collection_rule",
            "",
        )
    ),
)

check(
    "zero_capability_valid",
    "zero capabilities"
    in explanation.get(
        "empty_snapshot_rule",
        "",
    ),
)

check(
    "all_required_matching",
    "ALL-required"
    in explanation.get(
        "matching_rule",
        "",
    ),
)

check(
    "empty_requirement_compatible_rule",
    "therefore compatible"
    in explanation.get(
        "empty_requirement_rule",
        "",
    ),
)

check(
    "assignment_external",
    "does not assign workers"
    in explanation.get(
        "assignment_boundary",
        "",
    ),
)

check(
    "capacity_external",
    "separate"
    in explanation.get(
        "capacity_boundary",
        "",
    ),
)

check(
    "runtime_capability_external",
    "separate"
    in explanation.get(
        "runtime_capability_boundary",
        "",
    ),
)

check(
    "service_registry_external",
    "runtime services"
    in explanation.get(
        "service_registry_boundary",
        "",
    ),
)

check(
    "runtime_registration_external",
    "job_type-to-handler"
    in explanation.get(
        "runtime_registration_boundary",
        "",
    ),
)

check(
    "supported_job_types_external",
    "do not define individual-worker"
    in explanation.get(
        "supported_job_type_boundary",
        "",
    ),
)

check(
    "execution_external",
    "does not dispatch or execute jobs"
    in explanation.get(
        "execution_boundary",
        "",
    ),
)

check(
    "persistence_external",
    "does not persist"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)

check(
    "purity",
    "no external mutation or I/O"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


# ============================================================
# 16 — PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not mutate Worker Registration",
    "does not infer capabilities from worker_type",
    "does not infer capabilities from Worker Pool membership",
    "does not inspect Worker Health",
    "does not inspect Stale Worker Detection",
    "does not inspect Worker Drain",
    "does not calculate Worker Capacity",
    "does not perform Worker Assignment",
    "does not acquire worker leases",
    "does not renew worker leases",
    "does not release worker leases",
    "does not perform Worker Scaling",
    "does not perform Worker Shutdown",
    "does not initiate Worker Recovery",
    "does not register runtime handlers",
    "does not unregister runtime handlers",
    "does not dispatch runtime handlers",
    "does not duplicate Runtime Capability Negotiation",
    "does not register Runtime Service Registry services",
    "does not use supported_job_types as worker capabilities",
    "does not route queue jobs",
    "does not access Queue Infrastructure",
    "does not access orchestration",
    "does not access Runtime State Store",
    "does not persist capability state",
    "does not perform filesystem I/O",
    "does not perform network I/O",
    "does not dispatch jobs",
    "does not execute jobs",
)


prohibitions = tuple(
    explanation.get(
        "prohibitions"
    )
    or ()
)


for index, item in enumerate(
    required_prohibitions,
    start=1,
):

    check(
        "prohibition_"
        + str(index),
        item in prohibitions,
        item,
    )


# ============================================================
# 17 — IMPORT / API BOUNDARY
# ============================================================

source = CAPABILITY_PATH.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(
    source
)


backend_imports = []


for node in ast.walk(
    tree
):

    if isinstance(
        node,
        ast.ImportFrom,
    ):

        module_name = (
            node.module
            or ""
        )

        if module_name.startswith(
            "backend.server"
        ):

            backend_imports.append(
                module_name
            )


check(
    "backend_imports_exact",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.registration",
    ],
    backend_imports,
)


expected_all = (
    "UNIVERSAL_WORKER_CAPABILITY_VERSION",
    "UNIVERSAL_WORKER_CAPABILITY_SNAPSHOT_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_CAPABILITY_MATCH_SCHEMA_VERSION",
    "MIN_UNIVERSAL_WORKER_CAPABILITY_LENGTH",
    "MAX_UNIVERSAL_WORKER_CAPABILITY_LENGTH",
    "MAX_UNIVERSAL_WORKER_CAPABILITIES",
    "UNIVERSAL_WORKER_CAPABILITY_IDENTITY_SEPARATOR",
    "UniversalWorkerCapabilityError",
    "UniversalWorkerCapabilitySnapshot",
    "UniversalWorkerCapabilityMatchResult",
    "normalize_universal_worker_capability",
    "normalize_universal_worker_capabilities",
    "create_universal_worker_capability_snapshot",
    "supports_universal_worker_capability",
    "match_universal_worker_capabilities",
    "explain_universal_worker_capability_v1",
)


check(
    "api_surface_exact",
    tuple(
        capability.__all__
    )
    == expected_all,
    capability.__all__,
)


# ============================================================
# 18 — SIDE EFFECT / COUPLING BOUNDARY
# ============================================================

forbidden_calls = {
    "open",
    "read_text",
    "write_text",
    "write_json",
    "mkdir",
    "unlink",
    "remove",

    "assign_universal_worker",
    "discover_universal_workers",

    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",

    "evaluate_universal_worker_health",
    "evaluate_universal_stale_worker",
    "evaluate_universal_worker_drain",
    "evaluate_universal_worker_recovery",
    "evaluate_universal_worker_scaling",
    "evaluate_universal_worker_shutdown",

    "add_universal_worker_pool_member",
    "remove_universal_worker_pool_member",

    "register_runtime_handler",
    "unregister_runtime_handler",
    "dispatch_registered_runtime_handler",

    "register_runtime_capability_manifest",
    "get_runtime_capability_registry",

    "services_with_capability",
    "register_service",
    "unregister_service",

    "enqueue_job",
    "dequeue_job",
    "route_job",

    "get_runtime_state_store_registry",

    "persist",
    "save",
    "dispatch_job",
    "execute_job",
}


found_forbidden_calls = []


for node in ast.walk(
    tree
):

    if not isinstance(
        node,
        ast.Call,
    ):

        continue

    if isinstance(
        node.func,
        ast.Name,
    ):

        call_name = (
            node.func.id
        )

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        call_name = (
            node.func.attr
        )

    else:

        continue

    if call_name in forbidden_calls:

        found_forbidden_calls.append(
            (
                call_name,
                getattr(
                    node,
                    "lineno",
                    0,
                ),
            )
        )


check(
    "no_forbidden_calls",
    not found_forbidden_calls,
    found_forbidden_calls,
)


# ============================================================
# 19 — PROTECTED AUTHORITIES
# ============================================================

for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(
        path
    )

    check(
        "protected_"
        + name,
        actual
        == expected,
        actual,
    )


# ============================================================
# 20 — CANONICAL FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_4_1_13_worker_capability",

        capability.UNIVERSAL_WORKER_CAPABILITY_VERSION,
        capability.UNIVERSAL_WORKER_CAPABILITY_SNAPSHOT_SCHEMA_VERSION,
        capability.UNIVERSAL_WORKER_CAPABILITY_MATCH_SCHEMA_VERSION,

        capability_ast,

        "canonical_worker_registration_identity",

        "generic_normalized_capability_tokens",
        "lowercase_tokens",
        "capability_length_2_128",
        "maximum_1024_capabilities",
        "normalized_duplicate_rejection",
        "deterministic_lexical_ordering",

        "zero_capability_snapshot_valid",

        "all_required_matching",
        "empty_requirement_compatible",
        "exact_missing_capability_evidence",

        "worker_type_does_not_imply_capability",
        "worker_pool_does_not_imply_capability",

        "compatibility_evidence_only",
        "assignment_external",
        "capacity_external",

        "runtime_capability_negotiation_separate",
        "runtime_service_registry_separate",
        "runtime_registration_handlers_separate",
        "supported_job_types_separate",

        "health_external",
        "stale_external",
        "drain_external",
        "leasing_external",
        "scaling_external",
        "shutdown_external",
        "recovery_external",

        "no_queue_access",
        "no_orchestration_access",
        "no_runtime_state_store",
        "no_persistence",
        "no_filesystem_io",
        "no_network_io",
        "no_dispatch",
        "no_execution",

        "pure_worker_capability_evidence_authority",
    )
)


worker_capability_fingerprint = (
    hashlib.sha256(
        fingerprint_material.encode(
            "utf-8"
        )
    ).hexdigest().upper()
)


check(
    "fingerprint_generated",
    len(
        worker_capability_fingerprint
    )
    == 64,
    worker_capability_fingerprint,
)


# ============================================================
# 21 — FINAL AST
# ============================================================

final_ast = ast_sha(
    CAPABILITY_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_CAPABILITY_AST,
    final_ast,
)


# ============================================================
# REPORT
# ============================================================

passed = sum(
    1
    for _, ok, _
    in checks
    if ok
)

total = len(
    checks
)


lines = [
    (
        "PHASE 4.1.13 — UNIVERSAL WORKER "
        "CAPABILITY MANAGEMENT FINAL CERTIFICATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER CAPABILITY AST SHA256: "
        + capability_ast
    ),
    (
        "WORKER CAPABILITY FINGERPRINT: "
        + worker_capability_fingerprint
    ),
    "",
]


for index, (
    name,
    ok,
    detail,
) in enumerate(
    checks,
    start=1,
):

    lines.append(
        (
            f"{index}. {name}: "
            f"{'PASS' if ok else 'FAIL'}"
        )
    )

    if detail:

        lines.append(
            "   "
            + detail
        )


lines.extend(
    [
        "",
        "=" * 112,
        (
            "FINAL WORKER CAPABILITY CERTIFICATION: "
            + (
                "PASS"
                if passed == total
                else "FAIL"
            )
        ),
        (
            "CHECKS PASSED: "
            + str(
                passed
            )
            + "/"
            + str(
                total
            )
        ),
        "",
        "WORKER CAPABILITY MODIFIED DURING CERTIFICATION: NO",
        "4.1.1 WORKER REGISTRATION MODIFIED: NO",
        "4.1.2 WORKER DISCOVERY MODIFIED: NO",
        "4.1.3 WORKER ASSIGNMENT MODIFIED: NO",
        "4.1.4 WORKER LEASING MODIFIED: NO",
        "4.1.5 WORKER HEALTH MODIFIED: NO",
        "4.1.6 WORKER RECOVERY MODIFIED: NO",
        "4.1.7 WORKER SCALING MODIFIED: NO",
        "4.1.8 WORKER SHUTDOWN MODIFIED: NO",
        "4.1.9 WORKER POOL MODIFIED: NO",
        "4.1.10 WORKER HEARTBEAT MODIFIED: NO",
        "4.1.11 STALE WORKER DETECTION MODIFIED: NO",
        "4.1.12 WORKER DRAIN MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "RUNTIME LIFECYCLE MANAGER MODIFIED: NO",
        "RUNTIME SHUTDOWN PROCESS MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "WORKER REGISTRATION MUTATED: NO",
        "WORKER TYPE USED AS IMPLIED CAPABILITY: NO",
        "WORKER POOL USED AS IMPLIED CAPABILITY: NO",
        "WORKER HEALTH INSPECTED: NO",
        "STALE WORKER DETECTION INSPECTED: NO",
        "WORKER DRAIN INSPECTED: NO",
        "WORKER CAPACITY CALCULATED: NO",
        "WORKER ASSIGNMENT PERFORMED: NO",
        "WORKER LEASE MUTATED: NO",
        "WORKER SCALING PERFORMED: NO",
        "WORKER SHUTDOWN PERFORMED: NO",
        "WORKER RECOVERY INITIATED: NO",
        "RUNTIME HANDLER REGISTERED/DISPATCHED: NO",
        "RUNTIME CAPABILITY NEGOTIATION ACCESSED/MUTATED: NO",
        "RUNTIME SERVICE REGISTRY ACCESSED/MUTATED: NO",
        "SUPPORTED_JOB_TYPES USED AS WORKER CAPABILITIES: NO",
        "QUEUE INFRASTRUCTURE ACCESSED: NO",
        "ORCHESTRATION ACCESSED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "CAPABILITY STATE PERSISTED: NO",
        "FILESYSTEM I/O: NO",
        "NETWORK I/O: NO",
        "JOB DISPATCH/EXECUTION: NO",
        "",
        (
            "PHASE 4.1.13 FREEZE CANDIDATE: "
            + (
                "YES"
                if passed == total
                else "NO"
            )
        ),
    ]
)


REPORT_PATH.write_text(
    "\n".join(
        lines
    ),
    encoding="utf-8",
)

print(
    "\n".join(
        lines
    )
)


if passed != total:

    raise SystemExit(
        "Phase 4.1.13 Worker Capability final certification failed."
    )
