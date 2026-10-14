import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from catalog import ROOT, check, load, render, validate


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.data = load(ROOT)

    def test_seed_and_generated_pages(self):
        validate(self.data)
        check(ROOT, render(self.data))

    def test_unread_source_cannot_support_claim(self):
        self.data["theories"]["dashui"]["claims"] = [{"text": "unsupported", "source_ids": ["dashui-video"], "attribution": "secondary_summary"}]
        with self.assertRaisesRegex(AssertionError, "Unread source"):
            validate(self.data)

    def test_failed_query_cannot_be_complete(self):
        run = next(iter(self.data["runs"].values()))
        run["status"] = "complete"
        with self.assertRaisesRegex(AssertionError, "Complete run"):
            validate(self.data)

    def test_no_increment_still_generates_a_report(self):
        self.data["events"] = {}
        for run in self.data["runs"].values():
            run["event_ids"] = []
        validate(self.data)
        page = render(self.data)["daily/2026/2026-10-13.md"]
        self.assertIn("未登记内容增量", page)
        self.assertIn("检索记录", page)

    def test_duplicate_snapshot_is_rejected(self):
        duplicate = copy.deepcopy(next(iter(self.data["sources"].values())))
        duplicate["id"] = "duplicate"
        self.data["sources"]["duplicate"] = duplicate
        with self.assertRaisesRegex(AssertionError, "Duplicate source"):
            validate(self.data)

    def test_secondary_is_not_original_author(self):
        claim = self.data["theories"]["huangmao"]["claims"][0]
        claim["attribution"] = "author_statement"
        with self.assertRaisesRegex(AssertionError, "Secondary source"):
            validate(self.data)

    def test_broken_run_event_reference_is_rejected(self):
        run = next(iter(self.data["runs"].values()))
        run["event_ids"] = []
        with self.assertRaisesRegex(AssertionError, "Broken run/event"):
            validate(self.data)


if __name__ == "__main__":
    unittest.main()
