# Dialogue — Social & Community

## Summary
Social/community layer. Review system linked to BookingItem. Forum (Thread/Post) with admin threads. GenericForeignKey patterns for comments, likes, bookmarks. WordPress integration via `Reaction`.

## Models

### Review
Product/service review linked to `BookingItem`.
- `user` FK (nullable — anonymous reviews), `guest_email` (for anonymous)
- `booking_item` FK (nullable), `rating` (1-5), `title`, `review_text` (RichText)
- `is_approved`, `content_type` + `object_id` + GenericForeignKey, `slug`

### Reaction
WordPress GraphQL integration. `wordpress_post_id`, `content_type` (currently `blog_post` only), `user` FK, `reaction_type` (like/love/laugh/wow/sad/angry). Unique: `(wordpress_post_id, user)`.

### Thread
Forum thread. `category` FK, `creator` FK, `title`, `slug`, `content`, `is_admin_thread`, `is_pinned`. GenericForeignKey + GenericRelation to `Like`, `Bookmark`.

### Post
Reply in thread. `thread` FK, `user` FK, `slug`, `content`. GenericRelation to `Like`, `Comment`.

### Comment
Generic comment. GenericForeignKey, `author` FK, `content`. GenericRelation to `Like`.

### Like
Generic like. GenericForeignKey, `user` FK. Unique: `(content_type, object_id, user)`.

### Bookmark
Generic bookmark. GenericForeignKey, `user` FK.

## GenericForeignKey Pattern

```python
content_type = ForeignKey(ContentType)
object_id = PositiveIntegerField()
content_object = GenericForeignKey('content_type', 'object_id')
```

Attachable: `Comment`, `Thread`, `Like`, `Bookmark`.

## Related
- [[bookings]]
- [[accounts]]
