# R1 Backend Audit — FAV-1 Favorite Heart

Session #82 · 2026-06-08 · Backend specialist

## Backend Status

### ADR Compliance
- **Bug 1 fix (create stores real CT for contract):** SHIPPED. Blog path keeps sentinel `ContentType.objects.get_for_model(Bookmark)` (`smartenplus-backend/dialogue/views.py:910`); contract path uses real CT from `_validate_contract_params` and stores it via `Bookmark.objects.create(..., content_type=ct, object_id=oid)` (`smartenplus-backend/dialogue/views.py:920`). Matches ADR lines 113–120.
- **Bug 2 fix (ORM filter missing content_type for contract):** SHIPPED. `check` line 885 filters `user + content_type + object_id` for contract (no CT on blog path line 882 — intentional per ADR). `delete` line 950 same. `create` line 915 `.exists()` guard same. Matches ADR lines 95–96, 135–136, 117–118.
- **Two separate validation methods:** SHIPPED. `_validate_wordpress_params` (`smartenplus-backend/dialogue/views.py:830`) and `_validate_contract_params` (`smartenplus-backend/dialogue/views.py:856`) both present; dispatch in `check`/`create`/`delete` at lines 880–887, 901–922, 945–952. **Bonus:** `_validate_contract_params(self, object_id)` drops the misleading unused `content_type` param flagged in ADR MAJOR scrutiny — already applied (no cleanup needed).
- **unique_together migration:** EXISTS. `smartenplus-backend/dialogue/migrations/0026_alter_bookmark_unique_together.py:16-19` adds `unique_together={('content_type', 'object_id', 'user')}`. Model `dialogue/models.py:156-157` declares the same constraint. Migration generated 2026-06-02 (6 days pre-audit), depends on `0025_review_guest_email` (line 12) — no missing pre-reqs.

### Prod Dup Audit
**No DB access from this environment.** `.env` points to AWS RDS prod (`POSTGRES_DB_HOST=database-1.cajk6spdqzsx.us-west-2.rds.amazonaws.com`); local `db.sqlite3` is 0 bytes. Cannot run:
```sql
SELECT user_id, content_type_id, object_id, COUNT(*)
FROM dialogue_bookmark
GROUP BY 1,2,3
HAVING COUNT(*) > 1;
```
**Required before this migration runs in prod.** `AlterUniqueTogether` creates a unique index — DB will REJECT the ALTER if any (user, content_type, object_id) triplet already has >1 row. Block on someone with RDS read-replica access running the query.

