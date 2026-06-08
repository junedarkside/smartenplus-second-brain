# Next.js HMR Cross-Module Callback Staleness

A Pages Router Fast Refresh edge case where a child component module is hot-replaced but the parent module's callback function stays stale. Discovered #86 while debugging the operator image alt/caption feature.

## Symptom

- Code looks correct end-to-end (source, compiled bundle, backend all verified)
- New behavior visible in UI (e.g., 3 form fields render) but only the OLD fields persist
- Hard refresh may or may not fix it; recompile + hard refresh eventually does
- Network tab shows PATCH body missing the new fields even though the React state has them
- 200 OK from backend, but `updated_at` doesn't reflect the new fields

## Mechanism

When you change two files in the same save (e.g., a dialog component AND its parent page that owns the `onSubmit` callback):
1. Fast Refresh replaces the **child** module's JSX → user sees new fields/behavior
2. Fast Refresh does **NOT** replace the **parent** module in some sessions → its function references stay old
3. New child calls `onSubmit({ new_field_a, new_field_b, ... })` with the new shape
4. Parent's OLD callback destructures only the OLD keys: `({ old_field_a, fileUpload })` → silently drops the new fields
5. PATCH body is sent with only old fields → backend saves only old fields
6. User concludes "new fields don't persist"

The dialog may have 3 inputs visible, but the PATCH payload is only 1 field because the parent's spread/destructure never saw the new keys.

## Detection (5-probe instrumentation pattern)

Add a unique-prefixed `console.log` at every step of the call chain. Prefix: `[DBG-NAME]` so cleanup = single grep.

1. **Bundle fingerprint** — log on page mount: confirms which compiled bundle the browser is running
2. **Dialog submit values** — log at `handleSubmit` top: shows what dialog sends upward
3. **Page callback received** — log at parent `handleDialogSubmit` top: shows what parent destructured
4. **RTK Query request** — log inside `query: (arg) => { ...; return req; }`: shows actual HTTP request shape
5. **Backend raw body** — `print(f"...{dict(request.data)}")` in `partial_update`: shows what Django parsed

The chain breaks at exactly one point: where the new keys disappear. That tells you which module is stale.

## Why hard refresh works (sometimes)

`Cache-Control: no-store, must-revalidate` is set on dev chunks, so the browser does fetch fresh. But Next.js dev server may need a full `.next` recompile after the second file change. If the user hard-refreshes BEFORE the parent module is recompiled, they get the stale parent. After the parent recompiles (a few seconds), the next hard-refresh gets fresh code. Mismatch in timing = intermittent hard-refresh success.

## Fix (one-time)

Ask the user to hard-refresh and **wait 5-10 seconds** for the dev server to recompile both files, then hard-refresh again.

## Prevention (architectural)

Move the mutation call INTO the dialog component. The dialog calls `useUpdateOperatorImageMutation` directly; the parent no longer needs an `onSubmit` callback. This eliminates the cross-module callback dependency entirely. Adds ~10 lines, removes the `onSubmit` indirection.

```js
// Before (parent owns callback):
// index.js
const [updateImage] = useUpdateOperatorImageMutation();
const handleDialogSubmit = async ({ altText, ... }) => updateImage({ ... });
<ImageEditDialog onSubmit={handleDialogSubmit} />

// After (dialog owns mutation):
// ImageEditDialog.js
const [updateImage] = useUpdateOperatorImageMutation();
const handleSubmit = () => updateImage({ ... });
// parent just renders <ImageEditDialog />
```

Worth doing if Fast Refresh keeps biting on other dialogs with parent-owned callbacks. Skip for one-off.

## When to Suspect

- Dialog/state change involves a parent `onSubmit` (or similar) callback that destructures specific arg keys
- Partial persistence of only the OLD keys
- Hard refresh sometimes fixes it, sometimes doesn't
- Source code + compiled bundle + backend all verified correct

## Related

- [[operator-image-alt-caption-fields]] — session where this was first observed
- [[admin-dashboard-image-pipeline]] — broader image system context
