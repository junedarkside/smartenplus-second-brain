# R2 Skeptic — FAV-1 Challenge

Session #82 · 2026-06-08 · Skeptic agent (challenger of synthesis)

## Methodology
7 lenses: race, security, integrity, performance, ux, migration, scope. Traced file:line through:
- `smartenplus-backend/dialogue/views.py:820-965` (BookmarkViewSet)
- `smartenplus-backend/dialogue/views.py:410-555` (LikeViewSet, comparison)
- `smartenplus-backend/dialogue/models.py:148-160` (Bookmark + unique_together)
- `smartenplus-backend/dialogue/migrations/0026_alter_bookmark_unique_together.py` (constraint migration)
- `smartenplus-backend/dialogue/migrations/0027_reviewimage.py` (downstream blocker)
- `smartenplus-backend/Smartenplus/settings.py:401-416` (auth + throttle classes)
- `smartenplus-frontend/components/blog/BookmarkButton.js` (DELETE call site, axios pattern)
- `smartenplus-frontend/components/UI/LikeButton.js` (sibling bug suspect)
- `smartenplus-frontend/components/activities/browse/DayTripCard.js:82-133` (event flow, keydown)
- `smartenplus-frontend/components/utils/useAuthRedirect.js:3-17` (hook pattern to mirror)

No rubber-stamp. Synthesis's G1 is real and confirmed; but I also found missed blockers and a critical cross-CT correctness bug. I cite each claim.

---

## Findings (ordered: blocker → major → nit)

### Finding 1 — LikeViewSet.delete has the SAME 405 bug as BookmarkViewSet.delete
- **Severity:** blocker
- **Lens:** integrity (data leak — silently broken un-favorite path)
- **Claim:** Synthesis §G1 says BookmarkViewSet's `def delete` is missing `@action(detail=False, ...)` and is bound to detail URL → 405 on list URL. Synthesis only flags + fixes the BookmarkViewSet. The like path is identical.
- **Evidence:**
  - `smartenplus-backend/dialogue/views.py:470` — `class LikeViewSet` `def delete(self, request, *args, **kwargs):` overrides `ModelViewSet.destroy` with no `@action` decorator. By the same DRF routing rule synthesis applied to bookmarks, this method is bound to detail URL `/dialogue/likes/{id}/`, NOT list URL `/dialogue/likes/`.
  - `smartenplus-frontend/components/UI/LikeButton.js:56` — `await axiosInstance.delete(likeUrl, { data: { content_type: ..., object_id: ... } });` where `likeUrl = \`${baseURL}/dialogue/likes/\`` (line 16). This is the LIST URL, not `/dialogue/likes/{id}/`. DRF returns **405 Method Not Allowed** because there is no list-level DELETE handler.
  - **The like has been broken in prod since the custom `delete` override was added.** Production users can like blog posts but cannot un-like them. `dialogue_like` table grows monotonically.
  - Notice in `r1-frontend.md §Tasks #1-2` the synthesis correctly identifies both `BookmarkButton.js:41-45,65` and `LikeButton.js:18-22,41` as having the same `axiosInstance` inline bug, and routes both through Task 4's `useAuthAxios` refactor. But Task 4 is FRONTEND-ONLY — it does NOT add a backend decorator. So after Task 4 ships, both `BookmarkButton` and `LikeButton` will send cleaner DELETE calls, and BOTH will hit 405.
- **Why it matters:** The synthesis fixes BookmarkViewSet (Task 1) but leaves LikeViewSet.delete as 405. PR ships. Production users hit a like button → fills red, can't un-fill. The exact same "stuck filled" symptom r1-backend.md Gaps #1 called out for bookmarks, now also true for likes. The r1-backend.md audit only read `BookmarkViewSet`; the sibling bug slipped through the same net.
- **Suggested change:** Add to Task 1 of synthesis: apply the same `@action(detail=False, methods=['delete'], url_path='')` decorator to `LikeViewSet.delete` at `views.py:470`. ~5 min additional work, identical code shape. r1-backend.md should add LikeViewSet to its audit checklist next time.

