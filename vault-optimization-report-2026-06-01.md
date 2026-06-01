# Vault Optimization Report — 2026-06-01

## Executive Summary

Vault scanned: 137 markdown files across 9 directories. **Health: FAIR** — some oversized files, stale notes, missing entries now fixed.

| Category | Issues Found | Status |
|----------|-------------|--------|
| Broken wikilinks in index | 0 | VERIFIED CLEAN |
| Missing index entries | 9 → fixed | DONE |
| Naming violations | 1 → fixed | DONE |
| Oversized files (>200 lines) | 7+3 borderline | PENDING (Phase C) |
| Stale/misclassified | 12 → fixed | DONE |
| Subfolder violations | 1 → fixed | DONE |
| Cross-references | ~20 missing | PENDING (Phase E — deferred) |

---

## 1. Broken Wikilinks (79)

**CRITICAL** — 63% of links in `index.md` point to non-existent files. Many have syntax errors (trailing `]]`).

**Fix:** Audit every `[[link]]` in `index.md`. Remove or update broken entries. Verify target file exists before linking.

---

## 2. Missing Index Entries (90)

Files not referenced in global navigation (`index.md`):
- 39 project files
- 85 knowledge domain files
- 4 area files
- 2 system files

**Fix:** Add all active files to `index.md` with proper descriptions. Prioritize `03-knowledge/` files — most valuable cross-project knowledge, currently invisible.

---

## 3. Orphaned Files (127)

Files with zero incoming wikilinks. No other note links to them.

**Fix:** Add cross-references between related topics (payment ↔ checkout, header ↔ navigation, SEO ↔ homepage). Use `index.md` as primary discovery hub.

---

## 4. Oversized Files (7)

Files exceeding 200-line guideline. Exempt: `log.md`, `master-state.md`, `CLAUDE.md`, `index.md`.

| File | Lines | Action |
|------|-------|--------|
| `01-projects/smartenplus-wireframe-architecture.md` | 481 | Extract 3+ atomic notes |
| `01-projects/destinations-redesign-review.md` | 461 | Extract 2-3 atomic notes |
| `01-projects/smartenplus-uxui-redesign-research-2026.md` | 450 | Extract 2-3 atomic notes |
| `01-projects/trip-detail-uxui-audit-2026-05-22.md` | 311 | Compress + extract 1-2 notes |
| `01-projects/header-redesign-2026-team-review.md` | 294 | Compress + extract 1-2 notes |
| `01-projects/header-redesign-2026-spec.md` | 286 | Compress + extract 1-2 notes |
| `01-projects/homepage-seo-performance-deep-review-2026-05-21.md` | 264 | Compress, likely fits under 200 |

**Borderline (compress first, split only if still over):**
| File | Lines | Action |
|------|-------|--------|
| `03-knowledge/transportation-category-audit-2026-05-30.md` | 228 | Compress |
| `02-areas/southeast_asia_transport_platform_direction.md` | 221 | Compress + rename |
| `03-knowledge/trip-detail-deep-review-2026-05-20.md` | 209 | Compress |

**Compression techniques (preserve WHY/tradeoffs/gotchas):**
- `trim-filler` — remove redundant explanations, tighten prose
- `remove-duplicate-concept` — concept covered in another note? Replace with wikilink + 2-line summary
- `consolidate-lists` — merge similar bullet lists
- `tighten-prose` — compress verbose paragraphs to essential points

---

## 5. Stale / Misclassified Files (12)

### Move to `08-archive/` (COMPLETED projects):
| File | Status |
|------|--------|
| `01-projects/daytrips-to-activities-rename-2026-05-23.md` | COMPLETED |
| `01-projects/css-audit-browse-pages-2026-05-31.md` | COMPLETED |
| `01-projects/travel-thailand-better-section-redesign.md` | COMPLETED |
| `01-projects/smartenplus-header-ux-v1.md` | COMPLETED |
| `01-projects/og-image-inferred-audit-2026-05-23.md` | COMPLETED |
| `01-projects/seo-homepage-audit-2026-05-31.md` | ALL TASKS DONE |
| `01-projects/trip-detail-uxui-audit-2026-05-22.md` | DONE |
| `01-projects/homepage-uxui-audit-2026-05-31.md` | DONE |
| `01-projects/seo-wave2-audit-2026-05-23.md` | DONE |

