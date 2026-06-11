# Frontend Architecture Audit (2026-06-11)

## Summary

Full architecture audit of `smartenplus-frontend` (state management, components, data fetching, performance, maintainability). 3 Explore agents + main-thread hand-verification of every High/Medium claim. Result: **3 confirmed latent bugs, 2 confirmed duplication issues, 1 dead-code cluster (6 items, all grep-verified), 1 repo-hygiene cluster, 4 explorer findings overturned.** No critical user-facing bugs — architecture is fundamentally sound. Checkout/payment logic excluded (covered by [[booking-payment-e2e-audit-2026-06-11]], verified twice same day).

## Scope & Method

- Codebase shape: ~1138 JS files, 525 components, 89 pages, 13 Redux slices + 8 RTK Query APIs, ~40 hooks, 2 contexts.
- Explorer findings treated as candidates only; each verified by direct read + grep before classification. Audit spec: fewest high-impact findings, highest confidence; "not best practice" alone disqualified.

## Confirmed Bugs (all latent — no current user impact, real traps)

### 1. MEDIUM — dead auth branch in tripsApi + dayTripsApi (Bug, latent)
`store/api/tripsApi.js:15` and `store/api/dayTripsApi.js:42` read `const { session } = getState()` — but session lives in NextAuth, never in Redux (`store/index.js:31-46` registers no session reducer). Authorization header is NEVER attached.
**Why latent:** all currently-used endpoints in both APIs are public browse endpoints; `createBooking` mutation (dayTripsApi.js:136) has zero callers (grep-verified).
**Impact:** future dev adds an authenticated endpoint to either API and assumes the auth branch works → silent 401s. Contrast: `bookingsApi.js:11` does it correctly via `await getSession()`.
**Fix:** copy the `getSession()` pattern from bookingsApi, or delete both dead auth branches.

### 2. LOW — dayTripsApi reads wrong store key for language (Bug, latent)
`store/api/dayTripsApi.js:35`: `const { dayTrip } = getState()` — slice is registered as `activities` (`store/index.js:44`), so `dayTrip` is always undefined and Accept-Language is always `'en'`.
**Why latent:** `setSelectedLanguage` reducer (`dayTripSlice.js:99`) is never dispatched from any UI (grep-verified); `useDayTripData.js:13` uses local useState instead.
**Fix:** `const { activities } = getState()` — one word. Do this whenever language selection gets wired up.

### 3. MEDIUM (latent, NOT critical) — useEffect inside Formik render prop (Bug)
`components/forms/checkout/Passengers.js:629` and `:706` — two `useEffect` calls inside the `{({ values, setFieldValue }) => {...}}` render callback, with `eslint-disable react-hooks/rules-of-hooks` mislabeling it "a valid pattern".
**Debug-mantra falsification (2026-06-11):** traced Formik 2.2.9 source — `formik.cjs.development.js:1097` invokes `children(formikbag)` as a **plain function call inside `Formik(props)`'s own body**, so both effects register on **Formik's fiber**, not a child. Three hypotheses tested:
- "child fiber, safe" → DISPROVEN (plain call).
- "crashes today" → DISPROVEN: `Passengers.js:602` early-returns the skeleton BEFORE `<Formik>` mounts; only 2 unconditional effects in the render prop, nothing conditional between 625–706; Formik calls children once per render unconditionally → Formik hook count is **constant**, mount/unmount via the line-602 gate resets cleanly. **No crash now.**
- "harmless" → PARTIAL: no crash, but genuinely against rules-of-hooks.
**Real impact (refined):** (a) any future edit inserting a conditional hook / early-return / extra hook between line 625 and the effects flips Formik's hook count → "Rendered more/fewer hooks" crash in the checkout passenger step; the 1122-line file makes that plausible. (b) the `eslint-disable` comment actively misleads the next dev by calling it valid. (c) effects close over `Passengers` vars while living on Formik's fiber — brittle, works only because the arrow re-closes each render. No test guards this — `Passengers.integration.test.js` fails to load (mui-tel-input ESM, per [[frontend-test-infrastructure-audit-2026-06-03]]).
**Fix:** extract both effects into a top-level `<FormikValuesSync/>` child rendered inside `<Formik>`, reading values via `useFormikContext()` — moves hooks to their own stable fiber, deletes both eslint-disable lies, zero behavior change. Effect bodies (629–699 sync, 706–729 ghost-data check) move verbatim.

## Confirmed Duplication

### 4. LOW — bumpCartVersion defined twice with manual-sync comment
`store/api/api-slice.js:7-11` and `store/index.js:210/232` — identical `CART_VERSION_KEY` + `bumpCartVersion` (cross-tab cart sync). api-slice.js:6 says "Must stay in sync with bumpCartVersion in store/index.js" — the duplication was a circular-import workaround. The `store/index.js` export has zero importers (grep-verified); api-slice copy is used 3×; index.js copy powers the storage-event listener (line 219).
**Impact:** edit one copy, cross-tab cart sync silently breaks.
**Fix:** extract to `store/cart-version.js` (≈8 lines), import in both. Kills the circular-import problem and the sync comment.

### 5. CLEANUP — createCart double cache invalidation
`store/api/api-slice.js:70` (`invalidatesTags` LIST) + `:76-79` (manual `invalidateTags` of LIST again + cart id inside `onQueryStarted`). Two invalidation passes per cart creation.
**Fix:** single `invalidatesTags: (result) => [{type:'Cart', id: result?.id}, {type:'Cart', id:'LIST'}]`; keep only `bumpCartVersion()` in onQueryStarted.

