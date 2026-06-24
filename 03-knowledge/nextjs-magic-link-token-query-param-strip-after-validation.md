# nextjs-magic-link-token-query-param-strip-after-validation

## Summary
In Next.js Pages Router, pass ephemeral credentials (magic-link/OTA tokens) as a query param (`/my-trip?token=`), validate in `getServerSideProps`, then `router.replace` to strip `?token=` before rendering PII. Never use a route segment (`/my-trip/[token]`).

## Why It Matters
Route segments trigger ISR prerender + SEO crawls with invalid/expired tokens → error noise + wasted compute. A token left in the URL leaks into server logs, CDN logs, and `document.referrer` (exposed to any third-party script or link navigation) — a PII/credential disclosure. Stripping after validation closes the leak with one line.

## Detail
```jsx
// pages/my-trip.js — query param, NOT [token] route segment
export async function getServerSideProps(context) {
  const token = context.query.token;
  const data = await validateToken(token); // SSR, no client waterfall
  if (!data) return { notFound: true };
  return { props: { data } };
}

export default function MyTrip({ data }) {
  const router = useRouter();
  useEffect(() => {
    router.replace('/my-trip', undefined, { shallow: true }); // strip ?token=
  }, []);
  return <TripView data={data} />;
}
```

## Constraints / Gotchas
- `router.replace` (not `push`) — no back-button re-add of the token. `shallow: true` avoids a re-fetch.
- Validate server-side (getServerSideProps) so the token never reaches the client bundle unvalidated.
- Token bound to email = read-only scope; elevate to `booking_id` binding for write-access tokens.

## Related
- [[ota-portal-review]] — P3a + Q10 source
- [[ota-magic-link-trip-view]]
