---
title: Content questions for /help/faqs landing page
date: 2026-06-07
status: sent (awaiting reply)
owner: charuwatnaranong
deadline: EOD 2026-06-09
related:
  - 01-projects/help-faqs-landing-2026-06-07/audit.md
  - smartenplus-frontend/pages/help/faqs.js
  - smartenplus-frontend/helpers/wordpress/api.js (POSTS_BY_FAQ_CATEGORY)
---

# Content Questions for `/help/faqs` Landing Page

Build is technically complete (shipped branch `260607-feat/help-faqs-landing`). Assumed defaults for the 2 questions below. If actual answers differ significantly, follow-up patch may be needed (1-line change to `CANONICAL_TAGS` constant or `first: 30` cap in `getServerSideProps`).

## Question 1 (to content team — WordPress admin)

> **Subject:** FAQ inventory for `/help/faqs` landing page
>
> Hi content team,
>
> We just shipped a new `/help/faqs` landing page that aggregates all FAQ posts from the WP `FAQs` category. Two questions to confirm our defaults:
>
> **Q1.1 — Post count:** We set the cap at `first: 30` based on rough estimate. Actual count please? Run this in WPGraphiQL:
> ```graphql
> { posts(where: {categoryName: "FAQs"}) { pageInfo { offsetPagination { total } } } }
> ```
> If 31+, we may need pagination or "load more" button.
>
> **Q1.2 — Tag taxonomy:** Our code groups FAQs into 4 buckets by tag slug: `transport`, `payment`, `booking`, `cancellation` (with `other` fallback). Are these the canonical tag slugs applied to your FAQ posts? If different, please share the actual tag list so we can update the grouping.
>
> **Deadline:** EOD 2026-06-09 (Mon).
>
> Reference: `01-projects/help-faqs-landing-2026-06-07/audit.md` (sections 5 + 11)

## Question 2 (to BD)

> **Subject:** `/help/faqs` — confirm v1 spec (no source links per Q&A)
>
> For the new `/help/faqs` landing page, each Q&A renders inline (expandable `<details>` with full answer body inline, sanitized via DOMPurify).
>
> **Decision shipped in v1:** No "Read full article" link per Q&A. Clean expandable list, all content inline. Source posts at `/help/faqs/{slug}` still accessible via direct URL or `BlogCard`/`RelatedPostsWidget`/`ProductCard` click-throughs.
>
> Please confirm: v1 as spec'd is OK, or override to v2 with source link below each Q&A? v2 needs 1-line `CANONICAL_TAGS` change + add `categories { nodes { slug } }` to GraphQL query.
>
> **Deadline:** EOD 2026-06-09.
>
> Reference: `01-projects/help-faqs-landing-2026-06-07/audit.md` (section 11 Q(c))

## Defaults assumed (no answers yet)

| Question | Default used | Risk if wrong | Fix effort |
|----------|--------------|---------------|-----------|
| Q1.1 FAQ count | `first: 30` cap, no pagination | If >30 FAQs, posts beyond 30 invisible | S (1 file, cursor pagination or load-more) |
| Q1.2 Tag slugs | `['transport', 'payment', 'booking', 'cancellation']` + `other` fallback | If different slugs, all posts fall to `other` bucket (1 big list) | XS (1 line in `CANONICAL_TAGS`) |
| Q2.1 Source links | No source link per Q&A | If BD wants v2, 1 patch | S (GraphQL field + link JSX) |

## Update on receipt

When answers come back:
1. If Q1.1 = >30: patch `getServerSideProps` + add pagination
2. If Q1.2 = different tags: update `CANONICAL_TAGS` constant in `pages/help/faqs.js:11`
3. If Q2.1 = v2: add source link JSX + `categories` field to GraphQL query

Mark this file's `status` field as `answered-YYYY-MM-DD` when all 3 answered.
