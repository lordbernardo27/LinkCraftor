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
    / "phase_4_1_13_worker_capability_regression.txt"
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
            "Worker Capability AST changed before regression.\n"
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
                "Protected authority changed before "
                "4.1.13 regression: "
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


def make_registration(
    worker_id="worker-a",
    instance_id="instance-1",
    worker_type="semantic_worker",
):

    return registration.create_universal_worker_registration(
        worker_id=worker_id,
        worker_type=worker_type,
        worker_instance_id=instance_id,
        runtime_version="runtime-v1",
        host_id="host-1",
        registered_at="2026-08-17T00:00:00+00:00",
    )


reg = make_registration()


# ============================================================
# 1 — AST / CONSTANTS
# ============================================================

check(
    "capability_ast_stable",
    ast_sha(
        CAPABILITY_PATH
    )
    == EXPECTED_CAPABILITY_AST,
    ast_sha(
        CAPABILITY_PATH
    ),
)

check(
    "version_exact",
    capability.UNIVERSAL_WORKER_CAPABILITY_VERSION
    == "universal_worker_capability_v4.1.13",
)

check(
    "snapshot_schema_exact",
    capability.UNIVERSAL_WORKER_CAPABILITY_SNAPSHOT_SCHEMA_VERSION
    == "universal_worker_capability_snapshot_schema_v1",
)

check(
    "match_schema_exact",
    capability.UNIVERSAL_WORKER_CAPABILITY_MATCH_SCHEMA_VERSION
    == "universal_worker_capability_match_schema_v1",
)

check(
    "min_length_exact",
    capability.MIN_UNIVERSAL_WORKER_CAPABILITY_LENGTH
    == 2,
)

check(
    "max_length_exact",
    capability.MAX_UNIVERSAL_WORKER_CAPABILITY_LENGTH
    == 128,
)

check(
    "max_count_exact",
    capability.MAX_UNIVERSAL_WORKER_CAPABILITIES
    == 1024,
)

check(
    "identity_separator_exact",
    capability.UNIVERSAL_WORKER_CAPABILITY_IDENTITY_SEPARATOR
    == "::",
)


# ============================================================
# 2 — TOKEN BOUNDARIES
# ============================================================

two_char = "a1"

max_char = (
    "a"
    + (
        "b"
        * 127
    )
)


check(
    "token_min_boundary",
    capability.normalize_universal_worker_capability(
        two_char
    )
    == two_char,
)

check(
    "token_max_boundary",
    capability.normalize_universal_worker_capability(
        max_char
    )
    == max_char,
)


for bad in (
    "a",
    "x" * 129,
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
        "length_boundary_rejected_"
        + str(
            len(bad)
        ),
        rejected,
    )


# ============================================================
# 3 — TOKEN NORMALIZATION ATTACK MATRIX
# ============================================================

valid_cases = (
    (
        " Semantic.Read ",
        "semantic.read",
    ),
    (
        "\tARTICLE.Validate\n",
        "article.validate",
    ),
    (
        "A_B-C.D:E9",
        "a_b-c.d:e9",
    ),
    (
        "01",
        "01",
    ),
    (
        "9capability",
        "9capability",
    ),
)


for index, (
    raw,
    expected,
) in enumerate(
    valid_cases,
    start=1,
):

    actual = (
        capability.normalize_universal_worker_capability(
            raw
        )
    )

    check(
        "valid_normalization_"
        + str(index),
        actual
        == expected,
        actual,
    )


invalid_token_cases = (
    None,
    True,
    False,
    0,
    1,
    1.0,
    b"semantic.read",
    bytearray(
        b"semantic.read"
    ),
    [],
    {},
    (),
    set(),

    "",
    " ",
    "\t",
    "\n",

    "_a",
    "-a",
    ".a",
    ":a",

    "a b",
    "a\tb",
    "a\nb",
    "a/b",
    "a\\b",
    "a@b",
    "a#b",
    "a$b",
    "a%b",
    "a^b",
    "a&b",
    "a*b",
    "a+b",
    "a=b",
    "a,b",
    "a;b",
    "a?b",
    "a!b",
    "a(b",
    "a)b",
    "a[b",
    "a]b",
    "a{b",
    "a}b",
    "a<b",
    "a>b",
    'a"b',
    "a'b",

    "éx",
    "能力",
    "😀x",
)


