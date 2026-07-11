# Command Centre — Direct Requests Pending-Count Pill

## Summary
Surface the count of `pending` customer requests as a numeric pill on (1) the **Direct Requests** tab label and (2) the **Command Centre** sidemenu item. Both pills show the same number.

## Context
Admins at `/dashboard/command-centre` must click into the **Direct Requests** tab to discover how many customer requests are still `pending`. The sidemenu "Command Centre" entry gives no signal either, so a new pending request can sit unseen until an admin happens to visit the page. A visible count pill on both surfaces makes the triage queue glanceable from anywhere in the dashboard.

## Current state (audited 2026-07-11)

The feature is almost entirely wired already — only the data plumbing is missing:

| Surface | Status | Evidence |
|---|---|---|
| Sidemenu badge UI | **Already exists** | `admin-dashboard/components/sidemenu/SideBarListMenu.js:173,228` — `<Badge badgeContent={badgeCounts[menu.path] \|\| 0} color="error" max={99}>` wraps every menu icon |
| Sidemenu badge source | **Only `/cs` unread wired** | `admin-dashboard/pages/dashboard/SideList.js:169` — `badgeCounts = totalUnread > 0 ? { '/cs': totalUnread } : {}` |
| Command Centre menu entry | path = `/dashboard/command-centre` | `admin-dashboard/components/sidemenu/menuData.js:104-109` |
| Direct Requests tab label | **Plain, no badge** | `admin-dashboard/pages/dashboard/command-centre/index.js:1201` — `<Tab label="Direct Requests" />` |
| Pending data query | **Reusable, shared RTK cache** | `useGetCustomerRequestsQuery({request_status:'pending'})` (`store/api/ordersApi.js:190`) → `GET /admin-dashboard-tickets/tickets/?request_status=pending`; `transformResponse` → flat array; `providesTags:['Ticket']`; `keepUnusedDataFor:30` |
| Pending count derivation | **Already inline in the tab** | `command-centre/index.js:165` — `pendingRequests = tickets.filter(t => t.request_type)` |
| Status-change refresh | **Already wired** | `store/api/ordersApi.js:216` — `updateRequestStatus` mutation `invalidatesTags: ['Ticket']` |

**Conclusion:** ~3 small FE edits, **zero backend change**. Badge UI, query, count derivation, and cache-invalidation refresh all exist — only the wiring between them is missing.

## Implementation (3 edits, admin-dashboard repo)

### Edit 1 — `pages/dashboard/SideList.js` (sidemenu pill, all dashboard pages)
Mount the pending-count query at layout level so the pill shows on every page.
- Import `useGetCustomerRequestsQuery` from `@/store/api/ordersApi`.
- In `SideList`, mount it with the **same args as the command-centre tab** so RTK dedupes to one network call:
  ```js
  const { data: pendingTickets = [] } = useGetCustomerRequestsQuery(
    { request_status: 'pending' },
    { skip: !session || !accessToken }
  )
  const pendingRequestCount = pendingTickets.filter(t => t.request_type).length
  ```
- Extend the existing `badgeCounts` (line 169) to include the Command Centre path:
  ```js
  const badgeCounts = {
    ...(totalUnread > 0 ? { '/cs': totalUnread } : {}),
    ...(pendingRequestCount > 0 ? { '/dashboard/command-centre': pendingRequestCount } : {}),
  }
  ```
`SideBarListMenu` already keys by `menu.path` (`/dashboard/command-centre`) → the pill renders with no UI change.

### Edit 2 — `pages/dashboard/command-centre/index.js` (tab pill)
Lift the count into `CommandCentrePage` so the tab label can display it. The tab body keeps its own query — shared cache, no extra call.
- Import `useGetCustomerRequestsQuery` (ordersApi) + `Badge` (`@mui/material`) into `CommandCentrePage` (line 1178+).
- Mount the query in `CommandCentrePage`:
  ```js
  const { data: pendingTickets = [] } = useGetCustomerRequestsQuery(
    { request_status: 'pending' },
    { skip: !session }
  )
  const pendingRequestCount = pendingTickets.filter(t => t.request_type).length
  ```
