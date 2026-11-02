"""Regression checks for PDF replacements and curated paper metadata."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import build_paper_index as builder


class PaperUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pdf = self.root / "Example- A Paper.pdf"
        self.pdf.write_bytes(b"replacement PDF")
        self.entry = {
            "id": "stable-paper-id",
            "title": "Example: A Paper",
            "authors": ["Tin Cheuk Leung", "Koleman Strumpf"],
            "year": 2026,
            "date": "October 2026",
            "type": "working_paper",
            "pdf_path": "/Example-%20A%20Paper.pdf",
            "external_url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5853062",
            "abstract": "Exact curated abstract, including punctuation.",
            "abstract_source": "manual",
            "fulltext_hash": "old-hash",
            "fulltext_excerpt": "Obsolete PDF text",
            "featured": True,
            "featured_order": 3,
            "slides": {"label": "Slides", "url": "/slides/new.pdf"},
            "coauthors": [{"name": "Koleman Strumpf", "url": "https://users.wfu.edu/strumpks/"}],
        }
        self.text = "Abstract\nExtracted abstract that must not replace the curated version.\n" + "Main text. " * 500
        self.text += "\nA late-page searchable result after the old excerpt limit."
        self.cache = {self.entry["id"]: {"fulltext_hash": "old-hash", "fulltext": "Obsolete PDF text"}}
        for name, value in [("ROOT", self.root), ("PAPER_DIRS", {"working_paper": self.root})]:
            patcher = patch.object(builder, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def update(self, refresh=False):
        with patch.object(builder, "read_pdf_text", return_value=self.text) as read, patch.object(
            builder, "infer_year_from_pdf_metadata", return_value=2026
        ):
            result = builder.update_entries_for_type("working_paper", [self.entry], refresh, self.cache)
        return result, read

    def test_replacement_preserves_curated_fields_and_indexes_complete_text(self):
        curated = {key: self.entry[key] for key in (
            "id", "title", "authors", "date", "external_url", "abstract", "abstract_source",
            "slides", "featured", "featured_order", "coauthors",
        )}
        self.entry = builder.ensure_schema([self.entry], "working_paper")[0]
        result, read = self.update()
        self.assertEqual(result["unmatched"], [])
        self.assertEqual(result["updated"], 1)
        read.assert_called_once_with(self.pdf)
        for key, value in curated.items():
            self.assertEqual(self.entry[key], value)
        self.assertEqual(self.entry["fulltext_hash"], builder.sha256_file(self.pdf))
        self.assertNotIn("late-page", self.entry["fulltext_excerpt"])
        row = builder.build_search_index([self.entry], self.cache)[0]
        for query in ["October 2026", "Koleman Strumpf", "Exact curated abstract", "late-page searchable result"]:
            self.assertIn(query, row["searchable_text"])
        self.assertNotIn("Obsolete PDF text", row["searchable_text"])

        # Simulate reloading the generated cache on a subsequent unchanged run.
        self.cache = {row["id"]: json.loads(json.dumps(row))}
        result, read = self.update()
        read.assert_not_called()
        self.assertEqual(result["updated"], 0)
        self.assertEqual(builder.build_search_index([self.entry], self.cache), [row])

        result, read = self.update(refresh=True)
        read.assert_called_once_with(self.pdf)
        self.assertEqual(self.entry["abstract"], curated["abstract"])
        self.assertEqual(builder.build_search_index([self.entry], self.cache), [row])

    def test_retained_old_version_does_not_replace_selected_pdf(self):
        (self.root / "Old title.pdf").write_bytes(b"old version")
        self.entry["previous_title"] = "Old title"
        result, read = self.update()
        read.assert_called_once_with(self.pdf)
        self.assertEqual(result["unmatched"], [])
        self.assertEqual(self.entry["pdf_path"], "/Example-%20A%20Paper.pdf")

    def test_stale_fulltext_cache_is_not_used(self):
        self.entry["fulltext_hash"] = "new-hash"
        row = builder.build_search_index([self.entry], self.cache)[0]
        self.assertNotIn("fulltext", row)

    def test_automatic_abstracts_still_refresh(self):
        self.entry.pop("abstract_source")
        with patch.object(builder, "extract_abstract", return_value="Updated automatic abstract"):
            self.update()
        self.assertEqual(self.entry["abstract"], "Updated automatic abstract")


if __name__ == "__main__":
    unittest.main()