### 6. LOW — three date-helper files with overlapping concerns
`helpers/Date.js` (React component, miscategorized in /helpers), `helpers/dateHelper.js` (`getDateString`, `calculateAge`…), `helpers/dateUtils.js` (`formatDate`, `formatIsoDate`…). No single source of truth for date formatting.
**Fix:** consolidate opportunistically when next touching date logic — not worth a dedicated PR.

## Dead Code (all zero-reference, grep-verified ex node_modules/.next/tests)

| Item | Note |
|---|---|
| `components/lines*/` | literal `*` in dirname; contains `line-list copy.js` |
| `components/omisecharge/OmiseCharge.js` | superseded by `components/payment/OmiseScriptLoader.js` |
| `components/UI/GridComponent2.js` | fork of active GridComponent, never imported |
| `store/migrations/cart-migration-v1.js` | superseded by inline migrations in `store/index.js:62-168` |
| `dummy-data.js` (root) | zero refs |
| `hooks/use-http.js` | NOT dead — 1 caller (`components/autocompletesearch/ApiRequest.js`); legacy axios layer beside RTK Query. Migrate only when touching autocomplete. |

**Fix:** delete first 5 in one cleanup commit (~10 min, zero risk).

## Repo Hygiene (CLEANUP — all git-tracked, verified via `git ls-files`)

- 5 `.backup` files: `components/UI/FeaturedImageHeader.backup.js`, `components/bookings/BookingDetail.js.backup`, `utils/blog/breadcrumbUtils.js.backup`, `lib/homepage/components/PopularRoutesSection.js.backup`, `DAYTRIP_BACKEND_REQUIREMENTS.md.backup`
- Build artifacts tracked: `dev.log`, `build-output.log` (.gitignore lacks `*.log` general pattern + `*.backup`)
- Backend material in frontend repo: `db/` (3 SQL scripts), `data/view-counts.json`, `PAGINATION_BACKEND_CHANGE.diff`, `RESUME_CART_SYNC_FIX.sh`
- 4 stale root design docs: `HEADER_REDESIGN_2026.md`, `HOMEPAGE_REDESIGN_2026.md`, `POPULAR_ROUTES_REDESIGN_2026.md`, `homepage-refinement-2026.md` → move to `docs/archive/`

**Fix:** one hygiene commit: `git rm` + add `*.backup`, `*.log`, `dev.log` to .gitignore.

## Design Decisions / Tech Debt (documented to prevent re-flagging)

- **Oversized files** — `pages/checkout/index.js` (1200), `Passengers.js` (1122), `SlideCalendar2.js` (1035), `PaymentComponent.js` (787) violate the project's own 200-line rule. Audit found NO concrete cost beyond finding 3 — no merge-conflict history, no duplicated internal logic worth extracting. **Ruling: refactor only when touching; no dedicated refactor PR.** Splitting working checkout code carries more risk than the size does.
- **PersistGate not wrapping `<Component>`** (`_app.js:90-97`) — known candidate C1 in [[booking-payment-e2e-audit-2026-06-11]]; pages handle rehydration manually. Not relitigated here.
- **Mixed `refetchOnMountOrArgChange`** — intentional 429 protection (documented per call site). Not a sync bug.
- **`CLAUDE.original.md`** — intentional caveman:compress backup, not clutter.
- **Slice file naming** (kebab `cart-slice.js` vs camel `dayTripSlice.js` vs snake `sync_storage.js`) — style only, zero functional cost. Fix opportunistically on rename, never as dedicated change.
- **Versioned components** (`TripDetail2`, `ProductSearchForm2`, `CalendarDatePickerv2`) — both versions verified active on different routes; NOT duplication. GridComponent2 was the only dead fork.
- **`components/dev/` + `components/debug/`** — gated by `DevToolsProvider` early-return in prod; RTKQueryInspector loaded via `next/dynamic` (code-split). Bundle impact unverified candidate, likely small. No action.

## Overturned Findings (explorer claims — record per audit discipline)

1. "tripsApi/dayTripsApi auth bug → all trips requests 401 for logged-in users" — OVERSTATED: all used endpoints public, no current failure. Downgraded to latent (finding 1).
2. "main-header.js:55 `cloneElement(searchBarContent, {stacked:true})` breaks memoization, hot-path re-renders" — FALSE: the object is the props *bag*, spread into the element; child receives primitive `stacked: true`. React.memo compares individual props, and JSX creates new elements per render anyway. Memoizing the bag changes nothing.
3. "HeaderSearchContext useMemo missing setter deps defeats memoization" — FALSE: useState setters are referentially stable; adding them to deps is a no-op.
4. "Passengers.js hooks violation is Critical, may already throw in production" — OVERSTATED: both effects unconditional → hook order stable today. Real but latent (finding 3).

## Verdict

No architecture change needed. Redux/RTK Query split is coherent, persistence migrations work (v4-v7 verified), resetStore covers all slices, contexts properly memoized, effect cleanup correct in all spot-checked listeners. Highest-value actions, in order: finding 3 (checkout crash trap), finding 1 (auth trap), finding 4 (cart-sync trap), then one dead-code + one hygiene commit.

## Related

[[booking-payment-e2e-audit-2026-06-11]] · [[architecture]] · [[frontend-test-infrastructure-audit-2026-06-03]] · [[payment-checkout-architecture-audit]] · [[people-also-book-checkout-audit]]
