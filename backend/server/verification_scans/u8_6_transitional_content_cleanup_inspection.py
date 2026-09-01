from pathlib import Path
import ast


path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

source = path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

tree = ast.parse(source)


print(
    "=== U8.6 TRANSITIONAL CONTENT CLEANUP INSPECTION ==="
)

print(
    f"FILE={path}"
)


# ------------------------------------------------------------
# A. All .strip() calls
# ------------------------------------------------------------

print()
print("=== A. ALL .strip() CALLS ===")

strip_calls = []

for node in ast.walk(tree):
    if not isinstance(node, ast.Call):
        continue

    func = node.func

    if not (
        isinstance(func, ast.Attribute)
        and func.attr == "strip"
    ):
        continue

    code = (
        ast.get_source_segment(
            source,
            node,
        )
        or ""
    )

    strip_calls.append(
        (
            getattr(
                node,
                "lineno",
                None,
            ),
            code,
        )
    )

for line, code in strip_calls:
    print()
    print(
        f"LINE {line}: {code}"
    )

print(
    "STRIP_CALL_COUNT=",
    len(strip_calls),
)


# ------------------------------------------------------------
# B. Canonical builder exact content assignments
# ------------------------------------------------------------

print()
print(
    "=== B. CANONICAL BUILDER CONTENT ASSIGNMENTS ==="
)

builder = next(
    node
    for node in tree.body
    if isinstance(
        node,
        ast.FunctionDef,
    )
    and node.name
    == "build_uduc_from_normalized_content"
)

builder_source = (
    ast.get_source_segment(
        source,
        builder,
    )
    or ""
)

for marker in [
    "title = normalized_content.title",
    "headings = list(",
    "normalized_content.headings",
    "content_body =",
    "normalized_content.text",
]:
    print(
        f"{marker}:",
        "YES"
        if marker in builder_source
        else "NO",
    )


# ------------------------------------------------------------
# C. Helper function bodies
# ------------------------------------------------------------

print()
print("=== C. CONTENT-RELATED HELPERS ===")

wanted = {
    "_as_list",
    "_paragraphs_from_content_body",
    "_build_heading_map",
    "_build_uduc_structure",
}

for node in tree.body:
    if (
        isinstance(
            node,
            ast.FunctionDef,
        )
        and node.name in wanted
    ):
        print()
        print(
            f"--- {node.name} ---"
        )
        print(
            ast.get_source_segment(
                source,
                node,
            )
        )


# ------------------------------------------------------------
# D. _as_list reachability
# ------------------------------------------------------------

print()
print("=== D. _as_list REACHABILITY ===")

as_list_calls = []

for node in ast.walk(tree):
    if not isinstance(
        node,
        ast.Call,
    ):
        continue

    if (
        isinstance(
            node.func,
            ast.Name,
        )
        and node.func.id
        == "_as_list"
    ):
        as_list_calls.append(
            (
                getattr(
                    node,
                    "lineno",
                    None,
                ),
                ast.get_source_segment(
                    source,
                    node,
                )
                or "",
            )
        )

for line, code in as_list_calls:
    print(
        f"LINE {line}: {code}"
    )

print(
    "AS_LIST_CALL_COUNT=",
    len(as_list_calls),
)


# ------------------------------------------------------------
# E. Canonical builder normalization-like calls
# ------------------------------------------------------------

print()
print(
    "=== E. CANONICAL BUILDER NORMALIZATION-LIKE CALLS ==="
)

normalization_markers = [
    ".strip(",
    "unicodedata",
    "normalize(",
    "_normalize_",
    "fix_mojibake",
    "article_cleaning",
    "article_body_cleaning",
    "re.sub(",
]

for marker in normalization_markers:
    print(
        f"{marker}: "
        f"{builder_source.count(marker)}"
    )


# ------------------------------------------------------------
# F. H1 compatibility block
# ------------------------------------------------------------

print()
print("=== F. H1 COMPATIBILITY EVIDENCE ===")

for node in ast.walk(builder):
    if not isinstance(
        node,
        ast.Assign,
    ):
        continue

    targets = [
        target.id
        for target in node.targets
        if isinstance(
            target,
            ast.Name,
        )
    ]

    if "h1" in targets:
        print(
            ast.get_source_segment(
                source,
                node,
            )
        )


# ------------------------------------------------------------
# G. Structural offset behavior
# ------------------------------------------------------------

print()
print("=== G. PARAGRAPH OFFSET EVIDENCE ===")

paragraph_fn = next(
    node
    for node in tree.body
    if isinstance(
        node,
        ast.FunctionDef,
    )
    and node.name
    == "_paragraphs_from_content_body"
)

paragraph_source = (
    ast.get_source_segment(
        source,
        paragraph_fn,
    )
    or ""
)

for marker in [
    "m.start()",
    "m.end()",
    "block = m.group(0).strip()",
    '"text": block',
    '"start_char": m.start()',
    '"end_char": m.end()',
]:
    print(
        f"{marker}:",
        "YES"
        if marker in paragraph_source
        else "NO",
    )


# ------------------------------------------------------------
# H. Heading map exactness
# ------------------------------------------------------------

print()
print("=== H. HEADING MAP EXACTNESS ===")

heading_fn = next(
    node
    for node in tree.body
    if isinstance(
        node,
        ast.FunctionDef,
    )
    and node.name
    == "_build_heading_map"
)

heading_source = (
    ast.get_source_segment(
        source,
        heading_fn,
    )
    or ""
)

for marker in [
    'h = str(heading or "").strip()',
    "body.find(h, search_from)",
    '"heading": h',
]:
    print(
        f"{marker}:",
        "YES"
        if marker in heading_source
        else "NO",
    )


# ------------------------------------------------------------
# I. Final classification evidence
# ------------------------------------------------------------

print()
print("=== I. U8.6 CLASSIFICATION EVIDENCE ===")

print(
    "CANONICAL_TITLE_RENORMALIZED:",
    "YES"
    if "title = normalized_content.title.strip("
    in builder_source
    else "NO",
)

print(
    "CANONICAL_BODY_RENORMALIZED:",
    "YES"
    if "normalized_content.text.strip("
    in builder_source
    else "NO",
)

print(
    "CANONICAL_HEADINGS_RENORMALIZED:",
    "YES"
    if "_as_list(normalized_content.headings)"
    in builder_source
    else "NO",
)

print(
    "HEADING_MAP_STRIPS_DERIVED_HEADING:",
    "YES"
    if 'h = str(heading or "").strip()'
    in heading_source
    else "NO",
)

print(
    "PARAGRAPH_OBJECT_TEXT_STRIPS_MATCH:",
    "YES"
    if "block = m.group(0).strip()"
    in paragraph_source
    else "NO",
)

print(
    "H1_STRIP_PRESENT:",
    "YES"
    if ").strip()" in builder_source
    and "h1 = str(" in builder_source
    else "NO",
)

print(
    "U8.6_NEXT_DECISION:",
    "PATCH_ONLY_IF_DERIVED_STRUCTURE_CHANGES_CANONICAL_U7_IDENTITY",
)