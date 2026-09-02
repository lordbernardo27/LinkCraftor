import backend.server.universal_unified_content_document.uucd_engine_v1 as uucd


print("=== U9.7 CANONICAL IDENTITY CONTRACT INSPECTION ===")


# ------------------------------------------------------------
# A. Frozen Uploaded Document source identity
# ------------------------------------------------------------

print()
print("=== A. SOURCE IDENTITY AUTHORITY ===")

workspace_id = "ws_u9_7"
source_type = "uploaded_document"
source_record_id = "upload_doc_001"
title = "Identity Contract Document"

print(
    "WORKSPACE_ID="
    + repr(workspace_id)
)

print(
    "SOURCE_TYPE="
    + repr(source_type)
)

print(
    "SOURCE_RECORD_ID="
    + repr(source_record_id)
)

print(
    "SOURCE_NAME_PRIORITY="
    "original_filename>stored_filename>document_id"
)

print(
    "CANONICAL_URL="
    + repr("")
)


# ------------------------------------------------------------
# B. Canonical document_id derivation
# ------------------------------------------------------------

print()
print("=== B. CANONICAL DOCUMENT_ID DERIVATION ===")

document_id_1 = uucd._stable_document_id(
    workspace_id=workspace_id,
    source_type=source_type,
    source_record_id=source_record_id,
)

document_id_2 = uucd._stable_document_id(
    workspace_id=workspace_id,
    source_type=source_type,
    source_record_id=source_record_id,
)

print(
    "DOCUMENT_ID_1="
    + repr(document_id_1)
)

print(
    "DOCUMENT_ID_2="
    + repr(document_id_2)
)

print(
    "DOCUMENT_ID_DETERMINISTIC="
    + str(
        document_id_1
        == document_id_2
    )
)

print(
    "DOCUMENT_ID_DIRECTLY_REUSES_UDUC_ID="
    + str(
        document_id_1
        == source_record_id
    )
)


# ------------------------------------------------------------
# C. Workspace sensitivity
# ------------------------------------------------------------

print()
print("=== C. WORKSPACE SENSITIVITY ===")

different_workspace_id = (
    uucd._stable_document_id(
        workspace_id="ws_u9_7_other",
        source_type=source_type,
        source_record_id=source_record_id,
    )
)

print(
    "DIFFERENT_WORKSPACE_DOCUMENT_ID="
    + repr(
        different_workspace_id
    )
)

print(
    "WORKSPACE_CHANGES_DOCUMENT_ID="
    + str(
        different_workspace_id
        != document_id_1
    )
)


# ------------------------------------------------------------
# D. Source-record sensitivity
# ------------------------------------------------------------

print()
print("=== D. SOURCE_RECORD SENSITIVITY ===")

different_source_record_id = (
    uucd._stable_document_id(
        workspace_id=workspace_id,
        source_type=source_type,
        source_record_id="upload_doc_002",
    )
)

print(
    "DIFFERENT_SOURCE_RECORD_DOCUMENT_ID="
    + repr(
        different_source_record_id
    )
)

print(
    "SOURCE_RECORD_CHANGES_DOCUMENT_ID="
    + str(
        different_source_record_id
        != document_id_1
    )
)


# ------------------------------------------------------------
# E. Source-type sensitivity
# ------------------------------------------------------------

print()
print("=== E. SOURCE_TYPE SENSITIVITY ===")

different_source_type_id = (
    uucd._stable_document_id(
        workspace_id=workspace_id,
        source_type="website",
        source_record_id=source_record_id,
    )
)

print(
    "DIFFERENT_SOURCE_TYPE_DOCUMENT_ID="
    + repr(
        different_source_type_id
    )
)

print(
    "SOURCE_TYPE_CHANGES_DOCUMENT_ID="
    + str(
        different_source_type_id
        != document_id_1
    )
)


# ------------------------------------------------------------
# F. content_ref determinism and scoping
# ------------------------------------------------------------

print()
print("=== F. CONTENT_REF CONTRACT ===")

content_ref_1 = uucd._stable_content_ref(
    workspace_id=workspace_id,
    document_id=document_id_1,
)

content_ref_2 = uucd._stable_content_ref(
    workspace_id=workspace_id,
    document_id=document_id_1,
)

content_ref_other_workspace = (
    uucd._stable_content_ref(
        workspace_id="ws_u9_7_other",
        document_id=document_id_1,
    )
)

print(
    "CONTENT_REF_1="
    + repr(content_ref_1)
)

print(
    "CONTENT_REF_2="
    + repr(content_ref_2)
)

print(
    "CONTENT_REF_DETERMINISTIC="
    + str(
        content_ref_1
        == content_ref_2
    )
)

print(
    "CONTENT_REF_WORKSPACE_SCOPED="
    + str(
        content_ref_other_workspace
        != content_ref_1
    )
)

print(
    "CONTENT_REF_CONTAINS_WORKSPACE="
    + str(
        workspace_id
        in content_ref_1
    )
)

print(
    "CONTENT_REF_CONTAINS_DOCUMENT_ID="
    + str(
        document_id_1
        in content_ref_1
    )
)


# ------------------------------------------------------------
# G. body_ref determinism and scoping
# ------------------------------------------------------------

print()
print("=== G. BODY_REF CONTRACT ===")

body_ref_1 = uucd._stable_body_ref(
    workspace_id=workspace_id,
    document_id=document_id_1,
    title=title,
)

