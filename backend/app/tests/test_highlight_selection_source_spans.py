import unittest

from backend.server.stores.highlight_selection_engine import (
    select_highlight_candidates,
)


class TestHighlightSelectionSourceSpans(unittest.TestCase):

    ARTICLE = (
        "  Kidney disease requires monitoring.\n"
        "Kidney disease needs treatment."
    )
    PHRASE = "Kidney disease"

    def candidate(self, start, end=None, verified=True):
        if end is None:
            end = start + len(self.PHRASE)

        return {
            "phrase": self.PHRASE,
            "position_intelligence": {
                "literal_span_verified": verified,
                "matched_occurrence": {
                    "start": start,
                    "end": end,
                },
            },
        }

    def select(self, candidates, article=None):
        return select_highlight_candidates(
            workspace_id="ws_span_test",
            doc_id="doc_span_test",
            article_text=article if article is not None else self.ARTICLE,
            phrase_candidates=candidates,
            resolved_targets=None,
        )["selected"]

    def starts(self):
        first = self.ARTICLE.find(self.PHRASE)
        second = self.ARTICLE.find(
            self.PHRASE,
            first + len(self.PHRASE),
        )
        return first, second

    def test_two_verified_original_occurrences(self):
        first, second = self.starts()

        selected = self.select([
            self.candidate(first),
            self.candidate(second),
        ])

        self.assertEqual(len(selected), 2)

        spans = {
            item["selection_source_span"]["start"]:
            item["selection_source_span"]
            for item in selected
        }

        self.assertEqual(set(spans), {first, second})

        for start, span in spans.items():
            self.assertEqual(
                span["end"],
                start + len(self.PHRASE),
            )
            self.assertEqual(
                span["coordinate_space"],
                "original_article",
            )
            self.assertEqual(
                span["text"],
                self.ARTICLE[start:span["end"]],
            )

        self.assertTrue(all(
            item["selection_source_span_status"] == "verified"
            for item in selected
        ))

    def test_original_and_normalized_coordinates_are_distinct(self):
        first, _ = self.starts()

        selected = self.select([self.candidate(first)])
        self.assertEqual(len(selected), 1)

        item = selected[0]

        self.assertEqual(
            item["selection_source_span"]["start"],
            first,
        )
        self.assertNotEqual(
            item["first_position"],
            first,
        )
        self.assertEqual(
            item["selection_position_intelligence"]["coordinate_space"],
            "normalized_article",
        )
        self.assertEqual(
            item["selection_source_span"]["coordinate_space"],
            "original_article",
        )

    def test_invalid_claimed_span_is_unverified(self):
        first, _ = self.starts()

        selected = self.select([
            self.candidate(first + 1),
        ])

        self.assertEqual(len(selected), 1)
        self.assertIsNone(
            selected[0]["selection_source_span"]
        )
        self.assertEqual(
            selected[0]["selection_source_span_status"],
            "unverified",
        )

    def test_unverified_upstream_span_is_not_certified(self):
        first, _ = self.starts()

        selected = self.select([
            self.candidate(first, verified=False),
        ])

        self.assertEqual(len(selected), 1)
        self.assertIsNone(
            selected[0]["selection_source_span"]
        )
        self.assertEqual(
            selected[0]["selection_source_span_status"],
            "unverified",
        )

    def test_unlocated_candidate_has_no_invented_span(self):
        selected = self.select([
            {"phrase": self.PHRASE},
        ])

        self.assertEqual(len(selected), 1)
        self.assertIsNone(
            selected[0]["selection_source_span"]
        )
        self.assertEqual(
            selected[0]["selection_source_span_status"],
            "unverified",
        )

    def test_original_capitalization_and_upstream_data_survive(self):
        article = "Kidney Disease requires monitoring."
        phrase = "kidney disease"

        original_position = {
            "literal_span_verified": True,
            "matched_occurrence": {
                "start": 0,
                "end": len(phrase),
            },
        }

        selected = self.select(
            [{
                "phrase": phrase,
                "position_intelligence": original_position,
                "candidate_id": "upstream_candidate_1",
                "source_hash": "upstream_hash_1",
            }],
            article=article,
        )

        self.assertEqual(len(selected), 1)
        item = selected[0]

        self.assertEqual(
            item["selection_source_span"]["text"],
            "Kidney Disease",
        )
        self.assertEqual(
            item["selection_source_span_status"],
            "verified",
        )
        self.assertEqual(
            item["position_intelligence"],
            original_position,
        )
        self.assertEqual(
            item["candidate_id"],
            "upstream_candidate_1",
        )
        self.assertEqual(
            item["source_hash"],
            "upstream_hash_1",
        )


if __name__ == "__main__":
    unittest.main()
