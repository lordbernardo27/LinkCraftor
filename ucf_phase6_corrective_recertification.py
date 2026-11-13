from __future__ import annotations

import copy
import dataclasses
import hashlib
import importlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

PHASE6 = (
    ROOT
    / "backend/server/coordination/stage_handoff"
)

P61 = PHASE6 / "stage_result_processor.py"
P62 = PHASE6 / "output_input_mapping.py"
P63 = PHASE6 / "context_propagation.py"
P64 = PHASE6 / "artifact_reference_handoff.py"
P65 = PHASE6 / "handoff_validation.py"
P66 = PHASE6 / "handoff_certification.py"

F61 = PHASE6 / "stage_result_processor.phase_6_1.freeze.json"
F62 = PHASE6 / "output_input_mapping.phase_6_2.freeze.json"
F63 = PHASE6 / "context_propagation.phase_6_3.freeze.json"
F64 = PHASE6 / "artifact_reference_handoff.phase_6_4.freeze.json"
F65 = PHASE6 / "handoff_validation.phase_6_5.freeze.json"
F66 = PHASE6 / "handoff_certification.phase_6_6.freeze.json"

RESULT_CONTRACT = (
    ROOT
    / "backend/server/coordination/universal_stages/result_contract.py"
)

CORRECTIVE_REPORT = (
    ROOT
    / "phase_6_corrective_recertification_report.txt"
)

CORRECTIVE_FREEZE = (
    PHASE6
    / "phase_6_corrective_recertification.freeze.json"
)


OLD = {
    "61_source":
        "8106D844B0B4D1C4D4E3A07A6232F4796010C604F538ED0F8E45F823D2C64456",

    "62_source":
        "ADEB1AC79CD14EDD55706FB119B30D72EC9D22CC4E1C555FED03BC8112C4A744",

    "63_source":
        "1060639F9B8BB20AFDD5B3D42E4265DDD082E267631EFEA08AD5295FCC17B596",

    "64_source":
        "8D3C80C1B9B5FEC1D1EF225F97CB0300D018E8FCFDD93F7E4E874FA0D45D3655",

    "65_source":
        "725F30637C686889B2A77F7B30EB297B0C35755002CAE245E4D45D105EFB07EE",

    "66_source":
        "FC540DEFC9BAE2AB5FA974CC54AEB03450256C5865CDAA81EEA2EB3152D20977",

    "61_freeze":
        "58AD1700AC8EA9BB838EC9E11273A7723D9D7C1F80D5FCB6222AFE563FB2017F",

    "62_freeze":
        "DB45DE654E1CA336A35150EF11142B36CFDF3ED2FFE4AA46D03568939E9D5C5E",

    "63_freeze":
        "39AD8A1ABF7753F0A5E8A9F2195E60495CCC38708DDDAAC01C8BDF8885B555D1",

    "64_freeze":
        "71B3A04739CB2D00D7A0DBC7EB7E86F820F3930BD2C4E20F375906E58C74857C",

    "65_freeze":
        "AB31AFF04CBE02F154278A9CB581CA6E777DBE143B13B37605553E006D286868",

    "66_freeze":
        "3B84DA7C33FB621A922EC60D3F3D641CC887AD26F405E9BCA6DAF04C447CEC2D",

    "stage_result_contract":
        "B3469B10BB2F8F9372E4336784D09A143C78FABE45BF039B61B76F4A2DC33B24",
}


