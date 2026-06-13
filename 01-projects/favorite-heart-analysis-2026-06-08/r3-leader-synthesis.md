# R3 Leader Synthesis — FAV-1 Favorite Heart

**Session #82 · 2026-06-08 · Leader synthesis (final report)**

## Verdict

**Fix-then-ship.** Skeptic found 3 NEW BLOCKERs not in Phase-2 synthesis + confirmed the 1 BLOCKER synthesis caught. Highest priority: silent cross-CT data loss on the blog path (`views.py:882, 947, 903`) — user with a contract bookmark at id=42 visiting a blog post with `databaseId=42` will see the heart pre-filled and tapping "remove" silently destroys the contract row. Code work ~2-3 hrs; external prod-dup audit gates the 0026 migration but does NOT gate code merge.

## Phase Summary

- **Phase 1 (3 specialists)**
  - **Backend** ([r1-backend.md](./r1-backend.md)): ADR bugs 1 & 2 confirmed shipped (`views.py:910, 920`). New BLOCKER found — `def delete` at `views.py:935` lacks `@action` decorator → 405 on list URL → un-favorite broken in prod. Prod dup audit MUST run before 0026.
  - **Frontend** ([r1-frontend.md](./r1-frontend.md)): BookmarkButton overlay shipped (`BookmarkButton.js:105-129`), DayTripCard wired (`DayTripCard.js:127-132`). axiosInstance inline (`BookmarkButton.js:41-45`, `LikeButton.js:18-22`) still firing re-fetches. WCAG 2.5.5 fail at `BookmarkButton.js:110` (`size="medium"` = 40px, needs 44). Recommended `useAuthAxios()` hook factory at `components/utils/useAuthAxios.js`.
  - **UX** ([r1-ux.md](./r1-ux.md)): "Save into void" — no Saved Tours surface in `ProfileMenu.js`. Optimistic flip without animation. Per Q3 user grill decision: clean defer, no stub.
- **Phase 2 (synthesis)**: 9-task plan. Q3 deferred. Confirmed BookmarkViewSet 405. Q2 IntersectionObserver mitigation for N+1 hydration.
- **Phase 3 (skeptic)** ([r2-skeptic.md](./r2-skeptic.md)): 8 findings — 3 BLOCKER, 3 MAJOR, 2 NIT. 2 of 3 BLOCKERS were missed by synthesis (LikeViewSet 405, cross-CT silent corruption, keyboard race amplified by Q2).
- **Phase 4 (leader, this doc)**: Reorder to 14 tasks; group into 4 commits + 1 external task. Defer Q3 wishlist + Q4 a/b test + blog CT data migration.

---

## Updated Task List (priority order)

### 1. [BLOCKER — Skeptic #2] Cross-CT data loss on blog path

- **Severity:** silent destructive data corruption (worst-class bug — no error to user)
- **File:** `smartenplus-backend/dialogue/views.py:882, 903, 947`
- **Defect:** Blog path queries `Bookmark.objects.filter(user=request.user, object_id=oid)` with NO `content_type` filter. A user with contract bookmark `(user=U, CT=operators.contract, object_id=42)` who visits a blog with `databaseId=42` hits the blog path: `check` returns `bookmarked=true` (matches the contract row), tap "remove" runs `delete` which calls `Bookmark.objects.filter(user, object_id=42).first().delete()` → contract row destroyed.
- **Fix shape:** Add sentinel CT filter to ALL 3 blog-path queries.
  ```python
  # views.py:882 (check)
  bookmark = Bookmark.objects.filter(
      user=request.user,
      content_type=ContentType.objects.get_for_model(Bookmark),
      object_id=oid
  ).first()
  # Same shape at :903 (.exists()) and :947 (.first()).
  ```
  Cache the sentinel CT at module-level (see Task 12) so it doesn't re-query 3× per request.
- **Effort:** 20 min
- **Risk:** LOW. Existing blog rows ALL have sentinel CT set (per ADR Bug 1 fix — `views.py:910`), so the added filter is a no-op for the intended row set but blocks the cross-CT collision. Validate with: `SELECT COUNT(*) FROM dialogue_bookmark WHERE content_type_id = (SELECT id FROM django_content_type WHERE app_label='dialogue' AND model='bookmark');` should equal blog-bookmark count.
- **Deps:** None.

### 2. [BLOCKER — Skeptic #1] LikeViewSet.delete 405

