# Vault Optimization Snapshot — 2026-06-16

## Pre-state baseline (from `scripts/vault-stats.py`)

| Metric | Value |
|---|---|
| notes_total | 472 |
| unique_targets | 442 |
| broken_unique | 68 |
| orphans | 78 |
| date_prefix_files | 105 |

## Workstreams in this pass
1. Folder-level MOCs (additive)
2. Project subfolder READMEs (additive)
3. Orphan wiring via MOC injection (edit)
4. Broken wikilink repair (in-place edits)
5. Template placeholder masking (edit)
6. `.original.md` move to `.originals/` (move, 65 files)
7. `docs/testing/` deprecation stub (additive)

## Deferred
- 105 date-prefix filename renames (separate wave, breaks inbound wikilinks)

## Post-state targets
- orphans ≤ 25 (from 78)
- broken_unique ≤ 30 (all template-only)
- note count: 472 + ~16 new READMEs = ~488
