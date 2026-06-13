# Checkout UX/UI Audit — 2026-06-10

## Summary

3-agent audit of `http://localhost:3000/checkout` vs SmartEnPlus design system.
Agents: UX Reviewer, UI/CSS Reviewer, Design System Auditor.
Branch: `260609-feat/cross-sell-gtm-recommendations`.
Scrutinized: 2026-06-10 — 2 false positives corrected, 1 missing finding added.

**Critical infrastructure bug found:** `helpers/` excluded from `tailwind.config.js` content — DS utility classes built in `designSystem.js` are purged in production.

**Tailwind ↔ MUI compatibility issue found:** No CSS injection order configured — MUI Emotion styles inject after Tailwind static CSS, silently overriding Tailwind utilities on MUI components. `StyledEngineProvider injectFirst` fix not applied.

---

## High-Priority Fixes

### 0. Tailwind ↔ MUI CSS injection order — Tailwind utilities silently fail on MUI components (PRODUCTION BUG)

- **Issue:** MUI Emotion injects styles at runtime, AFTER `tailwindcss/tailwind.css` static import in `_app.js:11`. No `StyledEngineProvider injectFirst`, no `createEmotionCache`, no `important` config in `tailwind.config.js`. MUI wins every specificity tie → Tailwind classes on MUI components are silently dead.
- **Confirmed dead classes in checkout:**
  - `MUI Alert` at `EnhancedTripCard.js:276` — `py-1 px-2` overridden by Emotion padding
  - `MUI Alert` at `EnhancedTripCard.js:379` — `py-2 border-orange-200` overridden
  - `MUI Typography` at `InlinePassengerSelector.js:334,338` — `text-xs` overridden by variant font-size
- **Safe (not affected):** `MUI Box` layout classes (`flex`, `gap`, `flex-col`) work because Box has no default flex styles. Plain `<div>`/`<button>` elements unaffected.
- **Fix:** Add `StyledEngineProvider injectFirst` in `_app.js` (2-line change, zero risk):
  ```jsx
  import { StyledEngineProvider } from '@mui/material/styles';
  <StyledEngineProvider injectFirst>
    <ThemeProvider theme={theme}>...
  ```
- **Files:** `pages/_app.js`
- **Priority:** CRITICAL

### 1. Tailwind PurgeCSS silently kills designSystem.js classes (PRODUCTION BUG)

- **Issue:** `tailwind.config.js` content covers `./pages`, `./components`, `./lib` — NOT `./helpers/`. `designSystem.js` in `helpers/` builds classes like `hover:bg-brand-primary-dark`, `gap-1` dynamically. PurgeCSS never scans helpers → classes dead in production.
- **Fix:** Add `./helpers/**/*.{js,ts}` to `content` array in `tailwind.config.js`
- **Files:** `tailwind.config.js`, `helpers/designSystem.js`
- **Priority:** CRITICAL

### 2. "Back to search" is a MUI Tab, not a back button

- **Issue:** `CheckOutNavBar.js:85` — navigation-destroying action has same visual weight as step tabs. Tap risk on mobile.
- **Fix:** Replace with standalone `<a>` or `Button variant="text"` above the tab strip, visually separated
- **Files:** `components/forms/checkout/CheckOutNavBar.js:85`
- **Priority:** High

### 3. Step numbers change based on runtime flag (confusing UX)

- **Issue:** `hasMixedPassengerCounts` causes "3. Confirmation" vs "4. Confirmation" — same user sees different numbers on repeat visits
- **Fix:** Remove numbers from tab labels; use step names only. Renumber in one place if needed.
- **Files:** `components/forms/checkout/CheckOutNavBar.js:107-114`
- **Priority:** High

### 4. Mobile "Cart Summary" toggle has zero ARIA

- **Issue:** `index.js:1093` — `<h2 onClick>` with no `aria-expanded`, `aria-controls`, no visual affordance (chevron). Screen reader failure.
- **Fix:** Replace with `<details>/<summary>` or MUI `Accordion` with ARIA attributes
- **Files:** `pages/checkout/index.js:1093`
- **Priority:** High

### 5. Error text: `color: red` + `font-size: 10px` — WCAG failure

- **Issue:** Raw `color: red` has insufficient contrast on white. `font-size: 10px` below WCAG minimum (~12px). Affects all passenger/flight form field errors.
- **Fix:** `color: #EF4444` (DS error token), `font-size: 0.75rem`
- **Files:** `Passengers.module.css:66-68`, `FlightInfoForm.module.css:58-60`
- **Priority:** High

