---
name: verify-render-path-before-fixing-symptom-match
description: A component name/pattern matching a UI symptom is not proof it's the component actually rendering on the affected route — verify via render tree or live DOM before fixing, especially in codebases with near-duplicate components.
type: knowledge-atom
date: 2026-09-18
parent: admin-dashboard-sidebar-scrollbar-fix-2026-09-18
---

# Verify Render Path Before Fixing a Symptom-Matched Component

## Summary
Grep/name-matching a component to a UI bug report ("sidebar" bug → found a component literally named `sidemenu.js` with the exact bug pattern) is not confirmation it's the component actually rendering on the affected route. Fixed it, shipped it, bug persisted — the real component was a near-duplicate file (`SideList.js`) nobody had linked. Cost: 2 full round-trips (fix → merge → push → user re-reports → re-diagnose → re-fix → re-merge → re-push) that a 1-line grep or a live DOM check would have prevented on the first pass.

## Context
admin-dashboard sidebar showed a visible vertical scrollbar. An Explore agent found `components/sidemenu/sidemenu.js` — a MUI `Drawer` with `openedMixin`/`closedMixin` overflow handling, matching the bug shape exactly. Fixed via `PaperProps={{ className: 'scrollbar-hide' }}` (reusing an existing global util), reviewed by `nextjs-fullstack-architect`, committed + merged to `develop`, pushed. User rebuilt, restarted, scrollbar still there.

## Problem
Nobody checked whether `sidemenu.js` was actually imported by the page rendering the bug. It wasn't — `grep -rn "from '.*sidemenu/sidemenu'"` across the repo returned nothing except the component's own `.stories.js`. The real render path was `pages/dashboard/index.js` → `Dashboard.js` → `SideList` (`pages/dashboard/SideList.js`) — an independent, near-identical `Drawer`/mixin implementation, not a shared component. Two files with the same shape existed; the fix landed on the dead one.

## Root-Cause Method That Actually Worked
Live DOM inspection beat re-reading source a third time:
```js
// via Chrome DevTools / MCP javascript_tool, on the live page
const p = document.querySelector('.MuiDrawer-paper');
JSON.stringify({
  className: p.className,          // does it have the fix's class?
  overflowY: getComputedStyle(p).overflowY,
  scrollHeight: p.scrollHeight,    // > clientHeight confirms real overflow
  clientHeight: p.clientHeight,
});
```
`className` lacked `scrollbar-hide` even after the "fix" — proof the deployed DOM wasn't rendering the file that was edited. From there, tracing `pages/dashboard/index.js` → `Dashboard.js` → import list found the real component in under a minute.

## Pattern — Cheap Confirmation Before Declaring a Fix Done
1. Grep for the fix's own signature (new className, new prop, new import) against the page's actual render path — `pages/<route>.js` and everything it imports — not just "a component that looks related."
2. If a live server is available, confirm the DOM/behavior directly instead of trusting source-reading alone. Source can be correct and still be dead code.
3. When a fix doesn't take effect after a clean rebuild, suspect **wrong file**, not stale cache, as an equally likely cause — check both, don't assume one.
4. In codebases where similar components get copy-pasted rather than shared (confirmed pattern here — two independent `Drawer` implementations with the same mixin code), name-similarity is weak evidence. Import-graph truth is the only real evidence.

## Trigger Conditions
Apply this check whenever:
- A bug report names a UI area ("sidebar", "header", "modal") and more than one component in the codebase plausibly matches that name/shape
- The fix is applied but not immediately live-verified on the actual affected route
- A "fix didn't work" report comes back after a clean build — before re-diagnosing the CSS/logic, re-confirm the edited file is even in the render path

## Tradeoffs
- **Pro:** A single `grep` for the new prop/class against the live route, or one DOM query, costs seconds and eliminates an entire class of wrong-file bugs
- **Pro:** Generalizes beyond this one bug — applies to any "I fixed X but it's not showing" report
- **Con:** Adds a verification step to every fix — worth it specifically when component-name-matching was the only evidence used to locate the target file (i.e., no explicit file path was given/confirmed by the user or an import trace)

## Related
- [[mui-menu-paper-overflow-guard]] — different MUI overflow pattern (Menu Paper height capping), not the same bug class, but same component family (MUI Paper-based overflow)
- Fix detail: admin-dashboard `pages/dashboard/SideList.js` + dead code `components/sidemenu/sidemenu.js`, both patched with `PaperProps={{ className: 'scrollbar-hide' }}` reusing `styles/globals.css:122-129`