**Likely hotspots to check first** (educated guess from code):
- Blog bookmarks — `object_id` is WP `databaseId`, CT is sentinel (Bookmark's own). If the same user re-bookmarked the same WP post during a window where `_validate_wordpress_params` 409 was not yet enforced, dups may exist.
- Contract bookmarks — fresh path, lower risk. Only ~weeks of prod traffic since contract path shipped.

### Gaps Discovered
1. **`delete` action routing is broken on ModelViewSet.** `def delete(self, request, *args, **kwargs)` at `smartenplus-backend/dialogue/views.py:935` overrides `ModelViewSet.destroy`, which is bound to **detail URL** `/dialogue/bookmarks/{id}/` — not the list URL the docstring claims (line 940: `DELETE /dialogue/bookmarks/`). DRF will 405 a DELETE on the list. Either the frontend hits the detail URL (but then `body` is ignored per HTTP spec on some stacks) or this endpoint is silently dead. Need to verify frontend `BookmarkButton.js` axios call shape — if it sends `DELETE /dialogue/bookmarks/` with body, **delete is broken in prod** (only `check` + `create` work; un-favoriting leaks rows). This is the strongest backend-side reason the heart appears "stuck filled" the ADR mentions.
2. **No `@action(detail=False, methods=['delete'])` decorator** on the custom `delete`. Should be a `@action(detail=False, methods=['delete'], url_path='remove')` (or similar) — current binding to list-level DELETE without decorator violates DRF convention. If anything hits `/dialogue/bookmarks/` with DELETE, DRF returns 405 even though the code is reachable through destroy.
3. **`get_queryset` filter at line 828** scopes Bookmark rows to `request.user` — but the default `ModelViewSet.list` and `destroy` actions still exist and route through `BookmarkSerializer`. If a malicious user calls `GET /dialogue/bookmarks/` they'll get only their own (safe), but `GET /dialogue/bookmarks/{id}/` could 404 cleanly (also safe). Low risk but worth noting.
4. **BookmarkViewSet has no `lookup_field`** set, so default is `id`. With the new `unique_together`, the (content_type, object_id, user) tuple is the natural key — not `id`. Long-term consideration; not blocking.

### Rollout Risk
- **0026 migration applying against non-empty prod data with dups → DDL fails, migration aborts mid-batch, partial schema state.** Django will leave the migration in a failed state. Recovery = manual `DELETE FROM dialogue_bookmark WHERE id IN (dupe ids)` then re-run. No data loss for *unique* triplets.
- **No reverse code path.** If 0026 has run and a user with dups somehow slipped through, the application `.exists()` guard at lines 903/915 prevents new dups — but pre-existing dups from before the guard was added are stuck. Migration won't add the constraint on a non-unique table.
- **Contract path is new code on top of an old data shape.** Users who bookmarked a contract in dev (CT=operators.contract) vs blog in prod (CT=dialogue.bookmark) live in the same `dialogue_bookmark` table now keyed by CT. Cross-CT collision at same `object_id` for same user is impossible post-migration (unique constraint includes CT).
- **Frontend depends on `delete` working.** If gap #1 is real, prod users can favorite but never un-favorite — unbounded row growth in `dialogue_bookmark`. Low volume (activity card heart), but still drift.

### Backend Tasks (in priority order)
1. **[dialogue/views.py:935] Fix `delete` action binding.** Add `@action(detail=False, methods=['delete'], url_path='remove')` decorator OR move to a custom URL via router. Verify which URL the frontend actually calls first. **Effort:** 15 min. **Risk:** low (only affects unfavorite path; no current users rely on it working in prod if it never worked).
2. **[prod DB, dialogue_bookmark] Run dup query before deploying 0026.** `SELECT user_id, content_type_id, object_id, COUNT(*) FROM dialogue_bookmark GROUP BY 1,2,3 HAVING COUNT(*) > 1;` If non-zero, dedupe manually (keep lowest `id`) before `python manage.py migrate`. **Effort:** 1 query + 1 cleanup SQL. **Risk:** zero (read-only audit; cleanup deletes dups only).
3. **[dialogue/views.py:856] Confirm `_validate_contract_params` signature is `(self, object_id)` not `(self, content_type, object_id)`.** Already done — line 856 shows `(self, object_id)`. **No-op.** (ADR scrutiny fix pre-applied.)
4. **[dialogue/models.py:156] Add explicit `indexes` for `(content_type, object_id)` hot path** (the check/create/delete filter combo). `unique_together` creates a unique index but covering just the (CT, object_id) half of the tuple would speed up `check` and `delete`. **Effort:** 5 min + 1 migration. **Risk:** low (additive index only). **Defer** until traffic justifies — current scale probably fine.
5. **[ops] Confirm 0026 deployed to prod.** Migration file exists locally 2026-06-02; cannot verify prod apply from code. **Effort:** 1 SSH/RDS check. **Risk:** high if 0026 has been applied to a DB that previously had dups — DDL failure with no rollback runbook.

## Verdict
**Fix-then-Ship.** Core ADR changes (Bugs 1/2, two validate methods, unique_together migration) all shipped and correct in code. Two real concerns remain: (a) `delete` action binding likely 405s in prod → unfavorite broken, (b) prod dup audit MUST run before 0026 applies or migration aborts. Both are 30-min fixes once DB access is available.
