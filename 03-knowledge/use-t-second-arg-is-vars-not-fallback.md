---
name: use-t-second-arg-is-vars-not-fallback
description: useT(key, vars) — second argument is template-variable substitution, NOT a fallback string. Passing a fallback string silently fails.
type: knowledge-atom
date: 2026-10-06
tags: [i18n, useT, gotcha]
---

# `useT` Second Arg Is Vars, Not Fallback

## Signature

```js
const t = useT();
t('trip.quickAnswer')              // ✅ lookup key
t('trip.title', { name: 'Hat Yai' })  // ✅ vars for {name} substitution
t('trip.quickAnswer', 'How to get there')  // ❌ WRONG — 'How to get there' treated as vars object
```

## Behaviour on Missing Key

Missing key → `useT` returns the raw key string as-is + fires `console.warn`.

```
TRIP.QUICKANSWER  ← what shows in the browser
```

No second-arg fallback exists. Fix = add the key to `helpers/i18n/strings/en.js` + `th.js`.

## Files

- `hooks/useT.js` — hook implementation
- `helpers/i18n/strings/en.js` — English catalog
- `helpers/i18n/strings/th.js` — Thai catalog

## Incident

Session #456: `RouteQuickAnswer.js` called `t('trip.quickAnswer', 'How to get there')`. Key missing → browser showed `TRIP.QUICKANSWER` in all-caps. Fix: add key to both catalogs, remove second arg.
