from __future__ import annotations

import hashlib
import sys
import time
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
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
    compute_canonical_content_hash_v1,
    validate_universal_handoff_envelope_v1,
)


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_PASS_COUNT = 2219
MAX_FAILURE_DETAILS = 25

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

PROTECTED_PATHS = {
    "Body Store": (
        DATA_ROOT
        / "universal_article_body_store"
    ),

    "UUCD output": (
        DATA_ROOT
        / "universal_unified_content_documents"
    ),

    "WUC output": (
        DATA_ROOT
        / "website_unified_content"
    ),

    "WUC Store": (
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

    for item in sorted(
        path.rglob("*"),
        key=lambda value: (
            value.relative_to(
                path
            ).as_posix()
        ),
    ):
        digest.update(
            item.relative_to(
                path
            ).as_posix().encode(
                "utf-8"
            )
        )

        digest.update(
            b"\x00"
        )

        if item.is_file():
            digest.update(
                item.read_bytes()
            )

        digest.update(
            b"\n"
        )

    return digest.hexdigest()


def descriptor_identity(
    descriptor,
    index: int,
) -> str:
    if isinstance(
        descriptor,
        dict,
    ):
        for field in (
            "source_record_id",
            "document_id",
            "article_id",
            "record_id",
            "title",
        ):
            value = descriptor.get(
                field
            )

            if value:
                return str(
                    value
                )

    return (
        "descriptor_"
        + str(
            index
        )
    )


before = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_PATHS.items()
}


print()
print("=" * 112)
print(
    "ALL 2,219 ARTICLES — TRANSIENT BODY PAYLOAD READINESS AUDIT"
)
print("=" * 112)
print()

started = time.perf_counter()

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
                    contract
                )
            )
        )

    raise SystemExit(1)


counts = Counter()

counts[
    "descriptors"
] = len(
    descriptors
)

failures = []
word_counts = []
character_counts = []

binding_fields = (
    "document_id",
    "workspace_id",
    "source_type",
    "content_hash",
    "body_length",
    "body_word_count",
    "body_ref",
)


print(
    "PASS descriptors loaded: "
    + str(
        len(
            descriptors
        )
    )
)

print()


