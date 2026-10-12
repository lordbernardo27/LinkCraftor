import unittest

from backend.server.stores.highlight_selection_engine import (
    select_highlight_candidates,
)


class TestHighlightSelectionSentenceContext(unittest.TestCase):

    PHRASE = "kidney disease"

    def candidate(self, phrase, start, verified=True):
        return {
            "phrase": phrase,
            "position_intelligence": {
                "literal_span_verified": verified,
                "matched_occurrence": {
                    "start": start,
                    "end": start + len(phrase),
                },
            },
        }

    def select(self, article, candidates):
        return select_highlight_candidates(
            workspace_id="ws_sentence",
            doc_id="doc_sentence",
            article_text=article,
            phrase_candidates=candidates,
            resolved_targets=None,
        )["selected"]

    def test_repeated_phrase_gets_correct_individual_sentence(self):
        article = (
            "Kidney disease requires monitoring. "
            "Early treatment slows kidney disease progression."
        )

        first = article.casefold().find(self.PHRASE)
        second = article.casefold().find(self.PHRASE, first + 1)

        selected = self.select(article, [
            self.candidate(self.PHRASE, first),
            self.candidate(self.PHRASE, second),
        ])

        self.assertEqual(len(selected), 2)

        by_position = {
            item["selection_source_span"]["start"]: item
            for item in selected
        }

        self.assertEqual(
            by_position[first]["selection_sentence_context"]["text"],
            "Kidney disease requires monitoring.",
        )
        self.assertEqual(
            by_position[second]["selection_sentence_context"]["text"],
            "Early treatment slows kidney disease progression.",
        )

    def test_sentence_offsets_match_original_article(self):
        article = (
            "  Kidney disease requires monitoring.\n"
            "Kidney disease needs treatment."
        )

        start = article.find("Kidney disease")

        selected = self.select(
            article,
            [self.candidate(self.PHRASE, start)],
        )

        self.assertEqual(len(selected), 1)

        context = selected[0]["selection_sentence_context"]

        self.assertEqual(context["start"], start)
        self.assertEqual(
            article[context["start"]:context["end"]],
            context["text"],
        )
        self.assertEqual(
            context["coordinate_space"],
            "original_article",
        )

    def test_common_title_abbreviation_does_not_split_sentence(self):
        article = (
            "Dr. Mensah treated kidney disease. "
            "Patients recovered."
        )

        start = article.find(self.PHRASE)

        selected = self.select(
            article,
            [self.candidate(self.PHRASE, start)],
        )

        self.assertEqual(
            selected[0]["selection_sentence_context"]["text"],
            "Dr. Mensah treated kidney disease.",
        )

    def test_two_occurrences_in_one_sentence_share_context(self):
        article = (
            "Kidney disease and kidney disease require monitoring."
        )

        first = article.casefold().find(self.PHRASE)
        second = article.casefold().find(self.PHRASE, first + 1)

        selected = self.select(article, [
            self.candidate(self.PHRASE, first),
            self.candidate(self.PHRASE, second),
        ])

        self.assertEqual(len(selected), 2)

        self.assertEqual(
            {
                item["selection_sentence_context"]["text"]
                for item in selected
            },
            {article},
        )

        self.assertEqual(
            len({
                item["selection_occurrence_id"]
                for item in selected
            }),
            2,
        )

    def test_unverified_source_has_no_certified_context(self):
        article = "Kidney disease requires monitoring."

        selected = self.select(article, [
            self.candidate(self.PHRASE, 0, verified=False),
        ])

        self.assertEqual(len(selected), 1)
        self.assertIsNone(
            selected[0]["selection_sentence_context"]
        )
        self.assertEqual(
            selected[0]["selection_sentence_context_status"],
            "unverified",
        )

    def test_invalid_offset_has_no_sentence_context(self):
        article = "Kidney disease requires monitoring."

        selected = self.select(article, [
            self.candidate(self.PHRASE, 1),
        ])

        self.assertEqual(len(selected), 1)
        self.assertIsNone(
            selected[0]["selection_sentence_context"]
        )

    def test_upstream_sentence_context_is_not_overwritten(self):
        article = "Kidney disease requires monitoring."

        candidate = self.candidate(self.PHRASE, 0)
        candidate["sentence_context"] = "Original upstream context"
        candidate["source_hash"] = "original_hash"

        selected = self.select(article, [candidate])

        self.assertEqual(len(selected), 1)

        item = selected[0]

        self.assertEqual(
            item["sentence_context"],
            "Original upstream context",
        )
        self.assertEqual(
            item["source_hash"],
            "original_hash",
        )
        self.assertEqual(
            item["selection_sentence_context"]["text"],
            article,
        )
        self.assertEqual(
            item["selection_sentence_context_status"],
            "derived_from_verified_span",
        )

    def test_sentence_without_terminal_punctuation(self):
        article = "Kidney disease requires monitoring"

        selected = self.select(article, [
            self.candidate(self.PHRASE, 0),
        ])

        self.assertEqual(len(selected), 1)
        self.assertEqual(
            selected[0]["selection_sentence_context"]["text"],
            article,
        )


if __name__ == "__main__":
    unittest.main()
