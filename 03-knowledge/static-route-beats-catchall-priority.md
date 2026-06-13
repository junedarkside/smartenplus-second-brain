# Static Route Beats Catch-All Priority

## Summary
Next.js Pages Router routes static paths (`/help/faqs`) ahead of catch-all routes (`pages/help/[...slug].js`) — creating a static `pages/help/faqs.js` makes the catch-all skip `["faqs"]` automatically. No explicit priority config needed.

## Context
Next.js Pages Router resolves routes in this order: static > dynamic > catch-all. When both `pages/help/faqs.js` (static) and `pages/help/[...slug].js` (catch-all) exist, requests to `/help/faqs` hit the static file; the catch-all's `slug` param becomes `["faqs"]` only when no static file matches. This is undocumented behavior in the routing precedence rules.

## Problem
A team adding a new "Help & FAQs" landing page at `/help/faqs` may not realize there's a catch-all `pages/help/[...slug].js` already serving all `/help/*` paths. The naive approach (just create `pages/help/faqs.js`) works, but a team that's not aware of the catch-all may:
- Try to delete the catch-all (breaks other `/help/*` routes)
- Add explicit priority config (unnecessary, no such config in Pages Router)
- Rename the static route to `/help/faqs-landing` to "avoid the catch-all" (hack)

The rule is: the routing system already handles this — just create the static file.

## Details
The directory structure:

```
pages/
  help/
    [...slug].js   ← catch-all, serves /help/foo, /help/foo/bar, etc.
    faqs.js        ← static, serves /help/faqs ONLY
    index.js       ← static, serves /help
```

Request to `/help/faqs` → `pages/help/faqs.js` (static wins).
Request to `/help/getting-started` → `pages/help/[...slug].js` with `slug = ["getting-started"]`.
Request to `/help/foo/bar` → `pages/help/[...slug].js` with `slug = ["foo", "bar"]`.

Inside `faqs.js`, you can export `getStaticProps` for SSG, or no data fetching at all — the page is just a React component file. The catch-all's `slug` simply does not include `"faqs"` because the static file shadows it.

## Decision
When adding a new help/docs/blog sub-route that has a static landing page AND a catch-all sibling, just create the static `.js` file at the matching path. No priority config, no catch-all editing. The Pages Router handles precedence automatically.

## Tradeoffs
- Pro: Zero config — Pages Router does the right thing
- Pro: No risk of breaking other catch-all routes
- Pro: Static routes can use `getStaticProps` for build-time data; catch-alls typically use `getStaticPaths` + `getStaticProps` with `fallback`
- Con: The rule is not in the official Next.js docs prominently. Devs new to the codebase may not know.
- Con: If the static file is removed, the catch-all silently starts serving that path (no error). Behavior change is silent.

## Consequences
Codify in the help/docs sub-route convention. Any new "landing page" for a help/docs/blog surface follows this pattern: static file at the exact path, catch-all handles the rest. Future devs should grep `pages/help/ pages/docs/ pages/blog/` for `[...slug]` to find catch-alls before adding new static routes.

This will recur in any project with catch-all routing for help/docs/blog surfaces. Document the rule so it doesn't get rediscovered.

## Related
- [[nextjs-fixed-header-per-route]] — sibling pattern for layout variation by route