for index, descriptor in enumerate(
    descriptors,
    start=1,
):
    identity = descriptor_identity(
        descriptor,
        index,
    )

    stage = "certified_source"

    try:
        source = (
            load_transient_certified_wuc_source_v1(
                descriptor
            )
        )

        counts[
            "certified_sources"
        ] += 1

        stage = "wuc"

        wuc = (
            build_transient_website_unified_content_v1(
                certified_source=source
            )
        )

        counts[
            "wuc_packages"
        ] += 1

        stage = "envelope"

        envelope = (
            build_transient_uucd_from_wuc_v1(
                wuc
            )
        )

        counts[
            "envelopes"
        ] += 1

        stage = "envelope_validation"

        validate_universal_handoff_envelope_v1(
            envelope
        )

        counts[
            "validated_envelopes"
        ] += 1

        record = envelope.get(
            "uucd_record"
        )

        payload = envelope.get(
            "body_payload"
        )

        binding = envelope.get(
            "binding"
        )

        if not isinstance(
            record,
            dict,
        ):
            raise RuntimeError(
                "Missing uucd_record."
            )

        if not isinstance(
            payload,
            dict,
        ):
            raise RuntimeError(
                "Missing body_payload."
            )

        if not isinstance(
            binding,
            dict,
        ):
            raise RuntimeError(
                "Missing binding."
            )

        counts[
            "body_payloads"
        ] += 1

        body = payload.get(
            "content_body"
        )

        if not isinstance(
            body,
            str,
        ):
            raise RuntimeError(
                "content_body is not a string."
            )

        if not body:
            raise RuntimeError(
                "content_body is empty."
            )

        counts[
            "complete_bodies"
        ] += 1

        calculated_hash = (
            compute_canonical_content_hash_v1(
                body
            )
        )

        if (
            payload.get(
                "content_hash"
            )
            != calculated_hash
        ):
            raise RuntimeError(
                "content_hash mismatch."
            )

        if (
            payload.get(
                "body_length"
            )
            != len(
                body
            )
        ):
            raise RuntimeError(
                "body_length mismatch."
            )

        calculated_words = len(
            body.split()
        )

        if (
            payload.get(
                "body_word_count"
            )
            != calculated_words
        ):
            raise RuntimeError(
                "body_word_count mismatch."
            )

        if (
            wuc.get(
                "content_body"
            )
            != body
        ):
            raise RuntimeError(
                "WUC body differs from Body Payload."
            )

        if "content_body" in record:
            raise RuntimeError(
                "UUCD Record contains content_body."
            )

        if not all(
            record.get(
                field
            )
            == payload.get(
                field
            )
            == binding.get(
                field
            )
            for field in binding_fields
        ):
            raise RuntimeError(
                "Binding fields do not match."
            )

        if (
            envelope.get(
                "envelope_status"
            )
            != "READY_FOR_BODY_STORE"
        ):
            raise RuntimeError(
                "Envelope is not READY_FOR_BODY_STORE."
            )

        if (
            record.get(
                "body_status"
            )
            != "PENDING_BODY_STORE_WRITE"
        ):
            raise RuntimeError(
                "Invalid UUCD body_status."
            )

        if (
            record.get(
                "handoff",
                {},
            ).get(
                "eligible_for_body_store"
            )
            is not True
        ):
            raise RuntimeError(
                "Record is not eligible for Body Store."
            )

        counts[
            "ready"
        ] += 1

        word_counts.append(
            calculated_words
        )

        character_counts.append(
            len(
                body
            )
        )

    except Exception as exc:
        counts[
            "failures"
        ] += 1

        if len(
            failures
        ) < MAX_FAILURE_DETAILS:
            failures.append(
                {
                    "index":
                        index,

                    "identity":
                        identity,

                    "stage":
                        stage,

                    "error_type":
                        type(
                            exc
                        ).__name__,

                    "error":
                        str(
                            exc
                        ),
                }
            )

    if (
        index % 100 == 0
        or index
        == len(
            descriptors
        )
    ):
        elapsed = (
            time.perf_counter()
            - started
        )

        print(
            "Processed "
            + str(
                index
            )
            + "/"
            + str(
                len(
                    descriptors
                )
            )
            + " | Ready: "
            + str(
                counts[
                    "ready"
                ]
            )
            + " | Failures: "
            + str(
                counts[
                    "failures"
                ]
            )
            + " | Elapsed: "
            + f"{elapsed:.1f}s"
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


checks = {
    "descriptor_count":
        counts[
            "descriptors"
        ]
        == EXPECTED_PASS_COUNT,

    "all_certified_sources":
        counts[
            "certified_sources"
        ]
        == EXPECTED_PASS_COUNT,

    "all_wuc_packages":
        counts[
            "wuc_packages"
        ]
        == EXPECTED_PASS_COUNT,

    "all_envelopes":
        counts[
            "envelopes"
        ]
        == EXPECTED_PASS_COUNT,

    "all_validated_envelopes":
        counts[
            "validated_envelopes"
        ]
        == EXPECTED_PASS_COUNT,

    "all_body_payloads":
        counts[
            "body_payloads"
        ]
        == EXPECTED_PASS_COUNT,

    "all_complete_bodies":
        counts[
            "complete_bodies"
        ]
        == EXPECTED_PASS_COUNT,

    "all_ready":
        counts[
            "ready"
        ]
        == EXPECTED_PASS_COUNT,

    "zero_failures":
        counts[
            "failures"
        ]
        == 0,

    "production_outputs_unchanged":
        all(
            unchanged.values()
        ),
}


print()
print("=" * 112)
print(
    "TRANSIENT BODY PAYLOAD READINESS RESULTS"
)
print("=" * 112)
print()

print(
    "PASS descriptors:                  "
    + str(
        counts[
            "descriptors"
        ]
    )
)

print(
    "Certified WUC sources loaded:       "
    + str(
        counts[
            "certified_sources"
        ]
    )
)

print(
    "Transient WUC packages built:       "
    + str(
        counts[
            "wuc_packages"
        ]
    )
)

print(
    "Universal Handoff Envelopes built:  "
    + str(
        counts[
            "envelopes"
        ]
    )
)

print(
    "Validated envelopes:                "
    + str(
        counts[
            "validated_envelopes"
        ]
    )
)

print(
    "Body Payloads present:              "
    + str(
        counts[
            "body_payloads"
        ]
    )
)

print(
    "Complete content_body values:       "
    + str(
        counts[
            "complete_bodies"
        ]
    )
)

print(
    "Ready for Body Store Writer:        "
    + str(
        counts[
            "ready"
        ]
    )
)

print(
    "Pipeline failures:                  "
    + str(
        counts[
            "failures"
        ]
    )
)

if word_counts:
    print()
    print(
        "Smallest article, words:           "
        + str(
            min(
                word_counts
            )
        )
    )

    print(
        "Largest article, words:            "
        + str(
            max(
                word_counts
            )
        )
    )

    print(
        "Average article, words:            "
        + str(
            sum(
                word_counts
            )
            // len(
                word_counts
            )
        )
    )

    print(
        "Total words ready:                 "
        + str(
            sum(
                word_counts
            )
        )
    )

    print(
        "Total characters ready:            "
        + str(
            sum(
                character_counts
            )
        )
    )


print()
print(
    "FINAL CHECKS"
)

for name, passed in checks.items():
    print(
        "  "
        + f"{name:<44}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )


print()
print(
    "PRODUCTION OUTPUTS"
)

for name, passed in unchanged.items():
    print(
        "  "
        + f"{name:<30}"
        + (
            "UNCHANGED"
            if passed
            else "CHANGED"
        )
    )


print()
print(
    "FAILURE DETAILS"
)

if failures:
    for failure in failures:
        print()
        print(
            "  Index:      "
            + str(
                failure[
                    "index"
                ]
            )
        )

        print(
            "  Identity:   "
            + failure[
                "identity"
            ]
        )

        print(
            "  Stage:      "
            + failure[
                "stage"
            ]
        )

        print(
            "  Error type: "
            + failure[
                "error_type"
            ]
        )

        print(
            "  Error:      "
            + failure[
                "error"
            ]
        )

else:
    print(
        "  None"
    )


print()
print(
    "Body Store files written:          0"
)

print(
    "Persistent UUCD records written:   0"
)

print(
    "Persistent WUC packages written:   0"
)

print(
    "Runtime jobs created:              0"
)

print()

if all(
    checks.values()
):
    print(
        "ALL 2,219 BODY PAYLOADS: READY"
    )

    print(
        "Every PASS article produced one complete, validated "
        "Universal Body Payload."
    )

else:
    print(
        "ALL 2,219 BODY PAYLOADS: NOT READY"
    )

    print(
        "Do not populate the production Body Store yet."
    )

    raise SystemExit(1)

print("=" * 112)

