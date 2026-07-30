from __future__ import annotations

import hashlib
import inspect
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(
    PROJECT_ROOT
) not in sys.path:
    sys.path.insert(
        0,
        str(
            PROJECT_ROOT
        ),
    )


from backend.server.website_unified_content.certified_wuc_input import (
    load_article_validation_pass_contract_v1,
    load_transient_certified_wuc_source_v1,
)

from backend.server.website_unified_content.website_unified_content_engine_v1 import (
    build_transient_website_unified_content_v1,
)

from backend.server.universal_unified_content_document.uucd_engine_v1 import (
    build_transient_uucd_from_wuc_v1,
    validate_universal_handoff_envelope_v1,
)


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_PASS_COUNT = 2219

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "transient_wuc_exact_callable_contracts_v1.json"
)

PROTECTED_PATHS = {
    "production_body_store": (
        DATA_ROOT
        / "universal_article_body_store"
    ),

    "persistent_uucd_output": (
        DATA_ROOT
        / "universal_unified_content_documents"
    ),

    "persistent_wuc_output": (
        DATA_ROOT
        / "website_unified_content"
    ),

    "persistent_wuc_store": (
        DATA_ROOT
        / "website_unified_content_store"
    ),
}


def fingerprint(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    if not path.exists():
        digest.update(
            b"ABSENT"
        )
        return digest.hexdigest()

    for candidate in sorted(
        path.rglob("*"),
        key=lambda item: (
            item.relative_to(
                path
            ).as_posix()
        ),
    ):
        relative = candidate.relative_to(
            path
        ).as_posix()

        digest.update(
            relative.encode(
                "utf-8"
            )
        )

        digest.update(
            b"\x00"
        )

        if candidate.is_file():
            digest.update(
                candidate.read_bytes()
            )

        digest.update(
            b"\n"
        )

    return digest.hexdigest()


def safe_mapping_summary(
    value: Any,
) -> dict[str, Any]:
    if not isinstance(
        value,
        dict,
    ):
        return {
            "type":
                type(
                    value
                ).__name__,

            "is_mapping":
                False,
        }

    summary: dict[str, Any] = {
        "type":
            type(
                value
            ).__name__,

        "is_mapping":
            True,

        "keys":
            sorted(
                value.keys()
            ),
    }

    for key, child in value.items():
        if isinstance(
            child,
            str,
        ):
            summary[
                key
            ] = {
                "type":
                    "str",

                "length":
                    len(
                        child
                    ),

                "empty":
                    not bool(
                        child
                    ),
            }

        elif isinstance(
            child,
            dict,
        ):
            summary[
                key
            ] = {
                "type":
                    "dict",

                "keys":
                    sorted(
                        child.keys()
                    ),
            }

        elif isinstance(
            child,
            list,
        ):
            summary[
                key
            ] = {
                "type":
                    "list",

                "length":
                    len(
                        child
                    ),
            }

        else:
            summary[
                key
            ] = {
                "type":
                    type(
                        child
                    ).__name__,

                "value":
                    child
                    if isinstance(
                        child,
                        (
                            int,
                            float,
                            bool,
                            type(
                                None
                            ),
                        ),
                    )
                    else None,
            }

    return summary


def signature_report(
    function,
) -> dict[str, Any]:
    signature = inspect.signature(
        function
    )

    parameters = []

    for name, parameter in signature.parameters.items():
        parameters.append(
            {
                "name":
                    name,

                "kind":
                    str(
                        parameter.kind
                    ),

                "required":
                    (
                        parameter.default
                        is inspect.Parameter.empty
                    ),

                "default":
                    (
                        None
                        if parameter.default
                        is inspect.Parameter.empty
                        else repr(
                            parameter.default
                        )
                    ),

                "annotation":
                    (
                        None
                        if parameter.annotation
                        is inspect.Parameter.empty
                        else repr(
                            parameter.annotation
                        )
                    ),
            }
        )

    return {
        "name":
            function.__name__,

        "module":
            function.__module__,

        "signature":
            str(
                signature
            ),

        "parameters":
            parameters,

        "return_annotation":
            (
                None
                if signature.return_annotation
                is inspect.Signature.empty
                else repr(
                    signature.return_annotation
                )
            ),
    }


functions = [
    load_article_validation_pass_contract_v1,
    load_transient_certified_wuc_source_v1,
    build_transient_website_unified_content_v1,
    build_transient_uucd_from_wuc_v1,
    validate_universal_handoff_envelope_v1,
]

before = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_PATHS.items()
}

