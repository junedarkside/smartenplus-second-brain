# ADR: Activity Card Favorite Button — Persistent via Bookmark API

## Summary
Extend `BookmarkButton.js` with `icon` + `variant` props. Fix `BookmarkViewSet` with two separate validation methods — blog path unchanged, contract path gets real ContentType lookup. Replace local-state heart in `DayTripCard` with wired component. No new models, no migration.

## Context
`DayTripCard` at `/activities?category=DAY_TOUR` has a heart button with `useState(false)` only — resets on every refresh. Backend has a generic `Bookmark` model (ContentTypes framework) already used for blog posts. Decision: reuse or build new?

## Problem
- Heart in `DayTripCard.js:32` is cosmetic only — no persistence
- `BookmarkViewSet._validate_wordpress_params` hard-rejects any `content_type != 'blog_post'` (line 837)
- `BookmarkButton.js` icon and style hardcoded — no heart/overlay mode
- Two silent ORM bugs in `BookmarkViewSet` (details below)
- **Critical:** blog `object_id` = WordPress `databaseId` (not Django PK). Blog `content_type` FK stores `Bookmark`'s own CT row as sentinel (Bug 1) — corrupted but functional. Fixing blog CT would break existing prod data.

## Decision
**Extend existing infrastructure. Do not create new model or migration.**

Two separate validation methods — not one unified method — per single-responsibility principle.

## Architectural Details

### Backend Bug 1 — `create` stores wrong ContentType (line 900)
```python
# WRONG — stores Bookmark model's own CT, not the target object
content_type=ContentType.objects.get_for_model(Bookmark)
```
- **Blog path:** keep sentinel behaviour — fixing breaks existing prod bookmarks
- **Contract path:** fix with `ContentType.objects.get(app_label='operators', model='contract')`

### Backend Bug 2 — ORM filters missing `content_type` (lines 868, 928)
```python
# WRONG — blog post ID 42 and contract ID 42 would collide
Bookmark.objects.filter(user=request.user, object_id=object_id)
```
- **Blog path:** leave as-is — existing data has no real CT, adding filter would return zero results
- **Contract path:** add `content_type=ct` to all three ORM queries (`check`, `create`, `delete`)

### Two separate validation methods

No `Contract` import needed — `ContentType.objects.get(app_label=..., model=...)` resolves by string.

```python
def _validate_blog_params(self, content_type, object_id):
    # Unchanged from _validate_wordpress_params — returns (content_type_str, int_id)
    if not content_type or not object_id:
        raise ValidationError({"error": "Missing required parameters", "message": "Both content_type and object_id are required"})
    if content_type != 'blog_post':
        raise ValidationError({"error": "Unsupported content type", "message": f"Content type '{content_type}' is not supported"})
    try:
        object_id = int(object_id)
        if object_id <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        raise ValidationError({"error": "Invalid WordPress post ID", "message": "WordPress post ID must be a positive integer"})
    return content_type, object_id

def _validate_contract_params(self, content_type, object_id):
    # New — returns (ContentType obj, int_id)
    try:
        object_id = int(object_id)
        if object_id <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        raise ValidationError({"error": "object_id must be a positive integer"})
    try:
        ct = ContentType.objects.get(app_label='operators', model='contract')
    except ContentType.DoesNotExist:
        raise ValidationError({"error": "Contract content type not found"})
    return ct, object_id
```

Each action dispatches:
```python
if content_type == 'blog_post':
    ...
elif content_type == 'contract':
    ...
else:
    raise ValidationError({"error": f"Content type '{content_type}' is not supported"})
```

### Full action implementations

**`check`:**
```python
@action(detail=False, methods=['get'], url_path='check')
def check(self, request):
    content_type = request.query_params.get('content_type')
    object_id = request.query_params.get('object_id')
    if content_type == 'blog_post':
        _, oid = self._validate_blog_params(content_type, object_id)
        bookmark = Bookmark.objects.filter(user=request.user, object_id=oid).first()
    elif content_type == 'contract':
        ct, oid = self._validate_contract_params(content_type, object_id)
        bookmark = Bookmark.objects.filter(user=request.user, content_type=ct, object_id=oid).first()
    else:
        raise ValidationError({"error": f"Content type '{content_type}' is not supported"})
    return Response({'bookmarked': bookmark is not None})
```

