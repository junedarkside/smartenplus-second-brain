# r1-health — Content Health + Staleness Findings

> Agent: `health-checker` · Type: structure+health (content) · Scope: `01-projects/`, `03-knowledge/`
> Part of [[vault-optimization-audit-2026-06-21/r3-leader-synthesis]]

## Summary
15 notes deep-read, 315 grep-scanned, **24 issues** across 5 categories. Zero AI filler.

## Scope Covered
Deep-read (15): payment-deep-review (303), payment-deep-review-test-cases (324), 01-projects/README (184), payment-audit-bugs (153), trip-detail-page-review (189), trip-detail-deep-review (160), design-system-audit (312), omise-api-reference (196), payment-pending-deadlock (153), trip-detail-server-side-seo-pattern (60).
Grep-scan: `stable_id`, `useTripSEO`, `api/users/{id}`, filler phrases, status contradictions, ISR patterns.

## Stale/Removed-Feature Refs

### STABLE_ID — 10 files (framed as open debt, but removed 2026-02-13)
- `payment-deep-review.md:5` — "M4 RETRACTED" + stable_id cleanup in carry-over
- `payment-audit-bugs.md:26-30` — stable_id as LOW tech debt with file lists
- Evidence: frontend CLAUDE.md "stable_id removed 2026-02-13"
- Proposal: update line 5; mark payment-audit-bugs stable_id section completed/archived with date
- Risk: **medium** — devs search for removed code
- Reason: framed as debt, should be "resolved"

### USETRIPSEO — 4 files ref deleted hook
- `trip-detail-page-review.md:14,98` ("useTripSEO hook", "~line 290")
- `trip-detail-deep-review.md:48,94` ("~line 418", "~line 321")
- Evidence: `trip-detail-server-side-seo-pattern.md:7` — hook replaced by `tripDetailSEOUtils.js`
- Proposal: update refs to cite new pattern file + correct lines, OR archive 2026-05-20 audit notes
- Risk: **medium** — line numbers mislead devs
- Reason: pre-refactor audit findings

### SELF-PROFILE API — correct, no issue
Both `accounts.md` + `api-endpoints.md` correctly document `/api/users/{id}/` admin-only since 2026-05-07, self-profile `/api/user/`.

## Contradictions

### Polling status vocabulary — `omise-api-reference.md:179`
- Claim: poll `successful || paid`
- vs `payment-deep-review.md:92`: useQRPolling.js:88-91 checks `paid` only
- Proposal: clarify both Omise (`successful`) + GatewayCharge (`paid`) domains; current impl checks `paid`
- Risk: **low** (doc inconsistency, not functional)

### ISR revalidation scope — `isr-revalidate-csr-vs-isr-field-matrix.md:11-12`
- Claim: field-level ISR ("rate: CSR overlay... ISR only after date pick")
- vs `trip-detail-server-side-seo-pattern.md:28`: revalidate:300 is page-level
- Proposal: clarify page-level ISR; CSR overlay covers rate volatility in-session
- Risk: **medium** — could drive wrong on-demand revalidation
- Reason: Next.js ISR is page-level, matrix oversimplifies

## Generic Filler — ZERO
No "This document/In this note/comprehensive overview" matches. Notes well-written.

## Missing WHY — 3 summary sections
- `design-system-audit.md:1-5` — WHAT not WHY adoption matters. Add 2-3 lines business impact.
- `omise-api-reference.md:1-4` — no purpose statement. Add "Reference for payment integration decisions..."
- `trip-detail-page-review.md:1-4` — no audit trigger. Add "Triggered by SEO decline + CLS reports..."
- Risk: **low** (informative, lacks strategic context)

## Broken Operational Claims — 3

### `trip-detail-deep-review.md:27`
- Claim: "ISR known build regression"
- Issue: no version specificity; may be resolved in Next 14.2.5
- Proposal: verify current; update "previously observed" or remove
- Risk: **low**

### `payment-audit-bugs.md:26-30`
- Claim: stable_id lines 317-357 dead code
- Issue: line numbers drift; per payment-deep-review:151 stable_id "comment-only in source + 2 test files"
- Proposal: remove precise lines; state "files reference stable_id in comments/tests"
- Risk: **medium** — wrong line numbers

### `design-system-audit.md:193-202`
- Claim: violation counts (pdfStyles.js: 33 hardcoded colors)
- Issue: time-sensitive snapshot; code changed since 2026-06-13
- Proposal: add timestamp caveat "As of 2026-06-13"
- Risk: **low**

## Coverage Notes
- Not scanned: 01-projects audit subfolders (time-boxed, inherent staleness), 03-knowledge <150 lines (low ROI), folders outside 01-projects+03-knowledge
- Method limitation: line numbers in audit notes are volatile → recommend function-name refs over line numbers vault-wide
