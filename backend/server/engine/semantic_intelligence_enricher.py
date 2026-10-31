"""






LinkCraftor Semantic Intelligence Enricher.













Canonical Phase 3 JSON contract foundation.






No intelligence source is represented as executed until






its actual integration is implemented and verified.






"""













from __future__ import annotations
from backend.server.engine.semantic_intelligence_topic_intent_validation import validate_phrase_topic_intent
from backend.server.engine.semantic_intelligence_alias_enrichment import enrich_phrase_aliases






from backend.server.engine.semantic_intelligence_canonical_concept_enrichment import enrich_canonical_concept_entities






from backend.server.engine.semantic_enricher_source_health import assess_enricher_source_health





from backend.server.engine.evidence_integrity_enricher_adapter import validate_candidate_evidence_integrity













from copy import deepcopy






from typing import Any













from backend.server.engine.semantic_memory_enricher_adapter import (






    retrieve_phrase_memory_evidence,






)













from backend.server.engine.intelligence_graph_enricher_adapter import (






    retrieve_workspace_concept_evidence,






)













from backend.server.engine.semantic_concept_relationship_enricher_adapter import (



    retrieve_persisted_concept_relationships,



)







from backend.server.engine.entity_graph_enricher_adapter import (






    retrieve_phrase_graph_relationships,




    retrieve_phrase_graph_paths,






)













from backend.server.engine.reasoning_intelligence_enricher_adapter import (






    retrieve_phrase_reasoning_evidence,






)













from backend.server.engine.explainability_enricher_adapter import (






    explain_candidate_evidence,






)




















SOURCE_NAMES = (






    "semantic_memory",






    "intelligence_graph",






    "reasoning_intelligence",






    "explainability_intelligence",






    "evidence_certification",






)




















def _pending_source() -> dict[str, Any]:






    return {






        "status": "not_executed",






        "available": None,






        "evidence_ids": [],






    }




















