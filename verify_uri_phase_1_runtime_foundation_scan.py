from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


# ============================================================
# UNIVERSAL RUNTIME INFRASTRUCTURE
# PHASE 1 — RUNTIME FOUNDATION
# READ-ONLY INVENTORY SCAN
# ============================================================

SCAN_VERSION = "uri_phase_1_runtime_foundation_scan_v1"
MAX_FILE_BYTES = 2_000_000
MAX_EVIDENCE_PER_CHECK = 20

PROJECT_ROOT = Path.cwd().resolve()
BACKEND_ROOT = PROJECT_ROOT / "backend" / "server"

REPORT_ROOT = (
    BACKEND_ROOT
    / "data"
    / "runtime_scans"
    / "uri_phase_1_runtime_foundation"
)

TIMESTAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
TEXT_REPORT_PATH = REPORT_ROOT / f"phase_1_runtime_foundation_scan_{TIMESTAMP}.txt"
JSON_REPORT_PATH = REPORT_ROOT / f"phase_1_runtime_foundation_scan_{TIMESTAMP}.json"

ALLOWED_SUFFIXES = {
    ".py",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".env",
    ".md",
    ".txt",
}

ROOT_CONFIG_NAMES = {
    ".env",
    ".env.example",
    ".env.production",
    ".env.development",
    ".env.test",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "setup.py",
    "setup.cfg",
    "pytest.ini",
    "tox.ini",
    "docker-compose.yml",
    "docker-compose.yaml",
    "Dockerfile",
}

EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    ".idea",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "htmlcov",
    "backups",
    "backup",
}

# Large generated stores are not needed for a source-architecture scan.
EXCLUDED_RELATIVE_PREFIXES = {
    "backend/server/data/raw_website_html_store",
    "backend/server/data/udare_store",
    "backend/server/data/website_unified_content",
    "backend/server/data/uploaded_document_unified_content",
    "backend/server/data/universal_article_body_store",
    "backend/server/data/saved_sessions",
}


@dataclass(frozen=True)
class Evidence:
    path: str
    line: int
    excerpt: str
    rule: str
    strength: str


@dataclass
class CheckResult:
    check_id: str
    title: str
    status: str
    confidence: str
    dedicated_evidence_count: int
    supporting_evidence_count: int
    evidence: list[Evidence]
    interpretation: str
    required_next_action: str


