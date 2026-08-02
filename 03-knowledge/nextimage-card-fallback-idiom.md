# next/image card fallback idiom (reusable, don't fork)

**What:** The shared pattern for image-led cards that must survive null/missing image URLs without a blank or broken slot. Canonical source: `components/UI/PopularRouteImageCard.js:31-36,58`. Copied (not imported) into `StationCard` in `pages/airport-transfer/index.js` at #282.

**Why copy, not import:** `PopularRouteImageCard` is route-shaped (props, aria, labels bound to a route). Airport card is station-shaped. Importing would force prop-shape coupling / a shared abstraction "just in case" → over-engineering. The *idiom* is small enough to copy; the *component* is not reusable across shapes.

**The idiom:**
```jsx
const rawSrc = loc.image || bgDefault.src;        // bgDefault from helpers/constants (static import, has .src)
const [imgSrc, setImgSrc] = useState(rawSrc);
useEffect(() => { setImgSrc(loc.image || bgDefault.src); }, [loc.image]);  // re-sync when data changes
// ...
<Image
  src={imgSrc}
  fill
  sizes='(max-width: 639px) 100vw, (max-width: 767px) 50vw, (max-width: 1023px) 33vw, 25vw'
  className='object-cover group-hover:scale-105 transition-transform duration-300'
  placeholder='blur' blurDataURL={blurDataURL}   // shared base64 blur, quality={75}
  onError={() => setImgSrc(bgDefault.src)}        // runtime 404/broken → branded fallback
/>
```

**Three-layer safety:** (1) `|| bgDefault.src` at init handles null field, (2) `useEffect` re-sync handles data change after mount, (3) `onError` handles a URL that *exists* but 404s at runtime. All three needed — none is redundant.

**Gotcha that caused a crash (#282):** the payload field is a *shape trap*. `station.location_name` is a nested Location **object** (`{id, country, location_name, city, province, image}`), NOT a string. Passing it to `capitalizeWords` (which calls `.replace`) → `TypeError: string.replace is not a function`. Read `.city`/`.province` off the object; the image lives at `.image`. Verify field shape by curl before assuming string.

**Data reality (airport stations, #282):** `location_name.image` = null for ALL 4 airports (0 of 4). So the card renders the branded fallback on every card today, auto-upgrading as location images upload. Ship the image card anyway — fallback > text-only, and it's ready for photos. But the design spec must LEAD with the fallback state, not mockups of real photos.

**next.config remotePatterns must allow the image host** — S3 (`smartenplus-bucket.s3.amazonaws.com`, `smartenplus-wp-s3...`) + local `127.0.0.1` are already whitelisted where location images live.

Related: [[section-contentcard-wrapper-pattern]] · [[airport-transfer-at1-redesign-spec]]
