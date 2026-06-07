# Migration 0026 Runbook — Bookmark unique_together

**Migration:** `0026_alter_bookmark_unique_together.py` (generated 2026-06-02)
**Blocks:** `0027_reviewimage.py` (depends on 0026, line 10)
**Risk:** DDL aborts on existing duplicate rows → migration state stuck → 0027 cannot apply.

## Pre-Migration Audit (REQUIRED)

Run on a read replica of prod RDS, NOT prod directly:

```sql
SELECT user_id, content_type_id, object_id, COUNT(*)
FROM dialogue_bookmark
GROUP BY user_id, content_type_id, object_id
HAVING COUNT(*) > 1;
```

- **0 rows:** Safe to apply. Proceed.
- **>0 rows:** STOP. Run cleanup (next section) before applying.

## Cleanup (if dups exist)

Manual dedupe — keep lowest `id` per (user_id, content_type_id, object_id) tuple:

```sql
-- Find dups first
SELECT id, user_id, content_type_id, object_id
FROM dialogue_bookmark
WHERE id NOT IN (
  SELECT MIN(id)
  FROM dialogue_bookmark
  GROUP BY user_id, content_type_id, object_id
);

-- Delete dups (keep MIN(id) per tuple)
DELETE FROM dialogue_bookmark
WHERE id NOT IN (
  SELECT MIN(id)
  FROM dialogue_bookmark
  GROUP BY user_id, content_type_id, object_id
);
```

Verify:

```sql
SELECT user_id, content_type_id, object_id, COUNT(*)
FROM dialogue_bookmark
GROUP BY 1, 2, 3
HAVING COUNT(*) > 1;
-- Expected: 0 rows
```

## Apply Migration

```bash
cd /path/to/smartenplus-backend
python manage.py migrate dialogue 0026
```

Expected output: `Applying dialogue.0026_alter_bookmark_unique_together... OK`

## Failure Recovery

If `ALTER UNIQUE TOGETHER` aborts mid-batch:

1. Check Django migration state:
   ```bash
   python manage.py showmigrations dialogue
   ```
   If `[ ] 0026` is unchecked: migration did NOT apply. Safe to re-run cleanup + retry.
   If `[X] 0026`: migration partially applied. Investigate before re-running.

2. If migration aborted at unique-index creation (DDL):
   - PostgreSQL: `ALTER TABLE ... ADD CONSTRAINT ... UNIQUE` is atomic. If it failed, the table is in the pre-0026 state. No partial state to clean.
   - Verify with `\d dialogue_bookmark` in psql — `unique_together` should NOT be present if migration aborted.

3. Re-run cleanup query, then re-apply.

## Cascade to 0027

If 0026 applied cleanly:

```bash
python manage.py migrate dialogue 0027
```

If 0026 failed, 0027 will fail with `NodeNotFoundError: Migration dialogue.0026_alter_bookmark_unique_together dependencies reference an unapplied migration. Do not apply this migration.` Fix 0026 first.

## Verification Post-Apply

```sql
-- Confirm constraint exists
SELECT conname, contype
FROM pg_constraint
WHERE conrelid = 'dialogue_bookmark'::regclass
  AND contype = 'u';
-- Expected: 1 row, conname includes 'content_type_object_id_user'

-- Confirm no dups (should already be 0 from pre-audit)
SELECT user_id, content_type_id, object_id, COUNT(*)
FROM dialogue_bookmark
GROUP BY 1, 2, 3
HAVING COUNT(*) > 1;
-- Expected: 0 rows
```

## App Code Dependencies

- Backend `dialogue/views.py:882, 903, 947` (blog path filters): now use `_blog_bookmark_ct()` helper from FAV-1 fix. Safe post-0026 because filter includes `content_type`.
- Backend `dialogue/views.py:915, 950` (contract path filters): include `content_type=ct`. Safe post-0026.
- 0026 + FAV-1 cross-CT fix are inseparable — apply 0026 with FAV-1 backend changes.

## Reference

- FAV-1 audit: `01-projects/favorite-heart-analysis-2026-06-08/`
- Skeptic finding #4: `r2-skeptic.md`
- Leader synthesis: `r3-leader-synthesis.md` (Task 5: RDS dup audit, Task 6: cascade runbook)