for index, bad in enumerate(
    invalid_token_cases,
    start=1,
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
        "invalid_token_attack_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# 4 — COLLECTION TYPE ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        None,
        "semantic.read",
        b"semantic.read",
        bytearray(
            b"semantic.read"
        ),
        {
            "semantic.read":
                True
        },
        0,
        1,
        1.0,
        True,
        False,
        object(),
    ),
    start=1,
):

    try:

        capability.normalize_universal_worker_capabilities(
            bad
        )

    except capability.UniversalWorkerCapabilityError as exc:

        rejected = (
            exc.code
            == "invalid_worker_capability_collection"
        )

    else:

        rejected = False

    check(
        "collection_type_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 5 — COLLECTION ITERABLE FORMS
# ============================================================

list_result = (
    capability.normalize_universal_worker_capabilities(
        [
            "semantic.read",
            "document.extract",
        ]
    )
)

tuple_result = (
    capability.normalize_universal_worker_capabilities(
        (
            "semantic.read",
            "document.extract",
        )
    )
)

set_result = (
    capability.normalize_universal_worker_capabilities(
        {
            "semantic.read",
            "document.extract",
        }
    )
)

generator_result = (
    capability.normalize_universal_worker_capabilities(
        item
        for item in (
            "semantic.read",
            "document.extract",
        )
    )
)


expected_pair = (
    "document.extract",
    "semantic.read",
)


check(
    "list_iterable_supported",
    list_result
    == expected_pair,
)

check(
    "tuple_iterable_supported",
    tuple_result
    == expected_pair,
)

check(
    "set_iterable_deterministic",
    set_result
    == expected_pair,
)

check(
    "generator_iterable_supported",
    generator_result
    == expected_pair,
)


# ============================================================
# 6 — NORMALIZED DUPLICATE ATTACKS
# ============================================================

duplicate_cases = (
    (
        "semantic.read",
        "semantic.read",
    ),
    (
        "Semantic.Read",
        "semantic.read",
    ),
    (
        " semantic.read ",
        "semantic.read",
    ),
    (
        "\tSEMANTIC.READ\n",
        "semantic.read",
    ),
    (
        "A_B",
        "a_b",
    ),
)


for index, values in enumerate(
    duplicate_cases,
    start=1,
):

    try:

        capability.normalize_universal_worker_capabilities(
            values
        )

    except capability.UniversalWorkerCapabilityError as exc:

        rejected = (
            exc.code
            == "duplicate_worker_capability"
        )

    else:

        rejected = False

    check(
        "normalized_duplicate_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 7 — CAPABILITY COUNT BOUNDARY
# ============================================================

max_capability_collection = tuple(
    "cap"
    + str(index).zfill(
        4
    )
    for index in range(
        capability.MAX_UNIVERSAL_WORKER_CAPABILITIES
    )
)


max_result = (
    capability.normalize_universal_worker_capabilities(
        max_capability_collection
    )
)


check(
    "max_capability_count_accepted",
    len(
        max_result
    )
    == capability.MAX_UNIVERSAL_WORKER_CAPABILITIES,
)


overflow_collection = (
    max_capability_collection
    + (
        "overflow.cap",
    )
)


try:

    capability.normalize_universal_worker_capabilities(
        overflow_collection
    )

except capability.UniversalWorkerCapabilityError as exc:

    rejected = (
        exc.code
        == "worker_capability_count_too_large"
    )

else:

    rejected = False


check(
    "capability_count_overflow_rejected",
    rejected,
)


# ============================================================
# 8 — REGISTRATION TYPE ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        "",
        "worker-a",
        [],
        {},
        (),
        set(),
        object(),
    ),
    start=1,
):

    try:

        capability.create_universal_worker_capability_snapshot(
            registration=bad,
            capabilities=(),
        )

    except capability.UniversalWorkerCapabilityError as exc:

        rejected = (
            exc.code
            == "invalid_worker_capability_registration"
        )

    else:

        rejected = False

    check(
        "registration_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 9 — SNAPSHOT IDENTITY FORGERY
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
        "worker_id",
        "\t",
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
        "worker_instance_id",
        "\t",
    ),
    (
        "worker_type",
        "",
    ),
    (
        "worker_type",
        " ",
    ),
    (
        "worker_type",
        "\t",
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
            "snapshot_identity_forgery_"
            + field_name
            + "_"
            + repr(
                bad_value
            )
        ),
        rejected,
    )


