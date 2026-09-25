---
name: sitecontext-language-branch-pattern
description: Pattern for branching a shared component's static strings by language using useSite() with zero prop changes to any caller — used to fix ContactUs.js showing English on the Thai /th/about page. Shipped 2026-09-25.
type: knowledge-atom
date: 2026-09-25
parent: multi-market-i18n-analytics-migration
---

# SiteContext Language-Branch Pattern (Zero Prop Changes)

## Summary
To make a shared, zero-prop component render different static text per language, consume `useSite()` directly inside the component and branch a local `COPY` lookup object by `language` — no prop threading, no caller changes, safe for components with multiple existing callers across different locale contexts.

## Why It Matters
`components/pages-info/ContactUs.js` is called from 4 pages (`about`, `th/about`, `privacy`, `terms`) — only one of which needs Thai text. CLAUDE.md requires grepping all callers before touching any shared component; this pattern avoids needing to touch any of them, since `useSite()` self-resolves from the URL path via the already-mounted `SiteProvider` in `_app.js` and defaults safely to English if ever rendered outside a provider.

## Detail
```js
import { useSite } from '../contexts/SiteContext';

const COPY = {
  en: { heading: 'Contact Us', followUs: 'Follow us on social media:', address: 'Bangkok 10250, Thailand.' },
  th: { heading: 'ติดต่อเรา', followUs: 'ติดตามเราบนโซเชียลมีเดีย:', address: 'กรุงเทพฯ 10250 ประเทศไทย' },
};

const ContactUs = () => {
  const { language } = useSite()
  const t = COPY[language] || COPY.en
  return <h2>{t.heading}</h2> // etc.
};
```
Component signature stays `() => {}` — zero props added, zero props removed. All 4 callers unaffected; only the two locale-scoped routes (`/about` vs `/th/about`) actually see different output, and that's driven by URL path via `resolveLanguage()`, not by anything the caller passes in.

## Constraints / Gotchas
- Only safe because `useSite()` never throws (deliberate divergence from `useCurrency()`, documented in `components/contexts/SiteContext.js`) — defaults to `DEFAULT_LANGUAGE` ('en') if called outside `SiteProvider`. A context that throws outside its provider would make this pattern unsafe to use in a shared component without auditing every render path.
- This is the "tier 2" customization level in [[nextjs-builtin-i18n-vs-page-cloning]] — a small in-file branch, not a separate file. Reach for this only when the difference really is just static strings; anything requiring different data-fetching per language still needs the language passed down explicitly (see `withLangParam`'s SSR-explicit-lang requirement).
- Doesn't cover dynamic/fetched content — this pattern is for hardcoded UI strings only. WordPress/Django-sourced content still needs its own language-aware fetch.

## Related
- [[multi-market-i18n-analytics-migration]] — parent project; the "Phase 3b — UI chrome" loose end this fix is a first instance of
- [[nextjs-builtin-i18n-vs-page-cloning]] — the 3-tier customization model this pattern is tier 2 of
