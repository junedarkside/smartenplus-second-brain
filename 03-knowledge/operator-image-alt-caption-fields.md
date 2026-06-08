# Operator Image Alt/Caption Fields

Schema, dialog UX, and grid alt chain for `OperatorImageGallery` metadata editing. Shipped #86 (`admin-dashboard` `71c2352` + `smartenplus-backend` `08b6593`).

## Schema

Two new nullable `CharField(max_length=250)` on `OperatorImageGallery` (`operators/models.py:559-561`):
- `alt_text` — HTML `alt` attribute for a11y/SEO
- `caption` — display caption shown alongside the image
- `description` — pre-existing longer-context field

Migration `operators/migrations/0058_operatorimagegallery_alt_text_and_more.py` adds both as nullable. No data migration needed; existing rows get `NULL`.

## Serializer

`OperatorImageGallerySerializer` (`operators/serializers.py:33`) lists both in `fields` and **NOT** in `read_only_fields`, so PATCH accepts them. No custom `update()` method, no `extra_kwargs`.

## Dialog UX

`pages/routemanagement/operators/images/ImageEditDialog.js`:
- 3 stacked `TextField`s: Alt text (rows 2), Description (rows 4), Caption (rows 2). Each `inputProps={{ maxLength: 250 }}`, each `fullWidth`.
- `useEffect` on `[open, editImage]` (NOT `operatorName` — prevents re-prefill on Autocomplete load):
  - Pre-fills `altText` from `editImage.alt_text` if present
  - Otherwise builds `<operatorName> - <filename-slug>` from the image URL
  - Filename slug: strip extension, replace `[-_]+` with spaces, strip non-alphanumeric
- Re-opens respect user-typed values (prefill only on first open of a new image).

## Grid Alt Chain

`pages/routemanagement/operators/images/index.js:263`:
```jsx
alt={item.alt_text || item.description || item.operator_name || ''}
```

Inside the dialog preview, same chain on the `next/image` `alt` prop (line 90).

## RTK Query Payload

`useUpdateOperatorImageMutation` (`store/api/operatorsApi.js:123`) uses spread — no slice change needed:
```js
updateImage({ id, alt_text: altText, description, caption })
```
`altText` (camelCase) is renamed to `alt_text` (snake_case) at the call site. Backend serializer reads `alt_text` directly off the model.

## Critical Gotcha

**DRF ModelSerializer silently drops unknown fields with 200 OK.** A PATCH body that sends `altText` (camelCase) instead of `alt_text` (snake_case) returns 200 but `alt_text` is never saved. Verified in #86: backend test with `altText: 'X'` returned `{alt_text: None, description: '...', caption: '...'}` with status 200. Any future 3rd-party integration that uses camelCase will silently fail. The frontend must always send snake_case in the PATCH body.

## Related

- [[admin-dashboard-image-pipeline]] — parent note (image identity, file validation, dropzone HEIC decode)
- [[django-soft-delete-s3-file-preserve]] — soft-delete invariant (orthogonal but same model)
- [[nextjs-hmr-cross-module-callback-staleness]] — debug artifact from this session
