#!/usr/bin/env python3
"""Validate the repository's Markdown links and wiki page conventions."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"
ENTITY_DIRS = {"sources", "features", "products", "personas", "concepts", "style", "analyses"}
REQUIRED_FIELDS = {"title", "type", "created", "updated", "sources", "tags"}
WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`]*`")


def markdown_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*.md") if ".git" not in path.parts)


def check_frontmatter(path: Path, errors: list[str]) -> None:
    try:
        relative = path.relative_to(WIKI)
    except ValueError:
        return
    if not relative.parts or relative.parts[0] not in ENTITY_DIRS:
        return
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        errors.append(f"{path.relative_to(ROOT)}: unclosed YAML frontmatter")
        return
    block = parts[1]
    keys = {line.split(":", 1)[0].strip() for line in block.splitlines() if ":" in line}
    missing = REQUIRED_FIELDS - keys
    if missing:
        errors.append(f"{path.relative_to(ROOT)}: missing fields {', '.join(sorted(missing))}")


def check_links(path: Path, wiki_stems: set[str], errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    text = INLINE_CODE.sub("", FENCED_CODE.sub("", text))
    for target in WIKILINK.findall(text):
        stem = Path(target.strip()).name
        if stem not in wiki_stems:
            errors.append(f"{path.relative_to(ROOT)}: unresolved wikilink [[{target}]]")
    for raw_target in MARKDOWN_LINK.findall(text):
        target = raw_target.split("#", 1)[0].strip()
        if not target or "://" in target or target.startswith(("mailto:", "#")):
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            errors.append(f"{path.relative_to(ROOT)}: unresolved link ({raw_target})")


def main() -> int:
    errors: list[str] = []
    files = markdown_files()
    wiki_stems = {path.stem for path in WIKI.rglob("*.md")}
    for path in files:
        check_frontmatter(path, errors)
        check_links(path, wiki_stems, errors)
    if errors:
        print("Wiki quality check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Wiki quality check passed ({len(files)} Markdown files checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
