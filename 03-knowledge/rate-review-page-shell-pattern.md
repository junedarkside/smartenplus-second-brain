# Rate-Review Page Shell Pattern

**Date:** 2026-06-06
**Context:** All rate-review pages must match platform visual language (blog/trips).

## Standard Shell Structure

```jsx
<div className="w-full flex flex-col gap-2">
  <NextSeo {...seo} />

  {/* Hero */}
  <div className="relative">
    {/* Floating nav — matches BlogPageWrapper exactly */}
    <div className="absolute top-2 left-0 right-0 w-full z-40 pointer-events-none">
      <div className="max-w-[1200px] mx-auto flex flex-row justify-between items-center px-3 pointer-events-auto">
        <button
          onClick={() => router.back()}  // or router.push('/rate-review')
          className="flex items-center justify-center w-9 h-9 bg-white/80 backdrop-blur-md rounded-full shadow-md text-gray-800 hover:bg-white transition-all"
          aria-label="Go back"
        >
          <ArrowBackIosNewOutlinedIcon style={{ fontSize: 18 }} />
        </button>
        <ShareButton />
      </div>
    </div>
    <FeaturedImageHeader title="..." imgUrl={bgDefault}>
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full z-20">
        <div className="max-w-[1200px] mx-auto text-center px-4">
          <h1 className="text-gray-50 text-2xl md:text-4xl lg:text-5xl font-bold mb-2">...</h1>
        </div>
      </div>
    </FeaturedImageHeader>
  </div>

  {/* Breadcrumb */}
  <div className="max-w-[1200px] mx-auto w-full px-2 md:px-3">
    <DynamicStandardBreadcrumb lastBreadcrumb="..." />
  </div>

  {/* Content */}
  <div className="max-w-[1200px] mx-auto w-full px-2 md:px-3 pb-8">
    {/* page content */}
  </div>
</div>
```

## Key Rules

- **Root element:** `<div className="w-full flex flex-col gap-2">` — NOT `<section>`
- **Back button:** floating `w-9 h-9 bg-white/80 backdrop-blur-md rounded-full` — NOT MUI `IconButton`
- **Back icon:** `ArrowBackIosNewOutlinedIcon` (same as blog/trips) — NOT `ArrowBackIosOutlinedIcon`
- **H1:** overlaid on hero, `text-gray-50 font-bold` — NOT inside content area
- **Breadcrumb:** `px-2 md:px-3` below hero
- **Content:** `px-2 md:px-3 pb-8` (list pages) or `px-4 pb-8` (detail/form pages)

## Anti-Patterns (wrong)

```jsx
// WRONG — old pattern
<section className='w-full mx-auto'>
  <div className="pt-4">
    <Tooltip title="...">
      <IconButton sx={{ color: COLORS.brand.primary }}>
        <ArrowBackIosOutlinedIcon />
      </IconButton>
    </Tooltip>
  </div>
  <h1 className="text-gray-800 text-xl font-bold text-center pt-2">...</h1>
</section>
```

## Which pages use this pattern

- `pages/rate-review/index.js`
- `pages/rate-review/[reviewSlug].js`
- `pages/rate-review/submit-review/[...slug].js`
- `pages/blog/index.js` (via `BlogPageWrapper`)
- `pages/trips/index.js` (manual implementation)
