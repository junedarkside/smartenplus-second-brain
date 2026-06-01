---
name: pdf-contract-import-research
description: Research + architecture for parsing non-standard operator PDFs via local AI agent + NotebookLM → ContractImportDraft (DB) → admin review → PATCH
metadata:
  type: project
---

# PDF Contract Import — Research & Architecture

## Status: PARKED — Architecture agreed, not yet scheduled for implementation

Grill session completed 2026-06-01. All major decisions locked. Parked for future consideration. Resume from "Still Open" section when ready to build.

---

## Summary

Operators submit non-standard PDFs (Thai/English) to update existing contracts. **Agreed flow: NotebookLM → Local AI Agent → `ContractImportDraft` DB staging → Admin Dashboard review/edit → PATCH.**

Two separate systems: (1) local AI agent on admin's machine, (2) existing admin dashboard with new draft review UI.

---

## Agreed Architecture

### Entry Point
Admin selects **operator** → dashboard fetches all contracts for that operator → admin pastes PDF text (table format) → clicks "Extract & Propose".

PDF is a **table** — one row per contract/route. AI splits rows reliably.

### Full Flow

```
Admin (contract list page, filtered by operator)
  │
  │  1. selects operator
  │  2. pastes NotebookLM output (table from PDF)
  │  3. clicks "Extract & Propose"
  ▼
Django Backend
  │
  │  POST /admin-dashboard-operators/import-draft/bulk/
  │  body: { operator_slug, text }
  │
  ├─ fetches all contracts + linked trips for operator
  │    (provides as context to AI for matching)
  │
  ├─ calls GLM/MiniMax API (key in Django env)
  │    → extracts N rows from table
  │    → matches each row to contract slug by route name + type
  │    → returns { rows: [{ contract_slug, confidence, contract_delta, trip_delta }] }
  │
  ├─ validates each delta
  │    → date format, enum membership, min≤max, dep_time < arr_time
  │    → errors stored per row in validation_errors
  │
  ├─ writes one ContractImportDraft per matched contract
  │    → proposed_contract_delta: JSONField (changed contract fields only)
  │    → proposed_trip_delta: JSONField (dep_time, arr_time — transport only)
  │    → validation_errors: JSONField { field: reason }
  │    → match_confidence: float
  │    → status: "pending"
  │    → overwrites any existing unconfirmed draft for that contract
  │
  └─ returns match table to dashboard
  ▼
Admin (match review — fast step)
  │
  │  sees table:
  │  Route summary | Matched contract | Confidence | ✓ Accept
  │  high confidence (>0.85) → pre-checked
  │  low confidence → unchecked, admin must confirm
  │
  │  clicks "Create Drafts" for accepted matches
  ▼
Admin (draft review — per contract)
  │
  │  Field          | Current     | Proposed    | Warning | ✓
  │  departure_time | 08:00       | 09:00       |         | ✓
  │  arrival_time   | 12:00       | 13:00       |         | ✓
  │  Adult rate     | 1,200 THB   | 1,400 THB   |         | ✓
  │  Child rate     | 800 THB     | 900 THB     |         | ✓
  │  start_date     | 2026-01-01  | 2026-03-01  |         | ✓
  │  place names    | (text hint) | admin picks from LocationSelector
  │
  │  admin edits inline if needed
  │  clicks Confirm
  ▼
Django Backend
  ├─ PATCH /admin-dashboard-operators/contract-details/{slug}/  (contract delta)
  ├─ PATCH /admin-dashboard-operators/trips/{trip_id}/          (trip delta, if present)
  └─ draft deleted
```

**Key invariants:**
- AI never writes directly to contract or trip — only to draft staging
- Admin always confirms before any PATCH fires
- One active draft per contract — new run overwrites previous unconfirmed draft
- Rate card: merge by `ratecard` type key — untouched types survive
- Draft stores delta only — review shows changed fields only, no noise
- Draft auto-deletes after 7 days (Celery beat)
- GLM/MiniMax API key in Django env only — never exposed to browser/Vercel

---

## Why NotebookLM (not in-house LLM)