def enrich_selected_phrase_candidates(






    *,






    selected_candidates: list[dict[str, Any]],






    workspace_id: str | None = None,






) -> dict[str, Any]:






    """Package canonical candidates without fabricating enrichment."""













    if not isinstance(selected_candidates, list):






        raise TypeError("selected_candidates must be a list.")













    if any(not isinstance(item, dict) for item in selected_candidates):






        raise TypeError("All selected candidates must be dictionaries.")













    candidates = deepcopy(selected_candidates)













    enriched_candidates = []













    for index, candidate in enumerate(candidates):






        enriched_candidates.append({






            "candidate_id": candidate.get("upstream_candidate_id"),






            "candidate_index": index,






            "original_candidate": deepcopy(candidate),






            "semantic_context": {






                "status": "not_executed",






                "detected_topic": None,






                "detected_intent": None,






                "meaning": None,






                "contextual_relevance": None,






                "ambiguity_status": "not_evaluated",






                "related_concepts": [],






            },






            "semantic_memory": _pending_source(),






            "intelligence_graph": _pending_source(),






            "reasoning_intelligence": _pending_source(),






            "explainability": _pending_source(),






            "evidence_certification": {






                "status": "not_executed",






                "usable_evidence_ids": [],






                "rejected_evidence_ids": [],






                "warnings": [],






            },






            "enrichment_status": "pending",






            "scorer_readiness": {






                "ready": False,






                "reason": "Semantic enrichment has not executed",






            },






        })













    package = {






        "ok": True,






        "schema_version": "1.0.0",






        "component": "semantic_intelligence_enricher",






        "status": "ENRICHMENT_PENDING",






        "enrichment_executed": False,






        "context": {






            "workspace_id": None,






            "document_id": None,






            "vertical": None,






            "language": None,






            "article_topic": None,






        },






        "pipeline": {






            "input_stage": "highlight_selection_engine",






            "output_stage": "semantic_intelligence_enricher",






            "next_stage": "original_scorer",






            "input_candidate_count": len(candidates),






            "output_candidate_count": len(candidates),






            "candidate_order_preserved": True,






            "candidate_identity_preserved": True,






        },






        "intelligence_sources": {






            name: _pending_source()






            for name in SOURCE_NAMES






        },






        "evidence_registry": {},






        "candidate_count": len(candidates),






        "candidates": candidates,






        "enriched_candidates": enriched_candidates,






        "summary": {






            "candidates_received": len(candidates),






            "candidates_returned": len(candidates),






            "fully_enriched": 0,






            "partially_enriched": 0,






            "without_usable_evidence": len(candidates),






            "candidates_removed": 0,






            "candidates_pending_enrichment": len(candidates),






        },






        "downstream_contract": {






            "consumer": "original_scorer",






            "enrichment_is_advisory": True,






            "final_link_allocation_performed": False,






            "route_dispatch_performed": False,






            "target_resolution_performed": False,






            "final_highlight_validation_performed": False,






        },






    }




















    # An omitted workspace ID preserves the original foundation behavior.






    if workspace_id is None:






        enrich_canonical_concept_entities(package)






        enrich_phrase_aliases(package)
        validate_phrase_topic_intent(package)
        from backend.server.engine.semantic_phrase_topic_intent_interpreter import attach_selector_topic_intent_advisory
        attach_selector_topic_intent_advisory(enriched_candidates)
        from backend.server.engine.semantic_intelligence_semantic_relationship_enrichment import attach_provisional_semantic_relationships
        attach_provisional_semantic_relationships(enriched_candidates)
        from backend.server.engine.semantic_intelligence_graph_observation_376 import attach_provisional_graph_observations
        attach_provisional_graph_observations(enriched_candidates)
        return package













    # Validate before attempting any workspace-scoped retrieval.






    import re






    if not isinstance(workspace_id, str) or not re.fullmatch(






        r"[A-Za-z0-9_-]+", workspace_id






    ):






        raise ValueError("A valid workspace_id is required.")













    package["context"]["workspace_id"] = workspace_id













    failures = 0













    for entry in package["enriched_candidates"]:






        original_candidate = entry["original_candidate"]






        phrase = original_candidate.get("phrase")






        index = entry["candidate_index"]













        if not isinstance(phrase, str) or not phrase.strip():






            entry["semantic_memory"] = {






                "status": "not_queried",






                "memory_matches": [],






                "evidence_ids": [],






                "reason": "missing_candidate_phrase",






            }






            continue













        try:






            memory = retrieve_phrase_memory_evidence(






                workspace_id=workspace_id,






                phrase=phrase,
                candidate_context=deepcopy(original_candidate),










            )






            if (






                not isinstance(memory, dict)






                or memory.get("status") not in (






                    "evidence_found", "no_evidence"






                )






                or not isinstance(






                    memory.get("retrieved_memory"), list






                )






                or memory.get("workspace_id") != workspace_id






                or memory.get("certified") is not False






            ):






                raise RuntimeError("Invalid memory adapter response")













            matches = memory["retrieved_memory"]






            evidence_ids = []













            for position, match in enumerate(matches):






                if not isinstance(match, dict):






                    raise RuntimeError("Invalid memory match")













                evidence_id = f"memory_candidate_{index}_{position}"






                evidence_ids.append(evidence_id)













                package["evidence_registry"][evidence_id] = {






                    "source": "semantic_memory",






                    "workspace_id": workspace_id,






                    "candidate_index": index,






                    "memory_id": match.get("memory_id"),






                    "text": match.get("text"),






                    "retrieval_score": match.get("recall_score"),






                    "retrieval_method": memory.get("retrieval_method"),






                    **{




                        field: deepcopy(match[field])




                        for field in (




                            "canonical", "semantic_type", "aliases",




                            "confidence", "confidence_factors",




                            "source_count", "evidence_count",




                            "first_seen_at", "last_seen_at",




                            "source_feed_version", "source_id",




                            "document_id", "provenance", "stale",




                            "contextual_relevance",




                        )




                        if field in match




                    },




                    "certified": False,






                    "validity_status": (




                        "stale"




                        if match.get("stale") is True




                        else "not_evaluated"




                    ),




                    **(




                        {




                            "source_validity_status": deepcopy(




                                match["validity_status"]




                            )




                        }




                        if "validity_status" in match




                        else {}




                    ),






                }













            entry["semantic_memory"] = {






                "status": memory["status"],






                "memory_matches": deepcopy(matches),






                "evidence_ids": evidence_ids,






                "retrieval_method": memory.get("retrieval_method"),






                "certified": False,






            }






            entry["enrichment_status"] = "partial"













        except Exception as exc:






            failures += 1






            entry["semantic_memory"] = {






                "status": "error",






                "memory_matches": [],






                "evidence_ids": [],






                "error_type": type(exc).__name__,






            }













    package["intelligence_sources"]["semantic_memory"] = {






        "status": (






            "completed_with_errors" if failures else "completed"






        ),






        "available": failures == 0,






        "evidence_ids": list(package["evidence_registry"]),






        "error_count": failures,






    }













    package["enrichment_executed"] = bool(






        package["enriched_candidates"]






    )






    package["status"] = (






        "ENRICHMENT_COMPLETED_WITH_GAPS"






        if package["enriched_candidates"]






        else "ENRICHMENT_PENDING"






    )






    package["summary"]["partially_enriched"] = sum(






        item["enrichment_status"] == "partial"






        for item in package["enriched_candidates"]






    )






    package["summary"]["candidates_pending_enrichment"] = sum(






        item["enrichment_status"] == "pending"






        for item in package["enriched_candidates"]






    )













    # No source evidence is certified here. Other intelligence






    # sources and Phase 3.6 certification remain pending.













    # Phase 3.3: read existing workspace concept evidence only.






    # Concept aliases are not certified semantic graph edges.






    graph_errors = 0






    graph_executed = 0






    graph_evidence_ids = []













    for entry in package["enriched_candidates"]:






        candidate = entry["original_candidate"]






        phrase = candidate.get("phrase")






        index = entry["candidate_index"]













        if not isinstance(phrase, str) or not phrase.strip():






            entry["intelligence_graph"] = {






                "status": "not_queried",






                "concept_matches": [],






                "relationship_edges": [],






                "relationship_retrieval_status": "not_implemented",






                "evidence_ids": [],






                "reason": "missing_candidate_phrase",






                "certified": False,






            }






            continue













        try:






            graph = retrieve_workspace_concept_evidence(






                workspace_id=workspace_id,






                phrase=phrase,






            )













            if (






                not isinstance(graph, dict)






                or graph.get("workspace_id") != workspace_id






                or graph.get("status") not in (






                    "concept_evidence_found", "no_evidence"






                )






                or not isinstance(graph.get("concept_matches"), list)






                or graph.get("relationship_edges") != []






                or graph.get("certified") is not False






            ):






                raise RuntimeError("Invalid concept evidence contract")













            matches = graph["concept_matches"]






            evidence_ids = []






            graph_executed += 1













            for position, match in enumerate(matches):






                if not isinstance(match, dict):






                    raise RuntimeError("Invalid concept evidence record")













                evidence_id = f"graph_concept_{index}_{position}"






                evidence_ids.append(evidence_id)













                package["evidence_registry"][evidence_id] = {






                    "source": "workspace_concept_store",






                    "evidence_type": "concept_or_alias_match",






                    "workspace_id": workspace_id,






                    "candidate_index": index,






                    "concept_key": match.get("concept_key"),






                    "concept": match.get("concept"),






                    "match_type": match.get("match_type"),






                    "source_record": deepcopy(






                        match.get("original_record")






                    ),






                    "relationship_asserted": False,






                    "certified": False,






                    "validity_status": "not_evaluated",






                }













            graph_evidence_ids.extend(evidence_ids)













            entry["intelligence_graph"] = {






                "status": graph["status"],






                "source": "workspace_concept_store",






                "concept_matches": deepcopy(matches),






                "relationship_edges": [],






                "relationship_retrieval_status": (






                    "not_implemented"






                ),






                "evidence_ids": evidence_ids,






                "certified": False,






            }













            if matches:






                entry["enrichment_status"] = "partial"













        except Exception as exc:






            graph_errors += 1






            entry["intelligence_graph"] = {






                "status": "error",






                "concept_matches": [],






                "relationship_edges": [],






                "evidence_ids": [],






                "relationship_retrieval_status": "not_implemented",






                "error_type": type(exc).__name__,






                "certified": False,






            }













    package["intelligence_sources"]["intelligence_graph"] = {






        "status": (






            "completed_with_errors" if graph_errors






            else "concept_retrieval_completed"






            if graph_executed






            else "not_executed"






        ),






        "available": graph_executed > 0,






        "evidence_ids": graph_evidence_ids,






        "error_count": graph_errors,






        "relationship_retrieval_status": "not_implemented",






    }













    # Some candidates may have been enriched solely through






    # graph concepts; recalculate the existing summary.






    package["summary"]["partially_enriched"] = sum(






        item["enrichment_status"] == "partial"






        for item in package["enriched_candidates"]






    )






    package["summary"]["candidates_pending_enrichment"] = sum(






        item["enrichment_status"] == "pending"






        for item in package["enriched_candidates"]






    )




















    # Phase 3.3: retrieve stored entity graph observations.






    relation_ids = []






    relation_errors = 0






    relation_queries = 0













    for entry in package["enriched_candidates"]:






        phrase = entry["original_candidate"].get("phrase")






        index = entry["candidate_index"]






        section = entry["intelligence_graph"]













        section["matched_nodes"] = []






        section["relationship_edges"] = []






        section["relationship_evidence_ids"] = []













        if not isinstance(phrase, str) or not phrase.strip():






            section["relationship_retrieval_status"] = "not_queried"






            continue













        try:






            result = retrieve_phrase_graph_relationships(






                workspace_id=workspace_id,






                phrase=phrase,






            )













            if (






                not isinstance(result, dict)






                or result.get("workspace_id") != workspace_id






                or result.get("certified") is not False






                or result.get("status") not in (






                    "no_evidence",






                    "node_evidence_found",






                    "relationship_evidence_found",






                )






                or not isinstance(result.get("matched_nodes"), list)






                or not isinstance(result.get("relationship_edges"), list)






            ):






                raise RuntimeError("Invalid graph retrieval contract")













            nodes = result["matched_nodes"]






            edges = result["relationship_edges"]






            status = result["status"]













            if any(not isinstance(item, dict) for item in nodes + edges):






                raise RuntimeError("Malformed graph evidence")













            if (






                (status == "no_evidence" and (nodes or edges))






                or (status == "node_evidence_found" and (not nodes or edges))






                or (status == "relationship_evidence_found" and not edges)






            ):






                raise RuntimeError("Inconsistent graph status")













            for edge in edges:






                if (






                    edge.get("certified") is not False






                    or not edge.get("source_node_id")






                    or not edge.get("target_node_id")






                    or not isinstance(edge.get("original_record"), dict)






                ):






                    raise RuntimeError("Invalid graph edge provenance")













            ids = []













            for position, edge in enumerate(edges):






                evidence_id = f"entity_graph_edge_{index}_{position}"






                ids.append(evidence_id)













                package["evidence_registry"][evidence_id] = {






                    "source": "uploaded_entity_graph",






                    "evidence_type": "observed_graph_relationship",






                    "workspace_id": workspace_id,






                    "candidate_index": index,






                    "edge_index": edge.get("edge_index"),






                    "source_node_id": edge["source_node_id"],






                    "target_node_id": edge["target_node_id"],






                    "relationship_type": edge.get("relationship_type"),






                    "relationship_weight": edge.get("relationship_weight"),






                    "original_edge": deepcopy(edge["original_record"]),






                    "source_node": deepcopy(edge.get("source_node")),






                    "target_node": deepcopy(edge.get("target_node")),






                    "semantic_equivalence_asserted": False,






                    "approved_link_target": False,






                    "certified": False,






                    "validity_status": "not_evaluated",






                }













            relation_queries += 1






            relation_ids.extend(ids)













            section["matched_nodes"] = deepcopy(nodes)






            section["relationship_edges"] = deepcopy(edges)






            section["relationship_evidence_ids"] = ids






            section["evidence_ids"].extend(ids)






            section["relationship_retrieval_status"] = status






            section["relationship_storage_status"] = result.get(






                "storage_status"






            )













        except Exception as exc:






            relation_errors += 1






            section["relationship_retrieval_status"] = "error"






            section["relationship_error_type"] = type(exc).__name__


















    # Phase 3.3.5: read-only graph-path retrieval.




    path_ids = []




    path_queries = 0




    path_errors = 0









    for entry in package["enriched_candidates"]:




        phrase = entry["original_candidate"].get("phrase")




        index = entry["candidate_index"]




        section = entry["intelligence_graph"]




        section["graph_paths"] = []




        section["path_evidence_ids"] = []









        if not isinstance(phrase, str) or not phrase.strip():




            section["path_retrieval_status"] = "not_queried"




            continue









        try:




            result = retrieve_phrase_graph_paths(




                workspace_id=workspace_id,




                phrase=phrase,




            )









            if (




                not isinstance(result, dict)




                or result.get("workspace_id") != workspace_id




                or result.get("certified") is not False




                or result.get("status") not in (




                    "no_evidence", "node_evidence_found",




                    "path_evidence_found",




                )




                or not isinstance(result.get("graph_paths"), list)




            ):




                raise RuntimeError("Invalid graph path contract")









            paths = result["graph_paths"]




            if (




                result.get("path_count") != len(paths)




                or (result["status"] == "path_evidence_found") != bool(paths)




            ):




                raise RuntimeError("Inconsistent graph path status")









            for item in paths:




                if not isinstance(item, dict):




                    raise RuntimeError("Malformed graph path")




                node_ids = item.get("node_ids")




                nodes = item.get("nodes")




                edges = item.get("edges")




                hops = item.get("hop_count")




                if (




                    item.get("certified") is not False




                    or not isinstance(node_ids, list)




                    or not isinstance(nodes, list)




                    or not isinstance(edges, list)




                    or type(hops) is not int




                    or not 1 <= hops <= 2




                    or len(edges) != hops




                    or len(node_ids) != hops + 1




                    or len(nodes) != len(node_ids)




                    or any(not isinstance(n, str) for n in node_ids)




                    or len(set(node_ids)) != len(node_ids)




                ):




                    raise RuntimeError("Invalid graph path structure")









                for position, node in enumerate(nodes):




                    if (




                        not isinstance(node, dict)




                        or node.get("node_id") != node_ids[position]




                        or not isinstance(node.get("original_record"), dict)




                    ):




                        raise RuntimeError("Invalid graph path node")









                for position, edge in enumerate(edges):




                    if (




                        not isinstance(edge, dict)




                        or edge.get("certified") is not False




                        or edge.get("source_node_id") != node_ids[position]




                        or edge.get("target_node_id") != node_ids[position + 1]




                        or not isinstance(edge.get("original_record"), dict)




                        or type(edge.get("edge_index")) is not int




                    ):




                        raise RuntimeError("Invalid graph path edge")









            ids = []




            for position, item in enumerate(paths):




                evidence_id = f"entity_graph_path_{index}_{position}"




                if evidence_id in package["evidence_registry"]:




                    raise RuntimeError("Duplicate graph path evidence ID")









                package["evidence_registry"][evidence_id] = {




                    "source": "uploaded_entity_graph",




                    "evidence_type": "observed_graph_path",




                    "workspace_id": workspace_id,




                    "candidate_index": index,




                    "node_ids": deepcopy(item["node_ids"]),




                    "nodes": deepcopy(item["nodes"]),




                    "edges": deepcopy(item["edges"]),




                    "hop_count": item["hop_count"],




                    "semantic_equivalence_asserted": False,




                    "approved_link_target": False,




                    "certified": False,




                    "validity_status": "not_evaluated",




                }




                ids.append(evidence_id)









            section["graph_paths"] = deepcopy(paths)




            section["path_evidence_ids"] = ids




            section["evidence_ids"].extend(ids)




            section["path_retrieval_status"] = result["status"]




            section["path_storage_status"] = result.get("storage_status")




            path_ids.extend(ids)




            path_queries += 1









        except Exception as exc:




            path_errors += 1




            section["path_retrieval_status"] = "error"




            section["path_error_type"] = type(exc).__name__













    # Phase 3.3.2: independently retrieve persisted concept relationships.



    concept_relation_ids = []



    concept_relation_queries = 0



    concept_relation_errors = 0







    for entry in package["enriched_candidates"]:



        phrase = entry["original_candidate"].get("phrase")



        index = entry["candidate_index"]



        section = entry["intelligence_graph"]







        section["concept_relationships"] = []



        section["concept_relationship_evidence_ids"] = []







        if not isinstance(phrase, str) or not phrase.strip():



            section["concept_relationship_retrieval_status"] = "not_queried"



            continue







        try:



            result = retrieve_persisted_concept_relationships(



                workspace_id=workspace_id,



                phrase=phrase,



            )







            if (



                not isinstance(result, dict)



                or result.get("workspace_id") != workspace_id



                or result.get("source") != "semantic_map_v2_concept_graph"



                or result.get("certified") is not False



                or result.get("linking_decision_performed") is not False



                or result.get("status") not in (



                    "no_evidence", "relationship_evidence_found",



                )



                or not isinstance(result.get("relationship_records"), list)



            ):



                raise RuntimeError("Invalid concept relationship contract")







            records = result["relationship_records"]







            if (



                type(result.get("relationship_count")) is not int



                or result["relationship_count"] != len(records)



                or (result["status"] == "relationship_evidence_found")



                   != bool(records)



            ):



                raise RuntimeError("Inconsistent concept relationship status")







            # Validate every record before adding any registry evidence.



            for record in records:



                if not isinstance(record, dict):



                    raise RuntimeError("Malformed concept relationship")







                if (



                    record.get("certified") is not False



                    or record.get("approved_link_target") is not False



                    or record.get("semantic_equivalence_asserted") is not False



                    or not isinstance(record.get("canonical_phrase"), str)



                    or not record["canonical_phrase"].strip()



                    or not isinstance(record.get("related_phrase"), str)



                    or not record["related_phrase"].strip()



                    or not isinstance(record.get("relation_type"), str)



                    or not record["relation_type"].strip()



                    or not isinstance(record.get("source"), str)



                    or not record["source"].strip()



                    or not isinstance(record.get("original_evidence"), dict)



                    or not isinstance(record.get("conflict_resolution"), dict)



                    or record["conflict_resolution"].get("hard_blocked")



                       is not False



                    or type(record.get("concept_index")) is not int



                    or type(record.get("evidence_index")) is not int



                    or record["concept_index"] < 0



                    or record["evidence_index"] < 0



                ):



                    raise RuntimeError("Invalid concept relationship provenance")







                if (



                    record["original_evidence"].get("source")



                       != record["source"]



                    or record["original_evidence"].get("relation_type")



                       != record["relation_type"]



                    or record["original_evidence"].get("related_phrase")



                       != record["related_phrase"]



                ):



                    raise RuntimeError("Concept relationship source mismatch")







                for field in ("concept_confidence", "evidence_confidence"):



                    value = record.get(field)



                    if (



                        type(value) not in (float, int)



                        or not 0 <= value <= 1



                    ):



                        raise RuntimeError("Invalid concept confidence")







            ids = [



                f"semantic_concept_relation_{index}_{position}"



                for position in range(len(records))



            ]







            if (



                len(set(ids)) != len(ids)



                or any(key in package["evidence_registry"] for key in ids)



            ):



                raise RuntimeError("Duplicate concept relationship evidence")







            for evidence_id, record in zip(ids, records):



                package["evidence_registry"][evidence_id] = {



                    "source": "semantic_map_v2_concept_graph",



                    "evidence_type": "observed_concept_relationship",



                    "workspace_id": workspace_id,



                    "candidate_index": index,



                    "concept_index": record["concept_index"],



                    "evidence_index": record["evidence_index"],



                    "relation_type": record["relation_type"],



                    "original_evidence": deepcopy(record["original_evidence"]),



                    "relationship_record": deepcopy(record),



                    "semantic_equivalence_asserted": False,



                    "approved_link_target": False,



                    "certified": False,



                    "validity_status": "not_evaluated",



                }







            section["concept_relationships"] = deepcopy(records)



            section["concept_relationship_evidence_ids"] = ids



            section["evidence_ids"].extend(ids)



            section["concept_relationship_retrieval_status"] = result["status"]



            section["concept_relationship_storage_status"] = result.get(



                "storage_status"



            )



            concept_relation_ids.extend(ids)



            concept_relation_queries += 1







        except Exception as exc:



            concept_relation_errors += 1



            section["concept_relationship_retrieval_status"] = "error"



            section["concept_relationship_error_type"] = type(exc).__name__










    # Phase 3.3.4: classify retrieved semantic relationship signals.


    # This does not infer new edges or assert semantic equivalence.


    semantic_signal_ids = []


    semantic_signal_count = 0





    for entry in package["enriched_candidates"]:


        section = entry["intelligence_graph"]


        section["semantic_relationship_signals"] = []


        section["semantic_relationship_evidence_ids"] = []





        if section.get("concept_relationship_retrieval_status") != (


            "relationship_evidence_found"


        ):


            section["semantic_relationship_retrieval_status"] = (


                "source_unavailable"


                if section.get("concept_relationship_retrieval_status") == "error"


                else "no_evidence"


            )


            continue





        records = section.get("concept_relationships", [])


        ids = section.get("concept_relationship_evidence_ids", [])





        # Both collections were validated during concept retrieval.


        # Refuse incomplete attribution rather than synthesizing proof.


        if not isinstance(records, list) or not isinstance(ids, list) or (


            len(records) != len(ids)


        ):


            section["semantic_relationship_retrieval_status"] = "error"


            continue





        signals = []


        signal_ids = []





        for record, evidence_id in zip(records, ids):


            if not isinstance(record, dict) or not isinstance(evidence_id, str):


                continue


            if evidence_id not in package["evidence_registry"]:


                continue


            if record.get("certified") is not False:


                continue


            if record.get("approved_link_target") is not False:


                continue


            if record.get("semantic_equivalence_asserted") is not False:


                continue


            if (


                not isinstance(record.get("conflict_resolution"), dict)


                or record["conflict_resolution"].get("hard_blocked") is not False


            ):


                continue





            relation_type = record.get("relation_type")


            if relation_type == "synonym":


                signal_type = "recorded_synonym_observation"


            elif relation_type == "article_related_concept":


                signal_type = "recorded_topical_association"


            else:


                # Other relationships remain in concept evidence but


                # are not promoted into semantic relationship signals.


                continue





            signals.append({


                "signal_type": signal_type,


                "recorded_relation_type": relation_type,


                "canonical_phrase": record.get("canonical_phrase"),


                "related_phrase": record.get("related_phrase"),


                "source": record.get("source"),


                "source_role": record.get("source_role"),


                "concept_confidence": record.get("concept_confidence"),


                "evidence_confidence": record.get("evidence_confidence"),


                "evidence_id": evidence_id,


                "semantic_equivalence_asserted": False,


                "approved_link_target": False,


                "certified": False,


            })


            signal_ids.append(evidence_id)





        section["semantic_relationship_signals"] = signals
        # confidence_evidence_main_integration_378
        # Preserve source confidence and existing evidence ownership.
        from backend.server.engine.semantic_intelligence_confidence_evidence_378 import (
            preserve_confidence_evidence,
        )
        section["semantic_relationship_confidence_evidence"] = (
            preserve_confidence_evidence(signals)
        )


        section["semantic_relationship_evidence_ids"] = signal_ids


        section["semantic_relationship_retrieval_status"] = (


            "observational_signals_found" if signals else "no_evidence"


        )


        semantic_signal_ids.extend(signal_ids)


        semantic_signal_count += len(signals)





    graph_source = package["intelligence_sources"]["intelligence_graph"]






    graph_source["evidence_ids"].extend(relation_ids)






    graph_source["relationship_evidence_ids"] = relation_ids


    # These reference existing concept evidence, not new registry entries.


    graph_source["semantic_relationship_evidence_ids"] = semantic_signal_ids


    graph_source["semantic_relationship_signal_count"] = semantic_signal_count


    graph_source["semantic_relationship_retrieval_status"] = (


        "observational_signals_found"


        if semantic_signal_count else "no_evidence"


    )






    graph_source["evidence_ids"].extend(concept_relation_ids)



    graph_source["concept_relationship_evidence_ids"] = concept_relation_ids



    graph_source["concept_relationship_query_count"] = concept_relation_queries



    graph_source["concept_relationship_error_count"] = concept_relation_errors



    graph_source["concept_relationship_retrieval_status"] = (



        "completed_with_errors" if concept_relation_errors



        else "completed" if concept_relation_queries



        else "not_executed"



    )








    graph_source["evidence_ids"].extend(path_ids)




    graph_source["path_evidence_ids"] = path_ids




    graph_source["path_query_count"] = path_queries




    graph_source["path_error_count"] = path_errors




    graph_source["path_retrieval_status"] = (




        "completed_with_errors" if path_errors




        else "completed" if path_queries




        else "not_executed"




    )











    graph_source["relationship_query_count"] = relation_queries






    graph_source["relationship_error_count"] = relation_errors






    graph_source["relationship_retrieval_status"] = (






        "completed_with_errors" if relation_errors






        else "completed" if relation_queries






        else "not_executed"






    )













    if relation_errors:






        graph_source["status"] = "completed_with_errors"






    elif relation_queries and graph_source["status"] == "not_executed":






        graph_source["status"] = "relationship_retrieval_completed"













    graph_source["available"] = (






        graph_source["available"] or relation_queries > 0






    )













    # Derive enrichment state from evidence, not lookup execution.






    for entry in package["enriched_candidates"]:






        memory_ids = entry["semantic_memory"].get("evidence_ids", [])






        graph_ids = entry["intelligence_graph"].get("evidence_ids", [])






        graph_nodes = entry["intelligence_graph"].get("matched_nodes", [])













        has_evidence = bool(memory_ids or graph_ids or graph_nodes)













        entry["enrichment_status"] = (






            "partial" if has_evidence else "pending"






        )













    package["summary"]["partially_enriched"] = sum(






        item["enrichment_status"] == "partial"






        for item in package["enriched_candidates"]






    )






    package["summary"]["candidates_pending_enrichment"] = sum(






        item["enrichment_status"] == "pending"






        for item in package["enriched_candidates"]






    )




















    # Phase 3.4: reuse existing document-level reasoning evidence.






    # No phrase-level semantic proof or link decision is asserted.






    reasoning_ids = []






    reasoning_queries = 0






    reasoning_errors = 0













    for entry in package["enriched_candidates"]:






        phrase = entry["original_candidate"].get("phrase")






        index = entry["candidate_index"]













        section = entry["reasoning_intelligence"]













        if not isinstance(section, dict):






            raise RuntimeError("Invalid reasoning JSON section")













        section["matched_documents"] = []






        section["document_relationships"] = []






        section["reasoning_observations"] = []






        section["evidence_ids"] = []






        section["phrase_level_semantic_proof"] = False






        section["linking_decision_performed"] = False






        section["certified"] = False













        if not isinstance(phrase, str) or not phrase.strip():






            section["status"] = "not_queried"






            continue













        try:






            result = retrieve_phrase_reasoning_evidence(






                workspace_id=workspace_id,






                phrase=phrase,






            )













            if (






                not isinstance(result, dict)






                or result.get("workspace_id") != workspace_id






                or result.get("status") not in (






                    "no_evidence", "document_context_found"






                )






                or result.get("certified") is not False






                or result.get("phrase_level_semantic_proof") is not False






                or result.get("linking_decision_performed") is not False






                or not isinstance(result.get("matched_documents"), list)






                or not isinstance(result.get("document_relationships"), list)






                or not isinstance(result.get("reasoning_observations"), list)






            ):






                raise RuntimeError("Invalid reasoning evidence contract")
            # reasoning_signal_association_377_integration
            from backend.server.engine.semantic_intelligence_reasoning_signals_377 import associate_reasoning_signals
            section["reasoning_signal_association"] = (
                associate_reasoning_signals(
                    entry.get("original_candidate"),
                    result,
                    expected_workspace_id=workspace_id,
                )
            )













            docs = result["matched_documents"]






            relations = result["document_relationships"]






            observations = result["reasoning_observations"]













            if any(






                not isinstance(item, dict)






                for item in docs + relations + observations






            ):






                raise RuntimeError("Malformed reasoning records")













            if result["status"] == "no_evidence" and (






                docs or relations or observations






            ):






                raise RuntimeError("No-evidence status mismatch")













            if result["status"] == "document_context_found" and not docs:






                raise RuntimeError("Document context missing")













            if any(






                item.get("certified") is not False






                for item in observations






            ):






                raise RuntimeError("Reasoning observation certification invalid")













            matched_ids = {






                str(item.get("document_id"))






                for item in docs






                if item.get("document_id") is not None






            }













            if len(matched_ids) != len(docs):






                raise RuntimeError("Invalid or duplicate document identity")













            for relation in relations:






                left = str(relation.get("left_document_id", ""))






                right = str(relation.get("right_document_id", ""))






                if left not in matched_ids and right not in matched_ids:






                    raise RuntimeError("Unrelated reasoning relationship")













            records = {}













            for position, document in enumerate(docs):






                evidence_id = f"reasoning_document_{index}_{position}"






                records[evidence_id] = {






                    "source": "workspace_cross_document_reasoning",






                    "evidence_type": "document_phrase_occurrence",






                    "workspace_id": workspace_id,






                    "candidate_index": index,






                    "original_record": deepcopy(document),






                    "interpretation": "document_occurrence_only",






                    "phrase_level_semantic_proof": False,






                    "approved_link_target": False,






                    "certified": False,






                    "validity_status": "not_evaluated",






                }













            for position, relation in enumerate(relations):






                evidence_id = f"reasoning_relation_{index}_{position}"






                records[evidence_id] = {






                    "source": "workspace_cross_document_reasoning",






                    "evidence_type": "document_relationship_context",






                    "workspace_id": workspace_id,






                    "candidate_index": index,






                    "original_record": deepcopy(relation),






                    "interpretation": "document_level_context_only",






                    "phrase_level_semantic_proof": False,






                    "approved_link_target": False,






                    "certified": False,






                    "validity_status": "not_evaluated",






                }













            if any(






                evidence_id in package["evidence_registry"]






                for evidence_id in records






            ):






                raise RuntimeError("Reasoning evidence ID collision")













            package["evidence_registry"].update(records)






            ids = list(records)






            reasoning_ids.extend(ids)






            reasoning_queries += 1













            section["status"] = result["status"]






            section["matched_documents"] = deepcopy(docs)






            section["document_relationships"] = deepcopy(relations)






            section["reasoning_observations"] = deepcopy(observations)






            section["evidence_ids"] = ids






            section["source"] = "workspace_cross_document_reasoning"













            if ids:






                entry["enrichment_status"] = "partial"













        except Exception as exc:






            reasoning_errors += 1






            section["status"] = "error"






            section["error_type"] = type(exc).__name__













    reasoning_source = package["intelligence_sources"][






        "reasoning_intelligence"






    ]













    reasoning_source["status"] = (






        "completed_with_errors" if reasoning_errors






        else "retrieval_completed" if reasoning_queries






        else "not_executed"






    )






    reasoning_source["available"] = bool(reasoning_ids)






    reasoning_source["evidence_ids"] = reasoning_ids






    reasoning_source["query_count"] = reasoning_queries






    reasoning_source["error_count"] = reasoning_errors






    reasoning_source["certified"] = False













    package["summary"]["partially_enriched"] = sum(






        item["enrichment_status"] == "partial"






        for item in package["enriched_candidates"]






    )






    package["summary"]["candidates_pending_enrichment"] = sum(






        item["enrichment_status"] == "pending"






        for item in package["enriched_candidates"]






    )




















    # Phase 3.5 ? explain only the evidence already registered.






    explanation_ids = []






    explanation_errors = 0






    explanation_count = 0













    for entry in package["enriched_candidates"]:






        index = entry["candidate_index"]






        candidate = entry["original_candidate"]













        # Collect evidence belonging to this candidate only.






        candidate_evidence_ids = [






            evidence_id






            for evidence_id, record in package["evidence_registry"].items()






            if isinstance(record, dict)






            and record.get("candidate_index") == index






        ]













        try:






            explanation = explain_candidate_evidence(






                candidate_index=index,






                candidate=candidate,






                evidence_ids=candidate_evidence_ids,






                evidence_registry=package["evidence_registry"],






            )













            if (






                not isinstance(explanation, dict)






                or explanation.get("candidate_index") != index






                or explanation.get("evidence_ids") != candidate_evidence_ids






                or explanation.get("certified") is not False






                or explanation.get("approved_link_target") is not False






                or explanation.get("scorer_decision_performed") is not False






                or explanation.get("status") not in (






                    "evidence_explained", "no_evidence"






                )






            ):






                raise RuntimeError("Invalid explanation contract")













            if explanation.get("evidence_count") != len(






                candidate_evidence_ids






            ):






                raise RuntimeError("Explanation evidence count mismatch")













            section = entry["explainability"]













            if not isinstance(section, dict):






                raise RuntimeError("Invalid Explainability section")













            section.update(deepcopy(explanation))
            # explanation_evidence_main_integration_3798
            # Associate existing validated registry evidence only.
            # No additional retrieval, scoring, or link authorization.
            from backend.server.engine.semantic_intelligence_explanation_evidence_379 import (
                associate_explanation_evidence,
            )

            evidence_association = associate_explanation_evidence(
                candidate_index=index,
                evidence_ids=candidate_evidence_ids,
                evidence_registry=package["evidence_registry"],
            )

            if evidence_association["status"] == "invalid":
                raise RuntimeError(
                    "Invalid explanation evidence association: "
                    + str(evidence_association.get("reason"))
                )

            if (
                evidence_association["evidence_ids"]
                != candidate_evidence_ids
                or evidence_association["evidence_count"]
                != len(candidate_evidence_ids)
            ):
                raise RuntimeError(
                    "Explanation evidence association mismatch"
                )

            section["evidence_association"] = evidence_association

            # sparse_main_integration_386
            # Assess existing candidate evidence without deleting,
            # reordering, scoring, or automatically linking phrases.
            from backend.server.engine.semantic_intelligence_sparse_38 import (
                assess_sparse_intelligence,
            )

            # sparse_confidence_producer_connection_382
            sparse_graph = entry.get("intelligence_graph")
            if sparse_graph is not None and not isinstance(sparse_graph, dict):
                raise RuntimeError("Invalid sparse confidence Graph section")

            sparse_confidence_evidence = (
                sparse_graph.get(
                    "semantic_relationship_confidence_evidence"
                )
                if sparse_graph is not None else None
            )

            sparse_assessment = assess_sparse_intelligence(
                candidate_index=index,
                original_candidate=candidate,
                evidence_association=evidence_association,
                confidence_evidence=sparse_confidence_evidence,
            )

            if sparse_assessment["status"] == "invalid":
                raise RuntimeError(
                    "Sparse intelligence assessment invalid: "
                    + str(sparse_assessment.get("reason"))
                )

            if (
                sparse_assessment["candidate_retained"] is not True
                or sparse_assessment["original_candidate"] != candidate
                or sparse_assessment["evidence_ids"]
                != candidate_evidence_ids
            ):
                raise RuntimeError(
                    "Sparse intelligence candidate/evidence mismatch"
                )

            entry["sparse_intelligence"] = sparse_assessment

            # provenance_main_integration_37108
            # Reuse existing explanation evidence and registry records.
            # Provenance remains observational and non-authorizing.
            from backend.server.engine.semantic_intelligence_provenance_3710 import (
                associate_candidate_provenance,
                inventory_cross_intelligence_provenance,
                validate_provenance_consistency,
            )

            candidate_provenance = associate_candidate_provenance(
                candidate_index=index,
                original_candidate=candidate,
                evidence_association=evidence_association,
                evidence_registry=package["evidence_registry"],
            )

            if candidate_provenance["status"] == "invalid":
                raise RuntimeError(
                    "Candidate provenance association invalid: "
                    + str(candidate_provenance.get("reason"))
                )

            graph_section = entry.get("intelligence_graph")
            confidence_section = None
            if isinstance(graph_section, dict):
                confidence_section = graph_section.get(
                    "semantic_relationship_confidence_evidence"
                )

            provenance_sections = {
                "explainability": {
                    "evidence_ids": evidence_association["evidence_ids"]
                },
            }

            if "reasoning_intelligence" in entry:
                provenance_sections["reasoning_intelligence"] = entry[
                    "reasoning_intelligence"
                ]

            if "intelligence_graph" in entry:
                provenance_sections["intelligence_graph"] = graph_section

            if confidence_section is not None:
                if not isinstance(confidence_section, dict):
                    raise RuntimeError(
                        "Invalid confidence provenance section"
                    )
                provenance_sections["confidence_evidence"] = (
                    confidence_section
                )

            provenance_inventory = inventory_cross_intelligence_provenance(
                candidate_index=index,
                sections=provenance_sections,
            )

            if provenance_inventory["status"] == "invalid":
                raise RuntimeError(
                    "Cross-intelligence provenance inventory invalid: "
                    + str(provenance_inventory.get("reason"))
                )

            provenance_consistency = validate_provenance_consistency(
                candidate_index=index,
                candidate_provenance=candidate_provenance,
                evidence_association=evidence_association,
                cross_intelligence_provenance=provenance_inventory,
            )

            if provenance_consistency["status"] == "invalid":
                raise RuntimeError(
                    "Provenance consistency invalid: "
                    + str(provenance_consistency.get("reason"))
                )

            section["provenance"] = {
                "schema_version": "semantic_provenance_bundle_v1",
                "candidate": candidate_provenance,
                "cross_intelligence": provenance_inventory,
                "consistency": provenance_consistency,
                "independent_provenance_verified": False,
                "semantic_proof_certified": False,
                "scorer_decision_performed": False,
                "automatic_linking_authorized": False,
            }






            explanation_count += 1






            explanation_ids.extend(candidate_evidence_ids)













        except Exception as exc:






            explanation_errors += 1






            entry["explainability"] = {






                "status": "error",






                "error_type": type(exc).__name__,






                "candidate_index": index,






                "evidence_ids": [],






                "certified": False,






                "approved_link_target": False,






                "scorer_decision_performed": False,






            }













    package["intelligence_sources"]["explainability_intelligence"] = {






        "status": (






            "completed_with_errors" if explanation_errors






            else "explanations_completed"






            if explanation_count else "not_executed"






        ),






        "available": explanation_count > 0,






        "explanation_count": explanation_count,






        "error_count": explanation_errors,






        "evidence_ids": explanation_ids,






        "certified": False,






        "linking_decisions_performed": False,






    }




















    # Phase 3.6: advisory structural integrity, not semantic certification.






    integrity_results = []













    for entry in package["enriched_candidates"]:






        index = entry["candidate_index"]













        references = [






            evidence_id






            for evidence_id, record in package["evidence_registry"].items()






            if isinstance(record, dict)






            and record.get("candidate_index") == index






        ]













        try:






            integrity = validate_candidate_evidence_integrity(






                workspace_id=workspace_id,






                candidate_index=index,






                evidence_ids=references,






                evidence_registry=package["evidence_registry"],






            )













            if (






                not isinstance(integrity, dict)






                or integrity.get("workspace_id") != workspace_id






                or integrity.get("candidate_index") != index






                or integrity.get("status") not in (






                    "integrity_passed",






                    "integrity_failed",






                    "no_evidence",






                )






                or integrity.get("certified") is not False






                or integrity.get("semantic_certification_status")






                   != "not_performed"






                or integrity.get("linking_decision_performed") is not False






                or integrity.get("scorer_decision_performed") is not False






            ):






                raise RuntimeError("Invalid integrity response")













        except Exception as exc:






            integrity = {






                "status": "integrity_failed",






                "workspace_id": workspace_id,






                "candidate_index": index,






                "checked_count": 0,






                "failure_count": 1,






                "failures": [{






                    "reason": "integrity_validation_error",






                    "error_type": type(exc).__name__,






                }],






                "evidence_integrity_valid": False,






                "semantic_certification_status": "not_performed",






                "certified": False,






                "linking_decision_performed": False,






                "scorer_decision_performed": False,






            }













        section = entry.setdefault("evidence_certification", {})






        if not isinstance(section, dict):






            raise RuntimeError("Invalid evidence certification section")













        section.update(deepcopy(integrity))






        section["certification_performed"] = False



        # Phase 3.6: enforce per-candidate evidence eligibility.

        # Structural integrity is not authoritative certification.

        checked_records = integrity.get("checked_evidence", [])

        valid_checked = (

            isinstance(checked_records, list)

            and all(

                isinstance(item, dict)

                and isinstance(item.get("evidence_id"), str)

                and item.get("integrity_valid") is True

                and item.get("semantically_certified") is False

                for item in checked_records

            )

        )



        checked_ids = (

            [item["evidence_id"] for item in checked_records]

            if valid_checked else []

        )



        integrity_eligible = (

            integrity["status"] == "integrity_passed"

            and integrity.get("failure_count") == 0

            and integrity.get("checked_count") == len(references)

            and valid_checked

            and len(checked_ids) == len(set(checked_ids))

            and set(checked_ids) == set(references)

        )



        # Fail closed for any failed, empty or inconsistent report.

        if integrity_eligible:

            section["usable_evidence_ids"] = list(references)

            section["rejected_evidence_ids"] = []

            section["warnings"] = [

                "Structural integrity passed; semantic certification "

                "has not been performed."

            ]

        else:

            section["usable_evidence_ids"] = []

            section["rejected_evidence_ids"] = list(references)

            section["warnings"] = [

                "Evidence is not eligible for the Scorer: missing, "

                "failed or inconsistent integrity verification."

            ]

            if integrity["status"] == "integrity_passed":

                section["status"] = "integrity_failed"

                section["evidence_integrity_valid"] = False

                section["warnings"].append(

                    "Validator response did not establish full "

                    "candidate evidence coverage."

                )



        entry["scorer_readiness"] = {

            "ready": False,

            "reason": (

                "Evidence has structural integrity, but authoritative "

                "semantic certification and Scorer integration "

                "remain pending."

                if integrity_eligible else

                "Candidate evidence is absent or failed the "

                "integrity eligibility boundary."

            ),

        }








        # Aggregate the final enforced candidate status, not the
        # preliminary validator response.
        integrity_results.append(deepcopy(section))













    passed = sum(






        item["status"] == "integrity_passed"






        for item in integrity_results






    )






    failed = sum(






        item["status"] == "integrity_failed"






        for item in integrity_results






    )






    empty = sum(






        item["status"] == "no_evidence"






        for item in integrity_results






    )













    package["intelligence_sources"]["evidence_integrity"] = {






        "status": (






            "completed_with_failures"






            if failed else "validation_completed"






        ),






        "candidates_checked": len(integrity_results),






        "integrity_passed": passed,






        "integrity_failed": failed,






        "no_evidence": empty,






        "semantic_certification_status": "not_performed",






        "certified": False,






    }



















    # Phase 3.8: independent operational-health report.





    package["operational_health"] = assess_enricher_source_health(





        enrichment_package=package





    )











    enrich_canonical_concept_entities(package)






    enrich_phrase_aliases(package)
    validate_phrase_topic_intent(package)
    from backend.server.engine.semantic_phrase_topic_intent_interpreter import attach_selector_topic_intent_advisory
    attach_selector_topic_intent_advisory(enriched_candidates)
    from backend.server.engine.semantic_intelligence_semantic_relationship_enrichment import attach_provisional_semantic_relationships
    attach_provisional_semantic_relationships(enriched_candidates)
    from backend.server.engine.semantic_intelligence_graph_observation_376 import attach_provisional_graph_observations
    attach_provisional_graph_observations(enriched_candidates)

    # sparse_batch_integration_386b
    # Verify that every original selected candidate survived enrichment.
    # Prepare an advisory handoff, not an executable Scorer decision.
    from backend.server.engine.semantic_intelligence_sparse_38 import (
        validate_sparse_candidate_retention,
        prepare_sparse_scorer_handoff,
    )

    sparse_rows = package.get("enriched_candidates")

    if not isinstance(sparse_rows, list):
        raise RuntimeError("Sparse batch: enriched candidates missing")

    if len(sparse_rows) != len(selected_candidates):
        raise RuntimeError(
            "Sparse batch: selected/enriched candidate count mismatch"
        )

    sparse_assessments = []

    for sparse_index, sparse_entry in enumerate(sparse_rows):
        if (
            not isinstance(sparse_entry, dict)
            or sparse_entry.get("candidate_index") != sparse_index
            or sparse_entry.get("original_candidate")
            != selected_candidates[sparse_index]
        ):
            raise RuntimeError(
                "Sparse batch: candidate identity/order mismatch"
            )

        assessment = sparse_entry.get("sparse_intelligence")
        if not isinstance(assessment, dict):
            raise RuntimeError(
                "Sparse batch: missing candidate assessment at "
                + str(sparse_index)
            )

        sparse_assessments.append(assessment)

    sparse_retention = validate_sparse_candidate_retention(
        selected_candidates=selected_candidates,
        sparse_assessments=sparse_assessments,
    )

    if sparse_retention["status"] != "all_candidates_retained":
        raise RuntimeError(
            "Sparse batch retention invalid: "
            + str(sparse_retention.get("reason"))
        )

    sparse_handoff = prepare_sparse_scorer_handoff(
        selected_candidates=selected_candidates,
        sparse_assessments=sparse_assessments,
    )

    if sparse_handoff["status"] != "advisory_handoff_prepared":
        raise RuntimeError(
            "Sparse advisory handoff invalid: "
            + str(sparse_handoff.get("reason"))
        )

    if (
        sparse_handoff["candidate_count"] != len(selected_candidates)
        or sparse_retention["retained_count"] != len(selected_candidates)
        or [
            record["original_candidate"]
            for record in sparse_handoff["candidates"]
        ] != selected_candidates
    ):
        raise RuntimeError("Sparse batch: final handoff mismatch")

    package["sparse_candidate_retention"] = sparse_retention
    package["sparse_scorer_advisory_handoff"] = sparse_handoff

    return package




















__all__ = ["enrich_selected_phrase_candidates"]






