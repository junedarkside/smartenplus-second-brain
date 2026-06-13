# MUI Emotion + Tailwind injectFirst

## Summary
To prevent MUI Emotion from silently overriding Tailwind utilities on MUI components (`<MUI Alert>`, `<MUI Typography>`), wrap `_app.js` tree in `<StyledEngineProvider injectFirst>`. Also add `./helpers/**/*.{js,ts}` to `tailwind.config.js` content array — `designSystem.js` is in `helpers/`, not `components/`, so PurgeCSS kills its dynamically-built classes.

## Context
SmartEnPlus uses MUI for component primitives (Alert, Typography, Button, etc.) and Tailwind for utility classes. MUI uses Emotion (CSS-in-JS) under the hood. Both write to the same DOM stylesheet cascade. The order of stylesheet injection determines specificity: later-injected styles win on equal specificity.

## Problem
Two distinct bugs:

1. **MUI overrides Tailwind.** By default, Emotion injects styles at the END of `<head>`. Tailwind's compiled CSS is in `<head>` first. So `class="bg-red-500 text-white"` on an MUI `<Alert>` is overridden by Emotion's own `background-color` from the `severity="error"` prop. Result: the Tailwind class appears in the DOM but has no visible effect. Silent failure.

2. **Tailwind purges dynamic classes from `designSystem.js`.** `designSystem.js` lives in `helpers/`, not `components/`. Tailwind's `content` config in `tailwind.config.js` is set to scan `components/`. Any class string built dynamically inside `designSystem.js` (e.g. `bg-${color}-500`) is not present in a static source file Tailwind can scan. PurgeCSS strips it from the build. Silent failure — class is referenced in code, missing in CSS.

Both bugs share the symptom: class is in the code, not in the rendered output. Both are non-obvious — dev tools show the class on the element, no errors, just wrong look.

## Details
Fix 1 in `pages/_app.js`:

```js
import { StyledEngineProvider } from '@mui/material/styles';

export default function MyApp({ Component, pageProps }) {
  return (
    <StyledEngineProvider injectFirst>
      {/* rest of tree */}
    </StyledEngineProvider>
  );
}
```

`injectFirst` tells Emotion to inject its styles BEFORE the static CSS in `<head>`. Tailwind's CSS comes first → MUI components now respect Tailwind utility classes.

Fix 2 in `tailwind.config.js`:

```js
module.exports = {
  content: [
    './pages/**/*.{js,ts}',
    './components/**/*.{js,ts}',
    './helpers/**/*.{js,ts}',  // ← required for designSystem.js
  ],
  // ...
};
```

`./helpers/**/*.{js,ts}` covers `designSystem.js` and any other helper that builds class strings.

## Decision
- Always wrap the app in `<StyledEngineProvider injectFirst>` when mixing MUI + Tailwind
- Always include `./helpers/**/*.{js,ts}` in Tailwind's content config when `designSystem.js` or similar helpers exist
- These are "set once, forget" fixes — but if missed, the bugs return silently

## Tradeoffs
- Pro: Two one-time fixes that solve 100% of MUI+Tailwind interaction bugs
- Pro: No runtime cost, no per-component logic
- Pro: Works for any MUI component, not just Alert/Typography
- Con: `injectFirst` changes the global stylesheet order. Any other CSS-in-JS library added later (styled-components) will also need to be configured for order.
- Con: Adding helpers to Tailwind's content scan slightly increases build time (more files to grep). Negligible at our scale.
- Con: Neither fix throws an error. If someone removes the StyledEngineProvider wrapper or the helpers glob, the bugs return silently. Need a comment in each file explaining WHY.

## Consequences
Every new project in this stack starts with both fixes. Codify in the project bootstrap checklist. Future devs touching `_app.js` or `tailwind.config.js` should grep for the comments. If a new helper is added that builds class strings, add it to the content glob (or move it to `components/`).

Framework upgrades: MUI v6 / Tailwind v4 may change this. Re-validate on upgrade.

## Related
- [[design-system-audit-2026-06-13]] — broader design system audit
