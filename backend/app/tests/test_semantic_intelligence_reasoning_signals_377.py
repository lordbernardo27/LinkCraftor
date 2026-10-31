from copy import deepcopy

from backend.server.engine.semantic_intelligence_reasoning_signals_377 import (
    associate_reasoning_signals,
)


def candidate():
    sentence = "Diabetes treatment involves clinical monitoring."
    phrase = "Diabetes treatment"
    return {
        "phrase": phrase,
        "selection_occurrence_id": "occ_1",
        "selection_source_span_status": "verified",
        "selection_sentence_context_status":
            "derived_from_verified_span",
        "selection_source_span": {
            "start": 100,
            "end": 100 + len(phrase),
            "text": phrase,
            "coordinate_space": "original_article",
        },
        "selection_sentence_context": {
            "start": 100,
            "end": 100 + len(sentence),
            "text": sentence,
            "coordinate_space": "original_article",
        },
    }


def retrieval():
    return {
        "status": "document_context_found",
        "workspace_id": "ws_whattoexpect_com",
        "phrase": "Diabetes treatment",
        "source": "workspace_cross_document_reasoning",
        "matched_documents": [
            {
                "document_id": "doc1",
                "match_type": "exact_document_phrase",
                "title": "Example",
            }
        ],
        "document_relationships": [
            {
                "left_document_id": "doc1",
                "right_document_id": "doc2",
                "score": 0.72,
            }
        ],
        "reasoning_observations": [
            {
                "observation": "phrase_present_in_workspace_documents",
                "document_count": 1,
                "certified": False,
            }
        ],
        "phrase_level_semantic_proof": False,
        "linking_decision_performed": False,
        "certified": False,
    }


def test_document_context_preserved_without_semantic_proof():
    result = associate_reasoning_signals(candidate(), retrieval())
    assert result["status"] == "document_context_found"
    assert result["phrase_context_verified"] is True
    assert result["phrase_level_semantic_proof"] is False
    assert result["confidence"] is None
    assert result["document_relationships"][0]["score"] == 0.72
    assert result["certified"] is False


def test_candidate_and_retrieval_unmodified():
    c, r = candidate(), retrieval()
    before_c, before_r = deepcopy(c), deepcopy(r)
    associate_reasoning_signals(c, r)
    assert c == before_c
    assert r == before_r


def test_no_evidence_abstains():
    r = retrieval()
    r.update({
        "status": "no_evidence",
        "matched_documents": [],
        "document_relationships": [],
        "reasoning_observations": [],
    })
    result = associate_reasoning_signals(candidate(), r)
    assert result["status"] == "no_evidence"
    assert result["phrase_level_semantic_proof"] is False


def test_phrase_mismatch_is_invalid():
    r = retrieval()
    r["phrase"] = "Unrelated phrase"
    assert associate_reasoning_signals(candidate(), r)["status"] == "invalid"


def test_unverified_occurrence_abstains():
    c = candidate()
    c["selection_source_span_status"] = "unverified"
    result = associate_reasoning_signals(c, retrieval())
    assert result["status"] == "unavailable"


def test_wrong_coordinates_abstain():
    c = candidate()
    c["selection_source_span"]["start"] += 1
    result = associate_reasoning_signals(c, retrieval())
    assert result["status"] == "unavailable"


def test_unrelated_document_relationship_rejected():
    r = retrieval()
    r["document_relationships"][0]["left_document_id"] = "unknown1"
    r["document_relationships"][0]["right_document_id"] = "unknown2"
    assert associate_reasoning_signals(candidate(), r)["status"] == "invalid"


def test_missing_retrieval_distinguished():
    result = associate_reasoning_signals(candidate(), None)
    assert result["status"] == "source_verified_retrieval_unavailable"


def test_retrieval_cannot_claim_certification():
    r = retrieval()
    r["certified"] = True
    assert associate_reasoning_signals(candidate(), r)["status"] == "invalid"


def test_no_linking_authority():
    result = associate_reasoning_signals(candidate(), retrieval())
    assert result["automatic_linking_authorized"] is False
    assert result["linking_decision_performed"] is False



def test_377_expected_workspace_matches():
    c, r = candidate(), retrieval()
    c["workspace_id"] = "ws_whattoexpect_com"
    result = associate_reasoning_signals(
        c, r, expected_workspace_id="ws_whattoexpect_com"
    )
    assert result["status"] == "document_context_found"


def test_377_cross_workspace_retrieval_rejected():
    c, r = candidate(), retrieval()
    r["workspace_id"] = "ws_other_com"
    result = associate_reasoning_signals(
        c, r, expected_workspace_id="ws_whattoexpect_com"
    )
    assert result["status"] == "invalid"


def test_377_candidate_workspace_disagreement_rejected():
    c, r = candidate(), retrieval()
    c["workspace_id"] = "ws_other_com"
    result = associate_reasoning_signals(
        c, r, expected_workspace_id="ws_whattoexpect_com"
    )
    assert result["status"] == "invalid"


def test_377_invalid_article_hash_rejected():
    c = candidate()
    c["selection_article_text_sha256"] = "invalid_hash"
    result = associate_reasoning_signals(
        c, retrieval(),
        expected_workspace_id="ws_whattoexpect_com",
    )
    assert result["status"] == "invalid"


def test_377_valid_article_hash_preserved():
    c = candidate()
    c["selection_article_text_sha256"] = "a" * 64
    result = associate_reasoning_signals(
        c, retrieval(),
        expected_workspace_id="ws_whattoexpect_com",
    )
    assert result["status"] == "document_context_found"
    assert result["source_occurrence"]["article_sha256"] == "a" * 64


