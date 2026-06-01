# React Hooks Rules — Lowercase Component Name

## Summary

ESLint `react-hooks/rules-of-hooks` (Next.js `next/core-web-vitals` preset) blocks build when hooks called inside lowercase-named function. Component names must start with uppercase (PascalCase) to be recognized as React components.

## Context

Next.js 14+ extends `next/core-web-vitals` ESLint preset, which sets `react-hooks/rules-of-hooks` to **error** (not warning). This rule enforces that hooks (`useRouter`, `useState`, `useEffect`, etc.) can only be called from:
1. React function components (names start with uppercase)
2. Custom React Hook functions (names start with `use`)

## Problem

Lowercase function name → ESLint treats as plain utility function → hooks inside = violation → **build fails**.

Example blocking error:
```
./pages/help/index.js
17:18  Error: React Hook "useRouter" is called in function "index" that is neither a React function component nor a custom React Hook function.  react-hooks/rules-of-hooks
```

## Details

- **PascalCase mandatory** — `const HelpPage = (props) => {` ✅ | `const index = (props) => {` ❌
- **`index.js` files are NOT exempt** — common trap in Next.js pages. Always use PascalCase: `Index`, `HelpPage`, `BlogIndex`.
- **Import safety** — Next.js pages are route-based, not imported elsewhere. Renaming is safe (no reference breakage).

## Tradeoffs

**Why strict?** Hooks rely on call order. Lowercase-named functions could be utility functions that call hooks conditionally → order violations → silent bugs. Enforcing naming convention = guardrail.

**Impact:** Build-blocking error, not warning. Cannot ship with violations.

## Consequences

- Always name page components with PascalCase, even in `index.js`
- Fix is 2-line change: function name + export default name
- No import side-effects (Next.js routing = implicit)

## Related

- [[nextjs-patterns]]
- [[nextjs-hydration-rules]]
