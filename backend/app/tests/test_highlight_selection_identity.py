import unittest
from backend.server.stores.highlight_selection_engine import select_highlight_candidates


class TestHighlightSelectionIdentity(unittest.TestCase):

    def run_selector(self, candidates):
        return select_highlight_candidates(
            workspace_id="ws_test",
            doc_id="doc_test",
            article_text="Kidney health matters. Blood pressure matters.",
            phrase_candidates=candidates,
            resolved_targets=None,
        )

    def test_missing_identities_assigned(self):
        result = self.run_selector([{"phrase": "Kidney health"}])
        self.assertEqual(len(result["selected"]), 1)
        self.assertEqual(result["selected"][0]["workspace_id"], "ws_test")
        self.assertEqual(result["selected"][0]["doc_id"], "doc_test")

    def test_matching_identities_accepted(self):
        result = self.run_selector([{
            "phrase": "Kidney health",
            "workspace_id": "ws_test",
            "doc_id": "doc_test",
        }])
        self.assertEqual(len(result["selected"]), 1)

    def test_wrong_workspace_rejected(self):
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            self.run_selector([{"phrase": "Kidney health", "workspace_id": "wrong"}])

    def test_wrong_document_rejected(self):
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            self.run_selector([{"phrase": "Kidney health", "doc_id": "wrong"}])

    def test_duplicate_wrong_workspace_rejected(self):
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            self.run_selector([
                {"phrase": "Kidney health"},
                {"phrase": "Kidney health", "workspace_id": "wrong"},
            ])

    def test_duplicate_wrong_document_rejected(self):
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            self.run_selector([
                {"phrase": "Kidney health"},
                {"phrase": "Kidney health", "doc_id": "wrong"},
            ])

    def test_empty_phrase_wrong_document_rejected(self):
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            self.run_selector([{"phrase": "", "doc_id": "wrong"}])

    def test_empty_phrase_wrong_workspace_rejected(self):
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            self.run_selector([{"phrase": "", "workspace_id": "wrong"}])


if __name__ == "__main__":
    unittest.main()
