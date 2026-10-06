# Wiki Log

Append-only chronological record of all activity: ingests, queries, and lint passes.

To view recent activity: `grep "^## \[" log.md | tail -10`

---

## [2026-04-07] init | Wiki created

Wiki initialized for a technical writer's personal knowledge base.

Structure created:
- `raw/` — source documents folder
- `wiki/` — LLM-maintained knowledge base
- `wiki/sources/` — per-source summary pages
- `CLAUDE.md` — schema and operating instructions

Core pages created:
- `wiki/index.md`
- `wiki/log.md`
- `wiki/overview.md`
- `wiki/glossary.md`

Next step: Drop your first source into `raw/` and say **"ingest [filename]"**.

## [2026-10-06] lint | PR #1 quality checker review fixes

Excluded immutable `raw/` Markdown inputs from link validation. Required a
standalone closing frontmatter delimiter in column zero and validated YAML values
against the existing entity schema. Added regression coverage and pinned PyYAML
for local checks and the quality workflow. No entity pages or raw inputs changed.

Validation on Python 3.12.14: all 10 unittest tests passed; devcontainer JSON,
`py_compile`, the wiki checker (12 Markdown files), and `git diff --check` passed.