### 6. Negative margin hack for error positioning

- **Issue:** `margin: -10px 0px 0px 40px` — brittle, breaks on different icon sizes
- **Fix:** Use `padding-left` on parent container or `display:flex + gap` layout
- **Files:** `Passengers.module.css:64`, `FlightInfoForm.module.css:56`
- **Priority:** High

### 7. Modal buttons use `bg-blue-600` not brand primary

- **Issue:** Auth-choice modal buttons use `bg-blue-600` (#2563EB) and raw `bg-white` — diverges from `brand.primary: #3b5998`
- **Fix:** Replace with `bg-brand-primary` Tailwind token or MUI Button with DS palette
- **Files:** `pages/checkout/index.js:1156, 1167`
- **Priority:** High

### 8. Bootstrap palette in globals.css overrides DS status colors

- **Issue:** `.primary (#007bff)`, `.success (#28a745)`, `.danger (#dc3545)`, `.warning (#ffc107)`, `.info (#17a2b8)` — all Bootstrap legacy, all diverge from DS `status.*` tokens
- **Fix:** Replace with DS tokens: `success → #10B981`, `error → #EF4444`, `warning → #F59E0B`, `info → #3B82F6`
- **Files:** `styles/globals.css` (badge classes)
- **Priority:** High

---

## Medium-Priority Fixes

### CSS Architecture

| Issue | File:Line | Fix |
|-------|-----------|-----|
| `gap: 18.61px` fractional px | Passengers.module.css:42, FlightInfoForm.module.css:41 | `gap: 1.25rem` |
| Mixed units: `20px` + `.75rem` same file | Passengers.module.css:18,23 | Standardize to `rem` |
| `border-radius: 4px` on container (DS=6px) | Passengers.module.css:12, FlightInfoForm.module.css:12, Confirmation.module.css:11 | `border-radius: 6px` |
| `#CACACA` input border not in DS | Passengers.module.css:46,58 | Map to DS border token or `#e9ebee` |
| `#eaeaea` vs `#e9ebee` — two border colors | NavBar:8 vs Passengers:11 | Pick one; `#e9ebee` is more common |
| `padding: .725rem` arbitrary | CheckOutNavBar.module.css:29 | Round to `.75rem` |
| Dead `.my_button` with `#4CAF50` | Passengers.module.css:32-39, FlightInfoForm.module.css:31-38 | Delete — never rendered |
| 85% duplicate code between Passengers + FlightInfoForm modules | Both files | Extract to `FormCard.module.css` |
| `CheckOutNavBar.module.css` never imported — dead file (40 lines) | CheckOutNavBar.module.css | Delete entire file; `CheckOutNavBar.js` uses only MUI Tabs + `sx` props, never imports this module |

### UX

| Issue | File:Line | Fix |
|-------|-----------|-----|
| Top-level `alert` on validation fail, no inline field errors | index.js:801 | Scroll to first errored field after submit, or list fields in alert |
| T&C dialog opens before content loads, no spinner | Confirmation.js:51-59 | Add spinner inside `DialogContent` while `content === ''` |
| Silent form reset when `hasMixedPassengerCounts` clears | index.js:184-200 | Show 1-line notice: "Assignment step removed" |
| 500ms hardcoded `setTimeout` before Formik submit, no feedback | index.js:862,870 | Show loading spinner on Next button during delay |
| Hidden instruction on mobile: `hidden sm:inline` in Confirmation | Confirmation.js:144 | Remove `hidden` or use collapsible info banner at all widths |

### Design System

| Issue | File | Fix |
|-------|------|-----|
| Inter never applied globally — body uses system font stack | `globals.css` | Set `font-family: var(--font-inter)` on `body` |
| `globals.css` `.form-control` = `0.8rem` — below DS base 16px | `globals.css` | `font-size: 1rem` or remove override |
| `AlertMessage` component exists but PaymentComponent uses raw MUI Alert | `PaymentComponent.js` | Reuse `/components/UI/AlertMessage.js` |
| NavBar MUI `sx` uses `fontSize: '12px'`, `minHeight: "36px"` inline | `CheckOutNavBar.js` | Use Tailwind `text-xs` / DS spacing tokens |

---

## Low-Priority Polish

| Issue | File:Line | Fix |
|-------|-----------|-----|
| `line-height: 1.42rem` — should be unitless | CheckOutSideBar.module.css:4 | `line-height: 1.42` |
| 7 commented-out CSS blocks | Passengers:22,24,65 / FlightInfoForm:22,57 / Confirmation:22 / SideBar:24-25 | Delete |
| `Itineraries.module.css` only has hide/show — near-empty | Itineraries.module.css | Consolidate to shared utility class or delete |
| `aria-label` on tabs encodes full validation state text | CheckOutNavBar.js:96-103 | Use `aria-disabled` instead; keep label static |
| Typo `PassemgerDetails` (missing 'n') | Confirmation.js:123 | Rename file + component to `PassengerDetails` |
| Mobile padding `px-2` = 8px too tight on main container | index.js:898 | `px-4` minimum (16px) |
| Double info icon: MUI Alert `InfoIcon` + `ℹ️` emoji in body text | Confirmation.js:95 | Remove emoji from string |
| Dynamic `aria-label` reads full state string on every focus | CheckOutNavBar.js | Use `aria-disabled` + static label |
| `bg-gradient-to-br from-gray-700 to-gray-800` — raw Tailwind, no DS gradient | EnhancedTripCard.js | Document or remove |
| `gray-*` Tailwind scale used directly — DS neutral scale not registered | EnhancedTripCard.js, TotalCartSummary.js | Register neutral scale in tailwind.config or document bypass |
| `#4267b3` in `CheckOutNavBar.module.css:17` — dead code (file never imported) | CheckOutNavBar.module.css | Delete file; not a live violation |

---

## Design System Compliance

### Overall Score

| Dimension | Score | Main Issue |
|-----------|-------|------------|
| Colors | 4/10 | Bootstrap palette in globals.css; 15+ violations |
| Spacing | 7/10 | NavBar `sx` px leaks; mostly Tailwind-correct in steps |
| Typography | 5/10 | Inter never global; system font overrides; inline px |
| Components | 6/10 | Shared AlertMessage/Modal used; Button primitive missing; inline `<button>` reinvention |

### Color Violations Summary (non-DS values)

`#4CAF50`, `color: red`, `#616771`, `#4267b3`, `#CACACA`, `#eaeaea`, `#007bff`, `#6c757d`, `#28a745`, `#dc3545`, `#ffc107`, `#17a2b8`, `#343a40`, `#4b4b4b` — 14 violations across checkout + globals

---

## What Works Well

- Forward tab nav correctly gated on `isCurrentStepValid` — prevents step skipping
- Backward nav always open — correct for booking flow
- Guest mode banner persistent with "Clear My Data" CTA + success feedback
- SessionStorage recovery after refresh with cart-ID verification + 30-min TTL — robust
- `formStep >= N` render pattern preserves form state across navigation (no remount)
- QR payment cancel dialog prevents accidental session drop
- Step validation in `useStepValidation` hook — clean separation, easy to audit
- `text-fb-blue` Tailwind token correctly maps to `brand.primary` — one consistent DS usage

---

## Items to NOT Add

- Do not add neutral color scale to tailwind.config without auditing all existing `gray-*` usage — risk of visual regressions
- Do not replace MUI Tabs in NavBar wholesale — only "Back to search" needs extraction; rest of tab navigation logic is sound
- Do not consolidate Passengers + FlightInfoForm modules without checking that `PassengerAssignment.js` and `FlightInfoForm.js` both import from their own modules (not shared)

---

## Related

- `docs/design/DESIGN_SYSTEM.md` — token definitions
- `tailwind.config.js` — extend for `./helpers/**` content path
- `helpers/designSystem.js` — DS constants (currently purged in prod)
- `styles/globals.css` — Bootstrap badge classes to migrate
- `pages/_app.js` — add `StyledEngineProvider injectFirst` for Tailwind↔MUI fix
- `08-archive/homepage-uxui-audit-2026-05-31.md` — previous audit for pattern reference
- MUI docs: https://mui.com/material-ui/guides/interoperability/#tailwind-css

## Related Atoms (Extracted 2026-06-13)
- [[mui-emotion-tailwind-injectfirst]] — `<StyledEngineProvider injectFirst>` + add `helpers/**/*` to tailwind content array
- [[migrate-bootstrap-palette-to-ds-tokens]] — replace Bootstrap legacy palette with `COLORS.status.*` tokens
