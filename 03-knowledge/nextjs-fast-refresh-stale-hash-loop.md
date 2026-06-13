# Next.js Fast Refresh Stale Hash Loop

## Summary
Next.js 14.2.x Fast Refresh loops with `webpack.hot-update.json 404` are caused by stale compilation hash + on-demand route compilation cascade, not application code. Loop self-terminates when all routes compile. Mitigation: `next.config.js` `webpack.watchOptions.ignored` for files written by external processes (e.g., `public/audit-screenshots/`).

## Context
Next.js dev server uses Fast Refresh (HMR) to push incremental updates to the browser. Each compilation has a hash. The browser requests `webpack.hot-update.json` (or `.js`) to fetch the delta. When the hash on the server has moved beyond what the browser expects, the request 404s — but the browser keeps polling.

## Problem
In a Next.js 14.2.x project, the dev server enters a fast-refresh loop under specific conditions:
1. A file change triggers a partial recompile
2. The browser has a stale hash (e.g., from a previous session or a HMR client that didn't unmount cleanly)
3. The dev server logs `webpack.hot-update.json 404` continuously
4. The dev server may not be doing real work, but the request log + CPU usage spike
5. The loop self-terminates once every route has been compiled at least once (on-demand compilation hits the route, updates the hash, the browser catches up)

This is NOT a bug in app code. The "fix" attempts that touch the code (clear .next, restart server, downgrade Next.js) don't address the root cause and are not portable.

The specific trigger in our project: writing files to `public/audit-screenshots/` during an active UI audit. The dev server's file watcher sees new PNGs, triggers recompile, hash shifts, browser polls the old hash, 404, repeat.

## Details
The fix in `next.config.js`:

```js
module.exports = {
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        ...config.watchOptions,
        ignored: [
          ...(config.watchOptions?.ignored || []),
          '**/public/audit-screenshots/**',
          '**/.audit-artifacts/**',
        ],
      };
    }
    return config;
  },
};
```

This tells webpack's file watcher to ignore writes to those directories. The dev server still serves the files (Next.js serves `public/` statically), it just doesn't recompile when they change.

The loop self-terminates: trigger a route compile (visit the page in the browser or `curl localhost:3000/route`) and the hash updates. Browser catches up, polls the new hash, gets 200, loop ends.

## Decision
- For any directory that receives writes from external processes (audit scripts, screenshot tools, test runners), add to `next.config.js` `webpack.watchOptions.ignored`
- Do not attempt to fix this at the app level — it's a framework interaction
- If the loop appears in dev, force a route compile (visit every page once) to break it
- 7+ failed fix attempts in the original audit confirm this is not fixable by tweaking the app

## Tradeoffs
- Pro: Ignored directories don't trigger recompile storms
- Pro: Fix is one-time config change
- Pro: Reusable for any external-write directory
- Con: Requires knowing the trigger in advance. New audit/test tools writing to new directories will re-trigger the loop.
- Con: The "loop self-terminates on full route compile" behavior is undocumented. Devs may not believe it and waste time debugging.

## Consequences
The audit-screenshots directory is the current known trigger. Any new external write directory needs the same `watchOptions.ignored` treatment. Add a comment in `next.config.js` explaining WHY (so the next dev doesn't remove the entry as "unused config"). On Next.js major upgrades, re-validate the fix.

## Related
- [[nextjs-patterns]] — broader Next.js gotcha collection
