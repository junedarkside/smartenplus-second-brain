# Translation Source Fingerprint (Out-of-Date Flag)

## Summary
Store a short hash of the English text a translation was written from. A translation is "needs update" when the parent's current hash differs. Self-healing: any full rewrite re-bases it, no signal fan-out.

## Context
Translations stay approved when the English description changes, so visitors can see text that no longer matches. Staff need a persistent flag, not a one-off warning in a dialog.

## Details
- `StationTranslation.source_hash` (16 hex chars of sha256 over NFC `name\ndescription`). Pure helper `english_fingerprint(name, description)` in its own module (importable by the data migration).
- `save()` stamps the current hash only on a FULL save (`update_fields is None`): bot, Django admin, CSV import. Status-only saves pass `update_fields` (send back to draft) and keep the old hash, so a stale translation stays flagged. `queryset.update()` paths (approve, rename un-review) never stamp.
- Unknown origin (`''`) is never flagged. Migration stamps existing rows with the current fingerprint (assumes they were current).
- Clearing: rewrite (bot/admin/CSV) or the staff "mark as up to date" endpoint (`.update(source_hash=…)`, so status and `updated_at` do not change).
- Read side: computed in the dashboard serializer from one prefetch (`to_attr`), no per-row query; shown only with `?include=translations`.
- Rename of the English name also un-reviews all translations (separate guard in `translation_signals.py`, exact compare, no trim); the AD warning must compare the same way.

## Tradeoffs
Alternative was a boolean set by a signal on every English change: simpler to explain but fans out writes and clears awkwardly.

## Related
[[bot-draft-then-human-approve-design]] · [[route-info-station-i18n-missing-context]]