- **Severity:** stuck-filled symptom in prod (like cannot be un-toggled, `dialogue_like` grows unbounded)
- **File:** `smartenplus-backend/dialogue/views.py:470`
- **Defect:** `def delete(self, request, *args, **kwargs):` overrides `ModelViewSet.destroy` (bound to detail URL `/dialogue/likes/{id}/`), but frontend (`LikeButton.js:56`) calls list URL `/dialogue/likes/` with body → DRF 405. Same root cause as BookmarkViewSet (Task 4); the audit only checked BookmarkViewSet.
- **Fix shape:**
  ```python
  # views.py:469 — add decorator above def delete
  @action(detail=False, methods=['delete'], url_path='')
  def delete(self, request, *args, **kwargs):
      ...
  ```
- **Effort:** 5 min (one decorator line)
- **Risk:** LOW. The current method is already 405-dead in prod — adding the decorator only enables what was always intended.
- **Deps:** None.

### 3. [BLOCKER — Skeptic #3] DayTripCard keyboard Enter/Space race

- **Severity:** a11y blocker — keyboard users toggle heart AND navigate away
- **File:** `smartenplus-frontend/components/activities/browse/DayTripCard.js:123-125`
- **Defect:** Card has `onKeyDown` at `:96-101` that fires on Enter/Space → `handleViewDetails()` → `router.push`. Box wrapper at `:123-125` only stops `onClick`, not `onKeyDown`. When focused heart receives Enter/Space, IconButton fires `handleBookmarkToggle` AND key bubbles to Card → navigation. Q2 IntersectionObserver (Task 11) amplifies this by encouraging keyboard tab through deferred cards.
- **Fix shape:**
  ```jsx
  <Box
    onClick={(e) => e.stopPropagation()}
    onKeyDown={(e) => {
      if (e.key === 'Enter' || e.key === ' ') e.stopPropagation();
    }}
    sx={{ position: 'absolute', top: 8, right: 8, zIndex: 10 }}
  >
  ```
- **Effort:** 2 min
- **Risk:** LOW. Pure additive listener; does not change Card's nav behavior for the rest of the card surface.
- **Deps:** None.

### 4. [BLOCKER — Synthesis G1] BookmarkViewSet.delete 405

- **Severity:** un-favorite broken in prod; row growth unbounded
- **File:** `smartenplus-backend/dialogue/views.py:935`
- **Defect:** `def delete` overrides `ModelViewSet.destroy` (detail URL), frontend (`BookmarkButton.js:86`) calls list URL `/dialogue/bookmarks/`. Same shape as Task 2.
- **Fix shape:**
  ```python
  # views.py:934 — add decorator above def delete
  @action(detail=False, methods=['delete'], url_path='')
  def delete(self, request, *args, **kwargs):
      ...
  ```
- **Effort:** 5 min
- **Risk:** LOW. Same justification as Task 2.
- **Deps:** None.

### 5. [BLOCKER — Synthesis Task 2] Prod dup audit on RDS

- **Severity:** gates 0026 migration deploy (NOT code merge)
- **External task** — not in repo
- **Run** (against `database-1.cajk6spdqzsx.us-west-2.rds.amazonaws.com`, read-only):
  ```sql
  SELECT user_id, content_type_id, object_id, COUNT(*) AS n
  FROM dialogue_bookmark
  GROUP BY 1, 2, 3
  HAVING COUNT(*) > 1
  ORDER BY n DESC;
  ```
- **If rows > 0:** dedupe manually (keep lowest `id`) BEFORE running `python manage.py migrate dialogue`:
  ```sql
  DELETE FROM dialogue_bookmark
  WHERE id NOT IN (
    SELECT MIN(id) FROM dialogue_bookmark
    GROUP BY user_id, content_type_id, object_id
  );
  ```
- **Effort:** 15 min with RDS access
- **Risk:** ZERO (read-only audit). Cleanup deletes only duplicate rows.
- **Deps:** RDS read access. Blocks the migration apply, NOT the code merge.

### 6. [MAJOR — Skeptic #4] Migration 0026 abort cascade blocks 0027

