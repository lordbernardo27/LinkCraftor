from pathlib import Path
import ast


print("=== U9.2 UUCD SOURCE-BOUNDARY INSPECTION ===")


engine_path = Path(
    "backend/server/"
    "universal_unified_content_document/"
    "uucd_engine_v1.py"
)

uduc_path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

coordinator_path = Path(
    "backend/server/pipelines/"
    "upload_document/coordinator.py"
)


engine_source = engine_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

engine_tree = ast.parse(
    engine_source
)

uduc_source = uduc_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

coordinator_source = coordinator_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)


# ------------------------------------------------------------
# A. Hard-coded WUC assumptions
# ------------------------------------------------------------

print()
print("=== A. HARD-CODED WUC ASSUMPTIONS ===")

wuc_markers = [
    "website_unified_content",
    "full_body_received_from_wuc",
    "wuc_schema_version",
    "wuc_engine_version",
    "wuc_content_id",
    "WUC package",
    "wuc_package",
]

for marker in wuc_markers:
    count = engine_source.count(
        marker
    )

    print(
        f"{marker}={count}"
    )


# ------------------------------------------------------------
# B. Source-neutral helpers
# ------------------------------------------------------------

print()
print("=== B. SOURCE-NEUTRAL HELPER INVENTORY ===")

neutral_candidates = [
    "_stable_document_id",
    "_stable_content_ref",
    "_stable_body_ref",
    "compute_canonical_content_hash_v1",
    "_binding_hash",
    "validate_universal_handoff_envelope_v1",
]

function_names = {
    node.name
    for node in engine_tree.body
    if isinstance(
        node,
        ast.FunctionDef,
    )
}

for name in neutral_candidates:
    print(
        f"{name}_PRESENT="
        f"{name in function_names}"
    )


# ------------------------------------------------------------
# C. Exact helper signatures
# ------------------------------------------------------------

print()
print("=== C. SOURCE-NEUTRAL HELPER SIGNATURES ===")

for node in engine_tree.body:
    if not isinstance(
        node,
        ast.FunctionDef,
    ):
        continue

    if node.name not in neutral_candidates:
        continue

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
        f"ARGS={args}"
    )


# ------------------------------------------------------------
# D. Source-type support
# ------------------------------------------------------------

print()
print("=== D. SUPPORTED SOURCE TYPES ===")

namespace = {}

exec(
    compile(
        engine_source,
        str(engine_path),
        "exec",
    ),
    namespace,
)

supported_source_types = namespace.get(
    "SUPPORTED_SOURCE_TYPES"
)

print(
    "SUPPORTED_SOURCE_TYPES="
    + repr(
        supported_source_types
    )
)


# ------------------------------------------------------------
# E. Current UDUC source contract
# ------------------------------------------------------------

print()
print("=== E. CURRENT UDUC SOURCE CONTRACT ===")

for marker in [
    '"source_type": "uploaded_document"',
    'source_type="uploaded_document"',
    "source_type",
    "source_format",
    "content_body",
    "structure",
    "metadata",
    "workspace_id",
    "document_id",
]:
    print(
        f"UDUC_MARKER_{marker}="
        f"{marker in uduc_source}"
    )


# ------------------------------------------------------------
# F. Current upload coordinator U8 end-point
# ------------------------------------------------------------

print()
print("=== F. CURRENT UPLOAD COORDINATOR U8 END-POINT ===")

for marker in [
    "build_and_write_uduc_from_normalized_content",
    "uduc_result",
    'uduc_result.get("uduc")',
    "run_uploaded_document_to_highlight_pipeline",
    "run_uploaded_document_registry_to_active_target_set_pipeline",
    "build_transient_uucd_from_wuc_v1",
    "persist_finalized_uucd_v1",
]:
    print(
        f"COORDINATOR_MARKER_{marker}="
        f"{marker in coordinator_source}"
    )


# ------------------------------------------------------------
# G. WUC-specific builder internals
# ------------------------------------------------------------

print()
print("=== G. WUC-SPECIFIC BUILDER INTERNALS ===")

builder = next(
    (
        node
        for node in engine_tree.body
        if isinstance(
            node,
            ast.FunctionDef,
        )
        and node.name
        == "build_transient_uucd_from_wuc_v1"
    ),
    None,
)

if builder is None:
    print(
        "BUILDER_NOT_FOUND"
    )
else:
    builder_source = (
        ast.get_source_segment(
            engine_source,
            builder,
        )
        or ""
    )

    for marker in [
        "_stable_document_id",
        "_stable_content_ref",
        "_stable_body_ref",
        "compute_canonical_content_hash_v1",
        "_binding_hash",
        "validate_universal_handoff_envelope_v1",
        "website_unified_content",
        "full_body_received_from_wuc",
    ]:
        print(
            f"BUILDER_USES_{marker}="
            f"{marker in builder_source}"
        )


# ------------------------------------------------------------
# H. Source-aware entry-point candidates
# ------------------------------------------------------------

print()
print("=== H. SOURCE-AWARE ENTRY-POINT CANDIDATES ===")

source_aware_functions = []

for node in engine_tree.body:
    if not isinstance(
        node,
        ast.FunctionDef,
    ):
        continue

    source = (
        ast.get_source_segment(
            engine_source,
            node,
        )
        or ""
    ).lower()

    if (
        "source_type"
        in source
        and "wuc_package"
        not in source
        and node.name
        != "_validate_wuc_contract"
    ):
        source_aware_functions.append(
            node.name
        )

print(
    "SOURCE_AWARE_FUNCTION_COUNT="
    + str(
        len(source_aware_functions)
    )
)

for name in source_aware_functions:
    print(
        f"SOURCE_AWARE_FUNCTION={name}"
    )


# ------------------------------------------------------------
# I. Boundary decision evidence
# ------------------------------------------------------------

print()
print("=== I. U9.2 BOUNDARY EVIDENCE ===")

print(
    "CURRENT_UUCD_SCHEMA="
    + repr(
        namespace.get(
            "UUCD_SCHEMA_VERSION"
        )
    )
)

print(
    "CURRENT_UUCD_ENGINE_VERSION="
    + repr(
        namespace.get(
            "UUCD_ENGINE_VERSION"
        )
    )
)

print(
    "CURRENT_BUILDER="
    "build_transient_uucd_from_wuc_v1"
)

print(
    "CURRENT_BUILDER_IS_WUC_SPECIFIC="
    + str(
        "website_unified_content"
        in engine_source
        and "full_body_received_from_wuc"
        in engine_source
    )
)

print(
    "CANONICAL_HELPERS_ARE_REUSABLE="
    + str(
        all(
            name in function_names
            for name in neutral_candidates
        )
    )
)

print(
    "UPLOAD_COORDINATOR_ALREADY_RUNS_UUCD="
    + str(
        "build_transient_uucd_from_wuc_v1"
        in coordinator_source
        or "persist_finalized_uucd_v1"
        in coordinator_source
    )
)

print(
    "U9.2_PATCH_DECISION: PENDING_STRATEGY_CLASSIFICATION"
)

print(
    "U9.2_NEXT_STEP: CLASSIFY_SOURCE_AWARE_ADAPTER_VS_DEDICATED_UDUC_BUILDER"
)