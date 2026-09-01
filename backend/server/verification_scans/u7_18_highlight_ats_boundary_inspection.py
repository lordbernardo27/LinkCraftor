from pathlib import Path
import ast

target = Path(
    "backend/server/stores/upload_document_normalizer.py"
)

source = target.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(source)

print(
    "=== U7.18 - U7 VS HIGHLIGHT / ATS BOUNDARY INSPECTION ==="
)
print("FILE=", target)


print()
print("=== A. IMPORTS ===")

imports = []

for node in tree.body:
    if isinstance(
        node,
        (
            ast.Import,
            ast.ImportFrom,
        ),
    ):
        code = ast.get_source_segment(
            source,
            node,
        )
        imports.append(code)
        print(code)


print()
print("=== B. DOWNSTREAM TERM SCAN ===")

terms = [
    "highlight",
    "active target",
    "active_target",
    "ats",
    "target_pool",
    "target pool",
    "target_registry",
    "target registry",
    "register_target",
    "target_score",
    "target_rank",
    "scorer",
    "score",
    "ranking",
    "semantic_runtime_reader",
    "phrase_selector",
    "phrase_density",
    "candidate_window_guard",
    "smart_phrase_extractor",
    "route_dispatcher",
    "target_resolution",
    "publication_validation",
    "accept",
    "reject",
    "anchor",
    "workspace_id",
    "registry",
    "uucd",
]

lowered = source.lower()

for term in terms:
    print(
        f"{term}: "
        f"{lowered.count(term.lower())}"
    )


print()
print("=== C. OUTPUT DATACLASS FIELDS ===")

normalized_class = next(
    node
    for node in tree.body
    if isinstance(
        node,
        ast.ClassDef,
    )
    and node.name
    == "NormalizedUploadedDocumentContent"
)

fields = []

for node in normalized_class.body:
    if isinstance(
        node,
        ast.AnnAssign,
    ) and isinstance(
        node.target,
        ast.Name,
    ):
        fields.append(
            node.target.id
        )

for field in fields:
    print(field)

forbidden_fields = {
    "highlight",
    "highlights",
    "highlight_spans",
    "highlight_ranges",
    "anchor",
    "anchors",
    "anchor_candidates",
    "review_decisions",
    "accept_reject",
    "active_target_set",
    "target_id",
    "target_score",
    "target_rank",
    "workspace_id",
    "registry",
    "semantic_score",
    "route",
    "resolved_target",
}

present_forbidden_fields = sorted(
    forbidden_fields.intersection(
        fields
    )
)

print(
    "FORBIDDEN_DOWNSTREAM_FIELD_COUNT=",
    len(
        present_forbidden_fields
    ),
)

for field in present_forbidden_fields:
    print(
        "FORBIDDEN_FIELD=",
        field,
    )


print()
print("=== D. CALL-SITE SCAN ===")

downstream_call_terms = {
    "highlight",
    "active_target",
    "target",
    "score",
    "rank",
    "registry",
    "workspace",
    "semantic",
    "route",
    "resolve",
    "publish",
}

call_hits = []

for node in ast.walk(tree):
    if not isinstance(
        node,
        ast.Call,
    ):
        continue

    call = (
        ast.get_source_segment(
            source,
            node,
        )
        or ""
    )

    lowered_call = call.lower()

    if any(
        term in lowered_call
        for term in downstream_call_terms
    ):
        call_hits.append(
            (
                getattr(
                    node,
                    "lineno",
                    None,
                ),
                call,
            )
        )

for line, call in call_hits:
    print()
    print(
        f"LINE {line}"
    )
    print(call)

print(
    "DOWNSTREAM_CALL_HIT_COUNT=",
    len(call_hits),
)


print()
print("=== E. ASSIGNMENT / MUTATION SCAN ===")

mutation_terms = (
    "workspace",
    "registry",
    "target",
    "highlight",
)

mutation_hits = []

for node in ast.walk(tree):
    if not isinstance(
        node,
        (
            ast.Assign,
            ast.AnnAssign,
            ast.AugAssign,
        ),
    ):
        continue

    code = (
        ast.get_source_segment(
            source,
            node,
        )
        or ""
    )

    lowered_code = code.lower()

    if any(
        term in lowered_code
        for term in mutation_terms
    ):
        mutation_hits.append(
            (
                getattr(
                    node,
                    "lineno",
                    None,
                ),
                code,
            )
        )

for line, code in mutation_hits:
    print()
    print(
        f"LINE {line}"
    )
    print(code)

print(
    "DOWNSTREAM_MUTATION_HIT_COUNT=",
    len(mutation_hits),
)


print()
print("=== F. BOUNDARY DECISION ===")

print(
    "U7_OUTPUT_HAS_HIGHLIGHT_ATS_FIELDS:",
    "YES"
    if present_forbidden_fields
    else "NO",
)

print(
    "U7_HAS_HIGHLIGHT_IMPORT:",
    "YES"
    if any(
        "highlight" in (
            item or ""
        ).lower()
        for item in imports
    )
    else "NO",
)

print(
    "U7_HAS_ATS_TARGET_IMPORT:",
    "YES"
    if any(
        (
            "active_target" in (
                item or ""
            ).lower()
            or "target_pool" in (
                item or ""
            ).lower()
        )
        for item in imports
    )
    else "NO",
)

print(
    "U7_DOWNSTREAM_CALL_DEPENDENCY:",
    "YES"
    if call_hits
    else "NO",
)

print(
    "U7_DOWNSTREAM_MUTATION_DEPENDENCY:",
    "YES"
    if mutation_hits
    else "NO",
)