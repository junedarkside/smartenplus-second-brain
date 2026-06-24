# RTK Query: Force Refetch via useRef

When `invalidatesTags` alone doesn't trigger a re-render (stale cache edge case after mutation), expose the `refetch` fn via prop callback + `useRef` in parent.

```js
// Child component
const { data, refetch } = useGetCustomerRequestsQuery(bookingId, { skip: !bookingId });
useEffect(() => { if (onRefetchReady) onRefetchReady(refetch); }, [refetch, onRefetchReady]);

// Parent component
const refetchFn = useRef(null);
<Child onRefetchReady={(fn) => { refetchFn.current = fn; }} />

// On mutation success — call directly, don't wait for tag invalidation
refetchFn.current?.();
```

Surfaced during P1e: `invalidatesTags: ['CustomerRequests']` in `submitChangeRequest` wasn't reliably triggering list refetch when cache was already populated. Direct `refetch()` call = guaranteed.

Pattern lives in: `components/bookings/ChangeRequestsSection.js` + `BookingDetailMain.js` (session #159).