- **Severity:** ops cascade — bad 0026 leaves `dialogue` migrations stuck
- **Files:** `smartenplus-backend/dialogue/migrations/0026_alter_bookmark_unique_together.py:15-19`, `0027_reviewimage.py:10`
- **Defect:** `0027` depends on `0026`. If `0026` aborts forward (e.g., dup violation), `0027` cannot apply. If `0027` has ALREADY been applied to prod (file dated 2026-06-05, 3 days post-0026), the synthesis's rollback "to 0025" requires reverse-0027 first.
- **Fix shape:** Add to deploy runbook in this repo (`smartenplus-backend/docs/RUNBOOK_BOOKMARK_UNIQUE.md` or similar):
  1. Verify current prod migration state: `python manage.py showmigrations dialogue | grep -E '(0025|0026|0027)'`
  2. If `0027` already applied, rollback path: `migrate dialogue 0026` → `migrate dialogue 0025`
  3. If only `0026` applied, rollback: `migrate dialogue 0025`
  4. After dedupe (Task 5), re-apply: `migrate dialogue 0026` then `migrate dialogue 0027`
- **Effort:** 10 min doc + 1 ssh check
- **Risk:** LOW (documentation only; no code change).
- **Deps:** Ops/SRE has shell access. Coordinate with Task 5.

### 7. [Q5 IN-SCOPE] Extract `useAuthAxios()` hook + refactor BookmarkButton + LikeButton

- **Severity:** code quality + perf (eliminates re-fetch loop)
- **New file:** `smartenplus-frontend/components/utils/useAuthAxios.js`
- **Refactor:** `BookmarkButton.js:41-45,65`, `LikeButton.js:18-22,41`
- **Defect:** `axios.create({...})` runs every render → new object reference → `useEffect` dep `[contentType, objectId, axiosInstance]` re-fires → `/check/` re-hits. Today React state bail-out masks it after 1-2 cycles but parent re-renders restart the storm. 12 cards × N renders = N+1 hydration storm.
- **Fix shape:**
  ```js
  // components/utils/useAuthAxios.js (matches useAuthRedirect.js factory pattern)
  import { useMemo } from 'react';
  import axios from 'axios';
  import { useSession } from 'next-auth/react';
  import { baseURL } from '../../helpers/constants';

  export const useAuthAxios = () => {
    const { data: session } = useSession();
    const token = session?.accessToken;
    const instance = useMemo(
      () => axios.create({ baseURL, headers: { Authorization: `Bearer ${token}` } }),
      [token]
    );
    return { instance, token, isAuthenticated: !!token };
  };
  ```
  ```js
  // BookmarkButton.js — replace lines 39-45,65,86,91
  const { instance: axiosInstance, token } = useAuthAxios();
  // remove `const bookmarkUrl = ${baseURL}/dialogue/bookmarks/` (use relative paths only — see Task 9)
  // useEffect deps: [contentType, objectId, token]
  await axiosInstance.get('/dialogue/bookmarks/check/', { params: {...} });
  await axiosInstance.post('/dialogue/bookmarks/', { content_type, object_id });
  await axiosInstance.delete('/dialogue/bookmarks/', { data: { content_type, object_id } });
  ```
  Same shape applied to `LikeButton.js`.
- **Effort:** 30 min (15 hook + 15 dual refactor)
- **Risk:** LOW-MED. Behavior preserved; relative-URL switch tested by network tab inspection on /activities and /blog/[slug].
- **Deps:** Tasks 2 + 4 (the 405 fix must be in same commit so the refactored DELETE actually works).

### 8. [MAJOR — Skeptic #5] Two-tab race surfaces as 100ms heart flip-revert

- **Severity:** UX glitch + uncaught `IntegrityError` could return 500
- **Files:** `smartenplus-backend/dialogue/views.py:903, 915` (race surfaces here); `BookmarkButton.js:80-95` (UX revert lives here)
- **Defect:** Multi-tab — both tabs pass `.exists()` check, one `.create()` succeeds, the other hits 0026 unique constraint → uncaught `IntegrityError` → DRF 500 OR (if DRF middleware converts) ambiguous 400. Optimistic UI in Tab B flips filled → empty → user sees flicker.
- **Fix shape (server, simplest path):**
  ```python
  # views.py:907-912 (blog path) and :918-920 (contract path) — wrap create in try/except
  from django.db import IntegrityError
  try:
      bookmark = Bookmark.objects.create(user=request.user, content_type=ct, object_id=oid)
  except IntegrityError:
      return Response(
          {"error": "Already bookmarked", "message": "You have already bookmarked this contract"},
          status=status.HTTP_409_CONFLICT
      )
  ```
