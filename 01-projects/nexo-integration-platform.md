# Nexo — SmartEnPlus Integration Platform

## Summary
Standalone Django backend that integrates external transport operators (Lomprayah, SPC Thailand) with SmartEnPlus via one normalized API. Repo: `/Users/charuwatnaranong/Desktop/SmartEnPlus/Nexo`, GitHub `junedarkside/nexo` (private, branches `main` + `develop`).

## Status
Phase 1 foundation built 2026-11-03 (git `main`, 7 commits, 18 tests + ruff green, not pushed, no remote). Django 5.2 + DRF; `apps/{core,providers,mappings}`; `integrations/base` (adapter + registry by dotted path); `/api/v1/health/`; capability + mapping + append-only audit models; Docker files (compose only config-validated, image not built). No provider module yet; Phase 2 needs provider docs/credentials.

**Lomprayah (2026-11-03):** only 3 unofficial website endpoints known (source-station, destination-station, quota). Reverse-documented in repo `docs/providers/lomprayah-api-reference.md` (tags observed/inferred/unknown). Owner: **Lomprayah provides seat availability only** — booking UNSUPPORTED, so no booking machinery for Lomprayah; Phase 4 booking = SPC only. `availableAllotment` >0 AVAILABLE, 0 UNAVAILABLE; 429/timeout/missing items = UNKNOWN. Rate limit hit (429 after ~20 calls at 0.4s). Timetable sample matched API times; overnight timetable uses arrival date, API `travelDate` = departure date. Open: permission for automated access, official partner API.

## Why it exists
SmartEnPlus should not learn each provider's API format, auth, availability or booking payload. Provider logic isolated in one modular monolith so adding an operator = new module, not new infra.

## Non-negotiables (full rules in repo `CLAUDE.md`; engineering rules = section 17)
- **SmartEnPlus owns all Central IDs** (station, route). Platform only stores them as references in mapping records; never generates, edits, or retires them. Reports missing/invalid IDs back.
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
Nothing about provider endpoints is verified. Missing: SPC docs/credentials, how SmartEnPlus supplies Central IDs, SmartEnPlus-to-platform auth, Coolify target. Tracked in repo `docs/open-questions.md`.

## Related
- Repo ADR 0001: Central ID ownership + modular monolith (`docs/decisions/0001-...`)
- [[architecture]] — main SmartEnPlus architecture
- [[backend-architecture]] — SmartEnPlus Django backend (consumer of this API)
