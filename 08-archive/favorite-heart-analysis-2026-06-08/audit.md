# FAV-1 Favorite Heart — Executive Summary

**Session #82 · 2026-06-08**

## TL;DR

Code is mostly shipped (BookmarkButton + DayTripCard wired, ADR Bugs 1/2 fixed, 0026 unique-together migration exists). Skeptic found **3 silent/destructive bugs** missed by Phase-2 synthesis: cross-CT data loss on blog path, LikeViewSet.delete 405, and a keyboard Enter/Space race on the card. ~3-4 hrs of focused work to ship safely.

## Verdict

**Fix-then-ship.**

## What's done

- **Frontend** (`smartenplus-frontend/`)
  - `components/blog/BookmarkButton.js:31-32, 105-129` — `icon` + `variant` props + overlay JSX
  - `components/activities/browse/DayTripCard.js:16, 20, 127-132` — wired with `dynamic({ssr:false})` + `contract` + `overlay`
- **Backend** (`smartenplus-backend/`)
  - `dialogue/views.py:830, 856` — two separate validate methods (`_validate_wordpress_params`, `_validate_contract_params`)
  - `dialogue/views.py:856` — `_validate_contract_params(self, object_id)` already drops unused `content_type` param (ADR scrutiny pre-applied)
  - `dialogue/views.py:910, 920` — contract path uses real `ContentType` (Bug 1 fix); blog path keeps sentinel
  - `dialogue/views.py:885, 950, 915` — contract path filters include `content_type` (Bug 2 fix); blog path intentionally omits per ADR
  - `dialogue/migrations/0026_alter_bookmark_unique_together.py:15-19` — `unique_together = ('content_type', 'object_id', 'user')`

## What's broken (BLOCKERs)

1. **Cross-CT data loss on blog path** — `dialogue/views.py:882, 903, 947`. A user with a contract bookmark at id=42 visiting a blog with `databaseId=42` sees the heart pre-filled; tapping "remove" silently DELETES the contract row. The new 0026 unique constraint does NOT prevent this (CT differs).
2. **`BookmarkViewSet.delete` + `LikeViewSet.delete` both return 405 in prod** — `dialogue/views.py:935` and `:470`. Both `def delete` methods override `ModelViewSet.destroy` (detail URL), but frontend (`BookmarkButton.js:86`, `LikeButton.js:56`) calls list URL with body. Un-favorite is broken for both since the override shipped. Stuck-filled hearts grow `dialogue_bookmark` and `dialogue_like` unbounded.
3. **DayTripCard keyboard Enter/Space race** — `DayTripCard.js:123-125` Box wrapper stops `onClick` but NOT `onKeyDown`. Tabbing to heart + pressing Enter toggles the heart AND navigates to the detail page (Card's onKeyDown at `:96-101` catches the bubbled key). Q2 IntersectionObserver hydration encourages keyboard nav of deferred cards → amplifies the bug.

## What's needed

14 tasks in priority order (full detail in [r3-leader-synthesis.md](./r3-leader-synthesis.md)). Top of the queue:

1. Cross-CT sentinel filter on blog path (`dialogue/views.py:882, 903, 947`)
2. `@action(detail=False, methods=['delete'], url_path='')` on `LikeViewSet.delete` (`dialogue/views.py:470`)
3. `onKeyDown` stopPropagation on DayTripCard Box (`DayTripCard.js:124`)
4. Same `@action` decorator on `BookmarkViewSet.delete` (`dialogue/views.py:935`)
5. Prod dup audit on RDS (gates migration; does NOT gate code merge)

Then: `useAuthAxios()` hook + Bookmark/Like refactor, 409 dedup, 44×44 + focus ring, IntersectionObserver hydration (rootMargin 200px), LRU-cache the contract CT lookup, optional scale-pulse animation, runbook for 0026/0027 cascade.

## Effort

- Code work: ~2.5 hrs (4 commits)
- Optional polish: +30 min
- External: Task 5 prod dup audit (15 min with RDS access)
- Manual smoke test: 30 min
- **Total: ~3-4 hrs**

## Branch

`260608-feat/fav-1-bookmark-extension` (from `develop` — NOT direct to develop).

## Risks

- **Migration 0026 cascade** — `0027_reviewimage.py:10` depends on `0026`. Bad 0026 abort blocks 0027 redeploy. Runbook in Task 6 documents the rollback chain (`migrate dialogue 0026` reverses 0027 first, then `migrate dialogue 0025`).
- **Two-tab race surfaces as 100ms heart flip-revert** — Task 8 catches `IntegrityError` server-side (returns clean 409) AND treats 409/404 as success-state client-side (no UI revert).
- **0026 may already be applied to prod** — file dated 2026-06-02, audit run 2026-06-08 (6 days). Verify with `python manage.py showmigrations dialogue` before migration steps.

## Out of scope (confirmed)

- Wishlist page (Q3 user decision — clean defer, no stub)
- Heart count display
- A/B test setup (Q4)
- Blog `content_type` data migration to real `blog_post` CT (ADR §Known Tech Debt — Task 1 sentinel-filter is the safe bridge)
- `BookmarkViewSet.lookup_field` composite key

## References

- ADR: [04-decisions/adr-activity-card-favorite-button.md](../../04-decisions/adr-activity-card-favorite-button.md)
- All 4 vault reports: [r1-backend.md](./r1-backend.md) · [r1-frontend.md](./r1-frontend.md) · [r1-ux.md](./r1-ux.md) · [r2-skeptic.md](./r2-skeptic.md)
- Full leader synthesis: [r3-leader-synthesis.md](./r3-leader-synthesis.md)
