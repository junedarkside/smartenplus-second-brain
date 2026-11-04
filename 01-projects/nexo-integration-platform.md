# Nexo — SmartEnPlus Integration Platform

## Summary
Standalone Django backend that integrates external transport operators (Lomprayah, SPC Thailand) with SmartEnPlus via one normalized API. Repo: `/Users/charuwatnaranong/Desktop/SmartEnPlus/Nexo`, GitHub `junedarkside/nexo` (private, branches `main` + `develop`).

## Status
Phase 1 done, Phase 2 Lomprayah read-only done (2026-11-03). GitHub `junedarkside/nexo` (private): `develop` is the working branch (`e29a4d5`), `main` is **owner-only** (Claude never commits, pushes or merges it). Django 5.2 + DRF; `apps/{core,providers,mappings,locations,availability}`; `integrations/{base,lomprayah}`; 162 tests + ruff green.
- **API v1** (docs in repo `docs/api.md`, ADR 0002): `GET /api/v1/providers/{slug}/stations/` and `/availability/`, per-caller hashed API keys, error envelope, stations cache (fresh 1 h, stale 24 h), availability cache 45 s (10 s when UNKNOWN), 20 live provider calls/min cap. Lomprayah capabilities are seeded UNVERIFIED + disabled, so endpoints return 403 until the owner enables them.
- **Live test passed** (real Lomprayah, 2 calls, no 429): 39 stations; Bangkok to Koh Tao and Chumphon to Koh Nangyuan returned departures with seats; cache repeat call 0.017 s.
- **Per-customer IDs (ADR 0003, 2026-11-03):** each customer (ApiClient) owns its IDs; mappings, the API (caller sees only its own `central_id`) and the staff mapping page `/admin/stations/<provider>/<client_id>/` are scoped to it. Picker list comes from `ApiClient.stations_url` (https, public IPs only; SmartEnPlus: its public `/api/v1/stations/`). CSV import for customers without an endpoint = slice 2, not built.
- **Local dev:** `make run` (migrate + server on :8001), `make dev-key` (writes `DEV_API_KEY` to git-ignored `.env`), `make lomprayah-on|off`, dev console at `http://localhost:8001/dev/` (SmartEnPlus BE on :8000) (DEBUG only, prefilled key, auto-loads stations). No superuser needed except for Django Admin.
- **Not verified:** Lomprayah has not confirmed `availableAllotment` meaning or allowed automated access, real rate limit unknown (20/min and 60/min are guesses).
- **Next:** JSON 404 handler for unknown URLs, sort departures by time, draft Lomprayah partner-API request, SPC (blocked on docs and credentials).

**Lomprayah (2026-11-03):** only 3 unofficial website endpoints known (source-station, destination-station, quota). Reverse-documented in repo `docs/providers/lomprayah-api-reference.md` (tags observed/inferred/unknown). Owner: **Lomprayah provides seat availability only** — booking UNSUPPORTED, so no booking machinery for Lomprayah; Phase 4 booking = SPC only. `availableAllotment` >0 AVAILABLE, 0 UNAVAILABLE; 429/timeout/missing items = UNKNOWN. Rate limit hit (429 after ~20 calls at 0.4s). Timetable sample matched API times; overnight timetable uses arrival date, API `travelDate` = departure date. Open: permission for automated access, official partner API.

## Deploy to Coolify (LIVE 2026-11-04)
- Running at `https://nexo.smartenplus.co.th` on the shared Coolify VPS. Compose app `nexo-api` (`web` + `redis`, file `docker-compose.coolify.yml`, branch `develop`, deploy key, Auto deploy off) plus a separate Postgres 16 **Database resource** `nexo-postgres` with a daily backup to its own private R2 bucket `nexo-db-backups`. One `web` replica only (migrate runs on start). Hosting facts and UI lessons: Coolify base `projects/nexo.md` and `coolify/gotchas.md` section C.
- Verified from outside: health 200, Let's Encrypt certificate, HTTP redirects to HTTPS (302), static 200, ports 8000/5432/6379 closed, admin login works, HSTS `max-age=3600`.
- Verified backups: object present in R2, restore drill passed (52 KB dump restored into a throwaway local postgres:16; 16 tables, user, 26 migrations, API key, capabilities intact). First scheduled run still to check (2026-11-05).
- Lomprayah `stations` capability enabled by owner (evidence source: repo reference doc, still observed not verified); live fetch through Nexo with an API key returned the station list, all `central_id` null (nothing mapped yet).
- Lessons that cost time (all in repo history and Coolify base): `${VAR:?}` in the compose file fails Coolify's build step (now `${VAR:-}`); a Coolify variable with the same name as the compose key is locked as "Derived in Compose" (now `PUBLIC_HOSTNAME`); a mistyped variable name (`SECURE_HSTS`) silently does nothing, so check with `printenv` in the container.
- Open: HSTS to 31536000 after about a week, uptime monitor, real ApiClient name and Station list URL in prod Django Admin, repo `docs/deploy-coolify.md` still describes older UI names.

