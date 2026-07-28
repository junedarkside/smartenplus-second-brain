# Personalizing a static/ISR Next.js homepage without cross-user leak

**Context:** SmartEnPlus homepage (`pages/homepagev2.js`, re-exported by `pages/index.js`) is `getStaticProps` + `revalidate` (ISR). The generated HTML is shared across all visitors and the ISR cache persists in a Docker volume (`smartenplus_next_cache`). We needed a logged-in-only "personalized band" (greeting + upcoming trips + rebook) above the discovery content — WITHOUT regressing the guest page.

## The trap

Putting any per-user data into `getStaticProps` bakes it into the shared static HTML → it leaks to every visitor and gets frozen in the ISR volume until revalidation. Server-side personalization on an ISR page is a data-leak bug, not just a caching quirk.

## The pattern (safe)

Client-hydrated band, mounted as a sibling in the page, that **returns `null` for guests**:

```js
// components/FrontPage/PersonalizedHomeBand.js
const PersonalizedHomeBand = () => {
  const { data: session, status } = useSession();
  const skip = status !== 'authenticated' || !session?.id;
  // ...RTK Query hooks with { skip } fire in parallel...
  if (skip) return null;   // guest → renders nothing
  return (/* band */);
};

// homepagev2.js — client-only, never in static HTML
const PersonalizedHomeBand = dynamic(
  () => import('../components/FrontPage/PersonalizedHomeBand'),
  { ssr: false }
);
```

Why it's leak-proof:
- `ssr: false` → the band is never part of the server-rendered/ISR HTML at all.
- `if (skip) return null` → for guests the client renders nothing → guest DOM is **byte-identical** to before. Verified by curling `/` logged-out: 0 band markers, unchanged HTML.
- Auth data is fetched client-side per session → no shared cache, no cross-user bleed.

Same inverse trick to HIDE guest-only sections for logged-in users: add `useSession()` to the page (client hook, does NOT touch `getStaticProps`) and wrap the block in `{!session?.id && (...)}`. Guests still get it in static HTML (SEO intact); logged-in users hide it post-hydration.

## Gotcha found alongside — `/bookingsummary/` tab is NUMERIC

Backend `BookingSummaryViewSet` reads `?tab=` as a numeric string: `'1'`=upcoming (`confirm=True AND traveling_date>=today`), `'2'`=completed, `'3'`=canceled. Passing a semantic string like `tab='upcoming'` does **not** error — the `tab == '1'` check silently fails, the filter is skipped, and the endpoint returns ALL bookings (past + refunded leak in). Always pass `'1'`/`'2'`/`'3'`. Belt-and-suspenders: client-filter with `getBookingStatus(b) === 'confirmed'` (`helpers/bookingStatusHelper.js`) since a refunded row can still carry `confirm=True`.

## Takeaways

- On an ISR/SSG page, personalize on the **client** (`dynamic ssr:false` + null-for-guest), never in `getStaticProps`.
- "Guest output byte-identical" is the acceptance test for no-side-effect on a shared page — verify by diffing logged-out HTML.
- Reuse existing tokenized components (`BookingItemCard`, `StatCard`, shared `Section`) so a new band adds zero design primitives.

Shipped #274 (`feat/home-personalized-band` → develop `a505cfcb`).
