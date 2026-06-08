---
name: two-surface-parity-shared-module
description: When 2 UI surfaces need identical UX (grid, search, dialog, actions) over different data sources, extract a `shared/` module. Each surface becomes a thin wrapper. No duplicate code, no drift.
metadata:
  type: knowledge
---

# Two-surface parity via shared module

## Summary

When 2 UI surfaces need identical UX (image grid + search + metadata dialog + add/remove actions) but consume different data sources, extract a `shared/` module of reusable pieces. Each surface becomes thin wrapper. No duplicate code, no drift, no "which version is right" question.

## Context

admin-dashboard `components/Images/` had 2 surfaces:
- `OperatorImages.js` — master gallery, RTK Query `useGetOperatorAllImagesQuery`, read-only metadata dialog, add button (sends to selected set)
- `ProductImages.js` — per-contract selected set, Formik-bound `imageSelection`, editable metadata dialog, drag-reorder, delete

User asked: "ProductImages needs same metadata dialog + same search/filter as OperatorImages." Both have image grid. Both have click-to-open dialog. Both want search. The grid, dialog, and search logic were identical — only data source + editable-flag + action-button varied.

## Problem

Copy-paste two surfaces = 2 places to fix bugs + drift over time. OperatorImages dialog gains a new field, ProductImages dialog doesn't, behavior diverges. User reports: "editing metadata on selected images works, but the dialog on operator gallery doesn't have field X."

Extracting to one `OperatorImageDialog` shared by both = `OperatorImages` edits, `ProductImages` reuses. But search/filter logic also wanted parity. Each piece (dialog, search bar, hook, draggable card) extracted separately to `components/Images/shared/`, re-imported by both surfaces.

## Details

```
components/Images/
  shared/
    ImageMetadataDialog.js    # read-only + edit modes via isReadOnly prop
    ImageSearchBar.js         # debounced input
    useImageSearch.js         # filter + isFiltering state
    DraggableImageCard.js     # drag + caption bar + dialog trigger
    ImageCard.js              # non-draggable variant
    ImageGrid.js              # empty/loading/skeleton state
    index.js                  # barrel re-export
  OperatorImages.js           # 145 lines — uses shared pieces, RTK Query
  ProductImages.js            # 170 lines — uses shared pieces, Formik
  ImageSelection.js           # container, owns data flow
```

Each surface file = composition + surface-specific wiring (data source, action button, edit vs read-only). No duplication of grid, dialog, search.

Key contract decisions:
- `ImageMetadataDialog` accepts `isReadOnly` prop. Both modes share same field rendering, validation, layout.
- `useImageSearch` returns `{ searchQuery, setSearchQuery, debouncedQuery, filteredItems, isFiltering }`. Both surfaces call identically.
- `DraggableImageCard` vs `ImageCard` — separate components, same prop shape. OperatorImages uses static `ImageCard` (no reorder), ProductImages uses `DraggableImageCard`. No "isDraggable" boolean on one component = cleaner.
- `ImageGrid` owns empty/loading state. Surfaces pass `isEmpty`, `isLoading`, `emptyTitle`, `emptyIcon`. No per-surface skeleton duplication.

## Decision

**Extract per-concern shared modules, not per-screen shared components.** When 2 surfaces need the SAME interaction, the shared pieces are the sub-pieces (dialog, search, card), not a full "ImageManager" wrapper. Each surface still owns its own composition.

**Multiple variants stay separate components, not boolean props.** `ImageCard` + `DraggableImageCard` not `ImageCard isDraggable={true}`. Boolean prop = hidden complexity, separate component = visible choice. Mirror the codebase's existing pattern.

**Surfaces stay thin.** If a surface file exceeds ~200 lines, that's a signal that shared extraction is incomplete. Both ended at 145/170 lines.

## Tradeoffs

- More files in `shared/` (7 here). New contributors must learn the module boundary. Worth it: 2 surfaces × N files = 2N vs N+M (M = shared count).
- If 3rd surface appears, must decide: does it reuse existing shared pieces or need new ones? Answer is usually "reuse" — 3rd surface forces shared module to become real abstraction, not 2-surface special case.
- Surface-specific behavior (Formik wiring in ProductImages, RTK Query in OperatorImages) stays in surface file. Don't try to abstract that — different state libraries = different wiring patterns.

## Consequences

- Bug fix in dialog logic = 1 file change, 2 surfaces benefit.
- Adding a 3rd image surface (e.g. preview modal) = compose from existing shared pieces + thin wrapper. ~80% reuse.
- When shared module grows past ~10 files, consider whether it should be promoted to `components/[domain]/` (e.g. `components/images/`) for naming clarity.
- Test parity: when shipping a feature on one surface, verify other surface still works. Shared module is a contract between surfaces.

## Related

- [[image-metadata-formik-state-only-save]] — Formik wiring pattern (one of the surfaces)
- [[admin-dashboard-image-pipeline]] — pipeline context
- [[nextjs-hmr-cross-module-callback-staleness]] — gotcha when parent/child both import shared dialog
- Source: `admin-dashboard/components/Images/shared/` (7 files), `OperatorImages.js`, `ProductImages.js`
