from __future__ import annotations

import ast
import re
from pathlib import Path


path = Path(
    "backend/server/workers/udare_reconstruction_worker.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)

import_statement = (
    "from backend.server.stores.udare_store_index_builder "
    "import build_udare_store_index_v1\n"
)


if import_statement not in text:
    lines = text.splitlines(
        keepends=True
    )

    insertion_index = None

    for index, line in enumerate(
        lines
    ):
        stripped = line.lstrip()

        if (
            stripped.startswith(
                "def "
            )
            or stripped.startswith(
                "class "
            )
        ):
            insertion_index = index
            break

    if insertion_index is None:
        raise RuntimeError(
            "Could not identify worker import boundary."
        )

    lines.insert(
        insertion_index,
        import_statement
        + "\n",
    )

    text = "".join(
        lines
    )


if "udare_store_index_result = build_udare_store_index_v1(" not in text:
    pattern = re.compile(
        r'''
        ^(?P<indent>[ \t]*)
        return[ \t]+\{
        [ \t]*\r?\n
        (?P<inner>[ \t]*)
        ["']ok["'][ \t]*:[ \t]*True[ \t]*,
        ''',
        re.MULTILINE
        | re.VERBOSE,
    )

    matches = list(
        pattern.finditer(
            text
        )
    )

    if len(
        matches
    ) != 1:
        raise RuntimeError(
            "Expected exactly one successful worker return "
            f"block; found {len(matches)}."
        )

    match = matches[
        0
    ]

    indent = match.group(
        "indent"
    )

    injection = (
        f'{indent}udare_store_index_result = '
        f'build_udare_store_index_v1(\n'
        f'{indent}    workspace_id\n'
        f'{indent})\n\n'
    )

    text = (
        text[
            :match.start()
        ]
        + injection
        + text[
            match.start():
        ]
    )


ast.parse(
    text,
    filename=str(
        path
    ),
)

path.write_text(
    text,
    encoding="utf-8",
)

print(
    "UDARE WORKER INDEX INTEGRATION: PASS"
)