| Option | Verdict | Reason |
|--------|---------|--------|
| Django + Claude API | Rejected | Overkill for current volume. Infra cost. API key management. |
| Next.js API Route | Rejected | 10s serverless timeout. No existing pattern. |
| n8n workflow | Rejected | Async-only. Admin needs sync response in browser. |
| Regex/heuristics | Rejected | Non-standard PDFs = no parseable pattern. Thai fails. |
| NotebookLM (human bridge) | **Chosen** | Free. Thai support. No infra. Admin controls quality. |

**Future:** If volume grows → revisit Django + Claude Haiku `tool_use` (original plan preserved below for reference).

---

## Field Extraction Map

Fields NotebookLM extracts per `service_category`. Admin uses the matching prompt template.

### All Categories
| Field | JSON key | Type | Notes |
|-------|----------|------|-------|
| Contract name | `name` | string | |
| Start date | `startDate` | YYYY-MM-DD | |
| End date | `endDate` | YYYY-MM-DD | |
| Advance booking | `advanceHour`, `advanceMin` | int | Split from "X hrs Y min" |
| Duration | `durationHour`, `durationMin` | int | Split from "X hrs Y min" |

### Transport / Transfer
| Field | JSON key | Type | Notes |
|-------|----------|------|-------|
| Rate card | `rateCard` | array | See rate card section |
| Route info | `routeInfo` | HTML string | Rich text description |
| Timeline stops | `timelinePlaces` | array of names | ⚠️ See place resolution below |

### Day Tour / Experience / Accommodation etc.
| Field | JSON key | Type | Notes |
|-------|----------|------|-------|
| Rate card | `rateCard` | array | See rate card section |
| Tour highlights | `tourHighlights` | HTML string | |
| Inclusions | `inclusions` | HTML string | |
| Exclusions | `exclusions` | HTML string | |
| What to bring | `whatToBring` | HTML string | |
| Meeting point type | `meetingPointType` | enum | HOTEL_PICKUP / MEET_ON_LOCATION / SPECIFIC_POINT |
| Meeting point details | `meetingPointDetails` | string | |
| Min participants | `minParticipants` | int | |
| Max participants | `maxParticipants` | int | |
| Difficulty | `difficultyLevel` | enum | EASY / MODERATE / CHALLENGING |
| Duration days | `tourDurationDays` | int | Multi-day only |

---

## Rate Card Structure

`ratecard` is an enum string — not a foreign key. Safe for NotebookLM extraction.

```json
"rateCard": [
  { "ratecard": "ADULT", "selling_rate": 1200, "bar_rate": 1000 },
  { "ratecard": "CHILD", "selling_rate": 800,  "bar_rate": 700  },
  { "ratecard": "VEHICLE", "selling_rate": 4500, "bar_rate": 4000 }
]
```

**Valid values by contract type:**
- `JOIN` → ADULT, CHILD, INFANT
- `PRIVATE` / `CHARTER` → VEHICLE only

Prompt template must include these enum values so NotebookLM uses correct keys.

---

## ⚠️ Unresolved: Place/Station Name Resolution

Timeline `dndCharacterData` places must reference existing `Place` records by DB ID. NotebookLM extracts text names ("Phuket Airport", "ท่าเรือ") — these don't auto-map to IDs.

**Options:**
1. **Manual admin selection** — show extracted name as hint, admin picks matching Place from existing `LocationSelector` dropdown. Safe, no false matches.
2. **Fuzzy name match** — query Places API, rank by string similarity, pre-select best match. Risky — Thai name variants + typos cause silent mismatches.

**Recommendation:** Option 1 (manual selection). Timeline place count is small (typically 2–5 stops). Fuzzy match saves ~30 seconds but risks wrong place IDs silently corrupting routes.

**Status: needs confirmation before implementation.**

---

## ⚠️ Open Research Questions (deep research needed)

1. **Prompt template design** — What exact prompt produces consistent JSON from NotebookLM across different operator PDF formats? Need to test with real operator PDFs. Needs a prompt per `service_category`.

