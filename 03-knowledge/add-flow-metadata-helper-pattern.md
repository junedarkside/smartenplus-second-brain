---
name: add-flow-metadata-helper-pattern
description: When an "add" action crosses model boundaries (e.g. source gallery → selected set), helper must carry metadata fields verbatim. Destructuring to {id, image} silently drops alt_text/description/caption.
metadata:
  type: knowledge
---

# Add-flow metadata helper pattern

## Summary

When a helper adds an item from one model surface to another (OperatorImageGallery → ImageGallery), it must copy ALL metadata fields, not just `id` and `image`. Destructure-then-spread pattern silently drops everything not in destructure list.

## Context

Two image models in admin-dashboard: `OperatorImageGallery` (master gallery, has alt_text/description/caption) + `ImageGallery` (per-contract selected set, same fields). User clicks "Add" on gallery → image appears in contract's selected set. Initial helper:

```js
const handleAddClick = (e, imageData) => {
  const { id, image } = imageData;
  addImageIfUnique(images, { id, image });  // metadata dropped here
};
```

Selected image showed no alt text in contract form. User had to click into metadata dialog and retype it.

## Problem

**Destructure = whitelist.** Anything not in destructure list is lost. PR review can't catch this: both `{id, image}` destructure AND `{id, image, alt_text, description, caption}` destructure look identical at call site until you know the model has more fields.

## Details

Helper that handles uniqueness must carry metadata through. Update helper, not every call site:

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

Call site becomes simple:

```js
const handleAddClick = (e, imageData) => {
  e.preventDefault();
  const result = addImageIfUnique(imagesRef.current, imageData);  // pass whole item
  if (result.wasAdded) { ... }
};
```

## Decision

**Pass whole object, do destructure inside helper.** Helper knows what consumer model needs. Future fields added in ONE place. Applies to any "add from gallery to selection" / "add from list to cart" / "duplicate from template" flow.

## Tradeoffs

- Helper now coupled to consumer model's field shape. If two consumers need different field sets, parameterize carry list or split helper.
- `pickString` coercion defends against `null`/`undefined`/numbers sneaking through from half-typed response. Costs 1 line; saves "alt_text: undefined" downstream rendering bugs.

## Consequences

- Always pass full `imageData` to helper, not pre-destructured subset. Callers should not destructure before passing.
- For models with many carry fields, prefer explicit field list in helper over `...newImage` spread (spread risks picking up unwanted fields like `created_at`).
- Test add flow specifically: add image, verify all metadata fields present in dest model's state, not just `id` + `image`.

## Related

- [[image-metadata-formik-state-only-save]] — matching pattern for edit side
- [[admin-dashboard-image-pipeline]] — broader pipeline context
- Source: `admin-dashboard/components/utils/imageHelpers.js:16-49`
