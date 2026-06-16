# Dangling Export/Import Bug Pattern

## Summary
Build-breaking bug class: a call site imports a name that doesn't exist in the source module — either never exported (agent worktree drift) or exported under a different shape (default vs named). Caught twice in one session, different files, same root shape.

## Context
2026-06-16 build failure: `TypeError: getOptimalImageQuality is not a function` across 13 activity-detail SSG pages.

## Instances Found

### 1. Missing export (agent worktree drift)
`components/activities/detail/AirbnbPhotoGrid.js` imported `getOptimalImageQuality` from `helpers/imageOptimization.js`. The function existed only in 3 uncommitted `.claude/worktrees/agent-*` branches — never merged to main/develop. Call site landed on main; helper definition didn't.

**Fix:** re-add the export to the real module, matching the worktree implementation (SSR-safe `typeof window === 'undefined'` guard).

### 2. Named vs default import mismatch
`pages/help/faqs.js` did `import { fetcher } from '../../helpers/fetcher'` but `helpers/fetcher.js` only has `export default fetcher`. Webpack "Attempted import error" — non-fatal at build time (page still compiles), but functionally broken (`fetcher` resolves to `undefined` at runtime in that file).

**Fix:** match the other 17 call sites — `import fetcher from '../../helpers/fetcher'`.

## Detection Method
Both instances found by: `grep -rn "<fnName>" --include="*.js" . --exclude-dir=.next --exclude-dir=node_modules --exclude-dir=.claude` then checking the source module's actual `export` lines against every call site. Build output (`npm run build`) surfaces #1 immediately (hard TypeError); #2 only surfaces as a webpack warning, not a build failure — easy to miss without explicit grep sweep.

## Prevention / Reuse
When auditing a fix to a missing-export bug, **always grep the whole module's other exports against their call sites too** — same bug class often hides elsewhere uncaught because it doesn't always hard-fail the build (default/named mismatches just warn).

When deleting unused exports during cleanup, verify zero callers with the same exclude pattern (`.next`, `node_modules`, `.claude/worktrees`) — agent worktrees can contain phantom callers that don't exist on the real branch.

## Related
- [[trip-detail-server-side-seo-pattern]]
