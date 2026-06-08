---
name: image-metadata-formik-state-only-save
description: Image/dialog metadata edits ride along with parent form's existing Save button via Formik setFieldValue. No separate mutation endpoint, no separate save button, no extra notify wiring.
metadata:
  type: knowledge
---

# Image metadata — Formik-state-only save

## Summary

When a sub-component's edits (e.g. image metadata dialog) should be persisted by parent form's existing Save button, write to Formik state on confirm. Parent's `setFieldValue` is the contract; no new mutation endpoint, no new save button, no extra notify wiring.

## Context

Two image surfaces in admin-dashboard: OperatorImages (gallery) + ProductImages (per-contract selected set). User edits metadata (alt_text, description, caption) on a selected image. Contract Save button already exists. Adding "Save metadata" button to dialog = two save paths + ordering conflicts.

## Problem

- New mutation endpoint for per-image save: new URL, new state, new error handling, new race against contract save. Overkill.
- Separate save button in dialog: two save paths, user confusion ("which one do I click?"), stale state on race.
- Local component state only: edits vanish on parent re-render.

## Details

Wire dialog as controlled Formik consumer:

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
  onSubmit={handleMetadataUpdate}  // no readOnly — dialog becomes form
/>
```

`transformContractFormValues` already passes `imageSelection` through to backend payload verbatim. Contract Save → backend → response → re-seed Formik → one loop.

## Decision

**Reuse parent form's save flow.** Dialog job: gather edit, write to Formik, show snackbar, close. Persistence is parent's job. Same pattern as any other Formik field — image metadata is just a nested field array.

## Tradeoffs

- Snackbar says "Image metadata updated" but data not in DB until user clicks contract Save. Technically correct (Formik state IS updated) but may confuse users who close tab without saving. Tradeoff accepted — alternative = more code for marginal UX win.
- If parent form has validation that rejects new image metadata, dialog edit silently rolled back. Rare (image fields loose) but possible. Document in dialog's contract.

## Consequences

- Zero new endpoints, zero new save buttons, zero new state. Reuses `useAlert` provider (snackbar), `setFieldValue` (state), parent Save (persistence).
- Backend must read all metadata fields from request payload, not just rely on FK lookups. See [[django-partial-update-elif-metadata-drop]] for matching backend invariant.
- For dialogs that DO need immediate persistence (e.g. confirmation that can't be undone), this pattern doesn't fit. Use a direct mutation then.

## Related

- [[add-flow-metadata-helper-pattern]] — matching helper for other side (gallery → selected)
- [[django-partial-update-elif-metadata-drop]] — backend invariant that makes this work
- [[nextjs-hmr-cross-module-callback-staleness]] — gotcha when dialogs go through parent onSubmit
- Source: `admin-dashboard/components/Images/ProductImages.js:65-76`