print()
print("=" * 116)
print(
    "TRANSIENT WUC → BODY PAYLOAD — EXACT CALLABLE CONTRACT SCAN"
)
print("=" * 116)
print()

signature_results = []

for function in functions:
    result = signature_report(
        function
    )

    signature_results.append(
        result
    )

    print(
        result[
            "name"
        ]
    )

    print(
        "  Module:    "
        + result[
            "module"
        ]
    )

    print(
        "  Signature: "
        + result[
            "signature"
        ]
    )

    print(
        "  Parameters:"
    )

    for parameter in result[
        "parameters"
    ]:
        print(
            "    - "
            + parameter[
                "name"
            ]
            + " | kind="
            + parameter[
                "kind"
            ]
            + " | required="
            + str(
                parameter[
                    "required"
                ]
            )
            + " | default="
            + str(
                parameter[
                    "default"
                ]
            )
        )

    print()


print(
    "FIRST DESCRIPTOR EXECUTION"
)
print(
    "-" * 116
)

contract = load_article_validation_pass_contract_v1(
    WORKSPACE_ID,
    expected_pass_count=EXPECTED_PASS_COUNT,
)

if isinstance(
    contract,
    dict,
):
    descriptors = (
        contract.get(
            "descriptors"
        )
        or contract.get(
            "records"
        )
        or contract.get(
            "articles"
        )
        or contract.get(
            "pass_records"
        )
    )

elif isinstance(
    contract,
    list,
):
    descriptors = contract

else:
    descriptors = None


if not isinstance(
    descriptors,
    list,
):
    print(
        "FAIL: PASS contract did not expose a descriptor list."
    )

    print(
        "Contract type: "
        + type(
            contract
        ).__name__
    )

    if isinstance(
        contract,
        dict,
    ):
        print(
            "Available keys: "
            + str(
                sorted(
                    contract.keys()
                )
            )
        )

    raise SystemExit(1)


if not descriptors:
    print(
        "FAIL: PASS descriptor list is empty."
    )

    raise SystemExit(1)


first_descriptor = descriptors[
    0
]

certified_source = (
    load_transient_certified_wuc_source_v1(
        first_descriptor
    )
)


print(
    "Descriptor count:       "
    + str(
        len(
            descriptors
        )
    )
)

print(
    "Descriptor type:        "
    + type(
        first_descriptor
    ).__name__
)

if isinstance(
    first_descriptor,
    dict,
):
    print(
        "Descriptor keys:        "
        + str(
            sorted(
                first_descriptor.keys()
            )
        )
    )

print(
    "Certified source type:  "
    + type(
        certified_source
    ).__name__
)

if isinstance(
    certified_source,
    dict,
):
    print(
        "Certified source keys: "
        + str(
            sorted(
                certified_source.keys()
            )
        )
    )


builder_signature = inspect.signature(
    build_transient_website_unified_content_v1
)

builder_parameters = list(
    builder_signature.parameters.values()
)

builder_execution = {
    "attempted":
        False,

    "success":
        False,

    "call_style":
        None,

    "error_type":
        None,

    "error":
        None,

    "wuc_summary":
        None,
}


