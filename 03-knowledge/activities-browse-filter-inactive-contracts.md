# Activities Browse — Inactive Contracts Bug

**Root cause:** `ContractViewSet` base queryset has no `is_actived` filter. Frontend never sends `?status=active` param to API.

**Affected:** `pages/activities/index.js` → `/activities?category=DAY_TOUR` shows `is_actived=False` contracts.

**Fix:** `store/api/dayTripsApi.js:54` — add 1 line:
```js
params.append('status', 'active');  // filters is_actived=True on backend
```

No backend change needed. Part of [[activities-day-tour-page-review-2026-06-01]] P0 findings.

## Related
- [[activities-day-tour-page-review-2026-06-01]] — full 14-finding audit
