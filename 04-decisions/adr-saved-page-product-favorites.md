# ADR: Saved Page + Product Favorites (Bookmark read-side)

## Status
accepted — **deployed to PRODUCTION 2026-07-29** (via develop; FE `b959f1ea`, BE `126f213`). Migration `0010_product_slug` auto-applied on deploy (`docker-compose-rds.yml:13` runs `manage.py migrate` at container start).

### Implementation deltas vs proposal
- **Trip cards favorite the Contract, not Product.** The FE has no genuine Product-based card surface — trip search results + detail page are Contract-based (`productSlug` = contract slug). Product content-type wiring + `Product.slug` migration still shipped (future-proofs a real Product surface) but the live path is `contentType="contract"`, same as day-tour. `_contract_summary` enriched (name, operator, route) for the Saved list.
- **List `list()` override** ships as a plain-dict `Response` (no `BookmarkListSerializer` class — YAGNI). Batched hydration verified at **2 queries** (rows + Product bulk; CT lookups lru_cached), better than the 3-query target. 8 tests pass.
- **Heart placement:** trip list = footer cluster in `TripItemLayoutV2` (not absolute overlay — text card, no image); trip detail = top bar beside Share in `TripDetailHero`.
- **Saved page blog rows** hydrate title/slug via a new FE `getPostsByDatabaseIds` WP GraphQL batch query (`blogApi`) — WP stays source of truth, one call, no Django→WP coupling.
- **NEW: guest fav auto-save** — guest tap stashes `{contentType,objectId}` in sessionStorage, `BookmarkButton` replays the save once on authenticated return (no re-click). One-shot, matched on contentType+objectId. Not in original proposal; added from user feedback.
- **Also shipped:** profile-menu "Saved" entry + SubMenuRow icon-alignment fix.
- **Deferred (not shipped):** save-confirmation snackbar; DS token cleanups (heart color #E11D48 vs #EF4444, Outlined-icon drift); blog-sentinel CT debt.

## Summary
Read-side companion to [[adr-activity-card-favorite-button]]. Add a "Saved" list page for logged-in users, extend the `Bookmark` write-path to `Product` (recurring trip service), and surface a `list` endpoint that embeds per-type object summaries so the page renders in one call. No new model. One additive migration (Product.slug).

## Context
Favorites currently WRITE only. Blog posts ([[adr-activity-card-favorite-button]]) and day-tour contracts persist a `Bookmark` row, but there is **no surface where a user sees their saved items** — the heart fills, then the item vanishes into the DB. `BookmarkViewSet` exposes `list`/`check`/`create`/`delete`, wiring only `blog_post` (sentinel CT — see [[sentinel-content-type-bookmark-blog]]) and `contract`. `list` returns raw `{content_type, object_id}` — unrenderable by the frontend. Admin dashboard has no favorites view (out of scope).

Decided via 4-agent review (django / nextjs / ux / design) on 2026-07-29. Plan: `~/.claude/plans/check-vault-and-faverit-twinkling-alpaca.md`.

## Decision
1. **Favorite target = `Product`**, not `Route` or dated `Trip`. FE `TripCardV2` already carries `productSlug`; Product preserves service-type granularity a Route would flatten. Trip rejected — a saved dated departure expires, leaving a stale list.
2. **`list` embeds per-type object summary.** Custom `list()` override with **batched hydration = 3 DB queries total** regardless of bookmark count (partition rows by content_type → one `Product.objects.filter(pk__in=ids)` per type → map back). Never traverse `content_object` per-row (GenericFK = N+1). `object` nullable when target deleted (orphan bookmark → `null`, not 500).
3. **Unified vertical list, no tabs.** One chronological `SavedItemRow` list branching on `content_type` (product row vs blog row). Resolves the ux(unified)-vs-design(tabbed) split: design's real objection was a card-GRID breaking on mixed shapes → answered by rows, not grid. Tabs deferred until volume justifies.
4. **Name = "Saved" everywhere.** Retire "wishlist"/"favorites" from user copy (aria-labels currently drift). Model stays `Bookmark` (impl detail).
5. **Heart lives in the card PARENT.** `TripCardV2` is a text-only flex sub-component — mounting an overlay inside breaks `flex-1`. Overlay goes in `TripItemLayoutV2` with `position:relative` + stopPropagation on click AND keydown (mirror `DayTripCard.js:112-117`).

### Locked API shape (both repos code to this)
```json
GET /dialogue/bookmarks/  →  [
  { "id", "content_type", "object_id", "created_at",
    "object": { "id","product_name","slug","route_from","route_to","service_type","image","from_price" } }   // product
  { "id", ..., "object": { "wordpress_post_id": <id> } }   // blog_post — FE fetches WP; no server-side WP call
]
```

## Alternatives Considered
1. **Bookmark `Route`** — has slug already, no migration. Rejected: loses service-type granularity (one Route serves many products); naming mismatch with FE `productSlug`.
2. **FE N follow-up fetches per bookmark** — rejected: browser-level N+1, kills perceived perf on a 50-item list.
3. **Tabbed Saved page** — rejected for launch: low early volume makes 2-3-item tabs feel sparse; unified list + type chip suffices.
4. **New `Favorite` model** — rejected: `Bookmark` generic FK already fits; new model = 4+ files + migration for zero gain (same reasoning as write-side ADR).
5. **Chosen: extend Bookmark to Product + hydrated list + unified rows** — one additive migration, mirrors existing contract branch, zero blast radius on blog/contract paths.

## Tradeoffs
- **Gained:** users see saved items; favorites extend to trip search cards; 1-call render (no N+1); reuse-heavy (Section, ProfileHeader, BookingEmptyState pattern, contract branch, DayTripCard overlay).
- **Lost:** `Product` needs a `slug` field it lacks today → 1 additive migration (+ connect existing pre_save slug signal). Without it, saved-card click has no URL.
- **Risk:** orphan bookmark (Product hard-deleted) → list must return `object:null` or 500s. `list` tag invalidation must be added or the Saved page goes stale after any toggle (all 4 agents flagged). Post-auth `callbackUrl` must return guest to the tour page or save-intent is lost (conversion risk).

## Consequences
- **BE:** `products/models.py` gains `slug` + migration; `dialogue/views.py` gains `_get_product_ct` (lru_cache), `_validate_product_params`, a `product` branch in check/create/delete (mirror contract), and a `list()` override; `dialogue/serializers.py` gains a `BookmarkListSerializer` + `Product` import. Blog + contract paths untouched.
- **FE:** `api-slice.js` gains `getUserBookmarks` + `{Bookmark,id:'LIST'}` on create/delete invalidation; new `pages/account/saved.js` + `components/account/SavedItemRow.js`; NAV_CARD in `dashboard.js` (`FavoriteBorderIcon`, `isFullWidth`); `productId` threaded `TripItem.js → TripItemLayoutV2`; aria-labels → "Save"/"Remove from saved".
- **Deferred debt (do NOT fix here):** blog sentinel CT ([[sentinel-content-type-bookmark-blog]]); heart-color drift `#E11D48` vs `text-red-500`; `Favorite*Outlined` vs non-Outlined icon drift. Add `COLORS.wishlist` token when next touched.
- **UX polish (recommended):** save-confirmation snackbar (overlay heart gives zero text feedback today); profile-menu "Saved" row; no global header icon at launch.

## Build cost note (AI implementation)
Every file+line is enumerated in the plan → implementers use direct Read/Grep/Edit, **no Explore** (≈739k tokens/call). Batch as 2 sessions (1 BE, 1 FE), sonnet tier — design is done, work is mechanical. BE list-shape ships+locks before FE builds against it (sequence gate = no rework).

## Related
- [[adr-activity-card-favorite-button]] — write-side (button + contract wiring). This ADR is the read-side companion.
- [[sentinel-content-type-bookmark-blog]] — blog CT sentinel; product path must not touch it.
- [[wishlist-per-card-state-not-page]] — superseded rationale (per-card state was pre-backend; now persisted + listed).
- [[migration-0026-runbook]] — prior Bookmark migration (unique_together).
- [[rtk-query-advanced-patterns]] — bookmark 409/404 suppression, invalidatesTags patterns.
