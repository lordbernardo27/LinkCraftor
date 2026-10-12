import unittest

from backend.server.stores.highlight_selection_engine import (
    select_highlight_candidates,
)


class TestHighlightSelectionOccurrences(unittest.TestCase):

    ARTICLE = (
        "Kidney disease may progress. "
        "Kidney disease needs care."
    )
    PHRASE = "Kidney disease"

    def candidate(self, start, **metadata):
        return {
            "phrase": self.PHRASE,
            "position_intelligence": {
                "literal_span_verified": True,
                "matched_occurrence": {
                    "start": start,
                    "end": start + len(self.PHRASE),
                },
            },
            **metadata,
        }

    def run_selector(self, article, items):
        return select_highlight_candidates(
            workspace_id="ws_occurrence_test",
            doc_id="doc_occurrence_test",
            article_text=article,
            phrase_candidates=items,
            resolved_targets=None,
        )["selected"]

    def starts(self):
        first = self.ARTICLE.find(self.PHRASE)
        second = self.ARTICLE.find(
            self.PHRASE, first + len(self.PHRASE)
        )
        return first, second

    def test_distinct_occurrences_have_distinct_ids(self):
        first, second = self.starts()
        selected = self.run_selector(
            self.ARTICLE,
            [self.candidate(first), self.candidate(second)],
        )
        self.assertEqual(len(selected), 2)
        self.assertEqual(
            len({x["selection_phrase_id"] for x in selected}), 1
        )
        self.assertEqual(
            len({x["selection_occurrence_id"] for x in selected}), 2
        )
        self.assertEqual(
            {x["first_position"] for x in selected},
            {first, second},
        )

    def test_ids_are_deterministic_across_input_order(self):
        first, second = self.starts()
        forward = self.run_selector(
            self.ARTICLE,
            [self.candidate(first), self.candidate(second)],
        )
        reverse = self.run_selector(
            self.ARTICLE,
            [self.candidate(second), self.candidate(first)],
        )
        def identities(items):
            return {
                x["position_intelligence"]["matched_occurrence"]["start"]:
                x["selection_occurrence_id"]
                for x in items
            }
        self.assertEqual(identities(forward), identities(reverse))

    def test_duplicate_occurrence_is_removed(self):
        first, second = self.starts()
        selected = self.run_selector(
            self.ARTICLE,
            [
                self.candidate(first),
                self.candidate(first),
                self.candidate(second),
            ],
        )
        self.assertEqual(len(selected), 2)

    def test_upstream_identifiers_are_preserved(self):
        first, _ = self.starts()
        selected = self.run_selector(
            self.ARTICLE,
            [self.candidate(
                first,
                phrase_id="upstream_phrase_1",
                candidate_id="upstream_candidate_1",
                occurrence_id="upstream_occurrence_1",
                source_version="v7",
                source_hash="upstream_hash",
            )],
        )
        self.assertEqual(len(selected), 1)
        item = selected[0]
        self.assertEqual(item["phrase_id"], "upstream_phrase_1")
        self.assertEqual(item["candidate_id"], "upstream_candidate_1")
        self.assertEqual(item["occurrence_id"], "upstream_occurrence_1")
        self.assertEqual(item["source_version"], "v7")
        self.assertEqual(item["source_hash"], "upstream_hash")
        self.assertTrue(item["selection_phrase_id"])
        self.assertTrue(item["selection_occurrence_id"])

    def test_content_change_changes_occurrence_id(self):
        first, _ = self.starts()
        changed = self.ARTICLE.replace(
            "may progress", "can progress"
        )
        original = self.run_selector(
            self.ARTICLE, [self.candidate(first)]
        )[0]
        revised = self.run_selector(
            changed, [self.candidate(first)]
        )[0]
        self.assertEqual(
            original["selection_phrase_id"],
            revised["selection_phrase_id"],
        )
        self.assertNotEqual(
            original["selection_occurrence_id"],
            revised["selection_occurrence_id"],
        )

    def test_unlocated_phrase_identity_is_deterministic(self):
        items = [{"phrase": self.PHRASE}]
        first = self.run_selector(self.ARTICLE, items)
        second = self.run_selector(self.ARTICLE, items)
        self.assertEqual(len(first), 1)
        self.assertEqual(
            first[0]["selection_occurrence_id"],
            second[0]["selection_occurrence_id"],
        )


if __name__ == "__main__":
    unittest.main()