### Finding 2 — Cross-CT data loss on blog path (the path synthesis inherits as "out of scope")
- **Severity:** blocker
- **Lens:** integrity (silent cross-CT row destruction)
- **Claim:** The ADR's "Bug 2 fix" only patches the contract path. Blog path keeps `Bookmark.objects.filter(user=request.user, object_id=oid).first()` with NO content_type filter (line 882, 947, 903). Synthesis inherits this and tracks it as "intentional" / "ADR §Known Tech Debt."
- **Evidence (re-traced):**
  - `views.py:935-960` — `delete` blog path: `Bookmark.objects.filter(user=request.user, object_id=oid).first()`. The `.first()` will match the FIRST row by id ordering — could be a blog row OR a contract row, depending on insertion order. The method then `.delete()`s that single row.
  - Concrete failure scenario:
    1. User bookmarks WP blog post with `databaseId=42`. Row R1: `(user=U, content_type=Bookmark, object_id=42)`.
    2. User later visits activity detail for contract id=42. DayTripCard heart calls `/check/?content_type=contract&object_id=42` → filter `user + CT=operators.contract + object_id=42` → no match → returns `{bookmarked: false}`. Heart shows empty. (Good — contract path uses real CT.)
    3. User taps the empty heart. `POST /dialogue/bookmarks/ {content_type: "contract", object_id: 42}`. Contract path runs. Exists-check uses real CT (line 915) → no match → `Bookmark.objects.create(user, CT=operators.contract, 42)`. New row R2 created. Good.
    4. **Now reverse scenario**: User has a contract bookmark at id=42 (R2), and visits a BLOG with `databaseId=42`. Blog `check` filters `user + object_id=42` (no CT) → matches R2 → returns `{bookmarked: true}`. Heart shows filled. **WRONG** — user never bookmarked the blog.
    5. User taps to "remove" the (incorrectly) filled blog heart. `DELETE /dialogue/bookmarks/ {content_type: "blog_post", object_id: 42}`. Blog path runs (line 947). Filter `user + object_id=42` → matches R2 (the contract row!) → **deletes R2**. User's contract bookmark silently destroyed.
  - This is the worst kind of bug: silent, no error to user, no toast, no audit log. User goes to `/profile/saved-tours` (Q3 wishlist, future) and finds the contract missing.
- **Why it matters:** The blog path is the "leave as-is" decision in ADR §Bug 2. The synthesis inherits it. r1-backend.md's gap analysis is silent on this scenario. The new `unique_together` constraint actually makes the failure MORE reachable — it prevents the user from having two blog rows for the same id, but doesn't prevent the (Blog, id=42) ↔ (Contract, id=42) collision because the CT differs.
- **Suggested change:** Synthesis needs to either:
  - (a) Filter blog path delete by sentinel CT: `Bookmark.objects.filter(user=request.user, content_type=ContentType.objects.get_for_model(Bookmark), object_id=oid).first()`. Plus add a real `content_type='blog_post'` map in the schema (a `WP_POST_CT = ContentType.objects.get_for_model(Bookmark)` constant or a separate model). This is the cleanest fix.
  - (b) OR document the collision in the rollout as a known-data-loss vector and ship a "guard" that disallows `content_type='blog_post'` checks on a `Bookmark` row whose `content_type` is the sentinel but `object_id` matches a known contract id. Band-aid.
  - The real fix requires the data migration that ADR §Known Tech Debt defers — until then, ANY content type lookup against a blog row will be wrong. Synthesis must not inherit "fix blog path" as out of scope; it must call this out in Open Questions.

### Finding 3 — Keyboard Enter/Space on the heart IconButton navigates the Card (race)
- **Severity:** blocker
- **Lens:** race (event delegation)
- **Claim:** `DayTripCard.js:122-133` wraps the `FavoriteButton` in a `<Box onClick={(e) => e.stopPropagation()}>` to stop mouse-click bubble. The Card itself has `onKeyDown` (line 96-100) handling `Enter`/`Space` to navigate to the detail page. The Box has NO `onKeyDown` stopPropagation.
- **Evidence:**
  - `DayTripCard.js:90-115` — `<Card onClick={handleViewDetails} onKeyDown={...Enter/Space...} ...>` — keyboard listeners are active.
  - `DayTripCard.js:123-125` — `<Box onClick={(e) => e.stopPropagation()} sx={{...}}>` — only `onClick`, not `onKeyDown`.
  - `BookmarkButton.js:108` — `<IconButton onClick={handleBookmarkToggle} ...>` — IconButton handles Enter/Space via internal onClick mapping (React pattern). When pressed, it fires `handleBookmarkToggle` AND the keydown bubbles up to the Box, then to the Card.
  - Result: User tabs to heart, presses Enter → heart toggles state → click bubbles (or keydown bubbles) up → Card's onKeyDown catches Enter → `handleViewDetails()` → router.push to detail page. User toggles the heart AND navigates. Tap-and-disappear with no visible feedback.
