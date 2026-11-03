# Nexo — SmartEnPlus Integration Platform

## Summary
Standalone Django backend that integrates external transport operators (Lomprayah, SPC Thailand) with SmartEnPlus via one normalized API. Repo: `/Users/charuwatnaranong/Desktop/SmartEnPlus/Nexo`, GitHub `junedarkside/nexo` (private, branches `main` + `develop`).

## Status
Phase 1 done, Phase 2 Lomprayah read-only done (2026-11-03). GitHub `junedarkside/nexo` (private): `develop` is the working branch (`e29a4d5`), `main` is **owner-only** (Claude never commits, pushes or merges it). Django 5.2 + DRF; `apps/{core,providers,mappings,locations,availability}`; `integrations/{base,lomprayah}`; 162 tests + ruff green.
- **API v1** (docs in repo `docs/api.md`, ADR 0002): `GET /api/v1/providers/{slug}/stations/` and `/availability/`, per-caller hashed API keys, error envelope, stations cache (fresh 1 h, stale 24 h), availability cache 45 s (10 s when UNKNOWN), 20 live provider calls/min cap. Lomprayah capabilities are seeded UNVERIFIED + disabled, so endpoints return 403 until the owner enables them.
- **Live test passed** (real Lomprayah, 2 calls, no 429): 39 stations; Bangkok to Koh Tao and Chumphon to Koh Nangyuan returned departures with seats; cache repeat call 0.017 s.
- **Per-customer IDs (ADR 0003, 2026-11-03):** each customer (ApiClient) owns its IDs; mappings, the API (caller sees only its own `central_id`) and the staff mapping page `/admin/stations/<provider>/<client_id>/` are scoped to it. Picker list comes from `ApiClient.stations_url` (https, public IPs only; SmartEnPlus: its public `/api/v1/stations/`). CSV import for customers without an endpoint = slice 2, not built.
- **Local dev:** `make run` (migrate + server on :8001), `make dev-key` (writes `DEV_API_KEY` to git-ignored `.env`), `make lomprayah-on|off`, dev console at `http://localhost:8001/dev/` (SmartEnPlus BE on :8000) (DEBUG only, prefilled key, auto-loads stations). No superuser needed except for Django Admin.
- **Not verified:** Redis never run, Docker image not built, Lomprayah has not confirmed `availableAllotment` meaning or allowed automated access, real rate limit unknown (20/min and 60/min are guesses).
- **Next:** JSON 404 handler for unknown URLs, sort departures by time, draft Lomprayah partner-API request, SPC (blocked on docs and credentials).

**Lomprayah (2026-11-03):** only 3 unofficial website endpoints known (source-station, destination-station, quota). Reverse-documented in repo `docs/providers/lomprayah-api-reference.md` (tags observed/inferred/unknown). Owner: **Lomprayah provides seat availability only** — booking UNSUPPORTED, so no booking machinery for Lomprayah; Phase 4 booking = SPC only. `availableAllotment` >0 AVAILABLE, 0 UNAVAILABLE; 429/timeout/missing items = UNKNOWN. Rate limit hit (429 after ~20 calls at 0.4s). Timetable sample matched API times; overnight timetable uses arrival date, API `travelDate` = departure date. Open: permission for automated access, official partner API.

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
