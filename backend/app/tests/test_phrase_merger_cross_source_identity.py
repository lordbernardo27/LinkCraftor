import unittest
from unittest.mock import patch

from backend.server.stores import phrase_merger


class TestPhraseMergerCrossSourceIdentity(unittest.TestCase):

    ARTICLE = (
        "Kidney disease requires monitoring. "
        "Kidney disease needs treatment."
    )
    PHRASE = "Kidney disease"

    def position(self, start):
        return {
            "literal_span_verified": True,
            "matched_occurrence": {
                "start": start,
                "end": start + len(self.PHRASE),
            },
            "first_position": start,
            "all_positions": [start],
            "occurrence_count": 1,
        }

    def merge(self, extractor_start, discovery_start):
        extractor = {
            "phrase": self.PHRASE,
            "doc_id": "doc_test",
            "candidate_id": "extractor_101",
            "phrase_id": "extractor_phrase_1",
            "source_version": "v3",
            "source_hash": "hash_A",
            "paragraph_context": "Extractor paragraph",
        }

        discovery = {
            "phrase": self.PHRASE,
            "doc_id": "doc_test",
            "candidate_id": "discovery_205",
            "phrase_id": "discovery_phrase_1",
            "source_version": "v7",
            "source_hash": "hash_B",
            "paragraph_context": "Discovery paragraph",
            "discovery_context_tag": "discovery_only",
        }

        with (
            patch.object(
                phrase_merger,
                "_recover_extractor_occurrence",
                return_value=self.position(extractor_start),
            ),
            patch.object(
                phrase_merger,
                "_recover_discovery_occurrence",
                return_value=self.position(discovery_start),
            ),
        ):
            return phrase_merger.merge_phrase_candidates(
                text=self.ARTICLE,
                extractor_candidates=[extractor],
                discovery_candidates=[discovery],
                document_id="doc_test",
            )

    def test_exact_overlap_preserves_both_sources(self):
        records = self.merge(0, 0)

        self.assertEqual(len(records), 1)
        candidate = records[0]
        intelligence = candidate["merger_intelligence"]

        self.assertTrue(intelligence["merged_cross_source"])
        self.assertEqual(
            candidate["provenance"],
            ["smart_phrase_extractor", "phrase_discovery"],
        )

        metadata = intelligence["source_metadata"]

        extractor = metadata["smart_phrase_extractor"]
        discovery = metadata["phrase_discovery"]

        self.assertEqual(extractor["candidate_id"], "extractor_101")
        self.assertEqual(discovery["candidate_id"], "discovery_205")

        self.assertEqual(extractor["phrase_id"], "extractor_phrase_1")
        self.assertEqual(discovery["phrase_id"], "discovery_phrase_1")

        self.assertEqual(extractor["source_version"], "v3")
        self.assertEqual(discovery["source_version"], "v7")

        self.assertEqual(extractor["source_hash"], "hash_A")
        self.assertEqual(discovery["source_hash"], "hash_B")

        self.assertEqual(
            extractor["paragraph_context"],
            "Extractor paragraph",
        )
        self.assertEqual(
            discovery["paragraph_context"],
            "Discovery paragraph",
        )

        self.assertEqual(candidate["candidate_id"], "extractor_101")
        self.assertEqual(
            candidate["discovery_context_tag"],
            "discovery_only",
        )

        positions = intelligence["source_position_intelligence"]

        self.assertEqual(
            positions["smart_phrase_extractor"]["matched_occurrence"]["start"],
            0,
        )
        self.assertEqual(
            positions["phrase_discovery"]["matched_occurrence"]["start"],
            0,
        )

    def test_different_occurrences_remain_separate(self):
        second_start = self.ARTICLE.find(self.PHRASE, 1)
        self.assertGreater(second_start, 0)

        records = self.merge(0, second_start)

        self.assertEqual(len(records), 2)
        self.assertFalse(any(
            record["merger_intelligence"]["merged_cross_source"]
            for record in records
        ))


if __name__ == "__main__":
    unittest.main()