# ============================================================
# 10 — RESULT IDENTITY FORGERY
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

        "worker_capabilities":
            (),

        "required_capabilities":
            (),

        "missing_capabilities":
            (),

        "compatible":
            True,
    }

    kwargs[
        field_name
    ] = bad_value

    try:

        capability.UniversalWorkerCapabilityMatchResult(
            **kwargs
        )

    except capability.UniversalWorkerCapabilityError:

        rejected = True

    else:

        rejected = False

    check(
        (
            "result_identity_forgery_"
            + field_name
            + "_"
            + repr(
                bad_value
            )
        ),
        rejected,
    )


# ============================================================
# 11 — SNAPSHOT DIRECT COLLECTION ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        None,
        "semantic.read",
        b"semantic.read",
        bytearray(
            b"semantic.read"
        ),
        {
            "semantic.read":
                True
        },
        True,
        False,
        1,
    ),
    start=1,
):

    try:

        capability.UniversalWorkerCapabilitySnapshot(
            worker_id=reg.worker_id,
            worker_instance_id=reg.worker_instance_id,
            worker_type=reg.worker_type,
            capabilities=bad,
        )

    except capability.UniversalWorkerCapabilityError:

        rejected = True

    else:

        rejected = False

    check(
        "snapshot_collection_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 12 — SNAPSHOT DUPLICATE FORGERY
# ============================================================

try:

    capability.UniversalWorkerCapabilitySnapshot(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        capabilities=(
            "Semantic.Read",
            "semantic.read",
        ),
    )

except capability.UniversalWorkerCapabilityError as exc:

    rejected = (
        exc.code
        == "duplicate_worker_capability"
    )

else:

    rejected = False


check(
    "snapshot_normalized_duplicate_rejected",
    rejected,
)


# ============================================================
# 13 — SNAPSHOT ORDER CANONICALIZATION
# ============================================================

unordered_snapshot = (
    capability.UniversalWorkerCapabilitySnapshot(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        capabilities=(
            "z.cap",
            "a.cap",
            "m.cap",
        ),
    )
)


check(
    "snapshot_direct_order_canonicalized",
    unordered_snapshot.capabilities
    == (
        "a.cap",
        "m.cap",
        "z.cap",
    ),
)


# ============================================================
# 14 — SUPPORT API SNAPSHOT ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        "",
        [],
        {},
        (),
        object(),
    ),
    start=1,
):

    try:

        capability.supports_universal_worker_capability(
            snapshot=bad,
            capability="semantic.read",
        )

    except capability.UniversalWorkerCapabilityError as exc:

        rejected = (
            exc.code
            == "invalid_worker_capability_snapshot"
        )

    else:

        rejected = False

    check(
        "support_snapshot_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 15 — SUPPORT TOKEN ATTACKS
# ============================================================

base_snapshot = (
    capability.create_universal_worker_capability_snapshot(
        registration=reg,
        capabilities=(
            "semantic.read",
            "document.extract",
            "article.validate",
        ),
    )
)


for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        "",
        " ",
        "a",
        "_semantic.read",
        "semantic read",
    ),
    start=1,
):

    try:

        capability.supports_universal_worker_capability(
            snapshot=base_snapshot,
            capability=bad,
        )

    except capability.UniversalWorkerCapabilityError:

        rejected = True

    else:

        rejected = False

    check(
        "support_token_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 16 — MATCH API SNAPSHOT ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        "",
        [],
        {},
        (),
        object(),
    ),
    start=1,
):

    try:

        capability.match_universal_worker_capabilities(
            snapshot=bad,
            required_capabilities=(),
        )

    except capability.UniversalWorkerCapabilityError as exc:

        rejected = (
            exc.code
            == "invalid_worker_capability_snapshot"
        )

    else:

        rejected = False

    check(
        "match_snapshot_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 17 — REQUIRED-COLLECTION ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        None,
        "semantic.read",
        b"semantic.read",
        bytearray(
            b"semantic.read"
        ),
        {
            "semantic.read":
                True
        },
        True,
        False,
        1,
        object(),
    ),
    start=1,
):

    try:

        capability.match_universal_worker_capabilities(
            snapshot=base_snapshot,
            required_capabilities=bad,
        )

    except capability.UniversalWorkerCapabilityError as exc:

        rejected = (
            exc.code
            == "invalid_worker_capability_collection"
        )

    else:

        rejected = False

    check(
        "required_collection_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 18 — REQUIRED NORMALIZED DUPLICATES
# ============================================================

try:

    capability.match_universal_worker_capabilities(
        snapshot=base_snapshot,
        required_capabilities=(
            "Semantic.Read",
            "semantic.read",
        ),
    )

except capability.UniversalWorkerCapabilityError as exc:

    rejected = (
        exc.code
        == "duplicate_worker_capability"
    )

else:

    rejected = False


check(
    "required_normalized_duplicate_rejected",
    rejected,
)


# ============================================================
# 19 — ALL-REQUIRED MATCH MATRIX
# ============================================================

match_cases = (
    (
        (),
        True,
        (),
    ),
    (
        (
            "semantic.read",
        ),
        True,
        (),
    ),
    (
        (
            "semantic.read",
            "article.validate",
        ),
        True,
        (),
    ),
    (
        (
            "document.extract",
            "semantic.read",
            "article.validate",
        ),
        True,
        (),
    ),
    (
        (
            "body_store.repair",
        ),
        False,
        (
            "body_store.repair",
        ),
    ),
    (
        (
            "semantic.read",
            "body_store.repair",
        ),
        False,
        (
            "body_store.repair",
        ),
    ),
    (
        (
            "z.cap",
            "a.cap",
        ),
        False,
        (
            "a.cap",
            "z.cap",
        ),
    ),
)


for index, (
    required,
    expected_compatible,
    expected_missing,
) in enumerate(
    match_cases,
    start=1,
):

    result = (
        capability.match_universal_worker_capabilities(
            snapshot=base_snapshot,
            required_capabilities=required,
        )
    )

    check(
        "match_matrix_compatible_"
        + str(index),
        result.compatible
        is expected_compatible,
    )

    check(
        "match_matrix_missing_"
        + str(index),
        result.missing_capabilities
        == expected_missing,
        result.missing_capabilities,
    )


# ============================================================
# 20 — RESULT MISSING-SET FORGERY
# ============================================================

for index, (
    worker_caps,
    required_caps,
    forged_missing,
) in enumerate(
    (
        (
            (
                "semantic.read",
            ),
            (
                "semantic.read",
            ),
            (
                "semantic.read",
            ),
        ),
        (
            (
                "semantic.read",
            ),
            (
                "semantic.read",
                "body_store.repair",
            ),
            (),
        ),
        (
            (
                "semantic.read",
            ),
            (
                "semantic.read",
                "body_store.repair",
            ),
            (
                "semantic.read",
            ),
        ),
        (
            (),
            (
                "z.cap",
                "a.cap",
            ),
            (
                "a.cap",
            ),
        ),
    ),
    start=1,
):

    try:

        capability.UniversalWorkerCapabilityMatchResult(
            worker_id=reg.worker_id,
            worker_instance_id=reg.worker_instance_id,
            worker_type=reg.worker_type,
            worker_capabilities=worker_caps,
            required_capabilities=required_caps,
            missing_capabilities=forged_missing,
            compatible=False,
        )

    except capability.UniversalWorkerCapabilityError:

        rejected = True

    else:

        rejected = False

    check(
        "missing_set_forgery_"
        + str(index),
        rejected,
    )


# ============================================================
# 21 — COMPATIBLE TYPE ATTACK
# ============================================================

for index, bad_compatible in enumerate(
    (
        None,
        0,
        1,
        "",
        "true",
        [],
        {},
    ),
    start=1,
):

    try:

        capability.UniversalWorkerCapabilityMatchResult(
            worker_id=reg.worker_id,
            worker_instance_id=reg.worker_instance_id,
            worker_type=reg.worker_type,
            worker_capabilities=(),
            required_capabilities=(),
            missing_capabilities=(),
            compatible=bad_compatible,
        )

    except capability.UniversalWorkerCapabilityError as exc:

        rejected = (
            exc.code
            == "invalid_worker_capability_compatible"
        )

    else:

        rejected = False

    check(
        "compatible_type_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 22 — COMPATIBILITY FORGERY
# ============================================================

for index, (
    worker_caps,
    required_caps,
    missing_caps,
    forged_compatible,
) in enumerate(
    (
        (
            (),
            (),
            (),
            False,
        ),
        (
            (
                "semantic.read",
            ),
            (
                "semantic.read",
            ),
            (),
            False,
        ),
        (
            (),
            (
                "semantic.read",
            ),
            (
                "semantic.read",
            ),
            True,
        ),
    ),
    start=1,
):

    try:

        capability.UniversalWorkerCapabilityMatchResult(
            worker_id=reg.worker_id,
            worker_instance_id=reg.worker_instance_id,
            worker_type=reg.worker_type,
            worker_capabilities=worker_caps,
            required_capabilities=required_caps,
            missing_capabilities=missing_caps,
            compatible=forged_compatible,
        )

    except capability.UniversalWorkerCapabilityError as exc:

        rejected = (
            exc.code
            == "inconsistent_worker_capability_compatibility"
        )

    else:

        rejected = False

    check(
        "compatibility_forgery_"
        + str(index),
        rejected,
    )


# ============================================================
# 23 — RESULT COLLECTION CANONICALIZATION
# ============================================================

canonicalized_result = (
    capability.UniversalWorkerCapabilityMatchResult(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        worker_capabilities=(
            "z.cap",
            "a.cap",
        ),
        required_capabilities=(
            "m.cap",
            "a.cap",
        ),
        missing_capabilities=(
            "m.cap",
        ),
        compatible=False,
    )
)


check(
    "result_worker_caps_sorted",
    canonicalized_result.worker_capabilities
    == (
        "a.cap",
        "z.cap",
    ),
)

check(
    "result_required_caps_sorted",
    canonicalized_result.required_capabilities
    == (
        "a.cap",
        "m.cap",
    ),
)

check(
    "result_missing_caps_sorted",
    canonicalized_result.missing_capabilities
    == (
        "m.cap",
    ),
)


# ============================================================
# 24 — SCHEMA ATTACKS
# ============================================================

for bad_schema in (
    "",
    " ",
    "wrong",
    "universal_worker_capability_snapshot_schema_v2",
):

    try:

        capability.UniversalWorkerCapabilitySnapshot(
            worker_id=reg.worker_id,
            worker_instance_id=reg.worker_instance_id,
            worker_type=reg.worker_type,
            capabilities=(),
            schema_version=bad_schema,
        )

    except capability.UniversalWorkerCapabilityError as exc:

        rejected = (
            exc.code
            == "invalid_worker_capability_snapshot_schema_version"
        )

    else:

        rejected = False

    check(
        "snapshot_schema_attack_"
        + repr(
            bad_schema
        ),
        rejected,
    )


for bad_schema in (
    "",
    " ",
    "wrong",
    "universal_worker_capability_match_schema_v2",
):

    try:

        capability.UniversalWorkerCapabilityMatchResult(
            worker_id=reg.worker_id,
            worker_instance_id=reg.worker_instance_id,
            worker_type=reg.worker_type,
            worker_capabilities=(),
            required_capabilities=(),
            missing_capabilities=(),
            compatible=True,
            schema_version=bad_schema,
        )

    except capability.UniversalWorkerCapabilityError as exc:

        rejected = (
            exc.code
            == "invalid_worker_capability_match_schema_version"
        )

    else:

        rejected = False

    check(
        "match_schema_attack_"
        + repr(
            bad_schema
        ),
        rejected,
    )


# ============================================================
# 25 — IMMUTABILITY
# ============================================================

canonical_snapshot = (
    capability.create_universal_worker_capability_snapshot(
        registration=reg,
        capabilities=(
            "semantic.read",
            "document.extract",
        ),
    )
)

canonical_match = (
    capability.match_universal_worker_capabilities(
        snapshot=canonical_snapshot,
        required_capabilities=(
            "semantic.read",
        ),
    )
)


for obj in (
    canonical_snapshot,
    canonical_match,
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
                + type(
                    obj
                ).__name__
                + "_"
                + field.name
            ),
            immutable,
        )


# ============================================================
# 26 — EXACT FIELD CONTRACT
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


for forbidden_field in (
    "job_id",
    "job_type",
    "pipeline",
    "stage",
    "handler",
    "handler_reference",
    "pool_id",
    "capacity",
    "available_capacity",
    "available_slots",
    "max_concurrency",
    "health",
    "health_state",
    "stale",
    "drain_state",
    "lease_id",
    "lease_owner",
    "queue_id",
    "runtime_service",
    "runtime_capability",
    "runtime_handler",
):

    check(
        "forbidden_snapshot_field_"
        + forbidden_field,
        forbidden_field
        not in snapshot_fields,
    )

    check(
        "forbidden_match_field_"
        + forbidden_field,
        forbidden_field
        not in match_fields,
    )


# ============================================================
# 27 — DETERMINISM
# ============================================================

deterministic_snapshots = tuple(
    capability.create_universal_worker_capability_snapshot(
        registration=reg,
        capabilities=values,
    )
    for values in (
        (
            "semantic.read",
            "document.extract",
            "article.validate",
        ),
        (
            "article.validate",
            "semantic.read",
            "document.extract",
        ),
        {
            "document.extract",
            "article.validate",
            "semantic.read",
        },
    )
)


check(
    "deterministic_snapshot_across_orderings",
    (
        deterministic_snapshots[0]
        == deterministic_snapshots[1]
        == deterministic_snapshots[2]
    ),
)


deterministic_matches = tuple(
    capability.match_universal_worker_capabilities(
        snapshot=deterministic_snapshots[0],
        required_capabilities=values,
    )
    for values in (
        (
            "semantic.read",
            "article.validate",
        ),
        (
            "article.validate",
            "semantic.read",
        ),
        {
            "article.validate",
            "semantic.read",
        },
    )
)


check(
    "deterministic_match_across_orderings",
    (
        deterministic_matches[0]
        == deterministic_matches[1]
        == deterministic_matches[2]
    ),
)


# ============================================================
# 28 — WORKER TYPE DOES NOT IMPLY CAPABILITY
# ============================================================

worker_type_only_snapshot = (
    capability.create_universal_worker_capability_snapshot(
        registration=reg,
        capabilities=(),
    )
)


check(
    "worker_type_does_not_imply_capability",
    worker_type_only_snapshot.capabilities
    == (),
)

check(
    "worker_type_name_not_automatically_supported",
    capability.supports_universal_worker_capability(
        snapshot=worker_type_only_snapshot,
        capability="semantic_worker",
    )
    is False,
)


# ============================================================
# 29 — DIFFERENT WORKERS CAN HAVE DIFFERENT CAPABILITIES
# ============================================================

reg_b = make_registration(
    worker_id="worker-b",
    instance_id="instance-9",
    worker_type="semantic_worker",
)

snapshot_a = (
    capability.create_universal_worker_capability_snapshot(
        registration=reg,
        capabilities=(
            "semantic.read",
        ),
    )
)

snapshot_b = (
    capability.create_universal_worker_capability_snapshot(
        registration=reg_b,
        capabilities=(
            "document.extract",
        ),
    )
)


check(
    "same_worker_type_different_capabilities_allowed",
    (
        snapshot_a.worker_type
        == snapshot_b.worker_type
        and
        snapshot_a.capabilities
        != snapshot_b.capabilities
    ),
)


# ============================================================
# 30 — NO JOB TYPE SEMANTIC COUPLING
# ============================================================

job_like_capability = (
    capability.create_universal_worker_capability_snapshot(
        registration=reg,
        capabilities=(
            "website.article.integrity",
        ),
    )
)


check(
    "generic_job_like_token_allowed_as_plain_capability",
    job_like_capability.capabilities
    == (
        "website.article.integrity",
    ),
)


# ============================================================
# 31 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    capability.explain_universal_worker_capability_v1()
)


