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
