"""Regression tests for scripts.check_wiki."""

from __future__ import annotations

import io
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

    def test_rejects_embedded_closing_delimiters(self) -> None:
        for delimiter in ("  ---\n", "value---\n", "--- extra\n", "----\n"):
            with self.subTest(delimiter=delimiter):
                content = VALID_FRONTMATTER.rsplit("---\n", 1)[0] + delimiter
                errors = []
                check_wiki.check_frontmatter(self.write_page(content), errors)
                self.assertEqual(errors, ["wiki/concepts/example.md: unclosed YAML frontmatter"])

    def test_accepts_standalone_delimiter_at_eof_and_crlf(self) -> None:
        for content in (VALID_FRONTMATTER.rsplit("---\n", 1)[0] + "---",
                        VALID_FRONTMATTER.replace("\n", "\r\n")):
            with self.subTest(content=content):
                errors = []
                check_wiki.check_frontmatter(self.write_page(content), errors)
                self.assertEqual(errors, [])

    def test_rejects_invalid_values(self) -> None:
        cases = {
            "title": ["", "null", "''", "'   '", "42", "[]"],
            "type": ["", "unknown", "[]", "true"],
            "created": ["", "2026-02-30", "2026-9-18", "'2026-02-30'", "'2026-9-18'", "42", "2026-09-18T00:00:00Z"],
            "updated": ["", "yesterday", "2026-13-01"],
            "sources": ["", "source.pdf", "{}", "[null]", "[42]", "['']"],
            "tags": ["", "engineering", "{}", "[true]", "[['nested']]"],
        }
        for field, values in cases.items():
            old_line = next(line for line in VALID_FRONTMATTER.splitlines() if line.startswith(field + ":"))
            for value in values:
                with self.subTest(field=field, value=value):
                    content = VALID_FRONTMATTER.replace(old_line, f"{field}: {value}")
                    errors = []
                    check_wiki.check_frontmatter(self.write_page(content), errors)
                    self.assertTrue(errors)

    def test_accepts_schema_values_and_yaml_lists(self) -> None:
        for entity_type in check_wiki.ENTITY_TYPES:
            with self.subTest(entity_type=entity_type):
                content = (VALID_FRONTMATTER.replace("type: concept", f"type: {entity_type}")
                           .replace("created: 2026-09-18", 'created: "2026-09-18"')
                           .replace("sources: []", 'sources:\n  - "document.pdf"')
                           .replace("tags: []", 'tags: [engineering, "wiki"]'))
                errors = []
                check_wiki.check_frontmatter(self.write_page(content), errors)
                self.assertEqual(errors, [])

    def test_rejects_malformed_yaml_and_non_mapping(self) -> None:
        for block in ("title: [unfinished", "- title", "", "just a scalar"):
            with self.subTest(block=block):
                errors = []
                check_wiki.check_frontmatter(self.write_page(f"---\n{block}\n---\n"), errors)
                self.assertTrue(errors)

    def test_raw_sources_are_excluded_but_maintained_links_are_checked(self) -> None:
        raw = self.root / "raw" / "nested"
        raw.mkdir(parents=True)
        source = raw / "source.md"
        content = "[asset](uncopied.png)\n[[uncopied-article]]\n"
        source.write_text(content, encoding="utf-8")
        with mock.patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(check_wiki.main(), 0)
        self.assertNotIn(source, check_wiki.markdown_files())
        self.assertEqual(source.read_text(encoding="utf-8"), content)
        for relative in ("README.md", "docs/guide.md", "wiki/concepts/example.md", "docs/raw/guide.md"):
            with self.subTest(path=relative):
                path = self.root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(VALID_FRONTMATTER + content, encoding="utf-8")
                with mock.patch("sys.stderr", new_callable=io.StringIO) as stderr:
                    self.assertEqual(check_wiki.main(), 1)
                self.assertIn("unresolved link (uncopied.png)", stderr.getvalue())
                self.assertIn("unresolved wikilink [[uncopied-article]]", stderr.getvalue())
                path.unlink()


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
