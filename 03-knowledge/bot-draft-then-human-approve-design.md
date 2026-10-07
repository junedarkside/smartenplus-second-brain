# Bot Writes Drafts, Humans Approve

## Summary
An external AI bot may only create unreviewed drafts; visitors never see them until staff approve. Reusable shape for any AI-written public text.

## Context
Station names/descriptions in other languages are written by a bot and shown on the public site. Mistakes must never go live unseen.

## Details
- Forced server side on every bot write: `is_reviewed=False`, `source='bot'`, `updated_by=user`. The bot cannot set them. Account flag `is_station_info_agent` (never `is_staff`, or it could approve itself); throttle scope (200/hour).
- Upsert on the natural key (station, language): POST creates (201) or updates a draft (200); an approved row returns 409 so the bot cannot pull live text. `en` is rejected: the live English text is human-owned and an English translation row is never served anyway.
- HTML cleaned on write with the same bleach allowlist as the CSV import (`clean_field`).
- Review: AD page lists pending bot drafts with the English beside them; approve (version-checked), reject (delete draft, bot can post again), send back to draft, mark as up to date. Notification = sidebar badge from a summary count (no email, no Celery).
- Read side serves a translation only when `is_reviewed=True`; otherwise English (fallback in the serializer mixin).
- Known gaps: bot may re-post a rejected draft; English HTML is not bleached on the BE (visitor FE cleans on render; FE rendered English raw until this work).

## Related
[[version-checked-approve-reject]] · [[translation-source-fingerprint-staleness]] · [[i18n-catalog-with-staff-overrides-pattern]]
