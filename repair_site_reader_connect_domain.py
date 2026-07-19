from pathlib import Path
import re


path = Path(
    "backend/server/routes/site_reader.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)


# Ensure HTTPException is available for proper FastAPI validation.
http_exception_imported = bool(
    re.search(
        r"(?m)^\s*from\s+fastapi(?:\.[A-Za-z0-9_.]+)?\s+import\s+"
        r"[^\n]*\bHTTPException\b",
        text,
    )
)


if not http_exception_imported:
    future_import = (
        "from __future__ import annotations\n"
    )

    if future_import in text:
        text = text.replace(
            future_import,
            (
                future_import
                + "\n"
                + "from fastapi import HTTPException\n"
            ),
            1,
        )
    else:
        text = (
            "from fastapi import HTTPException\n"
            + text
        )


pattern = re.compile(
    r"""
    (
        ^def[ \t]+connect_domain
        \(
            payload:[ \t]*ConnectDomainPayload
        \):
        \r?\n
        [ \t]+domain[ \t]*=
        [ \t]*_normalize_domain
        \(
            payload\.domain
        \)
        \r?\n
    )
    [ \t]*\r?\n
    [ \t]+if[ \t]+not[ \t]+domain:
    \r?\n
    [ \t]*\r?\n
    [ \t]+try:
    """,
    re.MULTILINE | re.VERBOSE,
)


replacement = r'''\1
    if not domain:
        raise HTTPException(
            status_code=400,
            detail="A valid domain is required.",
        )

    workspace_id = _workspace_id_from_domain(
        domain
    )

    try:
'''


updated, replacement_count = pattern.subn(
    replacement,
    text,
    count=1,
)


if replacement_count != 1:
    raise RuntimeError(
        "The expected broken connect_domain block "
        "was not found exactly once. No source file "
        "was changed."
    )


path.write_text(
    updated,
    encoding="utf-8",
)


print(
    "CONNECT_DOMAIN REPAIR: PASS"
)

print(
    "Added missing invalid-domain handling."
)

print(
    "Added workspace_id construction before orchestration."
)
