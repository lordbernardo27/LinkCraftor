from pathlib import Path

path = Path(
    "backend/server/universal_unified_content_document/"
    "uucd_engine_v1.py"
)

raw = path.read_bytes()
had_bom = raw.startswith(b"\xef\xbb\xbf")
source = raw.decode("utf-8-sig")

needle = '''    if uucd_record.get(
        "body_status"
    ) != "PENDING_BODY_STORE_WRITE":
        raise UUCDContractError(
            "UUCD body_status must be PENDING_BODY_STORE_WRITE."
        )

    return True
'''

replacement = '''    if uucd_record.get(
        "body_status"
    ) != "PENDING_BODY_STORE_WRITE":
        raise UUCDContractError(
            "UUCD body_status must be PENDING_BODY_STORE_WRITE."
        )

    if envelope_mapping.get(
        "envelope_status"
    ) != "READY_FOR_BODY_STORE":
        raise UUCDContractError(
            "Envelope status must be READY_FOR_BODY_STORE."
        )

    return True
'''

if replacement in source:
    print(
        "U9.15_PATCH_STATUS="
        "ENVELOPE_STATUS_GATE_ALREADY_PRESENT"
    )
elif needle not in source:
    raise RuntimeError(
        "Could not locate exact validator insertion point."
    )
else:
    source = source.replace(
        needle,
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
        "U9.15_PATCH_STATUS="
        "ENVELOPE_STATUS_GATE_ADDED"
    )

print(
    "TARGET="
    + str(path)
)