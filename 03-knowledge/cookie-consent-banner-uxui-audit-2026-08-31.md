---
name: cookie-consent-banner-uxui-audit-2026-08-31
description: UX/UI, accessibility, and code-quality audit of components/UI/CookieConsentBanner.js — dark-pattern risk on unequal button prominence, missing ARIA/focus management, undocumented z-index outside design system scale, chat-bubble collision on mobile.
metadata:
  type: knowledge
  status: final
  date: 2026-08-31
---

# Cookie Consent Banner — UX/UI Audit

## Summary

Audited `components/UI/CookieConsentBanner.js` (mounted `pages/_app.js:106`, dynamic-imported `ssr:false` at `pages/_app.js:27`). Functionally sound consent-mode wiring (confirmed correct in [[gtm-custom-html-ignores-consent-mode]]) but the presentation layer has one GDPR dark-pattern risk, three accessibility gaps, one design-system violation (z-index), and one real visual collision on mobile. No blocking functional bugs. All findings preserve the `consent_granted` dataLayer contract untouched — no finding below touches `updateGtagConsent`.

## Findings — Dark-Pattern / Legal Risk

### 1. Unequal button prominence — EU/PDPA dark-pattern risk
`components/UI/CookieConsentBanner.js:63-77`

"Accept All" is `bg-brand-primary` solid fill, `font-semibold`, `px-5` (wider). "Decline" is an outline button, `font-medium`, `px-4`, gray text. Under EDPB Guidelines 03/2022 and CNIL/ICO guidance, "Reject" must carry **equal visual weight** to "Accept" (same size, same visual salience — outline-vs-solid asymmetry is the canonical example of a "false hierarchy" dark pattern). Thai PDPA guidance (per [[cs-consent-gdpr-model]] posture: EU+US+Thai audience) tracks the same principle.

**Fix:** give Decline equal visual weight — either both solid with neutral vs. brand color, or both outline. Do not vary font-weight or padding between the two.

### 2. No "Manage preferences" / granular option — conflicts with vault consent model
`components/UI/CookieConsentBanner.js:59-77`

Only binary Accept All / Decline exists. `updateGtagConsent` already sends four separate signals (`ad_storage`, `analytics_storage`, `ad_user_data`, `ad_personalization`) but the UI cannot express partial consent — a user cannot decline ads but keep analytics. [[cs-consent-gdpr-model]] §5 requires consent to be "granular" for the marketing consent record; this banner is analytics/ads consent, not the same record, but the same granularity principle applies under GDPR Recital 32 to any bundled non-essential purposes. Not blocking (binary accept/decline is legally defensible if both options are equally easy), but flag as a gap versus best practice.

**Fix:** out of scope for this pass — no code change recommended now, just tracked. If a "Manage" tier is added later, it must still preserve the "push `consent_granted` on grant only" contract from [[gtm-custom-html-ignores-consent-mode]] — a partial-grant state would need its own dataLayer event, not reuse `consent_granted` as currently scoped to Meta Pixel triggering.

## Findings — Accessibility

### 3. No ARIA role / label on the banner container
`components/UI/CookieConsentBanner.js:54-55`

The outer `<div>` has no `role` and no `aria-label`/`aria-labelledby`. Screen reader users navigating by landmarks will not discover this as a distinct region — it reads as anonymous body content mixed into the page flow.

**Fix:**
```jsx
<div
  role="region"
  aria-label="Cookie consent"
  className="fixed bottom-0 left-0 right-0 z-[70] ..."
>
```
Use `role="region"` (not `dialog`) — this banner does not trap focus or block page interaction, so `dialog`/`alertdialog` semantics would be misleading and require focus-trap behavior this component doesn't implement.

### 4. No focus management on mount
`components/UI/CookieConsentBanner.js:15-25` (the `useEffect` that calls `setIsVisible(true)`)

When the banner appears, focus stays wherever it was (often `<body>`). A screen reader user gets no notification a new interactive region appeared unless they happen to tab into it later. This is worsened by `ssr:false` — see Finding 7.

