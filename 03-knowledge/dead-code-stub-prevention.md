# Dead Code / Stub Prevention

## Summary

Active grep check added to Post-Edit verification table in all 3 repo CLAUDE.md files to catch stubs and dead code before merge.

## Problem

CLAUDE.md had a passive "NO TECH DEBT" rule but no active detection step. Claude could pass all 6 post-edit checks (props, callers, side effects, edge cases, console errors, tests) and still leave:
- `// TODO` or `// FIXME` comments
- `console.log` debug statements
- Unused imports from refactoring
- Empty catch blocks
- Stub functions returning `null` or `undefined`
- Unreachable branches from incomplete refactor

Common triggers: context switch mid-session, interrupted flow, large refactor where original path got orphaned.

## Detection (added to Post-Edit table)

**Frontend / Admin (JS/JSX):**
```bash
grep -rn "TODO\|FIXME\|console\.log\|stub\|placeholder" <changed files>
```
Also check: unused imports, empty catch blocks, unreachable branches.

**Backend (Python/Django):**
```bash
grep -rn "TODO\|FIXME\|print(\|# stub\|placeholder" <changed files>
```
Also check: unused imports, bare `except:`, dead branches.

## Where Enforced

Post-Edit Verification table in:
- `smartenplus-frontend/CLAUDE.md` (JS patterns)
- `smartenplus-backend/CLAUDE.md` (Python patterns)
- `admin-dashboard/CLAUDE.md` (JS patterns)

Added 2026-10-06 between "No new console errors" and "Tests pass" rows.

## Decision

Added as Post-Edit table row (not a separate section) because the table is the mandatory checklist Claude runs before calling a task done — the only place an active grep will actually execute every session.

## Related

- [[claude-cost-optimization-patterns]]
- [[claude-agent-model-pinning-pattern]]
