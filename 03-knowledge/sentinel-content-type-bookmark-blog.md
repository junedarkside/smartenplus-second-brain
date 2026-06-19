# Sentinel Content Type Filter for Bookmark Blog Path

## Summary
`Bookmark.objects.filter(user=...)` queries on the blog path MUST filter by sentinel `content_type=ContentType.objects.get_for_model(Bookmark)` to prevent cross-content-type row destruction (user has contract bookmark at id=42, visits blog post with `databaseId=42`, taps "remove" → silently deletes the contract row).

## Context
The `Bookmark` model in Django is a generic foreign key — `content_type` + `object_id` points to a bookmarked row. The current schema uses `Bookmark` as its own content type (the row IS the bookmark). When the blog's "save/bookmark" feature is added, it will likely reuse this Bookmark model rather than create a separate `BlogBookmark` model — the natural next step is to allow blog posts to be bookmarked too.

## Problem
The worst-class silent destructive bug. Concrete scenario:
1. User bookmarks contract id=42 → Bookmark row (content_type=Bookmark, object_id=42) created
2. User visits blog post that happens to have `databaseId=42` (WordPress blog ID 42 = same number, different model)
3. User taps "remove bookmark" on the blog post
4. Frontend calls `DELETE /api/bookmarks/?object_id=42` without filtering by content type
5. Backend query: `Bookmark.objects.filter(user=u, object_id=42).delete()` — deletes the contract bookmark row
6. User loses their contract bookmark with zero UI indication anything went wrong

The bug is silent (200 response, UI shows "removed"), destructive (real data loss), and only triggers on number collision between blog IDs and contract IDs.

## Details
Until the proper `BlogBookmark` content type migration ships, the safe bridge is the sentinel filter:

```python
# bookmarks/views.py or bookmarks/services.py
from django.contrib.contenttypes.models import ContentType
from .models import Bookmark

bookmark_ct = ContentType.objects.get_for_model(Bookmark)

# ALWAYS filter by content_type=Bookmark on the blog path
Bookmark.objects.filter(
    user=request.user,
    content_type=bookmark_ct,
    object_id=blog_post_database_id,
).delete()
```

The blog path uses the same Bookmark model but the `content_type=Bookmark` filter scopes the query to "rows that ARE bookmarks" — not "rows bookmarked by the user, regardless of target." The two are very different.

## Decision
All blog-path bookmark queries MUST include the sentinel `content_type=ContentType.objects.get_for_model(Bookmark)` filter. This is the only safe bridge until a real `BlogBookmark` content type migration lands. Add a model-level check or a custom manager that enforces this — relying on view-level discipline is fragile.

## Tradeoffs
- Pro: Prevents the silent destructive bug class entirely
- Pro: One-line filter, no schema change
- Pro: Drop-in replacement when `BlogBookmark` content type ships
- Con: The filter is "until migration" — must be tracked as tech debt and removed once the proper content type exists
- Con: If a future code path forgets the filter, the bug returns silently. Need a model-level constraint or test to catch this.

## Consequences
This is a known silent data loss path. The fix must be enforced at the model or manager level, not just in views. Consider adding a custom manager `Bookmark.objects.for_blog()` that hard-codes the content_type filter — any view that uses the raw manager on the blog path will be a code review red flag.

The audit in `01-projects/contract-model-ambiguity-audit.md` identifies the broader pattern: generic FKs + cross-content-type lookups = silent data loss risk. The sentinel filter is the immediate mitigation.

## Related
- [[contract-model-ambiguity-audit]] — broader generic FK ambiguity audit
- [[django-serializer-shadowing-pattern]] — related DRF serializer pattern that can mask these bugs
