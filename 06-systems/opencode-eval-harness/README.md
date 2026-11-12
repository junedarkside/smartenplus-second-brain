# OpenCode eval harness

Scores OpenCode models as junior coders on a synthetic repo. Method: [[evaluating-cheap-models-as-coding-workers]].

Run: `python run_eval.py opencode-go/gpt-6-luna,opencode-go/claude-haiku-5-5 [A_tests,B_bugfix,C_trap,D_split] > results.jsonl`

- `template/` is copied fresh per run into a temp dir with its own git root and a permission config (bash, webfetch, external_directory denied; edit allowed only for the named files).
- Checkers run the code, mutate `pkg/pricing.py` for the test-writing task, and list changed files from `git status`.
- Gotcha: opencode follows `$PWD`, not the process cwd. The runner sets `PWD`; without it edits land in the template.
- `PY` at the top of `run_eval.py` points at the Nexo venv (needs pytest). Change it on another machine.
- Timeout 300s per run. Read real cost in the OpenCode console, not `opencode stats`.
- Trap task runs with edits allowed on the whole copy (a deny-all sandbox hides scope violations); other tasks allow only the named files.
- `results-*.jsonl` are the saved raw results per eval date (2026-11-12: sandboxed first pass and unsandboxed trap rerun).
