# SmartEnPlus — Architecture

## Summary
Pages Router Next.js 14 app. Redux state management. RTK Query for API. Component-based UI with MUI + Tailwind. Frontend only — for backend architecture, see [[backend-architecture]].

## Pages Router Structure
- `/pages/_app.js` — providers (Redux, theme, auth)
- `/pages/api/` — API routes
- Dynamic routes: `[...slug].js` for trip detail pages

## Redux Slices
`passenger` `cart` `location` `calendar` `paymentStatus` `searchFormUI` `authentication` `checkout` `ui` `dayTrip`

Key: `checkout` slice owns `isGuestMode`. `cart` slice owns cart items. Never cross-contaminate.

## RTK Query APIs
`api-slice` (base) · `tripsApi` · `dayTripsApi` · `bookingsApi` · `accountApi` · `familyApi` · `recommendationsApi` `blogApi`

Important: `refetchOnMountOrArgChange: false` — prevents 429 errors. Use `skip` for conditional queries. Transform in RTK, not components.

## Component Tree
```
/components/
├── UI/         # Reusable UI primitives
├── forms/      # Forms + checkout flow
├── trips/      # Trip browse/detail
├── daytrips/   # Day trip browse/detail
├── search/     # Search
├── bookings/   # Booking management
├── layout/     # Header/footer/nav
├── cart/       # Cart
├── checkout/   # Checkout flow
├── payment/    # Payment forms
├── passenger/  # Passenger selection
├── auth/       # Authentication
└── HOC/        # Higher-order components
```

## Data Flow
1. RTK Query fetches data → Redux store
2. Container components read from store via hooks
3. Presentational components receive props
4. User actions → dispatch → RTK mutation → API → invalidate tags → refetch

## Key Patterns
- **DatePicker:** Date objects in Formik, format to string ONLY when sending to API
- **Error handling:** Helpers return `null` + `console.warn`, never throw
- **Operational day:** `isOperationalDay(date, operational_days)` — never inline
- **Free label:** `formatPriceWithFree()` for zero/missing rates
- **Contract fetch loading:** Pass `isContractFetching` bool through component chain
- **Dynamic imports:** `next/dynamic` + `ssr: false` for heavy components
- **State rule:** `useState` for UI-only, Redux for cross-component. Max 3 prop levels → Redux

## Component Constraints
- Max 200 lines per component
- Named exports only
- Fetch in parent, pass as props
- Hook when logic >20 lines or reused
- Never nest component definitions

## Related
- [[README]]
- [[payment-system]]
- [[checkout-flow]]
- [[nextjs-patterns]]
- [[backend-architecture]]

## Cross-Cutting Knowledge Atoms (Linked 2026-06-13)

Architecture hub references for orphan knowledge notes consolidated here:

### Backend
- [[django-booking-creation-validation-gate]] — booking creation validation gate
- [[django-celery-beat-database-scheduler]] — Celery Beat DatabaseScheduler pattern
- [[toctou-select-for-update-before-api-call]] — TOCTOU guard: select_for_update before external API call
- [[omise-attributes-dict-extraction]] — Omise SDK `_attributes` dict extraction
- [[payment-idempotency-key-cart-total]] — H3: `X-Idempotency-Key: ${cartId}:${total}` + wrapped response shape
- [[api-mirroring-pattern-new-features]] — cross-cutting API mirroring for new features
- [[site-url-config-pattern]] — site URL config (`baseURL` vs `NEXT_PUBLIC_DOMAIN`)

### Frontend
- [[frontend-debug-utilities]] — dev-tooling utilities overview
- [[next-font-self-host-perf-pattern]] — `next/font/google` self-host migration
- [[react-hooks-rules-lowercase-component]] — React hooks rules: lowercase component name gotcha
- [[two-surface-parity-shared-module]] — two-surface parity shared module pattern
- [[usedayTripFilters-hydration-spurious-push]] — `useDayTripFilters` pre-hydration query read
- [[touch-target-44px-enforcement]] — 44px touch target enforcement
- [[star-aria-radiogroup-pattern]] — star rating ARIA radiogroup a11y
- [[adaptive-header-route-type-pattern]] — Type A/B header route-type pattern
- [[hero-back-share-buttons-2row-header-fix]] — hero back/share buttons 2-row header fix

### Recommendations
- [[django-m2m-location-join-recommendations]] — M2M location JOIN for recommendations engine

### API Reference
- [[api-endpoints]] — SmartEnPlus API endpoint reference (status codes, request/response shapes)
