# Contributing

Wiki Karpathy uses issues for intent, short-lived branches for work, and pull requests
for review. For the current priorities and tool boundaries, see
[`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md).

## Make a change

1. Open an issue using the most relevant template.
2. Create a branch such as `ingest/source-name` or `docs/topic`.
3. Follow `AGENTS.md` and the schema in `CLAUDE.md`.
4. Keep `raw/` immutable; add files there, but never rewrite an existing source.
5. Run the checks below and open a pull request linked to the issue.

```bash
python scripts/check_wiki.py
git diff --check
```

Knowledge changes require human review. Confirm that summaries preserve the source's
meaning, claims are traceable, and no confidential or personal data was committed.