CHECKS = [
    {
        "id": "1.1.1",
        "title": "Universal Runtime Kernel",
        "dedicated": [
            r"\bclass\s+(UniversalRuntimeKernel|RuntimeKernel)\b",
            r"\bdef\s+(run_universal_runtime|initialize_universal_runtime|create_runtime_kernel)\b",
            r"\buniversal_runtime_kernel\b",
            r"universal_runtime_infrastructure",
        ],
        "supporting": [
            r"\bruntime kernel\b",
            r"\bruntime core\b",
            r"\buniversal runtime\b",
            r"\bruntime_context\b",
        ],
        "interpretation": (
            "A genuine kernel must provide the central runtime entry point and "
            "common services without embedding individual pipeline business logic."
        ),
    },
    {
        "id": "1.1.2",
        "title": "Runtime Configuration",
        "dedicated": [
            r"\bclass\s+\w*Runtime\w*(Config|Settings)\b",
            r"\bclass\s+(RuntimeConfig|RuntimeSettings)\b",
            r"\bdef\s+(load_runtime_config|get_runtime_config|validate_runtime_config)\b",
            r"\bruntime_config(?:uration)?\b",
        ],
        "supporting": [
            r"\bBaseSettings\b",
            r"\bos\.getenv\b",
            r"\bos\.environ\b",
            r"\bload_dotenv\b",
            r"\bsettings\b",
            r"\bconfig\b",
        ],
        "interpretation": (
            "Runtime configuration should be centralized, validated, typed where "
            "possible, environment-aware, and independent of pipeline handlers."
        ),
    },
    {
        "id": "1.1.3",
        "title": "Runtime Environment Management",
        "dedicated": [
            r"\bclass\s+RuntimeEnvironment\b",
            r"\bdef\s+(detect_runtime_environment|load_runtime_environment|validate_runtime_environment)\b",
            r"\bruntime_environment\b",
            r"\bAPP_ENV\b",
            r"\bRUNTIME_ENV\b",
        ],
        "supporting": [
            r"\bdevelopment\b",
            r"\bproduction\b",
            r"\bstaging\b",
            r"\btesting\b",
            r"\benvironment\b",
            r"\.env",
        ],
        "interpretation": (
            "Environment management must explicitly distinguish development, "
            "testing, staging, and production behavior."
        ),
    },
    {
        "id": "1.1.4",
        "title": "Runtime Service Registry",
        "dedicated": [
            r"\bclass\s+(RuntimeServiceRegistry|UniversalRuntimeRegistry|ServiceRegistry)\b",
            r"\bdef\s+(register_runtime_service|get_runtime_service|resolve_runtime_service)\b",
            r"\bruntime_service_registry\b",
            r"\bservice_registry\b",
        ],
        "supporting": [
            r"\bregister_handler\b",
            r"\bregister_pipeline\b",
            r"\bregister_stage\b",
            r"\bhandler_registry\b",
            r"\bregistry\b",
            r"\bdispatch_table\b",
        ],
        "interpretation": (
            "The service registry should register runtime services separately from "
            "pipeline-stage handler registration."
        ),
    },
    {
        "id": "1.1.5",
        "title": "Runtime Lifecycle Manager",
        "dedicated": [
            r"\bclass\s+(RuntimeLifecycleManager|UniversalRuntimeLifecycle)\b",
            r"\bdef\s+(start_runtime|stop_runtime|restart_runtime|manage_runtime_lifecycle)\b",
            r"\bruntime_lifecycle\b",
            r"\blifecycle_manager\b",
        ],
        "supporting": [
            r"\blifespan\b",
            r"\bstartup\b",
            r"\bshutdown\b",
            r"\bstart\(",
            r"\bstop\(",
            r"\bclose\(",
        ],
        "interpretation": (
            "A lifecycle manager must coordinate ordered startup, readiness, drain, "
            "shutdown, cleanup, and failure handling."
        ),
    },
    {
        "id": "1.1.6",
        "title": "Runtime Boot Process",
        "dedicated": [
            r"\bdef\s+(boot_runtime|initialize_runtime|bootstrap_runtime|runtime_boot)\b",
            r"\bruntime_boot\b",
            r"\bbootstrap_universal_runtime\b",
            r"\binitialize_universal_runtime\b",
        ],
        "supporting": [
            r"@app\.on_event\([\"']startup[\"']\)",
            r"@.*\.on_event\([\"']startup[\"']\)",
            r"\basynccontextmanager\b",
            r"\blifespan\b",
            r"\bstartup_event\b",
            r"\bstartup_handler\b",
        ],
        "interpretation": (
            "The boot process must initialize configuration, state stores, "
            "registries, services, and readiness checks in a deterministic order."
        ),
    },
    {
        "id": "1.1.7",
        "title": "Runtime Shutdown Process",
        "dedicated": [
            r"\bdef\s+(shutdown_runtime|stop_runtime|runtime_shutdown|drain_runtime)\b",
            r"\bruntime_shutdown\b",
            r"\bshutdown_universal_runtime\b",
            r"\bgraceful_shutdown\b",
        ],
        "supporting": [
            r"@app\.on_event\([\"']shutdown[\"']\)",
            r"@.*\.on_event\([\"']shutdown[\"']\)",
            r"\bshutdown_event\b",
            r"\bsignal\.SIGTERM\b",
            r"\bsignal\.SIGINT\b",
            r"\batexit\.register\b",
            r"\bdrain\b",
            r"\bclose\(",
        ],
        "interpretation": (
            "Shutdown must stop new admissions, drain or safely release work, "
            "persist state, release leases, and close services."
        ),
    },
    {
        "id": "1.1.8",
        "title": "Runtime Versioning",
        "dedicated": [
            r"\bRUNTIME_VERSION\b",
            r"\bUNIVERSAL_RUNTIME_VERSION\b",
            r"\bruntime_version\b",
            r"\bclass\s+RuntimeVersion\b",
            r"\bdef\s+(get_runtime_version|validate_runtime_version)\b",
        ],
        "supporting": [
            r"\b__version__\b",
            r"\bversion\b",
            r"\bschema_version\b",
            r"\bpipeline_version\b",
        ],
        "interpretation": (
            "Runtime versioning must identify the runtime contract independently "
            "from individual pipeline or data-schema versions."
        ),
    },
    {
        "id": "1.1.9",
        "title": "Runtime Compatibility Layer",
        "dedicated": [
            r"\bclass\s+(RuntimeCompatibilityLayer|CompatibilityLayer)\b",
            r"\bdef\s+(check_runtime_compatibility|validate_runtime_compatibility|is_runtime_compatible)\b",
            r"\bruntime_compatibility\b",
            r"\bcompatibility_layer\b",
        ],
        "supporting": [
            r"\bminimum_runtime_version\b",
            r"\bsupported_runtime_version\b",
            r"\bbackward compatibility\b",
            r"\bcompatible\b",
            r"\bcompatibility\b",
            r"\bmigration\b",
        ],
        "interpretation": (
            "The compatibility layer must define whether jobs, workers, handlers, "
            "state schemas, and runtime versions can operate together safely."
        ),
    },
    {
        "id": "1.1.10",
        "title": "Runtime Persistence Interface",
        "dedicated": [
            r"\bclass\s+\w*Runtime\w*(Repository|Store|Persistence)\s*\(",
            r"\bclass\s+(RuntimePersistenceInterface|RuntimeRepository)\b",
            r"\bdef\s+(persist_runtime_state|load_runtime_state|save_runtime_state)\b",
            r"\bruntime_persistence_interface\b",
            r"\bruntime_repository\b",
        ],
        "supporting": [
            r"\bProtocol\b",
            r"\bABC\b",
            r"\babstractmethod\b",
            r"\brepository\b",
            r"\bpersistence\b",
            r"\bstore\b",
            r"\bread_\w+\b",
            r"\bwrite_\w+\b",
        ],
        "interpretation": (
            "The persistence interface must define storage contracts without "
            "binding the runtime kernel to one file, database, or queue backend."
        ),
    },
    {
        "id": "1.1.11",
        "title": "Runtime State Store Abstraction",
        "dedicated": [
            r"\bclass\s+(RuntimeStateStore|UniversalRuntimeStateStore)\b",
            r"\bdef\s+(get_runtime_state_store|create_runtime_state_store)\b",
            r"\bruntime_state_store\b",
            r"\bstate_store_abstraction\b",
        ],
        "supporting": [
            r"\bjob_store\b",
            r"\bqueue_store\b",
            r"\blease_store\b",
            r"\bcheckpoint_store\b",
            r"\bevent_store\b",
            r"\bstate_store\b",
        ],
        "interpretation": (
            "The state-store abstraction should provide replaceable durable stores "
            "for jobs, queues, leases, workers, checkpoints, and runtime events."
        ),
    },
    {
        "id": "1.1.12",
        "title": "Runtime Schema Management",
        "dedicated": [
            r"\bclass\s+(RuntimeSchemaManager|RuntimeSchemaRegistry)\b",
            r"\bdef\s+(migrate_runtime_schema|validate_runtime_schema|register_runtime_schema)\b",
            r"\bruntime_schema_version\b",
            r"\bruntime_schema_manager\b",
            r"\bruntime_schema_registry\b",
        ],
        "supporting": [
            r"\bschema_version\b",
            r"\bschema migration\b",
            r"\bmigrations?\b",
            r"\bmodel_validator\b",
            r"\bBaseModel\b",
            r"\bdataclass\b",
            r"\bTypedDict\b",
        ],
        "interpretation": (
            "Schema management must version and migrate runtime-owned records such "
            "as jobs, queues, leases, workers, checkpoints, and events."
        ),
    },
    {
        "id": "1.1.13",
        "title": "Runtime Foundation Certification",
        "dedicated": [
            r"\bcertif(?:y|ication).*runtime foundation\b",
            r"\bruntime foundation.*certif(?:y|ication)\b",
            r"\bverify_uri_phase_1\b",
            r"\bverify_runtime_foundation\b",
            r"\btest_runtime_foundation\b",
            r"\bruntime_foundation_certification\b",
        ],
        "supporting": [
            r"\bcertification\b",
            r"\bverification\b",
            r"\bacceptance criteria\b",
            r"\bPASS\b",
            r"\bFAIL\b",
            r"\bpytest\b",
            r"\bunittest\b",
        ],
        "interpretation": (
            "Certification requires dedicated acceptance tests and persistent "
            "evidence for the complete Phase 1 foundation, not merely unit tests "
            "for isolated runtime functions."
        ),
    },
]


