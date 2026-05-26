# Hero Alignment Audit — Homepage vs Other Pages

## Homepage Hero (current state after changes)

**File:** `pages/homepagev2.js` (lines ~388-411)

```jsx
<FeaturedImageHeader
  title="SmartEnPlus Booking Center"
  imgUrl={heroBannerImage || bgDefault}
>
  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full z-20">
    <section className="w-full mx-auto z-10">
      <div className="max-w-[1200px] mx-auto">
        <header className="flex flex-col gap-2">
          <h1 className="text-gray-50 text-center text-lg md:text-2xl lg:text-3xl font-bold mx-2">
            {seoData.title}
          </h1>
          <p className="text-gray-200 text-center text-xs md:text-sm lg:text-base mx-2 leading-snug">
            Book buses, ferries and trains across Thailand — instantly confirmed.
          </p>
        </header>

        <section className="bg-white mx-2 md:mx-3 p-2 rounded sm:rounded-lg flex flex-col gap-2 min-h-[300px] md:min-h-[104px] md:h-[104px]">
          <DynamicProductSearchForm onSearch={handleFindTrips} errors={searchErrors} />
        </section>
      </div>
    </section>
  </div>
  <ScrollIndicator />
</FeaturedImageHeader>
```

**FeaturedImageHeader usage:**
- `title` — set
- `imgUrl` — heroBannerImage || bgDefault
- `children` — content div (no `pt-[88px]`)
- `isCinematic` — NOT passed (default false)
- `customMinHeight` — NOT passed (uses default min-h)

**H1:** `text-lg md:text-2xl lg:text-3xl font-bold` — same as other pages

**Content structure:** header (h1 + subtitle p) + section (search form)

---

## Destinations Hero

**File:** `pages/destinations/index.js` (lines ~82-103)

```jsx
<FeaturedImageHeader title={`Thailand All Destinations`} imgUrl={bgDefault}>
  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full z-20 pt-[88px]">
    <section className="w-full mx-auto z-10">
      <div className="max-w-[1200px] mx-auto flex flex-col gap-4 px-4">
        <h1 className='text-gray-50 text-lg md:text-2xl lg:text-3xl font-bold text-center'>
          Thailand All Destinations
        </h1>

        <SearchBar ... />

        <StatsDisplay ... />
      </div>
    </section>
  </div>
</FeaturedImageHeader>
```

**FeaturedImageHeader usage:**
- `title` — set
- `imgUrl` — bgDefault
- `children` — content div WITH `pt-[88px]`
- `isCinematic` — NOT passed (default false)
- `customMinHeight` — NOT passed (uses default min-h)

**H1:** `text-lg md:text-2xl lg:text-3xl font-bold` — same as homepage

---

## Trips Hero

**File:** `pages/trips/index.js` (lines ~509-524)

```jsx
<FeaturedImageHeader
  title="Explore Thailand's Travel Routes"
  imgUrl={bgDefault}
>
  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full z-20 pt-[88px]">
    <section className="w-full mx-auto z-10">
      <div className="max-w-[1200px] mx-auto">
        <div className='flex flex-col gap-2'>
          <h1 className='text-gray-50 text-lg md:text-2xl lg:text-3xl font-bold text-center'>{h1PageTitle}</h1>
        </div>
      </div>
    </section>
  </div>
</FeaturedImageHeader>
```

**FeaturedImageHeader usage:**
- `title` — set
- `imgUrl` — bgDefault
- `children` — content div WITH `pt-[88px]`
- `isCinematic` — NOT passed (default false)
- `customMinHeight` — NOT passed (uses default min-h)

**H1:** `text-lg md:text-2xl lg:text-3xl font-bold` — same as homepage

---

## FeaturedImageHeader Component (for reference)

**File:** `components/UI/FeaturedImageHeader.js`

**Props accepted:** `title`, `imgUrl`, `children`, `actionButton`, `customMinHeight`, `blogTitle`, `onImageLoad`, `onImageError`, `imageLoaded`, `isCinematic`

**Container:**
- Default min-height: `min-h-[200px] sm:min-h-[250px] md:min-h-[460px]`
- `customMinHeight` overrides if provided
- `isCinematic` removes internal bounds (uses `inset-0`)

**Image:** Uses `fill` + `objectFit: cover` via MemoizedImage

**Background:** ColorThief color extraction (cached) with fallback `rgb(156, 163, 175)` — no hardcoded ColorThief dependency

---

## Side-by-Side Comparison

| Aspect | Homepage | Destinations | Trips |
|--------|----------|--------------|-------|
| `pt-[88px]` in child div | NO | YES | YES |
| `isCinematic` passed | NO | NO | NO |
| `customMinHeight` passed | NO | NO | NO |
| H1 size | `text-lg md:text-2xl lg:text-3xl` | Same | Same |
| Search form present | YES (ProductSearchForm) | YES (SearchBar + StatsDisplay) | NO |
| ScrollIndicator | YES | NO | NO |
| Background color | ColorThief (dynamic) | ColorThief (dynamic) | ColorThief (dynamic) |
| has subtitle p tag | YES | NO | NO |

---

## What Needs to Change to Match Homepage

### Destinations Hero
1. **Remove `pt-[88px]`** from child div (line 83) — homepage hero does NOT have this padding
2. **Optional:** Add subtitle paragraph matching homepage tone (for consistency)
3. **Optional:** Add `ScrollIndicator` if desired (homepage has it)

### Trips Hero
1. **Remove `pt-[88px]`** from child div (line 515) — homepage hero does NOT have this padding
2. **Optional:** Add subtitle paragraph for consistency with homepage messaging
3. **Optional:** Add `ScrollIndicator` if desired