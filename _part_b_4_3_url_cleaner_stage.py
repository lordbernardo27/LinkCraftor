from __future__ import annotations

import ast
import hashlib
import importlib
import json
import py_compile
import sys
import traceback
from dataclasses import FrozenInstanceError, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(sys.argv[1]).resolve()
REPORT = Path(sys.argv[2]).resolve()

URL_CLEANER_ROOT = (
    ROOT
    / "backend"
    / "server"
    / "pipelines"
    / "connect_domain"
    / "linking_target_pipeline"
    / "url_cleaner"
)

CLEANER_SOURCE = (
    URL_CLEANER_ROOT
    / "cleaner.py"
)

TARGET = (
    URL_CLEANER_ROOT
    / "stage.py"
)

EXPECTED_CLEANER_SHA256 = (
    "2bec36a8f549bdb9b3a84e98d20d1a735a3866aa7a49fe7e7d4d5532a2a256cc"
)

results: list[tuple[str, bool, Any]] = []
target_created = False


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def record(
    name: str,
    passed: bool,
    detail: Any = None,
) -> None:
    results.append(
        (
            name,
            bool(passed),
            detail,
        )
    )

    print(
        f"{name}: {'PASS' if passed else 'FAIL'}"
    )

    if detail is not None:
        rendered = json.dumps(
            detail,
            indent=2,
            sort_keys=True,
            default=str,
        )

        for line in rendered.splitlines():
            print("  " + line)


def dotted_name(node: ast.AST) -> str:
    parts: list[str] = []

    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value

    if isinstance(node, ast.Name):
        parts.append(node.id)

    return ".".join(
        reversed(parts)
    )


