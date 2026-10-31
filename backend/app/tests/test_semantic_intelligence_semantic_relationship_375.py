from backend.server.engine.semantic_intelligence_semantic_relationship_enrichment import (
    enrich_explicit_semantic_relationship,
)


def candidate(sentence, phrase, verified=True):
    start = sentence.index(phrase)
    return {
        "phrase": phrase,
        "selection_source_span_status": (
            "verified" if verified else "unverified"
        ),
        "selection_sentence_context_status": (
            "derived_from_verified_span" if verified else "unverified"
        ),
        "selection_source_span": {
            "start": start,
            "end": start + len(phrase),
            "text": phrase,
            "coordinate_space": "original_article",
        },
        "selection_sentence_context": {
            "start": 0,
            "end": len(sentence),
            "text": sentence,
            "coordinate_space": "original_article",
        },
    }


def test_explicit_synonym():
    result = enrich_explicit_semantic_relationship(
        candidate(
            "High blood pressure is also known as hypertension.",
            "High blood pressure",
        )
    )
    assert result["status"] == "supported_unverified"
    assert result["relationships"][0]["relation_type"] == "synonym_of"
    assert result["certified"] is False


def test_explicit_type_of():
    result = enrich_explicit_semantic_relationship(
        candidate(
            "Insulin therapy is a type of diabetes treatment.",
            "Insulin therapy",
        )
    )
    assert result["relationships"][0]["relation_type"] == "narrower_than"


def test_target_endpoint():
    result = enrich_explicit_semantic_relationship(
        candidate(
            "Insulin therapy is a type of diabetes treatment.",
            "diabetes treatment",
        )
    )
    assert result["relationships"][0]["selected_endpoint"] == "target"


def test_cooccurrence_does_not_prove_relationship():
    result = enrich_explicit_semantic_relationship(
        candidate(
            "Diabetes treatment and insulin therapy were discussed.",
            "Diabetes treatment",
        )
    )
    assert result["status"] == "no_evidence"
    assert result["relationships"] == []


def test_unverified_source_abstains():
    result = enrich_explicit_semantic_relationship(
        candidate(
            "Insulin therapy is a type of diabetes treatment.",
            "Insulin therapy",
            verified=False,
        )
    )
    assert result["status"] == "unavailable"


