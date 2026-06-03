# Admin Dashboard — Component Patterns

Formik+Yup, RTK Query, MUI patterns, critical gotchas.

## Formik + Yup

- `buildContractValidationSchema()` — aggregates field schemas per category
- `transformContractFormValues()` — Formik → API payload, handles all category rules
- `toNullableNumber()` — always for Django IntegerFields (empty string = 500)
- Time fields: `TimePicker` stores `"HH:mm:ss"` string. Never `Yup.date()` — use `Yup.mixed()` with custom test. Handle both `Date` (initial load) and `string` (after pick).

## RTK Query

- All list endpoints: `transformResponse: (r) => r?.results ?? r` — handles paginated + legacy flat `[]`
- Lazy hooks: explicitly destructure from exports: `useLazyValidateImageDeletionQuery`
- `keepUnusedDataFor: 60`, `refetchOnMountOrArgChange`, tag cache invalidation
- Raw `axios` + `fetchDataFromApi` deprecated. All pages use RTK Query hooks.
- Dashboard migrated 2026-05-20: 3 RTK hooks replace 12 useState + useEffect + axios calls. Hooks run in parallel.
- New slice pattern: `store/api/dashboardApi.js` for dashboard-only endpoints

### Dashboard Data Sources

| Hook | Endpoint | Slice |
|------|----------|-------|
| `useGetDashboardStatsQuery()` | `/api/user/list-users/` | `dashboardApi` |
| `useGetTripsQuery({ page, pageSize })` | `/admin-dashboard-routes/trips/` | `tripsApi` |
| `useGetDashboardBookingsQuery()` | `/admin-dashboard/booking-summary/` | `dashboardApi` |

### Store Registration
New RTK Query slice: import → reducerPath → blacklist → middleware concat. See `store/index.js`.

## MUI Gotchas

- Tel Input needs transpilation (`next.config.js`)
- Date pickers: `AdapterDateFns`, not dayjs/moment
- Duplicate `sx` props — second overwrites first. Merge into single object.
- `ImagePreviewModal` needs explicit `width`/`height` on desktop — `fill` on `next/image` requires parent dimensions

## React Patterns

- `ImageCard` uses `React.memo` with custom comparator — include `onImageClick` or stale closure
- `ImageCard` + `DraggableImageCard` — `imageError` resets via `useEffect([src])` / `useEffect([imageItem.image])`. Do NOT remove — permanent grey-box if missing.
- `OperatorImages` reads `imagesRef.current` (not `dataImages`) in `handleAddClick` — stale closure guard

## Critical Gotchas

- `reactStrictMode false` — bugs surface in production only
- Two API URLs — `NEXT_PUBLIC_API_URL` vs `NEXT_PUBLIC_API_URL_CLIENT` (cart)
- `@/*` alias → project root (`jsconfig.json`)
- S3 images need remote patterns in `next.config.js`
- `formData.append('field', false)` → empty string. Use `String(false)`.
- `LocationSelector` single mode returns `id` not array — match `value` prop type
- Order status: `orderFilterOptions.js` + `orderStatusConstants.js` must stay in sync. Missing status = unfiltered + grey chip.

## Related
- [[nextjs-patterns]]
- [[admin-dashboard-contracts]]