2. **JSON paste field placement** — Where in the contract detail page UI does the paste input live? Inside the existing header toolbar (alongside Copy/Save)? Or a dedicated "Import" tab/section?

3. **Partial JSON handling** — NotebookLM may return only some fields (operator only updated prices, not dates). Dashboard must merge only present keys, skip nulls/missing. How does `formik.setValues` merge behave with partial objects?

4. **Rate card update vs replace** — Does pasting a new `rateCard` array REPLACE all existing rows, or MERGE by `ratecard` type? If operator adds a new vehicle class, should existing classes be preserved?

5. **Timeline place order** — PDF may list stops in order. Does extracted order map directly to `dndCharacterData` drag order? Or does admin always reorder manually after import?

6. **Validation failures after apply** — What if extracted `minParticipants > maxParticipants` or `startDate > endDate`? Dashboard applies to Formik then Yup catches on Save. Is that enough, or show inline warnings in diff review?

7. **Audit trail** — Should the PATCH include metadata that this update came from a PDF import? Useful for debugging. Or is the existing `updated_at` timestamp sufficient?

---

## Prompt Template Skeleton (draft — needs testing)

Admin copies this into NotebookLM after uploading operator PDF:

```
Extract contract fields from this document as JSON.
Use null for any field not found.

For service category: {TRANSPORTATION | DAY_TOUR | etc.}

Return exactly this JSON structure:
{
  "name": null,
  "startDate": null,       // YYYY-MM-DD
  "endDate": null,         // YYYY-MM-DD
  "advanceHour": null,     // integer hours
  "advanceMin": null,      // integer 0-59
  "durationHour": null,
  "durationMin": null,
  "rateCard": [],          // [{ "ratecard": "ADULT|CHILD|INFANT|VEHICLE", "selling_rate": 0, "bar_rate": 0 }]
  "routeInfo": null,       // HTML string (transport only)
  "tourHighlights": null,  // HTML string
  "inclusions": null,      // HTML string
  "exclusions": null,      // HTML string
  "meetingPointType": null, // "HOTEL_PICKUP" | "MEET_ON_LOCATION" | "SPECIFIC_POINT"
  "meetingPointDetails": null,
  "minParticipants": null,
  "maxParticipants": null,
  "difficultyLevel": null, // "EASY" | "MODERATE" | "CHALLENGING"
  "timelinePlaces": []     // [{ "name": "stop name", "time": "HH:MM" }]
}
```

**Status: draft only — needs validation against real PDFs.**

---

## Dashboard Feature Scope (pending deep research)

### Minimum viable
- "Import from PDF" button in `ContractDetailHeader`
- Modal: paste JSON textarea → parse → diff table
- Diff table: field | current | extracted | checkbox
- Apply selected → `formik.setValues()` merge
- Place fields: show extracted name as hint, admin selects from dropdown

### Out of scope (Phase 2)
- Direct PDF upload to dashboard (keep NotebookLM as extraction layer)
- Bulk import across contracts
- Auto place-name fuzzy matching
- Audit trail metadata on PATCH

---

## Decision Log

| Decision | Chosen | Rejected | Reason |
|----------|--------|----------|--------|
| Extraction tool | NotebookLM | Claude API, local regex | Free, Thai support, no infra |
| AI agent runtime | Local (Hermes/Ollama on machine) | Hosted API | Privacy, no per-call cost |
| Agent → dashboard hand-off | `ContractImportDraft` DB model | Browser state (Option A) | Agent runs async/offline — no browser to write to |
| Draft cardinality | One active draft per contract | Queue of drafts | Prevents stale proposal backlog |
| Draft expiry | 7-day TTL via Celery beat | Never expire | Prevent accumulation |
| Draft discard | Explicit Reject + TTL | TTL only | Admin needs explicit reject action |
| Agent auth to backend | NextAuth session (admin login) | Service token | No local agent — Django handles AI call server-side |
| Agent write target | Draft only, never contract directly | Direct PATCH | Hallucinated fields must not corrupt live data |
| Rate card type | Enum string (ADULT/CHILD/VEHICLE) | FK lookup | Safe for NLM/agent extraction |
| Place/station resolution | Manual admin selection in review UI | Fuzzy name match | Thai name variants cause silent mismatches |
| Rate card merge strategy | Merge by `ratecard` type key | Replace all | Operator PDF rarely lists all tiers — replace silently deletes untouched types |

