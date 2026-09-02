from pathlib import Path

path = Path(
    "backend/server/universal_unified_content_document/"
    "uucd_engine_v1.py"
)

raw = path.read_bytes()
had_bom = raw.startswith(b"\xef\xbb\xbf")
source = raw.decode("utf-8-sig")

function_marker = (
    "def validate_universal_handoff_envelope_v1("
)

gate = '''    if envelope_mapping.get(
        "envelope_status"
    ) != "READY_FOR_BODY_STORE":
        raise UUCDContractError(
            "Envelope status must be READY_FOR_BODY_STORE."
        )

'''

if gate in source:
    print(
        "U9.15_PATCH_STATUS="
        "ENVELOPE_STATUS_GATE_ALREADY_PRESENT"
    )
else:
    start = source.find(
        function_marker
    )

    if start == -1:
        raise RuntimeError(
            "Envelope validator function not found."
        )

    next_function = source.find(
        "\ndef ",
        start + len(function_marker),
    )

    if next_function == -1:
        function_end = len(source)
    else:
        function_end = next_function

    function_source = source[
        start:function_end
    ]

    return_marker = (
        "    return True"
    )

    return_position = function_source.rfind(
        return_marker
    )

    if return_position == -1:
        raise RuntimeError(
            "Final return True not found inside "
            "envelope validator."
        )

    absolute_position = (
        start
        + return_position
    )

    source = (
        source[:absolute_position]
        + gate
        + source[absolute_position:]
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