if len(
    builder_parameters
) == 1:
    parameter = builder_parameters[
        0
    ]

    builder_execution[
        "attempted"
    ] = True

    try:
        if parameter.kind in {
            inspect.Parameter.KEYWORD_ONLY,
        }:
            builder_execution[
                "call_style"
            ] = (
                "keyword:"
                + parameter.name
            )

            wuc = (
                build_transient_website_unified_content_v1(
                    **{
                        parameter.name:
                            certified_source
                    }
                )
            )

        else:
            builder_execution[
                "call_style"
            ] = "positional"

            wuc = (
                build_transient_website_unified_content_v1(
                    certified_source
                )
            )

        builder_execution[
            "success"
        ] = True

        builder_execution[
            "wuc_summary"
        ] = safe_mapping_summary(
            wuc
        )

    except Exception as exc:
        builder_execution[
            "error_type"
        ] = type(
            exc
        ).__name__

        builder_execution[
            "error"
        ] = str(
            exc
        )

else:
    print()
    print(
        "WUC builder has "
        + str(
            len(
                builder_parameters
            )
        )
        + " parameters; automatic execution was skipped."
    )


print()
print(
    "WUC BUILDER EXECUTION"
)
print(
    "  Attempted:  "
    + str(
        builder_execution[
            "attempted"
        ]
    )
)

print(
    "  Call style: "
    + str(
        builder_execution[
            "call_style"
        ]
    )
)

print(
    "  Success:    "
    + str(
        builder_execution[
            "success"
        ]
    )
)

if builder_execution[
    "error"
]:
    print(
        "  Error type: "
        + str(
            builder_execution[
                "error_type"
            ]
        )
    )

    print(
        "  Error:      "
        + str(
            builder_execution[
                "error"
            ]
        )
    )


if builder_execution[
    "success"
]:
    print(
        "  WUC type:   "
        + str(
            builder_execution[
                "wuc_summary"
            ][
                "type"
            ]
        )
    )

    print(
        "  WUC keys:   "
        + str(
            builder_execution[
                "wuc_summary"
            ].get(
                "keys"
            )
        )
    )


after = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_PATHS.items()
}

unchanged = {
    name:
        before[
            name
        ]
        == after[
            name
        ]

    for name
    in PROTECTED_PATHS
}


report = {
    "schema_version":
        "transient_wuc_exact_callable_contracts_v1",

    "workspace_id":
        WORKSPACE_ID,

    "scan_mode":
        "READ_ONLY",

    "function_signatures":
        signature_results,

    "descriptor_count":
        len(
            descriptors
        ),

    "first_descriptor_summary":
        safe_mapping_summary(
            first_descriptor
        ),

    "first_certified_source_summary":
        safe_mapping_summary(
            certified_source
        ),

    "wuc_builder_execution":
        builder_execution,

    "production_outputs_unchanged":
        unchanged,

    "wuc_packages_persisted":
        0,

    "body_payloads_persisted":
        0,

    "uucd_records_persisted":
        0,

    "body_store_files_written":
        0,

    "runtime_jobs_created":
        0,
}


REPORT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT_PATH.write_text(
    json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


print()
print(
    "PRODUCTION OUTPUTS"
)

for name, passed in unchanged.items():
    print(
        "  "
        + f"{name:<34}"
        + (
            "UNCHANGED"
            if passed
            else "CHANGED"
        )
    )

print()
print(
    "WUC packages persisted:        0"
)

print(
    "Body Payloads persisted:       0"
)

print(
    "UUCD records persisted:        0"
)

print(
    "Body Store files written:      0"
)

print(
    "Runtime jobs created:          0"
)

print()
print(
    "Scan report: "
    + str(
        REPORT_PATH
    )
)

print()

if not all(
    unchanged.values()
):
    print(
        "EXACT CALLABLE CONTRACT SCAN: FAIL"
    )

    print(
        "A protected production output changed."
    )

    raise SystemExit(1)

print(
    "EXACT CALLABLE CONTRACT SCAN: PASS"
)

print(
    "The exact signatures and first certified-source shape were "
    "identified without persistent pipeline output."
)

print("=" * 116)
