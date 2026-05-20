# Admin Dashboard — Component Patterns

Formik+Yup, RTK Query, MUI patterns, and critical gotchas.

## Formik + Yup

- `buildContractValidationSchema()` — aggregates field schemas per category
- `transformContractFormValues()` — Formik → API payload, handles all category rules
- `toNullableNumber()` — always for Django IntegerFields (empty string = 500)
- Time fields: `TimePicker` stores `"HH:mm:ss"` string. Never use `Yup.date()` — use `Yup.mixed()` with custom test. Handle both `Date` (initial load) and `string` (after pick).

## RTK Query

- All list endpoints: `transformResponse: (r) => r?.results ?? r` — handles paginated `{count, results:[]}` + legacy flat `[]`
- Lazy hooks must be explicitly destructured from exports: `useLazyValidateImageDeletionQuery`
- `keepUnusedDataFor: 60`, `refetchOnMountOrArgChange`, tag cache invalidation
- Every page uses RTK Query hooks — raw `axios` + `fetchDataFromApi` are deprecated. `fetchDataFromApi` only remains in `components/data/utils/fetchData.js` as legacy artifact.
- Dashboard (`pages/dashboard/Main/Main.js`) migrated 2026-05-20: was last page using manual fetching. Pattern: 3 RTK Query hooks replace 12 useState + useEffect + axios calls. Hooks run in parallel automatically.
- New slice pattern: `store/api/dashboardApi.js` for dashboard-only endpoints (`getDashboardStats`, `getDashboardBookings`)

### Dashboard Data Sources

| Hook | Endpoint | Slice |
|------|----------|-------|
| `useGetDashboardStatsQuery()` | `/api/user/list-users/` | `dashboardApi` |
| `useGetTripsQuery({ page, pageSize })` | `/admin-dashboard-routes/trips/` | `tripsApi` |
| `useGetDashboardBookingsQuery()` | `/admin-dashboard/booking-summary/` | `dashboardApi` |

### Store Registration Checklist

When adding new RTK Query slice: import → reducerPath → blacklist → middleware concat. See `store/index.js`.

## MUI Gotchas

- Tel Input needs transpilation (`next.config.js`)
- Date pickers use `AdapterDateFns`, not dayjs/moment
- Duplicate `sx` props — second overwrites first. Merge into single object.
- `ImagePreviewModal` needs explicit `width`/`height` on desktop — `fill` on `next/image` requires parent dimensions

## React Patterns

- `ImageCard` uses `React.memo` with custom comparator — include `onImageClick` in comparison or stale closure results
- `ImageCard` + `DraggableImageCard` — `imageError` resets via `useEffect([src])` / `useEffect([imageItem.image])`. Do NOT remove these — permanent grey-box if missing.
- `OperatorImages` reads `imagesRef.current` (not `dataImages`) in `handleAddClick` — stale closure guard

## Critical Gotchas

- `reactStrictMode false` — bugs surface in production only
- Two API URLs — `NEXT_PUBLIC_API_URL` vs `NEXT_PUBLIC_API_URL_CLIENT` (cart)
- `@/*` alias → project root (`jsconfig.json`)
- S3 images need remote patterns in `next.config.js`
- `formData.append('field', false)` → empty string. Use `String(false)`.
- `LocationSelector` single mode returns `id` not array — match `value` prop type
- Order status: two files must stay in sync — `orderFilterOptions.js` + `orderStatusConstants.js`. Missing status = unfiltered + grey chip.

## Related

- [[nextjs-patterns]] — ISR, dynamic SSR disable, RTK Query conventions
- [[admin-dashboard-contracts]] — Contract form flow, payload rules