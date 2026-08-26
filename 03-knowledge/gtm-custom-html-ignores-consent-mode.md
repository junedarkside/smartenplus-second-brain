# GTM Custom HTML Tags Ignore Consent Mode Signals

## Summary

Google Consent Mode v2 signals are **advisory**. Built-in Google tags (GA4, Google Ads) read them and self-suppress. A **GTM Custom HTML tag does not** — it executes raw `<script>` whenever its trigger fires, regardless of `ad_storage`, `analytics_storage`, or any other signal. A correct Consent Mode implementation therefore provides **zero** protection for a Custom HTML tag such as a hand-added Meta Pixel.

## Context

Found in session #363 by measuring production, not by reading code. SmartEnPlus had a correct-looking Consent Mode v2 setup and a cookie banner that worked. The Meta Pixel tracked anyway.

Three behaviours measured on `www.smartenplus.co.th` with `localStorage` cleared:

| State | Expected | Actual |
|---|---|---|
| Banner visible, **untouched** | no tracking | `tr/?ev=PageView` → **200**, `_fbp` cookie written |
| **Decline** clicked, page reloaded | no tracking | PageView fired again, same `_fbp` |
| Decline click itself | not reported | `ev=SubscribedButtonClick`, `cd[buttonText]=Decline`, `es=automatic` |

The third is the one to notice: Meta's **Automatic Advanced Matching** captured the user's act of refusing and sent it to Meta.

## Problem

The app code was not at fault, and that is what makes this hard to spot:

- `pages/_app.js:88-99` — `strategy="beforeInteractive"`, all four signals `denied`, `wait_for_update: 500`, firing **before** GTM mounts
- `components/UI/CookieConsentBanner.js:6-14` — `gtag('consent','update',…)` on choice; `:19-32` replays the stored choice on mount

Both verified present in the live `dataLayer` during the failure. The signals were set correctly and arrived on time. **The Custom HTML tag simply never consulted them.**

Auditing the consent code in isolation will always pass. Only a network trace reveals it.

### Why the usual fix is unavailable

GTM's per-tag **Advanced Settings → Consent Settings** panel is the documented way to gate a Custom HTML tag. On container `GTM-PS3WS7R` that panel does not render at all (investigated in #361: consent overview BETA enabled, container settings saved, tag hard-reopened, absence confirmed via page text — cause still unknown). So the documented path was closed.

## Decision

Gate at the **trigger**, not inside the tag.

1. Push a dedicated event when — and only when — consent is granted:
   ```js
   if (granted) {
     window.dataLayer?.push({ event: 'consent_granted' });
   }
   ```
2. In GTM, create a **Custom Event** trigger on `consent_granted`.
3. On the Pixel tag, **remove `All Pages`** and attach the new trigger.

Declining pushes nothing, so the trigger never matches and the tag never executes. The block is absolute rather than conditional — no in-tag JS guard to get wrong.

Rejected alternative: an in-tag `if (localStorage…)` guard. It lives in GTM rather than the repo, is invisible to code review, and still loads the tag body.

## Details

### Removing `All Pages` is the actual fix

GTM fires a tag if **any** attached trigger matches. Leaving `All Pages` alongside the new trigger changes nothing.

### Ordering is load-bearing

Publishing the GTM change before the frontend reaches production removes `All Pages` while no `consent_granted` event exists — killing the tag for **accepting** users too.

Correct sequence: deploy code → confirm the event in production → publish GTM.

```js
// in the production console, after accepting
window.dataLayer.filter(e => e.event === 'consent_granted')
// → must be non-empty before touching GTM
```

### Split the guard, or the gate can silently fail

An existing combined early return will swallow the new push:

```js
// before — a missing gtag skips the dataLayer push too
if (typeof window === 'undefined' || typeof window.gtag !== 'function') return;

// after — the push no longer depends on gtag being present
if (typeof window === 'undefined') return;
if (typeof window.gtag === 'function') { /* consent update */ }
if (granted) { window.dataLayer?.push({ event: 'consent_granted' }); }
```

Otherwise any user whose `gtag` shim failed to initialize keeps the tag dark forever.

### Verify with page state, not blocked requests

The strongest evidence the tag never ran:

```js
typeof window.fbq                                              // → "undefined"
[...document.scripts].map(s=>s.src).filter(s=>s.includes('facebook'))   // → []
```

Absence of a network request is weaker — it can mean "blocked" rather than "never attempted". Also note **same-domain navigation does not clear Chrome's request log**, so a stale entry reads as a live one; check a timestamp, clear the log, or test on a different path.

### The returning-visitor case is the one that breaks

A returning accepter never clicks anything — the choice is replayed from a `useEffect` on mount. Verify that path explicitly; it fires later than document start, so tag timing shifts a few hundred ms.

### Turn off Automatic Advanced Matching separately

The trigger gate stops it pre-consent, but AAM stays active for users who accept, scraping checkout form fields (email, phone, name) and hashing them to Meta. Disable it in Events Manager → pixel → Settings. Independent of the gate; no deploy.

## Consequences

- Event **volume** drops by however many visitors decline or never choose. That is the intent, not a regression.
- Event **timing** shifts later — the tag fires on `consent_granted`, not at document start.
- **Every future Custom HTML tag must use the same trigger.** Building the remaining event tags on `All Pages` would reintroduce the gap.
- A Consent Mode audit that reads only code will keep passing while the gap is live. **Measure the network.**

## Related

- [[master-state]] — session #363
- [[csp-duplicate-headers-intersection]] — the CSP work that let the Pixel run far enough to expose this
- `components/UI/CookieConsentBanner.js` · `pages/_app.js:88-99` · container `GTM-PS3WS7R`
