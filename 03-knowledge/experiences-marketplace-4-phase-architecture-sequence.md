---
name: experiences-marketplace-4-phase-architecture-sequence
description: Architecture sequence for /activities 2026 marketplace redesign — 4-phase rollout (frontend-only → backend filters → mobile → iPad polish). Frontend-endowed; no backend coupling.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: experiences-2026-marketplace-redesign
---

# Experiences Marketplace — 4-Phase Architecture Sequence

## Summary
Phased rollout strategy for `/activities` 2026 marketplace redesign: frontend-only → backend filters → mobile → iPad polish. Frontend-endowed; no backend coupling.

## Why It Matters
Prevents a blocked backend from stalling the entire redesign. Each phase independently ships; phases 2-4 gate on backend readiness.

## Detail
**Phase 1 (frontend-only):** Sidebar layout, 4-col grid, premium card, sort bar. Zero backend changes — filters use existing API params. Ships immediately.

**Phase 2 (backend filters):** Django adds new filter params (category×destination combos, price ranges, duration bands). Frontend consumes new params.

**Phase 3 (mobile):** Responsive refinements for phone viewports. Filter bar collapses to bottom sheet, grid drops to 2-col.

**Phase 4 (iPad):** Tablet polish. 3-col grid, touch-optimized spacing, landscape orientation fixes.

## Constraints / Gotchas
Phase 1 MUST NOT depend on Phase 2 filters. If backend delays, Phase 1 still shippable with current filter set.

## Related
- [[experiences-2026-marketplace-redesign]] — parent redesign spec (layout, components, token map)