**Fix:** on the transition to visible, move focus to the banner region or its first button:
```jsx
const bannerRef = useRef(null);
useEffect(() => {
  if (isVisible) bannerRef.current?.focus();
}, [isVisible]);
```
with `tabIndex={-1}` added to the container div so it's programmatically focusable without adding a tab stop for mouse users.

### 5. No `aria-live` announcement
`components/UI/CookieConsentBanner.js:54-77`

Appearance of the banner is a live DOM change but nothing announces it to assistive tech already focused elsewhere (e.g., a user who tabbed past where the banner will render before it mounts). Combined with Finding 4, a screen reader user may complete a form or navigate the page without ever learning cookies are being requested.

**Fix:** add `aria-live="polite"` to the outer container alongside the `role="region"` from Finding 3. Do not use `assertive` — this is not urgent/blocking content.

### 6. Tap targets meet the 44×44px WCAG target — no fix needed, verified
`components/UI/CookieConsentBanner.js:64-76`

`py-2` (8px) + `text-sm` line-height (20px) + border ≈ 36-38px visual height, which is under the strict 44px target-size AAA guideline but passes WCAG 2.1 AA (2.5.5 Target Size is AAA-only in 2.1; **2.5.8 Target Size (Minimum) is AA in WCAG 2.2** and requires 24×24px minimum, which this passes comfortably). Not a blocking finding since the project references WCAG 2.1 AA compliance. Flagging as **informational only** — if the project ever targets WCAG 2.2 AA, current `py-2` height is fine (24px+ floor), no change needed either way.

## Findings — Next.js / React Patterns

### 7. `ssr:false` causes a mount-time flash for first-time visitors — expected, but no skeleton/transition softens it
`pages/_app.js:27`, `components/UI/CookieConsentBanner.js:15-25`

`dynamic(..., { ssr: false })` is the correct call — the component reads `localStorage` synchronously in an effect, which cannot run server-side. This is not a hydration-mismatch bug. However there is a visible **pop-in**: the banner has no mount transition (no `transition`/`animate` classes), so first-time visitors see it snap into existence with a hard cut, which reads as janky against the rest of the app's `transition-colors` usage on the buttons themselves (`:69`, `:74`). This is polish, not correctness.

**Fix (optional, non-blocking):** add a simple `transition-transform` + translate-Y mount animation, e.g. wrap the visibility toggle in a CSS class swap (`translate-y-full` → `translate-y-0`) rather than a hard `if (!isVisible) return null`.

### 8. Effect chain — verified compliant, not a violation
`components/UI/CookieConsentBanner.js:15-25`

Project rule forbids effect B depending on effect A's result. This component has exactly one `useEffect`, and `updateGtagConsent` is a plain function call inside it (not a second effect reacting to state the first effect set) — no chain exists. **No fix needed**, listed here only to confirm the pattern was checked per the audit brief.

### 9. try/catch-with-`console.warn` — verified compliant
`components/UI/CookieConsentBanner.js:17-24`, `:29-33`

Matches the project convention ("helpers return null + `console.warn`, never throw"). Both the read path and write path degrade gracefully — a `localStorage` failure re-shows the banner (read) or silently no-ops the persistence while still applying the in-memory consent choice (write). **No fix needed.**

## Findings — Layout / Visual Collision

### 10. z-[80] is outside the project's Z_INDEX scale and inconsistent with its own semantic tier
`components/UI/CookieConsentBanner.js:55`

`helpers/designSystem.js:184-194` defines the canonical scale:
```
base:0, dropdown:10, sticky:20, overlay:30, modal:40, popover:50, tooltip:60, notification:70, scrollTop:500
```
The chat widget (`components/chat/ChatBubble.js:7`, `ChatPanel.js:144`) correctly consumes this via `CHAT.position.bubble.zIndex = Z_INDEX.popover` (50). The cookie banner instead hardcodes `z-[80]` — a value that doesn't exist in the scale at all, sits above `notification` (70), and was invented ad hoc rather than reusing a token. This is exactly the kind of untracked magic number the scale exists to prevent, and the next dev adding a toast/notification at `notification:70` will silently render underneath this banner.

