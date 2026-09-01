from pathlib import Path
import ast

target = Path(
    "backend/server/stores/uploaded_document_unified_content.py"
)

source = target.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(source)

print(
    "=== U7.17 UDUC NORMALIZATION-LIKE CALL CLASSIFICATION ==="
)

wanted_attrs = {
    "strip",
    "lower",
    "upper",
    "replace",
    "split",
    "join",
}

hits = []

for node in ast.walk(tree):
    if not isinstance(node, ast.Call):
        continue

    if not isinstance(node.func, ast.Attribute):
        continue

    if node.func.attr not in wanted_attrs:
        continue

    hits.append(
        (
            node.lineno,
            node.func.attr,
            ast.get_source_segment(
                source,
                node,
            ),
        )
    )

for line, attr, code in sorted(
    hits,
    key=lambda item: item[0],
):
    print()
    print(
        f"LINE {line} [{attr}]"
    )
    print(code)

print()
print(
    "NORMALIZATION_LIKE_CALL_COUNT=",
    len(hits),
)

print()
print("=== REGEX CALLS ===")

regex_hits = []

for node in ast.walk(tree):
    if not isinstance(node, ast.Call):
        continue

    call = (
        ast.get_source_segment(
            source,
            node,
        )
        or ""
    )

    if (
        "re.sub(" in call
        or "re.split(" in call
        or "re.finditer(" in call
    ):
        regex_hits.append(
            (
                node.lineno,
                call,
            )
        )

for line, call in sorted(
    regex_hits,
    key=lambda item: item[0],
):
    print()
    print(
        f"LINE {line}"
    )
    print(call)

print()
print(
    "REGEX_CALL_COUNT=",
    len(regex_hits),
)