def sha(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def section(title: str) -> None:
    print()
    print("=" * 120)
    print(title)
    print("=" * 120)


checks = []


def check(
    name: str,
    condition,
) -> None:

    ok = bool(condition)

    checks.append(
        (
            name,
            ok,
        )
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if not ok:
        raise RuntimeError(
            f"Check failed: {name}"
        )


def replace_once(
    text: str,
    old: str,
    new: str,
    label: str,
) -> str:

    count = text.count(
        old
    )

    if count != 1:
        raise RuntimeError(
            f"{label}: expected exactly one occurrence, found {count}"
        )

    return text.replace(
        old,
        new,
        1,
    )


def recursive_replace(
    value,
    replacements: dict[str, str],
):

    if isinstance(
        value,
        dict,
    ):
        return {
            key:
                recursive_replace(
                    item,
                    replacements,
                )
            for key, item
            in value.items()
        }

    if isinstance(
        value,
        list,
    ):
        return [
            recursive_replace(
                item,
                replacements,
            )
            for item
            in value
        ]

    if isinstance(
        value,
        str,
    ):
        result = value

        for old, new in replacements.items():
            result = result.replace(
                old,
                new,
            )

        return result

    return value


def write_json(
    path: Path,
    data,
) -> None:

    path.write_text(
        json.dumps(
            data,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def purge_modules() -> None:

    prefixes = (
        "backend.server.coordination.stage_handoff",
        "backend.server.coordination.universal_stages.result_contract",
    )

    for name in tuple(
        sys.modules
    ):

        if name.startswith(
            prefixes
        ):
            sys.modules.pop(
                name,
                None,
            )

    importlib.invalidate_caches()


section(
    "PHASE 6 CERTIFIED DEFECT CORRECTION"
)


# ==================================================================
# 0 — EXACT PRE-PATCH AUTHORITY
# ==================================================================

section(
    "0 — PRE-PATCH FROZEN AUTHORITY GUARD"
)


for path, expected in (
    (
        P61,
        OLD["61_source"],
    ),
    (
        P62,
        OLD["62_source"],
    ),
    (
        P63,
        OLD["63_source"],
    ),
    (
        P64,
        OLD["64_source"],
    ),
    (
        P65,
        OLD["65_source"],
    ),
    (
        P66,
        OLD["66_source"],
    ),
    (
        F61,
        OLD["61_freeze"],
    ),
    (
        F62,
        OLD["62_freeze"],
    ),
    (
        F63,
        OLD["63_freeze"],
    ),
    (
        F64,
        OLD["64_freeze"],
    ),
    (
        F65,
        OLD["65_freeze"],
    ),
    (
        F66,
        OLD["66_freeze"],
    ),
    (
        RESULT_CONTRACT,
        OLD["stage_result_contract"],
    ),
):

    check(
        f"exact frozen authority: {path.name}",
        path.exists()
        and sha(path)
        == expected,
    )


check(
    "corrective freeze does not already exist",
    not CORRECTIVE_FREEZE.exists(),
)


# Preserve all Phase 7/8 files as a before/after protection set.

later_roots = [
    ROOT
    / "backend/server/coordination/advanced_orchestration",

    ROOT
    / "backend/server/coordination/workflow_persistence",
]


later_before = {}

for later_root in later_roots:

    if not later_root.exists():
        continue

    for path in later_root.rglob("*"):

        if path.is_file():
            later_before[
                path.resolve()
            ] = sha(
                path
            )


# ==================================================================
# 1 — BACKUP
# ==================================================================

section(
    "1 — CORRECTIVE BACKUP"
)


stamp = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

backup = (
    ROOT
    / "backend/server/data/runtime_backups"
    / f"ucf_phase6_corrective_{stamp}"
)

backup.mkdir(
    parents=True,
    exist_ok=False,
)


canonical_targets = [
    P61,
    P66,
    F61,
    F63,
    F64,
    F65,
    F66,
]


for path in canonical_targets:

    shutil.copy2(
        path,
        backup
        / path.name,
    )


print(
    "BACKUP:",
    backup,
)


created_files = [
    CORRECTIVE_REPORT,
    CORRECTIVE_FREEZE,
]

for filename in (
    "stage_result_processor_phase_6_1_corrective_certification.txt",
    "context_propagation_phase_6_3_lineage_refresh.txt",
    "artifact_reference_handoff_phase_6_4_lineage_refresh.txt",
    "handoff_validation_phase_6_5_lineage_refresh.txt",
    "handoff_certification_phase_6_6_corrective_certification.txt",
):

    created_files.append(
        ROOT
        / filename
    )


try:

    # ==============================================================
    # 2 — PATCH 6.1
    # ==============================================================

    section(
        "2 — PATCH 6.1 STAGE RESULT PROCESSOR"
    )


    source = P61.read_text(
        encoding="utf-8"
    )


    source = replace_once(
        source,
        '"stage_result_processor_v6.1.0"',
        '"stage_result_processor_v6.1.1"',
        "6.1 processor version",
    )


    source = replace_once(
        source,
        '"stage_result_processor_schema_v1"',
        '"stage_result_processor_schema_v2"',
        "6.1 schema version",
    )


    # Add canonical execution target immediately after source identity.
    source = replace_once(
        source,

        '''    workspace_id: str

    job_id: str
    job_type: str
''',

        '''    workspace_id: str

    # Canonical source execution authority preserved from
    # UniversalStageResult.
    execution_target: Any

    job_id: str
    job_type: str
''',

        "6.1 execution_target field",
    )


    # Preserve canonical timing and contract lineage.
    source = replace_once(
        source,

        '''    artifact_references: Tuple[str, ...]

    failure_code: str
''',

        '''    artifact_references: Tuple[str, ...]

    # Canonical terminal timing evidence.
    started_at: str
    finished_at: str

    failure_code: str
''',

        "6.1 timing fields",
    )


    source = replace_once(
        source,

        '''    metadata: Mapping[str, Any]

    source_result_contract_version: str
''',

        '''    metadata: Mapping[str, Any]

    # Canonical contract lineage from UniversalStageResult.
    workflow_contract_version: str
    stage_reference_contract_version: str
    source_result_contract_version: str
''',

        "6.1 contract-lineage fields",
    )


    # Add mappings to ProcessedStageResult construction.
    source = replace_once(
        source,

        '''        workspace_id=
            result.workspace_id,

        job_id=
''',

        '''        workspace_id=
            result.workspace_id,

        execution_target=
            result.execution_target,

        job_id=
''',

        "6.1 execution_target mapping",
    )


    source = replace_once(
        source,

        '''        artifact_references=
            tuple(
                result.artifact_references
            ),

        failure_code=
''',

        '''        artifact_references=
            tuple(
                result.artifact_references
            ),

        started_at=
            result.started_at,

        finished_at=
            result.finished_at,

        failure_code=
''',

        "6.1 timing mapping",
    )


    source = replace_once(
        source,

        '''        metadata=
            result.metadata,

        source_result_contract_version=
            result.contract_version,
''',

        '''        metadata=
            result.metadata,

        workflow_contract_version=
            result.workflow_contract_version,

        stage_reference_contract_version=
            result.stage_reference_contract_version,

        source_result_contract_version=
            result.contract_version,
''',

        "6.1 contract-lineage mapping",
    )


    # Add canonical fields to serialized processed evidence.
    source = replace_once(
        source,

        '''            "workspace_id":
                self.workspace_id,

            "job_id":
''',

        '''            "workspace_id":
                self.workspace_id,

            "execution_target":
                (
                    self.execution_target.value
                    if hasattr(
                        self.execution_target,
                        "value",
                    )
                    else str(
                        self.execution_target
                    )
                ),

            "job_id":
''',

        "6.1 execution_target serialization",
    )


    source = replace_once(
        source,

        '''            "artifact_references":
                list(
                    self.artifact_references
                ),

            "failure_code":
''',

        '''            "artifact_references":
                list(
                    self.artifact_references
                ),

            "started_at":
                self.started_at,

            "finished_at":
                self.finished_at,

            "failure_code":
''',

        "6.1 timing serialization",
    )


    source = replace_once(
        source,

        '''            "metadata":
                _thaw(
                    self.metadata
                ),

            "source_result_contract_version":
''',

        '''            "metadata":
                _thaw(
                    self.metadata
                ),

            "workflow_contract_version":
                self.workflow_contract_version,

            "stage_reference_contract_version":
                self.stage_reference_contract_version,

            "source_result_contract_version":
''',

        "6.1 contract-lineage serialization",
    )


    P61.write_text(
        source,
        encoding="utf-8",
    )


    NEW61 = sha(
        P61
    )


    check(
        "6.1 source changed",
        NEW61
        != OLD["61_source"],
    )


    print(
        "NEW 6.1 SHA256:",
        NEW61,
    )


    # ==============================================================
    # 3 — REAL 6.1 FIELD-PRESERVATION PROOF
    # ==============================================================

    section(
        "3 — 6.1 CANONICAL FIELD-PRESERVATION PROOF"
    )


    purge_modules()


    result_mod = importlib.import_module(
        "backend.server.coordination.universal_stages.result_contract"
    )

    processor_mod = importlib.import_module(
        "backend.server.coordination.stage_handoff.stage_result_processor"
    )


    UniversalStageResult = (
        result_mod.UniversalStageResult
    )

    UniversalStageResultStatus = (
        result_mod.UniversalStageResultStatus
    )

    StageExecutionTarget = getattr(
        result_mod,
        "StageExecutionTarget",
    )


    target = tuple(
        StageExecutionTarget
    )[0]


    canonical = UniversalStageResult(
        result_id=
            "result_phase6_corrective_probe",

        workflow_id=
            "workflow_phase6_corrective_probe",

        correlation_id=
            "correlation_phase6_corrective_probe",

        stage_id=
            "stage_phase6_corrective_probe",

        stage_version=
            "1.0.0",

        pipeline_id=
            "pipeline_phase6_corrective_probe",

        workflow_type=
            "corrective_probe",

        workspace_id=
            "workspace_phase6_corrective_probe",

        execution_target=
            target,

        job_id=
            "job_phase6_corrective_probe",

        job_type=
            "corrective_probe_job",

        status=
            UniversalStageResultStatus.COMPLETED,

        output={
            "probe":
                True,
        },

        result_reference=
            "result://phase6-corrective-probe",

        artifact_references=(),

        started_at=
            "2026-11-08T00:00:00+00:00",

        finished_at=
            "2026-11-08T00:00:01+00:00",

        failure_code="",
        failure_message="",
        failure_details={},

        metadata={
            "probe":
                True,
        },
    )


    validation = canonical.validate()


    check(
        "canonical probe validates",
        validation.is_valid,
    )


    processed = (
        processor_mod.process_stage_result(
            canonical
        )
    )


    processed_fields = tuple(
        field.name
        for field
        in dataclasses.fields(
            processor_mod.ProcessedStageResult
        )
    )


    for field_name in (
        "execution_target",
        "started_at",
        "finished_at",
        "workflow_contract_version",
        "stage_reference_contract_version",
        "source_result_contract_version",
    ):

        check(
            f"ProcessedStageResult field exists: {field_name}",
            field_name
            in processed_fields,
        )


    check(
        "execution_target preserved exactly",
        processed.execution_target
        == canonical.execution_target,
    )

    check(
        "started_at preserved exactly",
        processed.started_at
        == canonical.started_at,
    )

    check(
        "finished_at preserved exactly",
        processed.finished_at
        == canonical.finished_at,
    )

    check(
        "workflow_contract_version preserved exactly",
        processed.workflow_contract_version
        == canonical.workflow_contract_version,
    )

    check(
        "stage_reference_contract_version preserved exactly",
        processed.stage_reference_contract_version
        == canonical.stage_reference_contract_version,
    )

    check(
        "contract_version mapped to source_result_contract_version",
        processed.source_result_contract_version
        == canonical.contract_version,
    )

    check(
        "status remains represented by disposition",
        processed.disposition.value
        == canonical.status.value,
    )


    serialized = (
        processed.to_dict()
    )


    for field_name in (
        "execution_target",
        "started_at",
        "finished_at",
        "workflow_contract_version",
        "stage_reference_contract_version",
        "source_result_contract_version",
    ):

        check(
            f"serialized processed evidence contains {field_name}",
            field_name
            in serialized,
        )


    check(
        "processor version bumped",
        processor_mod.STAGE_RESULT_PROCESSOR_VERSION
        == "stage_result_processor_v6.1.1",
    )

    check(
        "processor schema bumped",
        processor_mod.STAGE_RESULT_PROCESSOR_SCHEMA_VERSION
        == "stage_result_processor_schema_v2",
    )


    # ==============================================================
    # 4 — VERIFY 6.2–6.5 PRODUCTION SOURCES REMAIN EXACT
    # ==============================================================

    section(
        "4 — 6.2–6.5 PRODUCTION IMMUTABILITY"
    )


    for path, expected in (
        (
            P62,
            OLD["62_source"],
        ),
        (
            P63,
            OLD["63_source"],
        ),
        (
            P64,
            OLD["64_source"],
        ),
        (
            P65,
            OLD["65_source"],
        ),
    ):

        check(
            f"{path.name} unchanged",
            sha(path)
            == expected,
        )


    # Ensure the downstream modules still import with the enlarged
    # ProcessedStageResult contract.

    for module_name in (
        "backend.server.coordination.stage_handoff.output_input_mapping",
        "backend.server.coordination.stage_handoff.context_propagation",
        "backend.server.coordination.stage_handoff.artifact_reference_handoff",
        "backend.server.coordination.stage_handoff.handoff_validation",
    ):

        module = importlib.import_module(
            module_name
        )

        check(
            f"downstream import compatible: {module_name}",
            module is not None,
        )


    # ==============================================================
    # 5 — REPLACEMENT 6.1 CERTIFICATION + FREEZE
    # ==============================================================

    section(
        "5 — REPLACEMENT 6.1 CERTIFICATION + FREEZE"
    )


    report61 = (
        ROOT
        / "stage_result_processor_phase_6_1_corrective_certification.txt"
    )


    report61.write_text(
        "\n".join(
            (
                "LINKCRAFTOR",
                "UNIVERSAL COORDINATION FRAMEWORK",
                "PHASE 6.1 — CORRECTIVE CERTIFICATION",
                "",
                "Certified defect:",
                "Canonical UniversalStageResult fields were previously dropped.",
                "",
                "Corrected preservation:",
                "- execution_target",
                "- started_at",
                "- finished_at",
                "- workflow_contract_version",
                "- stage_reference_contract_version",
                "- status remains represented by disposition",
                "- contract_version remains represented by source_result_contract_version",
                "",
                "Processor version: stage_result_processor_v6.1.1",
                "Schema version: stage_result_processor_schema_v2",
                f"Source SHA256: {NEW61}",
                "",
                "6.2–6.5 production source modified: NO",
                "Runtime execution authority added: NO",
                "",
                "STATUS: CERTIFIED",
            )
        )
        + "\n",
        encoding="utf-8",
    )


    old_f61 = json.loads(
        F61.read_text(
            encoding="utf-8-sig"
        )
    )


    new_f61 = copy.deepcopy(
        old_f61
    )


    new_f61[
        "freeze_version"
    ] = "stage_result_processor_phase_6_1_freeze_v2"


    new_f61[
        "freeze_created_at"
    ] = datetime.now(
        timezone.utc
    ).isoformat()


    new_f61[
        "processor"
    ][
        "version"
    ] = "stage_result_processor_v6.1.1"


    new_f61[
        "processor"
    ][
        "schema_version"
    ] = "stage_result_processor_schema_v2"


    new_f61[
        "processor"
    ][
        "sha256"
    ] = NEW61


    new_f61[
        "final_certification_report"
    ] = {
        "path":
            report61.name,

        "sha256":
            sha(
                report61
            ),
    }


    new_f61[
        "corrective_revision"
    ] = {
        "reason":
            "Certified canonical field-loss defect",

        "supersedes_source_sha256":
            OLD["61_source"],

        "supersedes_freeze_sha256":
            OLD["61_freeze"],

        "preserved_canonical_fields": [
            "execution_target",
            "started_at",
            "finished_at",
            "workflow_contract_version",
            "stage_reference_contract_version",
        ],

        "status_mapping":
            "status -> disposition",

        "contract_mapping":
            "contract_version -> source_result_contract_version",
    }


    write_json(
        F61,
        new_f61,
    )


    NEWF61 = sha(
        F61
    )


    print(
        "NEW 6.1 FREEZE SHA256:",
        NEWF61,
    )


    # ==============================================================
    # 6 — REFRESH 6.3 LINEAGE FREEZE
    # ==============================================================

    section(
        "6 — REFRESH 6.3 LINEAGE"
    )


    report63 = (
        ROOT
        / "context_propagation_phase_6_3_lineage_refresh.txt"
    )


    report63.write_text(
        "\n".join(
            (
                "LINKCRAFTOR UCF PHASE 6.3 LINEAGE REFRESH",
                f"Production source SHA256: {sha(P63)}",
                "Production source modified: NO",
                f"Replacement Phase 6.1 source SHA256: {NEW61}",
                f"Replacement Phase 6.1 freeze SHA256: {NEWF61}",
                "ProcessedStageResult import compatibility: PASS",
                "STATUS: RE-CERTIFIED AGAINST CORRECTED 6.1 AUTHORITY",
            )
        )
        + "\n",
        encoding="utf-8",
    )


    f63 = json.loads(
        F63.read_text(
            encoding="utf-8-sig"
        )
    )


    f63 = recursive_replace(
        f63,
        {
            OLD["61_source"]:
                NEW61,

            OLD["61_freeze"]:
                NEWF61,
        },
    )


    f63[
        "freeze_version"
    ] = "context_propagation_phase_6_3_freeze_v2"


    f63[
        "freeze_created_at"
    ] = datetime.now(
        timezone.utc
    ).isoformat()


    f63[
        "final_certification_report"
    ] = {
        "path":
            report63.name,

        "sha256":
            sha(
                report63
            ),
    }


    f63[
        "lineage_refresh"
    ] = {
        "reason":
            "Phase 6.1 corrective revision",

        "production_source_modified":
            False,

        "supersedes_freeze_sha256":
            OLD["63_freeze"],
    }


    write_json(
        F63,
        f63,
    )


    NEWF63 = sha(
        F63
    )


    print(
        "NEW 6.3 FREEZE SHA256:",
        NEWF63,
    )


    # ==============================================================
    # 7 — REFRESH 6.4 LINEAGE FREEZE
    # ==============================================================

    section(
        "7 — REFRESH 6.4 LINEAGE"
    )


    report64 = (
        ROOT
        / "artifact_reference_handoff_phase_6_4_lineage_refresh.txt"
    )


    report64.write_text(
        "\n".join(
            (
                "LINKCRAFTOR UCF PHASE 6.4 LINEAGE REFRESH",
                f"Production source SHA256: {sha(P64)}",
                "Production source modified: NO",
                f"Replacement Phase 6.1 source SHA256: {NEW61}",
                f"Replacement Phase 6.1 freeze SHA256: {NEWF61}",
                f"Replacement Phase 6.3 freeze SHA256: {NEWF63}",
                "ProcessedStageResult import compatibility: PASS",
                "STATUS: RE-CERTIFIED AGAINST CORRECTED UPSTREAM LINEAGE",
            )
        )
        + "\n",
        encoding="utf-8",
    )


    f64 = json.loads(
        F64.read_text(
            encoding="utf-8-sig"
        )
    )


    f64 = recursive_replace(
        f64,
        {
            OLD["61_source"]:
                NEW61,

            OLD["61_freeze"]:
                NEWF61,

            OLD["63_freeze"]:
                NEWF63,
        },
    )


    f64[
        "freeze_version"
    ] = "artifact_reference_handoff_phase_6_4_freeze_v2"


    f64[
        "freeze_created_at"
    ] = datetime.now(
        timezone.utc
    ).isoformat()


    f64[
        "final_certification_report"
    ] = {
        "path":
            report64.name,

        "sha256":
            sha(
                report64
            ),
    }


    f64[
        "lineage_refresh"
    ] = {
        "reason":
            "Phase 6.1 corrective revision",

        "production_source_modified":
            False,

        "supersedes_freeze_sha256":
            OLD["64_freeze"],
    }


    write_json(
        F64,
        f64,
    )


    NEWF64 = sha(
        F64
    )


    print(
        "NEW 6.4 FREEZE SHA256:",
        NEWF64,
    )


    # ==============================================================
    # 8 — REFRESH 6.5 LINEAGE FREEZE
    # ==============================================================

    section(
        "8 — REFRESH 6.5 LINEAGE"
    )


    report65 = (
        ROOT
        / "handoff_validation_phase_6_5_lineage_refresh.txt"
    )


    report65.write_text(
        "\n".join(
            (
                "LINKCRAFTOR UCF PHASE 6.5 LINEAGE REFRESH",
                f"Production source SHA256: {sha(P65)}",
                "Production source modified: NO",
                f"Replacement Phase 6.1 source SHA256: {NEW61}",
                f"Replacement Phase 6.1 freeze SHA256: {NEWF61}",
                f"Replacement Phase 6.3 freeze SHA256: {NEWF63}",
                f"Replacement Phase 6.4 freeze SHA256: {NEWF64}",
                "ProcessedStageResult type compatibility: PASS",
                "STATUS: RE-CERTIFIED AGAINST CORRECTED UPSTREAM LINEAGE",
            )
        )
        + "\n",
        encoding="utf-8",
    )


    f65 = json.loads(
        F65.read_text(
            encoding="utf-8-sig"
        )
    )


    f65 = recursive_replace(
        f65,
        {
            OLD["61_source"]:
                NEW61,

            OLD["61_freeze"]:
                NEWF61,

            OLD["63_freeze"]:
                NEWF63,

            OLD["64_freeze"]:
                NEWF64,
        },
    )


    f65[
        "freeze_version"
    ] = "handoff_validation_phase_6_5_freeze_v2"


    f65[
        "freeze_created_at"
    ] = datetime.now(
        timezone.utc
    ).isoformat()


    f65[
        "final_certification_report"
    ] = {
        "path":
            report65.name,

        "sha256":
            sha(
                report65
            ),
    }


    f65[
        "lineage_refresh"
    ] = {
        "reason":
            "Phase 6.1 corrective revision",

        "production_source_modified":
            False,

        "supersedes_freeze_sha256":
            OLD["65_freeze"],
    }


    write_json(
        F65,
        f65,
    )


    NEWF65 = sha(
        F65
    )


    print(
        "NEW 6.5 FREEZE SHA256:",
        NEWF65,
    )


    # ==============================================================
    # 9 — PATCH 6.6 CERTIFICATION AUTHORITY
    # ==============================================================

    section(
        "9 — PATCH 6.6 CERTIFICATION AUTHORITY"
    )


    source66 = P66.read_text(
        encoding="utf-8"
    )


    source66 = replace_once(
        source66,
        '"handoff_certification_v6.6.0"',
        '"handoff_certification_v6.6.1"',
        "6.6 certification version",
    )


    replacements66 = {
        OLD["61_source"]:
            NEW61,

        OLD["61_freeze"]:
            NEWF61,

        OLD["63_freeze"]:
            NEWF63,

        OLD["64_freeze"]:
            NEWF64,

        OLD["65_freeze"]:
            NEWF65,
    }


    for old_value, new_value in replacements66.items():

        if old_value not in source66:
            raise RuntimeError(
                "Expected 6.6 authority value missing: "
                + old_value
            )

        source66 = source66.replace(
            old_value,
            new_value,
        )


    P66.write_text(
        source66,
        encoding="utf-8",
    )


    NEW66 = sha(
        P66
    )


    check(
        "6.6 source changed only for corrective authority/version",
        NEW66
        != OLD["66_source"],
    )


    print(
        "NEW 6.6 SOURCE SHA256:",
        NEW66,
    )


    # ==============================================================
    # 10 — VERIFY 6.6 ACTUAL HASH MACHINERY
    # ==============================================================

    section(
        "10 — VERIFY REPLACEMENT 6.6 HASH MACHINERY"
    )


    purge_modules()


    cert_mod = importlib.import_module(
        "backend.server.coordination.stage_handoff.handoff_certification"
    )


    actual_sources = dict(
        cert_mod._actual_source_hashes()
    )


    actual_freezes = dict(
        cert_mod._actual_freeze_hashes()
    )


    expected_sources = {
        phase:
            expected
        for phase, _filename, expected
        in cert_mod._EXPECTED_SOURCE_SHA256
    }


    expected_freezes = {
        phase:
            expected
        for phase, _filename, expected
        in cert_mod._EXPECTED_FREEZE_SHA256
    }


    check(
        "6.6 source authority exactly matches actual",
        actual_sources
        == expected_sources,
    )


    check(
        "6.6 freeze authority exactly matches actual",
        actual_freezes
        == expected_freezes,
    )


    check(
        "6.6 sees replacement 6.1 source",
        actual_sources["6.1"]
        == NEW61,
    )


    check(
        "6.6 sees unchanged 6.2 source",
        actual_sources["6.2"]
        == OLD["62_source"],
    )


    check(
        "6.6 sees unchanged 6.3 source",
        actual_sources["6.3"]
        == OLD["63_source"],
    )


    check(
        "6.6 sees unchanged 6.4 source",
        actual_sources["6.4"]
        == OLD["64_source"],
    )


    check(
        "6.6 sees unchanged 6.5 source",
        actual_sources["6.5"]
        == OLD["65_source"],
    )


    composite = (
        cert_mod._phase_6_composite_fingerprint(
            tuple(
                cert_mod._actual_source_hashes()
            )
        )
    )


    print(
        "NEW PHASE 6 COMPOSITE:",
        composite,
    )


    # ==============================================================
    # 11 — REPLACEMENT 6.6 REPORT + FREEZE
    # ==============================================================

    section(
        "11 — REPLACEMENT 6.6 CERTIFICATION + FREEZE"
    )


    report66 = (
        ROOT
        / "handoff_certification_phase_6_6_corrective_certification.txt"
    )


    report66.write_text(
        "\n".join(
            (
                "LINKCRAFTOR",
                "UNIVERSAL COORDINATION FRAMEWORK",
                "PHASE 6.6 — CORRECTIVE HANDOFF CERTIFICATION",
                "",
                "Phase 6.1 corrected: YES",
                "6.2 production source changed: NO",
                "6.3 production source changed: NO",
                "6.4 production source changed: NO",
                "6.5 production source changed: NO",
                "",
                f"6.1 source SHA256: {NEW61}",
                f"6.2 source SHA256: {sha(P62)}",
                f"6.3 source SHA256: {sha(P63)}",
                f"6.4 source SHA256: {sha(P64)}",
                f"6.5 source SHA256: {sha(P65)}",
                "",
                f"6.1 freeze SHA256: {NEWF61}",
                f"6.2 freeze SHA256: {sha(F62)}",
                f"6.3 freeze SHA256: {NEWF63}",
                f"6.4 freeze SHA256: {NEWF64}",
                f"6.5 freeze SHA256: {NEWF65}",
                "",
                f"Phase 6 composite SHA256: {composite}",
                "Certification version: handoff_certification_v6.6.1",
                "",
                "STATUS: CERTIFIED",
            )
        )
        + "\n",
        encoding="utf-8",
    )


    old_f66 = json.loads(
        F66.read_text(
            encoding="utf-8-sig"
        )
    )


    new_f66 = recursive_replace(
        old_f66,
        {
            OLD["61_source"]:
                NEW61,

            OLD["61_freeze"]:
                NEWF61,

            OLD["63_freeze"]:
                NEWF63,

            OLD["64_freeze"]:
                NEWF64,

            OLD["65_freeze"]:
                NEWF65,

            OLD["66_source"]:
                NEW66,
        },
    )


    new_f66[
        "freeze_version"
    ] = "handoff_certification_phase_6_6_freeze_v2"


    new_f66[
        "freeze_created_at"
    ] = datetime.now(
        timezone.utc
    ).isoformat()


    new_f66[
        "production"
    ][
        "version"
    ] = "handoff_certification_v6.6.1"


    new_f66[
        "production"
    ][
        "sha256"
    ] = NEW66


    new_f66[
        "phase_6_composite"
    ][
        "sha256"
    ] = composite


    new_f66[
        "phase_6_predecessor_sources"
    ][
        "6.1"
    ][
        "sha256"
    ] = NEW61


    new_f66[
        "phase_6_predecessor_freezes"
    ][
        "6.1"
    ] = NEWF61


    new_f66[
        "phase_6_predecessor_freezes"
    ][
        "6.3"
    ] = NEWF63


    new_f66[
        "phase_6_predecessor_freezes"
    ][
        "6.4"
    ] = NEWF64


    new_f66[
        "phase_6_predecessor_freezes"
    ][
        "6.5"
    ] = NEWF65


    new_f66[
        "final_certification_report"
    ] = {
        "path":
            report66.name,

        "sha256":
            sha(
                report66
            ),
    }


    new_f66[
        "corrective_revision"
    ] = {
        "reason":
            "Phase 6.1 canonical field-loss defect",

        "supersedes_phase_6_composite":
            "24298F802614DDE0C794516B52B0FF40092B64F783E18351B93687BC8812D938",

        "supersedes_6_6_source_sha256":
            OLD["66_source"],

        "supersedes_6_6_freeze_sha256":
            OLD["66_freeze"],

        "6.2_to_6.5_production_sources_modified":
            False,
    }


    write_json(
        F66,
        new_f66,
    )


    NEWF66 = sha(
        F66
    )


    print(
        "NEW 6.6 FREEZE SHA256:",
        NEWF66,
    )


    # ==============================================================
    # 12 — FINAL POST-CORRECTION CERTIFICATION
    # ==============================================================

    section(
        "12 — FINAL POST-CORRECTION CERTIFICATION"
    )


    check(
        "canonical UniversalStageResult unchanged",
        sha(
            RESULT_CONTRACT
        )
        == OLD[
            "stage_result_contract"
        ],
    )


    for path, expected in (
        (
            P62,
            OLD["62_source"],
        ),
        (
            P63,
            OLD["63_source"],
        ),
        (
            P64,
            OLD["64_source"],
        ),
        (
            P65,
            OLD["65_source"],
        ),
        (
            F62,
            OLD["62_freeze"],
        ),
    ):

        check(
            f"untouched authority exact: {path.name}",
            sha(path)
            == expected,
        )


    # Ensure no Phase 7/8 file changed.
    later_after = {}

    for later_root in later_roots:

        if not later_root.exists():
            continue

        for path in later_root.rglob("*"):

            if path.is_file():

                later_after[
                    path.resolve()
                ] = sha(
                    path
                )


    check(
        "Phase 7/8 file inventory unchanged",
        set(
            later_after
        )
        == set(
            later_before
        ),
    )


    check(
        "Phase 7/8 hashes unchanged",
        later_after
        == later_before,
    )


    # Final reload verifies canonical imports after every manifest/source
    # has reached its replacement identity.
    purge_modules()


    final_processor = importlib.import_module(
        "backend.server.coordination.stage_handoff.stage_result_processor"
    )

    final_cert = importlib.import_module(
        "backend.server.coordination.stage_handoff.handoff_certification"
    )


    check(
        "final processor version",
        final_processor.STAGE_RESULT_PROCESSOR_VERSION
        == "stage_result_processor_v6.1.1",
    )


    check(
        "final processor schema",
        final_processor.STAGE_RESULT_PROCESSOR_SCHEMA_VERSION
        == "stage_result_processor_schema_v2",
    )


    check(
        "final handoff certification version",
        final_cert.HANDOFF_CERTIFICATION_VERSION
        == "handoff_certification_v6.6.1",
    )


    check(
        "final 6.6 source hashes exact",
        dict(
            final_cert._actual_source_hashes()
        )
        == {
            phase:
                expected
            for phase, _filename, expected
            in final_cert._EXPECTED_SOURCE_SHA256
        },
    )


    check(
        "final 6.6 freeze hashes exact",
        dict(
            final_cert._actual_freeze_hashes()
        )
        == {
            phase:
                expected
            for phase, _filename, expected
            in final_cert._EXPECTED_FREEZE_SHA256
        },
    )


    # ==============================================================
    # 13 — CORRECTIVE MASTER REPORT / FREEZE
    # ==============================================================

    section(
        "13 — CORRECTIVE MASTER CERTIFICATION"
    )


    passed = sum(
        1
        for _name, ok
        in checks
        if ok
    )


    CORRECTIVE_REPORT.write_text(
        "\n".join(
            (
                "LINKCRAFTOR",
                "UNIVERSAL COORDINATION FRAMEWORK",
                "PHASE 6 — CERTIFIED DEFECT CORRECTION",
                "",
                f"FORMAL CHECKS PASSED: {passed}",
                "FORMAL CHECKS FAILED: 0",
                "",
                "Corrected:",
                "- execution_target preservation",
                "- started_at preservation",
                "- finished_at preservation",
                "- workflow_contract_version preservation",
                "- stage_reference_contract_version preservation",
                "",
                "Existing mappings retained:",
                "- status -> disposition",
                "- contract_version -> source_result_contract_version",
                "",
                f"6.1 replacement SHA256: {NEW61}",
                f"6.1 replacement freeze SHA256: {NEWF61}",
                f"6.3 refreshed freeze SHA256: {NEWF63}",
                f"6.4 refreshed freeze SHA256: {NEWF64}",
                f"6.5 refreshed freeze SHA256: {NEWF65}",
                f"6.6 replacement SHA256: {NEW66}",
                f"6.6 replacement freeze SHA256: {NEWF66}",
                f"Phase 6 replacement composite SHA256: {composite}",
                "",
                "6.2–6.5 production source modified: NO",
                "Phase 7 modified: NO",
                "Phase 8 modified: NO",
                "",
                "STATUS: CERTIFIED + FROZEN",
            )
        )
        + "\n",
        encoding="utf-8",
    )


    corrective_document = {
        "framework":
            "Universal Coordination Framework",

        "phase":
            "6",

        "action":
            "certified_defect_correction",

        "certified":
            True,

        "frozen":
            True,

        "defect": {
            "component":
                "6.1 Stage Result Processor",

            "old_source_sha256":
                OLD["61_source"],

            "old_freeze_sha256":
                OLD["61_freeze"],

            "missing_fields": [
                "execution_target",
                "started_at",
                "finished_at",
                "workflow_contract_version",
                "stage_reference_contract_version",
            ],
        },

        "replacement": {
            "6.1_source_sha256":
                NEW61,

            "6.1_freeze_sha256":
                NEWF61,

            "6.2_source_sha256":
                sha(
                    P62
                ),

            "6.2_freeze_sha256":
                sha(
                    F62
                ),

            "6.3_source_sha256":
                sha(
                    P63
                ),

            "6.3_freeze_sha256":
                NEWF63,

            "6.4_source_sha256":
                sha(
                    P64
                ),

            "6.4_freeze_sha256":
                NEWF64,

            "6.5_source_sha256":
                sha(
                    P65
                ),

            "6.5_freeze_sha256":
                NEWF65,

            "6.6_source_sha256":
                NEW66,

            "6.6_freeze_sha256":
                NEWF66,

            "phase_6_composite_sha256":
                composite,
        },

        "production_changes": {
            "6.1":
                True,

            "6.2":
                False,

            "6.3":
                False,

            "6.4":
                False,

            "6.5":
                False,

            "6.6":
                True,

            "phase_7":
                False,

            "phase_8":
                False,
        },

        "backup":
            str(
                backup
                .relative_to(
                    ROOT
                )
            ),

        "certification_report": {
            "path":
                CORRECTIVE_REPORT.name,

            "sha256":
                sha(
                    CORRECTIVE_REPORT
                ),
        },

        "formal_checks_passed":
            passed,

        "created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "next":
            "Resume Phase 8.4 Pause",
    }


    write_json(
        CORRECTIVE_FREEZE,
        corrective_document,
    )


    print()
    print("=" * 120)
    print("PHASE 6 CORRECTIVE FINAL STATUS")
    print("=" * 120)

    print(
        "FORMAL CHECKS:",
        passed,
        "PASS",
    )

    print(
        "PHASE 6.1 CORRECTED: TRUE"
    )

    print(
        "PHASE 6.1 CERTIFIED + FROZEN: TRUE"
    )

    print(
        "PHASE 6.2 PRODUCTION MODIFIED: FALSE"
    )

    print(
        "PHASE 6.3 PRODUCTION MODIFIED: FALSE"
    )

    print(
        "PHASE 6.4 PRODUCTION MODIFIED: FALSE"
    )

    print(
        "PHASE 6.5 PRODUCTION MODIFIED: FALSE"
    )

    print(
        "PHASE 6.6 RE-CERTIFIED + FROZEN: TRUE"
    )

    print(
        "PHASE 7 MODIFIED: FALSE"
    )

    print(
        "PHASE 8 MODIFIED: FALSE"
    )

    print()

    print(
        "NEW 6.1 SOURCE SHA256:",
        NEW61,
    )

    print(
        "NEW 6.1 FREEZE SHA256:",
        NEWF61,
    )

    print(
        "NEW 6.3 FREEZE SHA256:",
        NEWF63,
    )

    print(
        "NEW 6.4 FREEZE SHA256:",
        NEWF64,
    )

    print(
        "NEW 6.5 FREEZE SHA256:",
        NEWF65,
    )

    print(
        "NEW 6.6 SOURCE SHA256:",
        NEW66,
    )

    print(
        "NEW 6.6 FREEZE SHA256:",
        NEWF66,
    )

    print(
        "NEW PHASE 6 COMPOSITE SHA256:",
        composite,
    )

    print(
        "CORRECTIVE MASTER FREEZE SHA256:",
        sha(
            CORRECTIVE_FREEZE
        ),
    )

    print()

    print(
        "NEXT: PHASE 8.4 PAUSE + 8.5 RESUME + "
        "8.6 RESTART RECOVERY + 8.7 PERSISTENCE CERTIFICATION"
    )

    print("=" * 120)


except Exception:

    print()
    print("=" * 120)
    print("CORRECTIVE RUN FAILED — RESTORING CANONICAL FILES")
    print("=" * 120)

    for path in canonical_targets:

        backup_file = (
            backup
            / path.name
        )

        if backup_file.exists():

            shutil.copy2(
                backup_file,
                path,
            )

    for path in created_files:

        if path.exists():
            path.unlink()

    print(
        "ROLLBACK COMPLETE."
    )

    raise