required_explanation_checks = (
    (
        "phase",
        explanation.get(
            "phase"
        )
        == "4.1.13",
    ),
    (
        "component",
        explanation.get(
            "component"
        )
        == "Universal Worker Capability Management",
    ),
    (
        "worker_scope",
        "individual-worker"
        in explanation.get(
            "scope_rule",
            "",
        ),
    ),
    (
        "canonical_identity",
        (
            "worker_id"
            in explanation.get(
                "identity_rule",
                "",
            )
            and
            "worker_instance_id"
            in explanation.get(
                "identity_rule",
                "",
            )
        ),
    ),
    (
        "worker_type_external",
        "does not itself imply capabilities"
        in explanation.get(
            "worker_type_rule",
            "",
        ),
    ),
    (
        "generic_token_rule",
        "generic normalized"
        in explanation.get(
            "capability_rule",
            "",
        ),
    ),
    (
        "immutable_collection",
        "immutable"
        in explanation.get(
            "collection_rule",
            "",
        ),
    ),
    (
        "duplicate_free_collection",
        "duplicate-free"
        in explanation.get(
            "collection_rule",
            "",
        ),
    ),
    (
        "deterministic_collection",
        "deterministically sorted"
        in explanation.get(
            "collection_rule",
            "",
        ),
    ),
    (
        "zero_capability_valid",
        "zero capabilities"
        in explanation.get(
            "empty_snapshot_rule",
            "",
        ),
    ),
    (
        "all_required_matching",
        "ALL-required"
        in explanation.get(
            "matching_rule",
            "",
        ),
    ),
    (
        "empty_required_compatible",
        "therefore compatible"
        in explanation.get(
            "empty_requirement_rule",
            "",
        ),
    ),
    (
        "assignment_external",
        "does not assign workers"
        in explanation.get(
            "assignment_boundary",
            "",
        ),
    ),
    (
        "registration_external",
        "does not mutate"
        in explanation.get(
            "registration_boundary",
            "",
        ),
    ),
    (
        "pool_external",
        "does not imply"
        in explanation.get(
            "pool_boundary",
            "",
        ),
    ),
    (
        "capacity_external",
        "separate"
        in explanation.get(
            "capacity_boundary",
            "",
        ),
    ),
    (
        "runtime_capability_external",
        "separate"
        in explanation.get(
            "runtime_capability_boundary",
            "",
        ),
    ),
    (
        "service_capability_external",
        "runtime services"
        in explanation.get(
            "service_registry_boundary",
            "",
        ),
    ),
    (
        "runtime_registration_external",
        "job_type-to-handler"
        in explanation.get(
            "runtime_registration_boundary",
            "",
        ),
    ),
    (
        "supported_job_types_external",
        "do not define individual-worker"
        in explanation.get(
            "supported_job_type_boundary",
            "",
        ),
    ),
    (
        "execution_external",
        "does not dispatch or execute jobs"
        in explanation.get(
            "execution_boundary",
            "",
        ),
    ),
    (
        "persistence_external",
        "does not persist"
        in explanation.get(
            "persistence_boundary",
            "",
        ),
    ),
    (
        "purity",
        "no external mutation or I/O"
        in explanation.get(
            "purity_rule",
            "",
        ),
    ),
)


