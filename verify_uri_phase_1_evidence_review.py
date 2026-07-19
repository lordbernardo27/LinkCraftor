from __future__ import annotations

import ast
import codecs
import json
import re
import tokenize
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCAN_VERSION = "uri_phase_1_evidence_review_v1"

PROJECT_ROOT = Path.cwd().resolve()
REPORT_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_scans"
    / "uri_phase_1_runtime_foundation"
)

TIMESTAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
OUTPUT_PATH = REPORT_ROOT / f"phase_1_evidence_review_{TIMESTAMP}.txt"

RELEVANT_SYMBOL_PATTERN = re.compile(
    r"runtime|kernel|config|setting|environment|service|registry|"
    r"lifecycle|boot|startup|shutdown|version|compatib|persist|"
    r"repository|state|store|schema|migration|certif|verify|"
    r"queue|worker|job|lease|checkpoint|event",
    re.IGNORECASE,
)

MAX_CONTEXT_LOCATIONS_PER_FILE = 30
MAX_SYMBOLS_PER_FILE = 80


def relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def resolve_report_path(value: str) -> Path:
    candidate = Path(value)

    if candidate.is_absolute():
        return candidate

    return PROJECT_ROOT / candidate


def newest_inventory_report() -> Path:
    reports = sorted(
        REPORT_ROOT.glob("phase_1_runtime_foundation_scan_*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not reports:
        raise FileNotFoundError(
            f"No Phase 1 JSON inventory report found under: {REPORT_ROOT}"
        )

    return reports[0]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def python_aware_parse(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": relative_path(path),
        "exists": path.exists(),
        "has_utf8_bom": False,
        "parse_status": "NOT_CHECKED",
        "syntax_error_line": None,
        "syntax_error_offset": None,
        "syntax_error_message": None,
        "encoding": None,
        "tree": None,
        "text": None,
    }

    if not path.exists():
        result["parse_status"] = "FILE_MISSING"
        return result

    try:
        raw = path.read_bytes()
    except OSError as exc:
        result["parse_status"] = "READ_ERROR"
        result["syntax_error_message"] = str(exc)
        return result

    result["has_utf8_bom"] = raw.startswith(codecs.BOM_UTF8)

    try:
        with tokenize.open(path) as handle:
            result["encoding"] = handle.encoding
            text = handle.read()
    except (OSError, SyntaxError, UnicodeError) as exc:
        result["parse_status"] = "DECODE_ERROR"
        result["syntax_error_message"] = str(exc)
        return result

    result["text"] = text

    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        result["parse_status"] = "CONFIRMED_SYNTAX_ERROR"
        result["syntax_error_line"] = exc.lineno
        result["syntax_error_offset"] = exc.offset
        result["syntax_error_message"] = exc.msg
        return result

    result["parse_status"] = "PARSE_PASS"
    result["tree"] = tree
    return result


def compact(value: str, limit: int = 260) -> str:
    value = re.sub(r"\s+", " ", value).strip()

    if len(value) <= limit:
        return value

    return value[: limit - 3] + "..."


def extract_symbols(tree: ast.AST) -> list[dict[str, Any]]:
    symbols: list[dict[str, Any]] = []

    if not isinstance(tree, ast.Module):
        return symbols

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            symbols.append(
                {
                    "kind": "CLASS",
                    "name": node.name,
                    "line": node.lineno,
                    "relevant": bool(RELEVANT_SYMBOL_PATTERN.search(node.name)),
                }
            )

        elif isinstance(node, ast.AsyncFunctionDef):
            symbols.append(
                {
                    "kind": "ASYNC FUNCTION",
                    "name": node.name,
                    "line": node.lineno,
                    "relevant": bool(RELEVANT_SYMBOL_PATTERN.search(node.name)),
                }
            )

        elif isinstance(node, ast.FunctionDef):
            symbols.append(
                {
                    "kind": "FUNCTION",
                    "name": node.name,
                    "line": node.lineno,
                    "relevant": bool(RELEVANT_SYMBOL_PATTERN.search(node.name)),
                }
            )

        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            names: list[str] = []

            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        names.append(target.id)
            elif isinstance(node.target, ast.Name):
                names.append(node.target.id)

            for name in names:
                if RELEVANT_SYMBOL_PATTERN.search(name):
                    symbols.append(
                        {
                            "kind": "CONSTANT/STATE",
                            "name": name,
                            "line": node.lineno,
                            "relevant": True,
                        }
                    )

    relevant = [symbol for symbol in symbols if symbol["relevant"]]

    if relevant:
        return relevant[:MAX_SYMBOLS_PER_FILE]

    return symbols[:20]


def context_for_lines(
    text: str,
    line_numbers: list[int],
    radius: int = 2,
) -> list[str]:
    source_lines = text.splitlines()
    rendered: list[str] = []
    emitted: set[int] = set()

    for requested_line in sorted(set(line_numbers))[
        :MAX_CONTEXT_LOCATIONS_PER_FILE
    ]:
        start = max(1, requested_line - radius)
        end = min(len(source_lines), requested_line + radius)

        rendered.append(
            f"  CONTEXT AROUND LINE {requested_line}"
        )

        for line_number in range(start, end + 1):
            if line_number in emitted:
                continue

            emitted.add(line_number)
            marker = ">>" if line_number == requested_line else "  "
            rendered.append(
                f"  {marker} {line_number:>6}: "
                f"{source_lines[line_number - 1]}"
            )

        rendered.append("")

    return rendered


def main() -> int:
    print("=" * 78)
    print("UNIVERSAL RUNTIME INFRASTRUCTURE")
    print("PHASE 1 — EVIDENCE REVIEW AND SYNTAX VALIDATION")
    print("=" * 78)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    if not REPORT_ROOT.exists():
        print(f"FAIL: Report directory was not found: {REPORT_ROOT}")
        return 1

    try:
        inventory_path = newest_inventory_report()
    except FileNotFoundError as exc:
        print(f"FAIL: {exc}")
        return 1

    inventory = load_json(inventory_path)

    checks = inventory.get("checks", [])
    risks = inventory.get("risk_findings", [])
    original_syntax_errors = inventory.get("python_syntax_errors", [])

    print(f"Inventory report: {inventory_path}")
    print(f"Original apparent syntax errors: {len(original_syntax_errors)}")
    print()

    # --------------------------------------------------------
    # Revalidate apparent syntax errors using tokenize.open().
    # --------------------------------------------------------

    validation_results: list[dict[str, Any]] = []

    for original in original_syntax_errors:
        source_path = resolve_report_path(str(original.get("path", "")))
        validated = python_aware_parse(source_path)
        validated["original_scanner_error"] = original.get("syntax_error")
        validation_results.append(validated)

    parse_counts = Counter(
        item["parse_status"]
        for item in validation_results
    )

    false_positive_results = [
        item
        for item in validation_results
        if item["parse_status"] == "PARSE_PASS"
    ]

    confirmed_error_results = [
        item
        for item in validation_results
        if item["parse_status"] == "CONFIRMED_SYNTAX_ERROR"
    ]

    bom_false_positives = [
        item
        for item in false_positive_results
        if item["has_utf8_bom"]
    ]

    # --------------------------------------------------------
    # Collect exact evidence locations by source file.
    # --------------------------------------------------------

    evidence_by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for check in checks:
        for evidence in check.get("evidence", []):
            evidence_by_path[str(evidence.get("path", ""))].append(
                {
                    "source_type": "CHECK",
                    "source_id": check.get("check_id"),
                    "source_title": check.get("title"),
                    "strength": evidence.get("strength"),
                    "line": evidence.get("line"),
                    "rule": evidence.get("rule"),
                    "excerpt": evidence.get("excerpt"),
                }
            )

    for risk in risks:
        for evidence in risk.get("evidence", []):
            evidence_by_path[str(evidence.get("path", ""))].append(
                {
                    "source_type": "RISK",
                    "source_id": risk.get("risk_id"),
                    "source_title": risk.get("title"),
                    "strength": "RISK",
                    "line": evidence.get("line"),
                    "rule": risk.get("message"),
                    "excerpt": evidence.get("excerpt"),
                }
            )

    output: list[str] = [
        "=" * 78,
        "UNIVERSAL RUNTIME INFRASTRUCTURE",
        "PHASE 1 — EVIDENCE REVIEW REPORT",
        "=" * 78,
        "",
        f"Review version: {SCAN_VERSION}",
        f"Timestamp UTC: {datetime.now(timezone.utc).isoformat()}",
        f"Project root: {PROJECT_ROOT}",
        f"Source inventory report: {inventory_path}",
        "",
        "IMPORTANT",
        "-" * 78,
        "This is still a read-only architecture review.",
        "No Phase 1 component is certified by this report.",
        "",
        "ORIGINAL INVENTORY POSITION",
        "-" * 78,
    ]

    for check in checks:
        output.append(
            f"{check.get('check_id'):<7} "
            f"{check.get('status', 'UNKNOWN'):<8} "
            f"{check.get('title', '')}"
        )

    output.extend(
        [
            "",
            "SYNTAX ERROR REVALIDATION",
            "-" * 78,
            f"Originally reported: {len(original_syntax_errors)}",
            f"Python-aware parse passed: "
            f"{parse_counts.get('PARSE_PASS', 0)}",
            f"Confirmed syntax errors: "
            f"{parse_counts.get('CONFIRMED_SYNTAX_ERROR', 0)}",
            f"Missing files: "
            f"{parse_counts.get('FILE_MISSING', 0)}",
            f"Decode/read failures: "
            f"{parse_counts.get('DECODE_ERROR', 0) + parse_counts.get('READ_ERROR', 0)}",
            f"BOM-related parse-pass candidates: {len(bom_false_positives)}",
            "",
        ]
    )

    if false_positive_results:
        output.append("APPARENT FALSE POSITIVES")
        output.append("-" * 78)

        for item in false_positive_results:
            original_error = item.get("original_scanner_error") or {}
            output.append(
                f"{item['path']} | "
                f"robust_parse=PASS | "
                f"utf8_bom={item['has_utf8_bom']} | "
                f"original_line={original_error.get('line')} | "
                f"original_message={original_error.get('message')}"
            )

        output.append("")

    if confirmed_error_results:
        output.append("CONFIRMED PYTHON SYNTAX ERRORS")
        output.append("-" * 78)

        for item in confirmed_error_results:
            output.append(
                f"{item['path']}:{item['syntax_error_line']} | "
                f"{item['syntax_error_message']}"
            )

        output.append("")
    else:
        output.extend(
            [
                "CONFIRMED PYTHON SYNTAX ERRORS",
                "-" * 78,
                "None confirmed by Python-aware parsing.",
                "",
            ]
        )

    output.extend(
        [
            "PHASE 1 CHECK EVIDENCE",
            "=" * 78,
            "",
        ]
    )

    for check in checks:
        output.extend(
            [
                f"{check.get('check_id')} — {check.get('title')}",
                f"INVENTORY STATUS: {check.get('status')}",
                f"CONFIDENCE: {check.get('confidence')}",
                f"DEDICATED EVIDENCE COUNT: "
                f"{check.get('dedicated_evidence_count', 0)}",
                f"SUPPORTING EVIDENCE COUNT: "
                f"{check.get('supporting_evidence_count', 0)}",
                f"INTERPRETATION: {check.get('interpretation')}",
                "EVIDENCE:",
            ]
        )

        evidence_items = check.get("evidence", [])

        if not evidence_items:
            output.append("  - None.")
        else:
            for evidence in evidence_items:
                output.append(
                    f"  - [{evidence.get('strength')}] "
                    f"{evidence.get('path')}:{evidence.get('line')} | "
                    f"rule={evidence.get('rule')} | "
                    f"{evidence.get('excerpt')}"
                )

        output.append("")

    output.extend(
        [
            "ARCHITECTURE RISK EVIDENCE",
            "=" * 78,
            "",
        ]
    )

    for risk in risks:
        output.extend(
            [
                f"{risk.get('risk_id')} — {risk.get('title')}",
                f"STATUS: {risk.get('status')}",
                f"MEANING: {risk.get('message')}",
                "EVIDENCE:",
            ]
        )

        evidence_items = risk.get("evidence", [])

        if not evidence_items:
            output.append("  - No automatic match.")
        else:
            for evidence in evidence_items:
                output.append(
                    f"  - {evidence.get('path')}:{evidence.get('line')} | "
                    f"{evidence.get('excerpt')}"
                )

        output.append("")

    output.extend(
        [
            "SOURCE FILE STRUCTURAL REVIEW",
            "=" * 78,
            "",
        ]
    )

    for path_value in sorted(evidence_by_path):
        if not path_value:
            continue

        source_path = resolve_report_path(path_value)
        output.append(f"FILE: {relative_path(source_path)}")

        references = evidence_by_path[path_value]
        reference_labels = sorted(
            {
                f"{item['source_type']}:{item['source_id']}"
                for item in references
            }
        )
        output.append(
            f"REFERENCED BY: {', '.join(reference_labels)}"
        )

        if not source_path.exists():
            output.extend(
                [
                    "STATUS: FILE MISSING",
                    "",
                ]
            )
            continue

        if source_path.suffix.lower() != ".py":
            try:
                text = source_path.read_text(
                    encoding="utf-8-sig",
                    errors="replace",
                )
            except OSError as exc:
                output.extend(
                    [
                        f"STATUS: READ ERROR — {exc}",
                        "",
                    ]
                )
                continue

            evidence_lines = [
                int(item["line"])
                for item in references
                if isinstance(item.get("line"), int)
            ]

            output.extend(context_for_lines(text, evidence_lines))
            output.append("")
            continue

        parsed = python_aware_parse(source_path)
        output.append(
            f"PYTHON PARSE STATUS: {parsed['parse_status']}"
        )
        output.append(
            f"UTF-8 BOM: {parsed['has_utf8_bom']}"
        )
        output.append(
            f"DETECTED ENCODING: {parsed['encoding']}"
        )

        if parsed["parse_status"] != "PARSE_PASS":
            output.append(
                f"ERROR: line={parsed['syntax_error_line']} | "
                f"{parsed['syntax_error_message']}"
            )
            output.append("")
            continue

        symbols = extract_symbols(parsed["tree"])
        output.append("RELEVANT TOP-LEVEL SYMBOLS:")

        if not symbols:
            output.append("  - No top-level symbols identified.")
        else:
            for symbol in symbols:
                output.append(
                    f"  - {symbol['kind']:<15} "
                    f"{symbol['name']} "
                    f"(line {symbol['line']})"
                )

        output.append("EVIDENCE CONTEXT:")

        evidence_lines = [
            int(item["line"])
            for item in references
            if isinstance(item.get("line"), int)
        ]

        output.extend(
            context_for_lines(
                parsed["text"],
                evidence_lines,
            )
        )
        output.append("")

    output.extend(
        [
            "=" * 78,
            "FINAL REVIEW POSITION",
            "=" * 78,
            "",
            "This evidence review does not mark any checklist item complete.",
            "Its purpose is to establish the exact source files requiring manual",
            "architectural assessment before Phase 1 implementation begins.",
            "",
            "PHASE 1 CERTIFICATION: NOT CERTIFIED",
            "",
        ]
    )

    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        "\n".join(output),
        encoding="utf-8",
    )

    print("SYNTAX REVALIDATION")
    print("-" * 78)
    print(f"Originally reported:       {len(original_syntax_errors)}")
    print(
        f"Python-aware parse passed: "
        f"{parse_counts.get('PARSE_PASS', 0)}"
    )
    print(
        f"Confirmed syntax errors:   "
        f"{parse_counts.get('CONFIRMED_SYNTAX_ERROR', 0)}"
    )
    print(
        f"BOM parse-pass candidates: {len(bom_false_positives)}"
    )
    print()

    print("PHASE 1 EVIDENCE FILES")
    print("-" * 78)
    print(f"Unique evidence files: {len(evidence_by_path)}")
    print(f"Risk categories: {len(risks)}")
    print()

    print(f"Evidence review report: {OUTPUT_PATH}")
    print()
    print("PHASE 1 EVIDENCE REVIEW COMPLETE")
    print("NO PRODUCTION CODE WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
