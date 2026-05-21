# Admin Dashboard — Image Pipeline

Frontend image state management, error reset hooks, dedup helpers.

## Image Identity Model

Two models, different IDs, same image URL:
- **OperatorImageGallery** — operator gallery (source of truth for path)
- **ImageGallery** — contract image records (copies path from operator gallery)

After contract save, IDs change from OperatorImageGallery → ImageGallery. Dedup checks both ID and URL.

## Image Helpers (`components/utils/imageHelpers.js`)

```javascript
isDuplicateImage(images, id, url) // ID + normalized URL fallback. Cross-model dedup.
addImageIfUnique(images, newImage) // uses isDuplicateImage. Prevents double-add after save.
removeImageById(images, id)        // ID only. Correct for delete (targets specific row).
```

## ImageCard Error Reset

`ImageCard.js` and `DraggableImageCard.js` — `imageError` resets via `useEffect`:

```javascript
// ImageCard
useEffect(() => { setImageError(false) }, [src])

// DraggableImageCard
useEffect(() => { setImageError(false) }, [imageItem.image])
```

Do NOT remove these — permanent grey-box if missing.

## Image Flow (Contracts)

```
Formik imageSelection [{id, image}]
  → ImageSelection (container)
    → ProductImages (selected grid — drag reorder, delete, preview)
    → OperatorImages (gallery — add to selection, preview)
  → transformContractFormValues: imageSelection passes through unchanged
  → Backend update: reads imageSelection from request data
    → creates/updates ImageGallery records per {id, image, order}
  → Response: image_gallery (read-only, from imagegallery_set)
  → useContractFormData: data?.image_gallery → Formik imageSelection
```

## File Upload Validation

Backend enforces: ext whitelist + 10MB max. Client mirrors this.

- `DropFilesInput.js` — 10MB filter on both `onDrop` + `onFileDrop`. Pass `onValidationError` prop to surface rejected filenames.
- `OperatorForm.js` — `handleFileChange` validates type (`jpg/png/gif/webp`) + 10MB via `formik.setFieldError`.
- `ImageSelection.js` + `OperatorImageGallery/index.js` — pass `onValidationError={(msg) => showAlert(msg, 'warning')}` to `DropFilesInput`/`ImageEditDialog`.

## Related

- [[operators]] — Operator model, image gallery
- [[admin-dashboard-contracts]] — Contract image flow