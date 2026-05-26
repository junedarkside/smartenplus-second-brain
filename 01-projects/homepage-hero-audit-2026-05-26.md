# Homepage Hero Section Audit — 2026-05-26

**Team:** design-review + ux-research-specialist + frontend-design-enhanced
**Scope:** Homepage vs all other page heroes

---

## Pages with Hero Sections

| Page | Component | Cinematic | Min-Height | Search in Hero |
|------|-----------|-----------|------------|----------------|
| Homepage v2 | `FeaturedImageHeader` | Yes | `min-h-screen` | Yes (embedded) |
| Homepage v1 | `FeaturedImageHeader` | No | `min-h-[460px]` | Yes (embedded) |
| Destinations | `FeaturedImageHeader` | No | `md:min-h-[460px]` | Yes (SearchBar) |
| Blog Index | `FeaturedImageHeader` | No | `md:min-h-[460px]` | Yes (WP Search) |
| Blog Post | `FeaturedImageHeader` (dynamic) | No | `md:min-h-[460px]` | No |
| Trip Detail | `FeaturedImageHeader` | No | `md:min-h-[460px]` | No |
| Activities Detail | `FeaturedImageHeader` | No | `md:min-h-[460px]` | No |
| Search Results | `FeaturedImageHeader` | No | `md:min-h-[460px]` | No |
| Trips Index | `FeaturedImageHeader` | No | `md:min-h-[460px]` | No |
| Airport Transfers | `FeaturedImageHeader` | No | `md:min-h-[460px]` | No |
| **Activities Browse** | **None** | N/A | None | No |
| **Trip Detail (by ID)** | **None** | N/A | None | No |

---

## Critical Issues Found

### P0 — Breaks Visual Pattern

**1. Activities Browse has zero hero**
- Plain MUI Typography header, no image, no gradient
- Only major page without `FeaturedImageHeader`
- Feels like a utility tool, not a travel platform
- Compare: GetYourGuide/Airbnb always lead with imagery

**2. Trip Detail (`/trips/[tripId].js`) has no hero**
- `pages/trips/[tripId].js` has no `FeaturedImageHeader` at all
- Only relies on NextSEO — no visual header
- Same problem as Activities Browse

### P1 — Inconsistent Scale

**3. Homepage uses `min-h-screen`; every other page uses `md:min-h-[460px]`**
- Homepage is full-viewport; all sub-pages collapse to 460px
- Jarring visual drop when navigating from homepage to any inner page
- Homepage v1 already uses `min-h-[460px]` — v2 introduced the cinematic mode

**4. `isCinematic` creates asymmetric behavior**
- Homepage: hides back button, uses `inset-0` layout, `hero-top-gradient` applied
- Other pages: back button visible, standard layout
- Cinematic mode is homepage-only — no other page uses it

**5. Blog H1 is `text-5xl`; all others use `text-3xl`**
- Blog is 67% larger than homepage
- Trip Detail uses `font-semibold` vs `font-bold` everywhere else

**6. Trip Detail has no hero CTA**
- All other browse pages have search or action in hero
- Trip Detail hero is purely informational

### P2 — Technical Inconsistencies

**7. Image optimization varies per page**
- Homepage: `getOptimizedImageSizes`, `getOptimalImageQuality`, `placeholder="blur"`, `priority`
- Other pages: basic `fill` + `priority` only
- ColorThief dynamic gradient: homepage only

**8. No consistent CTA treatment**
- Homepage: white rounded panel form
- Destinations: MUI SearchBar
- Blog: WordPress Search
- Trip Detail: nothing

---

## What Homepage Gets Right

- Search embedded directly in hero — users can search immediately on arrival
- Banner rotation creates visual interest (though adds complexity)
- Trust indicators below fold (ratings section) — but NOT in hero itself
- 2026 research doc recommends compact 45-60vh hero — homepage at `min-h-screen` is taller than recommended

---

## Should Homepage Hero Be Redesigned to Match Other Pages?

**Answer: No — but both need to converge toward the 2026 direction.**

The 2026 UX/UI Redesign Research doc says:
- Hero height: **45-60vh recommended**, NOT fullscreen
- Remove oversized cinematic dominance, add operational clarity
- Calm premium minimalism — less visual noise

**Homepage problems (per 2026 direction):**
- `min-h-screen` is too tall — should be 55vh max
- Rotating banners add complexity without proportional UX gain
- No trust signals in hero
- Cinematic mode is 2019-era pattern

**Other pages problems (per 2026 direction):**
- Activities Browse: no hero at all — jarring vs all other pages
- Trip Detail: no hero at all
- Inconsistent H1 weights and sizes
- No hero CTA on Trip Detail

**Recommended convergence:**
1. **Homepage** — reduce hero to 55-60vh, remove banner rotation, add trust badge, keep embedded search
2. **Activities Browse + Trip Detail** — add `FeaturedImageHeader` with compact hero
3. **All pages** — standardize `font-bold` and `text-3xl` for H1

---

## Priority Actions

| Priority | Action | Pages Affected |
|----------|--------|----------------|
| P0 | Add `FeaturedImageHeader` hero | Activities Browse, Trip Detail |
| P1 | Reduce homepage hero height to 55-60vh | Homepage |
| P1 | Standardize H1: `text-3xl font-bold` everywhere | Blog, Trip Detail |
| P1 | Remove `isCinematic` or document it as brand choice | Homepage |
| P2 | Add search CTA to Trip Detail hero | Trip Detail |
| P2 | Unify CTA treatment (white panel or SearchBar) | All hero pages |
| P3 | Lock blog hero to branded image | Blog |
| P3 | Add trust rating to homepage hero | Homepage |

---

## Related Vault Docs

- `smartenplus-uxui-redesign-research-2026.md` — 2026 redesign direction
- `homepage-ux-review-2026-05-21.md` — prior homepage audit
- `trip-detail-uxui-audit-2026-05-22.md` — trip detail audit
- `nav-header-redesign-2026-05-24.md` — header/nav alignment
