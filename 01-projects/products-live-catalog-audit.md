# Products Live-Catalog Gap Audit

## Summary
Systematic audit of SmartEnPlus live catalog (https://www.smartenplus.co.th) to identify coverage gaps across **5 product types** — transportation (Join / Private / Charter) + Experiences + Activities. Generates BD-ready questions (via `grill` skill) for staff to source operators and close gaps.

## Context
Started 2026-06-28. User goal = grow catalog by closing undersupplied locations/routes/activities. Data folder at `/Users/charuwatnaranong/Desktop/SmartEnPlus/business-development/products-live-catalog/`. Distilled knowledge in vault `03-knowledge/`.

## Coverage scope

| Lens | BE filter | Surfacing |
|---|---|---|
| Join | `contract_type=JOIN` ∩ transport cats | Shared scheduled |
| Private | `contract_type=PRIVATE` ∩ transport cats | Private vehicle |
| Charter | `contract_type=CHARTER` ∩ transport cats | Hourly charter |
| Experiences | `service_category=MULTI_DAY_TOUR` | Multi-day packages |
| Activities | `service_category ∈ {DAY_TOUR, SPA_WELLNESS, EVENT_TICKET, ATTRACTION_TICKET, FOOD_DINING, ACCOMMODATION}` | Single-day + services |

Geographic = Thailand + cross-border (Laos, Cambodia, Myanmar, Malaysia).

## Three-layer gap matrix

| Layer | Source | Tells us |
|---|---|---|
| Reference | [[thailand-location-coverage-framework]] | What *should* exist |
| Live | sitemap.xml + public APIs | What we *actually* sell |
| Admin | Prod read-only Django shell | What operators *have loaded* |

**Gap** = Reference − Live. **Sub-gap** = Admin − Live. See [[three-layer-gap-coverage-matrix]].

## Phases

### Phase 0 — Framework ✅ DONE 2026-06-28
- Data folder + 3 markdown files created at `business-development/products-live-catalog/`
- 4 vault atomic notes authored: [[live-catalog-discovery-protocol]], [[thailand-location-coverage-framework]], [[three-layer-gap-coverage-matrix]], [[operator-outreach-question-template]]
- index.md + log.md updated

### Phase 1 — First snapshot ⏳ AWAITING USER APPROVAL
- Polite scrape sitemap.xml + public APIs (1 req/sec, cached)
- Read-only Django shell queries on prod DB for ground truth
- First snapshot: `business-development/products-live-catalog/snapshots-2026-06-28.md`
- Populate `gap-inventory.md`

### Phase 2 — Grill batch
- Invoke `grill` skill per gap with [[operator-outreach-question-template]]
- Save to `grill-questions/{date}-{slug}.md`
- User forwards to BD staff

### Phase 3 — Wrap-up + iteration
- Update `master-state.md` Section 2 with BD action items
- Atomize (≤5): prioritize discovery protocol + template + reference framework
- Commit + push vault

### Phase 4 — Re-audit cadence
- Every 4–6 weeks or after major operator onboard
- Append-only history

## Decision
Framework first (no scraping), then polite scrape + Django shell admin queries. Data in `business-development/`, knowledge in vault. `grill` skill for BD-ready questions. Re-audit cadence every 4–6 weeks.

## Tradeoffs
- **Pro:** 5-lens tagging reveals partial coverage (has Join but lacks Charter = actionable BD signal).
- **Pro:** Sub-gap = different fix path (data/pipeline, not BD).
- **Con:** Reference set is curated, not exhaustive — false negatives possible.
- **Con:** Admin DB requires Django shell access — barrier for non-engineering BD.

## Related
- [[live-catalog-discovery-protocol]]
- [[thailand-location-coverage-framework]]
- [[three-layer-gap-coverage-matrix]]
- [[operator-outreach-question-template]]
- [[business-development-thailand-platform-analysis]]
- [[transportation-category-audit]]

## Critical files

### Data (`business-development/products-live-catalog/`)
- `README.md` — project charter
- `methodology.md` — discovery protocol working copy
- `gap-inventory.md` — open gaps table
- `raw/` — API response dumps
- `grill-questions/{date}-{slug}.md` — BD-ready questions
- `resolved/{slug}-resolved-{date}.md` — closed gaps

### Knowledge (vault `03-knowledge/`)
- `live-catalog-discovery-protocol.md`
- `thailand-location-coverage-framework.md`
- `three-layer-gap-coverage-matrix.md`
- `operator-outreach-question-template.md`

### Read-only
- `/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-backend/operators/models.py` (Contract.service_category + contract_type)
- `/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-backend/products/models.py` (Route/Station)