for name, ok in (
    required_explanation_checks
):

    check(
        "explanation_"
        + name,
        ok,
    )


# ============================================================
# 32 — PROHIBITION MATRIX
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
# 33 — IMPORT BOUNDARY
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

    elif isinstance(
        node,
        ast.Import,
    ):

        for alias in node.names:

            if alias.name.startswith(
                "backend.server"
            ):

                backend_imports.append(
                    alias.name
                )


check(
    "backend_imports_exact",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.registration",
    ],
    backend_imports,
)


# ============================================================
# 34 — API SURFACE
# ============================================================

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
# 35 — FORBIDDEN CALLS
# ============================================================

forbidden_call_names = {
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

    "send",
    "post",
    "publish",
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

    if call_name in forbidden_call_names:

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
# 36 — NO RESPONSIBILITY BLEED
# ============================================================

function_names = tuple(
    node.name.lower()
    for node in ast.walk(
        tree
    )
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    )
)


for forbidden_name_token in (
    "assign_worker",
    "lease",
    "health",
    "stale",
    "drain",
    "recover",
    "scale",
    "shutdown",
    "capacity",
    "pool_member",
    "register_handler",
    "dispatch_handler",
    "execute_job",
    "route_job",
    "runtime_service",
    "runtime_capability_registry",
):

    matches = tuple(
        name
        for name in function_names
        if forbidden_name_token in name
    )

    check(
        "no_function_bleed_"
        + forbidden_name_token,
        not matches,
        matches,
    )


