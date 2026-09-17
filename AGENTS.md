# Codex operating guide

This repository is a Markdown knowledge base, not an application. Keep changes small,
traceable, and easy to review.

## Start every task

1. Read `CLAUDE.md`, `wiki/index.md`, and the latest entries in `wiki/log.md`.
2. Check `git status` before editing.
3. Treat files under `raw/` as immutable inputs.

## Content rules

- Follow the page schema and workflows in `CLAUDE.md`.
- Use kebab-case filenames and Obsidian `[[wikilinks]]` for internal wiki links.
- Update `wiki/index.md` whenever an entity page is created, renamed, or removed.
- Append relevant ingestion, query, and lint activity to `wiki/log.md`; never rewrite
  old log entries.
- Do not invent a source or a claim. Make uncertainty and provenance explicit.

## Before finishing

- Run `python scripts/check_wiki.py`.
- Review `git diff --check` and `git status --short`.
- Summarize changed knowledge and any follow-up work in the pull request.
