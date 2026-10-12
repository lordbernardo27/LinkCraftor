import unittest

from backend.server.stores.highlight_selection_engine import (
    select_highlight_candidates,
)


class TestHighlightSelectionParagraphContext(unittest.TestCase):

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
            workspace_id="ws_paragraph",
            doc_id="doc_paragraph",
            article_text=article,
            phrase_candidates=candidates,
            resolved_targets=None,
        )["selected"]

    def test_repeated_phrase_in_separate_paragraphs(self):
        article = (
            "Kidney disease requires monitoring.\n\n"
            "Kidney disease requires treatment."
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
            by_position[first]["selection_paragraph_context"]["text"],
            "Kidney disease requires monitoring.",
        )
        self.assertEqual(
            by_position[second]["selection_paragraph_context"]["text"],
            "Kidney disease requires treatment.",
        )

    def test_single_line_break_stays_in_same_paragraph(self):
        article = (
            "Kidney disease is monitored\n"
            "with regular laboratory testing.\n\n"
            "Another paragraph follows."
        )

        selected = self.select(
            article,
            [self.candidate(self.PHRASE, 0)],
        )

        self.assertEqual(len(selected), 1)
        self.assertEqual(
            selected[0]["selection_paragraph_context"]["text"],
            "Kidney disease is monitored\n"
            "with regular laboratory testing.",
        )

    def test_crlf_and_whitespace_only_separator(self):
        article = (
            "Introduction.\r\n \r\n"
            "  Kidney disease needs monitoring.\r\n"
            "Follow-up is important.\r\n\r\n"
            "Conclusion."
        )

        start = article.find("Kidney disease")

        selected = self.select(
            article,
            [self.candidate(self.PHRASE, start)],
        )

        self.assertEqual(len(selected), 1)

        context = selected[0]["selection_paragraph_context"]

        self.assertEqual(
            context["text"],
            "Kidney disease needs monitoring.\r\n"
            "Follow-up is important.",
        )
        self.assertEqual(
            context["start"],
            start,
        )
        self.assertEqual(
            article[context["start"]:context["end"]],
            context["text"],
        )

    def test_two_occurrences_in_one_paragraph_share_context(self):
        article = (
            "Kidney disease and\n"
            "kidney disease require monitoring."
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
                item["selection_paragraph_context"]["text"]
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

    def test_upstream_paragraph_metadata_is_preserved(self):
        article = "Kidney disease requires monitoring."

        candidate = self.candidate(self.PHRASE, 0)
        candidate["paragraph_context"] = "Original upstream paragraph"
        candidate["source_version"] = "v7"
        candidate["source_hash"] = "hash_123"

        selected = self.select(article, [candidate])

        self.assertEqual(len(selected), 1)

        item = selected[0]

        self.assertEqual(
            item["paragraph_context"],
            "Original upstream paragraph",
        )
        self.assertEqual(item["source_version"], "v7")
        self.assertEqual(item["source_hash"], "hash_123")
        self.assertEqual(
            item["selection_paragraph_context"]["text"],
            article,
        )
        self.assertEqual(
            item["selection_paragraph_context_status"],
            "derived_from_verified_span",
        )

    def test_unverified_occurrence_has_no_derived_paragraph(self):
        article = "Kidney disease requires monitoring."

        selected = self.select(
            article,
            [self.candidate(self.PHRASE, 0, verified=False)],
        )

        self.assertEqual(len(selected), 1)
        self.assertIsNone(
            selected[0]["selection_paragraph_context"]
        )
        self.assertEqual(
            selected[0]["selection_paragraph_context_status"],
            "unverified",
        )

    def test_occurrence_crossing_paragraph_boundary_is_unresolved(self):
        article = "kidney\n\ndisease"
        phrase = article

        selected = self.select(
            article,
            [self.candidate(phrase, 0)],
        )

        self.assertEqual(len(selected), 1)
        self.assertEqual(
            selected[0]["selection_source_span_status"],
            "verified",
        )
        self.assertIsNone(
            selected[0]["selection_paragraph_context"]
        )
        self.assertEqual(
            selected[0]["selection_paragraph_context_status"],
            "unresolved_paragraph_boundary",
        )

    def test_leading_and_trailing_blank_lines(self):
        article = (
            " \n\n"
            "  Kidney disease needs monitoring.  "
            "\n\n "
        )

        start = article.find("Kidney disease")

        selected = self.select(
            article,
            [self.candidate(self.PHRASE, start)],
        )

        self.assertEqual(len(selected), 1)

        context = selected[0]["selection_paragraph_context"]

        self.assertEqual(context["start"], start)
        self.assertEqual(
            context["text"],
            "Kidney disease needs monitoring.",
        )
        self.assertEqual(
            article[context["start"]:context["end"]],
            context["text"],
        )


if __name__ == "__main__":
    unittest.main()
