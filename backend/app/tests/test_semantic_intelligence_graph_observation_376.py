from copy import deepcopy

from backend.server.engine.semantic_intelligence_semantic_relationship_enrichment import (
    attach_provisional_semantic_relationships,
)
from backend.server.engine.semantic_intelligence_graph_observation_376 import (
    prepare_provisional_graph_observations,
)


def build(sentence, phrase, index=0):
    offset = 100
    local = sentence.index(phrase)
    original = {
        "phrase": phrase,
        "selection_occurrence_id": f"occ_{index}",
        "selection_source_span_status": "verified",
        "selection_sentence_context_status": "derived_from_verified_span",
        "selection_source_span": {
            "start": offset + local,
            "end": offset + local + len(phrase),
            "text": phrase,
            "coordinate_space": "original_article",
        },
        "selection_sentence_context": {
            "start": offset,
            "end": offset + len(sentence),
            "text": sentence,
            "coordinate_space": "original_article",
        },
    }
    row = {
        "candidate_index": index,
        "original_candidate": original,
        "semantic_context": {},
        "intelligence_graph": {
            "status": "existing",
            "evidence_ids": ["existing_evidence"],
        },
    }
    attach_provisional_semantic_relationships([row])
    if index != 0:
        # The attachment enumerates from zero. For an isolated test,
        # translate the generated lineage to the supplied row index.
        rel = row["semantic_context"]["provisional_semantic_relationships"]
        rel["lineage"]["candidate_index"] = index
        for observation in rel["relationships"]:
            observation["source_candidate_index"] = index
    return row