- **Why it matters:** The UX audit (r1-ux.md §UX Risks "Optimistic flip on card click collision") only investigated MOUSE bubble. Keyboard path is unhandled. Worse: with IntersectionObserver hydration deferral (Task 8), users are MORE likely to use keyboard (tabbing through deferred placeholders that just became visible) — so the bug is amplified by another synthesis task.
- **Suggested change:** Add `onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') e.stopPropagation(); }}` to the Box at `DayTripCard.js:123`. ~2 lines. Synthesis Task 8's "verification" step should add a keyboard test.

### Finding 4 — Migration 0026 prod abort blocks migration 0027; no rollback tested
- **Severity:** major
- **Lens:** migration
- **Claim:** Synthesis §Phase C identifies prod dup audit (Task 2) as the deploy gate for migration 0026. Synthesis §Rollback plan claims "Django auto-generates reverse for `AlterUniqueTogether`" — but says nothing about the cascade if 0026 FAILS forward (DDL aborts).
- **Evidence:**
  - `smartenplus-backend/dialogue/migrations/0026_alter_bookmark_unique_together.py:15-19` — `AlterUniqueTogether` operation.
  - `smartenplus-backend/dialogue/migrations/0027_reviewimage.py:10` — `dependencies = [('dialogue', '0026_alter_bookmark_unique_together')]`. **If 0026 fails, 0027 cannot apply.** (0027 was generated 2026-06-05, after 0026 on 2026-06-02. Has 0027 been deployed? Synthesis doesn't say.)
  - `smartenplus-backend/dialogue/migrations/0025_review_guest_email.py` (the prior one) exists. 0024 is the most recent pre-0026.
  - DDL behavior on Postgres: `ALTER TABLE ... ADD CONSTRAINT ... UNIQUE` runs as a single statement inside a transaction. If it fails, the transaction aborts and the constraint is NOT added. **However** Django's `migrate` command wraps each migration in a transaction by default, so failure should be clean. BUT: if Django is run with `--no-utpc-constraints` or against a Postgres setup with autocommit-like behavior (e.g., some RDS Proxy configurations), the partial state is a real risk.
  - More importantly: synthesis §Rollback plan says "Roll back 0026 to 0025" but doesn't validate that any in-flight 0027 application rolls back too. If 0027 was applied in a different deploy (e.g., a hotfix on 2026-06-06) and we now need to roll back 0026, `migrate dialogue 0025_review_guest_email` will FAIL because 0027 depends on 0026. Need to roll back to 0025 BEFORE 0027, but only if 0027 is currently applied.
- **Why it matters:** The synthesis treats the prod dup audit as a one-shot gate. The 0026→0027 dependency means a single bad migration can break deploys for any future `dialogue` migration. Ops needs to know the cascade.
- **Suggested change:** Add a Task 2.5: "Verify prod is on migration 0026 (not 0027) before 0026 ships. If 0027 is already applied, plan to ship 0026 with `--fake-initial` and a manual `ALTER TABLE` for the constraint." ~5 min ops check. Synthesis §Rollback plan should explicitly chain: "If 0027 is applied: `migrate dialogue 0026` first (reverse-0027), then `migrate dialogue 0025`. If only 0026 applied: `migrate dialogue 0025` directly."

### Finding 5 — Two-tab race condition: unique constraint saves DB, breaks UX
- **Severity:** major
- **Lens:** race
- **Claim:** User has Tab A and Tab B open on `/activities?category=DAY_TOUR`. Taps heart in Tab A (optimistic fill). Before Tab A's POST returns, taps heart in Tab B on the same card (optimistic fill). Tab A's POST wins, 201. Tab B's POST hits unique constraint, 409 → catch block reverts → Tab B heart flips from filled back to empty.
- **Evidence:**
  - `BookmarkButton.js:80-95` — handleBookmarkToggle: optimistic `setBookmarked(!previousState)` then await POST/DELETE. Catch block reverts. NO request deduplication.
  - `views.py:903` blog path + `views.py:915` contract path — both `.exists()` checks before create, but no `SELECT ... FOR UPDATE` or DB lock. Two concurrent POSTs in flight → both pass exists-check → one creates, the other's create hits unique constraint (now enforced by 0026) → `IntegrityError` → returns 409 (only if caught) or 500.
  - Wait — the views don't catch `IntegrityError` from the unique constraint. If 0026 is in place AND the application-level `.exists()` check races, the second POST raises `IntegrityError`, which DRF turns into a 500. The synthesis's Task 1 fix (decorator) doesn't add `try/except IntegrityError`.
  - Even if 409 is returned cleanly, Tab B's UX is: tap → filled → 100ms later empty. No explanation. User thinks the heart is broken.
- **Why it matters:** The unique constraint is meant to prevent DB-level dups, but it surfaces as a UX failure when the optimistic UI commits before the server response. Multi-tab browsing is a common pattern (e.g., users research activities in one tab, book in another).
- **Suggested change:** Synthesis should add to Task 1 (or as Task 1.5): wrap `Bookmark.objects.create` in `try/except IntegrityError` → return 409 with the same shape as the `.exists()` pre-check. ~3 lines. UX: optionally suppress the optimistic revert when the 409 is received and re-fetch /check/ (the truth source). Synthesis doesn't propose this; r1-ux.md §Risks "No undo path" is related but the synthesis didn't make the connection.

### Finding 6 — ADR §NIT: `_validate_contract_params` does live DB lookup per request, never cached
- **Severity:** nit (becomes major at scale)
- **Lens:** performance
- **Claim:** ADR §NIT acknowledged `ContentType.objects.get(app_label='operators', model='contract')` is a per-request DB hit. Synthesis inherits as "Acceptable at current volume" but doesn't add a `functools.lru_cache` fix.
- **Evidence:** `views.py:864-867` — every `check`, `create`, `delete` on the contract path runs the lookup. With 12 cards × page load × 1 /check/ = 12 hits per page load. At 100 concurrent users = 1200 SELECTs/min hitting `django_content_type` for the same row. Postgres buffer cache will absorb it (CT rows are tiny + hot), but it's a free win.
- **Why it matters:** Trivial to fix, removes a known ADR-flagged wart, makes the code self-documenting ("this is a static lookup").
- **Suggested change:** Module-level: `OPERATORS_CONTRACT_CT = ContentType.objects.get(app_label='operators', model='contract')` after Django apps are loaded, OR use `@functools.lru_cache(maxsize=None)` on a helper function `get_contract_ct()`. ~3 lines. Add as Task 9a or fold into Task 1.

### Finding 7 — `useAuthAxios` adds `baseURL`, but synthesis's refactored call still uses absolute `bookmarkUrl` — minor inconsistency
- **Severity:** nit
- **Lens:** performance / ux (code quality)
- **Claim:** The proposed `useAuthAxios` returns `instance` with `baseURL` set. The synthesis's refactored BookmarkButton code shape keeps `bookmarkUrl = \`${baseURL}/dialogue/bookmarks/\`` and calls `instance.delete(bookmarkUrl, { data: {...} })`.
- **Evidence:** Synthesis §Task 4 code shape:
  ```js
  const { instance: axiosInstance, token, isAuthenticated } = useAuthAxios();
  // ... no change to bookmarkUrl ...
  await axiosInstance.delete(bookmarkUrl, { data: { content_type, object_id } });
  ```
  With `baseURL` set on the instance, axios prepends it. The full URL becomes `https://api.smartenplus.co.thhttps://api.smartenplus.co.th/dialogue/bookmarks/` — malformed. Wait, axios with `baseURL` set and an absolute URL passed to `.delete()` uses the absolute URL, not base+path. So it works, but the absolute URL is now redundant.
- **Why it matters:** Code works but is misleading. The pattern doesn't match what `useAuthAxios` was designed for. Future devs reading the code will wonder: "why is baseURL set on the instance AND an absolute URL passed?" Maintainability hit.
- **Suggested change:** In the refactor, drop `bookmarkUrl` and call `instance.delete('/dialogue/bookmarks/', { data: {...} })`. Same for LikeButton. Or, alternatively, keep `bookmarkUrl` but pass it WITHOUT baseURL on the instance. Synthesis should pick one style. The cleaner pattern is to pass relative paths and let the instance's baseURL handle the prefix.

### Finding 8 — IntersectionObserver rootMargin 100px may be too tight for fast scrollers
- **Severity:** nit
- **Lens:** ux / performance
- **Claim:** Synthesis §Task 8 proposes `rootMargin: '100px'` to prefetch 100px before scroll.
- **Evidence:** On mobile (touch swipe), a single flick can scroll 300-500px. Trackpad scroll on a 12-card grid can hit similar velocities. With 100px prefetch, a fast scroll may reveal cards before the observer fires, leaving an empty 48×48 placeholder. User taps the empty space → nothing happens.
- **Why it matters:** This is the synthesis's Q2 "defer hydration" mitigation. If it lags, users see dead placeholders. The 100ms IntersectionObserver `setIsVisible` is a microtask, so it should be near-instant. But the dynamic `import()` for `FavoriteButton` (DayTripCard.js:20) is chunk-loaded. First-load of that chunk adds 50-200ms. Combined: fast scroll + chunk load = 250-400ms of dead placeholder.
- **Suggested change:** Bump `rootMargin` to `'200px'` or `'300px'`. Or `trigger once + setIsVisible(true)` immediately on the first `entry.isIntersecting` for cards above the fold (using `IntersectionObserverEntry.isIntersecting` on initial observation). Synthesis's Task 8 is otherwise correct.

---

## Verdict

**Fix-then-ship — but synthesis is missing 2 blockers (Findings 1, 2, 3) and 1 minor-but-real cascade (Finding 4).**

The synthesis correctly nails G1 (BookmarkViewSet.delete 405) and the 0026 prod dup gate. It does NOT spot:
1. **LikeViewSet has the identical 405 bug** — same fix applies, ~5 min.
2. **Cross-CT data loss on blog path** — this is a SILENT destructive bug the synthesis inherits from ADR. Either fix it (add CT filter to blog path delete) or call it out in Open Questions.
3. **Keyboard Enter/Space race** — synthesis's IntersectionObserver defer makes keyboard navigation more likely, and the Box has no onKeyDown stopPropagation.
4. **Migration cascade 0026→0027** — synthesis's rollback plan doesn't chain correctly if 0027 is already applied.

If Findings 1+2+3 are added to the plan, ship. If not, do not deploy — the un-favorite-broken + silent-data-loss + keyboard-nav-broken combo is exactly the "stuck filled" symptom r1-backend.md Gaps #1 was trying to explain, but in a way the team hasn't actually fixed.

The single biggest reason for Fix-then-Ship (not Ship-as-is): **the synthesis's G1 fix is necessary but not sufficient.** It fixes BookmarkViewSet's 405 but leaves LikeViewSet's 405 in place. The PR will close one half of a two-headed bug and ship the other half.

---

## Questions for Leader

1. **Cross-CT blog path correctness:** Is it acceptable to ship a heart that can silently delete the wrong bookmark? The ADR documents the bug as Known Tech Debt, but shipping a `useAuthAxios` refactor without addressing it means the user-facing impact (data loss) is real, not theoretical. Leader should escalate to product: "do you want us to fix the blog path's CT filter as part of this PR, or formally defer with a follow-up ticket that has a date?"

2. **LikeViewSet audit gap:** Why did r1-backend.md only audit BookmarkViewSet? LikeViewSet shares the pattern (line 470). Was the scope pre-narrowed? If yes, document that LikeViewSet is a SEPARATE ticket. If no, the audit was incomplete and Synthesis Task 1 should expand to both.

3. **Migration 0027 production state:** Has 0027 been deployed to prod? If yes, the rollback plan in §Phase D is wrong (cannot roll back to 0025 without first rolling back 0027). If no, the rollout is fine but the deploy script must guard against 0027 sneaking in first.

4. **IntersectionObserver + keyboard navigation:** When the user is keyboard-only (a11y user, screen reader, motor impairment), is the 100ms observer + chunk-load acceptable, or should the heart be hydrated on first focus (not on visible) for a11y compliance? Leader should consult WCAG 2.4.7 (focus visible) and 2.2.1 (timing adjustable) before finalizing Task 8.

5. **Two-tab UX:** Is the team OK with the heart "flips then reverts" behavior under multi-tab? If not, the fix is request deduplication on the client (use a Map of in-flight requests keyed by `(contentType, objectId, action)`) OR server-side `If-Match` semantics. Either is ~20 lines. Synthesis doesn't propose either.

6. **Save-into-void (Q3 contradiction):** Synthesis recommends "clean defer" but the wishlist page is the ONLY discoverable surface for the heart. If the user-facing symptom is "I tapped save and it's gone," that's a churn risk on day 1. Leader should confirm with product that the deferred wishlist page has a target sprint, not a vague "later."

## Related Atoms (Extracted 2026-06-13)
- [[sentinel-content-type-bookmark-blog]] — Skeptic Finding 2 (silent destructive data loss on blog path)
- [[iconbutton-keydown-stoppropagation-card]] — Skeptic Finding 3 (a11y blocker)
- [[lru-cache-content-type-lookup]] — Skeptic Finding 6 (`@lru_cache(maxsize=2)` for CT lookups; 12 hits/page eliminated)
- [[useauth-axios-hook-factory]] — Skeptic Finding 7 (relative vs absolute URL gotcha)