RISK_RULES = [
    {
        "id": "RISK-01",
        "title": "Import-time runtime execution",
        "patterns": [
            r"^\s*(run_universal_knowledge_queue_v1|start_runtime|boot_runtime)\(",
            r"^\s*threading\.Thread\(.*start",
        ],
        "message": (
            "Runtime work may be starting during module import rather than through "
            "an explicit lifecycle or boot boundary."
        ),
    },
    {
        "id": "RISK-02",
        "title": "Hard-coded workspace or user identity",
        "patterns": [
            r"[\"']ws_[A-Za-z0-9_-]+[\"']",
            r"[\"']user_[A-Za-z0-9_-]+[\"']",
        ],
        "message": (
            "Hard-coded tenant identity in runtime code can violate universal "
            "runtime and workspace-isolation requirements."
        ),
    },
    {
        "id": "RISK-03",
        "title": "Hard-coded absolute filesystem path",
        "patterns": [
            r"[\"'][A-Za-z]:\\[^\"']+",
            r"[\"']/home/[^\"']+",
        ],
        "message": (
            "Absolute paths reduce runtime portability and may bypass centralized "
            "configuration."
        ),
    },
    {
        "id": "RISK-04",
        "title": "Mutable module-level runtime state",
        "patterns": [
            r"^\s*(RUNTIME|WORKERS|QUEUES|JOBS|REGISTRY|SERVICES)\s*=\s*(\{\}|\[\]|set\(\))",
        ],
        "message": (
            "Unprotected process-local mutable state may not survive restarts and "
            "may become unsafe under concurrency."
        ),
    },
    {
        "id": "RISK-05",
        "title": "Pipeline-specific logic inside universal runtime file",
        "patterns": [
            r"\b(udare|website_article_integrity|article_validation|semantic_intelligence)\b",
        ],
        "message": (
            "Universal runtime modules containing pipeline-specific business logic "
            "may violate the business-logic-agnostic kernel boundary."
        ),
    },
]