---

## ⚠️ Open Research Questions (deep research needed)

1. ~~**Local agent tooling**~~ — **RESOLVED: No local agent.** Django handles AI call server-side. Admin pastes NotebookLM output into dashboard. No local process needed.

2. ~~**NotebookLM → agent hand-off**~~ — **RESOLVED: Admin pastes NLM output into dashboard textarea.** Django bulk extract endpoint receives text + operator_slug.

3. **GLM/MiniMax model + prompt** — Which model + prompt produces reliable JSON extraction from Thai/English table PDFs. Must include: operator contract list as context, table parsing instructions, enum values, dep/arr time HH:MM format. Needs testing with real operator PDFs.

4. ~~**Rate card merge strategy**~~ — **RESOLVED: Merge by `ratecard` type key.** Untouched types survive.

5. **Place name resolution in review UI** — Reuse existing `LocationSelector` (single mode, returns `id`) or build new component? `LocationSelector` already handles Places API search — likely reusable.

6. ~~**Draft payload shape**~~ — **RESOLVED: Delta only.** `proposed_contract_delta` + `proposed_trip_delta` — changed fields only.

7. ~~**Service token**~~ — **RESOLVED: No service token.** Admin NextAuth session used. Django calls GLM/MiniMax server-side.

8. ~~**Validation before draft write**~~ — **RESOLVED.** Django validates before writing draft. Errors in `validation_errors` JSONField, shown per-field in review UI.

9. **Match confidence threshold** — 0.85 proposed for auto-check. Needs validation against real operator PDFs. Too high = admin manually accepts all. Too low = wrong matches pre-accepted.

10. **Trip delta field scope** — Confirmed: `departure_time`, `arrival_time`. Any other trip fields operator PDFs typically update? Check `TripDashBoardViewSet` update payload.

---

## Two-System Boundary

```
┌─────────────────────────────────┐    ┌──────────────────────────────────┐
│   LOCAL AI AGENT (your machine) │    │   ADMIN DASHBOARD (Next.js app)  │
│                                 │    │                                  │
│  - Reads NotebookLM output      │    │  - Shows pending draft badge     │
│  - Fetches contract via API     │    │  - Draft review page             │
│  - Produces proposed payload    │    │  - Inline edit before confirm    │
│  - Writes ContractImportDraft   │───▶│  - Confirm → PATCH contract      │
│                                 │    │  - Reject → delete draft         │
│  Auth: service token            │    │  - Auth: NextAuth (admin login)  │
└─────────────────────────────────┘    └──────────────────────────────────┘
                                                        │
                                                        ▼
                                         Django Backend (existing)
                                         ContractImportDraft model (new)
                                         Contract model (existing, patched)
```

---

## Backend Changes Needed (Django)

| Component | What |
|-----------|------|
| `ContractImportDraft` model | `contract` FK, `proposed_contract_delta` JSONField, `proposed_trip_delta` JSONField, `validation_errors` JSONField, `match_confidence` float, `status` (pending/confirmed/rejected), `created_at`, `updated_at` |
| Bulk extract endpoint | `POST /admin-dashboard-operators/import-draft/bulk/` — receives `{operator_slug, text}`, calls GLM/MiniMax, writes N drafts |
| Draft read endpoint | `GET /admin-dashboard-operators/contract-details/{slug}/import-draft/` — dashboard reads pending draft |
| Draft confirm endpoint | `POST /admin-dashboard-operators/contract-details/{slug}/import-draft/confirm/` — PATCH contract + PATCH trip + delete draft |
| Draft reject endpoint | `DELETE /admin-dashboard-operators/contract-details/{slug}/import-draft/` |
| GLM/MiniMax integration | Called from bulk endpoint — key in Django env (`GLM_API_KEY` or `MINIMAX_API_KEY`) |
| Celery beat task | Delete drafts older than 7 days |

