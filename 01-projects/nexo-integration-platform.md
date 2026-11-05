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

**Mapping page (2026-11-04):** on `develop` `d435775` (169 tests), needs Coolify redeploy. Built: menu link (Admin > Mappings > "Map <provider> stations"), row anchor after save, "Find station" search box, clickable status counts (`?status=`), "ID not in list?" box open when the customer list fails to load. Checked in local Chrome (search, status filter, menu button). Owner set the SmartEnPlus Station list URL in prod. No station mapped yet in prod. UX ideas not built: next-pending review jump, CSV export, same-name flag in picker. Validation idea: 2-3 staff map 10 stations, measure wrong-ID rate.
**Lomprayah partner request:** draft (EN + TH, unsent) in repo `docs/providers/lomprayah-partner-request.md`. Owner to fill contact fields and send. Asks for written permission, partner API + sandbox, rate limit, `availableAllotment` meaning, timezone/currency, change contact, data sharing across customers. The 20/min cap quoted is our own guess.

## Contracts page for sign-off (built 2026-11-04, renamed from "Contract report" 2026-11-05)
- Page `/admin/stations/<slug>/<client_id>/contracts/` (old `/report/` URLs 302 to it; link on the mapping page): customer contracts, each station, mapped Lomprayah station, flags, digest, Print / Save as PDF. Checks stations only, not route, timetable or fare.
- Data: BE feed `GET /internal/nexo/operators/<id>/contracts/` (Bearer `NEXO_FEED_TOKEN`; empty = off). Nexo: `ApiClient.contracts_url`, env `CONTRACT_FEED_TOKENS` (JSON by customer name, never in the DB). Limit: one feed URL per customer.
- Prod facts (2026-11-04): Lomprayah operator id in SmartEnPlus = 29; feed URL `https://api.smartenplus.co.th/internal/nexo/operators/29/contracts/`; ApiClient name is lowercase `smartenplus` and the `CONTRACT_FEED_TOKENS` JSON key must match it exactly. 39 mappings already exist; Central IDs 141, 88, 83 each map to several Lomprayah stations (report flags them).
- Go-live steps and error meanings: master-state resume item 00. Repo doc: `docs/mapping-admin.md`.
- **Seat check per contract (merged `develop` `c697369` 2026-11-05, not deployed, feature off):** "Check seats" button per active contract opens a dialog with a date picker; Nexo asks Lomprayah for the mapped station pair via `apps/availability/services.get_availability` (capability gate, 45 s cache, 20 calls/min shared). Only when both stations are approved, else "Not checked". Lists all departures for the pair; the contract's own departure is now picked by time (see next bullets). Shares `apps/availability/payload.py` and `TravelDateSerializer` with the public API. Needs the `availability` capability enabled; Lomprayah access terms unconfirmed. SmartEnPlus has no allotment model (seat status only via an n8n webhook in `operators/views.py` `check_seat_availability`), so there is no comparison. Repo doc: `docs/mapping-admin.md` "Seat check per contract".
- **Map station + Change mapping on the page (merged `develop` `09fced8` 2026-11-05, 259 tests; redeploy of `nexo-api` needed for Change):** owner wanted station mapping settable per contract (SmartEnPlus checks Lomprayah allotment per contract). *Map station* (UNMAPPED/REJECTED/RETIRED stations) proposes a PENDING mapping; *Change mapping* (one live APPROVED/PENDING mapping) proposes the new provider station and retires (APPROVED) or rejects (PENDING) the old one in ONE transaction, reason required (5+ chars), audit rows cross-linked. Never approves: approval stays on the mapping page. Customer ID comes from the feed server-side, never the form. Race guard: page posts `mapping_id`; server locks the old row and refuses "Reload" unless it is the single live row. HTTP calls finish before the transaction. Retiring an APPROVED row makes every contract using that customer station PENDING and stops the API resolving it until the new one is approved. Rules in repo `docs/mapping-admin.md` ("Map station..." and "Change mapping..."). Reviewed by Opus rules agent + UX agent; Chrome-checked on a throwaway DB. Not checked: Safari, mobile, print. Same-person propose+approve still warn-only (owner never decided).
- **Searchable all-stations picker (merged `develop` `3331bc9` 2026-11-05):** the Map/Change dialog lists every Lomprayah station; already-mapped ones are greyed out with a text reason ("mapped to X (ID n)" or "pending for X"); search ignores case, accents, spacing, every typed word must match. Owner hit the empty picker live ("koh samui" found nothing). A greyed station can only be reused after its mapping is changed on the mapping page (many-to-one not built).
- **Seat check matches the contract's time (merged `develop` `eccb76e` 2026-11-05, 298 tests, no migration, not deployed):** the feed has no `departure_time`, so the time is read from the END of the contract name ("... pier 09.30", one clear time, else unknown) in `apps/locations/contract_time.py`; the departure with the same clock time shows first ("09:30 departure: 120 seats"), others collapsed. Time equality is a heuristic and the dialog says so. No match / two matches / no time in the name / provider UNKNOWN each get a message; never shown as zero seats; matched 0 reads "0 seats, sold out", missing seats "seats unknown". Nothing stored. Seat counts still need the `availability` capability enabled (off in prod; owner saw "Capability 'availability' is not enabled"). Evidence: Lomprayah quota items carry `boatLineStationId` (unique per departure, stability across dates/direction NOT verified), `departureTime`, `availableAllotment`, prices. Rejected for now: a stored per-contract DEPARTURE mapping (UX agent: only worth it if the ID is stable and sign-off must prove the time is real). Later: SmartEnPlus feed `departure_time` (separate branch in smartenplus-backend, dev team deploys; Nexo should read it first, not built).

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