**`create`:**
```python
def create(self, request, *args, **kwargs):
    content_type = request.data.get('content_type')
    object_id = request.data.get('object_id')
    if content_type == 'blog_post':
        _, oid = self._validate_blog_params(content_type, object_id)
        if Bookmark.objects.filter(user=request.user, object_id=oid).exists():
            return Response({"error": "Already bookmarked", "message": "You have already bookmarked this post"}, status=status.HTTP_409_CONFLICT)
        bookmark = Bookmark.objects.create(
            user=request.user,
            content_type=ContentType.objects.get_for_model(Bookmark),  # keep sentinel — don't break existing data
            object_id=oid
        )
    elif content_type == 'contract':
        ct, oid = self._validate_contract_params(content_type, object_id)
        if Bookmark.objects.filter(user=request.user, content_type=ct, object_id=oid).exists():
            return Response({"error": "Already bookmarked", "message": "You have already bookmarked this contract"}, status=status.HTTP_409_CONFLICT)
        bookmark = Bookmark.objects.create(user=request.user, content_type=ct, object_id=oid)
    else:
        raise ValidationError({"error": f"Content type '{content_type}' is not supported"})
    return Response({"success": True, "message": "Bookmark added successfully", "data": {"id": bookmark.id, "content_type": content_type, "object_id": bookmark.object_id, "created_at": bookmark.created_at}}, status=status.HTTP_201_CREATED)
```

**`delete`:**
```python
def delete(self, request, *args, **kwargs):
    content_type = request.data.get('content_type')
    object_id = request.data.get('object_id')
    if content_type == 'blog_post':
        _, oid = self._validate_blog_params(content_type, object_id)
        bookmark = Bookmark.objects.filter(user=request.user, object_id=oid).first()
    elif content_type == 'contract':
        ct, oid = self._validate_contract_params(content_type, object_id)
        bookmark = Bookmark.objects.filter(user=request.user, content_type=ct, object_id=oid).first()
    else:
        raise ValidationError({"error": f"Content type '{content_type}' is not supported"})
    if not bookmark:
        return Response({"error": "Not found", "message": "Bookmark not found"}, status=status.HTTP_404_NOT_FOUND)
    bookmark.delete()
    return Response({"success": True, "message": "Bookmark removed successfully"})
```

### `BookmarkButton.js` — new props + overlay variant

New imports:
```js
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';
import FavoriteIcon from '@mui/icons-material/Favorite';
import IconButton from '@mui/material/IconButton';
```

New props: `icon = 'bookmark'`, `variant = 'default'`

Overlay early return (before existing `<button>` JSX):
```jsx
if (variant === 'overlay') {
  return (
    <IconButton
      onClick={handleBookmarkToggle}
      disabled={loading || status === 'loading'}
      size="small"
      sx={{
        bgcolor: 'rgba(255,255,255,0.8)',
        '&:hover': { bgcolor: 'white' },
        opacity: (loading || status === 'loading') ? 0.5 : 1,
        transition: 'opacity 0.2s',
      }}
      aria-label={bookmarked ? 'Remove from wishlist' : 'Save to wishlist'}
    >
      {icon === 'heart'
        ? bookmarked
          ? <FavoriteIcon sx={{ fontSize: 18, color: '#E11D48' }} />
          : <FavoriteBorderIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
        : bookmarked
          ? <BookmarkIcon fontSize="small" className="text-fb-blue" />
          : <BookmarkBorderIcon fontSize="small" className="text-gray-500" />
      }
    </IconButton>
  );
}
```

Default `<button>` path unchanged. No spinner in overlay (no layout shift on card).

### `DayTripCard.js` — swap local state for wired component

Remove (lines 15, 18–19, 32):
```js
import React, { useState } from 'react';  // → import React from 'react'
import FavoriteIcon from '@mui/icons-material/Favorite';
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';
const [isWishlisted, setIsWishlisted] = useState(false);
```

Add:
```js
import dynamic from 'next/dynamic';
const FavoriteButton = dynamic(() => import('../../blog/BookmarkButton'), { ssr: false });
```

Replace wishlist `<button>` block (lines 124–132):
```jsx
<Box
  onClick={(e) => e.stopPropagation()}
  sx={{ position: 'absolute', top: 8, right: 8, zIndex: 10 }}
>
  <FavoriteButton
    contentType="contract"
    objectId={workingContract.id}
    icon="heart"
    variant="overlay"
  />
</Box>
```

## Tradeoffs

