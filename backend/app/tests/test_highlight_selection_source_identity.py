import hashlib

import pytest

from backend.server.stores.candidate_window_guard import (
    candidate_window_guard,
)
from backend.server.stores.phrase_strength_scorer import (
    score_phrase_strength,
)
from backend.server.stores.highlight_selection_engine import (
    _selection_source_hash_status,
    select_highlight_candidates,
)


ARTICLE = (
    "Kidney disease requires monitoring. "
    "Kidney disease can progress."
)

ARTICLE_HASH = hashlib.sha256(
    ARTICLE.encode("utf-8")
).hexdigest()


def candidate(**metadata):
    return {
        "phrase": "Kidney disease",
        "source_type": "body",
        "workspace_id": "ws_source_identity",
        "doc_id": "source-identity-test",
        "score": 99.0,
        "extractor_score": 99.0,
        **metadata,
    }


def select(items):
    return select_highlight_candidates(
        workspace_id="ws_source_identity",
        doc_id="source-identity-test",
        article_text=ARTICLE,
        phrase_candidates=items,
        resolved_targets=None,
        vertical="health",
    )


def selected_records(value):
    if isinstance(value, dict):
        if "selection_article_text_sha256" in value:
            yield value

        for child in value.values():
            yield from selected_records(child)

    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from selected_records(child)


def test_guard_and_scorer_preserve_source_metadata():
    metadata = {
        "source_version": "revision-7",
        "source_hash": ARTICLE_HASH,
        "source_hash_basis": "article_text_utf8_sha256",
        "content_hash": "a" * 64,
        "asset_version_id": "asset-7",
        "snapshot_id": "snapshot-7",
    }

    incoming = candidate(**metadata)

    guarded = candidate_window_guard(
        incoming,
        source_type="body",
        workspace_id="ws_source_identity",
        document_id="source-identity-test",
        vertical="health",
    )

    scored = score_phrase_strength(
        guarded,
        source_type="body",
        workspace_id="ws_source_identity",
        document_id="source-identity-test",
        vertical="health",
    )

    for record in (incoming, guarded, scored):
        for key, value in metadata.items():
            assert record[key] == value


def test_source_hash_status_contract():
    assert _selection_source_hash_status(
        {}, ARTICLE_HASH
    ) == "not_provided"

    assert _selection_source_hash_status(
        {
            "source_hash": ARTICLE_HASH.upper(),
            "source_hash_basis": "article_text_utf8_sha256",
        },
        ARTICLE_HASH,
    ) == "verified_match"

    assert _selection_source_hash_status(
        {
            "source_hash": "0" * 64,
            "source_hash_basis": "article_text_utf8_sha256",
        },
        ARTICLE_HASH,
    ) == "stale_source_mismatch"

    assert _selection_source_hash_status(
        {
            "source_hash": "invalid",
            "source_hash_basis": "article_text_utf8_sha256",
        },
        ARTICLE_HASH,
    ) == "invalid_declared_hash"


def test_stale_source_hash_is_rejected():
    incoming = candidate(
        source_hash="0" * 64,
        source_hash_basis="article_text_utf8_sha256",
    )

    with pytest.raises(
        ValueError,
        match="source hash mismatch",
    ):
        select([incoming])


def test_invalid_declared_hash_is_rejected():
    incoming = candidate(
        source_hash="not-a-valid-sha256",
        source_hash_basis="article_text_utf8_sha256",
    )

    with pytest.raises(
        ValueError,
        match="invalid declared source hash",
    ):
        select([incoming])


def test_unknown_hash_basis_is_not_falsely_rejected():
    incoming = candidate(
        source_hash="0" * 64,
        source_hash_basis="canonical_uucd_content_body",
    )

    result = select([incoming])

    assert isinstance(result, dict)


def test_canonical_content_hash_is_not_falsely_compared():
    incoming = candidate(
        content_hash="f" * 64,
        source_version="revision-9",
        asset_version_id="asset-9",
    )

    result = select([incoming])

    assert isinstance(result, dict)


def test_selected_candidate_has_source_identity():
    incoming = candidate(
        source_version="revision-7",
        source_hash=ARTICLE_HASH,
        source_hash_basis="article_text_utf8_sha256",
        content_hash="a" * 64,
        asset_version_id="asset-7",
        snapshot_id="snapshot-7",
    )

    records = list(selected_records(select([incoming])))

    assert records, "Selector produced no selected candidate"

    record = records[0]

    assert record["selection_article_text_sha256"] == ARTICLE_HASH
    assert (
        record["selection_article_text_hash_basis"]
        == "article_text_utf8_sha256"
    )
    assert (
        record["selection_source_hash_status"]
        == "verified_match"
    )
    assert (
        record["selection_source_version_status"]
        == "provided_unverified"
    )

    for key in (
        "source_version",
        "source_hash",
        "content_hash",
        "asset_version_id",
        "snapshot_id",
    ):
        assert record[key] == incoming[key]
