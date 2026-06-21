# r1-atoms — Lint + Atomize Findings

> Agent: `lint-atoms` · Type: lint+atomize · Scope: `01-projects/`, `03-knowledge/`, `04-decisions/`
> Part of [[vault-optimization-audit-2026-06-21/r3-leader-synthesis]]

## Summary
26 notes scanned over 150 lines, **7 splits proposed**.

## Scope Covered
- `01-projects/`: 19 notes over 150 lines (8 top files verified)
- `03-knowledge/`: 6 notes over 150 lines (5 verified)
- `04-decisions/`: 1 note over 150 lines (verified)
- Total scanned: 26 files

## Proposals

### `01-projects/experiences-2026-marketplace-redesign.md` (349 lines)
- Extractable atoms:
  - `marketplace-redesign-phase-1-spec.md` (~80) — Phase 1 deliverables, files modified, verification
  - `marketplace-redesign-phase-2-backend-filters.md` (~60) — Phase 2 FilterSet, duration_type mapping, slugs
  - `marketplace-redesign-phase-3-mobile.md` (~40) — Mobile bottom sheet, sticky bar
  - `marketplace-redesign-phase-4-ipad-polish.md` (~30) — iPad layout, empty states, dark mode
  - `marketplace-redesign-decisions-table.md` (~50) — 17 decision records
- Source after: keep as overview index
- Risk: **medium** — preserve crosslinks
- Reason: phase break explicit; decision table self-contained

### `01-projects/filter-functionality-audit.md` (326 lines)
- Extractable atoms:
  - `filter-checkbox-object-stringify-bug-fix.md` (~50) — BUG-001 root cause + fix
  - `filter-checkbox-onclick-vs-onchange-bug.md` (~40) — BUG-002
  - `filter-checkbox-ischecked-reference-bug.md` (~30) — BUG-003
  - `filter-dialog-gate-operator-list-bug.md` (~20) — ISSUE-002
  - `filter-backend-departure-station-guard-bug.md` (~25) — BACKEND-001
- Source after: keep summary table + verdict + recommendations
- Risk: **low** — bugs independent, code blocks isolated
- Reason: each bug atomic fixable unit

### `01-projects/payment-deep-review-test-cases.md` (324 lines)
- Extractable atoms:
  - `payment-test-cases-smoke-tests.md` (~80) — TC-S1..S8
  - `payment-test-cases-manual-qa.md` (~100) — TC-M1..M7
  - `payment-test-cases-e2e-specs.md` (~120) — TC-E1..E7
  - `payment-test-coverage-matrix.md` (~40) — finding→test mapping
- Risk: **low** — groups already sectioned
- Reason: smoke/manual/e2e distinct workflows

### `03-knowledge/design-system-audit.md` (312 lines)
- Extractable atoms:
  - `design-system-token-coverage-matrix.md` (~60)
  - `design-system-component-violation-report.md` (~50)
  - `design-system-debate-outcomes.md` (~70) — 5 debate positions
  - `design-system-migration-roadmap.md` (~80) — 5-phase plan
- Risk: **medium** — preserve crosslinks to codebase paths
- Reason: roadmap is long-lived ref separate from snapshot

### `01-projects/payment-deep-review.md` (303 lines)
- Extractable atoms:
  - `payment-h1-amount-validation-fix.md` (~40)
  - `payment-h2-legacy-webhook-410-fix.md` (~20)
  - `payment-h3-order-reuse-response-shape-fix.md` (~30)
  - `payment-h4-charge-id-orderdetails-fix.md` (~30)
  - `payment-h5-reconcile-gate-payment-pending.md` (~35)
- Risk: **high** — HIGH findings cross-ref'd from implement-plan, test-cases, verification
- Reason: each HIGH independent security/correctness fix

### `04-decisions/adr-activity-card-favorite-button.md` (300 lines)
- Extractable atoms:
  - `adr-favorite-button-backend-validation-split.md` (~70)
  - `adr-favorite-button-backend-orm-fixes.md` (~60)
  - `adr-favorite-button-frontend-overlay-variant.md` (~50)
  - `adr-favorite-button-daytripcard-wiring.md` (~30)
  - `adr-favorite-button-scrutiny-findings.md` (~70)
- Risk: **medium** — preserve decision context (tradeoffs)
- Reason: scrutiny findings are post-decision audit

### `01-projects/payment-implement-plan.md` (294 lines)
- Extractable atoms:
  - `payment-batch-1-h3-h4-fix.md` (~50)
  - `payment-batch-2-h2-m10-legacy-routes.md` (~40)
  - `payment-batch-3-h1-m8-security-pair.md` (~50)
  - `payment-code-reuse-contract.md` (~40)
- Risk: **high** — primary ref for payment-deep-review fixes
- Reason: each batch production-safe unit

### `01-projects/experience-detail-page-redesign.md` (287 lines)
- Extractable atoms:
  - `experience-detail-redesign-decisions-table.md` (~60) — 11 decisions
  - `experience-detail-redesign-layout-spec.md` (~80) — grid, breakpoints
  - `experience-detail-redesign-components.md` (~100) — AirbnbPhotoGrid etc.
  - `experience-detail-redesign-booking-panel-sticky-fix.md` (~30)
- Risk: **medium** — grid math must match sidebar atom
- Reason: decisions table reusable; components are impl units

## Skipped (keep as-is — 12 files)
- `03-knowledge/recommendation-engine-completion-roadmap.md` (269) — single coherent narrative
- `03-knowledge/README.md` (263) — MOC index, breaking links damages nav
- `01-projects/activities-day-tour-page-review.md` (245) — single audit story
- `01-projects/activities-location-search-bug.md` (240) — cohesive debug session
- `01-projects/trip-page-full-audit.md` (212) — IMPLEMENTED, historical
- `01-projects/cs-centralization-design-concept.md` (211) — unified spec, 3 surfaces share principles
- `03-knowledge/transportation-category-audit.md` (212) — single conceptual model
- `03-knowledge/design-system-audit-activity-detail.md` (202) — page-specific audit unit
- `03-knowledge/precompute-popular-contracts-fix-plan.md` (201) — single incident response
- `01-projects/checkout-uxui-audit.md` (198) — 3-agent audit group
- `01-projects/profile-dropdown-redesign.md` (197) — single decision narrative
- `03-knowledge/omise-api-reference.md` (196) — single API reference catalog

## Coverage Notes
- 26 files over 150 lines identified via `wc -l`
- Top 8 longest read/sampled to confirm structure
- 3 (`payment-deep-review`, `payment-implement-plan`, `experience-detail-page-redesign`) partially read; structure confirmed
- Remaining 18 (150-200 lines) assessed by filename + vault principles
