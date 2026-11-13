---
name: sync-ota-bookings-supabase-401
description: OPEN issue seen 2026-11-13 in prod worker logs - Celery task sync_ota_bookings gets Supabase 401 "permission denied for schema gmail12go" and retries. Not caused by the VPS patch. To audit.
metadata:
  type: project
  status: open-needs-audit
  date: 2026-11-13
  parent: ota-sync-supabase-mirror
---

# `sync_ota_bookings`: Supabase 401 (permission denied for schema gmail12go)

## Summary
In the SmartEnPlus prod Celery worker logs (seen 2026-11-13, during the Coolify VPS apt patch), `sync_ota_bookings` fails with Supabase HTTP 401 `permission denied for schema gmail12go` and the task retries. The OTA mirror (`cs.CsOtaBooking`) is probably not refreshing. Customer payments and notifications are not affected (checked: 0 orphan charges, 0 unnotified paid orders after the patch).

## Context
- Task: `cs/tasks.py` `sync_ota_bookings`, beat every 15 min (`Smartenplus/celery.py`). Design in [[ota-sync-supabase-mirror]]; store in [[supabase-ota-booking-store]].
- Django reads Supabase server-side over PostgREST with `SUPABASE_URL` + `SUPABASE_ANON_KEY`. Vault history says the data lives in schema `gmail12go` (table `Information`), read through the `public.view_information` view.
- The patch (docker-ce upgrade + reboot, `coolify/maintenance.md` in the Coolify base vault) restarted all containers. The error is a Supabase-side permission refusal, so a restart does not explain it. Found while reading worker logs; not proven when it started.

## Facts not known yet (audit first)
- First failing run: not checked. Compare with the last good sync (latest `CsOtaBooking.supabase_ingested_at` in prod).
- Whether it failed before 2026-11-12 (before the BE deploy) or only after.
- Whether the retry loop floods the queue or the logs.

## Leads to check (hypotheses, none verified)
1. `SUPABASE_ANON_KEY` or `SUPABASE_URL` in the Coolify env changed or was lost in the EC2 to Coolify move (the BE moved to the VPS on 2026-11-03/04; check against the old EC2 env).
2. Supabase grants: the `anon` role lost `USAGE` on schema `gmail12go`, or the view `public.view_information` runs as invoker and the underlying schema grant was removed (Supabase "exposed schemas" setting, or a security fix by whoever owns the Supabase project).
3. Code reads `gmail12go` directly instead of the `public` view (message names the schema). Read `cs/supabase_client.py`.
4. Supabase project paused or key rotated (401 vs 403: check the exact body and `code`).

## Safe first steps
- Read-only: worker log lines (`docker logs` of the worker, filter `sync_ota_bookings`), `cs/supabase_client.py`, env var names in Coolify (not values).
- One `curl` to the view with the prod anon key from the owner's shell, to see the same 401 outside Django. Never paste the key into chat or the vault.
- No prod writes, no beat changes, no key rotation without the owner.

## Impact
OTA portal and staff views built on `CsOtaBooking` ([[ota-portal-overview]]) may show stale OTA bookings. Direct bookings are unaffected.

## Related
[[ota-sync-supabase-mirror]] · [[supabase-ota-booking-store]] · [[ota-portal-overview]]