**Fix:** add `banner: 70` is wrong (collides with `notification`); the semantically correct slot is between `notification` (70) and `scrollTop` (500). Cleanest fix: reuse `Z_INDEX.notification` (70) directly — a cookie banner and a toast notification are not expected to co-occur, and if they do, either ordering is acceptable. Replace `z-[80]` with `z-[${Z_INDEX.notification}]` (i.e. `z-[70]`) by importing `Z_INDEX` from `helpers/designSystem.js`, or add a named `Z_INDEX.consentBanner: 70` if the project prefers a distinct semantic name over reusing `notification`. Either way, stop hand-rolling `z-[80]`.

Other `z-[...]` usages checked for collision (`grep -rn "z-\[" --include="*.js"`): `NavBar.js:66` (`z-[1000]`, dropdown menu — no conflict, far above), `main-header.js:42` (`z-[1200]`, skip-link focus state — no conflict), `TransportationSearch.js:151` (`z-[10]`, inline decorative element — no conflict). No other fixed-position element competes with the banner's actual stacking range once corrected to 70.

### 11. Chat bubble overlaps the banner region on mobile — real visual collision, not just z-index
`components/chat/ChatBubble.js:6` (`bottom-6 right-4 sm:right-6`) vs. `components/UI/CookieConsentBanner.js:55` (`fixed bottom-0 ... w-full`)

The banner is full-width and pinned to `bottom-0`; the chat bubble sits at `bottom-6` (24px) in the bottom-right corner — which is *inside* the banner's height envelope on mobile where the banner wraps to two rows (`flex-col`, `:56`) and can easily exceed 96px+ tall (text row + button row + padding). The chat bubble will render on top of or partially behind the banner text/buttons for any visitor who hasn't dismissed the banner yet, and is currently guaranteed to be behind it once Finding 10's z-index fix is applied (`popover:50` < `notification:70`), making the bubble unreachable while the banner is showing.

**Fix:** the chat bubble is likely intentional to be reachable at all times; the simplest correct fix is conditional — either (a) `ChatBubble` reads the same `smartenplus_cookie_consent` localStorage key and shifts its `bottom` offset up (e.g. `bottom-24` instead of `bottom-6`) while the banner is visible, matching the pattern `ChatPanel` already uses (`bottom-24` at `ChatPanel.js:143` for the same reason — panel avoids the bubble), or (b) confirm with design whether the chat bubble should simply be suppressed while the consent banner is showing. Do not solve this by further raising the banner's z-index — that only fixes stacking order, not the physical overlap of tap targets.

## Findings — Code Quality / Reuse

### 12. Raw `<button>` elements instead of shared `Button` — checked, not a real violation
`components/UI/CookieConsentBanner.js:64-76` vs. `components/UI/button.js`

`components/UI/button.js` is a thin, unstyled passthrough (`<button onClick={props.onClick} disabled={disabled}>{props.children}</button>`, all styling commented out / delegated to a currently-unused `button.module.css`). It provides no className prop pass-through, no variant system, and no styling contract to inherit — adopting it here would add an indirection layer with zero behavioral or visual benefit, and CLAUDE.md's reuse rule is "80% covered? Extend, don't fork" — this doesn't clear that bar since the shared component covers 0% of what this banner needs (Tailwind classes, `Link` for the "Accept" case is not used here, disabled-state theming). **No fix required.** If a real styled `Button` component with variant props (`primary`/`outline`) is ever built, migrate then — not before.

## Related

- [[gtm-custom-html-ignores-consent-mode]] — the `consent_granted` dataLayer contract this audit's fixes must not break
- [[cs-consent-gdpr-model]] — GDPR/PDPA posture (EU+US+Thai), granular-consent principle referenced in Finding 2
- `components/UI/CookieConsentBanner.js` · `pages/_app.js:27,106` · `helpers/designSystem.js:184-194,310-324` · `components/chat/ChatBubble.js` · `components/UI/button.js`
