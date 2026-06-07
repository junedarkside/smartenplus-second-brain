---
title: /help/faqs Landing Page Audit
date: 2026-06-07
status: draft
tags: [f11-followup, help, faq, seo, content]
related:
  - master-state.md (F11-FOLLOWUP deferred items)
  - 07-logs/log.md:9 (session #72 rationale)
  - 07-logs/session-history.md:28-31 (F11 original <details> pattern)
  - 01-projects/website-audit-full-2026-06-06/r3-leader-synthesis.md
---

# /help/faqs Landing Page Audit

## 1. Context

Footer `Help & FAQs` link added in session #72 (`3534e21`) routes to `/help/faqs` — that URL **404s** today (no page exists). The link was added when the visible homepage FAQ was removed in favor of a trust strip. The footer slot promised Q&A content but the destination is broken.

Session #72 6-agent debate (PM/BD/UX + 3 scrutinize) recommended a dedicated 25-30 Q&A aggregated landing page at `/help/faqs` to:
- Replace the homepage FAQ that was removed (wrong funnel stage, 1.86/5 design score, JSON-LD silently invalid)
- Provide a single bookmarkable destination for the footer link
- Capture search traffic on common pre-purchase questions

**Critical SEO constraint:** `FAQPage` rich results were deprecated by Google in August 2023. The page must NOT emit `FAQPageJsonLd`. Reference: `07-logs/log.md:9` session #72 entry.

**Why now:** The 404 has been live since #72 shipped (2026-06-07). Footer link click goes to a broken page. Low risk to fix; high value (unblocks BD/UX recommendation, removes a dead link).

## 2. Goal

A single landing page at `/help/faqs` that:
- Aggregates 25-30 Q&A pairs from the WordPress `FAQs` category
- Groups by tag (4-5 buckets: transport, payment, booking, cancellation, other)
- Each Q&A expand/collapse via native `<details>/<summary>`
- No pagination, no search, no filter (scope: simple aggregated list)
- Canonical: `${getSiteUrl()}/help/faqs` (no `FAQPage` JSON-LD)
- Lint clean, 44px tap targets, no CLS

**Non-goals (out of scope):**
- B2B corporate CTA strip (awaits 280px product decision)
- Shared `<Accordion>` / `<FAQAccordion>` atom (UX flagged, deferred)
- Search/filter UI (scope creep)
- Per-Q&A canonical source pages (already exist at `/help/[childCategory]/[postSlug]`)
- FAQ post authoring workflow (content team owns)

## 3. URL + routing

**New file:** `pages/help/faqs.js` (sibling to `pages/help/index.js` and `pages/help/[...slug].js`).

**Routing precedence in Next.js Pages Router:**
- Static path `/help/faqs` wins over catch-all `[...slug].js` because static routes have higher priority
- This means `[...slug].js` will NOT receive `["faqs"]` — confirmed by existing patterns

**Title (matches existing pattern):**
```js
// pages/help/faqs.js
const HelpFaqs = () => { ... }
export default HelpFaqs
```

**Side effect to verify:** `pages/help/[...slug].js` should never receive `slug=["faqs"]` once `faqs.js` exists. Add a defensive check or unit test in the build ticket (out of scope here).

## 4. Content source

**WordPress GraphQL** via existing helper at `helpers/wordpress/api.js`.

**New query helper:** `POSTS_BY_FAQ_CATEGORY` (add to `helpers/wordpress/api.js`, ~30 lines).

**Pattern reuse:** Mirror `POSTS_BY_CHILD_CATEGORY` at `helpers/wordpress/api.js:601`. Pass child category slug = `"faqs"`.

**Query shape** (per WordPress `POST_BY_SLUG` schema at `api.js:223`):
```graphql
query PostsByFaqCategory($first: Int = 30) {
  posts(first: $first, where: {categoryName: "FAQs", orderby: {field: DATE, order: DESC}}) {
    nodes {
      databaseId
      slug
      title
      excerpt
      content
      tags {
        nodes { name slug }
      }
      featuredImage { node { sourceUrl altText } }
    }
  }
}
```

**Note:** `content` field returns HTML (rendered with `dangerouslySetInnerHTML` — same pattern as `[...slug].js:222`).

**Estimated post count:** ~25-30 (per BD recommendation). Verify via GraphQL query before build.

## 5. Grouping strategy

Group FAQ posts by `tags.nodes[].name` (first tag wins, fallback bucket = `general`).

**Expected buckets** (5):
- `transport` (van, ferry, train, transfers)
- `payment` (cards, PromptPay, refunds)
- `booking` (reservations, changes, confirmation)
- `cancellation` (refunds, policy, timing)
- `other` (catch-all)

**Grouping function:** Reuse pattern from `pages/help/[...slug].js:31-66` (groups by `locationFields.location/station/route`). Same `reduce` shape, different grouping key.

**Rendering:** Each group = one section with h2 title + stacked `<details>` items. `divide-y divide-gray-200` between items. No MUI Accordion needed.

## 6. UX pattern

**Native `<details>`/`<summary>`** (proven in original F11 per `07-logs/session-history.md:29`).

**Per Q&A:**
```html
<details className="group py-4 border-b border-gray-200">
  <summary className="flex justify-between items-center cursor-pointer text-base font-semibold text-gray-900 min-h-[44px]">
    {post.title}
    <ChevronIcon className="transition-transform group-open:rotate-180" />
  </summary>
  <div
    className="mt-2 text-sm text-gray-700 prose prose-sm max-w-none"
    dangerouslySetInnerHTML={{ __html: post.content }}
  />
</details>
```

**No JS needed** for expand/collapse. Browser handles open/close state. No hydration cost. No new component.

**Tap target:** `min-h-[44px]` on summary → WCAG 2.2 compliant.

**Accessibility:** Native `<details>` already exposes `aria-expanded` via browser. No custom keyboard handling needed.

## 7. SEO

**Canonical:**
```js
import { getSiteUrl } from '../../utils/blog/seoHelper';
// NextSeo config
canonical: `${getSiteUrl()}/help/faqs`
```

**No JSON-LD:** `FAQPage` rich results deprecated Aug 2023. Per session #72 log, the original homepage FAQ's JSON-LD was silently invalid. Don't repeat that mistake. Plain `NextSeo` title + description only.

**Optional:** `BreadcrumbJsonLd` if/when a breadcrumb trail makes sense. Skip for v1 (single-level page).

**Title/description:**
- Title: `Help & FAQs | SmartEnPlus`
- Description: `Common questions about booking, payment, transport, and cancellations in Thailand. Quick answers from SmartEnPlus.`

**Pattern reuse:** `getSiteUrl()` at `utils/blog/seoHelper.js`. Canonical rewrite pattern at `pages/help/[...slug].js:76-77` (replaces `blog.smartenplus.co.th` → `www.smartenplus.co.th`).

## 8. Page layout

**Hero:** `FeaturedImageHeader` with `bgDefaultImage1` (matches `pages/help/index.js:68`).

**Breadcrumb:** Standard breadcrumb component (`components/UI/StandardBreadcrumb`) → `Help / FAQs`.

**Content area:** Single column, `max-w-[1200px] mx-auto px-2 md:px-3 xl:px-0` (canonical padding pattern from session #76 RR alignment).

**Group rendering:** Stack groups vertically, each group has h2 + 5-7 Q&A `<details>` items. `space-y-8` between groups.

**No trust strip, no CTA, no B2B section** (all deferred per #72 debate).

## 9. Existing filters — leave as-is

Both filters are **correct** and should remain:
- `pages/help/index.js:143` — `filter(category => category.name !== 'FAQs')` keeps FAQs out of category index
- `pages/homepagev2.js:451` — same filter (homepage no longer shows FAQ at all)

The new `/help/faqs` page is the dedicated destination. Removing the filter would put FAQs back in the category index (cluttering the 4-col grid). Keep both filters.

## 10. Out of scope

| Item | Reason | Where tracked |
|------|--------|---------------|
| B2B corporate CTA strip | Awaits 280px product decision | `master-state.md:113` |
| Shared `<Accordion>` / `<FAQAccordion>` atom | UX flagged, native `<details>` sufficient for v1 | `master-state.md:114` |
| Search/filter UI | Scope creep; v2 if analytics show demand | new ticket |
| Per-Q&A canonical source links | Posts already exist at `/help/[childCategory]/[postSlug]` | n/a |
| FAQ post authoring | Content team workflow, not engineering | n/a |
| `/help/faqs/[slug]` nested routes | Single-page aggregation only | n/a |
| FAQ count beyond 30 | Pagination; not needed for v1 | new ticket |
| Analytics instrumentation | Cross-cutting concern, separate sprint | n/a |

## 11. Open questions

Need answers from BD/content team before/during build:

- **(a) Exact FAQ post count** — How many `FAQs` category posts exist in WP right now? Need to query GraphQL. If <20, may need content expansion.
- **(b) Tag taxonomy** — Confirm the 5 expected buckets (transport / payment / booking / cancellation / other). Are tags already applied to FAQ posts in WP, or do they need to be added?
- **(c) Source post linking** — Should each Q&A in the aggregated list link to its full source post at `/help/[childCategory]/[postSlug]`? (v1 = no link, just expand inline. v2 = "Read full article" link.)

## 12. Acceptance criteria

- [ ] `/help/faqs` returns 200 (footer link works)
- [ ] 25-30 Q&As visible (or however many exist)
- [ ] Grouped by 4-5 tag buckets
- [ ] Each Q&A expandable via `<details>`/`<summary>`
- [ ] Canonical `${getSiteUrl()}/help/faqs` set correctly
- [ ] **No** `FAQPageJsonLd` in page source
- [ ] No CLS (hero loads before Q&A list)
- [ ] 44px tap targets on summaries
- [ ] Lint clean (`npx eslint pages/help/faqs.js`)
- [ ] Visual check on mobile + desktop + tablet

## 13. Build sequence

Sequential, not parallel:

1. **Spec approval** (this doc reviewed by PM/BD) → unblocks step 2
2. **GraphQL query helper** — add `POSTS_BY_FAQ_CATEGORY` to `helpers/wordpress/api.js`. Lint check.
3. **Page file** — `pages/help/faqs.js` (scaffold hero + breadcrumb + group render). Lint check.
4. **Visual check** — dev server, expand/collapse UX, mobile/tablet/desktop
5. **Open questions answered** — at minimum (a) post count, (b) tag taxonomy
6. **Vault sync** — session-end entry, log entry, master-state update (F11-FOLLOWUP closed)

**Estimated effort:** 2-3 hours total (per session #72 estimate).

## Appendix A — File:line references

| Pattern | File:line | Reuse as |
|---------|-----------|----------|
| GraphQL query shape | `helpers/wordpress/api.js:601` | `POSTS_BY_FAQ_CATEGORY` skeleton |
| Single post schema | `helpers/wordpress/api.js:223` | Field selection reference |
| Grouping function | `pages/help/[...slug].js:31-66` | Group by tag pattern |
| Content render | `pages/help/[...slug].js:222` | `dangerouslySetInnerHTML` pattern |
| Canonical rewrite | `pages/help/[...slug].js:76-77` | `blog.smartenplus.co.th` → `www.smartenplus.co.th` |
| Hero pattern | `pages/help/index.js:68` | `FeaturedImageHeader` + `bgDefaultImage1` |
| Padding pattern | (per session #76) `px-2 md:px-3 xl:px-0` | Content area |
| `getSiteUrl()` | `utils/blog/seoHelper.js` | Canonical helper |
| `StandardBreadcrumb` | `components/UI/StandardBreadcrumb` | Breadcrumb component |
| Footer link target | `components/layout/footer.js:33` | Confirmed `/help/faqs` |

## Appendix B — Related vault refs

- `master-state.md:111-116` — F11-FOLLOWUP 3 deferred items
- `07-logs/log.md:9` — session #72 rationale (6-agent debate)
- `07-logs/session-history.md:28-31` — F11 spec mismatch + original `<details>` UX
- `01-projects/website-audit-full-2026-06-06/r3-leader-synthesis.md` — F11 rework context
- `components/layout/footer.js:33` — Footer `Help & FAQs` link (broken since #72)
- `pages/help/index.js:143` — FAQs filter (correct, leave as-is)
- `pages/homepagev2.js:451` — Homepage FAQs filter (correct, leave as-is)