def test_wrong_coordinates_abstain():
    item = candidate(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    item["selection_source_span"]["start"] += 1
    result = enrich_explicit_semantic_relationship(item)
    assert result["status"] == "unavailable"


def test_no_linking_or_graph_authorization():
    result = enrich_explicit_semantic_relationship(
        candidate(
            "High blood pressure is also known as hypertension.",
            "High blood pressure",
        )
    )
    assert result["automatic_linking_authorized"] is False
    assert result["graph_mutation_performed"] is False
    assert result["linking_decision_performed"] is False


def test_unsupported_causal_statement_abstains():
    result = enrich_explicit_semantic_relationship(
        candidate(
            "Diabetes can cause nerve damage.",
            "Diabetes",
        )
    )
    assert result["status"] == "no_evidence"



def test_negated_type_of_no_affirmative_relationship():
    item = candidate(
        "Insulin therapy is not a type of diabetes treatment.",
        "Insulin therapy",
    )
    result = enrich_explicit_semantic_relationship(item)
    assert result["relationships"] == []
    assert result["status"] == "no_evidence"


def test_rejected_type_of_claim_abstains():
    result = enrich_explicit_semantic_relationship(
        candidate(
            "It is incorrect to say insulin therapy is a type of diabetes treatment.",
            "insulin therapy",
        )
    )
    assert result["relationships"] == []
    assert result["certified"] is False


def test_disputed_claim_does_not_produce_relation():
    result = enrich_explicit_semantic_relationship(
        candidate(
            "Researchers dispute whether insulin therapy is a type of diabetes treatment.",
            "insulin therapy",
        )
    )
    assert result["status"] == "ambiguous"
    assert result["relationships"] == []


def test_hypothetical_relation_abstains():
    result = enrich_explicit_semantic_relationship(
        candidate(
            "Insulin therapy might be a type of diabetes treatment.",
            "Insulin therapy",
        )
    )
    assert result["relationships"] == []


def test_quoted_relation_not_promoted():
    result = enrich_explicit_semantic_relationship(
        candidate(
            '"Insulin therapy is a type of diabetes treatment" was quoted as a claim.',
            "Insulin therapy",
        )
    )
    assert result["status"] == "no_evidence"
    assert result["relationships"] == []


def test_negated_synonym_not_inferred():
    result = enrich_explicit_semantic_relationship(
        candidate(
            "High blood pressure is not also known as hypertension.",
            "High blood pressure",
        )
    )
    assert result["relationships"] == []
    assert result["certified"] is False


def test_explicit_affirmative_relationship_still_supported():
    result = enrich_explicit_semantic_relationship(
        candidate(
            "Insulin therapy is a type of diabetes treatment.",
            "Insulin therapy",
        )
    )
    assert result["status"] == "supported_unverified"
    assert result["relationships"][0]["relation_type"] == "narrower_than"


def test_uncertainty_never_mutates_graph_or_links():
    result = enrich_explicit_semantic_relationship(
        candidate(
            "Researchers dispute whether insulin therapy is a type of diabetes treatment.",
            "insulin therapy",
        )
    )
    assert result["certified"] is False
    assert result["automatic_linking_authorized"] is False
    assert result["graph_mutation_performed"] is False
    assert result["linking_decision_performed"] is False


def test_selected_occurrence_with_nonzero_article_offset():
    sentence = "Insulin therapy is a type of diabetes treatment."
    phrase = "Insulin therapy"
    item = candidate(sentence, phrase)
    offset = 500

    for key in ("selection_source_span", "selection_sentence_context"):
        item[key]["start"] += offset
        item[key]["end"] += offset

    result = enrich_explicit_semantic_relationship(item)
    assert result["status"] == "supported_unverified"
    assert result["relationships"][0]["source_span"]["start"] == 500



def _integration_row(sentence, phrase, verified=True):
    from copy import deepcopy

    original = candidate(sentence, phrase, verified=verified)
    return {
        "candidate_index": 0,
        "original_candidate": deepcopy(original),
        "semantic_context": {
            "status": "not_executed",
            "provisional_topic_intent": {"status": "existing"},
        },
        "intelligence_graph": {"status": "existing"},
        "semantic_memory": {"status": "existing"},
    }


def test_375_attachment_preserves_existing_intelligence():
    from copy import deepcopy
    from backend.server.engine.semantic_intelligence_semantic_relationship_enrichment import (
        attach_provisional_semantic_relationships,
    )

    row = _integration_row(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    original = deepcopy(row["original_candidate"])

    result = attach_provisional_semantic_relationships([row])

    attached = result[0]["semantic_context"][
        "provisional_semantic_relationships"
    ]

    assert attached["status"] == "supported_unverified"
    assert attached["relationships"][0]["relation_type"] == "narrower_than"
    assert result[0]["original_candidate"] == original
    assert result[0]["semantic_context"]["provisional_topic_intent"] == {
        "status": "existing"
    }
    assert result[0]["intelligence_graph"] == {"status": "existing"}
    assert result[0]["semantic_memory"] == {"status": "existing"}
    assert attached["certified"] is False
    assert attached["automatic_linking_authorized"] is False
    assert attached["graph_mutation_performed"] is False


def test_375_attachment_negated_statement_abstains():
    from backend.server.engine.semantic_intelligence_semantic_relationship_enrichment import (
        attach_provisional_semantic_relationships,
    )

    rows = [_integration_row(
        "Insulin therapy is not a type of diabetes treatment.",
        "Insulin therapy",
    )]

    result = attach_provisional_semantic_relationships(rows)
    attached = result[0]["semantic_context"][
        "provisional_semantic_relationships"
    ]

    assert attached["status"] == "no_evidence"
    assert attached["relationships"] == []


def test_375_attachment_preserves_existing_relationship_field():
    from backend.server.engine.semantic_intelligence_semantic_relationship_enrichment import (
        attach_provisional_semantic_relationships,
    )

    row = _integration_row(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    row["semantic_context"]["provisional_semantic_relationships"] = {
        "status": "preexisting"
    }

    result = attach_provisional_semantic_relationships([row])
    assert result[0]["semantic_context"][
        "provisional_semantic_relationships"
    ] == {"status": "preexisting"}


def test_375_actual_main_enricher_return_integration():
    from copy import deepcopy
    from backend.server.engine.semantic_intelligence_enricher import (
        enrich_selected_phrase_candidates,
    )

    first = candidate(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    second = candidate(
        "High blood pressure is also known as hypertension.",
        "High blood pressure",
    )
    third = candidate(
        "Insulin therapy is not a type of diabetes treatment.",
        "Insulin therapy",
    )

    selected = [first, second, third]
    snapshot = deepcopy(selected)

    package = enrich_selected_phrase_candidates(
        selected_candidates=deepcopy(selected),
        workspace_id=None,
    )

    rows = package["enriched_candidates"]

    assert len(rows) == 3

    for index, row in enumerate(rows):
        assert row["candidate_index"] == index
        assert row["original_candidate"] == snapshot[index]

        semantic = row["semantic_context"]
        assert "provisional_topic_intent" in semantic

        relation = semantic["provisional_semantic_relationships"]

        assert relation["certified"] is False
        assert relation["automatic_linking_authorized"] is False
        assert relation["graph_mutation_performed"] is False
        assert relation["linking_decision_performed"] is False

    assert rows[0]["semantic_context"][
        "provisional_semantic_relationships"
    ]["relationships"][0]["relation_type"] == "narrower_than"

    assert rows[1]["semantic_context"][
        "provisional_semantic_relationships"
    ]["relationships"][0]["relation_type"] == "synonym_of"

    assert rows[2]["semantic_context"][
        "provisional_semantic_relationships"
    ]["relationships"] == []

    assert selected == snapshot



def test_375_lineage_binds_candidate_and_occurrence():
    from backend.server.engine.semantic_intelligence_semantic_relationship_enrichment import (
        attach_provisional_semantic_relationships,
    )

    row = _integration_row(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    row["original_candidate"].update({
        "upstream_candidate_id": "candidate_alpha",
        "selection_occurrence_id": "occurrence_alpha",
        "workspace_id": "test_workspace",
        "doc_id": "test_document",
    })

    result = attach_provisional_semantic_relationships([row])
    advisory = result[0]["semantic_context"][
        "provisional_semantic_relationships"
    ]
    lineage = advisory["lineage"]
    relationship = advisory["relationships"][0]

    assert lineage["candidate_id"] == "candidate_alpha"
    assert lineage["candidate_index"] == 0
    assert lineage["selection_occurrence_id"] == "occurrence_alpha"
    assert lineage["document_id"] == "test_document"
    assert lineage["semantic_claim_certified"] is False
    assert relationship["evidence_fingerprint"] == lineage[
        "evidence_fingerprint"
    ]
    assert relationship["direction"] == "source_to_target"
    assert relationship["certified"] is False


def test_375_synonym_direction_is_bidirectional():
    from backend.server.engine.semantic_intelligence_semantic_relationship_enrichment import (
        attach_provisional_semantic_relationships,
    )

    rows = [_integration_row(
        "High blood pressure is also known as hypertension.",
        "High blood pressure",
    )]
    advisory = attach_provisional_semantic_relationships(rows)[0][
        "semantic_context"
    ]["provisional_semantic_relationships"]

    assert advisory["relationships"][0]["direction"] == "bidirectional"


def test_375_repeat_phrase_occurrences_do_not_share_evidence_id():
    from copy import deepcopy
    from backend.server.engine.semantic_intelligence_semantic_relationship_enrichment import (
        attach_provisional_semantic_relationships,
    )

    first = _integration_row(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    second = deepcopy(first)

    first["original_candidate"]["selection_occurrence_id"] = "occ_first"
    second["original_candidate"]["selection_occurrence_id"] = "occ_second"

    shift = 1000
    for key in ("selection_source_span", "selection_sentence_context"):
        second["original_candidate"][key]["start"] += shift
        second["original_candidate"][key]["end"] += shift

    rows = attach_provisional_semantic_relationships([first, second])
    first_advisory = rows[0]["semantic_context"][
        "provisional_semantic_relationships"
    ]
    second_advisory = rows[1]["semantic_context"][
        "provisional_semantic_relationships"
    ]

    assert first_advisory["lineage"]["candidate_index"] == 0
    assert second_advisory["lineage"]["candidate_index"] == 1
    assert first_advisory["relationships"][0]["evidence_id"] != (
        second_advisory["relationships"][0]["evidence_id"]
    )


def test_375_fingerprint_is_stable_for_same_candidate():
    from copy import deepcopy
    from backend.server.engine.semantic_intelligence_semantic_relationship_enrichment import (
        attach_provisional_semantic_relationships,
    )

    first = _integration_row(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    second = deepcopy(first)

    a = attach_provisional_semantic_relationships([first])[0][
        "semantic_context"
    ]["provisional_semantic_relationships"]

    b = attach_provisional_semantic_relationships([second])[0][
        "semantic_context"
    ]["provisional_semantic_relationships"]

    assert a["lineage"]["evidence_fingerprint"] == b[
        "lineage"
    ]["evidence_fingerprint"]


def test_375_unverified_occurrence_has_no_verified_lineage():
    from backend.server.engine.semantic_intelligence_semantic_relationship_enrichment import (
        attach_provisional_semantic_relationships,
    )

    rows = [_integration_row(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
        verified=False,
    )]

    advisory = attach_provisional_semantic_relationships(rows)[0][
        "semantic_context"
    ]["provisional_semantic_relationships"]

    assert advisory["status"] == "unavailable"
    assert "lineage" not in advisory
    assert advisory["relationships"] == []


def test_375_lineage_does_not_modify_original_candidate():
    from copy import deepcopy
    from backend.server.engine.semantic_intelligence_semantic_relationship_enrichment import (
        attach_provisional_semantic_relationships,
    )

    row = _integration_row(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    snapshot = deepcopy(row["original_candidate"])

    result = attach_provisional_semantic_relationships([row])

    assert result[0]["original_candidate"] == snapshot
    assert result[0]["semantic_context"][
        "provisional_topic_intent"
    ] == {"status": "existing"}