body_ref_2 = uucd._stable_body_ref(
    workspace_id=workspace_id,
    document_id=document_id_1,
    title=title,
)

body_ref_other_workspace = (
    uucd._stable_body_ref(
        workspace_id="ws_u9_7_other",
        document_id=document_id_1,
        title=title,
    )
)

body_ref_other_document = (
    uucd._stable_body_ref(
        workspace_id=workspace_id,
        document_id=different_source_record_id,
        title=title,
    )
)

body_ref_other_title = (
    uucd._stable_body_ref(
        workspace_id=workspace_id,
        document_id=document_id_1,
        title="Different Identity Contract Title",
    )
)

print(
    "BODY_REF_1="
    + repr(body_ref_1)
)

print(
    "BODY_REF_2="
    + repr(body_ref_2)
)

print(
    "BODY_REF_DETERMINISTIC="
    + str(
        body_ref_1
        == body_ref_2
    )
)

print(
    "BODY_REF_WORKSPACE_SCOPED="
    + str(
        body_ref_other_workspace
        != body_ref_1
    )
)

print(
    "BODY_REF_DOCUMENT_SCOPED="
    + str(
        body_ref_other_document
        != body_ref_1
    )
)

print(
    "BODY_REF_TITLE_SENSITIVE="
    + str(
        body_ref_other_title
        != body_ref_1
    )
)

print(
    "BODY_REF_CONTAINS_WORKSPACE="
    + str(
        workspace_id
        in body_ref_1
    )
)


# ------------------------------------------------------------
# H. Identity-format checks
# ------------------------------------------------------------

print()
print("=== H. CANONICAL ID FORMAT ===")

print(
    "DOCUMENT_ID_PREFIX_OK="
    + str(
        document_id_1.startswith(
            "uucd_"
        )
    )
)

print(
    "DOCUMENT_ID_LENGTH="
    + str(
        len(document_id_1)
    )
)

hex_part = (
    document_id_1[
        len("uucd_"):
    ]
)

print(
    "DOCUMENT_ID_HEX_LENGTH="
    + str(
        len(hex_part)
    )
)

print(
    "DOCUMENT_ID_HEX_ONLY="
    + str(
        all(
            c in "0123456789abcdef"
            for c in hex_part
        )
    )
)


# ------------------------------------------------------------
# I. No random/time-based identity evidence
# ------------------------------------------------------------

print()
print("=== I. RANDOM / TIME IDENTITY EXCLUSIONS ===")

helper_source = (
    uucd._stable_document_id.__code__
)

print(
    "STABLE_DOCUMENT_ID_FUNCTION_NAME="
    + repr(
        helper_source.co_name
    )
)

print(
    "STABLE_DOCUMENT_ID_ARGUMENTS="
    + repr(
        helper_source.co_varnames[
            :helper_source.co_argcount
            + helper_source.co_kwonlyargcount
        ]
    )
)

print(
    "TIMESTAMP_ARGUMENT_PRESENT="
    + str(
        "timestamp"
        in helper_source.co_varnames
        or "created_at"
        in helper_source.co_varnames
    )
)

print(
    "RANDOM_ARGUMENT_PRESENT="
    + str(
        "random"
        in helper_source.co_varnames
        or "uuid"
        in helper_source.co_varnames
    )
)


# ------------------------------------------------------------
# J. Frozen identity mapping summary
# ------------------------------------------------------------

print()
print("=== J. U9.7 IDENTITY CONTRACT SUMMARY ===")

print(
    "U9.7_WORKSPACE_ID_AUTHORITY="
    "UDUC_WORKSPACE_ID"
)

print(
    "U9.7_SOURCE_TYPE="
    "uploaded_document"
)

print(
    "U9.7_SOURCE_RECORD_ID_AUTHORITY="
    "UDUC_DOCUMENT_ID"
)

print(
    "U9.7_SOURCE_ID="
    "UDUC_DOCUMENT_ID"
)

print(
    "U9.7_SOURCE_IDENTITY_SOURCE_RECORD_ID="
    "UDUC_DOCUMENT_ID"
)

print(
    "U9.7_CANONICAL_DOCUMENT_ID="
    "STABLE_HELPER(workspace_id,source_type,source_record_id)"
)

print(
    "U9.7_SOURCE_NAME_PRIORITY="
    "ORIGINAL_FILENAME>STORED_FILENAME>UDUC_DOCUMENT_ID"
)

print(
    "U9.7_CANONICAL_URL="
    "EMPTY_STRING"
)

print(
    "U9.7_CONTENT_REF="
    "STABLE_WORKSPACE_DOCUMENT_SCOPED"
)

print(
    "U9.7_BODY_REF="
    "STABLE_WORKSPACE_DOCUMENT_TITLE_SCOPED"
)

print(
    "U9.7_RANDOM_UUID_ALLOWED=False"
)

print(
    "U9.7_TIMESTAMP_IDENTITY_ALLOWED=False"
)

print(
    "U9.7_FILENAME_ONLY_IDENTITY_ALLOWED=False"
)

print(
    "U9.7_STORED_PATH_ONLY_IDENTITY_ALLOWED=False"
)

print(
    "U9.7_PATCH_DECISION: NONE_INSPECTION_ONLY"
)

print(
    "U9.7_NEXT_STEP: FREEZE_CANONICAL_IDENTITY_CONTRACT"
)