def normalize_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def is_excluded(path: Path) -> bool:
    relative = normalize_relative(path)

    if any(part in EXCLUDED_DIRECTORY_NAMES for part in path.parts):
        return True

    for prefix in EXCLUDED_RELATIVE_PREFIXES:
        if relative == prefix or relative.startswith(prefix + "/"):
            return True

    return False


def iter_candidate_files() -> Iterable[Path]:
    seen: set[Path] = set()

    if BACKEND_ROOT.exists():
        for path in BACKEND_ROOT.rglob("*"):
            if not path.is_file():
                continue
            if is_excluded(path):
                continue
            if path.suffix.lower() not in ALLOWED_SUFFIXES:
                continue
            if path.stat().st_size > MAX_FILE_BYTES:
                continue

            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield resolved

    for name in ROOT_CONFIG_NAMES:
        path = PROJECT_ROOT / name
        if path.exists() and path.is_file():
            resolved = path.resolve()
            if resolved not in seen and path.stat().st_size <= MAX_FILE_BYTES:
                seen.add(resolved)
                yield resolved


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def compact_excerpt(value: str, limit: int = 240) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


def find_pattern_evidence(
    files: list[Path],
    patterns: list[str],
    strength: str,
    rule_prefix: str,
) -> list[Evidence]:
    evidence: list[Evidence] = []
    compiled = [
        (pattern, re.compile(pattern, re.IGNORECASE))
        for pattern in patterns
    ]

    for path in files:
        text = read_text(path)
        if not text:
            continue

        lines = text.splitlines()

        for line_number, line in enumerate(lines, start=1):
            for pattern, regex in compiled:
                if regex.search(line):
                    evidence.append(
                        Evidence(
                            path=normalize_relative(path),
                            line=line_number,
                            excerpt=compact_excerpt(line),
                            rule=f"{rule_prefix}: {pattern}",
                            strength=strength,
                        )
                    )
                    break

            if len(evidence) >= MAX_EVIDENCE_PER_CHECK:
                return evidence

    return evidence