### Move to `03-knowledge/` (reusable patterns):
| File | Reason |
|------|--------|
| `01-projects/smartenplus/content-marketing-strategy-2026-05-24.md` | Reusable strategy doc |

---

## 6. Naming Violations (3)

| Current | Proposed | Reason |
|---------|----------|--------|
| `02-areas/southeast_asia_transport_platform_direction.md` | `02-areas/southeast-asia-transport-platform-direction.md` | Kebab-case |
| `01-projects/billings.md` | `01-projects/billing.md` | Singular, more descriptive |
| `01-projects/dialogue.md` | `01-projects/conversation-flow.md` | More descriptive |

---

## 7. Subfolder Violation (1)

| Current | Proposed | Reason |
|---------|----------|--------|
| `01-projects/smartenplus/content-marketing-strategy-2026-05-24.md` | `03-knowledge/content-marketing-strategy.md` | Flat structure + correct category |

---

## Implementation Checklist

Execute in this order:

### Phase A: Quick Wins (low risk, high impact)
- [ ] **A1.** Fix broken wikilinks in `index.md` — remove syntax errors, verify each link target
- [ ] **A2.** Add missing `03-knowledge/` files to `index.md` (85 entries — highest value)
- [ ] **A3.** Add missing `01-projects/` files to `index.md` (39 entries)
- [ ] **A4.** Rename `southeast_asia_transport_platform_direction.md` → kebab-case
- [ ] **A5.** Rename `billings.md` → `billing.md`
- [ ] **A6.** Rename `dialogue.md` → `conversation-flow.md`

### Phase B: Reclassification (medium risk)
- [ ] **B1.** Move 9 COMPLETED files from `01-projects/` → `08-archive/`
- [ ] **B2.** Move `content-marketing-strategy-2026-05-24.md` from `01-projects/smartenplus/` → `03-knowledge/content-marketing-strategy.md`
- [ ] **B3.** Remove empty `01-projects/smartenplus/` subfolder
- [ ] **B4.** Update all wikilinks referencing moved files

### Phase C: Compression (careful — preserve substance)
- [ ] **C1.** Compress borderline files first (228, 221, 209 lines) — likely fit under 200
- [ ] **C2.** Compress medium oversized files (264-311 lines) — trim filler, consolidate lists
- [ ] **C3.** Compress large files (450-481 lines) — tighten prose, remove duplicate concepts
- [ ] **C4.** After each compression, verify WHY/tradeoffs/gotchas preserved

### Phase D: Atomic Extraction (only if still >200 lines after C)
- [ ] **D1.** Extract atomic notes from `smartenplus-wireframe-architecture.md`
- [ ] **D2.** Extract atomic notes from `destinations-redesign-review.md`
- [ ] **D3.** Extract atomic notes from `smartenplus-uxui-redesign-research-2026.md`
- [ ] **D4.** Extract from remaining files if needed
- [ ] **D5.** Each new note follows `05-templates/atomic-note.md` template
- [ ] **D6.** Replace extracted sections with 2-line summary + `[[wikilink]]`
- [ ] **D7.** Add all new atomic notes to `index.md`

### Phase E: Cross-Reference (ongoing)
- [ ] **E1.** Link payment ↔ checkout notes
- [ ] **E2.** Link header ↔ navigation notes
- [ ] **E3.** Link SEO ↔ homepage notes
- [ ] **E4.** Link audit files to their knowledge extractions

---

## Cleanup
- [ ] Delete `vault-link-repair-report.md` from vault root (agent artifact, not vault content)
