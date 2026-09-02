from pathlib import Path

path = Path(
    "backend/server/runtime/"
    "uucd_runtime_handoff_v1.py"
)

raw = path.read_bytes()
had_bom = raw.startswith(
    b"\xef\xbb\xbf"
)

source = raw.decode(
    "utf-8-sig"
)

source = source.replace(
    "\r\n",
    "\n",
)

gate_marker = (
    'record.get(\n'
    '            "body_status"\n'
)

if gate_marker in source:
    print(
        "U9.19_PATCH_STATUS="
        "BODY_STATUS_GATE_ALREADY_PRESENT"
    )

else:
    anchor = '''    if "content_body" in record:
        raise UUCDRuntimeHandoffContractError(
            "Persisted UUCD must not contain content_body."
        )

'''

    replacement = '''    if "content_body" in record:
        raise UUCDRuntimeHandoffContractError(
            "Persisted UUCD must not contain content_body."
        )

    if (
        record.get(
            "body_status"
        )
        != "STORED_AND_VERIFIED"
    ):
        raise UUCDRuntimeHandoffContractError(
            "body_status must be STORED_AND_VERIFIED."
        )

'''

    if anchor not in source:
        raise RuntimeError(
            "Could not locate persisted-UUCD "
            "content_body boundary."
        )

    source = source.replace(
        anchor,
        replacement,
        1,
    )

    encoding = (
        "utf-8-sig"
        if had_bom
        else "utf-8"
    )

    path.write_text(
        source,
        encoding=encoding,
        newline="\n",
    )

    print(
        "U9.19_PATCH_STATUS="
        "BODY_STATUS_GATE_ADDED"
    )

print(
    "TARGET="
    + str(path)
)