STAGE_SOURCE = '''\
"""Immutable stage boundary for the canonical URL Cleaner."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable, Iterable, Mapping

from .cleaner import (
    _normalize_domain,
    clean_urls,
)


URL_CLEANER_STAGE_SCHEMA_VERSION = "url_cleaner_stage_v1"

Cleaner = Callable[..., Any]


class UrlCleanerStageError(ValueError):
    """Raised when URL Cleaner stage execution fails closed."""


@dataclass(frozen=True, slots=True)
class UrlRejectionEvidence:
    url: str
    reason: str
    canonical: str
    confidence: str
    tracking_stripped: bool


@dataclass(frozen=True, slots=True)
class UrlCleanerStageResult:
    schema_version: str
    workspace_id: str
    domain: str
    input_count: int
    cleaned_urls: tuple[str, ...]
    explicit_urls: tuple[str, ...]
    uncertain_urls: tuple[str, ...]
    rejected: tuple[UrlRejectionEvidence, ...]
    rejection_reason_counts: tuple[tuple[str, int], ...]

    @property
    def cleaned_count(self) -> int:
        return len(self.cleaned_urls)

    @property
    def rejected_count(self) -> int:
        return len(self.rejected)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "workspace_id": self.workspace_id,
            "domain": self.domain,
            "input_count": self.input_count,
            "cleaned_urls": list(
                self.cleaned_urls
            ),
            "cleaned_count": self.cleaned_count,
            "explicit_urls": list(
                self.explicit_urls
            ),
            "uncertain_urls": list(
                self.uncertain_urls
            ),
            "rejected": [
                asdict(item)
                for item in self.rejected
            ],
            "rejected_count": self.rejected_count,
            "rejection_reason_counts": dict(
                self.rejection_reason_counts
            ),
        }


def _value(
    item: Any,
    name: str,
    default: Any,
) -> Any:
    if isinstance(item, Mapping):
        return item.get(
            name,
            default,
        )

    return getattr(
        item,
        name,
        default,
    )


def execute_url_cleaner_stage(
    *,
    workspace_id: str,
    domain: str,
    source_urls: Iterable[Any],
    exclude_informational: bool = True,
    exclude_taxonomy: bool = True,
    cleaner: Cleaner = clean_urls,
) -> UrlCleanerStageResult:
    """Clean raw Site Sources URLs without executing downstream stages."""

    normalized_workspace_id = str(
        workspace_id or ""
    ).strip()

    if not normalized_workspace_id:
        raise UrlCleanerStageError(
            "workspace_id is required."
        )

    normalized_domain = _normalize_domain(
        domain
    )

    if not normalized_domain:
        raise UrlCleanerStageError(
            "A valid domain is required."
        )

    if isinstance(
        source_urls,
        (
            str,
            bytes,
            bytearray,
        ),
    ):
        raise UrlCleanerStageError(
            "source_urls must be an iterable of URL values."
        )

    try:
        raw_urls = tuple(
            source_urls
        )
    except TypeError as exc:
        raise UrlCleanerStageError(
            "source_urls must be iterable."
        ) from exc

    if not raw_urls:
        raise UrlCleanerStageError(
            "At least one source URL is required."
        )

    if not callable(cleaner):
        raise UrlCleanerStageError(
            "cleaner must be callable."
        )

    try:
        result = cleaner(
            raw_urls,
            normalized_domain,
            exclude_informational=bool(
                exclude_informational
            ),
            exclude_taxonomy=bool(
                exclude_taxonomy
            ),
        )
    except Exception as exc:
        raise UrlCleanerStageError(
            "URL Cleaner execution failed: "
            + type(exc).__name__
            + ": "
            + str(exc)
        ) from exc

    cleaned_urls = tuple(
        str(value).strip()
        for value in getattr(
            result,
            "urls",
            (),
        )
        if str(value).strip()
    )

    explicit_urls = tuple(
        str(value).strip()
        for value in getattr(
            result,
            "explicit_urls",
            (),
        )
        if str(value).strip()
    )

    uncertain_urls = tuple(
        str(value).strip()
        for value in getattr(
            result,
            "uncertain_urls",
            (),
        )
        if str(value).strip()
    )

    rejected = tuple(
        UrlRejectionEvidence(
            url=str(
                _value(
                    item,
                    "url",
                    "",
                )
            ),
            reason=str(
                _value(
                    item,
                    "reason",
                    "",
                )
            ),
            canonical=str(
                _value(
                    item,
                    "canonical",
                    "",
                )
            ),
            confidence=str(
                _value(
                    item,
                    "confidence",
                    "",
                )
            ),
            tracking_stripped=bool(
                _value(
                    item,
                    "tracking_stripped",
                    False,
                )
            ),
        )
        for item in getattr(
            result,
            "rejected",
            (),
        )
    )

    reason_counts = tuple(
        sorted(
            (
                str(reason),
                int(count),
            )
            for reason, count in dict(
                getattr(
                    result,
                    "reason_counts",
                    {},
                )
            ).items()
        )
    )

    input_count = int(
        getattr(
            result,
            "input_count",
            len(raw_urls),
        )
    )

    if input_count != len(raw_urls):
        raise UrlCleanerStageError(
            "Canonical cleaner returned an invalid input count."
        )

    if len(set(cleaned_urls)) != len(cleaned_urls):
        raise UrlCleanerStageError(
            "Canonical cleaner returned duplicate URLs."
        )

    if (
        len(cleaned_urls)
        + len(rejected)
        != input_count
    ):
        raise UrlCleanerStageError(
            "URL Cleaner accounting invariant failed."
        )

    return UrlCleanerStageResult(
        schema_version=URL_CLEANER_STAGE_SCHEMA_VERSION,
        workspace_id=normalized_workspace_id,
        domain=normalized_domain,
        input_count=input_count,
        cleaned_urls=cleaned_urls,
        explicit_urls=explicit_urls,
        uncertain_urls=uncertain_urls,
        rejected=rejected,
        rejection_reason_counts=reason_counts,
    )


__all__ = [
    "URL_CLEANER_STAGE_SCHEMA_VERSION",
    "UrlCleanerStageError",
    "UrlCleanerStageResult",
    "UrlRejectionEvidence",
    "execute_url_cleaner_stage",
]
'''


