# Code Size & Complexity Enforcement

Derived from SWE best practice research (2026-10-06). Applied across all 3 SmartEnPlus repos.

## Why

CLAUDE.md had correct thresholds (≤30 lines/function, ≤10 branches, file <500 red) but no automated enforcement. Claude could grow a file past limits with no step flagging it.

## Industry Standard Thresholds

| Metric | Threshold | Source |
|--------|-----------|--------|
| Cyclomatic complexity (McCabe) | ≤ 10 | Google internal, McCabe original paper |
| Cognitive complexity | ≤ 15 | SonarQube default quality gate |
| Function length | ≤ 50 lines (JS), ≤ 30 lines (Python) | Team convention |
| File length | ≤ 400 lines warn, ≤ 500 hard limit | Team convention |
| Max params | ≤ 3–4 | Airbnb, SmartEnPlus |

**Cyclomatic vs cognitive:** cyclomatic = execution path count (testability). Cognitive = how hard to read (penalizes nesting). Modern teams prefer cognitive for code review; cyclomatic for test coverage estimation.

## What Was Configured

### JS repos (FE + Admin) — `.eslintrc.json`

```json
"rules": {
  "complexity": ["warn", 10],
  "max-lines": ["warn", { "max": 400, "skipBlankLines": true, "skipComments": true }],
  "max-lines-per-function": ["warn", { "max": 50, "skipBlankLines": true, "skipComments": true }],
  "max-depth": ["warn", 4],
  "max-params": ["warn", 4]
}
```

Admin kept `max-params: warn/3` (stricter, was already set).

### Python (BE) — `.flake8`

```ini
[flake8]
max-line-length = 119
max-complexity = 10
per-file-ignores =
    */migrations/*.py: E501,W503
    manage.py: E402
extend-ignore = E203,W503
```

## Enforcement Layer Strategy

| Layer | What | Why |
|-------|------|-----|
| Editor (ESLint/flake8) | All rules as `warn` | Instant, inline, no friction |
| Pre-commit | Lint + format only (fast <2s) | Blocks before push |
| CI | Tests + lint (`error`-level rules) | Can't bypass |
| PR review | Human judgment on splits | Async, catches design issues |

Rules set to `warn` not `error` — editor shows violations on legacy files without blocking CI. Upgrade to `error` after backlog cleared.

**Do NOT put slow checks in pre-commit** (type-check, full test suite) — devs bypass hooks when slow.

## CLAUDE.md Changes

All 3 repos got:
- **Pre-Flight:** size budget check (`wc -l` before adding code, extract if >300)
- **Post-Edit table:** "File size in bounds" row (`wc -l` + ESLint/flake8 reference)

## Key Insight

Real enforcement = CI hard block. Editor warnings alone = ignored in practice. The pattern: warn locally, block in CI, document in CLAUDE.md so AI agents also check.
