# Admin Dashboard — Image Pipeline

Frontend image state management, error reset hooks, dedup helpers.

## Image Identity Model

Two models, different IDs, same image URL:
- **OperatorImageGallery** — operator gallery (source of truth for path)
- **ImageGallery** — contract image records (copies path)

After contract save, IDs change OperatorImageGallery → ImageGallery. Dedup checks both ID + URL.

## Image Helpers (`components/utils/imageHelpers.js`)

```javascript
isDuplicateImage(images, id, url) // ID + normalized URL fallback. Cross-model dedup.
addImageIfUnique(images, newImage) // uses isDuplicateImage. Prevents double-add after save.
removeImageById(images, id)        // ID only. Correct for delete (targets specific row).
```

## ImageCard Error Reset

`ImageCard.js` + `DraggableImageCard.js` — `imageError` resets via `useEffect`:
```javascript
// ImageCard
useEffect(() => { setImageError(false) }, [src])
// DraggableImageCard
useEffect(() => { setImageError(false) }, [imageItem.image])
```
Do NOT remove — permanent grey-box if missing.

## Image Flow (Contracts)

```
Formik imageSelection [{id, image}]
  → ImageSelection → ProductImages (grid) + OperatorImages (gallery)
  → transformContractFormValues: imageSelection unchanged
  → Backend: reads imageSelection → creates/updates ImageGallery records
  → Response: image_gallery (read-only, from imagegallery_set)
  → useContractFormData: data?.image_gallery → Formik imageSelection
```

## File Upload Validation

Backend: ext whitelist + 10MB max. Client mirrors.
- `DropFilesInput.js` — 10MB filter on `onDrop` + `onFileDrop`. `onValidationError` prop surfaces rejected filenames.
- `OperatorForm.js` — `handleFileChange` validates type (`jpg/png/gif/webp`) + 10MB via `formik.setFieldError`.
- `ImageSelection.js` + `OperatorImageGallery/index.js` — pass `onValidationError` to alert.

## Related
- [[operators]]
- [[admin-dashboard-contracts]]