def inspect_python_structure(path: Path) -> dict:
    result = {
        "path": normalize_relative(path),
        "classes": [],
        "functions": [],
        "async_functions": [],
        "imports": [],
        "syntax_error": None,
    }

    text = read_text(path)
    if not text:
        return result

    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        result["syntax_error"] = {
            "line": exc.lineno,
            "message": exc.msg,
        }
        return result

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            result["classes"].append(
                {
                    "name": node.name,
                    "line": node.lineno,
                }
            )
        elif isinstance(node, ast.AsyncFunctionDef):
            result["async_functions"].append(
                {
                    "name": node.name,
                    "line": node.lineno,
                }
            )
        elif isinstance(node, ast.FunctionDef):
            result["functions"].append(
                {
                    "name": node.name,
                    "line": node.lineno,
                }
            )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                result["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            result["imports"].append(module)

    return result


def classify_check(check: dict, files: list[Path]) -> CheckResult:
    dedicated = find_pattern_evidence(
        files=files,
        patterns=check["dedicated"],
        strength="DEDICATED",
        rule_prefix="dedicated",
    )

    supporting = find_pattern_evidence(
        files=files,
        patterns=check["supporting"],
        strength="SUPPORTING",
        rule_prefix="supporting",
    )

    # Remove duplicate evidence locations where a dedicated rule already matched.
    dedicated_locations = {
        (item.path, item.line)
        for item in dedicated
    }
    supporting = [
        item
        for item in supporting
        if (item.path, item.line) not in dedicated_locations
    ]

    if dedicated:
        status = "FOUND"
        confidence = "MEDIUM"

        dedicated_paths = {item.path for item in dedicated}
        if len(dedicated_paths) >= 2 or len(dedicated) >= 3:
            confidence = "HIGH"

        required_next_action = (
            "Inspect the dedicated implementation and verify whether it satisfies "
            "the complete Phase 1 contract. FOUND does not mean certified."
        )
    elif supporting:
        status = "PARTIAL"
        confidence = "MEDIUM"
        required_next_action = (
            "Existing fragments or references were found, but no clearly dedicated "
            "implementation was identified. Architecture and implementation review "
            "are required."
        )
    else:
        status = "MISSING"
        confidence = "HIGH"
        required_next_action = (
            "No implementation evidence was found by the inventory scan. Confirm "
            "manually before designing the missing component."
        )

    evidence = (dedicated + supporting)[:MAX_EVIDENCE_PER_CHECK]

    return CheckResult(
        check_id=check["id"],
        title=check["title"],
        status=status,
        confidence=confidence,
        dedicated_evidence_count=len(dedicated),
        supporting_evidence_count=len(supporting),
        evidence=evidence,
        interpretation=check["interpretation"],
        required_next_action=required_next_action,
    )


def scan_risks(files: list[Path]) -> list[dict]:
    findings: list[dict] = []

    runtime_files = [
        path
        for path in files
        if "runtime" in path.name.lower()
        or "orchestrator" in path.name.lower()
        or "queue" in path.name.lower()
        or "worker" in path.name.lower()
    ]

    for risk in RISK_RULES:
        patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in risk["patterns"]
        ]

        risk_evidence: list[dict] = []

        for path in runtime_files:
            text = read_text(path)
            if not text:
                continue

            lines = text.splitlines()

            for line_number, line in enumerate(lines, start=1):
                if any(pattern.search(line) for pattern in patterns):
                    risk_evidence.append(
                        {
                            "path": normalize_relative(path),
                            "line": line_number,
                            "excerpt": compact_excerpt(line),
                        }
                    )

                if len(risk_evidence) >= 20:
                    break

            if len(risk_evidence) >= 20:
                break

        findings.append(
            {
                "risk_id": risk["id"],
                "title": risk["title"],
                "status": "REVIEW" if risk_evidence else "NO_MATCH",
                "message": risk["message"],
                "evidence": risk_evidence,
            }
        )

    return findings


