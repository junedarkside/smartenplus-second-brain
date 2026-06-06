# Rate-Review CSS Consistency Audit — 2026-06-06

**Branch:** `260606-fix/heic-review-upload`

## Fixes Applied

### BookingReviewList.js
| Was | Fixed to | Why |
|-----|----------|-----|
| `Typography` for heading | `<h2>` native | One-off MUI import, rest of file uses `<span>` |
| `text-gray-600` heading | `text-gray-900` | Design system `HOMEPAGE_SECTION.heading` |
| Missing `sm:text-xl` | `text-lg sm:text-xl` | `TYPOGRAPHY_SCALE.h3` responsive pattern |
| `hover:bg-blue-600` button | `hover:bg-brand-primary-dark` | Wrong Tailwind color vs design system token |
| `py-2 px-4 rounded-md mt-2` | `py-3 px-6 rounded-lg mt-auto` | Match `BUTTON_CONFIG.primary` sizing |
| `'#FFA000'` star fill | `COLORS.status.warning` | Tokenize hardcoded hex |
| `EventAvailableOutlined` import | removed | Dead import |
| `p-2 mb-3` header | `px-1 mb-4` | Was half of `UnifiedCard p-4`, now consistent |
| Sort label "Sort by Date (Ascending)" | "Date: Asc/Desc" | Too long at 320px, wraps |

### pages/rate-review/index.js
| Was | Fixed to | Why |
|-----|----------|-----|
| Two separate `max-w-[1200px]` wrappers | Collapsed to one | Unnecessary nesting |
| `px-2 md:px-3` | `px-2 md:px-3` (breadcrumb) / `px-4 md:px-6` → reverted back to `px-2 md:px-3` | Match platform |
| `rounded-lg` on invisible section | removed | No visual effect |
| `<div className="flex flex-col gap-0">` wrapper | removed | Single-child zero-gap = useless |
| `import ReviewList` | removed | Dead import |
| `router` in useEffect deps | `status` | `router` unused in effect body |
| No session-loading guard | `if (status === 'loading' \|\| loading)` | Prevented blank flash |

### pages/rate-review/[reviewSlug].js
| Was | Fixed to | Why |
|-----|----------|-----|
| Duplicate `return normalized` | one `return` | Dead code |
| Static `canonical: 'https://smartenplus.co.th/rate-review'` | Dynamic `${getSiteUrl()}/rate-review/${reviewSlug}` | All 3 pages had same canonical |
| Missing `www.` in canonical | `www.smartenplus.co.th` | CLAUDE.md SEO rule |
| `useMemo(seo, [])` | `useMemo(seo, [reviewSlug])` | Stale canonical when slug changes |
| Error state: bare `text-red-600` text | `UnifiedCard` + "Back to reviews" button | `EmptyState` is available |
| MUI `IconButton` back nav | Floating `bg-white/80` button | Match platform pattern |

### pages/rate-review/submit-review/[...slug].js
| Was | Fixed to | Why |
|-----|----------|-----|
| Dead `FeaturedImageHeader`, `bgDefault` imports | removed | Never used |
| No `COLORS` import | added | Used for `CircularProgress` |
| `CircularProgress` unstyled | `sx={{ color: COLORS.brand.primary }}` | Match `[reviewSlug].js` |
| `#3b5998` hardcoded in `sx` | `COLORS.brand.primary` | Use token |
| `onClose={() => router.push('/')}` | `router.push('/rate-review')` | Cancel went to homepage |
| MUI `IconButton` back nav | Floating `bg-white/80` button | Match platform pattern |

### RateAndReviewForm.js
| Was | Fixed to | Why |
|-----|----------|-----|
| `text-gray-400` caption | `text-gray-500` | WCAG AA contrast (#6B7280 = 4.6:1) |