| | Extend Bookmark | New Favorite model |
|--|--|--|
| Migration | No | Yes |
| Backend files | 1 | 4+ |
| Blog regression risk | None (path isolated) | None |
| Contract data integrity | Correct (real CT) | Correct |
| Tech debt | Blog CT corruption documented, not fixed | Clean slate |

## Consequences
- Activity card favorites persist per user, survive refresh
- Unauthenticated → `useAuthRedirect` → `/api/auth/signin?callbackUrl=/activities...`
- Blog bookmark unchanged — default props preserve all existing behaviour
- Blog CT corruption documented but not fixed (out of scope — requires data migration)
- `operators.Contract` CT row auto-exists in `django_content_type`

## Scrutiny Findings (post-grill audit)

### BLOCKER — Missing `unique_together` on `Bookmark` model

`dialogue/models.py:148` — `Bookmark` has no `unique_together`. `Like` model at line 100 has `unique_together = ('content_type', 'object_id', 'user')`. `Bookmark` does not.

**Impact:** Duplicate guard in `create` is application-level only (`.exists()` check, no DB lock). Two simultaneous POSTs pass both checks → two rows created → user unfavorites → `delete` removes one → `check` still returns `True` → heart stuck filled permanently.

**Fix — 1 migration required (ADR claim "no migration" was wrong for correctness):**
```python
# dialogue/models.py — add Meta class to Bookmark
class Bookmark(models.Model):
    ...
    class Meta:
        unique_together = ('content_type', 'object_id', 'user')
```
Generate: `python manage.py makemigrations dialogue`. Non-destructive — adds DB index only.

### MAJOR — `_validate_contract_params` signature includes unused `content_type` param

Dispatch already guarantees `content_type == 'contract'` before calling. Receiving it as param is misleading — future dev passes wrong value, no error.

**Fix:** Remove from signature and all call sites:
```python
def _validate_contract_params(self, object_id):  # not content_type
```
Call: `ct, oid = self._validate_contract_params(object_id)`

### MAJOR (pre-existing, document only) — `axiosInstance` in `useEffect` deps = infinite fetch

`BookmarkButton.js:36–60` — `axiosInstance = axios.create(...)` is inline (new object each render). Line 60 deps: `[contentType, objectId, axiosInstance]`. New object each render → `useEffect` fires every render → network request to `/check/` each cycle.

**Not broken because:** `setBookmarked(false)` when already `false` = no state change = React bails after 1–2 cycles. But it still fires the fetch on every parent re-render until state stabilizes. Worse in overlay variant (hydrates on client).

**Fix (separate task, not in this ADR):**
```js
const token = session?.accessToken;
const axiosInstance = useMemo(() => axios.create({
    headers: { Authorization: `Bearer ${token}` }
}), [token]);
// useEffect deps: [contentType, objectId, token]
```
Same bug exists in `LikeButton.js:41`. Fix both together in a separate cleanup task.

### NIT — `_validate_contract_params` does live DB lookup per request

`ContentType.objects.get(app_label='operators', model='contract')` hits DB on every call. Acceptable at current volume. Future: cache with `functools.lru_cache` or module-level lazy init.

## Known Tech Debt
- Blog bookmark `content_type` FK stores `Bookmark`'s own CT row (sentinel). Real fix: migrate existing rows to correct `blog_post`-equivalent CT and update view. Deferred — needs WP-side mapping.
- `axiosInstance` inline in `BookmarkButton` + `LikeButton` causes unnecessary re-fetches. Fix with `useMemo([token])`. Separate task.

## Files Changed
| File | Change |
|------|--------|
| `smartenplus-backend/dialogue/views.py` | Two separate validate methods; dispatch per content_type; contract path gets real CT + correct ORM filters |
| `smartenplus-backend/dialogue/migrations/00XX_bookmark_unique_together.py` | **New** — adds `unique_together` constraint to `Bookmark` |
| `smartenplus-frontend/components/blog/BookmarkButton.js` | `icon` + `variant` props; overlay uses `<IconButton>`; spinner suppressed in overlay |
| `smartenplus-frontend/components/activities/browse/DayTripCard.js` | Remove local state; dynamic import; mount with `contract` + `overlay` |

## Verdict
**Fix-then-ship.** Core architecture correct. One migration needed (unique constraint). One signature cleanup. Pre-existing fetch loop documented for separate task.

## Related
- [[nextjs-hydration-rules]] — SSR safety via `dynamic(..., { ssr: false })`
- [[activities-browse-filter-inactive-contracts]] — same `DayTripCard` context