- Replace the plain tab label (line 1201):
  ```jsx
  <Tab label={
    <Badge badgeContent={pendingRequestCount || 0} color="error" max={99}
           sx={{ '& .MuiBadge-badge': { right: -14, top: 8 } }}>
      Direct Requests
    </Badge>
  } />
  ```
  (The `sx` nudges the badge clear of the tab text; final offset per design review.)

Both edits use the **identical** count derivation → the two pills are guaranteed equal.

## Decision — refresh policy
**Mount + RTK tag-invalidation.** Count loads when the dashboard layout mounts (sidemenu) and auto-refreshes whenever any admin changes a ticket status, because `updateRequestStatus` already `invalidatesTags: ['Ticket']`, which re-runs every `getCustomerRequests` subscriber.

Rejected alternatives (owner decision, 2026-07-11 — best fit for current resource + stack):
- **Polling (e.g. 60s)** — extra load for marginal gain; new-customer-ticket visibility not worth a constant heartbeat.
- **Supabase realtime** — heaviest; would need a new ticket-insert channel + BE confirmation that ticket inserts are mirrored to Supabase. Overkill for a small triage queue.

Trade-off accepted: a brand-new customer-created ticket only bumps the pill on the **next navigation/refresh**, not in realtime. Acceptable because the triage queue is human-paced.

## Out of scope / future
- **Backend count-only endpoint.** `transformResponse` strips DRF's `{count, results}` to the array, so no count field reaches the FE today. The pending triage queue is small and the shared-cache call is cheap. If the queue ever scales, add a `?count_only` / metadata endpoint instead of loading full rows. Deferred — revisit only if pending volume grows.
- **OTA Bookings / Direct Bookings tab pills** — not requested.
- No code is changed by the author of this note; execution is the dev team's.

## Verification (after dev team implements)
1. `cd admin-dashboard && npm run dev` → open `http://localhost:3001`.
2. **Sidemenu** — log in, land on any dashboard page. With ≥1 pending ticket, "Command Centre" icon shows a red pill with the count; with 0, no pill.
3. **Tab** — go to `/dashboard/command-centre`. "Direct Requests" label shows the same number as the sidemenu pill.
4. **Equality** — open Direct Requests (default filter = pending). Table row count == tab pill == sidemenu pill.
5. **Refresh on action** — resolve/reject a pending ticket from the Review dialog → both pills decrement immediately (no manual refresh).
6. **New ticket** — create a customer request from the frontend → pill updates on next navigation (expected per mount-refresh policy).
7. **Network** — only one `GET .../tickets/?request_status=pending` across sidemenu + tab (shared RTK cache), not duplicated.

## Review (2026-07-11)
Code review verdict: **sound and implementable — no blockers.** 2 doc-accuracy corrections:
1. **"~3 edits" is actually 2** — Edit 1 (SideList.js) and Edit 2 (command-centre/index.js) cover everything; there is no third file.
2. **Shared-cache claim is filter-dependent** — the tab body's own query uses `{request_status: statusFilter || undefined}`, so it dedupes with the pill query only while the filter is `pending` (the default). Changing the filter issues a second distinct call (acceptable). Verification steps 4 and 7 hold only at the default filter.

Notable risks (accepted): query error → pill absent (data falls back to `[]`, same as the existing `/cs` badge); pre-existing redundant `refetch()` at `DirectRequestsTab` line 150 (out of scope, invalidatesTags already covers it).

2 simplifications adopted: `badgeCounts` as a plain object without conditional spreads (`SideBarListMenu` already zero-guards via `|| 0`), and tab `badgeContent` without `|| 0` (count is always an integer; MUI Badge hides at 0 by default).

Dev-ready detail → [[command-centre-pending-badge-implementation]].

## Related
- [[command-centre-pending-badge-implementation]]
- [[command-centre-gap-audit]]
- [[command-centre-ticket-booking-flow]]
- [[command-centre-direct-notify-redesign]]
- [[cs-flat-dict-list-endpoint-pattern]]
