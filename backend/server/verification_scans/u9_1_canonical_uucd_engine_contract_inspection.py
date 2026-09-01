from pathlib import Path
import ast

path = Path(
    "backend/server/"
    "universal_unified_content_document/"
    "uucd_engine_v1.py"
)

source = path.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(source)

print("=== U9.1 CANONICAL UUCD ENGINE CONTRACT INSPECTION ===")


# ------------------------------------------------------------
# A. Exact canonical constants
# ------------------------------------------------------------

print()
print("=== A. CANONICAL CONSTANT VALUES ===")

wanted_constants = {
    "UUCD_SCHEMA_VERSION",
    "UUCD_ENGINE_VERSION",
    "REQUIRED_UUCD_RECORD_FIELDS",
}

namespace = {}

exec(
    compile(
        source,
        str(path),
        "exec",
    ),
    namespace,
)

for name in sorted(
    wanted_constants
):
    print()
    print(f"{name}=")
    print(
        repr(
            namespace.get(name)
        )
    )


# ------------------------------------------------------------
# B. Top-level function signatures
# ------------------------------------------------------------

print()
print("=== B. TOP-LEVEL FUNCTION SIGNATURES ===")

for node in tree.body:
    if not isinstance(
        node,
        ast.FunctionDef,
    ):
        continue

    if any(
        marker in node.name.lower()
        for marker in [
            "uucd",
            "wuc",
            "validate",
            "body",
        ]
    ):
        args = []

        for arg in node.args.args:
            args.append(
                arg.arg
            )

        for arg in node.args.kwonlyargs:
            args.append(
                "*:" + arg.arg
            )

        print(
            f"FUNCTION={node.name}"
        )
        print(
            "ARGS="
            + repr(args)
        )


# ------------------------------------------------------------
# C. Exact canonical builder
# ------------------------------------------------------------

print()
print("=== C. CANONICAL BUILDER SOURCE ===")

builder_name = (
    "build_transient_uucd_from_wuc_v1"
)

builder = next(
    (
        node
        for node in tree.body
        if isinstance(
            node,
            ast.FunctionDef,
        )
        and node.name == builder_name
    ),
    None,
)

if builder is None:
    print(
        "CANONICAL_BUILDER_NOT_FOUND"
    )
else:
    print(
        ast.get_source_segment(
            source,
            builder,
        )
    )


# ------------------------------------------------------------
# D. Builder-return keys
# ------------------------------------------------------------

print()
print("=== D. BUILDER RETURN / OUTPUT KEY INVENTORY ===")

if builder is not None:
    string_keys = []

    for node in ast.walk(
        builder
    ):
        if isinstance(
            node,
            ast.Constant,
        ) and isinstance(
            node.value,
            str,
        ):
            value = node.value

            if (
                "_" in value
                or value
                in {
                    "uucd_record",
                    "body_payload",
                    "handoff",
                    "metadata",
                }
            ):
                string_keys.append(
                    value
                )

    for value in sorted(
        set(string_keys)
    ):
        print(
            f"BUILDER_STRING={value}"
        )


# ------------------------------------------------------------
# E. WUC requirements
# ------------------------------------------------------------

print()
print("=== E. WUC INPUT REQUIREMENT INVENTORY ===")

if builder is not None:
    builder_source = (
        ast.get_source_segment(
            source,
            builder,
        )
        or ""
    )

    for line_number, line in enumerate(
        builder_source.splitlines(),
        start=builder.lineno,
    ):
        lower = line.lower()

        if any(
            marker in lower
            for marker in [
                "eligible_for_uucd",
                "workspace_id",
                "document_id",
                "content_body",
                "source_type",
                "content_hash",
                "metadata",
                "handoff",
                "body_",
            ]
        ):
            print(
                f"{line_number}: {line}"
            )


# ------------------------------------------------------------
# F. Validation contract source
# ------------------------------------------------------------

print()
print("=== F. UUCD VALIDATION FUNCTIONS ===")

for node in tree.body:
    if not isinstance(
        node,
        ast.FunctionDef,
    ):
        continue

    if (
        "validate" in node.name.lower()
        or "require" in node.name.lower()
    ):
        text = (
            ast.get_source_segment(
                source,
                node,
            )
            or ""
        )

        if (
            "uucd" in text.lower()
            or "wuc" in text.lower()
        ):
            print()
            print(
                f"--- {node.name} ---"
            )
            print(text)


print()
print(
    "U9.1_ENGINE_CONTRACT_INSPECTION: COMPLETE"
)
print(
    "U9.1_PATCH_DECISION: NONE_INSPECTION_ONLY"
)