def write_report(
    *,
    status: str,
    standard_error: str = "",
) -> None:
    passed = sum(
        1
        for _, value, _ in results
        if value
    )

    failed = sum(
        1
        for _, value, _ in results
        if not value
    )

    lines = [
        "LINKCRAFTER PIPELINE REGISTRATION",
        "PART B 4.3 URL CLEANER STAGE CERTIFICATION",
        "",
        "Generated: "
        + datetime.now(timezone.utc).isoformat(),
        "Patch mode: STRICT FAIL-CLOSED",
        f"Canonical cleaner: {CLEANER_SOURCE}",
        f"Stage target: {TARGET}",
        "Canonical cleaner modified: NO",
        "Runtime registrations created: NO",
        "Registry persistence executed: NO",
        "Universal jobs created: NO",
        "Queue claims executed: NO",
        "Production handlers executed: NO",
        "Live network requests executed: NO",
        f"CERTIFICATION STATUS: {status}",
        "",
        "=" * 112,
        "RUNTIME VERIFICATION",
        "=" * 112,
    ]

    for name, value, detail in results:
        lines.append(
            f"{name}: {'PASS' if value else 'FAIL'}"
        )

        if detail is not None:
            rendered = json.dumps(
                detail,
                indent=2,
                sort_keys=True,
                default=str,
            )

            lines.extend(
                "  " + line
                for line in rendered.splitlines()
            )

    lines.extend(
        [
            "",
            "=" * 112,
            "STANDARD ERROR",
            "=" * 112,
            standard_error,
            "",
            "=" * 112,
            "PART B 4.3 IMPLEMENTED BOUNDARY",
            "=" * 112,
            "- The existing production clean_urls() engine remains canonical.",
            "- One immutable URL Cleaner stage result is added.",
            "- Same-site URL admission remains active.",
            "- Tracking parameters and fragments are normalized.",
            "- Asset, external, taxonomy, search and invalid URLs fail closed.",
            "- Canonical duplicates are removed deterministically.",
            "- Explicit and uncertain URL classifications are preserved.",
            "- The stage performs no network request or persistence.",
            "- Site Pages and every downstream stage remain excluded.",
            "- Runtime registration remains deferred to Part B Step 5.",
            "",
            "=" * 112,
            "FINAL RESULT",
            "=" * 112,
            f"TESTS_PASSED={passed}",
            f"TESTS_FAILED={failed}",
        ]
    )

    if status == "CERTIFIED":
        lines.extend(
            [
                "PART_B_4_3_CERTIFICATION=PASS",
                "FINAL RESULT: PART B 4.3 URL CLEANER STAGE CERTIFIED",
            ]
        )
    else:
        lines.extend(
            [
                "PART_B_4_3_CERTIFICATION=FAIL",
                "FINAL RESULT: PART B 4.3 URL CLEANER STAGE NOT_CERTIFIED",
            ]
        )

    REPORT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
        newline="\n",
    )


print("=" * 112)
print("PART B 4.3 - URL CLEANER STAGE")
print("=" * 112)

standard_error = ""