def test_type_of_graph_observation():
    row = build(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    before = deepcopy(row)
    result = prepare_provisional_graph_observations(row)
    assert result["status"] == "supported_unverified"
    obs = result["observations"][0]
    assert obs["source_node"]["surface"] == "Insulin therapy"
    assert obs["target_node"]["surface"] == "diabetes treatment"
    assert obs["relation_type"] == "narrower_than"
    assert obs["source_node"]["canonical_concept_id"] is None
    assert obs["graph_mutation_authorized"] is False
    assert row == before


def test_synonym_graph_observation():
    row = build(
        "High blood pressure is also known as hypertension.",
        "High blood pressure",
    )
    obs = prepare_provisional_graph_observations(row)["observations"][0]
    assert obs["direction"] == "bidirectional"
    assert obs["relation_type"] == "synonym_of"


def test_negated_statement_abstains():
    row = build(
        "Insulin therapy is not a type of diabetes treatment.",
        "Insulin therapy",
    )
    result = prepare_provisional_graph_observations(row)
    assert result["status"] == "no_evidence"
    assert result["observations"] == []


def test_missing_evidence_id_rejected():
    row = build(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    relation = row["semantic_context"][
        "provisional_semantic_relationships"
    ]["relationships"][0]
    del relation["evidence_id"]
    assert prepare_provisional_graph_observations(row)["status"] == "invalid"


def test_lineage_mismatch_rejected():
    row = build(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    row["original_candidate"]["selection_occurrence_id"] = "wrong"
    assert prepare_provisional_graph_observations(row)["status"] == "invalid"


def test_candidate_index_mismatch_rejected():
    row = build(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    row["candidate_index"] = 99
    assert prepare_provisional_graph_observations(row)["status"] == "invalid"


def test_existing_intelligence_graph_is_untouched():
    row = build(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    graph = deepcopy(row["intelligence_graph"])
    prepare_provisional_graph_observations(row)
    assert row["intelligence_graph"] == graph


def test_unknown_relationship_type_rejected():
    row = build(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    rel = row["semantic_context"][
        "provisional_semantic_relationships"
    ]["relationships"][0]
    rel["relation_type"] = "causes"
    assert prepare_provisional_graph_observations(row)["status"] == "invalid"


def test_missing_relationship_source_unavailable():
    assert prepare_provisional_graph_observations({
        "candidate_index": 0,
        "original_candidate": {},
        "semantic_context": {},
    })["status"] == "unavailable"



def test_376_wrong_occurrence_text_rejected():
    row = build(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    row["original_candidate"]["selection_source_span"]["text"] = (
        "Wrong therapy"
    )
    assert prepare_provisional_graph_observations(row)["status"] == "invalid"


def test_376_nonhex_fingerprint_rejected():
    row = build(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    parent = row["semantic_context"]["provisional_semantic_relationships"]
    parent["lineage"]["evidence_fingerprint"] = "z" * 64
    parent["relationships"][0]["evidence_fingerprint"] = "z" * 64
    parent["relationships"][0]["evidence_id"] = (
        "semantic_relation:" + "z" * 64 + ":0"
    )
    assert prepare_provisional_graph_observations(row)["status"] == "invalid"


def test_376_malformed_evidence_suffix_rejected():
    row = build(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    relation = row["semantic_context"][
        "provisional_semantic_relationships"
    ]["relationships"][0]
    relation["evidence_id"] += ":unexpected"
    assert prepare_provisional_graph_observations(row)["status"] == "invalid"


def test_376_modified_sentence_coordinates_rejected():
    row = build(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    original = row["original_candidate"]
    original["selection_source_span"]["start"] += 1
    original["selection_source_span"]["end"] += 1
    parent = row["semantic_context"]["provisional_semantic_relationships"]
    parent["lineage"]["source_span"]["start"] += 1
    parent["lineage"]["source_span"]["end"] += 1
    parent["relationships"][0]["source_span"]["start"] += 1
    parent["relationships"][0]["source_span"]["end"] += 1
    assert prepare_provisional_graph_observations(row)["status"] == "invalid"



def test_376_recalculated_evidence_fingerprint_valid():
    row = build(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    result = prepare_provisional_graph_observations(row)

    assert result["status"] == "supported_unverified"
    observation = result["observations"][0]
    assert observation["independent_validation_status"] == "not_performed"
    assert observation["node_resolution_status"] == "unresolved"
    assert observation["graph_edge_authorized"] is False


def test_376_forged_hex_fingerprint_rejected():
    row = build(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    parent = row["semantic_context"]["provisional_semantic_relationships"]
    forged = "a" * 64

    parent["lineage"]["evidence_fingerprint"] = forged
    relation = parent["relationships"][0]
    relation["evidence_fingerprint"] = forged
    relation["evidence_id"] = "semantic_relation:" + forged + ":0"

    assert prepare_provisional_graph_observations(row)["status"] == "invalid"


def test_376_candidate_identity_mismatch_rejected():
    row = build(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    row["original_candidate"]["upstream_candidate_id"] = "forged_id"

    assert prepare_provisional_graph_observations(row)["status"] == "invalid"


def test_376_wrong_evidence_index_rejected():
    row = build(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    relation = row["semantic_context"][
        "provisional_semantic_relationships"
    ]["relationships"][0]
    relation["evidence_id"] = relation["evidence_id"][:-1] + "9"

    assert prepare_provisional_graph_observations(row)["status"] == "invalid"


def test_376_article_hash_lineage_mismatch_rejected():
    row = build(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    row["original_candidate"][
        "selection_article_text_sha256"
    ] = "b" * 64

    assert prepare_provisional_graph_observations(row)["status"] == "invalid"


def test_376_observation_does_not_certify_or_mutate_graph():
    from copy import deepcopy

    row = build(
        "High blood pressure is also known as hypertension.",
        "High blood pressure",
    )
    snapshot = deepcopy(row)

    result = prepare_provisional_graph_observations(row)

    assert result["status"] == "supported_unverified"
    assert result["certified"] is False
    assert result["graph_mutation_authorized"] is False
    assert result["graph_mutation_performed"] is False
    assert result["automatic_linking_authorized"] is False
    assert result["observations"][0]["graph_edge_authorized"] is False
    assert row == snapshot



def test_376_main_enricher_graph_observation_integration():
    from backend.server.engine.semantic_intelligence_enricher import (
        enrich_selected_phrase_candidates,
    )

    for workspace in (None, "ws_whattoexpect_com"):
        row = build(
            "Insulin therapy is a type of diabetes treatment.",
            "Insulin therapy",
        )
        candidate = deepcopy(row["original_candidate"])

        package = enrich_selected_phrase_candidates(
            selected_candidates=[deepcopy(candidate)],
            workspace_id=workspace,
        )

        enriched = package["enriched_candidates"]
        assert len(enriched) == 1
        assert enriched[0]["original_candidate"] == candidate

        semantic = enriched[0]["semantic_context"]
        assert isinstance(semantic["provisional_topic_intent"], dict)
        assert isinstance(
            semantic["provisional_semantic_relationships"], dict
        )

        graph = semantic["provisional_graph_relationships"]
        assert graph["status"] == "supported_unverified"
        assert len(graph["observations"]) == 1

        observation = graph["observations"][0]
        assert observation["relation_type"] == "narrower_than"
        assert observation["graph_edge_authorized"] is False
        assert observation["independent_validation_status"] == "not_performed"
        assert graph["certified"] is False
        assert graph["graph_mutation_authorized"] is False
        assert graph["automatic_linking_authorized"] is False

        assert isinstance(enriched[0]["intelligence_graph"], dict)


def test_376_graph_attachment_does_not_modify_existing_graph():
    from backend.server.engine.semantic_intelligence_graph_observation_376 import (
        attach_provisional_graph_observations,
    )

    row = build(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    before_graph = deepcopy(row["intelligence_graph"])
    before_original = deepcopy(row["original_candidate"])

    result = attach_provisional_graph_observations([row])

    assert result[0]["intelligence_graph"] == before_graph
    assert result[0]["original_candidate"] == before_original


def test_376_graph_attachment_does_not_overwrite_existing_output():
    from backend.server.engine.semantic_intelligence_graph_observation_376 import (
        attach_provisional_graph_observations,
    )

    row = build(
        "Insulin therapy is a type of diabetes treatment.",
        "Insulin therapy",
    )
    row["semantic_context"]["provisional_graph_relationships"] = {
        "status": "preexisting"
    }

    attach_provisional_graph_observations([row])

    assert row["semantic_context"][
        "provisional_graph_relationships"
    ] == {"status": "preexisting"}