# ============================================================
# 37 — NO HIDDEN JOB/HANDLER/CAPACITY POLICY
# ============================================================

source_lower = (
    source.lower()
)


for forbidden_symbol in (
    "supported_job_types =",
    "job_type:",
    "handler_reference:",
    "runtimehandlerregistration",
    "runtimeserviceregistry",
    "runtimecapabilityregistry",
    "available_capacity:",
    "available_slots:",
    "max_concurrency:",
    "pool_id:",
    "health_state:",
    "drain_state:",
    "lease_id:",
    "queue_id:",
):

    check(
        "no_hidden_policy_"
        + forbidden_symbol.replace(
            " ",
            "_"
        ),
        forbidden_symbol
        not in source_lower,
    )


# ============================================================
# 38 — PROTECTED AUTHORITY MATRIX
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
# 39 — FINAL AST RECHECK
# ============================================================

final_ast = ast_sha(
    CAPABILITY_PATH
)


check(
    "worker_capability_ast_final",
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


failures = [
    (
        name,
        detail,
    )
    for name, ok, detail
    in checks
    if not ok
]


lines = [
    (
        "PHASE 4.1.13 — UNIVERSAL WORKER "
        "CAPABILITY MANAGEMENT ADVERSARIAL REGRESSION"
    ),
    "=" * 112,
    "",
    (
        "WORKER CAPABILITY AST SHA256: "
        + final_ast
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


if failures:

    lines.extend(
        [
            "",
            "FAILURE SUMMARY",
            "-" * 112,
        ]
    )

    for name, detail in failures:

        lines.append(
            "FAIL: "
            + name
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
            "ADVERSARIAL WORKER CAPABILITY REGRESSION: "
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
        "WORKER CAPABILITY AST MODIFIED: NO",
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
            "STATUS: REGRESSION PASS "
            "— FINAL CERTIFICATION REQUIRED"
            if passed == total
            else
            "STATUS: REGRESSION FAILED "
            "— PATCH REQUIRED BEFORE CERTIFICATION"
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
        "Phase 4.1.13 Worker Capability adversarial regression failed."
    )