def identify_runtime_candidate_files(files: list[Path]) -> list[dict]:
    candidates: list[dict] = []

    runtime_terms = {
        "runtime",
        "queue",
        "worker",
        "orchestrator",
        "job",
        "registry",
        "dispatcher",
        "execution",
        "lifecycle",
        "state_store",
        "repository",
    }

    for path in files:
        relative = normalize_relative(path).lower()
        name = path.name.lower()

        matched_terms = sorted(
            term
            for term in runtime_terms
            if term in relative or term in name
        )

        if not matched_terms:
            continue

        candidates.append(
            {
                "path": normalize_relative(path),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "matched_terms": matched_terms,
            }
        )

    candidates.sort(key=lambda item: item["path"])
    return candidates


def format_check(result: CheckResult) -> list[str]:
    lines = [
        f"{result.check_id} — {result.title}",
        f"STATUS: {result.status}",
        f"CONFIDENCE: {result.confidence}",
        f"DEDICATED EVIDENCE: {result.dedicated_evidence_count}",
        f"SUPPORTING EVIDENCE: {result.supporting_evidence_count}",
        f"INTERPRETATION: {result.interpretation}",
        f"NEXT ACTION: {result.required_next_action}",
        "EVIDENCE:",
    ]

    if not result.evidence:
        lines.append("  - None found.")
    else:
        for item in result.evidence:
            lines.append(
                f"  - [{item.strength}] "
                f"{item.path}:{item.line} | {item.excerpt}"
            )

    lines.append("")
    return lines