- **Fix shape (client, complementary):** In `BookmarkButton.js:97-99` catch block, when `error.response?.status === 409` for a POST (already bookmarked) — KEEP optimistic `bookmarked=true`, do NOT revert. For DELETE 404, KEEP `bookmarked=false`. Treat duplicate-state errors as success.
- **Effort:** 20 min (10 backend + 10 client)
- **Risk:** LOW. Both fixes are defensive; no behavior change for the happy path.
- **Deps:** Task 4 (backend POST/DELETE in same commit) and Task 7 (client refactor in same commit).

### 9. [NIT — Skeptic #7] Misleading `baseURL` + absolute `bookmarkUrl` redundancy

- **Severity:** maintainability nit
- **File:** `BookmarkButton.js:39, 86, 91` and `LikeButton.js:16, 56, 62` (rolled into Task 7's refactor)
- **Defect:** `useAuthAxios()` sets `baseURL` on instance, but the refactor keeps `bookmarkUrl = ${baseURL}/dialogue/bookmarks/`. Axios uses the absolute URL and ignores baseURL silently — works but misleads future devs.
- **Fix shape:** Adopt the relative-path style — already shown in Task 7's snippet (drop `bookmarkUrl` / `likeUrl` constants entirely, pass `/dialogue/bookmarks/` and `/dialogue/likes/` as path strings).
- **Effort:** Folded into Task 7 (no extra time)
- **Risk:** None.
- **Deps:** Task 7.

### 10. [A11Y P0] BookmarkButton overlay 44×44 + focus ring

- **Severity:** WCAG 2.5.5 fail + WCAG 2.4.7 (focus visible)
- **File:** `smartenplus-frontend/components/blog/BookmarkButton.js:107-118`
- **Defect:** `size="medium"` renders 40×40 (below 44 spec). Default IconButton focus ring is faint on white bg.
- **Fix shape:**
  ```jsx
  <IconButton
    onClick={handleBookmarkToggle}
    disabled={loading || status === 'loading'}
    sx={{
      width: 44,
      height: 44,
      bgcolor: 'rgba(255,255,255,0.8)',
      '&:hover': { bgcolor: 'white' },
      '&:focus-visible': { outline: '2px solid #1E40AF', outlineOffset: 2 },
      opacity: (loading || status === 'loading') ? 0.5 : 1,
      transition: 'opacity 0.2s',
    }}
    aria-label={bookmarked ? 'Remove from wishlist' : 'Save to wishlist'}
  >
  ```
  (`size` prop removed; explicit `width/height: 44` is more reliable than `size="large"` which is 48 but composes oddly with MUI internal padding.)
- **Effort:** 5 min
- **Risk:** LOW. Larger touch target only.
- **Deps:** None.

### 11. [Q2 IN-SCOPE] IntersectionObserver hydration deferral for /check/

- **Severity:** perf — eliminates 12-card hydration storm on /activities
- **File:** `smartenplus-frontend/components/activities/browse/DayTripCard.js:122-133` (wrap FavoriteButton) OR move into `BookmarkButton.js` as opt-in `deferUntilVisible` prop
- **Fix shape (lean — wrap at the card level):**
  ```jsx
  // DayTripCard.js — useState + useRef + useEffect with IntersectionObserver
  const [isVisible, setIsVisible] = React.useState(false);
  const heartRef = React.useRef(null);
  React.useEffect(() => {
    if (!heartRef.current) return;
    const obs = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setIsVisible(true); obs.disconnect(); } },
      { rootMargin: '200px' }  // Skeptic #8: bump from 100 to 200 for fast-scroll/chunk-load lag
    );
    obs.observe(heartRef.current);
    return () => obs.disconnect();
  }, []);

  <Box
    ref={heartRef}
    onClick={(e) => e.stopPropagation()}
    onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') e.stopPropagation(); }}
    sx={{ position: 'absolute', top: 8, right: 8, zIndex: 10, width: 44, height: 44 }}
  >
    {isVisible && (
      <FavoriteButton
        contentType="contract"
        objectId={workingContract.id}
        icon="heart"
        variant="overlay"
      />
    )}
  </Box>
  ```
- **Effort:** 25 min
- **Risk:** MED. Reserve 44×44 box space (already added in Task 10) to avoid layout shift when component hydrates.
- **Deps:** Tasks 3 + 10 (must compose with onKeyDown stop + 44×44 placeholder).

### 12. [NIT — Skeptic #6] Cache `ContentType` lookup in `_validate_contract_params`

- **Severity:** perf nit — 12 cards × 1 /check/ per load → 12 redundant `django_content_type` SELECTs
- **File:** `smartenplus-backend/dialogue/views.py:864-867`
- **Fix shape:** Module-level helper with `lru_cache`:
  ```python
  # at top of views.py with other imports
  from functools import lru_cache

  @lru_cache(maxsize=2)
  def _get_contract_ct():
      return ContentType.objects.get(app_label='operators', model='contract')

  @lru_cache(maxsize=2)
  def _get_bookmark_sentinel_ct():
      return ContentType.objects.get_for_model(Bookmark)

  # in _validate_contract_params (views.py:864) — replace try/except block
  ct = _get_contract_ct()
  ```
  Same sentinel-CT helper used by Task 1's blog-path filter and Task 1's create-path sentinel (`views.py:910`).
- **Effort:** 10 min
- **Risk:** LOW. `lru_cache` survives process lifetime (gunicorn workers); CT rows do not change at runtime.
- **Deps:** Task 1 (uses the same sentinel helper).

### 13. [UX nice-to-have] Scale-pulse animation on heart fill

- **Severity:** delight — Klook/Booking parity
- **File:** `BookmarkButton.js:119-126`
- **Fix shape:** CSS keyframes on the filled-state Favorite icon:
  ```jsx
  // add to overlay sx (or as <Box> wrapper around the icon)
  '@keyframes heartPulse': { '0%': { transform: 'scale(1)' }, '50%': { transform: 'scale(1.3)' }, '100%': { transform: 'scale(1)' } },
  '& .filled-heart': { animation: bookmarked ? 'heartPulse 200ms ease-out' : 'none' }
  ```
- **Effort:** 30 min
- **Risk:** LOW.
- **Deps:** Task 10 (overlay sx restructure).
- **Recommendation:** include in Commit 3 if time permits; otherwise defer.

### 14. [DEFER] Out of scope for this PR

- Wishlist page / Saved Tours surface in `ProfileMenu.js` — Q3 user decision: clean defer, no stub.
- Heart count display (no `count` field exists on `Bookmark`).
- A/B test setup (Q4 user decision: 6 agents, ~90 min — no A/B infra).
- Blog `content_type` data migration to real `blog_post` CT — requires WP-side mapping. Task 1's sentinel-CT filter is the bridge fix.
- `BookmarkViewSet.lookup_field` change to composite key (r1-backend Gap #4 — future improvement).
- IntegrityError catch around `Like.objects.create` (`views.py:459`) — `Like` model already has `unique_together` (per ADR scrutiny) but no try/except. Same fix pattern as Task 8; defer to a follow-up Like-cleanup PR.

---

## Commit Strategy

Branch: **`260608-feat/fav-1-bookmark-extension`** from `develop` (per user explicit grill answer).

| # | Commit | Subject | Files | Effort |
|---|--------|---------|-------|--------|
| 1 | Backend BLOCKERs | `fix(bookmark): cross-CT data loss + 405 on Like/Bookmark delete + keyboard race` | `dialogue/views.py` (Tasks 1, 2, 4) + `DayTripCard.js` (Task 3) | 35 min |
| 2 | Hook extraction + un-favorite enablement | `refactor(auth): extract useAuthAxios + adopt in Bookmark/Like buttons + 409 dedup` | `components/utils/useAuthAxios.js` (new) + `BookmarkButton.js` + `LikeButton.js` + `dialogue/views.py` (Task 8 backend) | 50 min |
| 3 | A11Y + perf + polish | `feat(a11y): 44px heart + focus ring + IntersectionObserver hydration + scale pulse` | `BookmarkButton.js` (Task 10, 13) + `DayTripCard.js` (Task 11) + `dialogue/views.py` (Task 12) | 70 min |
| 4 | Migration safety | `docs(runbook): bookmark unique_together rollback + 0026/0027 cascade` | `smartenplus-backend/docs/RUNBOOK_BOOKMARK_UNIQUE.md` (Task 6) | 10 min |

**External (not a commit):** Task 5 prod dup audit on RDS — gates the migration deploy, not the code merge.

---

## Rollout

1. **Code merge:** PR → `develop` → 1 reviewer + Tasks 1, 2, 3, 4 manual smoke test on `/activities` and `/blog/[slug]`.
2. **Pre-migration:** Run Task 5 dup audit on RDS read-replica. If non-zero rows: dedupe with `DELETE ... NOT IN (MIN id)` (see Task 5 SQL).
3. **Migration:** `python manage.py migrate dialogue 0026` then `0027` (if not already applied). Reference Task 6 runbook for rollback chain.
4. **Feature flag:** Ship unflagged. Heart is already on the card; the fix is correctness, not visibility.
5. **Manual test (30 min):** Logged-in tap → fill → reload → still filled. Logged-out tap → signin redirect. Two-tab tap on same card → no flicker. Tab to heart → Enter → toggles WITHOUT navigation. iPhone 12 simulator → 44×44 tap target.

---

## Time Estimate

| Item | Time |
|------|------|
| Code work (Tasks 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12) | ~2.5 hrs |
| Optional polish (Task 13 scale pulse) | +30 min |
| External: prod dup audit (Task 5) | 15 min |
| Manual smoke test | 30 min |
| **Total focused work** | **~3-4 hrs** |

---

## Out of Scope (confirmed by user grill)

- Wishlist page (Q3 — clean defer, no stub)
- Heart count display
- A/B test setup (Q4)
- Blog CT corruption data migration (ADR §Known Tech Debt — Task 1 sentinel-filter is the safe bridge)
- `BookmarkViewSet.lookup_field` composite key (r1-backend Gap #4)
- `Like.objects.create` IntegrityError catch (separate Like-cleanup PR)

---

## Questions for User (max 2)

- **§A — Commit strategy:** Approve 4-commit split (BLOCKERs, hook+refactor, a11y+perf, docs) with prod dup audit gating ONLY the migration apply, not the code merge?
- **§B — Two-tab UX:** For Task 8 — accept "treat 409 POST and 404 DELETE as success-state" client policy (no refetch, no UI revert)? This is the simplest of the three options skeptic listed (swallow / refetch / 100ms dedup window) and matches the "no surprise reverts" UX principle.

---

## Severity Breakdown (skeptic findings + synthesis ownership)

| # | Finding | Severity | Source | Synthesis Plan |
|---|---------|----------|--------|---------------|
| Skeptic #1 | LikeViewSet.delete 405 | BLOCKER | skeptic | Task 2 |
| Skeptic #2 | Cross-CT blog-path data loss | BLOCKER | skeptic | Task 1 |
| Skeptic #3 | DayTripCard keyboard race | BLOCKER | skeptic | Task 3 |
| Synthesis G1 | BookmarkViewSet.delete 405 | BLOCKER | synthesis | Task 4 |
| Synthesis Task 2 | Prod dup audit | BLOCKER (gates migration) | synthesis | Task 5 |
| Skeptic #4 | 0026/0027 cascade | MAJOR | skeptic | Task 6 |
| Skeptic #5 | Two-tab race | MAJOR | skeptic | Task 8 |
| Skeptic #7 | Redundant baseURL + absolute URL | NIT | skeptic | Task 9 (folded into Task 7) |
| Skeptic #6 | CT lookup not cached | NIT | skeptic | Task 12 |
| Skeptic #8 | IntersectionObserver 100px tight | NIT | skeptic | Folded into Task 11 (200px) |

---

## References

- ADR: [04-decisions/adr-activity-card-favorite-button.md](../../04-decisions/adr-activity-card-favorite-button.md)
- Phase 1: [r1-backend.md](./r1-backend.md) · [r1-frontend.md](./r1-frontend.md) · [r1-ux.md](./r1-ux.md)
- Phase 3: [r2-skeptic.md](./r2-skeptic.md)
- Executive summary: [audit.md](./audit.md)

## Related Atoms (Extracted 2026-06-13)
- [[useauth-axios-hook-factory]] — `useAuthAxios()` `useMemo([token])`; pass relative paths to avoid 405 sync bug
- [[sentinel-content-type-bookmark-blog]] — `Bookmark.objects.filter` MUST filter by `content_type=ContentType.objects.get_for_model(Bookmark)` (silent destructive bug)
- [[iconbutton-keydown-stoppropagation-card]] — nested IconButton needs BOTH `onClick` + `onKeyDown` `stopPropagation`

## Sibling Sub-Files (Linked 2026-06-13)
- [[audit]] — executive summary
- [[migration-0026-runbook]] — DB migration 0026 runbook
- [[r1-backend]] — Phase 1 backend audit
- [[r1-frontend]] — Phase 1 frontend audit
