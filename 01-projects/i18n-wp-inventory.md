---
name: i18n-wp-inventory
description: W0 inventory of WordPress content for Thai i18n (pages, tags, help/FAQ, posts) scanned live 2026-10-15, plus content-team authoring checklist.
type: project
date: 2026-10-15
parent: i18n-rollout-plan
---

# WP Inventory for Thai i18n (W0)

## Summary
WP (`https://blog.smartenplus.co.th/graphql`, read-only scan 2026-10-15) has **3 Thai pages and zero Thai posts or tags**. Thai pages are done. Everything W3 and W5 need is still to be authored. Until a Thai post exists, W3 can ship but shows English guides on every `/th/*` page.

## Why this matters
W3 reads guide posts by tag with `GET_ALL_POSTS_BY_TAG` and the station slug as the tag (`pages/destinations/[slug].js:345-349`). Thai = tag `<slug>-th`, fallback English ([[i18n-rollout-plan]] W3). A Thai tag only helps if Thai posts carry it.

## Pages (8 published, scanned via GraphQL `pages`)
| Slug | Thai pair | Used by | Status |
|---|---|---|---|
| `about` / `about-th` | yes | `/about` (W1) | done |
| `privacy` / `privacy-th` | yes | `/privacy` (W2) | done |
| `terms` / `terms-th` | yes | `/terms` (W2) | done |
| `smartenplus` | **no** | homepage WP data (W4); `getLocalizedPage('smartenplus','th')` falls back to English | gap, W4 |
| `exploring-northern-thailand-by-long-tail-boat-...` | no | stray 2023 page, not wired to FE | ignore or archive in WP |

Pairing rule: Thai page slug = base slug + `-th`, top-level (registry `wpSlugSuffix`). No other base page needs a Thai twin today.

## Tags (1468 total, 1399 with posts)
- **0 tags end in `-th`.** W3 Thai lookup finds nothing today.
- 5 tags have Thai names and Thai slugs (e.g. `กระบี่`, `เกาะหลีเป๊ะ`, 1 post each). Different scheme, will not match `<slug>-th`. Decide: rename to `-th` convention or leave.
- Heaviest tags (English guide volume): `thailand-transportation` 705, `thailand-destinations` 695, `thailand-travel-guide` 645, `koh-lipe` 425, `krabi` 332, `ao-nang` 197, `phuket` 176, `chiang-mai` 171, `hat-yai` 161, `koh-lanta` 141, `bangkok` 122.
- Messy tail: near-duplicates (`ao-nang-to-bankok`, `aonang`, `ao-nam-mao-pie`) and empty tags. Do not mirror them in Thai.

## Posts (1629) and categories (22)
- **0 posts** have a Thai title or a `-th` slug.
- Big categories: `destination-guides` 1233, `transportation-guides` 368, `itinerary-planning` 144, `uncategorized` 52, `activities` 40, `news` 31.
- Help/FAQ = **posts under child categories of `helps`** (not pages): `faqs` 38, `booking-process` 12, `general` 12, `member-information` 3, `delays-cancellations` 4, `check-in-travel-documents-tickets` 5, `contact-us` 1, `payment-refund` 1, `work-with-us` 1. About 77 posts total, 0 Thai. Needed by W5. Empty `faqs-2` and `helps` roots are structure only.

## Content-team authoring checklist
1. **Start small for W3:** pick the top destinations by traffic (e.g. Krabi, Phuket, Chiang Mai, Koh Lipe, Ao Nang, Bangkok). Per destination, author 3-5 Thai guide posts.
2. **Tag each Thai post** with `<station-slug>-th` (exactly the English tag slug + `-th`). One typo = invisible post.
3. Thai posts keep English category slugs (`destination-guides`, etc.) so category UI stays consistent.
4. **Help/FAQ (W5):** translate by category. Decide first if Thai posts reuse the English categories or get their own (open, goes with W5 decision).
5. Do not edit `privacy-th`, `terms-th`, `about-th` slugs. FE depends on them.
6. Homepage twin `smartenplus-th` only when W4 starts.

## Decisions needed (user)
- Ship W3 before any Thai tag exists (FE ready, English shown) or wait for first Thai batch?
- The 5 Thai-slug tags: rename to `-th` scheme or ignore?
- Stray 2023 page: archive in WP?

## Method and limits
Public GraphQL queries `pages`, `tags`, `categories`, `posts` paged to the end, saved only in session scratchpad (not committed). Counts are a snapshot of 2026-10-15. Draft or private content is not visible. Station slug list from the backend was **not** cross-checked against tags, so which stations have an English tag is unverified.

## Related
[[i18n-rollout-plan]] · [[i18n-standard-structure]]