## Risks (owner-finalized 2026-11-04, from BD + UX agent review)
1. **Unofficial endpoints.** Only 3 website endpoints, no permission for automated access. Can be blocked or changed anytime. 429 seen after about 20 calls.
2. **Guessed numbers.** Cache 45 s, client throttle 60/min, provider cap 20/min. No single-flight, so many users on one route can exhaust the cap and return UNKNOWN.
3. **SPC blocked.** Only booking provider. No docs, credentials or sandbox, so no start date for the revenue phase.
4. **Seat meaning unconfirmed.** `availableAllotment` unverified. A seat count that is not real stock hurts trust.
5. **Ops gaps.** No uptime monitor, HSTS at 1 h, auto deploy off.
6. **One-person mapping.** Proposer can also approve (warning only). A wrong mapping sends customers to the wrong place.

**Mapping page (2026-11-04):** menu link added (Admin > Mappings > "Map <provider> stations", `develop` `cc9f959`, needs Coolify redeploy). No station mapped yet in prod. UX review ideas, not built: row anchor after save, search box, clickable status counts, next-pending review jump, open "not in list" box when picker fails, CSV export, same-name flag in picker. Validation idea: 2-3 staff map 10 stations, measure wrong-ID rate.

## Why it exists
SmartEnPlus should not learn each provider's API format, auth, availability or booking payload. Provider logic isolated in one modular monolith so adding an operator = new module, not new infra.

## Non-negotiables (full rules in repo `CLAUDE.md`; engineering rules = section 17)
- **Each customer owns its own Central IDs** (station, route; SmartEnPlus is the first, ADR 0003). Platform only stores them as references in per-customer mapping records; never generates, edits, or retires them. Reports missing/invalid IDs back to the owning customer.
- Provider IDs stay separate, stored as strings.
- Modular monolith: one Django app, one PostgreSQL, one Redis. No per-provider services.
- Availability is exactly `AVAILABLE` / `UNAVAILABLE` / `UNKNOWN`; missing data is never zero stock.
- Booking: persist attempt first, caller idempotency key, no blind retry after timeout, uncertain outcome = `UNKNOWN`/`PENDING_RECONCILIATION`, never auto-`CONFIRMED`.
- Capabilities per provider: `SUPPORTED` / `UNSUPPORTED` / `UNVERIFIED` + enabled flag. Only verified+enabled in prod.

## Stack
Python/Django, DRF, PostgreSQL, Redis, Celery (only when justified), HTTPX, Docker Compose, Coolify, Django Admin. Deploy know-how: see Coolify base vault (`/Users/charuwatnaranong/Desktop/Projects/Coolify`).

## Phases
1. Foundation (Django, PG, settings, API versioning, provider registry, mapping foundation, Docker Compose)
2. Read-only: Lomprayah stations + quota investigation; SPC auth/locations/routes; mapping workflow
3. Availability (confirm inventory semantics first)
4. Booking (SPC end to end, idempotency, reconciliation)

## Open
Owner decisions: key rotation/expiry policy for prod, Coolify network private or public, when to enable Lomprayah capabilities in prod, second customer and whether it needs the CSV import, SPC docs/credentials, mapping approver rule. Tracked in repo `docs/open-questions.md`.

## Related
- Repo ADR 0001: Central ID ownership + modular monolith (`docs/decisions/0001-...`); ADR 0003: per-customer station IDs (`docs/decisions/0003-...`)
- [[architecture]] — main SmartEnPlus architecture
- [[backend-architecture]] — SmartEnPlus Django backend (consumer of this API)
