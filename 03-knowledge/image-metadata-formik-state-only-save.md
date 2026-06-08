---
name: image-metadata-formik-state-only-save
description: Image/dialog metadata edits ride along with parent form's existing Save button via Formik setFieldValue. No separate mutation endpoint, no separate save button, no extra notify wiring.
metadata:
  type: knowledge
---

# Image metadata — Formik-state-only save

## Summary

When a sub-component's edits (e.g. image metadata dialog) should be persisted by the parent form's existing Save button, write to Formik state on confirm. The parent's `setFieldValue` is the contract; no new mutation endpoint, no new save button, no extra notify wiring.

## Context

Two image surfaces in admin-dashboard: OperatorImages (gallery) and ProductImages (per-contract selected set). User wants to edit metadata (alt_text, description, caption) on a selected image. There's already a contract Save button. Adding a "Save metadata" button to the dialog would create two save paths + need to handle ordering conflicts.

## Problem

- New mutation endpoint for per-image save: new URL, new state, new error handling, new race against contract save. Overkill.
- Separate save button in dialog: two save paths, user confusion ("which one do I click?"), stale state on race.
- Local component state only: edits vanish on parent re-render.

## Details

Wire the dialog as a controlled Formik consumer:

```jsx
const handleMetadataUpdate = ({ altText, description, caption }) => {
  const updatedImages = dataImages.map((img) =>
    img.id === detailsImage.id
      ? { ...img, alt_text: altText, description, caption }
      : img
  );
  setImages(updatedImages);                    // local component state
  form.setFieldValue(name, updatedImages);     // Formik field
  showAlert('Image metadata updated', 'success');  // provider snackbar
  handleCloseDetails();
};

// In JSX:
<ImageMetadataDialog
  isEditMode
  isSubmitting={false}
  onSubmit={handleMetadataUpdate}  // no readOnly flag — dialog becomes form
/>
```

`transformContractFormValues` already passes `imageSelection` through to the backend payload verbatim. Contract Save → backend → response → re-seed Formik → all in one loop.

## Decision

**Reuse the parent form's save flow.** The dialog's job is: gather edit, write to Formik, show snackbar, close. Persistence is the parent's job. This is the same pattern as any other Formik field — image metadata is just a nested field array.

## Tradeoffs

- Snackbars say "Image metadata updated" but the data isn't in the DB until user clicks contract Save. Technically correct (Formik state IS updated) but might confuse users who close the tab without saving. Tradeoff accepted — alternative is more code for marginal UX win.
- If the parent form has validation that rejects the new image metadata, the dialog edit is silently rolled back. This is rare (image fields are loose) but possible. Document in the dialog's contract.

## Consequences

- Zero new endpoints, zero new save buttons, zero new state. Reuses `useAlert` provider (snackbar), `setFieldValue` (state), parent Save (persistence).
- The backend must read all metadata fields from the request payload, not just rely on FK lookups. See [[django-partial-update-elif-metadata-drop]] for the matching backend invariant.
- For dialogs that DO need immediate persistence (e.g. confirmation that can't be undone), this pattern doesn't fit. Use a direct mutation then.

## Related

- [[add-flow-metadata-helper-pattern]] — matching helper for the other side (gallery → selected)
- [[django-partial-update-elif-metadata-drop]] — backend invariant that makes this work
- [[nextjs-hmr-cross-module-callback-staleness]] — gotcha when dialogs go through parent onSubmit
- Source: `admin-dashboard/components/Images/ProductImages.js:65-76`
