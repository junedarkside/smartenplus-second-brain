# PDF Parsing Pipeline Pattern — NotebookLM → Django → Draft

## Summary

Admin-facing pipeline for parsing non-standard operator PDFs (Thai/English) into contract update proposals. Human-in-the-loop: NotebookLM extracts, Django validates and stages, admin confirms before any live data changes.

## Context

Operators submit PDF price tables to update existing contracts. PDFs are non-standard (Thai/English mix, no machine-parseable format). Regex/heuristics fail on Thai. Direct LLM API call from Django is overkill for current volume.

## Architecture

```
Admin pastes NotebookLM output (table → JSON)
  ↓
POST /admin-dashboard-operators/import-draft/bulk/
  {operator_slug, text}
  ↓
Django: fetch all contracts for operator (context for matching)
  → call GLM/MiniMax API (key in Django env, never browser)
  → extract N rows → match each to contract slug by route+type
  → validate delta (date format, enum, min≤max, dep < arr)
  → write ContractImportDraft per match
  ↓
Admin: match review table (confidence → pre-check ≥0.85)
  ↓
Admin: per-draft diff review (current | proposed | warning | ✓)
  → inline edit, place names via LocationSelector
  ↓
Confirm → PATCH contract + PATCH trip → draft deleted
Reject → draft deleted
```

## Key Invariants

- AI never writes directly to contract — staging draft only
- One active draft per contract — new run overwrites unconfirmed draft
- Delta only stored — review shows changed fields only
- Draft TTL: 7 days via Celery beat
- GLM/MiniMax API key in Django env only (`GLM_API_KEY` or `MINIMAX_API_KEY`)
- Auth: admin NextAuth session — no service token needed

## Decision: Why NotebookLM

| Option | Verdict | Reason |
|--------|---------|--------|
| Django + Claude API | Rejected | Overkill for current volume |
| Next.js API Route | Rejected | 10s serverless timeout |
| n8n workflow | Rejected | Async-only, admin needs sync response |
| Regex/heuristics | Rejected | Thai fails, non-standard PDFs |
| NotebookLM (human bridge) | **Chosen** | Free, Thai support, no infra, admin controls quality |

Future: volume grows → revisit Django + Claude Haiku `tool_use`.

## Backend Components Needed

| Component | What |
|-----------|------|
| `ContractImportDraft` | FK to contract, `proposed_contract_delta` JSONField, `proposed_trip_delta` JSONField, `validation_errors` JSONField, `match_confidence` float, `status` (pending/confirmed/rejected) |
| Bulk extract endpoint | `POST /admin-dashboard-operators/import-draft/bulk/` |
| Draft CRUD | GET (read), POST /confirm/, DELETE /reject/ per contract slug |
| Celery beat | Delete drafts older than 7 days |

## Rate Card Merge Strategy

Merge by `ratecard` enum key — untouched types survive. Never replace-all: operator PDF rarely lists all tiers.

```json
"rateCard": [
  { "ratecard": "ADULT", "selling_rate": 1200, "bar_rate": 1000 },
  { "ratecard": "CHILD", "selling_rate": 800,  "bar_rate": 700  }
]
```

Valid values: `JOIN` → ADULT/CHILD/INFANT. `PRIVATE`/`CHARTER` → VEHICLE only.

## Place/Station Name Resolution

Timeline places must reference existing `Place` DB IDs. NotebookLM extracts text names.

**Decision: manual admin selection.** Show extracted name as hint, admin picks from `LocationSelector` dropdown. Fuzzy match rejected — Thai name variants cause silent wrong-place-ID corruption.

## Open Questions (resolve before first commit)

1. GLM/MiniMax prompt — needs testing with real operator PDFs per `service_category`
2. Confidence threshold 0.85 — validate against real PDFs (too high = all manual, too low = wrong pre-accepted)
3. Trip delta field scope — `departure_time` + `arrival_time` confirmed; check if other trip fields appear in operator PDFs
4. `LocationSelector` reuse — single-mode, returns ID — verify reusable without changes

## Related

[[pdf-import-pre-validation-rules]] — 6 red flags + safeguards before first commit
[[pdf-contract-import-adversarial-review]] — adversarial critique, revised model schema, 3-screen UX
[[django-async-ai-call-pattern]] — async Celery pattern if migrating to hosted LLM
[[admin-dashboard-contracts]] — category registry, form flow, payload rules
[[celery-tasks]] — Celery beat TTL pattern
