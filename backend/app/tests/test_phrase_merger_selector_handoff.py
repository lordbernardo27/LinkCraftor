import unittest
from unittest.mock import patch

from backend.server.stores import phrase_merger
from backend.server.stores.highlight_selection_engine import (
    select_highlight_candidates,
)


class TestPhraseMergerSelectorHandoff(unittest.TestCase):

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

    def run_pipeline(self, extractor_start, discovery_start):
        extractor = {
            "phrase": self.PHRASE,
            "workspace_id": "ws_handoff",
            "doc_id": "doc_handoff",
            "candidate_id": "extractor_101",
            "phrase_id": "extractor_phrase_1",
            "source_version": "extractor_v3",
            "source_hash": "extractor_hash",
            "paragraph_context": "Extractor paragraph",
        }

        discovery = {
            "phrase": self.PHRASE,
            "workspace_id": "ws_handoff",
            "doc_id": "doc_handoff",
            "candidate_id": "discovery_205",
            "phrase_id": "discovery_phrase_1",
            "source_version": "discovery_v7",
            "source_hash": "discovery_hash",
            "paragraph_context": "Discovery paragraph",
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
            merged = phrase_merger.merge_phrase_candidates(
                text=self.ARTICLE,
                extractor_candidates=[extractor],
                discovery_candidates=[discovery],
                document_id="doc_handoff",
            )

        selected = select_highlight_candidates(
            workspace_id="ws_handoff",
            doc_id="doc_handoff",
            article_text=self.ARTICLE,
            phrase_candidates=merged,
            resolved_targets=None,
        )["selected"]

        return merged, selected

    def test_exact_overlap_survives_merger_and_selector(self):
        merged, selected = self.run_pipeline(0, 0)

        self.assertEqual(len(merged), 1)
        self.assertEqual(len(selected), 1)

        candidate = selected[0]
        intelligence = candidate["merger_intelligence"]

        self.assertTrue(intelligence["merged_cross_source"])
        self.assertEqual(
            candidate["provenance"],
            ["smart_phrase_extractor", "phrase_discovery"],
        )

        sources = intelligence["source_metadata"]

        self.assertEqual(
            sources["smart_phrase_extractor"]["candidate_id"],
            "extractor_101",
        )
        self.assertEqual(
            sources["phrase_discovery"]["candidate_id"],
            "discovery_205",
        )

        self.assertEqual(
            sources["smart_phrase_extractor"]["source_hash"],
            "extractor_hash",
        )
        self.assertEqual(
            sources["phrase_discovery"]["source_hash"],
            "discovery_hash",
        )

        self.assertEqual(
            sources["smart_phrase_extractor"]["source_version"],
            "extractor_v3",
        )
        self.assertEqual(
            sources["phrase_discovery"]["source_version"],
            "discovery_v7",
        )

        self.assertEqual(
            sources["smart_phrase_extractor"]["paragraph_context"],
            "Extractor paragraph",
        )
        self.assertEqual(
            sources["phrase_discovery"]["paragraph_context"],
            "Discovery paragraph",
        )

        positions = intelligence["source_position_intelligence"]

        self.assertEqual(
            positions["smart_phrase_extractor"]
            ["matched_occurrence"]["start"],
            0,
        )
        self.assertEqual(
            positions["phrase_discovery"]
            ["matched_occurrence"]["start"],
            0,
        )

        self.assertEqual(candidate["first_position"], 0)
        self.assertEqual(candidate["workspace_id"], "ws_handoff")
        self.assertEqual(candidate["doc_id"], "doc_handoff")
        self.assertTrue(
            candidate["selection_phrase_id"].startswith("sp_")
        )
        self.assertTrue(
            candidate["selection_occurrence_id"].startswith("so_")
        )

    def test_different_occurrences_survive_handoff(self):
        second_start = self.ARTICLE.find(self.PHRASE, 1)
        self.assertGreater(second_start, 0)

        merged, selected = self.run_pipeline(0, second_start)

        self.assertEqual(len(merged), 2)
        self.assertEqual(len(selected), 2)

        self.assertEqual(
            {candidate["first_position"] for candidate in selected},
            {0, second_start},
        )

        self.assertEqual(
            len({
                candidate["selection_phrase_id"]
                for candidate in selected
            }),
            1,
        )

        self.assertEqual(
            len({
                candidate["selection_occurrence_id"]
                for candidate in selected
            }),
            2,
        )

        self.assertEqual(
            {
                tuple(candidate["provenance"])
                for candidate in selected
            },
            {
                ("smart_phrase_extractor",),
                ("phrase_discovery",),
            },
        )


if __name__ == "__main__":
    unittest.main()
