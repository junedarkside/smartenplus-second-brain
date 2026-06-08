---
name: add-flow-metadata-helper-pattern
description: When an "add" action crosses model boundaries (e.g. source gallery → selected set), the helper must carry metadata fields verbatim. Destructuring to {id, image} silently drops alt_text/description/caption.
metadata:
  type: knowledge
---

# Add-flow metadata helper pattern

## Summary

When a helper adds an item from one model surface to another (OperatorImageGallery → ImageGallery), it must copy ALL the metadata fields, not just `id` and `image`. The destructure-then-spread pattern silently drops everything not in the destructure list.

## Context

Two image models in admin-dashboard: `OperatorImageGallery` (master gallery, has alt_text/description/caption) and `ImageGallery` (per-contract selected set, same fields). User clicks "Add" on the gallery → image appears in the contract's selected set. Initial helper looked like:

```js
const handleAddClick = (e, imageData) => {
  const { id, image } = imageData;
  addImageIfUnique(images, { id, image });  // metadata dropped here
};
```

The selected image then showed no alt text in the contract form. User had to click into metadata dialog and retype it.

## Problem

**Destructure = whitelist.** Anything not in the destructure list is lost. Code reviewers can't catch this in PR review because both `{id, image}` destructure AND `{id, image, alt_text, description, caption}` destructure look identical at the call site until you know the model has more fields.

## Details

The helper that handles uniqueness must carry metadata through. Update the helper, not every call site:

```js
// imageHelpers.js
const pickString = (value) => (typeof value === 'string' ? value : undefined);

export const addImageIfUnique = (images, newImage) => {
  const isDuplicate = images.some(
    (img) => img.id === newImage.id || img.image === newImage.image
  );
  if (isDuplicate) return { updatedImages: images, wasAdded: false };

  const carried = {
    id: newImage.id,
    image: newImage.image,
    alt_text: pickString(newImage.alt_text) ?? '',
    description: pickString(newImage.description) ?? '',
    caption: pickString(newImage.caption) ?? '',
  };
  if (typeof newImage.order === 'number') carried.order = newImage.order;

  return { updatedImages: [...images, carried], wasAdded: true };
};
```

Then the call site becomes simple:

```js
const handleAddClick = (e, imageData) => {
  e.preventDefault();
  const result = addImageIfUnique(imagesRef.current, imageData);  // pass whole item
  if (result.wasAdded) { ... }
};
```

## Decision

**Pass the whole object, do the destructure inside the helper.** The helper knows what the consumer model needs. Future fields get added in ONE place. This applies to any "add from gallery to selection" / "add from list to cart" / "duplicate from template" flow.

## Tradeoffs

- The helper is now coupled to the consumer model's field shape. If two consumers need different field sets, parameterize the carry list or split the helper.
- `pickString` coercion defends against `null`/`undefined`/numbers sneaking through from a half-typed response. Costs 1 line; saves "alt_text: undefined" downstream rendering bugs.

## Consequences

- Always pass the full `imageData` to the helper, not a pre-destructured subset. Callers should not destructure before passing.
- For models with many carry fields, prefer an explicit field list in the helper over `...newImage` spread (spread risks picking up unwanted fields like `created_at`).
- Test the add flow specifically: add image, verify all metadata fields are present in the dest model's state, not just `id` and `image`.

## Related

- [[image-metadata-formik-state-only-save]] — matching pattern for the edit side
- [[admin-dashboard-image-pipeline]] — broader pipeline context
- Source: `admin-dashboard/components/utils/imageHelpers.js:16-49`