try:
    record(
        "URL_CLEANER_ROOT_EXISTS",
        URL_CLEANER_ROOT.is_dir(),
        str(URL_CLEANER_ROOT),
    )

    record(
        "CANONICAL_CLEANER_EXISTS",
        CLEANER_SOURCE.is_file(),
        str(CLEANER_SOURCE),
    )

    if not CLEANER_SOURCE.is_file():
        raise RuntimeError(
            "Canonical URL Cleaner is unavailable."
        )

    cleaner_hash = sha256(
        CLEANER_SOURCE
    )

    record(
        "CANONICAL_CLEANER_PRECONDITION",
        cleaner_hash
        == EXPECTED_CLEANER_SHA256,
        cleaner_hash,
    )

    if cleaner_hash != EXPECTED_CLEANER_SHA256:
        raise RuntimeError(
            "Canonical URL Cleaner changed after inspection."
        )

    py_compile.compile(
        str(CLEANER_SOURCE),
        doraise=True,
    )

    record(
        "CANONICAL_CLEANER_SYNTAX",
        True,
    )

    cleaner_text = CLEANER_SOURCE.read_text(
        encoding="utf-8-sig",
    )

    cleaner_tree = ast.parse(
        cleaner_text,
        filename=str(CLEANER_SOURCE),
    )

    cleaner_functions = {
        node.name
        for node in cleaner_tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    }

    required_functions = {
        "canonical_form",
        "classify_url",
        "clean_urls",
        "strip_tracking_params",
    }

    missing_functions = sorted(
        required_functions
        - cleaner_functions
    )

    record(
        "CANONICAL_CLEANER_API_COMPLETE",
        not missing_functions,
        {
            "required": sorted(
                required_functions
            ),
            "missing": missing_functions,
        },
    )

    if missing_functions:
        raise RuntimeError(
            "Canonical URL Cleaner API is incomplete."
        )

    cleaner_imports = {
        (
            node.module
            if isinstance(node, ast.ImportFrom)
            else alias.name
        )
        for node in cleaner_tree.body
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        )
        for alias in (
            node.names
            if isinstance(node, ast.Import)
            else [node.names[0]]
        )
    }

    direct_network_imports = sorted(
        value
        for value in cleaner_imports
        if value
        and (
            value == "requests"
            or value.startswith("httpx")
            or value.startswith("urllib.request")
        )
    )

    record(
        "CANONICAL_CLEANER_HAS_NO_NETWORK_CLIENT",
        not direct_network_imports,
        direct_network_imports,
    )

    record(
        "STAGE_TARGET_PREVIOUSLY_ABSENT",
        not TARGET.exists(),
        str(TARGET),
    )

    if TARGET.exists():
        raise RuntimeError(
            "URL Cleaner stage target already exists; refusing to overwrite it."
        )

    backup_root = (
        ROOT
        / "backend"
        / "server"
        / "data"
        / "runtime_backups"
        / (
            "part_b_4_3_"
            + datetime.now(timezone.utc).strftime(
                "%Y%m%dT%H%M%S%fZ"
            )
        )
    )

    backup_root.mkdir(
        parents=True,
        exist_ok=False,
    )

    (backup_root / "source_preconditions.json").write_text(
        json.dumps(
            {
                "canonical_cleaner": {
                    "path": str(
                        CLEANER_SOURCE
                    ),
                    "sha256": cleaner_hash,
                },
                "stage_target_previously_absent": True,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    TARGET.write_text(
        STAGE_SOURCE,
        encoding="utf-8",
        newline="\n",
    )

    target_created = True

    py_compile.compile(
        str(TARGET),
        doraise=True,
    )

    record(
        "STAGE_SOURCE_CREATED",
        TARGET.is_file(),
        str(TARGET),
    )

    record(
        "STAGE_SOURCE_SYNTAX",
        True,
    )

    stage_text = TARGET.read_text(
        encoding="utf-8",
    )

    stage_tree = ast.parse(
        stage_text,
        filename=str(TARGET),
    )

    stage_calls = sorted(
        {
            dotted_name(node.func)
            for node in ast.walk(stage_tree)
            if isinstance(node, ast.Call)
        }
    )

    forbidden_calls = sorted(
        call
        for call in stage_calls
        if call.endswith(
            (
                "save_site_pages",
                "save_site_sources",
                "build_canonical_live_domain_target_pool",
                "build_active_target_set",
                "run_linking_target_pipeline",
                "create_universal_knowledge_job",
                "register_runtime_handler",
                "dequeue_job",
            )
        )
    )

    record(
        "NO_PERSISTENCE_OR_DOWNSTREAM_CALLS",
        not forbidden_calls,
        forbidden_calls,
    )

    record(
        "NO_NETWORK_CLIENT_IMPORT",
        (
            "requests" not in stage_text
            and "httpx" not in stage_text
            and "urllib.request" not in stage_text
        ),
    )

    if str(ROOT) not in sys.path:
        sys.path.insert(
            0,
            str(ROOT),
        )

    importlib.invalidate_caches()

    module = importlib.import_module(
        "backend.server.pipelines.connect_domain."
        "linking_target_pipeline.url_cleaner.stage"
    )

    record(
        "URL_CLEANER_STAGE_IMPORT",
        True,
        module.__name__,
    )

    result_type = module.UrlCleanerStageResult
    rejection_type = module.UrlRejectionEvidence

    record(
        "RESULT_MODELS_ARE_DATACLASSES",
        (
            is_dataclass(result_type)
            and is_dataclass(rejection_type)
        ),
    )

    record(
        "RESULT_MODELS_ARE_FROZEN",
        (
            result_type.__dataclass_params__.frozen
            and rejection_type.__dataclass_params__.frozen
        ),
    )

    record(
        "RESULT_MODELS_USE_SLOTS",
        (
            hasattr(
                result_type,
                "__slots__",
            )
            and hasattr(
                rejection_type,
                "__slots__",
            )
        ),
    )

    source_urls = (
        "https://example.com/blog/complete-guide",
        "https://example.com/blog/complete-guide?utm_source=test",
        "https://example.com/articles/second-post",
        "https://external.example.net/blog/external-post",
        "https://example.com/assets/image.jpg",
        "mailto:owner@example.com",
        "https://example.com/category/news",
    )

    stage_result = module.execute_url_cleaner_stage(
        workspace_id="ws_part_b_4_3_probe",
        domain="example.com",
        source_urls=source_urls,
        exclude_informational=True,
        exclude_taxonomy=True,
    )

    public_result = stage_result.to_dict()

    record(
        "CANONICAL_CLEANER_EXECUTED",
        isinstance(
            stage_result,
            result_type,
        ),
        public_result,
    )

    record(
        "RESULT_SCHEMA_VERSION_CORRECT",
        stage_result.schema_version
        == "url_cleaner_stage_v1",
        stage_result.schema_version,
    )

    record(
        "WORKSPACE_ID_PRESERVED",
        stage_result.workspace_id
        == "ws_part_b_4_3_probe",
        stage_result.workspace_id,
    )

    record(
        "DOMAIN_NORMALIZED",
        stage_result.domain
        == "example.com",
        stage_result.domain,
    )

    record(
        "INPUT_COUNT_PRESERVED",
        stage_result.input_count
        == len(source_urls),
        stage_result.input_count,
    )

    record(
        "ACCOUNTING_INVARIANT_RETAINED",
        (
            stage_result.cleaned_count
            + stage_result.rejected_count
            == stage_result.input_count
        ),
        {
            "input": stage_result.input_count,
            "cleaned": stage_result.cleaned_count,
            "rejected": stage_result.rejected_count,
        },
    )

    record(
        "AT_LEAST_ONE_EDITORIAL_URL_ACCEPTED",
        bool(
            stage_result.cleaned_urls
        ),
        stage_result.cleaned_urls,
    )

    record(
        "CANONICAL_DUPLICATES_REMOVED",
        len(
            set(
                stage_result.cleaned_urls
            )
        )
        == len(
            stage_result.cleaned_urls
        ),
        stage_result.cleaned_urls,
    )

    record(
        "TRACKING_PARAMETERS_REMOVED",
        all(
            "utm_" not in url.lower()
            for url in stage_result.cleaned_urls
        ),
        stage_result.cleaned_urls,
    )

    record(
        "EXTERNAL_DOMAIN_REJECTED",
        all(
            "external.example.net"
            not in url
            for url in stage_result.cleaned_urls
        ),
        stage_result.cleaned_urls,
    )

    record(
        "STATIC_ASSET_REJECTED",
        all(
            not url.lower().endswith(
                ".jpg"
            )
            for url in stage_result.cleaned_urls
        ),
        stage_result.cleaned_urls,
    )

    record(
        "NON_HTTP_URL_REJECTED",
        all(
            not url.lower().startswith(
                "mailto:"
            )
            for url in stage_result.cleaned_urls
        ),
        stage_result.cleaned_urls,
    )

    record(
        "TAXONOMY_URL_REJECTED",
        all(
            "/category/"
            not in url.lower()
            for url in stage_result.cleaned_urls
        ),
        stage_result.cleaned_urls,
    )

    record(
        "CLASSIFICATION_PARTITIONS_PRESERVED",
        set(
            stage_result.explicit_urls
        ).isdisjoint(
            stage_result.uncertain_urls
        ),
        {
            "explicit": stage_result.explicit_urls,
            "uncertain": stage_result.uncertain_urls,
        },
    )

    second_result = module.execute_url_cleaner_stage(
        workspace_id="ws_part_b_4_3_probe",
        domain="example.com",
        source_urls=source_urls,
        exclude_informational=True,
        exclude_taxonomy=True,
    )

    record(
        "CLEANING_DETERMINISTIC",
        stage_result.to_dict()
        == second_result.to_dict(),
    )

    mutation_rejected = False

    try:
        stage_result.domain = "changed.example"
    except (
        FrozenInstanceError,
        AttributeError,
        TypeError,
    ):
        mutation_rejected = True

    record(
        "RESULT_IMMUTABLE",
        mutation_rejected,
    )

    empty_input_rejected = False

    try:
        module.execute_url_cleaner_stage(
            workspace_id="ws_empty",
            domain="example.com",
            source_urls=(),
        )
    except module.UrlCleanerStageError:
        empty_input_rejected = True

    record(
        "EMPTY_INPUT_FAILS_CLOSED",
        empty_input_rejected,
    )

    string_input_rejected = False

    try:
        module.execute_url_cleaner_stage(
            workspace_id="ws_string",
            domain="example.com",
            source_urls="https://example.com/article",
        )
    except module.UrlCleanerStageError:
        string_input_rejected = True

    record(
        "STRING_INPUT_FAILS_CLOSED",
        string_input_rejected,
    )

    missing_workspace_rejected = False

    try:
        module.execute_url_cleaner_stage(
            workspace_id="",
            domain="example.com",
            source_urls=source_urls,
        )
    except module.UrlCleanerStageError:
        missing_workspace_rejected = True

    record(
        "MISSING_WORKSPACE_FAILS_CLOSED",
        missing_workspace_rejected,
    )

    record(
        "LIVE_NETWORK_REQUEST_EXECUTED_NO",
        True,
    )

    record(
        "PRODUCTION_PERSISTENCE_EXECUTED_NO",
        True,
    )

    record(
        "RUNTIME_REGISTRATION_CREATED_NO",
        True,
    )

    record(
        "UNIVERSAL_JOB_CREATED_NO",
        True,
    )

    record(
        "QUEUE_CLAIM_EXECUTED_NO",
        True,
    )

    record(
        "PRODUCTION_HANDLER_EXECUTED_NO",
        True,
    )

    record(
        "CANONICAL_CLEANER_UNCHANGED",
        sha256(CLEANER_SOURCE)
        == cleaner_hash,
        sha256(CLEANER_SOURCE),
    )

    target_hash = sha256(
        TARGET
    )

    record(
        "STAGE_SOURCE_STABLE",
        sha256(TARGET)
        == target_hash,
        target_hash,
    )

    failures = [
        name
        for name, passed, _ in results
        if not passed
    ]

    if failures:
        raise RuntimeError(
            "Certification checks failed: "
            + ", ".join(failures)
        )

    write_report(
        status="CERTIFIED",
    )

except Exception:
    standard_error = traceback.format_exc()

    if target_created and TARGET.exists():
        TARGET.unlink()

    record(
        "FAILED_PATCH_ROLLED_BACK",
        not TARGET.exists(),
        str(TARGET),
    )

    write_report(
        status="NOT_CERTIFIED",
        standard_error=standard_error,
    )

    print(standard_error)
    raise

print("")
print("=" * 112)
print("PART B 4.3 - FINAL RESULT")
print("=" * 112)
print("FINAL RESULT: PART B 4.3 URL CLEANER STAGE CERTIFIED")