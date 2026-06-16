# ADR: Contract Soft-Delete via Separate `is_deleted` Flag

## Status
proposed — design approved 2026-06-16, not yet built.

## Context

Admin contracts list (`/routemanagement/contracts`) today supports only **activate/deactivate** (`is_actived` flag) and **hard-delete** (default DRF `destroy`). Two problems:

1. **Hard-delete crashes on real data.** `BookingItem.contract` and `CartItem.contract` are `on_delete=PROTECT` (`bookings/models.py:42`, `carts/models.py`). Any contract that has ever been booked → `IntegrityError` on delete. Hard-delete is effectively unusable for live contracts.
2. **No recoverable "deleted" state.** `is_actived=False` means *paused* (intentionally hidden, will return). There is no way to express *removed but recoverable* distinct from paused.

Need: a real soft-delete that keeps the row (audit + recoverability), shows in admin with a Deleted state, and makes the contract vanish from smartenplus-frontend (not listed, detail 404, not bookable).

## Decision

Add **separate** soft-delete fields to `Contract`, mirroring the proven `ImageGallery` pattern already in the backend:

- Fields on `operators/models.py` Contract: `is_deleted` (BooleanField, db_index=True, default=False), `deleted_at` (DateTimeField null/blank), `deleted_by` (FK `accounts.Account`, SET_NULL, `related_name='deleted_contracts'`). Copy from ImageGallery `operators/models.py:526-535`.
- `ContractViewSet.destroy()` override soft-deletes instead of hard-deleting — copy the working override already in the same file at `operators/views.py:1954-1977`. Use `.save()` (not bulk `.update()`) so the `post_save` cache-invalidation signal (`operators/signals.py:17-37`) fires.
- New `restore` DRF action (mirror `update_activation` at `operators/views.py:330-348`).
- **Public queryset filters `is_deleted=False`** — the load-bearing change: list `products/views.py:430`, detail `ProductDetailViewSet.queryset :845` (deleted slug → existing 404 path `:894-895`).

`is_deleted` is the source of truth for "deleted". `is_actived` stays the source of truth for "paused".

## Alternatives Considered

1. **Reuse `is_actived` as delete** — rejected. Collapses paused-vs-removed into one flag; no recoverable distinction; admin can't show a true Deleted status separate from Inactive.
2. **Hard-delete (fix the FKs)** — rejected. PROTECT FKs exist on purpose (booking history must not vanish). Loosening them to CASCADE/SET_NULL would destroy audit trail.
3. **Separate `is_deleted` flag (chosen)** — sidesteps the PROTECT IntegrityError entirely (soft-delete is a `.save()`, not a `.delete()`), preserves audit, enables restore.

## Tradeoffs

**Core debate — does `is_deleted=True` also set `is_actived=False`? → YES (belt-and-suspenders).**

Every existing public/booking guard keys off `is_actived`: public list (`products/views.py:430`), availability (`:666`), frontend `useDayTripAvailability`, `DayTripBookingWidget` (`CONTRACT_INACTIVE`), checkout `Itineraries`/`EnhancedTripCard`. Forcing `is_actived=False` on delete means **every one of those guards catches a deleted contract even if a new `is_deleted=False` filter is missed somewhere** (recommendations, sitemap, future endpoints). Defense in depth.

**Restore does NOT auto-reactivate.** Restore clears `is_deleted/deleted_at/deleted_by` only, leaves `is_actived=False`. Admin explicitly re-activates via existing `update_activation` after review — prevents a restored contract going live/bookable before a human checks it. (Intentionally differs from ImageGallery `restore_selected`, which has no "active" concept.)

- **Gained:** defense-in-depth hiding, recoverability, audit preserved, **frontend ZERO code changes** (backend public-queryset filter alone hides deleted).
- **Lost:** `is_deleted` and `is_actived` no longer fully orthogonal (deleted implies inactive). Acceptable — the redundancy is the safety feature.
- **Risk:** ISR pre-rendered frontend detail pages stay live until revalidation. `post_save` busts the API cache, not Next's ISR cache. If instant hard-404 required, trigger on-demand revalidation.

Rule:
- Delete: `is_deleted=True, deleted_at=now, deleted_by=user, is_actived=False`
- Restore: `is_deleted=False, deleted_at=None, deleted_by=None` (leave `is_actived` as-is = False)

## Consequences

- **Admin dashboard** gains: Deleted chip (`StatusBadgeCell`), Deleted filter card (`ContractsSummaryStrip`, rides existing `?status=` rails), Delete + Restore actions (`ContractsActionBar`), `deleteContract`/`restoreContract` mutations (`store/api/contractsApi.js`). Backend admin summary adds `deleted_contracts` count + `status=deleted` filter; active/inactive counts gain `is_deleted=False` to avoid double-count.
- **`update_activation` must guard `is_deleted=False`** (`operators/views.py:339`) so a deleted contract can't be re-activated onto the public site via the bulk-activate path.
- **Frontend unchanged.** Verified: browse sends `status=active`, detail returns `notFound:true` on 404, booking guards catch via `is_actived`/`CONTRACT_INACTIVE`.
- **Slug stable** — `pre_save_slug_field` only runs when slug empty, so soft-delete keeps slug and `product_detail_v1_{slug}_*` cache key.

## Related
- [[django-soft-delete-s3-file-preserve]] — the ImageGallery soft-delete pattern this mirrors (file-bearing concern; contract is the non-file analog).
- [[activities-browse-filter-inactive-contracts]] — frontend `status=active` filter; complementary public-hiding mechanism that already keys off `is_actived`.
- [[admin-dashboard-contracts]] — contracts entity page.
