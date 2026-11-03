# Nexo — SmartEnPlus Integration Platform

## Summary
Standalone Django backend that integrates external transport operators (Lomprayah, SPC Thailand) with SmartEnPlus via one normalized API. Repo: `/Users/charuwatnaranong/Desktop/SmartEnPlus/Nexo` (no git yet).

## Status
Initialized 2026-11-03. Docs only (`CLAUDE.md`, `README.md`, `docs/`). No Django project, no code. Phase 1 not started.

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
Nothing about provider endpoints is verified. Missing: provider docs/credentials, how SmartEnPlus supplies Central IDs, SmartEnPlus-to-platform auth, repo/package name, Coolify target. Tracked in repo `docs/open-questions.md`.

## Related
- Repo ADR 0001: Central ID ownership + modular monolith (`docs/decisions/0001-...`)
- [[architecture]] — main SmartEnPlus architecture
- [[backend-architecture]] — SmartEnPlus Django backend (consumer of this API)
