# r1-links — Link Integrity Findings

> Agent: `link-doctor` · Type: link integrity · Scope: whole vault
> Part of [[vault-optimization-audit-2026-06-21/r3-leader-synthesis]]

## Summary
- Broken wikilinks (real): **9** — script-fixable
- Stub links (write-later): 21 (low)
- Orphan pages: **1 true** (`prod-capacity-celery-audit`)
- index.md gaps: **58 unindexed** (6 high-value)
- Alias usage: 70 in index.md (intentional, not misuse)
- **Vault link health: GOOD**

## Scope Covered
524 total .md · 415 indexed · 466 unique wikilinks · 109 orphan candidates → 1 true orphan after filtering

## Tool Used
Read `scripts/vault-broken-links-repair.py` for repair rules, replicated detection with grep/find/bash (script mutates — detection only).

## Broken Wikilinks (real) — 9

**Cross-vault `../` refs** (4):
- `../activities-pagination-ux-audit-2026-06-05` → `activities-pagination-ux-audit-2026-06-05-audit`
- `../gyg-card-rate-analysis-2026-06-05` → `gyg-card-rate-analysis-2026-06-05-audit`
- `../gyg-page-analysis-2026-06-04-overview` → `gyg-page-analysis-2026-06-04-overview` (exists)
- `../rate-review-uxui-audit-2026-06-06-overview` → `rate-review-uxui-audit-2026-06-06-overview` (exists)

**Legacy `docs/` paths** (4):
- `docs/features/payment/PAYMENT_CHECKOUT_ARCHITECTURE_REVIEW.md` → `payment-checkout-architecture-audit`
- `docs/testing/PAYMENT_CANCEL_FLOW_TESTS.md` → `payment-cancel-state-prevmethod-guard`
- `docs/testing/PAYMENT_CHECKOUT_AUDIT.md` → `payment-checkout-architecture-audit`
- `docs/testing/PAYMENT_CHECKOUT_MANUAL_TEST_GUIDE.md` → `payment-checkout-e2e-testing`

**Subfolder README** (1):
- `01-projects/operators` → `01-projects/operators/README` or create `operators.md`

Proposal: run `scripts/vault-broken-links-repair.py` in write mode (idempotent, rules confirmed). Risk: **medium** (operators link may be stale).

## Stub Links (write-later) — 21
- Template placeholders (8) in `05-templates/r1-specialist.md` — expected, low
- Code symbols (2): `theme.js`, `designSystem.md` — anti-pattern examples, low
- Subfolder README refs (9): working-dir patterns, low
- Archive `.originals` refs (2): intentional, none

## Orphan Pages — 1 true
- `prod-capacity-celery-audit` — no inbound wikilink
  - Risk: **medium** — completed audit not integrated
  - Proposal: link from `01-projects/README` or a Celery parent, or move to `08-archive/` if superseded
- Filtered (expected): 46 `.original`, 16 `r1-r5`/`round1-3` team outputs, 5 `cs-*`, core files, session files

## index.md Gaps — 58 unindexed

**High-value (should index)** — 6:
- `finding-submit-review-auth-2026-06-07` — security finding
- `migration-0026-runbook` — operational runbook
- `serializer-field-omission-starves-ui` — bug pattern
- `dangling-export-import-bug-pattern` — bug pattern
- `filter-functionality-audit` — audit
- `prod-capacity-celery-audit` — audit

**Working files (expected, not critical)**: 31 `r1-r5` outputs, 7 `round1-3` outputs, `session-52-handoff`, `session-history`, `vault-guardrails`, `vault-protocol`, `2026-06-07-content-questions-help-faqs`.

Invalid index entries: 2 (both resolve via Obsidian folder search — none).

## Alias Misuse — none
70 `[[name|alias]]` in index.md are intentional display names (`[[master-state|Master State]]`). Pattern is display-only in index.md, not content-note aliases. Schema clarification recommended.

## Coverage Notes
- 365 unique wikilinks vs 415 index entries (aliases)
- Most "gaps" = working files intentionally excluded
- All 9 broken links have script rules; idempotent write safe
