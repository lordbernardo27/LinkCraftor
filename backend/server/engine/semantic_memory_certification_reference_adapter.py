




"""Read-only Phase 3.6 canonical reference consistency checks.









This does not authenticate the issuing authority, workspace binding,




operational-to-canonical mapping, or revocation state.




"""









from __future__ import annotations









from copy import deepcopy




import hashlib




import hmac




import json




import re




from typing import Any














def _digest(payload: dict[str, Any]) -> str:




    raw = json.dumps(




        payload, sort_keys=True,




        separators=(",", ":"), ensure_ascii=True,




    )




    return hashlib.sha256(raw.encode("utf-8")).hexdigest()














def inspect_semantic_memory_certification_reference(




    *,




    workspace_id: str,




    operational_memory_id: str,




    canonical_memory_object_id: str | None = None,




    certification_result: dict[str, Any] | None = None,




    final_package: dict[str, Any] | None = None,




    retrieval_bundle: dict[str, Any] | None = None,




) -> dict[str, Any]:




    result = {




        "status": "unverified",




        "workspace_id": workspace_id,




        "operational_memory_id": operational_memory_id,




        "canonical_memory_object_id": None,




        "reference_integrity_valid": False,




        "authority_verified": False,




        "certification_performed": False,




        "certified": False,




        "memory_is_certified_truth": False,




        "certification_reference": None,




        "certification_lineage": None,




        "reasons": [],




    }









    def reject(reason: str) -> dict[str, Any]:




        result["reasons"].append(reason)




        return deepcopy(result)









    if not isinstance(workspace_id, str) or not re.fullmatch(




        r"[A-Za-z0-9_-]+", workspace_id




    ):




        return reject("invalid_workspace_id")









    if not isinstance(operational_memory_id, str) or not (




        operational_memory_id.strip()




    ):




        return reject("missing_operational_memory_id")









    if not isinstance(canonical_memory_object_id, str) or not (




        re.fullmatch(




            r"semanticmemoryobject:v1:[a-f0-9]{64}",




            canonical_memory_object_id,




        )




    ):




        return reject("missing_trusted_identity_mapping")









    if not all(isinstance(item, dict) for item in (




        certification_result, final_package, retrieval_bundle




    )):




        return reject("missing_canonical_artifacts")









    if (




        certification_result.get("schema")




        != "full_semantic_memory_hard_certification_result_v1"




        or certification_result.get("status")




        != "FULL_SEMANTIC_MEMORY_HARD_CERTIFIED"




        or certification_result.get("certified") is not True




    ):




        return reject("invalid_certification_result_contract")









    if (




        final_package.get("schema")




        != "final_semantic_memory_package_v1"




        or retrieval_bundle.get("schema")




        != "semantic_memory_retrieval_read_contract_bundle_v1"




    ):




        return reject("invalid_canonical_package_schema")









    root = final_package.get("semantic_memory_lineage_root_id")




    package_id = final_package.get(




        "final_semantic_memory_package_id"




    )




    package_digest = final_package.get(




        "final_semantic_memory_package_digest"




    )




    contract_id = retrieval_bundle.get(




        "retrieval_contract_bundle_id"




    )









    if not all(isinstance(value, str) and value for value in (




        root, package_id, package_digest, contract_id




    )):




        return reject("missing_canonical_identity")









    if (




        certification_result.get("semantic_memory_lineage_root_id")




        != root




        or certification_result.get(




            "final_semantic_memory_package_id"




        ) != package_id




        or certification_result.get(




            "final_semantic_memory_package_digest"




        ) != package_digest




        or retrieval_bundle.get(




            "semantic_memory_lineage_root_id"




        ) != root




    ):




        return reject("cross_artifact_identity_mismatch")










    canonical_objects = final_package.get("final_memory_objects")
    explicit_ids = final_package.get("final_memory_object_ids")

    if canonical_objects is not None:
        if not isinstance(canonical_objects, (list, tuple)):
            return reject("invalid_final_memory_objects")

        ordered_final_ids = []

        for memory_object in canonical_objects:
            if not isinstance(memory_object, dict):
                return reject("invalid_final_memory_object")

            if memory_object.get("schema") != "semantic_memory_object_v1":
                return reject("invalid_final_memory_object")

            memory_id = memory_object.get("memory_object_id")

            if not isinstance(memory_id, str) or not memory_id:
                return reject("invalid_final_memory_object_id")

            ordered_final_ids.append(memory_id)

        if explicit_ids is not None:
            if not isinstance(explicit_ids, (list, tuple)):
                return reject("invalid_memory_partition_contract")

            if list(explicit_ids) != ordered_final_ids:
                return reject("final_memory_identity_mismatch")

    elif isinstance(explicit_ids, (list, tuple)):
        ordered_final_ids = list(explicit_ids)

    else:
        return reject("invalid_memory_partition_contract")

    if any(
        not isinstance(memory_id, str) or not memory_id
        for memory_id in ordered_final_ids
    ):
        return reject("invalid_final_memory_object_id")

    if len(set(ordered_final_ids)) != len(ordered_final_ids):
        return reject("duplicate_final_memory_object_id")

    fields = (









        "default_readable_memory_ids",




        "held_memory_ids",




        "blocked_memory_ids",




        "contested_memory_ids",




        "historical_memory_ids",




    )









    if any(




        not isinstance(final_package.get(field), (list, tuple))




        for field in fields




    ):




        return reject("invalid_memory_partition_contract")









    retrieval_ids = retrieval_bundle.get(




        "default_readable_memory_ids"




    )




    if not isinstance(retrieval_ids, (list, tuple)):




        return reject("invalid_retrieval_read_contract")









    try:




        partitions = [




            set(final_package[field]) for field in fields




        ]




        all_ids = set(ordered_final_ids)




        retrieval_set = set(retrieval_ids)




    except TypeError:




        return reject("malformed_partition_identifiers")









    for i, left in enumerate(partitions):




        for right in partitions[i + 1:]:




            if left & right:




                return reject("overlapping_memory_partitions")









    if (




        len(all_ids) != len(ordered_final_ids)




        or all_ids != set().union(*partitions)




        or partitions[0] != retrieval_set




    ):




        return reject("inconsistent_memory_partitions")









    if (




        canonical_memory_object_id not in all_ids




        or canonical_memory_object_id not in partitions[0]




    ):




        return reject("memory_not_canonically_default_readable")













    # Verify canonical 4.6.28K retrieval-contract identity.



    metadata_records = retrieval_bundle.get("retrieval_metadata_records")



    contract_digest = retrieval_bundle.get(



        "retrieval_contract_bundle_digest"



    )



    if not isinstance(metadata_records, (list, tuple)):



        return reject("missing_retrieval_metadata_records")



    if not isinstance(contract_digest, str):



        return reject("missing_retrieval_contract_digest")










    # Verify individual canonical metadata identities and bindings.


    metadata_payload_fields = (


        "memory_object_id",


        "memory_lineage_record_id",


        "retrieval_class",


        "default_runtime_readable",


        "memory_state",


        "stability_state",


        "retention_state",


        "current_version",


        "source_final_graph_id",


    )





    final_object_ids = set(ordered_final_ids)


    metadata_object_ids = set()





    for record in metadata_records:


        if not isinstance(record, dict):


            return reject("invalid_retrieval_metadata_record")





        if record.get("schema") != (


            "semantic_memory_retrieval_metadata_v1"


        ):


            return reject("invalid_retrieval_metadata_schema")





        if any(


            field not in record


            for field in metadata_payload_fields


        ):


            return reject("incomplete_retrieval_metadata_payload")





        memory_id = record["memory_object_id"]





        if not isinstance(memory_id, str):


            return reject("invalid_metadata_memory_object_id")





        if memory_id not in final_object_ids:


            return reject("metadata_memory_object_not_in_package")





        if memory_id in metadata_object_ids:


            return reject("duplicate_metadata_memory_object_id")





        metadata_object_ids.add(memory_id)





        readable = memory_id in partitions[0]





        if record["default_runtime_readable"] is not readable:


            return reject("metadata_default_readability_mismatch")





        if record.get(


            "explicit_state_aware_read_required"


        ) is not (not readable):


            return reject("metadata_state_aware_read_mismatch")







        expected_class_by_memory_id = {}



        class_partitions = {

            "default_readable_memory_ids": "ACTIVE_MEMORY",

            "held_memory_ids": "HELD_MEMORY",

            "blocked_memory_ids": "BLOCKED_MEMORY",

            "contested_memory_ids": "CONTESTED_MEMORY",

            "historical_memory_ids": "HISTORICAL_MEMORY",

        }



        for partition_name, class_name in class_partitions.items():

            for classified_memory_id in final_package[partition_name]:

                expected_class_by_memory_id[

                    classified_memory_id

                ] = class_name



        if record["retrieval_class"] != (

            expected_class_by_memory_id.get(memory_id)

        ):

            return reject("metadata_retrieval_class_mismatch")




        if record["source_final_graph_id"] != (


            final_package.get("source_final_graph_id")


        ):


            return reject("metadata_graph_lineage_mismatch")





        payload = {


            field: record[field]


            for field in metadata_payload_fields


        }





        try:


            expected_digest = _digest(payload)


        except (TypeError, ValueError):


            return reject("invalid_retrieval_metadata_payload")





        actual_digest = record.get("retrieval_metadata_digest")


        actual_id = record.get("retrieval_metadata_id")





        if not isinstance(actual_digest, str) or not isinstance(


            actual_id, str


        ):


            return reject("missing_retrieval_metadata_identity")





        if not (


            hmac.compare_digest(actual_digest, expected_digest)


            and hmac.compare_digest(


                actual_id,


                "semanticmemoryretrievalmetadata:v1:"


                + expected_digest,


            )


        ):


            return reject("retrieval_metadata_digest_mismatch")





    if metadata_object_ids != final_object_ids:


        return reject("incomplete_metadata_memory_coverage")





    metadata_ids = []



    for record in metadata_records:



        if not isinstance(record, dict):



            return reject("invalid_retrieval_metadata_record")



        metadata_id = record.get("retrieval_metadata_id")



        if not isinstance(metadata_id, str) or not metadata_id:



            return reject("invalid_retrieval_metadata_id")



        metadata_ids.append(metadata_id)







    if len(metadata_ids) != len(set(metadata_ids)):



        return reject("duplicate_retrieval_metadata_ids")







    for field in fields:



        if not isinstance(retrieval_bundle.get(field), (list, tuple)):



            return reject("invalid_retrieval_partition_contract")



        if list(retrieval_bundle[field]) != list(final_package[field]):



            return reject("retrieval_partition_mismatch")







    retrieval_payload = {



        "semantic_memory_lineage_root_id": root,



        "retrieval_metadata_ids": metadata_ids,



        **{



            field: list(retrieval_bundle[field])



            for field in fields



        },



    }



    expected_retrieval_digest = _digest(retrieval_payload)



    expected_retrieval_id = (



        "semanticmemoryretrievalcontractbundle:v1:"



        + expected_retrieval_digest



    )



    if not (



        hmac.compare_digest(



            contract_digest, expected_retrieval_digest



        )



        and hmac.compare_digest(



            contract_id, expected_retrieval_id



        )



    ):



        return reject("retrieval_contract_digest_mismatch")







    payload = {




        "semantic_memory_lineage_root_id": root,




        "final_memory_object_ids": list(ordered_final_ids),
        **{




            field: list(final_package[field])




            for field in fields




        },




        "source_learning_engine_package_id":




            final_package.get(




                "source_final_learning_engine_package_id"




            ),




        "source_final_graph_id":




            final_package.get("source_final_graph_id"),




        "retrieval_contract_bundle_id": contract_id,




    }









    try:
        expected_digest = _digest(payload)
    except (TypeError, ValueError):
        return reject("invalid_canonical_package_payload")









    if not (




        hmac.compare_digest(package_digest, expected_digest)




        and hmac.compare_digest(




            package_id,




            "finalsemanticmemory:v1:" + expected_digest,




        )




    ):




        return reject("canonical_package_digest_mismatch")









    result["status"] = "reference_consistent_authority_pending"




    result["canonical_memory_object_id"] = (




        canonical_memory_object_id




    )




    result["reference_integrity_valid"] = True




    result["certification_reference"] = {




        "final_semantic_memory_package_id": package_id,




        "final_semantic_memory_package_digest": package_digest,




        "retrieval_contract_bundle_id": contract_id,




    }




    result["certification_lineage"] = {




        "semantic_memory_lineage_root_id": root,




        "source_final_learning_engine_package_id":




            final_package.get(




                "source_final_learning_engine_package_id"




            ),




        "source_final_graph_id":




            final_package.get("source_final_graph_id"),




        "canonical_memory_object_id":




            canonical_memory_object_id,




    }




    result["reasons"] = [




        "Internal reference consistency only; authority, "




        "workspace and record binding, and revocation are unverified."




    ]




    return deepcopy(result)














__all__ = [




    "inspect_semantic_memory_certification_reference"




]
