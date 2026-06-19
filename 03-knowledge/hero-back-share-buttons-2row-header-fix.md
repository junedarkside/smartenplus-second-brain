Compressing directly since no file path was given — applying rules to the provided text inline.

# Hero Back/Share Buttons — 2-Row Header Problem & Fix

## Summary

Back/Share buttons on trip/activity detail hero images hidden behind 2-row fixed header. Multiple fix attempts. Root cause identified. Fix implemented, NOT yet verified in browser (server in production mode, not dev).

## Problem

2-row fixed header = 96px total (Row 1: 48px + Row 2: 48px). Hero uses `md:-mt-[96px]` for full-bleed behind header. Old back/share buttons at `absolute top-0 z-30` inside `FeaturedImageHeader` — placed at viewport y=0, under AppBar (z-1100). Invisible.

## Root Causes Found

### RC-1 — Wrong prop name
`FeaturedImageHeader` passed `shareUrl={shareUrl}` to `<ShareButton>` but `ShareButton` expects prop `url`. Fixed.

### RC-2 — Wrong containing block
`showActions` div was `absolute` inside `<header relative>` with no in-flow children (all `absolute`). Header height collapses → `absolute top-[96px]` renders in unexpected position. Fixed by moving inside inner image container.

### RC-3 — Dynamic loader prop chain breaks (ACTUAL ROOT CAUSE)
`TripDetailHero` receives `FeaturedImageHeader` as injected prop (page passes `DynamicFeaturedImageHeader`). When `TripDetailHero` calls `<FeaturedImageHeader showActions shareUrl={shareUrl}>`, prop passes through but DOM test confirmed: button NOT in DOM. Dynamic wrapper + prop injection chain silently drops `showActions` rendering.

**Proof:** `node -e` Playwright DOM check returned `Back btn in DOM: false` after file changes on disk.

### RC-4 — Server in production mode
Dev server is `next-server` (production), not `next dev`. HMR disabled. Source changes don't take effect. Must run `npm run dev`.

## Solution Implemented

Moved buttons OUT of `FeaturedImageHeader`. Render directly in outer wrapper `div` of `TripDetailHero` and `DayTripHero` — no dynamic loader chain.

**Architecture:**
```
<div className='relative flex flex-col gap-2'>     ← TripDetailHero outer wrapper
  {/* Buttons rendered HERE — no dynamic dependency */}
  <div className='absolute md:top-[96px] top-2 left-0 right-0 w-full z-30 pointer-events-none'>
    <div className='max-w-[1200px] mx-auto flex justify-between px-3 pointer-events-auto'>
      <button onClick={router.back()}>← Back</button>
      <ShareButton url={shareUrl} />
    </div>
  </div>
  <FeaturedImageHeader ...>...</FeaturedImageHeader>
</div>
```

**Why `md:top-[96px]` works:**
- Outer div starts at y=0 viewport (hero has `-mt-[96px]`, pulls whole column up)
- `absolute top-[96px]` inside = y=96px viewport = bottom edge of 2-row AppBar ✓
- `z-30` within div's stacking context — above hero image/gradient (z-auto), unrelated to AppBar z-1100

**Button style — glassmorphism pill:**
```
bg-white/90 backdrop-blur-md rounded-full px-4 py-2 shadow-md text-gray-800 text-sm font-medium hover:bg-white transition-all
```

## Files Changed (2026-05-30)

| File | Change |
|------|--------|
| `components/UI/FeaturedImageHeader.js` | Removed `showActions` + `shareUrl` props + block |
| `components/trips/detail/TripDetailHero.js` | Added `relative` wrapper + button row. Imports: `useRouter`, `ArrowBackIosNewOutlinedIcon`, `ShareButton` |
| `components/activities/detail/DayTripHero.js` | Same pattern. Uses `router.asPath` as shareUrl |
| `components/layout/main-header.js` | Row 2 `py-4` → `py-[10px]` on nav links + `!min-h-[48px]` on Row 2 Toolbar to enforce 96px total |
| `components/trips/detail/skeletons/FeaturedImageHeaderSkeleton.js` | Button zone shifted to `md:top-[96px]` |

## Verification Status

NOT verified in browser. Server running as `next-server` (production), not `npm run dev`. Lint passes. DOM test showed old code still served.

**To verify next session:**
1. `npm run dev` (not just start server)
2. Open `http://localhost:3000/trips/hatyai/koh-lipe`
3. Glassmorphism pill buttons: `← Back` left, Share right, below nav Row 2
4. Test `http://localhost:3000/activities/detail/[slug]` — same buttons
5. Test homepage — NO buttons (correct)

## Key Lesson

`DynamicFeaturedImageHeader` (Next.js dynamic) injected as prop into `TripDetailHero` = opaque chain. Props forwarded through dynamic wrappers can silently fail to trigger conditional renders in underlying component. Render page-level UI controls directly in calling component, not inside dynamically-loaded ones.

## Related

- [[header-redesign-2026-implementation]]
- [[mobile-header-analysis]]