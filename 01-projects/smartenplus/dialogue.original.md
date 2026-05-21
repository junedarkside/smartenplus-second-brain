# Dialogue — Social & Community

## Summary
Dialogue app is social/community layer. Review system linked to BookingItem. Forum (Thread/Post) with admin threads. GenericForeignKey patterns for attachable comments, likes, bookmarks. WordPress integration via `Reaction` (GraphQL-based reactions).

---

## Models

### Review
Product/service review. Linked to `BookingItem`.

**Fields:**
- `user` FK to `Account` (nullable — anonymous reviews allowed)
- `guest_email` — for anonymous reviews
- `booking_item` FK (nullable)
- `rating` — 1-5 stars
- `title`, `review_text` (RichText)
- `is_approved` — moderation flag
- `content_type` + `object_id` + `content_object` — GenericForeignKey (can attach to any model)
- `slug` — auto-generated unique

Anonymous reviews: `user=None`, `guest_email` required.

### Reaction
WordPress GraphQL integration. Stores WordPress post reactions.

**Fields:**
- `wordpress_post_id` — WordPress database ID from GraphQL
- `content_type` — currently only `blog_post` supported
- `user` FK
- `reaction_type` — like/love/laugh/wow/sad/angry

**Unique constraint:** `(wordpress_post_id, user)` — one reaction per user per post.

Indexes: `(wordpress_post_id)`, `(user, wordpress_post_id)`, `(content_type, wordpress_post_id)`.

### Thread
Forum thread. `category` FK, `creator` FK.

**Fields:**
- `title`, `slug` (auto-generated), `content`
- `is_admin_thread`, `is_pinned`
- GenericForeignKey (`content_type` + `object_id` + `content_object`) — attachable to any object
- GenericRelation to `Like`, `Bookmark`

### Post
Reply in a thread. `thread` FK, `user` FK.

**Fields:** `slug` (auto-generated), `content`. GenericRelation to `Like`, `Comment`.

### Comment
Generic comment on any object.

**Fields:** GenericForeignKey (`content_type` + `object_id` + `content_object`), `author` FK, `content`. GenericRelation to `Like`.

### Like
Generic like on any object.

**Fields:** GenericForeignKey, `user` FK. Unique: `(content_type, object_id, user)`.

### Bookmark
Generic bookmark on any object.

**Fields:** GenericForeignKey, `user` FK.

---

## GenericForeignKey Pattern

Several models use Django's `GenericForeignKey` to attach to any model:

```python
content_type = ForeignKey(ContentType)
object_id = PositiveIntegerField()
content_object = GenericForeignKey('content_type', 'object_id')
```

Attachable: `Comment`, `Thread`, `Like`, `Bookmark`.

---

## Related
- [[bookings]] (Review linked to BookingItem)
- [[accounts]] (User model)