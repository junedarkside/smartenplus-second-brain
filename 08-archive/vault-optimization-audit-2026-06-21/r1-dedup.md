# r1-dedup — Dedup + Merge Findings

> Agent: `dedup-hunter` · Type: dedup+merge · Scope: whole vault (excl `.08-archive/.originals/`)
> Part of [[vault-optimization-audit-2026-06-21/r3-leader-synthesis]]

## Summary
8 clusters analyzed, **1 merge proposed**, 7 verified distinct. Vault health: 9/10. No critical duplication.

## Scope Covered
- `01-projects/` (71 files), `03-knowledge/` (235), `04-decisions/` (7), `08-archive/` (49 excl `.originals/`)
- Clusters: payment (37), design-system (15), contract/audit (40+), checkout (13), cs-centralization (3), experience (9)

## Merge Proposals

### Cluster: design-system
- Files: `03-knowledge/design-systems.md` (50 lines, 3 inbound), `03-knowledge/designSystem.md` (45 lines, 13 inbound), `03-knowledge/design-system-audit.md` (889 lines), `08-archive/design-system-audit-2026-05-31.md`
- Overlap: **90%** between `design-systems.md` and `designSystem.md` — both hubs pointing to `helpers/designSystem.js`, same token categories
- Proposal: merge `design-systems.md` → `designSystem.md`, archive the absorbed one
- Sections to consolidate: "Why Tokens", "Lessons", "MUI + Tailwind Coordination" from `design-systems.md` → append to `designSystem.md`
- Links to update: `index.md:419` entry (point to `designSystem.md` only); zero live inbound to `design-systems.md`
- Risk: **low**
- Reason: dual hubs confuse; rule 5 anti-duplication
- ⚠️ **INTERACTS WITH** structure-sheriff rename (`designSystem.md`→`design-system.md`) — see r3 reconciliation

## Distinct (no action — 7 clusters)
- **payment**: 85% overlap but archive status correct. `payment-integration.md` canonical (16 inbound vs 4 archived). Healthy archive-to-live.
- **contract-audit**: `03-knowledge/contract-model-ambiguity-audit.md` vs `08-archive/contract-ambiguity-audit/` (7 round files). Live = synthesized decision; archive = multi-round audit bundle. Intentional.
- **payment-architecture-audit**: 95% overlap but `08-archive/payment-checkout-architecture-audit-2026-05-17.md` superseded; live canonical. Correct.
- **cs-centralization**: 75% — ADR + review + UX design, distinct purposes. No merge.
- **checkout**: 60% — general rules vs state-persistence vs step-flow, atomic (<100 lines each). No merge.
- **trip-detail**: 40% — `trip-detail-page-review.md` vs `trip-detail-deep-review.md` = sequential audit trail (3-agent → 4-agent adversarial). Intentional.
- **audit-bundles**: 2026-06-XX bundles (r1/r2/r3 structure). Convention.
- **image**: <20% — 9 files, distinct (pipeline, header, OG, operator, webpack). No merge.

## Coverage Notes
- Archive-vs-live: all checked archives correctly superseded; zero cases where archive more current than live
- Atomization: current sizes appropriate (avg 62 lines, <200). No further atomization needed beyond 2026-06-13 pass
- Gaps: none
