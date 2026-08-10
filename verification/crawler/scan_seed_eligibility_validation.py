from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")

OUTPUT = (
    ROOT
    / "seed_eligibility_validation_scan.txt"
)

EXTENSIONS = {
    ".py",
    ".json",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".toml",
}

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
}

SEARCH_GROUPS = {
    "seed_eligibility": [
        r"seed[_\s-]*eligib",
        r"eligib.*seed",
        r"seed.*eligib",
        r"approve[_\s-]*seed",
        r"reject[_\s-]*seed",
    ],

    "crawl_frontier": [
        r"crawl[_\s-]*frontier",
        r"frontier[_\s-]*(?:entry|item|url|queue)",
        r"enqueue[_\s-]*(?:crawl|url)",
    ],

    "robots": [
        r"robots\.txt",
        r"robotparser",
        r"robots[_\s-]*(?:policy|rule|allow|deny)",
        r"can_fetch",
    ],

    "dns_network_safety": [
        r"dns[_\s-]*(?:resolve|resolution|resolver)",
        r"getaddrinfo",
        r"private[_\s-]*(?:ip|network)",
        r"loopback",
        r"link[_\s-]*local",
        r"localhost",
        r"ssrf",
    ],

    "url_domain_validation": [
        r"url[_\s-]*(?:valid|validation|validator)",
        r"domain[_\s-]*(?:valid|validation|validator)",
        r"validate[_\s-]*url",
        r"validate[_\s-]*domain",
        r"allowed[_\s-]*scheme",
        r"https?[_\s-]*scheme",
    ],

    "reachability_redirects": [
        r"reachab",
        r"redirect[_\s-]*(?:resolve|resolution|chain)",
        r"canonical[_\s-]*tag",
        r"http[_\s-]*status",
    ],

    "crawler_policy": [
        r"crawl[_\s-]*policy",
        r"crawler[_\s-]*policy",
        r"crawl[_\s-]*(?:allow|deny)",
        r"crawl[_\s-]*permission",
    ],

    "seed_registry_integration": [
        r"Universal Web Seed Registry",
        r"universal_web_seed",
        r"seed_protection",
        r"register_universal_web_seed",
    ],
}


def should_skip(path: Path) -> bool:
    return any(
        part in SKIP_DIRS
        for part in path.parts
    )


def safe_read(path: Path) -> str | None:
    try:
        return path.read_text(
            encoding="utf-8-sig"
        )
    except (
        UnicodeDecodeError,
        OSError,
    ):
        return None


files_scanned = 0

candidate_files: dict[
    str,
    list[tuple[str, int, str]],
] = {}

group_counts = {
    group: 0
    for group in SEARCH_GROUPS
}

compiled = {
    group: [
        re.compile(
            pattern,
            re.IGNORECASE,
        )
        for pattern in patterns
    ]
    for group, patterns
    in SEARCH_GROUPS.items()
}


for path in ROOT.rglob("*"):
    if not path.is_file():
        continue

    if should_skip(path):
        continue

    if path.suffix.lower() not in EXTENSIONS:
        continue

    if path.resolve() == OUTPUT.resolve():
        continue

    files_scanned += 1

    text = safe_read(path)

    if text is None:
        continue

    lines = text.splitlines()

    for line_number, line in enumerate(
        lines,
        start=1,
    ):
        matched_groups = []

        for group, patterns in compiled.items():
            if any(
                pattern.search(line)
                for pattern in patterns
            ):
                matched_groups.append(
                    group
                )

        if not matched_groups:
            continue

        relative = str(
            path.relative_to(ROOT)
        )

        entries = candidate_files.setdefault(
            relative,
            [],
        )

        group_label = ",".join(
            matched_groups
        )

        entries.append(
            (
                group_label,
                line_number,
                line.strip()[:300],
            )
        )

        for group in matched_groups:
            group_counts[group] += 1


report_lines = []

report_lines.append(
    "============================================================"
)
report_lines.append(
    "SEED ELIGIBILITY VALIDATION - READ-ONLY REPOSITORY SCAN"
)
report_lines.append(
    "============================================================"
)
report_lines.append("")
report_lines.append(
    f"Repository: {ROOT}"
)
report_lines.append(
    f"Files scanned: {files_scanned}"
)
report_lines.append(
    f"Candidate files: {len(candidate_files)}"
)
report_lines.append("")

report_lines.append(
    "============================================================"
)
report_lines.append(
    "MATCH COUNTS BY CATEGORY"
)
report_lines.append(
    "============================================================"
)

for group, count in group_counts.items():
    report_lines.append(
        f"{group}: {count}"
    )

report_lines.append("")

report_lines.append(
    "============================================================"
)
report_lines.append(
    "HIGH-VALUE CRAWLER FILE INVENTORY"
)
report_lines.append(
    "============================================================"
)

crawler_dir = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
)

if crawler_dir.exists():
    for path in sorted(
        crawler_dir.rglob("*.py")
    ):
        report_lines.append(
            str(
                path.relative_to(ROOT)
            )
        )
else:
    report_lines.append(
        "Crawler directory not found."
    )

report_lines.append("")

report_lines.append(
    "============================================================"
)
report_lines.append(
    "MATCHED FILES AND EVIDENCE"
)
report_lines.append(
    "============================================================"
)

for relative in sorted(
    candidate_files
):
    report_lines.append("")
    report_lines.append(
        f"FILE: {relative}"
    )
    report_lines.append(
        "-" * 72
    )

    matches = candidate_files[
        relative
    ]

    for (
        group_label,
        line_number,
        line,
    ) in matches[:80]:
        report_lines.append(
            f"[{group_label}] "
            f"L{line_number}: "
            f"{line}"
        )

    if len(matches) > 80:
        report_lines.append(
            f"... {len(matches) - 80} additional matches omitted"
        )


OUTPUT.write_text(
    "\n".join(report_lines),
    encoding="utf-8",
)

print("")
print("============================================================")
print(" SEED ELIGIBILITY VALIDATION SCAN COMPLETE")
print("============================================================")
print("")
print(f"Files scanned:   {files_scanned}")
print(
    f"Candidate files: {len(candidate_files)}"
)
print("")
print("Match counts:")

for group, count in group_counts.items():
    print(
        f"  {group}: {count}"
    )

print("")
print("Report:")
print(f"  {OUTPUT}")
print("")
print("READ-ONLY SCAN: COMPLETE")