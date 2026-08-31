from __future__ import annotations

from pathlib import Path
import re


ROOT = Path.cwd()

SCAN_ROOTS = [
    ROOT / "backend" / "server" / "routes",
    ROOT / "backend" / "server" / "stores",
    ROOT / "backend" / "server" / "pipelines" / "upload_document",
    ROOT / "frontend" / "public" / "assets" / "js",
]

EXCLUDED_PARTS = {
    "backups",
    "verification_scans",
    "__pycache__",
    "data",
    "saved_sessions",
}

TEXT_SUFFIXES = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".html",
}

PATTERNS = {
    "CANONICAL_ROUTER_SYMBOL": [
        r"\bdetect_upload_source_type\b",
    ],

    "CANONICAL_DISPATCHER_SYMBOL": [
        r"\bextract_upload_document_v1\b",
    ],

    "PHYSICAL_EXTENSION_MAP": [
        r'"\.txt"\s*:',
        r'"\.md"\s*:',
        r'"\.markdown"\s*:',
        r'"\.html"\s*:',
        r'"\.htm"\s*:',
        r'"\.docx"\s*:',
    ],

    "LOGICAL_FAMILY_DISPATCH": [
        r'source_type\s*==\s*["\']txt["\']',
        r'source_type\s*==\s*["\']markdown["\']',
        r'source_type\s*==\s*["\']html["\']',
        r'source_type\s*==\s*["\']docx["\']',
    ],

    "MIME_ROUTING_CANDIDATE": [
        r"\bcontent_type\b",
        r"\bmime\b",
        r"\bmimetypes\b",
    ],

    "MAGIC_SIGNATURE_ROUTING_CANDIDATE": [
        r"\bmagic\b",
        r"\bfile_signature\b",
        r"\bcontent_signature\b",
        r"\bsignature_bytes\b",
        r"\bdetect_signature\b",
    ],

    "UPLOAD_ROUTE_CANDIDATE": [
        r'@router\.(?:post|put)\(["\'][^"\']*upload',
        r'["\']/api/files/upload',
    ],

    "LEGACY_JOB_WORKER_CANDIDATE": [
        r"\bupload_job\b",
        r"\bdocument_upload_job\b",
        r"\bupload_worker\b",
        r"\bbackgroundtasks?\b",
    ],

    "WEBSITE_CONTAMINATION_CANDIDATE": [
        r"\barticle_body_cleaning_engine\b",
        r"\barticle_cleaning_pipeline\b",
        r"\braw_website_html\b",
    ],

    "URL_DRAFT_CONTAMINATION_CANDIDATE": [
        r"/api/urls/import",
        r"/api/draft/import",
    ],

    "FRONTEND_ALIAS_CANDIDATE": [
        r'["\']\.markdown["\']',
        r'["\']\.htm["\']',
    ],
}


def excluded(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    return any(item.lower() in parts for item in EXCLUDED_PARTS)


def iter_files():
    seen = set()

    for scan_root in SCAN_ROOTS:
        if not scan_root.exists():
            continue

        for path in scan_root.rglob("*"):
            if not path.is_file():
                continue

            if excluded(path):
                continue

            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue

            resolved = path.resolve()

            if resolved in seen:
                continue

            seen.add(resolved)
            yield path


print("=== U5.15 - LEGACY ROUTING DISCOVERY ===")
print()

matches = []

for path in iter_files():
    try:
        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except Exception:
        continue

    lines = text.splitlines()

    for category, expressions in PATTERNS.items():
        for line_no, line in enumerate(lines, start=1):
            for expression in expressions:
                if re.search(
                    expression,
                    line,
                    flags=re.IGNORECASE,
                ):
                    relative = path.relative_to(ROOT).as_posix()

                    item = (
                        category,
                        relative,
                        line_no,
                        line.strip(),
                    )

                    matches.append(item)
                    break


if not matches:
    print("NO_MATCHES_FOUND")
else:
    current_category = None

    for category, path, line_no, line in sorted(matches):
        if category != current_category:
            print()
            print(f"=== {category} ===")
            current_category = category

        print(f"{path}:{line_no}")
        print(f"  {line}")


print()
print("========================================")
print(f"TOTAL_MATCHES: {len(matches)}")
print("U5.15_DISCOVERY_SCAN_COMPLETE")
print("NO_FILES_MODIFIED")