**No service token needed** — admin calls bulk endpoint via existing NextAuth session. GLM/MiniMax is called server-side by Django, never by browser.

---

## Frontend Changes Needed (Admin Dashboard)

| Component | What |
|-----------|------|
| Import page | New page: operator selector + paste textarea + "Extract & Propose" button |
| Match review table | Route summary \| Matched contract \| Confidence \| Accept checkbox. "Create Drafts" button. |
| Contract list | "Pending import" badge on contracts with active draft |
| Contract detail header | "Review Import Draft" button when draft exists |
| Draft review component | Field diff table: field \| current \| proposed \| warning \| checkbox. Inline edit. Confirm + Reject. Place names via `LocationSelector`. |
| RTK Query endpoints | `bulkExtractDraft`, `getContractDraft`, `confirmContractDraft`, `rejectContractDraft` |

---

---

## 🔴 Adversarial Review — Critical Findings (2026-06-01)

Full critique by Product Designer + Operations Consultant + Django Architect. Optimize for operational efficiency and error prevention, not engineering elegance.

### Root Problem With Current Design

11 steps because it solves three problems as one pipeline: PDF extraction + AI matching + supervised update. This coupling is the root cause of most weaknesses. Clean design separates extraction → matching → confirmation as independent concerns.

---

### 🚨 Red Flags — Stop Before Development

**Red Flag 1: One draft per contract with hard delete**
Must reverse before any code is written. Silent data loss via TTL, audit impossible, race condition in concurrent use. Fix: append-with-batch-ID + soft-delete (status=expired, never DELETE).

**Red Flag 2: Synchronous AI call in Django request**
WSGI worker blocked 5-20 seconds per import. 5 concurrent admins = 5 blocked workers = entire dashboard degrades. Fix: return `task_id` immediately, Celery handles AI call, frontend polls status.

**Red Flag 3: LLM doing contract matching**
Passing all operator contracts to LLM = expensive, slow, non-deterministic. Fix: LLM does extraction only. Python fuzzy matching handles contract matching against pre-fetched queryset.

**Red Flag 4: No pre-validation before draft creation**
Rate type mismatch (JOIN contract with VEHICLE rate) returns 400 at confirmation time — after admin reviewed and approved. Trust destroyed. Fix: all validation runs at draft creation, not confirmation.

**Red Flag 5: Confidence score as auto-accept gate**
0.85 threshold that auto-checks a row is a live-pricing risk. One high-confidence wrong-direction match (southbound vs northbound, same route, score >0.85) propagates to production. Fix: confidence = display emphasis only. All rows require human checkbox.

**Red Flag 6: No large-delta warning**
LLM decimal parsing errors (13500 vs 1350) are real and common. Must flag rate change >30% as hard warning regardless of confidence. Two lines of Python. Non-negotiable in MVP.

---

### Draft Model — Required Changes Before First Commit

Current design is unsafe. Required fields to add:

```
batch_id          UUID, indexed — one per import session
created_by        FK to Account
source_text_hash  SHA-256 of pasted input (dedup detection)
confirmed_at      timestamp
confirmed_by      FK to Account
superseded_by     FK self-referential, nullable
match_candidates  JSON — top 3 matches per row, not just best
status            pending / confirmed / rejected / expired (never DELETE)
```

**TTL Celery task must set status=expired, not DELETE rows.** Confirmed drafts retained forever for audit.

---

### AI Matching — Core Risk

Route names in PDFs ≠ route names in DB. "Hua Hin - Bangkok (VIP)" ≠ "Bangkok–Hua Hin VIP Coach". One route can have multiple contracts (same route, different trip departure times) — AI matching on route name + type alone cannot disambiguate.

**Fix: two-stage matching**
1. Match Route by name similarity (Python fuzzy, not LLM)
2. Match Contract within route by type + trip departure time
Show top 2-3 candidates per row — admin selects. Never auto-select a single match.

---

### UX — Reduce to 3 Screens (from 5)

**Screen 1: Import Setup**
Operator (pre-populated from context if possible) + paste area + Submit → returns task_id immediately.