def test_377_invalid_occurrence_identity_rejected():
    c = candidate()
    c["selection_occurrence_id"] = ""
    result = associate_reasoning_signals(
        c, retrieval(),
        expected_workspace_id="ws_whattoexpect_com",
    )
    assert result["status"] == "invalid"


def test_377_wrong_retrieved_phrase_rejected_with_workspace():
    r = retrieval()
    r["phrase"] = "different treatment"
    result = associate_reasoning_signals(
        candidate(),
        r,
        expected_workspace_id="ws_whattoexpect_com",
    )
    assert result["status"] == "invalid"



def test_377_document_score_preserved_without_phrase_confidence():
    result = associate_reasoning_signals(candidate(), retrieval())

    assert result["status"] == "document_context_found"
    assert result["confidence"] is None
    assert result["phrase_level_semantic_proof"] is False

    records = result["document_relationship_confidence"]
    assert len(records) == 1
    assert records[0]["source_score"] == 0.72
    assert records[0]["scope"] == "document_relationship_only"
    assert records[0]["phrase_level_confidence"] is None
    assert records[0]["confidence_certified"] is False


def test_377_missing_score_not_fabricated():
    r = retrieval()
    del r["document_relationships"][0]["score"]

    result = associate_reasoning_signals(candidate(), r)

    assert result["status"] == "document_context_found"
    record = result["document_relationship_confidence"][0]
    assert record["source_score_present"] is False
    assert record["source_score"] is None
    assert record["source_score_status"] == "not_provided"


def test_377_zero_and_one_scores_are_preserved():
    for score in (0, 1):
        r = retrieval()
        r["document_relationships"][0]["score"] = score

        result = associate_reasoning_signals(candidate(), r)

        assert result["status"] == "document_context_found"
        assert result["document_relationship_confidence"][0][
            "source_score"
        ] == score
        assert result["confidence"] is None


def test_377_invalid_score_values_rejected():
    for score in (
        -0.1, 1.1, float("nan"), float("inf"),
        float("-inf"), True, False, "0.72", None,
    ):
        r = retrieval()
        r["document_relationships"][0]["score"] = score

        result = associate_reasoning_signals(candidate(), r)

        assert result["status"] == "invalid"
        assert result["reason"] == "invalid_document_relationship_score"


def test_377_source_scores_are_not_changed():
    r = retrieval()
    before = deepcopy(r)

    result = associate_reasoning_signals(candidate(), r)

    assert result["status"] == "document_context_found"
    assert r == before
    assert result["document_relationships"] == r[
        "document_relationships"
    ]


def test_377_multiple_relationship_scores_remain_distinct():
    r = retrieval()
    r["document_relationships"].append({
        "left_document_id": "doc1",
        "right_document_id": "doc3",
        "score": 0.41,
    })

    result = associate_reasoning_signals(candidate(), r)

    assert result["status"] == "document_context_found"
    records = result["document_relationship_confidence"]

    assert len(records) == 2
    assert records[0]["source_score"] == 0.72
    assert records[1]["source_score"] == 0.41
    assert result["confidence"] is None



def test_377_relationship_provenance_is_traceable():
    result = associate_reasoning_signals(
        candidate(), retrieval(),
        expected_workspace_id="ws_whattoexpect_com",
    )
    assert result["status"] == "document_context_found"
    records = result["document_relationship_provenance"]
    assert len(records) == 1

    record = records[0]
    assert record["workspace_id"] == "ws_whattoexpect_com"
    assert record["selected_phrase"] == "Diabetes treatment"
    assert record["selected_occurrence_id"] == "occ_1"
    assert record["relationship_index"] == 0
    assert record["left_document_id"] == "doc1"
    assert record["right_document_id"] == "doc2"
    assert record["matched_left_document"] is True
    assert record["matched_right_document"] is False
    assert record["independent_evidence_verified"] is False
    assert record["phrase_semantic_proof"] is False


def test_377_provenance_preserves_original_coordinates():
    c = candidate()
    result = associate_reasoning_signals(c, retrieval())

    record = result["document_relationship_provenance"][0]
    assert record["source_span"] == {"start": 100, "end": 118}
    assert record["sentence_span"] == {
        "start": 100,
        "end": 100 + len(
            "Diabetes treatment involves clinical monitoring."
        ),
    }


def test_377_source_evidence_id_not_invented():
    result = associate_reasoning_signals(candidate(), retrieval())
    record = result["document_relationship_provenance"][0]
    assert record["source_evidence_id"] is None
    assert result["confidence"] is None


def test_377_existing_source_evidence_id_preserved():
    r = retrieval()
    r["document_relationships"][0]["evidence_id"] = "source-evidence-17"

    result = associate_reasoning_signals(candidate(), r)
    assert result["status"] == "document_context_found"
    assert result["document_relationship_provenance"][0][
        "source_evidence_id"
    ] == "source-evidence-17"


def test_377_invalid_source_evidence_id_rejected():
    for evidence_id in ("", " ", None, 123):
        r = retrieval()
        r["document_relationships"][0]["evidence_id"] = evidence_id
        result = associate_reasoning_signals(candidate(), r)
        assert result["status"] == "invalid"
        assert result["reason"] == "invalid_source_evidence_id"


def test_377_multiple_relationship_provenance_keeps_order():
    r = retrieval()
    r["document_relationships"].append({
        "left_document_id": "doc3",
        "right_document_id": "doc1",
        "score": 0.41,
    })

    original = deepcopy(r)
    result = associate_reasoning_signals(candidate(), r)

    assert result["status"] == "document_context_found"
    records = result["document_relationship_provenance"]
    assert len(records) == 2
    assert [v["relationship_index"] for v in records] == [0, 1]
    assert [v["left_document_id"] for v in records] == [
        "doc1", "doc3"
    ]
    assert result["document_relationship_confidence"][1][
        "source_score"
    ] == 0.41
    assert r == original
