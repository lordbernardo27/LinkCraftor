from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.server.common.text_statistics import (
    count_words,
    count_characters,
    count_utf8_bytes,
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

PROTECTED = [
    DATA_ROOT / "universal_article_body_store",
    DATA_ROOT / "website_unified_content",
    DATA_ROOT / "website_unified_content_store",
    DATA_ROOT / "universal_unified_content_documents",
]


def fingerprint(path: Path) -> str:
    h = hashlib.sha256()

    if not path.exists():
        h.update(b"ABSENT")
        return h.hexdigest()

    for item in sorted(
        path.rglob("*"),
        key=lambda p: p.relative_to(path).as_posix(),
    ):
        h.update(
            item.relative_to(path).as_posix().encode("utf-8")
        )

        if item.is_file():
            h.update(item.read_bytes())

    return h.hexdigest()


before = {
    str(path): fingerprint(path)
    for path in PROTECTED
}

contract = load_article_validation_pass_contract_v1(
    WORKSPACE_ID,
    expected_pass_count=EXPECTED_PASS_COUNT,
)

descriptors = (
    contract.get("descriptors")
    or contract.get("records")
    or contract.get("articles")
    or contract.get("pass_records")
)

if not isinstance(descriptors, list):
    raise RuntimeError("PASS descriptor list not found.")

stats = {
    "certified_sources": 0,
    "wuc_packages": 0,
    "envelopes": 0,
    "validated": 0,
    "body_payloads": 0,
    "body_present": 0,
    "hash_present": 0,
    "length_ok": 0,
    "char_ok": 0,
    "utf8_ok": 0,
    "word_ok": 0,
    "failures": 0,
}

for descriptor in descriptors:

    try:

        source = load_transient_certified_wuc_source_v1(
            descriptor
        )

        stats["certified_sources"] += 1

        wuc = build_transient_website_unified_content_v1(
            certified_source=source
        )

        stats["wuc_packages"] += 1

        envelope = build_transient_uucd_from_wuc_v1(
            wuc
        )

        stats["envelopes"] += 1

        validate_universal_handoff_envelope_v1(
            envelope
        )

        stats["validated"] += 1

        body = envelope["body_payload"]

        stats["body_payloads"] += 1

        content = body["content_body"]

        if content:
            stats["body_present"] += 1

        if body.get("content_hash"):
            stats["hash_present"] += 1

        if (
            body["body_length"]
            == len(content)
        ):
            stats["length_ok"] += 1

        if (
            count_characters(content)
            == body["body_length"]
        ):
            stats["char_ok"] += 1

        if (
            count_utf8_bytes(content)
            == len(
                content.encode("utf-8")
            )
        ):
            stats["utf8_ok"] += 1

        if (
            count_words(content)
            == body["body_word_count"]
        ):
            stats["word_ok"] += 1

    except Exception:
        stats["failures"] += 1

after = {
    str(path): fingerprint(path)
    for path in PROTECTED
}

print()
print("=" * 100)
print("COMPLETE BODY PIPELINE READINESS")
print("=" * 100)
print()

for k, v in stats.items():
    print(f"{k:<32} {v}")

print()

print("PROTECTED OUTPUTS")

for path in PROTECTED:

    state = (
        "UNCHANGED"
        if before[str(path)] == after[str(path)]
        else "CHANGED"
    )

    print(
        f"{path.name:<35}{state}"
    )

print()

if (
    stats["failures"] == 0
    and stats["certified_sources"] == EXPECTED_PASS_COUNT
    and stats["word_ok"] == EXPECTED_PASS_COUNT
):
    print("FINAL STATUS : READY")
else:
    print("FINAL STATUS : NOT READY")

print("=" * 100)
