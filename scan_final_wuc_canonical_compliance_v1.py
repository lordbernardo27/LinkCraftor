"""Final read-only canonical compliance scan for Website Unified Content."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_COUNT = 2219

SERVER_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
)

DATA_ROOT = (
    SERVER_ROOT
    / "data"
)

WUC_ROOT = (
    SERVER_ROOT
    / "website_unified_content"
)

INPUT_READER = (
    WUC_ROOT
    / "certified_wuc_input.py"
)

ENGINE = (
    WUC_ROOT
    / "website_unified_content_engine_v1.py"
)

RUNNER = (
    WUC_ROOT
    / "wuc_population_runner_v1.py"
)

INIT_FILE = (
    WUC_ROOT
    / "__init__.py"
)

VERIFICATION_REPORT = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "wuc_population_runner_v1_verification.json"
)

EVIDENCE_ROOT = (
    DATA_ROOT
    / "website_unified_content_evidence"
    / WORKSPACE_ID
    / "runs"
)

FINAL_REPORT = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "final_wuc_canonical_compliance_v1.json"
)

PROHIBITED_PATHS = [
    DATA_ROOT
    / "website_unified_content",

    DATA_ROOT
    / "website_unified_content_store",

    SERVER_ROOT
    / "stores"
    / "website_unified_content_store.py",
]

REQUIRED_PACKAGE_FIELDS = {
    "schema_version",
    "engine_version",
    "content_id",
    "document_id",
    "workspace_id",
    "source_type",
    "source_format",
    "source_identity",
    "title",
    "h1",
    "headings",
    "canonical_url",
    "content_body",
    "content_hash",
    "body_length",
    "body_word_count",
    "structure",
    "metadata",
    "handoff",
}

REQUIRED_SOURCE_IDENTITY_FIELDS = {
    "source_record_id",
    "canonical_url",
    "udare_article_path",
    "udare_article_sha256",
}

REQUIRED_STRUCTURE_FIELDS = {
    "block_count",
    "heading_count",
    "content_word_count",
    "blocks",
}

REQUIRED_BLOCK_FIELDS = {
    "block_id",
    "block_index",
    "block_type",
    "tag",
    "text",
    "text_sha256",
    "word_count",
}

REQUIRED_HEADING_FIELDS = {
    "heading_id",
    "level",
    "text",
    "block_index",
}

REQUIRED_METADATA_FIELDS = {
    "article_validation_status",
    "article_validation_run_id",
    "article_validation_certificate_id",
    "wuc_persistence_mode",
    "complete_content_preserved",
    "content_reduction_performed",
    "summarization_performed",
    "truncation_performed",
    "word_count_limit_applied",
    "article_body_persisted_by_wuc",
    "intermediate_wuc_store_created",
    "performs_reconstruction",
    "performs_article_validation",
    "performs_semantic_analysis",
}

REQUIRED_HANDOFF_FIELDS = {
    "next_stage",
    "eligible_for_uucd",
    "body_field",
    "full_body_handoff",
}

FORBIDDEN_ENGINE_CALLS = {
    "write_text",
    "write_bytes",
    "dump",
    "dumps",
    "open",
    "copy",
    "copy2",
    "copyfile",
    "mkdir",
    "makedirs",
    "unlink",
    "remove",
    "rmtree",
    "rename",
    "replace",
    "register_runtime_handler",
    "enqueue",
    "dispatch",
    "create_job",
    "submit_job",
    "build_and_write_uucd_from_wuc_v1",
    "write_uucd",
    "save_uucd",
    "upsert_uucd",
    "persist_uucd",
}

FORBIDDEN_ENGINE_IMPORT_TERMS = {
    "runtime",
    "universal_unified_content",
    "uucd",
    "universal_article_body_store",
    "article_body_store",
}


def load_json(
    path: Path,
) -> dict[str, Any]:
    value = json.loads(
        path.read_text(
            encoding="utf-8-sig",
        )
    )

    if not isinstance(
        value,
        dict,
    ):
        raise RuntimeError(
            f"Expected JSON object: {path}"
        )

    return value


def load_jsonl(
    path: Path,
) -> list[dict[str, Any]]:
    records: list[
        dict[str, Any]
    ] = []

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        for line_number, line in enumerate(
            handle,
            start=1,
        ):
            stripped = line.strip()

            if not stripped:
                continue

            value = json.loads(
                stripped
            )

            if not isinstance(
                value,
                dict,
            ):
                raise RuntimeError(
                    f"Expected JSON object at {path}:{line_number}"
                )

            records.append(
                value
            )

    return records


def function_names(
    tree: ast.AST,
) -> set[str]:
    return {
        node.name
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
    }


def call_name(
    node: ast.Call,
) -> str:
    if isinstance(
        node.func,
        ast.Name,
    ):
        return node.func.id

    if isinstance(
        node.func,
        ast.Attribute,
    ):
        return node.func.attr

    return ""


def import_names(
    tree: ast.AST,
) -> list[str]:
    names: list[str] = []

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            names.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            module = str(
                node.module or ""
            )

            names.extend(
                (
                    module
                    + "."
                    + alias.name
                ).strip(".")
                for alias in node.names
            )

    return names


def return_dictionary_keys(
    tree: ast.AST,
    function_name: str,
) -> set[str]:
    keys: set[str] = set()

    for node in ast.walk(
        tree
    ):
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        if node.name != function_name:
            continue

        for child in ast.walk(
            node
        ):
            if not isinstance(
                child,
                ast.Return,
            ):
                continue

            if not isinstance(
                child.value,
                ast.Dict,
            ):
                continue

            for key in child.value.keys:
                if (
                    isinstance(
                        key,
                        ast.Constant,
                    )
                    and isinstance(
                        key.value,
                        str,
                    )
                ):
                    keys.add(
                        key.value
                    )

    return keys


failures: list[str] = []
warnings: list[str] = []

required_files = {
    "__init__.py":
        INIT_FILE,

    "certified_wuc_input.py":
        INPUT_READER,

    "website_unified_content_engine_v1.py":
        ENGINE,

    "wuc_population_runner_v1.py":
        RUNNER,
}

for name, path in required_files.items():
    if not path.is_file():
        failures.append(
            "Missing required WUC file: "
            + name
        )


trees: dict[
    str,
    ast.AST
] = {}

if not failures:
    for name, path in required_files.items():
        source = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )

        try:
            trees[
                name
            ] = ast.parse(
                source,
                filename=str(
                    path
                ),
            )

        except SyntaxError as exc:
            failures.append(
                f"Syntax failure in {name}: "
                f"line {exc.lineno}: {exc.msg}"
            )


input_tree = trees.get(
    "certified_wuc_input.py"
)

engine_tree = trees.get(
    "website_unified_content_engine_v1.py"
)

runner_tree = trees.get(
    "wuc_population_runner_v1.py"
)


input_functions = (
    function_names(
        input_tree
    )
    if input_tree
    else set()
)

engine_functions = (
    function_names(
        engine_tree
    )
    if engine_tree
    else set()
)

runner_functions = (
    function_names(
        runner_tree
    )
    if runner_tree
    else set()
)


required_input_functions = {
    "load_article_validation_pass_contract_v1",
    "load_transient_certified_wuc_source_v1",
}

required_engine_functions = {
    "build_transient_website_unified_content_v1",
}

required_runner_functions = {
    "run_wuc_population_v1",
}


missing_input_functions = (
    required_input_functions
    - input_functions
)

missing_engine_functions = (
    required_engine_functions
    - engine_functions
)

missing_runner_functions = (
    required_runner_functions
    - runner_functions
)

if missing_input_functions:
    failures.append(
        "Missing certified-input functions: "
        + ", ".join(
            sorted(
                missing_input_functions
            )
        )
    )

if missing_engine_functions:
    failures.append(
        "Missing WUC engine functions: "
        + ", ".join(
            sorted(
                missing_engine_functions
            )
        )
    )

if missing_runner_functions:
    failures.append(
        "Missing WUC runner functions: "
        + ", ".join(
            sorted(
                missing_runner_functions
            )
        )
    )


forbidden_calls: list[
    dict[str, Any]
] = []

forbidden_imports: list[
    str
] = []

article_body_reads: list[
    str
] = []

if engine_tree:
    for node in ast.walk(
        engine_tree
    ):
        if isinstance(
            node,
            ast.Call,
        ):
            name = call_name(
                node
            )

            if name in FORBIDDEN_ENGINE_CALLS:
                forbidden_calls.append(
                    {
                        "name":
                            name,

                        "line":
                            node.lineno,
                    }
                )

            if (
                isinstance(
                    node.func,
                    ast.Attribute,
                )
                and node.func.attr
                == "get"
                and node.args
                and isinstance(
                    node.args[
                        0
                    ],
                    ast.Constant,
                )
                and node.args[
                    0
                ].value
                == "article_body"
            ):
                article_body_reads.append(
                    f"line {node.lineno}"
                )

    for imported_name in import_names(
        engine_tree
    ):
        lowered = imported_name.casefold()

        if any(
            term in lowered
            for term
            in FORBIDDEN_ENGINE_IMPORT_TERMS
        ):
            forbidden_imports.append(
                imported_name
            )


if forbidden_calls:
    failures.append(
        "Forbidden WUC engine calls detected."
    )

if forbidden_imports:
    failures.append(
        "Forbidden WUC engine imports detected."
    )

if article_body_reads:
    failures.append(
        "Legacy article_body field is read by the WUC engine."
    )


engine_return_keys = (
    return_dictionary_keys(
        engine_tree,
        "build_transient_website_unified_content_v1",
    )
    if engine_tree
    else set()
)

missing_package_fields = (
    REQUIRED_PACKAGE_FIELDS
    - engine_return_keys
)

if missing_package_fields:
    failures.append(
        "WUC engine return package is missing fields: "
        + ", ".join(
            sorted(
                missing_package_fields
            )
        )
    )


verification: dict[
    str,
    Any
] = {}

if not VERIFICATION_REPORT.is_file():
    failures.append(
        "WUC population verification report is missing."
    )

else:
    verification = load_json(
        VERIFICATION_REPORT
    )

    if (
        verification.get(
            "verification_status"
        )
        != "PASS"
    ):
        failures.append(
            "WUC population verification status is not PASS."
        )


result = verification.get(
    "result"
)

if not isinstance(
    result,
    dict,
):
    result = {}


if result.get(
    "input_count"
) != EXPECTED_COUNT:
    failures.append(
        "WUC input count is not 2,219."
    )

if result.get(
    "processed_count"
) != EXPECTED_COUNT:
    failures.append(
        "WUC processed count is not 2,219."
    )

if result.get(
    "pass_count"
) != EXPECTED_COUNT:
    failures.append(
        "WUC PASS count is not 2,219."
    )

if result.get(
    "fail_count"
) != 0:
    failures.append(
        "WUC contains failed records."
    )

if result.get(
    "full_body_handoff_ready_count"
) != EXPECTED_COUNT:
    failures.append(
        "Not all WUC records are full-body handoff ready."
    )

if result.get(
    "certificate_status"
) != "CERTIFIED":
    failures.append(
        "WUC certificate status is not CERTIFIED."
    )

if result.get(
    "article_bodies_persisted_by_wuc"
) is not False:
    failures.append(
        "WUC reports article-body persistence."
    )

if result.get(
    "intermediate_wuc_store_created"
) is not False:
    failures.append(
        "WUC reports an intermediate Store."
    )

if result.get(
    "uucd_documents_written"
) is not False:
    failures.append(
        "WUC reports UUCD writes."
    )


run_directories = (
    [
        path
        for path in EVIDENCE_ROOT.iterdir()
        if path.is_dir()
    ]
    if EVIDENCE_ROOT.is_dir()
    else []
)

if not run_directories:
    failures.append(
        "No WUC evidence run directory exists."
    )


latest_run = (
    max(
        run_directories,
        key=lambda path: (
            path.stat().st_mtime
        ),
    )
    if run_directories
    else None
)


pass_manifest_path = (
    latest_run
    / "wuc_pass_manifest.jsonl"
    if latest_run
    else None
)

fail_manifest_path = (
    latest_run
    / "wuc_fail_manifest.jsonl"
    if latest_run
    else None
)

certificate_path = (
    latest_run
    / "wuc_certificate.json"
    if latest_run
    else None
)

report_path = (
    latest_run
    / "wuc_report.json"
    if latest_run
    else None
)


pass_records: list[
    dict[str, Any]
] = []

fail_records: list[
    dict[str, Any]
] = []

certificate: dict[
    str,
    Any
] = {}

run_report: dict[
    str,
    Any
] = {}


for label, path in (
    (
        "PASS manifest",
        pass_manifest_path,
    ),
    (
        "FAIL manifest",
        fail_manifest_path,
    ),
    (
        "certificate",
        certificate_path,
    ),
    (
        "report",
        report_path,
    ),
):
    if (
        path is None
        or not path.is_file()
    ):
        failures.append(
            f"WUC {label} is missing."
        )


if (
    pass_manifest_path
    and pass_manifest_path.is_file()
):
    pass_records = load_jsonl(
        pass_manifest_path
    )

if (
    fail_manifest_path
    and fail_manifest_path.is_file()
):
    fail_records = load_jsonl(
        fail_manifest_path
    )

if (
    certificate_path
    and certificate_path.is_file()
):
    certificate = load_json(
        certificate_path
    )

if (
    report_path
    and report_path.is_file()
):
    run_report = load_json(
        report_path
    )


if len(
    pass_records
) != EXPECTED_COUNT:
    failures.append(
        "WUC PASS manifest does not contain 2,219 records."
    )

if fail_records:
    failures.append(
        "WUC FAIL manifest is not empty."
    )


source_ids = [
    str(
        record.get(
            "source_record_id"
        )
        or ""
    ).strip()
    for record in pass_records
]

if any(
    not source_id
    for source_id in source_ids
):
    failures.append(
        "One or more WUC PASS records lack source_record_id."
    )

if len(
    set(
        source_ids
    )
) != len(
    source_ids
):
    failures.append(
        "Duplicate source_record_id values exist in WUC evidence."
    )


required_pass_fields = {
    "source_record_id",
    "document_id",
    "content_id",
    "workspace_id",
    "content_hash",
    "body_length",
    "body_word_count",
    "block_count",
    "heading_count",
    "udare_article_path",
    "udare_article_sha256",
    "article_validation_run_id",
    "article_validation_certificate_id",
    "complete_content_preserved",
    "content_reduction_performed",
    "summarization_performed",
    "truncation_performed",
    "word_count_limit_applied",
    "full_body_handoff_ready",
    "status",
}


for index, record in enumerate(
    pass_records,
    start=1,
):
    missing = (
        required_pass_fields
        - set(
            record
        )
    )

    if missing:
        failures.append(
            f"PASS record {index} is missing fields: "
            + ", ".join(
                sorted(
                    missing
                )
            )
        )

        break

    if record.get(
        "status"
    ) != "PASS":
        failures.append(
            f"PASS record {index} status is invalid."
        )

        break

    if record.get(
        "complete_content_preserved"
    ) is not True:
        failures.append(
            f"PASS record {index} lacks complete-content certification."
        )

        break

    if record.get(
        "content_reduction_performed"
    ) is not False:
        failures.append(
            f"PASS record {index} reports content reduction."
        )

        break

    if record.get(
        "summarization_performed"
    ) is not False:
        failures.append(
            f"PASS record {index} reports summarization."
        )

        break

    if record.get(
        "truncation_performed"
    ) is not False:
        failures.append(
            f"PASS record {index} reports truncation."
        )

        break

    if record.get(
        "word_count_limit_applied"
    ) is not False:
        failures.append(
            f"PASS record {index} reports a word-count limit."
        )

        break

    if record.get(
        "full_body_handoff_ready"
    ) is not True:
        failures.append(
            f"PASS record {index} is not handoff ready."
        )

        break

    if int(
        record.get(
            "body_length"
        )
        or 0
    ) <= 0:
        failures.append(
            f"PASS record {index} has invalid body_length."
        )

        break

    if int(
        record.get(
            "body_word_count"
        )
        or 0
    ) <= 0:
        failures.append(
            f"PASS record {index} has invalid body_word_count."
        )

        break

    if int(
        record.get(
            "block_count"
        )
        or 0
    ) <= 0:
        failures.append(
            f"PASS record {index} has invalid block_count."
        )

        break


if certificate.get(
    "certificate_status"
) != "CERTIFIED":
    failures.append(
        "WUC evidence certificate is not CERTIFIED."
    )

if certificate.get(
    "input_count"
) != EXPECTED_COUNT:
    failures.append(
        "WUC certificate input count is incorrect."
    )

if certificate.get(
    "pass_count"
) != EXPECTED_COUNT:
    failures.append(
        "WUC certificate PASS count is incorrect."
    )

if certificate.get(
    "fail_count"
) != 0:
    failures.append(
        "WUC certificate FAIL count is not zero."
    )

if certificate.get(
    "complete_content_preserved"
) is not True:
    failures.append(
        "WUC certificate does not certify complete content."
    )

if certificate.get(
    "article_bodies_persisted_by_wuc"
) is not False:
    failures.append(
        "WUC certificate reports body persistence."
    )

if certificate.get(
    "intermediate_wuc_store_created"
) is not False:
    failures.append(
        "WUC certificate reports an intermediate Store."
    )

if certificate.get(
    "uucd_documents_written"
) is not False:
    failures.append(
        "WUC certificate reports UUCD writes."
    )


if run_report.get(
    "complete_content_preservation_rule"
) is not True:
    failures.append(
        "WUC run report lacks complete-content rule."
    )

if run_report.get(
    "content_reduction_allowed"
) is not False:
    failures.append(
        "WUC run report permits content reduction."
    )

if run_report.get(
    "summarization_allowed"
) is not False:
    failures.append(
        "WUC run report permits summarization."
    )

if run_report.get(
    "truncation_allowed"
) is not False:
    failures.append(
        "WUC run report permits truncation."
    )

if run_report.get(
    "word_count_limit"
) is not None:
    failures.append(
        "WUC run report contains a word-count limit."
    )


prohibited_paths_present = [
    str(
        path
    )
    for path in PROHIBITED_PATHS
    if path.exists()
]

if prohibited_paths_present:
    failures.append(
        "A prohibited WUC Store path exists."
    )


total_word_count = sum(
    int(
        record.get(
            "body_word_count"
        )
        or 0
    )
    for record in pass_records
)

total_body_length = sum(
    int(
        record.get(
            "body_length"
        )
        or 0
    )
    for record in pass_records
)

total_blocks = sum(
    int(
        record.get(
            "block_count"
        )
        or 0
    )
    for record in pass_records
)

total_headings = sum(
    int(
        record.get(
            "heading_count"
        )
        or 0
    )
    for record in pass_records
)


checks = {
    "required_files_exist":
        all(
            path.is_file()
            for path in required_files.values()
        ),

    "all_python_syntax_valid":
        len(
            trees
        )
        == len(
            required_files
        ),

    "required_input_functions_exist":
        not missing_input_functions,

    "required_engine_function_exists":
        not missing_engine_functions,

    "required_runner_function_exists":
        not missing_runner_functions,

    "engine_has_no_forbidden_calls":
        not forbidden_calls,

    "engine_has_no_forbidden_imports":
        not forbidden_imports,

    "engine_does_not_read_legacy_article_body":
        not article_body_reads,

    "engine_return_contract_contains_required_fields":
        not missing_package_fields,

    "verification_status_pass":
        verification.get(
            "verification_status"
        )
        == "PASS",

    "input_count_2219":
        result.get(
            "input_count"
        )
        == EXPECTED_COUNT,

    "processed_count_2219":
        result.get(
            "processed_count"
        )
        == EXPECTED_COUNT,

    "pass_count_2219":
        result.get(
            "pass_count"
        )
        == EXPECTED_COUNT,

    "fail_count_zero":
        result.get(
            "fail_count"
        )
        == 0,

    "full_body_handoff_ready_2219":
        result.get(
            "full_body_handoff_ready_count"
        )
        == EXPECTED_COUNT,

    "certificate_certified":
        result.get(
            "certificate_status"
        )
        == "CERTIFIED",

    "pass_manifest_count_2219":
        len(
            pass_records
        )
        == EXPECTED_COUNT,

    "fail_manifest_empty":
        len(
            fail_records
        )
        == 0,

    "all_source_ids_unique":
        (
            len(
                source_ids
            )
            == EXPECTED_COUNT
            and len(
                set(
                    source_ids
                )
            )
            == EXPECTED_COUNT
        ),

    "complete_content_preservation_certified":
        certificate.get(
            "complete_content_preserved"
        )
        is True,

    "no_wuc_body_persistence":
        certificate.get(
            "article_bodies_persisted_by_wuc"
        )
        is False,

    "no_intermediate_wuc_store":
        (
            certificate.get(
                "intermediate_wuc_store_created"
            )
            is False
            and not prohibited_paths_present
        ),

    "no_uucd_writes":
        certificate.get(
            "uucd_documents_written"
        )
        is False,

    "summarization_forbidden":
        run_report.get(
            "summarization_allowed"
        )
        is False,

    "truncation_forbidden":
        run_report.get(
            "truncation_allowed"
        )
        is False,

    "content_reduction_forbidden":
        run_report.get(
            "content_reduction_allowed"
        )
        is False,

    "word_count_limit_none":
        run_report.get(
            "word_count_limit"
        )
        is None,

    "total_words_positive":
        total_word_count
        > 0,

    "total_body_length_positive":
        total_body_length
        > 0,

    "total_blocks_positive":
        total_blocks
        > 0,
}


for name, passed in checks.items():
    if passed is not True:
        marker = (
            "Verification check failed: "
            + name
        )

        if marker not in failures:
            failures.append(
                marker
            )


report = {
    "schema_version":
        "final_wuc_canonical_compliance_v1",

    "workspace_id":
        WORKSPACE_ID,

    "scan_mode":
        "READ_ONLY",

    "scan_status":
        (
            "PASS"
            if not failures
            else "FAIL"
        ),

    "checks":
        checks,

    "required_package_fields":
        sorted(
            REQUIRED_PACKAGE_FIELDS
        ),

    "detected_engine_return_fields":
        sorted(
            engine_return_keys
        ),

    "missing_package_fields":
        sorted(
            missing_package_fields
        ),

    "forbidden_engine_calls":
        forbidden_calls,

    "forbidden_engine_imports":
        forbidden_imports,

    "article_body_reads":
        article_body_reads,

    "evidence_run":
        (
            str(
                latest_run
            )
            if latest_run
            else None
        ),

    "pass_manifest_count":
        len(
            pass_records
        ),

    "fail_manifest_count":
        len(
            fail_records
        ),

    "unique_source_id_count":
        len(
            set(
                source_ids
            )
        ),

    "total_word_count":
        total_word_count,

    "total_body_length":
        total_body_length,

    "total_block_count":
        total_blocks,

    "total_heading_count":
        total_headings,

    "certificate_id":
        certificate.get(
            "certificate_id"
        ),

    "certificate_status":
        certificate.get(
            "certificate_status"
        ),

    "prohibited_paths_present":
        prohibited_paths_present,

    "source_files_modified":
        False,

    "data_outputs_modified":
        False,

    "runtime_state_modified":
        False,

    "failures":
        failures,
}


FINAL_REPORT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

FINAL_REPORT.write_text(
    json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 112)
print(
    "WEBSITE UNIFIED CONTENT — FINAL CANONICAL COMPLIANCE"
)
print("=" * 112)
print()

for name, passed in checks.items():
    print(
        f"{name:<58}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "Certified WUC inputs:                  "
    + str(
        result.get(
            "input_count"
        )
    )
)

print(
    "WUC PASS records:                      "
    + str(
        len(
            pass_records
        )
    )
)

print(
    "WUC FAIL records:                      "
    + str(
        len(
            fail_records
        )
    )
)

print(
    "Unique source records:                 "
    + str(
        len(
            set(
                source_ids
            )
        )
    )
)

print(
    "Total words preserved:                 "
    + str(
        total_word_count
    )
)

print(
    "Total body characters preserved:       "
    + str(
        total_body_length
    )
)

print(
    "Total semantic blocks preserved:       "
    + str(
        total_blocks
    )
)

print(
    "Total headings preserved:              "
    + str(
        total_headings
    )
)

print(
    "Certificate status:                    "
    + str(
        certificate.get(
            "certificate_status"
        )
    )
)

print(
    "Certificate ID:                        "
    + str(
        certificate.get(
            "certificate_id"
        )
    )
)

print()
print(
    "WUC Store:                             NONE"
)

print(
    "Article-body persistence by WUC:        False"
)

print(
    "UUCD writes by WUC:                     False"
)

print(
    "Runtime execution by WUC engine:        False"
)

print()
print(
    "Final compliance report: "
    + str(
        FINAL_REPORT
    )
)

print()
print(
    "FAILURES"
)

if failures:
    for failure in failures:
        print(
            "  - "
            + failure
        )

else:
    print(
        "  None"
    )

print()

if failures:
    print(
        "FINAL WUC CANONICAL COMPLIANCE: FAIL"
    )

    print(
        "Do not proceed to UUCD until every failure is resolved."
    )

    print("=" * 112)

    raise SystemExit(1)

print(
    "FINAL WUC CANONICAL COMPLIANCE: PASS"
)

print(
    "WUC contains the complete certified website-content contract "
    "and all 2,219 validated articles are full-body handoff ready."
)

print(
    "WUC performs transient structural conversion only and creates "
    "no Store, UUCD output, Body Store output or runtime side effect."
)

print("=" * 112)
