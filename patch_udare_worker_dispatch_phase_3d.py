from __future__ import annotations

import ast
from pathlib import Path


path = Path(
    "backend/server/workers/universal_knowledge_worker.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)


LEGACY_NAME = (
    "_execute_universal_knowledge_job_without_udare_v1"
)

PUBLIC_NAME = (
    "execute_universal_knowledge_job_v1"
)


def offsets(
    value: str,
) -> list[int]:
    results = [
        0
    ]

    for index, character in enumerate(
        value
    ):
        if character == "\n":
            results.append(
                index + 1
            )

    return results


def node_range(
    value: str,
    node: ast.AST,
) -> tuple[int, int]:
    line_offsets = offsets(
        value
    )

    start = (
        line_offsets[
            node.lineno - 1
        ]
        + node.col_offset
    )

    end = (
        line_offsets[
            node.end_lineno - 1
        ]
        + node.end_col_offset
    )

    return start, end


def argument_names(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[str]:
    return [
        argument.arg

        for argument
        in (
            list(
                function.args.posonlyargs
            )
            + list(
                function.args.args
            )
            + list(
                function.args.kwonlyargs
            )
        )
    ]


def delegation_call(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
) -> str:
    parts: list[str] = []

    for argument in function.args.posonlyargs:
        parts.append(
            argument.arg
        )

    for argument in function.args.args:
        parts.append(
            argument.arg
        )

    if function.args.vararg is not None:
        parts.append(
            "*"
            + function.args.vararg.arg
        )

    for argument in function.args.kwonlyargs:
        parts.append(
            argument.arg
            + "="
            + argument.arg
        )

    if function.args.kwarg is not None:
        parts.append(
            "**"
            + function.args.kwarg.arg
        )

    return ",\n        ".join(
        parts
    )


tree = ast.parse(
    text,
    filename=str(
        path
    ),
)


public_function = next(
    (
        node

        for node
        in tree.body

        if (
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name
            == PUBLIC_NAME
        )
    ),
    None,
)


legacy_function = next(
    (
        node

        for node
        in tree.body

        if (
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name
            == LEGACY_NAME
        )
    ),
    None,
)


already_patched = (
    legacy_function is not None
    and public_function is not None
    and "run_udare_reconstruction_job_v1"
    in ast.get_source_segment(
        text,
        public_function,
    )
)


if already_patched:
    print(
        "Universal worker UDARE dispatch already present."
    )

else:
    if public_function is None:
        raise RuntimeError(
            "execute_universal_knowledge_job_v1 was not found."
        )

    start, end = node_range(
        text,
        public_function,
    )

    original_source = text[
        start:end
    ]

    renamed_source = original_source.replace(
        (
            "def "
            + PUBLIC_NAME
            + "("
        ),
        (
            "def "
            + LEGACY_NAME
            + "("
        ),
        1,
    )

    if (
        renamed_source
        == original_source
    ):
        renamed_source = original_source.replace(
            (
                "async def "
                + PUBLIC_NAME
                + "("
            ),
            (
                "async def "
                + LEGACY_NAME
                + "("
            ),
            1,
        )

    if (
        renamed_source
        == original_source
    ):
        raise RuntimeError(
            "Unable to rename the existing universal executor."
        )

    arguments_source = ast.unparse(
        public_function.args
    )

    return_annotation = (
        (
            " -> "
            + ast.unparse(
                public_function.returns
            )
        )
        if public_function.returns is not None
        else ""
    )

    known_arguments = argument_names(
        public_function
    )

    job_argument = (
        "job"
        if "job" in known_arguments
        else (
            "job_data"
            if "job_data" in known_arguments
            else (
                known_arguments[
                    0
                ]
                if known_arguments
                else ""
            )
        )
    )

    if not job_argument:
        raise RuntimeError(
            "The universal worker executor has no job argument."
        )

    delegated_arguments = delegation_call(
        public_function
    )

    async_prefix = (
        "async "
        if isinstance(
            public_function,
            ast.AsyncFunctionDef,
        )
        else ""
    )

    await_prefix = (
        "await "
        if isinstance(
            public_function,
            ast.AsyncFunctionDef,
        )
        else ""
    )

    wrapper_source = (
        "\n\n"
        + async_prefix
        + "def "
        + PUBLIC_NAME
        + "("
        + arguments_source
        + ")"
        + return_annotation
        + ":\n"
        + "    _udare_job = "
        + job_argument
        + "\n\n"
        + "    if (\n"
        + "        isinstance(_udare_job, dict)\n"
        + "        and str(\n"
        + "            _udare_job.get(\"job_type\")\n"
        + "            or _udare_job.get(\"stage\")\n"
        + "            or \"\"\n"
        + "        ).strip()\n"
        + "        == \"udare_reconstruction\"\n"
        + "    ):\n"
        + "        from backend.server.workers.udare_reconstruction_worker import (\n"
        + "            run_udare_reconstruction_job_v1,\n"
        + "        )\n\n"
        + "        return run_udare_reconstruction_job_v1(\n"
        + "            job=_udare_job,\n"
        + "        )\n\n"
        + "    return "
        + await_prefix
        + LEGACY_NAME
        + "(\n"
        + "        "
        + delegated_arguments
        + "\n"
        + "    )"
    )

    updated = (
        text[
            :start
        ]
        + renamed_source
        + wrapper_source
        + text[
            end:
        ]
    )

    ast.parse(
        updated,
        filename=str(
            path
        ),
    )

    path.write_text(
        updated,
        encoding="utf-8",
    )

    print(
        "Universal worker UDARE dispatch patch: PASS"
    )

    print(
        "Existing non-UDARE executor preserved as:",
        LEGACY_NAME,
    )


final_text = path.read_text(
    encoding="utf-8-sig"
)

final_tree = ast.parse(
    final_text,
    filename=str(
        path
    ),
)

function_names = [
    node.name

    for node
    in final_tree.body

    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    )
]

if function_names.count(
    PUBLIC_NAME
) != 1:
    raise RuntimeError(
        "Expected exactly one public universal executor."
    )

if function_names.count(
    LEGACY_NAME
) != 1:
    raise RuntimeError(
        "Expected exactly one preserved legacy executor."
    )

print(
    "Universal worker dispatcher structure: PASS"
)