def main() -> int:
    print("=" * 78)
    print("UNIVERSAL RUNTIME INFRASTRUCTURE")
    print("PHASE 1 — RUNTIME FOUNDATION READ-ONLY SCAN")
    print("=" * 78)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Backend root: {BACKEND_ROOT}")
    print()

    if not BACKEND_ROOT.exists():
        print("FAIL: backend/server was not found.")
        print(
            "Run this scanner from the LinkCraftor project root:"
        )
        print(r"C:\Users\HP\Documents\LinkCraftor")
        return 1

    files = sorted(iter_candidate_files())

    python_files = [
        path
        for path in files
        if path.suffix.lower() == ".py"
    ]

    print(f"Candidate files scanned: {len(files)}")
    print(f"Python files parsed: {len(python_files)}")

    python_structure = [
        inspect_python_structure(path)
        for path in python_files
    ]

    syntax_errors = [
        item
        for item in python_structure
        if item["syntax_error"] is not None
    ]

    check_results = [
        classify_check(check, files)
        for check in CHECKS
    ]

    status_counts = Counter(
        result.status
        for result in check_results
    )

    risk_findings = scan_risks(files)
    runtime_candidate_files = identify_runtime_candidate_files(files)

    report = {
        "scan_version": SCAN_VERSION,
        "scan_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "READ_ONLY_SOURCE_INVENTORY",
        "project_root": str(PROJECT_ROOT),
        "backend_root": str(BACKEND_ROOT),
        "files_scanned": len(files),
        "python_files_parsed": len(python_files),
        "python_syntax_errors": syntax_errors,
        "phase": {
            "phase_id": "1",
            "phase_title": "Runtime Foundation",
            "certification_status": "NOT_CERTIFIED",
            "status_counts": dict(status_counts),
        },
        "checks": [
            {
                **asdict(result),
                "evidence": [
                    asdict(item)
                    for item in result.evidence
                ],
            }
            for result in check_results
        ],
        "risk_findings": risk_findings,
        "runtime_candidate_files": runtime_candidate_files,
    }

    REPORT_ROOT.mkdir(parents=True, exist_ok=True)

    JSON_REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    text_lines = [
        "=" * 78,
        "UNIVERSAL RUNTIME INFRASTRUCTURE",
        "PHASE 1 — RUNTIME FOUNDATION SCAN REPORT",
        "=" * 78,
        "",
        f"Scan version: {SCAN_VERSION}",
        f"Timestamp UTC: {report['scan_timestamp_utc']}",
        f"Project root: {PROJECT_ROOT}",
        f"Files scanned: {len(files)}",
        f"Python files parsed: {len(python_files)}",
        f"Python syntax errors: {len(syntax_errors)}",
        "",
        "IMPORTANT:",
        "FOUND means implementation evidence exists.",
        "PARTIAL means related fragments or references exist.",
        "MISSING means the scanner found no meaningful implementation evidence.",
        "No result from this inventory scan constitutes certification.",
        "",
        "PHASE 1 SUMMARY",
        "-" * 78,
        f"FOUND: {status_counts.get('FOUND', 0)}",
        f"PARTIAL: {status_counts.get('PARTIAL', 0)}",
        f"MISSING: {status_counts.get('MISSING', 0)}",
        "CERTIFICATION: NOT CERTIFIED",
        "",
    ]

    for result in check_results:
        text_lines.extend(format_check(result))

    text_lines.extend(
        [
            "RUNTIME FOUNDATION RISK REVIEW",
            "-" * 78,
        ]
    )

    for risk in risk_findings:
        text_lines.append(
            f"{risk['risk_id']} — {risk['title']}"
        )
        text_lines.append(f"STATUS: {risk['status']}")
        text_lines.append(f"MEANING: {risk['message']}")
        text_lines.append("EVIDENCE:")

        if not risk["evidence"]:
            text_lines.append("  - No automatic match.")
        else:
            for item in risk["evidence"]:
                text_lines.append(
                    f"  - {item['path']}:{item['line']} | "
                    f"{item['excerpt']}"
                )

        text_lines.append("")

    text_lines.extend(
        [
            "PYTHON SYNTAX REVIEW",
            "-" * 78,
        ]
    )

    if not syntax_errors:
        text_lines.append(
            "No Python syntax errors were detected in scanned source files."
        )
    else:
        for item in syntax_errors:
            text_lines.append(
                f"{item['path']}:{item['syntax_error']['line']} | "
                f"{item['syntax_error']['message']}"
            )

    text_lines.extend(
        [
            "",
            "RUNTIME CANDIDATE FILE INVENTORY",
            "-" * 78,
        ]
    )

    if not runtime_candidate_files:
        text_lines.append("No runtime candidate files were identified.")
    else:
        for item in runtime_candidate_files:
            text_lines.append(
                f"{item['path']} | "
                f"{item['size_bytes']} bytes | "
                f"sha256={item['sha256']} | "
                f"terms={','.join(item['matched_terms'])}"
            )

    text_lines.extend(
        [
            "",
            "=" * 78,
            "FINAL SCAN POSITION",
            "=" * 78,
            "",
            "This report is an inventory scan only.",
            "Phase 1 remains unchecked and NOT CERTIFIED.",
            "The next step is evidence review and manual architectural assessment.",
            "",
        ]
    )

    TEXT_REPORT_PATH.write_text(
        "\n".join(text_lines),
        encoding="utf-8",
    )

    print()
    print("PHASE 1 INVENTORY RESULTS")
    print("-" * 78)

    for result in check_results:
        print(
            f"{result.check_id:<7} "
            f"{result.status:<8} "
            f"{result.title}"
        )

    print("-" * 78)
    print(f"FOUND:   {status_counts.get('FOUND', 0)}")
    print(f"PARTIAL: {status_counts.get('PARTIAL', 0)}")
    print(f"MISSING: {status_counts.get('MISSING', 0)}")
    print("CERTIFICATION: NOT CERTIFIED")
    print()

    if syntax_errors:
        print(
            f"WARNING: {len(syntax_errors)} Python syntax "
            "error(s) were detected."
        )
    else:
        print("Python syntax scan: PASS")

    review_risks = [
        item
        for item in risk_findings
        if item["status"] == "REVIEW"
    ]
    print(
        f"Architecture risk categories requiring review: "
        f"{len(review_risks)}"
    )

    print()
    print(f"Text report: {TEXT_REPORT_PATH}")
    print(f"JSON report: {JSON_REPORT_PATH}")
    print()
    print("SCAN COMPLETE — NO PRODUCTION CODE WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
