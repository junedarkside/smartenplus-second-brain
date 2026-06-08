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

## Operator Gallery Image Normalization (2026-06-08)

`/routemanagement/operators/images?query=<slug>` upload path now normalizes every file server-side to WebP ≤100KB before hashing/storing.

- `operators/utils.py:process_operator_image` — mirrors `dialogue.utils.process_review_image` (120KB target). 100KB here, broader allowlist (jpg/jpeg/png/webp/gif/heic/heif/avif).
- `operators/views.py:OperatorImageGalleryViewSet.create` — calls `process_operator_image` immediately after `_validate_upload_file`. All subsequent hashing (MD5 + SHA-256), dedup (per-operator + Asset), and storage operate on the processed WebP bytes. Result: identical visual content dedups across formats (HEIC + JPEG of same photo = one Asset row).
- `_UPLOAD_ALLOWED_EXTENSIONS` adds `'heif'`.
- `pillow-heif` opener is already registered globally via `dialogue/apps.py:ready`.
- Frontend: `DropFilesInput` now accepts an optional `accept` prop (default `image/*`); `ImageEditDialog.js` passes `accept="image/*,.heic,.heif"` so iOS Safari offers HEIC in the file picker.
- Out of scope (deliberately): contract-create `ImageSelection`, `placeEdit`, `OperatorForm` logo, hero banner. Their uploads also get normalized transparently (server-side, same endpoint), but no client changes were made.

## Dropzone HEIC Client-Side Decode (2026-06-08)

Server-side conversion handles the *uploaded* image, but the local pre-upload
thumbnail still needs a real bitmap. Chrome/Firefox/Edge cannot decode HEIC
in `<img>` (HEVC license issue). `smartenplus-frontend/components/RateAndReview`
solves this with `heic2any`; admin-dashboard mirrors that pattern.

- `heic2any@^0.0.4` installed in `package.json`. Dynamic `import()` inside
  the event handler → lazy load, only fetched when a HEIC file is selected.
- `components/Images/DropFilesInput.js` — new `isHeic(file)` and
  `convertHeicToJpeg(file)` helpers. `onDrop` + `onFileDrop` are async,
  `Promise.all(valid.map(convertHeicToJpeg))` decodes in parallel, the
  original HEIC `File` is replaced with a new `File` containing JPEG bytes
  + `.jpg` extension. The `fileList` then contains only decodable formats.
- The HEIC `File.lastModified` differs from the JPEG's, so the `key` in
  the fileList map (`file.name + file.lastModified`) is unique per File.
- Native `<img>` renders JPEG in all browsers. No `onError` fallback, no
  `BrokenImageIcon` — the previous Part 2a/2b approach (broken-glyph detection
  + icon) was unreliable; `onError` for HEIC blob URLs may not fire on
  Chrome/Firefox/Edge.
- Side effect (positive): `DropFilesInput` shared with `ImageSelection`
  (contract create) + `placeEdit` (place edit). Both get HEIC preview for free.
- `heic2any` works with Next.js 14 + Webpack 5 out of the box. No
  `transpilePackages` change needed (smartenplus-frontend also doesn't add it).

## Dropzone HEIC Loading State (2026-06-08)

Big iPhone HEIC files take 1-3s to decode via heic2any. Without
feedback, users see nothing during that window.

- `components/Images/DropFilesInput.js` — `loadingKeys` Set tracks
  files currently being decoded. Render `CircularProgress` (size 24
  desktop / 20 mobile) in the 50x50 (40x40 mobile) thumbnail box
  while a file's key is in the set. On decode complete, replace the
  HEIC File in `fileList` in place (same index) with the JPEG File
  and remove the key from `loadingKeys`. Filename + size render
  immediately (no async dependency).
- `addFiles(valid)` shared by `onDrop` and `onFileDrop` — adds all
  valid files to `fileList` immediately, kicks off HEIC decode in
  background per file, replaces in place on success or surfaces
  `onValidationError` + removes on failure.
- Non-HEIC files never enter `loadingKeys` — no spinner flash for
  jpg/png/webp users. `CircularProgress` is theme-aware (text.primary
  in light/dark mode) and already in the MUI bundle.
- Corrupt HEIC handling: on `heic2any` throw, call
  `onValidationError("Failed to decode <name>: file removed.")` and
  filter the file out of `fileList`. Other files unaffected.
- External API (`onFileChange` File[]) unchanged. No new deps.

## Related
- [[operators]]
- [[admin-dashboard-contracts]]
- [[operator-image-soft-delete-cascade-gap]] — soft-delete does NOT cascade to contract `ImageGallery` rows (shared URL string, no FK)