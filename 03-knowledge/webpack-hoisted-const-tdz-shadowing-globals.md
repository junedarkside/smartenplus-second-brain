# Webpack-Hoisted `const` TDZ When Shadowing Globals

## Summary
In Next.js Pages Router SSR (and any webpack-bundled CJS output), a local `const <name>` that shadows a global identifier (most commonly `window`) gets hoisted to module scope — landing it BEFORE a `typeof <name>` guard and triggering a `ReferenceError: Cannot access '<name>' before initialization` on every SSR call.

## Context
Caught on session #352 (`fix/locations-hub-tech-debt`). After swapping `isomorphic-dompurify` for `dompurify` + a manual JSDOM window, the page returned `LocationErrorState` for every location with a populated description (only hatyai in the test data, but the bug was universal — just hadn't been hit yet). Diagnostic via `console.log` in the catch block:

```
ReferenceError: Cannot access 'window' before initialization
    at getPurifier (pages/locations/[slug].js:77:5)
```

## The Bug

Source code reads naturally:
```js
const getPurifier = () => {
  if (typeof window !== 'undefined') return DOMPurify;   // line 28
  if (serverPurify) return serverPurify;
  const { JSDOM } = require('jsdom');
  const window = new JSDOM('').window;                    // line 34 — shadows global
  serverPurify = DOMPurify(window);
  return serverPurify;
};
```

But webpack/Next.js's emitted CJS for getServerSideProps hoists `const window` to module scope. The bundled output looks roughly like:
```js
// module scope (hoisted from getPurifier body)
const window = new JSDOM('').window;          // ← evaluated at module init

// getPurifier body
const getPurifier = () => {
  if (typeof window !== 'undefined') return ...;  // ← TDZ: module-init hasn't finished
  ...
};
```

Result: first `getPurifier()` call hits TDZ on `typeof window` because the hoisted `const window` declaration is in scope but uninitialized.

**Why it doesn't always fail**: the error fires only when the sanitize code path is exercised — i.e., when `summaryData.description` is truthy. Hatyai had a 2219-char description; bangkok/phuket/chiangmai had empty/missing descriptions → sanitize returned `''` → no call to `getPurifier` → no TDZ.

**Why typeof doesn't save you**: `typeof undeclaredVar` is safe (returns `"undefined"` without throwing). But `typeof <declared-but-not-yet-initialized>` throws ReferenceError under TDZ. Hoisting converts the local `const` into a declaration the `typeof` operator can see.

## Fix

Rename the local var to break the shadow:
```js
const getPurifier = () => {
  if (typeof window !== 'undefined') return DOMPurify;
  if (serverPurify) return serverPurify;
  const { JSDOM } = require('jsdom');
  const jsdomWindow = new JSDOM('').window;          // ← no longer shadows global
  serverPurify = DOMPurify(jsdomWindow);
  return serverPurify;
};
```

Commit `24109412`. No semantic change. Verified live at `/locations/hatyai` — 200, 141 KB, all 5 JSON-LD blocks present.

## General Rule

**Never name a local variable the same as a global the code references earlier in scope**, especially:
- `window` (always reachable via `typeof window` check)
- `self` (Worker / browser-shared)
- `global` / `globalThis` (Node / cross-env)
- `process` (always defined in Next.js SSR)
- `document` / `navigator`

Even if your `typeof <name>` check seems to gate the variable, webpack bundlers that hoist `const`/`let` can move the declaration above the check in the emitted code.

## Diagnostic Recipe

When `getServerSideProps` catch block returns the generic "Failed to fetch" error and you can't see the real error:

1. Add `console.log('[debug] getServerSideProps threw:', error?.message, error?.stack?.split('\n').slice(0, 6).join('\n'))` inside the catch.
2. Hit the page once.
3. Read dev-server terminal (stderr is on the user's TTY per `lsof -p <PID>`).
4. Fix root cause, remove the console.log.

This caught the TDZ error on the first try — without it, the only signal was the opaque "Failed to fetch" error message.

## Related
- `[[dompurify-xss-prevention-pattern]]` Option B — manual JSDOM setup that originally triggered this bug
- `[[nextjs-hydration-rules]]` Rule 2 (no dual JSX trees via `isClient`) — same defensive principle
- Session #352 master-state entry