**Screen 2: Unified Review Table (replaces Match Review + Draft Review per contract)**
One row per extracted update. Columns: route from PDF (raw) | matched contract + slug | confidence color band | field deltas inline ("ADULT: 1200→1350") | warnings | accept checkbox.
Expandable row = field-level sub-table. Bulk accept/reject by threshold. Keyboard navigation (Tab/Space/Enter).

**Screen 3: Confirmation Summary**
"X contracts updated. Y have active bookings. Confirm?" One click.

---

### Missing Safeguards

| Missing | Risk | Fix |
|---------|------|-----|
| Re-import guard | Second import silently overwrites first | Warn if `source_text_hash` match exists within TTL |
| Active booking warning | Rate change on contract with future bookings | Query orders, surface count as hard warning |
| Concurrent draft race condition | Two admins same contract = last write wins | `select_for_update()` on draft record |
| `transaction.atomic()` on confirm | Contract PATCH succeeds, Trip PATCH fails = partial state | Wrap both PATCHes in single atomic block |
| Rollback UI | No recovery after bad import | Phase 2: "Undo last import" via `django-simple-history` |
| Audit log of import session | No record of who/what/when imported | Store import session (text, AI response, batch_id, user) |
| Delta vs current-at-confirmation | Base state changes between draft creation and confirm | Show delta vs live values at confirm time, not draft-creation time |

---

### Scalability Concerns

- **Async required from day 1.** Synchronous AI call blocks WSGI workers. Non-negotiable.
- **Index `ContractImportDraft` on** `(operator_id, status, created_at)` from first migration.
- **Cache extraction by `source_text_hash`.** Prevents duplicate LLM cost on re-import.
- **Rate card delta must contain only changed types.** Full rate table in delta creates unnecessary `django-simple-history` entries for unchanged values.

---

### Architecture Component Verdicts

| Component | Verdict |
|-----------|---------|
| NotebookLM extraction | **Simplify** — add structured prompt template to reduce output variance. Phase 2: direct PDF upload |
| Django AI call (sync) | **Redesign** — async Celery task, returns task_id immediately |
| LLM for matching | **Remove** — Python fuzzy matching only |
| `ContractImportDraft` model | **Redesign** — append+batch_id+soft-delete before first line of code |
| Match Review screen (separate) | **Remove** — merge into unified table |
| Draft Review per contract (separate page) | **Simplify** — expandable row detail, not separate page |
| Rate card delta merge | **Keep** — merge-by-type-key correct, tighten to changed types only |
| Celery TTL hard delete | **Redesign** — status=expired transition only |

---

### MVP Recommendation (revised)

**Scope:** Rate card updates only. No trip time updates. One async flow.

**Staff workflow: 4 actions**
1. Operator page → "Import from PDF"
2. Paste NotebookLM output → Submit → spinner/task polling
3. Unified review table → bulk accept high-confidence, handle low-confidence manually
4. Confirm → done

**New endpoints needed:**
- `POST /admin-dashboard-operators/contract-import/` → returns `task_id`
- `GET /admin-dashboard-operators/import-tasks/{task_id}/` → status + result
- `POST /admin-dashboard-operators/contract-import/{batch_id}/confirm/` → list of draft IDs, `transaction.atomic()`

**Not in MVP:** trip time updates, LocationSelector place resolution, rollback UI, direct PDF upload.

---

### Phase 2 Recommendation

- Trip time updates (`departure_time`, `arrival_time`) with Bangkok timezone conversion + duplicate-trip pre-validation
- Direct PDF upload replacing NotebookLM copy-paste
- LocationSelector for place name resolution
- Rollback UI via `django-simple-history`
- Re-import conflict detection via `source_text_hash`
- Import analytics: confidence distribution, rejection rate, override rate per operator

---

## Related

[[admin-dashboard-contracts]] — category registry, form flow, payload rules
[[admin-dashboard-component-patterns]] — RTK Query, Formik, MUI patterns
[[operators]] — Django Contract model, service_category enum, Place model
[[stations]] — Station, Location, Place models (place ID resolution)
[[celery-tasks]] — Celery beat pattern for TTL + async task patterns
