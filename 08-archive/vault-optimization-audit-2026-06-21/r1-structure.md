# r1-structure — Structure + Naming Findings

> Agent: `structure-sheriff` · Type: structure+health · Scope: whole vault
> Part of [[vault-optimization-audit-2026-06-21/r3-leader-synthesis]]

## Summary
Mostly compliant. **3 naming violations**, **1 premature subfolder**, **2 non-standard folders**, archive subfolder proliferation (acceptable). Special files healthy.

## Scope Covered
All 9 standard folders + root special files. (Counts: 01-projects/235, 03-knowledge/233, 08-archive/164 per agent — minor variance from other agents.)

## Naming Violations

### 1. `03-knowledge/designSystem.md` — PascalCase
- Proposal: rename → `design-system.md`
- Backlinks: 4 (`08-archive/rate-review-uxui-audit-2026-06-06/r1-visual.md`, `01-projects/cs-centralization-design-concept.md`, `03-knowledge/design-system-audit-activity-detail.md`, self)
- Risk: **low**
- ⚠️ Interacts with dedup-hunter merge — see r3

### 2. `03-knowledge/usedayTripFilters-hydration-spurious-push.md` — camelCase
- Proposal: rename → `use-day-trip-filters-hydration-spurious-push.md`
- Backlinks: 3 (`index.md`, `01-projects/architecture.md`, `03-knowledge/README.md`)
- Risk: **low**

### 3. `03-knowledge/mui-autocomplete-handlInputchange-parent-emit.md` — camelCase + typo
- Proposal: rename → `mui-autocomplete-handle-input-change-parent-emit.md` (fix `handlInputchange` typo)
- Backlinks: 5 (`index.md`, `03-knowledge/README.md`, `03-knowledge/usedayTripFilters-hydration-spurious-push.md`, `03-knowledge/mui-autocomplete-inputvalue-sync.md` ×2)
- Risk: **low**

## Misplaced Files

### `08-archive/2026-06-07-content-questions-help-faqs.md` — date in filename
- Proposal: rename → `content-questions-help-faqs.md`
- Backlinks: 4 (`07-logs/session-history.md`, `07-logs/log.md`, `08-archive/README.md`, `08-archive/help-faqs-landing-2026-06-07/README.md`)
- Risk: **medium**
- ⚠️ **CONFLICT** with archive-curator: archive schema permits dates in `08-archive/`. See r3 reconciliation — likely no action.

## Non-Standard Folders

### `docs/`
- Contents: `README.md` + empty `testing/`
- Proposal: merge `docs/README.md` into root `README.md` or `08-archive/README.md`; delete empty `testing/`
- Backlinks: none
- Risk: **low**

### `scripts/`
- Contents: `vault-stats.py`, `vault-broken-links-repair.py`
- Proposal: move → `06-systems/` (operational tooling)
- Backlinks: check `vault-wrapup.sh` workflows
- Risk: **low**

### `.obsidian/`
- App config, not content. Keep; ensure `.gitignore`.

## Nesting Issues

### `01-projects/customer-os-thesis-review/` — premature subfolder (7 files)
- Proposal: flatten with prefix: `customer-os-thesis-grill-audit.md`, `customer-os-thesis-r1-product.md`, `customer-os-thesis-r1-strategy.md`, `customer-os-thesis-r1-tech-feasibility.md`, `customer-os-thesis-r2-skeptic-review.md`, `customer-os-thesis-r3-leader-synthesis.md`, rename `README.md` → `customer-os-thesis-review.md`
- Backlinks: few, mostly from CS centralization docs
- Risk: **medium**
- Reason: vault forbids subfolders until scale demands; 7 files ≠ scale

### Archive subfolder proliferation (9 dirs in `08-archive/`)
- Proposal: **accept as exception** (audit bundles belong together). Optionally strip dates from folder names (`activities-pagination-ux-audit-2026-06-05` → `-bundle`).
- Risk: **low**

## Special File Health
- `master-state.md` (77 lines) — healthy, correct section order, trimmed (78% reduction)
- `index.md` (446 lines) — acceptable, one-line-per-page format intended
- `log.md` (724 lines) — healthy, reverse-chrono by design
- `vault-protocol.md` / `vault-guardrails.md` — not in CLAUDE.md Special Files table; add or clarify as optional supplements

## Coverage Notes
- `02-areas/`, `04-decisions/`, `05-templates/`, `06-systems/`, `07-logs/` — all compliant, flat
- `08-archive/.originals/` — acceptable (hidden, caveman:compress backups)

## Priority
1. High: rename 3 camelCase files
2. Medium: flatten `customer-os-thesis-review/`
3. Low: relocate `docs/`, move `scripts/`, strip archive folder dates
