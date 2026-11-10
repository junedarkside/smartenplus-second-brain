# OpenCode Delegation Workflow

**Context:** Nexo, 2026-11-10 (#564). Junior coding tasks go to cheap OpenCode models through herdr; Claude orchestrates and verifies. Repo rules: Nexo `CLAUDE.md` section 19.

## Summary
Delegate narrow, reversible tasks. Never trust the worker's report: the orchestrator reads the diff and runs the tests.

## Steps
1. Classify the task. Lane A: non-coding on public or synthetic text. Lane B: junior coding (tests for existing code, small bugfix in a named file, file split by existing pattern). Never: booking, idempotency, reconciliation, Central ID mapping, auth/secrets, availability semantics, migrations, payment, passenger data.
2. Prepare: feature branch, clean `git status`, run in a repo copy **without `.env`** (e.g. `git archive develop`), write `opencode.json` with `bash`, `webfetch`, `external_directory` denied and `edit` allowed only for the target file.
3. Run in a herdr pane: `herdr pane split --current --direction right --cwd <copy> --no-focus`, `herdr agent start <name> --kind opencode --pane <id>`, `herdr agent prompt <name> "<text>" --wait --timeout MS`.
4. Verify as orchestrator: read the diff, only allowed files changed, run pytest and lint, break the code on purpose (mutation check) and confirm the new tests fail.
5. Close the pane, copy the file into the real repo on its own branch, run `make check`.

## Gotchas
- Interactive OpenCode does not accept `-m`; set `"model"` in `opencode.json`. `opencode run -m provider/model` works for non-interactive runs.
- With bash denied the agent writes tests but cannot run them. That is the point: the orchestrator is the tester.
- Billing is per token. Read cost in the OpenCode console; `opencode stats` reports 0. A 5-request test-writing run cost about $0.0033.
- Data egress: the files an agent reads go to the model provider. Use only models whose retention policy the owner accepted.

## Related
[[claude-cost-optimization-patterns]], [[evaluating-cheap-models-as-coding-workers]]
