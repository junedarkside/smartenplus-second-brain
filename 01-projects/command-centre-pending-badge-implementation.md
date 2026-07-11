# Command Centre Pending Badge — Implementation

Dev-ready edit list, reviewed 2026-07-11. Spec context, rationale, and refresh-policy decision → [[command-centre-pending-badge]].

**Summary:** 2 edits, admin-dashboard repo only, zero backend change.
**Repo:** `/Users/charuwatnaranong/Desktop/AdminDashBoard/admin-dashboard/`

## Edit 1 — `pages/dashboard/SideList.js` (sidemenu pill)

Import `useGetCustomerRequestsQuery` from ordersApi. Mount at the top of `SideList` — `session` (line 81, useSession) and `accessToken` (line 80, Redux) are both already in scope:

```js
const { data: pendingTickets = [] } = useGetCustomerRequestsQuery(
  { request_status: 'pending' },
  { skip: !session || !accessToken }
)
const pendingRequestCount = pendingTickets.filter(t => t.request_type).length
```

Replace line 169 with the simplified form (reviewer-adopted — `SideBarListMenu` already does `badgeContent={badgeCounts[menu.path] || 0}`, so zero values are safe; conditional spreads unnecessary):

```js
const badgeCounts = {
  '/cs': totalUnread,
  '/dashboard/command-centre': pendingRequestCount,
}
```

## Edit 2 — `pages/dashboard/command-centre/index.js` (tab pill)

In `CommandCentrePage` (`session` already at line 1179; skip guard `{ skip: !session }` consistent with the file's existing queries), mount the same query + derivation as Edit 1 — identical args, so it shares the RTK cache entry with the sidemenu mount. Import `Badge` from `@mui/material`.

Replace line 1201 with the simplified form (no `|| 0` — count is always an integer; MUI Badge hides at 0 by default):

```jsx
<Tab label={
  <Badge badgeContent={pendingRequestCount} color="error" max={99}
         sx={{ '& .MuiBadge-badge': { right: -14, top: 8 } }}>
    Direct Requests
  </Badge>
} />
```

## Known behaviors (document, don't fix)

1. **Network:** sidemenu + page-level mounts share ONE call (identical arg `{request_status:'pending'}`). The tab body's own query uses `{request_status: statusFilter || undefined}` (index.js:125-129) — dedupes with the pill query ONLY while `statusFilter='pending'` (the default). Filter change → second distinct call. Acceptable.
2. **Pill == table row count only while tab filter = pending** (default). Filter changed → pill still shows pending count (by design), table shows filtered rows.
3. **Query error → pill absent** (data falls back to `[]`). Same as the existing `/cs` badge. Accepted.
4. **Pre-existing debt, out of scope:** `DirectRequestsTab` line 150 explicit `refetch()` is redundant with `invalidatesTags: ['Ticket']`.

## Verification checklist

1. `cd admin-dashboard && npm run dev` → open `http://localhost:3001`.
2. **Sidemenu** — log in, land on any dashboard page. With ≥1 pending ticket, "Command Centre" shows a red pill with the count; with 0, no pill.
3. **Tab** — go to `/dashboard/command-centre`. "Direct Requests" label shows the same number as the sidemenu pill.
4. **Equality (default filter only)** — open Direct Requests with the filter at its default (`pending`). Table row count == tab pill == sidemenu pill. If the filter is changed, the pills keep showing the pending count while the table shows filtered rows — expected.
5. **Refresh on action** — resolve/reject a pending ticket from the Review dialog → both pills decrement immediately (RTK `'Ticket'` tag invalidation, no manual refresh).
6. **New ticket** — create a customer request from the frontend → pill updates on next navigation (expected per mount-refresh policy).
7. **Network (default filter state)** — one `GET .../tickets/?request_status=pending` across sidemenu + page + tab body (shared RTK cache). Changing the tab filter issues a second, differently-parameterized call — expected, not a regression.

## Related
- [[command-centre-pending-badge]]
- [[command-centre-gap-audit]]
- [[command-centre-ticket-booking-flow]]
