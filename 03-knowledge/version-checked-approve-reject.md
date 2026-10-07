# Version-Checked Approve and Reject

## Summary
When staff act on rows a background writer (a bot) can still change, send each row's `updated_at` with the action and only act on rows whose version still matches. Approve is one UPDATE; delete needs a row lock first.

## Context
AI bot drafts station translations while staff review them in the Admin Dashboard. The bot may rewrite a draft after staff loaded the page and before they click Approve or Reject. Without a version check staff approve or delete text they never saw.

## Details
- Request body: `{items: [{id, updated_at}]}`, bounded (500 items, id 1..2^31-1). Server builds one `Q(id=…, updated_at=…)` OR-filter shared by approve and reject (`_unchanged_filter`).
- Approve: `queryset.filter(unchanged).update(...)`. The filter is part of the single UPDATE statement, so it is atomic. Response `{approved, skipped}`; stale rows are skipped and reappear in the list with the new text.
- **Delete is different.** `queryset.delete()` on a model with `post_delete` receivers collects rows first and then runs `DELETE … WHERE pk IN (ids)`. The version filter is NOT in that DELETE, so a bot write between the SELECT and the DELETE would be deleted unseen. Fix: inside `transaction.atomic()`, `select_for_update(of=('self',))` the matching rows, then delete exactly those pks. The bot's write waits on the row lock. Run the cache-flush helper once, outermost, not nested.
- Log each delete with user id and row ids, never the email.
- SQLite tests cannot prove row locking; test the logic (stale version skipped) and rely on Postgres for the lock.

## Related
[[bot-draft-then-human-approve-design]] · [[drf-put-bypass-vulnerability]]
