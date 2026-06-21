# r1-archive — Archive Curation Findings

> Agent: `archive-curator` · Type: all types (archive-scoped) · Scope: `08-archive/`
> Part of [[vault-optimization-audit-2026-06-21/r3-leader-synthesis]]

## Summary
165 files / 19,916 lines. **Well-structured and healthy.** All audits complete. `.originals` retention justified. One optional catalog gap.

## Scope Covered
- 165 total (43 root + 65 `.originals` + 10 audit dirs + 47 subdir files)
- 65 `.original.md` backups in `.originals/` (hidden from Obsidian)
- 10 audit subdirs with multi-round structure

## .originals Retention Review — KEEP ALL
- 65 `.original.md` = pre-edit backups, audit trail (rule 88 "never delete — archive")
- Sampled value:
  - `payment-integration.original.md` → unique payment state decisions not in live
  - `trip-detail-deep-review-2026-05-20.original.md` → 4-agent adversarial history
  - `transportation-category-audit-2026-05-30.original.md` → code-only baseline vs later DB queries
- No prune candidates. `.originals/` leading-dot hides from Obsidian graph.

## Incomplete Audit Runs — NONE
All 10 subdirs have synthesis (`r3-leader-synthesis.md` or `round3-skeptic.md`):
- `website-audit-full-2026-06-06/` ✓, `rate-review-uxui-audit-2026-06-06/` ✓, `activities-pagination-ux-audit-2026-06-05/` ✓, `contract-ambiguity-audit/` ✓, `favorite-heart-analysis-2026-06-08/` ✓, all others ✓.

## Archive-vs-Live Duplication — 1 (acceptable)
- `08-archive/README.md` duplicates root `README.md` basename — **accept**: archive MOC vs vault root, different scope, no path collision.
- All others: no duplicate basenames; archive date-prefix + kebab prevents collision with live (no dates in live).

## Naming Inconsistencies — NONE
- Date format: consistent `YYYY-MM-DD` throughout
- Kebab-case: fully compliant
- `2026-06-07-content-questions-help-faqs.md` date prefix: **allowed** in archive (schema permits). Compliance, not violation.
- ⚠️ **CONFLICT** with structure-sheriff (flagged as violation). Per schema, dates allowed in `08-archive/`. See r3 — no action.

## Catalog Gap — OPTIONAL
- `08-archive/` has `README.md` MOC but no dedicated catalog
- Proposal (optional): add `08-archive/index.md` with `File | Date | Summary` table, auto-generated from README entries
- Alternative: rely on root `index.md` (user preference)
- Risk: **low**; current README MOC functional

## Coverage Notes
- Verified healthy: 33 files have "→ See [[...]]" supersedence markers; 131 have `## Related`; all 10 audit dirs follow r1-r2-r3/round pattern; 11 READMEs
- Archive hygiene: clean. Rule 88 followed.
