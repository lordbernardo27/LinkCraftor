from __future__ import annotations

import ast
import codecs
import hashlib
import json
import py_compile
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


PATCH_VERSION = "uri_phase_1_precondition_site_reader_repair_v1"

PROJECT_ROOT = Path.cwd().resolve()
TARGET = PROJECT_ROOT / "backend" / "server" / "routes" / "site_reader.py"
MAIN_FILE = PROJECT_ROOT / "backend" / "server" / "main.py"

TIMESTAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

BACKUP_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"uri_phase1_site_reader_syntax_repair_{TIMESTAMP}"
)

BACKUP_FILE = (
    BACKUP_ROOT
    / "backend"
    / "server"
    / "routes"
    / "site_reader.py"
)

EVIDENCE_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "uri_phase_1"
    / "precondition_repairs"
)

EVIDENCE_JSON = (
    EVIDENCE_ROOT
    / f"site_reader_syntax_repair_{TIMESTAMP}.json"
)

EVIDENCE_TEXT = (
    EVIDENCE_ROOT
    / f"site_reader_syntax_repair_{TIMESTAMP}.txt"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_result(text: str, filename: str) -> dict:
    try:
        ast.parse(text, filename=filename)
    except SyntaxError as exc:
        return {
            "status": "FAIL",
            "line": exc.lineno,
            "offset": exc.offset,
            "message": exc.msg,
        }

    return {
        "status": "PASS",
        "line": None,
        "offset": None,
        "message": None,
    }


def decode_source(raw: bytes) -> tuple[str, str]:
    if raw.startswith(codecs.BOM_UTF8):
        return raw.decode("utf-8-sig"), "utf-8-sig"

    return raw.decode("utf-8"), "utf-8"


def encode_source(text: str, encoding: str) -> bytes:
    if encoding == "utf-8-sig":
        return text.encode("utf-8-sig")

    return text.encode("utf-8")


def fail(message: str) -> None:
    raise RuntimeError(message)


def main() -> int:
    print("=" * 78)
    print("UNIVERSAL RUNTIME INFRASTRUCTURE")
    print("PHASE 1 PRECONDITION — SITE_READER SYNTAX REPAIR")
    print("=" * 78)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Target:       {TARGET}")
    print()

    if not TARGET.exists():
        fail(f"Target file does not exist: {TARGET}")

    if not MAIN_FILE.exists():
        fail(f"Main application file does not exist: {MAIN_FILE}")

    original_raw = TARGET.read_bytes()
    original_text, original_encoding = decode_source(original_raw)
    original_hash = sha256_bytes(original_raw)
    original_parse = parse_result(original_text, str(TARGET))

    print("PRE-PATCH VALIDATION")
    print("-" * 78)
    print(f"Encoding:     {original_encoding}")
    print(f"SHA256:       {original_hash}")
    print(f"Parse status: {original_parse['status']}")

    if original_parse["status"] == "FAIL":
        print(
            f"Syntax error: line={original_parse['line']} "
            f"offset={original_parse['offset']} "
            f"message={original_parse['message']}"
        )

    expected_return_pattern = re.compile(
        r'(?m)^return \{"ok": False, "error": "invalid_domain"\}\s*$'
    )

    defective_matches = list(
        expected_return_pattern.finditer(original_text)
    )

    if len(defective_matches) == 0:
        # The repair may already have been applied.
        already_fixed_pattern = re.compile(
            r'(?m)^    return \{"ok": False, "error": "invalid_domain"\}\s*$'
        )

        fixed_matches = list(
            already_fixed_pattern.finditer(original_text)
        )

        if len(fixed_matches) == 1:
            current_parse = parse_result(
                original_text,
                str(TARGET),
            )

            if current_parse["status"] == "PASS":
                print()
                print("NO PATCH REQUIRED")
                print(
                    "The invalid_domain return is already indented "
                    "and site_reader.py parses successfully."
                )
                return 0

        fail(
            "The expected defective return line was not found. "
            "No file was modified."
        )

    if len(defective_matches) != 1:
        fail(
            "Expected exactly one defective invalid_domain return, "
            f"but found {len(defective_matches)}. No file was modified."
        )

    match = defective_matches[0]

    following_text = original_text[match.end():]
    following_lines = following_text.splitlines()

    next_nonblank = None

    for line in following_lines[:6]:
        if line.strip():
            next_nonblank = line
            break

    expected_marker = "    # LC_CONNECT_DOMAIN_EXISTING_WORKSPACE_6_3"

    if next_nonblank != expected_marker:
        fail(
            "Safety check failed. The defective return was not immediately "
            "followed by the expected existing-workspace marker. "
            "No file was modified."
        )

    BACKUP_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        TARGET,
        BACKUP_FILE,
    )

    repaired_text = expected_return_pattern.sub(
        '    return {"ok": False, "error": "invalid_domain"}',
        original_text,
        count=1,
    )

    if repaired_text == original_text:
        fail("Replacement produced no change.")

    repaired_raw = encode_source(
        repaired_text,
        original_encoding,
    )

    TARGET.write_bytes(repaired_raw)

    try:
        repaired_parse = parse_result(
            repaired_text,
            str(TARGET),
        )

        if repaired_parse["status"] != "PASS":
            fail(
                "site_reader.py still fails AST parsing after repair: "
                f"line={repaired_parse['line']} "
                f"message={repaired_parse['message']}"
            )

        py_compile.compile(
            str(TARGET),
            doraise=True,
        )

        py_compile.compile(
            str(MAIN_FILE),
            doraise=True,
        )

    except Exception:
        shutil.copy2(
            BACKUP_FILE,
            TARGET,
        )

        print()
        print("ROLLBACK COMPLETE")
        print(
            "Verification failed, so the original site_reader.py "
            "was restored automatically."
        )
        raise

    repaired_final_raw = TARGET.read_bytes()
    repaired_hash = sha256_bytes(repaired_final_raw)

    evidence = {
        "patch_version": PATCH_VERSION,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "target": str(TARGET),
        "backup": str(BACKUP_FILE),
        "original_encoding": original_encoding,
        "original_sha256": original_hash,
        "repaired_sha256": repaired_hash,
        "original_parse": original_parse,
        "repaired_parse": repaired_parse,
        "change": {
            "before": 'return {"ok": False, "error": "invalid_domain"}',
            "after": '    return {"ok": False, "error": "invalid_domain"}',
            "replacement_count": 1,
        },
        "verification": {
            "site_reader_ast_parse": "PASS",
            "site_reader_py_compile": "PASS",
            "main_py_compile": "PASS",
            "automatic_rollback_required": False,
        },
        "phase_1_effect": {
            "precondition_repair": "PASS",
            "phase_1_certification": "NOT_CERTIFIED",
            "phase_1_item_completed": None,
        },
    }

    EVIDENCE_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    EVIDENCE_JSON.write_text(
        json.dumps(
            evidence,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    evidence_lines = [
        "=" * 78,
        "URI PHASE 1 PRECONDITION REPAIR EVIDENCE",
        "=" * 78,
        "",
        f"Patch version: {PATCH_VERSION}",
        f"Timestamp UTC: {evidence['timestamp_utc']}",
        f"Target: {TARGET}",
        f"Backup: {BACKUP_FILE}",
        "",
        f"Original SHA256: {original_hash}",
        f"Repaired SHA256: {repaired_hash}",
        "",
        "CHANGE",
        "-" * 78,
        'Before: return {"ok": False, "error": "invalid_domain"}',
        'After:      return {"ok": False, "error": "invalid_domain"}',
        "",
        "VERIFICATION",
        "-" * 78,
        "site_reader.py AST parse: PASS",
        "site_reader.py compilation: PASS",
        "main.py compilation: PASS",
        "Automatic rollback required: NO",
        "",
        "PHASE 1 STATUS",
        "-" * 78,
        "Precondition repair: PASS",
        "Universal Runtime Foundation: NOT CERTIFIED",
        "No Phase 1 checklist item was marked complete.",
        "",
    ]

    EVIDENCE_TEXT.write_text(
        "\n".join(evidence_lines),
        encoding="utf-8",
    )

    print()
    print("POST-PATCH VERIFICATION")
    print("-" * 78)
    print("site_reader.py AST parse:   PASS")
    print("site_reader.py compilation: PASS")
    print("main.py compilation:        PASS")
    print()
    print(f"Original backup: {BACKUP_FILE}")
    print(f"Evidence JSON:   {EVIDENCE_JSON}")
    print(f"Evidence text:   {EVIDENCE_TEXT}")
    print()
    print("PHASE 1 PRECONDITION REPAIR: PASS")
    print("NO PRODUCTION DATA WAS MODIFIED")
    print("PHASE 1 REMAINS NOT CERTIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
