"""Regression tests for scripts.check_wiki."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import check_wiki


VALID_FRONTMATTER = """---
title: Example
type: concept
created: 2026-09-18
updated: 2026-09-18
sources: []
tags: []
---
# Example
"""


class CheckFrontmatterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.wiki = self.root / "wiki"
        self.entity_dir = self.wiki / "concepts"
        self.entity_dir.mkdir(parents=True)
        self.root_patch = mock.patch.object(check_wiki, "ROOT", self.root)
        self.wiki_patch = mock.patch.object(check_wiki, "WIKI", self.wiki)
        self.root_patch.start()
        self.wiki_patch.start()

    def tearDown(self) -> None:
        self.wiki_patch.stop()
        self.root_patch.stop()
        self.temp_dir.cleanup()

    def write_page(self, content: str) -> Path:
        path = self.entity_dir / "example.md"
        path.write_text(content, encoding="utf-8")
        return path

    def test_accepts_complete_frontmatter(self) -> None:
        errors: list[str] = []
        check_wiki.check_frontmatter(self.write_page(VALID_FRONTMATTER), errors)
        self.assertEqual(errors, [])

    def test_rejects_unclosed_frontmatter(self) -> None:
        errors: list[str] = []
        malformed = VALID_FRONTMATTER.rsplit("---\n", 1)[0]
        check_wiki.check_frontmatter(self.write_page(malformed), errors)
        self.assertEqual(
            errors,
            ["wiki/concepts/example.md: unclosed YAML frontmatter"],
        )

    def test_rejects_missing_required_field(self) -> None:
        errors: list[str] = []
        missing_tags = VALID_FRONTMATTER.replace("tags: []\n", "")
        check_wiki.check_frontmatter(self.write_page(missing_tags), errors)
        self.assertEqual(
            errors,
            ["wiki/concepts/example.md: missing fields tags"],
        )


class CheckLinksTests(unittest.TestCase):
    def test_ignores_example_links_inside_code(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = root / "page.md"
            path.write_text(
                "`[[missing-inline]]`\n\n```markdown\n[[missing-fenced]]\n```\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            with mock.patch.object(check_wiki, "ROOT", root):
                check_wiki.check_links(path, set(), errors)
            self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
